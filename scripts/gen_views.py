#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["PyYAML==6.0.3"]
# ///
"""Render every repeated view of the repository from `homework.yaml`.

`scripts/gen_views.py` is the one owner of every repeated view (D-13): the
README index, the multi-root workspace, the `mkdocs.yml` navigation, the
generated documentation pages and `platformio.shared.ini`. This plan implements
the `readme` view first and keeps the whole spine — one metadata loader, one
ownership manifest, one plan-then-apply classifier and one drift reporter — so
every later subcommand reuses it instead of inventing its own.

The `workspace` subcommand owns its whole file: the reviewed template under
`templates/views/` is the only writer, and a folder display name or path reaches
it as one pre-rendered fragment.

The `nav` subcommand renders the whole `mkdocs.yml`, including its `nav:` block,
because D-06 gives one reviewed template the whole file. `--all` runs the
implemented views in the fixed order `readme`, `workspace`, `shared-ini`,
`docs`, `nav`; a view that raises `CheckError` aborts the run with exit 2 and a
stderr line naming it, so a zero-homework tree is never a partial success.

The committed `generated.manifest` is the only authority on which paths this
generator owns (D-17). It is a JSON object `{"version": 1, "entries": [...]}`
whose entries are sorted by `path`, carry `path`, `owner`, `mode`, `sha256` and
`bytes`, and additionally `marker_begin`/`marker_end` for a region entry. The
manifest never lists itself: its own correctness is proven by recomputing it and
comparing bytes with the committed copy.

The generator never reads the clock, never invokes PlatformIO, never reads
`git remote` (a fixture root has none) and produces byte-identical output across
runs. Two generator runs over the same tree are not serialized; do not run them
concurrently. Each file is written through a temporary file in its own directory
followed by `os.replace`, so no file is ever observed half-written, but nothing
coordinates two writers and the last one wins per file.

Usage:
  uv run scripts/gen_views.py <readme|workspace|shared-ini|docs|nav> [--check]
                              [--json] [--dir PATH]
  uv run scripts/gen_views.py --all [--check] [--json] [--dir PATH]

Exit codes (the vocabulary shared with `check_metadata.py`, D-23):
  0  every record is CREATE, UNCHANGED, MODIFIED or DELETE (write mode), or
     every record is UNCHANGED (check mode)
  1  a content problem on an owned file (ERROR), a stale path the manifest
     lists but no view produces (ORPHAN), or, in check mode, any drift
  2  usage or environment error (bad arguments, an unimplemented view, a target
     outside the static allowlist, a symlink on a target path, an ambiguous
     marker region, an unreadable or malformed manifest, an unknown
     `{{placeholder}}`, a missing or unreadable template, an OS-level write
     failure)

`--check` never writes: it classifies, emits the records and returns.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
import tempfile
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.metadata.errors import CheckError  # noqa: E402
from scripts.metadata.paths import (  # noqa: E402
    derive_parts,
    relative_path,
    resolve_root,
)
from scripts.metadata.render import read_text, render  # noqa: E402
from scripts.metadata.yaml_loader import StrictSafeLoader  # noqa: E402

# D-02/D-11: the site and repository URLs are module constants, following the
# `BOARD` precedent in `scripts/new_homework`: a fixture root has no git remote.
SITE_URL = "https://vloktiev-emb.github.io/homeworks/"
REPOSITORY_URL = "https://github.com/VLoktiev-EMB/homeworks"

# D-03: every wholly generated file starts with this header, and write mode
# refuses to delete a stale path that does not carry it (T-5-09).
GENERATED_HEADER = (
    "<!-- GENERATED — do not edit. Run: uv run scripts/gen_views.py --all -->"
)

# D-17: one committed ledger of the paths this generator owns.
MANIFEST_PATH = "generated.manifest"

# D-14/D-09: the README owns prose; the generator owns this region.
MARKER_BEGIN = "<!-- BEGIN GENERATED: homeworks -->"
MARKER_END = "<!-- END GENERATED -->"

# D-13: the canonical `--all` order. `docs` and `nav` stay registered here so a
# later plan adds a handler without reordering anything; `_select_views` runs
# only the subset that has one, which is what keeps the order stable across
# plans.
VIEWS = ("readme", "workspace", "shared-ini", "docs", "nav")

# The static allowlist: a target the generator may write. Anything else is a
# usage error (exit 2) before a single record is printed (T-5-08).
ALLOWED_FILES = (
    "README.md",
    "mkdocs.yml",
    "homeworks.code-workspace",
    "platformio.shared.ini",
)
ALLOWED_PREFIXES = ("docs",)

# Statuses that block write mode. DELETED is a whole-file view whose target is
# absent; recreating it is a deliberate future decision, so it blocks today.
BLOCKING_STATUSES = ("ERROR", "ORPHAN", "DELETED")

TABLE_HEADER = "| ID | Project | Board | Framework | Status | Report |"
TABLE_SEPARATOR = "|----|---------|-------|-----------|--------|--------|"

CONCURRENCY_NOTE = (
    "Two generator runs over the same tree are not serialized; "
    "do not run them concurrently."
)

# META-07/D-15: the four roots that always lead the workspace folder list.
WORKSPACE_FIXED_ROOTS = (
    ("repo", "."),
    ("docs", "docs"),
    ("lib", "lib"),
    ("scripts", "scripts"),
)

_CONTROL = re.compile(r"[\x00-\x1f\x7f]+")
_SHA256_HEX = re.compile(r"^[0-9a-f]{64}$")


def _escape_cell(value):
    """Make a metadata value safe inside one Markdown table cell (ASVS V5).

    Control characters, tabs and newlines collapse to a single space, so a
    multi-line title cannot break the table row. `|` is escaped because it
    would open another column, and `[`/`]` because `_homework_rows` puts the
    title inside a Markdown link label: an unescaped `]` would close the label
    early and an unescaped `[` would open a nested link.
    """
    text = "" if value is None else str(value)
    text = _CONTROL.sub(" ", text).strip()
    return text.replace("|", "\\|").replace("[", "\\[").replace("]", "\\]")


def _load_homeworks(root):
    """Load every `homeworks/*/homework.yaml` with the strict loader.

    `StrictSafeLoader` (not `yaml.safe_load`) turns a duplicated `title`,
    `board` or `toolchain` key into a `ConstructorError` — a `CheckError` here —
    so the generator can never render a silently chosen value (T-5-31). The
    returned records are sorted numerically by `(module, lesson, slug)`, so
    `1_10-x` sorts after `1_3-y`.
    """
    directory = root / "homeworks"
    try:
        directory_mode = os.lstat(directory).st_mode
    except FileNotFoundError:
        return []
    except OSError as exc:
        raise CheckError(f"cannot inspect homeworks: {exc}") from exc
    if stat.S_ISLNK(directory_mode):
        raise CheckError("homeworks is a symlink; refusing to follow it")
    if not stat.S_ISDIR(directory_mode):
        raise CheckError("homeworks exists and is not a directory")

    try:
        projects = sorted(directory.iterdir(), key=lambda item: item.name)
    except OSError as exc:
        raise CheckError(f"cannot list homeworks: {exc}") from exc

    records = []
    for project in projects:
        try:
            project_mode = os.lstat(project).st_mode
        except OSError as exc:
            raise CheckError(f"cannot inspect {project.name}: {exc}") from exc
        if stat.S_ISLNK(project_mode):
            raise CheckError(
                f"homeworks/{project.name} is a symlink; refusing to follow it"
            )
        if not stat.S_ISDIR(project_mode):
            continue
        parts = derive_parts(project.name)
        display = f"{relative_path(root, project)}/homework.yaml"
        text = read_text(project / "homework.yaml", display)
        try:
            document = yaml.load(text, Loader=StrictSafeLoader)
        except yaml.YAMLError as exc:
            raise CheckError(f"{display} is not valid YAML: {exc}") from exc
        if not isinstance(document, dict):
            raise CheckError(f"{display} must be a YAML mapping")
        title = document.get("title")
        records.append(
            {
                "id": project.name,
                "display": display,
                "document": document,
                "module": parts["module"],
                "lesson": parts["lesson"],
                "slug": parts["slug"],
                "title": (
                    title.strip()
                    if isinstance(title, str) and title.strip()
                    else parts["title"]
                ),
            }
        )
    records.sort(
        key=lambda item: (int(item["module"]), int(item["lesson"]), item["slug"])
    )
    return records


def _homework_rows(homeworks, *, link_style):
    """Render the pre-rendered table body for `{{homework_rows}}` (D-20).

    D-11 fixes the six columns: ID, Project, Board, Framework, Status, Report.
    A relative link is repository-relative (the README); an absolute link is a
    `REPOSITORY_URL` URL (the site home page cannot use `../../` — Pitfall 3).
    """
    if link_style not in ("relative", "absolute"):
        raise CheckError(f"unknown link style {link_style!r}")
    rows = []
    for homework in homeworks:
        identifier = homework["id"]
        document = homework["document"]
        number = f"{homework['module']}.{homework['lesson']}"
        title = _escape_cell(homework["title"])
        report = document.get("report")
        report_path = report.get("path") if isinstance(report, dict) else None
        if not isinstance(report_path, str) or not report_path:
            report_path = "report.md"
        if link_style == "relative":
            project_link = f"homeworks/{identifier}/"
            report_link = f"homeworks/{identifier}/{report_path}"
        else:
            project_link = f"{REPOSITORY_URL}/tree/main/homeworks/{identifier}/"
            report_link = (
                f"{REPOSITORY_URL}/blob/main/homeworks/{identifier}/{report_path}"
            )
        rows.append(
            "| "
            + " | ".join(
                (
                    _escape_cell(number),
                    f"[{number} {title}]({project_link})",
                    _escape_cell(document.get("board")),
                    _escape_cell(document.get("framework")),
                    _escape_cell(document.get("status")),
                    f"[report]({report_link})",
                )
            )
            + " |"
        )
    return "\n".join(rows)


def _region(text, begin, end, display):
    """Return the inclusive `(start, stop)` indices of the owned marker region.

    The end marker carries no region name (D-14 spells it `<!-- END GENERATED
    -->`), so zero begin markers, more than one, or an end marker before the
    begin marker makes "the region" ambiguous. That is an environment problem
    (exit 2), not drift (T-5-08).
    """
    begin_count = text.count(begin)
    end_count = text.count(end)
    if begin_count != 1 or end_count != 1:
        raise CheckError(
            f"{display}: expected exactly one {begin!r} and one {end!r}; "
            f"found {begin_count} and {end_count}"
        )
    start = text.index(begin)
    stop = text.index(end)
    if stop < start:
        raise CheckError(f"{display}: the end marker precedes the begin marker")
    return start, stop + len(end)


def _component_conflict(base, relative):
    """Walk *relative* from *base* with `lstat`; never resolve a component.

    T-5-08: a symlink at any component would redirect a write out of the
    intended file, so every prefix is inspected before `exists()`,
    `read_bytes()` or a write can traverse it. A missing component means the
    rest of the path is absent and safe to create.
    """
    consumed = Path()
    parts = Path(relative).parts
    for index, part in enumerate(parts):
        consumed = consumed / part
        current = base / Path(*parts[: index + 1])
        try:
            mode = os.lstat(current).st_mode
        except FileNotFoundError:
            return
        except OSError as exc:
            raise CheckError(f"cannot inspect {consumed.as_posix()}: {exc}") from exc
        if index == len(parts) - 1:
            if stat.S_ISLNK(mode):
                raise CheckError(
                    f"{consumed.as_posix()} is a symlink; refusing to follow "
                    "or overwrite it"
                )
            return
        if stat.S_ISLNK(mode):
            raise CheckError(
                f"intermediate path {consumed.as_posix()} is a symlink; "
                "refusing to follow it"
            )
        if not stat.S_ISDIR(mode):
            raise CheckError(
                f"intermediate path {consumed.as_posix()} exists and is not "
                "a directory"
            )


def _allowed_target(relative):
    """Refuse any target outside the static generated-view allowlist (exit 2)."""
    path = Path(relative)
    parts = path.parts
    if not parts or path.is_absolute() or ".." in parts:
        raise CheckError(
            f"{path.as_posix()} is outside the generated-view allowlist"
        )
    if len(parts) == 1 and parts[0] in ALLOWED_FILES:
        return
    if len(parts) > 1 and parts[0] in ALLOWED_PREFIXES:
        return
    raise CheckError(
        f"{path.as_posix()} is outside the generated-view allowlist"
    )


def _validate_entry(entry):
    """Validate one manifest entry and return it in canonical key order."""
    if not isinstance(entry, dict):
        raise CheckError(f"{MANIFEST_PATH} entries must be JSON objects")
    for key in ("path", "owner", "mode"):
        value = entry.get(key)
        if not isinstance(value, str) or not value:
            raise CheckError(
                f"{MANIFEST_PATH} entry is missing a non-empty {key}"
            )
    mode = entry["mode"]
    if mode not in ("whole", "region"):
        raise CheckError(
            f"{MANIFEST_PATH} entry mode {mode!r} is neither whole nor region"
        )
    digest = entry.get("sha256")
    if not isinstance(digest, str) or not _SHA256_HEX.match(digest):
        raise CheckError(
            f"{MANIFEST_PATH} entry for {entry['path']} has no lowercase "
            "SHA-256 digest"
        )
    size = entry.get("bytes")
    if isinstance(size, bool) or not isinstance(size, int) or size < 0:
        raise CheckError(
            f"{MANIFEST_PATH} entry for {entry['path']} has no byte count"
        )
    path = Path(entry["path"])
    if path == Path(MANIFEST_PATH):
        raise CheckError(f"{MANIFEST_PATH} must never list itself")
    _allowed_target(path)
    canonical = {
        "path": path.as_posix(),
        "owner": entry["owner"],
        "mode": mode,
    }
    if mode == "region":
        for key in ("marker_begin", "marker_end"):
            value = entry.get(key)
            if not isinstance(value, str) or not value:
                raise CheckError(
                    f"{MANIFEST_PATH} region entry for {entry['path']} is "
                    f"missing {key}"
                )
            canonical[key] = value
    allowed = {"path", "owner", "mode", "sha256", "bytes"}
    if mode == "region":
        allowed |= {"marker_begin", "marker_end"}
    extra = set(entry) - allowed
    if extra:
        raise CheckError(
            f"{MANIFEST_PATH} entry for {entry['path']} has unknown keys: "
            + ", ".join(sorted(extra))
        )
    canonical["sha256"] = digest
    canonical["bytes"] = size
    return canonical


def _load_manifest(root):
    """Return the validated manifest entries; a missing manifest is empty."""
    path = root / MANIFEST_PATH
    try:
        mode = os.lstat(path).st_mode
    except FileNotFoundError:
        return []
    except OSError as exc:
        raise CheckError(f"cannot inspect {MANIFEST_PATH}: {exc}") from exc
    if stat.S_ISLNK(mode):
        raise CheckError(f"{MANIFEST_PATH} is a symlink; refusing to follow it")
    if not stat.S_ISREG(mode):
        raise CheckError(f"{MANIFEST_PATH} exists and is not a regular file")
    try:
        raw = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise CheckError(f"{MANIFEST_PATH} is not valid UTF-8: {exc}") from exc
    except OSError as exc:
        raise CheckError(f"cannot read {MANIFEST_PATH}: {exc}") from exc
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise CheckError(f"{MANIFEST_PATH} is not valid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise CheckError(f"{MANIFEST_PATH} must be a JSON object")
    extra = set(payload) - {"version", "entries"}
    if extra:
        raise CheckError(
            f"{MANIFEST_PATH} has unknown keys: " + ", ".join(sorted(extra))
        )
    version = payload.get("version")
    if isinstance(version, bool) or not isinstance(version, int) or version != 1:
        raise CheckError(f"{MANIFEST_PATH} must declare version 1")
    entries = payload.get("entries")
    if not isinstance(entries, list):
        raise CheckError(f"{MANIFEST_PATH} must declare an entries list")
    validated = []
    seen = set()
    for entry in entries:
        canonical = _validate_entry(entry)
        if canonical["path"] in seen:
            raise CheckError(
                f"{MANIFEST_PATH} lists {canonical['path']} twice"
            )
        seen.add(canonical["path"])
        validated.append(canonical)
    return validated


def _manifest_entry(*, path, owner, mode, owned, marker_begin=None, marker_end=None):
    """Build one canonical manifest entry, refusing the manifest itself."""
    relative = Path(path)
    if relative == Path(MANIFEST_PATH):
        raise CheckError(f"{MANIFEST_PATH} must never list itself")
    _allowed_target(relative)
    if mode not in ("whole", "region"):
        raise CheckError(f"unknown manifest mode {mode!r}")
    entry = {"path": relative.as_posix(), "owner": owner, "mode": mode}
    if mode == "region":
        if not marker_begin or not marker_end:
            raise CheckError("a region manifest entry needs both markers")
        entry["marker_begin"] = marker_begin
        entry["marker_end"] = marker_end
    entry["sha256"] = hashlib.sha256(owned).hexdigest()
    entry["bytes"] = len(owned)
    return entry


def _manifest_bytes(entries):
    """Serialize the manifest deterministically (sorted, two spaces, one `\\n`)."""
    ordered = sorted(entries, key=lambda item: item["path"])
    payload = {"version": 1, "entries": ordered}
    return (json.dumps(payload, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def _write_atomic(target, data):
    """Write *data* so each file appears whole or not at all."""
    descriptor, temporary = tempfile.mkstemp(
        dir=target.parent, prefix=".gen_views-"
    )
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
        os.replace(temporary, target)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise


def _emit(records, as_json):
    """Print the records sorted by path and return them."""
    ordered = sorted(records, key=lambda item: item["path"])
    if as_json:
        payload = [
            {
                "path": item["path"],
                "status": item["status"],
                "reason": item["reason"],
            }
            for item in ordered
        ]
        print(json.dumps(payload, indent=2))
    else:
        for item in ordered:
            print(f"{item['path']}: {item['status']} — {item['reason']}")
    return ordered


def _render_readme(root, homeworks):
    """Return the produced entry for the README marker region."""
    display = "README.md"
    template_display = "templates/views/homeworks-table.md.tmpl"
    template = read_text(root / template_display, template_display)
    rendered = render(
        template,
        {"homework_rows": _homework_rows(homeworks, link_style="relative")},
        template_display,
    ).rstrip("\n")
    owned = rendered.encode("utf-8")
    _allowed_target(Path(display))
    _component_conflict(root, Path(display))
    return {
        "path": display,
        "owner": "readme",
        "mode": "region",
        "target": root / display,
        "owned": owned,
        "marker_begin": MARKER_BEGIN,
        "marker_end": MARKER_END,
    }


def _workspace_folders(homeworks):
    """Render the `{{workspace_folders}}` fragment (D-15, META-07).

    The four fixed roots lead, then one entry per homework in the
    `_load_homeworks` order. The fragment is assembled line by line with
    `json.dumps` as the only serializer for the two string values, so a title
    carrying a quote or a newline cannot break the file (T-5-14). Entries are
    separated by `,\\n`, so every entry but the last carries a trailing comma.

    A path is ASCII and repository-relative by construction; the check is still
    explicit because META-07 permits a non-ASCII display *name*, never a
    non-ASCII path.
    """
    entries = list(WORKSPACE_FIXED_ROOTS)
    for homework in homeworks:
        entries.append(
            (
                f"{homework['module']}.{homework['lesson']} {homework['title']}",
                f"homeworks/{homework['id']}",
            )
        )
    blocks = []
    for name, path in entries:
        if not path.isascii():
            raise CheckError(f"workspace folder path {path!r} is not ASCII")
        parts = Path(path).parts
        if Path(path).is_absolute() or ".." in parts:
            raise CheckError(
                f"workspace folder path {path!r} is not repository-relative"
            )
        blocks.append(
            "\t\t{\n"
            "\t\t\t\"name\": " + json.dumps(name, ensure_ascii=False) + ",\n"
            "\t\t\t\"path\": " + json.dumps(path, ensure_ascii=False) + "\n"
            "\t\t}"
        )
    return ",\n".join(blocks)


def _render_workspace(root, homeworks):
    """Return the produced entry for the whole `homeworks.code-workspace`."""
    display = "homeworks.code-workspace"
    template_display = "templates/views/workspace.json.tmpl"
    template = read_text(root / template_display, template_display)
    rendered = render(
        template,
        {"workspace_folders": _workspace_folders(homeworks)},
        template_display,
    )
    data = rendered.encode("utf-8")
    _allowed_target(Path(display))
    _component_conflict(root, Path(display))
    return {
        "path": display,
        "owner": "workspace",
        "mode": "whole",
        "target": root / display,
        "data": data,
        "owned": data,
    }


RENDERERS = {
    "readme": _render_readme,
    "workspace": _render_workspace,
}


def _select_views(args):
    """Return the views this run owns; `--all` covers every implemented view."""
    if args.all:
        return tuple(view for view in VIEWS if view in RENDERERS)
    if args.view not in RENDERERS:
        raise CheckError(f"the {args.view} view is not implemented in this plan")
    return (args.view,)


def _classify_produced(root, entry, manifest_by_path):
    """Classify one produced target; return `(record, payload, delete)`.

    A region target's owned bytes are the marker slice, both markers included,
    so an authored edit outside the region is not drift and a moved marker is.
    A region file that is absent on disk is an ERROR: write mode must never
    recreate an authored file and silently drop its prose.
    """
    path = entry["path"]
    target = entry["target"]
    listed = path in manifest_by_path

    if entry["mode"] == "region":
        if not target.exists():
            return (
                {
                    "path": path,
                    "status": "ERROR",
                    "reason": (
                        "region file is absent; write mode never recreates an "
                        "authored file"
                    ),
                },
                None,
                None,
            )
        if not target.is_file():
            return (
                {
                    "path": path,
                    "status": "ERROR",
                    "reason": "target exists and is not a regular file",
                },
                None,
                None,
            )
        try:
            text = target.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            raise CheckError(f"{path} is not valid UTF-8: {exc}") from exc
        except OSError as exc:
            raise CheckError(f"cannot read {path}: {exc}") from exc
        start, stop = _region(
            text, entry["marker_begin"], entry["marker_end"], path
        )
        existing = text[start:stop].encode("utf-8")
        if existing == entry["owned"]:
            return (
                {
                    "path": path,
                    "status": "UNCHANGED",
                    "reason": "owned bytes are identical",
                },
                None,
                None,
            )
        payload = (
            text[:start] + entry["owned"].decode("utf-8") + text[stop:]
        ).encode("utf-8")
        return (
            {
                "path": path,
                "status": "MODIFIED",
                "reason": "owned bytes differ from the rendered region",
            },
            payload,
            None,
        )

    # A whole-file view: `workspace` and `shared-ini` produce one today; the
    # `docs` view will add generated pages on the same branch.
    data = entry["data"]
    if not target.exists():
        if listed:
            return (
                {
                    "path": path,
                    "status": "DELETED",
                    "reason": "manifest-listed file is absent on disk",
                },
                None,
                None,
            )
        return (
            {"path": path, "status": "CREATE", "reason": "target does not exist"},
            data,
            None,
        )
    if not target.is_file():
        return (
            {
                "path": path,
                "status": "ERROR",
                "reason": "target exists and is not a regular file",
            },
            None,
            None,
        )
    try:
        existing = target.read_bytes()
    except OSError as exc:
        raise CheckError(f"cannot read {path}: {exc}") from exc
    if existing == data:
        return (
            {
                "path": path,
                "status": "UNCHANGED",
                "reason": "target bytes are identical",
            },
            None,
            None,
        )
    return (
        {
            "path": path,
            "status": "MODIFIED",
            "reason": "target bytes differ",
        },
        data,
        None,
    )


def _classify_orphan(root, entry, check):
    """Classify one manifest-listed path no selected view produces.

    Check mode reports ORPHAN and stops. Write mode removes the file only when
    it exists and its first line is the generated-file header (T-5-09); any
    other orphan is reported as ORPHAN and blocks the whole run.
    """
    path = entry["path"]
    target = root / path
    _component_conflict(root, Path(path))
    if check:
        return (
            {
                "path": path,
                "status": "ORPHAN",
                "reason": "the manifest lists a path this view no longer produces",
            },
            None,
        )
    if not target.exists():
        return (
            {
                "path": path,
                "status": "DELETE",
                "reason": "orphan is already absent; manifest entry removed",
            },
            None,
        )
    if not target.is_file():
        return (
            {
                "path": path,
                "status": "ORPHAN",
                "reason": "orphan exists and is not a regular file; refusing to touch it",
            },
            None,
        )
    try:
        with target.open(encoding="utf-8") as handle:
            first_line = handle.readline().rstrip("\n")
    except UnicodeDecodeError:
        first_line = ""
    except OSError as exc:
        raise CheckError(f"cannot read {path}: {exc}") from exc
    if first_line != GENERATED_HEADER:
        return (
            {
                "path": path,
                "status": "ORPHAN",
                "reason": (
                    "orphan does not carry the generated-file header; "
                    "refusing to delete it"
                ),
            },
            None,
        )
    return (
        {
            "path": path,
            "status": "DELETE",
            "reason": "orphan carries the generated-file header",
        },
        target,
    )


def _build_plan(root, selected, check):
    """Classify every selected target and the manifest; write nothing.

    Returns `(records, writes, deletes, manifest_write)`. *writes* maps a path
    to `(target, bytes)`; *deletes* is a list of `Path`s; *manifest_write* is
    the manifest bytes to write, or `None` when the committed copy is in sync.
    """
    homeworks = _load_homeworks(root)
    manifest_entries = _load_manifest(root)
    manifest_by_path = {entry["path"]: entry for entry in manifest_entries}

    produced = {}
    records = []
    for view in selected:
        try:
            entry = RENDERERS[view](root, homeworks)
        except CheckError as exc:
            # The view name is part of the diagnostic: in `--all`, the operator
            # must know which view made the run abort.
            raise CheckError(f"{view}: {exc}") from exc
        if entry["path"] in produced:
            raise CheckError(f"two views produce {entry['path']}")
        produced[entry["path"]] = entry

    writes = {}
    deletes = []
    for path in sorted(produced):
        entry = produced[path]
        record, payload, delete = _classify_produced(
            root, entry, manifest_by_path
        )
        records.append(record)
        if payload is not None:
            writes[path] = (entry["target"], payload)
        if delete is not None:
            deletes.append(delete)

    selected_owners = set(selected)
    orphans = {
        entry["path"]: entry
        for entry in manifest_entries
        if entry["owner"] in selected_owners and entry["path"] not in produced
    }
    for path in sorted(orphans):
        record, delete = _classify_orphan(root, orphans[path], check)
        records.append(record)
        if delete is not None:
            deletes.append(delete)

    # Preserve entries this run does not own; replace produced paths; drop the
    # selected-owner orphans (write mode may delete them; a blocked run writes
    # nothing at all).
    new_entries = [
        entry
        for entry in manifest_entries
        if entry["owner"] not in selected_owners
        and entry["path"] not in produced
    ]
    new_entries.extend(
        _manifest_entry(
            path=path,
            owner=entry["owner"],
            mode=entry["mode"],
            owned=entry["owned"],
            marker_begin=entry.get("marker_begin"),
            marker_end=entry.get("marker_end"),
        )
        for path, entry in produced.items()
    )
    manifest_data = _manifest_bytes(new_entries)

    manifest_target = root / MANIFEST_PATH
    if not manifest_target.exists():
        records.append(
            {
                "path": MANIFEST_PATH,
                "status": "CREATE",
                "reason": "manifest does not exist",
            }
        )
        manifest_write = manifest_data
    else:
        try:
            committed = manifest_target.read_bytes()
        except OSError as exc:
            raise CheckError(f"cannot read {MANIFEST_PATH}: {exc}") from exc
        if committed == manifest_data:
            records.append(
                {
                    "path": MANIFEST_PATH,
                    "status": "UNCHANGED",
                    "reason": "manifest bytes are identical",
                }
            )
            manifest_write = None
        else:
            records.append(
                {
                    "path": MANIFEST_PATH,
                    "status": "MODIFIED",
                    "reason": "manifest bytes differ",
                }
            )
            manifest_write = manifest_data
    return records, writes, deletes, manifest_write


def _apply(root, writes, deletes, manifest_write):
    """Write every classified payload; check mode never reaches this."""
    for target, data in writes.values():
        target.parent.mkdir(parents=True, exist_ok=True)
        _write_atomic(target, data)
    for target in deletes:
        target.unlink(missing_ok=True)
    if manifest_write is not None:
        _write_atomic(root / MANIFEST_PATH, manifest_write)


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="gen_views",
        description="Render every repeated view of the repository from homework.yaml.",
        epilog=CONCURRENCY_NOTE,
    )
    parser.add_argument(
        "view",
        nargs="?",
        choices=VIEWS,
        metavar="VIEW",
        help="which view to render; exactly one of VIEW or --all is required",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="render every implemented view in the fixed order readme, "
        "workspace, shared-ini, docs, nav",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="report drift and exit non-zero without writing anything",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit one sorted JSON array of {path, status, reason} records",
    )
    parser.add_argument(
        "--dir",
        metavar="PATH",
        help="repository root to generate into (default: git rev-parse --show-toplevel)",
    )
    args = parser.parse_args(argv)

    try:
        if args.all == bool(args.view):
            raise CheckError("choose exactly one VIEW or --all")
        selected = _select_views(args)
        root = resolve_root(args.dir)
        records, writes, deletes, manifest_write = _build_plan(
            root, selected, args.check
        )
        ordered = _emit(records, args.json)
    except CheckError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.check:
        return 0 if all(item["status"] == "UNCHANGED" for item in ordered) else 1

    if any(item["status"] in BLOCKING_STATUSES for item in ordered):
        return 1

    try:
        _apply(root, writes, deletes, manifest_write)
    except OSError as exc:
        print(f"ERROR: write failed: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())

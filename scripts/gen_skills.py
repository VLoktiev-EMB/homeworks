#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# ///
"""Generate the `.agents/skills/` mirror from the canonical `.claude/skills/` tree.

`scripts/gen_skills.py` is the only owner of the mirror (D-01, D-04). The
canonical tree is authored Markdown and may use the full Claude Code
frontmatter surface; the mirror is a projection that keeps only the portable
Agent Skills fields, so `.agents/skills/` advertises exactly the behaviour the
other clients can honour (D-02).

Two transform invariants (never re-serialize YAML — Pitfall 2):

1. A mirror `SKILL.md` is `---`, the surviving top-level frontmatter blocks
   verbatim, `---`, the generated marker, the optional explicit-invocation
   banner, one blank line, and then the canonical body byte for byte. A
   column-0 `#` comment is preserved in place and is never read as a key. The
   banner appears exactly when `disable-model-invocation` was dropped, because
   dropping that field widens invocation: absence means "the model may
   invoke" (Pitfall 1).
2. Every non-`SKILL.md` mirror file is the generated marker, a newline, and
   then the canonical bytes unchanged. A mirrored reference is therefore not
   byte-identical to its source; its bytes from line 2 onward are.

`generated.skills.manifest` is the committed ledger of mirror ownership. It is
`{"version": 1, "entries": [...]}` with entries sorted by `path`, each carrying
`path`, `owner`, `source`, `mode`, `sha256` and `bytes`, and it never lists
itself. A write deletes only a manifest-listed path that carries the generated
marker at the documented position: the first line for a non-`SKILL.md` file,
the line immediately after the closing frontmatter fence for a `SKILL.md`.

An absent `.claude/skills/` is a usage error rather than an empty plan: a
mistyped `--dir` must never orphan-delete the whole committed mirror.

The generator never reads the clock, never invokes PlatformIO and produces
byte-identical output across runs. Each file is written through a temporary
file in its own directory followed by `os.replace`, so no file is ever
observed half-written. Two runs over the same tree are not serialized; do not
run them concurrently.

Usage:
  uv run scripts/gen_skills.py [--check] [--json] [--dir PATH]

Exit codes (the vocabulary shared with `check_metadata.py`, D-23):
  0  every record is CREATE or UNCHANGED (write mode), or every record is
     UNCHANGED (check mode)
  1  a content problem on an owned file (ERROR), a stale path the manifest
     lists but no canonical file produces (ORPHAN), or, in check mode, any
     drift
  2  usage or environment error (bad arguments, an absent canonical root, a
     symlink on any path component, a skill directory name outside the slug
     pattern, a `SKILL.md` whose `name` differs from its directory, a
     `_shared/SKILL.md`, a file deeper than `references/<file>`, an unknown
     frontmatter field, an unclosed fence, an unreadable or malformed
     manifest, an OS-level write failure)

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

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.metadata.errors import CheckError  # noqa: E402
from scripts.metadata.paths import resolve_root  # noqa: E402
from scripts.metadata.render import read_regular_text  # noqa: E402

# Phase 9/D-05: every generated mirror file starts with this marker, and write
# mode refuses to delete a stale path that does not carry it (T-09-08).
GENERATED_HEADER = (
    "<!-- GENERATED — do not edit. Run: uv run scripts/gen_skills.py -->"
)

# D-04/D-05: one committed ledger of the paths this generator owns. It is a
# separate file because `gen_views.py` stays scoped to the three view files and
# two generators must never share a write target.
MANIFEST_PATH = "generated.skills.manifest"

# A status that blocks write mode. A produced-but-absent target is a CREATE in
# write mode and a DELETED record only in check mode, so write mode can always
# repair it.
BLOCKING_STATUSES = ("ERROR", "ORPHAN")

# D-01: authored tree and generated mirror.
CANONICAL_ROOT = (".claude", "skills")
MIRROR_ROOT = (".agents", "skills")

# D-21: shared guardrails live here; it holds files, never a `SKILL.md`.
SHARED_NAME = "_shared"

# A skill directory name is also a path component under the mirror (T-09-01).
_SKILL_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_SHA256_HEX = re.compile(r"^[0-9a-f]{64}$")

# The Agent Skills specification's portable frontmatter set. Everything here is
# kept verbatim.
PORTABLE = frozenset(
    {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
)

# The Claude Code-only frontmatter set. It is dropped from the mirror, because
# the other clients cannot honour it.
CLAUDE_ONLY = frozenset(
    {
        "disable-model-invocation",
        "user-invocable",
        "model",
        "context",
        "argument-hint",
        "arguments",
        "when_to_use",
        "paths",
        "hooks",
        "shell",
        "effort",
        "background",
        "agent",
        "disallowed-tools",
    }
)


def _display(*parts):
    """Render a repository-relative display path for a diagnostic."""
    return "/".join(parts)


def _lstat_mode(path, display):
    """Return the `lstat` mode of *path*, or exit 2 when it cannot be read."""
    try:
        return os.lstat(path).st_mode
    except FileNotFoundError:
        raise CheckError(f"{display} disappeared during the run") from None
    except OSError as exc:
        raise CheckError(f"cannot inspect {display}: {exc}") from exc


def _read_bytes(path, display):
    """Read one regular file as bytes; failure is an environment error."""
    try:
        return path.read_bytes()
    except OSError as exc:
        raise CheckError(f"cannot read {display}: {exc}") from exc


def _list_directory(directory, display):
    """Return a directory's entries sorted by name, or exit 2."""
    try:
        return sorted(directory.iterdir(), key=lambda item: item.name)
    except OSError as exc:
        raise CheckError(f"cannot list {display}: {exc}") from exc


def _component_conflict(base, relative):
    """Walk *relative* from *base* with `lstat`; never resolve a component.

    T-09-02: a symlink at any component would redirect a read or a write out of
    the intended path, so every prefix is inspected before `exists()`,
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
    """Refuse any mirror target outside `.agents/skills/` (exit 2, T-09-01)."""
    path = Path(relative)
    parts = path.parts
    if (
        not parts
        or path.is_absolute()
        or ".." in parts
        or parts[:2] != MIRROR_ROOT
        or len(parts) < 4
    ):
        raise CheckError(f"{path.as_posix()} is outside the skills mirror")
    if parts[2] != SHARED_NAME and not _SKILL_NAME.match(parts[2]):
        raise CheckError(
            f"{path.as_posix()} has no valid skill component under the mirror"
        )


def _validate_source(source):
    """Refuse a manifest source outside `.claude/skills/` (exit 2)."""
    parts = source.parts
    if (
        not parts
        or source.is_absolute()
        or ".." in parts
        or parts[:2] != CANONICAL_ROOT
        or len(parts) < 4
    ):
        raise CheckError(
            f"manifest source {source.as_posix()!r} is outside the canonical tree"
        )


def _split_frontmatter(text, display):
    """Return `(frontmatter text without its fences, body after the fence)`."""
    if not text.startswith("---\n"):
        raise CheckError(f"{display} must start with a '---' frontmatter fence")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise CheckError(f"{display}: frontmatter is not closed")
    return text[4 : end + 1], text[end + 5 :]


def _scan_blocks(frontmatter):
    """Split frontmatter into `(key, block_text)` pairs, comments included.

    A block starts at a column-0 line and continues through indented and blank
    lines, so a nested `metadata:` map is one block and is emitted verbatim. A
    column-0 `#` line is a YAML comment: it becomes its own `(None, text)`
    block and is never treated as a key, so an authored comment cannot trip
    the unknown-field refusal.
    """
    blocks = []
    key = None
    lines = []

    def flush():
        nonlocal key, lines
        if lines:
            blocks.append((key, "".join(lines)))
        key = None
        lines = []

    for line in frontmatter.splitlines(keepends=True):
        if line.startswith("#"):
            flush()
            blocks.append((None, line))
            continue
        if not line.strip():
            if lines:
                lines.append(line)
            continue
        if not line[0].isspace():
            flush()
            key = line.split(":", 1)[0].strip()
            lines.append(line)
        else:
            lines.append(line)
    flush()
    return blocks


def _scalar(block):
    """Return a block's first-line value, unquoted when it is a quoted scalar."""
    _, separator, raw = block.splitlines()[0].partition(":")
    if not separator:
        return ""
    value = raw.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    return value


def _transform_skill(text, display, skill_name):
    """Project one canonical `SKILL.md` into its mirror bytes (D-02)."""
    frontmatter, body = _split_frontmatter(text, display)
    name = None
    kept = []
    dropped = set()
    for key, block in _scan_blocks(frontmatter):
        if key is None:
            kept.append(block)
            continue
        if key == "name":
            name = _scalar(block)
        if key in PORTABLE:
            kept.append(block)
        elif key in CLAUDE_ONLY:
            dropped.add(key)
        else:
            raise CheckError(f"{display}: unknown frontmatter field {key!r}")
    if name != skill_name:
        raise CheckError(
            f"{display}: frontmatter name {name!r} does not match its directory "
            f"{skill_name!r}"
        )
    banner = ""
    if "disable-model-invocation" in dropped:
        banner = (
            f"> **Invocation:** explicit only — run `/{skill_name}`. "
            "Do not invoke this skill automatically.\n"
        )
    # Exactly one blank line separates the inserted lines from the body. A
    # canonical body already begins with the blank line after its closing
    # fence, so adding one there would produce two; the body itself is never
    # trimmed, so its bytes stay identical.
    separator = "" if body.startswith("\n") else "\n"
    return (
        "---\n"
        + "".join(kept)
        + "---\n"
        + GENERATED_HEADER
        + "\n"
        + banner
        + separator
        + body
    ).encode("utf-8")


def _skill_files(directory, display):
    """Return `(relative, path, display)` for one skill directory's files.

    Root files and `references/<file>` are mirror targets. Any other nested
    directory, and a file deeper than `references/<file>`, is exit 2 rather
    than silently omitted: the Agent Skills guidance keeps references one level
    deep.
    """
    files = []
    for entry in _list_directory(directory, display):
        entry_display = f"{display}/{entry.name}"
        mode = _lstat_mode(entry, entry_display)
        if stat.S_ISLNK(mode):
            raise CheckError(f"{entry_display} is a symlink; refusing to follow it")
        if stat.S_ISDIR(mode):
            if entry.name != "references":
                raise CheckError(
                    f"{entry_display}: only a references/ directory may nest "
                    "under a skill"
                )
            for inner in _list_directory(entry, entry_display):
                inner_display = f"{entry_display}/{inner.name}"
                inner_mode = _lstat_mode(inner, inner_display)
                if stat.S_ISLNK(inner_mode):
                    raise CheckError(
                        f"{inner_display} is a symlink; refusing to follow it"
                    )
                if stat.S_ISDIR(inner_mode):
                    raise CheckError(
                        f"{inner_display}: references are one level deep; a file "
                        "deeper than references/<file> is not mirrored"
                    )
                if not stat.S_ISREG(inner_mode):
                    raise CheckError(f"{inner_display} is not a regular file")
                files.append(
                    (f"references/{inner.name}", inner, inner_display)
                )
            continue
        if not stat.S_ISREG(mode):
            raise CheckError(f"{entry_display} is not a regular file")
        files.append((entry.name, entry, entry_display))
    return files


def _shared_files(directory, display):
    """Return every file under `_shared/`, refusing symlinks (Pitfall 7).

    `_shared/` holds files, never a skill, so a `SKILL.md` directly inside it
    is refused: a client would discover that directory as a skill.
    """
    files = []
    for current, dirnames, filenames in os.walk(directory, followlinks=False):
        current_path = Path(current)
        relative_dir = current_path.relative_to(directory).as_posix()
        current_display = (
            display if relative_dir == "." else f"{display}/{relative_dir}"
        )
        dirnames.sort()
        for name in dirnames:
            candidate_display = f"{current_display}/{name}"
            mode = _lstat_mode(current_path / name, candidate_display)
            if stat.S_ISLNK(mode):
                raise CheckError(
                    f"{candidate_display} is a symlink; refusing to follow it"
                )
        for name in sorted(filenames):
            candidate = current_path / name
            candidate_display = f"{current_display}/{name}"
            mode = _lstat_mode(candidate, candidate_display)
            if stat.S_ISLNK(mode):
                raise CheckError(
                    f"{candidate_display} is a symlink; refusing to follow it"
                )
            if not stat.S_ISREG(mode):
                raise CheckError(f"{candidate_display} is not a regular file")
            relative = candidate.relative_to(directory).as_posix()
            if relative == "SKILL.md":
                raise CheckError(
                    f"{candidate_display}: _shared/ must not contain SKILL.md; "
                    "a client would discover it as a skill"
                )
            files.append((relative, candidate, candidate_display))
    return files


def _build_targets(root):
    """Return every mirror target, keyed by its repository-relative path."""
    canonical_display = _display(*CANONICAL_ROOT)
    canonical = root.joinpath(*CANONICAL_ROOT)
    _component_conflict(root, Path(canonical_display))
    try:
        mode = os.lstat(canonical).st_mode
    except FileNotFoundError:
        raise CheckError(
            f"{canonical_display} is absent; refusing to empty the mirror. "
            "Pass the repository root with --dir if it was mistyped."
        ) from None
    except OSError as exc:
        raise CheckError(f"cannot inspect {canonical_display}: {exc}") from exc
    if stat.S_ISLNK(mode):
        raise CheckError(
            f"{canonical_display} is a symlink; refusing to follow it"
        )
    if not stat.S_ISDIR(mode):
        raise CheckError(
            f"{canonical_display} exists and is not a directory"
        )

    produced = {}
    for child in _list_directory(canonical, canonical_display):
        child_display = f"{canonical_display}/{child.name}"
        child_mode = _lstat_mode(child, child_display)
        if stat.S_ISLNK(child_mode):
            raise CheckError(f"{child_display} is a symlink; refusing to follow it")
        if not stat.S_ISDIR(child_mode):
            raise CheckError(
                f"{child_display} is not a directory; the canonical tree holds "
                "only skill directories"
            )
        if child.name == SHARED_NAME:
            skill_name = None
            files = _shared_files(child, child_display)
        else:
            if not _SKILL_NAME.match(child.name):
                raise CheckError(
                    f"{child_display}: a skill directory name must match "
                    "^[a-z0-9]+(?:-[a-z0-9]+)*$"
                )
            skill_name = child.name
            files = _skill_files(child, child_display)
            if not any(relative == "SKILL.md" for relative, _, _ in files):
                raise CheckError(
                    f"{child_display}: a skill directory must contain SKILL.md"
                )
        for relative, path, file_display in files:
            mirror = _display(*MIRROR_ROOT, child.name, relative)
            source = _display(*CANONICAL_ROOT, child.name, relative)
            _allowed_target(Path(mirror))
            _validate_source(Path(source))
            if mirror in produced:
                raise CheckError(f"two canonical files produce {mirror}")
            if relative == "SKILL.md" and skill_name is not None:
                text = read_regular_text(path, file_display)
                data = _transform_skill(text, file_display, skill_name)
            else:
                data = (
                    (GENERATED_HEADER + "\n").encode("utf-8")
                    + _read_bytes(path, file_display)
                )
            produced[mirror] = {"path": mirror, "source": source, "data": data}
    return produced


def _manifest_entry(*, path, source, data):
    """Build one canonical manifest entry, refusing an unowned path."""
    _allowed_target(Path(path))
    _validate_source(Path(source))
    entry = {
        "path": Path(path).as_posix(),
        "owner": "skills",
        "source": Path(source).as_posix(),
        "mode": "whole",
    }
    entry["sha256"] = hashlib.sha256(data).hexdigest()
    entry["bytes"] = len(data)
    return entry


def _validate_entry(entry):
    """Validate one manifest entry and return it in canonical key order."""
    if not isinstance(entry, dict):
        raise CheckError(f"{MANIFEST_PATH} entries must be JSON objects")
    allowed = {"path", "owner", "source", "mode", "sha256", "bytes"}
    extra = set(entry) - allowed
    if extra:
        raise CheckError(
            f"{MANIFEST_PATH} entry has unknown keys: " + ", ".join(sorted(extra))
        )
    for key in ("path", "owner", "source", "mode"):
        value = entry.get(key)
        if not isinstance(value, str) or not value:
            raise CheckError(
                f"{MANIFEST_PATH} entry is missing a non-empty {key}"
            )
    if entry["owner"] != "skills":
        raise CheckError(
            f"{MANIFEST_PATH} entry for {entry['path']} has owner "
            f"{entry['owner']!r}; only 'skills' is allowed"
        )
    if entry["mode"] != "whole":
        raise CheckError(
            f"{MANIFEST_PATH} entry for {entry['path']} has mode "
            f"{entry['mode']!r}; only 'whole' is allowed"
        )
    path = Path(entry["path"])
    if path == Path(MANIFEST_PATH):
        raise CheckError(f"{MANIFEST_PATH} must never list itself")
    _allowed_target(path)
    _validate_source(Path(entry["source"]))
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
    return {
        "path": path.as_posix(),
        "owner": "skills",
        "source": Path(entry["source"]).as_posix(),
        "mode": "whole",
        "sha256": digest,
        "bytes": size,
    }


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
            raise CheckError(f"{MANIFEST_PATH} lists {canonical['path']} twice")
        seen.add(canonical["path"])
        validated.append(canonical)
    return validated


def _manifest_bytes(entries):
    """Serialize the manifest deterministically (sorted, two spaces, one `\\n`)."""
    ordered = sorted(entries, key=lambda item: item["path"])
    payload = {"version": 1, "entries": ordered}
    return (json.dumps(payload, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def _write_atomic(target, data):
    """Write *data* so each file appears whole or not at all."""
    descriptor, temporary = tempfile.mkstemp(
        dir=target.parent, prefix=".gen_skills-"
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


def _classify_produced(root, target, manifest_by_path, check):
    """Classify one produced target; return `(record, payload)`.

    A whole-file target that the canonical tree still produces is a CREATE in
    write mode even when the manifest lists it, so a deleted mirror file is
    repaired by the documented command. Check mode keeps reporting that state
    as DELETED so the drift never passes silently.
    """
    path = target["path"]
    destination = root / path
    _component_conflict(root, Path(path))
    listed = path in manifest_by_path

    if not destination.exists():
        if listed and check:
            return (
                {
                    "path": path,
                    "status": "DELETED",
                    "reason": "manifest-listed file is absent on disk",
                },
                None,
            )
        return (
            {
                "path": path,
                "status": "CREATE",
                "reason": (
                    "manifest-listed file is absent; recreating it"
                    if listed
                    else "target does not exist"
                ),
            },
            target["data"],
        )
    if not destination.is_file():
        return (
            {
                "path": path,
                "status": "ERROR",
                "reason": "target exists and is not a regular file",
            },
            None,
        )
    try:
        existing = destination.read_bytes()
    except OSError as exc:
        raise CheckError(f"cannot read {path}: {exc}") from exc
    if existing == target["data"]:
        return (
            {
                "path": path,
                "status": "UNCHANGED",
                "reason": "target bytes are identical",
            },
            None,
        )
    return (
        {
            "path": path,
            "status": "MODIFIED",
            "reason": "target bytes differ",
        },
        target["data"],
    )


def _carries_generated_marker(target, path):
    """Return whether *target* carries the marker at the documented position."""
    try:
        text = target.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False
    lines = text.splitlines()
    if Path(path).name == "SKILL.md":
        if not lines or lines[0] != "---":
            return False
        for index in range(1, len(lines)):
            if lines[index] == "---":
                return index + 1 < len(lines) and lines[index + 1] == GENERATED_HEADER
        return False
    return bool(lines) and lines[0] == GENERATED_HEADER


def _classify_orphan(root, entry, check):
    """Classify one manifest-listed path no canonical file produces.

    Check mode reports ORPHAN and stops. Write mode removes the file only when
    it exists and carries the generated marker at the documented position
    (T-09-08); any other orphan is reported as ORPHAN and blocks the run.
    """
    path = entry["path"]
    target = root / path
    _component_conflict(root, Path(path))
    if check:
        return (
            {
                "path": path,
                "status": "ORPHAN",
                "reason": "the manifest lists a path no canonical file produces",
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
    if not _carries_generated_marker(target, path):
        return (
            {
                "path": path,
                "status": "ORPHAN",
                "reason": (
                    "orphan does not carry the generated marker; refusing to "
                    "delete it"
                ),
            },
            None,
        )
    return (
        {
            "path": path,
            "status": "DELETE",
            "reason": "orphan carries the generated marker",
        },
        target,
    )


def _build_plan(root, check):
    """Classify every target and the manifest; write nothing.

    Returns `(records, writes, deletes, manifest_write)`. *writes* maps a path
    to `(target, bytes)`; *deletes* is a list of `Path`s; *manifest_write* is
    the manifest bytes to write, or `None` when the committed copy is in sync.
    """
    produced = _build_targets(root)
    manifest_entries = _load_manifest(root)
    manifest_by_path = {entry["path"]: entry for entry in manifest_entries}

    records = []
    writes = {}
    deletes = []
    for path in sorted(produced):
        record, payload = _classify_produced(
            root, produced[path], manifest_by_path, check
        )
        records.append(record)
        if payload is not None:
            writes[path] = (root / path, payload)

    orphans = {
        entry["path"]: entry
        for entry in manifest_entries
        if entry["path"] not in produced
    }
    for path in sorted(orphans):
        record, delete = _classify_orphan(root, orphans[path], check)
        records.append(record)
        if delete is not None:
            deletes.append(delete)

    new_entries = [
        _manifest_entry(
            path=path, source=target["source"], data=target["data"]
        )
        for path, target in produced.items()
    ]
    manifest_data = _manifest_bytes(new_entries)

    manifest_target = root / MANIFEST_PATH
    _component_conflict(root, Path(MANIFEST_PATH))
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
        prog="gen_skills",
        description="Generate the .agents/skills mirror from .claude/skills.",
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
        root = resolve_root(args.dir)
        records, writes, deletes, manifest_write = _build_plan(root, args.check)
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

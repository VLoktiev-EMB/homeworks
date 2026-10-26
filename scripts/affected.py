#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["PyYAML==6.0.3"]
# ///
"""Map a git diff to the build and simulation matrix Phase 8 feeds to CI.

The mapper answers one question: given the paths a pull request changed, which
PlatformIO environments must be built, and which must be simulated? It reads
the dependency graph from `platformio.ini` `lib_deps` plus each
`lib/<name>/library.json`, through the one reader set extracted in 05-01
(`scripts/metadata/platformio.py`), so the architecture gate and the matrix can
never disagree about what depends on what (D-23).

Fanout table (D-24, with the explicit no-build-impact reading of RESEARCH Open
Question 1). Each entry reads `<changed path> -> <effect>`:

- `.planning/`, `docs/`, `.github/`, `.claude/`, `.agents/`,
  `templates/views/`, `boards/`, `.skill-state/`, or exactly `README.md`,
  `AGENTS.md`, `LICENSE`, `generated.manifest`, `generated.skills.manifest`,
  `homeworks.code-workspace`, `scripts/gen_skills.py`,
  `scripts/serial_capture.py` -> no build, no simulation
- `homeworks/<id>/...` -> that project's environments
- `lib/<name>/...` -> every project whose `lib_deps` names `<name>`, transitively
  through `library.json` `dependencies`
- exactly `platformio.shared.ini`, or `partitions/...`, `scripts/pio/...`,
  `schema/...`, `scripts/affected.py` -> every project
- anything else -> every project (fail-safe)

`NO_BUILD_IMPACT` is explicit and tested entry by entry. It exists because
every generated-view pull request rewrites `generated.manifest`; without the
set, that one path would widen to all 30+ homeworks and rebuild the tree for a
documentation edit. The Phase 9 entries follow the same rule: `.claude/skills/`
and `.agents/skills/` are authored or generated Markdown, `scripts/gen_skills.py`
writes only that Markdown, and `.skill-state/` is untracked checkpoint state.
These paths are view, documentation and skill inputs, never compilation
inputs. The fail-safe stays: an unrecognised path widens, so an unknown shared
input can never silently skip a build (T-5-12, T-5-32).

The project set is every `homeworks/*/` directory plus the single top-level
`tests/` project when `tests/platformio.ini` exists. `tests/` is a real
consumer of `common`, `port` and `host`, so a `lib/**` change must reach it; it
has no `homework.yaml`, so it contributes to `build` only.

The mapper is read-only. It never invokes PlatformIO, never reads the clock,
never writes to the tree and never touches the network; two runs over the same
input print byte-identical output. Path names from a diff are contributor
controlled, so an absolute path, a Windows-absolute path or any `..` segment is
treated as an unrecognised shared input and widens the set instead of being
read (T-5-11).

Output:
  `--format json` (default) prints one object
  `{"build": [{"project", "env", "framework"}], "simulate": [...]}` sorted by
  `(project, env)`. `--format paths` prints `build <project> <env> <framework>`
  lines and then `simulate <project> <env> <framework>` lines. Stdout carries
  the payload and nothing else, because Phase 8 pipes it into `fromJson(...)`;
  every diagnostic goes to stderr.

Usage:
  uv run scripts/affected.py [--dir PATH] [--paths-from PATH | --base REV]
                             [--format {json,paths}]

Exit codes:
  0  success
  1  content problem: a diff under `homeworks/<id>/` for a directory that
     contains `homework.yaml` or a source file but has no `platformio.ini`
  2  usage or environment error (bad arguments, an unreadable `--paths-from`
     file, a failing `git diff`, an unreadable INI or metadata document)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import yaml  # noqa: E402

from scripts.metadata.errors import CheckError  # noqa: E402
from scripts.metadata.paths import relative_path, resolve_root  # noqa: E402
from scripts.metadata.platformio import (  # noqa: E402
    dep_names,
    load_ini,
    option,
    preload_extra_configs,
)
from scripts.metadata.yaml_loader import StrictSafeLoader  # noqa: E402

# Paths that feed the authored documentation and the generated views, never a
# PlatformIO build. Directory entries end with `/` and match by prefix; a file
# entry matches exactly, so `boards/` cannot match `boards-notes.md`. The set is
# deliberately explicit: an unknown path still widens (T-5-12).
NO_BUILD_IMPACT = (
    ".planning/",
    "docs/",
    ".github/",
    "templates/views/",
    "boards/",
    "README.md",
    "AGENTS.md",
    "LICENSE",
    "generated.manifest",
    "homeworks.code-workspace",
    # Phase 9: skills are authored or generated Markdown, and the generator
    # writes only that Markdown; the checkpoint state is untracked. None of
    # them is a PlatformIO build input.
    ".claude/",
    ".agents/",
    "generated.skills.manifest",
    ".skill-state/",
    # Named explicitly because an unrecognised path widens the matrix: a
    # generator-only pull request must not rebuild every project.
    "scripts/gen_skills.py",
    # The skill runtime helper captures serial output; it is never a
    # compilation input.
    "scripts/serial_capture.py",
)

# Shared inputs every project consumes. `scripts/affected.py` names itself so a
# change to the mapper rebuilds the tree rather than trusting its own logic.
WIDEN_ALL = (
    "platformio.shared.ini",
    "partitions/",
    "scripts/pio/",
    "schema/",
    "scripts/affected.py",
)

# `simulation.tool` values that mean "this project is not simulated".
SIMULATE_OFF = ("none",)

# The source suffixes `check_architecture.py` already treats as project content.
SOURCE_SUFFIXES = (".c", ".h", ".cpp", ".cc", ".hpp", ".ino")

WINDOWS_ABSOLUTE = re.compile(r"^[A-Za-z]:[\\/]")


def _safe_relative(raw):
    """Return the repository-relative POSIX spelling, or `None` when unsafe.

    A path is unsafe when it is absolute, Windows-absolute or carries a `..`
    segment anywhere. Such a path is never read and never echoed: the caller
    widens the matrix instead (T-5-11). `./` and a trailing `/` are normalised
    away, so `homeworks/<id>/` behaves exactly like `homeworks/<id>`.
    """
    if not raw:
        return None
    normalised = raw.replace("\\", "/")
    if (
        raw.startswith("\\\\")
        or normalised.startswith("/")
        or WINDOWS_ABSOLUTE.match(normalised)
    ):
        return None
    segments = normalised.split("/")
    if any(segment == ".." for segment in segments):
        return None
    cleaned = [segment for segment in segments if segment not in ("", ".")]
    if not cleaned:
        return None
    return "/".join(cleaned)


def _read_paths_file(path):
    """Read changed paths from a file, NUL- or newline-separated.

    A file containing a NUL byte is `-z`-shaped; otherwise it is line-shaped.
    Every token is trimmed and an empty token is dropped. Decoding tolerates a
    non-UTF-8 name with `surrogateescape` so one odd path cannot abort the run.
    """
    try:
        data = Path(path).read_bytes()
    except OSError as exc:
        raise CheckError(f"cannot read --paths-from {path}: {exc}") from exc
    separator = b"\0" if b"\0" in data else b"\n"
    changed = []
    for token in data.split(separator):
        candidate = token.decode("utf-8", "surrogateescape").strip()
        if candidate:
            changed.append(candidate)
    return changed


def _git_paths(root, base):
    """Return the changed paths git reports, NUL-separated and decoded.

    `--base REV` diffs `REV...HEAD`; without it the working tree is compared
    with `HEAD`. The `-z` form survives a space or newline in a path.
    """
    if base:
        command = ["git", "diff", "--name-only", "-z", f"{base}...HEAD"]
    else:
        command = ["git", "diff", "--name-only", "-z", "HEAD"]
    try:
        completed = subprocess.run(
            command, cwd=str(root), capture_output=True, check=False
        )
    except OSError as exc:
        raise CheckError(f"cannot execute git: {exc}") from exc
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", "replace").strip()
        raise CheckError(f"git diff failed: {detail or 'unknown error'}")
    return [
        token.decode("utf-8", "surrogateescape")
        for token in completed.stdout.split(b"\0")
        if token
    ]


def _changed_paths(root, args):
    """Return the changed paths from the first source the arguments name."""
    if args.paths_from:
        return _read_paths_file(args.paths_from)
    return _git_paths(root, args.base)


def _has_homework_content(directory):
    """Return whether *directory* holds metadata or a source file.

    A directory with neither is still scaffolding and is skipped; one that has
    `homework.yaml` or a source file but no `platformio.ini` is a real project
    the matrix cannot represent.
    """
    if (directory / "homework.yaml").is_file():
        return True
    for current, dirnames, filenames in os.walk(directory, followlinks=False):
        dirnames[:] = sorted(
            name
            for name in dirnames
            if not (Path(current) / name).is_symlink()
        )
        for filename in filenames:
            path = Path(current) / filename
            if path.is_symlink():
                continue
            if filename.endswith(SOURCE_SUFFIXES):
                return True
    return False


def _simulation_tool(path, project_id):
    """Return `simulation.tool` from *path*, or `"none"` when it is absent.

    The document is parsed with `StrictSafeLoader`, so a duplicated `simulation`
    key is a `CheckError` (exit 2) rather than a silently chosen last value
    (T-5-13). A project with no `homework.yaml`, such as `tests`, is `"none"`.
    """
    if not path.is_file():
        return "none"
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise CheckError(f"cannot read {project_id}/homework.yaml: {exc}") from exc
    try:
        document = yaml.load(text, Loader=StrictSafeLoader)
    except yaml.YAMLError as exc:
        raise CheckError(f"{project_id}/homework.yaml: {exc}") from exc
    if not isinstance(document, dict):
        return "none"
    simulation = document.get("simulation")
    if not isinstance(simulation, dict):
        return "none"
    tool = simulation.get("tool")
    return tool if isinstance(tool, str) and tool else "none"


def _project_record(root, directory, project_id):
    """Return one project record, or `None` for a skipped directory.

    The record carries its `(env, framework)` pairs, the library names it
    depends on directly, its `simulation.tool` value and whether it is a real
    project the matrix cannot build (no `platformio.ini`).
    """
    ini = directory / "platformio.ini"
    display = f"{project_id}/platformio.ini"
    if not ini.is_file():
        if not _has_homework_content(directory):
            return None
        return {
            "project": project_id,
            "envs": [],
            "deps": set(),
            "tool": "none",
            "incomplete": True,
        }

    parser = load_ini(ini, display)
    preload_extra_configs(parser, directory, display)

    envs = []
    deps = set()
    for section in parser.sections():
        if not section.startswith("env:"):
            continue
        env = section[len("env:") :]
        framework = option(parser, section, "framework")
        if not framework:
            if option(parser, section, "platform") == "native":
                framework = "native"
            else:
                raise CheckError(
                    f"{display}: environment {env!r} has no resolvable framework"
                )
        envs.append((env, framework))
        deps.update(dep_names(option(parser, section, "lib_deps")))

    return {
        "project": project_id,
        "envs": envs,
        "deps": deps,
        "tool": _simulation_tool(directory / "homework.yaml", project_id),
        "incomplete": False,
    }


def _projects(root):
    """Return every project record: each `homeworks/*/` plus top-level `tests`.

    `tests` joins the set only when `tests/platformio.ini` exists, because it
    is the top-level native consumer of `common`, `port` and `host`.
    """
    projects = []
    homeworks = root / "homeworks"
    if homeworks.is_dir():
        for directory in sorted(
            homeworks.iterdir(), key=lambda item: item.as_posix()
        ):
            if directory.is_symlink() or not directory.is_dir():
                continue
            record = _project_record(
                root, directory, relative_path(root, directory)
            )
            if record is not None:
                projects.append(record)
    tests = root / "tests"
    if (tests / "platformio.ini").is_file():
        projects.append(_project_record(root, tests, "tests"))
    return projects


def _dependency_names(document):
    """Return the library names a `library.json` document depends on.

    The mapping form names its keys; the list form names its strings (or the
    `name` of a mapping entry). A missing key is a leaf (RESEARCH Pitfall 9).
    """
    if not isinstance(document, dict):
        return set()
    raw = document.get("dependencies")
    names = set()
    if isinstance(raw, str):
        names.add(raw)
    elif isinstance(raw, dict):
        names.update(str(key) for key in raw)
    elif isinstance(raw, list):
        for item in raw:
            if isinstance(item, str):
                names.add(item)
            elif isinstance(item, dict) and isinstance(item.get("name"), str):
                names.add(item["name"])
    return names


def _library_dependencies(root):
    """Map every `lib/<name>/library.json` to its direct dependency names."""
    dependencies = {}
    libraries = root / "lib"
    if not libraries.is_dir():
        return dependencies
    for manifest in sorted(
        libraries.glob("*/library.json"), key=lambda item: item.as_posix()
    ):
        name = manifest.parent.name
        try:
            text = manifest.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            raise CheckError(f"cannot read lib/{name}/library.json: {exc}") from exc
        try:
            document = json.loads(text)
        except json.JSONDecodeError as exc:
            raise CheckError(
                f"lib/{name}/library.json is not valid JSON: {exc}"
            ) from exc
        dependencies[name] = _dependency_names(document)
    return dependencies


def _closure(names, dependencies):
    """Return *names* plus their transitive library dependencies.

    A `seen` set bounds the walk, so a malformed circular `library.json` chain
    terminates instead of recursing without bound (T-5-13).
    """
    resolved = set()
    pending = list(names)
    while pending:
        name = pending.pop()
        if name in resolved:
            continue
        resolved.add(name)
        pending.extend(dependencies.get(name, ()))
    return resolved


def _consumers(projects, dependencies):
    """Map each library name to the set of project ids that consume it."""
    consumers = {}
    for project in projects:
        for library in _closure(project["deps"], dependencies):
            consumers.setdefault(library, set()).add(project["project"])
    return consumers


def _matches(relative, rules):
    """Match *relative* against a rule set: prefix for directories, exact for files."""
    for rule in rules:
        if rule.endswith("/"):
            if relative.startswith(rule):
                return True
        elif relative == rule:
            return True
    return False


def _fan_out(root, paths, projects, consumers):
    """Return the set of project ids a changed-path list selects.

    The table is applied in order: no-build-impact first, then the specific
    rules, then the fail-safe widen. An unsafe path and any unrecognised path
    both widen (T-5-11, T-5-12).
    """
    every = {project["project"] for project in projects}
    selected = set()
    for raw in paths:
        relative = _safe_relative(raw)
        if relative is None:
            selected.update(every)
            continue
        if _matches(relative, NO_BUILD_IMPACT):
            continue
        if _matches(relative, WIDEN_ALL):
            selected.update(every)
            continue

        segments = relative.split("/")
        if segments[0] == "homeworks" and len(segments) >= 2:
            directory = root / "homeworks" / segments[1]
            project = "homeworks/" + segments[1]
            if directory.is_symlink() or not directory.is_dir():
                selected.update(every)
            elif project in every:
                selected.add(project)
            continue
        if segments[0] == "lib" and len(segments) >= 2:
            matched = consumers.get(segments[1])
            if matched:
                selected.update(matched)
            else:
                selected.update(every)
            continue
        selected.update(every)
    return selected


def _entries(selected, projects):
    """Build the sorted `build` and `simulate` lists for *selected* projects.

    A native environment appears in `build` only. `simulate` drops native
    environments and every project whose `simulation.tool` is `none`.
    """
    build = []
    simulate = []
    for project in projects:
        if project["project"] not in selected:
            continue
        for env, framework in project["envs"]:
            entry = {
                "project": project["project"],
                "env": env,
                "framework": framework,
            }
            build.append(entry)
            if framework == "native" or env == "native":
                continue
            if project["tool"] in SIMULATE_OFF:
                continue
            simulate.append(dict(entry))
    build.sort(key=lambda item: (item["project"], item["env"]))
    simulate.sort(key=lambda item: (item["project"], item["env"]))
    return {"build": build, "simulate": simulate}


def _render(payload, fmt):
    """Render the payload as JSON (default) or one line per entry."""
    if fmt == "paths":
        lines = [
            f"build {entry['project']} {entry['env']} {entry['framework']}"
            for entry in payload["build"]
        ]
        lines.extend(
            f"simulate {entry['project']} {entry['env']} {entry['framework']}"
            for entry in payload["simulate"]
        )
        return "".join(line + "\n" for line in lines)
    return json.dumps(payload, indent=2) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Map a git diff to the build and simulation matrix."
    )
    parser.add_argument(
        "--dir",
        metavar="PATH",
        help="repository root (default: git rev-parse --show-toplevel)",
    )
    source = parser.add_mutually_exclusive_group()
    source.add_argument(
        "--paths-from",
        metavar="PATH",
        help="read changed paths from a file instead of invoking git",
    )
    source.add_argument(
        "--base",
        metavar="REV",
        help="diff REV...HEAD instead of the working tree against HEAD",
    )
    parser.add_argument(
        "--format",
        choices=("json", "paths"),
        default="json",
        help="output format (default: json)",
    )
    args = parser.parse_args(argv)

    try:
        root = resolve_root(args.dir)
        paths = _changed_paths(root, args)
        projects = _projects(root)
        consumers = _consumers(projects, _library_dependencies(root))
        selected = _fan_out(root, paths, projects, consumers)
        incomplete = [
            project["project"]
            for project in projects
            if project["incomplete"] and project["project"] in selected
        ]
        if incomplete:
            for project in incomplete:
                print(
                    f"ERROR: {project} has no platformio.ini; add the file or "
                    "move the change outside the project",
                    file=sys.stderr,
                )
            return 1
        payload = _entries(selected, projects)
    except CheckError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    sys.stdout.write(_render(payload, args.format))
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Write one root compilation database that names every shared-library source.

clangd resolves a file by walking upward and using the first
`compile_commands.json` it finds. The databases that already describe the
shared libraries are siblings — under `tests/`, `homeworks/<id>/`
and `templates/homework-espidf/` — so a source under `lib/` has none. This
script reads those three databases, keeps exactly one entry per `lib/**` source,
and writes a root `compile_commands.json` that clangd discovers from `lib/`.

Each `lib/` subtree is served by its own representative context, because one
compile command per path is a physical constraint:

  common, port, host   tests/compile_commands.json          (native)
  arduino              homeworks/<id>/...                   (Arduino)
  espidf               templates/homework-espidf/...        (ESP-IDF)

The script reads only. It runs no PlatformIO command and writes exactly one
file, through a sibling temporary file plus an atomic replace, so a reader
never sees a half-written database.

Usage:
  python3 scripts/gen_clangd_db.py [--root PATH]

Exit codes (the same 0/1/2 vocabulary as `scripts/clang-tidy-db`):
  0  a complete database was written
  1  a source database is absent, or a `lib/` source has no selected entry
  2  usage or environment error (unusable root, unreadable or malformed
     database, or a `lib/` subtree the mapping does not name)
"""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import sys
from pathlib import Path

OUTPUT_NAME = "compile_commands.json"

# The fields a clangd entry needs. `output` is PlatformIO bookkeeping and is
# dropped; a relative `-o` or include path stays resolvable because `directory`
# is copied verbatim.
ENTRY_FIELDS = ("directory", "command", "arguments")

SOURCE_SUFFIXES = (".c", ".cpp")


def find_arduino_source(root: Path) -> tuple[Path, str]:
    """Find an Arduino compile commands database from homeworks/ or provide a remedy."""
    homeworks_dir = root / "homeworks"
    if homeworks_dir.is_dir():
        # First priority: an active homework with an existing compile_commands.json
        for hw in sorted(homeworks_dir.iterdir()):
            if not hw.is_dir():
                continue
            db_path = hw / "compile_commands.json"
            if db_path.is_file():
                return (
                    db_path.relative_to(root),
                    f"pio run -d homeworks/{hw.name} -t compiledb",
                )
        # Second priority: an active homework directory without compile_commands.json
        for hw in sorted(homeworks_dir.iterdir()):
            if not hw.is_dir():
                continue
            hw_yaml = hw / "homework.yaml"
            if hw_yaml.is_file():
                return (
                    (hw / "compile_commands.json").relative_to(root),
                    f"pio run -d homeworks/{hw.name} -t compiledb",
                )
    return (
        Path("homeworks") / "<id>" / "compile_commands.json",
        "pio run -d homeworks/<id> -t compiledb (for an active Arduino homework)",
    )


def get_sources(root: Path) -> list[tuple[tuple[str, ...], Path, str]]:
    """Return the ordered source groups for the given repository root.

    One ordered group per representative context. Each triple is (subtrees,
    source database, the exact PlatformIO command that writes it). Order matters:
    a path named by two databases belongs to the first group whose subtree holds
    it, so `lib/common` stays in the native context even though the Arduino
    database describes it too.
    """
    arduino_db, arduino_remedy = find_arduino_source(root)
    return [
        (
            ("common", "port", "host"),
            Path("tests") / "compile_commands.json",
            "pio run -d tests -e native -t compiledb",
        ),
        (
            ("arduino",),
            arduino_db,
            arduino_remedy,
        ),
        (
            ("espidf",),
            Path("templates") / "homework-espidf" / "compile_commands.json",
            "pio run -d templates/homework-espidf -e esp32s3_espidf -t compiledb",
        ),
    ]


class EnvironmentProblem(Exception):
    """An unusable root or an unreadable database: exit 2, never a silent pass."""


class MissingInput(Exception):
    """A required database or an undescribed source: exit 1 with a remedy."""


def resolve_root(directory: str | None) -> Path:
    """Return the root to generate for, defaulting to the script's repository."""
    root = Path(directory) if directory else Path(__file__).resolve().parents[1]
    root = root.resolve()
    if not root.is_dir():
        raise EnvironmentProblem(f"not a directory: {root}")
    return root


def load_database(database: Path) -> list:
    """Read and shape-check one source database; a malformed file exits 2."""
    try:
        text = database.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise EnvironmentProblem(f"cannot read {database}: {exc}") from exc
    try:
        entries = json.loads(text)
    except json.JSONDecodeError as exc:
        raise EnvironmentProblem(f"cannot parse {database}: {exc}") from exc
    if not isinstance(entries, list):
        raise EnvironmentProblem(f"{database}: top level must be a list of entries")
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("file"), str):
            raise EnvironmentProblem(
                f"{database}: every entry must be an object with a string 'file'"
            )
    return entries


def resolved_file(entry: dict, root: Path) -> Path:
    """Resolve an entry's `file` the way the database declares it.

    A relative `file` is relative to that entry's own `directory`, never to the
    root. A `directory` that is itself relative is taken from the root, and a
    still-relative result is taken from the root as well.
    """
    source = Path(entry["file"])
    if not source.is_absolute():
        directory = entry.get("directory")
        base = Path(directory) if isinstance(directory, str) and directory else root
        if not base.is_absolute():
            base = root / base
        source = base / source
    if not source.is_absolute():
        source = root / source
    return source.resolve()


def _under(resolved: Path, base: Path) -> bool:
    """Return whether *resolved* lies at or below *base*."""
    try:
        resolved.relative_to(base)
    except ValueError:
        return False
    return True


def select_entries(
    root: Path, sources: list[tuple[tuple[str, ...], Path, str]] | None = None
) -> dict[Path, dict]:
    """Return one source entry per resolved `lib/` path; the first group wins."""
    if sources is None:
        sources = get_sources(root)
    selected: dict[Path, dict] = {}
    libraries = root / "lib"
    for subtrees, database, remedy in sources:
        path = root / database
        if not path.is_file():
            raise MissingInput(f"{path} is absent.\n  regenerate it with: {remedy}")
        entries = load_database(path)
        seen: set[Path] = set()
        for entry in entries:
            resolved = resolved_file(entry, root)
            if resolved in seen:
                continue
            if not any(_under(resolved, libraries / subtree) for subtree in subtrees):
                continue
            seen.add(resolved)
            selected.setdefault(resolved, entry)
    return selected


def unmapped_subtrees(
    root: Path, sources: list[tuple[tuple[str, ...], Path, str]] | None = None
) -> list[str]:
    """Return every child directory of `lib/` that no group names."""
    if sources is None:
        sources = get_sources(root)
    mapped = {subtree for subtrees, _database, _remedy in sources for subtree in subtrees}
    libraries = root / "lib"
    if not libraries.is_dir():
        return []
    return sorted(
        child.name
        for child in libraries.iterdir()
        if child.is_dir() and child.name not in mapped
    )


def missing_sources(
    root: Path,
    selected: dict[Path, dict],
    sources: list[tuple[tuple[str, ...], Path, str]] | None = None,
) -> list[tuple[Path, str]]:
    """Return every `.c`/`.cpp` under `lib/` that has no selected entry."""
    if sources is None:
        sources = get_sources(root)
    remedies = {
        subtree: remedy for subtrees, _database, remedy in sources for subtree in subtrees
    }
    libraries = root / "lib"
    missing: list[tuple[Path, str]] = []
    if not libraries.is_dir():
        return missing
    for source in sorted(libraries.rglob("*")):
        if not source.is_file() or source.suffix not in SOURCE_SUFFIXES:
            continue
        if source.resolve() in selected:
            continue
        subtree = source.relative_to(libraries).parts[0]
        missing.append((source, remedies.get(subtree, "")))
    return missing


def write_database(database: Path, entries: list) -> None:
    """Write the database atomically: a reader sees the old file or the new one."""
    payload = json.dumps(entries, indent=2) + "\n"
    temporary = database.with_name(f"{database.name}.tmp")
    try:
        temporary.write_text(payload, encoding="utf-8")
        os.replace(temporary, database)
    except OSError as exc:
        with contextlib.suppress(OSError):
            temporary.unlink()
        raise EnvironmentProblem(f"cannot write {database}: {exc}") from exc


def run_generate(root: Path) -> tuple[int, list[str]]:
    """Return the exit status and the message lines for one root."""
    sources = get_sources(root)
    selected = select_entries(root, sources)
    unnamed = unmapped_subtrees(root, sources)
    if unnamed:
        raise EnvironmentProblem(
            "lib/ subtree has no compile-command source: " + ", ".join(unnamed)
        )

    missing = missing_sources(root, selected, sources)
    if missing:
        lines = [
            f"FAIL gen-clangd-db: {len(missing)} lib source(s) have no compile command:"
        ]
        for source, remedy in missing:
            lines.append(f"  {source}")
            lines.append(f"  regenerate it with: {remedy}")
        return 1, lines

    entries = []
    for path in sorted(selected, key=lambda item: item.as_posix()):
        source = selected[path]
        entry = {field: source[field] for field in ENTRY_FIELDS if field in source}
        entry["file"] = path.as_posix()
        entries.append(entry)

    write_database(root / OUTPUT_NAME, entries)
    return 0, [
        f"PASS gen-clangd-db: {len(entries)} entries from {len(sources)} database(s)"
    ]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate the root compilation database for lib/."
    )
    parser.add_argument(
        "--root",
        metavar="PATH",
        help="repository root to generate for (default: this script's repository)",
    )
    args = parser.parse_args(argv)

    try:
        root = resolve_root(args.root)
        status, lines = run_generate(root)
    except MissingInput as exc:
        print(f"FAIL gen-clangd-db: {exc}")
        return 1
    except EnvironmentProblem as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    for line in lines:
        print(line)
    return status


if __name__ == "__main__":
    sys.exit(main())

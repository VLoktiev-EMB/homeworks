#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["PyYAML==6.0.3", "jsonschema==4.26.0"]
# ///
"""Verify the homework metadata contract.

`schema/homework.schema.json` is the machine-readable contract for every
`homeworks/<id>/homework.yaml`, and `scripts/metadata/contract.py` is the one
implementation that applies it (D-12). `schema/board-profile.schema.json` is the
contract for every `boards/<id>.yaml`, applied by
`scripts/metadata/board_profile.py` (D-27). This script is the thin entry point
for both families: it finds the documents, hands their text to the shared
modules, and renders the records. No validation rule lives here.

Usage:
  uv run scripts/check_metadata.py [--dir PATH] [--json] [PATH...]

Exit codes (a CI contract from Phase 8 onward):
  0  every scanned document satisfies the contract
  1  violation, reported as one or more ERROR records on stdout
  2  usage or environment error (bad arguments, missing document, missing or
     malformed schema, unreadable or inconsistent shared configuration)

A content problem inside a document — a symlinked document, an oversized file,
a YAML syntax error, a non-mapping payload, a duplicated key, a schema
violation, an `id` that disagrees with its directory, or a toolchain pin that
drifted from `platformio.shared.ini` — stays at exit 1. Only the environment
exits 2.

A positional argument selects the family it names. A path under `<root>/boards/`
that ends in `.yaml` is a board profile; anything else is a homework directory or
one of its contract files. When positionals are given, a family with no selected
path is scanned not at all: a board-only run never widens to every homework, and
a homework-only run never widens to every board profile. With no positionals
both families scan everything.

The checker is read-only: it never writes to the tree, never reads the clock,
and two consecutive runs produce byte-identical output. With `--json` it
prints one JSON array of `{"path", "status", "reason"}` objects and nothing
else, so Phase 8 CI can consume the same records without parsing prose (D-23).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.metadata.board_profile import (  # noqa: E402
    load_board_schema,
    validate_board_text,
)
from scripts.metadata.contract import (  # noqa: E402
    CheckError,
    load_schema,
    relative_path,
    resolve_root,
    validate_candidate,
    validate_homework_text,
    validate_task_text,
)


def _record(root, path, status, reason, line=0):
    """Render one record with a repository-relative POSIX path."""
    return {
        "path": relative_path(root, path),
        "status": status,
        "reason": reason,
        "line": line,
    }


def _relative_lexical(root, path):
    """Render *path* relative to *root* without following a symlink."""
    try:
        root_path = Path(os.path.abspath(root))
        candidate = Path(os.path.abspath(path))
        return candidate.relative_to(root_path).as_posix()
    except (ValueError, OSError):
        return Path(str(path)).name


def _lexical_record(root, path, status, reason, line=0):
    """A record whose display path is lexical, for a refused symlink."""
    item = _record(root, path, status, reason, line)
    item["path"] = _relative_lexical(root, path)
    return item


def _read_document(root, path):
    """Return `(text, failure_record)`; exactly one of the two is `None`.

    A symlinked document is refused without following or opening the target
    (CR-06), preventing information leaks from outside host files. A decode
    failure is a content problem on that document (exit 1). An unreadable file
    is an environment problem (exit 2), as before.
    """
    if path.is_symlink():
        return None, _lexical_record(
            root, path, "ERROR", f"{path.name} is a symlink; refusing to follow it"
        )
    try:
        return path.read_text(encoding="utf-8"), None
    except UnicodeDecodeError as exc:
        return None, _record(
            root, path, "ERROR", f"document is not valid UTF-8: {exc}"
        )
    except OSError as exc:
        raise CheckError(f"cannot read {path}: {exc}") from exc


def _validate_directory(root, directory):
    """Validate one `homeworks/<id>/` directory: both contract files in order.

    `homework.yaml` is read first because its `status` decides whether the
    `TODO` sentinel in `task.md` is legal (D-39). A directory that contains
    neither file is an ERROR on the directory path, never a silent skip.
    """
    homework = Path(directory) / "homework.yaml"
    task = Path(directory) / "task.md"
    has_homework = homework.is_symlink() or homework.is_file()
    has_task = task.is_symlink() or task.is_file()

    if not has_homework and not has_task:
        return [
            _record(
                root,
                directory,
                "ERROR",
                "directory contains neither homework.yaml nor task.md",
            )
        ]

    records = []
    if not has_homework:
        records.append(_record(root, homework, "ERROR", "homework.yaml is missing"))
        homework_text = None
    else:
        homework_text, failure = _read_document(root, homework)
        if failure is not None:
            records.append(failure)

    if not has_task:
        records.append(_record(root, task, "ERROR", "task.md is missing"))
        task_text = None
    else:
        task_text, failure = _read_document(root, task)
        if failure is not None:
            records.append(failure)

    if homework_text is not None and task_text is not None:
        records.extend(
            validate_candidate(
                homework_text,
                task_text,
                root=root,
                homework_path=homework,
                task_path=task,
            )
        )
    elif homework_text is not None:
        records.extend(
            validate_homework_text(homework_text, root=root, path=homework)
        )
    elif task_text is not None:
        # Without a readable homework.yaml the status is unknown; treat the
        # sentinel as illegal so nothing hides behind a broken sibling.
        records.extend(
            validate_task_text(
                task_text, status=None, reference=None, path=task, root=root
            )
        )
    return records


def _directories(root, positionals=None):
    """Return the sorted `homeworks/<id>/` directories this run should read.

    With `positionals` `None` every direct child directory of `homeworks/` is
    scanned. With a list — even an empty one — exactly the named directories are
    used, so a board-only invocation never widens to every homework. A
    positional may name that directory, its `homework.yaml` or its `task.md`. A
    path that does not resolve to a directory is a usage error (exit 2).
    """
    root = Path(root)
    if positionals is not None:
        targets = []
        for raw in positionals:
            candidate = Path(raw)
            if not candidate.is_absolute():
                candidate = root / candidate
            if candidate.is_file():
                candidate = candidate.parent
            if not candidate.is_dir():
                raise CheckError(f"no homework directory at {raw}")
            targets.append(candidate)
    else:
        homeworks = root / "homeworks"
        targets = (
            [
                path
                for path in sorted(homeworks.iterdir(), key=lambda item: item.as_posix())
                if path.is_dir()
            ]
            if homeworks.is_dir()
            else []
        )

    unique = {}
    for target in targets:
        unique[target.resolve()] = target
    return sorted(unique.values(), key=lambda item: item.as_posix())


def _relative_lexical(root, path):
    """Render *path* relative to *root* without resolving a symlink.

    A refused symlink must be named by the path the repository contains, not by
    whatever file it points at. Resolution would either echo the target inside
    the root or degrade to a bare name when the target is outside; the lexical
    form keeps the `boards/<stem>.yaml` identity and never leaks an absolute
    path.
    """
    root = Path(os.path.abspath(root))
    candidate = Path(os.path.abspath(path))
    try:
        return candidate.relative_to(root).as_posix()
    except ValueError:
        return candidate.name


def _partition_paths(root, paths):
    """Split positional paths into the board and homework families.

    A path is a board profile when it is lexically under `<root>/boards/` and
    names a `.yaml` file. The classification is lexical on purpose: a symlinked
    document must still be classified as a board path, so `_board_documents`
    can refuse it instead of following it into whatever family its target
    lives in.
    """
    root = Path(root)
    boards = root / "boards"
    board_paths = []
    homework_paths = []
    for raw in paths:
        candidate = Path(raw)
        if not candidate.is_absolute():
            candidate = root / candidate
        normalized = Path(os.path.abspath(candidate))
        if normalized.suffix == ".yaml" and boards in normalized.parents:
            board_paths.append(raw)
        else:
            homework_paths.append(raw)
    return board_paths, homework_paths


def _board_documents(root, positionals=None):
    """Return `(documents, records)` for this run's board profiles.

    `documents` is the sorted list of regular `boards/*.yaml` files to read.
    `records` carries one ERROR record for each selected document that is a
    symlink; such a document is never followed, matching the homework checker's
    lexical, containment-only posture.

    With `positionals` `None` the whole `boards/` directory is scanned. With a
    list — even an empty one — exactly the named documents are used, so a
    homework-only invocation never widens to every board profile. A missing
    `boards/` is not an error, because the metadata fixtures carry only
    `schema/` and `platformio.shared.ini`; a `boards/` that exists and is a
    symlink or is not a directory is an environment error (exit 2).
    """
    root = Path(root)
    boards = root / "boards"

    if positionals is None:
        if boards.is_symlink():
            raise CheckError(
                f"{relative_path(root, boards)} is a symlink; refusing to follow it"
            )
        if not boards.exists():
            return [], []
        if not boards.is_dir():
            raise CheckError(f"{relative_path(root, boards)} is not a directory")
        candidates = sorted(
            (path for path in boards.iterdir() if path.suffix == ".yaml"),
            key=lambda item: item.as_posix(),
        )
        strict = False
    else:
        candidates = []
        for raw in positionals:
            candidate = Path(raw)
            if not candidate.is_absolute():
                candidate = root / candidate
            candidates.append(candidate)
        strict = True

    documents = []
    records = []
    for candidate in candidates:
        if candidate.is_symlink():
            records.append(
                {
                    "path": _relative_lexical(root, candidate),
                    "status": "ERROR",
                    "reason": "board document is a symlink; refusing to follow it",
                    "line": 0,
                }
            )
            continue
        if not candidate.is_file():
            if strict:
                raise CheckError(
                    f"no board profile at {_relative_lexical(root, candidate)}"
                )
            continue
        documents.append(candidate)

    unique = {}
    for document in documents:
        unique[document.as_posix()] = document
    ordered = sorted(unique.values(), key=lambda item: item.as_posix())
    return ordered, records


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Verify the homework metadata contract."
    )
    parser.add_argument(
        "--dir",
        metavar="PATH",
        help="repository root to check (default: git rev-parse --show-toplevel)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit one JSON array of records on stdout (no summary line)",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        metavar="PATH",
        help=(
            "homework directory, homework.yaml, or boards/<id>.yaml to check "
            "(default: every document of both families)"
        ),
    )
    args = parser.parse_args(argv)

    try:
        root = resolve_root(args.dir)
        load_schema(root)
        load_board_schema(root)
        if args.paths:
            board_paths, homework_paths = _partition_paths(root, args.paths)
        else:
            board_paths = homework_paths = None
        board_documents, records = _board_documents(root, board_paths)
        for document in board_documents:
            text, failure = _read_document(root, document)
            if failure is not None:
                records.append(failure)
                continue
            records.extend(validate_board_text(text, root=root, path=document))
        for directory in _directories(root, homework_paths):
            records.extend(_validate_directory(root, directory))
    except CheckError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    records.sort(key=lambda item: item["path"])
    violations = sum(1 for record in records if record["status"] == "ERROR")

    if args.json:
        payload = [
            {
                "path": record["path"],
                "status": record["status"],
                "reason": record["reason"],
            }
            for record in records
        ]
        print(json.dumps(payload, indent=2))
        return 1 if violations else 0

    for record in records:
        print(f"{record['path']}: {record['status']} — {record['reason']}")

    print()
    if violations:
        print(f"FAIL: {violations} metadata violation(s)")
        return 1
    print("PASS: metadata contract satisfied")
    return 0


if __name__ == "__main__":
    sys.exit(main())

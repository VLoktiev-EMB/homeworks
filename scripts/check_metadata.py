#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["PyYAML==6.0.3", "jsonschema==4.26.0"]
# ///
"""Verify the homework metadata contract.

`schema/homework.schema.json` is the machine-readable contract for every
`homeworks/<id>/homework.yaml`, and `scripts/metadata/contract.py` is the one
implementation that applies it (D-12). This script is the thin entry point: it
finds the documents, hands their text to the shared module, and renders the
records. No validation rule lives here.

Usage:
  uv run scripts/check_metadata.py [--dir PATH] [PATH...]

Exit codes (a CI contract from Phase 8 onward):
  0  every scanned document satisfies the contract
  1  violation, reported as one or more ERROR records on stdout
  2  usage or environment error (bad arguments, missing document, missing or
     malformed schema, unreadable or inconsistent shared configuration)

A content problem inside a document — an oversized file, a YAML syntax error,
a non-mapping payload, a duplicated key, a schema violation, an `id` that
disagrees with its directory, or a toolchain pin that drifted from
`platformio.shared.ini` — stays at exit 1. Only the environment exits 2.

The checker is read-only: it never writes to the tree, never reads the clock,
and two consecutive runs produce byte-identical output.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.metadata.contract import (  # noqa: E402
    CheckError,
    load_schema,
    relative_path,
    resolve_root,
    validate_homework_text,
)


def _targets(root, positionals):
    """Return the sorted `homework.yaml` paths this run should read.

    With no positional every `homeworks/*/homework.yaml` is scanned. A
    positional may name a homework directory or a document inside one. A path
    that does not resolve to a document is a usage error (exit 2).
    """
    root = Path(root)
    if positionals:
        targets = []
        for raw in positionals:
            candidate = Path(raw)
            if not candidate.is_absolute():
                candidate = root / candidate
            if candidate.is_dir():
                candidate = candidate / "homework.yaml"
            if not candidate.is_file():
                raise CheckError(f"no homework document at {raw}")
            targets.append(candidate)
    else:
        homeworks = root / "homeworks"
        targets = sorted(homeworks.glob("*/homework.yaml")) if homeworks.is_dir() else []

    unique = {}
    for target in targets:
        unique[target.resolve()] = target
    return sorted(unique.values(), key=lambda item: item.as_posix())


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
        "paths",
        nargs="*",
        metavar="PATH",
        help="homework directory or homework.yaml to check (default: all)",
    )
    args = parser.parse_args(argv)

    try:
        root = resolve_root(args.dir)
        load_schema(root)
        records = []
        for target in _targets(root, args.paths):
            try:
                text = target.read_text(encoding="utf-8")
            except UnicodeDecodeError as exc:
                records.append(
                    {
                        "path": relative_path(root, target),
                        "status": "ERROR",
                        "reason": f"document is not valid UTF-8: {exc}",
                        "line": 0,
                    }
                )
                continue
            except OSError as exc:
                raise CheckError(f"cannot read {target}: {exc}") from exc
            records.extend(validate_homework_text(text, root=root, path=target))
    except CheckError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    records.sort(key=lambda item: item["path"])
    for record in records:
        print(f"{record['path']}: {record['status']} — {record['reason']}")

    violations = sum(1 for record in records if record["status"] == "ERROR")
    print()
    if violations:
        print(f"FAIL: {violations} metadata violation(s)")
        return 1
    print("PASS: metadata contract satisfied")
    return 0


if __name__ == "__main__":
    sys.exit(main())

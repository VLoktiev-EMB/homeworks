#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["PyYAML==6.0.3"]
# ///
"""Verify the report and evidence contract.

`scripts/report/` holds the rules and the literal vocabulary; this script is the
only module that touches the filesystem, reads `homework.yaml` with PyYAML, and
decides the exit code. It deliberately declares PyYAML only: it reads metadata
values and never re-validates the schema, so importing
`scripts.metadata.contract` (which imports jsonschema at module scope) would
drag a second dependency into the hook environment (D-02).

Usage:
  uv run scripts/check_report.py [--dir PATH] [--json] [PATH...]

Exit codes (the vocabulary shared with `check_metadata.py`, D-04):
  0  every scanned homework satisfies the report contract
  1  a violation, reported as one or more ERROR records on stdout
  2  a usage or environment error (bad arguments, an unreadable file, a missing
     repository root)

A content problem inside a document stays at exit 1: an absent, empty or
symlinked report, a malformed `homework.yaml`, an inconsistent status pair, an
oversized report, or a structural rule failure. Only the environment exits 2.

A positional may name a homework directory or any document inside it; a file is
reduced to its parent directory exactly as `check_metadata.py` does. With no
positionals every direct child of `homeworks/` is scanned.

The checker is read-only: it never writes, never reads the clock, and two
consecutive runs produce byte-identical output. `--json` prints one array of
`{"path", "status", "rule", "line", "reason"}` objects and nothing else.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.metadata.errors import CheckError  # noqa: E402
from scripts.metadata.paths import relative_path, resolve_root  # noqa: E402
from scripts.metadata.render import read_regular_text  # noqa: E402
from scripts.metadata.yaml_loader import StrictSafeLoader  # noqa: E402
from scripts.report.contract import validate_report  # noqa: E402


def _record(root, path, status, rule, reason, line=0):
    """Render one record with a repository-relative POSIX path."""
    return {
        "path": relative_path(root, path),
        "status": status,
        "rule": rule,
        "line": line,
        "reason": reason,
    }


def _relative_lexical(root, path):
    """Render *path* relative to *root* without following a symlink.

    A refused symlink must be named by the path the repository contains, never
    by its target: resolution would echo the target inside the root or degrade
    to a bare name when it escapes.
    """
    root = Path(os.path.abspath(root))
    candidate = Path(os.path.abspath(path))
    try:
        return candidate.relative_to(root).as_posix()
    except ValueError:
        return candidate.name


def _lexical_record(root, path, status, rule, reason, line=0):
    """A record whose display path is lexical, for a refused symlink."""
    item = _record(root, path, status, rule, reason, line)
    item["path"] = _relative_lexical(root, path)
    return item


# D-18: the only consistent homework-status / report-status pairs.
ALLOWED_REPORT_STATUS = {
    "planned": ("placeholder",),
    "in-progress": ("draft", "complete"),
    "complete": ("complete",),
    "verified": ("complete",),
}


def _read_metadata(root, homework):
    """Return `(metadata, records)`; records is non-empty when reading failed."""
    try:
        text = homework.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        return None, [
            _record(root, homework, "ERROR", "RPT-001", f"homework.yaml is not valid UTF-8: {exc}")
        ]
    except OSError as exc:
        raise CheckError(f"cannot read {homework}: {exc}") from exc

    try:
        metadata = yaml.load(text, Loader=StrictSafeLoader)
    except yaml.YAMLError as exc:
        return None, [
            _record(root, homework, "ERROR", "RPT-001", f"homework.yaml is not valid YAML: {exc}")
        ]
    if not isinstance(metadata, dict):
        return None, [_record(root, homework, "ERROR", "RPT-001", "homework.yaml is not a mapping")]
    return metadata, []


def _status_records(root, homework, status, report_status):
    """`RPT-003`: the homework status and the report status agree (D-18)."""
    allowed = ALLOWED_REPORT_STATUS.get(status)
    if allowed is None:
        return [
            _record(
                root,
                homework,
                "ERROR",
                "RPT-003",
                f"unknown homework status {status!r}",
            )
        ]
    if report_status in allowed:
        return []
    expected = " or ".join(allowed)
    return [
        _record(
            root,
            homework,
            "ERROR",
            "RPT-003",
            f"homework status {status!r} requires report.status {expected}, "
            f"not {report_status!r}",
        )
    ]


def _validate_directory(root, directory):
    """Validate one `homeworks/<id>/` directory."""
    directory = Path(directory)
    homework = directory / "homework.yaml"
    if not homework.is_file():
        return [
            _record(
                root,
                directory,
                "ERROR",
                "RPT-001",
                "homework.yaml is missing; no report declared",
            )
        ]

    metadata, records = _read_metadata(root, homework)
    if records:
        return records

    report = metadata.get("report")
    if not isinstance(report, dict):
        # D-31/Pitfall 18: the schema does not require `report`, so a `planned`
        # homework is legitimately valid without one and is skipped.
        if metadata.get("status") == "planned":
            return [_record(root, homework, "OK", "", "no report declared")]
        return [
            _record(
                root,
                homework,
                "ERROR",
                "RPT-001",
                "homework.yaml declares no report block",
            )
        ]

    report_path_value = report.get("path")
    report_status = report.get("status")
    if not isinstance(report_path_value, str) or not report_path_value.strip():
        return [_record(root, homework, "ERROR", "RPT-001", "report.path is absent")]
    if not isinstance(report_status, str) or not report_status.strip():
        return [_record(root, homework, "ERROR", "RPT-001", "report.status is absent")]

    records = _status_records(root, homework, metadata.get("status"), report_status)

    report_path = directory / report_path_value
    if report_path.is_symlink():
        records.append(
            _lexical_record(
                root,
                report_path,
                "ERROR",
                "RPT-002",
                "report document is a symlink; refusing to follow it",
            )
        )
        return records
    if not report_path.is_file():
        records.append(
            _record(root, report_path, "ERROR", "RPT-002", "report document is absent")
        )
        return records

    text = read_regular_text(report_path, relative_path(root, report_path))
    records.extend(
        validate_report(
            text,
            metadata,
            homework_dir=directory,
            repo_root=root,
            path=report_path,
        )
    )
    return records


def _directories(root, positionals=None):
    """Return the sorted homework directories this run should read.

    A positional may name the directory or any document inside it; a file is
    reduced to its parent. A positional that does not resolve to a directory is
    a usage error (exit 2). With no positionals every direct child directory of
    `homeworks/` is scanned.
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


def _dedupe(records):
    """Drop byte-identical records while preserving order."""
    unique = []
    seen = set()
    for item in records:
        key = (item["path"], item["status"], item["rule"], item["line"], item["reason"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique


def main(argv=None):
    parser = argparse.ArgumentParser(description="Verify the report and evidence contract.")
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
        help="homework directory or report document to check (default: every homework)",
    )
    args = parser.parse_args(argv)

    try:
        root = resolve_root(args.dir)
        records = []
        for directory in _directories(root, args.paths or None):
            records.extend(_validate_directory(root, directory))
    except CheckError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    records = _dedupe(records)
    records.sort(key=lambda item: (item["path"], item["line"], item["rule"]))
    violations = sum(1 for item in records if item["status"] == "ERROR")

    if args.json:
        print(json.dumps(records, indent=2))
        return 1 if violations else 0

    for item in records:
        suffix = f" [{item['rule']}]" if item["rule"] else ""
        print(f"{item['path']}:{item['line']}: {item['status']}{suffix} — {item['reason']}")

    print()
    if violations:
        print(f"FAIL: {violations} report violation(s)")
        return 1
    print("PASS: report contract satisfied")
    return 0


if __name__ == "__main__":
    sys.exit(main())

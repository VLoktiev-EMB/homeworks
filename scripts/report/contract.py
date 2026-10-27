#!/usr/bin/env python3
"""The report contract rules, free of file I/O and third-party imports (D-02).

`scripts/check_report.py` owns the filesystem and the YAML read; this module
owns the rules. Each record is `{"path", "status", "rule", "line", "reason"}`
where `status` is `OK` or `ERROR` and `rule` is a stable `RPT-…` identifier
(D-04). A missing heading reports line 0, because the document has no line for
an absent heading to name.

This module may import `scripts.metadata.errors` and `scripts.metadata.paths`
only. It must never import `scripts.metadata.contract`, which drags PyYAML and
jsonschema into the test import graph, and never PyYAML itself (Pitfall 9).
"""

from __future__ import annotations

from pathlib import Path

from scripts.metadata.paths import relative_path
from scripts.report import markdown
from scripts.report.vocabulary import REPORT_HEADINGS


def _declared_path(metadata, homework_dir):
    """Return the declared report path, defaulting to `report.md`."""
    report = metadata.get("report") if isinstance(metadata, dict) else None
    value = report.get("path") if isinstance(report, dict) else None
    if not isinstance(value, str) or not value.strip():
        value = "report.md"
    base = Path(homework_dir) if homework_dir is not None else Path(".")
    return base / value


def _display(path, repo_root):
    """Render the record path without ever echoing an absolute root."""
    if repo_root is not None:
        return relative_path(repo_root, path)
    return Path(path).as_posix()


def validate_report(text, metadata, *, homework_dir=None, repo_root=None, path=None):
    """Validate one report document and return its records.

    The caller owns discovery, the size gate and the lifecycle checks; this
    function owns the document structure. An empty document is an `ERROR`
    (`RPT-002`) and never a pass.
    """
    report_path = Path(path) if path is not None else _declared_path(metadata, homework_dir)
    display = _display(report_path, repo_root)

    def record(status_value, rule, reason, line=0):
        return {
            "path": display,
            "status": status_value,
            "rule": rule,
            "line": line,
            "reason": reason,
        }

    if not text.strip():
        return [record("ERROR", "RPT-002", "report document is empty")]

    lines = text.splitlines()
    found = markdown.headings(lines)

    records = []
    seen = set()
    previous = -1
    for heading in found:
        if heading.level != 2 or heading.text not in REPORT_HEADINGS:
            continue
        if heading.text in seen:
            records.append(
                record(
                    "ERROR",
                    "RPT-103",
                    f'duplicate heading "{heading.text}"',
                    heading.line,
                )
            )
            continue
        seen.add(heading.text)
        index = REPORT_HEADINGS.index(heading.text)
        if index < previous:
            records.append(
                record(
                    "ERROR",
                    "RPT-102",
                    f'heading "{heading.text}" is out of ascending order',
                    heading.line,
                )
            )
        previous = index

    for missing in REPORT_HEADINGS:
        if missing not in seen:
            records.append(record("ERROR", "RPT-101", f'missing heading "{missing}"'))

    if records:
        return records
    return [record("OK", "", "report contract satisfied")]

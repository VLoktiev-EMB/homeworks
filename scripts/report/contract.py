#!/usr/bin/env python3
"""The report contract rules, free of file I/O and third-party imports (D-02).

`scripts/check_report.py` owns the filesystem and the YAML read; this module
owns the structural rules. Each record is `{"path", "status", "rule", "line", "reason"}`
where `status` is `OK` or `ERROR` and `rule` is a stable `RPT-…` identifier (D-04).
A missing heading reports line 0.

This module is lightweight, robust, and fast: it validates the existence of the
10 standard engineering sections in ascending order, proper status handling,
absence of unresolved TODO/TBD sentinels, document size, and language, without
imposing rigid AST parsing on markdown tables.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from scripts.metadata.paths import relative_path
from scripts.report import markdown
from scripts.report.vocabulary import (
    REPORT_HEADINGS,
    REPORT_MAX_BYTES,
)

SENTINEL = re.compile(r"\b(?:TODO|TBD)\b")


def is_cyrillic(character: str) -> bool:
    """Return True if character falls in standard Cyrillic Unicode blocks."""
    code = ord(character)
    return (
        (0x0400 <= code <= 0x04FF)
        or (0x0500 <= code <= 0x052F)
        or (0x2DE0 <= code <= 0x2DFF)
        or (0xA640 <= code <= 0xA69F)
    )


@dataclass(frozen=True)
class Diagram:
    """The diagram part ids, or the reason they could not be read."""

    parts: tuple[str, ...] | None = None
    error: str | None = None


def parse_diagram(text: str) -> Diagram:
    """Turn the diagram payload into its part ids; never raises."""
    try:
        payload = json.loads(text)
    except (ValueError, RecursionError) as exc:
        return Diagram(error=f"assets/diagram.json is not valid JSON: {exc}")
    if not isinstance(payload, dict) or not isinstance(payload.get("parts"), list):
        return Diagram(error="assets/diagram.json is not an object with a `parts` list")
    parts = tuple(
        part["id"]
        for part in payload["parts"]
        if isinstance(part, dict) and isinstance(part.get("id"), str)
    )
    return Diagram(parts=parts)


def _declared_path(metadata, homework_dir):
    """Fallback resolution of report path from metadata."""
    if isinstance(metadata, dict):
        report = metadata.get("report")
        if isinstance(report, dict):
            declared = report.get("path")
            if isinstance(declared, str):
                return Path(homework_dir or ".") / declared
    return Path(homework_dir or ".") / "report.md"


def _display(path: Path, repo_root: Path | None) -> str:
    """Render a display path relative to repo_root if given."""
    if repo_root is not None:
        try:
            return relative_path(repo_root, path)
        except Exception:
            pass
    return str(path)


def validate_report(
    text: str,
    metadata: dict | None,
    *,
    homework_dir=None,
    repo_root=None,
    path=None,
    diagram=None,
):
    """Validate report structure and return list of records."""
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

    # 1. Empty check (RPT-002)
    if not text.strip():
        return [record("ERROR", "RPT-002", "report document is empty")]

    # 2. Maximum byte size check (RPT-004)
    size = len(text.encode("utf-8"))
    if size > REPORT_MAX_BYTES:
        return [
            record(
                "ERROR",
                "RPT-004",
                f"report document is {size} bytes, larger than the {REPORT_MAX_BYTES}-byte bound",
            )
        ]

    # 3. Status waiver for placeholder reports
    report = metadata.get("report") if isinstance(metadata, dict) else None
    report_status = report.get("status") if isinstance(report, dict) else None
    if report_status == "placeholder":
        return [
            record(
                "OK",
                "",
                "report content checks are waived by report.status: placeholder",
            )
        ]

    lines = text.splitlines()
    found = markdown.headings(lines)

    records = []

    # 4. Heading structure: 10 required headings in ascending order, no duplicates
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

    # If top-level headings are missing or broken, return early
    if records:
        return records

    # 5. Language check: no Cyrillic characters in authored English report
    for number, line in enumerate(lines, start=1):
        offending = next((character for character in line if is_cyrillic(character)), None)
        if offending is not None:
            records.append(
                record(
                    "ERROR",
                    "RPT-405",
                    f"Cyrillic character {offending!r} is not allowed in report.md",
                    number,
                )
            )

    # 6. Sentinels check: no unresolved TODO / TBD in complete/draft reports
    for number, line in enumerate(lines, start=1):
        match = SENTINEL.search(line)
        if match is not None:
            records.append(
                record(
                    "ERROR",
                    "RPT-406",
                    f'sentinel "{match.group(0)}" is not allowed in a draft or complete report',
                    number,
                )
            )

    if records:
        return records

    return [record("OK", "", "report contract satisfied")]

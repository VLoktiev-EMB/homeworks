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
from scripts.report.vocabulary import (
    INDUSTRY_NOTE_PREFIX,
    NOT_APPLICABLE,
    NOT_APPLICABLE_SECTIONS,
    NOT_APPLICABLE_SUFFIX,
    REPORT_HEADINGS,
    REQUIRED_SUBSECTIONS,
    STATUS_PREFIX,
)


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


def _section_lookup(sections):
    """Map a section heading text to its section (the first occurrence)."""
    lookup = {}
    for section in sections:
        lookup.setdefault(section.heading.text, section)
    return lookup


def _parent_section(sections, line):
    """Return the level-2 section whose body contains *line*, if any."""
    for section in sections:
        if section.heading.line < line <= section.body_end:
            return section
    return None


def _carries_marker(lines, section):
    """True when a not-applicable marker appears in the section body."""
    for number in range(section.body_start, section.body_end + 1):
        if lines[number - 1].strip().startswith("_Not applicable"):
            return True
    return False


def _valid_marker(stripped):
    """True for the exact `_Not applicable — <reason>._` form (D-06/D-34)."""
    if not stripped.startswith(NOT_APPLICABLE):
        return False
    if not stripped.endswith(NOT_APPLICABLE_SUFFIX):
        return False
    reason = stripped[len(NOT_APPLICABLE) : -len(NOT_APPLICABLE_SUFFIX)]
    return bool(reason.strip())


def _subsection_records(lines, sections, record):
    """`RPT-104`: every required subsection exists within its parent section.

    Presence only: an unknown subsection between two required ones is legal
    (Pitfall 6), because the worked example carries one in section 7. A section
    that is entirely not applicable waives nothing except section 5's four
    subsections, which D-34 and the documented reading of Open Question 1 allow.
    """
    records = []
    lookup = _section_lookup(sections)
    for section_heading, required in REQUIRED_SUBSECTIONS.items():
        section = lookup.get(section_heading)
        if section is None:
            continue  # RPT-101 already reports a missing section
        if section_heading == "5. Hardware and Wiring" and _carries_marker(lines, section):
            continue
        present = {child.text for child in section.children if child.level == 3}
        for missing in required:
            if missing in present:
                continue
            records.append(
                record(
                    "ERROR",
                    "RPT-104",
                    f'section "{section_heading}" is missing required subsection "{missing}"',
                )
            )
    return records


def _not_applicable_records(lines, sections, record):
    """`RPT-105`/`RPT-106`: the marker carries a reason and sits where allowed."""
    records = []
    for number, text in enumerate(lines, start=1):
        stripped = text.strip()
        if not stripped.startswith("_Not applicable"):
            continue
        if not _valid_marker(stripped):
            records.append(
                record(
                    "ERROR",
                    "RPT-105",
                    "the not-applicable marker must read "
                    "'_Not applicable — <reason>._' with a non-empty reason",
                    number,
                )
            )
            continue
        parent = _parent_section(sections, number)
        name = parent.heading.text if parent is not None else None
        if name not in NOT_APPLICABLE_SECTIONS:
            where = f'section "{name}"' if name else "outside a numbered section"
            records.append(
                record(
                    "ERROR",
                    "RPT-106",
                    f"the not-applicable marker is not allowed in {where}",
                    number,
                )
            )
    return records


def _required_paragraph_records(lines, sections, record):
    """`RPT-107`/`RPT-108`: the named paragraph opening exists in its section."""
    records = []
    lookup = _section_lookup(sections)
    checks = (
        ("8. Analysis", INDUSTRY_NOTE_PREFIX, "RPT-107"),
        ("9. Conclusions", STATUS_PREFIX, "RPT-108"),
    )
    for section_heading, prefix, rule in checks:
        section = lookup.get(section_heading)
        if section is None:
            continue  # RPT-101 already reports a missing section
        if markdown.paragraph_begins_with(
            lines, section.body_start, section.body_end, prefix
        ):
            continue
        records.append(
            record(
                "ERROR",
                rule,
                f'section "{section_heading}" must contain a paragraph beginning "{prefix}"',
            )
        )
    return records


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

    sections = markdown.sections(lines, found)
    records.extend(_subsection_records(lines, sections, record))
    records.extend(_not_applicable_records(lines, sections, record))
    records.extend(_required_paragraph_records(lines, sections, record))

    if records:
        return records
    return [record("OK", "", "report contract satisfied")]

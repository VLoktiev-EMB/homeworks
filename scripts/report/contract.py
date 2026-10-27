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
from scripts.report import markdown, tables
from scripts.report.vocabulary import (
    ASSUMPTIONS_HEADER,
    BOM_HEADER,
    CALCULATIONS_HEADER,
    INDUSTRY_NOTE_PREFIX,
    LEDGER_HEADER,
    NOT_APPLICABLE,
    NOT_APPLICABLE_SECTIONS,
    NOT_APPLICABLE_SUFFIX,
    PIN_MAP_HEADER,
    REPORT_HEADINGS,
    REPORT_MAX_BYTES,
    REQUIRED_SUBSECTIONS,
    SECTION_ONE_HEADER,
    STATUS_PREFIX,
    TRACEABILITY_HEADER,
)

# D-06/D-34: a required table names its owning section, and optionally the
# `###` subsection that owns it. The header literals stay in `vocabulary.py`;
# this tuple only wires them to their position.
REQUIRED_TABLES = (
    ("section 1 metadata", "1. Title and Metadata", None, SECTION_ONE_HEADER),
    ("assumptions", "3. Assumptions", None, ASSUMPTIONS_HEADER),
    ("bill of materials", "5. Hardware and Wiring", "Bill of Materials", BOM_HEADER),
    ("pin map", "5. Hardware and Wiring", "Pin Map", PIN_MAP_HEADER),
    (
        "electrical calculations",
        "5. Hardware and Wiring",
        "Electrical Calculations",
        CALCULATIONS_HEADER,
    ),
    ("measurement ledger", "7. Results", "Measurement Ledger", LEDGER_HEADER),
    ("traceability matrix", "7. Results", "Traceability Matrix", TRACEABILITY_HEADER),
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


def _valid_marker(stripped):
    """True for the exact `_Not applicable — <reason>._` form (D-06/D-34)."""
    if not stripped.startswith(NOT_APPLICABLE):
        return False
    if not stripped.endswith(NOT_APPLICABLE_SUFFIX):
        return False
    reason = stripped[len(NOT_APPLICABLE) : -len(NOT_APPLICABLE_SUFFIX)]
    return bool(reason.strip())


def _marker_in_range(lines, start, end):
    """True when a *valid* not-applicable marker sits in the inclusive range."""
    return any(_valid_marker(lines[number - 1].strip()) for number in range(start, end + 1))


def _section_waived(lines, section):
    """True when the section itself carries the marker, before any child heading.

    A marker inside one subsection waives that subsection only, never its
    siblings (D-34). `_marker_in_range` requires a valid marker, so a malformed
    one is reported by `RPT-105` and waives nothing.
    """
    first_child = min((child.line for child in section.children), default=section.body_end + 1)
    return _marker_in_range(lines, section.body_start, first_child - 1)


def _subsection_range(section, name):
    """Return the inclusive body range of `### name`, or `None` when absent."""
    for child in section.children:
        if child.level == 3 and child.text == name:
            later = [heading.line for heading in section.children if heading.line > child.line]
            end = min(later) - 1 if later else section.body_end
            return child.line + 1, end
    return None


def _owned_range(lines, section, subsection):
    """Return `(start, end, waived)` for a required table's owning range."""
    if subsection is None:
        start, end = section.body_start, section.body_end
    else:
        body = _subsection_range(section, subsection)
        if body is None:
            return None
        start, end = body
    waived = _section_waived(lines, section)
    if not waived and subsection is not None:
        waived = section.heading.text in NOT_APPLICABLE_SECTIONS and _marker_in_range(
            lines, start, end
        )
    return start, end, waived


def _table_records(lines, sections, extracted, record):
    """`RPT-201`: every required table carries its exact header literal.

    The table family runs after the heading-presence family but alongside the
    subsection family: the live 1.3 report is missing `### Next Steps` yet its
    tables are still reportable, and `docs/standards/report.md` maps each rule
    id to one checklist item, so a defect must not hide another.
    """
    records = []
    lookup = _section_lookup(sections)
    for label, section_heading, subsection, expected in REQUIRED_TABLES:
        section = lookup.get(section_heading)
        if section is None:
            continue  # RPT-101 reports a missing section
        owned_range = _owned_range(lines, section, subsection)
        if owned_range is None:
            continue  # RPT-104 reports a missing subsection
        start, end, waived = owned_range
        table = next(
            (candidate for candidate in extracted if start <= candidate.header_line <= end),
            None,
        )
        if table is None:
            if not waived:
                records.append(
                    record(
                        "ERROR",
                        "RPT-201",
                        f'table "{label}" is absent; expected header "{" | ".join(expected)}"',
                    )
                )
            continue
        if table.header != expected:
            records.append(
                record(
                    "ERROR",
                    "RPT-201",
                    f'table "{label}" has header "{" | ".join(table.header)}"; '
                    f'expected "{" | ".join(expected)}"',
                    table.header_line,
                )
            )
            continue

    return records


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
        if section_heading == "5. Hardware and Wiring" and _section_waived(lines, section):
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

    size = len(text.encode("utf-8"))
    if size > REPORT_MAX_BYTES:
        return [
            record(
                "ERROR",
                "RPT-004",
                f"report document is {size} bytes, larger than the "
                f"{REPORT_MAX_BYTES}-byte bound",
            )
        ]

    report = metadata.get("report") if isinstance(metadata, dict) else None
    report_status = report.get("status") if isinstance(report, dict) else None
    if report_status == "placeholder":
        # D-17: a placeholder report only has to exist and be non-empty; its
        # headings and tables are not validated until authoring starts.
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
    rows = tables.extract_tables(text)
    records.extend(_subsection_records(lines, sections, record))
    records.extend(_not_applicable_records(lines, sections, record))
    records.extend(_required_paragraph_records(lines, sections, record))
    records.extend(_table_records(lines, sections, rows, record))

    if records:
        return records
    return [record("OK", "", "report contract satisfied")]

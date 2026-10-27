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

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path

from scripts.metadata.paths import relative_path
from scripts.report import markdown, tables
from scripts.report.vocabulary import (
    ASSUMPTIONS_HEADER,
    BOM_HEADER,
    CALCULATIONS_HEADER,
    EVIDENCE_LABEL_ORDER,
    EVIDENCE_LABELS,
    INDUSTRY_NOTE_PREFIX,
    LEDGER_HEADER,
    NOT_APPLICABLE,
    NOT_APPLICABLE_SECTIONS,
    NOT_APPLICABLE_SUFFIX,
    PIN_MAP_HEADER,
    REPORT_HEADINGS,
    REPORT_MAX_BYTES,
    REPORT_REQUIREMENTS,
    REQUIRED_SUBSECTIONS,
    SECTION_ONE_HEADER,
    STATUS_PREFIX,
    TRACEABILITY_HEADER,
    TRACEABILITY_STATUSES,
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

# D-15: the columns that may not be empty, by table label.
REQUIRED_CELLS = {
    "assumptions": ("Impact if wrong", "Validation"),
    "electrical calculations": (
        "Input provenance",
        "Result",
        "Uncertainty",
        "Assumption effect",
    ),
}

# D-15: a safety list item must open with a bold hazard name.
SAFETY_BULLET = re.compile(r"^[-*+]\s")

# D-11: the implementation commit is a 7-40 character lowercase hex string,
# compared as text and never executed or fetched (T-10-09).
IMPLEMENTATION_COMMIT = "Implementation commit"
HEX_COMMIT = re.compile(r"^[0-9a-f]{7,40}$")

# D-13/D-39: a path-like token carries a slash or a known code, document or
# data extension. The tuple is deliberately explicit so a command such as
# `pio run -d homeworks/<id>` splits on whitespace and only the path-like
# token is resolved (Pitfall 11).
PATH_EXTENSIONS = (
    ".md",
    ".py",
    ".c",
    ".h",
    ".cpp",
    ".hpp",
    ".json",
    ".yaml",
    ".yml",
    ".txt",
    ".ini",
    ".toml",
    ".csv",
    ".png",
    ".svg",
    ".pdf",
    ".log",
)

# The ledger columns this module reads, resolved once from the literal header.
_LEDGER_ID = LEDGER_HEADER.index("ID")
_LEDGER_VALUE = LEDGER_HEADER.index("Value")
_LEDGER_LABEL = LEDGER_HEADER.index("Label")
_LEDGER_INSTRUMENT = LEDGER_HEADER.index("Instrument")
_LEDGER_METHOD = LEDGER_HEADER.index("Method")
_LEDGER_COMMIT = LEDGER_HEADER.index("Implementation commit")

# The traceability columns the artifact and status rules read.
_TRACEABILITY_ID = TRACEABILITY_HEADER.index("ID")
_TRACEABILITY_ARTIFACT = TRACEABILITY_HEADER.index("Design artifact")
_TRACEABILITY_EVIDENCE = TRACEABILITY_HEADER.index("Evidence")
_TRACEABILITY_STATUS = TRACEABILITY_HEADER.index("Status")

# D-36: the four id-bearing tables and the prefix each row id must carry.
ID_TABLES = (
    ("assumptions", "A"),
    ("electrical calculations", "C"),
    ("measurement ledger", "L"),
    ("traceability matrix", "T"),
)

# D-36: an intra-report id token. The leading word boundary keeps `REPORT-01`
# from matching its trailing `T-01`.
IDENTIFIER = re.compile(r"\b([ACLT])-(\d{2})\b")

# D-13: artifact tokens are only those inside a backticked span.
BACKTICK_SPAN = re.compile(r"`([^`]+)`")


def path_like(token):
    """True when *token* looks like a path rather than prose (D-13)."""
    return "/" in token or token.lower().endswith(PATH_EXTENSIONS)


def _cell(row, index):
    """Return a row's normalized cell, or `""` when the row is short (RPT-202)."""
    return row.normalized[index] if index < len(row.normalized) else ""


def _lexically_contained(candidate, root):
    """True when *candidate* sits inside *root* after `.`/`..` normalization.

    `os.path.abspath` normalizes the path without following a symlink, which is
    the lexical half of the D-13 posture (Pitfall 10).
    """
    try:
        Path(os.path.abspath(candidate)).relative_to(Path(os.path.abspath(root)))
        return True
    except ValueError:
        return False


def resolve_artifact(token, homework_dir, repo_root):
    """Return True when *token* resolves to an existing path under either root.

    An absolute token is rejected before any filesystem call. A relative token
    is tried from the homework directory and from the repository root; the
    candidate must be lexically contained in one of the two roots and, as
    defence in depth, its resolved position must stay inside that root. Only
    existence is checked; no file is opened (D-13, T-10-07, T-10-08).
    """
    if not isinstance(token, str) or not token.strip():
        return False
    if Path(token).is_absolute():
        return False
    roots = [
        Path(os.path.abspath(root))
        for root in (homework_dir, repo_root)
        if root is not None
    ]
    if not roots:
        return False
    for base in roots:
        candidate = Path(os.path.abspath(base / token))
        inside = next((root for root in roots if _lexically_contained(candidate, root)), None)
        if inside is None or not candidate.exists():
            continue
        resolved = Path(os.path.realpath(candidate))
        if not _lexically_contained(resolved, Path(os.path.realpath(inside))):
            continue
        return True
    return False


def artifact_tokens(cell):
    """Yield every path-like token inside a backticked span (D-13).

    A span is split on whitespace so a command such as
    `pio run -d homeworks/<id>` is not treated as one path (Pitfall 11).
    """
    for span in BACKTICK_SPAN.findall(cell):
        for token in span.split():
            if path_like(token):
                yield token


@dataclass(frozen=True)
class Diagram:
    """The diagram part ids, or the reason they could not be read.

    `parse_diagram` never raises (T-10-27): a pull request can replace the
    diagram with malformed or hostile JSON, and the contract reports that as a
    content error instead of a traceback.
    """

    parts: tuple[str, ...] | None = None
    error: str | None = None


def parse_diagram(text):
    """Turn the diagram payload into its part ids; never raises (T-10-27)."""
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
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


def _table_records(lines, sections, extracted, diagram, record):
    """`RPT-201` ... `RPT-207`: header, row shape, cells, safety and BOM.

    The table family runs after the heading-presence family but alongside the
    subsection family: the live 1.3 report is missing `### Next Steps` yet its
    tables are still reportable, and `docs/standards/report.md` maps each rule
    id to one checklist item, so a defect must not hide another.
    """
    records = []
    lookup = _section_lookup(sections)
    owned = []
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
        if not table.rows and not waived:
            records.append(
                record(
                    "ERROR",
                    "RPT-204",
                    f'table "{label}" has no data rows and no not-applicable marker',
                    table.header_line,
                )
            )
        owned.append((label, table, waived))

    # RPT-202: every row of every table keeps its header's column count.
    for table in extracted:
        for row in table.rows:
            if len(row.cells) == len(table.header):
                continue
            records.append(
                record(
                    "ERROR",
                    "RPT-202",
                    f"table row has {len(row.cells)} cells but its header has "
                    f"{len(table.header)}",
                    row.line,
                )
            )

    # RPT-203: the D-15 required cells are non-empty.
    for label, table, _ in owned:
        required = REQUIRED_CELLS.get(label)
        if required is None:
            continue
        for row in table.rows:
            for column in required:
                index = table.header.index(column)
                if index >= len(row.normalized) or row.normalized[index]:
                    continue
                records.append(
                    record(
                        "ERROR",
                        "RPT-203",
                        f'table "{label}" row has an empty "{column}" cell',
                        row.line,
                    )
                )

    records.extend(_safety_records(lines, lookup, record))
    records.extend(_bom_records(lines, lookup, owned, diagram, record))
    return records, owned


def _safety_records(lines, lookup, record):
    """`RPT-205`: at least one hazard bullet, each opening `- **` (D-15)."""
    section = lookup.get("5. Hardware and Wiring")
    if section is None or _section_waived(lines, section):
        return []
    body = _subsection_range(section, "Safety Checklist")
    if body is None:
        return []  # RPT-104 reports the missing subsection
    if _marker_in_range(lines, *body):
        return []
    start, end = body
    bullets = [
        (number, lines[number - 1].strip())
        for number in range(start, end + 1)
        if SAFETY_BULLET.match(lines[number - 1].strip())
    ]
    if not bullets:
        return [
            record(
                "ERROR",
                "RPT-205",
                'the "Safety Checklist" must contain at least one hazard bullet',
                start,
            )
        ]
    return [
        record(
            "ERROR",
            "RPT-205",
            'safety bullet must begin "- **" and name a hazard',
            number,
        )
        for number, stripped in bullets
        if not stripped.startswith("- **")
    ]


def _bom_records(lines, lookup, owned, diagram, record):
    """`RPT-206`/`RPT-207`: BOM refs resolve to diagram part ids (D-12)."""
    section = lookup.get("5. Hardware and Wiring")
    if section is None or _section_waived(lines, section):
        return []
    bom = next((table for label, table, _ in owned if label == "bill of materials"), None)
    waived = next(
        (waived for label, _, waived in owned if label == "bill of materials"),
        None,
    )
    if waived is None:
        # The BOM subsection was absent or mis-headered and `owned` therefore
        # does not carry it. A marker in that subsection is still a waiver.
        body = _subsection_range(section, "Bill of Materials")
        waived = body is not None and _marker_in_range(lines, *body)
    if waived:
        return []
    if diagram is None:
        return [
            record(
                "ERROR",
                "RPT-207",
                "the bill of materials applies but assets/diagram.json was not read",
            )
        ]
    if diagram.error is not None:
        return [record("ERROR", "RPT-207", f"the bill of materials applies but {diagram.error}")]
    if bom is None:
        return []  # RPT-201 already reports the absent or mis-headered table
    known = set(diagram.parts or ())
    return [
        record(
            "ERROR",
            "RPT-206",
            f'BOM Ref "{row.normalized[0]}" is not a part id in assets/diagram.json',
            row.line,
        )
        for row in bom.rows
        if row.normalized and row.normalized[0] not in known
    ]


def _ledger_records(owned, record):
    """`RPT-301`, `RPT-303`, `RPT-304`, `RPT-305`: the measurement ledger.

    Every vocabulary rule is scoped to the ledger `Label`/`Value` cells and the
    section-1 commit cell. The report's explanatory prose legitimately contains
    the words `observed` and `not measured`, so no rule scans the document for
    them (D-10, Pitfall 3).
    """
    ledger = next((table for label, table, _ in owned if label == "measurement ledger"), None)
    metadata_table = next(
        (table for label, table, _ in owned if label == "section 1 metadata"),
        None,
    )
    records = []

    section_commit = None
    if metadata_table is not None:
        for row in metadata_table.rows:
            if _cell(row, 0) == IMPLEMENTATION_COMMIT:
                section_commit = (_cell(row, 1), row.line)
                break
    if section_commit is not None and not HEX_COMMIT.match(section_commit[0]):
        records.append(
            record(
                "ERROR",
                "RPT-304",
                'section-1 "Implementation commit" must be a 7-40 character '
                "lowercase hex string",
                section_commit[1],
            )
        )

    if ledger is None:
        return records

    for row in ledger.rows:
        row_id = _cell(row, _LEDGER_ID)
        value = _cell(row, _LEDGER_VALUE)
        label = _cell(row, _LEDGER_LABEL)
        instrument = _cell(row, _LEDGER_INSTRUMENT)
        method = _cell(row, _LEDGER_METHOD)
        commit = _cell(row, _LEDGER_COMMIT)

        # RPT-301: the semantic label is a closed set, and `observed` alone is
        # not a member (D-10).
        if label not in EVIDENCE_LABELS:
            expected = ", ".join(EVIDENCE_LABEL_ORDER)
            records.append(
                record(
                    "ERROR",
                    "RPT-301",
                    f'ledger row "{row_id}" has label "{label}"; expected one of {expected}',
                    row.line,
                )
            )

        # RPT-303: the value prefix is a function of the label.
        if label == "not measured":
            reason = value[len("not measured:") :] if value.startswith("not measured:") else ""
            if not reason.strip():
                records.append(
                    record(
                        "ERROR",
                        "RPT-303",
                        f'ledger row "{row_id}" value must begin "not measured:" with a reason',
                        row.line,
                    )
                )
        elif label == "measured" and not (
            value.startswith("user-reported:") or value.startswith("serial-log:")
        ):
            records.append(
                record(
                    "ERROR",
                    "RPT-303",
                    f'ledger row "{row_id}" measured value must begin '
                    '"user-reported:" or "serial-log:"',
                    row.line,
                )
            )
        elif label == "measured (observed)" and not value.startswith("serial-log:"):
            records.append(
                record(
                    "ERROR",
                    "RPT-303",
                    f'ledger row "{row_id}" measured (observed) value must begin "serial-log:"',
                    row.line,
                )
            )

        # RPT-304: one code tree per report; the hex shape and equality are
        # textual comparisons, never a git lookup (D-11, Pitfall 17).
        if not HEX_COMMIT.match(commit):
            records.append(
                record(
                    "ERROR",
                    "RPT-304",
                    f'ledger row "{row_id}" "Implementation commit" must be a '
                    "7-40 character lowercase hex string",
                    row.line,
                )
            )
        elif section_commit is not None and commit != section_commit[0]:
            records.append(
                record(
                    "ERROR",
                    "RPT-304",
                    f'ledger row "{row_id}" "Implementation commit" {commit!r} does not '
                    f"match the section-1 commit {section_commit[0]!r}",
                    row.line,
                )
            )

        # RPT-305: the provenance depth the label promises (D-39).
        if label == "datasheet" and not (
            re.search(r"\[\d+\]", instrument) or re.search(r"\[\d+\]", method)
        ):
            records.append(
                record(
                    "ERROR",
                    "RPT-305",
                    f'ledger row "{row_id}" datasheet row must cite an [N] source in its '
                    "instrument or method",
                    row.line,
                )
            )
        elif label == "calculated" and not re.search(r"\bC-\d{2}\b", method):
            records.append(
                record(
                    "ERROR",
                    "RPT-305",
                    f'ledger row "{row_id}" calculated row must name a C-NN calculation',
                    row.line,
                )
            )
        elif label == "simulated" and not any(path_like(token) for token in method.split()):
            records.append(
                record(
                    "ERROR",
                    "RPT-305",
                    f'ledger row "{row_id}" simulated row must name a scenario or '
                    "run-artifact path",
                    row.line,
                )
            )
        elif label == "measured" and instrument.strip().lower() in ("", "none"):
            records.append(
                record(
                    "ERROR",
                    "RPT-305",
                    f'ledger row "{row_id}" measured row must name an instrument other '
                    'than "none"',
                    row.line,
                )
            )

    return records


def _traceability_records(owned, homework_dir, repo_root, record):
    """`RPT-306`, `RPT-307`, `RPT-308`, `RPT-310`: the traceability matrix.

    Artifact existence is checked for `verified`, `manual` and `not applicable`
    rows; a `pending` row is exempt because its evidence may not exist yet
    (D-13). A status outside the enum is `RPT-306`, and the artifact check is
    skipped for that row because its meaning is unknown.
    """
    records = []

    # RPT-308: each id matches its table's shape and is unique within it.
    for label, prefix in ID_TABLES:
        table = next((table for name, table, _ in owned if name == label), None)
        if table is None:
            continue
        seen = set()
        for row in table.rows:
            row_id = _cell(row, 0)
            if not re.fullmatch(rf"{prefix}-\d{{2}}", row_id):
                records.append(
                    record(
                        "ERROR",
                        "RPT-308",
                        f'table "{label}" row id "{row_id}" does not match {prefix}-NN',
                        row.line,
                    )
                )
                continue
            if row_id in seen:
                records.append(
                    record(
                        "ERROR",
                        "RPT-308",
                        f'table "{label}" row id "{row_id}" is duplicated',
                        row.line,
                    )
                )
                continue
            seen.add(row_id)

    matrix = next(
        (table for name, table, _ in owned if name == "traceability matrix"),
        None,
    )
    rows = matrix.rows if matrix is not None else ()

    # RPT-310: every report requirement is cited by at least one row (D-41).
    for requirement in REPORT_REQUIREMENTS:
        if any(requirement in cell for row in rows for cell in row.cells):
            continue
        records.append(
            record(
                "ERROR",
                "RPT-310",
                f"the traceability matrix does not cite {requirement}",
            )
        )

    can_resolve = homework_dir is not None or repo_root is not None
    for row in rows:
        row_id = _cell(row, _TRACEABILITY_ID)
        status = _cell(row, _TRACEABILITY_STATUS)
        if status not in TRACEABILITY_STATUSES:
            records.append(
                record(
                    "ERROR",
                    "RPT-306",
                    f'traceability row "{row_id}" has status "{status}"; expected '
                    "verified, manual, pending, or not applicable",
                    row.line,
                )
            )
            continue
        if status == "pending" or not can_resolve:
            continue
        for column, index in (
            ("Design artifact", _TRACEABILITY_ARTIFACT),
            ("Evidence", _TRACEABILITY_EVIDENCE),
        ):
            raw = row.cells[index] if index < len(row.cells) else ""
            for token in artifact_tokens(raw):
                if resolve_artifact(token, homework_dir, repo_root):
                    continue
                records.append(
                    record(
                        "ERROR",
                        "RPT-307",
                        f'traceability row "{row_id}" {column} token "{token}" does not '
                        "resolve under the homework directory or the repository root",
                        row.line,
                    )
                )

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


def validate_report(
    text,
    metadata,
    *,
    homework_dir=None,
    repo_root=None,
    path=None,
    diagram=None,
):
    """Validate one report document and return its records.

    The caller owns discovery, the size gate, the lifecycle checks and the
    diagram read; this function owns the document structure. `diagram` is a
    `Diagram` built by `parse_diagram`, or `None` when the caller did not read
    one. An empty document is an `ERROR` (`RPT-002`) and never a pass.
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
    table_records, owned = _table_records(lines, sections, rows, diagram, record)
    records.extend(table_records)
    records.extend(_ledger_records(owned, record))
    records.extend(_traceability_records(owned, homework_dir, repo_root, record))

    if records:
        return records
    return [record("OK", "", "report contract satisfied")]

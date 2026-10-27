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
    DECISION_APPENDIX_HEADING,
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

# D-11: the four section-1 identity cells, each mapped to the metadata path it
# must equal. `Board` and `Language` are deliberately absent: they are display
# text, and the worked example writes a prose board description against the
# metadata slug, so string-comparing them would reject a compliant report.
IDENTITY_FIELDS = (
    ("Homework ID", ("id",)),
    ("Title", ("title",)),
    ("Homework status", ("status",)),
    ("Report status", ("report", "status")),
)

# D-11: the three toolchain cells and the comparison each one needs.
TOOLCHAIN_FIELDS = (
    ("Framework", ("framework",), "casefold"),
    ("PlatformIO Core", ("toolchain", "platformio"), "cell"),
    ("Platform", ("toolchain", "platform"), "platform"),
)

# D-40: the Cyrillic blocks the English-only scan covers.
CYRILLIC_RANGES = (
    (0x0400, 0x04FF),
    (0x0500, 0x052F),
    (0x2DE0, 0x2DFF),
    (0xA640, 0xA69F),
)

# D-16: a sentinel token anywhere in a draft or complete report.
SENTINEL = re.compile(r"\b(?:TODO|TBD)\b")

# D-38: a Markdown inline link or image, and the scheme that marks a target as
# external. An external target is never fetched or resolved.
INLINE_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]*)\)")
EXTERNAL_SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")

# D-37: the paragraph lead-ins section 7 must carry when the metadata promises
# a native suite or a simulation run.
NATIVE_PREFIXES = ("**Native suite.**", "**Native tests.**")
SIMULATION_PREFIX = "**Simulation.**"
RUN_CLAIM_TOKENS = ("exited 0", "scenario passed")


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


def _metadata_value(metadata, path):
    """Return the metadata value at *path*, or `None` when any step is absent."""
    value = metadata
    for key in path:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def is_cyrillic(character):
    """True when *character* is a single Cyrillic codepoint (D-40)."""
    if not isinstance(character, str) or len(character) != 1:
        return False
    code = ord(character)
    return any(low <= code <= high for low, high in CYRILLIC_RANGES)


def _link_target(raw):
    """Return the relative target of one inline-link payload, or `None`.

    An optional angle-bracket wrapper, title, fragment and query are stripped.
    A scheme-bearing target (`https:`, `mailto:`, …) is external and is never
    resolved or fetched (D-38, T-10-11). A fragment-only target needs no file.
    """
    text = raw.strip()
    if not text:
        return None
    if text.startswith("<"):
        end = text.find(">")
        if end == -1:
            return None
        text = text[1:end].strip()
    else:
        text = text.split()[0]
    text = text.split("#", 1)[0].split("?", 1)[0].strip()
    if not text or text.startswith("#") or EXTERNAL_SCHEME.match(text):
        return None
    return text


def link_targets(lines):
    """Yield `(line, target)` for every relative Markdown link or image.

    Fenced code is skipped for the same reason the heading and table scanners
    skip it: a sample link inside a fence is not a document link.
    """
    in_fence = False
    for number, line in enumerate(lines, start=1):
        if markdown.FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for match in INLINE_LINK.finditer(line):
            target = _link_target(match.group(1))
            if target is not None:
                yield number, target


def _paragraphs(lines, start, end):
    """Yield `(first_line, joined_text)` for each paragraph in an inclusive range."""
    current = []
    first = None
    for number in range(start, end + 1):
        text = lines[number - 1]
        if not text.strip():
            if current:
                yield first, " ".join(current)
            current = []
            first = None
            continue
        if not current:
            first = number
        current.append(text.strip())
    if current:
        yield first, " ".join(current)


def _identity_line(table, key):
    """Return the line of the section-1 row whose `Field` is *key*."""
    try:
        field_index = table.header.index("Field")
    except ValueError:
        return table.header_line
    for row in table.rows:
        if field_index < len(row.normalized) and row.normalized[field_index] == key:
            return row.line
    return table.header_line


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


def _defined_ids(owned):
    """Return `{prefix: {id}}` for the four id-bearing tables."""
    defined = {}
    for label, prefix in ID_TABLES:
        table = next((table for name, table, _ in owned if name == label), None)
        if table is None:
            continue
        ids = defined.setdefault(prefix, set())
        for row in table.rows:
            row_id = _cell(row, 0)
            if re.fullmatch(rf"{prefix}-\d{{2}}", row_id):
                ids.add(row_id)
    return defined


def _cross_reference_records(lines, sections, owned, record):
    """`RPT-309`: every `A-NN`/`C-NN`/`L-NN`/`T-NN` token resolves (D-36).

    Tokens are collected from sections 1-9 and the decision appendix, never
    from the reference list. A duplicate id is `RPT-308`, not this rule.
    """
    defined = _defined_ids(owned)
    scoped = set(REPORT_HEADINGS[:9]) | {DECISION_APPENDIX_HEADING}
    records = []
    for section in sections:
        if section.heading.text not in scoped:
            continue
        for number in range(section.body_start, section.body_end + 1):
            for match in IDENTIFIER.finditer(lines[number - 1]):
                if match.group(0) in defined.get(match.group(1), set()):
                    continue
                records.append(
                    record(
                        "ERROR",
                        "RPT-309",
                        f'"{match.group(0)}" does not resolve to a row in the '
                        f"{match.group(1)} table",
                        number,
                    )
                )
    return records


def _citation_records(lines, sections, record):
    """`RPT-311`/`RPT-312`: bidirectional IEEE citations, section-scoped (D-36).

    Entries live only in `## 10. References`; citations live only in sections
    1-9 and the decision appendix. Neither side is a document-wide sweep, so the
    wrapped section-8 line that begins `[1] ` is a citation, not an entry.
    """
    entries = markdown.reference_entries(lines, sections, "10. References")
    entry_numbers = {number for number, _ in entries}
    scoped = list(REPORT_HEADINGS[:9]) + [DECISION_APPENDIX_HEADING]
    citations = markdown.citation_tokens(lines, sections, scoped)
    cited_numbers = {number for number, _ in citations}
    records = []
    for number, line in citations:
        if number in entry_numbers:
            continue
        records.append(
            record(
                "ERROR",
                "RPT-311",
                f'citation [{number}] has no entry in "10. References"',
                line,
            )
        )
    for number, line in entries:
        if number in cited_numbers:
            continue
        records.append(
            record(
                "ERROR",
                "RPT-312",
                f"reference entry [{number}] is never cited in sections 1-9 or the "
                "Decision Appendix",
                line,
            )
        )
    return records


def _identity_records(found, owned, metadata, record):
    """`RPT-401`...`RPT-403`: identity and toolchain match normalized metadata.

    The comparison is always against a machine value, never display prose. A
    cell is normalized first (`normalize_cell`), `Framework` is compared with
    `casefold()`, and `Platform` goes through `normalize_platform`, so both
    repository spellings compare equal (D-11, Pitfall 2).
    """
    records = []

    # RPT-401: exactly one H1, and it names the homework title.
    h1s = [heading for heading in found if heading.level == 1]
    title = _metadata_value(metadata, ("title",))
    if len(h1s) != 1:
        line = h1s[1].line if len(h1s) > 1 else 0
        records.append(
            record(
                "ERROR",
                "RPT-401",
                f"the report has {len(h1s)} level-1 headings; expected exactly one",
                line,
            )
        )
    elif isinstance(title, str) and tables.normalize_cell(h1s[0].text) != tables.normalize_cell(
        title
    ):
        records.append(
            record(
                "ERROR",
                "RPT-401",
                f"the level-1 heading {h1s[0].text!r} does not match "
                f'homework.yaml title {title!r}',
                h1s[0].line,
            )
        )

    table = next(
        (candidate for label, candidate, _ in owned if label == "section 1 metadata"),
        None,
    )
    if table is None:
        return records

    # RPT-402: the four identity cells equal their metadata values.
    for field_name, path in IDENTITY_FIELDS:
        expected = _metadata_value(metadata, path)
        if not isinstance(expected, str):
            continue
        observed = tables.lookup_row(table, field_name)
        if observed is None:
            records.append(
                record(
                    "ERROR",
                    "RPT-402",
                    f'section-1 "{field_name}" cell is absent; expected {expected!r}',
                    table.header_line,
                )
            )
            continue
        if tables.normalize_cell(observed) == tables.normalize_cell(expected):
            continue
        records.append(
            record(
                "ERROR",
                "RPT-402",
                f'section-1 "{field_name}" is {observed!r}; expected {expected!r}',
                _identity_line(table, field_name),
            )
        )

    # RPT-403: the three toolchain cells equal their metadata values under the
    # comparison each one needs. `Board` and `Language` are display text and are
    # deliberately not compared (D-11).
    for field_name, path, comparison in TOOLCHAIN_FIELDS:
        expected = _metadata_value(metadata, path)
        if not isinstance(expected, str):
            continue
        observed = tables.lookup_row(table, field_name)
        if observed is None:
            records.append(
                record(
                    "ERROR",
                    "RPT-403",
                    f'section-1 "{field_name}" cell is absent; expected {expected!r}',
                    table.header_line,
                )
            )
            continue
        if comparison == "casefold":
            matches = observed.casefold() == expected.casefold()
        elif comparison == "platform":
            matches = tables.normalize_platform(observed) == tables.normalize_platform(expected)
        else:
            matches = tables.normalize_cell(observed) == tables.normalize_cell(expected)
        if matches:
            continue
        records.append(
            record(
                "ERROR",
                "RPT-403",
                f'section-1 "{field_name}" is {observed!r}; expected {expected!r}',
                _identity_line(table, field_name),
            )
        )

    return records


def _link_records(lines, homework_dir, repo_root, record):
    """`RPT-404`: every relative link or image target resolves (D-38).

    External schemes are dropped by `link_targets` before any filesystem call,
    so a URL is never fetched (T-10-11). A relative target is resolved through
    `resolve_artifact`, which refuses an absolute or escaping path.
    """
    if homework_dir is None and repo_root is None:
        return []
    records = []
    for number, target in link_targets(lines):
        if resolve_artifact(target, homework_dir, repo_root):
            continue
        records.append(
            record(
                "ERROR",
                "RPT-404",
                f'link target "{target}" does not resolve under the homework '
                "directory or the repository root",
                number,
            )
        )
    return records


def _language_records(lines, record):
    """`RPT-405`: `report.md` is English-only (D-40)."""
    records = []
    for number, line in enumerate(lines, start=1):
        offending = next((character for character in line if is_cyrillic(character)), None)
        if offending is None:
            continue
        records.append(
            record(
                "ERROR",
                "RPT-405",
                f"Cyrillic character {offending!r} is not allowed in report.md",
                number,
            )
        )
    return records


def _sentinel_records(lines, record):
    """`RPT-406`: no `TODO`/`TBD` sentinel in a draft or complete report (D-16).

    A `placeholder` report never reaches this rule because `validate_report`
    returns its waiver first (D-17).
    """
    records = []
    for number, line in enumerate(lines, start=1):
        match = SENTINEL.search(line)
        if match is None:
            continue
        records.append(
            record(
                "ERROR",
                "RPT-406",
                f'sentinel "{match.group(0)}" is not allowed in a draft or complete report',
                number,
            )
        )
    return records


def _status_claim_records(lines, sections, metadata, record):
    """`RPT-407`/`RPT-408`: section-7 claims match homework.yaml (D-37).

    Only presence and the two run-claim tokens are machine-checked; whether the
    prose describes the run honestly stays a review duty (D-14, T-10-14).
    """
    section = next((item for item in sections if item.heading.text == "7. Results"), None)
    if section is None:
        return []
    paragraphs = list(_paragraphs(lines, section.body_start, section.body_end))
    records = []

    # RPT-407: a native-suite result paragraph when the metadata promises one.
    if _metadata_value(metadata, ("tests", "native")) is True and not any(
        text.startswith(NATIVE_PREFIXES) for _, text in paragraphs
    ):
        records.append(
            record(
                "ERROR",
                "RPT-407",
                'section 7 must contain a "**Native suite.**" or "**Native tests.**" '
                "paragraph because tests.native is true",
            )
        )

    # RPT-408: a simulation paragraph, and its claim agrees with the status.
    simulation = _metadata_value(metadata, ("simulation",))
    if not isinstance(simulation, dict):
        return records
    paragraph = next(
        ((number, text) for number, text in paragraphs if text.startswith(SIMULATION_PREFIX)),
        None,
    )
    if paragraph is None:
        records.append(
            record(
                "ERROR",
                "RPT-408",
                'section 7 must contain a paragraph beginning "**Simulation.**" '
                "because homework.yaml declares a simulation block",
            )
        )
        return records
    number, text = paragraph
    claims_run = any(token in text for token in RUN_CLAIM_TOKENS)
    status = simulation.get("status")
    if status == "verified" and not claims_run:
        records.append(
            record(
                "ERROR",
                "RPT-408",
                'the simulation paragraph must state an executed-run outcome '
                '("exited 0" or "scenario passed") because simulation.status is verified',
                number,
            )
        )
    elif status == "pending" and claims_run:
        records.append(
            record(
                "ERROR",
                "RPT-408",
                'the simulation paragraph claims an executed run ("exited 0" or '
                '"scenario passed") although simulation.status is pending',
                number,
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
    records.extend(_cross_reference_records(lines, sections, owned, record))
    records.extend(_citation_records(lines, sections, record))
    records.extend(_identity_records(found, owned, metadata, record))
    records.extend(_link_records(lines, homework_dir, repo_root, record))
    records.extend(_language_records(lines, record))
    records.extend(_sentinel_records(lines, record))
    records.extend(_status_claim_records(lines, sections, metadata, record))

    if records:
        return records
    return [record("OK", "", "report contract satisfied")]

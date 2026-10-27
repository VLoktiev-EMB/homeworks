#!/usr/bin/env python3
"""The one literal vocabulary the report contract and the template share.

Every string the report contract asserts lives here and nowhere else, so the
checker, `templates/report/report.md` and `docs/standards/report.md` cannot
drift into three spellings of one heading (D-08/D-23). The headings are locked
verbatim by D-07, the table headers by D-08, the evidence labels by D-10 and
the not-applicable marker by D-06/D-34.

This module imports nothing: `python3 -m unittest discover scripts/tests` runs
without a third-party package, so a stdlib-only test may import it directly.
"""

from __future__ import annotations

# D-07: the ten numbered section headings, in their required ascending order.
REPORT_HEADINGS = (
    "1. Title and Metadata",
    "2. Objective",
    "3. Assumptions",
    "4. Theory",
    "5. Hardware and Wiring",
    "6. Methodology",
    "7. Results",
    "8. Analysis",
    "9. Conclusions",
    "10. References",
)

# D-07: optional, and only after the ten numbered sections.
DECISION_APPENDIX_HEADING = "Decision Appendix"

# D-07: each required `###` subsection, resolved against its parent section.
REQUIRED_SUBSECTIONS = {
    "4. Theory": ("Limitations",),
    "5. Hardware and Wiring": (
        "Bill of Materials",
        "Pin Map",
        "Electrical Calculations",
        "Safety Checklist",
    ),
    "7. Results": ("Measurement Ledger", "Traceability Matrix"),
    "9. Conclusions": ("Next Steps",),
}

# D-11 row keys, pinned per Open Question 2: the section-1 table is `Field | Value`.
SECTION_ONE_HEADER = ("Field", "Value")

# D-08: the six evidence-table headers.
ASSUMPTIONS_HEADER = ("ID", "Assumption", "Impact if wrong", "Validation")
BOM_HEADER = ("Ref", "Part or value", "Quantity", "Package", "Source or link", "Notes")
PIN_MAP_HEADER = ("Signal", "Pin", "Connects to", "Notes")
CALCULATIONS_HEADER = (
    "ID",
    "Quantity",
    "Formula",
    "Units",
    "Input provenance",
    "Result",
    "Uncertainty",
    "Assumption effect",
)
LEDGER_HEADER = (
    "ID",
    "Quantity",
    "Value",
    "Label",
    "Instrument",
    "Method",
    "Uncertainty",
    "Implementation commit",
)
TRACEABILITY_HEADER = (
    "ID",
    "Claim or requirement",
    "Design artifact",
    "Verification method",
    "Evidence",
    "Status",
)

# D-06/D-34: the one marker that replaces an artifact that does not apply.
NOT_APPLICABLE = "_Not applicable — "
NOT_APPLICABLE_SUFFIX = "._"

# D-34: only sections 3 and 5 can genuinely be absent; the rest never are.
NOT_APPLICABLE_SECTIONS = frozenset({"3. Assumptions", "5. Hardware and Wiring"})

# D-07: the two required paragraph openings in sections 8 and 9.
INDUSTRY_NOTE_PREFIX = "Industry note:"
STATUS_PREFIX = "Status:"

# D-10: the five semantic labels plus the single qualified form.
EVIDENCE_LABELS = frozenset(
    {
        "measured",
        "calculated",
        "simulated",
        "datasheet",
        "not measured",
        "measured (observed)",
    }
)

# REPORT-01 ... REPORT-08: the report requirements the traceability matrix covers.
REPORT_REQUIREMENTS = tuple(f"REPORT-0{index}" for index in range(1, 9))

# D-02/D-19: the report bound is deliberately not the 64 KiB metadata cap. The
# live worked example is 42,344 bytes, so the metadata cap would leave the
# contract only ~1.5x headroom (Pitfall 14); a full report can legitimately grow.
REPORT_MAX_BYTES = 1024 * 1024

# D-04/D-43: one ordered registry `rule_id -> (summary, remediation)`. The ids
# are the stable contract the tests and `docs/standards/report.md` assert; the
# summaries are the short reason wording, the remediations the human fix.
RULES = {
    "RPT-001": (
        "the report declaration is missing or unreadable",
        "add a `report` block with `path` and `status` to `homework.yaml`",
    ),
    "RPT-002": (
        "the declared report document is absent, empty, or a symlink",
        "write a non-empty `report.md` at `report.path`; never commit a symlink",
    ),
    "RPT-003": (
        "the homework status and report status disagree",
        "align the pair: planned/placeholder, in-progress/draft or complete, "
        "complete or verified/complete",
    ),
    "RPT-004": (
        "the report document exceeds the size bound",
        "split unrelated material out of the report; keep it under one mebibyte",
    ),
    "RPT-101": (
        "a required numbered heading is missing",
        "add the heading exactly as the ten-section contract spells it",
    ),
    "RPT-102": (
        "the numbered headings are out of ascending order",
        "move the heading to its numbered position",
    ),
    "RPT-103": (
        "a numbered heading appears more than once",
        "keep one copy of the heading",
    ),
    "RPT-104": (
        "a required subsection is missing from its parent section",
        "add the subsection inside its parent section, or mark the section "
        "not applicable where the contract allows it",
    ),
    "RPT-105": (
        "the not-applicable marker is malformed or has no reason",
        "write `_Not applicable — <reason>._` with a non-empty reason",
    ),
    "RPT-106": (
        "the not-applicable marker is in a position where it is forbidden",
        "write the content for this section; only sections 3 and 5 may be "
        "not applicable",
    ),
    "RPT-107": (
        "section 8 has no paragraph beginning `Industry note:`",
        "add at least one `Industry note:` paragraph to the analysis",
    ),
    "RPT-108": (
        "section 9 has no paragraph beginning `Status:`",
        "state the honest status in a `Status:` paragraph in the conclusions",
    ),
    "RPT-201": (
        "a required table is absent or its header differs from the contract",
        "write the table inside its section with exactly the contracted header",
    ),
    "RPT-202": (
        "a table row has a different cell count from its header",
        "add or remove the missing cell; a literal pipe inside a cell must be "
        "escaped as `\\|`",
    ),
    "RPT-203": (
        "a required table cell is empty",
        "fill the cell with the evidence, the calculation, or an explicit "
        "not-applicable reason",
    ),
    "RPT-204": (
        "a required table has no data rows",
        "add at least one data row, or replace the table with "
        "`_Not applicable — <reason>._` where the contract allows it",
    ),
    "RPT-205": (
        "the safety checklist is empty or a bullet lacks the bold hazard prefix",
        "write at least one `- **Hazard.** <consequence and check>` bullet",
    ),
    "RPT-206": (
        "a bill-of-materials `Ref` is not a part id in `assets/diagram.json`",
        "use the diagram part id as the BOM reference, or add the part to the "
        "diagram",
    ),
    "RPT-207": (
        "the bill of materials applies but `assets/diagram.json` is absent or "
        "malformed",
        "restore a readable `assets/diagram.json` with a `parts` list, or mark "
        "the bill of materials not applicable",
    ),
}

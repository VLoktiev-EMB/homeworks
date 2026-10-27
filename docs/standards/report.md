# Report and evidence standard

This is the human entry point for the homework report contract. The deterministic checker in
`scripts/check_report.py` is the machine gate; this page states what the gate checks, why each
rule exists, and what to do before opening a pull request. Read it once when you start a
report and return to the rule reference when a failure names an `RPT-…` id.

The standard is English, like every repository artifact. The conversation with the author may
be in another language.

## Before you start

Three artifacts carry the report, and each has one job:

- `homework.yaml` `report` — the declaration: `path` names the document and `status` is
  `placeholder`, `draft`, or `complete`. It is the only place the lifecycle is recorded.
- `report.md` — the authored document at `report.path`. It carries the ten numbered sections,
  the evidence tables, and the prose.
- `assets/diagram.json` — the wiring source of truth. Its `parts` list supplies the part ids
  the bill of materials references.

Start from `templates/report/report.md`, then fill it against an existing completed report
(such as `homeworks/<id>/report.md`) as the reference. Run the checker from the
repository root at any point:

```bash
uv run scripts/check_report.py
```

With no positional argument the checker scans every direct child of `homeworks/`. To focus on
one homework, pass its directory or its document:

```bash
uv run scripts/check_report.py --dir . homeworks/<id>
```

Every record prints `path:line: STATUS [RULE] — reason`. An `ERROR` names a rule id; look the
id up in [Rule reference](#rule-reference) for the fix.

## The contract

A report is one uniform skeleton. Every heading and table below is present in every report;
a section that does not apply is marked, never omitted.

### Numbered headings

The ten level-2 headings are literal and ascending. No duplicates are allowed, and a heading
inside a fenced code block is not a section:

1. `1. Title and Metadata`
2. `2. Objective`
3. `3. Assumptions`
4. `4. Theory`
5. `5. Hardware and Wiring`
6. `6. Methodology`
7. `7. Results`
8. `8. Analysis`
9. `9. Conclusions`
10. `10. References`

An optional `## Decision Appendix` may follow the references. It is the only additional
level-2 heading the contract recognizes.

### Required subsections

Each `###` subsection belongs to its parent section:

| Parent section | Required subsections |
|----------------|----------------------|
| `4. Theory` | `Limitations` |
| `5. Hardware and Wiring` | `Bill of Materials`, `Pin Map`, `Electrical Calculations`, `Safety Checklist` |
| `7. Results` | `Measurement Ledger`, `Traceability Matrix` |
| `9. Conclusions` | `Next Steps` |

An unknown subsection between two required ones is legal. A required subsection under the
wrong parent is absent for that parent.

### Required tables

The section-1 identity table header is pinned as `Field | Value` (Open Question 2). Its rows
carry the homework identity and the implementation commit; they are not a free-form key/value
store.

Six evidence tables are required, each with this exact header:

- **Assumptions** — `ID | Assumption | Impact if wrong | Validation`
- **Bill of materials** — `Ref | Part or value | Quantity | Package | Source or link | Notes`
- **Pin map** — `Signal | Pin | Connects to | Notes`
- **Electrical calculations** — `ID | Quantity | Formula | Units | Input provenance | Result | Uncertainty | Assumption effect`
- **Measurement ledger** — `ID | Quantity | Value | Label | Instrument | Method | Uncertainty | Implementation commit`
- **Traceability matrix** — `ID | Claim or requirement | Design artifact | Verification method | Evidence | Status`

Every row keeps its header's cell count. A literal pipe inside a cell is escaped as `\|`. The
assumption `Impact if wrong` and `Validation` cells, and the calculation `Input provenance`,
`Result`, `Uncertainty`, and `Assumption effect` cells, are non-empty. Every table carries at
least one data row, or the not-applicable marker where the contract allows it.

### Required paragraphs

- Section 8 must contain at least one paragraph beginning `Industry note:`.
- Section 9 must contain a paragraph beginning `Status:`.
- Section 10 must contain at least one IEEE-numbered entry matching `[N]`.

The document carries exactly one level-1 heading, and its text equals `homework.yaml` `title`.

## When a section does not apply

The single marker is `_Not applicable — <reason>._`, with a non-empty reason. It replaces the
artifact; it never sits beside one, and a table is never left empty.

The marker is allowed only where the artifact can genuinely be absent:

- Section 3 may be not applicable with a reason.
- Section 5 and its four subsections may be not applicable for a software-only assignment.
- Every other numbered section, and the Decision Appendix, is never not applicable.

An N/A `## 5. Hardware and Wiring` waives its four subsections; otherwise all four are
required (Open Question 1). A marker written with no reason, or in a forbidden position, is an
error.

## Evidence vocabulary

Every measurement-ledger row carries exactly one label from this closed set:

- `measured`
- `calculated`
- `simulated`
- `datasheet`
- `not measured`
- `measured (observed)`

A bare `observed` is never a label. The qualified form `measured (observed)` is the only
variant.

The `Value` cell begins with the prefix its label requires:

- `not measured` begins `not measured: <reason>`.
- `measured` begins `user-reported:` or `serial-log:`.
- `measured (observed)` begins `serial-log:`.

A row also records the provenance depth its label promises: a `datasheet` row cites an `[N]`
source in its instrument or method cell, a `calculated` row names a `C-NN` calculation, a
`simulated` row names a scenario or run-artifact path, and a `measured` row names an
instrument other than `none`.

The vocabulary is scoped to the ledger `Label` and `Value` cells. Prose elsewhere may discuss
`observed` or `not measured`; a document-wide keyword scan would false-positive on the
explanation, so none is used.

## Cross-file rules

The checker compares the report with the repository. These rules are machine-checked against
normalized values, never display prose:

- **Identity.** The H1 equals `homework.yaml` `title`. The section-1 `Homework ID`, `Title`,
  `Homework status`, and `Report status` cells equal `id`, `title`, `status`, and
  `report.status`.
- **Toolchain.** `Framework` is compared case-insensitively. `PlatformIO Core` and `Platform`
  are compared after normalization, so `platformio/espressif32 8.0.0` equals
  `espressif32@8.0.0`. `Board` and `Language` are display text and are not string-compared.
- **Commit identity.** The `Implementation commit` cell is a 7-40 character lowercase hex
  string, and every ledger row repeats the same value. A ledger that names a different code
  tree is not evidence for this report.
- **BOM and diagram.** Every bill-of-materials `Ref` is a part id in `assets/diagram.json`.
  Extra diagram parts without a BOM row are allowed, because the diagram may carry virtual
  instruments such as the serial monitor. When the BOM applies, a missing or malformed
  diagram is an error.
- **Links.** Every relative Markdown link and image target resolves under the homework
  directory or the repository root. A target that escapes either root is an error. External
  URLs are never fetched.
- **Cross-references.** `A-NN`, `C-NN`, `L-NN`, and `T-NN` ids are unique within their table,
  and every in-text citation of one resolves to a matching row. Every `[N]` citation resolves
  to a section-10 entry, and every entry is cited at least once in sections 1-9 or the
  Decision Appendix.
- **Requirement coverage.** The traceability matrix cites each of `REPORT-01` through
  `REPORT-08` at least once.
- **Language and sentinels.** `report.md` contains no Cyrillic codepoint. A `draft` or
  `complete` report contains no `TODO` or `TBD` sentinel.
- **Status claims.** When `tests.native` is true, section 7 carries a `**Native suite.**` or
  `**Native tests.**` paragraph. When `homework.yaml` declares a simulation block, section 7
  carries a `**Simulation.**` paragraph whose run claim agrees with `simulation.status`.

## Status and the gate

The report status moves in one direction:

1. `placeholder` — the scaffolded skeleton. The document must exist and be non-empty; its
   headings and tables are not validated.
2. `draft` — authoring has started. The full contract applies.
3. `complete` — the author asserts the contract is satisfied and every claim carries a label.

The status pair must be consistent with the homework status:

| Homework status | Allowed report status |
|-----------------|-----------------------|
| `planned` | `placeholder` |
| `in-progress` | `draft` or `complete` |
| `complete` | `complete` |
| `verified` | `complete` |

`complete` certifies the checked contract and the honesty of the labels. It does not assert
that a bench measurement exists: a report may be complete with `not measured` rows when the
`Status:` paragraph states the evidence basis (D-35).

The check is a merge precondition, not advice. It runs in the local `check-report` hook, in
the CI `meta` job through `pre-commit run --all-files`, and through the required `gate`
fan-in.

Flip `placeholder → draft` when authoring starts and `→ complete` when this checklist passes.
The transition is a documented process, not a machine rule (D-43).

## Rule reference

The table lists every rule id the checker emits, in registry order. The set of ids here equals
`scripts/report/vocabulary.py` `RULES` exactly; a rule added in code without a row here fails
`RuleRegistryTests`.

| Rule | Meaning | Fix |
|------|---------|-----|
| `RPT-001` | the report declaration is missing, unreadable, or its `path` is uncontained | add a `report` block with `path` and `status` to `homework.yaml`, and keep `path` a relative path inside the homework directory |
| `RPT-002` | the declared report document is absent, empty, or a symlink | write a non-empty `report.md` at `report.path`; never commit a symlink |
| `RPT-003` | the homework status and report status disagree | align the pair: planned/placeholder, in-progress/draft or complete, complete or verified/complete |
| `RPT-004` | the report document exceeds the size bound | split unrelated material out of the report; keep it under one mebibyte |
| `RPT-101` | a required numbered heading is missing | add the heading exactly as the ten-section contract spells it |
| `RPT-102` | the numbered headings are out of ascending order | move the heading to its numbered position |
| `RPT-103` | a numbered heading appears more than once | keep one copy of the heading |
| `RPT-405` | the report contains a Cyrillic codepoint | rewrite the text in English; `report.md` is English-only |
| `RPT-406` | a draft or complete report still carries a TODO or TBD sentinel | replace the sentinel with the real content, or keep the report at `report.status: placeholder` until authoring starts |

## Self-audit checklist

Work through all eight groups before opening a pull request. Each item names the machine rules
that back it; the rule reference states the fix. The checklist is derived from the rule ids, so
the human review and the machine gate share one source (D-25).

- [ ] **Sections.** All ten numbered headings are present, literal, ordered, and unique; the
  four required subsection groups are under their parents; section 8 opens a paragraph with
  `Industry note:`; section 9 opens one with `Status:`; the document has exactly one H1 equal
  to the metadata title; every relative link and image resolves; the text is English-only
  (`RPT-101`, `RPT-102`, `RPT-103`, `RPT-104`, `RPT-107`, `RPT-108`, `RPT-401`, `RPT-404`,
  `RPT-405`).
- [ ] **Bill of materials.** Every `Ref` is a part id in `assets/diagram.json`; the six-column
  header is literal; every row keeps the header's cell count; the table has at least one data
  row or the marker; the diagram is present and readable when the BOM applies (`RPT-201`,
  `RPT-202`, `RPT-204`, `RPT-206`, `RPT-207`).
- [ ] **Pin map.** The four-column header uses `Pin`, not a board-specific column name; every
  signal maps to a pin and a connection; every row keeps the header's cell count (`RPT-201`,
  `RPT-202`).
- [ ] **Calculations.** Every family the design exercises is selected from
  `docs/standards/electrical-calculations.md`; each row states the formula, units, input
  provenance, result, uncertainty, and assumption effect; every required cell is non-empty
  (`RPT-201`, `RPT-202`, `RPT-203`, `RPT-204`).
- [ ] **Safety.** The checklist names at least one hazard, and every bullet opens with a bold
  `- **Hazard.**` prefix that states the consequence and the check (`RPT-205`).
- [ ] **Ledger.** Every row uses exactly one label from the vocabulary; every value carries the
  prefix its label requires; every implementation commit is the same 7-40 character lowercase
  hex value as section 1; every row carries the provenance depth its label promises (`RPT-301`,
  `RPT-303`, `RPT-304`, `RPT-305`).
- [ ] **Traceability.** Every status is `verified`, `manual`, `pending`, or `not applicable`;
  every artifact and evidence token resolves; every id is well formed and unique; every
  in-text id resolves; the matrix cites `REPORT-01` through `REPORT-08` (`RPT-306`, `RPT-307`,
  `RPT-308`, `RPT-309`, `RPT-310`).
- [ ] **Status.** The homework status and report status pair is allowed; the report exists and
  is non-empty; the section-1 identity and toolchain cells equal their metadata values; a
  `draft` or `complete` report carries no `TODO`/`TBD`; the section-7 native and simulation
  claims agree with `homework.yaml` (`RPT-001`, `RPT-002`, `RPT-003`, `RPT-004`, `RPT-402`,
  `RPT-403`, `RPT-406`, `RPT-407`, `RPT-408`).

## Review-enforced standards

Four expectations are documented here but deliberately not machine-checked. They need judgment
and would be brittle as a keyword rule:

- **Semantic truth.** The checker cannot decide whether a value was really measured, whether a
  citation supports the claim, or whether the analysis is honest. That remains a review duty
  (D-14).
- **Catalog membership.** `docs/standards/electrical-calculations.md` is a selection aid. The
  checker validates the calculation table's eight columns and non-empty cells, never whether a
  row names a catalog family; enforcing membership would couple report wording to a growing
  catalog (D-24).
- **Uncertainty basis.** Each uncertainty cell states its basis: a tolerance stack, meter
  accuracy, a datasheet bound, or an expanded uncertainty with a coverage factor (GUM-lite,
  D-42). A bare `±` without a stated basis is discouraged in review.
- **Instrument vocabulary.** Prefer `multimeter`, `oscilloscope`, `logic analyzer`,
  `power supply`, `thermal camera`, `Wokwi`, or `none`, but a new instrument is allowed
  without a checker change.

---
phase: 10-report-and-evidence-system
plan: "02"
subsystem: tooling
tags: [python, markdown-parser, table-contract, bom, diagram, stdlib]

requires:
  - phase: 10-report-and-evidence-system
    provides: plan 10-01's stdlib-only scripts/report package, fence-aware Markdown scan, pipe-cell helpers and the record/exit-code contract
provides:
  - scripts/report/tables.py extract_tables/Table/Row table-block extraction
  - rule ids RPT-201..RPT-207 with a violating fixture per rule
  - BOM referential integrity against assets/diagram.json with a non-raising parse
  - a fixture report carrying all seven contracted tables and a default diagram
affects: [10-03, 10-04, 10-05, 10-06]

actuals:
  tokens: 10414
  tasks: 3
  commits: 3
  plan_head_before: 90c15c0bfdf0da13aa8c99bac8a6fbf670932b61
  plan_head_after: d2ef2735a87a1e66fee362525fadd3216fd7974c

tech-stack:
  added: []
  patterns:
    - "Table blocks are extracted in the same fence-aware pass that classifies headings; a table inside a fence is invisible"
    - "A rule family does not hide another: heading-presence errors short-circuit, but table rules run alongside subsection rules"
    - "The diagram parse is a pure text-to-parts function in contract.py; only the CLI reads the file"
    - "A not-applicable marker waives its own artifact: section level for the whole section, subsection level for that subsection only"

key-files:
  created: []
  modified:
    - scripts/report/tables.py
    - scripts/report/contract.py
    - scripts/report/vocabulary.py
    - scripts/tests/test_report.py
    - scripts/check_report.py

key-decisions:
  - "REQUIRED_TABLES wires each header literal from vocabulary.py to its owning section and subsection; contract.py never restates a header tuple"
  - "The diagram read lives in check_report.py through read_regular_text inside the report size gate, while json.loads and the shape check live in contract.parse_diagram, so the contract module stays free of file I/O (D-02)"
  - "Table rules run with the subsection rules rather than after them, so the live 1.3 report reports its pin-map header (RPT-201) and its missing Next Steps (RPT-104) in one pass"
  - "A malformed not-applicable marker is reported by RPT-105 and waives nothing; only a valid marker suppresses a table rule"
  - "The compliant fixture now carries all seven tables and a default assets/diagram.json with part ids esp and r1, the first consumer of the diagram that plan 10-01 deliberately deferred"

patterns-established:
  - "One Table record (header_line, normalized header, rows) feeds every table rule, so 10-03 reuses the extractor for the ledger and matrix"
  - "A hostile cross-file input is parsed behind a never-raising boundary and reported as a content error at exit 1, never a traceback or exit 2"

requirements-completed: [REPORT-02, REPORT-03, REPORT-04, REPORT-05]

coverage:
  - id: D1
    description: "Fence-aware table-block extraction plus exact header matching for the section-1 metadata table and the six D-08 data tables"
    requirement: REPORT-02
    verification:
      - kind: unit
        ref: "scripts/tests/test_report.py#PinMapTests"
        status: pass
    human_judgment: false
  - id: D2
    description: "Row-shape (RPT-202), required-cell (RPT-203) and data-row-or-not-applicable (RPT-204) rules, including escaped-pipe cell counts"
    requirement: REPORT-04
    verification:
      - kind: unit
        ref: "scripts/tests/test_report.py#CalculationsTests"
        status: pass
    human_judgment: false
  - id: D3
    description: "The safety checklist carries at least one bold `- **` hazard bullet (RPT-205)"
    requirement: REPORT-05
    verification:
      - kind: unit
        ref: "scripts/tests/test_report.py#SafetyTests"
        status: pass
    human_judgment: false
  - id: D4
    description: "BOM referential integrity against assets/diagram.json (RPT-206) with an absent or malformed diagram reported as RPT-207"
    requirement: REPORT-02
    verification:
      - kind: unit
        ref: "scripts/tests/test_report.py#BomTests"
        status: pass
      - kind: integration
        ref: "uv run scripts/check_report.py"
        status: pass
    human_judgment: false

duration: 15 min
completed: 2026-10-27
status: complete
---

# Phase 10 Plan 02: Table Contract and BOM Referential Integrity Summary

**The report's seven contracted tables are now machine-checked: exact headers, row shape, required cells, a data-row-or-N/A rule, bold safety bullets, and BOM references that must exist as `assets/diagram.json` part ids.**

## Performance

- **Duration:** 15 min
- **Started:** 2026-10-27T14:05Z
- **Completed:** 2026-10-27T14:20Z
- **Tasks:** 3
- **Files modified:** 5 (4 report modules/tests, 1 CLI)

## Accomplishments

- `scripts/report/tables.py` gained `extract_tables`, `Table` and `Row`. The extractor
  reuses the `markdown.FENCE` definition, so a table drawn inside a fenced block is never
  parsed, and it keeps a mismatched row instead of dropping it, so the shape rule can name
  it.
- `RPT-201` matches the first table inside each owning section or subsection against the
  literal in `vocabulary.py`, naming the table, its header line, and both the observed and
  expected headers. The seven owners are the section-1 metadata table, assumptions, BOM,
  pin map, calculations, ledger, and traceability matrix.
- `RPT-202` counts cells after the escaped-pipe-aware split; `RPT-203` requires the D-15
  non-empty cells and names the column; `RPT-204` requires a data row or the N/A marker;
  `RPT-205` requires at least one `- **` hazard bullet.
- `RPT-206`/`RPT-207` compare every BOM `Ref` with `assets/diagram.json` part ids. The
  diagram is read through `read_regular_text` (symlink-refusing) inside the report size
  gate, parsed by a never-raising `parse_diagram`, and a missing, unreadable, oversized,
  non-UTF-8, non-JSON or wrongly shaped file is one `RPT-207` at exit 1.
- The live 1.3 report now reports exactly one `RPT-201` (the `ESP32-S3 pin` pin-map header)
  and no `RPT-202`…`RPT-207` record, alongside the known `RPT-104`; exit 1, never 2.

## Task Commits

Each task was committed atomically:

1. **Task 1: Extract tables and enforce exact headers** - `46ac04e` (feat)
2. **Task 2: Row shape, required cells, data-row-or-N/A and safety** - `53acb68` (feat)
3. **Task 3: BOM referential integrity against `assets/diagram.json`** - `d2ef273` (feat)

**Plan metadata:** this SUMMARY commit (docs)

## Files Created/Modified

- `scripts/report/tables.py` — `extract_tables`, `Table`, `Row`, plus the existing cell
  helpers; the fence-aware block scanner.
- `scripts/report/contract.py` — `REQUIRED_TABLES`, `REQUIRED_CELLS`, `Diagram`,
  `parse_diagram`, `_table_records`, `_safety_records`, `_bom_records`, and the
  section/subsection waiver helpers.
- `scripts/report/vocabulary.py` — `RPT-201`…`RPT-207` registered with a summary and a
  remediation.
- `scripts/tests/test_report.py` — the seven table literals, the upgraded compliant
  fixture, `PinMapTests`, `CalculationsTests`, `SafetyTests`, and `BomTests`.
- `scripts/check_report.py` — `_read_diagram` and the diagram pass-through into
  `validate_report`.

## Decisions Made

- **Header literals stay in one module.** `REQUIRED_TABLES` in `contract.py` references
  the vocabulary constants by name; no header tuple is restated.
- **The diagram parse is pure.** `parse_diagram(text)` in `contract.py` owns `json.loads`
  and the `parts` shape check; `check_report.py` owns the file read and the size gate.
  This keeps `contract.py` free of file I/O (D-02) while placing the parse where the
  threat register expects it.
- **Table rules do not hide behind subsection errors.** Heading-presence failures
  (RPT-101…103) still short-circuit, because a missing section would cascade. Subsection
  and paragraph failures do not, so the live report's `RPT-104` and its pin-map `RPT-201`
  both appear.
- **Waivers are per artifact.** A valid marker before the first `###` waives the whole
  section; a marker inside one `###` waives that subsection only. A malformed marker
  waives nothing and is already `RPT-105`.
- **The fixture gained the diagram now.** Plan 10-01 deliberately shipped no
  `assets/diagram.json` because no rule read it; this plan is the first consumer, so the
  default fixture writes `esp` and `r1`, matching its BOM rows.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Task 1's verification selector needed tests in Task 1**
- **Found during:** Task 1
- **Issue:** the plan's Task 1 `<verify>` runs `-k pin_map`, but the plan's file list for
  Task 1 omitted `scripts/tests/test_report.py`; without a `PinMapTests` class the
  selector would report `Ran 0 tests`.
- **Fix:** added `PinMapTests` (four `test_pin_map_*` methods) in Task 1, proving exact
  headers for all seven tables, the renamed pin-map column with its true line, and the
  absent-table case.
- **Files modified:** `scripts/tests/test_report.py`
- **Verification:** `python3 -m unittest scripts.tests.test_report -k pin_map -v` — 4
  tests, green.
- **Committed in:** `46ac04e`

**2. [Rule 2 - Missing Critical] The compliant fixture needed all seven tables and a diagram**
- **Found during:** Tasks 1 and 3
- **Issue:** the plan-10-01 fixture satisfied only the heading rules; it had no BOM, pin
  map, calculations, ledger, or traceability table and no diagram. Once `RPT-201` and
  `RPT-207` existed, every acceptance test would fail for an unrelated reason.
- **Fix:** the fixture now composes the seven table literals into the section bodies, and
  `write_report` writes a default `assets/diagram.json` unless a test asks for none.
- **Files modified:** `scripts/tests/test_report.py`
- **Verification:** the full report suite and `python3 -m unittest discover scripts/tests`
  are green; the diagram-specific tests cover missing, malformed, extra-part and N/A
  shapes.
- **Committed in:** `46ac04e` (tables) and `d2ef273` (diagram)

---

**Total deviations:** 2 auto-fixed (1 blocking, 1 missing critical).
**Impact on plan:** the rules are exactly as specified. The fixture grew because the
contract now consumes it; no rule was weakened to make the real tree pass.

## Issues Encountered

- The first missing-diagram assertion expected the phrase `assets/diagram.json is absent`,
  while `read_regular_text` reports `cannot read …: file is absent`. The test now asserts
  the file name and `file is absent`, keeping the honest shared-helper message rather than
  duplicating the wording.

## User Setup Required

None — no external service configuration required.

## Verification

- `python3 -m unittest scripts.tests.test_report -k bom` — 9 tests, green.
- `-k pin_map` — 4 tests, green; `-k calculations` — 6 tests, green; `-k safety` — 4
  tests, green. Each selector is non-zero.
- `python3 -m unittest scripts.tests.test_report` — 50 tests, green.
- `python3 -m unittest discover scripts/tests` — 491 tests, `OK (skipped=1)`.
- `uv run scripts/check_report.py` on the real tree — exit 1 with exactly one `RPT-201`
  (the pin-map header) and the known `RPT-104`; no `RPT-202`…`RPT-207` record.
- `uv run ruff check` on every changed Python file — no issues.
- No commit bypassed the hooks; `ruff check`, secret scan, generated-file and generated
  view/skill mirrors passed on all three task commits.

## Next Phase Readiness

- Plan 10-03 can import `scripts.report.tables.extract_tables` for the ledger and the
  traceability matrix instead of re-parsing pipe rows.
- The `RPT-201`…`RPT-207` ids and messages are stable and ready for the
  `docs/standards/report.md` remediation table (10-05).
- The real tree still intentionally fails `RPT-104` and the pin-map `RPT-201` until the
  1.3 retrofit in plan 10-06, per D-44.

## Self-Check: PASSED

- Modified files exist: `scripts/report/tables.py`, `scripts/report/contract.py`,
  `scripts/report/vocabulary.py`, `scripts/tests/test_report.py`,
  `scripts/check_report.py`.
- Commits exist on `worktree-agent-ad6437aec376852ca`: `46ac04e`, `53acb68`, `d2ef273`.
- Full suite: `Ran 491 tests — OK (skipped=1)`.

---
*Phase: 10-report-and-evidence-system*
*Completed: 2026-10-27*

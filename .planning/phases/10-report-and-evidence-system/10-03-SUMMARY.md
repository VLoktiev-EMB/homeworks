---
phase: 10-report-and-evidence-system
plan: "03"
subsystem: tooling
tags: [python, report-checker, evidence-ledger, traceability, ieee-citations, stdlib]

requires:
  - phase: 10-report-and-evidence-system
    provides: plan 10-01's report engine and rule/record contract, and plan 10-02's table extraction and BOM/diagram checking
provides:
  - rule ids RPT-301, RPT-303, RPT-304, RPT-305 for the measurement ledger
  - rule ids RPT-306, RPT-307, RPT-308, RPT-310 for the traceability matrix
  - rule ids RPT-309, RPT-311, RPT-312 for intra-report ids and IEEE citations
  - resolve_artifact(token, homework_dir, repo_root) for plan 10-04's internal links
  - markdown.reference_entries / markdown.citation_tokens section-scoped helpers
affects: [10-04, 10-05, 10-06]

actuals:
  tokens: 10763
  tasks: 3
  commits: 3
  plan_head_before: 39f94bcfe19f86e45d5f16ff1ab23b342d9055c5
  plan_head_after: 2f763b7

tech-stack:
  added: []
  patterns:
    - "Every evidence rule is scoped to a cell or a named section, never a document-wide sweep"
    - "Artifact tokens are only backticked spans, split on whitespace, so a command is not one path"
    - "Lexical containment gates every artifact candidate; only existence is checked, never contents"

key-files:
  created: []
  modified:
    - scripts/report/contract.py
    - scripts/report/markdown.py
    - scripts/report/vocabulary.py
    - scripts/tests/test_report.py

key-decisions:
  - "`RPT-302` is deliberately unregistered and reserved for a future bare-`observed`-in-prose rule; the reservation is documented in vocabulary.py so the gap is intentional, not an omission"
  - "resolve_artifact tries the homework directory and then the repository root as starting points, then requires lexical containment and a resolved containment as defence in depth; an absolute token is rejected before any filesystem call"
  - "RPT-310 emits one record per missing REPORT-01..REPORT-08 requirement at line 0, so zero rows yields eight records ordered by requirement id"
  - "RPT-307 checks only `Design artifact` and `Evidence` cells; a `pending` row and a row with an invalid status are exempt from artifact resolution"
  - "Reference entries are paragraphs inside `## 10. References` only and citations are collected from sections 1-9 plus the decision appendix, so the wrapped `[1]` line in section 8 stays a citation"

patterns-established:
  - "A provenance rule reads only the cell whose label makes the promise; the surrounding prose is never scanned"
  - "Section-scoped citation collection in markdown.py replaces the forbidden document-wide `^\\[N\\] ` sweep"

requirements-completed: [REPORT-06, REPORT-07]

coverage:
  - id: D1
    description: "Measurement-ledger vocabulary, value prefixes, commit identity, and provenance depth"
    requirement: REPORT-06
    verification:
      - kind: unit
        ref: "scripts/tests/test_report.py#LedgerTests"
        status: pass
      - kind: integration
        ref: "uv run scripts/check_report.py (real tree has no RPT-301/303/304/305 record)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Traceability status enum, artifact existence, id shape/uniqueness, and REPORT-01..08 coverage"
    requirement: REPORT-07
    verification:
      - kind: unit
        ref: "scripts/tests/test_report.py#TraceabilityTests"
        status: pass
      - kind: integration
        ref: "uv run scripts/check_report.py (real tree has no RPT-306/307/308 record)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Intra-report id resolution and bidirectional IEEE citation checks"
    requirement: REPORT-07
    verification:
      - kind: unit
        ref: "scripts/tests/test_report.py#CrossReferenceTests"
        status: pass
      - kind: integration
        ref: "uv run scripts/check_report.py (real tree has no RPT-309/311/312 record)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Shared resolve_artifact helper for plan 10-04's internal-link rule"
    verification:
      - kind: unit
        ref: "scripts/tests/test_report.py#TraceabilityTests.test_traceability_escaping_token_reports_rpt_307"
        status: pass
    human_judgment: false

duration: 5 min
completed: 2026-10-27
status: complete
---

# Phase 10 Plan 03: Evidence and Cross-Reference Summary

**The measurement ledger and the traceability matrix are now machine-checked: labels, value prefixes, commit identity, provenance depth, status enum, artifact existence, id resolution, requirement coverage, and both directions of the IEEE citation graph.**

## Performance

- **Duration:** 5 min
- **Started:** 2026-10-27T14:23:33Z
- **Completed:** 2026-10-27T14:28:24Z
- **Tasks:** 3
- **Files modified:** 4

## Accomplishments

- `RPT-301`/`RPT-303`/`RPT-304`/`RPT-305` cover the ledger: the closed label set
  (`observed` alone fails), the value prefix each label requires, the 7-40 character
  lowercase hex commit compared against the section-1 cell, and the provenance depth
  (datasheet `[N]`, calculated `C-NN`, simulated scenario path, measured instrument).
- `RPT-306`/`RPT-307`/`RPT-308`/`RPT-310` cover the matrix: the status enum, artifact and
  evidence existence for `verified`/`manual`/`not applicable` rows, `A-NN`/`C-NN`/`L-NN`/`T-NN`
  shape and uniqueness, and one record per missing `REPORT-01`..`REPORT-08`.
- `RPT-309`/`RPT-311`/`RPT-312` close the cross-reference graph: in-text ids resolve inside
  sections 1-9 and the appendix, citations without entries fail, and entries without
  citations fail.
- `resolve_artifact(token, homework_dir, repo_root)` is exported for plan 10-04's RPT-404;
  it rejects absolute tokens before any filesystem call, tries both roots, and checks only
  existence.
- The live report yields no `RPT-30x`/`RPT-31x` record: all 12 ledger rows, 17 matrix rows,
  8+6+12+17 ids, and six citations pass, including the wrapped `[1]` line at section 8.

## Task Commits

Each task was committed atomically:

1. **Task 1: Ledger vocabulary, value prefixes, commit identity, provenance depth** - `eb6405b` (feat)
2. **Task 2: Traceability status, artifacts, ids, requirement coverage** - `7bae82e` (feat)
3. **Task 3: Section-scoped ids and bidirectional IEEE citations** - `2f763b7` (feat)

**Plan metadata:** this SUMMARY commit (docs)

## Files Created/Modified

- `scripts/report/contract.py` — `path_like`, `artifact_tokens`, `resolve_artifact`,
  `_ledger_records`, `_traceability_records`, `_defined_ids`, `_cross_reference_records`,
  `_citation_records`, and the constants they read.
- `scripts/report/markdown.py` — `REFERENCE_ENTRY`, `CITATION`, `reference_entries`, and
  `citation_tokens`, all paragraph- and section-scoped.
- `scripts/report/vocabulary.py` — `EVIDENCE_LABEL_ORDER`, `TRACEABILITY_STATUSES`, and the
  registry entries for `RPT-301`, `RPT-303`..`RPT-312` with the `RPT-302` reservation note.
- `scripts/tests/test_report.py` — `LedgerTests`, `TraceabilityTests`, `CrossReferenceTests`,
  the section-1 commit row, the two-row traceability fixture citing every requirement, the
  section-4 `[1]` citation, and the `platformio.ini` fixture artifact.

## Decisions Made

- **`RPT-302` stays unregistered.** The id is reserved for a future bare-`observed`-in-prose
  rule, and the reservation is written next to the registry so the gap is visibly intended.
- **Artifact resolution starts from both roots.** A token is tried under the homework
  directory and under the repository root, because the live matrix mixes
  homework-relative (`lib/pattern/src/controller.c`) and repository-relative
  (`scripts/check_architecture.py`, `../../scripts/pio/merge_firmware.py`) tokens.
- **Containment is lexical first.** `os.path.abspath` normalizes `.`/`..` without following
  a symlink; a resolved containment check is the defence in depth. Only `Path.exists()` is
  called, never a read.
- **Artifact tokens are backticked spans only.** A span is split on whitespace, so
  `` `pio run -d homeworks/1_3-police-flasher` `` contributes only its path-like token.
- **RPT-307 checks `Design artifact` and `Evidence` only.** D-13 names those two cells;
  `Verification method` commands such as `check_metadata.py` are deliberately not resolved.
- **Reference and citation collection is section-scoped.** Entries come only from
  `## 10. References` at paragraph starts; citations come only from sections 1-9 and the
  decision appendix. This is what keeps the wrapped `[1]` line in section 8 a citation
  rather than a seventh entry.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Task 1's verification selector needed `LedgerTests` in Task 1**
- **Found during:** Task 1
- **Issue:** Task 1's `<verify>` runs `-k ledger`, but its `<files>` list omitted
  `scripts/tests/test_report.py`; without a `LedgerTests` class the selector would report
  `Ran 0 tests`.
- **Fix:** added `LedgerTests` (twelve `test_ledger_*` methods) in Task 1.
- **Files modified:** `scripts/tests/test_report.py`
- **Verification:** `python3 -m unittest scripts.tests.test_report -k ledger -v` — 12 tests, green.
- **Committed in:** `eb6405b`

**2. [Rule 2 - Missing Critical] The compliant fixture grew to satisfy the new rules**
- **Found during:** Tasks 1-3
- **Issue:** the plan-10-02 fixture had no section-1 commit row, one traceability row that
  cited no requirement, no citation in sections 1-9, and no `platformio.ini`. Once
  `RPT-304`, `RPT-310`, `RPT-312`, and `RPT-307` existed, every acceptance test would fail
  for an unrelated reason.
- **Fix:** added `| Implementation commit | 9e1238d |` to the section-1 table, a second
  traceability row citing `REPORT-01`..`REPORT-08`, the `[1]` citation in section 4, and a
  `platformio.ini` written by `write_report`.
- **Files modified:** `scripts/tests/test_report.py`
- **Verification:** the full report suite is green; each negative fixture fails only because
  of its single mutation.
- **Committed in:** `eb6405b` (commit row), `7bae82e` (traceability row and artifact),
  `2f763b7` (citation)

**3. [Rule 3 - Blocking] Task 3's rule ids also needed `vocabulary.py` registration**
- **Found during:** Task 3
- **Issue:** Task 3's `<files>` list omitted `scripts/report/vocabulary.py`, but a rule that
  is not in `RULES` is not part of the stable contract the tests and the future
  `docs/standards/report.md` assert.
- **Fix:** registered `RPT-309`, `RPT-311`, and `RPT-312` with their summaries and
  remediations.
- **Files modified:** `scripts/report/vocabulary.py`
- **Verification:** the registry is complete; `ruff` is clean and the suite is green.
- **Committed in:** `2f763b7`

---

**Total deviations:** 3 auto-fixed (2 blocking, 1 missing critical).
**Impact on plan:** the rules are exactly as specified. The fixture grew because the
contract now consumes it; no rule was weakened to make the real tree pass.

## Issues Encountered

- The plan's verification text says the real tree exits 1 "only for `RPT-104` and
  `RPT-310`". The measured run reports one more expected record, `RPT-201` for the live
  pin-map header (`ESP32-S3 pin` vs `Pin`), which plan 10-06 retrofits per D-44. The
  checker is not weakened; the actual output is recorded below.

## User Setup Required

None — no external service configuration required.

## Verification

- `python3 -m unittest scripts.tests.test_report -k ledger -v` — 12 tests, green.
- `python3 -m unittest scripts.tests.test_report -k traceability -v` — 11 tests, green.
- `python3 -m unittest scripts.tests.test_report -k cross_reference -v` — 5 tests, green.
- `python3 -m unittest scripts.tests.test_report` — 78 tests, green.
- `python3 -m unittest discover scripts/tests` — 527 tests, `OK (skipped=1)`.
- `uv run ruff check` on every changed Python file — no issues.
- `uv run scripts/check_report.py` on the real tree — exit 1 with exactly five expected
  records: `RPT-104` (missing `### Next Steps`), three `RPT-310` (REPORT-01, REPORT-05,
  REPORT-08), and `RPT-201` (the pin-map header). No evidence, id, or citation record.
- No commit bypassed the hooks; `ruff`, the secret scan, and the generated-file,
  generated-view, and skills-mirror gates passed on all three task commits.

## Next Phase Readiness

- Plan 10-04 can import `resolve_artifact(token, homework_dir, repo_root)` directly for
  `RPT-404` and reuse the `artifact_tokens` heuristic for link targets.
- `RPT-301`..`RPT-312` are stable and ready for the `docs/standards/report.md` remediation
  table; `RPT-302` remains deliberately unregistered.
- The real tree still intentionally fails `RPT-104`, `RPT-201`, and the three `RPT-310`
  records until the 1.3 retrofit in plan 10-06.

## Self-Check: PASSED

- Modified files exist: `scripts/report/contract.py`, `scripts/report/markdown.py`,
  `scripts/report/vocabulary.py`, `scripts/tests/test_report.py`.
- Commits exist on `worktree-agent-a63f9d7067734f1ac`: `eb6405b`, `7bae82e`, `2f763b7`.
- Full suite: `Ran 527 tests — OK (skipped=1)`.

---
*Phase: 10-report-and-evidence-system*
*Completed: 2026-10-27*

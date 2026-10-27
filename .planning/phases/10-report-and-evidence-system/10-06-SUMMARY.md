---
phase: 10-report-and-evidence-system
plan: "06"
subsystem: documentation
tags: [python, report-checker, markdown, retrofit, real-tree, regression, traceability]

requires:
  - phase: 10-report-and-evidence-system
    provides: plans 10-01…10-04's checker, rule registry, table extraction, ledger rules, traceability rules, and document-integrity rules
provides:
  - "homeworks/1_3-police-flasher/report.md retrofitted with exactly the three D-44 edits, so the shipped worked example passes the contract"
  - "RealTreeTests in scripts/tests/test_report.py, locking the repository against the checker"
  - "The green real-tree baseline the check-report hook (plan 10-07) can now gate on"
affects: [10-07, 10-08, 11]

actuals:
  tokens: 2464
  tasks: 2
  commits: 2
  plan_head_before: f987410ce14821c9758e26d39c3f0ba47ed5bec6
  plan_head_after: ff746fadf51ab5aa88bfcd71312993c68026fda0

tech-stack:
  added: []
  patterns:
    - "A retrofit is bounded: change only the cells the contract names and leave every claim, value, label, and commit untouched"
    - "A real-tree regression asserts the checker's exit code, summary line, JSON shape, sort order, and byte-identical determinism, and guards its count assertion against vacuity"
    - "A live-tree family test asserts the whole-tree exit code as well as the absence of its own rule family, so a rule cannot pass while unrelated violations stay open"

key-files:
  created: []
  modified:
    - homeworks/1_3-police-flasher/report.md
    - scripts/tests/test_report.py

key-decisions:
  - "The pin-map change rewrites the header row and its separator row together, because a wide separator under the shortened header reads as a typo; no data row, claim, value, label, or commit moved"
  - "T-19 anchors the safety checklist by naming `report.md` in the Design artifact cell, so RPT-307 still resolves a real file instead of exempting prose"
  - "T-20 is `manual`, not `verified`: honest status, known limitations, and next steps are a human review, not a command that produces evidence"
  - "The six pre-existing live-tree tests moved from exit 1 to exit 0 because the retrofit removes the last violations; they still assert their own rule family is absent and now additionally assert the whole tree passes (no rule weakened)"

patterns-established:
  - "`RealTreeTests` discovers reports with `Path(\"homeworks\").glob(\"*/report.md\")`, asserts the discovery is non-empty, and then compares the record count to it"
  - "The JSON shape assertion checks `rule` and `line` presence, every `path` is a file, and the array is sorted by `(path, line, rule)`"

requirements-completed: [REPORT-01, REPORT-03, REPORT-05, REPORT-07, REPORT-08]

coverage:
  - id: D1
    description: "The shipped worked example satisfies the report contract: pin-map header `Pin`, `### Next Steps` in section 9, and traceability rows T-18…T-20 for REPORT-01, REPORT-05, and REPORT-08"
    requirement: REPORT-01
    verification:
      - kind: integration
        ref: "uv run scripts/check_report.py — exit 0, one OK record, PASS summary"
        status: pass
    human_judgment: false
  - id: D2
    description: "RealTreeTests locks the shipped tree: exit 0, PASS summary, one OK record per discovered report, rule/line keys, sorted array, byte-identical consecutive runs"
    requirement: REPORT-07
    verification:
      - kind: unit
        ref: "python3 -m unittest scripts.tests.test_report -k real_tree -v — Ran 3 tests, OK"
        status: pass
    human_judgment: false

duration: 3min
completed: 2026-10-27
status: complete
---

# Phase 10 Plan 06: Retrofit the Worked Example and Lock the Real Tree Summary

**The shipped 1.3 report now passes its own contract through exactly the three D-44 edits, and `RealTreeTests` makes the repository itself the proof the contract is satisfiable.**

## Performance

- **Duration:** 3 min
- **Started:** 2026-10-27T14:42:12Z
- **Completed:** 2026-10-27T14:44:50Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- Retrofitted `homeworks/1_3-police-flasher/report.md` with the bounded three-edit change:
  the pin-map header cell became `Pin`, `### Next Steps` was added as the last subsection of
  section 9, and rows `T-18`…`T-20` were appended for `REPORT-01`, `REPORT-05`, and
  `REPORT-08` in the existing six-column grammar.
- `uv run scripts/check_report.py` now exits 0 on the real tree with
  `homeworks/1_3-police-flasher/report.md:0: OK — report contract satisfied` and
  `PASS: report contract satisfied`.
- Added `RealTreeTests` with three tests that assert the exit code and PASS summary, one
  `OK` record per `homeworks/*/report.md` with `rule` and `line` keys, every path a file,
  the `(path, line, rule)` sort order, and byte-identical consecutive runs.
- Verified the whole repository: `python3 -m unittest discover scripts/tests` runs 572 tests,
  `OK (skipped=1)`; `uv run scripts/check_metadata.py` exits 0.

## Task Commits

Each task was committed atomically:

1. **Task 1: Apply the bounded three-edit retrofit to the live report** - `a69c130` (docs)
2. **Task 2: Add the real-tree regression and prove the full contract on the repository** - `ff746fa` (test)

**Plan metadata:** this SUMMARY commit (docs: complete retrofit and real-tree plan)

## Files Created/Modified

- `homeworks/1_3-police-flasher/report.md` — the three D-44 edits: pin-map header literal,
  `### Next Steps`, and traceability rows `T-18`…`T-20`; no other statement changed.
- `scripts/tests/test_report.py` — `RealTreeTests`, a module-docstring note, and the six
  live-tree family assertions flipped from exit 1 to exit 0.

## Decisions Made

- The pin-map retrofit rewrote the header row and its separator row together. A four-column
  separator under a shortened header would read as a typo; the separator carries no claim,
  value, label, or commit, and every data row is byte-identical.
- `T-19` names `report.md` in `Design artifact` so the safety checklist is anchored to a path
  that exists; the alternative — leaving the cell prose-only — would make `RPT-307` silently
  vacuous for that row.
- `T-20` is `manual` because honest status, verified toolchain, known limitations, and next
  steps are owned by a human review; claiming `verified` would assert a command that does not
  exist.
- The six pre-existing live-tree tests now assert exit 0. Their family-specific
  `rules & {...}` assertions are unchanged, so they remain meaningful while the whole tree is
  also proven green; no rule was weakened to reach this state.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Flipped six pre-existing live-tree assertions from exit 1 to exit 0**
- **Found during:** Task 2 (real-tree regression)
- **Issue:** plan 10-06's retrofit removes the last three violation classes
  (`RPT-201`, `RPT-104`, three `RPT-310` records), so the identity, language, link, status
  claim, traceability, and cross-reference live-tree tests — which asserted `returncode == 1`
  — would fail and leave `python3 -m unittest discover scripts/tests` red, contradicting the
  plan's own verification.
- **Fix:** changed the six assertions to `assertEqual(0, result.returncode, ...)`. Each test
  still asserts its own rule family is absent from the JSON records; the change strengthens,
  rather than relaxes, the live-tree coverage.
- **Files modified:** `scripts/tests/test_report.py`
- **Verification:** `python3 -m unittest scripts.tests.test_report` — 123 tests, OK;
  `python3 -m unittest discover scripts/tests` — 572 tests, OK (skipped=1).
- **Committed in:** `ff746fa` (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** The retrofit itself is exactly the three D-44 edits. The auto-fix is the
mechanical consequence of the tree turning green and touches no contract rule.

## Threat Model Disposition

- **T-10-18 (Repudiation):** mitigated. `### Next Steps` restates only the bench evidence
  pass, the `hw/<id>` tag, and scale-out, each already named in section 9 or the `Status:`
  paragraph, and every new row is `verified` or `manual` with an artifact that resolves;
  `RPT-307` emits no record on the real tree.
- **T-10-19 (Tampering):** mitigated. The diff touches no measurement ledger row, calculation,
  reference, appendix, or `Implementation commit` value; the ledger rules re-ran green in the
  same gate.
- **T-10-SC (Tampering):** no new package, no hook change in this plan.

## Issues Encountered

None.

## Known Stubs

None. No placeholder text, hardcoded empty value, or unwired component was introduced.

## Threat Flags

None — the two modified files add no network endpoint, auth path, or schema surface.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- The real-tree baseline is green, so the `check-report` hook plan 10-07 adds can gate on a
  repository that satisfies its own contract instead of grandfathering the worked example.
- Every real `report.md` yields exactly one `OK` record, and `RealTreeTests` fails if a second
  report is added without a record or if a record stops being `OK`.
- No blocker remains for plans 10-07 and 10-08.

## Self-Check: PASSED

- Files exist: `homeworks/1_3-police-flasher/report.md`, `scripts/tests/test_report.py`.
- Commits exist on `worktree-agent-a0818a99934ab8d5d`: `a69c130`, `ff746fa`.
- Checker: `uv run scripts/check_report.py` — exit 0, one `OK` record, `PASS` summary.
- Suite: `python3 -m unittest discover scripts/tests` — 572 tests, `OK (skipped=1)`.

---
*Phase: 10-report-and-evidence-system*
*Completed: 2026-10-27*

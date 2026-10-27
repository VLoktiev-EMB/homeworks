---
phase: 10-report-and-evidence-system
plan: 10
subsystem: testing
tags: [python, report-contract, path-containment, symlink, hostile-input, json]

# Dependency graph
requires:
  - phase: 10-report-and-evidence-system
    plan: 09
    provides: hostile metadata and diagram bounds with a parseable --json contract
  - phase: 10-report-and-evidence-system
    plan: 01
    provides: the report contract rules and the RPT-* record family
provides:
  - `check_report._contained_report_path`, refusing an absolute, `..`-bearing, symlinked or realpath-escaping `report.path` before any read
  - `ReportPathContainmentTests` and `HostileDocumentContractTests` regression coverage
  - a tightened `RPT-001` summary and remediation in the registry and the standard
affects: [10-report-and-evidence-system, check_report]

# Actuals (#2632) — same estimateTokens scale as the plan's `estimate`.
actuals:
  tokens: 4001
  tasks: 2
  commits: 2
plan_head_before: 042d5bd44b1482d51087c7e8924fb48c708f481a
plan_head_after: 75eaebd125b686909e519e45782f0eb8e3feae61

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Contain an untrusted declared path lexically, then prove parent-realpath containment"
    - "Walk parent components with lstat and refuse a symlink on any prefix"
    - "Keep the final component's shipped classification by checking parents only"

key-files:
  created: []
  modified:
    - scripts/check_report.py
    - scripts/tests/test_report.py
    - scripts/report/vocabulary.py
    - docs/standards/report.md

key-decisions:
  - "Place `_contained_report_path` in `scripts/check_report.py`, the one module that performs file I/O; `scripts/report/contract.py` stays filesystem-free (D-02)."
  - "Reject any `..` component outright: after a symlinked component, lexical normalization can look contained while the real path escapes."
  - "Walk only the parent components with `lstat`, so the final-component symlink and the absent document keep their shipped `RPT-002` classification."
  - "Emit the refusal as `RPT-001` on `homework.yaml`, preserving any `RPT-003` already collected, and never echo the declared or host path."

patterns-established:
  - "Parent-component `lstat` walk plus parent-realpath containment: the `new_homework`/`resolve_artifact` posture applied to the declared report path."
  - "Contract-level hostile tests assert exit code, a parseable non-empty `--json` array, the five record keys, no traceback, and byte-identical reruns together."

requirements-completed: [REPORT-01, REPORT-02, REPORT-03, REPORT-04, REPORT-05, REPORT-06, REPORT-07, REPORT-08, TOOL-08]

coverage:
  - id: D1
    description: "An absolute report.path is RPT-001 at exit 1 and the outside file is never opened"
    requirement: REPORT-01
    verification:
      - kind: unit
        ref: "scripts/tests/test_report.py#ReportPathContainmentTests.test_absolute_report_path_is_rpt_001_and_never_read"
        status: pass
    human_judgment: false
  - id: D2
    description: "A ..-bearing report.path that leaves the homework directory is RPT-001 and is never opened"
    requirement: REPORT-02
    verification:
      - kind: unit
        ref: "scripts/tests/test_report.py#ReportPathContainmentTests.test_parent_directory_escape_is_rpt_001_and_never_read"
        status: pass
    human_judgment: false
  - id: D3
    description: "An intermediate symlink component is RPT-001 before any read, while the linked target stays unread"
    requirement: REPORT-03
    verification:
      - kind: unit
        ref: "scripts/tests/test_report.py#ReportPathContainmentTests.test_intermediate_symlink_is_rpt_001_and_never_read"
        status: pass
    human_judgment: false
  - id: D4
    description: "A compliant nested relative report.path is still accepted and the final symlink/absent cases stay RPT-002"
    requirement: REPORT-04
    verification:
      - kind: unit
        ref: "scripts/tests/test_report.py#ReportPathContainmentTests"
        status: pass
    human_judgment: false
  - id: D5
    description: "Deep metadata, deep diagram and an escaping path each keep the --json contract with deterministic bytes"
    requirement: TOOL-08
    verification:
      - kind: unit
        ref: "scripts/tests/test_report.py#HostileDocumentContractTests"
        status: pass
    human_judgment: false
  - id: D6
    description: "The registry and the standard agree on the tightened RPT-001 wording and the unchanged id set"
    requirement: REPORT-05
    verification:
      - kind: unit
        ref: "scripts/tests/test_report.py#RuleRegistryTests"
        status: pass
    human_judgment: false

# Metrics
duration: 10min
completed: 2026-10-27
status: complete
---

# Phase 10 Plan 10: Report Path Containment Summary

**A hostile `homework.yaml` can no longer redirect the checker outside the homework directory: an absolute, `..`-bearing, symlinked or realpath-escaping `report.path` is an `RPT-001` record at exit 1 and is never opened**

## Performance

- **Duration:** approx. 10 min
- **Completed:** 2026-10-27T15:56Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments

- Closed CR-03 of gap G-10-1: `_contained_report_path` rejects an absolute value and any `..` component, requires lexical containment under the homework directory, walks every parent component with `os.lstat`, and proves parent-realpath containment as defence in depth.
- The refusal is an `RPT-001` content record at exit 1 that names the failure class and never echoes the declared or a host path; any `RPT-003` status record already collected is preserved.
- The final component keeps its shipped classification: a symlinked or absent document is still `RPT-002`, and a compliant nested path such as `docs/report.md` still validates.
- Pinned the gap truth end to end across all three hostile inputs: deep metadata (`RPT-001`), deep diagram (`RPT-207`) and the escaping path (`RPT-001`) each exit 1 with a parseable non-empty `--json` array, the five record keys, no traceback and byte-identical repeated runs.
- Tightened the `RPT-001` summary and remediation in `RPT-001`'s registry entry and the standard's rule table without adding, removing or renumbering a rule id.

## TDD Evidence (RED before GREEN)

Task 1 is a `tracer`/`tdd="true"` task. The failing cases were written and run before the implementation:

- RED: `ReportPathContainmentTests` ran 6 tests, 3 failures. The absolute case failed with `'[RPT-001]' not found`; the observed stdout was ten `RPT-101` records against the outside sentinel, proving the outside file was opened. The `..` escape and the intermediate-symlink case failed the same way (`report.md:0: ERROR [RPT-101]`), proving the linked/outside target was read.
- GREEN: after adding `_contained_report_path` and updating the call site, the class passed 6 of 6; `LifecycleTests` stayed 10 of 10, so the final-symlink, absent, empty and oversized behaviours did not regress.
- Semantic assessment: each RED failure was the planned assertion on the target test, and the observed output was the security defect itself (the outside document was read and validated), not a fixture or loader fault.

## Task Commits

Each task landed as one atomic commit, as the plan's success criteria require:

1. **Task 1: Contain report.path before any read** - `8b945e3` (fix, tracer)
2. **Task 2: Pin the hostile-document contract end to end and document the tightened rule** - `75eaebd` (test)

**Plan metadata:** committed separately by the final metadata commit (this file).

## Files Created/Modified

- `scripts/check_report.py` - `import stat`; `_contained_report_path`; the containment call site in `_validate_directory`; the module docstring now names the `report.path` containment rule.
- `scripts/tests/test_report.py` - the `report_path` keyword on `homework_yaml`; `_outside_sentinel` on `FixtureBase`; `ReportPathContainmentTests`; `HostileDocumentContractTests`.
- `scripts/report/vocabulary.py` - the tightened `RPT-001` summary and remediation.
- `docs/standards/report.md` - the matching `RPT-001` row.

## Verification Results

| Check | Result |
|-------|--------|
| `python3 -m unittest scripts.tests.test_report.ReportPathContainmentTests -v` | 6 tests, OK |
| `python3 -m unittest scripts.tests.test_report.LifecycleTests -v` | 10 tests, OK |
| `python3 -m unittest scripts.tests.test_report.HostileDocumentContractTests -v` | 4 tests, OK |
| `python3 -m unittest scripts.tests.test_report.RuleRegistryTests -v` | 8 tests, OK |
| `python3 -m unittest discover scripts/tests` | 598 tests, OK (1 pre-existing environmental skip) |
| `uv run scripts/check_report.py` | `PASS: report contract satisfied` |
| `uv run scripts/check_metadata.py` | `PASS: metadata contract satisfied` |
| `pre-commit run --files <four changed files>` | all hooks Passed |

## Decisions Made

- The helper lives in `scripts/check_report.py`: it is the only module that performs file I/O, while `scripts/report/contract.py` must stay free of filesystem calls (D-02).
- Rejecting every `..` component is stricter than lexical normalization on purpose: a `..` after a symlinked component can escape while the normalized string still looks contained.
- Only the parent components are walked and realpath-checked, so the shipped final-component `RPT-002` classification is not weakened or reclassified.
- The refusal is attached to `homework.yaml` rather than the declared path, so no absolute or escaping path is echoed into a record (IN-02).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Accepted-path fixture adapted its traceability token**
- **Found during:** Task 1, writing the nested-relative acceptance case
- **Issue:** The compliant report's traceability row names `` `report.md` `` as a design artifact. With `report.path: docs/report.md`, `RPT-307` would demand a root-level `report.md` that contradicts the declared nested path, so the planned `assert_accepted` could not pass.
- **Fix:** The fixture replaces the traceability token with `` `docs/report.md` ``, which is the honest artifact for the declared path; no checker rule changed.
- **Files modified:** `scripts/tests/test_report.py`
- **Commit:** `8b945e3`

### Minor construction details (not behaviour deviations)

- `_outside_sentinel` lives on `FixtureBase` rather than `ReportPathContainmentTests`, so the contract-level class can reuse it without a second copy.
- Added `test_absent_document_is_still_rpt_002` alongside the final-symlink case to cover the plan's behaviour bullet that an absent document stays `RPT-002` (the shipped `LifecycleTests` case still covers it too).
- RED and GREEN landed in the task's single atomic commit, per the plan's success criterion "each task lands as one atomic commit"; the RED evidence is recorded above.

## Issues Encountered

- The worktree shell wrapper refused compound `git` invocations and `git status`; every git step ran as a separate plain `/usr/bin/git` command from the worktree root. No `--no-verify` was used and every hook ran.

## Known Stubs

None. No placeholder values, empty data flows or skipped assertions were introduced.

## Threat Flags

None beyond the plan's register. The change reduces attack surface (T-10-30 and T-10-31 mitigated) and introduces no new network, auth or filesystem surface; `scripts/report/contract.py` remains filesystem-free.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- G-10-1's CR-03 is closed with regression tests at the checker and contract levels.
- The full hostile-document proof (deep metadata, deep diagram, escaping path) now asserts exit code, JSON shape, traceback absence and determinism together.

---

## Self-Check

- Created files: none expected; all four modified files exist and are committed.
- Commits present on HEAD: `8b945e3` and `75eaebd` (measured: 2 commits between `042d5bd` and HEAD).

## Self-Check: PASSED

---

*Phase: 10-report-and-evidence-system*
*Completed: 2026-10-27*

---
phase: 04-metadata-contract-and-scaffolding
plan: 08
subsystem: infra
tags: [python, scaffolding, symlink, security, filesystem, path-containment, unittest]

requires:
  - phase: 04-metadata-contract-and-scaffolding
    provides: "plan-then-write scaffold (04-01, 04-04) and the component-level lstat walk (04-06)"
provides:
  - "exit-2 refusal of a symlink, a non-directory or an escaping base at homeworks/ itself"
  - "resolved-base equality proof (base.resolve() == <root>/homeworks) before any plan output"
  - "lexical containing-directory derivation that keeps the id-equals-directory rule under a symlinked ancestor"
  - "two regression tests pinning both verifier reproductions"
affects: [phase-05-generated-views, phase-08-ci, homework-scaffolding, metadata-checker]

actuals:
  tokens: 1882
  tasks: 2
  commits: 4
  plan_head_before: 69339054d56fa93bb752212781bb10c1526c7c55
  plan_head_after: d65619f26ce8ff45de95192d1b036f9bde844ddf

tech-stack:
  added: []
  patterns:
    - "Inspect the repository-root-level base with os.lstat before the per-component walk, and require its resolved form to equal the intended path."
    - "Derive identity-bearing directory names from os.path.abspath parts, never from resolve(), so a symlinked ancestor cannot erase the comparison input."
    - "RED-first regression tests recorded against the unmodified code before each fix."

key-files:
  created: []
  modified:
    - scripts/new_homework
    - scripts/metadata/contract.py
    - scripts/tests/test_new_homework.py
    - scripts/tests/test_homework_metadata.py

key-decisions:
  - "The homeworks base is inspected inside _contained_target, which main calls before _build_plan and _emit, so the refusal happens before any plan record and before the first mkdir."
  - "A symlink at homeworks/ is a usage/environment error (exit 2) regardless of its target; a non-directory is the same, and a base whose resolve() differs from <root>/homeworks is refused as an escaping base."
  - "The containment proof compares the base's resolved form rather than resolving the candidate, so the proof is no longer circular once the base is known not to be a link."
  - "_homework_directory derives parts from os.path.abspath, which normalizes . and .. without following symlinks; no resolve() or realpath() remains in that helper."

patterns-established:
  - "Base-first containment: lstat the root-level base, then walk components, then prove the resolved base equals the intended path."
  - "Lexical identity derivation for path-to-name comparisons that must survive symlinked ancestors."

requirements-completed: [FOUND-01, META-01, META-04]

coverage:
  - id: D1
    description: "A symlink at homeworks/ itself is refused at exit 2 with empty stdout for both --dry-run and a real run; the link stays intact and its destination receives zero files"
    requirement: META-04
    verification:
      - kind: unit
        ref: "scripts/tests/test_new_homework.py#ConflictTests.test_homeworks_base_symlink_exits_2"
        status: pass
    human_judgment: false
  - id: D2
    description: "A non-directory or resolving-away homeworks base is refused before the plan, and every 04-06 refusal beneath homeworks/<id> is unchanged"
    requirement: FOUND-01
    verification:
      - kind: unit
        ref: "scripts/tests/test_new_homework.py#ConflictTests (target-directory, intermediate-symlink, regular-file, final-file cases)"
        status: pass
      - kind: unit
        ref: "python3 -m unittest scripts.tests.test_new_homework -v (27 tests)"
        status: pass
    human_judgment: false
  - id: D3
    description: "A homework.yaml id that differs from its containing directory is an ERROR record at exit 1 even when homeworks/ is a symlink outside the root"
    requirement: META-01
    verification:
      - kind: unit
        ref: "scripts/tests/test_homework_metadata.py#IdentityTests.test_id_mismatch_survives_a_symlinked_homeworks_base"
        status: pass
    human_judgment: false
  - id: D4
    description: "Normal-tree identity, payload, Cyrillic, sentinel and allowance behaviour, plus the scaffold's rendered-id check, are unchanged"
    requirement: META-01
    verification:
      - kind: unit
        ref: "scripts/tests/test_homework_metadata.py (57 tests)"
        status: pass
      - kind: unit
        ref: "scripts/tests/test_new_homework.py#ErrorTests.test_mismatched_rendered_id_is_error"
        status: pass
    human_judgment: false

duration: 10 min
completed: 2026-10-24
status: complete
---

# Phase 4 Plan 8: Symlinked `homeworks` Base Containment Summary

**The scaffold now refuses a symlinked, non-directory or escaping `homeworks` base at exit 2 before any plan output, and the checker derives containing directories lexically so the id-equals-directory rule survives a symlinked ancestor.**

## Performance

- **Duration:** 10 min
- **Started:** 2026-10-24T21:57:00Z
- **Completed:** 2026-10-24T22:06:55Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments

- `_contained_target` now `lstat`s the `homeworks` base itself before computing the target: a symlink, a non-directory, or a base whose `resolve()` is not `<root>/homeworks` is a `CheckError` rendered as `ERROR:` on stderr with exit 2 and empty stdout. The refusal runs in `main` before `_build_plan` and `_emit`, so no CREATE record can precede it and no write can be redirected outside the repository root.
- `_homework_directory` no longer resolves paths. It derives the containing directory from `os.path.abspath(...).parts`, which normalizes `.` and `..` without following symlinks, so a candidate reached through a symlinked `homeworks/` still reports `homeworks/<dir>/homework.yaml` and the id-equals-directory rule fires instead of silently returning `None`.
- Two regression tests pin both verifier reproductions: the symlinked base for `--dry-run` and a real run, and the id mismatch under a symlinked ancestor. Both were recorded failing against the unmodified code first.
- Every earlier behaviour still holds: CREATE/UNCHANGED idempotency, `--dry-run` parity, JSON record shape, both golden trees, the 04-06 target/intermediate/final symlink refusals, and the full metadata matrix.

## Task Commits

Each task was committed atomically, RED before GREEN:

1. **Task 1 RED: pin the symlinked `homeworks` base refusal** - `04f10e6` (test)
2. **Task 1 GREEN: refuse a symlinked `homeworks` base** - `45e8176` (fix)
3. **Task 2 RED: pin the id-match invariant under a symlinked ancestor** - `c7b7953` (test)
4. **Task 2 GREEN: derive the containing directory lexically** - `d65619f` (fix)

**Plan metadata:** `docs(04-08): complete symlinked homeworks base containment plan` (see final commit)

_Note: the two RED commits carry the failing regression tests only; each GREEN commit carries its fix._

## RED Evidence (recorded before each fix)

| Test | Symptom on the unmodified code |
|------|--------------------------------|
| `test_homeworks_base_symlink_exits_2` (`dry-run`) | Exit 0, eight `CREATE` records on stdout; the refusal fragment was absent. |
| `test_homeworks_base_symlink_exits_2` (`real`) | Exit 0, eight `CREATE` records; the run wrote through the link into the outside directory. |
| `test_id_mismatch_survives_a_symlinked_homeworks_base` | Exit 0 with `PASS: metadata contract satisfied`; no `containing directory` ERROR, because `_homework_directory` resolved the candidate away from the root and returned `None`. |

After the fixes the same tests pass, `scripts.tests.test_new_homework` reports 27 tests OK, and `scripts.tests.test_homework_metadata` reports 57 tests OK.

## Files Created/Modified

- `scripts/new_homework` - base `lstat` plus resolved-base equality inside `_contained_target`; new exact reasons `homeworks is a symlink; refusing to follow it`, `homeworks exists and is not a directory`, `homeworks base resolves outside the repository root; refusing to scaffold`, `cannot inspect homeworks: <error>`; exit-2 docstring paragraph updated. No new function, CLI flag, import or placeholder.
- `scripts/metadata/contract.py` - `import os`; lexical `_homework_directory(root, path)` using `os.path.abspath(...).parts`, with no `resolve()` or `realpath()` call and an updated docstring.
- `scripts/tests/test_new_homework.py` - `ConflictTests.test_homeworks_base_symlink_exits_2`.
- `scripts/tests/test_homework_metadata.py` - `IdentityTests.test_id_mismatch_survives_a_symlinked_homeworks_base`.

## Decisions Made

- The base refusal lives in `_contained_target` because `main` already calls it before `_build_plan` and `_emit`; this keeps the all-or-nothing ordering of D-24 without moving any other step.
- A symlinked base is refused even when it points inside the root: the contract is "never follow the base", so the message does not depend on the link target.
- The containment proof now compares `base.resolve()` against `root / "homeworks"` after the base is known not to be a link, which removes the circularity the verifier identified while retaining `resolve()` + `relative_to()` as defense in depth for the candidate.
- The identity helper uses lexical parts precisely because `resolve()` is what erased `homeworks/<dir>`; `relative_to` and `realpath` are deliberately not substituted in.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- The plan's acceptance criterion names `scripts.tests.test_new_homework.DynamicTemplateTests.test_mismatched_rendered_id_is_error`, but the test is defined in `ErrorTests`. The test was run under its real class name and passes; no code change was made for the naming discrepancy.
- The sandbox denies writes to uv's default cache (`~/.cache/uv`), so every test run used `UV_CACHE_DIR=/tmp/claude-501/uv-cache`. No repository file or configuration was changed for this.
- The repository-wide suite emitted three non-fatal `deny network-outbound` sandbox notices while still reporting `Ran 307 tests ... OK`; no test failed and no host was needed.
- `gsd_run` is unavailable in this execution environment, so state/roadmap updates are left to the orchestrator as instructed, and the commit ledger was recorded directly with `git rev-parse HEAD`.

## Threat Flags

None. The only new surface is the threat register's own T-04-26/T-04-27 mitigations; T-04-28 remains accepted debt and T-04-SC is unaffected because no dependency pin changed.

## Known Stubs

None.

## User Setup Required

None - no external service configuration required.

## Verification

| Command | Result |
|---------|--------|
| `python3 -m unittest scripts.tests.test_new_homework scripts.tests.test_homework_metadata -v` | 84 tests, OK |
| `python3 -m unittest discover -s scripts/tests -v` | 307 tests, OK (≥ 307 required) |
| `pre-commit run --all-files` | All hooks Passed; no file rewritten |

## Next Phase Readiness

- The last carried-forward Phase 4 containment gap is closed: no scaffold write can land outside `<root>/homeworks` through a symlinked base, and the identity invariant no longer depends on `Path.resolve()`.
- Both verifier reproductions are pinned by regressions, so a future change that reopens either path fails the suite rather than passing silently.
- Content idempotency (D-20), `--dry-run` parity (D-21), the JSON record shape (D-23), both golden trees, the schema and every template are unchanged.

---
*Phase: 04-metadata-contract-and-scaffolding*
*Completed: 2026-10-24*

## Self-Check: PASSED

- `scripts/new_homework` — FOUND
- `scripts/metadata/contract.py` — FOUND
- `scripts/tests/test_new_homework.py` — FOUND
- `scripts/tests/test_homework_metadata.py` — FOUND
- Commit `04f10e6` (Task 1 RED) — FOUND, ancestor of HEAD
- Commit `45e8176` (Task 1 GREEN) — FOUND, ancestor of HEAD
- Commit `c7b7953` (Task 2 RED) — FOUND, ancestor of HEAD
- Commit `d65619f` (Task 2 GREEN) — FOUND, ancestor of HEAD
- All three plan-level verification commands ran green.

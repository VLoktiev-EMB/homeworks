---
phase: 04-metadata-contract-and-scaffolding
plan: 06
subsystem: infra
tags: [python, scaffolding, symlink, security, filesystem, unittest]

# Dependency graph
requires:
  - phase: 04-metadata-contract-and-scaffolding
    provides: "plan-then-write scaffold (04-01, 04-04) and its disposable-root integration suite"
provides:
  - "component-level lstat containment walk in scripts/new_homework"
  - "exit-2 refusal of a symlink at homeworks/<id> before the plan is built"
  - "three regression tests pinning CR-01 and WR-02"
affects: [phase-05-generated-views, phase-08-ci, homework-scaffolding]

# Actuals (#2632) — chars/4 over the realized diff, measured from the plan ledger.
actuals:
  tokens: 2594
  tasks: 2
  commits: 2
  plan_head_before: 9c73a71bb628fad41610653ba4ce5b123396a68a
  plan_head_after: bf5a4cfe4806077f36fdb2b7550eb824c334bc35

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Inspect every path component with os.lstat before any exists(), is_file() or read_bytes() call."
    - "Refusal reasons name the offending repository-relative path."

key-files:
  created: []
  modified:
    - scripts/new_homework
    - scripts/tests/test_new_homework.py

key-decisions:
  - "A symlink at homeworks/<id> is a usage error (exit 2) raised before the plan is built; a symlink or non-directory below it is a CONFLICT (exit 1) that blocks every write."
  - "Containment is proven by an lstat walk over every component; resolve() plus relative_to() stays only as defense in depth, and the unresolved target is what later steps see."

patterns-established:
  - "Component walk: refuse symlinked or non-directory components without resolving the candidate path."

requirements-completed: [META-04, FOUND-01]

# Coverage metadata (#1602)
coverage:
  - id: D1
    description: "A symlink on any candidate target component, or a non-directory intermediate component, is refused without traversal and no file is written"
    requirement: META-04
    verification:
      - kind: unit
        ref: "scripts/tests/test_new_homework.py#ConflictTests.test_intermediate_directory_symlink_is_conflict_and_writes_nothing"
        status: pass
      - kind: unit
        ref: "scripts/tests/test_new_homework.py#ConflictTests.test_target_directory_symlink_exits_2"
        status: pass
      - kind: unit
        ref: "scripts/tests/test_new_homework.py#ConflictTests.test_regular_file_at_intermediate_path_is_conflict"
        status: pass
    human_judgment: false
  - id: D2
    description: "Existing scaffold contract unchanged: CREATE/UNCHANGED byte idempotency, --dry-run parity, JSON record shape, and both golden trees"
    requirement: FOUND-01
    verification:
      - kind: unit
        ref: "scripts/tests/test_new_homework.py#IdempotencyTests"
        status: pass
      - kind: unit
        ref: "scripts/tests/test_new_homework.py#DryRunTests"
        status: pass
      - kind: unit
        ref: "scripts/tests/test_new_homework.py#JsonTests"
        status: pass
      - kind: unit
        ref: "scripts/tests/test_new_homework.py#GoldenTreeTests"
        status: pass
    human_judgment: false

# Metrics
duration: 2 min
completed: 2026-10-24
status: complete
---

# Phase 4 Plan 6: Symlink Containment in the Homework Scaffold Summary

**Component-level `lstat` walk refuses symlinked and non-directory target paths, closing the write-escape path while scaffold idempotency and both golden trees stay byte-identical.**

## Performance

- **Duration:** 2 min
- **Started:** 2026-10-24T21:38:13Z
- **Completed:** 2026-10-24T21:40:54Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- `scripts/new_homework` now inspects every component from `homeworks/<id>` to the final target with `os.lstat` before any `exists()`, `is_file()` or `read_bytes()` call, so no path resolution can traverse a symlinked parent.
- An intermediate symlink is `CONFLICT` at exit 1 naming the offending path; a non-directory intermediate component is likewise `CONFLICT` at exit 1 instead of a partial write followed by exit 2 (WR-02).
- A symlink at `homeworks/<id>` is refused with exit 2 and no plan output; the link and its destination are left intact.
- Three regression tests reproduce both verifier symlink variants and the partial-write case, and all 26 tests in the module, 301 repository tests and `pre-commit run --all-files` are green.

## Task Commits

Each task was committed atomically:

1. **Task 1: Pin the three containment failures as regression tests (RED)** - `37e6b70` (test)
2. **Task 2: Refuse symlinked and non-directory target components (GREEN)** - `bf5a4cf` (fix)

**Plan metadata:** `docs(04-06): complete symlink containment plan` (see final commit)

_Note: TDD tasks may have multiple commits (test → feat → refactor)_

## Files Created/Modified

- `scripts/new_homework` - new `_component_conflict(base, relative)` helper; `_classify(base, target, data)`; `_contained_target` returns the unresolved target; `import stat`; docstring exit-code and D-20 contracts updated.
- `scripts/tests/test_new_homework.py` - three `ConflictTests` regressions for the intermediate symlink, the target-directory symlink, and the regular-file intermediate component.

## TDD Evidence (RED before GREEN)

Task 1 ran the three new tests against the unmodified scaffold and recorded the reproduced symptoms:

- `test_intermediate_directory_symlink_is_conflict_and_writes_nothing` failed with `AssertionError: 1 != 0`: the run exited 0, every record was `CREATE`, and `src/main.cpp` was written through `homeworks/1_3-fixture/src` into the outside directory.
- `test_target_directory_symlink_exits_2` failed with `AssertionError: 2 != 0`: the run printed the full JSON plan and exited 0, following the link into `homeworks/sub/1_3-fixture`.
- `test_regular_file_at_intermediate_path_is_conflict` failed with `AssertionError: 1 != 2`: the run wrote a partial project and then failed with `ERROR: write failed: [Errno 17] File exists: .../homeworks/1_3-fixture/src`.

After Task 2 the same three tests pass, and the full module reports `Ran 26 tests ... OK`.

## Decisions Made

- A symlink at `homeworks/<id>` is treated as a usage/environment error (exit 2) because the run cannot even form a target directory; a symlink or non-directory below it is a `CONFLICT` record (exit 1) because the plan is still printable and the offending path belongs in the per-path report.
- The component walk owns containment; `resolve()` plus `relative_to()` is retained only as defense in depth, and the unresolved `target` is returned so no later step can act on a link target.
- Refusal strings keep the exact wording required by the plan and the verifier fragments: `target is a symlink; refusing to follow or overwrite it`, `intermediate path homeworks/<id>/<part> is a symlink; refusing to follow it`, `intermediate path homeworks/<id>/<part> exists and is not a directory`, and `target homeworks/<id> is a symlink; refusing to follow it`.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- The sandbox denies writes to the default uv cache (`~/.cache/uv`), so every `uv run` inside the test suite failed with `Could not acquire lock` until the verification commands were run with `UV_CACHE_DIR` pointed at the session temp directory. This is an execution-environment constraint, not a code or plan change; no test or scaffold file was altered for it.

## User Setup Required

None - no external service configuration required.

## Threat Flags

None. No new endpoint, auth path, file-access pattern or schema change was introduced beyond the threat register's T-04-22/T-04-23 mitigations; T-04-SC is unaffected because no dependency pin changed.

## Next Phase Readiness

- CR-01 and WR-02 are closed: no scaffold write can land outside `homeworks/` or through a symlinked directory, and every refusal leaves the tree untouched.
- The remaining Phase 4 verification gaps (WR-01 allowlist suppression, CR-02 composed YAML key) are owned by sibling gap-closure plans, not this one.
- Content idempotency (`D-20`), `--dry-run` parity (`D-21`), the JSON record shape (`D-23`) and both golden trees are unchanged.

---

## Self-Check

## Self-Check: PASSED

- `scripts/new_homework` — FOUND
- `scripts/tests/test_new_homework.py` — FOUND
- `.planning/phases/04-metadata-contract-and-scaffolding/04-06-SUMMARY.md` — FOUND
- Commit `37e6b70` (RED tests) — FOUND, ancestor of HEAD
- Commit `bf5a4cf` (hardening) — FOUND, ancestor of HEAD

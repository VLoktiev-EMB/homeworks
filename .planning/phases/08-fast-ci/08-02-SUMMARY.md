---
phase: 08-fast-ci
plan: 02
subsystem: infra
tags: [github-actions, nightly, schedule, widen-all, gitleaks, platformio, ci-topology]

# Dependency graph
requires:
  - phase: 08-fast-ci
    plan: 01
    provides: ci.yml with the pinned action SHAs, the meta/changes/build/gate graph and the
      pinned gitleaks 8.30.1 install block
  - phase: 05-generated-views-and-documentation-site
    provides: scripts/affected.py and its tested {build, simulate} contract with the WIDEN_ALL table
provides:
  - .github/workflows/nightly.yml with the changes, build and secrets jobs
  - the full project matrix from feeding platformio.shared.ini to affected.py --paths-from
  - the post-merge full-history gitleaks scan that security.yml used to own
  - retirement of .github/workflows/homework.yml and .github/workflows/security.yml
affects: [08-fast-ci plans 03-04, AGENTS.md CI sections, the workflow-count contract]

# Actuals (#2632)
actuals:
  tokens: 4134
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "Scheduled full matrix: feed the mapper's own WIDEN_ALL path table to affected.py instead of adding an --all flag"
    - "Non-cancelling concurrency group for a scheduled workflow: overlap is forbidden, cancellation is not used"
    - "One job id per responsibility; the display name preserves the retired workflow's identity"

key-files:
  created:
    - .github/workflows/nightly.yml
  modified:
    - scripts/tests/test_ci_workflows.py
  deleted:
    - .github/workflows/homework.yml
    - .github/workflows/security.yml

key-decisions:
  - "The nightly matrix is the mapper's own WIDEN_ALL result for platformio.shared.ini, not a curated project list or a new --all flag, so a project the mapper misses fails the drift test rather than silently leaving the nightly."
  - "The job id is `secrets` while its display name stays `gitleaks (full history)`, so the post-merge scan keeps the identity the retired security.yml job reported."
  - "The workflow-count test now asserts two files and the job-id extractor scans only the top-level `jobs:` block, so a key such as `schedule:` can never be read as a job."

patterns-established:
  - "A scheduled workflow reuses the pull-request cache key verbatim, so the default branch seeds the cache every pull request restores"
  - "A retirement commit lands only in the task that adds the replacement check, so no check is uncovered between commits"

requirements-completed: [TOOL-06]

coverage:
  - id: D1
    description: "nightly.yml runs the widen-all changes job and the 90-minute build matrix (native test vs target build) with the empty-matrix guard"
    requirement: TOOL-06
    verification:
      - kind: unit
        ref: "scripts/tests/test_ci_workflows.py#WorkflowTextTests.test_nightly_computes_the_full_matrix"
        status: pass
      - kind: unit
        ref: "scripts/tests/test_ci_workflows.py#WorkflowTextTests.test_nightly_declares_the_full_matrix_job_set"
        status: pass
      - kind: other
        ref: "printf 'platformio.shared.ini\\n' | uv run scripts/affected.py --paths-from /dev/stdin (every project with platformio.ini, plus tests)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The repository has exactly two workflows: ci.yml and nightly.yml"
    requirement: TOOL-06
    verification:
      - kind: unit
        ref: "scripts/tests/test_ci_workflows.py#WorkflowTriggerKeyTests.test_every_workflow_declares_a_textual_trigger_key (asserts a count of two)"
        status: pass
      - kind: other
        ref: "git ls-files .github/workflows -> ci.yml, nightly.yml"
        status: pass
    human_judgment: false
  - id: D3
    description: "The nightly secrets job restores the post-merge full-history gitleaks scan with fetch-depth: 0 and the pinned 8.30.1 binary"
    requirement: TOOL-06
    verification:
      - kind: unit
        ref: "scripts/tests/test_ci_workflows.py#WorkflowTextTests.test_nightly_carries_the_full_history_scan"
        status: pass
    human_judgment: false
  - id: D4
    description: "nightly.yml declares no simulation job, no Wokwi credential and no simulation marker outside comments"
    requirement: TOOL-06
    verification:
      - kind: unit
        ref: "scripts/tests/test_ci_workflows.py#WorkflowTextTests.test_nightly_declares_no_simulation"
        status: pass
    human_judgment: false
  - id: D5
    description: "A scheduled nightly run seeds the default-branch toolchain cache and stays within the 90-minute per-entry budget"
    verification: []
    human_judgment: true
    rationale: "Cache scoping and cold/warm durations can only be observed in a live scheduled run; the key equality with the pull-request build is a text contract, not a runtime measurement (F-15)."

# Metrics
duration: 2min
completed: 2026-10-26
status: complete
plan_head_before: c184efca4b17d755b35a3e803c3a66473284d18e
plan_head_after: 91739a062257cb7c6f017997b3eda06d403c7ae0
---

# Phase 8 Plan 2: Nightly full matrix replaces the single-project build Summary

**A daily run builds and native-tests every project from the mapper's widen-all set, and the
retired post-merge gitleaks scan continues inside the same workflow**

## Performance

- **Duration:** 2 min
- **Started:** 2026-10-26T18:55:38Z
- **Completed:** 2026-10-26T18:58:04Z
- **Tasks:** 2
- **Files modified:** 4 (one created, one modified, two deleted)

## Accomplishments

- Created `.github/workflows/nightly.yml` with `changes`, `build` and `secrets`; `changes`
  writes `platformio.shared.ini` to `$RUNNER_TEMP/all-paths.txt` and feeds it to
  `uv run scripts/affected.py --paths-from`, so the mapper's own `WIDEN_ALL` table produces
  the full project set without a new flag or a curated list.
- The `build` job runs each matrix entry under a 90-minute per-entry budget with
  `fail-fast: false`, `max-parallel: 4`, the pin-derived cache key shared with the
  pull-request build, the empty-string-then-`[]` job guard and the `pio test -e native`
  versus `pio run -e <env>` split.
- Added the `secrets` job (`gitleaks (full history)`, `fetch-depth: 0`, pinned 8.30.1 with the
  committed SHA-256) and retired `security.yml` in the same commit, so the post-merge scan
  never disappears between commits.
- Retired `homework.yml`; its build and native-test commands now live in the matrix job.
- Extended `scripts/tests/test_ci_workflows.py`: the module now asserts the nightly widen-all
  invocation, the non-cancelling concurrency group, the `{changes, build, secrets}` job set,
  the full-history scan and the absence of all three simulation markers, and the workflow
  count drops from three to two (module 17 -> 22 tests, suite 313 -> 316).

## Task Commits

Each task was committed atomically:

1. **Task 1: Nightly full matrix replaces the single-project build** - `ff3c0cf` (feat)
2. **Task 2: Retire `security.yml` once nightly owns the post-merge scan** - `91739a0` (feat)

**Plan metadata:** committed separately below (docs).

_Note: no TDD plan, so no RED/GREEN/REFACTOR commits._

## Files Created/Modified

- `.github/workflows/nightly.yml` — the scheduled full-matrix run: `changes` (widen-all),
  `build` (per-entry 90-minute budget, pin-derived cache, native/target split) and `secrets`
  (full-history gitleaks).
- `.github/workflows/homework.yml` — deleted; its two commands are matrix entries now.
- `.github/workflows/security.yml` — deleted; its scan is the nightly `secrets` job.
- `scripts/tests/test_ci_workflows.py` — `NIGHTLY` constant, a `job_ids()` extractor, five new
  nightly contracts, the count going three -> two and the renamed
  `test_every_workflow_declares_a_textual_trigger_key`.

## Decisions Made

- The nightly matrix is the mapper's `WIDEN_ALL` result for `platformio.shared.ini`, not a
  curated project list and not a new `--all` flag. A project the mapper misses fails the
  widen-all assertion, so the mapper stays the single owner of the full set.
- The job id is `secrets` and the display name stays `gitleaks (full history)`, preserving the
  identity the retired `security.yml` job reported while keeping the id meaningful in
  `needs:`.
- The `job_ids()` helper scans only the block after the top-level `jobs:` key and stops at
  the first column-zero line, so `schedule:` or `workflow_dispatch:` can never be read as a
  job id.
- The `secrets` job sits in `nightly.yml` rather than a `push: main` trigger, because a push
  trigger would repeat the whole matrix on every merge and leave D-1's one-workflow-per-event
  topology intact.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- `gsd_run` is not available in this worktree, so the per-task and metadata commits used
  `/usr/bin/git` directly with the same hook surface; all 13 pre-commit hooks passed on both
  commits and on `pre-commit run --all-files --show-diff-on-failure`.
- The plan's tracked-workflow-set `<automated>` check embeds `git` inside a Python one-liner,
  which this harness's worktree guard refuses. The equivalent check ran as a plain
  `git ls-files .github/workflows` (exactly `ci.yml` and `nightly.yml`) plus the unit test that
  asserts a count of two.
- `yamllint` is not installed as a system binary in this worktree; the pinned pre-commit hook
  ran it over both new and existing YAML and passed.
- The first test run after writing `nightly.yml` failed the workflow-count assertion with four
  files, as expected before `homework.yml` is removed in the same task; the removal brought the
  count back to three for Task 1 and to two in Task 2.

## Known Stubs

None.

## Threat Flags

None — the `secrets` job is the T-8-07 mitigation already recorded in the plan's threat
model (redacted scan, `contents: read` only), and the build job follows T-8-08/T-8-09.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The workflow directory now holds exactly the pull-request gate and the nightly run; later
  plans must extend `ci.yml`'s `gate.needs` in the same commit that adds a PR job.
- A live scheduled run is still needed to measure the cold/warm cache behaviour and to confirm
  the 90-minute per-entry budget (F-15); it cannot be proven from the local tree.
- `TOOL-06`'s nightly half is satisfied textually; the live-run deliverable stays
  human-judged until the first scheduled run reports green.

## Self-Check: PASSED

- `.github/workflows/nightly.yml` exists; `.github/workflows/homework.yml` and
  `.github/workflows/security.yml` are absent from the working tree and from `git ls-files`.
- Commits `ff3c0cf` and `91739a0` are ancestors of `HEAD` (`91739a0`).
- `python3 -m unittest scripts.tests.test_ci_workflows -v`: 22 tests, `OK`.
- `python3 -m unittest discover scripts/tests`: 316 tests, `OK` (1 skipped).
- `pre-commit run --all-files --show-diff-on-failure`: all 13 hooks passed.
- Widen-all verification returned every project with a `platformio.ini`, plus `tests`.

---
*Phase: 08-fast-ci*
*Completed: 2026-10-26*

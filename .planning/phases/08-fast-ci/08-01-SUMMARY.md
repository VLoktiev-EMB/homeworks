---
phase: 08-fast-ci
plan: 01
subsystem: infra
tags: [github-actions, ci, changed-only-build, fan-in-gate, gitleaks, wokwi-cli, pre-commit]

# Dependency graph
requires:
  - phase: 05-generated-views-and-documentation-site
    provides: scripts/affected.py and its tested {build, simulate} JSON contract with fail-safe widening
  - phase: 06-developer-experience-and-quality-layering
    provides: the pinned pre-commit hook surface that the meta job now runs whole
  - phase: 04.2-tracer-homework-1-3
    provides: the single-project workflow, its pinned action SHAs and the measured 1m38s baseline
provides:
  - .github/workflows/ci.yml with the meta, changes, build and gate job graph
  - the literal `gate` job that becomes the ruleset's single required status check
  - a meta job that runs the full-history secret scan before any contributor hook, then the whole hook surface and the diagram lint
  - retirement of .github/workflows/generated-views.yml into the gen-views-check hook
affects: [08-fast-ci plans 02-04, AGENTS.md CI sections, the ruleset human checkpoint]

# Actuals (#2632)
actuals:
  tokens: 5400
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "Fan-in gate: one job depends on every PR job and allows only `success` and `skipped`"
    - "Job-level empty-matrix guard that rejects the empty string before the literal `[]`"
    - "Untrusted values enter a `run:` body only through `env:` and are quoted in the shell"

key-files:
  created:
    - .github/workflows/ci.yml
  modified:
    - scripts/tests/test_ci_workflows.py
  deleted:
    - .github/workflows/generated-views.yml

key-decisions:
  - "The gate's jq filter is split across YAML lines without a backslash; the backslash continuation copied from RESEARCH Pattern 1 is invalid jq and would fail the required check on every run."
  - "The scan-before-hooks assertion compares `rindex` positions, because the ordering comment names `pre-commit install-hooks` before the step itself exists."
  - "The title step sits between checkout and setup-python, and the history scan is inserted between checkout and the title step, so no contributor hook can run before the scan."

patterns-established:
  - "One workflow owns the whole pull-request decision; matrix jobs are never a required check"
  - "Every CI text contract names the exact command string, so a rename or a dropped flag fails the suite"

requirements-completed: [TOOL-05, TOOL-06]

coverage:
  - id: D1
    description: "ci.yml carries meta, changes, build and the literal `gate`, with the labeled trigger, the empty-matrix guard and the native-versus-target command split"
    requirement: TOOL-06
    verification:
      - kind: unit
        ref: "scripts/tests/test_ci_workflows.py#WorkflowTextTests"
        status: pass
    human_judgment: false
  - id: D2
    description: "generated-views.yml is retired and the drift gate reads the gen-views-check hook surface"
    requirement: TOOL-05
    verification:
      - kind: unit
        ref: "scripts/tests/test_ci_workflows.py#test_drift_gate_lives_in_the_hook_surface"
        status: pass
    human_judgment: false
  - id: D3
    description: "meta scans the full history before any contributor hook runs and lints every committed diagram with the pinned tools"
    requirement: TOOL-05
    verification:
      - kind: unit
        ref: "scripts/tests/test_ci_workflows.py#MetaJobSurfaceTests"
        status: pass
    human_judgment: false
  - id: D4
    description: "A live pull-request run reports a green `gate` and the ruleset adopts it as the required check"
    requirement: TOOL-06
    verification: []
    human_judgment: true
    rationale: "A real GitHub Actions run and the GitHub-UI ruleset change cannot be proven from the local tree; the check becomes selectable only after it has passed once."

# Metrics
duration: 2min
completed: 2026-10-26
status: complete
plan_head_before: b606c963b4de57fd609cc9de3909ab5ea8d44aea
plan_head_after: 472ae96441e628247dad05852111ede464add22c
---

# Phase 8 Plan 1: Fast CI changed-only pull-request gate Summary

**One `ci.yml` whose changed-only `build` matrix and full-history `meta` scan fan into the literal `gate` required check**

## Performance

- **Duration:** 2 min
- **Started:** 2026-10-26T18:51:01Z
- **Completed:** 2026-10-26T18:53:25Z
- **Tasks:** 2
- **Files modified:** 3 (one created, one modified, one deleted)

## Accomplishments

- Created `.github/workflows/ci.yml` with `meta`, `changes`, `build` and `gate`; `changes` maps
  `origin/$BASE` through `scripts/affected.py`, `build` runs `pio test -e native` for a native
  entry and `pio run` otherwise, and `gate` allows only `success` and `skipped`.
- Retired `generated-views.yml`; the drift contract now lives in the `gen-views-check`
  pre-commit hook, and `meta` runs `pre-commit run --all-files --show-diff-on-failure`.
- Moved the full-history gitleaks 8.30.1 scan and the `wokwi-cli` 0.28.1 diagram lint into
  `meta`, with the scan ahead of `pre-commit install-hooks` and both binaries
  checksum-verified before execution.
- Extended `scripts/tests/test_ci_workflows.py` with the title, read-only, drift-hook,
  ordering and pinned-version contracts; 17 tests in the module, 311 in the suite.

## Task Commits

Each task was committed atomically:

1. **Task 1: End-to-end changed-only PR gate** — `20a1e4e` (feat)
2. **Task 2: Move the full-history secret scan and the diagram lint into `meta`** — `472ae96` (feat)

**Plan metadata:** committed separately below (docs).

_Note: no TDD plan, so no RED/GREEN/REFACTOR commits._

## Files Created/Modified

- `.github/workflows/ci.yml` — the single pull-request workflow: fast `meta`, `changes`, the
  changed-only `build` matrix and the fan-in `gate`.
- `scripts/tests/test_ci_workflows.py` — the workflow text contracts; `GENERATED_VIEWS` becomes
  `CI` plus `PRECOMMIT`, and the new `MetaJobSurfaceTests` pin the scan ordering and tools.
- `.github/workflows/generated-views.yml` — deleted; its command runs inside `meta` through
  the hook surface.

## Decisions Made

- The gate's jq filter is written across YAML lines without a backslash continuation. The
  verbatim RESEARCH Pattern 1 form (`... "skipped") \` + newline) is a jq syntax error and
  would have failed the required check on every pull request; verified locally that the
  multi-line program compiles and prints the offenders.
- The scan-before-hooks assertion uses `rindex`, not `index`: the step's own ordering comment
  names `pre-commit install-hooks` first, so a first-occurrence comparison measured the
  comment, not the executed command. The test now says so in a comment.
- `meta` keeps both the cache restore and `pre-commit install-hooks` ahead of the hook run,
  and the gitleaks/wokwi installs after it. The scan, however, runs immediately after
  checkout — the ordering the trust boundary actually needs.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] The prescribed jq filter is invalid jq**
- **Found during:** Task 1 (end-to-end changed-only PR gate)
- **Issue:** RESEARCH Pattern 1, which the plan directs the `gate` step to follow, splits the
  jq program with a trailing backslash. jq has no line-continuation escape outside a string,
  so the run would exit 3 with `syntax error, unexpected INVALID_CHARACTER` on every pull
  request, leaving `gate` permanently red.
- **Fix:** Split the program across YAML lines without the backslash; newlines are ordinary
  jq whitespace. Verified by feeding a `success`/`failure` payload through the exact program
  and by the workflow suite.
- **Files modified:** `.github/workflows/ci.yml`
- **Verification:** `jq` printed `build=failure` for a failing dependency; all 17 module tests
  pass.
- **Committed in:** `20a1e4e` (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** The only deviation is a correctness fix to a prescribed snippet; the job
graph, triggers, permissions and guards are exactly as planned. No scope creep.

## Issues Encountered

- The first version of `test_meta_scans_history_before_running_hooks` compared first-occurrence
  indices and failed (`2157 not less than 660`) because the new ordering comment mentions
  `pre-commit install-hooks`. Reworked to `rindex` and documented the reason in the test.
- `wokwi-cli lint --offline` exits 0 with one informational `unsupported-part` note for
  `board-esp32-s3-devkitc-1`, matching the Phase 7 evidence row.
- The `gh`/`git` shorthand is wrapped by the local output-condensing tool and is refused in
  this worktree; commits used `/usr/bin/git` directly with the same hook surface.

## Known Stubs

None.

## User Setup Required

None at this stage. The ruleset change (adding `gate` as the required status check) is the
phase-level human checkpoint after the first live green run, not a setup step for this plan.

## Next Phase Readiness

- `ci.yml` is ready for Plan 2 to retire `homework.yml` and `security.yml`, at which point the
  workflow count assertion drops from three to two.
- `gate.needs` intentionally names only `changes`, `meta` and `build`; later plans must extend
  the list in the same commit that adds a job.
- The live-run and ruleset adoption deliverable (D4) stays human-judged until a real pull
  request reports `gate`.

## Self-Check: PASSED

- `.github/workflows/ci.yml` exists; `.github/workflows/generated-views.yml` is absent from
  the working tree and from `git ls-files`.
- Commits `20a1e4e` and `472ae96` are ancestors of `HEAD` (`472ae96`).
- `python3 -m unittest discover scripts/tests`: 311 tests, `OK` (1 skipped).
- `pre-commit run --all-files --show-diff-on-failure`: all 13 hooks passed.

---
*Phase: 08-fast-ci*
*Completed: 2026-10-26*

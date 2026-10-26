---
phase: 08-fast-ci
plan: 03
subsystem: infra
tags: [github-actions, ci, python-suite, static-analysis, clang-tidy, simulation, artifact-upload]

# Dependency graph
requires:
  - phase: 08-fast-ci
    plan: 01
    provides: ci.yml with the meta/changes/build/gate graph, the pinned action SHAs and the meta hook surface
  - phase: 08-fast-ci
    plan: 02
    provides: nightly.yml as the only other workflow, and the retirement of homework.yml and security.yml
  - phase: 05-generated-views-and-documentation-site
    provides: scripts/affected.py and its tested {build, simulate} JSON contract with fail-safe widening
  - phase: 07-simulation-spike
    provides: the measured wokwi-cli 0.28.1 command, the exit-code mapping and the absolute --serial-log-file evidence
provides:
  - python-tests and static-analysis jobs that feed the single gate
  - the opt-in simulate job with an event-first fork guard, a step-level token check and 7-day evidence artifacts
  - CiWorkflowContractTests, which derives gate.needs from the file and pins the whole aggregation contract
affects: [08-fast-ci plan 04, AGENTS.md CI sections, the ruleset human checkpoint]

# Actuals (#2632)
actuals:
  tokens: 4980
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "A pull-request job that runs the pre-push hook stage explicitly, after generating the compile database"
    - "An artifact name derived in shell and exported through $GITHUB_ENV, so no expression interpolation reaches the upload"
    - "A metered job that records its evidence before returning the CLI exit status"

key-files:
  created: []
  modified:
    - .github/workflows/ci.yml
    - scripts/tests/test_ci_workflows.py

key-decisions:
  - "The simulate job's guard leads with `!cancelled()` and then `github.event_name == 'pull_request'`, so a workflow_dispatch run never dereferences a null pull-request context."
  - "The token is tested in a step (`if: env.WOKWI_CLI_TOKEN == ''`), never in the job-level `if`, because the `secrets` context is unavailable there."
  - "The artifact name is derived from `tr -c 'A-Za-z0-9._-' '-'` under LC_ALL=C and exported via $GITHUB_ENV; upload-artifact rejects a slash and every project id carries one."
  - "static-analysis restores the same `~/.cache/pre-commit` entry as meta, under the same key and with no restore-keys, so the pre-push hook environments are restored rather than rebuilt."
  - "The scenario step runs under `set -uo pipefail` without `-e`, so quota.json and both logs are written before the captured exit status is returned."
  - "`test_gate_runs_under_not_cancelled` drops comment-only lines before asserting `always()` is absent: the D-2 comment above `gate` names `always()` to explain why it is not used, so a raw-text assertion would test the explanation instead of the YAML."

patterns-established:
  - "One job per responsibility: python-tests proves the suite, static-analysis proves the host translation units, and gate alone decides the merge"
  - "Every aggregation test derives its expected set from the file rather than hard-coding it, so a new job that is missing from `needs` fails locally"

requirements-completed: [TOOL-05, TOOL-06, SIM-04]

# Coverage metadata (#1602)
coverage:
  - id: D1
    description: "python-tests installs uv 0.13.5 and runs the stdlib suite on every pull request, closing the WR-13 gap"
    requirement: TOOL-05
    verification:
      - kind: unit
        ref: "scripts/tests/test_ci_workflows.py#WorkflowTextTests.test_python_suite_runs_in_ci"
        status: pass
    human_judgment: false
  - id: D2
    description: "static-analysis restores the pre-commit cache, generates the native compile database and runs the pre-push clang-tidy stage over lib/common/src and lib/host/src"
    requirement: TOOL-06
    verification:
      - kind: unit
        ref: "scripts/tests/test_ci_workflows.py#WorkflowTextTests.test_static_analysis_runs_the_pre_push_stage"
        status: pass
      - kind: unit
        ref: "scripts/tests/test_ci_workflows.py#WorkflowTextTests.test_static_analysis_restores_the_pre_commit_cache"
        status: pass
    human_judgment: false
  - id: D3
    description: "simulate runs only for a labelled, same-repository, policy-clean pull request; it builds the firmware, runs the pinned wokwi-cli with a 15-second timeout and uploads serial.log, stdout.log and quota.json under a slash-free derived name"
    requirement: SIM-04
    verification:
      - kind: unit
        ref: "scripts/tests/test_ci_workflows.py#WorkflowTextTests.test_simulation_is_guarded_and_uploads_evidence"
        status: pass
      - kind: unit
        ref: "scripts/tests/test_ci_workflows.py#WorkflowTextTests.test_simulation_pins_the_cli_and_maps_exit_codes"
        status: pass
    human_judgment: false
  - id: D4
    description: "The gate contract is derived from the file: gate.needs covers every other job, only success and skipped pass, gate runs under !cancelled(), and no workflow writes simulation.status"
    requirement: TOOL-06
    verification:
      - kind: unit
        ref: "scripts/tests/test_ci_workflows.py#CiWorkflowContractTests"
        status: pass
    human_judgment: false
  - id: D5
    description: "A labelled same-repository pull request runs the simulate job end to end and leaves three artifacts; the same pull request without the label spends no quota; the ruleset then adopts gate as its required check"
    requirement: SIM-04
    verification: []
    human_judgment: true
    rationale: "The run needs the repository secret and a maintainer-applied label, is metered against the free-tier quota, and the ruleset is a GitHub-UI artifact; none can be exercised from the local tree (SIM-04, D-20)."

duration: 2min
completed: 2026-10-26
status: complete
plan_head_before: 8cc9895c85729effa9cab7d8228cccf74db14311
plan_head_after: 6781790c7f958ff24bf9948716d0472ec29acd7b
---

# Phase 8 Plan 3: Pull-request suite, host static analysis and opt-in simulation Summary

**`gate` now covers the Python suite and the host clang-tidy surface, and a labelled same-repository pull request can run a metered simulation that leaves seven-day evidence without ever reaching a fork**

## Performance

- **Duration:** 2 min
- **Started:** 2026-10-26T19:00:14Z
- **Completed:** 2026-10-26T19:02:19Z
- **Tasks:** 3
- **Files modified:** 2

## Accomplishments

- Added `python-tests` (10-minute budget) which installs `uv==0.13.5` and runs
  `python -m unittest discover scripts/tests`, closing the Phase 5 WR-13 gap.
- Added `static-analysis` (20-minute budget) which restores the same `~/.cache/pre-commit`
  entry as `meta`, installs the pinned PlatformIO and pre-commit, runs
  `pio run -d tests -e native -t compiledb`, and then
  `pre-commit run --all-files --hook-stage pre-push` — the only path that executes the two
  `stages: [pre-push]` clang-tidy hooks (Pitfall 8).
- Added the opt-in `simulate` job: event-first guard, both dependency results, head-repository
  equality, the `simulate` label and the two non-empty checks; `max-parallel: 2`; a
  step-level token refusal; a firmware build before the scenario; the pinned wokwi-cli 0.28.1
  with its recorded SHA-256; `--timeout 15000`; `--serial-log-file`; a `quota.json` recording
  the exit code and serial-log byte count; and an `if: always()` upload with
  `retention-days: 7` and `if-no-files-found: error`.
- Widened `gate.needs` to `[changes, meta, build, python-tests, static-analysis, simulate]`.
- Added `CiWorkflowContractTests` with eleven tests; the `needs` test derives the job set from
  the file, so a new job that is missing from `needs` fails the suite. The module went from
  22 to 38 tests and the suite from 316 to 332.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add `python-tests` and `static-analysis` and widen `gate.needs`** — `59f0bc6` (feat)
2. **Task 2: Add the opt-in `simulate` job with evidence upload** — `d901f0d` (feat)
3. **Task 3: Lock the gate contract and the matrix guards into the workflow test suite** — `6781790` (test)

**Plan metadata:** committed separately below (docs).

_Note: no TDD plan, so no RED/GREEN/REFACTOR commits._

## Files Created/Modified

- `.github/workflows/ci.yml` — two new required-surface jobs and the opt-in `simulate` job;
  `gate.needs` names all six.
- `scripts/tests/test_ci_workflows.py` — three job-surface tests, two simulation tests, the
  `job_block` and `needs_ids` helpers, and the eleven-test `CiWorkflowContractTests` class.

## Decisions Made

- The `simulate` job's `if` leads with `!cancelled()` and then `github.event_name ==
  'pull_request'`, so a `workflow_dispatch` run never reads a null pull-request context.
- The token check is a step (`if: env.WOKWI_CLI_TOKEN == ''`) and the job-level `if` never
  references `secrets`, which is unavailable in that context.
- The artifact name is derived in shell (`tr -c 'A-Za-z0-9._-' '-'` under `LC_ALL=C`) and
  exported through `$GITHUB_ENV`; the upload reads only `${{ env.ARTIFACT_NAME }}`.
- `static-analysis` restores the same `~/.cache/pre-commit` key as `meta` with no
  `restore-keys`, and generates the database itself because `scripts/clang-tidy-db` is a
  validator, never a generator.
- `test_gate_runs_under_not_cancelled` drops comment-only lines before asserting `always()`
  is absent: the D-2 comment names `always()` to explain why it is not used, so a raw-text
  assertion would have failed on the explanation rather than on the YAML.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- `.github/workflows/security.yml` is listed in Task 2's `read_first` but was retired by plan
  02; its pinned gitleaks install and scan block already live in `ci.yml`'s `meta` job, which
  is where the task's instructions redirected the reader anyway.
- `gsd_run` is not available in this worktree, so the per-task and metadata commits used
  `/usr/bin/git` directly with the same hook surface; all 13 pre-commit hooks passed on every
  commit and on `pre-commit run --all-files --show-diff-on-failure`.
- The comment in `.yamllint.yaml` still says "the four workflows"; it is now stale (two
  workflows remain). It is pre-existing and outside this plan's `files_modified`, so it was
  not edited.

## Known Stubs

None.

## Threat Flags

None — the `simulate` job is the T-8-11, T-8-12, T-8-13, T-8-14, T-8-15, T-8-21, T-8-22 and
T-8-23 mitigation already recorded in the plan's threat model, and the two analysis jobs are
the T-8-16 mitigation. No new trust boundary was introduced.

## User Setup Required

`WOKWI_CLI_TOKEN` (repository secret) and the `simulate` label are needed before the first
labelled run; both are recorded in the plan's `user_setup` and are not required for the
required check, which skips cleanly without them.

## Next Phase Readiness

- `ci.yml` declares `meta`, `changes`, `build`, `python-tests`, `static-analysis`, `simulate`
  and `gate`; TOOL-05 and TOOL-06 are satisfied textually.
- SIM-04's textual half is satisfied; the first labelled run is the measurement that resolves
  the `max-parallel: 2` and 10-minute budget assumptions and confirms the absolute
  `--serial-log-file` path in CI.
- Plan 04 must keep `gate.needs` exhaustive; `test_gate_needs_every_pull_request_job` fails
  the suite the moment a job is added without it.

## Self-Check: PASSED

- `.github/workflows/ci.yml` and `scripts/tests/test_ci_workflows.py` exist.
- Commits `59f0bc6` and `d901f0d` are ancestors of `HEAD` (`6781790`).
- `python3 -m unittest scripts.tests.test_ci_workflows -v`: 38 tests, `OK` (11 in
  `CiWorkflowContractTests`).
- `python3 -m unittest discover scripts/tests`: 332 tests, `OK` (1 skipped).
- `python3 -m unittest scripts.tests.test_simulation_paths -v`: 3 tests, `OK`.
- `pre-commit run --all-files --show-diff-on-failure`: all 13 hooks passed.
- The module imports neither PyYAML nor jsonschema.

---
*Phase: 08-fast-ci*
*Completed: 2026-10-26*

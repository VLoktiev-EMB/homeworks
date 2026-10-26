---
phase: 08-fast-ci
plan: 04
subsystem: docs
tags: [agents-md, documentation, ci-policy, gate, required-check, simulation-policy, pull-request-template, adr]

# Dependency graph
requires:
  - phase: 08-fast-ci
    plan: 01
    provides: ci.yml with the meta/changes/build/gate graph and the meta hook surface
  - phase: 08-fast-ci
    plan: 02
    provides: nightly.yml as the only other workflow and the retirement of homework.yml and security.yml
  - phase: 08-fast-ci
    plan: 03
    provides: python-tests, static-analysis and the opt-in simulate job feeding the single gate
provides:
  - AGENTS.md that names exactly ci.yml and nightly.yml and no retired workflow
  - the literal `gate` contract with its rename obligation written into the rulebook and the decision index
  - a split simulation policy — a [SHOULD] eligibility rule and a [MUST] fork guarantee
  - the CI hook-surface and ADR-0013 deferral statements in Quality tooling
  - the `gate` line in the pull-request Definition of Done
  - one decision row for the single fan-in gate topology
affects: [08-fast-ci phase verification, the GitHub ruleset human checkpoint, TOOL-05, TOOL-06, SIM-04]

# Actuals (#2632)
actuals:
  tokens: 2951
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "A rulebook rule names its enforcement point, and every CI claim names a job or workflow that exists in the tree"
    - "A policy with an optional half and a non-negotiable half is written as two rules, not one qualified rule"

key-files:
  created: []
  modified:
    - AGENTS.md
    - .github/pull_request_template.md
    - docs/decisions/README.md
    - .yamllint.yaml

key-decisions:
  - "The simulation policy is a new `### Simulation` subsection: a `[SHOULD]` eligibility rule names the changed project, the maintainer-applied label, the same-repository head, the 15-second timeout and the 7-day retention, while a separate `[MUST]` rule states the fork guarantee."
  - "The quick-start row keeps the developer spelling `python3 -m unittest discover scripts/tests` and names the CI job's exact `python -m unittest discover scripts/tests` in the purpose, so both forms are discoverable."
  - "The retired workflow names are removed outright instead of being annotated as retired, so no reader can follow a name to a file that no longer exists."
  - "The decision row is inserted directly after the simulator row as the plan directs; it shares the 2026-10-26 date with the rows around it."

patterns-established:
  - "AGENTS.md's layout and routing table name only workflows that exist; a retired name is a documentation bug, not history"
  - "A required-check rename is documented as a same-pull-request obligation, because the ruleset matches the literal job name"

requirements-completed: [TOOL-05, TOOL-06, SIM-04]

# Coverage metadata (#1602)
coverage:
  - id: D1
    description: "AGENTS.md names ci.yml (meta, changes, build, python-tests, static-analysis, simulate, gate) and nightly.yml in the layout and routing table, and neither retired workflow name survives"
    requirement: TOOL-05
    verification:
      - kind: other
        ref: "python3 -c AGENTS.md structural assertions (08-04-PLAN.md Task 1 <automated>)"
        status: pass
      - kind: unit
        ref: "scripts/tests/test_ci_workflows.py#WorkflowTriggerKeyTests.test_every_workflow_declares_a_textual_trigger_key (asserts the two-workflow set)"
        status: pass
    human_judgment: false
  - id: D2
    description: "AGENTS.md states that the literal `gate` job is the single required status check and that renaming it requires the ruleset change in the same pull request"
    requirement: TOOL-06
    verification:
      - kind: other
        ref: "python3 -c AGENTS.md structural assertions (08-04-PLAN.md Task 1 <automated>)"
        status: pass
    human_judgment: false
  - id: D3
    description: "AGENTS.md separates the simulation eligibility rule ([SHOULD]) from the fork guarantee ([MUST])"
    requirement: SIM-04
    verification:
      - kind: other
        ref: "python3 -c AGENTS.md structural assertions (08-04-PLAN.md Task 1 <automated>)"
        status: pass
    human_judgment: false
  - id: D4
    description: "The pull-request template names the required gate check, the decision index carries the single fan-in gate row with its change cost, and the yamllint comment states no workflow count"
    requirement: TOOL-06
    verification:
      - kind: other
        ref: "python3 -c template/decision/yamllint assertions (08-04-PLAN.md Task 2 <automated>)"
        status: pass
    human_judgment: false
  - id: D5
    description: "The GitHub ruleset adopts `gate` as its single required status check"
    requirement: TOOL-06
    verification: []
    human_judgment: true
    rationale: "Rulesets are a GitHub-UI artifact, and the check becomes selectable only after it has passed on a pull request within the last 7 days; no local command can prove or perform the change (D-20)."

duration: 3min
completed: 2026-10-26
status: complete
plan_head_before: 16ce8a277250e3971901496e65a9a48bab284b8a
plan_head_after: b8917e55c8c228cc8b0af8fd94a1773a769ab4b1
---

# Phase 8 Plan 4: Rulebook, template and decision index aligned with the two-workflow CI topology Summary

**`AGENTS.md` now names only `ci.yml` and `nightly.yml`, pins the literal `gate` required check with its rename obligation, and splits the simulation policy into an optional label-gated rule and a non-negotiable fork guarantee**

## Performance

- **Duration:** 3 min
- **Started:** 2026-10-26T19:03:42Z
- **Completed:** 2026-10-26T19:06:27Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments

- Replaced the retired secret-scan bullet in the repository layout with two bullets naming
  `ci.yml` (all seven pull-request jobs) and `nightly.yml` (full matrix plus the nightly
  secret scan); removed the retired drift-workflow sentence and restated the
  `gen-views-check` contract as running inside `meta`'s `pre-commit run --all-files`.
- Extended the `scripts/affected.py` paragraph to say the `changes` job consumes its
  `{build, simulate}` payload and that nightly feeds it the `platformio.shared.ini` path, so
  the mapper's own widen-all rule produces the full matrix.
- Added the `[MUST] [ENFORCED: CI]` pull-request rule naming the literal `gate` job as the
  single required status check and requiring the ruleset change in the same pull request.
- Added the fifth quick-start row (`python3 -m unittest discover scripts/tests`) and named
  the exact `python -m unittest discover scripts/tests` command the `python-tests` job runs;
  extended the `pre-commit run --all-files` row to identify it as the `meta` command.
- Updated Secrets to name `ci.yml`'s `meta` scan and `nightly.yml`'s `secrets` job, and
  Quality tooling to record the full hook surface and the `static-analysis` pre-push stage
  while replacing the Phase 8 forward reference with the ADR-0013 deferral (D-17).
- Added a `### Simulation` section with the `[SHOULD]` eligibility rule (changed project,
  maintainer-applied label, same-repository head, 15-second timeout, 7-day retention) and the
  `[MUST]` fork guarantee, and pointed the routing table at both workflows plus the new
  "Investigate a red required check" row.
- Added `- [ ] The required gate check is green` to the pull-request Definition of Done,
  recorded the single fan-in gate decision row with its change cost, and removed the stale
  workflow count from the `.yamllint.yaml` comment.

## Task Commits

Each task was committed atomically:

1. **Task 1: `AGENTS.md` names the CI topology, the `gate` contract and the simulation policy** — `1afdb61` (docs)
2. **Task 2: Record the decision and align the template, the index and the yamllint comment** — `b8917e5` (docs)

**Plan metadata:** committed separately below (docs).

_Note: no TDD plan, so no RED/GREEN/REFACTOR commits._

## Files Created/Modified

- `AGENTS.md` — layout, generated-views and affected.py paragraphs, quick-start, PR/tags,
  Secrets, Quality tooling, a new Simulation section and the routing table.
- `.github/pull_request_template.md` — one Definition of Done line naming the required
  `gate` check; the rest of the checklist is untouched.
- `docs/decisions/README.md` — one row for the single fan-in `gate` topology and its change
  cost, after the simulator row.
- `.yamllint.yaml` — the comment no longer states a workflow count; every rule and value is
  unchanged.

## Decisions Made

- The simulation policy becomes its own `### Simulation` subsection with two rules rather
  than one qualified rule, because the optional eligibility and the fork guarantee have
  different severities.
- The quick-start row uses the developer spelling `python3` and names the CI job's exact
  `python -m unittest discover scripts/tests` in the purpose, satisfying both the local
  convention and the textual contract.
- Retired workflow names are deleted rather than annotated, so the rulebook cannot send a
  reader to a file that does not exist.
- The decision row sits immediately after the simulator row, as the plan directs; both carry
  the 2026-10-26 date.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- `gsd_run` is not available in this worktree, so the task commits used `/usr/bin/git`
  directly. All 13 pre-commit hooks ran on both commits and on
  `pre-commit run --all-files --show-diff-on-failure`.
- The plan's Task 1 `<automated>` assertion requires the substring
  `python -m unittest discover scripts/tests`, while the prescribed quick-start row spells the
  command with `python3`; the purpose column names the CI spelling so both the command and
  the assertion hold.
- The Task 2 `<human-check>` (add `gate` to the ruleset after the first green run) is a live
  GitHub-UI step and is recorded below for end-of-phase UAT, not executed here.

## Known Stubs

None.

## Threat Flags

None — this plan changes documentation only and introduces no new network endpoint, auth
path, file-access pattern or schema change. T-8-17 and T-8-18 are mitigated by naming only
jobs that exist and by writing the rename obligation into both the rulebook and the decision
row; T-8-19 is accepted as a documentation-only residual.

## User Setup Required

One manual step remains for the phase, recorded for end-of-phase UAT: after the first green
`ci.yml` run on a pull request, the repository owner opens Settings -> Rules -> the `main`
ruleset and adds `gate` as the required status check (0 approvals). The check becomes
selectable only after it has passed once within the last 7 days (D-20).

## Next Phase Readiness

- `AGENTS.md`, the pull-request template, the decision index and the yamllint comment now
  agree with the two workflows that exist; TOOL-05, TOOL-06 and SIM-04 are documented where a
  contributor looks first.
- The live ruleset change remains the only open deliverable for the phase and is human-only.
- The full suite (332 tests, 1 skipped), the 13-hook pre-commit surface and
  `uv run scripts/gen_views.py --all --check` are green.

## Self-Check: PASSED

- `AGENTS.md`, `.github/pull_request_template.md`, `docs/decisions/README.md` and
  `.yamllint.yaml` exist.
- Commits `1afdb61` and `b8917e5` are ancestors of `HEAD` (`b8917e5`).
- `python3 -m unittest scripts.tests.test_ci_workflows -v`: 38 tests, `OK`.
- `python3 -m unittest discover scripts/tests`: 332 tests, `OK` (1 skipped).
- `pre-commit run --all-files --show-diff-on-failure`: all 13 hooks passed.
- `uv run scripts/gen_views.py --all --check`: all four generated targets unchanged.

---
*Phase: 08-fast-ci*
*Completed: 2026-10-26*

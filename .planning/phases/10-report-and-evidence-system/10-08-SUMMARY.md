---
phase: 10-report-and-evidence-system
plan: "08"
subsystem: tooling
tags: [pre-commit, hook, report-contract, merge-gate, agents-md, pr-template, decisions, skill-mirror]

requires:
  - phase: 10-report-and-evidence-system
    provides: plans 10-01…10-07's checker, template, retrofit, standards, and rule registry
provides:
  - "check-report pre-commit hook — check-only, PyYAML-only, scoped to the eight report-contract input families"
  - "test_every_hook_id_appears_in_one_stage_tuple — the closed hook-id set, so no hook dodges the stage checks"
  - "test_check_report_hook_is_check_only_and_scoped — the hook's shape and scope, asserted rather than declared"
  - "AGENTS.md Quick start row 6, Reports and evidence rule block, Definition of Done clause 4, routing row"
  - ".github/pull_request_template.md checker checkbox and four-item Report self-audit"
  - "docs/decisions/README.md checked-contract row"
  - "hw-report stub repointed at docs/standards/report.md and the checker, with its regenerated mirror"
affects: [11]

actuals:
  tokens: 5732
  tasks: 3
  commits: 2
  plan_head_before: 96efd359c806e811e98d7b3c2ea26af557b051fd
  plan_head_after: 8665e4f

tech-stack:
  added: []
  patterns:
    - "The stage tuples are module constants and the config's own id set must equal their union, so a new hook cannot be added without an inspection decision"
    - "A folded `>-` hook pattern is read back by joining its continuation lines with one space, exactly as YAML folds it, so the test matches the regex the hook receives"
    - "One command and one standard are named on every human surface; the prose itself stays review-enforced (261026-ky7)"

key-files:
  created: []
  modified:
    - .pre-commit-config.yaml
    - scripts/tests/test_tooling_config.py
    - AGENTS.md
    - .github/pull_request_template.md
    - docs/decisions/README.md
    - .claude/skills/hw-report/SKILL.md
    - .claude/skills/hw-report/CHANGELOG.md
    - .agents/skills/hw-report/SKILL.md
    - .agents/skills/hw-report/CHANGELOG.md
    - generated.skills.manifest

key-decisions:
  - "The merge-gate flip is recorded as enabled (option `enable`, D-19): the checker gates merges from Phase 10 onward and no grandfather clause is introduced"
  - "The routing-table row replaced the stale `docs/standards/ (planned, Phase 10)` row rather than sitting beside it, so the table keeps exactly one report row"
  - "`_hook_folded_field` joins a `>-` continuation block with single spaces, mirroring YAML folding, because `_hook_field` would return the bare `>-` marker"
  - "`test_every_fast_hook_keeps_the_pre_commit_stage` and `test_both_push_hooks_declare_the_pre_push_stage` now read `FAST_HOOK_IDS` / `PUSH_HOOK_IDS`, so the closed-set test and the stage tests share one source"

requirements-completed: [TOOL-08, REPORT-01, REPORT-02, REPORT-03, REPORT-04, REPORT-05, REPORT-06, REPORT-07, REPORT-08]

coverage:
  - id: D1
    description: "The check-report pre-commit hook exists, is check-only, and runs the report checker over the eight declared input families"
    requirement: TOOL-08
    verification:
      - kind: unit
        ref: "scripts/tests/test_tooling_config.py#HookLayeringTests.test_check_report_hook_is_check_only_and_scoped"
        status: pass
      - kind: other
        ref: "pre-commit run check-report --all-files"
        status: pass
    human_judgment: false
  - id: D2
    description: "The config's hook-id set equals the union of the fast and push tuples, so a new hook cannot go uninspected"
    requirement: TOOL-08
    verification:
      - kind: unit
        ref: "scripts/tests/test_tooling_config.py#HookLayeringTests.test_every_hook_id_appears_in_one_stage_tuple"
        status: pass
    human_judgment: false
  - id: D3
    description: "The hw-report mirror is regenerated from the canonical skill and the drift check proves it"
    requirement: TOOL-08
    verification:
      - kind: other
        ref: "uv run scripts/gen_skills.py --check"
        status: pass
      - kind: other
        ref: "pre-commit run gen-skills-check --all-files"
        status: pass
    human_judgment: false
  - id: D4
    description: "AGENTS.md, the pull-request template, the decisions table, and the hw-report stub all name `uv run scripts/check_report.py` and `docs/standards/report.md`"
    verification:
      - kind: other
        ref: "pre-commit run --all-files (markdownlint-cli2 + the whole hook surface)"
        status: pass
    human_judgment: true
    rationale: "Prose sync is review-enforced by design (261026-ky7 pruned document-text assertions); only the hook shape, the id set, and the mirror are machine-pinned, so a human confirms the three surfaces say the same thing."

duration: 11min
completed: 2026-10-27
status: complete
---

# Phase 10 Plan 08: Merge Gate and Human Surfaces Summary

**`check-report` is now a check-only pre-commit hook with a closed hook-id set behind it, and AGENTS.md, the pull-request template, the decisions table, and the `hw-report` stub all name the same command and the same standard.**

## Performance

- **Duration:** 11 min
- **Started:** 2026-10-27T15:06:40Z
- **Completed:** 2026-10-27T15:17:13Z
- **Tasks:** 3
- **Files modified:** 10

## Checkpoint Decision

The plan opened with a `checkpoint:decision` ("Confirm the one-way merge-gate flip before the
hook lands"). The human selected **`enable`** in this session, the option D-19 specifies.

- **Recorded answer:** `enable` — enable `check_report` as a merge gate in this phase.
- **Consequence:** the checker is a merge precondition from Phase 10 onward, Definition of Done
  clause 4 changes from "guidance" to "the checked contract", and no grandfather clause exists.
- **Not taken:** `defer`, which would have contradicted D-19 and required a superseding row in
  `docs/decisions/README.md`.

## Accomplishments

- Added the `check-report` hook beside `check-metadata`: `language: python`,
  `additional_dependencies: ["PyYAML==6.0.3"]`, `entry: python scripts/check_report.py`,
  `pass_filenames: false`, `stages: [pre-commit]`, and a folded `(?x)` `files` pattern reaching
  exactly the eight declared families — each homework's `report.md`, `homework.yaml`, and
  `assets/diagram.json`; `templates/report/`; both standards documents; the checker; and
  `scripts/report/`. It stays out of `docs/standards/vscode.md` and `README.md`.
- Closed the hook set: `FAST_HOOK_IDS` and `PUSH_HOOK_IDS` are module constants, and
  `test_every_hook_id_appears_in_one_stage_tuple` asserts the config's parsed `- id:` set equals
  their union and that the two tuples are disjoint.
- Added `test_check_report_hook_is_check_only_and_scoped`, which proves the exact entry, the
  single pin, the absence of any `args:`, `pass_filenames: false`, the pre-commit stage, and the
  eight-family scope in both directions.
- Points every human surface at the gate: the `AGENTS.md` quick-start row 6, a compact
  `### Reports and evidence` block of three `[MUST]`/`[ENFORCED: pre-commit]` bullets, a rewritten
  Definition of Done clause 4, and a routing-table row; the pull-request template's checker
  checkbox plus a four-item `### Report self-audit`; and one checked-contract row in
  `docs/decisions/README.md`.
- Repointed the `hw-report` stub at `docs/standards/report.md` and the checker, added the dated
  changelog entry, and regenerated the `.agents/skills/` mirror and manifest with
  `uv run scripts/gen_skills.py`. The skill stays `metadata.status: stub` and
  `disable-model-invocation: true`.

## Task Commits

Each task was committed atomically:

1. **Task 1: Confirm the one-way merge-gate flip** — answered `enable`; no commit (decision only).
2. **Task 2: Add the check-report hook and close the hook-set test** - `112c6b4` (feat)
3. **Task 3: Point AGENTS.md, the pull-request template, the decisions table, and the hw-report stub at the gate** - `8665e4f` (docs)

**Plan metadata:** the SUMMARY commit (docs: complete the merge gate and human surfaces plan).

## Files Created/Modified

- `.pre-commit-config.yaml` — the `check-report` hook in the local block, with the check-only and
  PyYAML-only boundary recorded in comments.
- `scripts/tests/test_tooling_config.py` — `FAST_HOOK_IDS` / `PUSH_HOOK_IDS`, the scope samples,
  `_hook_folded_field`, and the two new tests.
- `AGENTS.md` — quick-start row 6, the `### Reports and evidence` block, DoD clause 4, the routing
  row; the obsolete `Planned: report structure … (Phase 10)` line is gone.
- `.github/pull_request_template.md` — `uv run scripts/check_report.py` in the checklist and the
  `### Report self-audit` list.
- `docs/decisions/README.md` — one `2026-10-27` row, `Record` `—`.
- `.claude/skills/hw-report/SKILL.md`, `CHANGELOG.md` — the stub pointer and its dated entry.
- `.agents/skills/hw-report/SKILL.md`, `CHANGELOG.md`, `generated.skills.manifest` — regenerated,
  never hand-edited.

## Decisions Made

- **Merge gate enabled (D-19).** Recorded from the human's `enable` answer; the checker is a merge
  precondition and no grandfather clause is introduced.
- **The routing row was replaced, not duplicated.** The plan asked for a new routing row and the
  removal of the `Planned:` line; the existing `Report structure and formatting rationale |
  docs/standards/ (planned, Phase 10)` row was the same concern pointing at a directory rather
  than the standard, so it became the single new row instead of leaving a stale twin.
- **The folded pattern is read back the way YAML folds it.** `_hook_field` returns the bare `>-`
  marker, so `_hook_folded_field` joins the continuation lines with single spaces; the test then
  matches the exact regex the hook receives.
- **The stage tuples became the shared source.** The two stage tests reference the same constants
  the closed-set test unions, so adding a hook requires one edit in one place.

## Deviations from Plan

None that altered the contract — the hook, the tests, and the four human surfaces were built as
written. Two implementation details worth naming:

- `.agents/skills/hw-report/CHANGELOG.md` was regenerated alongside `SKILL.md`; the plan named only
  the `SKILL.md` mirror file, but `gen_skills.py` owns the whole `hw-report` mirror including the
  changelog, so both moved together.
- The plan's task-2 `<verify>` (`-k report`) matches one test; the closed-set test's name does not
  contain "report", so the whole module was also run (88 tests, `OK (skipped=1)`) to prove it.

**Total deviations:** 0 auto-fixed. **Impact:** none on scope, correctness, or the threat surface.

## Issues Encountered

- The harness refused a `git add` invoked through the shell's `rtk` wrapper as unverifiable inside
  the worktree; staging and committing were run with `/usr/bin/git` from the worktree root instead.
  No history or content changed.
- The full `discover` run exceeds the foreground default, so it was run in the background and
  finished green: 582 tests, `OK (skipped=1)` (the pre-existing clangd-guide skip).

## Threat Model Disposition

- **T-10-23 (Tampering, `check-report`):** mitigated. The hook declares `pass_filenames: false`
  and `stages: [pre-commit]` with no `args:`, and `test_check_report_hook_is_check_only_and_scoped`
  asserts both the absence of write arguments and the exact entry.
- **T-10-24 (Tampering / supply chain, hook dependencies):** mitigated. The environment is exactly
  `["PyYAML==6.0.3"]`, already pinned elsewhere; no `rev` changed and the test asserts the exact
  list.
- **T-10-25 (Tampering, document drift):** partially mitigated. AGENTS.md and the pull-request
  template both name `docs/standards/report.md` and the same command, but the prose itself stays
  review-enforced; the machine half is the rule-id set test from plan 10-07 and the mirror check.
- **T-10-26 (Tampering, `.agents/skills/` mirror):** mitigated. Regenerated only by
  `uv run scripts/gen_skills.py`; `gen-skills-check` is green.
- **T-10-SC (Tampering, dependency installs):** mitigated. No package was added.

## Known Stubs

None. The `hw-report` skill remains an intentional stub by design (D-27), not a stub defect: it
carries `metadata.status: stub`, `disable-model-invocation: true`, and a complete manual fallback.
Promotion is a Phase 11 candidate.

## Threat Flags

None — the changes add no network endpoint, auth path, file-access pattern, or schema surface.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- The gate is live locally and in CI without a new job: `meta` already runs
  `pre-commit run --all-files`, and `gate` aggregates it. `.github/workflows/ci.yml` is unchanged.
- Plan 10-08 completes Phase 10; requirement marking and the phase-level state/roadmap updates are
  left to the orchestrator, which owns the shared artifacts in worktree mode.
- `scripts/affected.py` was deliberately untouched (D-32): a report change already selects its
  homework for a build, and the report check is a whole-tree `meta` concern.

## Self-Check: PASSED

- Files exist: `.pre-commit-config.yaml`, `scripts/tests/test_tooling_config.py`, `AGENTS.md`,
  `.github/pull_request_template.md`, `docs/decisions/README.md`,
  `.claude/skills/hw-report/SKILL.md`, `.agents/skills/hw-report/SKILL.md`,
  `generated.skills.manifest`.
- Commits exist: `112c6b4`, `8665e4f`.
- `pre-commit run check-report --all-files` — Passed.
- `pre-commit run --all-files` — all 15 hooks Passed (the exact `meta` command).
- `python3 -m unittest scripts.tests.test_tooling_config` — 88 tests, `OK (skipped=1)`.
- `python3 -m unittest discover scripts/tests` — 582 tests, `OK (skipped=1)`.
- `uv run scripts/check_metadata.py` and `uv run scripts/check_report.py` — `PASS`.
- `uv run scripts/gen_skills.py --check` — exit 0, no drift.
- `.github/workflows/ci.yml` — unchanged.

---
*Phase: 10-report-and-evidence-system*
*Completed: 2026-10-27*

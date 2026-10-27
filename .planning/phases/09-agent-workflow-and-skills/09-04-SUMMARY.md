---
phase: 09-agent-workflow-and-skills
plan: 04
subsystem: tooling
tags: [agent-skills, hw-build, bounded-repair, escalation, generated-mirror]

# Dependency graph
requires:
  - phase: 09-agent-workflow-and-skills
    plan: 01
    provides: scripts/gen_skills.py, the generated.skills.manifest ledger and the gen-skills-check hook
  - phase: 09-agent-workflow-and-skills
    plan: 02
    provides: .claude/skills/_shared/guardrails.md, the shared policy the skill reads
  - phase: 04.2-tracer-homework-1-3
    provides: F-03 cold-run facts and F-05 native -Werror and fake-reset facts
provides:
  - .claude/skills/hw-build/SKILL.md, the two-leg build and native-suite contract
  - .claude/skills/hw-build/references/repair-loop.md, the bounded loop and escalation payload
  - the hw-build CHANGELOG.md and LESSONS.md records
  - their generated .agents/skills mirror and the updated generated.skills.manifest ledger
affects: [09-08-dry-run, phase-10-report-format]

# Actuals (#2632) — pairs with the plan's estimate to calibrate future estimates.
# Same estimateTokens scale (chars/4 over the realized diff), never a harness token count.
actuals:
  tokens: 6400
  tasks: 2
  commits: 1

plan_head_before: 8b4f00dc43572329c4fd697949a6a90dfeacffca
plan_head_after: 1127b9c1326fe32074ccfa6615108b727515d96d

tech-stack:
  added: []
  patterns:
    - a two-leg build contract where each leg owns its own two-attempt counter
    - the whole invocation stops for user direction when either leg exhausts two
    - the escalation payload explains cause, both fixes, commands with exit codes, warnings and a direction question

key-files:
  created:
    - .claude/skills/hw-build/SKILL.md
    - .claude/skills/hw-build/references/repair-loop.md
    - .claude/skills/hw-build/CHANGELOG.md
    - .claude/skills/hw-build/LESSONS.md
    - .agents/skills/hw-build/SKILL.md
    - .agents/skills/hw-build/references/repair-loop.md
    - .agents/skills/hw-build/CHANGELOG.md
    - .agents/skills/hw-build/LESSONS.md
  modified:
    - generated.skills.manifest

key-decisions:
  - "Both tasks landed in one commit because scripts/gen_skills.py refuses a skill directory without SKILL.md, so a references-only tree cannot pass the gen-skills-check gate."
  - "The repair counter is stated per run, not per error: the build leg and the native leg each own two attempts, and either leg's exhaustion stops the whole invocation."
  - "The shared tests/ suite runs on a user request or a lib/ diff only, matching scripts/affected.py; hw-build never claims the full pre-PR chain."

patterns-established:
  - "A bounded loop names its counter's lifetime explicitly and gives each independent leg its own budget."
  - "An escalation quotes warnings separately from errors and ends the run before a third edit."
  - "A build skill reports the real command and its real exit code instead of wrapping PlatformIO."

requirements-completed: [FLOW-06]

coverage:
  - id: D1
    description: "references/repair-loop.md defines the per-run two-attempt counter per leg, the whole-invocation stop, the environment rule, the shared-suite triggers, the repair boundaries, the F-03/F-05 facts and the escalation payload"
    requirement: FLOW-06
    verification:
      - kind: integration
        ref: "test -s .claude/skills/hw-build/references/repair-loop.md"
        status: pass
      - kind: integration
        ref: "uv run scripts/gen_skills.py --check"
        status: pass
    human_judgment: true
    rationale: "D-18 makes the loop review-enforced model behaviour; the 09-08 dry run staged fixture is the behavioural evidence."
  - id: D2
    description: "SKILL.md states the real two commands, the id regex and argv rule, the default_envs/-e fallback, the two-attempt stop, the shared-suite trigger and the no-commit/no-checkpoint rules"
    requirement: FLOW-06
    verification:
      - kind: integration
        ref: "pre-commit run markdownlint-cli2 --files .claude/skills/hw-build/SKILL.md"
        status: pass
      - kind: integration
        ref: "pio run -d homeworks/1_3-police-flasher && pio test -d homeworks/1_3-police-flasher -e native"
        status: pass
    human_judgment: true
    rationale: "The conversation contract is prose; the commands it names were re-run green, but the bounded behaviour itself is observed in the 09-08 transcript."
  - id: D3
    description: "The canonical directory and its generated mirror carry SKILL.md, the repair-loop reference and both dated companion records; the ledger lists all four and --check is clean"
    requirement: FLOW-06
    verification:
      - kind: integration
        ref: "uv run scripts/gen_skills.py --check"
        status: pass
      - kind: integration
        ref: "pre-commit run gen-skills-check --all-files"
        status: pass
      - kind: integration
        ref: "python3 -m unittest discover scripts/tests"
        status: pass
    human_judgment: false

duration: 5 min
completed: 2026-10-26
status: complete
---

# Phase 9 Plan 04: hw-build Bounded Repair Loop Summary

**A two-leg build and native-suite contract bounds repairs at two attempts per leg per run, stops the whole invocation on exhaustion, and escalates with the cause, both fixes, the evidence and a direction question.**

## Performance

- **Duration:** 5 min
- **Started:** 2026-10-26T21:31:00Z
- **Completed:** 2026-10-26T21:36:42Z
- **Tasks:** 2 (committed as 1, see Deviations)
- **Files modified:** 9

## Accomplishments

- `references/repair-loop.md` fixes the counter's lifetime: `attempt` starts at zero when
  a leg begins, counts repairs rather than errors, and gives the build leg and the native
  leg two attempts each. The whole invocation stops as soon as either leg exhausts two,
  and only a new user-directed run resets it.
- The loop names the real commands: `pio run -d homeworks/<id>` with `-e <env>` when
  `default_envs` is absent or plural, and `pio test -d homeworks/<id> -e native`. It
  forbids a wrapper that hides the exit code.
- The shared `pio test -d tests -e native` runs only on an explicit user request or a
  `lib/` diff, and the skill says which trigger fired and never claims the full pre-PR
  chain.
- Repair boundaries are explicit: `src/`, `include/`, or a homework-local
  `homeworks/<id>/lib/**`; a fixture needs a demonstrated defect and user confirmation; an
  assertion is never weakened; unrelated reformatting, `git checkout --` and tree resets
  are forbidden.
- The escalation payload carries the cause, both fixes with files and reasoning, the
  commands and exit codes, warnings quoted separately, what was ruled out, and one
  direction question; it never edits again.
- F-03 cold-run facts and F-05 `-Werror` / fake-reset / idle-button-HIGH facts are written
  as repair evidence, and the skill states it writes no `.skill-state/` checkpoint and
  never commits.
- The canonical directory and the generated mirror carry the same four files, and
  `uv run scripts/gen_skills.py --check` is clean.

## Task Commits

Each task's work was committed atomically:

1. **Tasks 1 and 2: the repair-loop reference, the skill contract, the companion records and the regenerated mirror** - `1127b9c` (feat)

**Plan metadata:** this SUMMARY commit.

## Files Created/Modified

- `.claude/skills/hw-build/references/repair-loop.md` - the bounded loop and escalation payload
- `.claude/skills/hw-build/SKILL.md` - the two-leg build and native-suite contract
- `.claude/skills/hw-build/CHANGELOG.md` - the dated 0.1 delivery record
- `.claude/skills/hw-build/LESSONS.md` - the F-05 native-build lesson
- `.agents/skills/hw-build/**` - the generated mirror of all four files
- `generated.skills.manifest` - the updated mirror ledger

## Decisions Made

- Tasks 1 and 2 were committed together because `scripts/gen_skills.py` exits 2 with
  `ERROR: .claude/skills/hw-build: a skill directory must contain SKILL.md`. A commit
  carrying only the reference cannot pass the `gen-skills-check` hook, and staging a
  partial mirror would leave the committed ledger naming files the commit does not carry.
- The reference treats the build leg and the native leg as independent budgets while the
  stop condition is shared, so one leg's success never refunds the other's attempts.
- The environment rule is written as a fallback rather than a default: the homework
  declares one `default_envs` entry today, so the bare command is correct there.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Tasks 1 and 2 could not be committed separately**
- **Found during:** Task 1 commit
- **Issue:** The `gen-skills-check` pre-commit hook runs `python scripts/gen_skills.py
  --check` over the whole tree, and the generator exits 2 when a skill directory has no
  `SKILL.md`. A commit carrying only `references/repair-loop.md` therefore cannot pass the
  gate, and a commit carrying the canonical files without their mirror would leave the
  committed ledger drifting.
- **Fix:** Wrote the Task 2 deliverables before the first commit and landed both tasks in
  one atomic commit; all acceptance criteria are satisfied in the tree.
- **Files modified:** the four canonical skill files, their four mirror files and
  `generated.skills.manifest`
- **Verification:** `uv run scripts/gen_skills.py --check` exits 0;
  `pre-commit run gen-skills-check --all-files` passes; the commit ran the full pre-commit
  surface with no skip and no `--no-verify`.
- **Committed in:** `1127b9c`

---

**Total deviations:** 1 auto-fixed (blocking)
**Impact on plan:** No scope change and no unverified content. The only cost is that the
task-to-commit mapping is 1 rather than 2.

## Issues Encountered

- The worktree's rtk git guard refuses compound `git` invocations and runtime-expanded
  environment variables, so every git call ran as a plain `/usr/bin/git` command. No hook
  was bypassed.
- The first target-build output was truncated by the command condenser, so the build was
  re-run with an explicit `EXIT=$?` probe and reported `SUCCESS` with `EXIT=0`.

## Known Stubs

None - `hw-build` is an implemented skill, not a stub. The four stubs in this phase are
owned by plan 09-02.

## Threat Flags

None - the surfaces this plan adds (the id in `pio run -d`, the reported result, the
repair target set) are the ones the plan's threat register already covers (T-09-06,
T-09-20, T-09-14, T-09-SC).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The 09-08 dry run can name `hw-build`'s two commands and stage the three-error fixture
  the plan's assumption names; this skill supplies the bounded loop it must observe.
- `uv run scripts/gen_skills.py --check` exits 0 with every record `UNCHANGED`,
  `pre-commit run gen-skills-check --all-files` passes, and
  `python3 -m unittest discover scripts/tests` reports 375 tests with 1 skip.
- `pio run -d homeworks/1_3-police-flasher` reports `SUCCESS` (exit 0) and
  `pio test -d homeworks/1_3-police-flasher -e native` reports 38 passed cases, proving the
  commands the skill names are the real ones.
- No blockers.

## Self-Check: PASSED

- `1127b9c` is an ancestor of HEAD; the four canonical files and the four mirror files
  exist and are non-empty; the mirror check and the tooling suite are green.

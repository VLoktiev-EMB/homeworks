---
phase: 09-agent-workflow-and-skills
plan: 02
subsystem: tooling
tags: [agent-skills, guardrails, stubs, generated-mirror, course-index]

# Dependency graph
requires:
  - phase: 09-agent-workflow-and-skills
    plan: 01
    provides: scripts/gen_skills.py, the generated.skills.manifest ledger and the check-only gen-skills-check hook
  - phase: 05-generated-views
    provides: the plan-then-apply generator spine and the committed manifest shape
provides:
  - .claude/skills/_shared/guardrails.md, the shared policy every implemented skill reads
  - the hw-report, schematic and course-index stubs with dated CHANGELOG.md and LESSONS.md records
  - their generated .agents/skills mirror and the updated generated.skills.manifest ledger
affects: [09-03, 09-04, 09-05, 09-06, 09-07, 09-08, phase-10-report-format]

# Actuals (#2632) — pairs with the plan's estimate to calibrate future estimates.
actuals:
  tokens: 5953
  tasks: 3
  commits: 3

plan_head_before: cd9d3cd54d0e0f6174585d3616e7c0c54af9fa82
plan_head_after: 00847b895cbb6d9070dd8576fd4c5d65cef21793

tech-stack:
  added: []
  patterns:
    - severity-and-enforcement annotation reuse for shared policy prose
    - stub contract: status marker, description self-label, body banner, manual fallback, dated records
    - the read-only skill is the only model-invocable skill

key-files:
  created:
    - .claude/skills/_shared/guardrails.md
    - .claude/skills/hw-report/SKILL.md
    - .claude/skills/hw-report/CHANGELOG.md
    - .claude/skills/hw-report/LESSONS.md
    - .claude/skills/schematic/SKILL.md
    - .claude/skills/schematic/CHANGELOG.md
    - .claude/skills/schematic/LESSONS.md
    - .claude/skills/course-index/SKILL.md
    - .claude/skills/course-index/CHANGELOG.md
    - .claude/skills/course-index/LESSONS.md
    - .agents/skills/_shared/guardrails.md
    - .agents/skills/hw-report/SKILL.md
    - .agents/skills/hw-report/CHANGELOG.md
    - .agents/skills/hw-report/LESSONS.md
    - .agents/skills/schematic/SKILL.md
    - .agents/skills/schematic/CHANGELOG.md
    - .agents/skills/schematic/LESSONS.md
    - .agents/skills/course-index/SKILL.md
    - .agents/skills/course-index/CHANGELOG.md
    - .agents/skills/course-index/LESSONS.md
  modified:
    - generated.skills.manifest

key-decisions:
  - "The guardrails live in `_shared/guardrails.md` and are mirrored as a file, so `../_shared/guardrails.md` resolves identically under `.claude/skills/` and `.agents/skills/` from every skill directory."
  - "`course-index` omits `disable-model-invocation` because it is read-only; the other three stubs keep it, and the generator injects the explicit-only banner only where the key was dropped."
  - "Every stub `description` names the skill a placeholder, so a client that reads only `description` cannot mistake it for an implemented capability; the body banner stays the authoritative marker."
  - "No content validator was added, per D-18: the only machine check remains the mirror drift check, and the stub wording is review-enforced."

patterns-established:
  - "Shared policy prose reuses the AGENTS.md register: one severity and one enforcement point per rule."
  - "A stub names what it does not do, the manual fallback command, and a dated CHANGELOG.md and LESSONS.md entry naming its run."
  - "A read-only skill may be model-invoked; a skill that writes files or touches hardware is explicit-only."

requirements-completed: [FLOW-04, FLOW-07]

coverage:
  - id: D1
    description: "_shared/guardrails.md states the flashing, commit/PR, specification-versus-best-practice, ambiguity, secrets and evidence rules with a severity and enforcement point each"
    requirement: FLOW-04
    verification: []
    human_judgment: true
    rationale: "D-18 makes skill prose review-enforced; the machine check proves only that the mirror is in sync, not that the policy wording is correct."
  - id: D2
    description: "The hw-report, schematic and course-index stubs each carry metadata.status: stub, a self-labelling description, a body banner naming the gap and the manual fallback, and dated CHANGELOG.md and LESSONS.md records"
    requirement: FLOW-07
    verification: []
    human_judgment: true
    rationale: "D-18 declines a content validator, so the stub markers and fallback wording are review-enforced rather than asserted by a test."
  - id: D3
    description: "Every authored file is mirrored behind the generated marker and the ledger is current"
    requirement: FLOW-07
    verification:
      - kind: integration
        ref: "uv run scripts/gen_skills.py --check"
        status: pass
      - kind: integration
        ref: "pre-commit run gen-skills-check --all-files"
        status: pass
    human_judgment: false
  - id: D4
    description: "course-index is read-only and model-invocable, and its body reads the generated README region between the two markers"
    requirement: FLOW-07
    verification:
      - kind: integration
        ref: "python3 -c assertion over canonical and mirror course-index SKILL.md"
        status: pass
    human_judgment: true
    rationale: "The structural assertions pass, but the rule that the skill never re-scans homeworks/ is prose and stays review-enforced."

duration: 2 min
completed: 2026-10-26
status: complete
---

# Phase 9 Plan 02: Shared Guardrails and the Four-Stub Inventory Summary

**A six-section review-enforced guardrails file and three documented stubs — `hw-report`, `schematic` and `course-index` — ship together with their generated mirror and a drift-clean ledger, closing the four-stub inventory.**

## Performance

- **Duration:** 2 min
- **Started:** 2026-10-26T21:26:20Z
- **Completed:** 2026-10-26T21:28:25Z
- **Tasks:** 3
- **Files modified:** 21

## Accomplishments

- `_shared/guardrails.md` carries the six policies in the required order, each rule
  annotated with a `[MUST]` or `[SHOULD]` severity and `[ENFORCED: review]`; the
  flashing section names the literal `так` / `yes` affirmation, forbids a default
  yes and forbids pre-approving `upload`, and the secrets section records only
  `simulation_token_present: true|false`.
- `hw-report`, `schematic` and `course-index` are stubs at `metadata.version: "0.1"`
  with `metadata.status: stub`, a self-labelling description, a body banner naming
  what each does not do, the manual fallback, and dated `CHANGELOG.md` and
  `LESSONS.md` records.
- `course-index` is the only model-invocable skill: it omits
  `disable-model-invocation`, reads the README region between
  `<!-- BEGIN GENERATED: homeworks -->` and `<!-- END GENERATED -->`, and never
  re-scans `homeworks/`.
- The generator mirrored `_shared/` as a file with no `_shared/SKILL.md`, produced
  the three stub mirrors, and updated `generated.skills.manifest`; `--check` is
  clean.

## Task Commits

Each task was committed atomically:

1. **Task 1: Write the shared guardrails and the `hw-report` stub** - `a5d9e59` (feat)
2. **Task 2: Add the `schematic` stub and regenerate the mirror** - `defa698` (feat)
3. **Task 3: Add the read-only `course-index` stub and close the stub inventory** - `00847b8` (feat)

**Plan metadata:** this SUMMARY commit.

## Files Created/Modified

- `.claude/skills/_shared/guardrails.md` - the shared six-section policy every
  implemented skill reads before its first write
- `.claude/skills/hw-report/{SKILL,CHANGELOG,LESSONS}.md` - the report stub and its
  dated records
- `.claude/skills/schematic/{SKILL,CHANGELOG,LESSONS}.md` - the wiring stub naming
  the Wokwi diagram editor and `wokwi-cli lint --offline`
- `.claude/skills/course-index/{SKILL,CHANGELOG,LESSONS}.md` - the read-only,
  model-invocable index stub
- `.agents/skills/**` - the generated mirror of all ten authored files
- `generated.skills.manifest` - the updated mirror ledger

## Decisions Made

- The guardrails are mirrored as a file under `.agents/skills/_shared/`, so the
  `../_shared/guardrails.md` include path resolves identically in both trees from
  any skill directory.
- `hw-report`'s fallback states explicitly that the template skeleton is not a
  validated report contract, and Phase 10 owns the format and its validation.
- The three new stubs keep `disable-model-invocation: true`; only `course-index`
  omits it, which is the one intended asymmetry (D-03, D-20).

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- Task 1's `<files>` header listed only the canonical files, while its `<action>`
  requires `uv run scripts/gen_skills.py` and its `<acceptance_criteria>` require
  the mirror and the ledger. The action and criteria governed, so the Task 1
  commit also carries `.agents/skills/_shared/guardrails.md`, the three
  `hw-report` mirror files and `generated.skills.manifest`. No rule deviation was
  needed.
- The cross-phase defect register `.planning/WINDOWS.md` is absent in this wave
  and `gsd_run` is unavailable in the worktree, so the optional ledger append was
  skipped; the intentional stubs are recorded below instead.

## Known Stubs

- `.claude/skills/hw-report/SKILL.md` is an intentional v0.1 stub
  (`metadata.status: stub`, FLOW-07/D-19). It does not write `report.md`,
  transcribe assumptions, or validate the measurement ledger; the manual fallback
  is the template skeleton plus `docs/standards/` once Phase 10 publishes it.
  Promotion is a deferred idea in `09-CONTEXT.md`, not a gap in this plan.
- `.claude/skills/schematic/SKILL.md` is an intentional v0.1 stub. It does not
  open or edit `assets/diagram.json`, validate part placement, or update the pin
  map; the manual fallback is the Wokwi diagram editor plus
  `wokwi-cli lint --offline homeworks/<id>/assets/diagram.json`.
- `.claude/skills/course-index/SKILL.md` is an intentional v0.1 stub. It does not
  answer from live metadata and does not regenerate the index; the manual
  fallback is the generated README region.

## Threat Flags

None - the new surfaces (shared policy prose, stub markers, mirrored `_shared`
file) are the ones the plan's threat register already covers; T-09-05, T-09-11,
T-09-18 and T-09-04 are mitigated in the authored guardrails and stub banners.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The shared policy and the four-stub inventory are in place, so `new-homework`,
  `hw-build` and `hw-flash` can reference `../_shared/guardrails.md` in the next
  wave.
- `uv run scripts/gen_skills.py --check` exits 0 with 13 `UNCHANGED` records, and
  `pre-commit run gen-skills-check --all-files` passes.
- `python3 -m unittest discover scripts/tests` reports 375 tests with 1 skip.
- No blockers.

## Self-Check: PASSED

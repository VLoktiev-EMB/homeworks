---
phase: 09-agent-workflow-and-skills
plan: 06
subsystem: documentation
tags: [agent-skills, rulebook, onboarding, generated-files, drift-gate]

# Dependency graph
requires:
  - phase: 09-agent-workflow-and-skills
    plan: 01
    provides: scripts/gen_skills.py, generated.skills.manifest, the gen-skills-check hook and the narrowed markdownlint surface
  - phase: 05-generated-views
    provides: the committed-manifest generator spine and the check-only hook pattern
provides:
  - the AGENTS.md live skills layout, routing row and two-class generated-file rule
  - the docs/standards/vscode.md 14-hook count and gen-skills-check bullet
affects: [09-07, 09-08, phase-10-report-format]

# Actuals (#2632) — pairs with the plan's estimate to calibrate future estimates.
actuals:
  tokens: 1521
  tasks: 2
  commits: 2

plan_head_before: cd9d3cd54d0e0f6174585d3616e7c0c54af9fa82
plan_head_after: 1f125d9b4df07669cd8beaf657551e73a54e1e9b

tech-stack:
  added: []
  patterns:
    - "one rulebook paragraph names the canonical tree, the generated mirror, its only writer and both drift gates"
    - "the generated-file rule splits build output from a committed generated projection that is regenerated and drift-checked, with the repair command named once"

key-files:
  created: []
  modified:
    - AGENTS.md
    - docs/standards/vscode.md

key-decisions:
  - "The 14-hook count stays review-enforced with the task's exact-token assertion; no derived doc-sync test was added, matching the prose-test prune in 261026-ky7."
  - "The two generated-file classes are resolved in a separate [MUST] bullet rather than by weakening the existing build-output rule, so neither rule contradicts the other."

requirements-completed: [FLOW-01]

coverage:
  - id: D1
    description: "AGENTS.md names the live skills layout, both trees, the only writer, the --check command, the gen-skills-check hook and the lint surface, with no phase placeholder left"
    requirement: FLOW-01
    verification:
      - kind: integration
        ref: "python3 -c text-contract assertion over AGENTS.md"
        status: pass
      - kind: integration
        ref: "pre-commit run markdownlint-cli2 --files AGENTS.md docs/standards/vscode.md"
        status: pass
    human_judgment: false
  - id: D2
    description: "AGENTS.md distinguishes build output from a committed generated projection and names the skills mirror repair command"
    requirement: FLOW-01
    verification:
      - kind: integration
        ref: "python3 -c text-contract assertion over AGENTS.md"
        status: pass
    human_judgment: false
  - id: D3
    description: "docs/standards/vscode.md states 14 commit hooks and lists gen-skills-check with its repair command after the views hook"
    requirement: FLOW-01
    verification:
      - kind: integration
        ref: "python3 -c text-contract assertion over docs/standards/vscode.md"
        status: pass
    human_judgment: false

duration: 2 min
completed: 2026-10-26
status: complete
---

# Phase 9 Plan 06: Rulebook and Onboarding Skills Layout Summary

**The canonical rulebook and the editor onboarding guide now name the live skills layout,
its drift gate and repair command, and the rulebook separates a committed generated
projection from build output.**

## Performance

- **Duration:** 2 min
- **Started:** 2026-10-26T21:26:21Z
- **Completed:** 2026-10-26T21:28:01Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- `AGENTS.md` replaces the stale "project skills are planned" sentence with the live
  layout: `.claude/skills/<name>/SKILL.md` as the canonical authored tree,
  `.agents/skills/` as its generated committed mirror, `scripts/gen_skills.py` as the only
  writer, and both `uv run scripts/gen_skills.py --check` and the `gen-skills-check` hook
  as the drift gate.
- The `## Repository layout` inventory now names both skill trees, the generator and
  `generated.skills.manifest`; the generated-paths paragraph names both ledgers and both
  committed projections.
- The routing-table row points at the live paths and the repair command, and no
  `(planned, Phase 9)` text remains anywhere in the file.
- A new `[MUST]` `[ENFORCED: pre-commit]` bullet in `### Assets and generated files`
  resolves the two classes: build output is never committed, while a committed generated
  projection is regenerated and drift-checked, so a hand edit is never the fix.
- `docs/standards/vscode.md` now says `14 hooks run on commit and 2 on push.` and lists
  `gen-skills-check` with the repair command `uv run scripts/gen_skills.py`.

## Task Commits

Each task was committed atomically:

1. **Task 1: Name the live skills layout in `AGENTS.md`** - `9f0e2fd` (docs)
2. **Task 2: Update the editor guide's hook count and hook list** - `1f125d9` (docs)

**Plan metadata:** this SUMMARY commit.

## Files Created/Modified

- `AGENTS.md` - live skills layout, repository-layout bullets, both-ledger generated-paths
  paragraph, routing row, lint-surface sentence and the two-class generated-file bullet
- `docs/standards/vscode.md` - 14-hook count and the `gen-skills-check` bullet

## Decisions Made

- The 14-hook count remains review-enforced with the exact-token assertion in the task,
  rather than a derived doc-sync test: the repository pruned that test class in
  `261026-ky7`, and a new prose guard would repeat the mistake.
- The two generated-file classes are stated as a new bullet. The existing build-output
  rule keeps its exact wording, so the new rule resolves the ambiguity without restating
  or weakening anything.
- The lint surface is stated where a reader meets the layout: authored
  `.claude/skills/**` Markdown is linted, while the generated `.agents/**` mirror and the
  generated `.claude/CLAUDE.md` adapter are excluded.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- The environment routes git through an rtk worktree guard that refuses compound git
  commands; each git operation was run as a plain, separate `/usr/bin/git` command. All
  commits ran with the normal pre-commit hooks and none used `--no-verify`.

## Known Stubs

None - both edits are authored Markdown; no stub was introduced.

## Threat Flags

None - the plan's threat register already covers both surfaces (a stale rule causing a
wrong repair action, and a contributor hand-editing the generated mirror).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The rulebook and the onboarding guide now agree with the generator, the ledger and the
  `gen-skills-check` hook that wave 1 shipped.
- `python3 -m unittest discover scripts/tests` reports 375 tests with 1 skip and
  `OK`; markdownlint is clean on both edited files.
- No blockers. The remaining Phase 9 plans can add canonical skills without touching the
  documentation surface again.

## Self-Check: PASSED

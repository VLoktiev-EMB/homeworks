---
phase: 09-agent-workflow-and-skills
plan: 07
subsystem: documentation
tags: [agent-skills, generated-adapter, decision-record, phase-gate]

# Dependency graph
requires:
  - phase: 09-agent-workflow-and-skills
    plan: 01
    provides: the canonical .claude/skills/ tree, the generated .agents/skills/ mirror, gen_skills.py and the gen-skills-check hook
  - phase: 09-agent-workflow-and-skills
    plan: 06
    provides: the AGENTS.md live skills layout and the two-class generated-file rule
provides:
  - the regenerated GSD:skills block in .claude/CLAUDE.md listing all seven skills
  - the accepted docs/decisions/README.md row for the canonical/mirror layout
affects: [09-08, /gsd-verify-work, phase-10-report-format]

# Actuals (#2632) — pairs with the plan's estimate to calibrate future estimates.
actuals:
  tokens: 1053
  tasks: 2
  commits: 2

plan_head_before: 61c90abbbca1bb96ba7ed66069ecdd208053fabd
plan_head_after: a523c229d9c2161e767aa94e528656a017e2a7d7

tech-stack:
  added: []
  patterns:
    - "a generator-owned marker block is replaced by slicing the generator's --output, never by an edit inside the markers"
    - "a costly layout decision is one table row, with the reason in the Why column and the status accepted"

key-files:
  created: []
  modified:
    - .claude/CLAUDE.md
    - docs/decisions/README.md

key-decisions:
  - "The adapter's GSD:skills block was regenerated with the GSD 1.16.0 generator through `--output`, then spliced by a stdlib script; only the skills slice was used, so no GSD:project/stack/conventions/architecture section entered the adapter."
  - "The decision row's Change cost cell is the bare word `costly` and its justification lives in the Why column; the plan's action put the justification in the cost cell while its verify asserted `| costly |`, and the machine check was the binding contract."
  - "The layout is recorded as one table row with no ADR file, matching D-01/D-05 and the repository's table-first decision rule."

requirements-completed: [FLOW-01]

coverage:
  - id: D1
    description: "The GSD:skills block lists exactly seven skills with descriptions and .claude/skills/<name>/SKILL.md paths, and every byte outside the block is identical to HEAD"
    requirement: FLOW-01
    verification:
      - kind: integration
        ref: "python3 -I /tmp/verify_task1.py (marker-pair, seven-row and outside-block identity assertions)"
        status: pass
    human_judgment: false
  - id: D2
    description: "docs/decisions/README.md carries one accepted, costly, dated row naming the canonical tree, the generated mirror and generated.skills.manifest, with no ADR file"
    requirement: FLOW-01
    verification:
      - kind: integration
        ref: "python3 -I /tmp/verify_task2.py (decision-row text assertion)"
        status: pass
    human_judgment: false
  - id: D3
    description: "The full local phase gate is green: all 14 pre-commit hooks, the metadata checker and the 375-test Python suite"
    requirement: FLOW-01
    verification:
      - kind: integration
        ref: "pre-commit run --all-files"
        status: pass
      - kind: integration
        ref: "uv run scripts/check_metadata.py"
        status: pass
      - kind: integration
        ref: "python3 -m unittest discover scripts/tests"
        status: pass
    human_judgment: false

duration: 1 min
completed: 2026-10-26
status: complete
---

# Phase 9 Plan 07: Claude Adapter Regeneration and Layout Decision Summary

**The Claude Code adapter's generator-owned skills block now lists all seven live project
skills, the canonical/mirror layout is recorded as one accepted decision row, and the full
local phase gate is green.**

## Performance

- **Duration:** 1 min
- **Started:** 2026-10-26T21:42:08Z
- **Completed:** 2026-10-26T21:43:30Z
- **Tasks:** 2
- **Files modified:** 2

## Generator invocation (recorded per the plan's must-have)

- Tool: `~/.claude/gsd-core/bin/gsd_run`, GSD **1.16.0** (`~/.claude/gsd-core/package.json`).
- `gsd_run` is **not** on `PATH`; it was invoked by absolute path.
- Exact command:
  `~/.claude/gsd-core/bin/gsd_run query generate-claude-md --output /tmp/skills-claude-md.md`
  run from the worktree root.
- `--output` support was re-confirmed at `~/.claude/gsd-core/bin/lib/profile-output.cjs:1070`
  (`let outputPath = options.output;`).
- The temporary output is 53.9 kB and lives outside the repository; it is not committed. Its
  reported sections were `generated: [project, stack, skills, workflow]`, `fallback:
  [conventions, architecture]`; only the `GSD:skills` slice was spliced.

## Accomplishments

- Preflight of the generator output: exactly one `<!-- GSD:skills-start` marker, exactly one
  `<!-- GSD:skills-end -->` marker, and exactly seven discovery rows with the expected
  `.claude/skills/<name>/SKILL.md` path shape before anything was spliced.
- `.claude/CLAUDE.md` replaces the stale "No project skills found" sentence with a
  seven-row table naming `course-index`, `hw-build`, `hw-flash`, `hw-report`,
  `new-homework`, `schematic` and `simulate`, each with its description and canonical path.
- The diff outside the generator-owned block is empty: the `@AGENTS.md` import, the adapter
  prose, the `GSD:workflow` block and the `GSD:profile` block are byte-identical to `HEAD`,
  and no extra managed section was added.
- `docs/decisions/README.md` gains one accepted row dated `2026-10-26` naming the canonical
  `.claude/skills/` tree, the committed generated `.agents/skills/` mirror and the
  `generated.skills.manifest` drift ledger, with change cost `costly`. No ADR file was
  created.
- Full phase gate green: all 14 pre-commit hooks passed, `uv run scripts/check_metadata.py`
  printed `PASS`, and `python3 -m unittest discover scripts/tests` reported
  `Ran 375 tests ... OK (skipped=1)`.

## Task Commits

Each task was committed atomically:

1. **Task 1: Regenerate the GSD-owned project-skills block** - `db85422` (docs)
2. **Task 2: Record the layout decision and run the full phase gate** - `a523c22` (docs)

**Plan metadata:** this SUMMARY commit.

## Files Created/Modified

- `.claude/CLAUDE.md` - the `GSD:skills` block only: stale no-skills sentence replaced by the
  generator's seven-row table.
- `docs/decisions/README.md` - one new dated accepted row for the canonical/mirror layout.

## Decisions Made

- The generator was run only with `--output` into `/tmp`, then the `GSD:skills` slice was
  copied by a small stdlib Python splice. Running it in the working tree would have added the
  `project`, `stack`, `conventions` and `architecture` fallbacks this repository deliberately
  omits, so the splice keeps the adapter unchanged outside the owned block.
- The decision's Change cost cell is the bare word `costly`, with "the hook, the ledger and
  every skill path name the layout" moved into the Why column. The plan's action placed that
  justification inside the cost cell, but its `<verify>` asserted the exact token `| costly |`;
  the machine check was treated as binding. Recorded below as a reconciliation deviation.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Reconciled the decision row's cost cell with its verify assertion**
- **Found during:** Task 2
- **Issue:** The task action specified the Change cost cell as
  `costly — the hook, the ledger and every skill path name the layout`, while the task's
  `<verify>` asserted the literal substring `| costly |`, which that longer cell cannot match.
- **Fix:** The Change cost cell is `costly`; the justification is preserved in the Why column.
  Both the action's requirement (the cost is `costly`) and the verify assertion now hold.
- **Files modified:** `docs/decisions/README.md`
- **Commit:** `a523c22`

**2. [Rule 3 - Blocking] Git had to be invoked as a plain `/usr/bin/git` command**
- **Found during:** Both tasks
- **Issue:** The environment routes git through an rtk worktree guard that refuses compound
  commands and inline `python3 -c` programs containing git, so the plan's inline verify
  commands could not run verbatim.
- **Fix:** Each git operation ran as a plain `/usr/bin/git` command, and the two verify
  assertions were run as short stdlib scripts in `/tmp` (the same assertions, unchanged in
  substance). No hook was bypassed.
- **Files modified:** none (execution mechanics only)
- **Commit:** n/a

## Issues Encountered

- The rtk worktree guard refused `git` inside compound shell constructs and `python3 -c`
  programs that name git; all git calls were therefore run as separate plain `/usr/bin/git`
  commands, matching the note in `09-06-SUMMARY.md`. All commits ran the normal pre-commit
  hooks; none used `--no-verify`.

## Known Stubs

None - both edits are generated/authored Markdown; no stub was introduced.

## Threat Flags

None - the plan's threat register already covers both surfaces (a hand-patched generator block
and a partial skills regeneration), and neither surfaced during execution.

## User Setup Required

None - the generator is the already-installed GSD 1.16.0; no external service or dependency
was added.

## Next Phase Readiness

- The adapter now agrees with the seven-skill tree that wave 1 shipped, so a fresh Claude
  Code session is pointed at every live skill.
- The canonical/mirror layout is durably recorded, closing the decision side of D-01/D-05.
- The full local gate is green; no blockers. STATE.md and ROADMAP.md were intentionally left
  untouched for the orchestrator to update after the wave merges.

## Self-Check: PASSED

- `FOUND: .planning/phases/09-agent-workflow-and-skills/09-07-SUMMARY.md`
- `FOUND: .claude/CLAUDE.md`
- `FOUND: docs/decisions/README.md`
- `FOUND: db85422` (Task 1 commit is an ancestor of HEAD)
- `FOUND: a523c22` (Task 2 commit is an ancestor of HEAD)

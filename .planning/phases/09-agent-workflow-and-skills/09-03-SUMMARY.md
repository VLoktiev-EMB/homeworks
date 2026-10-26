---
phase: 09-agent-workflow-and-skills
plan: 03
subsystem: tooling
tags: [agent-skills, new-homework, question-bank, state-file, checkpoints, generated-mirror]

# Dependency graph
requires:
  - phase: 09-agent-workflow-and-skills
    plan: 01
    provides: scripts/gen_skills.py, the generated.skills.manifest ledger and the check-only gen-skills-check hook
  - phase: 09-agent-workflow-and-skills
    plan: 02
    provides: .claude/skills/_shared/guardrails.md, the shared policy every implemented skill reads
  - phase: 04.2-tracer-homework-1-3
    provides: F-01 idempotence and UV_CACHE_DIR, F-04 private-library manifest, F-05 native test facts
provides:
  - .claude/skills/new-homework/SKILL.md, the guided and one-shot conversation contract
  - .claude/skills/new-homework/references/question-bank.md, the eight-topic prose intake
  - .claude/skills/new-homework/references/state-file.md, the .skill-state schema and write discipline
  - the new-homework CHANGELOG.md and LESSONS.md records
  - their generated .agents/skills mirror and the updated generated.skills.manifest ledger
affects: [09-04, 09-05, 09-06, 09-07, 09-08, phase-10-report-format]

# Actuals (#2632) — pairs with the plan's estimate to calibrate future estimates.
# Same estimateTokens scale (chars/4 over the realized diff), never a harness token count.
actuals:
  tokens: 11700
  tasks: 3
  commits: 2

plan_head_before: 9b7f1ed5fddae3f3837e8156635f515fe9e48a16
plan_head_after: 402b42e6265c327a13a64bde10ccaa6392e70a8a

tech-stack:
  added: []
  patterns:
    - prose question bank with one default, one conditional branch and one state key per topic
    - one documented state shape that separates block pauses from the three named checkpoints
    - the skill writes the state file before every checkpoint menu and deletes it only after the report checkpoint

key-files:
  created:
    - .claude/skills/new-homework/SKILL.md
    - .claude/skills/new-homework/references/question-bank.md
    - .claude/skills/new-homework/references/state-file.md
    - .claude/skills/new-homework/CHANGELOG.md
    - .claude/skills/new-homework/LESSONS.md
  modified:
    - generated.skills.manifest

key-decisions:
  - "Task 1 and Task 2 landed in one commit because scripts/gen_skills.py refuses a skill directory without SKILL.md, so a references-only tree cannot pass the gen-skills-check gate."
  - "The question bank keeps exactly eight H2 topics and puts the closing 'what the answers mean', provenance and friction material after a thematic break, so `mode` stays the first bank question (D-11)."
  - "The state reference names the block pause and the three checkpoints as different write paths: block pauses update blocks[] and next_block, and only intake, code and report append to checkpoints[]."

patterns-established:
  - "A prose bank states, for every topic, its question, its default, its conditional branch and the state key it writes."
  - "A checkpoint record is written before the menu, not after it, and is deleted only after the last checkpoint succeeds."
  - "Every `uv run` in a skill carries UV_CACHE_DIR=${TMPDIR:-/tmp}/uv-cache, because F-01 names the cache rather than one command."

requirements-completed: [FLOW-02, FLOW-03, FLOW-04, FLOW-05]

coverage:
  - id: D1
    description: "The eight-topic prose intake covers mode, board, framework, language, specification, simulation, tests and deliverables, each with its default, branch and state key, plus the pre-scaffold provenance gate"
    requirement: FLOW-02
    verification:
      - kind: integration
        ref: "grep -c '^## ' .claude/skills/new-homework/references/question-bank.md -> 8"
        status: pass
    human_judgment: true
    rationale: "D-12 makes eight-topic coverage review-enforced and forbids a doc-sync test; the heading count proves the shape, not the wording."
  - id: D2
    description: "state-file.md documents every D-13 field, the enumerated values, the block-versus-checkpoint vocabulary, the resume rule, the git-failure fallback and the atomic-write discipline"
    requirement: FLOW-04
    verification:
      - kind: integration
        ref: "uv run scripts/gen_skills.py --check"
        status: pass
    human_judgment: true
    rationale: "D-18 declines a content validator; the generator proves only that the mirror is in sync with the authored bytes."
  - id: D3
    description: "SKILL.md runs the guided loop and the one-shot mode over the same bank, with the exact pause menus, the provenance gate, the five blocks and the conflict record"
    requirement: FLOW-03
    verification:
      - kind: integration
        ref: "pre-commit run markdownlint-cli2 --files .claude/skills/new-homework/SKILL.md"
        status: pass
      - kind: integration
        ref: "uv run scripts/gen_skills.py --check"
        status: pass
    human_judgment: true
    rationale: "The conversation contract is prose; the phase dry run in 09-08 is the behavioural evidence, and the exact menus are review-enforced."
  - id: D4
    description: "The companion records are dated, state the scaffold idempotence rule, and the five-file canonical directory is mirrored with a drift-clean ledger"
    requirement: FLOW-05
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

duration: 2 min
completed: 2026-10-26
status: complete
---

# Phase 9 Plan 03: new-homework Guided and One-Shot Workflow Summary

**An eight-topic prose intake, a five-block guided loop and a three-checkpoint state record make `new-homework` the repository's first fully implemented skill, wired to the scaffold, the view generator and the metadata checker.**

## Performance

- **Duration:** 2 min
- **Started:** 2026-10-26T21:31:24Z
- **Completed:** 2026-10-26T21:33:31Z
- **Tasks:** 3 (committed as 2, see Deviations)
- **Files modified:** 11

## Accomplishments

- `references/question-bank.md` is an eight-topic prose bank in the D-11 order — `mode`,
  `board`, `framework`, `language`, `specification`, `simulation`, `tests`,
  `deliverables` — with the homework id acquired and validated before the bank and each
  topic naming its question, default, branch and state key.
- The bank is honest about the scaffold: only `esp32-s3-devkitc-1` can be created,
  `language` is `cpp` for both templates, and any other board stops with an
  unsupported-scaffold escalation that names the manual path.
- `references/state-file.md` fixes one `.skill-state/<id>.json` shape with every D-13
  field, separates block pauses from the three named checkpoints, and states the resume,
  git-failure, atomic-write, symlink and delete/keep rules.
- `SKILL.md` runs the guided loop explain, write, explain, run, scenario, optional
  terminology check, pause, with the exact `[Продовжити | Поясни глибше | Стоп]` menu,
  and the one-shot mode over the same bank without block pauses.
- The pre-scaffold provenance gate keeps `homework.status: planned` while any of the four
  values is `TODO`, and the report block owns the BOM and calculation sub-sections rather
  than introducing a sixth block.
- The canonical directory and its generated mirror both carry five files, and
  `uv run scripts/gen_skills.py --check` is clean.

## Task Commits

Each task's work was committed atomically:

1. **Tasks 1 and 2: the question bank, the state contract and the workflow** - `07c6f4a` (feat)
2. **Task 3: companion records and the regenerated mirror** - `402b42e` (feat)

**Plan metadata:** this SUMMARY commit.

## Files Created/Modified

- `.claude/skills/new-homework/references/question-bank.md` - the eight-topic prose intake
- `.claude/skills/new-homework/references/state-file.md` - the state schema and write discipline
- `.claude/skills/new-homework/SKILL.md` - the guided and one-shot workflow contract
- `.claude/skills/new-homework/CHANGELOG.md` - the dated 0.1 delivery record
- `.claude/skills/new-homework/LESSONS.md` - the scaffold-idempotence lesson
- `.agents/skills/new-homework/**` - the generated mirror of all five files
- `generated.skills.manifest` - the updated mirror ledger

## Decisions Made

- Tasks 1 and 2 were committed together because `scripts/gen_skills.py` refuses a skill
  directory without `SKILL.md` (`ERROR: ... a skill directory must contain SKILL.md`), so
  the references could not pass the pre-commit `gen-skills-check` gate on their own.
- The closing "what the answers mean", provenance and friction paragraphs sit after a
  thematic break rather than under a ninth H2, so the bank keeps exactly the eight
  required topics.
- The bank writes `mode` as a top-level state key and every other answer under `intake.*`,
  matching the schema the state reference documents.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Tasks 1 and 2 could not be committed separately**
- **Found during:** Task 1 commit
- **Issue:** The `gen-skills-check` pre-commit hook runs
  `python scripts/gen_skills.py --check` over the whole tree, and the generator exits 2
  with `ERROR: .claude/skills/new-homework: a skill directory must contain SKILL.md`. A
  commit carrying only the two references therefore cannot pass the gate, so the plan's
  task split is not representable in git history.
- **Fix:** Wrote `SKILL.md` (the Task 2 deliverable) before the first commit and landed
  Task 1 and Task 2 in one atomic commit, then kept Task 3 as its own commit. All three
  tasks' acceptance criteria are satisfied in the tree.
- **Files modified:** `.claude/skills/new-homework/SKILL.md`, both references, the
  three-file mirror and `generated.skills.manifest`
- **Verification:** `uv run scripts/gen_skills.py --check` exits 0; the commit ran the
  full pre-commit surface with no skip and no `--no-verify`.
- **Committed in:** `07c6f4a`

---

**Total deviations:** 1 auto-fixed (blocking)
**Impact on plan:** No scope change and no unverified content. The only cost is that the
task-to-commit mapping is 2 rather than 3.

## Issues Encountered

- The worktree's rtk git guard refuses compound `git` invocations, so every git call ran
  as a plain `/usr/bin/git` command. No hook was bypassed.
- The `uv run --with markdownlint-cli2` probe failed because the package is not on the
  configured index; the pinned pre-commit hook supplied the linter instead, and it passed.

## Known Stubs

None - `new-homework` is an implemented skill, not a stub. The four stubs in this phase
are owned by plan 09-02.

## Threat Flags

None - the new surfaces (id and template validation, the state write path, the token
boolean) are the ones the plan's threat register already covers (T-09-03, T-09-19,
T-09-07, T-09-12, T-09-13).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `hw-build`, `hw-flash` and the dry run can now reference the implemented skill and its
  two references; the dry run in 09-08 is the behavioural evidence for the conversation
  contract.
- `uv run scripts/gen_skills.py --check` exits 0 with every record `UNCHANGED`,
  `pre-commit run gen-skills-check --all-files` passes, and
  `python3 -m unittest discover scripts/tests` reports 375 tests with 1 skip.
- No blockers.

## Self-Check: PASSED

- `07c6f4a` and `402b42e` are ancestors of HEAD; both trees' five files exist and are
  non-empty; the mirror check and the tooling suite are green.

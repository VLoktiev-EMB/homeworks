---
phase: 09-agent-workflow-and-skills
plan: 01
subsystem: tooling
tags: [agent-skills, generator, pre-commit, markdown, affected-paths, drift-gate]

# Dependency graph
requires:
  - phase: 05-generated-views
    provides: the plan-then-apply generator spine, the committed manifest shape and the check-only hook pattern
  - phase: 04-metadata-contract
    provides: scripts/metadata/errors.py, paths.resolve_root and render.read_regular_text
  - phase: 08-fast-ci
    provides: the CI meta job that runs the whole pre-commit surface with --all-files
provides:
  - scripts/gen_skills.py, the only owner of the .agents/skills mirror
  - the committed generated.skills.manifest ledger
  - the canonical .claude/skills/simulate stub and its generated mirror
  - the check-only gen-skills-check pre-commit hook
  - .gitignore and scripts/affected.py policy for the skill trees, ledger and state directory
affects: [09-02, 09-03, 09-04, 09-05, 09-06, 09-07, 09-08, phase-10-report-format]

# Actuals (#2632) — pairs with the plan's estimate to calibrate future estimates.
actuals:
  tokens: 18000
  tasks: 3
  commits: 4

plan_head_before: 9cf63651274d519e616bf068c0a2ba1faa16cf96
plan_head_after: d37c02fe12652d84de53071ae8b62b9cca91a32d

tech-stack:
  added: []
  patterns:
    - line-preserving YAML frontmatter projection (top-level block scan, verbatim emission, no serializer)
    - marker-position orphan deletion (first line for non-SKILL.md, the line after the closing fence for SKILL.md)
    - deterministic ledger with path, owner, source, mode, sha256 and bytes, sorted, never self-listing

key-files:
  created:
    - scripts/gen_skills.py
    - scripts/tests/test_gen_skills.py
    - generated.skills.manifest
    - .claude/skills/simulate/SKILL.md
    - .claude/skills/simulate/CHANGELOG.md
    - .claude/skills/simulate/LESSONS.md
    - .agents/skills/simulate/SKILL.md
    - .agents/skills/simulate/CHANGELOG.md
    - .agents/skills/simulate/LESSONS.md
  modified:
    - scripts/tests/temp_root.py
    - .gitignore
    - .pre-commit-config.yaml
    - scripts/affected.py
    - scripts/tests/test_affected.py
    - scripts/tests/test_tooling_config.py

key-decisions:
  - "The generated-marker separator is conditional: a canonical body that already begins with the blank line after its fence supplies the single separator, so the body bytes stay unchanged and no double blank line appears."
  - "The markdownlint exclude landed one commit before the simulate skill, because the generated mirror would otherwise fail the hook at the skill commit; the remaining task-3 edits stayed in their own commit."
  - "A separate generated.skills.manifest implements the D-04 discretion grant, with owner 'skills' and mode 'whole' validated as literals on load."

patterns-established:
  - "Line-preserving frontmatter projection: scan top-level blocks, emit portable blocks verbatim, inject the explicit-only banner exactly when disable-model-invocation was dropped."
  - "One header policy for every non-SKILL.md mirror file: marker, newline, canonical bytes; a mirrored reference is not byte-identical to its source, its bytes from line 2 are."
  - "A check-only generator hook watches its generator, its metadata helpers, both skill trees and the ledger, and never regenerates or stages."
  - "A skills-only or generator-only diff selects no build, while an unrecognised path still widens."

requirements-completed: [FLOW-01, FLOW-07]

coverage:
  - id: D1
    description: "scripts/gen_skills.py projects the canonical skill tree into a transformed, byte-stable .agents/skills mirror with --check, --json and --dir"
    requirement: FLOW-01
    verification:
      - kind: unit
        ref: "scripts/tests/test_gen_skills.py"
        status: pass
      - kind: integration
        ref: "uv run scripts/gen_skills.py --check"
        status: pass
    human_judgment: false
  - id: D2
    description: "generated.skills.manifest is a sorted, digest-correct, non-self-listing ledger of every mirror file"
    requirement: FLOW-01
    verification:
      - kind: unit
        ref: "scripts/tests/test_gen_skills.py#ManifestTests"
        status: pass
    human_judgment: false
  - id: D3
    description: "The simulate stub names the manual wokwi-cli command, the offline lint form, the Wokwi quota and the evidence boundary"
    requirement: FLOW-07
    verification: []
    human_judgment: true
    rationale: "D-18 makes skill content review-enforced; no machine check asserts the stub wording, only that its mirror is in sync."
  - id: D4
    description: "The gen-skills-check hook, the markdownlint surface and the no-build-impact policy are wired and green"
    requirement: FLOW-01
    verification:
      - kind: unit
        ref: "scripts/tests/test_tooling_config.py#MarkdownlintSurfaceTests and HookLayeringTests"
        status: pass
      - kind: unit
        ref: "scripts/tests/test_affected.py#NoBuildImpactTests"
        status: pass
      - kind: integration
        ref: "pre-commit run gen-skills-check --all-files"
        status: pass
    human_judgment: false

duration: 10 min
completed: 2026-10-26
status: complete
---

# Phase 9 Plan 01: Skills Mirror Generator and First Skill Summary

**A stdlib-only generator projects authored `.claude/skills/` into a transformed,
committed `.agents/skills/` mirror with a digest ledger, and the `simulate` stub plus
its drift gate ship together.**

## Performance

- **Duration:** 10 min
- **Started:** 2026-10-26T21:13:00Z
- **Completed:** 2026-10-26T21:23:21Z
- **Tasks:** 3
- **Files modified:** 15

## Accomplishments

- `scripts/gen_skills.py` is the only owner of the mirror: it discovers the canonical
  tree, keeps portable frontmatter blocks verbatim, drops the Claude-only fields,
  injects the explicit-only invocation banner when `disable-model-invocation` was
  dropped, and writes atomically.
- The transform preserves a column-0 `#` comment, refuses an unknown field, an
  unclosed fence, a bad skill slug, a `name`/directory mismatch, a `_shared/SKILL.md`,
  a reference deeper than one level, an absent canonical root and every symlink with
  exit 2 and one `ERROR:` line.
- `generated.skills.manifest` is committed, sorted, digest-correct and never lists
  itself; `--check` reports `MODIFIED`, `DELETED` and `ORPHAN` and writes nothing.
- The `simulate` stub ships both as authored prose and as its generated projection,
  marking itself `metadata.status: stub` and naming the manual `wokwi-cli` command.
- `gen-skills-check` runs `python scripts/gen_skills.py --check` at pre-commit, the
  markdownlint surface now lints authored skills but not the generated mirror, and a
  skills-only or generator-only diff selects no build.

## Task Commits

Each task was committed atomically:

1. **Task 1: End-to-end canonical → mirror transform** - `ac77c50` (feat; the
   separator refinement is folded into this amended commit)
2. **Blocking markdownlint surface fix** - `2db6b8b` (fix; deviation, see below)
3. **Task 2: Commit the `simulate` stub and its generated mirror** - `97f8840` (feat)
4. **Task 3: Wire the drift gate and the affected-path policy** - `d37c02f` (feat)

**Plan metadata:** this SUMMARY commit.

## Files Created/Modified

- `scripts/gen_skills.py` - the only mirror owner, with `--check`, `--json` and `--dir`
- `scripts/tests/test_gen_skills.py` - 39 stdlib-only integration tests through `uv run`
- `scripts/tests/temp_root.py` - the new `write_skills_root` fixture builder
- `.gitignore` - re-includes `generated.skills.manifest`, ignores `.skill-state/`
- `.claude/skills/simulate/{SKILL,CHANGELOG,LESSONS}.md` - the canonical stub
- `.agents/skills/simulate/{SKILL,CHANGELOG,LESSONS}.md` - the generated projection
- `generated.skills.manifest` - the committed mirror ledger
- `.pre-commit-config.yaml` - `gen-skills-check`, the narrowed markdownlint exclude and
  `.skill-state` in the `no-generated-files` pathspec
- `scripts/affected.py` - the skills tree, ledger, state directory and generator are
  no-build-impact paths
- `scripts/tests/test_affected.py` - the four new no-build-impact paths
- `scripts/tests/test_tooling_config.py` - `gen-skills-check` in the stage tuple and
  the new `MarkdownlintSurfaceTests`

## Decisions Made

- The mirror separator is conditional rather than unconditional. Adding one `\n`
  after the banner produced two blank lines because the canonical body already begins
  with the blank line after its closing fence; the conditional keeps exactly one blank
  line and leaves the body bytes unchanged.
- The markdownlint surface fix was committed before the skill because the generated
  mirror is authored nowhere and must not be linted; leaving it to task 3 made the
  task 2 commit unrepresentable.
- The real-tree drift check is clean (`uv run scripts/gen_skills.py --check` exits 0
  with four `UNCHANGED` records), so the committed mirror needs no regeneration.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] The transform emitted two blank lines before the mirrored body**
- **Found during:** Task 2 (first real skill generation)
- **Issue:** The reference transform always appended `"\n"` after the banner, but a
  canonical body already starts with the blank line after its fence, so the mirror
  carried two empty lines and contradicted the plan's "one blank line and the
  untouched body".
- **Fix:** `_transform_skill` adds the separator only when the body does not already
  begin with a newline; the body bytes are never trimmed.
- **Files modified:** `scripts/gen_skills.py`
- **Verification:** the 39-test suite passes, the real-tree `--check` is clean, and the
  mirror now shows one blank line before `# Simulate (stub)`.
- **Committed in:** `ac77c50` (folded into the amended Task 1 commit)

**2. [Rule 3 - Blocking] The generated mirror failed markdownlint at the Task 2 commit**
- **Found during:** Task 2 commit
- **Issue:** `.agents/skills/simulate/SKILL.md` failed `MD041` because the repository
  still excluded only `.planning/` and `.claude/`; the `.agents/` exclusion was
  scheduled for Task 3.
- **Fix:** landed the markdownlint exclude change early as its own atomic commit, then
  committed the skill and mirror separately. Task 3's remaining edits kept their own
  commit.
- **Files modified:** `.pre-commit-config.yaml`
- **Verification:** `pre-commit run markdownlint-cli2 --files .claude/skills/simulate/SKILL.md`
  passes, and the generated mirror is excluded.
- **Committed in:** `2db6b8b`

**3. [Plan verification literal] The Task 3 verify assertion contradicts its action**
- **Found during:** Task 3
- **Issue:** The `<verify>` block asserts the literal `^(\.planning/|\.claude/|\.agents/)`,
  which would exclude `.claude/skills/**`; the action and acceptance criterion require
  authored skill prose to be linted and only the generated mirror and adapter excluded.
- **Fix:** implemented the action's `^(\.planning/|\.agents/|\.claude/(?!skills/))` and
  verified the semantics behaviorally with `MarkdownlintSurfaceTests` plus an adapted
  literal assertion.
- **Files modified:** `.pre-commit-config.yaml`, `scripts/tests/test_tooling_config.py`
- **Verification:** `re.search` returns no match for `.claude/skills/simulate/SKILL.md`
  and a match for `.claude/CLAUDE.md` and `.agents/skills/simulate/SKILL.md`; the
  tooling suite passes.
- **Committed in:** `2db6b8b` (config) and `d37c02f` (test)

---

**Total deviations:** 2 auto-fixed (1 bug, 1 blocking) plus 1 plan-literal correction.
**Impact on plan:** All three were necessary for the mirror contract and for the commit
gate to pass. No scope creep; no hook was bypassed and no `--no-verify` was used.

## Issues Encountered

- The environment routes git through an rtk worktree guard that refuses plain `git`
  write subcommands; `/usr/bin/git` is the accepted form inside the worktree. All
  commits ran with the normal pre-commit hooks and none used `--no-verify`.
- During Task 2, an attempted commit left the skill files staged and they were swept
  into the config commit; the commit was soft-reset and split so each change is atomic
  again. The final history has no mixed commit.

## Known Stubs

- `.claude/skills/simulate/SKILL.md` is an intentional v0.1 stub (`metadata.status: stub`,
  FLOW-07/D-19). It does not run a simulation, read serial output or write a ledger row;
  the manual `wokwi-cli` command and the offline lint form are the documented fallback.
  Promotion is a deferred idea in `09-CONTEXT.md`, not a gap in this plan.

## Threat Flags

None - the new surfaces (path construction, symlink refusal, orphan deletion, mirror
projection) are the ones the plan's threat register already covers.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The generator, ledger, hook and affected-path policy are in place, so the remaining
  skill plans can author canonical directories and regenerate the mirror.
- `python3 -m unittest discover scripts/tests` reports 375 tests with 1 skip (the
  clangd guide test), and the full `pre-commit run --all-files` surface is green.
- No blockers. The next plan (09-02) can extend the canonical tree without touching
  the generator.

## Self-Check: PASSED

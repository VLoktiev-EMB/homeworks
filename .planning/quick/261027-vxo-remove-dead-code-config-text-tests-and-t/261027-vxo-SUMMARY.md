---
phase: quick-261027-vxo
plan: "01"
subsystem: tooling
tags: [pre-commit, skills-mirror, dead-code, test-pruning, platformio]

requires:
  - phase: quick-261026-ky7
    provides: the precedent that prose-only guards are removed while behavioral coverage stays

provides:
  - four dead paths removed with no tracked reference outside the ADR archive
  - seven skills carrying only SKILL.md, references/ and _shared/guardrails.md
  - regenerated .agents/skills mirror and 11-entry generated.skills.manifest
  - template build output removed, ten tracked scaffold files intact
  - one atomic Conventional Commit carrying the trim

affects: [skill-authoring, pre-commit-gate, ci-workflow-contract]

actuals:
  tokens: 38000
  tasks: 3
  commits: 1
  plan_head_before: 12ed5eb7c1a2934ea66fad49b12eb16cd25e08d1
  plan_head_after: 61c0100d83cc2bb28700ab2c5b5eade419446416

tech-stack:
  added: []
  patterns: [generator-owned mirror, explicit-path staging, atomic trim commit]

key-files:
  created: []
  modified:
    - scripts/tests/ (four modules removed, thirteen survivors intact)
    - .claude/skills/hw-build/SKILL.md
    - .claude/skills/hw-flash/SKILL.md
    - .claude/skills/new-homework/SKILL.md
    - .claude/skills/hw-build/references/repair-loop.md
    - .agents/skills/ (four mirror files rewritten, eighteen orphans deleted)
    - generated.skills.manifest
    - AGENTS.md
    - .yamllint.yaml

key-decisions:
  - "The repository keeps only what directly affects the homework artifact: the site-guarding scripts, the reviewer-testing script, the two configuration-text test modules and the fourteen skill process documents are gone."
  - "The ADR archive keeps its historical references to the deleted test module; AGENTS.md forbids rewriting an ADR body and explicitly allows a named path to no longer exist."
  - "The .yamllint policy comment lost its now-false assertion about test_ci_workflows; the linter policy itself is unchanged."
  - "The whole trim lands as one atomic commit, as the plan's Task 3 verification requires; a per-task split would leave Task 3 with nothing to commit."

patterns-established:
  - "A canonical deletion is always followed by exactly one gen_skills.py run, never a hand edit of the mirror."
  - "A dangling reference to a deleted path is repaired at the config-text level, but never inside an ADR body."

requirements-completed: []

coverage:
  - id: D1
    description: "The two dead scripts and the two configuration-text test modules are absent and unreferenced outside the ADR archive."
    verification:
      - kind: other
        ref: "test ! -e scripts/ci/check_lfs_pointers.sh && test ! -e scripts/review_smoke_test.sh && test ! -e scripts/tests/test_tooling_config.py && test ! -e scripts/tests/test_ci_workflows.py"
        status: pass
      - kind: unit
        ref: "python3 -m unittest discover scripts/tests — Ran 397 tests / OK (skipped=1)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The fourteen skill process documents are gone from both trees, no prose pointer survives, and the mirror plus manifest are regenerated."
    verification:
      - kind: integration
        ref: "uv run scripts/gen_skills.py --check — every mirror file and the manifest UNCHANGED"
        status: pass
      - kind: other
        ref: "generated.skills.manifest holds 11 entries; find reports zero CHANGELOG.md/LESSONS.md"
        status: pass
    human_judgment: false
  - id: D3
    description: "The ESP-IDF template carries no .pio or .cache build output and still has its ten tracked files."
    verification:
      - kind: other
        ref: "test ! -d templates/homework-espidf/.pio && test ! -d templates/homework-espidf/.cache && git ls-files templates/homework-espidf | wc -l == 10"
        status: pass
    human_judgment: false
  - id: D4
    description: "Every gate command is green and one atomic commit carries only the planned tracked paths."
    verification:
      - kind: integration
        ref: "pio run -d homeworks/1_3-police-flasher; pio test -d tests -e native (73/73); pre-commit run --all-files (exit 0)"
        status: pass
      - kind: integration
        ref: "uv run scripts/check_metadata.py; uv run scripts/check_report.py — both PASS"
        status: pass
    human_judgment: false

metrics:
  duration: 10min
  completed: 2026-10-27
status: complete
---

# Quick 261027-vxo: Remove Dead Code, Config-Text Tests, and Skill Process Docs

**Four dead scripts/tests, fourteen skill process documents, and the ESP-IDF template build output removed, with the generated skills mirror and manifest regenerated to eleven entries in one atomic commit.**

## Performance

- **Duration:** 10 min 32 s
- **Started:** 2026-10-27T21:05:07Z
- **Completed:** 2026-10-27T21:15:39Z
- **Tasks:** 3
- **Files modified:** 43 (32 deletions, 11 modifications)

## Accomplishments

- Deleted `scripts/ci/check_lfs_pointers.sh`, `scripts/review_smoke_test.sh`,
  `scripts/tests/test_tooling_config.py` and `scripts/tests/test_ci_workflows.py`;
  the stdlib suite dropped from 522 to 397 tests and stayed green.
- Deleted the fourteen `CHANGELOG.md` / `LESSONS.md` process documents from the
  canonical tree and every prose pointer to them, then let `scripts/gen_skills.py`
  delete the eighteen mirror orphans and rewrite the manifest from 25 to 11 entries.
- Removed `templates/homework-espidf/.pio` and `.cache` while keeping all ten tracked
  scaffold files byte-identical.
- Ran the full gate: both PlatformIO commands, the stdlib suite, both checkers, the
  mirror check and the whole pre-commit surface are green.

## Task Commits

One atomic commit carries the entire plan, as Task 3's verification requires:

1. **Tasks 1-3: dead paths, process docs, template junk** - `61c0100` (chore)

**Plan metadata:** not committed by the executor; the orchestrator handles the docs commit.

## Files Created/Modified

- `scripts/ci/check_lfs_pointers.sh` — deleted (guarded a documentation site removed in `9d28f5d`)
- `scripts/review_smoke_test.sh` — deleted (tested the reviewers, not the artifact)
- `scripts/tests/test_tooling_config.py` — deleted (configuration-text assertions)
- `scripts/tests/test_ci_workflows.py` — deleted (configuration-text assertions)
- `.claude/skills/*/CHANGELOG.md`, `.claude/skills/*/LESSONS.md` — 14 files deleted
- `.claude/skills/hw-build/SKILL.md`, `hw-flash/SKILL.md`, `new-homework/SKILL.md` — changelog/lessons prose removed
- `.claude/skills/hw-build/references/repair-loop.md` — changelog/lessons prose removed
- `.agents/skills/` — 18 orphans deleted, 4 mirror files regenerated
- `generated.skills.manifest` — 25 → 11 entries
- `AGENTS.md` — skills-layout bullet drops the process documents
- `.yamllint.yaml` — policy comment no longer names the deleted test module

## Decisions Made

- Kept the five ADR references to `test_tooling_config` untouched. `AGENTS.md` marks the
  ADR body as the historical record and states that a path it names may no longer exist,
  so rewriting it would have violated a `[MUST]` rule to satisfy a grep.
- Removed the now-false `test_ci_workflows` assertion from the `.yamllint.yaml` policy
  comment. This is config text, not a change to the yamllint tool or its rules.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Repaired the dangling `.yamllint.yaml` reference**
- **Found during:** Task 1 verification
- **Issue:** The plan asserted that no tracked file outside `.planning/` names the four
  deleted paths. `git grep` found `.yamllint.yaml:18` still claiming the workflows are
  "asserted to keep the textual `on:` in `test_ci_workflows`".
- **Fix:** Trimmed the trailing clause so the comment ends at "The key check is the only
  safe fix." No linter rule, pin or hook changed.
- **Files modified:** `.yamllint.yaml`
- **Verification:** `yamllint` pre-commit hook passes; the grep now returns only the ADR
  archive hits.
- **Committed in:** `61c0100`

### Accepted Residuals (not auto-fixed)

**2. The ADR archive still names `test_tooling_config`**
- **Found during:** Task 1 verification
- **Issue:** `docs/decisions/0012-formatting-approximation.md` (2 hits) and
  `docs/decisions/0013-clangd-multi-root-contract.md` (3 hits) name the deleted module in
  their `### Confirmation` sections.
- **Why not fixed:** `AGENTS.md` is `[MUST]`: "Do not rewrite the ADR body: it is the
  historical record of what was decided, and a path it names may no longer exist."
- **Consequence:** Task 1's literal verify
  `! git grep -nE '...' -- . ':!.planning'` **fails** with those five ADR hits. It is
  reported as a failure here, not as a pass. The plan's must-have truth "no tracked file
  outside `.planning/` names any of them" is met only for non-ADR files.

**3. Plan-specified `python3` checker invocations fail on the system interpreter**
- **Found during:** Task 3 gate
- **Issue:** `python3 scripts/check_metadata.py` and `python3 scripts/check_report.py`
  raise `ModuleNotFoundError: No module named 'yaml'`. Both scripts carry a PEP 723
  `# /// script` header declaring `PyYAML==6.0.3` and `jsonschema==4.26.0`, and
  `AGENTS.md`'s quick-start runs them as `uv run`.
- **Fix:** None needed in the code; the change does not cause it. The repository's
  canonical invocation was run and passed:
  `uv run scripts/check_metadata.py` → `PASS: metadata contract satisfied`;
  `uv run scripts/check_report.py` → `PASS: report contract satisfied`.
- **Reported as:** the plan's literal `python3 …` form is a **failure**, for the
  environment reason above; the `uv run` form is a pass.

**4. The plan commits once, not once per task**
- **Found during:** Task sequencing
- **Issue:** The orchestrator's generic rule says "commit each task atomically", while
  the plan's Task 3 requires a single commit whose verification asserts HEAD's subject
  and an empty `git status --porcelain -- . ':!.planning'`. Splitting would leave Task 3
  with no paths to commit and break its verification.
- **Fix:** Followed the plan and `AGENTS.md` ("Every change is one atomic commit"):
  one commit, `61c0100`, carrying all 43 planned paths.

---

**Total deviations:** 1 auto-fixed (Rule 2), 3 accepted residuals documented above.
**Impact on plan:** The trim itself is complete and every gate the change can affect is
green. The residuals are a project-rule conflict (ADR history), an environment mismatch
(`python3` vs `uv`), and a commit-granularity instruction conflict.

## Issues Encountered

- `pre-commit run --all-files` did not hit the recorded `end-of-file-fixer` sandbox
  limitation on `.vscode/settings.json`; all fourteen hooks passed on the first run.
- `scripts/ci/` became empty and disappeared on its own; no placeholder was created.

## User Setup Required

None - no external service configuration required.

## Known Stubs

None.

## Threat Flags

None — no new network endpoint, auth path, file-access pattern or schema change was
introduced. The two accepted loss-of-coverage dispositions (T-VXO-01, T-VXO-02) are
recorded in the plan and materialised exactly as planned.

## Next Phase Readiness

- The repository surface matches the maintainer's 2026-10-27 decision.
- Reviewers should note that `scripts/clangd-wrapper.sh` behavior and the
  `pull_request_target` / `permissions: read` CI invariants now rest on review and the
  pre-push stage alone.

---
*Phase: quick-261027-vxo*
*Completed: 2026-10-27*

## Self-Check: PASSED

- All four deleted paths are absent from the working tree.
- `scripts/tests/__init__.py`, `temp_root.py` and every surviving module exist.
- All nine edited canonical files exist.
- Commit `61c0100` is an ancestor of HEAD.
- The only unstaged path is the pre-existing `.planning/todos/…` modification; the
  SUMMARY is untracked and left for the orchestrator's docs commit.

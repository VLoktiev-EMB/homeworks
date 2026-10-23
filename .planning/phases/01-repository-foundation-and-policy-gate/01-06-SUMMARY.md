---
phase: 01-repository-foundation-and-policy-gate
plan: 06
subsystem: documentation
tags: [agents-md, rulebook, claude-adapter, single-source, homework-id, readme, licensing, python-unittest]

# Dependency graph
requires:
  - plan: 01-01
    provides: "scripts/tests/ package, unittest discovery, and scripts/check_policy.py"
  - plan: 01-02
    provides: ".gitignore / .gitattributes and the LFS routing referenced by the rulebook"
  - plan: 01-03
    provides: ".pre-commit-config.yaml and .github/workflows/security.yml"
  - plan: 01-04
    provides: "LICENSE, NOTICE, LICENSES/, REUSE.toml for the README and the license rules"
  - plan: 01-05
    provides: ".github/PULL_REQUEST_TEMPLATE/{homework,infra,docs}.md and check_pr_templates.py"
  - plan: 01-07
    provides: "docs/decisions/README.md and ADRs 0001-0005"
  - plan: 01-08
    provides: "scripts/tag_homework.sh, the only tag path"
provides:
  - "AGENTS.md — canonical rulebook, 194 lines, five-token enforcement vocabulary, routing table"
  - ".claude/CLAUDE.md — thin adapter: @AGENTS.md import plus three verbatim generator blocks"
  - "README.md — purpose, rules and decisions pointers, precise MIT/CC-BY-4.0 split"
  - "scripts/tests/test_agents_md.py — 12-test ceiling/vocabulary/routing/adapter contract"
  - "scripts/tests/test_homework_id.py — extracts the documented ID pattern and proves its behavior"
affects: [phase-02, phase-03, phase-04, phase-05, phase-09, every future agent run]

actuals:
  tokens: 18400
  tasks: 3
  commits: 4
  plan_head_before: 4b7ba7d23a1358c0c8e103e5e1a9141b79e08933
  plan_head_after: 531b2a3c086afa5e3bb2f8d3daff0806ab0a4a0a

tech-stack:
  added: []
  patterns:
    - "Single-source rulebook: the rules live in AGENTS.md, the tool adapter imports it, and a test fails if the adapter grows enforcement tags of its own"
    - "Generator-block slicing: the adapter test removes GSD marker blocks before asserting 'no restated rules', so a generator run cannot turn the test red"
    - "Documentation as the test fixture: the homework-ID regex is extracted from AGENTS.md prose and applied, so prose and behavior cannot drift"

key-files:
  created:
    - AGENTS.md
    - scripts/tests/test_agents_md.py
    - scripts/tests/test_homework_id.py
  modified:
    - .claude/CLAUDE.md
    - README.md

key-decisions:
  - "The [ENFORCED: CI] tag is defined as repository automation or a CI drift check, which lets the protected-branch rule name the ruleset honestly while staying inside the locked three-mechanism vocabulary."
  - "Squash-only is documented as scoped to merges into the default branch; repo-level merge and rebase stay enabled for feature branches, matching ADR-0003."
  - "The gitleaks rule states that the pinned default ruleset is pattern-based and does not flag every vendor key shape; widening it is a Phase 6 decision through .gitleaks.toml, never a quiet allowlist entry."
  - "The adapter's @AGENTS.md import is line 1, not merely the first substantive line, so the test's strictest reading is satisfied."
  - "The routing table names docs/standards/ only with a '(planned, Phase 5)' marker on the same line; the same rule is enforced for every future mention by the test, not by review."

patterns-established:
  - "Rulebook contract tests: ceiling, literal token vocabulary, canonical command list, routing targets, and a verbatim precedence sentence are all asserted."
  - "Adapter no-fork test: strip generator-owned blocks, then assert the enforcement vocabulary is absent from hand-written prose."

requirements-completed: [FOUND-02, FOUND-10]

coverage:
  - id: D1
    description: "Canonical AGENTS.md at 194 lines with all five enforcement tokens, canonical commands, a routing table, and the verbatim nearest-file precedence sentence"
    requirement: FOUND-10
    verification:
      - kind: unit
        ref: "python3 -m unittest scripts.tests.test_agents_md.RulebookTest -v (7 tests)"
        status: pass
      - kind: integration
        ref: "wc -l AGENTS.md -> 194 (ceiling 300)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Homework-ID convention documented and test-proven: canonical forms match, empty/separator-less/mixed-case/dotted/non-ASCII forms fail"
    requirement: FOUND-02
    verification:
      - kind: unit
        ref: "python3 -m unittest scripts.tests.test_homework_id -v (6 tests)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Thin Claude adapter: @AGENTS.md on line 1, no rule text, three generator blocks preserved byte-for-byte"
    requirement: FOUND-10
    verification:
      - kind: unit
        ref: "python3 -m unittest scripts.tests.test_agents_md.AdapterTest -v (5 tests)"
        status: pass
      - kind: integration
        ref: "byte comparison of lines 744-772 of the pre-rewrite file against the preserved tail -> identical"
        status: pass
      - kind: integration
        ref: "grep -c '^@AGENTS.md' .claude/CLAUDE.md -> 1"
        status: pass
    human_judgment: false
  - id: D4
    description: "Foundation README: purpose, Phase 1 of 11 status, AGENTS.md and docs/decisions/ pointers, precise MIT / CC-BY-4.0 split naming VLoktiev-EMB"
    verification:
      - kind: other
        ref: "python3 token check over README.md: AGENTS.md, docs/decisions, LICENSE, NOTICE, MIT, CC-BY-4.0, VLoktiev-EMB -> all present"
        status: pass
      - kind: integration
        ref: "ls AGENTS.md README.md docs/decisions/README.md LICENSE NOTICE -> all exist"
        status: pass
    human_judgment: false
  - id: D5
    description: "The repository is green under the full local gate after the README rewrite"
    verification:
      - kind: integration
        ref: "pre-commit run --all-files -> all five hooks Passed"
        status: pass
      - kind: integration
        ref: "python3 -m unittest discover -s scripts/tests -v -> 99 tests OK"
        status: pass
      - kind: integration
        ref: "python3 scripts/check_pr_templates.py -> exit 0"
        status: pass
      - kind: integration
        ref: "python3 scripts/check_policy.py --check -> exit 0, every line PASS against live GitHub"
        status: pass
    human_judgment: false

duration: ~25min
completed: 2026-10-23
status: complete
---

# Phase 1 Plan 06: Canonical Rulebook and Thin Adapter Summary

**One 194-line `AGENTS.md` now carries every rule with a severity tag and an enforcement
mechanism, `.claude/CLAUDE.md` is reduced to a seven-line `@AGENTS.md` import that cannot
fork the rules, and an 18-test contract binds the ceiling, the vocabulary, the canonical
commands, the routing table, the verbatim precedence sentence, and the homework-ID regex to
the prose that states them.**

## Performance

- **Duration:** ~25 min
- **Started:** not captured (session opened at the plan file)
- **Completed:** 2026-10-23
- **Tasks:** 3 of 3 complete
- **Files modified:** 5 (3 created, 2 rewritten)

## Accomplishments

- Wrote `AGENTS.md` in the six-section order D-04 fixes — project, agent quick-start,
  repository layout, tagged rules, routing table, precedence — at **194 lines**, well
  under the 300-line ceiling, with every rule carrying both `[MUST]`/`[SHOULD]` and one of
  `[ENFORCED: pre-commit]`, `[ENFORCED: CI]`, `[ENFORCED: review]`.
- Made the enforcement vocabulary usable rather than decorative: a legend defines what
  each mechanism means (developer machine / repository automation or CI drift check /
  human reviewer), so `[ENFORCED: CI]` can honestly cover the `main` ruleset as well as a
  workflow.
- Documented the facts the merged wave-2 work established: squash-only applies to merges
  **into the default branch** while repo-level merge and rebase stay enabled; tags exist
  only through `scripts/tag_homework.sh <id>`; the repository is public on a free plan, so
  no rule assumes a paid feature; and the pinned gitleaks default ruleset is pattern-based,
  not exhaustive.
- Reduced `.claude/CLAUDE.md` from **772 lines to 29** (7 hand-written lines plus 22 lines
  of generator-owned blocks). The three generator blocks — `skills`, `workflow`, `profile`
  — were verified byte-identical to the pre-rewrite tail (lines 744-772), and the
  `@AGENTS.md` import is line 1.
- Rewrote `README.md` from the one-line placeholder into the minimum honest front door:
  purpose, an explicit "Phase 1 of 11" status, pointers to `AGENTS.md` and
  `docs/decisions/README.md`, and the MIT / CC-BY-4.0 split naming `VLoktiev-EMB`.
- Added an 18-test contract (12 in `test_agents_md.py`, 6 in `test_homework_id.py`) that
  turns four silent failure modes into red tests: the rulebook growing unreadable, the
  adapter forking into its own rules, a dead `docs/standards/` link, and the documented ID
  pattern drifting from the one the prose claims.

## Task Commits

1. **Task 1 RED: failing rulebook and homework-ID contract tests** — `57633de` (test)
2. **Task 1 GREEN: canonical AGENTS.md rulebook** — `b8d1125` (feat)
3. **Task 2: thin `.claude/CLAUDE.md` adapter** — `4c72b54` (refactor)
4. **Task 3: minimal foundation README** — `531b2a3` (docs)

The plan-metadata commit (this SUMMARY) follows.

## TDD cycle (Task 1)

- **RED (`57633de`):** `NO_COLOR=1 python3 -m unittest scripts.tests.test_agents_md
  scripts.tests.test_homework_id -v` → `Ran 18 tests`, `FAILED (failures=21)`.
  Every failure named a missing artifact or a missing assertion target
  (`missing …/AGENTS.md`, `expected exactly one anchored pattern in AGENTS.md, found []`).
  No import, loader, or fixture error appeared.
- **GREEN (`b8d1125`):** the rulebook subset `scripts.tests.test_agents_md.RulebookTest`
  plus `scripts.tests.test_homework_id` → `Ran 13 tests … OK`; `wc -l AGENTS.md` → 194.
- **Full GREEN after Task 2:** the plan's exact Task 1 command —
  `python3 -m unittest scripts.tests.test_agents_md scripts.tests.test_homework_id -v`
  → `Ran 18 tests … OK`, once the adapter existed (see Deviation 1).

## As shipped

| Artifact | Measurement |
|---|---|
| `AGENTS.md` | 194 lines (ceiling 300); five enforcement tokens present |
| Adapter | 29 lines total: 7 hand-written + 22 generator-owned |
| ID regex | `^[0-9]+_[0-9]+-[a-z0-9-]+$` |
| Test contract | 18 tests (12 + 6) |
| Full suite | 99 tests OK |

Adapter structure, in order:

1. `@AGENTS.md` — line 1.
2. `# Claude Code adapter` heading plus four lines stating that AGENTS.md is canonical,
   wins on conflict, and that the adapter carries mechanics only.
3. `<!-- GSD:skills-start source:skills/ -->` … `-end` — preserved verbatim.
4. `<!-- GSD:workflow-start source:GSD defaults -->` … `-end` — preserved verbatim.
5. `<!-- GSD:profile-start -->` … `-end` — preserved verbatim.

## Where the removed adapter material lives

Nothing left the repository's knowledge base; only the always-loaded adapter stopped
carrying it.

- The 739 removed lines (the generated project, stack, conventions, and architecture
  blocks) are recoverable from git history — the parent of `4c72b54` — and from
  `.planning/research/STACK.md`, which is the source GSD generated them from.
- Their publishable home is `docs/standards/` from **Phase 5** (D-01). Until then no
  published copy exists; that is deliberate, not a loss.
- The durable rules that would otherwise have been lost in the interim are stated in
  `AGENTS.md` (workflow, layout, Git policy, secrets, assets, licensing).

## Files Created/Modified

- `AGENTS.md` — canonical rulebook; six sections; 194 lines
- `.claude/CLAUDE.md` — thin adapter; 772 → 29 lines
- `README.md` — foundation README; 1 → 30 lines
- `scripts/tests/test_agents_md.py` — 12 tests: 7 rulebook, 5 adapter
- `scripts/tests/test_homework_id.py` — 6 tests, including five rejection probes

## Decisions Made

- **Define `[ENFORCED: CI]` to include repository automation.** The protected-branch rule
  is enforced by the GitHub ruleset, not by a workflow; the locked vocabulary has no
  "ruleset" token. Rather than misstate the mechanism or invent a fourth token, the legend
  defines CI as "repository automation or a CI drift check", and the rule names the
  ruleset and the `check_policy.py` proof explicitly.
- **Keep the gitleaks limitation visible in the rulebook.** The pinned 8.30.1 default
  ruleset flags a PEM private-key block but not every vendor key shape. Saying so prevents
  a future reader from treating a green scan as an exhaustive guarantee, and it routes any
  widening to a Phase 6 `.gitleaks.toml` decision rather than a quiet allowlist entry.
- **Assert the adapter's import on line 1.** "First substantive line" is ambiguous; line 1
  is the strictest reading and leaves no room for a title to hide a missing import.
- **Strip generator blocks before asserting "no restated rules".** The adapter must be
  able to accept a future generator run without this test turning red, while still failing
  if hand-written prose reintroduces the enforcement vocabulary.
- **Treat `docs/standards/` as a planned path, enforced on every line.** The test rejects
  any line that mentions it without "planned", so a future dead link cannot be added by a
  hurried edit.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Task 1's verify command spans Task 2's deliverable**
- **Found during:** Task 1 (GREEN verification)
- **Issue:** The plan's `<behavior>` for Task 1 places the adapter assertions in
  `test_agents_md.py`, and Task 1's `<automated>` runs that whole module — but the adapter
  it asserts is Task 2's file (`.claude/CLAUDE.md`), which Task 1 does not own. As written,
  Task 1 cannot be green before Task 2 runs.
- **Fix:** At Task 1 the rulebook subset was verified
  (`test_agents_md.RulebookTest` + `test_homework_id`, 13 tests OK) and the exact combined
  command was re-run to green immediately after Task 2 committed the adapter (18 tests
  OK). No test was weakened and no assertion was removed.
- **Files modified:** none
- **Verification:** 13 tests OK at Task 1; 18 tests OK at Task 2; 99 tests OK on the full
  suite.
- **Committed in:** `b8d1125` (rulebook), `4c72b54` (adapter)

---

**Total deviations:** 1 auto-fixed (Rule 3, a plan-ordering artifact)
**Impact on plan:** No scope change and no weakened verification. The split between Task 1
and Task 2 remains honest: one commit adds the rulebook, the next adds the adapter that
imports it.

## Issues Encountered

- The worktree-isolation guard refuses compound commands that mention `git` outside a
  plain single invocation, so the generator-block comparison was done by reading the
  pre-rewrite file from the main checkout with `pathlib` rather than by piping
  `git show`. The comparison reported `BLOCKS IDENTICAL: True`.
- The commit ledger file (`$(git rev-parse --git-dir)/gsd-plan-head-before-01-06`) could
  not be written — the guard refuses writes into the shared `.git` directory. The commit
  count and both head SHAs in `actuals` were measured directly
  (`git rev-list --count 4b7ba7d..HEAD` → 4; two `git rev-parse` calls).
- Every commit ran the real pre-commit gate (config present on this base); no
  `--no-verify` and no `PRE_COMMIT_ALLOW_NO_CONFIG` was needed anywhere in this plan.

## User Setup Required

None — no external service configuration required.

## Known Stubs

None. The routing table's `docs/standards/` and skills rows are explicitly marked as
planned for Phases 5 and 9, and the test enforces that marker.

## Threat Flags

None — the changed files stay inside the plan's threat model. T-1-11 is mitigated exactly
as designed: `AdapterTest` fails if the adapter stops importing `AGENTS.md`, starts
carrying enforcement tags, or loses a generator marker pair. T-1-13 holds: neither
`AGENTS.md` nor `README.md` contains a real name, an institution, or an email address —
only the public handle `VLoktiev-EMB`. T-1-SC does not apply; no package was installed.

## Next Phase Readiness

- `AGENTS.md` is the single place to change a rule from now on. Both Claude Code and
  `AGENTS.md`-aware tools read the same text; the adapter is an import, not a copy.
- **Phase 2** can add `homeworks/` and `lib/` without touching the rulebook's structure;
  the layout section already names both as planned with their phase.
- **Phase 4** owns the `homework.yaml` schema that will enforce the documented ID pattern
  mechanically; the pattern as shipped is `^[0-9]+_[0-9]+-[a-z0-9-]+$`.
- **Phase 5** relocates the removed stack/standard material into `docs/standards/` and
  should, in the same change, update the routing-table row to drop its "planned" marker —
  the test will keep any stale marker visible until then.
- **Phase 9** adds project skills; the skills block in the adapter is already preserved
  and waiting for the generator.

## Self-Check: PASSED

- All five planned files exist on disk: `AGENTS.md`, `.claude/CLAUDE.md`, `README.md`,
  `scripts/tests/test_agents_md.py`, `scripts/tests/test_homework_id.py`.
- Commits `57633de`, `b8d1125`, `4c72b54`, `531b2a3` are ancestors of HEAD.
- `python3 -m unittest scripts.tests.test_agents_md scripts.tests.test_homework_id -v` —
  18 tests, OK.
- `python3 -m unittest discover -s scripts/tests -v` — 99 tests, OK.
- `pre-commit run --all-files` — all five hooks Passed.
- `python3 scripts/check_pr_templates.py` — exit 0.
- `python3 scripts/check_policy.py --check` — exit 0, every line PASS.
- `grep -c '^@AGENTS.md' .claude/CLAUDE.md` — 1; `wc -l AGENTS.md` — 194.

---
*Phase: 01-repository-foundation-and-policy-gate*
*Completed: 2026-10-23*

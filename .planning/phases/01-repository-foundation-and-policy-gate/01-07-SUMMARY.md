---
phase: 01-repository-foundation-and-policy-gate
plan: 07
subsystem: documentation
tags: [adr, madr, architecture-decision-records, git-policy, licensing, reuse, git-lfs, python-unittest, tdd]

# Dependency graph
requires:
  - "01-01 — policy/ruleset-main.json, policy/repository.json, and the measured --apply behavior ADR-0003 cites"
provides:
  - "docs/decisions/template.md — MADR 4.0.0 full template, exact section order"
  - "docs/decisions/README.md — numbering rules and the status index for ADRs 0001-0005"
  - "docs/decisions/0001..0005 — five accepted MADR records"
  - "scripts/tests/test_adrs.py — numbering, frontmatter, index-agreement, and required-content test (18 tests)"
  - "Next ADR number reserved: 0006 for the Phase 2 symlink decision"
affects: [01-04, 01-06, phase-02, phase-03, phase-07, phase-08-ci, docs-site]

actuals:
  tokens: 12300
  tasks: 2
  commits: 3
  plan_head_before: 76110a09422d192d0b0317b313f02b1d33855c42
  plan_head_after: ad9520b53a25c2d8788ebeca44960f594dac53f1

tech-stack:
  added: []
  patterns:
    - "MADR 4.0.0 full records: frontmatter → context → drivers → options → outcome → consequences → confirmation → pros/cons → more information"
    - "Dependency-free documentation tests: frontmatter parsed as plain text, headings matched by exact line, status index parsed as a Markdown table"
    - "Permanent sequential ADR numbering guarded by a unit test rather than by convention"

key-files:
  created:
    - docs/decisions/template.md
    - docs/decisions/README.md
    - docs/decisions/0001-monorepo-with-independent-projects.md
    - docs/decisions/0002-ports-and-adapters-no-universal-hal.md
    - docs/decisions/0003-git-policy-and-protected-main.md
    - docs/decisions/0004-license-and-attribution.md
    - docs/decisions/0005-asset-and-lfs-policy.md
    - scripts/tests/test_adrs.py
  modified: []

key-decisions:
  - "Squash-only is recorded as scoped to merges into the default branch, not repo-wide; the ruleset's required_linear_history + allowed_merge_methods=[\"squash\"] is the enforcement point, and repo-level merge/rebase flags stay true."
  - "A 200 from PATCH /repos is not evidence a setting applied: GitHub silently ignores unsupported security_and_analysis fields, so ADR-0003 requires re-reading and diffing; the two free-plan toggles are a documented revisit trigger."
  - "ADR-0003 records require_extra_approval_for_unattributed_changes as explicitly unverified (assumption A2), rather than asserting it is preserved."
  - "The numbering test asserts contiguity from 0001 plus the presence of 0001-0005, rather than exactly five files, so Phase 2 adding 0006 needs no test edit."
  - "The index table is the machine-readable status surface: number, title, status, and date are all asserted against frontmatter and the H1 title."

requirements-completed: [TOOL-07]

coverage:
  - id: D1
    description: "Five MADR 4.0 ADRs with a permanent numbering scheme and a status index"
    requirement: TOOL-07
    verification:
      - kind: unit
        ref: "python3 -m unittest scripts.tests.test_adrs -v (18 tests)"
        status: pass
      - kind: unit
        ref: "python3 -m unittest discover -s scripts/tests -v (28 tests)"
        status: pass
    human_judgment: false
  - id: D2
    description: "ADR-0003 carries the audit gaps: tag mutability, approvals trigger, public .planning, free-plan trigger, unverified A2"
    requirement: TOOL-07
    verification:
      - kind: unit
        ref: "scripts/tests/test_adrs.py#test_adr_0003_records_the_git_policy_audit_gaps"
        status: pass
    human_judgment: false
  - id: D3
    description: "ADR-0004 and ADR-0005 carry the substitution, stale-reference, boundary, and Pages/LFS notes"
    requirement: TOOL-07
    verification:
      - kind: unit
        ref: "scripts/tests/test_adrs.py#test_adr_0004_records_the_license_substitutions, #test_adr_0005_records_the_asset_policy"
        status: pass
    human_judgment: false

duration: ~5min
completed: 2026-10-23
status: complete
---

# Phase 1 Plan 07: Architecture Decision Records Summary

**Five MADR 4.0 records with permanent sequential numbering and a status index, guarded by an 18-test suite — including ADR-0003's explicit account of squash-only scoping, the silently-ignored free-plan settings, mutable `hw/<id>` tags, and the accepted public planning trail.**

## Performance

- **Duration:** ~5 min
- **Started:** 2026-10-23T17:14:15Z
- **Completed:** 2026-10-23T17:16:11Z
- **Tasks:** 2 of 2 complete
- **Files created:** 8 (no files modified outside this plan's own index)

## Accomplishments

- Wrote `docs/decisions/template.md` as the MADR 4.0.0 full template: the five
  frontmatter keys and the eight-section order, with the status enum
  `proposed | rejected | accepted | deprecated | superseded by ADR-NNNN`.
- Established the numbering contract in `docs/decisions/README.md`: sequential on
  acceptance, never reused, next = highest + 1, with a status table that the test
  cross-checks against each record's frontmatter and H1 title.
- Recorded the two foundational architecture decisions (monorepo of independent
  PlatformIO projects; ports and adapters with no universal HAL) with real
  alternatives and their honest downsides.
- Recorded ADR-0003 with the parts that were *measured*, not assumed: squash-only
  scoped to the default branch, the free-plan silently-ignored secret-scanning
  fields, the revisit trigger, and the still-unverified
  `require_extra_approval_for_unattributed_changes` parameter.
- Recorded ADR-0004 (MIT/CC-BY-4.0 split, handle-only identity, `REUSE.toml`
  substitution for the deprecated dep5 artifact, `.github/PULL_REQUEST_TEMPLATE/`
  kept on the MIT catch-all, stale SIM-02 reference) and ADR-0005 (eight LFS
  extensions, 1024 kB guard, linked videos, docs images as normal Git objects
  because Pages cannot serve LFS).
- Reserved **0006** for the Phase 2 symlink decision and stated it in the index.

## Task Commits

1. **Task 1: MADR template, status index, and ADRs 0001-0002** — `7b75cc3` (docs)
2. **Task 2 RED: failing ADR numbering/index/content assertions** — `f6a1dea` (test)
3. **Task 2 GREEN: ADRs 0003-0005 and completed index** — `ad9520b` (feat)

## TDD Evidence (task 2)

- **RED:** `python3 -m unittest scripts.tests.test_adrs -v` → `Ran 18 tests … FAILED
  (failures=4)` before ADRs 0003-0005 existed. The four failures were
  `test_phase_one_numbers_0001_to_0005_exist` and the three required-content tests.
- **GREEN:** the same command after writing the records and index rows → `Ran 18
  tests … OK`.
- The RED commit `f6a1dea` precedes the GREEN commit `ad9520b`; both are additive and
  independently revertable.

## Deviations from Plan

### Auto-fixed Issues

None affecting code or content.

### Environment note (not a deviation)

- The machine has a **global `pre-commit` hook installed but no
  `.pre-commit-config.yaml` in the repository yet** (plan 01-06 introduces it). A plain
  `git commit` aborted with "No .pre-commit-config.yaml file was found". Rather than
  pass `--no-verify`, commits used the hook's own documented escape,
  `PRE_COMMIT_ALLOW_NO_CONFIG=1`, which prints "Skipping `pre-commit`" and runs the
  commit normally. Once 01-06 lands the config, the variable becomes unnecessary.

### Content additions beyond the letter of the plan

- The plan's required-content list for ADR-0003 named the tag gap, the approvals
  trigger, and the public-planning consequence. The record and its test additionally
  assert the default-branch scoping of squash-only, the "a 200 is not evidence"
  behavior, the free-plan revisit trigger, and the name of the unverified parameter —
  all mandated by the critical findings carried into this execution.

## Files Created/Modified

- `docs/decisions/template.md` — MADR 4.0.0 full template
- `docs/decisions/README.md` — purpose, numbering rules, status index (0001-0005), next number 0006
- `docs/decisions/0001-monorepo-with-independent-projects.md`
- `docs/decisions/0002-ports-and-adapters-no-universal-hal.md`
- `docs/decisions/0003-git-policy-and-protected-main.md`
- `docs/decisions/0004-license-and-attribution.md`
- `docs/decisions/0005-asset-and-lfs-policy.md`
- `scripts/tests/test_adrs.py` — 18 structural and content tests

## Decisions Made

- **Index agreement is asserted three ways**: every record has a row, every row has a
  file, and both the status and the H1 title match. A typo in either direction fails.
- **Forward-compatible numbering test**: contiguity from 0001 plus presence of
  0001-0005, instead of "exactly five files", so Phase 2 adding 0006 requires no test
  change and still cannot introduce a gap or duplicate.
- **No YAML dependency**: frontmatter is parsed as `key: value` plain text, matching
  the dependency-free style of `scripts/tests/test_check_policy.py` and avoiding a
  new install.
- **MADR order includes `Pros and Cons` after `Confirmation`**, as verified verbatim
  from the `adr/madr` 4.0.0 template in the research, with a test that every option
  subsection carries at least one Good/Neutral/Bad judgement.

## Issues Encountered

- `git add` without an absolute binary path is intercepted by the `rtk` wrapper, and
  the worktree-isolation guard refuses a compound `cd … && git …` command. All git
  operations were run as `/usr/bin/git <subcommand>` from the worktree root.
- `git commit` required the `PRE_COMMIT_ALLOW_NO_CONFIG=1` escape described above.

## Known Stubs

None.

## Threat Flags

None. The changed files stay inside the plan's threat model: T-1-12 (index integrity,
mitigated by the test), T-1-14 (handle-only identity, asserted by a no-email test and
by every record naming only `VLoktiev-EMB`), and T-1-SC (no packages installed; the
MADR template is attributed in `NOTICE` by plan 01-04).

## Next Phase Readiness

- **Next ADR number is 0006**, reserved for Phase 2's symlink decision; the index says
  so. Adding it needs the record plus its row, and the test stays green.
- The MADR template is the required shape for every later ADR; `test_adrs.py`
  will enforce it for 0006 and beyond without modification.
- ADR-0004 carries the actionable follow-up for Phase 7 planning: correct
  `REQUIREMENTS.md` SIM-02's stale "ADR-0004" reference to a later number.
- ADR-0003 carries the two operational triggers: approvals → 1 when a second
  maintainer joins; re-add the two secret-scanning keys on Team/Enterprise.

## Self-Check: PASSED

- All eight planned files exist on disk.
- Commits `7b75cc3`, `f6a1dea`, `ad9520b` are ancestors of HEAD.
- `python3 -m unittest scripts.tests.test_adrs -v` — 18 tests, OK.
- `python3 -m unittest discover -s scripts/tests -v` — 28 tests, OK.
- `ruff check scripts/tests/test_adrs.py` — no issues.

---
*Phase: 01-repository-foundation-and-policy-gate*
*Completed: 2026-10-23*

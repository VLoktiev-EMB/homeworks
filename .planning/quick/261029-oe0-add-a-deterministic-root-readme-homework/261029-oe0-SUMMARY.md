---
phase: quick
plan: 261029-oe0
subsystem: repo-tooling
tags: [readme, generator, pre-commit, metadata, markdown]

requires:
  - phase: quick
    provides: "the metadata contract and resolve_root/validate_homework_text in scripts/metadata"
provides:
  - "scripts/gen_readme.py — deterministic marker-region generator with --dir and --check"
  - "scripts/tests/test_gen_readme.py — 14 behavioural tests driven through uv run"
  - "a full English root README with a generated ## Homeworks table"
  - "a check-only readme-index pre-commit hook inherited by CI"
affects: [homeworks, README, AGENTS.md, course-index skill]

actuals:
  tokens: 7355
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "PEP 723 script + sys.path insert, matching scripts/check_metadata.py"
    - "marker-region rewrite: only bytes between BEGIN/END markers change"
    - "atomic write via sibling NamedTemporaryFile + os.replace"

key-files:
  created:
    - scripts/gen_readme.py
    - scripts/tests/test_gen_readme.py
  modified:
    - README.md
    - .pre-commit-config.yaml
    - AGENTS.md
    - .agents/skills/course-index/SKILL.md

key-decisions:
  - "The readme-index hook uses language: python with PyYAML==6.0.3 and jsonschema==4.26.0, because the CI meta job installs only pre-commit and the system has no `python` and no PyYAML under `python3`."
  - "The generated table is a projection of schema-validated metadata: report paths are never stat'ed on disk, and backslash is escaped before pipe in every free-text cell."
  - "Check mode reports `README.md: stale — run: uv run scripts/gen_readme.py` and is the only gate; no workflow file or step was added."

patterns-established:
  - "Generated-region ownership: the marker block is written only by scripts/gen_readme.py and gated by a check-only hook."

requirements-completed: ["QUICK-261029-oe0"]

coverage:
  - id: D1
    description: "Deterministic README homework index generator with --dir and --check, plus its behavioural test module"
    requirement: QUICK-261029-oe0
    verification:
      - kind: unit
        ref: "python3 -m unittest scripts.tests.test_gen_readme"
        status: pass
    human_judgment: false
  - id: D2
    description: "Rewritten root README with a generated ## Homeworks table listing the three real homeworks"
    requirement: QUICK-261029-oe0
    verification:
      - kind: integration
        ref: "uv run scripts/gen_readme.py --check"
        status: pass
    human_judgment: false
  - id: D3
    description: "Check-only readme-index pre-commit hook, green locally and inherited by CI's meta job"
    requirement: QUICK-261029-oe0
    verification:
      - kind: integration
        ref: "pre-commit run --all-files"
        status: pass
    human_judgment: false
  - id: D4
    description: "AGENTS.md rule and routing row plus corrected course-index skill status vocabulary"
    requirement: QUICK-261029-oe0
    verification:
      - kind: other
        ref: "grep 'scripts/gen_readme.py' AGENTS.md; grep 'planned`, `in-progress`, `complete`, `verified`' .agents/skills/course-index/SKILL.md"
        status: pass
    human_judgment: false

duration: 7min
completed: 2026-10-29
status: complete
---

# Quick Task 261029-oe0: Deterministic Root README Homework Index Summary

**A marker-region generator that renders the root README's `## Homeworks` table from validated `homework.yaml` metadata, gated by a check-only pre-commit hook that CI inherits.**

## Performance

- **Duration:** 7 min
- **Started:** 2026-10-29T15:37:21Z
- **Completed:** 2026-10-29T15:42:34Z
- **Tasks:** 2/2
- **Files modified:** 6

## Accomplishments

- `scripts/gen_readme.py` rewrites only the bytes between `<!-- BEGIN GENERATED: homeworks -->` and `<!-- END GENERATED -->`; `--check` reports drift and writes nothing; exit 2 covers absent/duplicate/inverted markers and unreadable inputs; exit 1 covers invalid metadata.
- The rewritten `README.md` is a full guide with ten designed sections and a generated table listing `1_3-police-flasher`, `1_4-dual-led-button-modes`, and `1_5-button-bounce` in order, each with a project and report link.
- One check-only `readme-index` hook with `language: python` and both existing pins; no workflow file or step was added, and CI's `meta` job inherits it through `pre-commit run --all-files`.
- `AGENTS.md` names the generator as the only writer of the region, and the `course-index` skill now lists the schema's four statuses and the generated region as the README source of truth.

## Task Commits

1. **Task 1: Add the generator, its tests, the rewritten README, and the check-only hook** - `2246ac5` (feat)
2. **Task 2: Document the generated region and correct the course-index skill** - `c2b44f5` (docs)

## Files Created/Modified

- `scripts/gen_readme.py` - deterministic marker-region generator (`--dir`, `--check`, atomic write)
- `scripts/tests/test_gen_readme.py` - 14 tests covering order/links, report and `none` cells, pipe escaping, empty message, every exit-2 marker case, drift without a write, idempotency, prose preservation, invalid document
- `README.md` - full repository guide with the generated `## Homeworks` region
- `.pre-commit-config.yaml` - one check-only `readme-index` local hook
- `AGENTS.md` - `[MUST] [ENFORCED: pre-commit]` rule and routing row
- `.agents/skills/course-index/SKILL.md` - corrected overview, statuses, quick-reference rows, and a fifth discovery rule

## Decisions Made

- Hook uses `language: python` with `PyYAML==6.0.3` and `jsonschema==4.26.0`: the CI `meta` job installs only pre-commit, the system has no `python`, and `python3` carries neither pin.
- The table is a projection of validated metadata, never of disk state: `_report_cell` reads only `report.path`, and no file is `stat`ed.
- Escaping order is backslash first, then pipe, so a literal `\|` cannot split a row.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- The initial pipe-escaping assertion counted raw `|` characters, which also counts the escaped separator. The assertion now counts unescaped `" | "` separators, which is the property the test intends to pin.

## Threat Surface Scan

No new network endpoints, auth paths, or trust-boundary surface. The generator writes only `<root>/README.md` through a sibling temporary file and `os.replace`; the hook runs the in-repo script in a pinned virtualenv with no network access. No new dependency was added.

## Known Stubs

None.

## User Setup Required

None.

## Next Phase Readiness

The root README is truthful and cannot drift silently: any metadata edit, schema change, or README edit triggers the same check locally and in CI. No blockers.

## Self-Check: PASSED

All six deliverable files exist and both task commits (`2246ac5`, `c2b44f5`) are ancestors of `HEAD`.

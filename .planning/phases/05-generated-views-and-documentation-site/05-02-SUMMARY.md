---
phase: 05-generated-views-and-documentation-site
plan: 02
subsystem: tooling
tags: [metadata, jsonschema, pyyaml, strict-loader, board-profile, pre-commit]

requires:
  - phase: 04-metadata-contract-and-scaffolding
    provides: the single `check_metadata.py` entry point, the 0/1/2 exit-code contract, and `StrictSafeLoader`
provides:
  - "`schema/board-profile.schema.json` — the machine-enforced contract for `boards/<id>.yaml`"
  - "`boards/esp32-s3-devkitc-1.yaml` — the first committed board profile at the D-04 path"
  - "`scripts/metadata/board_profile.py` — `load_board_schema` and `validate_board_text`"
  - "per-family positional routing in `scripts/check_metadata.py`"
  - "`BoardProfileTests` and a board schema shape assertion"
  - "`boards/` in the `check-metadata` pre-commit `files:` regex"
affects: [05-07 board pages, 05-08 docs pins, Phase 8 CI]

actuals:
  tokens: 6257
  tasks: 2
  commits: 2
  plan_head_before: 78f1e7c5ae520b471ebd9699b2b9eb98c7f94f39
  plan_head_after: 64b6204c9ff4322bda1019c2916a089b413d1a56

tech-stack:
  added: []
  patterns:
    - "one validator per document family, extended rather than duplicated (D-27)"
    - "strict duplicate-key loader for authored YAML (StrictSafeLoader)"
    - "lexical, containment-only symlink refusal that names the repository path"

key-files:
  created:
    - schema/board-profile.schema.json
    - boards/esp32-s3-devkitc-1.yaml
    - scripts/metadata/board_profile.py
  modified:
    - scripts/check_metadata.py
    - scripts/tests/test_homework_metadata.py
    - .pre-commit-config.yaml

key-decisions:
  - "The board schema keeps the homework envelope: `additionalProperties: false`, anchored `pattern` instead of `format`, and an enum for `frameworks` with its rationale written into the description."
  - "`validate_board_text` parses with `StrictSafeLoader`, so a duplicated `psram` or `pinout_url` key is an ERROR record rather than a silently last-wins value."
  - "Positional arguments are partitioned by family; a family with no selected path is scanned not at all, never widened to 'all'."
  - "A symlinked board document is refused with a lexical repository-relative record path, so neither the target nor an absolute location leaks."
  - "No homework-to-board cross-existence rule is added: it would invalidate existing fixture roots and is outside D-27."

patterns-established:
  - "Second document family through the same checker: `load_schema` and `load_board_schema` share one try block, so a broken schema is exit 2."
  - "Record paths for refused symlinks use `_relative_lexical`, not `relative_path`, because resolution would erase the symlink's own identity."

requirements-completed: [META-05, META-08]

coverage:
  - id: D1
    description: "`boards/<id>.yaml` is a first-class, schema-validated document family validated by the existing `scripts/check_metadata.py`"
    requirement: "META-05"
    verification:
      - kind: unit
        ref: "scripts/tests/test_homework_metadata.py#BoardProfileTests"
        status: pass
      - kind: integration
        ref: "uv run scripts/check_metadata.py --json"
        status: pass
    human_judgment: false
  - id: D2
    description: "Positional arguments select the family they name and never widen the other family to 'all'"
    requirement: "META-05"
    verification:
      - kind: unit
        ref: "scripts/tests/test_homework_metadata.py#BoardProfileTests.test_board_only_positional_scans_no_homework"
        status: pass
      - kind: unit
        ref: "scripts/tests/test_homework_metadata.py#BoardProfileTests.test_homework_only_positional_scans_no_board"
        status: pass
      - kind: unit
        ref: "scripts/tests/test_homework_metadata.py#BoardProfileTests.test_mixed_positionals_scan_exactly_the_named_families"
        status: pass
    human_judgment: false
  - id: D3
    description: "A local edit under `boards/` re-runs the metadata validator before it can be committed"
    requirement: "META-05"
    verification:
      - kind: other
        ref: "grep -q 'boards/' .pre-commit-config.yaml"
        status: pass
    human_judgment: false
  - id: D4
    description: "The board profile is committed at the D-04 path the generator and site navigation will consume"
    requirement: "META-08"
    verification:
      - kind: unit
        ref: "scripts/tests/test_homework_metadata.py#BoardProfileTests.test_accepted_profile_is_ok"
        status: pass
      - kind: integration
        ref: "uv run scripts/check_metadata.py boards/esp32-s3-devkitc-1.yaml"
        status: pass
    human_judgment: false

duration: 4min
completed: 2026-10-26
status: complete
---

# Phase 05 Plan 02: Board Profile Contract Summary

**`boards/<id>.yaml` became a schema-validated document family through the unchanged `check_metadata.py` entry point, with per-family positional routing and `StrictSafeLoader` rejecting duplicated keys.**

## Performance

- **Duration:** ~4 min
- **Started:** 2026-10-25T22:23Z (worktree created)
- **Completed:** 2026-10-25T22:26Z
- **Tasks:** 2
- **Files modified:** 6 (3 created, 3 modified)

## Accomplishments

- Added `schema/board-profile.schema.json`: draft 2020-12, `additionalProperties: false`, anchored patterns, `psram` enum, `frameworks` enum array with `uniqueItems` and a documented rationale.
- Committed the one real board profile at `boards/esp32-s3-devkitc-1.yaml`, byte-identical to `templates/board-profile/profile.yaml`.
- Added `scripts/metadata/board_profile.py` with `load_board_schema` and `validate_board_text`, parsing with `StrictSafeLoader` and rendering `{path, status, reason, line}` records.
- Extended `scripts/check_metadata.py` with `_board_documents`, `_partition_paths`, a second schema load inside the existing `try`, and a lexical symlink refusal. The 0/1/2 exit-code contract and the read-only guarantee are unchanged.
- Added `BoardProfileTests` (16 cases) plus a board-schema shape assertion; widened the `check-metadata` pre-commit `files:` regex to `boards/`.

## Task Commits

Each task was committed atomically:

1. **Task 1: Validate one board profile end to end through the existing checker** - `59690d3` (feat)
2. **Task 2: Pin the board-profile contract with tests and widen the metadata hook** - `64b6204` (test)

## Files Created/Modified

- `schema/board-profile.schema.json` — the board-profile contract.
- `boards/esp32-s3-devkitc-1.yaml` — the first committed profile (D-04 path).
- `scripts/metadata/board_profile.py` — `BOARD_SCHEMA_PATH`, `BOARD_DIRECTORY`, `load_board_schema`, `validate_board_text`.
- `scripts/check_metadata.py` — `_board_documents`, `_partition_paths`, `_relative_lexical`, the second schema load and the positional partition.
- `scripts/tests/test_homework_metadata.py` — `BoardProfileTests`; `SchemaShapeTest` board assertion; `BOARD_SCHEMA`/`BOARD_TEMPLATE` constants.
- `.pre-commit-config.yaml` — `boards/` added to `check-metadata`'s `files:` regex and its comment.

## Decisions Made

- Kept the board schema flat (six scalars plus one array) while copying the homework envelope exactly; no `$defs` were needed.
- Used lexically derived record paths for refused symlinks (`_relative_lexical`) instead of `relative_path`, because resolution would report the symlink target (or a bare basename) and lose the repository identity the record must name.
- The `boards/` directory symlink is a `CheckError` (exit 2); a symlinked document is an `ERROR` record (exit 1), matching the task's environment/content split.
- Did not add a homework-to-board cross-existence rule (rejected in the plan's review disposition).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Imported the shared loader/exception from `contract.py` instead of `yaml_loader.py`**

- **Found during:** Task 1 (implementation start)
- **Issue:** The plan directs `scripts/metadata/board_profile.py` to import `CheckError` from `scripts.metadata.errors` and `StrictSafeLoader` from `scripts.metadata.yaml_loader`. Those modules are created by parallel plan 05-01 and do not exist in this worktree; importing them made the module and every verification fail immediately.
- **Fix:** Imported `MAX_INPUT_BYTES`, `CheckError`, `StrictSafeLoader` and `relative_path` from `scripts.metadata.contract`. That module is the same object source, and 05-01's plan re-exports all five moved names from `contract.py`, so the import stays correct after the wave merges.
- **Files modified:** `scripts/metadata/board_profile.py`
- **Verification:** `uv run scripts/check_metadata.py --json` resolves and passes; the full suite is green.
- **Committed in:** `59690d3` (Task 1 commit)

### Execution notes (not deviations)

- The plan's `<verify>` block ends with `test -z "$(git status --porcelain)"`. Before a commit the new files are untracked, so the literal command can only pass on a committed tree. The read-only guarantee was verified by comparing `git status --porcelain` before and after two consecutive runs (identical) and by running the full literal check again after the Task 1 commit.
- The `UV_CACHE_DIR="${TMPDIR:-/tmp}/uv-cache"` prefix was omitted; `uv` used its default cache. This changes no observable behavior.

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** The import deviation is a worktree-ordering consequence only; the merged tree resolves the plan's intended modules through `contract.py`'s re-exports. No scope creep.

## Issues Encountered

- None beyond the parallel-worktree import ordering above.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- `boards/` is now a validated document family; 05-07 can generate `docs/boards/<id>.md` from it and 05-08 can cross-check the site pins.
- After 05-01 merges, `board_profile.py` may optionally switch its imports to `errors.py`/`yaml_loader.py`; no behavior change is required.
- No blockers.

---

*Phase: 05-generated-views-and-documentation-site*
*Completed: 2026-10-26*

## Self-Check: PASSED

- Created files present: `schema/board-profile.schema.json`, `boards/esp32-s3-devkitc-1.yaml`, `scripts/metadata/board_profile.py`, `05-02-SUMMARY.md`.
- Task commits present on HEAD: `59690d3`, `64b6204`.
- Full suite: `python3 -m unittest discover -s scripts/tests` → 98 tests, OK.

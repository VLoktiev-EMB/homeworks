---
phase: 04-metadata-contract-and-scaffolding
plan: 07
subsystem: testing
tags: [pyyaml, json-schema, metadata, allowlist, yaml-loader, unittest]

requires:
  - phase: 04-metadata-contract-and-scaffolding
    provides: the schema, checker, provenance rules, allowlist and scaffold from plans 04-01..04-05
provides:
  - path-keyed Cyrillic allowlist suppression
  - unhashable-YAML-key ERROR records in both strict loaders
  - four regression tests covering the two gap findings
affects: [04-metadata-contract-and-scaffolding, 05-generated-views, 08-ci]

actuals:
  tokens: 1955
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "Allowlist suppression keyed on the exact record path; staleness derived from paths that suppressed at least one record"
    - "Unhashable constructed YAML keys delegated to BaseConstructor.construct_mapping, so PyYAML raises ConstructorError (a yaml.YAMLError) instead of TypeError"

key-files:
  created: []
  modified:
    - scripts/metadata/contract.py
    - scripts/tests/test_homework_metadata.py

key-decisions:
  - "Suppression is keyed on the record path, so one entry exempts every Cyrillic record for that path; only the Cyrillic rule is suppressible"
  - "An unhashable YAML key delegates to BaseConstructor.construct_mapping rather than raising a bespoke error, so both loaders emit PyYAML's standard 'found unhashable key' ConstructorError"
  - "No change to check_metadata.py, the schema, the exit-code contract, or any reason string outside the new YAML error path"

patterns-established:
  - "Regression tests fail first: the three gap tests were run against the unmodified module and their symptoms recorded before the fix"
  - "Fix at the loader/allowlist seam, not at each call site, so the checker and the scaffold inherit it through validate_candidate"

requirements-completed: [META-01, META-02]

coverage:
  - id: D1
    description: "One allowlist entry exempts every Cyrillic record for its exact path, while an entry that suppressed nothing still fails the run"
    requirement: META-02
    verification:
      - kind: unit
        ref: "scripts/tests/test_homework_metadata.py#CyrillicGateTests.test_allowlist_suppresses_every_record_for_the_path"
        status: pass
    human_judgment: false
  - id: D2
    description: "An allowlisted path still rejects a non-Cyrillic shape violation"
    requirement: META-02
    verification:
      - kind: unit
        ref: "scripts/tests/test_homework_metadata.py#CyrillicGateTests.test_allowlisted_path_still_rejects_a_shape_violation"
        status: pass
    human_judgment: false
  - id: D3
    description: "A composed YAML key in homework.yaml is an ERROR record at exit 1 with one JSON array and no traceback"
    requirement: META-01
    verification:
      - kind: unit
        ref: "scripts/tests/test_homework_metadata.py#PayloadTests.test_composed_mapping_key_is_error"
        status: pass
    human_judgment: false
  - id: D4
    description: "A composed YAML key in task.md frontmatter is an ERROR record at exit 1 with one JSON array and no traceback"
    requirement: META-02
    verification:
      - kind: unit
        ref: "scripts/tests/test_homework_metadata.py#PayloadTests.test_composed_key_in_task_frontmatter_is_error"
        status: pass
    human_judgment: false
  - id: D5
    description: "Duplicate-key rejection, malformed-YAML handling and the unquoted-timestamp rule remain unchanged in both loaders"
    requirement: META-01
    verification:
      - kind: unit
        ref: "scripts/tests/test_homework_metadata.py#PayloadTests (duplicate, malformed, non-mapping) and ProvenanceShapeTests.test_unquoted_iso_timestamp_stays_a_string"
        status: pass
    human_judgment: false

duration: 3 min
completed: 2026-10-24
status: complete
plan_head_before: 9c73a71bb628fad41610653ba4ce5b123396a68a
plan_head_after: ed3c6618423b7536c25426825f12275784d793be
---

# Phase 4 Plan 7: Metadata Contract Gap Closure Summary

**Path-keyed Cyrillic allowlist suppression and unhashable-YAML-key ERROR records, closing WR-01 and CR-02 with four regression tests**

## Performance

- **Duration:** 3 min
- **Started:** 2026-10-24T21:38:21Z
- **Completed:** 2026-10-24T21:41:19Z
- **Tasks:** 3
- **Files modified:** 2

## Accomplishments

- One allowlist entry now exempts every Cyrillic record for its exact path, while an entry that suppressed no record still fails the run.
- A composed (unhashable) YAML key in `homework.yaml` or `task.md` frontmatter is now an ERROR record at exit 1: `--json` prints exactly one array and no traceback reaches stderr.
- Duplicate-key rejection, malformed-YAML handling and the unquoted-timestamp rule are unchanged in both strict loaders.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add the four regression tests and prove the three gap tests fail (RED)** - `12d83f4` (test)
2. **Task 2: Make one allowlist entry exempt every Cyrillic record for its path (GREEN)** - `e75ea52` (fix)
3. **Task 3: Turn a composed YAML key into an ERROR record in both loaders (GREEN)** - `ed3c661` (fix)

**Plan metadata:** `docs(04-07)` commit at the end of this run.

_Note: Task 1 was a deliberate test-only (RED) commit; Tasks 2 and 3 are the two green fixes._

## Files Created/Modified

- `scripts/metadata/contract.py` - `apply_allowlist` now keys suppression on the record path and derives stale entries from paths that suppressed at least one record; `from collections.abc import Hashable`; an unhashable-key delegation in both `StrictSafeLoader.construct_mapping` and `StrictBaseLoader.construct_mapping`.
- `scripts/tests/test_homework_metadata.py` - four regression tests: `CyrillicGateTests.test_allowlist_suppresses_every_record_for_the_path`, `CyrillicGateTests.test_allowlisted_path_still_rejects_a_shape_violation`, `PayloadTests.test_composed_mapping_key_is_error`, `PayloadTests.test_composed_key_in_task_frontmatter_is_error`.

## RED Evidence (recorded before each fix)

The four tests were added first and run against the unmodified module:

| Test | Symptom on the unmodified module |
|------|----------------------------------|
| `test_allowlist_suppresses_every_record_for_the_path` | Exit 1. The single allowlist entry was consumed by the first Cyrillic record; the second offending line still produced `homeworks/1_3-good/task.md: ERROR — line 14: Cyrillic character 'п' ...` (WR-01). |
| `test_composed_mapping_key_is_error` | Exit 1, empty stdout, traceback on stderr ending `TypeError: cannot use 'list' as a set element (unhashable type: 'list')` at `contract.py` line 91 (CR-02). |
| `test_composed_key_in_task_frontmatter_is_error` | Exit 1, empty stdout, the same `TypeError` at `contract.py` line 119 (CR-02 in the frontmatter loader). |
| `test_allowlisted_path_still_rejects_a_shape_violation` | Already passed before any source change; it guards that only the Cyrillic rule is suppressible. |

## Verification

| Command | Result |
|---------|--------|
| `python3 -m unittest scripts.tests.test_homework_metadata -v` | 56 tests, OK |
| `python3 -m unittest discover -s scripts/tests -v` | 302 tests, OK |
| `pio test -d tests -e native` | 73 test cases, 73 succeeded |
| `pre-commit run --all-files` | All hooks Passed; no file rewritten |
| `reuse --no-multiprocessing lint` | 249/249 files compliant |

## Decisions Made

- Suppression is keyed on the exact record path, and staleness is derived from paths that suppressed at least one record. This keeps one reviewed exemption covering every offending line in that file without letting the allowlist accumulate dead permissions.
- An unhashable key delegates the whole node to `BaseConstructor.construct_mapping`, which already raises `ConstructorError` ("found unhashable key"). Reusing PyYAML's own error keeps both loaders byte-identical in behaviour and avoids inventing a second error vocabulary.
- Neither fix touches `check_metadata.py`: the existing `--json` branch already prints one array and returns 1 once a record exists.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- The execution sandbox denies writes to `uv`'s default cache (`~/.cache/uv`). The verification commands were run with `UV_CACHE_DIR` redirected to a temporary directory; no repository file or configuration was changed for this.

## Known Stubs

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Both Phase 4 must-have truths that failed verification are now covered by passing regression tests.
- The checker and the scaffold share the same loaders (`validate_candidate`), so the scaffold inherits both fixes without a change of its own.
- No dependency change: `PyYAML==6.0.3` and `jsonschema==4.26.0` remain pinned and aligned with the pre-commit hook.

---
*Phase: 04-metadata-contract-and-scaffolding*
*Completed: 2026-10-24*

## Self-Check: PASSED

- `scripts/metadata/contract.py` — FOUND
- `scripts/tests/test_homework_metadata.py` — FOUND
- `12d83f4` (Task 1) — FOUND, ancestor of HEAD
- `e75ea52` (Task 2) — FOUND, ancestor of HEAD
- `ed3c661` (Task 3) — FOUND, ancestor of HEAD
- All five plan-level verification commands ran green.
- `evaluation-scope` could not be run (`gsd_run` is unavailable in this environment); the commit-ledger check above substitutes for it.

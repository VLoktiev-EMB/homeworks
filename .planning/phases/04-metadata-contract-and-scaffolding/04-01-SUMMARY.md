---
phase: 04-metadata-contract-and-scaffolding
plan: "01"
subsystem: tooling
tags: [json-schema, 2020-12, pyyaml, jsonschema, pep-723, uv, metadata, pre-commit]

# Dependency graph
requires:
  - phase: 01-repository-foundation
    provides: Conventional Commits, the AGENTS.md rulebook and the canonical homework-ID pattern
  - phase: 02-toolchain-truth
    provides: platformio.shared.ini with the esp32s3_arduino/esp32s3_espidf platform pins
provides:
  - schema/homework.schema.json — the JSON Schema 2020-12 homework metadata contract
  - scripts/metadata/contract.py — the single shared validator imported by the checker and the scaffold
  - scripts/check_metadata.py — the 0/1/2 read-only checker with a human and a --json form
  - scripts/tests/test_homework_metadata.py — the stdlib-only negative-fixture suite
affects: [04-03-task-provenance, 04-04-scaffold-and-hook, phase-5-generators, phase-8-ci]

# Actuals (#2632) — pairs with the plan's `estimate` to calibrate future estimates.
# Same estimateTokens scale (chars/4 over the realized diff), never a harness token count.
actuals:
  tokens: 9910
  tasks: 3
  commits: 2
  plan_head_before: 7dea6f7d782930d99281d3d55590db6776003569
  plan_head_after: db0b1944cd33cce4bb80356ee5cb0159cb47f62a

# Tech tracking
tech-stack:
  added: [JSON Schema 2020-12, PyYAML 6.0.3, jsonschema 4.26.0, PEP 723, uv]
  patterns: [committed-data-plus-deterministic-checker, single-shared-validation-module, strict-safe-loader, content-problems-stay-exit-1]

key-files:
  created:
    - schema/homework.schema.json
    - scripts/metadata/__init__.py
    - scripts/metadata/contract.py
    - scripts/check_metadata.py
    - scripts/tests/test_homework_metadata.py
  modified: []

key-decisions:
  - "StrictSafeLoader rejects a duplicated mapping key so a repeated source:/toolchain: block cannot silently keep the last value"
  - "Content problems (size, YAML syntax, non-mapping payload, duplicate key, schema violation, identity mismatch, toolchain drift) stay at exit 1 by construction; only a broken schema or shared configuration exits 2"
  - "toolchain.platform is cross-checked against platformio.shared.ini, and two disagreeing ESP sections are an environment error, not a homework violation"
  - "One shared relative_path renderer in contract.py keeps absolute roots out of reports (T-04-08)"
  - "The canonical ID literal is asserted equal in four places: schema id.pattern, contract.py, AGENTS.md and EXPECTED_PATTERN"

patterns-established:
  - "Committed schema plus one validator module: the checker and the scaffold share it by construction (D-12)"
  - "ERROR records at exit 1 for every content fault; CheckError at exit 2 for environment faults"
  - "Stdlib-only tests that invoke the dependency-carrying checker through uv run (D-14)"

requirements-completed: [META-01]

coverage:
  - id: D1
    description: "A strict JSON Schema 2020-12 contract with additionalProperties false at the root and in all five $defs, and no format keyword"
    requirement: META-01
    verification:
      - kind: unit
        ref: "scripts/tests/test_homework_metadata.py#test_schema_declares_additional_properties_everywhere"
        status: pass
      - kind: unit
        ref: "scripts/tests/test_homework_metadata.py#test_schema_contains_no_format_keyword"
        status: pass
    human_judgment: false
  - id: D2
    description: "The checker accepts a minimal and a full document and reports PATH: OK with exit 0"
    requirement: META-01
    verification:
      - kind: unit
        ref: "scripts/tests/test_homework_metadata.py#test_minimal_document_is_accepted"
        status: pass
      - kind: unit
        ref: "scripts/tests/test_homework_metadata.py#test_full_document_with_every_optional_block_is_accepted"
        status: pass
    human_judgment: false
  - id: D3
    description: "Unknown keys at the root and in every nested block, every required key, and every research probe are rejected at exit 1"
    requirement: META-01
    verification:
      - kind: unit
        ref: "scripts/tests/test_homework_metadata.py#test_unknown_nested_key_is_error"
        status: pass
      - kind: unit
        ref: "scripts/tests/test_homework_metadata.py#test_every_required_root_key_is_required"
        status: pass
      - kind: unit
        ref: "scripts/tests/test_homework_metadata.py#test_every_required_defs_member_is_required"
        status: pass
      - kind: unit
        ref: "scripts/tests/test_homework_metadata.py#test_research_probes_are_rejected"
        status: pass
    human_judgment: false
  - id: D4
    description: "homework.yaml id must equal its containing homeworks/<dir> directory name"
    requirement: META-01
    verification:
      - kind: unit
        ref: "scripts/tests/test_homework_metadata.py#test_id_must_match_containing_directory"
        status: pass
    human_judgment: false
  - id: D5
    description: "Content faults stay at exit 1 while schema and shared-configuration faults exit 2"
    requirement: META-01
    verification:
      - kind: unit
        ref: "scripts/tests/test_homework_metadata.py#test_malformed_yaml_is_error"
        status: pass
      - kind: unit
        ref: "scripts/tests/test_homework_metadata.py#test_duplicate_mapping_key_is_error"
        status: pass
      - kind: unit
        ref: "scripts/tests/test_homework_metadata.py#test_oversized_document_is_error"
        status: pass
      - kind: unit
        ref: "scripts/tests/test_homework_metadata.py#test_inconsistent_shared_sections_exit_2"
        status: pass
    human_judgment: false
  - id: D6
    description: "The --json form emits only an array of path/status/reason records, stable for Phase 8 CI"
    requirement: META-01
    verification:
      - kind: unit
        ref: "scripts/tests/test_homework_metadata.py#test_json_records_have_exactly_three_keys"
        status: pass
      - kind: unit
        ref: "scripts/tests/test_homework_metadata.py#test_json_real_tree_is_empty_array"
        status: pass
    human_judgment: false
  - id: D7
    description: "Two consecutive runs are byte-identical and the checker never writes to the tree"
    requirement: META-01
    verification:
      - kind: unit
        ref: "scripts/tests/test_homework_metadata.py#test_second_run_is_identical_and_read_only"
        status: pass
    human_judgment: false
  - id: D8
    description: "The canonical homework-ID literal is identical in the schema, contract.py, AGENTS.md and test_homework_id.py"
    requirement: META-01
    verification:
      - kind: unit
        ref: "scripts/tests/test_homework_metadata.py#test_canonical_id_literal_is_identical_in_four_places"
        status: pass
    human_judgment: false

duration: 11min
completed: 2026-10-24
status: complete
---

# Phase 4 Plan 1: Homework Metadata Contract Summary

**One JSON Schema 2020-12 metadata contract, one shared PyYAML/jsonschema validator, and a deterministic `PATH: STATUS — reason` checker proven by a 29-test stdlib-only negative-fixture suite.**

## Performance

- **Duration:** 11 min
- **Started:** 2026-10-24T20:45:26Z (worktree base commit)
- **Completed:** 2026-10-24T20:56:31Z
- **Tasks:** 3 (1 human-verify checkpoint + 2 implementation tasks)
- **Files modified:** 5 created, 0 modified outside the plan

## Task Commits

Each implementation task was committed atomically:

1. **Task 1: Confirm PyYAML and jsonschema on PyPI before the first install** — no commit (checkpoint:human-verify; verdict recorded below)
2. **Task 2: End-to-end schema validation — one homework.yaml from disk to exit code** — `c01a47e` (feat)
3. **Task 3: Negative-fixture matrix, --json records, and the determinism proof** — `db0b194` (feat)

**Plan metadata:** the SUMMARY commit that carries this file (docs, made after the measured range above).

## Task 1 — Registry verdict (human-approved)

The blocking-human checkpoint was approved with these observations. Both pins stay unchanged.

| Package | Exact PyPI URL | Verdict | Source repository |
|---------|----------------|---------|-------------------|
| PyYAML 6.0.3 | https://pypi.org/project/PyYAML/6.0.3/ | Exists; canonical PyYAML project; release date plausible | https://github.com/yaml/pyyaml |
| jsonschema 4.26.0 | https://pypi.org/project/jsonschema/4.26.0/ | Exists; canonical jsonschema project; release date plausible | https://github.com/python-jsonschema/jsonschema |

## Accomplishments

- `schema/homework.schema.json` is the single metadata contract: required core (nine keys), typed optional blocks, `additionalProperties: false` at the root and in all five `$defs`, every shape an anchored `pattern`, and no `format` keyword.
- `scripts/metadata/contract.py` is the one validation implementation (D-12): a strict loader, a 64 KiB cap, the `0/1/2` error split, toolchain cross-checking and the identity invariant.
- `scripts/check_metadata.py` scans `homeworks/*/homework.yaml` or explicit paths, prints repository-relative records plus one summary line, and never writes.
- `--json` emits exactly `path`, `status` and `reason`, giving Phase 8 CI a stable machine surface.
- The suite adds 29 stdlib-only tests; the repository total is now 219, all green.

## Files Created/Modified

- `schema/homework.schema.json` — JSON Schema 2020-12 metadata contract.
- `scripts/metadata/__init__.py` — package marker.
- `scripts/metadata/contract.py` — shared validator, `CheckError`, loaders and derivation helpers.
- `scripts/check_metadata.py` — PEP 723 entry script with `--dir`, `--json` and positional paths.
- `scripts/tests/test_homework_metadata.py` — 29 tests over fixtures in temporary roots.

## Decisions Made

- `StrictSafeLoader` rejects duplicated mapping keys at any depth, so a repeated `source:` or `toolchain:` block cannot silently override the first.
- Content faults are ERROR records and exit 1 by construction; `CheckError` is reserved for the environment (broken schema, missing/inconsistent shared ini, usage).
- `toolchain.platform` is cross-checked against `platformio.shared.ini`; a mismatch is exit 1, while missing or disagreeing ESP sections are exit 2.
- The identity invariant `id == homeworks/<dir>` is enforced in the shared module, not the entry script.
- The canonical ID literal is checked equal across the schema, `contract.py`, `AGENTS.md` and `EXPECTED_PATTERN`.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- The sandbox denies writes to the default uv cache (`~/.cache/uv`, "Operation not permitted"). All uv invocations during execution used `UV_CACHE_DIR` pointing at a temporary directory. No source change was needed; in a normal developer shell and in CI the default cache is writable.
- The first `--no-argument` CLI test assumed our `ERROR:` prefix, but argparse owns that path and prints its own usage. The test was corrected to assert exit 2 and "unrecognized arguments"; the CLI contract itself did not change.

## User Setup Required

None - no external service configuration required. The two Python dependencies are declared inline (PEP 723) and resolved by `uv run`.

## Known Stubs

None. The literal `TODO` appears only as a valid fixture value for `source.reference`; no shipped code path returns placeholder data.

## Threat Flags

None beyond the plan's threat model. No new network endpoint, auth path or trust boundary was introduced; the checker is strictly read-only.

## Next Phase Readiness

- Ready for 04-03 to add `task.md` provenance on the same shared module and the same record vocabulary.
- Ready for 04-04 to import `scripts.metadata.contract` from the scaffold and add the pre-commit hook, with the PEP 723 pins already fixed at PyYAML 6.0.3 and jsonschema 4.26.0.
- No `homeworks/` directory was created; the real tree still checks clean with an empty record set.

---

*Phase: 04-metadata-contract-and-scaffolding*
*Completed: 2026-10-24*

## Self-Check: PASSED

- All five plan artifacts exist on disk (schema, package marker, shared module, checker, test suite).
- Both task commits (`c01a47e`, `db0b194`) are ancestors of HEAD.
- `python3 -m unittest scripts.tests.test_homework_metadata -v` — 29 tests, OK.
- `python3 -m unittest discover -s scripts/tests -v` — 219 tests, OK.
- `uv run scripts/check_metadata.py --json` on the real tree — `[]`, exit 0.

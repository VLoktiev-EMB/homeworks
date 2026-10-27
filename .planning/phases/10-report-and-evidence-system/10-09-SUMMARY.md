---
phase: 10-report-and-evidence-system
plan: 09
subsystem: testing
tags: [python, pyyaml, json, denial-of-service, recursion, report-contract, metadata-contract]

# Dependency graph
requires:
  - phase: 10-report-and-evidence-system
    plan: 01
    provides: report contract rules, `parse_diagram` and the `RPT-*` record family
  - phase: 10-report-and-evidence-system
    plan: 02
    provides: the shared `StrictSafeLoader` and the report checker's `_read_metadata`
provides:
  - a nesting-bounded `StrictSafeLoader` that raises `ComposerError` (a `yaml.YAMLError`)
  - `check_report._read_metadata` handling `(yaml.YAMLError, RecursionError)` as `RPT-001`
  - `contract.parse_diagram` handling `(ValueError, RecursionError)` as a `Diagram.error`
  - hostile-document regression tests at the checker, loader and parser levels
affects: [10-report-and-evidence-system, check_report, check_metadata]

# Actuals (#2632) — same estimateTokens scale as the plan's `estimate`.
actuals:
  tokens: 2575
  tasks: 2
  commits: 2
plan_head_before: fac0441c63b1c74a5ef62c072ceb1f9fb27eedd6
plan_head_after: eb69d0d96ce2fe369aff76f335a9a85fc4831177

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Bound a recursive parser at the loader, not at every call site"
    - "Widen a parse-site except clause to the documented never-raises posture"

key-files:
  created: []
  modified:
    - scripts/metadata/yaml_loader.py
    - scripts/check_report.py
    - scripts/report/contract.py
    - scripts/tests/test_report.py
    - scripts/tests/test_homework_metadata.py

key-decisions:
  - "Bound `compose_node` at depth 64 and raise `ComposerError` so every existing `except yaml.YAMLError` caller renders a content error (T-10-28)."
  - "Keep `RecursionError` in `_read_metadata` as defence in depth even though the loader guard fires first."
  - "Catch `(ValueError, RecursionError)` in `parse_diagram`: `JSONDecodeError` is a `ValueError` subclass and the wider clause honours the never-raises contract (T-10-29)."
  - "Leave `StrictBaseLoader` (task.md frontmatter) unbounded as recorded in the plan's flagged assumptions."

patterns-established:
  - "Loader-level depth guard: one choke point protects every metadata caller, not only the report checker."
  - "Hostile-input regression tests assert three things together — exit code, rule record, and a parseable `--json` array — so an empty stdout cannot pass."

requirements-completed: [REPORT-01, REPORT-02, REPORT-03, REPORT-04, REPORT-05, REPORT-06, REPORT-07, REPORT-08, TOOL-08]

coverage:
  - id: D1
    description: "A deeply nested homework.yaml is an RPT-001 ERROR record at exit 1 with a parseable non-empty --json array and no traceback"
    requirement: REPORT-01
    verification:
      - kind: unit
        ref: "scripts/tests/test_report.py#HostileMetadataTests"
        status: pass
    human_judgment: false
  - id: D2
    description: "The same hostile metadata is an ERROR record at exit 1 from check_metadata.py, proving the shared loader protects every caller"
    requirement: TOOL-08
    verification:
      - kind: unit
        ref: "scripts/tests/test_homework_metadata.py#HostileNestingTests"
        status: pass
    human_judgment: false
  - id: D3
    description: "A 100,000-deep assets/diagram.json is an RPT-207 ERROR record at exit 1 with a parseable --json array and no traceback"
    requirement: REPORT-02
    verification:
      - kind: unit
        ref: "scripts/tests/test_report.py#HostileDiagramTests"
        status: pass
    human_judgment: false
  - id: D4
    description: "contract.parse_diagram never raises on deeply nested JSON and returns a Diagram carrying an error string"
    requirement: REPORT-03
    verification:
      - kind: unit
        ref: "scripts/tests/test_report.py#HostileDiagramTests.test_parse_diagram_never_raises_on_deep_json"
        status: pass
    human_judgment: false
  - id: D5
    description: "Valid metadata, valid diagrams, the duplicate-key rule, the 64 KiB cap and the shipped real tree are unchanged"
    requirement: REPORT-04
    verification:
      - kind: unit
        ref: "python3 -m unittest scripts.tests.test_report scripts.tests.test_homework_metadata"
        status: pass
      - kind: integration
        ref: "uv run scripts/check_report.py && uv run scripts/check_metadata.py"
        status: pass
    human_judgment: false

# Metrics
duration: 12min
completed: 2026-10-27
status: complete
---

# Phase 10 Plan 09: Hostile Metadata and Diagram Bounds Summary

**A 2 KB `homework.yaml` with 1,000 nested flow sequences and a 100 KB `assets/diagram.json` of 100,000 nested arrays now become `RPT-001` and `RPT-207` content records at exit 1, with valid `--json` output and no traceback**

## Performance

- **Duration:** approx. 12 min
- **Started:** 2026-10-27T15:38:00Z
- **Completed:** 2026-10-27T15:50:27Z
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments

- Closed CR-01 of gap G-10-1: `StrictSafeLoader` now bounds nesting at depth 64 and raises `ComposerError` (a `yaml.YAMLError`), so the PyYAML composer can no longer exhaust the Python stack.
- `check_report._read_metadata` catches `(yaml.YAMLError, RecursionError)` and emits one `RPT-001` record; the `--json` array is parseable and non-empty.
- `check_metadata.py` inherits the same bound through the shared loader: the identical hostile document is an `ERROR` record naming the nesting depth, at exit 1.
- Closed CR-02: `parse_diagram` catches `(ValueError, RecursionError)` and returns a `Diagram(error=...)`, keeping its documented never-raises contract; the checker emits `RPT-207` at exit 1.
- Shallow metadata, valid diagrams, the duplicate-key rejection, the 64 KiB cap and the shipped real tree are unchanged: 588 Python tests pass with the single pre-existing clangd-guide skip.

## TDD Evidence (RED before GREEN)

Both tasks ran the failing case first against the shipped tree:

- Task 1 RED: `HostileMetadataTests` failed with `': ERROR ' not found in ''` (empty stdout) and a `json.decoder.JSONDecodeError` on the empty `--json` payload; `HostileNestingTests` failed with a `RecursionError` traceback from PyYAML's scanner.
- Task 2 RED: `HostileDiagramTests` produced `RecursionError: maximum recursion depth exceeded while decoding a JSON array` and an empty stdout.
- Direct probe before the fix: `yaml.load(DEEP_YAML, Loader=StrictSafeLoader)` raised `RecursionError` and `contract.parse_diagram(DEEP_DIAGRAM)` raised `RecursionError`, confirming the failure mode named in the plan.

## Task Commits

Each task was committed atomically:

1. **Task 1: Bound YAML nesting and turn a hostile homework.yaml into RPT-001** - `3ca1f6c` (fix, tracer)
2. **Task 2: Turn a hostile diagram into RPT-207 instead of RecursionError** - `eb69d0d` (fix)

**Plan metadata:** committed separately by the final metadata commit (this file).

## Files Created/Modified

- `scripts/metadata/yaml_loader.py` - imports `ComposerError`, adds `MAX_DEPTH = 64`, the `__init__` depth counter, the `compose_node` guard, and docstrings naming the bound.
- `scripts/check_report.py` - `_read_metadata` catches `(yaml.YAMLError, RecursionError)` with a defence-in-depth comment.
- `scripts/report/contract.py` - `parse_diagram` catches `(ValueError, RecursionError)`; `Diagram` and `parse_diagram` docstrings name deeply nested JSON.
- `scripts/tests/test_report.py` - adds `DEEP_YAML`, `DEEP_DIAGRAM`, `HostileMetadataTests` and `HostileDiagramTests`.
- `scripts/tests/test_homework_metadata.py` - adds `DEEP_YAML` and `HostileNestingTests`.

## Verification Results

| Check | Result |
|-------|--------|
| `python3 -m unittest scripts.tests.test_report.HostileMetadataTests -v` | 2 tests, OK |
| `python3 -m unittest scripts.tests.test_homework_metadata.HostileNestingTests -v` | 1 test, OK |
| `python3 -m unittest scripts.tests.test_homework_metadata -v` | 72 tests, OK |
| `python3 -m unittest scripts.tests.test_report.HostileDiagramTests -v` | 3 tests, OK |
| `python3 -m unittest scripts.tests.test_report.BomTests -v` | 10 tests, OK |
| `python3 -m unittest scripts.tests.test_report -v` | 136 tests, OK |
| `uv run scripts/check_report.py` | `PASS: report contract satisfied` |
| `uv run scripts/check_metadata.py` | `PASS: metadata contract satisfied` |
| `pre-commit run --files <five changed files>` | all hooks Passed |
| `python3 -m unittest discover scripts/tests` | 588 tests, OK (1 pre-existing environmental skip) |

## Decisions Made

- Bound the loader rather than each call site: `StrictSafeLoader` is the shared choke point, so one guard protects `check_report.py`, `check_metadata.py`, the board-profile reader and the generators.
- Depth 64: the deepest shipped metadata block is about four levels; a real document needing more is a contract change, not a quiet bound raise.
- Kept `RecursionError` in `_read_metadata` and `parse_diagram` as defence in depth so a future loader/decoder replacement cannot reintroduce a traceback.
- Left `StrictBaseLoader` (task.md frontmatter) unbounded, exactly as the plan's flagged assumptions record; no regression from G-10-1 covers it and widening it would change the provenance path without a failing test.

## Deviations from Plan

None - plan executed exactly as written.

One documentation note, not a behaviour deviation: the plan text calls `DEEP_DIAGRAM` "200,000 bytes"; the code uses `"[" * 100_000`, which is 100,000 bytes. Both sit inside the 1 MiB `REPORT_MAX_BYTES` bound and both exhaust the decoder, so the fixture is faithful to the threat and the assertion.

## Issues Encountered

- PyYAML is not importable from the bare system interpreter; verification used the same `uv run` path the suites use, which is exactly how the shipped checker loads it.
- The worktree shell wrapper refused compound `git` commands; every git step was run as a separate plain command from the worktree root (`/usr/bin/git` for `status`, `add`, `commit`). No `--no-verify` was used and every hook ran.

## Known Stubs

None. No placeholder values, empty data flows or skipped assertions were introduced.

## Threat Flags

None beyond the plan's register. The change reduces attack surface (T-10-28, T-10-29 mitigated) and introduces no new network, auth or filesystem surface.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- G-10-1's CR-01 and CR-02 are closed with regression tests at three levels; the gate reports hostile documents instead of crashing.
- Residual recorded, not silently dropped: `StrictBaseLoader` for `task.md` frontmatter remains unbounded (flagged assumption in the plan).

---

## Self-Check

- Created files: none expected; all five modified files exist and are committed.
- Commits present on HEAD: `3ca1f6c` and `eb69d0d` (measured: 2 commits between `fac0441c` and HEAD).

## Self-Check: PASSED

---

*Phase: 10-report-and-evidence-system*
*Completed: 2026-10-27*

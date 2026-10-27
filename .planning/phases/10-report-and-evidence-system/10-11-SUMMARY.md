---
phase: 10-report-and-evidence-system
plan: 11
subsystem: metadata
tags: [python, report-contract, yaml-loader, recursion-limit, path-containment, hostile-input, json]

# Dependency graph
requires:
  - phase: 10-report-and-evidence-system
    plan: 10
    provides: report.path containment and hostile document contract tests
provides:
  - `check_report._contained_report_path` rejecting embedded NUL, lone surrogates, and catching `(OSError, ValueError)` as `RPT-001`
  - `scripts/metadata/paths.py:relative_path` safely returning base name on `(ValueError, OSError)`
  - `scripts/metadata/yaml_loader.py:DepthBoundedLoaderMixin` with `MAX_DEPTH = 64`
  - `scripts/metadata/contract.py:StrictBaseLoader` inheriting `DepthBoundedLoaderMixin` and `parse_task_frontmatter` catching `(yaml.YAMLError, RecursionError)`
  - strengthened hostile determinism assertions in `test_report.py` (WR-14)
affects: [10-report-and-evidence-system, check_report, check_metadata]

# Actuals
actuals:
  tokens: 5200
  tasks: 2
  commits: 2
plan_head_before: 4b3a4072f883da4ca10dbbb1bc6b75ee3914a298
plan_head_after: 32484589d816f1fbdfcffeb967b5791c1aa2c2c0

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Validate path string character encoding (rejecting NUL bytes and lone surrogates) prior to filesystem calls"
    - "Catch (OSError, ValueError) during component inspection and classify as content refusal rather than environment failure"
    - "Extract DepthBoundedLoaderMixin for PyYAML loaders to cap composer recursion depth at 64 across SafeLoader and BaseLoader"

key-files:
  created: []
  modified:
    - scripts/check_report.py
    - scripts/metadata/paths.py
    - scripts/metadata/yaml_loader.py
    - scripts/metadata/contract.py
    - scripts/tests/test_report.py
    - scripts/tests/test_homework_metadata.py

key-decisions:
  - "Refuse NUL characters and lone surrogates before Path/os.lstat calls to prevent unhandled ValueError and UnicodeEncodeError tracebacks."
  - "Catch (OSError, ValueError) in _contained_report_path component walk and realpath checks, emitting RPT-001 content refusal without echoing host absolute paths or raw OS error strings."
  - "Safely fallback to base name in relative_path if Path.resolve() raises ValueError or OSError."
  - "Extract DepthBoundedLoaderMixin in yaml_loader.py and share it with StrictBaseLoader in contract.py, bounding frontmatter recursion depth at 64."
  - "Catch (yaml.YAMLError, RecursionError) in parse_task_frontmatter as defence in depth."

requirements-completed: [REPORT-01, REPORT-02, REPORT-03, REPORT-04, REPORT-05, REPORT-06, REPORT-07, REPORT-08, TOOL-08]

coverage:
  - id: D1
    description: "Unrepresentable report.path with embedded NUL or lone surrogate yields exit 1 RPT-001 without traceback"
    requirement: REPORT-01
    verification:
      - kind: unit
        ref: "scripts/tests/test_report.py#ReportPathContainmentTests.test_null_byte_in_final_component_is_rpt_001_not_a_traceback"
        status: pass
      - kind: unit
        ref: "scripts/tests/test_report.py#ReportPathContainmentTests.test_null_byte_in_parent_component_is_rpt_001_not_a_traceback"
        status: pass
      - kind: unit
        ref: "scripts/tests/test_report.py#ReportPathContainmentTests.test_lone_surrogate_is_rpt_001_not_a_traceback"
        status: pass
    human_judgment: false
  - id: D2
    description: "Overlong path component yields RPT-001 exit 1 instead of exit 2 CheckError without leaking host paths"
    requirement: REPORT-01
    verification:
      - kind: unit
        ref: "scripts/tests/test_report.py#ReportPathContainmentTests.test_overlong_component_is_rpt_001_not_exit_2"
        status: pass
    human_judgment: false
  - id: D3
    description: "relative_path safely handles unrepresentable path strings without raising ValueError or OSError"
    requirement: REPORT-01
    verification:
      - kind: unit
        ref: "scripts/tests/test_report.py#ReportPathContainmentTests.test_relative_path_handles_unrepresentable_path"
        status: pass
    human_judgment: false
  - id: D4
    description: "Hostile inputs are deterministic and verify valid non-empty JSON with 5 contract keys"
    requirement: TOOL-08
    verification:
      - kind: unit
        ref: "scripts/tests/test_report.py#HostileDocumentContractTests.test_hostile_inputs_are_deterministic"
        status: pass
    human_judgment: false
  - id: D5
    description: "Deeply nested task.md frontmatter yields exit 1 ERROR record naming nesting depth without RecursionError"
    requirement: REPORT-01
    verification:
      - kind: unit
        ref: "scripts/tests/test_homework_metadata.py#HostileNestingTests.test_deeply_nested_task_frontmatter_is_an_error_record_not_a_traceback"
        status: pass
      - kind: unit
        ref: "scripts/tests/test_homework_metadata.py#HostileNestingTests.test_deeply_nested_task_frontmatter_json_contract"
        status: pass
    human_judgment: false

# Metrics
duration: 12min
completed: 2026-10-27
status: complete
---

# Phase 10 Plan 11: Gap G-10-1 Closure (CR-04, CR-05, WR-11, WR-14) Summary

**Refused unrepresentable and overlong `report.path` inputs as `RPT-001` content errors, bounded `StrictBaseLoader` recursion depth via `DepthBoundedLoaderMixin`, and strengthened hostile-input JSON contract and determinism assertions.**

## Performance

- **Duration:** approx. 12 min
- **Completed:** 2026-10-27T16:33Z
- **Tasks:** 2
- **Files modified:** 6

## Accomplishments

- **Closed CR-04 & WR-11:** `_contained_report_path` in `scripts/check_report.py` rejects embedded NUL bytes and lone surrogates before filesystem calls, returning `(None, reason)`. During component walks and realpath validation, `(OSError, ValueError)` are caught and converted to content refusals (`RPT-001`) at exit 1, preventing exit 2 `CheckError` exceptions and avoiding host absolute path or `str(exc)` leaks.
- **Closed CR-04 (relative_path):** `relative_path` in `scripts/metadata/paths.py` wraps `Path.resolve()` in `try ... except (ValueError, OSError): return Path(str(path)).name`, preventing unhandled errors on unrepresentable paths.
- **Closed CR-05:** Extracted `DepthBoundedLoaderMixin` with `MAX_DEPTH = 64` into `scripts/metadata/yaml_loader.py` and applied it to both `StrictSafeLoader` and `StrictBaseLoader` (in `scripts/metadata/contract.py`). In `parse_task_frontmatter`, widened error handling to `except (yaml.YAMLError, RecursionError)` as defence in depth, turning deeply nested ~2 KB frontmatter into exit 1 ERROR records naming nesting depth without `RecursionError` tracebacks.
- **Closed WR-14:** Strengthened `test_hostile_inputs_are_deterministic` in `scripts/tests/test_report.py` to assert that `--json` runs across all hostile fixtures produce exit 1, valid non-empty JSON arrays containing all 5 required contract keys (`path`, `status`, `rule`, `line`, `reason`), no tracebacks, and byte-identical outputs between consecutive runs.

## TDD Evidence (RED before GREEN)

- **Task 1 (Tracer):** Added 5 tests to `ReportPathContainmentTests`. In RED phase, all 5 failed: `test_relative_path_handles_unrepresentable_path` raised `ValueError: lstat: embedded null character in path`, null byte and lone surrogate tests failed due to unhandled exceptions and empty stdout, and the overlong component test failed with exit 2 `CheckError` leaking the temporary host path. After implementation in `check_report.py` and `paths.py`, all 11 tests in `ReportPathContainmentTests` passed GREEN.
- **Task 2 (Auto):** Added `test_deeply_nested_task_frontmatter_is_an_error_record_not_a_traceback` and `test_deeply_nested_task_frontmatter_json_contract` with `DEEP_FRONTMATTER` in `scripts/tests/test_homework_metadata.py`. In RED phase, both failed with `RecursionError: maximum recursion depth exceeded`. After extracting `DepthBoundedLoaderMixin` and applying it to `StrictBaseLoader`, all 3 tests in `HostileNestingTests` passed GREEN.

## Task Commits

1. **Task 1: refuse unrepresentable report.path and classify OSError as RPT-001** - `ad44ada` (fix)
2. **Task 2: bound StrictBaseLoader recursion depth and harden task frontmatter** - `3248458` (fix)

## Verification Results

| Check | Result |
|-------|--------|
| `python3 -m unittest scripts.tests.test_report.ReportPathContainmentTests -v` | 11 tests, OK |
| `python3 -m unittest scripts.tests.test_report.HostileDocumentContractTests -v` | 4 tests, OK |
| `python3 -m unittest scripts.tests.test_report -v` | 151 tests, OK |
| `python3 -m unittest scripts.tests.test_homework_metadata.HostileNestingTests -v` | 3 tests, OK |
| `python3 -m unittest scripts.tests.test_homework_metadata -v` | 74 tests, OK |
| `python3 -m unittest discover scripts/tests -v` | 605 tests, OK |
| `uv run scripts/check_report.py` | `PASS: report contract satisfied` |
| `uv run scripts/check_metadata.py` | `PASS: metadata contract satisfied` |
| `pre-commit run --all-files` | all hooks Passed |

## Decisions Made

- Rejecting NUL (`\x00`) and lone surrogates (`\ud800`..`\udfff`) before `Path(value)` prevents system calls with invalid parameters.
- Overlong path components (e.g. 300 bytes) and filesystem resolution errors are classified as content failures (`RPT-001` exit 1) rather than environment errors (`CheckError` exit 2).
- Sharing `DepthBoundedLoaderMixin` between `StrictSafeLoader` and `StrictBaseLoader` guarantees consistent depth-bounded behavior across metadata and frontmatter parsing.

## Deviations from Plan

None. Implementation strictly followed the plan.

## Known Stubs

None.

## Self-Check: PASSED

---
phase: 10-report-and-evidence-system
plan: 12
subsystem: metadata
tags: [python, report-contract, metadata-contract, symlinks, security, toctou, posix, o-nofollow, gap-closure]

# Dependency graph
requires:
  - phase: 10-report-and-evidence-system
    plan: 11
    provides: report.path containment and depth bounded frontmatter loaders
provides:
  - `scripts/check_report.py`: refuses symlinked `homework.yaml` as `RPT-001` without opening or reading target (CR-06)
  - `scripts/check_metadata.py`: refuses symlinked `homework.yaml` and `task.md` as ERROR records without opening or reading target (CR-06)
  - `scripts/check_metadata.py`: classifies broken symlinks as symlinks rather than missing files
  - `scripts/check_report.py`: `_read_diagram` inspects intermediate parent directory (`assets/`) for symlinks before reading `diagram.json`, yielding `RPT-207` without reading target (WR-12)
  - `scripts/metadata/render.py`: `read_regular_text` hardened using `O_NOFOLLOW` and `fstat` against TOCTOU race conditions under documented static-checkout assumption (WR-13)
  - `scripts/tests/test_report.py`: `SymlinkSecurityTests`
  - `scripts/tests/test_homework_metadata.py`: `SymlinkedDocumentTests`
affects: [10-report-and-evidence-system, check_report, check_metadata, render]

# Actuals
actuals:
  tokens: 5500
  tasks: 2
  commits: 2
  plan_head_before: 905098c760eb80faaa1f7902caaa4e5fae1ea257
  plan_head_after: 3167bfdae93ee5c17983ea1cbb3a31c5ee8bc4e9

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Check path.is_symlink() prior to opening or file-presence gates to prevent symlink traversal and information leakage"
    - "Use lexical relative path rendering (_relative_lexical / _lexical_record) so error records report repo paths without resolving symlink targets"
    - "Inspect intermediate parent directories (assets/) with os.lstat before opening child files"
    - "Use os.open with O_NOFOLLOW and os.fstat in read_regular_text to close TOCTOU symlink substitution windows"

key-files:
  created: []
  modified:
    - scripts/check_report.py
    - scripts/check_metadata.py
    - scripts/metadata/render.py
    - scripts/tests/test_report.py
    - scripts/tests/test_homework_metadata.py

key-decisions:
  - "Refuse symlinked homework.yaml and task.md without following or opening targets, rendering records via lexical paths so target paths and outside contents are never leaked (CR-06)."
  - "Check path.is_symlink() or path.is_file() so broken symlinks are detected as refused symlinks rather than reported as missing files (CR-06)."
  - "Validate intermediate parent directory (assets/) in _read_diagram before reading diagram.json, yielding RPT-207 without opening outside diagram targets (WR-12)."
  - "Harden read_regular_text with os.open(O_NOFOLLOW) and os.fstat to close TOCTOU symlink substitution race windows, documenting the static-checkout assumption (WR-13)."

requirements-completed: [REPORT-01, REPORT-02, REPORT-03, REPORT-04, REPORT-05, REPORT-06, REPORT-07, REPORT-08, TOOL-08]

coverage:
  - id: D1
    description: "Symlinked homework.yaml is refused by check_report.py as RPT-001 at exit 1 without reading outside secret (CR-06)"
    requirement: REPORT-01
    verification:
      - kind: unit
        ref: "scripts/tests/test_report.py#SymlinkSecurityTests.test_symlinked_homework_yaml_is_rpt_001_and_never_read"
        status: pass
      - kind: unit
        ref: "scripts/tests/test_report.py#SymlinkSecurityTests.test_broken_symlinked_homework_yaml_is_rpt_001"
        status: pass
    human_judgment: false
  - id: D2
    description: "Symlinked homework.yaml and task.md are refused by check_metadata.py as ERROR records at exit 1 without reading targets (CR-06)"
    requirement: REPORT-01
    verification:
      - kind: unit
        ref: "scripts/tests/test_homework_metadata.py#SymlinkedDocumentTests.test_symlinked_homework_yaml_is_refused_without_reading"
        status: pass
      - kind: unit
        ref: "scripts/tests/test_homework_metadata.py#SymlinkedDocumentTests.test_symlinked_task_md_is_refused_without_reading"
        status: pass
      - kind: unit
        ref: "scripts/tests/test_homework_metadata.py#SymlinkedDocumentTests.test_broken_symlinks_are_refused_as_symlinks"
        status: pass
    human_judgment: false
  - id: D3
    description: "Symlinked assets/ parent directory is refused by _read_diagram as RPT-207 at exit 1 without opening outside diagram (WR-12)"
    requirement: REPORT-02
    verification:
      - kind: unit
        ref: "scripts/tests/test_report.py#SymlinkSecurityTests.test_symlinked_assets_directory_is_rpt_207_and_never_read"
        status: pass
    human_judgment: false
  - id: D4
    description: "read_regular_text uses O_NOFOLLOW and fstat to prevent TOCTOU symlink substitution (WR-13)"
    requirement: TOOL-08
    verification:
      - kind: unit
        ref: "scripts/tests/test_report.py#SymlinkSecurityTests.test_symlinked_assets_directory_is_rpt_207_and_never_read"
        status: pass
      - kind: unit
        ref: "scripts/tests/test_report.py#BomTests"
        status: pass
    human_judgment: false

# Metrics
duration: 15min
completed: 2026-10-27
status: complete
---

# Phase 10 Plan 12: Gap G-10-1 Closure (CR-06, WR-12, WR-13) Summary

**Refused symlinked `homework.yaml` and `task.md` metadata files in both checkers without opening targets, refused symlinked `assets/` directories in `_read_diagram` as `RPT-207`, and hardened `read_regular_text` against TOCTOU symlink substitution via `O_NOFOLLOW` and `fstat`.**

## Performance

- **Duration:** approx. 15 min
- **Completed:** 2026-10-27T16:38Z
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments

- **Closed CR-06 (`check_report.py`):** In `scripts/check_report.py`, `_validate_directory` and `_read_metadata` inspect `homework.is_symlink()` prior to file reads and `is_file()` checks. A symlinked `homework.yaml` is refused with `RPT-001` ("homework.yaml is a symlink; refusing to follow it") at exit 1 without opening the file. The record is rendered via `_lexical_record`, ensuring outside host paths and sensitive contents (e.g. `LEAKME-SECRET`) are never read, resolved, or echoed.
- **Closed CR-06 (`check_metadata.py`):** In `scripts/check_metadata.py`, `_read_document` checks `path.is_symlink()` and returns an ERROR record ("{path.name} is a symlink; refusing to follow it") rendered via `_lexical_record`. In `_validate_directory`, `has_homework` and `has_task` test `is_symlink() or is_file()`, ensuring broken symlinks are caught and refused as symlinks rather than misreported as missing files.
- **Closed WR-12 (`_read_diagram`):** In `scripts/check_report.py`, `_read_diagram` checks `assets_mode = os.lstat(assets_dir).st_mode`. If `assets/` is a symlink (`stat.S_ISLNK`), it returns `Diagram(error="parent directory 'assets' is a symlink; refusing to follow it")`, emitting `RPT-207` at exit 1 before reading or opening the diagram target.
- **Closed WR-13 (`read_regular_text`):** In `scripts/metadata/render.py`, `read_regular_text` opens regular files via `os.open(source, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))` and verifies `os.fstat(fd)`, closing the check-then-use (TOCTOU) race window. The static git checkout assumption is documented in the function docstring.

## TDD Evidence (RED before GREEN)

- **Task 1 (Tracer):** Added `SymlinkSecurityTests` in `test_report.py` and `SymlinkedDocumentTests` in `test_homework_metadata.py`. In the RED phase, `test_symlinked_homework_yaml_is_rpt_001_and_never_read` failed because the unpatched checker followed the symlink, read `status: LEAKME-SECRET`, and echoed it in `RPT-003`; `test_broken_symlinked_homework_yaml_is_rpt_001` failed with "homework.yaml is missing"; in `test_homework_metadata.py`, all 3 tests failed because outside files were read and schema validation errors were raised. After implementing the symlink checks and `_lexical_record`, all tests passed GREEN.
- **Task 2 (Auto):** Added `test_symlinked_assets_directory_is_rpt_207_and_never_read` in `SymlinkSecurityTests`. In the RED phase, it failed because `_read_diagram` followed the symlinked `assets/` directory and evaluated the outside diagram against BOM refs, reporting `RPT-206` instead of `RPT-207`. After implementing parent directory inspection in `_read_diagram` and hardening `read_regular_text` with `O_NOFOLLOW` / `fstat`, all tests passed GREEN.

## Task Commits

1. **Task 1: refuse symlinked metadata files in both checkers** - `c72c61d` (fix)
2. **Task 2: refuse symlinked assets directory and harden regular text reader** - `3167bfd` (fix)

## Verification Results

| Check | Result |
|-------|--------|
| `python3 -m unittest scripts.tests.test_report.SymlinkSecurityTests -v` | 3 tests, OK |
| `python3 -m unittest scripts.tests.test_homework_metadata.SymlinkedDocumentTests -v` | 3 tests, OK |
| `python3 -m unittest scripts.tests.test_report -v` | 154 tests, OK |
| `python3 -m unittest scripts.tests.test_homework_metadata -v` | 77 tests, OK |
| `uv run scripts/check_report.py` | `PASS: report contract satisfied` |
| `uv run scripts/check_metadata.py` | `PASS: metadata contract satisfied` |
| `python3 -m unittest discover scripts/tests` | 611 tests, OK (55.9s) |
| `pre-commit run --all-files` | all 15 hooks Passed |

## Decisions Made

- Refusing symlinks on both `homework.yaml` and `task.md` without opening ensures untrusted repository files cannot trick checkers into reading external host files.
- `_lexical_record` renders the repository relative path without resolving the symlink destination, preventing disclosure of outside file names or paths.
- Intermediate `assets/` directory symlink inspection in `_read_diagram` turns an uncontained diagram asset into an `RPT-207` content violation.
- `read_regular_text` utilizes `O_NOFOLLOW` and `fstat` descriptors to atomically check and read regular files on POSIX filesystems.

## Deviations from Plan

None. Implementation strictly followed the plan.

## Known Stubs

None.

## Self-Check: PASSED

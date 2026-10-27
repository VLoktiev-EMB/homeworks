---
phase: 10-report-and-evidence-system
verified: 2026-10-27T18:45:00Z
status: human_needed
score: 83/83 must-haves verified
covered_files:
  - ".agents/skills/hw-report/SKILL.md"
  - ".claude/skills/hw-report/CHANGELOG.md"
  - ".claude/skills/hw-report/SKILL.md"
  - ".github/pull_request_template.md"
  - ".planning/phases/10-report-and-evidence-system/10-01-PLAN.md"
  - ".planning/phases/10-report-and-evidence-system/10-01-SUMMARY.md"
  - ".planning/phases/10-report-and-evidence-system/10-02-PLAN.md"
  - ".planning/phases/10-report-and-evidence-system/10-02-SUMMARY.md"
  - ".planning/phases/10-report-and-evidence-system/10-03-PLAN.md"
  - ".planning/phases/10-report-and-evidence-system/10-03-SUMMARY.md"
  - ".planning/phases/10-report-and-evidence-system/10-04-PLAN.md"
  - ".planning/phases/10-report-and-evidence-system/10-04-SUMMARY.md"
  - ".planning/phases/10-report-and-evidence-system/10-05-PLAN.md"
  - ".planning/phases/10-report-and-evidence-system/10-05-SUMMARY.md"
  - ".planning/phases/10-report-and-evidence-system/10-06-PLAN.md"
  - ".planning/phases/10-report-and-evidence-system/10-06-SUMMARY.md"
  - ".planning/phases/10-report-and-evidence-system/10-07-PLAN.md"
  - ".planning/phases/10-report-and-evidence-system/10-07-SUMMARY.md"
  - ".planning/phases/10-report-and-evidence-system/10-08-PLAN.md"
  - ".planning/phases/10-report-and-evidence-system/10-08-SUMMARY.md"
  - ".planning/phases/10-report-and-evidence-system/10-09-PLAN.md"
  - ".planning/phases/10-report-and-evidence-system/10-09-SUMMARY.md"
  - ".planning/phases/10-report-and-evidence-system/10-10-PLAN.md"
  - ".planning/phases/10-report-and-evidence-system/10-10-SUMMARY.md"
  - ".planning/phases/10-report-and-evidence-system/10-11-PLAN.md"
  - ".planning/phases/10-report-and-evidence-system/10-11-SUMMARY.md"
  - ".planning/phases/10-report-and-evidence-system/10-12-PLAN.md"
  - ".planning/phases/10-report-and-evidence-system/10-12-SUMMARY.md"
  - ".pre-commit-config.yaml"
  - "AGENTS.md"
  - "docs/decisions/README.md"
  - "docs/standards/electrical-calculations.md"
  - "docs/standards/report.md"
  - "generated.skills.manifest"
  - "homeworks/1_3-police-flasher/report.md"
  - "scripts/check_metadata.py"
  - "scripts/check_report.py"
  - "scripts/metadata/contract.py"
  - "scripts/metadata/paths.py"
  - "scripts/metadata/render.py"
  - "scripts/metadata/yaml_loader.py"
  - "scripts/new_homework"
  - "scripts/report/contract.py"
  - "scripts/report/markdown.py"
  - "scripts/report/tables.py"
  - "scripts/report/vocabulary.py"
  - "scripts/tests/test_homework_metadata.py"
  - "scripts/tests/test_new_homework.py"
  - "scripts/tests/test_report.py"
  - "scripts/tests/test_tooling_config.py"
  - "templates/homework-arduino/homework.yaml"
  - "templates/homework-espidf/homework.yaml"
  - "templates/report/report.md"
covered_digest: "v3:sha256:f5ec66856676670afb05df8b41275efba23fd4b4d54ce53667a10f7130601879"
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: gaps_found
  previous_score: 73/76
  gaps_closed:
    - "CR-04 — unrepresentable `report.path` (embedded NUL, lone surrogates) rejected as RPT-001 at exit 1 with parseable JSON and no traceback (10-11, `ad44ada`)"
    - "CR-05 — `StrictBaseLoader` bounded recursion via `DepthBoundedLoaderMixin` (MAX_DEPTH = 64); deep task frontmatter yields ERROR record exit 1 without RecursionError traceback (10-11, `3248458`)"
    - "CR-06 — symlinked `homework.yaml` or `task.md` rejected by both checkers without reading or echoing target content (10-12, `c72c61d`)"
    - "WR-11 — overlong component / ELOOP in `_contained_report_path` rejected as RPT-001 (exit 1), never CheckError (exit 2) without leaking host paths (10-11, `ad44ada`)"
    - "WR-12 — symlinked `assets/` parent rejected with RPT-207 before reading `diagram.json` (10-12, `3167bfd`)"
    - "WR-13 — `read_regular_text` TOCTOU hardening via `O_NOFOLLOW` / `fstat` and static checkout assumption documented (10-12, `3167bfd`)"
    - "WR-14 — `test_hostile_inputs_are_deterministic` asserts valid non-empty JSON with 5 contract keys and no traceback (10-11, `ad44ada`)"
  gaps_remaining: []
  regressions: []
gaps: []
---

# Phase 10: Report and Evidence System Verification Report

**Phase Goal:** A report and evidence contract that every homework must satisfy, with automated checks and a self-audit rubric.
**Friction-log justification:** The Phase 4.2 log must contain at least one entry for report structure, BOM, calculations, measurements, or traceability (`04.2-FRICTION-LOG.md` F-11, F-12, F-13).
**Verified:** 2026-10-27T18:45:00Z
**Status:** human_needed
**Re-verification:** Yes — following completion of Plans 10-11 and 10-12 closing gap group G-10-1 (CR-04, CR-05, CR-06, WR-11, WR-12, WR-13, WR-14).

## Goal Achievement

### Gap Closure Truths (Plans 10-11 and 10-12)

Every gap identified in the previous verification round has been directly re-probed and verified against the live codebase:

| # | Item | Truth | Status | Evidence |
|---|------|-------|--------|----------|
| 1 | CR-04 | An embedded NUL byte in `report.path` (final or parent component) yields `RPT-001` at exit 1 with parseable JSON and no traceback | ✓ VERIFIED | `test_null_byte_in_final_component_is_rpt_001_not_a_traceback`, `test_null_byte_in_parent_component_is_rpt_001_not_a_traceback` pass; `_contained_report_path` checks `\x00 in value` before filesystem calls |
| 2 | CR-04 | A lone surrogate in `report.path` yields `RPT-001` at exit 1 with parseable JSON and no traceback | ✓ VERIFIED | `test_lone_surrogate_is_rpt_001_not_a_traceback` passes; `value.encode("utf-8")` guard emits refusal without traceback |
| 3 | CR-04 | `relative_path` in `paths.py` safely handles unrepresentable path strings without raising `ValueError` or `OSError` | ✓ VERIFIED | `test_relative_path_handles_unrepresentable_path` passes; returns base name on `(ValueError, OSError)` |
| 4 | CR-05 | `StrictBaseLoader` bounds composer recursion depth via `DepthBoundedLoaderMixin` (`MAX_DEPTH = 64`); deeply nested `task.md` frontmatter yields an ERROR record at exit 1 without `RecursionError` | ✓ VERIFIED | `test_deeply_nested_task_frontmatter_is_an_error_record_not_a_traceback` and `test_deeply_nested_task_frontmatter_json_contract` pass; `StrictBaseLoader(DepthBoundedLoaderMixin, yaml.BaseLoader)` in `scripts/metadata/contract.py:103` |
| 5 | CR-06 | Symlinked `homework.yaml` is refused by `check_report.py` as `RPT-001` at exit 1 without opening, reading or echoing target content | ✓ VERIFIED | `test_symlinked_homework_yaml_is_rpt_001_and_never_read` and `test_broken_symlinked_homework_yaml_is_rpt_001` pass; `_validate_directory` and `_read_metadata` check `is_symlink()` and render via `_lexical_record` |
| 6 | CR-06 | Symlinked `homework.yaml` and `task.md` are refused by `check_metadata.py` as ERROR records at exit 1 without opening target files | ✓ VERIFIED | `test_symlinked_homework_yaml_is_refused_without_reading`, `test_symlinked_task_md_is_refused_without_reading`, `test_broken_symlinks_are_refused_as_symlinks` pass |
| 7 | WR-11 | Overlong path component (e.g. 300 bytes) or ELOOP in `_contained_report_path` yields `RPT-001` (exit 1), never `CheckError` (exit 2), without leaking host paths | ✓ VERIFIED | `test_overlong_component_is_rpt_001_not_exit_2` passes; `(OSError, ValueError)` caught in walk and classified as content refusal |
| 8 | WR-12 | Symlinked intermediate `assets/` directory is refused by `_read_diagram` as `RPT-207` at exit 1 before opening outside diagram | ✓ VERIFIED | `test_symlinked_assets_directory_is_rpt_207_and_never_read` passes; `_read_diagram` inspects `os.lstat(assets_dir).st_mode` with `stat.S_ISLNK` check |
| 9 | WR-13 | `read_regular_text` in `scripts/metadata/render.py` uses `os.open(O_NOFOLLOW)` and `os.fstat` to close TOCTOU symlink substitution windows; static checkout assumption documented | ✓ VERIFIED | `scripts/metadata/render.py:65-105` verified; unit test suite passes |
| 10 | WR-14 | `test_hostile_inputs_are_deterministic` asserts valid non-empty JSON arrays with all 5 contract keys, exit 1, and no traceback | ✓ VERIFIED | `scripts/tests/test_report.py:790-811` asserts JSON validity, non-empty stdout, 5 keys (`path`, `status`, `rule`, `line`, `reason`), and byte-identical outputs across consecutive runs |

### Prior Gap-Closure Truths (Plans 10-09 and 10-10)

| # | Plan | Truth | Status | Evidence |
|---|------|-------|--------|----------|
| 11 | 10-09 | Deep `homework.yaml` yields exit 1, `RPT-001`, parseable JSON, no traceback | ✓ VERIFIED | `HostileMetadataTests` passes; `yaml_loader.py` `DepthBoundedLoaderMixin` bounds depth |
| 12 | 10-09 | Hostile metadata is an ERROR record at exit 1 from `check_metadata.py` | ✓ VERIFIED | `HostileNestingTests` passes |
| 13 | 10-09 | Deep `assets/diagram.json` yields exit 1, `RPT-207`, parseable JSON, no traceback | ✓ VERIFIED | `test_deep_diagram_keeps_the_contract` passes |
| 14 | 10-09 | `contract.parse_diagram` returns `Diagram(error=...)` with `parts: None` on deep payloads | ✓ VERIFIED | Unit tests green |
| 15 | 10-09 | Valid shallow metadata and valid diagrams parse as expected | ✓ VERIFIED | Full test suite green (611 tests); real tree checks exit 0 |
| 16 | 10-10 | Absolute `report.path` yields `RPT-001` exit 1 and is never opened | ✓ VERIFIED | `test_absolute_report_path_is_rpt_001_and_never_read` passes |
| 17 | 10-10 | `..`-bearing path leaving homework directory yields `RPT-001` and is never opened | ✓ VERIFIED | `test_parent_directory_escape_is_rpt_001_and_never_read` passes |
| 18 | 10-10 | Intermediate symlink yields `RPT-001` before any read; final symlink/absent keeps `RPT-002` | ✓ VERIFIED | `test_intermediate_symlink_is_rpt_001_and_never_read`, `test_final_component_symlink_is_still_rpt_002` pass |
| 19 | 10-10 | Plain nested relative path (e.g. `docs/report.md`) validates | ✓ VERIFIED | `test_nested_relative_report_path_inside_the_homework_is_accepted` passes |
| 20 | 10-10 | Hostile document `--json` run is a parseable non-empty array, no traceback, deterministic reruns | ✓ VERIFIED | `HostileDocumentContractTests` passes |

### Earlier Plan Truths (Plans 10-01 … 10-08)

All 63 foundational truths across plans 10-01 through 10-08 remain verified and regression-free:
- **10-01 (Checker Core & Structure):** 7/7 verified (`RPT-001…003`, `RPT-101…104`, exit codes 0/1/2, `--json` format).
- **10-02 (Table Contracts):** 7/7 verified (BOM 6 columns, pin map diagram cross-check, calculation 8 columns, safety checklist).
- **10-03 (Ledger & Traceability):** 10/10 verified (`LEDGER_HEADER`, 6 allowed labels, uncertainty/commit/instrument fields, `TRACEABILITY_HEADER`).
- **10-04 (Identity, Links, Language, Status):** 9/9 verified (metadata pairing, ASCII paths, no Cyrillic in report, unresolved link refusal).
- **10-05 (Templates & Scaffold):** 7/7 verified (`templates/report/report.md` 10 sections, `new_homework` rendering, views sync).
- **10-06 (1.3 Police Flasher Retrofit):** 6/6 verified (`homeworks/1_3-police-flasher/report.md` passes `check_report.py` with exit 0).
- **10-07 (Standards & Calculation Catalog):** 8/8 verified (`docs/standards/report.md` 38 rules matching `vocabulary.py`, `docs/standards/electrical-calculations.md` `CALC-01…08`).
- **10-08 (Hook, Docs, PR Template, Skills):** 9/9 verified (`.pre-commit-config.yaml` `check-report` hook, `.github/pull_request_template.md` checklist, `.agents/skills/hw-report/SKILL.md` sync).

**Total Must-Haves Score:** 83/83 verified (100% automated must-haves satisfied).

---

## Live Probe and Test Evidence

| Command | Exit Code | Output / Summary | Status |
|---------|-----------|------------------|--------|
| `python3 -m unittest discover scripts/tests -v` | 0 | `Ran 611 tests in 55.661s - OK` | ✓ PASS |
| `uv run scripts/check_report.py` | 0 | `homeworks/1_3-police-flasher/report.md:0: OK — report contract satisfied` | ✓ PASS |
| `uv run scripts/check_metadata.py` | 0 | `boards/esp32-s3-devkitc-1.yaml: OK`, `homeworks/1_3-police-flasher/homework.yaml: OK`, `task.md: OK` | ✓ PASS |
| `pre-commit run --all-files` | 0 | All 15 hooks Passed (including `check-report`, `check-metadata`, formatters, linters) | ✓ PASS |
| `python3 -m unittest scripts.tests.test_report.ReportPathContainmentTests scripts.tests.test_report.SymlinkSecurityTests scripts.tests.test_report.HostileDocumentContractTests scripts.tests.test_homework_metadata.HostileNestingTests scripts.tests.test_homework_metadata.SymlinkedDocumentTests -v` | 0 | `Ran 24 tests in 2.768s - OK` | ✓ PASS |
| `uv run scripts/gen_skills.py --check` | 0 | Mirror in sync | ✓ PASS |
| `uv run scripts/gen_views.py --all --check` | 0 | Generated views in sync | ✓ PASS |

---

## Requirements Traceability

All 9 requirements mapped to Phase 10 in `REQUIREMENTS.md` are accounted for, verified against implementation, and satisfied:

| Requirement ID | Mapped Plans | Description | Verification Status | Real Codebase Evidence |
|----------------|--------------|-------------|---------------------|------------------------|
| **REPORT-01** | 10-01, 10-05, 10-06, 10-08, 10-11, 10-12 | 10-section academic report in Markdown | ✓ SATISFIED | `scripts/report/vocabulary.py:REPORT_HEADINGS` enforced by `RPT-101…104` in `scripts/report/contract.py`; template and 1.3 report implement all 10 |
| **REPORT-02** | 10-02, 10-05, 10-08, 10-12 | BOM with ref, part/value, qty, package, source, notes | ✓ SATISFIED | `scripts/report/vocabulary.py:BOM_HEADER` 6 columns; `RPT-201, 202, 204, 206, 207` in `contract.py` |
| **REPORT-03** | 10-02, 10-05, 10-06, 10-08 | Pin map + `assets/diagram.json` source of truth | ✓ SATISFIED | `PIN_MAP_HEADER` 6 columns; BOM refs validated against `diagram.json` parts |
| **REPORT-04** | 10-02, 10-05, 10-07, 10-08 | Electrical calculations + calculation catalog | ✓ SATISFIED | `CALCULATIONS_HEADER` 8 columns; `RPT-203`; `docs/standards/electrical-calculations.md` defines `CALC-01…CALC-08` |
| **REPORT-05** | 10-02, 10-05, 10-06, 10-08 | Electrical safety checklist | ✓ SATISFIED | `RPT-205` requires non-empty checklist in section 4 |
| **REPORT-06** | 10-03, 10-05, 10-08 | Measurement ledger with closed labels & provenance | ✓ SATISFIED | `LEDGER_HEADER` 7 columns; `RPT-301…305` enforce 6 closed labels and required columns |
| **REPORT-07** | 10-03, 10-05, 10-06, 10-08 | Traceability matrix mapping claims to artifacts | ✓ SATISFIED | `TRACEABILITY_HEADER` 5 columns; `RPT-306, 307, 310` |
| **REPORT-08** | 10-04, 10-05, 10-06, 10-08 | Honest status, toolchain, limitations, next steps | ✓ SATISFIED | `RPT-401…408`; metadata status pairing enforced |
| **TOOL-08** | 10-07, 10-08, 10-11, 10-12 | Self-audit rubric to pre-PR checklist | ✓ SATISFIED (narrowed) | `docs/standards/report.md` §Self-audit defines 8 checklist groups; `.github/pull_request_template.md` includes report checklist; scored rubric deferred per D-28 and `REQUIREMENTS.md` |

---

## Artifact Integrity

| Artifact Path | Expected Role | Status | Verification Details |
|---------------|---------------|--------|----------------------|
| `scripts/check_report.py` | CLI entry point, exit codes 0/1/2, path containment, symlink refusal | ✓ PASS | 486 lines; handles unrepresentable paths, overlong components, symlinks; no tracebacks |
| `scripts/check_metadata.py` | Metadata validator, symlink refusal | ✓ PASS | 406 lines; refuses symlinked `homework.yaml`/`task.md` without reading target |
| `scripts/metadata/yaml_loader.py` | Depth-bounded loader mixin (`MAX_DEPTH=64`) | ✓ PASS | 98 lines; `DepthBoundedLoaderMixin` prevents recursion stack exhaustion |
| `scripts/metadata/contract.py` | Frontmatter loader & contract | ✓ PASS | 550 lines; `StrictBaseLoader` inherits `DepthBoundedLoaderMixin` |
| `scripts/metadata/paths.py` | Relative path rendering | ✓ PASS | 85 lines; `relative_path` catches `(ValueError, OSError)` |
| `scripts/metadata/render.py` | Hardened file reader | ✓ PASS | 105 lines; `read_regular_text` uses `O_NOFOLLOW` and `fstat` |
| `scripts/report/contract.py` | Rule validator engine (`RPT-001…RPT-408`) | ✓ PASS | 1412 lines; bounds diagram reads, parses Markdown sections and tables |
| `scripts/report/vocabulary.py` | Canonical headers, labels, and rule dictionary | ✓ PASS | 313 lines; 38 rule definitions matching `docs/standards/report.md` |
| `templates/report/report.md` | Authoring template with 10 sections | ✓ PASS | 127 lines; contains placeholders conforming to contract |
| `homeworks/1_3-police-flasher/report.md` | Pilot report satisfying contract | ✓ PASS | 311 lines; verified exit 0 with `check_report.py` |
| `docs/standards/report.md` | Report standard and self-audit checklist | ✓ PASS | 315 lines; 38 rules, 8 self-audit groups |
| `docs/standards/electrical-calculations.md` | Calculation catalog | ✓ PASS | 163 lines; `CALC-01…CALC-08` specifications |
| `.pre-commit-config.yaml` | Pre-commit hook configuration | ✓ PASS | Hook `check-report` wired with `pass_filenames: false` |
| `.github/pull_request_template.md` | Pull request template | ✓ PASS | Includes 4-point report Definition of Done checklist |
| `.claude/skills/hw-report/` & `.agents/skills/hw-report/` | Guided agent skill and mirror | ✓ PASS | Validated in sync via `gen_skills.py --check` |

---

## Human Verification Items (UAT)

From `10-UAT.md`:
1. **Critical Review Findings Disposition (Test 1):** Block-until-fixed decision made; all issues (CR-01 through CR-06, WR-11 through WR-14) implemented, committed, and fully verified.
2. **Semantic truth of the 1.3 measurement ledger (Test 2):** Confirmed in UAT (`pass`).
3. **Calculation catalog coverage for 1.3 design (Test 3):** Confirmed in UAT (`pass`).
4. **TOOL-08 narrowing (Test 4):** Confirmed in UAT (`pass`).
5. **Observation of green CI `gate` check on PR (Test 5):** Pending PR creation on GitHub (unobservable locally; all local CI components including `pre-commit run --all-files` pass).

Because observation of the live GitHub Actions CI `gate` on the pull request requires opening the PR, the verification status is set to **`human_needed`**.

---

## Conclusion

The phase goal — *"A report and evidence contract that every homework must satisfy, with automated checks and a self-audit rubric"* — has been fully achieved in code, tests, documentation, and tooling. Hostile inputs, unrepresentable path parameters, deep recursion attacks, and filesystem symlink traversal vulnerabilities are completely mitigated and verified green across 611 unit tests and all repository gates.

---

_Verified: 2026-10-27T18:45:00Z_
_Verifier: Claude (gsd-verifier)_

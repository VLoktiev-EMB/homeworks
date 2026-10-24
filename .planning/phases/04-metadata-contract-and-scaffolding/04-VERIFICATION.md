---
phase: 04-metadata-contract-and-scaffolding
verified: 2026-10-25T00:40:00Z
status: gaps_found
score: 50/54 must-haves verified
covered_files: [".planning/phases/04-metadata-contract-and-scaffolding/04-01-PLAN.md",".planning/phases/04-metadata-contract-and-scaffolding/04-01-SUMMARY.md",".planning/phases/04-metadata-contract-and-scaffolding/04-02-PLAN.md",".planning/phases/04-metadata-contract-and-scaffolding/04-02-SUMMARY.md",".planning/phases/04-metadata-contract-and-scaffolding/04-03-PLAN.md",".planning/phases/04-metadata-contract-and-scaffolding/04-03-SUMMARY.md",".planning/phases/04-metadata-contract-and-scaffolding/04-04-PLAN.md",".planning/phases/04-metadata-contract-and-scaffolding/04-04-SUMMARY.md",".planning/phases/04-metadata-contract-and-scaffolding/04-05-PLAN.md",".planning/phases/04-metadata-contract-and-scaffolding/04-05-SUMMARY.md",".pre-commit-config.yaml","AGENTS.md","NOTICE","REUSE.toml","docs/decisions/0009-homework-metadata-contract.md","docs/decisions/0010-python-dependency-policy.md","docs/decisions/README.md","schema/homework.schema.json","scripts/check_metadata.py","scripts/metadata/__init__.py","scripts/metadata/allowlist.json","scripts/metadata/contract.py","scripts/new_homework","scripts/tests/fixtures/golden/homework-arduino/README.md","scripts/tests/fixtures/golden/homework-arduino/assets/.gitkeep","scripts/tests/fixtures/golden/homework-arduino/homework.yaml","scripts/tests/fixtures/golden/homework-arduino/include/.gitkeep","scripts/tests/fixtures/golden/homework-arduino/platformio.ini","scripts/tests/fixtures/golden/homework-arduino/src/main.cpp","scripts/tests/fixtures/golden/homework-arduino/task.md","scripts/tests/fixtures/golden/homework-arduino/test/test_homework/test_homework.c","scripts/tests/fixtures/golden/homework-espidf/README.md","scripts/tests/fixtures/golden/homework-espidf/assets/.gitkeep","scripts/tests/fixtures/golden/homework-espidf/homework.yaml","scripts/tests/fixtures/golden/homework-espidf/include/.gitkeep","scripts/tests/fixtures/golden/homework-espidf/platformio.ini","scripts/tests/fixtures/golden/homework-espidf/sdkconfig.defaults","scripts/tests/fixtures/golden/homework-espidf/src/main.cpp","scripts/tests/fixtures/golden/homework-espidf/task.md","scripts/tests/fixtures/golden/homework-espidf/test/test_homework/test_homework.c","scripts/tests/temp_root.py","scripts/tests/test_adrs.py","scripts/tests/test_homework_metadata.py","scripts/tests/test_metadata_deps.py","scripts/tests/test_new_homework.py","scripts/tests/test_templates.py","templates/adr/template.md","templates/board-profile/profile.yaml","templates/homework-arduino/README.md","templates/homework-arduino/assets/.gitkeep","templates/homework-arduino/homework.yaml","templates/homework-arduino/include/.gitkeep","templates/homework-arduino/platformio.ini","templates/homework-arduino/src/main.cpp","templates/homework-arduino/template.yaml","templates/homework-arduino/test/test_homework/test_homework.c","templates/homework-espidf/README.md","templates/homework-espidf/assets/.gitkeep","templates/homework-espidf/homework.yaml","templates/homework-espidf/include/.gitkeep","templates/homework-espidf/platformio.ini","templates/homework-espidf/sdkconfig.defaults","templates/homework-espidf/src/main.cpp","templates/homework-espidf/template.yaml","templates/homework-espidf/test/test_homework/test_homework.c","templates/report/report.md","templates/task/task.md"]
covered_digest: "v3:sha256:16dcfbfca0b174af462f5afe28a4e5debbc19d92bd4e495621f691c98f7c9033"
behavior_unverified: 1
overrides_applied: 0
gaps:
  - truth: "A symlink at any candidate target path is classified CONFLICT and left intact, never followed or compared through."
    status: failed
    reason: "Reproduced twice on a disposable root. (a) An intermediate directory symlink homeworks/<id>/src -> <outside> is followed: the plan says CREATE, exit is 0, and src/main.cpp (1535 bytes) is written outside homeworks/. (b) A symlink at the target directory homeworks/<id> itself -> homeworks/sub/<id> is accepted: exit 0, no CONFLICT, and all eight files land under homeworks/sub/<id>/. _contained_target() resolves the target directory and accepts any destination inside homeworks/, and _classify() checks only the final file path. The docstring's own promise ('a target that escapes homeworks/' -> exit 2) and D-20/D-24 are not met."
    artifacts:
      - path: "scripts/new_homework"
        issue: "lines 245-263 classify only the final target; lines 266-283 resolve the target directory but do not reject a symlink there or on intermediate components; lines 338-347 mkdir/mkstemp through the symlinked parent."
      - path: "scripts/tests/test_new_homework.py"
        issue: "test_symlinked_target_is_conflict_and_left_intact covers only a symlink at a file target (README.md), not the target directory or an intermediate directory."
    missing:
      - "Reject a symlink on homeworks/<id> and on every intermediate target component before classification; classify such a path CONFLICT (or exit 2) without following it."
      - "Regression tests for both reproduced variants (intermediate directory symlink and target-directory symlink)."
  - truth: "Cyrillic anywhere in task.md is an error unless the allowlist names that exact path with a non-empty reason; an unmatched allowlist entry fails the run."
    status: partial
    reason: "Reproduced: a task.md with two Cyrillic lines and one allowlist entry naming that exact path still exits 1 — only the first Cyrillic record is suppressed, the second remains ERROR. apply_allowlist() consumes one entry per record instead of exempting the path. The stale-entry half of the truth does work."
    artifacts:
      - path: "scripts/metadata/contract.py"
        issue: "apply_allowlist() lines 423-444 sets matched[index] = True on the first record for the path and leaves later records for the same path unsuppressed."
      - path: "scripts/tests/test_homework_metadata.py"
        issue: "test_allowlist_suppresses_the_exact_path uses a single Cyrillic line, so the partial suppression is not exercised."
    missing:
      - "Treat one allowlist entry as exempting every Cyrillic record for that exact path; keep a stale entry failing the run."
      - "A test with two Cyrillic lines and one entry."
  - truth: "Every content problem is reported as an ERROR record at exit 1, and --json always prints exactly one JSON array of {path,status,reason} records (derived from 04-01 Task 3 acceptance and the checker module contract)."
    status: failed
    reason: "Reproduced on a homework.yaml containing a composed YAML key (? [a, b]): the checker dies with TypeError: cannot use 'list' as a set element, prints a traceback to stderr, emits an empty stdout (no JSON array), and exits 1. Same loader code affects task.md frontmatter. No ERROR record is produced and the --json contract is broken."
    artifacts:
      - path: "scripts/metadata/contract.py"
        issue: "StrictSafeLoader.construct_mapping (lines 87-99) and StrictBaseLoader.construct_mapping (lines 115-127) put an arbitrary constructed key into a set; an unhashable list/dict key raises TypeError, which is not a yaml.YAMLError and is not caught."
      - path: "scripts/check_metadata.py"
        issue: "lines 231-241 assume records always exist; the uncaught TypeError escapes before any JSON is printed."
    missing:
      - "Handle unhashable keys without a set membership test (delegate to super(), which raises ConstructorError, a YAMLError), so the payload becomes an ERROR record at exit 1."
      - "Regression tests for ? [a, b] in homework.yaml and in task.md frontmatter, asserting one JSON array and an ERROR record."
behavior_unverified_items:
  - truth: "task.md contains an English paraphrase, the source reference, the retrieval date, and attribution, and never contains original internal material."
    test: "Scaffold a homework and inspect the rendered task.md; confirm the paraphrase is the author's own English text and that no internal course wording is reproduced."
    expected: "The four provenance fields carry real values once status leaves planned, and the body is an English paraphrase with no original internal material."
    why_human: "Paraphrase originality is a judgment call; the checker only proves machine-observable shape (URL, ISO 8601, SPDX-like, Cyrillic scan, sentinel gating). 04-01 and 04-03 prohibitions explicitly forbid presenting the checker as proof of originality. The scaffolded task.md is a TODO skeleton by design (D-30/D-39), and no real homework ships yet."
human_verification:
  - test: "Review the first real homework's task.md for paraphrase originality and absence of internal course material."
    expected: "English paraphrase in the author's words, real source_url/retrieved/attribution/license values, no original assignment text."
    why_human: "Originality cannot be machine-verified; the Cyrillic scan and shape checks are proxies only."
---

# Phase 04: Metadata Contract and Scaffolding Verification Report

**Phase Goal:** One schema-validated homework contract and a deterministic scaffold that produces a buildable homework from a template.
**Verified:** 2026-10-25T00:40:00Z
**Status:** gaps_found
**Re-verification:** No — initial verification

## Goal Achievement

The contract, templates and scaffold exist and work for the intended path: both templates scaffold into a disposable root and build (`pio run` SUCCESS for Arduino and ESP-IDF), the scaffolded Arduino native environment passes Unity, the 298-test repository suite, `pio test -d tests -e native` (73/73), `pre-commit run --all-files` and `reuse lint` are green. However, three must-have truths fail: symlink containment in the scaffold, whole-path allowlist suppression, and the checker's composed-YAML-key crash.

### Observable Truths

| # | Truth | Status | Evidence |
| --- | --- | --- | --- |
| 1 | [ROADMAP SC1] `scripts/new_homework` scaffolds from either template, is idempotent, supports `--dry-run`, and refuses to overwrite | ✓ VERIFIED | Manual second run: all 8 records `UNCHANGED`, exit 0; `test_conflict_and_deletion_write_nothing` and `test_dry_run_matches_the_real_run` pass |
| 2 | [ROADMAP SC2] Scaffolded project has `platformio.ini`, `src/`, `include/`, `test/`, `assets/`, `README.md`, `task.md`, `homework.yaml`, and builds immediately | ✓ VERIFIED | Manual scaffold produced all 8 paths; `pio run` SUCCESS for Arduino (5.86 s) and ESP-IDF (25.39 s) |
| 3 | [ROADMAP SC3] `homework.yaml` validated by a JSON Schema with `additionalProperties: false`; unknown key rejected; every required field recorded | ✓ VERIFIED | `schema/homework.schema.json` has `additionalProperties: false` at root and in all five `$defs`; unknown top-level `bogus` key → exit 1 naming `'bogus'` |
| 4 | [ROADMAP SC4] `task.md` contains an English paraphrase, source reference, retrieval date, attribution, and no original internal material | ⚠️ PRESENT_BEHAVIOR_UNVERIFIED | Shape rules enforced (`URL_PATTERN`, `valid_iso8601`, `SPDX_LIKE`, sentinel gating, Cyrillic gate); originality is not machine-verifiable — see Human Verification |
| 5 | [ROADMAP SC5] `templates/` provides Arduino, ESP-IDF, report, task, ADR and board-profile templates | ✓ VERIFIED | All six directories exist; `test_every_template_directory_exists` passes |
| 6 | [04-01] Checker exits 0 on a schema-valid `homework.yaml` and prints `PATH: OK — reason` | ✓ VERIFIED | Manual run on scaffolded tree printed `homeworks/1_3-gate-arduino/homework.yaml: OK — metadata contract satisfied`, exit 0 |
| 7 | [04-01] Unknown key inside each nested block (source, toolchain, simulation, tests, report) rejected independently | ✓ VERIFIED | `additionalProperties: false` in every `$def`; `test_unknown_nested_key_is_error` passes with subTests |
| 8 | [04-01] Every invalid research probe rejected (id, status, framework, platformio, duplicate/absolute/dot-dot/backslash/trailing-slash assets) | ✓ VERIFIED | `test_research_probes_are_rejected` covers all nine cases; schema patterns reject each |
| 9 | [04-01] Every required root key and every required `$def` member proven separately | ✓ VERIFIED | `test_every_required_root_key_is_required` / `test_every_required_defs_member_is_required` pass |
| 10 | [04-01] `homework.yaml` whose `id` differs from its containing `homeworks/<dir>/` is rejected | ✓ VERIFIED | `test_id_must_match_containing_directory` passes; `_homework_directory()` implements it |
| 11 | [04-01] YAML syntax errors, non-mapping payloads and duplicate mapping keys produce ERROR records and exit 1, never 2 | ✓ VERIFIED | `test_malformed_yaml_is_error`, `test_non_mapping_payload_is_error`, `test_duplicate_mapping_key_is_error` pass (exit 1 + `: ERROR — `) |
| 12 | [04-01] A `homework.yaml` over 64 KiB produces an ERROR record and exit 1 | ✓ VERIFIED | `test_oversized_document_is_error` passes (`larger than 65536 bytes`) |
| 13 | [04-01] Schema uses patterns, never the `format` keyword | ✓ VERIFIED | No `format` key in `schema/homework.schema.json`; `test_schema_contains_no_format_keyword` passes |
| 14 | [04-01] A second identical run is byte-identical and leaves the tree unchanged | ✓ VERIFIED | `test_second_run_is_identical_and_read_only` passes; checker is read-only by construction |
| 15 | [04-01] Canonical ID pattern literal identical in schema `id.pattern`, `contract.py`, `AGENTS.md` and `EXPECTED_PATTERN` | ✓ VERIFIED | `^[0-9]+_[0-9]+-[a-z0-9-]+$` in all four; `test_canonical_id_literal_is_identical_in_four_places` passes |
| 16 | [derived, 04-01 Task 3] Every content problem is an ERROR record at exit 1 and `--json` always prints one JSON array | ✗ FAILED | Composed YAML key `? [a, b]` → `TypeError` traceback, empty stdout, no array (gap 3) |
| 17 | [04-02] Arduino template has `template.yaml` plus the seven non-task FOUND-01 paths | ✓ VERIFIED | Directory listing matches exactly |
| 18 | [04-02] ESP-IDF template has the same set plus `sdkconfig.defaults`, no `CMakeLists.txt`, no `src/CMakeLists.txt`, no `sdkconfig.<env>` | ✓ VERIFIED | `find` shows no generated input; `test_espidf_ships_no_generated_build_input` passes |
| 19 | [04-02] Neither homework template contains `task.md` | ✓ VERIFIED | `find` shows no `task.md` under `templates/homework-*`; `test_no_homework_template_owns_task_md` passes |
| 20 | [04-02] A copy rendered at `homeworks/<id>` depth builds with `pio run`, and its native environment passes `pio test -e native` | ✓ VERIFIED | Scaffolded output built: Arduino SUCCESS, ESP-IDF SUCCESS; Arduino native 2/2 tests passed |
| 21 | [04-02] Both starter files call `lib/port` through the matching adapter | ✓ VERIFIED | `arduino_gpio_port`/`arduino_log_port` and `espidf_gpio_port`/`espidf_log_port` are called; target builds compile the adapters |
| 22 | [04-02] Arduino entry defines `setup`/`loop`; ESP-IDF defines `app_main` with C linkage | ✓ VERIFIED | `void setup(void)`/`void loop(void)`; `extern "C" void app_main(void)` |
| 23 | [04-02] Target env declares only `extends` and `lib_deps`; `lib/host` and Unity appear only in `[env:native]` | ✓ VERIFIED | Both `platformio.ini` files match; `test_target_section_declares_only_extends_and_lib_deps` passes |
| 24 | [04-02] `default_envs` names the target only; no dollar-brace interpolation anywhere | ✓ VERIFIED | `default_envs = esp32s3_arduino` / `esp32s3_espidf`; `test_no_dollar_brace_interpolation` passes |
| 25 | [04-03] `task.md` frontmatter parsed as text with the base loader, so an unquoted ISO timestamp stays a string | ✓ VERIFIED | `StrictBaseLoader`; `test_unquoted_iso_timestamp_stays_a_string` passes |
| 26 | [04-03] The four TODO provenance fields pass only while `status: planned` | ✓ VERIFIED | `test_planned_task_sentinels_are_accepted` / `test_sentinel_is_rejected_once_status_leaves_planned` pass |
| 27 | [04-03] Non-URL `source_url`, date without timezone, non-SPDX license rejected | ✓ VERIFIED | `URL_PATTERN`, `valid_iso8601`, `SPDX_LIKE`; `test_invalid_shapes_are_rejected` passes |
| 28 | [04-03] Cyrillic anywhere is an error unless the allowlist names that exact path with a non-empty reason; unmatched entry fails | ✗ FAILED | Reproduced: two Cyrillic lines + one entry for the path → second line still ERROR (gap 2); stale entries do fail |
| 29 | [04-03] `source.reference` and `source_url` must agree when both are URLs | ✓ VERIFIED | `test_mismatched_reference_and_source_url_is_error` passes (exit 1, not a warning) |
| 30 | [04-03] Malformed frontmatter, duplicate frontmatter key and task.md over 64 KiB → ERROR record, exit 1 | ✓ VERIFIED | Three tests pass with exit 1 and `: ERROR — ` (composed-key payload covered by truth 16) |
| 31 | [04-03] A directory with neither `homework.yaml` nor `task.md` produces a deterministic ERROR | ✓ VERIFIED | `_validate_directory` lines 95-103; `test_orphan_directory_is_error` passes |
| 32 | [04-03] Cyrillic detection covers assigned characters in every Cyrillic block, incl. Extended-A/B | ✓ VERIFIED | `is_cyrillic_char` uses the Unicode name; `test_extended_b_character_is_rejected` passes |
| 33 | [04-03] Body TODOs documented as manual-review signals; only the five provenance fields are status-gated | ✓ VERIFIED | ADR-0009 "The sentinel rule" states both |
| 34 | [04-03] `templates/task`, `report`, `board-profile`, `adr` exist; ADR template moved byte-identically with no copy left | ✓ VERIFIED | Old path absent at HEAD; last committed old blob `2e24d924…` equals `git hash-object templates/adr/template.md` |
| 35 | [04-03] `NOTICE` names `templates/adr/template.md` and no longer `docs/decisions/template.md` | ✓ VERIFIED | NOTICE lines 19-25 reference only the new path |
| 36 | [04-04] Malformed id, unknown template, missing manifest, unknown placeholder and dollar-brace each exit 2 before any plan output | ✓ VERIFIED | Six `ErrorTests` pass, asserting exit 2, empty stdout and `ERROR:` |
| 37 | [04-04] Template selection is dynamic (`templates/homework-<name>/template.yaml`), no argparse `choices` registry | ✓ VERIFIED | `_template_directory` resolves by path; `test_new_template_directory_is_accepted_without_a_cli_change` passes |
| 38 | [04-04] A rendered `homework.yaml` whose `id` differs from the target directory is rejected as ERROR | ✓ VERIFIED | `test_mismatched_rendered_id_is_error` passes |
| 39 | [04-04] A symlink at any candidate target path is CONFLICT and left intact, never followed | ✗ FAILED | Two reproductions: intermediate symlink writes outside with exit 0; target-directory symlink accepted (gap 1) |
| 40 | [04-04] Write phase creates each parent before `mkstemp`; a conflict or `--dry-run` creates no `homeworks/` or `homeworks/<id>/` directory | ✓ VERIFIED | Code order confirmed; `test_dry_run_creates_no_directories` and `test_repository_homeworks_directory_is_never_created` pass |
| 41 | [04-04] Scaffolded Arduino and ESP-IDF trees match their golden trees byte-for-byte | ✓ VERIFIED | Independent byte comparison of freshly scaffolded `1_3-fixture` trees: 8 and 9 files, zero byte mismatches |
| 42 | [04-04] PEP 723 pins equal the pre-commit hook dependencies, and the suite actually invokes the hook | ✓ VERIFIED | `test_both_entry_scripts_declare_the_same_pins`, `test_hook_pins_match_the_entry_scripts`, `test_hook_invocation` pass |
| 43 | [04-04] Validation and conflict failures leave the tree untouched; an OS write failure may leave a partial project | ✓ VERIFIED | Plan-then-write order; `test_conflict_and_deletion_write_nothing` passes (WR-02 notes a write-time failure case) |
| 44 | [04-05] ADR-0009/0010 have the five MADR frontmatter keys, eight sections in order, chosen-option sentence, ≥2 options with pros/cons, agreeing index rows | ✓ VERIFIED | Both records inspected; `test_adrs.py` (eight `MADR_SECTIONS` in order) passes |
| 45 | [04-05] `docs/decisions/README.md` states `Next number: 0011` | ✓ VERIFIED | Read in the file |
| 46 | [04-05] `AGENTS.md` lists `schema/`, `templates/`, `lib/`, `homeworks/<id>/` as present; adds the checker to quick-start; adds both routing rows; ≤300 lines | ✓ VERIFIED | Lines 26, 46-53, 215-216; 227 lines |
| 47 | [04-05] `AGENTS.md` contains exactly one backticked anchored regex and no new `^...$` backticked span | ✓ VERIFIED | `grep -E '`\^[^`]*\$`'` returns exactly line 107 |
| 48 | [04-05] `test_agents_md` and `test_homework_id` pass after the edit without changing either test | ✓ VERIFIED | 18 tests OK; both files last changed in Phase 1 commit `e2dd499` |
| 49 | [04-05] ADR-0009 lists all five sentinel-bearing fields normatively and records body TODOs as manual-review | ✓ VERIFIED | Numbered list 1-5 plus the manual-review paragraph |
| 50 | [04-05] `REUSE.toml` declares `templates/**/*.md` as CC-BY-4.0 after the MIT catch-all, and `reuse lint` passes | ✓ VERIFIED | MIT `path = "**"` precedes the CC-BY annotation; `reuse lint` compliant (246/246 files) |
| 51 | [04-05] `scripts/new_homework` scaffolds both templates into a temp root and each builds with `pio run` | ✓ VERIFIED | Arduino SUCCESS 5.86 s; ESP-IDF SUCCESS 25.39 s from scaffolded output |
| 52 | [04-05] Scaffolded Arduino native environment passes `pio test -e native` | ✓ VERIFIED | 2/2 tests passed |
| 53 | [04-05] Scaffolded ESP-IDF reports 16 MB flash and octal PSRAM from generated `sdkconfig.json` | ✓ VERIFIED | `.pio/build/esp32s3_espidf/config/sdkconfig.json`: `ESPTOOLPY_FLASHSIZE = "16MB"`, `SPIRAM_MODE_OCT = true` |
| 54 | [04-05] Full repository suite and `pre-commit run --all-files` are green | ✓ VERIFIED | 298 tests OK; `pio test` 73/73; all pre-commit hooks passed |

**Score:** 50/54 truths verified (1 present, behavior-unverified)

### Prohibitions

All ten plan prohibitions were checked and pass:

- No `format` keyword in the schema; URL and ISO 8601 use patterns plus stdlib code.
- No document claims that the checker proves paraphrase originality.
- Homework templates ship no generated build input (`CMakeLists.txt`, `src/CMakeLists.txt`, `sdkconfig.<env>`).
- The report template stays a bare skeleton.
- The allowlist rejects an empty reason (exit 2) and a stale entry fails the run.
- The scaffold never normalizes content to manufacture `UNCHANGED`; only byte equality counts.
- Unknown placeholders, symlinked template entries and unreadable template entries all stop the run.
- ADR-0009/0010 name Phase 8 as the CI owner and do not claim CI enforcement today.
- The `REUSE.toml` MIT catch-all stays first.

### Required Artifacts

| Artifact | Expected | Status | Details |
| --- | --- | --- | --- |
| `schema/homework.schema.json` | JSON Schema 2020-12 contract | ✓ VERIFIED | 93 lines, strict at all depths, patterns only |
| `scripts/metadata/__init__.py` | Package marker | ✓ VERIFIED | Docstring-only package init |
| `scripts/metadata/contract.py` | Single validation implementation | ✓ VERIFIED | 634 lines; defect CR-02 (gap 3) and WR-01 (gap 2) |
| `scripts/check_metadata.py` | Thin 0/1/2 entry point | ✓ VERIFIED | 255 lines; imports contract, no rules re-implemented |
| `scripts/new_homework` | Plan-then-write scaffold | ✓ VERIFIED | 440 lines; defect CR-01 (gap 1) |
| `scripts/tests/test_homework_metadata.py` | META-01/02 matrix | ✓ VERIFIED | 803 lines |
| `scripts/tests/test_new_homework.py` | META-04/FOUND-01 matrix | ✓ VERIFIED | 422 lines; symlink coverage incomplete (gap 1) |
| `scripts/tests/test_templates.py` | META-03 inventory | ✓ VERIFIED | 373 lines |
| `scripts/tests/test_metadata_deps.py` | D-13 drift + hook invocation | ✓ VERIFIED | 235 lines |
| `scripts/tests/temp_root.py` | Disposable root harness | ✓ VERIFIED | `render_tree` unused (IN-06) |
| `scripts/tests/fixtures/golden/homework-arduino/` | Committed golden tree | ✓ VERIFIED | 8 files, byte-identical to fresh scaffold |
| `scripts/tests/fixtures/golden/homework-espidf/` | Committed golden tree | ✓ VERIFIED | 9 files, byte-identical to fresh scaffold |
| `templates/homework-arduino/` | Arduino template | ✓ VERIFIED | 8 authored files including `template.yaml` |
| `templates/homework-espidf/` | ESP-IDF template | ✓ VERIFIED | 9 authored files including `sdkconfig.defaults` |
| `templates/task/task.md` | Task skeleton | ✓ VERIFIED | Sentinel frontmatter + body TODO |
| `templates/report/report.md` | Report skeleton | ✓ VERIFIED | Bare skeleton, no report contract |
| `templates/board-profile/profile.yaml` | Board profile | ✓ VERIFIED | Not consumed by any executable (WR-03) |
| `templates/adr/template.md` | MADR template | ✓ VERIFIED | Byte-identical move |
| `scripts/metadata/allowlist.json` | Empty allowlist | ✓ VERIFIED | Version 1, empty entries |

### Key Link Verification

| From | To | Via | Status | Details |
| --- | --- | --- | --- | --- |
| `check_metadata.py` | `scripts/metadata/contract.py` | `sys.path.insert` + imports | WIRED | No validation rule re-implemented in the entry script |
| `contract.py` | `schema/homework.schema.json` | `SCHEMA_PATH` against `--dir` root | WIRED | One literal, no duplicate path |
| schema `id.pattern` | `contract.py` / `AGENTS.md` / `test_homework_id.py` | shared canonical literal | WIRED | Byte-identical in all four |
| `validate_homework_text` | containing `homeworks/<dir>/` | `_homework_directory()` | WIRED | Works for normal paths; returns `None` through a symlinked target (gap 1) |
| template `platformio.ini` | `../../platformio.shared.ini` | `extra_configs` | WIRED | Both builds resolved it |
| `src/main.cpp` | `port/` + adapter headers | factory calls | WIRED | Adapters compiled into both builds |
| template native test | `lib/host` + Unity | `pio test -e native` | WIRED | 2/2 passed |
| `new_homework` | `validate_candidate` | import + call before first `mkdir` | WIRED | No validation rule in the scaffold |
| checker | `homework.yaml` before `task.md` | `_validate_directory` order | WIRED | Status gates the sentinel |
| `test_adrs.py` | moved ADR template + README | `TEMPLATE_FILE` + relative link | WIRED | ADR tests pass |
| scaffold writes | target directory + `os.replace` | containment check (D-24) | ⚠️ PARTIAL | Temp-file + replace works; containment check bypassed by intermediate/target-dir symlinks (gap 1) |
| ADR-0009 | checker behaviour | written authority | WIRED | Schema path and sentinel rule documented |
| `AGENTS.md` | schema path | repository contract | WIRED | Names `schema/homework.schema.json` |
| phase gate | scaffolded output | temp-root build | WIRED | Built from scaffolded trees, not hand-rendered copies |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
| --- | --- | --- | --- | --- |
| `check_metadata.py` | `records` | `contract.validate_*` over real files | Yes — manual valid/unknown-key runs | ✓ FLOWING |
| `new_homework` | `payloads` / `records` | templates → `_render` → `validate_candidate` → write | Yes — 8/9 files written and byte-compared | ✓ FLOWING |
| ESP-IDF build | `sdkconfig.json` | ESP-IDF build system | Yes — `16MB`, `SPIRAM_MODE_OCT: true` | ✓ FLOWING |
| `templates/board-profile/profile.yaml` | board id | not read by any executable | No consumer | ✗ DISCONNECTED (WR-03, warning) |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| --- | --- | --- | --- |
| Checker accepts valid metadata | `uv run scripts/check_metadata.py --dir <scaffolded root>` | `…homework.yaml: OK — metadata contract satisfied`, exit 0 | ✓ PASS |
| Checker rejects unknown top-level key | same with `bogus: 1` | `ERROR — Additional properties are not allowed ('bogus' …)`, exit 1 | ✓ PASS |
| Scaffold creates eight paths | `uv run scripts/new_homework 1_3-x --template arduino --dir <tmp>` | 8 CREATE records, exit 0 | ✓ PASS |
| Second run is idempotent | same command again | 8 `UNCHANGED`, exit 0 | ✓ PASS |
| Intermediate symlink containment | symlink `homeworks/1_3-x/src → outside`, then scaffold | exit 0, `outside/main.cpp` written (1535 B) | ✗ FAIL |
| Target-directory symlink containment | `homeworks/1_3-x → homeworks/sub/1_3-x`, then scaffold | exit 0, all files under `homeworks/sub/1_3-x` | ✗ FAIL |
| Composed YAML key handling | `? [a, b]` in `homework.yaml`, `--json` | `TypeError` traceback, empty stdout, exit 1 | ✗ FAIL |
| Allowlist exempts path | two Cyrillic lines + one entry for the path | second line remains `ERROR`, exit 1 | ✗ FAIL |
| Arduino target build | `pio run -d …/1_3-gate-arduino` | SUCCESS, 5.86 s | ✓ PASS |
| ESP-IDF target build | `pio run -d …/1_3-gate-espidf` | SUCCESS, 25.39 s | ✓ PASS |
| Scaffolded native test | `pio test -d …/1_3-gate-arduino -e native` | 2/2 succeeded | ✓ PASS |
| Golden byte equality | fresh scaffold vs committed golden | 8 and 9 files, zero byte mismatches | ✓ PASS |
| Repository suite | `python3 -m unittest discover -s scripts/tests` | 298 tests OK | ✓ PASS |
| Native Unity suite | `pio test -d tests -e native` | 73/73 succeeded | ✓ PASS |
| Pre-commit gate | `pre-commit run --all-files` | every hook Passed | ✓ PASS |
| REUSE compliance | `reuse --no-multiprocessing lint` | compliant, 246/246 | ✓ PASS |
| Named AGENTS/hash tests | `python3 -m unittest scripts.tests.test_agents_md scripts.tests.test_homework_id` | 18 tests OK | ✓ PASS |

### Probe Execution

Not applicable: the phase declares no `probe-*.sh` scripts and its validation strategy names no probe harness. The phase gate is the build + suite matrix recorded above.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| --- | --- | --- | --- | --- |
| FOUND-01 | 04-02, 04-04, 04-05 | One independent PlatformIO project per homework with the eight paths | ✓ SATISFIED | Scaffold produces all eight paths and both templates build; caveat: symlink containment (gap 1) and no live homework yet |
| META-01 | 04-01 | `homework.yaml` validated by a JSON Schema with `additionalProperties: false`, recording the full field set | ✓ SATISFIED | Schema + checker verified; caveat: composed-key crash (gap 3) |
| META-02 | 04-03 | `task.md` carries paraphrase, source reference, retrieval date, attribution; never original internal material | ? NEEDS HUMAN | Shape, sentinel and Cyrillic rules verified; paraphrase originality is a human review item |
| META-03 | 04-02, 04-03 | Six templates exist | ✓ SATISFIED | All six directories and their declared files exist |
| META-04 | 04-04 | Scaffold, idempotent, `--dry-run`, refuses overwrite | ✓ SATISFIED | Verified by manual runs and integration tests; caveat: symlink containment (gap 1) |

No orphaned requirements: every Phase 4 requirement in `REQUIREMENTS.md` (FOUND-01, META-01–META-04) is claimed by at least one plan.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| --- | --- | --- | --- | --- |
| `scripts/new_homework` | 245-263, 266-283, 338-347 | Symlink not checked on target directory or intermediate components | 🛑 Blocker | Writes outside `homeworks/` with exit 0 (CR-01, gap 1) |
| `scripts/metadata/contract.py` | 87-99, 115-127 | `key in set` on an arbitrary constructed YAML key | 🛑 Blocker | `TypeError` traceback, empty `--json` output (CR-02, gap 3) |
| `scripts/metadata/contract.py` | 423-444 | One allowlist entry consumed per record | 🛑 Blocker | A multi-line Cyrillic file stays failing despite an entry (WR-01, gap 2) |
| `scripts/new_homework` | 245-263 | A regular file at an intermediate path is classified CREATE | ⚠️ Warning | Partial project written, then exit 2 (WR-02) |
| `scripts/new_homework` / `AGENTS.md` | 88, 136-142, 204-214 / 48-49 | `board`/`framework` mapping entries are unused; `board-profile` is not rendered | ⚠️ Warning | Manifest framework can disagree with rendered metadata; rulebook overclaims (WR-03) |
| `scripts/tests/test_templates.py` | 87 | Placeholder lint regex differs from the renderer's | ⚠️ Warning | Some invalid tokens pass lint but fail the scaffold (WR-04) |
| `scripts/tests/test_new_homework.py` | 105-129 | Golden diff compares splitlines, not bytes | ⚠️ Warning | EOL/final-newline regressions invisible to the test (WR-05); actual trees match today |
| `scripts/metadata/contract.py` | 480-499 | Degenerate id yields an empty display title | ℹ️ Info | `1_3--` scaffolds a homework with a blank title (IN-01) |
| `scripts/metadata/contract.py` | 613-621 | `toolchain.platformio` not cross-checked against `PLATFORMIO_CORE` | ℹ️ Info | A drifted Core pin passes (IN-02) |
| `scripts/metadata/contract.py` | 87-127 | YAML merge keys rejected as "invalid YAML" | ℹ️ Info | Misleading message (IN-03) |
| `scripts/metadata/contract.py` | 227-233 | Non-string provenance reported as "value is empty" | ℹ️ Info | Misleading message (IN-04) |
| `scripts/new_homework` | 324-336 | `mkstemp` leaves mode 0600; SIGKILL leaves temp files | ℹ️ Info | File modes differ from 0644 (IN-05) |
| `scripts/tests/temp_root.py` | 61-121 | `render_tree` unused | ℹ️ Info | Dead fixture generator (IN-06) |
| `scripts/new_homework` | 428-435 | Unreachable `except CheckError` in the write phase | ℹ️ Info | Dead branch (IN-07) |
| `scripts/metadata/contract.py` | 332-370 | Cascading task error when `homework.yaml` is invalid | ℹ️ Info | Misleading diagnostics (IN-08) |

Debt-marker gate: no `TBD`, `FIXME` or `XXX` marker exists in any file this phase modified.

### Human Verification Required

1. **Paraphrase originality of the first real `task.md`**

   **Test:** Scaffold a homework, fill the four provenance fields and the body, then review the text.
   **Expected:** The body is an English paraphrase in the author's own words, with real `source_url`, `retrieved`, `attribution` and `license` values, and no original internal course material.
   **Why human:** The checker proves machine-observable shape only; the phase's own prohibitions forbid presenting it as proof of originality, and no real homework ships yet.

### Gaps Summary

The phase delivers the intended happy path end-to-end: a strict schema, one shared validator, two buildable templates, a deterministic idempotent scaffold, six template kinds, ADRs, rulebook and license updates, with every repository gate green. Three must-have truths fail:

1. **Symlink containment (CR-01, blocker).** `_contained_target()` resolves `homeworks/<id>` but accepts a destination still inside `homeworks/`, and `_classify()` checks only the final file path. An intermediate directory symlink lets the scaffold write outside `homeworks/` with exit 0, and a symlink at `homeworks/<id>` itself is followed silently. Both variants were reproduced on disposable roots.
2. **Whole-path allowlist suppression (WR-01, blocker for the truth).** One allowlist entry suppresses only the first Cyrillic record for a path, so a file with two offending lines still fails. Reproduced.
3. **Composed YAML key crash (CR-02, blocker for the derived `--json`/ERROR-record truth).** An unhashable YAML key raises `TypeError`, producing a traceback and empty stdout instead of an ERROR record. Reproduced for `homework.yaml`; the same loader governs `task.md` frontmatter.

The remaining review warnings (WR-02–WR-05, IN-01–IN-08) are real but do not violate a plan must-have; they are recorded above for the gap-closure plan to consider.

---

_Verified: 2026-10-25T00:40:00Z_
_Verifier: Claude (gsd-verifier)_

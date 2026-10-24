---
phase: "4"
slug: "metadata-contract-and-scaffolding"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: validated
nyquist_compliant: true
wave_0_complete: true
created: "2026-10-24"
validated: "2026-10-25"
---

# Phase 4 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | stdlib `unittest` (no pytest, no third-party import in tests — D-14) |
| **Config file** | none — discovery via `scripts/tests/__init__.py` |
| **Quick run command** | `python3 -m unittest discover -s scripts/tests -v` |
| **Full suite command** | `python3 -m unittest discover -s scripts/tests -v` plus `pio test -d tests -e native` and one `pio run` per scaffolded template |
| **Estimated runtime** | ~77 s baseline (310 tests) + ~31 s for the two target builds |

---

## Sampling Rate

- **After every task commit:** Run `python3 -m unittest discover -s scripts/tests -v`
- **After every plan wave:** Run the quick suite, plus `pio test -d tests -e native` if a shared library changed
- **Before `/gsd-verify-work`:** Full suite must be green, `pre-commit run --all-files` green, and one target build per template from the temp-root fixture
- **Max feedback latency:** ~90 seconds
- **Do not add `pio run -d tests -e native`:** it fails on `unity_config.h` (Pitfall P3); native is a test-only environment.

---

## Per-Task Verification Map

Task IDs are assigned by the planner. This map fixes the requirement → test binding the plans must honor.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 04-04-T2, 04-06-T2, 04-08-T1 | 04-04 | 3 | FOUND-01 | T-04-03 | Scaffold never writes outside the target root | integration | `python3 -m unittest scripts.tests.test_new_homework.ConflictTests -v` (symlinked target, intermediate directory, target directory, `homeworks` base) + `RepositoryStateTests.test_repository_homeworks_directory_is_never_created` | ✅ | ✅ green |
| 04-05-T3 | 04-05 | 4 | FOUND-01 | — | Target env builds from the scaffolded tree | build (phase gate) | `pio run -d <tmp>/homeworks/1_3-gate-arduino` and `...-espidf` — both `SUCCESS`, Flash max 6,553,600, recorded in `04-05-SUMMARY.md` | ✅ | ✅ green |
| 04-01-T3 | 04-01 | 1 | META-01 | T-04-01 | Unknown top-level key is rejected | unit | `python3 -m unittest scripts.tests.test_homework_metadata.UnknownKeyTests.test_unknown_top_level_key_is_error -v` | ✅ | ✅ green |
| 04-01-T3 | 04-01 | 1 | META-01 | T-04-01 | Unknown key inside every nested block is rejected | unit | `...UnknownKeyTests.test_unknown_nested_key_is_error` (subTest per `$defs`) | ✅ | ✅ green |
| 04-01-T2, 04-01-T3 | 04-01 | 1 | META-01 | T-04-04 | Required fields, enums, patterns, `uniqueItems` behave | unit | `...RequiredKeyTests.test_every_required_root_key_is_required`, `...test_every_required_defs_member_is_required`, `...SchemaShapeTest.test_schema_declares_additional_properties_everywhere` | ✅ | ✅ green |
| 04-03-T1 | 04-03 | 2 | META-02 | — | Frontmatter has exactly four non-empty fields | unit | `...TaskProvenanceTests.test_extra_task_frontmatter_key_is_error`, `...test_missing_task_md_is_error`, `...test_malformed_frontmatter_is_error` | ✅ | ✅ green |
| 04-03-T1 | 04-03 | 2 | META-02 | — | URL, ISO 8601, SPDX-like shape are enforced via `pattern` + `datetime` (not `format`) | unit | `...ProvenanceShapeTests.test_valid_url_timestamp_and_license_are_accepted`, `...test_invalid_shapes_are_rejected`, `...SchemaShapeTest.test_schema_contains_no_format_keyword` | ✅ | ✅ green |
| 04-03-T2, 04-07-T2, 04-09-T2 | 04-03 | 2 | META-02 | T-04-05 | Cyrillic is rejected; allowlist entry suppresses; stale entry fails | unit | `...CyrillicGateTests -v` (8 tests, incl. `test_allowlist_suppresses_every_record_for_the_path` and `test_allowlisted_path_still_rejects_a_shape_violation`) | ✅ | ✅ green |
| 04-03-T2 | 04-03 | 2 | META-02 | — | `source.reference` / `source_url` disagreement is an error | unit | `...CrossValidationTests.test_mismatched_reference_and_source_url_is_error` | ✅ | ✅ green |
| 04-03-T3 | 04-03 | 2 | META-03 | T-04-06 | All six template directories exist with the required files | unit | `scripts.tests.test_templates.TemplateInventoryTests.test_every_template_directory_exists`, `...test_inventory_matches_exactly` | ✅ | ✅ green |
| 04-02-T3 | 04-02 | 1 | META-03 | T-04-06 | No `${...}`; every `{{...}}` is in the known set | unit | `...TemplateTextTests.test_placeholders_are_the_closed_vocabulary`, `...test_placeholder_lint_rejects_an_unknown_token`, `...test_no_dollar_brace_interpolation` | ✅ | ✅ green |
| 04-03-T3 | 04-03 | 2 | META-03 | — | The ADR template moved and the old path is gone | unit | `...TemplateInventoryTests.test_adr_template_moved_out_of_the_decisions_directory` + updated `scripts.tests.test_adrs` | ✅ | ✅ green |
| 04-04-T2 | 04-04 | 3 | META-04 | T-04-02 | Second run reports `UNCHANGED` and exit 0 | integration | `scripts.tests.test_new_homework.IdempotencyTests.test_second_run_is_all_unchanged`, `...test_two_real_runs_are_byte_identical` | ✅ | ✅ green |
| 04-04-T2 | 04-04 | 3 | META-04 | T-04-02 | Modified target reports `CONFLICT`, exit 1, and writes nothing | integration | `...ConflictTests.test_conflict_and_deletion_write_nothing` | ✅ | ✅ green |
| 04-04-T2 | 04-04 | 3 | META-04 | — | `--dry-run` prints the same records and creates nothing | integration | `...DryRunTests.test_dry_run_matches_the_real_run`, `...test_dry_run_creates_no_directories` | ✅ | ✅ green |
| 04-04-T2 | 04-04 | 3 | META-04 | — | Golden trees match for both templates | integration | `...GoldenTreeTests.test_arduino_tree_matches_its_golden`, `...test_espidf_tree_matches_its_golden` (unified diff on failure) | ✅ | ✅ green |
| 04-04-T3 | 04-04 | 3 | D-13 | — | PEP 723 and pre-commit declarations agree | unit | `scripts.tests.test_metadata_deps.MetadataDependencyTests.test_both_entry_scripts_declare_the_same_pins`, `...test_hook_pins_match_the_entry_scripts` | ✅ | ✅ green |
| 04-04-T3 | 04-04 | 3 | D-37 | — | The pre-commit hook's config shape is correct | unit | `...MetadataDependencyTests.test_hook_declares_an_isolated_python_environment`, `...test_hook_files_pattern_includes_homeworks_schema_and_scaffold`, `...test_hook_invocation` | ✅ | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

### Gap-closure coverage

The four gap-closure plans add regressions on top of the rows above; each is bound to the
requirement it repairs and runs green in the 310-test suite.

| Plan | Requirement | Regression |
|------|-------------|-----------|
| 04-06 | FOUND-01 | `ConflictTests.test_symlinked_target_is_conflict_and_left_intact`, `...test_intermediate_directory_symlink_is_conflict_and_writes_nothing`, `...test_target_directory_symlink_exits_2` |
| 04-07 | META-02 | `CyrillicGateTests.test_allowlist_suppresses_every_record_for_the_path`, `...test_allowlisted_path_still_rejects_a_shape_violation`; `PayloadTests.test_composed_mapping_key_is_error`, `...test_composed_key_in_task_frontmatter_is_error` |
| 04-08 | FOUND-01, META-01 | `ConflictTests.test_homeworks_base_symlink_exits_2`, `IdentityTests.test_id_mismatch_survives_a_symlinked_homeworks_base` |
| 04-09 | FOUND-01, META-01, META-04 | `IdentityTests.test_id_mismatch_holds_when_the_root_is_spelled_differently`, `...test_matching_id_is_accepted_when_the_root_is_spelled_differently`, `...test_id_mismatch_survives_a_symlinked_base_under_a_differently_spelled_root` |

---

## Wave 0 Requirements

- [x] `scripts/tests/test_homework_metadata.py` — covers META-01, META-02, the allowlist, exit codes and `--json` (60 tests)
- [x] `scripts/tests/test_new_homework.py` — covers META-04, FOUND-01's path set, idempotency, dry-run, conflict, and the golden trees (27 tests)
- [x] `scripts/tests/test_templates.py` — covers META-03 and the `platformio.ini` shape (22 tests)
- [x] `scripts/tests/test_metadata_deps.py` — covers D-13's drift rule (9 tests)
- [x] `scripts/tests/fixtures/golden/homework-{arduino, espidf}/` — the committed expected trees
- [x] A shared temp-root helper (copytree + symlink `lib/`) used by the scaffold tests
- [x] Update `scripts/tests/test_adrs.py`'s `TEMPLATE_FILE` (Pitfall P12)
- [x] No framework install is needed; the suite is stdlib-only

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| — | — | None — every phase behavior has automated verification | — |

*All other phase behaviors have automated verification.*

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 90s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** validated 2026-10-25 — 18/18 map rows green, 0 gaps, 0 escalated

## Validation Audit 2026-10-24

| Metric | Count |
|---|---|
| Gaps found | 0 |
| Resolved | 0 |
| Escalated | 0 |

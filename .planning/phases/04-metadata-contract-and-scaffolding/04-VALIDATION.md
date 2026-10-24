---
phase: "4"
slug: "metadata-contract-and-scaffolding"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-10-24"
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
| **Estimated runtime** | ~62 s baseline (190 tests) + ~31 s for the two target builds |

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
| TBD | TBD | TBD | FOUND-01 | T-04-03 | Scaffold never writes outside the target root | integration | `uv run scripts/new_homework 1_3-fixture --template arduino --dir <tmp>` then walk the tree | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | FOUND-01 | — | Target env builds from the scaffolded tree | build | `pio run -d <tmp>/homeworks/1_3-fixture` (Arduino and ESP-IDF) | ❌ W0 (phase verification step) | ⬜ pending |
| TBD | TBD | TBD | META-01 | T-04-01 | Unknown top-level key is rejected | unit | `test_homework_metadata.py::test_unknown_top_level_key_is_error` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | META-01 | T-04-01 | Unknown key inside every nested block is rejected | unit | `...::test_unknown_nested_key_is_error` (subTest per `$defs`) | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | META-01 | T-04-04 | Required fields, enums, patterns, `uniqueItems` behave | unit | `...::test_schema_accepts_valid_and_rejects_invalid_fixtures` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | META-02 | — | Frontmatter has exactly four non-empty fields | unit | `...::test_task_frontmatter_shape` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | META-02 | — | URL, ISO 8601, SPDX-like shape are enforced via `pattern` + `datetime` (not `format`) | unit | `...::test_provenance_shapes` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | META-02 | T-04-05 | Cyrillic is rejected; allowlist entry suppresses; stale entry fails | unit | `...::test_cyrillic_gate_and_allowlist` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | META-02 | — | `source.reference` / `source_url` disagreement is an error | unit | `...::test_cross_validation` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | META-03 | T-04-06 | All six template directories exist with the required files | unit | `test_templates.py::test_template_inventory` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | META-03 | T-04-06 | No `${...}`; every `{{...}}` is in the known set | unit | `...::test_placeholder_lint` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | META-03 | — | The ADR template moved and the old path is gone | unit | `...::test_adr_template_moved` + updated `test_adrs.py` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | META-04 | T-04-02 | Second run reports `UNCHANGED` and exit 0 | integration | `test_new_homework.py::test_second_run_is_noop` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | META-04 | T-04-02 | Modified target reports `CONFLICT`, exit 1, and writes nothing | integration | `...::test_conflict_writes_nothing` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | META-04 | — | `--dry-run` prints the same records and creates nothing | integration | `...::test_dry_run_parity` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | META-04 | — | Golden trees match for both templates | integration | `...::test_golden_tree` (unified diff on failure) | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | D-13 | — | PEP 723 and pre-commit declarations agree | unit | `test_metadata_deps.py::test_pinned_versions_agree` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | D-37 | — | The pre-commit hook's config shape is correct | unit | `test_metadata_deps.py::test_hook_declaration` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `scripts/tests/test_homework_metadata.py` — covers META-01, META-02, the allowlist, exit codes and `--json`
- [ ] `scripts/tests/test_new_homework.py` — covers META-04, FOUND-01's path set, idempotency, dry-run, conflict, and the golden trees
- [ ] `scripts/tests/test_templates.py` — covers META-03 and the `platformio.ini` shape
- [ ] `scripts/tests/test_metadata_deps.py` — covers D-13's drift rule
- [ ] `scripts/tests/fixtures/golden/homework-{arduino,espidf}/` — the committed expected trees
- [ ] A shared temp-root helper (copytree + symlink `lib/`) used by the scaffold tests
- [ ] Update `scripts/tests/test_adrs.py`'s `TEMPLATE_FILE` (Pitfall P12)
- [ ] No framework install is needed; the suite is stdlib-only

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Target firmware build for both templates | FOUND-01 | Requires the ESP32-S3 toolchain; not part of the stdlib test suite | Run `pio run` in the scaffolded Arduino and ESP-IDF fixtures; expect `SUCCESS` and inspect `sdkconfig.json` for 16 MB flash and octal PSRAM |

*All other phase behaviors have automated verification.*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 90s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

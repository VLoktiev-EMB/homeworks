---
phase: 04-metadata-contract-and-scaffolding
verified: 2026-10-24T22:23:26Z
status: gaps_found
score: 57/59 must-haves verified
covered_files: [".planning/phases/04-metadata-contract-and-scaffolding/04-01-PLAN.md",".planning/phases/04-metadata-contract-and-scaffolding/04-01-SUMMARY.md",".planning/phases/04-metadata-contract-and-scaffolding/04-02-PLAN.md",".planning/phases/04-metadata-contract-and-scaffolding/04-02-SUMMARY.md",".planning/phases/04-metadata-contract-and-scaffolding/04-03-PLAN.md",".planning/phases/04-metadata-contract-and-scaffolding/04-03-SUMMARY.md",".planning/phases/04-metadata-contract-and-scaffolding/04-04-PLAN.md",".planning/phases/04-metadata-contract-and-scaffolding/04-04-SUMMARY.md",".planning/phases/04-metadata-contract-and-scaffolding/04-05-PLAN.md",".planning/phases/04-metadata-contract-and-scaffolding/04-05-SUMMARY.md",".planning/phases/04-metadata-contract-and-scaffolding/04-06-PLAN.md",".planning/phases/04-metadata-contract-and-scaffolding/04-06-SUMMARY.md",".planning/phases/04-metadata-contract-and-scaffolding/04-07-PLAN.md",".planning/phases/04-metadata-contract-and-scaffolding/04-07-SUMMARY.md",".planning/phases/04-metadata-contract-and-scaffolding/04-08-PLAN.md",".planning/phases/04-metadata-contract-and-scaffolding/04-08-SUMMARY.md",".pre-commit-config.yaml","AGENTS.md","NOTICE","REUSE.toml","docs/decisions/0009-homework-metadata-contract.md","docs/decisions/0010-python-dependency-policy.md","docs/decisions/README.md","schema/homework.schema.json","scripts/check_metadata.py","scripts/metadata/__init__.py","scripts/metadata/allowlist.json","scripts/metadata/contract.py","scripts/new_homework","scripts/tests/fixtures/golden/homework-arduino/README.md","scripts/tests/fixtures/golden/homework-arduino/assets/.gitkeep","scripts/tests/fixtures/golden/homework-arduino/homework.yaml","scripts/tests/fixtures/golden/homework-arduino/include/.gitkeep","scripts/tests/fixtures/golden/homework-arduino/platformio.ini","scripts/tests/fixtures/golden/homework-arduino/src/main.cpp","scripts/tests/fixtures/golden/homework-arduino/task.md","scripts/tests/fixtures/golden/homework-arduino/test/test_homework/test_homework.c","scripts/tests/fixtures/golden/homework-espidf/README.md","scripts/tests/fixtures/golden/homework-espidf/assets/.gitkeep","scripts/tests/fixtures/golden/homework-espidf/homework.yaml","scripts/tests/fixtures/golden/homework-espidf/include/.gitkeep","scripts/tests/fixtures/golden/homework-espidf/platformio.ini","scripts/tests/fixtures/golden/homework-espidf/sdkconfig.defaults","scripts/tests/fixtures/golden/homework-espidf/src/main.cpp","scripts/tests/fixtures/golden/homework-espidf/task.md","scripts/tests/fixtures/golden/homework-espidf/test/test_homework/test_homework.c","scripts/tests/temp_root.py","scripts/tests/test_adrs.py","scripts/tests/test_homework_metadata.py","scripts/tests/test_metadata_deps.py","scripts/tests/test_new_homework.py","scripts/tests/test_templates.py","templates/adr/template.md","templates/board-profile/profile.yaml","templates/homework-arduino/README.md","templates/homework-arduino/assets/.gitkeep","templates/homework-arduino/homework.yaml","templates/homework-arduino/include/.gitkeep","templates/homework-arduino/platformio.ini","templates/homework-arduino/src/main.cpp","templates/homework-arduino/template.yaml","templates/homework-arduino/test/test_homework/test_homework.c","templates/homework-espidf/README.md","templates/homework-espidf/assets/.gitkeep","templates/homework-espidf/homework.yaml","templates/homework-espidf/include/.gitkeep","templates/homework-espidf/platformio.ini","templates/homework-espidf/sdkconfig.defaults","templates/homework-espidf/src/main.cpp","templates/homework-espidf/template.yaml","templates/homework-espidf/test/test_homework/test_homework.c","templates/report/report.md","templates/task/task.md"]
covered_digest: "v3:sha256:ecc427837b9dcc07f2a4d21b414bbc83250392a1a0d5dade3e306b6832799fff"
behavior_unverified: 1
overrides_applied: 0
re_verification:
  previous_status: gaps_found
  previous_score: 54/56
  gaps_closed:
    - "A symlink at `homeworks/` itself is refused at exit 2 with empty stdout before any plan record, for both `--dry-run` and a real run; the link stays intact and its destination receives no file (04-08)."
    - "A non-directory `homeworks` base and a base that does not resolve to `<root>/homeworks` are refused before the plan, and every 04-06 refusal beneath `homeworks/<id>` is unchanged (04-08)."
    - "A mismatched `id` under a symlinked `homeworks` base is an ERROR record at exit 1 in the default directory scan (04-08)."
  gaps_remaining:
    - "The id-equals-directory invariant is silently skipped when an explicit absolute positional path uses a spelling that differs from the resolved root (for example `/tmp` versus `/private/tmp` on macOS), so the checker exits 0 on a mismatched id."
  regressions:
    - "The lexical derivation added in d65619f regressed the spelling-mismatch case that the previous `resolve()`-based helper handled: the current helper returns None instead of the containing directory."
gaps:
  - truth: "A `homework.yaml` whose `id` differs from its containing `homeworks/<dir>/` is rejected as an ERROR record at exit 1."
    status: failed
    reason: "Reproduced on a disposable root under the macOS `/tmp` spelling (canonical `/private/tmp`). `scripts/check_metadata.py --dir /tmp/claude-501/verify04-clean /tmp/claude-501/verify04-clean/homeworks/1_3-ctrl` exits 0 with `PASS: metadata contract satisfied` for a `homework.yaml` holding `id: \"9_9-other\"` in directory `1_3-ctrl`. The same tree is correctly rejected at exit 1 when the positional is relative (`homeworks/1_3-ctrl`), when both spellings are canonical, and when the default scan runs — so the invariant depends on the absolute spelling agreeing with `resolve_root()`. The cause is `_homework_directory()` comparing `os.path.abspath(root)` (root is already resolved by `resolve_root`) against `os.path.abspath(path)` (an absolute positional keeps the caller's spelling); the prefix comparison fails and the helper returns `None`, which both `validate_homework_text` and `validate_candidate` treat as 'identity not applicable'. The same bypass suppresses the symlinked-base protection: `--dir /private/tmp/.../verify04-base /tmp/.../verify04-base/homeworks/1_3-good` exits 0 with `homework.yaml: OK` even though the id is `1_3-other`. This is the carried-forward identity gap, not new scope: the file was modified after the previous verification (d65619f), and the pre-04-08 `resolve()`-based helper returned `1_3-ctrl` for the same inputs, so the lexical rewrite introduced the regression."
    artifacts:
      - path: "scripts/metadata/contract.py"
        issue: "`_homework_directory()` (lines 582-599) compares two independently canonicalized spellings; `os.path.abspath` normalizes `.`/`..` but does not reconcile `/tmp` with `/private/tmp`, so a root/path spelling mismatch returns `None` instead of the containing directory."
      - path: "scripts/check_metadata.py"
        issue: "`_directories()` (lines 147-182) hands the caller's lexical absolute target to validation, so an explicit positional in the non-canonical spelling reaches `_homework_directory()` unreconciled."
      - path: "scripts/tests/test_homework_metadata.py"
        issue: "No regression covers a differing root/path spelling for an explicit positional; `IdentityTests.test_id_mismatch_survives_a_symlinked_homeworks_base` and `run_fixture()` never pass a positional path."
    missing:
      - "Derive the containing directory in a spelling-independent way: resolve the prefix before the `homeworks` component and compare it with the resolved root, while keeping the `homeworks` component and everything below it lexical (resolving them would reopen the symlinked-base bypass)."
      - "Regression test: a disposable root created under a non-canonical spelling (for example `/tmp/...`), invoked as `--dir <same spelling> <same spelling>/homeworks/<dir>` with a mismatched id, must exit 1 with the containing-directory ERROR; a canonical-spelling control must agree."
      - "Re-check that the default scan and the symlinked-`homeworks` case still reject after the change."
advisory:
  - finding: "TOCTOU between plan and write: `_write_all` re-walks the path with `mkdir(parents=True, exist_ok=True)` and `os.replace`, so a component swapped to a symlink after classification could redirect the write."
    category: security
    reason: "Same containment class as the fixed truth, but no deterministic evidence: reproduction needs a concurrent actor inside the plan-to-write window. Re-checking components immediately before each write, or using `O_NOFOLLOW` directory descriptors, would close it. Not counted as a blocker."
    evidence_status: "none provided"
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
**Verified:** 2026-10-24T22:23:26Z
**Status:** gaps_found
**Re-verification:** Yes — after gap closure (04-06, 04-07, 04-08)

## Goal Achievement

The scaffold side is genuinely finished: a symlink at `homeworks/` itself is now refused at exit 2 before any plan record, for both `--dry-run` and a real run, under both canonical and non-canonical root spellings; a non-directory base is refused; every refusal beneath `homeworks/<id>` still holds; both templates still scaffold, build (5.85 s Arduino, 25.18 s ESP-IDF) and pass their native suites (2/2); the 307-test suite, `pre-commit run --all-files` and `reuse lint` are green. Both prior contract gaps (one allowlist entry suppressing every Cyrillic record for its path, and composed YAML keys becoming ERROR records) were re-reproduced and remain closed.

One contract invariant still fails, and it is a regression introduced by 04-08: `_homework_directory()` now compares two independently canonicalized absolute spellings. When an explicit absolute positional path uses a spelling that differs from the resolved root — the normal macOS `/tmp` → `/private/tmp` and `/var` → `/private/var` situation, which is exactly `$TMPDIR` here — the prefix comparison fails, the helper returns `None`, and the checker exits 0 on a `homework.yaml` whose `id` does not match its directory. The pre-04-08 `resolve()`-based helper handled that spelling correctly; the lexical rewrite traded that case for the symlinked-base case instead of covering both.

### Observable Truths

| # | Truth | Status | Evidence |
| --- | --- | --- | --- |
| 1 | [ROADMAP SC1] `scripts/new_homework` scaffolds from either template, is idempotent, supports `--dry-run`, and refuses to overwrite | ✓ VERIFIED | Fresh run 8 CREATE; second run 8 UNCHANGED, exit 0; `DryRunTests` and `ConflictTests` pass |
| 2 | [ROADMAP SC2] Scaffolded project has `platformio.ini`, `src/`, `include/`, `test/`, `assets/`, `README.md`, `task.md`, `homework.yaml`, and builds immediately | ✓ VERIFIED | Fresh scaffolds produced 8 (Arduino) and 9 (ESP-IDF) paths; `pio run` SUCCESS 5.85 s / 25.18 s; native 2/2 |
| 3 | [ROADMAP SC3] `homework.yaml` validated by a JSON Schema with `additionalProperties: false`; unknown key rejected; every required field recorded | ✓ VERIFIED | 6 `additionalProperties: false` (root + five `$defs`); `bogus: 1` → ERROR, exit 1 |
| 4 | [ROADMAP SC4] `task.md` contains an English paraphrase, source reference, retrieval date, attribution, and no original internal material | ⚠️ PRESENT_BEHAVIOR_UNVERIFIED | Shape rules enforced; originality is not machine-verifiable — see Human Verification |
| 5 | [ROADMAP SC5] `templates/` provides Arduino, ESP-IDF, report, task, ADR and board-profile templates | ✓ VERIFIED | All six directories exist; `test_templates` 22 tests OK |
| 6 | [04-01] Checker exits 0 on valid `homework.yaml` and prints `PATH: OK — reason` | ✓ VERIFIED | Repository root and a fresh scaffolded tree both `PASS: metadata contract satisfied`, exit 0 |
| 7 | [04-01] Unknown key inside each nested block rejected independently | ✓ VERIFIED | `additionalProperties: false` in every `$def`; `test_unknown_nested_key_is_error` passes |
| 8 | [04-01] Every invalid research probe rejected | ✓ VERIFIED | `test_research_probes_are_rejected` covers all nine cases |
| 9 | [04-01] Every required root key and every required `$def` member proven separately | ✓ VERIFIED | `test_every_required_root_key_is_required` / `test_every_required_defs_member_is_required` pass |
| 10 | [04-01] `homework.yaml` whose `id` differs from its containing `homeworks/<dir>/` is rejected | ✗ FAILED | `--dir /tmp/... /tmp/.../homeworks/1_3-ctrl` with `id: "9_9-other"` exits 0; relative or canonical-spelling positional exits 1 — see gap |
| 11 | [04-01] YAML syntax errors, non-mapping payloads and duplicate mapping keys → ERROR record, exit 1, never 2 | ✓ VERIFIED | Three tests pass; composed-key case passes (rows 16) |
| 12 | [04-01] A `homework.yaml` over 64 KiB → ERROR record and exit 1 | ✓ VERIFIED | `test_oversized_document_is_error` passes |
| 13 | [04-01] Schema uses patterns, never the `format` keyword | ✓ VERIFIED | `grep '"format"'` → 0; `test_schema_contains_no_format_keyword` passes |
| 14 | [04-01] A second identical run is byte-identical and leaves the tree unchanged; checker is read-only | ✓ VERIFIED | `test_second_run_is_identical_and_read_only` passes; manual UNCHANGED run |
| 15 | [04-01] Canonical ID pattern literal identical in schema, `contract.py`, `AGENTS.md`, `EXPECTED_PATTERN` | ✓ VERIFIED | `test_canonical_id_literal_is_identical_in_four_places` passes |
| 16 | [derived, 04-01 Task 3] Every content problem is an ERROR record at exit 1 and `--json` always prints one JSON array | ✓ VERIFIED (gap closed) | Manual composed key in both documents → exit 1, one array, no traceback; both tests pass |
| 17 | [04-02] Arduino template has `template.yaml` plus the seven non-task FOUND-01 paths | ✓ VERIFIED | Directory listing matches; `test_arduino_tree_matches_its_golden` passes |
| 18 | [04-02] ESP-IDF template has the same set plus `sdkconfig.defaults`, no generated build input | ✓ VERIFIED | `test_espidf_ships_no_generated_build_input` passes |
| 19 | [04-02] Neither homework template contains `task.md` | ✓ VERIFIED | `find` shows none under `templates/homework-*` |
| 20 | [04-02] A copy rendered at `homeworks/<id>` depth builds, and its native environment passes `pio test -e native` | ✓ VERIFIED | Scaffolded Arduino native 2/2; both target builds SUCCESS |
| 21 | [04-02] Both starter files call `lib/port` through the matching adapter | ✓ VERIFIED | `arduino_gpio_port()` / `espidf_gpio_port()` calls present; adapters compiled |
| 22 | [04-02] Arduino entry defines `setup`/`loop`; ESP-IDF defines `app_main` with C linkage | ✓ VERIFIED | `extern "C" void app_main(void)` inspected in the ESP-IDF template |
| 23 | [04-02] Target env declares only `extends` and `lib_deps`; `lib/host` and Unity only in `[env:native]` | ✓ VERIFIED | `test_target_section_declares_only_extends_and_lib_deps` passes |
| 24 | [04-02] `default_envs` names the target only; no dollar-brace interpolation anywhere | ✓ VERIFIED | `grep -rn '\${' templates/` → none; `test_no_dollar_brace_interpolation` passes |
| 25 | [04-03] `task.md` frontmatter parsed as text with the base loader, so an unquoted ISO timestamp stays a string | ✓ VERIFIED | `StrictBaseLoader`; `test_unquoted_iso_timestamp_stays_a_string` passes |
| 26 | [04-03] The four TODO provenance fields pass only while `status: planned` | ✓ VERIFIED | Both sentinel tests pass; manual `status: complete` yields five ERROR records, exit 1 |
| 27 | [04-03] Non-URL `source_url`, date without timezone, non-SPDX license rejected | ✓ VERIFIED | `test_invalid_shapes_are_rejected` passes |
| 28 | [04-03] Cyrillic anywhere is an error unless the allowlist names that exact path with a non-empty reason; unmatched entry fails | ✓ VERIFIED (gap closed) | Manual two-Cyrillic-lines + one entry → exit 0; stale/empty-reason tests pass |
| 29 | [04-03] `source.reference` and `source_url` must agree when both are URLs | ✓ VERIFIED | `test_mismatched_reference_and_source_url_is_error` passes |
| 30 | [04-03] Malformed frontmatter, duplicate frontmatter key and task.md over 64 KiB → ERROR, exit 1 | ✓ VERIFIED | Three tests pass; composed-key frontmatter ERROR (row 16) |
| 31 | [04-03] A directory with neither `homework.yaml` nor `task.md` produces a deterministic ERROR | ✓ VERIFIED | `test_orphan_directory_is_error` passes |
| 32 | [04-03] Cyrillic detection covers every Cyrillic block, incl. Extended-B | ✓ VERIFIED | `test_extended_b_character_is_rejected` passes |
| 33 | [04-03] Body TODOs documented as manual-review signals; only the five provenance fields are status-gated | ✓ VERIFIED | ADR-0009 "The sentinel rule" states both |
| 34 | [04-03] `templates/task`, `report`, `board-profile`, `adr` exist; ADR template moved with no copy left | ✓ VERIFIED | `templates/adr/template.md` present; old path absent; `test_adrs` passes |
| 35 | [04-03] `NOTICE` names `templates/adr/template.md` and no longer the old path | ✓ VERIFIED | NOTICE line 21 references only the new path |
| 36 | [04-04] Malformed id, unknown template, missing manifest, unknown placeholder and dollar-brace each exit 2 before any plan output | ✓ VERIFIED | Six `ErrorTests` pass; base refusals also exit 2 (rows 57-59) |
| 37 | [04-04] Template selection is dynamic; no argparse `choices` registry | ✓ VERIFIED | `test_new_template_directory_is_accepted_without_a_cli_change` passes |
| 38 | [04-04] A rendered `homework.yaml` whose `id` differs from the target directory is rejected as ERROR | ✓ VERIFIED | Bad template under a non-canonical root: exit 1, mismatch ERROR, no target directory created |
| 39 | [04-04/04-06/04-08] A symlink at any candidate target path, intermediate component, or `homeworks/` base is refused, never followed or compared through | ✓ VERIFIED (gap closed) | Six `ConflictTests` pass; manual base-symlink dry/real runs exit 2 with empty stdout; destination receives nothing |
| 40 | [04-04] Write phase creates each parent before `mkstemp`; a conflict or `--dry-run` creates no directory | ✓ VERIFIED | Code order confirmed; dry-run/conflict directory tests pass |
| 41 | [04-04] Scaffolded Arduino and ESP-IDF trees match their golden trees byte-for-byte | ✓ VERIFIED | `test_arduino_tree_matches_its_golden` / `test_espidf_tree_matches_its_golden` pass |
| 42 | [04-04] PEP 723 pins equal the pre-commit hook dependencies, and the suite invokes the hook | ✓ VERIFIED | `test_metadata_deps` passes |
| 43 | [04-04] Validation and conflict failures leave the tree untouched; an OS write failure may leave a partial project | ✓ VERIFIED | `test_conflict_and_deletion_write_nothing` passes; write-phase order confirmed |
| 44 | [04-05] ADR-0009/0010 have the five MADR keys, eight sections in order, chosen-option sentence, ≥2 options, agreeing index rows | ✓ VERIFIED | `test_adrs.py` passes |
| 45 | [04-05] `docs/decisions/README.md` states `Next number: 0011` | ✓ VERIFIED | Read: line 35 |
| 46 | [04-05] `AGENTS.md` lists the present paths, adds the checker to quick-start and both routing rows, ≤300 lines | ✓ VERIFIED | 227 lines; quick-start and routing rows present |
| 47 | [04-05] `AGENTS.md` contains exactly one backticked anchored regex | ✓ VERIFIED | Line 107 is the only occurrence; `test_agents_md` passes |
| 48 | [04-05] `test_agents_md` and `test_homework_id` pass after the edit without changing either test | ✓ VERIFIED | 307-test suite OK |
| 49 | [04-05] ADR-0009 lists all five sentinel-bearing fields normatively and records body TODOs as manual-review | ✓ VERIFIED | Numbered list 1-5 plus manual-review paragraph |
| 50 | [04-05] `REUSE.toml` declares `templates/**/*.md` as CC-BY-4.0 after the MIT catch-all; `reuse lint` passes | ✓ VERIFIED | MIT `path = "**"` precedes the CC-BY annotation; `reuse lint` compliant (253/253) |
| 51 | [04-05] `scripts/new_homework` scaffolds both templates into a temp root and each builds with `pio run` | ✓ VERIFIED | Arduino SUCCESS 5.85 s; ESP-IDF SUCCESS 25.18 s from scaffolded output |
| 52 | [04-05] Scaffolded Arduino native environment passes `pio test -e native` | ✓ VERIFIED | 2/2 tests passed |
| 53 | [04-05] Scaffolded ESP-IDF reports 16 MB flash and octal PSRAM | ✓ VERIFIED | `.pio/build/esp32s3_espidf/config/sdkconfig.json`: `ESPTOOLPY_FLASHSIZE: "16MB"`, `SPIRAM_MODE_OCT: true` |
| 54 | [04-05] Full repository suite and `pre-commit run --all-files` are green | ✓ VERIFIED | 307 tests OK; `pre-commit run --all-files` exit 0 |
| 55 | [04-06] A regular file at an intermediate target component is CONFLICT, exit 1, file unchanged | ✓ VERIFIED | `test_regular_file_at_intermediate_path_is_conflict` passes |
| 56 | [04-07] An allowlisted path still fails on a non-Cyrillic content problem | ✓ VERIFIED | Manual: two Cyrillic lines + allowlist → exit 0; add `source_url: not-a-url` → exit 1 with the URL error |
| 57 | [04-08] A symlink at `homeworks/` itself is refused with exit 2 and empty stdout before any plan record, for both `--dry-run` and a real run; link intact, destination receives no file | ✓ VERIFIED | Manual `/tmp`-spelled root: both runs `ERROR: homeworks is a symlink; refusing to follow it`, exit 2, 0 stdout bytes, outside dir empty; test passes |
| 58 | [04-08] A non-directory `homeworks` base is refused at exit 2 | ✓ VERIFIED | Manual regular file at `homeworks` → `ERROR: homeworks exists and is not a directory`, exit 2 |
| 59 | [04-08] A mismatched `id` is an ERROR at exit 1 under a symlinked `homeworks` base, and the resolved base must equal `<root>/homeworks` | ✓ VERIFIED | Manual `--dir /tmp/...` default scan → `id: '1_3-other' does not match the containing directory '1_3-good'`, exit 1; test passes; normal, absent and non-canonical roots accepted |

**Score:** 57/59 truths verified (1 present, behavior-unverified; 1 failed)

Gap-closure truth mapping: 04-08's base-refusal, non-directory and resolved-base truths are rows 57-59; its symlinked-ancestor id-match truth is folded into row 59 (default scan) and its spelling-independent generality is what fails at row 10. 04-06's target/intermediate/final/regular-file truths map onto rows 39 and 55; 04-07's allowlist and composed-key truths onto rows 28, 16 and 56.

### Deferred Items

None — no later phase in the milestone claims the checker's identity invariant or scaffold containment.

### Advisory (New Scope, Unevidenced)

| # | Finding | Category | Why Advisory |
|---|---------|----------|--------------|
| 1 | TOCTOU between the plan and the write phase: `_write_all` re-walks the path with `mkdir(parents=True, exist_ok=True)` and `os.replace`, so a component swapped to a symlink after classification could redirect the write (T-04-28) | security | Same containment class, but reproduction needs a concurrent local actor; no deterministic evidence, so it is reported, not blocking. The 04-08 plan records it as accepted debt. |

### Required Artifacts

| Artifact | Expected | Status | Details |
| --- | --- | --- | --- |
| `schema/homework.schema.json` | JSON Schema 2020-12 contract | ✓ VERIFIED | Strict at all depths, patterns only, no `format` |
| `scripts/metadata/__init__.py` | Package marker | ✓ VERIFIED | Docstring-only |
| `scripts/metadata/contract.py` | Single validation implementation | ✓ VERIFIED | Path-keyed `apply_allowlist`; `Hashable` guards; lexical identity helper (spelling-dependent — gap) |
| `scripts/check_metadata.py` | Thin 0/1/2 entry point | ✓ VERIFIED | Imports contract; no rules re-implemented |
| `scripts/new_homework` | Plan-then-write scaffold | ✓ VERIFIED | Base `lstat` + resolved-base equality; component walk; writes only after the plan is clean |
| `scripts/tests/test_homework_metadata.py` | META-01/02 matrix | ✓ VERIFIED | 57 tests; no spelling-mismatch positional regression |
| `scripts/tests/test_new_homework.py` | META-04/FOUND-01 matrix | ✓ VERIFIED | 27 tests, including the base-symlink refusal for dry-run and real |
| `scripts/tests/test_templates.py` | META-03 inventory | ✓ VERIFIED | 22 tests |
| `scripts/tests/test_metadata_deps.py` | D-13 drift + hook invocation | ✓ VERIFIED | Passes |
| `scripts/tests/temp_root.py` | Disposable root harness | ✓ VERIFIED | `homeworks=False` used by the base-symlink test |
| `scripts/tests/fixtures/golden/homework-arduino/` | Committed golden tree | ✓ VERIFIED | 8 files, byte-identical |
| `scripts/tests/fixtures/golden/homework-espidf/` | Committed golden tree | ✓ VERIFIED | 9 files, byte-identical |
| `templates/homework-arduino/` | Arduino template | ✓ VERIFIED | 8 authored files including `template.yaml` |
| `templates/homework-espidf/` | ESP-IDF template | ✓ VERIFIED | 9 authored files including `sdkconfig.defaults` |
| `templates/task/task.md`, `report/`, `board-profile/`, `adr/` | Skeleton templates | ✓ VERIFIED | All present |
| `scripts/metadata/allowlist.json` | Empty allowlist | ✓ VERIFIED | Version 1, no entries |

### Key Link Verification

| From | To | Via | Status | Details |
| --- | --- | --- | --- | --- |
| `check_metadata.py` | `scripts/metadata/contract.py` | `sys.path.insert` + imports | WIRED | No validation rule re-implemented |
| `contract.py` | `schema/homework.schema.json` | `SCHEMA_PATH` against root | WIRED | One literal |
| schema `id.pattern` | `contract.py` / `AGENTS.md` / `test_homework_id.py` | shared canonical literal | WIRED | Byte-identical in all four |
| `validate_homework_text` | containing `homeworks/<dir>/` | `_homework_directory()` | ⚠️ PARTIAL | Fires for relative/canonical positionals and the default scan; returns `None` when the absolute path spelling differs from the resolved root (gap) |
| template `platformio.ini` | `../../platformio.shared.ini` | `extra_configs` | WIRED | Both builds resolved it |
| `src/main.cpp` | `port/` + adapter headers | factory calls | WIRED | Adapters compiled |
| template native test | `lib/host` + Unity | `pio test -e native` | WIRED | 2/2 passed |
| `new_homework` | `validate_candidate` | import + call before first `mkdir` | WIRED | Scaffold rejects a rendered id mismatch (manual bad template) |
| `_contained_target` | `homeworks` base | `os.lstat` + `base.resolve()` equality | WIRED | Symlink/non-directory refused at exit 2; absent and normal bases accepted |
| `_component_conflict` | every component from `homeworks/<id>` down | `os.lstat` walk before `_classify` | WIRED | Six conflict tests pass |
| `_write_all` | blocked-plan precondition | early return before write phase | WIRED | Reached only when no CONFLICT/ERROR |
| `apply_allowlist` | record path | path-keyed suppression + `used_paths` staleness | WIRED | Two-Cyrillic-line manual case exits 0 |
| strict loaders | ERROR records | unhashable key → `ConstructorError` | WIRED | Both documents yield one JSON array, no traceback |
| `test_adrs.py` | moved ADR template + README | relative link | WIRED | Passes |
| `_write_atomic` | target directory + `os.replace` | temp file + replace | ⚠️ PARTIAL | Statically safe; TOCTOU window remains (advisory) |
| ADR-0009 | checker behaviour | written authority | WIRED | Schema path and sentinel rule documented |
| `AGENTS.md` | schema path | repository contract | WIRED | Names the schema path |
| phase gate | scaffolded output | temp-root build | WIRED | Built from scaffolded trees |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
| --- | --- | --- | --- | --- |
| `check_metadata.py` | `records` | `contract.validate_*` over real files | Yes — valid, unknown-key, allowlist, composed-key and identity runs | ✓ FLOWING |
| `new_homework` | `payloads` / `records` | templates → `_render` → `validate_candidate` → write | Yes — files written and byte-compared | ✓ FLOWING |
| ESP-IDF build | `sdkconfig.json` | ESP-IDF build system | Yes — 16 MB, octal PSRAM | ✓ FLOWING |
| `templates/board-profile/profile.yaml` | board id | not read by any executable | No consumer | ✗ DISCONNECTED (WR-03, warning unchanged) |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| --- | --- | --- | --- |
| Checker accepts valid metadata | `uv run --offline scripts/check_metadata.py` (repo root) | `PASS: metadata contract satisfied`, exit 0 | ✓ PASS |
| Checker rejects unknown top-level key | appended `bogus: 1` | `ERROR — Additional properties are not allowed ('bogus' …)`, exit 1 | ✓ PASS |
| Scaffold creates the eight paths | `uv run --offline scripts/new_homework 1_3-fixture --template arduino --dir <tmp>` | 8 CREATE records, exit 0 | ✓ PASS |
| Second run is idempotent | same again | 8 `UNCHANGED`, exit 0 | ✓ PASS |
| `homeworks/` itself a symlink, `--dry-run` | `homeworks -> <outside>` | exit 2, empty stdout, `ERROR: homeworks is a symlink; refusing to follow it` | ✓ PASS |
| `homeworks/` itself a symlink, real run | same | exit 2, empty stdout, outside directory empty, link intact | ✓ PASS |
| `homeworks` is a regular file | `homeworks` contains text | exit 2, `ERROR: homeworks exists and is not a directory` | ✓ PASS |
| Symlink at `homeworks/<id>` | link to a sibling directory | exit 2, empty stdout, destination empty | ✓ PASS |
| Intermediate symlink | `homeworks/<id>/src -> <outside>` | exit 1, CONFLICT naming the path, 0 files outside | ✓ PASS |
| Regular file at intermediate path | `homeworks/<id>/src` is a file | exit 1, CONFLICT, bytes unchanged | ✓ PASS |
| Whole-path allowlist | two Cyrillic lines + one entry for the path | exit 0, no ERROR record | ✓ PASS |
| Allowlist is rule-scoped | same path + `source_url: not-a-url` | exit 1 with the URL error | ✓ PASS |
| Composed YAML key in `homework.yaml` | `? [a, b]` + `--json` | exit 1, one JSON array, `found unhashable key`, no traceback | ✓ PASS |
| Composed YAML key in `task.md` frontmatter | same `--json` | exit 1, one JSON array, ERROR record, no traceback | ✓ PASS |
| Mismatched id, mismatched root/path spelling | `--dir /tmp/... /tmp/.../homeworks/1_3-ctrl` | exit 0 (`PASS`) — invariant skipped | ✗ FAIL |
| Mismatched id, relative positional | `--dir /tmp/... homeworks/1_3-ctrl` | exit 1 with the containing-directory ERROR | ✓ PASS |
| Mismatched id, canonical spellings | `--dir /private/tmp/... /private/tmp/.../homeworks/1_3-ctrl` | exit 1 with the containing-directory ERROR | ✓ PASS |
| Mismatched id through a symlinked base, explicit cross-spelling positional | `--dir /private/tmp/.../verify04-base /tmp/.../verify04-base/homeworks/1_3-good` | exit 0 (`PASS: metadata contract satisfied`) — invariant and path prefix both lost | ✗ FAIL |
| Mismatched id through a symlinked base, default scan | `--dir /tmp/.../verify04-base` | exit 1 with the containing-directory ERROR | ✓ PASS |
| Rendered id mismatch in the scaffold | bad template rendering `id: "9_9-other"`, target `1_3-bad` | exit 1, ERROR record, no target directory | ✓ PASS |
| Arduino target build | `pio run -d …/1_3-good` | SUCCESS, 5.85 s | ✓ PASS |
| ESP-IDF target build | `pio run -d …/1_3-gate-espidf` | SUCCESS, 25.18 s | ✓ PASS |
| Scaffolded native test | `pio test -d …/1_3-good -e native` | 2/2 succeeded | ✓ PASS |
| Golden byte equality | `test_new_homework` golden tests | 8/8 and 9/9, zero mismatches | ✓ PASS |
| Repository suite | `python3 -m unittest discover -s scripts/tests` | 307 tests OK | ✓ PASS |
| Local gate | `pre-commit run --all-files` | all hooks Passed, exit 0 | ✓ PASS |
| License gate | `reuse --no-multiprocessing lint` | compliant with REUSE 3.3 (253/253) | ✓ PASS |

### Probe Execution

Not applicable: the phase declares no `probe-*.sh` scripts (`find scripts -path '*/tests/probe-*.sh'` returned nothing) and its validation strategy names no probe harness. The phase gate is the build + suite + pre-commit matrix recorded above.

### Test Quality Audit

| Test File | Linked Req | Active | Skipped | Circular | Assertion Level | Verdict |
|-----------|-----------|--------|---------|----------|-----------------|---------|
| `scripts/tests/test_homework_metadata.py` | META-01, META-02 | 57 | 0 | 0 | Value/behavioral | PASS |
| `scripts/tests/test_new_homework.py` | META-04, FOUND-01 | 27 | 0 | 0 | Value/behavioral | PASS |
| `scripts/tests/test_templates.py` | META-03, FOUND-01 | 22 | 0 | 0 | Value | PASS |
| `scripts/tests/test_metadata_deps.py` | META-04 | — | 0 | 0 | Value | PASS |

**Disabled tests on requirements:** 0.
**Circular patterns detected:** 0 (the golden trees are committed snapshots, independently byte-compared).
**Insufficient assertions:** 1 — `CyrillicGateTests.test_allowlisted_path_still_rejects_a_shape_violation` has no Cyrillic in its fixture, so it also passes if `apply_allowlist` is never invoked (WR-08). The behaviour was verified directly with a two-Cyrillic-line fixture that still rejects the shape error. WARNING, not blocking.
**Missing regression:** 1 — no test drives `check_metadata.py` with an explicit absolute positional under a spelling that differs from the resolved root; that gap is why the row-10 regression passed the 307-test suite.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| --- | --- | --- | --- | --- |
| FOUND-01 | 04-02, 04-04, 04-05, 04-06, 04-08 | One independent PlatformIO project per homework with the eight paths | ✓ SATISFIED | Scaffold produces all eight paths; both templates build; the `homeworks/`-symlink containment escape is closed |
| META-01 | 04-01, 04-05, 04-07, 04-08 | `homework.yaml` validated by a JSON Schema with `additionalProperties: false`, full field set | ✓ SATISFIED | Schema + checker verified; composed-key case is an ERROR record. Caveat: the derived id-match identity truth (row 10) is spelling-dependent in the checker |
| META-02 | 04-03, 04-05, 04-07 | `task.md` carries paraphrase, source reference, retrieval date, attribution; never original internal material | ? NEEDS HUMAN | Shape, sentinel, Cyrillic and allowlist rules verified; paraphrase originality is a human review item |
| META-03 | 04-02, 04-03, 04-05 | Six templates exist | ✓ SATISFIED | All six directories and their declared files exist |
| META-04 | 04-04, 04-05, 04-06, 04-08 | Scaffold, idempotent, `--dry-run`, refuses overwrite | ✓ SATISFIED | Verified by manual runs and integration tests; base and component refusals verified |

No orphaned requirements: every Phase 4 requirement in `REQUIREMENTS.md` (FOUND-01, META-01–META-04) is claimed by at least one plan. ℹ️ Info: the checkbox lines for FOUND-01, META-03 and META-04 in `REQUIREMENTS.md` are still unchecked even though implementation evidence exists; that is bookkeeping, not a deliverable failure.

### Decision Coverage

All 39 trackable `04-CONTEXT.md` decisions are honored by shipped artifacts (`check.decision-coverage-verify`: 39/39, `not_honored: []`).

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| --- | --- | --- | --- | --- |
| `scripts/metadata/contract.py` | 582-599 | `_homework_directory()` compares `os.path.abspath(root)` with `os.path.abspath(path)`; a differing spelling returns `None` | 🛑 Blocker | The id-equals-directory invariant is silently skipped for explicit absolute positionals under a non-canonical root spelling (row 10) |
| `scripts/tests/test_homework_metadata.py` | `IdentityTests`, `run_fixture` | No regression drives an explicit absolute positional under a differing spelling | 🛑 Blocker | The regression passed the green suite unpinned |
| `scripts/new_homework` | 438-447 | Path re-walked at write time with ordinary `pathlib`/`os.replace` | ⚠️ Warning | TOCTOU window; advisory, needs a concurrent actor |
| `scripts/tests/test_homework_metadata.py` | 441-457 | Shape-violation fixture contains no Cyrillic character | ⚠️ Warning | Test passes without exercising suppression (WR-08); behaviour verified manually |
| `scripts/metadata/contract.py` | `apply_allowlist` | Duplicate allowlist entries never become stale | ℹ️ Info | Redundant entries are tolerated (IN-09) |
| `scripts/metadata/contract.py` | `lstrip` call | Literal BOM character in source | ℹ️ Info | Works, but invisible in review (IN-10) |
| `scripts/new_homework` | write phase | `mkstemp` leaves mode 0600; SIGKILL leaves temp files | ℹ️ Info | File modes differ from 0644; partial project on kill (IN-05) |

Debt-marker gate: no `TBD`, `FIXME` or `XXX` marker exists in any file this phase modified.

### Human Verification Required

1. **Paraphrase originality of the first real `task.md`**

   **Test:** Scaffold a homework, fill the four provenance fields and the body, then review the text.
   **Expected:** The body is an English paraphrase in the author's own words, with real `source_url`, `retrieved`, `attribution` and `license` values, and no original internal course material.
   **Why human:** The checker proves machine-observable shape only; the phase's own prohibitions forbid presenting it as proof of originality, and no real homework ships yet.

### Gaps Summary

The 04-08 scaffold work is real and complete. A symlink at `homeworks/` itself is now `lstat`ed before the plan: both `--dry-run` and a real run exit 2 with empty stdout, the link stays intact, and the destination receives no file — reproduced on this machine under the non-canonical `/tmp` spelling, with the canonical `/private/tmp` spelling behind it. A non-directory base exits 2, an absent base is still allowed, the resolved-base equality is present, and every 04-06 refusal beneath `homeworks/<id>` still passes. Both templates scaffold, build and pass native tests, the goldens are byte-identical, and the 307-test suite, `pre-commit` and `reuse lint` are green.

The identity half of the 04-08 contract is not spelling-independent, and that is a regression rather than a new discovery. `_homework_directory()` was correctly rewritten to stop resolving the candidate (which is what erased `homeworks/<dir>` under a symlinked base), but it now compares two spellings without reconciling them: `resolve_root()` canonicalizes the root to `/private/tmp/...`, while an explicit absolute positional keeps the caller's `/tmp/...` spelling. The prefix comparison fails, the helper returns `None`, and both the checker's `validate_homework_text` and the scaffold's `validate_candidate` treat that as "identity not applicable". On this machine that is not an exotic invocation — `$TMPDIR` is `/tmp/...`, so `--dir "$TMPDIR/root" "$TMPDIR/root/homeworks/x"` hits it. The same condition suppresses the symlinked-base protection when the two spellings are mixed. The pre-04-08 `resolve()`-based helper returned `1_3-ctrl` for the identical inputs, so `d65619f` traded one bypass for another instead of closing the class.

The fix is local and must not reopen the symlinked-base bypass: reconcile the spelling of the ancestor prefix (resolve the parts before the `homeworks` component and compare with the resolved root) while keeping the `homeworks` component and everything below it lexical, then pin both the default scan and an explicit same-spelling absolute positional under a non-canonical root. Until then the phase is not done, because "one schema-validated homework contract" includes the identity rule that `id` names its directory.

---

_Verified: 2026-10-24T22:23:26Z_
_Verifier: Claude (gsd-verifier)_

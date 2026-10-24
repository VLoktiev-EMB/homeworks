---
phase: 04-metadata-contract-and-scaffolding
verified: 2026-10-24T21:54:20Z
status: gaps_found
score: 54/56 must-haves verified
covered_files: [".planning/phases/04-metadata-contract-and-scaffolding/04-01-PLAN.md",".planning/phases/04-metadata-contract-and-scaffolding/04-01-SUMMARY.md",".planning/phases/04-metadata-contract-and-scaffolding/04-02-PLAN.md",".planning/phases/04-metadata-contract-and-scaffolding/04-02-SUMMARY.md",".planning/phases/04-metadata-contract-and-scaffolding/04-03-PLAN.md",".planning/phases/04-metadata-contract-and-scaffolding/04-03-SUMMARY.md",".planning/phases/04-metadata-contract-and-scaffolding/04-04-PLAN.md",".planning/phases/04-metadata-contract-and-scaffolding/04-04-SUMMARY.md",".planning/phases/04-metadata-contract-and-scaffolding/04-05-PLAN.md",".planning/phases/04-metadata-contract-and-scaffolding/04-05-SUMMARY.md",".planning/phases/04-metadata-contract-and-scaffolding/04-06-PLAN.md",".planning/phases/04-metadata-contract-and-scaffolding/04-06-SUMMARY.md",".planning/phases/04-metadata-contract-and-scaffolding/04-07-PLAN.md",".planning/phases/04-metadata-contract-and-scaffolding/04-07-SUMMARY.md",".pre-commit-config.yaml","AGENTS.md","NOTICE","REUSE.toml","docs/decisions/0009-homework-metadata-contract.md","docs/decisions/0010-python-dependency-policy.md","docs/decisions/README.md","schema/homework.schema.json","scripts/check_metadata.py","scripts/metadata/__init__.py","scripts/metadata/allowlist.json","scripts/metadata/contract.py","scripts/new_homework","scripts/tests/fixtures/golden/homework-arduino/README.md","scripts/tests/fixtures/golden/homework-arduino/assets/.gitkeep","scripts/tests/fixtures/golden/homework-arduino/homework.yaml","scripts/tests/fixtures/golden/homework-arduino/include/.gitkeep","scripts/tests/fixtures/golden/homework-arduino/platformio.ini","scripts/tests/fixtures/golden/homework-arduino/src/main.cpp","scripts/tests/fixtures/golden/homework-arduino/task.md","scripts/tests/fixtures/golden/homework-arduino/test/test_homework/test_homework.c","scripts/tests/fixtures/golden/homework-espidf/README.md","scripts/tests/fixtures/golden/homework-espidf/assets/.gitkeep","scripts/tests/fixtures/golden/homework-espidf/homework.yaml","scripts/tests/fixtures/golden/homework-espidf/include/.gitkeep","scripts/tests/fixtures/golden/homework-espidf/platformio.ini","scripts/tests/fixtures/golden/homework-espidf/sdkconfig.defaults","scripts/tests/fixtures/golden/homework-espidf/src/main.cpp","scripts/tests/fixtures/golden/homework-espidf/task.md","scripts/tests/fixtures/golden/homework-espidf/test/test_homework/test_homework.c","scripts/tests/temp_root.py","scripts/tests/test_adrs.py","scripts/tests/test_homework_metadata.py","scripts/tests/test_metadata_deps.py","scripts/tests/test_new_homework.py","scripts/tests/test_templates.py","templates/adr/template.md","templates/board-profile/profile.yaml","templates/homework-arduino/README.md","templates/homework-arduino/assets/.gitkeep","templates/homework-arduino/homework.yaml","templates/homework-arduino/include/.gitkeep","templates/homework-arduino/platformio.ini","templates/homework-arduino/src/main.cpp","templates/homework-arduino/template.yaml","templates/homework-arduino/test/test_homework/test_homework.c","templates/homework-espidf/README.md","templates/homework-espidf/assets/.gitkeep","templates/homework-espidf/homework.yaml","templates/homework-espidf/include/.gitkeep","templates/homework-espidf/platformio.ini","templates/homework-espidf/sdkconfig.defaults","templates/homework-espidf/src/main.cpp","templates/homework-espidf/template.yaml","templates/homework-espidf/test/test_homework/test_homework.c","templates/report/report.md","templates/task/task.md"]
covered_digest: "v3:sha256:d3eec8fbaf47eb1369e1d4fa8232b12c87bc7340219418a8b44728c801798d57"
behavior_unverified: 1
overrides_applied: 0
re_verification:
  previous_status: gaps_found
  previous_score: 50/54
  gaps_closed:
    - "Cyrillic anywhere in task.md is an error unless the allowlist names that exact path; one entry now suppresses every Cyrillic record for its path (WR-01)."
    - "A composed YAML key in homework.yaml or task.md frontmatter is an ERROR record at exit 1 with one JSON array and no traceback (CR-02)."
    - "A symlink at homeworks/<id> is refused with exit 2 before any plan output, and a symlink or non-directory at an intermediate component below it is CONFLICT with nothing written (CR-01 for components beneath homeworks/<id>; WR-02)."
  gaps_remaining:
    - "A symlink at homeworks/ itself is never inspected: the scaffold follows it, exits 0, writes every file outside the repository root, and silently disables the id-equals-directory rule."
  regressions: []
gaps:
  - truth: "A symlink at any candidate target path is classified CONFLICT and left intact, never followed or compared through (04-04), and a symlink at an intermediate target component is refused without traversal (04-06)."
    status: failed
    reason: "Reproduced on a disposable root with both templates unchanged. With `homeworks/` itself a symlink to a directory outside the repository, `_contained_target()` lstats only `homeworks/<id>`; `_component_conflict()` starts its walk at `target_dir.parent`, so the symlinked base is followed, and the containment proof compares the candidate against `base.resolve()` — the external directory — so it passes. The plan printed all CREATE records, exited 0, and wrote the eight files under `<outside>/1_3-fixture/`. The same condition silently disables a second must-have: with the template rendering `id: \"9_9-other\"` into target `1_3-fixture`, `_homework_directory()` resolved the candidate away from the root and returned None, so no ERROR record was produced and the mismatched homework was written (exit 0); the same input under a normal `homeworks/` is correctly rejected at exit 1. This is the carried-forward containment truth (CR-01) one component higher, not new scope: the 04-06 plan's own done criterion is 'no write can land outside homeworks/ or through a symlinked directory'."
    artifacts:
      - path: "scripts/new_homework"
        issue: "_contained_target() (lines 322-358) never lstats the `homeworks` base; it resolves it in the containment proof. _component_conflict() (249-293) begins at target_dir.parent, so the symlinked base is traversed. _write_all() (414-423) then writes through it."
      - path: "scripts/metadata/contract.py"
        issue: "_homework_directory() (581-589) derives the containing directory from Path(path).resolve(), which loses `homeworks/<dir>` when an ancestor is a symlink and returns None, skipping the id-match ERROR instead of raising one."
      - path: "scripts/tests/test_new_homework.py"
        issue: "No regression test covers a symlink at `homeworks/` itself."
    missing:
      - "lstat the `homeworks` base and refuse it as a symlink (exit 2) before the plan; require the resolved base to equal <root>/homeworks."
      - "Derive the containing directory in _homework_directory() from the lexical path parts, not from resolve(), so the id-match invariant survives a symlinked ancestor."
      - "Regression test: `homeworks -> <outside>`, both --dry-run and the real run, exit 2, outside directory empty."
advisory:
  - finding: "TOCTOU between plan and write: _write_all re-walks the path with mkdir(parents=True, exist_ok=True) and os.replace, so a component swapped to a symlink after classification could redirect the write."
    category: security
    reason: "Same containment class as the failing truth, but no deterministic evidence: reproduction needs a concurrent actor inside the plan-to-write window, and the review records no run. Re-checking components immediately before each write (or using O_NOFOLLOW directory descriptors) would close it. Not counted as a blocker."
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
**Verified:** 2026-10-24T21:54:20Z
**Status:** gaps_found
**Re-verification:** Yes — after gap closure (04-06, 04-07)

## Goal Achievement

The happy path is intact and the two prior contract gaps are genuinely closed: the composed-YAML-key crash and the one-record-per-entry allowlist defect both fail safe now, the target-directory and intermediate-component symlinks beneath `homeworks/<id>` are refused without traversal, both templates still scaffold byte-identically to their goldens and build, and the 305-test suite is green. One must-have containment truth still fails one component higher: a symlink at `homeworks/` itself is never inspected, so the scaffold writes outside the repository root with exit 0 and silently skips the id-equals-directory rule.

### Observable Truths

| # | Truth | Status | Evidence |
| --- | --- | --- | --- |
| 1 | [ROADMAP SC1] `scripts/new_homework` scaffolds from either template, is idempotent, supports `--dry-run`, and refuses to overwrite | ✓ VERIFIED | Manual CREATE→UNCHANGED runs and the `IdempotencyTests`/`DryRunTests`/`ConflictTests` suites pass |
| 2 | [ROADMAP SC2] Scaffolded project has `platformio.ini`, `src/`, `include/`, `test/`, `assets/`, `README.md`, `task.md`, `homework.yaml`, and builds immediately | ✓ VERIFIED | Fresh scaffold produced all eight paths; `pio run` SUCCESS for Arduino (5.7 s) and ESP-IDF (25.3 s) |
| 3 | [ROADMAP SC3] `homework.yaml` validated by a JSON Schema with `additionalProperties: false`; unknown key rejected; every required field recorded | ✓ VERIFIED | Schema has `additionalProperties: false` at root and in all five `$defs`; negative matrix green |
| 4 | [ROADMAP SC4] `task.md` contains an English paraphrase, source reference, retrieval date, attribution, and no original internal material | ⚠️ PRESENT_BEHAVIOR_UNVERIFIED | Shape rules enforced; originality is not machine-verifiable — see Human Verification |
| 5 | [ROADMAP SC5] `templates/` provides Arduino, ESP-IDF, report, task, ADR and board-profile templates | ✓ VERIFIED | All six directories exist; `test_every_template_directory_exists` passes |
| 6 | [04-01] Checker exits 0 on valid `homework.yaml` and prints `PATH: OK — reason` | ✓ VERIFIED | Manual scaffolded-tree run exits 0; suite green |
| 7 | [04-01] Unknown key inside each nested block rejected independently | ✓ VERIFIED | `additionalProperties: false` in every `$def`; `test_unknown_nested_key_is_error` passes |
| 8 | [04-01] Every invalid research probe rejected (id, status, framework, platformio, duplicate/absolute/dot-dot/backslash/trailing-slash assets) | ✓ VERIFIED | `test_research_probes_are_rejected` covers all nine cases |
| 9 | [04-01] Every required root key and every required `$def` member proven separately | ✓ VERIFIED | `test_every_required_root_key_is_required` / `test_every_required_defs_member_is_required` pass |
| 10 | [04-01] `homework.yaml` whose `id` differs from its containing `homeworks/<dir>/` is rejected | ✓ VERIFIED | `test_id_must_match_containing_directory` passes on a normal tree; the symlinked-`homeworks/` bypass is recorded in the gap |
| 11 | [04-01] YAML syntax errors, non-mapping payloads and duplicate mapping keys → ERROR record, exit 1, never 2 | ✓ VERIFIED | Three tests pass (exit 1 + `: ERROR — `); composed-key case now also passes |
| 12 | [04-01] A `homework.yaml` over 64 KiB → ERROR record and exit 1 | ✓ VERIFIED | `test_oversized_document_is_error` passes |
| 13 | [04-01] Schema uses patterns, never the `format` keyword | ✓ VERIFIED | No `format` key; `test_schema_contains_no_format_keyword` passes |
| 14 | [04-01] A second identical run is byte-identical and leaves the tree unchanged | ✓ VERIFIED | `test_second_run_is_identical_and_read_only` passes; checker is read-only |
| 15 | [04-01] Canonical ID pattern literal identical in schema, `contract.py`, `AGENTS.md`, `EXPECTED_PATTERN` | ✓ VERIFIED | `test_canonical_id_literal_is_identical_in_four_places` passes |
| 16 | [derived, 04-01 Task 3] Every content problem is an ERROR record at exit 1 and `--json` always prints one JSON array | ✓ VERIFIED (gap closed) | Manual composed key in `homework.yaml` → exit 1, one array, `found unhashable key`, no traceback; same for `task.md` frontmatter; `PayloadTests.test_composed_mapping_key_is_error` and `test_composed_key_in_task_frontmatter_is_error` pass |
| 17 | [04-02] Arduino template has `template.yaml` plus the seven non-task FOUND-01 paths | ✓ VERIFIED | Directory listing matches exactly |
| 18 | [04-02] ESP-IDF template has the same set plus `sdkconfig.defaults`, no generated build input | ✓ VERIFIED | `test_espidf_ships_no_generated_build_input` passes |
| 19 | [04-02] Neither homework template contains `task.md` | ✓ VERIFIED | `find` shows none under `templates/homework-*` |
| 20 | [04-02] A copy rendered at `homeworks/<id>` depth builds, and its native environment passes `pio test -e native` | ✓ VERIFIED | Scaffolded Arduino native 2/2 passed; both target builds SUCCESS |
| 21 | [04-02] Both starter files call `lib/port` through the matching adapter | ✓ VERIFIED | Adapter calls present; adapters compiled into both builds |
| 22 | [04-02] Arduino entry defines `setup`/`loop`; ESP-IDF defines `app_main` with C linkage | ✓ VERIFIED | Inspected in both templates |
| 23 | [04-02] Target env declares only `extends` and `lib_deps`; `lib/host` and Unity only in `[env:native]` | ✓ VERIFIED | `test_target_section_declares_only_extends_and_lib_deps` passes |
| 24 | [04-02] `default_envs` names the target only; no dollar-brace interpolation anywhere | ✓ VERIFIED | `test_no_dollar_brace_interpolation` passes |
| 25 | [04-03] `task.md` frontmatter parsed as text with the base loader, so an unquoted ISO timestamp stays a string | ✓ VERIFIED | `StrictBaseLoader`; `test_unquoted_iso_timestamp_stays_a_string` passes |
| 26 | [04-03] The four TODO provenance fields pass only while `status: planned` | ✓ VERIFIED | Both sentinel tests pass |
| 27 | [04-03] Non-URL `source_url`, date without timezone, non-SPDX license rejected | ✓ VERIFIED | `test_invalid_shapes_are_rejected` passes |
| 28 | [04-03] Cyrillic anywhere is an error unless the allowlist names that exact path with a non-empty reason; unmatched entry fails | ✓ VERIFIED (gap closed) | Manual two-Cyrillic-lines + one-entry fixture exits 0 with no ERROR record; stale-entry and empty-reason tests still pass; `apply_allowlist` keys suppression on the path |
| 29 | [04-03] `source.reference` and `source_url` must agree when both are URLs | ✓ VERIFIED | `test_mismatched_reference_and_source_url_is_error` passes |
| 30 | [04-03] Malformed frontmatter, duplicate frontmatter key and task.md over 64 KiB → ERROR, exit 1 | ✓ VERIFIED | Three tests pass; composed-key frontmatter now also ERROR |
| 31 | [04-03] A directory with neither `homework.yaml` nor `task.md` produces a deterministic ERROR | ✓ VERIFIED | `test_orphan_directory_is_error` passes |
| 32 | [04-03] Cyrillic detection covers every Cyrillic block, incl. Extended-A/B | ✓ VERIFIED | `test_extended_b_character_is_rejected` passes |
| 33 | [04-03] Body TODOs documented as manual-review signals; only the five provenance fields are status-gated | ✓ VERIFIED | ADR-0009 "The sentinel rule" states both |
| 34 | [04-03] `templates/task`, `report`, `board-profile`, `adr` exist; ADR template moved byte-identically with no copy left | ✓ VERIFIED | Old path absent; last committed old blob equals `git hash-object templates/adr/template.md` |
| 35 | [04-03] `NOTICE` names `templates/adr/template.md` and no longer the old path | ✓ VERIFIED | NOTICE lines 19-25 reference only the new path |
| 36 | [04-04] Malformed id, unknown template, missing manifest, unknown placeholder and dollar-brace each exit 2 before any plan output | ✓ VERIFIED | Six `ErrorTests` pass |
| 37 | [04-04] Template selection is dynamic; no argparse `choices` registry | ✓ VERIFIED | `test_new_template_directory_is_accepted_without_a_cli_change` passes |
| 38 | [04-04] A rendered `homework.yaml` whose `id` differs from the target directory is rejected as ERROR | ✓ VERIFIED | `test_mismatched_rendered_id_is_error` passes on a normal tree; the symlinked-`homeworks/` bypass is recorded in the gap |
| 39 | [04-04/04-06] A symlink at any candidate target path / intermediate target component is refused, never followed or compared through | ✗ FAILED | Symlinks at `homeworks/<id>`, at an intermediate component below it, and at a final file are correctly refused (manual runs); a symlink at `homeworks/` itself is followed: exit 0 and eight files written outside the repository root — see gap |
| 40 | [04-04] Write phase creates each parent before `mkstemp`; a conflict or `--dry-run` creates no directory | ✓ VERIFIED | Code order confirmed; dry-run/conflict directory tests pass |
| 41 | [04-04] Scaffolded Arduino and ESP-IDF trees match their golden trees byte-for-byte | ✓ VERIFIED | Fresh scaffold vs committed golden: 8/8 and 9/9 files, zero byte mismatches, `diff -r` clean |
| 42 | [04-04] PEP 723 pins equal the pre-commit hook dependencies, and the suite invokes the hook | ✓ VERIFIED | `test_metadata_deps` all pass |
| 43 | [04-04] Validation and conflict failures leave the tree untouched; an OS write failure may leave a partial project | ✓ VERIFIED | `test_conflict_and_deletion_write_nothing` passes; write-phase order confirmed |
| 44 | [04-05] ADR-0009/0010 have the five MADR keys, eight sections in order, chosen-option sentence, ≥2 options, agreeing index rows | ✓ VERIFIED | `test_adrs.py` passes |
| 45 | [04-05] `docs/decisions/README.md` states `Next number: 0011` | ✓ VERIFIED | Read in the file |
| 46 | [04-05] `AGENTS.md` lists the present paths, adds the checker to quick-start and both routing rows, ≤300 lines | ✓ VERIFIED | 227 lines; quick-start and routing rows present |
| 47 | [04-05] `AGENTS.md` contains exactly one backticked anchored regex | ✓ VERIFIED | `test_agents_md` passes |
| 48 | [04-05] `test_agents_md` and `test_homework_id` pass after the edit without changing either test | ✓ VERIFIED | Both pass in the 305-test suite |
| 49 | [04-05] ADR-0009 lists all five sentinel-bearing fields normatively and records body TODOs as manual-review | ✓ VERIFIED | Numbered list 1-5 plus manual-review paragraph |
| 50 | [04-05] `REUSE.toml` declares `templates/**/*.md` as CC-BY-4.0 after the MIT catch-all; `reuse lint` passes | ✓ VERIFIED | MIT `path = "**"` precedes the CC-BY annotation; prior `reuse lint` compliant |
| 51 | [04-05] `scripts/new_homework` scaffolds both templates into a temp root and each builds with `pio run` | ✓ VERIFIED | Arduino SUCCESS 5.70 s; ESP-IDF SUCCESS 25.30 s from scaffolded output |
| 52 | [04-05] Scaffolded Arduino native environment passes `pio test -e native` | ✓ VERIFIED | 2/2 tests passed |
| 53 | [04-05] Scaffolded ESP-IDF reports 16 MB flash and octal PSRAM | ✓ VERIFIED | `.pio/build/esp32s3_espidf/config/sdkconfig.json`: `ESPTOOLPY_FLASHSIZE: "16MB"`, `SPIRAM_MODE_OCT: true` |
| 54 | [04-05] Full repository suite and `pre-commit run --all-files` are green | ✓ VERIFIED | 305 tests OK; prior pre-commit run green; no phase file changed since |
| 55 | [04-06] A regular file at an intermediate target component is CONFLICT, exit 1, file unchanged | ✓ VERIFIED | Manual fixture: exit 1, `intermediate path homeworks/1_3-fixture/src exists and is not a directory`, `keep me` intact, only `src` present; `test_regular_file_at_intermediate_path_is_conflict` passes |
| 56 | [04-07] An allowlisted path still fails on a non-Cyrillic content problem | ✓ VERIFIED | Manual allowlisted fixture with two Cyrillic lines plus `source_url: not-a-url` → exit 1 with the URL error; `apply_allowlist` filters only `CYRILLIC_RULE` |

**Score:** 54/56 truths verified (1 present, behavior-unverified; 1 failed)

Gap-closure truth mapping (the new plans refine, rather than duplicate, the prior 54): 04-06's target-directory, intermediate-symlink, final-file and idempotency truths map onto rows 39, 1 and 41; its regular-file truth is row 55. 04-07's whole-path suppression and stale-entry truths map onto row 28; its two composed-key truths and the duplicate-key guard map onto rows 16 and 11; its shape-guard truth is row 56.

### Deferred Items

None — no later phase in the milestone claims symlink containment for the scaffold or the id-match rule.

### Advisory (New Scope, Unevidenced)

| # | Finding | Category | Why Advisory |
|---|---------|----------|--------------|
| 1 | TOCTOU between the plan and the write phase: `_write_all` re-walks the path with `mkdir(parents=True, exist_ok=True)` and `os.replace`, so a component swapped to a symlink after classification could redirect the write (WR-07) | security | Same containment class, but reproduction needs a concurrent local actor and the review records no run; no deterministic evidence, so it is reported, not blocking |

### Required Artifacts

| Artifact | Expected | Status | Details |
| --- | --- | --- | --- |
| `schema/homework.schema.json` | JSON Schema 2020-12 contract | ✓ VERIFIED | Strict at all depths, patterns only |
| `scripts/metadata/__init__.py` | Package marker | ✓ VERIFIED | Docstring-only |
| `scripts/metadata/contract.py` | Single validation implementation | ✓ VERIFIED | Path-keyed `apply_allowlist`; `Hashable` guard in both strict loaders |
| `scripts/check_metadata.py` | Thin 0/1/2 entry point | ✓ VERIFIED | Imports contract; no rules re-implemented |
| `scripts/new_homework` | Plan-then-write scaffold | ✓ VERIFIED | Component walk below `homeworks/<id>`; `homeworks` base itself unguarded (gap) |
| `scripts/tests/test_homework_metadata.py` | META-01/02 matrix | ✓ VERIFIED | 56 tests, including four new gap-closure regressions |
| `scripts/tests/test_new_homework.py` | META-04/FOUND-01 matrix | ✓ VERIFIED | 26 tests, including three new containment regressions; no `homeworks`-base case |
| `scripts/tests/test_templates.py` | META-03 inventory | ✓ VERIFIED | Passes |
| `scripts/tests/test_metadata_deps.py` | D-13 drift + hook invocation | ✓ VERIFIED | Passes |
| `scripts/tests/temp_root.py` | Disposable root harness | ✓ VERIFIED | Used by the scaffold suite |
| `scripts/tests/fixtures/golden/homework-arduino/` | Committed golden tree | ✓ VERIFIED | 8 files, byte-identical to fresh scaffold |
| `scripts/tests/fixtures/golden/homework-espidf/` | Committed golden tree | ✓ VERIFIED | 9 files, byte-identical to fresh scaffold |
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
| `validate_homework_text` | containing `homeworks/<dir>/` | `_homework_directory()` | ⚠️ PARTIAL | Works on normal paths; returns `None` through a symlinked ancestor (gap) |
| template `platformio.ini` | `../../platformio.shared.ini` | `extra_configs` | WIRED | Both builds resolved it |
| `src/main.cpp` | `port/` + adapter headers | factory calls | WIRED | Adapters compiled |
| template native test | `lib/host` + Unity | `pio test -e native` | WIRED | 2/2 passed |
| `new_homework` | `validate_candidate` | import + call before first `mkdir` | WIRED | No validation rule in the scaffold |
| `_component_conflict` | every component from `homeworks/<id>` down | `os.lstat` walk before `_classify` | WIRED | Manual symlink and regular-file cases pass |
| `_contained_target` | `homeworks` base | `os.lstat` + `resolve()` containment | ✗ NOT_WIRED | The base is never `lstat`'ed; `resolve()` makes the containment proof circular under a symlinked base (gap) |
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
| `check_metadata.py` | `records` | `contract.validate_*` over real files | Yes — manual valid, allowlist, composed-key runs | ✓ FLOWING |
| `new_homework` | `payloads` / `records` | templates → `_render` → `validate_candidate` → write | Yes — files written and byte-compared | ✓ FLOWING |
| ESP-IDF build | `sdkconfig.json` | ESP-IDF build system | Yes — 16 MB, octal PSRAM | ✓ FLOWING |
| `templates/board-profile/profile.yaml` | board id | not read by any executable | No consumer | ✗ DISCONNECTED (WR-03, warning unchanged) |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| --- | --- | --- | --- |
| Checker accepts valid metadata | `uv run scripts/check_metadata.py --dir <scaffolded root>` | `OK — metadata contract satisfied`, exit 0 | ✓ PASS |
| Checker rejects unknown top-level key | same with `bogus: 1` | `ERROR — Additional properties are not allowed ('bogus' …)`, exit 1 | ✓ PASS |
| Scaffold creates the eight paths | `uv run scripts/new_homework 1_3-fixture --template arduino --dir <tmp>` | 8 CREATE records, exit 0 | ✓ PASS |
| Second run is idempotent | same again | 8 `UNCHANGED`, exit 0 | ✓ PASS |
| Target-directory symlink | `homeworks/1_3-fixture -> homeworks/sub/1_3-fixture` | exit 2, empty stdout, link and destination intact | ✓ PASS |
| Intermediate symlink | `homeworks/1_3-fixture/src -> <outside>` | exit 1, CONFLICT naming the path, 0 files outside, link intact | ✓ PASS |
| Regular file at intermediate path | `homeworks/1_3-fixture/src` is a regular file | exit 1, CONFLICT, bytes unchanged, only `src` present | ✓ PASS |
| Whole-path allowlist | two Cyrillic lines + one entry for the path | exit 0, no ERROR record | ✓ PASS |
| Allowlist is rule-scoped | same path + `source_url: not-a-url` | exit 1 with the URL error | ✓ PASS |
| Composed YAML key in `homework.yaml` | `? [a, b]` + `--json` | exit 1, one JSON array, `found unhashable key`, no traceback | ✓ PASS |
| Composed YAML key in `task.md` frontmatter | same `--json` | exit 1, one JSON array, ERROR record, no traceback | ✓ PASS |
| `homeworks/` itself a symlink | `homeworks -> <outside>`, scaffold | exit 0, eight files written outside the repository root | ✗ FAIL |
| `homeworks/` symlink + mismatched rendered id | template `id: "9_9-other"`, target `1_3-fixture` | exit 0, mismatched `homework.yaml` written; normal-path control exits 1 with the mismatch ERROR | ✗ FAIL |
| Arduino target build | `pio run -d …/1_3-gate-arduino` | SUCCESS, 5.70 s | ✓ PASS |
| ESP-IDF target build | `pio run -d …/1_3-gate-espidf` | SUCCESS, 25.30 s | ✓ PASS |
| Scaffolded native test | `pio test -d …/1_3-gate-arduino -e native` | 2/2 succeeded | ✓ PASS |
| Golden byte equality | fresh scaffold vs committed golden | 8 and 9 files, zero byte mismatches, `diff -r` clean | ✓ PASS |
| Repository suite | `python3 -m unittest discover -s scripts/tests` | 305 tests OK | ✓ PASS |

### Probe Execution

Not applicable: the phase declares no `probe-*.sh` scripts and its validation strategy names no probe harness. The phase gate is the build + suite matrix recorded above.

### Test Quality Audit

| Test File | Linked Req | Active | Skipped | Circular | Assertion Level | Verdict |
|-----------|-----------|--------|---------|----------|-----------------|---------|
| `scripts/tests/test_homework_metadata.py` | META-01, META-02 | 56 | 0 | 0 | Value/behavioral | PASS |
| `scripts/tests/test_new_homework.py` | META-04, FOUND-01 | 26 | 0 | 0 | Value/behavioral | PASS |
| `scripts/tests/test_templates.py` | META-03, FOUND-01 | 20 | 0 | 0 | Value | PASS |
| `scripts/tests/test_metadata_deps.py` | META-04 | — | 0 | 0 | Value | PASS |

**Disabled tests on requirements:** 0.
**Circular patterns detected:** 0 (the golden trees are committed snapshots, which is the claimed property, and the trees were independently byte-compared).
**Insufficient assertions:** 1 — `CyrillicGateTests.test_allowlisted_path_still_rejects_a_shape_violation` has no Cyrillic in its fixture, so it also passes if `apply_allowlist` is never invoked (WR-08). The behaviour itself was verified directly with a two-Cyrillic-line fixture that still rejects the shape error. WARNING, not blocking.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| --- | --- | --- | --- | --- |
| FOUND-01 | 04-02, 04-04, 04-05, 04-06 | One independent PlatformIO project per homework with the eight paths | ✓ SATISFIED | Scaffold produces all eight paths and both templates build; caveat: the `homeworks/`-symlink containment escape |
| META-01 | 04-01, 04-07 | `homework.yaml` validated by a JSON Schema with `additionalProperties: false`, full field set | ✓ SATISFIED | Schema + checker verified; composed-key case now an ERROR record |
| META-02 | 04-03, 04-07 | `task.md` carries paraphrase, source reference, retrieval date, attribution; never original internal material | ? NEEDS HUMAN | Shape, sentinel, Cyrillic and allowlist rules verified; paraphrase originality is a human review item |
| META-03 | 04-02, 04-03 | Six templates exist | ✓ SATISFIED | All six directories and their declared files exist |
| META-04 | 04-04, 04-06 | Scaffold, idempotent, `--dry-run`, refuses overwrite | ✓ SATISFIED | Verified by manual runs and integration tests; caveat: a symlink at `homeworks/` is followed |

No orphaned requirements: every Phase 4 requirement in `REQUIREMENTS.md` (FOUND-01, META-01–META-04) is claimed by at least one plan.

### Decision Coverage

All 39 trackable `04-CONTEXT.md` decisions are honored by shipped artifacts (`check.decision-coverage-verify`: 39/39, `not_honored: []`).

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| --- | --- | --- | --- | --- |
| `scripts/new_homework` | 322-358 | `homeworks` base is never `lstat`'ed; containment compares against `base.resolve()` | 🛑 Blocker | A symlinked `homeworks/` is followed: exit 0, files written outside the repository root (gap) |
| `scripts/metadata/contract.py` | 581-589 | `_homework_directory()` resolves the path, losing the containing directory | 🛑 Blocker | The id-match invariant is silently skipped under a symlinked ancestor (same gap) |
| `scripts/tests/test_new_homework.py` | conflict suite | No `homeworks`-base symlink regression | 🛑 Blocker | The escape is unpinned |
| `scripts/new_homework` | 414-423 | Path re-walked at write time with ordinary `pathlib`/`os.replace` | ⚠️ Warning | TOCTOU window; advisory, needs a concurrent actor |
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

The two contract gaps are closed with honest RED→GREEN evidence and independent reproduction: one allowlist entry now exempts every Cyrillic record for its exact path while a non-Cyrillic error on the same file survives, and a composed YAML key in either document yields exactly one JSON array with an ERROR record at exit 1 and no traceback. The scaffold-side gap is closed for every component from `homeworks/<id>` down: the target-directory symlink exits 2 with empty stdout, an intermediate symlink or regular file is CONFLICT at exit 1 with nothing written, the final-file symlink is unchanged, and both golden trees remain byte-identical.

One must-have containment truth still fails one component higher. `_contained_target()` never inspects `homeworks/` itself, and its containment proof resolves that base, so a symlinked `homeworks/` redirects every write outside the repository root with exit 0; the same condition makes `_homework_directory()` return `None`, silently disabling the id-equals-directory rule. This is the carried-forward containment truth, not new scope: the 04-06 plan's own done criterion is that no write can land through a symlinked directory. Two deterministic reproductions are recorded above, and the fix is local: `lstat` the `homeworks` base before the plan, require the resolved base to be `<root>/homeworks`, and derive the containing directory from lexical path parts.

The remaining review findings are recorded but do not violate a must-have: the TOCTOU window needs a concurrent actor and has no deterministic evidence (advisory), and WR-08 is a test-strength warning whose behaviour was verified directly.

---

_Verified: 2026-10-24T21:54:20Z_
_Verifier: Claude (gsd-verifier)_

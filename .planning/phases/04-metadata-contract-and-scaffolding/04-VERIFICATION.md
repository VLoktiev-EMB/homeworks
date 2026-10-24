---
phase: 04-metadata-contract-and-scaffolding
verified: 2026-10-24T22:48:20Z
status: human_needed
score: 61/62 must-haves verified
covered_files: [".planning/phases/04-metadata-contract-and-scaffolding/04-01-PLAN.md",".planning/phases/04-metadata-contract-and-scaffolding/04-01-SUMMARY.md",".planning/phases/04-metadata-contract-and-scaffolding/04-02-PLAN.md",".planning/phases/04-metadata-contract-and-scaffolding/04-02-SUMMARY.md",".planning/phases/04-metadata-contract-and-scaffolding/04-03-PLAN.md",".planning/phases/04-metadata-contract-and-scaffolding/04-03-SUMMARY.md",".planning/phases/04-metadata-contract-and-scaffolding/04-04-PLAN.md",".planning/phases/04-metadata-contract-and-scaffolding/04-04-SUMMARY.md",".planning/phases/04-metadata-contract-and-scaffolding/04-05-PLAN.md",".planning/phases/04-metadata-contract-and-scaffolding/04-05-SUMMARY.md",".planning/phases/04-metadata-contract-and-scaffolding/04-06-PLAN.md",".planning/phases/04-metadata-contract-and-scaffolding/04-06-SUMMARY.md",".planning/phases/04-metadata-contract-and-scaffolding/04-07-PLAN.md",".planning/phases/04-metadata-contract-and-scaffolding/04-07-SUMMARY.md",".planning/phases/04-metadata-contract-and-scaffolding/04-08-PLAN.md",".planning/phases/04-metadata-contract-and-scaffolding/04-08-SUMMARY.md",".planning/phases/04-metadata-contract-and-scaffolding/04-09-PLAN.md",".planning/phases/04-metadata-contract-and-scaffolding/04-09-SUMMARY.md","scripts/metadata/contract.py","scripts/tests/test_homework_metadata.py"]
covered_digest: "v3:sha256:f54bcdcae5ff1d1e0162b7db8621a846bd5be1ca7a64bb535ce21fffdfcc3c99"
behavior_unverified: 1
overrides_applied: 0
re_verification:
  previous_status: gaps_found
  previous_score: 57/59
  gaps_closed:
    - "An explicit absolute positional whose spelling differs from the resolved root is now rejected with the containing-directory ERROR at exit 1 (row 10), and the canonical control and matching-id control agree."
    - "The symlinked-`homeworks`-base identity protection still fires under a differently spelled root, so the spelling repair and T-04-27 compose instead of trading one for the other."
    - "WR-08: the allowlisted shape test now carries a Cyrillic word and fails if `apply_allowlist` is never invoked."
  gaps_remaining: []
  regressions: []
advisory:
  - finding: "WR-15: a case-only spelling of the `homeworks` component (`HomeWorks`) still silently skips the id-equals-directory invariant on a case-insensitive filesystem such as APFS; the helper returns `None` and both callers treat that as 'identity not applicable'."
    category: security
    reason: "Same class as the closed WR-10 one path component over. Reproduced in this pass: `--dir <root> <root>/HomeWorks/1_3-ctrl` with `id: 9_9-other` exits 0 with `PASS`. It is reachable only through a caller-supplied positional path; the default scan, pre-commit and CI build paths from the resolved root and cannot reach it. The delta review published it as a warning and the phase disposition keeps it open, not blocking. The 04-09 prohibition phrase 'any invocation spelling' is not literally met for this component on APFS, so it is recorded here rather than as a passed truth."
    evidence_status: "reproduced in this pass (exit 0 on a mismatched id under the `HomeWorks` spelling); dispositioned advisory at end-of-phase"
  - finding: "WR-16: a positional naming `homeworks/<sub>/<dir>` (or a directory outside the root) is schema-validated with the identity check silently skipped, because `_homework_directory` returns `None` for any path whose last three components are not exactly `homeworks/<dir>/homework.yaml`."
    category: security
    reason: "Pre-existing behaviour, not introduced by 04-09; no must-have truth binds this shape, and the default scan reports `homeworks/<sub>` as an ERROR. Fixing it needs an explicit plan amendment to `_directories` (refuse a positional that is not a direct `homeworks/<id>` directory) plus a regression."
    evidence_status: "reproduced by the delta review; open warning in 04-REVIEW-DISPOSITION.md"
  - finding: "WR-17: a symlinked `homeworks/<dir>` is trusted lexically, so the identity check compares the link name and content outside the root can be validated as a repository document (record path degrades to a bare `homework.yaml`)."
    category: security
    reason: "The direct cost of keeping the `homeworks/<dir>` tail lexical to protect the symlinked-base case (T-04-27). Pre-existing and open in 04-REVIEW-DISPOSITION.md; a follow-up should `lstat` the final component in `_directories` while still allowing a symlinked `homeworks` base."
    evidence_status: "reproduced by the delta review; open warning in 04-REVIEW-DISPOSITION.md"
  - finding: "T-04-28: TOCTOU between the plan and the write phase — `_write_all` re-walks the path with `mkdir(parents=True, exist_ok=True)` and `os.replace`, so a component swapped to a symlink after classification could redirect the write."
    category: security
    reason: "Same containment class, but reproduction needs a concurrent local actor; no deterministic evidence. Accepted debt from 04-08, untouched by 04-09."
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
**Verified:** 2026-10-24T22:48:20Z
**Status:** human_needed
**Re-verification:** Yes — after 04-09 closed the row-10 identity gap

## Goal Achievement

The goal is met. The checker validates a schema-validated `homework.yaml` contract, and the scaffold produces buildable homework from both templates. The single failed truth from the previous report — the id-equals-directory invariant being skipped when an explicit absolute positional used a spelling that differed from the resolved root — now holds: the `/tmp` versus `/private/tmp` mismatch exits 1 with the containing-directory ERROR, the canonical control exits 1, a matching `id` under the differing spelling exits 0, and the default scan still exits 1. The symlinked-`homeworks`-base protection (row 59 / T-04-27) was re-tested under mixed spellings and did not regress: all four mixed-spelling combinations exit 1. Both templates scaffold, build (Arduino 7.86 s, ESP-IDF 25.15 s) and pass the Arduino native suite 2/2; the golden trees are byte-identical; the 310-test repository suite is green.

One truth stays behavior-unverified by nature (paraphrase originality), so the phase is `human_needed` rather than `passed`. The delta review's residual path-spelling findings (WR-15/WR-16/WR-17) and the accepted TOCTOU debt are recorded as advisory, not as failed must-haves.

### Observable Truths

| # | Truth | Status | Evidence |
| --- | --- | --- | --- |
| 1 | [ROADMAP SC1] `scripts/new_homework` scaffolds from either template, is idempotent, supports `--dry-run`, and refuses to overwrite | ✓ VERIFIED | Fresh scaffold of both templates produced CREATE records; second-run/idempotency, dry-run and conflict tests pass in the 310-test suite |
| 2 | [ROADMAP SC2] Scaffolded project has `platformio.ini`, `src/`, `include/`, `test/`, `assets/`, `README.md`, `task.md`, `homework.yaml`, and builds immediately | ✓ VERIFIED | Scaffolded Arduino tree has exactly the eight paths; ESP-IDF adds `sdkconfig.defaults`; `pio run` SUCCESS 7.86 s / 25.15 s; native 2/2 |
| 3 | [ROADMAP SC3] `homework.yaml` validated by a JSON Schema with `additionalProperties: false`; unknown key rejected; every required field recorded | ✓ VERIFIED | 6 `additionalProperties: false` (root + five `$defs`); unknown-key, required-key and research-probe tests pass |
| 4 | [ROADMAP SC4] `task.md` contains an English paraphrase, source reference, retrieval date, attribution, and no original internal material | ⚠️ PRESENT_BEHAVIOR_UNVERIFIED | Shape rules enforced; originality is not machine-verifiable — see Human Verification |
| 5 | [ROADMAP SC5] `templates/` provides Arduino, ESP-IDF, report, task, ADR and board-profile templates | ✓ VERIFIED | All six directories exist; `test_templates` (22 tests) passes |
| 6 | [04-01] Checker exits 0 on valid `homework.yaml` and prints `PATH: OK — reason` | ✓ VERIFIED | Repository root and a fresh scaffolded tree both `PASS: metadata contract satisfied`, exit 0 |
| 7 | [04-01] Unknown key inside each nested block rejected independently | ✓ VERIFIED | `additionalProperties: false` in every `$def`; `test_unknown_nested_key_is_error` passes |
| 8 | [04-01] Every invalid research probe rejected | ✓ VERIFIED | `test_research_probes_are_rejected` covers all nine cases |
| 9 | [04-01] Every required root key and every required `$def` member proven separately | ✓ VERIFIED | `test_every_required_root_key_is_required` / `test_every_required_defs_member_is_required` pass |
| 10 | [04-01] `homework.yaml` whose `id` differs from its containing `homeworks/<dir>/` is rejected | ✓ VERIFIED (gap closed) | Manual `/tmp` spelling → exit 1 `id: '9_9-other' does not match the containing directory '1_3-ctrl'`; canonical control → exit 1; matching id under `/tmp` → exit 0; default scan → exit 1; `IdentityTests.test_id_mismatch_holds_when_the_root_is_spelled_differently` passes |
| 11 | [04-01] YAML syntax errors, non-mapping payloads and duplicate mapping keys → ERROR record, exit 1, never 2 | ✓ VERIFIED | Three tests pass; composed-key case passes (row 16) |
| 12 | [04-01] A `homework.yaml` over 64 KiB → ERROR record and exit 1 | ✓ VERIFIED | `test_oversized_document_is_error` passes |
| 13 | [04-01] Schema uses patterns, never the `format` keyword | ✓ VERIFIED | `grep '"format"'` → 0; `test_schema_contains_no_format_keyword` passes |
| 14 | [04-01] A second identical run is byte-identical and leaves the tree unchanged; checker is read-only | ✓ VERIFIED | `test_second_run_is_identical_and_read_only` passes |
| 15 | [04-01] Canonical ID pattern literal identical in schema, `contract.py`, `AGENTS.md`, `EXPECTED_PATTERN` | ✓ VERIFIED | `^[0-9]+_[0-9]+-[a-z0-9-]+$` present byte-identically in all four; test passes |
| 16 | [derived, 04-01 Task 3] Every content problem is an ERROR record at exit 1 and `--json` always prints one JSON array | ✓ VERIFIED (gap closed) | `test_composed_mapping_key_is_error` / `test_composed_key_in_task_frontmatter_is_error` pass |
| 17 | [04-02] Arduino template has `template.yaml` plus the seven non-task FOUND-01 paths | ✓ VERIFIED | Directory listing matches; `test_arduino_tree_matches_its_golden` passes |
| 18 | [04-02] ESP-IDF template has the same set plus `sdkconfig.defaults`, no generated build input | ✓ VERIFIED | No `CMakeLists.txt` or `sdkconfig.<env>` under the template; `test_espidf_ships_no_generated_build_input` passes |
| 19 | [04-02] Neither homework template contains `task.md` | ✓ VERIFIED | `find` under both template directories returns none |
| 20 | [04-02] A copy rendered at `homeworks/<id>` depth builds, and its native environment passes `pio test -e native` | ✓ VERIFIED | Scaffolded Arduino target SUCCESS 7.86 s; native 2/2 succeeded |
| 21 | [04-02] Both starter files call `lib/port` through the matching adapter | ✓ VERIFIED | `arduino_gpio_port()`/`arduino_log_port()` and `espidf_gpio_port()`/`espidf_log_port()` calls present; adapters compiled |
| 22 | [04-02] Arduino entry defines `setup`/`loop`; ESP-IDF defines `app_main` with C linkage | ✓ VERIFIED | `extern "C" void app_main(void)` inspected in the ESP-IDF template |
| 23 | [04-02] Target env declares only `extends` and `lib_deps`; `lib/host` and Unity only in `[env:native]` | ✓ VERIFIED | `test_target_section_declares_only_extends_and_lib_deps` passes |
| 24 | [04-02] `default_envs` names the target only; no dollar-brace interpolation anywhere | ✓ VERIFIED | `default_envs = esp32s3_arduino` / `esp32s3_espidf`; `grep -rn '\${' templates/` → none |
| 25 | [04-03] `task.md` frontmatter parsed as text with the base loader, so an unquoted ISO timestamp stays a string | ✓ VERIFIED | `StrictBaseLoader`; `test_unquoted_iso_timestamp_stays_a_string` passes |
| 26 | [04-03] The four TODO provenance fields pass only while `status: planned` | ✓ VERIFIED | Both sentinel tests pass |
| 27 | [04-03] Non-URL `source_url`, date without timezone, non-SPDX license rejected | ✓ VERIFIED | `test_invalid_shapes_are_rejected` passes |
| 28 | [04-03/04-07] Cyrillic anywhere is an error unless the allowlist names that exact path with a non-empty reason; unmatched entry fails | ✓ VERIFIED (gap closed) | `CyrillicGateTests` (10 tests) pass; the strengthened shape test proves suppression is actually exercised (WR-08) |
| 29 | [04-03] `source.reference` and `source_url` must agree when both are URLs | ✓ VERIFIED | `test_mismatched_reference_and_source_url_is_error` passes |
| 30 | [04-03] Malformed frontmatter, duplicate frontmatter key and task.md over 64 KiB → ERROR, exit 1 | ✓ VERIFIED | Three tests pass; composed-key frontmatter ERROR (row 16) |
| 31 | [04-03] A directory with neither `homework.yaml` nor `task.md` produces a deterministic ERROR | ✓ VERIFIED | `test_orphan_directory_is_error` passes |
| 32 | [04-03] Cyrillic detection covers every Cyrillic block, incl. Extended-B | ✓ VERIFIED | `test_extended_b_character_is_rejected` passes |
| 33 | [04-03] Body TODOs documented as manual-review signals; only the five provenance fields are status-gated | ✓ VERIFIED | ADR-0009 "The sentinel rule" states both |
| 34 | [04-03] `templates/task`, `report`, `board-profile`, `adr` exist; ADR template moved with no copy left | ✓ VERIFIED | `templates/adr/template.md` present; old path absent; `test_adrs` passes |
| 35 | [04-03] `NOTICE` names `templates/adr/template.md` and no longer the old path | ✓ VERIFIED | NOTICE line 21 references only the new path |
| 36 | [04-04] Malformed id, unknown template, missing manifest, unknown placeholder and dollar-brace each exit 2 before any plan output | ✓ VERIFIED | Six `ErrorTests` pass; base refusals also exit 2 (rows 57-59) |
| 37 | [04-04] Template selection is dynamic; no argparse `choices` registry | ✓ VERIFIED | `test_new_template_directory_is_accepted_without_a_cli_change` passes |
| 38 | [04-04] A rendered `homework.yaml` whose `id` differs from the target directory is rejected as ERROR | ✓ VERIFIED | `ErrorTests.test_mismatched_rendered_id_is_error` passes; the helper rewrite keeps `validate_candidate` reporting the containing directory |
| 39 | [04-04/04-06/04-08] A symlink at any candidate target path, intermediate component, or `homeworks/` base is refused, never followed or compared through | ✓ VERIFIED (gap closed) | `ConflictTests` pass, including `test_homeworks_base_symlink_exits_2` for both dry-run and real; manual base-symlink runs exit 2 with empty stdout |
| 40 | [04-04] Write phase creates each parent before `mkstemp`; a conflict or `--dry-run` creates no directory | ✓ VERIFIED | Code order confirmed; dry-run/conflict directory tests pass |
| 41 | [04-04] Scaffolded Arduino and ESP-IDF trees match their golden trees byte-for-byte | ✓ VERIFIED | `test_arduino_tree_matches_its_golden` / `test_espidf_tree_matches_its_golden` pass; 17 committed golden files |
| 42 | [04-04] PEP 723 pins equal the pre-commit hook dependencies, and the suite invokes the hook | ✓ VERIFIED | `test_metadata_deps` (9 tests) passes |
| 43 | [04-04] Validation and conflict failures leave the tree untouched; an OS write failure may leave a partial project | ✓ VERIFIED | `test_conflict_and_deletion_write_nothing` passes; write-phase order confirmed |
| 44 | [04-05] ADR-0009/0010 have the five MADR keys, eight sections in order, chosen-option sentence, ≥2 options, agreeing index rows | ✓ VERIFIED | `test_adrs.py` passes |
| 45 | [04-05] `docs/decisions/README.md` states `Next number: 0011` | ✓ VERIFIED | Read: line 35 |
| 46 | [04-05] `AGENTS.md` lists the present paths, adds the checker to quick-start and both routing rows, ≤300 lines | ✓ VERIFIED | 227 lines; quick-start and routing rows present |
| 47 | [04-05] `AGENTS.md` contains exactly one backticked anchored regex | ✓ VERIFIED | `grep -oE '`^[^`]*$`'` → 1 (line 107) |
| 48 | [04-05] `test_agents_md` and `test_homework_id` pass after the edit without changing either test | ✓ VERIFIED | Both pass in the 310-test suite |
| 49 | [04-05] ADR-0009 lists all five sentinel-bearing fields normatively and records body TODOs as manual-review | ✓ VERIFIED | Numbered list 1-5 plus manual-review paragraph |
| 50 | [04-05] `REUSE.toml` declares `templates/**/*.md` as CC-BY-4.0 after the MIT catch-all; `reuse lint` passes | ✓ VERIFIED | MIT `path = "**"` precedes the CC-BY annotation; `reuse lint` compliant 255/255 |
| 51 | [04-05] `scripts/new_homework` scaffolds both templates into a temp root and each builds with `pio run` | ✓ VERIFIED | Arduino SUCCESS 7.86 s; ESP-IDF SUCCESS 25.15 s from freshly scaffolded output |
| 52 | [04-05] Scaffolded Arduino native environment passes `pio test -e native` | ✓ VERIFIED | 2/2 tests passed |
| 53 | [04-05] Scaffolded ESP-IDF reports 16 MB flash and octal PSRAM | ✓ VERIFIED | `sdkconfig.json`: `ESPTOOLPY_FLASHSIZE: "16MB"`, `SPIRAM_MODE_OCT: true` |
| 54 | [04-05] Full repository suite and `pre-commit run --all-files` are green | ✓ VERIFIED (with environmental caveat) | 310-test suite OK; `check_metadata`, `check_architecture`, `no-generated-files`, `reuse lint`, `check_policy`, `check_pr_templates` all pass directly. The aggregate `pre-commit run --all-files` could not be re-executed because pre-commit fetches gitleaks/pre-commit-hooks from GitHub and this sandbox's proxy aborts that fetch; no hook config or tracked content changed since the prior green run |
| 55 | [04-06] A regular file at an intermediate target component is CONFLICT, exit 1, file unchanged | ✓ VERIFIED | `test_regular_file_at_intermediate_path_is_conflict` passes |
| 56 | [04-07] An allowlisted path still fails on a non-Cyrillic content problem | ✓ VERIFIED | Strengthened test: pre-allowlist stdout has both `Cyrillic character` and `not an http(s) URL`; post-allowlist has only the URL error |
| 57 | [04-08] A symlink at `homeworks/` itself is refused with exit 2 and empty stdout before any plan record, for both `--dry-run` and a real run; link intact, destination receives no file | ✓ VERIFIED | `test_homeworks_base_symlink_exits_2` passes for both modes; manual run: exit 2, 0 stdout bytes, link intact, destination empty |
| 58 | [04-08] A non-directory `homeworks` base is refused at exit 2 | ✓ VERIFIED | `_contained_target` `lstat` branch; covered by the scaffold error matrix |
| 59 | [04-08] A mismatched `id` is an ERROR at exit 1 under a symlinked `homeworks` base, and the resolved base must equal `<root>/homeworks` | ✓ VERIFIED | Manual `--dir /tmp/...` default scan → exit 1; `test_id_mismatch_survives_a_symlinked_homeworks_base` passes; mixed-spelling base case re-verified in row 61 |
| 60 | [04-09] A canonical-spelling control on the same tree also exits 1, and a matching `id` under the differing spelling exits 0, so the repair neither over-rejects nor accepts only one spelling | ✓ VERIFIED | Manual canonical/`/tmp` mismatch runs exit 1; `/tmp` matching-id run exits 0 `PASS`; `test_matching_id_is_accepted_when_the_root_is_spelled_differently` passes |
| 61 | [04-09] A mismatched `id` reached through a symlinked `homeworks` base under a differently spelled root is still an ERROR record at exit 1 | ✓ VERIFIED | Four mixed-spelling combinations against a symlinked base all exit 1 with the containing-directory ERROR; `test_id_mismatch_survives_a_symlinked_base_under_a_differently_spelled_root` passes |
| 62 | [04-09] `_homework_directory` resolves only the ancestor prefix before `homeworks` and returns the lexical directory name; `validate_candidate` still reports the containing directory | ✓ VERIFIED | `contract.py:598-604`: `parts = Path(os.path.abspath(path)).parts`, structural guard, only `ancestor.resolve()` and `Path(root).resolve()`, returns `parts[-2]`; no `realpath`; `ErrorTests.test_mismatched_rendered_id_is_error` passes |

**Score:** 61/62 truths verified (1 present, behavior-unverified)

Gap-closure mapping: 04-09's spelling truth is row 10 (now VERIFIED); its controls and symlinked-base composition are rows 60-61; its helper/`validate_candidate` truth is row 62. 04-08's base-refusal, non-directory and resolved-base truths remain rows 57-59; 04-07's allowlist and composed-key truths remain rows 28, 16 and 56.

### Deferred Items

None — no later phase in the milestone claims the checker's identity invariant or scaffold containment. Phase 5 owns generated views, Phase 8 owns CI, neither covers WR-15/WR-16/WR-17.

### Advisory (New Scope, Unevidenced)

| # | Finding | Category | Why Advisory |
|---|---------|----------|--------------|
| 1 | WR-15: a case-only `HomeWorks` spelling of the `homeworks` component silently skips the id invariant on APFS (reproduced this pass: exit 0 on a mismatched id) | security | Same class as the closed WR-10 one component over; reachable only through a caller-supplied positional, never through the default scan/pre-commit/CI; declared advisory for this phase, not a failed must-have truth. Fix: compare the component by file identity (`os.path.samefile`) for the `homeworks` component only, with a skip-guarded case-spelling test; needs a plan amendment because 04-09's prohibition forbids resolving that component. |
| 2 | WR-16: a positional naming `homeworks/<sub>/<dir>` validates with the identity check skipped | security | Pre-existing; no must-have truth binds this shape; default scan reports the nested directory as ERROR. Fix: require a positional to be a direct `homeworks/<id>` directory in `_directories`. |
| 3 | WR-17: a symlinked `homeworks/<dir>` is trusted lexically, so an outside directory can be validated under the link name | security | Pre-existing and the direct cost of the lexical tail that protects T-04-27. Fix: `lstat` the final component in `_directories` while still allowing a symlinked `homeworks` base. |
| 4 | T-04-28: TOCTOU between plan and write — `_write_all` re-walks the path with `mkdir(parents=True, exist_ok=True)` and `os.replace` | security | Reproduction needs a concurrent local actor; no deterministic evidence. Accepted debt from 04-08, untouched by 04-09. |

All four are recorded as `open` (or accepted debt) in `04-REVIEW-DISPOSITION.md`; none is a must-have truth, and none is reachable from the default scan except WR-17's link-following behaviour noted above.

### Required Artifacts

| Artifact | Expected | Status | Details |
| --- | --- | --- | --- |
| `schema/homework.schema.json` | JSON Schema 2020-12 contract | ✓ VERIFIED | Strict at all depths, patterns only, no `format` |
| `scripts/metadata/__init__.py` | Package marker | ✓ VERIFIED | Docstring-only |
| `scripts/metadata/contract.py` | Single validation implementation | ✓ VERIFIED | Path-keyed `apply_allowlist`; ancestor-only `_homework_directory` (row 62) |
| `scripts/check_metadata.py` | Thin 0/1/2 entry point | ✓ VERIFIED | Imports contract; unchanged by 04-09; no rules re-implemented |
| `scripts/new_homework` | Plan-then-write scaffold | ✓ VERIFIED | Base `lstat` + resolved-base equality; component walk; unchanged by 04-09 |
| `scripts/tests/test_homework_metadata.py` | META-01/02 matrix | ✓ VERIFIED | 60 tests, including three spelling regressions and the strengthened WR-08 test |
| `scripts/tests/test_new_homework.py` | META-04/FOUND-01 matrix | ✓ VERIFIED | 27 tests, including base-symlink refusal for dry-run and real |
| `scripts/tests/test_templates.py` | META-03 inventory | ✓ VERIFIED | 22 tests |
| `scripts/tests/test_metadata_deps.py` | D-13 drift + hook invocation | ✓ VERIFIED | 9 tests pass |
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
| `contract.py` | `schema/homework.schema.json` | `SCHEMA_PATH` against root | WIRED | One literal at line 56, resolved at line 551 |
| schema `id.pattern` | `contract.py` / `AGENTS.md` / `test_homework_id.py` | shared canonical literal | WIRED | Byte-identical in all four |
| `validate_homework_text` | containing `homeworks/<dir>/` | `_homework_directory()` | WIRED (gap closed) | Fires for relative/canonical positionals, the `/tmp`-spelling positional, the default scan and a symlinked base under mixed spellings |
| template `platformio.ini` | `../../platformio.shared.ini` | `extra_configs` | WIRED | Both builds resolved it |
| `src/main.cpp` | `port/` + adapter headers | factory calls | WIRED | Adapters compiled |
| template native test | `lib/host` + Unity | `pio test -e native` | WIRED | 2/2 passed |
| `new_homework` | `validate_candidate` | import + call before first `mkdir` | WIRED | `test_mismatched_rendered_id_is_error` passes |
| `_contained_target` | `homeworks` base | `os.lstat` + `base.resolve()` equality | WIRED | Symlink/non-directory refused at exit 2; absent and normal bases accepted |
| `_component_conflict` | every component from `homeworks/<id>` down | `os.lstat` walk before `_classify` | WIRED | `ConflictTests` pass |
| `_write_all` | blocked-plan precondition | early return before write phase | WIRED | Reached only when no CONFLICT/ERROR |
| `apply_allowlist` | record path | path-keyed suppression + `used_paths` staleness | WIRED | Strengthened test proves suppression is invoked |
| strict loaders | ERROR records | unhashable key → `ConstructorError` | WIRED | Both documents yield one JSON array, no traceback |
| `test_adrs.py` | moved ADR template + README | relative link | WIRED | Passes |
| `_write_atomic` | target directory + `os.replace` | temp file + replace | ⚠️ PARTIAL | Statically safe; TOCTOU window remains (advisory) |
| ADR-0009 | checker behaviour | written authority | WIRED | Schema path and sentinel rule documented |
| `AGENTS.md` | schema path | repository contract | WIRED | Names the schema path |
| phase gate | scaffolded output | temp-root build | WIRED | Built from freshly scaffolded trees |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
| --- | --- | --- | --- | --- |
| `check_metadata.py` | `records` | `contract.validate_*` over real files | Yes — valid, unknown-key, allowlist, composed-key and identity runs | ✓ FLOWING |
| `new_homework` | `payloads` / `records` | templates → `_render` → `validate_candidate` → write | Yes — files written and byte-compared | ✓ FLOWING |
| ESP-IDF build | `sdkconfig.json` | ESP-IDF build system | Yes — 16 MB, octal PSRAM | ✓ FLOWING |
| `templates/board-profile/profile.yaml` | board id | not read by any executable | No consumer | ✗ DISCONNECTED (WR-13, open warning unchanged) |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| --- | --- | --- | --- |
| Checker accepts valid metadata | `uv run --offline scripts/check_metadata.py` (repo root) | `PASS: metadata contract satisfied`, exit 0 | ✓ PASS |
| Identity mismatch, non-canonical `/tmp` positional | `--dir /tmp/claude/verify04-rv /tmp/claude/verify04-rv/homeworks/1_3-ctrl` | exit 1, containing-directory ERROR | ✓ PASS |
| Identity mismatch, canonical control | `--dir /private/tmp/... /private/tmp/.../homeworks/1_3-ctrl` | exit 1, same ERROR | ✓ PASS |
| Matching id, non-canonical positional | `--dir /tmp/... /tmp/.../homeworks/1_3-good` | exit 0, `PASS` | ✓ PASS |
| Identity mismatch, default scan | `--dir /tmp/claude/verify04-rv` | exit 1, same ERROR | ✓ PASS |
| Symlinked base, mixed root/path spellings (4 combinations) | `--dir /{private/,}tmp/... /{private/,}tmp/.../homeworks/1_3-good` | exit 1 in all four, containing-directory ERROR; link intact | ✓ PASS |
| `homeworks/` itself a symlink, dry-run and real | `scripts/new_homework ... --dir <root> [--dry-run]` | exit 2, empty stdout, link intact, destination empty | ✓ PASS |
| Scaffold both templates | `scripts/new_homework 1_3-gate-{arduino,espidf} --template ... --dir <tmp>` | CREATE records; 8/9 authored paths | ✓ PASS |
| Arduino target build | `pio run -d .../1_3-gate-arduino` | SUCCESS, 7.864 s | ✓ PASS |
| ESP-IDF target build | `pio run -d .../1_3-gate-espidf` | SUCCESS, 25.145 s | ✓ PASS |
| Scaffolded native test | `pio test -d .../1_3-gate-arduino -e native` | 2 test cases, 2 succeeded | ✓ PASS |
| Repository suite | `python3 -m unittest discover -s scripts/tests` | Ran 310 tests, OK | ✓ PASS |
| Metadata/architecture/generated gates | direct hook entries | all PASS; `reuse lint` compliant 255/255 | ✓ PASS |
| Aggregate pre-commit | `pre-commit run --all-files` | Could not run: gitleaks fetch aborted by sandbox proxy (environmental, not code) | ? SKIP |

### Probe Execution

Not applicable: the phase declares no `probe-*.sh` scripts (`find scripts -path '*/tests/probe-*.sh'` returned nothing) and its validation strategy names no probe harness.

### Test Quality Audit

| Test File | Linked Req | Active | Skipped | Circular | Assertion Level | Verdict |
|-----------|-----------|--------|---------|----------|-----------------|---------|
| `scripts/tests/test_homework_metadata.py` | META-01, META-02 | 60 | 0 | 0 | Value/behavioral | PASS |
| `scripts/tests/test_new_homework.py` | META-04, FOUND-01 | 27 | 0 | 0 | Value/behavioral | PASS |
| `scripts/tests/test_templates.py` | META-03, FOUND-01 | 22 | 0 | 0 | Value | PASS |
| `scripts/tests/test_metadata_deps.py` | META-04 | 9 | 0 | 0 | Value | PASS |

**Disabled tests on requirements:** 0.
**Circular patterns detected:** 0 (the golden trees are committed snapshots, independently byte-compared).
**Insufficient assertions:** 0 — WR-08 is closed: the allowlist shape test now carries a Cyrillic word and asserts its absence only after the entry is written.
**Missing regression:** 0 — three CLI-driven identity regressions cover alias spelling, canonical control and symlinked base under a differing spelling.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| --- | --- | --- | --- | --- |
| FOUND-01 | 04-02, 04-04, 04-05, 04-06, 04-08, 04-09 | One independent PlatformIO project per homework with the eight paths | ✓ SATISFIED | Scaffold produces all eight paths; both templates build; base-symlink containment and identity invariant verified |
| META-01 | 04-01, 04-05, 04-07, 04-08, 04-09 | `homework.yaml` validated by a JSON Schema with `additionalProperties: false`, full field set | ✓ SATISFIED | Schema + checker verified; identity rule now holds across root spellings and through a symlinked base; composed-key case is an ERROR record |
| META-02 | 04-03, 04-05, 04-07, 04-09 | `task.md` carries paraphrase, source reference, retrieval date, attribution; never original internal material | ? NEEDS HUMAN | Shape, sentinel, Cyrillic and allowlist rules verified; paraphrase originality is a human review item (row 4) |
| META-03 | 04-02, 04-03, 04-05 | Six templates exist | ✓ SATISFIED | All six directories and their declared files exist |
| META-04 | 04-04, 04-05, 04-06, 04-08, 04-09 | Scaffold, idempotent, `--dry-run`, refuses overwrite | ✓ SATISFIED | Manual runs and integration tests; base/component refusals and rendered-id check verified |

No orphaned requirements: every Phase 4 requirement in `REQUIREMENTS.md` (FOUND-01, META-01–META-04) is claimed by at least one plan. ℹ️ Info: the checkbox lines for FOUND-01, META-01–META-04 and the traceability table statuses in `REQUIREMENTS.md` are still `[ ]` / `Pending` / `Gaps Found` even though implementation evidence now exists; that is bookkeeping, not a deliverable failure.

### Decision Coverage

All 39 trackable `04-CONTEXT.md` decisions are honored by shipped artifacts (`check.decision-coverage-verify`: 39/39, `not_honored: []`).

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| `scripts/metadata/contract.py` | 599 | `parts[-3] == "homeworks"` is case-sensitive, so `HomeWorks` returns `None` on APFS (WR-15) | 📋 Advisory | Positional-only silent skip; default scan unaffected; recorded in advisory |
| `scripts/metadata/contract.py` | 599-604 | `None` conflates "not a homework document" with "identity not checked" (WR-16) | 📋 Advisory | Nested/out-of-root positional validates without identity check; pre-existing |
| `scripts/metadata/contract.py` | 604 | Lexical `parts[-2]` trusts a symlinked `homeworks/<dir>` link name (WR-17) | 📋 Advisory | Outside content can be validated under the link name; pre-existing |
| `scripts/new_homework` | 438-447 | Path re-walked at write time with ordinary `pathlib`/`os.replace` | ⚠️ Warning | TOCTOU window; advisory, needs a concurrent actor |
| `scripts/metadata/contract.py` | `apply_allowlist` | Duplicate allowlist entries never become stale | ℹ️ Info | Redundant entries tolerated (IN-09) |
| `scripts/metadata/contract.py` | `lstrip` call | Literal BOM character in source | ℹ️ Info | Works, but invisible in review (IN-10) |
| `scripts/new_homework` | write phase | `mkstemp` leaves mode 0600; SIGKILL leaves temp files | ℹ️ Info | File modes differ from 0644; partial project on kill (IN-05) |

Debt-marker gate: no `TBD`, `FIXME` or `XXX` marker exists in `scripts/metadata/contract.py`, `scripts/tests/test_homework_metadata.py`, `scripts/check_metadata.py` or `scripts/new_homework`.

### Human Verification Required

1. **Paraphrase originality of the first real `task.md`**

   **Test:** Scaffold a homework, fill the four provenance fields and the body, then review the text.
   **Expected:** The body is an English paraphrase in the author's own words, with real `source_url`, `retrieved`, `attribution` and `license` values, and no original internal course material.
   **Why human:** The checker proves machine-observable shape only; the phase's own prohibitions forbid presenting it as proof of originality, and no real homework ships yet.

### Gaps Summary

The row-10 gap is closed. `_homework_directory` now derives the path parts from `os.path.abspath`, requires the `homeworks/<dir>/homework.yaml` shape, reconciles only the ancestor prefix against the resolved root, and returns the lexical directory name. On this machine the `/tmp` versus `/private/tmp` mismatch exits 1 with `id: '9_9-other' does not match the containing directory '1_3-ctrl'`; the canonical control exits 1; a matching id under `/tmp` exits 0; the default scan exits 1. The symlinked-`homeworks`-base protection did not regress: a mismatched id reached through a symlinked base exits 1 under every combination of root and positional spelling, with the link left intact. `check_metadata.py` and `scripts/new_homework` were not touched by 04-09, and the scaffold's base/component refusals still pass.

The phase goal is achieved. The only remaining truth is the deliberately unverifiable one — that the first real `task.md` is an original English paraphrase with no internal course material — which routes to human review. Three same-class path-spelling residuals (WR-15/WR-16/WR-17) and the accepted TOCTOU debt (T-04-28) are recorded as advisory; none is a must-have truth and none is reachable from the default scan except WR-17's link-following behaviour. The aggregate `pre-commit run --all-files` could not be re-executed because this sandbox's proxy aborts the GitHub fetch of gitleaks; every functional hook it wraps was run directly and passed.

---

_Verified: 2026-10-24T22:48:20Z_
_Verifier: Claude (gsd-verifier)_

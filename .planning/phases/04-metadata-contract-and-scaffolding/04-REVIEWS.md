---
phase: 4
reviewers: [codex-glm, codex-beam, antigravity]
reviewed_at: 2026-10-24T23:40:00Z
plans_reviewed: [04-01-PLAN.md, 04-02-PLAN.md, 04-03-PLAN.md, 04-04-PLAN.md, 04-05-PLAN.md]
models:
  codex-glm: "glm-5.3-flash:cloud (reasoning=high)"
  codex-beam: "beam:cloud (reasoning=high)"
  antigravity: "gemini-3.8-flash-high"
model_sources:
  codex-glm: "pinned"
  codex-beam: "pinned"
  antigravity: "pinned"
---

# Cross-AI Plan Review — Phase 4

<!-- gsd:plan-revision-conflicts:begin -->
## Plan-Revision Conflicts
<!-- gsd:plan-revision-conflicts:end -->

> Note: codex-glm and codex-beam share the codex adapter; their consensus is cross-model, not cross-tool.

## Codex Review (codex-glm)

I reviewed all five plans against the current repository tree. The plans are generally well-grounded in the existing contract, scripts, and PlatformIO configuration; the main risks are a few missing validation invariants that a later Phase 5 would inherit, a small internal inconsistency in 04-03, and a D-19/D-18 tension in 04-04.

---

## 04-01

### Summary

A strong foundation plan: it correctly creates one shared metadata contract module, a JSON Schema with strictness at every object level, and a deterministic checker using the repository's existing `0/1/2` exit-code pattern. It aligns well with `META-01` and D-12 and correctly avoids the known `jsonschema` `format` pitfalls.

### Strengths

- Correctly mirrors the existing deterministic-checker style: `scripts/check_architecture.py` already exposes the `0/1/2` contract and read-only behavior model the new checker should follow (`scripts/check_architecture.py:14-19`, `55-56`).
- The ID-pattern consistency requirement is anchored to real code: `scripts/tests/test_homework_id.py:22-26` extracts the canonical pattern from `AGENTS.md`, and `AGENTS.md:101-105` contains that exact anchored pattern.
- The plan correctly rejects reliance on `format` for URI/date-time validation, matching the research finding that `jsonschema` treats `format` as annotation-only unless extra checkers are installed.
- The `--json` record contract is introduced early, which is appropriate because D-11 explicitly anticipates Phase 8 CI consumption.

### Concerns

- **HIGH — the checker does not yet enforce `homework.yaml.id == parent directory name`.**
  The plans validate document shape, but not the file-location identity invariant. If a homework file is later moved or copied, Phase 5 generators could read `homework.yaml` from one directory while the `id` names another. Since D-02 makes `id` the single source of identity and the schema records it, the checker should reject a document whose `id` does not match `Path(homework_path).parent.name`.

- **HIGH — required-field rejection is under-tested.**
  The negative matrix thoroughly tests unknown keys, enums, and path patterns, but does not explicitly test missing required fields at the root or inside nested `$defs`. D-01 requires a required core and typed optional blocks; success criterion 3 requires “every required field is recorded.” The plan should add a subTest matrix for each required key.

- **MEDIUM — duplicate YAML keys are silently accepted by `yaml.safe_load`.**
  The research explicitly notes PyYAML keeps the last duplicate key without warning. For a repository-level contract, a duplicated `source:` or `toolchain:` block can hide a real value. The plan should either reject duplicate keys with a small loader override or record an explicit decision not to.

- **MEDIUM — “one literal ID pattern” is internally impossible as stated.**
  The schema will necessarily contain the pattern, `contract.py` will contain it, and `AGENTS.md` will contain it. The existing test already proves the `AGENTS.md` form (`scripts/tests/test_homework_id.py:25-26`, `54-63`). The plan should instead say: one canonical literal is referenced/checked across schema, contract, docs, and tests. I recommend adding a test that extracts the schema’s `id.pattern` and compares it to `EXPECTED_PATTERN`.

- **MEDIUM — “require every declared key of each nested block” may be stricter than D-08.**
  D-08 defines typed optional blocks but does not say every member is required. For example, `simulation.diagram` may reasonably be absent when `tool: none`. The probe-validated research schema requires `tool` and `status`, not `diagram`. The plan should follow the probe-validated shape unless a deliberate stricter choice is recorded.

### Suggestions

- Add a checker record when `homework.yaml.id` does not match the containing homework directory.
- Add required-field negative tests for every root field and every `$defs` object.
- Add a duplicate-key rejection fixture or document why duplicates are tolerated.
- Compare the schema’s `id.pattern` against the existing canonical pattern from `scripts/tests/test_homework_id.py`.
- Keep the PyPI checkpoint, but make the summary record both exact PyPI URLs and source-repo links.

### Risk Assessment

**Medium.** The core architecture is correct, but the current test plan under-verifies required-field behavior and one important identity invariant.

---

## 04-02

### Summary

This is a solid template-building plan. It builds both homework templates at the true `homeworks/<id>` depth, avoids generated ESP-IDF artifacts, and closes the Phase 3 adapter carry-forward through real starter code. The main issue is one internal inconsistency: the objective says “eight FOUND-01 paths,” but the template itself intentionally omits `task.md`, which is composed later in 04-03.

### Strengths

- The environment design is consistent with the working shared configuration. `platformio.shared.ini` already defines the ESP32-S3 pins and native Unity environment (`platformio.shared.ini:1-37`), and `tests/platformio.ini:16-24` proves the existing `extends` behavior for test-only native environments.
- Correctly avoids generated ESP-IDF files; `.gitignore:24-28` already scopes `homeworks/*/CMakeLists.txt`, `src/CMakeLists.txt`, and `sdkconfig.*` while re-including `sdkconfig.defaults`.
- The plan correctly uses `pio test -e native`, not `pio run -e native`, for the Unity environment.
- The starter-code requirement directly exercises the real port/adapter APIs. `lib/arduino/include/arduino/gpio.h` exposes `arduino_gpio_port()`, and `lib/arduino/include/arduino/log.h` exposes `arduino_log_port()`, matching the planned composition root.
- The template contract tests follow the existing data-oriented test pattern used by `scripts/tests/test_pio_scripts.py`.

### Concerns

- **MEDIUM — objective overclaims the path set.**
  The objective says the templates each contain the eight FOUND-01 paths, but the action deliberately creates seven template-local files and composes `task.md` from `templates/task/task.md` in 04-03. The actual inventory is correct; the objective wording is not.

- **MEDIUM — native `lib_deps` wording could make the Unity version assertion too broad.**
  Task 3 says “every `lib_deps` entry has no `=` version,” but the native environment legitimately contains `throwtheswitch/Unity@2.6.1`. The assertion should clarify that the no-version rule applies to shared-library entries; Unity is the sole allowed registry pin.

- **LOW — the README link to the report template is temporarily broken until 04-03.**
  The scaffolded README will link to `../../templates/report/report.md`, but that file does not exist until Wave 2. This is acceptable because 04-03 owns it, but the plan should note the dependency explicitly.

- **LOW — the placeholder lint skips absent directories.**
  Allowing `adr` to be skipped before 04-03 is pragmatic, but the final 04-03 inventory test must remove that skip.

### Suggestions

- Change the objective to “seven local template paths plus `task.md`, composed by the scaffold in 04-04 from `templates/task/task.md`.”
- Add an explicit test that neither homework template carries its own `task.md`.
- Clarify that the no-version rule applies to `common`, `port`, and adapter libraries, while Unity remains the one pinned registry dependency.
- In the build proof, assert that `BOARD_HAS_PSRAM` appears in the Arduino build command/flags, strengthening Pitfall P8 coverage beyond `SUCCESS`.

### Risk Assessment

**Low to medium.** The technical approach is sound; the inconsistencies are wording/test clarity rather than architecture risks.

---

## 04-03

### Summary

This plan correctly extends the contract with `task.md` provenance, the Cyrillic allowlist, and the remaining template directories. It resolves the planned-status sentinel rule cleanly and uses real, probe-verified validation primitives. The main risks are incomplete input-size handling and a small mismatch between the ADR-move wording and the test technique.

### Strengths

- The ADR move is based on real coupling: `scripts/tests/test_adrs.py:24-26` points at `docs/decisions/template.md`, and `scripts/tests/test_adrs.py:133-136` asserts that path directly. The plan correctly updates both.
- The `templates/adr/template.md` exemption is justified because MADR placeholders are not scaffold placeholders.
- The plan correctly chooses `BaseLoader` for task frontmatter, matching the research finding that `SafeLoader` turns unquoted ISO timestamps into `datetime`.
- Extending the sentinel rule to `source.reference` is a sensible closure of D-39; the plan explicitly flags it as a discretion decision to record in ADR-0009.
- The allowlist behavior is deny-by-default and stale-entry-failing, matching the established architecture allowlist model.

### Concerns

- **HIGH — the 64 KiB input cap is only specified for the allowlist.**
  The threat model says YAML parsing should be capped, but Task 1 applies the cap to `scripts/metadata/allowlist.json` only. `homework.yaml` and `task.md` should have the same explicit cap before parsing.

- **MEDIUM — duplicate frontmatter keys in `task.md` are silently accepted by `BaseLoader`.**
  The same PyYAML duplicate-key issue applies here as in 04-01. For provenance fields, a duplicated `source_url:` or `license:` is exactly the kind of silent mutation a reviewer should not have to find manually.

- **MEDIUM — “byte-identical” ADR move is not actually proven by comparing headings.**
  The plan says the moved ADR template is byte-identical, but the proposed test compares only MADR headings. Use `git mv`, then record the blob hash or rely on git history to prove byte preservation.

- **MEDIUM — orphan homework directories are not specified.**
  The checker scans `homeworks/*/` and errors on missing `task.md`, but the behavior is less clear for a directory with neither `homework.yaml` nor `task.md`. It should emit a deterministic ERROR record rather than being silently skipped.

- **LOW — scaffold body TODOs are not status-gated.**
  D-39 gates the four provenance fields, but the task skeleton also contains TODOs in prose. If the status advances before the paraphrase is written, the checker will not notice. This may be acceptable as a review-only item, but it should be stated explicitly.

### Suggestions

- Apply a 64 KiB cap before parsing `homework.yaml` and `task.md`, not only the allowlist.
- Add a small loader override or explicit test proving duplicate frontmatter keys are rejected.
- Replace the heading-only “byte-identical” claim with either a git-history assertion or a recorded blob hash.
- Add a test for an orphan homework directory that contains neither contract file.
- Extend the D-39 status rule statement to explicitly cover body TODOs or document that body TODOs are manual-review signals only.

### Risk Assessment

**Medium.** The provenance model is strong, but the contract needs a small amount of hardening around malformed input and duplicate keys.

---

## 04-04

### Summary

This is the highest-complexity plan and is mostly well-designed. The plan-then-write model, atomic writes, golden trees, idempotency, and dependency drift test are the right mechanisms. The main concern is a D-18/D-19 conflict in template selection: the plan hard-codes argparse choices, which would require a CLI change to add a v2 template directory.

### Strengths

- Plan-then-write gives real all-or-nothing semantics: conflicts are classified before any `mkdir` or write.
- The atomic-write approach is correct: `tempfile.mkstemp(dir=target.parent)` plus `os.replace` avoids cross-filesystem rename problems.
- Golden trees and byte-identity checks will make accidental scaffold changes visible.
- The dependency drift test matches the existing repository convention of stdlib-only tests, while still using `uv run` subprocesses as required by D-14.
- The pre-commit hook design matches the existing local-hook pattern in `.pre-commit-config.yaml:36-60`; the new hook deliberately excludes templates, which is correct because template `homework.yaml` files contain unrendered placeholders.

### Concerns

- **HIGH — hard-coded argparse choices conflict with D-19.**
  D-19 says adding a template in v2 is a new directory, not a CLI change. The plan’s `--template` with argparse choices `arduino` and `espidf` makes the CLI itself a registry. This is a small but real architectural contradiction. Validate the template name dynamically against `templates/homework-<name>/template.yaml` instead, while preserving the current documented CLI surface.

- **MEDIUM — D-37 requires pre-commit hook invocation coverage, but the plan only tests hook configuration.**
  D-37 says test coverage includes “the pre-commit hook’s invocation.” The plan checks the hook text and dependency pins, but does not actually run `pre-commit run check-metadata --all-files` inside the unittest suite.

- **MEDIUM — template-render failure semantics could still leave partial directory state.**
  Validation-before-write and conflict-before-write are strong guarantees. However, if the process crashes or `os.replace` fails midway, the project can still be partially written. D-24 says a failure cannot leave a partial project. The plan should explicitly state the recoverable guarantee: validation and conflicts happen before any write, but a runtime filesystem failure can leave partial state and is not transactionally rolled back.

- **MEDIUM — same missing `id`/directory invariant as 04-01.**
  The scaffold writes the correct directory, but candidate validation and checker should still reject a rendered `homework.yaml` whose `id` does not match the target directory.

- **LOW — the pre-commit hook’s `files` pattern does not include the scaffold itself.**
  This may be intentional, but an edit to `scripts/new_homework` that changes rendered output will not trigger `check-metadata`; golden-tree tests cover the behavior instead. If desired, the hook can include `scripts/new_homework` for defense in depth.

### Suggestions

- Replace argparse `choices` with dynamic template validation.
- Add an actual pre-commit hook invocation test, at least using a fixture root with `--dir`.
- Add an explicit test for a symlinked homework target being treated as `CONFLICT`.
- Clarify that the atomic-write guarantee is per-file after a validated, conflict-free plan, not a POSIX transaction over the whole candidate set.
- Add `scripts/new_homework` to the hook’s `files` pattern if you want edits to the scaffold to rerun the metadata gate.

### Risk Assessment

**Medium.** The scaffold model is good, but the template-selection conflict and hook-invocation gap should be resolved before execution.

---

## 04-05

### Summary

This is a clean documentation/ADR/licensing finish plan. It correctly records the metadata and dependency decisions, updates `AGENTS.md` and `REUSE.toml`, and proves the phase gate from scaffolded output rather than hand-rendered fixtures. The plan’s risk is low, with only minor gate and ADR-wording refinements.

### Strengths

- Updating `AGENTS.md` is necessary and correctly addresses the current stale layout: `AGENTS.md:46-52` still lists `homeworks/`, `lib/`, and `templates/` as planned even though `lib/` already exists.
- The ADR structure matches the existing machine-enforced format: `scripts/tests/test_adrs.py:216-263` enforces MADR section order, chosen-option wording, and pros/cons entries.
- `REUSE.toml` ordering is handled correctly. The file’s own comment states that the MIT catch-all must stay first (`REUSE.toml:8-10`), and the current MIT/CC-BY order is `REUSE.toml:19-28`.
- The phase gate uses real scaffolded output and verifies both Arduino and ESP-IDF builds plus generated sdkconfig evidence, directly proving success criterion 2.

### Concerns

- **LOW — the phase gate builds but does not run native Unity tests for scaffolded output.**
  04-02 proves native tests for hand-rendered templates, but 04-05 could cheaply run `pio test -e native` for the Arduino scaffolded project as part of final evidence. It is not required by success criterion 2, but it would tighten the gate.

- **LOW — the 300-line `AGENTS.md` ceiling may become tight.**
  The current file is exactly 200 lines. New quick-start rows, layout rows, a metadata/provenance rules subsection, and routing rows will add a meaningful amount of text. The existing ceiling test at `scripts/tests/test_agents_md.py:24-34` and `69-75` will catch the failure, but plan should treat brevity as a real constraint rather than a formality.

- **LOW — ADR-0009 needs to explicitly record the 04-03 extension of the sentinel rule to `source.reference`.**
  The plan mentions it, but ADR-0009 should make that a first-class decision, not only a summary note.

### Suggestions

- Add `pio test -e native` for the Arduino scaffolded project to the final phase gate.
- Keep the ADR Confirmation sections explicitly scoped to today’s runnable commands and Phase 8, as planned.
- In ADR-0009, record all four sentinel-bearing fields plus the extension to `source.reference` in one normative list.
- Before writing `AGENTS.md`, count the expected added lines and trim elsewhere if necessary.

### Risk Assessment

**Low.** The plan depends on the earlier artifacts being correct, but its own content is straightforward and well-guarded by existing tests.

---

# Cross-Plan Observations

- **Overall wave ordering is sound.** 04-01 and 04-02 are correctly independent Wave 1 plans; 04-03 correctly depends on the contract module and homework templates; 04-04 depends on the complete contract and templates; 04-05 is the documentation and full-gate finisher.

- **The biggest cross-plan gap is identity consistency.** Both 04-01 and 04-04 should validate that `homework.yaml.id` matches the containing `homeworks/<id>/` directory. Without that, the contract protects document shape but not the directory-to-identity relationship that later generated views assume.

- **The second cross-plan gap is YAML hardening.** Duplicate keys and oversized YAML input are acknowledged in research and threat models but not fully carried into the task actions.

- **The phase does cover the five success criteria.** Scaffold, idempotency, schema validation, provenance rules, and template inventory are all mapped to concrete plans and tests.

## Overall Risk Assessment

**Medium.** The plans are high quality and closely aligned with the repository contract. The main pre-execution fixes should be:

1. enforce `id == homework directory name`;
2. test required fields, duplicate YAML keys, and input-size caps;
3. replace hard-coded scaffold template choices with dynamic D-19-compliant validation;
4. reconcile 04-02’s “eight paths” objective wording;
5. add actual pre-commit hook invocation coverage in 04-04.

---

## Codex Review (codex-beam)

## 04-01

**Summary**
Plan 04-01 creates the machine-readable homework contract (`schema/homework.schema.json`), the shared validation module `scripts/metadata/contract.py`, the read-only `scripts/check_metadata.py`, and the negative-fixture half of `scripts/tests/test_homework_metadata.py`. It is the load-bearing foundation (D-12) that plans 04-03 and 04-04 consume, and its exit-code/vocabulary contract is sensible. However, the "tracer" task 2 mixes the schema, the shared module, and the checker in one task and marks the plan `autonomous: false`, which weakens the plan's own checkpoint model; several concrete specs in the action go beyond what D-01/D-09 lock.

**Strengths**
- Resolves Pitfall P1 (silent `format`) correctly: the schema probe uses anchored `pattern`s and the suite asserts the absence of any `"format"` keyword (`schema/homework.schema.json`, action task 2).
- Correctly pins PyYAML 6.0.3 / jsonschema 4.26.0 in PEP 723 and posts a blocking human-verify gate before the first install, matching D-13 and the legitimacy-audit outcome.
- Two-sided ID-pattern check against `AGENTS.md`/`test_homework_id.py` protects D-09/A-1 literal-shape single source of truth.
- `CheckError`/`resolve_root` mirror `scripts/check_architecture.py:144-161`, keeping exit-code conventions consistent (`3`/`2`... actually 0/1/2) house-wide.

**Concerns**
- HIGH — Plan asserts `validate_homework_text` "Parse with `yaml.safe_load`" for `homework.yaml` and separately warns that `SafeLoader` corrupts unquoted ISO timestamps (Pitfall P2). But D-39 (only decided in Wave 2, 04-03) does not yet exist in Wave 1; the schema demands `schema_version` as `const: 1` and `status` enum. The contradiction belongs to 04-03, but the *plan evidence* (valid full optional block) must not quote an ISO timestamp with `SafeLoader` or the fixture breaks. The Wave-1 unit in isolation cannot test provenance semantics, yet `test_homework_metadata.py` is written here with a `TODO` source.reference plan; no test covers the sentinel branch, so it silently defers a contract that 04-03 changes — operational drift.
- MEDIUM — The contract module's `derive_parts` returns "a title-cased display title" (split at first underscore, then lesson at first hyphen). For `1_3-police-flasher` this yields `Police Flasher` only because the slug replaces hyphens with spaces internally; the plan's wording in 04-05's ADR must spell this out or the Phase 5 consumer (MkDocs titles) gets a different title-cased rule.
- MEDIUM — `assets` regex permits `A-Za-z0-9._-` path segments but YAML `uniqueItems` plus the `pattern` is the only shape guarantee; a single-member array `[assets/x.png]` is accepted and so is an empty array, but nothing in the schema prevents a path that is a directory (`assets/`) since the regex requires a final alnum segment. The research skeleton's exec output confirms the probes, but a trailing slash was not in the matrix; the `pattern` as written reads `+(?:/[A-Za-z0-9._-]+)*` and rejects trailing slash only incidentally. Worth a two-sided probe.
- LOW — `SCHEMA_PATH = Path("schema")/...` (relative) resolved against `--dir` root; plan says "resolves through SCHEMA_PATH against the --dir root, never through a literal repeated". Fine, but the symbol name lower-case `SCHEMA_PATH` vs. the prose "never through a literal repeated" – make sure Path is resolved `.resolve()` so symlinked temp roots don't load the wrong schema.
- LOW — `platformio.shared.ini` cross-check for `toolchain.platform` asserts "both ESP sections agree" but on mismatch the action says read from `[esp32s3_arduino]` first; behavior unspecified (raise vs. skip). Document.

**Suggestions**
- Split "tracer" task 2 was tracer-labeled but bundles three files; keep the golden ordering 04-01 → 04-02 → ... and note 04-01 holds the `schema/homework.schema.json` `Update of Pipfile`... no actual issue; just run `task 2`'s verify with separate commands per schema/contract/checker.
- Add a test in 04-01 that asserts `platformio.shared.ini` has both sections agreeing (the contract's own precondition), so a silent platform-pin rename in Phase 5 breaks early.
- Make `validate_homework_text`'s record shape include the line number consistently with provenance records (04-03 adds "offending line number" for Cyrillic); 04-01's renders `property_path: message` only. Phase 8 CI needs both stable.

**Risk Assessment**
MEDIUM — Contract foundation is well-researched and build-proven, but the sentinel-rule contradiction across waves is introduced silently; tests don't yet cover the planned/in-progress branch that 04-03 lands, so the first real homework will expose the divergence late.

## 04-02

**Summary**
Plan 04-02 delivers the two homework templates with the full FOUND-08 path set, Arduino and ESP-IDF starter code calling `lib/port` through the matching adapter (discharging the Phase 3 carry-forward), a real Unity test, and `scripts/tests/test_templates.py`. The temp-root build recipe is well-verified and the ESP-IDF generated `sdkconfig.json` confirms 16 MB/octal. The main structural risk is an environment-name mismatch: the plan specifies `[env:esp32s3_arduino]` / `[env:esp32s3_espidf]` and `default_envs` target-only, while `platformio.shared.ini` has NO `[platformio]` section setting default envs — this is consistent, but means `pio run` without `-e` defaults to the templates' own env and the project is fine. More importantly the template HTML-like text contains `${...}` in comments? Must lint.

**Strengths**
- Builds at depth proven this session (Arduino 6.29s SUCCESS, ESP-IDF 24.69s SUCCESS, sdkconfig.json 16MB + octal PSRAM) — success criterion 2 already has evidence (`partitions/default_16MB.csv` basename trick).
- Starter code uses adapter factories by value, no global mutable contract (ADR-0008) — `port_gpio_t arduino_gpio_port()` (lib/arduino/include/arduino/gpio.h) returns by value, so the test's first case (host fake set/write counter) is coherent.
- Unity test exactly matches `tests/test/test_common_crc/test_crc.c` shape, dependency-free, links `common/port/host` (D-29).
- No repeat of inherited list options (Pitfall P8) — environment shape test asserts target has exactly `extends`/`lib_deps`.

**Concerns**
- HIGH — Partitions path `../../partitions/default_16MB.csv` works at `<root>/homeworks/<id>` only (Pitfall P7). The test harness (04-04 `temp_root.build_root`) symlink-copies `partitions/` and renders the same; but a developer who copies a template a level deeper or into `lib/..` gets "Missing partition table". No runtime guard — at least document the constraint in the template README or the scaffold should verify it. The template's `platformio.ini` `extra_configs = ../../platformio.shared.ini` has the same depth sensitivity.
- MEDIUM — The test's claim "exact per-template file inventory" lists `include/.gitkeep` and `assets/.gitkeep`; the Arduino `test/test_homework/test_homework.c` path needs the directory. If `.gitkeep` files are committed with mode 100644 and zero bytes, `git ls-files` keeps them — but in a clean checkout `git clone` does create empty files (fine). However, `scripts/new_homework` must copy the `.gitkeep` files; `--no-empty` rules not involved.
- MEDIUM — `sdkconfig.defaults` only contains 3 lines; the builders may need `CONFIG_BOOTLOADER_WDT` defaults. Verified build succeeded, so acceptable.
- MEDIUM — Template README links to `../../templates/report/report.md` (which only exists after 04-03) and `task.md`. The link target for report is `../../templates/report/report.md` (from `homeworks/<id>/README.md` → `templates/report/report.md`). That's a cross-tree link inside the repo, which works on disk but not on a Pages site serving only `homeworks/`? Phase 5 handles site nav; note it as a Phase 5 implication. Not a blocker.
- LOW — `default_envs` is set to target env only, but PlatformIO's `pio test -e native` requires explicit flag; some developers expect `pio test` to run native. D-28 deliberately does this; note in docs.
- LOW — The test asserts `framework` property... no, it checks placeholder vocabulary and ini shape; good two-sided assertion.

**Suggestions**
- Add a CI-equivalent smoke (one-time) `pio run -e esp32s3_arduino -t compiledb` to assert adapters compiled by name in generated `compile_commands.json` — the research already did; pinning in `test_templates.py` would protect against `src/main.cpp` forgetting the include.
- Forgive the `libraries` glue: `lib_deps = common=symlink://../../lib/common` requires `lib` at sibling depth of `homeworks/`. If `lib/` is ever relocated, all templates break. Note AGENTS.md path contract.

**Risk Assessment**
MEDIUM — Excellent verification evidence; primary residual risk is depth-locked relative paths and the external dependency on `lib/` + `platformio.shared.ini` + `partitions/`/`scripts/pio/` all co-located.

## 04-03

**Summary**
Plan 04-03 extends the contract with `task.md` provenance rules, the Cyrillic gate + allowlist, the cross-validation between `source.reference` and `source_url`, the D-39 sentinel-status branch, and adds the four remaining template directories plus the ADR template move. It directly resolves the Open Question 1 conflict. It also quietly extends D-39 to `source.reference` ("record in task summary") — a reasonable scope decision but it creates a contract change not represented in CONTEXT.md locked decisions beyond D-39; ADR-0009 must carry it (04-05).

**Strengths**
- Uses `yaml.BaseLoader` (Pattern 4) so unquoted ISO timestamps stay strings — matches the probe in findings and prevents `retrieved: 2026-...` from becoming datetime. Correct.
- `validate_candidate` is filesystem-free, enabling D-12's shared single validation entry point for `new_homework` before first write.
- Allowlist shape with path+reason, stale-entry fails — consistent with `check_architecture.py` allowlist (referenced pattern).
- ADR move with three-site impact (README link, test_adrs.py at line 26 and 135) handled in the same commit; byte-identical move via `git mv`.

**Concerns**
- HIGH — The Cyrillic scan (`CYRILLIC = re.compile(r"[Ѐ-ԯ... microtime range]"`) as one regex. The text reports it "matches `поліцейський`" but the range `[Ѐ-ԯ]` excludes some Cyrillic (e.g., top-level extended ranges could miss 𝓙? plan names 4 ranges total). Plan says 4 disjoint ranges; verify coverage of Extended-A/B/C/Phonetic. A user could spell a homoglyph (`е` Latin vs `е` Cyrillic) or copy an OCR typo. The allowlist mechanism handles false positives but false negatives (real Cyrillic that slips through) are not handled. At ASVS MEDIUM that's a known acceptance.
- HIGH — `stale allowlist entry` records are appended after `apply_allowlist`; if an allowlist has both a valid suppression (full exit 0 candidate) and a stale entry, the final exit is 1. Correct. But `apply_allowlist` matches on record path — if checker emits a Cyrillic record for `task.md` BEFORE allowlist load (missing allowlist = exit 2), path must be repo-relative. OK. If `--dir` is a temp root, allowlist path equals temp root path; the test scenario "entry for a different path" → stale entry exit 1. Fine. But in test harness the allowlist path is `scripts/metadata/allowlist.json` and the matched record path is `homeworks/1_3-prov/task.md`; tests must name the full repo-relative path. Helpers need to be documented in test.
- MEDIUM — "exact sentinel TODO in four fields": what if a field contains `TODO (fill later)` with extra text? Plan says "equal to the sentinel" → accepted only when planned. So `TODO (extra)` would fail URL checks under planned, implying review signal — arguably good (strictness).
- MEDIUM — Status change `planned → in-progress` requiring real provenance means any lone `uv run scripts/new_homework` output cannot pass checker; the scaffold's own scaffolded `task.md` ships every field with `TODO`, and `status: planned`. So wiring a hook on unrendered `templates/.../task.md` must fail (it does) since templates are excluded from the `files` glob.
- LOW — `homework.yaml` field `source.reference` cross-validation (D-17) says mismatch is exit 1; plan implements when both carry URLs. When `reference: TODO` (sentinel) and `source_url: TODO`, both "match" but that's allowed only at planned.
- LOW — `report`/`simulation` block optional; tests only concern provenance.

**Suggestions**
- Pin the Cyrillic ranges against CLDR's `[\p{Script=Cyrillic}]` or switch to `unicodedata` category `LC`/`L` lookup of Script extension — a `[^\w]`-aware check is more robust and avoids test fragility. Keep the regex only if necessity; but the plan's probe already validates, so fine as written.
- Make `validate_candidate` return record dicts with a `block` key for debugging at JSON output? No — CONTEXT says "any other content is a CONFLICT"; stick to 3 keys per D-23.

**Risk Assessment**
HIGH — The most complex single plan. It lands 4 fields × 2 sentinel sides × allowlist staleness × cross-validation simultaneously in a shared module that only exists after this plan; 04-04 consumes it. Implementation defects in `BaseLoader`/sentinel logic could leak invalid provenance and not be surfaced until pilot. Mitigate by adopting test_matrix from task 2 fully rather than subTests that collapse.

## 04-04

**Summary**
Plan 04-04 builds `scripts/new_homework`, two committed golden trees, `scripts/tests/test_new_homework.py`, `scripts/tests/temp_root.py`, `scripts/tests/test_metadata_deps.py`, and the pre-commit `check-metadata` hook. It is the highest-risk execution surface (path resolution, atomic writes, content-idempotency, placeholder rendering, validation-before-write). The "plan-then-write" design is right; the main operational concern is cross-platform atomicity (POSIX `os.replace` within dir is fine) and the absolute-path usage inside subprocess tests (`--dir` seam, per OQ 5). The plan's checker hook uses `language: python` + `additional_dependencies` (D-13) but `entry: python scripts/check_metadata.py` — the entry script is invoked via pre-commit's python, and its PEP 723 shebang does not apply (correct, since `language: python` runs plain `python`); requires `scripts/check_metadata.py` to be runnable when `python` is pre-commit's interpreter. The drift test guards versions, not import path. (The repo has no `__init__.py` at scripts/ — wait, 04-01 adds `scripts/metadata/__init__.py` only; `scripts/__init__.py`? Let's check.)

**Strengths**
- `[env:native]` sim pattern for tmp root build — same as validated recipe.
- `--dry-run` as same algorithm with write skipped — fulfills D-21 by construction rather than a separate branch.
- Symlinked templates refused; symlinked targets are `CONFLICT` — mitigates path traversal / elevation (T-04-03).
- Golden trees pin any scaffold change as a diff (D-37) — strong regression guard.
- `--json` exact three-key records for CI consumption named by 04-01 as CI-consumer.

**Concerns**
- HIGH — Template rendering with `re.sub`? If template contains a `{{}` junk entry (unknown double-brace), the plan says exit 2; but the placeholder lint (04-02/04-03) should catch in CI. The scaffold must reject `{{` inside strings it does not own; a `{{ define.inspect }}`-style unknown in a `README.md` fails before any write. Good. But there's a subtle bug: the literal `${...}` in plain substitution could occur in `platformio.ini`'s comments or `${sys.parallel...}`-like; the template `platformio.ini` extends a shared ini but keeps nothing like that, so fine. Still, every template file must be scanned including `.gitkeep` (empty, safe) and binary-like `sdkconfig.defaults`.
- MEDIUM — `templates/homework-*/task.md` is NOT in the template; `task.md` is composed from `templates/task/task.md` (OQ 6 resolution). The plan calls out "every file under template except `template.yaml`, plus task.md from templates/task". Good. But the golden-tree tests must verify the rendered `task.md` equals rendered task template; since there is only one task template (D-26 move), fine.
- MEDIUM — The temp_root helper must be stdlib; D-14 forbids importing PyYAML/jsonschema in tests. `temp_root.py` is only copying files, so okay. But the drift test is "parse text" only — passing; ensure no accidental `import yaml` in `test_new_homework.py`.
- MEDIUM — All-or-nothing "nothing is written when any conflict exists" requires validation BEFORE `mkdir`, but `tempfile.mkstemp(dir=target.parent)` needs `target.parent` to exist, and if target.parent doesn't exist yet it fails. Plan addresses: "create target directories, THEN write each file through temp + os.replace" after the all-conflict gate, so no parent absent at write time. But the *candidate set* classification (CREATE for target absent) requires only in-memory; good. However a read-only filesystem or permission issue fails at write time after the plan prints CREATE — exit 2 then. Acceptable.
- LOW — `--dir` default uses `git rev-parse --show-toplevel`; a file-only environment (no git) would need `GT` env. Sufficient per OQ 5.
- LOW — PEP 723 shebang `#!/usr/bin/env -S uv run --script` requires `uv` on PATH; confirmed in environment.

**Suggestions**
- Add a test for parent-directory creation: scaffold a new id in a fresh tmp (candidate `homeworks/<id>` absent) succeeds and creates eight paths; a conflict run leaves `homeworks/` itself created? D-21 says "never writes, never creates directories"; the conflict path must not call `mkdir` at all. Assert no empty `homeworks/` directory. The automated verify in plan already does `test ! -e "$TMP/homeworks/1_3-conf/assets/.gitkeep"` but parent may linger — add `homeworks/<id>` absence check.
- Capture and verify the per-`CREATE` path count equals 8 + scaffolding dirs; the golden tree does this.

**Risk Assessment**
HIGH — Most execution-intensive plan; failure modes include path containment false-negatives, atomic-write races on Windows (not in scope, dev on Linux/mac), and the exact-byte golden-tree pinning. Proven by tests; gate (04-05) needs to actually build from scaffolded output.

## 04-05

**Summary**
Plan 04-05 records the contract as ADR-0009/0010, updates `AGENTS.md` (layout, quick-start, metadata rules sub-section, routing table, pre-commit row) under the 300-line ceiling, adds `templates/**/*.md` to `REUSE.toml` CC-BY list after MIT catch-all, and runs the full gate: two real builds from scaffolded output, ESP-IDF sdkconfig check, full suite, pre-commit. It is the integration gate and is appropriately scoped except for two documentation constraints that are easy to violate: `AGENTS.md` already has exactly one anchored backtick pattern (see test_homework_id), and D-34 demands adding `schema/` + `templates/` + `lib/` to "present today" — all fine, but the new metadata-rules section must not accidentally quote pypi version pins in backticks starting with `^` and ending with `$` (unlikely), and must not exceed 300 lines (already 200, 100 lines of headroom — tight for five edits + rules sub-section + two routing rows).

**Strengths**
- Gate builds from scaffolded output, not hand-rendered fixtures (D-22) — critical: proves Phase 3 carry-forward on the real deliverable path.
- `reuse --no-multiprocessing lint` + test_license_hygiene run; annotation ordering enforced (last-match-wins, confirmed REUSE comment and test plan).
- Phase 8 explicitly named as CI owner (avoids overclaiming automation today).

**Concerns**
- MEDIUM — `AGENTS.md` additions must fit under 300 lines. Plan adds quick-start row, layout moves 3 paths, a new `### Metadata and provenance` rules subsection (four [MUST] rules), routing table two rows, and pre-commit purpose edit. Existing layout blocks already mention these paths under "Planned" with descriptions; removing three lines saves ~3 lines but the subsection must be compact. The two-sentence risk<rfl:parameter name=" may exceed 300. Must measure.
- MEDIUM — `REUSE.toml` only adds `.md` glob for templates; the `templates/**/*.ini` and `templates/**/*.json` "stay MIT catch-all" — per plan comment they do, but no explicit annotation means catch-all claims them — correct (default rule, fine).
- MEDIUM — `scripts/new_homework` gate verifies the build, but if the test suite or pre-commit fails, the plan note says "fix the owning plan rather than weakening the gate"; fine. However `pre-commit run --all-files` will newly run the `check-metadata` hook which scans `homeworks/` (empty) and must exit 0 — because 04-04 hook `always_run`? The plan sets HA... no, `always_run` not set for check-metadata; pre-commit default runs only if `files` match. With no homework files, it may be skipped. The plan states `pre-commit run check-metadata --all-files`; that forces it. Ensure the hook's `files` pattern also matches `schema/` so pre-commit activates (it does, `schema/homework.schema.json` matches).
- LOW — The gate runs `pio run` which requires network (none new). Already proven available.

**Suggestions**
- Measure `wc -l AGENTS.md` after edits as part of the gate: plan's own automated check `wc -l` with 300 ceiling.
- ADR-0009 must enumerate the field sets (D-01) and the D-39 extension to `source.reference` (04-03 decided) to avoid documentation debt; plan does enumerate.
- Update the agent quick-start COMMANDS? `test_agents_md` checks five exact substrings; new `uv run scripts/check_metadata.py` isn't required by the test, so harmless.

**Risk Assessment**
MEDIUM — Integration-weighted risk; if 04-04's scaffold has a subtle bug, both template builds fail late. But each piece was verified independently by research, and the gate formally covers it.

## Cross-plan and overall

**Phase-level risk**: MEDIUM overall. Foundations are excellent and build-proven; the heaviest landmine is the Wave-2/Wave-3 contract drift (04-03's sentinel branch must match 04-04's scaffold and 04-01's checker byte-for-byte). Plan count: all five covered.

---

## Antigravity Review

This review evaluates the five execution plans (`04-01-PLAN.md` through `04-05-PLAN.md`) for Phase 4 against the codebase at `/Users/vloktiev/Dev/miltech/homeworks`. All referenced files, line numbers, test contracts, and build behaviors have been verified directly against the working repository.

---

## 04-01

### 1. Summary
Plan 04-01 establishes the foundational metadata contract for the homework monorepo. It introduces `schema/homework.schema.json` (JSON Schema 2020-12 with strict `additionalProperties: false` across root and definitions), the shared validation module `scripts/metadata/contract.py`, and the CLI checker `scripts/check_metadata.py`. It implements the repository-standard `0/1/2` exit-code contract and `--json` format for Phase 8 CI integration. In strict adherence to decision D-14, test coverage in `scripts/tests/test_homework_metadata.py` is entirely standard-library-based without direct third-party imports of `yaml` or `jsonschema`.

### 2. Strengths
- **Single Source of Truth**: Eliminates validator duplication by designing `scripts/metadata/contract.py` as the sole engine imported by both `scripts/check_metadata.py` and the future `scripts/new_homework` (D-12).
- **Proactive Schema Pitfall Avoidance**: Replaces the `format` keyword with anchored regex `pattern` attributes and explicit Python date validation, bypassing JSON Schema 2020-12's silent annotation-only default behavior (Pitfall P1).
- **Zero-Dependency Test Rigor**: Adheres to D-14 by writing `scripts/tests/test_homework_metadata.py` strictly using `unittest` and `subprocess`, asserting on exit codes and `--json` outputs across isolated temporary trees without introducing `PyYAML` or `jsonschema` into the test runner.
- **Literal Identifier Synchronization**: Asserts that `contract.py` shares the exact canonical ID regex literal (`^[0-9]+_[0-9]+-[a-z0-9-]+$`) documented in [AGENTS.md:139](file:///Users/vloktiev/Dev/miltech/homeworks/AGENTS.md#L139) and tested in [scripts/tests/test_homework_id.py:26](file:///Users/vloktiev/Dev/miltech/homeworks/scripts/tests/test_homework_id.py#L26).

### 3. Concerns
- **[MEDIUM] Unhandled YAML Syntax Errors vs. Exit Code Contract**:
  - *Evidence*: Task 2 specifies parsing with `yaml.safe_load(text)` inside `validate_homework_text`. If a target `homework.yaml` contains invalid syntax (e.g. malformed indentation or unmatched quotes), `yaml.safe_load` raises `yaml.YAMLError` (`ScannerError`/`ParserError`).
  - *Mechanism*: If this exception is unhandled or caught as `CheckError`, `scripts/check_metadata.py` exits `2` (environment/usage error). However, per the exit code contract in [scripts/check_architecture.py:14-19](file:///Users/vloktiev/Dev/miltech/homeworks/scripts/check_architecture.py#L14-L19) and D-11, an invalid file under `homeworks/` is a metadata violation that must output `PATH: ERROR — <reason>` and exit `1`. Exit `2` must be reserved strictly for environment errors (e.g., missing schema, inaccessible repository root, or invalid CLI arguments).
- **[LOW] Handling Non-Mapping YAML Payloads**:
  - *Evidence*: `yaml.safe_load("")` on an empty file returns `None`; a YAML document containing only a scalar or array returns a non-dict.
  - *Mechanism*: While `Draft202012Validator.iter_errors` correctly flags `None is not of type 'object'`, downstream cross-validation (such as checking `toolchain.platform` against `platformio.shared.ini` per [platformio.shared.ini:2](file:///Users/vloktiev/Dev/miltech/homeworks/platformio.shared.ini#L2)) must guard against non-dict types before key indexing to avoid `TypeError`.
- **[LOW] `derive_parts` Input Validation**:
  - *Evidence*: `derive_parts(homework_id)` in Task 2 splits on the first underscore and first hyphen.
  - *Mechanism*: If called with an arbitrary string without first checking `HOMEWORK_ID.match()`, an unexpected string could raise `ValueError` or `IndexError`.

### 4. Suggestions
- Wrap `yaml.safe_load` inside `validate_homework_text` in a `try...except yaml.YAMLError as exc:` block that yields a structured `{"path": path, "status": "ERROR", "reason": f"YAML syntax error: {exc}"}` record, guaranteeing exit code 1 on malformed files.
- Ensure `derive_parts` validates the identifier against `HOMEWORK_ID` before slicing.

### 5. Risk Assessment
- **Risk Level**: LOW. The architecture is straightforward, bounded, and closely mirrors the mature conventions of `scripts/check_architecture.py`.

---

## 04-02

### 1. Summary
Plan 04-02 authors the two PlatformIO homework templates (`templates/homework-arduino/` and `templates/homework-espidf/`). It ensures each template satisfies the project structure requirements of FOUND-01 and META-03. Crucially, it discharges the Phase 3 carry-forward from `.planning/STATE.md` by demonstrating that the template starter code directly compiles the port adapters (`lib/arduino` and `lib/espidf`) under target toolchains. It also establishes template consistency checks in `scripts/tests/test_templates.py`.

### 2. Strengths
- **Closure of Deferred Adapter Compilation**: The starter code includes [lib/arduino/include/arduino/gpio.h:14](file:///Users/vloktiev/Dev/miltech/homeworks/lib/arduino/include/arduino/gpio.h#L14) and [lib/espidf/include/espidf/gpio.h:15](file:///Users/vloktiev/Dev/miltech/homeworks/lib/espidf/include/espidf/gpio.h#L15), linking through `arduino_gpio_port()` and `espidf_gpio_port()`. This proves target compilation of the adapters at homework depth via `pio run`, resolving the Phase 3 deferral with empirical compiler evidence.
- **Protection Against List Option Overwrite**: Adheres to Pitfall P8 (documented in [tests/platformio.ini:16-21](file:///Users/vloktiev/Dev/miltech/homeworks/tests/platformio.ini#L16-L21)) by having target environments specify only `extends` and `lib_deps`. This preserves inherited `build_flags` (such as `-DBOARD_HAS_PSRAM` from [platformio.shared.ini:15](file:///Users/vloktiev/Dev/miltech/homeworks/platformio.shared.ini#L15)).
- **Clean ESP-IDF Generated File Boundary**: Leaves `CMakeLists.txt`, `src/CMakeLists.txt`, and `sdkconfig.<env>` out of the repository tree (Pitfalls P4 & P5), providing only the authored `sdkconfig.defaults` (16 MB flash, octal PSRAM). This respects `.gitignore` rules and the pre-commit hook in [.pre-commit-config.yaml:38-48](file:///Users/vloktiev/Dev/miltech/homeworks/.pre-commit-config.yaml#L38-L48).
- **Graceful Multi-Phase Template Inventory**: Configures `scripts/tests/test_templates.py` to skip template directories that do not yet exist (`task`, `report`, `adr`, `board-profile`), allowing Wave 1 tests to remain green before Plan 04-03 runs.

### 3. Concerns
- **[LOW] Arduino Sketch Lifecycle vs. Contract Instance Scoping**:
  - *Evidence*: [docs/decisions/0008-common-depends-on-port.md:68-69](file:///Users/vloktiev/Dev/miltech/homeworks/docs/decisions/0008-common-depends-on-port.md#L68-L69) notes: *"a consumer holds a borrowed const pointer for the duration of a call and never stores it in a global"*.
  - *Mechanism*: In `templates/homework-arduino/src/main.cpp`, `setup()` initializes the port structs and `loop()` writes pin levels. Because the Arduino runtime splits initialization from iteration without a continuous caller frame, holding `port_gpio_t` across iterations requires static file-scope storage. The plan permits this ("file-scope or function-scope values passed by pointer"), but the template code should explicitly document that file-scope storage is an Arduino composition-root necessity, distinct from library code where global state remains prohibited.
- **[LOW] Native Unity Test Download in Cold Environments**:
  - *Evidence*: `[env:native]` in both templates declares `throwtheswitch/Unity@2.6.1` in `lib_deps`, mirroring [tests/platformio.ini:29](file:///Users/vloktiev/Dev/miltech/homeworks/tests/platformio.ini#L29).
  - *Mechanism*: While cached on the primary development environment, a cold runner without internet access during `pio test -e native` would fail if PlatformIO needs to fetch Unity.

### 4. Suggestions
- Add an explanatory comment in `templates/homework-arduino/src/main.cpp` clarifying why `static port_gpio_t` is retained at file scope in Arduino sketches.
- Verify that `scripts/tests/test_templates.py` asserts that `sdkconfig.defaults` in `templates/homework-espidf` contains exactly the three expected lines (`CONFIG_ESPTOOLPY_FLASHSIZE_16MB=y`, `CONFIG_SPIRAM=y`, `CONFIG_SPIRAM_MODE_OCT=y`).

### 5. Risk Assessment
- **Risk Level**: LOW. The build configurations have been pre-validated via probe fixtures, and the templates strictly maintain the architectural boundaries.

---

## 04-03

### 1. Summary
Plan 04-03 integrates the provenance rules for `task.md` frontmatter, implements the Cyrillic gate and deny-by-default allowlist (`scripts/metadata/allowlist.json`), and introduces cross-validation between `homework.yaml` and `task.md`. It also creates the four remaining template directories (`templates/task/`, `templates/report/`, `templates/board-profile/`, and `templates/adr/`), relocating the existing MADR template from `docs/decisions/template.md` to `templates/adr/template.md` and updating its consumers.

### 2. Strengths
- **Status-Conditional Sentinel Resolution (D-39)**: Solves the tension between unpopulated starter templates and strict provenance checking by allowing literal `TODO` values in `task.md` and `homework.yaml` (`source.reference`) exclusively when `status: planned`. Any advancement to `in-progress`, `complete`, or `verified` strictly enforces real URLs, ISO 8601 timestamps with timezones, and SPDX licenses.
- **Frontmatter Scalar Preservation (Pitfall P2)**: Parses frontmatter with `yaml.BaseLoader` instead of `SafeLoader`, ensuring unquoted ISO 8601 timestamps are preserved as strings rather than converted to `datetime.datetime` objects.
- **Fail-Fast Stale Allowlist Enforcement**: Requires allowlist entries to have non-empty `path` and `reason` fields, enforcing a 64 KiB cap and failing with exit code 1 if an entry is unused, following the model of [scripts/check_architecture.py:51-53](file:///Users/vloktiev/Dev/miltech/homeworks/scripts/check_architecture.py#L51-L53).
- **Consolidated Validation Candidate Seam**: Introduces `validate_candidate` in `contract.py`, enabling Plan 04-04's scaffolding script to validate rendered content in memory before writing to disk.

### 3. Concerns
- **[MEDIUM] Broken Path in Legal Attribution `NOTICE`**:
  - *Evidence*: [NOTICE:21-25](file:///Users/vloktiev/Dev/miltech/homeworks/NOTICE#L21-L25) states:
    ```markdown
    ### MADR decision-record template

    `docs/decisions/template.md` is derived from the MADR 4.0.0 template
    (<https://github.com/adr/madr>), which is licensed under the MIT License.
    ```
  - *Mechanism*: Task 3 moves `docs/decisions/template.md` to `templates/adr/template.md` and updates [docs/decisions/README.md:6](file:///Users/vloktiev/Dev/miltech/homeworks/docs/decisions/README.md#L6) and [scripts/tests/test_adrs.py:26, 135](file:///Users/vloktiev/Dev/miltech/homeworks/scripts/tests/test_adrs.py#L26). However, `NOTICE` is omitted from `files_modified` and Task 3 actions. Moving the file leaves a dead path reference in the repository's legal notice.
- **[MEDIUM] Exit Code on Missing or Corrupt `task.md` Frontmatter**:
  - *Evidence*: Task 1 states: *"Add `parse_task_frontmatter(text)` that splits at the leading fence pair... and raises `CheckError` when the fences are absent, the block is not a mapping, or the mapping is empty"*.
  - *Mechanism*: If `parse_task_frontmatter` raises `CheckError` and it is not caught within `validate_task_text`, the CLI checker will exit `2`. However, missing or malformed frontmatter in a homework's `task.md` is a contract violation (exit `1`), not an environmental failure (exit `2`).

### 4. Suggestions
- Add `NOTICE` to `files_modified` in Plan 04-03, updating line 21 to reference `templates/adr/template.md`.
- Ensure `validate_task_text` catches frontmatter parsing errors and translates them into `ERROR` records on `task.md` rather than allowing `CheckError` to abort execution with exit code 2.

### 5. Risk Assessment
- **Risk Level**: MEDIUM. While the core validation logic is robust, the unhandled legal notice reference in `NOTICE` and the exit code mapping for malformed frontmatter require correction.

---

## 04-04

### 1. Summary
Plan 04-04 delivers `scripts/new_homework`, the authoritative tool for scaffolding homework directories. It enforces content-based idempotency (D-20), atomic file writes (D-24), strict `--dry-run` parity (D-21), and conflict detection without partial writes. It pins generated output against committed golden trees (`scripts/tests/fixtures/golden/`), integrates the `check-metadata` pre-commit hook into `.pre-commit-config.yaml`, and adds a stdlib test (`scripts/tests/test_metadata_deps.py`) to guarantee synchronization between PEP 723 script dependencies and pre-commit hook configurations (D-13).

### 2. Strengths
- **Strict Plan-Then-Write Architecture**: Renders all candidate files in memory, validates them via `contract.validate_candidate`, and evaluates filesystem states before creating directories or touching disk. Any validation error or file conflict aborts the run cleanly with zero writes.
- **True Content Idempotency**: By deriving title without clock lookups (Pitfall P10) and comparing target files byte-for-byte, repeated runs cleanly report `UNCHANGED` with exit code 0.
- **Path Traversal Containment**: Enforces path containment (`target.resolve().relative_to(base)`) and strictly validates `homework_id` and template names before inspecting the filesystem, mitigating traversal threats (T-04-02).
- **Dependency Drift Prevention (D-13)**: The stdlib-only `test_metadata_deps.py` parses PEP 723 metadata from both `scripts/check_metadata.py` and `scripts/new_homework`, asserting equality against `.pre-commit-config.yaml`'s `additional_dependencies`.

### 3. Concerns
- **[LOW] Parent Directory Creation Before `tempfile.mkstemp`**:
  - *Evidence*: `write_atomic` uses `tempfile.mkstemp(dir=target.parent, prefix=".new_homework-")` to ensure atomicity via same-filesystem `os.replace`.
  - *Mechanism*: For nested project files (e.g. `homeworks/<id>/src/main.cpp`), `target.parent` does not exist prior to scaffolding. Furthermore, in a clean repository, `homeworks/` itself does not exist. `new_homework` must ensure `os.makedirs(target.parent, exist_ok=True)` is called prior to invoking `mkstemp` during the write phase.
- **[LOW] Symlinked Target Handling**:
  - *Evidence*: D-20 requires that any unexpected target content is treated as a `CONFLICT`.
  - *Mechanism*: If an existing path in `homeworks/<id>` is a symlink, comparing content might follow the link or fail unexpectedly. The path classification loop should explicitly check `target_path.is_symlink()` and classify it as `CONFLICT`.

### 4. Suggestions
- Ensure `write_atomic` explicitly calls `target.parent.mkdir(parents=True, exist_ok=True)` before `mkstemp`.
- Include a specific test case in `scripts/tests/test_new_homework.py` asserting that an existing symlink at a target file path triggers a `CONFLICT` record and leaves the symlink intact.

### 5. Risk Assessment
- **Risk Level**: LOW. The plan-then-write workflow combined with golden-tree diffing and atomic renames provides strong protection against corrupting repository state.

---

## 04-05

### 1. Summary
Plan 04-05 finalizes Phase 4. It documents architectural decisions in ADR-0009 (Metadata Contract) and ADR-0010 (Python Dependency Policy), updates `AGENTS.md` and `REUSE.toml` to reflect the new repository layout and licensing, and runs the final phase gate. The gate proves success criterion 2 by scaffolding both Arduino and ESP-IDF projects with `scripts/new_homework`, building them with `pio run`, verifying octal PSRAM and 16 MB flash from generated `sdkconfig.json`, and running the complete test suite and pre-commit hooks.

### 2. Strengths
- **Verification from Scaffolded Output**: Validates success criterion 2 by running `pio run` against projects produced directly by `scripts/new_homework` rather than pre-fabricated fixtures.
- **Hardware Profile Evidence**: Extracts and asserts on `sdkconfig.json` to prove `CONFIG_ESPTOOLPY_FLASHSIZE_16MB=y` and `CONFIG_SPIRAM_MODE_OCT=y`, verifying the hardware contract established in FOUND-09.
- **Accurate CI Scope Documentation**: Explicitly notes in the Confirmation sections of ADR-0009 and ADR-0010 that verification is performed via local developer commands today, acknowledging that automated CI enforcement belongs to Phase 8.
- **Licensing Order Preservation**: Follows the last-match-wins rule in `REUSE.toml` by placing the `templates/**/*.md` CC-BY-4.0 annotation after the catch-all MIT rule.

### 3. Concerns
- **[HIGH] Regex Pattern Count Collision in `test_homework_id.py`**:
  - *Evidence*: [scripts/tests/test_homework_id.py:38-42, 55-60](file:///Users/vloktiev/Dev/miltech/homeworks/scripts/tests/test_homework_id.py#L38-L42) implements the following test:
    ```python
    cls.patterns = [
        span
        for span in BACKTICKED.findall(cls.text)
        if span.startswith("^") and span.endswith("$")
    ]
    ...
    def test_documents_exactly_one_anchored_pattern(self):
        self.assertEqual(
            len(self.patterns),
            1,
            f"expected exactly one anchored pattern in AGENTS.md, found {self.patterns}",
        )
    ```
  - *Mechanism*: Task 2 updates `AGENTS.md` by adding a `### Metadata and provenance` section. If this section quotes the ID pattern again in backticks (e.g. `` `^[0-9]+_[0-9]+-[a-z0-9-]+$` ``) or introduces any other anchored backticked regular expression (such as pre-commit file patterns like `` `^(homeworks/|schema/...)` ``), `len(self.patterns)` will exceed 1, causing `scripts/tests/test_homework_id.py` to fail.
- **[LOW] Line Ceiling Budget in `AGENTS.md`**:
  - *Evidence*: [scripts/tests/test_agents_md.py:25](file:///Users/vloktiev/Dev/miltech/homeworks/scripts/tests/test_agents_md.py#L25) enforces `LINE_CEILING = 300`.
  - *Mechanism*: `AGENTS.md` is currently 200 lines long. The planned additions (quick-start table entry, layout updates, rules section, routing table entries) must remain concise to stay well clear of the 300-line limit.

### 4. Suggestions
- When updating `AGENTS.md` in Task 2, do not place any anchored regex pattern inside backticks in the new `### Metadata and provenance` section. Reference the rule in `### Homework identifiers` by prose or cross-reference instead.
- Run `python3 -m unittest scripts.tests.test_homework_id` immediately after modifying `AGENTS.md`.

### 5. Risk Assessment
- **Risk Level**: MEDIUM. The regex assertion collision in `test_homework_id.py` is an immediate point of failure if `AGENTS.md` is edited without strict awareness of the test's exact regex scanning mechanics.

---

## Overall Phase 4 Synthesis & Cross-Plan Analysis

### Alignment with Phase 4 Success Criteria
1. **Scaffold Functionality**: Success Criterion 1 (idempotent, dry-run, refusal to overwrite) is fully covered by Plan 04-04 (`scripts/new_homework`).
2. **Immediate Buildability**: Success Criterion 2 (scaffolded project contains 8 paths and builds immediately) is addressed across 04-02, 04-04, and verified in the gate in 04-05.
3. **Strict Metadata Schema**: Success Criterion 3 (`homework.yaml` schema with `additionalProperties: false` at all levels) is delivered by 04-01.
4. **Task Provenance and Original Paraphrase**: Success Criterion 4 (`task.md` frontmatter, absence of internal materials) is covered by 04-03, with machine checks for shape and Cyrillic script, and manual review for paraphrase authenticity.
5. **Template Suite**: Success Criterion 5 (Arduino, ESP-IDF, report, task, ADR, and board-profile templates) is split cleanly between 04-02 and 04-03.

### Critical Action Items Before Execution
1. **Update `NOTICE` Path (Plan 04-03)**: Include `NOTICE` in Plan 04-03 to repoint line 21 to `templates/adr/template.md`.
2. **Protect `test_homework_id.py` (Plan 04-05)**: Ensure no new backticked strings matching `^\^.*\$$` are introduced into `AGENTS.md`.
3. **Normalize Validation Exit Codes (Plans 04-01 & 04-03)**: Ensure YAML syntax errors and malformed `task.md` frontmatter emit `ERROR` records resulting in exit code 1, preserving exit code 2 strictly for invocation and environment errors.

---

---

## Consensus Summary

All three reviewers produced source-grounded reviews and each covered all five plans
(`04-01` through `04-05`). codex-glm and codex-beam share the `codex` adapter, so their
agreement is cross-model rather than cross-tool; the antigravity review uses a different
adapter and model family. codex-beam's output contains a few garbled passages in its
`04-01`/`04-02` sections, so its line-level claims were treated with lower confidence
than its architectural findings.

### Agreed Strengths

- **Single validation seam.** `scripts/metadata/contract.py` is designed as the one engine
  behind `scripts/check_metadata.py` and the future `scripts/new_homework`, avoiding a
  second validator (D-12). Raised by all three.
- **Schema pitfalls are actively avoided, not inherited.** Replacing `format` with anchored
  `pattern`s plus explicit Python date checks defuses the annotation-only behaviour of
  JSON Schema 2020-12 (Pitfall P1). Raised by all three.
- **`yaml.BaseLoader` for `task.md` frontmatter** keeps unquoted ISO timestamps as strings
  instead of `datetime` objects (Pitfall P2). Raised by all three.
- **Plan-then-write with atomic replacement and golden trees** gives 04-04 real
  all-or-nothing semantics and makes accidental scaffold drift visible. Raised by all three.
- **Builds at true homework depth** prove the Phase 3 adapter carry-forward with compiler
  evidence rather than fixtures. Raised by all three.
- **The phase gate builds from scaffolded output, not hand-rendered fixtures**, which is
  what makes success criterion 2 credible. Raised by all three.

### Agreed Concerns

1. **HIGH — `AGENTS.md` edits can break two existing tests.** The file is exactly 200 lines
   and `scripts/tests/test_agents_md.py:25` caps it at 300, while
   `scripts/tests/test_homework_id.py:38-42,55-60` asserts that `AGENTS.md` contains exactly
   **one** backticked anchored regex. The planned "Metadata and provenance" subsection must
   neither quote the ID pattern again nor add another `^…$` backticked span, and the added
   lines must stay inside the remaining budget. Raised by all three (antigravity HIGH,
   codex-glm LOW, codex-beam MEDIUM); verified against the live files.
2. **HIGH/MEDIUM — `homework.yaml.id` is not checked against its own directory name.** The
   plans validate document shape but not the location identity invariant, so a moved or
   copied `homework.yaml` can name a different homework than its parent directory. Both the
   checker (04-01) and scaffold candidate validation (04-04) should reject a mismatch.
   Raised by codex-glm (HIGH) and codex-beam.
3. **MEDIUM — the pre-commit metadata hook is configured but never invoked in tests.** D-37
   asks for the hook's invocation to be covered; the plans assert on hook text and pinned
   dependencies only, and do not run `pre-commit run check-metadata --all-files` from the
   suite. A hook that is never executed can be silently misconfigured. Raised by codex-glm
   and codex-beam.
4. **MEDIUM — 04-02's objective overclaims the template path set.** The objective says each
   homework template carries all eight FOUND-01 paths, but `task.md` is deliberately
   composed from `templates/task/task.md` in 04-03. The inventory is right; the wording is
   not. Raised by codex-glm and codex-beam.
5. **MEDIUM — directory creation ordering around `tempfile.mkstemp`.** `write_atomic` needs
   `target.parent` to exist before `mkstemp(dir=target.parent)`, and `homeworks/` may not
   exist in a clean tree. The write phase must create parents explicitly, while the
   conflict path must still create nothing. Raised by antigravity and codex-beam.
6. **LOW — symlinked targets should be an explicit `CONFLICT`.** All three reviewers ask for
   a test that a symlink at a candidate path is classified as a conflict and left intact
   rather than followed or compared through.

### Divergent Views

- **Overall risk is rated differently.** antigravity calls 04-01 LOW and 04-05 MEDIUM;
  codex-glm calls the phase MEDIUM; codex-beam rates 04-03 and 04-04 HIGH. The disagreement
  is mostly about how much weight to give cross-plan contract drift (04-01 → 04-03 → 04-04)
  versus the strength of the per-plan verification steps.
- **Template selection vs D-19 (codex-glm only, HIGH).** `--template` with argparse
  `choices: [arduino, espidf]` makes the CLI a template registry, whereas D-19 says a new
  template is a new directory. Dynamic validation against
  `templates/homework-<name>/template.yaml` would preserve both the CLI surface and D-19.
  The other two reviewers did not raise it; worth a deliberate decision either way.
- **Duplicate YAML keys (codex-glm only).** PyYAML silently keeps the last duplicate key, so
  a duplicated `source:` or `toolchain:` block can hide a real value. codex-beam notes the
  loader choice but not duplicate-key handling.
- **Cyrillic range coverage (codex-beam only, HIGH).** A hand-written disjoint range set can
  miss Extended-A/B/C and homoglyphs; a script-property check would be more robust. The
  plan's probes cover the named samples, so this is a hardening question rather than a
  proven defect.
- **Input-size caps beyond the allowlist (codex-glm only, HIGH).** The 64 KiB cap is applied
  to `allowlist.json` but not explicitly to `homework.yaml` and `task.md`.
- **Exit-code semantics for malformed input (antigravity only).** YAML syntax errors and
  malformed `task.md` frontmatter must become ERROR records (exit 1), not escape as
  `CheckError` (exit 2). This is verified against the `0/1/2` contract in
  `scripts/check_architecture.py:14-19` and is the sharpest single finding in that review.
- **`NOTICE` still points at the old ADR template path (antigravity only, MEDIUM).** 04-03
  moves `docs/decisions/template.md` to `templates/adr/template.md` and updates
  `docs/decisions/README.md` and `scripts/tests/test_adrs.py`, but `NOTICE:21` still names
  `docs/decisions/template.md` and `NOTICE` is absent from `files_modified`. Verified: the
  reference is live and the plan does not mention it.

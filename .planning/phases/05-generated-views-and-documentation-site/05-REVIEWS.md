---
phase: 05
reviewers: [codex, antigravity, ollama]
reviewed_at: 2026-10-25T21:59:53Z
plans_reviewed:
  - .planning/phases/05-generated-views-and-documentation-site/05-01-PLAN.md
  - .planning/phases/05-generated-views-and-documentation-site/05-02-PLAN.md
  - .planning/phases/05-generated-views-and-documentation-site/05-03-PLAN.md
  - .planning/phases/05-generated-views-and-documentation-site/05-04-PLAN.md
  - .planning/phases/05-generated-views-and-documentation-site/05-05-PLAN.md
  - .planning/phases/05-generated-views-and-documentation-site/05-06-PLAN.md
  - .planning/phases/05-generated-views-and-documentation-site/05-07-PLAN.md
  - .planning/phases/05-generated-views-and-documentation-site/05-08-PLAN.md
  - .planning/phases/05-generated-views-and-documentation-site/05-09-PLAN.md
models:
  codex: "glm-5.3-flash:cloud (reasoning=high)"
  antigravity: "gemini-3.8-flash-high"
  ollama: "glm-5.3-flash:cloud"
model_sources:
  codex: "pinned"
  antigravity: "pinned"
  ollama: "requested"
---

# Cross-AI Plan Review — Phase 05

<!-- gsd:plan-revision-conflicts:begin -->
## Plan-Revision Conflicts
<!-- gsd:plan-revision-conflicts:end -->

## Codex Review

# Plan Review — Phase 05 vs. repository source

I verified the referenced renderer, checker, schema, fixture, workspace, shared INI, tests, workflows, and authored docs directly in the repository. The plans are unusually grounded in real mechanisms, but there are two repo-level integration gaps worth fixing before execution.

## 05-01

### Summary

This is a well-scoped Wave 0 extraction plan. It targets behavior that really exists, preserves the renderer and `platformio.ini` semantics, and provides the test fixture that later generator plans need. The main risk is not in the extraction itself, but in not going far enough: the renderer/reader modules are correctly isolated from PyYAML, but the generator spine later imports the heavier metadata contract module.

### Strengths

- The extraction targets real duplication: the renderer lives in `scripts/new_homework:223-238`, `read_text` in `scripts/new_homework:241-248`, and the `extends`/`lib_deps` readers live in `scripts/check_architecture.py:419-489`.
- The `errors.py` split is justified by the real module coupling: `scripts/metadata/contract.py:44-46` imports both PyYAML and jsonschema, while the plan correctly keeps `render.py` and `platformio.py` free of those imports.
- The plan preserves the repository’s actual INI reading idiom: `configparser.ConfigParser(interpolation=None)` is already used at `scripts/metadata/contract.py:441`.
- The synthetic fixture avoids the real `docs/` and `homeworks/` trees; the existing `temp_root.py:26-37` copies only the contract-adjacent inputs, so adding `write_synthetic_root` is consistent with that pattern.

### Concerns

- **MEDIUM — `preload_extra_configs` splitting is under-specified.** The real path is `../../platformio.shared.ini` at `homeworks/1_3-police-flasher/platformio.ini:6`, and top-level tests use `../platformio.shared.ini` at `tests/platformio.ini:6`. Splitting on commas/whitespace is probably sufficient today, but the plan should define whether quoted entries or spaces inside a relative path are allowed; otherwise a future extra config can silently resolve wrong.
- **LOW — `write_synthetic_root` does not copy `partitions/`.** That is fine for the fixture tests as specified, but the docstring should state this explicitly, because `temp_root.build_root` currently does copy it at `scripts/tests/temp_root.py:26-37`.

### Suggestions

- Add one regression test that `scripts.metadata.platformio.CheckError is scripts.metadata.errors.CheckError`; the plan’s verification has this, so make it a first-class acceptance criterion.
- Specify that `preload_extra_configs` resolves every entry relative to the containing project directory, not the repository root; `homeworks/1_3-police-flasher/platformio.ini:1-6` relies on that exact rule.
- Define `write_synthetic_root`’s non-copy list explicitly in the module docstring, not only in the plan.

### Risk Assessment

**LOW–MEDIUM.** The extraction is grounded and likely safe. The main medium risk is future extra-config complexity, not today’s tree.

---

## 05-02

### Summary

This plan correctly extends the current validator rather than creating a second board validator, and the first board profile matches the committed template exactly. The major quality issue is duplicate-key handling: the board-validator wording permits `yaml.safe_load`, but the repository already has a stricter YAML loader for this exact failure mode.

### Strengths

- The existing metadata validator already enforces the sorting and JSON record contract at `scripts/check_metadata.py:204-227`; extending the record stream rather than adding a second entry point matches D-27.
- The template shape is real and small: `templates/board-profile/profile.yaml:1-8` contains exactly `id`, `soc`, `flash_mb`, `psram`, `frameworks`, and `pinout_url`.
- Rejecting JSON Schema `format` and using anchored patterns is consistent with the existing homework schema, which is strict at `schema/homework.schema.json:1-5` and has no `format` keyword.
- Avoiding a homework-to-board cross-existence rule is pragmatic: the current metadata contract permits optional simulation/report blocks, and forcing board existence would reject otherwise valid fixtures.

### Concerns

- **MEDIUM — duplicate YAML keys may be allowed in board profiles.** The plan says the validator may use `yaml.safe_load`, but `scripts/metadata/contract.py:73-101` already implements `StrictSafeLoader` specifically because PyYAML silently keeps the last duplicate mapping key. If `validate_board_text` does not use that loader, a duplicated `pinout_url` or `psram` key can pass without detection, and the proposed `BoardProfileTests` does not cover it.
- **LOW — symlink behavior for `boards/` is not specified.** The homework checker has careful identity and symlink logic at `scripts/metadata/contract.py:498-520`, while `_board_documents` is only described as returning sorted `boards/*.yaml`. The plan should state whether a symlinked board file is refused or followed by the checker.

### Suggestions

- Require `StrictSafeLoader` for board documents and add a duplicate-key test to `BoardProfileTests`.
- Add an explicit rule for symlinked board files, mirroring the checker’s existing read-only and containment posture.
- In the board schema, document why `frameworks` is an enum rather than free text; it is tied to the homework framework enum at `schema/homework.schema.json:20-24`.

### Risk Assessment

**MEDIUM.** The schema and validator structure are sound. The unresolved YAML-loader ambiguity is the main concrete gap.

---

## 05-03

### Summary

This is the strongest generated-view plan: manifest ownership, marker regions, `--check`, atomic writes, and orphan deletion are all grounded in mechanisms that already exist. It should work, but it contains the phase’s most important unresolved dependency: the generator imports the metadata contract while declaring only PyYAML, and the contract imports jsonschema.

### Strengths

- The plan-then-apply model is real: `scripts/new_homework:298-321` classifies bytes without following symlinks, `scripts/new_homework:424-436` performs an atomic temp-file write, and `scripts/new_homework:450-468` emits sorted records. Reusing that model is the right architecture.
- The README migration targets the actual stale table and prose: `README.md:9-11` still names Phase 4.2, and `README.md:13-17` contains the current four-column table with no markers.
- The manifest plan correctly accounts for `.gitignore`: `*.manifest` currently ignores all manifests at `.gitignore:253`, so `!generated.manifest` is required to make D-17 work.
- Cell escaping directly addresses published-Markdown injection: metadata titles cross into table cells in `README.md` and later the site home table.

### Concerns

- **HIGH — the generator’s declared dependency set is inconsistent with its real import graph.** The plan makes `gen_views.py` depend only on PyYAML, but it also imports `scripts.metadata.contract`; that module imports `yaml` and `Draft202012Validator` unconditionally at `scripts/metadata/contract.py:44-46`. Running under PEP 723 with only `PyYAML==6.0.3`, or later under the planned PyYAML-only pre-commit/CI environment, will fail on `ModuleNotFoundError: jsonschema`. This also affects 05-09.
- **MEDIUM — `yaml.safe_load` is not as strict as the repository’s existing loader.** `_load_homeworks` is specified with `yaml.safe_load`, but `scripts/metadata/contract.py:82-101` already proves why duplicate keys need detection. A duplicate `title` or `toolchain` key in a generated output input can silently choose the last value.
- **LOW — concurrency semantics are honest but not user-facing.** The plan states that concurrent runs are not serialized. That is acceptable for pre-commit/CI, but the CLI should print one sentence warning against parallel generator invocation.

### Suggestions

- Before 05-03, split the pure metadata helpers (`resolve_root`, `relative_path`, `derive_parts`) into a stdlib-only module, or make the generator import only narrowly isolated modules. Do not add jsonschema to the generator merely to make the import graph work.
- Use `contract.StrictSafeLoader` or an equivalent duplicate-key-aware loader in `_load_homeworks`, and add a generated row test with a duplicated YAML key.
- Add a test that the manifest never contains an entry whose path equals `generated.manifest`, even if a future view accidentally tries to register it.
- Keep `RealTreeSmokeTest` as a byte-identity check, but also assert that `--check` produces no temp files; that catches accidental repair behavior.

### Risk Assessment

**HIGH.** The generator architecture is good, but the import/dependency mismatch is not speculative: `contract.py` imports jsonschema at module scope, while the generator plans prohibit that dependency.

---

## 05-04

### Summary

`affected.py` has the right fail-safe orientation and correctly reuses the extracted `platformio.ini` readers. Its largest correctness gap is that it defines “project” as only `homeworks/*/`, so the top-level native test project is not a consumer even though it consumes shared libraries.

### Strengths

- The fanout rules are appropriately conservative: `platformio.shared.ini`, `partitions/`, `scripts/pio/`, `schema/`, and unknown paths widen to every project, so an unrecognized shared input cannot silently skip builds.
- The plan correctly preserves the `name=symlink://` alias rule: `scripts/check_architecture.py:464-489` explicitly takes the library name from the spec, not the alias.
- It correctly handles inherited `framework` through `extra_configs` and `extends`, which is necessary because the homework INI only carries `extends = esp32s3_arduino` at `homeworks/1_3-police-flasher/platformio.ini:12-17`, while the framework value lives in `platformio.shared.ini:1-4`.
- Treating a missing `library.json` `dependencies` field as a leaf is accurate today: `lib/common/library.json:1-8` and `lib/port/library.json:1-8` contain only `name`, `version`, and `build`.

### Concerns

- **HIGH — the top-level `tests/` project is excluded from “every consumer.”** `tests/platformio.ini:25-29` consumes `common`, `port`, and `host`, yet `_projects` returns records only from `homeworks/*/`. If Phase 8 consumes `build` as the matrix, a `lib/**` diff will select homework builds but not the shared-library Unity suite. That contradicts the phase goal of mapping `lib/**` changes to every consumer project.
- **MEDIUM — the dependency graph is incomplete because `library.json` dependencies do not exist.** No real manifest has a `dependencies` edge, so `common → port` is invisible. The plan acknowledges this, but a future homework that lists only `common` would silently miss `lib/port` changes.
- **LOW — exit 1 for a homework directory with no `platformio.ini` may over-trigger on metadata-only or still-scaffolding directories.** The rule is safe, but it should distinguish “changed homework source/config under a real project” from “empty homework directory,” or the error message should explicitly tell the contributor what to do.

### Suggestions

- Either include `tests/platformio.ini` as a project entry in `build`, or add an explicit `test` array to the JSON contract and update the plan’s Phase 8-facing contract. Sorting by `(project, env)` still works.
- Add explicit `FanoutTests` cases proving `lib/common` changes reach `tests/` and `lib/port` changes reach `tests/`.
- Once actual library dependencies are represented, add transitive `common → port` fanout tests plus a leaf-only manifest test.
- Record the `NO_BUILD_IMPACT` table in the generated README or a doc page as well as the module docstring, since it is policy data and not just implementation detail.

### Risk Assessment

**HIGH.** The mapper’s fail-safe behavior is good, but omitting the top-level test consumer is a real matrix-correctness failure for the next phase.

---

## 05-05

### Summary

The workspace and shared-INI plans match today’s artifacts closely and correctly refuse pin disagreement instead of choosing a winner. The remaining issues are dependency-graph reuse from 05-03 and the fact that the PlatformIO Core pin is generated as prose but not machine-checked.

### Strengths

- The current workspace really is tab-indented and whole-file structured at `homeworks.code-workspace:1-19`; generating it from a template and preserving the `extensions` block is the right compatibility choice.
- The shared INI really has the three sections and the SCons comment that must survive: `platformio.shared.ini:1-25` carries both ESP sections and `platformio.shared.ini:27-31` carries the documented SCons comment.
- Refusing multiple distinct `(toolchain.platformio, toolchain.platform)` pairs avoids the circularity described in the research: `scripts/metadata/contract.py:558-566` currently compares each homework’s platform pin against the shared INI.

### Concerns

- **MEDIUM — it inherits 05-03’s import issue.** If `gen_views.py` imports `scripts.metadata.contract` for `derive_parts` or root/path helpers, the shared-INI/workspace view still requires jsonschema at import time even though its PEP 723 dependencies do not include it.
- **MEDIUM — the PlatformIO Core pin is not machine-checked.** The generated header gives `{{platformio_pin}}` a home, but the current checker validates only `toolchain.platform` against the shared INI at `scripts/metadata/contract.py:558-566`. The homework schema requires `toolchain.platformio` at `schema/homework.schema.json:48-54`, so Core pin drift can remain unnoticed.
- **LOW — zero-homework fixture behavior needs a fixture mechanism.** `write_synthetic_root` as planned always writes two homeworks, so the zero-homework `shared-ini` case needs either a parameter or a separate minimal root builder.

### Suggestions

- Extend pin consistency to cross-check `toolchain.platformio`, the generated header’s Core pin, and the CI-installed PlatformIO Core version where feasible.
- Add a `write_synthetic_root(..., homeworks=False)` or equivalent fixture mode for the zero-homework exit-2 test.
- Add a test that the rendered shared INI contains no substring matching `homeworks/[0-9]+_[0-9]+-`; this directly pins the “zero per-homework entries” invariant.
- Capture the exact current SCons comment as a fixture string and compare the rendered file against it, not merely “contains” checks.

### Risk Assessment

**MEDIUM.** The two generated files are well-modeled; the risk is pin/version drift and the shared generator import problem.

---

## 05-06

### Summary

This is a disciplined vendoring plan. The checksum ledger, explicit file allowlist, license requirement, and CDN prohibition cover the failure modes that MkDocs cannot detect. The remaining risk is mostly process provenance and future-version hygiene.

### Strengths

- The file set is explicit and excludes unnecessary `.woff`/`.ttf` fallbacks, reducing the committed binary surface while keeping `.woff2` as normal non-LFS git objects; `.gitattributes:3-18` routes only the eight declared extension families to LFS.
- The checksum gate addresses a real MkDocs blind spot: `extra_css`/`extra_javascript` paths can be missing without warning, so `FILES.sha256` plus `verify_tree` is the only effective integrity mechanism.
- The plan verifies both listed-file completeness and on-disk-file completeness, not only digest equality; that catches partial trees and unlisted additions.
- `render-math.js` is deliberately authored rather than vendored, with Material’s `document$` re-render integration.

### Concerns

- **LOW — the ledger proves byte integrity, not source authenticity.** `FILES.sha256` is generated from the copied tarball, so it prevents partial or altered copies later, but it does not independently prove that the first copy came from the authentic npm artifact unless a provenance record or one-time digest is recorded separately.
- **LOW — ASCII-only assertion for `render-math.js` may be unnecessarily strict.** The file can be ASCII today, but forcing ASCII prevents a harmless UTF-8 comment. That is acceptable if intentional, but should be documented as a policy rather than as an implementation accident.

### Suggestions

- Add one short commit-message or template comment recording the npm tarball URL and the exact one-time tarball SHA-256 used for vendoring; this makes future audits independent from the generated ledger.
- Ensure `verify_tree` also refuses directories under `fonts/`; the current file-set check is strong, but an unexpected subdirectory should fail for the same reason an unlisted file does.
- Add the vendored version directory name to the docs pin cross-check in 05-08, not only the path segment.

### Risk Assessment

**LOW.** The mechanism is appropriate for MIT-licensed static assets.

---

## 05-07

### Summary

Generated homework and board pages are correctly designed as metadata cards plus outbound links, avoiding report embedding and relative-link breakage. The plan is generally strong, but it needs better coverage of optional metadata and the same YAML-loading strictness issue.

### Strengths

- Absolute GitHub links avoid the MkDocs strict-mode failure mode for links pointing outside `docs/`; the report and README targets are real files under `homeworks/1_3-police-flasher/`.
- The board page’s `../homeworks/<id>.md` link is valid because both sides remain inside `docs/`.
- The plan protects authored content: `docs/decisions/README.md:1-26` is the decision index and is explicitly left untouched.
- Reusing the same six-column table template for `README.md` and `docs/index.md` directly enforces D-11.

### Concerns

- **MEDIUM — optional `report` behavior is undefined.** `schema/homework.schema.json:80-90` makes `report` optional, while the homework page always emits a Report link and the six-column table includes a Report cell. The plan defines missing `simulation` behavior but not missing `report` behavior; that can crash or emit a broken link.
- **MEDIUM — board loading should use the strict YAML loader.** The plan says `yaml.safe_load` for `boards/*.yaml`, but a duplicate `id` or `flash_mb` key can silently overwrite the earlier value; the repository already has the stricter mechanism in `scripts/metadata/contract.py:73-101`.
- **LOW — board id-versus-file stem mismatch needs a generator-side rule.** The checker will make the mismatch an ERROR after 05-02, but the generator should still refuse to generate a page path that disagrees with the profile id rather than relying on a separate gate.

### Suggestions

- Define missing `report` rendering now: either omit the cell, emit “none”, or render a placeholder link to the project. Add a schema-fixture test for each choice.
- Use `StrictSafeLoader` for board YAML and add a duplicate-key board-page test.
- Add a test that a board profile whose `id` does not match its file stem causes an exit-2 environment error from the generator as well.
- Add a real-tree assertion that no generated page contains `../../` before the strict build is introduced in 05-08.

### Risk Assessment

**MEDIUM.** Page shape and link policy are correct; optional metadata and YAML strictness need tightening.

---

## 05-08

### Summary

Generating the whole `mkdocs.yml` from a reviewed template is the right move, and the nav-completeness test is valuable. The plan’s main implementation detail to clarify is heading extraction from ADR files, because every real ADR starts with YAML frontmatter.

### Strengths

- The existing docs tree really has a small, finite Markdown set: `docs/decisions/` contains eleven ADR files plus `README.md`, so the generated nav can cover the whole tree without a nav plugin.
- The plan’s explicit `- "<label>": <path>` nav shape and the `nav_targets()` check directly target the common MkDocs YAML scalar failure.
- Keeping `omitted_files: warn` plus a generated Decisions section keeps `--strict` meaningful, rather than weakening strict validation to make a hand-maintained nav pass.
- Pin consistency is implemented without PyYAML or subprocess, preserving the stdlib-only test policy.

### Concerns

- **MEDIUM — ADR heading extraction must account for frontmatter.** Every ADR begins with `---`, as shown by `docs/decisions/0001-monorepo-with-independent-projects.md:1-2`. “First ATX heading” is likely intended to mean the first heading after frontmatter, but the plan should say so; otherwise an implementation that scans the first line or mishandles frontmatter can produce a wrong nav label.
- **MEDIUM — the line-based nav completeness regex can become brittle.** It is fine for the generated template, but it assumes every target has no spaces or quoted characters. That is true for ASCII homework paths, but should be explicitly part of the template contract.
- **LOW — strict build remains an external command, not a generator invariant.** That is correct by design, but CI must run it separately; the plan should not imply that `nav --check` proves the site builds.

### Suggestions

- Specify that the decision-label extractor skips YAML frontmatter and then finds the first `# ` heading; add one ADR fixture with and without a frontmatter block.
- Add a test that a title containing a double quote is escaped by replacing it with a single quote, exactly as planned; include a test for a title containing a colon as well.
- Make strict build a named CI step in 05-09 and keep it separate from drift checking.
- Extend `PinConsistencyTests` to assert the exact `0.19.0` directory name and the CSS reference, not just the path segment.

### Risk Assessment

**MEDIUM–LOW.** The config architecture is strong; frontmatter handling is the main implementation ambiguity.

---

## 05-09

### Summary

The gate and deployment workflow plan matches the repository’s existing CI style and the required Pages model. It has two enforcement points and no matrix. Its blocker is the same generator dependency mismatch: PyYAML-only environments cannot import the planned `gen_views.py`.

### Strengths

- The house workflow style is real: `.github/workflows/homework.yml:7-12` uses read-only permissions and concurrency, and `.github/workflows/homework.yml:20-33` already pins checkout/setup-python by commit SHA.
- The `AGENTS.md` corrections target both stale lines: `AGENTS.md:39` and `AGENTS.md:192` both still say Phase 5 for `docs/standards/`.
- `gen-views-check` is check-only, which satisfies D-21 and keeps the drift gate honest.
- Splitting drift and docs workflows is cleaner than trying to skip a Pages deploy on pull requests inside one workflow.

### Concerns

- **HIGH — the PyYAML-only hook will fail on the current plan’s generator imports.** `gen-views-check` is specified with `additional_dependencies: ["PyYAML==6.0.3"]`, and the CI job installs only PyYAML. But `scripts.metadata.contract` imports `yaml` plus `Draft202012Validator` at `scripts/metadata/contract.py:44-46`, and 05-03 explicitly imports that module. The hook/CI environments therefore need either a stdlib-only split or a jsonschema dependency.
- **MEDIUM — no drift-hook test covers stale output that is not a one-byte edit.** The probe edits `mkdocs.yml`, which is good, but the hook should also be tested against a manifest-only drift and an orphaned generated file if `--all --check` is expected to catch all four drift classes.
- **LOW — docs deploy needs the repository’s Pages setting change, which the plan correctly records, but should also be verified before the first production run.** A dry-run or feature-branch `workflow_dispatch` against a non-production Pages configuration is not possible for `deploy-pages`, so the setup step needs an explicit maintainer checklist.

### Suggestions

- Fix the contract/module split before executing this plan; the cleanest option is to move `resolve_root`, `relative_path`, and `derive_parts` into a stdlib-only module and import that from `gen_views.py`.
- Add a test that the generated-views workflow JSON has exactly `contents: read`, one job, no matrix, and no step other than the check.
- Add a test that the docs workflow’s LFS guard fails when a synthetic `site/` file contains the LFS marker, in addition to simply grepping the workflow YAML.
- Preserve `AGENTS.md` quick-start semantics as planned, but add the Pages one-time setup to the PR template or repository onboarding note if one exists later.

### Risk Assessment

**HIGH.** Workflow permissions and deployment are well-designed, but the PyYAML-only environment cannot run the generator as currently planned.

---

# Cross-plan assessment

The dependency ordering is coherent, and the plans collectively cover META-05 through META-08 without adding a premature Phase 8 matrix. However, execution should address three points first:

1. **Contract-import / dependency mismatch.** `scripts/metadata/contract.py:44-46` imports PyYAML and jsonschema, while the generator, pre-commit hook, and CI job are specified to carry only PyYAML. Fix this in Wave 0 by splitting pure metadata helpers or explicitly updating the dependency policy.
2. **Top-level `tests/` consumer omission.** `tests/platformio.ini:25-29` consumes shared libraries but `affected.py` only scans `homeworks/*/`. Phase 8 would otherwise build changed homeworks without rebuilding/running the shared-library native suite.
3. **YAML duplicate-key strictness.** The repository already has `StrictSafeLoader` at `scripts/metadata/contract.py:73-101`; generated-view and board-profile loaders should reuse it rather than allowing `yaml.safe_load`.

With those corrections, the plans are high quality and substantially lower-risk than a hand-maintained generated-view system.


---

## Antigravity Review

# Architecture and Implementation Review: Phase 05 — Generated Views and Documentation Site

This review evaluates the nine implementation plans for Phase 05 against the live codebase at `/Users/vloktiev/Dev/miltech/homeworks`. Claims, import structures, regexes, existing fixtures, and configuration patterns were checked against repository source files.

---

## 05-01

### Summary
Plan 05-01 establishes the shared foundation for Phase 05 by extracting duplicate template rendering logic (`_render`, `_read_text`) from `scripts/new_homework` into `scripts/metadata/render.py` and `platformio.ini` parsing routines (`_option`, `_extends_targets`, `_dep_names`) from `scripts/check_architecture.py` into `scripts/metadata/platformio.py`. It creates `scripts/metadata/errors.py` to decouple the shared `CheckError` class from heavy third-party dependencies, provides the Wave 0 test fixture builder (`write_synthetic_root` in `scripts/tests/temp_root.py`), and pins the documentation dependencies in `requirements-docs.txt`.

### Strengths
- **Clean separation of `CheckError` (`scripts/metadata/errors.py`)**: Moving `CheckError` out of `scripts/metadata/contract.py` (which imports `yaml` at line 44 and `jsonschema` at line 45) allows stdlib-only modules and tests (`scripts.metadata.render`, `scripts.metadata.platformio`, and `scripts/tests/`) to raise and catch the shared exception without violating the project's dependency isolation policy (04/D-14).
- **Preservation of critical review fixes**: `scripts/check_architecture.py:438-444` (the `native` PREFIX check from code review WR-03) and lines 471-489 (the `name=symlink://` alias extraction from code review CR-01) are preserved verbatim in `scripts/metadata/platformio.py`, preventing regression of previously audited architectural boundaries.
- **Single-pass placeholder substitution contract**: The plan explicitly tests that `render(text, mapping, display)` operates in a single pass, preventing template injection if a metadata value contains a placeholder string like `{{homework_id}}`.

### Concerns
- **Missing re-export of `CheckError` in `scripts/check_architecture.py`** *(Severity: MEDIUM)*:
  In `scripts/check_architecture.py:140`, `CheckError` is defined at module scope. If existing or external tests catch `scripts.check_architecture.CheckError`, deleting the class without re-exporting it (`from scripts.metadata.errors import CheckError`) could cause `AttributeError` or unhandled exceptions.
- **Partial extraction of shared utilities leaves a transitively imported dependency trap** *(Severity: HIGH)*:
  Plan 05-01 extracts `render.py` and `platformio.py` to be stdlib-only. However, in Plan 05-03, `scripts/gen_views.py` is created with dependencies declared only as `["PyYAML==6.0.3"]`, but it imports `derive_parts`, `resolve_root`, and `relative_path` from `scripts.metadata.contract`. In `scripts/metadata/contract.py:45`, `from jsonschema import Draft202012Validator` is executed at module import time. In an environment without `jsonschema` installed, any script importing `contract.py` crashes with `ModuleNotFoundError`. Plan 05-01 should extract `resolve_root`, `relative_path`, and `derive_parts` (from `scripts/metadata/contract.py:380-430`) into a dependency-free helper module (e.g. `scripts/metadata/paths.py`).
- **`extra_configs` multi-entry and comment handling** *(Severity: LOW)*:
  In `preload_extra_configs(parser, project_dir, display)`, resolving comma- and whitespace-separated entries must strip inline comments (PlatformIO INIs frequently use `;` comments, as seen in `homeworks/1_3-police-flasher/platformio.ini:1-3`).

### Suggestions
- Ensure `scripts/check_architecture.py` re-exports `CheckError` from `scripts.metadata.errors`.
- Extract `derive_parts`, `resolve_root`, and `relative_path` out of `scripts/metadata/contract.py` into a lightweight, stdlib-only module (`scripts/metadata/paths.py`) in Plan 05-01 so downstream generator scripts (`gen_views.py` and `affected.py`) do not import `contract.py` and trigger its top-level `jsonschema` import.
- In `preload_extra_configs`, strip trailing comments (lines or tokens containing `;` or `#`) before path resolution.

### Risk Assessment
**MEDIUM**. The core extractions and test fixture additions are well isolated, but the failure to isolate `derive_parts` and path utilities from `contract.py` creates a critical runtime dependency flaw for downstream plans.

---

## 05-02

### Summary
Plan 05-02 defines the machine-readable schema for board profiles (`schema/board-profile.schema.json`) using JSON Schema draft 2020-12, copies the verified `templates/board-profile/profile.yaml` into `boards/esp32-s3-devkitc-1.yaml`, creates `scripts/metadata/board_profile.py`, and integrates board profile validation into `scripts/check_metadata.py` and the `check-metadata` pre-commit hook.

### Strengths
- **Single checker architecture preserved (D-27)**: Rather than introducing a second CLI tool, `scripts/check_metadata.py` remains the single validation entry point for all repository metadata, preserving the 0/1/2 exit-code semantics and the `--json` output format.
- **Strict schema definition without `format` keywords**: In alignment with `test_homework_metadata.SchemaShapeTest`, the schema avoids the non-enforcing `"format": "uri"` keyword and uses an anchored regex (`^https://[^\s]+$`) for `pinout_url`, `additionalProperties: false`, and an explicit enum array for `frameworks`.
- **Tolerant handling of absent `boards/` directory**: By returning an empty list when `boards/` is absent, the plan ensures existing test fixtures in `scripts/tests/test_homework_metadata.py` (which only copy `schema/` and `platformio.shared.ini` via `scripts/tests/temp_root.py`) do not break.

### Concerns
- **CLI Positional Path Collision in `check_metadata.py`** *(Severity: MEDIUM)*:
  In `scripts/check_metadata.py:153-174`, `_directories(root, positionals)` handles positional arguments by assuming any file argument is a child of a homework directory:
  ```python
  if candidate.is_file():
      candidate = candidate.parent
  ```
  If a developer or script runs `uv run scripts/check_metadata.py boards/esp32-s3-devkitc-1.yaml`, `candidate.parent` becomes `boards/`. In `_validate_directory(root, directory)` (`scripts/check_metadata.py:87-100`), it looks for `boards/homework.yaml` and `boards/task.md`, neither of which exists, resulting in a spurious validation error: `"directory contains neither homework.yaml nor task.md"`. Furthermore, if `args.paths` is passed (e.g. targeting a single homework directory), `_board_documents(root)` will either run unconditionally (ignoring the positional filter) or fail to validate specified board files.
- **Duplicate loader logic** *(Severity: LOW)*:
  The plan notes that `scripts/metadata/board_profile.py` should parse YAML with duplicate-key detection. `scripts/metadata/contract.py:180-220` already defines a custom YAML constructor (`_UniqueLoader`) for detecting duplicate keys and capping input bytes (`MAX_INPUT_BYTES`). Re-implementing or bypassing this loader in `board_profile.py` risks divergence in error formats.

### Suggestions
- Update `scripts/check_metadata.py`'s positional argument routing in `main()` to partition `args.paths` into board paths (matching `boards/` or board schema) and homework paths (matching `homeworks/` or directory structures), passing the respective subsets to `_board_documents` and `_directories`.
- Import and reuse `_UniqueLoader` and `MAX_INPUT_BYTES` from `scripts.metadata.contract` in `board_profile.py`.

### Risk Assessment
**LOW**. The schema design, pre-commit hook extension, and test cases are tight and follow established patterns. The positional CLI routing issue is easily addressed.

---

## 05-03

### Summary
Plan 05-03 constructs the core generator infrastructure in `scripts/gen_views.py`. It implements the `readme` view, splicing the six-column homework catalog table (`templates/views/homeworks-table.md.tmpl`) into `README.md` between marker comments, writes the initial `generated.manifest` ownership ledger, and establishes comprehensive drift detection (`--check`), orphan tracking, and atomic file replacements (`os.replace`).

### Strengths
- **Marker-bounded region protection (D-14)**: Authored prose in `README.md` is protected by strict delimiter boundaries (`<!-- BEGIN GENERATED: homeworks -->` and `<!-- END GENERATED -->`). The manifest hashes only the region content, ensuring changes to surrounding prose are not flagged as drift.
- **Strict symlink and traversal defenses**: By adapting `_component_conflict` from `scripts/new_homework:251-295`, every component of an output path is verified using `os.lstat` before reading or writing, preventing symlink traversal attacks.
- **Atomic write protocol**: File updates utilize temporary files in the destination directory (`.gen_views-*`) followed by `os.replace`, guaranteeing that files are never observed in a truncated or half-written state.
- **Gitignore un-ignoring of the manifest**: Adding `!generated.manifest` directly after `*.manifest` in `.gitignore` (which currently ignores `*.manifest` at line 253) properly tracks the ownership ledger.

### Concerns
- **`ModuleNotFoundError: No module named 'jsonschema'` at runtime** *(Severity: HIGH)*:
  Plan 05-03 specifies that `scripts/gen_views.py` has a PEP 723 dependency list of only `["PyYAML==6.0.3"]` because it reads metadata without validating it. However, the action specifies importing `contract.derive_parts`, `contract.resolve_root`, and `contract.relative_path` from `scripts.metadata.contract`. Because `scripts/metadata/contract.py:45` unconditionally executes `from jsonschema import Draft202012Validator`, running `uv run scripts/gen_views.py readme` in an environment containing only `PyYAML` fails immediately with `ModuleNotFoundError: No module named 'jsonschema'`.
- **Markdown table cell escaping does not sanitize link brackets** *(Severity: LOW)*:
  `_escape_cell` collapses whitespace and escapes pipes (`|` -> `\|`). In `_homework_rows`, the project title is formatted into markdown link syntax: `[<module>.<lesson> <title>](<path>)`. If a homework title contains square brackets `[` or `]`, the markdown link parser will break.

### Suggestions
- In Plan 05-01 / Plan 05-03, move `derive_parts`, `resolve_root`, and `relative_path` to a standalone module like `scripts/metadata/paths.py` that does not import `contract.py` or `jsonschema`. Alternatively, add `jsonschema==4.26.0` to `scripts/gen_views.py`'s dependency declaration and hook dependencies.
- Update `_escape_cell` to also escape or replace square brackets (`[` and `]`) in fields that are interpolated into markdown link text.

### Risk Assessment
**MEDIUM**. The architectural design of the generator spine and manifest is exemplary, but the missing dependency resolution for `jsonschema` when importing `contract.py` is a blocking defect that must be fixed.

---

## 05-04

### Summary
Plan 05-04 creates `scripts/affected.py` and `scripts/tests/test_affected.py` to map repository diffs (`--paths-from`, `--base`, or working tree) to the CI build and simulation matrix (`{"build": [...], "simulate": [...]}`). It implements `lib/**` fanout to dependent homework projects via `lib_deps` and `library.json`, excludes native environments and `simulation.tool: none` projects from simulation, and provides a fail-safe rule that widens unrecognised shared paths to all projects.

### Strengths
- **Single source of truth for dependencies (D-23)**: Dependencies are resolved directly from `platformio.ini` `lib_deps` and `lib/<name>/library.json` using the shared parser module extracted in Plan 05-01, avoiding duplicate dependency manifests in `homework.yaml`.
- **Robust stream parsing and safety guards**: The CLI supports NUL-delimited input (`git diff -z`) and decodes with `surrogateescape`, preventing malformed filenames or non-UTF-8 characters from crashing the diff analyzer.
- **Clean output format separation**: Machine-readable JSON is emitted cleanly to stdout while diagnostics and errors are restricted to stderr, ensuring seamless consumption by GitHub Actions (`strategy.matrix: ${{ fromJson(...) }}`).

### Concerns
- **`NO_BUILD_IMPACT` omits repository-root documentation and generator files, causing full matrix rebuilds** *(Severity: HIGH)*:
  `NO_BUILD_IMPACT` is defined in task 1 as:
  ```python
  NO_BUILD_IMPACT = (".planning/", "docs/", ".github/", "README.md", "AGENTS.md", "LICENSE")
  ```
  However, Phase 05 introduces or modifies several repository-root files that have no firmware build impact: `generated.manifest`, `mkdocs.yml`, `requirements-docs.txt`, `homeworks.code-workspace`, and `templates/views/`. Under the plan's fail-safe rule ("anything else widens to every project"), any PR that regenerates views (which always updates `generated.manifest`), edits `mkdocs.yml`, or updates `requirements-docs.txt` will trigger a full rebuild of every homework assignment in CI.
- **Transitive library dependency resolution edge case** *(Severity: LOW)*:
  Currently, `lib/common/library.json` and `lib/port/library.json` carry no `dependencies` key (as confirmed in `lib/common/library.json:1-8`). While the plan acknowledges this (Pitfall 9) and notes that all current projects declare both `common` and `port` directly in their `platformio.ini` (e.g. `homeworks/1_3-police-flasher/platformio.ini:15-16`), the recursive expansion in `_consumers` must guard against circular dependencies in `library.json` using a `seen` set.

### Suggestions
- Expand `NO_BUILD_IMPACT` to include all documentation, configuration, and generator metadata files that do not affect compilation:
  ```python
  NO_BUILD_IMPACT = (
      ".planning/", "docs/", ".github/", "README.md", "AGENTS.md", "LICENSE",
      "mkdocs.yml", "requirements-docs.txt", "generated.manifest",
      "homeworks.code-workspace", "templates/views/", "boards/"
  )
  ```
- Ensure `_consumers` maintains a `seen` set when traversing `library.json` dependency chains to prevent infinite recursion on malformed circular dependencies.

### Risk Assessment
**MEDIUM**. The dependency resolution and diff parsing are well designed, but failing to include `generated.manifest` and docs files in `NO_BUILD_IMPACT` will cause unnecessary CI rebuilds on every view update.

---

## 05-05

### Summary
Plan 05-05 implements the two whole-file view generators: `homeworks.code-workspace` (the multi-root VS Code workspace) and `platformio.shared.ini` (the shared PlatformIO environment configurations). It replaces manual configuration with metadata projections, enforces pin consensus across all assignments, and eliminates two persistent manual friction points identified in Phase 4.2.

### Strengths
- **Editor compatibility and byte stability**: Generating `homeworks.code-workspace` with tab indentation (`\t`), distinct folder paths (`.`, `docs`, `lib`, `scripts`, and homeworks), and preserving the exact `extensions` block (`homeworks.code-workspace:10-18`) ensures that VS Code re-saving does not produce formatting noise or spurious git diffs.
- **Fail-closed pin disagreement contract**: Instead of picking an arbitrary pin when homeworks disagree on `toolchain.platform` or `toolchain.platformio`, the generator halts with exit code 1 and identifies all conflicting homeworks.
- **Preservation of critical SCons flags**: The five-line SCons comment and configuration in `platformio.shared.ini:27-30` are preserved verbatim in `templates/views/shared-ini.ini.tmpl`, ensuring native test builds on host toolchains remain intact.

### Concerns
- **Zero homework handling in `shared-ini` vs `workspace`** *(Severity: LOW)*:
  In `shared-ini`, zero homeworks exits 2 because no platform pin can be inferred. In `workspace`, zero homeworks keeps the four fixed roots (`.`, `docs`, `lib`, `scripts`). This distinction is sensible, but `temp_root.py` or synthetic test fixtures with zero homeworks could encounter unexpected failures if `--all` is run.
- **Non-ASCII character validation in paths** *(Severity: LOW)*:
  The plan mandates that all paths in `homeworks.code-workspace` must be ASCII. While `homework.schema.json` already restricts `id` to `^[0-9]+_[0-9]+-[a-z0-9-]+$`, checking `path.isascii()` explicitly in the generator provides defense-in-depth against unexpected directory names.

### Suggestions
- Ensure that `uv run scripts/gen_views.py --all` provides clear diagnostic messages if `shared-ini` exits 2 on an empty tree while other subcommands succeed.
- Add an explicit unit test verifying that `templates/views/shared-ini.ini.tmpl` and the generated `platformio.shared.ini` still pass `scripts.metadata.contract.read_shared_platform_pin(root)`.

### Risk Assessment
**LOW**. Both whole-file templates and their generation logic are well bounded, deterministic, and backed by strong consensus validation.

---

## 05-06

### Summary
Plan 05-06 vendors the KaTeX 0.19.0 math rendering distribution (24 static assets including 20 `.woff2` font files, CSS, JS, and auto-render extensions) into `docs/assets/vendor/katex/0.19.0/`, creates an authored glue script (`render-math.js`) for Material's `document$` subscription, establishes a committed `FILES.sha256` checksum ledger, and implements stdlib-only integrity and mutation discrimination tests in `scripts/tests/test_docs_pins.py`.

### Strengths
- **Elimination of build-time network dependency (D-07)**: Vendoring KaTeX guarantees that `mkdocs build --strict` runs offline, in hermetic CI environments, and is immune to upstream CDN outages or font 404s.
- **Negative discrimination testing (`KatexVendoringDiscriminationTests`)**: Recognizing that MkDocs does not validate the existence of assets referenced in `extra_css`/`extra_javascript` (Pitfall 4), the plan includes unit tests that mutate file bytes, remove fonts, and add unlisted files to verify that `verify_tree()` reliably fails when assets are tampered with.
- **Lightweight font selection**: By vendoring only modern `.woff2` fonts and omitting legacy `.woff` and `.ttf` fallbacks, the vendored footprint is kept under ~600 KB without sacrificing rendering quality in modern browsers.

### Concerns
- **Network availability during local task execution** *(Severity: LOW)*:
  Task 1 requires running `npm pack katex@0.19.0` or downloading from npm registry via `curl`. In sandboxed or offline environments without external internet access, the developer or subagent executing the task must have network access enabled during this initial acquisition step. Once committed, no network is ever needed again.
- **Handling of CRLF line endings in `FILES.sha256`** *(Severity: LOW)*:
  If git line-ending normalization (`core.autocrlf`) converts `FILES.sha256` on Windows checkouts, reading the file or checking hashes could produce trailing `\r` issues if parsed strictly by line splitting. Parsing should strip `\r`.

### Suggestions
- In `scripts/tests/test_docs_pins.py:read_ledger()`, explicitly use `read_bytes().decode("utf-8").splitlines()` or strip `\r\n` to prevent cross-platform checksum mismatches.
- Document that `FILES.sha256` must be marked with `-text` or `eol=lf` in `.gitattributes` if cross-platform checkouts are expected.

### Risk Assessment
**LOW**. Vendoring static assets with cryptographic verification is straightforward and eliminates a class of silent build and rendering failures.

---

## 05-07

### Summary
Plan 05-07 implements the `docs` subcommand of `scripts/gen_views.py`, generating the documentation pages from repository metadata: individual homework pages (`docs/homeworks/<id>.md`) with D-02 metadata cards, board specification pages (`docs/boards/<board-id>.md`) from `boards/*.yaml`, and the site home page (`docs/index.md`) integrating the shared six-column homework table with authored prose.

### Strengths
- **Absolute URLs for repository artifact links (D-02, Pitfall 3)**: Generated homework pages link to `report.md` and `README.md` via absolute GitHub URLs (`https://github.com/VLoktiev-EMB/homeworks/...`) rather than relative paths (`../../homeworks/<id>/report.md`), preventing MkDocs `--strict` from failing with missing doc file errors.
- **Single template for README and site index (D-11)**: Reusing `templates/views/homeworks-table.md.tmpl` across both `README.md` (relative links) and `docs/index.md` (absolute links) via the `link_style` parameter prevents visual and structural drift between GitHub and the documentation site.
- **Orphan file detection in docs directories**: Scanning `docs/homeworks/` and `docs/boards/` for unlisted `.md` files ensures that renamed or deleted homeworks and boards do not leave orphaned pages on the published site.

### Concerns
- **Missing `docs/index.md` on first generation run** *(Severity: MEDIUM)*:
  In task 3, `docs/index.md` is authored with a marker region before running `gen_views.py docs`. However, the plan specifies:
  `A region target that is absent on disk is an ERROR record (exit 1) and is never recreated, exactly as the readme view behaves.`
  If a clean clone or temporary test environment runs `gen_views.py docs` without `docs/index.md` already existing on disk, the command fails with exit 1. The test fixture builder (`write_synthetic_root` in `temp_root.py`) must be verified to scaffold a skeleton `docs/index.md` with markers so that generator tests do not fail unexpectedly.
- **Board profile pinout URL formatting in markdown table** *(Severity: LOW)*:
  In `templates/views/board-page.md.tmpl`, `pinout_url` is substituted into a two-column markdown table. If long URLs (such as Espressif's 100+ character user guide URLs in `templates/board-profile/profile.yaml:8`) are rendered as bare text, they degrade table readability on mobile devices.

### Suggestions
- Ensure `write_synthetic_root` in `scripts/tests/temp_root.py` scaffolds `docs/index.md` with authored prose and markers whenever `docs` view testing is requested.
- Format `pinout_url` as a clean markdown link (e.g. `[Official Pinout Diagram]({{pinout_url}})`) in `board-page.md.tmpl`.

### Risk Assessment
**LOW**. Page generation patterns are clean, strictly bounded, and isolate authored content from generated cards.

---

## 05-08

### Summary
Plan 05-08 delivers the site configuration generator (`gen_views.py nav`), rendering `mkdocs.yml` from `templates/views/mkdocs.yml.tmpl`. It constructs the complete four-section navigation tree (Home, Homeworks, Boards, Decisions) by scanning `docs/` and extracting titles from ADR ATX headings. It validates the configuration against the Zensical-compatible subset, builds the documentation site with `mkdocs build --strict`, and verifies pin consistency across `requirements-docs.txt`, `mkdocs.yml`, and vendored KaTeX in `scripts/tests/test_docs_pins.py`.

### Strengths
- **Single template ownership of `mkdocs.yml` (D-06)**: Rather than attempting virtual page generation (which Zensical explicitly ignores), the entire `mkdocs.yml` is generated and tracked under drift detection (`--check`), ensuring plugins, themes, markdown extensions, and navigation remain in sync.
- **Quoted YAML key formatting avoids syntax traps (Pitfall 1)**: Formatting every nav item explicitly as `- "<label>": <path>` ensures that labels containing colons or special characters parse as valid YAML key-value pairs rather than quoted scalar strings.
- **Automatic ADR nav generation prevents strict build failures (Pitfall 2)**: With `validation.nav.omitted_files: warn` under `--strict`, any unlisted markdown file fails the build. Scanning `docs/decisions/*.md` and extracting titles dynamically ensures that adding an ADR never breaks the documentation build.

### Concerns
- **ADR frontmatter parsing when extracting headings** *(Severity: MEDIUM)*:
  In `docs/decisions/`, every ADR file (e.g. `docs/decisions/0001-monorepo-with-independent-projects.md:1-8`) begins with YAML frontmatter bounded by `---`. The first `#` ATX heading occurs on line 9 or 10. The heading extractor in `_nav_entries` must scan line-by-line past the frontmatter block rather than reading only the first non-empty line of the file.
- **Subcommand name semantics (`nav` vs `mkdocs.yml`)** *(Severity: LOW)*:
  Subcommand `nav` generates the whole `mkdocs.yml` file, not just the `nav:` block. The plan documents this in the module docstring, but users running `gen_views.py --help` might find the name counter-intuitive.

### Suggestions
- Ensure the decision heading extractor specifically ignores frontmatter lines (between initial `---` and closing `---`) before searching for the first line matching `^#\s+(.+)`.
- In `scripts/tests/test_gen_views.py:NavTests`, include a test case with a decision file containing complex YAML frontmatter and a heading with quotes/special characters to verify heading extraction.

### Risk Assessment
**LOW**. The configuration skeleton has already been proven in local probes against the real repository tree, and the automated pin cross-checks provide strong regression protection.

---

## 05-09

### Summary
Plan 05-09 closes Phase 05 by integrating the drift verification gate into local development and CI. It adds the `gen-views-check` hook to `.pre-commit-config.yaml`, creates `.github/workflows/generated-views.yml` to fail PRs on drifted views, creates `.github/workflows/docs.yml` to strictly build and deploy the site to GitHub Pages via OIDC artifact upload on `main`, and corrects the two `AGENTS.md` lines that mis-scheduled `docs/standards/`.

### Strengths
- **Check-only gate prevents silent mutation (D-21)**: The pre-commit hook runs `python scripts/gen_views.py --all --check` with `pass_filenames: false` and never mutates or stages files, maintaining a clear separation between auditing and editing.
- **Secure GitHub Actions workflow design**: Both workflows follow the repository security baseline:
  - `permissions: contents: read` on PRs (no write privileges).
  - SHA-pinned action steps with version comments.
  - Zero repository secrets required.
  - Deployment uses OIDC (`id-token: write`, `pages: write`) and the `github-pages` environment rather than legacy `gh-pages` branch commits.
- **LFS pointer guard in deploy workflow (Pitfall 12)**: The docs workflow checks out with `lfs: false` and runs an explicit check failing the job if `site/` contains `git-lfs.github.com/spec/v1`, preventing broken binary pointers from reaching the public site.

### Concerns
- **Pre-commit and CI environment missing `jsonschema` dependency** *(Severity: HIGH)*:
  Plan 05-09 configures the `gen-views-check` hook with:
  ```yaml
  additional_dependencies: ["PyYAML==6.0.3"]
  ```
  and `.github/workflows/generated-views.yml` with:
  ```yaml
  run: python -m pip install PyYAML==6.0.3
  ```
  Because `scripts/gen_views.py` imports `scripts.metadata.contract` (which imports `jsonschema` at line 45), running `gen-views-check` in pre-commit or in CI will fail with `ModuleNotFoundError: No module named 'jsonschema'`.
- **`AGENTS.md` verification regex trap** *(Severity: LOW)*:
  In task 3, the verify command runs:
  ```python
  lines = [l for l in text.splitlines() if "docs/standards" in l]
  assert len(lines) == 2
  ```
  When updating the "Repository layout" section of `AGENTS.md` to describe the new `boards/` and `docs/` artifacts, the author must be careful not to introduce a third mention of `docs/standards/` in that paragraph, or this assertion will fail.

### Suggestions
- Either fix the import chain in Plan 05-01 / Plan 05-03 (by extracting path helpers to a stdlib-only module), or add `jsonschema==4.26.0` to both `additional_dependencies` in `.pre-commit-config.yaml` and the pip install step in `.github/workflows/generated-views.yml`.
- Ensure the description added to `AGENTS.md` does not accidentally reference `docs/standards/`.

### Risk Assessment
**MEDIUM**. The workflow security, pre-commit configuration, and documentation updates are high quality, but the `jsonschema` import error will block both pre-commit and CI until corrected.

---

## Cross-Plan Synthesis & Phase Goal Verification

### Phase Goal Achievement
The nine plans collectively satisfy all four requirements of Phase 05:
- **META-05**: Fulfilled via `scripts/gen_views.py` (`readme`, `workspace`, `shared-ini`, `nav`, `docs`), `generated.manifest`, and the CI/pre-commit `--check` gates.
- **META-06**: Fulfilled via `scripts/affected.py`, with dependency graph extraction from `platformio.ini` and `library.json`.
- **META-07**: Fulfilled via `homeworks.code-workspace` generation from `templates/views/workspace.json.tmpl`.
- **META-08**: Fulfilled via vendored KaTeX 0.19.0, strict MkDocs Material configuration, and `.github/workflows/docs.yml`.

### Key Recommendations Summary
1. **Resolve the `jsonschema` Transitive Import (Blocking)**:
   In Plan 05-01, extract `derive_parts`, `resolve_root`, and `relative_path` from `scripts/metadata/contract.py` into a new, stdlib-only module `scripts/metadata/paths.py`. This ensures `gen_views.py` can remain dependent only on `PyYAML==6.0.3` without triggering `scripts/metadata/contract.py:45`'s `jsonschema` import in pre-commit and CI.
2. **Correct `NO_BUILD_IMPACT` in `affected.py`**:
   In Plan 05-04, add `generated.manifest`, `mkdocs.yml`, `requirements-docs.txt`, `homeworks.code-workspace`, and `templates/views/` to `NO_BUILD_IMPACT` so that documentation updates do not trigger full firmware rebuilds across all 30 assignments.
3. **Handle Positional CLI Arguments in `check_metadata.py`**:
   In Plan 05-02, update `main()` in `scripts/check_metadata.py` to route positional board profile paths to `_board_documents()` rather than passing them to `_directories()`.


---

## Ollama Review

ollama review failed or returned empty output. stderr:

Raw response body:
The operation was aborted due to timeout
Diagnosis: ollama is an HTTP lane and carries no reasoning-effort setting.

---

## Consensus Summary

**Склад рев'ю:** два доказові (source-grounded) рев'ю — Codex і Antigravity; обидва покрили всі 9 планів. Лейн Ollama не дав результату (таймаут HTTP-запиту), тому до консенсусу не залучається. Усі твердження нижче перевірені по коду репозиторію.

### Agreed Strengths

- **Архітектура генератора (05-03) спирається на реальні механізми.** Модель plan-then-apply, atomic write і sorted records скопійовані з `scripts/new_homework`, а не вигадані: класифікація байтів без переходу по symlink, `os.replace` для атомарної заміни. Обидва рев'юери назвали 05-03 найсильнішим планом фази.
- **Витяг спільних модулів у 05-01 обраний правильно.** Винесення `CheckError` в `scripts/metadata/errors.py` і `platformio.ini`-читачів у `scripts/metadata/platformio.py` звільняє їх від `yaml`/`jsonschema` і зберігає правило 04/D-14 (stdlib-only тести). Обидва рев'юери підтвердили, що це знімає реальне зв'язування модулів.
- **Вендоринг KaTeX (05-06) закриває сліпу зону MkDocs.** `extra_css`/`extra_javascript` не валідуються збирачем навіть під `--strict`, тож `FILES.sha256` плюс тест на мутацію — єдиний реальний механізм цілісності. Обидва схвалили повноту перевірки (listed vs on-disk).
- **Безпековий дизайн CI (05-09) відповідає стилю репозиторію.** `contents: read` на PR, SHA-pinned дії, OIDC + `deploy-pages` замість `gh-pages`-гілки, check-only drift-хук. Обидва рев'юери визнали дизайн коректним.

### Agreed Concerns

1.  **HIGH / блокуюча — розбіжність між оголошеними залежностями генератора і його реальним графом імпортів.** `scripts/gen_views.py` оголошує лише `PyYAML` у PEP 723, але імпортує `scripts.metadata.contract`, який на module scope виконує `from jsonschema import Draft202012Validator` (`scripts/metadata/contract.py:44-46`). Той самий модуль тягне pre-commit-хук `gen-views-check` (`additional_dependencies: ["PyYAML==6.0.3"]`) і CI-джоба з `pip install PyYAML==6.0.3` — обидва впадуть з `ModuleNotFoundError: No module named 'jsonschema'`. Це зачіпає 05-01 (не витягнуто потрібні хелпери), 05-03, 05-05 та 05-09.
    **Рекомендація (однакова в обох):** у 05-01 витягти `resolve_root`, `relative_path`, `derive_parts` з `contract.py` у stdlib-only модуль (напр. `scripts/metadata/paths.py`) і імпортувати його з генератора та `affected.py`. Додавати `jsonschema` у генератор — гірший варіант: він тягне валідацію туди, де план свідомо її не робить.

2.  **MEDIUM — `yaml.safe_load` замість наявного strict-лоадера.** Репозиторій уже має захист від дубльованих ключів (`StrictSafeLoader` / `_UniqueLoader`, `scripts/metadata/contract.py:73-101`), бо PyYAML мовчки залишає останнє входження. Плани 05-02, 05-03 і 05-07 описують `yaml.safe_load` для board-профілів і метаданих — дубльований `title`, `psram` чи `pinout_url` пройде непоміченим. Потрібен strict-лоадер і тест на дубльований ключ.

3.  **MEDIUM — витяг заголовків ADR для `nav` мусить пропускати frontmatter.** Кожен ADR у `docs/decisions/` починається з `---`-блоку; перший `# `-заголовок іде за ним. Формулювання «перший ATX-заголовок» двозначне і дає хибні nav-мітки. Обидва рев'юери просять явно вказати «після frontmatter» і додати фікстуру з frontmatter і без нього.

4.  **MEDIUM/LOW — `preload_extra_configs` недоспецифікований.** Реальні шляхи — `../../platformio.shared.ini` (`homeworks/1_3-police-flasher/platformio.ini:6`) і `../platformio.shared.ini` (`tests/platformio.ini:6`). Потрібно зафіксувати: розв'язання відносно каталогу проєкту, а не кореня репо; обробка inline-коментарів (`;`/`#`); правила для кількох entries.

### Divergent Views

- **`affected.py` (05-04): два різноспрямовані, але сумісні зауваження.** Codex (HIGH) — множина «усіх споживачів» не включає верхньорівневий `tests/`-проєкт, який споживає `common`, `port`, `host` (`tests/platformio.ini:24-29`); зміна `lib/**` не вибере нативний Unity-набір. Antigravity (HIGH) — `NO_BUILD_IMPACT` замалий: `generated.manifest`, `mkdocs.yml`, `requirements-docs.txt`, `homeworks.code-workspace`, `templates/views/` не входять до нього, тож кожен PR на views тригерить повний rebuild усіх проєктів. Це не суперечність: перше — недобір споживачів, друге — перебір через fail-safe. Обидва треба закрити в одному контракті (`build`/`simulate` масиви + розширений `NO_BUILD_IMPACT`).
- **Оцінка ризику 05-02 і 05-09.** Codex: 05-02 MEDIUM, 05-09 HIGH. Antigravity: 05-02 LOW (наголос на позиційних аргументах `check_metadata.py`, які зараз завжди трактуються як homework-каталоги), 05-09 MEDIUM. Спільний блокер (`jsonschema`) обидва бачать однаково, різниця — у вазі другорядних пунктів.
- **05-07 `docs/index.md`.** Antigravity (MEDIUM) вважає ризиком те, що регіон-таргет, відсутній на диску, дає exit 1 — тож `write_synthetic_root` має створювати `docs/index.md` з маркерами. Codex цього не підняв, але підняв невизначену поведінку відсутнього `report` (`schema/homework.schema.json` робить його опційним). Обидва стосуються 05-07 і мають бути закриті в плані.

---
phase: 6
reviewers: [codex-glm, codex-beam, antigravity]
reviewed_at: 2026-10-26T10:32:53Z
plans_reviewed: [06-01-PLAN.md, 06-02-PLAN.md, 06-03-PLAN.md, 06-04-PLAN.md, 06-05-PLAN.md]
models:
  codex-glm: "glm-5.3-flash:cloud (reasoning=high)"
  codex-beam: "beam:cloud (reasoning=high)"
  antigravity: "gemini-3.8-flash-high"
model_sources:
  codex-glm: "pinned"
  codex-beam: "pinned"
  antigravity: "pinned"
---

# Cross-AI Plan Review — Phase 6

<!-- gsd:plan-revision-conflicts:begin -->
## Plan-Revision Conflicts

<!-- gsd:plan-revision-conflicts:end -->

> Note: codex-glm and codex-beam share the codex adapter; their consensus is cross-model, not cross-tool.

## Codex Review (codex-glm)

## 06-01

### Summary

This is the strongest of the five plans: the 60-file scope matches the actual tree, the check-only clang-format hook is based on a verified pre-commit mechanism, and the plan correctly couples template sources with their golden fixtures. The two-task tracer-then-scale structure is appropriate, and the build/test verification after include sorting is the right precaution for a whole-tree reformat.

### Strengths

- The formatting target is real: `git ls-files '*.c' '*.h' '*.cpp' '*.cc' '*.hpp' '*.ino'` currently returns exactly 60 tracked C/C++ files in this repository.
- The check-only hook correctly overrides the mirror’s default in-place behavior: `entry: clang-format --dry-run --Werror`, matching the requirement in D-04. The plan also explicitly asserts non-mutation through file comparison.
- The golden-fixture coupling is real and verified: `scripts/tests/test_new_homework.py:68-74` snapshots every file via `rglob("*")`, so dotfiles and reformatted template/golden files are both covered.
- The plan correctly adds `default_stages: [pre-commit]`; `.pre-commit-config.yaml:1-2` currently has no such key, so the pre-push all-stages default is a real risk.
- The `lib/common/src/hex.c` reference is appropriate: it exercises signed bitwise behavior later analyzed by `bugprone-signed-bitwise`, while still being a small formatting tracer.

### Concerns

- **MEDIUM — the `hex.c` reformat claim that it is already close to the D-02 shape is only partly true.** `lib/common/src/hex.c` uses 4-space indentation and a 120-ish line style, but many other library adapters use 2-space indentation, e.g. `lib/arduino/src/gpio.c`. That is acceptable for the broad pass, but Task 1 should not use `hex.c` as the main visual reference for the eventual tree-wide style.
- **MEDIUM — `SortIncludes` can change the order of framework and project includes even when they are already separated.** The plan’s build checks are the right mitigation, but it should require an explicit per-block include-order diff review in addition to the general whitespace review. `homeworks/1_3-police-flasher/src/main.cpp` includes `<Arduino.h>` before all quoted headers; a naive include sort should not merge those blocks, but this should be reviewed explicitly.
- **LOW — the `.clang-format` invariant test is text-based only.** It meets D-05, but it can be defeated by duplicate later overrides. A one-off stronger check can shell out to the pinned `clang-format --dump-config`; this can stay outside the mandatory stdlib test.

### Suggestions

- Make the Task 2 verify include one focused diff review command, e.g. `git diff --check -- lib/ homeworks/ tests/ templates/ scripts/tests/fixtures/golden/`, and require the diff to show either indentation/wrapping changes or include-block changes only.
- Add one explicit assertion that there is no `.editorconfig`, matching D-03 and preventing accidental reintroduction in the same phase.
- Keep the mechanical reformat and hook wiring in separate commits if review noise becomes large; the plan already allows this and it is the safer review path.

### Risk Assessment

**MEDIUM.** The design is sound and the scope is accurate, but a 60-file mechanical reformat is inherently high-review-noise. The local build/test gates reduce the risk substantially.

---

## 06-02

### Summary

This plan correctly addresses the hard multi-root editor-contract trap and the esp-clangd builtin-header pitfall. The generator-based workspace settings approach is supported by the existing generator architecture, and the wrapper discovery design is the right shape. The main residual risks are behavioral verification of clangd on the real project and a few shell/environment edge cases.

### Strengths

- The multi-root approach is well grounded: `templates/views/workspace.json.tmpl:1-13` is a generated whole-file template, while `scripts/gen_views.py:640-649` passes a closed mapping to `render()`. Adding a `settings` object there correctly keeps the generator as the owner.
- The plan correctly avoids `${...}` in the template while still emitting `${env:HOME}` in the generated output: `scripts/metadata/render.py:38-52` rejects `$...` only in the template text, not in mapping values.
- The scaffold claim is verified: `scripts/new_homework:147-176` walks every regular template file except `template.yaml`, including dotfiles, so `.clangd` can be added without touching the scaffold.
- The golden-tree coupling is real: `scripts/tests/test_new_homework.py:68-74` uses `rglob("*")`, and `scripts/tests/temp_root.py:353-383` includes dotfiles when regenerating fixtures.
- The wrapper threat model is appropriate: it forbids `**` and limits query-driver execution to PlatformIO toolchain binaries.

### Concerns

- **MEDIUM — `PLATFORMIO_CORE_DIR` can make the `--query-driver` value relative.** The plan says the two globs are absolute, but `PLATFORMIO_CORE_DIR` is not always absolute. If that environment variable is relative, `--query-driver="$PLATFORMIO_CORE_DIR/toolchain-*/bin/*,..."` violates D-17. The wrapper should resolve the base path to an absolute path or reject a relative value.
- **MEDIUM — `set -euo pipefail` can make the fallback path fragile if the lookup uses naïve command substitution.** Under `set -e`, `CLANGD=$(command -v esp-clangd)` in a `zsh`/`bash` replacement context can exit before checking the Espressif directory if `esp-clangd` is not on `PATH`. The wrapper tests should explicitly cover “not on PATH but present under `$HOME/.espressif`”.
- **MEDIUM — `clangd.path` points to `~/.local/bin/clangd-wrapper`, but `~/.local/bin` is not guaranteed to exist.** The exact command in the truth is `ln -sf ...`; on a clean macOS/Linux home this can fail. The guide should use `mkdir -p "$HOME/.local/bin" && ln -sf ...` while still presenting it as one logical setup step.
- **LOW — `Diagnostics.Suppress` suppresses both `unknown-argument` and `drv_unknown_argument` globally for that project.** That is justified for GCC-only Xtensa flags, but it could hide a genuinely wrong user-added compiler flag. ADR 0013 should call this tradeout out explicitly.
- **LOW — clangd behavior still needs the planned manual live verification.** The tests can prove configuration identity and wrapper behavior, but not that diagnostics disappear in the real Arduino and ESP-IDF IDE flows.

### Suggestions

- Add a `ClangdWrapperTests` case that sets a fake `esp-clangd` only under a temporary `~/.espressif` directory and omits it from `PATH`.
- Make Task 3 also assert, not only that the two settings objects are equal, but that `.vscode/settings.json` and the generated workspace have identical key sets—not just JSON deep equality, which already does that, but also that no cpptools key is accidentally deleted.
- Record the expected `clangd --check` result on `homeworks/1_3-police-flasher/src/main.cpp` in `06-VALIDATION.md`, not only in prose.

### Risk Assessment

**MEDIUM.** Architecture and repository mechanics are strong, but the wrapper and onboarding path have several small environmental edge cases that can turn into novice-facing failures.

---

## 06-03

### Summary

This plan covers the fast lint layer well and has accurate file-scope intent, but it contains one concrete correctness defect in the yamllint policy: the four remaining `truthy` findings are almost certainly the four GitHub workflows’ `on:` keys, which cannot be fixed by changing values. The ruff cleanup items are verifiable in source and are appropriate.

### Strengths

- The ruff fixes are source-backed. The three long lines are real: `scripts/affected.py:20,22,23`, with line 20 at 231 characters. The `zip` issue is real: `scripts/check_architecture.py:564`, and adding `strict=True` is safe because `matched` is built from the same-length `entries` list.
- The metadata re-export plan is accurate: `scripts/metadata/contract.py:55-65` imports six objects specifically for re-export, so an explicit `__all__` is the right way to satisfy `F401` without removing a public symbol.
- The unused-import cleanup is real: `scripts/tests/test_homework_metadata.py:30` imports `sys`, while a repository grep shows only that import line, not an actual use.
- A `[tool.ruff]`-only `pyproject.toml` is a valid decision; the PEP 723 scripts remain the dependency policy.
- The markdownlint exclusions correctly distinguish generated pages from authored docs and decisions, matching the generator ownership contract.

### Concerns

- **HIGH — the yamllint `truthy` fix is wrong for GitHub Actions.** The repo has four workflows, each with a top-level `on:` key: `.github/workflows/homework.yml:3`, `security.yml:3`, `generated-views.yml:3`, and `docs.yml:8`. yamllint commonly flags `on:` as a truthy key unless `truthy.check-keys: false` is set. The plan’s instruction to “fix the four `truthy` findings by writing `true`/`false` instead of `yes`/`no`/`on`/`off`” is therefore not implementable for these four findings. The policy should be:
  ```yaml
  truthy:
    check-keys: false
  ```
- **MEDIUM — the markdownlint backlog may include a few rule-specific false positives on existing ADR headings.** Existing ADRs intentionally repeat the same section headings, e.g. `docs/decisions/0001-monorepo-with-independent-projects.md:11` and `docs/decisions/0002-ports-and-adapters-no-universal-hal.md:11` both have “Context and Problem Statement”. If the measured `MD024` finding is the ADR template, the fix should be a per-directory `allow_different_nesting`/duplicate-heading policy or ADR-specific config, not generic prose edits that break the ADR format.
- **LOW — markdownlint will cover generated `docs/index.md`, `docs/homeworks/*`, and `docs/boards/*` only because the plan excludes those exact paths.** That is fine today, but future generated families will need the same policy update.

### Suggestions

- Change `.yamllint.yaml` to:
  ```yaml
  rules:
    truthy:
      allowed-values: ["true", "false"]
      check-keys: false
  ```
  and rename the task action from “fix four truthy findings” to “ignore YAML truthy keys for GitHub Actions”.
- Add a small policy test or explicit acceptance criterion that all four workflow files still contain valid `on:` keys after yamllint passes.
- For `MD024`, inspect the exact 11-finding list before editing; do not assume all findings are prose defects.

### Risk Assessment

**MEDIUM-HIGH.** The lint architecture is sound, but the yamllint truthy mistake would leave the plan unable to pass its own gate without either violating GitHub Actions syntax or adding a hidden exception.

---

## 06-04

### Summary

This plan correctly identifies the two hardest clang-tidy facts: cpp-linter-hooks skips locally without a database, and pre-commit’s default stages apply to all stages. The local database guard is a strong solution, and the staged test layering is appropriate. However, the scope of the changed-files pattern and the verification of actual clang-tidy execution leave gaps around headers and vacuous passes.

### Strengths

- The database location claim is real: `scripts/pio/compiledb.py:21-22` pins the database to `$PROJECT_DIR`, so `tests/compile_commands.json` is the correct database for the native suite.
- The current database really analyzes `lib/common` and `lib/host`: `tests/compile_commands.json` contains common sources, host sources, Unity, and `tests/src/main.c`, but no port implementation TU.
- The pre-push default-stage risk is real: `.pre-commit-config.yaml:1-2` currently declares only pre-commit, so adding pre-push without `default_stages: [pre-commit]` would run every hook on push.
- The guard-before-clang-tidy ordering is correct and should be enforced textually as planned.
- Fixing the signed bitwise sites in `lib/common/src/hex.c:48-49` and `hex.c:89` is preferable to `NOLINT`.

### Concerns

- **MEDIUM — the guard must specify how compile-command-relative paths are resolved.** `tests/compile_commands.json` contains both absolute paths and relative entries such as `.pio/libdeps/native/Unity/src/unity.c` and `src/main.c`. Relative entries are relative to `tests/`, not the repository root. If the guard resolves them against the repository root, it will falsely report a stale or missing database.
- **MEDIUM — `lib/port` headers are probably not directly analyzable by clang-tidy today.** The database has no port TU, and the plan’s hook pattern includes `lib/port/include/.*\.h`. If cpp-linter-hooks passes that header directly to clang-tidy, clang tooling may report “no compile command” and skip it. The plan records the native-test-TU gap but not this analogous port-header gap.
- **MEDIUM — `lib/common/include` and `lib/host/include` are not in the hook’s `files` pattern.** A header-only change can therefore skip both the guard and clang-tidy. If that is intentional, it should be stated; if not, it is a coverage gap.
- **MEDIUM — the clang-tidy verify can pass vacuously.** `pre-commit run clang-tidy --hook-stage pre-push --files lib/common/src/hex.c` can exit 0 with no diagnostics if cpp-linter-hooks filters to changed lines and there are no local changes. The plan asserts that cland-tidy “analyses the host libraries”, but the given command does not necessarily prove that.
- **LOW — `WarningsAsErrors: ""` is warnings-first, but the plan does not state how cpp-linter-hooks treats remaining warnings.** If any diagnostics appear on changed lines, the hook likely returns non-zero; if none appear, the gate is silent. The phase should record that distinction explicitly.

### Suggestions

- Resolve relative compile-command entries against `<root>/tests/`; add a unit fixture using both absolute and relative `file` entries, mirroring the real database shape.
- Either narrow the pre-push `files` pattern to TUs actually present in the database, or add a documented note that port and header-only changes are analyzed only indirectly when a related source TU also changes.
- Add one validation probe that proves clang-tidy is actually running: temporarily introduce a known warning into a disposable temp-root copy, or record the clang-tidy version + TU count in `06-VALIDATION.md`.
- Include `lib/common/include/**.h` and `lib/host/include/**.h` in the guard’s `files` pattern only if the plan also explains how diagnostics are surfaced from a header-only change.
- Add a `ClangTidyDbGuardTests` case with a compile database that names a missing relative path under `tests/`, proving the intended relative resolution.

### Risk Assessment

**MEDIUM-HIGH.** The guard concept is excellent and directly fixes the upstream hook’s local-skip behavior, but the changed-file scope and path-resolution details are under-specified and could make part of the gate either false-pass or false-fail.

---

## 06-05

### Summary

This plan closes the phase with the right documentation, ADR, navigation, and rulebook artifacts. The generator and docs gates are correctly integrated. The main missing onboarding step is the pre-push hook installation, and a few guide assertions are brittle.

### Strengths

- The strict-nav risk is real and correctly handled: `templates/views/mkdocs.yml.tmpl:14-25` uses an explicit `nav:`, `PinConsistencyTests` checks every `docs/**/*.md` target at `scripts/tests/test_docs_pins.py:447-479`, and `.github/workflows/docs.yml:58-59` runs `mkdocs build --strict`.
- ADR navigation is automatically generated: `scripts/gen_views.py:1102-1151` scans `docs/decisions/*.md`, so adding 0012/0013 will naturally require a regeneration of `mkdocs.yml` and `generated.manifest`.
- The decision-index structure matches the repo: `docs/decisions/README.md:10-30` uses the table-first model, and numbered ADR files already exist.
- The AGENTS edit location is correct: the rulebook currently declares only three enforcement tags at `AGENTS.md:77-78` and has `Secrets` at line 149 before `Assets and generated files` at line 162.
- The guide correctly avoids claiming a simulation path; that remains Phase 7.

### Concerns

- **MEDIUM — the guide omits `pre-commit install` from its explicit content contract.** D-10 relies on one `pre-commit install` wiring both stages. The guide’s exact machine steps list the symlink and compiledb generation, but not the hook installation, even though success criterion 5 is about the whole beginner setup. `RulebookAndGuideTests` should assert `pre-commit install`.
- **MEDIUM — the plan asserts the guide contains `pip`.** That is brittle and potentially contradictory with D-06, which forbids pip-user installs. If the goal is to document a caution, make the test assert a stronger phrase such as “Do not install linters with pip” or `pre-commit install`; asserting any occurrence of `pip` is too weak.
- **LOW — “exactly one machine-level setup step” is slightly overstated.** Installing VS Code, extensions, ESP-IDF/esp-clangd, and running `pre-commit install` are also machine-level. The guide can say “one repository-specific machine step” instead.
- **LOW — the generated decision nav will depend on the first `# ` heading after frontmatter.** The new ADRs must use the same frontmatter shape as 0010/0011 or the nav label can degrade from the filename fallback.
- **LOW — exact-substring tests for prose are useful smoke checks, but can become brittle.** Prefer asserting command substrings and required terms, not full sentences.

### Suggestions

- Add `pre-commit install` to the Task 1 content contract and to `RulebookAndGuideTests`.
- Replace the `pip` assertion with a direct assertion for `pre-commit install` and a negative assertion for Homebrew/apt/global pip.
- In the symlink command, use `mkdir -p "$HOME/.local/bin" && ln -sf "$PWD/scripts/clangd-wrapper.sh" "$HOME/.local/bin/clangd-wrapper"`.
- Add a checklist section to the guide summarizing the five pre-commit hooks and two pre-push hooks after Phase 6 is complete.

### Risk Assessment

**MEDIUM.** The documentation architecture is correct and the generated-site gates are strong, but the novice walkthrough is missing one essential hook-installation step and has two brittle verification assertions.

---

## Cross-Plan Assessment

### Dependency and sequencing

The wave ordering is mostly correct: the formatting hook must precede all later hook assertions; the lint layer precedes the clang-tidy layer; documentation follows both. A few cross-wave gaps remain:

- 06-02’s symlink command and 06-05’s guide content must agree exactly. If 06-05 changes `ln -sf` to `mkdir -p && ln -sf`, 06-02’s must-have should not hardcode the bare command.
- 06-04’s clang-tidy ADR language must include the port-header/database gap, not only the native-test-TU gap.
- 06-03’s yamllint policy must be corrected before 06-04, because `pre-commit run --all-files` will fail the whole later gate as soon as yamllint is wired.

### Most important review-blocking fixes

1. **06-03 HIGH:** set `truthy.check-keys: false` for GitHub workflows.
2. **06-04 MEDIUM-HIGH:** specify relative path resolution for compile-command entries and remove the vacuous-pass risk.
3. **06-02 / 06-05 MEDIUM:** make the wrapper symlink and guide agree on `mkdir -p "$HOME/.local/bin"` and include `pre-commit install`.

### Overall Conclusion

The plan set is unusually well grounded in repository reality and avoids speculative work. Most of the proposed mechanisms match actual code paths, generator ownership, test harnesses, and CI gates. The main issues are not architectural; they are narrow correctness defects in lint policy and hook-scope validation. Once those are fixed, the wave sequence should be able to deliver Phase 6 with LOW-to-MEDIUM residual risk rather than the current MEDIUM-HIGH.

---

## Codex Review (codex-beam)

> [reviewed-without-source-citations] This reviewer declared source-grounded evidence but cited no file:line source evidence, so it reviewed the pasted plan text only — down-weight its verdict in the Consensus Summary.

## 06-01

**Summary** — This plan lays down the formatting contract `.clang-format`, adds one check-only `mirrors-clang-format` hook, and performs a whole-tree mechanical reformat. It is well-scoped for Wave 1: 60 tracked C/C++ files matches the repository today, and the check-only hook semantics are correct. The main risks are operational (running an external wheel over 60 files) rather than design risks.

**Strengths**
- The hook entry override (`entry: clang-format --dry-run --Werror`) directly addresses the mirror's in-place default, which is the real failure mode for D-04.
- `default_stages: [pre-commit]` is introduced together with the hook, avoiding Pitfall 2 before later plans add pre-push hooks.
- The golden-tree coupling is explicit: templates and fixtures are formatted in the same pass, so `GoldenTreeTests` remains meaningful.
- `ClangFormatConfigTests` shells out through subprocess-style text checks and stays stdlib-only, consistent with 04/D-14.

**Concerns**
- **MEDIUM — single-pass mechanical failure.** If `SortIncludes: true` breaks a build, the plan tells the executor to report rather than patch, but there is no recorded fallback ordering or a way to isolate the breakage to one file. Build success should be verified incrementally.
- **LOW — test placeholder breadth.** `ClangFormatConfigTests` asserts key substrings but the plan does not pin a full resolved-config assertion (e.g. `clang-format --dump-config` output). This leaves a gap if an unknown key is silently ignored by 23.1.3.

**Suggestions**
- Run the build after formatting each group (`lib`, then `tests`, then homeworks), not only once at the end.
- Optionally strengthen the test to invoke `clang-format --dump-config` and assert resolved values.

**Risk Assessment** — MEDIUM. The main exposure is a wide mechanical diff with include reordering; everything else is configuration.

---

## 06-02

**Summary** — This plan delivers esp-clangd configuration, the wrapper, and the generator-owned editor contract. The central deviation from the original D-19, D-19a, is justified by the multi-root settings scope trap and is the most valuable correction in the phase. Plans to add `.clangd` to five locations keep the golden/scaffold contract intact.

**Strengths**
- Correctly identifies that a root `.vscode/settings.json` does not reach other workspace roots, and emits the same object into `workspace.json.tmpl`.
- `BuiltinHeaders: QueryDriver` is the specific fix needed for esp-clangd 21.1.3's missing resource headers, and the plan frames it so the ADR records the caveat.
- Wrapper resolution order and bounded `--query-driver` globs are testable and leak no machine-specific paths.
- The renderer constraint (`${...}` rejected in template text, mapping value emitted verbatim) is explicitly respected; `clangd.path` is emitted literally through `{{clangd_wrapper_path}}`.

**Concerns**
- **HIGH — `${workspaceFolder}` must not leak.** If the template ever contains `${workspaceFolder}` in text it will be rejected by `DOLLAR_BRACE`. The plan avoids this by using `${env:HOME}`, which is supported. The reviewer should verify the committed template never includes `${workspaceFolder}`.
- **MEDIUM — symlink as a manual step.** A single `ln -sf` step is acceptable but is an implicit failure point; the drift test cannot detect that the user did not create it.

**Suggestions**
- Record the symlink command in both the guide and the wrapper's missing-binary message.
- Keep `clangd.path` out of the folder `.vscode/settings.json` duplicated value plan? The plan mirrors the same object; fine.

**Risk Assessment** — MEDIUM. The multi-root behavior itself is outside automated test reach, so the drift test only proxies.

---

## 06-03

**Summary** — This plan adds ruff, yamllint, markdownlint as check-only hooks and clears their backlogs. The scoped file lists match D-11/D-14. The risk is that the backlog cleanup is larger than estimated.

**Strengths**
- Exact revs for all three tools follow D-06; no system installs.
- `ruff-check` is used rather than `ruff-format`, avoiding a second mechanical diff.
- Generated pages are explicitly excluded, leaving `gen_views.py --check` as the owner.
- A root `pyproject.toml` without `[project]` was verified not to make the repo a uv project.

**Concerns**
- **MEDIUM — un-scoped long lines.** Only `scripts/affected.py`, `check_architecture.py`, and `contract.py` are named for ruff cleanup, but ruff can surface `E501` in other Python files. The plan defers to "fix any other finding", which is adequate if the implementer actually runs the hook.
- **LOW — yamllint truthy misconfiguration.** Setting `allowed-values: ['true', 'false']` redefines valid truthies rather than allowing default booleans. If no documented examples exist, this may reject intended YAML. Verify against the actual four findings.

**Suggestions**
- Run `ruff check` across the tree before making edits to get the full backlog.
- Double-check yamllint's truthy configuration against the four offending files.

**Risk Assessment** — MEDIUM. The design is sound; execution risk is the breadth of cleanup.

---

## 06-04

**Summary** — This plan introduces the pre-push static-analysis layer: a pinned `cpp-linter-hooks` clang-tidy, a DB guard, D-07a's scope narrowing, and the seven `hex.c` fixes. It correctly addresses the cpp-linter-hooks "skip locally on missing DB" inversion with a guard placed first.

**Strengths**
- The guard exits non-zero with the exact regeneration command and never generates or writes files.
- `default_stages: [pre-commit]` plus explicit `stages: [pre-push]` on both hooks enforces layering.
- `portability-avoid-pragma-once` is disabled rather than converting 11 headers, a pragmatic choice recorded in the ADR.
- `hex.c` fixes use explicit casts, preserving behavior, rather than suppressing diagnostics.

**Concerns**
- **HIGH — guard before clang-tidy ordering.** Pre-commit runs repos in file order; the plan specifies the local guard block above `cpp-linter-hooks`. This must be verified in the final file.
- **MEDIUM — native test TUs remain uncovered.** D-08a records the gap and defers database generation for tests to Phase 8. This satisfies success criteria but leaves user expectation risk; the ADR/guide must say so clearly.

**Suggestions**
- Include a guard test that temporarily renames the DB and asserts the exact command and exit code.
- Make sure the guard exists at `scripts/clang-tidy-db` with a usable entry in pre-commit (shebang and executable mode).

**Risk Assessment** — MEDIUM. Configuration correctness is the make-or-break part.

---

## 06-05

**Summary** — This plan authors the onboarding guide, creates two ADRs, updates `AGENTS.md`, and adds tests. It completes the phase's social/documentation deliverables. The key operational step is adding the `Standards` nav entry without hand-editing generated files.

**Strengths**
- The guide's required content matches TOOL-04 and avoids promising simulation, which belongs to Phase 7.
- ADR 0012/0013 record the two non-obvious decisions with the repository's six-section MADR skeleton.
- Two decision-table rows dated 2026-10-26 satisfy AGENTS.md's default-row rule.
- `AGENTS.md` gains a fourth enforcement point and a Routing-table entry, as required.

**Concerns**
- **HIGH — `RulebookAndGuideTests` asserts the substring `pip`.** Given D-06 explicitly forbids pip installs, this assertion appears contradictory and could force the guide to mention a forbidden method. Consider changing the assertion to absence or a distinguishing phrase.
- **MEDIUM — keep ADR bodies stable.** The plan warns against rewriting them; this is governance, not code risk, but a reviewer should enforce it.
- **LOW — generated manifest regeneration.** Must happen through `gen_views.py --all` only; a hand edit fails the drift hook.

**Suggestions**
- Replace the `pip` substring assertion with checks for "pre-commit" and "no Homebrew" or similar.
- Verify the strict `mkdocs build --strict` succeeds once the Standards page exists and is named in nav.

**Risk Assessment** — MEDIUM. Documentation and navigation correctness is a gate-level risk.

---

## Antigravity Review

> [reviewed-without-source-citations] This reviewer declared source-grounded evidence but cited no file:line source evidence, so it reviewed the pasted plan text only — down-weight its verdict in the Consensus Summary.

## 06-01

### Summary
Plan 06-01 establishes the foundational formatting contract for the repository. It introduces `.clang-format` based on LLVM with specific overrides matching decision D-02 as a documented approximation of ESP-IDF style, configures a check-only pre-commit hook via `mirrors-clang-format` v23.1.3, applies a one-time mechanical reformat across all 60 tracked C/C++ files (including template sources and golden test fixtures), and validates configuration invariants with stdlib-only unit tests (`ClangFormatConfigTests`). The plan is sound, well-bounded, and directly satisfies the formatting portion of TOOL-01 and Success Criterion 1.

### Strengths
- **Rigorous Check-Only Hook Design**: The pre-commit hook configuration overrides `entry: clang-format --dry-run --Werror` in [.pre-commit-config.yaml](file:///Users/vloktiev/Dev/miltech/homeworks/.pre-commit-config.yaml), preventing the default in-place modification (`clang-format -i`) from silently staging or masking dirty working trees.
- **Atomic Template & Golden Synchronization**: The plan formats [templates/homework-arduino/src/main.cpp](file:///Users/vloktiev/Dev/miltech/homeworks/templates/homework-arduino/src/main.cpp) and [scripts/tests/fixtures/golden/homework-arduino/src/main.cpp](file:///Users/vloktiev/Dev/miltech/homeworks/scripts/tests/fixtures/golden/homework-arduino/src/main.cpp) in the exact same pass with the pinned wheel (`clang-format==23.1.3`), preventing drift failures in [scripts/tests/test_new_homework.py#L110-L134](file:///Users/vloktiev/Dev/miltech/homeworks/scripts/tests/test_new_homework.py#L110-L134) (`GoldenTreeTests.assert_golden`).
- **Stdlib-Only Invariant Enforcement**: `ClangFormatConfigTests` validates D-02 keys (`IndentWidth: 4`, `ColumnLimit: 120`, `UseTab: Never`, `AfterFunction: true`, `ReflowComments: false`) via plain text reading without importing `yaml` or external dependencies, adhering strictly to rule `04/D-14`.
- **Pre-Commit Stage Guarding**: Setting `default_stages: [pre-commit]` in [.pre-commit-config.yaml](file:///Users/vloktiev/Dev/miltech/homeworks/.pre-commit-config.yaml#L1-L3) fixes the default pre-commit behavior where hooks run across all stages, ensuring fast commit feedback without leaking into pre-push.

### Concerns
- **Shell Pipeline Syntax in Task 2 Action** *(Severity: LOW)*: Task 2 states: `git ls-files '*.c' '*.h' '*.cpp' '*.cc' '*.hpp' '*.ino' piped to uvx --from clang-format==23.1.3 clang-format -i`. Running `clang-format -i` with filenames piped directly into stdin (without `xargs`) causes `clang-format` to format standard input and write to standard output rather than modifying the files in-place on disk. The command must use `xargs` (e.g. `git ls-files ... | xargs uvx --from clang-format==23.1.3 clang-format -i`).
- **Blame Attribution Disruption** *(Severity: LOW)*: A single mechanical reformat across all 60 tracked C/C++ files will touch almost every line of code in `lib/`, `tests/`, and `homeworks/1_3-police-flasher/`. While accepted in decision D-01, the plan does not establish a `.git-blame-ignore-revs` mechanism to keep `git blame` legible for future contributors.

### Suggestions
- Ensure Task 2 specifies `git ls-files ... | xargs uvx --from clang-format==23.1.3 clang-format -i` explicitly to avoid execution stalls.
- Consider creating a `.git-blame-ignore-revs` file committing the SHA of the tree reformat so contributors can configure git to ignore the whitespace commit during blame traversal.

### Risk Assessment
**LOW**. The scope is tightly bounded to formatting and configuration. The templates contain no `{{...}}` tags in C/C++ source files, verified tracked file count is exactly 60, and existing native and target test suites verify compilation neutrality.

---

## 06-02

### Summary
Plan 06-02 implements the language server integration for ESP32-S3 development. It adds a standardized `.clangd` fragment with `CompilationDatabase: .` and `BuiltinHeaders: QueryDriver` to both homework templates, both golden fixtures, and `homeworks/1_3-police-flasher/`. It delivers `scripts/clangd-wrapper.sh` to resolve `esp-clangd` dynamically with bounded `--query-driver` globs, updates the generator `templates/views/workspace.json.tmpl` to emit workspace `settings`, mirrors this contract to `.vscode/settings.json`, and adds verification tests (`ClangdConfigTests`, `ClangdWrapperTests`, `EditorContractTests`).

### Strengths
- **Resolution of Built-in Header Trap**: Requiring `BuiltinHeaders: QueryDriver` in `.clangd` solves the issue where `esp-clangd` 21.1.3 ships without resource headers, extracting `<stdbool.h>` and `<stdint.h>` from the queried GCC driver without hardcoding transient package paths.
- **Clean Generator Placeholder Isolation**: The plan respects [scripts/metadata/render.py#L28-L42](file:///Users/vloktiev/Dev/miltech/homeworks/scripts/metadata/render.py#L28-L42) (`DOLLAR_BRACE` check that rejects `${...}` in templates) by placing `{{clangd_wrapper_path}}` in [templates/views/workspace.json.tmpl](file:///Users/vloktiev/Dev/miltech/homeworks/templates/views/workspace.json.tmpl) and injecting `${env:HOME}/.local/bin/clangd-wrapper` via the mapping dict in [scripts/gen_views.py#L640-L650](file:///Users/vloktiev/Dev/miltech/homeworks/scripts/gen_views.py#L640-L650) (`_render_workspace`).
- **Multi-Root Scope Correction (D-19a)**: Addresses the VS Code multi-root limitation where `.vscode/settings.json` only applies to the root folder, ensuring settings (`C_Cpp.intelliSenseEngine: "disabled"`, format on save via clangd) reach individual homework roots via `homeworks.code-workspace`.

### Concerns
- **Novice Directory Prerequisite Failure** *(Severity: MEDIUM)*: The onboarding instructions and wrapper path rely on `ln -sf "$PWD/scripts/clangd-wrapper.sh" "$HOME/.local/bin/clangd-wrapper"`. On clean macOS or Linux environments, `~/.local/bin` does not exist by default. Running `ln -sf` without `mkdir -p "$HOME/.local/bin"` will fail with `No such file or directory`, halting beginner onboarding.
- **Pipefail Trap in `scripts/clangd-wrapper.sh`** *(Severity: MEDIUM)*: Task 2 mandates `set -euo pipefail`. If the wrapper searches for the binary using `ls -d "$HOME"/.espressif/tools/esp-clangd/esp-*/esp-clangd/bin/clangd 2>/dev/null | sort -V | tail -1`, and no `esp-*` directory exists, `ls` exits with non-zero status (1). Under `set -e -o pipefail`, the pipeline fails immediately, causing the wrapper script to abort at that line rather than falling through to print the helpful diagnosis and exit with code 2 as intended.
- **Concurrency on Shared Output** *(Severity: LOW)*: Task 3 regenerates `homeworks.code-workspace` and `generated.manifest`. Because Wave 2 runs 06-02 and 06-03 in parallel, if 06-03 were also to touch views or manifest, race conditions could arise. However, inspection confirms 06-03 does not edit views, and manifest updates are isolated.

### Suggestions
- In `scripts/clangd-wrapper.sh`, avoid `ls | sort` under `pipefail`. Use safe globbing:
  ```bash
  candidates=("$HOME"/.espressif/tools/esp-clangd/esp-*/esp-clangd/bin/clangd)
  if [ -e "${candidates[0]}" ]; then
    CLANGD=$(printf '%s\n' "${candidates[@]}" | sort -V | tail -1)
  fi
  ```
- Update onboarding instructions and tests to mandate `mkdir -p "$HOME/.local/bin"` prior to creating the symlink.

### Risk Assessment
**LOW-MEDIUM**. The architecture correctly tackles the VS Code multi-root limitations and `esp-clangd` builtins. Addressing the directory creation and wrapper shell pipefail ensures seamless execution for beginners.

---

## 06-03

### Summary
Plan 06-03 introduces fast linting layers to pre-commit: `ruff-check` (v0.17.2) via `pyproject.toml`, `yamllint` (v1.38.0) via `.yamllint.yaml`, and `markdownlint-cli2` (v0.24.0) via `.markdownlint-cli2.jsonc`. It scopes each hook to authored files, excluding generated pages, vendored assets, and `.planning/`. It also clears existing lint backlogs across Python, YAML, and Markdown files.

### Strengths
- **Targeted SCons Injection Handling**: Configuring `per-file-ignores` in `pyproject.toml` for `F821` on `scripts/pio/*.py` and `homeworks/*/merge_firmware.py` prevents breaking SCons build scripts where `Import("env")` and `env` are injected runtime globals ([scripts/pio/compiledb.py#L19-L21](file:///Users/vloktiev/Dev/miltech/homeworks/scripts/pio/compiledb.py#L19-L21), [homeworks/1_3-police-flasher/merge_firmware.py#L13-L54](file:///Users/vloktiev/Dev/miltech/homeworks/homeworks/1_3-police-flasher/merge_firmware.py#L13-L54)).
- **Preservation of Documented Re-exports**: Rather than removing "unused" imports in [scripts/metadata/contract.py#L58-L65](file:///Users/vloktiev/Dev/miltech/homeworks/scripts/metadata/contract.py#L58-L65), Task 1 defines `__all__`, preserving public API re-exports for downstream consumers without pulling `jsonschema` into stdlib tools.
- **Noise Suppression on Practical Formatting**: Disabling `MD013` (line length) and `MD060` (table formatting) in `.markdownlint-cli2.jsonc` avoids destructive reformats across 100-120 column tables and prose.
- **Strict Check-Only Mode**: None of the hooks pass `--fix`, enforcing that pre-commit remains a deterministic gating check rather than an unintended file mutator.

### Concerns
- **Critical GitHub Actions Workflow Corruption in Task 2** *(Severity: HIGH)*: Task 2 states: *"fix the four `truthy` findings by writing `true`/`false` instead of `yes`/`no`/`on`/`off`"*. In GitHub Actions workflows ([.github/workflows/docs.yml#L8](file:///Users/vloktiev/Dev/miltech/homeworks/.github/workflows/docs.yml#L8), [.github/workflows/generated-views.yml#L3](file:///Users/vloktiev/Dev/miltech/homeworks/.github/workflows/generated-views.yml#L3), [.github/workflows/homework.yml#L3](file:///Users/vloktiev/Dev/miltech/homeworks/.github/workflows/homework.yml#L3), [.github/workflows/security.yml#L3](file:///Users/vloktiev/Dev/miltech/homeworks/.github/workflows/security.yml#L3)), the top-level trigger key is `on:`. Under YAML 1.1, `on` is parsed as boolean true, triggering yamllint's `truthy` rule. If an implementer follows the plan instruction literally and changes `on:` to `true:`, GitHub Actions parser will reject the workflow file as invalid schema. The correct fix is either quoting the trigger key (`'on':`) or configuring `.yamllint.yaml` with `rules: truthy: {allowed-values: ['true', 'false'], check-keys: false}`.
- **Omission of `.yamllint.yaml` from Hook File Filter** *(Severity: LOW)*: In Task 2, the `files:` regex for yamllint is `^(\.github/workflows/|homeworks/[^/]+/homework\.yaml$|boards/[^/]+\.yaml$|templates/.*\.ya?ml$|\.pre-commit-config\.yaml$)`. This filter does not match `.yamllint.yaml` itself, leaving the linter's own configuration unvalidated.

### Suggestions
- **Action Required**: Explicitly revise the Task 2 action in 06-03 to quote the `on:` keys in GitHub Actions workflows as `'on':` (or add `check-keys: false` to the yamllint config) and forbid changing `on:` to `true:`.
- Include `|\.yamllint\.ya?ml$` in the hook's `files:` pattern in [.pre-commit-config.yaml](file:///Users/vloktiev/Dev/miltech/homeworks/.pre-commit-config.yaml).

### Risk Assessment
**HIGH** (due to the risk of workflow breakage if `on:` is rewritten to `true:`; drops to **LOW** if quote-fixing `'on':` is explicitly clarified).

---

## 06-04

### Summary
Plan 06-04 sets up the pre-push static analysis layer. It introduces `.clang-tidy` configured with `bugprone-*`, `cert-*`, `performance-*`, `portability-*`, `readability-*`, and `clang-analyzer-*` (disabling `portability-avoid-pragma-once` and keeping `WarningsAsErrors: ""`). It adds `scripts/clang-tidy-db` as a pre-push guard that halts pushes if `tests/compile_commands.json` is missing or older than project inputs, integrates `cpp-linter-hooks` pinned at `--version=23.1.3`, resolves seven `bugprone-signed-bitwise` warnings in `lib/common/src/hex.c`, and machine-checks guard and layering behavior in `test_tooling_config.py`.

### Strengths
- **Inversion of Upstream Skipping Pitfall**: By placing the local `clang-tidy-db` guard hook *ahead* of `cpp-linter-hooks` in [.pre-commit-config.yaml](file:///Users/vloktiev/Dev/miltech/homeworks/.pre-commit-config.yaml), the plan overcomes `cpp-linter-hooks`' default behavior of silently skipping execution when `compile_commands.json` is missing in local runs.
- **Zero-Suppression Cleanup of Signed Bitwise Findings**: In [lib/common/src/hex.c#L48-L91](file:///Users/vloktiev/Dev/miltech/homeworks/lib/common/src/hex.c#L48-L91), integer promotion on bitwise shifts and masks is fixed through clean `(unsigned int)` casts rather than suppressing warnings with `NOLINT`, maintaining strict code quality.
- **Strict Two-Stage Cadence Enforcement**: `default_install_hook_types: [pre-commit, pre-push]` combined with `default_stages: [pre-commit]` and explicit `stages: [pre-push]` ensures that the fast linters never run at push time and static analysis never blocks commit time.

### Concerns
- **Header Omission in Pre-Push Hook Scope** *(Severity: HIGH)*: Both `clang-tidy-db` and `clang-tidy` hooks define:
  `files: ^(lib/(common|host)/src/.*\.(c|h)|lib/port/include/.*\.h)$`
  In `lib/common` and `lib/host`, public headers reside in `lib/common/include/common/*.h` ([lib/common/include/common/hex.h](file:///Users/vloktiev/Dev/miltech/homeworks/lib/common/include/common/hex.h), `crc.h`, `ring_buffer.h`, `timing.h`) and `lib/host/include/host/*.h` ([lib/host/include/host/fake_gpio.h](file:///Users/vloktiev/Dev/miltech/homeworks/lib/host/include/host/fake_gpio.h)). None of these headers are under `src/`!
  Consequently, changes to any header in `lib/common/include/` or `lib/host/include/` will **never match** the hook pattern and will completely bypass the clang-tidy pre-push check.
- **Clang-tidy Execution on Standalone Headers** *(Severity: MEDIUM)*: While `lib/port/include/.*\.h` matches the pattern, `lib/port` has no translation units in `tests/compile_commands.json` ([tests/platformio.ini#L25-L29](file:///Users/vloktiev/Dev/miltech/homeworks/tests/platformio.ini#L25-L29)). When `cpp-linter-hooks` runs clang-tidy directly on a header file without an associated translation unit in the compilation database, clang-tidy may fail or output `Compile command not found`. Clang-tidy is intended to analyze C translation units and check headers via `HeaderFilterRegex: "^(lib|homeworks)/.*"`.
- **Relative Path Handling in `scripts/clang-tidy-db`** *(Severity: LOW)*: Task 1 specifies checking mtimes of "any `file` entry it names that still exists". In PlatformIO SCons compilation databases, `file` fields may be relative to `directory`. The script must resolve `Path(entry["directory"]) / entry["file"]` if relative, otherwise existence checks could fail falsely.

### Suggestions
- Expand the hook `files:` regex in [.pre-commit-config.yaml](file:///Users/vloktiev/Dev/miltech/homeworks/.pre-commit-config.yaml) to include public headers:
  `files: ^(lib/(common|host)/(src|include)/.*\.(c|h)|lib/port/include/.*\.h)$`
- Verify how `cpp-linter-hooks` handles header-only arguments when invoked directly on `lib/port/include/port/*.h`. If `cpp-linter-hooks` throws errors when checking headers directly, consider configuring the hook to run on host `.c` sources while relying on `HeaderFilterRegex` to inspect included headers.

### Risk Assessment
**MEDIUM**. The pre-push stage separation and database freshness checks are well engineered, but the `files:` regex pattern must be corrected to include `lib/common/include/` and `lib/host/include/`.

---

## 06-05

### Summary
Plan 06-05 provides developer onboarding documentation and governance integration. It authors `docs/standards/vscode.md` to guide beginners through VS Code setup, clangd configuration, and no-hardware testing. It integrates the guide into the generated navigation via `templates/views/mkdocs.yml.tmpl`, documents ADR 0012 (formatting approximation) and ADR 0013 (esp-clangd and multi-root contract), indexes them in `docs/decisions/README.md`, updates `AGENTS.md` with a `Quality tooling` section and four-point enforcement vocabulary, and validates all documentation links and assertions in `RulebookAndGuideTests`.

### Strengths
- **Strict Generator & Site Navigation Coupling**: The plan recognizes that [scripts/tests/test_docs_pins.py#L472-L482](file:///Users/vloktiev/Dev/miltech/homeworks/scripts/tests/test_docs_pins.py#L472-L482) (`test_nav_lists_every_markdown_file_under_docs`) and [.github/workflows/docs.yml#L58-L59](file:///Users/vloktiev/Dev/miltech/homeworks/.github/workflows/docs.yml#L58-L59) (`mkdocs build --strict`) fail if an authored Markdown file is missing from `mkdocs.yml`. By authoring `docs/standards/vscode.md`, updating `templates/views/mkdocs.yml.tmpl`, and regenerating via `scripts/gen_views.py --all` in Task 1, documentation integrity is preserved.
- **Accurate Scope Boundaries**: The guide clearly documents that native test translation units are excluded from clang-tidy (D-08a) and that simulation belongs to Phase 7, preventing user confusion or false expectations.
- **Rulebook Vocabulary Alignment**: Updating `AGENTS.md` to define `[ENFORCED: pre-push]` alongside `pre-commit`, `CI`, and `review` formalizes the four quality gates across the repository.

### Concerns
- **Missing Parent Directory Command in Guide** *(Severity: MEDIUM)*: As noted in 06-02, Task 1 specifies documenting the symlink setup: `ln -sf "$PWD/scripts/clangd-wrapper.sh" "$HOME/.local/bin/clangd-wrapper"`. If `docs/standards/vscode.md` does not instruct the user to run `mkdir -p "$HOME/.local/bin"` first, the setup step will fail on clean machines.
- **Sequential Regeneration Churn** *(Severity: LOW)*: Task 1 updates `templates/views/mkdocs.yml.tmpl` and regenerates `mkdocs.yml`. Task 2 adds ADR 0012 and 0013, which dynamically appends entries to `decision_nav_entries` in `mkdocs.yml` via [scripts/gen_views.py#L1102-L1122](file:///Users/vloktiev/Dev/miltech/homeworks/scripts/gen_views.py#L1102-L1122), requiring a second regeneration. While valid, executors must ensure `generated.manifest` is committed after the final regeneration.

### Suggestions
- Ensure `docs/standards/vscode.md` includes `mkdir -p "$HOME/.local/bin"` immediately preceding the `ln -sf` command.
- Ensure `RulebookAndGuideTests` asserts the presence of the `mkdir -p` command in `docs/standards/vscode.md`.

### Risk Assessment
**LOW**. The plan coordinates view generation, site documentation, ADR indexing, and rulebook alignment without disrupting build or test gates.

---

## Cross-Plan Findings and Architectural Consistency

### Dependency Graph & Sequencing
The execution waves are properly structured:
- **Wave 1 (06-01)**: Base formatting and pre-commit setup.
- **Wave 2 (06-02, 06-03)**: Language server setup and fast linting layers. Both depend on 06-01. File sets do not overlap: 06-02 edits `workspace.json.tmpl`, `.clangd`, and `scripts/clangd-wrapper.sh`; 06-03 edits `pyproject.toml`, `.yamllint.yaml`, `.markdownlint-cli2.jsonc`, and `.pre-commit-config.yaml`.
- **Wave 3 (06-04)**: Static analysis pre-push layer. Depends on 06-01 and 06-03 (completing pre-commit configuration before adding pre-push hooks).
- **Wave 4 (06-05)**: Documentation, ADRs, and rulebook updates. Depends on 06-02 and 06-04.

### Test Architecture Consistency
The test architecture is exceptionally disciplined:
- Tests avoid importing `yaml` or `jsonschema` in adherence to rule `04/D-14`.
- All newly added checks (`ClangFormatConfigTests`, `ClangdConfigTests`, `ClangdWrapperTests`, `EditorContractTests`, `ClangTidyConfigTests`, `ClangTidyDbGuardTests`, `HookLayeringTests`, `RulebookAndGuideTests`) reside cleanly in a single new test module: [scripts/tests/test_tooling_config.py](file:///Users/vloktiev/Dev/miltech/homeworks/scripts/tests/test_tooling_config.py).
- Existing golden tests ([scripts/tests/test_new_homework.py](file:///Users/vloktiev/Dev/miltech/homeworks/scripts/tests/test_new_homework.py)) and navigation consistency tests ([scripts/tests/test_docs_pins.py](file:///Users/vloktiev/Dev/miltech/homeworks/scripts/tests/test_docs_pins.py)) are integrated into verification blocks.

---

## Overall Risk and Readiness Assessment

### Summary Verdict
**READY WITH TWO REQUIRED ADJUSTMENTS**. The plan suite is exceptionally thorough, technically grounded in real machine probes, and fully compliant with project rules. Two specific issues must be addressed during execution:

1. **[Plan 06-03] GitHub Actions Workflow Truthy Fix**: Do NOT change `on:` to `true:` in `.github/workflows/*.yml`. Use `'on':` or configure yamllint to avoid invalidating GitHub Actions syntax.
2. **[Plan 06-04] Clang-Tidy Hook Header Scope**: Update the `files:` regex in `.pre-commit-config.yaml` to include `lib/common/include/` and `lib/host/include/` so that public header edits are not silently excluded from static analysis.

---

## Consensus Summary

Three reviewers ran: `codex-glm` (glm-5.3-flash:cloud), `codex-beam` (beam:cloud), and
`antigravity` (gemini-3.8-flash-high). All three covered all five plan ids.

`codex-beam` and `antigravity` were both stamped `[reviewed-without-source-citations]` by the
runner — they declared source-grounded evidence but did not cite it in the `path:line` form the
grader requires. Their concerns are recorded below but are **not** counted at full consensus
weight. `codex-glm` supplied grounded `path:line` evidence throughout and carries the heaviest
weight in this summary. The claims in "Agreed Concerns" were additionally re-verified against the
tree by the orchestrator before being promoted here.

### Agreed Strengths

- **The plans are grounded in verified repository reality, not assumption.** The 60-file
  C/C++ count, `scripts/tests/test_new_homework.py:68-74`'s whole-tree golden snapshot, the
  generator ownership of `templates/views/workspace.json.tmpl`, and the compile-database location
  at `scripts/pio/compiledb.py:21-22` all check out (codex-glm, antigravity, codex-beam).
- **Check-only hook semantics are correct in every plan.** `entry: clang-format --dry-run --Werror`
  overrides the mirror's in-place default, and adding `default_stages: [pre-commit]` prevents the
  later pre-push hooks from running at commit time (all three reviewers).
- **06-02's multi-root editor correction (D-19a) is the most valuable change in the phase.** Root
  `.vscode/settings.json` does not reach other workspace roots; emitting the same settings object
  through the generated `homeworks.code-workspace` fixes a real novice-facing trap. Pairing it with
  `BuiltinHeaders: QueryDriver` also closes esp-clangd's missing-resource-header gap (all three).
- **06-04's guard-before-clang-tidy ordering is the right inversion of the upstream hook.** It is
  the only way to turn cpp-linter-hooks' silent local skip into a loud, actionable failure
  (all three reviewers).
- **The test architecture is disciplined.** New checks stay stdlib-only (no `yaml`/`jsonschema`
  import, per `04/D-14`) and are consolidated in `scripts/tests/test_tooling_config.py`, while
  existing golden and nav-consistency suites remain the integration points (antigravity, codex-glm).

### Agreed Concerns

1. **HIGH — 06-03: the yamllint `truthy` remediation is unimplementable as written.**
   `06-03-PLAN.md:149` instructs the executor to fix the four `truthy` findings by "writing
   `true`/`false` instead of `yes`/`no`/`on`/`off`". The repository has exactly four YAML files
   with a top-level `on:` key — `.github/workflows/{docs,generated-views,homework,security}.yml` —
   and `on:` is parsed as boolean `true` under YAML 1.1. Rewriting those to `true:` breaks GitHub
   Actions schema validation; the four findings and the four workflows match one-to-one. The policy
   must become `truthy: {check-keys: false}` (optionally plus quoting the keys as `'on':`), and the
   task action must be renamed accordingly. Raised HIGH by codex-glm and antigravity, and flagged
   independently by codex-beam. **Blocking.**

2. **HIGH — 06-04: the hook `files:` regex silently excludes public headers.**
   `06-04-PLAN.md:120` uses `^(lib/(common|host)/src/.*\.(c|h)|lib/port/include/.*\.h)$`, but
   `lib/common/include/common/` and `lib/host/include/host/` exist and are outside `src/`. A
   header-only change therefore bypasses both the database guard and clang-tidy entirely. Raised
   HIGH by antigravity and MEDIUM by codex-glm; verified against the tree. **Blocking.**

3. **MEDIUM — 06-05: the `pip` assertion contradicts D-06.**
   `06-05-PLAN.md:198` asserts the guide "contains … `pip`", while `06-05-PLAN.md:70` requires the
   guide to document *no* pip-user install. The assertion is too weak and can only be satisfied by
   mentioning a forbidden method. Replace it with a positive `pre-commit install` assertion plus a
   negative Homebrew/apt/global-pip assertion (codex-glm, codex-beam; also raised by antigravity as
   a documentation-quality concern).

4. **MEDIUM — 06-02/06-05: `~/.local/bin` is assumed to exist.**
   The symlink step `ln -sf "$PWD/scripts/clangd-wrapper.sh" "$HOME/.local/bin/clangd-wrapper"`
   fails on a clean macOS or Linux home directory, which is exactly the audience the guide targets.
   Add `mkdir -p "$HOME/.local/bin" &&` in the plan, the wrapper's diagnostic message, and the
   guide, and assert it in `RulebookAndGuideTests` (codex-glm, antigravity, codex-beam).

5. **MEDIUM — 06-05: the guide's content contract omits `pre-commit install`.**
   D-10 depends on one `pre-commit install` wiring *both* stages, yet the enumerated machine steps
   in `06-05-PLAN.md:122` stop at the symlink and `compiledb`. Success criterion 5 covers the whole
   beginner setup, so the step must be in the content contract and in the test (codex-glm,
   codex-beam).

6. **MEDIUM — 06-02: `set -euo pipefail` can abort the wrapper before its fallback diagnostic.**
   Candidate discovery built as a pipeline (e.g. `ls … 2>/dev/null | sort -V | tail -1`) exits
   non-zero when nothing matches, so the script dies at the lookup line instead of printing the
   intended message and exiting 2. Use an array/glob that tolerates no matches, and add a wrapper
   test that exercises "not on `PATH`, but present under `$HOME/.espressif`" (codex-glm,
   antigravity).

### Divergent Views

- **Overall readiness.** `antigravity` returns "READY WITH TWO REQUIRED ADJUSTMENTS" and rates
  06-01, 06-02 and 06-05 LOW; `codex-glm` rates the set MEDIUM with 06-03 and 06-04 MEDIUM-HIGH;
  `codex-beam` rates every plan MEDIUM. The disagreement is mostly about how much
  verification-noise counts as risk, not about any specific mechanism.
- **06-01 mechanical reformat granularity.** `codex-beam` wants the build re-run after each group
  (`lib`, then `tests`, then homeworks) so a `SortIncludes` breakage can be isolated;
  `codex-glm` considers one post-pass build gate plus an explicit include-block diff review
  sufficient; `antigravity` rates the plan LOW and asks only for `xargs` in the reformat command
  and a `.git-blame-ignore-revs` entry.
- **06-04 database and header analysis.** `codex-glm` wants relative compile-command entries
  resolved against `<root>/tests/` and a probe that proves clang-tidy actually ran (the current
  verify command can pass vacuously); `antigravity` wants the regex widened and questions whether
  `cpp-linter-hooks` can analyze a standalone header with no TU; `codex-beam` treats the native-TU
  gap as adequately recorded in D-08a and the ADR.
- **06-05 prose assertions generally.** `codex-glm` would prefer asserting command substrings and
  required terms rather than full sentences; `codex-beam` agrees only about the `pip` assertion.
  `antigravity` treats the exact-substring policy as a strength ("a later edit cannot silently drop
  a required step").

### Recommended Fix Order

1. Correct the yamllint policy in 06-03 **before** any later plan wires the hook, or
   `pre-commit run --all-files` fails the whole downstream gate.
2. Widen the 06-04 `files:` regex and specify relative-path resolution in `scripts/clang-tidy-db`.
3. Align 06-02 and 06-05 on `mkdir -p "$HOME/.local/bin"`, `pre-commit install`, and the `pip`
   assertion so the two plans cannot drift.

---
phase: 06-developer-experience-and-quality-layering
verified: 2026-10-26T12:24:25Z
status: passed
score: 56/56 must-haves verified
covered_files:
  - .clang-format
  - .clang-tidy
  - .github/pull_request_template.md
  - .github/workflows/security.yml
  - .gitignore
  - .markdownlint-cli2.jsonc
  - .planning/phases/06-developer-experience-and-quality-layering/06-01-PLAN.md
  - .planning/phases/06-developer-experience-and-quality-layering/06-01-SUMMARY.md
  - .planning/phases/06-developer-experience-and-quality-layering/06-02-PLAN.md
  - .planning/phases/06-developer-experience-and-quality-layering/06-02-SUMMARY.md
  - .planning/phases/06-developer-experience-and-quality-layering/06-03-PLAN.md
  - .planning/phases/06-developer-experience-and-quality-layering/06-03-SUMMARY.md
  - .planning/phases/06-developer-experience-and-quality-layering/06-04-PLAN.md
  - .planning/phases/06-developer-experience-and-quality-layering/06-04-SUMMARY.md
  - .planning/phases/06-developer-experience-and-quality-layering/06-05-PLAN.md
  - .planning/phases/06-developer-experience-and-quality-layering/06-05-SUMMARY.md
  - .planning/phases/06-developer-experience-and-quality-layering/06-06-PLAN.md
  - .planning/phases/06-developer-experience-and-quality-layering/06-06-SUMMARY.md
  - .pre-commit-config.yaml
  - .vscode/settings.json
  - .yamllint.yaml
  - AGENTS.md
  - docs/decisions/0006-public-commit-identity.md
  - docs/decisions/0012-formatting-approximation.md
  - docs/decisions/0013-clangd-multi-root-contract.md
  - docs/decisions/README.md
  - docs/standards/vscode.md
  - generated.manifest
  - homeworks.code-workspace
  - homeworks/1_3-police-flasher/.clangd
  - homeworks/1_3-police-flasher/lib/pattern/include/pattern/controller.h
  - homeworks/1_3-police-flasher/lib/pattern/include/pattern/pattern.h
  - homeworks/1_3-police-flasher/lib/pattern/src/controller.c
  - homeworks/1_3-police-flasher/lib/pattern/src/pattern.c
  - homeworks/1_3-police-flasher/merge_firmware.py
  - homeworks/1_3-police-flasher/report.md
  - homeworks/1_3-police-flasher/src/main.cpp
  - homeworks/1_3-police-flasher/test/test_controller/test_controller.c
  - homeworks/1_3-police-flasher/test/test_homework/test_homework.c
  - homeworks/1_3-police-flasher/test/test_pattern/test_pattern.c
  - lib/arduino/src/gpio.c
  - lib/arduino/src/log.c
  - lib/arduino/src/time.c
  - lib/common/include/common/hex.h
  - lib/common/include/common/timing.h
  - lib/common/src/crc.c
  - lib/common/src/hex.c
  - lib/common/src/ring_buffer.c
  - lib/common/src/timing.c
  - lib/espidf/src/gpio.c
  - lib/espidf/src/log.c
  - lib/espidf/src/time.c
  - lib/host/src/fake_gpio.c
  - lib/host/src/fake_i2c.c
  - lib/host/src/fake_log.c
  - lib/host/src/fake_spi.c
  - lib/host/src/fake_time.c
  - lib/port/include/port/gpio.h
  - lib/port/include/port/i2c.h
  - lib/port/include/port/log.h
  - lib/port/include/port/time.h
  - mkdocs.yml
  - pyproject.toml
  - scripts/affected.py
  - scripts/check_architecture.py
  - scripts/clang-tidy-db
  - scripts/clang-tidy-hook
  - scripts/clangd-wrapper.sh
  - scripts/gen_views.py
  - scripts/metadata/contract.py
  - scripts/tests/fixtures/golden/homework-arduino/.clangd
  - scripts/tests/fixtures/golden/homework-arduino/src/main.cpp
  - scripts/tests/fixtures/golden/homework-arduino/test/test_homework/test_homework.c
  - scripts/tests/fixtures/golden/homework-espidf/.clangd
  - scripts/tests/fixtures/golden/homework-espidf/src/main.cpp
  - scripts/tests/fixtures/golden/homework-espidf/test/test_homework/test_homework.c
  - scripts/tests/test_ci_workflows.py
  - scripts/tests/test_homework_metadata.py
  - scripts/tests/test_tooling_config.py
  - templates/homework-arduino/.clangd
  - templates/homework-arduino/src/main.cpp
  - templates/homework-arduino/test/test_homework/test_homework.c
  - templates/homework-espidf/.clangd
  - templates/homework-espidf/src/main.cpp
  - templates/homework-espidf/test/test_homework/test_homework.c
  - templates/views/mkdocs.yml.tmpl
  - templates/views/workspace.json.tmpl
  - tests/src/main.c
  - tests/test/test_common_crc/test_crc.c
  - tests/test/test_common_hex/test_hex.c
  - tests/test/test_common_ring_buffer/test_ring_buffer.c
  - tests/test/test_common_timing/test_timing.c
  - tests/test/test_host_fake_time/test_fake_time.c
  - tests/test/test_host_fakes/test_host_fakes.c
  - tests/test/test_port_contracts/test_contracts.c
covered_digest: "v3:sha256:d2f51af46c460fa0dffaabf2c150439892c9eca11b57dddb54122e7e32165028"
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: human_needed
  previous_score: 50/51
  gaps_closed:
    - "G-06-1: the headless esp-clangd check command is documented and executed in the attached-value form --check=<path>; the wrapper exits 0 with `All checks completed, 0 errors`."
  gaps_remaining: []
  regressions: []
deferred:
  - truth: "TOOL-03's CI layer — full build, tests, schema, docs, architecture, and simulation checks in CI"
    addressed_in: "Phase 8"
    evidence: "Phase 8 goal: 'Pull requests are gated by a fast, changed-only CI pipeline with one required check'; Phase 6 context explicitly defers CI wiring, the CI matrix, and PR-time checks to Phase 8 (TOOL-05, TOOL-06, SIM-04)."
---

# Phase 6: Developer Experience and Quality Layering Verification Report

**Phase Goal:** A novice can open the workspace, get correct ESP32 IntelliSense, and have formatting and layered quality checks run without guesswork.
**Friction-log justification:** The Phase 4.2 log must contain at least one entry for formatting, IntelliSense, or local feedback; otherwise the tooling is not added.
**Verified:** 2026-10-26T12:24:25Z
**Status:** passed
**Re-verification:** Yes — after the 06-06 gap-closure plan closed G-06-1. The report was regenerated from the current tree because the covered source changed.

## Friction-Log Justification

**VERIFIED.** `.planning/phases/04.2-tracer-homework-1-3/04.2-FRICTION-LOG.md` contains real
entries and an explicit Phase 6 automation row:

- **F-05** (line 76) — native `-Wall -Wextra -Werror` fails while the target build stays green;
  local feedback is the friction.
- **F-18** (line 232) — opening the homework as a workspace folder makes the IDE emit untracked
  `c_cpp_properties.json` and friends because no committed editor configuration exists.
- `## Top automation candidates` row (line 269): *"Add clang-format, clang-tidy, and an
  esp-clangd IntelliSense path to the workspace | F-05, F-18 | Phase 6"*.

The justification is present and names this phase by number. The tooling was not added on
speculation.

## Goal Achievement

### Observable Truths

Roadmap success criteria are listed first (R1–R5), followed by the plan-level must-haves
(1.1–5.11) and the 06-06 gap-closure must-haves (6.1–6.5). Plan-level truths add detail; none
subtracts a roadmap criterion.

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| R1 | `clang-format --dry-run --Werror` passes with 4-space indent, 120 columns, function braces on a new line, documented as an ESP-IDF approximation | ✓ VERIFIED | `.clang-format` carries `IndentWidth: 4`, `ColumnLimit: 120`, `AfterFunction: true`; the pinned 23.1.3 dry-run over all 60 tracked C/C++ files exits 0; ADR 0012 says "approximation", "never equivalence" |
| R2 | clang-tidy runs bugprone, cert, performance, and portability checks on host code in pre-push | ✓ VERIFIED | `.clang-tidy` selects all four families plus readability/clang-analyzer; `pre-commit run --all-files --hook-stage pre-push` ran `clang-tidy-db` + `clang-tidy`, both Passed |
| R3 | esp-clangd resolves ESP32-S3 includes through per-project `.clangd` and explicit absolute `--query-driver` globs; cpptools IntelliSense disabled | ✓ VERIFIED | All five `.clangd` copies are byte-identical (`cdbcba024be1420f108e5bab76ffca5372115fb4`); wrapper forwards two bounded absolute globs; the live run `"$HOME/.local/bin/clangd-wrapper" --check=homeworks/1_3-police-flasher/src/main.cpp` exits 0 with `All checks completed, 0 errors` after loading the Xtensa toolchain includes; the three cpptools keys are `disabled` |
| R4 | pre-commit runs format, markdownlint, yamllint, ruff, and gitleaks; pre-push runs clang-tidy | ✓ VERIFIED | The commit stage runs 13 hooks; gitleaks, clang-format, ruff-check, yamllint and markdownlint-cli2 all Passed. The pre-push stage ran exactly the two clang-tidy hooks, both Passed. See the environment note about `end-of-file-fixer` |
| R5 | `docs/standards/vscode.md` takes a beginner from install to format-on-save, Problems panel, clangd, and a no-hardware check | ✓ VERIFIED | 188-line guide covers install, both extensions, the symlink, `pre-commit install`, compiledb, format-on-save, Problems panel, the attached headless check, no-hardware commands, and a Windows/WSL note; `mkdocs build --strict` exits 0 |
| 1.1 | `.clang-format` resolves to 4-space, 120-column, tabs never, function braces on a new line, `ReflowComments` disabled; documented approximation | ✓ VERIFIED | Keys present exactly once; ADR 0012; the 23.1.3 dry-run resolves the file |
| 1.2 | clang-format hook is check-only; a failing run leaves every file byte-identical | ✓ VERIFIED | Hook entry is `clang-format --dry-run --Werror` with no `-i`; the prior independent misformatted-temp probe exited 1 with unchanged bytes |
| 1.3 | Every tracked C/C++ file (60) passes the pinned 23.1.3 check with zero violations | ✓ VERIFIED | `git ls-files '*.c' '*.h' '*.cpp' '*.hpp'` = 60; the independent 23.1.3 dry-run exits 0 |
| 1.4 | Both templates and their golden fixtures were reformatted by the same pass; the golden tree stays byte-identical | ✓ VERIFIED | Template and golden `main.cpp` sha256 are equal for both Arduino and ESP-IDF; `python3 -m unittest scripts.tests.test_new_homework` — 35 tests OK |
| 1.5 | Reformat did not break the build: shared native, homework native, ESP32-S3 build green | ✓ VERIFIED | `pio test -d tests -e native` 73/73; homework native 38/38; `pio run -d homeworks/1_3-police-flasher` SUCCESS |
| 1.6 | No `.editorconfig` exists at the root or in any subtree; committed tool configs are the only style sources | ✓ VERIFIED | `git ls-files '*editorconfig*'` returns 0; the only files on disk are gitignored Unity copies under `.pio/libdeps/` |
| 1.7 | `SortIncludes` reordered includes without adding, removing, or retyping one | ✓ VERIFIED | Recomputed the include multiset of all 44 reformatted C/C++ files between `2d56320^` and `2d56320`: 0 mismatches |
| 2.1 | Scaffolded Arduino/ESP-IDF homework carries `.clangd` byte-identical to its golden; golden-tree tests green with no change to `scripts/new_homework` | ✓ VERIFIED | All five `.clangd` sha256 equal; `test_new_homework` 35 tests OK; the scaffold script is not in the phase diff |
| 2.2 | The real `homeworks/1_3-police-flasher/` carries the same `.clangd` | ✓ VERIFIED | sha256 equal to both templates and both goldens |
| 2.3 | Every committed `.clangd` sets `CompilationDatabase: .` and `BuiltinHeaders: QueryDriver`; the database is the one `scripts/pio/compiledb.py` writes to the project root | ✓ VERIFIED | `.clangd` keys present in all five copies; `compiledb.py` sets `COMPILATIONDB_PATH=$PROJECT_DIR/compile_commands.json` |
| 2.4 | Wrapper resolves `$ESP_CLANGD` → PATH → newest `~/.espressif` build, never aborts under `set -euo pipefail`, exits 2 only on exhaustion | ✓ VERIFIED | `ClangdWrapperTests` pass inside the 74-test module; source uses `command -v` in `if`, `nullglob`, and count-guarded arrays |
| 2.5 | On exhaustion the wrapper prints one `FAIL clangd-wrapper:` line naming the installation source, the two-step install command, and `docs/standards/vscode.md` | ✓ VERIFIED | Source `fail` message checked; an invalid `$ESP_CLANGD` probe printed one FAIL line naming the executable and exited 2 |
| 2.6 | A relative `PLATFORMIO_CORE_DIR` is refused with exit 2 and a FAIL line | ✓ VERIFIED | Independent probe: `PLATFORMIO_CORE_DIR=relative` → one FAIL line, exit 2 |
| 2.7 | Editor contract carries exactly the eight expected keys in both settings; three cpptools keys are `disabled` | ✓ VERIFIED | Parsed both JSON files: identical 8-key sets; all three cpptools values `disabled`; `EditorContractTests` pass |
| 2.8 | Wrapper passes exactly two bounded absolute `--query-driver` globs and never a recursive wildcard | ✓ VERIFIED | Independent probe with a fake clangd printed exactly `--query-driver=<abs>/toolchain-*/bin/*,<abs>/tool-*/bin/*`; no `**` |
| 2.9 | Generated workspace carries `settings`; `.vscode/settings.json` mirrors it; cpptools disabled, format-on-save for C/C++, `--background-index` | ✓ VERIFIED | Parsed objects are equal; `editor.formatOnSave = true`; `clangd.arguments = ["--background-index"]` |
| 2.10 | `clangd.path` is emitted as the literal home-relative wrapper path, so the closed renderer accepts it and multi-root resolves it | ✓ VERIFIED | `gen_views.py:653` supplies `${env:HOME}/.local/bin/clangd-wrapper`; template uses `{{clangd_wrapper_path}}`; generated workspace carries the literal |
| 2.11 | `gen_views.py --all --check` exits 0 and `generated.manifest` records the new workspace hash | ✓ VERIFIED | All eight views UNCHANGED, exit 0; the manifest carries the workspace entry and the check validates it |
| 3.1 | `ruff-check`, `yamllint`, and `markdownlint-cli2` each pass on the committed tree | ✓ VERIFIED | All three Passed inside `pre-commit run --all-files` |
| 3.2 | ruff configured once in root `pyproject.toml` with py313, 100 columns, E/F/I/UP/B, and the two F821 ignores | ✓ VERIFIED | File matches exactly; no `[project]` table |
| 3.3 | yamllint covers authored YAML only with the specified rules | ✓ VERIFIED | `.yamllint.yaml` extends default with max 120, `document-start: disable`, restricted `truthy` with `check-keys: false`; hook `files` regex matches the named families |
| 3.4 | The four `truthy` findings are workflow trigger keys; `check-keys: false` clears them and all four workflows keep a top-level `on:` | ✓ VERIFIED | All four workflows carry `^on:`; `test_ci_workflows` passes in the 356-test run |
| 3.5 | markdownlint covers authored Markdown, excludes the named families, disables MD013/MD060, and uses MD024 `siblings_only` | ✓ VERIFIED | Config and hook `exclude` match; no ADR heading renamed |
| 3.6 | No authored YAML or ADR prose is rewritten to satisfy a linter; policy fixes where correct, real fixes only for real defects | ✓ VERIFIED | The phase diff's two edits are real defects relative to the committed policy: a >120-column URL line in `security.yml` and an unlabelled fence in ADR 0006. Recorded deviation below |
| 3.7 | Every added hook is check-only: no auto-correct flag, no rewrite or staging | ✓ VERIFIED | `ruff-check` (not `ruff-format`), yamllint and markdownlint with no `--fix`; `test_no_hook_auto_corrects_or_filters_to_all_lines` passes |
| 3.8 | The one-time cleanup changed no behaviour: stdlib suite, metadata checker, generated-view check still green | ✓ VERIFIED | 356 tests OK; `check-metadata` and `gen-views-check` Passed in the all-files run |
| 4.1 | Missing/stale database exits 1 with exactly `pio run -d tests -e native -t compiledb`; the guard never generates, writes, or skips | ✓ VERIFIED | Independent probe with an empty root: exit 1, one FAIL line naming that command; fresh database PASS exit 0 |
| 4.2 | Fresh database analyses every in-scope host source with no diagnostic; an injected `bugprone-signed-bitwise` violation makes the hook fail and name it | ✓ VERIFIED | The pre-push run passes over the real tree; `ClangTidyHookWrapperTests` prove the hook fails on undescribed/skipped sources; the injection probe is recorded in 06-04-SUMMARY D4 |
| 4.3 | A database `file` entry is resolved against its own `directory`, not the repository root | ✓ VERIFIED | Guard and hook resolve relative entries against the entry directory; the relative-entry tests pass |
| 4.4 | Both pre-push hook patterns reach the header trees, or — if the header probe shows a standalone header cannot be analysed — the narrowing is recorded in ADR 0013 rather than applied silently | ✓ VERIFIED (escape clause applied) | The probe showed a bare header exits 0 without analysis; review CR-02 narrowed both patterns to `.c` under `lib/*/src` and made the hook fail on undescribed sources. The contract is recorded in ADR 0013, AGENTS.md, and the guide |
| 4.5 | pre-push runs exactly the two clang-tidy hooks; every fast hook runs only at `pre-commit` | ✓ VERIFIED | `default_stages: [pre-commit]` + explicit `stages:`; the all-files pre-push run executed exactly `clang-tidy-db` and `clang-tidy` |
| 4.6 | `default_install_hook_types` is `[pre-commit, pre-push]` | ✓ VERIFIED | Present in `.pre-commit-config.yaml`; the guide's single `pre-commit install` command matches |
| 4.7 | `.clang-tidy` covers bugprone, cert, performance, portability, readability, clang-analyzer; disables `portability-avoid-pragma-once`; `WarningsAsErrors` empty | ✓ VERIFIED | File matches; `ClangTidyConfigTests` pass |
| 4.8 | The seven real `bugprone-signed-bitwise` findings are fixed by unsigned casts; behaviour unchanged and native suite green | ✓ VERIFIED | Four casts in `hex.c` (lines 49, 50, 90, 91) and three in `crc.c` (lines 18, 21, 23); 73/73 native tests pass. Attribution note below |
| 4.9 | The guard's local hook block precedes the `cpp-linter-hooks` block in file order | ✓ VERIFIED | `clang-tidy-db` at line 233; `cpp-linter-hooks` repo at line 254 |
| 5.1 | `docs/standards/vscode.md` is named in an explicit `Standards` nav section of the template; generated `mkdocs.yml` carries it; strict build green | ✓ VERIFIED | Template and generated nav both carry `Standards → standards/vscode.md`; `mkdocs build --strict` exit 0 |
| 5.2 | The guide covers install → format-on-save, Problems panel, clangd, no-hardware; macOS/Linux with a Windows WSL note | ✓ VERIFIED | All sections present; `RulebookAndGuideTests.test_the_guide_names_the_editor_surfaces` passes |
| 5.3 | The guide names exactly one repository-specific machine step — the `mkdir -p` + `ln -sf` command — and explains `clangd.path` resolution | ✓ VERIFIED | Guide says "the one repository-specific machine step"; the two-step wrapper command test passes |
| 5.4 | The guide includes `pre-commit install` as one command wiring both stages and a checklist naming the hooks a contributor meets | ✓ VERIFIED | `pre-commit install` present; guide lists 13 commit + 2 push hooks, matching the config's 15 ids |
| 5.5 | The guide names no Homebrew, Debian package-manager, or global/user pip installation | ✓ VERIFIED | No such command; `test_the_guide_names_no_system_package_manager_install` passes |
| 5.6 | The guide explains the no-hardware path with `pio test -d tests -e native` and `pio run -d homeworks/1_3-police-flasher`, and does not claim a simulation path | ✓ VERIFIED | Both commands present; the guide explicitly says simulation belongs to Phase 7 |
| 5.7 | The guide records the clang-tidy native-test-TU gap explicitly | ✓ VERIFIED | "Native test translation units are out of scope... belongs to Phase 8 CI" in the guide; the same gap is in ADR 0013 § Native test translation units |
| 5.8 | ADR 0012 records the approximation; ADR 0013 records esp-clangd/multi-root, `BuiltinHeaders: QueryDriver`, the `--query-driver` execution implication, and the test-TU gap | ✓ VERIFIED | Both ADR bodies carry the required sections; ADR 0013 also records the analysed-scope narrowing |
| 5.9 | `docs/decisions/README.md` gains two rows dated 2026-10-26, status `accepted`, linked to the ADRs | ✓ VERIFIED | Rows for 0012 and 0013 present with `accepted` and links |
| 5.10 | `AGENTS.md` gains a `Quality tooling` section, uses four enforcement points, and gains a routing row to `docs/standards/vscode.md` | ✓ VERIFIED | Section at line 165; `ENFORCED:` values include pre-commit, pre-push, CI, review; routing row at line 247 |
| 5.11 | `generated.manifest` records the new `mkdocs.yml` hash and `gen_views.py --all --check` exits 0 | ✓ VERIFIED | Manifest carries the entry; all views UNCHANGED, exit 0 |
| 6.1 | `"$HOME/.local/bin/clangd-wrapper" --check=homeworks/1_3-police-flasher/src/main.cpp`, run from the repository root, prints `All checks completed, 0 errors` and exits 0 | ✓ VERIFIED | Executed in this pass: exit 0, `All checks completed, 0 errors`; the detached form still exits 1 with `clangd: Unknown command line argument` |
| 6.2 | The guide's "see the same analysis without the editor" command is that exact attached form, and the guide states why: esp-clangd declares the flag with an optional attached value, so the value must be joined with `=` | ✓ VERIFIED | `docs/standards/vscode.md:112` carries the attached form; lines 115–116 state `--check[=<string>]` and the stray-positional consequence |
| 6.3 | Both occurrences in `06-VERIFICATION.md` and the one occurrence in `06-VALIDATION.md` name the same attached form, so a re-verifier is not handed a command that exits 1 | ✓ VERIFIED | The 06-VALIDATION table carries it once; this regenerated report carries it in R3, 6.1, the spot-check table, and the UAT section. The pre-06-06 detached copies were replaced |
| 6.4 | `scripts/tests/test_tooling_config.py` fails when the guide's attached command is removed or when a detached value followed by a `.c`/`.cpp` path returns, and a third case proves the detector matches the exact line recorded in `06-UAT.md` | ✓ VERIFIED | `ClangdCheckCommandTests` has positive (`assertIn(CHECK_COMMAND, GUIDE)`), negative (`assertIsNone(DETACHED_CHECK_PATTERN.search(GUIDE))`), and non-vacuity (`assertIsNotNone(DETACHED_CHECK_PATTERN.search(RECORDED_DEFECT_LINE))`) cases; the 74-test module passes |
| 6.5 | The ADR 0013 body, `06-02-PLAN.md`, `06-02-SUMMARY.md`, and `06-UAT.md` are byte-identical to their pre-plan state; every remaining detached-form occurrence in the repository is listed in the occurrence audit with a reason | ✓ VERIFIED | `git diff --stat e8beb02..HEAD` over the four files and `scripts/clangd-wrapper.sh` is empty. The audit's pre-plan ledger matches every remaining source-path occurrence; see the nuance note below |

**Score:** 56/56 truths verified (0 present, behavior-unverified).
`behavior_unverified`: 0.

R3 was the only behavior-dependent truth left at the previous pass. It is now **VERIFIED** because
the live invocation was executed in this pass, not merely grepped: the wrapper resolved esp-clangd
21.1.3, loaded the homework `compile_commands.json`, queried the Xtensa toolchain, and reported
`All checks completed, 0 errors`, exit 0. The separate editor surface (Problems panel,
format-on-save) was exercised by the human UAT, not inferred.

### Recorded Deviations (non-blocking)

1. **Plan 06-04 truth 4.4 (header patterns).** At plan time both pre-push patterns were expected
   to reach `lib/common/include/**` and `lib/host/include/**`. The header probe exited 0 because
   pinned clang-tidy 23.1.3 skips a bare header silently, so the plan's escape clause applied.
   Code review CR-02 then proved a header-only push passed with no analysis at all; the fix
   narrowed both patterns to `.c` under `lib/*/src` and added `scripts/clang-tidy-hook`, which
   fails when a source has no compile command. The final contract is recorded in ADR 0013,
   AGENTS.md, and the guide.
2. **Plan 06-04 truth 4.8 wording.** The seven `bugprone-signed-bitwise` findings are four in
   `lib/common/src/hex.c` and three in `lib/common/src/crc.c`, not seven in `hex.c`. The intent —
   fix every real finding, change no behaviour, keep the native suite green — is met.
3. **Plan 06-03 truth 3.6.** The phase diff contains two authored-file edits that a strict reading
   calls "rewritten to satisfy a linter": a >120-column URL in `.github/workflows/security.yml`
   and a `text` language tag added to a fence in ADR 0006. Both are real defects relative to the
   committed policy and are the plan's own prescribed remedy; neither silences a rule.
4. **Plan 06-01 truth 1.6.** Three `.editorconfig` files exist under gitignored
   `.pio/libdeps/native/.../Unity/`. They are downloaded dependency build output, untracked, and
   not style sources for this repository; no tracked `.editorconfig` exists.
5. **Plan 06-06 truth 6.5 nuance.** The occurrence audit was measured at `e8beb02`, before the
   gap-closure plan. After the plan the only additional detached source-path occurrence is the
   `RECORDED_DEFECT_LINE` fixture constant in `scripts/tests/test_tooling_config.py:1113`, which
   the plan requires as the non-vacuity fixture and which is explicitly not authored Markdown. The
   other post-plan mentions (`06-06-SUMMARY.md`, `06-UAT.md` lines 47 and 50) describe the defect
   in prose and are historical records. No live authored command is detached.

### Deferred Items

Items not yet met but explicitly addressed in later milestone phases.

| # | Item | Addressed In | Evidence |
|---|------|-------------|----------|
| 1 | TOOL-03's CI layer: full build, tests, schema, docs, architecture, and simulation checks in CI | Phase 8 | Phase 8 goal: "Pull requests are gated by a fast, changed-only CI pipeline with one required check"; Phase 6 context defers CI wiring (TOOL-05, TOOL-06, SIM-04) |

### Advisory (New Scope, Unevidenced)

None. This re-verification pass raised no new Step 7 finding. The five open info-level review
findings (IN-01..IN-05) remain recorded as `open` in `06-REVIEW-DISPOSITION.md`; none is backed
by a failing test or a reproducible command that breaks the phase goal. They are pre-existing
review observations, not regressions introduced by the gap-closure round.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `.clang-format` | single C/C++ style source | ✓ VERIFIED | All D-02 keys, documented approximation |
| `.clang-tidy` | host-only, warnings-first policy | ✓ VERIFIED | Six families, empty `WarningsAsErrors`, unanchored header filter |
| `.pre-commit-config.yaml` | layered check-only hooks | ✓ VERIFIED | 13 commit + 2 push hooks; pinned revs; explicit stages |
| `scripts/clangd-wrapper.sh` | discovered esp-clangd launcher | ✓ VERIFIED | mode 100755, bounded globs, exit-2 vocabulary |
| `scripts/clang-tidy-db` | read-only database guard | ✓ VERIFIED | mode 100755, exit 0/1/2, names the remedy |
| `scripts/clang-tidy-hook` | fail on unanalysed source | ✓ VERIFIED | mode 100755, database membership pre-check + skip-marker check |
| `templates/homework-*/`, goldens, real homework `.clangd` | five byte-identical fragments | ✓ VERIFIED | identical sha256 `cdbcba02...` |
| `templates/views/workspace.json.tmpl` | emitted editor contract | ✓ VERIFIED | `settings` block with closed placeholder |
| `.vscode/settings.json` | single-folder mirror | ✓ VERIFIED | parsed object equal to workspace `settings` |
| `pyproject.toml`, `.yamllint.yaml`, `.markdownlint-cli2.jsonc` | one policy per tool | ✓ VERIFIED | match plan |
| `docs/standards/vscode.md` | beginner guide with the attached check | ✓ VERIFIED | 188 lines, attached form at line 112, rationale at 115 |
| `docs/decisions/0012-*.md`, `0013-*.md`, `README.md` | two ADRs + rows | ✓ VERIFIED | accepted, 2026-10-26 |
| `AGENTS.md` | Quality tooling section, four points, routing row | ✓ VERIFIED | present |
| `scripts/tests/test_tooling_config.py` | machine checks | ✓ VERIFIED | 74 tests, 10 classes, including `ClangdCheckCommandTests` |

### Key Link Verification

The `query verify.key-links` text probe reports several `verified: false` entries because it
requires the `from:` value to be a literal file path and the `to:` value to be a literal string
in that file. Several links here are structural (hash equality, parsed-object equality, a hook
resolving a config by cwd). Each is verified below by the actual mechanism, not by a substring.

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `.pre-commit-config.yaml` clang-format | `.clang-format` | `-style=file` | WIRED | Hook args `[-style=file]`, entry `clang-format --dry-run --Werror` |
| template `main.cpp` | golden `main.cpp` | same pinned reformat | WIRED | sha256 equal for both templates |
| template `.clangd` | golden `.clangd` | golden-tree equality | WIRED | sha256 equal, 35 golden tests OK |
| `.clangd` `CompilationDatabase: .` | `scripts/pio/compiledb.py` | database written to the project root | WIRED | `COMPILATIONDB_PATH=$PROJECT_DIR/compile_commands.json` |
| `workspace.json.tmpl` | `.vscode/settings.json` | `EditorContractTests` equality | WIRED | parsed objects identical, 8 keys |
| ruff-check hook | `pyproject.toml` | root-relative `[tool.ruff]` | WIRED | no `-c` argument; hook Passed |
| markdownlint hook | generated pages | `exclude` regex | WIRED | explicit families; hook Passed |
| yamllint hook | `.yamllint.yaml` | cwd/ancestor resolution | WIRED | no `-c` argument; hook Passed |
| `clang-tidy-db` | `tests/compile_commands.json` | guard validates the database | WIRED | PASS on the fresh database, exit 0 |
| clang-tidy hook | `.clang-tidy` | root-resolved check set | WIRED | `FormatStyle: file`; pre-push Passed |
| `.clang-tidy` | `lib/common/src/hex.c`, `crc.c` | signed-bitwise fixes | WIRED | seven unsigned casts; native suite green |
| `docs/standards/vscode.md` | `templates/views/mkdocs.yml.tmpl` | mandatory `Standards` nav | WIRED | template + generated nav; strict build exit 0 |
| `docs/standards/vscode.md` | `scripts/clangd-wrapper.sh` | one symlink step | WIRED | guide names the script at lines 46 and 54 |
| `AGENTS.md` | `docs/standards/vscode.md` | routing row | WIRED | row at line 247 |
| `docs/standards/vscode.md` | `esp-clangd 21.1.3` | verbatim argument forwarding | WIRED | the documented attached form executed to exit 0 |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| `homeworks.code-workspace` | `settings["clangd.path"]` | `gen_views.py` mapping → `workspace.json.tmpl` | Yes — literal `${env:HOME}/...` | ✓ FLOWING |
| `.vscode/settings.json` | settings object | hand-maintained mirror of the same contract | Yes — equality test keeps it equal | ✓ FLOWING |
| `generated.manifest` | hashes | `gen_views.py` over real inputs | Yes — `--check` validates | ✓ FLOWING |
| `mkdocs.yml` | `nav` | `mkdocs.yml.tmpl` + generated decision/board entries | Yes — strict build resolves the page | ✓ FLOWING |
| `homeworks/1_3-police-flasher/.clangd` | include resolution | `compile_commands.json` + `--query-driver` globs | Yes — live run reported 0 errors | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Live attached esp-clangd check | `"$HOME/.local/bin/clangd-wrapper" --check=homeworks/1_3-police-flasher/src/main.cpp` | exit 0, `All checks completed, 0 errors` | ✓ PASS |
| Detached form still rejected | `scripts/clangd-wrapper.sh --check homeworks/1_3-police-flasher/src/main.cpp` | exit 1, `Unknown command line argument` | ✓ PASS |
| Stdlib suite | `UV_CACHE_DIR=$TMPDIR/uv-cache python3 -m unittest discover -s scripts/tests` | 356 tests OK | ✓ PASS |
| Tooling config suite | `python3 -m unittest scripts.tests.test_tooling_config` | 74 tests OK | ✓ PASS |
| Scaffold golden tree | `python3 -m unittest scripts.tests.test_new_homework` | 35 tests OK | ✓ PASS |
| Commit hooks | `pre-commit run --all-files` | 12 Passed; `end-of-file-fixer` blocked by the sandbox, see note | ✓ PASS (environment note) |
| Push hooks | `pre-commit run --all-files --hook-stage pre-push` | 2 Passed | ✓ PASS |
| Format check | 23.1.3 dry-run over 60 tracked files | exit 0 | ✓ PASS |
| Database guard | `python3 scripts/clang-tidy-db` | PASS, exit 0 | ✓ PASS |
| Database guard, absent | `python3 scripts/clang-tidy-db --dir <empty>` | exit 1, exact remedy line | ✓ PASS |
| Wrapper failure path | `ESP_CLANGD=/nonexistent` | exit 2, one FAIL line | ✓ PASS |
| Wrapper relative base | `PLATFORMIO_CORE_DIR=relative` | exit 2, one FAIL line | ✓ PASS |
| Wrapper globs | fake clangd, absolute base | exactly two bounded globs, no `**` | ✓ PASS |
| Metadata contract | `uv run scripts/check_metadata.py` | PASS | ✓ PASS |
| Shared native suite | `pio test -d tests -e native` | 73/73 succeeded | ✓ PASS |
| Homework native suite | `pio test -d homeworks/1_3-police-flasher -e native` | 38/38 succeeded | ✓ PASS |
| ESP32-S3 build | `pio run -d homeworks/1_3-police-flasher` | SUCCESS | ✓ PASS |
| Generated views | `uv run scripts/gen_views.py --all --check` | all 8 UNCHANGED, exit 0 | ✓ PASS |
| Strict site build | `mkdocs build --strict` | exit 0 | ✓ PASS |
| Include set preserved | git diff `2d56320^..2d56320`, 44 files | 0 include-multiset mismatches | ✓ PASS |

**Environment note.** The commit-stage `end-of-file-fixer` failed only because the sandbox denies
`open('.vscode/settings.json', 'rb+')` (`PermissionError: Operation not permitted`). It is a
sandbox path restriction, not a repository defect: the file is unchanged, the hook is not one of
the five quality hooks the phase requires, and the same 12 other commit hooks passed. The 06-06
summary recorded the identical sandbox behaviour. No source edit was made.

### Probe Execution

No `scripts/*/tests/probe-*.sh` probes exist and no probe script is named in the plans or
summaries. Step 7c: SKIPPED (not applicable).

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| TOOL-01 | 06-01, 06-04 | clang-format 23.1.3 approximation; clang-tidy runs bugprone/cert/performance/portability on host code | ✓ SATISFIED | Formatter check green over 60 files; `.clang-tidy` + pre-push layer green; ADRs 0012/0013 |
| TOOL-02 | 06-02, 06-06 | esp-clangd via wrapper, per-project `.clangd`, compiledb databases, absolute `--query-driver`, cpptools disabled | ✓ SATISFIED | Wrapper + five `.clangd` + editor contract verified; the live attached check now exits 0 |
| TOOL-03 | 06-03, 06-04 | Layered checks: fast hooks in pre-commit; clang-tidy in pre-push; full checks in CI | ✓ SATISFIED (local layers) / deferred (CI) | 13 commit + 2 push hooks green; the CI layer is Phase 8 (deferred item) |
| TOOL-04 | 06-05, 06-06 | `docs/standards/vscode.md` onboards a VS Code beginner | ✓ SATISFIED | Guide + nav + strict build + `RulebookAndGuideTests`; the guide's no-hardware path is the roadmap SC5 "no-hardware check" (simulation is Phase 7) |

No orphaned requirements: `REQUIREMENTS.md` maps only TOOL-01–TOOL-04 to Phase 6, and every ID
appears in at least one plan's `requirements` field (TOOL-01 in 06-01/06-04; TOOL-02 in
06-02/06-06; TOOL-03 in 06-03/06-04; TOOL-04 in 06-05/06-06).

### Decision Coverage

All 27 trackable CONTEXT.md decisions are honored by shipped artifacts
(`check.decision-coverage-verify`: `total: 27, honored: 27, not_honored: []`).

### Test Quality Audit

| Test File | Linked Req | Active | Skipped | Circular | Assertion Level | Verdict |
|-----------|-----------|--------|---------|----------|-----------------|---------|
| `scripts/tests/test_tooling_config.py` | TOOL-01..04 | 74 | 0 | No | Behavioral (argv capture, exit codes, parsed-object equality, sha256) | ✓ ADEQUATE |
| `scripts/tests/test_new_homework.py` | TOOL-02 | 35 | 0 | No | Behavioral (golden-tree byte equality) | ✓ ADEQUATE |
| `scripts/tests/test_ci_workflows.py` | TOOL-03 | active in 356-test run | 0 | No | Value (textual `on:` key) | ✓ ADEQUATE |

**Disabled tests on requirements:** 0.
**Circular patterns detected:** 0. The tests write temporary fixtures in their own temp roots;
expected values (argv, exit codes, hashes) are hardcoded, not generated by the system under test.
**Insufficient assertions:** 0. `ClangdCheckCommandTests` is non-vacuous: the positive case pins
the attached command, the negative case rejects a detached path, and the third case feeds the
recorded UAT defect through the same pattern.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `.planning/ROADMAP.md` | 317, 331, 336, 351 | `TBD` plan counts for Phases 7–11 | ℹ️ Info | Roadmap placeholders for future phases, not implementation debt; not a phase-modified source file |
| `.planning/STATE.md` | 142–144 | `Needs TBD` todo candidates | ℹ️ Info | Pre-existing todo records, out of scope |
| `06-REVIEW-DISPOSITION.md` | IN-01..IN-05 | open info-level review findings | ℹ️ Info | Deliberately out of scope; none blocks the goal. IN-04 (workspace recommends only PlatformIO) is mitigated by the guide naming both extensions and the unwanted recommendations |

No stubs, placeholder implementations, or hardcoded-empty data paths were found in the phase's
implementation files. `scripts/clang-tidy-hook`'s `return []` returns an empty list of problem
paths, not a stub; `test_the_template_uses_the_closed_placeholder` is a test name, not a
placeholder implementation. The debt-marker scan over the phase's implementation files returned
no `TBD`/`FIXME`/`XXX`.

### Human Verification (UAT Resolution)

The previous pass left three human items. All three were exercised in `06-UAT.md` (status
complete), so no new human item is open:

| UAT test | Result | Evidence |
|----------|--------|----------|
| 1. Live ESP32-S3 include resolution through esp-clangd | pass after G-06-1 closure | The UAT's issue was the detached `--check <file>` form. The attached form now exits 0 with `All checks completed, 0 errors`; this pass re-ran it directly. |
| 2. Format-on-save and Problems panel in a live VS Code | pass | After installing `llvm-vs-code-extensions.vscode-clangd` v0.6.0 and creating the documented symlink, saving restored the committed style and `git diff` stayed empty. |
| 3. No-hardware beginner path from the guide | pass | The named commands work with no board attached; the guide does not promise a simulation path. |

The editor surface remains a human observation by nature; it is recorded as passed rather than
re-opened, and the attached non-editor command that would otherwise have sent the next verifier
back into the defect is now guarded by `ClangdCheckCommandTests`.

### Gaps Summary

No must-have truth is FAILED, no artifact is missing or a stub, no key link is broken, and no
blocker anti-pattern exists. G-06-1 is closed on the current tree: the guide, the validation
table, and this report all carry the attached form
`--check=homeworks/1_3-police-flasher/src/main.cpp`, which was executed in this pass to exit 0
with `All checks completed, 0 errors`; the detached form still fails with exit 1. The phase goal
is implemented and independently green: the formatter gate is check-only, the layered hooks run
exactly where they claim, the editor contract is generated and drift-tested, the onboarding guide
is published in the strict site build, and the friction-log justification is present (F-05, F-18,
and the explicit Phase 6 automation row).

The only outstanding items are explicitly out of phase scope: TOOL-03's CI layer is Phase 8, and
the five info-level review findings are recorded as open, non-blocking observations. The recorded
deviations above (header narrowing after CR-02, the `hex.c`/`crc.c` attribution, the two
lint-driven edits, the gitignored Unity `.editorconfig` copies, and the intentional recorded-defect
fixture) are documented and do not affect goal achievement.

---

_Verified: 2026-10-26T12:24:25Z_
_Verifier: Claude (gsd-verifier)_

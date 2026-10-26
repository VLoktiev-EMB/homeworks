---
phase: 06-developer-experience-and-quality-layering
verified: 2026-10-26T11:53:41Z
status: human_needed
score: 50/51 must-haves verified
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
covered_digest: "v3:sha256:23ad0d15f7eb9ea085d3f812ce375307967f03ce62329c66b55a28c2f558868a"
behavior_unverified: 1
overrides_applied: 0
deferred:
  - truth: "TOOL-03's CI layer — full build, tests, schema, docs, architecture, and simulation checks in CI"
    addressed_in: "Phase 8"
    evidence: "Phase 8 goal: 'Pull requests are gated by a fast, changed-only CI pipeline with one required check'; Phase 6 context explicitly defers CI wiring, the CI matrix, and PR-time checks to Phase 8 (TOOL-05, TOOL-06, SIM-04)."
behavior_unverified_items:
  - truth: "esp-clangd resolves ESP32-S3 includes through per-project .clangd files and explicit absolute --query-driver globs (roadmap SC3)"
    test: "Generate the database with `pio run -d homeworks/1_3-police-flasher -t compiledb`, then run `\"$HOME/.local/bin/clangd-wrapper\" --check homeworks/1_3-police-flasher/src/main.cpp`."
    expected: "`All checks completed, 0 errors`, exit 0, with no unresolved stdbool.h/stdint.h."
    why_human: "Needs a live esp-clangd installation and a generated compilation database. The suite injects a fake $ESP_CLANGD and therefore proves resolution order and argument forwarding, not real include resolution."
human_verification:
  - test: "Follow `docs/standards/vscode.md` on a clean macOS or Linux profile, then open `homeworks.code-workspace` and `homeworks/1_3-police-flasher/src/main.cpp`."
    expected: "No cpptools squiggles; the Problems panel is empty; clangd reports 'All checks completed'."
    why_human: "Live editor behaviour with a real clangd extension and compilation database is not reproducible headlessly."
  - test: "Save an edited C/C++ file in VS Code."
    expected: "Format-on-save applies the committed `.clang-format` (4 spaces, 120 columns, function brace on a new line)."
    why_human: "Format-on-save is an editor action; the repository proves the policy and hook, not the editor's save path."
  - test: "With no board attached, run `pio test -d tests -e native` and `pio run -d homeworks/1_3-police-flasher`."
    expected: "Both commands succeed, matching the guide's no-hardware section."
    why_human: "The guide's beginner acceptance is a human walkthrough; the commands themselves were run during verification and pass."
---

# Phase 6: Developer Experience and Quality Layering Verification Report

**Phase Goal:** A novice can open the workspace, get correct ESP32 IntelliSense, and have formatting and layered quality checks run without guesswork.
**Friction-log justification:** The Phase 4.2 log must contain at least one entry for formatting, IntelliSense, or local feedback; otherwise the tooling is not added.
**Verified:** 2026-10-26T11:53:41Z
**Status:** human_needed
**Re-verification:** No — initial verification

## Friction-Log Justification

**VERIFIED.** `.planning/phases/04.2-tracer-homework-1-3/04.2-FRICTION-LOG.md` contains real
entries and an explicit Phase 6 automation row:

- **F-05** — native `-Wall -Wextra -Werror` fails while the target build stays green; local
  feedback is the friction.
- **F-18** — opening the homework as a workspace folder makes the IDE emit untracked
  `c_cpp_properties.json` and friends because no committed editor configuration exists.
- `## Top automation candidates` row: *"Add clang-format, clang-tidy, and an esp-clangd
  IntelliSense path to the workspace | F-05, F-18 | Phase 6"*.

The justification is present and names this phase by number. The tooling was not added on
speculation.

## Goal Achievement

### Observable Truths

Roadmap success criteria are listed first (R1–R5), followed by the plan-level must-haves.
Plan-level truths add detail; none subtracts a roadmap criterion.

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| R1 | `clang-format --dry-run --Werror` passes with 4-space indent, 120 columns, function braces on a new line, documented as an ESP-IDF approximation | ✓ VERIFIED | `.clang-format` carries all keys; `uvx --from clang-format==23.1.3 clang-format --dry-run --Werror -style=file` over all 60 tracked C/C++ files exits 0; ADR 0012 says "approximation, never equivalence" |
| R2 | clang-tidy runs bugprone, cert, performance, and portability checks on host code in pre-push | ✓ VERIFIED | `.clang-tidy` selects all four families plus readability/clang-analyzer; both pre-push hooks pass with `pre-commit run --all-files --hook-stage pre-push` |
| R3 | esp-clangd resolves ESP32-S3 includes through per-project `.clangd` and explicit absolute `--query-driver` globs; cpptools IntelliSense disabled | ⚠️ PRESENT_BEHAVIOR_UNVERIFIED | All five `.clangd` copies are byte-identical and set `CompilationDatabase: .` + `BuiltinHeaders: QueryDriver`; wrapper forwards exactly two absolute globs (probed); cpptools keys are `disabled`. Live include resolution needs a real esp-clangd + database — see Human Verification |
| R4 | pre-commit runs format, markdownlint, yamllint, ruff, and gitleaks; pre-push runs clang-tidy | ✓ VERIFIED | `pre-commit run --all-files` executes 13 commit hooks and passes; pre-push executes exactly `clang-tidy-db` + `clang-tidy` and passes |
| R5 | `docs/standards/vscode.md` takes a beginner from install to format-on-save, Problems panel, clangd, and a no-hardware check | ✓ VERIFIED | 185-line guide covers install, both extensions, symlink, `pre-commit install`, compiledb, format-on-save, Problems panel, no-hardware commands, Windows/WSL note; nav is generated and `mkdocs build --strict` exits 0 |
| 1.1 | `.clang-format` resolves to 4-space, 120-column, tabs never, function braces on a new line, `ReflowComments` disabled; documented approximation | ✓ VERIFIED | Keys present exactly once; ADR 0012; resolved dump confirmed via the 23.1.3 dry-run |
| 1.2 | clang-format hook is check-only; a failing run leaves every file byte-identical | ✓ VERIFIED | Entry is `clang-format --dry-run --Werror` (no `-i`); independent probe on a misformatted temp file exited 1 and the file remained byte-identical |
| 1.3 | Every tracked C/C++ file (60) passes the pinned 23.1.3 check with zero violations | ✓ VERIFIED | `git ls-files` count = 60; independent 23.1.3 dry-run exits 0 |
| 1.4 | Both templates and their golden fixtures were reformatted by the same pass; `test_new_homework` golden tree stays byte-identical | ✓ VERIFIED | Template and golden `main.cpp` sha256 are equal; `python3 -m unittest scripts.tests.test_new_homework` — 35 tests OK |
| 1.5 | Reformat did not break the build: shared native, homework native, ESP32-S3 build green | ✓ VERIFIED | `pio test -d tests -e native` 73/73; homework native 38/38; `pio run -d homeworks/1_3-police-flasher` SUCCESS |
| 1.6 | No `.editorconfig` exists at the root or in any subtree; committed tool configs are the only style sources | ✓ VERIFIED | No tracked `.editorconfig`; the three files found are Unity copies under gitignored `.pio/libdeps/`, not repository style sources. Note recorded below |
| 1.7 | `SortIncludes` reordered includes without adding, removing, or retyping one | ✓ VERIFIED | Compared the include multiset of all 44 reformatted C/C++ files between `2d56320^` and `2d56320`: 0 mismatches |
| 2.1 | Scaffolded Arduino/ESP-IDF homework carries `.clangd` byte-identical to its golden; `GoldenTreeTests` green with no change to `scripts/new_homework` | ✓ VERIFIED | All five `.clangd` sha256 equal; `test_new_homework` 35 tests OK; `scripts/new_homework` absent from the phase diff |
| 2.2 | The real `homeworks/1_3-police-flasher/` carries the same `.clangd` | ✓ VERIFIED | sha256 equal to both templates and both goldens |
| 2.3 | Every committed `.clangd` sets `CompilationDatabase: .` and `BuiltinHeaders: QueryDriver`; database is the one `scripts/pio/compiledb.py` writes to the project root | ✓ VERIFIED | `.clangd` keys present in all five copies; `compiledb.py` sets `COMPILATIONDB_PATH=$PROJECT_DIR/compile_commands.json` |
| 2.4 | Wrapper resolves `$ESP_CLANGD` → PATH → newest `~/.espressif` build, never aborts under `set -euo pipefail`, exits 2 only on exhaustion | ✓ VERIFIED | `ClangdWrapperTests` (9 cases) pass; source uses `command -v` in `if`, `nullglob`, and count-guarded arrays |
| 2.5 | On exhaustion the wrapper prints one `FAIL clangd-wrapper:` line naming the installation source, the two-step install command, and `docs/standards/vscode.md` | ✓ VERIFIED | Wrapper `fail` message checked in source; `test_nothing_resolvable_prints_the_two_step_install_command` passes; an invalid `$ESP_CLANGD` probe printed one FAIL line and exited 2 |
| 2.6 | A relative `PLATFORMIO_CORE_DIR` is refused with exit 2 and a FAIL line | ✓ VERIFIED | Independent probe: `PLATFORMIO_CORE_DIR=relative` → FAIL line, exit 2 |
| 2.7 | Editor contract carries exactly the eight expected keys in both settings; three cpptools keys are `disabled` | ✓ VERIFIED | Parsed both JSON files: identical 8-key sets; all three cpptools values `disabled`; `EditorContractTests` passes |
| 2.8 | Wrapper passes exactly two bounded absolute `--query-driver` globs and never a recursive wildcard | ✓ VERIFIED | Independent probe with a fake clangd printed exactly `toolchain-*/bin/*,tool-*/bin/*` under an absolute base |
| 2.9 | Generated workspace carries `settings`; `.vscode/settings.json` mirrors it; cpptools disabled, format-on-save for C/C++, `--background-index` | ✓ VERIFIED | Objects are byte-equal; all values checked |
| 2.10 | `clangd.path` is emitted as the literal home-relative wrapper path, so the closed renderer accepts it and multi-root resolves it | ✓ VERIFIED | `gen_views.py:653` supplies `${env:HOME}/.local/bin/clangd-wrapper`; template uses `{{clangd_wrapper_path}}`; generated workspace carries the literal |
| 2.11 | `gen_views.py --all --check` exits 0 and `generated.manifest` records the new workspace hash | ✓ VERIFIED | All eight views UNCHANGED, exit 0; manifest contains the workspace entry and the check validates it |
| 3.1 | `ruff-check`, `yamllint`, and `markdownlint-cli2` each pass on the committed tree | ✓ VERIFIED | All three passed inside `pre-commit run --all-files` |
| 3.2 | ruff configured once in root `pyproject.toml` with py313, 100 columns, E/F/I/UP/B, and the two F821 ignores | ✓ VERIFIED | File matches exactly; no `[project]` table |
| 3.3 | yamllint covers authored YAML only with the specified rules | ✓ VERIFIED | `.yamllint.yaml` extends default with max 120, `document-start: disable`, `truthy` values restricted and key checking off; hook `files` regex matches the named families |
| 3.4 | The four `truthy` findings are workflow trigger keys; `check-keys: false` clears them and all four workflows keep a top-level `on:` | ✓ VERIFIED | All four workflows carry `^on:`; `test_ci_workflows` asserts the textual key |
| 3.5 | markdownlint covers authored Markdown, excludes the named families, disables MD013/MD060, and uses MD024 `siblings_only` | ✓ VERIFIED | Config and hook `exclude` match; no ADR heading renamed |
| 3.6 | No authored YAML or ADR prose is rewritten to satisfy a linter; policy fixes where correct, real fixes only for real defects | ✓ VERIFIED | The two edits in the phase diff are real defects relative to the committed policy: a >120-column URL line in `security.yml` (behaviour-preserving split) and an unlabelled fence in ADR 0006 (`MD040`). Both are the plan's prescribed remedy ("if a further finding appears, fix the file"). Note recorded below |
| 3.7 | Every added hook is check-only: no auto-correct flag, no rewrite or staging | ✓ VERIFIED | `ruff-check` (not `ruff-format`), yamllint and markdownlint with no `--fix`; `test_no_hook_auto_corrects_or_filters_to_all_lines` passes |
| 3.8 | The one-time cleanup changed no behaviour: stdlib suite, metadata checker, generated-view check still green | ✓ VERIFIED | 353 tests OK; `check-metadata` and `gen-views-check` pass in the all-files run |
| 4.1 | Missing/stale database exits 1 with exactly `pio run -d tests -e native -t compiledb`; the guard never generates, writes, or skips | ✓ VERIFIED | Independent probe with an empty root: FAIL line naming that command, exit 1; `test_no_case_writes_a_new_file_into_the_root` passes; fresh database PASS exit 0 |
| 4.2 | Fresh database analyses every in-scope host source with no diagnostic; an injected `bugprone-signed-bitwise` violation makes the hook fail and name it | ✓ VERIFIED | Pre-push hook passes over the real tree; the hook wrapper fails on undescribed/skipped sources (`test_a_skipped_file_fails_the_hook`, `test_a_source_absent_from_the_database_is_rejected_before_running`); the injected-violation probe is recorded in 06-04-SUMMARY D4. Not independently re-injected to avoid mutating the tree |
| 4.3 | A database `file` entry is resolved against its own `directory`, not the repository root | ✓ VERIFIED | Guard and hook both resolve relative entries against the entry directory; `test_a_database_older_than_a_relative_source_exits_one` and `test_a_relative_entry_that_no_longer_exists_is_skipped` pass |
| 4.4 | Both pre-push hook patterns reach the header trees, or — if the header probe shows a standalone header cannot be analysed — the narrowing is recorded in ADR 0013 rather than applied silently | ✓ VERIFIED (escape clause applied) | The probe showed a bare header exits 0 without analysis; review CR-02 then narrowed both patterns to `^(lib/(common|host)/src/.*\.c)$` and made the hook fail on undescribed sources. The contract is recorded in ADR 0013, AGENTS.md, and the guide. Deviation recorded below |
| 4.5 | pre-push runs exactly the two clang-tidy hooks; every fast hook runs only at `pre-commit` | ✓ VERIFIED | `default_stages: [pre-commit]` + explicit `stages:`; the all-files pre-push run executed exactly `clang-tidy-db` and `clang-tidy` |
| 4.6 | `default_install_hook_types` is `[pre-commit, pre-push]` | ✓ VERIFIED | Present in `.pre-commit-config.yaml`; guide's single `pre-commit install` command matches |
| 4.7 | `.clang-tidy` covers bugprone, cert, performance, portability, readability, clang-analyzer; disables `portability-avoid-pragma-once`; `WarningsAsErrors` empty | ✓ VERIFIED | File matches; `ClangTidyConfigTests` passes |
| 4.8 | The seven real `bugprone-signed-bitwise` findings are fixed by unsigned casts; behaviour unchanged and native suite green | ✓ VERIFIED | Four casts in `hex.c` and three in `crc.c` (seven total); 73/73 native tests pass. Plan wording said "in hex.c" — attribution note below |
| 4.9 | The guard's local hook block precedes the `cpp-linter-hooks` block in file order | ✓ VERIFIED | `clang-tidy-db` at line 233, `cpp-linter-hooks` repo at line 254; `test_the_guard_precedes_the_clang_tidy_repository` passes |
| 5.1 | `docs/standards/vscode.md` is named in an explicit `Standards` nav section of the template; generated `mkdocs.yml` carries it; strict build green | ✓ VERIFIED | Template and generated nav both carry `Standards → standards/vscode.md`; `mkdocs build --strict` exit 0 |
| 5.2 | The guide covers install → format-on-save, Problems panel, clangd, no-hardware; macOS/Linux with a Windows WSL note | ✓ VERIFIED | All sections present; `RulebookAndGuideTests.test_the_guide_names_the_editor_surfaces` passes |
| 5.3 | The guide names exactly one repository-specific machine step — the `mkdir -p` + `ln -sf` command — and explains `clangd.path` resolution | ✓ VERIFIED | Guide states it is "the one repository-specific machine step"; `test_the_guide_carries_the_two_step_wrapper_command` passes |
| 5.4 | The guide includes `pre-commit install` as one command wiring both stages and a checklist naming the hooks a contributor meets | ✓ VERIFIED | `pre-commit install` present; guide lists 13 commit hooks + 2 push hooks, matching the config's 15 ids; `test_the_guide_states_the_real_hook_counts` passes |
| 5.5 | The guide names no Homebrew, Debian package-manager, or global/user pip installation | ✓ VERIFIED | No such command; only a false positive on the word "depends" for `apt`; `test_the_guide_names_no_system_package_manager_install` passes |
| 5.6 | The guide explains the no-hardware path with `pio test -d tests -e native` and `pio run -d homeworks/1_3-police-flasher`, and does not claim a simulation path | ✓ VERIFIED | Both commands present; guide explicitly says simulation belongs to Phase 7 |
| 5.7 | The guide records the clang-tidy native-test-TU gap explicitly | ✓ VERIFIED | "Native test translation units are out of scope... belongs to Phase 8 CI" in the guide; same in ADR 0013 |
| 5.8 | ADR 0012 records the approximation; ADR 0013 records esp-clangd/multi-root, `BuiltinHeaders: QueryDriver`, the `--query-driver` execution implication, and the test-TU gap | ✓ VERIFIED | Both ADR bodies carry the required sections; ADR 0013 additionally records the analysed-scope narrowing |
| 5.9 | `docs/decisions/README.md` gains two rows dated 2026-10-26, status `accepted`, linked to the ADRs | ✓ VERIFIED | Rows for 0012 and 0013 present with `accepted` and links |
| 5.10 | `AGENTS.md` gains a `Quality tooling` section, uses four enforcement points, and gains a routing row to `docs/standards/vscode.md` | ✓ VERIFIED | Section present; `ENFORCED:` values include pre-commit, pre-push, CI, review; routing row present; tests pass |
| 5.11 | `generated.manifest` records the new `mkdocs.yml` hash and `gen_views.py --all --check` exits 0 | ✓ VERIFIED | Manifest carries the entry; all views UNCHANGED, exit 0 |

**Score:** 50/51 truths verified (1 present and wired, behavior not exercised).
`behavior_unverified`: 1.

### Recorded Deviations (non-blocking)

1. **Plan 06-04 truth 4.4 (header patterns).** At plan time both pre-push patterns were
   expected to reach `lib/common/include/**` and `lib/host/include/**`. The header probe
   exited 0 because pinned clang-tidy 23.1.3 skips a bare header silently, so the plan's
   escape clause applied. Code review CR-02 (critical) then proved a header-only push passed
   with no analysis at all; the fix narrowed both patterns to `.c` under `lib/*/src` and
   added `scripts/clang-tidy-hook`, which fails when a source has no compile command. The
   final contract is recorded in ADR 0013, AGENTS.md, and the guide, so it is not silent.
   This is the correct resolution of the defect the plan's mechanism would have preserved;
   it is recorded here because it differs from the plan text.
2. **Plan 06-04 truth 4.8 wording.** The seven `bugprone-signed-bitwise` findings are four in
   `lib/common/src/hex.c` and three in `lib/common/src/crc.c`, not seven in `hex.c`. The
   intent — fix every real finding, change no behaviour, keep the native suite green — is met.
3. **Plan 06-03 truth 3.6.** The phase diff contains two authored-file edits that a strict
   reading calls "rewritten to satisfy a linter": a >120-column URL in
   `.github/workflows/security.yml` split across three variables, and a `text` language tag
   added to a fence in ADR 0006. Both are real defects relative to the committed policy and
   are the plan's own prescribed remedy for a residual finding; neither silences a rule.
4. **Plan 06-01 truth 1.6.** Three `.editorconfig` files exist under gitignored
   `.pio/libdeps/native/.../Unity/` and `.../Unity/`. They are downloaded dependency build
   output, untracked, and not style sources for this repository; no tracked or authoritative
   `.editorconfig` exists.

### Deferred Items

Items not yet met but explicitly addressed in later milestone phases.

| # | Item | Addressed In | Evidence |
|---|------|-------------|----------|
| 1 | TOOL-03's CI layer: full build, tests, schema, docs, architecture, and simulation checks in CI | Phase 8 | Phase 8 goal: "Pull requests are gated by a fast, changed-only CI pipeline with one required check"; Phase 6 context defers CI wiring (TOOL-05, TOOL-06, SIM-04) |

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `.clang-format` | single C/C++ style source | ✓ VERIFIED | All D-02 keys, documented approximation |
| `.clang-tidy` | host-only, warnings-first policy | ✓ VERIFIED | Six families, empty `WarningsAsErrors`, unanchored header filter |
| `.pre-commit-config.yaml` | layered check-only hooks | ✓ VERIFIED | 13 commit + 2 push hooks; pinned revs; explicit stages |
| `scripts/clangd-wrapper.sh` | discovered esp-clangd launcher | ✓ VERIFIED | mode 100755, bounded globs, exit-2 vocabulary |
| `scripts/clang-tidy-db` | read-only database guard | ✓ VERIFIED | mode 100755, exit 0/1/2, names the remedy |
| `scripts/clang-tidy-hook` | fail on unanalysed source | ✓ VERIFIED | mode 100755, database membership pre-check + skip-marker check |
| `templates/homework-*/`, goldens, real homework `.clangd` | five byte-identical fragments | ✓ VERIFIED | identical sha256 |
| `templates/views/workspace.json.tmpl` | emitted editor contract | ✓ VERIFIED | `settings` block with closed placeholder |
| `.vscode/settings.json` | single-folder mirror | ✓ VERIFIED | equal to workspace `settings` |
| `pyproject.toml`, `.yamllint.yaml`, `.markdownlint-cli2.jsonc` | one policy per tool | ✓ VERIFIED | match plan |
| `docs/standards/vscode.md` | beginner guide | ✓ VERIFIED | 185 lines, all required sections |
| `docs/decisions/0012-*.md`, `0013-*.md`, `README.md` | two ADRs + rows | ✓ VERIFIED | accepted, 2026-10-26 |
| `AGENTS.md` | Quality tooling section, four points, routing row | ✓ VERIFIED | present |
| `scripts/tests/test_tooling_config.py` | machine checks | ✓ VERIFIED | 71 tests, 9 classes |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `.pre-commit-config.yaml` clang-format | `.clang-format` | `-style=file` | WIRED | entry + args verified |
| template `main.cpp` | golden `main.cpp` | same pinned reformat | WIRED | sha256 equal |
| template `.clangd` | golden `.clangd` | golden-tree equality | WIRED | sha256 equal |
| `.clangd` `CompilationDatabase` | `scripts/pio/compiledb.py` | database written to project root | WIRED | `$PROJECT_DIR/compile_commands.json` |
| `workspace.json.tmpl` | `.vscode/settings.json` | `EditorContractTests` equality | WIRED | identical parsed objects |
| ruff-check hook | `pyproject.toml` | root-relative `[tool.ruff]` | WIRED | no `-c` argument |
| markdownlint hook | generated pages | `exclude` regex | WIRED | explicit families |
| yamllint hook | `.yamllint.yaml` | cwd/ancestor resolution | WIRED | no `-c` argument |
| `clang-tidy-db` | `tests/compile_commands.json` | guard validates the database | WIRED | PASS on fresh database |
| clang-tidy hook | `.clang-tidy` | root-resolved check set | WIRED | `FormatStyle: file`; pre-push passes |
| `.clang-tidy` | `lib/common/src/hex.c` | signed-bitwise fixes | WIRED | four unsigned casts; suite green |
| `docs/standards/vscode.md` | `templates/views/mkdocs.yml.tmpl` | mandatory `Standards` nav | WIRED | generated nav + strict build |
| `docs/standards/vscode.md` | `scripts/clangd-wrapper.sh` | one symlink step | WIRED | guide names the script |
| `AGENTS.md` | `docs/standards/vscode.md` | routing row | WIRED | row 247 |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| `homeworks.code-workspace` | `settings["clangd.path"]` | `gen_views.py` mapping → `workspace.json.tmpl` | Yes — literal `${env:HOME}/...` | ✓ FLOWING |
| `.vscode/settings.json` | settings object | hand-maintained mirror of the same contract | Yes — drift test keeps it equal | ✓ FLOWING |
| `generated.manifest` | hashes | `gen_views.py` over real inputs | Yes — `--check` validates | ✓ FLOWING |
| `mkdocs.yml` | `nav` | `mkdocs.yml.tmpl` + generated decision/board entries | Yes — strict build resolves the page | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Stdlib suite | `python3 -m unittest discover -s scripts/tests` | 353 tests OK | ✓ PASS |
| Tooling config suite | `python3 -m unittest scripts.tests.test_tooling_config` | 71 tests OK | ✓ PASS |
| Scaffold golden tree | `python3 -m unittest scripts.tests.test_new_homework` | 35 tests OK | ✓ PASS |
| Commit hooks | `pre-commit run --all-files` | 13 hooks pass | ✓ PASS |
| Push hooks | `pre-commit run --all-files --hook-stage pre-push` | 2 hooks pass | ✓ PASS |
| Format check | 23.1.3 dry-run over 60 tracked files | exit 0 | ✓ PASS |
| Format hook is non-mutating | dry-run on a misformatted temp file | exit 1, bytes identical | ✓ PASS |
| Database guard | `python3 scripts/clang-tidy-db` | PASS, exit 0 | ✓ PASS |
| Database guard, absent | `python3 scripts/clang-tidy-db --dir <empty>` | exit 1, exact remedy | ✓ PASS |
| Wrapper failure path | `ESP_CLANGD=/nonexistent` | exit 2, one FAIL line | ✓ PASS |
| Wrapper relative base | `PLATFORMIO_CORE_DIR=relative` | exit 2, one FAIL line | ✓ PASS |
| Wrapper globs | fake clangd, absolute base | exactly two bounded globs | ✓ PASS |
| Shared native suite | `pio test -d tests -e native` | 73/73 | ✓ PASS |
| Homework native suite | `pio test -d homeworks/1_3-police-flasher -e native` | 38/38 | ✓ PASS |
| ESP32-S3 build | `pio run -d homeworks/1_3-police-flasher` | SUCCESS | ✓ PASS |
| Generated views | `uv run scripts/gen_views.py --all --check` | all UNCHANGED, exit 0 | ✓ PASS |
| Strict site build | `mkdocs build --strict` | exit 0 | ✓ PASS |
| Include set preserved | git diff `2d56320^..2d56320`, 44 files | 0 include-multiset mismatches | ✓ PASS |

### Probe Execution

No `scripts/*/tests/probe-*.sh` probes exist and no probe script is named in the plans or
summaries. Step 7c: SKIPPED (not applicable).

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| TOOL-01 | 06-01, 06-04 | clang-format 23.1.3 approximation; clang-tidy runs bugprone/cert/performance/portability on host code | ✓ SATISFIED | Formatter check green over 60 files; `.clang-tidy` + pre-push layer green; ADRs 0012/0013 |
| TOOL-02 | 06-02 | esp-clangd via wrapper, per-project `.clangd`, compiledb databases, absolute `--query-driver`, cpptools disabled | ✓ SATISFIED | Wrapper + five `.clangd` + editor contract verified; live resolution is the one behavior-unverified item |
| TOOL-03 | 06-03, 06-04 | Layered checks: fast hooks in pre-commit; clang-tidy in pre-push; full checks in CI | ✓ SATISFIED (local layers) / deferred (CI) | 13 commit + 2 push hooks green; the CI layer is Phase 8 (deferred item) |
| TOOL-04 | 06-05 | `docs/standards/vscode.md` onboards a VS Code beginner | ✓ SATISFIED | Guide + nav + strict build + RulebookAndGuideTests |

No orphaned requirements: REQUIREMENTS.md maps only TOOL-01–TOOL-04 to Phase 6, and every ID
appears in a plan's `requirements` field.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `.planning/ROADMAP.md` | 317, 331, 346, 360, 375, 393–397 | `TBD` plan counts for Phases 7–11 | ℹ️ Info | Roadmap placeholders for future phases, not implementation debt; not a phase-modified source file |
| `.planning/STATE.md` | 142–144 | `Needs TBD` todo candidates | ℹ️ Info | Pre-existing todo records, out of scope |
| `06-REVIEW.md` IN-01..IN-05 | — | Open info-level review findings | ℹ️ Info | Deliberately out of scope (recorded in 06-REVIEW-DISPOSITION.md); none blocks the goal. IN-04 (workspace recommends only PlatformIO, not clangd) is the most user-visible |

No stubs, placeholder implementations, or hardcoded-empty data paths were found in the phase's
implementation files.

### Human Verification Required

#### 1. Live ESP32-S3 include resolution

**Test:** Generate the database with `pio run -d homeworks/1_3-police-flasher -t compiledb`,
then run `"$HOME/.local/bin/clangd-wrapper" --check homeworks/1_3-police-flasher/src/main.cpp`.
**Expected:** `All checks completed, 0 errors`, exit 0, with no unresolved `stdbool.h`/`stdint.h`.
**Why human:** Needs a live esp-clangd installation and a real database; the suite fakes
`$ESP_CLANGD`.

#### 2. Format-on-save and the Problems panel

**Test:** Open `homeworks.code-workspace` and `src/main.cpp` in VS Code; save an edited C/C++ file.
**Expected:** The Problems panel is empty and saving reformats to the committed style.
**Why human:** Editor behaviour is not reproducible headlessly.

#### 3. No-hardware check path

**Test:** With no board attached, run `pio test -d tests -e native` and
`pio run -d homeworks/1_3-police-flasher`.
**Expected:** Both succeed.
**Why human:** The guide's beginner acceptance is a human walkthrough (both commands pass in
verification).

### Gaps Summary

No must-have truth is FAILED and no artifact, key link, or blocker anti-pattern is broken.
The phase goal is implemented and independently green: the formatter gate is check-only, the
layered hooks run exactly where they claim, the editor contract is generated and drift-tested,
and the onboarding guide is published in the strict site build. The friction-log justification
is present (F-05, F-18, and the explicit Phase 6 automation row).

Two areas need a human decision or observation rather than a code change:

1. **One behavior-unverified truth (R3):** live esp-clangd include resolution cannot be
   exercised headlessly; it is the only item separating a clean 51/51 from the current 50/51.
2. **Open info-level review findings IN-01..IN-05.** IN-04 is a genuine onboarding wart: the
   workspace `extensions.recommendations` lists only `platformio.platformio-ide`, while the
   guide requires `llvm-vs-code-extensions.vscode-clangd` too. A novice who accepts the
   workspace prompt gets no language server until they read the guide. This does not break any
   must-have, but it is the one place where "open the workspace and get IntelliSense without
   guesswork" still depends on following the guide.

The plan-level deviations recorded above (header narrowing after CR-02, the `hex.c`/`crc.c`
attribution, the two lint-driven edits, and the gitignored Unity `.editorconfig` copies) are
documented and do not affect goal achievement.

---

_Verified: 2026-10-26T11:53:41Z_
_Verifier: Claude (gsd-verifier)_

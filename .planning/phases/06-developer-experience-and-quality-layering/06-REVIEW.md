---
phase: 06-developer-experience-and-quality-layering
reviewed: 2026-10-26T11:32:58Z
depth: standard
files_reviewed: 82
files_reviewed_list:
  - .clang-format
  - .clang-tidy
  - .github/pull_request_template.md
  - .github/workflows/security.yml
  - .gitignore
  - .markdownlint-cli2.jsonc
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
findings:
  critical: 2
  warning: 3
  info: 5
  total: 10
status: issues_found
---

# Phase 06: Code Review Report

**Reviewed:** 2026-10-26T11:32:58Z
**Depth:** standard
**Files Reviewed:** 82
**Status:** issues_found

## Summary

The phase's mechanical work checks out. The C/C++ diff is a clang-format pass plus the
seven intentional `bugprone-signed-bitwise` casts in `lib/common/src/hex.c` and
`lib/common/src/crc.c`; a token-level comparison found no other semantic change, and the
pinned clang-format 23.1.3 runs green over every tracked `.c/.h/.cpp` file. The committed
generated views are byte-identical (`gen_views.py --all --check` exits 0), `ruff check .` is
clean, yamllint 1.38.0 is clean over the hook's file set, and the whole `scripts/tests`
suite (339 tests) passes. The editor contract, the `.clangd` copies, the ADR pair, the
mkdocs nav, and the pre-commit stage layering are internally consistent.

The quality-layer semantics are not all sound. Two defects make the pre-push clang-tidy
layer report less analysis than it claims: the header filter is anchored so every
diagnostic that originates in a header is discarded, and a header-only change is passed to
clang-tidy as a translation unit that is silently skipped while the hook exits 0. A third
defect lets the database guard pass when a newly added source is missing from the database,
which produces the same silent skip for new code. The remaining findings are robustness,
test-strength, and documentation-accuracy issues.

## Critical Issues

### CR-01: `HeaderFilterRegex` is anchored to a repository-relative prefix, so every header diagnostic is discarded

**File:** `.clang-tidy:49`
**Issue:** clang-tidy matches `HeaderFilterRegex` against the header's `FileEntry` path, not
a repository-relative path (`ClangTidyDiagnosticConsumer::checkFilters` in LLVM uses
`const StringRef FileName(File->getName())` and then `getHeaderFilter()->match(FileName)`).
Every diagnostic whose `FileName` does not match leaves `LastErrorRelatesToUserCode` false
and is dropped. The database the pre-push hook uses resolves headers through absolute
include directories: `tests/compile_commands.json` carries
`-I/Users/.../lib/common/include` and `-I/Users/.../lib/host/include`, so a header is
reported as `/Users/.../lib/common/include/common/hex.h`. `^(lib|homeworks)/.*` does not
match that string. Consequence: no `bugprone-*`, `cert-*`, `performance-*`,
`portability-*`, `readability-*`, or `clang-analyzer-*` finding that originates in
`lib/common/include`, `lib/host/include`, or `lib/port/include` can ever be reported — not
by the pre-push hook and not by clangd's clang-tidy integration, which reads the same file.
This silently contradicts the phase's stated scope in `AGENTS.md:178` ("clang-tidy ...
analyses host-compiled code — `lib/common`, `lib/host`, and the `lib/port` headers"). The
current `ClangTidyConfigTests` only asserts that the key exists, so the suite cannot catch
this.
**Fix:**
```yaml
# .clang-tidy — unanchored, so it matches both a relative path and the absolute
# path clang emits for a PlatformIO include directory.
HeaderFilterRegex: "(^|/)(lib|homeworks)/.*"
```
Add a regression probe that injects a `bugprone-*` violation into
`lib/common/include/common/hex.h`, runs the pinned clang-tidy on a `.c` that includes it
(without cpp-linter's line filter), and requires the diagnostic to be printed.

### CR-02: A header-only push passes the pre-push gate with no analysis at all

**File:** `.pre-commit-config.yaml:246-252` (scope claim: `AGENTS.md:178`, `docs/decisions/0013-clangd-multi-root-contract.md:190-199`)
**Issue:** The hook's `files` pattern deliberately includes the `include` trees, but headers
are not translation units in `tests/compile_commands.json` (the database has 11 entries,
all `.c`). cpp-linter-hooks treats a trailing `.h` argument as a source file
(`SOURCE_FILE_SUFFIXES` contains `.h`), so a header-only push becomes
`clang-tidy -p tests ... lib/port/include/port/gpio.h`. `ClangTool` finds no compile
command, prints `Skipping <file>. Compile command not found.`, and returns 2, but
`clang-tidy`'s `main` ignores `ClangTool`'s status and exits 0. `cpp-linter-hooks` then
treats exit 0 with no `warning:`/`error:` text as success and, because it prints output only
on a non-zero result, hides the "Skipping" line entirely. The hook is green, the guard is
green, and nothing was analysed. The phase's own "header probe exited 0" measurement is
consistent with this skip rather than with analysis; ADR 0013 already admits that a zero
exit does not prove per-header analysis. This is the exact failure the guard's own comment
calls "worse than no guard".
**Fix:** Pick one honest contract:
- Narrow both hook `files` patterns to `\.c$`, state that headers are analysed only through
  an including translation unit (fix CR-01 so those diagnostics surface), and correct
  `AGENTS.md` and ADR 0013.
- Or give each analysed header a real compile command (for example a generated
  `compile_flags.txt`/synthetic `-fsyntax-only` entry), so clang-tidy does not skip it.
- Or, at pre-push, map a changed header to an owning `.c` file and analyse that.
In every variant, make the hook fail when its output contains
`Skipping ... Compile command not found.` so a no-op can never report success.

## Warnings

### WR-01: The database guard passes when a newly added source is missing from the database

**File:** `scripts/clang-tidy-db:121-132`
**Issue:** `stale_inputs` compares the database mtime only against the paths the database
already describes plus the two configuration inputs. A newly added
`lib/common/src/new_feature.c` is not described, so it is not a candidate. Reproduced on a
fixture: with the database and configuration inputs older than the new source, the guard
prints `PASS clang-tidy-db: ... fresher than 2 input(s)` and exits 0. The new source is then
handed to clang-tidy, which skips it for the CR-02 reason (`Compile command not found`),
and the hook reports success. The guard therefore fails at the one event it exists for: new
code arriving without a regenerated database.
**Fix:** Build the candidate set from the analyser scope on disk, not only from the
database. Compare the database's resolved `file` set with every existing `.c` under
`lib/common/src` and `lib/host/src`; a scoped source absent from the database is stale and
exits 1 with the existing remedy. Leave headers out — they are legitimately not compile
units. Add a test that creates a new `.c` and expects exit 1.

### WR-02: The wrapper can select a non-executable esp-clangd and exit 1, contradicting its documented exit codes

**File:** `scripts/clangd-wrapper.sh:51-58,73-75` (contract: `:19-22`)
**Issue:** Step 1 validates `$ESP_CLANGD` with `-f`/`-x`, but the discovered fallback
candidates are not checked. With a partially installed
`~/.espressif/tools/esp-clangd/esp-*/esp-clangd/bin/clangd` whose execute bit is missing,
the wrapper `exec`s it and the shell fails with
`.../clangd: Permission denied` and exit 1. Reproduced. The documented contract is exit 2
with a `FAIL clangd-wrapper:` remedy, which is what the onboarding guide's troubleshooting
assumes.
**Fix:** Filter or validate the fallback before `exec`:
```bash
shopt -s nullglob
candidates=("$HOME"/.espressif/tools/esp-clangd/esp-*/esp-clangd/bin/clangd)
shopt -u nullglob
executable=()
for candidate in "${candidates[@]}"; do
  [ -x "$candidate" ] && executable+=("$candidate")
done
[ "${#executable[@]}" -gt 0 ] && CLANGD="$(printf '%s\n' "${executable[@]}" | sort -V | tail -1)"
```
Add a `ClangdWrapperTests` case whose newest candidate is mode 0644 and assert exit 2 with
the `FAIL clangd-wrapper:` prefix.

### WR-03: The onboarding guide overstates what is pinned and how many hooks run

**File:** `docs/standards/vscode.md:7-9,131-132`
**Issue:** "Every formatter and linter is pinned in pre-commit. You never install one by
hand" is contradicted by the same page: esp-clangd is installed by hand from the Espressif
installer and is the on-save formatter and language server. "Five hooks run on commit" is
also inaccurate: `.pre-commit-config.yaml` declares 13 pre-commit hooks. The guide omits
`trailing-whitespace`, `end-of-file-fixer`, `check-merge-conflict`,
`check-added-large-files`, `no-generated-files`, `check-architecture`, `check-metadata`,
and `gen-views-check`, so a beginner blocked by a metadata or generated-view failure has no
documented explanation. `test_the_guide_lists_every_hook` checks only the seven linter ids,
so the omission is invisible to the suite.
**Fix:** Say that the *gate's* linters are pinned and that esp-clangd is the one
hand-installed editor component; either list every commit hook, or retitle the section
"Lint hooks you will meet" and state that the hygiene, metadata, and generated-view hooks
carry their own messages. Extend the guide test to the full hook set.

## Info

### IN-01: Unreachable branch in `described_paths`

**File:** `scripts/clang-tidy-db:115-116`
**Issue:** After `base = root / base` (or `base = root`), `base` is absolute, so
`source = base / source` is already absolute; the second `if not source.is_absolute()`
never fires. It is dead code that suggests a fallback the function does not have.
**Fix:** Delete it, or use it to implement the missing case: a relative `directory` should
be resolved against the compilation database's own directory first.

### IN-02: The guard-ordering rationale is wrong about pre-commit behavior

**File:** `.pre-commit-config.yaml:213-218`; test `scripts/tests/test_tooling_config.py:702-707`
**Issue:** pre-commit runs every hook and reports all failures; it does not stop at the
first failing hook unless `fail_fast: true`. The claim that a guard placed after the
clang-tidy repository "would never protect the gate" is false — the push is blocked either
way. The ordering only changes output order.
**Fix:** Either set `fail_fast: true` if short-circuiting (so the guard's remedy is the only
message) is the intent, or reword the comment and the test docstring as an output-order
preference rather than a correctness requirement.

### IN-03: A guide test is satisfied by a longer hook id

**File:** `scripts/tests/test_tooling_config.py:827-831`
**Issue:** `self.assertIn("clang-tidy", text)` is satisfied by the `clang-tidy-db` bullet.
Deleting the standalone `clang-tidy` entry from the guide would not fail the test.
**Fix:** Match the bullet form (for example ``"- `clang-tidy` —"``) or parse the section into
ids before asserting.

### IN-04: The workspace recommends only one of the two required extensions

**File:** `templates/views/workspace.json.tmpl:21-24` and `homeworks.code-workspace:41-43`
**Issue:** `extensions.recommendations` lists only `platformio.platformio-ide`, while the
guide requires `llvm-vs-code-extensions.vscode-clangd` as well. A contributor who accepts
the workspace prompt gets PlatformIO but no language server.
**Fix:** Add `llvm-vs-code-extensions.vscode-clangd` to the template's recommendations,
regenerate the workspace, and assert both ids in `EditorContractTests`.

### IN-05: Ruff targets Python 3.13 while the entry scripts declare 3.11

**File:** `pyproject.toml:13`; declared minimums in `scripts/gen_views.py:3` and `scripts/affected.py:3`
**Issue:** the scripts carry `requires-python = ">=3.11"`, but ruff lints with
`target-version = "py313"`. A `UP` fix gated on 3.12+ (for example `UP040`, which rewrites a
`TypeAlias` assignment into a PEP 695 `type` statement) would be offered and would break the
declared 3.11 minimum if applied. The hook is check-only, so this is a latent trap rather
than a current break.
**Fix:** Set `target-version = "py311"`, or raise the scripts' `requires-python` to match.

---

_Reviewed: 2026-10-26T11:32:58Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_

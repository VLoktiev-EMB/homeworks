---
phase: 06-developer-experience-and-quality-layering
plan: 02
subsystem: developer-tooling
tags: [clangd, esp-clangd, vscode, multi-root, query-driver, generator]

# Dependency graph
requires:
  - phase: 06-developer-experience-and-quality-layering
    provides: the check-only hook posture from 06-01 and the generator-owned view pattern from Phase 5
provides:
  - "one byte-identical per-project .clangd shipped by both homework templates, both goldens, and the real homework (D-16)"
  - "scripts/clangd-wrapper.sh, a discover-never-hardcode esp-clangd launcher with two bounded --query-driver globs (D-17)"
  - "a single editor contract emitted into homeworks.code-workspace and mirrored to .vscode/settings.json under a drift test (D-19a)"
  - "ClangdConfigTests, ClangdWrapperTests, and EditorContractTests as stdlib machine checks (TOOL-02)"
affects: [06-05, phase-08-ci]

actuals:
  tokens: 6002
  tasks: 3
  commits: 3
  plan_head_before: 065477d72cfeea61b7cf9c3208e7770fcb467b81
  plan_head_after: cc44760bf6ba1d344c4c7bf22acf6bc3db5ba853

tech-stack:
  added: [esp-clangd 21.1.3 discovery, clangd CompileFlags.BuiltinHeaders]
  patterns:
    - "Discover-never-hardcode: resolve a versioned tool directory at run time"
    - "Nullglob array fallback instead of an `ls | sort | tail` pipeline under pipefail"
    - "Generator-owned editor contract: a closed `{{clangd_wrapper_path}}` placeholder carries a literal `${env:HOME}` value"
    - "Two-scope mirror: workspace `settings` for multi-root, `.vscode/settings.json` for single-folder, kept equal by a stdlib drift test"

key-files:
  created:
    - scripts/clangd-wrapper.sh
    - .vscode/settings.json
    - templates/homework-arduino/.clangd
    - templates/homework-espidf/.clangd
    - scripts/tests/fixtures/golden/homework-arduino/.clangd
    - scripts/tests/fixtures/golden/homework-espidf/.clangd
    - homeworks/1_3-police-flasher/.clangd
  modified:
    - scripts/tests/test_tooling_config.py
    - templates/views/workspace.json.tmpl
    - scripts/gen_views.py
    - homeworks.code-workspace
    - generated.manifest

key-decisions:
  - "The `.clangd` fragment is a placeholder-free static file, so the scaffold ships it through the existing os.walk with no change to scripts/new_homework."
  - "The wrapper tests `command -v` inside an `if` and builds candidates with `shopt -s nullglob`, so no lookup aborts under `set -euo pipefail` before the diagnostic can print."
  - "The `settings` block precedes `extensions` in workspace.json.tmpl, preserving the existing verbatim-suffix assertion on the extensions block."
  - "The editor contract is emitted from the template, never hand-edited into the workspace; `.vscode/settings.json` is the only hand-maintained mirror and the drift test keeps it equal."

patterns-established:
  - "A tool directory that embeds a build date is resolved at run time; no committed file names it."
  - "A generator mapping value is the sanctioned escape hatch for text the template renderer rejects (`${...}`)."
  - "An editor contract has two scopes; a stdlib test compares the parsed values and the explicit key set."

requirements-completed: [TOOL-02]

coverage:
  - id: D1
    description: "Five byte-identical `.clangd` files carry CompilationDatabase `.`, BuiltinHeaders QueryDriver, the seven Xtensa flags, and both diagnostics; the scaffold and golden tree prove it end to end."
    requirement: TOOL-02
    verification:
      - kind: unit
        ref: "scripts/tests/test_tooling_config.py#ClangdConfigTests"
        status: pass
      - kind: integration
        ref: "python3 -m unittest scripts.tests.test_new_homework (35 tests, GoldenTreeTests green)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The wrapper resolves `$ESP_CLANGD`, then PATH, then the newest `~/.espressif` build; refuses a relative PLATFORMIO_CORE_DIR; and forwards exactly the two bounded absolute `--query-driver` globs."
    requirement: TOOL-02
    verification:
      - kind: unit
        ref: "scripts/tests/test_tooling_config.py#ClangdWrapperTests (9 tests)"
        status: pass
      - kind: other
        ref: "bash -n scripts/clangd-wrapper.sh && test -x scripts/clangd-wrapper.sh"
        status: pass
    human_judgment: false
  - id: D3
    description: "The editor contract is emitted into homeworks.code-workspace and mirrored to .vscode/settings.json: exactly eight keys, cpptools disabled, format-on-save via clangd, --background-index, the home-relative wrapper path."
    requirement: TOOL-02
    verification:
      - kind: unit
        ref: "scripts/tests/test_tooling_config.py#EditorContractTests (8 tests)"
        status: pass
      - kind: integration
        ref: "uv run scripts/gen_views.py --all --check"
        status: pass
    human_judgment: false
  - id: D4
    description: "A live VS Code window resolves ESP32-S3 includes through esp-clangd with 0 errors."
    requirement: TOOL-02
    verification:
      - kind: manual_procedural
        ref: "06-VALIDATION.md: clangd-wrapper --check homeworks/1_3-police-flasher/src/main.cpp -> All checks completed, 0 errors"
        status: unknown
    human_judgment: true
    rationale: "No stdlib test can prove a running editor server resolves includes; the plan records the exact command and expected output in 06-VALIDATION.md."

duration: 3min
completed: 2026-10-26
status: complete
---

# Phase 6 Plan 02: ESP32-S3 IntelliSense Contract and Editor Layering Summary

**One discoverable esp-clangd launcher, five byte-identical per-project `.clangd` fragments, and a generator-owned editor contract emitted into the multi-root workspace and mirrored under a drift test**

## Performance

- **Duration:** 3 min
- **Started:** 2026-10-26T10:59:27Z
- **Completed:** 2026-10-26T11:02:11Z
- **Tasks:** 3
- **Files modified:** 12 (8 created, 5 modified; 563 insertions, 3 deletions)

## Accomplishments

- Both homework templates, both golden fixtures, and the real `1_3-police-flasher` carry one byte-identical `.clangd` (sha256 `6e2ecf9c…`), proven by `ClangdConfigTests` and the unchanged `GoldenTreeTests`.
- `CompilationDatabase: .` points at the root database `scripts/pio/compiledb.py` writes, and `BuiltinHeaders: QueryDriver` gives esp-clangd 21.1.3 the system headers it otherwise lacks.
- `scripts/clangd-wrapper.sh` (mode 100755) resolves `$ESP_CLANGD`, then `esp-clangd` on PATH, then the newest `~/.espressif` build, and execs clangd with exactly two absolute `--query-driver` globs.
- The wrapper's guarded resolution survives `set -euo pipefail`: a `nullglob` array replaces the pipeline that would abort before the fallback diagnostic.
- The eight-key editor contract lives in `templates/views/workspace.json.tmpl`, reaches every multi-root folder through `homeworks.code-workspace`, and is mirrored to `.vscode/settings.json` under `EditorContractTests`.
- `gen_views.py --all --check` exits 0 and `generated.manifest` records the new workspace hash (`c3c08c02…`, 925 bytes).

## Task Commits

Each task was committed atomically:

1. **Task 1: Scaffolded project resolves ESP32 headers through its own `.clangd`** - `d314e7b` (feat)
2. **Task 2: Discover-never-hardcode esp-clangd wrapper with bounded `--query-driver` globs** - `1756a26` (feat)
3. **Task 3: One editor contract emitted twice and kept equal by a drift test** - `cc44760` (feat)

## Files Created/Modified

- `templates/homework-arduino/.clangd`, `templates/homework-espidf/.clangd` - the shipped fragment.
- `scripts/tests/fixtures/golden/homework-{arduino,espidf}/.clangd` - the golden-tree copies, generated through `temp_root.render_tree`.
- `homeworks/1_3-police-flasher/.clangd` - the real-tree copy (D-16 hand-add, once).
- `scripts/clangd-wrapper.sh` - 100755 launcher with the four-step resolution and the bounded driver allowlist.
- `templates/views/workspace.json.tmpl` - the generator-owned `settings` block with `{{clangd_wrapper_path}}`.
- `scripts/gen_views.py` - the `clangd_wrapper_path` mapping value in `_render_workspace`.
- `.vscode/settings.json` - the single-folder-open slice of the contract.
- `homeworks.code-workspace`, `generated.manifest` - regenerated, never hand-edited.
- `scripts/tests/test_tooling_config.py` - `ClangdConfigTests`, `ClangdWrapperTests`, `EditorContractTests` (28 tests total in the module).

## Decisions Made

- The `.clangd` fragment is placeholder-free, so `scripts/new_homework` needed no change: `os.walk` already includes dotfiles and only skips `template.yaml`.
- The golden fixtures were produced through `render_tree` into a temporary source containing only `.clangd`, which keeps the "never hand-copy" rule without re-rendering unrelated golden files.
- `settings` is placed before `extensions` in the workspace template so the existing `test_extensions_block_is_the_templates_own_bytes` verbatim-suffix assertion stays valid; a `settings` block after `extensions` would have put the rendered placeholder inside that suffix.
- The renderer's dollar-brace rejection is preserved by expressing `${env:HOME}/.local/bin/clangd-wrapper` as a mapping value, which `re.sub` never rescans.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Harness guard rejected the plan's literal verify and regeneration commands**
- **Found during:** Task 2 / Task 3
- **Issue:** The worktree-isolation guard refuses a shell command that assigns `HOME` and refuses `${TMPDIR:-/tmp}`-style runtime values. The plan's `bash -c 'HOME=$(mktemp -d) …'` verify and `UV_CACHE_DIR="${TMPDIR:-/tmp}/uv-cache"` regeneration form are both rejected by the harness, not by the code.
- **Fix:** Ran the regeneration with a literal `UV_CACHE_DIR=/tmp/uv-cache`, and proved the empty-environment behaviour through `ClangdWrapperTests`, which passes a controlled `env` to `subprocess.run` rather than the shell. No production file changed for this.
- **Files modified:** none (execution mechanics only).
- **Verification:** `ClangdWrapperTests.test_empty_espressif_tree_exits_2_without_a_shell_diagnostic` and `test_nothing_resolvable_prints_the_two_step_install_command` pass.
- **Committed in:** n/a (gate form only).

**2. [Rule 3 - Blocking] Workspace template ordering constrained by an existing generator test**
- **Found during:** Task 3
- **Issue:** `test_extensions_block_is_the_templates_own_bytes` compares the template and output from the `"extensions"` marker onward verbatim. Appending `settings` after `extensions` would have placed the substituted `${env:HOME}` value inside that suffix and failed the test.
- **Fix:** Emitted `settings` between `folders` and `extensions`; the plan does not constrain sibling order, and both the suffix assertion and the tab-indent assertion stay valid.
- **Files modified:** `templates/views/workspace.json.tmpl`.
- **Verification:** `python3 -m unittest scripts.tests.test_gen_views.WorkspaceTests` (7 tests) passes.
- **Committed in:** `cc44760`.

---

**Total deviations:** 2 auto-fixed (both Rule 3; one execution-mechanics, one template ordering).
**Impact on plan:** No shipped contract changed; the ordering keeps the existing generator suite meaningful.

## Issues Encountered

- `grep -c workspaceFolder` exits 1 on a zero count; the plan's `bash -c '[ "$(grep -c …)" = "0" ]'` wrapper accounts for that, and the direct count printed `0`.
- The full stdlib suite (`307 tests`) and the plan's four gates all exit 0 on the committed tree.

## User Setup Required

None - the onboarding symlink step (`mkdir -p "$HOME/.local/bin" && ln -sf …`) is documented for plan 06-05's guide and is not a repository change.

## Next Phase Readiness

- TOOL-02 is complete at the configuration level: per-project `.clangd`, absolute `--query-driver` globs, and cpptools IntelliSense disabled.
- The live-IDE check remains the manual `06-VALIDATION.md` entry; the automated suite proves configuration identity and wrapper behaviour only.
- No blockers; no committed file names a machine-specific esp-clangd or toolchain build path.

---
*Phase: 06-developer-experience-and-quality-layering*
*Completed: 2026-10-26*

## Self-Check: PASSED

- All five `.clangd` paths, `scripts/clangd-wrapper.sh`, `.vscode/settings.json`, and this SUMMARY exist on disk.
- `d314e7b`, `1756a26`, and `cc44760` are ancestors of `HEAD`.
- `python3 -m unittest discover -s scripts/tests` (307 tests), `uv run scripts/gen_views.py --all --check`, `bash -n`, and `test -x` all exited 0.

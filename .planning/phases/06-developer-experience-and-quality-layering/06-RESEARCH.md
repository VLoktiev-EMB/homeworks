# Phase 6: Developer Experience and Quality Layering - Research

**Researched:** 2026-10-26
**Domain:** Local developer tooling — clang-format / clang-tidy / clangd / pre-commit layers / VS Code multi-root
**Confidence:** HIGH on tool behaviour and pins (all probed on this machine); MEDIUM on the VS Code
multi-root resolution (needs one user decision); HIGH on the measured lint/format backlog.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

#### Formatting contract

- **D-01:** The whole tracked C/C++ tree is reformatted in one mechanical pass: `lib/`,
  `homeworks/`, `tests/`, plus the four `templates/homework-*/` sources and their four
  golden fixtures. The template files contain no `{{...}}` placeholders in C/C++ (only
  YAML and README do), so parsing them is safe, and the existing golden-tree test keeps
  the template and the fixture identical.
- **D-02:** `.clang-format` is based on LLVM with `IndentWidth: 4`, `TabWidth: 4`,
  `UseTab: Never`, `ColumnLimit: 120`, `BreakBeforeBraces: Custom` with
  `AfterFunction: true` and `AfterControlStatement: Never`, `PointerAlignment: Right`,
  `DerivePointerAlignment: false`, `AccessModifierOffset: -4`,
  `AllowShortFunctionsOnASingleLine: Empty`, `AllowShortIfStatementsOnASingleLine: Never`,
  `AllowShortLoopsOnASingleLine: false`, `IndentCaseLabels: false`,
  `SpaceBeforeParens: ControlStatements`, `AlignConsecutiveAssignments: false`,
  `AlignConsecutiveDeclarations: false`, `SortIncludes: true`, `ReflowComments: false`.
  It is documented as an approximation of ESP-IDF style, never as equivalence.
- **D-03:** No `.editorconfig`. Tool-specific configuration is the only style source:
  `.clang-format` for C/C++, markdownlint for Markdown, yamllint for YAML, ruff for Python.
- **D-04:** The pre-commit hook runs `clang-format --dry-run --Werror` on staged C/C++
  files only, and is check-only: it never rewrites or stages. The phase gate (and later CI)
  runs the same check with `--all-files`.
- **D-05:** One stdlib test under `scripts/tests/` asserts the agreed config invariants —
  `IndentWidth: 4`, `ColumnLimit: 120`, `UseTab: Never`, `AfterFunction: true`, and
  `ReflowComments: false` — so success criterion 1 is machine-checked rather than declared.

#### Tool delivery and pinning

- **D-06:** Every linter is pre-commit-managed with an exact `rev`: `mirrors-clang-format`
  v23.1.3, `ruff-pre-commit` v0.17.2, `markdownlint-cli2` v0.24.0, `yamllint` v1.38.0,
  and the existing gitleaks v8.30.1. Nothing is installed through Homebrew or another
  system package manager.
- **D-07:** clang-tidy is delivered by `cpp-linter/cpp-linter-hooks`, pinned, at clang-tidy
  23.1.3 so it matches clang-format. The platform's bundled `tool-clangtidy` 19.1.0 is not
  used. If the hook cannot pin 23.1.3, the planner must surface the mismatch rather than
  silently fall back.
- **D-08:** pre-push runs only clang-tidy, over host-compiled code: `lib/common`,
  `lib/port`, `lib/host`, and native test sources. Tests and builds stay in the phase gate
  and Phase 8 CI; pre-push must not become a second build system.
- **D-09:** When `compile_commands.json` is missing or stale, the clang-tidy hook exits
  non-zero and prints the exact regeneration command for the owning project. It never
  generates the database, writes `.pio/`, or skips silently.
- **D-10:** `default_install_hook_types` becomes `[pre-commit, pre-push]`, so one
  `pre-commit install` wires both stages and a novice cannot forget the pre-push half.

#### Lint surface

- **D-11:** markdownlint covers authored Markdown: root `README.md`, `AGENTS.md`, authored
  `docs/**/*.md` (generated pages excluded), `homeworks/**/*.md`, `templates/*.md`, and
  `.github/pull_request_template.md`. `.planning/` (211 files), `.claude/` (the generated
  adapter), generated pages, and vendored assets are excluded.
- **D-12:** Generated pages carrying the `GENERATED — do not edit` header are excluded from
  markdownlint. `gen_views.py --check` is the sole owner of their shape.
- **D-13:** ruff is configured once in a root `pyproject.toml`: `target-version = "py313"`,
  `line-length = 100`, `select = ["E", "F", "I", "UP", "B"]`.
- **D-14:** yamllint covers authored YAML: `.github/workflows/`, `homeworks/**/homework.yaml`,
  `boards/*.yaml`, `templates/**/*.yaml`, and `.pre-commit-config.yaml`. The generated
  `mkdocs.yml` is excluded for the same reason as generated Markdown.
- **D-15:** All three hooks are check-only, following Phase 5's D-21. The one-time cleanup
  is a separate change: `ruff --fix`, `markdownlint-cli2 --fix`, and manual yamllint edits.

#### clangd and VS Code

- **D-16:** `.clangd` is part of both homework templates and is produced by
  `scripts/new_homework`; the scaffold remains the only creation path. Content is
  `CompilationDatabase: .` plus the minimal flag set; the file is committed, the database
  is not. The existing `1_3-police-flasher` receives the same file once by hand, and the
  golden-tree equality test keeps the template, the fixture, and the real tree aligned.
- **D-17:** `scripts/clangd-wrapper.sh` resolves esp-clangd in this order: `$ESP_CLANGD`,
  `esp-clangd` on `PATH`, then the newest
  `~/.espressif/tools/esp-clangd/esp-*/esp-clangd/bin/clangd`. If none is found it fails
  with a message that names the installation source and points at the onboarding guide.
  It passes explicit absolute `--query-driver` globs for
  `~/.platformio/packages/toolchain-*/bin/*` and `tool-*/bin/*`, never `**`.
- **D-18:** One clangd server serves the whole multi-root workspace. Each project's
  database is found by nearest-ancestor discovery through its own `.clangd`; no global
  `--compile-commands-dir` is ever set.
- **D-19:** A committed root `.vscode/settings.json` carries the full contract:
  `clangd.path` points at the wrapper; cpptools IntelliSense, autocomplete, and error
  squiggles are disabled; format-on-save is enabled for C/C++ through clangd; and
  `--background-index` is passed. The workspace `unwantedRecommendations` block stays.
- **D-20:** `docs/standards/vscode.md` covers macOS and Linux; Windows appears only as a
  WSL note. It takes a beginner from installation to format-on-save, the Problems panel,
  clangd, and a no-hardware check.
- **D-21:** Two ADR files are created — one for the formatting approximation, one for the
  esp-clangd and multi-root contract — and each is linked from a row in
  `docs/decisions/README.md`.

#### Site and rulebook integration

- **D-22:** `templates/views/mkdocs.yml.tmpl` gains a `Standards` navigation section with
  the `vscode.md` entry. `gen_views.py` stays the single owner of `mkdocs.yml`, and the
  drift gate covers the new entry.
- **D-23:** `AGENTS.md` gains a `Quality tooling` section with rules for format, lint,
  gitleaks, and clang-tidy, and the enforcement vocabulary expands to four points:
  `[ENFORCED: pre-commit]`, `[ENFORCED: pre-push]`, `[ENFORCED: CI]`, and
  `[ENFORCED: review]`. The Routing table gains a row pointing at the onboarding guide.
- **D-24:** Phase 6 does not edit CI workflows. The quality layers are local only; CI
  wiring, the matrix, and PR-time checks remain Phase 8.

### Claude's Discretion

- The exact `.clang-tidy` check set and options, provided it covers bugprone, cert,
  performance, and portability, and stays warnings-first rather than error-first.
- The exact `.clangd` flag set beyond `CompilationDatabase: .`.
- The internal structure of `scripts/clangd-wrapper.sh`, including any caching of the
  resolved binary path.
- The exact markdownlint and yamllint rule configuration, provided the paths in D-11 and
  D-14 are covered.
- The shape of the onboarding guide (linear walkthrough versus task-based recipes) and the
  wording of both ADRs.
- The commit split between the mechanical reformat and the hook wiring.

### Deferred Ideas (OUT OF SCOPE)

- **CI wiring of the quality layers** — Phase 8 (TOOL-05, TOOL-06, F-16, WR-13). This
  phase deliberately keeps CI untouched.
- **ESP-IDF `compiledb` completeness fallback** — if PlatformIO's database proves
  incomplete for ESP-IDF, the CMake `-DCMAKE_EXPORT_COMPILE_COMMANDS=ON` fallback is a
  spike item for Phase 7 / the first ESP-IDF homework.
- **An AStyle check** — not built; clang-format remains the single standard, and the
  approximation is documented rather than duplicated.
- **Native Windows onboarding** — deferred; the guide covers macOS and Linux, with WSL as
  a note.
- **`.editorconfig`** — considered and declined in D-03.
- **Automatic detection of authored `docs/standards/` pages in navigation** — declined in
  favour of an explicit template entry (D-22).

### Reviewed Todos (not folded)

- *Promote merge_firmware.py into a shared tool* — Phase 7/8; it is simulation and
  platform-tooling work, not developer-environment configuration.
- *Trim governance ceremony (Phase 4.1)* — already completed; no remaining action.
- *Expand homework README and add a proper SVG schematic* — homework content, Phase 7 /
  Phase 11.
- *Standardize pull request titles across homeworks* — CI and process concern, Phase 8/9.
</user_constraints>

## Summary

Three things separate a plan that works from one that is written from documentation alone:

1. **Every pin in D-06/D-07 exists, and the mechanism each pin assumes was probed here.**
   `mirrors-clang-format` v23.1.3, `ruff-pre-commit` v0.17.2, `markdownlint-cli2` v0.24.0,
   `yamllint` v1.38.0 and `cpp-linter-hooks` v1.8.1 all resolve from `git ls-remote`; the
   `clang-format==23.1.3` and `clang-tidy==23.1.3` wheels exist on PyPI, so D-07's exact
   clang-tidy pin is feasible.

2. **Four configuration facts contradict what the obvious `.pre-commit-config.yaml` would
   say, and each was reproduced on this machine.** The mirror's default `entry` is
   `clang-format -i`, so check-only requires overriding `entry`. `default_stages` defaults
   to *all* stages, so without `default_stages: [pre-commit]` every linter also runs at
   pre-push — violating D-08's "pre-push runs only clang-tidy". `cpp-linter-hooks`
   deliberately *skips* clang-tidy locally when no database is found (and fails only when
   `CI` is set), which is the exact inverse of D-09. And esp-clangd 21.1.3 as installed
   ships **no resource headers**, so `<stdbool.h>` does not resolve without a `.clangd`
   option the current STACK sketch does not mention.

3. **The VS Code contract in D-19 does not reach the homework folders when the novice
   opens `homeworks.code-workspace`.** In a multi-root workspace a folder's
   `.vscode/settings.json` applies to that folder only, and vscode-clangd's
   `${workspaceFolder}` resolves to the *active file's directory* because
   `vscode.workspace.rootPath` is undefined. The same settings must therefore also be
   emitted into the generated `.code-workspace`, and `clangd.path` must be expressed
   without `${workspaceFolder}`.

**Primary recommendation:** keep every locked decision, and add four things the context
could not know: (a) `default_stages: [pre-commit]` plus an explicit `entry` override for
clang-format; (b) `CompileFlags.BuiltinHeaders: QueryDriver` in every `.clangd`, verified
to give zero diagnostics on `1_3-police-flasher`; (c) a local pre-push guard hook that owns
D-09's missing/stale-database failure in front of `cpp-linter-hooks`; (d) the settings
contract emitted into `homeworks.code-workspace` as well as `.vscode/settings.json`, with a
stdlib test that keeps the two identical.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Style source of truth | Repository config file (`.clang-format`, `.clang-tidy`, `.markdownlint-cli2.jsonc`, `.yamllint.yaml`, `pyproject.toml`) | — | One committed file per tool; no editor-level or machine-level style (D-03) |
| Fast feedback (format/lint/secrets) | Git pre-commit hook (pre-commit-managed environments) | Editor format-on-save | The hook is the gate; the editor is the convenience |
| Static analysis | Git pre-push hook (`cpp-linter-hooks`) + local guard hook | — | Needs a compilation database and is too slow for a commit hook |
| Compilation database | PlatformIO `compiledb` target (`scripts/pio/compiledb.py`) | — | Generated per machine, never committed; the hook only validates its presence |
| IntelliSense | clangd extension → `scripts/clangd-wrapper.sh` → esp-clangd | Per-project `.clangd` fragments | The wrapper makes the binary discoverable; fragments make each project's language flags correct |
| Editor contract | `.code-workspace` `settings` (workspace scope) + `.vscode/settings.json` (single-folder scope) | — | Multi-root workspace settings only live in the workspace file |
| Onboarding prose | `docs/standards/vscode.md` → MkDocs nav → generated site | `AGENTS.md` routing row | Authored page; navigation is generator-owned |

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| TOOL-01 | clang-format 23.1.3 configured as a documented ESP-IDF approximation (4 spaces, 120 columns, function brace on new line); clang-tidy runs bugprone, cert, performance, portability on host code | Pin verified (tag + wheel). Every D-02 key parses in clang-format 23.1.3 and resolves to the intended value (§Formatting probe). 60/60 tracked C/C++ files currently violate it, so the mechanical pass is real and complete. clang-tidy on `lib/common` + `lib/host` via `tests/compile_commands.json` exits 0 with 22 warnings (§clang-tidy probe) |
| TOOL-02 | esp-clangd serves the workspace through `scripts/clangd-wrapper.sh`, per-project `.clangd`, `compiledb` databases, absolute `--query-driver` globs; cpptools IntelliSense disabled | `--query-driver` is a comma-separated allowlist of absolute globs (§clangd docs). esp-clangd 21.1.3 resolves the Xtensa driver and system includes but has **no bundled resource headers**; `BuiltinHeaders: QueryDriver` fixes it — verified 0 errors on the real homework. Multi-root settings scope is the blocking design question (§Pitfall 1) |
| TOOL-03 | Layered checks: format, markdownlint, yamllint, ruff, gitleaks in pre-commit; clang-tidy in pre-push | Hook ids, entries and defaults read from the pinned tags. `default_stages` all-stages default reproduced. cpp-linter-hooks skip-vs-CI behaviour read from its README. Measured backlogs: yamllint 35, ruff 14, markdownlint 11 with MD013/MD060 off |
| TOOL-04 | `docs/standards/vscode.md` onboards a VS Code beginner: extensions, tasks, format-on-save, Problems panel, clangd, no-hardware simulation | `mkdocs build --strict` plus `validation.nav.omitted_files: warn` means an authored page absent from the template nav fails the docs workflow — D-22's entry is mandatory, not cosmetic. `docs/standards/` does not exist yet |
</phase_requirements>

## Standard Stack

### Core

| Library / tool | Version | Purpose | Why standard |
|----------------|---------|---------|--------------|
| pre-commit | 4.7.0 (installed) | Hook runner, stage installation | Already the repo's gate; `minimum_pre_commit_version: '4.7.0'` is already the floor — [VERIFIED: .pre-commit-config.yaml:1] `minimum_pre_commit_version: '4.7.0'` |
| mirrors-clang-format | v23.1.3 | clang-format 23.1.3 in an isolated Python env | Tag confirmed by `git ls-remote`; wheel `clang-format==23.1.3` on PyPI |
| cpp-linter-hooks | v1.8.1 | clang-tidy 23.1.3, version-pinned by `--version` | Tag confirmed; hook ids `clang-tidy` and `clang-format` read from the pinned `.pre-commit-hooks.yaml` |
| ruff-pre-commit | v0.17.2 | Python lint (check-only) | Tag confirmed; hook id is `ruff-check` (`ruff` is a legacy alias) |
| markdownlint-cli2 | v0.24.0 | Markdown lint | Tag confirmed; multi-file invocation verified to lint every file passed |
| yamllint | v1.38.0 | YAML lint | Tag confirmed; hook `entry: yamllint`, `types: [file, yaml]` |
| gitleaks | v8.30.1 | Secret scan | Already configured — [VERIFIED: .pre-commit-config.yaml:5-8] `repo: https://github.com/gitleaks/gitleaks` / `rev: v8.30.1` / `- id: gitleaks` |
| esp-clangd | 21.1.3 (`esp-21.1.3_20260408`) | ESP32-S3 language server | Installed at `~/.espressif/tools/esp-clangd/esp-21.1.3_20260408/esp-clangd/bin/clangd`; reports `Espressif clangd version 21.1.3` |

### Supporting

| Library / tool | Version | Purpose | When to use |
|----------------|---------|---------|-------------|
| clang-format wheel | 23.1.3 | Phase-gate `--all-files` run, local probes | Only via the pre-commit env; never installed globally (D-06) |
| clang-tidy wheel | 23.1.3 | Installed by cpp-linter-hooks on first run | Only via the hook env |
| PyYAML | 6.0.3 | Already pinned for hooks and PEP 723 headers | Unchanged; a new hook that needs YAML should reuse this pin |
| Node.js | 26.7.0 (installed) | markdownlint-cli2 hook runtime (`language: node`) | pre-commit provisions its own node env; the local node is only a fallback |

### Alternatives Considered

| Instead of | Could use | Tradeoff |
|------------|-----------|----------|
| `mirrors-clang-format` | `cpp-linter-hooks`' own `clang-format` hook | One repo for both tools, and `--version` pins exactly; but D-06 already fixes the mirror, and the mirror's `rev` *is* the clang-format version, which makes the pin self-documenting. Keep the mirror. |
| cpp-linter-hooks | a local `language: system` clang-tidy script | Would remove the one-command install and reintroduce a system dependency; D-07 rejects it, and the platform's `tool-clangtidy` is 19.1.0. |
| `BuiltinHeaders: QueryDriver` | `--resource-dir=<host clang resource dir>` in the wrapper | Both give 0 errors (verified); the config option is committed, portable, and needs no host clang. `--resource-dir` stays as a documented fallback only. |
| a committed `.clangd` with an absolute `-isystem` to the GCC builtin include | `BuiltinHeaders: QueryDriver` | The absolute path contains the toolchain package version (`…toolchain-xtensa-esp-elf@14.2.0+20260121…`) and breaks on every PlatformIO upgrade. |

**Installation:** none. Every linter is delivered through pre-commit; no `brew`, no
`pip install --user`, no global npm (D-06). The only machine-level step this research
recommends is the wrapper symlink described in Pitfall 1, which is a filesystem link, not a
package install.

**Version verification performed:**

```bash
git ls-remote --tags https://github.com/pre-commit/mirrors-clang-format 'refs/tags/v23.1.3*'
git ls-remote --tags https://github.com/astral-sh/ruff-pre-commit 'refs/tags/v0.17.*'
git ls-remote --tags https://github.com/DavidAnson/markdownlint-cli2 'refs/tags/v0.24.0*'
git ls-remote --tags https://github.com/adrienverge/yamllint 'refs/tags/v1.38.0*'
git ls-remote --tags https://github.com/cpp-linter/cpp-linter-hooks     # latest v1.8.1
python3 -c 'import urllib.request,json; ...'                            # PyPI releases
```

## Package Legitimacy Audit

No package is installed into the project's own environment; every tool is a pre-commit hook
whose environment pre-commit builds from the pinned repository. The audit therefore covers
the hook repositories and the two PyPI wheels the hooks pull in.

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| pre-commit (already in use) | PyPI | mature | very high | github.com/pre-commit/pre-commit | OK | Approved |
| mirrors-clang-format v23.1.3 | GitHub (pre-commit org) | mirror of LLVM releases | — | github.com/pre-commit/mirrors-clang-format | OK | Approved |
| clang-format 23.1.3 | PyPI | LLVM release wheel | high | llvm/llvm-project | OK | Approved |
| clang-tidy 23.1.3 | PyPI | LLVM release wheel (only 23.x on PyPI) | high | llvm/llvm-project | OK | Approved |
| cpp-linter-hooks v1.8.1 | GitHub / PyPI | active, MIT, used by several orgs | moderate | github.com/cpp-linter/cpp-linter-hooks | OK | Approved |
| ruff-pre-commit v0.17.2 | GitHub (astral-sh) | active | very high | github.com/astral-sh/ruff-pre-commit | OK | Approved |
| markdownlint-cli2 v0.24.0 | GitHub / npm | active | very high | github.com/DavidAnson/markdownlint-cli2 | OK | Approved |
| yamllint v1.38.0 | GitHub / PyPI | mature | high | github.com/adrienverge/yamllint | OK | Approved |

**Packages removed due to SLOP verdict:** none.
**Packages flagged suspicious [SUS]:** none.

*Two residual supply-chain notes for the plan, both already bounded by D-06/D-07:*
`markdownlint-cli2` runs as `language: node`, so the hook pulls npm dependencies into a
pre-commit-managed node env; `cpp-linter-hooks` downloads a wheel on first use per version.
Neither is avoidable without abandoning the pinned-rev model.

## Architecture Patterns

### System Architecture Diagram

```
author edits a file
        |
        +--- editor (VS Code, multi-root workspace)
        |        |
        |        +-- .code-workspace settings ---> cpptools IntelliSense DISABLED
        |        |                                  format-on-save -> clangd
        |        +-- clangd extension --> scripts/clangd-wrapper.sh
        |                                   |  resolve esp-clangd (ESP_CLANGD | PATH | newest esp-*)
        |                                   |  pass --query-driver=<abs toolchain globs>
        |                                   v
        |                              esp-clangd 21.1.3  (one server, whole window)
        |                                   |  nearest-ancestor .clangd per project
        |                                   |    CompilationDatabase: .
        |                                   |    BuiltinHeaders: QueryDriver   <-- required
        |                                   v
        |                              <project>/compile_commands.json  (generated, untracked)
        |
        +--- git commit
        |        |
        |        +-- pre-commit stage (all hooks except clang-tidy)
        |        |     gitleaks | hygiene | no-generated-files | check-architecture
        |        |     check-metadata | gen-views-check
        |        |     clang-format --dry-run --Werror | markdownlint-cli2 | yamllint | ruff-check
        |        |     (check-only: report, never rewrite or stage)
        |        v
        +--- git push
                 |
                 +-- pre-push stage
                       clang-tidy-db guard  --(absent/stale)--> exit 1 + exact regeneration command
                                              |
                                              v present
                       cpp-linter-hooks clang-tidy (--version=23.1.3, --compile-commands=tests)
                                              |
                                              v
                                     diagnostics on changed lines only
```

### Recommended Project Structure (new and changed paths)

```
.clang-format                     # D-02, approximates ESP-IDF/AStyle
.clang-tidy                       # host-only check set, warnings-first
.markdownlint-cli2.jsonc          # MD013/MD060 policy + globs
.yamllint.yaml                    # line-length 120, no document-start requirement
pyproject.toml                    # [tool.ruff] only — no [project] table
.pre-commit-config.yaml           # + default_stages, 5 new hooks, 2 pre-push hooks
.vscode/settings.json             # single-folder-open contract (committed)
scripts/
└── clangd-wrapper.sh             # 100755, resolves esp-clangd, passes --query-driver
scripts/clang-tidy-db             # pre-push guard (D-09)
scripts/tests/
├── test_tooling_config.py        # .clang-format invariants (D-05) + settings drift
templates/
├── homework-arduino/.clangd
├── homework-espidf/.clangd
├── views/mkdocs.yml.tmpl         # + Standards section
└── views/workspace.json.tmpl     # + settings block (see Pitfall 1)
scripts/tests/fixtures/golden/homework-{arduino,espidf}/.clangd
docs/standards/vscode.md          # new authored page
docs/decisions/0012-*.md, 0013-*.md
```

### Pattern 1: Check-only hooks (inherited from 05/D-21)

**What:** a hook reports a violation and exits non-zero; it never edits, formats, or stages.
**When to use:** every hook this phase adds.
**Example (verified shape):**

```yaml
- repo: https://github.com/pre-commit/mirrors-clang-format
  rev: v23.1.3
  hooks:
    - id: clang-format
      # The mirror's default entry is `clang-format -i`; overriding it is what
      # makes the hook check-only (D-04). Verified: a failing run left the tree clean.
      entry: clang-format --dry-run --Werror
      args: [-style=file]
      types_or: [c, c++]
```

### Pattern 2: Layered stage assignment

**What:** the stage a hook runs in is declared twice — in `default_stages` and per hook.
**When to use:** as soon as `default_install_hook_types` has more than one entry.

```yaml
minimum_pre_commit_version: '4.7.0'
default_install_hook_types: [pre-commit, pre-push]
default_stages: [pre-commit]          # REQUIRED: the default is ALL stages
```

### Pattern 3: Discover, never hardcode (wrapper)

**What:** the wrapper resolves the server binary and the toolchain globs at run time.
**Why:** esp-clangd's directory embeds its build date (`esp-21.1.3_20260408`) and the
toolchain directory embeds its package version (`toolchain-xtensa-esp-elf@14.2.0+20260121`).

```bash
# shape only — the planner owns the final text
CLANGD="${ESP_CLANGD:-$(command -v esp-clangd)}"
[ -n "$CLANGD" ] || CLANGD=$(ls -d "$HOME"/.espressif/tools/esp-clangd/esp-*/esp-clangd/bin/clangd 2>/dev/null | sort -V | tail -1)
PIO_PACKAGES="${PLATFORMIO_CORE_DIR:-$HOME/.platformio}/packages"
exec "$CLANGD" \
  --query-driver="$PIO_PACKAGES/toolchain-*/bin/*,$PIO_PACKAGES/tool-*/bin/*" \
  "$@"
```

### Pattern 4: Generator-owned editor contract

**What:** the workspace file is generated (`owner: "workspace"`, `mode: "whole"` in
`generated.manifest`), so the `settings` block belongs in
`templates/views/workspace.json.tmpl` and never in the emitted file.

### Anti-Patterns to Avoid

- **Adding a hook without `stages` and assuming pre-commit-only.** `default_stages` defaults
  to *all* stages ([CITED: pre-commit.com — "default_stages (optional: default (all
  stages))"]); reproduced: `clang-format` ran under `--hook-stage pre-push`.
- **`types_or` left at the mirror's default.** It includes `json`, `proto`, `java`,
  `javascript`, `c#`, `cuda`, `objective-c`, `metal` — a `.json` edit would be reformatted
  by clang-format.
- **A global `--compile-commands-dir` in `clangd.arguments`.** It disables per-project
  `.clangd` `CompilationDatabase` in a multi-root window (STACK §2.3, D-18).
- **`--query-driver='**'`.** It authorises execution of any binary a compile command names.
- **Committing `compile_commands.json`.** Already ignored; the generated-file hook would
  fail on it.
- **Editing `mkdocs.yml` or `homeworks.code-workspace` by hand.** Both are manifest-owned and
  the drift hook fails on the next commit.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Formatting check | a diff-based shell script or a Python formatter | `clang-format --dry-run --Werror` | It already prints `file:line:col: error: code should be clang-formatted [-Wclang-format-violations]` and exits 1 (verified) |
| clang-format install | a Homebrew/apt step in the guide | `mirrors-clang-format` hook | D-06; the hook env is hermetic and version-identical to the pin |
| clang-tidy install + version pin | a system install plus a hand-rolled wrapper | `cpp-linter-hooks` with `--version=23.1.3` | The wheel is installed per version into the hook env; the hook also implements changed-lines filtering |
| clangd binary discovery | a hardcoded absolute path in settings | `scripts/clangd-wrapper.sh` | D-17; paths embed build dates and package versions |
| Markdown rule set | a bespoke link/line checker | `markdownlint-cli2` | 1 038 default findings are already computed by it |
| YAML rule set | a YAML subset checker | `yamllint` | It resolves the repo config from the CWD ancestors (`.yamllint.yaml`) |
| Compilation database | a CMake or hand-written generator | `pio run -t compiledb` via `scripts/pio/compiledb.py` | Already pins `COMPILATIONDB_PATH` to the project root — [VERIFIED: scripts/pio/compiledb.py:21-23] `env.Replace(` / `    COMPILATIONDB_PATH=os.path.join(env.subst("$PROJECT_DIR"), "compile_commands.json")` / `)` |
| Settings drift between the two editor files | manual discipline | one stdlib test comparing the JSON values | Same pattern as the golden-tree test |

**Key insight:** every tool in this phase has a machine-readable failure mode that the
repo's existing gate style already handles (`PATH: STATUS — reason`, exit 0/1/2). Nothing
here needs a new abstraction; the work is configuration and one thin wrapper.

## Common Pitfalls

### Pitfall 1: A root `.vscode/settings.json` does not configure a multi-root workspace

**What goes wrong:** the novice opens `homeworks.code-workspace` (5 roots: `repo`, `docs`,
`lib`, `scripts`, `1.3 Police Flasher`). `.vscode/settings.json` is loaded only as *folder*
settings for the `repo` root, so `C_Cpp.intelliSenseEngine: "disabled"` and
`editor.formatOnSave` never reach homework files, and cpptools stays live alongside clangd.

**Why it happens:** workspace-scope settings for a multi-root workspace live in the
`.code-workspace` `settings` object; folder settings apply to that folder's resources only
([CITED: code.visualstudio.com/docs/configure/settings], [CITED: microsoft/vscode#94424]).

**Second half of the same trap:** `clangd.path` cannot use `${workspaceFolder}` there.
vscode-clangd substitutes `${workspaceFolder}` itself from `vscode.workspace.rootPath`,
which is undefined in a multi-root workspace, so it falls back to the *active editor's
directory* ([VERIFIED: clangd/vscode-clangd `src/config.ts` — `replacement()` returns
`vscode.workspace.rootPath`, else `path.dirname(activeTextEditor.document.uri.fsPath)`,
else `process.cwd()`]). The scoped form `${workspaceFolder:repo}` is unsupported
([CITED: clangd/vscode-clangd#696]). `${env:HOME}` **is** supported by the same function.

**How to avoid:** three coordinated moves, all inside D-19's spirit:
1. `templates/views/workspace.json.tmpl` gains a `settings` object with the full contract
   (this is the only scope that reaches all five roots); regenerate with
   `uv run scripts/gen_views.py --all`.
2. `.vscode/settings.json` carries the *same object* for single-folder opens.
3. Express `clangd.path` without `${workspaceFolder}`: `${env:HOME}/.local/bin/clangd-wrapper`,
   with one documented guide step, `ln -sf "$PWD/scripts/clangd-wrapper.sh" "$HOME/.local/bin/clangd-wrapper"`.
   A PATH-resolvable bare command name (`"clangd-wrapper"`) works too but depends on
   `~/.local/bin` being on `PATH`, which is not true on a default macOS install.

**Warning signs:** Problems panel shows both clangd and cpptools squiggles; format-on-save
does nothing inside `homeworks/…` but works inside `repo/…`; clangd logs
`clangd executable not found` after any file is opened.

**Decision needed:** this is the one place where research deviates from D-19. The planner
must either add the workspace `settings` block *and* the symlink step, or accept that the
canonical entry point is "open the repository folder, not the workspace file" and record
that in the guide (which weakens the phase goal). Recommendation: do both, and let the
guide name the workspace file as the entry point.

### Pitfall 2: pre-commit runs every hook in every installed stage by default

**What goes wrong:** `default_install_hook_types: [pre-commit, pre-push]` installs both git
hooks; a hook with no `stages` then runs in both. gitleaks, ruff, markdownlint, yamllint and
clang-format all re-run on every push, violating D-08's "pre-push runs only clang-tidy".

**Why it happens:** `default_stages` is "optional: default (all stages)"
([CITED: pre-commit.com configuration reference]); reproduced on this machine.

**How to avoid:** `default_stages: [pre-commit]` at the top level, and explicit
`stages: [pre-push]` on the clang-tidy hook and the database guard.

**Warning signs:** `pre-commit run --hook-stage pre-push --files <a .c file>` output names
more than the two push hooks.

### Pitfall 3: cpp-linter-hooks skips locally exactly when D-09 needs it to fail

**What goes wrong:** with no `compile_commands.json`, the hook "skips clang-tidy on your
machine and passes", and only fails when `CI` is set ([CITED: cpp-linter-hooks README,
"Compilation database"]). D-09 requires a non-zero exit with the regeneration command,
locally. Worse: passing `--compile-commands=<dir>` makes the hook run anyway ("The hook runs
clang-tidy anyway when `args` tell it how to compile: `-p`, `--extra-arg` or
`--extra-arg-before`"), so the database presence check disappears entirely.

**How to avoid:** two hooks, in this order in the file:
1. a `local` `language: system` guard (`stages: [pre-push]`, `files:` = the host C/C++
   pattern) that exits non-zero and prints
   `pio run -d tests -e native -t compiledb` when `tests/compile_commands.json` is absent or
   older than `tests/platformio.ini`, `platformio.shared.ini`, or the sources it describes;
2. the pinned `cpp-linter-hooks` clang-tidy hook with `--version=23.1.3`
   `--compile-commands=tests`.

Ordering note: pre-commit runs repositories in file order, so a guard placed inside the
existing bottom `local:` block would run *after* clang-tidy. Either add the guard in its own
`local:` repo above `cpp-linter-hooks`, or move `cpp-linter-hooks` to the end of the file.

**Warning signs:** a push with no database succeeds silently; `pre-commit run -v` shows a
"skipping" message instead of the regeneration command.

### Pitfall 4: esp-clangd ships no resource headers, so `<stdbool.h>` fails

**What goes wrong:** with the project database present and `--query-driver` matching, a
`clangd --check` on `homeworks/1_3-police-flasher/src/main.cpp` reports:

```
E[…] [drv_unknown_argument] Line 1: unknown argument: '-mdisable-hardware-atomics'
E[…] [drv_unknown_argument] Line 1: unknown argument: '-fstrict-volatile-bitfields'
E[…] [drv_unknown_argument] Line 1: unknown argument: '-fno-tree-switch-conversion'
E[…] [pp_file_not_found] Line 8: in included file: 'stdbool.h' file not found
```

**Why it happens:** two independent causes, both verified:
- GCC-only Xtensa flags reach clangd unchanged (fixed by `CompileFlags.Remove`).
- The installed esp-clangd package contains *only* `esp-clangd/bin/clangd` — no
  `lib/clang/<ver>/include` — and clangd's system-include extractor deliberately excludes
  the queried driver's builtin headers, keeping "clangd's versions" instead
  ([VERIFIED: clang-tools-extra/clangd/SystemIncludeExtractor.cpp — `case
  Config::BuiltinHeaderPolicy::Clangd:` … "exclude the queried builtins"]). With no clangd
  builtins, nothing supplies `stdbool.h`.

**How to avoid:** set `CompileFlags.BuiltinHeaders: QueryDriver` in every committed
`.clangd` ([CITED: clangd.llvm.org/config — "QueryDriver: Use the headers extracted from
the compiler via the --query-driver"]). Verified end-to-end: the same `--check` reports
`All checks completed, 0 errors` with this one line added. The docs' caveat — "if the
driver is not clang, … could lead to unexpected results such as false positive
diagnostics" — belongs in ADR 0013.

**Warning signs:** `stdbool.h`/`stdint.h`/`stddef.h` are unresolved while project headers
resolve; `--check` exits 3.

### Pitfall 5: Native test translation units are not in any compilation database

**What goes wrong:** D-08 names "native test sources" as part of the clang-tidy scope. They
cannot be analysed:
- `tests/compile_commands.json` (11 entries) contains `lib/common/src/*.c`,
  `lib/host/src/*.c`, Unity's `unity.c` and `tests/src/main.c` — **no** `tests/test/**`.
- `pio test` has no `-t/--target` option, so there is no compiledb target for a test build
  (`pio test --help` lists only build/upload/test filters).
- Running clang-tidy on `tests/test/test_common_crc/test_crc.c -p tests` exits 1 with
  `unity_config.h file not found` and `Found compiler error(s)` — it borrows the
  `tests/src/main.c` command, whose include paths do not describe a test build.

**How to avoid:** scope the clang-tidy hook to the host library sources that the database
does describe (`lib/common/src/*.c`, `lib/host/src/*.c`, plus the headers they include) and
state the test-TU gap explicitly in the ADR/guide. Do **not** hand-maintain `-I` flags for
test TUs: that is the "second build system" D-08 forbids.

**Warning signs:** clang-tidy output contains `unity_config.h` or diagnostics located in
`.pio/libdeps/native/Unity/**`; the hook passes but checks nothing.

### Pitfall 6: The measured lint backlogs will fail a naive first run

**What goes wrong:** adding the hooks without policy files fails immediately.
Measured on this tree with the D-13/§Discretion settings:

| Tool | Default policy | Findings |
|------|----------------|----------|
| clang-format | D-02 config | **60 of 60** tracked C/C++ files violate |
| clang-tidy (host libs, `-p tests`) | bugprone/cert/performance/portability | 22 warnings: 15 `portability-avoid-pragma-once`, 7 `bugprone-signed-bitwise` |
| yamllint | defaults | 35 (19 `line-length` >80, 12 `document-start`, 4 `truthy`) in 12 files |
| ruff (`E,F,I,UP,B`, line-length 100) | D-13 | 14 (5 `F821`, 4 `F401`, 3 `E501`, 1 `B905`, 1 `UP031`) in 6 files |
| markdownlint-cli2 | defaults | 1 038 (923 `MD013`, 104 `MD060`, 6 `MD034`, 2 `MD024`, 1 each `MD041`/`MD040`/`MD032`) |
| markdownlint-cli2 | `MD013: false`, `MD060: false` | 11 in 5 files |

**How to avoid:**
- `MD013` (80-column prose) is incompatible with this repo's ~100-column tables and prose:
  disable it, or set `line_length` to 120. `MD060` is a new table-style rule in markdownlint
  0.42 that would restyle every table in the repo: disable it.
- ruff's `F821` hits are **false positives**: `Import` and `env` are injected globals in
  SCons extra scripts (`scripts/pio/compiledb.py:19,21,22`;
  `homeworks/1_3-police-flasher/merge_firmware.py:13,54`). Add per-file ignores rather than
  "fixing" them — an import would break the build.
- yamllint's `line-length` at 80 must be raised (120 matches the C policy) and
  `document-start` relaxed, or 16 findings are pure noise.
- clang-tidy's `portability-avoid-pragma-once` is a style preference the repo does not
  follow (11 headers use `#pragma once`); disable it or convert headers in a separate
  change. `bugprone-signed-bitwise` in `hex.c` is a genuine minor issue.
- cpp-linter-hooks reports **only problems on changed lines by default** (via
  `--line-filter`), so the pre-existing clang-tidy backlog does not block a push. Do not add
  `--all-lines`; if it is ever added, the backlog must be cleared first.

**Warning signs:** a first `pre-commit run --all-files` returns hundreds of findings and the
temptation is to widen exclusions instead of setting the rules.

### Pitfall 7: `mkdocs build --strict` fails on an authored page without a nav entry

**What goes wrong:** `docs/standards/vscode.md` is created, the site builds locally with
warnings, and the `docs` workflow fails at `mkdocs build --strict`.

**Why it happens:** `mkdocs.yml` is generated from `templates/views/mkdocs.yml.tmpl`, whose
`validation.nav.omitted_files` is `warn`; `--strict` promotes every warning to an error —
[VERIFIED: .github/workflows/docs.yml:58-59] `- name: Build the site with warnings as errors`
/ `run: mkdocs build --strict`.

**How to avoid:** D-22's `Standards` section must land in the template in the same change as
the page, then `uv run scripts/gen_views.py --all` (never a hand edit), and the
`generated.manifest` entry for `mkdocs.yml` changes sha/bytes in that same regeneration.

### Pitfall 8: Adding `.clangd` to a template without updating its golden fixture fails CI

**What goes wrong:** `scripts/new_homework` renders every file under the template directory,
and `GoldenTreeTests` compares the scaffolded tree with
`scripts/tests/fixtures/golden/homework-<template>/` as a set *and* byte-for-byte.
`snapshot()` uses `rglob("*")` + `is_file()`, so dotfiles are included.

**How to avoid:** add `.clangd` to both templates, both golden trees, and the real
`homeworks/1_3-police-flasher/` in one coherent change; use
`scripts/tests/temp_root.py:render_tree` to regenerate the fixtures rather than copying by
hand. `template.yaml` (the manifest) is skipped by the scaffold and must not be added to the
goldens.

### Pitfall 9: A root `pyproject.toml` can look like a broken uv project

**What goes wrong:** suspicion that `uv run scripts/check_metadata.py` starts treating the
repo as a project.
**Verified:** not a problem. A `pyproject.toml` containing only `[tool.ruff]` and
`[tool.ruff.lint]` does not create a project; `uv run script.py` still reads the PEP 723
header and installs its dependencies (exit 0, PyYAML 6.0.3 resolved).

### Pitfall 10: `pre-commit run --all-files` must keep working

**What goes wrong:** the check hooks use `types_or: [c, c++]`, which includes the tracked
templates and goldens. That is intended (D-01 reforms them too), but a `files:`/`exclude:`
that drops them would let the template drift from the reformatted tree and the golden test
would catch it later, opaquely.

## Code Examples

### `.clang-format` — every key verified to parse on clang-format 23.1.3

```yaml
# Source: D-02; parsed with `clang-format 23.1.3 --dump-config` (exit 0)
BasedOnStyle: LLVM
IndentWidth: 4
TabWidth: 4
UseTab: Never
ColumnLimit: 120
BreakBeforeBraces: Custom
BraceWrapping:
  AfterFunction: true
  AfterControlStatement: Never
PointerAlignment: Right
DerivePointerAlignment: false
AccessModifierOffset: -4
AllowShortFunctionsOnASingleLine: Empty
AllowShortIfStatementsOnASingleLine: Never
AllowShortLoopsOnASingleLine: false
IndentCaseLabels: false
SpaceBeforeParens: ControlStatements
AlignConsecutiveAssignments: false
AlignConsecutiveDeclarations: false
SortIncludes: true
ReflowComments: false
```

Resolved values from `--dump-config` on this exact file: `IndentWidth: 4`, `ColumnLimit: 120`,
`UseTab: Never`, `SortIncludes: {Enabled: true, IgnoreCase: false}`,
`AllowShortFunctionsOnASingleLine: {Empty: true}`, `AlignConsecutiveAssignments: {Enabled: false}`,
`BreakBeforeBraces: Custom`, `ReflowComments: Never`. Boolean shorthand is accepted; the
D-05 invariant test can read the *source text*, but a stronger test shells out to
`clang-format --dump-config` and asserts the resolved values.

### `.clangd` — verified to produce 0 diagnostics

```yaml
CompileFlags:
  CompilationDatabase: .
  # Required: esp-clangd 21.1.3 ships no resource headers, and clangd excludes the
  # queried driver's builtin headers by default. Verified: 0 errors on
  # homeworks/1_3-police-flasher/src/main.cpp.
  BuiltinHeaders: QueryDriver
  Remove:
    - -mlongcalls
    - -mtext-section-literals
    - -mdisable-hardware-atomics
    - -fno-tree-switch-conversion
    - -fno-shrink-wrap
    - -fstrict-volatile-bitfields
    - -fmacro-prefix-map=*
Diagnostics:
  Suppress:
    - unknown-argument
    - drv_unknown_argument
```

`CompilationDatabase` accepts "A single path to a directory (absolute, or relative to the
fragment)", `Ancestors` (default) or `None` ([CITED: clangd.llvm.org/config]) — `.` is
therefore `<project>/`, which is where `compiledb.py` writes.

### `.clang-tidy` — host-only, warnings-first

```yaml
# Source: .planning/research/STACK.md §6.4, narrowed by the measured backlog
Checks: >
  -*,
  bugprone-*,
  cert-*,
  performance-*,
  portability-*,
  readability-*,
  clang-analyzer-*,
  -bugprone-easily-swappable-parameters,
  -bugprone-narrowing-conversions,
  -cert-err33-c,
  -readability-magic-numbers,
  -readability-identifier-length,
  -readability-function-cognitive-complexity,
  -portability-avoid-pragma-once
WarningsAsErrors: ""
HeaderFilterRegex: "^(lib|homeworks)/.*"
FormatStyle: file
```

clang-tidy 22 and newer enable **no checks** without a `Checks` key
([CITED: cpp-linter-hooks README]), so a `.clang-tidy` file is mandatory, not optional, even
though D-07 only names the hook.

### `.pre-commit-config.yaml` — target shape

```yaml
minimum_pre_commit_version: '4.7.0'
default_install_hook_types: [pre-commit, pre-push]
default_stages: [pre-commit]        # the default is ALL stages — see Pitfall 2

repos:
  # ... existing gitleaks / pre-commit-hooks / local hygiene+architecture+metadata+views ...
  - repo: https://github.com/pre-commit/mirrors-clang-format
    rev: v23.1.3
    hooks:
      - id: clang-format
        entry: clang-format --dry-run --Werror
        args: [-style=file]
        types_or: [c, c++]

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.17.2
    hooks:
      - id: ruff-check            # NOT `ruff`; `ruff-format` is out of scope (D-15)

  - repo: https://github.com/DavidAnson/markdownlint-cli2
    rev: v0.24.0
    hooks:
      - id: markdownlint-cli2
        exclude: ^(\.planning/|\.claude/|docs/index\.md$|docs/homeworks/|docs/boards/|docs/assets/vendor/)

  - repo: https://github.com/adrienverge/yamllint
    rev: v1.38.0
    hooks:
      - id: yamllint
        files: ^(\.github/workflows/|homeworks/[^/]+/homework\.yaml$|boards/[^/]+\.yaml$|templates/.*\.ya?ml$|\.pre-commit-config\.yaml$)

  - repo: local                   # guard must precede the clang-tidy repo
    hooks:
      - id: clang-tidy-db
        name: clang-tidy compilation database present
        language: system
        entry: python3 scripts/clang-tidy-db
        pass_filenames: false
        files: ^(lib/(common|host)/src/.*\.(c|h)|lib/port/include/.*\.h)$
        stages: [pre-push]

  - repo: https://github.com/cpp-linter/cpp-linter-hooks
    rev: v1.8.1
    hooks:
      - id: clang-tidy
        args: [--version=23.1.3, --compile-commands=tests]
        files: ^(lib/(common|host)/src/.*\.(c|h)|lib/port/include/.*\.h)$
        stages: [pre-push]
```

### `.markdownlint-cli2.jsonc` and `.yamllint.yaml` — minimum viable policy

```jsonc
// .markdownlint-cli2.jsonc
{
  "config": { "MD013": false, "MD060": false }
}
```

```yaml
# .yamllint.yaml
extends: default
rules:
  line-length: { max: 120 }
  document-start: disable
  truthy: { allowed-values: ['true', 'false'] }
```

`markdownlint-cli2` discovers `.markdownlint-cli2.jsonc`, then `.yaml`, `.cjs`, `.mjs`
([CITED: markdownlint-cli2 README v0.24.0]); `yamllint` looks for `.yamllint`,
`.yamllint.yaml`, or `.yamllint.yml` in the CWD and its parents
([CITED: yamllint 1.38.0 docs/configuration.rst]). pre-commit runs hooks from the repo root,
so both are found without an explicit `-c`.

### `pyproject.toml` — ruff only

```toml
[tool.ruff]
line-length = 100
target-version = "py313"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]

[tool.ruff.lint.per-file-ignores]
"scripts/pio/*.py" = ["F821"]
"homeworks/*/merge_firmware.py" = ["F821"]
```

Verified with `ruff 0.17.2 --show-settings`: `linter.line_length = 100`,
`linter.unresolved_target_version = 3.13`, E/F/I/UP/B resolved.

## State of the Art

| Old approach | Current approach | When changed | Impact |
|--------------|------------------|--------------|--------|
| Hook stages named `commit`, `push`, `merge-commit` | `pre-commit`, `pre-push`, `pre-merge-commit` | pre-commit 3.2.0 | `stages: [pre-push]` only; the repo already uses the new names in `default_install_hook_types` — [VERIFIED: .pre-commit-config.yaml:2] `default_install_hook_types: [pre-commit]` |
| clang-tidy runs a default check set | clang-tidy 22+ runs **no** checks without `Checks:` | LLVM 22 | `.clang-tidy` is required; omitting it fails the hook |
| Rely on clangd's bundled resource headers | `CompileFlags.BuiltinHeaders: QueryDriver` when the server ships none | clangd config option | Makes `<stdbool.h>` resolve with esp-clangd 21.1.3 |
| `ruff` hook id | `ruff-check` (`ruff` is a legacy alias) | ruff-pre-commit | New config should use `ruff-check`; `ruff-format` would add a second mechanical diff and is not required by TOOL-03 |
| gitleaks `protect`/`detect` | `gitleaks git` / `gitleaks dir` | gitleaks 8.x | The existing hook is already on v8.30.1 and needs no change |

**Deprecated/outdated:**
- `--compile-commands-dir` as a global clangd argument — disables per-project `.clangd`
  databases in a multi-root window.
- `--query-driver='**'` — an allowlist wildcard that authorises arbitrary execution.
- `.editorconfig` as a style source — declined in D-03.

## Assumptions Log

| # | Claim | Section | Risk if wrong |
|---|-------|---------|---------------|
| A1 | `cpp-linter-hooks` filters to changed lines during the real `pre-push` stage (README documents it; not exercised here) | Pitfall 6 | Pre-existing warnings would block every push; mitigation is to clear the backlog or scope `files:` |
| A2 | A `~/.local/bin/clangd-wrapper` symlink is acceptable as a documented setup step | Pitfall 1 | The novice must run one extra command; if rejected, the fallback is "open the repo folder, not the workspace file" |
| A3 | `ln -sf` symlinks are acceptable on macOS and Linux for the guide's target audience | Pitfall 1 | Windows users are already out of scope (D-20) |
| A4 | The user accepts converting 11 `#pragma once` headers only if `portability-avoid-pragma-once` stays enabled — recommendation is to disable it for now | Pitfall 6 | Re-enabling it later is a separate mechanical change across `lib/` |
| A5 | `markdownlint-cli2`'s `MD013: false` is acceptable rather than `line_length: 120` | Pitfall 6 | Choosing 120 leaves a handful of long-line findings to fix |
| A6 | Duplicating the settings object in `.vscode/settings.json` and the generated workspace is acceptable, guarded by a drift test | Pitfall 1 | A single-source alternative would require generating `.vscode/settings.json` too, widening the generator's ownership |

## Open Questions

1. **How is the multi-root editor contract expressed?** (Pitfall 1)
   - What we know: workspace-scope settings must live in the `.code-workspace`; folder
     settings do not cross roots; `${workspaceFolder}` is unusable there; `${env:HOME}` works.
   - What is unclear: whether the intended entry point is the workspace file or the repo
     folder, and whether the symlink step is acceptable onboarding friction.
   - Recommendation: emit the same `settings` object from `workspace.json.tmpl` and
     `.vscode/settings.json`, use `${env:HOME}/.local/bin/clangd-wrapper`, and add a stdlib
     drift test. Confirm with the user before locking.

2. **What happens to D-08's "native test sources"?** (Pitfall 5)
   - What we know: no database can describe them today; `pio test` has no compiledb target.
   - What is unclear: whether the requirement intends coverage of those TUs or merely names
     the host code family.
   - Recommendation: scope clang-tidy to `lib/` host sources, record the gap in ADR 0013 and
     the guide, and leave a Phase 8 follow-up note (CI owns database generation).

3. **Is the `.clang-tidy` backlog part of this phase?**
   - What we know: 22 warnings from 2 rules.
   - Recommendation: disable `portability-avoid-pragma-once` in the committed config, fix the
     seven `bugprone-signed-bitwise` findings in `hex.c` as part of the cleanup commit, and
     keep `WarningsAsErrors: ""`.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| pre-commit | the whole phase gate | ✓ | 4.7.0 | — |
| clang-format | SC1, D-04 | ✗ locally | — | delivered by `mirrors-clang-format` (verified install) |
| clang-tidy | SC2, D-08 | ✗ locally | — | delivered by `cpp-linter-hooks` (`clang-tidy==23.1.3` wheel exists) |
| esp-clangd | SC3, TOOL-02 | ✓ | 21.1.3 (`esp-21.1.3_20260408`) | wrapper errors with install guidance if absent |
| PlatformIO Core | compiledb | ✓ | 6.2.0 | — |
| Xtensa toolchain | query-driver, compiledb | ✓ | `toolchain-xtensa-esp-elf@14.2.0+20260121`, `toolchain-xtensa-esp32s3` | — |
| Python | scripts, hooks | ✓ | 3.13.13 | — |
| uv | `uv run` gates, gen_views | ✓ | 0.13.5 | — |
| Node.js | markdownlint-cli2 hook | ✓ | 26.7.0 | pre-commit provisions its own node env |
| git | hook installation | ✓ | 2.54.0 | — |
| Host clang | *(fallback only)* | ✓ | Apple clang 21.0.0, resource dir `/Library/Developer/CommandLineTools/usr/lib/clang/21` | only needed if `BuiltinHeaders: QueryDriver` is rejected |

**Missing dependencies with no fallback:** none.
**Missing dependencies with fallback:** clang-format and clang-tidy (both come from pinned
pre-commit environments, which is D-06's intent, not a fallback).

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | `unittest` (stdlib), discovered from the repository root — 279 test functions in 59 classes today |
| Config file | none — `python3 -m unittest discover -s scripts/tests -v` |
| Quick run command | `python3 -m unittest discover -s scripts/tests -v` |
| Full suite command | the same plus `pio test -d tests -e native`, `pio test -d homeworks/1_3-police-flasher -e native`, `pre-commit run --all-files`, `uv run scripts/check_metadata.py`, `uv run scripts/gen_views.py --all --check`, `mkdocs build --strict` |

Constraint inherited from 04/D-14: **tests never import `yaml` or `jsonschema`**. A test that
must parse `.pre-commit-config.yaml` or a JSON settings file either reads text or shells out
to `uv run` with PyYAML.

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| TOOL-01 | `.clang-format` resolves to the D-02 invariants | unit (subprocess) | `python3 -m unittest scripts.tests.test_tooling_config.ClangFormatConfigTests -v` | ❌ Wave 0 |
| TOOL-01 | the whole tracked C/C++ tree is formatted | gate | `pre-commit run --all-files` | ❌ hook |
| TOOL-01 | `.clang-tidy` covers the four families and is warnings-first | unit (text) | `python3 -m unittest scripts.tests.test_tooling_config.ClangTidyConfigTests -v` | ❌ Wave 0 |
| TOOL-02 | templates, goldens and the real tree carry an identical `.clangd` | unit | existing `GoldenTreeTests` + a new fixture assertion | ❌ fixture |
| TOOL-02 | `.clangd` carries `BuiltinHeaders: QueryDriver` and `CompilationDatabase: .` | unit (text) | `...ToolingConfigTests` | ❌ Wave 0 |
| TOOL-02 | the wrapper is executable and resolves in the documented order | unit (subprocess, temp HOME) | `...ClangdWrapperTests` | ❌ Wave 0 |
| TOOL-02 | `.vscode/settings.json` and the workspace `settings` agree | unit (json) | `...EditorContractTests` | ❌ Wave 0 |
| TOOL-03 | the five pre-commit hooks and the two pre-push hooks exist with the right stages | unit (text/uv-run) | `...HookLayeringTests` | ❌ Wave 0 |
| TOOL-03 | `default_stages` is pre-commit only | unit | same | ❌ Wave 0 |
| TOOL-04 | `docs/standards/vscode.md` exists and is in the generated nav | unit + gate | `python3 -m unittest scripts.tests.test_gen_views -v` and `uv run scripts/gen_views.py --all --check` | ❌ page |
| TOOL-04 | the site builds with the new page | gate | `mkdocs build --strict` | ✅ workflow |

### Sampling Rate

- **Per task commit:** `python3 -m unittest discover -s scripts/tests -v`
- **Per wave merge:** the full suite above plus `pre-commit run --all-files`
- **Phase gate:** all eight commands green, exactly as Phase 4.2's recorded gate

### Wave 0 Gaps

- [ ] `scripts/tests/test_tooling_config.py` — `.clang-format` resolved invariants, `.clang-tidy`
      families, `.clangd` keys, hook layering, editor-contract equality
- [ ] `scripts/tests/fixtures/golden/homework-{arduino,espidf}/.clangd`
- [ ] `scripts/clang-tidy-db` (the guard) with its own unit test using a temp root
- [ ] `scripts/clangd-wrapper.sh` (mode 100755) with a test that fakes `$ESP_CLANGD`

## Security Domain

`security_enforcement: true`, ASVS level 1.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | — |
| V3 Session Management | no | — |
| V4 Access Control | no | — |
| V5 Input Validation | yes | The wrapper rejects an unresolvable binary with a message rather than exec'ing a guess; `--query-driver` is a bounded glob list, never `**`; the DB guard refuses to run on a missing database |
| V6 Cryptography | no | — |
| V10 Malicious Code | yes | Every tool is a pinned `rev` (D-06/D-07); no unpinned `npx`, `pip install`, or `brew install` in any documented step |
| V14 Configuration | yes | Hook stages, `types_or` and file scopes are explicit; no hook rewrites or stages files |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Arbitrary binary execution through `--query-driver` | Elevation of privilege | Explicit absolute globs limited to `~/.platformio/packages/toolchain-*/bin/*` and `tool-*/bin/*`; the docs' warning that this "implies executing arbitrary binaries" belongs in the ADR |
| Hook environment tampering via a floating `rev` | Tampering | Exact tag per repo; the same discipline the repo already applies to action SHAs |
| Secret leakage in a new settings/wrapper file | Information disclosure | gitleaks stays in pre-commit; no credentials are introduced |
| A generated file hand-edited and committed | Tampering | `no-generated-files` plus `gen-views-check` remain unchanged; the workspace `settings` goes through the generator |
| Symlink traversal during scaffold/regeneration | Tampering | Unchanged: `new_homework` refuses symlinked template entries; the new `.clangd` is a regular file in both templates |

## Sources

### Primary (HIGH confidence — probed this session)

- `git ls-remote --tags` for mirrors-clang-format, ruff-pre-commit, markdownlint-cli2, yamllint, cpp-linter-hooks (tags confirmed).
- PyPI JSON API: `clang-format` 23.1.3 and `clang-tidy` 23.1.3 wheels; `cpp-linter-hooks` 1.8.1.
- Pinned `.pre-commit-hooks.yaml` at each tag (hook ids, entries, `types_or`, default args).
- cpp-linter-hooks v1.8.1 README (compilation-database skip/CI behaviour, `--version`, `--compile-commands`, changed-lines filtering).
- clang-format 23.1.3 `--dump-config` and `--dry-run --Werror` on this tree.
- clang-tidy 23.1.3 over `lib/common` + `lib/host` with `tests/compile_commands.json`.
- esp-clangd 21.1.3 `--check` on `homeworks/1_3-police-flasher/src/main.cpp`, with and without `BuiltinHeaders: QueryDriver`.
- `pre-commit 4.7.0` run with a probe config (stage routing, check-only entry override).
- markdownlint-cli2 v0.24.0, yamllint 1.38.0, ruff 0.17.2 over the real tree.
- Repository files read verbatim: `.pre-commit-config.yaml`, `.gitignore`, `homeworks.code-workspace`, `templates/views/workspace.json.tmpl`, `templates/views/mkdocs.yml.tmpl`, `tests/platformio.ini`, `platformio.shared.ini`, `scripts/pio/compiledb.py`, `scripts/new_homework`, `scripts/tests/test_new_homework.py`, `scripts/tests/temp_root.py`, `docs/decisions/README.md`, `generated.manifest`, `.github/workflows/docs.yml`.
- vscode-clangd `package.json` + `src/config.ts`; vscode-cpptools `Extension/package.json`; clangd `SystemIncludeExtractor.cpp`.

### Secondary (MEDIUM confidence — official docs, not executed)

- [CITED: clangd.llvm.org/config] — `CompileFlags.CompilationDatabase`, `BuiltinHeaders`, `Remove`, `Diagnostics.Suppress`, `Index.Background`.
- [CITED: clangd.llvm.org/design/compile-commands] and [CITED: clangd.llvm.org/guides/system-headers] — `--query-driver` is a comma-separated glob allowlist; the executed driver comes from the compile command.
- [CITED: pre-commit.com] — `default_stages` defaults to all stages; stage names changed in 3.2.0; `default_install_hook_types`.
- [CITED: code.visualstudio.com/docs/configure/settings] and [CITED: microsoft/vscode#94424] — workspace vs folder settings scope, multi-root variable resolution.
- [CITED: github.com/clangd/vscode-clangd#696] — `${workspaceFolder:Name}` unsupported.
- [CITED: github.com/DavidAnson/markdownlint-cli2 v0.24.0 README] — config file discovery, `--config`, `--no-globs`.
- [CITED: adrienverge/yamllint v1.38.0 docs/configuration.rst] — config file discovery order.
- [CITED: github.com/cpp-linter/cpp-linter-hooks README] — `--version`, database auto-detection, skip-vs-CI.

### Tertiary (LOW confidence — would need a run to confirm)

- [ASSUMED] cpp-linter-hooks' changed-lines filter behaves the same in the real pre-push
  stage as its README describes (A1).
- [ASSUMED] `~/.local/bin` is a suitable machine-level location for the wrapper symlink (A2).

## Metadata

**Confidence breakdown:**
- Standard stack and pins: HIGH — every tag and wheel verified; the clang-format/clang-tidy
  mechanisms exercised end to end.
- Architecture (hook layering, generator ownership, scaffold/golden coupling): HIGH — all
  read from the pinned sources and confirmed with runs.
- Editor/multi-root contract: MEDIUM — the tool behaviour is verified from extension source,
  but the resolution (workspace `settings` + symlink) needs a user decision.
- Pitfalls / measured backlogs: HIGH — counted on the real tree.
- clang-tidy native-test-TU coverage: HIGH that it is currently impossible; MEDIUM on the
  best long-term remedy (Phase 8 CI).

**Research date:** 2026-10-26
**Valid until:** 2026-11-25 for the pins (a month); re-verify `cpp-linter-hooks` and
`mirrors-clang-format` tags if the planning window slips past an LLVM release.

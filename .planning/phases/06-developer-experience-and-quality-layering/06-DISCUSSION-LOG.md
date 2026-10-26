# Phase 6: Developer Experience and Quality Layering - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-10-26
**Phase:** 6-Developer Experience and Quality Layering
**Areas discussed:** Formatting scope, Tool delivery, Lint surface, clangd and VS Code,
Site navigation, AGENTS.md rules

---

## Formatting scope

| Option | Description | Selected |
|--------|-------------|----------|
| Whole codebase now | One mechanical commit reformats every tracked C/C++ file (lib/, homeworks/, tests/); SC1 becomes literally green | ✓ |
| Changed files only | Hook checks staged files only; existing code untouched; SC1 would need narrowing and a baseline | |
| Pilot subset | lib/, tests/, and 1.3 only; debt returns with every new folder | |

**User's choice:** Whole codebase now.
**Notes:** The existing sources are already close to the target style (4 spaces, function
brace on a new line, about 120 columns), so the mechanical diff is expected to be mostly
whitespace.

---

## Templates in the format contract

| Option | Description | Selected |
|--------|-------------|----------|
| Include now | Add the four template sources and four golden fixtures; no `{{...}}` placeholders exist in C/C++ | ✓ |
| Exclude templates/ | Lower risk for scaffold tests, but every new project starts unformatted | |
| Format at render time | `new_homework` calls clang-format; adds an external dependency to a stdlib+PyYAML script | |

**User's choice:** Include now.
**Notes:** The golden-tree test already compares template output with the fixtures, so
formatting both keeps that guarantee intact.

---

## Enforcement point

| Option | Description | Selected |
|--------|-------------|----------|
| Staged + separate --all-files | Pre-commit checks staged C/C++ only; the phase gate runs `--all-files`; check-only, consistent with D-21 | ✓ |
| Always --all-files | Every commit scans all 60 files; drift impossible but each commit pays full cost | |
| Hook fixes | Hook rewrites and stages files; convenient but makes the gate unobservable | |

**User's choice:** Staged + separate `--all-files`.
**Notes:** Check-only matches the Phase 5 D-21 rule that hooks never regenerate or stage.

---

## Style source

| Option | Description | Selected |
|--------|-------------|----------|
| Tool-specific configs only | `.clang-format`, markdownlint, yamllint, ruff; no duplication | ✓ |
| Add .editorconfig | Editor-wide defaults; two places can diverge | |

**User's choice:** Tool-specific configs only.
**Notes:** No `.editorconfig` is added.

---

## Reformat contents

| Option | Description | Selected |
|--------|-------------|----------|
| Sort includes, keep comments | `SortIncludes: true`, `ReflowComments: false` | ✓ |
| Full LLVM defaults | Sort includes and reflow comments; larger diff, hand-wrapped comments disappear | |
| Minimal footprint | No sorting, no comment reflow; smallest semantic surface | |

**User's choice:** Sort includes, do not reflow comments.
**Notes:** No order-dependent macros were identified; the hand-wrapped explanatory
comments are deliberate and stay.

---

## Config invariant test

| Option | Description | Selected |
|--------|-------------|----------|
| Add a test | One stdlib test pins IndentWidth 4, ColumnLimit 120, UseTab Never, AfterFunction true, ReflowComments false | ✓ |
| No separate test | The `--dry-run --Werror` run is the only proof; a silent policy change would pass | |

**User's choice:** Add a test.
**Notes:** Makes SC1 machine-checked rather than declared.

---

## Tool delivery

| Option | Description | Selected |
|--------|-------------|----------|
| All through pre-commit | Pinned revs for clang-format, ruff, markdownlint, yamllint; clang-tidy through cpp-linter-hooks at 23.1.3 | ✓ |
| System installs | Homebrew LLVM and linters; hooks use `language: system` | |
| Hybrid with PlatformIO clang-tidy | Use the bundled tool-clangtidy 19.1.0; no extra install, but version divergence | |

**User's choice:** All through pre-commit.
**Notes:** This is the only route that works on the current machine, where none of the
linters are installed and only clang-tidy 19.1.0 exists inside PlatformIO.

---

## Pre-push contents

| Option | Description | Selected |
|--------|-------------|----------|
| clang-tidy only | Matches SC2 literally; tests stay in the phase gate and Phase 8 CI | ✓ |
| clang-tidy + native tests | Catches regressions before push, but adds minutes and toolchain downloads | |

**User's choice:** clang-tidy only.

---

## Missing compilation database

| Option | Description | Selected |
|--------|-------------|----------|
| Refuse with instructions | Exit non-zero and print `pio run -t compiledb -d <project>`; never mutate the tree | ✓ |
| Generate automatically | Run PlatformIO inside the hook; slow, may need network, writes `.pio/` | |
| Skip with a warning | Never blocks; silently weakens the gate | |

**User's choice:** Refuse with instructions.

---

## Hook installation

| Option | Description | Selected |
|--------|-------------|----------|
| One install for both stages | `default_install_hook_types: [pre-commit, pre-push]` | ✓ |
| Separate pre-push install | Keep the current default; a missed step silently disables clang-tidy | |

**User's choice:** One install for both stages.

---

## Markdown lint surface

| Option | Description | Selected |
|--------|-------------|----------|
| Authored documents | README, AGENTS.md, authored docs, homeworks, templates, PR template; excludes `.planning/` and generated pages | ✓ |
| Everything incl. .planning/ | 242 files become lint-maintained; large low-value diff | |
| Published docs only | Smallest diff, but homework READMEs and reports stay unchecked | |

**User's choice:** Authored documents.
**Notes:** `.planning/` alone holds 211 Markdown files.

---

## Generated Markdown

| Option | Description | Selected |
|--------|-------------|----------|
| Exclude generated | The drift gate is the sole owner of their shape | ✓ |
| Lint generated too | Generator templates must emit lint-clean Markdown; doubles the contract | |

**User's choice:** Exclude generated.

---

## Ruff configuration

| Option | Description | Selected |
|--------|-------------|----------|
| pyproject.toml, 100, E/F/I/UP/B | One root config matching the existing code | ✓ |
| ruff.toml, default 88 | Stricter; adds wrapping churn | |
| No config | Defaults; the 231-character docstring in affected.py fails without explanation | |

**User's choice:** `pyproject.toml`, line length 100, `E/F/I/UP/B`.

---

## Hook mode

| Option | Description | Selected |
|--------|-------------|----------|
| Check-only + one-time --fix | Hooks report only; the cleanup is a dedicated change | ✓ |
| Auto-fix where supported | ruff and markdownlint fix staged files; yamllint checks only | |

**User's choice:** Check-only with a one-time `--fix`.

---

## YAML lint surface

| Option | Description | Selected |
|--------|-------------|----------|
| Authored YAML + templates | Workflows, homework.yaml, boards, templates, pre-commit config; excludes generated mkdocs.yml | ✓ |
| Include mkdocs.yml | The generator must emit yamllint-clean YAML | |
| Workflows only | Minimal; homework.yaml and boards style stays unchecked | |

**User's choice:** Authored YAML plus templates.

---

## .clangd delivery

| Option | Description | Selected |
|--------|-------------|----------|
| Generated by new_homework | Both templates carry the file; 1.3 gets one backfill; the golden test guards equality | ✓ (Claude's call) |
| One root .clangd | `CompilationDatabase: .` would point at the repository root, not the project | |
| Hand-authored per project | 30+ copies with drift | |

**User's choice:** "Your call" — Claude chose generation through `scripts/new_homework`.
**Notes:** AGENTS.md makes the scaffold the only creation path; the golden-tree test turns
the new file into an enforced part of the contract. The existing 1.3 receives the same
file once by hand because the scaffold has no overwrite or add-missing mode.

---

## Wrapper discovery

| Option | Description | Selected |
|--------|-------------|----------|
| ESP_CLANGD -> PATH -> ~/.espressif | Layered discovery with a clear failure message | ✓ |
| PATH only | The Espressif installer does not add the binary to PATH | |
| Absolute path | Works on this machine and breaks everywhere else | |

**User's choice:** Layered discovery.

---

## VS Code settings

| Option | Description | Selected |
|--------|-------------|----------|
| Full contract | clangd.path, cpptools disabled, format-on-save through clangd, background index | ✓ |
| Minimum | Only clangd.path and cpptools off; format-on-save is a manual step | |

**User's choice:** Full contract.

---

## Onboarding platforms

| Option | Description | Selected |
|--------|-------------|----------|
| macOS + Linux | The two real environments: local macOS and Ubuntu CI; Windows as a WSL note | ✓ |
| macOS only | Shortest; public Linux readers and CI have no instructions | |
| macOS + Linux + Windows | Extra surface with no test path in this phase | |

**User's choice:** macOS and Linux.

---

## Decision records

| Option | Description | Selected |
|--------|-------------|----------|
| Two ADRs + table rows | Formatting approximation and language-server toolchain; both have rejected alternatives | ✓ |
| Table rows only | Least ceremony; the arguments against AStyle and stock clangd are not preserved | |
| One ADR + one row | Formatting as an ADR, clangd as a row | |

**User's choice:** Two ADRs plus table rows.

---

## Site navigation

| Option | Description | Selected |
|--------|-------------|----------|
| Standards section in the template | Explicit nav entry; `gen_views` remains the owner and the drift gate covers it | ✓ |
| Auto-discover pages | New source of truth; conflicts with the explicit `nav:` decision (05/D-05) | |
| Off-navigation | The page exists but is unreachable from the site | |

**User's choice:** Standards section in the template.

---

## AGENTS.md rules

| Option | Description | Selected |
|--------|-------------|----------|
| Section + pre-push in vocabulary | Quality tooling rules and a fourth enforcement point | ✓ |
| Section without vocabulary change | pre-push tagged as pre-commit; loses the fast/slow distinction | |
| Routing table row only | Minimal; no lint rules exist in the rulebook | |

**User's choice:** A `Quality tooling` section plus `[ENFORCED: pre-push]` in the vocabulary.

---

## Claude's Discretion

- The `.clangd` delivery mechanism (user deferred with "your call"); resolved as generation
  through `scripts/new_homework`.
- The exact `.clang-tidy` check set and options.
- The exact `.clangd` flags beyond `CompilationDatabase: .`.
- The wrapper's internal structure and any path caching.
- The markdownlint and yamllint rule configuration, within the agreed paths.
- The shape of the onboarding guide and the wording of both ADRs.
- The commit split between the mechanical reformat and hook wiring.

## Deferred Ideas

- CI wiring of the quality layers — Phase 8.
- ESP-IDF `compiledb` completeness fallback — Phase 7 / first ESP-IDF homework.
- AStyle check — not built.
- Native Windows onboarding — deferred.
- `.editorconfig` — declined.
- Automatic navigation discovery for authored standards pages — declined.

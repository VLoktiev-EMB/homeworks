---
status: accepted
date: 2026-10-26
decision-makers: [VLoktiev-EMB]
consulted: []
informed: []
---

# clangd and the multi-root editor contract

## Context and Problem Statement

A beginner opens `homeworks.code-workspace`, which has five roots: the repository itself,
`docs`, `lib`, `scripts`, and the homework project. Correct ESP32-S3 IntelliSense then depends
on four things that are easy to get wrong: which clangd binary runs, which compilers clangd is
allowed to query, where clangd finds a compilation database for each root, and which settings
scope reaches every root. The stock `.vscode/settings.json` is folder-scoped, so it does not
reach the other four roots; `${workspaceFolder}` is undefined in a multi-root window. A
language server that cannot find its standard headers reports false errors on a correct
program. How should the repository configure one clangd server for the whole workspace?

## Decision Drivers

* One clangd server must serve the whole multi-root workspace; a second server would duplicate
  indexes and disagree with the first.
* The binary must be discovered at run time, because the esp-clangd directory embeds a build
  date and the PlatformIO toolchain directory embeds a package version; neither can be
  committed.
* clangd must be allowed to query the toolchain compilers, and no other binary: `--query-driver`
  authorises executing the binaries it names.
* The editor settings must reach every root, and must not rely on a variable that is undefined
  in a multi-root window.
* The per-project compilation database must be found by nearest-ancestor discovery, not by one
  global directory.
* A beginner must complete the setup with as few machine steps as possible, and each step must
  be stated exactly.

## Considered Options

* One discovered esp-clangd behind `scripts/clangd-wrapper.sh`, per-project `.clangd`, and the
  editor contract emitted in the generated workspace `settings` object.
* A bare `clangd` from `PATH` with a global `--compile-commands-dir`.
* The root `.vscode/settings.json` alone, opened as a single folder instead of the workspace.
* A hand-maintained `-I` list per project in editor settings.

## Decision Outcome

Chosen option: "one discovered esp-clangd behind `scripts/clangd-wrapper.sh`, per-project
`.clangd`, and the editor contract emitted in the generated workspace `settings` object",
because it is the only combination that reaches all five roots, discovers both versioned
directories at run time, and keeps each project's database local.

`scripts/clangd-wrapper.sh` resolves the server in a fixed order: `$ESP_CLANGD`, then
`esp-clangd` on `PATH`, then the newest `~/.espressif/tools/esp-clangd/esp-*/esp-clangd/bin/clangd`.
If none is usable it exits 2 with a message that names the installation source and points at
`docs/standards/vscode.md`; it never guesses.

The wrapper passes exactly two absolute `--query-driver` globs:
`~/.platformio/packages/toolchain-*/bin/*` and `~/.platformio/packages/tool-*/bin/*`. A
recursive `**` is never used. The clangd documentation warns that `--query-driver` implies
**executing** the named binaries to extract their system includes, so the allowlist is kept
bounded to the two PlatformIO toolchain trees.

### Builtin headers

Every committed `.clangd` sets `BuiltinHeaders: QueryDriver`. esp-clangd 21.1.3 ships only
`esp-clangd/bin/clangd` — no `lib/clang/<version>/include` tree — and clangd's system-include
extractor deliberately excludes the queried driver's builtin headers by default, keeping
clangd's own versions instead. With no clangd builtins, `stdbool.h`, `stdint.h`, and
`stddef.h` do not resolve. `BuiltinHeaders: QueryDriver` makes the queried driver supply them.
The clangd documentation also records the caveat: when the driver is not clang, the extracted
result can produce unexpected behaviour such as false-positive diagnostics. The two bounded
globs above are the mitigation; the trade-off is accepted because the alternative is an editor
that cannot resolve the standard headers at all.

### Settings scope

Workspace-scope settings for a multi-root window live in the `.code-workspace` `settings`
object. A root `.vscode/settings.json` applies only to its own folder, and vscode-clangd
substitutes `${workspaceFolder}` from `vscode.workspace.rootPath`, which is undefined in a
multi-root window, falling back to the active editor's directory. The scoped form
`${workspaceFolder:repo}` is unsupported; `${env:HOME}` is supported. The contract therefore
uses `${env:HOME}/.local/bin/clangd-wrapper` and documents one prerequisite on a clean machine:
`mkdir -p "$HOME/.local/bin"` before the symlink.

The settings object is emitted twice and kept equal by a drift test: once in
`templates/views/workspace.json.tmpl`, which `scripts/gen_views.py` renders into
`homeworks.code-workspace`, and once in the committed root `.vscode/settings.json` for a
single-folder open. The renderer rejects `${...}` in template text, so the literal path enters
through a mapping value rather than through template text.

### Suppressed diagnostics

Each project's `.clangd` suppresses `unknown-argument` and `drv_unknown_argument`. The
PlatformIO Xtensa compile commands carry GCC-only flags such as `-mdisable-hardware-atomics`
and `-fstrict-volatile-bitfields`, which a clang-based server rejects. Suppressing those two
diagnostics is what makes the GCC flags tolerable without rewriting the build. The cost is
explicit: a genuinely wrong flag added by a contributor is not reported. The flags therefore
live in the per-project `.clangd`, where review can see and change them, rather than in an
editor setting that would hide the policy.

### Consequences

* Good, because one server and one index serve every root, and each project's database is
  found by nearest ancestor from its own `.clangd`.
* Good, because no committed file names a versioned tool directory, so a toolchain update does
  not break the editor.
* Good, because the query-driver allowlist is bounded to the two PlatformIO toolchain trees.
* Bad, because the setup needs one filesystem step, the `~/.local/bin` symlink, before the
  committed `clangd.path` resolves.
* Bad, because suppressed diagnostics can hide a genuinely wrong flag; review owns that risk.
* Neutral, because esp-clangd is Espressif's build of clangd; the standard headers it supplies
  are the ones the target build uses.

### Confirmation

* `python3 -m unittest scripts.tests.test_tooling_config.ClangdWrapperTests -v` runs the real
  wrapper with a temporary `HOME`, proves the resolution order, the exit-2 diagnostics, and the
  exact two forwarded globs.
* `python3 -m unittest scripts.tests.test_tooling_config.ClangdConfigTests -v` proves the five
  `.clangd` copies are byte-identical and carry `BuiltinHeaders: QueryDriver` and both
  suppressions.
* `python3 -m unittest scripts.tests.test_tooling_config.EditorContractTests -v` proves the two
  settings objects are equal, that cpptools IntelliSense is disabled, and that `clangd.path` is
  the `${env:HOME}` value.
* `"$HOME/.local/bin/clangd-wrapper" --check homeworks/1_3-police-flasher/src/main.cpp` reports
  `All checks completed, 0 errors` on a machine with a generated database.

## Pros and Cons of the Options

### One discovered esp-clangd, per-project `.clangd`, generated workspace settings

The wrapper finds the newest esp-clangd, each project names its own database, and the settings
object is generated into the workspace.

* Good, because the versioned tool directories are discovered rather than hardcoded.
* Good, because the settings reach every root through the only scope that does.
* Good, because the drift test keeps the two emissions of one contract equal.
* Neutral, because the user must run one symlink command; the guide states it exactly.
* Bad, because the wrapper is a shell script that must remain executable in git.

### A bare `clangd` from `PATH` with a global `--compile-commands-dir`

Use whatever clangd is installed and point every project at one database directory.

* Good, because no wrapper and no per-project file are needed.
* Bad, because the system clangd need not be esp-clangd and need not be pinned.
* Bad, because a global compile-commands directory cannot describe five roots with different
  databases.
* Bad, because no `--query-driver` allowlist is established, so include extraction either
  fails or is widened unsafely.

### The root `.vscode/settings.json` alone, opened as a single folder

Open the repository folder and rely on its folder-scoped settings.

* Good, because the file is already committed and needs no generator involvement.
* Bad, because opening the workspace file — the documented entry point — would not load those
  settings for the other roots.
* Bad, because `${workspaceFolder}` in `clangd.path` resolves to the active editor's directory
  in a multi-root window.
* Bad, because the homework root would lose format-on-save and the cpptools shutdown.

### A hand-maintained `-I` list per project in editor settings

Describe include paths in the editor instead of using a compilation database.

* Good, because clangd would not need a database per project.
* Bad, because the flag list duplicates the build system and drifts from it.
* Bad, because it becomes a second build system in an editor setting, which the phase's
  clang-tidy scope rule already forbids.
* Bad, because the database the build already emits would be ignored.

## More Information

The formatter the server applies on save is recorded in
`docs/decisions/0012-formatting-approximation.md`. The beginner-facing steps are in
`docs/standards/vscode.md`.

### Native test translation units

clang-tidy does not analyse native test sources. `tests/compile_commands.json` describes
`lib/common/src/*.c`, `lib/host/src/*.c`, Unity's `unity.c`, and `tests/src/main.c`, but no
file under `tests/test/**`; `pio test` exposes no compilation-database target. Running
clang-tidy on a test source borrows the `tests/src/main.c` command, whose include paths do not
describe a test build, and fails on a missing `unity_config.h`. The pre-push scope is therefore
host-compiled code only. The gap is handed to Phase 8, where CI owns database generation and
can decide whether a test build can be described without a second build system.

### Analysed scope: translation units, not headers

Plan 06-04 probed both pre-push hooks against `lib/common/include/common/hex.h` and
`lib/port/include/port/gpio.h`; both exited 0. That zero did not prove analysis: a bare header
has no compile command in `tests/compile_commands.json`, so clang-tidy skipped it and exited 0.
Pinned clang-tidy 23.1.3 skips silently; older builds print
`Skipping <file>. Compile command not found.`. Either way `cpp-linter-hooks` reported success.

The resolved contract is the narrow one. Both hook `files` patterns reach `.c` files under
`lib/common/src` and `lib/host/src` only, and `scripts/clang-tidy-hook` fails before running when
a source argument is absent from the database (closing the silent path) and also on a
`Compile command not found` line (closing the older path), so a skipped file can never be
reported as checked. A header is analysed through a translation unit that includes it, and the
unanchored `HeaderFilterRegex` is what lets the diagnostics those units emit for headers surface.
`lib/port` has no translation unit of its own and is covered only where a unit includes it. A
header-only change is therefore not analysed locally; Phase 8 CI, which owns database generation,
is where broader coverage belongs.

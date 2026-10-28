# VS Code setup

This page takes you from a clean macOS or Linux machine to a working ESP32-S3 editor:
correct includes, format-on-save, an empty Problems panel, and a check you can run with no
board attached. Windows is supported only through WSL; see the note at the end.

The gate's formatters and linters are pinned in pre-commit: you never install one of them by
hand and you do not need a system package manager for one, because the pinned hooks supply them
at exact revisions in pre-commit-owned environments. The one editor component you do install by
hand is esp-clangd, the language server and on-save formatter covered below.

## Before you start

You need:

- VS Code.
- `git`, the PlatformIO Core CLI (`pio`), the `uv` runner, and the `pre-commit` runner on
  `PATH`. Install each from its own upstream documentation; this repository does not pin the
  runners themselves.
- esp-clangd from the Espressif IDF tools installer. It lands under
  `~/.espressif/tools/esp-clangd/esp-*/esp-clangd/bin/clangd`; the wrapper finds the newest
  build, so never hardcode that path.

Open the repository root once (`code .`) and work from a terminal there.

## Install the extensions

Install two extensions:

- `llvm-vs-code-extensions.vscode-clangd` — the language server that supplies IntelliSense,
  diagnostics, and formatting.
- `platformio.platformio-ide` — builds, uploads, and the serial monitor.

The workspace lists `ms-vscode.cpptools-extension-pack` and `pioarduino.pioarduino-ide` as
unwanted recommendations. The committed settings disable cpptools IntelliSense, so installing
it would only add a second, conflicting set of squiggles.

## Make the wrapper reachable: the one repository-specific machine step

The committed editor contract points `clangd.path` at
`${env:HOME}/.local/bin/clangd-wrapper`. A multi-root workspace has no folder scope for that
setting and `${workspaceFolder}` is undefined there, so the wrapper must exist at a
home-relative path. One command creates both the directory and the symlink:

```bash
mkdir -p "$HOME/.local/bin" && ln -sf "$PWD/scripts/clangd-wrapper.sh" "$HOME/.local/bin/clangd-wrapper"
```

Run it once from the repository root. The `mkdir -p` half matters: `~/.local/bin` does not
exist on a clean macOS or Linux home. This is the one repository-specific machine step in
this guide; installing VS Code, the extensions, and esp-clangd are machine-level steps too,
and they are covered above.

`scripts/clangd-wrapper.sh` resolves esp-clangd in a fixed order: `$ESP_CLANGD`, then
`esp-clangd` on `PATH`, then the newest build under `~/.espressif/tools/esp-clangd/`. It also
passes a bounded `--query-driver` allowlist: two PlatformIO toolchain globs plus the host
compiler candidates `/usr/bin/gcc`, `/usr/bin/cc` and `/usr/bin/clang` that exist, so clangd
may execute only those compilers.

## Install the git hooks

One command wires both hook stages:

```bash
pre-commit install
```

`default_install_hook_types` is `[pre-commit, pre-push]`, so this single command installs the
fast checks that run on every commit and the static analysis that runs on every push. Running
it twice is harmless.

## Generate a compilation database

clangd reads a compilation database, not a guess about include paths. Generate the
per-project database whenever the build flags change:

```bash
pio run -d homeworks/<id> -t compiledb
```

The database is written to the project root and is never committed. Each homework carries
its own `.clangd`, so one clangd server serves the whole multi-root workspace and finds each
project's database by nearest ancestor. No global compile-commands directory is set.

The shared libraries under `lib/` sit outside every project, so clangd finds no database
above them. Build the three source databases the root database is assembled from:

- `pio run -d tests -e native -t compiledb`
- `pio run -d homeworks/<id> -t compiledb` (for an active Arduino homework)
- `pio run -d templates/homework-espidf -e esp32s3_espidf -t compiledb`

Then regenerate the root database with one command:

```bash
uv run scripts/gen_clangd_db.py
```

Alternatively, pass `--generate` to build any missing or stale source databases (and required
generated headers such as `sdkconfig.h`) automatically in one step:

```bash
uv run scripts/gen_clangd_db.py --generate
```

You can also run this in VS Code via `Terminal -> Run Task... -> Clangd: Regenerate Compilation Database`.

The root database is written at the repository root, is a build artifact, and stays
untracked. Project files and `tests/` files keep their nearest database; the root database
is the fallback for `lib/`. `lib/port` is header-only, so its headers are served by
inference from the nearest native entry rather than by an entry of their own.

## Format on save

The committed settings enable `editor.formatOnSave` for C and C++ and name clangd as the
formatter. Save a file and the committed `.clang-format` applies: four-space indent, a
120-column limit, and function braces on their own line. Format-on-save is therefore the
normal path; you do not format by hand.

`.clang-format` is an approximation of ESP-IDF style, which is AStyle, not clang-format.
Treat it as the repository's single standard, not as byte equivalence with the framework.

## Read the Problems panel

Open a source file such as `homeworks/<id>/src/main.cpp` and open the Problems panel (`View ->
Problems`, or `Ctrl+Shift+M` on Linux and `Cmd+Shift+M` on macOS). Expect no errors.

When clangd reports a problem, read the diagnostic's warning name:

- A `clang` or `clang-tidy` diagnostic comes from the language server and is actionable.
- `drv_unknown_argument` and `unknown-argument` are suppressed in the per-project `.clangd`,
  because GCC-only Xtensa flags are expected for a clang-based server. If one appears anyway,
  the project's `.clangd` is missing or is not the file in use.
- `pp_file_not_found` for `stdbool.h`, `stdint.h`, or `stddef.h` means
  `BuiltinHeaders: QueryDriver` is missing from `.clangd`, or the selected compiler cannot
  be queried.

To see the same analysis without the editor, run the wrapper directly:

```bash
"$HOME/.local/bin/clangd-wrapper" --check=homeworks/<id>/src/main.cpp
```

esp-clangd declares the flag as `--check[=<string>]`, so the value is attached with `=`; a
detached path is passed as a stray positional argument and clangd rejects it.

Expect `All checks completed, 0 errors` and exit code 0.

## Check without hardware

Two commands work with no board attached:

```bash
pio test -d tests -e native
pio run -d homeworks/<id>
```

The first runs the shared-library Unity suite on the host. The second compiles the homework
for its target environment without uploading. A no-hardware simulation path is not part of
this setup; it belongs to Phase 7.

## Hooks you will meet

14 hooks run on commit and 2 on push. The formatters and linters among them come from the
pinned pre-commit environments; esp-clangd, covered above, is the one hand-installed component,
and it runs in the editor rather than in the gate.

On commit:

- `gitleaks` — a staged credential was detected. Rotate the credential first, then remove it
  with a forward fix; never rewrite history.
- `trailing-whitespace` — a staged file carries trailing whitespace. The hook rewrites it and
  fails; re-stage the file and commit again.
- `end-of-file-fixer` — a staged text file does not end with one newline. The hook rewrites it
  and fails; re-stage the file and commit again.
- `check-merge-conflict` — a merge-conflict marker is still in a staged file.
- `check-added-large-files` — a staged file exceeds 1024 kB and is not one of the declared Git
  LFS types.
- `clang-format` — a staged C or C++ file does not match `.clang-format`. The hook only
  reports and never rewrites; reformat the file, then run
  `pre-commit run clang-format --files <path>` to confirm.
- `ruff-check` — a Python file violates the policy in `pyproject.toml`. The hook does not
  rewrite the file, so fix the finding and commit again.
- `yamllint` — an authored YAML file violates `.yamllint.yaml`.
- `markdownlint-cli2` — an authored Markdown file violates `.markdownlint-cli2.jsonc`.
- `no-generated-files` — a generated path (`compile_commands.json`, `site/`, `.pio/`, or an
  ESP-IDF build output inside a homework) is tracked. Remove it from the index.
- `check-architecture` — `lib/common` or `lib/port` gained a framework header, or `common`
  depends on an adapter. Fix the dependency rather than relaxing the checker.
- `check-metadata` — a `homework.yaml`, `task.md`, board profile, or schema is invalid. Read
  the message and correct the document.
- `gen-views-check` — a committed generated view is out of sync. Run
  `uv run scripts/gen_views.py --all`, review the diff, and commit the regenerated output.
- `gen-skills-check` — the committed `.agents/skills/` mirror is out of sync with
  `.claude/skills/`. Run `uv run scripts/gen_skills.py`, review the diff, and commit the
  regenerated mirror.

On push:

- `clang-tidy-db` — `tests/compile_commands.json` is absent, older than a configuration input
  or a described source, or missing a `.c` file under `lib/common/src` or `lib/host/src`.
  Regenerate it with `pio run -d tests -e native -t compiledb`; the hook never generates the
  database for you.
- `clang-tidy` — static analysis found a finding in a host translation unit at the pinned
  clang-tidy revision. It also fails when clang-tidy skips a file because the database has no
  compile command for it, so a green hook always means the file was analysed.

clang-tidy analyses the host translation units under `lib/common/src` and `lib/host/src`. A
header is analysed through a unit that includes it, never as a file of its own, so a
header-only change is not analysed locally; `lib/port` has no source of its own and is covered
only where a unit includes it. Native test translation units are out of scope: `pio test`
exposes no compilation-database target, so a test source is not analysed. That gap is recorded
in the clang-tidy decision record and belongs to Phase 8 CI.

## Windows

Native Windows is not supported by this setup. Install WSL 2, run the guide above inside the
Linux distribution, and open the workspace from that filesystem. Opening a WSL path from the
Windows-side VS Code is a different setup and is not covered here.

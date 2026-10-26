---
title: Shared-library IntelliSense is broken because no compile database is discoverable from lib/
date: 2026-10-26
context: Exploration after Phase 6 completed; explains why clangd reports errors in lib/**/*.c and why the fix is a separate phase
---

# Shared-library IntelliSense: diagnosis

## Problem

Opening almost any `.c`/`.cpp` under `lib/` shows clangd errors, for example
`lib/arduino/src/log.c`:

```text
#include <Arduino.h>            'Arduino.h' file not found
port_log_level_t                Unknown type name
PORT_LOG_ERROR                  Use of undeclared identifier
log_printf                      Call to undeclared function
port_log_t                      Unknown type name
```

This is not a broken toolchain. The header chain is correct: `lib/arduino/include/arduino/log.h`
includes `port/log.h`, and the source is valid C.

## Root cause

clangd resolves a file by walking **upward** from that file and using the first
`compile_commands.json` it finds. It never looks sideways into a sibling directory.

- `lib/arduino/src/log.c` → `lib/arduino/src`, `lib/arduino`, `lib`, repo root.
- There is no `compile_commands.json` and no `.clangd` at the repo root or under `lib/`.
- The only databases are siblings: `homeworks/1_3-police-flasher/compile_commands.json`
  and `tests/compile_commands.json`.

The homework database **does** contain the right command for the file:

```json
{ "directory": ".../homeworks/1_3-police-flasher",
  "file": "/Users/vloktiev/Dev/miltech/homeworks/lib/arduino/src/log.c",
  "command": "xtensa-esp32s3-elf-gcc ... -c" }
```

but clangd cannot reach it from `lib/`. With no compile command there are no `-I` paths,
no Arduino core headers and no `-D` defines, which produces exactly the error chain above.

The homework's own sources work only because `homeworks/1_3-police-flasher/.clangd` sets
`CompilationDatabase: .` and the database sits next to it. `tests/compile_commands.json`
covers `lib/common`, `lib/host` and `lib/port`, but has the same discovery problem.

Scope of the defect: every `.c`/`.cpp` outside `homeworks/1_3-police-flasher/` — `lib/`,
`templates/`, fixtures — i.e. "almost every file" in the workspace.

## Chosen fix

A generated **root** `compile_commands.json` plus a root `.clangd` with shared safe
defaults. clangd prefers the nearest database, so project and `tests/` files keep their
own; the root database becomes the fallback for `lib/**` only.

Per-subtree context mapping (one compile command per path is a physical constraint):

| Subtree | Command source |
|---|---|
| `lib/common`, `lib/port`, `lib/host` | `tests/compile_commands.json` (native, neutral context) |
| `lib/arduino` | `homeworks/1_3-police-flasher/compile_commands.json` (Arduino env) |
| `lib/espidf` | a database generated from `templates/homework-espidf` |

The root database is a build artifact: it stays untracked (`.gitignore` already excludes
`compile_commands.json`), and the one regeneration command is documented next to the
existing `pio run -d tests -e native -t compiledb` instruction in
`docs/standards/vscode.md`.

Rejected alternative: five hand-written `.clangd` files with `CompilationDatabase:`
pointing at `../../homeworks/1_3-police-flasher`. It works for Arduino but couples a
shared library to one specific homework path and leaves `lib/espidf` with no database at
all — so it cannot deliver "everywhere".

## Sequencing constraint

Phase 6 is complete but unmerged; its branch (`gsd/phase-6-…`) carries the wrapper,
`.clangd` files and the onboarding guide. Phase branching forks from `origin/HEAD`, so a
new phase started before the Phase 6 merge would lack `scripts/clangd-wrapper.sh` and the
guide it must extend. Merge Phase 6 first, then create the follow-up phase from `main`.

## Evidence commands

```bash
# Fails today: no compile command is discoverable from lib/
~/.local/bin/clangd-wrapper --check=lib/arduino/src/log.c

# Succeeds today: the homework database is next to the file
~/.local/bin/clangd-wrapper --check=homeworks/1_3-police-flasher/src/main.cpp
```

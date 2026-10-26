---
created: 2026-10-26T00:00:00.000Z
title: Generate a root compile database so lib/ has working IntelliSense
area: tooling
severity: major
resolves_phase: 6.1
files:
  - scripts/gen_clangd_db.py
  - .clangd
  - docs/standards/vscode.md
  - scripts/tests/test_tooling_config.py
  - .gitignore
---

## Problem

clangd reports `Arduino.h` not found and unknown `port_*` types in nearly every
`.c`/`.cpp` under `lib/`, because it walks upward from the file and finds no
`compile_commands.json` or `.clangd` at the repository root. The databases that cover
those files are siblings under `homeworks/1_3-police-flasher/` and `tests/`, which clangd
never consults. Full diagnosis: `.planning/notes/lib-intellisense-clangd-diagnosis.md`.

This contradicts the Phase 6 goal ("A novice can open the workspace, get correct ESP32
IntelliSense"), which the phase verification did not test for `lib/`.

## Solution

Deliver as a thin decimal phase `6.1-lib-intellisense`, after Phase 6 is merged:

1. **Precondition — merge Phase 6 first.** A new phase branches from `origin/HEAD`; it
   needs `scripts/clangd-wrapper.sh`, the per-project `.clangd` files and
   `docs/standards/vscode.md` on `main`.
2. **Generator.** `scripts/gen_clangd_db.py` reads the native (`tests/`), Arduino
   (`homeworks/1_3-police-flasher/`) and ESP-IDF (`templates/homework-espidf`) databases,
   keeps exactly one entry per `lib/**` source, and writes a root
   `compile_commands.json`. Fail with the exact `pio run -d <project> -t compiledb`
   command when a source database is missing — never silently emit a partial database.
3. **Root `.clangd`.** Shared safe defaults only: `BuiltinHeaders: QueryDriver`, the
   Xtensa `Remove:` list and `Diagnostics: Suppress` already proven in the homework
   `.clangd`. No hardcoded toolchain paths (D-17).
4. **Guide.** One regeneration command in `docs/standards/vscode.md`, next to the existing
   `compiledb` instruction, stating that the root database is untracked.
5. **Coverage test.** Assert every `lib/**/*.c` has an entry in the generated database and
   that a missing source database produces the documented error.
6. **Acceptance.** `clangd-wrapper --check=` exits 0 with `All checks completed, 0 errors`
   for one file from each of `lib/arduino`, `lib/espidf`, `lib/port`, `lib/common` and
   `lib/host`.

Boundary to state in the plan: `lib/port` and `lib/common` are compiled in three
environments, so one representative context (native) is chosen deliberately; this is not
a wrong-command bug.

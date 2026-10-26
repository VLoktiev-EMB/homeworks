---
status: testing
phase: 06-developer-experience-and-quality-layering
source: [06-VERIFICATION.md]
started: 2026-10-26T11:55:00Z
updated: 2026-10-26T11:55:00Z
---

## Current Test

number: 1
name: Live ESP32-S3 include resolution through esp-clangd
expected: |
  `pio run -d homeworks/1_3-police-flasher -t compiledb` succeeds, then
  `"$HOME/.local/bin/clangd-wrapper" --check homeworks/1_3-police-flasher/src/main.cpp`
  prints `All checks completed, 0 errors` and exits 0. Opening the folder in VS Code
  with the clangd extension shows no squiggles on the ESP32/Arduino includes.
awaiting: user response

## Tests

### 1. Live ESP32-S3 include resolution through esp-clangd
expected: `clangd-wrapper --check homeworks/1_3-police-flasher/src/main.cpp` prints `All checks completed, 0 errors`, exit 0; no squiggles in VS Code.
result: [pending]

### 2. Format-on-save and Problems panel in a live VS Code
expected: Saving a C/C++ file reformats it per `.clang-format`; the Problems panel is empty for the tracked sources; clangd reports `All checks completed`.
result: [pending]

### 3. No-hardware beginner path from the guide
expected: Following `docs/standards/vscode.md` on a machine with no board attached, the named commands (`pio test -d tests -e native`, `pio build/run` for the homework) work and the guide does not promise a simulation path.
result: [pending]

## Summary

total: 3
passed: 0
issues: 0
pending: 3
skipped: 0
blocked: 0

## Gaps

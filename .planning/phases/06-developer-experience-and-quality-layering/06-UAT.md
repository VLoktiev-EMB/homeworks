---
status: complete
phase: 06-developer-experience-and-quality-layering
source: [06-VERIFICATION.md]
started: 2026-10-26T11:55:00Z
updated: 2026-10-26T12:08:24.865Z
---

## Current Test

[testing complete]

## Tests

### 1. Live ESP32-S3 include resolution through esp-clangd
expected: `clangd-wrapper --check homeworks/1_3-police-flasher/src/main.cpp` prints `All checks completed, 0 errors`, exit 0; no squiggles in VS Code.
result: issue
reported: "(eval):1: no such file or directory: /Users/vloktiev/.local/bin/clangd-wrapper — after creating the documented symlink, `clangd-wrapper --check homeworks/1_3-police-flasher/src/main.cpp` fails with `clangd: Unknown command line argument 'homeworks/1_3-police-flasher/src/main.cpp'` and exit 1"
severity: major

### 2. Format-on-save and Problems panel in a live VS Code
expected: Saving a C/C++ file reformats it per `.clang-format`; the Problems panel is empty for the tracked sources; clangd reports `All checks completed`.
result: pass
note: "First save did nothing: the clangd extension was absent from VS Code and the wrapper symlink did not yet exist. After installing `llvm-vs-code-extensions.vscode-clangd` v0.6.0 and reloading the window, saving restored the file to the committed style (`git diff` empty, `clang-format --dry-run --Werror` passes)."

### 3. No-hardware beginner path from the guide
expected: Following `docs/standards/vscode.md` on a machine with no board attached, the named commands (`pio test -d tests -e native`, `pio build/run` for the homework) work and the guide does not promise a simulation path.
result: pass

## Summary

total: 3
passed: 2
issues: 1
pending: 0
skipped: 0
blocked: 0

## Gaps

- gap_id: G-06-1
  truth: "`\"$HOME/.local/bin/clangd-wrapper\" --check homeworks/1_3-police-flasher/src/main.cpp` prints `All checks completed, 0 errors` and exits 0."
  status: failed
  reason: "User reported: /Users/vloktiev/.local/bin/clangd-wrapper: no such file or directory; after creating the documented symlink, `clangd-wrapper --check homeworks/1_3-police-flasher/src/main.cpp` fails with `clangd: Unknown command line argument 'homeworks/1_3-police-flasher/src/main.cpp'` (exit 1)"
  severity: major
  test: 1
  root_cause: "esp-clangd 21.1.3 declares `--check[=<string>]`, so the value must be attached: `--check=<file>`. The guide documents the space-separated `--check <file>`, which leaves `--check` with an empty value and passes the path as a stray positional argument. The wrapper forwards arguments verbatim, so it cannot compensate. With `--check=<file>` the same invocation prints `All checks completed, 0 errors` and exits 0."
  artifacts:
    - path: "docs/standards/vscode.md"
      issue: "line 112 documents `--check <file>`; esp-clangd requires `--check=<file>`"
    - path: ".planning/phases/06-developer-experience-and-quality-layering/06-VERIFICATION.md"
      issue: "lines 109 and 346 repeat the non-working invocation in the manual-test contract"
  missing:
    - "Change the guide's verification command to `--check=homeworks/1_3-police-flasher/src/main.cpp`."
    - "Update the same invocation in 06-VERIFICATION.md so the manual-test contract matches the working form."
  debug_session: ""

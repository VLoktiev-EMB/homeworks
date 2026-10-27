---
phase: 11-pilot-homework-1-3-finalization
plan: 01
status: complete
completed_at: "2026-10-28T00:42:30+02:00"
commit: "7e58c70"
files_modified:
  - docs/standards/report.md
  - docs/standards/vscode.md
  - scripts/gen_clangd_db.py
  - scripts/gen_schematic.py
  - templates/homework-arduino/.clangd
  - templates/homework-espidf/.clangd
---

# Plan 11-01 Summary: Generic Infrastructure Decoupling

## What was done
1. **Dynamic Homework Discovery (`scripts/gen_clangd_db.py`)**:
   - Replaced hardcoded `Path("homeworks") / "1_3-police-flasher" / "compile_commands.json"` with dynamic homework discovery via `find_arduino_source(root)` and `get_sources(root)`.
   - The script scans `homeworks/` for active homework compilation databases or manifests, and falls back to generic `<id>` placeholders with instructions if none are found.
   - Removed all hardcoded mentions of `1_3-police-flasher` from comments and docstrings.
2. **Generic Schematic Tooling (`scripts/gen_schematic.py`)**:
   - Updated CLI argument help from `(e.g. homeworks/1_3-police-flasher)` to `(e.g. homeworks/<id>)`.
   - Updated layout docstring to reference generic anti-parallel LED circuits instead of `1_3-police-flasher`.
3. **Decoupled Template Configurations (`templates/homework-*/.clangd`)**:
   - Replaced comments citing `homeworks/1_3-police-flasher/src/main.cpp` with `homeworks/<id>/src/main.cpp` in both Arduino and ESP-IDF templates.
4. **Decoupled Documentation Standards (`docs/standards/vscode.md`, `docs/standards/report.md`)**:
   - Replaced all explicit `1_3-police-flasher` commands and references with generic `homeworks/<id>` placeholders.
5. **Verification**:
   - `python3 -m unittest discover scripts/tests`: 397 tests passed green.
   - `uv run scripts/gen_clangd_db.py`: dynamically discovered homework compile commands and succeeded with 15 entries from 3 databases.
   - `pre-commit run --all-files`: 14/14 checks passed green.

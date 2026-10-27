---
task: 261027-ut2
status: complete
date: 2026-10-27
slug: all-3-schematic-approaches
provides:
  - "Schemdraw IEEE vector electrical schematic generator in scripts/gen_schematic.py (--svg)"
  - "Solderless breadboard layout (wokwi-breadboard-half) and Manhattan routing for Wokwi (--format)"
  - "Lightweight GitHub Mermaid flowchart generation (--mermaid)"
  - "Unified --all flag generating all three visualization tiers"
  - "assets/schematic.svg and breadboard assets/diagram.json for 1_3-police-flasher"
  - "Updated schematic skill v1.2 with mirrored .agents/skills/schematic/"
affects: [scripts, homeworks/1_3-police-flasher, skills]
---

# Quick Task Summary: All 3 Schematic Approaches (Schemdraw, Wokwi, Mermaid)

## Overview

Successfully delivered a complementary 3-tier circuit visualization architecture:
1. **Schemdraw (`schematic.svg`)**: IEEE standard vector electrical schematic featuring standard electronic symbols (diodes, resistors, pushbuttons, IC pinouts, ground, power rails) for academic reports, articles, and documentation.
2. **Wokwi Breadboard (`diagram.json`)**: Realistic half-size solderless breadboard layout (`wokwi-breadboard-half`) with power rails, orthogonal Manhattan jumpers, and no floating components, verified with `wokwi-cli lint --offline`.
3. **Mermaid (`flowchart LR`)**: Direct Markdown block diagram for lightweight GitHub rendering without external dependencies.

## Key Changes

1. **`scripts/gen_schematic.py`**:
   - Added PEP 723 dependency: `schemdraw==0.23`.
   - Implemented `generate_schematic_svg(output_path: Path) -> Path`: generates crisp vector SVG with central ESP32-S3 block, MODE button, anti-parallel pair with Node X, and indicator LED.
   - Updated `reformat_police_flasher_diagram` to place `wokwi-breadboard-half` (`bb1`), route `3V3`/`GND` to breadboard rails (`bb1:tp.1`, `bb1:tn.1`), and connect components along tie strips (e.g. Node X on row 12).
   - Added CLI options: `--svg`, `--format`, `--mermaid`, and `--all`.
2. **`homeworks/1_3-police-flasher`**:
   - Generated `assets/schematic.svg` (12 KB vector SVG) and declared it in `homework.yaml` assets.
   - Formatted `assets/diagram.json` with solderless breadboard layout.
   - Embedded vector schematic, breadboard reference, and Mermaid diagram into `README.md` and `report.md`.
3. **Skills (`.claude/skills/schematic/` & `.agents/skills/schematic/`)**:
   - Updated `schematic` skill to version 1.2 describing all three tiers, rules, and commands.
   - Synced mirror using `uv run scripts/gen_skills.py` with verified zero drift.
4. **Verification**:
   - Added 11 unit tests in `scripts/tests/test_gen_schematic.py` covering SVG XML output, breadboard layout, Manhattan routing, and CLI flags.
   - All quality gates passed (pre-commit, metadata contract, report contract, native tests, build).

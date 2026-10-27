---
task: 261027-ut2
status: planned
date: 2026-10-27
slug: all-3-schematic-approaches
---

# Quick Task: Implement All 3 Schematic Approaches (Schemdraw, Wokwi Breadboard, Mermaid)

## Objective
Deliver three complementary circuit visualization approaches for homework assignments:
1. **Schemdraw (`schematic.svg`)**: Vector IEEE/IEC electrical schematic with standard electronic symbols (resistors, diodes, switches, IC pinouts, power rails) for reports and academic documentation.
2. **Wokwi Breadboard (`diagram.json`)**: Realistic physical breadboard layout (`wokwi-breadboard-half`) for the interactive simulator, eliminating floating components and showing students exactly how to wire jumpers on a physical bench.
3. **Mermaid Flowchart (`flowchart LR`)**: Lightweight, zero-dependency text-based block diagram embedded directly in Markdown for quick GitHub browsing.

## Plan Breakdown

### Task 1: Add Schemdraw SVG Generation to `scripts/gen_schematic.py`
- Add `schemdraw` dependency to `scripts/gen_schematic.py` (`# dependencies = ["PyYAML==6.0.3", "schemdraw==0.23"]`).
- Implement `generate_schematic_svg(hw_dir: Path) -> Path`:
  - Draws an IEEE-standard electrical diagram:
    - Central ESP32-S3 block with GPIO 4, 6, 7, 3V3, GND.
    - Button branch (GPIO 7 -> Pushbutton MODE -> GND).
    - Branch 1 (GPIO 4 -> R1 150Ω -> Anti-parallel pair: LED1 forward to GND, LED2 reverse to 3V3).
    - Branch 2 (GPIO 6 -> R2 150Ω -> LED3 forward to GND).
  - Saves vector SVG to `<hw_dir>/assets/schematic.svg`.
- Add `--svg` flag to CLI.
- Add unit tests in `scripts/tests/test_gen_schematic.py`.

### Task 2: Layout Wokwi Diagram with `wokwi-breadboard-half`
- Update `reformat_police_flasher_diagram` in `scripts/gen_schematic.py` to support breadboard layout:
  - Add `wokwi-breadboard-half` (`id: "bb1"`).
  - Position components on the breadboard:
    - Button `btn1` spanning breadboard center divider.
    - Resistors `r1`, `r2` plugged into breadboard rows.
    - LEDs `led1`, `led2`, `led3` plugged into corresponding rows.
    - Power rails (`bb1:tp.1` for 3.3V, `bb1:tn.1` for GND) supplied from ESP32.
    - Clean, realistic jumper wires.
- Reformat `homeworks/1_3-police-flasher/assets/diagram.json` and verify with `wokwi-cli lint --offline`.

### Task 3: Update Documentation & Skills
- Embed both `assets/schematic.svg` and the Mermaid diagram in `homeworks/1_3-police-flasher/README.md` and `report.md`.
- Update `.claude/skills/schematic/SKILL.md` (and mirrored `.agents/skills/schematic/`) to document all three tiers:
  - When to use Schemdraw vs Wokwi vs Mermaid.
  - Commands for each format.
- Run full test suite, pre-commit, and open PR.

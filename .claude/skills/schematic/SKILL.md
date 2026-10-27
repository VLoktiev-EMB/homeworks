---
name: schematic
description: Use when designing, editing, or formatting Wokwi diagram.json schematics, generating IEEE Schemdraw vector SVGs, creating Mermaid circuit flowcharts for READMEs or reports, or untangling overlapping wiring.
metadata:
  version: "1.2"
  status: active
---

# Schematic

Automate and format Wokwi `diagram.json` breadboard layouts, generate IEEE standard vector SVGs via Schemdraw, and create clean, readable Mermaid circuit diagrams.

## Overview

A circuit representation must be visually clear, verifiable, and suited to its consumption context. This repository adopts a three-tier visualization approach:

1. **IEEE Vector Schematic (`schematic.svg`)**: Generated via `schemdraw` Python library, using standard electrical symbols (resistors, diodes, switches, IC blocks, power/ground rails) for reports and academic papers.
2. **Interactive Breadboard Model (`diagram.json`)**: Solderless half-size breadboard (`wokwi-breadboard-half`) for the interactive Wokwi simulator, showing realistic component placement and orthogonal jumper wire routing.
3. **Markdown Block Diagram (`flowchart LR`)**: Lightweight, zero-dependency Mermaid diagram embedded directly in GitHub Markdown for quick browsing.

## When to Use

- Designing or updating Wokwi `assets/diagram.json` on a breadboard.
- Generating crisp vector electrical schematics (`assets/schematic.svg`) for reports.
- Generating a GitHub-flavored Mermaid flowchart for `README.md` or `report.md`.
- Resolving cluttered, tangled, or diagonally crossing wires in the Wokwi editor.
- Linting circuit connections offline using `wokwi-cli`.

### When NOT to Use

- For simulating firmware execution (use `simulate`).
- For PlatformIO building or flashing (use `hw-build` or `hw-flash`).

## Quick Reference

| Operation | Command | Output |
|---|---|---|
| Generate IEEE vector schematic SVG | `uv run scripts/gen_schematic.py homeworks/<id> --svg` | `assets/schematic.svg` |
| Format breadboard & Manhattan routing | `uv run scripts/gen_schematic.py homeworks/<id> --format` | `assets/diagram.json` |
| Generate Mermaid diagram for Markdown | `uv run scripts/gen_schematic.py homeworks/<id> --mermaid` | stdout (Markdown) |
| Complete 3-tier generation | `uv run scripts/gen_schematic.py homeworks/<id> --all` | SVG + JSON + Mermaid |
| Check diagram formatting status | `uv run scripts/gen_schematic.py homeworks/<id> --check` | return code 0/1 |
| Lint Wokwi circuit offline (no quota) | `wokwi-cli lint --offline homeworks/<id>/assets/diagram.json` | lint diagnostics |

## Breadboard & Layout Rules

When arranging components in Wokwi diagrams:

1. **Breadboard Integration**: Use `wokwi-breadboard-half` (`bb1`) adjacent to the microcontroller (`esp`).
2. **Power Rails**: Connect `3V3` and `GND` from the MCU to breadboard power rails (`bb1:tp.1`, `bb1:tn.1`). Components connect to rails rather than stretching long wires back to MCU header pins.
3. **Manhattan Routing**: Never leave routing instructions empty (`[]`) for complex connections. Use `["h...", "v..."]` offsets so wires travel along right angles without cutting across components or each other.
4. **Color Standards**:
   - Power (`3.3V` / `5V`): `red`
   - Ground (`GND`): `black`
   - Control / Signals: dedicated distinct colors (`green`, `blue`, `orange`, `purple`).

## Common Mistakes & Red Flags

- **Red Flag**: Floating components in empty space in Wokwi diagrams when a breadboard should be used.
- **Red Flag**: Empty bend arrays (`[]`) on connections that cross components, producing straight diagonal wires slicing through ICs. Always define Manhattan waypoints (e.g. `["h40", "v80"]`).
- **Mistake**: Inverting LED anode (`A`) and cathode (`C`), causing reverse bias and unlit LEDs.
- **Mistake**: Committing large raster PNG/JPG screenshots instead of scalable vector SVG (`schematic.svg`) and embedded Mermaid text.

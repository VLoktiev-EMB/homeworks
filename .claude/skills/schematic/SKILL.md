---
name: schematic
description: Use when designing, editing, or formatting Wokwi diagram.json schematics, generating Mermaid circuit flowcharts for READMEs or reports, or untangling overlapping wiring.
metadata:
  version: "1.1"
  status: active
---

# Schematic

Automate and format Wokwi `diagram.json` schematics and generate clean, readable Mermaid circuit diagrams.

## Overview

A schematic must be visually clear and verifiable. In this monorepo, circuits place the microcontroller centrally, inputs on the left, outputs on the right, and route connections along orthogonal Manhattan angles with right-angle bends to prevent overlapping and crossing lines.

## When to Use

- Designing or updating Wokwi `assets/diagram.json` for a homework.
- Resolving cluttered, tangled, or diagonally crossing wires in the Wokwi editor.
- Generating a GitHub-flavored Mermaid flowchart for `README.md` or `report.md`.
- Linting circuit connections offline using `wokwi-cli`.

### When NOT to Use

- For simulating firmware execution (use `simulate`).
- For PlatformIO building or flashing (use `hw-build` or `hw-flash`).

## Quick Reference

| Operation | Command |
|---|---|
| Format diagram & apply Manhattan routing | `uv run scripts/gen_schematic.py homeworks/<id> --format` |
| Generate Mermaid diagram for Markdown | `uv run scripts/gen_schematic.py homeworks/<id> --mermaid` |
| Check diagram formatting status | `uv run scripts/gen_schematic.py homeworks/<id> --check` |
| Lint Wokwi circuit offline (no quota) | `wokwi-cli lint --offline homeworks/<id>/assets/diagram.json` |

## Layout Rules

When arranging components in Wokwi diagrams:

1. **Board Placement**: Position the microcontroller board centrally (e.g. `top: 100`, `left: 50`).
2. **Inputs on Left**: Place pushbuttons and sensors on the left of the board (`left: -140` to `-160`) to avoid crossing output wiring.
3. **Outputs on Right**: Group series resistors and LEDs on the right side with ample vertical spacing (`gap >= 80px`).
4. **Manhattan Routing**: Never leave routing instructions empty (`[]`) for complex connections. Use `["h...", "v..."]` offsets so wires travel along right angles without cutting across components or each other.
5. **Color Standards**:
   - Power (`3.3V` / `5V`): `red`
   - Ground (`GND`): `black`
   - Control / Signals: dedicated distinct colors (`green`, `blue`, `orange`, `purple`).

## Common Mistakes & Red Flags

- **Red Flag**: Empty bend arrays (`[]`) on connections that cross components, producing straight diagonal wires slicing through ICs. Always define Manhattan waypoints (e.g. `["h40", "v80"]`).
- **Red Flag**: Stacking components vertically on top of each other with <50px spacing.
- **Mistake**: Inverting LED anode (`A`) and cathode (`C`), causing reverse bias and unlit LEDs.
- **Mistake**: Committing large binary screenshots of the simulator instead of embedding a Mermaid flowchart in Markdown.

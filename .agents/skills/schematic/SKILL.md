---
name: schematic
description: Automates clean Wokwi diagram layout, wire routing, and generates Mermaid circuit schematics.
metadata:
  version: "1.0"
  status: active
---
<!-- GENERATED — do not edit. Run: uv run scripts/gen_skills.py -->

# Schematic

Automate and format Wokwi `diagram.json` schematics and generate readable Mermaid circuit diagrams.

## Purpose

1. Maintain human-readable, non-tangled wiring in `assets/diagram.json`.
2. Generate embeddable Mermaid flowcharts for `README.md` and `report.md`.
3. Validate circuits using `wokwi-cli lint --offline`.

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

## Tools & Commands

### 1. Format Diagram Layout

Reformat an existing `diagram.json` with clean coordinates and routing:

```sh
uv run scripts/gen_schematic.py homeworks/<id> --format
```

### 2. Generate Mermaid Flowchart

Generate a GitHub-flavored Mermaid snippet to embed directly in Markdown:

```sh
uv run scripts/gen_schematic.py homeworks/<id> --mermaid
```

### 3. Lint the Diagram

Verify syntax and pin validity offline:

```sh
wokwi-cli lint --offline homeworks/<id>/assets/diagram.json
```

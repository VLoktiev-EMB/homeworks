---
name: schematic
description: Use when designing, editing, or formatting Wokwi diagram.json schematics, generating IEEE Schemdraw vector SVGs, creating Mermaid circuit flowcharts for READMEs or reports, or untangling overlapping wiring.
metadata:
  version: "2.0"
  status: active
---

# Schematic & Circuit Visualization

Authoritative engineering standards for the repository's three-tier circuit visualization architecture:
1. **Tier 1: IEEE Vector Electrical Schematics (`assets/schematic.svg`)** via Python `schemdraw`
2. **Tier 2: Interactive Solderless Breadboard Models (`assets/diagram.json`)** for Wokwi simulation
3. **Tier 3: Markdown Block Diagrams (`flowchart LR`)** via GitHub Mermaid

---

## When to Use

- Designing, scaffolding, or updating circuit diagrams for any homework project.
- Generating crisp, publication-grade vector electrical schematics (`assets/schematic.svg`) for reports.
- Formatting and routing breadboard layouts (`assets/diagram.json`) for the Wokwi simulator.
- Generating clean, unidirectional Mermaid block diagrams for `README.md` or `report.md`.
- Resolving cluttered, tangled, diagonally crossing, or dark-mode unreadable schematics.
- Linting Wokwi circuit connections offline without API token quota.

### When NOT to Use

- For running headless firmware simulation scenarios (use `simulate`).
- For PlatformIO building or flashing microcontroller targets (use `hw-build` or `hw-flash`).
- For editing firmware logic or C++ state machines.

---

## Quick Reference

| Operation | Command | Primary Output |
|---|---|---|
| Generate IEEE vector schematic SVG | `uv run scripts/gen_schematic.py homeworks/<id> --svg` | `assets/schematic.svg` |
| Format breadboard & Manhattan routing | `uv run scripts/gen_schematic.py homeworks/<id> --format` | `assets/diagram.json` |
| Generate Mermaid diagram for Markdown | `uv run scripts/gen_schematic.py homeworks/<id> --mermaid` | stdout (Markdown) |
| Complete 3-tier generation | `uv run scripts/gen_schematic.py homeworks/<id> --all` | SVG + JSON + Mermaid |
| Check diagram formatting status | `uv run scripts/gen_schematic.py homeworks/<id> --check` | return code 0/1 |
| Lint Wokwi circuit offline (no token) | `wokwi-cli lint --offline homeworks/<id>/assets/diagram.json` | lint diagnostics |

---

## Tier 1: IEEE Schemdraw Vector Schematics (`schematic.svg`)

Every homework must deliver an IEEE-compliant vector schematic readable a year later. Follow these non-negotiable rules (details in [references/schemdraw-patterns.md](references/schemdraw-patterns.md)):

1. **Mandatory Solid Card Background (Dark Mode Guarantee)**:
   * Schemdraw defaults to transparent background with black lines (`#000000`), making diagrams invisible in dark mode themes.
   * **Rule**: Inject `<rect width="100%" height="100%" fill="#ffffff" rx="8"/>` directly inside the root `<svg>` tag after rendering.
2. **Microcontroller Box Dimensions (`elm.Ic`)**:
   * Always use `size=(width, height)` (e.g. `size=(6.2, 5.5)`). Never use `w=` or `h=` kwargs (they are silently ignored by `elm.Ic`).
   * Allocate a generous slot count (e.g. 7 slots) so pin labels never collide with the center chip label (`loc="center"`).
   * Use `anchorname` when multiple pins share the visual name `GND` (e.g. `anchorname="GND_L"` and `anchorname="GND_R"`).
3. **Label Anchoring on Vertical vs Horizontal Components**:
   * In Schemdraw, for vertical elements (`down` or `up`), `loc="right"` attaches text to the **terminal end** of the element along the line, causing collisions with wires and nodes.
   * **Rule**: Use `loc="bottom"` for vertical elements to place text horizontally to the right of the component, centered vertically.
4. **Collision-Free Stepped Routing**:
   * Stagger multiple output branches: route upper buses vertically with step offsets (`elm.Line().up(0.6).at(...) -> elm.Line().right(...)`) so horizontal wires fly well above lower component branches.
   * Never let horizontal bus lines cut across vertical diodes or resistors.
5. **Switch Wiring Integrity**:
   * Active-LOW pushbuttons must wire in series: GPIO pin -> Switch -> Ground.
   * **Never** attach Ground to `btn.start` (that shorts the GPIO pin to Ground permanently). Attach Ground to `btn.end`.

---

## Tier 2: Interactive Wokwi Breadboard Models (`diagram.json`)

Detailed reference in [references/wokwi-breadboard.md](references/wokwi-breadboard.md):

1. **Breadboard Integration**: Always include `wokwi-breadboard-half` (`bb1`) adjacent to the MCU (`esp`).
2. **No-Chip-Crossing Rule**:
   * Wires emerging from MCU pin headers must **NEVER cut across the face of the microcontroller board, antenna, or RF metal shield**.
   * Use the **overhead conduit pattern**: step left off header pin (`h-20`), go up above the board (`v-40`), travel right across top (`h240`), and drop into breadboard column (`v30`).
3. **Power Bus Rails**:
   * Connect MCU `3V3` and `GND` to breadboard rails once (`bb1:tp.1` and `bb1:tn.1`).
   * All components tap power and ground locally via short vertical jumpers.
4. **Boundary Containment**:
   * All components must remain fully seated within breadboard rows (`a-e` and `f-j`). Never place components hanging off the bottom (keep `top <= 110`).
5. **Orthogonal Manhattan Vectors**:
   * All wire bends must use `["h...", "v..."]` right-angle offsets. Never leave bend arrays empty `[]` when crossing components.
6. **Standard Color Coding**:
   * `red` for 3.3V/5V Power, `black` for GND Ground, distinct dedicated colors for signals (`orange`, `purple`, `green`, `blue`).

---

## Tier 3: Markdown Block Diagrams (Mermaid `flowchart LR`)

Detailed reference in [references/mermaid-block-diagrams.md](references/mermaid-block-diagrams.md):

1. **Strictly Unidirectional Signal Flow**:
   * Always use `flowchart LR` representing functional flow:
     `[Inputs]` ---> `[Controller / MCU]` ---> `[Drivers / Resistors]` ---> `[Outputs / LEDs]`.
2. **The Loopback Trap (Zero Circular Arcs)**:
   * **NEVER** draw Ground returns as backward arrows into the MCU (`led1 -->|C -> GND| esp`).
   * Terminate Ground at dedicated sink nodes: `led1 --> gnd[GND]`.
   * Feed Power from dedicated source nodes: `pwr["3.3V"] --> led2`.
3. **Breadboard Net Abstraction**:
   * Do not render the breadboard (`bb1`) as a physical node in the Mermaid chart. Resolve intermediate row connections directly into component-to-component signal edges (`r1 --> led1`).

---

## Common Mistakes & Red Flags

- **Red Flag (Dark Mode Blindness)**: Committing a Schemdraw SVG without an explicit white card background rectangle `<rect fill="#ffffff"/>`.
- **Red Flag (Chip Slicing)**: Diagonal wires or horizontal jumps cutting across the ESP32 metal shield or antenna in Wokwi diagrams.
- **Red Flag (Tangled Loopbacks)**: Mermaid diagrams with backward curved arrows looping from outputs back into the MCU.
- **Red Flag (Hanging Parts)**: Components placed outside the physical breadboard grid boundary.
- **Mistake**: Using `elm.Ic(w=..., h=...)` instead of `elm.Ic(size=(w, h))`.
- **Mistake**: Using `loc="right"` on vertical diodes, causing labels to collide with terminal wires.
- **Mistake**: Attaching Ground to `btn.start` instead of `btn.end` on Schemdraw buttons.

---

## Verification Checklist

Before completing any homework schematic change, execute this verification sequence:

```sh
# 1. Generate all three tiers
uv run scripts/gen_schematic.py homeworks/<id> --all

# 2. Check diagram drift
uv run scripts/gen_schematic.py homeworks/<id> --check

# 3. Lint Wokwi netlist offline
wokwi-cli lint --offline homeworks/<id>/assets/diagram.json

# 4. Verify vector SVG has solid background
grep -q "<rect.*fill=\"#ffffff\"" homeworks/<id>/assets/schematic.svg && echo "Background card OK"

# 5. Run Python test suite
python3 -m unittest discover scripts/tests -k "schematic"
```

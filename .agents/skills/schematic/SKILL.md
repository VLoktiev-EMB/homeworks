---
name: schematic
description: Use when generating, drawing, validating, or repairing circuit diagrams, canonical IEEE vector schematics (assets/schematic.svg), Wokwi diagram.json layouts, shared-pin or totem-pole wiring, or Mermaid circuit diagrams. Trigger this skill whenever labels overlap, wires look tangled or diagonal, a schematic looks unprofessional, or the user asks for a circuit diagram, wiring diagram, or schematic cleanup.
metadata:
  version: "2.2"
  status: active
---

# Schematic & Circuit Visualization

The repository has three circuit visualization tiers, and one of them is generated
automatically for every circuit:

1. **Tier 1: IEEE vector schematic (`assets/schematic.svg`)** — generated from
   `assets/diagram.json` by `scripts/gen_schematic.py`.
2. **Tier 2: Wokwi circuit model (`assets/diagram.json`)** — the wiring source of truth.
3. **Tier 3: Mermaid block diagram (`flowchart LR`)** — also generated from the diagram.

## The universal rule

**Never write a renderer for one homework.** The generator reads `diagram.json` and chooses
a layout by itself:

- **Branch layout** — every external part is two-terminal, every signal net carries
  exactly one branch, and the graph is a forest rooted at the MCU pins. It draws real
  wires, series components, junctions, ground, and power symbols. A single LED with a
  series resistor is the typical case.
- **Row layout** — every two-terminal chain between two anchor nets (an MCU pin, power,
  or ground) becomes one horizontal row. A shared pin yields one row per branch, and
  matching net labels carry connectivity. Use this whenever a signal net has several
  branches, a branch returns to a rail, or the graph is not a forest. Internal series nets
  are drawn directly and never invented as `N` labels.
- **Net-label layout** — the universal fallback for multi-pin ICs, cyclic or isolated
  nets, and unknown part types. Each pin ends in a labelled stub, and matching labels
  express connectivity. It never fails on a valid diagram.

The dispatcher is automatic. When asked to draw a schematic, add or fix `diagram.json`,
then run the command. Do not inspect which branch or part type is present, and do not
create a new generation script.

## When to Use

- Drawing or regenerating `assets/schematic.svg` for any homework.
- Authoring or repairing `assets/diagram.json` so the Wokwi canvas is readable.
- Generating a Mermaid block diagram for a README or report.
- Checking whether a committed SVG matches its diagram.
- Repairing crossing wires, overlapping labels, clipped labels, or a dark-mode-invisible
  schematic.
- Validating a `diagram.json` before running `wokwi-cli`.

### When NOT to Use

- Running headless simulation scenarios (use `simulate`).
- Building or flashing firmware (use `hw-build` or `hw-flash`).
- Editing firmware logic.

## Quick Reference

| Operation | Command | Output |
|---|---|---|
| Draw the IEEE vector schematic | `uv run scripts/gen_schematic.py homeworks/<id> --svg` | `assets/schematic.svg` |
| Print the Mermaid block diagram | `uv run scripts/gen_schematic.py homeworks/<id> --mermaid` | stdout |
| Draw the SVG and print Mermaid | `uv run scripts/gen_schematic.py homeworks/<id> --all` | SVG + stdout |
| Validate the diagram and detect SVG drift | `uv run scripts/gen_schematic.py homeworks/<id> --check` | exit 0/1 |
| Lint the Wokwi netlist offline | `wokwi-cli lint --offline homeworks/<id>/assets/diagram.json` | diagnostics |

`--check` does two things: it validates referential integrity (unique part ids, every
connection names an existing part) and compares a fresh render with the committed SVG. A
stale SVG fails the check; the fix is `--svg`, never a hand edit.

## Canonical drawing rules

These rules come from the standard schematic conventions summarized in the Sources
section. They are style rules with a practical purpose: a reader follows a signal without
reconstructing the topology from tangled wires.

1. **Flow and rails.** Main signals flow left to right and top to bottom. Put the positive
   rail at the top, ground at the bottom, and keep that orientation for every branch.
2. **One grid, aligned parts.** Place the MCU once and align series parts on a common
   horizontal or vertical line. A component that is off-grid is what makes a drawing look
   "floating".
3. **Orthogonal wires.** Every bend is a right angle. Never route diagonally across the
   MCU face, the antenna, a button, or another component.
4. **Junctions.** A filled dot marks a connection. Draw a dot only where three wires meet;
   a four-way dot is ambiguous. A crossing without a dot is not a connection.
5. **Pin exits.** Leave a pin straight for at least one grid step before turning, so the
   pin name and the first wire are readable.
6. **Labels.** Label horizontal components above the body and vertical components beside
   it. Keep labels on their own row and never let two labels occupy the same space.
7. **Shared nets.** When one pin drives several branches, repeat the pin's net label on
   each branch instead of forcing all branches through one wire. This is the row layout,
   and it is the canonical answer to a shared-pin fork.
8. **No invented nets.** A series node between a resistor and an LED is drawn as a direct
   connection. Giving it a synthetic `N5` label hides the series relationship.
9. **Polarity.** An LED or diode points in the direction of conventional current: anode
   toward the source, cathode toward the sink. Rotate or flip the symbol, not the wires,
   when the reading direction is wrong.
10. **Board side and return locality.** Put left-header signals on the left wing and
    right-header signals on the right wing; route a rail feed to the opposite side over the
    top or bottom perimeter, never across the board face. Use the nearest board ground pin
    for a nearby return and one ground symbol for a far wing — both are the same net, but
    the drawing avoids a long loop.

## Tier 1: the generated SVG

The renderer applies these rules; they matter when you edit `scripts/schematic_svg.py` or
hand-author an SVG (details in [references/schemdraw-patterns.md](references/schemdraw-patterns.md)):

1. **Solid card background.** Schemdraw's transparent background makes black lines vanish
   in a dark theme. The renderer injects a white `<rect>` and widens the viewBox so
   terminal labels are never clipped at the right edge.
2. **Layout selection.** Try the branch layout first, then the row layout when the branch
   layout refuses a shared or non-forest net, then the universal net-label layout.
3. **MCU box.** `elm.Ic(size=(width, height))`, never `w=`/`h=`. The renderer sizes the box
   from the pin count and places it before the chains, because an IC inherits the current
   drawing direction.
4. **Row layout labels.** Every chain starts and ends with a power symbol, a ground symbol,
   or a net label. The MCU block repeats the same net labels. Internal nodes never get a
   synthetic `N` label.
5. **Labels and polarity.** Horizontal elements label above. A chain drawn right-to-left
   must reverse the LED so its anode still faces the source. The renderer derives the
   direction from the component's `A`/`C` pins.

## Tier 2: authoring `diagram.json`

The diagram is the wiring source of truth. The generator never rewrites its geometry;
author it by hand (details in [references/wokwi-breadboard.md](references/wokwi-breadboard.md)):

1. **Direct wiring is the default for discrete circuits.** Do not add an empty
   `wokwi-breadboard-half`; an unused breadboard is visual noise with floating parts.
   Anchor the board at `(top: 0, left: 0)`.
2. **One row per branch.** Put each LED and its series resistor on its own horizontal row,
   spaced at least 40–60 px from its neighbour. Align the row with the controlling pin when
   possible, and use a short vertical jog when the pin is not on that row.
3. **Shared pin means a totem pole.** For a pin that sources one branch and sinks another,
   draw the source branch above the pin (3V3 → resistor → LED → pin) and the sink branch
   below it (pin → resistor → LED → ground). The pin is the middle of the stack, and the
   current direction reads top to bottom. Do not place both branches on one row.
4. **Rotate the LED, not the wire.** A horizontal branch uses `"rotate": 90` or `270` so the
   anode and cathode land left and right. Verify the A/C direction in the editor; a `flip`
   attribute or a 180° change fixes a reversed symbol.
5. **Ground and power buses.** Join the LED cathodes with one vertical ground bus and take
   that bus to the board GND pin. Feed a sink branch from the board 3V3 pin. Avoid several
   long independent ground wires that overlap each other.
6. **Orthogonal wiring.** Wire bends use right-angle vectors (`["h...", "v..."]`). Never
   route diagonally across the MCU face, antenna, or button faces.
7. **Two-colour palette.** Draw every active/source path in `red` and every
   ground or sink return in `black`. Add a third colour only when a
   multi-signal bus needs discrimination; a simple LED circuit needs no
   rainbow.
8. **Breadboard only when needed.** Use one for multi-pin DIP ICs or dense bus topologies,
   and seat every component in a tie strip.

Pin names are part of the contract: the renderer derives MCU labels from them, and the
report's pin map must agree with the diagram.

## Tier 3: Mermaid

The Mermaid text is generated from the diagram, so the source of truth stays single
(details in [references/mermaid-block-diagrams.md](references/mermaid-block-diagrams.md)):

1. **Unidirectional flow.** `flowchart LR`: inputs → controller → drivers → outputs.
2. **No loopbacks.** Ground is a sink (`led1 --> gnd[GND]`), power is a source
   (`pwr["3.3V"] --> led2`); never draw a backward arrow into the MCU. A sink branch such
   as a blue LED returned to a GPIO is written controller-first in `diagram.json`
   (`["esp:4", "led_blue:C"]`) so the block diagram reads MCU → LED even though current
   enters the pin.
3. **No breadboard node.** Resolve rows into direct component-to-component edges.

## Common Mistakes & Red Flags

- **Red flag (shared-pin fork).** Two branches leaving one pin at nearly the same offset;
  the labels collide and the wires cross. This is the branch layout being asked to do a
  row layout's job.
- **Red flag (internal `N` labels).** A series resistor–LED node labelled `N5` in a
  discrete circuit; the reader has to reconstruct a chain that could have been drawn.
- **Red flag (per-homework renderer).** A new function, pin constant, or part name inside
  `scripts/gen_schematic.py` or `scripts/schematic_svg.py`. Add a diagram test instead.
- **Red flag (dark mode blindness).** A committed SVG without the white card `<rect>`.
- **Red flag (clipped labels).** A label running past the right edge; the viewBox padding
  in `_with_card_background` should have prevented it.
- **Red flag (diagonal wires).** A wire cutting across the board or another part; use a
  right-angle vector.
- **Mistake.** Treating the row or net-label layout as an error. Both are intended; only
  overlapping labels and crossings are defects.
- **Mistake.** Rotating an LED without checking which pin is `A` and which is `C`; the
  symbol can end up reverse-biased in simulation.

## Verification Checklist

```sh
# 1. Draw the SVG and print Mermaid
uv run scripts/gen_schematic.py homeworks/<id> --all

# 2. Validate the diagram and prove the committed SVG is not stale
uv run scripts/gen_schematic.py homeworks/<id> --check

# 3. Lint the Wokwi netlist offline
wokwi-cli lint --offline homeworks/<id>/assets/diagram.json

# 4. Confirm the dark-mode background card
grep -q '<rect.*fill="#ffffff"' homeworks/<id>/assets/schematic.svg && echo "Background card OK"

# 5. Run the renderer tests with Schemdraw available, so the SVG cases do not skip
uv run --with schemdraw==0.23 python -m unittest scripts.tests.test_gen_schematic -v
```

Then open `assets/schematic.svg` and check by eye: power at the top, ground at the bottom,
one row per branch, no two labels touching, and no internal `N` labels in a discrete
circuit. Open `diagram.json` in the Wokwi editor and check the same for the breadboard view.

### Visual acceptance checklist

A schematic is finished only when the canvas passes this list:

- The board is on one side, power at the top, ground at the bottom.
- Each branch has its own row; LEDs are vertical with horizontal labels.
- Resistors are horizontal and consistently oriented; a flipped band pattern is
  cosmetic, not a different circuit.
- Red marks every active/source path; black marks ground and sink returns.
- One `wokwi-gnd` symbol serves the returns; there is no long ground loop.
- No wire crosses a component, a label, or another wire.
- No wire runs diagonally across the board face.

When a diagram is malformed, `--check` names the offending part or terminal. Fix the
diagram, not the renderer. A new circuit is a new `diagram.json`, never a new code path.

## Sources

- IEEE 315 / ANSI Y32.2 symbol conventions, as summarized by the schematic guidelines in
  the references below.
- [Altium, "Easy Schematics Creation for Elegance and Readability"](https://resources.altium.com/p/creating-elegant-and-readable-schematics).
- [Circuit Cellar, "Drawing Schematics"](https://circuitcellar.com/resources/quickbits/drawing-schematics/).
- [Wokwi, "diagram.json File Format"](https://docs.wokwi.com/diagram-format) and
  [wokwi-led reference](https://docs.wokwi.com/parts/wokwi-led).

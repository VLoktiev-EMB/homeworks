---
name: schematic
description: Use when asked to draw, generate, or fix a circuit diagram or schematic for ANY homework — including an arbitrary Wokwi diagram.json, multi-pin ICs, sensors, or a topology never seen before. Renders IEEE vector SVGs and Mermaid flowcharts directly from the diagram, so "draw the schematic" needs no per-homework code. Also use when checking schematic drift, untangling crossing wires, or making a diagram readable in dark mode.
metadata:
  version: "2.1"
  status: active
---
<!-- GENERATED — do not edit. Run: uv run scripts/gen_skills.py -->

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

- **Branch layout** — used when every external part has exactly two terminals and the net
  graph is a forest rooted at the MCU pins. It draws real wires: series components,
  junctions, ground, and power symbols. An LED with a series resistor is the typical case.
- **Net-label layout** — the fallback for everything else: multi-pin ICs, cyclic nets,
  isolated parts, unknown part types. Each pin ends in a short stub labelled with its net
  name, and matching labels express the connectivity. This is a standard schematic
  technique and it never fails on a valid diagram.

The dispatcher is automatic. When asked to draw a schematic, add or fix `diagram.json`,
then run the command. Do not inspect which branch or part type is present, and do not
create a new generation script.

## When to Use

- Drawing or regenerating `assets/schematic.svg` for any homework.
- Generating a Mermaid block diagram for a README or report.
- Checking whether a committed SVG matches its diagram.
- Repairing crossing wires, clipped labels, or a dark-mode-invisible schematic.
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

## Tier 1: the generated SVG

The renderer applies these rules; they matter when you edit `scripts/schematic_svg.py` or
hand-author an SVG (details in [references/schemdraw-patterns.md](references/schemdraw-patterns.md)):

1. **Solid card background.** Schemdraw's transparent background makes black lines vanish
   in a dark theme. The renderer injects a white `<rect>` and widens the viewBox so
   terminal labels are never clipped at the right edge.
2. **MCU box.** `elm.Ic(size=(width, height))`, never `w=`/`h=`. The renderer sizes the box
   from the pin count, with a generous pitch so a junction can turn upward without hitting
   the next pin row.
3. **Labels.** Horizontal elements label above; vertical elements label with `loc="bottom"`
   beside the body. `loc="right"` on a vertical element collides with the terminal wire.
4. **Lane routing.** Each signal branch gets a vertical lane, and upper branches take the
   outer lane, so a branch's vertical drop runs beyond every lower branch's horizontal
   run. That is what prevents crossings without a mesh router.
5. **Polarity.** An `elm.LED()` drawn upward is reversed (`elm.LED().up().reverse()`) so a
   branch that returns to 3V3 has its anode at the rail. The branch layout applies this
   automatically from the part type and the net kind.

## Tier 2: authoring `diagram.json`

The diagram is the wiring source of truth. The generator never rewrites its geometry;
author it by hand (details in [references/wokwi-breadboard.md](references/wokwi-breadboard.md)):

1. **Direct wiring is the default for discrete circuits.** Do not add an empty
   `wokwi-breadboard-half`; an unused breadboard is visual noise with floating parts.
   Anchor the board at `(top: 0, left: 0)` and place each branch beside its GPIO pin.
2. **Use a breadboard only when the circuit genuinely needs one** — multi-pin DIP ICs or
   dense bus topologies. Then components must plug into tie strips, not float.
3. **Orthogonal wiring.** Wire bends use right-angle vectors (`["h...", "v..."]`). Never
   route diagonally across the MCU face, antenna, or button faces.
4. **Color code.** `red` for power, `black` for ground, and distinct colors for signals.

Pin names are part of the contract: the renderer derives MCU labels from them, and the
report's pin map must agree with the diagram.

## Tier 3: Mermaid

The Mermaid text is generated from the diagram, so the source of truth stays single
(details in [references/mermaid-block-diagrams.md](references/mermaid-block-diagrams.md)):

1. **Unidirectional flow.** `flowchart LR`: inputs → controller → drivers → outputs.
2. **No loopbacks.** Ground is a sink (`led1 --> gnd[GND]`), power is a source
   (`pwr["3.3V"] --> led2`); never draw a backward arrow into the MCU.
3. **No breadboard node.** Resolve rows into direct component-to-component edges.

## Common Mistakes & Red Flags

- **Red Flag (per-homework renderer).** A new function, pin constant, or part name inside
  `scripts/gen_schematic.py` or `scripts/schematic_svg.py`. Add a diagram test instead.
- **Red Flag (dark mode blindness).** A committed SVG without the white card `<rect>`.
- **Red Flag (clipped labels).** A label running past the right edge; the viewBox padding
  in `_with_card_background` should have prevented it.
- **Red Flag (crossing wires).** A branch drop crossing another branch's horizontal run;
  the lane ordering by pin height is what avoids it.
- **Mistake.** Running the retired `--format` flag; it no longer exists. Edit the
  diagram geometry deliberately or leave it as authored.
- **Mistake.** Treating the net-label fallback as an error. It is the intended layout for
  multi-pin parts and cyclic nets.

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

# 5. Run the renderer tests
python3 -m unittest discover scripts/tests -k "schematic"
```

When a diagram is malformed, `--check` names the offending part or terminal. Fix the
diagram, not the renderer. A new circuit is a new `diagram.json`, never a new code path.

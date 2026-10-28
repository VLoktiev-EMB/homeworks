# Schemdraw Vector Schematic Patterns

Complete reference for generating production-grade, IEEE-compliant vector electrical schematics (`assets/schematic.svg`) using the `schemdraw` Python library.

## 1. Dark Mode & High Contrast Guarantee

By default, `schemdraw` produces SVGs with transparent backgrounds and `#000000` (black) strokes and text. When viewed in GitHub dark mode or dark-themed IDEs, this renders the schematic completely invisible ("black-on-black").

### Mandatory Solid Card Pattern
Every generated schematic SVG must inject an explicit high-contrast white card background rectangle:

```python
import re
import schemdraw

with schemdraw.Drawing(show=False) as d:
    d.config(unit=2.0, fontsize=10, margin=1.5, bgcolor="white")
    # ... add elements ...
    svg_content = d.get_imagedata("svg").decode("utf-8")

# Inject solid white background rectangle for high contrast across dark and light modes
viewbox_match = re.search(r'viewBox="([^"]+)"', svg_content)
if viewbox_match:
    parts = viewbox_match.group(1).split()
    vx, vy, vw, vh = parts
    rect = f'<rect x="{vx}" y="{vy}" width="{vw}" height="{vh}" fill="#ffffff" rx="8"/>'
    svg_content = re.sub(r"(<svg[^>]*>)", r"\1" + rect, svg_content, count=1)

if not svg_content.endswith("\n"):
    svg_content += "\n"
output_path.write_text(svg_content, encoding="utf-8")
```

---

## 2. Microcontroller Block (`elm.Ic`)

### Common Pitfalls
1. **Ignored Dimensions**: `elm.Ic(w=3.5, h=4.5)` silently ignores `w` and `h` kwargs. The correct parameter is `size=(width, height)`.
2. **Crowded Pin Slots**: Using `slot="4/4"` places the top pin directly on the corner border of the IC, cutting pin text in half.
3. **Overlapping Center Label**: Small widths cause `elm.IcPin(name=...)` text from the left and right sides to collide directly with `.label("MCU Name", loc="center")`.

### Correct Pattern
```python
import schemdraw.elements as elm

ic = d.add(
    elm.Ic(
        size=(6.2, 5.5),  # Generous width and height
        pins=[
            # Left side inputs (use generous total slot denominator, e.g. 7)
            elm.IcPin(name="GPIO7", side="left", slot="4/7"),
            elm.IcPin(name="GND", anchorname="GND_L", side="left", slot="1/7"),
            # Right side outputs and rails
            elm.IcPin(name="GPIO4", side="right", slot="6/7"),
            elm.IcPin(name="GPIO6", side="right", slot="4/7"),
            elm.IcPin(name="3V3", side="right", slot="2/7"),
            elm.IcPin(name="GND", anchorname="GND_R", side="right", slot="1/7"),
        ],
    ).label("ESP32-S3\nDevKitC-1", loc="center", fontsize=11)
)
```

> [!TIP]
> Use `anchorname` when multiple pins share the same visual name (e.g. `GND`). This keeps both labeled as `GND` in the drawing while allowing distinct program access via `ic.GND_L` and `ic.GND_R`.

---

## 3. Label Anchoring for Two-Terminal Elements

In `schemdraw`, two-terminal elements (`Line`, `Resistor`, `LED`, `Capacitor`) define `loc` relative to the **direction of element travel**:

| Direction | Desired Visual Position | Correct `loc` | Wrong `loc` (Causes Bug) |
|---|---|---|---|
| Horizontal `right()` | Above element | `loc="top"` | `loc="up"` |
| Horizontal `right()` | Below element | `loc="bottom"` | `loc="down"` |
| Vertical `down()` | To the visual right | `loc="bottom"` | `loc="right"` (places text at the *end terminal*) |
| Vertical `down()` | To the visual left | `loc="top"` | `loc="left"` (places text at the *start terminal*) |
| Vertical `up()` | To the visual right | `loc="bottom"` | `loc="right"` (places text at the *top terminal*) |
| Vertical `up()` | To the visual left | `loc="top"` | `loc="left"` (places text at the *bottom terminal*) |

### Critical LED Example
```python
# LED dropping vertically to GND with text on the visual right:
d.add(elm.LED().down(1.5).label("LED1 (RED)\n[GPIO4=HIGH]", loc="bottom", ofst=0.2))

# Reversed LED rising vertically to 3.3V with text on the visual right:
d.add(elm.LED().up(1.5).reverse().label("LED2 (RED)\n[GPIO4=LOW]", loc="bottom", ofst=0.2))
```

---

## 4. Manhattan Branch Separation (Collision-Free Routing)

When an IC drives multiple parallel outputs on the same side, horizontal buses must never cut across vertical component paths.

### Technique: Stepped Overhead Routing
If `GPIO4` is above `GPIO6`, route `GPIO4`'s bus higher and further to the right:

```
[GPIO4] --+ (up 0.6)
          +---------------------------------------------> [ R1 ] ---> [Node X] ---> (LED1 / LED2)
[GPIO6] ----------------------------> [ R2 ] ---> [LED3] ---> GND
[ 3V3 ] --------> 3.3V
[ GND ] --------> GND
```

```python
# Lower branch (GPIO6 -> R2 -> LED3) stays close:
d.add(elm.Line().right(2.0).at(ic.GPIO6))
d.add(elm.Resistor().right(1.5).label("R2\n150Ω", loc="top"))
d.add(elm.Line().right(0.5))
d.add(elm.LED().down(1.5).label("LED3 (RED)\n[STATUS]", loc="bottom", ofst=0.2))
d.add(elm.Ground())

# Upper branch (GPIO4 -> R1 -> LEDs) steps up and flies overhead:
d.add(elm.Line().up(0.6).at(ic.GPIO4))
d.add(elm.Line().right(7.2))  # Extends well past LED3
d.add(elm.Resistor().right(1.5).label("R1\n150Ω", loc="top"))
d.add(elm.Line().right(0.5))
node_x = d.add(elm.Dot())

# Branch 1A: Down to GND
d.add(elm.Line().down(1.0).at(node_x.center))
d.add(elm.LED().down(1.5).label("LED1 (RED)\n[GPIO4=HIGH]", loc="bottom", ofst=0.2))
d.add(elm.Ground())

# Branch 1B: Up to 3.3V
d.add(elm.Line().up(1.0).at(node_x.center))
d.add(elm.LED().up(1.5).reverse().label("LED2 (RED)\n[GPIO4=LOW]", loc="bottom", ofst=0.2))
d.add(elm.Vdd().label("3.3V", loc="top"))
```

---

## 5. Switch & Button Sanity

Active-LOW pushbuttons with internal pull-up must be wired strictly in series between the GPIO pin and Ground:

```python
# CORRECT:
d.add(elm.Line().left(1.2).at(ic.GPIO7))
btn = d.add(elm.Button(up=True).left(1.5).label("MODE\n(SW1)", loc="top"))
d.add(elm.Line().down(1.0).at(btn.end))  # Attach GND to btn.end
d.add(elm.Ground())

# NEVER attach GND to btn.start — that permanently grounds the GPIO pin!
```

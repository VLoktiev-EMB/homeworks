# Wokwi Wiring Architectures & Routing Reference

Guidelines and standards for creating clean, realistic, and offline-verifiable circuit models (`assets/diagram.json`) in the Wokwi simulator.

---

## 1. Choosing the Circuit Architecture

Wokwi circuit diagrams fall into two primary design patterns. Choosing the wrong pattern leads to visual clutter, unphysical floating components, or tangled wires.

```
                      +-----------------------------+
                      | What components are needed? |
                      +--------------+--------------+
                                     |
              +----------------------+----------------------+
              |                                             |
   Discrete components only                      Multi-pin DIP ICs or
(LEDs, resistors, buttons, sensors:           dense multi-rail bus wiring
        2-6 parts)                                 (e.g. 74HC595)
              |                                             |
              v                                             v
     +-----------------+                           +-----------------+
     |    Pattern A    |                           |    Pattern B    |
     |  Board-Centric  |                           |   Solderless    |
     |  Direct Wiring  |                           |   Breadboard    |
     +-----------------+                           +-----------------+
     • No fake breadboard                          • Genuine tie-strip seating
     • Symmetrical pin-aligned wings               • Real power bus distribution
     • Short inline connections                    • Overhead conduit routing
```

---

## 2. Pattern A: Board-Centric Direct Wiring (Standard & Preferred)

Use this pattern for all discrete microcontroller circuits where components connect directly to board headers.

### Core Principles
1. **No Fake Breadboard**: Never place a `wokwi-breadboard-half` just for show. If parts aren't plugged into breadboard tie rows, an empty breadboard adds visual noise and forces wires into awkward long overhead detours.
2. **Pin-Aligned Wing Placement**:
   * Anchor the microcontroller board (`esp`) at origin `(top: 0, left: 0)`.
   * Group output branches (resistors, LEDs) in line with their respective GPIO pins (e.g. left side for pins 4, 6, 3V3, GND).
   * Group input devices (pushbuttons) on the same side or opposite side aligned with their pin.
3. **Inline Component Alignment**:
   * Align each resistor horizontally with its driving header pin (`top` aligned with pin row).
   * Seat the associated LED directly adjacent to its resistor with direct inline connection (`[]`).
4. **Perimeter Ground Return**:
   * Ground return wires route along the outer perimeter down to the bottom GND header pin or up to the top GND header pin.
   * Use strictly orthogonal Manhattan bends (`["v...", "h..."]`).
   * **Never cut across the MCU board body, antenna, buttons, or other components**.

### Golden Reference Example (Police Flasher, HW 1.3)
```json
{
  "version": 1,
  "author": "VLoktiev-EMB",
  "editor": "wokwi",
  "parts": [
    {
      "type": "board-esp32-s3-devkitc-1",
      "id": "esp",
      "top": 0,
      "left": 0,
      "attrs": { "flashSize": "16", "psramType": "octal", "psramSize": "8" }
    },
    { "type": "wokwi-resistor", "id": "r1", "top": 76.8, "left": -88.8, "attrs": { "value": "150" } },
    { "type": "wokwi-led", "id": "led1", "top": 40.8, "left": -140, "attrs": { "color": "red", "label": "LED1" } },
    { "type": "wokwi-led", "id": "led2", "top": -16.8, "left": -140, "attrs": { "color": "red", "label": "LED2" } },
    { "type": "wokwi-resistor", "id": "r2", "top": 119.3, "left": -88.8, "attrs": { "value": "150" } },
    { "type": "wokwi-led", "id": "led3", "top": 83.3, "left": -140, "attrs": { "color": "red", "label": "LED3" } },
    { "type": "wokwi-pushbutton", "id": "btn1", "top": 155, "left": -100, "attrs": { "color": "green", "label": "MODE" } }
  ],
  "connections": [
    ["esp:TX", "$serialMonitor:RX", "", []],
    ["esp:RX", "$serialMonitor:TX", "", []],
    ["btn1:1.l", "esp:7", "green", ["h20"]],
    ["btn1:2.l", "esp:GND.1", "black", ["v80", "h90"]],
    ["esp:4", "r1:2", "orange", []],
    ["r1:1", "led1:A", "blue", []],
    ["r1:1", "led2:C", "blue", ["v-38", "h-20"]],
    ["esp:3V3.1", "led2:A", "red", ["h-40", "v-15"]],
    ["led1:C", "esp:GND.1", "black", ["v200", "h120"]],
    ["esp:6", "r2:2", "purple", []],
    ["r2:1", "led3:A", "purple", []],
    ["led3:C", "esp:GND.1", "black", ["v160", "h120"]]
  ]
}
```

### Canonical layout checklist

Before placing a part, fix the reading direction:

- Power at the top, ground at the bottom, signal flow left to right.
- One row per branch; align the resistor with its driving pin.
- Right-angle wire vectors only; leave a pin straight before the first bend.
- A junction dot marks a connection; a crossing without a dot is not one.
- Component labels live above their own row and never share space with the next row.
- A series resistor–LED node is drawn as a direct connection, not a named net.
- Split the wings by board side: left-header signals on the left, right-header
  signals on the right; a rail feed to the opposite side goes over the top or
  bottom perimeter.
- Use the nearest ground return for each wing; one electrical net does not
  require one long wire.

### Pattern A2: Shared-Pin Totem Pole (One Pin, Two Branches)

Use this pattern when one GPIO sources one branch and sinks another, for example
a red and a blue LED on one push-pull pin. The pin is the middle of a vertical
stack:

- Above the pin: 3V3 -> resistor -> LED (anode toward 3V3) -> pin.
- Below the pin: pin -> resistor -> LED (anode toward the pin) -> ground.
- Every other signal keeps its own row below the stack.

Rules:

1. Give each branch its own row and at least 40–60 px of vertical separation.
2. Keep the LED in its default vertical orientation so its `label` stays
   horizontal, and let the resistor sit on the horizontal row beside it. A
   90°/270° rotation also turns the label on its side; rotate only an unlabeled
   LED, or replace the label with a `wokwi-text` part. Resistors are
   non-polar; leave them in the default orientation.
3. Use one `wokwi-gnd` symbol beside the LEDs and connect every cathode to
   `gnd1:GND`. The symbol is the global 0 V reference, so the long return loop
   to the board GND pin is unnecessary. Default LEDs have `A` at the top and
   `C` at the bottom; that orientation matches a downward current path.
4. Feed the sink branch from the board `3V3` pin; do not invent a second supply.
5. Use exactly two wire colours: **red** for the active/source path and
   **black** for a ground or sink return. The blue sink return is black even
   though it ends at GPIO4, because it is a return path; the red source path
   ends at the LED anode. Do not rainbow-code a simple LED circuit.
6. Route every wire with right-angle vectors and never across the board face.
   Give the sink return its own outside lane so it cannot cross the red
   source branches.

Example for the shared-GPIO4 police flasher:

```json
{
  "version": 1,
  "author": "VLoktiev-EMB",
  "editor": "wokwi",
  "parts": [
    {
      "type": "board-esp32-s3-devkitc-1",
      "id": "esp",
      "top": 0,
      "left": 0,
      "attrs": { "flashSize": "16", "psramType": "octal", "psramSize": "8" }
    },
    {
      "type": "wokwi-resistor",
      "id": "r_blue",
      "top": 23.45,
      "left": -97.4,
      "attrs": { "value": "100" }
    },
    {
      "type": "wokwi-led",
      "id": "led_blue",
      "top": -13.2,
      "left": -207.4,
      "attrs": { "color": "blue", "label": "BLUE" }
    },
    {
      "type": "wokwi-resistor",
      "id": "r_red",
      "top": 80.75,
      "left": -96,
      "attrs": { "value": "220" }
    },
    {
      "type": "wokwi-led",
      "id": "led_red",
      "top": 73.2,
      "left": -207.4,
      "attrs": { "color": "red", "label": "RED" }
    },
    {
      "type": "wokwi-resistor",
      "id": "r_white",
      "top": 109.55,
      "left": -96,
      "attrs": { "value": "100" }
    },
    {
      "type": "wokwi-led",
      "id": "led_white",
      "top": 140.4,
      "left": -207.4,
      "attrs": { "color": "white", "label": "WHITE" }
    },
    { "type": "wokwi-gnd", "id": "gnd1", "top": 200, "left": -260, "attrs": {} }
  ],
  "connections": [
    [ "esp:TX", "$serialMonitor:RX", "", [] ],
    [ "esp:RX", "$serialMonitor:TX", "", [] ],
    [ "esp:4", "led_blue:C", "black", [ "h-225.88", "v-28.98" ] ],
    [ "esp:4", "r_red:2", "red", [] ],
    [ "r_red:1", "led_red:A", "red", [ "h-57.6", "v28.8" ] ],
    [ "led_red:C", "gnd1:GND", "black", [ "h-57.2", "v84.8" ] ],
    [ "led_white:C", "gnd1:GND", "black", [ "h-57.2", "v17.6" ] ],
    [ "esp:5", "r_white:2", "red", [ "h-24.28", "v42", "v36.27" ] ],
    [ "r_white:1", "led_white:A", "red", [ "h-38.4", "v67.2" ] ],
    [ "led_blue:A", "r_blue:1", "red", [ "v0" ] ],
    [ "r_blue:2", "esp:3V3.1", "red", [ "v0" ] ]
  ],
  "dependencies": {}
}
```

The same topology in the SVG renderer becomes three rows: `3V3 -> r_blue ->
led_blue -> GPIO4`, `GPIO4 -> r_red -> led_red -> GND`, and `GPIO5 -> r_white ->
led_white -> GND`. The shared `GPIO4` label appears on both rows and on the MCU
pin; no internal net name is invented.

### Pattern A3: Split Wings with Right-Side Controls and a Shared Boot Node

Use this pattern when the board pinout separates outputs and inputs: the LED
branches sit on the left header (GPIO15/16 here), while the buttons sit on the
right header (GPIO0/21). The aim is one reading direction per side, a short
signal wire per control, and no wire across the board face.

Golden example (homework 1.4):

```json
{
  "version": 1,
  "author": "VLoktiev-EMB",
  "editor": "wokwi",
  "parts": [
    {
      "type": "board-esp32-s3-devkitc-1",
      "id": "esp",
      "top": 0,
      "left": 0,
      "attrs": { "flashSize": "16", "psramType": "octal", "psramSize": "8" }
    },
    {
      "type": "wokwi-resistor",
      "id": "r_a",
      "top": 25.45,
      "left": -97.4,
      "attrs": { "value": "220" }
    },
    {
      "type": "wokwi-led",
      "id": "led_a",
      "top": -11.35,
      "left": -207.4,
      "attrs": { "color": "red", "label": "LED A" }
    },
    {
      "type": "wokwi-resistor",
      "id": "r_b",
      "top": 67.95,
      "left": -97.4,
      "attrs": { "value": "220" }
    },
    {
      "type": "wokwi-led",
      "id": "led_b",
      "top": 31.15,
      "left": -207.4,
      "attrs": { "color": "red", "label": "LED B" }
    },
    {
      "type": "wokwi-pushbutton",
      "id": "btn_ext",
      "top": 179,
      "left": 268.8,
      "attrs": { "color": "green", "label": "MODE" }
    },
    {
      "type": "wokwi-pushbutton",
      "id": "btn_boot",
      "top": 140.6,
      "left": 182.4,
      "attrs": { "color": "blue", "label": "BOOT (onboard)" }
    },
    {
      "type": "wokwi-resistor",
      "id": "r_boot_onboard",
      "top": -5.35,
      "left": 113.8,
      "attrs": { "value": "10k" }
    },
    { "type": "wokwi-gnd", "id": "gnd1", "top": 230.4, "left": -250.2, "attrs": {} }
  ],
  "connections": [
    [ "esp:TX", "$serialMonitor:RX", "", [] ],
    [ "esp:RX", "$serialMonitor:TX", "", [] ],
    [ "esp:15", "r_a:2", "red", [] ],
    [ "r_a:1", "led_a:A", "red", [] ],
    [ "led_a:C", "gnd1:GND", "black", [ "h-47.6", "v199.75" ] ],
    [ "esp:16", "r_b:2", "red", [] ],
    [ "r_b:1", "led_b:A", "red", [] ],
    [ "led_b:C", "gnd1:GND", "black", [ "h-47.6", "v157.25" ] ],
    [ "esp:21", "btn_ext:1.l", "green", [ "h20" ] ],
    [ "esp:0", "btn_boot:1.l", "green", [ "h20" ] ],
    [ "btn_boot:2.l", "esp:GND.4", "black", [ "h-19.2", "v57.8" ] ],
    [ "btn_ext:2.l", "esp:GND.4", "black", [ "h-105.6", "v0.2" ] ],
    [ "esp:3V3.1", "r_boot_onboard:1", "red", [ "v0" ] ],
    [ "r_boot_onboard:2", "btn_boot:1.l", "red", [ "v-0.3", "h9.8" ] ]
  ],
  "dependencies": {}
}
```

Why it reads well:

- The left wing contains only the two output chains, so a reader follows
  `GPIO -> resistor -> LED -> ground` twice without crossing a control wire.
- Each button sits on the same horizontal row as its GPIO pin. The green signal
  wire is one short segment, and the label stays above its own row.
- The 10 kOhm pull-up is fed from the left-side `3V3.1` pin but placed above the
  board. Its red path goes up, over the top perimeter, and down to the BOOT
  node; it never crosses the antenna, the RGB LED, or the USB connectors.
- The near returns use the board's own `GND.4` pin. The far LED cathodes use
  one `wokwi-gnd` symbol. Both are the same electrical net, but each wing gets
  the shortest return instead of a long loop from one end of the board to the
  other.
- `esp:0` and the pull-up both land on `btn_boot:1.l`, so the BOOT node is the
  button's left pin. No synthetic `N` net is invented.
- The label `BOOT (onboard)` and the id `r_boot_onboard` state that the Wokwi
  model is a simulation equivalent of the DevKitC-1 hardware, not an extra
  physical part.

Reusable rules:

1. Split the wings by board side. A left-header signal belongs on the left; a
   right-header signal belongs on the right. A part that crosses the board
   face is a layout defect, even when the netlist is correct.
2. Align a control with its GPIO row. Place the button at the same `top` as the
   pin and give the signal wire one short horizontal vector (`h20` here).
3. Route a rail feed to the opposite side over the perimeter. A left-side
   `3V3` feed to a right-side node goes up and across the top, then down; it
   never cuts across the module, antenna, or connectors.
4. Prefer the nearest return. Use a nearby board `GND` pin for a near wing and
   one `wokwi-gnd` symbol for a far wing. The two are the same net; the rule is
   about drawing economy, not two grounds.
5. Keep the shared node explicit. A pull-up and a GPIO that meet on a button
   pin share that pin; do not invent an intermediate net label.
6. Mark simulation equivalents. Use the `(onboard)` label and an `_onboard` id
   when the diagram models a board feature that Wokwi does not provide.

---

## 3. Pattern B: Solderless Breadboard Wiring (Multi-Pin Chips)

Use this pattern when a solderless breadboard is genuinely needed to host multi-pin DIP ICs (e.g. 74HC595 shift register, multiplexer) or breakout boards.

### Grid and Coordinate Placement
* Half-size breadboard: `type: "wokwi-breadboard-half"`, placed adjacent to MCU at `(top: -30, left: 180)`.
* Every component pin must genuinely seat into a designated column tie strip:
  * Top section rows: `bb1:1t.a` through `bb1:30t.e`
  * Bottom section rows: `bb1:1b.f` through `bb1:30b.j`
  * Positive power bus: `bb1:tp.1` through `bb1:tp.30`
  * Negative ground bus: `bb1:tn.1` through `bb1:tn.30`

### No-Chip-Crossing Wire Routing
When routing from the left MCU header to the breadboard on the right:
1. Step **left** off the pin by 15–30 px (`h-20`).
2. Travel **up** above the top edge and antenna of the board (`v-40`).
3. Travel **right** across the top in a clean horizontal conduit (`h240`).
4. Drop **down** into the breadboard target column (`v30`).

---

## 4. Standard Wire Color Palette

A simple LED circuit uses two colours, not six. The reader should see the
current path at a glance.

| Wire Function | Wire Color in `diagram.json` | Example Nets |
|---|---|---|
| Active / source path | `"red"` | `esp:3V3.1 -> r_blue:2`, `esp:4 -> r_red:2`, `r_red:1 -> led_red:A` |
| Ground or sink return | `"black"` | `led_red:C -> gnd1:GND`, `esp:4 -> led_blue:C` |
| Multi-signal bus discrimination | a distinct colour per signal | use only when two signals share a bus and the reader must tell them apart |
| Debug serial | `"green"` | `esp:TX -> $serialMonitor:RX` |

---

## 5. Offline Verification

Always lint `assets/diagram.json` offline before committing:
```sh
wokwi-cli lint --offline homeworks/<id>/assets/diagram.json
```
A passing check ensures:
- All parts exist in the Wokwi catalog.
- All pin identifiers and net mappings are valid.
- Zero dangling or invalid pins exist.

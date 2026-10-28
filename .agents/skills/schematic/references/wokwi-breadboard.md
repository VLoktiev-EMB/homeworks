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

| Wire Function | Wire Color in `diagram.json` | Example Nets |
|---|---|---|
| Power (`3.3V` / `5V`) | `"red"` | `esp:3V3.1 -> led2:A`, `esp:3V3.1 -> bb1:tp.1` |
| Ground (`GND`) | `"black"` | `led1:C -> esp:GND.1`, `btn1:2.l -> esp:GND.1` |
| Input Signals | `"green"` | `btn1:1.l -> esp:7` |
| Driver / Output 1 | `"orange"` | `esp:4 -> r1:2` |
| Driver / Output 2 | `"purple"` | `esp:6 -> r2:2` |
| Intermediate Jumpers | `"blue"` | `r1:1 -> led1:A`, `r1:1 -> led2:C` |

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

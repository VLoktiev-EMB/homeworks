# Wokwi Breadboard & Manhattan Routing Reference

Guidelines and standards for creating clean, realistic, and offline-verifiable breadboard circuits (`assets/diagram.json`) in the Wokwi simulator.

## 1. Breadboard Coordinate Grid & Alignment

The standard half-size solderless breadboard (`wokwi-breadboard-half`) provides 30 columns with terminal rows `a-e` (top half) and `f-j` (bottom half), separated by a center DIP trough.

### Dimensions & Offsets
* **Standard Half-Size Breadboard**: `type: "wokwi-breadboard-half"`, dimensions roughly `300 × 160 px`.
* **MCU Placement**: Microcontroller board (`esp`) placed on the left (`top: 0, left: 0`).
* **Breadboard Placement**: Placed to the right (`top: -30, left: 180`).

### Pin Addressing
| Pin Section | Pin Syntax | Function |
|---|---|---|
| Top Positive Rail | `bb1:tp.1` .. `bb1:tp.30` | 3.3V / 5V VCC supply rail |
| Top Negative Rail | `bb1:tn.1` .. `bb1:tn.30` | Ground (GND) return rail |
| Top Terminal Rows | `bb1:1t.a` .. `bb1:30t.e` | Component signal ties |
| Bottom Terminal Rows | `bb1:1b.f` .. `bb1:30b.j` | Component signal ties |
| Bottom Positive Rail | `bb1:bp.1` .. `bb1:bp.30` | Optional auxiliary VCC rail |
| Bottom Negative Rail | `bb1:bn.1` .. `bb1:bn.30` | Optional auxiliary GND rail |

---

## 2. No-Chip-Crossing Wire Routing Rule

> [!IMPORTANT]
> Jumper wires emerging from microcontroller pin headers must **NEVER cut across the face of the microcontroller board, antenna, or RF shielding metal**.

### The Overhead Conduit Pattern
When routing wires from the left pin header of an MCU to a breadboard on the right:
1. Step **left** off the pin by 15–30 px (`h-20`).
2. Travel **up** above the top edge and antenna of the board (`v-40`).
3. Travel **right** across the top in a clean horizontal conduit (`h220`).
4. Drop **down** into the breadboard target column (`v30`).

```json
[
  "esp:4",
  "r1:1",
  "orange",
  [
    "h-15",
    "v-45",
    "h210",
    "v30"
  ]
]
```

### Power Rails Connection
Microcontroller `3V3` and `GND` should connect once to the breadboard top rails:
```json
[
  ["esp:3V3.1", "bb1:tp.1", "red", ["h-20", "v-40", "h240"]],
  ["esp:GND.1", "bb1:tn.1", "black", ["h20", "v-60", "h180"]]
]
```
All breadboarded components then tap `bb1:tp` and `bb1:tn` locally using short vertical jumpers (`v-20`), eliminating long diagonal wires back to the microcontroller headers.

---

## 3. Boundary Containment (No Off-Board Parts)

Every component must remain fully seated within the breadboard boundary:
* **Resistors**: Span horizontally between rows (e.g. `left: 230`, spanning cols 8–12).
* **LEDs**: Vertical orientation with cathode in the negative ground rail row or terminal strip (`left: 360`).
  * Upper LED: `top: 0`
  * Middle LED: `top: 55`
  * Lower LED: `top: 105` (never exceed `top: 120` on a half-breadboard to prevent parts hanging in the air).

---

## 4. Standard Wire Color Palette

| Wire Function | Wire Color in `diagram.json` | Example Nets |
|---|---|---|
| Power (`3.3V` / `5V`) | `"red"` | `3V3.1 -> bb1:tp.1`, `led2:A -> bb1:tp.15` |
| Ground (`GND`) | `"black"` | `GND.1 -> bb1:tn.1`, `led1:C -> bb1:tn.15` |
| Input Signals | `"green"` | `btn1:1.l -> esp:7` |
| Driver / Output 1 | `"orange"` | `esp:4 -> r1:1` |
| Driver / Output 2 | `"purple"` | `esp:6 -> r2:1` |
| Intermediate Jumpers | `"blue"` | `r1:2 -> bb1:12t.a` |

---

## 5. Offline Verification

Always lint `assets/diagram.json` before committing:
```sh
wokwi-cli lint --offline homeworks/<id>/assets/diagram.json
```
A green check confirms:
- All parts exist in the parts catalog.
- All pin identifiers are valid.
- No dangling or disconnected invalid nets exist.

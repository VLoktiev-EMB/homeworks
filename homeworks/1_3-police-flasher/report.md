# Police Flasher

A two-LED police beacon on the ESP32-S3-DevKitC-1 with a third LED, four run-time
patterns, three run-time speeds, and a single-GPIO half-bridge profile.

## 1. Title and Metadata

| Field | Value |
|-------|-------|
| Homework ID | `1_3-police-flasher` |
| Title | Police Flasher |
| Board | ESP32-S3-DevKitC-1 (N16R8: 16 MB flash, 8 MB octal PSRAM) |
| Framework | Arduino |
| Language | C++ composition root; pure C pattern library |
| PlatformIO Core | 6.2.0 |
| Platform | `platformio/espressif32` 8.0.0 |
| Homework status | `in-progress` |
| Report status | `draft` |
| Implementation commit | `6a60426` |
| Wiring source of truth | [assets/diagram.json](assets/diagram.json) |

The report describes the firmware at the implementation commit recorded above. The wiring
diagram is canonical: where this report and the diagram disagree, the diagram wins and this
report is corrected.

## 2. Objective

The assignment asks for a repeating police-style beacon on an ESP32-S3 board in which two
primary LEDs alternate and are never lit at the same time. This implementation delivers the
core alternation and all four extensions. A third LED takes part in the pattern. The pattern
is selected at run time from four modes without a reset. The speed is selected at run time
from three discrete bases. The two primary LEDs can be driven from a single GPIO through an
anti-parallel half-bridge, so the circuit does not need one pin per primary LED. The pattern
logic is a pure C library with a data-driven frame table, compiled unchanged for the target
and for the native Unity suite.

## 3. Assumptions

Each assumption is stated with the consequence of it being wrong and the method used to
validate it. A validation method that cannot be completed on the available bench is marked
as pending in the later evidence sections rather than assumed to have passed.

| ID | Assumption | Impact if wrong | Validation |
|----|------------|-----------------|------------|
| A-01 | Both LEDs of the anti-parallel pair are the same red type with a similar forward voltage. | The two halves differ in brightness, and the nominally off LED may conduct visibly. | Compare both LEDs in the multimeter's diode mode; confirm that exactly one is lit per alternating frame. |
| A-02 | The board regulator supplies 3.3 V nominal at the `3V3.1` pin. | LED current and the calculated timing margins shift; a low rail dims both halves. | Measure `3V3.1` to `GND.1` with a multimeter. |
| A-03 | The red LEDs have a forward voltage of about 1.9 V and a reverse rating of at least 5 V. | The operating current moves away from the design target, or the off LED sees an excessive reverse voltage. | Take the datasheet value, then measure the same part in diode mode and compare. |
| A-04 | R1 and R2 are 150 ohm parts with 5 percent tolerance. | The operating current changes by up to 5 percent beyond the calculated value. | Measure each resistor with a multimeter before assembly. |
| A-05 | BTN1 is a normally open momentary button wired to ground with the internal pull-up enabled. | A press reads inverted or never registers, so neither mode nor speed can be changed. | Continuity test with the board unpowered; observe the mode and speed changes over the serial log. |
| A-06 | The loop period is much shorter than the shortest half-hold, which is 50 ms at speed index 2 in CHASE. | Frame timing quantizes, and the beacon shows visible jitter at the fastest speed. | Measure the loop period or the GPIO4 period on the bench. |
| A-07 | GPIO4, GPIO6, and GPIO7 are safe, non-strapping pins for these signals. | A strapping pin can change the boot mode or the flash configuration at reset. | Check the datasheet strapping-pin table [1]; confirm that the build flashes and boots. |
| A-08 | `GND.1`, `GND.2`, and `GND.3` are one common board ground. | Separate returns create a ground offset and make the shared-current path unpredictable. | Continuity check between the three ground pins. |

## 4. Theory

### Frame model

A frame is a snapshot of the three LED flags plus a hold time: `(led_a, led_b, led_c,
hold_ms)`. Each mode owns a constant table of frames, and the hold of a frame is derived from
the selected speed base as `base_ms * num / den`. Keeping the rational pair in the table
makes the integer division visible in one place, keeps equal holds as distinct frames, and
ensures that a half-base hold cannot round to zero. Frames play in index order. The
controller advances at most one frame per tick; when a delayed tick leaves the schedule more
than one hold behind, it resynchronizes instead of catching up in a burst.

### Pattern modes

Four modes play in a fixed cycle: ALTERNATING, DOUBLE_FLASH, CHASE, and SOLID.

- ALTERNATING holds four frames of one base each: LED A, LED B, A plus LED C, and B plus C.
  Exactly one of LED A and LED B is active in every frame.
- DOUBLE_FLASH holds eight frames: two half-base pulses of LED A separated by a half-base
  gap, a full-base gap, two half-base pulses of LED B with the third LED joining the second
  pulse, and a full-base gap. Its cycle is five bases long.
- CHASE holds four half-base frames: LED A, LED B, LED C, and an off frame. Its cycle is two
  bases long.
- SOLID holds one all-on frame for four bases, so its cycle length is comparable with the
  other modes.

### Speed bases

Three speed bases are selectable: index 0 uses 400 ms, index 1 uses 200 ms, and index 2 uses
100 ms. Multiplying a mode's cycle length in bases by the selected base gives the pattern
period; for example ALTERNATING spans 1600 ms at index 0 and 400 ms at index 2, while CHASE
spans 800 ms and 200 ms respectively.

### Button handling

The button is read every tick as an active-low input. A raw level must remain stable for
30 ms before it becomes the debounced state. A short press is recognized on release and
advances the mode to the next entry in the fixed cycle. A press held for at least 600 ms
advances the speed once; releasing after a long press does not also advance the mode. Both
cycles wrap. A mode or speed change resets the frame schedule and applies the new frame on
the same tick.

### Single-GPIO half-bridge

The single-GPIO profile drives two anti-parallel LEDs from one pin. A literal anti-parallel
pair returned to ground cannot light its second LED, because current cannot flow from ground
into a GPIO pin. The implemented circuit is a half-bridge. One 150 ohm resistor connects
GPIO4 to a shared node X. LED1 has its anode at X and its cathode at ground. LED2 has its
anode at `3V3.1` and its cathode at X.

When GPIO4 is driven high, current flows from the pin through the resistor and LED1 to
ground, and LED1 clamps X near its forward voltage, about 1.9 V. LED2 then sees roughly
3.3 V minus 1.9 V, about 1.4 V, across it in reverse, below its conduction threshold, so it
stays off. When GPIO4 is driven low, current flows from `3V3.1` through LED2 and the resistor
into the pin, and LED2 clamps X near the same forward voltage below the rail. LED1 then sees
the same small reverse voltage and stays off. The argument depends on both LEDs having
similar forward voltages; unequal parts make the two halves unequal in brightness.

### Limitations

Two behaviours of the single-GPIO profile cannot be reproduced faithfully.

First, an all-off frame drives GPIO4 to a high-impedance input rather than to a driven level.
On hardware the shared node floats near the clamp voltage of whichever LED leaks, so "both
LEDs dark" is a simulation-only approximation, and the off LED's reverse voltage is not
well-defined in that state. The firmware expresses the off state as a pin-mode change, not as
a write level.

Second, SOLID drives the pin high because LED A wins the precedence rule. In the single-GPIO
profile only the HIGH-side LED of the anti-parallel pair therefore lights; the LOW-side LED
stays dark. The third LED is independent of the profile and remains on. Neither limitation is
a defect in the pattern logic, but a report that presented either as a hardware behaviour
would overstate the evidence.

## 5. Hardware and Wiring

The circuit is the ESP32-S3-DevKitC-1 with seven physical parts. The diagram at
[assets/diagram.json](assets/diagram.json) declares `flashSize: "16"`, `psramType: "octal"`,
and `psramSize: "8"`, and it is the source of truth for every connection below. The board pin
names and the `3V3.1`, `GND.1`, `GND.2`, and `GND.3` labels follow the ESP32-S3-DevKitC-1 user
guide [2], and the board attribute names follow the Wokwi diagram-format documentation [4].
The serial monitor pair in the diagram is a virtual instrument connected to `TX` and `RX`,
not a physical part.

### Bill of Materials

| Ref | Part or value | Quantity | Package | Source or link | Notes |
|-----|---------------|----------|---------|----------------|-------|
| esp | ESP32-S3-DevKitC-1, N16R8 (16 MB flash, 8 MB octal PSRAM) | 1 | DevKitC-1 module | n/a (standard) | Course board; 3.3 V regulator; the flash and PSRAM settings match the diagram attributes. |
| r1 | 150 ohm resistor | 1 | axial, 0.25 W | n/a (standard) | Series resistor from GPIO4 to node X. |
| led1 | Red LED, 5 mm | 1 | through-hole | n/a (standard) | Anode at node X, cathode at `GND.1`; lights when GPIO4 is high. |
| led2 | Red LED, 5 mm | 1 | through-hole | n/a (standard) | Anode at `3V3.1`, cathode at node X; lights when GPIO4 is low. |
| r2 | 150 ohm resistor | 1 | axial, 0.25 W | n/a (standard) | Series resistor from GPIO6 to the LED3 anode. |
| led3 | Red LED, 5 mm | 1 | through-hole | n/a (standard) | Anode at r2, cathode at `GND.2`. |
| btn1 | Momentary pushbutton, normally open | 1 | through-hole | n/a (standard) | One contact to GPIO7, the other to `GND.3`; the internal pull-up holds the pin high. |

### Pin Map

| Signal | ESP32-S3 pin | Connects to | Notes |
|--------|--------------|-------------|-------|
| Primary LED pair (LED A / LED B) | GPIO4 | `r1:1`; `r1:2` is node X, with `led1:A` and `led2:C` | Half-bridge drive. High lights LED1; low lights LED2; both low states are never driven together. |
| Third LED (LED C) | GPIO6 | `r2:1`; `r2:2` to `led3:A` | Independent of the primary pair and active in every mode that sets `led_c`. |
| Mode button | GPIO7 | `btn1:1.l`; `btn1:2.l` to `GND.3` | Configured as `INPUT_PULLUP`; a low level means pressed. |
| Reserved | GPIO5 | Not connected in this build | Reserved for the alternative three-LED profile, where each LED has its own pin. The composition root passes GPIO5 as `pin_b` but the single-GPIO profile never drives it. |
| Supply | 3V3.1 | `led2:A` | 3.3 V rail feeding the second half of the half-bridge. |
| Ground | GND.1 | `led1:C` | Return for LED1. |
| Ground | GND.2 | `led3:C` | Return for LED3. |
| Ground | GND.3 | `btn1:2.l` | Return for the button; the three ground pins are one common board ground. |

### Electrical Calculations

The calculations use the nominal 3.3 V supply, a 1.9 V typical forward voltage for a red
LED, and a 10 mA design target for the operating current. The supply and the forward voltage
are datasheet values until the bench measures them; the current target is a design choice.
Every row prints the formula and its inputs, so each result can be reproduced without any
other section.

| ID | Quantity | Formula | Units | Input provenance | Result | Uncertainty | Assumption effect |
|----|----------|---------|-------|------------------|--------|-------------|-------------------|
| C-01 | Series resistor R1 | `R = (Vs - Vf) / I` | ohm | `Vs = 3.3 V` datasheet nominal, pending measurement at `3V3.1`; `Vf = 1.9 V` datasheet typical, pending measurement in diode mode; `I = 10 mA` calculated design target | `R = (3.3 - 1.9) / 0.010 = 140 ohm`; the standard 150 ohm value is fitted | plus or minus 21 ohm from a plus or minus 0.05 V supply and a plus or minus 0.2 V forward voltage | Rounding up to 150 ohm lowers the current; a lower forward voltage raises it. |
| C-02 | LED current, LED1 high side | `I = (Vs - Vf) / R` | mA | `Vs = 3.3 V` datasheet nominal, pending measurement; `Vf = 1.9 V` datasheet typical, pending measurement; `R = 150 ohm` datasheet nominal, 5 percent tolerance | `I = 1.4 / 150 = 9.33 mA` | plus or minus 1.4 mA from the two voltage tolerances and the resistor tolerance | A 5 percent resistor changes the current by about 0.47 mA; the same forward voltage on both halves keeps them equally bright. |
| C-03 | Resistor power, R1 | `P = I^2 * R` | mW | `I = 9.33 mA` calculated, row C-02; `R = 150 ohm` datasheet nominal | `P = (9.33e-3)^2 * 150 = 13.1 mW` | plus or minus 3.9 mW, dominated by the current uncertainty | A 0.25 W part dissipates about 5 percent of its rating; a lower forward voltage raises the power slightly. |
| C-04 | Off-state reverse voltage, LED2 | `Vr = Vs - Vf` | V | `Vs = 3.3 V` datasheet nominal, pending measurement; `Vf = 1.9 V` datasheet typical, pending measurement; reverse rating 5 V datasheet | `Vr = 1.4 V`, about 28 percent of the 5 V rating | plus or minus 0.25 V from the two voltage tolerances | Valid only while the opposite LED conducts and clamps node X. The all-off frame drives GPIO4 to a high-impedance input, so the node floats and this calculation is excluded; the off LED's reverse voltage is not well-defined in that state. |
| C-05 | Pattern period | `T = base * sum(num / den)` | ms | Frame tables and rational holds calculated from the firmware; base 400, 200, or 100 ms calculated from the speed table | ALTERNATING 1600 / 800 / 400 ms; DOUBLE_FLASH 2000 / 1000 / 500 ms; CHASE 800 / 400 / 200 ms; SOLID 1600 / 800 / 400 ms for speed index 0 / 1 / 2 | exact as designed at the table level; the realized period adds one loop tick of quantization, pending measurement | A loop period close to the shortest 50 ms half-hold would stretch the fastest CHASE period; assumption A-06 bounds this. |
| C-06 | GPIO current margin | `margin = Imax - I` and `utilization = I / Imax * 100` | mA, percent | `Imax = 40 mA` datasheet absolute maximum per pin; `I = 9.33 mA` calculated, row C-02 | `margin = 30.67 mA`; `utilization = 23.3 percent` | plus or minus 1.4 mA on the current; the maximum is a datasheet limit, not a measured value | If the forward voltage falls to 1.8 V the current rises to 10.0 mA, still 25 percent of the limit; omitting the resistor would leave only the pin and the LED to limit current. |

### Safety Checklist

- **3V3-to-ground short.** `led2:A` is tied directly to `3V3.1` with no series element on that
  side. Node X, the `led2:C` lead, and the resistor body must never touch ground or the
  button return while the board is powered. Check continuity between `3V3.1` and each ground
  pin before applying power.
- **Per-pin current limit.** Each output pin drives its LED through a 150 ohm resistor, which
  keeps the calculated current near 9.3 mA, well below the ESP32-S3 absolute maximum of
  40 mA per pin. Never connect LED1, LED2, or LED3 without its series resistor, and never
  parallel two LEDs onto one resistor.
- **LED polarity.** LED1 must have its anode at node X and its cathode at `GND.1`; LED2 must
  have its anode at `3V3.1` and its cathode at node X; LED3 must have its anode at R2 and its
  cathode at `GND.2`. Reversing LED1 or LED2 swaps the high/low mapping and the beacon stops
  alternating correctly.
- **Shared ground.** `GND.1`, `GND.2`, and `GND.3` are the same board ground. Join all three
  returns to that single point and do not introduce a second ground reference, or the
  half-bridge current will flow through an unintended path.

## 6. Methodology

The target is built from the repository root with PlatformIO Core 6.2.0 and
`platformio/espressif32` 8.0.0:

```text
pio run -d homeworks/1_3-police-flasher
```

The build uses the project's 16 MB partition table and the N16R8 overrides inherited from
`platformio.shared.ini`. The firmware is flashed with the same toolchain, and the serial
port is opened at 115200 baud; the firmware prints `pattern ready` after a successful
controller initialization, which is the handshake the simulation scenario waits for.

The pure logic is exercised on the host with Unity:

```text
pio test -d homeworks/1_3-police-flasher -e native
```

The native environment follows the PlatformIO unit-testing structure [3]: it compiles the same
`lib/pattern` sources as the target, with `test_build_src = false`, and supplies
`host/fake_gpio` and `host/fake_time` as deterministic doubles. The suite covers the four mode
tables, the mode and speed cycles, the hold arithmetic, the debounce boundary, short and long
presses, both GPIO profiles, and the failure-retry paths. The Arduino composition root is not
unit-tested; it is covered by the target build and by the serial handshake.

The three D-11 bench measurements are taken with the following instruments and procedures.
Each result belongs in the measurement ledger, labelled with its instrument, method,
uncertainty, and the implementation commit.

1. **Supply voltage.** A multimeter in DC-volts mode across `3V3.1` and `GND.1`. The
   uncertainty is the meter's DC accuracy over the selected range, typically plus or minus
   0.5 percent of the reading plus two counts.
2. **LED current.** A multimeter in DC-current mode in series with the LED1 cathode, with the
   `led1:C` to `GND.1` connection temporarily broken. The uncertainty is the meter's
   DC-current accuracy, typically plus or minus 1.0 percent of the reading plus three counts,
   plus the burden voltage effect on the operating point.
3. **Blink period.** An oscilloscope or logic analyzer on GPIO4, measuring the interval
   between ten consecutive rising edges and dividing by ten. The uncertainty is plus or minus
   0.5 percent of the reading plus one sample interval of the instrument.

The forward voltage is additionally checked in the multimeter's diode mode and compared with
the datasheet value. Diode mode tests at a much lower current than the operating point, so
the reading is evidence about the part, not a substitute for the datasheet value in the
current calculation.

The serial log also records the debounce outcome and every mode and speed transition with a
timestamp. That record is labelled observed rather than measured, because the serial path
adds buffering and scheduling delay that the bench instruments do not characterise.

## 7. Results

_Pending: plan 04.2-05 adds the build, native-test, serial, and bench results._

## 8. Analysis

_Pending: plan 04.2-05 adds the analysis and the industry notes._

## 9. Conclusions

_Pending: plan 04.2-05 adds the evidence-bound conclusions and the honest status._

## 10. References

_Pending: plan 04.2-05 adds the IEEE reference list._

## Decision Appendix

_Pending: plan 04.2-05 adds the engineering decisions, dead ends, and friction._

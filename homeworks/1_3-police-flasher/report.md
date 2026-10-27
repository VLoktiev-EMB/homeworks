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
| Implementation commit | `9e1238d` |
| Wiring source of truth | [assets/diagram.json](assets/diagram.json) |

The recorded commit is the last commit that changes the homework's source, build, or
simulation inputs; every commit after it changes only documentation, and the source, build,
and simulation diff from `9e1238d` to the working tree is empty. The report describes the
firmware at the implementation commit recorded above. The wiring
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
| A-05 | BTN1 is a normally open momentary button wired to ground with the internal pull-up enabled. | A press reads inverted or never registers, so neither mode nor speed can be changed. | Continuity test with the board unpowered; observe the button presses on GPIO7 with a logic analyzer and confirm the resulting mode and speed changes on the LEDs, because the current firmware has no serial transition log. |
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

The circuit is the ESP32-S3-DevKitC-1 with seven physical parts. The vector electrical schematic
is available in [assets/schematic.svg](assets/schematic.svg). The breadboard simulation model at
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

| Signal | Pin | Connects to | Notes |
|--------|-----|-------------|-------|
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

The firmware emits exactly two serial events: `pattern ready` on a successful controller
initialization and `pattern init failed` otherwise. It does not log the debounce outcome, the
mode, or the speed, because `pattern_controller_tick` receives no log port and the controller
performs no transition logging. D-14 reserves the qualified form `measured (observed)` for a
debounce result read from a serial log, but no row uses that form today because the firmware
has no transition log to read; a logic-analyzer capture of GPIO7 is the instrument that can
produce a debounce observation for this hardware profile. `observed` is never used as a label
of its own.

## 7. Results

The target environment builds and the native suite runs on the host. The bench quantities are
reported through the ledger below; no serial log and no bench reading were supplied in this
session, so those rows are `not measured` and no value is inferred from the calculations.

**Target build.** `pio run -d homeworks/1_3-police-flasher` reports `SUCCESS` for
`esp32s3_arduino`. The incremental run that re-verified the report's code tree took 0.54 s;
the cold build of the same tree earlier in the phase took 8.21 s. The linker reports 22,752 of
327,680 bytes of RAM (6.9 percent) and 313,604 of 6,553,600 bytes of flash (4.8 percent). The
resolved dependency graph names `common`, `port`, `arduino`, and the homework-local `pattern`
library at version 0.1.0.

**Native suite.** `pio test -d homeworks/1_3-police-flasher -e native` reports 38 test cases
in three suites, all passed, in 1.429 s: `test_homework` (2 cases), `test_pattern` (14 cases),
and `test_controller` (22 cases). The suite covers the four frame tables and their rational
holds, the 399/400 ms debounce boundary, short and long presses, both GPIO profiles, the
schedule stall and 32-bit wrap behaviour, and the read and write retry paths.

**Serial observation.** No serial log was captured in this session, and the firmware has no transition logging: `pattern_controller_tick` receives no log port, so it cannot report a mode or a speed change over the serial port. The `pattern ready` and `pattern init failed` handshake messages described in the methodology are the only serial events the firmware is designed to emit, and neither was recorded here.

**Bench results.** No bench reading was supplied in this session. The supply voltage, the LED
current, the blink period, the forward voltage in diode mode, and the button debounce are
therefore `not measured` in the ledger, with the fixed reason `bench equipment offline during
automated tracer run`, rather than estimated from the calculations.
No measured values were captured in this session.

**Simulation.** The canonical diagram passed `wokwi-cli lint --offline`, and the scenario was
then executed in Wokwi: all three counted runs exited 0 and each captured stream carried exactly
one `pattern ready` line, so `simulation.status` is `verified`. The run output stays `simulated`
evidence, never bench evidence. The raw commands and per-run values are in
`.planning/phases/07-simulation-spike/07-SPIKE-EVIDENCE.md`, and the tool selection is recorded
in `docs/decisions/0014-simulator-selection.md`.

### Measurement Ledger

The label column uses exactly the five D-13 labels — `measured`, `calculated`, `simulated`,
`datasheet`, and `not measured` — plus the single qualified form `measured (observed)` that
D-14 reserves for a debounce result read from the firmware's serial log. A bare `observed` is
not a label. A `measured` value cell begins with `user-reported:` when the value was supplied
verbatim as a bench reading in the session, or `serial-log:` when it was read from the
firmware's own log; no other row carries the `measured` label. The implementation commit is
the code the report describes, and every row names the same commit as the metadata table.

| ID | Quantity | Value | Label | Instrument | Method | Uncertainty | Implementation commit |
|----|----------|-------|-------|------------|--------|-------------|-----------------------|
| L-01 | Supply voltage at `3V3.1` | not measured: bench equipment offline during automated tracer run | not measured | multimeter | DC volts across `3V3.1` and `GND.1`, procedure 1 in the methodology | not applicable: no reading was taken | `9e1238d` |
| L-02 | LED current through LED1 | not measured: bench equipment offline during automated tracer run | not measured | multimeter | DC current in series with the LED1 cathode, procedure 2 in the methodology | not applicable: no reading was taken | `9e1238d` |
| L-03 | Blink period on GPIO4 | not measured: bench equipment offline during automated tracer run | not measured | oscilloscope or logic analyzer | interval between ten rising edges divided by ten, procedure 3 in the methodology | not applicable: no reading was taken | `9e1238d` |
| L-04 | Forward voltage in diode mode | not measured: bench equipment offline during automated tracer run | not measured | multimeter | diode mode across LED1, forward biased, compared with the datasheet typical value | not applicable: no reading was taken | `9e1238d` |
| L-05 | Series resistance (calculated) | `R = (3.3 V - 1.9 V) / 10 mA = 140 ohm`; the standard 150 ohm part is fitted | calculated | none | C-01 from the datasheet nominal supply and forward voltage, with a 10 mA design target | plus or minus 21 ohm from a 0.05 V supply and a 0.2 V forward-voltage variation | `9e1238d` |
| L-06 | Resistor power (calculated) | `P = (9.33 mA)^2 * 150 ohm = 13.1 mW` | calculated | none | C-03 with the current of C-02 | plus or minus 3.9 mW, dominated by the current uncertainty | `9e1238d` |
| L-07 | Pattern period (calculated) | ALTERNATING 1600 / 800 / 400 ms; DOUBLE_FLASH 2000 / 1000 / 500 ms; CHASE 800 / 400 / 200 ms; SOLID 1600 / 800 / 400 ms at speed index 0 / 1 / 2 | calculated | none | C-05 from the frame tables and their rational holds | exact at the table level; the realized period adds loop-tick quantization that was not measured | `9e1238d` |
| L-08 | Expected Wokwi period (simulated) | alternating frame 0 holds GPIO4 high for 400 ms at speed index 0; the scenario expects GPIO4 high 100 ms after the handshake | simulated | Wokwi, three runs bounded by `--timeout 15000` | `scenario.yaml` read against the frame table; the scenario then executed with its `expect-pin esp:4 == 1` step passing in every run | expected timing only; the run confirms the assertion path, not a bench period, because simulation output is not hardware evidence | `9e1238d` |
| L-09 | Per-pin current limit (datasheet) | 40 mA absolute maximum per GPIO pin | datasheet | none | ESP32-S3 datasheet absolute maximum ratings [1], compared with C-06 | datasheet limit, not a measured value; C-06 computes a 30.67 mA margin | `9e1238d` |
| L-10 | Button debounce | not measured: bench equipment offline during automated tracer run; the firmware emits only the `pattern ready` handshake, so no serial transition log exists | not measured | logic analyzer on GPIO7 | logic-analyzer capture of the mode and speed transitions on GPIO7; the D-14 serial-timestamp method is unavailable until the firmware gains transition logging (Phase 11) | not applicable: no observation was captured | `9e1238d` |
| L-11 | Junction temperature | not measured: bench equipment offline during automated tracer run | not measured | none | the die temperature is not exposed by the firmware or by the board | not applicable: not observable with the available instruments | `9e1238d` |
| L-12 | Off-state node voltage at node X | not measured: bench equipment offline during automated tracer run | not measured | multimeter | DC volts at node X while the all-off frame leaves GPIO4 high-impedance | not applicable: no reading was taken, and the floating node has no well-defined value | `9e1238d` |

### Interpreting the Forward-Voltage Row

The forward voltage in the multimeter's diode mode would not equal the datasheet value used in
the calculations. Diode mode injects a small test current, typically well below one
milliampere, while the operating point of this circuit is about 9.3 mA; at the higher current
the junction is further forward biased, so the operating forward voltage is higher than the
diode-mode reading. The comparison is therefore evidence about the part, not a replacement for
the datasheet value in C-01 and C-02. In this session neither reading exists: the diode-mode
row is `not measured`, and the calculations continue to use the 1.9 V datasheet typical value,
which is why they carry the stated uncertainty rather than a measured value's tolerance.

### Traceability Matrix

The matrix maps every phase claim to the artifact that carries it, the method that checks it,
the evidence item that supports it, and a status. `verified` means a command or test in this
repository produced the evidence; `manual` means a human review owns it; `pending` means the
evidence does not exist yet and the row names the phase that owns it.

| ID | Claim or requirement | Design artifact | Verification method | Evidence | Status |
|----|----------------------|-----------------|---------------------|----------|--------|
| T-01 | Target build for `esp32s3_arduino` (INV-02) | `platformio.ini`, `src/main.cpp`, `lib/pattern` | `pio run -d homeworks/1_3-police-flasher` | `SUCCESS`; 22,752 of 327,680 bytes RAM and 313,604 of 6,553,600 bytes flash | verified |
| T-02 | Native Unity suite (INV-02) | `test/test_homework`, `test/test_pattern`, `test/test_controller` | `pio test -d homeworks/1_3-police-flasher -e native` | 38 of 38 cases pass in 1.429 s | verified |
| T-03 | Third-LED extension (D-02) | `led_c` column in the frame tables; GPIO6 in `src/main.cpp` | `test_pattern` third-LED cases; diagram net `esp:6` | 14 pattern cases pass; the net is present in `assets/diagram.json` | verified |
| T-04 | Variable-speed extension (D-02) | speed table of 400, 200, and 100 ms; long-press cycle | `test_pattern` hold-scaling case; `test_controller` speed-cycle case | both cases pass | verified |
| T-05 | Complex-pattern extension (D-02) | DOUBLE_FLASH and CHASE frame tables | `test_pattern` double-flash and chase cases | both cases pass | verified |
| T-06 | Single-GPIO extension (D-02) | `PATTERN_GPIO_SINGLE`; half-bridge wiring; controller precedence | `test_controller` SOLID and all-off cases; diagram nets `esp:4`, `r1`, `led1`, `led2` | cases pass; the four nets are present in `assets/diagram.json` | verified |
| T-07 | Bill of materials (REPORT-02) | BOM in section 5 | manual cross-check against the diagram part ids | 7 of 7 diagram ids have a BOM row | verified |
| T-08 | Pin map and wiring source of truth (REPORT-03) | pin map in section 5; `assets/diagram.json` | manual cross-check against the diagram nets | 10 required nets present; GPIO5 recorded as reserved | verified |
| T-09 | Diagram validity (REPORT-03) | `assets/diagram.json` | `wokwi-cli lint --offline` | exit 0 with the informational unsupported-part note | verified |
| T-10 | Electrical calculations (REPORT-04) | C-01 to C-06 in section 5 | recomputation from each printed formula and input | six rows carry formula, units, provenance, result, uncertainty, and assumption effect | verified |
| T-11 | Measurement ledger (REPORT-06) | ledger in section 7 | label and prefix check over L-01 to L-12 | 12 rows; labels within the five-label set plus `measured (observed)`; no `measured` row; the fixed `not measured` reason is present | verified |
| T-12 | Traceability matrix (REPORT-07) | this table | manual review of claim coverage | this file | manual |
| T-13 | English paraphrase and provenance (META-02) | `task.md` | D-09 checklist confirmed by the repository owner on 2026-10-25 and `check_metadata.py` | repository owner confirmed on 2026-10-25: no verbatim sentence, no distinctive phrasing, no original file committed; the checker exits 0 | manual |
| T-14 | Architecture boundary (INV-04) | `lib/` and `scripts/check_architecture.py` | `python3 scripts/check_architecture.py` | exit 0; the private library lives outside `lib/` | verified |
| T-15 | Simulation execution (SIM-01 first pass) | `scenario.yaml`, `wokwi.toml`, `../../scripts/pio/merge_firmware.py` | `wokwi-cli lint --offline`; the three-run execution recorded in `07-SPIKE-EVIDENCE.md` | lint exits 0; all three counted runs exited 0 with one `pattern ready` serial line each, so `simulation.status` is `verified` | verified |
| T-16 | High-impedance off-state behaviour is implemented and tested | controller mode change in `lib/pattern/src/controller.c`; limitation statement in sections 4 and 11 | `test_controller` all-off frame case; report statement | the fake records `INPUT` on the all-off frame; the hardware off-state node voltage is `not measured` (L-12) | verified |
| T-17 | SOLID single-pin precedence is implemented and tested | `led_a` precedence in `lib/pattern/src/controller.c`; limitation statement in sections 4 and 11 | `test_controller` SOLID case; report statement | the case passes; the LOW-side LED's hardware state was not observed | verified |
| T-18 | Ten-section report structure (REPORT-01) | `report.md` | `uv run scripts/check_report.py` | the ten contracted headings and every required subsection are present | verified |
| T-19 | Electrical safety checklist (REPORT-05) | Safety Checklist in `report.md` | manual review of the four hazard bullets against the wiring | four bold hazard bullets cover the 3V3-to-ground short, the per-pin current limit, the LED polarity, and the shared ground | verified |
| T-20 | Honest status, verified toolchain, limitations, and next steps (REPORT-08) | `report.md` | manual review of sections 4, 9, and the Decision Appendix | sections 4 and 9 state both fidelity limits; the `Status:` paragraph names Phase 11 for the tag and scale-out | manual |

## 8. Analysis

The firmware separates the pattern schedule from the platform in a way that changes what can be
tested. A state machine that reads an injected clock returns from every call, so a test can
place the clock at 399 ms and then at 400 ms and observe the frame boundary exactly, without
waiting. A `delay()`-based loop would make the same boundary a property of wall-clock time and
of the scheduler, and the 22 controller cases in this suite could not exist in their present
form; the five-tick drift and one-frame stall cases are expressible only because the elapsed
time is an argument rather than an ambient fact [3].

The half-bridge is the design correction that makes the single-GPIO requirement real. A literal
anti-parallel pair returned to ground can light only the LED whose anode faces the pin; on a low
output the other LED would need current to flow from ground into the GPIO, which it cannot.
The implemented circuit returns LED1 to ground and LED2 to the 3.3 V rail through the same
resistor, so a high output forward-biases LED1 and a low output forward-biases LED2. The
resistor therefore sets the current in both halves, and the datasheet limit of 40 mA per pin
[1] bounds the design: C-06 computes 9.33 mA and a 30.67 mA margin, so the 150 ohm choice is
conservative by a factor of about four rather than marginal [5].

Two behaviours of the profile are honestly simulation approximations. The all-off frame leaves
GPIO4 high-impedance, so node X floats near the clamp voltage of whichever LED leaks; "both
LEDs dark" describes the model, not the board, and the off-state node voltage is consequently
`not measured` rather than calculated. In SOLID the precedence rule drives the pin high, so
only the HIGH-side LED of the pair lights. Presenting either behaviour as a hardware result
would overstate the evidence, and both are recorded in the decision appendix and the
traceability matrix.

The forward-voltage comparison teaches the same lesson at the component level. A diode-mode
reading is taken at a test current far below the 9.3 mA operating point, so it is lower than
the value the junction presents in service; the calculations therefore keep the datasheet
typical value and carry its uncertainty, while a diode-mode row records an independent check of
the part. This is also why no bench quantity is inferred: a calculated value transferred into a
measured row would erase the distinction the evidence depends on.

Industry note: the non-blocking loop is the difference between a beacon that responds to its
button and one that does not. Embedded practice is to give every periodic task a deadline and a
tick, never a busy wait, because a blocking delay in one feature silently becomes the latency
of every other feature. The 30 ms debounce and the 600 ms long-press threshold are constants of
the same schedule, and the controller applies at most one frame per tick so a late loop cannot
produce a visible burst.

Industry note: hardware abstraction earns its keep only when it is narrower than the framework.
This homework uses `port_gpio_t` and `port_time_t` for exactly the two capabilities the logic
needs, and keeps the Arduino adapters at the composition root [6]; it does not wrap the whole
Arduino API, which would become a shadow framework and would hide the framework the course
teaches. The private library then compiles unchanged into the target and the host suite, so the
abstraction cost is paid once and the test seam comes with it.

Industry note: provenance in a measurement report is what lets a reviewer separate evidence
from expectation. A row that says `not measured` with a reason, an instrument, and a method is
more useful a year later than a plausible number with no trail, because the reviewer can see
which claims are still open and which phase owns them. The same discipline applies to the
simulation: in general, a scenario that has not been run is a `simulated` expectation, and a
lint result is not an observation. The executed run and the lint are therefore recorded as
separate evidence, so a reader can tell which claim rests on which.

## 9. Conclusions

The evidence supports four claims. The ESP32-S3 Arduino target builds from the same tree the
report describes, and the 38-case native suite passes, so the pattern logic and the controller
seam are exercised independently of the board. The four D-02 extensions are present in the
frame tables and reachable through the mode and speed cycles, and the native cases pin each
one. The wiring in `assets/diagram.json` lints against the Wokwi diagram format, and the pin
map, BOM, and calculations trace to its part ids and nets. The half-bridge is a correct
realization of the single-GPIO requirement, with its two fidelity limits stated rather than
hidden.

The evidence does not support any claim about the bench or the serial port, and the simulation
evidence is simulation-only. No measured values were captured in this session: the supply
voltage, LED current, blink period, forward voltage in diode mode, and button debounce are all
`not measured` with the fixed reason recorded in the ledger, and no measurement has been
inferred from a calculation. The Wokwi scenario was executed after that session: all three
counted runs exited 0 with one `pattern ready` line each, as recorded in
`.planning/phases/07-simulation-spike/07-SPIKE-EVIDENCE.md`, and the expected pattern timing
remains `simulated` evidence rather than a bench observation.

Status: the homework is in progress. No `hw/` tag exists; a tag is created only through
`scripts/tag_homework.sh <id>` after merge, and Phase 11 owns it. Simulation execution is
recorded in `.planning/phases/07-simulation-spike/07-SPIKE-EVIDENCE.md`, and the simulator
decision in `docs/decisions/0014-simulator-selection.md`. Phase 5 owns the generators for
the index, workspace, shared configuration, and documentation site; Phase 6 owns formatting,
clang-tidy, and the developer environment; Phase 8 owns the real CI matrix; Phase 10 owns the
report contract and its checker; Phase 11 owns the polished pilot, the tag, and scale-out.

### Next Steps

- Complete the bench evidence pass, so the `not measured` ledger rows can carry measured
  readings; Phase 11 owns it.
- Create the `hw/1_3-police-flasher` tag through `scripts/tag_homework.sh` after the pull
  request is merged; Phase 11 owns it.
- Scale the report contract and the retrofit out to the remaining homeworks; Phase 11 owns
  it.

## 10. References

[1] Espressif Systems, "ESP32-S3 Series Datasheet," Espressif Systems, 2025. [Online]. Available: <https://www.espressif.com/sites/default/files/documentation/esp32-s3_datasheet_en.pdf>

[2] Espressif Systems, "ESP32-S3-DevKitC-1 User Guide," Espressif Systems. [Online]. Available: <https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32s3/esp32-s3-devkitc-1/user_guide.html>

[3] PlatformIO, "Unit Testing: Shared Code," PlatformIO documentation. [Online]. Available: <https://docs.platformio.org/en/latest/advanced/unit-testing/structure/shared-code.html>

[4] Wokwi, "Diagram Format," Wokwi documentation. [Online]. Available: <https://docs.wokwi.com/diagram-format>

[5] VLoktiev-EMB, "ADR-0007: Symlinked shared libraries via lib_deps and library.json," Homeworks repository, Oct. 2026. [Online]. Available: <https://github.com/VLoktiev-EMB/homeworks/blob/main/docs/decisions/0007-symlink-shared-libraries.md>

[6] VLoktiev-EMB, "ADR-0008: Common depends on port; ports are consumer-owned," Homeworks repository, Oct. 2026. [Online]. Available: <https://github.com/VLoktiev-EMB/homeworks/blob/main/docs/decisions/0008-common-depends-on-port.md>

## Decision Appendix

1. **D-03 half-bridge correction.** The first single-GPIO idea was a literal anti-parallel pair
   returned to ground. It cannot light the second LED: on a low output the current would have
   to flow from ground into the GPIO pin. The circuit was corrected to the half-bridge in
   section 4, where LED1 returns to ground and LED2 returns to the 3.3 V rail through the same
   150 ohm resistor; one pin then drives either LED, and the resistor sets the current in both
   halves.
2. **High-impedance off state.** The all-off frame is a pin-mode change to `INPUT`, not a driven
   dark level. On hardware the shared node floats near the clamp voltage of the leaking LED, so
   "both LEDs dark" is a simulation-only approximation; the off-state node voltage is
   `not measured` (L-12), while the controller's mode-change behaviour is what the native suite
   verifies.
3. **SOLID on one pin.** `led_a` wins the precedence rule, so the pin is driven high and only
   the HIGH-side LED of the anti-parallel pair lights; the LOW-side LED stays dark. The third
   LED is independent and remains on. The frame tables keep `led_a` and `led_b` explicit so this
   rule stays visible and testable.
4. **D-08 timestamp amendment.** `retrieved` became `2026-10-23T00:00:00Z`. The checker's
   `valid_iso8601` requires a timezone, and a bare date is rejected once the status leaves
   `planned`; the date itself is unchanged.
5. **D-17 reading of ROADMAP success criterion 3.** A well-formed homework needs no
   per-homework entry in `platformio.shared.ini`: the file carries only the three shared
   environment sections, and the project extends them. The manual integration edits are the root
   README entry, the workspace folder, and the single-project CI workflow.
6. **D-18 reading of ROADMAP success criterion 3.** The CI outcome is one single-project workflow
   running `pio run` and `pio test -e native`, not a discovery matrix. Changed-only detection
   needs a separate script, which Phase 8 owns.
7. **Wokwi execution.** `WOKWI_CLI_TOKEN` was supplied outside the repository and its value is
   never recorded. All three counted runs exited 0 with one `pattern ready` serial line each, so
   `simulation.status` is `verified`; the commands and per-run values are in
   `.planning/phases/07-simulation-spike/07-SPIKE-EVIDENCE.md`, and the simulator decision is
   `docs/decisions/0014-simulator-selection.md`.
8. **Private library and controller seam (D-05, D-06, D-07).** The pattern logic stays
   homework-local at `lib/pattern` with a manifest that declares no frameworks; the controller
   takes `port_gpio_t` and `port_time_t` by value; the Arduino adapters live only in the
   composition root. Promotion to `lib/common` waits for real duplication across homeworks.
9. **D-09 paraphrase review record.** The repository owner performed the D-09 comparison against
   the access-restricted original on 2026-10-25 and confirmed three results: no verbatim sentence,
   no distinctive phrasing, and no original file committed. The document is English-only, contains
   zero Cyrillic codepoints, and names the public repository URL rather than the LMS URL. The
   review is a completed record, and `04-UAT.md` plus `04.2-SECURITY.md` T-4.2-02 hold the same
   confirmation and date.
10. **No release tag.** No `hw/` tag exists. The tag is created only through
    `scripts/tag_homework.sh <id>` after the pull request is merged, and Phase 11 owns that step;
    this phase ends with the homework in progress.

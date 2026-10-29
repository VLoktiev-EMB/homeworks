# Police Flasher

This homework implements an ESP32-S3 police beacon: a red and a blue LED
alternate on a shared push-pull GPIO, a white third LED adds a strobe phase,
and the cadence doubles on every full cycle. The pattern logic is a
framework-free step table verified by a native Unity suite; the target build,
the native suite, and the offline diagram lint are the evidence basis.

## 1. Title and Metadata

The values below are the metadata identity for this homework.

| Field | Value |
|-------|-------|
| Homework ID | `1_3-police-flasher` |
| Title | Police Flasher |
| Board | esp32-s3-devkitc-1 |
| Framework | Arduino |
| Language | C++ |
| PlatformIO Core | 6.2.0 |
| Platform | espressif32@8.0.0 |
| Homework status | in-progress |
| Report status | draft |
| Implementation commit | f2a1e0f |

## 2. Objective

The assignment asks for an ESP32 program that drives red and blue LEDs, each
through a series resistor, so the pair alternately flashes in a repeating
police-beacon sequence. It also offers optional extensions: a richer blink
pattern, a third LED, a changing blink speed, and a reduction of the two LEDs
to a single GPIO.

This implementation delivers all four extensions in one coherent circuit. Two
GPIOs drive three LEDs: GPIO4 carries the red and blue pair in push-pull, and
GPIO5 drives the white LED. The step table produces a red double flash, a blue
double flash, three white strobe pulses, and a pause, and it doubles every
duration after each full cycle.

## 3. Assumptions

The table records the design assumptions, including the two accepted intake
decisions.

| ID | Assumption | Impact if wrong | Validation |
|----|------------|-----------------|------------|
| A-01 | Red and blue share GPIO4 in push-pull, and the white LED uses GPIO5; this combines the three optional items into one circuit. | The wiring, bill of materials, and evidence would describe a different topology. | Diagram integrity is checked by L-03, and section 5 maps every terminal to a diagram part. |
| A-02 | Native tests are included although the initial intake selected none, because the repository Definition of Done requires a green native suite for pure logic. | The state machine would have no automated regression evidence, and the Definition of Done would be unmet. | L-02 is the historical two-suite result at `f2a1e0f`; the current tree runs the seven pattern tests in `test/test_police_pattern/`. |
| A-03 | The red LED forward voltage is 2.0 V at the calculated current, with a 1.8 V to 2.2 V bound for a typical 5 mm lamp. | Red current and resistor dissipation move inside the C-01 and C-05 bounds. | C-01 states the bound; the bench current L-04 is not measured. |
| A-04 | The blue LED forward voltage is 2.9 V at the calculated current, with a 2.8 V to 3.0 V bound. | Blue current moves inside the C-02 bound and brightness changes. | C-02 states the bound; the bench current L-05 is not measured. |
| A-05 | The white LED forward voltage is 3.0 V at the calculated current, with a 2.9 V to 3.1 V bound. | White current moves inside the C-03 bound and brightness changes. | C-03 states the bound; the bench current L-06 is not measured. |
| A-06 | GPIO4 and GPIO5 stay inside the ESP32-S3 40 mA per-pin absolute maximum. | An overcurrent event could damage the SoC pin. | C-04 compares the 5.9 mA worst case with the 40 mA limit from [1]. |
| A-07 | With GPIO4 in high-impedance INPUT, leakage is too small to light either shared-pin LED. | Visible ghosting would appear in the off state. | C-06 bounds the leakage drop at 1.1 mV; the visual check L-07 is not measured. |
| A-08 | The resistors are 1/4 W parts and need no derating at the calculated dissipation. | A smaller resistor could overheat. | C-05 compares 7.7 mW with the 250 mW rating. |

## 4. Theory

A push-pull GPIO can source current when driven HIGH and sink current when
driven LOW. The red branch runs from GPIO4 through `r_red` and `led_red` to
ground, so it conducts only when GPIO4 is HIGH. The blue branch runs from the
3.3 V rail through `r_blue` and `led_blue` to GPIO4, so it conducts only when
GPIO4 is LOW: the pin then sinks the blue current. When GPIO4 is HIGH, both
ends of the blue branch sit at 3.3 V and the LED is unbiased. When GPIO4 is
INPUT, neither branch has a complete current path, so both lamps are off. The
same pin therefore selects red, blue, or off without ever driving both lamps
at once.

The white LED is a conventional active-high branch from GPIO5 through
`r_white` and `led_white` to ground.

The pattern is a fixed table of fourteen steps. Each step names a pair state
and a white-LED level and carries a base duration. The state machine advances
when the caller's millisecond clock reaches the step deadline, and it never
reads a clock itself, so the same table runs on the target and under a host
test. `common_timer_expired` decides expiry with a signed 32-bit difference,
which keeps a deadline correct across the `millis()` wrap. After the last
step the index returns to zero and the `slow` flag toggles, doubling every
duration in the next cycle.

### Limitations

The implementation is not bench-verified: no current, voltage, brightness, or
temperature measurement was taken. The blue LED operates from a 3.3 V rail
with a forward voltage close to that rail, so its current is small and
sensitive to the actual lamp. Timing is limited by the 1 ms polling period and
the accuracy of `millis()`, and the pattern has no brightness or duty-cycle
control. The model assumes ideal push-pull behaviour and does not include pin
leakage beyond the C-06 bound.

## 5. Hardware and Wiring

The board is an ESP32-S3-DevKitC-1-N8 powered over USB. The wiring source of
truth is [assets/diagram.json](assets/diagram.json), and the generated IEEE
vector view is [assets/schematic.svg](assets/schematic.svg). The diagram is
linted offline by L-03, and its part ids are the bill-of-materials references
below.

### Bill of Materials

| Ref | Part or value | Quantity | Package | Source or link | Notes |
|-----|---------------|----------|---------|----------------|-------|
| esp | ESP32-S3-DevKitC-1-N8, 16 MB flash, 8 MB octal PSRAM | 1 | DevKitC | [2] | Board profile `boards/esp32-s3-devkitc-1.yaml` |
| r_red | 220 ohm resistor, 1/4 W | 1 | Axial THT | generic | Red branch series resistor |
| led_red | Red LED, Vf about 2.0 V | 1 | 5 mm THT | generic | Anode at `r_red`, cathode at ground |
| r_blue | 100 ohm resistor, 1/4 W | 1 | Axial THT | generic | Blue branch series resistor |
| led_blue | Blue LED, Vf about 2.9 V | 1 | 5 mm THT | generic | Anode at `r_blue`, cathode at GPIO4 |
| r_white | 100 ohm resistor, 1/4 W | 1 | Axial THT | generic | White branch series resistor |
| led_white | White LED, Vf about 3.0 V | 1 | 5 mm THT | generic | Anode at `r_white`, cathode at ground |

### Pin Map

| Signal | Pin | Connects to | Notes |
|--------|-----|-------------|-------|
| Red LED drive | GPIO4 | `r_red` terminal 2 | OUTPUT HIGH sources the red branch |
| Blue LED return | GPIO4 | `led_blue` cathode | OUTPUT LOW sinks the blue branch |
| Pair release | GPIO4 | Both LED branches | INPUT high impedance turns both off |
| White LED drive | GPIO5 | `r_white` terminal 2 | OUTPUT HIGH lights the white LED |
| 3.3 V supply | 3V3 | `r_blue` terminal 1 | Feeds the blue branch only |
| Ground return | GND | `led_red` cathode, `led_white` cathode | Common ground for both source branches |

### Electrical Calculations

| ID | Quantity | Formula | Units | Input provenance | Result | Uncertainty | Assumption effect |
|----|----------|---------|-------|------------------|--------|-------------|-------------------|
| C-01 | Red branch current | I = (V_rail - Vf_red) / R_red | mA | V_rail 3.3 V from [2], Vf 2.0 V from A-03, R 220 ohm from the BOM | 5.9 mA | plus or minus 0.9 mA from the 1.8 V to 2.2 V Vf bound | A-03 |
| C-02 | Blue branch current | I = (V_rail - Vf_blue) / R_blue | mA | V_rail 3.3 V from [2], Vf 2.9 V from A-04, R 100 ohm from the BOM | 4.0 mA | plus or minus 1.0 mA from the 2.8 V to 3.0 V Vf bound | A-04 |
| C-03 | White branch current | I = (V_rail - Vf_white) / R_white | mA | V_rail 3.3 V from [2], Vf 3.0 V from A-05, R 100 ohm from the BOM | 3.0 mA | plus or minus 1.0 mA from the 2.9 V to 3.1 V Vf bound | A-05 |
| C-04 | Worst-case GPIO4 current | I_pin = max(I_red, I_blue) | mA | C-01, C-02, and the 40 mA per-pin absolute maximum from [1] | 5.9 mA | plus or minus 0.9 mA from the red-current bound | A-06 |
| C-05 | Red resistor dissipation | P = I_red^2 times R_red | mW | C-01 and the 220 ohm BOM value | 7.7 mW | plus or minus 2.3 mW from the red-current bound | A-08 |
| C-06 | Off-state drop across the red branch | V_leak = I_leak times R_red | mV | 0.1 uA to 5 uA input-leakage bound from [1] and 220 ohm from the BOM | 0.22 mV typical | 0.02 mV to 1.1 mV across the leakage bound | A-07 |
| C-07 | Full-pattern duration | T_cycle = sum of the fourteen step durations | ms | Step table in `lib/police_pattern/src/police_pattern.c` | 2210 ms fast, 4420 ms slow | plus or minus 14 ms from the 1 ms polling tick | The table is exact; no assumption applies |

### Safety Checklist

- **Hazard.** A reversed LED polarity leaves the lamp dark or reverse-biased; check every anode and cathode against the pin map before applying power.
- **Hazard.** A missing or wrong series resistor can overdrive an LED or the GPIO; measure 220 ohm and 100 ohm before connecting the 3.3 V rail.
- **Hazard.** The blue branch feeds from 3.3 V and sinks into GPIO4; a wiring swap that bypasses `r_blue` could damage the SoC, so verify the resistor is in series on every build.
- **Hazard.** USB power and the board regulator share the 3.3 V rail; do not connect an external 3.3 V supply while USB is attached, and identify the power source before power-up.

## 6. Methodology

The project was scaffolded with `uv run scripts/new_homework 1_3-police-flasher --template arduino`, then implemented as a thin Arduino composition root over the framework-free `police_pattern` library. The shared `common_timer_expired` helper provides wrap-safe deadline handling, and the port GPIO contract keeps the firmware free of direct pin access outside the adapter.

The verification sequence was:

```sh
pio run -d homeworks/1_3-police-flasher
pio test -d homeworks/1_3-police-flasher -e native
uv run scripts/gen_schematic.py homeworks/1_3-police-flasher --all
uv run scripts/gen_schematic.py homeworks/1_3-police-flasher --check
wokwi-cli lint --offline homeworks/1_3-police-flasher/assets/diagram.json
pre-commit run --files homeworks/1_3-police-flasher
```

The build uses PlatformIO [3]. The diagram lint uses the Wokwi offline validator [4]; it consumes no simulation session and produces no behavioural evidence. No bench instrument was connected, so the current, voltage, brightness, and off-state entries remain design calculations and are labeled accordingly.

## 7. Results

The target build completed successfully for `esp32s3_arduino`, the native suite passed every case, and the diagram validator reported no errors. The fast pattern lasts 2210 ms and the slow pattern lasts 4420 ms by calculation.

**Native suite.** `pio test -d homeworks/1_3-police-flasher -e native` ran one suite and seven test cases, all passing. The pattern tests cover the initial red state, deadline boundaries, red/blue alternation, the white strobe phase, the doubled cadence at the cycle boundary, the millisecond wrap, and null-argument handling.

### Measurement Ledger

| ID | Quantity | Value | Label | Instrument | Method | Uncertainty | Implementation commit |
|----|----------|-------|-------|------------|--------|-------------|-----------------------|
| L-01 | Target build status | serial-log: SUCCESS for esp32s3_arduino | measured (observed) | PlatformIO 6.2.0 | pio run -d homeworks/1_3-police-flasher | none: binary pass or fail | f2a1e0f |
| L-02 | Native test result | serial-log: 9 of 9 test cases passed across 2 suites | measured (observed) | Unity 2.6.1 host runner | pio test -d homeworks/1_3-police-flasher -e native | none: binary pass or fail | f2a1e0f |
| L-03 | Diagram validation | serial-log: 1 informational note, 0 errors | measured (observed) | Wokwi CLI 0.28.1 | wokwi-cli lint --offline homeworks/1_3-police-flasher/assets/diagram.json | none: static check | f2a1e0f |
| L-04 | Red branch current | not measured: no bench instrument was connected | not measured | none | C-01 is the design basis | not applicable | f2a1e0f |
| L-05 | Blue branch current | not measured: no bench instrument was connected | not measured | none | C-02 is the design basis | not applicable | f2a1e0f |
| L-06 | White branch current | not measured: no bench instrument was connected | not measured | none | C-03 is the design basis | not applicable | f2a1e0f |
| L-07 | Shared-pin off-state glow | not measured: the visual check requires the physical board | not measured | none | C-06 is the design basis | not applicable | f2a1e0f |
| L-08 | Fast full-pattern duration | calculated: 2210 ms | calculated | none | C-07 sums the fourteen step durations | plus or minus 14 ms from the 1 ms polling tick | f2a1e0f |
| L-09 | Slow full-pattern duration | calculated: 4420 ms | calculated | none | C-07 doubles every fast duration | plus or minus 14 ms from the 1 ms polling tick | f2a1e0f |

L-02 is the historical observation at `f2a1e0f`. The GPIO-contract suite was removed afterwards as duplicate coverage of the top-level `tests/` project; the current tree runs the seven `police_pattern` tests in `test/test_police_pattern/`.

### Traceability Matrix

| ID | Claim or requirement | Design artifact | Verification method | Evidence | Status |
|----|----------------------|-----------------|---------------------|----------|--------|
| T-01 | REPORT-01: red and blue LEDs are driven through series resistors from two GPIO pins. | `src/main.cpp`, `assets/diagram.json` | Target build and diagram integrity check | L-01, L-03 | verified |
| T-02 | REPORT-02: red and blue alternate, and exactly one lamp is selected at a time. | `lib/police_pattern/src/police_pattern.c` | Native test `test_red_and_blue_alternate` | L-02 | verified |
| T-03 | REPORT-03: the sequence repeats continuously. | `lib/police_pattern/src/police_pattern.c` | Native test `test_cycle_boundary_doubles_the_cadence` | L-02 | verified |
| T-04 | REPORT-04: the enriched pattern adds double flashes and a white strobe phase. | `lib/police_pattern/src/police_pattern.c` | Native test `test_white_strobe_has_its_own_phase` | L-02 | verified |
| T-05 | REPORT-05: a third white LED participates in the pattern. | `src/main.cpp`, `assets/diagram.json` | Target build and diagram integrity check | L-01, L-03 | verified |
| T-06 | REPORT-06: the blink speed changes between fast and slow cycles. | `lib/police_pattern/src/police_pattern.c` | Native test `test_cycle_boundary_doubles_the_cadence` and C-07 | L-02, L-08, L-09 | verified |
| T-07 | REPORT-07: the red and blue pair uses only one GPIO. | `assets/diagram.json`, `src/main.cpp` | Manual wiring review and C-04 | C-04, L-03 | manual |
| T-08 | REPORT-08: the report describes the same circuit as the firmware and diagram. | `report.md`, `assets/diagram.json` | Schematic regeneration check and review | L-03 | verified |

## 8. Analysis

The evidence supports the logical claims: the step table selects exactly one pair state per step, the white strobe occupies its own phase, the cycle boundary doubles the cadence, and the deadline arithmetic survives the millisecond wrap. The target build proves that the composition root, the port contracts, the Arduino adapter, and the pattern library link together for the ESP32-S3 environment. It does not prove how bright the lamps are, how much current actually flows, whether the blue LED is visibly lit at 4.0 mA, or whether the high-impedance state produces any glow. Those claims remain pending a bench measurement, and the ledger marks every one of them as not measured.

Industry note: a one-pin two-lamp selector is a useful pin-budget technique, but it converts a simple source-drive circuit into a push-pull or sink-drive design whose off state depends on high impedance rather than on a driven LOW. In production hardware that trade is usually made deliberately, with a leakage bound, a defined power-up state, and a test that proves the off state on the real lamp.

## 9. Conclusions

The firmware satisfies the mandatory and optional behaviours at the code and wiring-model level, and the native suite gives repeatable regression evidence for the pattern. The electrical and optical behaviour is calculated but not measured, so the report does not claim bench verification.

Status: in-progress. The target build, the native suite, and the diagram lint pass; the homework pull request is merged; no bench measurement or simulation session was run. Open items are the bench current and off-state checks and the `hw/1_3-police-flasher` tag.

### Next Steps

- Measure the three branch currents and the shared-pin off-state voltage on the assembled board; close L-04 through L-07 when they are recorded. Owner: the author.
- Tag the merged commit with `scripts/tag_homework.sh 1_3-police-flasher`; the tag closes the Definition of Done.

## 10. References

[1] Espressif Systems, "ESP32-S3 Series Datasheet," Version 1.9, 2024. [Online]. Available: https://www.espressif.com/sites/default/files/documentation/esp32-s3_datasheet_en.pdf
[2] Espressif Systems, "ESP32-S3-DevKitC-1 User Guide," 2024. [Online]. Available: https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32s3/esp32-s3-devkitc-1/user_guide.html
[3] PlatformIO Labs, "PlatformIO Core Documentation," 2026. [Online]. Available: https://docs.platformio.org/
[4] Wokwi, "Wokwi Documentation," 2026. [Online]. Available: https://docs.wokwi.com/

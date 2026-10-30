# Button Contact Bounce Analysis with a Logic Analyzer and a Microcontroller

This report documents a firmware and wiring artifact that measures contact bounce on a
pull-up pushbutton at GPIO 16 of an ESP32-S3-DevKitC-1. The firmware timestamps every edge
through a `CHANGE` interrupt, and the same node is recorded by a Saleae Logic 8-channel
logic analyzer at 24 MS/s. The implementation and the ten-press bench capture are complete.
The raw firmware log is [`assets/measurements/serial.log`](assets/measurements/serial.log)
and the analyzer export is
[`assets/measurements/digital.csv`](assets/measurements/digital.csv); every
measurement-ledger row in section 7 is labelled `measured` or `calculated` from those two
files.

## 1. Title and Metadata

| Field | Value |
|-------|-------|
| Homework ID | 1_5-button-bounce |
| Title | Button Contact Bounce Analysis with a Logic Analyzer and a Microcontroller |
| Board | esp32-s3-devkitc-1 |
| Framework | arduino |
| Language | C++ (cpp) |
| PlatformIO Core | 6.2.0 |
| Platform | espressif32@8.0.0 |
| Homework status | complete |
| Report status | complete |
| Implementation commit | a99da51 |

## 2. Objective

The assignment asks for a pull-up button on GPIO 16, firmware that counts contact state
changes through a hardware interrupt, and a logic analyzer record of the same node during
ten presses made with different speed and force. For every press, the number of bounce
pulses and the bounce duration must be determined, and the analyzer count must be compared
with the firmware count. The final questions are whether the counts agree, when the
microcontroller misses or over-counts, the average bounce duration of this button, and the
minimum sufficient debounce.

This implementation delivers the firmware with its inline capture and analysis logic, the
wiring source of truth, the measurement procedure, and the ten-press capture stored in
`assets/measurements/`. The captured data is reported in section 7 and analyzed in section
8; no result in this report is inferred beyond what those two evidence files contain.

## 3. Assumptions

| ID | Assumption | Impact if wrong | Validation |
|----|------------|-----------------|------------|
| A-01 | A bounce pulse is one falling edge of the active-low signal; total edges are reported separately. | The analyzer edge total would be double the MCU pulse count and the comparison would look wrong. | Every burst reports `falling` and `edges`; the ledger compares the edge total, 65 MCU against 74 analyzer, as the primary result, and the falling-level count, 35 against 37, as a secondary comparison. |
| A-02 | The internal pull-up of about 45 kOhm is adequate for a short breadboard build; no external pull-up is fitted. | A weak pull-up with long leads can pick up noise and create phantom edges. | The analyzer trace must show a clean idle HIGH; an external 10 kOhm resistor is added if it does not. |
| A-03 | The logic analyzer and the board share a ground, and the analyzer input tolerates 3.3 V logic. | A floating reference produces phantom edges and an invalid comparison. | Continuity between analyzer GND and board GND is checked before the capture. |
| A-04 | A press burst ends LOW and a release burst ends HIGH; only press bursts count as press bounce. | Counting release bounce as press bounce inflates the raw falling count. | The `settled` field labels every burst; the ten-press sequence is recorded in the log. |
| A-05 | The bench capture was performed by one operator in a single ten-press session and attached as evidence. | A value that neither evidence file contains would be unsupported. | [`assets/measurements/serial.log`](assets/measurements/serial.log) and [`assets/measurements/digital.csv`](assets/measurements/digital.csv) are attached, and every ledger value is read from them. |
| A-06 | The 20 ms online debounce is a starting threshold; the minimum is derived from the measured HIGH gaps. | A threshold below the measured maximum HIGH gap of 160.625 us would split one press into several. | The 10 ms-clustered analyzer capture gives a 160.625 us maximum HIGH gap, so C-06 derives a 1 ms minimum; the 20 ms window exceeds it. |
| A-07 | The breadboard is mechanical only; the diagram models the same electrical net as a direct connection. | The drawing omits the breadboard but not any electrical node. | A continuity check of the physical build matches the diagram pin map. |
| A-08 | The analyzer samples fast enough to resolve the shortest bounce pulse. | A slower sample rate can miss short pulses and understate the real count. | The Saleae Logic 8-channel captured at 24 MS/s with a 1.65 V threshold and exported to [`assets/measurements/digital.csv`](assets/measurements/digital.csv). |

## 4. Theory

### Bounce model

When the contacts of a mechanical switch meet, they rebound before settling. Each rebound
makes and breaks the circuit, so a single press produces several transitions. Ganssle
measured sixteen switches and found an average bounce of about 1557 us, a maximum of about
6200 us for the sample, and one 157 ms outlier [5]. The duration depends on the switch, the
actuation speed, and the force, so a fixed debounce constant is a compromise rather than a
property of the button.

With the internal pull-up, the released line is HIGH and a press pulls it LOW. A bounce
pulse is a LOW excursion bounded by a falling edge and the following rising edge. The
firmware counts falling edges as pulses and also records the total edge count.

### Capture path

GPIO 16 is configured as `INPUT_PULLUP` through the consumer-owned GPIO contract. The
`CHANGE` interrupt is attached to the same pin [3]. The ISR reads the level and stores a
32-bit `micros()` timestamp in a 256-edge capture. The ISR runs from IRAM and is the only
writer, so it needs no lock. The loop briefly disables interrupts while it copies and clears
the capture, then analyzes it and prints it only after 250 ms without a new edge, so serial
traffic never interleaves with the bounce it describes. The ESP32-S3 also offers
a hardware glitch filter of two sample-clock cycles [4]; it is not enabled because the
assignment must expose the raw bounce rather than suppress it.

### Debounce criterion

The online path feeds the raw level to `common_debounce_update` with a 20 ms window. The
firmware derives the minimum window from the captured burst itself. A window accepts a
candidate once `elapsed >= stable_ms`, so a HIGH interval of exactly the window length would
be accepted and create an extra transition. The smallest safe window is therefore the
longest HIGH interval plus one millisecond:

`min_stable_ms = floor(max_high_us / 1000) + 1`

A burst with no HIGH interval needs no debounce and reports 0.

### Limitations

The ISR cannot see a pulse shorter than its entry latency, and the `micros()` timestamp has
one-microsecond granularity; the analyzer samples independently and can see more. The
capture holds 256 edges, so a pathological burst is marked `overflow=1` and is incomplete.
The burst dump blocks the loop while it prints, so the operator must wait for `READY`. The
firmware does not measure the analog edge shape, the contact resistance, or the exact
analyzer threshold; it records digital transitions only. The 32-bit microsecond timestamp
wraps after about 71.6 minutes, and all differences are computed modulo 2^32. In this capture
the ISR recorded 65 of the analyzer's 74 transitions. At 24 MS/s the analyzer resolves
41.7 ns, so the measured 0.25 us press event spans six samples. The 250 ms quiet-gap
segmentation merges rapid presses, so per-event bounce metrics are taken from a 10 ms
cluster over the analyzer transitions rather than from a single `BURST` duration.

## 5. Hardware and Wiring

The wiring source of truth is [`assets/diagram.json`](assets/diagram.json); the visual
breadboard diagram is [`assets/wiring.png`](assets/wiring.png), and the generated
IEEE vector view is [`assets/schematic.svg`](assets/schematic.svg). One side of the
pushbutton connects to GPIO 16 (header J3, pin 9) and the other side to GND. GPIO 16 is an
input with the internal pull-up, so the line is HIGH when released and LOW when pressed.
Channel 1 (`D0`) of the logic analyzer connects to the same GPIO 16 node, and the analyzer
GND connects to the board GND.

### Bill of Materials

| Ref | Part or value | Quantity | Package | Source or link | Notes |
|-----|---------------|----------|---------|----------------|-------|
| esp | ESP32-S3-DevKitC-1 with ESP32-S3-WROOM-1, 16 MB flash, 8 MB octal PSRAM | 1 | Board | [2] | Target board; GPIO 16 is on J3-9. |
| btn | Momentary pushbutton, normally open | 1 | THT | Bench stock; no datasheet | Contact bounce is measured in situ. |
| la | Logic analyzer, 8-channel, 3.3 V compatible | 1 | Instrument | Bench instrument; see [6] for the method | Saleae Logic 8-channel, 24 MS/s; D0 on GPIO 16; GND to board GND. |

### Pin Map

| Signal | Pin | Connects to | Notes |
|--------|-----|-------------|-------|
| Button contact A | GPIO 16 (J3-9) | btn:1.l | Internal pull-up; active low. |
| Button contact B | GND | btn:2.l | Return. |
| Analyzer channel 1 | GPIO 16 (J3-9) | la:D0 | Same electrical node as the button. |
| Analyzer ground | GND | la:GND | Common ground with the board. |

### Electrical Calculations

| ID | Quantity | Formula | Units | Input provenance | Result | Uncertainty | Assumption effect |
|----|----------|---------|-------|------------------|--------|-------------|-------------------|
| C-01 | Pull-up current when pressed | I = V / R | uA | V = 3.3 V; R = 45 kOhm typical from [1] | 73.3 | The datasheet row gives a typical value only | A-02; a weaker pull-up lowers the current but keeps the logic level valid. |
| C-02 | RC rise time of the released line | t = R * C | us | R = 45 kOhm from [1]; C = 100 pF estimated lead and input capacitance | 4.5 | C is an estimate, not a measurement | A-07 and A-08; larger capacitance slows the edge and shifts the threshold crossing. |
| C-03 | Minimum debounce for a burst | W = floor(max_high_us / 1000) + 1 | ms | Per-burst `max_high_us`; criterion from [5] | Per burst | 1 ms quantization and the `micros()` resolution | A-01 and A-06; a longer HIGH gap raises the minimum. |
| C-04 | Debounce margin over the published maximum | M = 20 ms / 6.2 ms | ratio | 20 ms chosen window; 6200 us maximum in [5]; 1 ms measured minimum from C-06 | 3.2 published; 20 measured | Ganssle's switch sample, not this button | A-06; 20 ms is 3.2x the published maximum and 20x the C-06 minimum and about 124x the measured HIGH gap. |
| C-05 | Serial dump time for a full capture | t = N * B / (baud / 10) | s | N = 256 edges; B = 20 bytes per line; 115200 baud | 0.44 | Line length varies with the timestamp width | A-05; a full capture blocks the loop for about 0.44 s, so the operator waits for `READY`. |
| C-06 | Minimum debounce from the measured maximum HIGH gap | W = floor(max_high_us / 1000) + 1 | ms | max_high_us = 160.625 us from the 10 ms-clustered analyzer capture, assets/measurements/digital.csv; criterion from [5] | 1 | 1 ms quantization; 41.7 ns analyzer sample interval at 24 MS/s | A-06; 20 ms is 20x this measured minimum and about 124x the measured HIGH gap. |

### Safety Checklist

- **Hazard.** 3.3 V logic only: a 5 V signal or a 5 V analyzer pull-up on GPIO 16 can damage the ESP32-S3 input; check the analyzer voltage before connecting.
- **Hazard.** Floating reference: connect the analyzer GND to the board GND before probing; a missing ground produces phantom edges.
- **Hazard.** Short circuit: verify that the button is between GPIO 16 and GND, not between 3.3 V and GND, before applying power.
- **Hazard.** Back-feed: disconnect USB before connecting an external supply, and never power the board from two sources at once.

## 6. Methodology

The target is built with `pio run -d homeworks/1_5-button-bounce`; the homework has no host
test suite. The node at GPIO 16 was recorded with a Saleae Logic 8-channel analyzer at
24 MS/s, a 1.65 V threshold, and channel `D0` tied to the same node; its ground is tied to
the board ground. The capture spans a delta-T of 12.364 s and holds 74 transitions, 37
falling and 37 rising, exported to
[`assets/measurements/digital.csv`](assets/measurements/digital.csv). The serial monitor runs
at 115200 baud.

The operator waits for `READY`, then presses the button ten times with different speed and
force. Each press produces one or more `BURST` lines. A press burst ends `settled=LOW`; the
matching release burst ends `settled=HIGH`. For each press, the press and release `BURST`
lines are paired with the analyzer clusters formed by a 10 ms gap over the exported `E`
transitions; a bounce event is a multi-transition cluster, and its duration is the
first-to-last span of that cluster. The minimum debounce is taken from the largest HIGH
interval inside a bounce cluster. The raw `BURST` `duration_us` and `min_stable_ms` are not
used as per-event metrics, because the 250 ms quiet gap merges rapid presses into one burst.

The two sources count differently. The firmware's `falling` and `rising` fields count the
level read at each ISR entry, not the transition direction, whereas the analyzer reports true
transitions. The edge total is therefore the primary comparison, 65 MCU edges against 74
analyzer edges; the falling-level comparison, 35 against 37, is secondary and carries that
caveat.

The firmware path is a `CHANGE` interrupt on GPIO 16, a 32-bit `micros()` timestamp per
edge, a 256-edge capture, a burst dump after 250 ms of quiet, and an online
`common_debounce_update` path with a 20 ms window. The interrupt, the interrupt-disable window
around the drain, the 256-edge capture, and the burst analysis all live in `src/main.cpp`;
the analysis is compiled only into the target and has no host test. No simulation was run,
and no Wokwi session quota was consumed.

## 7. Results

The target build succeeds for `esp32s3_arduino`. The schematic check exits 0, and the offline
Wokwi lint reports only the informational `unsupported-part` note for the ESP32-S3 board. The
ten-press capture is complete: over a 12.364 s analyzer window the export holds 74
transitions (37 falling, 37 rising), while the firmware `TOTAL` line reports 65 edges (35
falling-level, 30 rising-level), a difference of -9 edges (-12.2%). Five bounce events were
measured, one press-phase event of 0.25 us and four release-phase events between 305.5 us and
3780.25 us, with a mean of 978.1 us; the 160.625 us maximum HIGH gap yields a 1 ms minimum
sufficient debounce. The raw firmware log is
[`assets/measurements/serial.log`](assets/measurements/serial.log) and the analyzer export is
[`assets/measurements/digital.csv`](assets/measurements/digital.csv).

**Test coverage.** The homework ships no host test suite; the capture and the burst
analysis are compiled into the target only. The ten-press bench capture in
`assets/measurements/` is the verification path for their arithmetic: the firmware log and
the analyzer export are compared press by press in the ledger below.

### Measurement Ledger

| ID | Quantity | Value | Label | Instrument | Method | Uncertainty | Implementation commit |
|----|----------|-------|-------|------------|--------|-------------|-----------------------|
| L-01 | Press 1 edges and bounce | serial-log: MCU 4 edges (falling-level 3); digital.csv: analyzer 6 edges (3 falling); release bounce 363.167 us | measured | Saleae Logic 8-channel at 24 MS/s; ESP32-S3 CHANGE ISR | Pair the press and release BURST lines with the analyzer clusters | 41.7 ns analyzer sample interval; ISR entry latency and 1 us micros resolution | a99da51 |
| L-02 | Press 2 edges and bounce | serial-log: MCU 2 edges (falling-level 1); digital.csv: analyzer 2 edges (1 falling); no bounce | measured | Saleae Logic 8-channel at 24 MS/s; ESP32-S3 CHANGE ISR | Pair the press and release BURST lines with the analyzer clusters | 41.7 ns analyzer sample interval; ISR entry latency and 1 us micros resolution | a99da51 |
| L-03 | Press 3 edges and bounce | serial-log: MCU 18 edges (falling-level 9); digital.csv: analyzer 20 edges (10 falling); release bounce 3780.25 us | measured | Saleae Logic 8-channel at 24 MS/s; ESP32-S3 CHANGE ISR | Pair the press and release BURST lines with the analyzer clusters | 41.7 ns analyzer sample interval; ISR entry latency and 1 us micros resolution | a99da51 |
| L-04 | Press 4 edges and bounce | serial-log: MCU 2 edges (falling-level 1); digital.csv: analyzer 2 edges (1 falling); no bounce | measured | Saleae Logic 8-channel at 24 MS/s; ESP32-S3 CHANGE ISR | Pair the press and release BURST lines with the analyzer clusters | 41.7 ns analyzer sample interval; ISR entry latency and 1 us micros resolution | a99da51 |
| L-05 | Press 5 edges and bounce | serial-log: MCU 2 edges (falling-level 1); digital.csv: analyzer 4 edges (2 falling); press bounce 0.25 us | measured | Saleae Logic 8-channel at 24 MS/s; ESP32-S3 CHANGE ISR | Pair the press and release BURST lines with the analyzer clusters | 41.7 ns analyzer sample interval; ISR entry latency and 1 us micros resolution | a99da51 |
| L-06 | Press 6 edges and bounce | serial-log: MCU 2 edges (falling-level 1); digital.csv: analyzer 2 edges (1 falling); no bounce | measured | Saleae Logic 8-channel at 24 MS/s; ESP32-S3 CHANGE ISR | Pair the press and release BURST lines with the analyzer clusters | 41.7 ns analyzer sample interval; ISR entry latency and 1 us micros resolution | a99da51 |
| L-07 | Press 7 edges and bounce | serial-log: MCU 2 edges (falling-level 1); digital.csv: analyzer 2 edges (1 falling); no bounce | measured | Saleae Logic 8-channel at 24 MS/s; ESP32-S3 CHANGE ISR | Pair the press and release BURST lines with the analyzer clusters | 41.7 ns analyzer sample interval; ISR entry latency and 1 us micros resolution | a99da51 |
| L-08 | Press 8 edges and bounce | serial-log: MCU 25 edges (falling-level 14); digital.csv: analyzer 28 edges (14 falling); release bounce 305.5 us | measured | Saleae Logic 8-channel at 24 MS/s; ESP32-S3 CHANGE ISR | Pair the press and release BURST lines with the analyzer clusters | 41.7 ns analyzer sample interval; ISR entry latency and 1 us micros resolution | a99da51 |
| L-09 | Press 9 edges and bounce | serial-log: MCU 6 edges (falling-level 3); digital.csv: analyzer 6 edges (3 falling); release bounce 441.333 us | measured | Saleae Logic 8-channel at 24 MS/s; ESP32-S3 CHANGE ISR | Pair the press and release BURST lines with the analyzer clusters | 41.7 ns analyzer sample interval; ISR entry latency and 1 us micros resolution | a99da51 |
| L-10 | Press 10 edges and bounce | serial-log: MCU 2 edges (falling-level 1); digital.csv: analyzer 2 edges (1 falling); no bounce | measured | Saleae Logic 8-channel at 24 MS/s; ESP32-S3 CHANGE ISR | Pair the press and release BURST lines with the analyzer clusters | 41.7 ns analyzer sample interval; ISR entry latency and 1 us micros resolution | a99da51 |
| L-11 | Mean bounce duration (five events) | serial-log: ten-press sequence; digital.csv: mean 978.1 us across 5 bounce events; release-only mean 1222.6 us | measured | Saleae Logic 8-channel at 24 MS/s | Arithmetic mean of the five measured bounce-event durations | Event spread 0.25 us to 3780.25 us; one press-phase and four release-phase events | a99da51 |
| L-12 | Minimum sufficient debounce | 1 ms from C-06 | calculated | Saleae Logic 8-channel at 24 MS/s | C-06 applied to the 160.625 us maximum HIGH gap | 1 ms quantization; 41.7 ns analyzer sample interval | a99da51 |
| L-13 | MCU versus analyzer edge count | serial-log: MCU 65 edges (falling-level 35); digital.csv: analyzer 74 edges (37 falling); difference -9 edges (-12.2%) | measured | Saleae Logic 8-channel at 24 MS/s; ESP32-S3 CHANGE ISR | Compare the TOTAL line with the analyzer transition total over the same capture | ISR entry latency and 1 us micros resolution; the firmware counts the level at ISR entry while the analyzer counts true transitions | a99da51 |

### Traceability Matrix

| ID | Claim or requirement | Design artifact | Verification method | Evidence | Status |
|----|----------------------|-----------------|---------------------|----------|--------|
| T-01 | REPORT-01: the homework has a ten-section report with identity and metadata. | `homework.yaml`, `report.md` section 1 | Metadata checker and review | `homework.yaml`; section 1 | verified |
| T-02 | REPORT-02: the objective and acceptance criteria are stated. | `task.md`, `README.md` | Review | `task.md`; acceptance criteria | verified |
| T-03 | REPORT-03: every assumption has an impact and a validation. | Report section 3 | Review | A-01, A-02, A-03, A-04, A-05, A-06, A-07, A-08 | verified |
| T-04 | REPORT-04: the theory explains bounce, capture, debounce, and limitations. | Report section 4 | Review against [1], [3], [4], [5] | Sections 4 and 4.1 | verified |
| T-05 | REPORT-05: hardware, BOM, pin map, calculations, and safety are complete. | `assets/diagram.json`, `assets/schematic.svg`, report section 5 | `gen_schematic.py --check`; `wokwi-cli lint --offline` | Diagram and schematic | verified |
| T-06 | REPORT-06: the methodology is reproducible. | `README.md`, report section 6 | Review of the serial protocol and procedure | README and section 6 | verified |
| T-07 | REPORT-07: results carry honest evidence labels and traceability. | Report section 7 | Review of the ledger and matrix | L-01 through L-13; T-01 through T-12 | verified |
| T-08 | REPORT-08: analysis, conclusions, and references close the argument. | Report sections 8, 9, 10 | Review | Sections 8 to 10 | verified |
| T-09 | The firmware records every edge with a microsecond timestamp. | `src/main.cpp` | Target build and review of the ISR capture path | L-13; src/main.cpp | manual |
| T-10 | The firmware count and the analyzer count are compared for ten presses. | Report ledger and procedure | Bench capture by the owner | L-01 through L-13 | verified |
| T-11 | The minimum debounce is derived from the measured bursts. | `min_stable_ms` in `src/main.cpp` | Bench capture | C-03; C-06; L-12 | verified |
| T-12 | The schematic matches the wiring source of truth. | `assets/diagram.json` | `gen_schematic.py --check` | `assets/schematic.svg` | verified |

## 8. Analysis

The firmware recorded 65 edges against the analyzer's 74 over the same ten presses, a
difference of -9 edges (-12.2%). The microcontroller never over-counts: in every press the
MCU edge count is less than or equal to the analyzer count. Presses 2, 4, 6, 7, 9 and 10
agree exactly, while presses 1, 3, 5 and 8 miss 2, 2, 2 and 3 edges respectively. The misses
are edges that fall below the ISR's entry latency or collide inside the one-microsecond
`micros()` resolution; the analyzer at 24 MS/s resolves 41.7 ns and sees them. The
falling-level comparison, 35 MCU against 37 analyzer, is secondary: the firmware counts the
level read at ISR entry while the analyzer counts true transition direction, so the edge total
is the reliable comparison.

Bounce is concentrated in five events. Press 5 shows one press-phase event of 0.25 us;
presses 1, 3, 8 and 9 show release-phase events of 363.167 us, 3780.25 us, 305.5 us and
441.333 us. The mean over the five events is 978.1 us, and the release-only mean is 1222.6
us. Presses 2, 4, 6, 7 and 10 produced no multi-transition cluster at all. The firmware's
final burst reports `duration_us=1797561` and `min_stable_ms=237`, but the 250 ms quiet gap
merged presses 6 to 10 into that burst, so neither figure is a single-bounce metric; the
per-event values come from the 10 ms cluster analysis of the analyzer export.

The largest HIGH interval inside a bounce cluster is 160.625 us. C-06 rounds that up to the
next millisecond, so the minimum sufficient debounce is 1 ms. The 20 ms online window is 20
times that derived minimum and about 124 times the measured gap, which explains why the
debounced press count settles at ten while the raw edges keep bouncing.

Industry note: debounce is a property of the specific switch and its actuation, not a
universal constant. Ganssle found that identical switches can differ by a factor of two and
that one sample produced a 157 ms bounce [5]. A timestamped edge capture, rather than a
throttled counter print, is the diagnostic that makes the difference visible; the same
principle applies to any mechanical input, from a keypad to a limit switch.

## 9. Conclusions

The measured answers are: the firmware count does not agree exactly with the analyzer count,
at 65 against 74 edges (-9, -12.2%); the microcontroller under-counts by 2, 2, 2 and 3 edges
in presses 1, 3, 5 and 8 and never over-counts; the mean bounce duration is 978.1 us across
the five events, or 1222.6 us for the four release-phase events alone; and the minimum
sufficient debounce is 1 ms, derived from the 160.625 us maximum HIGH gap.

The deliverable is a working measurement instrument: a `CHANGE`-interrupt capture with
microsecond timestamps, an in-firmware analyzer, a debounced counter, a wiring model, and a
repeatable ten-press procedure that produced a complete data set. The target build is green.

Status: the implementation is committed at a99da51. The target build, the schematic check,
and the offline diagram lint are green. The ten-press capture is attached as
[`assets/measurements/serial.log`](assets/measurements/serial.log) and
[`assets/measurements/digital.csv`](assets/measurements/digital.csv), and every ledger row is
labelled `measured` or `calculated`. The `hw/1_5-button-bounce` tag has not been created by
this change.

### Next Steps

1. Maintainer: open the pull request for this change and run the local gates. The step closes when the metadata checker, the target build, and pre-commit are green.
2. Maintainer: merge the pull request after the required `gate` check is green. The step closes when the change is on the default branch.
3. Owner: create the `hw/1_5-button-bounce` tag through `scripts/tag_homework.sh` after the merge. The step closes when the tag exists on the merged commit.

## 10. References

[1] Espressif Systems, "ESP32-S3 Series Datasheet," Espressif Systems. [Online]. Available: https://www.espressif.com/sites/default/files/documentation/esp32-s3_datasheet_en.pdf. [Accessed: Oct. 28, 2026].

[2] Espressif Systems, "ESP32-S3-DevKitC-1 v1.1 User Guide," Espressif Systems. [Online]. Available: https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32s3/esp32-s3-devkitc-1/user_guide_v1.1.html. [Accessed: Oct. 28, 2026].

[3] Espressif Systems, "GPIO," Arduino ESP32 documentation. [Online]. Available: https://docs.espressif.com/projects/arduino-esp32/en/latest/api/gpio.html. [Accessed: Oct. 28, 2026].

[4] Espressif Systems, "GPIO & RTC GPIO," ESP-IDF Programming Guide (ESP32-S3). [Online]. Available: https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/gpio.html. [Accessed: Oct. 28, 2026].

[5] J. Ganssle, "Debouncing Contacts and Switches," The Ganssle Group. [Online]. Available: https://www.ganssle.com/debouncing.htm. [Accessed: Oct. 28, 2026].

[6] Pico Technology, "What is switch bounce & how to implement debounce," Oct. 3, 2024. [Online]. Available: https://www.picotech.com/library/articles/blog/what-is-switch-bounce-how-to-implement-debounce. [Accessed: Oct. 28, 2026].

## Decision Appendix

The owner accepted all four recommendations on 2026-10-28. The accepted assumptions are
A-01, A-02, A-04, and A-06.

| Requirement | Authority | Conflict or risk | Recommendation | Decision |
|-------------|-----------|------------------|----------------|----------|
| Count contact state changes; the sample counts only `FALLING` edges. | [3]; the assignment wording | Falling-only counting cannot see the contact return, and the analyzer edge total is ambiguous. | Attach `CHANGE`, log the level and `micros()` for every edge, and derive the falling count. | Accepted: the firmware logs both edges and reports falling and total counts separately. |
| The sample prints only the latest counter every 10 ms. | [5]; [3] | Intermediate bounce counts never appear as separate lines, so the serial log cannot be compared pulse by pulse. | Let the ISR fill a timestamp capture and dump the burst after a quiet gap. | Accepted: a 256-edge capture and a 250 ms quiet-gap dump. |
| `INPUT_PULLUP` is used without a stated common ground; the analyzer is connected directly. | [1], which gives 45 kOhm typical; [6] | A weak pull-up on a breadboard can pick up noise, and a missing ground floats the analyzer reference. | Keep `INPUT_PULLUP`, require a common ground and 3.3 V logic, and document an optional external 10 kOhm. | Accepted: the internal pull-up is used, the common ground is mandatory, and the external resistor is optional. |
| The sample has no debounce path, but the minimum debounce must be justified. | [5] | Without a second path there is no measured answer to the debounce question. | Add an online `common_debounce_update` path and an offline minimum-window calculation. | Accepted: a 20 ms online path and the per-burst `min_stable_ms` calculation. |

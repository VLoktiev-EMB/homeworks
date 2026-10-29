# Button Contact Bounce Analysis with a Logic Analyzer and a Microcontroller

This report documents a firmware and wiring artifact that measures contact bounce on a
pull-up pushbutton at GPIO 16 of an ESP32-S3-DevKitC-1. The firmware timestamps every edge
through a `CHANGE` interrupt, and the same node is recorded by channel 1 of a logic
analyzer. The implementation is complete and verified by a target build and a schematic
check. The ten-press bench capture that turns the measurement ledger from `not measured` into
`measured` is the remaining owner action.

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
| Homework status | in-progress |
| Report status | draft |
| Implementation commit | 66f966b |

## 2. Objective

The assignment asks for a pull-up button on GPIO 16, firmware that counts contact state
changes through a hardware interrupt, and a logic analyzer record of the same node during
ten presses made with different speed and force. For every press, the number of bounce
pulses and the bounce duration must be determined, and the analyzer count must be compared
with the firmware count. The final questions are whether the counts agree, when the
microcontroller misses or over-counts, the average bounce duration of this button, and the
minimum sufficient debounce.

This implementation delivers the firmware with its inline capture and analysis logic, the
wiring source of truth, and the measurement procedure. It does not
fabricate the ten-press result: the ledger rows stay `not measured` until the owner captures
the serial log and the analyzer trace.

## 3. Assumptions

| ID | Assumption | Impact if wrong | Validation |
|----|------------|-----------------|------------|
| A-01 | A bounce pulse is one falling edge of the active-low signal; total edges are reported separately. | The analyzer edge total would be double the MCU pulse count and the comparison would look wrong. | Every burst reports `falling` and `edges`; the ledger compares falling edges with the analyzer falling count. |
| A-02 | The internal pull-up of about 45 kOhm is adequate for a short breadboard build; no external pull-up is fitted. | A weak pull-up with long leads can pick up noise and create phantom edges. | The analyzer trace must show a clean idle HIGH; an external 10 kOhm resistor is added if it does not. |
| A-03 | The logic analyzer and the board share a ground, and the analyzer input tolerates 3.3 V logic. | A floating reference produces phantom edges and an invalid comparison. | Continuity between analyzer GND and board GND is checked before the capture. |
| A-04 | A press burst ends LOW and a release burst ends HIGH; only press bursts count as press bounce. | Counting release bounce as press bounce inflates the raw falling count. | The `settled` field labels every burst; the ten-press sequence is recorded in the log. |
| A-05 | The bench capture is performed by the owner after handoff. | The report would claim measurements that never happened. | The serial log and the analyzer capture are attached and cited in the ledger before a row changes to `measured`. |
| A-06 | The 20 ms online debounce is a starting threshold; the minimum is derived per burst. | A threshold below the measured maximum HIGH gap would split one press into several. | Each burst reports `min_stable_ms`; the threshold is raised if any burst exceeds 20 ms. |
| A-07 | The breadboard is mechanical only; the diagram models the same electrical net as a direct connection. | The drawing omits the breadboard but not any electrical node. | A continuity check of the physical build matches the diagram pin map. |
| A-08 | The analyzer samples at 10 MS/s or faster with a 1.65 V threshold. | A slower sample rate can miss short pulses and understate the real count. | The analyzer settings are recorded in the capture metadata. |

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
wraps after about 71.6 minutes, and all differences are computed modulo 2^32. No bench data
exists yet, so the quantitative answers remain open.

## 5. Hardware and Wiring

The wiring source of truth is [`assets/diagram.json`](assets/diagram.json); the generated
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
| la | Logic analyzer, 8-channel, 3.3 V compatible | 1 | Instrument | Bench instrument; see [6] for the method | D0 on GPIO 16; GND to board GND. |

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
| C-04 | Debounce margin over the published maximum | M = 20 ms / 6.2 ms | ratio | 20 ms chosen window; 6200 us maximum in [5] | 3.2 | Ganssle's switch sample, not this button | A-06; the margin is a starting point, not a guarantee. |
| C-05 | Serial dump time for a full capture | t = N * B / (baud / 10) | s | N = 256 edges; B = 20 bytes per line; 115200 baud | 0.44 | Line length varies with the timestamp width | A-05; a full capture blocks the loop for about 0.44 s, so the operator waits for `READY`. |

### Safety Checklist

- **Hazard.** 3.3 V logic only: a 5 V signal or a 5 V analyzer pull-up on GPIO 16 can damage the ESP32-S3 input; check the analyzer voltage before connecting.
- **Hazard.** Floating reference: connect the analyzer GND to the board GND before probing; a missing ground produces phantom edges.
- **Hazard.** Short circuit: verify that the button is between GPIO 16 and GND, not between 3.3 V and GND, before applying power.
- **Hazard.** Back-feed: disconnect USB before connecting an external supply, and never power the board from two sources at once.

## 6. Methodology

The target is built with `pio run -d homeworks/1_5-button-bounce`; the homework has no host
test suite. The analyzer is configured for a sample rate of at least 10 MS/s, a 1.65 V
threshold, and channel `D0` on GPIO 16; its ground is tied to the board ground. The serial
monitor runs at 115200 baud.

The operator waits for `READY`, then presses the button ten times with different speed and
force. Each press produces one or more `BURST` lines. A press burst ends `settled=LOW`; the
matching release burst ends `settled=HIGH`. For each press burst the operator records the
falling-edge count, the first-to-last edge duration, the longest HIGH gap, and
`min_stable_ms`, and compares the falling count with the analyzer's falling-edge count for
the same interval. The analyzer's own counting convention must be stated: if it reports
all edges, the pulse count is half of that total.

The firmware path is a `CHANGE` interrupt on GPIO 16, a 32-bit `micros()` timestamp per
edge, a 256-edge capture, a burst dump after 250 ms of quiet, and an online
`common_debounce_update` path with a 20 ms window. The interrupt, the interrupt-disable window
around the drain, the 256-edge capture, and the burst analysis all live in `src/main.cpp`;
the analysis is compiled only into the target and has no host test. No simulation was run,
and no Wokwi session quota was consumed.

## 7. Results

The target build succeeds for `esp32s3_arduino`. The schematic check exits 0, and the offline
Wokwi lint reports only the informational `unsupported-part` note for the ESP32-S3 board. The
ten-press bench capture has not yet been performed, so every measurement-ledger row is
labeled `not measured` with the reason.

**Test coverage.** The homework ships no host test suite; the capture and the burst
analysis are compiled into the target only. The bench procedure in section 6 is the
verification path for their arithmetic, so the implementation has no automated host check.

### Measurement Ledger

| ID | Quantity | Value | Label | Instrument | Method | Uncertainty | Implementation commit |
|----|----------|-------|-------|------------|--------|-------------|-----------------------|
| L-01 | Press 1 falling-edge count | not measured: bench capture pending | not measured | none | Analyzer channel 1 and the serial `BURST` line | Analyzer sample interval and ISR latency | 66f966b |
| L-02 | Press 2 falling-edge count | not measured: bench capture pending | not measured | none | Analyzer channel 1 and the serial `BURST` line | Analyzer sample interval and ISR latency | 66f966b |
| L-03 | Press 3 falling-edge count | not measured: bench capture pending | not measured | none | Analyzer channel 1 and the serial `BURST` line | Analyzer sample interval and ISR latency | 66f966b |
| L-04 | Press 4 falling-edge count | not measured: bench capture pending | not measured | none | Analyzer channel 1 and the serial `BURST` line | Analyzer sample interval and ISR latency | 66f966b |
| L-05 | Press 5 falling-edge count | not measured: bench capture pending | not measured | none | Analyzer channel 1 and the serial `BURST` line | Analyzer sample interval and ISR latency | 66f966b |
| L-06 | Press 6 falling-edge count | not measured: bench capture pending | not measured | none | Analyzer channel 1 and the serial `BURST` line | Analyzer sample interval and ISR latency | 66f966b |
| L-07 | Press 7 falling-edge count | not measured: bench capture pending | not measured | none | Analyzer channel 1 and the serial `BURST` line | Analyzer sample interval and ISR latency | 66f966b |
| L-08 | Press 8 falling-edge count | not measured: bench capture pending | not measured | none | Analyzer channel 1 and the serial `BURST` line | Analyzer sample interval and ISR latency | 66f966b |
| L-09 | Press 9 falling-edge count | not measured: bench capture pending | not measured | none | Analyzer channel 1 and the serial `BURST` line | Analyzer sample interval and ISR latency | 66f966b |
| L-10 | Press 10 falling-edge count | not measured: bench capture pending | not measured | none | Analyzer channel 1 and the serial `BURST` line | Analyzer sample interval and ISR latency | 66f966b |
| L-11 | Mean bounce duration across ten presses | not measured: bench capture pending | not measured | none | Mean of the ten `duration_us` values | Spread of the ten values | 66f966b |
| L-12 | Minimum sufficient debounce | not measured: bench capture pending | not measured | none | Maximum of the ten `min_stable_ms` values | 1 ms quantization and microsecond resolution | 66f966b |
| L-13 | MCU versus analyzer falling-edge count | not measured: bench capture pending | not measured | none | Pair each `BURST` line with the analyzer trace | Analyzer threshold and ISR latency | 66f966b |

### Traceability Matrix

| ID | Claim or requirement | Design artifact | Verification method | Evidence | Status |
|----|----------------------|-----------------|---------------------|----------|--------|
| T-01 | REPORT-01: the homework has a ten-section report with identity and metadata. | `homework.yaml`, `report.md` section 1 | Metadata checker and review | `homework.yaml`; section 1 | verified |
| T-02 | REPORT-02: the objective and acceptance criteria are stated. | `task.md`, `README.md` | Review | `task.md`; acceptance criteria | verified |
| T-03 | REPORT-03: every assumption has an impact and a validation. | Report section 3 | Review | A-01, A-02, A-03, A-04, A-05, A-06, A-07, A-08 | verified |
| T-04 | REPORT-04: the theory explains bounce, capture, debounce, and limitations. | Report section 4 | Review against [1], [3], [4], [5] | Sections 4 and 4.1 | verified |
| T-05 | REPORT-05: hardware, BOM, pin map, calculations, and safety are complete. | `assets/diagram.json`, `assets/schematic.svg`, report section 5 | `gen_schematic.py --check`; `wokwi-cli lint --offline` | Diagram and schematic | verified |
| T-06 | REPORT-06: the methodology is reproducible. | `README.md`, report section 6 | Review of the serial protocol and procedure | README and section 6 | verified |
| T-07 | REPORT-07: results carry honest evidence labels and traceability. | Report section 7 | Review of the ledger and matrix | L-01 through L-13; T-01 through T-12 | pending |
| T-08 | REPORT-08: analysis, conclusions, and references close the argument. | Report sections 8, 9, 10 | Review | Sections 8 to 10 | verified |
| T-09 | The firmware records every edge with a microsecond timestamp. | `src/main.cpp` | Target build and review of the ISR capture path | `src/main.cpp` | manual |
| T-10 | The firmware count and the analyzer count are compared for ten presses. | Report ledger and procedure | Bench capture by the owner | L-01 through L-13 | pending |
| T-11 | The minimum debounce is derived from the measured bursts. | `min_stable_ms` in `src/main.cpp` | Bench capture | C-03; L-12 | pending |
| T-12 | The schematic matches the wiring source of truth. | `assets/diagram.json` | `gen_schematic.py --check` | `assets/schematic.svg` | verified |

## 8. Analysis

The evidence currently supports the build, the wiring model, and the schematic consistency.
It does not yet support a quantitative answer to the four assignment questions, because the
ten-press capture has not been made.

The expected relationship is that the MCU falling count is less than or equal to the
analyzer falling count for the same press burst. The ISR can miss a pulse shorter than its
entry latency, and `micros()` cannot resolve two edges inside one microsecond, while the
analyzer samples independently. An apparent over-count has two likely causes. First, the
raw falling count also includes the release burst, because a released contact bounces on
the way back to HIGH; the `settled` field separates the two burst types. Second, noise or a
threshold that chatters on a slow RC edge can add edges that the analyzer, with a different
threshold, does not see. The report therefore compares press bursts only and states the
analyzer counting convention.

The 20 ms online window is about 3.2 times the 6200 us maximum in Ganssle's sample [5], so
it should collapse a typical button's bounce into one press. It is not a proof for this
button: if a measured burst reports `max_high_us` above 20 ms, the window must be raised to
that burst's `min_stable_ms`. The offline criterion C-03 makes that decision from the
trace rather than from a constant.

Industry note: debounce is a property of the specific switch and its actuation, not a
universal constant. Ganssle found that identical switches can differ by a factor of two and
that one sample produced a 157 ms bounce [5]. A timestamped edge capture, rather than a
throttled counter print, is the diagnostic that makes the difference visible; the same
principle applies to any mechanical input, from a keypad to a limit switch.

## 9. Conclusions

The deliverable is a working measurement instrument: a `CHANGE`-interrupt capture with
microsecond timestamps, an in-firmware analyzer, a debounced counter, a wiring model, and a
repeatable ten-press procedure. The target build is green. The four assignment questions
remain open only because the bench capture is pending; the report gives the exact comparison
and reduction that will answer them.

Status: the implementation is committed at 66f966b. The target build, the schematic check,
and the offline diagram lint are green. The ten-press bench capture and the measured ledger
are pending on the owner; the report is a draft, and no row is claimed as measured until the
serial log and the analyzer trace exist.

### Next Steps

1. Owner: capture ten presses with the serial log and the analyzer trace, and attach both to the homework. The step closes when both files are cited in the ledger.
2. Owner: replace the `not measured` rows L-01 through L-13 with the captured values and recompute the mean and the minimum debounce. The step closes when no `not measured` row remains.
3. Owner: set the report status to complete and the homework status to complete after the capture, then re-run the metadata and pre-commit gates. The step closes when both gates are green.
4. Maintainer: open the pull request, squash-merge it, and create the `hw/1_5-button-bounce` tag through `scripts/tag_homework.sh`. The step closes when the pull request is merged and the tag exists.

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

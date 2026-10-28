# Button Contact Bounce Analysis with a Logic Analyzer and a Microcontroller

Independent PlatformIO homework for `1_5-button-bounce`. It measures contact bounce on a
pull-up pushbutton, records every edge on GPIO 16, and compares the firmware count with a
logic analyzer capture of the same node.

**Status:** in-progress. Firmware, native tests, and wiring are complete. Bench
measurements are pending, so the report labels them `not measured` until they are captured.

- [Assignment paraphrase](task.md)
- [Report](report.md)
- [Wiring source of truth](assets/diagram.json)
- [IEEE vector schematic](assets/schematic.svg)

## Wiring

| Signal | ESP32-S3 pin | Connects to |
|--------|--------------|-------------|
| Button contact A | GPIO 16 (J3-9) | One side of the momentary pushbutton |
| Button contact B | GND | The other side of the pushbutton |
| Analyzer channel 1 | GPIO 16 (J3-9) | Logic analyzer `D0` |
| Analyzer ground | GND | Logic analyzer `GND` |

GPIO 16 is configured as `INPUT_PULLUP`; the internal pull-up is typically 45 kOhm. The
button therefore reads HIGH when released and LOW when pressed. The analyzer and the board
must share a ground, and the analyzer input must tolerate 3.3 V logic.

## Build and test

```sh
pio run -d homeworks/1_5-button-bounce
pio test -d homeworks/1_5-button-bounce -e native
```

The target environment is `esp32s3_arduino`. The native suite runs the framework-free
`bounce_logic` analysis on the host.

## Flash and capture

```sh
pio run -d homeworks/1_5-button-bounce -t upload --upload-port <PORT>
pio device monitor --port <PORT> --baud 115200
```

The serial port is never selected implicitly. Replace `<PORT>` with the port printed by
`pio device list`.

## Serial protocol

The firmware prints a fixed header, then one block per burst:

```text
BOUNCE_LOGGER 1
BUTTON_PIN=16 QUIET_GAP_MS=250 DEBOUNCE_MS=20
READY
BURST edges=7 falling=4 rising=3 duration_us=1200 max_high_us=150 min_stable_ms=1 settled=LOW overflow=0
E 0 100 L
E 1 250 H
...
TOTAL falling=4 rising=3 debounced=1
READY
```

A burst is dumped after 250 ms without a new edge, so serial traffic never interleaves with
the bounce it describes. A press ends `settled=LOW`; a release ends `settled=HIGH`. The
`TOTAL` line carries the running raw counts and the debounced press count.

## Measurement procedure

1. Wire the button between GPIO 16 and GND, and the analyzer channel to GPIO 16 with a
   common ground.
2. Flash the firmware and open the serial monitor at 115200 baud.
3. Wait for `READY`, then press the button ten times with different speed and force.
4. Save the serial log and the analyzer capture of the same interval.
5. For each press burst, compare `falling` and `min_stable_ms` with the analyzer trace.
6. Fill the measurement ledger in [`report.md`](report.md) and change the `not measured`
   labels to `measured` with the captured values.

## Layout

- `src/main.cpp` — composition root: pin, `CHANGE` interrupt, critical section, serial
  protocol, and the online debounce path.
- `lib/bounce_logic/` — framework-free edge capture and burst analysis, shared with the
  native suite.
- `test/test_bounce_logic/` — Unity tests for the capture, the statistics, the debounce
  window, the release case, and the microsecond wrap.
- `assets/diagram.json` — the Wokwi wiring model; `assets/schematic.svg` is generated from it.

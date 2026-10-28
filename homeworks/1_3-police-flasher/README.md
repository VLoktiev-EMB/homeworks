# Police Flasher

Independent PlatformIO homework for `1_3-police-flasher`. An ESP32-S3 drives a
red/blue police beacon pair and a white strobe LED.

**Status:** in-progress

## Behaviour

- GPIO4 drives the red and blue LEDs in push-pull. Output HIGH lights red
  (GPIO to resistor to LED to ground); output LOW lights blue (3.3 V to
  resistor to LED to GPIO); high-impedance input turns both off.
- GPIO5 drives the white third LED active-high through its own resistor.
- The `police_pattern` library owns a framework-free step table: a red double
  flash, a blue double flash, three white strobe pulses, and a pause. The step
  duration doubles on every full cycle, so the cadence alternates between fast
  and slow.
- `src/main.cpp` is the composition root: it maps the resolved pattern step
  onto the port GPIO contract and never blocks longer than one millisecond.

## Layout

| Path | Purpose |
|------|---------|
| `src/main.cpp` | Arduino composition root and GPIO mapping |
| `lib/police_pattern/` | Framework-free pattern state machine |
| `test/test_police_pattern/` | Unity native tests for the pattern |
| `test/test_homework/` | Unity native tests for the GPIO contract |
| `assets/diagram.json` | Wiring source of truth |
| `assets/schematic.svg` | Generated IEEE vector schematic |

## Build and test

```sh
pio run -d homeworks/1_3-police-flasher
pio test -d homeworks/1_3-police-flasher -e native
```

## Documents

- [Assignment paraphrase](task.md)
- [Report](report.md)
- [Wiring source of truth](assets/diagram.json)
- [Vector schematic](assets/schematic.svg)

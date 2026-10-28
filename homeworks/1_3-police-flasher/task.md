---
source_url: "internal course platform; no public URL"
retrieved: "2026-10-28"
attribution: "Course assignment, Module 1.3 (user-provided paraphrase)"
license: "Unknown; English paraphrase only, no original text redistributed"
---

# Police Flasher

## Task

Build an ESP32 program that drives two LEDs, red and blue, each through a
series resistor, so that the pair alternately flashes like a police beacon.
The sequence repeats continuously.

The implementation also covers the assignment's optional extensions: a richer
strobe cadence whose speed changes between cycles, a third (white) LED, and a
single-GPIO push-pull arrangement in which the red and blue LEDs share one
pin.

## Acceptance criteria

- Two GPIO pins are configured as outputs: the red/blue pair shares GPIO4 and
  the white LED uses GPIO5.
- Red and blue alternate; exactly one of them is lit at a time.
- The pattern repeats indefinitely and the main loop never blocks for longer
  than one pattern step.
- The white LED contributes a distinct strobe phase, and the cadence varies
  between fast and slow cycles.
- The firmware builds for `esp32s3_arduino`, and the pattern library passes
  the native Unity suite.
- The wiring, bill of materials, electrical calculations, and report evidence
  describe the same circuit.

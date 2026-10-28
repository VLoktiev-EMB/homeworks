---
source_url: not-public
retrieved: 2026-10-28
attribution: Course assignment, English paraphrase
license: All rights reserved - paraphrased, no original text reproduced
---

# Button Contact Bounce Analysis with a Logic Analyzer and a Microcontroller

## Task

Build a pull-up button circuit on GPIO 16 of an ESP32-S3-DevKitC-1, count contact state
changes in firmware through a hardware interrupt, and record the same node with channel 1
of a logic analyzer while pressing the button ten times with different speed and force.
For every press, determine how many bounce pulses occurred and how long the bounce lasted.
Compare the analyzer count with the firmware count.

## Acceptance criteria

- The firmware configures GPIO 16 as an input with the internal pull-up and attaches a
  CHANGE interrupt.
- Every captured edge is timestamped and emitted over the serial port without losing
  intermediate counts.
- The firmware reports raw falling-edge and total-edge counts per burst, and a debounced
  press count.
- A logic analyzer capture of the same node is compared with the firmware log for ten
  presses.
- The report states the measured bounce count and duration per press, the average bounce
  duration, and the minimum sufficient debounce.

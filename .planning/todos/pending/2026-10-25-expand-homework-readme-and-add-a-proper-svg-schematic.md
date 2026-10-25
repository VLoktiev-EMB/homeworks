---
created: 2026-10-25T20:30:55.503Z
title: Expand homework README and add a proper SVG schematic
area: docs
severity: minor
files:
  - homeworks/1_3-police-flasher/README.md
  - homeworks/1_3-police-flasher/assets/diagram.json
  - homeworks/1_3-police-flasher/wokwi.toml
  - homeworks/1_3-police-flasher/scenario.yaml
  - homeworks/1_3-police-flasher/platformio.ini
  - homeworks/1_3-police-flasher/lib/pattern/library.json
---

## Problem

The tracer homework is technically complete, but it is hard for an outside reader to
understand what the assignment actually was and how the circuit is put together.

- `homeworks/1_3-police-flasher/README.md` is a short build-and-run note. It does not
  explain the assignment, the behaviour expected from the pattern, the pin map, or how
  the pieces fit together, so a visitor cannot reconstruct the homework from it.
- The canonical wiring exists only as `assets/diagram.json`, a Wokwi JSON file that is
  not human-readable. There is no schematic image, so the circuit cannot be reviewed
  without opening the simulator.
- The requested wiring review ("more adequate and properly routed") has not been done:
  the two-LED anti-parallel branch on GPIO4, the third LED on GPIO6, and the MODE button
  on GPIO7 are correct in the JSON but their visual arrangement and the explanation of
  why node X floats in the all-off frame are not written down anywhere outside the report.
- The configuration is spread across `platformio.ini`, `wokwi.toml`, `scenario.yaml`,
  and `lib/pattern/library.json`; the README does not explain which file owns which
  setting, and the ordering/grouping in the files has not been reviewed for clarity.

The user also asked whether the README could be in Ukrainian, so that anyone interested
can see what the homework consisted of.

## Solution

TBD — candidate shape:

1. Rewrite `README.md` as a reader-facing document: assignment summary (English
   paraphrase with attribution, never the original course text), behaviour table per
   pattern and speed, pin map, wiring explanation, and a file-by-file configuration
   map. Decide between an English-only README with a Ukrainian section, or a
   Ukrainian reader-facing README plus the existing English engineering notes; keep
   repository artifacts English where `AGENTS.md` requires it and record the choice.
2. Add `assets/schematic.svg` — either generated from `diagram.json` or hand-authored —
   showing ESP32-S3 pins, the 150 ohm series resistor, the anti-parallel LED pair
   around node X, the second resistor and LED, and the MODE button to GND. Keep it
   consistent with the diagram's part ids (`esp`, `r1`, `led1`, `led2`, `r2`, `led3`,
   `btn1`) so the BOM rows still map one-to-one.
3. Review the wiring for readability and correctness, and state explicitly why the
   all-off frame leaves node X floating (the reverse-voltage calculation excludes it).
4. Regroup and comment the configuration files so each setting has one obvious owner;
   do not change behaviour or pin numbers without recording the decision.

Open question to settle first: whether "properly routed" means only improving the
schematic's visual layout, or also re-checking the electrical design. Confirm with the
repository owner before changing the wiring itself.

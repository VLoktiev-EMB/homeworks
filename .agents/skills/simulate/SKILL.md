---
name: simulate
description: Use when running Wokwi simulation scenarios headlessly, verifying circuit behavior without physical hardware, linting diagrams offline, or capturing simulated test evidence.
metadata:
  version: "1.0"
  status: active
---

# Wokwi Simulation

Run, test, and capture automated hardware simulation scenarios using `wokwi-cli`.

## Overview

Headless simulation executes compiled firmware against Wokwi virtual hardware models without bench equipment. Simulation runs verify GPIO sequencing, UART serial output, and scenario-driven button presses, producing reproducible `simulated` evidence for homework reports.

## When to Use

- Verifying firmware behavior headlessly before bench flashing.
- Testing automated interaction scenarios (`scenario.yaml`) such as button presses or timing checks.
- Linting circuit wiring and scenario syntax offline with zero API quota consumption.
- Capturing simulated log evidence for Section 8 of `report.md`.

### When NOT to Use

- For compiling code (use `hw-build` first — simulation requires an existing build artifact).
- As a substitute for real bench measurements (simulation never proves physical hardware electrical characteristics).
- For flashing physical microcontrollers (use `hw-flash`).

## Quick Reference

| Action | Command | Quota Cost |
|---|---|---|
| 1. Build target first | `pio run -d homeworks/<id>` | Zero (local compile) |
| 2. Lint circuit offline | `wokwi-cli lint --offline homeworks/<id>/assets/diagram.json` | Zero (offline check) |
| 3. Run interactive / scenario | `wokwi-cli homeworks/<id> --diagram-file assets/diagram.json --scenario scenario.yaml` | Consumes simulation seconds |

## Evidence and Quota Rules

1. **Evidence Boundary**: All findings and timing data produced by Wokwi MUST be labeled `simulated` in `report.md`. Simulation is never bench evidence.
2. **Quota Awareness**: The Wokwi free plan provides ~50 minutes of simulation per rolling 30 days.
   - Always run offline linting (`--offline`) first to catch wiring and scenario syntax errors before spending quota.
   - Keep scenario durations bounded (e.g. 5–15 seconds).
3. **Firmware Prerequisite**: `wokwi-cli` requires compiled binaries in `.pio/build/<env>/`. Always run `pio run` before executing a scenario.

## Common Mistakes & Red Flags

- **Red Flag**: Claiming simulated behavior as `measured` in the evidence ledger.
- **Red Flag**: Running simulation on an uncompiled project (causes `firmware not found` error).
- **Mistake**: Forgetting `--diagram-file assets/diagram.json`, which causes Wokwi to look for `diagram.json` in the root and fail.
- **Mistake**: Unbounded scenario wait times that consume monthly quota needlessly.

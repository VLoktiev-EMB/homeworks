---
status: complete
phase: 07-simulation-spike
source: [07-VERIFICATION.md]
started: 2026-10-26T16:11:34.627111Z
updated: 2026-10-26T16:31:57.575Z
---

## Current Test

[testing complete]

## Tests

### 1. Owner-run Wokwi session: confirm the three pasted stamped captures against the run 1-3 rows
expected: Each of the three captures contains `EXIT 0` and exactly one `I pattern ready` line; wall clock 5.815 s / 8.559 s / 12.701 s and cold/warm 3.759 s / 6.753 s / 11.238 s match the table; `**Outcome:** scenario passed` and `3/3` agree with the exit codes
result: pass

### 2. Velxio board capture: check `$HOME/velxio-boards.png` (587620 bytes) and the page `http://localhost:3080`
expected: The screenshot exists outside the repository and shows the `BOARDS 47` catalogue, including ESP32-S3 DevKit, XIAO ESP32-S3, Arduino Nano ESP32, STM32 Blue Pill and STM32 Black Pill, as recorded in §Velxio self-host attempt
result: pass

### 3. Prohibition P1-1 — the homework keeps no second copy of the merge action
expected: `homeworks/1_3-police-flasher/merge_firmware.py` is absent from disk and `git ls-files --error-unmatch` does not find it; the move and the `git rm` happen in one change
result: pass

### 4. Prohibition P1-2 — no `scripts/simulate.py` or simulation wrapper
expected: The tree contains no `scripts/simulate.py` and no simulation wrapper script; the probe lives only in the test module
result: pass

### 5. Prohibition P1-3 — no real `WOKWI_CLI_TOKEN` in a test, fixture, child env or recorded command
expected: The only assigned value in tracked source is the literal `dummy` (README and test_simulation_paths.py); no real token is present
result: pass

### 6. Prohibition P1-4 — the Wokwi command is not checked by prose or a doc-sync test
expected: The only evidence is an executed subprocess with its exit status and output; no README read and no document substring comparison
result: pass

### 7. Prohibition P2-1 — the `WOKWI_CLI_TOKEN` value reached neither a file, an argument, nor a transcript
expected: The only permitted sentence is `token supplied by the repository owner; value not recorded`; `git grep WOKWI_CLI_TOKEN -- .github` is empty
result: pass

### 8. Prohibition P2-2 — simulated digital state or timing is not presented as bench/hardware evidence
expected: Only the `expect-pin` state and the serial text are called simulation evidence; the report repeats that simulation output is not hardware evidence
result: pass

### 9. Prohibition P2-3 — quota is not derived from wall-clock
expected: Wall-clock seconds and simulated minutes are separate columns; 45 s = 3 × `--timeout 15000`, labelled `calculated (upper bound)`
result: pass

### 10. Prohibition P2-4 — no `--quiet` or `--interactive` added to a measurement run
expected: The protocol states an explicit prohibition; the captured commands do not carry those options
result: pass

### 11. Prohibition P2-5 — no simulated minutes, serial line, exit code or VCD path was invented
expected: Every missing quantity is recorded as `absent — <reason>` or `not measured — <reason>`; VCD for run 1 and the serial logs for runs 2-3 are marked absent
result: pass

### 12. Prohibition P3-1 — mutable `:master` is not the recorded image identity
expected: The identity is `ghcr.io/davidmonterocrespo24/velxio@sha256:5d673722…`; `:master` is named only as the pull reference
result: pass

### 13. Prohibition P3-2 — the vendor-documented board list is not presented as an observation
expected: The `Board coverage (vendor documentation)` row carries the `datasheet` label; the observed row references the screenshot and URL
result: pass

### 14. Prohibition P3-3 — the pilot was not ported into a Velxio sketch just to take a measurement
expected: Pilot compile and serial are `not measured` with a reason about the PlatformIO format; no ported sketch exists
result: pass

### 15. Prohibition P3-4 — no Velxio source, image layer or AGPL asset in the MIT repository
expected: `git ls-files` contains no fritzing/velxio artifact; the tree holds only the image reference and the AGPL boundary
result: pass

### 16. Prohibition P3-5 — the Velxio attempt consumed no Wokwi quota
expected: §Velxio self-host attempt states explicitly that Wokwi was not contacted and no session was opened
result: pass

### 17. Prohibition P4-1 — `schema/homework.schema.json` is unchanged
expected: `$defs.simulation.properties.status.enum` = `[none, pending, verified]`, there is no `evidence` key, and `additionalProperties: false`; the schema git diff is empty
result: pass

### 18. Prohibition P4-2 — no simulated value was promoted to `measured`
expected: The report's five-bridge vocabulary is unchanged (`measured`, `calculated`, `simulated`, `datasheet`, `not measured`); L-08 remains `simulated`
result: pass

### 19. Prohibition P4-3 — the record does not claim that Renode lacks STM32 support
expected: The Renode row names the unconfirmed course model, the absent STM32 homework/board profile and the missing installation; the phrase «Renode lacks STM32» does not appear
result: pass

### 20. Prohibition P4-4 — no copy of Fritzing part graphics in shared assets
expected: `docs/assets/` and `homeworks/*/assets/` received no new Fritzing artifact; `diagram.json` remains the single source of truth
result: pass

### 21. Prohibition P4-5 — the README was not expanded and no SVG diagram was added
expected: §Simulation received only a pointer to the evidence/ADR; no new SVG file exists
result: pass

### 22. Prohibition P4-6 — status is not set to `verified` on failed/blocked; no stale sentence remains
expected: `**Outcome:** scenario passed`, so `simulation.status: verified`; the 12 forbidden stale phrases are absent from report.md and README.md
result: pass

### 23. Prohibition P4-7 — vendor-documented or `not measured` Velxio values are not presented in the ADR as observations
expected: In the ADR matrix: `19 boards` — `datasheet`, 47 boards — observed, pilot compile/serial — `not measured`; the rows are not blended
result: pass

## Summary

total: 23
passed: 23
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps

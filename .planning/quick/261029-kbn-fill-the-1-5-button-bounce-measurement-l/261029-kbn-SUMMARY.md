---
phase: quick
plan: 261029-kbn
subsystem: homework-1_5-button-bounce
tags: [report, measurements, homework]
status: complete
requires: []
provides:
  - "Filled 1_5 measurement ledger from the serial log and analyzer export"
  - "Complete homework metadata and README Measurements section"
affects:
  - homeworks/1_5-button-bounce
tech-stack:
  added: []
  patterns:
    - "Ledger evidence prefixes serial-log: and digital.csv: name the artifact, never the reporter"
key-files:
  created:
    - homeworks/1_5-button-bounce/assets/measurements/serial.log
    - homeworks/1_5-button-bounce/assets/measurements/digital.csv
  modified:
    - homeworks/1_5-button-bounce/report.md
    - homeworks/1_5-button-bounce/README.md
    - homeworks/1_5-button-bounce/homework.yaml
decisions:
  - "Analyzer and firmware counts are compared as edge totals (65 versus 74), with the falling-level count (35 versus 37) secondary."
  - "Per-event bounce metrics use a 10 ms cluster over the analyzer transitions, because the firmware's 250 ms quiet gap merges rapid presses."
  - "Minimum sufficient debounce is 1 ms from the 160.625 us maximum HIGH gap via C-06."
metrics:
  duration: "~15 min"
  completed: "2026-10-29"
  tasks: 3
  files: 5
actuals:
  tokens: 9700
  tasks: 3
  commits: 1
---

# Quick Task 261029-kbn Summary

Filled the `1_5-button-bounce` measurement ledger from the committed serial log and Saleae
analyzer export, marked the homework and report complete, and added a README Measurements
section.

## What changed

- `report.md`: rewrote the lead, assumptions A-01/A-05/A-06/A-08, limitations, C-04, added
  C-06, methodology, results, all thirteen ledger rows, traceability T-07/T-09/T-10/T-11, the
  analysis, and the conclusions. Section 1 and every ledger row now name `a99da51`.
- `homework.yaml`: status and report status are `complete`; both measurement files are listed
  under `assets`.
- `README.md`: complete status, a `## Measurements` section, corrected procedure steps, and
  both evidence files in the Layout list.
- Added `assets/measurements/serial.log` and `assets/measurements/digital.csv` byte-for-byte
  unchanged.

## Headline results

- Analyzer: 24 MS/s, 12.364 s capture, 74 transitions (37 falling, 37 rising).
- Firmware: 65 edges (35 falling-level, 30 rising-level); difference -9 edges (-12.2%).
- Five bounce events, mean 978.1 us, release-only mean 1222.6 us.
- Maximum HIGH gap 160.625 us, minimum sufficient debounce 1 ms (20 ms window is about 124x).

## Deviations from Plan

- **Ledger evidence wording.** The plan's literal values used a `user-reported:` prefix; the
  orchestrator clarification forbids it, so every analyzer value names `digital.csv:` inside a
  `serial-log:`-prefixed value. This keeps the report contract's required prefix and names the
  actual evidence file.
- **README step 5.** Updated the procedure step that compared `falling`/`min_stable_ms` with
  the analyzer trace, because that method contradicts the 10 ms-cluster methodology; it now
  pairs the BURST lines with 10 ms analyzer clusters.
- **Ignored evidence file.** `serial.log` matched the boilerplate `*.log` ignore rule, so it
  was staged with `git add -f` as an authored evidence artifact (not generated build output).
  No `.gitignore` change was made, per the plan's file scope.

## Verification

- `uv run scripts/check_metadata.py` — PASS.
- `pio run -d homeworks/1_5-button-bounce` — PASS.
- `pre-commit run --files <five paths>` — all hooks PASS.
- SHA-256 unchanged: serial.log `4bc013f8…60168`, digital.csv `3eb4e27f…91e5f`.
- Commit `79d8061` contains the five intended files and no `.vscode/settings.json`.
- No tag was created or moved.

## Self-Check: PASSED

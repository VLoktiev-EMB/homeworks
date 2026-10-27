---
status: complete
phase: 09-agent-workflow-and-skills
source: [09-VERIFICATION.md]
started: 2026-10-27T13:16:55Z
updated: 2026-10-27T13:19:11.532Z
---

## Current Test

[testing complete]

## Tests

### 1. Capture a real device log through hardware
expected: |
  With a board attached after a confirmed upload, run
  `uv run scripts/serial_capture.py --id 1_3-police-flasher --seconds 20`,
  pressing RESET during the window because the firmware logs only in `setup()`.
  Exit 0, a `CAPTURED — N bytes captured from <port> (USB VID:PID=<vid>:<pid>) at <baud> baud`
  line naming `.skill-state/logs/1_3-police-flasher.log`, and a log holding the raw
  device bytes.
why_human: |
  No board is attached in this environment and the command sandbox refuses
  `/dev/cu.*`; the automated suite drives a fake `sys.executable` child on a PTY.
  The prior hardware report (`G-09-1`, no bytes captured) was closed by plans 09-15
  and 09-16: the monitor now opens with `--dtr 0 --rts 0` and the capture resolves and
  reports one port. This run only re-confirms that fixed path on hardware.
result: pass

## Summary

total: 1
passed: 1
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps

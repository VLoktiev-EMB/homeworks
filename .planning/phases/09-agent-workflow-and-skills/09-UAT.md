---
status: testing
phase: 09-agent-workflow-and-skills
source: [09-VERIFICATION.md]
started: 2026-10-27T10:55:00Z
updated: 2026-10-27T10:55:00Z
---

## Current Test

number: 1
name: Capture a real device log through hardware
expected: |
  Exit 0, a `CAPTURED — N bytes captured` line naming
  `.skill-state/logs/1_3-police-flasher.log`, and a log holding the raw device bytes.
awaiting: user response

## Tests

### 1. Capture a real device log through hardware
expected: |
  With a board connected after a confirmed upload, run
  `uv run scripts/serial_capture.py --id 1_3-police-flasher --seconds 20`.
  Exit 0, a `CAPTURED — N bytes captured` line naming
  `.skill-state/logs/1_3-police-flasher.log`, and a log holding the raw device bytes.
why_human: |
  The automated suite drives a fake `sys.executable -c` child on a PTY; the real
  `pio device monitor` needs hardware and a serial port.
result: [pending]

## Summary

total: 1
passed: 0
issues: 0
pending: 1
skipped: 0
blocked: 0

## Gaps

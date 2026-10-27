---
status: diagnosed
phase: 09-agent-workflow-and-skills
source: [09-VERIFICATION.md]
started: 2026-10-27T10:55:00Z
updated: 2026-10-27T11:50:39Z
---

## Current Test

[testing complete]

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
result: issue
reported: ".skill-state/logs/1_3-police-flasher.log: REFUSED — capture unavailable: no bytes captured (twice: firmware flashed, RESET pressed during the second 20-second window, board on /dev/cu.usbmodem2101)"
severity: major

## Summary

total: 1
passed: 0
issues: 1
pending: 0
skipped: 0
blocked: 0

## Gaps

- gap_id: G-09-1
  truth: "A board connected after a confirmed upload yields exit 0, a `CAPTURED — N bytes captured` line naming `.skill-state/logs/1_3-police-flasher.log`, and a log holding the raw device bytes"
  status: failed
  reason: "User reported: `.skill-state/logs/1_3-police-flasher.log: REFUSED — capture unavailable: no bytes captured`, reproduced twice with the firmware flashed and RESET pressed"
  severity: major
  test: 1
  root_cause: "`scripts/serial_capture.py` `_build_command` (288-303) omits `--dtr`/`--rts`, so `pio device monitor` opens the port with pyserial defaults DTR=1/RTS=1. On the ESP32-S3 that asserted pair holds the chip in reset — via the USB-Serial-JTAG peripheral on the native USB port (303A:1001) and via the auto-reset circuit on the CH343 UART bridge (1A86:55D3) — so the application never runs and emits nothing. Verified on both paths outside the sandbox: default capture 0 bytes; `pio device monitor --dtr 0 --rts 0` returns 248 bytes on CH343 and 282 bytes on native USB, both ending in `I pattern ready`. A sandboxed run is not a valid measurement: `/dev/cu.*` is refused with `Operation not permitted`."
  artifacts:
    - path: "scripts/serial_capture.py"
      issue: "Monitor argv omits `--dtr 0 --rts 0` and has no `--port`/`-p` passthrough"
    - path: ".claude/skills/hw-flash/SKILL.md"
      issue: "Contract never resolves or records the port, so flash and capture can target different interfaces (native USB vs UART bridge)"
    - path: "scripts/tests/test_serial_capture.py"
      issue: "Suite pins PTY byte fidelity but not the line-state argv or port selection"
  missing:
    - "Pass `--dtr 0 --rts 0` to `pio device monitor` so the port opens in the idle line state"
    - "Add `--port`/`-p` passthrough so a capture can target an explicit device"
    - "Refuse to capture when several candidate ports exist and no explicit port is given (never silently pick one)"
    - "Record the resolved port (device + VID:PID) in the `--json` object and the `CAPTURED` line"
    - "Pin the new argv and both line states in `scripts/tests/test_serial_capture.py`"
    - "Update the hw-flash contract: flash and capture must use the same port; document native USB vs UART bridge (baud, reset semantics, re-enumeration)"
  debug_session: .planning/debug/capture-no-bytes.md

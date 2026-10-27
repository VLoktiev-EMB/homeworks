---
phase: 09-agent-workflow-and-skills
plan: 15
subsystem: workflow-tooling
tags: [agent-skills, serial-capture, port-selection, baud-resolution, esp32s3, provenance]

# Dependency graph
requires:
  - phase: 09-agent-workflow-and-skills
    provides: "09-10..09-14 — PTY capture helper, widened credential scan, forwarded baud, duration validation, reaping finally"
provides:
  - "A capture that always names its port and opens it in the idle line state (`-p`, `--dtr 0`, `--rts 0`)"
  - "Fail-closed resolution to exactly one USB serial device, with an ambiguity refusal that names every candidate and `--port`"
  - "Effective-baud resolution from `pio project config` when `--baud` is omitted"
  - "Port path, VID:PID and baud in the `--json` object and the `CAPTURED` line, with the log still byte-exact raw device output"
affects: [09-uat-recheck, phase-10-report]

# Actuals (#2632) — same estimateTokens scale (chars/4 over the realized diff).
actuals:
  tokens: 7784
  tasks: 2
  commits: 2
plan_head_before: 00062e40e106977790022a4ab5e7cf063d326c4b
plan_head_after: 01e4fa0601c97ed91920d77b53edf63136dd2c39

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Resolve the interface explicitly and fail closed: one candidate or an explicit `--port`, never an implicit choice"
    - "Report provenance in the metadata output while the evidence file stays exactly the raw byte stream"
    - "Normalize a config value with `int(str(value))` because `pio project config` types the same option differently by section"

key-files:
  created: []
  modified:
    - scripts/serial_capture.py
    - scripts/tests/test_serial_capture.py

key-decisions:
  - "`resolve_baud` takes the raw `pio project config` payload and calls `_config_sections` itself, so the inline contract check and `main` share one call shape."
  - "`_run_json` reports `port discovery failed: <failure>` and never repeats child stderr; it is shared with `project_config`, so a failing config query surfaces under that same refusal prefix (exit 1)."
  - "Port identities are never deduplicated by VID:PID: two ports on one board are an ambiguity the user breaks with `--port`."
  - "The human line keeps the `CAPTURED — N bytes captured` prefix and appends `from <port> (USB VID:PID=<vid>:<pid>) at <baud> baud`; the log write is untouched."

patterns-established:
  - "A device-selecting helper proves its refusal before any process starts by patching the capture entry point with a side effect that would fail the test."

requirements-completed: [FLOW-01, FLOW-02, FLOW-03, FLOW-04, FLOW-05, FLOW-06, FLOW-07]

# Coverage metadata (#1602)
coverage:
  - id: D1
    description: "Exactly one USB serial device is selected among non-USB entries; zero and several candidates refuse with a reason naming the candidates and --port."
    requirement: FLOW-07
    verification:
      - kind: unit
        ref: "scripts/tests/test_serial_capture.py#PortResolutionTests"
        status: pass
    human_judgment: false
  - id: D2
    description: "The monitor argv always carries -p <resolved>, --dtr 0 and --rts 0 before --raw."
    requirement: FLOW-07
    verification:
      - kind: unit
        ref: "scripts/tests/test_serial_capture.py#BuildCommandTests.test_the_monitor_opens_in_the_idle_line_state_with_an_explicit_port"
        status: pass
      - kind: other
        ref: "python3 -c assertion on _build_command argv positions"
        status: pass
    human_judgment: false
  - id: D3
    description: "The end-to-end path reports port, VID:PID and baud, and the log bytes equal the child payload exactly."
    requirement: FLOW-07
    verification:
      - kind: e2e
        ref: "scripts/tests/test_serial_capture.py#CaptureEndToEndTests.test_a_capture_reports_the_port_vid_pid_and_baud"
        status: pass
    human_judgment: false
  - id: D4
    description: "An ambiguous port refuses before the capture starts, proven by a capture_pty side effect that would fail the test."
    requirement: FLOW-07
    verification:
      - kind: e2e
        ref: "scripts/tests/test_serial_capture.py#CaptureEndToEndTests.test_an_ambiguous_port_refuses_before_the_capture_starts"
        status: pass
    human_judgment: false
  - id: D5
    description: "The effective baud is --baud when supplied, otherwise the selected environment's monitor_speed; an unresolvable value is exit 2."
    requirement: FLOW-07
    verification:
      - kind: unit
        ref: "scripts/tests/test_serial_capture.py#BaudResolutionTests"
        status: pass
      - kind: e2e
        ref: "scripts/tests/test_serial_capture.py#CliResultPayloadTests.test_an_omitted_baud_is_reported_from_the_project"
        status: pass
    human_judgment: false
  - id: D6
    description: "--port values outside an absolute /dev path are exit 2 before any process starts."
    requirement: FLOW-07
    verification:
      - kind: unit
        ref: "scripts/tests/test_serial_capture.py#CliUsageTests.test_a_relative_port_is_a_usage_error and test_a_port_outside_dev_is_a_usage_error"
        status: pass
    human_judgment: false
  - id: D7
    description: "The existing PTY, early-exit, reaping, credential-scan and atomic-write guarantees still hold."
    requirement: FLOW-07
    verification:
      - kind: unit
        ref: "python3 -m unittest scripts.tests.test_serial_capture (62 tests)"
        status: pass
    human_judgment: false

duration: 8 min
completed: 2026-10-27
status: complete
---

# Phase 9 Plan 15: Serial Capture Port and Baud Resolution Summary

**A capture now names exactly one USB serial port, opens it in the idle line state that lets the ESP32-S3 run, and reports the interface and baud that produced the raw log**

## Performance

- **Duration:** 8 min
- **Started:** 2026-10-27T11:54:45Z
- **Completed:** 2026-10-27T12:03:00Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- `_build_command` now emits `pio device monitor -d homeworks/<id> -p <port> --dtr 0 --rts 0 --raw --quiet`, so the port opens in the idle line state instead of the asserted DTR/RTS pair that holds the ESP32-S3 in chip reset.
- `list_serial_devices`, `_usb_identity` and `resolve_port` filter `pio device list --json-output` to `USB VID:PID=<vid>:<pid>` entries and select exactly one; zero candidates refuse with `no USB serial device found`, and several refuse as `ambiguous USB serial ports (...); pass --port`, naming every candidate.
- `--port` is validated as an absolute `/dev` path with no `..` component and forwarded as one argv element; a path PlatformIO does not report as a USB serial device refuses rather than being guessed at.
- The `--json` object and the `CAPTURED` line carry `port`, `vid_pid` and `baud`; the log remains exactly the captured bytes with no header and no sidecar.
- `project_config`, `_config_sections` and `resolve_baud` read the selected environment's `monitor_speed` when `--baud` is omitted. An absent, non-integer or non-positive value, an unknown environment, or several default environments without `--env` is the documented exit-2 usage error; PlatformIO's 9600 fallback is never used silently.
- The module docstring records the selection rule, the idle line state, the provenance fields, the raw-log contract and the exit-code split.
- The capture suite grew from 42 to 62 tests; the full Python suite is green outside the sandbox (439 tests, 1 pre-existing skip).

## Task Commits

Each task was committed atomically:

1. **Task 1: Resolve one USB serial port, open it in the idle line state, and report its identity end to end** - `d1720f8` (fix)
2. **Task 2: Resolve the effective baud from the project and pin the usage and payload contracts** - `01e4fa0` (fix)

**Plan metadata:** the `docs(09-15)` SUMMARY commit (this file).

## Files Created/Modified

- `scripts/serial_capture.py` — `PortIdentity`, `USB_HWID`, `DEVICE_QUERY_TIMEOUT`, `_run_json`, `list_serial_devices`, `_usb_identity`, `resolve_port`, `_valid_port_path`, `project_config`, `_config_sections`, `_default_envs`, `resolve_baud`; `_build_command(args, port)` with `-p`/`--dtr`/`--rts`; `--port` argument and usage validation; `port`/`vid_pid`/`baud` in both payloads and the `CAPTURED` line; updated module docstring.
- `scripts/tests/test_serial_capture.py` — `PORT`, `SERIAL_DEVICES`, `SECOND_USB_DEVICE`, `PROJECT_CONFIG`; `PortResolutionTests`, `BaudResolutionTests`, `CaptureEndToEndTests`; updated `BuildCommandTests`, `CliResultPayloadTests`, `CliUsageTests`.

## Decisions Made

- `resolve_baud(explicit, config, env)` accepts the raw `pio project config` payload and runs `_config_sections` internally, matching the plan's inline verify and keeping `main` to one call.
- `_run_json` refuses with `port discovery failed: <failure class>` and never repeats child stderr, because stderr can echo a device path or device bytes. Because `project_config` shares the runner, a failing config query reports under the same prefix (exit 1) while config *shape* problems remain `CheckError` (exit 2).
- Ports are not deduplicated by VID:PID; the native USB interface and the UART bridge are a real ambiguity.
- The human `CAPTURED` line keeps its `CAPTURED — N bytes captured` prefix so existing outcome parsing is unaffected.
- The real `pio device list --json-output` and `pio project config --json-output` outputs on this host were inspected and match the new fixtures (`303A:1001` on `/dev/cu.usbmodem2101`, `monitor_speed` integer 115200 under `env:esp32s3_arduino`).

## Deviations from Plan

None - plan executed exactly as written.

The only execution-time adaptation was environmental: PTY allocation is refused inside the command sandbox (`command cannot start: out of pty devices`), so every capture-suite and full-suite run was repeated with the sandbox disabled, as the plan's `<verify>` notes allow. No test was skipped or weakened, and the sandboxed zero is not recorded as a result.

## Issues Encountered

- The plan's `@.planning/debug/capture-no-bytes.md` reference does not exist in this worktree or at the plan base commit. The measured root cause is recorded verbatim in `09-UAT.md` (root_cause) and was used from there; no implementation decision depended on the missing file.
- The sandboxed full-suite run reports PTY failures for every capture test; the outside-sandbox run is `OK (skipped=1)`, the one skip being the pre-existing `ClangdGuideCommandTests` case that requires `homeworks/1_3-police-flasher/compile_commands.json`.
- `git` subcommands other than `rev-parse` are refused through the repository's `rtk` wrapper in this worktree; the executor used `/usr/bin/git` directly for status, add, commit, log and diff. Commits ran with hooks enabled (no `--no-verify`).

## Known Stubs

None.

## Threat Flags

None — every new surface (port selection, `--port` validation, provenance reporting, line state) is covered by T-09-44 through T-09-47 in the plan's threat register.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The automated G-09-1 proof is in place: the argv, the fail-closed selection, the usage errors and the end-to-end identity are pinned, and the suite is green outside the sandbox.
- The remaining G-09-1 truth is the hardware re-check: with the board attached, `uv run scripts/serial_capture.py --id 1_3-police-flasher --seconds 20` must exit 0 and print `CAPTURED — N bytes captured`, naming `.skill-state/logs/1_3-police-flasher.log`. That is a `/gsd-verify-work` step, not an executor step; a sandboxed run is not evidence.
- `.claude/skills/hw-flash/SKILL.md` still describes the old monitor argv and the PlatformIO-chosen port. That file is outside this plan's `files_modified`, so the contract update remains open for a later plan.

## Self-Check: PASSED

- FOUND: scripts/serial_capture.py
- FOUND: scripts/tests/test_serial_capture.py
- FOUND: .planning/phases/09-agent-workflow-and-skills/09-15-SUMMARY.md
- FOUND: d1720f8
- FOUND: 01e4fa0

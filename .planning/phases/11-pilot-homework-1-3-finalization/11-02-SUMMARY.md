---
phase: 11-pilot-homework-1-3-finalization
plan: 02
status: complete
completed_at: "2026-10-28T00:45:00+02:00"
commit: "bab4ba6"
files_modified:
  - homeworks/1_3-police-flasher/README.md
  - homeworks/1_3-police-flasher/lib/pattern/include/pattern/controller.h
  - homeworks/1_3-police-flasher/lib/pattern/src/controller.c
  - homeworks/1_3-police-flasher/scenario.yaml
  - homeworks/1_3-police-flasher/src/main.cpp
  - homeworks/1_3-police-flasher/test/test_controller/test_controller.c
---

# Plan 11-02 Summary: Firmware Transition Logging and Wokwi Simulation Expansion

## What was done
1. **Transition Logging in Controller (`pattern_controller`)**:
   - Added `port_log_t log` field and `pattern_controller_set_logger()` to controller interface.
   - Emitted structured `PORT_LOG_INFO` log messages on mode transitions (`"mode: double_flash"`, `"mode: chase"`, etc.) and on long-press speed transitions (`"speed: fast"`, `"speed: fastest"`, etc.).
   - Initialized `controller->log = (port_log_t){0}` so unconfigured loggers safely discard output without crashing.
2. **Composition Root Logger Wiring (`main.cpp`)**:
   - Wired `pattern_controller_set_logger(&controller, logger)` in `setup()`.
   - Built ESP32-S3 firmware with PlatformIO successfully (`pio run -d homeworks/1_3-police-flasher`).
3. **Native Unit Test Coverage (`test_controller.c`)**:
   - Added a mock log sink (`test_log_sink_t`) and two new test cases: `test_controller_mode_transition_logs_event` and `test_controller_speed_transition_logs_event`.
   - Verified that all 40/40 test cases across the native test suite pass with 0 failures (`pio test -d homeworks/1_3-police-flasher -e native`).
4. **Expanded Wokwi Automation Scenario (`scenario.yaml`)**:
   - Added short press interaction on `btn1` (50ms hold) validating mode transition to `mode: double_flash`.
   - Added long press interaction on `btn1` (650ms hold) validating speed transition to `speed: fast`.
   - Total simulation time bounded to ~1.2s, keeping CI execution rapid.
5. **Documentation and Path Resolution**:
   - Updated `homeworks/1_3-police-flasher/README.md` to document the interactive simulation steps and expected serial monitor output.
   - Validated offline diagram linting (`wokwi-cli lint --offline`) and path resolution.
   - Verified local gate with `pre-commit run --all-files` (14/14 checks passed).

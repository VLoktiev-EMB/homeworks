---
status: complete
phase: 03-shared-core-and-dependency-rule
source: [03-VERIFICATION.md]
started: 2026-10-24T00:00:00Z
updated: 2026-10-23T23:23:41.024Z
---

## Current Test

[testing complete]

## Tests

### 1. ADR-0008 supersession scope
expected: Read `docs/decisions/0008-common-depends-on-port.md` against ADR-0002 and confirm
  the new record supersedes exactly the dependency-rule sentence and nothing else; ADR-0002
  remains accepted and unedited.
result: pass

### 2. I2C/SPI describe a bus abstraction, not a driver or HAL
expected: `lib/port/include/port/i2c.h` and `spi.h` expose bus-level read/write/transfer only
  — no register map, page, display, device initialisation or native-handle escape hatch.
result: pass

### 3. CRC and ring-buffer disclaimers are strong enough
expected: CRC is stated as data integrity, not authentication or trust; the ring buffer is
  stated as neither ISR-safe nor lock-free.
result: pass

### 4. Host fakes contain no policy
expected: `lib/host/src/*.c` only records, loops back, bounds-checks and injects one-shot
  failure; no production decision logic, schedule or state machine.
result: pass

### 5. Adapters are one framework call plus enum mapping
expected: Every callback in `lib/arduino/src/*.c` and `lib/espidf/src/*.c` translates one call
  and returns `PORT_OK` or a mapped `port_status_t`; no debounce, scheduling or business logic.
result: pass

### 6. I2C/SPI adapter deferral and target-compile ownership are adequate
expected: The deferral recorded in ADR-0008 D-08 and plan 03-06 is acceptable for this
  milestone, and Phase 4 / Phase 8 actually cover the post-Phase-3 target-compile gap.
result: pass

### 7. Test-tier prohibitions need permanent tests or an accepted one-off
expected: Either accept the one-off evidence, or add permanent tests for ADR-0002 immutability
  and for the ESP-IDF pin guard that precedes the `1ULL << pin` shift.
result: pass

### 8. Empty allowlist is the intended permanent policy
expected: No allowlist entries now; any future entry must name a path, a rule and a non-empty
  reason, and a stale entry fails the run.
result: pass

## Summary

total: 8
passed: 8
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps

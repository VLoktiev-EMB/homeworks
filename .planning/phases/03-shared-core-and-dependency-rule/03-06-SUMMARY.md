---
phase: 03-shared-core-and-dependency-rule
plan: 06
subsystem: adapters
tags: [ports-and-adapters, arduino, espidf, c11, target-compile, compilation-database, gpio, logging, time]

# Dependency graph
requires:
  - phase: 03-shared-core-and-dependency-rule
    plan: 01
    provides: "port_time_t contract, port_status_t vocabulary, host-only tests/ project"
  - phase: 03-shared-core-and-dependency-rule
    plan: 03
    provides: "port_gpio_t and port_log_t contracts with explicit enum values"
  - phase: 02-toolchain-truth
    provides: "pinned platformio/espressif32 8.0.0 and homeworks/0_0-toolchain-smoke composition example"
provides:
  - "Arduino time, GPIO and logging adapters as pure C translation units"
  - "ESP-IDF time, GPIO and logging adapters as pure C translation units"
  - "Target-compile proof by compilation-database entries naming an Xtensa compiler"
  - "Recorded D-08 deferral for I2C and SPI adapters and the post-Phase-3 compile gap"
affects: [03-07, 03-08, 04, 08, 11]

actuals:
  tokens: 2543
  tasks: 3
  commits: 3
  plan_head_before: 04ad3e5fa1bca34c352bdadf4badc37389107edd
  plan_head_after: e57d63695ee84b4ee8291be9242dcfee2935ee6f

tech-stack:
  added: []
  patterns:
    - "Adapter factory returns the consumer-owned port struct by value, initialized positionally"
    - "Framework header first, blank line, own project header quoted"
    - "One static callback per contract operation that translates one call and returns a status"
    - "Framework error codes mapped through one static helper, never exposed"
    - "Public adapter headers declare only port types and one factory"

key-files:
  created:
    - lib/arduino/include/arduino/time.h
    - lib/arduino/src/time.c
    - lib/arduino/include/arduino/gpio.h
    - lib/arduino/src/gpio.c
    - lib/arduino/include/arduino/log.h
    - lib/arduino/src/log.c
    - lib/espidf/include/espidf/time.h
    - lib/espidf/src/time.c
    - lib/espidf/include/espidf/gpio.h
    - lib/espidf/src/gpio.c
    - lib/espidf/include/espidf/log.h
    - lib/espidf/src/log.c
  modified: []

key-decisions:
  - "Adapters implement exactly three contracts each (time, GPIO, logging); I2C and SPI stay contracts without a framework implementation (D-08)"
  - "The ESP-IDF GPIO adapter rejects pin >= 64 before the pin-mask shift, so the undefined shift is unreachable"
  - "gpio_config_t is zero-initialised and both pull flags are set on every set_mode call, including the reject path ordering before the shift"
  - "The Arduino log adapter calls log_printf unconditionally because log_i/log_d expand to nothing at the default CORE_DEBUG_LEVEL"
  - "ESP-IDF read returns PORT_OK after storing gpio_get_level, because that call reports a level rather than an error code"

patterns-established:
  - "Adapter headers include only the matching port header; no framework include appears under an adapter's include/"
  - "Every framework result passes through map_esp_err so an esp_err_t never reaches a port header"
  - "Target-compile evidence is a compilation-database entry naming an Xtensa compiler, not a link-only artifact"

requirements-completed: [ARCH-03]

coverage:
  - id: D1
    description: "Arduino time adapter declares port_time_t arduino_time_port(void) with no framework type and translates millis()"
    requirement: ARCH-03
    verification:
      - kind: integration
        ref: "pio run -d homeworks/0_0-toolchain-smoke -e esp32s3_arduino -t compiledb#lib/arduino/src/time.c entry with xtensa-esp32s3-elf-gcc"
        status: pass
    human_judgment: false
  - id: D2
    description: "Arduino GPIO adapter maps three modes and two levels, rejects unknown values, and reports a NULL output as PORT_ERR_INVALID_ARG"
    requirement: ARCH-03
    verification:
      - kind: integration
        ref: "pio run -d homeworks/0_0-toolchain-smoke -e esp32s3_arduino && CDB entry for lib/arduino/src/gpio.c"
        status: pass
      - kind: automated
        ref: "python3 -c source assertion over lib/arduino/src/gpio.c"
        status: pass
    human_judgment: false
  - id: D3
    description: "Arduino logging adapter emits through unconditional log_printf with an E/W/I/D prefix and no C++ object"
    requirement: ARCH-03
    verification:
      - kind: integration
        ref: "pio run -d homeworks/0_0-toolchain-smoke -e esp32s3_arduino && CDB entry for lib/arduino/src/log.c"
        status: pass
      - kind: automated
        ref: "python3 -c source assertion rejecting log_i/log_d/Serial"
        status: pass
    human_judgment: false
  - id: D4
    description: "ESP-IDF time adapter divides the microsecond clock to milliseconds and returns the port contract"
    requirement: ARCH-03
    verification:
      - kind: integration
        ref: "pio run -d homeworks/0_0-toolchain-smoke -e esp32s3_espidf -t compiledb#lib/espidf/src/time.c entry with xtensa-esp32s3-elf-gcc"
        status: pass
    human_judgment: false
  - id: D5
    description: "ESP-IDF GPIO adapter zero-initialises gpio_config_t, sets both pull flags, guards pin >= 64 before the shift and maps driver errors"
    requirement: ARCH-03
    verification:
      - kind: integration
        ref: "pio run -d homeworks/0_0-toolchain-smoke -e esp32s3_espidf && CDB entry for lib/espidf/src/gpio.c"
        status: pass
      - kind: automated
        ref: "python3 -c source assertion on ordering, config initializer and map_esp_err"
        status: pass
    human_judgment: false
  - id: D6
    description: "ESP-IDF logging adapter maps four port levels onto the framework severity enum and keeps esp_log_level_t out of the header"
    requirement: ARCH-03
    verification:
      - kind: integration
        ref: "pio run -d homeworks/0_0-toolchain-smoke -e esp32s3_espidf && CDB entry for lib/espidf/src/log.c"
        status: pass
      - kind: automated
        ref: "python3 -c header scan for esp_err_t/gpio_num_t/esp_log_level_t"
        status: pass
    human_judgment: false
  - id: D7
    description: "I2C and SPI framework adapters are explicitly deferred and the post-Phase-3 target-compile gap is recorded with named owners"
    requirement: ARCH-03
    verification: []
    human_judgment: true
    rationale: "Whether the recorded risk names adequate owners and whether the deferral is the right scope call is a review judgement; no automated test can assert the absence of a future need."

duration: 2 min
completed: 2026-10-24
status: complete
---

# Phase 03 Plan 06: Framework Adapter Translation Units Summary

**Six pure-C translation units give Arduino and ESP-IDF the same time, GPIO and logging contracts, each proven by a target compilation-database entry naming `xtensa-esp32s3-elf-gcc`, while I2C and SPI stay contracts without an adapter.**

## Performance

- **Duration:** 2 min (first task commit 22:31:33Z to completion 22:33:23Z)
- **Tasks:** 3
- **Files modified:** 12 (12 created, 0 modified)

## Accomplishments

- `lib/arduino` and `lib/espidf` each implement exactly three contracts — time, GPIO and
  logging — as `.c` translation units that include the framework header first and the
  adapter's own header second.
- Both target environments build successfully:
  `pio run -d homeworks/0_0-toolchain-smoke -e esp32s3_arduino` and
  `-e esp32s3_espidf`; the six new sources appear in `compile_commands.json` with an
  `xtensa-esp32s3-elf-gcc` command.
- No public adapter header names a framework type: the three ESP-IDF headers are free of
  `esp_err_t`, `gpio_num_t` and `esp_log_level_t`, and the three Arduino headers are free
  of `Arduino.h`, `esp_` and C++ `class` spellings.
- The ESP-IDF GPIO adapter makes `1ULL << pin` unreachable above 63 by rejecting
  `pin >= 64` first, sets `pull_up_en` and `pull_down_en` explicitly on every call, and
  routes every driver result through `map_esp_err`.
- The native suite is unchanged and still adapter-free: `pio test -d tests -e native`
  reports 55/55 cases passing, and the Python gate reports 122 tests OK.

## Task Commits

Each task was committed atomically:

1. **Task 1: End-to-end Arduino time adapter — header, translation, target compile, CDB entry** — `8047d5a` (feat)
2. **Task 2: Arduino GPIO and logging adapters — enum translation and unconditional output** — `2df238d` (feat)
3. **Task 3: ESP-IDF time, GPIO and logging adapters — safe config, error mapping, no header leak** — `e57d636` (feat)

**Plan metadata:** committed separately as the SUMMARY commit.

## Framework call behind each callback

| Adapter | Callback | Framework call | Failure path |
|---------|----------|----------------|--------------|
| Arduino time | `arduino_now_ms` | `millis()` | none (clock cannot fail) |
| Arduino GPIO | `arduino_set_mode` | `pinMode()` | `PORT_ERR_INVALID_ARG` for an unknown mode |
| Arduino GPIO | `arduino_write` | `digitalWrite()` | `PORT_ERR_INVALID_ARG` for an unknown level |
| Arduino GPIO | `arduino_read` | `digitalRead()` | `PORT_ERR_INVALID_ARG` for a NULL output |
| Arduino logging | `arduino_log_write` | `log_printf()` | none (returns `void`) |
| ESP-IDF time | `espidf_now_ms` | `esp_timer_get_time() / 1000` | none (clock cannot fail) |
| ESP-IDF GPIO | `espidf_set_mode` | `gpio_config()` | `PORT_ERR_INVALID_ARG` for pin >= 64 or unknown mode; else `map_esp_err` |
| ESP-IDF GPIO | `espidf_write` | `gpio_set_level()` | `PORT_ERR_INVALID_ARG` for pin >= 64 or unknown level; else `map_esp_err` |
| ESP-IDF GPIO | `espidf_read` | `gpio_get_level()` | `PORT_ERR_INVALID_ARG` for pin >= 64 or NULL; else `PORT_OK` |
| ESP-IDF logging | `espidf_log_write` | `esp_log_write()` | none (returns `void`) |

`map_esp_err` returns `PORT_OK` for `ESP_OK` and `PORT_ERR_IO` for every other driver
result. `gpio_get_level` returns a level, not an error code, so `read` has no driver
result to map and returns `PORT_OK` after storing the level.

## Compilation-database evidence

Arduino environment (`esp32s3_arduino`), all six library sources listed; the three new
entries:

```text
.../lib/arduino/src/time.c   xtensa-esp32s3-elf-gcc ... -o .pio/build/esp32s3_arduino/lib6a2/arduino/time.c.o -c ...
.../lib/arduino/src/gpio.c   xtensa-esp32s3-elf-gcc ... -o .pio/build/esp32s3_arduino/lib6a2/arduino/gpio.c.o -c ...
.../lib/arduino/src/log.c    xtensa-esp32s3-elf-gcc ... -o .pio/build/esp32s3_arduino/lib6a2/arduino/log.c.o -c ...
```

ESP-IDF environment (`esp32s3_espidf`), 1081 database entries; the three new entries:

```text
.../lib/espidf/src/time.c   xtensa-esp32s3-elf-gcc ... -o .pio/build/esp32s3_espidf/libce0/espidf/time.o -c ...
.../lib/espidf/src/gpio.c   xtensa-esp32s3-elf-gcc ... -o .pio/build/esp32s3_espidf/libce0/espidf/gpio.o -c ...
.../lib/espidf/src/log.c    xtensa-esp32s3-elf-gcc ... -o .pio/build/esp32s3_espidf/libce0/espidf/log.o -c ...
```

Full builds (not only the database target) also compiled the objects:

```text
Compiling .pio/build/esp32s3_arduino/lib6a2/arduino/time.c.o
Compiling .pio/build/esp32s3_arduino/lib6a2/arduino/gpio.c.o
Compiling .pio/build/esp32s3_arduino/lib6a2/arduino/log.c.o
Compiling .pio/build/esp32s3_espidf/libce0/espidf/time.o
Compiling .pio/build/esp32s3_espidf/libce0/espidf/gpio.o
Compiling .pio/build/esp32s3_espidf/libce0/espidf/log.o
```

The database lives in `homeworks/0_0-toolchain-smoke/compile_commands.json`, which plan
03-07 deletes with the project. No test, script or configuration reads that path; the
evidence is temporary by design.

## Deferred adapters (D-08)

The contracts exist in `lib/port`; the framework implementations deliberately do not:

- Arduino I2C — `lib/port/include/port/i2c.h` has no `lib/arduino/src/i2c.c`
- Arduino SPI — `lib/port/include/port/spi.h` has no `lib/arduino/src/spi.c`
- ESP-IDF I2C — no `lib/espidf/src/i2c.c`
- ESP-IDF SPI — no `lib/espidf/src/spi.c`

The first homework that needs a bus owns its adapter. This also keeps the pure-C adapter
rule intact: `Wire` and `SPI` are C++ classes, so a future Arduino bus adapter would need
an explicit `.cpp` exception recorded before it lands (research Pitfall 6, assumption A8).

## Known Risks Carried Out of This Plan

| Risk | Impact | Owner |
|------|--------|-------|
| After plan 03-07 deletes the smoke project, no Phase 3 artifact compiles `lib/arduino` or `lib/espidf` | An adapter typo introduced in Phases 3–10 is invisible to `pio test -d tests` and the Python gate until Phase 11 | Phase 4 template smoke build (a scaffolded Arduino/ESP-IDF project lists its adapter) and Phase 8 changed-project CI |

This is recorded rather than repaired because a permanent target-compile project would make
the default local gate depend on the multi-minute ESP32 toolchain, which D-16 deliberately
keeps out of the per-commit surface; Phase 8 is where a changed-project CI matrix absorbs
that cost. This plan does not claim the gate survives Phase 3.

## Files Created/Modified

- `lib/arduino/include/arduino/time.h` — declares `port_time_t arduino_time_port(void)`; no framework include
- `lib/arduino/src/time.c` — `millis()` behind `arduino_now_ms`; positional aggregate factory
- `lib/arduino/include/arduino/gpio.h` — declares `port_gpio_t arduino_gpio_port(void)`; no framework include
- `lib/arduino/src/gpio.c` — `pinMode`, `digitalWrite`, `digitalRead` translation with argument rejection
- `lib/arduino/include/arduino/log.h` — declares `port_log_t arduino_log_port(void)`; no framework include
- `lib/arduino/src/log.c` — unconditional `log_printf` with an `E`/`W`/`I`/`D` prefix
- `lib/espidf/include/espidf/time.h` — declares `port_time_t espidf_time_port(void)`
- `lib/espidf/src/time.c` — `esp_timer_get_time() / 1000`
- `lib/espidf/include/espidf/gpio.h` — declares `port_gpio_t espidf_gpio_port(void)`
- `lib/espidf/src/gpio.c` — zero-initialised `gpio_config_t`, explicit pull flags, pin-range guard, `map_esp_err`, level translation
- `lib/espidf/include/espidf/log.h` — declares `port_log_t espidf_log_port(void)`
- `lib/espidf/src/log.c` — four-level mapping through `esp_log_write` with the fixed `"port"` tag

## Decisions Made

- Kept the three callbacks static and the factory as the only exported symbol, so the
  public surface is one function per adapter.
- Set `pull_up_en` and `pull_down_en` explicitly before the mode switch, then override
  only `pull_up_en` for the pull-up case. Every call therefore writes every field the
  driver reads, and the reject path never reaches `gpio_config`.
- Used a `switch` over the enum with a `default` that returns `PORT_ERR_INVALID_ARG`, so a
  value outside the enum can never be silently coerced into a framework macro.
- Reused the `(void)ctx;` idiom from the Phase 2 adapter stubs; none of these adapters owns
  state, so `ctx` stays `NULL` in every factory.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None. The Task 1 precondition held: `toolchain-xtensa-esp32s3`, `toolchain-xtensa-esp-elf`,
`framework-arduinoespressif32` and `framework-espidf` were already cached, so no new
package was fetched and the plan's `T-03-SC` disposition (installs nothing new) held.

## Known Stubs

None. Every callback delegates to a real framework call; none returns a placeholder value.

## Threat Flags

None. The new files add no network endpoint, auth path, file-access pattern or schema
change beyond the adapter-to-framework boundary already covered by T-03-35 to T-03-37.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `lib/arduino` and `lib/espidf` now expose the complete three-contract surface the
  remaining Phase 3 plans expect; plan 03-08's include scanner can assert the adapter
  headers contain only `port` includes.
- Plan 03-07 deletes `homeworks/0_0-toolchain-smoke/`, which is the only target-compile
  consumer of these adapters until a scaffolded homework lists one.
- The deferred I2C/SPI adapters remain an explicit D-08 gap, not an oversight; the
  contracts are already covered by the native contract suite.

---

*Phase: 03-shared-core-and-dependency-rule*
*Completed: 2026-10-24*

## Self-Check: PASSED

- All 12 declared adapter files exist on disk.
- All three task commits (`8047d5a`, `2df238d`, `e57d636`) and the SUMMARY commit (`0a630a3`) are ancestors of HEAD.
- `pio run -d homeworks/0_0-toolchain-smoke -e esp32s3_arduino`: SUCCESS; three adapter sources in the CDB with `xtensa-esp32s3-elf-gcc`.
- `pio run -d homeworks/0_0-toolchain-smoke -e esp32s3_espidf`: SUCCESS; three adapter sources in the CDB with `xtensa-esp32s3-elf-gcc`.
- `pio test -d tests -e native`: 55/55 cases passed, no adapter linked.
- `python3 -m unittest discover -s scripts/tests -v`: 122 tests OK.
- Self-check verdict: PASSED.

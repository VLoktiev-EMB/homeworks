---
phase: 03-shared-core-and-dependency-rule
plan: 03
subsystem: architecture
tags: [ports-and-adapters, c11, header-only, contract, gpio, i2c, spi, logging, unity]

# Dependency graph
requires:
  - phase: 03-shared-core-and-dependency-rule
    plan: 01
    provides: "port_status_t vocabulary, port_time_t contract, host-only tests/ PlatformIO project with Unity 2.6.1"
provides:
  - "port_gpio_t with set_mode, write and read over an opaque ctx"
  - "port_i2c_t with bus-level write, read and combined write_read"
  - "port_spi_t with bus-level transfer and write"
  - "port_log_t with four levels and a NULL-safe port_log_write wrapper"
  - "15-case native contract suite proving all five contracts are callable through their vtables"
affects: [03-04, 03-05, 03-06, 03-07, 03-08, 03-09]

actuals:
  tokens: 5160
  tasks: 3
  commits: 3
  plan_head_before: b035239026a43deea099ad0aa96639dd882bdc2e
  plan_head_after: 721e77a79e856f709a23231a4caadcb76a654be8

tech-stack:
  added: []
  patterns:
    - "Consumer-owned vtable struct with an opaque void *ctx and no other state"
    - "Header-only contracts: C standard includes plus port/status.h only"
    - "Positional struct initialization so a future C++ composition root compiles"
    - "Documented exception: time reads and log writes do not return port_status_t"

key-files:
  created:
    - lib/port/include/port/gpio.h
    - lib/port/include/port/i2c.h
    - lib/port/include/port/spi.h
    - lib/port/include/port/log.h
    - tests/test/test_port_contracts/test_contracts.c
  modified: []

key-decisions:
  - "I2C and SPI stay at address-plus-buffer-plus-length; no register map, page boundary, device init or native-handle accessor (ARCH-07)"
  - "GPIO pins are uint8_t because the ESP32-S3 range is 0..48 and the ESP-IDF adapter rejects a pin at or above 64"
  - "Pull-down and floating input are recorded as an additive enum extension, not an implicit default"
  - "port_log_write guards both a NULL port_log_t pointer and a NULL write callback so a zeroed sink safely discards output"
  - "Every vtable is initialized positionally, never with designated initializers, so it also compiles as C++17"

patterns-established:
  - "Contract header shell: #pragma once, C includes, extern \"C\" guard last"
  - "Each contract header states what it deliberately does not do (no framework type, no owned state, no blocking, no device behaviour)"
  - "Fakes live in the test file with the same signatures the adapters will return, so drift is a compile error"

requirements-completed: [ARCH-01, ARCH-07]

coverage:
  - id: D1
    description: "GPIO contract declares mode and level enums, three operations and an opaque ctx, and is callable through the vtable"
    requirement: ARCH-01
    verification:
      - kind: unit
        ref: "tests/test/test_port_contracts/test_contracts.c#test_gpio_ctx_reaches_every_callback"
        status: pass
      - kind: unit
        ref: "tests/test/test_port_contracts/test_contracts.c#test_gpio_write_then_read_round_trip"
        status: pass
    human_judgment: false
  - id: D2
    description: "I2C and SPI exist as narrow bus contracts with address, buffer and length only, and move data across the vtable"
    requirement: ARCH-01
    verification:
      - kind: unit
        ref: "tests/test/test_port_contracts/test_contracts.c#test_i2c_combined_write_read_passes_both_lengths"
        status: pass
      - kind: unit
        ref: "tests/test/test_port_contracts/test_contracts.c#test_spi_transfer_copies_without_allocation"
        status: pass
    human_judgment: false
  - id: D3
    description: "Logging contract exposes four levels, a void-returning write callback and a NULL-safe inline wrapper"
    requirement: ARCH-01
    verification:
      - kind: unit
        ref: "tests/test/test_port_contracts/test_contracts.c#test_log_receives_level_and_message"
        status: pass
      - kind: unit
        ref: "tests/test/test_port_contracts/test_contracts.c#test_log_null_sink_is_safe"
        status: pass
    human_judgment: false
  - id: D4
    description: "The time contract is called directly through port_time_now_ms and the callback observes its ctx"
    requirement: ARCH-01
    verification:
      - kind: unit
        ref: "tests/test/test_port_contracts/test_contracts.c#test_time_ctx_reaches_callback"
        status: pass
    human_judgment: false
  - id: D5
    description: "The status vocabulary is pinned: PORT_OK is zero and the four error members are distinct"
    requirement: ARCH-01
    verification:
      - kind: unit
        ref: "tests/test/test_port_contracts/test_contracts.c#test_status_values_are_stable"
        status: pass
    human_judgment: false
  - id: D6
    description: "The I2C and SPI shape is a bus abstraction, not a driver abstraction"
    requirement: ARCH-07
    verification: []
    human_judgment: true
    rationale: "Whether a header smuggles a framework concept expressed as a plain int is a design reading; the mechanical include scan lands in plan 03-08, so a reviewer must read the two headers against the rule."

# Metrics
duration: 2 min
completed: 2026-10-24
status: complete
---

# Phase 03 Plan 03: Port Contract Surface Summary

**GPIO, I2C, SPI and logging contracts join the existing time and status headers, and a 15-case native suite proves all five are callable through caller-owned vtables with no framework type and no owned state.**

## Performance

- **Duration:** 2 min
- **Started:** 2026-10-23T22:28:06Z
- **Completed:** 2026-10-23T22:29:36Z
- **Tasks:** 3
- **Files modified:** 5 (5 created)

## Accomplishments

- `lib/port` now declares all five ARCH-01 contracts: `time` and `status` from plan 03-01,
  plus `gpio`, `i2c`, `spi` and `log`.
- `pio test -d tests -e native` exits 0 with **34 passing cases**; the new
  `test_port_contracts` suite contributes 15 of them.
- Every contract is exercised through its vtable by a caller-provided implementation, and
  each test proves the same `ctx` pointer reaches the callback unchanged.
- I2C and SPI remain bus-level: address, buffer and length only, with no register map,
  page boundary, device initialisation, per-call timeout or native-handle accessor.
- `python3 -m unittest discover -s scripts/tests -v` still reports 122 tests OK.

## Exact vtable signatures

```c
/* port/gpio.h */
typedef struct port_gpio {
    port_status_t (*set_mode)(void *ctx, uint8_t pin, port_gpio_mode_t mode);
    port_status_t (*write)(void *ctx, uint8_t pin, port_gpio_level_t level);
    port_status_t (*read)(void *ctx, uint8_t pin, port_gpio_level_t *level);
    void *ctx;
} port_gpio_t;

/* port/i2c.h */
typedef struct port_i2c {
    port_status_t (*write)(void *ctx, uint8_t address, const uint8_t *data, size_t length);
    port_status_t (*read)(void *ctx, uint8_t address, uint8_t *data, size_t length);
    port_status_t (*write_read)(void *ctx, uint8_t address, const uint8_t *tx, size_t tx_length,
                                uint8_t *rx, size_t rx_length);
    void *ctx;
} port_i2c_t;

/* port/spi.h */
typedef struct port_spi {
    port_status_t (*transfer)(void *ctx, const uint8_t *tx, uint8_t *rx, size_t length);
    port_status_t (*write)(void *ctx, const uint8_t *data, size_t length);
    void *ctx;
} port_spi_t;

/* port/log.h */
typedef struct port_log {
    void (*write)(void *ctx, port_log_level_t level, const char *message);
    void *ctx;
} port_log_t;

static inline void port_log_write(const port_log_t *log, port_log_level_t level,
                                  const char *message);

/* port/time.h (from plan 03-01, recorded here for the closed surface) */
typedef struct port_time {
    uint32_t (*now_ms)(void *ctx);
    void *ctx;
} port_time_t;

static inline uint32_t port_time_now_ms(const port_time_t *time);
```

## Enum members and values

| Enum | Members (explicit and implicit values) |
|------|----------------------------------------|
| `port_status_t` | `PORT_OK = 0`, `PORT_ERR_TIMEOUT = 1`, `PORT_ERR_IO = 2`, `PORT_ERR_INVALID_ARG = 3`, `PORT_ERR_NOT_SUPPORTED = 4` |
| `port_gpio_mode_t` | `PORT_GPIO_INPUT = 0`, `PORT_GPIO_OUTPUT = 1`, `PORT_GPIO_INPUT_PULLUP = 2` |
| `port_gpio_level_t` | `PORT_GPIO_LOW = 0`, `PORT_GPIO_HIGH = 1` |
| `port_log_level_t` | `PORT_LOG_ERROR = 0`, `PORT_LOG_WARN = 1`, `PORT_LOG_INFO = 2`, `PORT_LOG_DEBUG = 3` |

`test_status_values_are_stable` pins `PORT_OK == 0` and the pairwise distinctness of the four
error members.

## Named test cases (`tests/test/test_port_contracts/test_contracts.c`)

| Area | Test cases |
|------|------------|
| GPIO | `test_gpio_ctx_reaches_every_callback`, `test_gpio_write_then_read_round_trip`, `test_gpio_invalid_level_is_rejected`, `test_gpio_two_contexts_are_independent` |
| I2C | `test_i2c_write_then_read_loopback`, `test_i2c_combined_write_read_passes_both_lengths`, `test_i2c_null_buffer_is_rejected` |
| SPI | `test_spi_transfer_copies_without_allocation`, `test_spi_write_records_the_transmitted_bytes`, `test_bus_contracts_use_their_own_context` |
| Time | `test_time_ctx_reaches_callback` |
| Logging | `test_log_receives_level_and_message`, `test_log_null_sink_is_safe`, `test_log_ctx_reaches_the_callback` |
| Status | `test_status_values_are_stable` |

## Rationale text recorded in `gpio.h`

Pin width:

> A pin is `uint8_t` because this phase targets the ESP32-S3 GPIO range (0..48); the
> ESP-IDF adapter rejects a pin at or above 64, so the narrower field cannot silently
> truncate a valid board pin.

Missing modes:

> Pin modes this phase can express. Pull-down input and floating input are deliberately
> absent: an adapter that accepted them would have to invent a default, so a future need is
> an additive enum member rather than an implicit behaviour.

## Why I2C and SPI are bus-level, not driver-level

`ARCHITECTURE.md` states the rule as "add a port only when the second homework needs the
same capability; abstract the bus, not the driver". `port_i2c_t` therefore takes a 7-bit
address, a buffer and a length and performs one bus transaction per call; `port_spi_t` takes
a transmit buffer, a receive buffer and a length, leaving chip-select, clock mode and
frequency to adapter-owned bus configuration. Register maps, page boundaries, device
initialisation and display or sensor behaviour stay in the homework consumer — the same
boundary that keeps `ssd1306_write(port_i2c_t *, ...)` reusable while a
`display_hal_init/draw/log/delay` mega-interface is not. A consumer that needs two devices
holds two bus instances rather than widening the contract. No handle accessor, per-call
timeout or device-state struct was added, because no consumer yet justifies one (D-08,
research Assumption A4).

## Files Created/Modified

- `lib/port/include/port/gpio.h` — mode and level enums, three operations, opaque `ctx`, pin-width and missing-mode rationale
- `lib/port/include/port/i2c.h` — bus-level write, read and combined write_read with a 7-bit address rule
- `lib/port/include/port/spi.h` — bus-level transfer and write with adapter-owned chip-select, clock mode and frequency
- `lib/port/include/port/log.h` — four levels, void-returning write callback and the NULL-safe `port_log_write` wrapper
- `tests/test/test_port_contracts/test_contracts.c` — local GPIO, I2C, SPI, clock and log implementations with 15 named cases

## Decisions Made

- Included the "what this contract does not do" invariant paragraph in GPIO at creation time
  and in I2C/SPI at creation time, so Task 3 needed no edit to those three headers.
- `port_log_write` guards both a NULL `port_log_t *` and a NULL `write` callback. Without the
  guard the documented "NULL sink discards output" rule would be a null dereference; the
  guard is the smallest way to make the documentation true.
- Fakes record the observed `ctx` pointer (GPIO and logging) rather than only inferring
  plumbing from state mutation, so the "ctx reaches every callback" claims are direct
  assertions.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Plan verify command defect] Task 2's header assertion used an out-of-scope variable**
- **Found during:** Task 2 verification
- **Issue:** the plan's snippet builds `bad` with `[bad.append((f,n)) for f,need in files.items() if ...]`.
  `n` is unbound in that comprehension's result expression, so the check raised
  `NameError: name 'n' is not defined` instead of reporting a result.
- **Fix:** no code change. Ran the equivalent flat comprehension
  `[(f,n) for f,need in c.items() for n in need if n not in pathlib.Path(f).read_text()]`,
  which preserves the intent (both headers exist and contain every required token).
- **Files modified:** none (verification only)
- **Verification:** `bad= []` after the header wording fix below
- **Committed in:** n/a (verification-only; evidence in this summary)

**2. [Rule 1 - Documentation token] `spi.h` said "Chip-select" where the verify required `chip-select`**
- **Found during:** Task 2 verification
- **Issue:** the sentence began with a capital C, so the case-sensitive token check for the
  documented bus rule reported `('lib/port/include/port/spi.h', 'chip-select')` missing.
- **Fix:** rephrased to "The chip-select line, clock mode and frequency are bus
  configuration..." — the rule is unchanged, the required lowercase token now appears.
- **Files modified:** `lib/port/include/port/spi.h`
- **Verification:** the equivalent assertion reports `bad= []`
- **Committed in:** `0085201` (part of Task 2 commit)

---

**Total deviations:** 2 auto-fixed (2 bugs, both in verification/documentation rather than behaviour)
**Impact on plan:** Neither changes the shipped API. The contract surface, the includes and
the test behaviour are exactly as planned.

## Issues Encountered

None beyond the two verification-level deviations above. The tracer feedback gate ran after
Task 1 (not auto mode, `human_verify_mode = end-of-phase`, automated verify only): the suite
passed end-to-end, so expansion continued without a checkpoint.

## Known Stubs

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- All five contracts are declared and callable, so plans 03-04 (`lib/host` fakes), 03-05
  (`lib/common` expansion) and 03-06 (framework adapters for time, GPIO and logging) can
  implement against a fixed surface.
- I2C and SPI have no adapter in this phase by design (D-08); the first homework that needs
  one owns that implementation.
- `tests/test/test_port_contracts/` is the place a new contract's call-through test joins.

---
*Phase: 03-shared-core-and-dependency-rule*
*Completed: 2026-10-24*

## Self-Check: PASSED

- All five declared files exist on disk.
- All three task commits (`fb3c9dc`, `0085201`, `721e77a`) are ancestors of HEAD.
- `pio test -d tests -e native`: 34/34 passed.
- `python3 -m unittest discover -s scripts/tests -v`: 122 tests OK.
- Self-check verdict: PASSED.

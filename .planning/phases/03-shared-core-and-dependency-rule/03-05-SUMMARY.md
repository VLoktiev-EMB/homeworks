---
phase: 03-shared-core-and-dependency-rule
plan: 05
subsystem: testing
tags: [c11, host-fakes, test-doubles, gpio, i2c, spi, logging, unity, allocation-free, ports-and-adapters]

# Dependency graph
requires:
  - phase: 03-shared-core-and-dependency-rule
    plan: 03-01
    provides: "tests/ native PlatformIO project with Unity 2.6.1 and the caller-owned fake conventions"
  - phase: 03-shared-core-and-dependency-rule
    plan: 03-03
    provides: "port_gpio_t, port_i2c_t, port_spi_t and port_log_t contracts"
provides:
  - "Bounded, caller-owned GPIO recording double with a defined configured flag and one-shot failure injection"
  - "Single-device loopback I2C double and recording SPI double"
  - "Capturing four-level log sink with bounded storage and a drop counter"
  - "An 18-case Unity suite covering normal, bounded and forced-error paths for all four fakes"
affects: [03-06, 03-08, 03-09, 11]

actuals:
  tokens: 7686
  tasks: 3
  commits: 3
  plan_head_before: 04ad3e5fa1bca34c352bdadf4badc37389107edd
  plan_head_after: a293a320c3e42b87775f86dabacc959f561931c4

tech-stack:
  added: []
  patterns:
    - "Caller-owned allocation-free test doubles bounded by public capacity macros"
    - "One-shot fail_next injection consumed only after argument and bound checks"
    - "Fakes return the same port_<contract>_t type the real adapters return"
    - "Overflow is counted (dropped) or rejected (PORT_ERR_INVALID_ARG), never truncated silently"

key-files:
  created:
    - lib/host/include/host/fake_gpio.h
    - lib/host/src/fake_gpio.c
    - lib/host/include/host/fake_i2c.h
    - lib/host/src/fake_i2c.c
    - lib/host/include/host/fake_spi.h
    - lib/host/src/fake_spi.c
    - lib/host/include/host/fake_log.h
    - lib/host/src/fake_log.c
    - tests/test/test_host_fakes/test_host_fakes.c
  modified: []

key-decisions:
  - "The log sink has no fail_next: the port_log_t write callback returns void, so there is no port_status_t to inject (research assumption A1)"
  - "configured[pin] means set_mode or write was seen for that pin; read never sets it"
  - "host_fake_i2c_write_read echoes the transmitted bytes; rx_length may not exceed tx_length, because one buffer models one device per transaction"
  - "host_fake_log_reset clears count and dropped only; count remains the authority and lines at or above it are inaccessible"
  - "host_fake_i2c_preset is a setup helper with no status return; a NULL pointer or an oversized length leaves the stored buffer unchanged"

patterns-established:
  - "Fixed-capacity array plus a public macro as the bound for every fake"
  - "One-shot forced_status consumed after validation, so an invalid request still reports its own error"
  - "Cross-fake contract test assigns each factory result to its real port type"

requirements-completed: [ARCH-01, ARCH-03]

coverage:
  - id: D1
    description: "GPIO double records modes, levels and write/read counts in a caller-owned 64-entry array, rejects out-of-range pins and NULL outputs, and scripts one failure"
    requirement: ARCH-03
    verification:
      - kind: unit
        ref: "tests/test/test_host_fakes/test_host_fakes.c#test_fake_gpio_records_writes"
        status: pass
      - kind: unit
        ref: "tests/test/test_host_fakes/test_host_fakes.c#test_fake_gpio_out_of_range_pin_is_rejected"
        status: pass
      - kind: unit
        ref: "tests/test/test_host_fakes/test_host_fakes.c#test_fake_gpio_forced_status_is_one_shot"
        status: pass
      - kind: unit
        ref: "tests/test/test_host_fakes/test_host_fakes.c#test_fake_gpio_set_mode_and_write_mark_configured"
        status: pass
    human_judgment: false
  - id: D2
    description: "I2C double loops one transaction through a bounded 32-byte buffer, records the last address, rejects oversized and NULL requests, and keeps two instances independent"
    requirement: ARCH-03
    verification:
      - kind: unit
        ref: "tests/test/test_host_fakes/test_host_fakes.c#test_fake_i2c_write_then_read"
        status: pass
      - kind: unit
        ref: "tests/test/test_host_fakes/test_host_fakes.c#test_fake_i2c_combined_transfer"
        status: pass
      - kind: unit
        ref: "tests/test/test_host_fakes/test_host_fakes.c#test_fake_i2c_oversized_write_is_rejected"
        status: pass
      - kind: unit
        ref: "tests/test/test_host_fakes/test_host_fakes.c#test_fake_i2c_two_instances_hold_separate_buffers"
        status: pass
    human_judgment: false
  - id: D3
    description: "SPI double records transmitted bytes, loops them back only when a receive buffer is supplied, and rejects transfers above 32 bytes"
    requirement: ARCH-03
    verification:
      - kind: unit
        ref: "tests/test/test_host_fakes/test_host_fakes.c#test_fake_spi_loops_back"
        status: pass
      - kind: unit
        ref: "tests/test/test_host_fakes/test_host_fakes.c#test_fake_spi_write_records_without_receive_buffer"
        status: pass
    human_judgment: false
  - id: D4
    description: "Log sink captures level and text for 32 lines of 64 bytes, truncates long text safely, counts overflow instead of overwriting, and returns NULL for an out-of-range index"
    requirement: ARCH-03
    verification:
      - kind: unit
        ref: "tests/test/test_host_fakes/test_host_fakes.c#test_fake_log_captures_level_and_text"
        status: pass
      - kind: unit
        ref: "tests/test/test_host_fakes/test_host_fakes.c#test_fake_log_truncates_long_text_safely"
        status: pass
      - kind: unit
        ref: "tests/test/test_host_fakes/test_host_fakes.c#test_fake_log_drops_after_capacity"
        status: pass
      - kind: unit
        ref: "tests/test/test_host_fakes/test_host_fakes.c#test_fake_log_at_out_of_range_is_null"
        status: pass
    human_judgment: false
  - id: D5
    description: "All five fakes are assignment-compatible with the real contract types, so signature drift is a compile error"
    requirement: ARCH-01
    verification:
      - kind: unit
        ref: "tests/test/test_host_fakes/test_host_fakes.c#test_all_fakes_expose_the_real_contract_types"
        status: pass
      - kind: unit
        ref: "tests/test/test_host_fakes/test_host_fakes.c#test_gpio_fake_returns_the_real_gpio_contract_type"
        status: pass
    human_judgment: false
  - id: D6
    description: "lib/host contains no framework header, no common header and no production policy"
    requirement: ARCH-03
    verification: []
    human_judgment: true
    rationale: "The include scan proves which headers appear, but whether a fake has grown a policy, schedule or state machine is a design reading; the textual include matrix arrives in plan 03-08."

duration: 2 min
completed: 2026-10-24
status: complete
---

# Phase 03 Plan 05: Deterministic Host Test Doubles Summary

**Recording GPIO, single-device loopback I2C, recording SPI and a bounded capturing log sink, each returning the real `port_*_t` contract type and each proven by normal, bounded and forced-error Unity cases.**

## Performance

- **Duration:** 2 min
- **Started:** 2026-10-23T22:31:21Z
- **Completed:** 2026-10-23T22:33:27Z
- **Tasks:** 3
- **Files modified:** 9 (9 created, 0 modified)

## Accomplishments

- `lib/host` now provides deterministic doubles for all five contracts: `fake_time` from
  plan 03-01 plus `fake_gpio`, `fake_i2c`, `fake_spi` and `fake_log` from this plan (D-07).
- `pio test -d tests -e native` exits 0 with **73 Unity cases across 7 suites**; the new
  `test_host_fakes` suite contributes 18 of them.
- Every fake returns the `port_<contract>_t` type the real adapters will return, and the
  cross-fake test assigns each factory result to that type, so a signature drift is a
  compile error rather than a silently passing test (ARCH-03, Pitfall C12).
- Every fake is caller-owned and allocation-free: GPIO is a 64-entry array, I2C and SPI
  keep 32-byte buffers, and the log sink holds 32 lines of 64 characters.
- Out-of-bound requests are reported, never silently truncated: an out-of-range pin, an
  oversized transfer, an under-sized read or a NULL buffer returns
  `PORT_ERR_INVALID_ARG`, and a full log sink increments `dropped` instead of overwriting.
- `python3 -m unittest discover -s scripts/tests -v` still reports 122 tests OK.
- An include scan of `lib/host/{include,src}` shows only `port` headers and C standard
  headers; no framework or `common` header appears.

## Task Commits

Each task was committed atomically:

1. **Task 1: End-to-end GPIO double — record, replay, bound, fail once** - `f1be43f` (feat)
2. **Task 2: I2C single-device loopback and SPI recording doubles** - `82872bd` (feat)
3. **Task 3: Capturing log sink and the cross-fake contract suite** - `a293a32` (feat)

**Plan metadata:** committed after this file was written (docs: complete plan)

## Exact Bounds and Public Surface

| Header | Public constants | Struct and accessors |
|--------|------------------|----------------------|
| `host/fake_gpio.h` | `HOST_FAKE_GPIO_PINS` = 64 | `host_fake_gpio_t`, `host_fake_gpio_reset`, `host_fake_gpio_fail_next`, `host_fake_gpio_port` |
| `host/fake_i2c.h` | `HOST_FAKE_I2C_CAPACITY` = 32 | `host_fake_i2c_t`, `host_fake_i2c_reset`, `host_fake_i2c_fail_next`, `host_fake_i2c_preset`, `host_fake_i2c_port` |
| `host/fake_spi.h` | `HOST_FAKE_SPI_CAPACITY` = 32 | `host_fake_spi_t`, `host_fake_spi_reset`, `host_fake_spi_fail_next`, `host_fake_spi_port` |
| `host/fake_log.h` | `HOST_FAKE_LOG_LINES` = 32, `HOST_FAKE_LOG_TEXT` = 64 | `host_fake_log_line_t`, `host_fake_log_t`, `host_fake_log_reset`, `host_fake_log_port`, `host_fake_log_count`, `host_fake_log_at` |

`host_fake_gpio_t` holds `mode[64]`, `level[64]`, `configured[64]`, `forced_status`, `writes`
and `reads`. `host_fake_i2c_t` holds `buffer[32]`, `length`, `last_address`, `transactions`
and `forced_status`. `host_fake_spi_t` holds `tx[32]`, `length`, `transfers` and
`forced_status`. `host_fake_log_t` holds `lines[32]`, `count` and `dropped`.

## Failure-Injection Convention

`host_fake_<contract>_fail_next(fake, status)` stores a one-shot status. Any value other
than `PORT_OK` is returned by the next operation and immediately replaced by `PORT_OK`;
`PORT_OK` therefore means "no forcing". Validation runs first, so an out-of-range pin or a
NULL output still returns `PORT_ERR_INVALID_ARG` and leaves the forcing in place.

The log sink deliberately has no `fail_next`: `port_log_t::write` returns `void`, so there
is no `port_status_t` to inject. This is the same documented exception recorded in
`port/log.h` and research assumption A1.

## Configured-Flag Rule

`configured[pin]` has exactly one meaning: this fake has seen a `set_mode` or a `write` for
that pin. Both set it; `read` never does, because replaying a stored level says nothing
about how the pin was configured. `host_fake_gpio_reset` clears it.
`test_fake_gpio_set_mode_and_write_mark_configured` pins all three cases.

## Log Overflow Convention

A message is copied up to `HOST_FAKE_LOG_TEXT - 1` bytes and always terminated with a null
byte, and the line still counts as recorded. Once `count == HOST_FAKE_LOG_LINES`, each
further message increments `dropped` and stores nothing. `host_fake_log_count` and
`host_fake_log_at` treat `count` as the sole authority; `host_fake_log_at` returns `NULL`
for an index at or above `count`.

## I2C Single-Device Limitation

`fake_i2c.h` states that one instance models one device per transaction, not a
multi-device bus: it records only the last address and owns one buffer, so two devices at
different addresses need two fake instances. `test_fake_i2c_two_instances_hold_separate_buffers`
proves the limitation is per instance rather than per type. `host_fake_i2c_write_read`
records `tx` and loops that buffer into `rx`; `rx_length` may not exceed `tx_length`,
because the single buffer models one transaction without modelling a device.

## Named Test Cases

- GPIO: `test_fake_gpio_records_writes`, `test_fake_gpio_replays_levels`,
  `test_fake_gpio_out_of_range_pin_is_rejected`, `test_fake_gpio_forced_status_is_one_shot`,
  `test_fake_gpio_set_mode_and_write_mark_configured`,
  `test_gpio_fake_returns_the_real_gpio_contract_type`
- I2C: `test_fake_i2c_write_then_read`, `test_fake_i2c_combined_transfer`,
  `test_fake_i2c_oversized_write_is_rejected`,
  `test_fake_i2c_two_instances_hold_separate_buffers`
- SPI: `test_fake_spi_loops_back`, `test_fake_spi_write_records_without_receive_buffer`
- Cross-fake: `test_bus_fakes_keep_separate_contexts`
- Log: `test_fake_log_captures_level_and_text`, `test_fake_log_truncates_long_text_safely`,
  `test_fake_log_drops_after_capacity`, `test_fake_log_at_out_of_range_is_null`
- Contract surface: `test_all_fakes_expose_the_real_contract_types`

## Files Created/Modified

- `lib/host/include/host/fake_gpio.h` — 64-pin bound, struct, factory, one-shot force and the configured-flag rule
- `lib/host/src/fake_gpio.c` — `set_mode`, `write` and `read` callbacks plus reset and failure injection
- `lib/host/include/host/fake_i2c.h` — 32-byte bound, single-device note, preset and factory
- `lib/host/src/fake_i2c.c` — write, read and combined `write_read` over the bounded buffer
- `lib/host/include/host/fake_spi.h` — 32-byte bound, recording struct and factory
- `lib/host/src/fake_spi.c` — transfer and write callbacks
- `lib/host/include/host/fake_log.h` — 32 x 64 bounded storage, line type, accessors and factory
- `lib/host/src/fake_log.c` — capture callback, truncation, drop counting and accessors
- `tests/test/test_host_fakes/test_host_fakes.c` — 18 named cases for all four fakes and the shared contract surface

## Decisions Made

- Kept the fakes as data recorders with no policy, schedule or state machine: they store,
  replay, loop back or fail on request, which is the line ARCH-03 and D-10 draw.
- Consumed the forced status only after argument and bound validation, so an invalid
  request reports its own error instead of masking it with a scripted one.
- Chose to echo `tx` in `host_fake_i2c_write_read` and to require `rx_length <= tx_length`,
  which follows the plan's "one buffer, one device per transaction" wording without
  inventing a register map.
- Documented `host_fake_i2c_preset` as a setup helper with no status return; a NULL or
  oversized preset leaves the stored buffer unchanged rather than truncating silently.
- Left `count` as the log sink's authority instead of clearing every stored line on reset;
  stale bytes above `count` are never exposed by `host_fake_log_at`.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Plan verify command defect] Task 2's header assertion used an unbound `n`**
- **Found during:** Task 2 verification
- **Issue:** the plan's snippet builds `bad` with
  `[bad.append((f,n)) for f,need in files.items() if ...]`; `n` is unbound in that
  comprehension's result expression, so the check raises `NameError` instead of reporting.
- **Fix:** no code change. Ran the equivalent flat comprehension
  `[(f,n) for f,need in files.items() for n in need if n not in read_text]`, preserving the
  intent (both headers exist and contain every required token).
- **Files modified:** none (verification only)
- **Verification:** `bad= []`
- **Committed in:** n/a (verification-only; evidence in this summary)

**2. [Rule 1 - Plan verify command defect] Task 3's header assertion repeats the unbound `n`**
- **Found during:** Task 3 verification
- **Issue:** the same `bad.append((f,n))` pattern appears in Task 3's snippet, with the same
  `NameError` result.
- **Fix:** no code change. Ran the equivalent assertion for the log header and the five
  fake-header existence check.
- **Files modified:** none (verification only)
- **Verification:** `missing= [] types= []`
- **Committed in:** n/a (verification-only; evidence in this summary)

---

**Total deviations:** 2 auto-fixed (2 plan verify-command defects, both verification-only)
**Impact on plan:** No shipped behaviour changes. The implementation, the public surface and
the test suite are exactly as planned.

## Issues Encountered

- The plan's must-have says "each fake can be scripted to fail once through a `fail_next`
  setter", but `port_log_t::write` returns `void`; the log sink therefore cannot return a
  scripted `port_status_t`. The four status-returning contracts (time is read-only, so
  GPIO, I2C and SPI) carry `fail_next`; the log sink deliberately does not. This is a
  wording inconsistency in the plan, not missing work.
- The first `pio test` run in the sandbox reported a denied outbound connection to a
  PlatformIO registry host; the cached toolchain and Unity still built and ran 73/73 cases,
  so no result was affected. No authentication gate occurred.

## Threat Surface

All three threats in the plan's register are mitigated as designed: each bound is a named
constant with a named rejection or drop-counter test (T-03-34), `host` is linked only from
`tests/` and this plan added no firmware dependency (T-03-33), and no package was installed
(T-03-SC). No new surface beyond the plan was introduced.

## Known Stubs

None. No placeholder values, skipped tests or unimplemented paths were introduced.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `lib/host` is a complete fake surface for the five contracts, so the 20-run determinism
  proof in plan 03-09 can exercise GPIO, buses and logging without hardware.
- The capacity macros stay public, so a future block transfer can raise a bound without
  changing a contract.
- The Phase 2 stub pair `lib/host/include/host.h` and `lib/host/src/host.c` remains
  untouched as planned; plan 03-07 retires it.
- Mock drift is proven only at compile time by the shared type; behavioural conformance
  against real adapters would need hardware and is out of scope (SCALE-03).

---
*Phase: 03-shared-core-and-dependency-rule*
*Completed: 2026-10-24*

## Self-Check: PASSED

- All 9 declared files exist on disk.
- All three task commits (`f1be43f`, `82872bd`, `a293a32`) are ancestors of HEAD.
- `pio test -d tests -e native`: 73 Unity cases across 7 suites, exit 0.
- `python3 -m unittest discover -s scripts/tests -v`: 122 tests OK.
- `git rev-list --count 04ad3e5..HEAD` measures 3 commits, matching the three tasks.
- Self-check verdict: PASSED.

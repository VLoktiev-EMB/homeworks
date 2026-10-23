---
phase: 03-shared-core-and-dependency-rule
verified: 2026-10-23T22:59:35Z
status: passed
score: 75/76 must-haves verified
covered_files: [".planning/phases/03-shared-core-and-dependency-rule/03-01-PLAN.md", ".planning/phases/03-shared-core-and-dependency-rule/03-01-SUMMARY.md", ".planning/phases/03-shared-core-and-dependency-rule/03-02-PLAN.md", ".planning/phases/03-shared-core-and-dependency-rule/03-02-SUMMARY.md", ".planning/phases/03-shared-core-and-dependency-rule/03-03-PLAN.md", ".planning/phases/03-shared-core-and-dependency-rule/03-03-SUMMARY.md", ".planning/phases/03-shared-core-and-dependency-rule/03-04-PLAN.md", ".planning/phases/03-shared-core-and-dependency-rule/03-04-SUMMARY.md", ".planning/phases/03-shared-core-and-dependency-rule/03-05-PLAN.md", ".planning/phases/03-shared-core-and-dependency-rule/03-05-SUMMARY.md", ".planning/phases/03-shared-core-and-dependency-rule/03-06-PLAN.md", ".planning/phases/03-shared-core-and-dependency-rule/03-06-SUMMARY.md", ".planning/phases/03-shared-core-and-dependency-rule/03-07-PLAN.md", ".planning/phases/03-shared-core-and-dependency-rule/03-07-SUMMARY.md", ".planning/phases/03-shared-core-and-dependency-rule/03-08-PLAN.md", ".planning/phases/03-shared-core-and-dependency-rule/03-08-SUMMARY.md", ".planning/phases/03-shared-core-and-dependency-rule/03-09-PLAN.md", ".planning/phases/03-shared-core-and-dependency-rule/03-09-SUMMARY.md", ".pre-commit-config.yaml", "AGENTS.md", "lib/arduino/include/arduino/gpio.h", "lib/arduino/include/arduino/log.h", "lib/arduino/include/arduino/time.h", "lib/arduino/library.json", "lib/arduino/src/gpio.c", "lib/arduino/src/log.c", "lib/arduino/src/time.c", "lib/common/include/common/crc.h", "lib/common/include/common/hex.h", "lib/common/include/common/ring_buffer.h", "lib/common/include/common/timing.h", "lib/common/library.json", "lib/common/src/crc.c", "lib/common/src/hex.c", "lib/common/src/ring_buffer.c", "lib/common/src/timing.c", "lib/espidf/include/espidf/gpio.h", "lib/espidf/include/espidf/log.h", "lib/espidf/include/espidf/time.h", "lib/espidf/library.json", "lib/espidf/src/gpio.c", "lib/espidf/src/log.c", "lib/espidf/src/time.c", "lib/host/include/host/fake_gpio.h", "lib/host/include/host/fake_i2c.h", "lib/host/include/host/fake_log.h", "lib/host/include/host/fake_spi.h", "lib/host/include/host/fake_time.h", "lib/host/library.json", "lib/host/src/fake_gpio.c", "lib/host/src/fake_i2c.c", "lib/host/src/fake_log.c", "lib/host/src/fake_spi.c", "lib/host/src/fake_time.c", "lib/port/include/port/gpio.h", "lib/port/include/port/i2c.h", "lib/port/include/port/log.h", "lib/port/include/port/spi.h", "lib/port/include/port/status.h", "lib/port/include/port/time.h", "lib/port/library.json", "partitions/default_16MB.csv", "platformio.shared.ini", "scripts/architecture/allowlist.json", "scripts/check_architecture.py", "scripts/tests/test_architecture_headers.py", "scripts/tests/test_check_architecture.py", "scripts/tests/test_gitignore.py", "scripts/tests/test_native_determinism.py", "scripts/tests/test_native_purity.py", "scripts/tests/test_pio_scripts.py", "tests/platformio.ini", "tests/src/main.c", "tests/test/test_common_crc/test_crc.c", "tests/test/test_common_hex/test_hex.c", "tests/test/test_common_ring_buffer/test_ring_buffer.c", "tests/test/test_common_timing/test_timing.c", "tests/test/test_host_fake_time/test_fake_time.c", "tests/test/test_host_fakes/test_host_fakes.c", "tests/test/test_port_contracts/test_contracts.c"]
covered_digest: "v3:sha256:06f35cc6514d985a779ee67dfd97094bb3c4e6918de37708835887ac2c383792"
behavior_unverified: 0
overrides_applied: 0
deferred:
  - truth: "`pio run -d homeworks/0_0-toolchain-smoke -e esp32s3_arduino -t compiledb` and the equivalent `esp32s3_espidf` run both succeed and their databases list the new adapter sources (03-06.6)."
    addressed_in: "Phase 4 and Phase 8"
    evidence: "Phase 4 success criterion 2: 'The scaffolded project contains ... and builds immediately'; Phase 8 success criterion 2: 'CI builds and unit-tests changed projects on every pull request'. The smoke project is retired by plan 03-07 by design; 03-06 records the post-Phase-3 target-compile gap as a known risk with those owners."
human_verification:
  - test: "Read docs/decisions/0008-common-depends-on-port.md against docs/decisions/0002-ports-and-adapters-no-universal-hal.md and confirm the new record supersedes exactly the dependency-rule sentence and nothing else."
    expected: "ADR-0008's supersession claim names only the dependency-rule sentence; ADR-0002 stays accepted and unedited. The blob hash already proves the file was not rewritten."
    why_human: "Whether prose supersedes the intended sentence and nothing more is a reading judgement; no test can assert the scope of a supersession."
  - test: "Read lib/port/include/port/i2c.h and spi.h and confirm they describe a bus abstraction, not a driver or universal HAL, and that no framework concept is smuggled through a plain integer."
    expected: "Bus-level read/write/transfer only; no register map, page, display, device initialisation or native-handle escape hatch."
    why_human: "The include scan proves framework headers areabsent, but API shape is a design reading (ARCH-07)."
  - test: "Read the CRC and ring-buffer header prose and judge whether the disclaimers are strong enough."
    expected: "CRC is stated as data integrity, not authentication or trust; the ring buffer is stated as neither ISR-safe nor lock-free."
    why_human: "Automation proves the words exist, not that they prevent a reader from over-claiming."
  - test: "Read lib/host/src/*.c and confirm the fakes record, loop back or fail on request and contain no policy, schedule or state machine."
    expected: "No production decision logic in any fake; only recording, loopback, bounds checks and one-shot failure injection."
    why_human: "No mechanical rule distinguishes a recording stub from a small policy (ARCH-03)."
  - test: "Read lib/arduino/src/*.c and lib/espidf/src/*.c and confirm every callback is one framework call plus enum mapping, with no business logic and no blocking."
    expected: "Each callback translates one call and returns PORT_OK or a mapped port_status_t; no debounce, scheduling or decision logic."
    why_human: "Adapter thinness is a design reading; the checker only proves the include edges."
  - test: "Confirm the scope call recorded in ADR-0008 D-08 and plan 03-06: I2C/SPI framework adapters are deferred, and the post-Phase-3 target-compile gate is owned by Phase 4 and Phase 8."
    expected: "The deferral is acceptable for this milestone and the named owners actually cover the gap."
    why_human: "Whether a deferral and its owners are adequate is a scope judgement, not an executable check."
  - test: "Decide whether the test-tier prohibitions that currently rely on one-off verification rather than a committed regression test need permanent tests."
    expected: "Either accept the one-off evidence or add a test for ADR-0002 immutability and for the ESP-IDF pin guard that precedes the `1ULL << pin` shift."
    why_human: "The properties are verified (blob hash equal; guard present before the shift), but neither has a permanent test, so a future edit could reintroduce the risk silently."
  - test: "Confirm the empty allowlist and its non-empty-reason/stale-entry rules are the intended permanent policy for scripts/architecture/allowlist.json."
    expected: "No entries now; any future entry must name a path, a rule and a non-empty reason, and a stale entry fails the run."
    why_human: "The schema is testable; whether a future reason justifies an exception is a reviewer judgement."
---

# Phase 03: Shared Core and Dependency Rule — Verification Report

**Phase goal:** A minimal, framework-free shared C core with enforced dependency edges and a deterministic native test suite.
**Verified:** 2026-10-23T22:59:35Z
**Status:** human_needed
**Re-verification:** No — initial verification (no previous VERIFICATION.md existed).

## Goal Achievement

### Roadmap success criteria

| # | Success criterion | Status | Evidence |
|---|---|---|---|
| 1 | `common` and `port` build in the native environment with no framework headers and no target toolchain | ✓ VERIFIED | `pio run -d tests -e native -t compiledb` writes 11 entries, all `/usr/bin/gcc`, no xtensa/riscv/framework token; all nine shared sources present (see Data-Flow Trace). |
| 2 | The top-level `tests/` PlatformIO project runs the shared Unity suite and passes | ✓ VERIFIED | `pio test -d tests -e native`: 73/73 cases in 7 suites, exit 0. |
| 3 | `check_architecture.py` rejects a forbidden include and the native compile gate fails the build | ✓ VERIFIED | Independent fixture: `#include <Arduino.h>` in `lib/common/src/timing.c` → exit 1 naming file and rule; `test_native_purity.FrameworkIncludeFixtureTests` shows the same include fails `pio run -d tests -e native`. |
| 4 | The suite produces identical results over 20 consecutive runs using fake time from `lib/host` | ✓ VERIFIED | `test_native_determinism`: 20 runs, one identical digest containing all seven suites, each run exit 0. |
| 5 | Public headers expose only C contracts with `extern "C"`; no universal HAL or whole-driver abstraction | ✓ VERIFIED | 21 headers; `test_architecture_headers` (7 tests) proves `#pragma once`, complete `extern "C"` guard, ASCII, per-library include sets and no framework type names. |

### Observable truths (per plan)

| # | Truth | Status | Evidence |
|---|---|---|---|
| 03-01.1 | `pio test -d tests -e native` exits 0 with a `[PASSED]` row for every declared test | ✓ VERIFIED | 73/73 passed on the real tree. |
| 03-01.2 | `tests/platformio.ini` overrides `extra_scripts` with `pre:../scripts/pio/compiledb.py`, repeats `-std=c11 -Wall -Wextra`, sets `test_build_src = false` | ✓ VERIFIED | File read; `test_pio_scripts.py:235` asserts the literal value. |
| 03-01.3 | `port/time.h` declares `port_time_t` (one `uint32_t (*now_ms)(void*)` + `void *ctx`), an inline wrapper, `#pragma once`, `extern "C"`, only `<stdint.h>` | ✓ VERIFIED | Header read; header suite passes. |
| 03-01.4 | `common/timing.c` reads no clock: unsigned elapsed, signed expiry, borrowed `const port_time_t *`; ~24.85-day horizon documented | ✓ VERIFIED | Source read; `test_timing.c` covers wrap, zero, deadline and beyond-horizon. |
| 03-01.5 | `common_debounce_update` rejects NULL state, NULL time and NULL `now_ms` safely | ✓ VERIFIED | Source read; `test_debounce_null_*` pass. |
| 03-01.6 | Fake time advances only through `host_fake_time_advance`, resets through `host_fake_time_reset`, instances are independent | ✓ VERIFIED | Source read; `test_host_fake_time` covers reset, advance, wrap and isolation. |
| 03-01.7 | Unity pinned as `throwtheswitch/Unity@2.6.1`; installed manifest reports 2.6.1 | ✓ VERIFIED | `tests/platformio.ini`; `tests/.pio/libdeps/native/Unity/library.json` reports `2.6.1`. |
| 03-01.8 | `tests/src/main.c` exists only for `compiledb`; `test_build_src = false` keeps it out of test binaries | ✓ VERIFIED | `compiledb` database contains `src/main.c` (resolved `tests/src/main.c`); test binaries exclude it. |
| 03-01.9 | `lib/port` owns no global mutable state | ✓ VERIFIED | Header-only library; all state is behind caller-owned `void *ctx`; no object files under `lib/port`. |
| 03-02.1 | ADR-0008 states the single allowed edge `common → port`, `port` depends on nothing, and supersedes only the dependency-rule sentence of ADR-0002 | ✓ VERIFIED | Record read; contains `This record supersedes exactly one sentence of`. |
| 03-02.2 | ADR-0008 fixes `void *ctx` semantics: no global mutable state; state belongs to the adapter or test double | ✓ VERIFIED | Record read; matches `port/time.h`, `gpio.h`, `log.h` prose. |
| 03-02.3 | `docs/decisions/README.md` has exactly one 0008 row and `Next number: **0009**`; `test_adrs` passes | ✓ VERIFIED | Row at line 31, footer at line 33; 190-test suite OK. |
| 03-02.4 | ADR-0002 is byte-identical to its committed state | ✓ VERIFIED | `git hash-object` = `git rev-parse HEAD:...` = `55a4c226…`. |
| 03-02.5 | `AGENTS.md` step 3 documents `pio test -d tests -e native`, step 2 documents `pio run -d <project>`, file ≤300 lines | ✓ VERIFIED | Lines 24–25; 200 lines. |
| 03-03.1 | `lib/port` declares all five contracts; each header has `#pragma once`, `extern "C"`, only C standard headers + own prefix | ✓ VERIFIED | Headers read; `test_architecture_headers` passes over 21 headers. |
| 03-03.2 | Every contract carries `void *ctx` and no other state | ✓ VERIFIED | All five structs carry only function pointers plus `ctx`. |
| 03-03.3 | I2C/SPI expose bus-level operations only; no driver state, register map, page/display concept or native-handle escape hatch | ✓ VERIFIED | `port/i2c.h`, `port/spi.h` read. |
| 03-03.4 | Every failable operation returns `port_status_t`; time read and log write are documented exceptions | ✓ VERIFIED | Headers read; `log.h` documents the `void` return. |
| 03-03.5 | The suite exercises all five contracts and proves `ctx` reaches the callback unchanged | ✓ VERIFIED | `test_port_contracts`: 433 lines, `test_time_ctx_reaches_callback` present and passing. |
| 03-03.6 | GPIO uses `uint8_t` pin, mode and level enums, no framework type; rationale and ESP-IDF `<64` guard documented | ✓ VERIFIED | `port/gpio.h` prose; `lib/espidf/src/gpio.c` rejects `pin >= 64` before the shift. |
| 03-03.7 | Pull-down and floating input are documented as absent limitations | ✓ VERIFIED | `port/gpio.h` comment. |
| 03-04.1 | `lib/common` ships exactly `ring_buffer`, `timing`, `crc`, `hex`; no other module | ✓ VERIFIED | Exact inventory asserted by `test_pio_scripts.py:53-60,273`. |
| 03-04.2 | Every `common` module is allocation-free and caller-owned | ✓ VERIFIED | Sources read; no allocator calls; caller-supplied storage and buffers. |
| 03-04.3 | No `common` module blocks, sleeps, yields or reads a clock; includes only C standard and own headers | ✓ VERIFIED | Checker prints `PASS blocking: no blocking token in lib/common`; include scan passes. |
| 03-04.4 | CRC-16/CCITT-FALSE; `common_crc16("123456789") == 0x29B1`; disclaimer present | ✓ VERIFIED | `test_crc16_check_value` passes; `crc.h` states integrity, not authentication. |
| 03-04.5 | Hex encode/decode round-trip all byte values, reject odd length/non-hex, report insufficient capacity | ✓ VERIFIED | `test_common_hex`: 160 lines, passing. |
| 03-04.6 | Hex failure contract: on failure `*out_length = 0` and no output byte written | ✓ VERIFIED | Source read; `test_hex_insufficient_capacity_writes_nothing` passes. |
| 03-04.7 | Ring buffer reports full/empty through return values, wraps without allocating, zero-init safe | ✓ VERIFIED | Source read; `test_ring_buffer_zero_initialised_is_safe` and wrap tests pass. |
| 03-04.8 | Ring-buffer header records single-threaded, non-ISR-safe semantics | ✓ VERIFIED | `ring_buffer.h:28-30`. |
| 03-05.1 | `lib/host` provides deterministic fakes for all five contracts | ✓ VERIFIED | Five header/source pairs exist and compile. |
| 03-05.2 | Each fake returns the exact `port_<contract>_t` and is built positionally, so drift is a compile error | ✓ VERIFIED | Factories return the contract structs by value; `test_all_fakes_expose_the_real_contract_types` passes. |
| 03-05.3 | Every fake is allocation-free/caller-owned with bounded storage (64 pins, 32-byte I2C/SPI, 32×64 log) | ✓ VERIFIED | Header constants read; bounds tests pass. |
| 03-05.4 | Fail-capable fakes expose a one-shot `fail_next`; the scripted status is returned once and cleared | ✓ VERIFIED | `fake_gpio`, `fake_i2c`, `fake_spi` implement it; time read and log write cannot fail by contract, so they have no `fail_next` (documented exceptions in 03-03.4). |
| 03-05.5 | GPIO `configured` flag means "configured or written through this fake"; `set_mode` and `write` set it, `read` does not | ✓ VERIFIED | Source read; header documents it. |
| 03-05.6 | I2C fake is documented as a single-device loopback, not a multi-device simulator | ✓ VERIFIED | `fake_i2c.h:12-17`. |
| 03-05.7 | `lib/host` includes only `port` and C standard headers; no framework header and no production logic | ✓ VERIFIED | Include scan passes; sources read. |
| 03-05.8 | `pio test` is the only exercise path; no firmware environment lists `host` | ✓ VERIFIED | Checker config rule passes; `test_host_symlink_appears_only_under_env_native` passes. |
| 03-06.1 | Arduino and ESP-IDF implement exactly time, GPIO and logging; no I2C/SPI adapter (recorded D-08 deferral) | ✓ VERIFIED | File inventory: three sources per adapter, no bus adapters. |
| 03-06.2 | Every adapter public header declares only `port_*` types and one factory; no framework type | ✓ VERIFIED | Headers read; header suite passes. |
| 03-06.3 | Every adapter source includes the framework header first, a blank line, then its own header | ✓ VERIFIED | Six sources read; shape matches. |
| 03-06.4 | The Arduino log adapter calls `log_printf` unconditionally | ✓ VERIFIED | `lib/arduino/src/log.c`. |
| 03-06.5 | ESP-IDF GPIO zero-inits `gpio_config_t`, sets pull-up/down explicitly, rejects `pin >= 64` before the shift, maps errors through `map_esp_err`, leaks no `esp_err_t` | ✓ VERIFIED | `lib/espidf/src/gpio.c` read. |
| 03-06.6 | Both target `compiledb` runs succeed and list the adapter sources | ⇢ DEFERRED | Cannot be re-executed: the smoke project was retired by plan 03-07 by design. Owner: Phase 4 SC2 and Phase 8 SC2. |
| 03-06.7 | Target-compile evidence is temporary; no permanent test, script or config reads the smoke project | ✓ VERIFIED | `grep` across `scripts/`, `tests/`, `lib/`, `platformio.shared.ini` and `.pre-commit-config.yaml` finds no reference. |
| 03-06.8 | The lost post-Phase-3 target-compile gate is recorded as a known risk with named owners | ✓ VERIFIED | `03-06-PLAN.md:313,333`; `03-06-SUMMARY.md:247`. |
| 03-07.1 | Both ESP sections point at `../../partitions/default_16MB.csv`; the file exists; a test resolves it from homework depth | ✓ VERIFIED | `platformio.shared.ini`; `scripts/tests/test_pio_scripts.py` passes. |
| 03-07.2 | The smoke project is gone from tree and index; `git ls-files homeworks` is empty; the removal is a dedicated `chore(03)` commit | ✓ VERIFIED | `git ls-files homeworks` empty; commit `5cb1571` deletes exactly the four smoke files. |
| 03-07.3 | `test_pio_scripts.py` no longer reads the smoke project, uses `tests/platformio.ini`, asserts the `pre:../` hook, exact inventory and `.c` suffix | ✓ VERIFIED | File read; suite passes. |
| 03-07.4 | `test_gitignore.py` uses neutral `homeworks/1_1-example/...` fixtures | ✓ VERIFIED | Lines 86–184. |
| 03-07.5 | Five manifests at `0.2.0`, all with `includeDir`, four with `srcDir`, `port` without | ✓ VERIFIED | Manifests read; `test_pio_scripts` asserts version. |
| 03-07.6 | The ten Phase 2 stub files are gone; remaining headers are the module headers from 03-01/03-03/03-05 | ✓ VERIFIED | `find lib` shows only module headers; header inventory asserts 21. |
| 03-07.7 | The strict source inventory is present on the final tree without contradicting it | ✓ VERIFIED | `test_library_sources_match_the_inventory_exactly` passes. |
| 03-07.8 | Full Python suite and native suite both pass on the final tree | ✓ VERIFIED | 190 Python tests OK; 73/73 native cases. |
| 03-08.1 | Checker exits 0 on the real tree with `PASS: dependency rule satisfied`; a forbidden include exits 1 naming file, line and rule | ✓ VERIFIED | Real run and independent fixture (see spot-checks). |
| 03-08.2 | Any `..` segment, absolute name, drive letter or UNC prefix is an escape | ✓ VERIFIED | Dedicated tests for embedded/leading `..`, absolute and Windows paths pass. |
| 03-08.3 | Edge matrix is module-level data; own-module headers allowed | ✓ VERIFIED | `EDGES` table at `check_architecture.py:80`; fixture matrix passes. |
| 03-08.4 | Per-owner external allowlist is tight; `stdio.h`/`stdlib.h`/`limits.h` absent for pure layers | ✓ VERIFIED | `EXTERNAL_OK` at `check_architecture.py:99`; `<stdlib.h>` fixture fails. |
| 03-08.5 | Blocking-token denylist applies to `lib/common/**` only | ✓ VERIFIED | `BLOCKING` tuple; real run prints the blocking PASS. |
| 03-08.6 | Comment stripper is stateful over `//`, `/* */`, strings and character literals | ✓ VERIFIED | `test_strip_comments_keeps_strings_and_drops_real_comments` passes. |
| 03-08.7 | Config parsing uses `ConfigParser(interpolation=None)`; closure, at-most-one-adapter and host-native rules enforced | ✓ VERIFIED | Source read; config fixture tests pass. |
| 03-08.8 | Allowlist is `{"version": 1, "entries": []}`; stale entry fails 1; malformed/empty reason fails 2 | ✓ VERIFIED | File read; allowlist fixture tests pass. |
| 03-08.9 | Missing `lib/` is exit 2; the checker never writes; two runs are identical | ✓ VERIFIED | Independent run: exit 2 on an empty root; `test_second_run_is_identical_and_read_only` passes. |
| 03-08.10 | `test_check_architecture` proves at least sixteen negative fixtures, including embedded `..`, absolute include, `<stdlib.h>`, `//` in a string, multi-line `lib_deps` and empty allowlist reason | ✓ VERIFIED | 41 tests pass in this module; named cases present. |
| 03-08.11 | `test_architecture_headers` proves the contract over the 21 final headers | ✓ VERIFIED | 7 tests pass; count asserted as 21 and discovered set matches. |
| 03-08.12 | `pre-commit run check-architecture --all-files` exits 0 and its `files` pattern covers the checker and `scripts/architecture/` | ✓ VERIFIED | Hook run: `Passed`; pattern read at `.pre-commit-config.yaml:59`. |
| 03-09.1 | `compiledb` database names only a host compiler and no target toolchain or framework include | ✓ VERIFIED | 11 entries, all `/usr/bin/gcc`; forbidden-token scan clean. |
| 03-09.2 | The database contains the nine shared sources and `tests/src/main.c` | ✓ VERIFIED | All ten present (main resolves to `tests/src/main.c`). |
| 03-09.3 | A framework include in a copied `common/timing.c` makes the native build fail | ✓ VERIFIED | `test_framework_include_fails_the_build` passes. |
| 03-09.4 | A relative cross-library include is measured to compile, recording the limit that only the checker rejects it | ✓ VERIFIED | `test_relative_cross_library_include_compiles` passes. |
| 03-09.5 | Every fixture path is asserted to stay inside the temporary root | ✓ VERIFIED | Containment assertions at `test_native_purity.py:164-170,322-328`. |
| 03-09.6 | The determinism test runs 20 times and compares a normalized per-line digest | ✓ VERIFIED | `RUNS = 20`; test executes 20 runs and passes. |
| 03-09.7 | The digest drops paths, line numbers, messages and durations | ✓ VERIFIED | Offline digest unit tests pass. |
| 03-09.8 | The digest contains one row for each of the seven suites | ✓ VERIFIED | `REQUIRED_SUITES` asserted; determinism test passes. |
| 03-09.9 | An offline digest unit test pins the exact normalization | ✓ VERIFIED | `test_digest_pins_the_exact_normalization` passes. |
| 03-09.10 | Both modules fail rather than skip when `pio` is absent; every subprocess has a timeout | ✓ VERIFIED | `_require_pio()` and `TIMEOUT_SECONDS` read; timeout passed to every `subprocess.run`. |
| 03-09.11 | `RUNS = 20` is a constant with no environment override | ✓ VERIFIED | `test_native_determinism.py:27`. |

**Score:** 75/76 truths verified (1 deferred to Phase 4/Phase 8; 0 present-but-behavior-unverified).

### Deferred Items

| # | Item | Addressed In | Evidence |
|---|------|--------------|----------|
| 1 | Target compile of the Arduino and ESP-IDF adapters (03-06.6) | Phase 4 and Phase 8 | Phase 4 SC2 "builds immediately"; Phase 8 SC2 "CI builds and unit-tests changed projects". The smoke project was retired by design in 03-07. |

### Required Artifacts

`gsd-tools query verify.artifacts` reports 63/64 artifact checks passed; the single reported miss is a stale `contains` expectation, not a stub. All 64 artifacts exist, are substantive, and are wired.

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `tests/platformio.ini`, `tests/src/main.c` | Host-only project and compiledb probe | ✓ VERIFIED | Both read; project builds and tests run. |
| 6 `lib/port/include/port/*.h`, 4 `lib/common/include`, `lib/common/src/*.c` | Contracts and pure primitives | ✓ VERIFIED | Read; compiled into the native database; behavior tested. |
| 5 `lib/host/include`, 5 `lib/host/src` | Deterministic doubles | ✓ VERIFIED | Read; cross-fake suite passes. |
| 6 adapter headers/sources | Thin adapters | ✓ VERIFIED | Read; present and include-clean; target compile deferred (see above). |
| `docs/decisions/0008-*.md`, `README.md`, `AGENTS.md` | ADR and runnable commands | ✓ VERIFIED | Read; `test_adrs` and `test_agents_md` pass. |
| `partitions/default_16MB.csv`, `platformio.shared.ini`, 5 `library.json` | Partition and manifest contract | ✓ VERIFIED | Read; `test_pio_scripts` passes. |
| `scripts/check_architecture.py`, `scripts/architecture/allowlist.json` | Dependency checker | ✓ VERIFIED | Runs green on the real tree; 41 fixture tests pass. |
| `scripts/tests/test_check_architecture.py`, `test_architecture_headers.py`, `test_native_purity.py`, `test_native_determinism.py`, `test_pio_scripts.py`, `test_gitignore.py` | Enforcement suites | ✓ VERIFIED | All execute and pass. |
| `lib/common/src/crc.c` | `contains: "0x29B1"` | WARNING: PATTERN MISMATCH (not a stub) | The file implements the polynomial (`0x1021`); the check value `0x29B1` is asserted at `tests/test/test_common_crc/test_crc.c:17`. The plan's `contains` field is misplaced, not the implementation. |

### Key Link Verification

`gsd-tools query verify.key-links` reports 29/30 verified. The one reported miss is a literal-pattern mismatch in the plan, not a broken link.

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `tests/platformio.ini` | `platformio.shared.ini` | `extra_configs` | WIRED | Literal present. |
| `tests/platformio.ini` | 3 library manifests + Unity | `lib_deps = symlink://` | WIRED | `common`, `port`, `host`, `Unity@2.6.1`. |
| `common/timing.h` | `port/time.h` | `const port_time_t *` | WIRED | Header read. |
| `test_timing.c` | `host/fake_time.h` | fake clock wired into debounce | WIRED | Test passes. |
| `port/gpio.h` | `port/status.h` | `port_status_t` returns | WIRED | Header read. |
| `test_port_contracts.c` | all five contracts | local vtables called through the API | WIRED | 433-line suite passes. |
| `test_architecture_headers.py` | `lib/port/include/port/status.h` | 21-header inventory | WIRED | Tool pattern `lib/port/include` is not a literal; the test builds `REPO_ROOT / "lib" / "port" / "include"`. The inventory test passes. |
| `.pre-commit-config.yaml` | `scripts/check_architecture.py` | local hook entry | WIRED | Hook passed. |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|---|---|---|---|---|
| `common/timing.c` | `now_ms`, `stable`, `candidate_since_ms` | caller-supplied `port_time_t`; tests inject `host_fake_time_port` | Yes | ✓ FLOWING |
| `port_gpio_t` vtable | pin mode/level | `host_fake_*` in tests; Arduino/ESP-IDF adapters on target | Yes (host path executed) | ✓ FLOWING |
| `port_i2c_t` / `port_spi_t` vtables | buffers, addresses, lengths | `host_fake_i2c`/`host_fake_spi` loopback | Yes | ✓ FLOWING |
| `port_log_t` vtable | level, message | `host_fake_log` capture | Yes | ✓ FLOWING |
| Adapter sources | framework calls | Arduino / ESP-IDF toolchain | Not runnable on host | ⇢ DEFERRED |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| Native Unity suite passes | `pio test -d tests -e native` | 73/73 succeeded, 7 suites, exit 0 | ✓ PASS |
| Full Python suite passes | `python3 -m unittest discover -s scripts/tests -v` | 190 tests OK (61.6 s) | ✓ PASS |
| Dependency checker passes the real tree | `python3 scripts/check_architecture.py` | `PASS: dependency rule satisfied`, exit 0 | ✓ PASS |
| Checker rejects a forbidden include | independent temp fixture (`<Arduino.h>` in `lib/common/src/timing.c`) | exit 1, names file/line/rule | ✓ PASS |
| CR-01 regression: alias does not mask the linked adapter | independent temp fixture (`port=symlink://.../lib/arduino`) | exit 1, "must also list 'port' (it lists arduino, common)" | ✓ PASS |
| Checker is fail-closed on a missing `lib/` | `python3 scripts/check_architecture.py --dir <empty>` | exit 2 | ✓ PASS |
| Local hook runs the checker | `pre-commit run check-architecture --all-files` | Passed | ✓ PASS |
| 20-run determinism | `python3 -m unittest scripts.tests.test_native_determinism -v` | 5 tests OK (52.7 s); 20 identical digests | ✓ PASS |
| Native purity and fixtures | `python3 -m unittest scripts.tests.test_native_purity -v` | 7 tests OK | ✓ PASS |

### Probe Execution

No `probe-*.sh` scripts are declared or present (`find scripts -path '*/tests/probe-*.sh'` returns none). The phase's runnable gates are the Python `unittest` modules and the Unity suite, all executed above.

| Probe | Command | Result | Status |
|---|---|---|---|
| — | — | No probe scripts in this phase | N/A |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|---|---|---|---|---|
| ARCH-01 | 03-01, 03-02, 03-03, 03-05, 03-08 | `lib/port` function-pointer contracts for time, GPIO, I2C, SPI, logging; no framework headers, no state | ✓ SATISFIED | Six headers; 21-header suite; callable vtable tests; no globals. |
| ARCH-02 | 03-01, 03-04, 03-08, 03-09 | `lib/common` pure domain logic; never blocks or sleeps | ✓ SATISFIED | Four modules; blocking denylist PASS; allocation-free sources; deterministic suite. |
| ARCH-03 | 03-01, 03-05, 03-06, 03-08 | Thin adapters and deterministic test doubles; no business logic | ✓ SATISFIED | Five host fakes; six adapter files; include matrix PASS; target compile deferred to Phase 4/8. |
| ARCH-05 | 03-02, 03-08, 03-09 | `check_architecture.py` and a native compile gate enforce the dependency rule | ✓ SATISFIED | Checker green on the real tree and red on forbidden fixtures; framework-include fixture fails the native build; relative cross-library limit measured and documented. |
| ARCH-06 | 03-01, 03-07, 03-09 | Top-level `tests/` project compiles `common` and `port` natively and runs the Unity suite | ✓ SATISFIED | `compiledb`: host-only, nine shared sources; 73/73 cases; 20 identical runs. |
| ARCH-07 | 03-03, 03-08 | No universal HAL; reusable drivers abstract the bus, not the whole driver | ✓ SATISFIED | Bus-level I2C/SPI contracts; no register map/device concept; header suite passes. |

**Orphaned requirements:** none. `ROADMAP.md` lists exactly ARCH-01, ARCH-02, ARCH-03, ARCH-05, ARCH-06, ARCH-07 for Phase 3, and every ID is claimed by at least one plan. ARCH-04 is the Phase 2 requirement and is marked complete there.

### Anti-Patterns Found

No `TBD`, `FIXME`, `XXX`, `PLACEHOLDER`, TODO/HACK, empty implementation or hardcoded stub data was found in any phase-modified file. The debt-marker gate is clean.

| File | Line | Pattern | Severity | Impact |
|---|---|---|---|---|
| `lib/common/src/crc.c` | — | Plan artifact expects literal `0x29B1`; file implements polynomial `0x1021`, check value asserted in the test | Info: Info | None on behavior; stale plan metadata only. |

Known open code-review findings (not must-have failures, recorded in `03-REVIEW.md` / `03-REVIEW-DISPOSITION.md`): 11 warnings and 7 info findings remain open (WR-02, WR-04–WR-10, IN-01–IN-07). The review's only blocker, CR-01, plus WR-01 and WR-03, were fixed in commit `6282788`; the fix and its four regression tests were re-executed here and pass.

### Human Verification Required

The automated gates are green. The items below are judgement-tier must-NOT statements and two test-tier items without a permanent regression test; they are not code failures.

#### 1. ADR-0008 supersession scope

**Test:** Read `docs/decisions/0008-common-depends-on-port.md` against ADR-0002.
**Expected:** Only the dependency-rule sentence is superseded; ADR-0002 stays accepted and unedited (its blob hash already matches `HEAD`).
**Why human:** The extent of a prose supersession is a reading judgement.

#### 2. Bus-abstraction shape (ARCH-07)

**Test:** Read `lib/port/include/port/i2c.h` and `spi.h`.
**Expected:** Bus-level transactions only; no register map, page, display, device init or native-handle escape hatch.
**Why human:** API shape is a design reading, not a machine-checkable include.

#### 3. Pure-layer prose claims

**Test:** Read the CRC and ring-buffer header prose.
**Expected:** CRC is integrity, not authentication or trust; the ring buffer is neither ISR-safe nor lock-free.
**Why human:** Automation proves the words exist, not that the claims are adequate.

#### 4. `lib/host` is policy-free

**Test:** Read `lib/host/src/*.c`.
**Expected:** Recording, loopback, bounds checks and one-shot failure only; no policy, schedule or state machine.
**Why human:** No mechanical rule separates a recording stub from a small policy.

#### 5. Adapter thinness

**Test:** Read `lib/arduino/src/*.c` and `lib/espidf/src/*.c`.
**Expected:** Each callback is one framework call plus enum mapping; no business logic, no blocking.
**Why human:** Adapter thinness is a design reading.

#### 6. Deferral adequacy

**Test:** Confirm the D-08 deferral of I2C/SPI adapters and the post-Phase-3 target-compile gap owned by Phase 4/Phase 8 are acceptable for this milestone.
**Expected:** The deferral and its named owners cover the gap.
**Why human:** Scope adequacy is a judgement.

#### 7. Test-tier prohibitions without a permanent test

**Test:** Decide whether to accept one-off evidence or add permanent tests for ADR-0002 immutability and for the ESP-IDF `pin >= 64` guard before the `1ULL << pin` shift.
**Expected:** Either accept, or add the two regression tests.
**Why human:** Both properties are verified now (blob hash equal; guard present before the shift) but neither has a committed test.

#### 8. Allowlist policy

**Test:** Confirm the empty allowlist and the non-empty-reason/stale-entry rules are the intended permanent policy.
**Expected:** No entries now; future entries must justify themselves.
**Why human:** The schema is testable; the legitimacy of a future reason is a reviewer judgement.

### Gaps Summary

No blocking gap was found. The phase goal is achieved in the codebase: a 21-header framework-free C core (`port`, `common`, `host`, `arduino`, `espidf`), a deterministic native suite (73 cases, 7 suites, 20 identical runs), and a dependency checker wired into pre-commit that is green on the real tree and red on forbidden fixtures. The CR-01 blocker and WR-01/WR-03 warnings from the code review were independently re-verified as fixed in commit `6282788`, including the four added regression tests. The ten Phase 2 stubs and `homeworks/0_0-toolchain-smoke/` are absent as designed; the only truth no longer executable is the target compile, which is deferred to Phase 4 SC2 and Phase 8 SC2 by the plan's own recorded known risk. Status is `human_needed` because eight prose/design judgements remain, not because any automated gate is red.

---

_Verified: 2026-10-23T22:59:35Z_
_Verifier: Claude (gsd-verifier)_

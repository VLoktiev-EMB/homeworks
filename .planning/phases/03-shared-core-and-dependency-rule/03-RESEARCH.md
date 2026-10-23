# Phase 3: Shared Core and Dependency Rule - Research

**Researched:** 2026-10-24
**Domain:** Framework-free C11 ports-and-adapters core, PlatformIO native Unity testing, textual architecture enforcement
**Confidence:** HIGH for PlatformIO/Unity mechanics and the checker design (verified by execution on this machine); MEDIUM for the exact contract signatures and the future Arduino I2C/SPI adapter path (design judgement, no consumer yet)

> Knowledge-graph note: `.planning/graphs/graph.json` is 1 h old and 2 commits behind
> (`628e0e1` vs `b2e0145`); the two commits are documentation-only. Graph relationships
> were treated as approximate.

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

#### Dependency direction

- **D-01:** The dependency edge is **`common → port`**. `lib/port` depends on nothing (no
  project headers, no framework headers); `lib/common` may include `port` headers and call
  injected port functions; adapters include `port` only; `port → common`, `port → adapter`,
  `adapter → common`, and any framework include in `common`/`port` are forbidden. This
  resolves the contradiction between ADR-0002 ("`common` depends on nothing; `port`
  depends on `common`") and ARCH-05/research ("`common → port`") in favour of the
  requirement text and the research component table.
  — **Reversibility:** costly — every shared source, adapter, and future homework's include
  graph plus the checker encode the direction; flipping it later is a repository-wide
  refactor.
- **D-02:** Record the direction in a new **`docs/decisions/0008-*.md`** that supersedes
  only the dependency-rule sentence of ADR-0002. ADR-0002 stays accepted and untouched as
  history; `docs/decisions/README.md` gains the 0008 row in the same change.
  — **Reversibility:** costly — ADR numbers are sequential and permanent, and published
  cross-references depend on them (Phase 1 D-27).
- **D-03:** Do **not** add a `dependencies` field to any `library.json`. With `symlink://`,
  PlatformIO resolves manifest dependencies against the package registry, which would try
  to fetch unrelated packages named `common`, `port`, and so on. Every project lists its
  full `lib_deps` explicitly; Phase 5 generates that list. This deliberately supersedes
  the advice on `.planning/research/STACK.md:248`.
- **D-04:** All five libraries move from `0.1.0` to **`0.2.0`**, because each gains real
  public API beyond the Phase 2 linking stub. The duplicated version-string returns in the
  `.c` sources are removed, so the version lives only in `library.json` (fixes Phase 2
  review WR-03).

#### Port contracts

- **D-05:** `lib/port` defines **all five contracts** required by ARCH-01: `time`, `gpio`,
  `i2c`, `spi`, and `log`. I2C and SPI expose narrow **bus-level** operations (transfer,
  read, write), never a whole-driver interface (ARCH-07).
- **D-06:** Every contract carries a `void *ctx` opaque pointer. "Port contains no state"
  is read as "port owns no global mutable state and mutates nothing"; the state behind
  `ctx` belongs to the adapter. This interpretation is recorded in ADR-0008. It allows
  multiple instances (two buses, two timers) and clean test isolation.
- **D-07:** `lib/host` provides deterministic fakes for **all five** contracts.
- **D-08:** `lib/arduino` and `lib/espidf` implement `time`, `log`, and `gpio` in this
  phase. I2C and SPI framework adapters are deferred to the first homework that needs
  them; the contracts exist, the implementations do not.
- **D-09:** Contracts report failure through `enum port_status_t` with at least
  `PORT_OK`, `PORT_ERR_TIMEOUT`, `PORT_ERR_IO`, `PORT_ERR_INVALID_ARG`,
  `PORT_ERR_NOT_SUPPORTED`. Logging uses four levels: `ERROR`, `WARN`, `INFO`, `DEBUG`.
  No POSIX `errno` mixing.
- **D-10:** Adapters stay thin: they translate a call and return a status; they contain no
  business logic and leak no framework types through their public headers.

#### Common logic

- **D-11:** Ship only the **proven minimum**: `ring_buffer`, `timing`, and `crc`/`hex`.
  `timing` includes a small `port_time_t`-based debounce/elapsed helper so the suite
  genuinely exercises fake time from `lib/host` (success criterion 4). `fixed_point`, a
  generic state machine, and a calculations module are deferred until real duplication
  appears (Pitfall C15).
- **D-12:** Homework-specific logic never moves into `lib/common`. The police-flasher
  logic lives in `homeworks/1_3-police-flasher/src/` in Phase 11; reuse is promoted to
  `common` only after the same code appears in a second or third homework ("copy twice,
  extract on the third use").

#### Tests, enforcement, and packaging

- **D-13:** The top-level `tests/` is a real PlatformIO project with `[env:native]`,
  `test_framework = unity`, and an explicit `lib_deps` of `common`, `port`, and `host`
  (symlinked). It must build and run without a target toolchain.
- **D-14:** Determinism is proven by `scripts/tests/test_native_determinism.py`, which
  invokes `pio test -e native` 20 times and compares a normalized summary of
  `test_name: PASS/FAIL` plus counts. Raw stdout is never compared, because it carries
  timings and paths. The test joins the repository gate
  `python3 -m unittest discover -s scripts/tests -v`.
- **D-15:** `scripts/check_architecture.py` performs a **textual `#include` scan** of
  `lib/**` and `homeworks/**`, enforcing the layer rules and the "exactly one adapter per
  homework" rule, with an empty-by-default allowlist mechanism. `tests/**` is not scanned.
  Transitive purity of `common`/`port` is proven by the native compile gate, not by the
  scanner.
- **D-16:** `check_architecture.py` runs as a **local pre-commit hook** in this phase. The
  20-run native suite stays in the Python test suite and manual runs; pre-push is Phase 6
  and CI is Phase 8.
- **D-17:** `lib/host` remains a library with `library.json`, linked only from `tests/`
  and `[env:native]`. The checker rejects `host` in `lib_deps` of any ESP/Arduino
  environment, so fakes cannot reach firmware.

#### Phase 2 carry-forward

- **D-18:** `default_16MB.csv` moves to **`partitions/default_16MB.csv`**;
  `platformio.shared.ini` points to `../../partitions/default_16MB.csv`; a test asserts
  that the path referenced by the shared configuration exists. This must land before the
  smoke project is deleted (Phase 2 review CR-01).
  — **Reversibility:** costly — every ESP32 project resolves this path relative to its own
  directory; moving it later breaks every existing build.
- **D-19:** `homeworks/0_0-toolchain-smoke/` is deleted in a dedicated commit, as an
  explicit task in this phase's plan (Phase 2 D-07).
- **D-20:** `scripts/tests/test_pio_scripts.py` is refactored off the smoke project onto
  permanent fixtures so that deleting the directory cannot produce `FileNotFoundError`
  (Phase 2 review WR-01). Project-specific assertions are either retargeted to `tests/` or
  removed with the project.
- **D-21:** C formatting is **deferred to Phase 6**. Write consistent code now; do not add
  clang-format or perform a mass reformat in this phase.

### Claude's Discretion

- Exact signatures, field names, and header layout of the five contracts, within the
  decisions above.
- Whether `lib/port` is header-only or ships a small `.c` for inline helpers.
- Internal `tests/` layout: test file names, whether one `[env:native]` is enough, and
  whether it extends `native_unity` or defines its own environment locally. Keeping
  `test_framework = unity` local to `tests/` is acceptable and avoids imposing Unity on
  future native homework environments.
- The normalized summary format used for the 20-run comparison.
- The internal implementation shape of `check_architecture.py` and the allowlist file
  format.

### Deferred Ideas (OUT OF SCOPE)

- I2C and SPI framework adapters in `lib/arduino` and `lib/espidf` — the first homework
  that needs them.
- `fixed_point`, a generic state machine, and a calculations module in `lib/common` —
  after real duplication (Pitfall C15).
- `check_architecture.py` and the native suite in CI — Phase 8.
- Generated `platformio.shared.ini` and its `--check` drift gate — Phase 5.
- Pre-push hooks — Phase 6.
- clang-format configuration and the mass reformat — Phase 6.
- A nested `lib/AGENTS.md` — only if the dependency rule genuinely diverges from the root
  rulebook (Phase 1 D-05).
- Homework-domain logic such as the police-flasher state machine — Phase 11, inside the
  homework.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| ARCH-01 | `lib/port` defines C function-pointer contracts for time, GPIO, I2C, SPI, and logging; no framework headers, no state | Concrete header set and signatures (§Pattern 1, §Code Examples); header-only library verified to provide its include path without a `src/`; `extern "C"` shape compiled under `-std=c11 -pedantic` and `-std=c++17 -pedantic` |
| ARCH-02 | `lib/common` contains pure C domain logic (ring buffers, timing, codecs) and never blocks or sleeps | `ring_buffer`/`timing`/`crc`/`hex` API surface (§Pattern 3); wraparound-safe elapsed/debounce arithmetic; a token denylist in the checker turns "never blocks" into a mechanical check |
| ARCH-03 | `lib/arduino`, `lib/espidf`, `lib/host` are thin adapters and deterministic doubles; no business logic | Verified that both framework adapters stay pure C for time/GPIO/log on the pinned toolchains; fakes implement the same vtable types, so signature drift is a compile error (Pitfall C12) |
| ARCH-05 | `scripts/check_architecture.py` and a native compile gate enforce the dependency rule | Verified that `common → adapter` **compiles and links** through a relative include, so the compile gate alone is insufficient; checker matrix, allowlist format, exit-code contract, and negative fixtures specified (§Pattern 4) |
| ARCH-06 | A top-level `tests/` PlatformIO project compiles `common`/`port` natively and runs the shared Unity suite without a target toolchain | Exact `tests/platformio.ini` executed end to end; `compiledb` output proves host-only compilers and no framework include paths; 20-run normalized digest approach validated |
| ARCH-07 | No universal HAL; reusable drivers abstract the bus, not the driver | Bus-level I2C/SPI contract shapes (no whole-driver interface, no `port_get_native_handle`); review rule recorded for the checker's limits |
</phase_requirements>

---

## Summary

Phase 3 is a design phase whose three riskiest assumptions are all mechanically testable, and all three were executed on this machine before writing this document. First, the native Unity project works exactly as the research documents claim: a `tests/` PlatformIO project with `extra_configs = ../platformio.shared.ini`, `extends = native_unity`, `test_framework = unity`, and `lib_deps` symlinking `common`, `port`, and `host` compiles and passes. Second, the compile gate really does reject a framework include in `common` (`fatal error: 'Arduino.h' file not found`), but it does **not** reject `common → adapter`, because a relative include across library directories compiles and links — so the textual checker is load-bearing, not decorative. Third, both framework adapters can remain pure C for the three contracts this phase implements (`millis`/`pinMode`/`digitalWrite`/`digitalRead`/`log_printf` under Arduino; `esp_timer_get_time`/`gpio_config`/`gpio_set_level`/`gpio_get_level`/`ESP_LOGI` under ESP-IDF), which preserves the Phase 2 D-15 rule that library sources stay `.c`.

Four findings change how the plan should be written. (1) `extra_scripts` paths resolve relative to the **project** directory, so `tests/` cannot inherit `pre:../../scripts/pio/compiledb.py` from `platformio.shared.ini` — it resolves two levels above the repository; `tests/` must override it with `pre:../scripts/pio/compiledb.py`. (2) Because D-03 forbids manifest `dependencies`, every consumer must list `port` explicitly; a project that lists `common` without `port` fails with `'port/time.h' file not found`. (3) PlatformIO writes Unity's per-test rows to stdout but the summary and durations to stderr, and Unity's failure rows carry an assertion message before the tab; the 20-run normalizer must iterate per-test lines (anchored per line, not with `re.MULTILINE` over the whole buffer) and must not use PlatformIO's summary counts. (4) `#include "../arduino/include/..."` compiles natively, proving the include scanner must reject path escapes explicitly.

**Primary recommendation:** build `port` as a header-only set of five consumer-owned vtables in `include/port/<name>.h`; implement `common` as four pure-C modules that take a `const port_time_t *` only where time is genuinely needed; implement `host` fakes as bounded, allocation-free structs; drive everything from one `tests/` project that overrides `extra_scripts` and pins Unity; and ship `scripts/check_architecture.py` with a deny-by-default, empty-allowlist policy plus a `pio run -t compiledb` purity assertion.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Capability contracts (time, GPIO, I2C, SPI, log) | Shared core — `lib/port` headers | — | Interfaces belong to the consumer (DIP in C); header-only so `common` links against no port object |
| Pure domain logic (ring buffer, timing, CRC, hex) | Shared core — `lib/common` | — | No framework, no allocation, no blocking; testable on the host |
| Framework translation (Arduino / ESP-IDF) | Edge adapters — `lib/arduino`, `lib/espidf` | — | Translate a call and return a status; framework types never cross the public header |
| Deterministic test doubles | Test infrastructure — `lib/host` | `tests/` | Fake time, recording GPIO, loopback buses, captured log; linked only by native builds |
| Test orchestration | `tests/` PlatformIO project | PlatformIO `test_framework = unity` | One project above all libraries; each `test/` subfolder is an independent Unity app |
| Dependency enforcement | Repository tooling — `scripts/check_architecture.py` | `.pre-commit-config.yaml` | Textual scan of `lib/**` and `homeworks/**`; the native compile gate covers transitive purity |
| Compile-time purity proof | `tests/` native build (`pio run -e native -t compiledb`) | `scripts/tests/test_native_purity.py` | Only a host compiler appears in the database; no framework/toolchain include path |
| Build configuration | `platformio.shared.ini` + `tests/platformio.ini` | — | Shared sections are hand-authored in this phase; generators arrive in Phase 5 |
| Permanent partition table | Repository data — `partitions/default_16MB.csv` | `platformio.shared.ini` | Both ESP environments resolve it relative to the project directory |
| Dependency-direction record | `docs/decisions/0008-*.md` | `docs/decisions/README.md` | Supersedes only the dependency-rule sentence of ADR-0002 |

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| C11 (`-std=c11`) | ISO/IEC 9899:2011 | Language for `port`, `common`, `host`, and adapter sources | Already the pinned native flag in `platformio.shared.ini`; `_Static_assert`, `stdbool`, fixed-width integers |
| PlatformIO Core | 6.2.0 | Build system, LDF, test runner | Pinned by FOUND-09; `pio --version` reports 6.2.0 on this machine |
| Unity | 2.6.1 | C test framework for the shared suite | Installed by `test_framework = unity`; official PlatformIO-supported framework |
| Python | 3.13.13 (PlatformIO venv) | Checker, tests, determinism driver | Repository scripts are stdlib-only; `unittest` discovery is the existing gate |
| pre-commit | 4.7.0 | Local hook runner | Already pinned in `.pre-commit-config.yaml`; hosts the new architecture hook |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| PlatformIO `native` platform | bundled with Core 6.2.0 | Host compiler, no toolchain download | Every `pio run/test -e native` |
| Apple clang (host) | 21.0.0 | Host C11 compiler on this machine | Local runs; Linux CI uses GCC (Phase 8) |
| `platformio/espressif32` | 8.0.0 | Arduino/ESP-IDF adapter compilation | Adapter builds only; not part of the native gate |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Unity | GoogleTest | C++ only; the shared core and tests must stay C, and the docs recommend Unity for embedded targets |
| Explicit `lib_deps` | `library.json` `dependencies` | Manifest dependencies resolve through the PlatformIO registry, fetching unrelated packages named `common`/`port` (D-03) |
| Textual include checker | A C preprocessor / clang-based tool | Over-engineered for a rule set of five libraries; would need the target toolchain and defeat the "no toolchain" property |
| Header-only `port` | A `port.c` with inline helpers | Adds a link dependency with no behaviour; verified that a header-only manifest works |
| `test_build_src` | `tests/` with no `src/` | Docs mark `test_build_src` "NOT RECOMMENDED"; `tests/` needs no application sources |

**Installation:**

```bash
# Nothing new is installed via pip/npm. Unity is fetched by PlatformIO on first use:
pio test -d tests -e native
# Unity 2.6.1 is installed into tests/.pio/libdeps/native/Unity
```

**Version verification:** PlatformIO Core 6.2.0 and pre-commit 4.7.0 were confirmed with
`pio --version` / `pre-commit --version`; Unity 2.6.1 was read from the installed
`library.json`; the host compiler is Apple clang 21.0.0. Training-data versions were not
trusted.

---

## Package Legitimacy Audit

> This phase installs one new external package, Unity, through the PlatformIO registry.
> The `package-legitimacy` seam could not reach PyPI from this sandbox (system certificate
> trust error), so registry age/download signals are **not observed** — that is an absence
> of observation, not a negative verdict.

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| `throwtheswitch/Unity` 2.6.1 | PlatformIO registry | installed on demand; long-established project | not observed (seam lookup failed) | `https://github.com/ThrowTheSwitch/Unity.git` (from installed manifest) | OK (install-verified) | Approved — pin `throwtheswitch/Unity@2.6.1` |
| `platformio` 6.2.0 | PyPI | pre-existing (FOUND-09) | not observed (seam lookup failed) | `https://github.com/platformio/platformio-core` | Not introduced by this phase | Approved (already the build system) |

**Packages removed due to [SLOP] verdict:** none

**Packages flagged as suspicious [SUS]:** none

*Provenance note:* the Unity name comes from the official PlatformIO unit-testing
documentation (`test_framework = unity`), not from a web search, and the installed
manifest declares `"license": "MIT"` and the official GitHub URL. The legitimacy seam's
registry leg is unavailable in this environment; the planner should treat the pin as
approved on that basis, not as a slopsquat.

---

## Architecture Patterns

### System Architecture Diagram

```
                       AUTHORING                              VERIFICATION
  ┌───────────────────────────────┐        ┌────────────────────────────────────────┐
  │ homeworks/<id>/src/*.cpp|.ino │        │ tests/  (platform = native)            │
  │  composition root             │        │  test/test_common_*/  test/test_port_*  │
  └───────┬───────────────┬───────┘        └───────┬───────────────────────┬────────┘
          │ calls         │ includes               │ includes              │ injects
          ▼               ▼                        ▼                       ▼
  ┌───────────────┐  ┌───────────────┐     ┌───────────────┐      ┌───────────────┐
  │ lib/common    │  │ lib/port      │     │ lib/common    │      │ lib/host      │
  │ pure C logic  │──▶│ 5 vtables     │◀────│ (same code)   │      │ fake_time     │
  │ no framework  │   │ header-only   │     └───────────────┘      │ fake_gpio     │
  └───────┬───────┘  └───────▲───────┘                            │ fake_i2c/spi  │
          │ calls through    │ implements                          │ fake_log      │
          │ function ptrs    │                                     └───────┬───────┘
          ▼                  │                                             │ implements
  ┌───────────────────────────┴──────────┐                                 │
  │ lib/arduino (.c) │ lib/espidf (.c)    │◀────────────────────────────────┘
  │ millis, pinMode   │ esp_timer, gpio_*  │
  │ log_printf        │ esp_log_write      │
  └───────────────────┴────────────────────┘

  ENFORCEMENT:  scripts/check_architecture.py  ── reads lib/**, homeworks/** ──▶ exit 0/1/2
                        ▲                                    │
                        │ pre-commit hook                    │ textual #include + lib_deps
                        │                                    ▼
                  .pre-commit-config.yaml          scripts/architecture/allowlist.json (empty)

  PURITY:  tests/ native build ──▶ compile_commands.json ──▶ host compiler only, no framework -I
```

Data flow for one test run:

1. `pio test -d tests -e native` resolves `extra_configs`, merges `native_unity`, installs/links Unity.
2. The LDF links only `common`, `port`, `host` (declared `lib_deps`).
3. Each `test/test_<area>/` folder compiles as an independent app with `main()` → `UNITY_BEGIN` → `RUN_TEST` → `UNITY_END`.
4. `lib/host` fakes advance logical time; no wall clock is read.
5. Unity prints `path:line: test_name\t[STATUS]` to stdout; PlatformIO prints durations to stderr.
6. The determinism driver extracts `suite/test_name: STATUS` and derived counts, discards everything else, and compares 20 digests.

### Recommended Project Structure

```
lib/
├── port/                       # header-only, no src/, no framework
│   ├── library.json            # name, version 0.2.0, build.includeDir
│   └── include/port/
│       ├── status.h            # enum port_status_t
│       ├── time.h              # port_time_t + static inline wrapper
│       ├── gpio.h              # port_gpio_t, port_gpio_mode_t
│       ├── i2c.h               # bus-level transfer/read/write
│       ├── spi.h               # bus-level write/transfer
│       └── log.h               # port_log_t, port_log_level_t
├── common/
│   ├── library.json
│   ├── include/common/{ring_buffer,timing,crc,hex}.h
│   └── src/{ring_buffer,timing,crc,hex}.c
├── arduino/
│   ├── library.json
│   ├── include/arduino/{time,gpio,log}.h
│   └── src/{time,gpio,log}.c    # pure C over Arduino C APIs
├── espidf/
│   ├── library.json
│   ├── include/espidf/{time,gpio,log}.h
│   └── src/{time,gpio,log}.c
└── host/
    ├── library.json
    ├── include/host/{fake_time,fake_gpio,fake_i2c,fake_spi,fake_log}.h
    └── src/{fake_time,fake_gpio,fake_i2c,fake_spi,fake_log}.c

partitions/
└── default_16MB.csv            # moved from the smoke project (D-18)

tests/
├── platformio.ini              # [env:native], extends native_unity, overrides extra_scripts
└── test/
    ├── test_common_ring_buffer/test_ring_buffer.c
    ├── test_common_timing/test_timing.c
    ├── test_common_crc/test_crc.c
    ├── test_common_hex/test_hex.c
    ├── test_port_contracts/test_contracts.c
    └── test_host_fakes/test_host_fakes.c

scripts/
├── check_architecture.py
├── architecture/allowlist.json # {"version": 1, "entries": []}
└── tests/
    ├── test_check_architecture.py
    ├── test_architecture_headers.py
    ├── test_native_determinism.py
    └── test_native_purity.py

docs/decisions/0008-*.md        # direction + ctx interpretation (D-02)
```

### Pattern 1: Consumer-owned vtable with an opaque `ctx`

**What:** `lib/port` declares a struct of function pointers plus `void *ctx`. The consumer
(`common`) holds a borrowed `const` pointer and calls through it. Adapters return an
instance by value; the composition root wires them.

**When to use:** any place pure logic needs time, a pin, a bus, or a log sink. Not for
framework idioms the course teaches.

**Example:**

```c
/* Source: lib/port/include/port/time.h — shape verified to compile as C11 and C++17
   with -Wall -Wextra -Werror -pedantic (clang 21). */
#pragma once
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif

typedef struct port_time {
    uint32_t (*now_ms)(void *ctx);
    void *ctx;
} port_time_t;

static inline uint32_t port_time_now_ms(const port_time_t *time) {
    return time->now_ms(time->ctx);
}

#ifdef __cplusplus
}
#endif
```

**Consumption rule:** `common` takes `const port_time_t *` as a parameter; it never stores
it in a global and never links against `port`'s objects (there are none). The compiler
resolves the call through the pointer, so `lib/port` needs no `.c`.

### Pattern 2: Header-only contracts, one status vocabulary

**What:** every contract lives in `include/port/<name>.h`; `status.h` is the single error
vocabulary; every operation that can fail returns `port_status_t`. Time reads and logging
do not fail and do not return it (documented exception, see Assumptions A1).

**When to use:** all five contracts, uniformly.

```c
/* lib/port/include/port/status.h */
typedef enum port_status_t {
    PORT_OK = 0,
    PORT_ERR_TIMEOUT,
    PORT_ERR_IO,
    PORT_ERR_INVALID_ARG,
    PORT_ERR_NOT_SUPPORTED
} port_status_t;
```

### Pattern 3: Pure logic receives time, never reads it

**What:** `common` contains no clock call. Timing helpers accept either a raw
`uint32_t now_ms` or a `const port_time_t *`, so tests drive logical time explicitly.

```c
/* lib/common/include/common/timing.h */
typedef struct common_debounce {
    bool stable;
    uint32_t last_change_ms;
} common_debounce_t;

uint32_t common_elapsed_ms(uint32_t now_ms, uint32_t since_ms);
bool common_timer_expired(uint32_t now_ms, uint32_t deadline_ms);
bool common_debounce_update(common_debounce_t *state, const port_time_t *time,
                            bool raw_input, uint32_t stable_ms);
```

Wraparound is handled with unsigned subtraction / signed difference, never with `>` on
absolute values (Pitfall "`millis()` wraparound", PITFALLS.md minor list).

### Pattern 4: Deny-by-default textual include scanner plus an explicit edge matrix

**What:** one pass per C/C++ file under `lib/**` and `homeworks/**`; comments stripped;
every `#include` classified as a project edge (first path segment names a known library)
or an external header; project edges are checked against the matrix, external headers
against a per-owner allowlist. Anything not explicitly allowed is a violation; the
allowlist file starts empty and every entry must carry a reason.

**When to use:** every phase from now on; this is the mechanical form of ARCH-05.

**Edge matrix (data, not code):**

| Owner | Allowed project edges | Allowed external headers |
|-------|----------------------|--------------------------|
| `port` | none | C standard headers only |
| `common` | `port` | C standard headers only |
| `arduino` | `port` | framework headers allowed; must not name `common`, `host`, or another adapter |
| `espidf` | `port` | same as `arduino` |
| `host` | `port` | C standard headers only |
| `homeworks/<id>` | `common`, `port`, `host`, exactly one adapter | framework headers allowed; must not escape into another homework |

**Why textual and not a preprocessor:** the rule is about source intent, not build results.
A relative `#include "../../arduino/include/..."` from `common` compiles and links natively
(verified), so the compiler cannot catch it.

### Pattern 5: A native test project above the libraries

**What:** `tests/` is a PlatformIO project whose only job is to build `common`, `port`,
and `host` on the host and run Unity. It has no `src/`; each `test/test_<area>/` folder is
an independent Unity application with `setUp`, `tearDown`, and `main`.

**When to use:** the shared-library suite; per-homework native tests stay inside the
homework project as `test/test_<area>/`.

**Key configuration fact:** `extra_scripts` is resolved relative to the **project**
directory, so `tests/` must override the inherited value.

### Anti-Patterns to Avoid

- **A universal HAL:** any `port_*` function that hides `pinMode`, `delay`, `Serial`, or a
  whole driver. The test is "does this hide a framework concept the course teaches?"
- **A `common` that reads time:** `millis()`/`esp_timer_get_time()` inside `lib/common`
  makes the suite non-deterministic and violates ARCH-02. Pass time in.
- **Manifest `dependencies`:** resolves through the registry and fetches stranger
  packages (D-03). List `lib_deps` explicitly.
- **`lib_extra_dirs`:** deprecated since PlatformIO 6.0 and silently pulls every library
  in `lib/`, including adapters, into native builds.
- **Asserting on PlatformIO's summary table:** it is on stderr, carries durations, and its
  counts do not correspond one-to-one with Unity test cases.
- **A `.cpp` entry inside `lib/`:** `lib/*/src/**` stays `.c`; C++ is only the homework
  composition root (Phase 2 D-15 amended).
- **Designated initializers in C++ homework code:** `(port_time_t){ .now_ms = f, ... }`
  is a C99 compound literal and a C++20 extension; it fails `-pedantic-errors` under
  C++17 (verified). Call the adapter factory instead.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Test harness, assertions, failure reporting | A custom `assert` loop | Unity via `test_framework = unity` | setUp/tearDown, per-test isolation, failure line numbers, exit code |
| Deterministic clock | `time()`, `clock()`, sleeps | `host_fake_time_t` + explicit `advance(ms)` | Wall clock makes the 20-run proof fail intermittently |
| Dependency analysis of C sources | A preprocessor or clang tooling | One comment-stripping `#include` regex | The rule needs source intent, runs without a toolchain, and stays under 300 lines |
| Package/dependency resolution | A manifest dependency graph | Explicit `lib_deps` + a closure rule in the checker | Registry resolution is the failure mode D-03 avoids |
| CRC tables/math | A third-party CRC library | A 20-line bitwise or a `static const uint8_t[256]` table | No dependency; the polynomial and check value become part of the test contract |
| Build orchestration | Make/CMake wrappers | PlatformIO | Already pinned; native and target share one project model |
| Shelling out to find changed files | Custom globbing | `pathlib.Path.rglob` with explicit roots | Deterministic, no shell, no symlink following |

**Key insight:** in this phase every "hand-rolled" piece is deliberately tiny and
testable, and every non-trivial piece (build, test framework, package resolution) is
delegated. The one place where a text parser is correct is the architecture rule, because
the rule is about what the source says, not what the compiler produces.

---

## Runtime State Inventory

This phase deletes a directory (`homeworks/0_0-toolchain-smoke/`) and moves a data file
(`default_16MB.csv`). The audit below distinguishes tracked state from runtime state.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | None — no database, cache, or datastore references the smoke project or the CSV path. Verified by `grep` across non-planning files. | None |
| Live service config | None — no external service (GitHub ruleset, Wokwi, Pages) names the smoke project. | None |
| OS-registered state | None — no scheduler entry, launch agent, or service unit. | None |
| Secrets/env vars | None — the smoke project has no `secrets.h` or env injection. | None |
| Build artifacts | `homeworks/0_0-toolchain-smoke/.pio/` and `compile_commands.json` are **untracked/ignored** (`git ls-files` lists only five files: `README.md`, `default_16MB.csv`, `platformio.ini`, `sdkconfig.defaults`, `src/main.cpp`). `.pio/libdeps/**` symlink caches pointing into `lib/` are recreated by the next build. | Delete the directory from the working tree, not only from the index (`git rm -r` leaves ignored files behind). No data migration. |
| Documentation references | `docs/decisions/0007-symlink-shared-libraries.md:89` names the smoke project as historical evidence (keep — it is history). `scripts/tests/test_pio_scripts.py:38-39` hard-reads the project (D-20). `scripts/tests/test_gitignore.py:86-88,136,171-184` uses smoke-project **path strings** as ignore-pattern fixtures; they are not existence checks but become misleading. | Refactor `test_pio_scripts.py`; retarget the `test_gitignore.py` fixture paths to a generic `homeworks/1_1-example/...`. |
| Tracked CSV | `homeworks/0_0-toolchain-smoke/default_16MB.csv` is tracked; the new `partitions/default_16MB.csv` must be added in the same change that deletes it, or a checkout of that commit has two copies / zero copies. | Move, do not copy. |

**Canonical question — after every file in the repo is updated, what runtime systems still
hold the old path?** Nothing. The CSV path is resolved at build time from
`platformio.shared.ini`; no cache embeds it. The `.pio` trees are disposable.

---

## Common Pitfalls

### Pitfall 1: `tests/` inherits `extra_scripts` with the wrong depth

**What goes wrong:** `[env:native] extends = native_unity` inherits
`extra_scripts = pre:../../scripts/pio/compiledb.py`. From `tests/`, `../../scripts` is two
levels above the repository, and the build fails with
`*** missing SConscript file '/private/tmp/scripts/pio/compiledb.py'` (observed in a probe
that copied `platformio.shared.ini` and `tests/` into a temp tree).

**Why it happens:** PlatformIO documents `extra_scripts` paths as "relative to the project
folder", not to the config file that declared them.

**How to avoid:** override in `tests/platformio.ini`:

```ini
extra_scripts = pre:../scripts/pio/compiledb.py
```

**Warning signs:** a build that works from `homeworks/<id>/` and fails from `tests/`, or a
"missing SConscript" path that points outside the repository.

### Pitfall 2: `common` without `port` in `lib_deps`

**What goes wrong:** `lib/common/include/common/timing.h:2:10: fatal error: 'port/time.h'
file not found` (verified by removing the `port` entry from a working project).

**Why it happens:** D-03 forbids manifest `dependencies`, so PlatformIO does not
transitively add `port`'s include directory. The include path exists only for libraries the
project declares.

**How to avoid:** every consumer lists `port`; the checker enforces the closure
(`common`/`host`/adapter present ⇒ `port` present).

**Warning signs:** "file not found" for a header that exists in `lib/port/include/`.

### Pitfall 3: `extends` does not merge list values

**What goes wrong:** adding `-Werror` in a child env replaces the inherited
`build_flags`, silently dropping `-std=c11 -Wall -Wextra`.

**Why it happens:** PlatformIO/`configparser` semantics: a key present in the child wins
wholesale.

**How to avoid:** repeat the full list in `tests/platformio.ini`, or interpolate
`${native_unity.build_flags}` and append. Repetition is clearer for three flags.

**Warning signs:** warnings that disappear after adding an option.

### Pitfall 4: Designated initializers in C++ homework code

**What goes wrong:** `port_time_t t = (port_time_t){ .now_ms = f, .ctx = &n };` fails under
`-std=c++17 -pedantic-errors` with "compound literals are a C99-specific feature" and
"designated initializers are a C++20 extension" (verified with clang 21).

**Why it happens:** the `.ino`/`.cpp` composition root is C++, while the contract examples
are C.

**How to avoid:** call the adapter factory (`port_time_t t = arduino_time_port();`) or use
positional aggregate initialization (`port_time_t t = { f, &n };`) in C++ code.

**Warning signs:** works with GCC defaults, breaks under `-pedantic` or a stricter GCC.

### Pitfall 5: Arduino logging silently compiled out

**What goes wrong:** `log_i(...)`/`log_d(...)` expand to `do {} while (0)` when
`ARDUHAL_LOG_LEVEL < level`; the default `CORE_DEBUG_LEVEL` is 0, so a naive log adapter
compiles and emits nothing.

**Why it happens:** `esp32-hal-log.h` gates each macro on `CORE_DEBUG_LEVEL`.

**How to avoid:** call `log_printf("%s\n", message)` (unconditional), or set
`-DCORE_DEBUG_LEVEL=3` deliberately in the Arduino environment. Verified that
`log_printf` is declared unconditionally and `pinMode`/`digitalWrite`/`digitalRead`/
`millis` are C-callable.

**Warning signs:** a test asserts a log line and the fake receives nothing on target while
the host fake passes.

### Pitfall 6: Arduino I2C/SPI adapters cannot stay pure C

**What goes wrong:** `Wire` and `SPI` are C++ classes; there is no C API. D-08 defers those
adapters, which is fortunate: when they arrive, `lib/arduino/src/i2c.cpp|spi.cpp` will be
needed, contradicting the blanket "library sources stay pure C" wording.

**Why it happens:** `Arduino.h` exposes only its C surface to a C compiler; `Serial`,
`Wire`, and `SPI` are guarded by `__cplusplus`.

**How to avoid:** record the exception now (open question O5). ESP-IDF's C headers exist
and can back a pure-C adapter — `driver/i2c_master.h` (new API) or the legacy
`driver/i2c.h`, plus `driver/spi_master.h` and `driver/gpio.h`, all present in ESP-IDF
6.1.0 on this machine — so the ESP-IDF adapters can stay `.c`.

**Warning signs:** a future plan tries to include `Wire.h` from a `.c` file.

### Pitfall 7: `pio test` from the repository root

**What goes wrong:** `pio test -e native` at the root fails with
`NotPlatformIOProjectError` (verified). AGENTS.md step 3 currently documents exactly this
command.

**Why it happens:** the root has no `platformio.ini`; the test project lives in `tests/`.

**How to avoid:** use `pio test -d tests -e native` everywhere (AGENTS.md, scripts, CI) and
update AGENTS.md step 3 in this phase so the documented gate is runnable.

**Warning signs:** "Not a PlatformIO project" in the quick-start.

### Pitfall 8: Comparing raw `pio test` output

**What goes wrong:** stdout carries `path:line:` prefixes; stderr carries durations
(`Took 0.22 seconds`, `00:00:00.222`); a failure row inserts an assertion message
(`test_fail: Expected 2 Was 1\t[FAILED]`). A digest over raw text changes every run.

**Why it happens:** PlatformIO's console formatting is not a stable interface.

**How to avoid:** extract per-test rows with a per-line anchored regex, drop path/line and
message, derive counts from the rows themselves, and assert the process exit code. Do not
use PlatformIO's summary counts: a run with two Unity tests reported
`3 test cases: 1 failed, 1 succeeded`.

**Warning signs:** a 20-run comparison that fails only on timing text.

### Pitfall 9: `test_framework = unity` auto-installs an unpinned range

**What goes wrong:** without an explicit entry, PlatformIO installs
`throwtheswitch/Unity @ ^2.6.1`, so a future release changes the suite under you (Pitfall
C7).

**Why it happens:** the framework integration is a convenience default.

**How to avoid:** add `throwtheswitch/Unity@2.6.1` to `tests/lib_deps`; verified that the
explicit pin wins and only one copy is installed.

**Warning signs:** "Installing throwtheswitch/Unity @ ^2.6.1" in a build log.

### Pitfall 10: Project-local `lib/` auto-discovery

**What goes wrong:** PlatformIO scans `<project>/lib` automatically. A probe with a
project-root `lib/` that contained an adapter linked the adapter even though only `common`
was declared — the classic `lib_extra_dirs` trap.

**Why it happens:** the LDF's default storage includes the project's own `lib_dir`.

**How to avoid:** keep `tests/` a **subdirectory** so its project lib dir is `tests/lib`
(absent); never add a root `platformio.ini` that would make the repository root a project.

**Warning signs:** an adapter source appears in a native build's compile database.

### Pitfall 11: `lib_ignore` names are library names

**What goes wrong:** ignoring `arduino` by folder name that differs from the manifest name
silently does nothing.

**Why it happens:** the docs state the value is the library name shown in `<...>` in the
dependency graph.

**How to avoid:** this phase needs no `lib_ignore`; if one is added, copy the name from the
graph. Prefer explicit `lib_deps`.

### Pitfall 12: Unity requires `setUp` and `tearDown`

**What goes wrong:** a test file with `main()` but no `setUp`/`tearDown` fails to link,
because `RUN_TEST` calls both.

**How to avoid:** every test file defines both, even empty; document it in the test
skeleton.

---

## Code Examples

### `tests/platformio.ini` (verified end to end)

```ini
; tests/platformio.ini — the shared-library native suite.
; extra_configs resolves relative to this project directory (verified).
[platformio]
default_envs = native
extra_configs = ../platformio.shared.ini

[env:native]
extends = native_unity
test_framework = unity
; extends does not merge lists: repeat the parent's flags and add -Werror.
build_flags =
    -std=c11
    -Wall
    -Wextra
    -Werror
; The shared native_unity section points at ../../scripts/..., which is two
; levels above the repository when resolved from tests/. Override it.
extra_scripts = pre:../scripts/pio/compiledb.py
lib_deps =
    common=symlink://../lib/common
    port=symlink://../lib/port
    host=symlink://../lib/host
    throwtheswitch/Unity@2.6.1
test_dir = test
```

### Unity test skeleton

```c
/* tests/test/test_common_timing/test_timing.c
   Source: Unity 2.6.1 conventions (setUp/tearDown are invoked by RUN_TEST). */
#include <unity.h>

#include "common/timing.h"
#include "host/fake_time.h"

static host_fake_time_t fake;

void setUp(void) { host_fake_time_reset(&fake); }
void tearDown(void) {}

static void test_elapsed_handles_wraparound(void) {
    TEST_ASSERT_EQUAL_UINT32(32u, common_elapsed_ms(0x00000010u, 0xFFFFFFF0u));
}

static void test_debounce_uses_fake_time(void) {
    const port_time_t clock = host_fake_time_port(&fake);
    common_debounce_t debounce = { false, 0 };

    TEST_ASSERT_FALSE(common_debounce_update(&debounce, &clock, true, 50u));
    host_fake_time_advance(&fake, 49u);
    TEST_ASSERT_FALSE(common_debounce_update(&debounce, &clock, true, 50u));
    host_fake_time_advance(&fake, 1u);
    TEST_ASSERT_TRUE(common_debounce_update(&debounce, &clock, true, 50u));
}

int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_elapsed_handles_wraparound);
    RUN_TEST(test_debounce_uses_fake_time);
    return UNITY_END();
}
```

### Adapter factories (pure C, both frameworks verified to compile)

```c
/* lib/arduino/src/time.c */
#include <Arduino.h>
#include "arduino/time.h"

static uint32_t arduino_now_ms(void *ctx) {
    (void)ctx;
    return (uint32_t)millis();
}

port_time_t arduino_time_port(void) {
    port_time_t port = { arduino_now_ms, NULL };
    return port;
}
```

```c
/* lib/espidf/src/time.c */
#include <stdint.h>
#include "esp_timer.h"
#include "espidf/time.h"

static uint32_t espidf_now_ms(void *ctx) {
    (void)ctx;
    return (uint32_t)(esp_timer_get_time() / 1000);
}

port_time_t espidf_time_port(void) {
    port_time_t port = { espidf_now_ms, NULL };
    return port;
}
```

### `check_architecture.py` core loop (sketch)

```python
INCLUDE = re.compile(r'^\s*#\s*include\s*[<"]([^>"]+)[>"]')
EDGES = {
    "port": frozenset(),
    "common": frozenset({"port"}),
    "arduino": frozenset({"port"}),
    "espidf": frozenset({"port"}),
    "host": frozenset({"port"}),
}
EXTERNAL_OK = {
    "port": C_STANDARD_HEADERS,
    "common": C_STANDARD_HEADERS,
    "host": C_STANDARD_HEADERS,
    "arduino": None,   # framework headers allowed; project names still checked
    "espidf": None,
}
BLOCKING = ("delay(", "delayMicroseconds(", "vTaskDelay", "sleep(", "usleep(",
            "HAL_Delay(", "millis(", "esp_timer_get_time(", "xTaskGetTickCount(")

def owner_of(relative_path: Path) -> str:
    parts = relative_path.parts
    if parts[0] == "lib":
        return parts[1]
    return "homeworks/" + parts[1]

def classify(name: str) -> tuple[str, str]:
    if name.startswith(("./", "../")):
        return "escape", name
    first = name.split("/", 1)[0]
    if first in EDGES:
        return "project", first
    return "external", name
```

Exit codes: `0` clean, `1` violation or stale allowlist entry, `2` usage/environment
(unreadable root, malformed allowlist, no `lib/`).

### Normalized digest for the 20-run proof (validated against real output)

```python
# Suite = the test_<area> directory that owns the file, e.g. "test_common_timing".
TEST_LINE = re.compile(
    r"^test/(?P<suite>test_[^/]+)/[^:]+:\d+: "
    r"(?P<name>\w+)(?:: .*?)?\t\[(?P<status>PASSED|FAILED|IGNORED)\]$"
)

def digest(stdout: str) -> str:
    rows = []
    for line in stdout.splitlines():
        match = TEST_LINE.match(line)          # per-line anchor; NOT findall(text)
        if match:
            rows.append((match["suite"], match["name"], match["status"]))
    lines = [f"{suite}/{name}: {status}" for suite, name, status in rows]
    for status in ("PASSED", "FAILED", "IGNORED"):
        lines.append(f"{status.lower()}={sum(1 for row in rows if row[2] == status)}")
    return "\n".join(lines)
```

Include the suite name because two suites may legitimately declare the same function name;
the ordered list then stays unambiguous.

Validated: four consecutive runs of a two-test suite produced an identical SHA-256; a
failing run produced `test_fail: FAILED`, `failed=1`, exit 1.

### Pre-commit hook

```yaml
      - id: check-architecture
        name: shared-library dependency rule
        language: system
        entry: python3 scripts/check_architecture.py
        files: ^(lib|homeworks)/
        pass_filenames: false
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `lib_extra_dirs = ../../lib` | `lib_deps = name=symlink://../../lib/name` | Deprecated in PlatformIO 6.0 | Explicit dependency set; an adapter cannot leak into a native build |
| `test_build_src = true` + `PIO_UNIT_TESTING` guards | Split libraries out of `src/`; `tests/` project links them | Documented as "NOT RECOMMENDED" | No entry-point guards; tests build only what they name |
| Compile a whole firmware to test logic | Native Unity suite with injected fakes | Long-standing embedded practice | Millisecond feedback; deterministic |
| `delay()`/`millis()` inside shared logic | Injected `port_time_t` + fake clock | Architecture decision (D-06) | Host-testable timing; 20-run determinism is provable |
| Hand-maintained dependency rules in docs | A checker in pre-commit | This phase | Drift becomes a failing commit, not a review comment |
| Per-library version strings in `.c` | Version only in `library.json` | D-04 | One source of truth (WR-03) |

**Deprecated/outdated:**

- `lib_extra_dirs` — deprecated since PlatformIO 6.0, removal pending.
- `compile_commands.json` committed to git — stale and machine-specific; already ignored.
- Raw `pio test` output comparison — durations and paths make it non-deterministic.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Time reads and logging do not need `port_status_t`; every other operation does | Pattern 2 | A uniform-return choice would change five signatures and every adapter; the opposite choice (status everywhere) adds branches callers will ignore |
| A2 | The five contracts need only a 64-pin fake GPIO array and 32 log lines | Pattern 3 | Test fakes would overflow or reject valid indices; constants are cheap to raise, and the bound is documented |
| A3 | `uint32_t` milliseconds is sufficient time resolution and range for the course | Pattern 1 | A future microsecond contract would need a second member; the 49-day wraparound is handled by the arithmetic |
| A4 | Bus-level I2C/SPI without per-call timeouts is implementable by both frameworks | Pattern 1 | Arduino `Wire.setTimeOut` is global; a per-call parameter would be a fake. Deferred adapters are the first real check |
| A5 | `common` needs no logging module this phase | Don't Hand-Roll | If a later module needs logging, it takes a `const port_log_t *`; no redesign |
| A6 | 20 `pio test` runs fit comfortably in the local gate (~10-15 s after the first build) | Validation | A slow CI runner could exceed a test timeout; use a 300 s per-run timeout and a single build |
| A7 | The allowlist stays empty through this phase | Pattern 4 | An entry would weaken the rule; every entry carries a reason and a stale entry fails |
| A8 | Arduino I2C/SPI adapters can later be `.cpp` without breaking the public C headers | Pitfall 6 | If D-15's "sources stay pure C" is read as absolute, the exception needs an ADR amendment before those adapters land |
| A9 | `-Werror` is safe alongside Unity 2.6.1 | Standard Stack, Validation | Verified with Apple clang 21 only; a GCC-only warning in Unity or the host headers would break Linux CI. Fallback: drop `-Werror` in `tests/` and keep the warnings visible |

**If this table is empty:** not applicable — eight assumptions are recorded.

---

## Open Questions

1. **Should Unity be pinned explicitly?**
   - What we know: `test_framework = unity` installs `^2.6.1`; an explicit
     `throwtheswitch/Unity@2.6.1` entry wins and installs once (verified).
   - What's unclear: whether the planner considers a third-party test dependency inside
     the repository's pin policy (Pitfall C7) or an acceptable convenience default.
   - Recommendation: pin explicitly; it costs one line and makes the suite reproducible.

2. **Disposition of Phase 2 WR-04 (over-broad `.gitignore` patterns).**
   - What we know: STATE lists WR-01..WR-04; CONTEXT discharges CR-01, WR-01, WR-03, and
     WR-02 is discharged by adding the missing assertions. WR-04 has no decision.
   - What's unclear: whether it belongs to this phase or to Phase 6/8.
   - Recommendation: leave WR-04 out of this phase; note it in the plan's risks so it is
     not silently dropped.

3. **`lib/port/library.json` `srcDir`.**
   - What we know: a manifest with `"srcDir": "src"` and no `src/` directory builds and
     supplies its include path (verified).
   - What's unclear: whether manifest uniformity or accuracy is preferred.
   - Recommendation: drop `srcDir` for `port`, keep `includeDir`; update
     `test_pio_scripts.py` to assert `includeDir` for all five and `srcDir` only where a
     source directory exists.

4. **Where the contract rationale lives.**
   - What we know: `docs/standards/` is Phase 5; ADR-0008 is this phase.
   - What's unclear: whether every signature decision belongs in ADR-0008 or in header
     comments.
   - Recommendation: ADR-0008 records only the direction and the `ctx` interpretation
     (D-02/D-06); per-contract invariants live as header comments beside the declarations.

5. **Future Arduino I2C/SPI adapters and the pure-C rule.**
   - What we know: `Wire`/`SPI` are C++ classes; the ESP-IDF drivers are C.
   - What's unclear: whether Phase 2 D-15 amended ("library sources stay pure C") is
     intended to bind adapters forever.
   - Recommendation: record the exception in the plan's deferred-ideas note; amend or
     supersede the sentence when those adapters are actually written, not now.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| PlatformIO Core | Build/test, determinism, purity | ✓ | 6.2.0 | — |
| Python (stdlib `unittest`) | Checker and all Python tests | ✓ | 3.13.13 (PlatformIO venv) | System Python 3.x |
| Host C compiler | Native build and tests | ✓ | Apple clang 21.0.0 | GCC on Linux CI |
| Unity | Shared suite | ✓ (on first use) | 2.6.1 | Pre-populate `tests/.pio/libdeps/native/Unity` for offline runs |
| pre-commit | Architecture hook | ✓ | 4.7.0 | Run `python3 scripts/check_architecture.py` directly |
| git | Repository-root resolution in tests/checkers | ✓ | 2.54.0 | — |
| `platformio/espressif32` | Adapter compilation only | ✓ | 8.0.0 | Not needed for the native gate |
| Network (PlatformIO registry) | First Unity install | ✓ (install succeeded) | — | Cache `.pio/libdeps` in CI |

**Missing dependencies with no fallback:** none.

**Missing dependencies with fallback:** Unity on a cold offline machine — the first
`pio test` needs the registry; after that the package is cached in `.pio/libdeps/native`.

---

## Validation Architecture

> `workflow.nyquist_validation` is `true` in `.planning/config.json`; this section is
> required.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Python `unittest` (stdlib) + Unity 2.6.1 (C) |
| Config file | none — `python3 -m unittest discover -s scripts/tests -v`; PlatformIO config at `tests/platformio.ini` |
| Quick run command | `python3 -m unittest discover -s scripts/tests -v` |
| Full suite command | `pio test -d tests -e native && python3 -m unittest discover -s scripts/tests -v && pre-commit run --all-files` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| ARCH-01 | Five contracts exist, header-only, no framework includes, `extern "C"` guarded | unit (Python) | `python3 -m unittest scripts.tests.test_architecture_headers -v` | ❌ Wave 0 |
| ARCH-01 | Contracts callable and observable at runtime | unit (C) | `pio test -d tests -e native --filter test_port_contracts` | ❌ Wave 0 |
| ARCH-02 | Ring buffer/timing/CRC/hex behave; no blocking token in `common` | unit (C + Python) | `pio test -d tests -e native --filter test_common_*`; `python3 -m unittest scripts.tests.test_check_architecture -v` | ❌ Wave 0 |
| ARCH-03 | Fakes implement the same vtable types; error injection returns the scripted status | unit (C) | `pio test -d tests -e native --filter test_host_fakes` | ❌ Wave 0 |
| ARCH-05 | Checker rejects `common → framework`, `common → adapter`, `port → common`, adapter → common, path escapes, and bad `lib_deps` | unit (Python, fixture trees) | `python3 -m unittest scripts.tests.test_check_architecture -v` | ❌ Wave 0 |
| ARCH-05/06 | Native compile gate fails on a framework include; succeeds on the real tree | integration (PlatformIO) | `python3 -m unittest scripts.tests.test_native_purity -v` | ❌ Wave 0 |
| ARCH-06 | Suite passes 20 consecutive times with an identical digest | integration (PlatformIO) | `python3 -m unittest scripts.tests.test_native_determinism -v` | ❌ Wave 0 |
| ARCH-07 | I2C/SPI contracts are bus-level; no whole-driver names; no framework leak | review + unit (Python) | checker matrix + header allowlist; review of `i2c.h`/`spi.h` | ❌ Wave 0 |
| D-18 | `board_build.partitions` resolves to an existing file from a project-depth path | unit (Python) | `python3 -m unittest scripts.tests.test_pio_scripts -v` | ✅ exists, edits required |
| D-20 | Suite does not read the smoke project | unit (Python) | same | ✅ exists, edits required |

### Sampling Rate

- **Per task commit:** `python3 -m unittest discover -s scripts/tests -v` plus, for C
  changes, `pio test -d tests -e native`.
- **Per wave merge:** the full suite command above.
- **Phase gate:** full suite green, `pre-commit run --all-files` green, and a manual
  20-run determinism confirmation before `/gsd-verify-work`.

### Wave 0 Gaps

- [ ] `tests/platformio.ini` and `tests/test/test_*/*.c` — the entire native project.
- [ ] `scripts/architecture/allowlist.json` — empty, schema described in the checker.
- [ ] `scripts/tests/test_check_architecture.py` — positive tree + at least twelve negative
      fixture cases (framework include, adapter include, reverse edge, adapter→common,
      `host`→framework, path escape, blocking token, allowlisted violation, stale
      allowlist, malformed allowlist, multi-adapter env, `host` in target env).
- [ ] `scripts/tests/test_architecture_headers.py` — header layout, `#pragma once`,
      `extern "C"` guard, C-standard-only includes for `port`/`common`/`host`.
- [ ] `scripts/tests/test_native_determinism.py` — 20 runs, normalized digest, explicit
      failure when `pio` is absent.
- [ ] `scripts/tests/test_native_purity.py` — host-compiler-only compile database and the
      negative `pio run` build.
- [ ] No framework install needed: Python tests are stdlib-only; Unity arrives through
      PlatformIO on the first test run.

---

## Security Domain

> `security_enforcement` is `true`, ASVS level 1.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | — |
| V3 Session Management | no | — |
| V4 Access Control | no | — |
| V5 Input Validation | yes | `argparse`; strict JSON schema checks on the allowlist; comment-stripped regexes; no `eval`, no interpolation |
| V6 Cryptography | no (CRC and hex are data integrity/encoding, not cryptography) | Do not present CRC as a security control in docs |
| V7 Error Handling and Logging | yes | Exit codes `0/1/2`; one-line `FAIL` diagnostics; no tracebacks; no secrets |
| V10 Malicious Code | yes | `subprocess.run([...])` with list arguments only; never `shell=True`; tests never execute repository scripts |
| V12 Files and Resources | yes | Resolve `--dir` and every include against the root; reject `../` escapes; walk with `followlinks=False`; cap allowlist size |
| V14 Configuration | yes | Parse `platformio.ini` with `interpolation=None`; treat `extends`/`extra_configs` as data, not code |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Shell injection through a filename in `--dir` or a symlink name | Tampering | `subprocess.run(["pio", "test", "-d", path, "-e", "native"])`, no shell |
| Path traversal in an `#include` (`../../...`) | Information disclosure | Classifier rejects any include starting with `../` or `./` before resolution |
| Symlink escape while scanning `lib/**` | Information disclosure | `os.walk(followlinks=False)` and `Path.resolve()` containment check |
| Oversized/malformed allowlist JSON | Denial of service | Read with a byte cap; `json.loads`; schema validation; exit 2 on failure |
| Checker silently passing an empty tree | Repudiation | Missing `lib/` is exit 2, never exit 0 |
| Fake adapters reaching firmware | Elevation of privilege | Ini rule rejects `host` in any non-native environment |
| CRC mistaken for a security primitive | Spoofing | Header comment and ADR wording state "data integrity, not authentication" |

---

## Sources

### Primary (HIGH confidence)

- `.planning/research/ARCHITECTURE.md` — layer rule, ports-and-adapters shape, testing
  architecture (project research, already reviewed).
- `.planning/research/PITFALLS.md` — C3, C8, C12, C15, M2, M8 (project research).
- PlatformIO docs via Context7 `/platformio/platformio-docs` — test hierarchy, shared
  code (`test_build_src` "NOT RECOMMENDED"), `test_dir`, `test_filter`, `lib_ignore`
  (library names, not folder names), `symlink://` local folder semantics, `extra_scripts`
  "relative to the project folder", `extra_configs` merge behaviour.
  `[CITED: docs.platformio.org/en/latest/advanced/unit-testing/structure/shared-code.html]`
- Unity docs via Context7 `/throwtheswitch/unity` — `setUp`/`tearDown` are invoked by
  `RUN_TEST`; `TEST_ASSERT_EQUAL_UINT32`; `TEST_IGNORE`.
- Local execution on this machine (2026-10-24): PlatformIO 6.2.0; native Unity project
  passes; `common`+`port` header-only layout links; Arduino and ESP-IDF adapters compile
  as C with the listed APIs; `common → adapter` relative include compiles; native
  `Arduino.h` include fails; `../../partitions/default_16MB.csv` builds in both ESP
  environments; `pio test` exit codes and output-stream split.
- In-repo files read this session (see the verbatim quotes below).

### Secondary (MEDIUM confidence)

- `.planning/research/STACK.md` §1.4–1.8 — `symlink://`, native Unity, N16R8 configuration
  (line 248's "port depends on common" is superseded by D-01/D-03).
- `https://www.volatileint.dev/posts/dependency-inversion-c/` — interface owned by the
  consumer, adapters return instances, consumers hold a borrowed `const` pointer.
- `docs/decisions/0002-ports-and-adapters-no-universal-hal.md` and
  `docs/decisions/0007-symlink-shared-libraries.md`.

### Tertiary (LOW confidence)

- The exact contract signatures are a design choice, not an observed standard; they are
  recorded in the Assumptions Log where they could be wrong.

### Verbatim in-repo values used above

- `platformio.shared.ini:34` — `    -std=c11`; `:31` — `[native_unity]`; `:37` —
  `extra_scripts = pre:../../scripts/pio/compiledb.py`. `[VERIFIED: platformio.shared.ini:31-37]`
- `platformio.shared.ini:10` and `:24` — `board_build.partitions = default_16MB.csv`
  (to become `../../partitions/default_16MB.csv`). `[VERIFIED: platformio.shared.ini:10,24]`
- `lib/common/library.json:3` — `"version": "0.1.0",` (same line in all five manifests).
  `[VERIFIED: lib/common/library.json:3]`
- `lib/common/src/common.c:3` — `const char *common_version(void) { return "0.1.0"; }`
  `[VERIFIED: lib/common/src/common.c:3]`
- `docs/decisions/README.md:32` — `Next number: **0008**.` `[VERIFIED: docs/decisions/README.md:32]`
- `scripts/tests/test_pio_scripts.py:38` —
  `PROJECT_INI = REPO_ROOT / "homeworks" / "0_0-toolchain-smoke" / "platformio.ini"`.
  `[VERIFIED: scripts/tests/test_pio_scripts.py:38]`
- `AGENTS.md:25` — `` | 3 | `pio test -e native` | Run firmware-side native tests, once
  `homeworks/` exists (Phase 2). | `` `[VERIFIED: AGENTS.md:25]`
- `homeworks/0_0-toolchain-smoke/platformio.ini:7-10` —
  `lib_deps =` / `    common=symlink://../../lib/common` / `    port=symlink://../../lib/port` /
  `    host=symlink://../../lib/host`. `[VERIFIED: homeworks/0_0-toolchain-smoke/platformio.ini:7-10]`

---

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH — versions read from the installed tools, not from training data.
- Architecture and contract shapes: MEDIUM — the pattern is settled (ADR-0002, D-01, D-05,
  D-09); exact member names are a design choice, and no consumer exercises I2C/SPI yet.
- PlatformIO/Unity mechanics: HIGH — every load-bearing claim was executed on this machine.
- Checker design: HIGH for mechanics, MEDIUM for the exact edge matrix (the rule set is a
  decision; the negative fixtures make it testable).
- Pitfalls: HIGH — each recorded pitfall was reproduced or read from the pinned headers.

**Research date:** 2026-10-24
**Valid until:** 2026-11-23 (30 days; PlatformIO and Unity are stable, but the ESP32
platform and Unity minor versions move quickly — re-check pins before Phase 8).

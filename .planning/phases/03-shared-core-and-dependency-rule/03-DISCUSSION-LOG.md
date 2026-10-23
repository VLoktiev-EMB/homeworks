# Phase 3: Shared Core and Dependency Rule - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-10-24
**Phase:** 3-Shared Core and Dependency Rule
**Areas discussed:** Dependency direction, Port surface, Common module set, Test gate and
determinism, `ctx` and statelessness, `lib/host` placement, Local gate placement, Package
metadata and versions, Partitions CSV location, Error and log model, Checker scan scope, C
style timing

---

## Dependency direction

| Option | Description | Selected |
|--------|-------------|----------|
| A. `common → port` | `port` is the lowest layer with no dependencies; `common` includes port headers and calls injected functions; adapters include `port` only. Matches ARCH-05 and the research component table; requires amending ADR-0002 or a new ADR-0008. | ✓ |
| B. `port → common` | ADR-0002 literally: `common` has no project dependencies and receives time/data as parameters; `port` may use `common` types; adapters see `common` transitively. Timer-driven state machines cannot live in `common`. | |
| C. Both independent | No edges between `common` and `port`; pure functions take primitives. Simplest checker, most manual wiring, no shared domain vocabulary. | |
| Claude decides | Choose from the report and record the reasoning in CONTEXT.md. | |

**User's choice:** A. `common → port`
**Notes:** The user requested additional research before deciding ("ще ресерч і надай мені
звіти для вирішення") and then asked what each library would actually contain ("поясни
мені що планується у common,port,adapter?") and whether homework-specific functions would
have to live in `common`. After the explanation, including the rule that domain logic
stays in the homework, the user chose A.

---

## Port surface

| Option | Description | Selected |
|--------|-------------|----------|
| 2. Five contracts, implementations on demand | All five contracts (ARCH-01 satisfied); host fakes for all five; Arduino/ESP-IDF implement time, log, GPIO; I2C/SPI framework adapters deferred. | ✓ |
| 1. Full scope | Five contracts plus full implementations in Arduino, ESP-IDF, and host immediately. Literal ARCH-01/ARCH-03, but I2C/SPI bring bus lifecycle without a consumer (Pitfall C15). | |
| 3. Minimum time + log | Only time and log (contracts, adapters, fakes); GPIO/I2C/SPI fully deferred. Purest YAGNI, but a documented deviation from ARCH-01. | |
| Claude decides | Choose from the report and record the decision. | |

**User's choice:** 2. Five contracts, implementations on demand
**Notes:** Research confirmed that ARCH-01 requires the contracts, not every adapter
implementation, so the chosen option satisfies the requirement without speculative bus
lifecycle work.

---

## Common module set

| Option | Description | Selected |
|--------|-------------|----------|
| Proven minimum | `ring_buffer` + `timing` + `crc`/`hex`. Three small domain-neutral modules with full tests; no speculative interfaces. | ✓ |
| All ARCH-02 categories | `ring_buffer` + `timing` + `crc` + `fixed_point` + generic state machine + calculations. Literal, but the last three have no consumer (C15). | |
| Minimum-minimum | Only `ring_buffer` + `timing`; codecs and calculations when the first homework appears. | |
| Claude decides | Choose from the report and record the decision. | |

**User's choice:** Proven minimum
**Notes:** `timing` includes a small `port_time_t`-based debounce/elapsed helper so success
criterion 4 genuinely exercises fake time from `lib/host`.

---

## Test gate and determinism

| Option | Description | Selected |
|--------|-------------|----------|
| A. Python test, 20 runs | `tests/` is a PlatformIO project with `[env:native]`, `test_framework = unity`, and explicit `lib_deps` for `common`/`port`/`host`. `scripts/tests/test_native_determinism.py` runs `pio test -e native` 20 times and compares a normalized summary. Joins the existing Python gate. | ✓ |
| B. Shell script | The same `tests/` project, with `scripts/run_native_tests.sh` looping 20 times and diffing. Simpler to read, not part of `python3 -m unittest discover`. | |
| C. PlatformIO target | The same project plus `pio run -t determinism` through an extra script. One tool, but the logic hides in SCons. | |
| Claude decides | Choose from the report and record the decision. | |

**User's choice:** A. Python test, 20 runs
**Notes:** Raw stdout is not compared; only the normalized `test_name: PASS/FAIL` summary
and counts, because timings and paths differ between runs.

---

## `ctx` and statelessness

| Option | Description | Selected |
|--------|-------------|----------|
| Allow `ctx` | Every contract carries `void *ctx`; "no state" means port owns no globals and mutates nothing, while the adapter owns the state. Multiple instances and clean test isolation; interpretation recorded in ADR-0008. | ✓ |
| Strictly no `ctx` | Adapters use file-static state; one instance per process; tests reset the global fake. | |
| `ctx` only for buses | `ctx` only where unavoidable (I2C/SPI handles, multiple UARTs); time/gpio/log use static singletons. | |

**User's choice:** Allow `ctx`

---

## `lib/host` placement

| Option | Description | Selected |
|--------|-------------|----------|
| A. Library, native only | Keep `lib/host` as a library with `library.json`; link it only from `tests/` and `[env:native]`; the checker rejects `host` in target environments. | ✓ |
| B. Under `tests/` | Move fakes to `tests/test_doubles/` as test-only code; native homework environments cannot reuse them. | |
| C. Rename | Rename `lib/host` to `lib/test_fakes`; requires updating ARCH-03, ADR-0002, and every reference. | |

**User's choice:** A. Library, native only

---

## Local gate placement

| Option | Description | Selected |
|--------|-------------|----------|
| A. Checker in pre-commit | Add a local pre-commit hook running `scripts/check_architecture.py`; the 20-run native suite stays in the Python test suite and manual runs; CI is Phase 8. | ✓ |
| B. Manual only | No hook in this phase; the checker runs manually and in the Python suite; hooks and CI land in Phase 8. | |
| C. Checker + pre-push | Checker in pre-commit plus the native suite in a new pre-push hook, pulling Phase 6 work forward. | |

**User's choice:** A. Checker in pre-commit

---

## Package metadata and versions

| Option | Description | Selected |
|--------|-------------|----------|
| A. No `dependencies` | Do not declare manifest dependencies; every project lists its full `lib_deps` explicitly (generated in Phase 5). Avoids registry resolution under `symlink://`. | ✓ |
| B. `dependencies` + duplication | Declare dependencies for the readable graph and duplicate the full list in `lib_deps` as a guard against registry fetches. | |
| C. Rely on LDF | Declare dependencies and let the Library Dependency Finder resolve them. | |

| Option | Description | Selected |
|--------|-------------|----------|
| A. `0.2.0` + remove duplicates | All five libraries bump to `0.2.0`; remove duplicated version strings from the `.c` sources so the version lives only in `library.json` (fixes WR-03). | ✓ |
| B. `0.1.0`, remove duplicates | Keep `0.1.0` until the pilot but still remove the duplicated version strings. | |
| C. Only `common`/`port` | Bump only `common` and `port` to `0.2.0`; keep adapters and `host` at `0.1.0`. | |

**User's choice:** A. No `dependencies`; A. `0.2.0` + remove duplicates
**Notes:** Research showed that with `symlink://` PlatformIO resolves a library's manifest
dependencies through the registry, so declaring them could fetch unrelated packages with
the same names.

---

## Partitions CSV location

| Option | Description | Selected |
|--------|-------------|----------|
| `partitions/` | One shared `partitions/default_16MB.csv`; `platformio.shared.ini` points to `../../partitions/default_16MB.csv`; an existence test guards it. Phase 2 review recommendation. | ✓ |
| Per-homework copy | A copy inside every homework, created by the Phase 4 scaffold. Maximum self-containment, but duplication and drift risk. | |
| `boards/` | `boards/partitions/default_16MB.csv`, grouping hardware-related data. | |

**User's choice:** `partitions/`

---

## Error and log model

| Option | Description | Selected |
|--------|-------------|----------|
| `port_status_t` + 4 levels | `enum port_status_t` (`PORT_OK`, `PORT_ERR_TIMEOUT`, `PORT_ERR_IO`, `PORT_ERR_INVALID_ARG`, `PORT_ERR_NOT_SUPPORTED`) and four log levels (`ERROR`/`WARN`/`INFO`/`DEBUG`). | ✓ |
| `int` errno + 7 levels | `int` errno-style and seven syslog levels. Familiar from POSIX but drags POSIX semantics into embedded contracts. | |
| `bool` + 3 levels | `bool`/`void` and three log levels. Minimal, loses the I2C/SPI failure cause. | |

**User's choice:** `port_status_t` + 4 levels

---

## Checker scan scope

| Option | Description | Selected |
|--------|-------------|----------|
| `lib` + `homeworks`, textual | Textual `#include` scan of `lib/**` and `homeworks/**`, layer rules plus the one-adapter rule, an empty allowlist mechanism; transitive violations are caught by the native compile gate; `tests/**` is not scanned. | ✓ |
| Scan everything | Also scan `tests/**` and `scripts/**`; stricter, but tests legitimately include `host` and frameworks, so exceptions would be needed. | |
| Preprocessor analysis | `clang -E -H` catches transitive includes, but requires clang, is slower, and complicates the deterministic native gate. | |

**User's choice:** `lib` + `homeworks`, textual

---

## C style timing

| Option | Description | Selected |
|--------|-------------|----------|
| ESP-IDF-like now | Write in the future style immediately (4 spaces, 120 columns, function brace on a new line, `port_`/`common_` prefixes); Phase 6 only adds clang-format and verifies. | |
| Defer to Phase 6 | Write consistently now; formatting and a single mass reformat land in Phase 6. | ✓ |
| Pull clang-format forward | Move the clang-format configuration from Phase 6 into this phase and format immediately; expands the phase scope. | |

**User's choice:** Defer to Phase 6

---

## Claude's Discretion

- Exact signatures, field names, and header layout of the five contracts.
- Whether `lib/port` is header-only or ships a small `.c` for inline helpers.
- Internal `tests/` layout and whether `test_framework = unity` stays local to `tests/`.
- The normalized summary format for the 20-run comparison.
- The internal implementation shape of `check_architecture.py` and the allowlist format.

## Deferred Ideas

- I2C and SPI framework adapters — first homework that needs them.
- `fixed_point`, generic state machine, calculations — after real duplication.
- CI wiring for the architecture check and native suite — Phase 8.
- Generated `platformio.shared.ini` and drift check — Phase 5.
- Pre-push hooks — Phase 6.
- clang-format and the mass reformat — Phase 6.
- Nested `lib/AGENTS.md` — only on genuine divergence.
- Police-flasher logic — Phase 11, inside the homework.

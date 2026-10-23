---
phase: 02-toolchain-truth
plan: 01
subsystem: infra
tags: [platformio, espressif32, symlink-libs, library-json, extern-c, compiledb, scons]

# Dependency graph
requires:
  - phase: 01-repository-foundation-and-policy-gate
    provides: ".gitignore coverage for compile_commands.json/.pio, stdlib unittest convention, committed-policy-as-data pattern"
provides:
  - "platformio.shared.ini with [esp32s3_arduino], [esp32s3_espidf], [native_unity]"
  - "five shared libraries (common, port, arduino, espidf, host) with library.json and extern \"C\" headers"
  - "homeworks/0_0-toolchain-smoke reference project wired through symlink:// lib_deps"
  - "scripts/pio/compiledb.py SCons hook and its data-level contract test"
affects: [02-03, 02-04, 03-shared-core, 05-metadata-generators]

actuals:
  tokens: 3365
  tasks: 2
  commits: 2

tech-stack:
  added: [PlatformIO Core 6.2.0, platformio/espressif32 8.0.0, platform-native 1.2.1, SCons 4.11.1]
  patterns:
    - "Named template sections + extends: a project env carries only extends and lib_deps"
    - "Shared libraries are consumed as lib_deps = <name>=symlink://../../lib/<name>, version declared once in library.json"
    - "One .cpp entry point with ARDUINO / ESP_PLATFORM / host branches; library sources stay pure C behind extern \"C\" headers"
    - "The SCons hook is verified as data (ast.parse + contract strings), never imported"

key-files:
  created:
    - platformio.shared.ini
    - scripts/pio/compiledb.py
    - scripts/tests/test_pio_scripts.py
    - lib/common/library.json
    - lib/common/include/common.h
    - lib/common/src/common.c
    - lib/port/library.json
    - lib/port/include/port.h
    - lib/port/src/port.c
    - lib/arduino/library.json
    - lib/arduino/include/arduino_adapter.h
    - lib/arduino/src/arduino_adapter.c
    - lib/espidf/library.json
    - lib/espidf/include/espidf_adapter.h
    - lib/espidf/src/espidf_adapter.c
    - lib/host/library.json
    - lib/host/include/host.h
    - lib/host/src/host.c
    - homeworks/0_0-toolchain-smoke/platformio.ini
    - homeworks/0_0-toolchain-smoke/src/main.cpp
    - homeworks/0_0-toolchain-smoke/README.md
  modified:
    - platformio.shared.ini

key-decisions:
  - "`-std=c11` stays in [native_unity] and is documented in an ini comment, because SCons 4.11.1 routes -std= by language (Environment.py:1176-1181) and never hands it to the .cpp entry point."

patterns-established:
  - "Config as committed data: platformio.shared.ini is hand-authored (D-02/D-04); the generator is Phase 5."
  - "Proof through the tool, not the config: the CDB contents and the build log are asserted, never the ini text."
  - "Test a build hook as data: Import(\"env\") makes the SCons script unimportable outside SCons."

requirements-completed: [ARCH-04, FOUND-09]

coverage:
  - id: D1
    description: "Shared configuration file with exactly three named sections, the espressif32@8.0.0 pin, the six N16R8 overrides and -DBOARD_HAS_PSRAM"
    requirement: FOUND-09
    verification:
      - kind: unit
        ref: "scripts/tests/test_pio_scripts.py#test_shared_ini_pins_and_overrides"
        status: pass
      - kind: unit
        ref: "scripts/tests/test_pio_scripts.py#test_shared_ini_has_exactly_three_named_sections"
        status: pass
    human_judgment: false
  - id: D2
    description: "Five library manifests and pure-C sources behind extern \"C\" headers"
    requirement: ARCH-04
    verification:
      - kind: unit
        ref: "scripts/tests/test_pio_scripts.py#test_library_manifests_agree_with_directories"
        status: pass
      - kind: unit
        ref: "scripts/tests/test_pio_scripts.py#test_entry_point_is_cpp_and_library_sources_are_c"
        status: pass
    human_judgment: false
  - id: D3
    description: "Green native build resolving three symlinked libraries (Found 3 compatible libraries, graph names common/port/host)"
    requirement: ARCH-04
    verification:
      - kind: integration
        ref: "pio run -d homeworks/0_0-toolchain-smoke -e native"
        status: pass
    human_judgment: false
  - id: D4
    description: "SCons compiledb hook wired into all three sections, setting only COMPILATIONDB_PATH; native CDB contains the three shared sources and src/main.cpp"
    requirement: ARCH-04
    verification:
      - kind: unit
        ref: "scripts/tests/test_pio_scripts.py#test_compiledb_script_contract_strings"
        status: pass
      - kind: unit
        ref: "scripts/tests/test_pio_scripts.py#test_shared_ini_wires_the_hook_in_all_three_sections"
        status: pass
      - kind: integration
        ref: "pio run -d homeworks/0_0-toolchain-smoke -t compiledb -e native"
        status: pass
    human_judgment: false
  - id: D5
    description: "Smoke project README states in English that the project is temporary, is not coursework and names the two expected Xtensa toolchains"
    verification: []
    human_judgment: true
    rationale: "Prose adequacy is not asserted by any test; a reviewer must confirm the wording prevents the project being read as the first homework."

duration: 4 min
completed: 2026-10-23
status: complete
plan_head_before: 8ea7880d473a64831fe019085cf41e6be665769f
plan_head_after: a4e7ff718a6811a53702b71b5a2822b44a939bc7
commits: 2
---

# Phase 02 Plan 01: Toolchain Truth — Shared Config, Libraries and Native Slice Summary

**Hand-authored shared PlatformIO config plus five symlink-resolved C libraries produce a green native build (`Found 3 compatible libraries`) and a 4-entry compilation database naming all three shared sources and the entry point.**

## Performance

- **Duration:** ~4 min
- **Started:** 2026-10-23T19:46:17Z (base commit 8ea7880 anchored the plan)
- **Completed:** 2026-10-23T19:50:19Z
- **Tasks:** 2
- **Files modified:** 21 created/modified (441 insertions)

## Accomplishments

- `platformio.shared.ini` declares exactly `[esp32s3_arduino]`, `[esp32s3_espidf]` and `[native_unity]`, pins `platform = espressif32@8.0.0`, carries the six D-14 N16R8 overrides, `-DBOARD_HAS_PSRAM`, and the `pre:../../scripts/pio/compiledb.py` hook in every section.
- Five libraries ship `library.json` (`name`/`version` 0.1.0/`build.srcDir`/`build.includeDir`), a guarded public header and a pure-C source; the two adapters include their framework header and call one real API.
- `homeworks/0_0-toolchain-smoke/` builds native with `lib_deps = <name>=symlink://../../lib/<name>` and no toolchain download.
- `scripts/pio/compiledb.py` sets exactly one SCons key, and 11 data-level tests pin the script, the shared-config contract and the shipped tree.

## Measured evidence

Native build (`pio run -d homeworks/0_0-toolchain-smoke -e native`):

```text
LDF: Library Dependency Finder -> https://bit.ly/configure-pio-ldf
LDF Modes: Finder ~ chain, Compatibility ~ soft
Found 3 compatible libraries
Scanning dependencies...
Dependency Graph
|-- common @ 0.1.0
|-- port @ 0.1.0
|-- host @ 0.1.0
========================= [SUCCESS] Took 0.32 seconds =========================
```

- **Native flag list:** `['-std=c11', '-Wall', '-Wextra']` (parsed from `[native_unity].build_flags`).
- **Language-mismatch diagnostics (`valid for C/ObjC but not for C++`):** 0 in the captured build log.
- **Native CDB:** 4 entries — `lib/common/src/common.c`, `lib/port/src/port.c`, `lib/host/src/host.c`, `src/main.cpp`.
- **Scoping warnings on the `compiledb` run:** 0 (`is scoping` absent from the log).
- **Repository suite:** `python3 -m unittest discover -s scripts/tests -v` → 121 tests OK; `check_policy.py --check` and `check_pr_templates.py` pass.

## Task Commits

Each task was committed atomically:

1. **Task 1: End-to-end slice — shared config, five libraries, green native build** — `0e63ce9` (feat)
2. **Task 2: SCons compiledb hook, its data-level test, and the shared-config contract test** — `a4e7ff7` (feat)

**Plan metadata:** committed separately as `docs(02-01): complete ...` (this file).

_Note: the test was written first and observed red (11 tests, 1 failure + 7 errors on the missing script and missing `extra_scripts`) before the hook landed; it is green with 11 tests after._

## Files Created/Modified

- `platformio.shared.ini` — three named template sections, exact pins, D-14 overrides, `-DBOARD_HAS_PSRAM`, `extra_scripts` in all three sections
- `scripts/pio/compiledb.py` — SCons pre-script; one `env.Replace(COMPILATIONDB_PATH=...)` under `$PROJECT_DIR`
- `scripts/tests/test_pio_scripts.py` — 11 tests covering the hook as data, the ini contract, the manifests and the entry-point shape
- `lib/{common,port,arduino,espidf,host}/library.json` — manifests; version lives only here
- `lib/*/include/*.h` — `#pragma once` plus `#ifdef __cplusplus / extern "C"` guards; no framework includes
- `lib/*/src/*.c` — one trivial symbol per library; adapters call `millis()` and `esp_err_to_name(ESP_OK)`
- `homeworks/0_0-toolchain-smoke/platformio.ini` — `[platformio]` + `[env:native]` (`extends`, `lib_deps`) only
- `homeworks/0_0-toolchain-smoke/src/main.cpp` — `ARDUINO` / `ESP_PLATFORM` / host branches
- `homeworks/0_0-toolchain-smoke/README.md` — temporary-and-not-coursework notice, toolchain note

## Decisions Made

- Restored `-std=c11` in `[native_unity]` per the research refresh and documented the SCons language routing in an ini comment instead of moving the flag into a per-project override.
- Kept `[env:*]` minimal (`extends` + `lib_deps`) so the no-merge semantics of `extends` can never silently drop template flags.
- Verified the SCons hook as data (`ast.parse` + contract strings) rather than importing it, since `Import("env")` is undefined outside SCons.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Resolved a plan-text ambiguity in test (k) source naming**
- **Found during:** Task 2 (test authoring)
- **Issue:** Task 2 item (k) asks for "each of the five `lib/<name>/src/<name>.c` files", but the plan's own `files_modified` list and Task 1 step 4 name the adapter sources `arduino_adapter.c` and `espidf_adapter.c`. A literal `<name>.c` assertion would fail on the two adapters.
- **Fix:** Encoded an explicit `LIB_SOURCES` mapping in the test (`common.c`, `port.c`, `arduino_adapter.c`, `espidf_adapter.c`, `host.c`) with a comment, honouring the authoritative file list without changing any shipped file.
- **Files modified:** `scripts/tests/test_pio_scripts.py`
- **Verification:** `test_entry_point_is_cpp_and_library_sources_are_c` passes; the five sources are present on disk.
- **Committed in:** `a4e7ff7` (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** No scope change and no file rename; only the test's path construction was corrected to match the plan's declared file set.

## Issues Encountered

None. The native build was green on the first run (0.63 s cold), required no toolchain download, and emitted zero language-mismatch warnings.

## User Setup Required

None - no external service configuration required.

## Known Stubs

None. The version strings returned by the five accessors are deliberate linkage fixtures, not stubs: `library.json` remains the single authoritative version declaration (D-12).

## Next Phase Readiness

- The `symlink://` wiring and the five manifests are proven, so plans 02-03/02-04 can add the Arduino and ESP-IDF environments without re-litigating the library layout.
- The `extra_scripts` hook now fires for every project that consumes the shared config; the ESP sections carry it but have not been exercised yet (that evidence belongs to the ESP plans).
- Deferred, by design: generation of `platformio.shared.ini` (Phase 5), deletion of `homeworks/0_0-toolchain-smoke/` (Phase 3), and `test_framework`/Unity (Phase 3).

## Self-Check: PASSED

- All 21 files listed above exist on disk (`platformio.shared.ini`, `scripts/pio/compiledb.py`, `scripts/tests/test_pio_scripts.py`, 15 `lib/` files, 3 smoke-project files, 1 modified ini).
- Commits `0e63ce9` and `a4e7ff7` are ancestors of HEAD; `commits: 2` measured with `git rev-list --count 8ea7880..HEAD`.
- Verification re-run at close-out: native build green, 11/11 new tests pass, full suite 121 tests OK, CDB carries 4 entries with no scoping warning.

---
*Phase: 02-toolchain-truth*
*Completed: 2026-10-23*

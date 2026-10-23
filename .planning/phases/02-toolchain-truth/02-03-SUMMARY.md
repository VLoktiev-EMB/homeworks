---
phase: 02-toolchain-truth
plan: 03
subsystem: infra
tags: [platformio, espressif32, arduino, esp32s3, n16r8, psram, compiledb, esptool]

# Dependency graph
requires:
  - phase: 02-toolchain-truth
    plan: 01
    provides: "platformio.shared.ini [esp32s3_arduino] with the espressif32@8.0.0 pin, the six D-14 N16R8 overrides and -DBOARD_HAS_PSRAM; five symlink-resolved libraries; the compiledb SCons hook"
provides:
  - "[env:esp32s3_arduino] in the smoke project, carrying only extends and lib_deps"
  - "A green Arduino build on PlatformIO Core 6.2.0 / platformio/espressif32 8.0.0"
  - "Artifact-level proof of 16 MB flash (esptool image-info) and octal PSRAM (qio_opi tokens plus a preprocessed CONFIG_SPIRAM 1)"
  - "Artifact-level proof that the shared libraries and the adapter compile into the Arduino build (ARCH-04)"
affects: [02-04, 03-shared-core, 08-ci]

actuals:
  tokens: 138
  tasks: 2
  commits: 1

tech-stack:
  added: []
  patterns:
    - "Per-record CDB assertion: compare each token's count with the record count, never with a fixed baseline"
    - "Prove a build flag by preprocessing the recorded compile command and grepping the macro"
    - "Read pio pkg exec output by content, because a package banner precedes the tool output on stdout"

key-files:
  created: []
  modified:
    - homeworks/0_0-toolchain-smoke/platformio.ini

key-decisions:
  - "Kept [env:esp32s3_arduino] to exactly extends and lib_deps, because extends replaces list options and any local build_flags would erase -DBOARD_HAS_PSRAM (P9, D-22)"
  - "Took every configuration conclusion from artifacts (CDB tokens, preprocessed macro, esptool image header), never from platformio.ini or the -DARDUINO_BOARD display string (P10)"
  - "Asserted token coverage as count == record count (64/64) rather than against the research baseline of 64 records, because the total is environment-dependent"

patterns-established:
  - "Equality-with-record-count assertion for configuration tokens in a compilation database"
  - "Preprocessor evidence for a define that a framework header can erase per translation unit (P5)"

requirements-completed: [FOUND-09, ARCH-04]

coverage:
  - id: D1
    description: "The Arduino environment composes from the shared template without losing flags, and builds green on the pinned toolchain"
    requirement: FOUND-09
    verification:
      - kind: unit
        ref: "python3 configparser assertion over [env:esp32s3_arduino] -> keys == {extends, lib_deps}"
        status: pass
      - kind: integration
        ref: "pio run -d homeworks/0_0-toolchain-smoke -e esp32s3_arduino -> [SUCCESS], arduino @ 0.1.0"
        status: pass
      - kind: integration
        ref: "pio project config --json-output -> memory_type=qio_opi, build_flags contains -DBOARD_HAS_PSRAM"
        status: pass
    human_judgment: false
  - id: D2
    description: "The Arduino image carries a 16 MB flash-size header"
    requirement: FOUND-09
    verification:
      - kind: integration
        ref: "pio pkg exec -p tool-esptool -- esptool --chip esp32s3 image-info .pio/build/esp32s3_arduino/firmware.bin -> 'Flash size: 16MB'"
        status: pass
    human_judgment: false
  - id: D3
    description: "The octal-PSRAM configuration reaches user code, not just the command line"
    requirement: FOUND-09
    verification:
      - kind: integration
        ref: "preprocess src/main.cpp with the recorded CDB command -> '#define CONFIG_SPIRAM 1'"
        status: pass
    human_judgment: false
  - id: D4
    description: "Every Arduino CDB record carries qio_opi/include, ARDUINO_PARTITION_default_16MB and BOARD_HAS_PSRAM, and the three shared sources plus the entry point are compiled"
    requirement: ARCH-04
    verification:
      - kind: integration
        ref: "python3 assertion over compile_commands.json after -t compiledb -e esp32s3_arduino -> 64/64 for each token, four sources present"
        status: pass
    human_judgment: false
  - id: D5
    description: "No generated artifact (CDB, firmware.bin, .pio) enters git"
    requirement: FOUND-09
    verification:
      - kind: manual_procedural
        ref: "git ls-files -ci --exclude-standard -- compile_commands.json 'homeworks/*/sdkconfig.*' -> empty; git check-ignore confirms both paths ignored"
        status: pass
    human_judgment: false

duration: ~1 min
completed: 2026-10-23
status: complete
plan_head_before: 5297b2a2f3683da06cb91f7766059b09ad5265c0
plan_head_after: c908e68ecc5073a88d0189aeacd1300186e87a9d
commits: 1
---

# Phase 02 Plan 03: Arduino ESP32-S3 (N16R8) Build and Artifact Evidence Summary

**The smoke project's new `esp32s3_arduino` environment builds green on PlatformIO Core 6.2.0 and `platformio/espressif32` 8.0.0, and the artifacts prove 16 MB flash, a preprocessed `CONFIG_SPIRAM 1`, and 64/64 CDB coverage of the octal-PSRAM tokens and all three shared sources.**

## Performance

- **Duration:** ~1 min (build 6.43 s warm; the platform and toolchain were already installed)
- **Started:** 2026-10-23T19:52:53Z
- **Completed:** 2026-10-23T19:53:46Z
- **Tasks:** 2/2 (Task 2 is evidence-only and changed no tracked file)
- **Files modified:** 1

## Accomplishments

- `[env:esp32s3_arduino]` added with exactly `extends = esp32s3_arduino` and three `lib_deps` entries (`common`, `port`, `arduino`) as `symlink://` sources with no versions (D-12, D-13, P9).
- Green build: `Found 47 compatible libraries`, graph names `common @ 0.1.0`, `port @ 0.1.0`, `arduino @ 0.1.0`; no warnings and no errors in the captured log.
- The resolved composition still inherits `board_build.arduino.memory_type = qio_opi` and `build_flags = ['-Wall', '-Wextra', '-Werror=return-type', '-DBOARD_HAS_PSRAM']` — a composition check only, not flash/PSRAM evidence.
- Artifact evidence for criteria 1, 2 and 4: 16 MB in the image header, `CONFIG_SPIRAM 1` after preprocessing, and all-record CDB token coverage.

## Measured evidence

**Toolchain pins (FOUND-09):**

```text
$ pio --version
PlatformIO Core, version 6.2.0

$ pio pkg show platformio/espressif32
Platform • 8.0.0 • Public • Published on Mon Oct 19 10:06:19 2026
```

**Arduino build:**

```text
Found 47 compatible libraries
|-- common @ 0.1.0
|-- port @ 0.1.0
|-- arduino @ 0.1.0
========================= [SUCCESS] Took 6.43 seconds =========================
esp32s3_arduino  SUCCESS   00:00:06.434
```

**Compilation database (after `pio run -t compiledb -e esp32s3_arduino`; the file is overwritten by any later `compiledb` run, P8):**

```text
entries=64 missing=[] counts={'qio_opi/include': 64, 'ARDUINO_PARTITION_default_16MB': 64, 'BOARD_HAS_PSRAM': 64}
```

- Record count: **64**. Each token count equals the record count; no baseline total was assumed.
- Sources present: `lib/common/src/common.c`, `lib/port/src/port.c`, `lib/arduino/src/arduino_adapter.c`, `src/main.cpp`.

**Preprocessed entry point (P5, D-22):**

```text
rc=0 CONFIG_SPIRAM=True
```

The exact Arduino compile command recorded in the CDB was run with `-E -dM` (dependency and output options stripped) from the entry's `directory`; the dump contains `#define CONFIG_SPIRAM 1`, so the octal-PSRAM configuration reaches user code and not merely the linker.

**Image header (P11):**

```text
Using tool-esptool@2.50400.0 package
esptool v5.4.0
...
Flash size: 16MB
Flash freq: 80m
Flash mode: DIO
```

`Flash mode: DIO` is expected PlatformIO behaviour — `qio` is converted to `dio` for the image header — and is not a defect. The `Using tool-esptool@…` banner is matched by content, never by line position.

**Board display string (recorded, deliberately not evidence — P10):**

```text
-DARDUINO_BOARD="Espressif ESP32-S3-DevKitC-1-N8 (8 MB QD, No PSRAM)"
```

The stock display name survives the overrides, so it disproves nothing. No acceptance item in this plan is derived from it or from `platformio.ini`.

**Compiler diagnostics deliberately retained:** none — 0 `warning:` and 0 `error:` lines in the build log.

**Generated-artifact check:**

```text
$ git ls-files -ci --exclude-standard -- compile_commands.json "homeworks/*/sdkconfig.*"
(empty)

$ git check-ignore -v homeworks/0_0-toolchain-smoke/compile_commands.json \
      homeworks/0_0-toolchain-smoke/.pio/build/esp32s3_arduino/firmware.bin
.gitignore:192:compile_commands.json  homeworks/0_0-toolchain-smoke/compile_commands.json
.gitignore:576:.pio                    homeworks/0_0-toolchain-smoke/.pio/build/esp32s3_arduino/firmware.bin
```

No log, CDB or `.bin` was committed (D-18, D-20).

## Task Commits

Each task was committed atomically:

1. **Task 1: Add the esp32s3_arduino environment and obtain a green build** — `c908e68` (feat)
2. **Task 2: Evidence-only — prove N16R8, the preprocessed PSRAM macro and the Arduino CDB composition** — no commit (its `<files>` is "None tracked"; it reads only gitignored build output)

**Plan metadata:** committed separately as `docs(02-03): complete Arduino N16R8 evidence plan`.

## Files Created/Modified

- `homeworks/0_0-toolchain-smoke/platformio.ini` — new `[env:esp32s3_arduino]` section with `extends` and three `lib_deps` symlink entries; no `build_flags`, `extra_scripts`, `src_filter` or `platform`

## Decisions Made

- The environment section stays minimal (`extends` + `lib_deps`), so `extends`' no-merge semantics cannot silently drop the parent `-DBOARD_HAS_PSRAM` (P9).
- Evidence is artifact-only. `pio project config` was used solely to confirm composition; flash size and PSRAM were proven from `esptool image-info` and from preprocessing, as the prohibitions require.
- Token coverage was asserted as `count == len(db)` rather than against the research's 64-record run, keeping the check valid on any machine.

## Deviations from Plan

None - plan executed exactly as written.

(The evidence helper scripts used to parse the config and CDB lived under the gitignored `.pio/` tree and were deleted after use; they were never tracked.)

## Issues Encountered

None. The platform and both Xtensa toolchains were already installed, so the first Arduino build took 6.43 s and required no download. The build produced zero warnings.

## User Setup Required

None - no external service configuration required.

## Known Stubs

None. The version strings returned by the five accessors remain deliberate linkage fixtures; `library.json` is still the single authoritative version declaration (D-12).

## Next Phase Readiness

- **For plan 02-04 (ESP-IDF):** the `compiledb` hook and the `symlink://` wiring are proven for a cross-compiled environment; the next `compiledb` run will overwrite this CDB by design (P8), so ESP-IDF evidence must be asserted immediately after its own run.
- **Criteria status:** criteria 1, 2 and 4 are now proven for the Arduino framework only; the ESP-IDF half and criterion 3 remain with plans 02-04/02-05.
- **Not established here, by design:** generation of `platformio.shared.ini` (Phase 5), deletion of the smoke project and its scoped CMake ignore patterns (Phase 3), CI wiring (Phase 8).

## Self-Check: PASSED

- `homeworks/0_0-toolchain-smoke/platformio.ini` exists and contains the `[env:esp32s3_arduino]` section.
- Commit `c908e68` is an ancestor of HEAD; `commits: 1` measured as `git rev-list --count 5297b2a..c908e68` (Task 2 made no commit because it tracked no file).
- Verification re-run at close-out: build `[SUCCESS]` 6.43 s, CDB 64/64 for all three tokens with four required sources, `CONFIG_SPIRAM=True`, `Flash size: 16MB` with the esptool banner, `git ls-files -ci` empty.

---
*Phase: 02-toolchain-truth*
*Completed: 2026-10-23*

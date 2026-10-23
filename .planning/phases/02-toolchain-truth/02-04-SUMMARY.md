---
phase: 02-toolchain-truth
plan: 04
subsystem: infra
tags: [platformio, esp-idf, esp32s3, n16r8, sdkconfig, partition-table, psram, compiledb, esptool]

# Dependency graph
requires:
  - phase: 02-toolchain-truth
    plan: 01
    provides: "platformio.shared.ini [esp32s3_espidf] with the espressif32@8.0.0 pin, board_build.partitions, and the compiledb SCons hook; five symlink-resolved libraries"
  - phase: 02-toolchain-truth
    plan: 02
    provides: "Scoped .gitignore patterns for CMakeLists.txt, src/CMakeLists.txt and sdkconfig.<env>, plus !homeworks/*/sdkconfig.defaults"
  - phase: 02-toolchain-truth
    plan: 03
    provides: "The Arduino half of criterion 2/4 and the esptool-wrapper reading pattern (P11)"
provides:
  - "A project-local default_16MB.csv that makes the ESP-IDF partition-table lookup resolve"
  - "sdkconfig.defaults with 16 MB flash and octal PSRAM Kconfig keys"
  - "[env:esp32s3_espidf] in the smoke project, carrying only extends and lib_deps"
  - "A green ESP-IDF build on PlatformIO Core 6.2.0 / platformio/espressif32 8.0.0"
  - "Artifact-level proof of 16 MB flash and octal PSRAM from sdkconfig.json and the image header"
  - "Artifact-level proof that the shared libraries and the entry point compile with -DESP_PLATFORM in every CDB record"
affects: [03-shared-core, 08-ci, 10-report-evidence]

actuals:
  tokens: 137
  tasks: 2
  commits: 1

tech-stack:
  added: []
  patterns:
    - "ESP-IDF configuration evidence is read from the generated sdkconfig.json and the image header, never from the build banner"
    - "Per-record CDB assertion: token count must equal the record count, never a fixed baseline"
    - "Project artifacts (partition CSV, sdkconfig.defaults) are authored source, not overrides in platformio.ini"

key-files:
  created:
    - homeworks/0_0-toolchain-smoke/default_16MB.csv
    - homeworks/0_0-toolchain-smoke/sdkconfig.defaults
  modified:
    - homeworks/0_0-toolchain-smoke/platformio.ini

key-decisions:
  - "Shipped default_16MB.csv in the project root because framework-espidf/components/partition_table/ has no such file and the builder aborts (P3)"
  - "Configured flash and PSRAM through sdkconfig.defaults, because an IDF -D in build_flags never reaches Kconfig (P4)"
  - "Kept [env:esp32s3_espidf] to exactly extends and lib_deps so the inherited board_build.partitions = default_16MB.csv stays literal (D-14, P9)"
  - "Asserted -DESP_PLATFORM coverage as count == len(db) (1074/1074) rather than against the research baseline of 1070, because the total is environment-dependent"

patterns-established:
  - "A mandatory ESP-IDF project artifact is committed source, not another board override"
  - "Equality-with-record-count assertion for configuration tokens in a compilation database"
  - "Read pio pkg exec output by content, because a package banner precedes the tool output on stdout"

requirements-completed: [FOUND-09, ARCH-04]

coverage:
  - id: D1
    description: "The ESP-IDF environment composes from the shared template without losing board_build.partitions and builds green with the shared libraries"
    requirement: FOUND-09
    verification:
      - kind: unit
        ref: "python3 configparser assertion over [env:esp32s3_espidf] -> keys == {extends, lib_deps}"
        status: pass
      - kind: integration
        ref: "pio run -d homeworks/0_0-toolchain-smoke -e esp32s3_espidf -> [SUCCESS] 34.05 s, espidf @ 0.1.0, Found 3 compatible libraries"
        status: pass
    human_judgment: false
  - id: D2
    description: "The effective Kconfig enables 16 MB flash and octal PSRAM"
    requirement: FOUND-09
    verification:
      - kind: integration
        ref: "python3 assertion over .pio/build/esp32s3_espidf/config/sdkconfig.json -> FLASHSIZE=16MB, FLASHSIZE_16MB, SPIRAM, SPIRAM_MODE_OCT true; SPIRAM_MODE_QUAD false"
        status: pass
    human_judgment: false
  - id: D3
    description: "The ESP-IDF image header reports a 16 MB flash size"
    requirement: FOUND-09
    verification:
      - kind: integration
        ref: "pio pkg exec -p tool-esptool -- esptool --chip esp32s3 image-info .pio/build/esp32s3_espidf/firmware.bin -> 'Flash size: 16MB' + 'Using tool-esptool@2.50400.0 package'"
        status: pass
    human_judgment: false
  - id: D4
    description: "The ESP-IDF CDB compiles the three shared sources and the entry point under the ESP-IDF branch"
    requirement: ARCH-04
    verification:
      - kind: integration
        ref: "pio run -t compiledb -e esp32s3_espidf + python3 assertion -> 1074 entries, four sources present once each, -DESP_PLATFORM 1074/1074"
        status: pass
    human_judgment: false
  - id: D5
    description: "The two mandatory project artifacts remove both known causes of failure, and generated files stay untracked"
    requirement: FOUND-09
    verification:
      - kind: manual_procedural
        ref: "build log contains neither 'Missing partition table file' nor 'Expected 16MB, found 2MB'"
        status: pass
      - kind: manual_procedural
        ref: "git check-ignore -q returns 0 for CMakeLists.txt, src/CMakeLists.txt and sdkconfig.esp32s3_espidf, and 1 for sdkconfig.defaults; git ls-files -ci is empty"
        status: pass
    human_judgment: false

duration: 2 min
completed: 2026-10-23
status: complete
plan_head_before: 6c924f21f736e90f511667047ac5e77be80557bd
plan_head_after: 4b3d12d08321c34a94112ba99a575cfb6c23bd80
commits: 1
---

# Phase 02 Plan 04: ESP-IDF ESP32-S3 (N16R8) Build and Artifact Evidence Summary

**The smoke project's new `esp32s3_espidf` environment builds green in 34.05 s on PlatformIO Core 6.2.0 and `platformio/espressif32` 8.0.0, and the artifacts prove 16 MB flash, `SPIRAM_MODE_OCT` in `sdkconfig.json`, `Flash size: 16MB` in the image header, and 1074/1074 `-DESP_PLATFORM` CDB records covering all three shared sources.**

## Performance

- **Duration:** ~2 min (build 34.05 s cold for the IDF image; the platform was already installed and the framework/toolchain were present)
- **Started:** 2026-10-23T19:54:20Z
- **Completed:** 2026-10-23T19:56:23Z
- **Tasks:** 2/2 (Task 2 is evidence-only and changed no tracked file)
- **Files modified:** 3

## Accomplishments

- `homeworks/0_0-toolchain-smoke/default_16MB.csv` ships the framework's own 16 MB layout (`nvs`, `otadata`, `app0`, `app1`, `spiffs`, `coredump`), so the IDF builder resolves `board_build.partitions = default_16MB.csv` from the project tree instead of aborting on a missing partition-table file (P3).
- `homeworks/0_0-toolchain-smoke/sdkconfig.defaults` carries exactly the three Kconfig keys (`CONFIG_ESPTOOLPY_FLASHSIZE_16MB=y`, `CONFIG_SPIRAM=y`, `CONFIG_SPIRAM_MODE_OCT=y`), so the effective configuration is 16 MB with octal PSRAM rather than the silently-green 2 MB default (P4).
- `[env:esp32s3_espidf]` added with exactly `extends` and `lib_deps` (`common`, `port`, `espidf` via `symlink://`), leaving every D-14 key inherited from the shared config (D-13, D-14, P9).
- Green build: `Found 3 compatible libraries`, graph names `common @ 0.1.0`, `port @ 0.1.0`, `espidf @ 0.1.0`; no warnings, no errors, no missing-partition or flash-size-mismatch lines.

## Measured evidence

**Toolchain pins (FOUND-09):**

```text
$ pio --version
PlatformIO Core, version 6.2.0

$ pio pkg show platformio/espressif32
Platform • 8.0.0 • Public • Published on Mon Oct 19 10:06:19 2026
```

**ESP-IDF build:**

```text
Found 3 compatible libraries
|-- common @ 0.1.0
|-- port @ 0.1.0
|-- espidf @ 0.1.0
Linking .pio/build/esp32s3_espidf/firmware.elf
Building .pio/build/esp32s3_espidf/firmware.bin
========================= [SUCCESS] Took 34.05 seconds =========================
esp32s3_espidf  SUCCESS   00:00:34.047
```

Log checks: `[SUCCESS]` present (1); `espidf @ 0.1.0` present (line 34); `Missing partition table file` 0 occurrences; `Expected 16MB, found 2MB` 0 occurrences; `undefined reference` 0 occurrences.

**Effective Kconfig (`sdkconfig.json`), the criterion-2 proof:**

```text
FLASHSIZE='16MB' FLASHSIZE_16MB=True SPIRAM=True SPIRAM_MODE_OCT=True SPIRAM_MODE_QUAD=False IDF_TARGET='esp32s3' PARTITION_TABLE_OFFSET=32768
```

Context values recorded as required: `IDF_TARGET = 'esp32s3'`, `PARTITION_TABLE_OFFSET = 32768`.

**Image header (P11 — matched by content, never by line position):**

```text
Using tool-esptool@2.50400.0 package
...
Flash size: 16MB
```

The banner is line 1 and the flash-size line is line 10 of the captured output; both are asserted by content.

**Compilation database (after `pio run -t compiledb -e esp32s3_espidf`; asserted immediately because the file is overwritten by any later run, P8):**

```text
entries=1074 missing=[] DESP_PLATFORM=1074 libs=common, espidf, port
lib/common/src/common.c            -> 1 record
lib/port/src/port.c                -> 1 record
lib/espidf/src/espidf_adapter.c    -> 1 record
src/main.cpp                       -> 1 record
```

`-DESP_PLATFORM` appears in every one of the 1074 records, which proves the ESP-IDF branch of the entry point compiled rather than the Arduino or host branch. The record total is environment-dependent and is not compared with the research baseline of 1070. The `compiledb` run printed zero `is scoping` warnings (the hook does not set `COMPILATIONDB_INCLUDE_TOOLCHAIN`).

**Generated-file hygiene (D-23):**

```text
$ git check-ignore -q homeworks/0_0-toolchain-smoke/CMakeLists.txt            -> 0
$ git check-ignore -q homeworks/0_0-toolchain-smoke/src/CMakeLists.txt        -> 0
$ git check-ignore -q homeworks/0_0-toolchain-smoke/sdkconfig.esp32s3_espidf  -> 0
$ git check-ignore -q homeworks/0_0-toolchain-smoke/sdkconfig.defaults        -> 1
$ git ls-files -ci --exclude-standard -- 'homeworks/*/CMakeLists.txt' 'homeworks/*/src/CMakeLists.txt' 'homeworks/*/sdkconfig.*'
(empty)
```

The three build-written files are ignored and untracked; the authored `sdkconfig.defaults` remains visible and was committed with a plain `git add`. No log, CDB, `sdkconfig.<env>`, `CMakeLists.txt` or `.bin` was committed (D-18, D-20, D-23).

## Task Commits

Each task was committed atomically:

1. **Task 1: ESP-IDF project artifacts and a green esp32s3_espidf environment** — `4b3d12d` (feat)
2. **Task 2: Evidence-only — prove 16 MB / octal PSRAM, the image header and the CDB composition** — no commit (its `<files>` is "None tracked"; it reads only gitignored build output)

**Plan metadata:** committed separately as `docs(02-04): complete ESP-IDF evidence plan` (this file).

## Files Created/Modified

- `homeworks/0_0-toolchain-smoke/default_16MB.csv` — six-partition 16 MB table copied from the Arduino core's own layout; sits in the project root so the IDF lookup resolves
- `homeworks/0_0-toolchain-smoke/sdkconfig.defaults` — the three Kconfig keys for 16 MB flash and octal PSRAM
- `homeworks/0_0-toolchain-smoke/platformio.ini` — new `[env:esp32s3_espidf]` section with `extends` and three `lib_deps` symlink entries; no `build_flags`, `extra_scripts`, `src_filter` or `platform`

## Decisions Made

- The partition CSV is a committed project artifact, not a change to `board_build.partitions`, so D-14 stays literal.
- Flash and PSRAM are configured through `sdkconfig.defaults`; a `-D` flag would never reach Kconfig, and SUCCESS alone is not evidence.
- The environment section stays minimal (`extends` + `lib_deps`), so `extends`' no-merge semantics cannot silently drop the parent partition key (P9).
- Evidence is artifact-only: `sdkconfig.json`, the image header and the CDB; the `HARDWARE: ... 16MB Flash` banner is never treated as evidence (prohibition, P4).

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None. The framework and toolchains were already present, the first ESP-IDF build took 34.05 s and produced zero warnings, and no build-generated file appeared in `git status`.

## User Setup Required

None - no external service configuration required.

## Known Stubs

None. The version strings returned by the five accessors remain deliberate linkage fixtures; `library.json` is still the single authoritative version declaration (D-12).

## Threat Flags

None — no new network endpoint, auth path, file-access pattern or schema at a trust boundary was introduced. The threat-register mitigations T-02-09 (partition CSV is committed source plus independent checks), T-02-10 (sdkconfig defaults plus sdkconfig.json and image-header assertions) and T-02-11 (scoped ignore rules re-asserted with `git check-ignore` and `git ls-files -ci`) are all implemented by this plan.

## Next Phase Readiness

- **Criteria status:** criterion 2 (16 MB + octal PSRAM) and criterion 4 (shared sources in the CDB) are now proven at artifact level for **both** frameworks; criterion 1 is green for all three environments (`native`, `esp32s3_arduino`, `esp32s3_espidf`); criterion 3 (the generated `platformio.shared.ini`) remains Phase 5 by D-03.
- **For Phase 3 (D-07):** deleting `homeworks/0_0-toolchain-smoke/` must also remove the two scoped CMake ignore patterns introduced by plan 02-02.
- **For Phase 8 (TOOL-05):** the criterion-2 and criterion-4 commands in this plan are the exact checks CI should re-run unchanged.

## Self-Check: PASSED

- `homeworks/0_0-toolchain-smoke/default_16MB.csv`, `sdkconfig.defaults` and `platformio.ini` exist with the asserted content.
- Commit `4b3d12d` is an ancestor of HEAD; `commits: 1` measured as `git rev-list --count 6c924f2..4b3d12d` (Task 2 made no commit because it tracked no file).
- Verification re-run at close-out: build `[SUCCESS]` 34.05 s, sdkconfig five-value assertion OK, `Flash size: 16MB` with the esptool banner, CDB 1074/1074 with four required sources, `git ls-files -ci` empty.

---
*Phase: 02-toolchain-truth*
*Completed: 2026-10-23*

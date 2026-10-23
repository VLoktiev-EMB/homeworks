# Phase 2: Toolchain Truth - Research

**Researched:** 2026-10-23 (refresh — supersedes the pre-amendment research file)
**Domain:** PlatformIO Core 6.2.0, `platformio/espressif32` 8.0.0, ESP32-S3-DevKitC-1 N16R8
overrides, `symlink://` shared libraries, compilation database
**Confidence:** HIGH — every mechanism this phase depends on was reproduced against the
toolchain actually installed on this machine in this session (three green builds, two
compilation databases, two `esptool image-info` runs, one linker failure per amendment).
The file is written in English as the task requires and as `AGENTS.md` requires of
repository artifacts.

---

<user_constraints>
## User Constraints (from CONTEXT.md)

> The amendments at `.planning/phases/02-toolchain-truth/02-CONTEXT.md:259-293` override
> the bullets they name. **D-15 and D-21 below are the amended text.** The pre-amendment
> wording (a `.c` entry point; ADR `0006`) is superseded and must not be planned against.
> Canonical-reference lines that still say `0006` (`02-CONTEXT.md:154`, `:179`, `:220`) are
> stale for the same reason.

### Locked Decisions

- **D-01:** There is exactly **one** shared configuration file, `platformio.shared.ini` at
  the repository root. Each project consumes it through
  `[platformio] extra_configs = ../../platformio.shared.ini` and inherits named sections
  (`[esp32s3_arduino]`, `[esp32s3_espidf]`, `[native_unity]`) with `extends`.
  — **Reversibility:** costly — moving the file later means editing `extra_configs` in
  every one of the 30+ homework projects, and a missed one builds with unpinned defaults.
- **D-02:** In Phase 2 the shared file is **written by hand and committed**. It is *not*
  generated. The generator arrives in Phase 5 (META-05).
- **D-03:** **Criterion 3 is explicitly re-read.** ROADMAP says "consumed ... from a
  generated `platformio.shared.ini`". In this phase the file is authored manually; only
  the *consumption* half of the criterion is satisfied. Phase 5 adds generation plus a
  `--check` drift gate. The planner and verifier must not claim generation happened here.
- **D-04:** `platformio.shared.ini` is **committed to git**, not gitignored. It is a
  source-of-truth configuration for a reproducible build, not a build product. The
  repository's "generated files are never committed" rule enumerates
  `compile_commands.json`, `site/`, and `.pio/`; this file is not in that list and must not
  be added to it.
- **D-05:** `.planning/research/ARCHITECTURE.md` line 220 ("`platformio.shared.ini` is
  generated per homework") is **superseded** by D-01. Downstream agents must not follow
  it. The research file stays untouched as a historical record.
- **D-06:** The reference project lives at `homeworks/0_0-toolchain-smoke/`. Its ID matches
  the repository pattern `^[0-9]+_[0-9]+-[a-z0-9-]+$`.
- **D-07:** It is **temporary**. When `tests/` and the Unity suite arrive in Phase 3, it is
  removed in a dedicated commit. Phase 3's plan must carry that deletion as an explicit
  task; otherwise a project that was never a homework silently enters the public homework
  index.
- **D-08:** It carries **no** `homework.yaml`, report, or `task.md`. Those artifacts belong
  to Phase 4 and Phase 10, and adding them here would make a throwaway build check look
  like coursework.
- **D-09:** `lib/common`, `lib/port`, `lib/arduino`, `lib/espidf`, and `lib/host` each get a
  `library.json` with `name`, `version`, `build.srcDir`, and `build.includeDir`. Every
  library starts at `0.1.0`.
- **D-10:** Each library exports **one trivial symbol** — enough to prove linking, nothing
  more. `common`'s symbol is called from the reference project's entry point so the linker
  cannot drop the library as unused.
- **D-11:** `lib/arduino` **includes `<Arduino.h>`** and calls one trivial Arduino API
  function; `lib/espidf` **includes an ESP-IDF driver header** (e.g. `<driver/gpio.h>` or
  `<esp_err.h>`) and calls one trivial API function. Without a framework header the ESP
  build proves only that the cross-compiler exists, which is not the point of the phase.
- **D-12:** Library versions are declared **only** in `library.json`. `lib_deps` entries
  carry the name and the symlink source, never a version:
  `common=symlink://../../lib/common`.
  — **Reversibility:** costly — the `lib/` directory names become the dependency-rule
  vocabulary (`common → port`, adapters → port) that Phase 3's checker enforces and every
  homework's `lib_deps` repeats.
- **D-13:** The reference project defines **both** ESP environments — `esp32s3_arduino`
  and `esp32s3_espidf` — and both must build. Success criterion 4 names both frameworks,
  so covering one leaves it unproven.
- **D-14:** The N16R8 overrides are exactly: `board_build.arduino.memory_type = qio_opi`,
  `board_build.flash_mode = qio`, `board_build.psram_type = opi`,
  `board_upload.flash_size = 16MB`, `board_upload.maximum_size = 16777216`,
  `board_build.partitions = default_16MB.csv`. The stock `esp32-s3-devkitc-1` manifest
  (8 MB, no PSRAM) is never used unmodified.
- **D-15 (amended):** The entry point is **`src/main.cpp`**, not `src/main.c`. It carries
  three thin branches: `#ifdef ARDUINO` → `setup()`/`loop()`; `#elif defined(ESP_PLATFORM)`
  → `extern "C" void app_main()`; `#else` → `int main(void)` for `native`. Reason: Arduino
  core 3.3.12 calls C++-mangled `setup`/`loop`, so a `.c` entry fails with
  `undefined reference to '_Z5setupv'`.
  **Library sources stay pure C** (`lib/*/src/*.c`), and each public header in
  `lib/*/include/` carries the standard `#ifdef __cplusplus / extern "C" {` guard so C++
  callers link against C symbols. This keeps future ESP-IDF/STM32 homework in pure C — the
  guard compiles to nothing under a C compiler.
- **D-16:** The `native` environment is proven by **`pio run -e native` only**. No
  `test_framework`, no `test/` directory, no Unity. The shared Unity suite and the
  top-level `tests/` project are Phase 3's.
- **D-17:** One shared extra script lives at `scripts/pio/compiledb.py`, wired from
  `platformio.shared.ini` as `extra_scripts = pre:../../scripts/pio/compiledb.py`. There is
  no per-project copy.
- **D-18:** The generated `compile_commands.json` stays **gitignored** (already covered by
  `.gitignore` from Phase 1, D-21). Only the producing script is committed.
- **D-19:** Build order is `native` → `esp32s3_arduino` → `esp32s3_espidf` → `compiledb`.
  The first end-to-end slice is a green native build with the symlinked libraries, which
  needs no toolchain download and proves the wiring; the riskier `espressif32@8.0.0` pin is
  exercised once the wiring is known good.
- **D-20:** The evidence of this phase is a **green `pio run` in the working session**. Build
  logs are **not** committed and not stored under `.planning/`. Committed logs age into
  false claims; the measurement and evidence contract is Phase 10's.
- **D-21 (amended):** The ADR is **`docs/decisions/0007-*.md`**. `0006-public-commit-identity.md`
  already exists and `docs/decisions/README.md` reserves 0007 for this decision. Sequential,
  permanent numbering (Phase 1 D-27) forbids reusing 0006.
- **D-22 (new):** `-DBOARD_HAS_PSRAM` is added to `build_flags` of `[esp32s3_arduino]`. It is
  a separate key, not part of the D-14 override list; without it the Arduino core may not
  initialise octal PSRAM.
- **D-23 (new):** ESP-IDF build-generated files in the project tree — `CMakeLists.txt`,
  `src/CMakeLists.txt`, and `sdkconfig.<env>` — are **added to `.gitignore`**, never
  committed. This extends, and does not weaken, the AGENTS.md "generated files are never
  committed" rule.

### Additional research findings the plan MUST carry as tasks

- P2: the ESP-IDF builder looks for `default_16MB.csv` in
  `framework-espidf/components/partition_table/`, where it does not exist. The project must
  ship its own `default_16MB.csv` (keeping D-14 literal) plus `sdkconfig.defaults` with
  `CONFIG_ESPTOOLPY_FLASHSIZE_16MB=y`, `CONFIG_SPIRAM=y`, `CONFIG_SPIRAM_MODE_OCT=y`.
- P1/P3: the three fixes (entry point, `extern "C"` guards, ESP-IDF partition/sdkconfig) must
  land **before** the first `pio run` of the affected environment, not as a later repair.
- Evidence for criteria 2 and 4 is taken from `esptool image-info` and from Python assertions
  over `compile_commands.json` / `sdkconfig.json` — never from re-reading `platformio.ini`.

### Claude's Discretion

- Exact content of each stub symbol (a version-string accessor is the natural choice).
- The internal implementation of `scripts/pio/compiledb.py`.
- Whether the smoke project's `README.md` is one line or several, provided it states the
  project is temporary and is not coursework.

### Deferred Ideas (OUT OF SCOPE)

- Generation of `platformio.shared.ini` from a board-profile source, plus a `--check` drift
  gate — Phase 5 (META-05).
- `tests/` PlatformIO project, the Unity suite, and `test_framework = unity` — Phase 3.
- Deletion of `homeworks/0_0-toolchain-smoke/` — Phase 3, as an explicit task in that
  phase's plan.
- `homework.yaml`, `task.md`, README index entries, and the report contract for the smoke
  project — not applicable; those belong to Phase 4 and Phase 10 for real homework.
- CI wiring for the builds (matrix, changed-only detection) — Phase 8.
- Fallback to `espressif32` 7.x or pioarduino if 8.0.0 fails — a contingency recorded in
  STATE.md, not a decision made in this phase.
- Architecture checker enforcing `common → port`, adapters → port — Phase 3 (ARCH-05).

</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| FOUND-09 | Toolchain is pinned: PlatformIO Core 6.2.0, `platformio/espressif32` 8.0.0, and explicit ESP32-S3-DevKitC-1 N16R8 overrides (16 MB flash, octal PSRAM). `[VERIFIED: .planning/REQUIREMENTS.md:32-34]` | Core 6.2.0 present (`pio --version` → `PlatformIO Core, version 6.2.0`); 8.0.0 resolves and is installed (`pio pkg show` → `Platform • 8.0.0`; `platform.json` → `"version": "8.0.0"`, `"engines": {"platformio": "^6"}`). Arduino and ESP-IDF builds green with D-14 + D-22. 16 MB proven from the image header and from the generated `sdkconfig.json`. See Standard Stack, Patterns 1-5, Pitfalls P1-P12. |
| ARCH-04 | Shared libraries are consumed through `lib_deps = <name>=symlink://../../lib/<name>` with a `library.json` per library and a generated `platformio.shared.ini`; `lib_extra_dirs` remains a generator fallback only. `[VERIFIED: .planning/REQUIREMENTS.md:71-74]` | `symlink://` resolution and the name alias verified in all three environments; `.pio-link` records `"uri": "symlink://../../lib/common"`; a missing manifest raises `MissingPackageManifestError`. CDBs contain all three library sources per ESP framework. See Patterns A, 6 and the CDB evidence tables. |

**Criterion 3 is read through D-03:** this phase satisfies only the *consumption* half of
ARCH-04. Generation is Phase 5 (META-05). The verifier must not require a generator here.

</phase_requirements>

---

## Summary

The pin is sound and the risk recorded in `STATE.md` ("espressif32 8.0.0 is new and must be
smoke-tested") is now discharged. On this machine, with the installed PlatformIO Core
6.2.0 and `platformio/espressif32` 8.0.0, a reference project with one `src/main.cpp`,
three shared libraries per environment and the D-14/D-22 overrides produced:

- `pio run -e native` → `[SUCCESS]`, `Found 3 compatible libraries`;
- `pio run -e esp32s3_arduino` → `[SUCCESS]` (5.70 s);
- `pio run -e esp32s3_espidf` → `[SUCCESS]` (24.73 s);
- `esptool --chip esp32s3 image-info` → `Flash size: 16MB` for **both** firmwares;
- `compile_commands.json` with 64 Arduino entries and 1070 ESP-IDF entries, each containing
  `lib/common/src/common.c`, `lib/port/src/port.c`, the matching adapter and `src/main.cpp`.

The amendments are correct and, in the cases tested, necessary:

1. **D-15 (amended) is required.** A `.c` entry does not link against Arduino core 3.3.12:
   `undefined reference to '_Z5setupv'` / `'_Z4loopv'`. A `.cpp` entry with
   `#ifdef ARDUINO` / `#elif defined(ESP_PLATFORM)` / `#else` links in all three
   environments. Pure-C library sources plus `extern "C"` guards link correctly; removing
   a guard reproduces `undefined reference to '_Z14common_versionv'`.
2. **D-21 (amended) is required.** `docs/decisions/0006-public-commit-identity.md` exists and
   `docs/decisions/README.md:31` says `Next number: **0007** (reserved for the Phase 2
   symlink decision).` The ADR is `0007-*`.
3. **D-22 is required.** Without `-DBOARD_HAS_PSRAM`, the Arduino preprocessor sees
   `CONFIG_SPIRAM_MODE_OCT 1` but **not** `CONFIG_SPIRAM`; with the flag it sees
   `CONFIG_SPIRAM 1`, `BOARD_HAS_PSRAM 1` and `CONFIG_SPIRAM_MODE_OCT 1`.
4. **D-23 addresses a real gap.** After a green ESP-IDF build the project tree contains
   `CMakeLists.txt` (118 B), `src/CMakeLists.txt` (199 B) and `sdkconfig.esp32s3_espidf`
   (94 536 B). All three are currently **visible** to `git check-ignore` in this repository;
   `.gitignore:11-12` only ignores `sdkconfig.old` / `sdkconfig.old.*`.
5. **P2 is reproduced exactly.** Removing the project-local CSV produces
   `Missing partition table file \`<abs>/homeworks/0_0-toolchain-smoke/default_16MB.csv\``;
   removing `sdkconfig.defaults` produces `Warning! Flash memory size mismatch detected.
   Expected 16MB, found 2MB!` while the build still reports `SUCCESS`.

Three corrections to the previous research and to the reviewed plans survive verification:

- **Drop `COMPILATIONDB_INCLUDE_TOOLCHAIN=True`.** With it, Core 6.2.0 prints
  `Warning! \`COMPILATIONDB_INCLUDE_TOOLCHAIN\` is scoping` four times per `compiledb` run
  (`piobuild.py:144-145`). Without it the warning count is zero and the CDB still contains
  every required source (verified: 64 / 1070 entries, same library sources). The documented
  snippet at Context7 prescribes the flag; the empirical warning and the absence of any
  need for toolchain include paths justify omitting it.
- **`-std=c11` does not reach the C++ entry point.** SCons 4.11.1 routes `-std=` by language
  (`Environment.py:1176-1181`: `++` → `CXXFLAGS`, otherwise `CFLAGS`). The recorded
  `src/main.cpp` command contains no `-std=c11`, and a clean native build emits zero
  `valid for C/ObjC but not for C++` warnings. The review concern is **refuted**; `build_src_flags`
  would not change anything (it is a project-`src`-only key, not a C-only key).
- **`pio pkg exec -p tool-esptool -- esptool` is the portable invocation.** It prints
  `Using tool-esptool@2.50400.0 package` as the first **stdout** line, then the esptool
  output; it exits `0` on success and `2` on a missing/invalid filename. Evidence scripts
  must use `grep`, never fixed line positions, and should check the file exists first.

One additional trap: after the overrides are applied the Arduino command line still carries
`-DARDUINO_BOARD="Espressif ESP32-S3-DevKitC-1-N8 (8 MB QD, No PSRAM)"`. The board **name
string** is not evidence; the image header and the CDB tokens are.

**Primary recommendation:** plan the phase around measured commands, and front-load the
three fixes into the task that first builds each environment — `src/main.cpp` + `extern "C"`
guards before the first Arduino build, `sdkconfig.defaults` + project-local `default_16MB.csv`
before the first ESP-IDF build, and `-DBOARD_HAS_PSRAM` before the first Arduino build. Prove
criteria 2 and 4 only from `esptool image-info`, `sdkconfig.json` and `compile_commands.json`.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Toolchain and platform pinning | Build config (`platformio.shared.ini`) | PlatformIO registry | `platform = espressif32@8.0.0` is the single place the version becomes a reproducibility contract. `[VERIFIED: pio project config --json-output]` |
| Environment composition | Build config (`[esp32s3_*]` + `extends`) | Project `platformio.ini` | Shared keys live in the root file; the project declares only `extends` and `lib_deps`. `[VERIFIED: pio project config --json-output]` |
| Flash size and PSRAM (Arduino) | Board build overrides (`board_build.*`, `board_upload.*`) | Arduino core precompiled kernel set (`qio_opi`) | `board_build.arduino.memory_type = qio_opi` selects the kernel directory; `-DBOARD_HAS_PSRAM` decides whether `CONFIG_SPIRAM` survives preprocessing. `[VERIFIED: CDB + `xtensa-esp32s3-elf-g++ -E -dM`]` |
| Flash size and PSRAM (ESP-IDF) | Project `sdkconfig.defaults` | ESP-IDF Kconfig → generated `sdkconfig.json` | `-D` flags in `build_flags` do not reach Kconfig; `CONFIG_ESPTOOLPY_FLASHSIZE_16MB`, `CONFIG_SPIRAM`, `CONFIG_SPIRAM_MODE_OCT` are Kconfig symbols. `[VERIFIED: .pio/build/<env>/config/sdkconfig.json]` |
| Partition table | Arduino: core `tools/partitions/`; ESP-IDF: project root | PlatformIO builder | Same ini value, two resolution locations. `[VERIFIED: builder/frameworks/espidf.py:1817-1830]` |
| Shared-library resolution | Library Dependency Finder (`lib_deps` + `library.json`) | PlatformIO package manager (`.pio/libdeps/<env>/*.pio-link`) | `symlink://` registers a link file; LDF finds the library by `#include`. `[VERIFIED: .pio-link JSON + dependency graph]` |
| Entry point | Source (`src/main.cpp`) | Framework runtime | One file, three branches; the framework decides symbol mangling, not the project. `[VERIFIED: nm on both firmwares]` |
| Build artifacts | `.pio/build/<env>/` | — | `firmware.bin`, `firmware.elf`, `partitions.bin`, `bootloader.bin`; all gitignored. `[VERIFIED: ls .pio/build/<env>]` |
| Compilation database | Build system (`compiledb` target + `extra_scripts`) | `scripts/pio/compiledb.py` | SCons assembles the DB from the build graph; the script only overrides the path. `[VERIFIED: platformio/builder/main.py:195-196]` |
| Evidence | External commands (`esptool image-info`, Python assertions) | Build artifacts | The ini states intent; only the image header, generated config and CDB state the result. |

---

## Standard Stack

### Core

| Library / tool | Version | Purpose | Why Standard |
|----------------|---------|---------|--------------|
| PlatformIO Core | **6.2.0** | Build system for every project | Already installed; FOUND-09. `[VERIFIED: pio --version → "PlatformIO Core, version 6.2.0"]` |
| `platformio/espressif32` | **8.0.0** (published 2026-10-19, Apache-2.0) | ESP32 platform | Current official platform with Arduino core 3.x and ESP-IDF 6.1. `[VERIFIED: pio pkg show platformio/espressif32 → "Platform • 8.0.0 • Public • Published on Mon Oct 19 10:06:19 2026"; platforms/espressif32/platform.json → "version": "8.0.0", "engines": {"platformio": "^6"}]` |
| `framework-arduinoespressif32` | `4.30312.261016` (Arduino core **3.3.12**, IDF 5.5.5) | Arduino framework | Pulled by platform 8.0.0. `[VERIFIED: packages/framework-arduinoespressif32/package.json → "version": "4.30312.261016"; image-info → "ESP-IDF: v5.5.5"]` |
| `framework-arduinoespressif32-esp32s3-libs` | `3.3.12` | Precompiled Arduino kernels for ESP32-S3 | Provides `qio_opi`, `qio_qspi`, `dio_opi`, `dio_qspi`, `opi_opi` variants. `[VERIFIED: package.json; directory listing]` |
| `framework-espidf` | `4.60100.0` (= ESP-IDF **6.1.0**) | ESP-IDF framework | Pulled by platform 8.0.0. `[VERIFIED: package.json → 4.60100.0; sdkconfig.json IDF version / image-info → "ESP-IDF: 6.1.0"]` |
| `toolchain-xtensa-esp-elf` | `14.2.0+20260121` (Arduino) and `15.2.0+20251204` (ESP-IDF) | Xtensa cross-compiler | Two distinct toolchains, both installed. `[VERIFIED: compile command paths; package.json in both directories]` |
| `tool-esptool` | `2.50400.0` (esptool **5.4.0**) | Flash/image inspection | Gives the `image-info` subcommand that proves the 16 MB header. `[VERIFIED: pio pkg show platformio/tool-esptool → "Tool • 2.50400.0"; esptool version → "esptool v5.4.0"]` |
| `platform-native` | `1.2.1` | Host build | No toolchain download; proves the wiring first. `[VERIFIED: platforms/native/platform.json → "version": "1.2.1"]` |

### Supporting build tools (installed by the ESP-IDF builder)

| Tool | Version | Purpose | Evidence |
|------|---------|---------|----------|
| `tool-cmake` | `3.30.2` | ESP-IDF project configuration | `[VERIFIED: packages/tool-cmake/package.json; cmake --version]` |
| `tool-ninja` | `1.13.2` | ESP-IDF build backend | `[VERIFIED: packages/tool-ninja/package.json; ninja --version]` |
| `tool-scons` | `4.41101.0` (SCons 4.11.1) | PlatformIO build engine | `[VERIFIED: packages/tool-scons/package.json; scons-local-4.11.1]` |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `espressif32@8.0.0` | `espressif32@7.1.3` (Arduino core 2.0.17) | Abandons FOUND-09 and the Arduino core 3.x API. Only if 8.0.0 proves blocked — none found in this session. |
| `espressif32@8.0.0` | pioarduino fork | Useful only for exotic C2/C61 targets; adds an unsupported dependency to a public repository. |
| `lib_deps = name=symlink://...` | `lib_extra_dirs` | Deprecated since PlatformIO 6.0; LDF would scan every library and can pull an unrelated adapter. `[CITED: https://github.com/platformio/platformio-docs/blob/develop/projectconf/sections/env/options/library/lib_extra_dirs.rst]` |
| `src/main.cpp` | `src/main.c` + shim | D-15 fixes *one* file; a shim adds a second file and does not solve the mangling problem (P1). |
| `pio pkg exec -p tool-esptool -- esptool` | `~/.platformio/packages/tool-esptool/esptool` | Hard-codes a core directory; breaks with a custom `PLATFORMIO_CORE_DIR`. |
| Project-local `sdkconfig.defaults` | `-D` flags in `build_flags` | `-D` never reaches Kconfig; the generated `sdkconfig.json` would keep the 2 MB default (P4). |

### Installation

```bash
# The platform and both toolchains are installed automatically by the first `pio run`.
# They are already present on this machine; a fresh machine downloads roughly 5.5 GB.
pio run -e native            # no download
pio run -e esp32s3_arduino   # Arduino core + s3 kernel set + Xtensa 14.2.0
pio run -e esp32s3_espidf    # ESP-IDF 6.1.0 + Xtensa 15.2.0 + cmake + ninja + scons
```

### Version verification

```bash
pio --version                        # PlatformIO Core, version 6.2.0
pio pkg show platformio/espressif32 # Platform • 8.0.0 • Public • Published on Mon Oct 19 10:06:19 2026
```

`pio pkg show` also fetches a README from `raw.githubusercontent.com`; in a network-restricted
sandbox that fetch can be denied while the version metadata above still prints. The sandbox
denial is not a registry failure.

---

## Package Legitimacy Audit

The `gsd-tools query package-legitimacy check` seam supports `npm`, `pypi` and `crates` only.
Run against PyPI for `platformio`, it returned `SUS` with **null** signals
(`exists: null`, `publishedAt: null`, `weeklyDownloads: null`, `repoUrl: null`) after
certificate-copy errors. That is an **absence of observation**, not a finding, and under the
absent-evidence rule it is not evidence about any version. It also cannot evaluate the
PlatformIO registry at all. Package identity below is therefore established from the two
authoritative sources available on this machine: the PlatformIO registry (`pio pkg show`)
and the installed packages' own manifests.

| Package | Registry | Version / Published | License | Source repo | Verdict | Disposition |
|---------|----------|---------------------|---------|-------------|---------|-------------|
| `platformio` (Core) | PyPI | 6.2.0, already installed | Apache-2.0 | github.com/platformio/platformio-core | OK | Approved (not installed by this phase) |
| `platformio/espressif32` | PlatformIO | 8.0.0, 2026-10-19 | Apache-2.0, 1210 stars | github.com/platformio/platform-espressif32 | OK | Approved |
| `platformio/framework-arduinoespressif32` | PlatformIO | 4.30312.261016, 2026-10-17 | LGPL-2.1-or-later | github.com/espressif/arduino-esp32 | OK | Approved (linked, never modified; firmware binaries are not committed) |
| `platformio/framework-arduinoespressif32-esp32s3-libs` | PlatformIO | 3.3.12 | LGPL-2.1-or-later | github.com/espressif/arduino-esp32 | OK | Approved |
| `platformio/framework-espidf` | PlatformIO | 4.60100.0 (IDF 6.1.0) | Apache-2.0 | github.com/espressif/esp-idf | OK | Approved |
| `platformio/toolchain-xtensa-esp-elf` | PlatformIO | 14.2.0+20260121 / 15.2.0+20251204 | binary toolchain | github.com/espressif/crosstool-NG | OK | Approved |
| `platformio/tool-esptool` | PlatformIO | 2.50400.0, 2026-09-23 | GPL-2.0-or-later | github.com/espressif/esptool | OK | Approved (build-time tool only; not linked into firmware or distributed) |
| `platformio/tool-cmake` | PlatformIO | 3.30.2 | Apache-2.0 | github.com/Kitware/CMake | OK | Approved |
| `platformio/tool-ninja` | PlatformIO | 1.13.2 | Apache-2.0 | github.com/ninja-build/ninja | OK | Approved |
| `platformio/tool-scons` | PlatformIO | 4.41101.0 | MIT | github.com/SCons/scons | OK | Approved |

**Packages removed due to SLOP verdict:** none.
**Packages flagged as suspicious [SUS]:** none. The seam's `SUS` verdict was an unobserved
lookup, not a slopsquat signal; no package was discovered through WebSearch or training data.

---

## Architecture Patterns

### System Architecture Diagram

```
platformio.shared.ini  (repo root, committed, hand-authored — D-02/D-04)
   ├─ [esp32s3_arduino] ── espressif32@8.0.0, D-14 overrides, D-22 flag
   ├─ [esp32s3_espidf]  ── espressif32@8.0.0, D-14 subset (partitions/flash)
   └─ [native_unity]    ── platform=native
            │
            │ extra_configs = ../../platformio.shared.ini
            ▼
homeworks/0_0-toolchain-smoke/platformio.ini
   [env:native]           extends native_unity    lib_deps: common, port, host
   [env:esp32s3_arduino]  extends esp32s3_arduino lib_deps: common, port, arduino
   [env:esp32s3_espidf]   extends esp32s3_espidf  lib_deps: common, port, espidf
            │
            ▼
   LDF ──► lib/<name>/library.json ──► .pio/libdeps/<env>/<name>.pio-link
            │                            {"uri": "symlink://../../lib/<name>"}
            ▼
   pio run -e <env> ──► .pio/build/<env>/firmware.bin
            │                    │
            │                    └─► esptool image-info ──► "Flash size: 16MB"
            │
            └─► ESP-IDF only: sdkconfig.defaults + default_16MB.csv
                     ├─► sdkconfig.<env>  (generated, project root)
                     ├─► CMakeLists.txt, src/CMakeLists.txt (generated)
                     └─► .pio/build/<env>/config/sdkconfig.json
                              (ESPTOOLPY_FLASHSIZE / SPIRAM / SPIRAM_MODE_OCT)

   pio run -t compiledb -e <env> ──► compile_commands.json (project root, gitignored)
            └─► SCons CompilationDatabase ──► every TU, including lib/<name>/src/*.c
```

The diagram shows data flow, not file layout: configuration → library resolution →
artifacts → evidence.

### Recommended Project Structure

```text
platformio.shared.ini              # repo root, committed (D-01/D-04)
scripts/pio/compiledb.py           # extra script, committed (D-17)
scripts/tests/test_pio_scripts.py  # AST-level contract test
lib/
├── common/{library.json,include/common.h,src/common.c}
├── port/{library.json,include/port.h,src/port.c}
├── arduino/{library.json,include/arduino_adapter.h,src/arduino_adapter.c}
├── espidf/{library.json,include/espidf_adapter.h,src/espidf_adapter.c}
└── host/{library.json,include/host.h,src/host.c}
homeworks/0_0-toolchain-smoke/
├── platformio.ini
├── default_16MB.csv          # ESP-IDF builder resolves this in the project root (P3)
├── sdkconfig.defaults        # ESP-IDF Kconfig defaults (P4)
├── src/main.cpp              # three branches (D-15 amended)
└── README.md
```

`CMakeLists.txt`, `src/CMakeLists.txt` and `sdkconfig.<env>` are **not** in the tree after a
clean clone; the ESP-IDF builder writes them on demand and D-23 keeps them out of git.

### Pattern A: Named sections + `extends` (verified)

**What:** the root file holds template sections without an `env:` prefix; each project
declares `[env:<name>]` with `extends = <template>` and its own `lib_deps`.

**When to use:** always, for this repository (D-01).

**Verified composition** (`pio project config --json-output`):

```text
[env:native]            extends=[native_unity],         build_flags=[-std=c11, -Wall, -Wextra]
[env:esp32s3_arduino]   extends=[esp32s3_arduino],      board=esp32-s3-devkitc-1, memory_type=qio_opi, ...
[env:esp32s3_espidf]    extends=[esp32s3_espidf],       framework=[espidf], partitions=default_16MB.csv
[esp32s3_arduino]       platform=espressif32@8.0.0,     build_flags="-Wall\n-Wextra\n-Werror=return-type\n-DBOARD_HAS_PSRAM"
```

**Semantics the planner must encode:**

- `extra_configs`: when the same group + option is declared in an extra file and the base
  file, the **extra file wins**. Because D-01 uses named template sections, not duplicated
  `[env:*]` keys, this override never fires in practice. `[CITED: https://github.com/platformio/platformio-docs/blob/develop/projectconf/sections/platformio/options/generic/extra_configs.rst]`
- `extends`: **does not merge** list values. `[CITED: https://github.com/platformio/platformio-docs/blob/develop/projectconf/sections/env/options/advanced/extends.rst]`
  Reproduced: with the parent carrying `build_flags = -DPARENT_FLAG=1` and the child
  `build_flags = -DCHILD_FLAG=1`, the child's resolved value was exactly
  `['-DCHILD_FLAG=1']` — the parent flag was gone.
- List-valued keys that are **replaced, not merged**: `build_flags`, `build_unflags`,
  `lib_deps`, `lib_extra_dirs`, `lib_ignore`, `extra_scripts`, `build_src_filter` /
  `src_filter`, `debug_init_break`.
- **Practical rule:** a project `[env:*]` contains **only** `extends` and `lib_deps`. Any
  other list-valued key in a project env is a signal that the template must change.

**Full verified `platformio.shared.ini`:**

```ini
[esp32s3_arduino]
platform = espressif32@8.0.0
board = esp32-s3-devkitc-1
framework = arduino
board_build.arduino.memory_type = qio_opi
board_build.flash_mode = qio
board_build.psram_type = opi
board_upload.flash_size = 16MB
board_upload.maximum_size = 16777216
board_build.partitions = default_16MB.csv
build_flags =
    -Wall
    -Wextra
    -Werror=return-type
    -DBOARD_HAS_PSRAM
extra_scripts = pre:../../scripts/pio/compiledb.py

[esp32s3_espidf]
platform = espressif32@8.0.0
board = esp32-s3-devkitc-1
framework = espidf
board_upload.flash_size = 16MB
board_upload.maximum_size = 16777216
board_build.partitions = default_16MB.csv
extra_scripts = pre:../../scripts/pio/compiledb.py

[native_unity]
platform = native
build_flags =
    -std=c11
    -Wall
    -Wextra
extra_scripts = pre:../../scripts/pio/compiledb.py
```

Why the ESP-IDF section carries only the flash/partition keys: `board_build.arduino.*` and
`board_build.psram_type` are read only by the Arduino builder; ESP-IDF PSRAM is a Kconfig
choice (`sdkconfig.defaults`), not a board-build key. Keeping the section honest prevents a
false belief that the ini alone configures PSRAM.

**Why `[native_unity]` has no `test_framework`:** D-16 proves `native` with `pio run -e native`
only. The name is kept so Phase 3 can add Unity without renaming. Verified: native is green
with no test framework.

### Pattern B: One entry point, three branches (D-15 amended, verified)

**What:** `src/main.cpp` with `#if defined(ARDUINO) … #elif defined(ESP_PLATFORM) … #else …`.

```cpp
#include <stdio.h>
#include "common.h"
#include "port.h"

#if defined(ARDUINO)
#include <Arduino.h>
#include "arduino_adapter.h"
void setup(void) { /* call common_version() and arduino_adapter_version() */ }
void loop(void) {}
#elif defined(ESP_PLATFORM)
#include "espidf_adapter.h"
extern "C" void app_main(void) { /* call common_version() and espidf_adapter_version() */ }
#else
#include "host.h"
int main(void) { /* call common_version(), port_version(), host_version() */ return 0; }
#endif
```

**Why each branch exists (all verified):**

| Branch | Macro evidence | Symbol evidence |
|--------|----------------|-----------------|
| Arduino | `-DARDUINO=10812` in all 64 Arduino CDB entries | `nm firmware.elf` shows `_Z5setupv`, `_Z4loopv`, and unmangled `common_version`, `arduino_adapter_version` |
| ESP-IDF | `-DESP_PLATFORM` in all 1070 ESP-IDF CDB entries; `-DARDUINO=` count is 0 | `nm firmware.elf` shows unmangled `app_main`, `common_version`, `espidf_adapter_version` |
| native | neither macro in the 4 native entries | links a host `main` |

`extern "C"` on `app_main` is mandatory: removing it fails the link with
`undefined reference to 'app_main'` referenced from
`framework-espidf/components/freertos/app_startup.c:204`.

### Pattern C: N16R8 overrides for Arduino (D-14 + D-22, verified)

| Key | Where it lands | Verified effect |
|-----|----------------|-----------------|
| `board_build.arduino.memory_type = qio_opi` | `build.arduino.memory_type` | Selects the precompiled kernel directory `…/framework-arduinoespressif32-esp32s3-libs/qio_opi`; the token `qio_opi/include` is in **64/64** Arduino CDB entries |
| `board_build.psram_type = opi` | `build.psram_type` | Participates in default memory-type selection; its individual effect was not isolated because `memory_type` is also set (A1) |
| `board_build.flash_mode = qio` | `build.flash_mode` | The image header reports **DIO**: `builder/main.py:88-97` — `if mode in ("qio", "qout"): return "dio"` |
| `board_upload.flash_size = 16MB` | Image header | `esptool image-info` → `Flash size: 16MB` |
| `board_upload.maximum_size = 16777216` | Upload/size check | Not independently exercised; the reported flash budget is the app partition (6 553 600 B), not this key (A2) |
| `board_build.partitions = default_16MB.csv` | Arduino: `tools/partitions/` of the core | `ARDUINO_PARTITION_default_16MB` in **64/64** CDB entries; `partitions.bin` produced (3 072 B) |
| `-DBOARD_HAS_PSRAM` (D-22) | Preprocessor define | `BOARD_HAS_PSRAM` in **64/64** CDB entries; without it `CONFIG_SPIRAM` is undefined in user TUs (P5) |

**Octal PSRAM mechanism:** the `qio_opi` kernel set ships `sdkconfig.h` with

```
#define CONFIG_SPIRAM 1
#define CONFIG_SPIRAM_MODE_OCT 1
#define CONFIG_SPIRAM_BOOT_INIT 1
```

`[VERIFIED: framework-arduinoespressif32-esp32s3-libs/qio_opi/include/sdkconfig.h:880-881,888]`,
whereas `qio_qspi/include/sdkconfig.h:881` defines `CONFIG_SPIRAM_MODE_QUAD 1`. The memory
type selects a kernel set in which octal PSRAM is already configured; `-DBOARD_HAS_PSRAM`
prevents `esp32-hal-psram.h:25-32` from erasing `CONFIG_SPIRAM` for code compiled with
`ESP32_ARDUINO_LIB_BUILDER`.

### Pattern D: ESP-IDF environment (P2, verified)

```ini
[esp32s3_espidf]
platform = espressif32@8.0.0
board = esp32-s3-devkitc-1
framework = espidf
board_upload.flash_size = 16MB
board_upload.maximum_size = 16777216
board_build.partitions = default_16MB.csv
extra_scripts = pre:../../scripts/pio/compiledb.py
```

```ini
# homeworks/0_0-toolchain-smoke/sdkconfig.defaults
CONFIG_ESPTOOLPY_FLASHSIZE_16MB=y
CONFIG_SPIRAM=y
CONFIG_SPIRAM_MODE_OCT=y
```

```text
# homeworks/0_0-toolchain-smoke/default_16MB.csv
# Name,   Type, SubType, Offset,  Size, Flags
nvs,      data, nvs,     0x9000,  0x5000,
otadata,  data, ota,     0xe000,  0x2000,
app0,     app,  ota_0,   0x10000, 0x640000,
app1,     app,  ota_1,   0x650000,0x640000,
spiffs,   data, spiffs,  0xc90000,0x360000,
coredump, data, coredump,0xFF0000,0x10000,
```

The CSV is byte-for-byte the Arduino core's own
`tools/partitions/default_16MB.csv` `[VERIFIED: framework-arduinoespressif32/tools/partitions/default_16MB.csv]`,
copied into the project because the ESP-IDF builder resolves `build.partitions` in
`framework-espidf/components/partition_table/` first and only then relative to the project
directory `[VERIFIED: builder/frameworks/espidf.py:1817-1830]`. That directory contains
`partitions_singleapp*.csv`, `partitions_two_ota*.csv` and helpers, but **no**
`default_16MB.csv` `[VERIFIED: ls components/partition_table/]`.

`sdkconfig.defaults` is read from `PROJECT_DIR` (`espidf.py:131`) and its mtime is compared
against `build.ninja` (`espidf.py:149-152`), so editing it is enough to trigger
reconfiguration — no manual deletion of the generated `sdkconfig.<env>` is required.

### Pattern E: Compilation database (verified for both frameworks)

```python
# scripts/pio/compiledb.py
import os
Import("env")

env.Replace(COMPILATIONDB_PATH=os.path.join(env.subst("$PROJECT_DIR"), "compile_commands.json"))
```

The `compiledb` target is core PlatformIO:
`env.Alias("compiledb", env.CompilationDatabase("$COMPILATIONDB_PATH"))`
`[VERIFIED: platformio/builder/main.py:195-196]`. The default path is already
`$PROJECT_DIR/compile_commands.json` (`builder/main.py:78`); setting it explicitly documents
the contract.

**Do not add `COMPILATIONDB_INCLUDE_TOOLCHAIN=True`.** Core 6.2.0 prints
`Warning! \`COMPILATIONDB_INCLUDE_TOOLCHAIN\` is scoping` four times per run
(`builder/tools/piobuild.py:144-145`); without it the warning count is zero and the CDB still
contains every required source. The option's only effect is appending toolchain include
directories to `CPPPATH` during `compiledb`.

**Verified results (this session):**

| Env | Entries | `lib/` sources present | `src/main.cpp` | Key tokens |
|-----|---------|------------------------|----------------|------------|
| `native` | 4 | `common.c`, `port.c`, `host.c` (absolute paths) | yes | neither `-DARDUINO=` nor `-DESP_PLATFORM` |
| `esp32s3_arduino` | 64 | `common.c`, `port.c`, `arduino_adapter.c` | 1 entry | `qio_opi/include` 64/64; `ARDUINO_PARTITION_default_16MB` 64/64; `BOARD_HAS_PSRAM` 64/64 |
| `esp32s3_espidf` | 1070 | `common.c`, `port.c`, `espidf_adapter.c` | 1 entry | `-DESP_PLATFORM` 1070/1070; `esp_driver_gpio/include` in 205 entries |

Counts are environment-dependent; assertions must test **membership and token presence**,
not an exact total. `compile_commands.json` is **overwritten** by every `compiledb` run. The
path is deliberately one file (D-17/D-18), so each framework's evidence must be asserted
immediately after its own run.

**LDF:** no `lib_ldf_mode` / `lib_compat_platform` override is needed. Every build reports
`LDF Modes: Finder ~ chain, Compatibility ~ soft` and finds all declared libraries
(`Found 3 compatible libraries` for native). ESP-IDF headers resolve because the builder
passes the component include paths to the library compile command.

### Pattern F: `symlink://` shared libraries (verified)

```ini
lib_deps =
    common=symlink://../../lib/common
    port=symlink://../../lib/port
    host=symlink://../../lib/host
```

- The path is resolved **relative to the project directory**, not the current working
  directory: the same project built from the repository root with
  `pio run -d homeworks/0_0-toolchain-smoke -e native` succeeded, and the CDB was still
  written to `<project>/compile_commands.json`.
- The Package Manager writes `.pio/libdeps/<env>/<name>.pio-link`:
  `{"cwd": "<project dir>", "spec": {"name": "common", "uri": "symlink://../../lib/common"}}`
  `[VERIFIED: .pio/libdeps/native/common.pio-link]`. Sources are not copied; edits in `lib/`
  are visible immediately. `[CITED: https://github.com/platformio/platformio-docs/blob/develop/core/userguide/pkg/cmd_install.rst]`
- A folder without a manifest fails with
  `MissingPackageManifestError: Could not find one of 'library.json, library.properties, module.json' manifest files in the package`.
  This is why D-09's `library.json` is not optional.
- The `<name>=` alias and the manifest `name` agree in this phase; LDF reports
  `common @ 0.1.0` from `library.json`, so the version lives in one place (D-12).

### Anti-Patterns to Avoid

- **`src/main.c` as the only entry point:** does not link with Arduino core 3.3.12 (P1).
- **Public headers without `extern "C"`:** the C++ entry point cannot see C symbols (P2).
- **`board_build.partitions = default_16MB.csv` for ESP-IDF without the project-local file:**
  guaranteed `Missing partition table file` (P3).
- **`[env]` in `platformio.shared.ini`:** a global section leaks into every future project;
  named sections plus `extends` are the D-01 design.
- **Proving 16 MB / octal PSRAM by reading `platformio.ini`:** the ini states intent; the
  image header, `sdkconfig.json` and the CDB state the result.
- **Expecting `Flash mode: QIO` in the image header:** the platform maps `qio` → `dio`.
- **`sdkconfig.*` in `.gitignore` without `!sdkconfig.defaults`:** silently ignores the
  authored default file (P7).
- **Bare `CMakeLists.txt` in `.gitignore`:** hides any future authored CMake project.
- **`COMPILATIONDB_INCLUDE_TOOLCHAIN=True`:** noisy warnings with no benefit here.
- **Parsing `pio pkg exec` output by line number:** the first stdout line is the
  `Using tool-esptool@… package` banner.

---

## Review Findings Reconciled

| Finding (02-REVIEWS.md) | Verdict | Evidence |
|-------------------------|---------|----------|
| `sdkconfig.*` also ignores `sdkconfig.defaults` (HIGH) | **Confirmed** | `git check-ignore -q sdkconfig.defaults` → IGNORED under `sdkconfig.*`; `!sdkconfig.defaults` after it → VISIBLE. Order matters: negation before the broad pattern does not work. |
| Add `sdkconfig.defaults` to `VISIBLE` in `scripts/tests/test_gitignore.py` | **Confirmed** | Current `VISIBLE` ends with `"sdkconfig"` and `"dependencies.lock"` only (`scripts/tests/test_gitignore.py:122-126`). |
| `src/main.cpp` is required in prose but not asserted in CDB checks | **Confirmed** | It is present (1 entry in each ESP CDB), so asserting it is cheap and honest. |
| Hard-coded `~/.platformio/packages/tool-esptool/esptool` is less portable | **Confirmed** | `pio pkg exec -p tool-esptool -- esptool version` works and prints the package banner; use it. |
| `-std=c11` reaches `g++` and emits a warning (MEDIUM) | **Refuted** | `src/main.cpp` compile command has no `-std`; zero matching warnings; SCons routes `-std=c11` to `CFLAGS` (`Environment.py:1176-1181`). |
| 02-01 Task 1 header check builds `lib/<name>/include/<name>.h` | **Confirmed as a plan defect** | Two adapters are named `arduino_adapter.h` / `espidf_adapter.h`; a glob `lib/*/include/*.h` is the correct shape. |
| 02-05 D-03 grep `platformio.shared.ini` will match `test_pio_scripts.py` | **Confirmed** | The planned test mentions the file; the audit must look for write/create semantics, or use git history (`git log --diff-filter=A -- platformio.shared.ini`). |
| 02-04 hygiene omits `src/CMakeLists.txt` | **Confirmed** | The builder creates both files (`espidf.py:206-213`); a scoped pattern for the root file does **not** match the nested one. |
| Final gate should rerun criterion-2 evidence | **Confirmed** | The gate should rerun both `image-info` checks and the `sdkconfig.json` assertions, not trust earlier summaries. |
| `.planning/**` contains Ukrainian prose while AGENTS.md requires English | **Open** | `.planning/**` is tracked and `REUSE.toml:26` assigns it CC-BY-4.0. This refresh is English; the planner should keep new artifacts English or record an explicit exclusion. |

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Configuration composition across projects | Copies of `platformio.ini` | `extra_configs` + `extends` | 30+ copies drift; duplicated keys are a divergence source. |
| Shared-library resolution | Custom `-I` / `-L` in `build_flags` | `lib_deps = name=symlink://...` + `library.json` | LDF decides order, transitive dependencies and rebuilds; the link file already records the source. |
| Compilation database | Parsing `-v` output or a custom walker | `pio run -t compiledb` | Core PlatformIO already builds a `CompilationDatabase` from the SCons graph. |
| Flash / PSRAM configuration | Patching `boards/esp32-s3-devkitc-1.json` | `board_build.*` overrides + `sdkconfig.defaults` | Overrides survive platform upgrades and do not modify a shared package; Kconfig is the only path for IDF. |
| Partition table for ESP-IDF | Editing the installed framework package | Project-local `default_16MB.csv` | The framework directory is shared and regenerated; the project file is the supported resolution path. |
| Image inspection | A bespoke ELF header parser | `esptool image-info` | The tool that builds the header is the tool that reads it. |

**Key insight:** PlatformIO already decides file selection, flags and build order through
manifests. Manual intervention breaks incrementality and hides dependencies.

---

## Common Pitfalls

### Pitfall P1: `src/main.c` does not link with Arduino core 3.x

**What goes wrong:** `pio run -e esp32s3_arduino` fails at link:

```text
undefined reference to `_Z5setupv'
undefined reference to `_Z4loopv'
```

with references from `framework-arduinoespressif32/cores/esp32/main.cpp:63` and `:71`.

**Why it happens:** the core calls `setup()` at `cores/esp32/main.cpp:67` and `loop()` at
`:82` as C++ functions; a `.c` file gives C symbols (`setup`, not `_Z5setupv`).
`#ifdef ARDUINO` does not change the language of the translation unit.

**How to avoid:** make the entry `src/main.cpp`; use `extern "C" void app_main(void)` for
the IDF branch and `int main(void)` for native.

**Warning signs:** any Arduino build where `src/` contains only `.c` files.

### Pitfall P2: Public headers without `extern "C"`

**What goes wrong:** after moving to `.cpp`, the link fails:

```text
undefined reference to `_Z14common_versionv'
```

**Why it happens:** the libraries are pure C; the entry point is C++. Without a guard the
compiler looks for a mangled symbol.

**How to avoid:** every public header in `lib/*/include/` carries
`#ifdef __cplusplus extern "C" { … } #endif`. Include framework headers **outside** the
guard (both orders compile on this toolchain, but outside avoids nesting C++ headers inside
`extern "C"`).

**Warning signs:** native links but Arduino/ESP-IDF fails, or vice versa, with
`undefined reference to _Z…`.

### Pitfall P3: ESP-IDF cannot find `default_16MB.csv`

**What goes wrong:** the first `esp32s3_espidf` build fails:

```text
Missing partition table file `/…/homeworks/0_0-toolchain-smoke/default_16MB.csv`
```

**Why it happens:** `generate_partition_table()` builds `framework-espidf/components/partition_table/`
plus `board.get("build.partitions", "partitions_singleapp.csv")` and falls back to a path
relative to the project only when the framework file is absent
`[VERIFIED: builder/frameworks/espidf.py:1817-1830]`. The framework directory has no
`default_16MB.csv`.

**How to avoid:** ship the project-local CSV (keeping D-14 literal) and add
`sdkconfig.defaults`.

**Warning signs:** the error names an absolute path inside the project directory.

### Pitfall P4: ESP-IDF silently keeps 2 MB flash and no PSRAM

**What goes wrong:** without `sdkconfig.defaults` the build still reports `SUCCESS`, but:

```text
Warning! Flash memory size mismatch detected. Expected 16MB, found 2MB!
Please select a proper value in your `sdkconfig.defaults` or via the `menuconfig` target!
```

**Why it happens:** `board_upload.flash_size` is compared with
`sdk_config["ESPTOOLPY_FLASHSIZE"]` (`espidf.py:2500-2509`); the comparison only warns.
Octal PSRAM is not enabled at all without `CONFIG_SPIRAM_MODE_OCT=y`.

**How to avoid:** the three-line `sdkconfig.defaults` from Pattern D. Assert the generated
`sdkconfig.json`, never the build banner (the banner's `16MB Flash` line comes from the
board manifest, not from Kconfig).

**Warning signs:** `SUCCESS` with the mismatch warning; `SPIRAM` absent from
`sdkconfig.json`.

### Pitfall P5: `-DBOARD_HAS_PSRAM` missing → `CONFIG_SPIRAM` undefined in user code

**What goes wrong:** `#if CONFIG_SPIRAM` in user code is false and `WString` uses a 64 KB
capacity even though octal PSRAM is initialised at boot.

**Why it happens:** `esp32-hal-psram.h:25-32` does:

```c
#if defined(ESP32_ARDUINO_LIB_BUILDER) && !defined(BOARD_HAS_PSRAM)
#ifdef CONFIG_SPIRAM_SUPPORT
#undef CONFIG_SPIRAM_SUPPORT
#endif
#ifdef CONFIG_SPIRAM
#undef CONFIG_SPIRAM
#endif
#endif
```

`ESP32_ARDUINO_LIB_BUILDER` is present in all 64 Arduino CDB entries; it comes from
`framework-arduinoespressif32-esp32s3-libs/flags/defines:1`.

**Evidence:** preprocessing `esp32-hal-psram.h` with `-DESP32_ARDUINO_LIB_BUILDER` and
`-I…/qio_opi/include` yields:
- without `-DBOARD_HAS_PSRAM`: only `#define CONFIG_SPIRAM_MODE_OCT 1`;
- with `-DBOARD_HAS_PSRAM`: `#define CONFIG_SPIRAM 1`, `#define BOARD_HAS_PSRAM 1`,
  `#define CONFIG_SPIRAM_MODE_OCT 1`.

**How to avoid:** D-22 — put `-DBOARD_HAS_PSRAM` in `[esp32s3_arduino]`'s `build_flags`.

**Warning signs:** `BOARD_HAS_PSRAM` absent from the CDB, or `CONFIG_SPIRAM` absent from the
preprocessor output.

### Pitfall P6: ESP-IDF writes files into the project tree

**What goes wrong:** after the first build the project contains `CMakeLists.txt` (118 B),
`src/CMakeLists.txt` (199 B) and `sdkconfig.esp32s3_espidf` (94 536 B). All three are
currently **visible** to git.

**Why it happens:** `create_default_project_files()` writes both CMake files when absent
(`espidf.py:187-213`); `SDKCONFIG_PATH` defaults to `PROJECT_DIR/sdkconfig.<PIOENV>`
(`espidf.py:99-103`).

**How to avoid:** D-23 — add them to `.gitignore` and to the `no-generated-files` hook.
Prefer scoped patterns:

```gitignore
homeworks/0_0-toolchain-smoke/CMakeLists.txt
homeworks/0_0-toolchain-smoke/src/CMakeLists.txt
```

A pattern for the root file does **not** match the nested one (verified). Bare
`CMakeLists.txt` would hide any future authored CMake project.

**Warning signs:** `git status` shows the files as untracked after the first IDF build.

### Pitfall P7: `sdkconfig.*` collides with `sdkconfig.defaults`

**What goes wrong:** `sdkconfig.*` ignores the authored `sdkconfig.defaults`; `git add`
refuses it and `git add -f` trips the `no-generated-files` hook.

**Why it happens:** git glob semantics. `sdkconfig.*` matches every basename starting with
`sdkconfig.`.

**How to avoid:** order-sensitive negation:

```gitignore
sdkconfig.*
!sdkconfig.defaults
!sdkconfig.defaults.*
```

Verified: with this order `sdkconfig.defaults` is VISIBLE and
`sdkconfig.esp32s3_espidf` is IGNORED. Reversing the order makes the default file IGNORED
again. Add `homeworks/0_0-toolchain-smoke/sdkconfig.defaults` to `VISIBLE` in
`scripts/tests/test_gitignore.py:100-126`.

**Warning signs:** `git check-ignore sdkconfig.defaults` exits 0.

### Pitfall P8: The compilation database is overwritten between environments

**What goes wrong:** checking "the CDB has Arduino **and** ESP-IDF sources" after two
`compiledb` runs only inspects the second run.

**Why it happens:** `COMPILATIONDB_PATH` is a single path per project
(`$PROJECT_DIR/compile_commands.json`).

**How to avoid:** assert immediately after each run, or copy to a temporary name that is
never committed.

**Warning signs:** the check passes for the last env and "fails" for the first.

### Pitfall P9: `extends` silently discards parent list values

**What goes wrong:** a project adds one `-D`, and every template flag disappears; the build
is "successful" with different flags.

**Why it happens:** `extends` does not merge list values. Reproduced:
`build_flags = ['-DCHILD_FLAG=1']` only.

**How to avoid:** do not override list-valued options in `[env:*]`; use
`${esp32s3_arduino.build_flags}` or repeat the full list if a project genuinely needs to.

**Warning signs:** `pio project config --json-output` shows no template flags in `env:*`.

### Pitfall P10: The board name string still says N8 / no PSRAM

**What goes wrong:** reading `-DARDUINO_BOARD="Espressif ESP32-S3-DevKitC-1-N8 (8 MB QD, No PSRAM)"`
from the compile command suggests the overrides did not apply.

**Why it happens:** the `name` field of `boards/esp32-s3-devkitc-1.json` is a display string;
the overrides do not rewrite it.

**How to avoid:** prove the configuration from `qio_opi/include`, `ARDUINO_PARTITION_default_16MB`,
`BOARD_HAS_PSRAM`, the preprocessed `CONFIG_SPIRAM`, and `image-info`'s `Flash size`.

**Warning signs:** an evidence script greps for "N16R8" or "PSRAM" in the board name.

### Pitfall P11: `pio pkg exec` output and exit codes

**What goes wrong:** a script parses line 1 of the output and finds
`Using tool-esptool@2.50400.0 package`, not the image header.

**Why it happens:** the wrapper prints the resolved package on **stdout** before esptool
runs. esptool exits `2` for a missing/invalid filename.

**How to avoid:** check the firmware file exists, then `grep -q 'Flash size: 16MB'`.

**Warning signs:** `head -1` shows the wrapper banner; exit code 2 with a usage message.

### Pitfall P12: Two Xtensa toolchains for one pin

**What goes wrong:** the Arduino build uses `toolchain-xtensa-esp-elf@14.2.0+20260121`, the
ESP-IDF build uses `toolchain-xtensa-esp-elf` (15.2.0). On disk this is about 2.4 GB, plus
the frameworks.

**Why it happens:** the platform manifest declares 14.2.0 with 15.2.0 as an optional
version; the ESP-IDF framework is built against 15.2.0.

**How to avoid:** do not "align" them manually; document that both are expected. The
evidence commands read compiler paths from the CDB, not from a guess.

**Warning signs:** an attempt to pin one toolchain for both environments breaks ESP-IDF.

---

## Code Examples

### Example 1: `library.json` (verified)

```json
{
  "name": "common",
  "version": "0.1.0",
  "build": {
    "srcDir": "src",
    "includeDir": "include"
  }
}
```

`version` is the only place the version lives (D-12). LDF reports `common @ 0.1.0`.

### Example 2: Project `platformio.ini` (verified)

```ini
[platformio]
default_envs = native
extra_configs = ../../platformio.shared.ini

[env:native]
extends = native_unity
lib_deps =
    common=symlink://../../lib/common
    port=symlink://../../lib/port
    host=symlink://../../lib/host

[env:esp32s3_arduino]
extends = esp32s3_arduino
lib_deps =
    common=symlink://../../lib/common
    port=symlink://../../lib/port
    arduino=symlink://../../lib/arduino

[env:esp32s3_espidf]
extends = esp32s3_espidf
lib_deps =
    common=symlink://../../lib/common
    port=symlink://../../lib/port
    espidf=symlink://../../lib/espidf
```

### Example 3: `extern "C"` in a public header (verified)

```c
#pragma once

#include <Arduino.h>          /* framework include outside the linkage guard */

#ifdef __cplusplus
extern "C" {
#endif

const char *arduino_adapter_version(void);

#ifdef __cplusplus
}
#endif
```

For `lib/espidf`, replace `<Arduino.h>` with `<driver/gpio.h>`. Both variants compiled in
their own environment, and the pure-C `.c` source called `pinMode(0, OUTPUT)` and
`gpio_reset_pin(GPIO_NUM_0)` respectively.

### Example 4: `src/main.cpp` (verified)

```cpp
#include <stdio.h>
#include "common.h"
#include "port.h"

#if defined(ARDUINO)
#include <Arduino.h>
#include "arduino_adapter.h"

void setup(void) {
    (void)printf("%s %s\n", common_version(), arduino_adapter_version());
}
void loop(void) {}

#elif defined(ESP_PLATFORM)
#include "espidf_adapter.h"

extern "C" void app_main(void) {
    (void)printf("%s %s\n", common_version(), espidf_adapter_version());
}

#else
#include "host.h"

int main(void) {
    (void)printf("%s %s %s\n", common_version(), port_version(), host_version());
    return 0;
}
#endif
```

`#include <stdio.h>` is required: the review noted the action prose named `printf` without
the include.

### Example 5: Deterministic criterion-4 checks

```bash
# Arduino — assert immediately after this run; the next compiledb overwrites the file.
pio run -t compiledb -e esp32s3_arduino
python3 - <<'PY'
import json, sys

db = json.load(open("homeworks/0_0-toolchain-smoke/compile_commands.json"))

def cmd(e):
    return e.get("command") or " ".join(e.get("arguments", []))

files = [e["file"] for e in db]
required = [
    "lib/common/src/common.c",
    "lib/port/src/port.c",
    "lib/arduino/src/arduino_adapter.c",
    "src/main.cpp",
]
missing = [s for s in required if not any(f.endswith(s) for f in files)]
assert not missing, missing
assert all("qio_opi/include" in cmd(e) for e in db), "qio_opi kernel set missing"
assert all("ARDUINO_PARTITION_default_16MB" in cmd(e) for e in db), "partition token missing"
assert all("BOARD_HAS_PSRAM" in cmd(e) for e in db), "PSRAM flag missing"
print(f"arduino CDB OK: {len(db)} entries")
PY

# ESP-IDF — rerun compiledb; the file is overwritten by design.
pio run -t compiledb -e esp32s3_espidf
python3 - <<'PY'
import json

db = json.load(open("homeworks/0_0-toolchain-smoke/compile_commands.json"))

def cmd(e):
    return e.get("command") or " ".join(e.get("arguments", []))

files = [e["file"] for e in db]
required = [
    "lib/common/src/common.c",
    "lib/port/src/port.c",
    "lib/espidf/src/espidf_adapter.c",
    "src/main.cpp",
]
missing = [s for s in required if not any(f.endswith(s) for f in files)]
assert not missing, missing
assert all("-DESP_PLATFORM" in cmd(e) for e in db), "ESP_PLATFORM missing"
print(f"espidf CDB OK: {len(db)} entries")
PY
```

### Example 6: Deterministic criterion-2 checks

```bash
# Arduino: the image header carries the flash size.
test -f homeworks/0_0-toolchain-smoke/.pio/build/esp32s3_arduino/firmware.bin
pio pkg exec -p tool-esptool -- esptool --chip esp32s3 image-info \
  homeworks/0_0-toolchain-smoke/.pio/build/esp32s3_arduino/firmware.bin \
  | grep -q 'Flash size: 16MB'

# ESP-IDF: both the generated Kconfig view and the image header.
python3 - <<'PY'
import json

s = json.load(open("homeworks/0_0-toolchain-smoke/.pio/build/esp32s3_espidf/config/sdkconfig.json"))
assert s["ESPTOOLPY_FLASHSIZE"] == "16MB"
assert s["ESPTOOLPY_FLASHSIZE_16MB"] is True
assert s["SPIRAM"] is True
assert s["SPIRAM_MODE_OCT"] is True
assert s["SPIRAM_MODE_QUAD"] is False
print("ESP-IDF 16MB + octal PSRAM OK")
PY

test -f homeworks/0_0-toolchain-smoke/.pio/build/esp32s3_espidf/firmware.bin
pio pkg exec -p tool-esptool -- esptool --chip esp32s3 image-info \
  homeworks/0_0-toolchain-smoke/.pio/build/esp32s3_espidf/firmware.bin \
  | grep -q 'Flash size: 16MB'
```

Observed values in the generated `sdkconfig.json`:
`ESPTOOLPY_FLASHSIZE = '16MB'` (str), `ESPTOOLPY_FLASHSIZE_16MB = True` (bool),
`SPIRAM = True`, `SPIRAM_MODE_OCT = True`, `SPIRAM_MODE_QUAD = False`,
`IDF_TARGET = 'esp32s3'` (str), `PARTITION_TABLE_OFFSET = 32768` (int).

### Example 7: AST-only test for the SCons script

```python
"""Contract test for scripts/pio/compiledb.py — do not import it."""

import ast
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "pio" / "compiledb.py"


def test_script_is_parseable_and_uses_scons_import() -> None:
    tree = ast.parse(SCRIPT.read_text(encoding="utf8"))
    calls = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "Import"
    ]
    assert calls, "compiledb.py must call Import(\"env\")"
```

Importing the script outside SCons raises `NameError: name 'Import' is not defined`; the AST
check is the correct contract.

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `lib_extra_dirs` | `lib_deps = name=symlink://…` | Deprecated since PlatformIO 6.0 | LDF no longer scans all of `lib/`; the dependency becomes explicit. |
| Arduino core 2.0.17 (platform 7.x) | Arduino core 3.3.12 (platform 8.0.0) | 2026-10-19 | Arduino-ESP32 3.x APIs; precompiled kernel sets per memory type. |
| Per-chip Xtensa toolchains | Unified `toolchain-xtensa-esp-elf` 14.2.0 / 15.2.0 | 8.0.0 | Older `toolchain-xtensa-esp32{,s2,s3}` packages are no longer needed. |
| ESP-IDF 5.5.x | ESP-IDF 6.1.0 (`framework-espidf 4.60100.0`) | 7.x → 8.0.0 | Different component/Kconfig set; `sdkconfig.defaults` is mandatory for 16 MB. |
| Single C/C++ standard flag | SCons routes `-std=` by language | SCons 4.11.1 | `-std=c11` stays on C files; the C++ entry point is untouched. |

**Deprecated/outdated:**
- `lib_extra_dirs` — do not use (ADR-0007).
- `src/main.c` as the Arduino entry point — does not work with core 3.x.
- Expecting `Flash mode: QIO` in the image header — the platform returns `DIO`.
- `COMPILATIONDB_INCLUDE_TOOLCHAIN=True` — noisy in Core 6.2.0 and unnecessary here.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `board_build.psram_type = opi` has an independent effect | Pattern C | Low: `board_build.arduino.memory_type = qio_opi` already selected the octal kernel set in this session; both keys are locked by D-14. |
| A2 | `board_upload.maximum_size = 16777216` matters to the upload/size check | Pattern C | Low: the observed flash budget is the app partition (6 553 600 B); the build passed. Keep the key because D-14 locks it. |
| A3 | `pio pkg exec` remains portable under a custom `PLATFORMIO_CORE_DIR` | Pitfall P11 / Alternatives | Low: it is a core command that resolves its own package directory; only the default layout was exercised. |
| A4 | The `-std=` language routing holds on Linux CI (gcc/g++ rather than Apple clang) | Pitfall P12 / Review Findings | Low: the routing is in SCons, above the toolchain; only macOS was executed here. |
| A5 | `pio pkg exec` prints exactly one banner line before esptool output in 6.2.0 | Pitfall P11 | Low for correctness: evidence scripts use `grep`, so an extra line is harmless. |
| A6 | The English-artifact rule applies to tracked `.planning/**` | Open Questions | Medium for repository policy: the new research and plans are English; existing planning files are partly Ukrainian. Record an explicit decision. |

---

## Open Questions

1. **Does the English-artifact rule cover `.planning/**`?**
   - What we know: `AGENTS.md` says repository artifacts are English; `.planning/**` is
     tracked and licensed CC-BY-4.0 by `REUSE.toml:26`.
   - What is unclear: whether planning prose is an "artifact" under that rule.
   - Recommendation: keep all new Phase 2 artifacts in English (this file is), and record
     the policy decision rather than silently leaving mixed-language prose.

2. **Should the `.gitignore` patterns for `CMakeLists.txt` be scoped or global?**
   - What we know: D-23 requires the generated files to be ignored; a bare `CMakeLists.txt`
     would hide a future authored CMake project; the smoke project is temporary (D-07).
   - What is unclear: whether Phase 3 removes the scoped patterns together with the project.
   - Recommendation: use the two scoped patterns in Pitfall P6 and delete them in the same
     Phase 3 commit that removes `homeworks/0_0-toolchain-smoke/`.

3. **How is D-03's "no generator" proven?**
   - What we know: `grep -rn 'platformio.shared.ini' scripts/` will match the planned
     contract test.
   - What is unclear: which audit shape is acceptable to the verifier.
   - Recommendation: audit for write/create semantics
     (`open(..., "w")`, `Path.write_text`, `touch`, template rendering) rather than any
     mention, or use `git log --diff-filter=A -- platformio.shared.ini` to show the file was
     added by a normal commit with no generator in the tree.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| PlatformIO Core | All builds | ✓ | 6.2.0 | — |
| Python | PlatformIO and evidence scripts | ✓ | 3.13.13 | — |
| `platform-native` | `pio run -e native` | ✓ | 1.2.1 | — |
| `espressif32` 8.0.0 | ESP builds | ✓ | 8.0.0 | 7.1.3 / pioarduino (not needed) |
| `framework-arduinoespressif32` + s3 libs | Arduino | ✓ | 4.30312.261016 / 3.3.12 | — |
| `framework-espidf` | ESP-IDF | ✓ | 4.60100.0 (IDF 6.1.0) | — |
| `toolchain-xtensa-esp-elf` | ESP builds | ✓ | 14.2.0 and 15.2.0 | — |
| `tool-esptool` | Criterion 2 evidence | ✓ | 2.50400.0 (esptool 5.4.0) | `pio pkg exec` |
| `tool-cmake` | ESP-IDF configure | ✓ | 3.30.2 | — |
| `tool-ninja` | ESP-IDF build | ✓ | 1.13.2 | — |
| `tool-scons` | PlatformIO build | ✓ | 4.41101.0 | — |
| `pre-commit` | Phase gate | ✓ | 4.7.0 | — |
| `git` | Ignore-hook checks | ✓ | 2.54.0 | — |
| Disk | Toolchains and frameworks | ✓ | ~5.5 GB already used; ~1.4 TB free | — |
| Network | First package installation on a fresh machine | ✓ (registry) | — | Offline build once installed |

**Missing dependencies with no fallback:** none on this machine.

**Missing dependencies with fallback:** none — everything the phase needs is installed after
the first `pio run`.

Note: `pio pkg show` fetches a README from `raw.githubusercontent.com`; a network-restricted
environment can deny that fetch while still printing the registry metadata. This does not
affect the build or the evidence commands.

---

## Validation Architecture

> `workflow.nyquist_validation` is `true` in `.planning/config.json`, so this section is
> required.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | No firmware unit framework in this phase (D-16). Repository scripts use the Python standard-library `unittest` runner. |
| Config file | `scripts/tests/` (unittest discovery); `homeworks/0_0-toolchain-smoke/platformio.ini` |
| Quick run command | `python3 -m unittest discover -s scripts/tests -v` |
| Full suite command | `pio run -e native && pio run -e esp32s3_arduino && pio run -e esp32s3_espidf` plus the evidence assertions in Examples 5 and 6 |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| FOUND-09 | Core is 6.2.0 | smoke | `pio --version \| grep -q '6.2.0'` | ✅ |
| FOUND-09 | Platform resolves to 8.0.0 | smoke | `pio pkg show platformio/espressif32 \| grep -qE 'Platform.*8\.0\.0'` | ✅ |
| FOUND-09 | Native build is green | integration | `pio run -d homeworks/0_0-toolchain-smoke -e native` | ❌ Wave 0 (project is new) |
| FOUND-09 | Arduino build is green | integration | `pio run -d homeworks/0_0-toolchain-smoke -e esp32s3_arduino` | ❌ Wave 0 |
| FOUND-09 | ESP-IDF build is green | integration | `pio run -d homeworks/0_0-toolchain-smoke -e esp32s3_espidf` | ❌ Wave 0 |
| FOUND-09 | Arduino image is 16 MB | integration | `pio pkg exec -p tool-esptool -- esptool --chip esp32s3 image-info …/esp32s3_arduino/firmware.bin \| grep -q 'Flash size: 16MB'` | ❌ Wave 0 |
| FOUND-09 | Arduino uses the octal kernel set and PSRAM flag | integration | Python `all(...)` over the Arduino CDB for `qio_opi/include`, `ARDUINO_PARTITION_default_16MB`, `BOARD_HAS_PSRAM` | ❌ Wave 0 |
| FOUND-09 | ESP-IDF is 16 MB with octal PSRAM | integration | Python assertions on `.pio/build/esp32s3_espidf/config/sdkconfig.json` | ❌ Wave 0 |
| FOUND-09 | ESP-IDF image is 16 MB | integration | `image-info` on `.pio/build/esp32s3_espidf/firmware.bin` | ❌ Wave 0 |
| ARCH-04 | `symlink://` libraries resolve and link | integration | `pio run -e native` with `Found 3 compatible libraries` and the dependency graph `common @ 0.1.0`, `port @ 0.1.0`, `host @ 0.1.0` | ❌ Wave 0 |
| ARCH-04 | Every library has a manifest | static | `test -f lib/{common,port,arduino,espidf,host}/library.json` | ❌ Wave 0 |
| ARCH-04 | Arduino CDB has the shared sources and `src/main.cpp` | integration | Python assertions after `-t compiledb -e esp32s3_arduino` | ❌ Wave 0 |
| ARCH-04 | ESP-IDF CDB has the shared sources and `src/main.cpp` | integration | Python assertions after `-t compiledb -e esp32s3_espidf` | ❌ Wave 0 |
| ARCH-04 | Generated ESP-IDF files stay ignored | static | `git check-ignore -q <path>` for `CMakeLists.txt`, `src/CMakeLists.txt`, `sdkconfig.esp32s3_espidf`; non-zero for `sdkconfig.defaults` | ❌ Wave 0 (extend `scripts/tests/test_gitignore.py`) |
| D-03 | No generator exists in this phase | review | Write/create audit over `scripts/`, or `git log --diff-filter=A -- platformio.shared.ini` | ✅ by review |

### Sampling Rate

- **Per task commit:** `python3 -m unittest discover -s scripts/tests -v` plus
  `pio run -e native` (about 0.3 s after the first build).
- **Per wave merge:** `pio run -e native` and `pio run -e esp32s3_arduino` with the CDB
  assertions.
- **Phase gate:** all three builds green, both CDB assertions, both image checks, the
  `sdkconfig.json` assertions, `python3 -m unittest discover -s scripts/tests -v`,
  `python3 scripts/check_policy.py --check`, `python3 scripts/check_pr_templates.py`,
  `pre-commit run --all-files`, and `git ls-files -ci --exclude-standard -- …` returning
  empty.

### Wave 0 Gaps

- [ ] `scripts/tests/test_pio_scripts.py` — AST-only contract for `scripts/pio/compiledb.py`
      (Example 7). Importing it outside SCons fails on `Import("env")`.
- [ ] `scripts/tests/test_gitignore.py` — add to `VISIBLE`:
      `homeworks/0_0-toolchain-smoke/sdkconfig.defaults`; add to `IGNORED`:
      `homeworks/0_0-toolchain-smoke/CMakeLists.txt`,
      `homeworks/0_0-toolchain-smoke/src/CMakeLists.txt`,
      `homeworks/0_0-toolchain-smoke/sdkconfig.esp32s3_espidf`.
- [ ] Optional static test for `platformio.shared.ini`: exactly three named sections, no
      `[env:]`, no `lib_extra_dirs`, `espressif32@8.0.0`, `-DBOARD_HAS_PSRAM`, and the
      three-line `extra_scripts` path.
- [ ] No fixture isolates the CDB between environments — assert immediately after each
      `compiledb` run (P8).
- [ ] No firmware test framework — intentional (D-16).

---

## Security Domain

> `security_enforcement: true`, `security_asvs_level: 1` in `.planning/config.json`.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | — |
| V3 Session Management | no | — |
| V4 Access Control | no | — |
| V5 Input Validation | yes (limited) | Paths in `lib_deps` / `extra_configs` are trusted but must resolve inside the repository; no absolute paths in commits. `extra_scripts` points at one reviewed repository file. |
| V6 Cryptography | no | — |
| V14 Configuration | yes | Pinned versions; `compile_commands.json` and `.pio/` are gitignored; generated ESP-IDF files are gitignored; `sdkconfig.defaults` carries no credentials. |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Registry package substitution (typosquat) | Tampering | Only `platformio/*` and `espressif/*`; exact pins; registry metadata checked. |
| Arbitrary code execution through `extra_scripts` | Elevation of Privilege | Exactly one script in the repository (`scripts/pio/compiledb.py`), reviewed; the path is relative and not a dependency. |
| Secret leakage in build logs | Information Disclosure | gitleaks in pre-commit and CI; build logs are not committed (D-20). |
| Uncontrolled toolchain download | Tampering | Packages come from the official registry over HTTPS at pinned versions. |
| Absolute paths in `compile_commands.json` | Information Disclosure | The file is gitignored (`.gitignore:16`, also `:174`). |

---

## Project Constraints (from CLAUDE.md / AGENTS.md)

Directives the plan must satisfy:

- **GSD workflow is mandatory:** every change goes through `/gsd-*` or a deterministic script
  under `scripts/`. Direct edits outside the workflow are not allowed.
  `[VERIFIED: AGENTS.md, "Change workflow"]`
- **Conventional Commits:** `type(scope): summary`, where `type` is one of `feat`, `fix`,
  `test`, `refactor`, `perf`, `docs`, `style`, `chore` and `scope` is the phase-plan or
  homework ID. Example: `feat(2_2): add shared PlatformIO config`.
- **Branches and PRs:** this is infrastructure, so use `infra/<slug>` and
  `.github/PULL_REQUEST_TEMPLATE/infra.md`; squash-merge into `main`.
- **Homework ID:** `^[0-9]+_[0-9]+-[a-z0-9-]+$`, ASCII-only. `0_0-toolchain-smoke` matches.
- **Generated files are never committed:** the enumerated list is
  `compile_commands.json`, `site/`, `.pio/`; D-23 extends it with the ESP-IDF generated
  files. `platformio.shared.ini` is **not** generated in this phase and must not be added.
- **REUSE:** the split is declared once. `lib/**` and `scripts/**` fall under the MIT
  catch-all; `*.md` and `homeworks/**/*.md` are CC-BY-4.0. `[VERIFIED: REUSE.toml:19-28]`
- **Secrets:** gitleaks must pass; no credentials in `platformio.ini` or
  `sdkconfig.defaults`.
- **LFS:** `.bin`/`.elf` are LFS-routed by `.gitattributes:9-10`, but generated firmware
  lives under `.pio/` and is never committed, so LFS is not exercised.
- **ADR:** cross-cutting decisions go to `docs/decisions/` with the next free number
  (**0007**) and an index update in the same change. `[VERIFIED: docs/decisions/README.md:31; scripts/tests/test_adrs.py:28-45]`
- **Language:** repository artifacts are English; communication with the user follows the
  user's language.

---

## Sources

### Primary (HIGH confidence)

Local reproduction on 2026-10-23 (PlatformIO Core 6.2.0, Python 3.13.13, macOS arm64):

- `pio --version` → `PlatformIO Core, version 6.2.0`.
- `pio pkg show platformio/espressif32` → `Platform • 8.0.0 • Public • Published on Mon Oct
  19 10:06:19 2026`, Apache-2.0, 1210 stars.
- `pio run -e native` → `[SUCCESS]`, `Found 3 compatible libraries`, `common @ 0.1.0`,
  `port @ 0.1.0`, `host @ 0.1.0`.
- `pio run -e esp32s3_arduino` → `[SUCCESS]` in 5.70 s.
- `pio run -e esp32s3_espidf` → `[SUCCESS]` in 24.73 s.
- `pio run -t compiledb -e {native,esp32s3_arduino,esp32s3_espidf}` → 4 / 64 / 1070 entries;
  all required library sources present; `src/main.cpp` present in both ESP CDBs.
- `pio pkg exec -p tool-esptool -- esptool --chip esp32s3 image-info …/firmware.bin` →
  `Flash size: 16MB`, `Flash mode: DIO`, exit 0 for both firmwares.
- Reproduced failures: `_Z5setupv`/`_Z4loopv` (`.c` entry); `_Z14common_versionv` (missing
  header guard); `app_main` (missing `extern "C"`); `Missing partition table file`;
  `Expected 16MB, found 2MB`; `MissingPackageManifestError`.
- `pio project config --json-output` → child `build_flags` replaced, not merged.
- `git check-ignore` matrix for `sdkconfig.*` / `!sdkconfig.defaults` and scoped
  `CMakeLists.txt` patterns; `git ls-files -ci` hook simulation.

Installed package sources (read this session):

- `~/.platformio/platforms/espressif32/platform.json` — version, engines, package pins.
- `~/.platformio/platforms/espressif32/builder/frameworks/espidf.py:99-103, 127-152,
  187-213, 480, 1817-1830, 2500-2509`.
- `~/.platformio/platforms/espressif32/builder/main.py:88-97`.
- `~/.platformio/platforms/espressif32/boards/esp32-s3-devkitc-1.json`.
- `~/.platformio/penv/lib/python3.13/site-packages/platformio/builder/main.py:78, 195-196`.
- `~/.platformio/penv/lib/python3.13/site-packages/platformio/builder/tools/piobuild.py:119,
  130-148`.
- `~/.platformio/penv/lib/python3.13/site-packages/platformio/builder/tools/piolib.py:964-966`.
- `~/.platformio/penv/lib/python3.13/site-packages/platformio/project/options.py:401-412`.
- `~/.platformio/packages/tool-scons/scons-local-4.11.1/SCons/Environment.py:1176-1181`.
- `~/.platformio/packages/framework-arduinoespressif32/cores/esp32/main.cpp:67, 82`.
- `~/.platformio/packages/framework-arduinoespressif32/cores/esp32/Arduino.h:154-200`.
- `~/.platformio/packages/framework-arduinoespressif32/cores/esp32/esp32-hal-psram.h:25-32`.
- `~/.platformio/packages/framework-arduinoespressif32/tools/partitions/default_16MB.csv`.
- `~/.platformio/packages/framework-arduinoespressif32-esp32s3-libs/flags/defines:1`.
- `~/.platformio/packages/framework-arduinoespressif32-esp32s3-libs/qio_opi/include/sdkconfig.h:880-881, 888`.
- `~/.platformio/packages/framework-arduinoespressif32-esp32s3-libs/qio_qspi/include/sdkconfig.h:881`.
- `~/.platformio/packages/framework-espidf/components/partition_table/` (no `default_16MB.csv`).
- `~/.platformio/packages/framework-espidf/components/esptool_py/Kconfig.projbuild:123-156`.
- `~/.platformio/packages/framework-espidf/components/esp_psram/esp32s3/Kconfig.spiram:1-18`.

Repository sources (read this session):

- `.gitignore:1-20`.
- `.pre-commit-config.yaml:19-34`.
- `scripts/tests/test_gitignore.py:95-126`.
- `scripts/tests/test_adrs.py:28-49`.
- `docs/decisions/README.md:20-31`.
- `REUSE.toml:15-28`.
- `.planning/REQUIREMENTS.md:28-77`.
- `.planning/phases/02-toolchain-truth/02-CONTEXT.md:1-299`.

### Secondary (MEDIUM confidence)

- Context7 `/platformio/platformio-docs`:
  - `extra_configs` override semantics.
  - `extends` no-merge semantics.
  - `symlink://` local-folder specification and manifest requirement.
  - `compile_commands.json` / `compiledb` documentation.
- `https://github.com/platformio/platform-espressif32/releases/tag/v8.0.0` — platform 8.0.0
  release context (Arduino core 3.3.12 / IDF 5.5.5 for Arduino, ESP-IDF 6.1).

### Tertiary (LOW confidence — not used for decisions)

- Prior `02-RESEARCH.md` claims that were not re-observed, such as exact CDB record counts
  (this session measured 4/64/1070, not 3/64/1074). Counts vary with the build graph; the
  plan must assert membership, not totals.

---

## Metadata

**Confidence breakdown:**

- **Standard stack: HIGH** — versions read from the installed manifests and the registry;
  all three builds green.
- **Architecture: HIGH** — `extends`, `symlink://`, the three-branch entry point, the
  compiledb path and the ESP-IDF artifacts were all executed.
- **Pitfalls: HIGH** — P1, P2, P3, P4, P5, P6, P7, P9, P11 and P12 were reproduced or
  directly observed; P8 and P10 are observed properties of the toolchain.
- **Validation: HIGH for the command shapes; MEDIUM for the exact record counts** (which are
  environment-dependent by design).

**Research date:** 2026-10-23
**Valid until:** 2026-11-22 (30 days; `platformio/espressif32` 8.0.0 was published on
2026-10-19 and may receive a patch release — re-check the pin before execution).

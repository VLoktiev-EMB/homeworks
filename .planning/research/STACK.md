# Stack Research

**Domain:** Embedded engineering course monorepo — 30+ independent PlatformIO projects (ESP32 Arduino + ESP-IDF, STM32, Arduino AVR), academic reports, wiring/simulation evidence, CI, and a generated documentation site
**Researched:** 2026-10-23
**Confidence:** HIGH for the build/lint/docs core; MEDIUM for the ESP-IDF language-server path; MEDIUM-LOW for the final simulation choice (must be settled by the spike)

---

## Executive Summary

The 2026 stack for this repository is unusually well defined. PlatformIO Core 6.2.0 plus the official `platform-espressif32` 8.0.0 now covers Arduino core 3.3.12 (ESP-IDF 5.5.5) and ESP-IDF 6.1 in one build system; `platform-ststm32` 20.0.0 covers STM32. Native Unity tests run on the host with no board attached. The one architectural correction is mandatory: **`lib_extra_dirs` is deprecated and scheduled for removal**. Use `lib_deps = <name>=symlink://../../lib/<name>` instead. This was validated locally on PlatformIO 6.2.0: a native build consumed a shared library through `symlink://`, compiled it, linked it, and ran correctly.

For the language server, clangd remains the right choice, but the naive "clangd + compiledb + `--query-driver`" recipe is incomplete for Xtensa. Stock clangd 21 can parse Xtensa since LLVM 20, but ESP32-S3 flags such as `-mcpu=esp32s3` and Espressif ISA extensions are best handled by Espressif's clangd fork (`esp-clang` / `tool-clangd-esp` 21.1.3). A single clangd process serves the whole multi-root workspace; per-project discovery works through `.clangd` + nearest-ancestor `compile_commands.json`, while cross-project symbol collisions remain a known limitation that must be designed around.

For simulation, the evidence points to a split strategy, not one winner. **Wokwi is the primary simulator** for ESP32 Arduino/ESP-IDF and AVR because its `diagram.json` is a real source-of-truth format, its CLI has mature headless assertions/screenshots/scenarios, and its ESP32 fidelity is the best available. **Velxio is a credible self-hosted fallback** for ESP32/AVR/RP2040, but the self-hosted image does not include STM32, and its CI is a paid hosted service. **Fritzing is not a simulator** and should be optional illustration only. **Renode is the only credible headless STM32 path** if the course's STM32 boards are F103/F4-class; QEMU's STM32 machines lack GPIO/I2C/DMA and are not viable.

Documentation should use MkDocs Material 9.7.7 now, with a deliberate migration plan: Material entered maintenance mode in November 2025 and reaches end of life on 2027-05-05. Its successor Zensical is still 0.0.x (0.0.71 on 2026-10-16), so adopting it today for a public course repository would be premature. Keep the config Zensical-compatible (no hooks, minimal plugins) and migrate at a milestone boundary after Zensical 0.1.x ships.

---

## Recommended Stack

| Layer | Choice | Version | Confidence |
|---|---|---|---|
| Build system | PlatformIO Core | 6.2.0 | HIGH |
| ESP32 platform | `platformio/espressif32` | 8.0.0 | MEDIUM (4 days old) |
| STM32 platform | `platformio/ststm32` | 20.0.0 | HIGH |
| Host tests | `platform = native` + Unity | PlatformIO-managed | HIGH |
| Shared libraries | `lib_deps = name=symlink://...` | — | HIGH (validated) |
| Language server | clangd (esp-clangd for Xtensa) | 21.x / 21.1.3 | MEDIUM |
| Compilation DB | `pio run -t compiledb` + extra script | — | HIGH (native), MEDIUM (ESP-IDF) |
| Primary simulation | Wokwi CLI | 0.29.0 | MEDIUM |
| Self-hosted simulation | Velxio (Docker) | rolling | MEDIUM |
| STM32 headless simulation | Renode | 1.17.0 | MEDIUM |
| Pinout/wiring art | Repo-owned YAML → SVG; PinViz optional | — | MEDIUM-LOW |
| Docs site | MkDocs Material | 9.7.7 | HIGH (with EOL caveat) |
| Math | KaTeX | 0.19.0 | HIGH |
| Diagrams | Mermaid (bundled with Material) | 11.x | HIGH |
| Formatter | clang-format | 23.1.3 | HIGH |
| Static analysis | clang-tidy | 23.1.3 | HIGH |
| Hooks | pre-commit | 4.7.0 | HIGH |
| Secrets | gitleaks | 8.30.1 | HIGH |
| Markdown | markdownlint-cli2 | 0.24.0 | HIGH |
| YAML | yamllint | 1.38.0 | HIGH |
| Metadata schema | check-jsonschema | 0.38.2 | HIGH |
| Python lint | ruff | 0.17.2 | HIGH |
| Binary assets | Git LFS | 10 GiB free tier | HIGH |

### Core Technologies

- **PlatformIO Core 6.2.0** — the single build system for Arduino, ESP-IDF, STM32, and native host tests.
- **`platformio/espressif32` 8.0.0** — Arduino 3.3.12 / ESP-IDF 5.5.5 and ESP-IDF 6.1 on ESP32-S3.
- **`platformio/ststm32` 20.0.0** — STM32 via `arduino`, `stm32cube`, `cmsis`, or `libopencm3`.
- **MkDocs Material 9.7.7** — documentation site generated from the same metadata as the README index.
- **Wokwi** — primary simulation and wiring source of truth (`diagram.json`).
- **Git + GitHub Actions + GitHub Pages** — protected `main`, PR checks, artifact deployment.

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---|---|---|---|
| Unity | PlatformIO-managed | Native unit tests | Pure logic in `lib/common`, `lib/port` |
| pymdown-extensions | 12.3 | Snippets, superfences, arithmatex, tabs | Every report with code or math |
| KaTeX | 0.19.0 | Formula rendering | Any report with equations |
| Mermaid | bundled (11.x) | State/timing/flow diagrams | Protocol and architecture explanations |
| check-jsonschema | 0.38.2 | `homework.yaml` validation | Every metadata change |
| Jinja2 / PyYAML | current | Deterministic docs, pinout, and workspace generation | Repository scripts |

### Development Tools

| Tool | Purpose | Notes |
|---|---|---|
| clangd (esp-clangd) | Language server | `--query-driver` over PlatformIO toolchains; esp-clangd for Xtensa |
| clang-format 23.1.3 | Formatting | Pinned everywhere; approximates ESP-IDF AStyle rules |
| clang-tidy 23.1.3 | Static analysis | Host-compiled code only |
| pre-commit 4.7.0 | Hook runner | Fast commit hooks, slower pre-push hooks |
| gitleaks 8.30.1 | Secret scanning | Staged changes locally, full history in CI |
| ruff 0.17.2 | Python lint/format | Repository scripts |
| markdownlint-cli2 0.24.0 | Markdown lint | Reports and docs |
| yamllint 1.38.0 | YAML lint | `homework.yaml`, workflows, configs |
| Wokwi CLI 0.29.0 | Headless simulation | Scenarios, assertions, screenshots |
| Renode 1.17.0 | STM32 headless tests | Robot Framework + GitHub Action |

### Installation

```bash
# Build system and host tests
pip install platformio==6.2.0

# Documentation
pip install -r requirements-docs.txt   # mkdocs==1.6.1, mkdocs-material==9.7.7, pymdown-extensions==12.3

# Repository quality
pip install pre-commit==4.7.0 ruff==0.17.2 check-jsonschema==0.38.2 yamllint==1.38.0
pre-commit install --install-hooks
pre-commit install --hook-type pre-push

# Markdown lint (Node)
npm install -g markdownlint-cli2@0.24.0

# Simulation (CI or local)
curl -L https://wokwi.com/ci/install.sh | sh

# Language server (choose one path)
# 1) Espressif esp-clang via ESP-IDF tools, or
# 2) pioarduino tool-clangd-esp package
```


---

## 1. PlatformIO Multi-Framework

### 1.1 Current versions and constraints

| Component | Version | Notes |
|---|---|---|
| PlatformIO Core | **6.2.0** (2026-09-05) | Requires Python >= 3.9; SCons 4.11.1; ZIP path-traversal security fix |
| `platformio/espressif32` | **8.0.0** (2026-10-19) | Arduino core 3.3.12 on ESP-IDF 5.5.5; `framework = espidf` uses ESP-IDF 6.1; toolchains 14.2.0+20260121; esptool 5.4 |
| `platformio/ststm32` | **20.0.0** (2026-08-31) | Frameworks: `arduino`, `stm32cube`, `cmsis`, `libopencm3`, `mbed`, `spl`, `zephyr` |
| `platform-native` | current | Uses the host compiler; no toolchain download; GCC preferred, Apple clang works on macOS |
| Unity | PlatformIO-managed | Use `test_framework = unity` |

Constraints that matter for this repository:

- **PlatformIO 8.0.0 is four days old** at research time. It is the first official release with Arduino core 3.x, so it is the only official path to current ESP32 Arduino. Pin it exactly, smoke-test it in Phase 0, and keep a documented fallback to `7.x` (Arduino 2.0.17) or the pioarduino fork if a blocking regression appears.
- **Arduino core 3.x contains breaking API changes**, especially around Bluetooth. Course code should avoid Bluetooth; if a lesson needs it, isolate it and pin the core.
- **One framework per environment.** Do not try to express "Arduino and ESP-IDF in the same env". Use separate environments (or separate homework projects) per the repository's own decision to keep separate templates.
- **ESP-IDF builds are materially slower** than Arduino builds (CMake + component manager + first-time Python env). Expect minutes per cold build; cache aggressively.
- **`pio` and Python isolation.** PlatformIO lives in `~/.platformio/penv`. Pin `platformio==6.2.0` in CI rather than "latest".

### 1.2 Repository layout that PlatformIO supports well

```
homeworks/1_3-police-flasher/
  platformio.ini
  src/                      # firmware entry point
  include/                  # project-private headers
  test/test_logic/           # native Unity tests
  assets/diagram.json
  homework.yaml
  README.md
lib/
  common/                    # pure C, no framework headers
  port/                      # thin port interfaces
  arduino/                   # Arduino adapter
  espidf/                    # ESP-IDF adapter
  host/                      # native adapter for tests
platformio.shared.ini        # shared env definitions
scripts/
docs/
```

Each homework remains an independent PlatformIO project. Shared libraries are referenced, never copied. PlatformIO shares installed platforms/toolchains globally, so 30+ projects do not multiply toolchain disk usage.

### 1.3 Shared configuration: `extra_configs` + `extends`

`extra_configs` is **not deprecated** and remains the documented way to compose configuration files. Use it for a root `platformio.shared.ini`, then `extends` named environments.

```ini
# homeworks/1_3-police-flasher/platformio.ini
[platformio]
default_envs = esp32s3
extra_configs = ../../platformio.shared.ini

[env:esp32s3]
extends = esp32s3_arduino
lib_deps =
    common=symlink://../../lib/common
    port=symlink://../../lib/port
    arduino=symlink://../../lib/arduino

[env:native]
extends = native_unity
lib_deps =
    common=symlink://../../lib/common
    port=symlink://../../lib/port
    host=symlink://../../lib/host
```

```ini
# platformio.shared.ini
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
    -std=gnu++17
    -Wall
    -Wextra
    -Werror=return-type
    -DARDUINO_USB_MODE=1
    -DARDUINO_USB_CDC_ON_BOOT=1
extra_scripts = pre:../../scripts/pio/compiledb.py

[esp32s3_espidf]
platform = espressif32@8.0.0
board = esp32-s3-devkitc-1
framework = espidf
board_build.arduino.memory_type = qio_opi
board_upload.flash_size = 16MB
board_build.partitions = default_16MB.csv
build_flags = -std=gnu11 -Wall -Wextra
extra_scripts = pre:../../scripts/pio/compiledb.py

[native_unity]
platform = native
test_framework = unity
test_build_src = true
build_flags = -std=c11 -Wall -Wextra -Werror
```

Caveat: `extends` does **not** merge list values such as `build_flags`. If an environment needs to add flags, repeat the full list or use `${common.build_flags}` interpolation. Keep the shared file small and explicit.

### 1.4 Shared libraries: replace `lib_extra_dirs`

This is the most important correction to the current project plan.

Official PlatformIO docs (v6.2.1b2) mark `lib_extra_dirs` as:

```
DATA_4c9e2a17_START
Deprecated since version 6.0: The lib_extra_dirs option has been deprecated and will be removed in the next major release.
DATA_4c9e2a17_END
```

Local validation on PlatformIO 6.2.0: `lib_extra_dirs` still works and emits **no runtime warning**, and `pio run -t compiledb` included the external library source. That makes it a trap: it works today, appears in old tutorials, and will break on the next major upgrade.

Use PlatformIO's Local Folder / Symbolic Link feature instead:

```ini
lib_deps =
    common=symlink://../../lib/common
```

Validated locally:

- A native project with `lib_deps = common=symlink://../lib/common` installed `common@0.1.0`, compiled `common.c`, archived `libcommon.a`, linked `program`, and printed the expected result.
- On macOS PlatformIO created `common.pio-link` in `.pio/libdeps/<env>/` rather than a raw symlink; this is the supported mechanism and it works.
- Paths are resolved **relative to the project directory**. From `homeworks/1_3-police-flasher/`, the repository `lib/` is `../../lib/`.
- The target must be a valid PlatformIO library: add `library.json` with `name`, `version`, `build.srcDir`, `build.includeDir`.
- Transitive dependencies are resolved by the Library Dependency Finder. Declare them in `library.json` (e.g. `port` depends on `common`) instead of listing everything in every homework.
- With `symlink://`, only the libraries you name are built. This is a feature: it avoids the classic `lib_extra_dirs` problem where every library in the extra directory is discovered and then must be excluded per environment with `lib_ignore`.

Migration rule for the roadmap: change the shared-library decision in `PROJECT.md` from `lib_extra_dirs` to `symlink://` before scaffolding 30 projects.

### 1.5 `lib_ignore` — still useful, narrower role

With `symlink://`, `lib_ignore` is no longer needed to exclude other homework libraries. Keep it for genuine conflicts with framework-bundled libraries, for example:

```ini
[env:esp32s3_espidf]
lib_ignore =
    DNSServer
    ESP Async WebServer
```

Do not build the repository architecture around `lib_ignore`; build it around explicit symlink dependencies.

### 1.6 Compilation database

`pio run -t compiledb` writes `compile_commands.json` to the project root by default. Two build variables matter:

- `COMPILATIONDB_INCLUDE_TOOLCHAIN=True` — include toolchain/sysroot paths. Default is `False`, which is the usual cause of "system headers not found" in clangd.
- `COMPILATIONDB_PATH` — override the output path.

Use one shared pre-script for every environment:

```python
# scripts/pio/compiledb.py
import os
Import("env")

env.Replace(COMPILATIONDB_INCLUDE_TOOLCHAIN=True)
env.Replace(COMPILATIONDB_PATH=os.path.join(env.subst("$PROJECT_DIR"), "compile_commands.json"))
```

Then:

```bash
pio run -t compiledb -e esp32s3
```

Validated for `platform = native`: a project with one `src/main.c` and one shared library produced two entries (`src/main.c` and the shared library source), with the shared library included. This is the required behavior for the repository's native test project.

ESP-IDF caveat (MEDIUM confidence): PlatformIO's `compiledb` for `framework = espidf` is known to be less complete than for Arduino, because the ESP-IDF build is driven through CMake and PlatformIO's wrapper. Reports of missing component include paths exist. The local validation attempt was blocked by a broken ESP-IDF Python environment (missing `idf_component_manager`), not by PlatformIO itself. Treat "ESP-IDF compiledb is complete enough for clangd" as a spike item, not a settled fact. If it is incomplete, the fallback is to generate a CMake compilation database (`-DCMAKE_EXPORT_COMPILE_COMMANDS=ON`) in a separate build directory and point `.clangd` at it.

Do **not** commit `compile_commands.json`: it is large, absolute-path dependent, and stale after every configuration change. Generate it locally and in CI when needed.

### 1.7 Native Unity tests

Use `platform = native` with `test_framework = unity`. Structure:

```
test/
  test_logic/
    test_logic.c
```

Typical test entry point:

```c
#include <unity.h>
#include "common.h"

void setUp(void) {}
void tearDown(void) {}

static void test_add(void) {
    TEST_ASSERT_EQUAL_INT(5, common_add(2, 3));
}

int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_add);
    return UNITY_END();
}
```

Rules:

- `test_build_src = true` when tests must compile code from `src/`. Otherwise PlatformIO builds only `lib/` dependencies and the test files.
- Shared library tests belong in a dedicated `tests/` PlatformIO project that symlinks `lib/common` and `lib/port`, not duplicated inside every homework.
- Native tests are the right place for TDD of pure logic. They are fast, deterministic, and run on Linux/macOS/Windows CI runners.
- Native tests cannot prove hardware behavior. Keep the tiered testing model: build always, unit tests for pure logic, simulation where supported, HIL when hardware is available.
- On macOS, `platform = native` uses the host compiler (Apple clang). This worked locally. On Linux CI, install `gcc`/`g++` explicitly.

### 1.8 ESP32-S3-DevKitC-1 N16R8 exact configuration

The stock `esp32-s3-devkitc-1` board manifest describes an **8 MB, no-PSRAM** board. For the N16R8 variant (16 MB quad flash, 8 MB octal PSRAM), override:

```ini
board = esp32-s3-devkitc-1
board_build.arduino.memory_type = qio_opi
board_build.flash_mode = qio
board_build.psram_type = opi
board_upload.flash_size = 16MB
board_upload.maximum_size = 16777216
board_build.partitions = default_16MB.csv
build_flags =
    -DBOARD_HAS_PSRAM
    -DARDUINO_USB_MODE=1
    -DARDUINO_USB_CDC_ON_BOOT=1
```

Notes:

- `qio_opi` is the correct memory type for N16R8 (quad flash, octal PSRAM). Using the default will silently misconfigure PSRAM.
- Native USB upload/debug requires the USB/OTG port and `ARDUINO_USB_MODE=1`; the UART port will not expose the built-in JTAG.
- If the board is used with ESP-IDF, the same flash/PSRAM settings must be reflected in `sdkconfig.defaults`.

### 1.9 PlatformIO commands for CI

```bash
# Build one environment
pio run -d homeworks/1_3-police-flasher -e esp32s3

# Run native tests
pio test -d homeworks/1_3-police-flasher -e native

# Generate the compilation database
pio run -d homeworks/1_3-police-flasher -t compiledb -e esp32s3

# Install dependencies without building
pio pkg install -d homeworks/1_3-police-flasher -e esp32s3
```

CI should build **changed** projects on pull requests and the full matrix nightly. A full 30-project ESP-IDF build is not a pull-request-sized job.

---

## 2. Language Server

### 2.1 clangd vs cpptools

| Criterion | clangd | cpptools (Microsoft C/C++) |
|---|---|---|
| License | Apache 2.0 with LLVM exceptions | Proprietary |
| Compilation database | Native `compile_commands.json` support | Uses `c_cpp_properties.json` / provider API |
| Cross-compilers | `--query-driver` extracts sysroot, defines, include paths from the real GCC | Built-in but less transparent; ignores unknown flags |
| Xtensa/ESP32 | Requires LLVM 20+ or Espressif's fork for ISA extensions | Tolerates Xtensa flags; IntelliSense is heuristic |
| C++ accuracy | Clang parser, high fidelity | EDG-based IntelliSense, good but different |
| Multi-root | One server, ancestor CDB discovery, global index | Per-workspace database, heavier |
| Resource use | Moderate; background index can be tuned | High memory on large trees |
| Telemetry | None | Present |
| Recommendation | **Primary** | Fallback only if clangd breaks on a specific lesson |

Use clangd. Keep cpptools out of the recommended setup to avoid two competing IntelliSense engines. If a student already has cpptools installed, disable its IntelliSense (`C_Cpp.intelliSenseEngine: "disabled"`) to prevent duplicate diagnostics.

### 2.2 Which clangd binary

Use **Espressif's clangd fork** for the whole workspace, not Apple's `/usr/bin/clangd`:

- Espressif maintains `espressif/llvm-project` with Xtensa and ESP RISC-V ISA extension support (`xespv`, `xesploop`, `xespdsp`). This removes "unknown argument" errors for ESP32 flags and improves intrinsic/header parsing.
- The pioarduino platform packages it as `tool-clangd-esp` 21.1.3+20260304.
- Espressif-IDE and the VS Code ESP-IDF extension install it as `esp-clang` (`esp-19.1.2` or newer).
- Upstream clangd gained an Xtensa target in LLVM 20, so a Homebrew LLVM 21 clangd can parse `--target=xtensa...`, but it still does not know Espressif's `-mcpu=esp32s3` extensions. Stock clangd is a fallback for ARM/native, not the primary ESP32 server.

Practical recommendation:

1. Install Espressif's clangd once (via ESP-IDF tools or the pioarduino `tool-clangd-esp` package).
2. Point VS Code's `clangd.path` at a wrapper script that selects it.
3. Use the same server for STM32/native; it is still Clang and handles ARM targets.

Apple clangd 21.0.0 (present on this machine) is acceptable for host/native code but is the wrong default for ESP32.

### 2.3 Recommended configuration

**Wrapper script** (`scripts/clangd-wrapper.sh`) — resolves the PlatformIO toolchain globs and execs the chosen clangd:

```bash
#!/usr/bin/env bash
set -euo pipefail
CLANGD="${CLANGD_BIN:-$HOME/.platformio/packages/tool-clangd-esp/bin/clangd}"
PIO_PACKAGES="${PLATFORMIO_CORE_DIR:-$HOME/.platformio}/packages"
exec "$CLANGD" \
  --query-driver="$PIO_PACKAGES/toolchain-*/bin/*,$PIO_PACKAGES/tool-*/bin/*" \
  --background-index \
  --background-index-priority=low \
  --header-insertion=never \
  --completion-style=detailed \
  --pch-storage=memory \
  --limit-results=100 \
  "$@"
```

**VS Code workspace settings** (`.vscode/settings.json`):

```json
{
  "clangd.path": "${workspaceFolder}/scripts/clangd-wrapper.sh",
  "clangd.arguments": [],
  "clangd.onConfigChanged": "restart",
  "C_Cpp.intelliSenseEngine": "disabled",
  "editor.formatOnSave": true,
  "[c]": { "editor.defaultFormatter": "llvm-vs-code-extensions.vscode-clangd" },
  "[cpp]": { "editor.defaultFormatter": "llvm-vs-code-extensions.vscode-clangd" }
}
```

Do **not** set `--compile-commands-dir` globally in a multi-root workspace: it is a single global override and it disables per-project `.clangd` `CompilationDatabase` settings. Let clangd discover each project's database by ancestor search.

**Per-project `.clangd`** (generated into each homework, committed):

```yaml
CompileFlags:
  CompilationDatabase: .
  Remove:
    - -mlongcalls
    - -mtext-section-literals
    - -mdisable-hardware-atomics
    - -fno-tree-switch-conversion
    - -fno-shrink-wrap
    - -fstrict-volatile-bitfields
    - -fmacro-prefix-map=*
  Add:
    - -D__XTENSA__=1
Diagnostics:
  Suppress:
    - unknown-argument
    - drv_unknown_argument
```

Only add `-D__XTENSA__=1` if the chosen clangd still falls back to the host target. With esp-clangd it should not be necessary.

**Shared libraries** have no single owning project. Add `compile_flags.txt` to each shared library directory so clangd has a sane fallback:

```text
-std=c11
-Iinclude
-Wall
-Wextra
```

For `lib/arduino` and `lib/espidf`, a plain host command is wrong. Either generate a synthetic database from one representative homework, or accept degraded navigation in adapter code and document it.

### 2.4 Multi-root behavior and known limitation

vscode-clangd runs **one clangd server per VS Code window**, not one per workspace folder. Consequences:

- `compile_commands.json` is discovered by walking **ancestors of each opened file**. Per-project databases therefore work naturally.
- `--compile-commands-dir` accepts one directory and is global. Avoid it.
- The background index is workspace-global. Duplicate symbols across 30 projects (common names such as `setup`, `loop`, `init`, `state`) can produce wrong "Go to Definition" results. This is a long-standing upstream limitation; a multi-root PR (#810) has been open, and a third-party fork (Eclipse CDT Cloud) spawns one server per project.
- Mitigations:
  - Prefix shared-library symbols (`common_`, `port_`) and avoid generic global names in adapters.
  - Start with `--background-index`; if memory or collisions become a problem, set `Index: Background: Skip` in `.clangd` or use `--background-index=0`.
  - For a lesson that truly needs isolated indexing, open that homework folder as its own VS Code window.

### 2.5 Failure modes and fixes

| Symptom | Root cause | Fix |
|---|---|---|
| `'stdio.h' file not found`, wrong glibc headers | `--query-driver` did not match; bare compiler name used | Use absolute/glob paths; add toolchain `bin` to `PATH`; set `COMPILATIONDB_INCLUDE_TOOLCHAIN=True` |
| `unknown argument: '-mlongcalls'` / `-mtext-section-literals` | GCC-only Xtensa flags passed to clangd | `.clangd` `CompileFlags.Remove`; use esp-clangd |
| `unknown target triple 'xtensa-...'` | clangd older than LLVM 20 or Apple build without Xtensa | Install LLVM 21+ or esp-clangd |
| ESP32 intrinsics/headers parse incorrectly | Stock clang lacks Espressif extensions | Use `esp-clang` / `tool-clangd-esp` |
| Missing Arduino library headers (`Wire.h`, `SPI.h`) | PlatformIO CDB omitted framework include paths (known issue class) | Upgrade PlatformIO; verify `COMPILATIONDB_INCLUDE_TOOLCHAIN`; regenerate after `pio pkg install` |
| Wrong completions after changing `platformio.ini` | Stale `compile_commands.json` | Rerun `pio run -t compiledb`; `clangd.onConfigChanged: restart` |
| Go to Definition lands in another homework | Global index + duplicate symbols | Prefix symbols; disable background index for the workspace |
| High CPU/memory with 30 projects open | Background indexing everything | `--background-index-priority=low`; open fewer folders; `Index: Background: Skip` |
| `--query-driver` works for ARM but not Xtensa | Different toolchain package names | Glob both `toolchain-*/bin/*` and `tool-*/bin/*` |
| `uint32_t` format warnings | GCC vs Clang disagree on Xtensa integer types | Define `__INT32_TYPE__`/`__UINT32_TYPE__` or suppress the diagnostic |

### 2.6 What NOT to use

- **Apple `/usr/bin/clangd` for ESP32.** It lacks the Xtensa/Espressif extensions.
- **`--compile-commands-dir` in a multi-root workspace.** It is a global override and disables `.clangd` databases.
- **cpptools as the primary engine.** Proprietary, heavier, and it competes with clangd.
- **`compile_commands.json` committed to git.** Stale and machine-specific.
- **`--query-driver='**'`.** It allows clangd to execute arbitrary binaries. Use explicit toolchain globs.

---

## 3. Simulation and Wiring

### 3.1 Decision summary

| Role | Tool | Why |
|---|---|---|
| Primary simulation + wiring source of truth | **Wokwi** | Best ESP32/AVR fidelity, `diagram.json`, mature headless CLI, scenarios, screenshots, custom chips |
| Self-hosted/offline fallback | **Velxio** (Docker) | AGPL, real QEMU for ESP32, AVR/RP2040 in browser, good canvas, but no STM32 self-host and paid hosted CI |
| STM32 headless firmware tests | **Renode** | MIT, headless Robot Framework, STM32F103/F4 platforms, CI action |
| Report illustrations only | **Fritzing** | Familiar breadboard art, but not a simulator and licensing restricts graphic reuse |
| Not recommended | **QEMU directly** | STM32 machines lack GPIO/I2C/DMA; unsuitable for this course |

### 3.2 Velxio

**Repository:** `davidmonterocrespo24/velxio` — created 2026-03-03, 3,454 stars, 2,113 commits, last push 2026-10-20, 14 open issues. Very active, but young and with inconsistent documentation (README says "40 boards", GitHub description says "19 real boards").

**Architecture:** Browser IDE (Monaco + canvas) with a split execution model. AVR and RP2040 run client-side via `avr8js` / `rp2040js`. ESP32, STM32, and Raspberry Pi Linux run QEMU on a Python/FastAPI backend, streaming GPIO/UART/I2C/SPI over WebSocket. ESP32 uses a QEMU 8.1.3 fork (`picsimlab-esp32`); ESP32-C3 uses a RISC-V backend. Docker packages QEMU libraries and toolchains.

**License:** **AGPLv3** for personal/educational/open-source use, with a **commercial license** for proprietary or SaaS use. Contributors sign a CLA. Network deployment of a modified version triggers AGPL source-offer obligations. For a public MIT course repository, running an unmodified self-hosted instance is fine, but **embedding or modifying Velxio in a way that serves it to users requires legal care**. Do not copy Velxio code into the repository.

**Self-hosting:**

- Prebuilt Docker image: `ghcr.io/davidmonterocrespo24/velxio:master`, port 3080, ~30 s pull, five named volumes for SQLite, Arduino cores, ccache, ESP-IDF builds.
- Docker Compose build: ~10–15 min first time, cached afterward.
- Manual: Node 18+, Python 3.12+, `arduino-cli`; browser boards only unless QEMU/ESP-IDF is wired manually.
- **Critical limitation:** the self-hosted image ships **AVR, RP2040, and ESP32 only**. STM32, Raspberry Pi Linux, ESP32-C6, and branded boards are online-only (STM32 and Pi also require Velxio Desktop with a paid plan). The README explicitly says STM32 needs licensed emulator binaries and multi-GB boot images.

**Supported frameworks:** Arduino C++ (AVR, RP2040, ESP32, STM32-hosted), MicroPython (RP2040, ESP32), ESP-IDF (ESP32 self-hosted), Python (Pi Linux hosted).

**Wiring visualization:** circuit canvas with board/component SVGs, live component picker, SPICE-based electrical layer showing currents/voltages/shorts, oscilloscope at ~8 ns GPIO timestamp resolution.

**Components:** 150+ interactive components (displays, sensors, motors, logic ICs, analog parts, breadboards). Custom chips can be written in C and compiled to WebAssembly.

**Serial:** Serial Monitor with UART output/input; ESP32 QEMU serial streaming; MicroPython REPL. CI has `--serial-log-file`.

**Headless/CI:** `velxio-cli` (install script), `velxio.toml` + Wokwi-compatible `diagram.json`, `velxio-cli run --expect-text ... --timeout ...`, YAML scenarios (`delay`, `wait-serial`, `write-serial`, `expect-pin`, `set-control`, `take-screenshot`), `velxio-cli lint`. GitHub Action `velxio/velxio-ci-action@v1`.

**CI cost/limits:** CI is a **paid, hosted** feature. Free has no CI. Maker has 200 simulated minutes/month, 1 concurrent job, 5 min/run. Pro has 2,000 min/month, 2 concurrent jobs, 10 min/run. No documented self-hosted CI runner. The CLI requires `velxio-cli login` and a token.

**MkDocs embedding:** no documented iframe/embed API. Link to `velxio.dev` or a self-hosted URL. Velxio's own docs are Astro Starlight, not MkDocs.

**Maintenance:** very active, but the project is only ~7 months old and its docs disagree on board counts and core versions. Treat it as promising but not yet a stable long-term dependency.

### 3.3 Wokwi

**What it is:** a mature hosted simulator with a local CLI and VS Code extension. The CLI is MIT-licensed; the simulation service is proprietary.

**`diagram.json` format:** version 1, with `parts` and `connections`. Each part has `id`, `type`, optional `left`/`top`, `attrs`, `rotate`, `hide`. Each connection is `["source:pin", "target:pin", "color", [wireInstructions]]`; the fourth element uses `v<px>` / `h<px>` and a single `*` separator. `wokwi-cli lint` validates unknown part types, invalid pins, duplicate IDs.

**Supported boards (relevant subset):** `board-esp32-devkit-c-v4`, `wokwi-esp32-devkit-v1`, `board-esp32-s3-devkitc-1`, `board-esp32-c3-devkitm-1`, `board-esp32-c6-devkitc-1`, `wokwi-arduino-nano`, `wokwi-arduino-uno`, `wokwi-arduino-mega`, `wokwi-attiny85`, `wokwi-pi-pico`, `board-pi-pico-w`, plus STM32 `board-st-nucleo-c031c6`, `board-st-nucleo-l031k6`, and Blue Pill (STM32F103C8).

**Frameworks:** Arduino core projects, **ESP-IDF projects**, MicroPython/CircuitPython, Rust, and custom firmware (`.bin`, `.elf`, `.uf2`).

**Fidelity:**

- ESP32/S3/C3/C6: WiFi simulated; **Bluetooth not simulated**; I2C master-only; I2S partial; TWAI partial; USB Serial+JTAG simulated without JTAG; MCPWM not implemented; RTC only pull resistors; ULP unavailable on ESP32/S3.
- CPU speed is capped near 8 MHz by default for simulation speed; this affects instruction execution, not peripheral timing. Override with `cpuFrequency`.
- Flash/PSRAM size and type are configurable.
- STM32: Blue Pill and two Nucleo boards. DMA is **not implemented**; RTC/IWDG/LPTIM/LPUART/comparator/PWR/sleep are missing; SPI is slow without DMA. Only suitable for simple lessons.

**PlatformIO/ESP-IDF integration:**

```toml
# wokwi.toml — PlatformIO Arduino
[wokwi]
version = 1
firmware = '.pio/build/esp32s3/firmware.bin'
elf = '.pio/build/esp32s3/firmware.elf'
```

For `framework = espidf` under PlatformIO, **do not point `firmware` at PlatformIO's `flasher_args.json`** — its paths (`bootloader/bootloader.bin`, `partition_table/partition-table.bin`) do not match PlatformIO's output layout. Merge the images with esptool `merge_bin` into `firmware.merged.bin` (a `merge_firmware.py` extra script) or write a corrected `flasher_args.json`. Use the merged image when custom partitions, filesystems, OTA, or >4 MB flash matter.

**CLI (v0.29.0, 2026-10-19):**

- Install: `curl -L https://wokwi.com/ci/install.sh | sh`.
- Auth: `WOKWI_CLI_TOKEN` (`wok_...`).
- Run: `wokwi-cli <project-dir>`, default 30 s.
- Assertions: `--expect-text`, `--fail-text`, `--scenario`, `--timeout`, `--timeout-exit-code`.
- Evidence: `--screenshot-part`, `--screenshot-time`, `--screenshot-file`, `--vcd-file`, `--coverage-file`.
- Other: `--heap-min-free`, `--heap-csv`, `--sdcard`, GDB server, `wokwi-cli chip compile`, `wokwi-cli lint`, experimental MCP server.
- Custom chips: C API compiled to WASM; register in `wokwi.toml` with `[[chip]]`; reference as `chip-<name>` in `diagram.json`.

**CI cost/limits:** rolling 30-day quota: Free 50 min, Hobby 200, Hobby+ 500, Pro 2,000. Per-session wall clock: 5 min Free/Hobby, 10 min Hobby+, 50 min Pro. Firmware is uploaded to the cloud, not stored, deleted after simulation. On-premise deployment is available on request. The pricing page does not list CI minutes for Community; the docs do. Verify before relying on the free tier.

**VS Code / offline:** the extension works online by default. **Offline mode is a Pro feature**; the engine is cached after an online run. Air-gapped custom packages are available on request.

**Embedding:** only an experimental/alpha endpoint (`https://wokwi.com/_alpha/wembed/<project-id>`) and prototype repos. Not officially supported. Do not make it a documentation dependency.

**License:** Wokwi service is proprietary; free for open-source/personal use, commercial use requires a Pro plan or commercial license. The CLI itself is MIT.

**Maintenance:** mature and active (`wokwi-cli` pushed 2026-10-20).

### 3.4 Fritzing

**Version:** 1.0.8 (2026-08-12).

**Format:** `.fzz` is a ZIP containing `sketch.fz` (XML) plus optional custom parts (`.fzp` + SVG) and code. Views: breadboard, schematic, PCB. Wires carry `x1/y1/x2/y2` and `wireFlags`. The XML references parts by `moduleIdRef`, not by embedding them.

**License:** application is **GPLv3**; documentation and part designs/breadboard graphics are **CC BY-SA 3.0**. Fritzing explicitly says it does **not** allow use of Fritzing part graphics in other software systems without permission. Your own circuits are yours, but published images should be attributed ("created with Fritzing").

**Headless/export:** the CLI supports `-svg FOLDER` (export all sketches in a folder to SVGs of all views) and `-gerber FOLDER`. It is a Qt GUI application, so headless CI needs `QT_QPA_PLATFORM=offscreen` or `xvfb`. There is no stable per-file export API. Batch folder export is the usable path.

**Git-friendliness:** poor. `.fzz` is a binary ZIP; diffs are opaque. Generated SVGs are text and diffable, but they are outputs, not sources.

**Verdict:** optional report illustration only. Do not make `.fzz` the source of truth. Manual export is acceptable for 30 reports; automated Fritzing in CI is not worth the complexity.

### 3.5 Renode and QEMU for STM32

**Renode 1.17.0 (2026-09-07), MIT license.** Actively maintained by Antmicro. STM32 support includes `stm32f103` (Blue Pill), `stm32f4` / `stm32f4_discovery`, `stm32f412`, `stm32f429`, with `.repl` platform descriptions covering GPIO, USART, I2C, SPI, timers, DMA, ADC, CAN, Ethernet. Headless CI is first-class:

- `renode-test` runs Robot Framework `.robot` files, emits `robot_output.xml`, `log.html`, `report.html`.
- `RENODE_CI_MODE=YES` for non-interactive CI; `-j` parallel; `-P` port pinning.
- `antmicro/renode-test-action@v4` GitHub Action.
- Supports UART/GPIO assertions, sensor injection, GDB, tracing.

Limitations: no wiring visualization, no ESP32/AVR, and the exact STM32 model must exist (or be written as `.repl`). If the course's STM32 boards are not F103/F4-class, Renode may not have a ready platform.

**QEMU (10.x):** STM32 machines are `stm32vldiscovery`, `netduino2`, `netduinoplus2`, `olimex-stm32-h405`, `b-l475e-iot01a`. Supported peripherals are core, ADC, EXTI, USART, SPI, SYSCFG, timers, and limited RCC. **GPIO, I2C, DMA, USB, CAN, DAC, RTC, SDIO are missing.** QEMU is therefore not viable for this course's STM32 lessons. It remains useful only as the engine inside Velxio.

### 3.6 Comparison matrix

| Criterion | Velxio | Wokwi | Fritzing | Renode | QEMU direct |
|---|---|---|---|---|---|
| Simulation fidelity | High for ESP32/AVR/RP2040 (real QEMU/browser cores); STM32 only hosted | High for ESP32/AVR; medium for 3 STM32 boards (no DMA) | None — design tool, not simulator | High for supported Cortex-M (STM32F103/F4) | Low for STM32 (no GPIO/I2C/DMA) |
| Wiring visualization | High — canvas, SPICE currents/voltages/shorts, oscilloscope | High — `diagram.json`, large part library, clean rendering | High — breadboard illustrations, manual layout | None — text/GPIO traces | None |
| Self-host / offline | Yes, Docker; **AVR/RP2040/ESP32 only** | No; offline VS Code only with Pro; on-prem on request | Yes, desktop offline | Yes, fully offline/headless | Yes |
| CI / headless | Hosted CLI + Action; **paid**; no self-host CI | Mature CLI + scenarios + screenshots/VCD/coverage; cloud | Weak: `-svg FOLDER`, Qt display needed | Excellent: `renode-test` + Robot + GH Action | Possible but bespoke |
| License | AGPLv3 + commercial; CLA | Service proprietary; CLI MIT; free for OSS, commercial needs Pro | GPLv3 app; parts CC BY-SA 3.0; graphic reuse restricted | MIT | GPLv2 |
| Setup effort | Low (Docker) to medium (CI account) | Low | Medium/high (manual drawing) | High (platform scripts, Robot tests) | High |
| MkDocs embedding | No documented embed; link out | Alpha iframe only; not supported | Export SVG/PNG, embed as image | Screenshots/logs only | None |
| Multi-platform | ESP32 Arduino/IDF, AVR, RP2040 self-host; STM32 hosted | ESP32 (best), AVR, RP2040, 3 STM32 boards | Any board with a part; no simulation | STM32/Cortex-M only | Limited STM32 |
| Custom components | C → WASM chips | C → WASM chips | Parts editor (license care) | `.repl` platform models | Device models in C |
| Maintenance | Very active, young (Mar 2026), docs inconsistent | Mature, active | Active (1.0.8, Aug 2026) | Active (1.17.0, Sep 2026) | Active |
| Cost | Free self-host; CI paid (Maker/Pro) | Free OSS tier; CI paid above 50 min/30 d | Free/paid download tiers | Free | Free |
| Best role | Offline/self-hosted ESP32 demo fallback | **Primary simulator and wiring source of truth** | Optional report illustration | STM32 headless tests | Not recommended |

### 3.7 CI budget math (why "nightly full matrix on free tiers" fails)

Assume 30 homeworks and ~30 s of simulated time each:

- One full simulation pass = ~15 minutes.
- Nightly for 30 days = ~450 minutes per 30-day window.
- Wokwi: Free 50 min → 3 full passes/month; Hobby+ 500 min → one nightly pass fits, barely; Pro 2,000 min → comfortable.
- Velxio: Free 0 CI; Maker 200 min → ~13 full passes/month; Pro 2,000 min → comfortable.

Therefore:

- On pull requests: simulate **only changed homeworks** (typically 1–3) — ~1.5 min per PR. Fits the free tier.
- Nightly: full simulation matrix only on a paid tier, or run a rotating subset on free.
- Keep simulation scenarios short (assert one serial line, one GPIO state, one screenshot) and set explicit timeouts.

### 3.8 Licensing implications

- **Velxio AGPLv3:** self-hosting unmodified is fine. If the repository publishes a modified Velxio or offers it as a network service, AGPL source obligations apply. Keep Velxio at arm's length: a Docker image reference in a script, not vendored code. The public course repository remains MIT.
- **Wokwi:** free tier is for open-source/personal use. This repository is public and MIT, so it qualifies. Commercial use or extensive CI requires Pro. Do not assume unlimited CI on the free tier.
- **Fritzing parts:** CC BY-SA 3.0 and an explicit restriction on reusing part graphics in other software. Do not copy Fritzing part SVGs into the docs site. Use Fritzing only to produce final images, with attribution, or avoid it.
- **Renode MIT:** safe to use and script in CI.

### 3.9 Spike plan and pass/fail criteria

Run the spike before committing the roadmap to a simulator. Suggested homework: 1.3 Police Flasher, plus one ESP-IDF project and one STM32 project if available.

| Spike check | Pass criteria |
|---|---|
| Wokwi: ESP32-S3 N16R8 Arduino build | Correct flash/PSRAM; LED pattern visible; serial assertion passes |
| Wokwi: ESP-IDF project via PlatformIO | Merged image boots; serial output correct; no `flasher_args.json` path errors |
| Wokwi CLI in GitHub Actions | `--expect-text` passes; screenshot artifact uploaded; measured minutes recorded |
| Wokwi: STM32 board (if it matches Blue Pill/Nucleo) | GPIO/UART work; document missing DMA/peripherals |
| Velxio Docker self-host | Boots in <5 min; ESP32 Arduino and ESP-IDF compile/run; serial works; no STM32 |
| Velxio CLI | `lint` works offline; `run --expect-text` works with a paid token; minutes measured |
| Fritzing headless | `-svg FOLDER` works under `xvfb`; output quality acceptable; license note written |
| Renode | The actual STM32 board has a matching `.repl`/`.resc`; a Robot test asserts UART/GPIO |
| MkDocs embedding | Wokwi alpha iframe or Velxio link renders acceptably; if not, use screenshots |

Decision rule: Wokwi wins the primary role unless the spike shows a blocking ESP-IDF/PlatformIO problem or unacceptable CI cost. Velxio is the fallback only for offline/self-hosted ESP32/AVR/RP2040. Renode is adopted only for STM32 if a matching platform exists; otherwise STM32 evidence is unit tests plus HIL.

### 3.10 `diagram.json` as the wiring contract

Use Wokwi's `diagram.json` as the single source of truth in `assets/diagram.json`:

- It is versioned (`"version": 1`), diffable JSON.
- It is understood by Wokwi and Velxio (Velxio explicitly accepts Wokwi diagrams).
- `wokwi-cli lint` / `velxio-cli lint` validate it in CI.
- Fritzing can be used to produce a prettier final illustration, but the `.fzz` is not the source.

Add a small `assets/wiring.md` generated from `diagram.json` (netlist table: component, pin, net, color) so reports contain a textual, reviewable wiring description even if the simulator changes.

---

## 4. Pinout Diagrams

### 4.1 License reality

| Source | License | Can you redistribute? |
|---|---|---|
| Arduino pinout PDFs and board designs | CC BY-SA 4.0 | Yes, with attribution + ShareAlike; do not use the Arduino trademark |
| Arduino documentation content | CC BY 4.0 (docs-content repo) | Yes, with attribution |
| Espressif datasheets, TRMs, DevKitC user guides | "All rights reserved"; no license granted | **No** — link only |
| ST datasheets and Nucleo user manuals | Proprietary | **No** — link only |
| PlatformIO board manifests (`platform-espressif32`, `platform-ststm32`) | Apache 2.0 | Yes (facts/JSON) |
| KiCad symbol/footprint libraries | CC BY-SA 4.0 with exception | Yes, with attribution; exception covers designs |
| Zephyr devicetree | Apache 2.0 | Yes |

Practical rule:

- **Link** Espressif and ST pinouts in `docs/boards/*.md`, with a note in `docs/sources.md`.
- **Embed** Arduino pinouts only if the page carries the CC BY-SA 4.0 attribution and a link to the license. Keep them in a clearly marked section so ShareAlike does not blur into the rest of the site.
- **Generate your own SVG** for ESP32-S3, STM32, and any board where the vendor image is proprietary. Pin facts (which GPIO is on which header pin) are not copyrightable; the drawing is.

### 4.2 Data sources for board profiles

1. **PlatformIO board manifests** — MCU, flash, RAM, upload speed, framework support. Apache 2.0.
2. **Vendor datasheets / DevKit user guides** — pin tables, strapping pins, ADC limits, current limits. Read and transcribe facts; do not copy figures.
3. **KiCad symbol libraries** — pin numbers and names for the package.
4. **Zephyr devicetree** — SoC pin mux and alternate functions.
5. **Board silkscreen / official pinout PDFs** — cross-check.

Store the result as `boards/<board>.yaml` (or `docs/boards/data/<board>.yaml`):

```yaml
id: esp32-s3-devkitc-1-n16r8
name: ESP32-S3-DevKitC-1 (N16R8)
mcu: ESP32-S3
flash: 16MB
psram: 8MB
headers:
  left:
    - pin: "1"
      gpio: "3V3"
      type: power
    - pin: "2"
      gpio: "GPIO4"
      functions: [ADC1_CH3, TOUCH4]
  right:
    - pin: "1"
      gpio: "GND"
      type: ground
```

### 4.3 Recommended generator

**Repo-owned, deterministic generator:**

- `scripts/gen_pinout.py` reads `boards/<board>.yaml`, validates it against a JSON Schema, and renders `docs/assets/pinouts/<board>.svg` from a Jinja2 template.
- Commit the SVG. CI regenerates and fails on drift (`git diff --exit-code`).
- The SVG can carry `data-gpio` and `data-function` attributes for search/tooltips.
- No external service, no license entanglement, no network in CI.

**Optional wiring illustration:** PinViz (MIT, Python, YAML/JSON → SVG, built-in ESP32-S3-DevKitC-1 and ESP32 DevKit V1 boards, v0.20.0 in Oct 2026). It is useful for wiring diagrams, but it is a very young project (5 stars, one primary maintainer). Pin it, commit its output, and do not make it a build-time dependency.

**What NOT to do:**

- Do not scrape and commit vendor pinout images.
- Do not embed Fritzing part SVGs (license restriction).
- Do not depend on a single-maintainer pinout library at build time; generate and commit.
- Do not hand-edit generated SVGs without updating the YAML; drift will be caught by CI.

---

## 5. Documentation

### 5.1 MkDocs Material status

- Current: **9.7.7** (2026-07-17), a security patch.
- **Maintenance mode** since 9.7.0 (2025-11-11). Only critical fixes and security updates.
- **End of life: 2027-05-05.**
- 9.7.5 pins `mkdocs<2`; MkDocs 2.0 is not supported.
- The team's successor is **Zensical**: still **0.0.71** (2026-10-16), with 0.1.0 announced for 2026-11-05. It reads `mkdocs.yml`, supports `modern`/`classic` themes, and is MIT. `hooks` remains unsupported.

**Decision:** use MkDocs Material 9.7.7 for the first milestone. It is stable, documented, and has the features this repository needs. Keep the configuration Zensical-compatible:

- No `hooks:`.
- Only plugins that Zensical supports or that can be dropped (search, tags). Avoid `mkdocs-monorepo-plugin`, `mkdocs-macros`, `mkdocs-awesome-pages`.
- Generate navigation with a script rather than a plugin.
- Write a short ADR: "MkDocs Material now, evaluate Zensical 0.1.x at the next milestone boundary." Revisit in Q1 2027, before the May 2027 EOL.

### 5.2 `requirements-docs.txt`

```text
mkdocs==1.6.1
mkdocs-material==9.7.7
pymdown-extensions==12.3
```

Pin exact versions. Do not use `mkdocs-material[imaging]` unless social cards are actually needed (it pulls Cairo and slows CI).

### 5.3 Configuration skeleton

```yaml
# mkdocs.base.yml
site_name: Embedded Engineering Homeworks
site_description: Course homeworks, reports, and evidence
theme:
  name: material
  features:
    - navigation.sections
    - navigation.indexes
    - navigation.top
    - content.code.copy
    - content.tabs.link
    - search.suggest
    - search.highlight
  palette:
    - scheme: default
      toggle: { icon: material/brightness-7, name: Switch to dark mode }
    - scheme: slate
      toggle: { icon: material/brightness-4, name: Switch to light mode }

markdown_extensions:
  - admonition
  - attr_list
  - def_list
  - footnotes
  - md_in_html
  - toc:
      permalink: true
  - pymdownx.details
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
  - pymdownx.tabbed:
      alternate_style: true
  - pymdownx.arithmatex:
      generic: true
  - pymdownx.highlight:
      anchor_linenums: true
      line_spans: __span
  - pymdownx.inlinehilite
  - pymdownx.snippets:
      base_path: ["."]
      check_paths: true
  - pymdownx.keys
  - pymdownx.tasklist:
      custom_checkbox: true

plugins:
  - search
```

`pymdownx.snippets` is the key feature for academic reports: include code and tables from files so the report and the code cannot drift.

### 5.4 Math

Use **KaTeX 0.19.0** with `pymdownx.arithmatex` (`generic: true`). KaTeX is faster than MathJax and covers the algebra, calculus, circuit equations, and statistics used in this course.

- Vendor `katex.min.js`, `katex.min.css`, `contrib/auto-render.min.js` under `docs/assets/vendor/katex/` so the site works offline and does not depend on a CDN. Register them via `extra_javascript` / `extra_css` in the generated MkDocs config.
- Re-render on Material's instant navigation:

```javascript
document$.subscribe(function () {
  renderMathInElement(document.body, {
    delimiters: [
      { left: "$$", right: "$$", display: true },
      { left: "$", right: "$", display: false },
      { left: "\\(", right: "\\)", display: false },
      { left: "\\[", right: "\\]", display: true }
    ]
  });
});
```

Use MathJax only if a lesson needs full LaTeX packages or MathML accessibility. Do not load both.

### 5.5 Mermaid

Material bundles Mermaid 11. Use fenced ```` ```mermaid ```` blocks with the `pymdownx.superfences` custom fence above. Do not add the Mermaid npm package or override the bundled version unless a specific diagram type requires it. Note that `mkdocs build --strict` does not validate Mermaid syntax; add a CI step only if diagrams become numerous.

### 5.6 Documentation generation pipeline

Do not use `mkdocs-monorepo-plugin` or a symlink farm. Generate a build tree deterministically:

1. `scripts/gen_docs.py` reads `homework.yaml` for every homework.
2. It creates `build/docs_src/`:
   - copies `docs/` (hand-written theory, boards, protocols, standards, decisions);
   - creates `homeworks/<module>_<lesson>-<name>.md` with front matter and an include of the report body;
   - copies `assets/` images and generated pinouts/SVGs;
   - writes `index.md` (course catalog) and `homeworks/index.md`.
3. It writes `build/mkdocs.yml` with `INHERIT: ../mkdocs.base.yml` and a generated `nav:` list.
4. `mkdocs build --strict -f build/mkdocs.yml` builds the site.

This keeps one source of truth (`homework.yaml` + `README.md`) and avoids plugin lock-in. It also gives the README index and the site the same metadata.

### 5.7 GitHub Pages deployment

Use artifact-based deployment, not `mkdocs gh-deploy`:

- `gh-deploy` pushes a `gh-pages` branch, bypassing the repository's protected-branch and PR conventions.
- Artifact deployment is auditable, uses OIDC, and does not create a branch.

```yaml
name: docs
on:
  push:
    branches: [main]
permissions:
  contents: read
  pages: write
  id-token: write
concurrency:
  group: pages
  cancel-in-progress: false
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
        with: { lfs: true }
      - uses: actions/setup-python@v7
        with:
          python-version: "3.13"
          cache: pip
          cache-dependency-path: requirements-docs.txt
      - run: pip install -r requirements-docs.txt
      - run: python scripts/gen_docs.py
      - run: mkdocs build --strict -f build/mkdocs.yml
      - uses: actions/upload-pages-artifact@v5
        with: { path: site }
  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - id: deployment
        uses: actions/deploy-pages@v5
```

Current action majors: `checkout@v7`, `setup-python@v7`, `cache@v6`, `configure-pages@v6`, `upload-pages-artifact@v5`, `deploy-pages@v5`.

### 5.8 What NOT to use

- **MkDocs 2.0** — Material 9.7.5+ pins `mkdocs<2`; 2.0 is not supported.
- **`mkdocs gh-deploy`** — bypasses branch protection and auditability.
- **MkDocs hooks and heavy plugins** — Zensical does not support hooks; plugins increase migration cost.
- **Social cards / `mkdocs-material[imaging]`** — Cairo dependency, slow CI, no value for this repository.
- **CDN-only math** — vendor KaTeX so the site is reproducible and offline-capable.
- **Zensical 0.0.x today** — too young for a public course repository; revisit after 0.1.x.
- **Committing generated `site/`** — build it in CI.

---

## 6. Quality Tooling

### 6.1 Tool versions

| Tool | Version | Role |
|---|---|---|
| clang-format | **23.1.3** | C/C++ formatting |
| clang-tidy | **23.1.3** | Static analysis (host-compiled code) |
| pre-commit | **4.7.0** | Hook runner, stages |
| pre-commit-hooks | **v6.0.0** | Trailing whitespace, EOF, YAML/JSON checks |
| mirrors-clang-format | **v23.1.3** | Pre-commit clang-format hook |
| ruff | **0.17.2** | Python lint/format for scripts |
| gitleaks | **8.30.1** | Secret scanning |
| markdownlint-cli2 | **0.24.0** | Markdown lint |
| yamllint | **1.38.0** | YAML lint |
| check-jsonschema | **0.38.2** | `homework.yaml` JSON Schema validation |
| ShellCheck | current | Shell scripts (optional but recommended) |
| actionlint | current | GitHub Actions workflow validation (optional) |

### 6.2 Three-layer model

| Layer | Trigger | Checks | Budget |
|---|---|---|---|
| Pre-commit | `git commit` | trailing whitespace, EOF, YAML/JSON parse, clang-format, ruff, markdownlint, yamllint, gitleaks, schema validation on changed `homework.yaml` | < 10 s |
| Pre-push | `git push` | clang-tidy on changed host-compiled C/C++ (`lib/common`, `lib/port`, native tests); native unit tests for changed libraries | < 2 min |
| CI | PR | All lint, schema, docs build, workspace/index drift, build changed projects, native tests, changed-homework simulation | < 15 min |
| CI nightly | Schedule | Full build matrix, full native test suite, full simulation matrix (paid tier) or rotating subset, link check, LFS audit | < 6 h |

Do not put clang-tidy in pre-commit. It needs a compilation database and is too slow for a commit hook.

### 6.3 clang-format: "ESP-IDF style" is AStyle-defined

Important correction: **ESP-IDF does not use clang-format.** The official style guide says ESP-IDF uses **AStyle**, configured by `tools/ci/astyle-rules.yml`. The rules that matter:

```
DATA_91b7d3f0_START
Use four spaces for each indentation level. Do not use tabs for indentation.
The maximum line length is 120 characters as long as it does not seriously affect the readability.
DATA_91b7d3f0_END
```

Function definitions put the brace on a separate line; control statements keep the brace on the same line. Naming: `snake_case` types ending in `_t`, `s_` prefix for static variables, `CamelCase` classes, `snake_case` methods.

Because the repository standardizes on clang-format, approximate ESP-IDF style with an explicit `.clang-format` and document the approximation in an ADR:

```yaml
# .clang-format
BasedOnStyle: LLVM
IndentWidth: 4
TabWidth: 4
UseTab: Never
ColumnLimit: 120
BreakBeforeBraces: Custom
BraceWrapping:
  AfterFunction: true
  AfterControlStatement: Never
  AfterClass: false
  AfterStruct: false
  AfterEnum: false
  AfterNamespace: false
  AfterUnion: false
  BeforeElse: false
  BeforeCatch: false
PointerAlignment: Right
DerivePointerAlignment: false
AccessModifierOffset: -4
AllowShortFunctionsOnASingleLine: Empty
AllowShortIfStatementsOnASingleLine: Never
AllowShortLoopsOnASingleLine: false
IndentCaseLabels: false
SpaceBeforeParens: ControlStatements
AlignConsecutiveAssignments: false
AlignConsecutiveDeclarations: false
```

Notes:

- Pin the clang-format **major.minor.patch** everywhere (pre-commit, CI, editor). Formatting changes between LLVM majors; an unpinned version produces churn.
- Do not run `clang-format` on third-party or vendored code.
- Use `git clang-format` for changed lines if full-file reformatting is too noisy during a lesson.
- If exact ESP-IDF compatibility matters more than clang-format, add an AStyle check as a separate CI job. Do not pretend clang-format is AStyle.

### 6.4 clang-tidy: scope and config

Run clang-tidy on **host-compiled code only**:

- `lib/common`, `lib/port`, `lib/host`.
- Native test builds.
- Not `lib/arduino` / `lib/espidf`, and not Xtensa firmware. Cross-target tidy with GCC-only flags is noisy and often wrong; the ESP-IDF toolchain's own `idf.py clang-check` is the upstream path but is not worth integrating into PlatformIO.

Recommended `.clang-tidy`:

```yaml
Checks: >
  -*,
  bugprone-*,
  cert-*,
  performance-*,
  portability-*,
  readability-*,
  clang-analyzer-*,
  -bugprone-easily-swappable-parameters,
  -bugprone-narrowing-conversions,
  -cert-err33-c,
  -readability-magic-numbers,
  -readability-identifier-length,
  -readability-function-cognitive-complexity

WarningsAsErrors: ""
HeaderFilterRegex: "^(lib|homeworks)/.*"
FormatStyle: file
CheckOptions:
  - key: readability-identifier-naming.StructCase
    value: lower_case
  - key: readability-identifier-naming.TypedefCase
    value: lower_case
  - key: readability-identifier-naming.TypedefSuffix
    value: _t
  - key: readability-identifier-naming.FunctionCase
    value: lower_case
  - key: readability-identifier-naming.GlobalVariablePrefix
    value: "g_"
  - key: readability-identifier-naming.StaticVariablePrefix
    value: "s_"
```

Run:

```bash
pio run -d homeworks/1_3-police-flasher -e native -t compiledb
clang-tidy -p homeworks/1_3-police-flasher \
  homeworks/1_3-police-flasher/src/*.c lib/common/src/*.c
```

Do not make `WarningsAsErrors` global at first. Start with warnings, fix the backlog, then promote a small set (`bugprone-*`, `clang-analyzer-*`) to errors.

### 6.5 `homework.yaml` validation

Use `check-jsonschema` with a schema in `schemas/homework.schema.json`:

```yaml
- repo: https://github.com/python-jsonschema/check-jsonschema
  rev: 0.38.2
  hooks:
    - id: check-jsonschema
      name: validate homework.yaml
      files: ^homeworks/[^/]+/homework\.yaml$
      args: ["--schemafile", "schemas/homework.schema.json"]
```

This is the cheapest way to keep 30+ metadata files consistent. Add cross-field rules (e.g., `framework: espidf` requires `language: c`) in the schema where possible; use a Python script for anything JSON Schema cannot express.

### 6.6 Pre-commit configuration skeleton

```yaml
default_stages: [pre-commit]
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v6.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-merge-conflict
      - id: check-added-large-files
        args: ["--maxkb=1024"]

  - repo: https://github.com/pre-commit/mirrors-clang-format
    rev: v23.1.3
    hooks:
      - id: clang-format
        types_or: [c, c++]

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.17.2
    hooks:
      - id: ruff-check
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.30.1
    hooks:
      - id: gitleaks

  - repo: https://github.com/DavidAnson/markdownlint-cli2
    rev: v0.24.0
    hooks:
      - id: markdownlint-cli2
        args: [--fix]

  - repo: https://github.com/adrienverge/yamllint
    rev: v1.38.0
    hooks:
      - id: yamllint
        args: [-c=.yamllint.yaml]

  - repo: https://github.com/python-jsonschema/check-jsonschema
    rev: 0.38.2
    hooks:
      - id: check-jsonschema
        files: ^homeworks/[^/]+/homework\.yaml$
        args: ["--schemafile", "schemas/homework.schema.json"]

  - repo: local
    hooks:
      - id: clang-tidy
        name: clang-tidy (host code)
        entry: scripts/hooks/clang_tidy_host.sh
        language: system
        files: ^(lib/(common|port|host)/.*\.(c|h)|homeworks/.*/test/.*\.c)$
        stages: [pre-push]
        pass_filenames: true
```

Notes:

- `stages: [pre-push]` is the current pre-commit 4.x syntax (not `push`).
- The gitleaks pre-commit hook scans staged changes. In CI, run `gitleaks git` for the full history (the old `protect`/`detect` subcommands were replaced by `git`/`dir`).
- `check-added-large-files --maxkb=1024` prevents accidental binary commits; LFS-tracked files are still caught by this hook, so add exceptions for intentional LFS paths.
- The local clang-tidy hook must generate/refresh the compilation database first, or fail with a clear message if it is missing.

### 6.7 CI shape

```yaml
jobs:
  lint:
    steps:
      - uses: actions/checkout@v7
        with: { lfs: false }
      - uses: actions/setup-python@v7
        with: { python-version: "3.13" }
      - run: pip install -r requirements-dev.txt
      - run: pre-commit run --all-files
      - run: python scripts/validate_metadata.py
      - run: python scripts/check_docs_drift.py

  build-changed:
    needs: lint
    steps:
      - uses: actions/checkout@v7
        with: { lfs: true }
      - uses: actions/cache@v6
        with:
          path: ~/.platformio/.cache
          key: ${{ runner.os }}-pio-${{ hashFiles('platformio.shared.ini') }}
          restore-keys: ${{ runner.os }}-pio-
      - run: pip install platformio==6.2.0
      - run: python scripts/changed_projects.py | xargs -I{} pio run -d {}

  test-native:
    steps:
      - run: pip install platformio==6.2.0
      - run: pio test -d tests -e native
```

Practical CI notes:

- `hashFiles('platformio.shared.ini')` is a better cache key than a single homework's `platformio.ini`; if you use version ranges, also hash a lock file or pin exact versions.
- Cache `~/.platformio/.cache` (official recommendation), not the entire `~/.platformio` (huge, stale).
- `actions/checkout` has `lfs: false` by default; set `lfs: true` only for jobs that need binary assets.
- Build changed projects with a path filter; do not run `pio run` over 30 projects on every PR.
- Run a nightly full matrix. ESP-IDF cold builds are minutes each; 30 projects will not fit a PR budget.

### 6.8 What NOT to use

- **clang-tidy as a hard gate on cross-target firmware.** GCC-only Xtensa flags and missing headers produce false positives.
- **Unpinned clang-format.** Version drift creates formatting churn.
- **`cppcheck` as the primary analyzer.** It is installed in some PlatformIO environments and is a useful second opinion, but clang-tidy has better C++ semantics and the project's agreed check set.
- **MISRA.** Explicitly out of scope; do not add `misra-cpp` checks.
- **Pre-commit hooks that build firmware.** Too slow and environment-dependent.
- **`WarningsAsErrors: '*'` at the start.** It will block the pilot on legacy noise.

---

## 7. Binary Assets

### 7.1 Git LFS quotas and behavior

| Item | Value |
|---|---|
| Free/Pro included storage | **10 GiB** |
| Free/Pro included bandwidth | **10 GiB/month** |
| Team/Enterprise | 250 GiB storage + 250 GiB bandwidth |
| Max LFS file size | 2 GB (Free/Pro), 4 GB (Team), 5 GB (Enterprise) |
| Over quota, budget $0 | LFS blocked for the rest of the month |
| Uploads | Count toward storage |
| Downloads / CI fetches | Count toward the repository owner's bandwidth |
| Forks / PRs | Count against the parent repository |
| GitHub Pages | **Git LFS is not supported** |

### 7.2 Recommended policy

Track with LFS only binaries that are large, non-diffable, and genuinely needed for reproducibility:

- `.fzz` (if Fritzing is used), `.pdf`, `.step`, `.stl`, `.zip`, firmware dumps (`.bin`, `.elf`) used as evidence, `.vcd` captures if large.
- Videos: **never commit**; link to YouTube/Drive.
- Screenshots: optimize to WebP/PNG under ~300 KB and commit as normal git objects. Do not put documentation images in LFS, because GitHub Pages cannot serve LFS content.
- SVGs: **not LFS**. They are text, diffable, and small.
- Generated pinouts and diagrams: normal git objects, committed.

Budget check: 30 homeworks × 20 MB of LFS assets = ~600 MB, well within 10 GiB. The risk is bandwidth, not storage: every CI job that checks out with `lfs: true` downloads the assets.

### 7.3 CI checkout implications

```yaml
- uses: actions/checkout@v7
  with:
    lfs: true          # only for jobs that need binary assets
```

- Lint, metadata, and docs-config jobs: `lfs: false` (default). They do not need binaries.
- Docs build and full firmware build: `lfs: true` only if the job actually reads LFS files.
- `GIT_LFS_SKIP_SMUDGE=1` for metadata-only checkouts.
- Avoid `git lfs pull` in a matrix job that runs 30 times; download once per job or use a shared artifact.

### 7.4 GitHub Pages implications

- Pages cannot serve LFS objects. Any image referenced by the docs site must be a normal git object.
- Pages limits: 1 GB recommended source repository, 1 GB max published site, **100 GB/month soft bandwidth**, 10 builds/hour soft limit (custom Actions workflows are not subject to the Jekyll build limit), 10-minute deployment timeout.
- Optimize images before committing. 30 reports with a few screenshots each can approach the 1 GB site limit if screenshots are uncompressed PNGs.

### 7.5 `.gitattributes` sketch

```gitattributes
*.fzz   filter=lfs diff=lfs merge=lfs -text
*.pdf   filter=lfs diff=lfs merge=lfs -text
*.step  filter=lfs diff=lfs merge=lfs -text
*.stl   filter=lfs diff=lfs merge=lfs -text
*.zip   filter=lfs diff=lfs merge=lfs -text
*.bin   filter=lfs diff=lfs merge=lfs -text
*.elf   filter=lfs diff=lfs merge=lfs -text
*.vcd   filter=lfs diff=lfs merge=lfs -text

*.svg   text eol=lf
*.md    text eol=lf
*.yaml  text eol=lf
*.yml   text eol=lf
*.json  text eol=lf
```

Do not add `*.png` to LFS globally. Use a size-based policy and review images before committing.

### 7.6 What NOT to do

- **Commit videos.** Link them.
- **Put docs images in LFS.** Pages cannot serve them.
- **Use LFS for SVG/Markdown/YAML/JSON.** You lose diffs and gain no benefit.
- **Cache LFS content in GitHub Actions artifacts across jobs.** It duplicates bandwidth and is usually slower than `lfs: true`.
- **Rely on the free 10 GiB bandwidth for a 30-project nightly matrix with `lfs: true`.** Measure and scope.

---

## 8. Version Compatibility Matrix

| Package A | Compatible with | Notes |
|---|---|---|
| PlatformIO Core 6.2.0 | Python >= 3.9 | Python 3.13.13 works locally; 3.12/3.11 are safe CI choices |
| `platformio/espressif32` 8.0.0 | PlatformIO Core 6.2.0 | Released 2026-10-19; smoke-test before scaling |
| espressif32 8.0.0 | Arduino core 3.3.12 / ESP-IDF 5.5.5 | Arduino 3.x has breaking Bluetooth/API changes |
| espressif32 8.0.0 | ESP-IDF 6.1 (`framework = espidf`) | Different IDF version from the Arduino core's embedded IDF |
| `platformio/ststm32` 20.0.0 | PlatformIO Core 6.2.0 | Frameworks: arduino, stm32cube, cmsis, libopencm3, mbed, spl, zephyr |
| `symlink://` libraries | PlatformIO 6.0+ | Replaces `lib_extra_dirs` (deprecated, removal in next major) |
| clangd 21.x | LLVM 20+ Xtensa target | Stock clangd lacks Espressif `-mcpu=esp32s3` extensions |
| esp-clangd 19/21 (Espressif) | ESP-IDF 5.x/6.x | Best ESP32 IntelliSense; also handles ARM |
| clang-format 23.1.3 | clang-tidy 23.1.3 | Keep the same LLVM major for formatting and analysis |
| MkDocs Material 9.7.7 | MkDocs 1.6.1 (< 2.0) | Material pins `mkdocs<2`; do not upgrade to MkDocs 2.0 |
| MkDocs Material 9.7.7 | pymdown-extensions 12.3 | Mermaid/arithmatex/superfences verified in the docs |
| Zensical 0.0.71 | `mkdocs.yml` (mostly) | Hooks unsupported; 0.1.0 announced 2026-11-05 |
| KaTeX 0.19.0 | `pymdownx.arithmatex` generic mode | Vendor assets; do not rely on a CDN |
| markdownlint-cli2 0.24.0 | Node 22/24/26 | Node 26.7.0 works locally |
| Git LFS | GitHub Free | 10 GiB storage + 10 GiB/month bandwidth; no Pages support |

---

## 9. Alternatives Considered

| Category | Recommended | Alternative | When the alternative makes sense |
|---|---|---|---|
| Build system | PlatformIO 6.2 + espressif32 8.0.0 | Native `idf.py` | Only for portability documentation, not the primary path (explicitly out of scope) |
| ESP32 platform | Official `platformio/espressif32` 8.0.0 | pioarduino fork | If official 8.0.0 has a blocking regression, or exotic C2/C61 targets are needed |
| Shared libraries | `lib_deps = symlink://` | `lib_extra_dirs` | Never for new work; it is deprecated |
| Shared config | `extra_configs` + `extends` | Duplicate every `platformio.ini` | Only for one-off homework with unusual flags |
| LSP | clangd (esp-clangd) | cpptools | A student already standardized on cpptools and disabled clangd; not the repository default |
| Primary simulator | Wokwi | Velxio | Offline/self-hosted requirement dominates, and STM32 is not needed in simulation |
| STM32 simulation | Renode | Wokwi STM32 boards | The board matches Blue Pill or Nucleo-C031/L031 |
| Wiring art | `diagram.json` + generated SVG | Fritzing | A specific report needs Fritzing's visual style and the license is respected |
| Docs | MkDocs Material 9.7.7 | Zensical 0.1.x | After 0.1.x stabilizes, or when Material EOL forces migration |
| Math | KaTeX | MathJax | Full LaTeX package support or MathML accessibility is required |
| Pinouts | Repo-owned YAML → SVG | PinViz | Wiring illustrations are needed and PinViz supports the board |
| Binary assets | Selective LFS | Plain git | Assets are small and diffable (SVG, optimized PNG) |

---

## 10. What NOT to Use (summary)

| Avoid | Why | Use instead |
|---|---|---|
| `lib_extra_dirs` | Deprecated since 6.0; removal in next major; no warning in 6.2.0 | `lib_deps = name=symlink://../../lib/name` |
| `platform = espressif32 @ ^6` | Arduino 2.0.17 / old IDF; misses Arduino 3.x | `espressif32@8.0.0` (or pioarduino if needed) |
| Apple clangd for ESP32 | No Xtensa/Espressif extensions | Espressif `esp-clang` / `tool-clangd-esp` |
| `--compile-commands-dir` in multi-root | Global override; disables `.clangd` databases | Nearest-ancestor CDB + per-project `.clangd` |
| `--query-driver='**'` | Executes arbitrary binaries | Explicit toolchain globs |
| Committing `compile_commands.json` | Stale, absolute paths, large | Generate locally/CI |
| Velxio self-host for STM32 | Not in the OSS image; needs licensed binaries | Wokwi STM32 (3 boards) or Renode |
| Velxio CI on the free tier | CI is paid; no self-host CI | Wokwi free tier for changed-only, or paid Velxio |
| Wokwi for Bluetooth lessons | Bluetooth not simulated | HIL or a different simulator; document the gap |
| QEMU direct for STM32 | No GPIO/I2C/DMA | Renode |
| Fritzing `.fzz` as source of truth | Binary ZIP, manual GUI export, graphic license restrictions | `diagram.json` + generated SVG |
| Embedding vendor pinout images | Espressif/ST reserve all rights | Link, or generate your own SVG |
| MkDocs 2.0 | Material 9.7.5+ pins `<2` | `mkdocs==1.6.1` |
| MkDocs hooks / heavy plugins | Zensical migration blocker | Scripts + base config |
| `mkdocs gh-deploy` | Bypasses branch protection/audit | `upload-pages-artifact` + `deploy-pages` |
| LFS for docs images | Pages cannot serve LFS | Normal git objects, optimized |
| LFS for SVG/text | Loses diffs | Plain git |
| Videos in git | Repository bloat | Link externally |
| clang-tidy on cross-target firmware as a hard gate | False positives from GCC-only flags | Host-compiled code only |
| Unpinned clang-format | Formatting churn across LLVM versions | Pin 23.1.3 everywhere |
| MISRA | Out of scope, heavy | ESP-IDF style + clang-tidy |

---

## 11. Stack Patterns by Variant

**If the homework is Arduino on ESP32:**
- Use `framework = arduino`, `platform = espressif32@8.0.0`, the N16R8 overrides, and Wokwi for simulation.
- Because Arduino 3.x is the current official core and Wokwi's ESP32 fidelity is the best available.

**If the homework is ESP-IDF:**
- Use a separate environment/project with `framework = espidf`, `sdkconfig.defaults`, and the merged-firmware path for Wokwi.
- Because PlatformIO remains the build system, but ESP-IDF has different configuration and slower builds.

**If the homework is STM32:**
- Use `framework = stm32cube` (or `arduino` if the lesson is Arduino-based); simulate with Renode if the board is F103/F4-class, or Wokwi if it is a Nucleo-C031/L031/Blue Pill.
- Because the course boards are unconfirmed; do not commit to one STM32 simulator before the spike.

**If the homework is pure logic:**
- Use `platform = native`, Unity, and TDD; no simulator is required.
- Because native tests are faster and deterministic, and simulation adds no value for pure functions.

**If hardware is available:**
- Add HIL evidence (scope/multimeter measurements) and keep the simulator as a regression check.
- Because simulation cannot prove electrical behavior.

---

## 12. Open Questions / Spike Items

1. **PlatformIO 8.0.0 stability.** It is four days old. Validate Arduino 3.3.12 and ESP-IDF 6.1 on the actual ESP32-S3 N16R8 before scaffolding 30 projects. Decide the fallback (7.x vs pioarduino) if a blocker appears.
2. **ESP-IDF `compiledb` completeness.** The local validation was blocked by a broken ESP-IDF Python environment (`idf_component_manager` missing), not by PlatformIO. Run the spike on a clean machine and verify that component include paths, `sdkconfig` defines, and generated headers appear in `compile_commands.json`.
3. **Which clangd binary ships in the onboarding guide.** Decide between `esp-clang` (installed via ESP-IDF tools) and `tool-clangd-esp` (pioarduino package). The wrapper script makes this swappable, but the guide must name one.
4. **Wokwi ESP-IDF full-image workflow.** Validate `merge_firmware.py` (esptool `merge_bin`) with the N16R8 16 MB layout, custom partitions, and PSRAM. Confirm that Wokwi honors `flashSize`/`psramSize`.
5. **Wokwi CI minutes on the real workload.** Measure a 1.3 simulation and a more complex lesson. Decide between free (changed-only), Hobby+ (nightly), or Pro.
6. **Velxio self-host viability.** Measure Docker cold start, ESP-IDF compile time, serial reliability, and whether the AGPL obligations are acceptable for the intended deployment (local only vs. shared).
7. **STM32 board identity.** The course's STM32 models are unconfirmed. If they are not F103/F4-class, Renode may lack a platform and Wokwi may lack a board; STM32 simulation then falls back to HIL.
8. **Pinout generator scope.** Decide how many boards need custom YAML (ESP32-S3-DevKitC-1 N16R8, Arduino Nano, STM32 variants) and whether PinViz is worth adopting for wiring illustrations.
9. **MkDocs → Zensical migration timing.** Re-evaluate after Zensical 0.1.x ships (announced 2026-11-05). Set a hard decision date before 2027-05-05 (Material EOL).
10. **LFS policy numbers.** Set concrete limits (max file size, total budget) and enforce them in CI. Measure LFS bandwidth from the first month of nightly builds.

---

## 13. Roadmap Implications

1. **Phase 0 — Toolchain truth.** Pin PlatformIO 6.2.0 and espressif32 8.0.0; validate the N16R8 config (flash/PSRAM/partitions); replace `lib_extra_dirs` with `symlink://`; validate native Unity tests and `compiledb`. This phase resolves the three assumptions in `PROJECT.md` that are now outdated.
2. **Phase 1 — Repository skeleton and docs pipeline.** Shared `platformio.shared.ini`, templates, `homework.yaml` schema, `scripts/gen_docs.py`, MkDocs Material, Pages deployment. Do not wait for simulation to build the docs skeleton.
3. **Phase 2 — Quality layering.** clang-format (documented as an ESP-IDF approximation, since ESP-IDF uses AStyle), clang-tidy on host code, pre-commit/pre-push/CI, gitleaks, schema validation. This must land before 30 homeworks, not after.
4. **Phase 3 — Simulation spike.** Wokwi (primary), Velxio (self-host fallback), Fritzing (illustration), Renode (STM32). Timebox by evidence, not by calendar; write the ADR with measured minutes and fidelity notes.
5. **Phase 4 — Pilot 1.3.** Implement the police flasher with all extensions, a report, a `diagram.json`, a native test, a Wokwi scenario, and a Pages entry. This validates the whole chain.
6. **Phase 5 — Scale to 30+.** Only after the pilot: scaffold per homework, changed-only CI, nightly full matrix, rotating simulation budget.

**Phase ordering rationale:** the build/toolchain decisions are prerequisites for every other artifact; the docs pipeline is independent of simulation and can proceed in parallel; simulation is the only high-uncertainty decision and must not block the repository skeleton. Quality tooling must precede scale, because retrofitting 30 projects is expensive.

**Research flags for phases:**

- Phase 0: deeper research on PlatformIO 8.0.0 regressions and ESP-IDF `compiledb`.
- Phase 3: the simulation spike is the main research-heavy phase; measure, do not assume.
- Phase 4: report generation and the 10-section structure may need a documentation-format spike.
- Phase 5: CI cost/time modeling at 30 projects (build matrix, LFS bandwidth, simulation minutes).

---

## Sources

### Official documentation and repositories

- PlatformIO Core 6.2.0 release notes — https://docs.platformio.org/en/latest/core/history.html and https://piolabs.com/blog/news/platformio-core-6-2-released.html — version, Python >= 3.9, SCons 4.11.1.
- PlatformIO `lib_extra_dirs` deprecation — https://docs.platformio.org/en/latest/projectconf/sections/env/options/library/lib_extra_dirs.html — "Deprecated since version 6.0".
- PlatformIO local folder / symlink — same page; validated locally on PlatformIO 6.2.0.
- PlatformIO compilation database — https://docs.platformio.org/en/latest/integration/compile_commands.html — `pio run -t compiledb`, `COMPILATIONDB_INCLUDE_TOOLCHAIN`, `COMPILATIONDB_PATH`.
- PlatformIO `extra_configs` — https://docs.platformio.org/en/latest/projectconf/sections/platformio/options/generic/extra_configs.html — active, not deprecated.
- PlatformIO unit testing — https://docs.platformio.org/en/latest/advanced/unit-testing/ — native, Unity, configuration options.
- PlatformIO GitHub Actions caching — https://docs.platformio.org/en/stable/integration/ci/github-actions.html — cache `~/.platformio/.cache`.
- `platformio/platform-espressif32` v8.0.0 — https://github.com/platformio/platform-espressif32/releases/tag/v8.0.0 — Arduino 3.3.12 / IDF 5.5.5, IDF 6.1, toolchains.
- `platformio/platform-ststm32` v20.0.0 — https://github.com/platformio/platform-ststm32/releases/tag/v20.0.0 — release date and frameworks.
- ESP-IDF code style guide — https://docs.espressif.com/projects/esp-idf/en/stable/esp32/contribute/style-guide.html — 4 spaces, no tabs, 120 chars, AStyle, `tools/ci/astyle-rules.yml`.
- Espressif-IDE clangd/esp-clang — https://docs.espressif.com/projects/espressif-ide/en/latest/additionalfeatures/clangd_cdt_support.html — `CompilationDatabase: build`, `Remove: [-m*, -f*]`, `fix_compile_commands.py`.
- pioarduino `tool-clangd-esp` — https://github.com/pioarduino/platform-espressif32/commit/fb230b117e60ba44734eb082032bdfe9829d8295 — Espressif clangd 21.1.3, Xtensa/ESP RISC-V extensions.
- clangd compile commands and `--query-driver` — https://clangd.llvm.org/design/compile-commands — behavior, absolute paths, target extraction.
- vscode-clangd multi-root limitation — https://github.com/clangd/vscode-clangd/issues/638 and https://github.com/clangd/clangd/discussions/2288 — one server, `.clangd` `CompilationDatabase`, global `--compile-commands-dir`.
- clangd ESP32 issue — https://github.com/clangd/clangd/issues/2256 — Xtensa target in LLVM 20+, flag stripping.
- Wokwi `diagram.json` format — https://docs.wokwi.com/diagram-format — version 1, parts, connections, wire instructions.
- Wokwi CLI usage — https://docs.wokwi.com/wokwi-ci/cli-usage — flags, scenarios, screenshots, VCD, coverage.
- Wokwi CI limits — https://docs.wokwi.com/wokwi-ci/getting-started — 50/200/500/2,000 min, session limits, cloud upload, on-prem on request.
- Wokwi pricing and licensing — https://wokwi.com/pricing and https://wokwi.com/license — free OSS, Pro, commercial.
- Wokwi ESP32 support and fidelity — https://docs.wokwi.com/guides/esp32 — boards, frameworks, WiFi/BLE/I2C/I2S limits, 8 MHz cap.
- Wokwi STM32 limitations — https://docs.wokwi.com/parts/board-st-nucleo-l031k6 and https://wokwi.com/stm32 — no DMA, missing peripherals, 3 boards.
- Wokwi PlatformIO/ESP-IDF integration — https://docs.wokwi.com/vscode/project-config and https://docs.wokwi.com/vscode/esp-idf — `wokwi.toml`, `flasher_args.json` caveat.
- Wokwi offline mode — https://docs.wokwi.com/vscode/offline-mode — Pro feature.
- Wokwi embed alpha — https://wokwi.com/experimental/embed and https://github.com/wokwi/wokwi-embed-example — not officially supported.
- Velxio repository — https://github.com/davidmonterocrespo24/velxio — architecture, AGPLv3 + commercial, self-host scope, board tables, CI, limitations. Metadata checked via GitHub API: created 2026-03-03, pushed 2026-10-20, 3,454 stars.
- Velxio CI quickstart — https://velxio.dev/docs/ci/quickstart/ — `velxio-cli`, `velxio.toml`, Wokwi-compatible `diagram.json`, paid plan.
- Velxio CI pricing — https://velxio.dev/docs/ci/ — Free 0, Maker 200 min, Pro 2,000 min; hosted only.
- Fritzing 1.0.8 release — https://fritzing.org/releases/1-0-8 — 2026-08-12.
- Fritzing sketch format — https://github.com/fritzing/fritzing-app/wiki/2.2-Sketch-file-format — `.fzz` ZIP, `sketch.fz`, views, wires.
- Fritzing licensing — https://fritzing.org/faq/ and https://github.com/fritzing/fritzing-app — GPLv3 app, CC BY-SA 3.0 parts, graphic reuse restriction.
- Fritzing CLI — `src/main.cpp` in `fritzing/fritzing-app` — `-svg FOLDER`, `-gerber FOLDER`, Qt GUI.
- Renode 1.17.0 — https://antmicro.com/blog/2026/09/renode-1-17-0-release — release and features.
- Renode testing — https://renode.readthedocs.io/en/latest/introduction/testing.html — Robot Framework, `renode-test`, CI mode.
- Renode STM32 platforms — https://renode.readthedocs.io/en/latest/introduction/supported-boards.html — STM32F103, STM32F4 Discovery.
- Renode license — https://github.com/renode/renode — MIT.
- QEMU STM32 machines — https://www.qemu.org/docs/master/system/arm/stm32.html — supported machines and missing peripherals.
- Arduino pinout licensing — https://support.arduino.cc/hc/en-us/articles/4415094490770 and https://github.com/arduino/docs-content/blob/main/LICENSE.md — CC BY-SA 4.0 pinouts, CC BY 4.0 docs.
- Espressif datasheet/TRM — https://documentation.espressif.com/esp32_datasheet_en.html — all rights reserved.
- MkDocs Material releases and status — https://github.com/squidfunk/mkdocs-material/releases and https://squidfunk.github.io/mkdocs-material/changelog/ — 9.7.7, maintenance mode, EOL 2027-05-05.
- Zensical — https://zensical.org/ and https://github.com/zensical/zensical/releases — 0.0.71 (2026-10-16), 0.1.0 announcement, MkDocs compatibility, hooks unsupported.
- MkDocs Material math — https://squidfunk.github.io/mkdocs-material/reference/math/ — arithmatex + KaTeX/MathJax.
- MkDocs Material publishing — https://squidfunk.github.io/mkdocs-material/publishing-your-site/ — workflow pattern; action versions updated to current majors in this document.
- GitHub Pages limits — https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits — 1 GB site, 100 GB/month, LFS unsupported.
- GitHub LFS billing — https://docs.github.com/en/billing/managing-billing-for-git-large-file-storage/about-billing-for-git-large-file-storage — 10 GiB/10 GiB, max file sizes.
- GitHub Actions versions — tags verified via GitHub API: checkout v7.0.1, setup-python v7.1.0, cache v6.1.0, configure-pages v6.0.0, upload-pages-artifact v5.0.0, deploy-pages v5.0.1.
- pre-commit hook versions — verified via GitHub API: pre-commit-hooks v6.0.0, mirrors-clang-format v23.1.3, ruff-pre-commit v0.17.2, cpp-linter-hooks v1.7.0.
- PyPI versions — platformio 6.2.0, mkdocs-material 9.7.7, mkdocs 1.6.1, pymdown-extensions 12.3, pre-commit 4.7.0, ruff 0.17.2, check-jsonschema 0.38.2, clang-format 23.1.3, clang-tidy 23.1.3, yamllint 1.38.0.
- npm versions — markdownlint-cli2 0.24.0, KaTeX 0.19.0 (2026-10-01), Mermaid 12.2.0 (Material bundles 11.x).
- PinViz — https://github.com/nordstad/PinViz — MIT, ESP32-S3-DevKitC-1 support, v0.19.0/v0.20.0, young project (5 stars).
- PlatformIO board manifest — https://github.com/platformio/platform-espressif32/blob/develop/boards/esp32-s3-devkitc-1.json — N8/no-PSRAM default, hence the N16R8 overrides.
- ESP32-S3 N16R8 configuration — https://github.com/sivar2311/ESP32-PlatformIO-Flash-and-PSRAM-configurations — `qio_opi`, 16 MB partitions.

### Local validation performed (2026-10-23)

- PlatformIO Core 6.2.0; Python 3.13.13; clangd 21.0.0 (Apple); Node 26.7.0; git 2.54.0.
- Native build with `lib_deps = common=symlink://../lib/common`: SUCCESS, 0.57 s, linked `libcommon.a`, program printed `5`.
- `pio run -t compiledb` on the native project: produced 2 entries, including the shared library source.
- `lib_extra_dirs`: works on 6.2.0 with no deprecation warning; docs still mark it deprecated.
- ESP-IDF `compiledb` validation: blocked by the local ESP-IDF Python environment missing `idf_component_manager`; not a PlatformIO result. Treat as an open spike item.

---

## Confidence Assessment

| Area | Confidence | Reason |
|---|---|---|
| PlatformIO core versions | HIGH | Official release notes + PyPI + local `pio --version` |
| `symlink://` shared libraries | HIGH | Official docs + local end-to-end build |
| `lib_extra_dirs` deprecation | HIGH | Official docs v6.2.1b2; local behavior confirms it still works |
| espressif32 8.0.0 / Arduino 3.x | MEDIUM | Official release, but only four days old; needs smoke testing |
| ESP32-S3 N16R8 config | HIGH | Board manifest + widely used configuration matrix |
| clangd basics | HIGH | Official clangd docs and issue threads |
| ESP-IDF clangd/compiledb | MEDIUM | Official Espressif docs + known gaps; not fully validated locally |
| Multi-root clangd behavior | HIGH | Upstream issue/discussion + maintainer guidance |
| Wokwi capabilities and limits | HIGH | Official docs, CLI docs, pricing/license pages |
| Wokwi CI cost model | MEDIUM | Minutes documented, but free-tier CI eligibility and real runtime need measurement |
| Velxio capabilities | MEDIUM | README and docs are detailed but internally inconsistent; young project |
| Velxio licensing/self-host scope | HIGH | README, LICENSE, and docs agree on AGPLv3 and STM32 exclusion |
| Fritzing format/license/CLI | HIGH | Official wiki, FAQ, source `main.cpp` |
| Renode STM32/CI | HIGH | Official docs, release notes, supported boards |
| QEMU STM32 limits | HIGH | Official QEMU docs |
| Pinout licensing | HIGH | Arduino CC BY-SA 4.0, Espressif all-rights-reserved, ST proprietary |
| Pinout generation tooling | MEDIUM-LOW | No mature, well-maintained, license-clean generator for all target boards; own generator is the safe choice |
| MkDocs Material status/EOL | HIGH | Official changelog/blog/release notes |
| Zensical readiness | HIGH | 0.0.71 release + roadmap; not production-ready for this use |
| Math/Mermaid | HIGH | Material reference docs; KaTeX/Mermaid versions verified via npm |
| Quality tool versions | HIGH | PyPI/npm/GitHub API |
| clang-format "ESP-IDF style" | HIGH | Official style guide says AStyle, not clang-format; the approximation is documented |
| LFS quotas/Pages limits | HIGH | Official GitHub docs |
| CI action versions | HIGH | GitHub API tags |

---

*Stack research for: embedded engineering course monorepo*
*Researched: 2026-10-23*

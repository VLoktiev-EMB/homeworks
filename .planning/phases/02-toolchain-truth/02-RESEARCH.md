# Phase 2: Toolchain Truth - Research

**Researched:** 2026-10-23
**Domain:** PlatformIO 6.2.0 + `platformio/espressif32` 8.0.0, ESP32-S3-DevKitC-1 N16R8 overrides,
`symlink://` shared libraries, compilation database
**Confidence:** HIGH — усі чотири критерії успіху перевірено локальними збірками в цій сесії
(зелені `native`, `esp32s3_arduino`, `esp32s3_espidf` і `compile_commands.json` з джерелами
спільних бібліотек для обох ESP-фреймворків). Знайдено три дефекти в поточних припущеннях,
які planner зобов'язаний виправити до написання плану.

---

<user_constraints>
## User Constraints (from CONTEXT.md)

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

### Reference project

- **D-06:** The reference project lives at `homeworks/0_0-toolchain-smoke/`. Its ID matches
  the repository pattern `^[0-9]+_[0-9]+-[a-z0-9-]+$`.
- **D-07:** It is **temporary**. When `tests/` and the Unity suite arrive in Phase 3, it is
  removed in a dedicated commit. Phase 3's plan must carry that deletion as an explicit
  task; otherwise a project that was never a homework silently enters the public homework
  index.
- **D-08:** It carries **no** `homework.yaml`, report, or `task.md`. Those artifacts belong
  to Phase 4 and Phase 10, and adding them here would make a throwaway build check look
  like coursework.

### Shared libraries

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

### Environments and entry points

- **D-13:** The reference project defines **both** ESP environments — `esp32s3_arduino`
  and `esp32s3_espidf` — and both must build. Success criterion 4 names both frameworks,
  so covering one leaves it unproven.
- **D-14:** The N16R8 overrides are exactly: `board_build.arduino.memory_type = qio_opi`,
  `board_build.flash_mode = qio`, `board_build.psram_type = opi`,
  `board_upload.flash_size = 16MB`, `board_upload.maximum_size = 16777216`,
  `board_build.partitions = default_16MB.csv`. The stock `esp32-s3-devkitc-1` manifest
  (8 MB, no PSRAM) is never used unmodified.
- **D-15:** One entry file serves both ESP frameworks through **conditional compilation**:
  `#ifdef ARDUINO` provides `setup()`/`loop()`, the `#else` branch provides `app_main()`.
  PlatformIO defines `ARDUINO` for the Arduino framework, so a single `src/main.c` links in
  both environments.
- **D-16:** The `native` environment is proven by **`pio run -e native` only**. No
  `test_framework`, no `test/` directory, no Unity. The shared Unity suite and the
  top-level `tests/` project are Phase 3's.

### Compilation database

- **D-17:** One shared extra script lives at `scripts/pio/compiledb.py`, wired from
  `platformio.shared.ini` as `extra_scripts = pre:../../scripts/pio/compiledb.py`. There is
  no per-project copy.
- **D-18:** The generated `compile_commands.json` stays **gitignored** (already covered by
  `.gitignore` from Phase 1, D-21). Only the producing script is committed.

### Build order and evidence

- **D-19:** Build order is `native` → `esp32s3_arduino` → `esp32s3_espidf` → `compiledb`.
  The first end-to-end slice is a green native build with the symlinked libraries, which
  needs no toolchain download and proves the wiring; the riskier `espressif32@8.0.0` pin is
  exercised once the wiring is known good.
- **D-20:** The evidence of this phase is a **green `pio run` in the working session**. Build
  logs are **not** committed and not stored under `.planning/`. Committed logs age into
  false claims; the measurement and evidence contract is Phase 10's.

### Decision records

- **D-21:** `docs/decisions/0006-*.md` records the `symlink://` versus `lib_extra_dirs`
  decision, as carried forward from Phase 1 (D-27: numbering is sequential and permanent).
  — **Reversibility:** one-way — the ADR number is permanent and referenced from
  `docs/decisions/README.md` and from the rulebook; renumbering breaks published
  cross-references.

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
| FOUND-09 | Toolchain pinned: PlatformIO Core 6.2.0, `platformio/espressif32` 8.0.0, explicit ESP32-S3-DevKitC-1 N16R8 overrides (16 MB flash, octal PSRAM). | Core 6.2.0 already installed (`pio --version` → `PlatformIO Core, version 6.2.0`). 8.0.0 resolvable and installed from the registry; `engines.platformio: "^6"`. Arduino env built green with D-14's exact override set. Розділи «Standard Stack», «Pattern 3», «Common Pitfalls P1–P3». |
| ARCH-04 | Shared libraries consumed through `lib_deps = <name>=symlink://../../lib/<name>` with `library.json` per library and a `platformio.shared.ini`; `lib_extra_dirs` remains a generator fallback only. | Перевірено на всіх трьох env: `common`, `port` і адаптер збираються з `../../lib/...`, CDB містить їхні джерела. Named sections + `extends` працюють; `lib_compat_platform`/`lib_ldf_mode` не потрібні. Розділи «Pattern 1», «Pattern 5». |

**Критерій 3 читається за D-03:** у цій фазі виконується лише *споживання* `platformio.shared.ini`.
Генерація — Phase 5. Verifier не повинен вимагати генератора.
</phase_requirements>

---

## Summary

Пін `platformio/espressif32` 8.0.0 справді розв'язується з реєстру (опубліковано 2026-10-19,
Apache-2.0) і сумісний з PlatformIO Core 6.2.0: платформа заявляє
`"engines": {"platformio": "^6"}`. Локальна перевірка в цій сесії дала **три зелені збірки**
(`native`, `esp32s3_arduino`, `esp32s3_espidf`) і `compile_commands.json`, який містить
джерела всіх трьох спільних бібліотек для обох ESP-фреймворків. Це знімає головний ризик
фази, зафіксований у STATE.md («espressif32 8.0.0 is new and must be smoke-tested»).

Однак композиція з CONTEXT.md у трьох місцях **не збереться як записана**, і це не
теоретичні ризики — це відтворені помилки лінкування й конфігурації:

1. **D-15 у формі `src/main.c` не лінкується з Arduino.** Ядро Arduino 3.3.12 очікує
   C++-мнгловані `setup`/`loop` (`_Z5setupv`, `_Z4loopv`), а `.c`-файл дає C-лінкування.
   Лінкувальник падає з `undefined reference to '_Z5setupv'`. Потрібен `src/main.cpp`
   (і третя гілка `#else` з `int main(void)` для `native`, бо `app_main` не є точкою входу
   хост-програми).
2. **Публічні заголовки бібліотек мусять мати `extern "C"`-обгортки.** Після переходу на
   `.cpp` точка входу не бачить C-символів: `undefined reference to
   '_Z23arduino_adapter_versionv'`. Це вимога вже цієї фази, хоча формально її закріплює
   ARCH-01 у Phase 3.
3. **`framework = espidf` не приймає `default_16MB.csv` з D-14 без однойменного файлу в
   проєкті.** Білдер шукає CSV у `framework-espidf/components/partition_table/` (там його
   немає — перевірено) і падає з `Missing partition table file`. Додатково потрібен
   `sdkconfig.defaults` з `CONFIG_ESPTOOLPY_FLASHSIZE_16MB=y`, інакше — попередження
   `Expected 16MB, found 2MB`, а octal PSRAM узагалі не вмикається без
   `CONFIG_SPIRAM_MODE_OCT=y`.

**Primary recommendation:** планувати фазу навколо *вимірюваних* команд (`pio run`,
`pio run -t compiledb`, `esptool image-info`), а композицію `platformio.ini` будувати так:
один `src/main.cpp` з трьома гілками, `sdkconfig.defaults` + проєктний `default_16MB.csv`
для ESP-IDF, `extern "C"` у кожному публічному заголовку, і явна перевірка токенів
`qio_opi` та `ARDUINO_PARTITION_default_16MB` у CDB замість довіри до ini.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Пін версій платформи й інструментів | Build config (`platformio.shared.ini`) | Registry | `platform = espressif32@8.0.0` — єдине місце, де версія стає частиною контракту відтворюваності |
| Композиція середовищ | Build config (`[esp32s3_*]` + `extends`) | Project `platformio.ini` | Спільні ключі живуть у root-файлі; проєкт лише підключає `lib_deps` |
| N16R8 flash/PSRAM | Board build overrides (`board_build.*`, `board_upload.*`) | Arduino framework (Arduino) / `sdkconfig.defaults` (ESP-IDF) | Ключі `board_build.arduino.*` читає лише Arduino-білдер; IDF конфігурується через Kconfig |
| Резолвінг спільних бібліотек | Library Dependency Finder (`lib_deps` + `library.json`) | PlatformIO package manager (`.pio/libdeps`) | `symlink://` реєструє бібліотеку в менеджері пакетів, LDF знаходить її за `#include` |
| Точка входу | Source (`src/main.cpp`) | Framework runtime | Один файл, три гілки; формат символів визначає фреймворк, не проєкт |
| Compilation database | Build system (`compiledb` target + `extra_scripts`) | `scripts/pio/compiledb.py` | SCons збирає CDB з графа збірки; скрипт лише керує опціями |
| Доказ конфігурації | Verification commands (`grep` по CDB, `esptool image-info`) | Build artifacts | Довіряти ini не можна: значення або застосовується білдером, або ігнорується |

---

## Standard Stack

### Core

| Library / tool | Version | Purpose | Why Standard |
|----------------|---------|---------|--------------|
| PlatformIO Core | **6.2.0** (2026-09-05) | Build system для всіх проєктів | Уже встановлений (`pio --version` → `PlatformIO Core, version 6.2.0`); вимога FOUND-09 |
| `platformio/espressif32` | **8.0.0** (2026-10-19) | Платформа ESP32 | Єдина офіційна платформа з Arduino core 3.x та ESP-IDF 6.1 |
| `framework-arduinoespressif32` | `4.30312.261016` (core **3.3.12**, IDF 5.5.5) | Arduino framework | Підтягується платформою 8.0.0 |
| `framework-espidf` | `4.60100.0` (= ESP-IDF **6.1.0**) | ESP-IDF framework | Підтягується платформою 8.0.0 |
| `toolchain-xtensa-esp-elf` | `14.2.0+20260121` (Arduino) / `15.2.0+20251204` (ESP-IDF) | Xtensa cross-compiler | Дві різні версії, обидві встановлюються автоматично |
| `tool-esptool` | `2.50400.0` (esptool **5.4.0**) | Прошивка й інспекція образів | Дає підкоманду `image-info` для доказу 16 MB |
| `platform-native` | поточна | Хост-збірка | Без завантаження тулчейну |

Джерело версій: `platform.json` пакета 8.0.0 — `"framework-arduinoespressif32": "~4.30312.0"`,
`"framework-espidf": "~4.60100.0"`, `"toolchain-xtensa-esp-elf": "14.2.0+20260121"`,
`"engines": {"platformio": "^6"}` [VERIFIED: розпакований `espressif32-8.0.0.tar.gz`,
`platform.json:3-40`].

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `espressif32@8.0.0` | `espressif32@7.1.3` (Arduino core 2.0.17) | Відмова від FOUND-09; старі API Arduino 2.x. Потрібно лише якщо 8.0.0 дасть блокер — жодного не знайдено |
| `espressif32@8.0.0` | pioarduino fork | Має сенс лише для екзотичних C2/C61; вносить непідтримувану залежність у публічний репозиторій |
| `lib_deps = name=symlink://...` | `lib_extra_dirs` | Задепрекейчено з 6.0; LDF сканує всі бібліотеки й може підтягнути чужий адаптер (ADR-0007) |
| `src/main.cpp` | `src/main.c` + шим | D-15 фіксує *один файл*; шим додає другий файл і не усуває проблему лінкування |

### Installation

```bash
# Платформа й тулчейни ставляться автоматично першим `pio run`
pio run -e esp32s3_arduino          # ~1.5 GB завантажень при першому запуску
pio run -e esp32s3_espidf           # + toolchain-xtensa-esp-elf 15.2.0
pio run -e native                   # без завантажень
```

### Version verification

```bash
pio --version                       # PlatformIO Core, version 6.2.0
pio pkg show platformio/espressif32 # 8.0.0, Published on Mon Oct 19 10:06:19 2026
```

Локально підтверджено: `pio pkg show platformio/espressif32` виводить
`Platform • 8.0.0 • Public • Published on Mon Oct 19 10:06:19 2026`, `License Apache-2.0`,
`Compatible Frameworks arduino, espidf` [VERIFIED: `pio pkg show`, 2026-10-23].

---

## Package Legitimacy Audit

Автоматичний `package-legitimacy check` для PyPI повернув `SUS` із **порожніми** сигналами
(`unknown-age`, `unknown-downloads`, `no-repository`) — це відсутність спостереження через
недоступність запиту, а не доказ. Тому нижче — ручна перевірка за авторитетними джерелами.

| Package | Registry | Age / Published | Signals | Source Repo | Verdict | Disposition |
|---------|----------|-----------------|---------|-------------|---------|-------------|
| `platformio` (Core) | PyPI | 6.2.0, `requires_python >=3.9` | Apache-2.0, вже встановлений | github.com/platformio/platformio-core | OK | Approved (не встановлюється цією фазою) |
| `platformio/espressif32` | PlatformIO | 8.0.0, 2026-10-19 | Apache-2.0, 1210 stars, sha256 `dd4c5633…422` | github.com/platformio/platform-espressif32 | OK | Approved |
| `platformio/framework-arduinoespressif32` | PlatformIO | 4.30312.261016, 2026-10-17 | LGPL-2.1-or-later, 17 561 stars | github.com/espressif/arduino-esp32 | OK | Approved (LGPL — не модифікуємо, лише лінкуємо) |
| `platformio/framework-espidf` | PlatformIO | 4.60100.0 (IDF 6.1.0) | Apache-2.0 | github.com/espressif/esp-idf | OK | Approved |
| `platformio/framework-arduinoespressif32-esp32s3-libs` | PlatformIO | 3.3.12, 2026-09-28 | прекомпільовані ядра, 86 MB | espressif/arduino-esp32 | OK | Approved |
| `platformio/toolchain-xtensa-esp-elf` | PlatformIO | 14.2.0+20260121 / 15.2.0+20251204 | бінарний тулчейн | espressif/crosstool-NG | OK | Approved |
| `platformio/tool-esptool` | PlatformIO | 2.50400.0, 2026-09-23 | бінарний | espressif/esptool | OK | Approved |

**Packages removed due to SLOP verdict:** none.
**Packages flagged as suspicious [SUS]:** none. Єдиний `SUS` був інструментальним
артефактом недоступного запиту; після ручної перевірки — `OK`.

Використовуються лише офіційні пакети `platformio/*` та `espressif/*`; жодного пакета,
знайденого через WebSearch, у фазі не встановлюється.

---

## Architecture Patterns

### System Architecture Diagram

```
platformio.shared.ini  (root, committed)
   ├─ [esp32s3_arduino] ── platform=espressif32@8.0.0, board overrides (D-14)
   ├─ [esp32s3_espidf]  ── platform=espressif32@8.0.0, board overrides (D-14)
   └─ [native_unity]    ── platform=native
            │
            │ extra_configs = ../../platformio.shared.ini
            ▼
homeworks/0_0-toolchain-smoke/platformio.ini
   [env:native]            extends native_unity     lib_deps: common, port, host
   [env:esp32s3_arduino]   extends esp32s3_arduino  lib_deps: common, port, arduino
   [env:esp32s3_espidf]    extends esp32s3_espidf   lib_deps: common, port, espidf
            │
            ▼
   LDF ──► lib/<name>/library.json ──► .pio/libdeps/<env>/<hash>/...  (symlink)
            │
            ▼
   pio run -e <env>  ──►  .pio/build/<env>/firmware.{elf,bin}
            │                    │
            │                    └─► esptool image-info ──► Flash size: 16MB
            ▼
   pio run -t compiledb -e <env>  ──►  compile_commands.json (project root, gitignored)
            │
            └─► SCons CompilationDatabase ──►  усі TU, включно з lib/<name>/src/*.c
```

Діаграма показує потік даних, а не структуру файлів: конфігурація → резолвінг бібліотек →
артефакти → доказ.

### Recommended Project Structure

```text
platformio.shared.ini              # root, committed (D-01/D-04)
scripts/pio/compiledb.py           # extra script, committed (D-17)
lib/
├── common/{library.json,include/common.h,src/common.c}
├── port/{library.json,include/port.h,src/port.c}
├── arduino/{library.json,include/arduino_adapter.h,src/arduino_adapter.c}
├── espidf/{library.json,include/espidf_adapter.h,src/espidf_adapter.c}
└── host/{library.json,include/host.h,src/host.c}
homeworks/0_0-toolchain-smoke/
├── platformio.ini
├── default_16MB.csv               # потрібен ESP-IDF-білдеру (див. P3)
├── sdkconfig.defaults             # потрібен ESP-IDF-білдеру (див. P3)
├── src/main.cpp                   # D-15 з поправкою (див. P1)
└── README.md
```

### Pattern 1: Named sections + `extends` (перевірено)

**What:** root-файл містить *шаблонні* секції без префікса `env:`; кожен проєкт оголошує
`[env:<name>]` з `extends = <шаблон>` і власним `lib_deps`.

**When to use:** завжди для цього репозиторію (D-01).

**Example (перевірено локальною збіркою):**

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
    -Wall
    -Wextra
    -Werror=return-type
    -DBOARD_HAS_PSRAM
extra_scripts = pre:../../scripts/pio/compiledb.py
```

**Семантика, яку planner мусить закодувати в план:**

- `extra_configs`: «If you declare the same pair of "group" + "option" in an extra
  configuration file which was previously declared in a base platformio.ini, it will be
  overwritten **with a value from extra configuration**»
  [CITED: docs.platformio.org/…/extra_configs.html]. Тобто додатковий файл **виграє** при
  дублюванні ключа в тій самій секції. Саме тому D-01 обрав один root-файл: дублювання
  ключів між проєктом і шаблоном не виникає.
- `extends`: «the `extends` option doesn't merge values from multiple sections or
  environments» [CITED: docs.platformio.org/…/extends.html].
  **Емпірично підтверджено:** батьківська секція мала `build_flags = -DPARENT_FLAG=1`,
  дочірня — `-DCHILD_FLAG=1`; `pio project config --json-output` показав у `env:native`
  лише `["build_flags", ["-DCHILD_FLAG=1"]]`. Отже **спискові опції замінюються, не
  зливаються**: `build_flags`, `lib_deps`, `extra_scripts`, `build_src_filter`,
  `src_filter`, `lib_ignore`. Якщо проєкту треба додати прапорець, він або повторює весь
  список, або використовує інтерполяцію `${esp32s3_arduino.build_flags}`.

**Практичне правило для плану:** `[env:*]` у проєкті містить **лише** `extends` і `lib_deps`.
Будь-який `build_flags` у проєкті — сигнал, що шаблон треба переробити.

### Pattern 2: Один entry point, три гілки (виправлення D-15)

**What:** `src/main.cpp` з `#if defined(ARDUINO) … #elif defined(ESP_PLATFORM) … #else …`.

```cpp
#include <stdio.h>
#include "common.h"
#include "port.h"

#if defined(ARDUINO)
#include <Arduino.h>
#include "arduino_adapter.h"
void setup(void) { /* ... */ }
void loop(void) {}
#elif defined(ESP_PLATFORM)
#include "espidf_adapter.h"
extern "C" void app_main(void) { /* ... */ }
#else
int main(void) { /* ... */ return 0; }
#endif
```

**Чому саме так:**

- `ARDUINO` визначає Arduino-фреймворк; `ESP_PLATFORM` — ESP-IDF (перевірено в CDB:
  `-DESP_PLATFORM` присутній у кожному TU ESP-IDF-збірки).
- `extern "C"` навколо `app_main` обов'язковий: ESP-IDF викликає `app_main` з C.
- `.c` **не працює** для Arduino: лінкувальник шукає `_Z5setupv`/`_Z4loopv`.
- `native` потребує `main()`, а не `app_main`; без третьої гілки `pio run -e native`
  падає на лінкуванні.

### Pattern 3: N16R8 overrides для Arduino (перевірено)

Ключі D-14 діють саме так:

| Ключ | Куди потрапляє | Ефект (перевірено) |
|------|----------------|--------------------|
| `board_build.arduino.memory_type = qio_opi` | `build.arduino.memory_type` | Вибирає підкаталог прекомпільованих ядер `…/framework-arduinoespressif32-esp32s3-libs/qio_opi`. У CDB токен `qio_opi` є в **64/64** записах |
| `board_build.psram_type = opi` | `build.psram_type` | Формує default memory type, якщо `memory_type` не заданий |
| `board_build.flash_mode = qio` | `build.flash_mode` | Для образу перетворюється на **DIO**: `if mode in ("qio", "qout"): return "dio"` [VERIFIED: `builder/main.py:88-100`, 8.0.0] |
| `board_upload.flash_size = 16MB` | заголовок образу | `esptool image-info` → `Flash size: 16MB` |
| `board_build.partitions = default_16MB.csv` | Arduino: `tools/partitions/` ядра; ESP-IDF: проєктна директорія | У CDB токен `ARDUINO_PARTITION_default_16MB` є в **64/64** записах |

**Доказ octal PSRAM:** `qio_opi/include/sdkconfig.h` містить

```
#define CONFIG_SPIRAM 1
#define CONFIG_SPIRAM_MODE_OCT 1
#define CONFIG_SPIRAM_BOOT_INIT 1
```

тоді як `qio_qspi/include/sdkconfig.h` — `#define CONFIG_SPIRAM_MODE_QUAD 1`
[VERIFIED: розпакований `framework-arduinoespressif32-esp32s3-libs-3.3.12.tar.gz`,
`sdkconfig.h:880-881` та `qio_qspi/include/sdkconfig.h:881`]. Це і є справжній механізм
увімкнення octal PSRAM: memory type вибирає набір ядер, у яких PSRAM уже сконфігурований.

### Pattern 4: ESP-IDF environment (додаткові артефакти, яких немає в D-14)

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

Обидва факти перевірені падінням, а потім зеленою збіркою (див. P3).

### Pattern 5: Compilation database (перевірено для обох фреймворків)

```python
# scripts/pio/compiledb.py
import os
Import("env")

env.Replace(COMPILATIONDB_INCLUDE_TOOLCHAIN=True)
env.Replace(COMPILATIONDB_PATH=os.path.join(env.subst("$PROJECT_DIR"), "compile_commands.json"))
```

`pio run -t compiledb` реалізовано ядром PlatformIO:
`env.Alias("compiledb", env.CompilationDatabase("$COMPILATIONDB_PATH"))`
[VERIFIED: `platformio/builder/main.py:195-196`, Core 6.2.0]. Шлях `pre:../../scripts/pio/compiledb.py`
резолвиться **відносно директорії проєкту** — перевірено: скрипт лежить у
`research/scripts/pio/`, проєкт — у `research/homeworks/0_0-smoke/`, і він виконався.

Результати (локальні, 2026-10-23):

| Env | Записів у CDB | Джерела `lib/` | Ключові токени |
|-----|---------------|----------------|----------------|
| `native` | 3 | `lib/common/src/common.c`, `lib/port/src/port.c` (абсолютні шляхи) | — |
| `esp32s3_arduino` | 64 | `common.c`, `port.c`, `arduino_adapter.c` | `qio_opi` — 64/64; `ARDUINO_PARTITION_default_16MB` — 64/64; `BOARD_HAS_PSRAM` — 0/64 |
| `esp32s3_espidf` | 1074 | `common.c`, `port.c`, `espidf_adapter.c` + `src/main.cpp` | `-DESP_PLATFORM`, `-DIDF_VER="6.1.0"`, `-DPLATFORMIO=60200`; 259 `-I` включно з `esp_driver_gpio/include` |

**Важливо:** `compile_commands.json` **перезаписується** кожним запуском `compiledb`,
тому доказ для Arduino і ESP-IDF треба робити послідовно, перевіряючи файл одразу після
кожної генерації (або тимчасово копіюючи його). Шлях `COMPILATIONDB_PATH` навмисно один
(D-17/D-18).

### Anti-Patterns to Avoid

- **`src/main.c` як єдиний entry point:** не лінкується з Arduino (P1).
- **Заголовки без `extern "C"`:** ламають C++-точку входу (P2).
- **`board_build.partitions = default_16MB.csv` для ESP-IDF без однойменного файлу в
  проєкті:** гарантована помилка «Missing partition table file» (P3).
- **`[env]` у `platformio.shared.ini`:** глобальна секція зачепить усі майбутні проєкти й
  зробить `extends` надлишковим; D-01 обрав named sections саме щоб цього уникнути.
- **Доказ «16 MB / octal PSRAM» читанням `platformio.ini`:** ini описує намір, не
  результат; доказ — `esptool image-info` + токени в CDB.
- **Очікування `Flash mode: QIO` в заголовку образу:** платформа перетворює `qio` → `dio`
  для образу; перевіряти треба `Flash size`, не mode.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Композиція конфігурації між проєктами | Копіювання `platformio.ini` у кожен проєкт | `extra_configs` + `extends` | 30+ копій дрейфують; дублювання ключів — джерело розбіжностей |
| Резолвінг спільних бібліотек | Власні `-I`/`-L` у `build_flags` | `lib_deps = name=symlink://...` + `library.json` | LDF сам вирішує порядок, транзитивні залежності й перезбірку |
| Генерація CDB | Парсинг `-v` виводу або власний скрипт | `pio run -t compiledb` | Ядро вже має `CompilationDatabase` і знає всі команди графа |
| Конфігурація flash/PSRAM | Патч `boards/esp32-s3-devkitc-1.json` | `board_build.*` overrides | Override не змінює спільний пакет і працює після оновлення платформи |
| Конфігурація ESP-IDF | `-D` у `build_flags` | `sdkconfig.defaults` | IDF генерує `sdkconfig.<env>` із defaults; `-D` не потрапляє в Kconfig |

**Key insight:** усе, що стосується вибору файлів, прапорців і порядку збірки, PlatformIO вже
вирішує через маніфести; ручне втручання ламає інкрементальність і приховує залежності.

---

## Common Pitfalls

### Pitfall P1: `src/main.c` не лінкується з Arduino (ядро 3.x)

**What goes wrong:** `pio run -e esp32s3_arduino` падає на лінкуванні:

```text
undefined reference to `_Z5setupv'
undefined reference to `_Z4loopv'
```

**Why it happens:** Arduino core 3.3.12 викликає `setup()`/`loop()` з `main.cpp` як
C++-функції; `.c`-файл дає C-лінкування (`setup`, не `_Z5setupv`).
`#ifdef ARDUINO` не змінює мову компіляції файлу.

**How to avoid:** entry point — `src/main.cpp`; для ESP-IDF-гілки — `extern "C" void
app_main(void)`; для native — третя гілка з `int main(void)`.

**Warning signs:** будь-яка збірка Arduino, де `src/` містить лише `.c`.

### Pitfall P2: Публічні заголовки без `extern "C"`

**What goes wrong:** після переходу на `.cpp` лінкування падає:

```text
"port_placeholder()", referenced from: _main in main.o
NOTE: found '_port_placeholder' in libport.a[2](port.o), declaration possibly missing 'extern "C"'
```

**Why it happens:** бібліотеки — чистий C (C-лінкування), споживач — C++. Без обгорток
компілятор шукає C++-мнглований символ.

**How to avoid:** кожен публічний заголовок у `lib/*/include/` має
`#ifdef __cplusplus extern "C" { … } #endif`. Це вимога ARCH-01, але вона стає
обов'язковою вже у Phase 2 через `.cpp`-точку входу.

**Warning signs:** лінкування проходить для `native`, але падає для Arduino/ESP-IDF (або
навпаки) з `undefined reference to _Z…`.

### Pitfall P3: ESP-IDF не знаходить `default_16MB.csv` і не бачить 16 MB flash

**What goes wrong:** перша збірка `esp32s3_espidf` завершується так:

```text
Warning! Flash memory size mismatch detected. Expected 16MB, found 2MB!
Please select a proper value in your `sdkconfig.defaults` or via the `menuconfig` target!
Missing partition table file `/…/homeworks/0_0-smoke/default_16MB.csv`
```

**Why it happens:** `generate_partition_table()` робить
`partitions_csv = board.get("build.partitions", "partitions_singleapp.csv")` і шукає файл у
`<framework-espidf>/components/partition_table/`; якщо не знайдено — бере шлях **відносно
проєкту** [VERIFIED: `builder/frameworks/espidf.py:1818-1830`, 8.0.0]. У
`framework-espidf/components/partition_table/` є лише `partitions_singleapp*` і
`partitions_two_ota*` — `default_16MB.csv` там немає [VERIFIED: `ls` інстальованого
`framework-espidf` 6.1.0]. Flash size перевіряється окремо й лише **попереджає**.

**How to avoid:** покласти `default_16MB.csv` у корінь проєкту (тоді D-14 лишається
дослівним) і додати `sdkconfig.defaults` з `CONFIG_ESPTOOLPY_FLASHSIZE_16MB=y`,
`CONFIG_SPIRAM=y`, `CONFIG_SPIRAM_MODE_OCT=y`. Після цього збірка зелена (перевірено).

**Warning signs:** банер `HARDWARE: … 16MB Flash` показує 16 MB навіть до виправлення —
він бере `board_upload.flash_size`, а не фактичний sdkconfig. Довіряти банерам не можна.

### Pitfall P4: `extends` мовчки відкидає батьківські списки

**What goes wrong:** проєкт додає один `-D` у `build_flags`, і всі прапорці шаблону
зникають; збірка «успішна», але з іншими прапорцями.

**Why it happens:** `extends` не зливає значення; дочірнє значення замінює батьківське
[CITED: docs.platformio.org/…/extends.html; підтверджено `pio project config --json-output`].

**How to avoid:** не перевизначати спискові опції в `[env:*]`; за потреби —
`${esp32s3_arduino.build_flags}` або повний повтор списку.

**Warning signs:** у `pio project config --json-output` `build_flags` у `env:*` не містить
прапорців шаблону.

### Pitfall P5: `-DBOARD_HAS_PSRAM` відсутній → PSRAM API «вимкнено» у кожному TU

**What goes wrong:** `#if CONFIG_SPIRAM` у користувацькому коді хибний; `WString` має
`CAPACITY_MAX = 65535` замість 3 MB. PSRAM при цьому ініціалізується IDF-ом під час
завантаження (`CONFIG_SPIRAM_BOOT_INIT` у `qio_opi`-ядрах), тому апаратно він є — але
код, що перевіряє `BOARD_HAS_PSRAM` або `CONFIG_SPIRAM`, поводиться як на платі без PSRAM.

**Why it happens:** `platformio-build.py` додає `-DESP32_ARDUINO_LIB_BUILDER` до
`CPPDEFINES` усього build-env (файл `flags/defines` пакета ядер), а `esp32-hal-psram.h`
робить:

```c
#if defined(ESP32_ARDUINO_LIB_BUILDER) && !defined(BOARD_HAS_PSRAM)
#ifdef CONFIG_SPIRAM
#undef CONFIG_SPIRAM
#endif
#endif
```

[VERIFIED: `cores/esp32/esp32-hal-psram.h:25-34`, core 3.3.12].

**How to avoid:** додати `-DBOARD_HAS_PSRAM` до `build_flags` `[esp32s3_arduino]`. Усі
реальні `qio_opi`-манифести це роблять (`esp32s3box`, `lolin_s3_pro` мають
`-DBOARD_HAS_PSRAM` у `build.extra_flags`) [VERIFIED: `boards/esp32s3box.json`,
`boards/lolin_s3_pro.json`]. Це окремий ключ, не частина списку D-14, тому D-14 не
порушується.

**Warning signs:** у CDB `BOARD_HAS_PSRAM` — 0 входжень (перевірено в цій сесії).

### Pitfall P6: ESP-IDF генерує файли в дереві проєкту

**What goes wrong:** після першої збірки `esp32s3_espidf` у проєкті з'являються
`CMakeLists.txt` (108 B), `src/CMakeLists.txt` (199 B) і `sdkconfig.esp32s3_espidf` (92 KB).
Вони не покриті `.gitignore` (там лише `sdkconfig.old*`), тож або потраплять у коміт, або
лишаться untracked.

**Why it happens:** `create_default_project_files()` створює CMake-файли, якщо їх немає;
`sdkconfig.<env>` — вихід CMake-конфігурації.

**How to avoid:** або (а) authored-версії обох `CMakeLists.txt` (2–3 рядки) + коміт
`sdkconfig.esp32s3_espidf` (`.gitignore` свідомо не ігнорує `sdkconfig` — див. рядки 8–12),
або (б) `board_build.esp-idf.sdkconfig_path` усередину `.pio/` і `.gitignore` для
`sdkconfig.*`. Рекомендація: (а) — проєкт тимчасовий (D-07) і зникне разом із Phase 3.

**Warning signs:** `git status` показує `CMakeLists.txt` або `sdkconfig.*` як untracked після
першої збірки.

### Pitfall P7: CDB перезаписується між середовищами

**What goes wrong:** перевірка «у CDB є джерела бібліотек для Arduino **і** ESP-IDF» робиться
після двох послідовних `compiledb`, і другий запуск затирає файл першого.

**Why it happens:** `COMPILATIONDB_PATH` за замовчуванням — `<project>/compile_commands.json`,
один на проєкт.

**How to avoid:** перевіряти одразу після кожного запуску або копіювати файл у тимчасове
ім'я (`compile_commands.arduino.json`), не комітячи його.

**Warning signs:** перевірка проходить для останнього env і «не проходить» для першого.

### Pitfall P8: Два різні тулчейни для одного піна

**What goes wrong:** Arduino-збірка використовує `toolchain-xtensa-esp-elf 14.2.0+20260121`,
ESP-IDF-збірка — `15.2.0+20251204` (його вимагає `framework-espidf`). На диску це ~2.4 GB.

**Why it happens:** пакети платформи й пакети фреймворку мають власні піни.

**How to avoid:** не «вирівнювати» версії вручну; це нормальна поведінка PlatformIO.
Задокументувати у звіті/README проєкту, що обидва тулчейни очікуються.

**Warning signs:** спроба зафіксувати один `toolchain-xtensa-esp-elf` для обох env ламає
ESP-IDF-збірку.

---

## Code Examples

### Приклад 1: `library.json` (перевірено)

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

`version` — єдине місце, де живе версія (D-12). `lib_deps` версію не несе.

### Приклад 2: `platformio.ini` проєкту (перевірено)

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

`<name>=symlink://<folder>` — офіційна форма; папка мусить містити маніфест із `name` і
`version` [CITED: docs.platformio.org/…/cmd_install.html#local-folder].

### Приклад 3: `extern "C"` у публічному заголовку (перевірено)

```c
#pragma once
#ifdef __cplusplus
extern "C" {
#endif

const char *common_version(void);

#ifdef __cplusplus
}
#endif
```

### Приклад 4: Детермінована перевірка критерію 4

```bash
cd homeworks/0_0-toolchain-smoke

# Arduino
pio run -t compiledb -e esp32s3_arduino
python3 - <<'PY'
import json, sys
db = json.load(open("compile_commands.json"))
files = [e["file"] for e in db]
need = ["lib/common/src/common.c", "lib/port/src/port.c", "lib/arduino/src/arduino_adapter.c"]
missing = [n for n in need if not any(f.endswith(n) for f in files)]
qio = sum("qio_opi/include" in (e.get("command") or " ".join(e.get("arguments", []))) for e in db)
part = sum("ARDUINO_PARTITION_default_16MB" in (e.get("command") or " ".join(e.get("arguments", []))) for e in db)
print(f"entries={len(db)} qio_opi={qio} partition={part} missing={missing}")
sys.exit(1 if missing or not qio or not part else 0)
PY

# ESP-IDF (окремий запуск — CDB перезаписується)
pio run -t compiledb -e esp32s3_espidf
python3 - <<'PY'
import json, sys
db = json.load(open("compile_commands.json"))
files = [e["file"] for e in db]
need = ["lib/common/src/common.c", "lib/port/src/port.c", "lib/espidf/src/espidf_adapter.c"]
missing = [n for n in need if not any(f.endswith(n) for f in files)]
print(f"entries={len(db)} missing={missing}")
sys.exit(1 if missing else 0)
PY
```

### Приклад 5: Детермінована перевірка критерію 2

```bash
# Arduino: заголовок образу
~/.platformio/packages/tool-esptool/esptool --chip esp32s3 \
  image-info .pio/build/esp32s3_arduino/firmware.bin | grep -E "Flash size|Flash mode"
# → Flash size: 16MB / Flash mode: DIO

# ESP-IDF: sdkconfig, який реально використано
python3 - <<'PY'
import json
s = json.load(open(".pio/build/esp32s3_espidf/config/sdkconfig.json"))
assert s["ESPTOOLPY_FLASHSIZE"] == "16MB"
assert s["ESPTOOLPY_FLASHSIZE_16MB"] is True
assert s["SPIRAM"] is True and s["SPIRAM_MODE_OCT"] is True
assert s["SPIRAM_MODE_QUAD"] is False
print("16MB + octal PSRAM OK")
PY
```

Ці значення реально спостерігалися: `ESPTOOLPY_FLASHSIZE = 16MB`,
`ESPTOOLPY_FLASHSIZE_16MB = True`, `SPIRAM = True`, `SPIRAM_MODE_OCT = True`,
`SPIRAM_MODE_QUAD = False`.

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `lib_extra_dirs` | `lib_deps = name=symlink://…` | deprecated з PlatformIO 6.0 | LDF більше не сканує весь `lib/`; залежність стає явною |
| Arduino core 2.0.17 (platform 7.x) | Arduino core 3.3.12 (platform 8.0.0) | 2026-10-19 | Arduino-ESP32 3.x API changes; новий пакет прекомпільованих ядер із memory-type варіантами |
| Тулчейн Xtensa 8.4.0 на кожен чип | Уніфікований `toolchain-xtensa-esp-elf` 14.2.0 / 15.2.0 | 8.0.0 | Старі пакети `toolchain-xtensa-esp32{,s2,s3}` більше не потрібні |
| ESP-IDF 5.5.x | ESP-IDF 6.1.0 (`framework-espidf 4.60100.0`) | 7.x → 8.0.0 | Інший набір компонентів і Kconfig; sdkconfig.defaults обов'язковий для 16 MB |
| `pio run -t compiledb` «для всього» | Той самий target, але CDB збирається з SCons-графа | — | Для ESP-IDF компоненти й бібліотеки компілюються SCons-ом, тому потрапляють у CDB |

**Deprecated/outdated:**
- `lib_extra_dirs` — не використовувати (ADR-0007).
- `src/main.c` як entry point для Arduino — не працює з core 3.x.
- Очікування `Flash mode: QIO` в заголовку — платформа віддає `DIO`.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `-DBOARD_HAS_PSRAM` варто додати до `build_flags` Arduino-env | P5, Pattern 3 | Низький: це додатковий прапорець, не частина D-14. Якщо користувач відмовиться — PSRAM працює, але `WString`/`#if CONFIG_SPIRAM` поводяться як без PSRAM |
| A2 | `sdkconfig.esp32s3_espidf` варто комітити, а не ігнорувати | P6 | Середній: 92 KB генерованого файлу в історії; альтернатива — `.gitignore`, що суперечить примітці Phase 1 |
| A3 | `app_main`-символ вимагає `extern "C"` у C++-файлі | P1 | Низький: перевірено, що без `extern "C"` IDF-збірка не лінкується (стандартна семантика C++) |
| A4 | `.planning/research/ARCHITECTURE.md` твердження про неповний `compiledb` для ESP-IDF не підтвердилося | Pattern 5 | Низький: локально 1074 записи з джерелами бібліотек; твердження стосувалося іншої версії/конфігурації |

---

## Open Questions

1. **D-15: `.c` чи `.cpp`?**
   - What we know: `src/main.c` з `#ifdef ARDUINO` не лінкується з Arduino core 3.3.12
     (`undefined reference to '_Z5setupv'`); `src/main.cpp` з трьома гілками збирається
     в усіх трьох env.
   - What's unclear: чи готовий користувач змінити розширення файлу, зафіксоване в D-15.
   - Recommendation: уточнити на етапі планування; запропонувати `.cpp` як єдиний варіант,
     що задовольняє критерій 1. Механізм D-15 (один файл, умовна компіляція) зберігається.

2. **Третя гілка для `native`.**
   - What we know: `app_main` не є точкою входу хост-програми; без `main()` `pio run -e
     native` падає.
   - What's unclear: чи вважати це розширенням D-15, чи окремим рішенням.
   - Recommendation: зафіксувати `#else int main(void)` як частину D-15-поправки.

3. **Номер ADR.**
   - What we know: `docs/decisions/README.md` каже `Next number: **0007** (reserved for the
     Phase 2 symlink decision)`; `0006-public-commit-identity.md` уже існує.
   - What's unclear: CONTEXT.md D-21 посилається на `0006-*` — це застаріле посилання.
   - Recommendation: створити `docs/decisions/0007-symlink-shared-libraries.md` і оновити
     індекс; не перевикористовувати 0006.

4. **`sdkconfig.defaults` і проєктний `default_16MB.csv` — це частина D-14?**
   - What we know: без них `esp32s3_espidf` не збирається взагалі.
   - What's unclear: чи трактувати їх як «ще один override» (поза списком D-14) або як
     обов'язкові артефакти проєкту.
   - Recommendation: вважати обов'язковими артефактами проєкту; D-14 лишається дослівним,
     бо `board_build.partitions` зберігає те саме значення.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| PlatformIO Core | Усі збірки | ✓ | 6.2.0 | — |
| Python | PlatformIO | ✓ | 3.13.13 | — |
| `platform-native` | `pio run -e native` | ✓ | інстальовано | — |
| `espressif32` 8.0.0 | ESP-збірки | ✓ (інстальовано в цій сесії) | 8.0.0 | 7.1.3 / pioarduino (не потрібно) |
| `toolchain-xtensa-esp-elf` | ESP-збірки | ✓ | 14.2.0 + 15.2.0 | — |
| `framework-arduinoespressif32` + s3 libs | Arduino | ✓ | 4.30312.261016 / 3.3.12 | — |
| `framework-espidf` | ESP-IDF | ✓ | 4.60100.0 (6.1.0) | — |
| esptool | Доказ 16 MB | ✓ | 5.4.0 | `pio pkg exec` |
| Диск | Тучейни + ядра | ✓ | ~12 GB зайнято до фази; +~2 GB після | — |
| Мережа | Перша інсталяція пакетів | ✓ (у цій сесії) | — | Офлайн-збірка після інсталяції |

**Missing dependencies with no fallback:** none.
**Missing dependencies with fallback:** none — усе, що потрібно, уже стоїть після першого
`pio run`.

---

## Validation Architecture

> `workflow.nyquist_validation` = `true` у `.planning/config.json`, тому секція обов'язкова.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Немає юніт-фреймворку для прошивки в цій фазі (D-16). Доказ — команди збірки та перевірки артефактів |
| Config file | `homeworks/0_0-toolchain-smoke/platformio.ini` |
| Quick run command | `cd homeworks/0_0-toolchain-smoke && pio run -e native` |
| Full suite command | `pio run -e native && pio run -e esp32s3_arduino && pio run -e esp32s3_espidf` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| FOUND-09 | Core 6.2.0 | smoke | `pio --version \| grep -q '6.2.0'` | ✅ |
| FOUND-09 | Платформа 8.0.0 резолвиться | smoke | `pio pkg show platformio/espressif32 \| grep -q '8.0.0'` | ✅ |
| FOUND-09 | N16R8 → 16 MB flash (Arduino) | integration | `esptool --chip esp32s3 image-info .pio/build/esp32s3_arduino/firmware.bin \| grep 'Flash size: 16MB'` | ✅ |
| FOUND-09 | Octal PSRAM (Arduino) | integration | `grep -q 'qio_opi/include' compile_commands.json` | ✅ |
| FOUND-09 | 16 MB + octal PSRAM (ESP-IDF) | integration | python-assert на `.pio/build/esp32s3_espidf/config/sdkconfig.json` | ✅ |
| ARCH-04 | `symlink://` бібліотеки збираються | integration | `pio run -e native` (LDF-граф містить `common`, `port`) | ✅ |
| ARCH-04 | CDB містить джерела бібліотек (Arduino) | integration | python-assert на `compile_commands.json` після `-e esp32s3_arduino` | ✅ |
| ARCH-04 | CDB містить джерела бібліотек (ESP-IDF) | integration | python-assert на `compile_commands.json` після `-e esp32s3_espidf` | ✅ |
| ARCH-04 | Кожна бібліотека має `library.json` | static | `test -f lib/{common,port,arduino,espidf,host}/library.json` | ✅ |
| D-03 | Генерації немає | review | Перевірити, що `platformio.shared.ini` закомічений вручну; жоден скрипт його не створює | ✅ |

### Sampling Rate

- **Per task commit:** `pio run -e native` (0.3 s після першої збірки).
- **Per wave merge:** `pio run -e native && pio run -e esp32s3_arduino` (~4 s кожна після
  першої збірки).
- **Phase gate:** усі три env зелені + обидві перевірки CDB + перевірка 16 MB/PSRAM.

### Wave 0 Gaps

- [ ] Немає автоматизованого скрипта, що перевіряє CDB; команди вище — одноразові. Постійний
      gate — Phase 8 (TOOL-05/TOOL-06), не ця фаза.
- [ ] `scripts/tests/` не містить тестів для `scripts/pio/compiledb.py`; за конвенцією
      репозиторію новий скрипт має брати участь у `python3 -m unittest discover -s
      scripts/tests`. Мінімальний тест (наявність файлу, відсутність синтаксичних помилок)
      доречний у цій фазі.
- [ ] Немає фікстури, що ізолює CDB між env — див. P7.

---

## Security Domain

> `security_enforcement: true`, `security_asvs_level: 1`.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | — |
| V3 Session Management | no | — |
| V4 Access Control | no | — |
| V5 Input Validation | yes (обмежено) | Шляхи в `lib_deps`/`extra_configs` — довірені, але мусять резолвитися лише в межах репозиторію; жодного абсолютного шляху в комітах |
| V6 Cryptography | no | — |
| V14 Configuration | yes | Піни версій; `compile_commands.json` і `.pio/` не комітяться; `extra_scripts` — лише власний скрипт |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Підміна пакета в реєстрі (typosquat) | Tampering | Лише `platformio/*` та `espressif/*`; точні піни; sha256 у реєстрі |
| Довільне виконання коду через `extra_scripts` | Elevation of Privilege | Рівно один скрипт у репозиторії (`scripts/pio/compiledb.py`), підлягає review; шлях відносний, не з `lib_deps` |
| Витік секретів у логах збірки | Information Disclosure | gitleaks у pre-commit і CI; логи не комітяться (D-20) |
| Неконтрольоване завантаження тулчейну | Tampering | Пакети з офіційного реєстру PlatformIO поверх HTTPS; піни версій |
| Абсолютні шляхи в CDB | Information Disclosure | `compile_commands.json` у `.gitignore` (рядок 16) |

---

## Project Constraints (from CLAUDE.md / AGENTS.md)

Директиви, які план мусить задовольнити:

- **GSD-воркфлоу обовʼязковий:** кожна зміна проходить через `/gsd-*` або детермінований
  скрипт під `scripts/`. Прямі редагування поза воркфлоу заборонені.
- **Conventional Commits:** `type(scope): summary`, `scope` — ID плану фази або homework ID.
  Приклад: `feat(2_2): add shared PlatformIO config`.
- **Гілки:** `infra/<slug>` для цієї фази (не `hw/`, бо це не homework); PR через
  `.github/PULL_REQUEST_TEMPLATE/infra.md`; squash-merge у `main`.
- **Homework ID:** `^[0-9]+_[0-9]+-[a-z0-9-]+$`, ASCII-only. `0_0-toolchain-smoke` відповідає.
- **Generated files не комітяться:** `compile_commands.json`, `site/`, `.pio/` — перелік
  вичерпний; `platformio.shared.ini` до нього не належить (D-04).
- **REUSE:** ліцензія оголошується один раз у `REUSE.toml`; нові файли підпадають під
  catch-all MIT (код і конфігурація) або CC-BY-4.0 (`*.md`, `homeworks/**/*.md`).
- **Секрети:** gitleaks має проходити; жодних облікових даних у `platformio.ini` або
  `sdkconfig.defaults`.
- **LFS:** не застосовується до цієї фази; `.elf`/`.bin` у `.pio/` не комітяться взагалі.
- **ADR:** cross-cutting рішення — у `docs/decisions/` із наступним вільним номером (**0007**)
  та оновленням `docs/decisions/README.md` у тому самому коміті.

---

## Sources

### Primary (HIGH confidence)

- Локальні збірки 2026-10-23 (PlatformIO Core 6.2.0, Python 3.13.13, macOS arm64):
  - `pio run -e native` → `SUCCESS` (0.27 s), LDF-граф `common @ 0.1.0`, `port @ 0.1.0`.
  - `pio run -e esp32s3_arduino` → `SUCCESS` (3.28 s) після виправлень P1/P2.
  - `pio run -e esp32s3_espidf` → `FAILED` (P3) → `SUCCESS` (22.21 s) після
    `sdkconfig.defaults` + проєктного `default_16MB.csv`.
  - `pio run -t compiledb -e esp32s3_arduino` → 64 записи; `-e esp32s3_espidf` → 1074 записи;
    `-e native` → 3 записи. У всіх присутні джерела `lib/`.
  - `esptool --chip esp32s3 image-info` → `Flash size: 16MB`, `Flash mode: DIO`.
  - `pio project config --json-output` → підтвердження, що `extends` не зливає `build_flags`.
- Пакет `espressif32-8.0.0.tar.gz` (реєстр PlatformIO): `platform.json`, `builder/main.py`,
  `builder/frameworks/espidf.py`, `boards/esp32-s3-devkitc-1.json`, `boards/esp32s3box.json`,
  `boards/lolin_s3_pro.json`.
- Пакет `framework-arduinoespressif32-4.30312.261016`: `tools/platformio-build.py`,
  `tools/partitions/default_16MB.csv`, `cores/esp32/esp32-hal-psram.h`, `cores/esp32/WString.h`.
- Пакет `framework-arduinoespressif32-esp32s3-libs-3.3.12`: `flags/defines`,
  `qio_opi/include/sdkconfig.h`, `qio_qspi/include/sdkconfig.h`.
- Інстальований `framework-espidf` 6.1.0: `components/partition_table/`,
  `components/esp_psram/esp32s3/Kconfig.spiram`, `components/esptool_py/Kconfig.projbuild`.
- PlatformIO Core 6.2.0 (інстальований): `platformio/builder/main.py`,
  `platformio/builder/tools/piobuild.py`.
- Реєстр PlatformIO API: `platformio/espressif32` (8.0.0, 2026-10-19, Apache-2.0),
  `framework-arduinoespressif32` (4.30312.261016, LGPL-2.1-or-later).
- PyPI JSON: `platformio` 6.2.0, `requires_python >=3.9`, Apache-2.0.

### Secondary (MEDIUM confidence)

- `https://github.com/platformio/platform-espressif32/releases/tag/v8.0.0` — Arduino core
  3.3.12 (IDF 5.5.5), ESP-IDF 6.1, тулчейни 14.2.0, «Removed deprecated functionality for
  pulling upstream Arduino core», 72 нові плати.
- `https://github.com/pioarduino/platform-espressif32/pull/478` — `qio_opi`-плати без
  `-DBOARD_HAS_PSRAM` втрачали PSRAM-поведінку в Arduino core 3.x.
- `https://community.platformio.org/t/how-do-you-set-up-a-new-board-esp32-s3-n16r8/32306` —
  практика N16R8-конфігурації (збігається з D-14).

### Tertiary (LOW confidence — не використано для рішень)

- Твердження `.planning/research/STACK.md` про неповний `compiledb` для ESP-IDF (MEDIUM у
  документі) локально **не підтвердилося**: CDB містить джерела бібліотек і `src/main.cpp`.

---

## Metadata

**Confidence breakdown:**

- Standard stack: **HIGH** — версії з реєстру й розпакованих пакетів; збірки зелені.
- Architecture: **HIGH** — усі три env зібрані локально; семантика `extends` перевірена
  експериментально.
- Pitfalls: **HIGH** — P1, P2, P3 відтворені як реальні помилки; P5 підтверджений вихідним
  кодом ядра; P6 і P7 спостережені.
- ESP-IDF compiledb: **HIGH** (1074 записи, джерела присутні) — раніше було MEDIUM.

**Research date:** 2026-10-23
**Valid until:** 2026-11-22 (30 днів; платформа 8.0.0 опублікована 4 дні тому й може швидко
отримати патч-реліз — перевіряти пін перед стартом).

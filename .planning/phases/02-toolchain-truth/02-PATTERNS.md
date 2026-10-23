# Phase 2: Toolchain Truth - Pattern Map

**Mapped:** 2026-10-23
**Files analyzed:** 23 (17 new, 6 modified; 5 `library.json` + 5 headers + 5 sources counted individually)
**Analogs found:** 6 files with a usable analog (2 exact, 4 partial / style-only); 15 files with **no** codebase analog

## Честная оценка (читати першою)

Репозиторій досі **не має жодного файлу PlatformIO**: `homeworks/`, `lib/`, `scripts/pio/`
не існують (перевірено `ls`), а `git ls-files` не містить жодного `.ini`, `.c`, `.h`,
`.cpp`, `sdkconfig*` чи `library.json`. Тому для більшості артефактів цієї фази
«найближчий аналог» — це **не схожий файл, а конвенція**:

| Конвенція | Джерело в репозиторії | Що вона дає цій фазі |
|---|---|---|
| Конфігурація як закомічені дані + окремий перевіряльник | `policy/*.json` + `scripts/check_policy.py` (Фаза 1) | `platformio.shared.ini` комітиться, покоління відкладене (D-02/D-04) |
| Python-скрипт: docstring з Usage/exit codes, stdlib, `PASS`/`FAIL` | `scripts/check_pr_templates.py` | форма `scripts/pio/compiledb.py` |
| `stdlib unittest` + `scripts/tests/` + `unittest discover` | `scripts/tests/test_*.py` (9 файлів) | новий тест для `compiledb.py` |
| MADR 4.0, структура перевіряється `test_adrs.py` | `docs/decisions/0006-*.md`, `README.md`, `template.md` | ADR-0007 |
| `.gitignore` перевіряється через `git check-ignore` | `scripts/tests/test_gitignore.py` | розширення під D-23 |
| Markdown-типографіка ~90 колонок, таблиці, bold-lead bullets | `docs/decisions/*.md`, `README.md` | README smoke-проєкту |

**Не вигадувати аналоги.** Для `.ini`, C/C++ джерел, `sdkconfig.defaults` і CSV-таблиці
розділів такого прецеденту немає; авторитетним джерелом є `02-RESEARCH.md` (Code Examples
1–5, Patterns 1–5) і PlatformIO. Нижче це позначено явно.

Усі названі аналоги перевірені `git ls-files -- <path>` — жоден шлях не походить із
gitignored install/runtime дзеркала.

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `platformio.shared.ini` (root, create) | config | data (declarative) | `policy/ruleset-main.json` — лише конвенція «закомічені дані як джерело істини» | partial (convention) |
| `scripts/pio/compiledb.py` (create) | utility / build hook | event-driven (SCons pre-script) | `scripts/check_pr_templates.py` | partial (Python house shape only) |
| `scripts/tests/test_pio_scripts.py` (create) | test | transform | `scripts/tests/test_check_pr_templates.py` | role-match |
| `lib/{common,port,arduino,espidf,host}/library.json` (5 create) | config (manifest) | data | `policy/repository.json` (JSON style only) | partial (style) |
| `lib/{common,port,arduino,espidf,host}/include/*.h` (5 create) | source (public header) | n/a | none | **none** |
| `lib/{common,port,arduino,espidf,host}/src/*.c` (5 create) | source (library impl) | n/a | none | **none** |
| `homeworks/0_0-toolchain-smoke/platformio.ini` (create) | config | data | none | **none** |
| `homeworks/0_0-toolchain-smoke/src/main.cpp` (create) | source (entry point) | control flow, 3 branches | none | **none** |
| `homeworks/0_0-toolchain-smoke/default_16MB.csv` (create) | data (partition table) | data | none | **none** |
| `homeworks/0_0-toolchain-smoke/sdkconfig.defaults` (create) | config (Kconfig fragment) | data | none | **none** |
| `homeworks/0_0-toolchain-smoke/README.md` (create) | documentation | n/a | root `README.md` | partial (typography) |
| `docs/decisions/0007-symlink-shared-libraries.md` (create) | documentation (ADR) | n/a | `docs/decisions/0006-public-commit-identity.md` | **exact** |
| `docs/decisions/README.md` (modify) | documentation (index) | n/a | itself | **exact** |
| `.gitignore` (modify) | config | n/a | itself | **exact** |
| `scripts/tests/test_gitignore.py` (modify) | test | transform | itself | **exact** |

**Coverage:** 6 exact/role-match, 6 partial, 11 no analog (рахуючи 3 файли-родини, що
розгортаються у 15 фізичних файлів: 5 `library.json`, 5 `.h`, 5 `.c`).

`REUSE.toml` **не змінюється**: catch-all `**` → MIT покриває `.ini`, `.c`, `.h`, `.cpp`,
`.json`, `sdkconfig.defaults`, `default_16MB.csv`; `homeworks/**/*.md` → CC-BY-4.0 уже
покриває новий README. Жодного per-file SPDX-заголовка не додавати.

---

## Pattern Assignments

### `platformio.shared.ini` (config, data)

**Analog:** немає жодного `.ini` у репозиторії. Конвенційний аналог —
`policy/ruleset-main.json`: закомічені дані, які описують контракт, тоді як перевірка
живе окремо. Тут перевірка — сам `pio run` (D-19/D-20), генератор — Фаза 5 (D-02/D-03).

**Джерело змісту:** `02-RESEARCH.md` §Pattern 1, повний блок (рядки 378-412). Копіювати
дослівно, включно з відступами у `build_flags` (4 пробіли, багаторядкове значення).

**Структурні правила, які planner мусить закодувати як задачі:**

- Рівно три секції без префікса `env:` — `[esp32s3_arduino]`, `[esp32s3_espidf]`,
  `[native_unity]`. Секції `[platformio]` тут **немає**: `extra_configs` оголошує кожен
  проєкт, інакше файл не знайде себе (D-01).
- `platform = espressif32@8.0.0` — точний пін (FOUND-09). `board = esp32-s3-devkitc-1`
  завжди з overrides D-14, ніколи «як є».
- `-DBOARD_HAS_PSRAM` — у `build_flags` `[esp32s3_arduino]` (D-22), окремий ключ, не
  частина списку D-14.
- `extra_scripts = pre:../../scripts/pio/compiledb.py` — шлях резолвиться відносно
  **директорії проєкту** (перевірено RESEARCH Pattern 5).
- `[native_unity]` **без** `test_framework` і без `test/` (D-16); назва збережена під
  Фазу 3.

**Застереження для planner (не рішення):** `build_flags` застосовуються і до C, і до C++
компіляції. Оскільки точка входу — `src/main.cpp` (D-15 amended), `-std=c11` у
`[native_unity]` потрапить у виклик `g++`, який дає попередження про невідповідний
стандарт. RESEARCH фіксує зелену збірку, але `-Werror` там не ввімкнено. Planner має
перевірити вивід `pio run -e native` на це попередження і свідомо вирішити: лишити
(документувати) або замінити на `-std=gnu11` лише для C-файлів бібліотек. Не виправляти
«на око» — спершу побачити вивід.

---

### `scripts/pio/compiledb.py` (utility / build hook, event-driven)

**Analog:** `scripts/check_pr_templates.py` — єдиний рід збігається частково: Python,
детермінований, комітиться в `scripts/`, але це CLI-перевіряльник, а не SCons-хук.

**House-форма Python-скрипта** (`scripts/check_pr_templates.py`, рядки 1-31): module
docstring, що пояснює *що і чому*, потім `from __future__ import annotations`, потім
лише stdlib-імпорти, потім константи модуля.

```python
#!/usr/bin/env python3
"""Verify the pull-request template contract.

...what it protects and why...

Usage:
  python3 scripts/check_pr_templates.py [--dir PATH]

Exit codes (a CI contract from Phase 8 onward):
  0  the template contract holds
  1  contract violation (...)
  2  usage or environment error (...)
"""

from __future__ import annotations

import argparse
import difflib
import re
import subprocess
import sys
from pathlib import Path
```

**Що копіювати:** docstring-стиль і дисципліну «лише stdlib».
**Що НЕ копіювати:** `#!/usr/bin/env python3`, `argparse`, `main()`, `sys.exit`,
`class CheckError`. `compiledb.py` виконується SCons-ом через `Import("env")`, а не як
CLI, тому аргументів і кодів виходу в нього немає.

**Зміст** — `02-RESEARCH.md` §Pattern 5 (рядки 515-527), дослівно:

```python
import os
Import("env")

env.Replace(COMPILATIONDB_INCLUDE_TOOLCHAIN=True)
env.Replace(COMPILATIONDB_PATH=os.path.join(env.subst("$PROJECT_DIR"), "compile_commands.json"))
```

Контракт, який planner має зафіксувати задачею:

- `pre:`-префікс у `extra_scripts` обов'язковий — скрипт мусить виконатися до побудови
  графа, інакше `Replace()` не вплине на ціль `compiledb`.
- `COMPILATIONDB_PATH` — один на проєкт і **перезаписується** кожним запуском (P7).
- Файл, який скрипт породжує, лишається gitignored (D-18; `.gitignore` рядок 16 уже
  містить `compile_commands.json`).
- Ніяких абсолютних шляхів, зашитих у файл: `$PROJECT_DIR` — єдине джерело.

---

### `scripts/tests/test_pio_scripts.py` (test, transform)

**Analog:** `scripts/tests/test_check_pr_templates.py` — та сама роль (тест
детермінованого скрипта), той самий раннер, та сама вимога працювати без мережі.

**Каркас тесту** (рядки 1-45 аналога):

```python
"""Tests for scripts/check_pr_templates.py.

The real-tree tests exercise the shipped contract end to end. Every negative
fixture copies the three templates into a temporary tree, mutates exactly one
property, and points the checker at the copy with ``--dir`` — the script's only
test seam.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import check_pr_templates

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "check_pr_templates.py"
```

**Критична відмінність, яку planner мусить закодувати:** аналог робить
`from scripts import check_pr_templates`. Для `scripts/pio/compiledb.py` цей рядок
**неможливий** — модуль викликає `Import("env")` на верхньому рівні, а `Import` існує
лише всередині SCons. Імпорт у звичайному `python3` впаде з `NameError`. Тому тест
перевіряє скрипт як *дані*, а не як модуль:

- `path.is_file()` — файл існує за шляхом, який згадує `platformio.shared.ini`;
- `ast.parse(text)` — синтаксис валідний без виконання;
- текст містить `Import("env")`, `COMPILATIONDB_PATH` і `$PROJECT_DIR` (контракт, а не
  реалізація);
- жодного абсолютного шляху (`/Users/`, `C:\\`) у файлі — вимога безпеки V5 цієї фази.

**Розташування:** `scripts/tests/test_pio_scripts.py` (RESEARCH §Wave 0 Gaps явно
вимагає участі в `python3 -m unittest discover -s scripts/tests`). `scripts/pio/` **не**
є пакетом, тому `from scripts.pio import compiledb` теж не працює — і не потрібен.

---

### `lib/*/library.json` × 5 (config manifest, data)

**Analog:** немає `library.json`. Стиль JSON — з `policy/ruleset-main.json` /
`policy/repository.json`: 2 пробіли, відсортовані ключі не обов'язкові, trailing newline,
без коментарів.

**Зміст** — `02-RESEARCH.md` Code Example 1 (рядки 739-748), дослівно для кожного з
п'яти імен:

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

Правила, які planner фіксує задачами:

- `name` **мусить** дорівнювати імені директорії (`common`, `port`, `arduino`,
  `espidf`, `host`) — `<name>=symlink://...` у `lib_deps` зв'язує їх, і LDF знаходить
  бібліотеку саме за цим ім'ям.
- `version` — єдине місце, де живе версія (D-12). `lib_deps` версію не несе ніколи.
- `build.srcDir`/`build.includeDir` обов'язкові (D-09) — без них LDF не побачить
  `src/*.c` за нестандартною назвою директорій.

---

### `lib/*/include/*.h` × 5 (public header, no analog)

**Analog:** немає — жодного `.h` у репозиторії. **Джерело:** `02-RESEARCH.md` Code
Example 3 (рядки 786-797) і Pitfall P2.

Кожен публічний заголовок **дослівно** в цій формі (це вимога лінкування, не стиль):

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

Імена символів (Claude's Discretion, але planner має зафіксувати одне ім'я на
бібліотеку, щоб тест і `main.cpp` не розійшлися):

| Бібліотека | Заголовок | Символ |
|---|---|---|
| `common` | `include/common.h` | `common_version(void)` |
| `port` | `include/port.h` | `port_version(void)` |
| `arduino` | `include/arduino_adapter.h` | `arduino_adapter_version(void)` |
| `espidf` | `include/espidf_adapter.h` | `espidf_adapter_version(void)` |
| `host` | `include/host.h` | `host_version(void)` |

`arduino_adapter.h`, `espidf_adapter.h` — це єдині заголовки, які тягнуть framework:
відповідний `.c` включає `<Arduino.h>` / `<driver/gpio.h>` (D-11), але **сам заголовок**
framework-заголовків не включає, інакше `common`/`port`/`native` отримають чужий
include-шлях.

---

### `lib/*/src/*.c` × 5 (library impl, no analog)

**Analog:** немає. **Джерело:** D-10, D-11 і P2.

Форма кожного файлу: `#include "<own>.h"`, потім єдина тривіальна функція, що повертає
рядок версії (`"0.1.0"`), наприклад:

```c
#include "common.h"

const char *common_version(void) { return "0.1.0"; }
```

`arduino_adapter.c` додатково включає `<Arduino.h>` і викликає одну тривіальну функцію
(наприклад `millis()`), `espidf_adapter.c` — `<esp_err.h>` (або `<driver/gpio.h>`) і одну
тривіальну API-функцію. Мета — довести, що framework-заголовок *резолвиться* під час
крос-компіляції, а не лише що компілятор існує (D-11).

**Ключове для planner:** джерела лишаються **чистим C** (D-15 amended). Не перейменовувати
на `.cpp` — це зламає вимогу «майбутні ESP-IDF/STM32 домашні в чистому C» і зробить
`extern "C"` непотрібним, але нешкідливим.

---

### `homeworks/0_0-toolchain-smoke/platformio.ini` (config, data)

**Analog:** немає — це перший `platformio.ini` у репозиторії. **Джерело:**
`02-RESEARCH.md` Code Example 2 (рядки 752-779).

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

Правила, які planner закодовує (усі з RESEARCH Pattern 1 / Pitfall P4):

- `[env:*]` містить **лише** `extends` і `lib_deps`. Будь-який `build_flags`,
  `extra_scripts` чи `src_filter` у проєкті — сигнал, що шаблон треба переробити:
  `extends` **замінює** спискові опції, не зливає їх.
- `extra_configs` живе тільки в `[platformio]` проєкту; шлях `../../` правильний для
  глибини `homeworks/<id>/`.
- `lib_deps` — це `name=symlink://../../lib/<name>`, без версії (D-12).
- Один `default_envs = native` дає змогу `pio run` без `-e` і відповідає D-19 (native
  перший).

---

### `homeworks/0_0-toolchain-smoke/src/main.cpp` (entry point, no analog)

**Analog:** немає джерел C/C++ узагалі. **Джерело:** `02-RESEARCH.md` Pattern 2
(рядки 428-444) і Pitfall P1.

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

Вимоги, які не можна «спростити»:

- Розширення **`.cpp`**, не `.c` (P1: інакше `undefined reference to '_Z5setupv'`).
- `extern "C"` навколо `app_main` (P1/A3).
- Третя гілка `int main(void)` для `native` — `app_main` не є точкою входу хост-програми.
- `common_version()` (і за бажанням `port_version()`, `host_version()`) **мусить**
  викликатися з тіла, щоб лінкер не викинув бібліотеку як невикористану (D-10). Краще
  роздрукувати результат через `printf`, щоб збірка ще й демонструвала зв'язування.

---

### `homeworks/0_0-toolchain-smoke/default_16MB.csv` (data, no analog)

**Analog:** немає. **Джерело:** `02-RESEARCH.md` Pattern 4 (рядки 500-509), дослівно.
Файл мусить лежати **в корені проєкту**: ESP-IDF-білдер шукає `default_16MB.csv` у
`framework-espidf/components/partition_table/`, де його немає, і падає з
`Missing partition table file` (P3). Це обов'язковий артефакт проєкту, а не «ще один
override» — D-14 лишається дослівним.

---

### `homeworks/0_0-toolchain-smoke/sdkconfig.defaults` (config, no analog)

**Analog:** немає. **Джерело:** `02-RESEARCH.md` Pattern 4 (рядки 493-498):

```ini
CONFIG_ESPTOOLPY_FLASHSIZE_16MB=y
CONFIG_SPIRAM=y
CONFIG_SPIRAM_MODE_OCT=y
```

Без нього — банер `Expected 16MB, found 2MB` і жодного octal PSRAM (P3). Це **не**
`build_flags`-прапорці: IDF генерує з нього `sdkconfig.<env>`, який потім і перевіряється
(доказ критерію 2).

---

### `homeworks/0_0-toolchain-smoke/README.md` (documentation)

**Analog:** кореневий `README.md` — типографіка (заголовок `#`, короткий абзац,
`**Status:**`-рядок, ~90 колонок). Структуру не копіювати: кореневий README описує
репозиторій, а цей файл — тимчасовий smoke-проєкт.

**Мінімум, який planner фіксує задачею** (D-07, Claude's Discretion щодо довжини):
файл явно каже, що проєкт **тимчасовий**, **не є coursework**, не має `homework.yaml`
і буде видалений у Фазі 3. Без цього речення публічний читач сприйме `homeworks/0_0-…`
як перше домашнє завдання — саме цього уникає D-07/D-08.

---

### `docs/decisions/0007-symlink-shared-libraries.md` (documentation, ADR)

**Analog:** `docs/decisions/0006-public-commit-identity.md` — **точний** збіг ролі; до
того ж `scripts/tests/test_adrs.py` механічно перевіряє структуру, тож відхилення від
нього — червоний тест, а не зауваження рев'ю.

**Frontmatter** (0006, рядки 1-7):

```markdown
---
status: accepted
date: 2026-10-23
decision-makers: [VLoktiev-EMB]
consulted: []
informed: []
---
```

**Decision Outcome відкривається дослівно** (вимога `test_adrs.py:227-237`):

```markdown
Chosen option: "{title of option}", because {justification}.
```

**Обов'язкові вісім секцій у цьому порядку** (`test_adrs.py:36-45`): `## Context and
Problem Statement` → `## Decision Drivers` → `## Considered Options` →
`## Decision Outcome` → `### Consequences` → `### Confirmation` →
`## Pros and Cons of the Options` → `## More Information`.

Додатково, з того ж тесту: щонайменше два `* `-пункти в Considered Options; для кожного
варіанта — `###`-підрозділ із рядками `* Good, because …` / `* Neutral, because …` /
`* Bad, because …`; **жодної email-адреси** в тексті (`test_adrs.py:169-173`).

**Зміст** (D-21 amended, D-05, D-12): `symlink://` проти задепрекейченого
`lib_extra_dirs`; версія живе лише в `library.json`; вибір обґрунтований тим, що LDF не
сканує весь `lib/`, і чужий адаптер не може потрапити в збірку; `Confirmation` посилається
на зелені збірки трьох env і на Phase 3 checker. Варіанти для `Pros and Cons` — рівно три
з RESEARCH §Alternatives Considered: `symlink://`, `lib_extra_dirs`, копіювання бібліотек
у кожен проєкт.

**Номер — 0007, не 0006** (D-21 amended; 0006 уже зайнятий `public-commit-identity`).

---

### `docs/decisions/README.md` (modify — index)

**Analog:** сам файл. Поточний хвіст (рядки 20-31) — статус-таблиця з чотирма колонками і
рядком «наступний номер»:

```markdown
| Number | Title | Status | Date |
|--------|-------|--------|------|
| 0006 | Public commit identity | accepted | 2026-10-23 |

Next number: **0007** (reserved for the Phase 2 symlink decision).
```

Задача: додати рядок `| 0007 | <точний title з ADR> | accepted | 2026-10-23 |` і оновити
рядок «Next number» на **0008**. `test_adrs.py:176-207` вимагає, щоб `number`, `title`,
`status` і `date` у таблиці **точно** збігалися з файлом ADR (`title` — рядок після `# `).
Розбіжність у регістрі чи формулюванні — падіння тесту.

---

### `.gitignore` (modify — config)

**Analog:** сам файл. Наявний блок ESP-IDF (рядки 8-13) — шаблон для нового блоку:

```gitignore
# ESP-IDF artifacts (regenerable by the component manager / build system)
# NOTE: `sdkconfig` and `dependencies.lock` are deliberately NOT ignored —
# they are per-project configuration and belong in version control.
sdkconfig.old
sdkconfig.old.*
managed_components/
```

**D-23 вимагає додати** (окремий блок із коментарем, що посилається на D-23): `CMakeLists.txt`,
`src/CMakeLists.txt`, `sdkconfig.<env>`.

**Критична колізія, яку planner мусить вирішити явно:** наявний коментар і
`scripts/tests/test_gitignore.py:124` тримають `sdkconfig` у списку **VISIBLE** — і це
правильно, це рукописна конфігурація проєкту. Тому шаблон має бути `sdkconfig.*`
(з точкою), а не `sdkconfig*`: перший ігнорує `sdkconfig.esp32s3_espidf`, але лишає
`sdkconfig` видимим. Шаблон без слеша матчить на будь-якій глибині, тож один
`CMakeLists.txt` покриває і корінь проєкту, і `src/`.

**Другорядний, але реальний розрив:** `.pre-commit-config.yaml` hook `no-generated-files`
(рядки 24-34) перелічує лише `compile_commands.json site .pio`. D-23 розширює *правило*,
але не цей hook — `git add -f CMakeLists.txt` пройде. Planner має або розширити `entry`
хука тими самими шляхами, або свідомо відкласти це й записати причину. Не мовчати.

---

### `scripts/tests/test_gitignore.py` (modify — test)

**Analog:** сам файл. Структура, яку треба продовжити — словник `IGNORED` за причинами
(рядки 56-96) і список `VISIBLE` (рядки 98-126):

```python
IGNORED = {
    "build output": [".pio/x", ".pioenvs/x", ".piolibdeps/x"],
    "generated files": ["compile_commands.json", "site/index.html", "out.log"],
    ...
}

VISIBLE = [
    ...
    # ESP-IDF per-project configuration belongs in version control; only the
    # regenerable artifacts (sdkconfig.old, managed_components/) are ignored.
    "sdkconfig",
    "dependencies.lock",
]
```

Задача: додати категорію `"esp-idf build-generated (D-23)"` з
`homeworks/0_0-toolchain-smoke/CMakeLists.txt`, `.../src/CMakeLists.txt`,
`.../sdkconfig.esp32s3_espidf` і **лишити** `sdkconfig` у `VISIBLE` — саме ця пара
перевірок ловить занадто широкий патерн. Якщо тест не оновити, зміна `.gitignore`
лишиться непокритою і регресія пройде мовчки.

---

## Shared Patterns

### 1. Python house style
**Source:** `scripts/check_pr_templates.py` (рядки 1-31, 240-268), `scripts/check_policy.py`
(рядки 1-21, 322-350).
**Apply to:** `scripts/pio/compiledb.py`, `scripts/tests/test_pio_scripts.py`.

```python
#!/usr/bin/env python3
"""<What this is.>

<Why it exists and what breaks without it.>

Usage:
  python3 scripts/<name>.py [--flag]

Exit codes (a CI contract from Phase 8 onward):
  0  ...
  1  ...
  2  ...
"""

from __future__ import annotations

import ...
```

Лише stdlib; `subprocess.run([...])` зі списком аргументів, ніколи `shell=True`;
`PASS:`/`FAIL:`-рядок на перевірку; `ERROR:` у `>&2`; один `return`-код наприкінці.
`compiledb.py` — виняток: він не CLI, тому без `argparse`/`sys.exit`, але docstring і
`from __future__` зберегти.

### 2. Резолюція кореня репозиторію
**Source:** `scripts/tests/test_gitignore.py` (рядки 21-31), `scripts/check_pr_templates.py`
(рядки 59-76).
**Apply to:** будь-який тест, що читає файли репозиторію.

```python
def _repo_root() -> Path:
    """Resolve the repository root so the suite runs from any working directory."""
    completed = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=True,
    )
    return Path(completed.stdout.strip())
```

Ніяких `Path(__file__).parents[N]` без перевірки — аналог пояснює чому: тест мусить
проходити з будь-якої робочої директорії.

### 3. Конфігурація як закомічені дані, перевірка — окремо
**Source:** `policy/*.json` + `scripts/check_policy.py` (Фаза 1), зафіксовано в
`01-PATTERNS.md` §`policy/ruleset-main.json`.
**Apply to:** `platformio.shared.ini`, `.gitignore`, `.gitignore`-тест.

Дані комітяться, дрейф ловить детермінована перевірка (`--check`). У цій фазі роль
«перевірки» для `platformio.shared.ini` виконує сам `pio run` + Python-assertions над
CDB/sdkconfig, а `--check`-генератор приходить у Фазі 5 — **не** описувати його як
наявний (D-03).

### 4. Доказ через інструмент, а не через конфіг
**Source:** RESEARCH §Anti-Patterns, §Validation Architecture.
**Apply to:** усі задачі-докази цієї фази.

`platformio.ini` описує намір; доказ — `esptool image-info`, токени в
`compile_commands.json` (`qio_opi`, `ARDUINO_PARTITION_default_16MB`) і
`.pio/build/esp32s3_espidf/config/sdkconfig.json`. Це узгоджується з наявною в
репозиторії звичкою `test_gitignore.py` питати `git check-ignore`, а не `grep` по файлу
(рядки 1-12): «reading either file as text would prove only that a string appears in it».

### 5. Markdown-типографіка
**Source:** `README.md`, `docs/decisions/0006-*.md`, `docs/decisions/README.md`.
**Apply to:** ADR-0007, README smoke-проєкту.

`##`/`###`-ієрархія, bold-lead bullets (`* Good, because …`), перенос ~90 колонок,
таблиці для структурних списків, fenced-блоки з мовним тегом.

### 6. Єдине джерело версії
**Source:** D-12 + `REUSE.toml` (конвенція «оголошується один раз»).
**Apply to:** `lib/*/library.json`, `lib_deps`.

Версія — лише в `library.json`. Якщо planner десь у `platformio.ini` чи в тесті пише
`common@0.1.0` — це вже другий осередок істини. Тест може перевіряти, що рядок
`"version": "0.1.0"` присутній у **кожному** з п'яти маніфестів, але не дублювати версію
в інших файлах.

### 7. Без абсолютних шляхів у закомічених файлах
**Source:** RESEARCH §Security Domain (V5, «Абсолютні шляхи в CDB»), `.gitignore` рядок 16.
**Apply to:** `platformio.shared.ini`, `platformio.ini`, `compiledb.py`,
`sdkconfig.defaults`, тест.

`symlink://../../lib/<name>`, `pre:../../scripts/pio/compiledb.py`, `$PROJECT_DIR` —
усі відносні або інтерпольовані. Жодного `/Users/...` у tracked-файлі.

---

## No Analog Found

Planner використовує вказане джерело замість пошуку прецеденту в кодовій базі.

| File | Role | Data Flow | Reason / Source |
|---|---|---|---|
| `platformio.shared.ini` | config | data | Жодного `.ini`, `.toml`-конфігу PlatformIO чи `extra_configs` у репозиторії. → RESEARCH Pattern 1 (рядки 336-412) |
| `lib/*/library.json` × 5 | config | data | Немає жодного маніфесту бібліотеки; стиль JSON успадковується від `policy/*.json`. → RESEARCH Code Example 1 |
| `lib/*/include/*.h` × 5 | source | n/a | Нуль `.h` у репозиторії. → RESEARCH Code Example 3 + P2 |
| `lib/*/src/*.c` × 5 | source | n/a | Нуль `.c`/`.cpp` у репозиторії. → D-10/D-11 |
| `homeworks/0_0-toolchain-smoke/platformio.ini` | config | data | Перший проєкт PlatformIO. → RESEARCH Code Example 2 |
| `.../src/main.cpp` | source (entry) | control flow | Немає точок входу, немає C++. → RESEARCH Pattern 2 + P1 |
| `.../default_16MB.csv` | data | data | Немає таблиць розділів. → RESEARCH Pattern 4 + P3 |
| `.../sdkconfig.defaults` | config | data | Немає Kconfig-фрагментів. → RESEARCH Pattern 4 + P3 |
| `.../README.md` | documentation | n/a | Лише типографіка кореневого README. → D-07/D-08 |
| `scripts/pio/compiledb.py` | utility (build hook) | event-driven | Немає SCons-скриптів; форма Python частково з `check_pr_templates.py`. → RESEARCH Pattern 5 |
| `scripts/tests/test_pio_scripts.py` | test | transform | Немає тесту для build-скрипта; каркас — з `test_check_pr_templates.py`, але без імпорту модуля. → RESEARCH §Wave 0 Gaps |

---

## Metadata

**Analog search scope:** увесь tracked-дерев (`git ls-files`, 76 файлів): `scripts/`,
`scripts/tests/`, `docs/decisions/`, `policy/`, `.github/`, кореневі конфіги. Перевірено
`ls -d homeworks lib scripts/pio` — усі три відсутні.
**Files scanned:** 12 прочитано (`check_policy.py`, `check_pr_templates.py`,
`test_check_pr_templates.py`, `test_gitignore.py`, `test_adrs.py`, `test_homework_id.py`,
`0002-*.md`, `0006-*.md`, `docs/decisions/README.md`, `template.md`, `REUSE.toml`,
`.gitignore`, `.pre-commit-config.yaml`, `README.md`, `infra.md`) + `01-PATTERNS.md` як
взірець формату.
**Tracked-source check:** кожен аналог перевірено `git ls-files -- <path>` → `TRACKED`.
Жодного шляху з `.gsd/capabilities/**` чи іншого gitignored дзеркала у файлі немає.
**Pattern extraction date:** 2026-10-23

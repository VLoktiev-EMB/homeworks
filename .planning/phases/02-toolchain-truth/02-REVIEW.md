---
phase: 02-toolchain-truth
reviewed: 2026-10-23T20:05:15Z
depth: standard
files_reviewed: 28
files_reviewed_list:
  - .gitignore
  - .pre-commit-config.yaml
  - docs/decisions/0007-symlink-shared-libraries.md
  - docs/decisions/README.md
  - homeworks/0_0-toolchain-smoke/README.md
  - homeworks/0_0-toolchain-smoke/default_16MB.csv
  - homeworks/0_0-toolchain-smoke/platformio.ini
  - homeworks/0_0-toolchain-smoke/sdkconfig.defaults
  - homeworks/0_0-toolchain-smoke/src/main.cpp
  - lib/arduino/include/arduino_adapter.h
  - lib/arduino/library.json
  - lib/arduino/src/arduino_adapter.c
  - lib/common/include/common.h
  - lib/common/library.json
  - lib/common/src/common.c
  - lib/espidf/include/espidf_adapter.h
  - lib/espidf/library.json
  - lib/espidf/src/espidf_adapter.c
  - lib/host/include/host.h
  - lib/host/library.json
  - lib/host/src/host.c
  - lib/port/include/port.h
  - lib/port/library.json
  - lib/port/src/port.c
  - platformio.shared.ini
  - scripts/pio/compiledb.py
  - scripts/tests/test_gitignore.py
  - scripts/tests/test_pio_scripts.py
findings:
  critical: 1
  warning: 4
  info: 7
  total: 12
status: issues_found
---

# Phase 02: Code Review Report

**Reviewed:** 2026-10-23T20:05:15Z
**Depth:** standard
**Files Reviewed:** 28
**Status:** issues_found

## Summary

Перевірено 28 файлів фази: спільну конфігурацію `platformio.shared.ini`, п'ять C-бібліотек з `library.json`, тимчасовий проєкт `homeworks/0_0-toolchain-smoke/`, генератор compilation database, правила `.gitignore`, pre-commit hook, ADR-0007 та два тест-модулі.

Перевірка не обмежувалась читанням: зібрано всі три середовища (`native`, `esp32s3_arduino`, `esp32s3_espidf`), згенеровано `compile_commands.json` для кожного, прогнано `python3 -m unittest discover -s scripts/tests -v` (122 тести, OK), `pre-commit run no-generated-files --all-files`, `reuse lint`, перевірено вміст `.pio-link`, бінарні таблиці розділів через `esptool image-info`, а також поведінку hook'а на тимчасовому індексі з примусово доданими згенерованими файлами.

Підтверджено: `-std=c11` справді потрапляє лише до C-компілятора (SCons 4.11.1 `Environment.py:1176-1181`), обидві ESP-прошивки мають `Flash size: 16MB`, таблиця розділів у `partitions.bin` обох середовищ збігається з `default_16MB.csv`, а заява ADR про застарілість `lib_extra_dirs` з 6.0 відповідає офіційній документації.

Головна проблема — не в поточній поведінці збірки, а в тому, що спільна конфігурація не є самодостатньою: вона посилається на `default_16MB.csv`, єдиний примірник якого лежить у тимчасовому проєкті, який ADR-0007 зобов'язується видалити у Phase 3. Друга системна проблема — тести й ADR описують контракт, який насправді не перевіряється.

Structural findings (fallow) у цьому запуску не надавалися, тому всі нижченаведені знахідки — narrative.

## Narrative Findings (AI reviewer)

### CR-01: Спільна конфігурація посилається на `default_16MB.csv`, єдиний примірник якого буде видалено у Phase 3

**Severity:** BLOCKER
**File:** `platformio.shared.ini:10`, `platformio.shared.ini:24`; `homeworks/0_0-toolchain-smoke/default_16MB.csv:1-7`; `docs/decisions/0007-symlink-shared-libraries.md:153-155`

**Issue:** Обидві секції (`esp32s3_arduino`, `esp32s3_espidf`) задають `board_build.partitions = default_16MB.csv`. PlatformIO розв'язує це значення відносно каталогу проєкту, тож файл мусить лежати в кожному `homeworks/<id>/`. Наразі єдиний примірник — у `homeworks/0_0-toolchain-smoke/`, а ADR-0007 (рядки 153-155) і `homeworks/0_0-toolchain-smoke/README.md:6-7` прямо кажуть, що цей каталог буде видалено у Phase 3. Після цього будь-який новий проєкт, що успадковує `esp32s3_arduino` або `esp32s3_espidf`, падає на старті: platform builder викликає `_parse_partitions()`, яка друкує `Could not find the file ... with partitions table` і робить `env.Exit(1)` (`platforms/espressif32/builder/main.py:122-128`; для ESP-IDF той самий `PARTITIONS_TABLE_CSV` формується в `frameworks/espidf.py`). Це не гіпотетичний ризик — це гарантована поломка спільного артефакту, який фаза і мала постачати.

**Fix:** Зробити таблицю розділів постійним спільним артефактом, а не деталлю тимчасового проєкту:

```ini
# platformio.shared.ini — шлях відносно каталогу проєкту, як і для lib_deps
[esp32s3_arduino]
board_build.partitions = ../../partitions/default_16MB.csv

[esp32s3_espidf]
board_build.partitions = ../../partitions/default_16MB.csv
```

Перенести `default_16MB.csv` у постійний каталог (наприклад, `partitions/`), додати тест, що файл, на який вказує `board_build.partitions`, існує, і згадати це в ADR-0007. Альтернатива — лишити копію на проєкт, але тоді вимогу «кожен homework копіює CSV» треба явно зафіксувати в ADR і перевіряти тестом.

### WR-01: Тести жорстко прив'язані до тимчасового smoke-проєкту і зламаються після Phase 3

**Severity:** WARNING
**File:** `scripts/tests/test_pio_scripts.py:38-39`, `scripts/tests/test_pio_scripts.py:127-131`, `scripts/tests/test_pio_scripts.py:196-204`

**Issue:** `PROJECT_INI` і `PROJECT_SRC` вказують на `homeworks/0_0-toolchain-smoke/`, який ADR-0007 зобов'язується видалити. `test_no_absolute_paths` викликає `PROJECT_INI.read_text()` (рядок 130), а `test_entry_point_is_cpp_and_library_sources_are_c` — `PROJECT_SRC.glob(...)` (рядок 198). Після видалення каталогу весь модуль падає з `FileNotFoundError`/`NotADirectoryError`, а не зі змістовним skip. Тобто документований ґейт `python3 -m unittest discover -s scripts/tests -v` стане червоним на етапі, який сам ADR вважає штатним.

**Fix:** Розділити тести на дві групи: контракт спільної конфігурації (`SHARED_INI`, `SCRIPT`) перевіряти завжди, а проєктно-специфічні — під умовним skip, напр.:

```python
@unittest.skipUnless(PROJECT_INI.is_file(), "temporary smoke project removed in Phase 3")
def test_no_absolute_paths_in_project_ini(self):
    ...
```

або одразу переспрямувати `PROJECT_INI`/`PROJECT_SRC` на постійний тестовий fixture, який переживе Phase 3.

### WR-02: ADR-0007 «Confirmation» заявляє чотири інваріанти, яких тести не перевіряють

**Severity:** WARNING
**File:** `docs/decisions/0007-symlink-shared-libraries.md:100-104`; `scripts/tests/test_pio_scripts.py:183-204`

**Issue:** ADR стверджує, що `scripts/tests/test_pio_scripts.py` фіксує контракт і що зміна, яка повертає `lib_extra_dirs`, копіює бібліотеку або додає друге оголошення версії, провалює набір. Фактично перевіряються лише: наявність трьох секцій, пін `espressif32@8.0.0`, шість ключів D-14, `extra_scripts` і збіг `name`/`version` у маніфестах. Не перевіряються:

- `lib_deps` у `homeworks/0_0-toolchain-smoke/platformio.ini` узагалі не читається — зміна `common=symlink://../../lib/common` на будь-який інший запис не провалить жодного тесту;
- секція `[env:native]`/`[env:esp32s3_arduino]`/`[env:esp32s3_espidf]` не перевіряється на `lib_extra_dirs` (перевіряється лише спільний INI, рядки 144-149);
- `extra_configs = ../../platformio.shared.ini` у проєкті не перевіряється — його видалення не провалить тести;
- заголовки не перевіряються на `extern "C"`, хоча ADR каже «pure C behind `extern "C"` headers»;
- копіювання бібліотеки в проєкт не виявляється взагалі;
- друге оголошення версії не лише не виявляється — воно вже існує (див. WR-03).

**Fix:** Додати відсутні перевірки, наприклад:

```python
def test_project_inherits_shared_config(self):
    parser = _read_config(PROJECT_INI)
    self.assertEqual(["../../platformio.shared.ini"], parser["platformio"]["extra_configs"])

def test_lib_deps_use_symlink_spelling(self):
    parser = _read_config(PROJECT_INI)
    for section in ("env:native", "env:esp32s3_arduino", "env:esp32s3_espidf"):
        for entry in parser[section]["lib_deps"].splitlines():
            self.assertRegex(entry.strip(), r"^[a-z]+=symlink://\.\./\.\./lib/[a-z]+$")
        self.assertNotIn("lib_extra_dirs", parser[section])
```

і аналогічно для `extern "C"`, версій та існування `default_16MB.csv`. Якщо якісь із цих гарантій не потрібні — прибрати їх із ADR, щоб запис не заявляв неправдивої перевірки.

### WR-03: Версія бібліотеки оголошена двічі — у `library.json` і в кожному `.c`

**Severity:** WARNING
**File:** `lib/common/src/common.c:3`, `lib/port/src/port.c:3`, `lib/host/src/host.c:3`, `lib/arduino/src/arduino_adapter.c:7`, `lib/espidf/src/espidf_adapter.c:7`; `lib/common/library.json:3` (аналогічно для решти)

**Issue:** ADR-0007 (рядки 63-65) прямо фіксує: «The version lives only in `library.json` (D-12); ... no other file repeats the version». Насправді кожен із п'яти `.c` повертає літерал `"0.1.0"`. Це два незалежні джерела істини: підняття версії в `library.json` до `0.2.0` залишить LDF-граф на `0.2.0`, а `printf` у `src/main.cpp` друкуватиме `0.1.0`, і жоден тест цього не помітить. ADR у такому вигляді описує стан, якого немає.

**Fix:** Або прибрати дублювання (наприклад, генерувати рядок версії з маніфесту під час збірки), або визнати два джерела та зв'язати їх тестом:

```python
literal = re.search(r'return "([^"]+)";', source.read_text()).group(1)
self.assertEqual(manifest["version"], literal, name)
```

і відкоригувати формулювання ADR-0007 відповідно до фактичної схеми.

### WR-04: Загальні шаблонні патерни `.gitignore` можуть тихо ховати авторські файли

**Severity:** WARNING
**File:** `.gitignore:106` (`*.d`), `.gitignore:115` (`*.map`), `.gitignore:136` (`*.out`), `.gitignore:183` (`build/`), `.gitignore:241` (`*.spec`), `.gitignore:285` (`target/`); `scripts/tests/test_gitignore.py:108-141`

**Issue:** Файл зібраний з кількох стандартних шаблонів, і частина патернів не має жодного відношення до PlatformIO, але може збігтися з авторськими артефактами курсової роботи: `*.out` — типове ім'я очікуваного результату тесту, `*.spec` — файл специфікації/тесту, `*.map` — карта зв'язку, яку інколи здають як доказ, `build/` і `target/` — довільні каталоги з тим самим ім'ям у будь-якому місці дерева. Наслідок — файл ніколи не потрапляє в коміт, автор бачить «чисте» дерево і не отримує жодної помилки. `VISIBLE` у тесті покриває лише конкретний перелік шляхів і ці випадки не ловить.

**Fix:** Звузити загальні патерни до відомих артефактів (наприклад, `firmware.out`, `build/` лише під конкретними каталогами) або додати явні винятки й представницькі записи у `VISIBLE`, скажімо:

```python
VISIBLE += [
    "homeworks/1_1-example/tests/expected.out",
    "homeworks/1_1-example/docs/design.spec",
    "homeworks/1_1-example/evidence/memory.map",
]
```

Якщо ці розширення справді ніколи не будуть авторськими — зафіксувати це рішення в ADR, а не лишати як побічний ефект шаблону.

### IN-01: `board_upload.maximum_size` перезаписується platform builder'ом, тому пін нічого не обмежує

**Severity:** INFO
**File:** `platformio.shared.ini:9`, `platformio.shared.ini:23`

**Issue:** Для Arduino `espressif32` викликає `_update_max_upload_size()` (`platforms/espressif32/builder/main.py:161-191`, виклик на рядках 408/412) і перезаписує `upload.maximum_size` розміром app-розділу з таблиці — тобто `0x640000` (6 553 600), а не `16777216`. Значення в INI не має ефекту, але `D14_KEYS` у тесті подає його як значущий пін.

**Fix:** Прибрати ключ або додати коментар, що реальну межу задає `board_build.partitions`; тест варто змінити так, щоб він перевіряв узгодженість CSV, а не неефективний ключ.

### IN-02: `.gitignore` містить дублікати та порожні заголовки секцій

**Severity:** INFO
**File:** `.gitignore:31` і `:192`, `:32` і `:378`, `:33`, `:196` і `:432`, `:36` і `:210`, `:40` і `:260`, `:41` і `:417`, `:43` і `:361`, `:63` і `:198`; порожні заголовки `:160-181`

**Issue:** Той самий патерн оголошено 2-3 рази (`compile_commands.json`, `site/`, `*.log`, `__pycache__/`, `.pytest_cache/`, `.ruff_cache/`, `.env`, `*.swp`), а блоки «Prerequisites», «Precompiled Headers», «Linker files», «Debugger Files», «Compiled Dynamic libraries», «Executables», «debug information files» залишились без жодного правила. Це ускладнює аудит: незрозуміло, який патерн є навмисним, а який — залишок шаблону.

**Fix:** Залишити по одному входженню на патерн і видалити порожні заголовки; поведінка не зміниться, а рев'ю стане однозначним.

### IN-03: README проєкту не містить команд відтворення доказів

**Severity:** INFO
**File:** `homeworks/0_0-toolchain-smoke/README.md:1-11`

**Issue:** README пояснює призначення проєкту й різницю тулчейнів, але не дає жодної команди, якою можна повторити докази з ADR: `pio run -e native`, `pio run -e esp32s3_arduino`, `pio run -e esp32s3_espidf`, `pio run -e <env> -t compiledb`, `esptool image-info`. Через рік відтворити перевірку можна лише реконструюючи її з ADR.

**Fix:** Додати короткий блок команд із очікуваним результатом (`[SUCCESS]`, `Flash size: 16MB`) у README.

### IN-04: `default_envs = native` не дає звичайному `pio run` перевірити ESP-середовища

**Severity:** INFO
**File:** `homeworks/0_0-toolchain-smoke/platformio.ini:2`

**Issue:** `pio run` без `-e` збирає лише `native`. Регресія в `esp32s3_arduino`/`esp32s3_espidf` (наприклад, у `board_build.*` або `build_flags`) не буде помічена стандартною командою, а тести не перевіряють успішність збірки ESP-середовищ.

**Fix:** Або лишити `native` для швидкості й додати CI-крок на всі три середовища, або задокументувати `pio run -e esp32s3_arduino -e esp32s3_espidf` як обов'язковий крок ґейту.

### IN-05: Назва `native_unity` обіцяє Unity-набір, якого ще немає, і `pio test -e native` не працює

**Severity:** INFO
**File:** `platformio.shared.ini:31`; `homeworks/0_0-toolchain-smoke/platformio.ini:6-10`

**Issue:** Секція зветься `native_unity`, але жодного `test/` каталогу чи залежності Unity немає. `pio test -e native` у проєкті завершується `TestDirNotExistsError`, а з кореня репозиторію — `PlatformIOProjectError`. Водночас `AGENTS.md` (крок 3) із Phase 2 вимагає запускати `pio test -e native`, тож документований ґейт зараз незапускний. Це відоме відкладення на Phase 3, але воно має бути явно позначене.

**Fix:** Або додати мінімальний `test/`-набір (навіть порожній із одним assert), або в `AGENTS.md`/README позначити крок 3 як активний лише після Phase 3, доки не з'явиться спільний тестовий проєкт.

### IN-06: ESP-IDF-середовище не успадковує `-Wall -Wextra`

**Severity:** INFO
**File:** `platformio.shared.ini:18-25`

**Issue:** `native_unity` і `esp32s3_arduino` задають `-Wall -Wextra`, а `esp32s3_espidf` — ні. Попередження в C-коді `lib/common`, `lib/port`, `lib/espidf` під ESP-IDF не з'являться, тоді як під двома іншими середовищами з'являться. Це не помилка збірки, але нерівномірне покриття.

**Fix:** Додати `build_flags = -Wall -Wextra` у `[esp32s3_espidf]` (за потреби з `-Wno-...` для шумних заголовків IDF).

### IN-07: Механізм PSRAM для Arduino не задокументований; `sdkconfig.defaults` діє лише на ESP-IDF

**Severity:** INFO
**File:** `homeworks/0_0-toolchain-smoke/sdkconfig.defaults:1-3`; `platformio.shared.ini:5-7`

**Issue:** `sdkconfig.defaults` читає лише ESP-IDF-збірка. Для Arduino `CONFIG_SPIRAM`/16 MB надходять із передкомпільованого варіанта `qio_opi`, який вибирається `board_build.arduino.memory_type = qio_opi`. ADR-0007 згадує лише результат («entry point preprocesses to `#define CONFIG_SPIRAM 1`»), але не механізм, тож читач може вирішити, що PSRAM вмикається через `sdkconfig.defaults` для обох фреймворків.

**Fix:** Додати один абзац у README/ADR: `sdkconfig.defaults` — джерело для `esp32s3_espidf`; для `esp32s3_arduino` еквівалентні налаштування приходять із `memory_type = qio_opi`.

---

_Reviewed: 2026-10-23T20:05:15Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_

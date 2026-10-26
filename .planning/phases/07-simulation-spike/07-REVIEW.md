---
phase: 07-simulation-spike
reviewed: 2026-10-26T16:01:12Z
depth: standard
files_reviewed: 13
files_reviewed_list:
  - docs/decisions/0014-simulator-selection.md
  - docs/decisions/README.md
  - docs/homeworks/1_3-police-flasher.md
  - generated.manifest
  - homeworks/1_3-police-flasher/README.md
  - homeworks/1_3-police-flasher/homework.yaml
  - homeworks/1_3-police-flasher/platformio.ini
  - homeworks/1_3-police-flasher/report.md
  - mkdocs.yml
  - pyproject.toml
  - scripts/pio/merge_firmware.py
  - scripts/tests/test_merge_firmware.py
  - scripts/tests/test_simulation_paths.py
findings:
  critical: 1
  warning: 6
  info: 6
  total: 13
status: issues_found
---

# Phase 07: Code Review Report

**Reviewed:** 2026-10-26T16:01:12Z
**Depth:** standard
**Files Reviewed:** 13
**Status:** issues_found

## Summary

Перевірено 13 файлів фази 07 (спайк симулятора): ADR-0014, оновлені твердження в
`report.md` і README, метадані та згенеровані подання, спільний post-action
`scripts/pio/merge_firmware.py` і два нові модулі тестів.

Що підтверджено виконанням, а не читанням:

* `uv run scripts/gen_views.py --all --check` — `UNCHANGED` для всіх 8 подань; хеші
  `generated.manifest` збігаються з файлами. Отже, `docs/homeworks/1_3-police-flasher.md`,
  `mkdocs.yml` і `generated.manifest` справді згенеровані, а не відредаговані вручну —
  окремого порушення тут немає.
* `uv run scripts/check_metadata.py` — `PASS`; `homework.yaml` зі `simulation.status:
  verified` відповідає схемі.
* `python3 -m unittest discover -s scripts/tests` — 378 тестів, `OK`; окремо
  `test_merge_firmware` (9 тестів) і `test_simulation_paths` (3 тести) проходять.
* `ruff check`, `yamllint`, `markdownlint-cli2`, `trailing-whitespace`,
  `end-of-file-fixer` — чисто.
* `wokwi-cli lint --offline` — exit 0, `Found 1 info`, текст
  `Part "esp" uses undocumented type "board-esp32-s3-devkitc-1"`; твердження ADR про
  undocumented part type точне.
* Заголовок фактично зібраного `firmware.merged.bin` — `e9 03 00 4f`, тобто bootloader з
  16 MB і QIO; `board_upload.flash_size = 16MB` справді доходить до `BoardConfig`, тому
  регресії в аргументах `--flash-mode`/`--flash-size` немає.

Головна знахідка — не косметика: `merge_firmware()` ігнорує код повернення
`env.Execute`, тому невдалий `esptool merge-bin` не провалює збірку. Інші знахідки
стосуються точності доказового ланцюга (implementation commit, повторюваність Velxio,
немаркована верхня межа квоти, надмірне твердження про те, що саме доводять тести) і
переносимості нового тесту на Windows.

## Critical Issues

### CR-01: Невдалий `esptool merge-bin` не провалює збірку — `pio run` лишається зеленим

**File:** `scripts/pio/merge_firmware.py:100-102`
**Issue:** `env.Execute(env.VerboseAction(...))` викликається як голий вираз, а його
результат відкидається. У SCons 4.11.1, який постачає PlatformIO,
`SCons.Environment.Environment.Execute` на невдачі **не кидає виняток**: він пише
`scons: *** Error N` у stderr і повертає статус. Це перевірено виконанням:

```text
before
scons: *** Error 1
false
returned: 1 -> no exception raised
after
```

`merge_firmware` — це Python-функція, зареєстрована через `env.AddPostAction`; вона
повертає `None`, тому SCons вважає post-action успішним. Наслідок: якщо `esptool`
відсутній у пакеті, впав на offset/вхідному файлі, переповнив диск або змінив CLI в
майбутньому релізі, `pio run -d homeworks/1_3-police-flasher` завершується з кодом 0, а
`firmware.merged.bin` лишається відсутнім або **старим**. Далі сценарій Wokwi або не
стартує, або спалить квоту на застарілому образі, а `.github/workflows/homework.yml`
(крок `pio run`) цього не побачить. Це порушує контракт кроку: «або merged-образ
створено, або збірка падає».

**Fix:** перевірити статус і перетворити його на помилку збірки. SCons перехоплює
`Exception` з Python-action і конвертує в `BuildError`, тому достатньо `RuntimeError`:

```python
status = env.Execute(
    env.VerboseAction(" ".join(command), "Merging firmware images into " + merged)
)
if status:
    raise RuntimeError(
        f"merge_firmware: esptool merge-bin failed with status {status}"
    )
```

Додати регресійний тест зі stub-env, у якому `Execute` повертає ненульовий статус, і
перевірити, що дія кидає виняток (див. IN-02).

## Warnings

### WR-01: Заявлений implementation commit більше не є останнім комітом, що змінює build/simulation inputs

**File:** `homeworks/1_3-police-flasher/report.md:19-27` (також `:298-310`, `:350`)
**Issue:** Таблиця метаданих каже `Implementation commit: 9e1238d`, а абзац нижче
стверджує: «The recorded commit is the last commit that changes the homework's source,
build, or simulation inputs; every commit after it changes only documentation, and the
source, build, and simulation diff from `9e1238d` to the working tree is empty». Це
хибно:

* `a370a7f` (`feat(phase-6)`) змінив `src/main.cpp`, `lib/pattern/src/controller.c`,
  `lib/pattern/src/pattern.c` і тести — тобто source-вхід;
* `60a4aac` (ця фаза) змінив `homeworks/1_3-police-flasher/platformio.ini` (`post:` на
  спільний скрипт) і **видалив** `homeworks/1_3-police-flasher/merge_firmware.py` —
  тобто build- і simulation-входи.

Отже, `git diff 9e1238d -- homeworks/1_3-police-flasher/{src,lib,test,platformio.ini,merge_firmware.py}`
не порожній. Фаза оновила сусідні simulation-твердження (§7, L-08, T-15, §9, Додаток 7),
але не оновила сам якір походження, тому звіт тепер суперечить власному T-15, який
називає `../../scripts/pio/merge_firmware.py`.

**Fix:** оновити `Implementation commit` на останній коміт, що торкається source/build/
simulation-входів (наразі `60a4aac`), або переформулювати абзац: назвати коміт, який
описує прошивку, і прямо зазначити, що build/simulation-входи пізніше змінювалися.
Стовпець implementation commit у ledger (зокрема L-08) привести у відповідність.

### WR-02: Рядок Velxio в матриці ролей суперечить власному доказовому стовпцю щодо STM32

**File:** `docs/decisions/0014-simulator-selection.md:61`
**Issue:** Колонка `Platforms` для Velxio перелічує «AVR, RP2040 and the ESP32 family,
including ESP32-S3» і **не згадує STM32**. У тому самому рядку колонка `Evidence depth`
каже «simulator catalogue `47` boards observed, including ESP32-S3 and STM32 boards», а
`07-SPIKE-EVIDENCE.md` (рядки 268-275) прямо фіксує STM32 Blue Pill / Black Pill у
каталозі й зазначає: «STM32 simulation is therefore not Renode-exclusive in principle,
although no STM32 run was attempted here». Читач ADR не може зрозуміти, чи STM32
покриває Velxio, Renode, чи жоден із них, і чому Renode лишається роллю для STM32 попри
спостережений каталог.

**Fix:** додати STM32 до спостереженого каталогу в колонці `Platforms` (наприклад,
«observed catalogue also shows STM32 Blue/Black Pill; no STM32 run was attempted») і
пояснити, чому роль STM32 усе одно закріплена за Renode (непідтверджена модель курсової
плати, відсутність STM32-домашньої роботи й board-профілю), а не мовчазно виключати
STM32 з рядка Velxio.

### WR-03: «Booted reproducibly» / «repeatable» для Velxio — властивість, якої не вимірювали

**File:** `docs/decisions/0014-simulator-selection.md:51-53`, `:61`, `:196`
**Issue:** Evidence містить **один** boot: `docker run` від mutable-тегу `:master`,
перший HTTP 200 на 9-й спробі через `16.988 s`, digest записано вже після запуску через
`docker inspect`. ADR на цій підставі каже «Velxio booted reproducibly», «Boot readiness
`16.988 s` `measured` from the digest-pinned image» і «its boot is digest-pinned and
repeatable». Повторюваність boot як вимірювана властивість не встановлена (n=1), а
«digest-pinned» описує записану ідентичність, тоді як контейнер стартував із mutable-тегу.
Evidence це розрізняє коректно; ADR — ні.

**Fix:** замінити на «booted once from an image whose digest was recorded as …» і
прибрати «repeatable» або явно означити його як повторюваність *ідентичності* образу, а
не boot-інтервалу.

### WR-04: У Consequences верхня межа квоти подана як фактичне споживання

**File:** `docs/decisions/0014-simulator-selection.md:169-170`
**Issue:** «three runs consumed `45 s` of a `50 min` window, and a larger matrix would
exhaust the budget». Evidence прямо каже, що dashboard before/after не надано, а `45 s` —
це `calculated (upper bound)` від `--timeout 15000`. У цьому bullet кваліфікатор
втрачено, хоча той самий ADR наполягає на ньому в таблицях (рядки 95-96, 124-125).
Твердження «a larger matrix would exhaust the budget» з 45 s на 50 min арифметично не
підкріплене: до вичерпання потрібно приблизно у 66 разів більше запусків.

**Fix:** «three runs consumed at most `45 s` (`calculated (upper bound)`), because the
dashboard delta was not supplied; a substantially larger matrix would approach the
`50 min` window». Не подавати bound як observed consumption.

### WR-05: ADR приписує `test_merge_firmware` доведення створення merged-образу

**File:** `docs/decisions/0014-simulator-selection.md:180-181`
**Issue:** «`python3 -m unittest scripts.tests.test_merge_firmware -v` proves the shared
merge action produces the merged image the scenario flashes». Насправді тести
викликають лише `build_merge_command`, `esptool_directory` і `esptool_binary`; вони не
викликають `merge_firmware()`, не запускають `esptool`, не перевіряють `AddPostAction` і
не перевіряють шлях `firmware.merged.bin`. Створення образу доводить evidence-файл
(`firmware.merged.bin`, `0x5da00` байтів), а не цей тест.

**Fix:** переформулювати: «proves the merge command assembly; the produced
`firmware.merged.bin` is recorded in `07-SPIKE-EVIDENCE.md`». Якщо потрібне саме
доведення дії — додати тест на `merge_firmware()` (IN-02).

### WR-06: `test_merge_firmware` не переноситься на Windows, хоча перевіряє Windows-гілку

**File:** `scripts/tests/test_merge_firmware.py:22`, `:110-115`, `:189-197`
**Issue:** Модуль під тестом імпортує `join` з `os.path` під час імпорту. На Windows це
`ntpath.join`, тому фактичні значення містять `\`, а очікувані рядки в тестах
жорстко записані з `/`:

```text
ntpath.join("/build/esp32s3_arduino", "firmware.merged.bin")
  -> '/build/esp32s3_arduino\\firmware.merged.bin'
ntpath.join("/packages/tool-esptool", "esptool.exe")
  -> '/packages/tool-esptool\\esptool.exe'
```

`test_output_target` і `test_windows_binary_name` впадуть на Windows-хості. Останній
патчить лише `os.name`, але не семантику `join`, тому його «Windows coverage» хибне на
будь-якому хості. Репозиторій документує `python3 -m unittest discover -s scripts/tests`
як робочу команду, тож червоний тест у Windows-контриб'ютора — реальна регресія
зручності.

**Fix:** будувати очікувані шляхи через `os.path.join`/`pathlib`, а для Windows-кейсу
патчити саме `join`:

```python
with mock.patch("scripts.pio.merge_firmware.os.name", "nt"), \
     mock.patch("scripts.pio.merge_firmware.join", ntpath.join):
    ...
```

## Info

### IN-01: `_quote` не нейтралізує shell-метасимволи, а board-значення взагалі не цитуються

**File:** `scripts/pio/merge_firmware.py:38-40`, `:66-89`
**Issue:** `_quote` лише обгортає значення в подвійні лапки й не екранує `"`, `$`,
backtick або `%` (на Windows). Docstring обмежує trust boundary «repository-controlled
paths», але `--chip`, `--flash-mode` і `--flash-size` беруться з `BoardConfig` пакета
платформи і не цитуються зовсім. Додатково `build_merge_command` повертає список уже
shell-цитованих слів, тому його не можна безпечно передати в shell-free executor як
argv — лапки стануть частиною аргументу.
**Fix:** використовувати `shlex.quote` для кожного аргументу або будувати argv-список і
виконувати його без shell; для board-значень додати валідацію за allowlist
(`qio|dio|qout|dout`, `^[0-9]+MB$`, `^esp32[a-z0-9-]*$`).

### IN-02: Немає тесту на саму дію `merge_firmware()` і на шлях помилки

**File:** `scripts/tests/test_merge_firmware.py:99-197`
**Issue:** Покриті лише чисті хелпери. Не перевірено: реєстрація
`env.AddPostAction("$BUILD_DIR/${PROGNAME}.bin", merge_firmware)`; гілка `env is None`
(модуль імпортується без SCons); поведінка при ненульовому статусі `env.Execute`
(див. CR-01). Docstring модуля обіцяє «the two esptool failure modes», але це лише
відсутність пакета й відсутність директорії, не помилка виконання.
**Fix:** додати stub-env тести: `Execute` → `1` має призводити до винятку; `AddPostAction`
викликається з правильним target; без SCons нічого не реєструється.

### IN-03: Тест шляхів Wokwi тихо скіпається, а `scripts/tests` не запускається в CI

**File:** `scripts/tests/test_simulation_paths.py:33-38`, `:52-72`
**Issue:** За відсутності `wokwi-cli` `setUp` робить `skipTest`, і загальний прогін
лишається зеленим. Жоден workflow не запускає `scripts/tests`, тому твердження ADR
«proves the documented Wokwi command resolves its diagram and scenario paths» істинне
лише на машині з установленим CLI. Крім того, тест виконує команду з додатковими
`--elf` і `--timeout`, яких немає в задокументованій у README команді, — це перевірка
path-resolution, а не дослівний запуск.
**Fix:** додати job для `scripts/tests` (Фаза 8) або явно зафіксувати умову скіпу в ADR;
називати тест «path-resolution probe», а не «the documented command».

### IN-04: Твердження «3/3» не несе застереження про відсутні serial-log файли запусків 2-3

**File:** `docs/decisions/0014-simulator-selection.md:60-61`
**Issue:** Evidence фіксує, що `--serial-log-file` для запусків 2 і 3 зберіг літерал
`<N>`, тому окремих serial-log файлів немає; лінію `I pattern ready` для цих запусків
узято зі stamped-виводу. Це розкрито в evidence, але ADR подає «exactly one
`I pattern ready` serial line (3/3)» без цього застереження.
**Fix:** додати «(run 1 from its serial log; runs 2-3 from the stamped CLI output)» або
переформулювати як «3/3 captured streams» замість «serial line».

### IN-05: Коментар у `pyproject.toml` називає не той символ, а ignore занадто широкий

**File:** `pyproject.toml:18-21`
**Issue:** Коментар каже «SCons injects `env` into these scripts», але ruff F821
спрацьовує на `Import` (ім'я, якого немає в чистому Python), а не на `env`. До того ж
`scripts/pio/*.py` — файловий, а не точковий ignore; `merge_firmware.py` уже має
власний `# noqa: F821`, тож ignore для нього надлишковий і водночас приховує будь-який
реальний F821 у цих скриптах.
**Fix:** уточнити коментар («`Import` is injected by SCons») і звузити ignore до
`compiledb.py` або конкретного рядка.

### IN-06: ADR каже «referenced by its immutable digest», але digest у ADR відсутній

**File:** `docs/decisions/0014-simulator-selection.md:158`
**Issue:** «The Velxio image is AGPLv3 and is referenced only, by its immutable digest» —
проте самого digest (`sha256:5d67…`) у ADR немає, він лише в
`07-SPIKE-EVIDENCE.md`. Читач ADR не може відтворити посилання на образ без переходу в
raw-запис, а формулювання обіцяє більше, ніж документ містить.
**Fix:** навести digest у ADR (у text-блоці) або замінити на «referenced only via the
digest recorded in `07-SPIKE-EVIDENCE.md`».

---

_Reviewed: 2026-10-26T16:01:12Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_

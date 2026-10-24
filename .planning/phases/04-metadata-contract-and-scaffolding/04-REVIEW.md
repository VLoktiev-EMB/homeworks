---
phase: 04-metadata-contract-and-scaffolding
reviewed: 2026-10-24T21:22:02Z
depth: standard
files_reviewed: 57
files_reviewed_list:
  - .pre-commit-config.yaml
  - AGENTS.md
  - NOTICE
  - REUSE.toml
  - docs/decisions/0009-homework-metadata-contract.md
  - docs/decisions/0010-python-dependency-policy.md
  - docs/decisions/README.md
  - schema/homework.schema.json
  - scripts/check_metadata.py
  - scripts/metadata/__init__.py
  - scripts/metadata/allowlist.json
  - scripts/metadata/contract.py
  - scripts/new_homework
  - scripts/tests/fixtures/golden/homework-arduino/README.md
  - scripts/tests/fixtures/golden/homework-arduino/assets/.gitkeep
  - scripts/tests/fixtures/golden/homework-arduino/homework.yaml
  - scripts/tests/fixtures/golden/homework-arduino/include/.gitkeep
  - scripts/tests/fixtures/golden/homework-arduino/platformio.ini
  - scripts/tests/fixtures/golden/homework-arduino/src/main.cpp
  - scripts/tests/fixtures/golden/homework-arduino/task.md
  - scripts/tests/fixtures/golden/homework-arduino/test/test_homework/test_homework.c
  - scripts/tests/fixtures/golden/homework-espidf/README.md
  - scripts/tests/fixtures/golden/homework-espidf/assets/.gitkeep
  - scripts/tests/fixtures/golden/homework-espidf/homework.yaml
  - scripts/tests/fixtures/golden/homework-espidf/include/.gitkeep
  - scripts/tests/fixtures/golden/homework-espidf/platformio.ini
  - scripts/tests/fixtures/golden/homework-espidf/sdkconfig.defaults
  - scripts/tests/fixtures/golden/homework-espidf/src/main.cpp
  - scripts/tests/fixtures/golden/homework-espidf/task.md
  - scripts/tests/fixtures/golden/homework-espidf/test/test_homework/test_homework.c
  - scripts/tests/temp_root.py
  - scripts/tests/test_adrs.py
  - scripts/tests/test_homework_metadata.py
  - scripts/tests/test_metadata_deps.py
  - scripts/tests/test_new_homework.py
  - scripts/tests/test_templates.py
  - templates/adr/template.md
  - templates/board-profile/profile.yaml
  - templates/homework-arduino/README.md
  - templates/homework-arduino/assets/.gitkeep
  - templates/homework-arduino/homework.yaml
  - templates/homework-arduino/include/.gitkeep
  - templates/homework-arduino/platformio.ini
  - templates/homework-arduino/src/main.cpp
  - templates/homework-arduino/template.yaml
  - templates/homework-arduino/test/test_homework/test_homework.c
  - templates/homework-espidf/README.md
  - templates/homework-espidf/assets/.gitkeep
  - templates/homework-espidf/homework.yaml
  - templates/homework-espidf/include/.gitkeep
  - templates/homework-espidf/platformio.ini
  - templates/homework-espidf/sdkconfig.defaults
  - templates/homework-espidf/src/main.cpp
  - templates/homework-espidf/template.yaml
  - templates/homework-espidf/test/test_homework/test_homework.c
  - templates/report/report.md
  - templates/task/task.md
findings:
  critical: 2
  warning: 5
  info: 8
  total: 15
status: issues_found
---

# Phase 04: Code Review Report

**Reviewed:** 2026-10-24T21:22:02Z
**Depth:** standard
**Files Reviewed:** 57
**Status:** issues_found

## Summary

Перевірено контракт метаданих (`schema/homework.schema.json`, `scripts/metadata/contract.py`),
перевірник `scripts/check_metadata.py`, скаффолд `scripts/new_homework`, шаблони, golden-фікстури,
тести та правила (ADR-0009, ADR-0010, `AGENTS.md`, `.pre-commit-config.yaml`, `REUSE.toml`).
Загалом архітектура «один валідатор, два споживачі» реалізована послідовно: перевірник і скаффолд
справді імпортують один модуль, схема строга (`additionalProperties: false`, жодного `format`),
exit-коди задокументовані й перевірені тестами. Наявні тести проходять (75 тестів
`test_homework_metadata` + `test_new_homework`, 48 тестів `test_templates`/`test_adrs`/`test_homework_id`,
9 тестів `test_metadata_deps`), але вони не покривають два відтворені дефекти безпеки/коректності:
запис за межі `homeworks/` через symlink у дереві цілі та необроблений `TypeError` на YAML-ключі
складеного типу.

Найважливіше: (1) скаффолд пише файли за межі `homeworks/`, якщо проміжний каталог цілі є symlink,
і завершується з кодом 0; (2) YAML-документ із ключем-послідовністю чи ключем-мапою валить перевірник
traceback-ом, а `--json` не друкує жодного масиву, що ламає задокументований CI-контракт.

## Critical Issues

### CR-01: Symlink у дереві цілі дозволяє запис за межі `homeworks/` (і звітує хибний шлях)

**File:** `scripts/new_homework:245-283`, `scripts/new_homework:324-347`

**Issue:** `_contained_target()` перевіряє лише кінцевий каталог `homeworks/<id>` через `resolve()`,
а `_classify()` перевіряє symlink тільки на самій цілі (`target.is_symlink()`). Жоден проміжний
компонент шляху не перевіряється, тому наявний symlink `homeworks/<id>/src -> <будь-де>` проходить
як «CREATE», і `_write_all()` через `target.parent.mkdir(..., exist_ok=True)` + `tempfile.mkstemp(dir=target.parent)`
пише `main.cpp` у каталог поза репозиторієм.

Відтворено на одноразовому root:

```text
mkdir -p homeworks/1_3-x outside
ln -s "$PWD/outside" homeworks/1_3-x/src
uv run scripts/new_homework 1_3-x --template arduino --dir "$ROOT"
# exit=0, stderr порожній
# homeworks/1_3-x/src/main.cpp: CREATE — target does not exist
# outside/main.cpp створено (1535 байт)
```

Це прямо суперечить docstring `scripts/new_homework:23` («a target that escapes `homeworks/`» → exit 2),
D-20 («any other existing content is CONFLICT, including a symlink, which is classified without ever
being followed») і D-24 (containment). Другий варіант того ж кореня: symlink на самому
`homeworks/<id>` (наприклад, на `homeworks/sub/1_3-x`) теж приймається; план звітує
`homeworks/1_3-x/...`, а байти лягають у `homeworks/sub/1_3-x/...`, і `_homework_directory()`
(`contract.py:567-575`) повертає `None`, бо шлях після `resolve()` має 4 компоненти, тому інваріант
`id == каталог` тихо пропускається.

**Fix:** відхиляти symlink і на кінцевому каталозі цілі, і на кожному проміжному компоненті, а
перевірку робити до класифікації:

```python
def _contained_target(root, homework_id):
    base = (root / "homeworks").resolve()
    target = base / homework_id
    if target.is_symlink():
        raise CheckError(f"homeworks/{homework_id} is a symlink; refusing")
    resolved = target.resolve()
    try:
        resolved.relative_to(base)
    except ValueError as exc:
        raise CheckError(
            f"target homeworks/{homework_id} escapes the homeworks directory"
        ) from exc
    return resolved


def _classify(target, data, target_dir):
    current = target.parent
    while current != target_dir:
        if current.is_symlink():
            return "CONFLICT", f"parent {current.name} is a symlink; refusing to follow it"
        current = current.parent
    ...
```

Додатково варто перевіряти `target.parent.resolve()` на належність `target_dir/resolve()` і додати
тест на обидва варіанти symlink-у (проміжний каталог і сам `homeworks/<id>`).

### CR-02: YAML-ключ складеного типу валить перевірник `TypeError`-ом; `--json` не друкує масиву

**File:** `scripts/metadata/contract.py:87-99`, `scripts/metadata/contract.py:115-127`, виклик — `scripts/check_metadata.py:212-213`

**Issue:** Обидва strict-завантажувачі роблять `key = self.construct_object(key_node, deep=deep)` і
потім `if key in seen:`. Для YAML-ключа-послідовності (`? [a, b]`) або ключа-мапи `construct_object`
повертає `list`/`dict`, і `in set` кидає `TypeError: cannot use 'list' as a set element`. `TypeError`
не є `yaml.YAMLError`, тому його не ловить ні `validate_homework_text`, ні `validate_task_text`.
Перевірка `isinstance(document, dict)` не рятує, бо падіння стається всередині побудови мапи.

Відтворено і для `homework.yaml`, і для frontmatter `task.md`:

```text
# homeworks/1_3-x/homework.yaml
? [a, b]
: c
$ uv run scripts/check_metadata.py --dir "$R" --json
Traceback ... TypeError: cannot use 'list' as a set element (unhashable type: 'list')
exit=1, stdout порожній
```

Порушено задокументовані контракти: «a content problem ... stays at exit 1» як ERROR-запис
(`scripts/check_metadata.py:23-26`) і «`--json` prints one JSON array ... and nothing else»
(`scripts/check_metadata.py:29-31`). CI-споживач `--json` отримує порожній stdout і traceback у stderr.
Тест `test_duplicate_*_key_is_error` покриває лише скалярні ключі, тому дефект не виявлено.

**Fix:** не використовувати `set` для довільних ключів і делегувати unhashable-випадок `super()`,
який штатно кидає `ConstructorError` (підклас `YAMLError`). Заодно викликати `flatten_mapping`
до сканування, щоб `<<:` не вважався невідомим тегом:

```python
def construct_mapping(self, node, deep=False):
    self.flatten_mapping(node)
    seen = []
    for key_node, _ in node.value:
        key = self.construct_object(key_node, deep=deep)
        try:
            duplicate = key in seen
        except TypeError:          # unhashable key: let super() raise ConstructorError
            continue
        if duplicate:
            raise ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key {key!r}",
                key_node.start_mark,
            )
        seen.append(key)
    return super().construct_mapping(node, deep=deep)
```

Додати регресійні тести для `homework.yaml` і `task.md` з `? [a, b]` та для merge-ключа.

## Warnings

### WR-01: Allowlist пригнічує один запис на один entry, а не весь шлях

**File:** `scripts/metadata/contract.py:423-444`

**Issue:** `apply_allowlist` витрачає один entry на один Cyrillic-запис (`if not matched[index] ... break`).
Якщо `task.md` містить кирилицю у двох рядках, один entry з шляхом цього файлу пригнічує лише перший
рядок, а другий лишається ERROR. Щоб приховати файл, потрібно двічі повторити той самий path+reason;
два однакові entry для файлу з одним рядком, навпаки, дають «stale». Це суперечить опису «Suppress
Cyrillic records by exact path» і не покрито тестами (тест `test_allowlist_suppresses_the_exact_path`
має лише один кириличний рядок).

Відтворено:

```text
apply_allowlist([rec(line=8), rec(line=9)], [{"path": "homeworks/1_3-x/task.md", ...}])
-> ([rec(line=9)], [])      # часткове пригнічення, entry позначено використаним
```

**Fix:** позначати entry використаним для всіх записів цього шляху:

```python
for item in records:
    if item.get("rule") != CYRILLIC_RULE:
        remaining.append(item)
        continue
    index = next(
        (i for i, entry in enumerate(entries) if entry["path"] == item["path"]),
        None,
    )
    if index is None:
        remaining.append(item)
    else:
        matched[index] = True
```

Додати тест із двома кириличними рядками і одним entry.

### WR-02: Наявний звичайний файл на місці проміжного каталогу класифікується як CREATE

**File:** `scripts/new_homework:245-263`, `scripts/new_homework:338-347`

**Issue:** `_classify` питає лише `target.exists()`. Якщо `homeworks/<id>/src` — звичайний файл, то
`homeworks/<id>/src/main.cpp` не існує (`ENOTDIR` → `exists()` False), тому план каже
`CREATE — target does not exist`, після чого `_write_all` пише частину файлів, падає на
`target.parent.mkdir()` з `FileExistsError` і повертає exit 2. Твердження D-24 «validation and conflict
detection happen before the first `mkdir`, so a validation or conflict failure cannot leave a partial
project» для цього випадку не виконується, хоча конфлікт детектується ще на етапі планування.

Відтворено:

```text
mkdir -p homeworks/1_3-x; : > homeworks/1_3-x/src
uv run scripts/new_homework 1_3-x --template arduino --dir "$ROOT"
# exit=2; README.md, homework.yaml, platformio.ini, assets/.gitkeep, include/.gitkeep уже записані
```

**Fix:** перевіряти батьківський шлях у `_classify` (після перевірки symlink-ів із CR-01):

```python
if target.parent.exists() and not target.parent.is_dir():
    return "CONFLICT", "a parent path exists and is not a directory"
```

і додати тест, що такий план не робить жодного запису.

### WR-03: `framework`/`board` — мертві елементи мапінгу; board id дублюється без перевірки

**File:** `scripts/new_homework:88`, `scripts/new_homework:136-142`, `scripts/new_homework:204-214`; `AGENTS.md:48-49`; `templates/board-profile/profile.yaml`

**Issue:** `_mapping()` повертає ключі `board` і `framework`, а `_template_manifest()` вимагає
`framework`, але жоден шаблон не містить `{{board}}` чи `{{framework}}` (перевірено grep-ом по
`templates/`). Реальний `framework` зашитий у кожному `templates/homework-*/homework.yaml`, а `board`
зашитий там же і в `new_homework.BOARD`. `templates/board-profile/profile.yaml` не читає жоден
виконуваний файл, хоча `AGENTS.md:48-49` стверджує, що `board-profile/` «rendered only by
`scripts/new_homework`». Наслідок: (а) копіювання шаблону з іншим `template.yaml: framework`
не змінює відрендерений `framework` і не дає помилки; (б) зміна board id у профілі не впливає на
скаффолд — ідентифікатор плати дублюється у 4 місцях (`profile.yaml`, два `homework.yaml`, `BOARD`,
а також `platformio.shared.ini`) без жодної перевірки узгодженості.

**Fix:** або підключити ці поля (додати `{{board}}`/`{{framework}}` у `homework.yaml`-шаблони і читати
board id з `templates/board-profile/profile.yaml`), або прибрати `board`/`framework` з `_mapping`,
`BOARD` і `PLACEHOLDER_NAMES`, та виправити `AGENTS.md:48-49`. Як мінімум — додати перевірку
`manifest["framework"]` проти відрендереного `homework.yaml`.

### WR-04: Regex лінтера плейсхолдерів не збігається з regex рендерера

**File:** `scripts/tests/test_templates.py:87` проти `scripts/new_homework:79`

**Issue:** лінтер використовує `\{\{([A-Za-z_][A-Za-z0-9_]*)\}\}`, а рендерер — `\{\{([^{}]*)\}\}`.
Токени, які скаффолд відхилить як «unknown placeholder», проходять лінтер: `{{}}`, `{{1bad}}`,
`{{ spaced }}`, `{{a.b}}`. Тобто зламаний шаблон може пройти `python3 -m unittest` і впасти лише під
час `scripts/new_homework`, хоча docstring модуля обіцяє «a closed placeholder vocabulary» і
«a broken expression cannot pass silently».

**Fix:** використати ту саму експресію, що й рендерер, і перевіряти кожен токен на належність
`PLACEHOLDER_NAMES` (плюс явно відхиляти порожній/пробільний токен):

```python
PLACEHOLDER = re.compile(r"\{\{([^{}]*)\}\}")
...
for token in PLACEHOLDER.findall(text):
    self.assertIn(token, PLACEHOLDER_NAMES)
```

### WR-05: Golden-diff не бачить зміни line-ending та фінального newline

**File:** `scripts/tests/test_new_homework.py:105-129` (особливо `117-119`)

**Issue:** `assert_golden` порівнює байти лише щоб вирішити, чи будувати diff, а сам diff будується
через `.decode("utf-8").splitlines()`. `"a\r\nb\r\n".splitlines()` і `"a\nb\n".splitlines()` дають
однаковий список, тому перехід LF→CRLF або зникнення фінального newline не дає жодного рядка diff і
`assertEqual([], differences)` проходить. Це послаблює заявлену гарантію «any unintended change to a
rendered file visible as a unified diff» — саме та зміна, яку D-20 забороняє («no line-ending
translation»), лишається невидимою.

**Fix:** додати пряме порівняння байтів перед людським diff:

```python
for name in sorted(expected):
    self.assertEqual(
        expected[name], actual[name],
        f"bytes differ for {name}",
    )
    # або difflib.diff_bytes, якщо потрібен саме текстовий diff
```

## Info

### IN-01: Вироджені `id` дають порожній display-title

**File:** `scripts/metadata/contract.py:480-499`; `schema/homework.schema.json:20`

**Issue:** канонічний regex `^[0-9]+_[0-9]+-[a-z0-9-]+$` дозволяє `1_3--` і `1_3-a-`. `derive_parts`
дає для них `title` `" "` і `"A "` відповідно; `title: " "` проходить `minLength: 1`, тому
`scripts/new_homework 1_3-- --template arduino` завершується з кодом 0 і створює homework із
порожнім заголовком. **Fix:** після `title = slug.replace("-", " ").title()` відхиляти результат,
що після `strip()` порожній (або звузити канонічний literal — це вимагає синхронної зміни
`AGENTS.md`, схеми, `contract.py` і `EXPECTED_PATTERN`).

### IN-02: `toolchain.platformio` не звіряється з `PLATFORMIO_CORE`

**File:** `scripts/metadata/contract.py:613-621`, `scripts/metadata/contract.py:75`

**Issue:** перевіряється лише `toolchain.platform` проти `platformio.shared.ini`; `toolchain.platformio`
перевіряється тільки схемою на форму `x.y.z`. Homework може задекларувати `platformio: "6.0.0"` і
пройти, хоча скаффолд завжди рендерить `PLATFORMIO_CORE = "6.2.0"`, що послаблює заявлену
відтворюваність. **Fix:** додати `if platformio != PLATFORMIO_CORE: errors.append(...)`.

### IN-03: YAML merge-ключі відхиляються як «invalid YAML»

**File:** `scripts/metadata/contract.py:87-99`, `scripts/metadata/contract.py:115-127`

**Issue:** duplicate-скан відбувається до `flatten_mapping`, тому `<<: *base` дає
`ConstructorError: could not determine a constructor for the tag 'tag:yaml.org,2002:merge'` і
перевірник повідомляє «invalid YAML», хоча документ валідний. Не критично (контракт хоче
явності), але повідомлення вводить в оману. **Fix:** див. фрагмент у CR-02 — `flatten_mapping`
перед циклом.

### IN-04: Не-рядкове значення provenance повідомляється як «value is empty»

**File:** `scripts/metadata/contract.py:227-233`

**Issue:** `BaseLoader` перетворює `attribution: [a, b]` на `list`, і перевірка
`not isinstance(value, str) or not value.strip()` видає `attribution: value is empty`, хоча значення
непорожнє. **Fix:** окреме повідомлення `f"{field}: value must be a string"` для не-рядкових значень.

### IN-05: Файли скаффолда отримують mode 0600; SIGKILL лишає temp-файли

**File:** `scripts/new_homework:324-336`

**Issue:** `tempfile.mkstemp` створює файл із mode `0600`, і `os.replace` зберігає цей mode, тому
відрендерені файли в робочому дереві відрізняються від звичайних `0644` (спостерігається на
`homework.yaml`, `README.md`, `platformio.ini`). Крім того, `BaseException`-обробка не спрацьовує
на `SIGKILL`, і `.new_homework-*` лишається в каталозі цілі. **Fix:** після `os.fdopen`/`write`
виставити `os.chmod(temporary, 0o666 & ~umask)` перед `os.replace`.

### IN-06: `temp_root.render_tree` — мертвий код

**File:** `scripts/tests/temp_root.py:61-121`

**Issue:** `render_tree` не викликається ніде (grep по `*.py`/`*.sh` не знаходить споживача), а
`build_root(source_root=...)` ніколи не викликається з аргументом, хоча docstring стверджує, що
`render_tree` «exists to build the committed golden fixtures». Генератора golden-фікстур у репозиторії
немає. **Fix:** або додати детермінований генератор фікстур, або прибрати `render_tree` і параметр
`source_root`, щоб не створювати хибного враження, що golden можна перегенерувати.

### IN-07: Недосяжний `except CheckError` у фазі запису

**File:** `scripts/new_homework:428-435`

**Issue:** `_write_all`/`_write_atomic` кидають лише `OSError`; `CheckError` у цьому блоці
недосяжний (він виникає тільки під час планування). Мертва гілка ускладнює читання. **Fix:** лишити
тільки `except OSError`.

### IN-08: Каскадна помилка `task.md` при невалідному `homework.yaml`

**File:** `scripts/metadata/contract.py:332-370`

**Issue:** `validate_candidate` повторно парсить `homework.yaml` і при `yaml.YAMLError` підставляє
`document = {}`, після чого `status = None`, і `validate_task_text` додає до звіту
`source_url: the sentinel 'TODO' is allowed only while status is 'planned', not None` — на додачу до
справжньої причини (невалідний YAML). Діагностика стає оманливою, особливо в `scripts/new_homework`,
де план показує помилку на `task.md`, а не на корені. **Fix:** не викликати `validate_task_text`,
якщо `validate_homework_text` уже повернув ERROR для невалідного/немап-документа (передавати
`status=None` лише тоді, коли документ успішно розпарсено).

---

_Reviewed: 2026-10-24T21:22:02Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_

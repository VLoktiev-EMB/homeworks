---
phase: 04-metadata-contract-and-scaffolding
reviewed: 2026-10-24T21:47:49Z
depth: standard
files_reviewed: 4
files_reviewed_list:
  - scripts/metadata/contract.py
  - scripts/new_homework
  - scripts/tests/test_homework_metadata.py
  - scripts/tests/test_new_homework.py
findings:
  critical: 0
  warning: 3
  info: 6
  total: 9
status: issues_found
---

# Phase 04: Code Review Report

**Reviewed:** 2026-10-24T21:47:49Z
**Depth:** standard
**Files Reviewed:** 4
**Status:** issues_found

## Summary

Перевірено чотири файли, які несуть два gap-closure-зміни: `scripts/new_homework` (lstat-обхід
компонентів цілі в плані 04-06) і `scripts/metadata/contract.py` (`apply_allowlist` з
path-ключем та `Hashable`-делегування в обох strict-завантажувачах у плані 04-07), разом із
двома тестовими модулями.

Обидві заявлені правки справді працюють і закривають те, що обіцяють:

- symlink на проміжному компоненті цілі тепер дає `CONFLICT` на кожному кандидаті під ним
  (відтворено: `homeworks/1_3-fixture/src -> <outside>` → exit 1, зовнішній каталог порожній,
  symlink цілий);
- symlink на самому `homeworks/<id>` дає exit 2 до друку плану;
- звичайний файл на місці проміжного каталогу більше не класифікується як `CREATE`;
- `? [a, b]` і в `homework.yaml`, і в frontmatter `task.md` дає ERROR-запис із
  `found unhashable key`, `--json` друкує один масив, traceback відсутній;
- один allowlist-entry пригнічує всі кириличні записи свого шляху, а не перший;
  non-Cyrillic-запис на тому ж шляху лишається, entry при цьому не стає stale.

Повний набір `scripts.tests.test_homework_metadata` + `scripts.tests.test_new_homework`
проходить: 82 тести, OK. Додатково поведінка перевірена прямими запусками модулів
(`validate_homework_text`, `validate_candidate`, `apply_allowlist`, `new_homework.main`)
на одноразових root-ах.

Критичних дефектів у цих чотирьох файлах не знайдено. Водночас контейнмент-правка 04-06 має
два залишкові вікна (WR-06, WR-07), а один із нових тестів 04-07 проходить із хибної причини
(WR-08). Раніше зафіксовані CR-02, WR-01 і WR-02 закрито; CR-01 закрито для компонентів
**під** `homeworks/`, залишок винесено в WR-06. Раніше зафіксовані IN-03, IN-05, IN-07, IN-08
лишаються відкритими й перепідтверджені нижче; IN-01, IN-02, IN-04, IN-06 стосуються ділянок,
яких ця хвиля не торкалася, і далі відстежуються в `04-REVIEW-DISPOSITION.md`.

## Warnings

### WR-06: Symlink на самому `homeworks/` обходить контейнмент і тихо вимикає перевірку `id`

**File:** `scripts/new_homework:322-358` (`_contained_target`, особливо `331`), `scripts/new_homework:249-293` (`_component_conflict`, `261`)

**Issue:** Обхід компонентів починається з `Path("homeworks")` і ніколи не робить `lstat`
самого `homeworks`. Якщо `homeworks` — symlink (наприклад, на теку поза репозиторієм), то
`base.resolve()`, з яким порівнюється `resolved`, вказує на ту саму зовнішню теку, тому
`relative_to()` проходить, план друкує `homeworks/<id>/...`, а `_write_all` пише файли за
межами кореня репозиторію з exit 0. Це той самий клас, що й CR-01, але вужчий: атакувальнику
достатньо контролювати один компонент дерева вище.

Відтворено з реальною валідацією (`homeworks -> <tmp>/elsewhere`, обидва шаблони не змінені):

```text
uv run scripts/new_homework 1_3-fixture --template arduino --dir "$ROOT"
# exit: 0
# homeworks/1_3-fixture/README.md: CREATE — target does not exist
# фактично записано у <tmp>/elsewhere/1_3-fixture/: README.md, assets, homework.yaml,
# include, platformio.ini, src, task.md, test  (8 файлів)
```

Другий, коректнісний наслідок: `_homework_directory()` (`contract.py:581-589`) резолвить
кандидатний шлях, не знаходить його під `root` і повертає `None`, тому явна перевірка
`id == homeworks/<dir>` у `validate_candidate` тихо пропускається. Відтворено: шаблон із
`id: "9_9-other"`, скаффолд у `homeworks/1_3-fixture` під symlinked `homeworks` → **exit 0**
(для звичайного `homeworks` той самий вхід дає exit 1). Homework створюється з порушеним
інваріантом ідентичності й потім падає на `check_metadata`.

**Fix:** перевіряти кореневий компонент так само, як решту, і вимагати, щоб резолвнутий
`homeworks` був рівно `<root>/homeworks`:

```python
base = root / "homeworks"
try:
    base_mode = os.lstat(base).st_mode
except FileNotFoundError:
    base_mode = None
except OSError as exc:
    raise CheckError(f"cannot inspect homeworks: {exc}") from exc
if base_mode is not None and stat.S_ISLNK(base_mode):
    raise CheckError("homeworks is a symlink; refusing to follow it")
```

Плюс у `_homework_directory()` виводити каталог із лексичного шляху (`Path(path).parts`), а не з
`resolve()`, щоб перевірка ідентичності не зникала через symlink. Додати регресійний тест:
`homeworks -> outside`, `--dry-run` і реальний запуск → exit 2, зовнішня тека порожня.

### WR-07: Між планом і записом шлях перевіряється лише один раз (TOCTOU)

**File:** `scripts/new_homework:414-423` (`_write_all`), `scripts/new_homework:400-411` (`_write_atomic`)

**Issue:** Гарантія «never followed» (T-04-22) діє лише на момент побудови плану. `_write_all`
згодом знову проходить шлях звичайними `pathlib`-викликами: `target.parent.mkdir(parents=True,
exist_ok=True)` розгортає symlink, а `os.replace(temporary, target)` пише за ним. Якщо
проміжний компонент (наприклад, `homeworks/<id>/src`) замінити на symlink після класифікації,
`mkdir(exist_ok=True)` завершиться успішно, і байти ляжуть у теку поза `homeworks/` — той самий
escape, який закривав CR-01, лише у вікні між планом і записом. Вікно вимагає локального
конкурентного актора, але саме цю властивість модуль заявляє як безумовну (`scripts/new_homework:26-35`,
`249-259`).

**Fix:** повторно перевіряти компоненти безпосередньо перед кожним записом (дешево, план уже
порахував `payloads`) і перервати run на будь-якому конфлікті:

```python
def _write_all(payloads, ordered, base):
    for record in ordered:
        if record["status"] != "CREATE":
            continue
        target, data = payloads[record["path"]]
        conflict = _component_conflict(base, target.relative_to(base))
        if conflict is not None:
            raise CheckError(f"{record['path']}: {conflict[1]}")
        target.parent.mkdir(parents=True, exist_ok=True)
        _write_atomic(target, data)
```

Сильніший варіант — тримати дескриптор каталогу (`os.open(..., O_DIRECTORY | O_NOFOLLOW)`) і
писати через `os.open(name, O_CREAT | O_EXCL | O_NOFOLLOW)` + `os.rename(src, dst,
src_dir_fd=..., dst_dir_fd=...)`.

### WR-08: Тест «allowlisted path still rejects a shape violation» не перевіряє пригнічення

**File:** `scripts/tests/test_homework_metadata.py:441-457`

**Issue:** У фікстурі цього тесту немає жодного кириличного символу — лише `source_url:
not-a-url`. Тому `validate_task_text` повертає ERROR-запис **без** `rule`, `apply_allowlist`
не пригнічує нічого і додає entry до `stale`. Перевірено напряму:

```text
A records: [{'path': 'homeworks/1_3-good/task.md', 'status': 'ERROR',
             'reason': "source_url: 'not-a-url' is not an http(s) URL", 'line': 0}]
A remaining, stale: ([<той самий ERROR>], [{'path': 'homeworks/1_3-good/task.md', ...}])
```

Тест проходить і тоді, коли `apply_allowlist` узагалі не застосовується (наприклад,
`return records, entries`), — тобто заявлена властивість «allowlist пригнічує лише Cyrillic-rule,
а shape-violation на тому ж шляху лишається» не доведена: entry у цьому сценарії не є
використаним. Це дає хибну впевненість саме в тій частині gap-closure, яку план 04-07 називає
prohibition.

**Fix:**

```python
def test_allowlisted_path_still_rejects_a_shape_violation(self):
    self.write_homework(
        task_text=TASK_TEMPLATE.replace(
            "source_url: TODO", "source_url: not-a-url"
        )
        + self.WORD
        + "\n"
    )
    self.write_allowlist([...])
    result = self.run_fixture()
    self.assert_rejected(result, "not an http(s) URL")
    self.assertNotIn("stale allowlist entry", result.stdout)
```

Другий `assertNotIn` доводить, що entry справді використаний, а не «випав» як stale.

## Info

### IN-03: YAML merge-ключі відхиляються як «invalid YAML»

**File:** `scripts/metadata/contract.py:88-108`, `scripts/metadata/contract.py:124-141`

**Issue:** Цикл duplicate-перевірки виконується **до** `flatten_mapping`, тому `<<: *base` у
`homework.yaml` дає `ConstructorError: could not determine a constructor for the tag
'tag:yaml.org,2002:merge'`, і користувач бачить «invalid YAML», хоча документ валідний.
Відтворено через `validate_homework_text` на реальному шаблоні. Дефект fail-closed, тому не
критичний, але діагностика оманлива, а duplicate-гарантія визначена на неflattened-вузлі.
**Fix:** у `StrictSafeLoader.construct_mapping` викликати `self.flatten_mapping(node)` перед
циклом (для `StrictBaseLoader` merge-семантики немає — лишити як є, `<<` тоді стає невідомим
ключем frontmatter і падає fail-closed). Врахувати, що `flatten_mapping` сам перезаписує
дублікати з merge, тож для повної duplicate-гарантії перевіряти вже flattened-результат.

### IN-05: Файли скаффолда отримують mode 0600; SIGKILL лишає temp-файли

**File:** `scripts/new_homework:400-411`

**Issue:** `tempfile.mkstemp` створює файл із `0600`, `os.replace` зберігає цей режим. На
одноразовому root усі вісім відрендерених файлів мають `0o600` замість звичайних `0644`, що
відрізняє їх від решти дерева й ламає очікування інших інструментів/користувачів. Обробка
`BaseException` не спрацьовує на `SIGKILL`, тому `.new_homework-*` лишається в каталозі.
**Fix:** `os.fchmod(descriptor, 0o666 & ~umask)` (або `0o644`) перед записом.

### IN-07: Недосяжний `except CheckError` у фазі запису

**File:** `scripts/new_homework:506-508`

**Issue:** `_write_all`/`_write_atomic` кидають лише `OSError`; `CheckError` у цьому блоці
недосяжний (він виникає тільки під час планування). Мертва гілка ускладнює читання й
приховує, що фактичний контракт фази запису — лише `OSError`. **Fix:** лишити тільки
`except OSError`.

### IN-08: Каскадна помилка `task.md` при невалідному `homework.yaml`

**File:** `scripts/metadata/contract.py:333-385` (особливо `346-351` і `372-384`)

**Issue:** `validate_candidate` повторно парсить `homework.yaml`; на `yaml.YAMLError`
підставляється `document = {}`, після чого `status = None`, і `validate_task_text` додає
чотири записи `... the sentinel 'TODO' is allowed only while status is 'planned', not None`.
Перевірено: невалідний `homework.yaml` породжує справжню помилку плюс чотири оманливі на
`task.md`. **Fix:** не викликати `validate_task_text` (або не застосовувати D-39), коли
`homework.yaml` не вдалося розпарсити; щонайменше — рендерити «статус невідомий» замість
`not None`.

### IN-09: Дублікати allowlist-entry ніколи не стають stale

**File:** `scripts/metadata/contract.py:449-457` (`allowed_paths`, `used_paths`), `scripts/metadata/contract.py:420-434` (`load_allowlist`)

**Issue:** `used_paths` — множина шляхів, тому два entry з однаковим `path` обидва вважаються
використаними, навіть якщо другий нічого не пригнічує. Перевірено:
`apply_allowlist(records, ENTRY + ENTRY) -> ([...], [])`. Таким чином allowlist може
накопичувати дублікати (і суперечливі `reason`) без жодного сигналу, хоча інваріант D-16 —
«entry, що нічого не пригнітив, є stale». **Fix:** у `load_allowlist` відхиляти повторний
`path` як `CheckError`, або рахувати stale по entry, а не по шляху.

```python
seen_paths = set()
for entry in validated:
    if entry["path"] in seen_paths:
        raise CheckError(f"{where}: duplicate allowlist path {entry['path']!r}")
    seen_paths.add(entry["path"])
```

### IN-10: Літеральний BOM-символ у виклику `lstrip`

**File:** `scripts/metadata/contract.py:174`

**Issue:** Символ U+FEFF вшитий у джерело невидимим літералом у виклику `lstrip`. Поведінка
правильна (перевірено: `task.md` з BOM парситься, номери рядків у Cyrillic-записах
збігаються), але такий літерал невидимий у diff-ах, його легко видалити випадково, і саме він
спричиняє спрацювання сканера invisible-unicode на цьому файлі. **Fix:** записати escape
явно — `text.lstrip("\N{ZERO WIDTH NO-BREAK SPACE}")`.

---

_Reviewed: 2026-10-24T21:47:49Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_

---
phase: 04-metadata-contract-and-scaffolding
reviewed: 2026-10-24T22:15:30Z
depth: standard
files_reviewed: 4
files_reviewed_list:
  - scripts/metadata/contract.py
  - scripts/new_homework
  - scripts/tests/test_homework_metadata.py
  - scripts/tests/test_new_homework.py
findings:
  critical: 0
  warning: 8
  info: 9
  total: 17
status: issues_found
---

# Phase 04: Code Review Report

**Reviewed:** 2026-10-24T22:15:30Z
**Depth:** standard
**Files Reviewed:** 4
**Status:** issues_found

> **Supersedes** the 2026-10-24T21:47:49Z report of this file (commit `d958855`).
> Ця версія перевіряє той самий scope після трьох gap-closure-планів: 04-06
> (`bf5a4cf`), 04-07 (`e75ea52`, `ed3c661`) і 04-08 (`45e8176`, `d65619f`).

## Summary

Перевірено чотири файли, які несуть увесь контракт metadata і скаффолдингу. Обидві
заявлені правки 04-08 справді працюють, і це підтверджено прямими запусками, а не
лише читанням:

- symlink на `homeworks/` тепер дає exit 2 з порожнім stdout (і для `--dry-run`, і для
  реального запуску), link лишається цілим, зовнішній каталог порожній
  (`scripts/new_homework:337-355`; відтворено);
- symlink на `homeworks/`, що вказує **всередину** root, теж відхиляється — контракт
  «ніколи не йти за base» не залежить від цілі;
- `homeworks` як звичайний файл дає exit 2 `homeworks exists and is not a directory`,
  файл не змінюється;
- нормальний tree: перший запуск exit 0 з `CREATE`, другий — exit 0 лише з
  `UNCHANGED` (ідемпотентність D-20 не порушена);
- `_homework_directory` справді більше не викликає `resolve()`/`realpath`, і
  id-перевірка тепер спрацьовує під symlinked-предком (перевірено на реальному
  symlink-дереві).

Водночас три нові дефекти внесені або оголені саме цією хвилею (WR-10, WR-11, WR-12),
один раніше не зафіксований дефект скаффолда знайдено поруч із правками (WR-09), і всі
дев'ять findings попереднього звіту або закриті, або лишаються відкритими з доказами
нижче. WR-09 — єдиний дефект, що порушує **записану prohibition** плану 04-04
(«must never silently skip a template entry it cannot render or copy»), і його варто
закрити до завершення фази.

**Як перевірялося.** Повний `uv run`-набір у цьому середовищі відтворити неможливо:
offline-кеш `uv` не містить `jsonschema`, тому `scripts/check_metadata.py` не
запускається. Усі твердження нижче отримані прямим імпортом
`scripts/metadata/contract.py` і `scripts/new_homework` на одноразових root-ах
(`temp_root.build_root`) зі стабом `jsonschema`, який не виконує schema-перевірку.
Там, де висновок залежить від schema, це сказано окремо; для WR-09, WR-10, WR-11 і
IN-11 сам висновок (набір файлів, деривація шляху, `path` запису, exit code) від
schema не залежить. Тестові модулі прочитані повністю, регресії зіставлені з
твердженнями 04-06/04-07/04-08-SUMMARY.

## Critical Issues

Немає. Security-дефекту, data-loss-ризику або обходу контейнменту з authored-input
не знайдено: `_contained_target` + `_component_conflict` закривають детермінований
escape, а залишкове вікно (WR-07) потребує локального конкурентного актора.

## Warnings

### WR-07: Між планом і записом шлях перевіряється лише один раз (TOCTOU) — STILL OPEN

**File:** `scripts/new_homework:424-435` (`_write_atomic`, `os.replace` на `432`), `scripts/new_homework:438-447` (`_write_all`)

**Issue:** Гарантія «never followed» діє лише на момент побудови плану. `_write_all`
знову проходить шлях звичайними `pathlib`-викликами: `target.parent.mkdir(parents=True,
exist_ok=True)` розгортає symlink, `tempfile.mkstemp(dir=target.parent)` створює
temp-файл за ним, а `os.replace(temporary, target)` пише туди ж. Окремий наслідок:
`os.replace` **перезаписує** файл, що з'явився на місці `CREATE`-цілі після
планування, — тобто no-overwrite тримається лише на класифікації, не на `O_EXCL`.

**Failure scenario (відтворено):** план будується, коли `homeworks/1_3-fixture/src`
ще немає (усі записи `CREATE`); далі `src` замінюється symlink-ом на зовнішній
каталог; `_write_all(payloads, ordered)` завершується без помилки, і
`outside/main.cpp` містить байти шаблону:

```text
plan statuses: ['CREATE']
files written outside homeworks: ['main.cpp']
```

Плани 04-06/04-08 оголосили це прийнятим боргом (T-04-28), але module docstring
(`scripts/new_homework:30-35`) і далі формулює властивість безумовно.

**Fix:** повторно перевіряти компоненти безпосередньо перед кожним записом і
відкривати ціль ексклюзивно:

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
        _write_atomic(target, data)   # os.open(..., O_CREAT|O_EXCL|O_NOFOLLOW)
```

Мінімум — прибрати безумовність із docstring: «перевіряється на момент планування».

### WR-08: Тест «allowlisted path still rejects a shape violation» досі не перевіряє пригнічення — STILL OPEN

**File:** `scripts/tests/test_homework_metadata.py:441-457`

**Issue:** У фікстурі немає жодного кириличного символу — лише
`source_url: not-a-url`. Тому `validate_task_text` повертає ERROR-запис **без**
`rule`, `apply_allowlist` не пригнічує нічого і додає entry до `stale`. Тест
`assert_rejected(result, "not an http(s) URL")` проходить, навіть якщо
`apply_allowlist` замінити на `return records, entries`: заявлена властивість
«allowlist пригнічує лише Cyrillic-rule, а shape-violation лишається» не доведена,
бо entry у цьому сценарії не є використаним (04-07 зафіксував це як prohibition).

**Fix:** додати кириличний рядок і довести, що entry використаний, а не «випав»:

```python
text = TASK_TEMPLATE.replace(
    "source_url: TODO", "source_url: not-a-url"
) + self.WORD + "\n"
...
self.assert_rejected(result, "not an http(s) URL")
self.assertNotIn("stale allowlist entry", result.stdout)
```

### WR-09: `os.walk` тихо пропускає недоступний каталог шаблону — exit 0 з неповним проєктом

**File:** `scripts/new_homework:160` (`os.walk(template_dir, followlinks=False)`), контракт — `scripts/new_homework:28-37`, `151-158` (docstring), 04-04 prohibition

**Issue:** `os.walk` викликається без `onerror`, тому будь-яка помилка `scandir`
(EACCES, EIO) мовчки ігнорується. Каталог не потрапляє в обхід, його файли не стають
кандидатами, `_build_plan` перевіряє лише наявність `homework.yaml` і `task.md` — і
запуск завершується **exit 0** з неповним проєктом. Це прямо порушує записану
prohibition 04-04 («must never silently skip a template entry it cannot render or
copy; … an unresolvable path must be reported and must stop the run») і truth FOUND-01
(«creates the eight FOUND-01 paths from either template»).

**Failure scenario (відтворено):** `chmod 000 templates/homework-arduino/src`,
`new_homework 1_3-fixture --template arduino --dry-run`:

```text
exit: 0 | stderr: (порожній)
main.cpp in plan: False
planned paths: README.md, assets/.gitkeep, homework.yaml, include/.gitkeep,
               platformio.ini, task.md, test/test_homework/test_homework.c
```

Тобто `src/main.cpp` зникає без жодного повідомлення; з реальним записом
користувач отримує «успішний» проєкт, який не збереться.

**Fix:** передати обробник, що перетворює будь-яку помилку обходу на exit 2:

```python
def _walk_error(exc):
    raise CheckError(f"cannot read template directory: {exc}") from exc

for current, dirnames, filenames in os.walk(
    template_dir, followlinks=False, onerror=_walk_error
):
```

Плюс регресійний тест із `os.chmod(dir, 0o000)` (з відновленням у `finally`).

### WR-10: Лексична перевірка `_homework_directory` тихо вимикає id-інваріант, коли root канонічний, а шлях — ні (регресія 04-08)

**File:** `scripts/metadata/contract.py:582-599` (особливо `592-595`)

**Issue:** Після 04-08 функція порівнює **лексичні** префікси `os.path.abspath(root)` і
`os.path.abspath(path)`. `resolve_root()` (`contract.py:462-479`) завжди повертає
**канонічний** root, а `check_metadata.py:159-165` приймає абсолютний positional
**без** нормалізації. Якщо root і шлях відрізняються лише symlink-аліасом префікса
(на macOS це стандартні `TMPDIR`: `/var/...` → `/private/var/...`, `/tmp` →
`/private/tmp`), префікс не збігається, функція повертає `None`, і перевірка
`id == homeworks/<dir>` **тихо не виконується**. Стара реалізація резолвила обидва
шляхи й цей випадок обробляла правильно — це регресія, а не успадкована поведінка.

**Failure scenario (відтворено):**

```text
root  = /private/tmp/x            (результат resolve_root)
path  = /tmp/x/homeworks/1_3-good/homework.yaml
old implementation -> '1_3-good'
new implementation -> None        # інваріант не спрацьовує
```

Практичний виклик: `uv run scripts/check_metadata.py --dir "$(pwd -P)" \
"$TMPDIR/root/homeworks/1_3-good"` — документ із `id: "9_9-other"` проходить з
exit 0, хоча та сама тека, передана без symlink-аліаса, дає exit 1. Тест
`IdentityTests.test_id_mismatch_survives_a_symlinked_homeworks_base`
(`test_homework_metadata.py:664-678`) цього не ловить, бо `run_fixture` передає лише
`--dir`, а шляхи будуються вже від резолвнутого root.

**Fix:** нормалізувати **тільки root** (не кандидата) — це не повертає діру зі
symlinked `homeworks`, бо tail лишається лексичним:

```python
root_parts = Path(os.path.abspath(root)).parts
path_parts = Path(os.path.abspath(path)).parts
if path_parts[: len(root_parts)] != root_parts:
    real_parts = Path(os.path.realpath(root)).parts
    if path_parts[: len(real_parts)] != real_parts:
        return None
    root_parts = real_parts
```

і додати тест із `--dir <canonical>` + absolute positional через symlink-аліас.

### WR-11: `relative_path` резолвить шлях, тому під symlinked-предком запис втрачає репозиторійний шлях

**File:** `scripts/metadata/contract.py:482-492`; взаємодія з `contract.py:438-459` (`apply_allowlist`) і новим `contract.py:582-599`

**Issue:** 04-08 зробив id-перевірку лексичною, але `display`-шлях запису й далі
будується через `Path(path).resolve()`. Під symlinked `homeworks` (саме той сценарій,
який 04-08 тепер обробляє) `resolve()` виводить шлях за межі root, `relative_to`
кидає `ValueError`, і функція повертає `Path(path).name` — голий basename. Наслідки:

1. D-23 обіцяє `{"path", "status", "reason"}` з репозиторійним шляхом, а CI отримує
   `homework.yaml` / `task.md` без жодної локації. Два різні homework-каталоги під тим
   самим symlink-ом дають записи з **однаковим** `path`, які неможливо атрибутувати
   (`check_metadata.py` не дедуплікує записи між каталогами; усередині однієї пари
   `_dedupe` лише схлопує два однакові id-записи, які прийшли з
   `validate_homework_text` і `validate_candidate`).
2. Allowlist 04-07 ключується саме на цей шлях: entry `homeworks/1_3-good/task.md`
   не збігається з `task.md`, тому легітимне пригнічення **не спрацьовує**, а entry
   стає stale → дві помилки замість однієї.

**Failure scenario (відтворено):** `homeworks -> <outside>`, у
`<outside>/1_3-good/task.md` кириличний рядок:

```text
validate_task_text(...) -> {'path': 'task.md', ..., 'rule': 'cyrillic'}
```

Тобто `apply_allowlist([...], [{"path": "homeworks/1_3-good/task.md"}])` не
пригнічує нічого. Новий тест 04-08 перевіряє лише підрядок `containing directory` у
reason і тому цей дефект не фіксує.

**Fix:** виводити display так само лексично, як `_homework_directory` (префікс root +
tail), а basename лишати тільки для шляху, що справді поза root. Додати в
`test_id_mismatch_survives_a_symlinked_homeworks_base` перевірку
`homeworks/1_3-good/homework.yaml` у stdout і окремий тест на allowlist під
symlinked-предком.

### WR-12: Дві з трьох нових гілок відмови `_contained_target` не покриті жодним тестом; coverage-запис 04-08 посилається на тести, які їх не перевіряють

**File:** `scripts/new_homework:344-355` (`349-350` — non-directory, `351-355` — resolved-base equality); `scripts/tests/test_new_homework.py:317-340`

**Issue:** `grep` по обох тестових модулях дає лише один рядок
`homeworks is a symlink; refusing to follow it`. Жоден тест не створює
`homeworks` як звичайний файл і жоден не викликає гілку
`homeworks base resolves outside the repository root`. При цьому
`04-08-SUMMARY.md` (coverage D2) стверджує: «A non-directory or resolving-away
homeworks base is refused before the plan», посилаючись на `ConflictTests`
(target-directory, intermediate-symlink, regular-file, final-file) — жоден із цих
тестів такої умови не створює. Тобто заявлена перевірка не існує, і must_have-truth
04-08 №2 («the resolved `homeworks` base to equal `<root>/homeworks`») не
закріплена.

Додатково: для канонічного `root` (а `resolve_root` іншого не повертає) рівність
`base.resolve() == root / "homeworks"` може не виконатися лише якщо `homeworks` —
symlink (уже відхилено вище) або якщо сам `root` підмінено між `resolve_root()` і
`_contained_target()`. Тобто гілка — defense-in-depth проти підміни root, а не
перевірка, яку можна відтворити на статичному дереві; жоден тест її не виконує.

**Fix:** додати два тести — `homeworks` як звичайний файл (exit 2, stdout порожній,
файл не змінений) і підміну root через `unittest.mock.patch` на
`Path.resolve`/`os.lstat`, щоб гілка рівності хоч раз виконалася. Якщо гілку
свідомо лишають як defense-in-depth — це має бути сказано в docstring і в
04-08-SUMMARY, а не подано як перевірену coverage-одиницю.

### WR-13: `framework`/`board` — мертві елементи мапінгу; manifest `framework` ніколи не звіряється з відрендереним документом (раніше WR-03, STILL OPEN)

**File:** `scripts/new_homework:210-220` (`216` — `framework`, `217` — `board`), `scripts/new_homework:123-148` (`yaml.safe_load` на `137`)

**Issue:** Мапа підстановки містить `framework` і `board`, але жоден шаблон не
використовує `{{framework}}` чи `{{board}}`: у `templates/homework-arduino/homework.yaml:5-6`
і `templates/homework-espidf/homework.yaml:5-6` значення вписані літералами
(`board: esp32-s3-devkitc-1`, `framework: arduino|espidf`). Отже:

- `_template_manifest` **вимагає** `framework`, але його значення ні на що не
  впливає: копія espidf-шаблону з `template.yaml: framework: arduino` відрендерить
  `framework: espidf` і пройде валідацію без жодної помилки;
- `BOARD` (`scripts/new_homework:94`) дублює літерал у двох шаблонах і в
  `templates/board-profile/profile.yaml:1` без жодної звірки;
- `_template_manifest` читає `template.yaml` через `yaml.safe_load`, тому
  дубльований `framework:` мовчки бере останнє значення — усупереч T-04-20, заради
  якого існують `StrictSafeLoader`/`StrictBaseLoader`.

**Fix:** або зробити `{{framework}}`/`{{board}}` єдиним джерелом у шаблонах, або
прибрати ці ключі з мапи й зробити `framework` необов'язковим; додати явну
звірку `manifest["framework"]` з розпарсеним `framework` у відрендереному
`homework.yaml` (ERROR-запис) і читати manifest через `StrictSafeLoader`.

### WR-14: Golden-diff не бачить різниці в line-ending і фінальному newline (раніше WR-05, STILL OPEN)

**File:** `scripts/tests/test_new_homework.py:105-129` (`116` — byte-compare, `118-128` — diff через `splitlines()`)

**Issue:** Байти порівнюються лише для того, щоб вирішити, чи будувати diff, а
єдиний сигнал збою — `assertEqual([], differences)`. Diff будується з
`.decode().splitlines()`, тому різниця, що зникає після `splitlines()`, дає порожній
diff і тест проходить.

**Failure scenario (відтворено):**

```text
expected = b"line one\nline two\n"; actual = b"line one\r\nline two"
bytes equal: False | rendered diff: []
```

Тобто CRLF-регресія або втрачений фінальний newline у шаблоні чи golden-фікстурі
не спіймається, хоча D-20 вимагає байтової ідемпотентності.

**Fix:** додати байтовий fallback у список різниць:

```python
if actual[name] != expected[name] and not file_differences:
    differences.append(
        f"{name}: bytes differ (actual {len(actual[name])} B, "
        f"expected {len(expected[name])} B)"
    )
```

## Info

### IN-03: YAML merge-ключі відхиляються як «invalid YAML» — STILL OPEN

**File:** `scripts/metadata/contract.py:89-109`, `scripts/metadata/contract.py:125-142`

**Issue:** Цикл duplicate-перевірки виконується **до** `flatten_mapping`, тому
`<<: *base` у `homework.yaml` дає `ConstructorError: could not determine a
constructor for the tag 'tag:yaml.org,2002:merge'` (відтворено), і користувач бачить
`invalid YAML: ...`, хоча документ валідний. Fail-closed, тому не критично, але
діагностика оманлива.

**Fix:** у `StrictSafeLoader.construct_mapping` викликати `self.flatten_mapping(node)`
перед циклом (для `StrictBaseLoader` merge-семантики немає — лишити як є).

### IN-05: Файли скаффолда отримують mode 0600; SIGKILL лишає temp-файли — STILL OPEN

**File:** `scripts/new_homework:424-435`

**Issue:** `tempfile.mkstemp` створює файл із `0600`, `os.replace` зберігає цей режим
(відтворено: `0o600` для `README.md`). Обробка `BaseException` не спрацьовує на
`SIGKILL`, тому `.new_homework-*` лишається в каталозі.

**Fix:** `os.fchmod(descriptor, 0o666 & ~umask)` перед записом.

### IN-07: Недосяжний `except CheckError` у фазі запису — STILL OPEN

**File:** `scripts/new_homework:528-535` (`530-532`)

**Issue:** `_write_all`/`_write_atomic` кидають лише `OSError`; `CheckError` у цьому
блоці недосяжний (він виникає тільки під час планування). Мертва гілка приховує, що
фактичний контракт фази запису — лише `OSError`. (Якщо застосувати фікс WR-07 із
повторним `_component_conflict`, гілка стане живою — тоді її треба лишити.)

**Fix:** лишити тільки `except OSError` або зробити її живою разом із WR-07.

### IN-08: Каскадна помилка `task.md` при невалідному `homework.yaml` — STILL OPEN

**File:** `scripts/metadata/contract.py:347-352` (`document = {}`), `scripts/metadata/contract.py:373-385`, `scripts/metadata/contract.py:250-256`

**Issue:** `validate_candidate` повторно парсить `homework.yaml`; на `yaml.YAMLError`
підставляється `document = {}`, далі `status = None`, і `validate_task_text` додає
чотири записи `... the sentinel 'TODO' is allowed only while status is 'planned',
not None` (відтворено на реальному шаблоні: один справжній YAML-ERROR + чотири
оманливі на `task.md`).

**Fix:** не застосовувати D-39, коли `homework.yaml` не вдалося розпарсити (або
рендерити «статус невідомий» замість `not None`).

### IN-09: Дублікати allowlist-entry ніколи не стають stale — STILL OPEN

**File:** `scripts/metadata/contract.py:450-458` (`allowed_paths`, `used_paths`), `scripts/metadata/contract.py:421-435`

**Issue:** `used_paths` — множина шляхів, тому два entry з однаковим `path` обидва
вважаються використаними, навіть якщо другий нічого не пригнічує. Відтворено:
`apply_allowlist([rec], [ENTRY, ENTRY_other_reason]) -> ([], [])`. Allowlist може
накопичувати дублікати (і суперечливі `reason`) без жодного сигналу, хоча інваріант
D-16 — «entry, що нічого не пригнітив, є stale».

**Fix:** у `load_allowlist` відхиляти повторний `path` як `CheckError`:

```python
seen_paths = set()
for entry in validated:
    if entry["path"] in seen_paths:
        raise CheckError(f"{where}: duplicate allowlist path {entry['path']!r}")
    seen_paths.add(entry["path"])
```

### IN-10: Літеральний BOM-символ у виклику `lstrip` — STILL OPEN

**File:** `scripts/metadata/contract.py:175`

**Issue:** U+FEFF вшитий у джерело невидимим літералом. Поведінка правильна
(`str.lstrip` з одним символом знімає лише провідні BOM), але літерал невидимий у
diff-ах, його легко видалити випадково, і саме він спричиняє спрацювання
invisible-unicode сканера на цьому файлі.

**Fix:** `text.lstrip("\N{ZERO WIDTH NO-BREAK SPACE}")`.

### IN-11: `HOMEWORK_ID.match` приймає id з trailing newline — exit 1 замість exit 2

**File:** `scripts/new_homework:506-510`, `scripts/metadata/contract.py:75`, `scripts/metadata/contract.py:502-506`

**Issue:** `re.match` з `$` у Python збігається і перед фінальним `\n`, тому
`$'1_3-x\n'` проходить CLI-guard (і `derive_parts`), хоча id невалідний. Далі
шаблон рендерить `id: "1_3-x` + newline + `"`, YAML складає це в `'1_3-x '`, і
запуск падає як id-mismatch на **exit 1** з розірваним на два рядки планом
(відтворено: `homeworks/1_3-x\n/README.md: CREATE — ...`), тобто з порушенням
«невалідний id → exit 2 до плану». ECMA-262 `$` у схемі такого id не приймає, тому
Python-guard і schema розходяться.

**Fix:** `HOMEWORK_ID.fullmatch(...)` у `main` і `derive_parts` (те саме для
`TEMPLATE_NAME`, `scripts/new_homework:81`).

### IN-12: `load_allowlist` не перевіряє форму шляху, яку вимагає AGENTS.md

**File:** `scripts/metadata/contract.py:426-434`

**Issue:** `AGENTS.md` («Metadata and provenance», `[MUST]`) вимагає, щоб запис
allowlist «names its exact repository-relative path». `load_allowlist` перевіряє
лише непорожній рядок: `path` може бути абсолютним (`/etc/passwd`), містити `..`
або бути голим basename (`task.md`). Звичайно такий entry просто стає stale, але у
сценарії WR-11 (display-шлях схлопується до `task.md`) basename-entry почне
пригнічувати записи зовсім іншого файлу.

**Fix:** вимагати `^homeworks/[A-Za-z0-9._-]+/(homework\.yaml|task\.md)$` (або
`PurePosixPath`-перевірку: не абсолютний, без `..`, ≥3 компонентів).

### IN-13: `toolchain.platformio` не звіряється з `PLATFORMIO_CORE` (раніше IN-02, STILL OPEN)

**File:** `scripts/metadata/contract.py:637-645`, `scripts/metadata/contract.py:77`

**Issue:** cross-check зі спільною конфігурацією виконується лише для
`toolchain.platform`. `toolchain.platformio` перевіряється тільки schema-патерном
`^\d+\.\d+\.\d+$`, тому `platformio: 9.9.9` у закоміченому `homework.yaml` проходить
checker, хоча `PLATFORMIO_CORE` (єдине джерело для скаффолда) — `6.2.0`.

**Fix:** додати симетричну перевірку
`if platformio != PLATFORMIO_CORE: errors.append(...)` (або окреме джерело truth у
`platformio.shared.ini`, як для `platform`).

---

## Prior findings re-checked

| Prior | Title | Status | Evidence |
|-------|-------|--------|----------|
| WR-06 | Symlink на `homeworks/` обходить контейнмент і вимикає перевірку `id` | **CLOSED** | `scripts/new_homework:337-355` (lstat + resolved-base equality) і `scripts/metadata/contract.py:582-599` (лексична деривація); тести `test_new_homework.py:317-340`, `test_homework_metadata.py:664-678`; відтворено: exit 2, stdout порожній, зовнішній каталог порожній |
| WR-07 | TOCTOU між планом і записом | **STILL OPEN** | `scripts/new_homework:424-435`, `438-447`; відтворено запис `outside/main.cpp` після підміни `src` на symlink (див. WR-07) |
| WR-08 | Тест «allowlisted path still rejects a shape violation» | **STILL OPEN** | `test_homework_metadata.py:441-457` — у фікстурі немає Cyrillic, entry стає stale, а не використаним (див. WR-08) |
| IN-03 | YAML merge-ключі | **STILL OPEN** | `contract.py:89-109`; відтворено `ConstructorError ... tag:yaml.org,2002:merge` |
| IN-05 | mode 0600 / temp-файли при SIGKILL | **STILL OPEN** | `new_homework:424-435`; відтворено `0o600` після `os.replace` |
| IN-07 | Недосяжний `except CheckError` | **STILL OPEN** | `new_homework:530-532`; єдине джерело `CheckError` — фаза планування |
| IN-08 | Каскадні помилки `task.md` | **STILL OPEN** | `contract.py:347-352`, `373-385`; відтворено 1 реальний + 4 записи `not None` |
| IN-09 | Дублікати allowlist-entry | **STILL OPEN** | `contract.py:450-458`; відтворено `apply_allowlist(..., [ENTRY, ENTRY]) -> ([], [])` |
| IN-10 | Літеральний BOM у `lstrip` | **STILL OPEN** | `contract.py:175`; invisible-unicode сканер спрацьовує на цьому файлі |

### Older rows from `04-REVIEW-DISPOSITION.md` re-verified in these files

| Disposition id | Status in this report | Evidence |
|----------------|-----------------------|----------|
| WR-03 (framework/board dead mapping) | **STILL OPEN**, тепер WR-13 | `new_homework:216-217`; жоден шаблон не містить `{{framework}}`/`{{board}}` |
| WR-05 (golden-diff line endings) | **STILL OPEN**, тепер WR-14 | `test_new_homework.py:116-128`; відтворено порожній diff при різних байтах |
| IN-02 (`toolchain.platformio` pin) | **STILL OPEN**, тепер IN-13 | `contract.py:637-645` перевіряє лише `platform` |

CR-02, WR-01 і WR-02 закрито попереднім звітом; CR-01 закрито ним для компонентів
під `homeworks/<id>`, а його залишок (base) закритий цією хвилею через WR-06. WR-04,
IN-01, IN-04 і IN-06 у цьому проході не переоцінювалися: WR-04/IN-06 стосуються
`scripts/tests/temp_root.py`, який не входить у scope, а IN-01/IN-04 — ділянок
`contract.py`/`new_homework`, яких ця хвиля не торкалася.

---

_Reviewed: 2026-10-24T22:15:30Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_

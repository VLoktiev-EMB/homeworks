---
phase: 09-agent-workflow-and-skills
reviewed: 2026-10-27T12:17:14Z
depth: standard
files_reviewed: 6
files_reviewed_list:
  - scripts/serial_capture.py
  - scripts/tests/test_serial_capture.py
  - .claude/skills/hw-flash/SKILL.md
  - .claude/skills/_shared/guardrails.md
  - .claude/skills/hw-flash/CHANGELOG.md
  - .claude/skills/hw-flash/LESSONS.md
findings:
  critical: 1
  warning: 3
  info: 5
  total: 9
status: issues_found
---

# Phase 09: Code Review Report (G-09-1: 09-15, 09-16)

**Reviewed:** 2026-10-27T12:17:14Z
**Depth:** standard
**Files Reviewed:** 6
**Status:** issues_found

## Summary

Перевірено дельту закриття G-09-1: явне розв'язання одного USB-порту, відкриття порту в
idle-стані (`--dtr 0 --rts 0`), звітування `port`/`vid_pid`/`baud` у `--json` та людському
рядку `CAPTURED`, а також контракт `hw-flash` «один розв'язаний порт для upload і capture».
Структурних знахідок (fallow) не надано; усі знахідки нижче — наративні.

Що перевірено, а не прийнято на віру:

- `pio device monitor --help` (PlatformIO Core 6.2.0) справді має `--dtr INTEGER RANGE`,
  `--rts INTEGER RANGE` і `-p`; `pio project config --json-output` та
  `pio device list --json-output` повертають форми, які відтворюють фікстури тестів;
  реальний пристрій цього хоста збігається з `SERIAL_DEVICES` (`USB VID:PID=303A:1001`).
- `python3 -m unittest discover scripts/tests` — 439 тестів, `OK` (запущено поза sandbox:
  у sandbox `pty.openpty()` падає з `out of pty devices`, що є середовищною відмовою, а не
  дефектом коду).
- `uv run scripts/gen_skills.py --check` — усі записи `UNCHANGED`; `.agents/skills/**` і
  `generated.skills.manifest` не редаговані вручну.
- Апаратний UAT (`uv run scripts/serial_capture.py --id 1_3-police-flasher --seconds 20` з
  під'єднаною платою) у рев'ю не відтворюється: sandbox закриває `/dev/cu.*`, плати немає.
  Твердження G-09-1 про реальні байти лишається непідтвердженим саме тут.

Цей звіт замінює попередній `09-REVIEW.md` (дельта 09-14); той текст лишається в історії git
(коміт `4df4a9f`).

## Narrative Findings (AI reviewer)

### CR-01: Сканування не ловить складені ключові слова, розділені пробілом

**File:** `scripts/serial_capture.py:139-145`
**Issue:** `_KEYWORDS` дозволяє лише суцільний варіант (`secretKey`, `secret_key`,
`secret-key`) і не допускає пробілу між словами складеного ключа. Перевірено прямим
викликом: `find_credential(b"SECRET KEY: hunter2")` і
`find_credential(b"secret key = hunter2")` повертають `False`. Це суперечить першому реченню
політики shared guardrails («a token, secret, password, passwd, passphrase, pwd, or API-key
assignment») і принципу fail-closed: рядок `SECRET KEY: <value>` з прошивки потрапить у
`.skill-state/logs/<id>.log`, тобто в єдиний файл, який ця перевірка має захищати. Дефект
передує дельті 09-15/09-16 (regex востаннє змінювався в 09-14), але файл у межах рев'ю, і
клас знахідки той самий, що й попередній CR-02 (прості присвоєння пароля).
**Fix:**
```python
_KEYWORDS = rb"(?:authorization|auth|token|secret(?:[\s_-]?key)?|pass(?:word|wd|phrase)|pwd|api[ _-]?key)"
```
Додати `b"secret key = hunter2"` і `b"SECRET KEY: hunter2"` до `REVIEW_SHAPES` та зберегти
негативний тест `auth mode = WPA2` (він не має почати збігатися: `auth` без пробільного
конектора далі не проходить).

### WR-01: `-d` для монітора ігнорує розв'язаний корінь репозиторію

**File:** `scripts/serial_capture.py:525` (виклик — `scripts/serial_capture.py:598`)
**Issue:** `_build_command` жорстко будує `-d "homeworks/" + args.id`, тобто шлях відносно
поточного робочого каталогу процесу, тоді як `project_config` (`:261-272`) читає конфігурацію
з абсолютного `root`, а `write_log_atomically` пише лог під тим самим `root`
(`:590-599`). Якщо запустити з підкаталогу репозиторію або з `--dir <root>`, конфігурація й
лог беруться з `root`, а `pio device monitor` відкриває проєкт, якого за шляхом відносно cwd
немає. Відтворено: при `cwd=/tmp` і `--dir <tmp-root>` отримано argv
`['pio','device','monitor','-d','homeworks/1_3-police-flasher', ...]`, хоча `root` передано
абсолютним. E2E-тест це маскує, бо патчить `_build_command` цілком.
**Fix:**
```python
command = _build_command(args, port, str(root / "homeworks" / args.id))
# у _build_command: "-d", project_dir  (абсолютний шлях)
```
Оновити `BuildCommandTests`, який зараз пінить `-d homeworks/<id>`.

### WR-02: Збій `pio project config` звітується як «port discovery failed» і має код 1 замість 2

**File:** `scripts/serial_capture.py:172-196`, `scripts/serial_capture.py:261-272`,
`scripts/serial_capture.py:594-595`, докстрінг `scripts/serial_capture.py:86-89`
**Issue:** `_run_json` зашиває префікс `port discovery failed` для кожного запиту, а
`project_config` використовує його без зміни підпису. Тому відсутній homework-каталог, збій
`pio`, таймаут або невалідний JSON конфігурації дають
`capture unavailable: port discovery failed: ...` з кодом 1, хоча жодного пошуку порту не
відбувалося. Це суперечить докстрінгу, який відносить «unresolvable `monitor_speed`» до
exit 2 (usage/environment), і збиває з пантелику при неправильному `--dir`.
**Fix:** параметризувати підпис (`_run_json(argv, failure: str)`) і для конфігураційного
запиту або підняти `CheckError` (exit 2), або явно задокументувати exit 1. Додати тест на
збій `project_config`.

### WR-03: Правило «один порт для upload і capture» продубльовано в guardrails і в скілі

**File:** `.claude/skills/_shared/guardrails.md:17-21`, `.claude/skills/hw-flash/SKILL.md:47-55`
**Issue:** Нормативне правило тепер сформульовано двічі: у shared guardrails і в
`hw-flash` («The selected path is passed to both the upload and the capture; neither command
resolves a port independently.»). План 09-16 (task H) прямо вимагав не переказувати правило
в скілі, а посилатися на shared-файл; репозиторій уже мав урок 09-09 про єдиного власника
політики. Два тексти неминуче розійдуться при наступній правці.
**Fix:** лишити в скілі лише операційні кроки (`pio device list`, фільтр `hwid`, вибір
єдиного кандидата, питання `--port`), а нормативне речення замінити посиланням на правило
shared guardrails.

### IN-01: Порада «pass --port» не працює, коли кандидатів нуль

**File:** `scripts/serial_capture.py:243-246`
**Issue:** Повідомлення `no USB serial device found; connect a board or pass --port`
пропонує `--port`, але `resolve_port` з явним `--port` усе одно вимагає, щоб шлях був у
списку `pio device list` (`:235-242`). За нуля кандидатів `--port` не допоможе — користувач
іде в глухий кут.
**Fix:** прибрати `or pass --port` з повідомлення про нуль кандидатів (лишити його лише для
ambiguous-випадку).

### IN-02: `--json` не дає JSON на exit 2

**File:** `scripts/serial_capture.py:564`, `scripts/serial_capture.py:619-621`
**Issue:** Help `--json` обіцяє «emit one JSON object», але будь-який `CheckError` (невалідний
id/порт/baud/тривалість) друкує текст у stderr і повертає 2 без JSON. Машинний споживач, який
передає `--json`, отримує порожній stdout.
**Fix:** або в `--json`-режимі друкувати JSON-об'єкт зі `status: REFUSED`/`USAGE`, або
уточнити help («one JSON object on success or capture refusal»). Існуючі `CliUsageTests`
не передають `--json`, тому їх це не ламає.

### IN-03: `HOMEWORK_ID`/`ENVIRONMENT` приймають хвіст `\n`

**File:** `scripts/serial_capture.py:572`, `scripts/serial_capture.py:577`
(регулярка — `scripts/metadata/paths.py:23`, `scripts/serial_capture.py:147`)
**Issue:** у Python `$` збігається і перед фінальним `\n`, тому
`HOMEWORK_ID.match("1_3-abc\n")` і `ENVIRONMENT.match("esp32\n")` істинні. Id із хвостовим
переводом рядка проходить валідацію (`write_log_atomically` перевіряє тим самим regex),
створює ім'я логу з `\n` і ламає `-d`-шлях. Це спадковий дефект (регулярка — канонічний
літерал, спільний зі схемою), але саме `main` покладається на нього.
**Fix:** використати `HOMEWORK_ID.fullmatch(...)` / `ENVIRONMENT.fullmatch(...)` (або `\Z`
у `scripts/metadata/paths.py`), щоб Python-перевірка не розходилася зі схемою.

### IN-04: Скіл не вимагає, щоб названий користувачем `--port` був серед знайдених кандидатів

**File:** `.claude/skills/hw-flash/SKILL.md:47-55`, `.claude/skills/hw-flash/SKILL.md:130`
**Issue:** Скіл валідує `--port` лише як абсолютний шлях під `/dev` без `..`, але не вимагає
належності до списку `pio device list`; хелпер цю належність перевіряє
(`scripts/serial_capture.py:235-242`). Тому друкарська помилка в шляху буде оголошена на
consent gate як «executed port», а потім відмовлена як `capture unavailable`. Додатково
фраза «neither command resolves a port independently» (рядок 55) суперечить опису нижче
(рядки 141-142), що хелпер самостійно розв'язує порт, коли `--port` не передано.
**Fix:** дописати, що названий `--port` має бути одним із оголошених USB-кандидатів, і
уточнити, що незалежне розв'язання хелпера — це fail-closed backstop для прямих викликів.

### IN-05: Явний `--baud` обходить перевірку вибору environment

**File:** `scripts/serial_capture.py:319-320`, `scripts/serial_capture.py:594-597`,
докстрінг `scripts/serial_capture.py:33-37`
**Issue:** Докстрінг обіцяє, що «an environment that cannot be chosen ... is a usage error»,
але `resolve_baud` повертає явний baud до читання конфігурації, а `main` узагалі не викликає
`resolve_baud`, коли `--baud` заданий. Прямий виклик з `--baud` без `--env` на проєкті без
`default_envs` (або з кількома) не перевіряє environment і дозволяє монітору вибрати його
неявно.
**Fix:** або перевіряти environment і на явному шляху (читаючи лише `default_envs`), або
уточнити докстрінг, що перевірка environment виконується лише без `--baud`.

---

_Reviewed: 2026-10-27T12:17:14Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_

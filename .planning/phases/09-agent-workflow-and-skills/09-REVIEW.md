---
phase: 09-agent-workflow-and-skills
reviewed: 2026-10-27T12:50:00Z
depth: standard
files_reviewed: 11
files_reviewed_list:
  - .agents/skills/_shared/guardrails.md
  - .agents/skills/hw-flash/CHANGELOG.md
  - .agents/skills/hw-flash/LESSONS.md
  - .agents/skills/hw-flash/SKILL.md
  - .claude/skills/_shared/guardrails.md
  - .claude/skills/hw-flash/CHANGELOG.md
  - .claude/skills/hw-flash/LESSONS.md
  - .claude/skills/hw-flash/SKILL.md
  - generated.skills.manifest
  - scripts/serial_capture.py
  - scripts/tests/test_serial_capture.py
findings:
  critical: 0
  warning: 2
  info: 3
  total: 5
status: issues_found
---

# Phase 09: Code Review Report (gap-closure 09-17, 09-18)

**Reviewed:** 2026-10-27T12:50:00Z
**Depth:** standard
**Files Reviewed:** 11
**Status:** issues_found

## Summary

Інкрементальне рев'ю дельти закриття `09-17`/`09-18` відносно `04e78ba2` (5 змінених
файлів, +59/−22, плюс перегенероване дзеркало `.agents/skills/**` і
`generated.skills.manifest`). Структурних знахідок (fallow) не надано; усі знахідки
нижче — наративні.

Що перевірено виконанням, а не прийнято на віру:

- `python3 -m unittest scripts.tests.test_serial_capture` — 53 тести `ok`, 11 падають
  виключно на `pty.openpty()` → `out of pty devices`. Це середовищна відмова sandbox
  (`/dev/ptmx` є, алокація заборонена), а не дефект коду: усі 11 задіюють `capture_pty`.
  `CredentialScanTests` — 12/12 `ok`; `_valid_port_path`, `resolve_port`,
  `resolve_baud`, `write_log_atomically`, `_build_command` і `main`-контракт перевірені
  поза PTY і проходять.
- `python3 scripts/gen_skills.py --check` → `EXIT:0`, усі записи `UNCHANGED`. Дзеркало
  `.agents/skills/**` і маніфест не редаговані вручну: будь-яка правка скіла йде в
  `.claude/skills/**` з наступною регенерацією.
- Прямі виклики `find_credential` на матриці форм політики (нижче) і на негативах.

### Re-check закритих знахідок

**CR-01 — ЗАКРИТО.** `_KEYWORDS` тепер `secret(?:[ _-]?key)?`. Перевірено прямим
викликом: `SECRET KEY: hunter2`, `secret key = hunter2`, `secret key: hunter2`,
`SECRET KEY = hunter2`, `Secret Key: hunter2`, `secret-key: hunter2`,
`secret_key = hunter2`, `secretkey: hunter2` → `True`. Усі закріплені негативи
лишилися `False`: `auth mode = WPA2`, `the cpwd tool reports ready`,
`author wrote nothing here`, `secret is`, ESP32 ROM boot log. Форми політики з
`optional separator`/`optional quoting`/`authorization`/`copula`/`embedded keyword`/
`passphrase`/`pwd`/`api key`/`api-key` також `True`. Guardrails називає складену форму,
є end-to-end тест відмови без запису лога і без `.skill-state`.

**WR-03 — ЧАСТКОВО ЗАКРИТО.** Назване речення («The selected path is passed to both the
upload and the capture; neither command resolves a port independently.») справді
видалене, і одна locator-фраза додана. Але нормативна половина правила про неоднозначний
набір портів усе ще переказана в скілі у двох місцях, попри твердження «it is not
restated here» — див. WR-13.

`WR-01` і `WR-02` лишаються відкритими за планом і тут не переоголошуються.

## Narrative Findings (AI reviewer)

### WR-13: Скіл усе ще переказує нормативне правило про неоднозначний порт, стверджуючи протилежне

**Severity:** WARNING
**File:** `.claude/skills/hw-flash/SKILL.md:50-52`, `.claude/skills/hw-flash/SKILL.md:54-55`,
`.claude/skills/hw-flash/SKILL.md:188-189`, `.claude/skills/hw-flash/CHANGELOG.md:11-12`
**Issue:** Locator-речення каже «Port handling follows the shared flashing rule in
`../_shared/guardrails.md`; it is not restated here.», але безпосередньо перед ним
стоїть «Stop the skill on more than one candidate, announcing every path and asking the
user for `--port`, because two interfaces can belong to one board.» — це той самий
нормативний припис, що й у guardrails: «the candidate set is ambiguous: stop and ask for
`--port` instead of capturing from one of them». Друга копія є нижче: «Both cables
attached produce two candidates, which is the ambiguous candidate set from before the
gate: stop and ask for `--port`.» Отже твердження «not restated here» хибне в межах
власного абзацу, і ризик дрейфу, який фіксувала WR-03, лишається саме для
ambiguity-половини правила: при наступній правці guardrails два тексти розійдуться.
CHANGELOG (`:11-12`) тим часом звітує, що скіл «no longer restates the shared
same-resolved-port rule».
**Fix:** лишити в скілі операційні кроки (запустити `pio device list --json-output`,
відфільтрувати за `hwid`, записати шлях і `VID:PID`, перевірити форму шляху), а
нормативні речення «stop … and ask for `--port`» прибрати з обох місць — наказ already
живе в guardrails, які скіл велить прочитати до gate. Якщо план усе ж вважає «stop/ask»
операційним кроком, переформулювати locator без хибного заперечення, наприклад:
`Port handling follows the shared flashing rule in ../_shared/guardrails.md; the steps below only apply it.`
Скопіювати правку в дзеркало регенерацією (`uv run scripts/gen_skills.py`), не руками.

### WR-14: Докстрінг модуля не описує складену форму ключового слова, яку скан тепер приймає

**Severity:** WARNING
**File:** `scripts/serial_capture.py:45-57` (контракт), `scripts/serial_capture.py:127-143`
(єдине місце, де форма названа), `scripts/serial_capture.py:144-147`
**Issue:** Докстрінг модуля перелічує прийняті форми («It matches a token, secret,
password, passwd, passphrase, pwd, API-key or auth/authorization keyword…») і не згадує
складену форму. Єдине згадування `secret key`/`secret-key`/`secretkey` — у коментарі над
`_KEYWORDS` (`:131-136`). Докстрінг цього файлу є контрактом поведінки (він докладно
описує exit-коди, гілки й межі), тож читач, який звіряє регекс із докстрінгом, дійде
висновку, що `SECRET KEY:` покритий лише ключовим словом `secret` — і при наступному
звуженні відновить CR-01. Додатково скан приймає складену форму й без роздільника
(`secretkey:`, `apikey:`), чого не називає ні політика, ні докстрінг (для fail-closed
скану це безпечний бік, але контракт має це фіксувати). Це вже третя перелічувана копія
набору форм (guardrails, коментар, докстрінг), що суперечить уроку 09-09 про єдиного
власника політики.
**Fix:** або додати одне речення в докстрінг: «A compound keyword may be written with one
space, underscore or hyphen, or with no separator (`secret key`, `secret_key`,
`secret-key`, `secretkey`)», або (краще, за уроком 09-09) замінити перелік форм у
докстрінгу посиланням на `_shared/guardrails.md` і лишити докстрінгу опис гілок, а не
набору ключових слів.

### IN-11: Межа конектора 128 символів не закріплена тестом, а назва тесту застаріла

**Severity:** INFO
**File:** `scripts/tests/test_serial_capture.py:257-261`, `scripts/serial_capture.py:152`
**Issue:** `test_a_connector_longer_than_32_characters_matches` перевіряє лише 32, 33 і 42,
хоча фактична межа в регексі — `[\w.-]{0,128}`. Немає жодного тесту ні на 128 (має
збігатися), ні на 129 (не має). Перевірено: `b"secret" + b"k"*n + b" = hunter2"` дає
`True` для n = 126, 127, 128 і `False` для n = 129, 130, 200, тобто рядок
`secret<129 ідентифікаторів> = hunter2` усе ще буде записаний у лог. Це задокументована
межа («at most 128»), а не порушення політики, але незакріплена межа дозволить майбутній
правці тихо змінити її в будь-який бік; назва тесту при цьому відсилає до давно знятої
межі 32.
**Fix:** перейменувати на `test_the_connector_ceiling_is_128_characters` і закріпити обидва
боки: `assertTrue` для 128, `assertFalse` для 129, з коментарем, що 129+ — задокументована
межа, а не недогляд.

### IN-12: Коментарі в тестовому модулі описують старий склад вибірок

**Severity:** INFO
**File:** `scripts/tests/test_serial_capture.py:7-11`, `scripts/tests/test_serial_capture.py:70-71`
**Issue:** Коментар над `REVIEW_SHAPES` каже «The six exact samples from 09-REVIEW.md
CR-02, then the four ordinary password assignments the WR-12 finding proved the scan
missed», хоча кортеж тепер містить дванадцять елементів, включно з двома новими
складеними формами. Докстрінг модуля (`:7-11`) перелічує шість форм CR-02, чотири WR-12,
`IDENTIFIER_SUFFIXED_ASSIGNMENTS` і long-suffix випадок, але не згадує ні новий кортеж
`SPACE_SEPARATED_COMPOUND_ASSIGNMENTS`, ні новий end-to-end тест складеного credential.
**Fix:** оновити обидва тексти: назвати додаткові складені форми у коментарі
`REVIEW_SHAPES` і додати складену форму та її end-to-end тест у докстрінг модуля.

### IN-13: Складене ключове слово з табуляцією лишається поза сканом

**Severity:** INFO
**File:** `scripts/serial_capture.py:145`
**Issue:** Клас роздільника — `[ _-]?`, тобто рівно один пробіл, підкреслення, дефіс або
нічого. Перевірено: `b"secret\tkey: hunter2"` і `b"secret  key: hunter2"` → `False`.
Політика guardrails називає саме «one space, underscore or hyphen», тож це
задокументований компроміс, а не порушення; але скан описаний як fail-closed, і
вирівняний табуляцією рядок прошивки — правдоподібний вивід. Перехід через межу рядка
при цьому не виникає.
**Fix:** якщо табуляцію треба покривати, замінити на `[ \t_-]?` (усе ще не перетинає
`\n`), додати позитивний тест `SECRET\tKEY:` і негативний `secret\nkey:`; якщо ні —
зафіксувати залишок явно в докстрінгу, щоб він не читався як недогляд.

### Перенесені відкриті знахідки (не переоголошуються)

`WR-01`, `WR-02` — відкриті за планом. `IN-01`, `IN-02`, `IN-03`, `IN-04`, `IN-05`,
`WR-07`, `WR-08`, `IN-07`, `IN-08`, `IN-09`, `IN-10` — лишаються відкритими з
`09-REVIEW-DISPOSITION.md` і цією дельтою не зачіпалися. Побічно: суперечливе речення,
назване другою половиною `IN-04` («neither command resolves a port independently»),
цією правкою видалене; перша половина `IN-04` (скіл не вимагає, щоб названий `--port` був
серед знайдених кандидатів) лишається відкритою.

---

_Reviewed: 2026-10-27T12:50:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_

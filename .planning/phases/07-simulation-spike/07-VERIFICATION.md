---
phase: 07-simulation-spike
verified: 2026-10-26T16:10:17Z
status: human_needed
score: 25/25 must-haves verified
covered_files: [".planning/phases/04.2-tracer-homework-1-3/04.2-FRICTION-LOG.md", ".planning/phases/07-simulation-spike/07-01-PLAN.md", ".planning/phases/07-simulation-spike/07-01-SUMMARY.md", ".planning/phases/07-simulation-spike/07-02-PLAN.md", ".planning/phases/07-simulation-spike/07-02-SUMMARY.md", ".planning/phases/07-simulation-spike/07-03-PLAN.md", ".planning/phases/07-simulation-spike/07-03-SUMMARY.md", ".planning/phases/07-simulation-spike/07-04-PLAN.md", ".planning/phases/07-simulation-spike/07-04-SUMMARY.md", ".planning/phases/07-simulation-spike/07-SPIKE-EVIDENCE.md", "docs/decisions/0014-simulator-selection.md", "docs/decisions/README.md", "docs/homeworks/1_3-police-flasher.md", "generated.manifest", "homeworks/1_3-police-flasher/README.md", "homeworks/1_3-police-flasher/homework.yaml", "homeworks/1_3-police-flasher/platformio.ini", "homeworks/1_3-police-flasher/report.md", "mkdocs.yml", "pyproject.toml", "scripts/pio/merge_firmware.py", "scripts/tests/test_merge_firmware.py", "scripts/tests/test_simulation_paths.py"]
covered_digest: "v3:sha256:a7d03a1af0ac9e3261bdd29e2b3d308dc391bb7a6a4a904f9daa4c48aa5084c2"
behavior_unverified: 0
overrides_applied: 0
human_verification:
  - test: "Owner-run Wokwi сесія: підтвердити три вставлені stamped-захоплення проти рядків run 1-3"
    expected: "Кожен із трьох захоплень містить `EXIT 0`, рівно один рядок `I pattern ready`; wall clock 5.815 s / 8.559 s / 12.701 s і cold/warm 3.759 s / 6.753 s / 11.238 s відповідають таблиці; `**Outcome:** scenario passed` і `3/3` узгоджені з exit-кодами"
    why_human: "Сесія token-gated і quota-metered, її не можна перезапустити у верифікаторі; доказ — owner-supplied captures у 07-SPIKE-EVIDENCE.md, і лише людина може підтвердити їхнє походження та відповідність рядкам"
  - test: "Velxio board capture: перевірити `$HOME/velxio-boards.png` (587620 байт) і сторінку `http://localhost:3080`"
    expected: "Скріншот існує поза репозиторієм і показує каталог `BOARDS 47`, включно з ESP32-S3 DevKit, XIAO ESP32-S3, Arduino Nano ESP32, STM32 Blue Pill і STM32 Black Pill, як записано в §Velxio self-host attempt"
    why_human: "Скріншот зберігається поза репозиторієм і не читається автоматичною перевіркою; достовірність observed-рядка — судження рецензента"
  - test: "Заборона P1-1 — у homework не залишилося другої копії merge action"
    expected: "`homeworks/1_3-police-flasher/merge_firmware.py` відсутній на диску і `git ls-files --error-unmatch` його не знаходить; переміщення і `git rm` в одному зміненні"
    why_human: "judgment-tier prohibition; доказ однозначний, але політика вимагає явного людського рішення"
  - test: "Заборона P1-2 — жодного `scripts/simulate.py` або simulation wrapper"
    expected: "У дереві немає `scripts/simulate.py` і жодного wrapper-скрипта симуляції; проба живе лише в тест-модулі"
    why_human: "judgment-tier prohibition; політика вимагає явного підтвердження"
  - test: "Заборона P1-3 — жодного реального `WOKWI_CLI_TOKEN` у тесті, fixture, дочірньому env або записаній команді"
    expected: "Єдина присвоєна величина в tracked source — літерал `dummy` (README і test_simulation_paths.py); реальний токен відсутній"
    why_human: "judgment-tier prohibition; скан доводить лише літерал `dummy`, а не відсутність токена поза tracked-деревом"
  - test: "Заборона P1-4 — Wokwi-команда не перевіряється прозою або doc-sync тестом"
    expected: "Єдиний доказ — виконаний subprocess з exit status і output; жодного читання README чи порівняння підрядка документа"
    why_human: "judgment-tier prohibition; політика вимагає явного рішення"
  - test: "Заборона P2-1 — значення `WOKWI_CLI_TOKEN` не потрапило ні в файл, ні в аргумент, ні в transcript"
    expected: "Єдине дозволене речення — `token supplied by the repository owner; value not recorded`; `git grep WOKWI_CLI_TOKEN -- .github` порожній"
    why_human: "judgment-tier prohibition; повний transcript і shell history верифікатор не бачить"
  - test: "Заборона P2-2 — симульований цифровий стан або таймінг не подано як bench/hardware evidence"
    expected: "Лише `expect-pin` стан і serial-текст названо simulation evidence; report повторює, що simulation output не є hardware evidence"
    why_human: "judgment-tier prohibition; оцінка формулювань у звіті — людське судження"
  - test: "Заборона P2-3 — quota не виведено з wall-clock"
    expected: "Wall-clock секунди і simulated minutes — окремі колонки; 45 s = 3 × `--timeout 15000`, позначено `calculated (upper bound)`"
    why_human: "judgment-tier prohibition; політика вимагає явного підтвердження"
  - test: "Заборона P2-4 — у measurement run не додано `--quiet` або `--interactive`"
    expected: "Протокол містить явну заборону; захоплені команди цих опцій не мають"
    why_human: "judgment-tier prohibition; фактичний запуск owner-а верифікатор не відтворює"
  - test: "Заборона P2-5 — жодного виведеного simulated-minutes, serial-рядка, exit-коду чи VCD шляху"
    expected: "Кожна відсутня величина записана як `absent — <reason>` або `not measured — <reason>`; VCD run 1 і serial-логи run 2-3 позначені absent"
    why_human: "judgment-tier prohibition; оцінка того, чи не виведено число з сусіднього значення, — людська"
  - test: "Заборона P3-1 — mutable `:master` не є записаною ідентичністю образу"
    expected: "Ідентичність — `ghcr.io/davidmonterocrespo24/velxio@sha256:5d673722…`; `:master` названо лише pull-посиланням"
    why_human: "judgment-tier prohibition; політика вимагає явного рішення"
  - test: "Заборона P3-2 — vendor-documented board list не подано як спостереження"
    expected: "Рядок `Board coverage (vendor documentation)` має мітку `datasheet`; observed-рядок посилається на скріншот і URL"
    why_human: "judgment-tier prohibition; розрізнення observation/datasheet у прозі — людське судження"
  - test: "Заборона P3-3 — pilot не перенесено в Velxio sketch заради вимірювання"
    expected: "Pilot compile і serial — `not measured` з причиною про PlatformIO-формат; жодного портованого скетча"
    why_human: "judgment-tier prohibition; політика вимагає явного підтвердження"
  - test: "Заборона P3-4 — жодного Velxio source, image layer або AGPL-ассета в MIT-репозиторії"
    expected: "`git ls-files` не містить жодного fritzing/velxio артефакту; у дереві лише посилання на образ і AGPL-межа"
    why_human: "judgment-tier prohibition; файловий скан не доводить відсутність скопійованого фрагмента поза tracked-шляхами"
  - test: "Заборона P3-5 — Velxio-спроба не спожила Wokwi quota"
    expected: "§Velxio self-host attempt містить явне твердження, що Wokwi не контактувався і сесія не відкривалася"
    why_human: "judgment-tier prohibition; vendor dashboard верифікатор не бачить"
  - test: "Заборона P4-1 — `schema/homework.schema.json` не змінено"
    expected: "`$defs.simulation.properties.status.enum` = `[none, pending, verified]`, немає ключа `evidence`, `additionalProperties: false`; git-диф схеми порожній"
    why_human: "judgment-tier prohibition; політика вимагає явного рішення"
  - test: "Заборона P4-2 — жодного simulated значення не підвищено до `measured`"
    expected: "П'ятимісткова лексика звіту незмінна (`measured`, `calculated`, `simulated`, `datasheet`, `not measured`); L-08 лишається `simulated`"
    why_human: "judgment-tier prohibition; оцінка прози — людське судження"
  - test: "Заборона P4-3 — запис не стверджує, що Renode не підтримує STM32"
    expected: "Рядок Renode називає непідтверджену модель курсу, відсутність STM32 homework/board profile і відсутність інсталяції; фрази «Renode lacks STM32» немає"
    why_human: "judgment-tier prohibition; перевірка відсутності конкретної заборони — людська"
  - test: "Заборона P4-4 — жодної копії Fritzing part graphics у спільних активах"
    expected: "`docs/assets/` і `homeworks/*/assets/` не отримали нового Fritzing-артефакту; `diagram.json` лишається єдиним джерелом істини"
    why_human: "judgment-tier prohibition; файловий скан покриває лише tracked-шляхи"
  - test: "Заборона P4-5 — README не розширено і SVG-схему не додано"
    expected: "§Simulation отримав лише pointer на evidence/ADR; нового SVG-файлу немає"
    why_human: "judgment-tier prohibition; оцінка обсягу редагування — людська"
  - test: "Заборона P4-6 — статус не виставлено `verified` на failed/blocked; немає застарілого речення"
    expected: "`**Outcome:** scenario passed`, тому `simulation.status: verified`; 12 заборонених stale-фраз відсутні у report.md і README.md"
    why_human: "judgment-tier prohibition; політика вимагає явного рішення"
  - test: "Заборона P4-7 — vendor-documented або `not measured` Velxio-значення не подано в ADR як спостереження"
    expected: "У матриці ADR: `19 boards` — `datasheet`, 47 boards — observed, pilot compile/serial — `not measured`; рядки не злиті"
    why_human: "judgment-tier prohibition; оцінка прози ADR — людське судження"
---

# Phase 7: Simulation Spike Verification Report

**Phase Goal:** An evidence-based simulator decision recorded in ADR-0004, with measured costs and
fidelity limits. **Friction-log justification:** the Phase 4.2 log must contain at least one entry
for simulation or wiring; otherwise the spike is not run.
**Verified:** 2026-10-26T16:10:17Z
**Status:** human_needed
**Re-verification:** No — initial verification (попереднього `07-VERIFICATION.md` не існувало)

> **Маппінг ADR-0004 → ADR-0014 (D-09).** Roadmap і `REQUIREMENTS.md` зберігають історичне
> формулювання «ADR-0004». ADR-0004 — це superseded ліцензійна ухвала; фактичний запис рішення
> про симулятори — `docs/decisions/0014-simulator-selection.md`. Це не відсутній deliverable:
> ADR-0014 існує, має рядок в індексі `docs/decisions/README.md` і містить зміст мети фази.

## Goal Achievement

### Observable Truths

| #   | Truth | Status | Evidence |
| --- | ----- | ------ | -------- |
| 1 | Лог Phase 4.2 містить щонайменше один запис про simulation або wiring (friction-log gate) | ✓ VERIFIED | `.planning/phases/04.2-tracer-homework-1-3/04.2-FRICTION-LOG.md` §F-08 «Execute the scenario: the Wokwi CLI is token-gated» (рядки 113-121) і §F-09 про merge/wiring; також F-19 про path-resolution |
| 2 | `pio run -d homeworks/1_3-police-flasher` після `-t clean` перелінковує застосунок і через `scripts/pio/merge_firmware.py` створює `firmware.merged.bin`; локальна копія відсутня і не tracked | ✓ VERIFIED | Живий запуск: `-t clean` exit 0, потім build `SUCCESS (9.11 s)` з рядком `Merging firmware images into …/firmware.merged.bin`; файл 383488 байт (`0x5da00`). `ls` — файлу немає; `git ls-files --error-unmatch` — «did not match» |
| 3 | Merge-команда — чиста функція, argv/offset/quoting/`-o`/fallback/обидві package-помилки/Windows-назва закріплені тестами без SCons | ✓ VERIFIED | `python3 -m unittest scripts.tests.test_merge_firmware -v` — 13 тестів OK; 9 named cases `MergeCommandTests` + 2 `MergeActionTests`; модуль імпортується без SCons (`env = None`) |
| 4 | `esptool_directory` кидає `SystemExit`, коли пакета немає і коли `get_package_dir` повертає `None` | ✓ VERIFIED | `test_missing_package_raises_system_exit`, `test_unpacked_package_raises_system_exit` зелені; код перевіряє обидві умови і називає `tool-esptool` та espressif32 8.x |
| 5 | Документована Wokwi-команда розв'язує `--scenario scenario.yaml` і `--diagram-file assets/diagram.json` відносно positional project dir і падає лише на connection stage | ✓ VERIFIED | `test_documented_command_reaches_the_connection_stage` — exit 1, `Error connecting to ws://127.0.0.1:1`, без `not found` |
| 6 | Спелування опцій від кореня репозиторію відхиляється, і відмова називає подвоєний шлях | ✓ VERIFIED | `test_repository_root_values_fail_at_the_path_stage` (`diagram.json not found`) і `test_negative_names_the_doubled_path` (`homeworks/1_3-police-flasher/homeworks/1_3-police-flasher/assets/diagram.json`) |
| 7 | `07-SPIKE-EVIDENCE.md` існує: лексика до даних, єдине token-речення, обидва protocol-блоки, `## Handoff to ADR-0014` з `**Outcome:**` | ✓ VERIFIED | Файл 33 KB; `## How to read this record` з п'ятьма мітками і `calculated (upper bound)`; `token supplied by the repository owner; value not recorded`; `## Owner-run protocol (Wokwi)`, `## Velxio protocol`; handoff має `**Outcome:** scenario passed` |
| 8 | Free ladder фіксує версію і short SHA `wokwi-cli`, lint exit 0, build-cold/warm медіани з трьох повторів, D-07 revalidation — кожне значення з міткою | ✓ VERIFIED | `0.28.1 (7cf4ffaebfd8)`; lint exit 0 `Found 1 info`; cold 10.98/7.63/8.13 → median 8.13 s; warm 0.50/0.49/0.48 → median 0.49 s; D-07 exit 1 `Error connecting to ws://127.0.0.1:1` без `Invalid scenario step key` |
| 9 | Run 1 має повний рядок: wall clock, simulator cold, exit code зі значенням, serial-line, simulated minutes, VCD path | ✓ VERIFIED | 5.815 s; 3.759 s; `0 — scenario completed; every step passed`; `yes — exactly one I pattern ready`; `calculated (upper bound) 15 s`; `absent — Error exporting VCD: Error 6: No logic analyzer in diagram` |
| 10 | Runs 2 і 3 мають warm-інтервали та точний serial count | ✓ VERIFIED | warm 6.753 s і 11.238 s; кожен stamped output містить рівно один `I pattern ready`; handoff — `3/3 runs observed the expected serial line` |
| 11 | Handoff outcome рівно одне з трьох значень; `scenario passed` вимагає exit 0 І `pattern ready`, тому саме виконання не є успіхом | ✓ VERIFIED | `**Outcome:** scenario passed`; усі три run rows exit 0; кожен stamped output містить `I pattern ready` і `Expected text matched: "pattern ready"`; serial reliability — точний дріб `3/3`, не відсоток |
| 12 | Значення токена відсутнє в репозиторії/evidence/команді/transcript; єдине token-речення — дозволене; єдине присвоєння — літерал `dummy` | ✓ VERIFIED | `git grep` по tracked source дає одне присвоєння: `homeworks/1_3-police-flasher/README.md:40: WOKWI_CLI_TOKEN=dummy`; `git grep WOKWI_CLI_TOKEN -- .github` порожній; в evidence лише дозволене речення |
| 13 | Коли run не дав serial log, VCD або dashboard delta, клітинка містить `absent — <first error line>` / `not measured — <reason>`, без виведених чисел | ✓ VERIFIED | VCD run 1 — `absent — Error exporting VCD: Error 6…`; serial-логи run 2-3 — `absent — the invocation used the literal placeholder <N>…`; dashboard — `not supplied by the owner`; simulated minutes — `calculated (upper bound)` |
| 14 | Velxio фіксує digest з `RepoDigests`, ніколи mutable tag; коли pull не стався — `not measured` з точною помилкою | ✓ VERIFIED | `ghcr.io/davidmonterocrespo24/velxio@sha256:5d673722f66cf2c5c8cef1fe4a04421a7d88fd863a7a266f8661ff269b3b3bc5`; `:master` названо лише pull-посиланням |
| 15 | Boot readiness = інтервал від старту `docker run` до першого HTTP 200; wall time і first-poll окремо; poll обмежений | ✓ VERIFIED | `docker run` 0.335 s (`measured`) і first HTTP 200 — attempt 9 of 60, 16.988 s (`measured`); boot readiness 16.988 s; 120 s ceiling позначено `calculated (upper bound)` |
| 16 | Board coverage має named capture, або точну причину; vendor-рядок відокремлений і позначений `datasheet` | ✓ VERIFIED | Observed: `$HOME/velxio-boards.png` (587620 байт) + URL `http://localhost:3080`, `BOARDS 47`, ESP32-S3 і STM32 присутні; vendor: `19 boards` з міткою `datasheet`; окремий рядок 182 FQBN |
| 17 | Velxio pilot compile і serial — чесно `not measured`; booted-but-unusable UI є валідним результатом | ✓ VERIFIED | `not measured — the self-hosted editor does not consume a PlatformIO project`; serial — `not measured — no UI run of the pilot was performed in this session`; контейнер завантажився і був знятий, тож unusable-UI гілка не активувалася |
| 18 | Жодного Velxio коду/шару/part graphic не вендорено; AGPL-межа записана | ✓ VERIFIED | §Licence boundary: AGPLv3, reference only; `git ls-files | grep -i 'fritzing|velxio'` — порожньо; `git status --porcelain` — чисто |
| 19 | ADR-0014 фіксує measured cold/warm start, build cold/warm, session duration, serial reliability у формі, яку підтримує evidence, і fidelity limits для Wokwi/Velxio/Renode/Fritzing | ✓ VERIFIED | ADR §Measured cost: build cold 8.13 s, build warm 0.49 s, simulator cold 3.759 s, warm 6.753/11.238 s, wall clock 5.815-12.701 s, serial `3/3`, simulated minutes `calculated (upper bound)` 15 s; §Fidelity limits — vendor limits + п'ять pilot-обмежень; Velxio pilot compile/serial — `not measured` |
| 20 | ADR має platform-role matrix і CI cost basis `calculated` з формулою, changed-project count, 1 run, PR cadence і чутливістю 5/50 | ✓ VERIFIED | Матриця Wokwi/Velxio/Renode/Fritzing з роллю, платформами і глибиною; формула `session_minutes_per_run × changed_projects_per_PR × runs_per_PR × PRs_per_month`; `PRs_per_month = 20`; 5 PR → 1.25 min, 50 PR → 12.5 min; усе `calculated` |
| 21 | `docs/decisions/README.md` отримує рівно один рядок у порядку дат з посиланням на ADR-0014; MkDocs nav містить ADR; docs-pins тест зелений | ✓ VERIFIED | Один рядок `2026-10-26 … [0014](0014-simulator-selection.md)`; `mkdocs.yml:41` — nav entry; `test_nav_lists_every_markdown_file_under_docs` — ok |
| 22 | `simulation.status` стає `verified` лише за `**Outcome:** scenario passed`; інакше лишається `pending` з blocker | ✓ VERIFIED | `homeworks/1_3-police-flasher/homework.yaml:17` — `status: verified`; handoff — `scenario passed`; generated page — `wokwi (verified)`; T-15 — `verified` |
| 23 | Усі застарілі simulation-твердження в `report.md` і homework README узгоджені | ✓ VERIFIED | Жодна з 10 заборонених фраз не знайдена; §7, L-08, T-15, §9 industry note, §9 conclusions/status, Decision Appendix 7 і README §Simulation містять pointer на evidence і ADR-0014 |
| 24 | Report вказує на спільний `../../scripts/pio/merge_firmware.py`; жодного live tracked-посилання на видалений проєктний шлях | ✓ VERIFIED | `report.md` — `merge_firmware.py` count n=1, `scripts/pio/merge_firmware.py` count m=1; `git grep` з `:!.planning` — 0 матчів; залишкові згадки є лише в історичних `.planning/` планах/сумарях, які не переписуються за політикою |
| 25 | П'ятимісткова лексика незмінна; жодне `simulated` не стало `measured`; схема незмінна; Fritzing-артефакту і part graphics немає; `diagram.json` канонічний і валідований lint | ✓ VERIFIED | Ledger definition незмінний; L-08 `simulated`; `$defs.simulation.properties.status.enum = [none, pending, verified]`, без `evidence`, `additionalProperties: false`; Fritzing/velxio файлів немає; `wokwi-cli lint --offline …/assets/diagram.json` exit 0 `Found 1 info` |

**Score:** 25/25 truths verified (0 present, behavior-unverified)

### Deferred Items

Немає. Усі п'ять roadmap success criteria закриваються цією фазою в межах role-proportional
глибини (D-05). Рядок Renode/STM32 і Velxio pilot compile лишаються свідомо `not measured` з
причинами, а не відкладеними gap-ами; справжній CI simulation run — Phase 8.

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | -------- | ------ | ------- |
| `scripts/pio/merge_firmware.py` | Shared post action: `build_merge_command`, `esptool_directory`, `esptool_binary`, `_quote`, `merge_firmware`, guarded SCons import | ✓ VERIFIED | 118 рядків; імпортується без SCons; жива збірка створила merged image; `_quote` docstring чесно обмежує претензію atomicity |
| `scripts/tests/test_merge_firmware.py` | `MergeCommandTests` — 9 named cases + CR-01 action tests | ✓ VERIFIED | 13 тестів OK; додано `test_failed_merge_raises` / `test_successful_merge_does_not_raise` для CR-01 |
| `scripts/tests/test_simulation_paths.py` | Positive, negative, non-vacuity probes | ✓ VERIFIED | 3 тести OK; child env рівно з чотирьох імен, `dummy` лише |
| `homeworks/1_3-police-flasher/platformio.ini` | `post:../../scripts/pio/merge_firmware.py` поруч із незміненим `pre:` compiledb | ✓ VERIFIED | Рядки 20-22; `-t compiledb` exit 0, `compile_commands.json` 222.4K |
| `homeworks/1_3-police-flasher/merge_firmware.py` | Видалений через `git rm` | ✓ VERIFIED | Відсутній на диску; не tracked |
| `pyproject.toml` | Лише `"scripts/pio/*.py" = ["F821"]`, коментар про одне місце | ✓ VERIFIED | Рядки 18-21 |
| `.planning/phases/07-simulation-spike/07-SPIKE-EVIDENCE.md` | Vocabulary, protocol blocks, free ladder, run table, quota ledger, handoff | ✓ VERIFIED | 33 KB, 655 рядків, усі секції присутні |
| `docs/decisions/0014-simulator-selection.md` | MADR: frontmatter, 8 секцій, role matrix, measured costs, fidelity limits, calculated CI basis, SIM-03/AGPL | ✓ VERIFIED | 259 рядків; `Chosen option:`; 8 MADR-секцій; `07-SPIKE-EVIDENCE.md` як code span |
| `docs/decisions/README.md` | Рівно один рядок з `[0014](0014-simulator-selection.md)` | ✓ VERIFIED | Один рядок, останній у таблиці, дата 2026-10-26 |
| `homeworks/1_3-police-flasher/homework.yaml` | `simulation.status` відповідає handoff outcome | ✓ VERIFIED | `tool: wokwi`, `diagram: assets/diagram.json`, `status: verified`; інші ключі не змінені |
| `homeworks/1_3-police-flasher/report.md` | Узгоджені §7, L-08, T-15, §9, Decision Appendix 7; спільний merge path | ✓ VERIFIED | Для 10 заборонених фраз — 0 матчів; T-15 status `verified`; evidence/ADR pointers на рядках 288-289, 350, 427-433, 482-483 |
| `homeworks/1_3-police-flasher/README.md` | §Simulation pointer замість deferral-речень | ✓ VERIFIED | Рядки 47-48 — pointer на evidence і ADR; command block і dummy-token параграф збережені |
| `docs/homeworks/1_3-police-flasher.md` | Generated Simulation cell | ✓ VERIFIED | `| Simulation | wokwi (verified) |`; `gen_views.py --all --check` — усі UNCHANGED |
| `mkdocs.yml` | Nav entry для ADR-0014 | ✓ VERIFIED | Рядок 41 після regeneration |
| `generated.manifest` | Оновлені digests/bytes | ✓ VERIFIED | `--all --check` — `manifest bytes are identical` |

### Key Link Verification

| From | To | Via | Status | Details |
| ---- | -- | --- | ------ | ------- |
| `homeworks/1_3-police-flasher/platformio.ini` | `scripts/pio/merge_firmware.py` | `post:` relative extra_scripts (бо `extends` замінює блок) | WIRED | Жива збірка завантажила post action і надрукувала merge-рядок |
| `scripts/tests/test_simulation_paths.py` | `homeworks/1_3-police-flasher/README.md` | Тест виконує те саме спелування опцій, а не матчить прозу | WIRED | Positive probe exit 1 на connection stage; README §Simulation документує ті самі значення |
| `07-SPIKE-EVIDENCE.md` | `homeworks/1_3-police-flasher/.pio/build/esp32s3_arduino/firmware.merged.bin` | `wokwi.toml` називає merged image, який продукує post action | WIRED | `wokwi.toml: firmware = ".pio/build/esp32s3_arduino/firmware.merged.bin"`; файл існує після чистої збірки |
| `07-SPIKE-EVIDENCE.md` | `docs/decisions/0014-simulator-selection.md` | ADR несе висновок і посилається на evidence як code span | WIRED | ADR §More Information і Confirmation називають `.planning/phases/07-simulation-spike/07-SPIKE-EVIDENCE.md`; жодного relative `.planning` Markdown-лінка |
| `07-SPIKE-EVIDENCE.md` (`**Outcome:**`) | `homeworks/1_3-police-flasher/homework.yaml` | `scenario passed` — єдина умова для `verified` | WIRED | Outcome `scenario passed`; YAML `status: verified`; Branch B не активовано |
| `homeworks/1_3-police-flasher/homework.yaml` | `docs/homeworks/1_3-police-flasher.md` | `simulation.status` — вхід генератора | WIRED | Generated page `wokwi (verified)`; `gen_views.py --all --check` зелений |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
| -------- | ------------- | ------ | ------------------ | ------ |
| `docs/homeworks/1_3-police-flasher.md` | Simulation cell | `homeworks/1_3-police-flasher/homework.yaml` `simulation.tool/status` через `scripts/gen_views.py` | Так — `wokwi (verified)` у committed page, `--check` підтверджує, що це не ручна правка | ✓ FLOWING |
| `docs/decisions/0014-simulator-selection.md` | Platform-role matrix і measured costs | `07-SPIKE-EVIDENCE.md` run table / ladder / Velxio section | Так — значення ADR збігаються з evidence (3.759 / 6.753 / 11.238 / 3/3 / 16.988 / 47 / 182) | ✓ FLOWING |
| `scripts/pio/merge_firmware.py` | `firmware.merged.bin` | `env.subst("$BUILD_DIR")`, `env.BoardConfig()`, `FLASH_EXTRA_IMAGES`, `ESP32_APP_OFFSET` | Так — жива збірка записала 383488 байт і надрукувала шлях | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| Чиста збірка створює merged image через shared post action | `pio run -d homeworks/1_3-police-flasher -t clean && pio run -d homeworks/1_3-police-flasher` | `Merging firmware images into …`; `SUCCESS (9.11 s)`; файл 383488 байт | ✓ PASS |
| Повторний `pre:` compiledb працює | `pio run -d homeworks/1_3-police-flasher -t compiledb` | `SUCCESS`; `compile_commands.json` 222.4K | ✓ PASS |
| Merge/simulation unit suite | `python3 -m unittest scripts.tests.test_merge_firmware scripts.tests.test_simulation_paths -v` | `Ran 14 tests … OK` | ✓ PASS |
| Повний stdlib suite | `python3 -m unittest discover -s scripts/tests -t .` | `Ran 380 tests … OK` | ✓ PASS |
| Generated views узгоджені | `uv run scripts/gen_views.py --all --check` | усі записи `UNCHANGED`; exit 0 | ✓ PASS |
| Metadata contract | `uv run scripts/check_metadata.py` | `PASS: metadata contract satisfied` | ✓ PASS |
| Docs-pins nav test | `python3 -m unittest scripts.tests.test_docs_pins.PinConsistencyTests.test_nav_lists_every_markdown_file_under_docs -v` | `Ran 1 test … OK` | ✓ PASS |
| Canonical diagram lint | `wokwi-cli lint --offline homeworks/1_3-police-flasher/assets/diagram.json` | exit 0; `Found 1 info` (`unsupported-part`) | ✓ PASS |
| CR-01 регресія | `test_failed_merge_raises` / `test_successful_merge_does_not_raise` у suite | ok/ok; код кидає `RuntimeError` на non-zero `env.Execute` | ✓ PASS |

### Probe Execution

Не застосовано: у фазі немає probe-скриптів (`find scripts -path '*/tests/probe-*.sh'` порожній),
а вимірювання Wokwi є owner-run сесією, а не probe. Доказ виконання — stamped captures у
`07-SPIKE-EVIDENCE.md`.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| ----------- | ---------- | ----------- | ------ | -------- |
| SIM-02 | 07-01, 07-02, 07-03, 07-04 | Повний spike: Wokwi (primary), Velxio (self-host fallback), Renode (STM32), Fritzing (illustration) на pilot-і; cold start, compile, serial reliability, measured minutes, fidelity limits; результат в ADR-0004 (фактично ADR-0014 за D-09) | ✓ SATISFIED | Evidence + ADR-0014 role matrix; Wokwi 3/3 executed; Velxio digest/boot/47-board catalogue; Renode/Fritzing `not measured` з причинами; CI cost basis `calculated`. Owner-run captures → human verification |
| SIM-03 | 07-04 | Fritzing SVG лише з attribution; part graphics не копіюються в shared assets/docs; `diagram.json` — джерело істини | ✓ SATISFIED | ADR §Licence boundary; жодного Fritzing/velxio файлу в `git ls-files`; `diagram.json` канонічний і проходить lint |

**Orphaned requirements:** немає. `REQUIREMENTS.md` мапить Phase 7 лише на SIM-02 і SIM-03, і
обидва заявлені у frontmatter планів (SIM-03 — у `07-04-PLAN.md`).

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| — | — | `TBD` / `FIXME` / `XXX` у файлах фази | — | Не знайдено жодного debt marker; debt-marker gate чистий |
| — | — | `scripts/simulate.py` або simulation wrapper | — | Не існує (D-14 дотримано) |
| — | — | Fritzing/velxio артефакти в tracked tree | — | Не знайдено |
| `docs/decisions/0014-simulator-selection.md` | 51-53 | «Velxio booted reproducibly» при одному виміряному boot | ℹ️ Info | WR-03 у `07-REVIEW-DISPOSITION.md`, лишається open; не порушує must-have, бо числове значення в матриці — один `measured` boot 16.988 s |
| `docs/decisions/0014-simulator-selection.md` | 169-170 | «three runs consumed 45 s» тоді як evidence позначає 45 s як upper bound | ℹ️ Info | WR-04, open; таблиця вище позначає `calculated (upper bound)`, тож must-have про «форму, яку підтримує evidence» не порушено |
| `docs/decisions/0014-simulator-selection.md` | 61 | Velxio Platforms не перелічує STM32, хоч evidence-клітинка того ж рядка називає STM32-плати | ℹ️ Info | WR-02, open; Renode-рядок не стверджує ексклюзивності, і observed STM32 presence записано в evidence-клітинці |
| `docs/decisions/0014-simulator-selection.md` | 180-181 | Confirmation приписує `test_merge_firmware` створення merged image | ℹ️ Info | WR-05, open; тест доводить argv/помилковий шлях, а merged image доведено живою збіркою в цій верифікації |
| `docs/decisions/0014-simulator-selection.md` | 158-159 | «referenced by its immutable digest» без наведення digest | ℹ️ Info | IN-06, open; digest є в evidence; жоден must-have не вимагає digest саме в ADR |

**Рішення щодо 12 відкритих review-знахідок:** жодна не порушує must-have. CR-01 (`fixed`,
`4f053b2`) перевірено: `merge_firmware()` кидає `RuntimeError` на non-zero `env.Execute`, і два
нові тести це закріплюють. Решта — формулювальні надмірності та info-зауваження; вони
залишаються `open` за рішенням ревʼю і не блокують мету фази.

### Human Verification Required

#### 1. Owner-run Wokwi сесія (три захоплення)

**Test:** Звірити три stamped-захоплення з таблицею run 1-3 у `07-SPIKE-EVIDENCE.md`.
**Expected:** Кожен містить `EXIT 0` і рівно один `I pattern ready`; wall clock 5.815 / 8.559 / 12.701 s; cold 3.759 s, warm 6.753 / 11.238 s; `**Outcome:** scenario passed` узгоджений із `3/3`.
**Why human:** Сесія token-gated і quota-metered; верифікатор не може її перезапустити, а доказ — owner-supplied captures.

#### 2. Velxio board capture

**Test:** Відкрити `$HOME/velxio-boards.png` (587620 байт) і сторінку `http://localhost:3080`.
**Expected:** Каталог `BOARDS 47`, включно з ESP32-S3 DevKit, XIAO ESP32-S3, Arduino Nano ESP32, STM32 Blue Pill і STM32 Black Pill.
**Why human:** Скріншот зберігається поза репозиторієм і не читається автоматично.

#### 3-23. Judgment-tier prohibitions (21 пункт)

Кожна заборона з `must_haves.prohibitions` усіх чотирьох планів має `verification: judgment` і
`status: unresolved`; політика вимагає явного людського рішення на кожну. Автоматичні докази
наведено в `human_verification` frontmatter; жодна не виглядає порушеною. Пункти:

1. P1-1 — друга копія merge action не залишилася.
2. P1-2 — немає `scripts/simulate.py` або wrapper.
3. P1-3 — жодного реального `WOKWI_CLI_TOKEN` у тесті/fixture/env/команді.
4. P1-4 — Wokwi-команда не перевіряється прозою чи doc-sync тестом.
5. P2-1 — значення токена не записано нікуди.
6. P2-2 — симульований стан/таймінг не подано як hardware evidence.
7. P2-3 — quota не виведено з wall-clock.
8. P2-4 — без `--quiet` / `--interactive` у measurement run.
9. P2-5 — жодного виведеного числа/рядка/VCD.
10. P3-1 — `:master` не є ідентичністю образу.
11. P3-2 — vendor board list не подано як observation.
12. P3-3 — pilot не портовано в Velxio sketch.
13. P3-4 — Velxio/AGPL-артефакти не вендорено.
14. P3-5 — Velxio не спожив Wokwi quota.
15. P4-1 — схема metadata не змінена.
16. P4-2 — `simulated` не підвищено до `measured`.
17. P4-3 — немає твердження «Renode не підтримує STM32».
18. P4-4 — Fritzing part graphics не скопійовано.
19. P4-5 — README не розширено, SVG не додано.
20. P4-6 — статус не `verified` на failed/blocked; немає stale-речення.
21. P4-7 — vendor/`not measured` Velxio-значення не подано як observation в ADR.

### Gaps Summary

Gap-ів немає: 25/25 must-have truths VERIFIED, 0 blocker-антипатернів, 0 debt markers,
0 behavior-unverified truths. Мета фази досягнута в коді й артефактах: ADR-0014 (маппінг
roadmap-ового ADR-0004 за D-09) існує, індексований, містить measured costs, fidelity limits,
platform-role matrix і calculated CI basis; evidence-файл містить вимірювання з мітками та
`scenario passed` 3/3; `simulation.status: verified` відповідає handoff; усі generated views
узгоджені; friction-log gate виконано (F-08/F-09).

Статус `human_needed` — не через gap, а через 21 judgment-tier prohibition і два owner-supplied
докази (Wokwi-сесія, Velxio-скріншот), які політика вимагає закрити явним людським рішенням.

---

_Verified: 2026-10-26T16:10:17Z_
_Verifier: Claude (gsd-verifier)_

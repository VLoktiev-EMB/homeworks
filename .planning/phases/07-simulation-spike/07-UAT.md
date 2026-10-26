---
status: complete
phase: 07-simulation-spike
source: [07-VERIFICATION.md]
started: 2026-10-26T16:11:34.627111Z
updated: 2026-10-26T16:31:57.575Z
---

## Current Test

[testing complete]

## Tests

### 1. Owner-run Wokwi сесія: підтвердити три вставлені stamped-захоплення проти рядків run 1-3
expected: Кожен із трьох захоплень містить `EXIT 0`, рівно один рядок `I pattern ready`; wall clock 5.815 s / 8.559 s / 12.701 s і cold/warm 3.759 s / 6.753 s / 11.238 s відповідають таблиці; `**Outcome:** scenario passed` і `3/3` узгоджені з exit-кодами
result: pass

### 2. Velxio board capture: перевірити `$HOME/velxio-boards.png` (587620 байт) і сторінку `http://localhost:3080`
expected: Скріншот існує поза репозиторієм і показує каталог `BOARDS 47`, включно з ESP32-S3 DevKit, XIAO ESP32-S3, Arduino Nano ESP32, STM32 Blue Pill і STM32 Black Pill, як записано в §Velxio self-host attempt
result: pass

### 3. Заборона P1-1 — у homework не залишилося другої копії merge action
expected: `homeworks/1_3-police-flasher/merge_firmware.py` відсутній на диску і `git ls-files --error-unmatch` його не знаходить; переміщення і `git rm` в одному зміненні
result: pass

### 4. Заборона P1-2 — жодного `scripts/simulate.py` або simulation wrapper
expected: У дереві немає `scripts/simulate.py` і жодного wrapper-скрипта симуляції; проба живе лише в тест-модулі
result: pass

### 5. Заборона P1-3 — жодного реального `WOKWI_CLI_TOKEN` у тесті, fixture, дочірньому env або записаній команді
expected: Єдина присвоєна величина в tracked source — літерал `dummy` (README і test_simulation_paths.py); реальний токен відсутній
result: pass

### 6. Заборона P1-4 — Wokwi-команда не перевіряється прозою або doc-sync тестом
expected: Єдиний доказ — виконаний subprocess з exit status і output; жодного читання README чи порівняння підрядка документа
result: pass

### 7. Заборона P2-1 — значення `WOKWI_CLI_TOKEN` не потрапило ні в файл, ні в аргумент, ні в transcript
expected: Єдине дозволене речення — `token supplied by the repository owner; value not recorded`; `git grep WOKWI_CLI_TOKEN -- .github` порожній
result: pass

### 8. Заборона P2-2 — симульований цифровий стан або таймінг не подано як bench/hardware evidence
expected: Лише `expect-pin` стан і serial-текст названо simulation evidence; report повторює, що simulation output не є hardware evidence
result: pass

### 9. Заборона P2-3 — quota не виведено з wall-clock
expected: Wall-clock секунди і simulated minutes — окремі колонки; 45 s = 3 × `--timeout 15000`, позначено `calculated (upper bound)`
result: pass

### 10. Заборона P2-4 — у measurement run не додано `--quiet` або `--interactive`
expected: Протокол містить явну заборону; захоплені команди цих опцій не мають
result: pass

### 11. Заборона P2-5 — жодного виведеного simulated-minutes, serial-рядка, exit-коду чи VCD шляху
expected: Кожна відсутня величина записана як `absent — <reason>` або `not measured — <reason>`; VCD run 1 і serial-логи run 2-3 позначені absent
result: pass

### 12. Заборона P3-1 — mutable `:master` не є записаною ідентичністю образу
expected: Ідентичність — `ghcr.io/davidmonterocrespo24/velxio@sha256:5d673722…`; `:master` названо лише pull-посиланням
result: pass

### 13. Заборона P3-2 — vendor-documented board list не подано як спостереження
expected: Рядок `Board coverage (vendor documentation)` має мітку `datasheet`; observed-рядок посилається на скріншот і URL
result: pass

### 14. Заборона P3-3 — pilot не перенесено в Velxio sketch заради вимірювання
expected: Pilot compile і serial — `not measured` з причиною про PlatformIO-формат; жодного портованого скетча
result: pass

### 15. Заборона P3-4 — жодного Velxio source, image layer або AGPL-ассета в MIT-репозиторії
expected: `git ls-files` не містить жодного fritzing/velxio артефакту; у дереві лише посилання на образ і AGPL-межа
result: pass

### 16. Заборона P3-5 — Velxio-спроба не спожила Wokwi quota
expected: §Velxio self-host attempt містить явне твердження, що Wokwi не контактувався і сесія не відкривалася
result: pass

### 17. Заборона P4-1 — `schema/homework.schema.json` не змінено
expected: `$defs.simulation.properties.status.enum` = `[none, pending, verified]`, немає ключа `evidence`, `additionalProperties: false`; git-диф схеми порожній
result: pass

### 18. Заборона P4-2 — жодного simulated значення не підвищено до `measured`
expected: П'ятимісткова лексика звіту незмінна (`measured`, `calculated`, `simulated`, `datasheet`, `not measured`); L-08 лишається `simulated`
result: pass

### 19. Заборона P4-3 — запис не стверджує, що Renode не підтримує STM32
expected: Рядок Renode називає непідтверджену модель курсу, відсутність STM32 homework/board profile і відсутність інсталяції; фрази «Renode lacks STM32» немає
result: pass

### 20. Заборона P4-4 — жодної копії Fritzing part graphics у спільних активах
expected: `docs/assets/` і `homeworks/*/assets/` не отримали нового Fritzing-артефакту; `diagram.json` лишається єдиним джерелом істини
result: pass

### 21. Заборона P4-5 — README не розширено і SVG-схему не додано
expected: §Simulation отримав лише pointer на evidence/ADR; нового SVG-файлу немає
result: pass

### 22. Заборона P4-6 — статус не виставлено `verified` на failed/blocked; немає застарілого речення
expected: `**Outcome:** scenario passed`, тому `simulation.status: verified`; 12 заборонених stale-фраз відсутні у report.md і README.md
result: pass

### 23. Заборона P4-7 — vendor-documented або `not measured` Velxio-значення не подано в ADR як спостереження
expected: У матриці ADR: `19 boards` — `datasheet`, 47 boards — observed, pilot compile/serial — `not measured`; рядки не злиті
result: pass

## Summary

total: 23
passed: 23
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps

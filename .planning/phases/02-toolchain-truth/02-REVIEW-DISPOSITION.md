---
phase: 02
review: 02-REVIEW.md
titles: json
findings:
  - id: CR-01
    severity: critical
    disposition: open
    title: "Спільна конфігурація посилається на `default_16MB.csv`, єдиний примірник якого буде видалено у Phase 3"
  - id: WR-01
    severity: warning
    disposition: open
    title: "Тести жорстко прив'язані до тимчасового smoke-проєкту і зламаються після Phase 3"
  - id: WR-02
    severity: warning
    disposition: open
    title: "ADR-0007 «Confirmation» заявляє чотири інваріанти, яких тести не перевіряють"
  - id: WR-03
    severity: warning
    disposition: open
    title: "Версія бібліотеки оголошена двічі — у `library.json` і в кожному `.c`"
  - id: WR-04
    severity: warning
    disposition: open
    title: "Загальні шаблонні патерни `.gitignore` можуть тихо ховати авторські файли"
  - id: IN-01
    severity: info
    disposition: open
    title: "`board_upload.maximum_size` перезаписується platform builder'ом, тому пін нічого не обмежує"
  - id: IN-02
    severity: info
    disposition: open
    title: "`.gitignore` містить дублікати та порожні заголовки секцій"
  - id: IN-03
    severity: info
    disposition: open
    title: "README проєкту не містить команд відтворення доказів"
  - id: IN-04
    severity: info
    disposition: open
    title: "`default_envs = native` не дає звичайному `pio run` перевірити ESP-середовища"
  - id: IN-05
    severity: info
    disposition: open
    title: "Назва `native_unity` обіцяє Unity-набір, якого ще немає, і `pio test -e native` не працює"
  - id: IN-06
    severity: info
    disposition: open
    title: "ESP-IDF-середовище не успадковує `-Wall -Wextra`"
  - id: IN-07
    severity: info
    disposition: open
    title: "Механізм PSRAM для Arduino не задокументований; `sdkconfig.defaults` діє лише на ESP-IDF"
open: 12
total: 12
recorded: 2026-10-23T20:06:07.574Z
---

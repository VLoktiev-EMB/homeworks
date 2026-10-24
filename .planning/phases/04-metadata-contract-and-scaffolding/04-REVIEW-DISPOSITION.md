---
phase: 04
review: 04-REVIEW.md
titles: json
findings:
  - id: CR-01
    severity: critical
    disposition: open
    title: "Symlink у дереві цілі дозволяє запис за межі `homeworks/` (і звітує хибний шлях)"
  - id: CR-02
    severity: critical
    disposition: open
    title: "YAML-ключ складеного типу валить перевірник `TypeError`-ом; `--json` не друкує масиву"
  - id: WR-01
    severity: warning
    disposition: open
    title: "Allowlist пригнічує один запис на один entry, а не весь шлях"
  - id: WR-02
    severity: warning
    disposition: open
    title: "Наявний звичайний файл на місці проміжного каталогу класифікується як CREATE"
  - id: WR-03
    severity: warning
    disposition: open
    title: "`framework`/`board` — мертві елементи мапінгу; board id дублюється без перевірки"
  - id: WR-04
    severity: warning
    disposition: open
    title: "Regex лінтера плейсхолдерів не збігається з regex рендерера"
  - id: WR-05
    severity: warning
    disposition: open
    title: "Golden-diff не бачить зміни line-ending та фінального newline"
  - id: IN-01
    severity: info
    disposition: open
    title: "Вироджені `id` дають порожній display-title"
  - id: IN-02
    severity: info
    disposition: open
    title: "`toolchain.platformio` не звіряється з `PLATFORMIO_CORE`"
  - id: IN-03
    severity: info
    disposition: open
    title: "YAML merge-ключі відхиляються як «invalid YAML»"
  - id: IN-04
    severity: info
    disposition: open
    title: "Не-рядкове значення provenance повідомляється як «value is empty»"
  - id: IN-05
    severity: info
    disposition: open
    title: "Файли скаффолда отримують mode 0600; SIGKILL лишає temp-файли"
  - id: IN-06
    severity: info
    disposition: open
    title: "`temp_root.render_tree` — мертвий код"
  - id: IN-07
    severity: info
    disposition: open
    title: "Недосяжний `except CheckError` у фазі запису"
  - id: IN-08
    severity: info
    disposition: open
    title: "Каскадна помилка `task.md` при невалідному `homework.yaml`"
open: 15
total: 15
recorded: 2026-10-24T21:22:31.904Z
---

# Phase 04: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| CR-01 | critical | open | - |
| CR-02 | critical | open | - |
| WR-01 | warning | open | - |
| WR-02 | warning | open | - |
| WR-03 | warning | open | - |
| WR-04 | warning | open | - |
| WR-05 | warning | open | - |
| IN-01 | info | open | - |
| IN-02 | info | open | - |
| IN-03 | info | open | - |
| IN-04 | info | open | - |
| IN-05 | info | open | - |
| IN-06 | info | open | - |
| IN-07 | info | open | - |
| IN-08 | info | open | - |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.

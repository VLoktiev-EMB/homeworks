---
phase: 04
review: 04-REVIEW.md
titles: json
findings:
  - id: WR-06
    severity: warning
    disposition: open
    title: "Symlink на самому `homeworks/` обходить контейнмент і тихо вимикає перевірку `id`"
  - id: WR-07
    severity: warning
    disposition: open
    title: "Між планом і записом шлях перевіряється лише один раз (TOCTOU)"
  - id: WR-08
    severity: warning
    disposition: open
    title: "Тест «allowlisted path still rejects a shape violation» не перевіряє пригнічення"
  - id: IN-03
    severity: info
    disposition: open
    title: "YAML merge-ключі відхиляються як «invalid YAML»"
  - id: IN-05
    severity: info
    disposition: open
    title: "Файли скаффолда отримують mode 0600; SIGKILL лишає temp-файли"
  - id: IN-07
    severity: info
    disposition: open
    title: "Недосяжний `except CheckError` у фазі запису"
  - id: IN-08
    severity: info
    disposition: open
    title: "Каскадна помилка `task.md` при невалідному `homework.yaml`"
  - id: IN-09
    severity: info
    disposition: open
    title: "Дублікати allowlist-entry ніколи не стають stale"
  - id: IN-10
    severity: info
    disposition: open
    title: "Літеральний BOM-символ у виклику `lstrip`"
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
  - id: IN-04
    severity: info
    disposition: open
    title: "Не-рядкове значення provenance повідомляється як «value is empty»"
  - id: IN-06
    severity: info
    disposition: open
    title: "`temp_root.render_tree` — мертвий код"
open: 20
total: 20
recorded: 2026-10-24T21:49:11.063Z
---

# Phase 04: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| WR-06 | warning | open | - |
| WR-07 | warning | open | - |
| WR-08 | warning | open | - |
| IN-03 | info | open | - |
| IN-05 | info | open | - |
| IN-07 | info | open | - |
| IN-08 | info | open | - |
| IN-09 | info | open | - |
| IN-10 | info | open | - |
| CR-01 | critical | open | - (not in the current review) |
| CR-02 | critical | open | - (not in the current review) |
| WR-01 | warning | open | - (not in the current review) |
| WR-02 | warning | open | - (not in the current review) |
| WR-03 | warning | open | - (not in the current review) |
| WR-04 | warning | open | - (not in the current review) |
| WR-05 | warning | open | - (not in the current review) |
| IN-01 | info | open | - (not in the current review) |
| IN-02 | info | open | - (not in the current review) |
| IN-04 | info | open | - (not in the current review) |
| IN-06 | info | open | - (not in the current review) |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.

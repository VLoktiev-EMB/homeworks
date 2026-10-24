---
phase: 04
review: 04-REVIEW.md
titles: json
findings:
  - id: WR-07
    severity: warning
    disposition: open
    title: "Між планом і записом шлях перевіряється лише один раз (TOCTOU)"
  - id: WR-08
    severity: warning
    disposition: fixed
    title: "Тест «allowlisted path still rejects a shape violation» не перевіряє пригнічення"
  - id: WR-09
    severity: warning
    disposition: open
    title: "`os.walk` тихо пропускає недоступний каталог шаблону — exit 0 з неповним проєктом"
  - id: WR-10
    severity: warning
    disposition: fixed
    title: "Лексична перевірка `_homework_directory` тихо вимикає id-інваріант, коли root канонічний, а шлях — ні (регресія 04-08)"
  - id: WR-11
    severity: warning
    disposition: open
    title: "`relative_path` резолвить шлях, тому під symlinked-предком запис втрачає репозиторійний шлях"
  - id: WR-12
    severity: warning
    disposition: open
    title: "Дві з трьох нових гілок відмови `_contained_target` не покриті тестами; coverage-запис 04-08 посилається на тести, які їх не перевіряють"
  - id: WR-13
    severity: warning
    disposition: open
    title: "`framework`/`board` — мертві елементи мапінгу; manifest `framework` ніколи не звіряється з відрендереним документом (раніше WR-03)"
  - id: WR-14
    severity: warning
    disposition: open
    title: "Golden-diff не бачить різниці в line-ending і фінальному newline (раніше WR-05)"
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
  - id: IN-11
    severity: info
    disposition: open
    title: "`HOMEWORK_ID.match` приймає id з trailing newline — exit 1 замість exit 2"
  - id: IN-12
    severity: info
    disposition: open
    title: "`load_allowlist` не перевіряє форму шляху, яку вимагає AGENTS.md"
  - id: IN-13
    severity: info
    disposition: open
    title: "`toolchain.platformio` не звіряється з `PLATFORMIO_CORE` (раніше IN-02)"
  - id: WR-06
    severity: warning
    disposition: fixed
    title: "Symlink на самому `homeworks/` обходить контейнмент і тихо вимикає перевірку `id`"
  - id: WR-15
    severity: warning
    disposition: open
    title: "Case-only написання компонента `homeworks` (`HomeWorks`) тихо вимикає id-інваріант на APFS"
  - id: WR-16
    severity: warning
    disposition: open
    title: "`None` зливає «не homework-документ» і «identity не перевірено» — позиційний шлях `homeworks/<sub>/<dir>` виходить з exit 0"
  - id: WR-17
    severity: warning
    disposition: open
    title: "Symlinked `homeworks/<dir>` довіряється лексично — звіряється ім'я лінка, а не реальний каталог"
  - id: IN-14
    severity: info
    disposition: open
    title: "`_homework_directory` залежить від CWD для відносних шляхів; docstring не згадує абсолютний шлях як передумову"
  - id: IN-15
    severity: info
    disposition: open
    title: "Налаштування alias-fixture продубльовано дослівно в усіх трьох нових `IdentityTests`"
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
  - id: WR-04
    severity: warning
    disposition: open
    title: "Regex лінтера плейсхолдерів не збігається з regex рендерера"
  - id: IN-01
    severity: info
    disposition: open
    title: "Вироджені `id` дають порожній display-title"
  - id: IN-04
    severity: info
    disposition: open
    title: "Не-рядкове значення provenance повідомляється як «value is empty»"
  - id: IN-06
    severity: info
    disposition: open
    title: "`temp_root.render_tree` — мертвий код"
open: 27
total: 30
recorded: 2026-10-24T22:50:00.000Z
---

# Phase 04: Code Review Disposition

Supersedes the 2026-10-24T22:20:00Z ledger. Re-recorded against the
2026-10-24T22:42:44Z incremental review (plan-04-09 delta vs `d6fa103`), which
re-verified only the two files that delta touched.

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| WR-07 | warning | open | - |
| WR-08 | warning | fixed | Closed by 04-09 Task 2 — `CyrillicGateTests.test_allowlisted_path_still_rejects_a_shape_violation` now carries a Cyrillic word and a shape violation in one file, so it exercises suppression rather than assuming it |
| WR-09 | warning | open | - |
| WR-10 | warning | fixed | Closed by 04-09 — `_homework_directory` reconciles only the ancestor prefix, so `/tmp` vs `/private/tmp` no longer skips the invariant. Re-verified by the 2026-10-24T22:42:44Z review |
| WR-11 | warning | open | - |
| WR-12 | warning | open | - |
| WR-13 | warning | open | - (renamed from WR-03) |
| WR-14 | warning | open | - (renamed from WR-05) |
| IN-03 | info | open | - |
| IN-05 | info | open | - |
| IN-07 | info | open | - |
| IN-08 | info | open | - |
| IN-09 | info | open | - |
| IN-10 | info | open | - |
| IN-11 | info | open | - |
| IN-12 | info | open | - |
| IN-13 | info | open | - (renamed from IN-02) |
| WR-06 | warning | fixed | Fixed by 04-08; re-verified in the 2026-10-24T22:42:44Z review — `lstat` of the base in `_contained_target` plus lexical `_homework_directory` |
| WR-15 | warning | open | New in the 2026-10-24T22:42:44Z review, published there as `WR-01`; re-IDed here because `WR-01` is already an open finding of the earlier review |
| WR-16 | warning | open | New in the 2026-10-24T22:42:44Z review, published there as `WR-02`; re-IDed for the same reason |
| WR-17 | warning | open | New in the 2026-10-24T22:42:44Z review, published there as `WR-03`; re-IDed for the same reason |
| IN-14 | info | open | New in the 2026-10-24T22:42:44Z review, published there as `IN-01`; re-IDed because `IN-01` is already an open finding |
| IN-15 | info | open | New in the 2026-10-24T22:42:44Z review, published there as `IN-02`; re-IDed for the same reason |
| CR-01 | critical | open | - (not in the current review) |
| CR-02 | critical | open | - (not in the current review) |
| WR-01 | warning | open | - (not in the current review) |
| WR-02 | warning | open | - (not in the current review) |
| WR-04 | warning | open | - (not in the current review) |
| IN-01 | info | open | - (not in the current review) |
| IN-04 | info | open | - (not in the current review) |
| IN-06 | info | open | - (not in the current review) |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently.

## Triage note

The review is advisory and does not block phase completion. Two things in this
ledger bear on the phase's claim:

- **WR-10 and WR-08 are now closed** — the two findings the previous triage note
  said must be fixed before re-verification. Both are pinned by tests that fail
  without the 04-09 change.
- **WR-15 is the same class of defect as the closed WR-10, one path component
  over.** The new `_homework_directory` docstring asserts the invariant "cannot
  be silently disabled"; that claim is false for a case-only spelling of the
  `homeworks` component (`HomeWorks`), which names the same directory on APFS.
  The default scan (pre-commit and CI) cannot reach it — it builds paths from
  the resolved root — so this is reachable only through a caller-supplied
  positional path, which is why it is a warning and not a blocker.

The open Critical rows CR-01 and CR-02 predate the 2026-10-24T22:15:30Z review that
re-verified the same files after 04-06/04-07/04-08, and are recorded here as
"not in the current review" rather than as live findings.

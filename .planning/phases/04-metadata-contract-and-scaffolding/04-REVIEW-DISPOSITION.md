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
    disposition: open
    title: "Тест «allowlisted path still rejects a shape violation» не перевіряє пригнічення"
  - id: WR-09
    severity: warning
    disposition: open
    title: "`os.walk` тихо пропускає недоступний каталог шаблону — exit 0 з неповним проєктом"
  - id: WR-10
    severity: warning
    disposition: open
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
open: 24
total: 25
recorded: 2026-10-24T22:20:00.000Z
---

# Phase 04: Code Review Disposition

Supersedes the 2026-10-24T21:49:11Z ledger, which was recorded against the
2026-10-24T21:47:49Z review (commit `d958855`). Re-recorded against the
2026-10-24T22:15:30Z review, which re-verified the same four files after the
04-06, 04-07 and 04-08 gap-closure plans.

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| WR-07 | warning | open | - |
| WR-08 | warning | open | - |
| WR-09 | warning | open | - |
| WR-10 | warning | open | - |
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
| WR-06 | warning | fixed | Fixed by 04-08; re-verified in 04-REVIEW.md — `lstat` of the base in `_contained_target` plus lexical `_homework_directory`, both pinned by `ConflictTests.test_homeworks_base_symlink_exits_2` and `IdentityTests.test_id_mismatch_survives_a_symlinked_homeworks_base` |
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

The review is advisory and does not block phase completion. Two of its findings
bear directly on what 04-08 claimed:

- **WR-10** is a regression introduced by 04-08 itself: the lexical prefix check
  in `_homework_directory` misses when the repository root is canonical
  (`resolve_root`) but the absolute positional argument is not (`/tmp` →
  `/private/tmp`, `/var` → `/private/var` on macOS), silently disabling the
  id-equals-directory invariant. This contradicts the plan's must_have.
- **WR-12** records that two of the three `_contained_target` refusal branches
  have no test, and that the 04-08 SUMMARY's coverage entry D2 cites tests that
  do not exercise them.

Both should be closed by a `--gaps` plan before the phase is re-verified.

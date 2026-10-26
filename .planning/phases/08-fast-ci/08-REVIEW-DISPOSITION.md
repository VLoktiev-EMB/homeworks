---
phase: 08
review: 08-REVIEW.md
titles: json
findings:
  - id: CR-01
    severity: critical
    disposition: fixed
    title: "Крок сценарію втрачає `quota.json` і мапінг виходу на будь-якому ненульовому коді `wokwi-cli`"
  - id: WR-01
    severity: warning
    disposition: open
    title: "`WOKWI_CLI_TOKEN` доступний кожному кроку job, включно з `pio run`, який виконує код з PR"
  - id: WR-02
    severity: warning
    disposition: open
    title: "Крок завантаження артефакту запускається з порожнім `ARTIFACT_NAME`, якщо попередній крок упав"
  - id: WR-03
    severity: warning
    disposition: open
    title: "Матриця `simulate` містить усі інструменти, крім `none`, а job завжди запускає `wokwi-cli`"
  - id: WR-04
    severity: warning
    disposition: open
    title: "Nightly-запуск може бути зеленим із порожньою матрицею, не доводячи нічого"
  - id: WR-05
    severity: warning
    disposition: open
    title: "`test_ci_grants_no_write_permission` обходиться формулюваннями `write-all` і `\"write\"`"
  - id: WR-06
    severity: warning
    disposition: open
    title: "`test_only_simulate_receives_a_secret` перевіряє лише текст до job `simulate`"
  - id: WR-07
    severity: warning
    disposition: open
    title: "Блоки встановлення `gitleaks` і `wokwi-cli` продубльовані, а копії не перевіряються на однаковість"
  - id: WR-08
    severity: warning
    disposition: open
    title: "Два «контрактні» тести перевіряють увесь файл, тому рядки `meta` задовольняють їх"
  - id: WR-09
    severity: warning
    disposition: open
    title: "`test_nightly_computes_the_full_matrix` проходить на коментарях і ключі кешу"
  - id: WR-10
    severity: warning
    disposition: open
    title: "Тест пінів перевіряє лише перші 8 символів SHA-256"
  - id: WR-11
    severity: warning
    disposition: open
    title: "Контракт `gate` не забороняє `continue-on-error`"
  - id: IN-01
    severity: info
    disposition: open
    title: "`step_block` не відповідає власному docstring і не знаходить крок без `name:`"
  - id: IN-02
    severity: info
    disposition: open
    title: "`test_every_workflow_declares_a_textual_trigger_key` жорстко фіксує кількість workflow"
  - id: IN-03
    severity: info
    disposition: open
    title: "Docstring модуля описує неповний склад `ci.yml`"
  - id: IN-04
    severity: info
    disposition: open
    title: "Магічне число 15 дублює `--timeout 15000`"
  - id: IN-05
    severity: info
    disposition: open
    title: "Тести LFS-охоронця покривають скрипт, який більше ніхто не викликає"
  - id: IN-06
    severity: info
    disposition: open
    title: "`AGENTS.md` називає команду quick-start «точною» командою CI, хоча CI додає прапорець"
  - id: IN-07
    severity: info
    disposition: open
    title: "Definition of Done у шаблоні PR не згадує Python-набір, який тепер блокує merge"
  - id: IN-08
    severity: info
    disposition: open
    title: "Збій `jq` у `changes` може тихо записати порожній вихід і пропустити збірку"
  - id: IN-09
    severity: info
    disposition: open
    title: "Job id `secrets` у nightly збігається з назвою контексту"
  - id: IN-10
    severity: info
    disposition: open
    title: "Зняття мітки `simulate` не перезапускає workflow"
  - id: IN-11
    severity: info
    disposition: open
    title: "Регулярний вираз заголовка приймає subject із самих пробілів"
open: 22
total: 23
recorded: 2026-10-26T19:20:00Z
---

# Phase 08: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| CR-01 | critical | fixed | commit 97c6099 — `set +e` around the pipeline, `set -e` after `PIPESTATUS`, `stat` fallback; asserted by `test_scenario_step_reads_pipestatus_under_errexit` |
| WR-01 | warning | open | - |
| WR-02 | warning | open | - |
| WR-03 | warning | open | - |
| WR-04 | warning | open | - |
| WR-05 | warning | open | - |
| WR-06 | warning | open | - |
| WR-07 | warning | open | - |
| WR-08 | warning | open | - |
| WR-09 | warning | open | - |
| WR-10 | warning | open | - |
| WR-11 | warning | open | - |
| IN-01 | info | open | - |
| IN-02 | info | open | - |
| IN-03 | info | open | - |
| IN-04 | info | open | - |
| IN-05 | info | open | - |
| IN-06 | info | open | - |
| IN-07 | info | open | - |
| IN-08 | info | open | - |
| IN-09 | info | open | - |
| IN-10 | info | open | - |
| IN-11 | info | open | - |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.

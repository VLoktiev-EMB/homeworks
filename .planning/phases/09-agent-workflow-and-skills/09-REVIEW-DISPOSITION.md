---
phase: 09
review: 09-REVIEW.md
titles: json
findings:
  - id: WR-01
    severity: warning
    disposition: open
    title: "The monitor's `-d` path ignores the resolved repository root"
  - id: WR-02
    severity: warning
    disposition: open
    title: "A failing `pio project config` is reported as port discovery and exits 1"
  - id: IN-12
    severity: info
    disposition: open
    title: "Test-module comments describe the old fixture composition"
  - id: IN-13
    severity: info
    disposition: open
    title: "Tab-separated and double-space compound keywords remain outside the scan"
  - id: IN-14
    severity: info
    disposition: open
    title: "The new docstring names a no-separator form the policy owner does not name and no test pins"
  - id: CR-01
    severity: critical
    disposition: fixed
    title: "Сканування не ловить складені ключові слова, розділені пробілом"
  - id: WR-03
    severity: warning
    disposition: fixed
    title: "Правило «один порт для upload і capture» продубльовано в guardrails і в скілі"
  - id: IN-01
    severity: info
    disposition: open
    title: "Порада «pass --port» не працює, коли кандидатів нуль"
  - id: IN-02
    severity: info
    disposition: open
    title: "`--json` не дає JSON на exit 2"
  - id: IN-03
    severity: info
    disposition: open
    title: "`HOMEWORK_ID`/`ENVIRONMENT` приймають хвіст ` `"
  - id: IN-04
    severity: info
    disposition: open
    title: "Скіл не вимагає, щоб названий користувачем `--port` був серед знайдених кандидатів"
  - id: IN-05
    severity: info
    disposition: open
    title: "Явний `--baud` обходить перевірку вибору environment"
  - id: CR-02
    severity: critical
    disposition: fixed
    title: "The credential-shape scan misses ordinary assignment forms, so the gated write can persist a credential"
  - id: CR-03
    severity: critical
    disposition: fixed
    title: "`hw-flash` never passes the user-resolved baud to the capture helper"
  - id: WR-04
    severity: warning
    disposition: fixed
    title: "The consent-gate example omits `-e <env>`, so it is not the exact command the rule requires"
  - id: WR-05
    severity: warning
    disposition: fixed
    title: "The general credential prohibition no longer covers logs outside the exception"
  - id: WR-06
    severity: warning
    disposition: fixed
    title: "The capture command omits `--quiet`, so PlatformIO's banner is captured into the log"
  - id: WR-07
    severity: warning
    disposition: open
    title: "`no-generated-files` does not cover the template-tree generated patterns"
  - id: WR-08
    severity: warning
    disposition: open
    title: "The uv cache override falls back to a fixed shared `/tmp` path"
  - id: WR-09
    severity: warning
    disposition: fixed
    title: "The no-build-impact paragraph in AGENTS.md omits the Phase 9 paths"
  - id: WR-10
    severity: warning
    disposition: fixed
    title: "`--seconds` accepts NaN and infinity, which crash the CLI with a traceback"
  - id: WR-11
    severity: warning
    disposition: fixed
    title: "An exception in the read loop leaves `pio device monitor` running"
  - id: WR-12
    severity: warning
    disposition: fixed
    title: "The credential scan still misses ordinary password assignments"
  - id: IN-06
    severity: info
    disposition: fixed
    title: "The suite does not exercise the helper's argv or the CLI result contract"
  - id: IN-07
    severity: info
    disposition: open
    title: "`write_log_atomically` does not enforce the scan that gates it"
  - id: IN-08
    severity: info
    disposition: open
    title: "The zero-byte refusal lives one layer above the function the plan names"
  - id: IN-09
    severity: info
    disposition: open
    title: "The new validators admit a trailing newline and a leading-hyphen environment"
  - id: IN-10
    severity: info
    disposition: open
    title: "Two `NO_BUILD_IMPACT` rules have no test entry"
  - id: WR-13
    severity: warning
    disposition: fixed
    title: "The skill still restates the ambiguous-port rule while claiming it is not restated"
  - id: WR-14
    severity: warning
    disposition: fixed
    title: "The module docstring omits the compound keyword shape the scan now admits"
  - id: IN-11
    severity: info
    disposition: fixed
    title: "The 128-character connector bound is not pinned by a test"
open: 16
total: 31
recorded: 2026-10-27T13:18:00.000Z
---

# Phase 09: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| WR-01 | warning | open | - |
| WR-02 | warning | open | - |
| IN-12 | info | open | - |
| IN-13 | info | open | - |
| IN-14 | info | open | - |
| CR-01 | critical | fixed | 09-17-PLAN.md — review re-run 2026-10-27 confirmed `SECRET KEY: hunter2`, `secret key = hunter2`, `Secret Key: hunter2` and `SECRET KEY = hunter2` match, every pinned benign negative still refuses, and `CredentialScanTests` is 12/12 green. (not in the current review) |
| WR-03 | warning | open | Partially closed by 09-18: the named sentence is gone and one locator remains, but WR-13 records the normative ambiguous-port half still restated at `hw-flash/SKILL.md:50-52` and `:188-189`. (not in the current review) |
| IN-01 | info | open | - (not in the current review) |
| IN-02 | info | open | - (not in the current review) |
| IN-03 | info | open | - (not in the current review) |
| IN-04 | info | open | - (not in the current review) |
| IN-05 | info | open | - (not in the current review) |
| CR-02 | critical | fixed | 09-10-PLAN.md — closed by `scripts/serial_capture.py` `find_credential` and its six-shape test. (not in the current review) |
| CR-03 | critical | fixed | 09-11-PLAN.md — closed by the announced `[--baud <n>]` segment and `BuildCommandTests` pinning the forwarded `-b` argv. (not in the current review) |
| WR-04 | warning | fixed | 09-10-PLAN.md — closed by the announced conditional `-e` segment. (not in the current review) |
| WR-05 | warning | fixed | 09-10-PLAN.md — closed by the `_shared/guardrails.md` "or any log" prohibition. (not in the current review) |
| WR-06 | warning | fixed | 09-10-PLAN.md — closed by the `--raw --quiet` monitor argv. (not in the current review) |
| WR-07 | warning | open | - (not in the current review) |
| WR-08 | warning | open | - (not in the current review) |
| WR-09 | warning | fixed | 09-10-PLAN.md — closed by the rewritten `AGENTS.md` no-build-impact paragraph. (not in the current review) |
| WR-10 | warning | fixed | 09-13-PLAN.md — closed by the `math.isfinite` positive-finite-upper-bound validation before `resolve_root`, the monitor argv or `Popen`. (not in the current review) |
| WR-11 | warning | fixed | 09-13-PLAN.md — closed by the reaping `finally` in `capture_pty`, which kills a live child and waits on every exception path. (not in the current review) |
| WR-12 | warning | fixed | 09-12-PLAN.md — closed by the widened `find_credential` covering the copula, embedded keyword, `passphrase` and `pwd` forms. (not in the current review) |
| IN-06 | info | fixed | 09-11-PLAN.md — closed by `BuildCommandTests`, `CliResultPayloadTests` and the concurrent-reader case. (not in the current review) |
| IN-07 | info | open | - (not in the current review) |
| IN-08 | info | open | - (not in the current review) |
| IN-09 | info | open | - (not in the current review) |
| IN-10 | info | open | - (not in the current review) |
| WR-13 | warning | open | - (not in the current review) |
| WR-14 | warning | open | - (not in the current review) |
| IN-11 | info | open | - (not in the current review) |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.

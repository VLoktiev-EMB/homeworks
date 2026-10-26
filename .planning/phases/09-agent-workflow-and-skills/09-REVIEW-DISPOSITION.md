---
phase: 09
review: 09-REVIEW.md
titles: json
findings:
  - id: CR-01
    severity: critical
    disposition: fixed
    title: "The capture snippet pipes stdout, so `pio device monitor` always exits before the bound"
  - id: CR-02
    severity: critical
    disposition: fixed
    title: "The credential-shape scan misses ordinary assignment forms, so the gated write can persist a credential"
  - id: WR-01
    severity: warning
    disposition: fixed
    title: "The log path is cwd-relative, contradicting the guardrails' scoped path"
  - id: WR-02
    severity: warning
    disposition: fixed
    title: "The symlink discipline claims a race-free guarantee the helper does not implement"
  - id: WR-03
    severity: warning
    disposition: fixed
    title: "The outcome table contradicts the rule that reaching the 20-second bound is a success"
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
  - id: IN-01
    severity: info
    disposition: fixed
    title: "The snippet is not runnable as written"
  - id: IN-02
    severity: info
    disposition: fixed
    title: "`pio project config` emits `monitor_speed` with two different types, and the skill does not normalize"
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
  - id: IN-03
    severity: info
    disposition: open
    title: "The simulation phase reference is stale"
  - id: IN-04
    severity: info
    disposition: open
    title: "The generator tests do not cover the edge cases above"
  - id: IN-05
    severity: info
    disposition: open
    title: "The `gen-skills-check` hook's `files` pattern is untested"
open: 5
total: 16
recorded: 2026-10-26T23:14:20.579Z
---

# Phase 09: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| CR-01 | critical | fixed | 09-10-PLAN.md — closed by `scripts/serial_capture.py` `capture_pty` (pseudo-terminal, no pipe). |
| CR-02 | critical | fixed | 09-10-PLAN.md — closed by `scripts/serial_capture.py` `find_credential` and its six-shape test. |
| WR-01 | warning | fixed | 09-10-PLAN.md — closed by `write_log_atomically` root anchoring. |
| WR-02 | warning | fixed | 09-10-PLAN.md — closed by `write_log_atomically` directory descriptors and the corrected `SKILL.md`. |
| WR-03 | warning | fixed | 09-10-PLAN.md — closed by the corrected `hw-flash` outcome table. |
| WR-04 | warning | fixed | 09-10-PLAN.md — closed by the announced conditional `-e` segment. |
| WR-05 | warning | fixed | 09-10-PLAN.md — closed by the `_shared/guardrails.md` "or any log" prohibition. |
| WR-06 | warning | fixed | 09-10-PLAN.md — closed by the `--raw --quiet` monitor argv. |
| IN-01 | info | fixed | 09-10-PLAN.md — closed by removing the snippet in favour of the helper. |
| IN-02 | info | fixed | 09-10-PLAN.md — closed by the `int(str(value))` normalization. |
| WR-07 | warning | open | - (not in the current review) |
| WR-08 | warning | open | - (not in the current review) |
| WR-09 | warning | fixed | 09-10-PLAN.md — closed by the rewritten `AGENTS.md` no-build-impact paragraph. |
| IN-03 | info | open | - (not in the current review) |
| IN-04 | info | open | - (not in the current review) |
| IN-05 | info | open | - (not in the current review) |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.

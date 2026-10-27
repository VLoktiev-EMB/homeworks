---
phase: 09
review: 09-REVIEW.md
titles: json
findings:
  - id: CR-03
    severity: critical
    disposition: fixed
    title: "`hw-flash` never passes the user-resolved baud to the capture helper"
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
  - id: RR-CR-01
    severity: critical
    disposition: open
    title: "The widened credential scan still persists `secretKey` / `secret_key` / `passwordHash` assignments"
  - id: RR-WR-01
    severity: warning
    disposition: open
    title: "The reaping `finally` can hang the bounded capture and mask the original failure"
  - id: RR-IN-01
    severity: info
    disposition: open
    title: "The announced capture command still is not the executed one on the default duration"
  - id: RR-IN-02
    severity: info
    disposition: open
    title: "The helper's new exit-2 usage error is outside the skill's outcome states"
  - id: RR-IN-03
    severity: info
    disposition: open
    title: "`CliDurationTests` does not prove the ordering the must-have claims"
  - id: RR-IN-04
    severity: info
    disposition: open
    title: "The copula branch now refuses ordinary status lines, and the docstring overstates the negative coverage"
open: 15
total: 31
recorded: 2026-10-27T00:15:41Z
---

# Phase 09: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| CR-03 | critical | fixed | 09-11-PLAN.md — closed by the announced `[--baud <n>]` segment and `BuildCommandTests` pinning the forwarded `-b` argv. (not in the current review) |
| WR-10 | warning | fixed | 09-13-PLAN.md — closed by the `math.isfinite` positive-finite-upper-bound validation before `resolve_root`, the monitor argv or `Popen`. (not in the current review) |
| WR-11 | warning | fixed | 09-13-PLAN.md — closed by the reaping `finally` in `capture_pty`, which kills a live child and waits on every exception path. (not in the current review) |
| WR-12 | warning | fixed | 09-12-PLAN.md — closed by the widened `find_credential` covering the copula, embedded keyword, `passphrase` and `pwd` forms. (not in the current review) |
| IN-06 | info | fixed | 09-11-PLAN.md — closed by `BuildCommandTests`, `CliResultPayloadTests` and the concurrent-reader case. (not in the current review) |
| IN-07 | info | open | - |
| IN-08 | info | open | - |
| IN-09 | info | open | - |
| IN-10 | info | open | - |
| CR-01 | critical | fixed | 09-10-PLAN.md — closed by `scripts/serial_capture.py` `capture_pty` (pseudo-terminal, no pipe). (not in the current review) |
| CR-02 | critical | fixed | 09-10-PLAN.md — closed by `scripts/serial_capture.py` `find_credential` and its six-shape test. (not in the current review) |
| WR-01 | warning | fixed | 09-10-PLAN.md — closed by `write_log_atomically` root anchoring. (not in the current review) |
| WR-02 | warning | fixed | 09-10-PLAN.md — closed by `write_log_atomically` directory descriptors and the corrected `SKILL.md`. (not in the current review) |
| WR-03 | warning | fixed | 09-10-PLAN.md — closed by the corrected `hw-flash` outcome table. (not in the current review) |
| WR-04 | warning | fixed | 09-10-PLAN.md — closed by the announced conditional `-e` segment. (not in the current review) |
| WR-05 | warning | fixed | 09-10-PLAN.md — closed by the `_shared/guardrails.md` "or any log" prohibition. (not in the current review) |
| WR-06 | warning | fixed | 09-10-PLAN.md — closed by the `--raw --quiet` monitor argv. (not in the current review) |
| IN-01 | info | fixed | 09-10-PLAN.md — closed by removing the snippet in favour of the helper. (not in the current review) |
| IN-02 | info | fixed | 09-10-PLAN.md — closed by the `int(str(value))` normalization. (not in the current review) |
| WR-07 | warning | open | - (not in the current review) |
| WR-08 | warning | open | - (not in the current review) |
| WR-09 | warning | fixed | 09-10-PLAN.md — closed by the rewritten `AGENTS.md` no-build-impact paragraph. (not in the current review) |
| IN-03 | info | open | - (not in the current review) |
| IN-04 | info | open | - (not in the current review) |
| IN-05 | info | open | - (not in the current review) |
| RR-CR-01 | critical | open | Gap-closure re-review `cc5fff3..HEAD`; the reviewer's own `CR-01`. Confirmed by the orchestrator: `find_credential` returns False for `{"secretKey": "hunter2"}`, `secret_key = hunter2` and `passwordHash: abcdef`. |
| RR-WR-01 | warning | open | Gap-closure re-review; the reviewer's own `WR-01`. |
| RR-IN-01 | info | open | Gap-closure re-review; the reviewer's own `IN-01`. |
| RR-IN-02 | info | open | Gap-closure re-review; the reviewer's own `IN-02`. |
| RR-IN-03 | info | open | Gap-closure re-review; the reviewer's own `IN-03`. |
| RR-IN-04 | info | open | Gap-closure re-review; the reviewer's own `IN-04`. Confirmed by the orchestrator: `password is required`, `auth is required` and `pwd directory` now match. |

`RR-` rows come from the second review of this phase (`09-REVIEW.md`, reviewed 2026-10-27T00:15:41Z,
covering only the gap-closure delta). The `RR-` prefix exists because that review restarted its ID
series at `CR-01` / `WR-01` / `IN-01` and those ids already carry *fixed* decisions above; recording
them verbatim would have dropped the earlier rows under the id-reuse rule below.

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.

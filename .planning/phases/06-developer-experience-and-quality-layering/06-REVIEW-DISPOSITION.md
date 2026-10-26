---
phase: 06
review: 06-REVIEW.md
titles: json
findings:
  - id: CR-01
    severity: critical
    disposition: open
    title: "`HeaderFilterRegex` is anchored to a repository-relative prefix, so every header diagnostic is discarded"
  - id: CR-02
    severity: critical
    disposition: open
    title: "A header-only push passes the pre-push gate with no analysis at all"
  - id: WR-01
    severity: warning
    disposition: open
    title: "The database guard passes when a newly added source is missing from the database"
  - id: WR-02
    severity: warning
    disposition: open
    title: "The wrapper can select a non-executable esp-clangd and exit 1, contradicting its documented exit codes"
  - id: WR-03
    severity: warning
    disposition: open
    title: "The onboarding guide overstates what is pinned and how many hooks run"
  - id: IN-01
    severity: info
    disposition: open
    title: "Unreachable branch in `described_paths`"
  - id: IN-02
    severity: info
    disposition: open
    title: "The guard-ordering rationale is wrong about pre-commit behavior"
  - id: IN-03
    severity: info
    disposition: open
    title: "A guide test is satisfied by a longer hook id"
  - id: IN-04
    severity: info
    disposition: open
    title: "The workspace recommends only one of the two required extensions"
  - id: IN-05
    severity: info
    disposition: open
    title: "Ruff targets Python 3.13 while the entry scripts declare 3.11"
open: 10
total: 10
recorded: 2026-10-26T11:46:33.622Z
---

# Phase 06: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| CR-01 | critical | open | - |
| CR-02 | critical | open | - |
| WR-01 | warning | open | - |
| WR-02 | warning | open | - |
| WR-03 | warning | open | - |
| IN-01 | info | open | - |
| IN-02 | info | open | - |
| IN-03 | info | open | - |
| IN-04 | info | open | - |
| IN-05 | info | open | - |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.

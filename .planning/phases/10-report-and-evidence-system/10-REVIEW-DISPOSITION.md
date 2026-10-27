---
phase: 10-report-and-evidence-system
review: 10-REVIEW.md
titles: json
findings:
  - id: CR-01
    severity: critical
    disposition: open
    title: "A deeply nested `homework.yaml` crashes the checker with a `RecursionError` traceback"
  - id: CR-02
    severity: critical
    disposition: open
    title: "`parse_diagram` raises `RecursionError` on deeply nested JSON, despite \"never raises\""
  - id: CR-03
    severity: critical
    disposition: open
    title: "`report.path` is trusted and read without containment, so the checker reads outside the repository"
  - id: WR-01
    severity: warning
    disposition: open
    title: "Marker, citation and cross-reference scanners do not skip fenced code, producing both false passes and false rejections"
  - id: WR-02
    severity: warning
    disposition: open
    title: "Required-table lookup takes the first table in range, rejecting a compliant report with an earlier unrelated table"
  - id: WR-03
    severity: warning
    disposition: open
    title: "The section-1 `Implementation commit` row is optional in practice"
  - id: WR-04
    severity: warning
    disposition: open
    title: "Section 10 may be empty although the standard requires at least one entry"
  - id: WR-05
    severity: warning
    disposition: open
    title: "Unknown level-2 headings, appendix placement, and marker-beside-artifact are not enforced"
  - id: WR-06
    severity: warning
    disposition: open
    title: "Ledger provenance is checked only in the `Method` cell for calculated/simulated rows, rejecting compliant rows"
  - id: WR-07
    severity: warning
    disposition: open
    title: "Combined citations (`[1, 6]`, ranges) are invisible, yielding a false RPT-312 and a false pass"
  - id: WR-08
    severity: warning
    disposition: open
    title: "The report template omits the `**Native suite.**` paragraph that RPT-407 requires"
  - id: WR-09
    severity: warning
    disposition: open
    title: "The size bounds are enforced after the whole file is read, and `homework.yaml` has no bound at all"
  - id: WR-10
    severity: warning
    disposition: open
    title: "`scripts/report/contract.py` performs filesystem I/O, contradicting its documented boundary"
  - id: IN-01
    severity: info
    disposition: open
    title: "Evidence tokens are over-broad; a URL or prose token in a backticked span is treated as a path"
  - id: IN-02
    severity: info
    disposition: open
    title: "Report-derived strings are printed without control-character sanitization"
  - id: IN-03
    severity: info
    disposition: open
    title: "The checker passes vacuously when `homeworks/` is absent"
  - id: IN-04
    severity: info
    disposition: open
    title: "Symlink handling is inconsistent for `homework.yaml` and for `homeworks/<id>`"
  - id: IN-05
    severity: info
    disposition: open
    title: "The worked example cites a nonexistent \"section 11\""
  - id: IN-06
    severity: info
    disposition: open
    title: "The `check-report` hook scope omits the metadata helpers the checker imports"
  - id: IN-07
    severity: info
    disposition: open
    title: "The documented record format and the self-audit checklist do not match the CLI"
  - id: IN-08
    severity: info
    disposition: open
    title: "Reference-style links and autolinks are not resolved, although the standard says every link must be"
  - id: IN-09
    severity: info
    disposition: open
    title: "RPT-407/RPT-408 token matching is case-sensitive and negation-blind"
open: 22
total: 22
recorded: 2026-10-27T15:40:00Z
---

# Phase 10: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| CR-01 | critical | open | Block-until-fixed (2026-10-27): RecursionError escapes the YAML-only except; reproduced — rc=1, empty `--json` stdout, traceback. See `10-UAT.md` G-10-1. |
| CR-02 | critical | open | Block-until-fixed (2026-10-27): RecursionError escapes the JSON-only except; reproduced — rc=1, empty `--json` stdout, traceback. See `10-UAT.md` G-10-1. |
| CR-03 | critical | open | Block-until-fixed (2026-10-27): `report.path` uncontained; reproduced reading `/etc/passwd` and `../../../secret.md` outside the root. See `10-UAT.md` G-10-1. |
| WR-01 | warning | open | 10-REVIEW.md |
| WR-02 | warning | open | 10-REVIEW.md |
| WR-03 | warning | open | 10-REVIEW.md |
| WR-04 | warning | open | 10-REVIEW.md |
| WR-05 | warning | open | 10-REVIEW.md |
| WR-06 | warning | open | 10-REVIEW.md |
| WR-07 | warning | open | 10-REVIEW.md |
| WR-08 | warning | open | 10-REVIEW.md |
| WR-09 | warning | open | 10-REVIEW.md |
| WR-10 | warning | open | 10-REVIEW.md |
| IN-01 | info | open | 10-REVIEW.md |
| IN-02 | info | open | 10-REVIEW.md |
| IN-03 | info | open | 10-REVIEW.md |
| IN-04 | info | open | 10-REVIEW.md |
| IN-05 | info | open | 10-REVIEW.md |
| IN-06 | info | open | 10-REVIEW.md |
| IN-07 | info | open | 10-REVIEW.md |
| IN-08 | info | open | 10-REVIEW.md |
| IN-09 | info | open | 10-REVIEW.md |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved.
A `|` in the reason is kept as prose and escaped on the next run.

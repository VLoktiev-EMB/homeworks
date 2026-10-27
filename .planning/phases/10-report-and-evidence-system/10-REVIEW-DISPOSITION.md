---
phase: 10
review: 10-REVIEW.md
titles: json
findings:
  - id: CR-04
    severity: critical
    disposition: open
    title: "An embedded NUL or lone surrogate in `report.path` still crashes the checker with a `ValueError` traceback"
  - id: CR-05
    severity: critical
    disposition: open
    title: "The depth guard was not applied to `StrictBaseLoader`, so a hostile `task.md` still crashes `check_metadata.py`"
  - id: CR-06
    severity: critical
    disposition: open
    title: "A symlinked `homework.yaml` is followed, letting untrusted content read an arbitrary host file and echo its values"
  - id: WR-11
    severity: warning
    disposition: open
    title: "A content-controlled overlong path becomes exit 2 and echoes the absolute candidate path"
  - id: WR-12
    severity: warning
    disposition: open
    title: "`assets/diagram.json` is read through a symlinked parent directory"
  - id: WR-13
    severity: warning
    disposition: open
    title: "Containment is check-then-use; the final open is not anchored to the inspected inode"
  - id: WR-14
    severity: warning
    disposition: open
    title: "`test_hostile_inputs_are_deterministic` is vacuous for the defect it claims to cover, and the two reproduced crashes have no test"
  - id: IN-10
    severity: info
    disposition: open
    title: "`report.path: .` is refused for the wrong stated reason"
  - id: IN-11
    severity: info
    disposition: open
    title: "`StrictSafeLoader` rejects standard YAML merge keys"
  - id: IN-12
    severity: info
    disposition: open
    title: "Duplicated hostile fixtures and JSON-contract tests"
  - id: CR-01
    severity: critical
    disposition: fixed
    title: "A deeply nested `homework.yaml` crashes the checker with a `RecursionError` traceback"
  - id: CR-02
    severity: critical
    disposition: fixed
    title: "`parse_diagram` raises `RecursionError` on deeply nested JSON, despite \"never raises\""
  - id: CR-03
    severity: critical
    disposition: fixed
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
    disposition: deferred
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
open: 27
total: 34
recorded: 2026-10-27T16:20:00.000Z
---

# Phase 10: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| CR-04 | critical | open | 10-REVIEW.md |
| CR-05 | critical | open | 10-REVIEW.md |
| CR-06 | critical | open | 10-REVIEW.md |
| WR-11 | warning | open | 10-REVIEW.md |
| WR-12 | warning | open | 10-REVIEW.md |
| WR-13 | warning | open | 10-REVIEW.md |
| WR-14 | warning | open | 10-REVIEW.md |
| IN-10 | info | open | 10-REVIEW.md |
| IN-11 | info | open | 10-REVIEW.md |
| IN-12 | info | open | 10-REVIEW.md |
| CR-01 | critical | fixed | Closed by 10-09 (`3ca1f6c`); re-review confirmed the `compose_node` depth guard fires for flow and block style and is not alias- or merge-key-bypassable. (not in the current review) |
| CR-02 | critical | fixed | Closed by 10-09 (`eb69d0d`); re-review confirmed `parse_diagram` catches `RecursionError` and emits RPT-207 with parseable JSON. (not in the current review) |
| CR-03 | critical | fixed | Closed by 10-10 (`8b945e3`) for absolute, `..`, intermediate-symlink, final-symlink and absent cases; the residual escape paths are split out as CR-04, CR-06, WR-12 and WR-13. (not in the current review) |
| WR-01 | warning | open | 10-REVIEW.md (not in the current review) |
| WR-02 | warning | open | 10-REVIEW.md (not in the current review) |
| WR-03 | warning | open | 10-REVIEW.md (not in the current review) |
| WR-04 | warning | open | 10-REVIEW.md (not in the current review) |
| WR-05 | warning | open | 10-REVIEW.md (not in the current review) |
| WR-06 | warning | open | 10-REVIEW.md (not in the current review) |
| WR-07 | warning | open | 10-REVIEW.md (not in the current review) |
| WR-08 | warning | open | 10-REVIEW.md (not in the current review) |
| WR-09 | warning | open | 10-REVIEW.md (not in the current review) |
| WR-10 | warning | open | 10-REVIEW.md (not in the current review) |
| IN-01 | info | open | 10-REVIEW.md (not in the current review) |
| IN-02 | info | open | 10-REVIEW.md (not in the current review) |
| IN-03 | info | open | 10-REVIEW.md (not in the current review) |
| IN-04 | info | deferred | Superseded: escalated to CR-06 (symlinked `homework.yaml` is followed and its values echoed). (not in the current review) |
| IN-05 | info | open | 10-REVIEW.md (not in the current review) |
| IN-06 | info | open | 10-REVIEW.md (not in the current review) |
| IN-07 | info | open | 10-REVIEW.md (not in the current review) |
| IN-08 | info | open | 10-REVIEW.md (not in the current review) |
| IN-09 | info | open | 10-REVIEW.md (not in the current review) |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently.

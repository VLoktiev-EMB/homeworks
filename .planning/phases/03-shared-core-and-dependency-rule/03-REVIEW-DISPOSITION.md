---
phase: 03
review: 03-REVIEW.md
titles: json
findings:
  - id: CR-01
    severity: critical
    disposition: fixed
    title: "`lib_deps` alias discards the symlink target, so a forbidden dependency passes the architecture gate"
  - id: WR-01
    severity: warning
    disposition: fixed
    title: "Test-looking environment names skip every config rule"
  - id: WR-02
    severity: warning
    disposition: open
    title: "The \"exactly one adapter\" rule is implemented as \"at most one adapter\""
  - id: WR-03
    severity: warning
    disposition: fixed
    title: "The `native` heuristic short-circuits the `extends` chain and misclassifies a target env"
  - id: WR-04
    severity: warning
    disposition: open
    title: "The GPIO double accepts pin modes and levels that both real adapters reject"
  - id: WR-05
    severity: warning
    disposition: open
    title: "ESP-IDF logging silently filters records the Arduino adapter emits"
  - id: WR-06
    severity: warning
    disposition: open
    title: "The ESP-IDF GPIO adapter rejects the wrong pin range and reports invalid arguments as I/O errors"
  - id: WR-07
    severity: warning
    disposition: open
    title: "`port_time_now_ms` dereferences an unchecked contract, unlike its sibling helper"
  - id: WR-08
    severity: warning
    disposition: open
    title: "`common_debounce_t` has no initializer and no documented initial value"
  - id: WR-09
    severity: warning
    disposition: open
    title: "The bus contracts do not define NULL buffer semantics, and the two in-repo implementations disagree"
  - id: WR-10
    severity: warning
    disposition: open
    title: "`AGENTS.md` still describes the shipped tree as planned and the local gate as three checks"
  - id: IN-01
    severity: info
    disposition: open
    title: "`consume_forced_status` is copied verbatim into three fakes"
  - id: IN-02
    severity: info
    disposition: open
    title: "Unused `<stdint.h>` in the ESP-IDF log adapter"
  - id: IN-03
    severity: info
    disposition: open
    title: "`test_check_architecture.py` cannot be executed directly"
  - id: IN-04
    severity: info
    disposition: open
    title: "The config group passes vacuously when no homework environment exists"
  - id: IN-05
    severity: info
    disposition: open
    title: "Nothing pins the `check-architecture` hook registration"
  - id: IN-06
    severity: info
    disposition: open
    title: "The blocking scan covers `lib/common` but not `lib/port`"
  - id: IN-07
    severity: info
    disposition: open
    title: "The ADR index gives no signal that ADR-0008 supersedes a sentence of ADR-0002"
open: 15
total: 18
recorded: 2026-10-23T22:54:09.258Z
---
# Phase 03: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| CR-01 | critical | fixed | fixed in 6282788: alias now resolves to the symlink target; regression test added |
| WR-01 | warning | fixed | fixed in 6282788: a test-like name exempts only a native environment |
| WR-02 | warning | open | - |
| WR-03 | warning | fixed | fixed in 6282788: only a native-prefixed extends target counts as native |
| WR-04 | warning | open | - |
| WR-05 | warning | open | - |
| WR-06 | warning | open | - |
| WR-07 | warning | open | - |
| WR-08 | warning | open | - |
| WR-09 | warning | open | - |
| WR-10 | warning | open | - |
| IN-01 | info | open | - |
| IN-02 | info | open | - |
| IN-03 | info | open | - |
| IN-04 | info | open | - |
| IN-05 | info | open | - |
| IN-06 | info | open | - |
| IN-07 | info | open | - |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved.

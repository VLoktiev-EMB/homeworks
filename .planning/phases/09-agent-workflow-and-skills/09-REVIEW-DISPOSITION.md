---
phase: 09
review: 09-REVIEW.md
titles: json
findings:
  - id: CR-01
    severity: critical
    disposition: open
    title: "`hw-flash` writes raw device output to a log, which the guardrails forbid"
  - id: CR-02
    severity: critical
    disposition: open
    title: "The capture baud assumption is false for the only real homework"
  - id: WR-01
    severity: warning
    disposition: open
    title: "The capture snippet does not implement the rules stated around it"
  - id: WR-02
    severity: warning
    disposition: open
    title: "`gen_skills.py` adds the \"explicit only\" banner for `disable-model-invocation: false`"
  - id: WR-03
    severity: warning
    disposition: open
    title: "The line-based frontmatter parser under-validates and can reject valid YAML"
  - id: WR-04
    severity: warning
    disposition: open
    title: "`new-homework` waits for exit 2 from a generator that exits 1 for a missing README"
  - id: WR-05
    severity: warning
    disposition: open
    title: "The `--dir` workflow validates the wrong root"
  - id: WR-06
    severity: warning
    disposition: open
    title: "`AGENTS.md` describes an `affected.py` no-build-impact set that no longer exists"
  - id: WR-07
    severity: warning
    disposition: open
    title: "`no-generated-files` does not cover the template-tree generated patterns"
  - id: WR-08
    severity: warning
    disposition: open
    title: "The uv cache override falls back to a fixed shared `/tmp` path"
  - id: IN-01
    severity: info
    disposition: open
    title: "`NO_BUILD_IMPACT` is not tested entry by entry"
  - id: IN-02
    severity: info
    disposition: open
    title: "The `no-generated-files` description omits the new state directory"
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
open: 15
total: 15
recorded: 2026-10-26T22:39:53Z
---

# Phase 09: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| CR-01 | critical | open | - |
| CR-02 | critical | open | - |
| WR-01 | warning | open | - |
| WR-02 | warning | open | - |
| WR-03 | warning | open | - |
| WR-04 | warning | open | - |
| WR-05 | warning | open | - |
| WR-06 | warning | open | - |
| WR-07 | warning | open | - |
| WR-08 | warning | open | - |
| IN-01 | info | open | - |
| IN-02 | info | open | - |
| IN-03 | info | open | - |
| IN-04 | info | open | - |
| IN-05 | info | open | - |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.

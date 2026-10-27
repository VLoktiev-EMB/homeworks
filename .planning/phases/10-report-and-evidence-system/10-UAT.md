---
status: partial
phase: 10-report-and-evidence-system
source: [10-VERIFICATION.md]
started: 2026-10-27T16:35:00Z
updated: 2026-10-27T15:39:39.019Z
---

# Phase 10 — Human Verification (UAT)

## Current Test

[testing complete]

## Tests

### 1. Decide the disposition of the three open critical findings in 10-REVIEW.md
expected: An explicit accept-as-known-limitation or block-until-fixed decision recorded in `10-REVIEW-DISPOSITION.md`; all three were reproduced against the real checker during verification.
result: issue
reported: "Delegated decision (2026-10-27, research-backed): block-until-fixed. All three reproduced against the real checker: CR-01/CR-02 exit 1 with empty --json stdout and a RecursionError traceback; CR-03 read /etc/passwd and ../../../secret.md outside the root."
severity: blocker

### 2. Confirm the semantic truth of the 1.3 measurement ledger
expected: Each `not measured` row was honestly unmeasured — the checker proves structure only (D-14), not truth.
result: pass

### 3. Confirm the calculation catalog covers the 1.3 design
expected: Every quantity in the report's calculation table maps to `CALC-01`…`CALC-06`, or is a deliberate outlier with a stated formula (D-24 keeps membership a human selection aid).
result: pass

### 4. Confirm TOOL-08's narrowing
expected: The contract-derived checklist in `docs/standards/report.md` is accepted as the deliverable (D-28); the scored rubric stays deferred until three real reports exist.
result: pass

### 5. Observe a green `gate` job on the pull request that carries this phase
expected: The aggregated `gate` status check is green on the phase pull request, including the `meta` job's `pre-commit run --all-files` with `check-report`.
result: blocked
blocked_by: other
reason: "No pull request exists for `gsd/phase-10-report-and-evidence-system` (`gh pr list --head … --state all` returns []), the branch has no upstream, and `gh run list --branch …` returns no runs. The aggregated `gate` check is unobservable until the branch is pushed and a pull request is opened."

## Summary

total: 5
passed: 3
issues: 1
pending: 0
skipped: 0
blocked: 1

## Gaps

- gap_id: G-10-1
  truth: "The phase does not advance while CR-01, CR-02 and CR-03 remain unresolved: the checker never raises on untrusted content and never reads outside the repository."
  status: failed
  reason: "Delegated decision: block-until-fixed. Reproduced against the real checker — CR-01/CR-02 raise RecursionError with empty --json stdout and a traceback; CR-03 reads /etc/passwd and ../../../secret.md outside the root."
  severity: blocker
  test: 1
  root_cause: "CR-01: scripts/check_report.py `_read_metadata` catches only yaml.YAMLError, so PyYAML's RecursionError escapes. CR-02: scripts/report/contract.py `parse_diagram` catches only json.JSONDecodeError, so RecursionError escapes. CR-03: scripts/check_report.py joins `report.path` to the homework directory with no absolute/`..` rejection and no component walk, so pathlib discards the base for absolute values and relative escapes reach outside the root."
  artifacts:
    - path: "scripts/check_report.py"
      issue: "`_read_metadata` catches only yaml.YAMLError; RecursionError escapes"
    - path: "scripts/report/contract.py"
      issue: "`parse_diagram` catches only json.JSONDecodeError; RecursionError escapes"
    - path: "scripts/check_report.py"
      issue: "`report.path` is joined and read with no containment"
  missing:
    - "Catch `(yaml.YAMLError, RecursionError)` in `_read_metadata` and emit RPT-001; consider a depth guard in `StrictSafeLoader` so `check_metadata.py` inherits it."
    - "Catch `(ValueError, RecursionError)` in `parse_diagram` and return `Diagram(error=...)`."
    - "Apply lexical and realpath containment plus a component `lstat` walk to `report.path`, emitting RPT-001/RPT-002 on escape."
    - "Add regression tests for all three cases."
  debug_session: ""

---
status: testing
phase: 01-repository-foundation-and-policy-gate
source: [01-VERIFICATION.md]
started: 2026-10-23T17:36:56Z
updated: 2026-10-23T17:36:56Z
---

## Current Test

number: 1
name: Direct-push probe (FOUND-03)
expected: |
  git push origin main on a scratch clone is rejected with a ruleset/protected-branch
  error; the scratch commit is discarded and nothing lands on main.
awaiting: user response

## Tests

### 1. Direct-push probe (FOUND-03)
expected: On a scratch clone, `git checkout main`, `git commit --allow-empty -m "test: ruleset rejection"`, `git push origin HEAD:main` is REJECTED by the ruleset. If it succeeds, stop and report the incident; do not rewrite history.
result: [pending]

### 2. `check_policy.py --apply` idempotence
expected: A second `python3 scripts/check_policy.py --apply` produces no diff, `--check` still exits 0, and `git status --porcelain` is unchanged.
result: [pending]

### 3. Real-GitHub tag creation (FOUND-04)
expected: After a homework pull request is merged into the default branch, `scripts/tag_homework.sh <id>` passes its merged-PR gate via `gh`, creates the tag at `origin/main`, and pushes it exactly once.
result: [pending]

### 4. First CI execution of the security workflow
expected: `.github/workflows/security.yml` runs on a GitHub runner; the gitleaks full-history job passes with redacted output and the reuse lint job reports compliance.
result: [pending]

### 5. Squash-merge and linear-history behaviour (backstop truths)
expected: The Phase 1 pull request squash-merges into exactly one commit on `main`; a second pull request touching the same region must update its base before it can merge.
result: [pending]

### 6. Judgment-tier prohibitions review
expected: No internal course material or original assignment text is present; no document describes a direct-push or force-push workflow.
result: [pending]

### 7. Accepted free-plan limitation (informational)
expected: When the organization plan changes, revisit ADR-0003's trigger for `secret_scanning_validity_checks` and `secret_scanning_non_provider_patterns`; both are unachievable on the current free plan.
result: [pending]

## Summary

total: 7
passed: 0
issues: 0
pending: 7
skipped: 0
blocked: 0

## Gaps

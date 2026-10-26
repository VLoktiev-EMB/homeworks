---
status: testing
phase: 08-fast-ci
source: [08-VERIFICATION.md]
started: 2026-10-26T19:25:00Z
updated: 2026-10-26T19:25:00Z
---

## Current Test

number: 1
name: Активація `gate` як єдиного required status check у ruleset
expected: |
  `gate` appears in the required-checks picker and the merge box shows it as the only required check.
awaiting: user response

## Tests

### 1. Активація `gate` як єдиного required status check у ruleset
expected: After the first green `ci.yml` run on a pull request, open Settings -> Rules -> the `main` ruleset and add `gate` as the required status check (0 approvals). `gate` appears in the picker and the merge box shows it as the only required check.
result: [pending]

### 2. Перший живий зелений прогін `ci.yml` на зміненому homework
expected: Open one pull request that changes `homeworks/1_3-police-flasher` and watch the run. `changes` emits a two-entry build matrix (target plus native), `build` runs `pio run` for the target and `pio test -e native` for native, `meta`, `python-tests` and `static-analysis` are green, and the literal `gate` reports success within its 15-minute budget.
result: [pending]

### 3. Симуляція за міткою `simulate` та її артефакти
expected: Applying the `simulate` label alone starts a fresh run; the `simulate` job runs, the artifact name contains no slash, `serial.log`, `stdout.log` and `quota.json` are present, and the scenario reports `passed`; without the label no simulation runs and `gate` stays green; a fork pull request never reaches the job.
result: [pending]

### 4. Нічний прогін, concurrency і відновлення кеша
expected: Observe one scheduled nightly run and one manual `workflow_dispatch` overlap attempt. The second run is queued rather than run concurrently (`cancel-in-progress: false`), every project with a `platformio.ini` plus `tests` appears in the matrix, and a later pull-request `build` restores the default-branch cache entry.
result: [pending]

### 5. Скасування superseded-прогону та `fail-fast: false`
expected: Open two pull requests against the same branch in quick succession. The superseded run is reported `cancelled`, the newer run produces its own fresh `gate`, and a failing matrix entry does not cancel the other entries of the same run.
result: [pending]

## Summary

total: 5
passed: 0
issues: 0
pending: 5
skipped: 0
blocked: 0

## Gaps

---
status: complete
phase: 08-fast-ci
source: [08-VERIFICATION.md]
started: 2026-10-26T19:25:00Z
updated: 2026-10-26T20:04:22.422Z
---

## Current Test

[testing complete]

## Tests

### 1. Активація `gate` як єдиного required status check у ruleset
expected: After the first green `ci.yml` run on a pull request, open Settings -> Rules -> the `main` ruleset and add `gate` as the required status check (0 approvals). `gate` appears in the picker and the merge box shows it as the only required check.
result: pass

### 2. Перший живий зелений прогін `ci.yml` на зміненому homework
expected: Open one pull request that changes `homeworks/1_3-police-flasher` and watch the run. `changes` emits a two-entry build matrix (target plus native), `build` runs `pio run` for the target and `pio test -e native` for native, `meta`, `python-tests` and `static-analysis` are green, and the literal `gate` reports success within its 15-minute budget.
result: pass

### 3. Симуляція за міткою `simulate` та її артефакти
expected: Applying the `simulate` label alone starts a fresh run; the `simulate` job runs, the artifact name contains no slash, `serial.log`, `stdout.log` and `quota.json` are present, and the scenario reports `passed`; without the label no simulation runs and `gate` stays green; a fork pull request never reaches the job.
result: pass

### 4. Нічний прогін, concurrency і відновлення кеша
expected: Observe one scheduled nightly run and one manual `workflow_dispatch` overlap attempt. The second run is queued rather than run concurrently (`cancel-in-progress: false`), every project with a `platformio.ini` plus `tests` appears in the matrix, and a later pull-request `build` restores the default-branch cache entry.
result: pass
note: "Verified after merge: two dispatches on main serialized (40391648469 in_progress, then 40391668288 queued and started only after it completed), the matrix listed 1_3-police-flasher/native, 1_3-police-flasher/esp32s3_arduino and tests/native plus gitleaks (full history), and the cache key Linux-pio-213dc845… exists on refs/heads/main. Two clauses were not observed directly: the cron trigger (next at 03:17 UTC) and the cache restore inside a later pull-request build, which GitHub performs mechanically from the base-branch entry."

### 5. Скасування superseded-прогону та `fail-fast: false`
expected: Open two pull requests against the same branch in quick succession. The superseded run is reported `cancelled`, the newer run produces its own fresh `gate`, and a failing matrix entry does not cancel the other entries of the same run.
result: pass

## Summary

total: 5
passed: 5
issues: 0
pending: 0
blocked: 0
skipped: 0
blocked: 0

## Gaps

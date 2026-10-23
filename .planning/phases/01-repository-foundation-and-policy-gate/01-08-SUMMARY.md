---
phase: 01-repository-foundation-and-policy-gate
plan: 08
subsystem: infra
tags: [git-tags, bash, precondition-gates, d-11, found-04, python-unittest, offline-tests]

# Dependency graph
requires:
  - phase: 01-repository-foundation-and-policy-gate
    provides: "scripts/tests/ package, unittest discovery, and the PASS/FAIL + aggregate-exit script style from plan 01-01"
provides:
  - "scripts/tag_homework.sh — deterministic hw/<id> tagger (mode 755) with D-11 precondition gates"
  - "scripts/tests/test_tag_homework.py — offline temp-repo refusal suite plus a no-forced-tag source assertion"
  - "Documented offline override TAG_HOMEWORK_SKIP_REMOTE for network-free tag tests"
affects: [01-06-agents-md, phase-08-ci]

actuals:
  tokens: 3583
  tasks: 2
  commits: 3
  plan_head_before: 76110a09422d192d0b0317b313f02b1d33855c42
  plan_head_after: 021ea481126a6dd1e7afdc9b5cbfe4d81af9b59f

tech-stack:
  added: []
  patterns:
    - "Precondition-gated action script: check every gate first, accumulate status, act only when the aggregate is zero"
    - "Offline shell-script tests: run the real script against a throwaway git repo with an explicit skip-remote override and an isolated git identity"

key-files:
  created:
    - scripts/tag_homework.sh
    - scripts/tests/test_tag_homework.py
  modified: []

key-decisions:
  - "The ID-shape precondition is a usage error and stops the run with exit 2 immediately after its FAIL line; the remaining D-11 preconditions (homework dir, tag unused, merged PR) all run and are aggregated into one exit code, exactly as scripts/review_smoke_test.sh does."
  - "TAG_HOMEWORK_SKIP_REMOTE=1 skips BOTH network gates (the origin ls-remote tag lookup and the gh merged-PR check), so unit tests never need network or a gh login; the override is documented as tests-only in --help."
  - "The tag base is resolved from refs/remotes/origin/HEAD rather than a hardcoded refs/remotes/origin/main, so the script keeps working if the default branch is renamed."
  - "A failed ls-remote is a FAIL, not a PASS: the remote tag check fails closed so a network error can never be mistaken for 'tag is unused'."
  - "The tag is lightweight (no -a) and pushed with an explicit refs/tags/ refspec once; an existing tag is never overwritten or moved and there is no override flag."

patterns-established:
  - "Aggregate precondition pattern: PASS/SKIP lines on stdout, FAIL lines on stderr, one exit code at the end (0 success / 1 precondition failure / 2 usage)."
  - "Source-level invariant test: read the script and fail if any forced git tag/push invocation appears, so the 'never moves a tag' truth is protected by the suite rather than by review."

requirements-completed: [FOUND-04]

coverage:
  - id: D1
    description: "tag_homework.sh refuses an already-existing hw/<id> tag and leaves the tag ref untouched"
    requirement: FOUND-04
    verification:
      - kind: unit
        ref: "scripts/tests/test_tag_homework.py#test_existing_tag_is_refused"
        status: pass
    human_judgment: false
  - id: D2
    description: "Invalid IDs (malformed, empty, uppercase) exit 2 with no tag created; a valid ID without homeworks/<id>/ exits 1"
    requirement: FOUND-04
    verification:
      - kind: unit
        ref: "scripts/tests/test_tag_homework.py#test_invalid_ids_are_rejected"
        status: pass
      - kind: unit
        ref: "scripts/tests/test_tag_homework.py#test_missing_homework_directory_is_refused"
        status: pass
    human_judgment: false
  - id: D3
    description: "The script source contains no forced tag or push invocation"
    requirement: FOUND-04
    verification:
      - kind: unit
        ref: "scripts/tests/test_tag_homework.py#test_source_has_no_forced_tag_or_push"
        status: pass
    human_judgment: false
  - id: D4
    description: "The success path — create the tag at the default-branch commit and push it once to origin"
    requirement: FOUND-04
    verification: []
    human_judgment: true
    rationale: "Requires a real merged homework pull request and a live origin; the suite deliberately covers only the refusal paths, so the creation/push path has not been executed even once."
  - id: D5
    description: "ShellCheck clean"
    verification: []
    human_judgment: false
    rationale: "shellcheck is not installed in this environment; the script passes bash -n and is written to the ShellCheck-friendly style used by scripts/review_smoke_test.sh."

duration: ~2min
completed: 2026-10-23
status: complete
---

# Phase 1 Plan 08: Homework Tag Gate Summary

**`scripts/tag_homework.sh` makes the human-created `hw/<id>` tag deterministic: four D-11 preconditions are checked in order, an existing tag is refused and never moved, and the whole refusal behavior is pinned by an offline temp-repo suite — leaving only the success path unexercised.**

## Performance

- **Duration:** ~2 min
- **Started:** 2026-10-23T17:14:18Z
- **Completed:** 2026-10-23T17:16:32Z
- **Tasks:** 2 of 2 complete
- **Files modified:** 2 created

## Accomplishments

- Added `scripts/tag_homework.sh` (mode 755) which checks the D-11 gates in a fixed
  order and only then creates a lightweight `hw/<id>` tag at the origin default
  branch's commit and pushes it once.
- Made "never duplicate, never move a tag" a testable property: the refusal cases
  assert the tag ref is unchanged, and a source-level test fails if any forced
  `git tag` / `git push` invocation is ever added.
- Kept the suite fully offline through the documented `TAG_HOMEWORK_SKIP_REMOTE=1`
  override, with an isolated git identity and `GIT_CONFIG_GLOBAL=/dev/null` so the
  fixture works on any machine without a configured git user.
- Verified the whole phase suite stays green: 14 tests (10 from plan 01-01 + 4 new).

## Precondition order (for AGENTS.md's routing table)

`scripts/tag_homework.sh <id>` evaluates, in this order:

1. **ID shape** — `^[0-9]+_[0-9]+-[a-z0-9-]+$`. Failure prints `FAIL id:` and exits **2**
   (usage error) before any further check.
2. **Homework directory** — `homeworks/<id>/` exists. Failure: `FAIL homework:`, status 1.
3. **Tag unused locally** — `git rev-parse -q --verify refs/tags/hw/<id>`. Failure:
   `FAIL tag:`, status 1.
4. **Tag unused on origin** — `git ls-remote --tags origin refs/tags/hw/<id>`; a failing
   `ls-remote` is itself a FAIL. Failure: `FAIL remote-tag:`, status 1.
5. **Merged PR** — `gh pr list --state merged --head hw/<id> --json number --jq length`
   must be non-zero. Failure: `FAIL merged-pr:`, status 1.

Only when all gates pass: `git fetch origin`, resolve `refs/remotes/origin/HEAD`, create
the tag at that commit, `git push origin refs/tags/hw/<id>` once, print `PASS:`.

**Offline override:** `TAG_HOMEWORK_SKIP_REMOTE=1` prints `SKIP` lines for gates 4 and 5.
Documented in `--help` as offline-tests-only. Exit codes: `0` success, `1` precondition or
push failure, `2` usage error.

## TDD evidence

### RED (commit `91da7ac`)

Command: `NO_COLOR=1 python3 -m unittest scripts.tests.test_tag_homework -v`

```
Ran 4 tests in 0.235s

FAILED (failures=6)
```

All six failures are the intended assertion — `AssertionError:
.../scripts/tag_homework.sh does not exist yet` — raised by the suite's own
`_require_script()` guard. No import, load, or fixture error appeared
(`unittest.loader._FailedTest` absent), so the module loaded and every test method
executed and failed on its planned behavior, not on setup.

**Semantic assessment:** valid RED. Each of the four test methods (with the three invalid-ID
subTests) failed because the subject under test had no implementation, which is exactly the
planned expected-vs-actual gap.

### GREEN (commit `021ea48`)

Command: `NO_COLOR=1 python3 -m unittest scripts.tests.test_tag_homework -v`

```
Ran 4 tests in 0.398s

OK
```

Full suite: `NO_COLOR=1 python3 -m unittest discover -s scripts/tests -v` → `Ran 14 tests … OK`.

### REFACTOR

None. The script was written once to the analog's style; no cleanup pass was needed.

## Task Commits

1. **Task 1: failing refusal suite (`test_tag_homework.py`)** — `91da7ac` (test)
2. **Lint follow-up on the test runner** — `bafe67d` (style)
3. **Task 2: `tag_homework.sh` precondition gate** — `021ea48` (feat)

## Files Created/Modified

- `scripts/tag_homework.sh` — D-11-gated tagger; `--help`, usage error exit 2, aggregated
  precondition exit 1, lightweight tag at the default-branch commit pushed once.
- `scripts/tests/test_tag_homework.py` — 4 tests / 6 assertions-level cases: existing tag
  refused and unchanged, invalid IDs, missing homework directory, no forced invocation in
  source.

## Decisions Made

- The ID-shape gate exits 2 immediately: a malformed ID is a usage error, and running the
  remaining checks against a path that cannot name a homework only produces misleading FAIL
  lines. The other three preconditions run to completion and aggregate into one exit code,
  matching `scripts/review_smoke_test.sh`.
- The remote gate fails closed. An `ls-remote` error is reported as `FAIL remote-tag:` with
  status 1 rather than being read as "no tag found", which would let an offline or
  unauthenticated run create a duplicate tag.
- The base commit is resolved through `refs/remotes/origin/HEAD` instead of hardcoding
  `origin/main`, per the wave instruction not to hardcode the default branch.
- No force flag exists anywhere in the script, including in its help text, so the
  source-level invariant test can assert the absence of the literal token.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Commits aborted because the worktree has no `.pre-commit-config.yaml`**
- **Found during:** Task 1 commit
- **Issue:** A globally installed pre-commit hook runs on `git commit` and exits 1 with
  `No .pre-commit-config.yaml file was found`. The config file belongs to a sibling plan in
  this same wave and is not present on this branch.
- **Fix:** Committed with `PRE_COMMIT_ALLOW_NO_CONFIG=1`, the hook's own documented opt-out.
  `--no-verify` was deliberately not used.
- **Files modified:** none
- **Verification:** All three commits were created normally and the hook reported
  `Skipping pre-commit`.
- **Committed in:** `91da7ac`, `bafe67d`, `021ea48`

**2. [Rule 1 - Bug] ruff PLW1510 on the test runner**
- **Found during:** Task 2 verification (`ruff check`)
- **Issue:** `subprocess.run` in `_run()` had no explicit `check` argument; the flag is
  intentional (the refusal cases must inspect non-zero exits) but implicit.
- **Fix:** Added `check=False` explicitly; behavior unchanged.
- **Files modified:** `scripts/tests/test_tag_homework.py`
- **Verification:** `ruff check` clean; suite still 4/4 OK.
- **Committed in:** `bafe67d`

---

**Total deviations:** 2 auto-fixed (1 blocking, 1 bug)
**Impact on plan:** Neither changed scope or behavior. The blocking fix was a wave-order
artifact (missing pre-commit config), not a plan defect.

## Issues Encountered

- `shellcheck` is not installed in this environment, so the ShellCheck check was skipped;
  `bash -n` is clean and the script follows the existing repository shell style.
- Running the suite generates `scripts/__pycache__/` and `scripts/tests/__pycache__/`. This
  branch has no `.gitignore` yet (it ships with a sibling plan), so they remain untracked and
  were deliberately not staged.
- The success path (`fetch` → resolve default branch → `tag` → `push`) has not been executed
  in any form. It is implemented, reviewed against `git` semantics, and reachable only with a
  live `origin`; see coverage item D4.

## Known Stubs

None.

## Threat Flags

None — the changed files stay inside the plan's threat model. T-1-07 (tag refs mutable
outside the script) remains accepted and is recorded for ADR-0003; T-1-SC is satisfied (no
packages installed).

## Next Phase Readiness

- AGENTS.md (plan 01-06) can route tag creation to `scripts/tag_homework.sh <id>` and cite
  the precondition order above; there is no other tag path.
- Phase 8 CI can invoke `python3 -m unittest discover -s scripts/tests` unchanged; the new
  tests add no network, no credentials, and no external tool beyond `git`.
- Residual, accepted gap (ADR-0003): a maintainer with push access can still move a tag
  outside the script, because branch rulesets never apply to tag refs.

## Self-Check: PASSED

- `scripts/tag_homework.sh` and `scripts/tests/test_tag_homework.py` exist on disk.
- Commits `91da7ac`, `bafe67d`, `021ea48` are ancestors of HEAD.
- `bash -n scripts/tag_homework.sh` — clean; mode `-rwxr-xr-x`.
- `scripts/tag_homework.sh --help` — exit 0.
- `python3 -m unittest scripts.tests.test_tag_homework -v` — 4 tests, OK.
- `python3 -m unittest discover -s scripts/tests -v` — 14 tests, OK.
- `ruff check scripts/tests/test_tag_homework.py` — clean.

---
*Phase: 01-repository-foundation-and-policy-gate*
*Completed: 2026-10-23*

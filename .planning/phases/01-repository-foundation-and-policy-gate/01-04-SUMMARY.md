---
phase: 01-repository-foundation-and-policy-gate
plan: 04
subsystem: infra
tags: [licensing, reuse, spdx, mit, cc-by-4.0, notice, pii, python-unittest]

# Dependency graph
requires:
  - plan: 01-01
    provides: "scripts/tests/ package and the pinned reuse 6.2.0 tool"
provides:
  - "LICENSE — MIT grant with one handle-only copyright line"
  - "NOTICE — license-split statement, MADR 4.0.0 attribution, trademark section"
  - "LICENSES/MIT.txt and LICENSES/CC-BY-4.0.txt — REUSE-required canonical texts"
  - "REUSE.toml — single declaration point: MIT catch-all plus CC-BY-4.0 overrides"
  - "scripts/tests/test_license_hygiene.py — 15 tests covering PII, lint, and the SPDX split"
affects:
  - "01-06 — README.md links LICENSE and NOTICE and states the split"
  - "01-07 — ADR-0004 records the REUSE.toml substitution and the PR-template boundary"
  - "phase-08-ci — reuse lint joins the pull-request pipeline"

actuals:
  tokens: 8664
  tasks: 2
  commits: 4
  plan_head_before: 76110a09422d192d0b0317b313f02b1d33855c42
  plan_head_after: bb5844d79a23a68eb0c9e6c3dc71d1971d983ccf

tech-stack:
  added: []
  patterns:
    - "REUSE.toml: one `**` catch-all first, overrides after it — reuse-tool matches annotations last-to-first, so ordering is the precedence mechanism"
    - "Mechanical PII guard: tests read `git config user.name`/`user.email` at runtime and compare published legal files against them"

key-files:
  created:
    - LICENSE
    - NOTICE
    - LICENSES/MIT.txt
    - LICENSES/CC-BY-4.0.txt
    - REUSE.toml
    - scripts/tests/test_license_hygiene.py
  modified: []

key-decisions:
  - "REUSE.toml replaces the `.reuse/dep5` artifact named by D-15 — DEP5 is deprecated in REUSE 3.3 and the two formats never coexist. ADR-0004 (plan 01-07) must record the substitution."
  - "The three `.github/PULL_REQUEST_TEMPLATE/*.md` files stay on the MIT catch-all: they are contribution machinery, not documentation or a report, so the OSPO 'not code → CC-BY' rationale does not reach them."
  - "LICENSES/MIT.txt keeps the SPDX placeholder `Copyright (c) <year> <copyright holders>` because license bodies are not hand-edited; the real handle-only line lives in LICENSE."
  - "reuse lint and reuse spdx are invoked with the global `--no-multiprocessing` flag — deterministic output, and the only way they run in a sandbox that denies POSIX semaphores."

patterns-established:
  - "Test-side artifact reader (`ArtifactTestCase.read_artifact`) asserts existence before reading, so a missing artifact reports as a clean assertion instead of an exception."
  - "Assertion messages never interpolate the git identity value, keeping PII out of test output and CI logs."

requirements-completed: [FOUND-06]

coverage:
  - id: D1
    description: "MIT LICENSE with a single handle-only copyright line, a NOTICE carrying third-party attribution and trademark sections, and the two REUSE-required canonical license texts"
    requirement: FOUND-06
    verification:
      - kind: unit
        ref: "scripts/tests/test_license_hygiene.py#LicenseFileTest"
        status: pass
      - kind: unit
        ref: "scripts/tests/test_license_hygiene.py#NoticeFileTest"
        status: pass
      - kind: unit
        ref: "scripts/tests/test_license_hygiene.py#LicenseTextsTest"
        status: pass
      - kind: integration
        ref: "grep -c '^Copyright (c) 2026 VLoktiev-EMB$' LICENSE → 1"
        status: pass
    human_judgment: false
  - id: D2
    description: "One REUSE.toml declares the MIT/CC-BY-4.0 split and reuse lint reports full coverage"
    requirement: FOUND-06
    verification:
      - kind: unit
        ref: "scripts/tests/test_license_hygiene.py#ReuseDeclarationTest.test_reuse_toml_exists_and_dep5_does_not"
        status: pass
      - kind: unit
        ref: "scripts/tests/test_license_hygiene.py#ReuseDeclarationTest.test_reuse_toml_declares_the_documented_globs"
        status: pass
      - kind: integration
        ref: "reuse --no-multiprocessing lint → exit 0, 41/41 files"
        status: pass
    human_judgment: false
  - id: D3
    description: "The SPDX dump resolves code paths to MIT and documentation paths to CC-BY-4.0"
    requirement: FOUND-06
    verification:
      - kind: unit
        ref: "scripts/tests/test_license_hygiene.py#ReuseDeclarationTest.test_spdx_dump_separates_code_from_documentation"
        status: pass
    human_judgment: false
  - id: D4
    description: "The public-handle-only rule is enforced mechanically against the configured git identity"
    requirement: FOUND-06
    verification:
      - kind: unit
        ref: "scripts/tests/test_license_hygiene.py#NoPublishedIdentityTest"
        status: pass
    human_judgment: false
  - id: D5
    description: "The `.github/PULL_REQUEST_TEMPLATE/*.md` MIT boundary decision is carried into ADR-0004"
    verification: []
    human_judgment: true
    rationale: "The decision is recorded in this SUMMARY and must be restated in ADR-0004 by plan 01-07; no test can prove a rationale reached a document written in another plan."

duration: ~20min
completed: 2026-10-23
status: complete
---

# Phase 1 Plan 04: License Boundary and REUSE Declaration Summary

**MIT for code and CC-BY-4.0 for documentation and reports, declared once in REUSE.toml
with a `**` catch-all first and overrides after it — lint-verified at 41/41 files, with
the handle-only identity and a mechanical guard against the configured git identity.**

## Performance

- **Duration:** ~20 min
- **Started:** not captured
- **Completed:** 2026-10-23
- **Tasks:** 2 of 2 complete
- **Files modified:** 6 created

## Accomplishments

- Published the irreversible grant with the public handle as the only identity:
  `LICENSE` carries the MIT text and exactly one copyright line,
  `Copyright (c) 2026 VLoktiev-EMB`.
- Wrote `NOTICE` with the license split, the MADR 4.0.0 attribution
  (`adr/madr`, MIT), the statement that no other third-party material — and
  specifically no Fritzing part graphics — is redistributed, and a trademark
  section naming Espressif, STMicroelectronics, and Arduino.
- Fetched the canonical license texts with `reuse download` instead of
  hand-writing them, then declared the whole split in a single `REUSE.toml`.
- Built a hygiene suite that fails if a real name or institution ever appears:
  it compares `LICENSE` and `NOTICE` against `git config user.name` and
  `user.email` at run time, so no real identity is written into the repository.
- Proved the declaration with both instruments the plan asked for: `reuse lint`
  exits 0 with every file declared, and the SPDX dump separates
  `scripts/check_policy.py` → MIT from `README.md` / `.planning/**` → CC-BY-4.0.

## Final REUSE.toml annotation list

Two annotations, in this order (reuse-tool evaluates last-to-first, so the
catch-all must stay first):

| # | `path` | `SPDX-License-Identifier` | `SPDX-FileCopyrightText` |
|---|--------|---------------------------|---------------------------|
| 1 | `**` | `MIT` | `2026 VLoktiev-EMB` |
| 2 | `["*.md", "docs/**", "homeworks/**/*.md", ".planning/**"]` | `CC-BY-4.0` | `2026 VLoktiev-EMB` |

Verified associations from `reuse --no-multiprocessing spdx`:

| Path | License |
|------|---------|
| `scripts/check_policy.py` | MIT |
| `scripts/tests/*.py`, `policy/*.json`, `NOTICE`, `.claude/CLAUDE.md` | MIT |
| `README.md` | CC-BY-4.0 |
| `.planning/PROJECT.md`, all `.planning/**` | CC-BY-4.0 |

Root `*.md` is root-only under reuse's anchored glob translation
(`[^/]*\.md` cannot cross a path separator), so nested Markdown is governed by
the explicit `docs/**`, `homeworks/**/*.md`, and `.planning/**` globs.

## reuse lint summary line

```
* Used licenses: CC-BY-4.0, MIT
* Read errors: 0
* Files with copyright information: 41 / 41
* Files with license information: 41 / 41

Congratulations! Your project is compliant with version 3.3 of the REUSE Specification :-)
```

Exit code: **0**. No `.reuse/dep5` exists; no per-file SPDX headers were added.

The count was **41 / 41** at the Task 2 GREEN run and **42 / 42** on the final
verification, which ran with this SUMMARY file present — it is covered by the
`.planning/**` CC-BY-4.0 annotation. The summary line is otherwise identical.

## License-download method (LICENSES/ texts)

Both canonical texts came from the tool itself, not from hand editing:

```
$ reuse download MIT
Successfully downloaded LICENSES/MIT.txt.

$ reuse download CC-BY-4.0
Successfully downloaded LICENSES/CC-BY-4.0.txt.
```

No fallback path was needed. Sizes: `MIT.txt` 1,078 bytes, `CC-BY-4.0.txt`
17,023 bytes. `MIT.txt` retains the SPDX placeholder copyright line by design.

## `.github/PULL_REQUEST_TEMPLATE/*.md` boundary decision — for ADR-0004

The three pull-request templates (created by plan 01-05) are **deliberately left
on the MIT catch-all**. They are contribution machinery — the contract a
contributor fills in — not documentation and not a homework report, so the OSPO
"not code → use CC-BY" rationale does not reach them. The catch-all already
covers those paths, so this plan asserts no annotation ordering against plan
01-05's files.

## TDD Cycles

Both tasks ran RED → GREEN. The plan is `type: execute` with `tdd="true"` tasks;
`workflow.tdd_mode` is `false` in `.planning/config.json`, so no machine gate
classifier ran — the evidence below is recorded for review.

### Task 1 — LICENSE, NOTICE, LICENSES texts, hygiene test

**RED** (`414f321`)

- **Command:** `NO_COLOR=1 python3 -m unittest scripts.tests.test_license_hygiene -v`
- **Exit:** 1 — `Ran 10 tests`, `FAILED (failures=12)`
- **Expected:** artifacts present, all assertions pass.
- **Actual:** every failure named a missing artifact — `LICENSE is missing`,
  `NOTICE is missing`, `LICENSES/MIT.txt is missing`,
  `LICENSES/CC-BY-4.0.txt is missing`.
- **Semantic assessment:** all 10 planned tests were discovered and each failed
  on its planned existence/content assertion. No import, syntax, or loader
  failure. A first run produced 4 failures plus 8 `FileNotFoundError` errors;
  that was refactored into `ArtifactTestCase.read_artifact` so a missing file
  reports as an assertion — a test-design fix, made before the RED commit.

**GREEN** (`acb7200`)

- Same command: `Ran 10 tests … OK`.
- `grep -c '^Copyright (c) 2026 VLoktiev-EMB$' LICENSE` → `1`.

### Task 2 — REUSE.toml, lint, SPDX spot-check

**RED** (`3902d4f`)

- **Command:** same suite, now 15 tests.
- **Exit:** 1 — `FAILED (failures=5)`, all five new checks failing:
  `REUSE.toml is missing`, lint non-zero, no SPDX association, globs absent,
  ordering absent.
- **Semantic assessment:** the failures are the planned "declaration absent"
  assertions. `reuse spdx` initially crashed inside `ProcessPoolExecutor` on a
  sandbox POSIX-semaphore denial, so the helper was switched to the tool's
  `--no-multiprocessing` flag; the RED verdict above is from the post-fix run.

**GREEN** (`bb5844d`)

- `Ran 15 tests … OK`; `reuse --no-multiprocessing lint` → exit 0, 41/41.
- Phase-gate preview: `python3 -m unittest discover -s scripts/tests -v` →
  `Ran 25 tests … OK`.

## Task Commits

1. **Task 1 RED: failing license hygiene tests** — `414f321` (test)
2. **Task 1 GREEN: LICENSE, NOTICE, canonical texts** — `acb7200` (feat)
3. **Task 2 RED: failing REUSE declaration tests** — `3902d4f` (test)
4. **Task 2 GREEN: REUSE.toml declaration** — `bb5844d` (feat)

The plan-metadata commit (this SUMMARY) follows.

## Files Created/Modified

- `LICENSE` — MIT text, one handle-only copyright line
- `NOTICE` — license split, MADR attribution, Fritzing exclusion, trademarks
- `LICENSES/MIT.txt` — canonical MIT text from the SPDX list
- `LICENSES/CC-BY-4.0.txt` — canonical CC-BY-4.0 legal code
- `REUSE.toml` — version 1, two annotations (MIT catch-all, CC-BY-4.0 override)
- `scripts/tests/test_license_hygiene.py` — 15 tests across four classes

## Decisions Made

- **REUSE.toml over `.reuse/dep5`.** D-15 names dep5, REUSE 3.3 deprecates it,
  and reuse-tool 6.2.0 reads `REUSE.toml`. The two formats never coexist; ADR-0004
  must state the substitution.
- **Ordering is the precedence mechanism.** reuse-tool's
  `find_annotations_item` iterates annotations in reverse and returns the last
  match, so the MIT catch-all is first and the CC-BY-4.0 override is last. A
  test pins that ordering so a future edit cannot silently invert the split.
- **Root `*.md` is root-only.** reuse anchors each glob with `^…$` and translates
  `*` to `[^/]*`, so `*.md` cannot reach nested Markdown. Nested documentation is
  named explicitly instead of relying on a gitignore-style interpretation.
- **`--no-multiprocessing` for every reuse invocation.** It makes output
  deterministic and is required in this sandbox; it changes no result.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Every commit required `PRE_COMMIT_ALLOW_NO_CONFIG=1`**
- **Found during:** Task 1, first commit
- **Issue:** a pre-commit hook is installed in the shared git directory, but
  `.pre-commit-config.yaml` does not exist on this branch — plan 01-03, running
  in a parallel worktree, is the plan that adds it. The hook aborted the commit.
- **Fix:** committed with `PRE_COMMIT_ALLOW_NO_CONFIG=1`, which lets pre-commit
  run with no config instead of skipping verification. `--no-verify` was never
  used.
- **Files modified:** none
- **Verification:** hook output reads `` `.pre-commit-config.yaml` config file not
  found. Skipping `pre-commit`. `` on all four commits.
- **Committed in:** all four task commits
- **Note for the orchestrator:** the condition disappears once 01-03 merges.

**2. [Rule 3 - Blocking] `reuse lint` and `reuse spdx` crash in this sandbox**
- **Found during:** Task 2, first RED run
- **Issue:** both commands build a `ProcessPoolExecutor`, and
  `os.sysconf("SC_SEM_NSEMS_MAX")` raises `PermissionError: [Errno 1] Operation
  not permitted` under the macOS seatbelt sandbox.
- **Fix:** every invocation uses the tool's global `--no-multiprocessing` flag.
  The tests call the same flag, so the suite is portable and deterministic
  rather than tuned to this machine.
- **Files modified:** `scripts/tests/test_license_hygiene.py`
- **Verification:** `reuse --no-multiprocessing lint` → exit 0, 41/41 files.
- **Committed in:** `bb5844d`

---

**Total deviations:** 2 auto-fixed (both Rule 3 - blocking)
**Impact on plan:** neither changes an artifact or an assertion. One is a
transient worktree condition owned by a parallel plan; the other is a tool flag.

## Issues Encountered

- The first RED run surfaced missing artifacts as `FileNotFoundError` (ERROR)
  rather than as failed assertions. Fixed by asserting existence before reading,
  which also gives a clearer failure message. Done inside Task 1 before its RED
  commit.
- `scripts/tests/__pycache__/` and `scripts/__pycache__/` are generated by the
  test runs and were removed before each commit; `.gitignore` is plan 01-02's
  artifact, so no ignore rule was added here.

## User Setup Required

None — no external service configuration required.

## Known Stubs

None.

## Threat Flags

None — the changed files stay inside the plan's threat model (T-1-03
information disclosure, T-1-06 third-party attribution, T-1-SC reuse install).

## Next Phase Readiness

- `LICENSE` and `NOTICE` exist for README.md (plan 01-06) to link.
- `REUSE.toml` is ready for `reuse lint` to join CI in Phase 8.
- **For plan 01-07 (ADR-0004):** record (a) the `REUSE.toml` substitution for
  `.reuse/dep5`; (b) the `.github/PULL_REQUEST_TEMPLATE/*.md` stay-on-MIT
  boundary and its rationale; (c) the ordering-based precedence mechanism
  (catch-all first, overrides last); (d) that root `*.md` is root-only under
  reuse glob semantics; and (e) the stale SIM-02 "ADR-0004" reference noted in
  RESEARCH Open Question 2.
- The hygiene suite is the mechanical guard for FOUND-06 and runs in the phase
  gate with the rest of `scripts/tests`.

## Self-Check: PASSED

- All six planned files exist on disk.
- Commits `414f321`, `acb7200`, `3902d4f`, `bb5844d` are ancestors of HEAD.
- `python3 -m unittest scripts.tests.test_license_hygiene -v` — 15 tests, OK.
- `python3 -m unittest discover -s scripts/tests -v` — 25 tests, OK.
- `reuse --no-multiprocessing lint` — exit 0, 41/41 files.
- `grep -c '^Copyright (c) 2026 VLoktiev-EMB$' LICENSE` — 1.

---
*Phase: 01-repository-foundation-and-policy-gate*
*Completed: 2026-10-23*

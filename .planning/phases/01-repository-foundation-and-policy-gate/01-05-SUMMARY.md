---
phase: 01-repository-foundation-and-policy-gate
plan: 05
subsystem: infra
tags: [pull-request-templates, template-drift, contract-check, python-unittest, subprocess, github]

# Dependency graph
requires:
  - phase: 01-repository-foundation-and-policy-gate
    provides: "scripts/tests/ package and the unittest discovery contract (plan 01-01)"
provides:
  - ".github/PULL_REQUEST_TEMPLATE/{homework,infra,docs}.md — shared header + per-type DoD"
  - "scripts/check_pr_templates.py — marker-slice drift checker, exit codes 0/1/2"
  - "scripts/tests/test_check_pr_templates.py — real-tree and tempdir contract suite"
  - "proof that the chooser cannot be suppressed by a stray default template"
affects: [phase-08-ci, all-future-pull-requests]

actuals:
  tokens: 4813
  tasks: 2
  commits: 3
  plan_head_before: 76110a09422d192d0b0317b313f02b1d33855c42
  plan_head_after: 3f7fd5b00363225c2b54c03a2b8f53ce569ab704

tech-stack:
  added: []
  patterns:
    - "Delimited shared contract: an identical byte range between HTML comment markers, compared across sibling documents"
    - "Tempdir fixtures pointing the checker at a copied tree via a single --dir seam"
    - "Exit-code contract 0 = clean / 1 = contract violation / 2 = usage or missing file"

key-files:
  created:
    - .github/PULL_REQUEST_TEMPLATE/homework.md
    - .github/PULL_REQUEST_TEMPLATE/infra.md
    - .github/PULL_REQUEST_TEMPLATE/docs.md
    - scripts/check_pr_templates.py
    - scripts/tests/test_check_pr_templates.py
  modified: []

key-decisions:
  - "The checker compares only the byte slice strictly between the markers; a whole-file comparison would fail by design because the Definition of Done differs per type (D-23)."
  - "A malformed marker pair is reported as two failures (markers + header) because a header cannot be compared without them, keeping the report honest rather than skipping the check."
  - "The DoD check requires at least one checklist row under every '## Definition of Done' heading; it deliberately does not pin exact wording, so templates can evolve without a code change."
  - "Default-template detection covers repo root, docs/, and .github/ in both casings, plus default.md/DEFAULT.md inside the template directory."

patterns-established:
  - "Contract files ship with a local checker in the same commit series; CI wiring is deferred, the assertion is not."
  - "Negative fixtures mutate exactly one property of a copied real tree, so each test names one contract clause."

requirements-completed: [FOUND-05]

coverage:
  - id: D1
    description: "Three type-specific PR templates exist with one identical shared header and distinct Definitions of Done"
    requirement: FOUND-05
    verification:
      - kind: unit
        ref: "python3 -m unittest scripts.tests.test_check_pr_templates -v (RealTreeTests.test_real_tree_passes, test_each_template_carries_exactly_one_marker_pair, test_required_dod_items_present_per_type)"
        status: pass
    human_judgment: false
  - id: D2
    description: "No default PR template exists at any fallback path, so the template chooser always appears"
    requirement: FOUND-05
    verification:
      - kind: unit
        ref: "scripts/tests/test_check_pr_templates.py#FixtureTests.test_stray_default_template_exits_1"
        status: pass
      - kind: integration
        ref: "python3 scripts/check_pr_templates.py — PASS default-template"
        status: pass
    human_judgment: false
  - id: D3
    description: "Header drift, an empty DoD section, a broken marker pair, and a missing template all fail closed with exit 1 or 2"
    requirement: FOUND-05
    verification:
      - kind: unit
        ref: "scripts/tests/test_check_pr_templates.py#FixtureTests (5 tests)"
        status: pass
    human_judgment: false
  - id: D4
    description: "No required checklist row demands AI-assistance disclosure"
    requirement: FOUND-05
    verification:
      - kind: unit
        ref: "scripts/tests/test_check_pr_templates.py#RealTreeTests.test_no_required_row_demands_ai_disclosure"
        status: pass
    human_judgment: false
  - id: D5
    description: "The checker is read-only and idempotent on the real tree"
    requirement: FOUND-05
    verification:
      - kind: unit
        ref: "scripts/tests/test_check_pr_templates.py#RealTreeTests.test_second_run_is_identical_and_read_only"
        status: pass
    human_judgment: false

duration: ~2min
completed: 2026-10-23
status: complete
---

# Phase 1 Plan 05: PR Template Contract Summary

**Three type-specific PR templates share one byte-identical marker-delimited header, and `scripts/check_pr_templates.py` turns header drift, empty DoD sections, broken markers, and a chooser-suppressing default template into local test failures.**

## Performance

- **Duration:** ~2 min
- **Started:** 2026-10-23T17:14:19Z
- **Completed:** 2026-10-23T17:16:16Z
- **Tasks:** 2 of 2 complete
- **Files modified:** 5 created

## Accomplishments

- Authored `homework.md`, `infra.md`, and `docs.md` under
  `.github/PULL_REQUEST_TEMPLATE/`. All three carry the D-22 shared header
  (type, phase/requirement, ADR or issue, and four verification checkboxes with
  link placeholders) between `<!-- pr-header:start -->` and `<!-- pr-header:end -->`.
  The slices are byte-identical at 350 bytes.
- Each template carries only the D-23 Definition of Done for its type:
  homework (build, native tests, report sections, provenance, index/workspace,
  simulation), infra (ADR, policy check, no secrets, docs), docs (links,
  markdownlint, no duplicated source).
- Shipped no default template at any fallback path — the chooser appears on
  every pull request.
- Implemented `scripts/check_pr_templates.py` (stdlib only) with a documented
  0/1/2 exit contract and a `--dir` seam; it is read-only and idempotent.
- Backed the contract with 10 tests: real-tree happy path, per-type DoD keywords,
  marker-pair uniqueness, the AI-disclosure prohibition, 5 negative tempdir
  fixtures, and an idempotence/read-only assertion.

## Shipped shared header (verbatim)

```markdown
<!-- pr-header:start -->
## Pull request

- **Type:** `homework` | `infra` | `docs`
- **Phase / requirement:** `<e.g. FOUND-03, Phase 1>`
- **ADR / issue:** `<docs/decisions/0003-... or #123>`

Verification (paste run links):
- [ ] `meta` checks passed — `<link>`
- [ ] build passed — `<link>`
- [ ] native tests passed — `<link>`
- [ ] `gitleaks` passed — `<link>`
<!-- pr-header:end -->
```

## Per-type Definition of Done as shipped

**homework.md**

- Build passes: `pio run` succeeds for every environment the homework touches
- Native tests pass: `python3 -m unittest discover -s scripts/tests -v`
- Report contains every required section, from objective through conclusion
- Every measurement carries a provenance label (measured, simulated, or calculated)
- Generated index and workspace are refreshed; `git status` shows no drift
- Simulation evidence is attached when the homework is simulated

**infra.md**

- Decision recorded as an ADR under `docs/decisions/`, or an explicit note that no ADR applies
- Policy check passes: `python3 scripts/check_policy.py --check`
- No new secrets: `gitleaks git` reports nothing on the branch
- Documentation updated wherever the change alters contributor behavior

**docs.md**

- Every added or changed link resolves, whether a local path or a URL
- Markdown is lint-clean: `markdownlint-cli2`
- No source material is duplicated; content links to its single canonical location

No template requires AI-assistance disclosure; the prohibition is proven by
`test_no_required_row_demands_ai_disclosure`.

## Task Commits

Each task was committed atomically:

1. **Task 1: Author the three templates with one shared header and distinct DoDs** — `eb24541` (feat)
2. **Task 2 (RED): Add failing tests for the PR template contract checker** — `aa77463` (test)
3. **Task 2 (GREEN): Implement the PR template contract checker** — `3f7fd5b` (feat)

**Plan metadata:** the SUMMARY commit that follows this file (docs).

## TDD Gate Compliance

| Gate | Commit | Evidence |
|------|--------|----------|
| RED | `aa77463` | `python3 -m unittest scripts.tests.test_check_pr_templates -v` → exit 1, `FAILED (failures=8)`; every target test failed on its planned assertion because `scripts/check_pr_templates.py` did not exist (`can't open file .../check_pr_templates.py`), not on a test or fixture fault |
| GREEN | `3f7fd5b` | Same command → exit 0, `Ran 10 tests ... OK` |
| REFACTOR | not needed | No obvious duplication; `ruff check` clean after the GREEN-phase lint fixes |

Semantic assessment of RED: the two tests that passed during RED
(`test_each_template_carries_exactly_one_marker_pair` and
`test_required_dod_items_present_per_type`) assert properties of the Task 1
templates, not of the missing checker; the 8 failures were all subprocess
assertions against the absent script. This is valid RED for the checker feature.

## Files Created/Modified

- `.github/PULL_REQUEST_TEMPLATE/homework.md` — homework contract: shared header + homework DoD
- `.github/PULL_REQUEST_TEMPLATE/infra.md` — infra contract: shared header + infra DoD
- `.github/PULL_REQUEST_TEMPLATE/docs.md` — docs contract: shared header + docs DoD
- `scripts/check_pr_templates.py` — read-only marker-slice checker, exit 0/1/2, `--dir` seam
- `scripts/tests/test_check_pr_templates.py` — 10 tests covering the real tree and five negative fixtures

## Decisions Made

- The checker reports a malformed marker pair as **two** failures (markers and
  header). Skipping the header comparison would have hidden a second broken
  invariant; the missing-end-marker test asserts the marker message, and the
  contract still exits 1.
- The header comparison is byte-level, using `bytes.find`, so no decoding or
  newline normalization can mask drift.
- The DoD check requires rows, not specific wording, so template edits that keep
  the checklist shape do not require touching the checker. The per-type content
  itself is pinned by `test_required_dod_items_present_per_type`.
- Default-template detection mirrors the plan's fallback list and adds
  `DEFAULT.md` for casing parity with the other paths.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Ruff rejected both new Python files**
- **Found during:** Task 2 (GREEN phase)
- **Issue:** `ruff check` flagged `EXE001` (shebang without executable bit) on
  `scripts/check_pr_templates.py` and `PLW1510` (implicit `check=` on
  `subprocess.run`) in the test helper. Both would fail the project's Python
  lint standard.
- **Fix:** `chmod +x scripts/check_pr_templates.py`; added explicit `check=False`
  to the subprocess helper.
- **Files modified:** `scripts/check_pr_templates.py` (mode 100755),
  `scripts/tests/test_check_pr_templates.py`
- **Verification:** `ruff check scripts/check_pr_templates.py
  scripts/tests/test_check_pr_templates.py` → no issues; suite still 10/10.
- **Committed in:** `3f7fd5b` (GREEN commit)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** lint compliance only; no behavioral or scope change.

## Issues Encountered

- The worktree inherits a `pre-commit` hook from the shared `.git`, but
  `.pre-commit-config.yaml` does not exist yet (plan 01-03 adds it). Every commit
  used `PRE_COMMIT_ALLOW_NO_CONFIG=1`; hooks were not skipped with `--no-verify`.
- Bash-tool git invocations are intercepted by the `rtk` wrapper, which the
  worktree-isolation guard cannot verify. `/usr/bin/git` was used throughout.
- The harness guard also rejected compound shell loops mentioning `.github/...`;
  verification was split into single-purpose commands instead.
- Generated `__pycache__/` directories were removed after test runs rather than
  ignored, because `.gitignore` belongs to plan 01-02.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- The contract is Phase-8-CI-ready: wiring is a single
  `python3 scripts/check_pr_templates.py` step, no code changes needed.
- Future template edits must keep the shared header slice byte-identical; the
  suite fails locally and will fail CI once wired.
- No default template may be added later; the checker and its fixture test both
  guard that path.

## Self-Check: PASSED

- All five files exist on disk.
- Commits `eb24541`, `aa77463`, `3f7fd5b` are ancestors of HEAD.
- `python3 -m unittest scripts.tests.test_check_pr_templates -v` — 10 tests, OK.
- `python3 -m unittest discover -s scripts/tests -v` — 20 tests, OK.
- `python3 scripts/check_pr_templates.py` — exit 0, every line PASS.
- `ruff check` on both new Python files — no issues.

---
*Phase: 01-repository-foundation-and-policy-gate*
*Completed: 2026-10-23*

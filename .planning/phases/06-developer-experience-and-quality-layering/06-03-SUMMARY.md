---
phase: 06-developer-experience-and-quality-layering
plan: 03
subsystem: developer-tooling
tags: [ruff, yamllint, markdownlint, pre-commit, lint-policy]

# Dependency graph
requires:
  - phase: 06-developer-experience-and-quality-layering
    provides: the check-only clang-format hook and `default_stages: [pre-commit]` (06-01)
  - phase: 05-generated-views-and-documentation-site
    provides: the generated-view drift gate and the check-only hook pattern (05/D-21)
provides:
  - "pyproject.toml as the single ruff policy (D-13)"
  - ".yamllint.yaml as the authored-YAML policy with truthy key checking disabled (D-14)"
  - ".markdownlint-cli2.jsonc as the authored-Markdown policy (D-11, D-12)"
  - "check-only ruff-check, yamllint, and markdownlint-cli2 hooks with explicit scopes"
  - "WorkflowTriggerKeyTests, the durable guard that every workflow keeps a text `on:` key"
affects: [06-04, phase-08-ci]

actuals:
  tokens: 5153
  tasks: 3
  commits: 3
  plan_head_before: 065477d72cfeea61b7cf9c3208e7770fcb467b81
  plan_head_after: 48cc3ee7f6e958aeb5d0637c293d2eefbd9f337d

tech-stack:
  added: [ruff 0.17.2, yamllint 1.38.0, markdownlint-cli2 0.24.0]
  patterns:
    - "One committed policy per tool, delivered by a pinned pre-commit repository and never by a system package"
    - "Truthiness key checking disabled rather than normalising a GitHub Actions trigger key"
    - "Generated pages and generated YAML stay outside the lint surface; gen_views.py --check owns their shape"

key-files:
  created:
    - pyproject.toml
    - .yamllint.yaml
    - .markdownlint-cli2.jsonc
  modified:
    - .pre-commit-config.yaml
    - scripts/affected.py
    - scripts/check_architecture.py
    - scripts/metadata/contract.py
    - scripts/tests/test_homework_metadata.py
    - scripts/tests/test_ci_workflows.py
    - homeworks/1_3-police-flasher/merge_firmware.py
    - homeworks/1_3-police-flasher/report.md
    - .github/workflows/security.yml
    - .github/pull_request_template.md
    - docs/decisions/0006-public-commit-identity.md
    - .gitignore

key-decisions:
  - "ruff, yamllint, and markdownlint each get exactly one committed policy and one pinned check-only hook; no fix flag exists anywhere."
  - "yamllint disables truthy KEY checking instead of rewriting the four GitHub Actions `on:` keys, which would break the workflow schema."
  - "markdownlint sets MD024 `siblings_only` so a title repeated by a deeper heading stays; no ADR body or heading is rewritten for it."
  - "Generated pages, generated mkdocs.yml, .planning/, .claude/, and the vendor tree stay out of scope, and every exclusion is named explicitly."
  - "The degenerate uv.lock that the ruff-only pyproject makes uv write is ignored as generated output, not committed as a dependency contract."

patterns-established:
  - "A lint policy clears a backlog by making the policy correct where the finding is a policy artefact and by fixing the file where the finding is a real defect."
  - "A linter that would touch CI reaches a workflow only as a lint path; a workflow edit is limited to the defect and is guarded by a shape test."

requirements-completed: [TOOL-03]

coverage:
  - id: D1
    description: "One ruff policy in the root pyproject.toml governs every Python file through a pinned, check-only ruff-check hook"
    requirement: TOOL-03
    verification:
      - kind: integration
        ref: "pre-commit run ruff-check --all-files"
        status: pass
      - kind: unit
        ref: "python3 -m unittest discover -s scripts/tests (288 tests)"
        status: pass
    human_judgment: false
  - id: D2
    description: "One yamllint policy covers authored YAML; the four workflow trigger keys stay textual and metadata validation is unaffected"
    requirement: TOOL-03
    verification:
      - kind: integration
        ref: "pre-commit run yamllint --all-files"
        status: pass
      - kind: unit
        ref: "scripts/tests/test_ci_workflows.py#WorkflowTriggerKeyTests"
        status: pass
      - kind: integration
        ref: "UV_CACHE_DIR=/tmp/uv-cache uv run scripts/check_metadata.py"
        status: pass
    human_judgment: false
  - id: D3
    description: "One markdownlint policy covers authored Markdown; generated pages stay generator-owned and the drift gate is green"
    requirement: TOOL-03
    verification:
      - kind: integration
        ref: "pre-commit run markdownlint-cli2 --all-files"
        status: pass
      - kind: integration
        ref: "UV_CACHE_DIR=/tmp/uv-cache uv run scripts/gen_views.py --all --check"
        status: pass
    human_judgment: false
  - id: D4
    description: "The full local gate is green after the three layers are added"
    requirement: TOOL-03
    verification:
      - kind: integration
        ref: "pre-commit run --all-files (13 hooks)"
        status: pass
    human_judgment: false

duration: 6min
completed: 2026-10-26
status: complete
---

# Phase 6 Plan 03: Fast Lint Layers Summary

**Ruff, yamllint, and markdownlint landed as pinned check-only pre-commit hooks with one committed policy each, and the measured backlog was cleared by policy plus real fixes**

## Performance

- **Duration:** 6 min
- **Started:** 2026-10-26T10:59:00Z
- **Completed:** 2026-10-26T11:05:13Z
- **Tasks:** 3
- **Files modified:** 12 (3 created, 12 touched)

## Accomplishments

- `pyproject.toml` carries `[tool.ruff]` only — `line-length = 100`,
  `target-version = "py313"`, `select = ["E", "F", "I", "UP", "B"]` — plus narrow
  per-file `F821` ignores for the two SCons injection sites. It has no `[project]`
  table, so the repository is not a uv project.
- The `ruff-check` hook is pinned at `ruff-pre-commit` v0.17.2 and carries no fix
  argument; the whole Python tree passes it.
- `.yamllint.yaml` sets `line-length: {max: 120}`, `document-start: disable`, and
  `truthy: {allowed-values: ['true', 'false'], check-keys: false}`. The four
  GitHub Actions trigger keys stay text, and `WorkflowTriggerKeyTests` guards them.
- `.markdownlint-cli2.jsonc` disables `MD013` and `MD060` and narrows `MD024` to
  same-level duplicates; the ADR and README heading structure is untouched.
- The markdown backlog was fixed rather than silenced: six bare reference URLs
  became angle-bracket links, the pull request template gained a top-level
  heading and a blank line before its list, and one ADR fence gained a language.
- `pre-commit run --all-files` (13 hooks), the 288-test stdlib suite, the metadata
  checker, and the generated-view drift check are all green.

## Task Commits

Each task was committed atomically:

1. **Task 1: ruff policy, hook, and a clean Python tree end to end** — `7020ff5` (feat)
2. **Task 2: yamllint policy, scoped hook, and workflow trigger-key guard** — `b3b8d92` (feat)
3. **Task 3: markdownlint policy, scoped hook, and a clean authored-Markdown tree** — `48cc3ee` (feat)

**Plan metadata:** committed separately (docs: complete plan summary).

## Files Created/Modified

- `pyproject.toml` — the single ruff policy; tool config only.
- `.yamllint.yaml` — the authored-YAML policy, including the `check-keys: false` rule.
- `.markdownlint-cli2.jsonc` — the authored-Markdown policy.
- `.pre-commit-config.yaml` — the three pinned hooks; two existing `files:` regexes
  were rewrapped so the file passes its own yamllint policy.
- `scripts/affected.py` — the fanout table in the module docstring became a
  wrapped bullet list; every path and effect is preserved.
- `scripts/check_architecture.py` — `zip(entries, matched, strict=True)`.
- `scripts/metadata/contract.py` — `__all__` names the six documented re-exports.
- `scripts/tests/test_homework_metadata.py` — the unused `sys` import is gone.
- `scripts/tests/test_ci_workflows.py` — `WorkflowTriggerKeyTests`, three stdlib tests.
- `homeworks/1_3-police-flasher/merge_firmware.py` — the `%s` quote helper is an f-string.
- `homeworks/1_3-police-flasher/report.md` — six reference URLs are angle-bracket links.
- `.github/pull_request_template.md` — `# Pull request` title and a blank line before a list.
- `docs/decisions/0006-public-commit-identity.md` — the identity fence is labelled `text`.
- `.gitignore` — `uv.lock` is ignored as generated output.

## Decisions Made

- The lint layers are local only. D-24 keeps CI wiring, the matrix, and PR-time checks
  in Phase 8; `.github/workflows/` enters the yamllint scope only as a lint path.
- `truthy.check-keys: false` is the policy-level fix for the four `on:` keys. Normalising
  them to `true`/`false` would be unparseable by the workflow schema.
- `MD024: {siblings_only: true}` permits the deliberate title-plus-deeper-heading shape
  while still failing a genuine duplicate at the same level.
- Check-only everywhere: `ruff-check` (never `ruff-format`), and no `--fix` argument on
  yamllint or markdownlint.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] The affected.py E501 sites are Markdown table rows, which cannot be wrapped**
- **Found during:** Task 1
- **Issue:** The plan asked to rewrap three over-100-column lines at 100 columns, but all
  three were rows of the fanout table in the module docstring. Splitting a table row breaks
  the table, so a literal rewrap was impossible.
- **Fix:** The table became a wrapped bullet list of `<changed path> -> <effect>` entries.
  Every path family and its effect is preserved, and every line is under 100 columns.
- **Files modified:** `scripts/affected.py`
- **Verification:** `pre-commit run ruff-check --all-files` exits 0; the 288-test suite is green.
- **Committed in:** `7020ff5`

**2. [Rule 3 - Blocking] Two existing hook regexes exceeded the new 120-column YAML policy**
- **Found during:** Task 2
- **Issue:** `.pre-commit-config.yaml` is inside D-14's own scope, and the existing
  `check-metadata` and `gen-views-check` `files:` regexes were 134 and 206 columns.
- **Fix:** `check-metadata`'s alternation was regrouped around `scripts/` with identical
  semantics; `gen-views-check` became a folded scalar prefixed with `(?x)`, so YAML's
  inserted fold spaces are ignored by the regex engine. Neither behavior changed.
- **Files modified:** `.pre-commit-config.yaml`
- **Verification:** both hooks still run and pass under `--all-files` and on a targeted
  file each (`scripts/metadata/contract.py`, `docs/index.md`).
- **Committed in:** `b3b8d92`

**3. [Rule 1 - Bug] A genuine line-length finding in security.yml contradicts the "no workflow touched" criterion**
- **Found during:** Task 2
- **Issue:** The plan requires `pre-commit run yamllint --all-files` to pass at
  `max: 120`, and separately asserts that `git diff HEAD --name-only -- .github/workflows/`
  prints nothing. `.github/workflows/security.yml:32` is a 137-column curl invocation, so
  the two requirements cannot both hold. The task's own action text resolves it: "if a
  further finding appears, fix the file; do not widen a rule."
- **Fix:** The gitleaks release URL is assembled in three shell variables and passed as one
  quoted argument. The downloaded tarball path is byte-identical, the checksum check is
  unchanged, and the `on:` trigger key is untouched.
- **Files modified:** `.github/workflows/security.yml`, `scripts/tests/test_ci_workflows.py`
- **Verification:** `pre-commit run yamllint --all-files` exits 0; all four workflows still
  declare a top-level `on:` key and `WorkflowTriggerKeyTests` asserts it.
- **Committed in:** `b3b8d92`

**4. [Rule 3 - Blocking] The ruff-only pyproject makes uv write a degenerate uv.lock**
- **Found during:** Task 2, after Task 1's pyproject landed
- **Issue:** uv treats a directory holding any `pyproject.toml` as a project. Every test
  that shells out to `uv run` therefore wrote a three-line `uv.lock` at the repository root,
  leaving generated output untracked. RESEARCH Pitfall 9 measured `uv run` exit 0 but did not
  check for this side effect.
- **Fix:** `.gitignore` now ignores `uv.lock` with a comment explaining that the file is a
  degenerate artifact, not a dependency contract.
- **Files modified:** `.gitignore`
- **Verification:** `git status --short` shows no `uv.lock` after the full suite ran twice.
- **Committed in:** `b3b8d92`

**5. [Rule 1 - Bug] A genuine MD040 finding in an ADR contradicts the "no docs/decisions file modified" criterion**
- **Found during:** Task 3
- **Issue:** The `MD024` findings are ADR heading repetition and are handled by policy, but
  a separate real finding remained: `docs/decisions/0006-public-commit-identity.md:17` is a
  fence with no language. Task 3's action says to name a fenced block's language, while its
  acceptance criterion says no `docs/decisions/` file is modified.
- **Fix:** The fence info string gained `text`. No prose, heading, or decision text changed.
- **Files modified:** `docs/decisions/0006-public-commit-identity.md`
- **Verification:** `pre-commit run markdownlint-cli2 --all-files` exits 0; ADR 0001 (the
  `MD024` site) is unchanged, and `git diff HEAD --name-only` for it prints nothing.
- **Committed in:** `48cc3ee`

---

**Total deviations:** 5 auto-fixed (3 Rule 1 bugs, 2 Rule 3 blockers)
**Impact on plan:** Four deviations resolve plan-internal contradictions between a policy and
an acceptance criterion; none widens an exclusion or disables a rule, and one (the `uv.lock`
ignore) is a side effect of the mandated ruff configuration. No shipped contract changed.

## Issues Encountered

- The `yamllint` hook initially reported three findings the policy had not cleared: two
  existing hook regexes and one workflow shell line. All were real, and all were fixed
  rather than excluded.
- The measured backlog of 11 markdownlint findings became 9 after `MD024: siblings_only`
  cleared the two heading findings, exactly as the policy predicted.
- The executor harness rejected the plan's literal `UV_CACHE_DIR="${TMPDIR:-/tmp}/uv-cache"`
  form (runtime-computed value); the same command ran with the literal `/tmp/uv-cache`.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Success criterion 4's pre-commit half is met locally: format, markdownlint, yamllint, ruff,
  and gitleaks all run and pass.
- Plan 06-04 (clang-tidy and the pre-push stage) builds on the same hook file and the same
  `default_stages` contract; it must add its hooks after the existing ones.
- TOOL-03 is declared by both 06-03 and 06-04, so it is left unmarked in `REQUIREMENTS.md`
  until 06-04 produces its summary (the shared-ID gate).
- No blockers.

---
*Phase: 06-developer-experience-and-quality-layering*
*Completed: 2026-10-26*

## Self-Check: PASSED

- `pyproject.toml`, `.yamllint.yaml`, `.markdownlint-cli2.jsonc`, and this SUMMARY exist on disk.
- `7020ff5` (Task 1), `b3b8d92` (Task 2), and `48cc3ee` (Task 3) are ancestors of `HEAD`.
- `pre-commit run --all-files`, `python3 -m unittest discover -s scripts/tests` (288 tests),
  `uv run scripts/check_metadata.py`, and `uv run scripts/gen_views.py --all --check` all exited 0.

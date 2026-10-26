# Phase 8: Fast CI - Context

**Gathered:** 2026-10-26
**Status:** Ready for planning

<domain>
## Phase Boundary

A pull-request pipeline that is fast, changed-only, and gated by exactly one required check;
simulation is optional and never blocks forks; a nightly run covers the full build and native
test matrix without simulation. The phase delivers:

- `.github/workflows/ci.yml` with `meta`, `changes`, `build`, `simulate`, and `gate` jobs.
- `.github/workflows/nightly.yml` running every project's build and native tests, no simulation.
- Retirement of `homework.yml` and `generated-views.yml`; their checks move into `meta`.
  `docs.yml` remains a `main`-only deploy workflow and is not a PR gate.
- Changed-only matrix plumbing over the existing `scripts/affected.py` JSON contract.
- An opt-in `simulate` job with a same-repo guard, step-level token check, explicit timeout,
  and artifact upload.
- PR-time `docs-build` and `python-tests` jobs, closing the Phase 5 WR-13 gap.
- A PR-title check using the Conventional Commits vocabulary.
- Updated `scripts/tests/test_ci_workflows.py` and `AGENTS.md`.
- One human checkpoint: the GitHub ruleset gains `gate` as its required status check after
  the first green `ci.yml` run.

**Requirements covered:** TOOL-05, TOOL-06, SIM-04.

**Explicitly not this phase:** the report and evidence checker (Phase 10), agent skills
(Phase 9), pilot finalization and the `hw/<id>` tag (Phase 11), any schema change, new
simulator measurement (Phase 7 closed it), ESP-IDF compile-database fallback, nightly
simulation, weekly full simulation, and programmatic ruleset changes.

</domain>

<decisions>
## Implementation Decisions

### Workflow topology and the single gate

- **D-1:** One PR-time `ci.yml` owns `meta`, `changes`, `build`, `simulate`, and `gate`.
  `homework.yml` and `generated-views.yml` retire; their commands move into `meta`.
  `docs.yml` stays `main`-only because Pages deployment needs the `github-pages`
  environment and OIDC, which a PR cannot provide. `security.yml` retires because its
  full-history gitleaks scan moves into `meta`.
  — **Reversibility:** costly — the ruleset's required check name, `AGENTS.md`, the
  workflow text tests, and every open PR's status surface reference this topology.
- **D-2:** `gate` is a fan-in job with `needs:` naming **every** PR job and
  `if: ${{ !cancelled() }}`. It fails when any dependency reports `failure`, `cancelled`,
  or `timed_out`; only `gate` is required in the ruleset. `always()` is not used because it
  also runs after cancellation. `gate` is a stable public contract:
  `scripts/tests/test_ci_workflows.py` asserts the literal job id, and a rename must update
  the ruleset in the same pull request.
  — **Reversibility:** one-way — GitHub matches required checks by literal name, and a
  renamed job leaves the required check permanently `Pending`, blocking every merge until
  the ruleset is edited by hand.

### Changed-only plumbing

- **D-3:** `changes` checks out with `fetch-depth: 0` and runs
  `uv run scripts/affected.py --base origin/<base_ref>`. On `workflow_dispatch` it falls
  back to `origin/main`. No third-party path filter is introduced: `affected.py` already
  owns the tested fanout and fail-safe, and a second glob dialect would disagree with it.
  — **Reversibility:** costly — the diff base is the input to every build decision, and a
  change alters what CI proves on every pull request.
- **D-4:** An empty matrix is skipped with a job-level
  `if: toJson(fromJson(needs.changes.outputs.matrix)) != '[]'`. The job-level condition is
  evaluated before the matrix is materialised, so it avoids GitHub's
  "Matrix vector does not contain any values" failure. `gate` treats an intentional skip as
  success, but fails when `changes` or `meta` failed. No synthetic noop entry is added to
  the `affected.py` output and no separate noop job exists.
- **D-5:** The fail-safe widening from 05/D-24 is preserved: an unrecognised shared path
  builds every project. It is never narrowed for speed; a slow correct run beats a fast
  unproven one.

### Build and test execution

- **D-6:** Per matrix entry, `env == "native"` runs
  `pio test -d <project> -e native`; every other environment runs
  `pio run -d <project> -e <env>`. Both `platformio.ini` files already document this
  contract ("reached with `pio test -e native`, never with `pio run -e native`"), and the
  top-level `tests/` project needs no special case. The 05/D-22 output contract is not
  changed.
  — **Reversibility:** costly — the command rule is the definition of what a green build
  means for every matrix entry.
- **D-7:** The build matrix uses `fail-fast: false` and `max-parallel: 4`. One project's
  failure does not cancel the others, and a `lib/**` fanout cannot occupy every runner.
  — **Reversibility:** reversible — both knobs are local to `ci.yml`.

### Simulation policy

- **D-8:** Simulation runs only when a maintainer applies the `simulate` label to the pull
  request **and** `affected.py` returns a non-empty `simulate` array. Fork PRs cannot apply
  the label, and the roadmap describes simulation as optional.
  — **Reversibility:** reversible — a later decision can auto-run for changed projects.
- **D-9:** Belt-and-braces fork guard: the job-level `if` requires the head repository to
  equal the base repository (`github.event.pull_request.head.repo.full_name ==
  github.repository`) and the label; the token is checked at step level, because a
  job-level `if` that references `secrets.*` can break YAML evaluation. A skipped simulation
  is success for `gate`; simulation is never a required check for fork pull requests.
- **D-10:** The simulation job uploads `serial.log`, the full scenario stdout, and a
  duration/quota JSON, with 7-day retention. The evidence must allow reproducing the run and
  confirming quota without re-running it.
- **D-11:** `wokwi-cli lint` stays in `meta` for every pull request: it needs no token and
  consumes no simulation quota.
- **D-12:** Simulation never flips `simulation.status` to `verified` by itself; the metadata
  status remains governed by the Phase 7 evidence rule — only an executed, evidenced run
  with the `scenario passed` outcome justifies it.

### Meta job surface

- **D-13:** The lint gate is one step,
  `pre-commit run --all-files --show-diff-on-failure`, with `pre-commit install-hooks` as a
  separate preceding step. `~/.cache/pre-commit` is cached on
  `hashFiles('.pre-commit-config.yaml')` with no `restore-keys`, so a pin bump rebuilds and
  a near-miss never runs linters outside the reviewed pin. clang-tidy's `pre-push` stage is
  not part of this command by construction.
- **D-14:** The full-history gitleaks scan moves from `security.yml` into `meta` as
  `gitleaks git --redact --verbose --log-opts="--all"`, keeping the pinned 8.30.1 binary and
  its checksum.
- **D-15:** `docs-build` (`mkdocs build --strict` plus the existing
  `scripts/ci/check_lfs_pointers.sh site` guard) and `python-tests`
  (`python -m unittest discover scripts/tests`) run as parallel jobs and feed the same
  `gate`. This closes WR-13 without slowing the lint feedback.
- **D-16:** The PR-title check is a `meta` step validating
  `^(feat|fix|test|refactor|perf|docs|style|chore)\([a-z0-9._-]+\): .+$` against
  `github.event.pull_request.title`; it is skipped on `workflow_dispatch`.
- **D-17:** clang-tidy in CI analyses host translation units only (`lib/common`, `lib/port`,
  `lib/host`) with a freshly generated compile database. Native test translation units stay
  the recorded ADR-0013 gap; closing it needs the `unity_config.h` fix and is not part of
  this phase.

### Caching and timeouts

- **D-18:** Build jobs cache `~/.platformio/packages`, `~/.platformio/.cache`, and
  `~/.cache/pip`, keyed on `runner.os` plus `hashFiles('platformio.shared.ini',
  'platformio.ini')`, with no broad `restore-keys`. The pins live in
  `platformio.shared.ini`, so hashing only a project's `platformio.ini` would not invalidate
  the toolchain on an espressif32 bump.
  — **Reversibility:** reversible — the cache is a performance optimisation, not a contract.
- **D-19:** Initial timeouts are generous: `meta` 15, `docs-build` 15, `python-tests` 10,
  each `build` job 30, `simulate` 10, `gate` 5, `nightly` 90 minutes. Cold and warm
  durations are measured over the first runs and the timeouts are tightened in a follow-up
  commit (F-15), not guessed downward up front.

### Human checkpoint and repository rules

- **D-20:** After the first green `ci.yml` run on a pull request, the repository owner adds
  `gate` as the required status check in the GitHub ruleset (0 approvals) through the UI.
  This is recorded as a human checkpoint in phase verification. A required check cannot be
  selected before it has passed at least once within the last 7 days, and rulesets remain a
  GitHub-UI artifact per `AGENTS.md`.
- **D-21:** `AGENTS.md` is updated: the quick-start gains the CI commands, the PR/tags
  section names the `gate` contract, and the quality-tooling section records that CI now
  runs the hook surface. The claim that `generated-views.yml` is a drift gate is replaced by
  the `meta` job.

### Claude's Discretion

- Every job id except `gate`, the step order inside `meta`, and the exact action SHAs
  (existing pinned SHAs are reused where the action is unchanged).
- The wording of `gate`'s failure diagnostic and how it prints `toJSON(needs.*.result)`.
- The exact shape of the duration/quota JSON artifact.
- The cron minute inside the ~03:00 UTC window for `nightly.yml`.
- Whether `docs-build` invokes `check_lfs_pointers.sh` exactly as `docs.yml` does or through
  a shared step.

### Folded Todos

- **Standardize pull request titles across homeworks**
  (`.planning/todos/pending/2026-10-25-standardize-pull-request-titles-across-homeworks.md`).
  Original problem: PR titles are free-form, but squash-only merging publishes the PR title
  as the commit subject, where history cannot be rewritten. It fits this phase because the
  todo itself asks for a machine check in a pull-request job, and `meta` is now the one
  PR-time job that owns repository policy checks.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and requirements
- `.planning/ROADMAP.md` §Phase 8: Fast CI — goal, success criteria 1–4, and the requirement
  mapping (TOOL-05, TOOL-06, SIM-04)
- `.planning/REQUIREMENTS.md` §Tooling and Quality — TOOL-05, TOOL-06; §Simulation and
  Diagrams — SIM-04; and the Traceability table rows for Phase 8
- `.planning/PROJECT.md` §Constraints and §Key Decisions — the pinned toolchain, the
  quality bar, and the "Three-layer checks" row whose CI layer is this phase
- `.planning/STATE.md` §Blockers/Concerns — the Phase 5 WR-13 carry-forward and the
  Phase 7 evidence that unblocks CI simulation

### Prior decisions that remain locked
- `.planning/phases/05-generated-views-and-documentation-site/05-CONTEXT.md` — D-21
  (check-only drift gate), D-22 (`affected.py` JSON shape), D-24 (fanout and fail-safe), and
  D-26 (the matrix is Phase 8, not Phase 5)
- `.planning/phases/06-developer-experience-and-quality-layering/06-CONTEXT.md` — D-08/D-08a
  (clang-tidy scope and the native-test-TU gap handed to Phase 8), D-24 (no CI edits in
  Phase 6)
- `.planning/phases/07-simulation-spike/07-CONTEXT.md` — D-11 (the calculated CI cost basis),
  D-14 (the simulation gate belongs to Phase 8)
- `.planning/phases/04.2-tracer-homework-1-3/04.2-FRICTION-LOG.md` — F-14 (matrix and single
  gate), F-15 (cache `~/.platformio/packages`, measure cold/warm, tighten the timeout), F-16
  (metadata and architecture checks in CI), F-17 (pin revalidation), and §Top automation
  candidates (the Phase 8 rows)

### Repository contracts and existing artifacts
- `scripts/affected.py` — the matrix producer; its `{build, simulate}` JSON and exit codes
  are the CI input contract
- `scripts/tests/test_ci_workflows.py` — asserts exactly four workflows today; must be
  updated for `ci.yml` and `nightly.yml` and gain the literal `gate` assertion
- `.github/workflows/homework.yml` — the single-project job being replaced
- `.github/workflows/generated-views.yml` — the drift job folded into `meta`
- `.github/workflows/security.yml` — the pinned gitleaks binary and checksum that move into
  `meta`
- `.github/workflows/docs.yml` — the `main`-only build/deploy that stays, and the LFS guard
  reused by `docs-build`
- `.pre-commit-config.yaml` — the hook surface, stage semantics, and pinned revisions that
  `meta` runs
- `scripts/clang-tidy-db` and `scripts/clang-tidy-hook` — the local guard and hook the CI
  clang-tidy job mirrors
- `scripts/ci/check_lfs_pointers.sh` — the LFS pointer guard
- `platformio.shared.ini` — the platform pins that key the toolchain cache
- `homeworks/1_3-police-flasher/platformio.ini` and `tests/platformio.ini` — the documented
  `pio test -e native` contract and `-Werror` flags
- `pyproject.toml` — the ruff policy used by the hook
- `requirements-docs.txt` — the MkDocs pins installed by `docs-build`
- `AGENTS.md` — the rulebook sections this phase updates (quick-start, PR/tags, quality)
- `.github/pull_request_template.md` — the Definition of Done that the title check complements
- `.planning/todos/pending/2026-10-25-standardize-pull-request-titles-across-homeworks.md` —
  the folded todo

### External references
- `https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-jobs`
  — `needs` semantics and conditional aggregation
- `https://jakewharton.com/fan-in-to-a-single-required-github-action/` — the fan-in gate
  pattern and why a skipped aggregator reports success
- `https://github.com/dorny/paths-filter/issues/66` — the empty-matrix job-level `if` pattern
- `https://docs.github.com/en/actions/reference/workflows-and-actions/dependency-caching` —
  the 10 GB cache cap, eviction, and key rules
- `https://docs.platformio.org/en/latest/integration/ci/github-actions.html` — the official
  cache paths and `pio run`/`pio test` split
- `https://docs.wokwi.com/wokwi-ci/github-actions` and
  `https://docs.wokwi.com/wokwi-ci/getting-started` — the token, quota, and action shape
- `https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/troubleshooting-rules`
  — required-check name matching and the 7-day selectability rule
- `https://github.com/pre-commit/action` and
  `https://www.git-automation.com/git-automation-cicd-hook-engineering/pre-commit-framework-for-polyglot-repos/caching-pre-commit-environments-in-ci/`
  — `--all-files` as the single source of truth and the cache-key rule

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `scripts/affected.py` — emits the exact `{build, simulate}` payload CI needs, with tested
  fanout, explicit `NO_BUILD_IMPACT`, and fail-safe widening; no code change is required.
- `scripts/ci/check_lfs_pointers.sh` — already runs in `docs.yml`; reuse it in `docs-build`.
- `.github/workflows/*.yml` — carry the pinned action SHAs, `contents: read`, and
  concurrency groups that `ci.yml` and `nightly.yml` should copy.
- `scripts/clang-tidy-db` and `scripts/clang-tidy-hook` — the local guard/hook pair whose
  commands and failure semantics the CI clang-tidy job mirrors.
- `scripts/tests/test_ci_workflows.py` — the existing text-contract test; extend it rather
  than starting a new suite.
- `requirements-docs.txt` and `pyproject.toml` — pinned inputs for `docs-build` and the lint
  hook.

### Established Patterns
- Workflows pin actions by commit SHA, use `permissions: contents: read`, and declare a
  `concurrency` group with `cancel-in-progress: true`.
- `scripts/tests/` is stdlib-only and reads workflows as plain text; it asserts textual
  contracts (`on:`, command strings, job names) and behavioural guards separately.
- Deterministic scripts print `PATH: STATUS — reason`, support `--json`, and exit 0/1/2;
  `affected.py` writes payload only to stdout and diagnostics only to stderr.
- Hooks and checks are check-only and never rewrite or stage (05/D-21).
- `AGENTS.md` rules carry a severity and an enforcement point; CI claims in it must match
  the workflows that actually exist.

### Integration Points
- `AGENTS.md` — quick-start table, "Pull requests and tags", "Quality tooling", and the
  statement that `generated-views.yml` runs the drift check.
- `scripts/tests/test_ci_workflows.py` — the workflow count, trigger-key tests, and the new
  literal `gate` assertion.
- `docs.yml` — unchanged trigger and deploy path; `docs-build` repeats only its build and
  guard steps, never the deploy.
- `.github/pull_request_template.md` — may name the `gate` check in the Definition of Done.
- `.planning/STATE.md` and the phase verification — the human checkpoint for the required
  check.

</code_context>

<specifics>
## Specific Ideas

- The Wokwi account is on the free plan: about 50 simulated minutes per rolling 30 days and a
  5-minute session cap; ADR-0014 records a `calculated (upper bound)` 15 seconds per run.
  Simulation must stay opt-in and time-capped.
- The only measured CI baseline is the Phase 4.2 single-project run at 1m38s against a
  45-minute timeout; it includes no simulation and no matrix.
- Four workflows exist today and `test_ci_workflows.py` asserts exactly four; the phase
  changes both the files and the assertion.
- The top-level `tests/` project has no `homework.yaml` and contributes to `build` only; its
  `native` env takes the same `pio test` branch as a homework's native env.
- `pio test` on a target environment would attempt hardware; the `native`-only rule prevents
  that.
- GitHub's cache ceiling is 10 GB per repository with 7-day eviction; the ESP32 toolchain is
  large, so the cache key must be pin-derived and the scope bounded.
- Required status checks are matched by literal name and must have passed within the last
  7 days to appear in the ruleset picker.

</specifics>

<deferred>
## Deferred Ideas

- **clang-tidy over native test translation units** — remains the ADR-0013 gap; needs the
  `unity_config.h` fix and is not part of Fast CI.
- **Merge queue support (`merge_group`)** — no merge queue is enabled; revisit only if one
  is adopted, because a missing trigger leaves the required check pending.
- **Nightly failure notifications** — not built; the job log and the red run are the signal.
- **Weekly full simulation matrix** — out of scope; the free-tier quota cannot sustain it.
- **Programmatic ruleset changes via the GitHub API** — declined; `AGENTS.md` keeps rulesets
  in the UI, so the required check is a human checkpoint.
- **A reusable workflow to share the build job between `ci.yml` and `nightly.yml`** —
  considered and declined in favour of two explicit files.
- **ESP-IDF compile-database completeness fallback** — belongs to the first ESP-IDF
  homework, not this phase.

### Reviewed Todos (not folded)

- *Expand homework README and add a proper SVG schematic* — homework content and reader
  documentation; Phase 11.
- *Promote `merge_firmware.py` into a shared tool* — already executed in Phase 7.
- *Generate a root compile database so `lib/` has working IntelliSense* — resolved by
  Phase 06.1.
- *Trim governance ceremony (Phase 4.1)* — already completed.

</deferred>

---

*Phase: 8-Fast CI*
*Context gathered: 2026-10-26*

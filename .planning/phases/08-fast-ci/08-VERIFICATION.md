---
phase: 08-fast-ci
verified: 2026-10-26T19:20:25Z
status: passed
score: 38/39 must-haves verified
covered_files:
  [
    ".github/pull_request_template.md",
    ".github/workflows/ci.yml",
    ".github/workflows/nightly.yml",
    ".planning/phases/08-fast-ci/08-01-PLAN.md",
    ".planning/phases/08-fast-ci/08-01-SUMMARY.md",
    ".planning/phases/08-fast-ci/08-02-PLAN.md",
    ".planning/phases/08-fast-ci/08-02-SUMMARY.md",
    ".planning/phases/08-fast-ci/08-03-PLAN.md",
    ".planning/phases/08-fast-ci/08-03-SUMMARY.md",
    ".planning/phases/08-fast-ci/08-04-PLAN.md",
    ".planning/phases/08-fast-ci/08-04-SUMMARY.md",
    ".yamllint.yaml",
    "AGENTS.md",
    "docs/decisions/README.md",
    "scripts/tests/test_ci_workflows.py",
  ]
covered_digest: "v3:sha256:a9db32663a860cb439f164e960f725c98cfeb85be06b00ec4ecade3dde338499"
behavior_unverified: 1
overrides_applied: 0
behavior_unverified_items:
  - truth: "A superseded pull-request run is cancelled by the concurrency group and the newer run reports a fresh `gate`; within a run `fail-fast: false` keeps one failing matrix entry from cancelling its siblings."
    test: "Open two pull requests against the same branch in quick succession, then inspect the first run's conclusion and whether the newer run reports a fresh `gate`; separately, fail one matrix entry of a multi-entry run and confirm its siblings still finish."
    expected: "The superseded run is reported `cancelled`, the newer run produces its own `gate`, and a failing matrix entry does not cancel the other entries of the same run."
    why_human: "The workflow declares `concurrency: cancel-in-progress: true` and `fail-fast: false`, and the text contract asserts both, but the cancellation/aggregation behaviour only exists in GitHub Actions at run time; no local test executes it."
human_verification:
  - test: "After the first green `ci.yml` run on a pull request, open Settings -> Rules -> the `main` ruleset and add `gate` as the required status check (0 approvals)."
    expected: "`gate` appears in the required-checks picker and the merge box shows it as the only required check."
    why_human: "Rulesets are a GitHub-UI artifact (AGENTS.md, D-20); a check becomes selectable only after it has passed within the last 7 days, and no repository file records the live ruleset."
  - test: "Open one pull request that changes `homeworks/1_3-police-flasher` and watch the `ci.yml` run."
    expected: "`changes` emits a two-entry build matrix (target plus native), `build` runs `pio run` for the target and `pio test -e native` for native, `meta`, `python-tests` and `static-analysis` are green, and the literal `gate` reports success within its 15-minute budget."
    why_human: "The workflow is a text contract locally; only a live GitHub run proves the triggers, matrix expansion, runner images, cache restore and the fan-in result. The 15-minute `meta` budget is a flagged, unmeasured assumption (F-15)."
  - test: "Apply the `simulate` label to one same-repository pull request that changes `homeworks/1_3-police-flasher`, then open the run artifacts; then remove the label and push again."
    expected: "Applying the label alone starts a fresh run; the `simulate` job runs, the artifact name contains no slash, `serial.log`, `stdout.log` and `quota.json` are present, and the scenario reports `passed`; without the label no simulation runs and `gate` stays green; a fork pull request never reaches the job."
    why_human: "The run needs the repository secret and a maintainer-applied label and is metered against the ~50 simulated minutes per 30 days free-tier quota; SIM-04 cannot be exercised from the local tree."
  - test: "Observe one scheduled nightly run and one manual `workflow_dispatch` overlap attempt; confirm the nightly cache is restored by a later pull-request `build` job."
    expected: "The second run is queued rather than run concurrently (`cancel-in-progress: false`), every project with a `platformio.ini` plus `tests` appears in the matrix, and the pull-request build restores the default-branch cache entry."
    why_human: "Cache scoping and cold/warm durations are GitHub runner facts; only the key equality is a text contract (F-15)."
gaps: []
---

# Phase 8: Fast CI Verification Report

**Phase Goal:** Pull requests are gated by a fast, changed-only CI pipeline with one required check; simulation is optional and never blocks forks.
**Friction-log justification:** The Phase 4.2 log must contain at least one entry for CI feedback time or changed-only builds; otherwise the pipeline is not built.
**Verified:** 2026-10-26T19:20:25Z
**Status:** human_needed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| #   | Truth | Status | Evidence |
| --- | ----- | ------ | -------- |
| 1 | A PR that changes a homework runs `changes` then `build`; the matrix comes from `scripts/affected.py --base origin/$BASE`, falling back to `main` on `workflow_dispatch`. | ✓ VERIFIED | `ci.yml:170-206` (`build: ${{ fromJson(needs.changes.outputs.build) }}`), fallback `base="${BASE_REF:-main}"`; mapper run: one homework → 2 build entries |
| 2 | A `native` matrix entry runs `pio test -d $PROJECT -e $ENV_NAME`; every other entry runs `pio run`. | ✓ VERIFIED | `ci.yml:241-252`, both values quoted; `test_build_splits_native_from_target` green |
| 3 | `meta` scans the full history with the pinned gitleaks binary immediately after checkout, before `pre-commit install-hooks` and any contributor hook. | ✓ VERIFIED | `ci.yml:36-64` scan precedes `install-hooks` at `:92`; `test_meta_scans_history_before_running_hooks` and `test_meta_fetches_the_full_history` green |
| 4 | `meta` runs `pre-commit install-hooks` then `pre-commit run --all-files --show-diff-on-failure`. | ✓ VERIFIED | `ci.yml:91-100`; hook surface includes check-metadata, check-architecture, gen-views-check, ruff, yamllint, markdownlint, clang-format |
| 5 | `meta` validates the PR title against the Conventional Commits pattern, reads it only from `env:`, and is skipped on `workflow_dispatch`. | ✓ VERIFIED | `ci.yml:68-80` (`env: PR_TITLE`, `if: github.event_name == 'pull_request'`); `test_meta_validates_the_title` green |
| 6 | Applying the `simulate` label to an open PR re-runs `ci.yml`. | ✓ VERIFIED | `ci.yml:9` `types: [opened, synchronize, reopened, edited, labeled]` |
| 7 | No PR job uses `pull_request_target` or a write permission; only the guarded `simulate` job reads a secret. | ✓ VERIFIED (amended by Plan 03) | `permissions: contents: read`; grep finds no `pull_request_target` and no `: write`; `secrets.` appears only at `ci.yml:307` inside `simulate`; `test_only_simulate_receives_a_secret` green. Plan 01's "no secret at all" wording predates Plan 03's explicit fork-guarded secret design |
| 8 | One job has id `gate` and name `gate`; it depends on every PR job, runs under `!cancelled()`, and fails unless every dependency is `success` or `skipped`. | ✓ VERIFIED | `ci.yml:427-452`; `needs: [changes, meta, build, python-tests, static-analysis, simulate]`; jq selector behaviourally checked with synthetic `needs` payload |
| 9 | An empty `build` matrix skips at job level, rejecting `''` before `[]`, and `gate` counts the skip as success. | ✓ VERIFIED | `ci.yml:216-222` (job-level `if` above `strategy:`); `test_build_skips_an_empty_matrix_at_job_level` green |
| 10 | `meta` pins gitleaks 8.30.1 and lints every `homeworks/*/assets/diagram.json` with `wokwi-cli lint --offline`. | ✓ VERIFIED | `ci.yml:38-64, 100-125`; local `wokwi-cli lint --offline` exit 0 (one informational `unsupported-part` note) |
| 11 | `scripts/affected.py` sorts by `(project, env)` and prints byte-identical output for identical input. | ✓ VERIFIED | `scripts/affected.py:477-478`; two identical runs produced the same SHA-256 (`730570e8…f0072`) |
| 12 | With no affected paths, `changes` emits `[]` for both matrices and no project is built. | ✓ VERIFIED | docs-only path run returned `{"build": [], "simulate": []}` |
| 13 | One-entry and multi-entry matrices take the same job path; only `[]` skips. | ✓ VERIFIED | One job-level guard, one matrix include (`ci.yml:216-228`); single-homework run returned 1 simulate and 2 build entries |
| 14 | `04.2-FRICTION-LOG.md` carries F-15 and the Phase 8 rows under `## Top automation candidates`. | ✓ VERIFIED | F-15 at line 196; Phase 8 rows at lines 271-273 |
| 15 | `nightly.yml` runs daily and on `workflow_dispatch`; its matrix is the full project set from feeding `platformio.shared.ini` to `affected.py --paths-from`. | ✓ VERIFIED | `nightly.yml:8-12, 42-53`; widen-all run returned `1_3` (2 envs) plus `tests` |
| 16 | Nightly applies the same `pio run` / `pio test -e native` split, declares no simulation job and no Wokwi credential, proven by a text assertion. | ✓ VERIFIED | `nightly.yml:96-107`; `test_nightly_declares_no_simulation` green (comment lines dropped) |
| 17 | After the phase the workflow directory holds exactly `ci.yml` and `nightly.yml`; `homework.yml` and `security.yml` are removed. | ✓ VERIFIED | `git ls-files .github/workflows` returns exactly the two files; both retired files absent from the tree |
| 18 | The full-history secret scan runs on the default branch every night. | ✓ VERIFIED | `nightly.yml:110-145` (`fetch-depth: 0`, pinned 8.30.1, `gitleaks git --redact --verbose --log-opts="--all"`) |
| 19 | Nightly uses the same toolchain cache key as the pull-request build, so the default-branch run seeds the cache PRs restore. | ✓ VERIFIED | Identical literal in `ci.yml:232` and `nightly.yml:85`: `${{ runner.os }}-pio-${{ hashFiles('platformio.shared.ini', 'platformio.ini') }}`; runtime seeding is covered by a human item |
| 20 | An empty nightly matrix skips through the same empty-string-then-`[]` job-level guard. | ✓ VERIFIED | `nightly.yml:65` above `strategy:` |
| 21 | A manual `workflow_dispatch` and a scheduled run never overlap: the workflow declares a non-cancelling concurrency group. | ✓ VERIFIED | `nightly.yml:18-22` `group: ${{ github.workflow }}`, `cancel-in-progress: false`; `test_nightly_serialises_its_runs` green (runtime overlap is a human item) |
| 22 | `python-tests` installs `uv==0.13.5` and runs `python -m unittest discover scripts/tests`. | ✓ VERIFIED | `ci.yml:259-279`; the same command runs locally: 333 tests, `OK` |
| 23 | `static-analysis` restores the same `~/.cache/pre-commit` entry as `meta`, generates the native compile database, then runs the `pre-push` stage. | ✓ VERIFIED | `ci.yml:288-340` (two cache steps with the same key, `pio run -d tests -e native -t compiledb`, `pre-commit run --all-files --hook-stage pre-push`) |
| 24 | `gate` depends on every pull-request job: `meta`, `changes`, `build`, `python-tests`, `static-analysis`, `simulate`. | ✓ VERIFIED | `ci.yml:429`; `test_gate_needs_every_pull_request_job` derives the set from the file and passes |
| 25 | `simulate` runs only for a PR event, same-repository head, `simulate` label, successful `changes` and `meta`, and a non-empty simulate array; a fork can never reach it. | ✓ VERIFIED | `ci.yml:314-323` guard order starts with `!cancelled()` then `github.event_name == 'pull_request'`; `test_simulate_depends_on_policy_jobs` green |
| 26 | The token is tested in a step, not in the job-level `if`, and an absent token fails that step. | ✓ VERIFIED | `ci.yml:332-336` (`if: env.WOKWI_CLI_TOKEN == ''`, `exit 1`) |
| 27 | `simulate` builds the target first, installs pinned wokwi-cli 0.28.1 after digest verification, runs the scenario with a 15-second timeout and `--serial-log-file`, and uploads three artifacts with 7-day retention. | ✓ VERIFIED | `ci.yml:338-422`; `test_simulation_is_guarded_and_uploads_evidence` and `test_simulation_pins_the_cli_and_maps_exit_codes` green; live metered run is a human item |
| 28 | The uploaded artifact name is derived in shell with every character outside `[A-Za-z0-9._-]` replaced; the upload `name:` reads that value. | ✓ VERIFIED | `ci.yml:370-383` (`LC_ALL=C tr -c 'A-Za-z0-9._-' '-'`, `ARTIFACT_NAME=simulation-…`) and `name: ${{ env.ARTIFACT_NAME }}` |
| 29 | The evidence directory and log files exist before the CLI runs, `quota.json` records the serial-log byte count and CLI exit code, and a missing file is an error. | ✓ VERIFIED | `ci.yml:370-421`; exercising the extracted step with a stub CLI exiting 42 wrote `quota.json` (`exit_code: 42`, `outcome: timeout`) and retained both logs; `if-no-files-found: error` |
| 30 | A skipped simulation counts as success at `gate`, and no workflow writes `simulation.status`. | ✓ VERIFIED | `gate` allows `skipped`; grep finds no `simulation.status` in either workflow; `test_no_workflow_writes_simulation_status` green |
| 31 | A superseded PR run is cancelled and the newer run reports a fresh `gate`; `fail-fast: false` keeps one failing matrix entry from cancelling siblings. | ⚠️ PRESENT_BEHAVIOR_UNVERIFIED | `ci.yml:21-23` and `:226-227` declare both, but no test exercises GitHub's cancellation/aggregation behaviour — see Human Verification |
| 32 | `AGENTS.md` names `ci.yml` and `nightly.yml` in the layout and routing table, and no retired workflow name survives. | ✓ VERIFIED | `AGENTS.md:33-36, 267-268`; assertions confirm neither `security.yml` nor `generated-views` remains |
| 33 | `AGENTS.md` states that `gate` is the single required status check and that a rename changes the ruleset in the same PR. | ✓ VERIFIED | `AGENTS.md:154-156` |
| 34 | `AGENTS.md` splits the simulation policy into a `[SHOULD]` eligibility rule and a `[MUST]` fork guarantee. | ✓ VERIFIED | `AGENTS.md:205-213` |
| 35 | `AGENTS.md` states the native-test translation-unit deferral per ADR-0013, with no stale "until Phase 8 supplies a database" claim. | ✓ VERIFIED | `AGENTS.md:189-191`; the old wording is absent |
| 36 | `AGENTS.md`'s quick-start and quality-tooling sections record the CI hook surface and the host clang-tidy stage. | ✓ VERIFIED | `AGENTS.md:23, 25, 198-201` |
| 37 | The pull-request template's Definition of Done names the required `gate` check. | ✓ VERIFIED | `.github/pull_request_template.md:18` |
| 38 | `docs/decisions/README.md` carries one row for the single-gate CI topology with its change cost. | ✓ VERIFIED | `docs/decisions/README.md:31` |
| 39 | `.yamllint.yaml`'s comment describes the workflow surface without a stale workflow count. | ✓ VERIFIED | `.yamllint.yaml:14-23`; no fixed count, `check-keys: false` and `allowed-values` intact |

**Score:** 38/39 truths verified (1 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | -------- | ------ | ------- |
| `.github/workflows/ci.yml` | Jobs `meta`, `changes`, `build`, `python-tests`, `static-analysis`, `simulate`, `gate` | ✓ VERIFIED | 452 lines; all seven job ids present; the `gate` needs-set derives from the file |
| `.github/workflows/nightly.yml` | Jobs `changes`, `build`, `secrets`; no simulation | ✓ VERIFIED | 145 lines; `test_nightly_declares_the_full_matrix_job_set` asserts exactly `{changes, build, secrets}` |
| `.github/workflows/generated-views.yml`, `homework.yml`, `security.yml` | Removed | ✓ VERIFIED | Absent from the working tree and from `git ls-files` |
| `scripts/tests/test_ci_workflows.py` | Workflow text contract, 39 tests | ✓ VERIFIED | 516 lines; module run: 39 tests, `OK`; stdlib only |
| `AGENTS.md` | CI topology, gate contract, simulation policy, ADR-0013 | ✓ VERIFIED | 279 lines; all assertions from Plan 04 Task 1 pass |
| `.github/pull_request_template.md` | `gate` line in Definition of Done | ✓ VERIFIED | Line 18 |
| `docs/decisions/README.md` | One single-fan-in-gate row | ✓ VERIFIED | Line 31 with change cost "high" |
| `.yamllint.yaml` | Comment without a workflow count; policy unchanged | ✓ VERIFIED | Lines 14-23 |

*(`gsd_run query verify.artifacts` returned `total: 0` for every plan because the frontmatter records artifacts as prose strings; the table above is a manual three-level check.)*

### Key Link Verification

| From | To | Via | Status | Details |
| ---- | -- | --- | ------ | ------- |
| `scripts/affected.py` stdout | `$GITHUB_OUTPUT` → build matrix | `jq -c` → `fromJson` | ✓ WIRED | `ci.yml:195-202` and `:228`; mapper executed and payload is valid compact JSON |
| `meta`, `changes`, `build`, `python-tests`, `static-analysis`, `simulate` | `gate.needs` | literal `needs:` list | ✓ WIRED | `ci.yml:429`; derived by `test_gate_needs_every_pull_request_job` |
| `gen-views-check` hook | `meta` hook run | `pre-commit run --all-files` | ✓ WIRED | Hook id and entry at `.pre-commit-config.yaml:188-200`; `test_drift_gate_lives_in_the_hook_surface` |
| checkout `fetch-depth: 0` | `gitleaks git --log-opts="--all"` | full history | ✓ WIRED | `ci.yml:33-34, 64`; ordering test green |
| `hashFiles('platformio.shared.ini', 'platformio.ini')` | toolchain cache key | `actions/cache` | ✓ WIRED | Same literal in `ci.yml:232`, `nightly.yml:85`, `ci.yml:301` |
| `platformio.shared.ini` | nightly matrix | `--paths-from` → `WIDEN_ALL` | ✓ WIRED | `nightly.yml:46-52`; widen-all run returned all projects plus `tests` |
| nightly cache key | default-branch cache → PR restore | same key literal | ✓ WIRED | Key equality verified; runtime seeding is a human item |
| nightly `secrets` job | post-merge scan | pinned gitleaks | ✓ WIRED | `nightly.yml:110-145` |
| `needs.changes.outputs.simulate` | `simulate.matrix.include` | `fromJson` | ✓ WIRED | `ci.yml:303-304, 329` |
| `simulate` steps | `upload-artifact` | `ARTIFACT_NAME` | ✓ WIRED | `ci.yml:383, 419-422`; name derivation tested |
| `WOKWI_CLI_TOKEN` | job-level env → step-level check | `secrets` context | ✓ WIRED | `ci.yml:307, 332-336` |
| ruleset required check | literal `gate` | GitHub UI | ⚠️ PARTIAL | The literal name is pinned in code and tests; the live ruleset is a UI artifact and cannot be read from the tree — human item |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
| -------- | ------------- | ------ | ------------------ | ------ |
| `ci.yml` `changes` | `build` / `simulate` | `scripts/affected.py --base origin/$BASE` | Yes — executed; one homework yielded 2 build / 1 simulate entries | ✓ FLOWING |
| `ci.yml` `build` | `matrix.include` | `fromJson(needs.changes.outputs.build)` | Yes — compact JSON from the mapper | ✓ FLOWING |
| `ci.yml` `simulate` | `matrix.include` | `fromJson(needs.changes.outputs.simulate)` | Yes — mapper emits the arduino entry only | ✓ FLOWING |
| `ci.yml` `simulate` | `ARTIFACT_NAME` | shell `tr` sanitisation → `$GITHUB_ENV` | Yes — derived from `PROJECT`/`ENV_NAME` | ✓ FLOWING |
| `ci.yml` `simulate` | `quota.json` | scenario exit status, timing, serial-log size | Yes — stub run produced a real file with `exit_code`/`outcome` | ✓ FLOWING |
| `ci.yml` `gate` | `RESULTS` | `toJSON(needs)` → jq selector | Yes — synthetic payload selected `build=failure`; all-pass produced no output | ✓ FLOWING |
| `nightly.yml` `changes` | `build` | `affected.py --paths-from` with `platformio.shared.ini` | Yes — widen-all returned the full set | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| Workflow text contract | `python3 -m unittest scripts.tests.test_ci_workflows -v` | 39 tests, `OK` | ✓ PASS |
| Whole Python suite (the `python-tests` job's command) | `python3 -m unittest discover scripts/tests` | 333 tests, `OK` | ✓ PASS |
| Mapper no-build and changed-only sets | `printf 'docs/standards/vscode.md\n' \| uv run scripts/affected.py --paths-from /dev/stdin` | `{"build": [], "simulate": []}` | ✓ PASS |
| Mapper one-homework set | one path under `homeworks/1_3-police-flasher` | 2 build entries, 1 simulate entry | ✓ PASS |
| Mapper determinism | run the widen-all input twice, `cmp` | byte-identical, same SHA-256 | ✓ PASS |
| `gate` result allowlist | exact jq program over `{success, failure, skipped}` | `build=failure`; all-pass/`skipped` produced zero lines | ✓ PASS |
| Scenario evidence on non-zero exit (CR-01) | extracted step run under `bash -e` with a stub CLI exiting 42 | `quota.json` written, `outcome: timeout`, exit 42, both logs retained | ✓ PASS |
| Diagram lint | `wokwi-cli lint --offline homeworks/1_3-police-flasher/assets/diagram.json` | exit 0 (one informational note) | ✓ PASS |
| Workflow YAML syntax | `pre-commit run yamllint --files .github/workflows/ci.yml .github/workflows/nightly.yml` | Passed | ✓ PASS |
| Simulation option spelling | `python3 -m unittest scripts.tests.test_simulation_paths -v` | 3 tests, `OK` (wokwi-cli present) | ✓ PASS |

### Probe Execution

| Probe | Command | Result | Status |
| ----- | ------- | ------ | ------ |
| — | — | No `scripts/*/tests/probe-*.sh` exists and the plans/summaries declare none | SKIPPED |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| ----------- | ----------- | ----------- | ------ | -------- |
| TOOL-05 | 08-01, 08-03, 08-04 | Fast `meta` job (schema, `--check` drift, lint, gitleaks, architecture) and a `changes` job computing the affected matrix | ✓ SATISFIED | `meta` runs the whole pre-commit hook surface plus the full-history gitleaks scan and diagram lint; `changes` emits both matrices; all contracts green |
| TOOL-06 | 08-01, 08-02, 08-03, 08-04 | CI builds/tests changed projects on every PR, exposes a single required `gate`, nightly runs the full matrix | ? NEEDS HUMAN | The `gate` job, its needs coverage and the nightly matrix exist and are text-tested; the ruleset adoption and a live green run cannot be verified from the tree |
| SIM-04 | 08-03, 08-04 | Simulation in CI only after the spike, only for changed projects, explicit timeouts, artifact upload, never required for forks | ? NEEDS HUMAN | The event-first guard, same-repo check, label, step-level token refusal, 15-second timeout, three-artifact upload and fork-skip are implemented and tested; the metered live run and quota behaviour need human verification |

**Orphaned requirements:** none. `REQUIREMENTS.md` maps exactly TOOL-05, TOOL-06 and SIM-04 to Phase 8 and every one is claimed by a plan. The `META-05` traceability note says its CI-matrix clause was deferred to Phase 8; the `changes` job now consumes `affected.py`, so that clause is fulfilled even though META-05 remains mapped to Phase 5.

### Test Quality Audit

| Test File | Linked Req | Active | Skipped | Circular | Assertion Level | Verdict |
| --------- | ---------- | ------ | ------- | -------- | --------------- | ------- |
| `scripts/tests/test_ci_workflows.py` | TOOL-05, TOOL-06, SIM-04 | 39 | 0 | 0 | Value / behavioral (exact command strings, ordering, derived job set; the `gate` jq selector and the scenario step were also exercised directly) | PASS |
| `scripts/tests/test_affected.py` | TOOL-05, TOOL-06 | 26 | 0 | 0 | Value (matrix payloads, widen-all, determinism) | PASS |
| `scripts/tests/test_simulation_paths.py` | SIM-04 | 3 active (one conditional environmental skip when `wokwi-cli` is absent; present here, so it ran) | 0 | 0 | Behavioral (`wokwi-cli` path resolution, negative control) | PASS |

**Disabled tests on requirements:** 0 → no blocker.
**Circular patterns detected:** 0 → no blocker.
**Insufficient assertions:** 1 non-blocking observation — several workflow contracts assert whole-file substrings (WR-08/WR-09/WR-10 in `08-REVIEW.md`), so a regression confined to the intended job could hide behind an identical line in `meta`. The must-haves name these exact assertions and they are present; the hardening is recorded as a review warning, not a phase gap.

### Decision Coverage

All trackable CONTEXT.md decisions are honored by shipped artifacts (21/21; no `not_honored` entries).

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| `.github/workflows/ci.yml` | 307 | Job-level `WOKWI_CLI_TOKEN` reaches the `pio run` step (WR-01) | ⚠️ WARNING | Least-privilege hardening; the token is still scoped to a same-repository, maintainer-labelled PR, and no must-have fails |
| `.github/workflows/ci.yml` | 419-422 | `upload-artifact` can run with an empty `ARTIFACT_NAME` when the preparation step fails (WR-02) | ⚠️ WARNING | Produces a secondary, misleading failure; evidence contract itself holds |
| `.github/workflows/nightly.yml` | 42-53 | An empty nightly matrix would still run green (WR-04) | ⚠️ WARNING | Latent drift detector weakness; the widen-all path currently returns a non-empty set |
| `scripts/tests/test_ci_workflows.py` | 237-278 | Whole-file contract assertions can be satisfied by another job's lines (WR-08/WR-09/WR-10) | ⚠️ WARNING | Test-hardening gaps already recorded in `08-REVIEW-DISPOSITION.md`; the named assertions exist and pass |
| `.pre-commit-config.yaml` | 222-224 | Comment still says the native-test gap is "handed to Phase 8", although Phase 8 deliberately leaves it to ADR-0013 | ℹ️ INFO | Stale comment outside this phase's write scope; AGENTS.md carries the correct statement |
| `AGENTS.md` | 23 | Calls the quick-start command the "exact command" CI runs, while the CI job also passes `--show-diff-on-failure` (IN-06) | ℹ️ INFO | Wording only |
| Review of phase files | — | No `TBD`/`FIXME`/`XXX` debt marker; no stub, hollow-property or empty-implementation pattern | — | Clean |

**Open code-review warnings:** 11 warnings and 11 info findings remain `open` in `08-REVIEW-DISPOSITION.md`. None of them negates a must-have; the single critical finding (CR-01) is fixed in commit `97c6099` and is now guarded by `test_scenario_step_reads_pipestatus_under_errexit`, which passes.

### Human Verification Required

1. **Adopt `gate` in the ruleset**

   **Test:** After the first green `ci.yml` run on a pull request, open Settings -> Rules -> the `main` ruleset and add `gate` as the required status check (0 approvals).
   **Expected:** `gate` appears in the required-checks picker and is the only required check.
   **Why human:** Rulesets are a GitHub-UI artifact (AGENTS.md, D-20); a check becomes selectable only after passing within 7 days, and no repository file records the live setting.

2. **First live `ci.yml` run and duration**

   **Test:** Open a pull request changing `homeworks/1_3-police-flasher` and watch the run.
   **Expected:** `changes` emits a two-entry matrix; `build` splits `pio run`/`pio test -e native`; `meta`, `python-tests` and `static-analysis` are green; `gate` is green within the 15-minute `meta` budget.
   **Why human:** Triggers, runner images, matrix expansion and fan-in only exist at run time; F-15 notes the 15-minute budget is unmeasured.

3. **Opt-in labelled simulation**

   **Test:** Apply the `simulate` label to one same-repository PR changing `homeworks/1_3-police-flasher`, then open the artifacts; remove the label and push again.
   **Expected:** The label alone starts a fresh run; the artifact name has no slash; `serial.log`, `stdout.log` and `quota.json` are present and the job reports `scenario passed`; without the label no quota is spent and `gate` stays green; a fork PR never reaches the job.
   **Why human:** The run needs the repository secret, a maintainer label and the metered free-tier quota (SIM-04).

4. **Nightly concurrency and cache**

   **Test:** Observe a scheduled nightly run and a simultaneous manual dispatch; then let a pull-request `build` job restore the toolchain cache.
   **Expected:** The second run queues instead of overlapping; the matrix lists every project with a `platformio.ini` plus `tests`; the PR build restores the default-branch cache.
   **Why human:** Cache scoping and cold/warm duration are GitHub runner facts (F-15).

5. **Superseded-run cancellation and fail-fast siblings** (the ⚠️ truth)

   **Test:** Push twice in quick succession to one PR; separately, fail one entry of a multi-entry matrix.
   **Expected:** The superseded run is `cancelled` and the newer run reports a fresh `gate`; the failing entry does not cancel its siblings in the same run.
   **Why human:** The declarations (`cancel-in-progress: true`, `fail-fast: false`) are text-verified, but no local test exercises GitHub's cancellation/aggregation behaviour.

### Gaps Summary

No blocking gap was found. Every artifact the plans promised exists, is substantive and is wired: the two workflows, the retired-workflow removals, the 39-test contract, `AGENTS.md`, the pull-request template, the decision row and the yamllint comment. All behavioural checks available locally pass, including the mapper, the `gate` selector, the CR-01 evidence path and the diagram lint.

The phase cannot be marked `passed` because the goal's central promise — one required check adopted in the GitHub ruleset — and the runtime halves of the pipeline (a live green run, a metered labelled simulation, nightly cache/concurrency) are external-service facts that no repository file proves. Those are recorded above for human verification, together with the one cancellation-invariant truth that no local test exercises.

---

_Verified: 2026-10-26T19:20:25Z_
_Verifier: Claude (gsd-verifier)_

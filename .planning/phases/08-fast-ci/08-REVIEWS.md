---
phase: 8
reviewers: [codex-glm, codex-beam, antigravity]
reviewed_at: 2026-10-26T18:34:56Z
plans_reviewed: [08-01-PLAN.md, 08-02-PLAN.md, 08-03-PLAN.md, 08-04-PLAN.md]
models:
  codex-glm: "glm-5.3-flash:cloud (reasoning=high)"
  codex-beam: "beam:cloud (reasoning=high)"
  antigravity: "gemini-3.8-flash-high"
model_sources:
  codex-glm: "pinned"
  codex-beam: "pinned"
  antigravity: "pinned"
---

# Cross-AI Plan Review — Phase 8

<!-- gsd:plan-revision-conflicts:begin -->
## Plan-Revision Conflicts

<!-- gsd:plan-revision-conflicts:end -->

> Note: codex-glm and codex-beam share the codex adapter; their consensus is cross-model, not cross-tool. antigravity is an independent tool.

## Codex Review (codex-glm)

## 08-01

### Summary
This is the strongest plan in the wave. It correctly maps Phase 8’s first half onto verified repository contracts: `scripts/affected.py` already emits the required sorted `{build, simulate}` payload (`scripts/affected.py:47-53`, `454-479`) and pretty-prints JSON (`scripts/affected.py:481-494`), so using `jq -c` before `$GITHUB_OUTPUT` is the right call. The literal `gate` contract, empty-matrix guard, native-vs-target split, stale drift-workflow retirement, and current workflow-test updates all connect cleanly to files that exist today.

### Strengths
- Correctly uses `pio test -e native` and `pio run -e <target>`, matching the documented contract in `tests/platformio.ini:10-13` and `homeworks/1_3-police-flasher/platformio.ini:22-24`, rather than treating native tests as ordinary builds.
- Correctly retires `generated-views.yml`: the same command already exists as the check-only hook at `.pre-commit-config.yaml:188-200`, and the current obsolete text test is `scripts/tests/test_ci_workflows.py:87-89`.
- Correctly avoids relying on the staged gitleaks hook in CI. That hook is explicitly `--staged` (`.pre-commit-config.yaml:14-16`), while the proven full-history command is in `.github/workflows/security.yml:44-45`.
- The `gate` allowlist is safer than a deny-list because GitHub’s dependency `result` vocabulary is success, failure, cancelled, or skipped — no `timed_out`.
- Pinning `ubuntu-24.04` is well justified by the November 2026 `ubuntu-latest` migration.

### Concerns
- **HIGH — gitleaks is scheduled after untrusted PR code runs.** Task 2 explicitly says to append the history scan after the hook step at `.planning/phases/08-fast-ci/08-01-PLAN.md:142-148`. Since `meta` checks out the PR tree before that and then runs `pre-commit run --all-files`, a contributor-controlled `.pre-commit-config.yaml` or hook script executes before the INV-01 history scan. Even without secrets, this makes the security control easier to bypass or interfere with. The scan should run immediately after checkout, before `pre-commit install-hooks` and the hook run.
- **MEDIUM — the PR-title contract is not tested in this plan.** D-16 and the plan include the title regex, but Task 1’s proposed tests only cover migration of the drift assertion; there is no `test_meta_validates_the_title` or equivalent. The same class is later added in 08-03, but it still does not cover the title check.
- **MEDIUM — security non-tampering is asserted only in prose.** The plan says no job gets secrets or a write token (`08-01-PLAN.md:40-43`), but no workflow text test asserts the absence of `secrets.*`, `pull_request_target`, or a write permission.
- **LOW — cache key includes a nonexistent root `platformio.ini`.** The plan explicitly says this is intentional at `08-01-PLAN.md:105`, and the shared pin at `platformio.shared.ini:5` is indeed the important input, but the simpler and clearer key is `hashFiles('platformio.shared.ini')` only.

### Suggestions
- Reorder `meta`: checkout → title check → install/run gitleaks → pre-commit install → pre-commit run → Wokwi lint. That makes the history scan independent of later contributor-controlled hook execution.
- Add workflow-text tests for the title command/regex, absence of `secrets.*` in non-simulation jobs, and absence of `pull_request_target`.
- Add tests that assert the exact gitleaks and Wokwi version/digest constants, not just the executable commands.
- Use `hashFiles('platformio.shared.ini')` for the build cache key unless a root `platformio.ini` is a deliberate future convention.

### Risk Assessment
**MEDIUM-HIGH.** The repository wiring is correct, but this plan establishes the one-way required-check contract and currently places the history scan after contributor-controlled hook execution. That ordering is still safe in the no-secrets PR workflow but weakens the stated security role of the check. I would not execute without fixing the ordering and adding the missing policy-contract tests.

---

## 08-02

### Summary
This plan correctly completes the nightly topology without introducing a second matrix source. It reuses `affected.py --paths-from platformio.shared.ini`, relying on the mapper’s actual `WIDEN_ALL` table at `scripts/affected.py:112-120`, and replaces both the hard-coded build workflow and `security.yml`. The “keep `security.yml` between tasks” sequencing detail is a good merge-safety guard.

### Strengths
- The full nightly matrix is derived from real behavior: `scripts/affected.py:421-451` widens `platformio.shared.ini` to every project, and `_entries()` (`scripts/affected.py:454-479`) includes both homework environments and the top-level `tests/` project.
- It correctly applies the same native/target command split as the PR build.
- Nightly caching on the default branch is the right way to seed PR caches, given GitHub’s cache branch-scope behavior.
- It handles the post-merge secret-scan gap: `security.yml` currently scans both PR refs and `main` (`security.yml:3-9`, `44-45`), while `meta` cannot scan the eventual squash commit.
- The test-count transition is correct: current tree has three workflows (`git ls-files .github/workflows`), the first task leaves three, and the second leaves two.

### Concerns
- **MEDIUM — the nightly “no simulation” guarantee is not covered by a named automated test.** The plan states the truth at `.planning/phases/08-fast-ci/08-02-PLAN.md:22` and acceptance criterion at `:105`, and `.planning/phases/08-fast-ci/08-VALIDATION.md:60,75` explicitly requires a text assertion, but Task 2 adds only the job-set and gitleaks assertions. This is a missing planned test.
- **MEDIUM — no concurrency control on `nightly.yml`.** The plan says not to add one (`08-02-PLAN.md:85`), which is reasonable for schedules but still permits overlapping `workflow_dispatch` and scheduled runs. A non-cancelling concurrency group would protect runner/cache usage without cancelling a normal schedule.
- **LOW — cache-key spelling repeats D-18’s nonexistent-root issue.** The same plan text at `08-02-PLAN.md:89` uses `hashFiles('platformio.shared.ini', 'platformio.ini')`, although no root `platformio.ini` exists.
- **LOW — the 90-minute timeout is per matrix job, not a whole-workflow budget.** That matches practical CI usage, but the plan/documentation wording “nightly 90 minutes” could be interpreted as overall. A comment in the workflow would avoid confusion.

### Suggestions
- Add `test_nightly_declares_no_simulation` and assert that `nightly.yml` contains none of `wokwi`, `WOKWI_CLI_TOKEN`, or `simulate`.
- Add a concurrency group such as `${{ github.workflow }}` with `cancel-in-progress: false` to avoid duplicate nightly runs.
- Prefer the shared-ini-only cache key in both 08-01 and 08-02.
- Clarify in the workflow comment that “90 minutes” applies per build job.

### Risk Assessment
**LOW-MEDIUM.** The topology is sound and the matrix source is verified. The main defect is under-testing an explicit success criterion, not an implementation-design flaw.

---

## 08-03

### Summary
This completes the phase’s remaining gate jobs. The `python-tests`, `static-analysis`, and fan-in widening are well specified, and the repository sources support them: the test suite is stdlib-driven, `scripts/clang-tidy-db` expects `tests/compile_commands.json` (`scripts/clang-tidy-db:52-60`), and the pre-push hooks really do contain the two clang-tidy hooks (`.pre-commit-config.yaml:225-255`). However, two live-GitHub issues are likely to make the opt-in simulation path unusable or unreliable on its first real use.

### Strengths
- Correctly documents the site-removal deviation from D-15: the site, `mkdocs.yml`, and `requirements-docs.txt` really were deleted in `9d28f5d`; the ROADMAP amendment is present at `.planning/ROADMAP.md:351`.
- Correctly creates a separate `static-analysis` job because the clang-tidy hooks are pre-push-only (`.pre-commit-config.yaml:233,255`) and require a generated compile database.
- The fork guard follows the right security shape: no `pull_request_target`, secrets exposed only to same-repo PR runs, label-gated execution, and step-level token check.
- It builds firmware in the simulate job, which is required because `wokwi.toml` points at local `.pio/build/esp32s3_arduino` artifacts (`homeworks/1_3-police-flasher/wokwi.toml:3-4`).
- The Wokwi command shape matches the CLI and the path-resolution tests: `--diagram-file`, `--scenario`, and `--timeout` are verified relative to the positional project path in `scripts/tests/test_simulation_paths.py:17-69`.

### Concerns
- **HIGH — a label application will not trigger this workflow.** The plan’s `pull_request` trigger from 08-01 includes `opened`, `synchronize`, `reopened`, and `edited` (`08-01-PLAN.md:99`), but omits `labeled`. If a maintainer applies the `simulate` label after the last push, the CI workflow will not run unless a later push happens. The human check at `08-03-PLAN.md:160-164` assumes label application produces an artifact run, but does not add the trigger type. GitHub’s Pull Request activity types include `labeled` [GitHub Docs — workflow event types](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#pull_request).
- **HIGH — the artifact name is invalid for every current simulated project.** Task 2 uses `simulation-${{ matrix.project }}-${{ matrix.env }}` (`08-03-PLAN.md:151,258`), and `affected.py` emits projects such as `homeworks/1_3-police-flasher` (`scripts/affected.py:462-479`). Slash in the artifact name is not a valid naming pattern; the action requires the name to match `[a-zA-Z0-9_-]+` and prohibits characters such as slash [actions/upload-artifact README](https://github.com/actions/upload-artifact#inputs).
- **MEDIUM — simulation can start before the policy gate.** The job uses `needs: changes` only (`08-03-PLAN.md:149`). If `meta` fails, simulation may still start and consume quota. Having `simulate` wait for `meta` would bound accidental spend on a PR that already fails policy.
- **MEDIUM — `static-analysis` lacks a pre-commit cache.** It runs `pre-commit install-hooks` but only caches PlatformIO paths (`08-03-PLAN.md:115`). By then, `meta` already established the `~/.cache/pre-commit` cache (`08-01-PLAN.md:101`), so static analysis should restore the same cache or share a reusable layer.
- **MEDIUM — the plan does not test Wokwi version/digest retention.** It tests the lint command, serial-log option, upload, and retention, but not that `0.28.1` and the recorded SHA-256 remain in the workflow.

### Suggestions
- Add `labeled` to `pull_request.types`, and document that label changes rerun the PR gate. If that rerun is too costly, use a dedicated opt-in path, but as currently designed the label event is required.
- Sanitize the artifact name, e.g. use a derived/sanitized project id rather than embedding the path with `/`.
- Add `meta` to `simulate.needs`, or otherwise explain why starting before policy results is acceptable.
- Cache `~/.cache/pre-commit` in `static-analysis` with the same D-13 key.
- Add contract assertions for `WOKWI_CLI_VERSION`, `WOKWI_CLI_SHA256`, and the gitleaks version/digest.
- Consider changing artifact upload from `if-no-files-found: warn` to `error` when the job reaches the scenario stage; D-10 describes an evidence contract.

### Risk Assessment
**HIGH.** The job design is coherent, but the missing `labeled` trigger and slash-bearing artifact name are likely live-run defects: one prevents the feature from being invoked as intended, and the other breaks the evidence upload. Both should be fixed before execution.

---

## 08-04

### Summary
This is the right documentation close-out: the current rulebook still names `security.yml` (`AGENTS.md:32`, `152-154`, `242`) and the `generated-views` PR workflow (`AGENTS.md:46-50`), which will become false after 08-01/08-02. The planned decision row, PR-template gate line, and yamllint comment update are appropriately small.

### Strengths
- The plan correctly replaces stale rulebook claims with the final two-workflow topology, rather than merely adding text.
- The decision-record method is correct for this repository: a row in `docs/decisions/README.md` with no file unless deeper argumentation is needed, consistent with the current instruction at `docs/decisions/README.md:1-5`.
- The PR-template edit is minimal and lands in the existing Definition of Done at `.github/pull_request_template.md:9-15`.
- The current yamllint comment does indeed contain a stale count — “the four workflows” at `.yamllint.yaml:16-19` — so that edit is warranted.
- The human ruleset checkpoint matches D-20 and the validation strategy’s manual-only gate at `.planning/phases/08-fast-ci/08-VALIDATION.md:80-85`.

### Concerns
- **MEDIUM — verification does not cover removal of `generated-views` references from `AGENTS.md`.** The automated check at `.planning/phases/08-fast-ci/08-04-PLAN.md:128` only asserts that `security.yml` is absent. Since `AGENTS.md:48` currently names the generated-views workflow, a stale reference survives the same class of failure the plan is meant to prevent.
- **LOW — the simulation rule is marked `[SHOULD]`.** The invariant about forks and required status may be intentional as a policy preference, but the fork/no-secret guarantee sounds closer to `[MUST]` than `[SHOULD]`.
- **LOW — the plan objective says “three workflow files”** at `.planning/phases/08-fast-ci/08-04-PLAN.md:45-47`, but the final topology is two workflows. This is textual drift that could confuse execution.
- **LOW — older planning artifacts remain stale.** `.planning/STATE.md:84,90` still say the generated-views/read-only PR job remains, and 08-CONTEXT still contains the original D-15 docs-build wording. The phase plans only note the deviation; the plan itself doesn’t update these references.

### Suggestions
- Extend both 08-04 assertions: assert neither `security.yml` nor `generated-views`/`generated-views.yml` appears in `AGENTS.md`.
- Use `[MUST]` for the non-negotiable simulation properties unless there is a deliberate reason to keep it advisory.
- Correct the “three workflow files” sentence to “two”.
- Either update the stale Phase 8 planning references or include a note that planning artifacts are historical so review does not mistake them for current enforcement.

### Risk Assessment
**LOW-MEDIUM.** Mostly straightforward policy alignment. The verification gap around stale generated-views references is the main fix worth making before execution.

---

## Cross-plan ordering and dependency assessment

The wave order is fundamentally right:

1. 08-01 establishes `ci.yml` and folds drift checking into `meta`.
2. 08-02 introduces nightly and then retires the two old workflows without leaving secret scanning uncovered between commits.
3. 08-03 widens the gate to the full job surface and adds opt-in simulation.
4. 08-04 aligns the rulebook and template after runtime behavior exists.

No dependency cycle exists. The one-way required-check concern is handled by the literal `gate` contract test, although the strongest enforcement arrives only in 08-03.

The largest cross-plan risks are also cross-contract:

- **Run the secret scan before any PR-source hook execution** in 08-01.
- **Add `labeled` to `pull_request.types`** so 08-03’s simulation switch can actually work.
- **Sanitize `matrix.project` in artifact names** because affected entries use repository paths.
- **Add the explicitly promised nightly/no-simulation and PR-title tests.**

## Overall assessment

**Overall risk: HIGH** as currently written, but reducible to **LOW-MEDIUM** with small plan edits.

The architectural choices are correct and unusually well aligned with the real repository contracts. The fan-in gate, changed-only matrix, nightly topology, and opt-in simulation design are sound. However, the two live-Actions issues in 08-03 plus the security ordering issue in 08-01 are enough to demand a plan revision before execution. These are not speculative architecture concerns; they affect whether the required gate, quota gate, and evidence contract behave as stated on the first real PR.


---

## Codex Review (codex-beam)

## 08-01

**Summary:** This plan turns the single hard-coded `homework.yml` into a changed-only pipeline, with `meta`, `changes`, `build`, and the literal fan-in `gate`. It is the load-bearing plan for TOOL-05/TOOL-06 and, aside from its size, is consistent with the in-tree contracts.

**Strengths**
- Keeps one drift surface: the hook is the source of truth (`gen-views-check` at `.pre-commit-config.yaml:188`/`:192`), not a duplicated CI command; the test move from `generated-views.yml` to the hook surface is appropriate.
- Preserves the fork-safe staged-only gap by copying the full-history scan from `.github/workflows/security.yml:24-45` (`gitleaks git --redact --verbose --log-opts="--all"`) into a separate `meta` step; the hook alone would scan an empty index (`.pre-commit-config.yaml:15` uses `--staged`).
- The job-level empty-matrix guard and `!cancelled()` aggregator follow the platform edge cases researched (matrix expansion precedes step execution; `needs.<job>.result` has no `timed_out` value).
- Build command split is correct per the in-tree contract (`pio test -e native`, not `pio run -e native`), and the top-level `tests/` project needs no special-case because `affected.py` emits `env: native` for it.

**Concerns**
- **MEDIUM:** The task says to leave the trigger-key workflow count at `3` while deleting `generated-views.yml` and adding `ci.yml`. That count is only coherent if `homework.yml` and `security.yml` both still exist at the end of this wave. The next plan then drops to `2`. A failure midway through wave 2 leaves tests pinned to a stale count.
- **MEDIUM:** `test_drift_gate_lives_in_the_hook_surface` changes both constants and test method names. The plan must ensure no dangling reference to `GENERATED_VIEWS` remains in `test_ci_workflows.py`, or the stdlib suite stops importing.
- **MEDIUM:** The full-history gitleaks step requires `fetch-depth: 0` in `meta`; the supplied checkout must include it, and the current `generated-views.yml`/`homework.yml` templates only set `persist-credentials: false`. This is stated, but a missed flag silently makes the scan shallow.
- **LOW:** The plan's `meta` includes both gitleaks install and wokwi-cli install in the same job, so hook cold time can dominate early runs; the shared cache key makes it one-time.

**Suggestions**
- Make the 08-01 test update assert workflow names rather than a hard-coded count where possible, so the later retirement does not require editing the same assertion twice.
- Add a short verification command that `ci.yml` contains `fetch-depth: 0` in `meta` before the gitleaks step.
- Keep `python -m unittest discover scripts/tests` as the task-level gate; it already covers 380 tests.

**Risk Assessment:** MEDIUM — the topology is sound, but the plan modifies the only workflow-count assertion in the repository's contract test, so ordering drift is the main failure mode.

## 08-02

**Summary:** Nightly replaces the single-project build with the full matrix derived through `affected.py`'s own widen-all table, and restores post-merge secret scanning after `security.yml` retires. It is the smaller, mechanically simpler plan and closes the plan's main topology gap.

**Strengths**
- Reuses the existing mapper instead of inventing a new full-matrix flag: feeding `platformio.shared.ini` through `--paths-from` exercises the `WIDEN_ALL` entry at `scripts/affected.py:113` and keeps a single source of truth.
- Keeps the pull-request build cache key identical, so the default-branch run seeds the cache that PR runs restore; this addresses the branch-scoped cache pitfall.
- Moves the full-history scan to nightly's `secrets` job, which is necessary because the squash commit is created after the PR scan closes.

**Concerns**
- **HIGH:** This is the plan that retires both `homework.yml` and `security.yml`. The research notes that `homework.yml` is the only build proof today; until CI first runs green, `meta`/`build` coverage for PRs depends entirely on the new workflows being syntactically correct.
- **MEDIUM:** `nightly.yml` declares no concurrency group. That is intentional to avoid cancelling scheduled runs, but two long nightly runs can overlap on the free-tier runner.
- **MEDIUM:** No simulation job is permitted in nightly by design. That is correct for quota, but the plan should ensure no future edit re-adds it silently; there is no automated assertion beyond the text test.
- **LOW:** The widen-all assertion in tests hard-codes the project set (`{"tests"} ∪ all homework dirs`). If a new homework lands without its matrix entry appearing, the test catches drift, which is desirable but makes the plan sensitive to repository growth.

**Suggestions**
- Add `test_nightly_has_no_simulation_reference` as a simple negative assertion, since that is the only guard against reintroducing nightly simulation.
- State the expected final `git ls-files .github/workflows` result in the plan summary, so the human checkpoint can verify it directly.

**Risk Assessment:** LOW-MEDIUM — the logic is already proven locally (`uv run scripts/affected.py --paths-from` produced every project), and the remaining risk is deployment and YAML correctness.

## 08-03

**Summary:** Completes the PR gate by adding `python-tests`, `static-analysis`, and the opt-in `simulate` job, then locks the aggregation contract in a new test class. This is where the phase carries real operational risk: the simulation path is unmeasured in CI and the guard behavior depends on null-context evaluation.

**Strengths**
- Closes the WR-13 Python-suite gap and the clang-tidy job gap with concrete commands that match the in-tree scripts (`pio run -d tests -e native -t compiledb` and `pre-commit run --all-files --hook-stage pre-push`).
- The belt-and-braces guard is correctly split: head-repo equality and label at job level, token at step level, avoiding the secrets-context evaluation failure.
- Artifact upload under `if: always()` with 7-day retention and the quota JSON is the right shape for evidence without policy mutation (`simulation.status` is never flipped by CI).
- The new `CiWorkflowContractTests` derive the `needs` set from the file, so dropping a dependency fails locally before reaching a PR.

**Concerns**
- **HIGH:** The simulation scenario uses an absolute `--serial-log-file` path under `$RUNNER_TEMP`. The plan itself flags this as unverified (`A2`), and `test_simulation_paths.py` only proves option spelling, not absolute-path acceptance.
- **HIGH:** The job-level `if` references `github.event.pull_request.labels.*.name` and head-repo equality. On `workflow_dispatch` the pull-request context is null; the plan should explicitly include `github.event_name == 'pull_request'` as the first short-circuit to avoid any null dereference in the expression evaluator.
- **MEDIUM:** `static-analysis` declares `timeout-minutes: 20`, but D-19 does not list a static-analysis timeout at all. This is a plan-level addition rather than a locked decision and should be reconciled.
- **MEDIUM:** There is no automated assertion that no workflow writes `simulation.status`; only the plan prohibition. Given the test style is textual, a grep assertion would be inexpensive and would make the contract durable.
- **MEDIUM:** `simulate` builds the firmware itself immediately before running, so a labelled PR pays the build cost again. That is correct because no build artifact is uploaded, but it should be made explicit in the plan's quota wording so the 15-second upper bound is not mistaken for total job minutes.
- **LOW:** `max-parallel: 2` in `simulate` bounds quota contention but is not derived from any measured per-run consumption; it is still a guess until the first labelled run.

**Suggestions**
- Make the simulate job-level guard safe by leading with `github.event_name == 'pull_request'` before any `github.event.pull_request.*` access.
- Add a text assertion that `--serial-log-file` is present and that no step interpolates `${{ matrix.* }}` into a `run:` body, since the plan's security claim rests on that.
- Reconcile the static-analysis timeout with D-19 or add it to that decision.

**Risk Assessment:** MEDIUM-HIGH — the PR-gate additions are straightforward, but the simulation job can only be validated by a live, quota-consuming run, and two of its critical assumptions are still unverified.

## 08-04

**Summary:** Aligns the rulebook, PR template, decision index, and yamllint comment with the new topology. It is documentation-only and low risk, but it touches the contract between `AGENTS.md` and the workflows, so its accuracy matters.

**Strengths**
- Removes the stale `.github/workflows/security.yml` reference from `AGENTS.md`, matching the repository layout after wave 2.
- Records the single-gate decision in `docs/decisions/README.md`, which is exactly the one-row default required by the decision rules.
- Keeps `.yamllint.yaml` policy values unchanged while replacing the stale workflow-count sentence.

**Concerns**
- **MEDIUM:** `AGENTS.md` must not claim an enforcement point that the workflows do not implement. The plan's text says `meta` scans the full history and `nightly`'s `secrets` job repeats it; both must be present or the rulebook over-claims. At wave 3, `nightly` already has `secrets`, so ordering is acceptable.
- **MEDIUM:** The plan says the simulation rule names the `simulate` label, same-repository condition, 15-second timeout, and 7-day retention. That is accurate, but the rule is only `[SHOULD] [ENFORCED: CI]`; contributors may read it as optional even in required-check contexts, so the wording should make clear it is an eligibility rule, not the gate.
- **LOW:** The yamllint comment change says the workflows are asserted to keep textual `on:` without a count. That matches the final 2-workflow reality, but the current `test_ci_workflows.py` has not yet had its count assertion renamed in wave 1; execution ordering must hold.
- **LOW:** No automated test ensures `AGENTS.md` claims match workflow files, so a later rename of `gate` could silently desync despite the written obligation.

**Suggestions**
- Add a low-cost assertion in `test_ci_workflows` (or a docs test) that `.yamllint.yaml` no longer mentions a workflow count and still contains `check-keys: false`.
- Clarify the simulation rule from "when simulation runs" to "simulation may run only when all three conditions hold," preserving the fork boundary.

**Risk Assessment:** LOW — documentation-only changes with no runtime effect; the residual risk is stale text, which review can catch.


---

## Antigravity Review

# Implementation Plan Review: Phase 8 (Fast CI)

This review examines plans `08-01`, `08-02`, `08-03`, and `08-04` for Phase 8 (*Fast CI*). All relative file paths were resolved against `/Users/vloktiev/Dev/miltech/homeworks` and verified against repository source files, configuration files, and live command executions.

---

## 08-01

### 1. Summary
Plan `08-01` establishes the foundational PR-time workflow [`.github/workflows/ci.yml`](file:///Users/vloktiev/Dev/miltech/homeworks/.github/workflows/ci.yml) containing four essential jobs: `meta` (running the local [`pre-commit`](file:///Users/vloktiev/Dev/miltech/homeworks/.pre-commit-config.yaml) hook surface, full-history secret scanning, diagram linting, and Conventional PR title enforcement), `changes` (evaluating diffs via [`scripts/affected.py`](file:///Users/vloktiev/Dev/miltech/homeworks/scripts/affected.py#L40-L65)), `build` (executing target builds with `pio run` or native unit tests with `pio test -e native` per matrix item), and `gate` (the single literal fan-in check required by GitHub rulesets). It cleanly retires [`.github/workflows/generated-views.yml`](file:///Users/vloktiev/Dev/miltech/homeworks/.github/workflows/generated-views.yml) by absorbing drift detection into `meta` and adjusts [`scripts/tests/test_ci_workflows.py`](file:///Users/vloktiev/Dev/miltech/homeworks/scripts/tests/test_ci_workflows.py#L1-L134) while keeping intermediate commits green.

### 2. Strengths
- **Stable Ruleset Aggregator**: Setting display name `name: gate` with `if: ${{ !cancelled() }}` and evaluating dependencies via `jq -r 'to_entries[] | select(.value.result != "success" and .value.result != "skipped")'` ensures that dynamic matrix jobs never break GitHub ruleset check matching.
- **Context Injection Defense**: PR title (`$PR_TITLE`), matrix projects (`$PROJECT`), and environments (`$ENV_NAME`) are routed strictly through `env:` variables rather than interpolating `${{ github.event.* }}` or `${{ matrix.* }}` into bash `run:` blocks, mitigating command injection vulnerabilities (T-8-01, T-8-02).
- **Cryptographic Tool Verification**: `gitleaks` (8.30.1) is checked against its published SHA-256 digest (`551f6f...`), and `wokwi-cli` (0.28.1) is checked against its recorded digest (`869f19...`), ensuring reproducible and tamper-evident toolchains.
- **Zero-Disruption Wave Transition**: By removing `generated-views.yml` while adding `ci.yml`, the workflow count remains exactly 3 (`ci.yml`, `homework.yml`, `security.yml`), preventing breakages in [`scripts/tests/test_ci_workflows.py:109`](file:///Users/vloktiev/Dev/miltech/homeworks/scripts/tests/test_ci_workflows.py#L109) (`self.assertEqual(3, len(files))`).

### 3. Concerns
- **MEDIUM**: Expression failure risk with `toJson(fromJson(...))`. Line 2152 specifies `if: toJson(fromJson(needs.changes.outputs.build)) != '[]'`. If the `changes` job terminates unexpectedly before writing `$GITHUB_OUTPUT`, `needs.changes.outputs.build` evaluates to `""` (empty string). In GitHub Actions expressions, `fromJson('')` crashes evaluation with a fatal syntax error, preventing the job from running or cleanly skipping. [08-RESEARCH.md](file:///Users/vloktiev/Dev/miltech/homeworks/.planning/phases/08-fast-ci/08-RESEARCH.md#L1529) Pitfall 4 explicitly documented: `if: ${{ needs.changes.outputs.build != '' && needs.changes.outputs.build != '[]' }}`.
- **LOW**: Redundant cache file path in key. Keying on `${{ runner.os }}-pio-${{ hashFiles('platformio.shared.ini', 'platformio.ini') }}` references a root `platformio.ini` which does not exist in this repository (all project configs reside at `homeworks/<id>/platformio.ini` or `tests/platformio.ini`). While `hashFiles` safely ignores non-matching patterns, keeping `'platformio.ini'` creates false expectations about root project files.

### 4. Suggestions
- Use direct string comparison on the job-level guard:
  ```yaml
  if: ${{ needs.changes.outputs.build != '' && needs.changes.outputs.build != '[]' }}
  ```
- Simplify the toolchain cache key to `${{ runner.os }}-pio-${{ hashFiles('platformio.shared.ini') }}` to accurately match repository layout.

### 5. Risk Assessment
- **Risk Level**: LOW
- **Justification**: Commands and script outputs were verified against live repository files. `scripts/affected.py` emits valid JSON for both docs-only diffs (`{"build": [], "simulate": []}`) and code changes, and pre-commit hooks pass locally.

---

## 08-02

### 1. Summary
Plan `08-02` adds the daily scheduled run [`.github/workflows/nightly.yml`](file:///Users/vloktiev/Dev/miltech/homeworks/.github/workflows/nightly.yml) (cron `17 3 * * *` and `workflow_dispatch`), generating the full build matrix by passing `platformio.shared.ini` to [`scripts/affected.py --paths-from`](file:///Users/vloktiev/Dev/miltech/homeworks/scripts/affected.py#L110-L116) to leverage the existing `WIDEN_ALL` contract. It systematically retires [`.github/workflows/homework.yml`](file:///Users/vloktiev/Dev/miltech/homeworks/.github/workflows/homework.yml) and [`.github/workflows/security.yml`](file:///Users/vloktiev/Dev/miltech/homeworks/.github/workflows/security.yml), migrating the full-history gitleaks scan to nightly to protect post-merge commits on `main`. Workflow tests are updated to assert exactly two workflows (`ci.yml` and `nightly.yml`).

### 2. Strengths
- **No Hand-Rolled Project Enumeration**: Reusing `affected.py --paths-from` with `platformio.shared.ini` ensures any newly added homework project under `homeworks/` is automatically discovered by nightly runs without manual workflow maintenance.
- **Post-Merge Secret Coverage**: Moving the full-history secret scan to nightly maintains INV-01 by detecting leaks that could be introduced via squashed pull-request titles or bodies on `main`, closing the gap created by retiring `security.yml`.
- **Default Branch Cache Seeding**: Nightly builds use the exact same cache key as PR builds (`${{ runner.os }}-pio-${{ hashFiles('platformio.shared.ini', 'platformio.ini') }}`), allowing the default branch run to prime cache entries that all PR branches can restore.
- **Accurate Post-Docs-Site Workflow Count**: Correctly accounts for the previous removal of `docs.yml` (commit `9d28f5d`), transitioning the workflow count in [`scripts/tests/test_ci_workflows.py`](file:///Users/vloktiev/Dev/miltech/homeworks/scripts/tests/test_ci_workflows.py#L109) from 3 to 2 without mismatching disk state.

### 3. Concerns
- **MEDIUM**: Same `toJson(fromJson(...))` expression guard on the nightly `build` job (line 2361), susceptible to empty string evaluation failure if `changes` job fails early.
- **LOW**: Potential cache evictions if PlatformIO build directories are cached indiscriminately. The plan caches `~/.platformio/packages`, `~/.platformio/.cache`, and `~/.cache/pip`, which respects GitHub Actions' 10 GB repository cache cap.

### 4. Suggestions
- Replace `toJson(fromJson(needs.changes.outputs.build)) != '[]'` with `needs.changes.outputs.build != '' && needs.changes.outputs.build != '[]'`.
- Add an explicit comment in `nightly.yml` explaining why simulation is omitted (to conserve Wokwi free-tier quota of ~50 simulated minutes per month).

### 5. Risk Assessment
- **Risk Level**: LOW
- **Justification**: Reusing `platformio.shared.ini` with `affected.py --paths-from` was verified directly on the repository tree and yields all 3 target/native entries (`homeworks/1_3-police-flasher` arduino/native and `tests` native).

---

## 08-03

### 1. Summary
Plan `08-03` completes `ci.yml` by introducing parallel `python-tests` (running `unittest discover scripts/tests` with pinned `uv==0.13.5`), `static-analysis` (running `pio run -d tests -e native -t compiledb` followed by `pre-commit run --all-files --hook-stage pre-push` for host clang-tidy), and the opt-in `simulate` job. Simulation is strictly gated to avoid quota drain and fork failures, executing `wokwi-cli` with a 15-second timeout and uploading `serial.log`, `stdout.log`, and `quota.json`. Finally, `gate.needs` is expanded, and [`CiWorkflowContractTests`](file:///Users/vloktiev/Dev/miltech/homeworks/scripts/tests/test_ci_workflows.py) locks in structural workflow constraints.

### 2. Strengths
- **Strict Simulation Perimeter (D-8, D-9)**: Requires `github.event.pull_request.head.repo.full_name == github.repository`, label `simulate`, and non-empty matrix. Secrets are never exposed to fork PRs, and absence of token fails closed on same-repo labeled PRs.
- **Closes ADR-0013 and WR-13 Gaps**: `python-tests` guarantees that all repository scripts remain tested in CI. `static-analysis` accurately produces `tests/compile_commands.json` on the fly, allowing pre-push clang-tidy to inspect `lib/common/src` and `lib/host/src`.
- **Dynamic Contract Verification**: `CiWorkflowContractTests.test_gate_needs_every_pull_request_job` parses the job keys of `ci.yml` and asserts `gate.needs` contains every other job, preventing silent gate omission in future edits.
- **Teeing Scenario Evidence**: Captures both exit status and terminal logs using `PIPESTATUS[0]` with `tee`, creating structured `quota.json` evidence alongside stdout and serial logs.

### 3. Concerns
- **HIGH**: Illegal forward slash in artifact upload name.
  Line 2616 and Line 2722 define:
  ```yaml
  name: simulation-${{ matrix.project }}-${{ matrix.env }}
  ```
  In this monorepo, `matrix.project` is formatted as `"homeworks/1_3-police-flasher"`.
  The interpolated artifact name evaluates to:
  `simulation-homeworks/1_3-police-flasher-esp32s3_arduino`.
  In GitHub Actions (`actions/upload-artifact@v4` / `v7`), forward slashes (`/`) and backslashes (`\`) are strictly forbidden in artifact names. Attempting to upload an artifact with `/` in its name causes `actions/upload-artifact` to exit with an error:
  `Artifact name is not valid: ... Contains the following invalid character: /`.
  Because the upload step will fail, the `simulate` job will report `failure`, causing `gate` to fail on every simulated run.
- **MEDIUM**: Uncached `pre-commit` environment in `static-analysis`.
  Line 2579 configures toolchain caching for `~/.platformio/packages` and `~/.platformio/.cache`, but omits `~/.cache/pre-commit`. Running `pre-commit run --all-files --hook-stage pre-push` downloads and sets up `cpp-linter-hooks` on every CI run, unnecessarily adding 30–60 seconds of cold setup time.
- **LOW**: Absence of `serial.log` on early simulation connection errors.
  If `wokwi-cli` encounters an early network failure before connecting to the simulator, `--serial-log-file` is not created by `wokwi-cli`. While `upload-artifact` targets the directory and sets `if-no-files-found: warn`, downstream evidence consumers might expect `serial.log` to always be present.

### 4. Suggestions
- **CRITICAL FIX**: Sanitize the artifact name before uploading by replacing slashes with dashes or extracting the basename:
  ```bash
  # Inside the scenario step:
  SAFE_PROJECT=$(echo "$PROJECT" | tr '/' '-')
  echo "ARTIFACT_NAME=simulation-${SAFE_PROJECT}-${ENV_NAME}" >> "$GITHUB_ENV"
  ```
  Then in the upload step:
  ```yaml
  name: ${{ env.ARTIFACT_NAME }}
  ```
  Ensure `CiWorkflowContractTests` verifies the sanitized pattern rather than asserting an illegal slash.
- Add `~/.cache/pre-commit` to the `actions/cache` paths in `static-analysis` using the same key as `meta`.
- Touch `$RUNNER_TEMP/simulation/serial.log` prior to launching `wokwi-cli` so the expected evidence triad always exists.

### 5. Risk Assessment
- **Risk Level**: MEDIUM
- **Justification**: The invalid artifact name (`/` character) will break any run where simulation is executed. Resolving the artifact naming reduces the risk level to LOW.

---

## 08-04

### 1. Summary
Plan `08-04` synchronizes repository documentation, contributor guides, and decision records with the new CI architecture. It updates [`AGENTS.md`](file:///Users/vloktiev/Dev/miltech/homeworks/AGENTS.md) (agent quick-start, layout, rules for `gate`, secrets scanning, and static analysis), adds `- [ ] The required gate check is green` to [`.github/pull_request_template.md`](file:///Users/vloktiev/Dev/miltech/homeworks/.github/pull_request_template.md#L12-L18), appends a formal decision row to [`docs/decisions/README.md`](file:///Users/vloktiev/Dev/miltech/homeworks/docs/decisions/README.md), and adjusts the workflow comment in [`.yamllint.yaml`](file:///Users/vloktiev/Dev/miltech/homeworks/.yamllint.yaml#L17-L18).

### 2. Strengths
- **Severity Tag Consistency**: Retains the mandatory `[MUST]` and `[SHOULD]` tags and enforcement levels (`[ENFORCED: CI]`, `[ENFORCED: review]`) required by [`AGENTS.md`](file:///Users/vloktiev/Dev/miltech/homeworks/AGENTS.md#L90-L95).
- **Pruning Stale References**: Systematically cleans up references to retired workflows (`security.yml`, `generated-views.yml`) across `AGENTS.md` and `.yamllint.yaml`.
- **Actionable PR Checklist**: Explicitly reminds contributors of the required status check in `.github/pull_request_template.md`.
- **Decision Record Integrity**: Records the single-gate fan-in topology with an accurate "high" change cost justification in `docs/decisions/README.md`.

### 3. Concerns
- **LOW**: Residual forward-reference in `AGENTS.md:179-180`.
  Currently, [`AGENTS.md:179-180`](file:///Users/vloktiev/Dev/miltech/homeworks/AGENTS.md#L179-L180) reads:
  `Native test translation units are out of scope until Phase 8 CI owns a database for them.`
  Because Phase 8 specifically deferred native test translation units (due to the `unity_config.h` issue documented in ADR-0013 and CONTEXT.md D-17), this forward-reference becomes stale. Plan `08-04` must update this phrasing to state that native test translation units remain deferred per ADR-0013.

### 4. Suggestions
- Explicitly update `AGENTS.md:179-180` to replace "until Phase 8 CI owns a database for them" with "and remain deferred per ADR-0013."

### 5. Risk Assessment
- **Risk Level**: LOW
- **Justification**: Purely documentation and configuration updates. Pre-commit hooks (`markdownlint-cli2`, `yamllint`) and test suites remain green.

---

## Cross-Plan Comparison and Overall Risk Assessment

### Dependency Sequencing
The four execution waves are logically ordered:
1. `08-01` creates the `ci.yml` tracer and single gate check while keeping old workflows temporarily.
2. `08-02` adds `nightly.yml`, migrates post-merge secret scanning, and safely removes `homework.yml` and `security.yml`.
3. `08-03` expands the PR gate with static analysis, Python tests, simulation, and strict contract tests.
4. `08-04` aligns documentation with the finished workflows.

### Workflow Count Validation
The planned updates to `scripts/tests/test_ci_workflows.py` correctly track the file system state after the earlier removal of `docs.yml`:
- Initial: 3 workflows (`generated-views.yml`, `homework.yml`, `security.yml`)
- After `08-01`: 3 workflows (`ci.yml`, `homework.yml`, `security.yml`)
- After `08-02` Task 1: 3 workflows (`ci.yml`, `nightly.yml`, `security.yml`)
- After `08-02` Task 2: 2 workflows (`ci.yml`, `nightly.yml`)
- Final: 2 workflows (`ci.yml`, `nightly.yml`)

### Overall Verdict
**Risk Level: MEDIUM** (due entirely to the invalid artifact name in `08-03`). Once the artifact naming pattern in `08-03` is sanitized to replace forward slashes (`/`), all plans achieve their respective phase goals cleanly and safely.


---

## Consensus Summary

Three independent reviewers ran the same source-grounded prompt against all four plans. Two of
them share the `codex` adapter but ran different models, so their agreement is **cross-model,
not cross-tool**; `antigravity` is an independent tool. All three covered every plan id.

Overall risk: **MEDIUM-HIGH**. The architectural choices are consistently judged sound — the
fan-in gate, the changed-only matrix, the nightly widen-all, and the fork-safe simulation
perimeter are all verified against the real repository contracts. The blockers that survive
consensus are operational and narrow: one invalid artifact name, one missing trigger type, and
several promised tests that the plans do not actually add.

### Agreed Strengths

- **The single literal `gate` is the right required-check contract.** Every reviewer confirmed
  the `id`/`name: gate` pair, `needs` over all PR jobs, `if: ${{ !cancelled() }}`, and the
  `success`/`skipped` allowlist. The allowlist is correct because GitHub's `needs.*.result`
  vocabulary has no `timed_out` value.
- **Changed-only plumbing reuses `scripts/affected.py` rather than a second glob dialect.** The
  sorted `{build, simulate}` payload, the pretty-printed stdout that requires `jq -c`, and the
  fail-safe widening table were all traced to the script, not taken on faith.
- **The native/target command split matches the in-tree contract.** `pio test -e native` and
  `pio run -e <env>` are confirmed against `tests/platformio.ini` and the pilot's
  `platformio.ini`; the top-level `tests/` project needs no special case.
- **Full-history gitleaks must be its own step.** The pre-commit hook is `--staged`, so it scans
  an empty index on a fresh checkout; the separate step is necessary, not redundant.
- **Nightly derives the full matrix from the mapper's own widen-all rule** and seeds the
  default-branch cache that PR builds restore.
- **The simulation perimeter is correctly shaped**: same-repo head check plus label at job level,
  token at step level, no `pull_request_target`, no secrets on fork PRs, and no write to
  `simulation.status`.

### Agreed Concerns

1. **HIGH — the simulation artifact name is invalid on every run.** The plans use
   `simulation-${{ matrix.project }}-${{ matrix.env }}`, and `affected.py` emits project ids such
   as `homeworks/1_3-police-flasher`. `actions/upload-artifact` rejects `/` in an artifact name,
   so the upload step fails and `gate` goes red on every simulated run. Sanitize the project id
   (for example `tr '/' '-'`) before naming the artifact, and assert the sanitized form in the
   workflow test.
2. **MEDIUM — the nightly "no simulation" guarantee has no automated assertion.** Both the
   truth in 08-02 and `08-VALIDATION.md` require a text assertion, but the plan adds only the
   job-set and gitleaks checks. Add a negative assertion over `nightly.yml` for `wokwi`,
   `WOKWI_CLI_TOKEN`, and `simulate`.
3. **MEDIUM — the PR-title check is not tested.** D-16 and the plan include the Conventional
   Commits regex, but no test asserts the title step, its regex, or that it is skipped on
   `workflow_dispatch`.
4. **MEDIUM — `static-analysis` does not restore the pre-commit cache.** It runs
   `pre-commit install-hooks` with only PlatformIO paths cached, so the pre-push hook
   environments are rebuilt on every run. Reuse `~/.cache/pre-commit` with the same key as
   `meta`.
5. **MEDIUM — the `AGENTS.md` verification is narrower than the edit.** The assertion covers
   the removal of `security.yml` but not the removal of the `generated-views` workflow
   reference, which the same plan edits.
6. **LOW — the toolchain cache key names a root `platformio.ini` that does not exist.** All
   three reviewers flagged `hashFiles('platformio.shared.ini', 'platformio.ini')`; the shared
   ini alone is the pin input. `hashFiles` tolerates the miss, so this is clarity, not a defect.

### Divergent Views

- **Overall risk.** `codex-glm` rates the set HIGH, `antigravity` MEDIUM, and `codex-beam`
  LOW-MEDIUM per plan while calling the simulation path MEDIUM-HIGH. The difference is whether
  the unverified live-Actions assumptions are treated as blocking; all three agree the
  architecture itself is sound.
- **Workflow-count ordering.** `codex-beam` reads the intermediate "3 workflows" assertion as a
  fragile midpoint; `antigravity` reads the same transition (3 → 3 → 3 → 2) as verified and
  correct. The plans do keep the suite green at every commit, so this is a robustness
  preference rather than a defect.
- **Retiring `homework.yml`/`security.yml` before a first green run.** `codex-beam` rates this
  HIGH; the others accept it because `security.yml`'s scan is replaced in the same commit and
  nightly owns the post-merge scan.

### Single-Reviewer Findings Worth Checking (unconfirmed)

- **`labeled` is missing from `pull_request.types`** (codex-glm, HIGH). Applying the `simulate`
  label after the last push would not trigger `ci.yml`, so the human check that assumes a label
  produces a run would not hold. Either add `labeled` or document that label changes require a
  push.
- **The full-history gitleaks step is ordered after contributor-controlled hook execution**
  (codex-glm, HIGH). Running the scan immediately after checkout makes the security control
  independent of later `pre-commit` execution.
- **The absolute `--serial-log-file` path is unverified** (codex-beam, HIGH). `test_simulation_paths.py`
  proves option spelling, not that an absolute path is accepted; the plan itself flags this as
  assumption A2.
- **The job-level `if` dereferences `github.event.pull_request.*` without an event guard**
  (codex-beam, HIGH). Leading with `github.event_name == 'pull_request'` removes any null-context
  risk on `workflow_dispatch`.
- **`toJson(fromJson(needs.changes.outputs.build))` fails on an empty string** (antigravity,
  MEDIUM). The research's Pitfall 4 recommends the direct comparison
  `needs.changes.outputs.build != '' && ... != '[]'`.
- **`simulate` depends only on `changes`** (codex-glm, MEDIUM). A labelled PR that already fails
  `meta` can still start a quota-consuming simulation; adding `meta` to `needs` bounds that.
- **`AGENTS.md` keeps a forward reference to "Phase 8 CI owns a database"** (antigravity, LOW).
  Native test translation units stay deferred per ADR-0013, so the sentence becomes false.

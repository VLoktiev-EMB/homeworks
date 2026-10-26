---
phase: "8"
slug: "fast-ci"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: validated
nyquist_compliant: true
wave_0_complete: true
created: "2026-10-26"
---

# Phase 8 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Python stdlib `unittest` (no third-party test runner) |
| **Config file** | none — discovery from `scripts/tests` |
| **Quick run command** | `python3 -m unittest discover scripts/tests` |
| **Full suite command** | `python3 -m unittest discover scripts/tests` |
| **Estimated runtime** | ~34 seconds locally (332 tests, 1 skipped) |

---

## Sampling Rate

- **After every task commit:** Run `python3 -m unittest discover scripts/tests`
- **After every plan wave:** Run `python3 -m unittest discover scripts/tests` plus
  `pre-commit run --all-files --show-diff-on-failure`
- **Before `/gsd-verify-work`:** Full suite must be green, and one live `ci.yml` run must be
  green before the ruleset checkpoint
- **Max feedback latency:** 60 seconds

---

## Per-Task Verification Map

Every task below carries an automated `<verify>` command that ran green during the Phase 8
execution and again during this audit.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 08-01/T1 End-to-end changed-only PR gate | 08-01 | 1 | TOOL-05, TOOL-06 | T-8-01 | Read-only permissions; no pull-request-target trigger | text contract | `python3 -m unittest scripts.tests.test_ci_workflows -v`; ci.yml contract assertions; `affected.py` no-build-impact | ✓ | ✅ green |
| 08-01/T2 Full-history secret scan and diagram lint in `meta` | 08-01 | 1 | TOOL-05 | T-8-02 | Scan runs before contributor-controlled hooks | text contract + tool run | `python3 -m unittest scripts.tests.test_ci_workflows -v`; `wokwi-cli lint --offline` | ✓ | ✅ green |
| 08-02/T1 Nightly full matrix | 08-02 | 2 | TOOL-06 | T-8-03 | Default-branch scan of the squash commit | text contract + behavioral | `python3 -m unittest scripts.tests.test_ci_workflows -v`; widen-all `affected.py --paths-from` | ✓ | ✅ green |
| 08-02/T2 Retire `security.yml` | 08-02 | 2 | TOOL-06 | T-8-03 | Replacement check lands in the same plan | text contract | `python3 -m unittest scripts.tests.test_ci_workflows -v`; `git ls-files .github/workflows` equals two files | ✓ | ✅ green |
| 08-03/T1 `python-tests` and `static-analysis` | 08-03 | 3 | TOOL-05, TOOL-06 | T-8-04 | Host-only clang-tidy over `lib/common/src` and `lib/host/src` | text contract | `python3 -m unittest scripts.tests.test_ci_workflows -v`; ci.yml stage assertions | ✓ | ✅ green |
| 08-03/T2 Opt-in `simulate` with evidence upload | 08-03 | 3 | SIM-04 | T-8-05 | Fork can never reach the token; step-level emptiness check | text contract | `python3 -m unittest scripts.tests.test_ci_workflows -v`; simulate-guard assertions | ✓ | ✅ green |
| 08-03/T3 Lock the gate contract into the suite | 08-03 | 3 | TOOL-05, TOOL-06, SIM-04 | T-8-06 | Contract tests assert absence of write permissions and status flips | text contract | `python3 -m unittest scripts.tests.test_ci_workflows.CiWorkflowContractTests -v` (11 tests) | ✓ | ✅ green |
| 08-04/T1 `AGENTS.md` names the CI topology | 08-04 | 4 | TOOL-05, TOOL-06, SIM-04 | T-8-07 | Policy names no enforcement point that does not exist | text contract | inline `AGENTS.md` assertions; `python3 -m unittest scripts.tests.test_ci_workflows -v` | ✓ | ✅ green |
| 08-04/T2 Decision row, template and yamllint comment | 08-04 | 4 | TOOL-05, TOOL-06, SIM-04 | T-8-07 | Ruleset stays a GitHub-UI artifact and a human checkpoint | text contract | inline template/decision/yamllint assertions; `python3 -m unittest scripts.tests.test_ci_workflows -v` | ✓ | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| TOOL-05 | `meta` runs the hook surface, gitleaks full history, `wokwi-cli lint`, and the title check; `changes` emits both matrices | text contract | `python3 -m unittest scripts.tests.test_ci_workflows -v` | ✓ `scripts/tests/test_ci_workflows.py` |
| TOOL-05 | `affected.py` maps a diff (including widen-all and no-build-impact) | behavioral | `python3 -m unittest scripts.tests.test_affected -v` | ✓ existing |
| TOOL-06 | `gate` is literal, `needs` every PR job, and allows only `success`/`skipped` | text contract | `python3 -m unittest scripts.tests.test_ci_workflows -v` | ✓ |
| TOOL-06 | `pio run` vs `pio test -e native` split and the native test suite | behavioral (CI only) | CI `build` matrix; local `pio test -d tests -e native` | ✓ existing commands |
| TOOL-06 | Nightly runs the full matrix, no simulation | text contract | `python3 -m unittest scripts.tests.test_ci_workflows -v` | ✓ |
| SIM-04 | Same-repo + label guard, step-level token check, timeout, artifact upload, no status flip | text contract | `python3 -m unittest scripts.tests.test_ci_workflows -v` | ✓ |
| SIM-04 | The documented Wokwi command resolves its paths | behavioral | `python3 -m unittest scripts.tests.test_simulation_paths -v` (skips if `wokwi-cli` is absent) | ✓ existing |

---

## Wave 0 Requirements

- [x] Extend `scripts/tests/test_ci_workflows.py`: exactly two workflows, literal `gate`,
      `needs` coverage, `if: ${{ !cancelled() }}`, gitleaks command, `wokwi-cli lint`,
      `uv run scripts/affected.py --base`, the empty-matrix guard, the simulate guard and
      artifact upload, and the nightly widen-all invocation.
- [x] Move the `gen-views-check` assertion from the deleted `generated-views.yml` to
      `.pre-commit-config.yaml` (hook id) and/or the `pre-commit run --all-files` command in
      `ci.yml`.
- [x] Add a text assertion that `nightly.yml` has no simulation reference.
- [x] No framework install is needed (stdlib `unittest`).

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `gate` becomes the required status check in the GitHub ruleset | TOOL-06 | Rulesets are a GitHub-UI artifact per `AGENTS.md`; a required check must have passed within the last 7 days to appear in the picker | After the first green `ci.yml` run on a pull request, open Settings → Rules → `main` ruleset and add `gate` as the required status check (0 approvals). |
| Simulation consumes Wokwi free-tier quota only on an explicit label | SIM-04 | The token is a repository secret and the run is metered (~50 min / 30 days); a fork cannot apply the label | Apply the `simulate` label to one same-repo pull request that changes a simulated project; confirm the job runs, uploads `serial.log` and the duration/quota JSON, and consumes no quota when the label is absent. |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 60s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** 2026-10-26 — Nyquist audit: 9/9 tasks automated and green; 2 manual-only items
(the ruleset adoption and one labelled simulation run) tracked above.

## Validation Audit 2026-10-26

| Metric | Count |
|---|---|
| Gaps found | 0 |
| Resolved | 9 |
| Escalated | 2 |

---
phase: "8"
slug: "fast-ci"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
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
| **Estimated runtime** | ~38 seconds locally (380 tests) |

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

Populated by the planner/executor once task IDs exist. The phase-level requirement mapping is
the authoritative contract and is reproduced below.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD | TBD | TBD | TOOL-05 / TOOL-06 / SIM-04 | T-8-01 … T-8-SC | See threat model | text contract / behavioral | See table below | ✓ / ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| TOOL-05 | `meta` runs the hook surface, gitleaks full history, `wokwi-cli lint`, and the title check; `changes` emits both matrices | text contract | `python3 -m unittest scripts.tests.test_ci_workflows -v` | ✓ extend `scripts/tests/test_ci_workflows.py` |
| TOOL-05 | `affected.py` maps a diff (including widen-all and no-build-impact) | behavioral | `python3 -m unittest scripts.tests.test_affected -v` | ✓ existing |
| TOOL-06 | `gate` is literal, `needs` every PR job, and allows only `success`/`skipped` | text contract | `python3 -m unittest scripts.tests.test_ci_workflows -v` | ✓ extend |
| TOOL-06 | `pio run` vs `pio test -e native` split and the native test suite | behavioral (CI only) | CI `build` matrix; local `pio test -d tests -e native` | ✓ existing commands |
| TOOL-06 | Nightly runs the full matrix, no simulation | text contract | `python3 -m unittest scripts.tests.test_ci_workflows -v` | ✓ extend |
| SIM-04 | Same-repo + label guard, step-level token check, timeout, artifact upload, no status flip | text contract | `python3 -m unittest scripts.tests.test_ci_workflows -v` | ✓ extend |
| SIM-04 | The documented Wokwi command resolves its paths | behavioral | `python3 -m unittest scripts.tests.test_simulation_paths -v` (skips if `wokwi-cli` is absent) | ✓ existing |

---

## Wave 0 Requirements

- [ ] Extend `scripts/tests/test_ci_workflows.py`: three workflows, literal `gate`,
      `needs` coverage, `if: ${{ !cancelled() }}`, gitleaks command, `wokwi-cli lint`,
      `uv run scripts/affected.py --base`, the empty-matrix guard, the simulate guard and
      artifact upload, and the nightly widen-all invocation.
- [ ] Move the `gen-views-check` assertion from the deleted `generated-views.yml` to
      `.pre-commit-config.yaml` (hook id) and/or the `pre-commit run --all-files` command in
      `ci.yml`.
- [ ] Add a text assertion that `nightly.yml` has no simulation reference.
- [ ] No framework install is needed (stdlib `unittest`).

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `gate` becomes the required status check in the GitHub ruleset | TOOL-06 | Rulesets are a GitHub-UI artifact per `AGENTS.md`; a required check must have passed within the last 7 days to appear in the picker | After the first green `ci.yml` run on a pull request, open Settings → Rules → `main` ruleset and add `gate` as the required status check (0 approvals). |
| Simulation consumes Wokwi free-tier quota only on an explicit label | SIM-04 | The token is a repository secret and the run is metered (~50 min / 30 days); a fork cannot apply the label | Apply the `simulate` label to one same-repo pull request that changes a simulated project; confirm the job runs, uploads `serial.log` and the duration/quota JSON, and consumes no quota when the label is absent. |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

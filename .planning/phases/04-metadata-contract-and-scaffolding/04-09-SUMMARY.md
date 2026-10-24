---
phase: 04-metadata-contract-and-scaffolding
plan: 09
subsystem: infra
tags: [python, metadata, identity, symlink, filesystem, path-spelling, unittest]

requires:
  - phase: 04-metadata-contract-and-scaffolding
    provides: "the lexical identity helper and the symlinked-homeworks-base protection from 04-08"
provides:
  - "a spelling-independent id-equals-directory check that resolves only the ancestor prefix before homeworks"
  - "three identity regressions driven through the real CLI, including the alias spelling and a symlinked base beneath it"
  - "a WR-08 test that proves the allowlist actually suppresses a Cyrillic record while a shape violation stays rejected"
affects: [phase-05-generated-views, phase-08-ci, metadata-checker, homework-scaffolding]

actuals:
  tokens: 1845
  tasks: 2
  commits: 3
  plan_head_before: 0c301ffbfd6de337ac98e34768ca4406c59a1cd8
  plan_head_after: 9312ec39b22e49f68b5813fc27a3244e1eb82676

tech-stack:
  added: []
  patterns:
    - "Reconcile only the filesystem prefix a caller may spell differently; keep the identity-bearing tail lexical."
    - "Build a deterministic path-spelling difference with a symlink alias instead of relying on the host's /tmp layout."
    - "RED-first regressions recorded against the unmodified helper before the fix."

key-files:
  created: []
  modified:
    - scripts/metadata/contract.py
    - scripts/tests/test_homework_metadata.py

key-decisions:
  - "`_homework_directory` derives `parts = Path(os.path.abspath(path)).parts`, requires `parts[-3] == 'homeworks'` and `parts[-1] == 'homework.yaml'`, and returns `parts[-2]` unchanged."
  - "Only the ancestor prefix is reconciled: `Path(*parts[:-3]).resolve()` is compared with `Path(root).resolve()`, so `/tmp` versus `/private/tmp` no longer returns `None` while `homeworks/<dir>` stays lexical."
  - "The resolution boundary is exactly the `homeworks` component; neither the component, the containing directory nor the document is ever resolved, so T-04-27's symlinked-base protection composes with the spelling repair."
  - "The three regressions call `run_checker` directly because `run_fixture()` hardcodes `--dir str(self.root)` and passes no positional path."
  - "No change to `check_metadata.py`, `new_homework`, the schema, the templates, the golden trees or the 0/1/2 exit-code contract."

requirements-completed: [FOUND-01, META-01, META-04]

coverage:
  - id: D1
    description: "A mismatched id reached through an explicit absolute positional is an ERROR at exit 1 under both an alias spelling and the canonical spelling"
    requirement: META-01
    verification:
      - kind: unit
        ref: "scripts/tests/test_homework_metadata.py#IdentityTests.test_id_mismatch_holds_when_the_root_is_spelled_differently"
        status: pass
      - kind: command
        ref: "uv run scripts/check_metadata.py --dir /tmp/claude/verify04-09 /tmp/claude/verify04-09/homeworks/1_3-ctrl"
        status: pass
    human_judgment: false
  - id: D2
    description: "A matching id is still accepted under the same differing spelling, so the repair cannot pass by rejecting every spelling"
    requirement: META-01
    verification:
      - kind: unit
        ref: "scripts/tests/test_homework_metadata.py#IdentityTests.test_matching_id_is_accepted_when_the_root_is_spelled_differently"
        status: pass
    human_judgment: false
  - id: D3
    description: "A mismatched id through a symlinked homeworks base under a differently spelled root is still an ERROR at exit 1"
    requirement: META-01
    verification:
      - kind: unit
        ref: "scripts/tests/test_homework_metadata.py#IdentityTests.test_id_mismatch_survives_a_symlinked_base_under_a_differently_spelled_root"
        status: pass
    human_judgment: false
  - id: D4
    description: "The default scan and the pre-existing symlinked-base regression still reject a mismatched id, and the scaffold's rendered-id check still fires"
    requirement: META-04
    verification:
      - kind: unit
        ref: "scripts/tests/test_homework_metadata.py#IdentityTests.test_id_mismatch_survives_a_symlinked_homeworks_base"
        status: pass
      - kind: unit
        ref: "scripts/tests/test_new_homework.py#ErrorTests.test_mismatched_rendered_id_is_error"
        status: pass
    human_judgment: false
  - id: D5
    description: "The allowlist shape test now carries a Cyrillic word, so it fails if apply_allowlist is never invoked while the shape violation stays rejected"
    requirement: META-02
    verification:
      - kind: unit
        ref: "scripts/tests/test_homework_metadata.py#CyrillicGateTests.test_allowlisted_path_still_rejects_a_shape_violation"
        status: pass
    human_judgment: false

duration: 3 min
completed: 2026-10-24
status: complete
---

# Phase 4 Plan 9: Spelling-Independent Identity Check Summary

**Ancestor-only path resolution makes the `id`-equals-directory rule hold across `/tmp` versus `/private/tmp` spellings while the symlinked-base protection stays intact, pinned by three real-CLI regressions.**

## Performance

- **Duration:** 3 min
- **Started:** 2026-10-24T22:33:10Z
- **Completed:** 2026-10-24T22:36:08Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- `_homework_directory` no longer compares two independently capitalized spellings. It derives `parts` from `os.path.abspath(path)`, requires the `homeworks/<dir>/homework.yaml` shape, resolves only the ancestor prefix before `homeworks`, compares that with the resolved root, and returns `parts[-2]` unchanged. The id-equals-directory invariant therefore fires for an explicit absolute positional under any root spelling, while `homeworks` and everything below it stay lexical.
- Three `IdentityTests` regressions drive the real checker CLI (`run_checker`, not `run_fixture`, which hardcodes `--dir str(self.root)` and passes no positional): alias-spelling mismatch with a canonical control, matching-id acceptance under the alias, and a symlinked `homeworks` base under a differently spelled root. The spelling difference is a deterministic symlink alias, not a reliance on the host's `/tmp` layout.
- `CyrillicGateTests.test_allowlisted_path_still_rejects_a_shape_violation` now carries a Cyrillic word and a `source_url: not-a-url` shape violation in the same reviewed file. It asserts both records before the allowlist is written and asserts that `Cyrillic character` is absent afterwards while the URL error remains, so the test fails if `apply_allowlist` is never invoked (WR-08).
- The verifier's row-10 reproduction now returns the containing-directory ERROR at exit 1 under the non-canonical `/tmp` spelling, as does the canonical control and the default scan, while a matching id under the `/tmp` spelling exits 0.

## Task Commits

Each task was committed atomically, RED before GREEN:

1. **Task 1 RED: pin the id-match invariant across root spellings** — `131a673` (test)
2. **Task 1 GREEN: reconcile only the ancestor prefix in the id check** — `9e33238` (fix)
3. **Task 2: make the allowlist shape test exercise suppression** — `9312ec3` (test)

**Plan metadata:** `docs(04-09): complete spelling-independent identity plan` (this commit).

_Note: the RED commit carries the three failing regressions only; the GREEN commit carries the helper rewrite._

## RED Evidence (recorded before the fix)

| Test | Symptom on the unmodified helper |
|------|----------------------------------|
| `test_id_mismatch_holds_when_the_root_is_spelled_differently` (`spelling='alias'`) | Exit 0: `homeworks/1_3-good/homework.yaml: OK — metadata contract satisfied`, then `PASS: metadata contract satisfied`. No containing-directory ERROR. |
| `test_id_mismatch_holds_when_the_root_is_spelled_differently` (`spelling='canonical'`) | Already exit 1 before the fix; kept as the control that the repair neither over-rejects nor accepts only one spelling. |
| `test_matching_id_is_accepted_when_the_root_is_spelled_differently` | Already exit 0 before the fix; the acceptance control. |
| `test_id_mismatch_survives_a_symlinked_base_under_a_differently_spelled_root` | Exit 0: `homework.yaml: OK — metadata contract satisfied` and `PASS: metadata contract satisfied`. Both the identity check and the symlinked-base protection were lost. |

Observed RED run: `Ran 6 tests ... FAILED (failures=2)` — the two failing tests are the alias subTest of method 1 and method 3. After the fix the same command reports `Ran 6 tests ... OK`.

## Files Created/Modified

- `scripts/metadata/contract.py` — `_homework_directory` rewritten to a structural `parts` guard plus ancestor-only resolution; docstring states that the ancestor spelling is reconciled while the `homeworks/<dir>/homework.yaml` tail stays lexical and that the resolution boundary is exactly the `homeworks` component. No new import (`os` was already present), no signature change, no other function touched.
- `scripts/tests/test_homework_metadata.py` — `IdentityTests.test_id_mismatch_holds_when_the_root_is_spelled_differently`, `IdentityTests.test_matching_id_is_accepted_when_the_root_is_spelled_differently`, `IdentityTests.test_id_mismatch_survives_a_symlinked_base_under_a_differently_spelled_root`, and the strengthened `CyrillicGateTests.test_allowlisted_path_still_rejects_a_shape_violation`.

## Decisions Made

- The helper returns the directory name from the lexical `parts[-2]` rather than from any resolved path, which is the property that keeps T-04-27's symlinked-base protection intact while T-04-29's spelling reconciliation is added.
- The structural guard (`len(parts) >= 4`, `parts[-1] == "homework.yaml"`, `parts[-3] == "homeworks"`) replaces the prefix-slice comparison, so an unrelated path cannot be mistaken for a homework directory.
- The regressions use a symlink alias rather than the machine's `/tmp` layout, so the spelling difference is real on every platform and the test is not macOS-only.
- The WR-08 test asserts both the pre-allowlist presence and the post-allowlist absence of the Cyrillic record, which is the property that distinguishes "suppression happened" from "there was nothing to suppress".

## Deviations from Plan

**1. [Rule 3 - Blocking issue] Commit scopes use `04-09`, not the plan's literal `04`**
- **Found during:** Task 1 commit; repeated for all three task commits
- **Issue:** the plan names `test(04): ...` and `fix(04): ...`, while `AGENTS.md` requires the Conventional Commit scope to be the phase-plan (or homework) ID and the executor's repository rules mandate `04-09`. The previous plan's commits use the `04-08` scope.
- **Fix:** committed as `test(04-09)`, `fix(04-09)`, `test(04-09)`. Message bodies otherwise follow the plan.
- **Files modified:** none
- **Verification:** `git log --oneline -12` shows the three `04-09` commits alongside the earlier `04-08` commits.
- **Commit:** `131a673`, `9e33238`, `9312ec3`

**Total deviations:** 1 auto-fixed (1 blocking/rule-precedence). **Impact:** commit metadata only; no code, schema, contract or behaviour change.

## Issues Encountered

- The plan's `<automated>` names `scripts.tests.test_new_homework.DynamicTemplateTests.test_mismatched_rendered_id_is_error`, but the test is defined in `ErrorTests`. The plan-named command therefore raises `AttributeError: type object 'DynamicTemplateTests' has no attribute 'test_mismatched_rendered_id_is_error'`. The real test was run under its actual class name and passes. No code change was made for the naming discrepancy; 04-08 recorded the same defect.
- The sandbox denies writes to `uv`'s default cache (`~/.cache/uv`), so every checker invocation used `UV_CACHE_DIR=/private/tmp/claude/uv-cache-04`. No repository file or configuration was changed for this.
- `gsd_run` is unavailable in this execution environment, so STATE.md and ROADMAP.md updates are left to the orchestrator as instructed. The commit ledger could not be written inside `.git` from the agent sandbox; the base SHA is recorded in `actuals.plan_head_before` and the count was measured with `git rev-list --count <base>..HEAD` (3).
- The full-suite run emitted three non-fatal `deny network-outbound 185.199.110.153:80` sandbox notices while still reporting `Ran 310 tests ... OK`; no test failed and no host was required.
- The disposable `/tmp/claude/verify04-09` fixture could not be removed (`rm -rf` was denied by the permission gate). It is outside the repository, untracked and not referenced by any committed artifact.

## Threat Flags

None. The only new surface is the threat register's own T-04-29/T-04-30 mitigations; T-04-28 remains accepted debt and T-04-SC is unaffected because no dependency pin changed.

## Known Stubs

None.

## User Setup Required

None — no external service configuration required.

## Verification

| Command | Result |
|---------|--------|
| `python3 -m unittest scripts.tests.test_homework_metadata.IdentityTests -v` | `Ran 6 tests in 0.571s` — `OK` (3 pre-existing + 3 new; the plan requires at least 6) |
| `python3 -m unittest scripts.tests.test_homework_metadata -v` | `Ran 60 tests in 7.419s` — `OK` |
| `python3 -m unittest scripts.tests.test_new_homework.ErrorTests.test_mismatched_rendered_id_is_error -v` | `Ran 1 test in 0.421s` — `OK` |
| `python3 -m unittest scripts.tests.test_homework_metadata scripts.tests.test_new_homework -v` | `Ran 87 tests in 10.535s` — `OK` |
| `python3 -m unittest discover -s scripts/tests -v` | `Ran 310 tests in 74.649s` — `OK` (≥ 307 required) |
| `uv run scripts/check_metadata.py` | `PASS: metadata contract satisfied` |
| `python3 scripts/check_policy.py --check` | `PASS: live GitHub state matches the committed policy` |
| `python3 scripts/check_pr_templates.py` | `PASS: PR template contract satisfied` |
| `scripts/check_dependency_rule.py` | Not present in this repository; the dependency rule runs as the pre-commit `shared-library dependency rule` hook, which Passed |
| `pre-commit run --all-files` | All 8 hooks `Passed`; no hook rewrote a file |

Manual row-10 reproduction on a disposable root (`/tmp/claude/verify04-09`, `id: 9_9-other` in `homeworks/1_3-ctrl/`, then `id: 1_3-ctrl` for the acceptance control):

| Invocation | Observed |
|------------|----------|
| `--dir /tmp/claude/verify04-09 /tmp/claude/verify04-09/homeworks/1_3-ctrl` | Exit 1 — `homeworks/1_3-ctrl/homework.yaml: ERROR — id: '9_9-other' does not match the containing directory '1_3-ctrl'` |
| `--dir /private/tmp/claude/verify04-09 /private/tmp/claude/verify04-09/homeworks/1_3-ctrl` (canonical control) | Exit 1 — the same record |
| `--dir /tmp/claude/verify04-09` (default scan) | Exit 1 — the same record |
| `--dir /tmp/claude/verify04-09 /tmp/claude/verify04-09/homeworks/1_3-ctrl` with `id: 1_3-ctrl` | Exit 0 — `PASS: metadata contract satisfied` |

### Must-Have Truths

| Truth | Evidence |
|-------|----------|
| An explicit absolute positional under a spelling that differs from the resolved root is rejected at exit 1 with the containing-directory ERROR | Manual `/tmp` invocation above; `IdentityTests.test_id_mismatch_holds_when_the_root_is_spelled_differently` |
| A canonical-spelling control also exits 1, and a matching `id` under the differing spelling exits 0 | Manual canonical control (exit 1) and `/tmp` matching-id run (exit 0, `PASS`); methods 1 and 2 |
| A mismatched `id` through a symlinked `homeworks` base under a differently spelled root is still an ERROR at exit 1 | `IdentityTests.test_id_mismatch_survives_a_symlinked_base_under_a_differently_spelled_root` |
| The default scan and `test_id_mismatch_survives_a_symlinked_homeworks_base` still reject exactly as row 59 recorded | Manual default scan (exit 1); both tests pass unchanged |
| `_homework_directory` resolves only the ancestor prefix and returns `parts[-2]` lexically | `scripts/metadata/contract.py` lines 582–606: the only `.resolve()` calls are `ancestor.resolve()` and `Path(root).resolve()`; no `realpath`; `parts[-3]`, `parts[-2]` and `path` are never resolved |
| `validate_candidate` still reports the containing directory for a rendered scaffold target | `ErrorTests.test_mismatched_rendered_id_is_error` — 1 test OK |

## Next Phase Readiness

- The single failed truth in `04-VERIFICATION.md` (row 10) is closed: the invariant no longer depends on the caller's spelling of the root, and the symlinked-base protection still holds beneath a differing spelling.
- The WR-08 "insufficient assertions" warning is closed: the test now fails if the allowlist is never applied.
- No schema, template, golden tree, placeholder, CLI flag, exit code or write path changed. T-04-28 (TOCTOU before write) remains accepted debt from 04-08 and is untouched here.
- `04-VERIFICATION.md` row 10 and key-link row `validate_homework_text → containing homeworks/<dir>/` can be re-verified as VERIFIED/WIRED by the verifier.

---

*Phase: 04-metadata-contract-and-scaffolding*
*Completed: 2026-10-24*

## Self-Check: PASSED

- `scripts/metadata/contract.py` — FOUND
- `scripts/tests/test_homework_metadata.py` — FOUND
- Commit `131a673` (Task 1 RED) — FOUND, ancestor of HEAD
- Commit `9e33238` (Task 1 GREEN) — FOUND, ancestor of HEAD
- Commit `9312ec3` (Task 2) — FOUND, ancestor of HEAD
- All plan-level verification commands ran green: 310-test suite, focused 87-test pair, `uv run scripts/check_metadata.py`, `pre-commit run --all-files`
- `gsd_run check evaluation-scope` could not run (`gsd_run` is unavailable in this environment); the `git rev-list --count` ledger check above substitutes for it

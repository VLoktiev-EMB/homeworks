---
phase: "9"
slug: "agent-workflow-and-skills"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: validated
nyquist_compliant: false
wave_0_complete: true
created: "2026-10-26"
---

# Phase 9 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Python stdlib `unittest` (no third-party runner) |
| **Config file** | none — discovery by module path |
| **Quick run command** | `python3 -m unittest scripts.tests.test_gen_skills -v` |
| **Full suite command** | `python3 -m unittest discover scripts/tests` |
| **Hook check** | `pre-commit run gen-skills-check --all-files` |
| **Estimated runtime** | ~5 seconds for the generator suite; ~30 seconds for the full suite |

The CI `python-tests` job runs exactly `python -m unittest discover scripts/tests`
(`.github/workflows/ci.yml`), and the repository convention is that tests never import
`yaml` or `jsonschema` (`scripts/tests/temp_root.py`).

---

## Sampling Rate

- **After every task commit:** Run `python3 -m unittest scripts.tests.test_gen_skills -v`
  and `pre-commit run gen-skills-check --all-files`.
- **After every plan wave:** Run `python3 -m unittest discover scripts/tests`.
- **Before `/gsd-verify-work`:** Full suite must be green, `pre-commit run --all-files`
  green, and the dry-run transcript recorded.
- **Max feedback latency:** 30 seconds.

---

## Per-Task Verification Map

The plans assign no task-level IDs; each row is keyed by the plan and requirement whose
evidence it audits.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 09-01 | 09-01 | 1 | FLOW-01 | — | Seven skill directories at v0.1 with changelog and lessons | manual/review (D-18) | — | ✅ `09-DRY-RUN.md` | ⬜ manual-only |
| 09-01 | 09-01 | 1 | FLOW-01 | — | Mirror matches the canonical tree | smoke | `uv run scripts/gen_skills.py --check` | ✅ | ✅ green |
| 09-03 | 09-03 | 3 | FLOW-02 | — | Guided and one-shot intake covers all eight topics | manual dry run (D-22) | — | ✅ `09-DRY-RUN.md` Legs 1, 3 | ⬜ manual-only |
| 09-03 | 09-03 | 3 | FLOW-03 | — | Guided block loop pauses with the exact menu and deepens on request | manual dry run | — | ✅ `09-DRY-RUN.md` Leg 2 | ⬜ manual-only |
| 09-03 | 09-03 | 3 | FLOW-04 | — | Checkpoints after intake, code, report; guardrails always apply | manual dry run + JSON inspection | — | ✅ `09-DRY-RUN.md` Legs 1–3 | ⬜ manual-only |
| 09-03 | 09-03 | 3 | FLOW-05 | — | Conflicts and ambiguity produce a recorded recommendation | manual dry run + JSON inspection | — | ✅ `09-DRY-RUN.md` Leg 3 | ⬜ manual-only |
| 09-04 | 09-04 | 4 | FLOW-06 | — | A failing build is repaired at most twice, then escalated | manual dry run against a broken fixture | — | ✅ `09-DRY-RUN.md` Legs 4–5 | ⬜ manual-only |
| 09-05 | 09-05 | 5 | FLOW-07 | T-09-32 | `hw-flash` stops at confirmation and resolves the baud before the monitor | manual + unit | `python3 -m unittest scripts.tests.test_gen_views.SharedIniTests -v` | ✅ | ✅ green (automated part) |
| 09-11 | 09-11 | 1 | FLOW-07 | T-09-31 | Both announced capture commands carry `[--baud <n>]`; `_build_command` forwards `-e`/`-b` only when supplied | unit | `python3 -m unittest scripts.tests.test_serial_capture.BuildCommandTests scripts.tests.test_serial_capture.CliResultPayloadTests scripts.tests.test_serial_capture.AtomicLogWriteTests -v` | ✅ | ✅ green |
| 09-12 | 09-12 | 2 | FLOW-07 | T-09-30 | The credential scan matches ordinary password assignments and still refuses before any file exists | unit | `python3 -m unittest scripts.tests.test_serial_capture.CredentialScanTests -v` | ✅ | ✅ green |
| 09-13 | 09-13 | 3 | FLOW-07 | — | An invalid `--seconds` is a usage error before any monitor starts; the child is reaped on every exception path | unit | `python3 -m unittest scripts.tests.test_serial_capture.CliDurationTests scripts.tests.test_serial_capture.CaptureReapTests -v` | ✅ | ✅ green |
| 09-14 | 09-14 | 4 | FLOW-07 | T-09-40 | An identifier-suffixed credential (`{"secretKey": "hunter2"}`, `secret_key = hunter2`, `passwordHash: abcdef`, `SECRET_KEY = hunter2`) matches, and the pinned benign set still does not | unit | `python3 -m unittest scripts.tests.test_serial_capture.CredentialScanTests -v` | ✅ | ✅ green |
| 09-14 | 09-14 | 4 | FLOW-07 | T-09-40 | An identifier-suffixed credential refuses before the filesystem is touched: `CaptureFailed`, no log file, no `.skill-state` directory | end-to-end | `python3 -m unittest scripts.tests.test_serial_capture.CaptureAndStoreTests -v` | ✅ | ✅ green |
| 09-14 | 09-14 | 4 | FLOW-01 | — | The guardrails capture exception, the helper docstring and the generated mirror name the same suffix form | smoke | `uv run scripts/gen_skills.py --check` | ✅ | ✅ green |
| 09-17 | 09-17 | 1 | FLOW-07 | — | A space-separated compound credential (`SECRET KEY: hunter2`, `secret key = hunter2`, `Secret Key: hunter2`, `secret key: hunter2`, `SECRET KEY = hunter2`) matches, and every pinned benign negative still does not | unit | `python3 -m unittest scripts.tests.test_serial_capture.CredentialScanTests -v` | ✅ | ✅ green |
| 09-17 | 09-17 | 1 | FLOW-07 | T-09-40 | A space-separated compound credential refuses before the filesystem is touched: `CaptureFailed`, no log file, no `.skill-state` directory | end-to-end | `python3 -m unittest scripts.tests.test_serial_capture.CaptureAndStoreTests.test_a_space_separated_compound_credential_child_writes_nothing -v` | ✅ | ✅ green |
| 09-18 | 09-18 | 2 | FLOW-01 | — | The shared guardrails own the resolved-port rule and the compound-credential shape; the regenerated mirror matches the canonical tree | smoke | `uv run scripts/gen_skills.py --check` | ✅ | ✅ green |
| 09-18 | 09-18 | 2 | FLOW-01 | — | `hw-flash/SKILL.md` carries no normative restatement of the shared port rule while keeping every operational step | manual/review (D-18) | — | ✅ | ✅ green (review) |
| 09-01 | 09-01 | 1 | — | — | Frontmatter transform strips Claude-only keys, keeps the body, injects the banner | unit | `python3 -m unittest scripts.tests.test_gen_skills -v` | ✅ | ✅ green |
| 09-01 | 09-01 | 1 | — | — | Unknown frontmatter key exits 2 | unit | same | ✅ | ✅ green |
| 09-01 | 09-01 | 1 | — | — | `--check` reports MODIFIED/DELETED/ORPHAN and writes nothing | unit | same | ✅ | ✅ green |
| 09-01 | 09-01 | 1 | — | — | Two generator runs are byte-identical | unit | same | ✅ | ✅ green |
| 09-01 | 09-01 | 1 | — | — | Manifest entries are sorted, digest-correct, never list the manifest | unit | same | ✅ | ✅ green |
| 09-01 | 09-01 | 1 | — | — | `_shared/` is mirrored as files, not as a skill | unit | same | ✅ | ✅ green |
| 09-01 | 09-01 | 1 | — | — | Symlink at any component is refused with exit 2 | unit | same | ✅ | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

**Deliberate omission:** no test asserts the existence, version, required files, or stub
markers of the real skills. D-18 makes those review-enforced, and `261026-ky7` removed the
prose/doc-sync test class for the same reason. A planner that adds one would violate the
locked decision.

---

## Wave 0 Requirements

- [x] `scripts/tests/test_gen_skills.py` — the generator suite described above.
- [x] `scripts/tests/temp_root.py` — add `write_skills_root(base)`, a stdlib-only builder
      that writes a small canonical skill tree (two skills, one `_shared` file, one
      reference, one stub) so the tests never depend on the authored skills.
- [x] No framework install: the suite is stdlib-only.
- [x] The real-tree smoke test (`gen_skills.py --check`) cannot exist until Wave 1 writes
      the canonical tree; order the plans accordingly.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Seven skills at v0.1 with changelog and lessons | FLOW-01 | Skill prose is not machine-checked by decision D-18 | Read each `SKILL.md` frontmatter and the two companion files; confirm `metadata.version: "0.1"`. |
| Guided/one-shot intake covers eight topics | FLOW-02 | Question bank is prose; coverage is review-enforced | Follow `references/question-bank.md` and confirm all eight topics are reachable. |
| Guided block loop and "explain deeper" | FLOW-03 | Behaviour lives in model instructions | Run the D-22 dry run and record the pause menu and the deepening response. |
| Checkpoints and guardrails | FLOW-04 | Behaviour lives in model instructions | Inspect `.skill-state/<id>.json` after intake, code, and report; confirm the confirmation gates. |
| Conflict and ambiguity record | FLOW-05 | Behaviour lives in model instructions | Trigger one conflict in the dry run and confirm the recommended assumption is in the state file and the report. |
| Two-attempt build repair then escalation | FLOW-06 | Behaviour lives in model instructions | Inject three independent compile errors (`E1`, `E2`, `E3`, one in homework-local `lib/pattern/src/controller.c`) into a temporary copy of 1.3, so no single fix turns the build green; confirm exactly two repairs, the unresolved `E3`, an explanation, and a stop with no third edit. |
| Flash gate and stub markers | FLOW-07 | Hardware is unavailable; prose is review-enforced | Run `hw-flash` to the gate and decline; confirm four stubs carry `metadata.status: stub`. |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter — not set: FLOW-02…FLOW-06 are
      manual-only by design (D-22 dry-run transcript), so the phase is VALIDATED (PARTIAL)

**Approval:** validated (partial) — audit re-run 2026-10-27 after the gap-closure plans
09-11…09-14 and again after 09-17/09-18; eighteen automated rows green, seven manual-only rows
carried with their dry-run evidence, and one review-enforced row. The 09-14 rows cover T-09-40
end to end: the scan matches the identifier-suffixed forms and the refusal happens before any
log file or state directory exists. The 09-17 rows extend that to the space-separated compound
form (`SECRET KEY: hunter2`), and 09-18 keeps the shared guardrails the single owner of both the
resolved-port rule and the compound-credential shape while the regenerated mirror matches.

## Validation Audit 2026-10-26

| Metric | Count |
|---|---|
| Gaps found | 5 |
| Resolved | 0 |
| Escalated | 5 |

## Validation Audit 2026-10-27

| Metric | Count |
|---|---|
| Gaps found | 0 |
| Resolved | 0 |
| Escalated | 0 |

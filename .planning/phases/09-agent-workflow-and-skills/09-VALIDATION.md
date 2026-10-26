---
phase: "9"
slug: "agent-workflow-and-skills"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
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

Task IDs are assigned by the plans; this table is the requirement-level contract they must
instantiate.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD | TBD | 1 | FLOW-01 | — | Seven skill directories at v0.1 with changelog and lessons | manual/review (D-18) | — | ❌ review only | ⬜ pending |
| TBD | TBD | 1 | FLOW-01 | — | Mirror matches the canonical tree | smoke | `uv run scripts/gen_skills.py --check` | ❌ after the tree exists | ⬜ pending |
| TBD | TBD | 1 | FLOW-02 | — | Guided and one-shot intake covers all eight topics | manual dry run (D-22) | — | ❌ transcript | ⬜ pending |
| TBD | TBD | 1 | FLOW-03 | — | Guided block loop pauses with the exact menu and deepens on request | manual dry run | — | ❌ transcript | ⬜ pending |
| TBD | TBD | 1 | FLOW-04 | — | Checkpoints after intake, code, report; guardrails always apply | manual dry run + JSON inspection | — | ❌ transcript | ⬜ pending |
| TBD | TBD | 1 | FLOW-05 | — | Conflicts and ambiguity produce a recorded recommendation | manual dry run + JSON inspection | — | ❌ transcript | ⬜ pending |
| TBD | TBD | 1 | FLOW-06 | — | A failing build is repaired at most twice, then escalated | manual dry run against a broken fixture | — | ❌ transcript | ⬜ pending |
| TBD | TBD | 1 | FLOW-07 | — | `hw-flash` stops at confirmation; four stubs carry `metadata.status: stub` | manual dry run + review | — | ❌ transcript | ⬜ pending |
| TBD | TBD | 1 | — | — | Frontmatter transform strips Claude-only keys, keeps the body, injects the banner | unit | `python3 -m unittest scripts.tests.test_gen_skills -v` | ❌ Wave 0 | ⬜ pending |
| TBD | TBD | 1 | — | — | Unknown frontmatter key exits 2 | unit | same | ❌ Wave 0 | ⬜ pending |
| TBD | TBD | 1 | — | — | `--check` reports MODIFIED/DELETED/ORPHAN and writes nothing | unit | same | ❌ Wave 0 | ⬜ pending |
| TBD | TBD | 1 | — | — | Two generator runs are byte-identical | unit | same | ❌ Wave 0 | ⬜ pending |
| TBD | TBD | 1 | — | — | Manifest entries are sorted, digest-correct, never list the manifest | unit | same | ❌ Wave 0 | ⬜ pending |
| TBD | TBD | 1 | — | — | `_shared/` is mirrored as files, not as a skill | unit | same | ❌ Wave 0 | ⬜ pending |
| TBD | TBD | 1 | — | — | Symlink at any component is refused with exit 2 | unit | same | ❌ Wave 0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

**Deliberate omission:** no test asserts the existence, version, required files, or stub
markers of the real skills. D-18 makes those review-enforced, and `261026-ky7` removed the
prose/doc-sync test class for the same reason. A planner that adds one would violate the
locked decision.

---

## Wave 0 Requirements

- [ ] `scripts/tests/test_gen_skills.py` — the generator suite described above.
- [ ] `scripts/tests/temp_root.py` — add `write_skills_root(base)`, a stdlib-only builder
      that writes a small canonical skill tree (two skills, one `_shared` file, one
      reference, one stub) so the tests never depend on the authored skills.
- [ ] No framework install: the suite is stdlib-only.
- [ ] The real-tree smoke test (`gen_skills.py --check`) cannot exist until Wave 1 writes
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

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

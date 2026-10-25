---
phase: "5"
slug: "generated-views-and-documentation-site"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-10-25"
---

# Phase 5 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `unittest` (stdlib), discovered from the repository root |
| **Config file** | none — `python3 -m unittest discover -s scripts/tests -v` |
| **Quick run command** | `python3 -m unittest discover -s scripts/tests -v` |
| **Full suite command** | `python3 -m unittest discover -s scripts/tests -v` plus `uv run --with-requirements requirements-docs.txt mkdocs build --strict` |
| **Estimated runtime** | ~30 seconds (stdlib suite); docs build adds ~10 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python3 -m unittest discover -s scripts/tests -v`
- **After every plan wave:** Run the same suite plus `pre-commit run --all-files`
- **Before `/gsd-verify-work`:** Full suite green, `mkdocs build --strict` green, and `uv run scripts/gen_views.py --all --check` green on the real tree
- **Max feedback latency:** 60 seconds

---

## Per-Task Verification Map

Task IDs are filled by the planner; the requirement-level mapping below is the contract.

| Requirement | Plan | Wave | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|-------------|------|------|------------|-----------------|-----------|-------------------|-------------|--------|
| META-05 | TBD | TBD | — | Generated writes are confined to manifest-owned paths; `--check` never writes | unit (subprocess) | `python3 -m unittest scripts.tests.test_gen_views.IdempotencyTests -v` | ❌ W0 | ⬜ pending |
| META-05 | TBD | TBD | — | Drift detection fails closed on modified/deleted/orphan files | unit | `python3 -m unittest scripts.tests.test_gen_views.DriftTests -v` | ❌ W0 | ⬜ pending |
| META-05 | TBD | TBD | — | The committed manifest is in sync with the tree | unit | `python3 -m unittest scripts.tests.test_gen_views.ManifestTests -v` | ❌ W0 | ⬜ pending |
| META-05 | TBD | TBD | — | `--check` on the real tree exits 0 without mutating it | smoke | `python3 -m unittest scripts.tests.test_gen_views.RealTreeSmokeTest -v` | ❌ W0 | ⬜ pending |
| META-05 | TBD | TBD | — | Conflicting toolchain pins are refused, never picked arbitrarily | unit | `python3 -m unittest scripts.tests.test_gen_views.SharedIniTests -v` | ❌ W0 | ⬜ pending |
| META-06 | TBD | TBD | — | Fanout widens safely; `docs/` and `.planning/` are explicit no-build-impact paths | unit | `python3 -m unittest scripts.tests.test_affected.FanoutTests -v` | ❌ W0 | ⬜ pending |
| META-06 | TBD | TBD | — | Framework resolves through `extra_configs` + `extends` | unit | `python3 -m unittest scripts.tests.test_affected.FrameworkTests -v` | ❌ W0 | ⬜ pending |
| META-06 | TBD | TBD | — | A real git repo, commit, and diff produce the expected matrix | integration | `python3 -m unittest scripts.tests.test_affected.EndToEndTests -v` | ❌ W0 | ⬜ pending |
| META-07 | TBD | TBD | — | Workspace roots are exactly `repo`, `docs`, `lib`, `scripts` + every homework; paths ASCII | unit | `python3 -m unittest scripts.tests.test_gen_views.WorkspaceTests -v` | ❌ W0 | ⬜ pending |
| META-08 | TBD | TBD | — | Docs pins, generated `mkdocs.yml`, and vendored KaTeX agree | unit | `python3 -m unittest scripts.tests.test_docs_pins.PinConsistencyTests -v` | ❌ W0 | ⬜ pending |
| META-08 | TBD | TBD | — | All 24 KaTeX files exist and match `FILES.sha256` | unit | `python3 -m unittest scripts.tests.test_docs_pins.KatexVendoringTests -v` | ❌ W0 | ⬜ pending |
| META-08 | TBD | TBD | — | The site builds with warnings as errors | CI only | `uv run --with-requirements requirements-docs.txt mkdocs build --strict` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `scripts/tests/test_gen_views.py` — META-05, META-07
- [ ] `scripts/tests/test_affected.py` — META-06
- [ ] `scripts/tests/test_docs_pins.py` — META-08 pins and KaTeX checksums (the predecessor `test_metadata_deps.py` was deleted in `597bd7a`; this is a new file, not an extension)
- [ ] `scripts/tests/temp_root.py` — add `boards/`, `docs/`, `templates/views/` to the copied fixture paths
- [ ] `requirements-docs.txt` — `mkdocs==1.6.1`, `mkdocs-material==9.7.7`, `pymdown-extensions==12.3`

*If none: "Existing infrastructure covers all phase requirements."*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| GitHub Pages serves the deployed artefact | META-08 | Requires the repository's Pages environment and a merge to `main` | After merge, open the Pages URL and confirm the home page, one homework page, and the boards page render with KaTeX fonts |

*All other phase behaviors have automated verification.*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

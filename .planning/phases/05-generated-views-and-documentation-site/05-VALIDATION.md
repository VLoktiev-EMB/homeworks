---
phase: "5"
slug: "generated-views-and-documentation-site"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: validated
nyquist_compliant: true
wave_0_complete: true
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
| META-05 | 05-03 | 2 | T-5-07, T-5-08 | Generated writes are confined to manifest-owned paths; `--check` never writes | unit (subprocess) | `python3 -m unittest scripts.tests.test_gen_views.IdempotencyTests -v` | ✅ | ✅ green |
| META-05 | 05-03 | 2 | T-5-09, T-5-10 | Drift detection fails closed on modified/deleted/orphan files and never deletes an unowned path | unit | `python3 -m unittest scripts.tests.test_gen_views.DriftTests -v` | ✅ | ✅ green |
| META-05 | 05-03 | 2 | T-5-09 | The committed manifest is in sync with the tree and never lists itself | unit | `python3 -m unittest scripts.tests.test_gen_views.ManifestTests -v` | ✅ | ✅ green |
| META-05 | 05-03 | 2 | T-5-10 | `--check` on the real tree exits 0 without mutating it | smoke | `python3 -m unittest scripts.tests.test_gen_views.RealTreeSmokeTest -v` | ✅ | ✅ green |
| META-05 | 05-05 | 3 | T-5-15, T-5-16 | Conflicting toolchain pins are refused, never picked arbitrarily | unit | `python3 -m unittest scripts.tests.test_gen_views.SharedIniTests -v` | ✅ | ✅ green |
| META-06 | 05-04 | 2 | T-5-12, T-5-13 | Fanout widens safely; `docs/` and `.planning/` are explicit no-build-impact paths | unit | `python3 -m unittest scripts.tests.test_affected.FanoutTests -v` | ✅ | ✅ green |
| META-06 | 05-04 | 2 | T-5-13 | Framework resolves through `extra_configs` + `extends` | unit | `python3 -m unittest scripts.tests.test_affected.FrameworkTests -v` | ✅ | ✅ green |
| META-06 | 05-04 | 2 | T-5-11 | A real git repo, commit, and diff produce the expected matrix | integration | `python3 -m unittest scripts.tests.test_affected.EndToEndTests -v` | ✅ | ✅ green |
| META-07 | 05-05 | 3 | T-5-14 | Workspace roots are exactly `repo`, `docs`, `lib`, `scripts` + every homework; paths ASCII | unit | `python3 -m unittest scripts.tests.test_gen_views.WorkspaceTests -v` | ✅ | ✅ green |
| META-08 | 05-08 | 5 | T-5-23, T-5-24 | Docs pins, generated `mkdocs.yml`, and vendored KaTeX agree; the nav omits nothing | unit | `python3 -m unittest scripts.tests.test_docs_pins.PinConsistencyTests -v` | ✅ | ✅ green |
| META-08 | 05-06 | 1 | T-5-17 | All 24 KaTeX files exist and match `FILES.sha256` | unit | `python3 -m unittest scripts.tests.test_docs_pins.KatexVendoringTests -v` | ✅ | ✅ green |
| META-08 | 05-08 | 5 | T-5-22, T-5-23 | The site builds with warnings as errors | CI only | `uv run --with-requirements requirements-docs.txt mkdocs build --strict` | ✅ | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [x] `scripts/tests/test_gen_views.py` — META-05, META-07 (planned in 05-03, grown in 05-05, 05-07, 05-08)
- [x] `scripts/tests/test_affected.py` — META-06 (planned in 05-04)
- [x] `scripts/tests/test_platformio_readers.py` — the shared `extra_configs`/`extends`/`lib_deps` reader (planned in 05-01)
- [x] `scripts/tests/test_ci_workflows.py` — the LFS-pointer guard and workflow-shape assertions (planned in 05-09)
- [x] `scripts/tests/test_docs_pins.py` — META-08 pins and KaTeX checksums (planned in 05-06 and 05-08; the predecessor `test_metadata_deps.py` was deleted in `597bd7a`, so this is a new file, not an extension)
- [x] `scripts/tests/temp_root.py` — `write_synthetic_root`, a two-homework three-library builder that also writes the top-level `tests/` consumer, a marker-bounded `docs/index.md`, a board profile, and a `homeworks=False` mode; it does not copy the authored `docs/` tree (planned in 05-01)
- [x] `requirements-docs.txt` — `mkdocs==1.6.1`, `mkdocs-material==9.7.7`, `pymdown-extensions==12.3` (planned in 05-01)
- [x] Wave 0 production prerequisites: `scripts/metadata/paths.py` (stdlib-only path/identity helpers) and `scripts/metadata/yaml_loader.py` (the shared duplicate-key-rejecting loader), so the PyYAML-only generator gate never imports jsonschema (planned in 05-01)

*If none: "Existing infrastructure covers all phase requirements."*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| GitHub Pages serves the deployed artefact | META-08 | Requires the repository's Pages environment and a merge to `main` | After merge, open the Pages URL and confirm the home page, one homework page, and the boards page render with KaTeX fonts |

*All other phase behaviors have automated verification.*

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 60s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** validated 2026-10-26 — 11 of 12 mapped rows re-run green on the phase branch; the twelfth (`mkdocs build --strict`) was run green locally and is CI-only by design. One manual-only item: the Pages deploy.

## Validation Audit 2026-10-25

| Metric | Count |
|---|---|
| Gaps found | 0 |
| Resolved | 0 |
| Escalated | 0 |

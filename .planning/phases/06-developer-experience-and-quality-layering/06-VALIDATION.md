---
phase: "6"
slug: "developer-experience-and-quality-layering"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: validated
nyquist_compliant: true
wave_0_complete: true
created: "2026-10-26"
---

# Phase 6 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `unittest` (Python stdlib) — 339 tests in `scripts/tests/` |
| **Config file** | none — discovery from the repository root via `scripts/tests/` |
| **Quick run command** | `python3 -m unittest discover -s scripts/tests -v` |
| **Full suite command** | `python3 -m unittest discover -s scripts/tests && pio test -d tests -e native && pio test -d homeworks/1_3-police-flasher -e native && pre-commit run --all-files && uv run scripts/check_metadata.py && uv run scripts/gen_views.py --all --check && uv run --python 3.13 --with-requirements requirements-docs.txt mkdocs build --strict` |
| **Estimated runtime** | ~60 s (unit suite estimate — re-measure at Wave 0) |

Constraint inherited from 04/D-14: tests never import `yaml` or `jsonschema`. A test that
must parse `.pre-commit-config.yaml`, `homeworks.code-workspace` or `.vscode/settings.json`
either reads text or shells out to `uv run --with PyYAML==6.0.3`.

---

## Sampling Rate

- **After every task commit:** Run `python3 -m unittest discover -s scripts/tests -v`
- **After every plan wave:** Run the full suite command above
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 120 seconds

---

## Per-Task Verification Map

Task IDs are assigned by the planner; these rows are the requirement-level contract the
plans must bind to.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 06-01 T1 | 06-01 | 0 | TOOL-01 | — | — | unit (text) | `python3 -m unittest scripts.tests.test_tooling_config.ClangFormatConfigTests -v` | ✅ | ✅ green |
| 06-01 T2 | 06-01 | — | TOOL-01 | T-6-01 | — | gate | `pre-commit run clang-format --all-files` | ✅ hook | ✅ green |
| 06-04 T1 | 06-04 | 0 | TOOL-01 | T-6-07 | The guard exits non-zero and names the exact regeneration command; it never writes the database or skips silently | unit (subprocess) | `python3 -m unittest scripts.tests.test_tooling_config.ClangTidyDbGuardTests -v` | ✅ | ✅ green |
| 06-02 T1 | 06-02 | — | TOOL-02 | — | `.clangd` files are regular files in both templates; `new_homework` refuses symlinked template entries | unit | `python3 -m unittest scripts.tests.test_new_homework -v` | ✅ | ✅ green |
| 06-02 T1 | 06-02 | — | TOOL-02 | — | — | unit (text) | `python3 -m unittest scripts.tests.test_tooling_config.ClangdConfigTests -v` | ✅ | ✅ green |
| 06-02 T2 | 06-02 | — | TOOL-02 | T-6-02 | Wrapper rejects an unresolvable binary or a relative toolchain base with a named remedy instead of exec'ing a guess; `--query-driver` is a bounded glob list, never `**` | unit (subprocess, temp HOME) | `python3 -m unittest scripts.tests.test_tooling_config.ClangdWrapperTests -v` | ✅ | ✅ green |
| 06-02 T3 | 06-02 | — | TOOL-02 | T-6-03 | The editor contract carries no credential and the settings object is single-sourced in the generator | unit (json) | `python3 -m unittest scripts.tests.test_tooling_config.EditorContractTests -v` | ✅ | ✅ green |
| 06-04 T2 | 06-04 | — | TOOL-03 | T-6-05 | Hook stages are explicit; no hook rewrites or stages files; both push hooks share one widened `files` pattern | unit (text) | `python3 -m unittest scripts.tests.test_tooling_config.HookLayeringTests -v` | ✅ | ✅ green |
| 06-03 T2 | 06-03 | — | TOOL-03 | T-6-06 | No workflow file is edited; all four keep a top-level trigger key | unit (text) | `python3 -m unittest scripts.tests.test_ci_workflows -v` | ✅ | ✅ green |
| 06-05 T1 | 06-05 | — | TOOL-04 | T-6-09 | The nav entry lives in the generator template; the page is reachable on a strict build | unit + gate | `python3 -m unittest scripts.tests.test_docs_pins.PinConsistencyTests -v` | ✅ page | ✅ green |
| 06-05 T1 | 06-05 | — | TOOL-04 | — | — | gate | `uv run --python 3.13 --with-requirements requirements-docs.txt mkdocs build --strict` | ✅ workflow | ✅ green |
| 06-05 T3 | 06-05 | — | TOOL-04 | T-6-10 | The guide documents only pre-commit-delivered tools, the two-step symlink, and the hook installation | unit (text) | `python3 -m unittest scripts.tests.test_tooling_config.RulebookAndGuideTests -v` | ✅ | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [x] `scripts/tests/test_tooling_config.py` — `.clang-format` resolved invariants,
      `.clang-tidy` families, `.clangd` keys, hook layering, editor-contract equality
- [x] `scripts/tests/fixtures/golden/homework-{arduino,espidf}/.clangd` — golden fixtures
      for the scaffold drift guard
- [x] `scripts/clang-tidy-db` (the missing/stale-database guard) plus its unit test with a
      temporary root
- [x] `scripts/clangd-wrapper.sh` (mode 100755) plus a test that fakes `$ESP_CLANGD`
- [x] trigger-key assertions for all four `.github/workflows/*.yml` files in
      `scripts/tests/test_ci_workflows.py` (the yamllint policy must not rewrite them)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| clangd resolves ESP32-S3 includes inside a live VS Code instance | TOOL-02 | Needs a running editor with the clangd extension and a real `compile_commands.json`; not reproducible headlessly in this repository's suite | Generate the database with `pio run -d homeworks/1_3-police-flasher -t compiledb`, then run `"$HOME/.local/bin/clangd-wrapper" --check homeworks/1_3-police-flasher/src/main.cpp`. Expected: `All checks completed, 0 errors`, exit 0. A failure exits 3 and names either the unresolved include (`stdbool.h`, `stdint.h`) or the rejected Xtensa flag. Then open the workspace, open `src/main.cpp`, and confirm no squiggles and that "clangd: All checks completed" appears. |
| Format-on-save and the Problems panel behave for a beginner | TOOL-04 | The onboarding guide's acceptance is a human walkthrough | Follow `docs/standards/vscode.md` from a clean machine profile; confirm save reformats and the Problems panel is empty |
| No-hardware check path | TOOL-04 | Requires the native simulation path from Phase 7 | Follow the guide's no-hardware section; confirm it names a command that works on a machine with no board attached |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 120s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** validated 2026-10-26 — 12/12 automated rows green; 3 manual-only (live IDE, format-on-save, no-hardware path)

## Validation Audit 2026-10-26

| Metric | Count |
|---|---|
| Gaps found | 0 |
| Resolved | 0 |
| Escalated | 0 |

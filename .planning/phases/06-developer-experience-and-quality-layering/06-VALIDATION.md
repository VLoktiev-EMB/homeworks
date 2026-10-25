---
phase: "6"
slug: "developer-experience-and-quality-layering"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-10-26"
---

# Phase 6 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `unittest` (Python stdlib) — 279 test functions in 59 classes |
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
| TBD (plan time) | — | 0 | TOOL-01 | — | N/A | unit (subprocess) | `python3 -m unittest scripts.tests.test_tooling_config.ClangFormatConfigTests -v` | ❌ W0 | ⬜ pending |
| TBD (plan time) | — | — | TOOL-01 | — | N/A | gate | `pre-commit run clang-format --all-files` | ❌ hook | ⬜ pending |
| TBD (plan time) | — | 0 | TOOL-01 | — | N/A | unit (text) | `python3 -m unittest scripts.tests.test_tooling_config.ClangTidyConfigTests -v` | ❌ W0 | ⬜ pending |
| TBD (plan time) | — | — | TOOL-02 | — | `.clangd` files are regular files in both templates; `new_homework` refuses symlinked template entries | unit | `python3 -m unittest scripts.tests.test_new_homework -v` | ✅ | ⬜ pending |
| TBD (plan time) | — | — | TOOL-02 | — | N/A | unit (text) | `python3 -m unittest scripts.tests.test_tooling_config.ClangdConfigTests -v` | ❌ W0 | ⬜ pending |
| TBD (plan time) | — | — | TOOL-02 | T-6-?? (wrapper) | Wrapper rejects an unresolvable binary with a named remedy instead of exec'ing a guess; `--query-driver` is a bounded glob list, never `**` | unit (subprocess, temp HOME) | `python3 -m unittest scripts.tests.test_tooling_config.ClangdWrapperTests -v` | ❌ W0 | ⬜ pending |
| TBD (plan time) | — | — | TOOL-02 | — | N/A | unit (json) | `python3 -m unittest scripts.tests.test_tooling_config.EditorContractTests -v` | ❌ W0 | ⬜ pending |
| TBD (plan time) | — | — | TOOL-03 | — | Hook stages are explicit; no hook rewrites or stages files | unit (text) | `python3 -m unittest scripts.tests.test_tooling_config.HookLayeringTests -v` | ❌ W0 | ⬜ pending |
| TBD (plan time) | — | — | TOOL-03 | — | N/A | unit | `python3 -m unittest scripts.tests.test_tooling_config.HookLayeringTests -v` | ❌ W0 | ⬜ pending |
| TBD (plan time) | — | — | TOOL-04 | — | N/A | unit + gate | `python3 -m unittest scripts.tests.test_gen_views -v && uv run scripts/gen_views.py --all --check` | ❌ page | ⬜ pending |
| TBD (plan time) | — | — | TOOL-04 | — | N/A | gate | `uv run --python 3.13 --with-requirements requirements-docs.txt mkdocs build --strict` | ✅ workflow | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `scripts/tests/test_tooling_config.py` — `.clang-format` resolved invariants,
      `.clang-tidy` families, `.clangd` keys, hook layering, editor-contract equality
- [ ] `scripts/tests/fixtures/golden/homework-{arduino,espidf}/.clangd` — golden fixtures
      for the scaffold drift guard
- [ ] `scripts/clang-tidy-db` (the missing/stale-database guard) plus its unit test with a
      temporary root
- [ ] `scripts/clangd-wrapper.sh` (mode 100755) plus a test that fakes `$ESP_CLANGD`

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| clangd resolves ESP32-S3 includes inside a live VS Code instance | TOOL-02 | Needs a running editor with the clangd extension and a real `compile_commands.json`; not reproducible headlessly in this repository's suite | Open the workspace, `pio run -d homeworks/1_3-police-flasher`, open `src/main.cpp`, confirm no `esp_system.h`/`stdbool.h` squiggles and that "clangd: All checks completed" appears |
| Format-on-save and the Problems panel behave for a beginner | TOOL-04 | The onboarding guide's acceptance is a human walkthrough | Follow `docs/standards/vscode.md` from a clean machine profile; confirm save reformats and the Problems panel is empty |
| No-hardware check path | TOOL-04 | Requires the native simulation path from Phase 7 | Follow the guide's no-hardware section; confirm it names a command that works on a machine with no board attached |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 120s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

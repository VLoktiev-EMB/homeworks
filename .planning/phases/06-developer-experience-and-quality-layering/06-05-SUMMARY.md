---
phase: 06-developer-experience-and-quality-layering
plan: 05
subsystem: developer-tooling
tags: [vscode, clangd, clang-format, adr, mkdocs, onboarding, pre-commit]

# Dependency graph
requires:
  - phase: 06-developer-experience-and-quality-layering
    provides: the pinned formatter and check-only hook (06-01); the wrapper, `.clangd`, and editor contract (06-02); the lint policies (06-03); the clang-tidy pre-push layer and database guard (06-04)
provides:
  - "`docs/standards/vscode.md` as the beginner onboarding guide (TOOL-04)"
  - "the static `Standards` navigation section in `templates/views/mkdocs.yml.tmpl`"
  - "ADR 0012 (formatting approximation) and ADR 0013 (clangd multi-root contract), each indexed in `docs/decisions/README.md`"
  - "the `Quality tooling` rulebook section, the four-point enforcement vocabulary, and an onboarding routing row"
  - "`RulebookAndGuideTests` as the stdlib machine check for the rulebook and the guide"
affects: [phase-08-ci, phase-09-skills, phase-10-report-standards]

actuals:
  tokens: 9569
  tasks: 3
  commits: 3
  plan_head_before: 1f31f2de113c88c31e95a7afa53972ecba7a6d94
  plan_head_after: ecb12d794b1b268f107badf062e752cf65889fe5

tech-stack:
  added: []
  patterns:
    - "An authored page reaches the generated nav only through the view template, and the strict site build plus PinConsistencyTests prove the entry exists"
    - "An approximation is recorded as a decision instead of being renamed into an equivalence"
    - "A guide's required steps and forbidden install forms are asserted as command substrings and required terms, not full sentences"

key-files:
  created:
    - docs/standards/vscode.md
    - docs/decisions/0012-formatting-approximation.md
    - docs/decisions/0013-clangd-multi-root-contract.md
  modified:
    - templates/views/mkdocs.yml.tmpl
    - mkdocs.yml
    - generated.manifest
    - docs/decisions/README.md
    - AGENTS.md
    - scripts/tests/test_tooling_config.py

key-decisions:
  - "The guide states clang-format as an approximation of ESP-IDF's AStyle style, and ADR 0012 carries the same conclusion so the site and the decision record cannot disagree."
  - "ADR 0013 records the borrowed-translation-unit outcome of plan 06-04's header probe rather than claiming per-header analysis that the probe did not prove."
  - "The guide names no system package-manager install; every linter is delivered by a pinned pre-commit revision, and RulebookAndGuideTests asserts the forbidden forms are absent."
  - "The rulebook's enforcement vocabulary now has four points; `[ENFORCED: pre-push]` is the one the clang-tidy layer needed."

patterns-established:
  - "A guide step that mutates the developer machine is written as one exact command, and its prerequisite directory is part of the same command."
  - "A documentation contract is machine-checked by asserting required command substrings and the absence of forbidden install forms."
  - "An ADR body is historical once written; the decision table row is the mutable index."

requirements-completed: [TOOL-04]

coverage:
  - id: D1
    description: "docs/standards/vscode.md carries the beginner path from install to format-on-save, the Problems panel, clangd, and a no-hardware check, and the generated Standards nav makes it reachable on a strict site build"
    requirement: TOOL-04
    verification:
      - kind: unit
        ref: "scripts/tests/test_tooling_config.py#RulebookAndGuideTests"
        status: pass
      - kind: unit
        ref: "scripts/tests/test_docs_pins.py#PinConsistencyTests.test_nav_lists_every_markdown_file_under_docs"
        status: pass
      - kind: integration
        ref: "mkdocs build --strict"
        status: pass
    human_judgment: false
  - id: D2
    description: "ADR 0012 records the formatting approximation and ADR 0013 the esp-clangd and multi-root contract, both indexed in the decision table and emitted into the generated decision navigation"
    requirement: TOOL-04
    verification:
      - kind: integration
        ref: "uv run scripts/gen_views.py --all --check"
        status: pass
      - kind: unit
        ref: "scripts/tests/test_docs_pins.py#PinConsistencyTests"
        status: pass
      - kind: integration
        ref: "pre-commit run markdownlint-cli2 --all-files"
        status: pass
    human_judgment: false
  - id: D3
    description: "AGENTS.md carries the Quality tooling section, all four enforcement tags, the onboarding routing row, and the guide in its repository-layout list"
    requirement: TOOL-04
    verification:
      - kind: unit
        ref: "scripts/tests/test_tooling_config.py#RulebookAndGuideTests"
        status: pass
      - kind: integration
        ref: "python3 -m unittest discover -s scripts/tests (339 tests)"
        status: pass
      - kind: integration
        ref: "pre-commit run markdownlint-cli2 --all-files"
        status: pass
    human_judgment: false
  - id: D4
    description: "A beginner follows the guide from a clean machine profile to format-on-save and an empty Problems panel"
    requirement: TOOL-04
    verification: []
    human_judgment: true
    rationale: "The acceptance is a human walkthrough on a clean machine; RulebookAndGuideTests proves the required steps exist and the forbidden install forms do not, not that a beginner succeeds. The walkthrough is recorded as manual-only in 06-VALIDATION.md."

duration: 3min
completed: 2026-10-26
status: complete
---

# Phase 6 Plan 05: Onboarding Guide and Decision Records Summary

**A beginner VS Code guide reachable from the generated site navigation, the formatting-approximation and clangd multi-root decisions recorded and indexed, and a rulebook quality section machine-checked by RulebookAndGuideTests**

## Performance

- **Duration:** 3 min
- **Started:** 2026-10-26T11:15:38Z
- **Completed:** 2026-10-26T11:18:43Z
- **Tasks:** 3
- **Files modified:** 9 (3 created, 6 modified; 651 insertions, 6 deletions)

## Accomplishments

- `docs/standards/vscode.md` takes a reader from installing the two extensions through the one repository-specific machine step, `pre-commit install`, the compilation database, format-on-save, the Problems panel, and two commands that work with no board attached.
- The guide states the clang-tidy native-test-TU gap explicitly and defers simulation to Phase 7, so it claims neither analysis it does not perform nor a path that does not exist yet.
- The static `Standards` section in `templates/views/mkdocs.yml.tmpl` is the only route from the authored page to the generated `mkdocs.yml`; the strict build and `PinConsistencyTests` both pass with it.
- ADR 0012 records clang-format as a documented approximation of ESP-IDF's AStyle style; ADR 0013 records the wrapper resolution order, the two bounded `--query-driver` globs and their execution warning, the `BuiltinHeaders: QueryDriver` rationale and caveat, the multi-root settings-scope trap, the suppressed-diagnostic trade-off, the test-TU gap, and the port-header probe outcome.
- `AGENTS.md` gains a `Quality tooling` section, the fourth enforcement point `[ENFORCED: pre-push]`, an onboarding routing row, and the guide in its repository-layout list.
- `RulebookAndGuideTests` asserts the four tags, the guide's required command substrings and terms, every hook id, and the absence of `brew install`, `apt-get install`, `pip install --user`, and `npm install -g`.

## Task Commits

Each task was committed atomically:

1. **Task 1: An authored standards page reaches the built site end to end** - `9e22fae` (feat)
2. **Task 2: Record the two non-obvious decisions and index them in the decision table** - `8867bd8` (docs)
3. **Task 3: Rulebook quality section, four-point enforcement vocabulary, and machine checks** - `ecb12d7` (docs)

**Plan metadata:** committed separately (docs: complete plan summary).

## Files Created/Modified

- `docs/standards/vscode.md` — the onboarding guide: prerequisites, extensions, the symlink step, hook installation, the database command, format-on-save, the Problems panel, the no-hardware check, the hooks checklist, and the WSL note.
- `docs/decisions/0012-formatting-approximation.md` — the AStyle-versus-clang-format decision with the D-02 key list and the absence of `.editorconfig` and an AStyle check.
- `docs/decisions/0013-clangd-multi-root-contract.md` — the wrapper, query-driver, builtin-header, settings-scope, suppression, test-TU, and port-header record.
- `docs/decisions/README.md` — two rows dated 2026-10-26 with status `accepted` and links to both ADRs.
- `templates/views/mkdocs.yml.tmpl` — the static `Standards` navigation section.
- `mkdocs.yml` — regenerated with the `Standards` section and both decision entries.
- `generated.manifest` — regenerated hashes and byte counts for `mkdocs.yml`.
- `AGENTS.md` — the `Quality tooling` section, four enforcement tags, the layout entry, the routing row, and the narrowed "Planned" paragraph.
- `scripts/tests/test_tooling_config.py` — `RulebookAndGuideTests` with eight assertions.

## Decisions Made

- The guide is task-based and states its one repository-specific machine step as a single `mkdir -p … && ln -sf …` command, because the parent directory does not exist on a clean home.
- ADR 0013 records the port-header probe as a borrowed-translation-unit outcome and explicitly notes that a zero exit for a bare header does not prove the header was analysed; that proof is Phase 8 work.
- The rulebook's gitleaks bullet points at the existing `Secrets` section instead of restating it, keeping the new section free of duplicated rules.
- The "Planned" paragraph now names only report structure (Phase 10) and project skills (Phase 9), so `docs/standards/` is no longer described solely as future work.

## Deviations from Plan

None — plan executed exactly as written. No deviation rule was triggered.

## Issues Encountered

- Task 3 instructs the executor to "replace the previous assertion that the guide contains the substring `pip`". No such assertion existed: `RulebookAndGuideTests` is new in this plan, and a repository-wide search found only unrelated `pip` substrings in two test method names. The intent was applied by writing the positive `pre-commit install` assertion and the negative assertions for the four forbidden install forms. No production change.
- `uv run --with-requirements requirements-docs.txt mkdocs build --strict` created an ignored `.venv/` in the worktree and wrote the ignored `site/` directory. Neither is tracked; `git status` is clean after the commits.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- Success criterion 5 is met: the guide covers install, format-on-save, the Problems panel, clangd, and a no-hardware check, and the site navigation reaches it.
- Success criterion 1's documentation half is met: the approximation is recorded as an approximation in both ADR 0012 and the guide.
- TOOL-04 is machine-checked by `RulebookAndGuideTests` and the strict site build; the live beginner walkthrough remains the manual verification already listed in `06-VALIDATION.md`.
- Phase 8 inherits the native-test-TU gap and the per-header analysis question recorded in ADR 0013; Phase 10 inherits report-structure standards under `docs/standards/`.
- No blockers.

---

*Phase: 06-developer-experience-and-quality-layering*
*Completed: 2026-10-26*

## Self-Check: PASSED

- `docs/standards/vscode.md`, `docs/decisions/0012-formatting-approximation.md`, and `docs/decisions/0013-clangd-multi-root-contract.md` exist on disk.
- `9e22fae`, `8867bd8`, and `ecb12d7` are ancestors of `HEAD`.
- `python3 -m unittest discover -s scripts/tests` (339 tests), `pre-commit run --all-files`,
  `uv run scripts/gen_views.py --all --check`, `uv run scripts/check_metadata.py`,
  `mkdocs build --strict`, `pio test -d tests -e native` (73 cases),
  `pio test -d homeworks/1_3-police-flasher -e native` (38 cases), and
  `python3 scripts/check_architecture.py` all exited 0.

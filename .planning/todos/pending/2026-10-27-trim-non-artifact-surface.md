---
created: 2026-10-27T00:00:00.000Z
title: Remove dead code, config-text tests, and template build junk
area: tooling
severity: minor
source: .planning/notes/repo-surface-trim-2026-10-27.md
files:
  - scripts/ci/check_lfs_pointers.sh
  - scripts/review_smoke_test.sh
  - scripts/tests/test_tooling_config.py
  - scripts/tests/test_ci_workflows.py
  - .claude/skills/
  - templates/homework-espidf/
---

# Remove dead code, config-text tests, and template build junk

Confirmed scope on 2026-10-27. The maintainer keeps planning artifacts, every scaffold
and generator, and every linter and static-analysis tool. Only the four groups below are
removed.

## D1 — dead code

- [ ] Delete `scripts/ci/check_lfs_pointers.sh` (38 lines). It guards the GitHub Pages
      site removed in `9d28f5d`; no workflow, script, or document calls it.
- [ ] Delete `scripts/review_smoke_test.sh` (92 lines). It tests the GSD reviewer lanes,
      not repository code.

## D2 — tests that assert configuration text

- [ ] Delete `scripts/tests/test_tooling_config.py` (1,537 lines).
- [ ] Delete `scripts/tests/test_ci_workflows.py` (509 lines).

Accepted loss: automated coverage of `clangd-wrapper.sh` behaviour and of the
`pull_request_target` / `permissions: read` CI invariants. Both subjects themselves stay.

## D3 — skill process documents

- [ ] Delete `.claude/skills/*/CHANGELOG.md` and `.claude/skills/*/LESSONS.md` (14 files).
- [ ] Regenerate the mirror: `uv run scripts/gen_skills.py`, then commit the mirror diff.
      Without this step the `gen-skills-check` hook fails on drift.

## D4 — untracked build junk inside a template

- [ ] `rm -rf templates/homework-espidf/.pio templates/homework-espidf/.cache` (33 MB).
      Nothing here is tracked; the template itself stays.

## Verify

- [ ] `pio run -d homeworks/1_3-police-flasher` is green.
- [ ] `pio test -d tests -e native` is green.
- [ ] `pre-commit run --all-files` is green with all hooks and pins unchanged.
- [ ] `python3 scripts/check_metadata.py` and `python3 scripts/check_report.py` are green.
- [ ] `python3 -m unittest discover scripts/tests` is green.
- [ ] `uv run scripts/gen_skills.py --check` is green.
- [ ] No dangling references to the deleted paths.

## Explicitly out of scope

Do not remove `.planning/`, any generator or scaffold (`gen_views`, `gen_skills`,
`affected`, `new_homework`, `templates/`, `homeworks.code-workspace`), or any linter and
static-analysis tool (`clang-format`, `clang-tidy`, `ruff`, `yamllint`,
`check_architecture`). The maintainer confirmed all of these stay.

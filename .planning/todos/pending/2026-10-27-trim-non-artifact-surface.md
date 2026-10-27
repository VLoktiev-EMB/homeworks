---
created: 2026-10-27T00:00:00.000Z
title: Trim non-artifact surface — planning archive, generators, drift hooks, dead scripts
area: tooling
severity: major
source: .planning/notes/repo-surface-trim-2026-10-27.md
files:
  - .planning/
  - scripts/gen_views.py
  - scripts/gen_skills.py
  - scripts/affected.py
  - scripts/check_architecture.py
  - scripts/clang-tidy-db
  - scripts/clang-tidy-hook
  - scripts/gen_clangd_db.py
  - scripts/clangd-wrapper.sh
  - scripts/review_smoke_test.sh
  - scripts/ci/check_lfs_pointers.sh
  - .agents/skills/
  - templates/views/
  - templates/homework-espidf/
  - generated.manifest
  - generated.skills.manifest
  - homeworks.code-workspace
  - .pre-commit-config.yaml
  - .github/workflows/ci.yml
  - .github/workflows/nightly.yml
---

# Trim non-artifact surface

Apply `.planning/notes/repo-surface-trim-2026-10-27.md`. Three atomic commits. Do not
rewrite history; every step is a forward change.

## Commit 1 — `chore(planning): untrack process history`

- [ ] `git rm -r --cached .planning/phases .planning/quick .planning/research .planning/notes .planning/todos .planning/debug`
- [ ] Add those paths to `.gitignore`; keep `PROJECT.md`, `ROADMAP.md`, `REQUIREMENTS.md`, `STATE.md`, `config.json` tracked.
- [ ] Leave the files on disk so GSD continues to work locally.

## Commit 2 — `refactor(tooling): drop generators and drift gates`

- [ ] Delete `scripts/gen_views.py`, `scripts/gen_skills.py`, `scripts/affected.py`, `scripts/check_architecture.py`, `scripts/architecture/`, `scripts/ci/`, `scripts/clang-tidy-db`, `scripts/clang-tidy-hook`, `scripts/clangd-wrapper.sh`, `scripts/gen_clangd_db.py`, `scripts/review_smoke_test.sh`.
- [ ] Delete `templates/views/`, `.agents/skills/`, `generated.manifest`, `generated.skills.manifest`, `homeworks.code-workspace`, `templates/homework-espidf/`, and the `.clangd` files.
- [ ] Remove the generated-header from `platformio.shared.ini`; it becomes authored.
- [ ] Delete `scripts/tests/test_gen_views.py`, `test_gen_skills.py`, `test_affected.py`, `test_tooling_config.py`; trim `temp_root.py` and `test_ci_workflows.py` to what survives.
- [ ] Remove the six custom hooks from `.pre-commit-config.yaml`: `no-generated-files`, `check-architecture`, `gen-views-check`, `gen-skills-check`, `clang-tidy-db`, `clang-tidy`; drop the pre-push stage.
- [ ] Remove CI job `changes` and `static-analysis`; `build` runs every project. Reduce `nightly.yml` to the secrets scan plus the full build.
- [ ] Keep `check_metadata` and `check_report` hooks; add a one-line grep for the dependency rule if desired.

## Commit 3 — `docs: record the trim and shrink the rulebook`

- [ ] Update `AGENTS.md`: remove the routing rows and rules for deleted paths; replace the 313-line rulebook with the surviving rules; keep the quick-start and Definition of Done.
- [ ] Update `README.md`: the homework table is hand-maintained.
- [ ] Mark the three reversed decisions in `docs/decisions/README.md` (generator, architecture check, second template) with a `superseded 2026-10-27` status and a link to the note. Do not rewrite ADR bodies.
- [ ] Set `graphify.enabled` and `intel.enabled` to `false` in `.planning/config.json`.

## Verify

- [ ] `pio run -d homeworks/1_3-police-flasher` is green.
- [ ] `pio test -d tests -e native` is green.
- [ ] `pre-commit run --all-files` is green with the trimmed hook set.
- [ ] `python3 scripts/check_metadata.py` is green.
- [ ] `python3 scripts/check_report.py` is green.
- [ ] No dangling references to deleted paths in `README.md`, `AGENTS.md`, `docs/`, `.github/`, or the skills.
- [ ] CI `gate` is green on the pull request with 4 jobs.

## Out of scope

Do not touch `lib/`, `tests/`, the schema, the report contract, or the surviving skills.
Those are the artifact path and are explicitly kept.

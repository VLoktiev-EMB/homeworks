---
title: Repository surface trim — keep only what directly affects the homework artifact
date: 2026-10-27
context: Repository-wide exploration two phases after the 2026-10-25 ceremony trim; measures the remaining non-artifact surface and reverses three lines of the earlier decision
---

# Repository surface trim

## Problem

Measured on 2026-10-27, with one homework in the repository and 26 commits of history:

| Metric | Value |
|---|---|
| Tracked files | 625 |
| Of them `.planning/` | 388 (62%), 355 markdown, ~17 MB |
| Homeworks | 1 (`1_3-police-flasher`) |
| Tooling (Python + shell, no tests) | 7,345 lines |
| Tooling tests | 9,526 lines |
| pre-commit hooks | 16 |
| CI jobs | 7 |
| Generators | 2 (`gen_views.py` 1,134 + `gen_skills.py` 926) |

The test suite is larger than the tooling it tests, and the planning archive is the
largest single body of tracked content. Most of this surface does not produce a homework;
it polices other files.

## Criterion

The 2026-10-25 note cut by **recurring cost**. This pass adds a narrower question, because
the maintainer's stated goal is speed of adding the next homework:

> Does this file directly affect the homework artifact — code, build, tests, wiring,
> report, or evidence?

If it only checks, generates, or narrates other files, it is non-artifact surface. Sunk
cost is not a reason to keep it; the same rule as the earlier note.

## Delete — non-artifact surface

| # | Path | Size | Why |
|---|---|---|---|
| 1 | `.planning/phases/`, `quick/`, `research/`, `notes/`, `todos/`, `debug/` | 355+ md, ~17 MB | Process history, not a homework. Keep `PROJECT.md`, `ROADMAP.md`, `REQUIREMENTS.md`, `STATE.md`, `config.json` |
| 2 | `scripts/gen_skills.py`, `.agents/skills/`, `generated.skills.manifest` | 926 lines + 25 files | Mirror for agents this repository does not use |
| 3 | `scripts/gen_views.py`, `templates/views/`, `generated.manifest`, `homeworks.code-workspace` | 1,134 lines + manifest | Generates three small files. `platformio.shared.ini` becomes hand-written; the README table is one row |
| 4 | `scripts/affected.py`, CI job `changes`, `test_affected.py` | 572 + 506 lines | Change matrix for one project; building everything costs the same |
| 5 | `scripts/check_architecture.py`, `scripts/architecture/allowlist.json`, its hook | 663 lines | Rule over four small libraries; a one-line grep or review |
| 6 | `scripts/clang-tidy-db`, `scripts/clang-tidy-hook`, pre-push stage, CI job `static-analysis` | 388 lines, 2 hooks | Analyses four C files; contributes nothing to the report |
| 7 | `scripts/gen_clangd_db.py`, `scripts/clangd-wrapper.sh`, `.clangd` | 378 lines | Editor IntelliSense wiring; does not affect the build |
| 8 | `scripts/review_smoke_test.sh` | 92 lines | Tests the reviewers, not the code |
| 9 | `scripts/ci/check_lfs_pointers.sh` | ~100 lines | Guards the documentation site removed in `9d28f5d` |
| 10 | `templates/homework-espidf/` | 10 files | Unused by any homework |
| 11 | `test_tooling_config.py`, `test_gen_views.py`, `test_gen_skills.py`, `test_affected.py` | 4,147 lines | Tests for the deleted tooling |
| 12 | `graphify` and `intel` config, `.planning/graphs/` | 15 MB | Generated, unread in daily work |
| 13 | `CHANGELOG.md` / `LESSONS.md` inside each skill (16 files) | — | Process artifacts; `SKILL.md` and `references/` remain |

## Keep — direct effect on the artifact

- `lib/`, `tests/`, `partitions/`, `boards/`, `platformio.shared.ini` (hand-written)
- `schema/`, `scripts/check_metadata.py`, `scripts/metadata/*`
- `scripts/check_report.py`, `scripts/report/*`, `docs/standards/report.md`,
  `docs/standards/electrical-calculations.md`
- `scripts/new_homework`, `templates/homework-arduino/`
- `scripts/pio/compiledb.py`, `scripts/pio/merge_firmware.py` (both run on every build)
- `scripts/serial_capture.py`, `scripts/gen_schematic.py` (evidence and schematic)
- `scripts/tag_homework.sh`
- Six skills: `hw-build`, `hw-flash`, `hw-report`, `simulate`, `schematic`, `new-homework`
- pre-commit: 10 standard hooks, 2 custom (`check-metadata`, `check-report`)
- CI: `meta`, `build`, `python-tests`, `gate` (4 jobs; `simulate` stays optional)

## Decisions reversed by this note

The earlier record is not rewritten; these lines are superseded here.

1. **`gen_views` kept.** The 2026-10-26 revisit kept the generator for three views "with
   the manifest, `--check`, the pre-commit hook". Reversed: the recurring cost is a
   per-change drift hook, a regeneration step, a 1,134-line generator and 1,002 lines of
   tests for three files that change only when a homework is added.
2. **`check_architecture` kept.** Phase 4.1 kept the checker with its allowlist for a
   later reduction. Reversed: reduce to a grep now; the rule is four lines of policy.
3. **Both homework templates kept.** Phase 4.1 kept the Arduino and ESP-IDF templates.
   Reversed for the unused one: an ESP-IDF template returns when the first ESP-IDF
   homework is scheduled.

## Expected result

| Metric | Now | After |
|---|---|---|
| Tracked files | 625 | ~190 |
| Tooling lines | 7,345 | ~3,100 |
| Tooling-test lines | 9,526 | ~4,500 |
| Custom hooks | 6 | 2 |
| CI jobs | 7 | 4 |

## Trade-offs, stated honestly

- The README table and `platformio.shared.ini` are edited by hand when a homework is
  added. That is one edit in three places per homework, against a per-change drift gate.
- The dependency rule is enforced by review, not automatically.
- A fresh clone has no phase history. The local directory keeps it.
- Editor IntelliSense under `lib/` gets weaker. `compile_commands.json` per project still
  exists, so a per-project editor setup is unaffected.

## Re-entry triggers

Restore a piece only when its cost becomes recurring again:

1. `affected.py` and the `changes` job — five or more projects, when building everything
   no longer fits the CI budget.
2. `gen_views` — ten or more homeworks, when hand-maintaining the index and the shared ini
   actually drifts.
3. clangd multi-root wiring — when `lib/` is edited daily rather than per phase.
4. ESP-IDF template — when the first ESP-IDF homework is scheduled.

## Relation to the earlier note

`.planning/notes/ceremony-vs-engineering-principle.md` remains the principle: cut by
recurring cost, keep engineering that protects the artifact. This note applies the
principle to the surface built in Phases 5–10 and records where it now disagrees with
that note's 2026-10-26 inventory.

## Outcome — what was actually executed

The maintainer reviewed the inventory and narrowed it before execution. The large
"Delete — non-artifact surface" table above is the **analysis**, not the decision. The
decision is:

- **Kept:** every `.planning/` artifact; every generator and scaffold (`gen_views`,
  `gen_skills`, `affected`, `new_homework`, `templates/`, `homeworks.code-workspace`);
  every linter and static-analysis tool (`clang-format`, `clang-tidy`, `ruff`,
  `yamllint`, `check_architecture`); every pre-commit hook and CI job.
- **Removed** (quick task `261027-vxo`, commits `61c0100` and `0bf6120`):
  - `scripts/ci/check_lfs_pointers.sh` — guarded the removed documentation site.
  - `scripts/review_smoke_test.sh` — tested the reviewers, not the code.
  - `scripts/tests/test_tooling_config.py` (1,537 lines) and
    `scripts/tests/test_ci_workflows.py` (509 lines) — configuration-text assertions.
  - 14 `.claude/skills/*/CHANGELOG.md` and `LESSONS.md` files, plus the prose pointers
    to them; the `.agents/skills` mirror was regenerated (25 → 11 manifest entries).
  - `templates/homework-espidf/.pio` and `.cache` — 33 MB of untracked build output.

Measured result: 43 files changed, 3,080 deletions, **597 tracked files**, 397 stdlib
tests OK (skipped=1), 73/73 native cases, 14/14 pre-commit hooks, `pio run` and both
contract checkers green. The remaining 9.7 MB file
`templates/homework-espidf/compile_commands.json` is untracked and was left for a
separate decision.

Do not read the table above as a mandate to delete the kept items. It records what was
considered; this section records what was done.

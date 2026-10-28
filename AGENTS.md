# AGENTS.md

Canonical rulebook for every agent that works in this repository. Tool-specific adapters
import this file instead of copying it — `.claude/CLAUDE.md` is one such adapter. If an
adapter and this file disagree, this file wins.

## Project

A public GitHub monorepo of independent PlatformIO homework projects for an embedded
engineering course. Each homework ships as a self-contained engineering artifact — code,
tests, an academic report, wiring, a bill of materials, calculations, and measured evidence
— understandable and verifiable a year later. Repository artifacts are English; conversation
with the user follows the user's language.

## Agent quick-start

Run from the repository root, in this order, before opening a pull request.

| Step | Command | Purpose |
|------|---------|---------|
| 1 | `pio run -d <project>` | Build the affected PlatformIO environment from its own project directory. |
| 2 | `pio test -d tests -e native` | Run the shared-library Unity suite from the top-level `tests/` project, without a target toolchain. |
| 3 | `pre-commit run --all-files` | Run the local gate — hygiene, large files, secrets, format, and the metadata contract. |
| 4 | `uv run scripts/check_metadata.py` | Validate homework metadata and task provenance against `schema/homework.schema.json`. |
| 5 | `python3 -m unittest discover scripts/tests` | Run the Python suite that the CI `python-tests` job runs. |

## Repository layout

Present today: this rulebook, `README.md`, one MIT `LICENSE`, `.gitignore`, `.gitattributes`,
`.pre-commit-config.yaml`, and the paths below.

- `.github/pull_request_template.md` — the single pull-request template.
- `.github/workflows/ci.yml` — the pull-request gate: `meta`, `changes`, `build`,
  `python-tests`, `static-analysis`, `simulate` and `gate`.
- `.github/workflows/nightly.yml` — the scheduled full build and native-test matrix plus the
  full-history secret scan.
- `.agents/standards/` — engineering standards: `report.md`, `electrical-calculations.md`, and `vscode.md`.
- `.agents/standards/vscode.md` — the VS Code onboarding guide, from install to the
  no-hardware check.
- `boards/` — one YAML profile per board, validated by the same metadata checker.
- `scripts/` — deterministic checks and the tag script; `scripts/tests/`
  — the test suite.
- `schema/` — `homework.schema.json`, the JSON Schema 2020-12 metadata contract.
- `templates/` — the scaffolding source, rendered only by `scripts/new_homework`.
- `lib/` — `port`, `common`, `host`, and the thin Arduino and ESP-IDF adapters.
- `homeworks/<id>/` — one project per assignment, created only by `scripts/new_homework`.
- `.agents/skills/` — the canonical authored skills, each with `SKILL.md` and optional
  `references/`, plus `_shared/guardrails.md`.
- `.claude/skills` — symlink to `.agents/skills/` for tool compatibility.

`site/` and `.pio/` are build output and stay ignored.

`scripts/affected.py` maps a diff to the build matrix: a change under `homeworks/`, `lib/`,
`platformio.shared.ini`, `partitions/`, `scripts/pio/` or `schema/` selects projects, an
explicit no-build-impact set (`.planning/`, `docs/`, `.github/`, `.claude/`, `.agents/`,
`boards/`, `.skill-state/`, `homeworks.code-workspace`, and `scripts/serial_capture.py`)
selects nothing, and any unrecognised path widens to every project.

`ci.yml`'s `changes` job consumes its `{build, simulate}` payload as the build and simulation
matrix, and `nightly.yml` feeds the mapper the `platformio.shared.ini` path so the mapper's
own widen-all rule produces the full matrix.

The GitHub Pages source is set to `None` by the maintainer; the repository publishes no
site, and the authored documents render in the repository view.

The live skills layout is `.claude/skills/<name>/SKILL.md` — the canonical authored tree —
with `.agents/skills/` as its generated, committed mirror. `scripts/gen_skills.py` is the
only writer of the mirror; `uv run scripts/gen_skills.py --check` and the
`gen-skills-check` pre-commit hook are the drift gate.

## Definition of Done

A homework is done when:

1. `pio run` is green for its target environment.
2. `pio test -e native` is green when the homework contains pure logic.
3. `task.md`, `homework.yaml`, `README.md`, and `report.md` exist, and metadata validation passes.
4. The pull request is merged and tagged `hw/<id>`.

## Rules

Every rule carries two dimensions: severity (`[MUST]` or `[SHOULD]`) and where a violation is
caught (`[ENFORCED: pre-commit]`, `[ENFORCED: pre-push]`, `[ENFORCED: CI]`, or
`[ENFORCED: review]`). No `[MAY]`, no `[INFO]`.

### Change workflow

- **[MUST]** **[ENFORCED: review]** Choose the lightest GSD tier that fits: `/gsd-fast`
  for a trivial edit (at most three file edits, under a minute, reversible, no research),
  `/gsd-quick` for a known multi-step change, and the phase workflow for architectural work
  or homework delivery. Judgment at the boundary is allowed; the rule is proportional. GSD
  is portable: Antigravity runs the same `/gsd-*` commands.
- **[MUST]** **[ENFORCED: review]** Every change is one atomic commit: verified, with no
  unrelated work in the same commit.
- **[MUST]** **[ENFORCED: review]** Commit messages follow Conventional Commits
  `type(scope): summary`, with `type` one of `feat`, `fix`, `test`, `refactor`, `perf`,
  `docs`, `style`, or `chore`, and `scope` the phase-plan or homework ID.
- **[SHOULD]** **[ENFORCED: review]** Prefer one logical change per pull request; split a
  change when its description needs an "and".

Highest-risk example — the commit message:

```text
Bad:   updated stuff
Good:  feat(1_3): add police flasher state machine
```

### Git, branches, and history

- **[MUST]** **[ENFORCED: CI]** Never push directly to the default branch and never
  force-push. Every change arrives through a branch and a pull request. The `main` ruleset
  rejects the write server-side; the ruleset itself is maintained in the GitHub UI.
- **[MUST]** **[ENFORCED: CI]** Published history is never rewritten: no rebase of a shared
  branch, no history edit, no tag move. The ruleset requires linear history, so squash-merge only.
- **[MUST]** **[ENFORCED: review]** Squash-only applies to merges **into the default
  branch**; repository-level merge and rebase stay enabled for feature branches.
- **[MUST]** **[ENFORCED: review]** Branch names use the anchors `hw/<id>` for a homework
  and `docs/<slug>` for documentation. Every other prefix is free-form.

### Homework identifiers

- **[MUST]** **[ENFORCED: review]** A homework ID matches `^[0-9]+_[0-9]+-[a-z0-9-]+$` —
  the `module_lesson-name` form, for example `1_3-police-flasher`. It is a path segment and
  is stable after publication. An empty ID, a separator-less name such as `police-flasher`,
  and a mixed-case name are invalid. The schema enforces the pattern and the checker
  requires the directory name to match the document's `id`.
- **[MUST]** **[ENFORCED: review]** Homework IDs and paths are ASCII-only (`[a-z0-9_.-]`).
  Display names in a report may use emoji and non-ASCII text, but paths and identifiers
  stay ASCII so byte length and codepoint length never diverge.

### Metadata and provenance

- **[MUST]** **[ENFORCED: pre-commit]** Every homework carries `homework.yaml` and
  `task.md`, validated by `scripts/check_metadata.py` against `schema/homework.schema.json`.
  The schema rejects an unknown key at any depth, so a new field is a schema change.
- **[MUST]** **[ENFORCED: review]** A homework directory is created only through
  `scripts/new_homework <id> --template <name>`. There is no overwrite path: a second run
  is `UNCHANGED`, and any other existing content is a conflict that writes nothing.
- **[MUST]** **[ENFORCED: pre-commit]** Provenance is captured at collection time in
  `task.md` frontmatter: `source_url`, `retrieved`, `attribution`, `license`. The sentinel
  `TODO` is legal there and in `homework.yaml` `source.reference` only while status is
  `planned`; later statuses need the real value, and body `TODO`s are manual-review signals.
- **[MUST]** **[ENFORCED: pre-commit]** The Unicode-name Cyrillic scan rejects Cyrillic
  text in an authored `task.md`; there is no per-path allowlist, so an exception edits text.

### Reports and evidence

- **[SHOULD]** **[ENFORCED: review]** A report follows the structure in
  `.agents/standards/report.md`, with honest evidence labels (`measured`, `calculated`,
  `simulated`, `datasheet`, `not measured`).

### Pull requests and tags

- **[MUST]** **[ENFORCED: review]** Open every pull request through the single default
  template at `.github/pull_request_template.md`; it carries the Definition of Done rather
  than a type chooser.
- **[MUST]** **[ENFORCED: CI]** The single required status check is the literal `gate` job,
  which aggregates every pull-request job. Renaming it requires the ruleset change in the
  same pull request.
- **[MUST]** **[ENFORCED: review]** Create the `hw/<id>` tag only through
  `scripts/tag_homework.sh <id>`, after the homework pull request is merged. Never create a
  tag by hand and never move a published tag; a forced update is forbidden.

### Secrets

- **[MUST]** **[ENFORCED: pre-commit]** gitleaks must pass. The local hook scans staged
  changes, `ci.yml`'s `meta` job scans the pull-request commit range on every pull request, and
  `nightly.yml`'s `secrets` job repeats the full-history scan on the default branch every night,
  replacing the retired secret-scan workflow. A red secret scan blocks the change.
- **[MUST]** **[ENFORCED: review]** A real secret triggers, in this order: rotate the
  credential first, assess exposure, remove it with a forward fix, and document the
  incident. Never rewrite history to remove it — rotation is the only real mitigation once
  a secret has reached a public repository.
- **[SHOULD]** **[ENFORCED: review]** Treat the scanner as pattern-based, not exhaustive.
  Widening the ruleset is a Phase 6 decision made in the open through `.gitleaks.toml`,
  never an allowlist relaxation added quietly.

### Quality tooling

- **[MUST]** **[ENFORCED: pre-commit]** C/C++ is formatted by the committed `.clang-format`,
  and the pinned hook runs it in check-only form (`--dry-run --Werror`): it reports and never
  rewrites.
- **[MUST]** **[ENFORCED: pre-commit]** Python and authored YAML are linted by ruff and
  yamllint from their committed policies (`pyproject.toml`, `.yamllint.yaml`).
- **[MUST]** **[ENFORCED: pre-commit]** The secret gate is gitleaks; see "Secrets" above.
- **[SHOULD]** **[ENFORCED: review]** An editor is configured from `.agents/standards/vscode.md`,
  not from ad-hoc settings.

### Simulation

- **[SHOULD]** **[ENFORCED: CI]** Simulation runs only when a pull request changes a project,
  a maintainer applies the `simulate` label, and the head repository equals the base
  repository. The job caps a run at a 15-second timeout and keeps its evidence for 7 days.
  These conditions describe when simulation *may* run; they are not a merge precondition.
- **[MUST]** **[ENFORCED: CI]** A fork pull request never receives the simulation token, and
  simulation is never a required check for it.

### Assets and generated files

- **[MUST]** **[ENFORCED: pre-commit]** Git LFS is used only for the eight declared non-diffable
  extensions in `.gitattributes` (`.pdf`, `.step`, `.stl`, `.fzz`, `.zip`, `.bin`, `.elf`, `.vcd`);
  the size guard passes LFS blobs and blocks anything else over 1024 kB.
- **[MUST]** **[ENFORCED: review]** Link videos; never commit them. Images referenced by
  a repository Markdown document (`.png`, `.jpg`, `.jpeg`, `.webp`, `.svg`) stay normal git
  objects, so the repository view and a checkout render the same bytes.
- **[MUST]** **[ENFORCED: pre-commit]** Generated build output is never committed:
  `compile_commands.json`, the `site/` build, and build output such as `.pio/` are listed
  in `.gitignore`, and the `no-generated-files` hook fails when any is tracked anyway —
  `.gitignore` alone cannot stop `git add -f`.

### Licensing and identity

- **[MUST]** **[ENFORCED: review]** Original code, documentation, and reports are released
  under the single MIT grant in `LICENSE`; a licence change is forward-only for published content.
- **[MUST]** **[ENFORCED: review]** Use the public handle or organization name only —
  never a private name, an institution, or an email address — in `LICENSE`, report metadata,
  commits, or trailers. The public GitHub account's display name is the accepted exception for
  server-side commit author metadata during a squash-merge.
- **[MUST]** **[ENFORCED: review]** Never commit internal course material or original
  assignment text. Assignments appear only as English paraphrase with attribution.

### Architecture

- **[MUST]** **[ENFORCED: CI]** `lib/common` and `lib/port` carry no framework
  headers, proven directly by `pio test -d tests -e native` on host.

## Routing table

| Recurring task | Where the truth lives |
|----------------|-----------------------|
| Open a pull request | `.github/pull_request_template.md` — the single template |
| Tag a merged homework | `scripts/tag_homework.sh <id>` — the only tag path |
| Create a homework | `scripts/new_homework <id> --template <name>` — the only supported path |
| Validate metadata and provenance | `uv run scripts/check_metadata.py` with `schema/homework.schema.json` |
| Inspect or extend the secret gate | `.pre-commit-config.yaml`, `.github/workflows/ci.yml` and `.github/workflows/nightly.yml` |
| Investigate a red required check | `.github/workflows/ci.yml` — the `gate` job |
| Choose a branch name | this file, "Git, branches, and history" |
| Set up a developer editor | `.agents/standards/vscode.md` — the onboarding guide |
| Report structure, evidence, and the self-audit checklist | `.agents/standards/report.md` |
| Reuse a versioned workflow skill | canonical `.agents/skills/`, symlinked `.claude/skills/` |

## Precedence

Nested `AGENTS.md` files are allowed when a subtree's rules genuinely differ from this
one; none exist today, and a nested file is added only on real divergence. The closest AGENTS.md to the edited file wins; explicit user chat prompts override everything.
A tool-specific adapter such as `.claude/CLAUDE.md` adds mechanics only; where it
disagrees with this file, this file wins.

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
| 3 | `pre-commit run --all-files` | Run the local gate: hygiene, large files, secrets, the dependency rule, and the metadata contract. |
| 4 | `uv run scripts/check_metadata.py` | Validate homework metadata and task provenance against `schema/homework.schema.json`. |

## Repository layout

Present today: this rulebook, `README.md`, one MIT `LICENSE`, `.gitignore`, `.gitattributes`,
`.pre-commit-config.yaml`, `mkdocs.yml`, `requirements-docs.txt`, `generated.manifest`, and
the paths below.

- `.github/pull_request_template.md` — the single pull-request template.
- `.github/workflows/security.yml` — the full-history secret scan.
- `docs/` — the documentation site source: the authored `decisions/` and `standards/` trees
  plus the generated `index.md`, `homeworks/`, `boards/` and `assets/vendor/`.
- `docs/standards/vscode.md` — the VS Code onboarding guide, from install to the
  no-hardware check.
- `boards/` — one YAML profile per board, validated by the same metadata checker.
- `scripts/` — deterministic checks, the view generator and the tag script; `scripts/tests/`
  — the test suite.
- `schema/` — `homework.schema.json`, the JSON Schema 2020-12 metadata contract.
- `templates/` — the scaffolding source, rendered only by `scripts/new_homework`, plus
  `templates/views/` — the text templates `scripts/gen_views.py` renders.
- `lib/` — `port`, `common`, `host`, and the thin Arduino and ESP-IDF adapters.
- `homeworks/<id>/` — one project per assignment, created only by `scripts/new_homework`.

The generated paths — the table region in `README.md`, `homeworks.code-workspace`,
`platformio.shared.ini`, `mkdocs.yml` and the generated pages under `docs/` — are committed
and registered in `generated.manifest`. The `gen-views-check` pre-commit hook and the
`generated-views` pull-request workflow both run `scripts/gen_views.py --all --check` and
fail on drift; the fix is `uv run scripts/gen_views.py --all`, never a hand edit. `site/` is
the only build output and stays ignored.

`scripts/affected.py` maps a diff to the build matrix: a change under `homeworks/`, `lib/`,
`platformio.shared.ini`, `partitions/`, `scripts/pio/` or `schema/` selects projects, an
explicit no-build-impact set (`.planning/`, `docs/`, `.github/`, `templates/views/`,
`boards/` and the generated view files) selects nothing, and any unrecognised path widens to
every project.

The first Pages deployment requires `Settings -> Pages -> Build and deployment -> Source` to
be `GitHub Actions`; that is a maintainer action completed before the first push to `main`,
not something the `docs` workflow can set for itself.

Planned: report structure under `docs/standards/` (Phase 10) and project skills under
`.claude/skills/` or `.agents/skills/` (Phase 9).

## Definition of Done

A homework is done when:

1. `pio run` is green for its target environment.
2. `pio test -e native` is green when the homework contains pure logic.
3. `task.md`, `homework.yaml`, `README.md`, and `report.md` exist, and metadata validation passes.
4. The report contains the sections that apply; the bill of materials, calculations, measurement ledger, and traceability matrix are guidance, not a merge gate.
5. The pull request is merged and tagged `hw/<id>`.

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

### Pull requests and tags

- **[MUST]** **[ENFORCED: review]** Open every pull request through the single default
  template at `.github/pull_request_template.md`; it carries the Definition of Done rather
  than a type chooser.
- **[MUST]** **[ENFORCED: review]** Create the `hw/<id>` tag only through
  `scripts/tag_homework.sh <id>`, after the homework pull request is merged. Never create a
  tag by hand and never move a published tag; a forced update is forbidden.

### Secrets

- **[MUST]** **[ENFORCED: pre-commit]** gitleaks must pass. The local hook scans staged
  changes, and `.github/workflows/security.yml` scans the full history on every pull
  request. A red secret scan blocks the change.
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
  rewrites. The tracked tree is expected to conform, so a failure is a local fix rather than a
  bulk reformat.
- **[MUST]** **[ENFORCED: pre-commit]** Python, authored YAML, and authored Markdown are
  linted by ruff, yamllint, and markdownlint-cli2 from their committed policies
  (`pyproject.toml`, `.yamllint.yaml`, `.markdownlint-cli2.jsonc`). Generated pages and the
  vendored tree are excluded because `gen_views.py --check` and their pins own them.
- **[MUST]** **[ENFORCED: pre-commit]** The secret gate is gitleaks; see "Secrets" above.
  Every formatter and linter named in this section arrives through a pinned `pre-commit`
  revision, never a system package manager, so the gate is byte-identical on every machine.
- **[MUST]** **[ENFORCED: pre-push]** clang-tidy 23.1.3 analyses the host translation units
  under `lib/common/src` and `lib/host/src`, and never runs at pre-commit. A header is analysed
  through a translation unit that includes it, never as a file of its own: a bare header has no
  compile command, so a header-only change is not analysed locally, and `lib/port` is covered
  only where a unit includes it. Native test translation units are out of scope until Phase 8
  CI owns a database for them.
- **[MUST]** **[ENFORCED: pre-push]** When `tests/compile_commands.json` is absent, older than
  a configuration input or a described source, or missing a `.c` file under the analysed trees,
  `scripts/clang-tidy-db` fails and prints `pio run -d tests -e native -t compiledb`. The
  clang-tidy hook fails rather than reporting success when clang-tidy skips a file for want of a
  compile command. Regenerating the database is a developer action; no hook generates it.
- **[SHOULD]** **[ENFORCED: review]** An editor is configured from `docs/standards/vscode.md`,
  not from ad-hoc settings. The committed editor contract is emitted by the generator and
  mirrored into `.vscode/settings.json`, and a drift test keeps the two equal.

### Assets and generated files

- **[MUST]** **[ENFORCED: pre-commit]** Git LFS is used only for the eight declared non-diffable
  extensions in `.gitattributes` (`.pdf`, `.step`, `.stl`, `.fzz`, `.zip`, `.bin`, `.elf`, `.vcd`);
  the size guard passes LFS blobs and blocks anything else over 1024 kB.
- **[MUST]** **[ENFORCED: review]** Link videos; never commit them. Page-served site
  assets (`.png`, `.jpg`, `.jpeg`, `.webp`, `.svg`) stay normal git objects, because GitHub
  Pages cannot serve LFS content.
- **[MUST]** **[ENFORCED: pre-commit]** Generated files are never committed:
  `compile_commands.json`, the `site/` build, and build output such as `.pio/` are listed
  in `.gitignore`, and the `no-generated-files` hook fails when any is tracked anyway —
  `.gitignore` alone cannot stop `git add -f`.

### Licensing and identity

- **[MUST]** **[ENFORCED: review]** Original code, documentation, and reports are released
  under the single MIT grant in `LICENSE`; a licence change is forward-only for published content.
- **[MUST]** **[ENFORCED: review]** Use the public handle or organization name only —
  never a private name, an institution, or an email address — in `LICENSE`, report metadata,
  commits, or trailers. The public GitHub account's display name is the accepted exception for
  server-side commit author metadata during a squash-merge (see `docs/decisions/0006-public-commit-identity.md`).
- **[MUST]** **[ENFORCED: review]** Never commit internal course material or original
  assignment text. Assignments appear only as English paraphrase with attribution.

### Decisions

- **[MUST]** **[ENFORCED: review]** A new decision defaults to one row in
  `docs/decisions/README.md`; that table is the index and the default record. Create an ADR
  file only when the decision needs real argumentation — alternatives, consequences, a long
  comparison — and link it from the row's `Record` column. No numbering is required.
- **[MUST]** **[ENFORCED: review]** Mark a superseded decision in the table's `Status`
  column. Do not rewrite the ADR body: it is the historical record of what was decided, and
  a path it names may no longer exist.
- **[SHOULD]** **[ENFORCED: review]** Raise required approvals from 0 to 1 when a second
  maintainer joins; until then the ruleset keeps 0 approvals and no bypass actors.

### Architecture

- **[MUST]** **[ENFORCED: pre-commit]** `lib/common` and `lib/port` carry no framework
  headers, and `common` does not depend on the adapters. `python3 scripts/check_architecture.py`
  runs in the hook on every change to `lib/`, `homeworks/`, or the checker itself.

## Routing table

| Recurring task | Where the truth lives |
|----------------|-----------------------|
| Change a GitHub rule or repository setting | the GitHub UI; record the reason in `docs/decisions/README.md` |
| Open a pull request | `.github/pull_request_template.md` — the single template |
| Tag a merged homework | `scripts/tag_homework.sh <id>` — the only tag path |
| Record a decision | a row in `docs/decisions/README.md`; link an ADR only when argumentation is needed |
| Create a homework | `scripts/new_homework <id> --template <name>` — the only supported path |
| Validate metadata and provenance | `uv run scripts/check_metadata.py` with `schema/homework.schema.json` |
| Inspect or extend the secret gate | `.pre-commit-config.yaml` and `.github/workflows/security.yml` |
| Choose a branch name | this file, "Git, branches, and history" |
| Set up a developer editor | `docs/standards/vscode.md` — the onboarding guide |
| Report structure and formatting rationale | `docs/standards/` (planned, Phase 10) |
| Reuse a versioned workflow skill | project skills under `.claude/skills/` (planned, Phase 9) |

## Precedence

Nested `AGENTS.md` files are allowed when a subtree's rules genuinely differ from this
one; none exist today, and a nested file is added only on real divergence. The closest AGENTS.md to the edited file wins; explicit user chat prompts override everything.
A tool-specific adapter such as `.claude/CLAUDE.md` adds mechanics only; where it
disagrees with this file, this file wins.

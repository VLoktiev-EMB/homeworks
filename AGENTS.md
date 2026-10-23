# AGENTS.md

Canonical rulebook for every agent that works in this repository. Tool-specific adapters
import this file instead of copying it — `.claude/CLAUDE.md` is one such adapter. If an
adapter and this file disagree, this file wins.

## Project

A public GitHub monorepo of independent PlatformIO homework projects for an embedded
engineering course. Each homework ships as a self-contained engineering artifact — code,
tests, an academic report, wiring, a bill of materials, calculations, and measured
evidence — that can be understood and verified a year later. Repository artifacts are
English; conversation with the user follows the user's language. The repository is
public and its GitHub organization is on the free plan, so no rule here may assume a
paid-only feature.

## Agent quick-start

Run from the repository root, in this order, before opening a pull request.

| Step | Command | Purpose |
|------|---------|---------|
| 1 | `/gsd-fast`, `/gsd-quick`, `/gsd-debug`, or `/gsd-execute-phase` | Route the change through the GSD workflow. |
| 2 | `pio run` | Build the affected PlatformIO environment. |
| 3 | `pio test -e native` | Run firmware-side native tests, once `homeworks/` exists (Phase 2). |
| 4 | `python3 -m unittest discover -s scripts/tests -v` | Run the repository test suite. |
| 5 | `python3 scripts/check_policy.py --check` | Prove live GitHub policy still matches `policy/`. |
| 6 | `python3 scripts/check_pr_templates.py` | Prove the three pull-request templates share one header. |
| 7 | `pre-commit run --all-files` | Run the local gate: hygiene, large files, secrets. |
| 8 | `scripts/tag_homework.sh <id>` | Tag a merged homework. Maintainers only, after merge. |

## Repository layout

Present today:

- `AGENTS.md` — this rulebook; `README.md` — the public front door.
- `LICENSE`, `NOTICE`, `LICENSES/`, `REUSE.toml` — the license split, declared once.
- `.gitignore`, `.gitattributes`, `.pre-commit-config.yaml` — ignore rules, LFS routing,
  and the local gate.
- `.github/PULL_REQUEST_TEMPLATE/` — three type-specific templates; no default template.
- `.github/workflows/security.yml` — the full-history secret scan.
- `docs/decisions/` — MADR records and their status index.
- `policy/` — the branch ruleset and repository settings as code.
- `scripts/` — deterministic checks and the tag script; `scripts/tests/` — the test suite.

Planned, each with the phase that introduces it:

- `homeworks/<id>/` — one independent PlatformIO project per assignment (Phase 2 onward).
- `lib/` — shared portable libraries: `common`, `port`, and thin adapters (Phase 3).
- `templates/` — the scaffolding source for a new homework (Phase 4).
- `docs/standards/` — report structure and formatting rationale (planned, Phase 5).
- `.claude/skills/` or `.agents/skills/` — versioned agent skills (planned, Phase 9).

## Rules

Every rule carries two dimensions: severity (`[MUST]` or `[SHOULD]`) and where a
violation is caught (`[ENFORCED: pre-commit]` on the developer machine,
`[ENFORCED: CI]` in repository automation or a CI drift check, `[ENFORCED: review]` by a
human reviewer). There is no `[MAY]` and no `[INFO]`.

### Change workflow

- **[MUST]** **[ENFORCED: review]** Every change goes through a GSD command
  (`/gsd-fast`, `/gsd-quick`, `/gsd-debug`, `/gsd-execute-phase`) or a deterministic
  script under `scripts/`. Direct edits outside that workflow are not allowed. GSD is
  portable: Antigravity and other tools run the same `/gsd-*` commands, so this rule
  belongs here, not in a Claude-only adapter.
- **[MUST]** **[ENFORCED: review]** Commit messages follow Conventional Commits:
  `type(scope): summary`, where `type` is one of `feat`, `fix`, `test`, `refactor`,
  `perf`, `docs`, `style`, or `chore`, and `scope` is the phase-plan or homework ID.
- **[SHOULD]** **[ENFORCED: review]** Prefer one logical change per pull request; split
  a change when its description needs an "and".

Highest-risk example — the commit message:

```text
Bad:   updated stuff

Good:  feat(1_3): add police flasher state machine
```

### Git, branches, and history

- **[MUST]** **[ENFORCED: CI]** Never push directly to the default branch and never
  force-push. Every change arrives through a branch and a pull request. The GitHub
  ruleset `main` rejects the write server-side, and `python3 scripts/check_policy.py
  --check` proves that ruleset is still in place.
- **[MUST]** **[ENFORCED: CI]** Published history is never rewritten: no rebase of a
  shared branch, no history edit, no tag move. The ruleset requires linear history, so a
  squash merge is the only route into the default branch.
- **[MUST]** **[ENFORCED: review]** Squash-only applies to merges **into the default
  branch**. Repository-level merge and rebase remain enabled so feature branches may use
  any strategy; do not "fix" that by disabling them.
- **[MUST]** **[ENFORCED: review]** Branch names use the anchors `hw/<id>` for a homework
  and `docs/<slug>` for documentation. Every other prefix is free-form and defaults to
  the `infra` pull-request template.

### Homework identifiers

- **[MUST]** **[ENFORCED: review]** A homework ID matches `^[0-9]+_[0-9]+-[a-z0-9-]+$` —
  the `module_lesson-name` form, for example `1_3-police-flasher`. The ID is a path
  segment and is stable after publication. An empty ID, a separator-less name such as
  `police-flasher`, and a mixed-case name are invalid. Phase 4 enforces the same pattern
  in the `homework.yaml` schema; until then, review is the gate.
- **[MUST]** **[ENFORCED: review]** Homework IDs and paths are ASCII-only (`[a-z0-9_.-]`).
  Display names in a report may use emoji and non-ASCII text, but paths and identifiers
  stay ASCII so byte length and codepoint length never diverge.

### Pull requests and tags

- **[MUST]** **[ENFORCED: review]** Open every pull request through a template under
  `.github/PULL_REQUEST_TEMPLATE/`, chosen by type: `homework`, `infra`, or `docs`. There
  is deliberately no default template, so the chooser always appears.
  `python3 scripts/check_pr_templates.py` keeps the shared header byte-identical.
- **[MUST]** **[ENFORCED: review]** Create the `hw/<id>` tag only through
  `scripts/tag_homework.sh <id>`, after the homework pull request is merged. Never create
  a tag by hand and never force-update one. Branch rulesets do not apply to tag refs, so
  this script is the only guard: it checks the ID shape, the homework directory, local and
  remote tag absence, and the merged pull request before it pushes once.

### Secrets

- **[MUST]** **[ENFORCED: pre-commit]** gitleaks must pass. The local hook scans staged
  changes, and `.github/workflows/security.yml` scans the full history on every pull
  request. A red secret scan blocks the change.
- **[MUST]** **[ENFORCED: review]** A real secret triggers, in this order: rotate the
  credential first, assess exposure, remove it with a forward fix, and document the
  incident. Never rewrite history to remove it — rotation is the only real mitigation
  once a secret has reached a public repository.
- **[SHOULD]** **[ENFORCED: review]** Treat the scanner as pattern-based, not
  exhaustive. The pinned gitleaks 8.30.1 default ruleset flags a PEM private-key block
  but not every vendor key shape, including vendor documentation examples. Widening the
  ruleset is a Phase 6 decision made in the open through `.gitleaks.toml`, never an
  allowlist relaxation added quietly.

Highest-risk example — secret handling:

```text
Bad:   commit the key, then try to scrub it from history.

Good:  rotate the key, remove it with a forward commit, document the incident.
```

### Assets and generated files

- **[MUST]** **[ENFORCED: pre-commit]** Git LFS is used only for the eight declared
  non-diffable extensions in `.gitattributes`: `.pdf`, `.step`, `.stl`, `.fzz`, `.zip`,
  `.bin`, `.elf`, `.vcd`. The pre-commit size guard passes LFS-tracked blobs and blocks
  anything else over 1024 kB.
- **[MUST]** **[ENFORCED: review]** Link videos; never commit them. Page-served site
  assets (`.png`, `.jpg`, `.jpeg`, `.webp`, `.svg`) stay normal git objects, because
  GitHub Pages cannot serve LFS content.
- **[MUST]** **[ENFORCED: pre-commit]** Generated files are never committed:
  `compile_commands.json`, the `site/` build, and build output such as `.pio/` are
  listed in `.gitignore`, and the `no-generated-files` pre-commit hook fails when any
  of them is tracked anyway — `.gitignore` alone cannot stop `git add -f`.

### Licensing and identity

- **[MUST]** **[ENFORCED: CI]** Original code is MIT-licensed; documentation and
  homework reports are CC-BY-4.0. The split is declared once in `REUSE.toml`, and
  `reuse lint` joins the pull-request pipeline in Phase 8.
- **[MUST]** **[ENFORCED: review]** Use the public handle or organization name only —
  never a real name, an institution, or an email address — in `LICENSE`, `NOTICE`,
  report metadata, commits, or trailers.
- **[MUST]** **[ENFORCED: review]** Never commit internal course material or original
  assignment text. Assignments appear only as English paraphrase with attribution.

### Decisions

- **[MUST]** **[ENFORCED: review]** Record cross-cutting infrastructure decisions as
  MADR records under `docs/decisions/`, using the next free number and updating
  `docs/decisions/README.md` in the same change. Numbers are sequential and permanent.
- **[SHOULD]** **[ENFORCED: review]** Raise required approvals from 0 to 1 when a second
  maintainer joins; until then the ruleset keeps 0 approvals and no bypass actors.

## Routing table

| Recurring task | Where the truth lives |
|----------------|-----------------------|
| Change a GitHub rule or repository setting | `policy/` with `scripts/check_policy.py`; record the reason in `docs/decisions/` |
| Open a pull request | `.github/PULL_REQUEST_TEMPLATE/{homework,infra,docs}.md`, chosen by type |
| Tag a merged homework | `scripts/tag_homework.sh <id>` — the only tag path |
| Record an infrastructure decision | `docs/decisions/README.md` and the next numbered MADR |
| Inspect or extend the secret gate | `.pre-commit-config.yaml` and `.github/workflows/security.yml` |
| Choose a branch name | this file, "Git, branches, and history" |
| Report structure and formatting rationale | `docs/standards/` (planned, Phase 5) |
| Reuse a versioned workflow skill | project skills under `.claude/skills/` (planned, Phase 9) |

## Precedence

Nested `AGENTS.md` files are allowed when a subtree's rules genuinely differ from this
one; none exist today, and a nested file is added only on real divergence. The closest AGENTS.md to the edited file wins; explicit user chat prompts override everything.
A tool-specific adapter such as `.claude/CLAUDE.md` adds mechanics only; where it
disagrees with this file, this file wins.

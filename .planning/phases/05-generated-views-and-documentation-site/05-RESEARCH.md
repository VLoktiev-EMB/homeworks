# Phase 5: Generated Views and Documentation Site - Research

**Researched:** 2026-10-25
**Domain:** Deterministic metadata-driven code generation, MkDocs Material site, GitHub Pages publication
**Confidence:** HIGH for the docs stack and the drift mechanics (empirically probed this session); MEDIUM for the `affected.py` fanout policy edges and for Zensical's treatment of a few top-level keys

## Summary

Every technical question this phase asks was answerable against a running toolchain rather than
against recollection. The docs stack is confirmed to work exactly as the requirements state:
`mkdocs==1.6.1`, `mkdocs-material==9.7.7` and `pymdown-extensions==12.3` resolve together, and
`mkdocs build --strict` returns 0 against the repository's **real** `docs/` tree with an explicit
`nav:` that lists all twelve pages. The Material 9.7.7 "MkDocs 2.0" banner prints to stderr but
does **not** increment MkDocs' warning counter, so it does not break `--strict`.

The single most consequential finding is a **negative** one that changes several plan tasks:
`scripts/tests/test_metadata_deps.py` — the pin-consistency test that CONTEXT D-30 says to
"extend" — was deleted in the Phase 04.1 ceremony trim (commit `597bd7a`; confirmed with
`git log --diff-filter=D`) `[VERIFIED: git log --diff-filter=D -- scripts/tests/test_metadata_deps.py]`.
It does not exist.
Phase 5 must **create** a pin-consistency test, not extend one. The second consequential finding
is that `scripts/check_architecture.py` already contains the exact `platformio.ini` machinery
`affected.py` needs (`_option` with `extends` resolution, `_dep_names` with the `name=symlink://`
alias rule, and the `native` prefix rule). Duplicating it would create a second, divergent
definition of the same facts; extracting it into a shared module is the correct move and follows
the D-19 precedent.

Two design landmines are worth naming up front. First, generating `platformio.shared.ini` from
`homework.yaml` while `check_metadata.py` validates `homework.yaml` **against**
`platformio.shared.ini` is circular; the generator must gather the distinct pin pairs across all
homeworks and fail on disagreement rather than pick a winner. Second, `--strict` with
`validation.nav.omitted_files: warn` makes the build fail if **any** Markdown file under `docs/`
is missing from `nav:` — so the generated nav must cover the twelve authored ADR pages, or that
specific validation key must be left at its default.

**Primary recommendation:** build one stdlib-plus-PyYAML generator (`scripts/gen_views.py`) with a
committed `generated.manifest`, extract the `{{placeholder}}` renderer and the `platformio.ini`
readers into `scripts/metadata/`, delete the `mkdocs-gen-files` idea entirely, vendor exactly 24
KaTeX files (~600 KB), and publish through `upload-pages-artifact` + `deploy-pages` on `main` only.

## User Constraints (from CONTEXT.md)

### Locked Decisions

#### What is committed and what is authored

- **D-01:** Generated documentation pages are **committed** to `docs/`, and every generator
  supports `--check`. `mkdocs-gen-files` is rejected: Zensical explicitly does not support
  it ("run scripts separately"), so a virtual-generation design would break the
  Zensical-compatible configuration the research requires. Committed output also keeps the
  site reviewable on GitHub without a build.
  — **Reversibility:** costly — switching to build-time generation would replace the drift
  gate, the Pages workflow, and the review model in one move.
- **D-02:** A generated homework page contains a **metadata card** (id, title, board,
  framework, language, status, toolchain, simulation status) plus **links** to
  `homeworks/<id>/report.md` and `README.md` on GitHub. The report body is not copied:
  copying Markdown without its `assets/` tree breaks every relative image path.
- **D-03:** Authored and generated pages share `docs/`. Every generated file starts with a
  `GENERATED — do not edit` header and is registered in the generator manifest.
- **D-04:** Board profiles live at `boards/<id>.yaml` in the repository root, as data beside
  `schema/`. `templates/board-profile/` remains the template; the generated page is
  `docs/boards/<id>.md`.
  — **Reversibility:** costly — the path is consumed by the generator, the metadata checker,
  and every future board page.
- **D-09:** The site home page is authored prose in `docs/index.md` between markers plus a
  generated homework table — the same split as the README.
- **D-12:** No authored `docs/standards/` pages this phase. Phase 10 owns the report and
  evidence contract; the `AGENTS.md` line that schedules `docs/standards/` for Phase 5 must
  be corrected in the same change.

#### Site configuration

- **D-05:** Navigation is an explicit `nav:` block in `mkdocs.yml`, ordered by homework id.
  No literate-nav plugin and no auto-generated navigation: the requirement names generated
  navigation, and both Zensical and Material accept an explicit tree.
- **D-06:** The whole `mkdocs.yml` is generated from `templates/views/mkdocs.yml` (Claude's
  discretion). One owner, `--check` covers theme, extensions, plugins, and navigation, and
  the Zensical constraint (search only, no hooks) is encoded in one reviewed template.
- **D-07:** KaTeX is **vendored** at `docs/assets/vendor/katex/0.19.0/` with its `LICENSE`
  and a checksum test. No CDN: the requirement says vendored, and an external host would
  make `--strict` builds depend on the network.
- **D-08:** Stock Material theme, no `docs/overrides/`. This keeps maximum Zensical
  compatibility and avoids tying the site to Material's internal template structure.
- **D-10:** Navigation structure: Home · Homeworks · Boards · Decisions.
- **D-11:** The generated homework table uses six columns — ID · Project · Board ·
  Framework · Status · Report — identical in `README.md` and on the site home page.

#### Generator surface

- **D-13:** One generator, `scripts/gen_views.py`, with subcommands `readme`, `workspace`,
  `nav`, `docs`, and `shared-ini`, plus `--all`. Every subcommand accepts `--check`. One
  loader, one manifest, one test surface.
- **D-14:** In `README.md` the generator owns only the region between
  `<!-- BEGIN GENERATED: homeworks -->` and `<!-- END GENERATED -->`; the prose stays
  authored.
- **D-15:** `homeworks.code-workspace` is generated **whole** from a template, including the
  `extensions` block. Folders are `repo`, `docs`, `lib`, `scripts`, and every homework.
  JSON has no markers, so partial ownership would require parse-and-rewrite anyway.
- **D-16:** `platformio.shared.ini` is generated whole from a template containing the three
  environment sections, with `platformio` and `platform@` substituted from `homework.yaml`.
  A homework still contributes **zero** entries there (04.2/D-17); the generator exists to
  keep the pins in one place and make drift impossible.
  — **Reversibility:** costly — pin substitution is the reproducibility contract checked by
  `check_metadata.py`.
- **D-17:** Ownership is recorded in a committed `generated.manifest` with paths and hashes.
  `--check` detects modified, deleted, and newly appearing files, and the manifest itself is
  covered by the same check.
- **D-18:** Templates are split by output kind: text views (README region, `mkdocs.yml`,
  documentation pages) come from `templates/views/`; JSON outputs (workspace, manifest) are
  serialized programmatically with deterministic formatting.
- **D-19:** The existing `{{placeholder}}` renderer in `scripts/new_homework` is extracted
  into a shared module (for example `scripts/metadata/render.py`) and used by both entry
  scripts. Unknown placeholders remain an error.
  — **Reversibility:** costly — the placeholder vocabulary is baked into every template and
  into both tools' tests (04/D-25, D-33).
- **D-20:** Repeated blocks are passed as pre-rendered fragments (`{{homework_rows}}`,
  `{{nav_entries}}`). No mini-loop syntax: that would be a new template language, which
  D-33 forbids.

#### Drift gate and affected.py

- **D-21:** `--check` runs in two places: a **check-only** pre-commit hook that fails and
  tells the user to run `uv run scripts/gen_views.py --all`, and one small CI job that
  satisfies META-05 ("CI fails on drift"). The matrix remains Phase 8. The hook never
  regenerates or stages files.
- **D-22:** `scripts/affected.py` emits a JSON object with `build` and `simulate` arrays;
  each entry is `{project, env, framework}`. `--format paths` prints a human-readable list.
  Phase 8 feeds the JSON straight into `strategy.matrix: ${{ fromJson(...) }}`.
- **D-23:** The dependency graph comes from `lib_deps = <name>=symlink://../../lib/<name>`
  in each homework's `platformio.ini` plus each `lib/<name>/library.json`. No new
  `homework.yaml` field: PlatformIO stays the single source of truth.
- **D-24:** Fanout rules: `lib/<name>` widens to its consumers; `platformio.shared.ini`,
  `partitions/`, `scripts/pio/`, `schema/`, and `affected.py` itself widen to every project;
  any unrecognised shared path widens to every project (fail-safe).

#### Scope fences

- **D-25:** The two friction-log candidates outside the roadmap — the private `lib/pattern`
  manifest generator (F-04) and the test scaffold plus inner `.gitignore` (F-05, F-18) — are
  deferred to backlog / Phase 9. They produce project content, not views of `homework.yaml`.
- **D-26:** Phase 5 generates **no** CI matrix. `affected.py` plus the drift job are the
  deliverable; converting them into a matrix is Phase 8 (04.2/D-18, F-14).
- **D-27:** `boards/<id>.yaml` is validated by extending `scripts/check_metadata.py` with a
  board-profile schema, preserving one validator and the 0/1/2 exit-code contract.

#### Testing and pins

- **D-28:** Generator tests extend the stdlib-only `scripts/tests/` suite and invoke the
  generator through `subprocess` (`uv run …`), so no test imports `yaml` (04/D-14).
  Mandatory invariants, kept lean: round-trip/idempotency (which also proves authored files
  are untouched), drift detection for modified/deleted/new files, and `affected.py` unit
  tests plus one end-to-end run in a temporary git repository.
- **D-29:** Tests build a small synthetic fixture tree (two homeworks, two libraries, one
  consumer each) in a temporary directory; one additional smoke test runs `--check` against
  the real tree.
- **D-30:** Docs build dependencies are pinned in `requirements-docs.txt` with exact
  versions (mkdocs-material 9.7.7, pymdown-extensions 12.3.0, mkdocs<2). No hash pinning.
  The existing stdlib pin-consistency test (04/D-13) is extended to cross-check
  `requirements-docs.txt`, the versions named in the generated `mkdocs.yml`, and the
  vendored KaTeX 0.19.0.

### Claude's Discretion

- Exact template names and layout under `templates/views/`.
- The internal module split of `gen_views.py` and `affected.py`, and the exact
  `generated.manifest` shape (as long as it carries paths and hashes).
- The generated Markdown page layout for homeworks, boards, and the home page.
- The exact CI workflow file name and job structure for the drift job, provided it is one
  job and not a matrix.
- Test fixture content and the exact assertions.

### Deferred Ideas (OUT OF SCOPE)

- **Private `lib/pattern` manifest + `lib_deps` generation (F-04)** — backlog / Phase 9; it is
  scaffold content, not a metadata view.
- **Test scaffold and inner `.gitignore` covering `.vscode/` (F-05, F-18)** — backlog /
  Phase 9 for the same reason.
- **CI `strategy.matrix`** — Phase 8; Phase 5 only supplies `affected.py`.
- **Report-body embedding on the site** — deferred until relative `assets/` paths are solved;
  `mkdocs-gen-files` is unavailable under the Zensical constraint.
- **Authored `docs/standards/` pages** — Phase 10; the `AGENTS.md` "Phase 5" line is updated
  instead.
- **External link checking** — Phase 8.
- **Zensical migration evaluation** — Q1 2027, before the 2027-05-05 Material EOL.

- **Reviewed Todos (not folded)**
- *Expand homework README and add a proper SVG schematic* — homework content (Phase 11 /
  Phase 7), outside the generated-views boundary.
- *Promote merge_firmware.py into a shared tool* — already deferred to Phase 7/8 in STATE.md.
- *Standardize pull request titles across homeworks* — CI/process concern, Phase 8/9.
- *Trim governance ceremony (Phase 4.1)* — already completed; no action.

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| META-05 | README index, MkDocs nav, workspace, `platformio.shared.ini`, and CI matrix generated from `homework.yaml`; every generator supports `--check`; CI fails on drift. | §Generator architecture; §Manifest and drift semantics; §mkdocs.yml skeleton; §Pre-commit and CI. The matrix half is Phase 8 by D-26; `affected.py` supplies its input. |
| META-06 | `scripts/affected.py` maps a git diff to a build and simulation matrix including `lib/**` fanout. | §affected.py design; `check_architecture.py` reuse (§Existing machinery); §Fanout table; §Pitfall 7. |
| META-07 | Committed multi-root `homeworks.code-workspace` with `repo`, `docs`, `lib`, `scripts`, every homework; display names may be emoji, paths ASCII. | §Workspace generation; §Existing artifacts table (current file has two folders and no `name` keys). |
| META-08 | MkDocs Material 9.7.7 site from the generated tree, Zensical-compatible, vendored KaTeX, Pages artifact deploy. | §Standard Stack; §Zensical constraints; §KaTeX vendoring; §Pages deployment; the strict-build probe (§Probe results) returned 0 on the real tree. |

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Metadata loading and validation | Repository tooling (`scripts/metadata/`) | — | One loader, one contract; the checker and both generators must not diverge (D-12, D-19). |
| View rendering (README rows, nav, pages, workspace) | Repository tooling (`scripts/gen_views.py`) | Committed artifacts | Rendering is deterministic text production; the artifacts are the reviewable output, not a build-time product (D-01). |
| Ownership and drift detection | Committed `generated.manifest` | Repository tooling (`--check`) | The manifest is the only record of what the generator owns; CI and pre-commit both compare against it (D-17). |
| Dependency fanout | Repository tooling (`scripts/affected.py`) | CI (`strategy.matrix`, Phase 8) | The graph is derived from `platformio.ini` + `library.json`; CI only consumes JSON (D-22, D-23). |
| Site build | Static site generator (MkDocs) | — | Never hand-rolled; the site is a projection of `docs/`, not a second source. |
| Publication | CI runner + GitHub Pages | — | Artifact deployment with OIDC; no `gh-pages` branch (STACK §5.7, verified against `deploy-pages` README). |
| Authored prose (home-page intro, decisions, ADRs) | Human | Generator owns only marker regions | D-09, D-14: the generator must never own a whole authored file except where D-15/D-16 lock it. |

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `mkdocs` | `1.6.1` | Static site generator | Latest 1.x; `mkdocs-material 9.7.7` declares `mkdocs<2,>=1.6` `[VERIFIED: pypi.org/pypi/mkdocs-material/9.7.7/json]`. 1.6.1 is the newest release on PyPI `[VERIFIED: pip index versions mkdocs]`. |
| `mkdocs-material` | `9.7.7` | Theme | Named by META-08. Uploaded 2026-07-17; maintenance mode, EOL 2027-05-05 `[VERIFIED: pypi.org/pypi/mkdocs-material/9.7.7/json]`. A newer `9.8.0` exists and is deliberately **not** used — META-08 pins 9.7.7. |
| `pymdown-extensions` | `12.3` | `arithmatex`, `superfences`, `tabbed`, `details`, `highlight` | Required by `arithmatex generic: true`; `mkdocs-material` requires `pymdown-extensions>=10.2` `[VERIFIED: pypi.org/pypi/mkdocs-material/9.7.7/json]`. `12.3` is the newest on PyPI `[VERIFIED: pip index versions pymdown-extensions]`. D-30 names "12.3.0"; the published artefact is `12.3` — pin the artefact string, not the docstring spelling. |
| KaTeX | `0.19.0` | Math rendering | MIT `[VERIFIED: npm view katex@0.19.0 license]`. Newest is 0.19.1; D-07 pins 0.19.0. |

**Verified combination:** `uv run --with-requirements requirements-docs.txt mkdocs build --strict`
resolved `mkdocs 1.6.1` + `mkdocs-material 9.7.7` on Python 3.14.7 and exited 0 against the real
`docs/` tree `[VERIFIED: local probe, /tmp/mkdocs-uv]`.

**Installation (local, reproducible, no venv):**

```bash
uv run --python 3.13 --with-requirements requirements-docs.txt mkdocs build --strict
```

`--with-requirements` is the whole reason `requirements-docs.txt` is enough: one command, no
virtualenv to activate, no `uv sync` state to invalidate.

**`requirements-docs.txt` (exact, no hashes per D-30):**

```text
mkdocs==1.6.1
mkdocs-material==9.7.7
pymdown-extensions==12.3
```

Do **not** add `mkdocs-material[imaging]` (drags Cairo) or any plugin beyond `search`.

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `PyYAML` | `6.0.3` | `homework.yaml` loading in the generator and `affected.py` | Already the repository pin; must appear in the PEP 723 header and the pre-commit hook `additional_dependencies` `[VERIFIED: .pre-commit-config.yaml:74]` |
| `jsonschema` | `4.26.0` | Not needed by the generators; needed by the checker and any board-profile schema | Do not add it to the generator's PEP 723 header — the generator reads, the checker validates |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `upload-pages-artifact` + `deploy-pages` | `mkdocs gh-deploy` | `gh-deploy` pushes a `gh-pages` branch, bypassing the protected-branch and PR rules in AGENTS.md; rejected by D-01's review model and STACK §5.8. |
| Explicit `nav:` | `literate-nav` / `awesome-pages` | Both are Zensical-supported, but D-05 locks the explicit tree and D-06 makes one template the owner. |
| `mkdocs-gen-files` | Virtual generation | Explicitly unsupported and silently ignored by Zensical — the generated nav would vanish on migration with no error. |
| `uv run --with-requirements` in CI | `pip install -r` + `setup-python` | Either works. `pip` + the already-pinned `setup-python` SHA avoids adding a fourth action; `uv` avoids a second install path. Recommend `pip` in CI (fewer new action SHAs) and `uv` locally. |

## Package Legitimacy Audit

| Package | Registry | Pinned version, upload date | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----------------------------|-----------|-------------|---------|-------------|
| `mkdocs` | PyPI | 1.6.1 — established (latest 1.x) | unknown to the seam | mkdocs/mkdocs | SUS (`unknown-downloads`) | Approved — flagged only by missing download telemetry; `[CITED: mkdocs.org]` and required by Material's own metadata |
| `mkdocs-material` | PyPI | 9.7.7 — 2026-07-17 | unknown to the seam | squidfunk/mkdocs-material | SUS (`too-new`, `unknown-downloads`) | Approved — "too-new" reads the *latest* release (9.8.0, 2026-10-24), not the pinned 9.7.7; META-08 names the package and version |
| `pymdown-extensions` | PyPI | 12.3 — 2026-10-14 | unknown to the seam | facelessuser/pymdown-extensions | SUS (`too-new`, `unknown-downloads`) | Approved — same heuristic artefact; D-30 names the version |
| `katex` | npm | 0.19.0 | 18,896,310/wk | KaTeX/KaTeX | SUS (`too-new`) | Approved — "too-new" reads the latest (0.19.1, 2026-10-23); D-07 names 0.19.0; MIT confirmed |

**Packages removed due to SLOP verdict:** none.
**Packages flagged as suspicious [SUS]:** the four above. Every verdict is driven by a
latest-release recency heuristic or by the seam's inability to read PyPI download counts — none
by package identity, a missing source repo, or a postinstall script. The planner may therefore
treat the checkpoint as satisfied by META-08/D-30/D-07 naming each package **and** version
explicitly; if the plan-checker requires the literal checkpoint anyway, add one
`checkpoint:human-verify` before the first `pip install -r requirements-docs.txt`, not four.

**Vendored, not installed:** KaTeX is copied into `docs/assets/vendor/katex/0.19.0/` as normal
git objects. It never enters a dependency graph and never reaches `requirements-docs.txt`.

## Architecture Patterns

### System Architecture Diagram

```text
                       homeworks/<id>/homework.yaml  (one per homework)
                                    │
                                    ├──────────────┐
                                    ▼              ▼
                        boards/<id>.yaml      lib/*/library.json
                                    │              │
                                    ▼              │
   templates/views/*.tmpl ────► scripts/gen_views.py ◄── scripts/metadata/render.py
                                    │                  scripts/metadata/platformio.py
                                    │                  (extends/lib_deps resolution)
                                    ▼
                 ┌──────────────────┼───────────────────┬────────────────┐
                 ▼                  ▼                   ▼                ▼
             README.md        mkdocs.yml       homeworks.code-workspace   docs/**/*.md
             (marker region)  (whole file)     (whole file)               (whole files)
                 │                  │                   │                │
                 │                  │                   │                │
                 └──────────┬───────┴───────────────────┴────────────────┘
                            ▼
                  generated.manifest  (path + mode + sha256, sorted)
                            │
              ┌─────────────┴──────────────┐
              ▼                            ▼
   pre-commit: gen-views-check   CI: generated-views drift job
   (check only, never stages)    (exit 1 on drift, no matrix)

   docs/ ──► mkdocs build --strict ──► site/ ──► upload-pages-artifact ──► deploy-pages
                  ▲                                                   (push to main only)
                  └── requirements-docs.txt (3 exact pins) + vendored KaTeX + LICENSE

   git diff --name-only -z  ──► scripts/affected.py ──► {"build":[…],"simulate":[…]}  ──► Phase 8
                                 ▲
                                 └── platformio.ini lib_deps + library.json (reused from
                                     scripts/check_architecture.py)
```

### Recommended Project Structure

```text
scripts/
├── gen_views.py              # PEP 723 entry point; subcommands readme|workspace|nav|docs|shared-ini|--all
├── affected.py               # PEP 723 entry point; git diff -> build/simulate arrays
├── metadata/
│   ├── __init__.py
│   ├── contract.py           # existing; unchanged except the board-profile extension (D-27)
│   ├── render.py             # NEW: extracted {{placeholder}} renderer (D-19)
│   └── platformio.py         # NEW: INI merge + extends + lib_deps helpers (shared with the checker)
└── tests/
    ├── temp_root.py          # extended fixture builder
    ├── test_gen_views.py     # NEW
    ├── test_affected.py      # NEW
    ├── test_docs_pins.py     # NEW: pin + KaTeX manifest consistency (replaces the deleted test_metadata_deps)
    └── fixtures/golden/...   # existing
templates/views/
├─ readme.md.tmpl           # README marker region body
├── mkdocs.yml.tmpl          # whole mkdocs.yml
├── workspace.json.tmpl      # whole homeworks.code-workspace
├── shared-ini.ini.tmpl      # whole platformio.shared.ini
├── homework-page.md.tmpl    # docs/homeworks/<id>.md
└── board-page.md.tmpl       # docs/boards/<id>.md
boards/
└── esp32-s3-devkitc-1.yaml  # NEW; shape = templates/board-profile/profile.yaml
docs/
├── index.md                 # NEW, authored prose + markers
├── homeworks/<id>.md        # generated
├── boards/<id>.md           # generated
├── decisions/*.md           # authored, unchanged
└── assets/vendor/katex/0.19.0/{katex.min.js,katex.min.css,contrib/auto-render.min.js,fonts/*.woff2,LICENSE}
generated.manifest           # NEW, committed, JSON
requirements-docs.txt        # NEW
mkdocs.yml                   # NEW, generated
```

### Pattern 1: Plan-then-apply with byte-exact classification

**What:** every subcommand computes the complete output set in memory, classifies each target,
prints `PATH: STATUS — reason`, and only then writes. `--check` stops after printing.
**When to use:** the whole generator, with no exceptions.
**Why:** `scripts/new_homework` already proves this shape (`[VERIFIED: scripts/new_homework:39-42]`:
"The plan is the production algorithm (D-21): compute every rendered file in memory, classify
every target, validate the candidate … print the records, and only then write."). Reusing it
means one mental model, one set of semantics, and one test vocabulary for both tools.

### Pattern 2: Marker-region ownership

**What:** a file the generator only partly owns carries a begin marker that names the region and a
single end marker.
**When to use:** `README.md` and `docs/index.md` only.
**Example:**

```markdown
<!-- BEGIN GENERATED: homeworks -->
| ID | Project | Board | Framework | Status | Report |
|----|---------|-------|-----------|--------|--------|
| 1.3 | [1.3 Police Flasher](homeworks/1_3-police-flasher/) | esp32-s3-devkitc-1 | arduino | in-progress | [report](homeworks/1_3-police-flasher/report.md) |
<!-- END GENERATED -->
```

The end marker carries no region name (D-14 spells it `<!-- END GENERATED -->`), so the
generator must refuse a file that contains more than one begin marker or whose end marker
precedes its begin marker — otherwise "the region" is ambiguous.

### Pattern 3: Fragment substitution, never a template language

**What:** repeated blocks arrive pre-rendered as single placeholders; the renderer performs one
non-recursive `{{name}}` pass.
**When to use:** `{{homework_rows}}`, `{{nav_entries}}`, `{{workspace_folders}}`,
`{{decision_entries}}`, `{{board_homework_list}}`.
**Why:** D-20 forbids loops; the existing regex is `\{\{([^{}]*)\}\}`
`[VERIFIED: scripts/new_homework:85]` and refuses `${...}` `[VERIFIED: scripts/new_homework:86]`.
The renderer never re-scans its own output, so a homework title containing `{{...}}` cannot
trigger a second substitution — that property must be preserved when the renderer moves to
`scripts/metadata/render.py`.

### Pattern 4: Manifest as the ownership ledger

**What:** one committed JSON file lists every generated path, its ownership mode and the SHA-256
of the bytes the generator produced.
**When to use:** `--check` and write mode both; the manifest is the only authority on "this file
is ours".

Suggested shape (Claude's discretion per the Decisions, but this shape makes all four drift
classes detectable):

```json
{
  "version": 1,
  "entries": [
    {
      "path": "README.md",
      "owner": "readme",
      "mode": "region",
      "marker_begin": "<!-- BEGIN GENERATED: homeworks -->",
      "marker_end": "<!-- END GENERATED -->",
      "sha256": "…",
      "bytes": 1234
    },
    {
      "path": "mkdocs.yml",
      "owner": "nav",
      "mode": "whole",
      "sha256": "…",
      "bytes": 2345
    }
  ]
}
```

Rules that make it work:

- entries sorted by `path`; two-space indent; one trailing newline; no timestamps, no
  environment data;
- the manifest **never lists itself** — its own correctness is proven by recomputing it and
  comparing bytes with the committed copy;
- `mode: "region"` hashes the region body **including both markers**, so an authored prose edit
  outside the region is not drift and a moved marker is;
- `owner` is the subcommand name, so a single-subcommand run rewrites only its own entries and a
  single-subcommand `--check` checks only its own entries.

### Anti-Patterns to Avoid

- **A second YAML writer.** Do not emit `mkdocs.yml` by dumping a Python dict with PyYAML — key
  order, quoting and anchors become unreadable in review, and D-06 says a reviewed template owns
  the file. Render text from `templates/views/`.
- **Regenerating inside the pre-commit hook.** D-21 forbids it: the hook must fail and print the
  command, never write or stage.
- **A hand-maintained `nav:` fragment beside a generated one.** The whole `mkdocs.yml` is one
  template; a "base + generated include" split (`INHERIT:`) is a second owner.
- **Deriving the repository URL from `git remote` at generation time.** It makes the fixture
  tests depend on a remote that a `tempfile` checkout does not have. Use a module constant
  (precedent: `BOARD = "esp32-s3-devkitc-1"` at `[VERIFIED: scripts/new_homework:94]`).
- **Lexicographic homework ordering.** `1_10-x` sorts before `1_3-y` as text. Order by
  `(int(module), int(lesson), slug)`.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Static site generation, nav trees, link rewriting | A custom Markdown→HTML pipeline | MkDocs + Material | Out of Scope in REQUIREMENTS.md: "Custom static site generator — reinvents MkDocs; creates maintenance burden." |
| Math delimiters | A regex that finds `$…$` in Markdown | `pymdownx.arithmatex` `generic: true` + KaTeX auto-render | Arithmatex handles escaping, code spans and fenced blocks; a regex breaks on `$` in code. Verified: it emits `<span class="arithmatex">\(x^2\)</span>` `[VERIFIED: local probe]`. |
| KaTeX page integration | A custom `<script>` that queries `.arithmatex` | `renderMathInElement` from `contrib/auto-render.min.js` inside `document$.subscribe(...)` | Material's instant loading swaps the body; `document$` is Material's own observable and the documented integration point `[CITED: squidfunk.github.io/mkdocs-material/reference/math]`. |
| INI parsing | A line splitter for `platformio.ini` | `configparser.ConfigParser(interpolation=None)` | Already the repository's approach `[VERIFIED: scripts/metadata/contract.py:441]`; verified to parse all four real INI files this session. |
| `extends`/`lib_deps` semantics | A second implementation | Extract `scripts/check_architecture.py`'s `_option`, `_extends_targets`, `_dep_names` into `scripts/metadata/platformio.py` | A divergent copy would let a dependency pass the architecture gate and vanish from the affected set. |
| Hashing | A custom checksum | `hashlib.sha256` | Stdlib, collision-resistant, and the checksum test needs nothing more. |
| Link validation | A custom Markdown link checker | MkDocs' own `validation:` block + `--strict` | Verified: it already fails on a broken `.md` link, a missing nav target and a missing anchor. |
| Git diff parsing | A path heuristic over `git status` | `git diff --name-only -z` (+ `git merge-base` for PRs) | NUL-separated output survives spaces and newlines; `merge-base` is the only correct base for a PR. |
| JSON serialization | String concatenation | `json.dumps(..., indent="\t", ensure_ascii=False)` + `\n` | The editor itself writes `homeworks.code-workspace` with tabs; matching it prevents a rewrite churn on the first folder add. |

## Runtime State Inventory

This phase converts three hand-authored files into generated ones. It is not a rename, but it is
a state migration, and the same question applies: *after every file is updated, what runtime
system still holds the old bytes?*

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | None — no database, datastore or serialized cache holds any generated view. Verified by `git ls-files` (333 tracked paths, none outside the repository). | None |
| Live service config | GitHub Pages publishing source. If the repository is currently set to "Deploy from a branch", the first `deploy-pages` run fails; the setting must be switched to "GitHub Actions" once, in the UI `[CITED: deploy-pages README, "If your Pages site is using a source branch …"]`. | One-time manual setting, recorded in the plan as a human step |
| OS-registered state | None. No launchd/systemd/pm2/task-scheduler entry names any generated path. | None — verified by inspection of the repository (tooling is `uv`, `pio`, `pre-commit` only) |
| Secrets / env vars | None new. The Pages job needs `pages: write` and `id-token: write` on `GITHUB_TOKEN`; no secret is created. | None |
| Build artifacts | `.pio/build/**` caches the resolved `platformio.ini` + `platformio.shared.ini`. A regenerated shared ini with an unchanged pin does not invalidate it; a changed pin does, and PlatformIO re-resolves on its own. `compile_commands.json` (gitignored) embeds the ini contents too. | No action; document that a pin change requires no manual cache clear. |
| IDE state (F-18) | `homeworks.code-workspace` is open in the editor; VS Code rewrites it on folder add, and the PlatformIO IDE writes `homeworks/<id>/.gitignore` and `.vscode/*`. The root `.gitignore` now covers the inner scaffolding (STATE, 2026-10-25), and the inner `.gitignore` **is tracked** at `homeworks/1_3-police-flasher/.gitignore`. | The generator must emit the workspace in the editor's own format (tabs) so a re-save is byte-identical. Do **not** generate the inner `.gitignore` (D-25). |
| Site build output | `site/` is gitignored `[VERIFIED: .gitignore]` and listed in the `no-generated-files` hook `[VERIFIED: .pre-commit-config.yaml:42-44]`. | None — but the docs workflow must build into `site/` and never into a tracked path. |

## Existing artifacts the generator must preserve or replace

| Artifact | Current state (verified this session) | Generator action |
|----------|----------------------------------------|------------------|
| `README.md` | Four-column table at line 15: `| ID | Project | Status | Report |`; no markers | Insert the two markers around the table and replace it with the six-column D-11 table. Authored prose (intro, "**Status:** the first homework…", Repository rules, Decisions, License) stays byte-identical. The intro paragraph is already stale ("Phase 4.2") — fix it in the same commit, by hand. |
| `homeworks.code-workspace` | Two folders (`"."` and `homeworks/1_3-police-flasher`), no `name` keys, tab indent, an `extensions` block with one recommendation and two unwanted ones | Replace whole. Emit `{"name": …, "path": …}` with `repo → "."`, `docs → "docs"`, `lib → "lib"`, `scripts → "scripts"`, then every homework. Keep `extensions` verbatim in the template. Serialize with `indent="\t"`. |
| `platformio.shared.ini` | Three sections `[esp32s3_arduino]`, `[esp32s3_espidf]`, `[native_unity]` at lines 1, 18, 31; a five-line SCons comment block above `[native_unity]` that must survive | Replace whole from a template that carries the comment verbatim. Substitute only the two pin values; add a generated-file header so the Core pin has a home (it has none today). |
| `AGENTS.md` | Line 39: ``Planned: `docs/standards/` (report structure, Phase 5)``; line 192: ``| Report structure and formatting rationale | `docs/standards/` (planned, Phase 5) |`` | Correct **both** lines (D-12). Moving only line 39 leaves the routing table lying. |
| `docs/decisions/` | Twelve tracked Markdown files; every relative link stays inside the directory (18 relative links, all `NNNN-*.md`) | Do not move or rewrite. The generated nav lists all twelve; `README.md` becomes the directory index (verified below). |
| `docs/decisions/README.md` | Table header at line 12: `| Date | Decision | Why | Change cost | Status | Record |` | Untouched; rendered as `decisions/index.html`. |
| `templates/board-profile/profile.yaml` | Fields `id`, `soc`, `flash_mb`, `psram`, `frameworks`, `pinout_url` — no placeholders | Copy to `boards/esp32-s3-devkitc-1.yaml` and pin the shape with a schema (D-27). |
| `templates/homework-arduino/template.yaml` | `framework`, `description` — a scaffold manifest, not metadata | Untouched by this phase. |
| `.pre-commit-config.yaml` | Three local hooks; `check-metadata` uses `language: python`, `additional_dependencies: ["PyYAML==6.0.3", "jsonschema==4.26.0"]`, `files:` regex, `pass_filenames: false` | Add `gen-views-check` following the same shape, with **only** `PyYAML==6.0.3`. |
| `.github/workflows/homework.yml` | Single project job, `runs-on: ubuntu-24.04`, `timeout-minutes: 45`, actions pinned by SHA with a comment | Untouched. The drift job and the docs job are new files. |
| `.gitignore` | `site/`, `compile_commands.json`, root-anchored generated patterns | No change needed — generated docs pages must **not** be ignored. |

## Common Pitfalls

### Pitfall 1: A nav entry written as one quoted scalar
**What goes wrong:** `- "1.3 Police Flasher: homeworks/1_3-police-flasher.md"` yields a single nav
label containing the colon, and MkDocs then warns that the whole string is not a document.
**Why it happens:** YAML forbids a colon inside an unquoted scalar; quoting the whole entry does
not help, because the colon is then part of the scalar rather than the key separator.
**How to avoid:** emit `- "Title": path` with the colon **unquoted** between key and value.
**Warning signs:** `A reference to '<page>: <path>' is included in the 'nav' configuration, which is
not found in the documentation files.` — reproduced and fixed this session `[VERIFIED: local probe]`.

### Pitfall 2: `omitted_files: warn` turns every stray page into a build failure
**What goes wrong:** with the strict validation block, adding an ADR to `docs/decisions/` without
regenerating `mkdocs.yml` fails the build, and the real tree fails immediately because the twelve
authored ADRs are not in nav.
**Why it happens:** `validation.nav.omitted_files: warn` makes `--strict` fail on any Markdown file
under `docs_dir` absent from `nav:` `[VERIFIED: local probe, F]`.
**How to avoid:** generate the Decisions section from a sorted `docs/decisions/*.md` scan, or leave
`omitted_files` at its default (`info`). Recommend generating the section — it keeps the strict
gate meaningful.
**Warning signs:** `The following pages exist in the docs directory, but are not included in the
"nav" configuration:`.

### Pitfall 3: A relative link out of `docs/` becomes a hard build failure
**What goes wrong:** linking `../../homeworks/<id>/report.md` from a generated page makes MkDocs
treat it as a docs-relative `.md` target, which does not exist.
**Why it happens:** `validation.links.not_found` is `warn` by default and `--strict` promotes it
`[VERIFIED: local probe, A and E]`.
**How to avoid:** every outbound link to a homework artefact is an absolute `https://github.com/…`
URL built from a module constant. Absolute external URLs produce no warning.
**Warning signs:** `Doc file 'homeworks/x.md' contains a link '…', but the target is not found among
documentation files.`

### Pitfall 4: A missing vendored asset is silent
**What goes wrong:** `extra_css` / `extra_javascript` pointing at a file that does not exist produces
**no warning at all**, and `--strict` still exits 0. So does a `katex.min.css` whose 20 font files
were never vendored — MkDocs never reads CSS.
**Why it happens:** MkDocs resolves theme/`extra_*` paths leniently and does not parse CSS
`url(...)` references `[VERIFIED: local probe, A and I]`.
**How to avoid:** the D-07 checksum test is the *only* mechanism. It must assert the presence and
SHA-256 of all 24 vendored files, not just the three scripts.
**Warning signs:** none from MkDocs — the page renders with raw `\(x^2\)` text in the browser.

### Pitfall 5: `docs/decisions/README.md` is the directory index, not a page called `README`
**What goes wrong:** assuming `decisions/README.md` publishes at `decisions/README/` and linking to
that URL.
**Why it happens:** MkDocs maps `README.md` to the directory index.
**How to avoid:** link to `decisions/` (it builds `decisions/index.html`) `[VERIFIED: local probe]`.

### Pitfall 6: The pin cycle between `homework.yaml` and `platformio.shared.ini`
**What goes wrong:** the generator wants to substitute the pin **from** `homework.yaml` while
`check_metadata.py` validates `homework.yaml`'s pin **against** `platformio.shared.ini`
`[VERIFIED: scripts/metadata/contract.py:558-566]`. With two homeworks declaring different pins,
"the" pin is undefined.
**Why it happens:** D-16 makes the ini a projection of the metadata, and the checker treats the ini
as the authority.
**How to avoid:** collect the distinct `(toolchain.platformio, toolchain.platform)` pairs across all
homeworks; zero homeworks → exit 2 ("no metadata to derive the pins from"); more than one distinct
pair → exit 1 naming every disagreeing homework. Never pick one arbitrarily.
**Warning signs:** a generated ini that silently encodes one homework's pin while another homework
declares a different one.

### Pitfall 7: `configparser` treats `:` as a delimiter
**What goes wrong:** a hand-rolled "split on `=`" reader works on today's files and breaks on a value
containing `=`; conversely `configparser` with default delimiters splits `pre:../../scripts/…` on
its first `:` if `=` is absent.
**Why it happens:** `ConfigParser` defaults to `delimiters=('=', ':')`.
**How to avoid:** use `ConfigParser(interpolation=None)` exactly as the repository already does
`[VERIFIED: scripts/metadata/contract.py:441]`; verified this session to parse
`platformio.shared.ini`, both homework INIs, the Arduino template and `tests/platformio.ini`
(all `lib_deps` values returned with a leading `\n` — strip before splitting lines).
**Warning signs:** a `lib_deps` value of `pre:../../scripts/pio/compiledb.py` reappearing under the
wrong key.

### Pitfall 8: `framework` is inherited, not declared
**What goes wrong:** `affected.py` reads `[env:esp32s3_arduino]` from the homework's
`platformio.ini`, finds no `framework` key, and emits an empty value.
**Why it happens:** the value lives in the **shared** ini, reached through `extends`, which is
reached through `extra_configs = ../../platformio.shared.ini`
`[VERIFIED: homeworks/1_3-police-flasher/platformio.ini:6]` (`lib_deps` sits at lines 14 and 36).
`check_architecture.py` does not need the
shared file because every env repeats `lib_deps`; `affected.py` does need it for `framework`.
**How to avoid:** load the homework ini, then `parser.read()` the files named by
`[platformio] extra_configs`, resolved **relative to the project directory** (`../../` for a
homework, `../` for `tests/`), then walk `extends`.
**Warning signs:** `"framework": ""` for an `esp32s3_arduino` environment.

### Pitfall 9: Library dependencies are declared nowhere today
**What goes wrong:** D-23 expects the `lib/<name>/library.json` `dependencies` field to supply
transitive edges. All five real manifests carry only `name`, `version` and `build`
`[VERIFIED: lib/common/library.json:1-8]` — `common → port` is absent.
**Why it happens:** PlatformIO would try to resolve a bare `"port": "*"` from the registry, so nobody
wrote it.
**How to avoid:** treat a missing `dependencies` key as "leaf" and rely on the fail-safe rule; and
because every current project lists `port` **directly**, the one real edge is already covered.
Record the gap explicitly in the plan; do **not** invent a registry-shaped dependency.
**Warning signs:** a `lib/port` change that fails to reach a future project which lists only
`common`.

### Pitfall 10: Material's MkDocs 2.0 banner is not a warning
**What goes wrong:** assuming the big red "MkDocs 2.0" box will fail `--strict`.
**Why it happens:** it goes to stderr but does not go through MkDocs' warning counter.
**How to avoid:** nothing — a probe with a clean tree exits 0 with the banner present
`[VERIFIED: local probe, B and I]`. Do not "fix" it by downgrading.

### Pitfall 11: The Pages artefact rejects symlinks and hidden files
**What goes wrong:** a symlinked directory in `site/` makes `upload-pages-artifact` fail; a needed
dotfile is silently dropped.
**Why it happens:** the artefact spec says the tar "must not contain any symbolic or hard links";
`include-hidden-files` defaults to `false` `[CITED: upload-pages-artifact README]`.
**How to avoid:** `docs/` contains no symlinks today (verified); the generator must never create
one; nothing the site needs is a dotfile.

### Pitfall 12: An LFS pointer can reach the artefact unnoticed
**What goes wrong:** a binary committed through LFS is referenced by the site; a checkout without
LFS leaves a 130-byte pointer file that gets copied into `site/` and served as the image.
**Why it happens:** Pages cannot serve LFS objects; a default checkout does not fetch them.
**How to avoid:** the site references no LFS-tracked path (D-02 links out; `.gitattributes` keeps
`*.png`/`*.svg` as normal git objects), so check out **without** LFS and add a one-line guard that
fails the job if `site/` contains `git-lfs.github.com/spec/v1`.

## Code Examples

### `mkdocs.yml` skeleton that passes `--strict` on this tree

Verified end to end against the real `docs/` directory (exit 0) `[VERIFIED: local probe, /tmp/mkdocs-real]`:

```yaml
site_name: Homeworks
site_url: https://vloktiev-emb.github.io/homeworks/
theme:
  name: material
  features:
    - navigation.sections
    - navigation.top
    - content.code.copy
  palette:
    - media: "(prefers-color-scheme: light)"
      scheme: default
      toggle: {icon: material/brightness-7, name: Switch to dark mode}
    - media: "(prefers-color-scheme: dark)"
      scheme: slate
      toggle: {icon: material/brightness-4, name: Switch to light mode}
plugins:
  - search
nav:
  - Home: index.md
  - Homeworks:
{{homework_nav_entries}}
  - Boards:
{{board_nav_entries}}
  - Decisions:
      - Decision record index: decisions/README.md
{{decision_nav_entries}}
validation:
  nav:
    omitted_files: warn
    absolute_links: warn
  links:
    not_found: warn
    absolute_links: warn
    unrecognized_links: warn
    anchors: warn
markdown_extensions:
  - admonition
  - attr_list
  - def_list
  - footnotes
  - md_in_html
  - tables
  - toc:
      permalink: true
  - pymdownx.details
  - pymdownx.superfences
  - pymdownx.tabbed:
      alternate_style: true
  - pymdownx.arithmatex:
      generic: true
  - pymdownx.highlight:
      anchor_linenums: true
      line_spans: __span
  - pymdownx.inlinehilite
  - pymdownx.keys
  - pymdownx.tasklist:
      custom_checkbox: true
extra_css:
  - assets/vendor/katex/0.19.0/katex.min.css
extra_javascript:
  - assets/vendor/katex/0.19.0/katex.min.js
  - assets/vendor/katex/0.19.0/contrib/auto-render.min.js
  - assets/vendor/katex/0.19.0/render-math.js
```

`site_url` must be the **project** URL (repository name included), not the apex; the owner is
lower-cased by Pages. `docs_dir` and `site_dir` are left at their defaults (`docs`, `site`).

### KaTeX: exactly which files to vendor

24 files, ~600 KB total `[VERIFIED: npm pack katex@0.19.0, file listing and sizes]`:

```text
docs/assets/vendor/katex/0.19.0/
├── LICENSE                             # 1,107 B — MIT, Khan Academy and contributors
├── katex.min.css                       # 24,793 B
├── katex.min.js                        # 272,868 B
├── contrib/auto-render.min.js          # 3,486 B
├── render-math.js                      # ~20 lines, authored (below)
└── fonts/                              # 20 × .woff2, ~296 KB total
    KaTeX_AMS-Regular.woff2
    KaTeX_Caligraphic-Bold.woff2  KaTeX_Caligraphic-Regular.woff2
    KaTeX_Fraktur-Bold.woff2      KaTeX_Fraktur-Regular.woff2
    KaTeX_Main-Bold.woff2         KaTeX_Main-BoldItalic.woff2
    KaTeX_Main-Italic.woff2       KaTeX_Main-Regular.woff2
    KaTeX_Math-BoldItalic.woff2   KaTeX_Math-Italic.woff2
    KaTeX_SansSerif-Bold.woff2    KaTeX_SansSerif-Italic.woff2
    KaTeX_SansSerif-Regular.woff2 KaTeX_Script-Regular.woff2
    KaTeX_Size1-Regular.woff2     KaTeX_Size2-Regular.woff2
    KaTeX_Size3-Regular.woff2     KaTeX_Size4-Regular.woff2
    KaTeX_Typewriter-Regular.woff2
```

`katex.min.css` declares `src: url(fonts/<name>.woff2) format("woff2"), url(fonts/<name>.woff)
format("woff"), url(fonts/<name>.ttf) format("truetype")` — the `fonts/` directory must sit beside
the CSS, and a browser takes the first source that loads. `.woff2`-only is sufficient for every
browser that renders Material 9; the `.woff`/`.ttf` fallbacks add ~900 KB for no user.

```javascript
// docs/assets/vendor/katex/0.19.0/render-math.js
// Source: squidfunk.github.io/mkdocs-material/reference/math (delimiter shape)
document$.subscribe(({ body }) => {
  renderMathInElement(body, {
    delimiters: [
      { left: "$$",  right: "$$",  display: true  },
      { left: "$",   right: "$",   display: false },
      { left: "\\(", right: "\\)", display: false },
      { left: "\\[", right: "\\]", display: true  }
    ]
  });
});
```

### `affected.py` output

```json
{
  "build": [
    {"project": "homeworks/1_3-police-flasher", "env": "esp32s3_arduino", "framework": "arduino"}
  ],
  "simulate": [
    {"project": "homeworks/1_3-police-flasher", "env": "esp32s3_arduino", "framework": "arduino"}
  ]
}
```

Sorted by `(project, env)`; native environments appear in `build` only; `simulate` excludes native
and any project whose `simulation.tool` is `none`. Diagnostics go to stderr so Phase 8 can consume
stdout unchanged.

### Git diff input

```bash
# CI: the PR's merge base, NUL-separated so spaces survive
git merge-base "origin/$BASE_REF" HEAD
git diff --name-only -z "$BASE...HEAD"

# tests: no git required for the unit cases
printf 'lib/common/src/x.c\0homeworks/1_3-police-flasher/src/main.cpp\0' > paths.txt
uv run scripts/affected.py --paths-from paths.txt
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `mkdocs gh-deploy` (pushes a branch) | `upload-pages-artifact` + `deploy-pages` (OIDC, no branch) | GitHub's Pages-from-Actions default | No branch bypasses protection; the artefact must be symlink-free and <1 GB |
| CDN-hosted KaTeX/MathJax | Vendored KaTeX + `document$` re-render | Material's instant-loading became standard | Offline-capable, reproducible `--strict` builds, and a real drift surface (checksum test) |
| `mkdocs-material` as the long-term answer | Material in maintenance, EOL 2027-05-05; Zensical is the successor | 9.7.0 (2025-11-11) | Config must stay Zensical-compatible now, not at migration time |
| `mkdocs-gen-files` for virtual pages | Committed generated pages | Zensical silently ignores it | Drift detection must be explicit (`generated.manifest`), which D-01/D-17 chose |
| `mkdocs-material` 9.8.0 | Pinned 9.7.7 | 9.8.0 published 2026-10-24 | META-08 names 9.7.7; a bump is a separate reviewed change |

**Deprecated/outdated:**
- `mkdocs<2` is a hard constraint from Material 9.7.5+, not a preference.
- `lib_extra_dirs` remains a generator fallback only (`ARCH-04`); this phase does not touch it.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Zensical silently ignores `validation:` (it is neither a plugin nor `hooks`), so including it keeps the config compatible | §Zensical constraints | A future Zensical build could error on an unknown top-level key instead of ignoring it; mitigation: `validation:` is a small, easily removed block |
| A2 | Zensical honours `extra_css`/`extra_javascript` with `theme.name: material` | §Zensical constraints | Its own docs only promise that "additional CSS and JavaScript work without changes when using the classic theme"; the modern theme "depend[s] on its established appearance". If it dropped them, math would stop rendering after migration — acceptable, because migration is Q1 2027 and the config is still reviewable |
| A3 | `platformio.shared.ini` is not read by any other tool expecting the current byte layout | §Pitfall 6 | `check_metadata.py` and `new_homework` both read it through `configparser`, so cosmetic changes are safe; a *pin* change cascades into every homework's metadata |
| A4 | The repository's Pages source is, or will be switched to, "GitHub Actions" | §Runtime State Inventory | If it stays branch-based, `deploy-pages` fails at the environment check and the deploy must be flipped in the UI |
| A5 | Twenty `.woff2` fonts are sufficient; the `.woff`/`.ttf` fallbacks are unnecessary | §KaTeX | A very old browser would show unstyled math glyphs. Low; the site targets a course audience |
| A6 | `docs/` will never contain a symlink or an LFS-tracked file that the site copies | §Pitfall 12 | A future asset would break the artefact upload or serve a pointer; the guard step makes it fail loudly instead |

## Open Questions

1. **Does the fail-safe widening rule make every docs edit rebuild every project?**
   - What we know: D-24 says "any unrecognised shared path widens to every project (fail-safe)".
     Read literally, a `docs/` or `.planning/` edit widens to all 30 projects.
   - What's unclear: whether "shared path" means "a path the build can consume" (then `docs/` is
     not shared) or "any path outside `homeworks/<id>/`".
   - Recommendation: implement an explicit, tested `NO_BUILD_IMPACT` set (`.planning/`, `docs/`,
     `README.md`, `AGENTS.md`, `LICENSE`, `.github/`) that yields an empty matrix, and keep the
     fail-safe for **everything else**. Record the set in `affected.py`'s docstring and one test.
     The planner should confirm this reading with the user rather than silently widening.

2. **Does `gen_views.py nav` own the whole `mkdocs.yml`?**
   - What we know: D-13 lists `nav` as a subcommand; D-06 says the whole `mkdocs.yml` is generated
     from one template.
   - What's unclear: nothing has a `mkdocs` subcommand name, so `nav` must be the one that renders
     the file.
   - Recommendation: keep the name (locked) and document it in the module docstring as
     "render `mkdocs.yml`, including `nav`". Do not add a fifth alias.

3. **Should write mode delete orphaned generated files?**
   - What we know: D-17 requires `--check` to detect "newly appearing" files; a renamed homework
     leaves its old page on disk.
   - What's unclear: whether the generator may delete.
   - Recommendation: write mode deletes a path **only** when the previous manifest listed it
     (so it is provably generator-owned) **and** the file still starts with the
     `GENERATED — do not edit` header; report it as `DELETE`. Never delete anything the manifest
     did not list.

4. **Is the KaTeX checksum a committed list or a recomputed hash?**
   - What we know: D-07 says "checksum test".
   - Recommendation: a committed `docs/assets/vendor/katex/0.19.0/FILES.sha256` in `sha256sum -c`
     format, generated once from the npm tarball, checked by a stdlib test with `hashlib`. It
     documents provenance and catches a partial copy.

5. **Should the drift job and the Pages deploy be one workflow file or two?**
   - Recommendation: two files. `docs.yml` (build + deploy on `main`, `workflow_dispatch`) and
     `generated-views.yml` (drift on `pull_request`). A single file would need the deploy job
     skipped on PRs anyway, and Phase 8's `meta` job will want a third.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| `uv` | Running every PEP 723 entry point and the tests | ✓ | 0.13.5 | `python3` + `pip install` (breaks the reproducibility story) |
| `python3` | Generator, checker, tests | ✓ | 3.13.13 (system); 3.14.7 under `uv` default | Pin `--python 3.13` in CI and locally |
| `git` | `resolve_root`, `affected.py`, `no-generated-files` | ✓ | system | none — required |
| `mkdocs` | Local site build | ✗ (not installed globally) | — | `uv run --with-requirements requirements-docs.txt …` (verified working) |
| `pio` | Nothing in this phase (the generator must never invoke PlatformIO — CONTEXT "Determinism") | ✓ | 6.2.0 | — |
| `pre-commit` | The drift hook | ✓ (hook framework already in use) | — | CI job |
| Network to PyPI/npm | First `uv run` of the docs stack; one-time KaTeX vendoring | ✓ | — | KaTeX is committed; only the docs deps need the network |

**Missing dependencies with no fallback:** none.
**Missing dependencies with fallback:** `mkdocs` — use the `uv run --with-requirements` form; do not
add it to a global environment.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | `unittest` (stdlib), discovered from the repository root |
| Config file | none — `python3 -m unittest discover -s scripts/tests -v` `[CITED: docs/decisions/0010-python-dependency-policy.md:19]` |
| Quick run command | `python3 -m unittest discover -s scripts/tests -v` (~ the current 81 tests; keep the new generator tests inside this budget by using `--paths-from` for `affected.py` units) |
| Full suite command | Same, plus `uv run --with-requirements requirements-docs.txt mkdocs build --strict` as a separate CI step |

### Phase Requirements → Test Map

Status legend: ✅ exists today; ❌ Wave 0 (must be created this phase).

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| META-05 | `readme`/`workspace`/`nav`/`docs`/`shared-ini` are idempotent: a second run is all `UNCHANGED` and every authored byte outside a marker region is untouched | unit (subprocess) | `python3 -m unittest scripts.tests.test_gen_views.IdempotencyTests -v` | ❌ Wave 0 |
| META-05 | `--check` exits 1 on a modified generated byte, on a deleted file, and on an orphan the manifest no longer lists | unit | `…test_gen_views.DriftTests -v` | ❌ Wave 0 |
| META-05 | The committed manifest is itself in sync (recompute + byte-compare) | unit | `…test_gen_views.ManifestTests -v` | ❌ Wave 0 |
| META-05 | `--check` on the **real** tree exits 0 (smoke) | smoke | `…test_gen_views.RealTreeSmokeTest -v` | ❌ Wave 0 |
| META-05 | Two homeworks with different `toolchain.platform` make `shared-ini` exit 1 and name both | unit | `…test_gen_views.SharedIniTests -v` | ❌ Wave 0 |
| META-06 | `lib/<name>` fans out to its consumers; `platformio.shared.ini`/`partitions/`/`schema/`/`scripts/pio/` fan out to every project; an unknown shared path widens to every project | unit | `python3 -m unittest scripts.tests.test_affected.FanoutTests -v` | ❌ Wave 0 |
| META-06 | `framework` resolves through `extra_configs` + `extends` (`arduino`, `espidf`, `native`) | unit | `…test_affected.FrameworkTests -v` | ❌ Wave 0 |
| META-06 | End to end in a `tempfile` repo with a real `git init`, a real commit and a real diff | integration | `…test_affected.EndToEndTests -v` | ❌ Wave 0 |
| META-07 | The workspace has exactly `repo`, `docs`, `lib`, `scripts` plus every homework; every `path` is ASCII; the file parses as JSON | unit | `…test_gen_views.WorkspaceTests -v` | ❌ Wave 0 |
| META-08 | `requirements-docs.txt`, the versions named in `mkdocs.yml`, and the vendored KaTeX version agree | unit | `…test_docs_pins.PinConsistencyTests -v` | ❌ Wave 0 (the predecessor was deleted in `597bd7a`) |
| META-08 | All 24 KaTeX files exist and match `FILES.sha256` | unit | `…test_docs_pins.KatexVendoringTests -v` | ❌ Wave 0 |
| META-08 | `mkdocs build --strict` exits 0 | CI only | `uv run --with-requirements requirements-docs.txt mkdocs build --strict` | ❌ Wave 0 (CI step) |

### Sampling Rate

- **Per task commit:** `python3 -m unittest discover -s scripts/tests -v`
- **Per wave merge:** the same, plus `pre-commit run --all-files`
- **Phase gate:** the full suite green, `mkdocs build --strict` green, and `--check` green on the real tree

### Wave 0 Gaps

- [ ] `scripts/tests/test_gen_views.py` — META-05, META-07
- [ ] `scripts/tests/test_affected.py` — META-06
- [ ] `scripts/tests/test_docs_pins.py` — META-08 pins and KaTeX checksums
- [ ] `scripts/tests/temp_root.py` — a second builder (or new `COPIED_PATHS` entries) for `boards/`,
      `docs/`, `templates/views/`; today it copies only `platformio.shared.ini`, `partitions`,
      `schema`, `templates`, `scripts/pio` `[VERIFIED: scripts/tests/temp_root.py:31-37]`
- [ ] A real-tree smoke helper that runs `--check` with `--dir <repo>` and asserts exit 0 without
      writing (the pattern already exists for the checker's real-tree JSON test, STATE 04.2)
- [ ] `requirements-docs.txt`

## Security Domain

`security_enforcement` is enabled and `security_asvs_level` is 1.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | — (no user-facing auth) |
| V3 Session Management | no | — |
| V4 Access Control | yes | The Pages job gets `contents: read`, `pages: write`, `id-token: write` and nothing else; the drift job gets `contents: read` only |
| V5 Input Validation | yes | `homework.yaml` and `boards/*.yaml` are data. Values that can contain `|`, newlines or backticks must be escaped before entering a Markdown table cell; `additionalProperties: false` already bounds the key set. The board-profile schema must repeat that rule |
| V6 Cryptography | yes | `hashlib.sha256` for the manifest and the KaTeX checksums; never a hand-rolled digest |
| V12 Files and Resources | yes | Every write goes through an `lstat`-checked path with a containment proof (reuse `new_homework`'s `_component_conflict` / `_contained_target`, `[VERIFIED: scripts/new_homework:251-382]`); writes are `os.replace` from a temp file in the target directory |
| V14 Configuration | yes | No secret is introduced; the workflow declares minimal `permissions:` |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Markdown/HTML injection through `homework.yaml` `title` (a `|` breaks a table; raw HTML passes through `md_in_html`) | Tampering | Escape `\|` in table cells, strip control characters and newlines from single-line fields, and never emit raw HTML from a metadata value |
| Path traversal through a symlinked `docs/`, `boards/` or `homeworks/` component | Tampering / Elevation | The `lstat` component walk from `new_homework`; refuse a symlink at any component, including the final one |
| Absolute path disclosure in `--json` diagnostics | Information disclosure | Reuse `relative_path()` `[VERIFIED: scripts/metadata/contract.py:398-408]`; an out-of-root path reduces to its final component |
| LFS pointer served as a site asset | Tampering / Repudiation | Check out without LFS; fail the docs job if `site/` contains `git-lfs.github.com/spec/v1` |
| Over-broad workflow token used to push to `main` | Elevation | `deploy-pages` uses OIDC and a `github-pages` environment; no `contents: write`, no `gh-pages` branch |
| Untrusted content executed from the vendored tarball | Elevation | KaTeX is copied as static files; nothing in the build imports it |

## Sources

### Primary (HIGH confidence)
- Context7 `/websites/mkdocs` — strict mode, the `validation` block, `--strict` CLI semantics
  (`[CITED: mkdocs.org/user-guide/configuration]`, `mkdocs.org/user-guide/cli`)
- Context7 `/squidfunk/mkdocs-material` — KaTeX + `pymdownx.arithmatex` configuration and the
  `document$` re-render (`[CITED: squidfunk.github.io/mkdocs-material/reference/math]`)
- Context7 `/platformio/platformio-docs` — `symlink://` package spec and `library.json`
  `dependencies` (`[CITED: docs.platformio.org]`)
- PyPI JSON for `mkdocs-material==9.7.7` — `requires_python >=3.8`,
  `mkdocs<2,>=1.6`, `pymdown-extensions>=10.2`, upload 2026-07-17
- `npm view katex@0.19.0` and the unpacked tarball — file list, 20 `.woff2`, CSS `@font-face`,
  MIT `LICENSE`
- `docs.github.com` Pages pages and the `deploy-pages` / `upload-pages-artifact` READMEs —
  permissions, `github-pages` environment, artefact constraints
- Local probes run this session with the exact pinned stack (see below)

### Secondary (MEDIUM confidence)
- `zensical.org/docs/compatibility/mkdocs/plugins/` — "Configuration for plugins not listed under
  Supported plugins is silently ignored"; `gen-files` unsupported
- `zensical.org/docs/compatibility/mkdocs/migration/` — `hooks` unsupported; `--theme`,
  `--use-directory-urls`, `--site-dir`, `gh-deploy`, `get-deps` unsupported; "Existing page paths,
  directory URLs, and navigation configuration remain unchanged"
- `zensical.org/docs/compatibility/markdown/python-markdown-extensions/` — `pymdownx.arithmatex`
  with `generic = true` is supported
- Zensical config/theme behaviour (palette, features, variant) — search results citing
  `zensical/zensical` `config.py` and the project's own `mkdocs.yml`; not fetched from the source

### Tertiary (LOW confidence)
- Nothing material. The `validation:` top-level key under Zensical is an explicit assumption (A1).

### Local probes (this session, macOS, `uv 0.13.5`)
- `/tmp/mkdocs-probe-1` — strict failure modes: broken `.md` link (exit 1), missing nav target
  (exit 1), missing anchor with `validation.links.anchors: warn` (exit 1), absolute link with
  `validation.nav.absolute_links: warn` (exit 1), omitted page with `omitted_files: warn` (exit 1),
  missing `extra_css`/`extra_javascript` (**no warning**, exit 0), clean tree (exit 0)
- `/tmp/mkdocs-probe-2` — `docs/decisions/README.md` builds as `decisions/index.html`; the
  `site_url` with a project subpath builds clean
- `/tmp/mkdocs-real` — the **real** `docs/` tree with an explicit 13-entry nav: exit 0
- `/tmp/mkdocs-uv` — `uv run --with-requirements requirements-docs.txt mkdocs build --strict`
  with the three exact pins: exit 0, `mkdocs 1.6.1`, `material 9.7.7`
- `configparser(interpolation=None)` parsed `platformio.shared.ini`,
  `homeworks/1_3-police-flasher/platformio.ini`, `templates/homework-arduino/platformio.ini` and
  `tests/platformio.ini`
- GitHub API `git/ref/tags` resolved `configure-pages@v6` →
  `45bfe0192ca1faeb007ade9deae92b16b8254a0d`, `upload-pages-artifact@v5` →
  `fc324d3547104276b827a68afc52ff2a11cc49c9`, `deploy-pages@v5` →
  `368f82528645a54fb793d4d04e342629a3f51346` (all lightweight commit refs, usable in `uses:`);
  the method re-derived the two SHAs already in `homework.yml` exactly

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — every version, requirement edge and build command was resolved against
  PyPI/npm and executed locally with the exact pins.
- Architecture (generator, manifest, affected.py): HIGH for the mechanisms (reusing `new_homework`
  and `check_architecture.py` idioms, verified file contents); MEDIUM for the two open design
  readings (fail-safe widening breadth, orphan deletion).
- Docs site and publication: HIGH — strict build green on the real tree; artefact rules from the
  action's own README.
- Zensical compatibility: MEDIUM — the plugin and migration pages are explicit, but the treatment of
  `validation:` and of `extra_css` under the modern theme is not stated anywhere.
- Pitfalls: HIGH — nine of the twelve were reproduced in a probe rather than recalled.

**Research date:** 2026-10-25
**Valid until:** 2026-11-24 for the generator/CI parts (30 days, stable). 7 days for the Pages and
Zensical parts — Material 9.8.0 shipped one day before this research and Zensical 0.1.0 is
announced for 2026-11-05, so re-check both before the deploy workflow lands.

## RESEARCH COMPLETE

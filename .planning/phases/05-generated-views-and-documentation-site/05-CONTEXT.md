# Phase 5: Generated Views and Documentation Site - Context

**Gathered:** 2026-10-25
**Status:** Ready for planning

<domain>
## Phase Boundary

Every repeated view of the repository is generated from `homework.yaml`, and a MkDocs
Material documentation site is built from the same metadata tree and deployed to GitHub
Pages. The phase delivers: `scripts/gen_views.py` (README index, multi-root workspace,
`mkdocs.yml` navigation, generated documentation pages, `platformio.shared.ini`) with a
`--check` drift mode; `scripts/affected.py`, which maps a git diff to the build and
simulation matrix; board profiles under `boards/`; the committed documentation site with a
vendored KaTeX; and one CI job that fails on generated-view drift.

The CI **matrix** that consumes `affected.py` is Phase 8. The authored `docs/standards/`
report contract is Phase 10. Report-body embedding on the site is deferred until relative
`assets/` paths are solved. Scaffolding of `lib/pattern` manifests and inner `.gitignore`
files belongs to the scaffold/Phase 9 track, not here.

**Requirements covered:** META-05, META-06, META-07, META-08.

</domain>

<decisions>
## Implementation Decisions

### What is committed and what is authored

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

### Site configuration

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

### Generator surface

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

### Drift gate and affected.py

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

### Scope fences

- **D-25:** The two friction-log candidates outside the roadmap — the private `lib/pattern`
  manifest generator (F-04) and the test scaffold plus inner `.gitignore` (F-05, F-18) — are
  deferred to backlog / Phase 9. They produce project content, not views of `homework.yaml`.
- **D-26:** Phase 5 generates **no** CI matrix. `affected.py` plus the drift job are the
  deliverable; converting them into a matrix is Phase 8 (04.2/D-18, F-14).
- **D-27:** `boards/<id>.yaml` is validated by extending `scripts/check_metadata.py` with a
  board-profile schema, preserving one validator and the 0/1/2 exit-code contract.

### Testing and pins

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

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and requirements
- `.planning/ROADMAP.md` §Phase 5 — goal, success criteria, and requirement mapping (META-05–08)
- `.planning/REQUIREMENTS.md` §Metadata and Documentation — META-05, META-06, META-07, META-08
- `.planning/research/SUMMARY.md` §Phase 8 (docs site) and §Research Findings 6–8 — MkDocs
  lifecycle, Zensical constraints, Pages/LFS interaction

### Decisions that constrain this phase
- `.planning/phases/04-metadata-contract-and-scaffolding/04-CONTEXT.md` — D-01/D-02
  (metadata contract, id-derived identity), D-05 (board id and board profile), D-07
  (toolchain pins), D-10–D-14 (schema, checker, dependency policy, stdlib tests), D-23
  (status vocabulary, exit codes), D-25/D-33 (`{{...}}` substitution, no Jinja)
- `.planning/phases/04.2-tracer-homework-1-3/04.2-CONTEXT.md` — D-17 (no per-homework
  shared-ini entries), D-18 (minimal CI; matrix is Phase 8), D-19 (no tag)
- `.planning/phases/04.2-tracer-homework-1-3/04.2-FRICTION-LOG.md` — F-01, F-14, F-18
  (generated views), F-04/F-05 (deferred candidates), and §Top automation candidates
  (phase ownership)

### Repository contracts and existing artifacts
- `schema/homework.schema.json` — the only metadata contract the generators may read
- `templates/board-profile/` — the board-profile template shape (04/D-32)
- `platformio.shared.ini` — the three environment sections and the SCons comment that must
  survive regeneration
- `homeworks.code-workspace` — the current hand-authored workspace being replaced
- `README.md` — the current hand-authored table and the surrounding prose that stays authored
- `AGENTS.md` — repository rules; its "docs/standards/ (Phase 5)" line is corrected by D-12
- `.pre-commit-config.yaml` — where the drift hook is added
- `.github/workflows/homework.yml` — the existing single-project workflow the drift job
  sits beside
- `docs/decisions/README.md` — the decisions table the site links to

### External references
- `https://zensical.org/docs/compatibility/mkdocs/plugins/` — the explicit statement that
  gen-files is unsupported and unsupported plugin config is silently ignored
- `https://zensical.org/docs/setup/navigation/` — automatic folder navigation and
  `nav` override semantics
- `https://squidfunk.github.io/mkdocs-material/getting-started/` — Material 9.x install and
  the `mkdocs<2` constraint

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `scripts/new_homework` — the production template renderer: plan-first, content-based
  UNCHANGED/CONFLICT, atomic writes, unknown-placeholder errors. The renderer and the
  plan/apply shape are the model for `gen_views.py`.
- `scripts/metadata/` — the shared contract module (`validate_candidate`) reused by the
  scaffold and the checker; the natural home for the extracted renderer and a board-profile
  validator.
- `scripts/check_metadata.py` — single validator with `--json`, exit codes 0/1/2, and the
  "never writes" rule (04/D-11); extend it for `boards/`.
- `templates/board-profile/` — the board profile shape already agreed in Phase 4.
- `scripts/tests/` — stdlib-only suite; the place for generator and `affected.py` tests.
- `scripts/pio/compiledb.py` — the existing build-adjacent script, and a shared path that
  must widen the affected set.

### Established Patterns
- Template rendering is plain `{{name}}` string substitution; `${...}` is forbidden;
  unknown placeholders are errors (04/D-25, D-33).
- Tools print `PATH: STATUS — reason`, support `--json`, and use exit codes 0 (clean),
  1 (violation), 2 (usage/environment) (04/D-23).
- Determinism: no clock reads, no network, no PlatformIO invocation from a generator.
- Tests never import `yaml` or `jsonschema`; they shell out to `uv run` (04/D-14).
- Generated output is not committed only when `.gitignore` covers it; the repo's
  `no-generated-files` hook makes accidental commits fail.

### Integration Points
- Root `README.md` table (marker region) and the site home table share one renderer path.
- `homeworks.code-workspace` roots must include `repo`, `docs`, `lib`, `scripts`, and every
  homework, with ASCII paths (04/D-09).
- `platformio.shared.ini` pins are cross-validated today by `check_metadata.py`; the
  generator must not create a second source of truth.
- `.github/workflows/homework.yml` stays as-is; the drift job is additive and must not
  become the Phase 8 matrix.
- `docs/decisions/` is authored today and becomes a site section without moving files.

</code_context>

<specifics>
## Specific Ideas

- The SC1 wording ("CI matrix regenerates") conflicts with 04.2/D-18 and F-14. The resolution
  is explicit: `affected.py` produces the matrix input in Phase 5; the workflow matrix is
  Phase 8. The planner must not re-open this.
- F-14 records that `platformio.shared.ini` needs no per-homework entry; the generator must
  therefore not invent one. Its only job there is pin substitution.
- F-18 records IDE output (`homeworks/<id>/.vscode/`) appearing as untracked noise when a
  folder is added to the workspace. The fix is deferred (D-25), but the generated workspace
  change should not make the noise worse.
- The friction log's automation rule is "build only what the log proves painful": the three
  Phase 5 candidates with evidence are README row, workspace folder, and the shared-ini
  decision. The docs site itself has no friction entry but is carried by META-08 and the
  roadmap goal.
- The site is a catalog, not a reading surface this phase: homework pages link out to the
  report rather than embedding it (D-02).

</specifics>

<deferred>
## Deferred Ideas

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

### Reviewed Todos (not folded)
- *Expand homework README and add a proper SVG schematic* — homework content (Phase 11 /
  Phase 7), outside the generated-views boundary.
- *Promote merge_firmware.py into a shared tool* — already deferred to Phase 7/8 in STATE.md.
- *Standardize pull request titles across homeworks* — CI/process concern, Phase 8/9.
- *Trim governance ceremony (Phase 4.1)* — already completed; no action.

</deferred>

---

*Phase: 5-Generated Views and Documentation Site*
*Context gathered: 2026-10-25*

# Phase 5: Generated Views and Documentation Site - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-10-25
**Phase:** 5-Generated Views and Documentation Site
**Areas discussed:** Where the generated tree lives, Generator surface, Drift gate and
affected.py, Phase 5 boundary, Generator templates, Generator tests, Docs toolchain pins,
Site home page

---

## Where the generated tree lives

### Where should generated docs/ pages live?

| Option | Description | Selected |
|--------|-------------|----------|
| Commit + `--check` | Generated files are tracked; git carries drift; Zensical-compatible without gen-files | ✓ |
| Build-time only | Generated into a gitignored directory during the build | |
| Hybrid | Navigation and index committed; homework pages build-time | |

**User's choice:** Commit + `--check`.
**Notes:** Zensical explicitly does not support `mkdocs-gen-files`, so virtual generation
would break the Zensical-compatible configuration.

### What does a generated homework page contain?

| Option | Description | Selected |
|--------|-------------|----------|
| Metadata + links | Metadata card plus links to report and README on GitHub | ✓ |
| Full report copied | Copy `report.md` and its assets into `docs/` | |
| Include via snippets | `pymdownx.snippets` inclusion | |

**User's choice:** Metadata + links.
**Notes:** Copying Markdown without its `assets/` tree breaks relative image paths.

### How to separate authored and generated pages in docs/?

| Option | Description | Selected |
|--------|-------------|----------|
| Shared `docs/` with markers | Authored and generated together, every generated file marked | ✓ |
| `docs-src/` → `docs/` | Separate authored source and generated tree | |
| Separate `_generated/` | Generated subtree with a visible boundary | |

**User's choice:** Shared `docs/` with markers.

### Where does the board profile live?

| Option | Description | Selected |
|--------|-------------|----------|
| `boards/<id>.yaml` at root | Data beside `schema/`; page generated from it | ✓ |
| `docs/boards/<id>.yaml` | Profile colocated with the generated page | |
| Per-homework copy | Each homework carries its own profile | |

**User's choice:** `boards/<id>.yaml` at root.

### How should site navigation be generated?

| Option | Description | Selected |
|--------|-------------|----------|
| Explicit `nav:` | Generated `nav:` block in `mkdocs.yml` | ✓ |
| Auto from folders | Rely on Zensical/MkDocs folder navigation | |
| SUMMARY + literate-nav | `docs/SUMMARY.md` through the literate-nav plugin | |

**User's choice:** Explicit `nav:`.

### Is `mkdocs.yml` fully generated or only the nav block?

| Option | Description | Selected |
|--------|-------------|----------|
| Generate the whole file | One template owns theme, extensions, plugins, nav | ✓ (Claude's call) |
| Hybrid with markers | Authored config plus a generated nav region | |

**User's choice:** "your call" → whole file generated.
**Notes:** One owner, one `--check`, and the Zensical constraint lives in one template.

### How is KaTeX supplied?

| Option | Description | Selected |
|--------|-------------|----------|
| Vendored 0.19.0 | Committed JS, CSS, fonts, LICENSE, checksum test | ✓ |
| CDN | External assets | |
| Defer KaTeX | Add math support later | |

**User's choice:** Vendored 0.19.0.

### Do we customise the Material theme this phase?

| Option | Description | Selected |
|--------|-------------|----------|
| Stock Material | No `docs/overrides/` | ✓ |
| Minimal overrides | Branding or home-page overrides | |
| Defer visual work | No customisation, revisit later | |

**User's choice:** Stock Material.

---

## Generator surface

### What form should the generator take?

| Option | Description | Selected |
|--------|-------------|----------|
| One script with subcommands | `gen_views.py` with `readme`, `workspace`, `nav`, `docs`, `shared-ini`, `--all` | ✓ |
| Separate scripts | One script per view | |
| One script, everything at once | No subcommands | |

**User's choice:** One script with subcommands.

### How does the generator own `README.md`?

| Option | Description | Selected |
|--------|-------------|----------|
| Marker region | Only the table between BEGIN/END GENERATED markers | ✓ |
| Whole file | Entire README generated | |
| Separate `INDEX.md` | Table moved out of README | |

**User's choice:** Marker region.

### How does the generator own `homeworks.code-workspace`?

| Option | Description | Selected |
|--------|-------------|----------|
| Whole file from template | Folders plus extensions block | ✓ |
| Update folders only | Parse and rewrite the `folders` array | |
| Check only | Keep it hand-authored, verify only | |

**User's choice:** Whole file from template.

### What does the generator do with `platformio.shared.ini`?

| Option | Description | Selected |
|--------|-------------|----------|
| Generate the three sections | Template plus pins from `homework.yaml`; zero per-homework entries | ✓ (Claude's call) |
| Only verify pins | Keep hand-authored, fail on pin drift | |
| Outside the generator | Leave it to `check_metadata.py` | |

**User's choice:** "your call" → generate the three sections.
**Notes:** Preserves 04.2/D-17 (no per-homework entry) while satisfying META-05 literally.

### How does the generator know which files it owns?

| Option | Description | Selected |
|--------|-------------|----------|
| Committed manifest | Paths and hashes; detects modified, deleted, new | ✓ |
| Header scanning | Discover ownership from file headers | |
| Both | Headers plus manifest | |

**User's choice:** Committed manifest.

---

## Drift gate and affected.py

### Where does `--check` run?

| Option | Description | Selected |
|--------|-------------|----------|
| pre-commit + one CI job | Local hook plus one small workflow job; matrix stays Phase 8 | ✓ |
| pre-commit only | CI check deferred to Phase 8 | |
| CI only | No local hook | |

**User's choice:** pre-commit + one CI job.

### How does the hook behave on drift?

| Option | Description | Selected |
|--------|-------------|----------|
| Check only | Fail and point at `gen_views.py --all` | ✓ |
| Regenerate + `git add` | Hook rewrites and stages | |
| Check with `--fix` | Check by default, explicit fix flag | |

**User's choice:** Check only.

### What is the `affected.py` output contract?

| Option | Description | Selected |
|--------|-------------|----------|
| JSON build+simulate | Two arrays of `{project, env, framework}` plus `--format paths` | ✓ |
| Single `include[]` | One flat matrix array | |
| Paths only | Newline-separated project paths | |

**User's choice:** JSON build+simulate.

### Where does `affected.py` get the dependency graph?

| Option | Description | Selected |
|--------|-------------|----------|
| Parse `platformio.ini` | `lib_deps` symlinks plus `library.json` | ✓ |
| New `homework.yaml` field | Add `libs:` to the schema | |
| From `compile_commands` | Build artifacts | |

**User's choice:** Parse `platformio.ini`.

### How does the affected set widen for shared-path changes?

| Option | Description | Selected |
|--------|-------------|----------|
| Explicit rules + fail-safe | Named rules, unknown shared path widens to all | ✓ |
| `lib/**` only | Only library changes fan out | |
| Everything outside a homework | Any non-homework path widens to all | |

**User's choice:** Explicit rules + fail-safe.

---

## Phase 5 boundary

### What happens to the two friction-log candidates outside ROADMAP?

| Option | Description | Selected |
|--------|-------------|----------|
| Defer both | Backlog / Phase 9 | ✓ |
| Take only `.gitignore` | Cheap noise fix now, manifest later | |
| Take both | Execute both here | |

**User's choice:** Defer both.

### Does Phase 5 generate the CI matrix?

| Option | Description | Selected |
|--------|-------------|----------|
| `affected.py` + drift job | Matrix conversion in Phase 8 | ✓ |
| Generate the matrix now | Literal SC1 reading | |
| Both | Matrix and `affected.py` | |

**User's choice:** `affected.py` + drift job.

### How is `boards/<id>.yaml` validated?

| Option | Description | Selected |
|--------|-------------|----------|
| Extend `check_metadata` | One validator, one exit-code contract | ✓ |
| Separate checker | `check_boards.py` | |
| No checker | Generator fails on missing fields | |

**User's choice:** Extend `check_metadata`.

### Does Phase 5 create authored `docs/standards/` pages?

| Option | Description | Selected |
|--------|-------------|----------|
| Infrastructure only | `docs/standards/` is Phase 10; fix the AGENTS.md line | ✓ |
| Add standards now | Create `report-structure.md` | |
| Skeleton of all sections | Empty authored sections | |

**User's choice:** Infrastructure only.

---

## Generator templates

### Where do generated-file templates live?

| Option | Description | Selected |
|--------|-------------|----------|
| `templates/views/` | All templates in a new directory | |
| Inline Python | Strings inside the generator | |
| Hybrid | Text from templates, JSON from code | ✓ |

**User's choice:** Hybrid.

### Do we reuse the `new_homework` renderer?

| Option | Description | Selected |
|--------|-------------|----------|
| Shared module | Extract the `{{...}}` renderer for both tools | ✓ |
| Duplicate | Copy a small renderer | |
| Jinja | Switch both tools to Jinja | |

**User's choice:** Shared module.

### How are repeated blocks represented?

| Option | Description | Selected |
|--------|-------------|----------|
| Pre-rendered fragments | `{{homework_rows}}`, `{{nav_entries}}` | ✓ |
| Mini `{{#each}}` loop | New template syntax | |
| Template per item | Many small templates | |

**User's choice:** Pre-rendered fragments.

---

## Generator tests

### Where and how is the generator tested?

| Option | Description | Selected |
|--------|-------------|----------|
| `scripts/tests` | Stdlib-only, subprocess to `uv run` | ✓ |
| pytest in `tests/generator` | New test framework | |
| CI + manual only | No automated suite | |

**User's choice:** `scripts/tests`.

### Which invariants are mandatory?

| Option | Description | Selected |
|--------|-------------|----------|
| Round-trip | Generation is idempotent and authored files are untouched | ✓ (Claude's call) |
| Drift detection | Modified/deleted/new detected | ✓ (Claude's call) |
| `affected.py` tests | Unit plus one end-to-end | ✓ (Claude's call) |

**User's choice:** "your call but without excessive bureaucracy" — the three above, no
separate ceremonial tests.

### What fixture shape do the tests use?

| Option | Description | Selected |
|--------|-------------|----------|
| Synthetic fixture | Two homeworks, two libraries, temp directory | ✓ |
| Copy of the real repo | Full copy in temp | |
| Real tree only | `--check` against the working tree | |

**User's choice:** Synthetic fixture plus one real-tree smoke test.

---

## Docs toolchain pins

### Where are docs build dependencies pinned?

| Option | Description | Selected |
|--------|-------------|----------|
| `requirements-docs.txt` | Exact versions, shared by CI and local | ✓ |
| PEP 723 in `build_docs.py` | uv-managed wrapper | |
| Version range | `>=9.7,<10` | |

**User's choice:** `requirements-docs.txt`.

### Is hash pinning required?

| Option | Description | Selected |
|--------|-------------|----------|
| Exact versions only | No hashes | ✓ |
| Pin with hashes | `pip-compile --generate-hashes` | |

**User's choice:** Exact versions only.

### Are docs pins verified automatically?

| Option | Description | Selected |
|--------|-------------|----------|
| Extend the D-13 test | Cross-check pins, generated mkdocs.yml, KaTeX | ✓ |
| No verification | Manual updates only | |

**User's choice:** Extend the D-13 test.

---

## Site home page

### How is the site home page structured?

| Option | Description | Selected |
|--------|-------------|----------|
| Prose + generated table | Authored prose between markers | ✓ |
| Fully generated | Whole page from a template | |
| Authored + separate page | Table on its own page | |

**User's choice:** Prose + generated table.

### What is the navigation structure?

| Option | Description | Selected |
|--------|-------------|----------|
| Home/Homeworks/Boards/Decisions | Flat four-section tree | ✓ |
| Getting Started/Reference | Sectioned structure | |
| Flat list | One list of all pages | |

**User's choice:** Home/Homeworks/Boards/Decisions.

### Which columns does the generated table have?

| Option | Description | Selected |
|--------|-------------|----------|
| Extended columns | ID · Project · Board · Framework · Status · Report | ✓ |
| Minimal columns | ID · Project · Status · Report | |
| Extended + Simulation | Adds simulation status | |

**User's choice:** Extended columns.

---

## Open todos

| Option | Description | Selected |
|--------|-------------|----------|
| None | No open todo belongs to Phase 5 | ✓ |
| README + SVG schematic | Homework content (Phase 11 / 7) | |
| `merge_firmware.py` promotion | Deferred to Phase 7/8 | |
| Standardise PR titles | CI/process (Phase 8/9) | |

**User's choice:** None folded.

## Claude's Discretion

- Generate the whole `mkdocs.yml` from a template rather than a hybrid with markers.
- Generate the three `platformio.shared.ini` sections from a template with pins substituted.
- Test coverage kept lean: round-trip/idempotency, drift detection, `affected.py` unit +
  one end-to-end; no separate ceremonial tests.
- Exact template names, module split, manifest shape, page layout, and workflow job
  structure.

## Deferred Ideas

- Private `lib/pattern` manifest and `lib_deps` generation → backlog / Phase 9
- Test scaffold and inner `.gitignore` covering `.vscode/` → backlog / Phase 9
- CI `strategy.matrix` → Phase 8
- Report-body embedding on the site → deferred until `assets/` paths are solved
- Authored `docs/standards/` → Phase 10
- External link checking → Phase 8
- Zensical migration evaluation → Q1 2027

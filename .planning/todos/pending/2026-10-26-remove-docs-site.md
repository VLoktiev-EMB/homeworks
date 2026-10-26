---
created: 2026-10-26T00:00:00.000Z
title: Remove the generated documentation site
area: tooling
severity: minor
files:
  - .github/workflows/docs.yml
  - mkdocs.yml
  - requirements-docs.txt
  - docs/index.md
  - docs/boards/esp32-s3-devkitc-1.md
  - docs/homeworks/1_3-police-flasher.md
  - templates/views/board-page.md.tmpl
  - templates/views/homework-page.md.tmpl
  - templates/views/mkdocs.yml.tmpl
  - scripts/gen_views.py
  - generated.manifest
  - scripts/tests/test_docs_pins.py
  - scripts/tests/test_gen_views.py
  - README.md
  - AGENTS.md
---

# Remove the generated documentation site

Source: exploration 2026-10-26; the reasoning is recorded in
`.planning/notes/ceremony-vs-engineering-principle.md` under
`## Revisit — 2026-10-26: the docs site is cut`.

The site is removed because the authored docs are already plain Markdown that GitHub
renders, and the site is a per-change deploy plus a per-change drift obligation for
content that does not need it.

## Delete

- [ ] `.github/workflows/docs.yml` (the Pages build and deploy workflow).
- [ ] `mkdocs.yml` and `requirements-docs.txt`.
- [ ] `docs/assets/vendor/` and the KaTeX checksum ledger.
- [ ] `docs/index.md`, `docs/boards/`, `docs/homeworks/`.
- [ ] `templates/views/board-page.md.tmpl`, `templates/views/homework-page.md.tmpl`,
      `templates/views/mkdocs.yml.tmpl`.
- [ ] `scripts/tests/test_docs_pins.py` (KaTeX vendoring, math rendering, pin
      consistency are all site-only).
- [ ] Any generated-views test cases that assert the four site-only views.

## Narrow

- [ ] `scripts/gen_views.py`: drop the `docs`, `nav` and `docs-page` owners. The
      remaining owners are `readme`, `workspace` and `shared-ini`.
- [ ] `generated.manifest`: shrink from 7 entries to 3 (`README.md`,
      `homeworks.code-workspace`, `platformio.shared.ini`). Do not hand-edit the
      manifest; regenerate it.
- [ ] `scripts/tests/test_gen_views.py`: keep coverage of the three remaining views,
      including the `--check` / `ORPHAN` behaviour.
- [ ] Keep `.github/workflows/generated-views.yml` and the `gen-views-check`
      pre-commit hook: they still guard the three core views.

## Update references

- [ ] `AGENTS.md`: repository layout, generated paths, quality-tooling and routing
      table rows that name `mkdocs.yml`, `docs/homeworks/`, `docs/boards/` or the docs
      workflow.
- [ ] `README.md`: any link or sentence that presents the Pages site as a deliverable.
- [ ] `.planning/PROJECT.md` and `.planning/STATE.md`: mark the Phase 5 site decision as
      superseded rather than rewriting it.
- [ ] `.planning/ROADMAP.md`: do not rewrite the Phase 5 history; record the removal in
      the current work instead.
- [ ] `.pre-commit-config.yaml`: confirm the site paths are no longer referenced by
      exclusions or generated-file patterns.

## Maintainer action

- [ ] GitHub `Settings -> Pages -> Build and deployment -> Source` = `None`, so the old
      artifact stops serving and the URL is no longer a deliverable.

## Verify

- [ ] `uv run scripts/gen_views.py --all --check` passes with 3 manifest entries.
- [ ] `pre-commit run --all-files` passes with the narrowed hook set.
- [ ] `uv run scripts/check_metadata.py` passes.
- [ ] `pio run -d homeworks/1_3-police-flasher` still builds.
- [ ] No dangling references to deleted paths in `README.md`, `AGENTS.md`, `docs/`,
      `.github/` or `scripts/`.

## Out of scope

Do not touch the metadata contract, the CI work of Phase 8, or the remaining generated
views in this task. The site removal should be one atomic change.

---
title: Trim governance ceremony (Phase 4.1)
date: 2026-10-25
priority: high
---

# Trim governance ceremony

Source: exploration 2026-10-25; the principle lives in
`.planning/notes/ceremony-vs-engineering-principle.md`. Target: one pull request, before
Phase 4.2.

## Delete

- [ ] `policy/` and `scripts/check_policy.py`; remove the policy step from the
      `AGENTS.md` quick-start. Keep the live GitHub ruleset and let the settings live in
      the GitHub UI. Leave `docs/decisions/0003-git-policy-and-protected-main.md` as
      history; do not rewrite it.
- [ ] `REUSE.toml`, `NOTICE`, `LICENSES/`, the `reuse` job in
      `.github/workflows/security.yml`, and any SPDX header requirement.
- [ ] `scripts/check_pr_templates.py`, `scripts/tests/test_check_pr_templates.py`, and
      `.github/PULL_REQUEST_TEMPLATE/{homework,infra,docs}.md`.
- [ ] `scripts/metadata/allowlist.json` and its handling in
      `scripts/metadata/contract.py`; replace it with a single Cyrillic grep.
- [ ] The gate logic in `scripts/tag_homework.sh`; keep a minimal tag script or document
      a three-line command.
- [ ] `scripts/tests/` modules that test the meta-tooling rather than product behaviour:
      `test_agents_md.py`, `test_license_hygiene.py`, `test_architecture_headers.py`,
      `test_native_purity.py`, `test_gitignore.py`, `test_templates.py`,
      `test_tag_homework.py`, `test_adrs.py`, `test_homework_id.py`,
      `test_metadata_deps.py`, `test_native_determinism.py`, `test_security_workflow.py`,
      `test_pio_scripts.py`, `test_check_architecture.py`, `test_check_policy.py`.
- [ ] The `.github/PULL_REQUEST_TEMPLATE/` directory; add one default
      `.github/pull_request_template.md`.

## Simplify

- [ ] Keep `LICENSE` as the single repo-wide MIT licence; remove the MIT/CC-BY split
      from `AGENTS.md` and `README.md`.
- [ ] Keep `scripts/tests/{test_homework_metadata.py,test_new_homework.py,temp_root.py,__init__.py}`.
- [ ] Rewrite `AGENTS.md`: a four-step quick-start (`pio run`, `pio test`,
      `pre-commit run --all-files`, metadata check); no policy, licence-split, or
      PR-drift rules; a proportional GSD rule (`/gsd-fast` for trivial, `/gsd-quick` for
      multi-step, the phase workflow for architectural work or homework delivery); a short
      Definition of Done.
- [ ] Keep gitleaks, the whitespace/EOF/merge/large-file hooks, `no-generated-files`,
      the metadata check, and the architecture check.
- [ ] Keep `docs/decisions/` as history, but stop requiring an ADR and a status-index
      update for every decision. New ADRs only for irreversible choices.
- [ ] Keep `scripts/architecture/allowlist.json` for now; the architecture checker is
      reduced in a later pass.

## Tooling corrections

- [ ] Keep the GSD culture: every change is an atomic Conventional Commit, verified, and
      contains no unrelated work. Replace only the blanket "every change must be preceded
      by a GSD command" wording with the proportional tier rule above.
- [ ] Fix or work around the global `/gsd-fast` staging behavior: it runs `git add -A`,
      which can stage unrelated files and `.planning/`. Stage only the touched files
      (upstream patch to `~/.claude/gsd-core/workflows/fast.md`, or a repo-local commit
      helper).
- [ ] Stop appending a `STATE.md` quick-task row for every trivial change; log only
      changes worth resuming from.

## Verify

- [ ] `pio test -d tests -e native` passes.
- [ ] The existing smoke build target still builds after the trim.
- [ ] `pre-commit run --all-files` passes with the trimmed hook set.
- [ ] `python3 scripts/check_metadata.py` passes on the current tree.
- [ ] No dangling references to deleted files in `README.md`, `AGENTS.md`, `docs/`, or
      `.github/`.

## Out of scope

Do not build generation, formatting, the CI matrix, skills, simulation, or the report
checker here. They belong to Phases 5–10 and are justified by the Phase 4.2 friction
log.

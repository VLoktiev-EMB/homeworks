---
created: 2026-10-25T20:37:24.995Z
title: Standardize pull request titles across homeworks
area: tooling
severity: minor
files:
  - .github/pull_request_template.md
  - AGENTS.md
  - .github/workflows/homework.yml
---

## Problem

Pull-request titles are free-form today. `AGENTS.md` defines Conventional Commits
`type(scope): summary` for commits and `.github/pull_request_template.md` defines the
body (the Definition of Done), but neither says anything about the PR title. Nothing
checks it, so titles can drift between homeworks and phases.

This matters more than usual for this repository because the project is squash-only into
the default branch: the PR description becomes the squash-merge commit body, and the PR
title is the natural source for the squash subject. An inconsistent title therefore ends
up in published history, where it cannot be rewritten (AGENTS.md forbids history edits).

Observed so far: PR #10 is `feat(1_3): deliver the police flasher tracer homework`, which
already looks like the intended shape, but it is convention by accident — no rule records
it and no check enforces it.

## Solution

TBD — candidate shape:

1. Record the convention in `AGENTS.md` under "Pull requests and tags": for a homework PR,
   `type(<homework-id>): <summary>` reusing the same `type` vocabulary as commits; for a
   docs/infrastructure PR, `docs(<slug>): <summary>` or `chore(<slug>): <summary>`. State
   that the title is what the squash subject should be.
2. Add a machine check rather than relying on review: a `pull_request` job step that
   validates the title against the pattern, or a local `pre-push` script. Prefer the
   GitHub check because the title can only be validated after the PR exists.
3. Document one good and one bad example in the pull-request template or AGENTS.md, the
   way the commit-message rule does.
4. Do not retrofit historical PRs: names already published stay as they are.

Open question: whether the scope is the homework ID (`1_3`) or the full directory id
(`1_3-police-flasher`), and whether the check belongs in the phase that owns CI (Phase 8)
rather than a standalone task.

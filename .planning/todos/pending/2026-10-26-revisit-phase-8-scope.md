---
created: 2026-10-26T00:00:00.000Z
title: Revisit Phase 8 scope before planning
area: process
severity: major
resolves_phase: 8
files:
  - .planning/phases/08-fast-ci/08-CONTEXT.md
  - .planning/phases/08-fast-ci/08-RESEARCH.md
  - .planning/ROADMAP.md
---

# Revisit Phase 8 scope before planning

Phase 8 research is complete (`08-RESEARCH.md`), but the phase was scoped on 2026-10-26
before the simplification decision recorded in
`.planning/notes/ceremony-vs-engineering-principle.md`. Do not plan the full pipeline by
inertia.

## Decide, per success criterion, whether it earns its recurring cost

1. `meta` job — schema, `--check` drift, lint, gitleaks, architecture, `wokwi-cli lint`.
2. `changes` + `build` + a single required `gate` check.
3. `simulate` — optional, changed-only, timeout-bounded, artifact upload, never required
   for forks.
4. Nightly full matrix.

## Known collisions with the simplification decision

- The research proposes a `docs-build` job. The docs site is being removed, so that job
  has no subject unless the site is reintroduced.
- The research proposes a `static-analysis` job for clang-tidy. clang-tidy already runs
  at pre-push locally; decide whether a second, CI-side gate earns its cost.
- The research keeps the `generated-views` check for the three remaining views. That is
  consistent with keeping the generator.
- `simulate` must stay quota-aware: the Wokwi free plan is metered at roughly 50 minutes
  per 30 days, and only sessions are metered.

## Outcome

Write the reduced Phase 8 scope into `08-CONTEXT.md` and `ROADMAP.md` before planning,
or record a decision to defer the phase. If the scope shrinks, update the Phase 8
requirement mapping (TOOL-05, TOOL-06, SIM-04) so the checker does not require coverage
for a job that was deliberately cut.

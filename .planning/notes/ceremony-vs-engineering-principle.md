---
title: Ceremony vs engineering — the trimming principle
date: 2026-10-25
context: Exploration that led to Phase 4.1 (Ceremony Trim) and Phase 4.2 (Tracer Homework 1.3)
---

# Ceremony vs engineering

## Problem

After four phases the repository had 31 completed plans, 272 tracked files, and no
homework. Infrastructure was built ahead of the work it serves, and part of it simulated
a multi-contributor organisation inside a single-author course repository.

## The two categories

**Bureaucracy** protects against *other people*: strangers opening pull requests,
contributors disagreeing about licence boundaries, maintainers drifting the branch
policy. In a single-author repository its per-change cost buys protection against a risk
that does not exist yet. It is cheap to restore later because it consists mostly of
configuration and checks that do not depend on homework code.

**Engineering** protects against *entropy in our own code*: formatting drifts, headers
leak framework dependencies, generated views go stale, reports omit evidence. Its cost
is paid regardless of how many people contribute, and it is expensive to delay because
the pieces depend on each other (format → IntelliSense → skills → reports).

The trim therefore removes bureaucracy and keeps engineering. It does not defer the
engineering stack; it schedules it.

## Decision rule

Cut, keep, or defer a check by **how often it runs**, not by how impressive it looks:

1. Runs on every change (hooks, CI jobs, PR ritual, multi-step quick-start): highest
   recurring friction, cut first.
2. Runs on every homework (metadata checker, scaffold, report gate): keep only what
   earns its time; simplify the rest.
3. Runs once or once a milestone (policy-as-code, REUSE, ADR ceremony): low recurring
   cost and low value; remove when touched, do not prioritise demolition.

Sunk cost is not a reason to delete working code; recurring cost is the reason to delete
it.

## Manual first, automate second

The repository had never produced a homework, so the real friction was unknown. Phase
4.2 therefore runs the full homework 1.3 cycle **manually** and records every friction
point. Phases 5–10 automate only what that log proves painful. An automation with no
entry in the log is not built.

## Process × artifact matrix

The tracer exercises every process against one real artifact:

| Process | What the tracer provides |
|---|---|
| Scaffold | `scripts/new_homework 1_3-police-flasher` |
| Build | `pio run` for the ESP32-S3 N16R8 environment |
| Native tests | Pattern state machine in `lib/common` |
| Formatting and linting | Real C/C++ sources |
| Generation | One real entry for the README index, workspace, shared ini, CI matrix |
| Simulation | `assets/diagram.json` and a Wokwi scenario |
| Report | Real BOM, pin map, calculations, measurements, traceability |
| CI | A pull request that changes one project |
| Skills | `new-homework` and `hw-build` driving the cycle |
| Tag | `hw/1_3-police-flasher` after merge (Phase 11) |

## Friction log

Recorded during Phase 4.2 in the phase directory. One entry per friction point:

- **step** — where it happened (scaffold, build, report, simulation, PR, …)
- **what hurt** — the concrete action that took time or felt wrong
- **frequency** — once, per homework, per change
- **cheap fix** — the smallest change that removes the friction
- **automation candidate** — yes/no, and which later phase would own it

## Inventory

**Cut now:** `policy/` and `check_policy.py`; `REUSE.toml`, `NOTICE`, `LICENSES/`, the
`reuse` CI job and SPDX headers (keep one MIT `LICENSE`); `check_pr_templates.py` and the
three-template split (one default template); the Cyrillic allowlist (one grep); the
four-gate `tag_homework.sh` (a three-line script); 18 meta-test modules (keep 2–3 smoke
tests); the nine-step quick-start (four steps); GSD-on-every-edit; ADR-per-decision; the
report merge gate.

**Keep:** MIT `LICENSE`; gitleaks; `schema/` and `check_metadata.py`; `new_homework` and
the two homework templates; the architecture check (later reduced to a small grep); the
Unity library suite; `pio run` / `pio test`; clang-format; one CI job.

**Keep in the roadmap and build against the tracer:** MkDocs site, workspace and
CI-matrix generation, clang-tidy and esp-clangd, the four-simulator spike, the seven
skills, the report and evidence checker.

**Return later, only if needed:** policy-as-code, REUSE compliance, the multi-template PR
workflow, the ADR status index.

## Consequences

- Phase 4.1 removes the ceremony.
- Phase 4.2 runs the tracer and produces the friction log.
- Phases 5–10 are justified line by line by that log.
- Phase 11 is the second pass of the same homework: polish, tag, scale.

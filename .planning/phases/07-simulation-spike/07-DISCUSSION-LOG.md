# Phase 7: Simulation Spike - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-10-26
**Phase:** 7-Simulation Spike
**Areas discussed:** Wokwi execution, Tool matrix, Evidence base, Friction-log scope

---

## Wokwi execution

| Option | Description | Selected |
|--------|-------------|----------|
| Owner executes (recommended) | The owner runs `wokwi-cli` outside the sandbox with their token; duration, serial output, and status are recorded. The token is never stored. This satisfies the primary SC2 path with real measurements. | ✓ (with protocol A) |
| Honest lint-only | Treat the missing token as a blocking failure; the ADR records lint-only as the honest result, `simulation.status` stays `pending`, and SC2 closes through the "blocking failure + fallback" branch. | |
| Defer execution to Phase 8 CI | Phase 7 produces a lint-only ADR with an explicit condition; the real run and timing move to Phase 8, where the token is a repository secret. | |

**User's choice:** The owner has a free plan with a token, but the quota drains quickly;
the asked variants were compared and protocol A was selected.

**Notes:** Protocol A = three short runs (cold, warm, repeat) with a `--timeout` of about
15 seconds each and a hard quota budget, falling back to a single run (protocol B) if the
consumption is unexpectedly large. Compilation, the merged image, and `lint` consume no
Wokwi quota. The owner supplies the token outside the sandbox.

---

## Tool matrix

| Option | Description | Selected |
|--------|-------------|----------|
| Role-proportional (recommended) | Wokwi executed; Velxio self-host attempted (boot, ESP-IDF compile, serial) with no Wokwi quota; Renode and Fritzing recorded as `not measured` with reasons; the license boundary is documented. | ✓ |
| Literally all four | Install Renode and Fritzing, find an STM32 model, and execute all four. Satisfies SC1 literally but requires installs, an unconfirmed board, and a much larger phase. | |
| Wokwi + Velxio only | Measure only Wokwi and Velxio; exclude Renode and Fritzing from the ADR as out of scope. | |

**User's choice:** Role-proportional.

**Notes:** The user asked whether Velxio had been skipped completely. Answer: not in the
roadmap (SC1 names it) but effectively in the environment (never run; the self-host image
excludes STM32). The phase will attempt it explicitly rather than let it become a silent
omission.

---

## Evidence base

### Where raw measurements live

| Option | Description | Selected |
|--------|-------------|----------|
| Evidence file + ADR (recommended) | `07-SPIKE-EVIDENCE.md` holds commands, durations, serial output, and quota consumed; ADR-0014 holds the conclusion and links to it. | ✓ |
| ADR body only | All timings and outputs inside ADR-0014; one artifact, but the ADR mixes decision with raw data. | |
| Table row + evidence only | One evidence file and one row in `docs/decisions/README.md`, no ADR file; the alternatives have no dedicated place. | |

**User's choice:** Evidence file + ADR.

### ADR number conflict

| Option | Description | Selected |
|--------|-------------|----------|
| ADR-0014, roadmap untouched (recommended) | Create `0014-simulator-selection.md` and a table row; leave the roadmap's "ADR-0004" as historical and record 0004 → 0014 in CONTEXT. | ✓ |
| ADR-0014 + correct roadmap | Same, plus a docs edit to the roadmap so a future reader does not look for a non-existent ADR-0004. | |
| Table row only | No ADR file; only a table row and the evidence file. | |

**User's choice:** ADR-0014, roadmap untouched.

**Notes:** `docs/decisions/0004-license-and-attribution.md` is the superseded license
decision; history is not rewritten.

### Lint-only versus executed

| Option | Description | Selected |
|--------|-------------|----------|
| No schema change (recommended) | `verified` means an executed run only; lint-only stays `pending`; the distinction lives in the evidence file and ADR. | ✓ |
| Add `simulation.evidence` field | A new `lint | executed` field with schema, checker, and tests; more precise but a schema change that touches generators and docs. | |
| Extend the enum | Add `lint-only` as a third status value; coarser than a separate field but fewer new keys. | |

**User's choice:** No schema change.

---

## Friction-log scope

| Option | Description | Selected |
|--------|-------------|----------|
| Promotion + path check (recommended) | Promote `merge_firmware.py` to `scripts/pio/merge_firmware.py` and add the F-19 path-resolution check. No gate script; the lint/executed distinction stays documentary. | ✓ |
| Minimum — ADR and evidence only | Only ADR-0014, the evidence file, and the executed run; the merge script stays project-local and the path check is the existing dummy-token command. | |
| Full set with gate | Promotion + path check + a `scripts/simulate.py` gate that distinguishes lint from executed. | |

**User's choice:** Promotion + path check.

---

## Claude's Discretion

- The exact measurement method (wall-clock command, repetition count, rounding,
  uncertainty notation) and the structure of `07-SPIKE-EVIDENCE.md`.
- The outline and wording of ADR-0014, provided it records measured cold start, compile
  time, serial reliability, simulated minutes, fidelity limits, the per-platform role, and
  the calculated CI cost basis.
- The order of the Wokwi and Velxio attempts.
- The implementation form of the path-resolution check, within the network-free constraint.
- The commit split between the evidence/ADR work and the `merge_firmware.py` promotion.

## Deferred Ideas

- `scripts/simulate.py` gate — Phase 8.
- Schema field or enum for lint-only versus executed — declined.
- Homework README expansion and SVG schematic — Phase 11, not a decimal phase.
- Renode/STM32 execution — v2.
- Fritzing illustration export — optional Phase 11 artifact.
- Nightly full simulation matrix — out of scope.
- ESP-IDF `compiledb` completeness fallback — later spike or the first ESP-IDF homework.
- Reviewed but not folded: README/SVG todo (Phase 11), root compile database todo
  (resolved by Phase 06.1), ceremony trim (completed), PR-title standardization
  (Phase 8/9).

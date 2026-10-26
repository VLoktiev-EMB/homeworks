# Phase 7: Simulation Spike - Context

**Gathered:** 2026-10-26
**Status:** Ready for planning

<domain>
## Phase Boundary

An evidence-based simulator decision recorded in an ADR, with measured costs and fidelity
limits. The phase delivers:

- A real, executed Wokwi run of the `1_3-police-flasher` scenario, or an honest recorded
  blocking failure with the chosen fallback and its evidence.
- A role-proportional evidence set for Wokwi (executed), Velxio (self-host attempt),
  Renode (not measured, with a reason), and Fritzing (not measured, license boundary).
- `07-SPIKE-EVIDENCE.md` with raw commands, durations, serial output, and quota consumed.
- `docs/decisions/0014-simulator-selection.md` plus a row in `docs/decisions/README.md`,
  stating which simulator serves each platform and the calculated CI cost basis.
- Promotion of `merge_firmware.py` into `scripts/pio/merge_firmware.py`.
- A path-resolution check for the documented Wokwi command (F-19).
- `wokwi-cli lint` validation of the canonical `diagram.json` (already green; re-asserted).

**Requirements covered:** SIM-02, SIM-03.

**Explicitly not this phase:** CI wiring, a CI simulation gate, and the `changes` matrix
stay Phase 8 (SIM-04, TOOL-05, TOOL-06). The report and evidence checker stays Phase 10.
Homework README expansion and an SVG schematic stay Phase 11. Renode/STM32 execution is a
v2 item because the course board models are unconfirmed. No schema change is made.

</domain>

<decisions>
## Implementation Decisions

### Wokwi execution evidence

- **D-01:** The spike executes the homework 1.3 scenario for real, using protocol A:
  three short runs — cold, warm, and one repeat for serial reliability — each bounded by a
  `--timeout` of about 15 seconds. A hard quota budget is tracked after every run; if the
  consumption is unexpectedly large, stop and fall back to protocol B (a single run).
  — **Reversibility:** reversible — additional runs can be added later, but quota spent is
  not recoverable within the rolling window.
- **D-02:** The owner supplies `WOKWI_CLI_TOKEN` outside the command sandbox (through the
  `!` prefix or a separate terminal). The token is never written to CONTEXT, the evidence
  file, a command line that is logged, or the repository; the evidence records only
  "token supplied by the repository owner; value not recorded".
  — **Reversibility:** one-way — a credential that reaches a public history cannot be
  unpublished; rotation is the only mitigation.
- **D-03:** Compilation, the merged-image post action, and `wokwi-cli lint` are measured
  locally and consume no Wokwi quota. Only the simulation session is metered, so compile
  time and cold/warm build behaviour are measured without quota pressure.
- **D-04:** Serial reliability is recorded as an observation, not a statistic: "3/3 runs
  observed the expected serial line", with the exact run count. If protocol B is used, the
  row states the smaller count and serial reliability is labelled `not measured`.

### Tool matrix depth

- **D-05:** Evidence depth is role-proportional, not equal-for-all:
  - **Wokwi** — executed, measured cold start, compile time, session duration, serial
    reliability, and quota consumed.
  - **Velxio** — a self-host attempt through the prebuilt Docker image: boot, ESP-IDF
    compile, and serial. This costs no Wokwi quota and is the cheapest second real
    measurement. Its self-host board limit (AVR/RP2040/ESP32, no STM32) is itself evidence.
  - **Renode** — `not measured` with the reason "no confirmed STM32 platform; Renode not
    installed"; consistent with the STATE blocker and the v2 deferral.
  - **Fritzing** — `not measured` with the reason "not a simulator"; the ADR records the
    license boundary only (SIM-03). No Fritzing illustration is produced in this phase.
  — **Reversibility:** reversible — a later phase can add depth without invalidating the
  record, provided the labels stay honest.
- **D-06:** If the Docker daemon or the image pull is unavailable, the owner may run the
  Velxio attempt outside the sandbox. If it still cannot run, the evidence records
  `not measured — <exact reason>` and no number is inferred.
- **D-07:** The Wokwi alpha scenario field names (`wait-serial`, `delay`, `expect-pin` with
  `part-id`, `name`, `value`) are revalidated against the installed `wokwi-cli 0.28.1`
  during the executed run. Any change found is owned by this phase (F-10).

### Evidence record

- **D-08:** Raw measurements live in
  `.planning/phases/07-simulation-spike/07-SPIKE-EVIDENCE.md`: exact commands, wall-clock
  durations, serial output, quota consumed per run, and a per-run table. Every value
  carries one of the established labels — measured, calculated, datasheet, or
  explicitly not measured, with the reason. The ADR carries the conclusion and links to
  this file rather than duplicating the raw data.
- **D-09:** The decision is recorded as `docs/decisions/0014-simulator-selection.md`
  (alternatives, consequences, and the platform/role matrix) plus a row in
  `docs/decisions/README.md`. The roadmap's "ADR-0004" is left untouched as a historical
  formulation; this CONTEXT records the mapping **0004 → 0014**. ADR `0004` remains the
  superseded license decision and is never rewritten.
  — **Reversibility:** costly — the number is referenced by the roadmap, the phase
  artifacts, and later phases; renaming it means updating every reference.
- **D-10:** `schema/homework.schema.json` is not changed. `simulation.status: verified`
  means an executed run with evidence; lint-only stays `pending`. The lint-versus-executed
  distinction lives in the evidence file and the ADR, not in the metadata contract. A new
  enum value or `simulation.evidence` field was considered and declined for this phase.
- **D-11:** The CI cost basis in the ADR is **calculated from measured inputs**: measured
  session duration × changed projects per pull request × runs per month, compared with the
  published quota. It is labelled `calculated`, not `measured`. A real CI simulation run is
  Phase 8 work and is not claimed here.

### Friction-log scope

- **D-12:** `merge_firmware.py` is promoted to `scripts/pio/merge_firmware.py` and consumed
  through a relative `post:` `extra_scripts` entry that survives `pio run -d <project>`.
  The per-homework copy is removed in the same change so two sources never coexist. The
  tool stays version-aware: it resolves `tool-esptool` on espressif32 8.x and fails with a
  clear message when the package name or esptool major differs.
  — **Reversibility:** costly — every homework with a custom partition table references the
  shared path; moving it again means touching each project.
- **D-13:** The F-19 path-resolution check is behavioral where possible without network
  access — the documented command is exercised with `WOKWI_CLI_TOKEN=dummy` and the
  failure must be a connection error, not a missing-file or doubled-path error. If a
  network-free automated form is not practical, it is a documented verification in the
  evidence file. It must not become a prose/doc-sync test; those were pruned in the
  `261026-ky7` quick task.
- **D-14:** No `scripts/simulate.py` gate is built in this phase. The lint-versus-executed
  distinction is carried by the evidence file, the ADR, and the report label vocabulary;
  the CI gate belongs to Phase 8, where the workflow shape is defined.
- **D-15:** The homework README expansion and the SVG schematic are deferred to Phase 11,
  not to a decimal phase. Phase 7 stays focused on the simulator decision.

### Claude's Discretion

- The exact measurement method (wall-clock command, repetition count for compile timing,
  rounding, uncertainty notation) and the structure of `07-SPIKE-EVIDENCE.md`.
- The outline, wording, and length of ADR-0014, provided it records measured cold start,
  compile time, serial reliability, simulated minutes, fidelity limits, the per-platform
  role, and the calculated CI cost basis.
- The order of the Wokwi and Velxio attempts, and whether the Velxio attempt runs before or
  after the three Wokwi runs.
- The implementation form of the path-resolution check, within the D-13 constraints.
- The exact commit split between the evidence/ADR work and the `merge_firmware.py`
  promotion.

### Folded Todos

- **Promote merge_firmware.py into a shared tool** (`.planning/todos/pending/2026-10-25-promote-merge-firmware-py-into-a-shared-tool.md`).
  Original problem: the Wokwi flash image requires a merged binary, and the working script
  lives inside one homework, so the next homework would copy it. It fits this phase because
  F-09 explicitly assigns the promotion to Phase 7/8 and the executed Wokwi run depends on
  the merged image.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and requirements
- `.planning/ROADMAP.md` §Phase 7: Simulation Spike — goal, success criteria 1–5, and the
  requirement mapping (SIM-02, SIM-03)
- `.planning/REQUIREMENTS.md` §Simulation and Diagrams — SIM-02, SIM-03, and SIM-04 as the
  Phase 8 boundary
- `.planning/PROJECT.md` §Constraints — simulation, spike timebox, licensing; and the Key
  Decisions row "Wokwi primary, Velxio fallback, Renode for STM32, Fritzing with attribution"
- `.planning/STATE.md` §Blockers/Concerns — STM32 board models unconfirmed; §Decisions —
  simulation execution deferred to Phase 7, `merge_firmware.py` promotion deferred to
  Phase 7/8

### Research that constrains the approach
- `.planning/research/STACK.md` §3.1–3.10 — the simulator decision summary, Velxio and
  Wokwi capabilities and quotas, Fritzing licensing, Renode/QEMU limits, the comparison
  matrix, the CI budget math, licensing implications, the spike pass/fail table (§3.9), and
  `diagram.json` as the wiring contract (§3.10)
- `.planning/research/SUMMARY.md` §Simulation Tool Decision Matrix and §Conflicts rows 4–5 —
  Wokwi-primary reversal and the CI simulation cadence
- `.planning/research/FEATURES.md` TS-26 (local simulation path), DF-01 (simulation in CI),
  and AF-11 (never present simulation as hardware evidence)
- `.planning/research/PITFALLS.md` C10 — assuming simulator behaviour equals hardware
  behaviour

### Friction log entries that this phase owns
- `.planning/phases/04.2-tracer-homework-1-3/04.2-FRICTION-LOG.md` F-08 (token-gated Wokwi,
  lint-only versus executed), F-09 (esptool 5 merge script), F-10 (option paths and alpha
  scenario fields), F-19 (path-resolution check), and §Top automation candidates (the
  Phase 7 row)

### Decisions and existing contracts
- `docs/decisions/README.md` — the table-first index; the simulator row is added here
- `docs/decisions/0004-license-and-attribution.md` — the occupied number that forces 0014
- `schema/homework.schema.json` §`$defs.simulation` — `tool` enum and
  `status: none | pending | verified`
- `homeworks/1_3-police-flasher/assets/diagram.json` — the canonical wiring, with
  `flashSize: 16`, octal PSRAM 8, parts `esp`, `r1`, `led1`, `led2`, `r2`, `led3`, `btn1`
- `homeworks/1_3-police-flasher/wokwi.toml` — firmware and ELF paths for
  `esp32s3_arduino`
- `homeworks/1_3-police-flasher/scenario.yaml` — the three-step alpha scenario
- `homeworks/1_3-police-flasher/merge_firmware.py` — the project-local post action being
  promoted
- `homeworks/1_3-police-flasher/README.md` §Simulation — the documented command and the
  dummy-token path proof
- `scripts/pio/compiledb.py` — the established shape for a shared `scripts/pio/` post
  script and its relative-path use
- `.planning/todos/pending/2026-10-25-promote-merge-firmware-py-into-a-shared-tool.md` —
  the folded todo and its trigger/contract questions

### External references
- `https://docs.wokwi.com/wokwi-ci/getting-started` — CLI install, `WOKWI_CLI_TOKEN`, and
  scenario options
- `https://docs.wokwi.com/guides/wokwi-ci-actions` — CI action shape and quota behaviour
- `https://github.com/davidmonterocrespo24/velxio` — the self-host image, board limits, and
  AGPL/commercial licensing

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `homeworks/1_3-police-flasher/wokwi.toml`, `assets/diagram.json`, and `scenario.yaml` are
  already present and lint-clean, so the executed run needs no new simulation input.
- `homeworks/1_3-police-flasher/merge_firmware.py` already produces the required merged
  image; the promotion is a move plus a path-contract change, not a rewrite.
- `scripts/pio/compiledb.py` is the existing example of a shared `scripts/pio/` post
  script consumed from a homework's `extra_scripts`; the promoted merge script follows the
  same shape.
- `scripts/tests/` is a stdlib-only suite with a habit of shelling out for external tools;
  the path-resolution check can live there if it stays network-free.
- `scripts/gen_views.py` and the metadata checker already read the `simulation` block, so
  `status: verified` propagates to the README index and the docs pages without new code.

### Established Patterns
- Deterministic scripts print `PATH: STATUS — reason`, support `--json`, and exit 0/1/2
  (04/D-23). The path-check should follow this where it is a script.
- Hooks and checks are check-only and never rewrite or stage (05/D-21).
- Tests never import `yaml` or `jsonschema`; they shell out to `uv run` (04/D-14).
- ADRs are table-first; an ADR file exists only for decisions with real argumentation
  (the ceremony-trim decision).
- The `extra_scripts` list is replaced wholesale by `extends`, so the inherited `pre:`
  compiledb entry must be repeated beside any new `post:` entry (F-10).

### Integration Points
- `scripts/pio/merge_firmware.py` — new shared home; `homeworks/1_3-police-flasher/platformio.ini`
  switches its `post:` entry to the relative path.
- `docs/decisions/README.md` — one new row linking ADR-0014.
- `homeworks/1_3-police-flasher/homework.yaml` — `simulation.status` flips from `pending`
  to `verified` only after an executed, evidenced run.
- `.planning/phases/07-simulation-spike/` — the evidence file and the discussion artifacts.
- Phase 8 — consumes the measured session duration and the calculated cost basis for the
  changed-only simulation gate; do not pre-empt that workflow.

</code_context>

<specifics>
## Specific Ideas

- The owner is on the **free Wokwi plan**; the quota is scarce. Research records a rolling
  30-day quota of about 50 simulated minutes and a 5-minute session cap. The protocol is
  sized for a few dozen seconds of quota, not minutes.
- Local environment at discussion time: `wokwi-cli 0.28.1` is installed;
  `WOKWI_CLI_TOKEN` is unset; Docker 29.9.2 is installed but reading
  `~/.docker/config.json` is denied inside the command sandbox; `renode` and Fritzing are
  not installed.
- The command sandbox blocks outbound access to `wss://wokwi.com`, so the executed run must
  happen outside it, run by the owner.
- `wokwi.toml` points at
  `.pio/build/esp32s3_arduino/firmware.merged.bin`, so the target build must precede every
  run and the merged image is part of the measured path.
- The Phase 4.2 first CI run was 1m38s for build plus native tests and included no
  simulation; it is the only measured CI baseline and does not cover simulated minutes.
- `simulation.status: pending` is the current value; only an executed run with evidence
  justifies `verified`.

</specifics>

<deferred>
## Deferred Ideas

- **Simulation gate script (`scripts/simulate.py`)** — Phase 8; the workflow shape is not
  yet defined, and building it now would be rewritten.
- **Schema field or enum value for lint-only versus executed** — considered and declined;
  the distinction stays documentary.
- **Homework README expansion and an SVG schematic** — Phase 11 (pilot finalization), not a
  decimal phase.
- **Renode execution and STM32 simulation** — v2; the course board models are unconfirmed
  and the STATE blocker stands.
- **Fritzing illustration export** — not produced in this phase; a possible Phase 11
  artifact with attribution.
- **Nightly full simulation matrix** — out of scope; the free-tier quota cannot sustain it.
- **ESP-IDF `compiledb` completeness fallback** (carried from Phase 6) — belongs to the
  first ESP-IDF homework or a later spike, not this phase.

### Reviewed Todos (not folded)
- *Expand homework README and add a proper SVG schematic* — homework content and reader
  documentation; deferred to Phase 11.
- *Generate a root compile database so `lib/` has working IntelliSense* — resolved by
  Phase 06.1; no remaining action.
- *Trim governance ceremony (Phase 4.1)* — already completed.
- *Standardize pull request titles across homeworks* — process and CI concern; Phase 8/9.

</deferred>

---

*Phase: 7-Simulation Spike*
*Context gathered: 2026-10-26*

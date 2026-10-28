# Phase 11: Pilot Homework 1.3 — Finalization - Context

**Gathered:** 2026-10-28
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase finalizes `homeworks/1_3-police-flasher` into a complete, standalone, self-contained reference homework artifact that validates the entire repository toolchain, and decouples repository-level infrastructure (templates, scripts, docs) from any hardcoded references to `1_3`.

**In scope:**
- Finalize `homeworks/1_3-police-flasher` firmware: add transition logging on mode/speed changes for serial verification.
- Automated Wokwi simulation: expand `scenario.yaml` to verify startup and button-driven transitions, producing `serial.log` evidence within ~3–5s wall clock.
- Report contract verification: update `homeworks/1_3-police-flasher/report.md` to pass `scripts/check_report.py` cleanly, embed `assets/schematic.svg`, and update measurement ledger labels.
- Generic infrastructure decoupling: eliminate hardcoded `1_3-police-flasher` paths and comments from `scripts/gen_clangd_db.py`, `scripts/gen_schematic.py`, `templates/homework-*`, and `docs/standards/*.md`.
- Close Phase 4.2 friction log (`.planning/phases/04.2-tracer-homework-1-3/04.2-FRICTION-LOG.md`).
- Pass full local gate (`pre-commit`, `pio test`, `check_report`, `check_metadata`, `python-tests`), prepare pull request, and establish `hw/1_3-police-flasher` tag.

**Out of scope:**
- Adding new hardware platforms (STM32, Raspberry Pi Pico) — deferred to v2.
- Changing shared library architecture (`lib/common`, `lib/port`).
- Creating homeworks other than 1.3.

</domain>

<decisions>
## Implementation Decisions

### Simulation & Evidence (Wokwi scenario.yaml)
- **D-11-01:** Expand `homeworks/1_3-police-flasher/scenario.yaml` beyond the single initial pin-check to simulate button press interactions on GPIO7, asserting pin transitions and capturing full `serial.log` output.
- **D-11-02:** Add lightweight transition logging (`port_log_write`) in the firmware controller so mode/speed state changes emit identifiable log lines. This provides verifiable serial evidence for `measured (observed)` / `serial-log:` ledger entries.
- **D-11-03:** Simulation duration must remain capped (~3–5 seconds wall clock) so it runs efficiently in local checks and CI.

### Measurement Ledger & Report Contract
- **D-11-04:** Hardware bench measurements (multimeter, oscilloscope) remain honestly labeled as `not measured: bench equipment offline during automated tracer run` with documented rationale.
- **D-11-05:** Calculated rows, datasheet ratings, and simulated/serial-observed rows are updated with the exact implementation commit hash matching HEAD.
- **D-11-06:** Report structure strictly satisfies `scripts/check_report.py` (10 sections, valid status, no TODO sentinels, ASCII/English only).

### Schematic Presentation
- **D-11-07:** In `homeworks/1_3-police-flasher/report.md`, Section 5 (Hardware and Wiring) embeds the Schemdraw vector SVG `assets/schematic.svg`.
- **D-11-08:** In `homeworks/1_3-police-flasher/README.md`, retain the interactive Mermaid flowchart diagram. `assets/diagram.json` remains the sole wiring truth for Wokwi.

### Generic Decoupling (Repo-Wide Infrastructure Cleanliness)
- **D-11-09:** `scripts/gen_clangd_db.py`: Remove hardcoded `Path("homeworks") / "1_3-police-flasher"`. Dynamically discover all active homework projects under `homeworks/*/` or accept a targeted path.
- **D-11-10:** `scripts/gen_schematic.py`: Remove hardcoded docstrings referring to `1_3-police-flasher`; make CLI and helpers fully generic across any homework directory.
- **D-11-11:** `templates/homework-arduino/.clangd` and `templates/homework-espidf/.clangd`: Replace `# homeworks/1_3-police-flasher/src/main.cpp.` with generic path comments.
- **D-11-12:** `docs/standards/vscode.md` and `docs/standards/report.md`: Replace hardcoded references to `1_3-police-flasher` with generic placeholders (`homeworks/<id>`, `pio run -d homeworks/<id> ...`) to establish that `1_3` is just one homework task, not a privileged template.

### Friction Log Closure & Tagging
- **D-11-13:** Audit all 19 friction points in `04.2-FRICTION-LOG.md` and document their resolution across Phases 5–10.1 and 11.
- **D-11-14:** Tagging `hw/1_3-police-flasher` is performed via `scripts/tag_homework.sh 1_3-police-flasher` after PR merge.

### the agent's Discretion
- Exact scenario button-timing in `scenario.yaml` and specific log string formats in `controller.c` are left to the agent's implementation discretion to keep tests robust and deterministic.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing:**

### Standards & Contracts
- `docs/standards/report.md` — The 10-section report contract and verification rules.
- `docs/standards/electrical-calculations.md` — Standard calculation methods and uncertainty formulas.
- `docs/standards/vscode.md` — Developer environment setup and toolchain commands.
- `docs/decisions/0014-simulator-selection.md` — Wokwi simulator selection, scenario conventions, and evidence standards.
- `schema/homework.schema.json` — JSON schema for homework.yaml metadata.

### Historical Context & Upstream Audits
- `.planning/phases/04.2-tracer-homework-1-3/04.2-FRICTION-LOG.md` — Friction log to close upon pilot finalization.
- `.planning/phases/04.2-tracer-homework-1-3/04.2-VERIFICATION.md` — Upstream tracer verification findings.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `scripts/check_report.py` & `scripts/report/contract.py`: Debureaucratized validator for `report.md`.
- `scripts/check_metadata.py`: Validates `homework.yaml` against `schema/homework.schema.json`.
- `scripts/gen_schematic.py`: Generates Schemdraw SVG, Wokwi wiring, and Mermaid diagrams.
- `scripts/tag_homework.sh`: Validates repo state and applies release tag.
- `homeworks/1_3-police-flasher/lib/pattern/`: Pure C pattern tables and controller tested natively with Unity.

### Established Patterns
- Anti-parallel LED circuit driven by single GPIO pin (GPIO4) with complementary output and high-impedance all-off state.
- Button debounce on GPIO7 with edge-triggered mode/speed cycling.
- Pure C library under `homeworks/1_3-police-flasher/lib/` compiling for both native Unity tests and Arduino ESP32-S3 target.

### Integration Points
- `scripts/gen_clangd_db.py` merges compile databases across all homeworks.
- `scripts/affected.py` computes affected matrix for CI build and simulate steps.
- `.github/workflows/ci.yml` executes `simulate` job for PRs touching homeworks when labeled.

</code_context>

<specifics>
## Specific Ideas

- The user specifically requested: eliminate all hardcoded mentions of `1_3` from repo documentation, templates, and scripts. `1_3` must be an ordinary homework, not a magic fixture.
- Keep `1_3-police-flasher` self-contained and verifiable a year later.

</specifics>

<deferred>
## Deferred Ideas

- None — all discussed items are within the scope of Phase 11.

</deferred>

---

*Phase: 11-Pilot Homework 1.3 — Finalization*
*Context gathered: 2026-10-28*

---
phase: 07-simulation-spike
verified: 2026-10-26T16:10:17Z
status: passed
score: 25/25 must-haves verified
covered_files: [".planning/phases/04.2-tracer-homework-1-3/04.2-FRICTION-LOG.md", ".planning/phases/07-simulation-spike/07-01-PLAN.md", ".planning/phases/07-simulation-spike/07-01-SUMMARY.md", ".planning/phases/07-simulation-spike/07-02-PLAN.md", ".planning/phases/07-simulation-spike/07-02-SUMMARY.md", ".planning/phases/07-simulation-spike/07-03-PLAN.md", ".planning/phases/07-simulation-spike/07-03-SUMMARY.md", ".planning/phases/07-simulation-spike/07-04-PLAN.md", ".planning/phases/07-simulation-spike/07-04-SUMMARY.md", ".planning/phases/07-simulation-spike/07-SPIKE-EVIDENCE.md", "docs/decisions/0014-simulator-selection.md", "docs/decisions/README.md", "docs/homeworks/1_3-police-flasher.md", "generated.manifest", "homeworks/1_3-police-flasher/README.md", "homeworks/1_3-police-flasher/homework.yaml", "homeworks/1_3-police-flasher/platformio.ini", "homeworks/1_3-police-flasher/report.md", "mkdocs.yml", "pyproject.toml", "scripts/pio/merge_firmware.py", "scripts/tests/test_merge_firmware.py", "scripts/tests/test_simulation_paths.py"]
covered_digest: "v3:sha256:a7d03a1af0ac9e3261bdd29e2b3d308dc391bb7a6a4a904f9daa4c48aa5084c2"
behavior_unverified: 0
overrides_applied: 0
human_verification:
  - test: "Owner-run Wokwi session: confirm the three pasted stamped captures against the run 1-3 rows"
    expected: "Each of the three captures contains `EXIT 0` and exactly one `I pattern ready` line; wall clock 5.815 s / 8.559 s / 12.701 s and cold/warm 3.759 s / 6.753 s / 11.238 s match the table; `**Outcome:** scenario passed` and `3/3` agree with the exit codes"
    why_human: "The session is token-gated and quota-metered, so the verifier cannot re-run it; the evidence is owner-supplied captures in 07-SPIKE-EVIDENCE.md, and only a human can confirm their provenance and match to the rows"
  - test: "Velxio board capture: check `$HOME/velxio-boards.png` (587620 bytes) and the page `http://localhost:3080`"
    expected: "The screenshot exists outside the repository and shows the `BOARDS 47` catalogue, including ESP32-S3 DevKit, XIAO ESP32-S3, Arduino Nano ESP32, STM32 Blue Pill and STM32 Black Pill, as recorded in §Velxio self-host attempt"
    why_human: "The screenshot lives outside the repository and is not read by automated checks; the credibility of the observed row is a reviewer's judgement"
  - test: "Prohibition P1-1 — the homework keeps no second copy of the merge action"
    expected: "`homeworks/1_3-police-flasher/merge_firmware.py` is absent from disk and `git ls-files --error-unmatch` does not find it; the move and the `git rm` happen in one change"
    why_human: "judgment-tier prohibition; the evidence is unambiguous, but policy requires an explicit human decision"
  - test: "Prohibition P1-2 — no `scripts/simulate.py` or simulation wrapper"
    expected: "The tree contains no `scripts/simulate.py` and no simulation wrapper script; the probe lives only in the test module"
    why_human: "judgment-tier prohibition; policy requires explicit confirmation"
  - test: "Prohibition P1-3 — no real `WOKWI_CLI_TOKEN` in a test, fixture, child env or recorded command"
    expected: "The only assigned value in tracked source is the literal `dummy` (README and test_simulation_paths.py); no real token is present"
    why_human: "judgment-tier prohibition; the scan proves the `dummy` literal only, not the absence of a token outside the tracked tree"
  - test: "Prohibition P1-4 — the Wokwi command is not checked by prose or a doc-sync test"
    expected: "The only evidence is an executed subprocess with its exit status and output; no README read and no document substring comparison"
    why_human: "judgment-tier prohibition; policy requires an explicit decision"
  - test: "Prohibition P2-1 — the `WOKWI_CLI_TOKEN` value reached neither a file, an argument, nor a transcript"
    expected: "The only permitted sentence is `token supplied by the repository owner; value not recorded`; `git grep WOKWI_CLI_TOKEN -- .github` is empty"
    why_human: "judgment-tier prohibition; the verifier cannot see the full transcript or shell history"
  - test: "Prohibition P2-2 — simulated digital state or timing is not presented as bench/hardware evidence"
    expected: "Only the `expect-pin` state and the serial text are called simulation evidence; the report repeats that simulation output is not hardware evidence"
    why_human: "judgment-tier prohibition; judging the report's wording is a human decision"
  - test: "Prohibition P2-3 — quota is not derived from wall-clock"
    expected: "Wall-clock seconds and simulated minutes are separate columns; 45 s = 3 × `--timeout 15000`, labelled `calculated (upper bound)`"
    why_human: "judgment-tier prohibition; policy requires explicit confirmation"
  - test: "Prohibition P2-4 — no `--quiet` or `--interactive` added to a measurement run"
    expected: "The protocol states an explicit prohibition; the captured commands do not carry those options"
    why_human: "judgment-tier prohibition; the verifier does not reproduce the owner's actual run"
  - test: "Prohibition P2-5 — no simulated minutes, serial line, exit code or VCD path was invented"
    expected: "Every missing quantity is recorded as `absent — <reason>` or `not measured — <reason>`; VCD for run 1 and the serial logs for runs 2-3 are marked absent"
    why_human: "judgment-tier prohibition; judging whether a number was inferred from an adjacent value is a human decision"
  - test: "Prohibition P3-1 — mutable `:master` is not the recorded image identity"
    expected: "The identity is `ghcr.io/davidmonterocrespo24/velxio@sha256:5d673722…`; `:master` is named only as the pull reference"
    why_human: "judgment-tier prohibition; policy requires an explicit decision"
  - test: "Prohibition P3-2 — the vendor-documented board list is not presented as an observation"
    expected: "The `Board coverage (vendor documentation)` row carries the `datasheet` label; the observed row references the screenshot and URL"
    why_human: "judgment-tier prohibition; distinguishing observation from datasheet in prose is a human decision"
  - test: "Prohibition P3-3 — the pilot was not ported into a Velxio sketch just to take a measurement"
    expected: "Pilot compile and serial are `not measured` with a reason about the PlatformIO format; no ported sketch exists"
    why_human: "judgment-tier prohibition; policy requires explicit confirmation"
  - test: "Prohibition P3-4 — no Velxio source, image layer or AGPL asset in the MIT repository"
    expected: "`git ls-files` contains no fritzing/velxio artifact; the tree holds only the image reference and the AGPL boundary"
    why_human: "judgment-tier prohibition; a file scan cannot prove the absence of a copied fragment outside tracked paths"
  - test: "Prohibition P3-5 — the Velxio attempt consumed no Wokwi quota"
    expected: "§Velxio self-host attempt states explicitly that Wokwi was not contacted and no session was opened"
    why_human: "judgment-tier prohibition; the verifier cannot see the vendor dashboard"
  - test: "Prohibition P4-1 — `schema/homework.schema.json` is unchanged"
    expected: "`$defs.simulation.properties.status.enum` = `[none, pending, verified]`, there is no `evidence` key, and `additionalProperties: false`; the schema git diff is empty"
    why_human: "judgment-tier prohibition; policy requires an explicit decision"
  - test: "Prohibition P4-2 — no simulated value was promoted to `measured`"
    expected: "The report's five-bridge vocabulary is unchanged (`measured`, `calculated`, `simulated`, `datasheet`, `not measured`); L-08 remains `simulated`"
    why_human: "judgment-tier prohibition; judging the prose is a human decision"
  - test: "Prohibition P4-3 — the record does not claim that Renode lacks STM32 support"
    expected: "The Renode row names the unconfirmed course model, the absent STM32 homework/board profile and the missing installation; the phrase «Renode lacks STM32» does not appear"
    why_human: "judgment-tier prohibition; checking for the absence of a specific claim is a human decision"
  - test: "Prohibition P4-4 — no copy of Fritzing part graphics in shared assets"
    expected: "`docs/assets/` and `homeworks/*/assets/` received no new Fritzing artifact; `diagram.json` remains the single source of truth"
    why_human: "judgment-tier prohibition; the file scan covers tracked paths only"
  - test: "Prohibition P4-5 — the README was not expanded and no SVG diagram was added"
    expected: "§Simulation received only a pointer to the evidence/ADR; no new SVG file exists"
    why_human: "judgment-tier prohibition; judging the extent of the edit is a human decision"
  - test: "Prohibition P4-6 — status is not set to `verified` on failed/blocked; no stale sentence remains"
    expected: "`**Outcome:** scenario passed`, so `simulation.status: verified`; the 12 forbidden stale phrases are absent from report.md and README.md"
    why_human: "judgment-tier prohibition; policy requires an explicit decision"
  - test: "Prohibition P4-7 — vendor-documented or `not measured` Velxio values are not presented in the ADR as observations"
    expected: "In the ADR matrix: `19 boards` — `datasheet`, 47 boards — observed, pilot compile/serial — `not measured`; the rows are not blended"
    why_human: "judgment-tier prohibition; judging the ADR prose is a human decision"
---

# Phase 7: Simulation Spike Verification Report

**Phase Goal:** An evidence-based simulator decision recorded in ADR-0004, with measured costs and
fidelity limits. **Friction-log justification:** the Phase 4.2 log must contain at least one entry
for simulation or wiring; otherwise the spike is not run.
**Verified:** 2026-10-26T16:10:17Z
**Status:** human_needed
**Re-verification:** No — initial verification (no previous `07-VERIFICATION.md` existed)

> **ADR-0004 → ADR-0014 mapping (D-09).** The roadmap and `REQUIREMENTS.md` keep the historical
> wording "ADR-0004". ADR-0004 is a superseded licensing decision; the actual record of the
> simulator decision is `docs/decisions/0014-simulator-selection.md`. This is not a missing
> deliverable: ADR-0014 exists, has a row in the `docs/decisions/README.md` index, and carries
> the substance of the phase goal.

## Goal Achievement

### Observable Truths

| #   | Truth | Status | Evidence |
| --- | ----- | ------ | -------- |
| 1 | The Phase 4.2 log contains at least one entry about simulation or wiring (friction-log gate) | ✓ VERIFIED | `.planning/phases/04.2-tracer-homework-1-3/04.2-FRICTION-LOG.md` §F-08 "Execute the scenario: the Wokwi CLI is token-gated" (lines 113-121) and §F-09 about merge/wiring; also F-19 about path resolution |
| 2 | `pio run -d homeworks/1_3-police-flasher` after `-t clean` relinks the application and, through `scripts/pio/merge_firmware.py`, produces `firmware.merged.bin`; no local copy remains and none is tracked | ✓ VERIFIED | Live run: `-t clean` exit 0, then build `SUCCESS (9.11 s)` with the line `Merging firmware images into …/firmware.merged.bin`; file 383488 bytes (`0x5da00`). `ls` — the file is gone; `git ls-files --error-unmatch` — "did not match" |
| 3 | The merge command is a pure function; argv/offset/quoting/`-o`/fallback/both package errors/Windows naming are pinned by tests without SCons | ✓ VERIFIED | `python3 -m unittest scripts.tests.test_merge_firmware -v` — 13 tests OK; 9 named cases in `MergeCommandTests` + 2 in `MergeActionTests`; the module imports without SCons (`env = None`) |
| 4 | `esptool_directory` raises `SystemExit` when the package is missing and when `get_package_dir` returns `None` | ✓ VERIFIED | `test_missing_package_raises_system_exit`, `test_unpacked_package_raises_system_exit` green; the code checks both conditions and names `tool-esptool` and espressif32 8.x |
| 5 | The documented Wokwi command resolves `--scenario scenario.yaml` and `--diagram-file assets/diagram.json` relative to the positional project dir and fails only at the connection stage | ✓ VERIFIED | `test_documented_command_reaches_the_connection_stage` — exit 1, `Error connecting to ws://127.0.0.1:1`, without `not found` |
| 6 | Spelling the options from the repository root is rejected, and the failure names the doubled path | ✓ VERIFIED | `test_repository_root_values_fail_at_the_path_stage` (`diagram.json not found`) and `test_negative_names_the_doubled_path` (`homeworks/1_3-police-flasher/homeworks/1_3-police-flasher/assets/diagram.json`) |
| 7 | `07-SPIKE-EVIDENCE.md` exists: vocabulary before data, the single token sentence, both protocol blocks, `## Handoff to ADR-0014` with `**Outcome:**` | ✓ VERIFIED | File 33 KB; `## How to read this record` with five labels and `calculated (upper bound)`; `token supplied by the repository owner; value not recorded`; `## Owner-run protocol (Wokwi)`, `## Velxio protocol`; the handoff has `**Outcome:** scenario passed` |
| 8 | The free ladder records the `wokwi-cli` version and short SHA, lint exit 0, build-cold/warm medians from three repeats, D-07 revalidation — every value labelled | ✓ VERIFIED | `0.28.1 (7cf4ffaebfd8)`; lint exit 0 `Found 1 info`; cold 10.98/7.63/8.13 → median 8.13 s; warm 0.50/0.49/0.48 → median 0.49 s; D-07 exit 1 `Error connecting to ws://127.0.0.1:1` without `Invalid scenario step key` |
| 9 | Run 1 has a complete row: wall clock, simulator cold, exit code with a value, serial line, simulated minutes, VCD path | ✓ VERIFIED | 5.815 s; 3.759 s; `0 — scenario completed; every step passed`; `yes — exactly one I pattern ready`; `calculated (upper bound) 15 s`; `absent — Error exporting VCD: Error 6: No logic analyzer in diagram` |
| 10 | Runs 2 and 3 have warm intervals and an exact serial count | ✓ VERIFIED | warm 6.753 s and 11.238 s; each stamped output contains exactly one `I pattern ready`; the handoff says `3/3 runs observed the expected serial line` |
| 11 | The handoff outcome is exactly one of three values; `scenario passed` requires exit 0 AND `pattern ready`, so execution alone is not success | ✓ VERIFIED | `**Outcome:** scenario passed`; all three run rows exit 0; each stamped output contains `I pattern ready` and `Expected text matched: "pattern ready"`; serial reliability is the exact fraction `3/3`, not a percentage |
| 12 | The token value is absent from the repository/evidence/command/transcript; the only token sentence is the permitted one; the only assignment is the literal `dummy` | ✓ VERIFIED | `git grep` over tracked source yields one assignment: `homeworks/1_3-police-flasher/README.md:40: WOKWI_CLI_TOKEN=dummy`; `git grep WOKWI_CLI_TOKEN -- .github` is empty; the evidence holds only the permitted sentence |
| 13 | When a run produced no serial log, VCD or dashboard delta, the cell contains `absent — <first error line>` / `not measured — <reason>`, with no inferred numbers | ✓ VERIFIED | VCD run 1 — `absent — Error exporting VCD: Error 6…`; serial logs for runs 2-3 — `absent — the invocation used the literal placeholder <N>…`; dashboard — `not supplied by the owner`; simulated minutes — `calculated (upper bound)` |
| 14 | Velxio records the digest from `RepoDigests`, never the mutable tag; when the pull did not happen — `not measured` with the exact error | ✓ VERIFIED | `ghcr.io/davidmonterocrespo24/velxio@sha256:5d673722f66cf2c5c8cef1fe4a04421a7d88fd863a7a266f8661ff269b3b3bc5`; `:master` is named only as the pull reference |
| 15 | Boot readiness = the interval from `docker run` start to the first HTTP 200; wall time and first poll are recorded separately; the poll is bounded | ✓ VERIFIED | `docker run` 0.335 s (`measured`) and first HTTP 200 — attempt 9 of 60, 16.988 s (`measured`); boot readiness 16.988 s; the 120 s ceiling is labelled `calculated (upper bound)` |
| 16 | Board coverage has a named capture or an exact reason; the vendor row is separated and labelled `datasheet` | ✓ VERIFIED | Observed: `$HOME/velxio-boards.png` (587620 bytes) + URL `http://localhost:3080`, `BOARDS 47`, ESP32-S3 and STM32 present; vendor: `19 boards` labelled `datasheet`; a separate row for 182 FQBNs |
| 17 | Velxio pilot compile and serial are honestly `not measured`; a booted-but-unusable UI is a valid result | ✓ VERIFIED | `not measured — the self-hosted editor does not consume a PlatformIO project`; serial — `not measured — no UI run of the pilot was performed in this session`; the container booted and was stopped, so the unusable-UI branch did not trigger |
| 18 | No Velxio code/layer/part graphic was vendored; the AGPL boundary is recorded | ✓ VERIFIED | §Licence boundary: AGPLv3, reference only; `git ls-files | grep -i 'fritzing|velxio'` — empty; `git status --porcelain` — clean |
| 19 | ADR-0014 records measured cold/warm start, build cold/warm, session duration and serial reliability in the form the evidence supports, and fidelity limits for Wokwi/Velxio/Renode/Fritzing | ✓ VERIFIED | ADR §Measured cost: build cold 8.13 s, build warm 0.49 s, simulator cold 3.759 s, warm 6.753/11.238 s, wall clock 5.815-12.701 s, serial `3/3`, simulated minutes `calculated (upper bound)` 15 s; §Fidelity limits — vendor limits + five pilot limits; Velxio pilot compile/serial — `not measured` |
| 20 | The ADR has a platform-role matrix and a `calculated` CI cost basis with the formula, changed-project count, 1 run, PR cadence and 5/50 sensitivity | ✓ VERIFIED | Matrix Wokwi/Velxio/Renode/Fritzing with role, platforms and depth; formula `session_minutes_per_run × changed_projects_per_PR × runs_per_PR × PRs_per_month`; `PRs_per_month = 20`; 5 PR → 1.25 min, 50 PR → 12.5 min; everything `calculated` |
| 21 | `docs/decisions/README.md` receives exactly one row in date order linking to ADR-0014; the MkDocs nav contains the ADR; the docs-pins test is green | ✓ VERIFIED | One row `2026-10-26 … [0014](0014-simulator-selection.md)`; `mkdocs.yml:41` — nav entry; `test_nav_lists_every_markdown_file_under_docs` — ok |
| 22 | `simulation.status` becomes `verified` only on `**Outcome:** scenario passed`; otherwise it stays `pending` with a blocker | ✓ VERIFIED | `homeworks/1_3-police-flasher/homework.yaml:17` — `status: verified`; handoff — `scenario passed`; generated page — `wokwi (verified)`; T-15 — `verified` |
| 23 | All stale simulation claims in `report.md` and the homework README are reconciled | ✓ VERIFIED | None of the 10 forbidden phrases was found; §7, L-08, T-15, §9 industry note, §9 conclusions/status, Decision Appendix 7 and README §Simulation carry a pointer to the evidence and ADR-0014 |
| 24 | The report points to the shared `../../scripts/pio/merge_firmware.py`; no live tracked reference to the deleted project path remains | ✓ VERIFIED | `report.md` — `merge_firmware.py` count n=1, `scripts/pio/merge_firmware.py` count m=1; `git grep` with `:!.planning` — 0 matches; remaining mentions exist only in historical `.planning/` plans/summaries, which are not rewritten by policy |
| 25 | The five-bridge vocabulary is unchanged; no `simulated` became `measured`; the schema is unchanged; there is no Fritzing artifact or part graphic; `diagram.json` is canonical and lint-validated | ✓ VERIFIED | The ledger definition is unchanged; L-08 `simulated`; `$defs.simulation.properties.status.enum = [none, pending, verified]`, no `evidence`, `additionalProperties: false`; no Fritzing/velxio files; `wokwi-cli lint --offline …/assets/diagram.json` exit 0 `Found 1 info` |

**Score:** 25/25 truths verified (0 present, behavior-unverified)

### Deferred Items

None. All five roadmap success criteria are closed by this phase within the role-proportional
depth (D-05). The Renode/STM32 row and the Velxio pilot compile remain deliberately `not measured`
with reasons, not deferred gaps; a real CI simulation run is Phase 8.

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | -------- | ------ | ------- |
| `scripts/pio/merge_firmware.py` | Shared post action: `build_merge_command`, `esptool_directory`, `esptool_binary`, `_quote`, `merge_firmware`, guarded SCons import | ✓ VERIFIED | 118 lines; imports without SCons; the live build produced the merged image; the `_quote` docstring honestly bounds the atomicity claim |
| `scripts/tests/test_merge_firmware.py` | `MergeCommandTests` — 9 named cases + CR-01 action tests | ✓ VERIFIED | 13 tests OK; `test_failed_merge_raises` / `test_successful_merge_does_not_raise` added for CR-01 |
| `scripts/tests/test_simulation_paths.py` | Positive, negative, non-vacuity probes | ✓ VERIFIED | 3 tests OK; child env has exactly four names, `dummy` only |
| `homeworks/1_3-police-flasher/platformio.ini` | `post:../../scripts/pio/merge_firmware.py` next to the unchanged `pre:` compiledb | ✓ VERIFIED | Lines 20-22; `-t compiledb` exit 0, `compile_commands.json` 222.4K |
| `homeworks/1_3-police-flasher/merge_firmware.py` | Removed with `git rm` | ✓ VERIFIED | Absent from disk; not tracked |
| `pyproject.toml` | Only `"scripts/pio/*.py" = ["F821"]`, with a comment about the single location | ✓ VERIFIED | Lines 18-21 |
| `.planning/phases/07-simulation-spike/07-SPIKE-EVIDENCE.md` | Vocabulary, protocol blocks, free ladder, run table, quota ledger, handoff | ✓ VERIFIED | 33 KB, 655 lines, all sections present |
| `docs/decisions/0014-simulator-selection.md` | MADR: frontmatter, 8 sections, role matrix, measured costs, fidelity limits, calculated CI basis, SIM-03/AGPL | ✓ VERIFIED | 259 lines; `Chosen option:`; 8 MADR sections; `07-SPIKE-EVIDENCE.md` as a code span |
| `docs/decisions/README.md` | Exactly one row with `[0014](0014-simulator-selection.md)` | ✓ VERIFIED | One row, last in the table, dated 2026-10-26 |
| `homeworks/1_3-police-flasher/homework.yaml` | `simulation.status` matches the handoff outcome | ✓ VERIFIED | `tool: wokwi`, `diagram: assets/diagram.json`, `status: verified`; other keys unchanged |
| `homeworks/1_3-police-flasher/report.md` | Reconciled §7, L-08, T-15, §9, Decision Appendix 7; shared merge path | ✓ VERIFIED | For the 10 forbidden phrases — 0 matches; T-15 status `verified`; evidence/ADR pointers on lines 288-289, 350, 427-433, 482-483 |
| `homeworks/1_3-police-flasher/README.md` | §Simulation pointer instead of deferral sentences | ✓ VERIFIED | Lines 47-48 — pointer to the evidence and ADR; the command block and dummy-token paragraph are preserved |
| `docs/homeworks/1_3-police-flasher.md` | Generated Simulation cell | ✓ VERIFIED | `| Simulation | wokwi (verified) |`; `gen_views.py --all --check` — all UNCHANGED |
| `mkdocs.yml` | Nav entry for ADR-0014 | ✓ VERIFIED | Line 41 after regeneration |
| `generated.manifest` | Updated digests/bytes | ✓ VERIFIED | `--all --check` — `manifest bytes are identical` |

### Key Link Verification

| From | To | Via | Status | Details |
| ---- | -- | --- | ------ | ------- |
| `homeworks/1_3-police-flasher/platformio.ini` | `scripts/pio/merge_firmware.py` | `post:` relative extra_scripts (because `extends` replaces the block) | WIRED | The live build loaded the post action and printed the merge line |
| `scripts/tests/test_simulation_paths.py` | `homeworks/1_3-police-flasher/README.md` | The test executes the same option spelling rather than matching prose | WIRED | Positive probe exit 1 at the connection stage; README §Simulation documents the same values |
| `07-SPIKE-EVIDENCE.md` | `homeworks/1_3-police-flasher/.pio/build/esp32s3_arduino/firmware.merged.bin` | `wokwi.toml` names the merged image the post action produces | WIRED | `wokwi.toml: firmware = ".pio/build/esp32s3_arduino/firmware.merged.bin"`; the file exists after a clean build |
| `07-SPIKE-EVIDENCE.md` | `docs/decisions/0014-simulator-selection.md` | The ADR carries the conclusion and references the evidence as a code span | WIRED | ADR §More Information and Confirmation name `.planning/phases/07-simulation-spike/07-SPIKE-EVIDENCE.md`; no relative `.planning` Markdown link |
| `07-SPIKE-EVIDENCE.md` (`**Outcome:**`) | `homeworks/1_3-police-flasher/homework.yaml` | `scenario passed` — the only condition for `verified` | WIRED | Outcome `scenario passed`; YAML `status: verified`; Branch B was not activated |
| `homeworks/1_3-police-flasher/homework.yaml` | `docs/homeworks/1_3-police-flasher.md` | `simulation.status` — the generator input | WIRED | Generated page `wokwi (verified)`; `gen_views.py --all --check` green |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
| -------- | ------------- | ------ | ------------------ | ------ |
| `docs/homeworks/1_3-police-flasher.md` | Simulation cell | `homeworks/1_3-police-flasher/homework.yaml` `simulation.tool/status` through `scripts/gen_views.py` | Yes — `wokwi (verified)` in the committed page; `--check` confirms it is not a hand edit | ✓ FLOWING |
| `docs/decisions/0014-simulator-selection.md` | Platform-role matrix and measured costs | `07-SPIKE-EVIDENCE.md` run table / ladder / Velxio section | Yes — the ADR values match the evidence (3.759 / 6.753 / 11.238 / 3/3 / 16.988 / 47 / 182) | ✓ FLOWING |
| `scripts/pio/merge_firmware.py` | `firmware.merged.bin` | `env.subst("$BUILD_DIR")`, `env.BoardConfig()`, `FLASH_EXTRA_IMAGES`, `ESP32_APP_OFFSET` | Yes — the live build wrote 383488 bytes and printed the path | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| A clean build creates the merged image through the shared post action | `pio run -d homeworks/1_3-police-flasher -t clean && pio run -d homeworks/1_3-police-flasher` | `Merging firmware images into …`; `SUCCESS (9.11 s)`; file 383488 bytes | ✓ PASS |
| The repeated `pre:` compiledb works | `pio run -d homeworks/1_3-police-flasher -t compiledb` | `SUCCESS`; `compile_commands.json` 222.4K | ✓ PASS |
| Merge/simulation unit suite | `python3 -m unittest scripts.tests.test_merge_firmware scripts.tests.test_simulation_paths -v` | `Ran 14 tests … OK` | ✓ PASS |
| Full stdlib suite | `python3 -m unittest discover -s scripts/tests -t .` | `Ran 380 tests … OK` | ✓ PASS |
| Generated views are consistent | `uv run scripts/gen_views.py --all --check` | every entry `UNCHANGED`; exit 0 | ✓ PASS |
| Metadata contract | `uv run scripts/check_metadata.py` | `PASS: metadata contract satisfied` | ✓ PASS |
| Docs-pins nav test | `python3 -m unittest scripts.tests.test_docs_pins.PinConsistencyTests.test_nav_lists_every_markdown_file_under_docs -v` | `Ran 1 test … OK` | ✓ PASS |
| Canonical diagram lint | `wokwi-cli lint --offline homeworks/1_3-police-flasher/assets/diagram.json` | exit 0; `Found 1 info` (`unsupported-part`) | ✓ PASS |
| CR-01 regression | `test_failed_merge_raises` / `test_successful_merge_does_not_raise` in the suite | ok/ok; the code raises `RuntimeError` on a non-zero `env.Execute` | ✓ PASS |

### Probe Execution

Not applicable: the phase has no probe scripts (`find scripts -path '*/tests/probe-*.sh'` is empty),
and the Wokwi measurement is an owner-run session, not a probe. Execution evidence is the stamped
captures in `07-SPIKE-EVIDENCE.md`.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| ----------- | ---------- | ----------- | ------ | -------- |
| SIM-02 | 07-01, 07-02, 07-03, 07-04 | Full spike: Wokwi (primary), Velxio (self-host fallback), Renode (STM32), Fritzing (illustration) on the pilot; cold start, compile, serial reliability, measured minutes, fidelity limits; result in ADR-0004 (actually ADR-0014 per D-09) | ✓ SATISFIED | Evidence + ADR-0014 role matrix; Wokwi 3/3 executed; Velxio digest/boot/47-board catalogue; Renode/Fritzing `not measured` with reasons; CI cost basis `calculated`. Owner-run captures → human verification |
| SIM-03 | 07-04 | Fritzing SVG only with attribution; part graphics are not copied into shared assets/docs; `diagram.json` is the source of truth | ✓ SATISFIED | ADR §Licence boundary; no Fritzing/velxio file in `git ls-files`; `diagram.json` is canonical and passes lint |

**Orphaned requirements:** none. `REQUIREMENTS.md` maps Phase 7 only to SIM-02 and SIM-03, and both
are declared in the plan frontmatter (SIM-03 — in `07-04-PLAN.md`).

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| — | — | `TBD` / `FIXME` / `XXX` in phase files | — | No debt marker found; the debt-marker gate is clean |
| — | — | `scripts/simulate.py` or a simulation wrapper | — | Does not exist (D-14 observed) |
| — | — | Fritzing/velxio artifacts in the tracked tree | — | None found |
| `docs/decisions/0014-simulator-selection.md` | 51-53 | "Velxio booted reproducibly" with a single measured boot | ℹ️ Info | WR-03 in `07-REVIEW-DISPOSITION.md`, remains open; it does not violate a must-have, because the numeric value in the matrix is a single `measured` boot of 16.988 s |
| `docs/decisions/0014-simulator-selection.md` | 169-170 | "three runs consumed 45 s" while the evidence labels 45 s as an upper bound | ℹ️ Info | WR-04, open; the table above labels it `calculated (upper bound)`, so the must-have about "the form the evidence supports" is not violated |
| `docs/decisions/0014-simulator-selection.md` | 61 | The Velxio Platforms column does not list STM32, though the evidence cell of the same row names STM32 boards | ℹ️ Info | WR-02, open; the Renode row claims no exclusivity, and the observed STM32 presence is recorded in the evidence cell |
| `docs/decisions/0014-simulator-selection.md` | 180-181 | Confirmation credits `test_merge_firmware` with creating the merged image | ℹ️ Info | WR-05, open; the test proves argv/the error path, while this verification proves the merged image with a live build |
| `docs/decisions/0014-simulator-selection.md` | 158-159 | "referenced by its immutable digest" without quoting the digest | ℹ️ Info | IN-06, open; the digest is in the evidence; no must-have requires the digest in the ADR itself |

**Decision on the 12 open review findings:** none violates a must-have. CR-01 (`fixed`,
`4f053b2`) was checked: `merge_firmware()` raises `RuntimeError` on a non-zero `env.Execute`, and
two new tests pin that. The rest are wording redundancies and info notes; they remain `open` by
review decision and do not block the phase goal.

### Human Verification Required

#### 1. Owner-run Wokwi session (three captures)

**Test:** Compare the three stamped captures with the run 1-3 table in `07-SPIKE-EVIDENCE.md`.
**Expected:** Each contains `EXIT 0` and exactly one `I pattern ready`; wall clock 5.815 / 8.559 / 12.701 s; cold 3.759 s, warm 6.753 / 11.238 s; `**Outcome:** scenario passed` agrees with `3/3`.
**Why human:** The session is token-gated and quota-metered; the verifier cannot re-run it, and the evidence is owner-supplied captures.

#### 2. Velxio board capture

**Test:** Open `$HOME/velxio-boards.png` (587620 bytes) and the page `http://localhost:3080`.
**Expected:** The `BOARDS 47` catalogue, including ESP32-S3 DevKit, XIAO ESP32-S3, Arduino Nano ESP32, STM32 Blue Pill and STM32 Black Pill.
**Why human:** The screenshot lives outside the repository and is not read automatically.

#### 3-23. Judgment-tier prohibitions (21 items)

Every prohibition in `must_haves.prohibitions` across all four plans has `verification: judgment` and
`status: unresolved`; policy requires an explicit human decision on each. The automated evidence is
listed in the `human_verification` frontmatter; none appears violated. The items:

1. P1-1 — no second copy of the merge action remains.
2. P1-2 — no `scripts/simulate.py` or wrapper.
3. P1-3 — no real `WOKWI_CLI_TOKEN` in a test/fixture/env/command.
4. P1-4 — the Wokwi command is not checked by prose or a doc-sync test.
5. P2-1 — the token value was written nowhere.
6. P2-2 — simulated state/timing is not presented as hardware evidence.
7. P2-3 — quota is not derived from wall-clock.
8. P2-4 — no `--quiet` / `--interactive` in a measurement run.
9. P2-5 — no inferred number/line/VCD.
10. P3-1 — `:master` is not the image identity.
11. P3-2 — the vendor board list is not presented as an observation.
12. P3-3 — the pilot was not ported into a Velxio sketch.
13. P3-4 — no Velxio/AGPL artifacts were vendored.
14. P3-5 — Velxio consumed no Wokwi quota.
15. P4-1 — the metadata schema is unchanged.
16. P4-2 — `simulated` was not promoted to `measured`.
17. P4-3 — there is no claim that "Renode does not support STM32".
18. P4-4 — Fritzing part graphics were not copied.
19. P4-5 — the README was not expanded and no SVG was added.
20. P4-6 — the status is not `verified` on failed/blocked; no stale sentence remains.
21. P4-7 — vendor/`not measured` Velxio values are not presented as observations in the ADR.

### Gaps Summary

No gaps: 25/25 must-have truths VERIFIED, 0 blocker anti-patterns, 0 debt markers,
0 behavior-unverified truths. The phase goal is achieved in code and artifacts: ADR-0014 (mapping
the roadmap's ADR-0004 per D-09) exists, is indexed, and carries measured costs, fidelity limits,
the platform-role matrix and the calculated CI basis; the evidence file contains labelled
measurements and `scenario passed` 3/3; `simulation.status: verified` matches the handoff; all
generated views are consistent; the friction-log gate is satisfied (F-08/F-09).

The `human_needed` status is not caused by a gap, but by the 21 judgment-tier prohibitions and two
owner-supplied pieces of evidence (the Wokwi session, the Velxio screenshot), which policy requires
to be closed by an explicit human decision.

---

_Verified: 2026-10-26T16:10:17Z_
_Verifier: Claude (gsd-verifier)_

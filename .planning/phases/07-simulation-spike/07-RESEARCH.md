# Phase 7: Simulation Spike - Research

**Researched:** 2026-10-26
**Domain:** Embedded simulation evidence (Wokwi CLI, Velxio self-host, Renode, Fritzing) and
evidence-record discipline
**Confidence:** HIGH for the installed toolchain and repository mechanics; MEDIUM for
external quota semantics and Velxio self-host behaviour; LOW for anything that can only be
learned from an executed, token-gated session.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** Protocol A — three short runs (cold, warm, one repeat for serial reliability),
  each bounded by a `--timeout` of about 15 seconds. A hard quota budget is tracked after
  every run; if consumption is unexpectedly large, stop and fall back to protocol B (a
  single run).
- **D-02:** The owner supplies `WOKWI_CLI_TOKEN` outside the command sandbox (through the
  `!` prefix or a separate terminal). The token is never written to CONTEXT, the evidence
  file, a command line that is logged, or the repository; the evidence records only
  "token supplied by the repository owner; value not recorded".
- **D-03:** Compilation, the merged-image post action, and `wokwi-cli lint` are measured
  locally and consume no Wokwi quota. Only the simulation session is metered, so compile
  time and cold/warm build behaviour are measured without quota pressure.
- **D-04:** Serial reliability is recorded as an observation, not a statistic: "3/3 runs
  observed the expected serial line", with the exact run count. If protocol B is used, the
  row states the smaller count and serial reliability is labelled `not measured`.
- **D-05:** Evidence depth is role-proportional: Wokwi executed; Velxio a self-host attempt
  through the prebuilt Docker image (boot, ESP-IDF compile, serial) whose self-host board
  limit is itself evidence; Renode `not measured` with the reason "no confirmed STM32
  platform; Renode not installed"; Fritzing `not measured` with the reason "not a
  simulator", the licence boundary only (SIM-03).
- **D-06:** If the Docker daemon or the image pull is unavailable, the owner may run the
  Velxio attempt outside the sandbox. If it still cannot run, the evidence records
  `not measured — <exact reason>` and no number is inferred.
- **D-07:** The Wokwi alpha scenario field names are revalidated against the installed
  `wokwi-cli 0.28.1` during the executed run. Any change found is owned by this phase
  (F-10).
- **D-08:** Raw measurements live in
  `.planning/phases/07-simulation-spike/07-SPIKE-EVIDENCE.md`: exact commands, wall-clock
  durations, serial output, quota consumed per run, and a per-run table. Every value
  carries one of the established labels — measured, calculated, datasheet, or explicitly
  not measured, with the reason. The ADR carries the conclusion and links to this file.
- **D-09:** The decision is `docs/decisions/0014-simulator-selection.md` plus a row in
  `docs/decisions/README.md`. The roadmap's "ADR-0004" is left untouched; the mapping
  **0004 → 0014** is recorded here. ADR `0004` remains the superseded licence decision.
- **D-10:** `schema/homework.schema.json` is not changed. `simulation.status: verified`
  means an executed run with evidence; lint-only stays `pending`.
- **D-11:** The CI cost basis in the ADR is **calculated from measured inputs**: measured
  session duration × changed projects per pull request × runs per month, compared with the
  published quota. It is labelled `calculated`, not `measured`.
- **D-12:** `merge_firmware.py` is promoted to `scripts/pio/merge_firmware.py` and consumed
  through a relative `post:` `extra_scripts` entry that survives `pio run -d <project>`.
  The per-homework copy is removed in the same change. The tool stays version-aware.
- **D-13:** The F-19 path-resolution check is behavioural where possible without network:
  the documented command is exercised with `WOKWI_CLI_TOKEN=dummy` and the failure must be
  a connection error, not a missing-file or doubled-path error. It must not become a
  prose/doc-sync test.
- **D-14:** No `scripts/simulate.py` gate is built in this phase.
- **D-15:** The homework README expansion and the SVG schematic are deferred to Phase 11.

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

### Deferred Ideas (OUT OF SCOPE)

- `scripts/simulate.py` gate (Phase 8).
- A schema field or enum value for lint-only versus executed (considered and declined).
- Homework README expansion and an SVG schematic (Phase 11).
- Renode execution and STM32 simulation (v2).
- Fritzing illustration export (not produced in this phase).
- Nightly full simulation matrix (out of scope).
- ESP-IDF `compiledb` completeness fallback (later).

</user_constraints>

## Summary

This phase is a measurement spike, not a feature build. The research therefore separates
three kinds of fact: what the **installed toolchain provably does** (verified by running the
local binaries and reading the CLI source at the exact tag the binary reports), what the
**vendors document** (quota, licences, board coverage), and what **only an executed run can
establish** (boot time, serial behaviour, simulated minutes). The last group is deliberately
left empty here and must be filled in `07-SPIKE-EVIDENCE.md`.

The single largest correction to the phase's working assumptions is about the scenario
schema. The repository's `scenario.yaml` is **correct for `wokwi-cli 0.28.1`**: `expect-pin`
reads `part-id`, `name`, and `value`. The published Wokwi docs are stale — they document
`pin` and `expected`, which pass local validation but are read differently by the CLI. The
authoritative evidence is the source at the installed commit (`7cf4ffaebf`, which is exactly
what `wokwi-cli --short-version` reports), not the docs page. D-07's revalidation can
therefore be closed **before** the paid run, by a network-free probe.

The second significant finding is that the F-19 path-resolution check can be made fully
deterministic and network-free. The CLI honours an undocumented `WOKWI_CLI_SERVER`
environment variable; pointing it at `ws://127.0.0.1:1` makes the CLI pass every local check
and fail at the connection stage. That converts D-13's "behavioural where possible" from a
manual observation into a two-assertion unit test with a negative control, costing no quota.

The third is a coupling the plan must not miss: flipping `simulation.status` to `verified`
and adding `docs/decisions/0014-simulator-selection.md` both change **generated** files.
`docs/homeworks/1_3-police-flasher.md` is in `generated.manifest`, and `mkdocs.yml`'s nav is
generated by scanning `docs/decisions/`. Without `uv run scripts/gen_views.py --all` the
`gen-views-check` hook fails, and
`test_docs_pins.py::test_nav_lists_every_markdown_file_under_docs` fails on a clean
checkout.

**Primary recommendation:** Plan the phase in four waves — (1) local, quota-free mechanics
(promotion, path test, lint re-assertion), (2) the owner-run Wokwi session with a
timestamp-stamping wrapper and a hard 15 000 ms timeout, (3) the owner-run Velxio boot
attempt, (4) the evidence file, ADR-0014, the status flip, and one `gen_views.py --all`
regeneration. Treat the Wokwi run as a `checkpoint:human-action` with a copy-paste block and
a fixed capture format, because the agent cannot reach `wss://wokwi.com` and must never see
the token.

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| SIM-02 | A full spike measures Wokwi (primary), Velxio (self-hosted fallback), Renode (STM32), and Fritzing (illustration) on the pilot, including cold start, compile, serial reliability, measured minutes, and fidelity limits; recorded in an ADR. | Verified CLI invocation shape, exit codes, quota semantics, scenario schema, `wokwi.toml` keys, and the decomposition of "cold start" into three named quantities (see *Measurement Protocol*). Velxio self-host facts, Renode/Fritzing `not measured` justifications, and the CI cost formula are all below. |
| SIM-03 | Fritzing SVGs may be used in reports with attribution; part graphics are not copied into shared assets or the docs site; `diagram.json` remains the source of truth. | Fritzing licence quotes verified from the app README; the FAQ restriction recorded; the phase produces no Fritzing artifact, so the criterion is satisfied by the ADR's licence paragraph plus a "no artifact produced" statement. |

## Architectural Responsibility Map

This repository is tooling, not a multi-tier application; the tiers are the developer
workstation, the hosted simulation service, the repository artifact layer, and CI.

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Firmware image assembly (merged flash image) | Local build (PlatformIO/SCons post action) | — | The merge must run where the toolchain and `tool-esptool` live; the hosted service only receives bytes. |
| Scenario execution and serial observation | Hosted simulation service (Wokwi cloud) via local CLI | Local CLI (validation, upload, exit-code mapping) | Simulation runs remotely; path resolution, scenario validation, and exit-code mapping are local. |
| Path-resolution contract (F-19) | Local test suite | Local CLI | The contract is about how the CLI joins option values to the project dir; only a local invocation can observe it. |
| Compile-time and build evidence | Local build | — | Compilation is local by construction and consumes no quota. |
| Quota accounting | Hosted service dashboard | Evidence file | Only the vendor dashboard observes consumption; the evidence records the observation or a bound. |
| Self-hosted fallback measurement | Local container runtime (Velxio image) | Browser UI | The image runs locally, but its editor is a browser app with no documented headless API. |
| Decision record and evidence | Repository artifact layer (`docs/decisions/`, `.planning/`) | — | The ADR is the conclusion; the evidence file is the raw data. |
| CI cost basis | Repository artifact layer (ADR) | Phase 8 CI | The formula is calculated here; execution and cadence are Phase 8. |

## Standard Stack

### Core

| Tool | Version | Purpose | Why Standard |
|------|---------|---------|--------------|
| `wokwi-cli` | **0.28.1** (`7cf4ffaebfd8`), MIT, installed from GitHub releases | Scenario execution, `lint`, serial capture | The installed binary; the repo's README already documents this version. Latest is 0.29.1 (2026-10-23); the scenario command shapes are unchanged between the two tags `[CITED: github.com/wokwi/wokwi-cli/compare/v0.28.1...v0.29.1]`. |
| PlatformIO Core | **6.2.0** (verified) | Build and merged image | Pinned repository toolchain. |
| `platformio/espressif32` | **8.0.0** | Target platform | Pinned; ships `tool-esptool` with esptool **5.4.0**. |
| esptool | **5.4.0** inside `~/.platformio/packages/tool-esptool` | `merge-bin` | The only supported merge path for the 16 MB custom partition table. |
| Docker | **29.9.2** (installed) | Velxio self-host attempt | Only local path to Velxio. Daemon is **unreachable inside the command sandbox** (`unix:///var/run/docker.sock` permission denied), so the attempt is owner-run. |

### Supporting

| Tool | Version | Purpose | When to Use |
|------|---------|---------|-------------|
| Python 3 stdlib (`subprocess`, `unittest`) | 3.13.13 | Timestamp wrapper; new path test; merge-script unit test | Always; the repo suite is stdlib-only. |
| `uv` | 0.13.5 | Runs scripts with PEP 723 headers; generator check | `uv run scripts/gen_views.py --all`, targeted test runs. |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Wokwi CLI with a real token | `wokwi/wokwi-ci-action@v1` in CI | Phase 8 work; this phase must not wire CI (SIM-04 boundary). |
| Docker self-host | `velxio.dev` hosted, or `velxio-cli` | Both need an account/token and are paid for CI; the self-host image is the only zero-cost second real measurement. |
| A committed measurement harness script | A one-off inline `python3` wrapper recorded in the evidence file | D-14 forbids a gate; a committed wrapper becomes a second tool surface with no recurring owner. |

**Installation (only if the CLI is missing; pin the version):**

```sh
curl -L https://wokwi.com/ci/install.sh | sh -s 0.28.1
```

The script prepends `v` itself (it downloads `.../releases/download/v$version/...`), so pass
`0.28.1`, not `v0.28.1` `[CITED: wokwi.com/ci/install.sh]`.

**Version verification (run this session):**

```text
wokwi-cli --short-version            -> 0.28.1 (7cf4ffaebfd8)
pio --version                        -> PlatformIO Core, version 6.2.0
~/.platformio/packages/tool-esptool/esptool version -> esptool v5.4.0 / 5.4.0
docker --version                     -> Docker version 29.9.2, build a82e528
python3 --version                    -> Python 3.13.13
```

## Package Legitimacy Audit

**No npm, PyPI, or crates package is installed by this phase.** The seam's registry lookup
could not run (`query package-legitimacy check` returned `SUS` with every signal `null`
because the npm request failed with certificate-trust errors); direct probes confirm the
packages do not exist at all, so the "no observation" is resolved by a different fact:
this phase installs nothing from a package registry.

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| `wokwi-cli` | none — **404 on npm and PyPI** | n/a | n/a | github.com/wokwi/wokwi-cli (MIT) | n/a | GitHub-release binary; pin with `sh -s 0.28.1` |
| `velxio` | none — **404 on PyPI** | n/a | n/a | github.com/davidmonterocrespo24/velxio (AGPLv3) | n/a | Container image `ghcr.io/davidmonterocrespo24/velxio:master`; record the digest |

**Packages removed due to `SLOP` verdict:** none.
**Packages flagged as suspicious `[SUS]`:** none.

Supply-chain notes for the planner:
- `ghcr.io/...:master` is a **mutable tag**. Record `docker inspect --format
  '{{index .RepoDigests 0}}' ghcr.io/davidmonterocrespo24/velxio:master` in the evidence so
  the measurement is reproducible.
- The CLI installer downloads an unsigned binary from GitHub releases. Record the version
  and short SHA in the evidence; the repository already treats tool versions as pinned
  facts.

## Architecture Patterns

### System Diagram — evidence flow

```text
source tree ──► pio run (local) ──► firmware.merged.bin ─┐
                                                          │
diagram.json ──► wokwi-cli lint --offline (local, no token, no quota)
                                                          │
scenario.yaml ─► scenario validation (local, dummy token) ─┤
                                                          ▼
                          wokwi-cli <project> --scenario … --timeout 15000
                                                          │
                        token ─► wokwi.toml ─► diagram ─► firmware ─► elf
                                                          │
                                             (dummy token + WOKWI_CLI_SERVER)
                                                          ├──► connection error  ← path check
                                             (real token, owner-run)
                                                          ▼
                                   hosted simulation ──► serial bytes + exit code
                                                          │
                          exit 0 = scenario passed │ 42 = timeout │ 1 = local/assert fail
                                                          ▼
                          07-SPIKE-EVIDENCE.md ──► ADR-0014 ──► decisions/README.md
                                                          ▼
                          homework.yaml status ──► gen_views.py --all ──► docs page + mkdocs nav
```

### Recommended Project Structure (files this phase adds or moves)

```text
docs/decisions/
├── README.md                          # + one row for 0014
└── 0014-simulator-selection.md        # new ADR (MADR frontmatter)

scripts/pio/
├── compiledb.py                       # existing pattern for a shared pre: script
└── merge_firmware.py                  # moved from the homework, now shared

scripts/tests/
├── test_merge_firmware.py             # new: pure command-assembly test
└── test_simulation_paths.py           # new: F-19 behavioural check (network-free)

homeworks/1_3-police-flasher/
├── platformio.ini                     # post:../../scripts/pio/merge_firmware.py
├── homework.yaml                      # simulation.status: verified (after evidence)
└── merge_firmware.py                  # DELETED in the same change

.planning/phases/07-simulation-spike/
└── 07-SPIKE-EVIDENCE.md               # new: raw data, commands, per-run table
```

### Pattern 1: Local-first measurement ladder

**What:** Order every check from cheapest to most expensive, with the paid step last.
**When to use:** Any quota-scarce measurement.
**Why:** Four of the five evidence types are free. Only the session costs simulated
minutes.

```text
1. lint (no token, offline)                       cost: 0
2. scenario validation (dummy token, fails before connect) cost: 0
3. path-resolution check (dummy token + local server)   cost: 0
4. clean + incremental compile, merge action       cost: 0
5. Velxio self-host boot                           cost: 0 Wokwi quota
6. Wokwi session × 3                               cost: ≤ 45 s simulated
```

### Pattern 2: Measurement wrapper (no repository artifact)

**What:** A one-off `python3` wrapper that stamps every output line with a monotonic
offset, so `Connected to Wokwi Simulation API` and `Starting simulation...` become
timestamps.
**When to use:** Every owner-run session.
**Example (validated this session against the dummy-token probe):**

```python
# Recorded inline in the evidence file; not committed as a tool.
import subprocess, sys, time
t0 = time.monotonic()
proc = subprocess.Popen(sys.argv[1:], stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT, text=True, bufsize=1)
for line in proc.stdout:
    print(f"+{time.monotonic() - t0:8.3f}s | {line.rstrip()}", flush=True)
rc = proc.wait()
print(f"+{time.monotonic() - t0:8.3f}s | EXIT {rc}", flush=True)
sys.exit(rc)
```

`--quiet` must **not** be passed on measurement runs: it suppresses the two lines the
wrapper exists to timestamp `[CITED: github.com/wokwi/wokwi-cli/blob/7cf4ffaebf/packages/cli/src/commands/simulate.ts]`.

### Pattern 3: Three-valued path probe (positive, negative, non-vacuity)

Follows the Phase 6 `ClangdCheckCommandTests` precedent (positive, negative, non-vacuity).

```text
positive:    correct relative option values  -> connection-stage error, no "not found"
negative:    repo-root option values         -> "diagram.json not found in <doubled path>"
non-vacuity: assert the negative case actually mentions the doubled path
```

The CLI's own check order makes this reliable: token → `wokwi.toml` → `diagram.json` →
firmware → ELF → lint → scenario → connect. A missing token therefore aborts **before**
path resolution (F-19's root cause), and a wrong path aborts **before** any connection.

### Anti-Patterns to Avoid

- **Presenting the simulator as an instrument:** Wokwi has no current, brightness, or
  voltage readout. Only `expect-pin` digital state and serial text are evidence (PITFALLS
  C10).
- **Calling a lint result "verified":** lint is not execution (D-10).
- **Deriving quota from wall-clock:** the documented quota is *simulation time*; wall-clock
  is a different quantity used for the session cap.
- **Parsing the Wokwi docs for the scenario schema:** the docs are stale (see Pitfall 1).
- **Adding a `scripts/simulate.py` gate now:** D-14; Phase 8 owns the workflow shape.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Bootable 16 MB flash image | A hand-assembled `dd`/`cat` image | `esptool merge-bin` via the post action | Offsets, headers, and flash-size padding are encoded in the tool. |
| Scenario assertion loop | A shell loop tailing the serial log | `--scenario` + `expect-pin` + exit code | The CLI validates steps locally and reports a precise failure. |
| Path-resolution proof | A prose/doc-sync test | The three-valued `wokwi-cli` probe with `WOKWI_CLI_SERVER` | Prose tests were pruned in quick task `261026-ky7`; only behaviour is wanted. |
| Serial capture | A pty/`screen` script | `--serial-log-file` | Raw serial bytes, no terminal escaping. |
| Quota measurement | Wall-clock × a guessed factor | Docs' definition + dashboard before/after | The only direct observation is the vendor dashboard. |
| Firmware-image test | A fake SCons environment emulator | Pure function extraction + one stub `env` | The SCons surface used is four methods; a stub is ten lines. |
| Container orchestration | A compose file or wrapper script | The documented `docker run` command | One attempt, one container; the README's command is the contract. |

**Key insight:** every hand-rolled substitute in this domain either consumes quota or
produces a number nobody can reproduce. The vendor tools already emit machine-readable
evidence (exit codes, serial log, VCD); the phase's job is to capture, not to generate.

## Runtime State Inventory

This phase performs one **file move with a path contract** (`merge_firmware.py`) and one
**metadata status flip**. Both can leave runtime state behind.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | None — no database, cache, or datastore holds the script path. Verified by reading `platformio.shared.ini`, `platformio.ini`, and `scripts/` (no references outside the homework). | None |
| Live service config | None. No live service is configured by this phase. Wokwi's cloud stores no project state: firmware is uploaded per run and deleted by the vendor. Velxio's container volumes are disposable and named in the evidence, not in the repo. | None (record the container name and volumes in the evidence) |
| OS-registered state | None — no launchd/systemd/scheduler registration. The `wokwi-cli` installer symlinks `$HOME/bin/wokwi-cli`; that is an existing install, not a phase artifact. | None |
| Secrets/env vars | `WOKWI_CLI_TOKEN` is read from the environment only; `WOKWI_CLI_SERVER` is a test-only override. Both are process-scoped; nothing persists. `gitleaks` has no Wokwi-specific rule (no `.gitleaks.toml`), so the protection is process discipline. | Never export in a logged shell (`set -x` forbidden); never write to a file; evidence records "value not recorded". |
| Build artifacts | `homeworks/1_3-police-flasher/.pio/build/esp32s3_arduino/firmware.merged.bin` (374.5 KB) and `firmware.elf` (6.4 MB) exist today. A clean build regenerates both. The promoted script writes only `$BUILD_DIR/firmware.merged.bin`. | Rebuild after the promotion so the post action proves the new relative path; never track `.pio/`. |
| Generated views | `docs/homeworks/1_3-police-flasher.md` currently contains `| Simulation | wokwi (pending) |` and is in `generated.manifest`; `mkdocs.yml` lists every ADR. | `uv run scripts/gen_views.py --all` after the status flip **and** after adding the ADR; commit the manifest with them. |
| Lint configuration | `pyproject.toml` has a per-file ignore `"homeworks/*/merge_firmware.py" = ["F821"]`. After the move it matches nothing. | Remove the stale ignore; `scripts/pio/*.py` already covers the new location. |

## Friction-Log Traceability

| Entry | What Phase 4.2 recorded | What this research establishes |
|-------|-------------------------|--------------------------------|
| F-08 | The CLI is token-gated; lint works without a token; the token is a CI credential | Confirmed: `requireToken()` runs first (`utils/token.ts`), lint needs no token, lint exit 0 with 1 info. The lint-vs-executed distinction stays documentary (D-10/D-14). |
| F-09 | `tool-esptool` replaced `tool-esptoolpy`; esptool 5 uses `merge-bin` and `--flash-mode`/`--flash-size` | Confirmed on the installed package (`esptool v5.4.0`). Promotion needs a `None` guard because `get_package_dir` returns `None`, and must not parse the PlatformIO package version. |
| F-10 | `extends` drops list options; option paths are project-relative; the scenario format is alpha | Confirmed from PlatformIO's `GetExtraScripts` and the CLI source; the field names are current (`name`/`value`), and local validation runs before connecting. |
| F-19 | A missing token masked a wrong path rule | Turned into a deterministic probe: `WOKWI_CLI_TOKEN=dummy` + `WOKWI_CLI_SERVER=ws://127.0.0.1:1` reaches the connection stage, and repo-root paths still fail with the doubled path. |

## Measurement Protocol (design)

This section is the deliverable the planner needs. It is deliberately prescriptive.

### Step 0 — Vocabulary (write this into the ADR)

"Cold start" is ambiguous in SC1. Decompose it and never use the bare phrase:

| Name | Definition | How measured | Cost |
|------|------------|--------------|------|
| **Build cold** | `pio run` after `pio run -t clean`, packages already installed | wall clock, 3 repeats, median | 0 |
| **Build warm** | `pio run` after touching `src/main.cpp` | wall clock, 3 repeats, median | 0 |
| **Simulator cold** | process spawn → first serial byte, **first invocation in the measurement session** | timestamp wrapper | ≤ timeout |
| **Simulator warm** | same interval on a subsequent invocation in the same session | timestamp wrapper | ≤ timeout |
| **Session duration (simulated)** | simulated time consumed by the scenario | bounded by `--timeout`; exact value from the dashboard delta, or from the VCD last timestamp if the run produces one | = quota |
| **Session duration (wall)** | process spawn → exit | timestamp wrapper total | 0 (not the quota unit) |

**There is no local CLI cache to clear.** Verified in source: the only network fetch outside
a session is the board bundle for `lint` without `--offline`, held in memory for the process
and never written to disk `[CITED: …/packages/cli/src/lint/index.ts]`. So "cold" cannot mean
"empty cache"; the ADR must define it as "first connection in the session vs reconnection"
and say so explicitly rather than implying a cache effect.

### Step 1 — Free measurements (agent or owner, in sandbox)

```sh
# 1. lint (no token)
wokwi-cli lint --offline homeworks/1_3-police-flasher/assets/diagram.json
#    expected: exit 0, "Found 1 info" with [unsupported-part] for board-esp32-s3-devkitc-1

# 2. scenario validation (dummy token — proves field names without a session)
: > "$TMPDIR/fixture.elf"   # any existing file satisfies the ELF existence check
WOKWI_CLI_TOKEN=dummy WOKWI_CLI_SERVER=ws://127.0.0.1:1 \
  wokwi-cli homeworks/1_3-police-flasher \
  --scenario scenario.yaml --diagram-file assets/diagram.json \
  --elf "$TMPDIR/fixture.elf" --timeout 15000
#    expected: reaches the connection stage; no "Invalid scenario step key"

# 3. build cold / warm (see Step 0)
pio run -d homeworks/1_3-police-flasher -t clean
pio run -d homeworks/1_3-police-flasher
```

Observed this session: an **incremental no-op** `pio run -d homeworks/1_3-police-flasher`
reports `[SUCCESS] Took 0.54 seconds` and takes 0.81 s wall including CLI startup. That is a
baseline, not the phase's measurement; a clean build is materially longer.

### Step 2 — Owner-run Wokwi session (protocol A)

Preconditions: the target build is green and `firmware.merged.bin` exists; the dashboard
usage figure is noted before the first run.

```sh
cd /Users/vloktiev/Dev/miltech/homeworks
read -rs WOKWI_CLI_TOKEN && export WOKWI_CLI_TOKEN   # never echoed, never in history
```

Run 1 (cold), 2 (warm), 3 (repeat). Each run:

```sh
python3 -u "$TMPDIR/stamp.py" wokwi-cli homeworks/1_3-police-flasher \
  --scenario scenario.yaml --diagram-file assets/diagram.json \
  --timeout 15000 --serial-log-file "$HOME/wokwi-run<N>.serial.log" \
  | tee "$HOME/wokwi-run<N>.log"
```

Capture rules:
- Do **not** add `--quiet`.
- Do **not** pass `--interactive`.
- Read the dashboard usage figure after each run and write the delta into the evidence; if
  the figure has coarse granularity, record the timeout bound instead and label the quota
  row `calculated (upper bound)`.
- Optional on run 1 only: `--vcd-file "$HOME/wokwi-run1.vcd"` (see Open Question 3).
- Strip ANSI if present (`FORCE_COLOR` may be set in some shells).

Exit-code mapping for the evidence table (from source):

| Exit | Meaning | Evidence label |
|------|---------|----------------|
| 0 | scenario completed; every step passed | `measured` |
| 42 | `--timeout` reached (default `--timeout-exit-code`) | `measured` (timeout) |
| 1 | token, config, path, firmware, scenario validation, or assertion failure | `measured` (failure) — read the first error line |

Serial reliability: the serial log must contain `pattern ready`; the exit code 0 already
implies `wait-serial` matched, but record both. Count is exact by construction ("3/3"),
never a percentage (D-04).

### Step 3 — Owner-run Velxio attempt

```sh
docker pull ghcr.io/davidmonterocrespo24/velxio:master
docker inspect --format '{{index .RepoDigests 0}}' ghcr.io/davidmonterocrespo24/velxio:master
time docker run -d --name velxio -p 3080:80 \
  -v velxio-data:/app/data -v velxio-arduino-libs:/root/.arduino15 \
  -v velxio-arduino-user-libs:/root/Arduino -v velxio-ccache:/var/cache/ccache \
  -v velxio-build:/var/lib/velxio-build \
  ghcr.io/davidmonterocrespo24/velxio:master
time curl -sf -o /dev/null http://localhost:3080   # poll until 200
docker logs --tail 50 velxio
```

**Feasibility caveat the planner must design around:** the self-hosted Velxio is a
browser editor. Its OSS README documents no headless CLI or HTTP run API; `velxio-cli` is
the hosted, token-gated path `[CITED: github.com/davidmonterocrespo24/velxio]`. It also
consumes sketches, not PlatformIO projects with `lib_deps` symlinks. The honest outcomes,
in order of likelihood:

1. **boot measured**, board list observed (ESP32-S3 + ESP-IDF present; STM32 absent), pilot
   compile and serial `not measured — the self-hosted editor does not consume a PlatformIO
   project` ;
2. **boot measured + a trivial ESP-IDF capability compile** in the UI (not the pilot);
3. **`not measured — <exact reason>`** (D-06).

Do **not** claim the pilot compiled or ran in Velxio unless a screenshot and a serial line
exist in the evidence.

The named volumes matter: without them the first ESP-IDF compile after a restart is 5–7
minutes instead of 5–30 seconds, which would make any "compile time" meaningless
`[CITED: github.com/davidmonterocrespo24/velxio]`.

### Step 4 — Calculated CI cost basis (D-11)

```
quota_minutes_per_30d = session_minutes_per_run × changed_projects_per_PR × runs_per_PR × PRs_per_month
```

Inputs and their labels:

| Input | Source | Label |
|-------|--------|-------|
| `session_minutes_per_run` | measured session duration, or the `--timeout` bound | `measured` or `calculated (upper bound)` |
| `changed_projects_per_PR` | `scripts/affected.py` fanout; typical 1 for a homework change, 1–3 under research STACK §3.7 | `calculated` |
| `runs_per_PR` | 1 (one scenario per project) | `calculated` |
| `PRs_per_month` | stated assumption (write it down; do not leave it implicit) | `assumed` |
| Published quota | Free 50 min rolling 30 days; session cap 5 min | `datasheet` (vendor docs) |

Also state the **session-cap** check separately: measured session wall-clock ≪ 5 min.
Worked example shape to include in the ADR (fill with measured values):

```text
0.25 min (15 s timeout bound) × 1 project × 1 run × 20 PRs = 5.0 min per 30 days = 10 % of Free
```

### Step 5 — Fidelity limits (must appear in the ADR)

Verified vendor limits for ESP32/ESP32-S3 `[CITED: docs.wokwi.com/guides/esp32]`:
Bluetooth "Not implemented"; I2C "Master only. 10-bit addressing not supported"; I2S partial
(ESP32) / absent (S3); MCPWM "Not implemented"; RTC "Only RTC Pull-up / Pull-down resistors";
ULP "Not implemented"; CPU frequency capped at "about 8 MHz" by default (override
`cpuFrequency`), which affects instruction timing but not peripheral timing.

Pilot-specific limits (already in the report, must not be contradicted):
- The all-off half-bridge frame leaves node X floating; "both LEDs dark" is a
  simulation-only approximation (F-07, report §8).
- The anti-parallel pair drives only the HIGH-lit LED in `PATTERN_MODE_SOLID`.
- No electrical claim (current, brightness, forward voltage) is supported by simulation.
- `board-esp32-s3-devkitc-1` is reported by lint as an **undocumented part type**
  ("This part may change or be removed in future versions") — a maintenance risk the ADR
  should name.
- The scenario API is alpha: "The API is not fully documented yet, and may change"
  `[CITED: docs.wokwi.com/wokwi-ci/automation-scenarios]`.

## Common Pitfalls

### Pitfall 1: Trusting the Wokwi docs for the scenario schema

**What goes wrong:** The docs table and examples for `expect-pin` show `pin` and `expected`.
The installed 0.28.1 reads `name` (preferred) and `value`; `pin` is accepted only as a
deprecated alias, and `expected` is ignored.
**Why it happens:** The docs lag the CLI's `pin`→`name` / `control`→`name` migration.
**How to avoid:** Treat the CLI source at the installed commit as authoritative. The repo's
`name`/`value` shape is correct.
**Warning signs:** A scenario that validates but fails at runtime with "expected to be 1 but
was …" because `value` is `undefined`.

### Pitfall 2: `--timeout` is milliseconds of *simulated* time

**What goes wrong:** `--timeout 15` aborts after 15 ms; the run looks like a firmware boot
failure and still consumes a session.
**How to avoid:** Always write `--timeout 15000`. The default is `30000`; `0` disables the
timeout entirely.
**Warning signs:** Exit 42 in well under a second; no serial output.

### Pitfall 3: The token gate masks path resolution (F-19)

**What goes wrong:** Without a token the CLI exits before resolving any path, so a wrong
command passes review.
**How to avoid:** `WOKWI_CLI_TOKEN=dummy` plus `WOKWI_CLI_SERVER=ws://127.0.0.1:1`.
**Warning signs:** "Missing WOKWI_CLI_TOKEN" in a run that was supposed to prove paths.

### Pitfall 4: Option values are joined to the positional project directory

**What goes wrong:** `--diagram-file homeworks/1_3-police-flasher/assets/diagram.json`
becomes `<project>/homeworks/1_3-police-flasher/assets/diagram.json`.
**How to avoid:** Option values are `assets/diagram.json` and `scenario.yaml`, always.
**Warning signs:** `diagram.json not found in <…>/homeworks/1_3-police-flasher/homeworks/…`.

### Pitfall 5: `lint` on a project directory looks only for `diagram.json`

**What goes wrong:** `wokwi-cli lint homeworks/1_3-police-flasher` reports "diagram.json not
found" because the diagram lives in `assets/`.
**How to avoid:** Pass the file path: `wokwi-cli lint --offline
homeworks/1_3-police-flasher/assets/diagram.json`.

### Pitfall 6: `extends` replaces `extra_scripts` wholesale

**What goes wrong:** Adding the `post:` entry drops the inherited
`pre:../../scripts/pio/compiledb.py`, so `compile_commands.json` silently stops being
produced.
**How to avoid:** Repeat the `pre:` entry beside the `post:` entry (already done; keep it
when editing the path).

### Pitfall 7: `pre:`/`post:` are load order, not build phases

**What goes wrong:** Assuming `post:` means "runs after the build".
**How to avoid:** PlatformIO loads `pre:` scripts before `$BUILD_SCRIPT` and `post:` scripts
after it; the actual merge is an SCons **post-action** registered with
`env.AddPostAction`. Also: `pio run -t clean` exits before either list is loaded, so a clean
measurement is two commands.

### Pitfall 8: `get_package_dir` returns `None`, not an error

**What goes wrong:** On a platform without `tool-esptool` (e.g. an older espressif32), the
current script does `join(None, "esptool")` and dies with a `TypeError` traceback.
**How to avoid:** Check `"tool-esptool" in env.PioPlatform().packages` at load time and fail
with a named message; resolve the path inside the post action.

### Pitfall 9: PlatformIO's `tool-esptool` version is not esptool's version

**What goes wrong:** `package.json` says `"version": "2.50400.0"` while `esptool version`
says `5.4.0`; a major check against the package version is meaningless.
**How to avoid:** Probe `esptool version` (or the presence of `merge-bin`) and parse the
tool's own output.

### Pitfall 10: The status flip and the new ADR change generated files

**What goes wrong:** Flipping `simulation.status` edits an input, not the committed page;
adding an ADR leaves `mkdocs.yml` stale.
**How to avoid:** `uv run scripts/gen_views.py --all` after both changes, then
`--check`. `docs/homeworks/1_3-police-flasher.md` is in `generated.manifest`, and
`test_docs_pins.py::test_nav_lists_every_markdown_file_under_docs` fails when an ADR is not
in the nav.

### Pitfall 11: The stale ruff ignore

**What goes wrong:** `pyproject.toml` ignores F821 for `homeworks/*/merge_firmware.py`;
after the move the entry is dead and the new file's `Import("env")` relies on the
`scripts/pio/*.py` entry.
**How to avoid:** Delete the homework pattern in the same commit as the move; confirm
`scripts/pio/*.py = ["F821"]` still covers the new file.

### Pitfall 12: Quota miscounting

**What goes wrong:** Presenting wall-clock seconds as "simulated minutes", or assuming a
failed connection costs nothing (it does — no session is opened, so it does cost nothing;
but a failed *scenario* does cost its simulated time).
**How to avoid:** Keep the two columns separate in the evidence; label the quota row
`measured` only when the dashboard delta is real.

### Pitfall 13: Claiming Renode lacks STM32 support

**What goes wrong:** "Renode has no STM32" is false (F103 Blue Pill, F4/F7 Discovery,
Nucleo-64 and many `.repl` platforms exist).
**How to avoid:** The defensible reason is: the course's STM32 board model is unconfirmed,
the repository has no STM32 homework or board profile, and Renode is not installed.

### Pitfall 14: Docker is unreachable in the sandbox

**What goes wrong:** A plan task that runs `docker run` in the sandbox fails with a socket
permission error that looks like a broken install.
**How to avoid:** Make the Velxio step a `checkpoint:human-action` (D-06).

## Code Examples

### Scenario validation without a token (verified this session)

```sh
cd /Users/vloktiev/Dev/miltech/homeworks
printf 'name: t\nversion: 1\nauthor: x\nsteps:\n  - bogus: 1\n' > /tmp/p.yaml
WOKWI_CLI_TOKEN=dummy wokwi-cli homeworks/1_3-police-flasher \
  --scenario /tmp/p.yaml --diagram-file assets/diagram.json
# stderr: Error: Invalid scenario step key: bogus        (exit 1)
```

This proves step-key validation runs **before** the WebSocket connection, which is what makes
D-07 closable without quota.

### Path-resolution probe (verified this session)

```sh
# positive: paths resolve, connection fails
: > "$TMPDIR/fixture.elf"
WOKWI_CLI_TOKEN=dummy WOKWI_CLI_SERVER=ws://127.0.0.1:1 \
  wokwi-cli homeworks/1_3-police-flasher \
    --elf "$TMPDIR/fixture.elf" --scenario scenario.yaml \
    --diagram-file assets/diagram.json --timeout 15000
# -> "Error connecting to ws://127.0.0.1:1: connect <EPERM|ECONNREFUSED>"   (exit 1)

# negative: repo-root option values double-join
WOKWI_CLI_TOKEN=dummy WOKWI_CLI_SERVER=ws://127.0.0.1:1 \
  wokwi-cli homeworks/1_3-police-flasher \
    --scenario homeworks/1_3-police-flasher/scenario.yaml \
    --diagram-file homeworks/1_3-police-flasher/assets/diagram.json
# -> "Error: diagram.json not found in <…>/homeworks/1_3-police-flasher/homeworks/1_3-police-flasher/assets/diagram.json"
```

Notes that make the test robust:
- `--elf` sets both the firmware and the ELF path, so the probe needs **no build artifact**
  and stays deterministic on a clean checkout. The trade-off is that it does not exercise
  `wokwi.toml`'s firmware path; that path is covered by the build + run itself.
- Assert on `"Error connecting to"` plus the override URL, **not** on the errno: inside a
  sandbox the error is `EPERM`, outside it is `ECONNREFUSED`.
- `WOKWI_CLI_SERVER` is undocumented; it exists at `constants.ts`
  (`process.env.WOKWI_CLI_SERVER ?? 'wss://wokwi.com/api/ws/beta'`). If a future CLI drops
  it, the test fails loudly — acceptable, and better than a network dependency.

### Merge-script command assembly (target shape for the promoted file)

```python
# scripts/pio/merge_firmware.py — SCons-injected globals guarded for import.
try:
    Import("env")  # noqa: F821 — provided by PlatformIO/SCons
except NameError:
    env = None

def build_merge_command(env, esptool, build_dir, target_path):
    """Return argv for esptool merge-bin; pure, so the test needs no SCons."""
    images = [(off, env.subst(path)) for off, path in env.get("FLASH_EXTRA_IMAGES", [])]
    images.append((env.subst("$ESP32_APP_OFFSET"), str(target_path)))
    argv = [esptool, "--chip", env.BoardConfig().get("build.mcu", "esp32"), "merge-bin",
            "-o", join(build_dir, "firmware.merged.bin"),
            "--flash-mode", env.BoardConfig().get("build.flash_mode", "dio"),
            "--flash-size", env.BoardConfig().get("upload.flash_size", "4MB")]
    for offset, path in images:
        argv += [offset if isinstance(offset, str) else hex(offset), path]
    return argv

if env is not None:
    # Guard the package at load time: a missing name fails fast, before a long compile.
    if "tool-esptool" not in env.PioPlatform().packages:
        raise SystemExit("merge_firmware: platform has no `tool-esptool` package …")
    env.AddPostAction("$BUILD_DIR/${PROGNAME}.bin", merge_firmware)
```

`env.PioPlatform().packages` is a plain dict
`[VERIFIED: ~/.platformio/penv/lib/python3.13/site-packages/platformio/platform/_packages.py:18-37]`,
and `GetExtraScripts` resolves relative entries under `fs.cd($PROJECT_DIR)`
`[VERIFIED: ~/.platformio/penv/lib/python3.13/site-packages/platformio/builder/tools/piomisc.py:132-142]`,
which is why `post:../../scripts/pio/merge_firmware.py` survives `pio run -d <project>`.

### Verified repository values (quoted from the files)

```json
// homeworks/1_3-police-flasher/assets/diagram.json:11-15
"attrs": {
  "flashSize": "16",
  "psramType": "octal",
  "psramSize": "8"
}
```

```toml
# homeworks/1_3-police-flasher/wokwi.toml:1-4
[wokwi]
version = 1
firmware = ".pio/build/esp32s3_arduino/firmware.merged.bin"
elf = ".pio/build/esp32s3_arduino/firmware.elf"
```

```yaml
# homeworks/1_3-police-flasher/scenario.yaml:1-12
name: Police flasher smoke
version: 1
author: VLoktiev-EMB
steps:
  - wait-serial: "pattern ready"
  - delay: 100ms
  - expect-pin:
      part-id: esp
      name: 4
      value: 1
```

```json
// schema/homework.schema.json:57-68
"simulation": {
  "type": "object",
  "additionalProperties": false,
  "required": ["tool", "status"],
  "properties": {
    "tool": { "enum": ["wokwi", "velxio", "renode", "fritzing", "none"] },
    "diagram": { ... },
    "status": { "enum": ["none", "pending", "verified"] }
  }
}
```

So: the diagram's flash/PSRAM settings live in `diagram.json` attrs (not `wokwi.toml`), the
scenario shape is current, and `verified` is already a legal status — D-10 needs no schema
change.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `expect-pin: {pin, value}` | `expect-pin: {name, value}` (`pin` deprecated alias) | Before 0.28.1 | The repo is already current; the docs are not. |
| `set-control: {control, value}` | `set-control: {name, value}` (`control` alias) | Before 0.28.1 | Same. |
| `tool-esptoolpy` + `merge_bin --flash_mode/--flash_size` | `tool-esptool` + `merge-bin --flash-mode/--flash-size` | espressif32 8.0.0 / esptool 5 | The published Wokwi PlatformIO script cannot run unchanged (F-09). |
| Wokwi CLI 0.25–0.28 scenario commands | 0.29.x adds heap monitoring only | 2026-10-23 (v0.29.1) | No scenario-shape change; 0.28.1 remains valid. |
| Velxio "self-host everything" | Self-host = AVR/RP2040/ESP32 only | Current README (2026-10-24) | STM32 is not evidence-able from the cheap path. |

**Deprecated/outdated:**
- The Wokwi docs' `expect-pin` example (`pin`/`expected`) — superseded by the CLI source.
- The Wokwi docs' supported-microcontroller list omits `board-esp32-s3-devkitc-1`, which is
  why lint emits an `[unsupported-part]` info note. The part works; the list is stale.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The rolling quota counts **simulated** time, so `--timeout 15000` bounds a run's cost at 0.25 min. | Measurement Protocol | If quota is wall-clock, cost rises by handshake + upload time (the 6.4 MB ELF dominates); the 50-min budget still holds for three runs, but the CI formula's unit changes. |
| A2 | Compile and `lint` consume no quota because no simulation session is opened. | Standard Stack | The billing consequence is inferred, not documented; the vendor could count sessions differently. |
| A3 | The CI dashboard exposes a before/after figure precise enough to derive a per-run delta. | Measurement Protocol | If granularity is whole minutes, per-run deltas are unreadable; fall back to the timeout bound labelled `calculated`. |
| A4 | The Velxio self-hosted editor cannot load a PlatformIO project, so pilot compile/serial may be unreachable. | Measurement Protocol Step 3 | If it can, the phase gains a real second measurement; if not, the ADR records `not measured` with the exact reason. |
| A5 | The Fritzing FAQ restriction ("do not allow the use of Fritzing part graphics in other software systems") is current. | Fritzing role | The page returned HTTP 403; the text is quoted from a search summary, not read directly. The repository rule (no part graphics in assets/docs) is conservative and safe either way. |
| A6 | The course's STM32 board model is unknown. | Renode role | If a model is confirmed later, the Renode row is revisitable (v2). |
| A7 | `--vcd-file` yields a usable simulated end timestamp. | Open Question 3 | If not, the simulated-minutes row is a bound, not a measurement. |
| A8 | The free plan still offers 50 min / 5 min as documented. | Standard Stack | Vendor tiers have changed before (pricing vs docs); check the dashboard before the run. |

## Open Questions

1. **Does the report need a one-line amendment when `simulation.status` flips?**
   - What we know: `homeworks/1_3-police-flasher/report.md:284-286` says "the scenario has
     not been executed … Phase 7 owns the execution"; `report.md:417` says "The evidence
     does not support any claim about … the simulator."
   - What's unclear: whether a dated report snapshot may stand unamended while the metadata
     says `verified`.
   - Recommendation: add one sentence in §7/§9 pointing at `07-SPIKE-EVIDENCE.md` and
     ADR-0014 in the same commit as the status flip. It is a correction of a present-tense
     falsehood, not the README expansion D-15 defers.

2. **Does `homeworks/1_3-police-flasher/README.md` need the same correction?**
   - Lines 44-45 say the run is deferred and the status stays `pending`.
   - Recommendation: replace those two lines with a pointer to the evidence file; keep the
     command block unchanged. Still not the Phase 11 expansion.

3. **Is a VCD or a screenshot worth the extra moving parts on scarce runs?**
   - VCD gives the simulated end time and pin transitions; a screenshot gives visual LED
     evidence but needs `--screenshot-part` and `--screenshot-time ≤ timeout`.
   - Recommendation: request the VCD on run 1 only; skip screenshots unless the pin
     assertion fails and a visual is needed for diagnosis.

4. **Which `PRs_per_month` should the cost basis assume?**
   - Recommendation: state one figure explicitly (e.g. 20) and show sensitivity at 5 and 50;
     never present the result as measured.

5. **Should the CLI version be pinned in documentation?**
   - Recommendation: record `wokwi-cli 0.28.1 (7cf4ffaebfd8)` in the evidence and the
     homework README; a full pin in the repository would need an install step, which is
     Phase 8's territory.

6. **How deep should the Velxio attempt go?**
   - Recommendation: boot + digest + board-list observation, then stop and record
     `not measured` for pilot compile/serial unless the UI genuinely loads the project.
     Do not port the homework to a sketch to make Velxio look measured.

7. **Does the ADR need to name the AVR/ESP-IDF/RP2040/STM32 roles even though only ESP32-S3
   was measured?**
   - Recommendation: yes — SC5 asks which simulator serves each platform. Label the
     unmeasured rows `not measured` and cite the vendor board matrices.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| `wokwi-cli` | Scenario run, lint, path test | ✓ | 0.28.1 (`7cf4ffaebfd8`) | — |
| `WOKWI_CLI_TOKEN` | Executed run | ✗ in this session (owner has one) | — | Owner-run outside sandbox; protocol B if unavailable |
| Outbound `wss://wokwi.com` | Executed run | ✗ (sandbox DNS blocked) | — | Owner-run; path check uses `WOKWI_CLI_SERVER` locally |
| PlatformIO Core | Build + merge | ✓ | 6.2.0 | — |
| `tool-esptool` (esptool) | Merge | ✓ | 5.4.0 | — |
| Docker daemon | Velxio self-host | ✗ inside sandbox (`/var/run/docker.sock` permission denied) | client 29.9.2 | Owner-run outside sandbox (D-06) |
| `docker` CLI | Velxio self-host | ✓ | 29.9.2 | — |
| `renode` | Renode measurement | ✗ | — | `not measured` (deferred to v2) |
| Fritzing | Illustration | ✗ | — | `not measured` (not produced this phase) |
| `uv` | Generator check, tests | ✓ | 0.13.5 | — |
| Python 3 | Tests, wrapper | ✓ | 3.13.13 | — |

**Missing dependencies with no fallback:**
- The Wokwi token and outbound `wss://wokwi.com` — the executed run cannot happen inside the
  sandbox. This is by design; the phase must include an owner-run checkpoint.

**Missing dependencies with fallback:**
- Docker daemon — owner-run outside the sandbox; if still unavailable, record
  `not measured` with the exact reason.
- Renode and Fritzing — `not measured` with reasons, which SC1 permits.

## Validation Architecture

`workflow.nyquist_validation` is `true` in `.planning/config.json`.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Python `unittest` (stdlib), 366 tests |
| Config file | none — discovery via `scripts/tests/` |
| Quick run command | `python3 -m unittest scripts.tests.test_simulation_paths scripts.tests.test_merge_firmware -v` (targeted; ~2 s) |
| Full suite command | `UV_CACHE_DIR="$TMPDIR/uvcache" python3 -m unittest discover -s scripts/tests -t .` (37 s, 366 tests) |

Sandbox note: the suite fails 76 tests inside the command sandbox unless `UV_CACHE_DIR`
points at a writable directory (verified: `uv` cannot create `~/.cache/uv/.tmp*`). Outside
the sandbox the plain command works. Use the `UV_CACHE_DIR` form in any agent-run gate.

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SIM-02 | Documented command resolves `--diagram-file` and `--scenario` relative to the positional project dir | unit (subprocess) | `python3 -m unittest scripts.tests.test_simulation_paths -v` | ❌ Wave 0 |
| SIM-02 | A repo-root option value is rejected (negative control, non-vacuity) | unit (subprocess) | same module | ❌ Wave 0 |
| SIM-02 | Promoted merge script builds `merge-bin` argv with the right offsets/quoting and a clear failure when `tool-esptool` is absent | unit (pure function) | `python3 -m unittest scripts.tests.test_merge_firmware -v` | ❌ Wave 0 |
| SIM-02 | `wokwi-cli lint --offline` exits 0 on the canonical diagram | manual / CI (Phase 8) | `wokwi-cli lint --offline homeworks/1_3-police-flasher/assets/diagram.json` | ✅ command exists; not yet in a test |
| SIM-02 | Measured cold/warm/serial/quota evidence recorded | manual-only | owner-run protocol; review of `07-SPIKE-EVIDENCE.md` | ❌ (not automatable without quota) |
| SIM-02 | ADR-0014 exists, is in the decisions table, and appears in the generated nav | unit (existing) | `python3 -m unittest scripts.tests.test_docs_pins.PinConsistencyTests.test_nav_lists_every_markdown_file_under_docs` | ✅ existing test, new input |
| SIM-02 | Generated views are in sync after the status flip | manual | `UV_CACHE_DIR="$TMPDIR/uvcache" uv run scripts/gen_views.py --all --check` | ✅ command exists |
| SIM-03 | No Fritzing artifact is copied into assets/docs | manual-only | review: no new files under `docs/assets/` or `homeworks/*/assets/` | — (no artifact produced) |

**Manual-only justification:** the executed session is token-gated and quota-metered; no
automated test can run it without consuming the owner's quota on every suite run. The
evidence file is the artefact a reviewer checks, exactly as the repo treats bench
measurements.

### Sampling Rate

- **Per task commit:** the targeted modules plus `uv run scripts/gen_views.py --all --check`
- **Per wave merge:** the full suite (366 tests) plus `pre-commit run --all-files`
- **Phase gate:** full suite green, `gen-views-check` green, `wokwi-cli lint` exit 0, and the
  evidence file complete before `/gsd-verify-work`

### Wave 0 Gaps

- [ ] `scripts/tests/test_simulation_paths.py` — covers the F-19 positive/negative/
      non-vacuity cases; skips with `shutil.which("wokwi-cli") is None` (repo convention).
- [ ] `scripts/tests/test_merge_firmware.py` — imports the promoted module with a stub
      `env`; asserts argv order, `-o` target, quoting, and the missing-package message.
- [ ] `scripts/pio/merge_firmware.py` — the promoted file (Wave 0 because both the build and
      the tests consume it).
- [ ] `pyproject.toml` — remove the now-dead `homeworks/*/merge_firmware.py` F821 ignore.

## Security Domain

`security_enforcement` is `true` (ASVS level 1).

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | Yes | `WOKWI_CLI_TOKEN` from the environment only; never a file, argument, or logged command line. `read -rs` at the prompt; no `set -x`. |
| V3 Session Management | No | No session or cookie is managed by this repository. |
| V4 Access Control | No | Nothing is served; the sandbox boundary is the control. |
| V5 Input Validation | Yes | The scenario YAML and `diagram.json` are parsed by a third-party CLI; the CLI validates step keys, delay units, and diagram structure before connecting. Repository-authored inputs are reviewed, not user-supplied. |
| V6 Cryptography | Yes | TLS to `wss://wokwi.com` is the vendor's; never hand-rolled. No repository crypto. |
| V14 Configuration | Yes | Secrets stay outside the repo (`gitleaks` has no Wokwi-specific rule; discipline + pre-commit scan); the Docker image tag is mutable, so the digest is recorded. |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Token leak into shell history or a transcript | Information disclosure | `read -rs`; no `set -x`; never echo; evidence records only "value not recorded". |
| Token committed to the repository | Information disclosure | `gitleaks` pre-commit and full-history CI; a leaked token is rotated first, never scrubbed by history rewrite. |
| Supply-chain: `curl \| sh` CLI installer | Tampering | Pin the version argument; record version + short SHA; the repository already pins toolchains. |
| Supply-chain: mutable container tag | Tampering | Record `RepoDigests`; optionally pull by digest. |
| Malicious or malformed `diagram.json`/`scenario.yaml` | Tampering / DoS | Lint offline before execution; the inputs are repository-reviewed in the same PR. |
| AGPL contamination from Velxio | Legal, not STRIDE | Reference the image only; never vendor Velxio code into this MIT repository. |
| Simulator output presented as hardware evidence | Repudiation / integrity | Five-label vocabulary; `simulated` distinct from `measured`; PITFALLS C10. |

## Sources

### Primary (HIGH confidence)

- Installed binaries, run this session: `wokwi-cli 0.28.1 (7cf4ffaebfd8)`, `pio 6.2.0`,
  `esptool v5.4.0`, Docker client `29.9.2`, Python `3.13.13`, `uv 0.13.5`.
- `github.com/wokwi/wokwi-cli` at commit `7cf4ffaebf` (= tag `v0.28.1`):
  `packages/cli/src/commands/simulate.ts`, `TestScenario.ts`,
  `scenario/ExpectPinCommand.ts`, `scenario/SetControlCommand.ts`,
  `scenario/DelayCommand.ts`, `scenario/WaitSerialCommand.ts`, `utils/parseTime.ts`,
  `utils/token.ts`, `constants.ts`, `config.ts`, `WokwiConfig.ts`, `lint/index.ts`.
- Local source reads: `~/.platformio/…/platformio/platform/_packages.py:18-37`,
  `…/builder/tools/piomisc.py:132-142`, `…/builder/main.py:155-189`.
- Repository reads: `schema/homework.schema.json:57-68`,
  `scripts/gen_views.py:1063-1084,1108-1157`,
  `homeworks/1_3-police-flasher/{wokwi.toml,scenario.yaml,platformio.ini,README.md,report.md}`,
  `platformio.shared.ini`, `docs/decisions/README.md`, `generated.manifest`,
  `docs/homeworks/1_3-police-flasher.md`, `pyproject.toml`, `mkdocs.yml`.
- Runtime probes: local lint (exit 0, 1 info), scenario step-key validation, doubled-path
  rejection, `WOKWI_CLI_SERVER` probe, incremental build (0.54 s reported), 366-test suite.

### Secondary (MEDIUM confidence)

- `docs.wokwi.com/wokwi-ci/getting-started` — rolling quota, per-session caps.
- `docs.wokwi.com/wokwi-ci/cli-usage` — options, `--timeout` milliseconds, exit code 42.
- `docs.wokwi.com/guides/esp32` — flash/PSRAM attrs, CPU cap, limitation list.
- `docs.wokwi.com/wokwi-ci/automation-scenarios` — alpha status (schema itself is stale).
- `github.com/davidmonterocrespo24/velxio` README — image, port, boards, licence, volumes.
- `github.com/fritzing/fritzing-app` README — attribution and ShareAlike text.
- `renode.readthedocs.io` supported boards — STM32 platform list.

### Tertiary (LOW confidence)

- `fritzing.org/faq/` — the part-graphics restriction (page returned 403; the text is quoted
  from a search summary and should be re-checked before it is used as a licence opinion).
- The research-store cache write was **blocked** by the command sandbox
  (`~/.gsd/research-cache/` is outside the write allowlist); the digests are therefore
  carried in this file and not persisted to the seam's cache.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — every version was read from the installed tool or registry.
- Scenario/config schema: HIGH — read from the CLI source at the exact installed commit and
  confirmed by local probes.
- Measurement protocol: MEDIUM — the mechanism is verified; the quota unit rests on vendor
  docs plus an inference (A1).
- Velxio: MEDIUM — vendor README is explicit; feasibility of loading this project is
  untested (A4).
- Renode/Fritzing role: MEDIUM — vendor facts verified; the course's STM32 model is unknown.
- Pitfalls: HIGH — most were reproduced locally this session.

**Research date:** 2026-10-26
**Valid until:** 2026-11-25 (30 days; re-check the Wokwi quota wording and CLI version
before the run if it slips past that).

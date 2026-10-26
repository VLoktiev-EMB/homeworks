---
status: accepted
date: 2026-10-26
decision-makers: [VLoktiev-EMB]
consulted: []
informed: []
---
# Simulator selection and the platform-role matrix

## Context and Problem Statement

The repository ships an ESP32-S3 Arduino homework with a Wokwi `diagram.json` and a
`scenario.yaml`, but until Phase 7 it had never executed that scenario: the Wokwi CLI is
token-gated and the token was absent, so only `wokwi-cli lint --offline` had run. A simulator
decision built on vendor documentation alone would repeat that gap at a larger scale. Phase 7
therefore ran a bounded spike and recorded every command, duration, serial observation and quota
figure in `.planning/phases/07-simulation-spike/07-SPIKE-EVIDENCE.md`.

The question is which simulator serves each platform this course uses, at what measured cost,
inside which fidelity limits, and behind which licence boundary. A tool that cannot run a
PlatformIO project must be labelled as such rather than described by its board catalogue, and a
value that was never observed must stay `not measured` with its reason.

## Decision Drivers

* Evidence depth is role-proportional: the primary tool is executed, the fallback is attempted,
  and a tool that serves only a deferred platform carries a reason instead of a number.
* The Wokwi free plan is scarce: a rolling 30-day quota of about 50 simulated minutes and a
  5-minute session cap (`datasheet`), so the protocol must fit in seconds, not minutes.
* The CI cost basis must be arithmetic over labelled inputs, not a claim of a CI run; a real CI
  simulation run is Phase 8 work.
* Fidelity limits decide what the simulation may be cited for: pin timing and logic are usable,
  and electrical quantities are not.
* The repository is MIT and public, so an AGPLv3 fallback may be referenced but never vendored.
* A reader must be able to re-derive every conclusion from the evidence file without trusting a
  summary.

## Considered Options

* Wokwi as the primary executed simulator, Velxio as the self-hosted fallback, Renode reserved
  for the STM32 role, and Fritzing for illustration only.
* Wokwi only, with no fallback and no STM32 path.
* Velxio self-hosted as the primary simulator.
* Renode as the primary simulator.
* No simulation at all, hardware bench only.

## Decision Outcome

Chosen option: "Wokwi as the primary executed simulator, Velxio as the self-hosted fallback,
Renode for the STM32 role, and Fritzing for illustration only", because Wokwi is the only tool
that executed the real PlatformIO project end to end, Velxio booted reproducibly without
consuming Wokwi quota and is the cheapest second real measurement, and the remaining two tools
are named honestly at the depth the evidence supports.

The platform-role matrix is the primary artefact of this record. One row per tool names its
role, the platforms it serves, and the evidence depth behind the row.

| Tool | Role | Platforms | Evidence depth |
|------|------|-----------|----------------|
| Wokwi | Primary executed simulator | ESP32 and ESP32-S3 | Three runs of the police-flasher scenario, each exit 0 with exactly one `I pattern ready` serial line (3/3); simulator cold `3.759 s` and simulator warm `6.753 s` and `11.238 s`, all `measured`; session wall clock `5.815 s`, `8.559 s` and `12.701 s`, `measured`; simulated minutes `calculated (upper bound)` `15 s` per run and `45 s` cumulative; 3 runs of quota consumed. |
| Velxio | Self-hosted fallback | AVR, RP2040 and the ESP32 family, including ESP32-S3 | Boot readiness `16.988 s` `measured` from the digest-pinned image; simulator catalogue `47` boards observed, including ESP32-S3 and STM32 boards, while the vendor page states `19` boards `datasheet`; the arduino-cli compile backend lists `182` FQBNs as a separate surface; pilot compile and serial `not measured — the self-hosted editor does not consume a PlatformIO project`; no Wokwi quota consumed. |
| Renode | STM32 role | STM32 | `not measured` — the course board model is unconfirmed, the repository holds no STM32 homework and no STM32 board profile, and Renode is not installed on the measurement machine. The row is revisitable in v2. |
| Fritzing | Illustration only | none claimed | `not measured` — Fritzing is not a simulator; it is an illustration tool, and this phase produced no Fritzing artifact. |

### Cold and warm start

The terms are defined rather than assumed, because a bare "cold start" conflates three
different quantities:

* **Build cold** is `pio run` after `pio run -t clean`, with the toolchain packages already
  installed.
* **Build warm** is `pio run` after touching `src/main.cpp`.
* **Simulator cold** is process spawn to the first serial byte on the first invocation in a
  measurement session.
* **Simulator warm** is the same interval on a subsequent invocation in the same session.

There is no local CLI cache to clear: the Wokwi CLI holds the board bundle in memory and never
writes it to disk. "Cold" therefore means the first connection in a session, not an empty cache,
and no speed claim is attached to "warm". The two measured warm intervals are longer than the
cold one because the wait before `Starting simulation...` dominates the interval, not because
of a cache effect.

### Measured cost of the executed simulator

Every value below is carried from the evidence file in the form its label supports.

| Quantity | Value | Label |
|----------|-------|-------|
| Build cold, median of three repeats | `8.13 s` | `measured` |
| Build warm, median of three repeats | `0.49 s` | `measured` |
| Simulator cold, first invocation | `3.759 s` | `measured` |
| Simulator warm, subsequent invocations | `6.753 s` and `11.238 s`, both recorded, no mean | `measured` |
| Session duration, wall clock | `5.815 s`, `8.559 s`, `12.701 s` | `measured` |
| Serial reliability | `3/3` runs observed the expected `pattern ready` line | `measured` |
| Simulated minutes per run | `15 s` | `calculated (upper bound)` from `--timeout 15000`; the dashboard delta was not supplied |
| Cumulative quota for the spike | 3 runs, `45 s` upper bound | `calculated (upper bound)` |
| Offline diagram lint | exit 0, `Found 1 info` | `measured` |

Serial reliability is an observation with an exact count, never a percentage: every counted run
exited 0 and its captured stream carried one `pattern ready` line. Protocol B, had it been used,
would have recorded the smaller count and labelled serial reliability `not measured`.

### Calculated CI cost basis

The cost basis is arithmetic over labelled inputs. It is labelled `calculated`, and it is not a
measured CI run:

```text
quota_minutes_per_30d =
    session_minutes_per_run × changed_projects_per_PR × runs_per_PR × PRs_per_month
```

| Input | Value | Label |
|-------|-------|-------|
| `session_minutes_per_run` | `0.25 min` (`15 s`) | `calculated (upper bound)`, carried from the per-run timeout bound |
| `changed_projects_per_PR` | `1` | `calculated` — `scripts/affected.py` selects the changed homework project; one project for a single-homework change |
| `runs_per_PR` | `1` | `calculated` — one scenario per project |
| `PRs_per_month` | `20` | stated assumption, not measured |
| Published free quota | `50 min` rolling 30 days, `5 min` session cap | `datasheet` |

At `PRs_per_month = 20` the worked example is
`0.25 min × 1 × 1 × 20 = 5.0 min per 30 days`, about `10 %` of the free quota. Sensitivity is
shown at `5 PRs per month` (`1.25 min`, about `2.5 %`) and at `50 PRs per month`
(`12.5 min`, about `25 %`). The `calculated (upper bound)` qualifier on the session duration
propagates into every figure here.

The session-cap check is separate and is satisfied: the measured wall clock of `5.815 s` to
`12.701 s` sits well under the `5 min` cap (`datasheet`). A real CI simulation run is Phase 8
work and is not claimed in this record.

### Fidelity limits

Verified vendor limits for the ESP32 family: Bluetooth is not implemented; I2C is master-only
with no 10-bit addressing; I2S is partial on ESP32 and absent on ESP32-S3; MCPWM is not
implemented; the RTC exposes only pull-up and pull-down resistors; ULP is not implemented; and
the default CPU frequency is about `8 MHz`, overridable through `cpuFrequency`, which affects
instruction timing and not peripheral timing.

The pilot adds five limits of its own:

* The all-off frame drives GPIO4 to a high-impedance input, so node X floats; "both LEDs dark"
  is a simulation-only approximation and the off-state node voltage stays `not measured`.
* The anti-parallel pair lights only the HIGH-side LED in `PATTERN_MODE_SOLID`.
* No electrical claim — current, brightness, or forward voltage — is supported by simulation.
* `board-esp32-s3-devkitc-1` is reported by lint as an undocumented part type, a maintenance
  risk if the part definition changes or is removed.
* The scenario API is alpha and may change between CLI releases.

### Licence boundary

Fritzing SVGs may appear in a report with attribution, and Fritzing part graphics are never
copied into `docs/assets/`, `homeworks/*/assets/`, or any other shared asset path.
`homeworks/1_3-police-flasher/assets/diagram.json` remains the single source of truth for the
wiring, and no Fritzing artifact is produced in this phase. The Fritzing FAQ restriction was
read from a search summary because the page returned HTTP 403; the repository rule above is
conservative and holds whether or not the quoted wording is exact.

The Velxio image is AGPLv3 and is referenced only, by its immutable digest: no Velxio source,
image layer, part graphic, or other asset is vendored into this MIT repository.

### Consequences

* Good, because the primary simulator was executed on the real project, so the timing and logic
  claims rest on observed output rather than vendor documentation.
* Good, because a second tool was measured at no Wokwi quota cost, so a fallback exists with a
  measured boot and an honest list of what it cannot run.
* Good, because every unmeasured row carries its reason, which keeps the record revisitable
  instead of silently incomplete.
* Bad, because the free-plan quota is a hard ceiling: three runs consumed `45 s` of a
  `50 min` window, and a larger matrix would exhaust the budget.
* Bad, because the pilot cannot be compiled in Velxio without porting it to a sketch, so the
  fallback's compile and serial depth stay `not measured`.
* Neutral, because the STM32 row is deferred to v2 and the course board model is still
  unconfirmed.

### Confirmation

* `python3 -m unittest scripts.tests.test_simulation_paths -v` proves the documented Wokwi
  command resolves its diagram and scenario paths without a real token.
* `python3 -m unittest scripts.tests.test_merge_firmware -v` proves the shared merge action
  produces the merged image the scenario flashes.
* `wokwi-cli lint --offline homeworks/1_3-police-flasher/assets/diagram.json` exits 0.
* `uv run scripts/gen_views.py --all --check` proves the committed generated views agree with
  the metadata this record depends on.
* Every raw command, duration, serial observation and quota row is re-readable in
  `.planning/phases/07-simulation-spike/07-SPIKE-EVIDENCE.md`.

## Pros and Cons of the Options

### Wokwi primary, Velxio fallback, Renode for STM32, Fritzing for illustration

Run the pilot on Wokwi, keep a quota-free self-hosted second opinion, and name the remaining
tools at the depth the evidence supports.

* Good, because the primary claim is backed by an executed scenario of the real project.
* Good, because the fallback costs no Wokwi quota and its boot is digest-pinned and repeatable.
* Good, because the role matrix makes each platform's coverage explicit instead of implying
  equal depth.
* Neutral, because the free-plan quota still bounds how often the primary path can run.
* Bad, because four rows mean four sets of limits to keep current.

### Wokwi only

Use one simulator and skip the fallback and the STM32 row.

* Good, because there is one toolchain to learn and one quota to watch.
* Bad, because a token or quota failure leaves no measured alternative.
* Bad, because the STM32 question would have no named owner or reason.
* Bad, because the record would overstate Wokwi's coverage of platforms it has not run.

### Velxio self-hosted as primary

Run everything in the self-hosted browser editor.

* Good, because it costs no Wokwi quota and needs no external token.
* Bad, because the editor does not consume a PlatformIO project, so the pilot cannot be
  compiled there without a port.
* Bad, because the image is AGPLv3, which constrains any deeper integration with an MIT
  repository.
* Neutral, because its board catalogue is broader than the executed evidence.

### Renode as primary

Use Renode for the simulated target.

* Good, because it is an open-source instruction-level simulator.
* Bad, because the course STM32 model is unconfirmed and the repository has no STM32 homework
  or board profile to run.
* Bad, because it is not installed on the measurement machine, so no measurement exists.
* Bad, because the ESP32-S3 pilot is not the platform Renode would serve.

### No simulation at all

Rely on the bench only.

* Good, because it removes a quota and a token dependency.
* Bad, because it would discard the executed evidence this phase produced.
* Bad, because CI would have no simulation path at all for Phase 8 to build on.
* Bad, because the report would keep its earlier, now stale, simulation claims.

## More Information

The raw record is `.planning/phases/07-simulation-spike/07-SPIKE-EVIDENCE.md`: it carries the
label vocabulary, the exact commands, the per-run table, the quota ledger, the Velxio self-host
record, and the `**Outcome:** scenario passed` handoff this decision relies on. It is cited as a
code span because it lives outside `docs/` and a relative Markdown link would not resolve in the
generated site.

The metadata contract keeps its existing `simulation` block, unchanged
([0009](0009-homework-metadata-contract.md)): `verified` means an executed run with evidence and
`pending` otherwise. The lint-versus-executed distinction lives in the evidence file and this
record, not in the schema.

Vendor references: Wokwi's ESP32 guide for the fidelity limits
(<https://docs.wokwi.com/guides/esp32>), the scenario API note
(<https://docs.wokwi.com/wokwi-ci/automation-scenarios>), and the Velxio image
(<https://github.com/davidmonterocrespo24/velxio>). The homework report points at this record
and at the evidence file from its simulation statements.

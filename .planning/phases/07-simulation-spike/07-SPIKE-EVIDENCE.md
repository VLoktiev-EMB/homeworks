# Phase 7 Spike Evidence — Simulator Selection

This document is the raw measurement record for Phase 7 (SIM-02). It serves the decision
recorded in `docs/decisions/0014-simulator-selection.md`: the ADR carries the conclusion and
the per-platform role matrix, while every command, duration, serial observation and quota
figure stays here so a reviewer can re-derive the conclusion without trusting a summary.
Nothing in this file is a bench measurement unless it carries the `measured` label and names
the instrument that produced it.

## How to read this record

Every value carries exactly one label from the fixed vocabulary:

| Label | Meaning |
|-------|---------|
| `measured` | Read from a real execution on this machine in this session, with the command named. |
| `calculated` | Derived arithmetically from labelled inputs; the formula is stated. |
| `simulated` | Produced by the hosted simulator; it is simulation evidence, never bench evidence. |
| `datasheet` | Quoted from vendor documentation or a published specification. |
| `not measured` | Deliberately absent, with the exact reason. |
| `calculated (upper bound)` | A bound derived from `--timeout 15000`, not an observed consumption. |

Two quantities are never substituted for one another: **wall-clock seconds are not simulated
minutes**. Wall clock is the process lifetime; simulated minutes are the quota unit the vendor
meters, bounded per run by `--timeout 15000`.

**Token discipline (D-02):** token supplied by the repository owner; value not recorded. That
sentence is the only token statement permitted anywhere in this repository. The only token
assignment that may appear in tracked source is the literal `dummy`.

**Evidence-depth rule (D-05):** depth is role-proportional. Wokwi is executed; Velxio is a
self-host attempt; Renode and Fritzing are `not measured` with reasons carried in the ADR.

## Owner-run protocol (Wokwi)

The command sandbox blocks outbound `wss://wokwi.com` and the token must never enter the
repository, a command line, or the transcript. The repository owner therefore runs every
session in a terminal outside the command sandbox. The agent never asks for, receives, or
writes the token value.

Run these steps in order, once per measurement session.

### 1. Materialise the timestamp wrapper

The nine-line wrapper stamps every CLI output line with a monotonic offset, so
`Connected to Wokwi Simulation API` and `Starting simulation...` become timestamps. It is a
one-off inline tool, not a committed artifact (D-14 forbids a gate).

```sh
cat > "$HOME/wokwi-stamp.py" <<'PY'
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
PY
shasum -a 256 "$HOME/wokwi-stamp.py"
```

Record the `shasum -a 256` output beside the run so the wrapper that produced the numbers is
identifiable.

### 2. Supply the token silently

```sh
cd /Users/vloktiev/Dev/miltech/homeworks
read -rs WOKWI_CLI_TOKEN && export WOKWI_CLI_TOKEN
```

`read -rs` echoes nothing and does not enter shell history. Never run `set -x` in this shell.
If the token becomes visible in any output, stop and rotate it before continuing.

### 3. Run the session

Run 1 (cold) only carries `--vcd-file`; runs 2 and 3 never do.

```sh
python3 -u "$HOME/wokwi-stamp.py" wokwi-cli homeworks/1_3-police-flasher \
  --scenario scenario.yaml --diagram-file assets/diagram.json \
  --timeout 15000 --serial-log-file "$HOME/wokwi-run1.serial.log" \
  --vcd-file "$HOME/wokwi-run1.vcd" \
  > "$HOME/wokwi-run1.log" 2>&1
echo "exit=$?"
```

Runs 2 and 3 use the identical command with the run number changed and no `--vcd-file`:

```sh
python3 -u "$HOME/wokwi-stamp.py" wokwi-cli homeworks/1_3-police-flasher \
  --scenario scenario.yaml --diagram-file assets/diagram.json \
  --timeout 15000 --serial-log-file "$HOME/wokwi-run<N>.serial.log" \
  > "$HOME/wokwi-run<N>.log" 2>&1
echo "exit=$?"
```

**Do not pipe the output into `tee`.** zsh without `pipefail` reports the last pipeline
element's status, which would hide the CLI's exit code. Redirect both streams to the capture
file and read `echo "exit=$?"` from the wrapper invocation itself.

**Never pass `--quiet` or `--interactive` on a measurement run.** `--quiet` suppresses the two
lines the wrapper exists to timestamp, and `--interactive` turns a bounded run into a manual
session.

### 4. Exit-code mapping

| Exit | Meaning |
|------|---------|
| 0 | scenario completed; every step passed (`measured`) |
| 42 | `--timeout` reached (`measured`, timeout) |
| 1 | token, config, path, firmware, scenario-validation, or assertion failure (`measured`, failure) — read the first error line |

### 5. Fixed capture

Strip ANSI sequences (`FORCE_COLOR` may be set in some shells) and paste back exactly:
(1) the full stamped output; (2) the `exit=` value; (3) the serial log contents; (4) the
dashboard usage figure before and after the run; (5) the VCD path and its last timestamp when
the file exists.

## Velxio protocol

Filled by Plan 03. Do not run it here. Docker is unreachable inside the command sandbox, so
the owner runs this outside it (D-06). The image is AGPLv3; reference the image only and never
vendor Velxio code into this MIT repository.

```sh
docker rm -f velxio 2>/dev/null || true
docker pull ghcr.io/davidmonterocrespo24/velxio:master
docker inspect --format '{{index .RepoDigests 0}}' ghcr.io/davidmonterocrespo24/velxio:master
docker run -d --name velxio -p 3080:80 \
  -v velxio-data:/app/data -v velxio-arduino-libs:/root/.arduino15 \
  -v velxio-arduino-user-libs:/root/Arduino -v velxio-ccache:/var/cache/ccache \
  -v velxio-build:/var/lib/velxio-build \
  ghcr.io/davidmonterocrespo24/velxio:master
```

The optional `docker rm -f velxio` first is deliberate: a stale container under that name
would otherwise block the single attempt. The `docker inspect` digest is mandatory because
`:master` is a mutable tag and the digest is the only reproducible identity.

Bounded readiness poll, at most 60 attempts two seconds apart:

```sh
for i in $(seq 1 60); do
  curl -sf -o /dev/null http://localhost:3080 && break
  sleep 2
done
docker logs --tail 50 velxio
```

Board capture: save a screenshot outside the repository, or copy the UI text listing the
supported boards, or record the page URL plus the exact reason the list is unavailable. Never
infer a board list.

Closing cleanup; the five named volumes stay in place so a later attempt does not pay the
5–7 minute cold ESP-IDF compile again:

```sh
docker rm -f velxio
```

## Velxio self-host attempt

**Provenance.** The repository owner disabled the command sandbox for this attempt — the
Docker socket is unreachable from inside it — and the orchestrator then executed the Velxio
protocol above in the owner's environment. Except for the board screenshot noted below, which
is the owner's own live UI capture, everything here is agent-executed output from the owner's
machine under that explicit sandbox change; it is **not** an owner-typed terminal capture, and
it cannot be reproduced from inside the command sandbox.

**Image identity.** The pull
`docker pull ghcr.io/davidmonterocrespo24/velxio:master` reported
`Status: Downloaded newer image for ghcr.io/davidmonterocrespo24/velxio:master`. The recorded
identity is the immutable digest returned by
`docker inspect --format '{{index .RepoDigests 0}}'` (`measured`):

```text
ghcr.io/davidmonterocrespo24/velxio@sha256:5d673722f66cf2c5c8cef1fe4a04421a7d88fd863a7a266f8661ff269b3b3bc5
```

The mutable `:master` tag is the pull reference only; it is never the recorded identity
(T-07-06).

**Run configuration.** Container name `velxio`; host port `3080` published to container port
`80`; the five named volumes, exactly as in the protocol block:

| Volume | Mount point |
|--------|-------------|
| `velxio-data` | `/app/data` |
| `velxio-arduino-libs` | `/root/.arduino15` |
| `velxio-arduino-user-libs` | `/root/Arduino` |
| `velxio-ccache` | `/var/cache/ccache` |
| `velxio-build` | `/var/lib/velxio-build` |

`docker rm -f velxio` was run first as cleanup; no prior container of that name existed, so it
removed nothing.

**Boot measurement.** Two separate values, never merged:

| Quantity | Value | Label | Basis |
|----------|-------|-------|-------|
| `docker run` wall time | 0.335 s | `measured` | `time` reported `0.01s user 0.01s system 5% cpu 0.335 total` |
| First HTTP 200 | attempt 9 of 60, 16.988 s after the `docker run` start | `measured` | bounded poll, 2 s apart, `curl -sf -o /dev/null http://localhost:3080` |

Boot readiness is defined as the interval from the `docker run` start to the first HTTP 200:
**16.988 s (`measured`)**. The `0.335 s` wall time is the container-creation call returning,
not boot; the difference between the two is not the boot interval and is not reported as one.
The poll was bounded at 60 attempts two seconds apart, a 120 s ceiling
(`calculated (upper bound)`); the ninth attempt succeeded, so the ceiling was never reached.
The container id printed by `docker run` was `806f6276b45f` — an identifier, not a measurement.

**Board coverage (observed) — simulator catalogue.** Capture: the owner's live UI screenshot,
saved outside the repository at `$HOME/velxio-boards.png` (587620 bytes, `measured`), together
with the page URL `http://localhost:3080`. The simulator board catalogue displays
**BOARDS 47** (`measured`). The screenshot shows, among others, Arduino Uno/Nano/Mega 2560,
Raspberry Pi Pico/Pico W, Raspberry Pi Zero/1B+/2B/3B/4B/5, ESP32 DevKit V1, ESP32 DevKit C V4,
ESP32-CAM, Wemos Lolin32 Lite, **ESP32-S3 DevKit**, XIAO ESP32-S3, Arduino Nano ESP32,
ESP32-C3 DevKit, XIAO ESP32-C3, ESP32-C3 SuperMini, **STM32 Blue Pill**, **STM32 Black Pill**
and STM32 Blue Pill (F103CB). The simulator catalogue therefore carries AVR, RP2040, ESP32,
ESP32-S3, ESP32-C3 and STM32 boards (`measured`).

**Board coverage (observed) — arduino-cli compile backend, a separate list.** This is a
different surface from the simulator catalogue and must not be read as one. The page URL
`http://localhost:3080/api/compile/boards` returned HTTP 200 and listed **182 FQBNs
(`measured`)**: 27 `arduino:avr:*` and 155 `rp2040:rp2040:*`, with no other core. That list
carries no ESP32/ESP32-S3 or STM32 FQBN (`measured`). It is the compile backend's arduino-cli
core list, not the simulator catalogue: an ESP32-family compile would go through the ESP-IDF /
arduino-esp32 toolchains present in the image (see the toolchain row), not through those
FQBNs. The setup-status URL `http://localhost:3080/api/compile/setup-status` returned HTTP 200
with `arduino-cli 1.5.1`, cores `arduino:avr 1.8.8` and `rp2040:rp2040 6.3.1` (`measured`).

**Toolchain presence — separate observation, from `docker logs --tail 50 velxio`.** The log
shows ESP-IDF 5.5 activated (`IDF_PATH=/opt/esp-idf-v5`), the Arduino component at
`/opt/arduino-esp32`, `arduino-esp32 3.x core (IDF5)` at `/opt/arduino-esp32-3`, the Velxio
backend on `127.0.0.1:8001`, nginx on port 80, a completed uvicorn startup, and
`GET https://velxio.dev/api/pro/news/feed` returning 200 (`measured`). These toolchains are
what an ESP32-family compile in the simulator would use; they are a toolchain observation, not
a board entry and not the arduino-cli FQBN list above.

**Board coverage (vendor documentation).** Label: `datasheet`. The image's root page
`http://localhost:3080` (HTML title/description) states, quoting the vendor text:

> "19 boards: Arduino Uno/Nano/Mega/ATtiny85 (AVR8), ESP32 / ESP32-S3 (Xtensa QEMU),
> ESP32-C3 / CH32V003 (RISC-V), Raspberry Pi Pico (RP2040), Raspberry Pi 3 (Linux ARM)"

The `19 boards` figure is vendor text (`datasheet`), not an observation; the observed
simulator catalogue shows 47 boards, a different count. The vendor page claims ESP32 and
ESP32-S3, and the UI observation corroborates ESP32-S3. The vendor row and both observed rows
stay separate and are never merged.

**Pilot compile and serial.** Both `not measured`:

| Quantity | Value | Label |
|----------|-------|-------|
| Pilot compile in Velxio | not measured — the self-hosted editor does not consume a PlatformIO project | `not measured` |
| Pilot serial output in Velxio | not measured — no UI run of the pilot was performed in this session | `not measured` |

The ESP32-S3 board **is** available in the simulator catalogue; the blocker is project format
(the editor consumes sketches, not a PlatformIO project with `lib_deps`), not board support.
No trivial ESP-IDF capability compile was run in the UI either, so there is no
capability-observation row. The homework was not ported to a Velxio sketch to manufacture a
measurement.

**ESP32-S3 and STM32 presence — observed, against the prior expectation.** The simulator
catalogue shows ESP32-S3 boards (ESP32-S3 DevKit, XIAO ESP32-S3, Arduino Nano ESP32) and STM32
boards (STM32 Blue Pill, STM32 Black Pill, STM32 Blue Pill F103CB) (`measured`). This
contradicts two earlier assumptions behind this plan — that ESP32-S3 was not available through
the self-hosted editor, and that STM32 was not available at all. Both are recorded as present
because the UI observation says so; the observation wins over the expectation. STM32
simulation is therefore not Renode-exclusive in principle, although no STM32 run was attempted
here.

**Licence boundary (AGPLv3).** The image is AGPLv3 and is **referenced only**: no Velxio
source, image layer, part graphic, or other asset is vendored into this MIT repository, and
`git status --porcelain` shows no change outside `.planning/phases/07-simulation-spike/`. This
record, a digest plus observed values, preserves that boundary (T-07-07).

**Why the five named volumes matter.** Without them the first ESP-IDF compile after a restart
is minutes rather than seconds (`datasheet`, quoted from the Velxio documentation: roughly
5–7 minutes cold against 5–30 seconds with warmed volumes). Any compile timing taken from this
image is meaningful only with all five volumes mounted; a number from a cold, volume-less
container would describe toolchain installation, not compilation.

**Cleanup record.** After the capture, `docker rm -f velxio` printed `velxio` and the container
was gone (`measured`). The five named volumes persist intentionally — `velxio-arduino-libs`,
`velxio-arduino-user-libs`, `velxio-build`, `velxio-ccache` and `velxio-data` — so a later
attempt does not repay the cold ESP-IDF compile.

**Wokwi quota.** This attempt consumed no Wokwi quota: it never contacted Wokwi, opened no
session and used no token. The quota ledger above is unaffected.

## Free measurement ladder

All measurements below are quota-free (D-03): no simulation session is opened. They were run
in the Plan 02 worktree on 2026-10-26.

| Quantity | Value | Label | Command / note |
|----------|-------|-------|----------------|
| `wokwi-cli` version | `0.28.1 (7cf4ffaebfd8)` | `measured` | `wokwi-cli --short-version` |
| PlatformIO Core | `6.2.0` | `measured` | `pio --version` |
| Offline lint | exit 0, `Found 1 info` | `measured` | `wokwi-cli lint --offline homeworks/1_3-police-flasher/assets/diagram.json` |
| Build cold, repeat 1 | 10.98 s | `measured` | `pio run -d … -t clean` then `pio run -d …` |
| Build cold, repeat 2 | 7.63 s | `measured` | same |
| Build cold, repeat 3 | 8.13 s | `measured` | same |
| **Build cold, median** | **8.13 s** | `measured` | median of the three repeats |
| Build warm, repeat 1 | 0.50 s | `measured` | `touch homeworks/1_3-police-flasher/src/main.cpp` then `pio run -d …` |
| Build warm, repeat 2 | 0.49 s | `measured` | same |
| Build warm, repeat 3 | 0.48 s | `measured` | same |
| **Build warm, median** | **0.49 s** | `measured` | median of the three repeats |
| Merged firmware | `firmware.merged.bin`, `0x5da00` bytes (374.5 KB) | `measured` | produced by the promoted `scripts/pio/merge_firmware.py` post action |
| D-07 scenario probe | exit 1, `Error connecting to ws://127.0.0.1:1` | `measured` | see below |

Definitions (RESEARCH §Step 0): build cold is `pio run` after `pio run -t clean` with packages
already installed; build warm is `pio run` after touching `src/main.cpp`. There is no local
CLI cache to clear, so neither build is a cache effect. `touch` changes mtime only; no file
content changed.

### D-07 scenario-field revalidation

Network-free probe, no quota, run with the literal dummy token against a closed local port:

```sh
WOKWI_CLI_TOKEN=dummy WOKWI_CLI_SERVER=ws://127.0.0.1:1 \
  wokwi-cli homeworks/1_3-police-flasher \
  --diagram-file assets/diagram.json --scenario scenario.yaml --timeout 15000
```

Observed (`measured`): exit 1 with

```text
Error: Error connecting to ws://127.0.0.1:1: connect EPERM 127.0.0.1:1 - Local (0.0.0.0:0)
```

The probe reached the connection stage with **no** `Invalid scenario step key` error, so the
repository's `scenario.yaml` field names are current for `wokwi-cli 0.28.1`: `wait-serial`,
`delay`, and `expect-pin` with `part-id`, `name`, `value`. The published documentation's
`pin`/`expected` example is stale. D-07 is closed by this probe, not by a documentation claim.

### Free-ladder observation

The Plan 02 worktree is a fresh checkout, so
`homeworks/1_3-police-flasher/.pio/build/esp32s3_arduino/firmware.merged.bin` did not exist
before this task. It is a build artifact (`.pio/` is ignored and never tracked), and the
documented cold-build step above regenerated it through the promoted `merge_firmware.py`
post action; the file is present and its size is recorded above. The first cold build also
installed the Unity library; one PlatformIO network-update probe to GitHub was denied inside
the sandbox and did not affect the build.

## Wokwi session — protocol A

Protocol A is three short runs (cold, warm, repeat), each bounded by `--timeout 15000`, with a
hard quota budget tracked after every run (D-01). Serial reliability is an observation, not a
statistic (D-04): the exact count is recorded, never a percentage.

All three runs of protocol A are recorded below: run 1 (cold), run 2 (warm) and run 3
(repeat). The table keeps its final columns.

| Run | Command | Wall clock | Simulator cold | Simulator warm | Exit code | Serial line present | Simulated minutes | Label | VCD |
|-----|---------|------------|----------------|----------------|-----------|---------------------|-------------------|-------|-----|
| 1 (cold) | stamped run-1 invocation (§Run 1 capture) | 5.815 s | 3.759 s | not measured — first invocation in the session | 0 — scenario completed; every step passed | yes — exactly one `I pattern ready` | calculated (upper bound) 15 s — dashboard before/after not supplied | measured | absent — Error exporting VCD: Error 6: No logic analyzer in diagram |
| 2 (warm) | stamped run-2 invocation (§Run 2 capture) | 8.559 s | not measured — not the first invocation in the session | 6.753 s | 0 — scenario completed; every step passed | yes — exactly one `I pattern ready` | calculated (upper bound) 15 s — dashboard before/after not supplied | measured | not requested — no `--vcd-file` on runs 2-3 |
| 3 (repeat) | stamped run-3 invocation (§Run 3 capture) | 12.701 s | not measured — not the first invocation in the session | 11.238 s | 0 — scenario completed; every step passed | yes — exactly one `I pattern ready` | calculated (upper bound) 15 s — dashboard before/after not supplied | measured | not requested — no `--vcd-file` on runs 2-3 |

Column rules (RESEARCH §Measurement Protocol Step 0): `Wall clock` is the wrapper's total
(process spawn to exit); `Simulator cold` is process spawn to the first serial byte on the
first invocation in the measurement session; `Simulator warm` is the same interval on a
subsequent invocation in the same session; `Exit code` carries its 0/42/1 meaning; `Serial
line present` answers whether `pattern ready` appears; `Simulated minutes` is the dashboard
delta labelled `measured` or the `--timeout 15000` bound labelled `calculated (upper bound)`;
`VCD` is the path when a run produced one, `not requested` when the option was omitted, and
otherwise `absent — <first error line>`.

If a run cannot produce a serial log, a VCD file, or a readable dashboard delta, the affected
cell records `absent — <first error line>`. No number is inferred.

### Run 1 capture — 2026-10-26

Exact command (run 1, cold; the token was supplied at a silent prompt in the owner's terminal,
outside the command sandbox — token supplied by the repository owner; value not recorded):

```sh
python3 -u "$HOME/wokwi-stamp.py" wokwi-cli homeworks/1_3-police-flasher \
  --scenario scenario.yaml --diagram-file assets/diagram.json \
  --timeout 15000 --serial-log-file "$HOME/wokwi-run1.serial.log" \
  --vcd-file "$HOME/wokwi-run1.vcd" \
  > "$HOME/wokwi-run1.log" 2>&1
echo "exit=$?"
```

Stamped output (`$HOME/wokwi-run1.log`, ANSI-stripped; `measured`):

```text
+   0.099s | Wokwi CLI v0.28.1 (7cf4ffaebfd8)
+   0.445s | Connected to Wokwi Simulation API 1.0.0-20261026-g45f2303e
+   2.542s | Starting simulation...
+   3.759s | ESP-ROM:esp32s3-20210327
+   3.759s | Build:Mar 27 2021
+   3.759s | rst:0x1 (POWERON),boot:0x8 (SPI_FAST_FLASH_BOOT)
+   3.759s | SPIWP:0xee
+   3.759s | mode:QIO, clock div:1
+   3.759s | load:0x3fce2820,len:0x10cc
+   3.759s | load:0x403c8700,len:0xc2c
+   3.759s | load:0x403cb700,len:0x30b0
+   3.759s | entry 0x403c88b8
+   4.973s | I pattern ready
+   4.973s | [Police flasher smoke] Expected text matched: "pattern ready"
+   4.975s | [Police flasher smoke] delay 100ms
+   5.370s | [Police flasher smoke] expect-pin esp:4 == 1
+   5.514s | [Police flasher smoke] Scenario completed successfully
+   5.658s | Error exporting VCD: Error 6: No logic analyzer in diagram
+   5.815s | EXIT 0
```

Wrapper invocation status (`measured`): `exit=0`.

Serial log contents (`$HOME/wokwi-run1.serial.log`, `measured`):

```text
ESP-ROM:esp32s3-20210327
Build:Mar 27 2021
rst:0x1 (POWERON),boot:0x8 (SPI_FAST_FLASH_BOOT)
SPIWP:0xee
mode:QIO, clock div:1
load:0x3fce2820,len:0x10cc
load:0x403c8700,len:0xc2c
load:0x403cb700,len:0x30b0
entry 0x403c88b8
I pattern ready
```

Run-1 notes:

- Wall clock `5.815 s` (`measured`) is the wrapper's `EXIT` line: process spawn to exit.
- Simulator cold `3.759 s` (`measured`) is process start (`+ 0.000 s`) to the first serial
  byte (`+ 3.759 s | ESP-ROM:esp32s3-20210327`). This is the first invocation in the
  measurement session, so the warm interval is `not measured` for this row.
- Exit code `0` (`measured`): scenario completed and every step passed, per the mapping above.
- The serial log contains exactly one `I pattern ready` line (`measured`); the scenario's
  `wait-serial` step matched it and the `expect-pin esp:4 == 1` step passed.
- Simulated minutes is `calculated (upper bound) 15 s` from `--timeout 15000`: the dashboard
  usage figure before and after the run was not supplied by the owner, so no observed
  consumption is recorded and no other number is inferred.
- VCD is `absent — Error exporting VCD: Error 6: No logic analyzer in diagram` (`measured`):
  no logic analyzer is present in `assets/diagram.json`, so the file was not produced. Its
  last timestamp cannot be read.
- The wrapper `shasum -a 256` was not included in the fixed capture: `not measured — not
  supplied by the owner`.
- Owner-reported token-risk scan of both captures: 0 matches for
  `token|bearer|secret|authorization` (owner-run; scan command not supplied).

### Run 2 capture — 2026-10-26

Exact command (run 2, warm; the token was supplied at a silent prompt in the owner's
terminal, outside the command sandbox — token supplied by the repository owner; value not
recorded). The `--serial-log-file` value kept the literal placeholder `<N>` instead of `2`,
so the run-specific serial log is recorded `absent` in the note below; the redirect target is
the run-2 capture file the owner reported.

```sh
python3 -u "$HOME/wokwi-stamp.py" wokwi-cli homeworks/1_3-police-flasher \
  --scenario scenario.yaml --diagram-file assets/diagram.json \
  --timeout 15000 --serial-log-file "$HOME/wokwi-run<N>.serial.log" \
  > "$HOME/wokwi-run2.log" 2>&1
echo "exit=$?"
```

Stamped output (owner-pasted, ANSI-stripped; `measured`):

```text
+   0.039s | Wokwi CLI v0.28.1 (7cf4ffaebfd8)
+   0.363s | Connected to Wokwi Simulation API 1.0.0-20261026-g45f2303e
+   4.855s | Starting simulation...
+   6.753s | ESP-ROM:esp32s3-20210327
+   6.753s | Build:Mar 27 2021
+   6.753s | rst:0x1 (POWERON),boot:0x8 (SPI_FAST_FLASH_BOOT)
+   6.753s | SPIWP:0xee
+   6.753s | mode:QIO, clock div:1
+   6.753s | load:0x3fce2820,len:0x10cc
+   6.753s | load:0x403c8700,len:0xc2c
+   6.753s | load:0x403cb700,len:0x30b0
+   6.753s | entry 0x403c88b8
+   7.879s | I pattern ready
+   7.879s | [Police flasher smoke] Expected text matched: "pattern ready"
+   7.879s | [Police flasher smoke] delay 100ms
+   8.256s | [Police flasher smoke] expect-pin esp:4 == 1
+   8.400s | [Police flasher smoke] Scenario completed successfully
+   8.559s | EXIT 0
```

Wrapper invocation status (`measured`): `exit=0`.

Serial log contents: the run-specific file `$HOME/wokwi-run2.serial.log` is
`absent — the invocation used the literal placeholder <N>, so both runs wrote to $HOME/wokwi-run<N>.serial.log (246 bytes, overwritten by run 3); the stamped output carries the same lines`.

Observed serial lines, quoted from the stamped output (`measured`; they match the single
overwritten serial file):

```text
ESP-ROM:esp32s3-20210327
Build:Mar 27 2021
rst:0x1 (POWERON),boot:0x8 (SPI_FAST_FLASH_BOOT)
SPIWP:0xee
mode:QIO, clock div:1
load:0x3fce2820,len:0x10cc
load:0x403c8700,len:0xc2c
load:0x403cb700,len:0x30b0
entry 0x403c88b8
I pattern ready
```

Run-2 notes:

- Wall clock `8.559 s` (`measured`) is the wrapper's `EXIT` line: process spawn to exit.
- Simulator warm `6.753 s` (`measured`) follows the RESEARCH §Step 0 definition — the same
  interval as the cold row on a subsequent invocation in the same session: process spawn
  (`+ 0.000 s`) to the first serial byte (`+ 6.753 s | ESP-ROM:esp32s3-20210327`). Raw
  anchors for audit: process start `+ 0.000 s`, `Starting simulation...` at `+ 4.855 s`,
  first serial byte `+ 6.753 s`. The pre-simulation phase is `4.855 s` and the simulated
  boot is `1.898 s` (`calculated` from the two measured timestamps).
- Exit code `0` (`measured`): scenario completed and every step passed, per the mapping above.
- The stamped output contains exactly one `I pattern ready` line (`measured`); the scenario's
  `wait-serial` step matched it and the `expect-pin esp:4 == 1` step passed.
- Simulated minutes is `calculated (upper bound) 15 s` from `--timeout 15000`: the dashboard
  usage figure before and after the run was not supplied by the owner, so no observed
  consumption is recorded and no other number is inferred.
- VCD is `not requested — no --vcd-file on runs 2-3`: the file was not asked for, so none
  exists and no timestamp is read.

### Run 3 capture — 2026-10-26

Exact command (run 3, repeat; the token was supplied at a silent prompt in the owner's
terminal, outside the command sandbox — token supplied by the repository owner; value not
recorded). As in run 2, `--serial-log-file` kept the literal placeholder `<N>`.

```sh
python3 -u "$HOME/wokwi-stamp.py" wokwi-cli homeworks/1_3-police-flasher \
  --scenario scenario.yaml --diagram-file assets/diagram.json \
  --timeout 15000 --serial-log-file "$HOME/wokwi-run<N>.serial.log" \
  > "$HOME/wokwi-run3.log" 2>&1
echo "exit=$?"
```

Stamped output (owner-pasted, ANSI-stripped; `measured`):

```text
+   0.035s | Wokwi CLI v0.28.1 (7cf4ffaebfd8)
+   2.117s | Connected to Wokwi Simulation API 1.0.0-20261026-g45f2303e
+  10.209s | Starting simulation...
+  11.238s | ESP-ROM:esp32s3-20210327
+  11.238s | Build:Mar 27 2021
+  11.238s | rst:0x1 (POWERON),boot:0x8 (SPI_FAST_FLASH_BOOT)
+  11.239s | SPIWP:0xee
+  11.239s | mode:QIO, clock div:1
+  11.239s | load:0x3fce2820,len:0x10cc
+  11.239s | load:0x403c8700,len:0xc2c
+  11.239s | load:0x403cb700,len:0x30b0
+  11.239s | entry 0x403c88b8
+  12.051s | I pattern ready
+  12.051s | [Police flasher smoke] Expected text matched: "pattern ready"
+  12.051s | [Police flasher smoke] delay 100ms
+  12.403s | [Police flasher smoke] expect-pin esp:4 == 1
+  12.550s | [Police flasher smoke] Scenario completed successfully
+  12.701s | EXIT 0
```

Wrapper invocation status (`measured`): `exit=0`.

Serial log contents: the run-specific file `$HOME/wokwi-run3.serial.log` is
`absent — the invocation used the literal placeholder <N>, so both runs wrote to $HOME/wokwi-run<N>.serial.log (246 bytes, overwritten by run 3); the stamped output carries the same lines`.

Observed serial lines, quoted from the stamped output (`measured`; they match the single
overwritten serial file):

```text
ESP-ROM:esp32s3-20210327
Build:Mar 27 2021
rst:0x1 (POWERON),boot:0x8 (SPI_FAST_FLASH_BOOT)
SPIWP:0xee
mode:QIO, clock div:1
load:0x3fce2820,len:0x10cc
load:0x403c8700,len:0xc2c
load:0x403cb700,len:0x30b0
entry 0x403c88b8
I pattern ready
```

Run-3 notes:

- Wall clock `12.701 s` (`measured`) is the wrapper's `EXIT` line: process spawn to exit.
- Simulator warm `11.238 s` (`measured`), same definition as run 2: process spawn
  (`+ 0.000 s`) to the first serial byte (`+ 11.238 s | ESP-ROM:esp32s3-20210327`). Raw
  anchors: process start `+ 0.000 s`, `Starting simulation...` at `+ 10.209 s`, first serial
  byte `+ 11.238 s`. The pre-simulation phase is `10.209 s` and the simulated boot is
  `1.029 s` (`calculated` from the two measured timestamps).
- Exit code `0` (`measured`): scenario completed and every step passed.
- The stamped output contains exactly one `I pattern ready` line (`measured`).
- Simulated minutes is `calculated (upper bound) 15 s` from `--timeout 15000`: no dashboard
  before/after figure was supplied, so no observed consumption is recorded.
- VCD is `not requested — no --vcd-file on runs 2-3`.

### Warm-interval observation

The two warm intervals are `6.753 s` and `11.238 s` (`measured`), both longer than the run-1
cold interval of `3.759 s`. That is not a contradiction: RESEARCH §Step 0 defines warm as the
"same interval on a subsequent invocation in the same session", and explicitly forbids reading
a cache effect into it — there is no local CLI cache to clear. The interval here is dominated
by the wait before `Starting simulation...` (connection and server allocation: `4.855 s` and
`10.209 s`), while the simulated boot after it stays in the `1.029`–`1.898 s` range
(`calculated`). A single warm value is therefore not representative; both measured values are
recorded rather than a mean, and no speed claim is attached to "warm".

## Quota ledger

The vendor dashboard is the only direct observation of consumption. The `Dashboard before` row
is read before the first session (A8: the free-plan quota is checked, not assumed).

| Run | Dashboard before | Dashboard after | Delta | Cumulative | Label |
|-----|------------------|-----------------|-------|------------|-------|
| Dashboard before | not supplied by the owner | — | — | — | not measured — dashboard before figure not supplied by the owner |
| 1 | not supplied by the owner | not supplied by the owner | not measured — dashboard before/after figures not supplied by the owner | 1 run / 15 s upper bound | calculated (upper bound) |
| 2 | not supplied by the owner | not supplied by the owner | not measured — dashboard before/after figures not supplied by the owner | 2 runs / 30 s upper bound | calculated (upper bound) |
| 3 | not supplied by the owner | not supplied by the owner | not measured — dashboard before/after figures not supplied by the owner | 3 runs / 45 s upper bound | calculated (upper bound) |

Rows are added cumulatively after every run. If the figure is too coarse for a per-run delta,
the row records the timeout bound instead and carries the `calculated (upper bound)` label.

## Handoff to ADR-0014

**Outcome:** scenario passed

**Expected serial line observed:** 3/3 runs observed the expected serial line

**Blocker:** none

**Quota consumed:** 3 runs; 45 s cumulative upper bound, `calculated (upper bound)` — dashboard figures not supplied

The outcome is exactly one of three values. `scenario passed` is legal only when every counted
run exited 0 **and** each serial log contains `pattern ready`; an executed run alone is never
success. `scenario failed` is written when an executed run exited non-zero for an assertion or
scenario-validation reason. `execution blocked` is written when the first error line names the
token, authentication, quota, or the connection; in that case the session stops and the phase
proceeds without flipping the homework status.

Basis for `scenario passed`: all three counted runs exited 0, and each run's stamped output
contains exactly one `I pattern ready` line and the scenario's own
`Expected text matched: "pattern ready"` line. For run 1 that line is also quoted from the
run-specific serial log. For runs 2 and 3 the run-specific serial log files are `absent` only
because the `--serial-log-file` argument kept the literal placeholder `<N>` and both runs
overwrote the same file; the serial lines are still quoted verbatim from each stamped output,
which captures the same stream. No serial line is invented for a file that was not produced.

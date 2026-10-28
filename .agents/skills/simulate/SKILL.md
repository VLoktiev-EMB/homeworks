---
name: simulate
description: Use when the user asks to simulate a homework circuit locally in VS Code with Wokwi, wants a wokwi.toml set up, needs to see LEDs or GPIO behavior without physical hardware, wants a diagram linted offline, or needs a bounded headless wokwi-cli scenario or VCD capture. Use this skill for any Wokwi, local simulation, logic-analyzer, or simulated-evidence request, even when the user only says "simulate it" or "run it in VS Code".
metadata:
  version: "2.0"
  status: active
---

# Wokwi Simulation

Read `../_shared/guardrails.md` before the first write. It owns the token,
evidence, and confirmation rules that this skill depends on.

Two runtimes simulate the same `assets/diagram.json`, and they are not
interchangeable:

| Runtime | Where it runs | Authorization | Quota |
|---------|---------------|---------------|-------|
| Wokwi for VS Code | Local simulator inside the extension | A free extension license activated in the browser | Does not consume the `wokwi-cli` cloud quota |
| `wokwi-cli` | Headless, connects to the Wokwi simulation API | `WOKWI_CLI_TOKEN` environment variable | About 50 minutes per rolling 30 days |

The local VS Code path is the default for a homework. Reach for `wokwi-cli`
only when the user asks for CI, automation, a scenario file, or a VCD capture.
Never ask for a CI token when the user only wants to watch the circuit locally.

## Setup: run this on every simulation request

### 1. Build the firmware first

Both runtimes read an existing build; neither compiles code.

```sh
pio run -d homeworks/<id>
```

The build must produce `.pio/build/<env>/firmware.bin` and `firmware.elf`,
where `<env>` is the `default_envs` value in the homework `platformio.ini`
(for this repository usually `esp32s3_arduino` or `esp32s3_espidf`). If
`default_envs` is absent, use the single directory under `.pio/build/` that
contains `firmware.bin`.

### 2. Ensure `assets/wokwi.toml`

If `assets/diagram.json` is absent, stop here: author the circuit with the
`schematic` skill first. A Wokwi project without a diagram has nothing to
simulate, and inventing a second netlist beside the authored one hides the
real wiring.

`wokwi.toml` must sit **next to** the `diagram.json` it configures. In this
repository the diagram lives in `assets/`, so the config is
`homeworks/<id>/assets/wokwi.toml` and the firmware paths climb one level:

```toml
# Wokwi for VS Code project configuration.
# The simulator reads the PlatformIO build artifacts; it never compiles.
[wokwi]
version = 1
firmware = "../.pio/build/<env>/firmware.bin"
elf = "../.pio/build/<env>/firmware.elf"
```

Rules for this file:

- Paths are relative to the `wokwi.toml` location, not to the repository root.
- Use forward slashes.
- Keep `assets/diagram.json` as the only netlist. Never create a second
  `diagram.json` at the homework or repository root just to please the
  extension; select the config file instead.
- The file contains paths only, never a token or a license.
- If the file already exists, validate it instead of overwriting it. Update it
  only when the environment name changed or the firmware paths are wrong.

Validate the result without guessing:

```sh
python3 -I - <<'PY'
import tomllib
from pathlib import Path

base = Path("homeworks/<id>/assets")
config = tomllib.loads((base / "wokwi.toml").read_text(encoding="utf-8"))["wokwi"]
assert config["version"] == 1
for key in ("firmware", "elf"):
    path = (base / config[key]).resolve()
    print(key, path, path.is_file())
PY
```

Both paths must print `True`. If either is missing, return to step 1.

### 3. Lint the diagram offline

This costs no quota and no token, and catches a broken part or pin before a
session starts:

```sh
wokwi-cli lint --offline homeworks/<id>/assets/diagram.json
```

Treat the `unsupported-part` note for the ESP32-S3 board as informational.
Any error output is a stop; fix the diagram, not the renderer.

## Local run in VS Code

Hand these steps to the user after the setup above:

1. Confirm the extension is installed: `code --list-extensions | grep -i wokwi`
   should show `wokwi.wokwi-vscode`. If it is absent, install it from the VS
   Code Marketplace before continuing.
2. Open the repository workspace or the homework folder in VS Code.
3. Command Palette -> **`Wokwi: Select Config File`** ->
   `homeworks/<id>/assets/wokwi.toml`.
4. Command Palette -> **`Wokwi: Start Simulator`** (or the Wokwi icon in the
   editor title bar or sidebar).

If VS Code asks for a license, run **`Wokwi: Request a new License`** and
activate it in the browser. That is the extension license, not
`WOKWI_CLI_TOKEN`; do not substitute one for the other.

After every firmware change, rebuild with `pio run` before restarting the
simulator. The extension keeps reading the last built artifacts.

Tell the user what the circuit should show, for example: the red and blue LEDs
alternate, the white LED adds a strobe phase, and the cadence changes between
cycles. A local run is still `simulated` evidence, never bench measurement.

## Optional headless run

Use this only for CI or an automated scenario. It requires a valid
`WOKWI_CLI_TOKEN` in the environment. Check presence only:

```sh
if [ -n "${WOKWI_CLI_TOKEN:-}" ]; then echo present; else echo absent; fi
```

Never print, log, or write the token value. If the variable is absent, stop and
ask the user to export it themselves; do not try to extract it from a local
credentials file.

The positional path is the project directory, and `--scenario` and
`--diagram-file` are resolved **relative to it**, not to the shell's current
directory. Use an absolute `--elf` and absolute log paths:

```sh
P="$PWD/homeworks/<id>"
wokwi-cli homeworks/<id> \
  --elf "$P/.pio/build/<env>/firmware.elf" \
  --scenario scenario.yaml \
  --diagram-file assets/diagram.json \
  --timeout 12000 \
  --serial-log-file "$P/.pio/sim/serial.log" \
  --vcd-file "$P/.pio/sim/police.vcd"
```

A bounded scenario keeps quota predictable:

```yaml
name: Police flasher cycle and speed change
version: 1
author: <public handle>
steps:
  - wait-serial: "police flasher started"
  - delay: 7000ms
```

Supported steps include `wait-serial`, `delay` with units such as `7000ms`,
`expect-pin` (`part-id`, `name` or the older `pin`, and `value`), `set-control`,
`write-serial`, and `take-screenshot`. Assert only driven pin states; a pin in
high-impedance `INPUT` has no guaranteed sampled value.

`--vcd-file` records the data of a `wokwi-logic-analyzer` part, not every MCU
pin automatically. To capture GPIO evidence without touching the authored
diagram, derive a temporary copy under the ignored `.pio/sim/` directory, add
the analyzer there, connect `D0`/`D1` to the pins and its ground to the board
ground, and lint that copy offline:

```json
{ "type": "wokwi-logic-analyzer", "id": "la", "top": 200, "left": 200, "attrs": {} }
```

Never overwrite `assets/diagram.json` with the instrumented copy, and never
commit the derived copy.

## Evidence rules

- A simulation result is `simulated`. It is never `measured`, never bench
  evidence, and never a substitute for current or voltage measurements.
- Update the report only after a run the user actually observed or a command
  that exited successfully. A failed or unauthorized run produces no claim.
- When a run succeeds and the user wants it recorded, add a `simulation` block
  to `homework.yaml`:
  `tool: wokwi`, `diagram: assets/diagram.json`, `status: verified`.
- Add a `**Simulation.**` paragraph to section 7 of `report.md` and a ledger
  row whose label is `simulated`. The row's method must name a run artifact:
  a saved screenshot such as `assets/simulation.png`, or a scenario or VCD
  path. A local visual run without an artifact is not `verified` evidence; keep
  `simulation.status: pending` until the user supplies one.
- The report status and homework status must still satisfy the pair in
  `.agents/standards/report.md`.

## Common mistakes and red flags

- **Red flag:** asking for a CI token for a local VS Code run. The extension
  uses its own license.
- **Red flag:** claiming simulated behavior as `measured`.
- **Red flag:** running a scenario on an uncompiled project; the CLI reports a
  missing firmware or ELF.
- **Red flag:** duplicating `diagram.json` at the repository root instead of
  selecting `assets/wokwi.toml` in the extension.
- **Mistake:** putting `wokwi.toml` at the repository root while the diagram is
  in `assets/`; the extension reports no `diagram.json` next to the config.
- **Mistake:** forgetting `--diagram-file assets/diagram.json`, which makes
  `wokwi-cli` look for a diagram in the project root.
- **Mistake:** unbounded scenario delays or a timeout far longer than the
  pattern under test.
- **Mistake:** expecting `wokwi-cli lint` to validate scenario YAML. It lints
  the diagram only; a malformed scenario surfaces when the scenario runs.

## Verification checklist

```sh
pio run -d homeworks/<id>
python3 -I -c "import tomllib,pathlib; b=pathlib.Path('homeworks/<id>/assets'); c=tomllib.loads((b/'wokwi.toml').read_text())['wokwi']; print([(k,(b/c[k]).resolve().is_file()) for k in ('firmware','elf')])"
wokwi-cli lint --offline homeworks/<id>/assets/diagram.json
# VS Code: Select Config File -> assets/wokwi.toml, then Start Simulator
# Optional headless: confirm WOKWI_CLI_TOKEN presence, then run the bounded command above
```

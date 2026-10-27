# Police Flasher

This project is the independent PlatformIO homework for `1_3-police-flasher`: an
ESP32-S3 Arduino police flasher whose pattern logic runs on the host in native unit
tests.

**Status:** in-progress

- [Report](report.md)
- [Assignment paraphrase](task.md)

The project must live at `homeworks/<id>`, two levels below the repository root, so
every relative path — including the shared partition table — resolves.

## Schematic and Wiring

The circuit combines an anti-parallel LED pair on GPIO4, a single indicator LED on GPIO6, and a mode pushbutton to GND on GPIO7:

```mermaid
flowchart LR
    subgraph Board["ESP32-S3 DevKitC-1"]
        esp[esp]
    end
    r1("r1 [150Ω]")
    led1("led1 [LED red]")
    led2("led2 [LED red]")
    r2("r2 [150Ω]")
    led3("led3 [LED red]")
    btn1("btn1 [MODE]")

    btn1 -->|1.l -> 7| esp
    btn1 -->|2.l -> GND.1| esp
    esp -->|4 -> 1| r1
    r1 -->|2 -> A| led1
    r1 -->|2 -> C| led2
    led1 -->|C -> GND.2| esp
    esp -->|3V3.1 -> A| led2
    esp -->|6 -> 1| r2
    r2 -->|2 -> A| led3
    led3 -->|C -> GND.2| esp
```

The interactive simulation model and wire routing are defined in [`assets/diagram.json`](assets/diagram.json).

## Simulation

`wokwi.toml` points at `.pio/build/esp32s3_arduino/firmware.merged.bin`, so build the
target before running the scenario. `wokwi-cli` 0.28.1 joins the values of
`--diagram-file` and `--scenario` to the positional project directory, not to the shell
working directory. Pass both option values relative to the project directory; passing
repository-root paths makes the CLI join the project path twice and abort before it
opens a connection. From the repository root:

```sh
pio run -d homeworks/1_3-police-flasher
wokwi-cli homeworks/1_3-police-flasher --diagram-file assets/diagram.json --scenario scenario.yaml
```

The equivalent form enters the project first, passes `.` as the positional project
argument, and keeps the same two option values:

```sh
cd homeworks/1_3-police-flasher
pio run
wokwi-cli . --diagram-file assets/diagram.json --scenario scenario.yaml
```

Execution needs `WOKWI_CLI_TOKEN`, and a missing token aborts earlier than path
resolution, so it cannot prove the paths. Run the command with
`WOKWI_CLI_TOKEN=dummy` to prove both paths resolve locally: the run reaches the
WebSocket connection or token stage without a real credential. The only token value
that belongs in this file is `dummy`; never write a real token here.
`wokwi-cli lint --offline homeworks/1_3-police-flasher/assets/diagram.json` validates the
wiring without one. The scenario has since been executed: all three counted runs exited 0 with
one `pattern ready` line each, so `simulation.status` in `homework.yaml` is `verified`. The
commands and per-run values are in
`.planning/phases/07-simulation-spike/07-SPIKE-EVIDENCE.md`, and the tool decision is in
`docs/decisions/0014-simulator-selection.md`.

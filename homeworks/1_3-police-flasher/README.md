# Police Flasher

This project is the independent PlatformIO homework for `1_3-police-flasher`: an
ESP32-S3 Arduino police flasher whose pattern logic runs on the host in native unit
tests.

**Status:** in-progress

- [Report](report.md)
- [Assignment paraphrase](task.md)

The project must live at `homeworks/<id>`, two levels below the repository root, so
every relative path — including the shared partition table — resolves.

## Simulation

`wokwi.toml` points at `.pio/build/esp32s3_arduino/firmware.merged.bin`, so build the
target before running the scenario. `wokwi-cli` resolves `--diagram-file` and
`--scenario` against the working directory, not the project directory, so pass both
paths repo-relative from the repository root:

```sh
pio run -d homeworks/1_3-police-flasher
wokwi-cli homeworks/1_3-police-flasher --diagram-file homeworks/1_3-police-flasher/assets/diagram.json --scenario homeworks/1_3-police-flasher/scenario.yaml
```

Execution needs `WOKWI_CLI_TOKEN`; `wokwi-cli lint --offline homeworks/1_3-police-flasher/assets/diagram.json`
validates the wiring without one. The run is deferred to Phase 7, so
`simulation.status` in `homework.yaml` stays `pending`.

---
name: simulate
description: Placeholder for running the Wokwi scenario and recording its evidence. Use only to look up the manual simulation command until this skill is promoted.
disable-model-invocation: true
metadata:
  version: "0.1"
  status: stub
---

# Simulate (stub)

> **Stub (v0.1).** This skill does not run a simulation, read serial output, or
> write a measurement-ledger row. Until it is promoted, run the documented
> command yourself:
> `wokwi-cli homeworks/<id> --diagram-file assets/diagram.json --scenario scenario.yaml`
> after `pio run -d homeworks/<id>`. A run consumes the Wokwi free-plan quota;
> simulation is never a build and never bench evidence.

## Manual command

Build the target first, then run the scenario from the repository root:

```bash
pio run -d homeworks/<id>
wokwi-cli homeworks/<id> --diagram-file assets/diagram.json --scenario scenario.yaml
```

The offline lint form checks the diagram and the scenario without spending
quota:

```bash
wokwi-cli lint --offline homeworks/<id>
```

## Quota

The Wokwi free plan allows about 50 minutes of simulation per rolling 30 days.
Compiling and linting are not simulation sessions, so only an actual run is
metered.

## Evidence boundary

A simulation run produces `simulated` evidence. It is never a build result and
never bench evidence, so it cannot stand in for a measured value.

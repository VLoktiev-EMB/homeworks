# Lessons

## 2026-10-27 — gap-closure run, 09-09

- A skill may claim to read a generated config value only when the generated source
  declares it. `hw-flash` asserted `monitor_speed` inheritance while no shared or
  homework PlatformIO file set it, so the monitor would have silently used 9600 against
  a report that records 115200. Declare the value in the template, then read and gate it.
- A policy exception belongs in the shared guardrails and is referenced, never restated
  in a skill. The capture exception now has one owner; `hw-flash` points at it, so the
  rule cannot drift into two disagreeing wordings.

## 2026-10-26 — initial 0.1 contract, phase 9 planning run

- The serial log has no owner for its meaning in v0.1: nothing parses it, no claim is
  extracted from it, and no measurement-ledger row is written. The rule it implies:
  capture the raw bytes and leave interpretation to a promoted parser, never to a guess
  made from one run's output.

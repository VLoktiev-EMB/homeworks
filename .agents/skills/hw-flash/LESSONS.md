<!-- GENERATED — do not edit. Run: uv run scripts/gen_skills.py -->
# Lessons

## 2026-10-26 — initial 0.1 contract, phase 9 planning run

- The serial log has no owner for its meaning in v0.1: nothing parses it, no claim is
  extracted from it, and no measurement-ledger row is written. The rule it implies:
  capture the raw bytes and leave interpretation to a promoted parser, never to a guess
  made from one run's output.

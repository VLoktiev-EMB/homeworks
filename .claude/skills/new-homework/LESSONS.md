# Lessons

## 2026-10-26 — initial 0.1 contract, phase 9 planning run

- The scaffold is idempotent: a second run reports `UNCHANGED` for every path, so a
  verification that demands `CREATE` fails after the first successful run. The rule it
  implies: accept `CREATE` or `UNCHANGED` from `scripts/new_homework`, and stop only on
  `CONFLICT` or `ERROR` (F-01).

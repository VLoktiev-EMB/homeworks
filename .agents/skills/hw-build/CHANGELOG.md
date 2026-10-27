<!-- GENERATED — do not edit. Run: uv run scripts/gen_skills.py -->
# Changelog

## 2026-10-26 — initial 0.1 contract, phase 9 planning run

- Added the two-leg build contract: the real `pio run -d homeworks/<id>` target build
  and the homework's `pio test -d homeworks/<id> -e native` suite, each reporting its
  own exit code.
- Added the bounded repair loop: at most two repair attempts per leg per run, with the
  whole invocation stopping when either leg exhausts two.
- Added the escalation payload that explains the cause, both attempted fixes and the
  evidence, then stops without a third edit.

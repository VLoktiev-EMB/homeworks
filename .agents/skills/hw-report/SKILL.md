---
name: hw-report
description: Placeholder for assembling a homework report from the measured evidence. Use only to look up the manual report fallback until this skill is promoted.
metadata:
  version: "0.1"
  status: stub
---
<!-- GENERATED — do not edit. Run: uv run scripts/gen_skills.py -->
> **Invocation:** explicit only — run `/hw-report`. Do not invoke this skill automatically.

# Report (stub)

> **Stub (v0.1).** This skill does not write `report.md`, transcribe assumptions,
> or validate the measurement ledger. The contract is published: follow
> `docs/standards/report.md`, and `uv run scripts/check_report.py` is its machine
> gate. Start from `templates/report/report.md` and use
> `homeworks/1_3-police-flasher/report.md` as the worked example. The checker
> proves structure and referential integrity, not that a value was measured —
> semantic truth stays a review duty. Promotion is a Phase 11 candidate, after
> the pilot is the first real use with the standard in place.

## Manual fallback

1. Start from the skeleton at `templates/report/report.md`.
2. Follow `docs/standards/report.md`; its self-audit checklist is the
   pre-pull-request gate alongside the machine rules.
3. Run `uv run scripts/check_report.py` from the repository root until it
   passes.
4. Compare the result with the worked example at
   `homeworks/1_3-police-flasher/report.md`.

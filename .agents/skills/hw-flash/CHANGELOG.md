<!-- GENERATED — do not edit. Run: uv run scripts/gen_skills.py -->
# Changelog

## 2026-10-26 — initial 0.1 contract, phase 9 planning run

- Added the explicit consent gate: print the board, the environment and the exact upload
  command, then accept only a literal `так` or `yes`, case-insensitive, with no other
  text. Every other answer stops, and no confirmation is reused.
- Added the upload leg, which runs `pio run -d homeworks/<id> -t upload` and reports the
  real exit code, with no repair and no second upload.
- Added the bounded `pio device monitor --raw` capture to the ignored
  `.skill-state/logs/<id>.log`, inheriting `monitor_speed` instead of hardcoding a baud,
  with the state-file path discipline and no log interpretation.
- Added the four outcome states and the `capture unavailable` rule that keeps the upload
  exit code as the flash result.

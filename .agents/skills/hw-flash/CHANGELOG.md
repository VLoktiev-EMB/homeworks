<!-- GENERATED — do not edit. Run: uv run scripts/gen_skills.py -->
# Changelog

## 2026-10-27 — gap-closure run, 09-09 (CR-01, CR-02, WR-01)

- Added fail-closed baud resolution before the gate: read `monitor_speed` from
  `pio project config -d homeworks/<id> --json-output`, stop and ask when the key is
  absent, and announce the effective baud in the consent gate. The shared PlatformIO
  template now declares `monitor_speed = 115200` for both ESP sections.
- Moved the capture policy to the shared guardrails' single scoped exception and
  referenced it here rather than restating it: the capture writes only after a
  credential-shape scan of the exact bytes finds no match.
- Corrected the bounded-capture snippet so it implements its own rules: the
  `needs_e_flag` branch, `OSError` handling for a missing `pio`, the pre-bound
  `returncode` check, the credential-shape scan, and the announced atomic
  `write_log_atomically` write to `.skill-state/logs/<id>.log`.
- Kept `metadata.version: "0.1"` and added no hardcoded `-b 115200`.

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

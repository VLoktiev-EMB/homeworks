<!-- GENERATED — do not edit. Run: uv run scripts/gen_skills.py -->
# Changelog

## 2026-10-27 — gap-closure run, 09-17, 09-18 (CR-01, WR-03)

- The credential scan now admits a space-separated compound keyword, so
  `SECRET KEY: <value>` and `secret key = <value>` are refused end to end and leave no log.
- The shared guardrails name that compound shape and its single-separator bound, so the
  policy and the scan agree.
- The skill no longer restates the shared same-resolved-port rule and points at it once;
  the operational port steps are unchanged.
- Kept `metadata.version: "0.1"`.

## 2026-10-27 — gap-closure run, 09-15, 09-16 (G-09-1)

- The monitor now opens the port with `--dtr 0 --rts 0`, so the ESP32-S3 application
  runs instead of being held in reset; the helper resolves exactly one USB serial
  device, forwards an explicit `--port` as `-p`, refuses an ambiguous set, and reports
  the device path, VID:PID and effective baud.
- `hw-flash` passes one resolved port to both `--upload-port` and `--port`, and
  documents the native USB-Serial-JTAG (`303A:1001`) and CH343 (`1A86:55D3`) paths,
  including baud significance, DTR/RTS reset semantics and re-enumeration.
- The log stays byte-exact raw device output with no header and no sidecar.
- Kept `metadata.version: "0.1"`.

## 2026-10-27 — gap-closure run, 09-14 (RR-CR-01)

- Widened the credential-shape scan to a keyword followed by identifier characters,
  so `secretKey: <value>`, `secret_key = <value>`, `passwordHash: <value>` and
  `SECRET_KEY = <value>` now match; the space-separated copula branch and its
  six-character floor are unchanged.
- Pinned the four shapes in `IDENTIFIER_SUFFIXED_ASSIGNMENTS` with their own named
  test, and added the end-to-end refusal test proving an identifier-suffixed
  credential leaves no log and no `.skill-state` directory.
- Named the suffix form in the shared capture exception and the helper docstring, and
  regenerated the `.agents/skills/` mirror rather than editing it.
- Kept `metadata.version: "0.1"`.

## 2026-10-27 — gap-closure run, 09-13 (WR-10, WR-11)

- Rejected a non-finite, non-positive or above-`MAX_SECONDS` `--seconds` with a
  `CheckError` before `resolve_root`, the monitor argv or `Popen`, so an invalid duration
  is the documented exit-2 usage error with no traceback and starts no process.
- Reaped the monitor in `capture_pty`'s outer `finally` on every exception path: a
  still-running child is killed, then waited, while the deadline, not-ready and EOF/EIO
  early returns keep working.
- Added `CliDurationTests` for NaN, infinity and an oversized bound, and
  `CaptureReapTests` proving an escaping `RuntimeError` leaves no live child.
- Kept `metadata.version: "0.1"`.

## 2026-10-27 — gap-closure run, 09-12 (WR-12)

- Widened the credential scan to the copula form (`password is <value>`), a keyword
  embedded after another word (`userpassword = <value>`), and the `passphrase` and `pwd`
  keywords, so the helper matches the policy sentence.
- Pinned the four new shapes in `REVIEW_SHAPES`, added a named assignment test, and added
  an ordinary-word negative test (`the cpwd tool reports ready`, `author wrote nothing
  here`) bounding the false-positive trade.
- Asserted that a credential match creates no `.skill-state` directory, proving the scan
  runs before the filesystem is touched.
- Kept `metadata.version: "0.1"`.

## 2026-10-27 — gap-closure run, 09-11 (CR-03, IN-06)

- Announced `[--baud <n>]` in both `hw-flash` capture commands, named `--baud` as the
  helper option, and stated that the helper appends `-b <n>` to the monitor.
- Named `[--env <env>]` and `[--baud <n>]` in the consent gate's conditional sentence, so
  the announced capture is the executed capture.
- Added `BuildCommandTests` for the forwarded `-e`/`-b` argv, `CliResultPayloadTests` for
  the `CAPTURED`/`REFUSED` JSON payloads, and a concurrent-reader case that observes only
  whole payloads.
- Kept `metadata.version: "0.1"`.

## 2026-10-27 — gap-closure run, 09-10 (CR-01, CR-02, WR-01..WR-06, IN-01, IN-02)

- Replaced the piped `pio device monitor` snippet with `scripts/serial_capture.py`, which
  allocates a pseudo-terminal, runs the monitor with `--raw --quiet`, reads the master for
  the bound, scans the exact bytes, and writes only on a clean scan.
- Widened the credential-shape scan to quoted, spaced, authorization and space-separated
  forms, including the six-character floor that catches `password abc123`.
- Restored the shared guardrails' general prohibition to cover the state file and any log
  outside the one scoped capture exception, and named the fail-closed scan shapes there.
- Announced the conditional `-e <env>` segment in the consent example and the upload
  command, normalized `monitor_speed` with `int(str(value))`, and replaced the outcome
  table's "timed out" wording with "capture failed".
- Kept `metadata.version: "0.1"`.

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

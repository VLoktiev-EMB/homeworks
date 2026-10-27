<!-- GENERATED — do not edit. Run: uv run scripts/gen_skills.py -->
# Lessons

## 2026-10-27 — gap-closure run, 09-17, 09-18

- A policy that enumerates credential shapes by name must enumerate every separator form the
  scan admits. A word-only reading of "secret assignment" misses `SECRET KEY:`, so the
  firmware line the rule forbids reaches the log.
- A normative rule duplicated in a skill drifts from its owner. The shared file states it
  once and every skill points at it; the operational steps stay in the skill.

## 2026-10-27 — gap-closure run, 09-15, 09-16

- A serial monitor must open the port in the idle line state. Asserted DTR/RTS hold an
  ESP32-S3 in reset, so a monitor that omits the flags captures nothing while the port
  still looks healthy.
- A command that must target one of several interfaces must resolve it explicitly, fail
  closed on ambiguity, and pass the same resolved identity to both the flash and the
  capture. An implicit choice can flash one interface and monitor the other.

## 2026-10-27 — gap-closure run, 09-14

- A keyword scan must cover identifier characters on both sides of the keyword.
  Matching only an adjacent separator misses camelCase and snake_case assignments such
  as `secretKey:` and `secret_key =`, so the credential the rule forbids reaches the log.

## 2026-10-27 — gap-closure run, 09-13

- A bounded wait must validate its duration before it starts the child. `select` raises on
  a non-finite or overflowing timeout, not the validator, so a NaN or infinity reaches the
  read loop as a traceback and a leaked child unless the check runs first.
- A child started by a helper must be owned in a `finally`. Every exceptional path that
  skips the happy-path kill leaves the serial port busy and the `Popen` unreaped, so the
  cleanup belongs in the block that also closes the descriptor, not in the happy path.

## 2026-10-27 — gap-closure run, 09-11

- A wrapper's flag is not the wrapped tool's flag: `hw-flash` told the agent to pass `-b`,
  which is the monitor flag the helper rejects. The skill must name the helper option, and
  a test must assert the forwarded argv so the two cannot drift.
- An announced command is only the executed command when every conditional segment is named
  in the same sentence. Naming `--env` alone left the baud conditional unannounced, so the
  gate could announce a baud the run never passed.

## 2026-10-27 — gap-closure run, 09-10

- A TTY-gated tool needs a pseudo-terminal, and the test must assert the child sees a TTY:
  a pipe is not a terminal, so a capture built on `subprocess.PIPE` reports
  `capture unavailable` on every run. The regression proof is the same child failing when
  its stdio is a pipe.
- A fail-closed scan must cover quoted, spaced, authorization and space-separated forms,
  and it must accept false positives. A narrower regex silently persists exactly the
  credential the rule forbids.
- A prose path guarantee must match the directory-descriptor operations the helper actually
  performs: `O_NOFOLLOW`, `dir_fd` and an exclusive temporary file are the promise, and a
  path-based `lstat` loop is not the same thing.

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

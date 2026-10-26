---
phase: 09-agent-workflow-and-skills
verified: 2026-10-26T23:42:40Z
status: gaps_found
score: 20/22 must-haves verified
covered_files: [".agents/skills/_shared/guardrails.md", ".agents/skills/hw-flash/CHANGELOG.md", ".agents/skills/hw-flash/LESSONS.md", ".agents/skills/hw-flash/SKILL.md", ".claude/skills/_shared/guardrails.md", ".claude/skills/hw-flash/CHANGELOG.md", ".claude/skills/hw-flash/LESSONS.md", ".claude/skills/hw-flash/SKILL.md", ".planning/phases/09-agent-workflow-and-skills/09-01-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-01-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-02-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-02-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-03-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-03-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-04-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-04-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-05-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-05-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-06-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-06-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-07-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-07-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-08-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-08-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-09-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-09-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-10-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-10-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-REVIEW-DISPOSITION.md", "AGENTS.md", "generated.skills.manifest", "scripts/affected.py", "scripts/serial_capture.py", "scripts/tests/test_affected.py", "scripts/tests/test_serial_capture.py"]
covered_digest: "v3:sha256:522c6b04bb555ad4165f213ffd4cbcaa2c0e7ca5c0eec767d55454f835343f98"
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: gaps_found
  previous_score: 14/16
  gaps_closed:
    - "The `hw-flash` bounded capture now runs through the tested PTY helper and writes `.skill-state/logs/<id>.log` on the declared-baud path; the piped-monitor snippet is gone."
    - "`find_credential` now matches the six shapes the earlier review executed, and a match writes nothing."
    - "The shared guardrails again forbid a credential in the state file or any log outside the one scoped capture exception."
    - "`AGENTS.md` names every Phase 9 no-build-impact path, including `scripts/serial_capture.py`."
  gaps_remaining:
    - "The fail-closed baud branch is not wired to the helper: `hw-flash` says `-b <n>` while the helper accepts `--baud` (CR-03)."
    - "The credential scan still misses ordinary password assignment forms (WR-12)."
  regressions: []
gaps:
  - truth: "`hw-flash` wires the user-resolved baud into the shipped capture helper, so the declared `monitor_speed` is used and an absent key never falls through to PlatformIO's 9600."
    status: failed
    reason: "The only executable capture command is `uv run scripts/serial_capture.py --id <id> [--env <env>] [--seconds 20]`; it never passes `--baud`. The prose tells the agent to pass `-b <n>`, which is a monitor flag the helper's argparse rejects. In the absent-`monitor_speed` branch the agent either omits the baud (the monitor inherits PlatformIO's forbidden 9600) or appends `-b` and the CLI exits 2. The gate also announces `Baud: <n>`, so the announced capture is not the executed capture. Reproduced: `serial_capture.py --help` lists `--baud`, not `-b` (CR-03)."
    artifacts:
      - path: ".claude/skills/hw-flash/SKILL.md"
        issue: "Lines 67 and 108 announce a capture command without `--baud`; lines 43-44 and 143-145 say to pass `-b <n>`."
      - path: ".agents/skills/hw-flash/SKILL.md"
        issue: "Generated mirror carries the same wrong flag."
      - path: "scripts/serial_capture.py"
        issue: "The helper exposes `--baud` (line 288), which appends `-b` to the monitor; no caller in the skill uses it."
    missing:
      - "Add `[--baud <n>]` to both announced capture commands and state that the helper appends `-b <n>` to the monitor."
      - "Update the 'nothing else is conditional' sentence to name `--env` and `--baud`."
      - "Add a `_build_command` test that asserts the `-b` argv, then regenerate the mirror."
  - truth: "No skill writes a credential to a log; the shared guardrails' secrets rule holds across every implemented skill."
    status: failed
    reason: "The sole permitted write is conditioned on a scan that finds no password assignment, but `find_credential` returns False for `password is hunter2`, `userpassword = hunter2`, `passphrase = hunter2` and `pwd = hunter2`. The long-form branch requires six non-space characters immediately after the whitespace, so the copula form misses; the leading `(?<![a-z0-9])` rejects a keyword preceded by a letter; `passphrase` and `pwd` are absent from the keyword set. Verified by executing the shipped regex. The same class of miss was CR-02 (WR-12)."
    artifacts:
      - path: "scripts/serial_capture.py"
        issue: "`_KEYWORDS` (line 82) and `CREDENTIAL` (lines 84-88) miss the four forms above."
      - path: ".claude/skills/_shared/guardrails.md"
        issue: "The exception promises a scan for a token, secret, password or API-key assignment; the implementation does not cover these password assignments."
      - path: ".agents/skills/_shared/guardrails.md"
        issue: "Generated mirror carries the same policy text."
    missing:
      - "Widen `_KEYWORDS` to `pass(?:word|wd|phrase)` and allow the copula in the long-form branch."
      - "Add the four shapes to `REVIEW_SHAPES` and the credential suite."
      - "Widen the guardrails sentence in the same change and regenerate the mirror."
  - truth: "The helper's CLI rejects a non-finite `--seconds` as a usage error instead of crashing with a traceback."
    status: partial
    reason: "`if args.seconds <= 0` is False for NaN and infinity, so `select.select` receives a non-finite timeout. Reproduced outside the sandbox: `capture_pty(..., float('nan'))` raises `ValueError: Invalid value NaN`, and `float('inf')` raises `OverflowError: timestamp out of range`; neither is `CaptureFailed` or `CheckError`, so `main` exits with a traceback and no cleanup (WR-10)."
    artifacts:
      - path: "scripts/serial_capture.py"
        issue: "Lines 310-311 validate only `<= 0`; the read loop at 143-153 does not catch non-finite `select` failures."
    missing:
      - "Reject a non-finite `--seconds` with `math.isfinite` and a `CheckError`, and consider a sane upper bound."
  - truth: "An exception in the read loop always reaps the started monitor, so the serial port is never left busy."
    status: partial
    reason: "`_terminate` runs only on the deadline, the not-ready branch and the EOF/EIO refusal. Any other exception after `Popen` (`KeyboardInterrupt`, the WR-10 `ValueError`/`OverflowError`, `MemoryError`) propagates while the `finally` closes only the master fd; the child is neither killed nor waited (WR-11)."
    artifacts:
      - path: "scripts/serial_capture.py"
        issue: "The `finally` at lines 165-166 closes the master but does not kill or reap the child."
    missing:
      - "Reap the child in the `finally` block (kill if still running, then wait) and keep the early-return paths."
advisory: []
human_verification:
  - test: "With a board connected, run `uv run scripts/serial_capture.py --id 1_3-police-flasher --seconds 20` after a confirmed upload and inspect the exit line and the ignored log."
    expected: "Exit 0, a `CAPTURED — N bytes captured` line naming `.skill-state/logs/1_3-police-flasher.log`, and a log whose bytes are the raw device output."
    why_human: "The automated suite uses a fake `sys.executable -c` child on a PTY; the real `pio device monitor` needs a board and a serial port. The declared-baud path is the only capture branch that is not blocked by CR-03."
---

# Phase 9: Agent Workflow and Skills Verification Report

**Phase Goal:** Seven versioned agent skills exist, with `new-homework` and `hw-build` fully usable in guided and one-shot modes. The Phase 4.2 friction log must justify the intake, build, and report skills.
**Verified:** 2026-10-26T23:42:40Z
**Status:** gaps_found
**Re-verification:** Yes — after gap-closure plan 09-10 and the incremental review of that change set

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | A capture started by `capture_and_store` returns the exact bytes a child writing to a PTY produced, including CR, LF, NUL and 0xff; the child sees stdin and stdout as TTYs, and the same child under a pipe exits non-zero. | ✓ VERIFIED | `scripts/serial_capture.py:122-166`; `CapturePtyTests.test_capture_preserves_every_byte_and_sees_a_tty` and `test_a_pipe_capture_would_fail_the_same_child` pass outside the sandbox (26/26). |
| 2 | A capture refuses with `capture unavailable` when the command cannot start, exits before the bound, or reaches the bound with zero bytes; reaching the bound with bytes is the success path. | ✓ VERIFIED | `capture_pty` raises on start/early-exit (`:126-163`); `capture_and_store` refuses empty bytes (`:255-256`); `main` prefixes `capture unavailable` (`:315-330`). Tests `test_capture_fails_on_an_early_{zero,nonzero}_exit`, `test_an_empty_child_writes_nothing`, `test_capture_stops_at_the_deadline` pass. The zero-byte branch lives in `capture_and_store`, not `capture_pty` (IN-08, wording only). |
| 3 | `find_credential` matches the six review shapes, does not match a benign boot log, and a match writes nothing. | ✓ VERIFIED | `scripts/serial_capture.py:82-103`; `CredentialScanTests` (all six shapes, `passwd`, `PASSWORD`, `password abc123`, `secret is`, boot log) pass; `test_a_credential_child_writes_nothing`. Narrowly true; the broader policy fails at truth 17. |
| 4 | `write_log_atomically` writes under the resolved root, refuses a symlinked `.skill-state`, `logs` or log component, leaves no temporary file, and replaces rather than appends. | ✓ VERIFIED | `scripts/serial_capture.py:202-247` uses `O_DIRECTORY | O_NOFOLLOW` and `dir_fd`; `AtomicLogWriteTests` (seven cases) pass. |
| 5 | Two concurrent atomic writes leave exactly one whole payload and no temporary file. | ✓ VERIFIED | `test_concurrent_writes_leave_one_whole_payload` passes. |
| 6 | `hw-flash` invokes `scripts/serial_capture.py` instead of a piped monitor, normalizes `monitor_speed` with `int(str(value))`, announces the conditional `-e env` segment, and its outcome table no longer calls the designed bound a timeout. | ✓ VERIFIED | `SKILL.md:67,108` invoke the helper; `:37` normalizes; `:71-72` states the conditional `-e`; `:177-182` has `Upload succeeded, capture failed`. No `stdout=subprocess.PIPE` in the skill. |
| 7 | The shared guardrails' general prohibition again covers the state file and any log outside the one scoped capture exception, and the exception states the fail-closed scan shapes. | ✓ VERIFIED | `_shared/guardrails.md:50-64` says "or any log" and enumerates optional separator, quoting, authorization and the six-character space-separated form. |
| 8 | The regenerated mirror and `generated.skills.manifest` match the canonical tree under `gen_skills.py --check`, and `scripts/affected.py` maps `scripts/serial_capture.py` to no build impact. | ✓ VERIFIED | `gen_skills.py --check` exits 0 with every record `UNCHANGED`; canonical and mirror bodies compare equal; `scripts/affected.py:123` and `test_affected.py:251`. |
| 9 | Seven project-local skills exist, each with `SKILL.md`, `CHANGELOG.md` and `LESSONS.md`; `new-homework` and `hw-build` are active and four skills are stubs. | ✓ VERIFIED | 21 skill files; `hw-build`, `hw-flash`, `new-homework` are active; `course-index`, `hw-report`, `schematic`, `simulate` carry `status: stub`. Version deviation: `new-homework` is `0.2` (see Deviations). |
| 10 | The Phase 4.2 friction log justifies the intake, build and report skills. | ✓ VERIFIED | `04.2-FRICTION-LOG.md` has `F-01` (intake/scaffold), `F-03`–`F-05` (build), `F-11`–`F-13` (report). |
| 11 | `new-homework` supports guided and one-shot modes with an adaptive bank in the order mode, board, framework, language, specification, simulation, tests, deliverables. | ✓ VERIFIED | `SKILL.md:47-49`; `references/question-bank.md` has the eight `##` sections in order; dry-run Legs 1–3. |
| 12 | Guided mode follows explain → code → run → questions at block granularity, pauses with `[Продовжити | Поясни глибше | Стоп]`, and deepening never advances the block. | ✓ VERIFIED | `new-homework/SKILL.md` block loop; dry-run Leg 2. |
| 13 | Both modes checkpoint after intake, after code and after report; guardrails apply. | ✓ VERIFIED | `references/state-file.md:69-99`; dry-run Legs 1–3. |
| 14 | Spec-vs-best-practice conflicts and ambiguity produce a recommended assumption transcribed into the report. | ✓ VERIFIED | `guardrails.md:34-48`; `A-01` in the dry run and report excerpt. |
| 15 | `hw-build` runs the real target build and native suite, caps each leg at two repairs, preserves warnings, never commits/resets, and escalates with evidence. | ✓ VERIFIED | `hw-build/SKILL.md`; `references/repair-loop.md`; dry-run Legs 4–5. |
| 16 | `hw-flash` prints the board, environment and exact upload command, requires a literal `так`/`yes`, runs no upload on a non-affirmative answer, and never pre-approves `upload`. | ✓ VERIFIED | `SKILL.md:50-101`; dry-run Leg 6. |
| 17 | `hw-flash` resolves the baud from the project fail-closed; the real homework resolves 115200 and an absent key stops before the monitor. | ✓ VERIFIED | `SKILL.md:35-44`; `platformio.shared.ini` declares 115200; `pio project config` resolves it; the absent-key branch stops and asks. |
| 18 | `hw-flash` wires the user-named baud into the shipped capture helper so the announced baud is the executed baud. | ✗ FAILED | The helper exposes `--baud`; the skill says `-b <n>` and never includes `--baud` in the capture command (CR-03). See gap 1. |
| 19 | No skill writes a credential to a log; the guardrails' secrets rule holds across every implemented skill. | ✗ FAILED | `find_credential` misses `password is hunter2`, `userpassword = hunter2`, `passphrase = hunter2`, `pwd = hunter2`; those bytes would be persisted (WR-12). See gap 2. |
| 20 | `scripts/gen_skills.py` is the only mirror writer, maintains the manifest, supports `--check`, and the committed tree is in sync. | ✓ VERIFIED | `gen_skills.py --check` exit 0; 25 mirror files, 25 manifest entries, no self-entry. |
| 21 | The drift gate is wired and `affected.py`/`.gitignore`/`AGENTS.md` cover the Phase 9 paths. | ✓ VERIFIED | `.pre-commit-config.yaml:229-239`; `.gitignore:83,270-272`; `affected.py:99-123`; the `AGENTS.md` no-build-impact paragraph names every path. |
| 22 | The `.claude/CLAUDE.md` `GSD:skills` block lists exactly seven skills and the decision row records the canonical/mirror split. | ✓ VERIFIED | Seven rows; `docs/decisions/README.md:33` dated `costly`/`accepted`. |
| 23 | The dry-run transcript records the guided, one-shot, conflict, build-repair and flash-gate legs and contains no credential or private absolute path. | ✓ VERIFIED | `09-DRY-RUN.md` Legs 1–6; no `/Users/`, `/home/`, token or password assignment. |
| 24 | The full local gate is green. | ✓ VERIFIED (20/22 truths) | `pre-commit run --all-files` exit 0 (14 hooks); `check_metadata.py` PASS; `python3 -m unittest discover scripts/tests` 403 OK; `pio test -d tests -e native` 73/73; `gen_views.py --all --check` and `gen_skills.py --check` exit 0. |

**Score:** 20/22 truths verified (0 present, behavior-unverified). Rows 18 and 19 are the two failed must-haves. Rows 3 and 6 are narrow task-level truths that pass; the broader failures are recorded at 18 and 19.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `scripts/serial_capture.py` | PTY capture, scan, atomic write, CLI | ✓ VERIFIED | Substantive, stdlib-only, 5 public callables; tests drive the shipped path. |
| `scripts/tests/test_serial_capture.py` | PTY, scan, write tests | ✓ VERIFIED | 26 tests, no skip; 26/26 pass outside the sandbox. |
| `scripts/affected.py`, `scripts/tests/test_affected.py` | Helper in no-build-impact policy | ✓ VERIFIED | Both entries present. |
| `.claude/skills/hw-flash/SKILL.md` | Helper invocation, corrected contract | ⚠️ PARTIAL | Helper wired, piped snippet gone; the baud flag is wrong (CR-03). |
| `.claude/skills/hw-flash/CHANGELOG.md`, `LESSONS.md` | Dated 2026-10-27 entries | ✓ VERIFIED | Both present. |
| `.claude/skills/_shared/guardrails.md` | Restored log prohibition and scan shapes | ✓ VERIFIED | Text present; implementation gap at WR-12. |
| `AGENTS.md` | No-build-impact paragraph names every Phase 9 path | ✓ VERIFIED | `.claude/`, `.agents/`, `.skill-state/`, both ledgers, both scripts. |
| `.agents/skills/**`, `generated.skills.manifest` | Regenerated projections | ✓ VERIFIED | 25 files, 25 entries, all `UNCHANGED`; bodies equal. |
| `09-REVIEW-DISPOSITION.md` | Findings recorded fixed | ✓ VERIFIED | Eleven fixed rows, `WR-09` added; the later review added nine open rows, so the recorded counts are `open: 14`, `total: 25` (supersedure, not drift). |
| Seven skill directories | Three files each, versioned, four stubs | ✓ VERIFIED | 21 files; versions as above. |
| `04.2-FRICTION-LOG.md` | Intake, build and report entries | ✓ VERIFIED | `F-01`, `F-03`–`F-05`, `F-11`–`F-13`. |
| `09-DRY-RUN.md` | Phase evidence transcript | ✓ VERIFIED | Legs 1–6; sanitized. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| PTY master | `capture_pty` → `find_credential` → `write_log_atomically` → ignored log | `scripts/serial_capture.py` | ✓ WIRED | Tests exercise the exact path. |
| `.claude/skills/hw-flash/SKILL.md` | `uv run scripts/serial_capture.py` → `capture_and_store` | helper CLI | ✓ WIRED | The command is present; `--baud` is not (CR-03). |
| `_shared/guardrails.md` policy | helper scan → six review fixtures | `find_credential` | ✓ WIRED | Six shapes pass; four more shapes miss (WR-12). |
| `.claude/skills/**` | `gen_skills.py` → `.agents/skills/**` → manifest → `gen-skills-check` | generator | ✓ WIRED | `--check` exit 0; hook present. |
| `affected.py` `NO_BUILD_IMPACT` | `NoBuildImpactTests.NO_BUILD_IMPACT_PATHS` | test tuple | ✓ WIRED | Same path in both. |
| `homeworks/<id>/platformio.ini` | `pio project config` → declared 115200 | shared ini inheritance | ✓ WIRED | Real homework resolves 115200. |
| User-named baud | helper `--baud` → monitor `-b` | `_build_command` | ✗ NOT_WIRED | `_build_command` supports `--baud`, but no skill command passes it. |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| `scripts/serial_capture.py` | raw bytes | PTY master from the child | Yes — exact `bytes(range(256))` | ✓ FLOWING |
| `write_log_atomically` | log bytes | scanned capture bytes | Yes — log equals payload | ✓ FLOWING |
| `gen_skills.py` | mirror bytes | canonical `.claude/skills/**` | Yes | ✓ FLOWING |
| `generated.skills.manifest` | `sha256`/`bytes` | generator transform | Yes — 25 entries | ✓ FLOWING |
| `hw-flash` baud branch | `user_baud` | `monitor_speed` / user answer | No — the helper never receives it | ✗ DISCONNECTED |
| Credential scan | device bytes | `find_credential` | Partial — four password forms pass unscanned | ⚠️ STATIC |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| PTY capture suite | `python3 -m unittest scripts.tests.test_serial_capture -v` (outside sandbox) | `Ran 26 tests … OK` | ✓ PASS |
| PTY denial is environmental | same command in the sandbox | `out of pty devices`; retried outside the sandbox | ✓ environmental |
| Full Python suite | `python3 -m unittest discover scripts/tests` | `Ran 403 tests … OK` | ✓ PASS |
| Native suite | `pio test -d tests -e native` | 73/73 succeeded | ✓ PASS |
| Metadata contract | `uv run scripts/check_metadata.py` | `PASS: metadata contract satisfied` | ✓ PASS |
| Generated views | `uv run scripts/gen_views.py --all --check` | all `UNCHANGED` | ✓ PASS |
| Skills mirror | `uv run scripts/gen_skills.py --check` | all `UNCHANGED` | ✓ PASS |
| Full pre-commit gate | `pre-commit run --all-files` (outside sandbox) | exit 0, 14 hooks, no modified file | ✓ PASS |
| Credential misses | execute `find_credential` on the four forms | `password is hunter2`, `userpassword = hunter2`, `passphrase = hunter2`, `pwd = hunter2` all False | ✗ FAIL (WR-12) |
| Non-finite duration | `capture_pty(..., float("nan"))` / `float("inf")` | `ValueError: Invalid value NaN` / `OverflowError: timestamp out of range` | ✗ FAIL (WR-10) |
| Baud flag surface | `scripts/serial_capture.py --help`; grep `--baud` in the skill | helper has `--baud`; skill has none, only `-b` | ✗ FAIL (CR-03) |

### Probe Execution

No `scripts/*/tests/probe-*.sh` probes are declared for this phase; the D-22 dry run is the phase's behavioral evidence.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| FLOW-01 | 09-01, 09-06, 09-07, 09-09, 09-10 | Seven skills at version 0.1; `new-homework` and `hw-build` implemented first | ✓ SATISFIED (with version deviation) | Seven directories; six at 0.1, `new-homework` at 0.2; mirror, ledger and adapter block wired. |
| FLOW-02 | 09-03, 09-08, 09-09, 09-10 | Guided + one-shot with an eight-topic adaptive bank | ✓ SATISFIED | Bank order and dry-run Legs 1/3. |
| FLOW-03 | 09-03, 09-08, 09-09, 09-10 | Explain → code → run → questions, pause per block, deepen when stuck | ✓ SATISFIED | Block loop and dry-run Leg 2. |
| FLOW-04 | 09-02, 09-03, 09-08, 09-09, 09-10 | Checkpoints after intake/code/report; guardrails always apply | ✓ SATISFIED | State schema and guardrails. |
| FLOW-05 | 09-03, 09-08, 09-09, 09-10 | Conflict/ambiguity with a recorded recommended assumption transcribed into the report | ✓ SATISFIED | `A-01` and report excerpt. |
| FLOW-06 | 09-04, 09-08, 09-09, 09-10 | Build repaired at most twice, then explained and escalated | ✓ SATISFIED | `repair-loop.md` and dry-run Leg 5. |
| FLOW-07 | 09-01, 09-02, 09-05, 09-08, 09-09, 09-10 | `hw-flash` requires explicit confirmation and captures serial logs; four thin stubs | ✗ BLOCKED | Consent gate and stubs verified; the capture is unsafe/incomplete in the baud branch (CR-03) and the credential scan still misses ordinary password assignments (WR-12). |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `.claude/skills/hw-flash/SKILL.md` (mirror too) | 67, 108, 143-145 | Capture command omits `--baud`; prose says `-b <n>` | 🛑 BLOCKER | The announced baud is not the executed baud; the absent-key branch either exits 2 or runs at 9600. |
| `scripts/serial_capture.py` | 82-88 | Credential regex misses `password is …`, `userpassword = …`, `passphrase = …`, `pwd = …` | 🛑 BLOCKER | A credential can be written under the sole permitted capture exception. |
| `scripts/serial_capture.py` | 310-311, 143-153 | `--seconds` accepts NaN/infinity; traceback and unreaped child | ⚠️ WARNING | A usage error surfaces as a traceback and can leave the monitor running. |
| `scripts/serial_capture.py` | 165-166 | `finally` closes the master but does not kill/reap the child | ⚠️ WARNING | A busy serial port and a ResourceWarning after an unexpected exception. |
| `scripts/serial_capture.py` | 90, 204, 301-307 | `^…$` validators accept a trailing newline; env accepts a leading `-` | ⚠️ WARNING | The validators do not implement the canonical shape (IN-09). |
| `scripts/tests/test_serial_capture.py` | 292-319, 230-251 | No `_build_command`, CLI payload or concurrent-reader test; concurrency torn-read unproven | ℹ️ INFO | The exact place CR-03 lives is untested (IN-06). |
| `scripts/serial_capture.py` | 202-247 | The write does not enforce the scan that gates it | ℹ️ INFO | Holds only while the sole caller scans first (IN-07). |
| `.planning/.../09-10-PLAN.md` | 35 | Zero-byte refusal attributed to `capture_pty`, implemented in `capture_and_store` | ℹ️ INFO | Contract wording mismatch; CLI behavior correct (IN-08). |
| `scripts/tests/test_affected.py` | 236-252 | `.skill-state/` has no test entry | ℹ️ INFO | A future drop of that rule would not fail (IN-10). |

### Human Verification Required

| Test | Expected | Why Human |
|------|----------|-----------|
| With a board connected, run `uv run scripts/serial_capture.py --id 1_3-police-flasher --seconds 20` after a confirmed upload. | Exit 0, `CAPTURED — N bytes captured`, and a raw device log under `.skill-state/logs/`. | The suite uses a fake PTY child; the real monitor needs hardware and a serial port. Run only after CR-03 is fixed if the absent-baud branch is exercised. |

### Deviations

- **`new-homework` is version 0.2, not 0.1.** Quick task `261026-x78` changed the ESP-IDF template to pure C and bumped the skill with a dated changelog. Six skills remain at 0.1. The roadmap SC1 literal is no longer true for one skill; the intent — a versioned skill — holds, and the 0.2 contract is internally consistent. Carried forward from the previous verification; if the literal must be enforced, record an override or amend SC1.
- **The disposition counts are `open: 14`, `total: 25`, not the plan's `open: 5`, `total: 16`.** The incremental review of the 09-10 change set added nine findings (`CR-03`, `WR-10`–`WR-12`, `IN-06`–`IN-10`) after the plan ran. The record reflects the current tree honestly; the plan's exact counts are superseded, not silently wrong.

### Gaps Summary

Plan 09-10 genuinely closed the two previous blockers for the main path. The piped-monitor snippet is gone: `scripts/serial_capture.py` allocates a PTY, sets the slave to raw mode, preserves `bytes(range(256))`, refuses an early exit and an empty capture, scans the bytes before any file exists, and writes the log through `O_DIRECTORY | O_NOFOLLOW` descriptors with `dir_fd`. The suite proves the pipe regression cannot return (26/26 pass outside the sandbox), the mirror and manifest are `UNCHANGED`, `scripts/serial_capture.py` maps to no build, `AGENTS.md` and the guardrails were corrected, and the full gate is green (403 Python tests, 73 native cases, metadata, views, skills, 14 pre-commit hooks).

Two must-haves still fail in the shipped, active `hw-flash` path. First, the skill never passes the user-resolved baud to the helper: the helper takes `--baud`, the skill says `-b <n>`, and the announced capture command has neither. In the absent-`monitor_speed` branch the run either exits 2 or silently monitors at PlatformIO's forbidden 9600, and the announced `Baud:` line is not the executed one. Second, the credential scan is still narrower than the policy it claims to implement: `password is hunter2`, `userpassword = hunter2`, `passphrase = hunter2` and `pwd = hunter2` all pass the gate, so a credential can be persisted under the only permitted write. These are the same classes as the prior CR-02 and the prior truth-10 failure, so the phase goal is not yet fully achieved. The remaining review findings (non-finite `--seconds`, unreaped child, trailing-newline validators, test gaps) are warnings or informational and do not independently block the goal.

---

_Verified: 2026-10-26T23:42:40Z_
_Verifier: Claude (gsd-verifier)_

---
phase: 09-agent-workflow-and-skills
verified: 2026-10-27T12:22:14Z
status: gaps_found
score: 41/44 must-haves verified
covered_files: [".agents/skills/_shared/guardrails.md", ".agents/skills/hw-build/SKILL.md", ".agents/skills/hw-flash/SKILL.md", ".agents/skills/new-homework/SKILL.md", ".claude/CLAUDE.md", ".claude/skills/_shared/guardrails.md", ".claude/skills/course-index/SKILL.md", ".claude/skills/hw-build/CHANGELOG.md", ".claude/skills/hw-build/LESSONS.md", ".claude/skills/hw-build/SKILL.md", ".claude/skills/hw-build/references/repair-loop.md", ".claude/skills/hw-flash/CHANGELOG.md", ".claude/skills/hw-flash/LESSONS.md", ".claude/skills/hw-flash/SKILL.md", ".claude/skills/hw-report/SKILL.md", ".claude/skills/new-homework/CHANGELOG.md", ".claude/skills/new-homework/LESSONS.md", ".claude/skills/new-homework/SKILL.md", ".claude/skills/new-homework/references/question-bank.md", ".claude/skills/new-homework/references/state-file.md", ".claude/skills/schematic/SKILL.md", ".claude/skills/simulate/SKILL.md", ".planning/phases/09-agent-workflow-and-skills/09-01-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-01-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-02-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-02-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-03-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-03-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-04-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-04-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-05-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-05-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-06-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-06-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-07-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-07-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-08-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-08-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-09-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-09-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-10-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-10-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-11-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-11-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-12-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-12-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-13-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-13-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-14-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-14-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-15-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-15-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-16-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-16-SUMMARY.md", ".pre-commit-config.yaml", "AGENTS.md", "generated.skills.manifest", "scripts/affected.py", "scripts/gen_skills.py", "scripts/serial_capture.py", "scripts/tests/test_affected.py", "scripts/tests/test_serial_capture.py"]
covered_digest: "v3:sha256:14a20cf7d9a03b66342ff097fbfea188eb79f986462ede1268963341eaaa6482"
behavior_unverified: 1
overrides_applied: 0
re_verification:
  previous_status: human_needed
  previous_score: 31/31
  gaps_closed:
    - "09-15 automated half of G-09-1: every monitor argv now carries -p <port> plus --dtr 0 --rts 0; resolve_port is fail-closed on zero or several USB serial devices; --port is validated and forwarded; the payload reports port, VID:PID and baud while the log stays raw device bytes."
    - "09-16 contract half of G-09-1: hw-flash resolves exactly one port before the consent gate and passes the same path to --upload-port and --port, and documents the native USB-Serial-JTAG versus CH343 paths."
  gaps_remaining:
    - "Truth 19 / review CR-01: find_credential misses a space-separated compound keyword (`SECRET KEY: hunter2`), so the guardrails' secrets rule does not hold across every assignment shape."
    - "Truth 42 / review WR-03: hw-flash/SKILL.md restates the same-port rule that the shared guardrails own; plan 09-16 required a reference, not a restatement."
    - "Truth 38: the hardware capture remains unproven in this environment; no board is attached and the sandbox refuses /dev/cu.*."
  regressions: []
gaps:
  - truth: "Truth 19 / RR-CR-01 lineage: no skill writes a credential to a log; the guardrails' secrets rule holds across every implemented skill."
    status: failed
    reason: "Direct execution: find_credential(b'SECRET KEY: hunter2') and find_credential(b'secret key = hunter2') both return False, although .claude/skills/_shared/guardrails.md names a 'token, secret, password, passwd, passphrase, pwd, or API-key assignment' as refused. A firmware line of that shape would be written to .skill-state/logs/<id>.log. Recorded by review CR-01."
    artifacts:
      - path: "scripts/serial_capture.py"
        issue: "The assignment branch admits an identifier connector but no whitespace connector between the words of a compound keyword."
    missing:
      - "Admit a space-separated compound keyword (for example `secret[\\s_-]?key`) in the assignment branch without letting `auth mode = WPA2` start matching."
      - "Add `SECRET KEY: hunter2` and `secret key = hunter2` to the positive fixtures and keep the pinned benign negatives."
  - truth: "Truth 42 / 09-16 must-have: the shared guardrails carry the same-port rule once, so no skill restates it."
    status: failed
    reason: ".claude/skills/hw-flash/SKILL.md:54-55 and :86 restate the normative same-port rule already owned by .claude/skills/_shared/guardrails.md:17-21. Plan 09-16 task H explicitly required 'Do not restate this rule in the skill; the skill points at the shared file'; review WR-03 records the same finding."
    artifacts:
      - path: ".claude/skills/hw-flash/SKILL.md"
        issue: "Lines 54-55 and 86 restate the shared same-resolved-port rule."
      - path: ".agents/skills/hw-flash/SKILL.md"
        issue: "The generated mirror carries the same restatement; regenerate after the canonical edit."
    missing:
      - "Replace the normative sentence in the skill with a pointer to the shared guardrails, keeping only the operational steps (pio device list, hwid filter, single-candidate choice, --port question)."
      - "Regenerate the mirror with `uv run scripts/gen_skills.py`."
deferred: []
advisory: []
behavior_unverified_items:
  - truth: "Truth 38 / 09-15 must-have: with the board attached, `uv run scripts/serial_capture.py --id 1_3-police-flasher --seconds 20` exits 0, prints `CAPTURED — N bytes captured` naming `.skill-state/logs/1_3-police-flasher.log`, and the log holds device bytes."
    test: "Connect the board, upload the firmware, then run `uv run scripts/serial_capture.py --id 1_3-police-flasher --seconds 20`; press RESET during the window because the firmware logs only in `setup()`."
    expected: "Exit 0, a `CAPTURED` line naming the ignored log and the resolved port/VID:PID/baud, and a log holding the raw device bytes (the boot line in the measured run)."
    why_human: "No board is attached in this environment and the command sandbox refuses /dev/cu.*; the automated suite drives a fake `sys.executable` child on a PTY."
human_verification:
  - test: "With the board attached after a confirmed upload, run `uv run scripts/serial_capture.py --id 1_3-police-flasher --seconds 20` and inspect the exit line and the ignored log."
    expected: "Exit 0, a `CAPTURED — N bytes captured from <port> (USB VID:PID=<vid>:<pid>) at <baud> baud` line naming `.skill-state/logs/1_3-police-flasher.log`, and a log holding the raw device bytes."
    why_human: "Hardware and a serial port are required; the sandbox refuses /dev/cu.* and no board is attached."
coincidental_reliance_items: []
---

# Phase 9: Agent Workflow and Skills Verification Report

**Phase Goal:** Seven versioned agent skills exist, with `new-homework` and `hw-build` fully usable in guided and one-shot modes.
**Friction-log justification:** The Phase 4.2 log must contain at least one entry for the intake, build, or report workflow; otherwise the corresponding skill is not written.
**Verified:** 2026-10-27T12:22:14Z
**Status:** gaps_found
**Re-verification:** Yes — after the G-09-1 gap-closure plans 09-15 and 09-16

## Goal Achievement

### Observable Truths

#### Prior must-haves (regression check, truths 1–31)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `capture_and_store` returns the exact bytes a child wrote to a PTY, including CR, LF, NUL and 0xff; the child sees stdin/stdout as TTYs and a pipe child fails. | ✓ VERIFIED | `test_capture_preserves_every_byte_and_sees_a_tty`, `test_a_pipe_capture_would_fail_the_same_child` pass in the 62-test capture suite. |
| 2 | A capture refuses with `capture unavailable` when the command cannot start, exits before the bound, or produces zero bytes; reaching the bound with bytes succeeds. | ✓ VERIFIED | `capture_pty` raises on start/early exit; `capture_and_store` refuses empty bytes; `test_capture_fails_when_the_command_cannot_start`, `test_capture_fails_on_an_early_zero_exit`, `test_capture_stops_at_the_deadline` pass. |
| 3 | `find_credential` matches the six review shapes, the four ordinary password assignments and the five identifier-suffixed assignments, and does not match the pinned benign set. | ✓ VERIFIED | `CredentialScanTests` (12 tests) pass; direct probe confirms `secretKey`, `secret_key`, `passwordHash`, `password =`, `password is`, `userpassword =`, `api key =` match and the four benign negatives return False. |
| 4 | `write_log_atomically` anchors under the resolved root, refuses a symlinked `.skill-state`/`logs`/log, leaves no temporary file, and replaces rather than appends. | ✓ VERIFIED | Seven `AtomicLogWriteTests` pass. |
| 5 | Two concurrent atomic writes leave exactly one whole payload and no temporary file; a reader never sees a torn log. | ✓ VERIFIED | `test_concurrent_writes_leave_one_whole_payload`, `test_a_concurrent_reader_never_sees_a_torn_log` pass. |
| 6 | `hw-flash` invokes `scripts/serial_capture.py` instead of a piped monitor, normalizes `monitor_speed`, announces the conditional `-e` segment, and calls the bound a success. | ✓ VERIFIED | `.claude/skills/hw-flash/SKILL.md`; no `subprocess.PIPE` in the skill. |
| 7 | The shared guardrails forbid a credential in the state file or any log outside the one scoped capture exception, and state the fail-closed scan shapes. | ✓ VERIFIED | `.claude/skills/_shared/guardrails.md` "Secrets" section, mirrored in `.agents/skills/_shared/guardrails.md`. |
| 8 | The regenerated mirror and `generated.skills.manifest` match the canonical tree, and `scripts/affected.py` maps `scripts/serial_capture.py` to no build impact. | ✓ VERIFIED | `uv run scripts/gen_skills.py --check` exits 0 with every record `UNCHANGED`; `scripts/affected.py:123`. |
| 9 | Seven project-local skills exist, each with `SKILL.md`, `CHANGELOG.md` and `LESSONS.md`; three are active and four are stubs. | ✓ VERIFIED | Seven directories; `hw-build` (0.1), `hw-flash` (0.1), `new-homework` (0.2) active; `course-index`, `hw-report`, `schematic`, `simulate` `status: stub`. Version deviation: `new-homework` is 0.2, documented in its changelog. |
| 10 | The Phase 4.2 friction log justifies the intake, build and report skills. | ✓ VERIFIED | `.planning/phases/04.2-tracer-homework-1-3/04.2-FRICTION-LOG.md`: F-01, F-03–F-05, F-11–F-13 (intake, build, report). |
| 11 | `new-homework` supports guided and one-shot modes with an adaptive bank ordered mode, board, framework, language, specification, simulation, tests, deliverables. | ✓ VERIFIED | `references/question-bank.md` carries the eight `##` sections in exactly that order; `SKILL.md` "Intake" distinguishes guided and one-shot. |
| 12 | Guided mode follows explain → code → run → questions at block granularity and pauses with `[Продовжити | Поясни глибше | Стоп]`; deepening never advances. | ✓ VERIFIED | `.claude/skills/new-homework/SKILL.md:109-119`. |
| 13 | Both modes checkpoint after intake, after code and after report; guardrails always apply. | ✓ VERIFIED | `references/state-file.md` checkpoints `intake`/`code`/`report`; `SKILL.md:137-145`; the state file is written before each menu. |
| 14 | Spec-vs-best-practice conflicts and ambiguity produce a recommended assumption transcribed into the report. | ✓ VERIFIED | `guardrails.md` "Specification versus best practice" and "Ambiguity"; `SKILL.md` "Conflicts and ambiguity". |
| 15 | `hw-build` runs the real target build and native suite, caps each leg at two repairs, preserves warnings, never commits/resets, and escalates with evidence. | ✓ VERIFIED | `.claude/skills/hw-build/SKILL.md`; `references/repair-loop.md` counter and escalation payload. |
| 16 | `hw-flash` prints board, environment and exact upload command, requires a literal `так`/`yes`, runs no upload on a non-affirmative answer, and never pre-approves `upload`. | ✓ VERIFIED | `SKILL.md` "The consent gate" and "The upload"; `allowed-tools` carries no `upload`. |
| 17 | `hw-flash` resolves the baud from the project fail-closed; the real homework resolves 115200 and an absent key stops before the monitor. | ✓ VERIFIED | `SKILL.md` "Before the gate"; `platformio.shared.ini` and `homeworks/1_3-police-flasher/platformio.ini` inherit 115200. |
| 18 | `hw-flash` wires the user-resolved baud into the helper, so the announced baud is the executed baud. | ✓ VERIFIED | `SKILL.md` carries `[--baud <n>]` and says the helper appends `-b <n>`; `test_baud_is_forwarded_as_dash_b` passes. |
| 19 | **GAP 2 / RR-CR-01:** no skill writes a credential to a log; the guardrails' secrets rule holds across every implemented skill, including keyword-prefixed identifiers. | ✗ FAILED | Direct probe: `SECRET KEY: hunter2` and `secret key = hunter2` return False, although the guardrails policy names a "secret … assignment". Review CR-01. See Gaps Summary. |
| 20 | `scripts/gen_skills.py` is the only mirror writer, maintains the manifest, supports `--check`, and the committed tree is in sync. | ✓ VERIFIED | `gen_skills.py --check` exit 0. |
| 21 | The drift gate is wired and `affected.py`/`.gitignore`/`AGENTS.md` cover the Phase 9 paths. | ✓ VERIFIED | `.pre-commit-config.yaml` `gen-skills-check`; `AGENTS.md` no-build-impact paragraph. |
| 22 | The `.claude/CLAUDE.md` `GSD:skills` block lists exactly seven skills and the decision row records the canonical/mirror split. | ✓ VERIFIED | Seven rows in `.claude/CLAUDE.md`; `docs/decisions/README.md:33`. |
| 23 | The dry-run transcript records the guided, one-shot, conflict, build-repair and flash-gate legs and contains no credential or private absolute path. | ✓ VERIFIED | `09-DRY-RUN.md` Legs 0–6; grep for `/Users/`, `/home/`, `hunter2` returns nothing. |
| 24 | The full local gate is green. | ✓ VERIFIED | `pre-commit run --all-files` exit 0 (14 hooks); `python3 -m unittest discover scripts/tests` 439 tests OK; metadata, generated views and mirror checks exit 0. |
| 25 | Both announced capture commands carry `[--baud <n>]`, the prose names `--baud` as the helper option, and the conditional sentence names `[--env <env>]` and `[--baud <n>]`. | ✓ VERIFIED | `SKILL.md` consent-gate and capture sections. |
| 26 | `_build_command` forwards `-e` and `-b` only when supplied; the CLI `CAPTURED`/`REFUSED` payloads and a concurrent reader are pinned by tests. | ✓ VERIFIED | `BuildCommandTests`, `CliResultPayloadTests`, `test_a_concurrent_reader_never_sees_a_torn_log` pass. |
| 27 | The four ordinary password assignments match and the pinned benign set stays unmatched. | ✓ VERIFIED | `test_the_ordinary_password_assignments_match`, `test_an_ordinary_word_containing_a_keyword_does_not_match` pass; direct probe confirms. |
| 28 | The guardrails sentence names the widened shapes and the mirror/manifest are regenerated. | ✓ VERIFIED | `guardrails.md` names `secretKey`, `secret_key`, `passwordHash` and the 128-character bound; `gen_skills.py --check` `UNCHANGED`. |
| 29 | `--seconds` rejects NaN, infinity, a non-positive value and an oversized bound before `resolve_root`/`_build_command`/`Popen`, and `capture_pty` reaps the child on an escaping exception. | ✓ VERIFIED | `CliDurationTests`, `test_an_exception_escaping_the_loop_reaps_the_child` pass. |
| 30 | **CR-01 (post-verification review):** the connector ceiling is 128 characters, and 32-, 33- and 42-character keyword suffixes all match. | ✓ VERIFIED | `serial_capture.py` uses `[\\w.-]{0,128}`; `test_a_connector_longer_than_32_characters_matches` passes. |
| 31 | **WR-01 (post-verification review):** `auth mode = WPA2` is pinned as a benign negative and does not match. | ✓ VERIFIED | `test_an_ordinary_word_containing_a_keyword_does_not_match` iterates it; direct probe returns False. |

#### 09-15 gap-closure must-haves (truths 32–38)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 32 | Every monitor argv carries `-p` with the resolved device path plus `--dtr 0` and `--rts 0`. | ✓ VERIFIED | `scripts/serial_capture.py:520-534`; `test_the_monitor_opens_in_the_idle_line_state_with_an_explicit_port` passes. |
| 33 | When `--port` is omitted, exactly one USB serial device is selected; zero candidates or more than one candidate refuses with a `capture unavailable` reason that names every candidate and tells the user to pass `--port`. | ✓ VERIFIED | `resolve_port:223-250`; `PortResolutionTests` (6 tests) pass. |
| 34 | `--port` is validated as an absolute device path under `/dev` and forwarded to the monitor as `-p`; a path that is not a USB serial device reported by `pio device list` refuses rather than guessing. | ✓ VERIFIED | `_valid_port_path:253-259`; `resolve_port` explicit branch; `CliUsageTests` `--port` cases and `test_an_explicit_port_absent_from_the_list_refuses` pass. |
| 35 | The `--json` object and the human `CAPTURED` line report the resolved device path, its `VID:PID`, and the baud actually used; the log file still holds exactly the raw device bytes with no injected header. | ✓ VERIFIED | `main:596-646`; `test_a_capture_reports_the_port_vid_pid_and_baud`, `test_a_json_success_payload` pass; `write_log_atomically` is unchanged and writes only the captured bytes. |
| 36 | The reported baud is `--baud` when supplied, otherwise the project's resolved `monitor_speed`; an unresolvable baud is the documented exit-2 usage error, never a silent fallback to 9600. | ✓ VERIFIED | `resolve_baud:313-351`; `BaudResolutionTests` (8 tests) pass. |
| 37 | The existing PTY byte-fidelity, early-exit, reaping, credential-scan and atomic-write guarantees still hold, and the full capture suite is green. | ✓ VERIFIED | `python3 -m unittest scripts.tests.test_serial_capture` — 62 tests, OK (outside the sandbox; the sandbox fails `pty.openpty()` with `out of pty devices`). |
| 38 | With the board attached, the UAT command exits 0, prints `CAPTURED — N bytes captured` naming `.skill-state/logs/1_3-police-flasher.log`, and the log holds device bytes. | ⚠️ PRESENT_BEHAVIOR_UNVERIFIED | Present and wired; no board is attached and the sandbox refuses `/dev/cu.*`. See Human Verification Required. |

#### 09-16 gap-closure must-haves (truths 39–44)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 39 | `hw-flash` resolves exactly one serial port before the consent gate and passes that same path to both the upload (`pio run --upload-port`) and the capture (`serial_capture.py --port`). | ✓ VERIFIED | `SKILL.md` "Before the gate" port bullet, the consent-gate example and "The upload"; both commands name the same resolved path. |
| 40 | When zero or several USB serial devices are present, the skill stops before the gate, names every candidate and asks for `--port`. | ✓ VERIFIED | `SKILL.md:48-53`. |
| 41 | The skill documents the two ESP32-S3 paths: native USB-Serial-JTAG (`303A:1001`) and CH343 (`1A86:55D3`), with baud significance, DTR/RTS reset semantics and re-enumeration. | ✓ VERIFIED | `SKILL.md:173-192` "The two serial paths". |
| 42 | The shared guardrails carry the same-port rule once, so no skill restates it. | ✗ FAILED | `SKILL.md:54-55` and `:86` restate the rule owned by `guardrails.md:17-21`; plan 09-16 task H required a reference only. Review WR-03. |
| 43 | The canonical `.claude/skills/**` files and the committed `.agents/skills/**` mirror agree; the mirror and `generated.skills.manifest` are produced only by `uv run scripts/gen_skills.py`. | ✓ VERIFIED | `gen_skills.py --check` exit 0, every record `UNCHANGED`. |
| 44 | The phase gate is green: the full Python suite, metadata, generated views, the mirror check and `pre-commit run --all-files`. | ✓ VERIFIED | 439 tests OK; `check_metadata.py` PASS; `gen_views.py --all --check` UNCHANGED; `gen_skills.py --check` exit 0; `pre-commit run --all-files` exit 0. |

**Score:** 41/44 truths verified (1 present, behavior-unverified; 2 failed).

### Deferred Items

None — no later roadmap phase covers the credential scan or the skill contracts.

### Advisory (New Scope, Unevidenced)

None. Every new-scope concern carries deterministic evidence (a named test, a direct probe, or an open review finding with a reproducible command).

### Issues (Open Review Findings)

These are recorded in `09-REVIEW-DISPOSITION.md`. They are not entries in any plan's `must_haves`, but two of them falsify phase truths and are therefore listed as gaps above.

| Finding | Severity | Open | Relationship to a truth |
|---------|----------|------|-------------------------|
| CR-01 — `find_credential` misses space-separated compound keywords (`SECRET KEY: hunter2`, `secret key = hunter2`). | critical | yes | Falsifies truth 19; recorded as gap 1. Direct probe returns False for both. |
| WR-01 — the monitor's `-d` is built as `homeworks/<id>` relative to the process cwd, while `project_config` and the log use the resolved root. | warning | yes | Not a must-have; a `--dir` or subdirectory run can monitor the wrong project. |
| WR-02 — a failing `pio project config` is reported as `port discovery failed` and exits 1 instead of 2. | warning | yes | Not a must-have; the docstring calls an unresolvable baud an exit-2 usage error. |
| WR-03 — the same-port rule is restated in `hw-flash` and the shared guardrails. | warning | yes | Falsifies truth 42; recorded as gap 2. |

IN-01 through IN-05 are open informational findings and do not affect a must-have.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `scripts/serial_capture.py` | PTY capture, fail-closed port and baud resolution, idle line state, scan, atomic write, CLI | ✓ VERIFIED | 647 lines, stdlib-only; 62 tests drive it. |
| `scripts/tests/test_serial_capture.py` | PTY, scan, write, argv, port, baud, payload, duration, reap tests | ✓ VERIFIED | 62 tests, 0 skips, 0 failures outside the sandbox. |
| `.claude/skills/hw-flash/SKILL.md` | One resolved port passed to upload and capture, two-path documentation, consent gate | ✓ VERIFIED | Content present; restates the shared same-port rule (truth 42). |
| `.claude/skills/_shared/guardrails.md` | Same-port rule, log prohibition and scoped capture exception | ✓ VERIFIED | Lines 17-21 and "Secrets"; mirrored. |
| `.claude/skills/hw-build/SKILL.md` + `references/repair-loop.md` | Real commands, two-attempt cap, escalation | ✓ VERIFIED | Present and substantive. |
| `.claude/skills/new-homework/SKILL.md` + `references/*` | Guided and one-shot modes, eight-topic bank, checkpoints, conflicts | ✓ VERIFIED | Present and substantive. |
| The four stub skills | `SKILL.md`, `CHANGELOG.md`, `LESSONS.md`, `status: stub` | ✓ VERIFIED | `course-index`, `hw-report`, `schematic`, `simulate`. |
| `generated.skills.manifest` and `.agents/skills/**` | Generated projection in sync | ✓ VERIFIED | `gen_skills.py --check` `UNCHANGED`. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `pio device list --json-output` | `resolve_port` | `_usb_identity` filter | ✓ WIRED | `serial_capture.py:199-250`. |
| `resolve_port` | `pio device monitor` | `-p <port> --dtr 0 --rts 0` | ✓ WIRED | `_build_command:520-534`. |
| `pio project config` | `resolve_baud` | `monitor_speed` of the selected env | ✓ WIRED | `project_config:261-272`, `resolve_baud:313-351`. |
| `resolve_port`/`resolve_baud` | `--json` and `CAPTURED` line | `main` payload | ✓ WIRED | `main:596-646`. |
| PTY master | `find_credential` → `write_log_atomically` | `capture_and_store` | ✓ WIRED | Scan precedes the write; a match writes nothing. |
| `.claude/skills/**` | `.agents/skills/**` → `generated.skills.manifest` | `scripts/gen_skills.py` | ✓ WIRED | `gen-skills-check` hook; `--check` exit 0. |
| board hwid | `--upload-port` and `--port` | `hw-flash` port resolution | ✓ WIRED (documented) | Same path named in both commands; runtime hardware not exercised. |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| `scripts/serial_capture.py` | captured bytes | PTY master fed by `pio device monitor` | Yes (fake child on a PTY; real device on hardware) | ✓ FLOWING (automated); hardware unverified |
| `scripts/serial_capture.py` | `port`, `vid_pid`, `baud` | `resolve_port` / `resolve_baud` | Yes | ✓ FLOWING |
| `hw-flash` announced commands | `<port>` | `pio device list --json-output` | Yes | ✓ FLOWING |
| `.agents/skills/**` | canonical bytes | `.claude/skills/**` | Yes | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Capture suite | `python3 -m unittest scripts.tests.test_serial_capture` | 62 tests, OK (outside sandbox) | ✓ PASS |
| Full Python suite | `python3 -m unittest discover scripts/tests` | 439 tests, OK | ✓ PASS |
| Mirror in sync | `uv run scripts/gen_skills.py --check` | exit 0, all `UNCHANGED` | ✓ PASS |
| Metadata contract | `uv run scripts/check_metadata.py` | PASS | ✓ PASS |
| Generated views | `uv run scripts/gen_views.py --all --check` | exit 0, `UNCHANGED` | ✓ PASS |
| Local gate | `pre-commit run --all-files` | exit 0, 14 hooks | ✓ PASS |
| Credential scan, compound keyword | direct `find_credential(b"SECRET KEY: hunter2")` | `False` (expected `True`) | ✗ FAIL (CR-01) |
| Hardware capture | `uv run scripts/serial_capture.py --id 1_3-police-flasher --seconds 20` | not run — no board, sandbox refuses `/dev/cu.*` | ? SKIP |

### Probe Execution

Not applicable — no `scripts/*/tests/probe-*.sh` file is declared or present. The plans' "probe rows" are manual resolution tables, not executable probes.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| FLOW-01 | 01–16 | Seven project-local skills at version 0.1; `new-homework` and `hw-build` fully implemented first. | ✓ SATISFIED (version note) | Seven skills exist; six at 0.1, `new-homework` at 0.2 (documented changelog bump). `hw-build` is 0.1 active. |
| FLOW-02 | 03, 08, 16 | `new-homework` guided and one-shot modes with an adaptive bank covering board, framework, language, mode, specification, simulation, tests, deliverables. | ✓ SATISFIED | `references/question-bank.md` eight sections; `SKILL.md` "Intake". |
| FLOW-03 | 03, 08 | Guided mode explanation → code → run → questions at block granularity, pauses after each block, deepens when stuck. | ✓ SATISFIED | `SKILL.md:109-119`. |
| FLOW-04 | 02, 03, 05, 08 | Both modes checkpoint after intake, code and report; flashing, commit/PR, conflicts and ambiguity guardrails always apply. | ✓ SATISFIED | `references/state-file.md`; `guardrails.md`; `SKILL.md` "Checkpoints". |
| FLOW-05 | 02, 03, 08 | Spec-vs-best-practice conflicts and ambiguity produce a recommended assumption recorded in the report. | ✓ SATISFIED | `guardrails.md`; `SKILL.md` "Conflicts and ambiguity"; dry-run Leg 3. |
| FLOW-06 | 04, 08 | A failing build is fixed at most twice, then explained and direction requested. | ✓ SATISFIED | `references/repair-loop.md`; dry-run Leg 5. |
| FLOW-07 | 05, 09–16 | `hw-flash` requires explicit confirmation and captures serial logs; the other four skills stay thin stubs. | ✓ SATISFIED (automated half) | Consent gate and capture helper verified; four stubs verified. Hardware capture remains human-verified (truth 38). |

**Orphaned requirements:** none — `REQUIREMENTS.md` maps only FLOW-01–07 to Phase 9, and every plan declares all seven.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| — | — | No `TBD`/`FIXME`/`XXX` marker in the changed code or skills. | — | — |
| `scripts/serial_capture.py` | 104-111 | A whitespace connector between compound keyword words is not admitted. | 🛑 Blocker | CR-01/gap 1. |
| `.claude/skills/hw-flash/SKILL.md` | 54-55, 86 | Restates a rule the shared guardrails own. | 🛑 Blocker | WR-03/gap 2. |
| `scripts/serial_capture.py` | 525 | `-d` path is cwd-relative while config and log use the resolved root. | ⚠️ Warning | WR-01. |
| `scripts/serial_capture.py` | 172-196, 594-595 | A config failure under the `port discovery failed` prefix and exit 1. | ⚠️ Warning | WR-02. |

### Human Verification Required

### 1. Capture a real device log through hardware

**Test:** With the board attached after a confirmed upload, run `uv run scripts/serial_capture.py --id 1_3-police-flasher --seconds 20`; press RESET during the window because the firmware logs only in `setup()`.
**Expected:** Exit 0, a `CAPTURED — N bytes captured from <port> (USB VID:PID=<vid>:<pid>) at <baud> baud` line naming `.skill-state/logs/1_3-police-flasher.log`, and a log holding the raw device bytes.
**Why human:** No board is attached in this environment and the command sandbox refuses `/dev/cu.*`; the automated suite drives a fake `sys.executable` child on a PTY.

### Gaps Summary

The phase's seven skills, both implemented workflows (`new-homework`, `hw-build`), the `hw-flash` contract and the generated mirror are present, substantive and wired. The automated half of G-09-1 is closed: the monitor now receives `-p <port> --dtr 0 --rts 0`, port and baud resolution are fail-closed, and the payload reports the resolved identity. The full local gate is green (439 tests, 14 pre-commit hooks, metadata, views, mirror).

Two must-have truths fail, and the hardware truth cannot be exercised here:

1. **Truth 19 (CR-01, critical).** `find_credential` does not match a space-separated compound keyword, so `SECRET KEY: hunter2` would be written to the capture log. The guardrails promise to refuse a "secret … assignment"; the regex does not. This predates the 09-15/09-16 delta but falsifies the previously verified blanket truth.
2. **Truth 42 (WR-03, warning).** `hw-flash/SKILL.md:54-55` and `:86` restate the same-port rule the shared guardrails own. Plan 09-16 task H explicitly required a reference, not a restatement, and the 09-16 summary's claim that the skill "does not restate it" is false.
3. **Truth 38 (hardware, present-but-behavior-unverified).** The real capture path has no hardware evidence in this environment. It is not counted as verified.

WR-01 and WR-02 remain open warnings and do not fail a must-have.

---

_Verified: 2026-10-27T12:22:14Z_
_Verifier: Claude (gsd-verifier)_

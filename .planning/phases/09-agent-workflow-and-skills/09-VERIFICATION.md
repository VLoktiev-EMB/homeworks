---
phase: 09-agent-workflow-and-skills
verified: 2026-10-27T12:54:23Z
status: gaps_found
score: 45/47 must-haves verified
covered_files: [".agents/skills/_shared/guardrails.md", ".agents/skills/hw-build/SKILL.md", ".agents/skills/hw-flash/CHANGELOG.md", ".agents/skills/hw-flash/LESSONS.md", ".agents/skills/hw-flash/SKILL.md", ".agents/skills/new-homework/SKILL.md", ".claude/CLAUDE.md", ".claude/skills/_shared/guardrails.md", ".claude/skills/course-index/CHANGELOG.md", ".claude/skills/course-index/LESSONS.md", ".claude/skills/course-index/SKILL.md", ".claude/skills/hw-build/CHANGELOG.md", ".claude/skills/hw-build/LESSONS.md", ".claude/skills/hw-build/SKILL.md", ".claude/skills/hw-build/references/repair-loop.md", ".claude/skills/hw-flash/CHANGELOG.md", ".claude/skills/hw-flash/LESSONS.md", ".claude/skills/hw-flash/SKILL.md", ".claude/skills/hw-report/CHANGELOG.md", ".claude/skills/hw-report/LESSONS.md", ".claude/skills/hw-report/SKILL.md", ".claude/skills/new-homework/CHANGELOG.md", ".claude/skills/new-homework/LESSONS.md", ".claude/skills/new-homework/SKILL.md", ".claude/skills/new-homework/references/question-bank.md", ".claude/skills/new-homework/references/state-file.md", ".claude/skills/schematic/CHANGELOG.md", ".claude/skills/schematic/LESSONS.md", ".claude/skills/schematic/SKILL.md", ".claude/skills/simulate/CHANGELOG.md", ".claude/skills/simulate/LESSONS.md", ".claude/skills/simulate/SKILL.md", ".planning/phases/09-agent-workflow-and-skills/09-01-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-01-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-02-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-02-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-03-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-03-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-04-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-04-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-05-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-05-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-06-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-06-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-07-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-07-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-08-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-08-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-09-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-09-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-10-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-10-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-11-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-11-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-12-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-12-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-13-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-13-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-14-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-14-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-15-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-15-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-16-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-16-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-17-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-17-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-18-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-18-SUMMARY.md", ".pre-commit-config.yaml", "AGENTS.md", "generated.skills.manifest", "scripts/affected.py", "scripts/gen_skills.py", "scripts/serial_capture.py", "scripts/tests/test_affected.py", "scripts/tests/test_serial_capture.py"]
covered_digest: "v3:sha256:a1b269a8b49634b6557539f849a5bbcb5979430e17ed987cbdd25d88dce3de31"
behavior_unverified: 1
overrides_applied: 0
re_verification:
  previous_status: gaps_found
  previous_score: 41/44
  gaps_closed:
    - "Truth 19 / review CR-01: find_credential now admits a space-separated compound keyword. Direct probe returns True for `SECRET KEY: hunter2`, `secret key = hunter2`, `Secret Key: hunter2`, `secret key: hunter2` and `SECRET KEY = hunter2`; every pinned benign negative still returns False; 12/12 CredentialScanTests pass."
  gaps_remaining:
    - "Truth 42 / review WR-03 + WR-13: hw-flash/SKILL.md still carries normative variants of the shared ambiguous-port rule at lines 50-52 and 188-189, and the locator at line 54-55 falsely claims `it is not restated here`."
    - "Truth 38: the hardware capture remains unproven in this environment; no board is attached and the sandbox refuses /dev/cu.*."
  regressions: []
gaps:
  - truth: "Truth 42 / 09-16 + 09-18 must-have: the shared guardrails carry the same-resolved-port rule once, so no skill restates it; hw-flash/SKILL.md carries no normative variant of it."
    status: failed
    reason: "`.claude/skills/hw-flash/SKILL.md:50-52` restates the guardrails' normative ambiguity instruction (`Stop the skill on more than one candidate, announcing every path and asking the user for --port`) and `:188-189` repeats it (`Both cables attached produce two candidates ... stop and ask for --port`). The locator sentence at `:54-55` says `Port handling follows the shared flashing rule in ../_shared/guardrails.md; it is not restated here.`, which is false within its own bullet. Review WR-13 records the same finding; plan 09-18's summary claim that the five normative restatements were replaced is not borne out for the ambiguity half."
    artifacts:
      - path: ".claude/skills/hw-flash/SKILL.md"
        issue: "Lines 50-52 and 188-189 restate the shared ambiguous-candidate rule; line 54-55 falsely claims no restatement."
      - path: ".agents/skills/hw-flash/SKILL.md"
        issue: "The generated mirror carries the same restatement at lines 51-53 and 189-190; regenerate after the canonical edit."
    missing:
      - "Remove the normative `stop ... and ask for --port` sentences from both places, or reformulate the locator so it does not claim a non-restatement (for example: `Port handling follows the shared flashing rule in ../_shared/guardrails.md; the steps below only apply it.`)."
      - "Keep every operational step: `pio device list --json-output`, the `USB VID:PID=` hwid filter, the single-candidate choice, the stop on zero, the `--port` prompt on ambiguity, and the absolute `/dev` validation."
      - "Regenerate the mirror with `uv run scripts/gen_skills.py`; never hand-edit `.agents/skills/**`."
deferred: []
advisory: []
behavior_unverified_items:
  - truth: "Truth 38 / 09-15 must-have: with the board attached, `uv run scripts/serial_capture.py --id 1_3-police-flasher --seconds 20` exits 0, prints `CAPTURED — N bytes captured` naming `.skill-state/logs/1_3-police-flasher.log`, and the log holds device bytes."
    test: "Connect the board, upload the firmware, then run `uv run scripts/serial_capture.py --id 1_3-police-flasher --seconds 20`; press RESET during the window because the firmware logs only in `setup()`."
    expected: "Exit 0, a `CAPTURED` line naming the ignored log and the resolved port/VID:PID/baud, and a log holding the raw device bytes (the boot line in the measured run)."
    why_human: "No board is attached in this environment and the command sandbox refuses /dev/cu.*; the automated suite drives a fake `sys.executable` child on a PTY."
coincidental_reliance_items: []
human_verification:
  - test: "With the board attached after a confirmed upload, run `uv run scripts/serial_capture.py --id 1_3-police-flasher --seconds 20` and inspect the exit line and the ignored log."
    expected: "Exit 0, a `CAPTURED — N bytes captured from <port> (USB VID:PID=<vid>:<pid>) at <baud> baud` line naming `.skill-state/logs/1_3-police-flasher.log`, and a log holding the raw device bytes."
    why_human: "Hardware and a serial port are required; the sandbox refuses /dev/cu.* and no board is attached."
---

# Phase 9: Agent Workflow and Skills Verification Report

**Phase Goal:** Seven versioned agent skills exist, with `new-homework` and `hw-build` fully usable in guided and one-shot modes.
**Friction-log justification:** The Phase 4.2 log must contain at least one entry for the intake, build, or report workflow; otherwise the corresponding skill is not written.
**Verified:** 2026-10-27T12:54:23Z
**Status:** gaps_found
**Re-verification:** Yes — after the `--gaps-only` run that executed plans 09-17 and 09-18 on top of the earlier 09-11…09-16 gap closure.

## Goal Achievement

### Observable Truths

#### Baseline must-haves (regression check, truths 1–31)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `capture_and_store` returns the exact bytes a child wrote to a PTY, including CR, LF, NUL and 0xff; the child sees stdin/stdout as TTYs and a pipe child fails. | ✓ VERIFIED | `test_capture_preserves_every_byte_and_sees_a_tty`, `test_a_pipe_capture_would_fail_the_same_child` pass in the 441-test suite. |
| 2 | A capture refuses with `capture unavailable` when the command cannot start, exits before the bound, or produces zero bytes; reaching the bound with bytes succeeds. | ✓ VERIFIED | `capture_pty` raises on start/early exit; `capture_and_store` refuses empty bytes; the corresponding tests pass. |
| 3 | `find_credential` matches the six review shapes, the four ordinary password assignments and the five identifier-suffixed assignments, and does not match the pinned benign set. | ✓ VERIFIED | `CredentialScanTests` (12 tests) pass; direct probe confirms all shapes and all four benign negatives. |
| 4 | `write_log_atomically` anchors under the resolved root, refuses a symlinked `.skill-state`/`logs`/log, leaves no temporary file, and replaces rather than appends. | ✓ VERIFIED | Seven `AtomicLogWriteTests` pass. |
| 5 | Two concurrent atomic writes leave exactly one whole payload and no temporary file; a reader never sees a torn log. | ✓ VERIFIED | `test_concurrent_writes_leave_one_whole_payload`, `test_a_concurrent_reader_never_sees_a_torn_log` pass. |
| 6 | `hw-flash` invokes `scripts/serial_capture.py` instead of a piped monitor, normalizes `monitor_speed`, announces the conditional `-e` segment, and calls the bound a success. | ✓ VERIFIED | `SKILL.md`; no `subprocess.PIPE` in the skill. |
| 7 | The shared guardrails forbid a credential in the state file or any log outside the one scoped capture exception, and state the fail-closed scan shapes. | ✓ VERIFIED | `guardrails.md` "Secrets" section, mirrored in `.agents/skills/_shared/guardrails.md`. |
| 8 | The regenerated mirror and `generated.skills.manifest` match the canonical tree, and `scripts/affected.py` maps `scripts/serial_capture.py` to no build impact. | ✓ VERIFIED | `gen_skills.py --check` exit 0, every record `UNCHANGED`; `scripts/affected.py`. |
| 9 | Seven project-local skills exist, each with `SKILL.md`, `CHANGELOG.md` and `LESSONS.md`; three are active and four are stubs. | ✓ VERIFIED | Seven directories; `hw-build` (0.1), `hw-flash` (0.1), `new-homework` (0.2) active; `course-index`, `hw-report`, `schematic`, `simulate` `status: stub`. Version deviation: `new-homework` is 0.2, documented in its changelog. |
| 10 | The Phase 4.2 friction log justifies the intake, build and report skills. | ✓ VERIFIED | `.planning/phases/04.2-tracer-homework-1-3/04.2-FRICTION-LOG.md`: F-01 (intake / `new-homework`), F-03 (build), F-07 (report contract). |
| 11 | `new-homework` supports guided and one-shot modes with an adaptive bank ordered mode, board, framework, language, specification, simulation, tests, deliverables. | ✓ VERIFIED | `references/question-bank.md` carries the eight `##` sections in exactly that order; `SKILL.md:47` distinguishes guided and one-shot. The 09-03 language sub-truth (`cpp` for both frameworks) is superseded by quick task `261026-x78`, recorded in `09-DRY-RUN.md:10-16` and the 0.2 changelog. |
| 12 | Guided mode follows explain → code → run → questions at block granularity and pauses with `[Продовжити | Поясни глибше | Стоп]`; deepening never advances. | ✓ VERIFIED | `SKILL.md:107-120`. |
| 13 | Both modes checkpoint after intake, after code and after report; guardrails always apply. | ✓ VERIFIED | `references/state-file.md` checkpoints `intake`/`code`/`report`; `SKILL.md` "Checkpoints". |
| 14 | Spec-vs-best-practice conflicts and ambiguity produce a recommended assumption transcribed into the report. | ✓ VERIFIED | `guardrails.md` "Specification versus best practice" and "Ambiguity"; `SKILL.md` "Conflicts and ambiguity". |
| 15 | `hw-build` runs the real target build and native suite, caps each leg at two repairs, preserves warnings, never commits/resets, and escalates with evidence. | ✓ VERIFIED | `.claude/skills/hw-build/SKILL.md`; `references/repair-loop.md` counter and escalation payload. |
| 16 | `hw-flash` prints board, environment and exact upload command, requires a literal `так`/`yes`, runs no upload on a non-affirmative answer, and never pre-approves `upload`. | ✓ VERIFIED | `SKILL.md` "The consent gate" and "The upload"; `allowed-tools` carries no `upload`. |
| 17 | `hw-flash` resolves the baud from the project fail-closed; the real homework resolves 115200 and an absent key stops before the monitor. | ✓ VERIFIED | `SKILL.md` "Before the gate"; `platformio.shared.ini` and the homework inherit 115200. |
| 18 | `hw-flash` wires the user-resolved baud into the helper, so the announced baud is the executed baud. | ✓ VERIFIED | `SKILL.md` carries `[--baud <n>]`; `test_baud_is_forwarded_as_dash_b` passes. |
| 19 | **GAP 1 / RR-CR-01 lineage:** no skill writes a credential to a log; the guardrails' secrets rule holds across every implemented skill, including space-separated compound keywords. | ✓ VERIFIED | Direct probe: `SECRET KEY: hunter2`, `secret key = hunter2`, `Secret Key: hunter2`, `secret key: hunter2`, `SECRET KEY = hunter2`, `secret-key: hunter2`, `secretkey: hunter2` all return True; `auth mode = WPA2`, `the cpwd tool reports ready`, `author wrote nothing here`, `secret is` and the benign boot log return False. This closes 09-17's shape, benign-negative and end-to-end truths: `test_space_separated_compound_assignments_match` and `test_a_space_separated_compound_credential_child_writes_nothing` pass. |
| 20 | `scripts/gen_skills.py` is the only mirror writer, maintains the manifest, supports `--check`, and the committed tree is in sync. | ✓ VERIFIED | `gen_skills.py --check` exit 0. |
| 21 | The drift gate is wired and `affected.py`/`.gitignore`/`AGENTS.md` cover the Phase 9 paths. | ✓ VERIFIED | `.pre-commit-config.yaml` `gen-skills-check`; `AGENTS.md` no-build-impact paragraph. |
| 22 | The `.claude/CLAUDE.md` `GSD:skills` block lists exactly seven skills and the decision row records the canonical/mirror split. | ✓ VERIFIED | Seven rows in `.claude/CLAUDE.md`; `docs/decisions/README.md:33`. |
| 23 | The dry-run transcript records the guided, one-shot, conflict, build-repair and flash-gate legs and contains no credential or private absolute path. | ✓ VERIFIED | `09-DRY-RUN.md` Legs 0–6; no `/Users/`, `/home/` or credential value. |
| 24 | The full local gate is green. | ✓ VERIFIED | `pre-commit run --all-files` exit 0 (14 hooks); 441 tests OK; metadata, views and mirror checks exit 0. |
| 25 | Both announced capture commands carry `[--baud <n>]`, the prose names `--baud` as the helper option, and the conditional sentence names `[--env <env>]` and `[--baud <n>]`. | ✓ VERIFIED | `SKILL.md:80`, `:122`, and the conditional sentence at `:84-85` and `:125-126`. |
| 26 | `_build_command` forwards `-e` and `-b` only when supplied; the CLI `CAPTURED`/`REFUSED` payloads and a concurrent reader are pinned by tests. | ✓ VERIFIED | `BuildCommandTests` (`test_env_is_forwarded`, `test_baud_is_forwarded_as_dash_b`, `test_env_and_baud_together`), `CliResultPayloadTests`, and the concurrent-reader case pass. |
| 27 | The four ordinary password assignments match and the pinned benign set stays unmatched. | ✓ VERIFIED | `test_the_ordinary_password_assignments_match`, `test_an_ordinary_word_containing_a_keyword_does_not_match` pass; direct probe confirms. |
| 28 | The guardrails sentence names the widened shapes and the mirror/manifest are regenerated. | ✓ VERIFIED | `guardrails.md:60-76` names the copula, embedded keyword, 128-character suffix, compound keyword and `passphrase`/`pwd`; `gen_skills.py --check` `UNCHANGED`. |
| 29 | `--seconds` rejects NaN, infinity, a non-positive value and an oversized bound before `resolve_root`/`_build_command`/`Popen`, and `capture_pty` reaps the child on an escaping exception. | ✓ VERIFIED | `main` checks `math.isfinite` before any process; `CliDurationTests` and `test_an_exception_escaping_the_loop_reaps_the_child` pass. |
| 30 | **CR-01 (post-verification review):** the connector ceiling is 128 characters, and 32-, 33- and 42-character keyword suffixes all match. | ✓ VERIFIED | `serial_capture.py` uses `[\w.-]{0,128}`; `test_a_connector_longer_than_32_characters_matches` passes. (Open IN-11: the 128/129 boundary is not pinned.) |
| 31 | **WR-01 (post-verification review):** `auth mode = WPA2` is pinned as a benign negative and does not match. | ✓ VERIFIED | The benign-negative test iterates it; direct probe returns False. |

#### 09-15 gap-closure must-haves (truths 32–38)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 32 | Every monitor argv carries `-p` with the resolved device path plus `--dtr 0` and `--rts 0`. | ✓ VERIFIED | `_build_command:521-545`; `test_the_monitor_opens_in_the_idle_line_state_with_an_explicit_port` passes. |
| 33 | When `--port` is omitted, exactly one USB serial device is selected; zero candidates or more than one candidate refuses with a `capture unavailable` reason that names every candidate and tells the user to pass `--port`. | ✓ VERIFIED | `resolve_port:231-258`; `PortResolutionTests` (7 tests) pass. |
| 34 | `--port` is validated as an absolute device path under `/dev` and forwarded to the monitor as `-p`; a path that is not a USB serial device reported by `pio device list` refuses rather than guessing. | ✓ VERIFIED | `_valid_port_path:261-267`; `resolve_port` explicit branch; the `--port` usage cases and `test_an_explicit_port_absent_from_the_list_refuses` pass. |
| 35 | The `--json` object and the human `CAPTURED` line report the resolved device path, its `VID:PID`, and the baud actually used; the log file still holds exactly the raw device bytes with no injected header. | ✓ VERIFIED | `main` payload; `test_a_capture_reports_the_port_vid_pid_and_baud`, `test_a_json_success_payload` pass; `write_log_atomically` writes only the captured bytes. |
| 36 | The reported baud is `--baud` when supplied, otherwise the project's resolved `monitor_speed`; an unresolvable baud is the documented exit-2 usage error, never a silent fallback to 9600. | ✓ VERIFIED | `resolve_baud:321-363`; `BaudResolutionTests` (8 tests) pass. |
| 37 | The existing PTY byte-fidelity, early-exit, reaping, credential-scan and atomic-write guarantees still hold, and the full capture suite is green. | ✓ VERIFIED | `python3 -m unittest discover scripts/tests` — 441 tests, OK, no skips (run outside the sandbox; the sandbox refuses `pty.openpty()`). |
| 38 | With the board attached, the UAT command exits 0, prints `CAPTURED — N bytes captured` naming `.skill-state/logs/1_3-police-flasher.log`, and the log holds device bytes. | ⚠️ PRESENT_BEHAVIOR_UNVERIFIED | Present and wired; no board is attached and the sandbox refuses `/dev/cu.*`. See Human Verification Required. |

#### 09-16 gap-closure must-haves (truths 39–44)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 39 | `hw-flash` resolves exactly one serial port before the consent gate and passes that same path to both the upload (`pio run --upload-port`) and the capture (`serial_capture.py --port`). | ✓ VERIFIED | `SKILL.md` port bullet, consent-gate example and "The upload"; both commands name the same resolved path. |
| 40 | When zero or several USB serial devices are present, the skill stops before the gate, names every candidate and asks for `--port`. | ✓ VERIFIED | `SKILL.md:47-52`. |
| 41 | The skill documents the two ESP32-S3 paths: native USB-Serial-JTAG (`303A:1001`) and CH343 (`1A86:55D3`), with baud significance, DTR/RTS reset semantics and re-enumeration. | ✓ VERIFIED | `SKILL.md:168-190` "The two serial paths". |
| 42 | The shared guardrails carry the same-port rule once, so no skill restates it. | ✗ FAILED | `SKILL.md:50-52` and `:188-189` restate the guardrails' normative ambiguity rule; `:54-55` falsely claims `it is not restated here`. Review WR-13. See Gaps Summary. |
| 43 | The canonical `.claude/skills/**` files and the committed `.agents/skills/**` mirror agree; the mirror and `generated.skills.manifest` are produced only by `uv run scripts/gen_skills.py`. | ✓ VERIFIED | `gen_skills.py --check` exit 0, every record `UNCHANGED`. |
| 44 | The phase gate is green: the full Python suite, metadata, generated views, the mirror check and `pre-commit run --all-files`. | ✓ VERIFIED | 441 tests OK; `check_metadata.py` PASS; `gen_views.py --all --check` UNCHANGED; `gen_skills.py --check` exit 0; `pre-commit run --all-files` exit 0 (14 hooks). |

#### 09-17 / 09-18 gap-closure must-haves (truths 45–47)

Truths 45–47 are the new, non-duplicative must-haves of the latest run. The 09-17 shape, benign-negative and end-to-end truths are verified under truth 19, and the 09-18 mirror and gate truths under truths 43–44, per the deduplication rule.

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 45 | The source comment above `_KEYWORDS` names the space-separated compound shape it now admits, so the regex and its prose agree (09-17). | ✓ VERIFIED | `serial_capture.py:127-143` names `secret key`, `secret_key`, `secret-key` and the literal separator class. |
| 46 | `hw-flash/SKILL.md` keeps its operational port steps — `pio device list --json-output`, the `USB VID:PID=` hwid filter, the single-candidate choice, the stop on zero, the `--port` question on ambiguity and the absolute `/dev` validation — and points at the shared file once (09-18). | ✓ VERIFIED | `SKILL.md:47-55` carries every operational step and exactly one locator sentence. Caveat: the locator's `it is not restated here` clause is false; that defect is truth 42. |
| 47 | The guardrails' capture exception names the space-separated compound keyword shape that plan 09-17 makes the scan admit, so policy and scan agree (09-18). | ✓ VERIFIED | `guardrails.md:69-71` names `secret key = <value>` and `SECRET KEY: <value>` with the one-space/underscore/hyphen bound. |

#### Superseded must-haves

The 09-03 plan required `language: cpp` for both frameworks, with the skill forbidden to derive `c` for ESP-IDF. Quick task `261026-x78` deliberately changed the ESP-IDF template to `src/main.c` with `language: c`; `09-DRY-RUN.md:10-16` records the supersession and the 0.2 changelog entry documents the derivation rule. The requirement is therefore superseded, not failed: `templates/homework-espidf/homework.yaml:7` and `references/question-bank.md` agree on `espidf -> c`.

**Score:** 45/47 truths verified (1 present, behavior-unverified; 1 failed).

### Deferred Items

None — no later roadmap phase covers the shared-port rule or the hardware capture path.

### Advisory (New Scope, Unevidenced)

None. Every new-scope concern from the fresh review (WR-14, IN-11, IN-12, IN-13) carries deterministic evidence — a direct probe or a reproducible test listing — and is recorded under Issues below; none falsifies a must-have.

### Issues (Open Review Findings)

These are recorded in `09-REVIEW-DISPOSITION.md`. They are not entries in any plan's `must_haves`, but truth 42's finding is a gap above.

| Finding | Severity | Open | Relationship to a truth |
|---------|----------|------|-------------------------|
| CR-01 — `find_credential` missed space-separated compound keywords. | critical | no (fixed) | Truth 19 now VERIFIED. |
| WR-03 / WR-13 — the same-port rule is still restated in `hw-flash` and the shared guardrails. | warning | yes | Falsifies truth 42; recorded as the gap. |
| WR-14 — the module docstring omits the compound keyword shape the scan admits. | warning | yes | Not a must-have; the 09-17 contract names the shape in the source comment, not the docstring. |
| WR-01 — the monitor's `-d` is built as `homeworks/<id>` relative to the process cwd. | warning | yes | Not a must-have; a `--dir` or subdirectory run can monitor the wrong project. |
| WR-02 — a failing `pio project config` is reported as `port discovery failed` and exits 1 instead of 2. | warning | yes | Not a must-have; `_run_json` maps any child failure to the discovery prefix. |
| IN-11 — the 128-character connector ceiling is not pinned; the test name still says 32. | info | yes | Not a must-have; `test_a_connector_longer_than_32_characters_matches` still checks only 32/33/42. |
| IN-12 — test-module comments describe the old fixture composition. | info | yes | Not a must-have. |
| IN-13 — a tab-separated compound keyword remains outside the scan. | info | yes | Not a must-have; the policy names one space, underscore or hyphen. |

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `scripts/serial_capture.py` | PTY capture, fail-closed port and baud resolution, idle line state, scan, atomic write, CLI | ✓ VERIFIED | Substantive; 441-test suite drives it. |
| `scripts/tests/test_serial_capture.py` | PTY, scan, write, argv, port, baud, payload, duration, reap tests | ✓ VERIFIED | 0 failures outside the sandbox. |
| `.claude/skills/hw-flash/SKILL.md` | One resolved port passed to upload and capture, two-path documentation, consent gate | ✓ VERIFIED | Content present; restates the shared ambiguity rule (truth 42). |
| `.claude/skills/_shared/guardrails.md` | Same-port rule, log prohibition, scoped capture exception | ✓ VERIFIED | Lines 17-21 and "Secrets"; mirrored. |
| `.claude/skills/hw-build/SKILL.md` + `references/repair-loop.md` | Real commands, two-attempt cap, escalation | ✓ VERIFIED | Present and substantive. |
| `.claude/skills/new-homework/SKILL.md` + `references/*` | Guided and one-shot modes, eight-topic bank, checkpoints, conflicts | ✓ VERIFIED | Present and substantive. |
| The four stub skills | `SKILL.md`, `CHANGELOG.md`, `LESSONS.md`, `status: stub` | ✓ VERIFIED | `course-index`, `hw-report`, `schematic`, `simulate`. |
| `generated.skills.manifest` and `.agents/skills/**` | Generated projection in sync | ✓ VERIFIED | `gen_skills.py --check` `UNCHANGED`. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `pio device list --json-output` | `resolve_port` | `_usb_identity` filter | ✓ WIRED | `serial_capture.py`. |
| `resolve_port` | `pio device monitor` | `-p <port> --dtr 0 --rts 0` | ✓ WIRED | `_build_command`. |
| `pio project config` | `resolve_baud` | `monitor_speed` of the selected env | ✓ WIRED | `resolve_baud`. |
| `resolve_port`/`resolve_baud` | `--json` and `CAPTURED` line | `main` payload | ✓ WIRED | `main`. |
| PTY master | `find_credential` → `write_log_atomically` | `capture_and_store` | ✓ WIRED | Scan precedes the write; a match writes nothing. |
| `_KEYWORDS` + `CREDENTIAL` | `find_credential` | compound alternation | ✓ WIRED | `secret(?:[ _-]?key)?`; direct probe confirms. |
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
| Full Python suite | `python3 -m unittest discover scripts/tests` | 441 tests, OK (outside sandbox) | ✓ PASS |
| Credential scan, compound keyword | `CredentialScanTests` | 12 tests, OK | ✓ PASS |
| Direct credential probe | `find_credential` over 17 positive and 7 negative samples | all as expected | ✓ PASS |
| Mirror in sync | `uv run scripts/gen_skills.py --check` | exit 0, all `UNCHANGED` | ✓ PASS |
| Metadata contract | `uv run scripts/check_metadata.py` | PASS | ✓ PASS |
| Generated views | `uv run scripts/gen_views.py --all --check` | exit 0, `UNCHANGED` | ✓ PASS |
| Local gate | `pre-commit run --all-files` | exit 0, 14 hooks | ✓ PASS |
| Hardware capture | `uv run scripts/serial_capture.py --id 1_3-police-flasher --seconds 20` | not run — no board, sandbox refuses `/dev/cu.*` | ? SKIP |

### Probe Execution

Not applicable — no `scripts/*/tests/probe-*.sh` file is declared or present.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| FLOW-01 | 01–18 | Seven project-local skills at version 0.1; `new-homework` and `hw-build` fully implemented first. | ✓ SATISFIED (version note) | Seven skills exist; six at 0.1, `new-homework` at 0.2 (documented changelog bump). `hw-build` is 0.1 active. |
| FLOW-02 | 03, 08, 16 | `new-homework` guided and one-shot modes with an adaptive bank covering board, framework, language, mode, specification, simulation, tests, deliverables. | ✓ SATISFIED | `references/question-bank.md` eight sections; `SKILL.md` "Intake". |
| FLOW-03 | 03, 08 | Guided mode explanation → code → run → questions at block granularity, pauses after each block, deepens when stuck. | ✓ SATISFIED | `SKILL.md:107-120`. |
| FLOW-04 | 02, 03, 05, 08 | Both modes checkpoint after intake, code and report; flashing, commit/PR, conflicts and ambiguity guardrails always apply. | ✓ SATISFIED | `references/state-file.md`; `guardrails.md`; `SKILL.md` "Checkpoints". |
| FLOW-05 | 02, 03, 08 | Spec-vs-best-practice conflicts and ambiguity produce a recommended assumption recorded in the report. | ✓ SATISFIED | `guardrails.md`; `SKILL.md` "Conflicts and ambiguity"; dry-run Leg 3. |
| FLOW-06 | 04, 08 | A failing build is fixed at most twice, then explained and direction requested. | ✓ SATISFIED | `references/repair-loop.md`; dry-run Leg 5. |
| FLOW-07 | 05, 09–18 | `hw-flash` requires explicit confirmation and captures serial logs; the other four skills stay thin stubs. | ✓ SATISFIED (automated half) | Consent gate and capture helper verified; four stubs verified. Hardware capture remains human-verified (truth 38). |

**Orphaned requirements:** none — `REQUIREMENTS.md` maps only FLOW-01–07 to Phase 9, and every plan declares all seven.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| — | — | No `TBD`/`FIXME`/`XXX` marker in the changed code or skills. | — | — |
| `.claude/skills/hw-flash/SKILL.md` | 50-52, 188-189 | Normative restatement of the shared ambiguity rule; the adjacent locator falsely denies it. | 🛑 Blocker | Truth 42 / WR-13. |
| `scripts/serial_capture.py` | `_build_command` | `-d` path is cwd-relative while config and log use the resolved root. | ⚠️ Warning | WR-01. |
| `scripts/serial_capture.py` | `_run_json` | A config failure under the `port discovery failed` prefix and exit 1. | ⚠️ Warning | WR-02. |
| `scripts/serial_capture.py` | 45-57 | Module docstring omits the compound keyword shape. | ⚠️ Warning | WR-14. |
| `scripts/tests/test_serial_capture.py` | 257 | Test name refers to the retired 32-character bound; 128/129 unpinned. | ℹ️ Info | IN-11. |

### Human Verification Required

### 1. Capture a real device log through hardware

**Test:** With the board attached after a confirmed upload, run `uv run scripts/serial_capture.py --id 1_3-police-flasher --seconds 20`; press RESET during the window because the firmware logs only in `setup()`.
**Expected:** Exit 0, a `CAPTURED — N bytes captured from <port> (USB VID:PID=<vid>:<pid>) at <baud> baud` line naming `.skill-state/logs/1_3-police-flasher.log`, and a log holding the raw device bytes.
**Why human:** No board is attached in this environment and the command sandbox refuses `/dev/cu.*`; the automated suite drives a fake `sys.executable` child on a PTY.

### Gaps Summary

The seven skills, both implemented workflows (`new-homework`, `hw-build`), the `hw-flash` contract and the generated mirror are present, substantive and wired. The CR-01 gap is genuinely closed: the compound-keyword scan matches every pinned positive, keeps every benign negative unmatched, and refuses end to end before any file is created. The mirror, metadata, generated views and the full 14-hook local gate are green, and the Python suite is 441/441.

One must-have truth still fails, and the hardware truth cannot be exercised here:

1. **Truth 42 (WR-03/WR-13, warning).** `hw-flash/SKILL.md:50-52` and `:188-189` still restate the shared guardrails' normative ambiguous-port instruction, while `:54-55` claims `it is not restated here`. Plan 09-18's must-have "`hw-flash/SKILL.md` carries no normative variant of it" is therefore not met, and its summary's claim that five normative restatements were replaced does not hold for the ambiguity half. Fix: remove the two `stop … and ask for --port` sentences (or reformulate the locator without the false denial), keep the operational steps, and regenerate the mirror.
2. **Truth 38 (hardware, present-but-behavior-unverified).** The real capture path has no hardware evidence in this environment. It is not counted as verified.

WR-01, WR-02, WR-14 and IN-11–IN-13 remain open review findings and do not fail a must-have.

---

_Verified: 2026-10-27T12:54:23Z_
_Verifier: Claude (gsd-verifier)_

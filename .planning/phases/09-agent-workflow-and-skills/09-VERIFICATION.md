---
phase: 09-agent-workflow-and-skills
verified: 2026-10-27T10:52:28Z
status: human_needed
score: 31/31 must-haves verified
covered_files: [".agents/skills/_shared/guardrails.md", ".agents/skills/hw-flash/CHANGELOG.md", ".agents/skills/hw-flash/LESSONS.md", ".agents/skills/hw-flash/SKILL.md", ".claude/skills/_shared/guardrails.md", ".claude/skills/hw-flash/CHANGELOG.md", ".claude/skills/hw-flash/LESSONS.md", ".claude/skills/hw-flash/SKILL.md", ".planning/phases/09-agent-workflow-and-skills/09-01-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-01-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-02-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-02-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-03-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-03-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-04-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-04-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-05-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-05-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-06-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-06-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-07-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-07-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-08-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-08-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-09-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-09-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-10-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-10-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-11-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-11-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-12-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-12-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-13-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-13-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-14-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-14-SUMMARY.md", "AGENTS.md", "generated.skills.manifest", "scripts/affected.py", "scripts/serial_capture.py", "scripts/tests/test_affected.py", "scripts/tests/test_serial_capture.py"]
covered_digest: "v3:sha256:62ccb00156a20b55e3c1ac9304dfba3462986ee8d7ed13d8e843d806e0beecb9"
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: gaps_found
  previous_score: 28/29
  gaps_closed:
    - "GAP 2 / RR-CR-01 / truth 19 — the assignment branch now admits a `[\\w.-]{0,128}` connector, so `{\"secretKey\": \"hunter2\"}`, `secret_key = hunter2`, `passwordHash: abcdef`, `SECRET_KEY = hunter2` and a 38-character suffix all match, and `capture_and_store` refuses them before any file exists; verified by direct execution and two named tests."
    - "CR-01 / review of 09-14 — the 32-character ceiling was raised to 128; `test_a_connector_longer_than_32_characters_matches` pins 32/33/42-character suffixes, and the guardrails, docstring and comment all state 128."
    - "WR-01 / review of 09-14 — `auth mode = WPA2` is pinned as a benign negative and returns False."
  gaps_remaining: []
  regressions: []
advisory: []
human_verification:
  - test: "With a board connected after a confirmed upload, run `uv run scripts/serial_capture.py --id 1_3-police-flasher --seconds 20` and inspect the exit line and the ignored log."
    expected: "Exit 0, a `CAPTURED — N bytes captured` line naming `.skill-state/logs/1_3-police-flasher.log`, and a log holding the raw device bytes."
    why_human: "The automated suite drives a fake `sys.executable -c` child on a PTY; the real `pio device monitor` needs hardware and a serial port."
---

# Phase 9: Agent Workflow and Skills Verification Report

**Phase Goal:** Seven versioned agent skills exist, with `new-homework` and `hw-build` fully usable in guided and one-shot modes.
**Verified:** 2026-10-27T10:52:28Z
**Status:** human_needed
**Re-verification:** Yes — after gap-closure plan 09-14 and the two review fixes (`87ca910`, `27462fb`)

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | A `capture_and_store` capture returns the exact bytes a child wrote to a PTY, including CR, LF, NUL and 0xff; the child sees stdin/stdout as TTYs and a pipe child fails. | ✓ VERIFIED | `scripts/serial_capture.py:150-198`; `test_capture_preserves_every_byte_and_sees_a_tty`, `test_a_pipe_capture_would_fail_the_same_child` pass in the 42-test suite. |
| 2 | A capture refuses with `capture unavailable` when the command cannot start, exits before the bound, or produces zero bytes; reaching the bound with bytes succeeds. | ✓ VERIFIED | `capture_pty` raises on start/early exit; `capture_and_store:275` refuses empty bytes; `main` prefixes `capture unavailable`. |
| 3 | `find_credential` matches the six review shapes, the four ordinary password assignments and the five identifier-suffixed assignments, and does not match the pinned benign set. | ✓ VERIFIED | `scripts/serial_capture.py:104-111`; `CredentialScanTests` (10 tests) pass. Direct probe: all six positives `True`; `secret is`, `the cpwd tool reports ready`, `author wrote nothing here`, `auth mode = WPA2`, boot log all `False`. |
| 4 | `write_log_atomically` anchors under the resolved root, refuses a symlinked `.skill-state`/`logs`/log, leaves no temporary file, and replaces rather than appends. | ✓ VERIFIED | `scripts/serial_capture.py:227-272`; seven `AtomicLogWriteTests` pass. |
| 5 | Two concurrent atomic writes leave exactly one whole payload and no temporary file; a reader never sees a torn log. | ✓ VERIFIED | `test_concurrent_writes_leave_one_whole_payload`, `test_a_concurrent_reader_never_sees_a_torn_log` pass. |
| 6 | `hw-flash` invokes `scripts/serial_capture.py` instead of a piped monitor, normalizes `monitor_speed`, announces the conditional `-e` segment, and calls the bound a success. | ✓ VERIFIED | `.claude/skills/hw-flash/SKILL.md:35-46,69-77,111-122`; no `subprocess.PIPE` in the skill. |
| 7 | The shared guardrails forbid a credential in the state file or any log outside the one scoped capture exception, and state the fail-closed scan shapes. | ✓ VERIFIED | `.claude/skills/_shared/guardrails.md:50-69`; the sentence now names the suffix form and the 128-character bound, matching `CREDENTIAL`. Mirror carries the same text. |
| 8 | The regenerated mirror and `generated.skills.manifest` match the canonical tree, and `scripts/affected.py` maps `scripts/serial_capture.py` to no build impact. | ✓ VERIFIED | `uv run scripts/gen_skills.py --check` exits 0 with every record `UNCHANGED`; `scripts/affected.py:123`; `scripts/tests/test_affected.py:251`. |
| 9 | Seven project-local skills exist, each with `SKILL.md`, `CHANGELOG.md` and `LESSONS.md`; three are active and four are stubs. | ✓ VERIFIED | Seven directories; `hw-build`, `hw-flash`, `new-homework` active; `course-index`, `hw-report`, `schematic`, `simulate` `status: stub`. Version deviation: `new-homework` is `0.2`. |
| 10 | The Phase 4.2 friction log justifies the intake, build and report skills. | ✓ VERIFIED | `.planning/phases/04.2-tracer-homework-1-3/04.2-FRICTION-LOG.md`: `F-01`, `F-03`–`F-05`, `F-11`–`F-13` (intake, build, report). |
| 11 | `new-homework` supports guided and one-shot modes with an adaptive bank ordered mode, board, framework, language, specification, simulation, tests, deliverables. | ✓ VERIFIED | `.claude/skills/new-homework/references/question-bank.md` has the eight `##` sections in that order; dry-run Legs 1 and 3. |
| 12 | Guided mode follows explain → code → run → questions at block granularity and pauses with `[Продовжити | Поясни глибше | Стоп]`; deepening never advances. | ✓ VERIFIED | `.claude/skills/new-homework/SKILL.md:109-119`; dry-run Leg 2. |
| 13 | Both modes checkpoint after intake, after code and after report; guardrails always apply. | ✓ VERIFIED | `references/state-file.md:18-99`; `SKILL.md:135-145`; dry-run Legs 1–3. |
| 14 | Spec-vs-best-practice conflicts and ambiguity produce a recommended assumption transcribed into the report. | ✓ VERIFIED | `guardrails.md:34-48`; dry-run `A-01` and report excerpt. |
| 15 | `hw-build` runs the real target build and native suite, caps each leg at two repairs, preserves warnings, never commits/resets, and escalates with evidence. | ✓ VERIFIED | `hw-build/SKILL.md:45-47,80`; `references/repair-loop.md:3-34,85-98`; dry-run Legs 4–5. |
| 16 | `hw-flash` prints board, environment and exact upload command, requires a literal `так`/`yes`, runs no upload on a non-affirmative answer, and never pre-approves `upload`. | ✓ VERIFIED | `SKILL.md:50-88`; dry-run Leg 6. |
| 17 | `hw-flash` resolves the baud from the project fail-closed; the real homework resolves 115200 and an absent key stops before the monitor. | ✓ VERIFIED | `SKILL.md:35-46`; `platformio.shared.ini:9,27` declares 115200 and `homeworks/1_3-police-flasher/platformio.ini` inherits it. |
| 18 | `hw-flash` wires the user-resolved baud into the helper, so the announced baud is the executed baud. | ✓ VERIFIED | `SKILL.md:69,111` carry `[--baud <n>]`; `:45-46` says the helper appends `-b <n>`; `:73-75` names both conditional segments; `BuildCommandTests` pass. Mirror matches. |
| 19 | **GAP 2 / RR-CR-01:** no skill writes a credential to a log; the guardrails' secrets rule holds across every implemented skill, including keyword-prefixed identifiers. | ✓ VERIFIED | `CREDENTIAL` assignment branch is `[\\w.-]{0,128}[\"']?\\s*[:=]\\s*[\"']?\\S+` (`serial_capture.py:104-111`); the copula branch is unchanged (`\\s+(?:is\\s+)?\\S{6,}`). Direct execution: the four RR-CR-01 shapes and `secret_key_for_production_environment_2026 = hunter2` all `True`; the pinned benign set all `False`. `test_identifier_suffixed_assignments_match` and `test_an_identifier_suffixed_credential_child_writes_nothing` pass; the latter asserts no log and no `.skill-state` directory. |
| 20 | `scripts/gen_skills.py` is the only mirror writer, maintains the manifest, supports `--check`, and the committed tree is in sync. | ✓ VERIFIED | `gen_skills.py --check` exit 0; every mirror file and the manifest `UNCHANGED`. |
| 21 | The drift gate is wired and `affected.py`/`.gitignore`/`AGENTS.md` cover the Phase 9 paths. | ✓ VERIFIED | `.pre-commit-config.yaml:229-230` (`gen-skills-check`); `affected.py:123`; `AGENTS.md` no-build-impact paragraph. |
| 22 | The `.claude/CLAUDE.md` `GSD:skills` block lists exactly seven skills and the decision row records the canonical/mirror split. | ✓ VERIFIED | Seven rows in `.claude/CLAUDE.md:18-24`; `docs/decisions/README.md:33`. |
| 23 | The dry-run transcript records the guided, one-shot, conflict, build-repair and flash-gate legs and contains no credential or private absolute path. | ✓ VERIFIED | `09-DRY-RUN.md` Legs 0–6; grep for `/Users/`, `/home/`, `hunter2` returns nothing. |
| 24 | The full local gate is green. | ✓ VERIFIED | `pre-commit run --all-files` exit 0 (14 hooks); `python3 -m unittest discover scripts/tests` 419 tests OK; `gen_skills.py --check` exit 0. |
| 25 | Both announced capture commands carry `[--baud <n>]`, the prose names `--baud` as the helper option, and the conditional sentence names `[--env <env>]` and `[--baud <n>]`. | ✓ VERIFIED | `SKILL.md:69,73-75,111,114-116,147-149`. |
| 26 | `_build_command` forwards `-e` and `-b` only when supplied; the CLI `CAPTURED`/`REFUSED` payloads and a concurrent reader are pinned by tests. | ✓ VERIFIED | `BuildCommandTests`, `CliResultPayloadTests`, `test_a_concurrent_reader_never_sees_a_torn_log` pass. |
| 27 | The four ordinary password assignments match and the pinned benign set (`secret is`, boot log, `the cpwd tool reports ready`, `author wrote nothing here`) stays unmatched. | ✓ VERIFIED | Executed `find_credential`: the four match; the negatives return False; `CredentialScanTests` pass. |
| 28 | The guardrails sentence names the widened shapes and the mirror/manifest are regenerated. | ✓ VERIFIED | `guardrails.md:55-67`; `gen_skills.py --check` `UNCHANGED`. |
| 29 | `--seconds` rejects NaN, infinity, a non-positive value and an oversized bound before `resolve_root`/`_build_command`/`Popen`, and `capture_pty` reaps the child on an escaping exception. | ✓ VERIFIED | `serial_capture.py` duration validator; CLI `--seconds nan` exits 2 with `ERROR:` and no traceback; `CliDurationTests` and `CaptureReapTests` pass. |
| 30 | **CR-01 (post-verification review):** the connector ceiling is 128 characters, and 32-, 33- and 42-character keyword suffixes all match. | ✓ VERIFIED | `serial_capture.py:104-111` uses `[\\w.-]{0,128}`; `test_a_connector_longer_than_32_characters_matches` pins 32/33/42 and passes; guardrails line 62, the module docstring and the `CREDENTIAL` comment all state 128. |
| 31 | **WR-01 (post-verification review):** `auth mode = WPA2` is pinned as a benign negative and does not match. | ✓ VERIFIED | `test_an_ordinary_word_containing_a_keyword_does_not_match` iterates `the cpwd tool reports ready`, `author wrote nothing here` and `auth mode = WPA2`, all asserted `False`; direct probe confirms `False`. |

**Score:** 31/31 observable truths verified. The 29 prior must-haves are all still verified; truth 19 (the only prior failure) now passes, and the two post-verification review fixes that completed it are recorded as truths 30 and 31. No truth is present-but-behavior-unverified.

### Gap-Closure Contract (09-14)

| 09-14 must-have | Status | Evidence |
|-----------------|--------|----------|
| `find_credential` returns True for the four identifier-suffixed shapes. | ✓ VERIFIED | Direct execution and `test_identifier_suffixed_assignments_match`. |
| Every previously pinned shape still matches and the benign set still returns False. | ✓ VERIFIED | `test_the_review_shapes_match`, `test_the_ordinary_password_assignments_match`, `test_an_ordinary_word_containing_a_keyword_does_not_match`, `test_a_benign_boot_log_does_not_match` pass. |
| `capture_and_store` refuses before the filesystem is touched (no log, no `.skill-state`). | ✓ VERIFIED | `test_an_identifier_suffixed_credential_child_writes_nothing` asserts `CaptureFailed` naming `credential`, no log path and no `.skill-state` directory. |
| The guardrails, docstring and generated mirror name the suffix form and agree with the implementation. | ✓ VERIFIED | `guardrails.md:61-65` (both trees) and the module docstring name `secretKey`, `secret_key`, `passwordHash` and the 128-character bound; `gen_skills.py --check` `UNCHANGED`. |
| `RR-CR-01` is recorded fixed and `T-09-40` closed only on proven coverage. | ✓ VERIFIED (record superseded) | `09-SECURITY.md` frontmatter is `threats_open: 0`, `status: verified`; `T-09-40` row is `closed`. `RR-CR-01` is no longer an ID in the consolidated `09-REVIEW-DISPOSITION.md`; its successor `CR-01` (32-character ceiling) and predecessor `CR-02` (missing assignment forms) are both `disposition: fixed`. The ledger now records `open: 9`, `total: 25` (all Info/Warning), replacing the 09-14 snapshot of `open: 14`, `total: 31`. |
| The capture suite, full Python suite and pre-commit gate are green; `--baud`, `--seconds` and the reaping `finally` behave as before. | ✓ VERIFIED | 42/42 capture tests, 419/419 full suite, 14/14 pre-commit hooks; `BuildCommandTests`, `CliDurationTests`, `CaptureReapTests` pass. |

### Deferred Items

None — no later roadmap phase covers the credential scan or the skill contracts.

### Advisory (New Scope, Unevidenced)

None. Every concern found in this pass is recorded as a warning or info in the anti-pattern table below; none is a blocker and none lacks evidence.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `scripts/serial_capture.py` | PTY capture, fail-closed scan, atomic write, CLI | ✓ VERIFIED | Substantive, stdlib-only; 42 tests drive it. Assignment branch and policy now agree at 128 characters. |
| `scripts/tests/test_serial_capture.py` | PTY, scan, write, argv, payload, duration, reap tests | ✓ VERIFIED | 42 tests, 0 skips, 0 failures. |
| `.claude/skills/hw-flash/SKILL.md` | Helper invocation with `--baud`, consent gate, exact command | ✓ VERIFIED | Both capture commands carry `[--baud <n>]`; consent gate at lines 77-88. |
| `.claude/skills/hw-flash/CHANGELOG.md`, `LESSONS.md` | Dated 09-14 entries | ✓ VERIFIED | Entries present in canonical and mirror. |
| `.claude/skills/_shared/guardrails.md` | General log prohibition and scoped exception naming the 128-character suffix form | ✓ VERIFIED | Lines 50-69; mirrors the implementation. |
| `AGENTS.md` | No-build-impact paragraph names every Phase 9 path | ✓ VERIFIED | `.claude/`, `.agents/`, `.skill-state/`, both ledgers, both scripts. |
| `.agents/skills/**`, `generated.skills.manifest` | Regenerated projections | ✓ VERIFIED | `gen_skills.py --check`: every record `UNCHANGED`. |
| Seven skill directories | Three files each, versioned, four stubs | ✓ VERIFIED | 21 files; `new-homework` at 0.2, six at 0.1; four stubs declared. |
| `04.2-FRICTION-LOG.md` | Intake, build and report entries | ✓ VERIFIED | `F-01`, `F-03`–`F-05`, `F-11`–`F-13`. |
| `09-DRY-RUN.md` | Phase evidence transcript | ✓ VERIFIED | Legs 0–6; sanitized. |
| `09-SECURITY.md` | Closed threat register | ✓ VERIFIED | `threats_open: 0`, `status: verified`, `T-09-40` closed. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| PTY master | `capture_pty` → `find_credential` → `write_log_atomically` → ignored log | `scripts/serial_capture.py` | ✓ WIRED | Tests exercise the exact path; an identifier-suffixed credential is refused before the write. |
| `.claude/skills/hw-flash/SKILL.md` | helper `--baud` → `_build_command` → monitor `-b <n>` | helper CLI | ✓ WIRED | `BuildCommandTests` pin the argv. |
| `_shared/guardrails.md` policy | `find_credential` assignment branch → `capture_and_store` refusal → no file | helper scan | ✓ WIRED | The four identifier-suffixed shapes and the 128-character bound match the policy; end-to-end refusal test passes. |
| `.claude/skills/**` | `gen_skills.py` → `.agents/skills/**` → manifest → `gen-skills-check` | generator | ✓ WIRED | `--check` exit 0; hook present. |
| `affected.py` `NO_BUILD_IMPACT` | `NoBuildImpactTests.NO_BUILD_IMPACT_PATHS` | test tuple | ✓ WIRED | Same path in both. |
| `homeworks/<id>/platformio.ini` | `platformio.shared.ini` → declared 115200 | `extra_configs` inheritance | ✓ WIRED | `monitor_speed = 115200` at lines 9 and 27; the homework extends the shared env. |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| `scripts/serial_capture.py` | raw bytes | PTY master from the child | Yes — exact `bytes(range(256))` | ✓ FLOWING |
| `write_log_atomically` | log bytes | scanned capture bytes | Yes — log equals payload | ✓ FLOWING |
| `gen_skills.py` | mirror bytes | canonical `.claude/skills/**` | Yes | ✓ FLOWING |
| `generated.skills.manifest` | `sha256`/`bytes` | generator transform | Yes | ✓ FLOWING |
| `hw-flash` baud branch | `user_baud` | `monitor_speed` / user answer | Yes — `--baud` reaches `_build_command` | ✓ FLOWING |
| Credential scan | device bytes | `find_credential` | Yes — the four shapes and long suffixes are matched and refused | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Capture suite | `python3 -m unittest scripts.tests.test_serial_capture -v` | `Ran 42 tests … OK`, 0 skips | ✓ PASS |
| Full Python suite | `python3 -m unittest discover scripts/tests` | `Ran 419 tests … OK` | ✓ PASS |
| Named behavior tests | `python3 -m unittest -v …BuildCommandTests …CaptureReapTests …CaptureAndStoreTests` | `Ran 9 tests … OK` | ✓ PASS |
| Credential shapes | direct `find_credential` probe over four RR-CR-01 shapes, a 38-character suffix and six benign lines | positives `[True, True, True, True, True, True]`; negatives `[False × 5]` | ✓ PASS |
| Invalid duration | `python3 scripts/serial_capture.py --id 1_3-police-flasher --seconds nan` | exit 2, `ERROR: --seconds must be a positive finite number no greater than 600` | ✓ PASS |
| Skills mirror | `uv run scripts/gen_skills.py --check` | every record `UNCHANGED`, exit 0 | ✓ PASS |
| Full pre-commit gate | `pre-commit run --all-files` | 14 hooks pass, `RC=0` | ✓ PASS |

### Probe Execution

No `scripts/*/tests/probe-*.sh` probes are declared for this phase; the D-22 dry run is the phase's behavioral evidence.

### Test Quality Audit

| Test File | Linked Req | Active | Skipped | Circular | Assertion Level | Verdict |
|-----------|-----------|--------|---------|----------|-----------------|---------|
| `scripts/tests/test_serial_capture.py` | FLOW-07 | 42 | 0 | No — fixtures are literal bytes, children are independent processes | Behavioral (end-to-end refusal, file absence, PTY byte equality) | PASS |
| `scripts/tests/test_affected.py` | FLOW-01, FLOW-07 | active | 0 | No — path tuples compared to the module constant | Value | PASS |

Disabled tests on requirements: 0. Circular patterns: 0. Insufficient assertions: 0.

### Decision Coverage

All 22 trackable CONTEXT.md decisions are honored by shipped artifacts (`gsd-tools query check.decision-coverage-verify`: `honored: 22`, `total: 22`, `not_honored: []`). Non-blocking.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| FLOW-01 | 09-01, 09-06, 09-07, 09-09, 09-10, 09-11, 09-12, 09-13, 09-14 | Seven skills at version 0.1; `new-homework` and `hw-build` implemented first | ✓ SATISFIED (version deviation) | Seven directories; six at 0.1, `new-homework` at 0.2; mirror, ledger and adapter block wired. |
| FLOW-02 | 09-03, 09-08, 09-09, 09-10, 09-11, 09-12, 09-13, 09-14 | Guided + one-shot with an eight-topic adaptive bank | ✓ SATISFIED | Bank order (mode → board → framework → language → specification → simulation → tests → deliverables) and dry-run Legs 1/3. |
| FLOW-03 | 09-03, 09-08, 09-09, 09-10, 09-11, 09-12, 09-13, 09-14 | Explain → code → run → questions, pause per block, deepen when stuck | ✓ SATISFIED | Block loop `SKILL.md:109-119` and dry-run Leg 2. |
| FLOW-04 | 09-02, 09-03, 09-08, 09-09, 09-10, 09-11, 09-12, 09-13, 09-14 | Checkpoints after intake/code/report; guardrails always apply | ✓ SATISFIED | State schema, three named checkpoints and the shared guardrails. |
| FLOW-05 | 09-03, 09-08, 09-09, 09-10, 09-11, 09-12, 09-13, 09-14 | Conflict/ambiguity with a recorded recommended assumption transcribed into the report | ✓ SATISFIED | `A-01` and report excerpt in the dry run. |
| FLOW-06 | 09-04, 09-08, 09-09, 09-10, 09-11, 09-12, 09-13, 09-14 | Build repaired at most twice, then explained and escalated | ✓ SATISFIED | `repair-loop.md` and dry-run Leg 5. |
| FLOW-07 | 09-01, 09-02, 09-05, 09-08, 09-09, 09-10, 09-11, 09-12, 09-13, 09-14 | `hw-flash` requires explicit confirmation and captures serial logs; four thin stubs | ✓ SATISFIED | Consent gate, baud wiring, 42-test capture suite including the fail-closed credential scan; four stubs declared. The real-hardware capture remains the one manual check below. |

No orphaned requirements: every FLOW ID mapped to this phase appears in at least one plan's `requirements` field.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `09-SECURITY.md` | 72 | The `T-09-40` mitigation cell still names the older `[\\w.-]{0,32}` connector while the code, guardrails and docstring state 128 | ⚠️ WARNING | The record understates the shipped coverage; it does not create a gap and does not reopen the closed threat. |
| `scripts/serial_capture.py` | 128-141 | `_terminate` waits without a bound, and the cleanup `finally` can replace the in-flight exception (prior RR-WR-01) | ⚠️ WARNING | A driver-wedged `pio` child could delay cleanup; a cleanup error could mask the original failure. Not exercised by the phase goal. |
| `09-SECURITY.md` | 110-130 | Three `## Security Audit 2026-10-27` snapshots disagree (39/39, 39/38, 39/39) and the trail table says 33/33 | ℹ️ INFO | Known deliberate residual; the frontmatter (`threats_open: 0`, `status: verified`) is authoritative. |
| `09-REVIEW-DISPOSITION.md` | frontmatter | `RR-CR-01` is absent from the consolidated ledger; counts are `open: 9`, `total: 25`, not the 09-14 snapshot `14/31` | ℹ️ INFO | The later review replaced RR-* IDs with CR-01/CR-02, both `fixed`; the closure is recorded under the successor ID. |
| `scripts/tests/test_serial_capture.py` | 206-210 | The 128-character ceiling is not boundary-pinned at 128/129; the test pins 32/33/42 | ℹ️ INFO | A future lowering to a bound above 42 but below 128 would stay green. No current defect. |
| `scripts/serial_capture.py` | 106-111 | The copula branch matches benign status lines such as `password is required` (prior RR-IN-04) | ℹ️ INFO | A benign capture can be refused; accepted risk R-09-02 bounds it. |

Debt markers: none in the files modified by this phase. The four stub skills contain the word "placeholder" by design (FLOW-07 requires them to remain thin).

### Human Verification Required

**1. Real-hardware capture**

**Test:** With a board connected after a confirmed upload, run `uv run scripts/serial_capture.py --id 1_3-police-flasher --seconds 20`.
**Expected:** Exit 0, a `CAPTURED — N bytes captured` line naming `.skill-state/logs/1_3-police-flasher.log`, and a log whose bytes are the raw device output.
**Why human:** The suite uses a fake `sys.executable -c` child on a PTY; the real `pio device monitor` needs hardware and a serial port. All other acceptance criteria are programmatic.

### Deviations and Residuals

- **`new-homework` is version 0.2, not 0.1.** Quick task `261026-x78` changed the ESP-IDF template to pure C and bumped the skill with a dated changelog. Six skills remain at 0.1. The roadmap SC1 literal is not true for one skill; the intent — a versioned skill — holds and the 0.2 contract is internally consistent. Carried forward as a deviation, not a blocker.
- **The connector admits at most 128 identifier characters.** An assignment whose identifier runs longer than 128 characters would still pass the scan. The guardrails, docstring and comment now state the 128-character bound, so the policy and implementation agree; this is the accepted residual shape of CR-01, not an open gap.
- **`09-SECURITY.md` audit snapshots are stale.** The frontmatter and the `T-09-40` row are current; older snapshot tables are retained historical text. Recorded as info above.
- **FLOW-02…FLOW-06 remain manual-only by decision D-22**, so `09-VALIDATION.md` keeps `nyquist_compliant: false` by design; the dry-run transcript is their evidence.

### Gaps Summary

The prior verification's single blocking gap is closed. The assignment branch of `CREDENTIAL` now admits a `[\\w.-]{0,128}` connector before the separator, so `{"secretKey": "hunter2"}`, `secret_key = hunter2`, `passwordHash: abcdef`, `SECRET_KEY = hunter2` and a 38-character keyword suffix all match, while the copula branch and its six-character floor are byte-for-byte unchanged and the pinned benign set — now including `auth mode = WPA2` — still returns False. `capture_and_store` refuses an identifier-suffixed credential before any log or `.skill-state` directory exists, proven end to end by a named test. The guardrails, module docstring and `CREDENTIAL` comment all state the 128-character bound, and the generated mirror is in sync.

The phase gate is green: 42/42 capture tests, 419/419 full Python tests, `gen_skills.py --check` with every record `UNCHANGED`, and 14/14 pre-commit hooks. All 31 observable truths are verified and no requirement is blocked. The two carried warnings (the stale 32-character mention in the `T-09-40` mitigation cell and the unbounded `_terminate` wait) do not affect the goal and do not reopen a threat. The only remaining item is the manual real-hardware capture, so the status is `human_needed` rather than `passed`.

---

_Verified: 2026-10-27T10:52:28Z_
_Verifier: Claude (gsd-verifier)_

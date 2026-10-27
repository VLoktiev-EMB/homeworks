---
phase: 09-agent-workflow-and-skills
verified: 2026-10-27T00:19:30Z
status: gaps_found
score: 28/29 must-haves verified
covered_files: [".agents/skills/_shared/guardrails.md", ".agents/skills/hw-flash/CHANGELOG.md", ".agents/skills/hw-flash/LESSONS.md", ".agents/skills/hw-flash/SKILL.md", ".claude/skills/_shared/guardrails.md", ".claude/skills/hw-flash/CHANGELOG.md", ".claude/skills/hw-flash/LESSONS.md", ".claude/skills/hw-flash/SKILL.md", ".planning/phases/09-agent-workflow-and-skills/09-01-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-01-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-02-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-02-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-03-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-03-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-04-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-04-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-05-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-05-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-06-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-06-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-07-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-07-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-08-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-08-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-09-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-09-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-10-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-10-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-11-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-11-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-12-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-12-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-13-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-13-SUMMARY.md", "AGENTS.md", "generated.skills.manifest", "scripts/affected.py", "scripts/serial_capture.py", "scripts/tests/test_affected.py", "scripts/tests/test_serial_capture.py"]
covered_digest: "v3:sha256:0799088defaf9980abf247dd26b7b8bb68343b73ab206ceb6aea434466d306f0"
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: gaps_found
  previous_score: 20/22
  gaps_closed:
    - "GAP 1 / CR-03 / truth 18 — the announced baud is now the executed baud: both capture commands carry [--baud <n>], the prose names --baud as the helper option, and BuildCommandTests pin the forwarded -b argv."
    - "GAP 3 / WR-10 — --seconds now rejects NaN, infinity, a non-positive value and an oversized bound with exit 2 before resolve_root, _build_command or Popen."
    - "GAP 4 / WR-11 — capture_pty now kills and reaps the monitor in its outer finally on every exception path; CaptureReapTests exercise the escaping-exception path."
  gaps_remaining:
    - "GAP 2 / WR-12 remainder / RR-CR-01 / truth 19 — the credential scan still requires the separator immediately after the keyword, so camelCase and snake_case assignments (secretKey, secret_key, passwordHash, SECRET_KEY) return False and those bytes would be written to .skill-state/logs/<id>.log under the sole permitted capture exception."
  regressions: []
gaps:
  - truth: "No skill writes a credential to a log; the shared guardrails' secrets rule holds across every implemented skill."
    status: failed
    reason: "The shipped find_credential returns False for `{\"secretKey\": \"hunter2\"}`, `secret_key = hunter2`, `SECRET_KEY = hunter2` and `passwordHash: abcdef`, executed directly against the current tree. capture_and_store calls find_credential and then write_log_atomically, so those bytes would be persisted under the only permitted capture write. The guardrails rule is [MUST]: the scoped exception applies only when the scan finds no `secret`, `password`, `passwd`, `passphrase`, `pwd`, token or API-key assignment. A keyword used as the prefix of a longer identifier is exactly such an assignment. This is the same class as the closed CR-02/WR-12 and remains open as RR-CR-01."
    artifacts:
      - path: "scripts/serial_capture.py"
        issue: "CREDENTIAL (lines 99-103) applies `[\"']?\\s*[:=]\\s*[\"']?\\S+` immediately after `_KEYWORDS`, so `secretKey`, `secret_key`, `SECRET_KEY` and `passwordHash` miss. The module docstring (lines 25-34) claims the keyword may sit inside a larger word without scoping that claim to the leading side."
      - path: "scripts/tests/test_serial_capture.py"
        issue: "REVIEW_SHAPES (lines 37-48) pins the four WR-12 forms but not the identifier-suffixed forms, so the suite cannot fail on this miss."
      - path: ".claude/skills/_shared/guardrails.md"
        issue: "The [MUST] capture exception (lines 55-67) promises a scan that refuses a `secret` assignment; the implementation does not cover the suffix/connector form. The generated mirror carries the same text."
    missing:
      - "Allow an identifier connector before the separator in the assignment branch only (for example `[\\w.-]{0,32}`), leaving the space-separated/copula branch and its six-character floor unchanged."
      - "Add `{\"secretKey\": \"hunter2\"}`, `secret_key = hunter2`, `passwordHash: abcdef` and `SECRET_KEY = hunter2` to the positive fixtures and pin them with a named test."
      - "Name the suffix form in the guardrails sentence and the docstring, then regenerate the mirror with `uv run scripts/gen_skills.py` (never hand-edit `.agents/skills/**`)."
      - "Re-run the capture suite, the full Python suite and `pre-commit run --all-files`, and record RR-CR-01 fixed."
advisory: []
human_verification:
  - test: "With a board connected, run `uv run scripts/serial_capture.py --id 1_3-police-flasher --seconds 20` after a confirmed upload and inspect the exit line and the ignored log."
    expected: "Exit 0, a `CAPTURED — N bytes captured` line naming `.skill-state/logs/1_3-police-flasher.log`, and a log whose bytes are the raw device output."
    why_human: "The automated suite uses a fake `sys.executable -c` child on a PTY; the real `pio device monitor` needs hardware and a serial port."
---

# Phase 9: Agent Workflow and Skills Verification Report

**Phase Goal:** Seven versioned agent skills exist, with `new-homework` and `hw-build` fully usable in guided and one-shot modes.
**Verified:** 2026-10-27T00:19:30Z
**Status:** gaps_found
**Re-verification:** Yes — after gap-closure plans 09-11, 09-12 and 09-13

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | A `capture_and_store` capture returns the exact bytes a child wrote to a PTY, including CR, LF, NUL and 0xff; the child sees stdin/stdout as TTYs and a pipe child fails. | ✓ VERIFIED | `scripts/serial_capture.py:137-184`; `test_capture_preserves_every_byte_and_sees_a_tty`, `test_a_pipe_capture_would_fail_the_same_child` pass (39/39 outside the sandbox). |
| 2 | A capture refuses with `capture unavailable` when the command cannot start, exits before the bound, or produces zero bytes; reaching the bound with bytes succeeds. | ✓ VERIFIED | `capture_pty` raises on start/early exit; `capture_and_store:273-274` refuses empty bytes; `main:335-350` prefixes `capture unavailable`. |
| 3 | `find_credential` matches the six review shapes, does not match a benign boot log, and a match writes nothing. | ✓ VERIFIED | `scripts/serial_capture.py:97-118`; `CredentialScanTests` and `CaptureAndStoreTests.test_a_credential_child_writes_nothing` pass. Narrow: the broader policy still fails at truth 19. |
| 4 | `write_log_atomically` anchors under the resolved root, refuses a symlinked `.skill-state`/`logs`/log, leaves no temporary file, and replaces rather than appends. | ✓ VERIFIED | `scripts/serial_capture.py:220-265`; seven `AtomicLogWriteTests` pass. |
| 5 | Two concurrent atomic writes leave exactly one whole payload and no temporary file; a reader never sees a torn log. | ✓ VERIFIED | `test_concurrent_writes_leave_one_whole_payload`, `test_a_concurrent_reader_never_sees_a_torn_log` pass. |
| 6 | `hw-flash` invokes `scripts/serial_capture.py` instead of a piped monitor, normalizes `monitor_speed`, announces the conditional `-e` segment, and calls the bound a success. | ✓ VERIFIED | `.claude/skills/hw-flash/SKILL.md:35-46,69-75,111-116,133-140`; no `subprocess.PIPE` in the skill. |
| 7 | The shared guardrails forbid a credential in the state file or any log outside the one scoped capture exception, and state the fail-closed scan shapes. | ✓ VERIFIED | `.claude/skills/_shared/guardrails.md:50-69`. Text present; the implementation is narrower (truth 19). |
| 8 | The regenerated mirror and `generated.skills.manifest` match the canonical tree, and `scripts/affected.py` maps `scripts/serial_capture.py` to no build impact. | ✓ VERIFIED | `gen_skills.py --check` exits 0 with every record `UNCHANGED`; `scripts/affected.py:123`, `scripts/tests/test_affected.py:251`. |
| 9 | Seven project-local skills exist, each with `SKILL.md`, `CHANGELOG.md` and `LESSONS.md`; three are active and four are stubs. | ✓ VERIFIED | Seven directories; `hw-build`, `hw-flash`, `new-homework` active; `course-index`, `hw-report`, `schematic`, `simulate` `status: stub`. Version deviation: `new-homework` is `0.2` (see Deviations). |
| 10 | The Phase 4.2 friction log justifies the intake, build and report skills. | ✓ VERIFIED | `04.2-tracer-homework-1-3/04.2-FRICTION-LOG.md`: `F-01`, `F-03`–`F-05`, `F-11`–`F-13`. |
| 11 | `new-homework` supports guided and one-shot modes with an adaptive bank ordered mode, board, framework, language, specification, simulation, tests, deliverables. | ✓ VERIFIED | `.claude/skills/new-homework/references/question-bank.md` has the eight `##` sections in order; dry-run Legs 1 and 3. |
| 12 | Guided mode follows explain → code → run → questions at block granularity and pauses with `[Продовжити | Поясни глибше | Стоп]`; deepening never advances. | ✓ VERIFIED | `.claude/skills/new-homework/SKILL.md:117-119`; dry-run Leg 2. |
| 13 | Both modes checkpoint after intake, after code and after report; guardrails always apply. | ✓ VERIFIED | `references/state-file.md:18-99`; dry-run Legs 1–3. |
| 14 | Spec-vs-best-practice conflicts and ambiguity produce a recommended assumption transcribed into the report. | ✓ VERIFIED | `guardrails.md:34-48`; dry-run `A-01` and report excerpt. |
| 15 | `hw-build` runs the real target build and native suite, caps each leg at two repairs, preserves warnings, never commits/resets, and escalates with evidence. | ✓ VERIFIED | `hw-build/SKILL.md`; `references/repair-loop.md:3-34,85-92`; dry-run Legs 4–5. |
| 16 | `hw-flash` prints board, environment and exact upload command, requires a literal `так`/`yes`, runs no upload on a non-affirmative answer, and never pre-approves `upload`. | ✓ VERIFIED | `SKILL.md:50-88`; dry-run Leg 6. |
| 17 | `hw-flash` resolves the baud from the project fail-closed; the real homework resolves 115200 and an absent key stops before the monitor. | ✓ VERIFIED | `SKILL.md:35-46`; `platformio.shared.ini:9,27` declares 115200 and `homeworks/1_3-police-flasher/platformio.ini` inherits it. |
| 18 | **GAP 1 / CR-03:** `hw-flash` wires the user-resolved baud into the helper, so the announced baud is the executed baud. | ✓ VERIFIED | `SKILL.md:69,111` carry `[--baud <n>]`; `:45-46` says the helper appends `-b <n>`; `:73-75` names both conditional segments; `BuildCommandTests` pass. Mirror `.agents/skills/hw-flash/SKILL.md:70,112` matches. |
| 19 | **GAP 2 / WR-12 remainder:** no skill writes a credential to a log; the guardrails' secrets rule holds across every implemented skill. | ✗ FAILED | Executed `find_credential`: `{"secretKey": "hunter2"}`, `secret_key = hunter2`, `SECRET_KEY = hunter2`, `passwordHash: abcdef` all return False. `capture_and_store` would write them. See gap 1 / RR-CR-01. |
| 20 | `scripts/gen_skills.py` is the only mirror writer, maintains the manifest, supports `--check`, and the committed tree is in sync. | ✓ VERIFIED | `gen_skills.py --check` exit 0; every mirror file and the manifest `UNCHANGED`. |
| 21 | The drift gate is wired and `affected.py`/`.gitignore`/`AGENTS.md` cover the Phase 9 paths. | ✓ VERIFIED | `.pre-commit-config.yaml` `gen-skills-check`; `affected.py:123`; `AGENTS.md` no-build-impact paragraph. |
| 22 | The `.claude/CLAUDE.md` `GSD:skills` block lists exactly seven skills and the decision row records the canonical/mirror split. | ✓ VERIFIED | Seven rows in `.claude/CLAUDE.md:18-24`; `docs/decisions/README.md:33`. |
| 23 | The dry-run transcript records the guided, one-shot, conflict, build-repair and flash-gate legs and contains no credential or private absolute path. | ✓ VERIFIED | `09-DRY-RUN.md` Legs 0–6; grep for `/Users/`, `/home/`, `hunter2`, password assignments returns nothing. |
| 24 | The full local gate is green. | ✓ VERIFIED | `pre-commit run --all-files` exit 0 (14 hooks); `python3 -m unittest discover scripts/tests` 416 tests OK; `gen_skills.py --check` exit 0. |
| 25 | **09-11:** both announced capture commands carry `[--baud <n>]`, the prose names `--baud` as the helper option, and the conditional sentence names `[--env <env>]` and `[--baud <n>]`. | ✓ VERIFIED | `SKILL.md:69,73-75,111,114-116,147-149`. |
| 26 | **09-11:** `_build_command` forwards `-e` and `-b` only when supplied; the CLI `CAPTURED`/`REFUSED` payloads and a concurrent reader are pinned by tests. | ✓ VERIFIED | `BuildCommandTests`, `CliResultPayloadTests`, `test_a_concurrent_reader_never_sees_a_torn_log` pass in the 39-test suite. |
| 27 | **09-12:** the four ordinary password assignments match and the pinned benign set (`secret is`, boot log, `the cpwd tool reports ready`, `author wrote nothing here`) stays unmatched. | ✓ VERIFIED | Executed `find_credential`: the four match; the pinned negatives return False; `CredentialScanTests` pass. |
| 28 | **09-12:** the guardrails sentence names the widened shapes and the mirror/manifest are regenerated. | ✓ VERIFIED | `guardrails.md:55-67`; `gen_skills.py --check` `UNCHANGED`. |
| 29 | **09-13:** `--seconds` rejects NaN, infinity, a non-positive value and an oversized bound before `resolve_root`/`_build_command`/`Popen`, and `capture_pty` reaps the child on an escaping exception. | ✓ VERIFIED | `serial_capture.py:328-331,181-184`; `CliDurationTests` and `CaptureReapTests` pass; CLI `--seconds nan` exits 2 with no traceback. |

**Score:** 28/29 observable truths verified; 1 FAILED (truth 19). The prior report counted 22 must-haves by excluding rows 3 and 6 as narrow task-level truths and scored 20/22; this report adds the five gap-closure truths it verifies, so the same result under the prior convention is 21/22 (only the credential-scan truth still fails).

### Deferred Items

Items not yet met but explicitly addressed in later milestone phases. None — no later phase in the current roadmap covers the credential-scan completeness.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `scripts/serial_capture.py` | PTY capture, scan, atomic write, CLI | ✓ VERIFIED | Substantive, stdlib-only; 39 tests drive it. The scan is narrower than its docstring at truth 19. |
| `scripts/tests/test_serial_capture.py` | PTY, scan, write, argv, payload, duration, reap tests | ✓ VERIFIED | 39 tests, no skip outside the sandbox; 39/39 pass. |
| `.claude/skills/hw-flash/SKILL.md` | Helper invocation with `--baud` and corrected contract | ✓ VERIFIED | CR-03 closed; both capture commands carry `[--baud <n>]`. |
| `.claude/skills/hw-flash/CHANGELOG.md`, `LESSONS.md` | Dated 2026-10-27 entries for 09-11/09-12/09-13 | ✓ VERIFIED | Entries present. |
| `.claude/skills/_shared/guardrails.md` | General log prohibition and widened exception | ✓ VERIFIED | Text present; implementation gap recorded at truth 19. |
| `AGENTS.md` | No-build-impact paragraph names every Phase 9 path | ✓ VERIFIED | `.claude/`, `.agents/`, `.skill-state/`, both ledgers, both scripts. |
| `.agents/skills/**`, `generated.skills.manifest` | Regenerated projections | ✓ VERIFIED | `gen_skills.py --check`: every record `UNCHANGED`. |
| `09-REVIEW-DISPOSITION.md` | Findings recorded accurately | ✓ VERIFIED | `RR-CR-01` recorded `open`; counts `open: 15`, `total: 31`. |
| Seven skill directories | Three files each, versioned, four stubs | ✓ VERIFIED | 21 files; `new-homework` at 0.2, six at 0.1. |
| `04.2-FRICTION-LOG.md` | Intake, build and report entries | ✓ VERIFIED | `F-01`, `F-03`–`F-05`, `F-11`–`F-13`. |
| `09-DRY-RUN.md` | Phase evidence transcript | ✓ VERIFIED | Legs 0–6; sanitized. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| PTY master | `capture_pty` → `find_credential` → `write_log_atomically` → ignored log | `scripts/serial_capture.py` | ✓ WIRED | Tests exercise the exact path. |
| `.claude/skills/hw-flash/SKILL.md` | helper `--baud` → `_build_command` → monitor `-b <n>` | helper CLI | ✓ WIRED | CR-03 closed; `BuildCommandTests` pin the argv. |
| `_shared/guardrails.md` policy | `find_credential` → `capture_and_store` refusal → no file | helper scan | ⚠️ PARTIAL | The four WR-12 forms match, but identifier-suffixed assignments miss (RR-CR-01). |
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
| `hw-flash` baud branch | `user_baud` | `monitor_speed` / user answer | Yes — `--baud` now reaches `_build_command` | ✓ FLOWING |
| Credential scan | device bytes | `find_credential` | Partial — identifier-suffixed assignments pass unscanned | ⚠️ STATIC |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Capture suite | `python3 -m unittest scripts.tests.test_serial_capture -v` (outside the sandbox) | `Ran 39 tests … OK` | ✓ PASS |
| PTY denial is environmental | same command in the sandbox | `OSError: out of pty devices`; retried outside the sandbox | ✓ environmental |
| Full Python suite | `python3 -m unittest discover scripts/tests` (outside the sandbox) | `Ran 416 tests … OK` | ✓ PASS |
| Skills mirror | `uv run scripts/gen_skills.py --check` | every record `UNCHANGED`, exit 0 | ✓ PASS |
| Full pre-commit gate | `pre-commit run --all-files` (outside the sandbox) | 14 hooks pass, `RC=0` | ✓ PASS |
| WR-12 forms | execute `find_credential` on `password is hunter2`, `userpassword = hunter2`, `passphrase = hunter2`, `pwd = hunter2` | all True | ✓ PASS |
| Identifier-suffixed forms | execute `find_credential` on `{"secretKey": "hunter2"}`, `secret_key = hunter2`, `SECRET_KEY = hunter2`, `passwordHash: abcdef` | all False | ✗ FAIL (RR-CR-01) |
| Benign status lines | execute `find_credential` on `password is required`, `auth is required`, `pwd directory` | all True | ⚠️ benign false positives (accepted risk R-09-02) |
| Duration usage error | `serial_capture.py --seconds nan` | exit 2, `ERROR:`, no traceback | ✓ PASS |
| Reap on escaping exception | `CaptureReapTests.test_an_exception_escaping_the_loop_reaps_the_child` | pass; record's `returncode` set | ✓ PASS |

### Probe Execution

No `scripts/*/tests/probe-*.sh` probes are declared for this phase; the D-22 dry run is the phase's behavioral evidence.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| FLOW-01 | 09-01, 09-06, 09-07, 09-09, 09-10, 09-11, 09-12, 09-13 | Seven skills at version 0.1; `new-homework` and `hw-build` implemented first | ✓ SATISFIED (version deviation) | Seven directories; six at 0.1, `new-homework` at 0.2; mirror, ledger and adapter block wired. |
| FLOW-02 | 09-03, 09-08, 09-09, 09-10, 09-11, 09-12, 09-13 | Guided + one-shot with an eight-topic adaptive bank | ✓ SATISFIED | Bank order and dry-run Legs 1/3. |
| FLOW-03 | 09-03, 09-08, 09-09, 09-10, 09-11, 09-12, 09-13 | Explain → code → run → questions, pause per block, deepen when stuck | ✓ SATISFIED | Block loop and dry-run Leg 2. |
| FLOW-04 | 09-02, 09-03, 09-08, 09-09, 09-10, 09-11, 09-12, 09-13 | Checkpoints after intake/code/report; guardrails always apply | ✓ SATISFIED | State schema and guardrails. |
| FLOW-05 | 09-03, 09-08, 09-09, 09-10, 09-11, 09-12, 09-13 | Conflict/ambiguity with a recorded recommended assumption transcribed into the report | ✓ SATISFIED | `A-01` and report excerpt. |
| FLOW-06 | 09-04, 09-08, 09-09, 09-10, 09-11, 09-12, 09-13 | Build repaired at most twice, then explained and escalated | ✓ SATISFIED | `repair-loop.md` and dry-run Leg 5. |
| FLOW-07 | 09-01, 09-02, 09-05, 09-08, 09-09, 09-10, 09-11, 09-12, 09-13 | `hw-flash` requires explicit confirmation and captures serial logs; four thin stubs | ✗ BLOCKED | Consent gate, baud wiring, duration validation and stubs verified; the capture can still persist an identifier-suffixed credential (RR-CR-01). |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `scripts/serial_capture.py` | 99-103 | Assignment branch requires the separator immediately after the keyword, so `secretKey`, `secret_key`, `SECRET_KEY` and `passwordHash` miss | 🛑 BLOCKER | A credential-shaped device line can be written under the sole permitted capture exception (RR-CR-01). |
| `scripts/tests/test_serial_capture.py` | 37-48 | `REVIEW_SHAPES` does not pin the identifier-suffixed forms | ⚠️ WARNING | The suite cannot fail on the blocker above. |
| `.claude/skills/_shared/guardrails.md` (mirror too) | 55-67 | The [MUST] exception promises a `secret` assignment scan the implementation does not fully provide | ⚠️ WARNING | Policy and implementation disagree; same root cause as the blocker. |
| `scripts/serial_capture.py` | 130-134, 181-184 | `_terminate` waits without a bound, and the reaping `finally` can mask the in-flight exception and skip closing the master (RR-WR-01) | ⚠️ WARNING | A driver-wedged `pio` child could delay cleanup, and a cleanup error could replace the original failure. |
| `scripts/serial_capture.py` | 99-103 | The copula branch matches benign status lines (`password is required`, `auth is required`, `pwd directory`), and the docstring overstates negative coverage (RR-IN-04) | ℹ️ INFO | A benign capture can be refused; the guardrails accept occasional false positives (R-09-02). |
| `.claude/skills/hw-flash/SKILL.md` | 69 vs 111-116 | The gate shows `--seconds 20` while execution omits it on the default path (RR-IN-01) | ℹ️ INFO | No capability change; the exact-command invariant is not literally true for that segment. |
| `.claude/skills/hw-flash/SKILL.md` | 178-192 | The helper's exit-2 usage error is outside the four outcome states (RR-IN-02) | ℹ️ INFO | An agent has no defined state for a rejected duration. |
| `scripts/tests/test_serial_capture.py` | 424-457 | `CliDurationTests` prove validation precedes `capture_pty` but not `resolve_root`/`_build_command` (RR-IN-03) | ℹ️ INFO | A future reordering would keep the tests green. |
| `09-SECURITY.md` | 72 | `T-09-40` is marked `closed` while RR-CR-01 is open | ⚠️ WARNING | The security contract overstates the scan's coverage; reopen or annotate when the fix lands. |

### Human Verification Required

| Test | Expected | Why Human |
|------|----------|-----------|
| With a board connected, run `uv run scripts/serial_capture.py --id 1_3-police-flasher --seconds 20` after a confirmed upload and inspect the exit line and the ignored log. | Exit 0, `CAPTURED — N bytes captured`, and a raw device log under `.skill-state/logs/`. | The suite uses a fake PTY child; the real monitor needs hardware and a serial port. |

### Deviations

- **`new-homework` is version 0.2, not 0.1.** Quick task `261026-x78` changed the ESP-IDF template to pure C and bumped the skill with a dated changelog. Six skills remain at 0.1. The roadmap SC1 literal is no longer true for one skill; the intent — a versioned skill — holds, and the 0.2 contract is internally consistent. Carried forward from the previous verification.
- **`09-SECURITY.md` marks `T-09-40` closed.** The gap-closure re-review's RR-CR-01 shows the mitigation is incomplete. The disposition ledger records it honestly as open; the security contract needs the same annotation.

### Gaps Summary

Plans 09-11, 09-12 and 09-13 closed three of the four previous gaps. The baud wiring is genuinely end to end now: both announced capture commands carry `[--baud <n>]`, the prose names the helper option, `_build_command` forwards `-b`, and `BuildCommandTests` pin the argv. `--seconds` rejects non-finite and oversized values with exit 2 before any process starts, and `capture_pty` reaps the monitor on an escaping exception; both are proven by new tests. The capture suite is 39/39 green outside the sandbox, the full Python suite is 416 tests OK, the mirror and manifest are `UNCHANGED`, and the 14-hook pre-commit gate exits 0.

One must-have still fails. The credential scan widened by 09-12 matches the four ordinary password assignments and keeps the pinned benign lines unmatched, but it still requires the separator immediately after the keyword. Executed against the shipped function, `{"secretKey": "hunter2"}`, `secret_key = hunter2`, `SECRET_KEY = hunter2` and `passwordHash: abcdef` all return False, and `capture_and_store` would write those bytes to `.skill-state/logs/<id>.log`. That violates the guardrails' [MUST] secrets rule and the scoped capture exception's own precondition; it is the same class as the closed CR-02/WR-12 and remains open as RR-CR-01. The phase goal therefore is not yet fully achieved. The remaining review findings (the unbounded cleanup wait, the benign copula false positives, the announced-versus-executed duration segment, the exit-2 outcome gap and the ordering test gap) are warnings or informational and do not independently block the goal.

---

_Verified: 2026-10-27T00:19:30Z_
_Verifier: Claude (gsd-verifier)_

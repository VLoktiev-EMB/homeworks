---
phase: 09-agent-workflow-and-skills
verified: 2026-10-26T23:16:35Z
status: gaps_found
score: 14/16 must-haves verified
covered_files: [".agents/skills/_shared/guardrails.md", ".agents/skills/hw-flash/SKILL.md", ".claude/CLAUDE.md", ".claude/skills/_shared/guardrails.md", ".claude/skills/course-index/SKILL.md", ".claude/skills/hw-build/SKILL.md", ".claude/skills/hw-build/references/repair-loop.md", ".claude/skills/hw-flash/CHANGELOG.md", ".claude/skills/hw-flash/LESSONS.md", ".claude/skills/hw-flash/SKILL.md", ".claude/skills/hw-report/SKILL.md", ".claude/skills/new-homework/SKILL.md", ".claude/skills/new-homework/references/question-bank.md", ".claude/skills/new-homework/references/state-file.md", ".claude/skills/schematic/SKILL.md", ".claude/skills/simulate/SKILL.md", ".gitignore", ".planning/phases/09-agent-workflow-and-skills/09-01-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-01-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-02-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-02-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-03-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-03-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-04-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-04-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-05-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-05-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-06-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-06-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-07-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-07-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-08-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-08-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-09-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-09-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-DRY-RUN.md", ".planning/phases/09-agent-workflow-and-skills/09-REVIEW-DISPOSITION.md", ".planning/phases/09-agent-workflow-and-skills/09-REVIEW.md", ".pre-commit-config.yaml", "AGENTS.md", "docs/decisions/README.md", "docs/standards/vscode.md", "generated.manifest", "generated.skills.manifest", "platformio.shared.ini", "scripts/affected.py", "scripts/gen_skills.py", "scripts/tests/temp_root.py", "scripts/tests/test_gen_skills.py", "scripts/tests/test_gen_views.py", "templates/views/shared-ini.ini.tmpl"]
covered_digest: "v3:sha256:2006fca6ab6385849801640e0318caaf45f3112fc2a151f63fb62d397321d50b"
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: gaps_found
  previous_score: 13/15
  gaps_closed:
    - "The `hw-flash` capture resolves `monitor_speed` from the project, stops when the key is absent, and the real homework now resolves 115200; the prior CR-02 (baud) is genuinely closed."
  gaps_remaining:
    - "No skill writes a credential to a log; the guardrails' secrets rule holds across every implemented skill."
    - "The `hw-flash` bounded capture executes and writes the ignored log path."
  regressions: []
gaps:
  - truth: "The `hw-flash` bounded capture runs and writes the ignored `.skill-state/logs/<id>.log` after a confirmed upload."
    status: failed
    reason: "The only executable capture example starts `pio device monitor` with `stdout=subprocess.PIPE` and `stderr=subprocess.PIPE` (`.claude/skills/hw-flash/SKILL.md:119`; mirror `:120`). PlatformIO 6.2.0 gates the monitor on `sys.stdout.isatty()` (`platformio/compat.py:37-39`) and `new_terminal()` raises `UserSideException` when stdout is not a TTY (`platformio/device/monitor/terminal.py:102-109`). Reproduced against the repository's only homework: `pio device monitor -d homeworks/1_3-police-flasher --raw -p /dev/null` with captured stdout returned exit 1 and printed the 'requires an interactive terminal' exception. The snippet therefore raises `CaptureFailed('monitor exited 1 before the bound')` on every run; the 'upload succeeded, capture succeeded' outcome is unreachable and no log is ever written. The dry run stopped at the consent gate (09-DRY-RUN.md Leg 6), so this path was never exercised before."
    artifacts:
      - path: ".claude/skills/hw-flash/SKILL.md"
        issue: "The capture snippet pipes stdout/stderr, which the monitor rejects; the executable example cannot produce a log."
      - path: ".agents/skills/hw-flash/SKILL.md"
        issue: "Generated mirror carries the same non-runnable snippet."
    missing:
      - "Replace the scripted `pio device monitor` invocation with a capture path that works headlessly: talk to the serial port directly (pyserial) or allocate a PTY for the child and read the master, and put the slave in raw mode so the captured bytes are not rewritten (09-REVIEW CR-01)."
      - "Add a deterministic check that exercises the chosen capture path (a fake serial source is enough) so a non-TTY regression cannot ship again."
      - "Regenerate `.agents/skills/` with `uv run scripts/gen_skills.py` after the skill change."
  - truth: "No skill writes a credential to a log; the shared guardrails' secrets rule holds across every implemented skill."
    status: failed
    reason: "The guardrails' only permitted capture write requires that a credential-shape scan of the exact bytes finds no match for 'a token, secret, password, or API-key assignment' (`.claude/skills/_shared/guardrails.md:54-61`). The implementation is `re.compile(rb\"(?i)(token|secret|password|api[_-]?key)[=:]\\s*\\S+\")` (`.claude/skills/hw-flash/SKILL.md:135`; mirror `:136`). Executed against ordinary device-output shapes it misses `secret = hunter2`, `PASSWORD = hunter2`, `{\"token\": \"abc123\"}`, `{\"apiKey\": \"abc123\"}`, `password abc123` and `Authorization: Bearer ...`; only the unspaced `token=abc123` and `secret:abc` forms match. A device that prints an ordinary assignment therefore passes the scan and its bytes are persisted, violating the same file's `[MUST]` prohibition. The exception is closed in form but not in substance."
    artifacts:
      - path: ".claude/skills/hw-flash/SKILL.md"
        issue: "The credential-shape regex requires the separator to touch the keyword and allows no quoting or whitespace, so ordinary assignment forms pass the gate."
      - path: ".agents/skills/hw-flash/SKILL.md"
        issue: "Generated mirror carries the same narrow regex."
      - path: ".claude/skills/_shared/guardrails.md"
        issue: "States the assignment shapes the scan must catch; the implementation does not."
    missing:
      - "Widen the scan to tolerate optional whitespace and quotes around the separator and cover the authorization form, for example `(?i)(?:token|secret|passw(?:or)?d|api[ _-]?key|auth(?:orization)?)[\"']?\\s*[=:]\\s*[\"']?\\S+` (09-REVIEW CR-02)."
      - "Decide explicitly whether the space-separated form (`password abc123`) is fail-closed; if so, add a `\\s+\\S{8,}` alternative and accept occasional false positives."
      - "Regenerate `.agents/skills/` with `uv run scripts/gen_skills.py` after the fix."
---

# Phase 9: Agent Workflow and Skills Verification Report

**Phase Goal:** Seven versioned agent skills exist, with `new-homework` and `hw-build` fully usable in guided and one-shot modes.
**Verified:** 2026-10-26T23:16:35Z
**Status:** gaps_found
**Re-verification:** Yes — after gap closure (plan 09-09)

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Seven project-local skills exist under `.claude/skills/`, each with `SKILL.md`, `CHANGELOG.md` and `LESSONS.md`; `new-homework` and `hw-build` are active and four skills are stubs. | ✓ VERIFIED | `find` inventory: seven directories plus `_shared/`; every skill has the three files. Six are `version: "0.1"`; `new-homework` is `0.2` with a dated changelog (deviation below). `course-index`, `hw-report`, `schematic`, `simulate` carry `status: stub`. |
| 2 | `new-homework` supports guided and one-shot modes with an adaptive question bank in the order mode, board, framework, language, specification, simulation, tests, deliverables. | ✓ VERIFIED | `references/question-bank.md` has all eight `##` sections in that order; `SKILL.md` "Intake" states guided asks the full bank and one-shot asks only non-inferable intake. Dry-run Legs 1 and 3. |
| 3 | Guided mode runs explain → write code → explain → run → questions → pause, with the exact menu `[Продовжити | Поясни глибше | Стоп]`; deepening never advances the block. | ✓ VERIFIED | `.claude/skills/new-homework/SKILL.md:101-133`; dry-run Leg 2 records the menu and `next_block` unchanged after `Поясни глибше`. |
| 4 | Both modes checkpoint after intake, after code and after report; the state file is written before each menu and block pauses do not append named checkpoints. | ✓ VERIFIED | `SKILL.md:135-145`; `references/state-file.md`; dry-run Legs 1–3. |
| 5 | Shared guardrails state the flashing, commit/PR, spec-vs-best-practice, ambiguity and secrets rules with severity and enforcement; conflicts produce a recorded recommendation transcribed into the report. | ✓ VERIFIED | `_shared/guardrails.md` every rule `[MUST] [ENFORCED: review]`; dry-run Leg 3 records `A-01` accepted and transcribed. The secrets rule is contradicted by truth 10. |
| 6 | `hw-build` runs the real target build and native suite with real exit codes, caps each leg at two repairs, preserves warnings, never commits/resets, and escalates with evidence. | ✓ VERIFIED | `hw-build/SKILL.md`; `references/repair-loop.md:8-19,21-35,85-98`; dry-run Legs 4–5 (green build; three errors, exactly two repairs, stop, no third edit). |
| 7 | `hw-flash` prints the board, environment and exact upload command, requires the literal `так`/`yes`, runs no upload on a non-affirmative answer, and never pre-approves `upload`. | ✓ VERIFIED | `hw-flash/SKILL.md:46-94`; dry-run Leg 6 (`ні`, no upload, no capture, no reused confirmation). |
| 8 | `hw-flash` resolves the baud from the project fail-closed; the repository's only real homework resolves 115200 instead of PlatformIO's 9600 default. | ✓ VERIFIED | `platformio.shared.ini:9,27` and `templates/views/shared-ini.ini.tmpl:9,27` declare `monitor_speed = 115200`; `pio project config -d homeworks/1_3-police-flasher --json-output` resolves 115200 for `env:esp32s3_arduino`; `SKILL.md:35-42` stops when the key is absent. Prior CR-02 (baud) is closed; the regression test passes. |
| 9 | The `hw-flash` bounded capture runs and writes `.skill-state/logs/<id>.log`. | ✗ FAILED | The snippet pipes the monitor's stdout; `pio device monitor` requires a TTY and exits 1 immediately. Reproduced directly. See gap 1. |
| 10 | No skill writes a credential to a log; the guardrails' secrets rule holds across every skill. | ✗ FAILED | The credential-shape regex misses ordinary assignment forms (`secret = …`, JSON `{"token": …}`, space-separated, `Authorization: Bearer …`). See gap 2. |
| 11 | `scripts/gen_skills.py` is the only mirror writer, maintains `generated.skills.manifest`, supports `--check`, and the committed tree is in sync. | ✓ VERIFIED | `python3 scripts/gen_skills.py --check` exits 0, every record `UNCHANGED`; 25 mirror files and 25 manifest entries match. |
| 12 | The drift gate is wired: `gen-skills-check` runs at `pre-commit`, watches the generator/ledger/both trees/`scripts/metadata/`, and passes no filenames; `markdownlint-cli2` lints authored skills and excludes the mirror. | ✓ VERIFIED | `.pre-commit-config.yaml:229-239`; the hook is present at `pre-commit` with `pass_filenames: false`. |
| 13 | `.gitignore` exposes `generated.skills.manifest`, ignores `.skill-state/`, and `scripts/affected.py` treats both skill trees, the ledger, the state directory and the generator as no-build-impact. | ✓ VERIFIED | `.gitignore:83,270-272`; `scripts/affected.py:99-120` includes every Phase 9 path. |
| 14 | `AGENTS.md` documents the live skills layout, the drift command, the routing row and the two generated-file classes; `docs/standards/vscode.md` states 14 commit hooks and lists `gen-skills-check` with its repair command. | ✓ VERIFIED | `AGENTS.md:50-59,81-85,243-248,294`; `docs/standards/vscode.md:154,184-186`. |
| 15 | The `.claude/CLAUDE.md` `GSD:skills` block lists exactly seven skills with canonical paths, and `docs/decisions/README.md` records the canonical/mirror decision as `costly`/`accepted`. | ✓ VERIFIED | The block has exactly seven rows; the decision row is dated 2026-10-26 with `costly` and `accepted`. |
| 16 | The dry-run transcript records the guided, one-shot, conflict, build-repair and flash-gate legs, a validation-sampling table, and contains no credential or private absolute path. | ✓ VERIFIED | `09-DRY-RUN.md:687-709,810-860`; `grep` for `/Users/`, `/home/` and token assignments returns nothing. It does not exercise the capture (stopped at the gate). |

**Score:** 14/16 truths verified (0 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `.claude/skills/new-homework/` | `SKILL.md`, two references, changelog, lessons | ✓ VERIFIED | Present and substantive; mirror in sync. |
| `.claude/skills/hw-build/` | `SKILL.md`, `references/repair-loop.md`, changelog, lessons | ✓ VERIFIED | Present and substantive. |
| `.claude/skills/hw-flash/` | `SKILL.md`, changelog, lessons | ⚠️ PRESENT, DEFECTIVE | Present and wired, but the capture cannot run and the credential gate is incomplete. |
| `.claude/skills/{hw-report,schematic,course-index,simulate}/` | Stub `SKILL.md` + changelog + lessons | ✓ VERIFIED | All carry `metadata.status: stub` and a body banner. |
| `.claude/skills/_shared/guardrails.md` | Shared policy | ✓ VERIFIED | Every rule has severity and enforcement; the capture exception has one owner. |
| `.agents/skills/**` | Generated mirror | ✓ VERIFIED | 25 files, all `UNCHANGED` under `--check`. |
| `generated.skills.manifest` | Committed ledger | ✓ VERIFIED | 25 entries, sorted, `owner`/`mode` literals, no self-entry. |
| `scripts/gen_skills.py` | Only mirror owner | ✓ VERIFIED | `--check`/`--json`/`--dir`; suite green. |
| `scripts/tests/test_gen_skills.py`, `temp_root.py` | Integration suite and fixture | ✓ VERIFIED | Present; suite green. |
| `gen-skills-check` hook | Pre-commit drift gate | ✓ VERIFIED | Present at `pre-commit`, no filenames. |
| `docs/decisions/README.md` row | One decision record | ✓ VERIFIED | Dated row present. |
| `.claude/CLAUDE.md` `GSD:skills` | Seven-row generated block | ✓ VERIFIED | Exactly seven rows. |
| `templates/views/shared-ini.ini.tmpl`, `platformio.shared.ini` | Declared monitor baud | ✓ VERIFIED | `monitor_speed = 115200` in both ESP sections. |
| `scripts/tests/test_gen_views.py` | Baud regression test | ✓ VERIFIED | `test_both_esp_sections_declare_the_monitor_baud` passes. |
| `09-DRY-RUN.md` | Phase evidence transcript | ✓ VERIFIED | Complete; capture leg not exercised. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `.claude/skills/<name>/SKILL.md` | `.agents/skills/<name>/SKILL.md` | `gen_skills.py` transform | ✓ WIRED | `--check` exits 0. |
| Every mirror file | `generated.skills.manifest` | `--check` byte comparison | ✓ WIRED | All records `UNCHANGED`. |
| `gen-skills-check` | `gen_skills.py --check` | pre-commit hook | ✓ WIRED | `.pre-commit-config.yaml:229-239`. |
| `.gitignore` negation | Tracked ledger | `!generated.skills.manifest` | ✓ WIRED | Ledger tracked. |
| `affected.py` entries | No-build-impact selection | `NO_BUILD_IMPACT` | ✓ WIRED | Tuple includes all Phase 9 paths. |
| `_shared/guardrails.md` | `new-homework`/`hw-build`/`hw-flash` | `../_shared/guardrails.md` | ✓ WIRED | All three read it before the first write/edit. |
| `course-index` | README generated region | `<!-- BEGIN GENERATED: homeworks -->` | ✓ WIRED | Stub names the exact region. |
| Seven skill directories | `GSD:skills` block | GSD `generate-claude-md` | ✓ WIRED | Seven rows with canonical paths. |
| `templates/views/shared-ini.ini.tmpl` | `platformio.shared.ini` | `gen_views.py` | ✓ WIRED | `--all --check` exit 0. |
| `homeworks/<id>/platformio.ini` | `pio project config` | shared ini inheritance | ✓ WIRED | Resolves 115200 for the real homework. |
| `hw-flash` capture | `.skill-state/logs/<id>.log` | `pio device monitor` → `write_log_atomically` | ✗ NOT_WIRED | The monitor exits 1 before producing bytes, so the write is never reached. |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| `scripts/gen_skills.py` | mirror bytes | canonical `.claude/skills/**` | Yes — reads the authored tree and writes the mirror/ledger | ✓ FLOWING |
| `generated.skills.manifest` | `sha256`/`bytes` | generator transform | Yes — matches the committed mirror | ✓ FLOWING |
| `course-index` stub | README region | root `README.md` generated table | Yes — names the live generated region | ✓ FLOWING (stub, by design) |
| `hw-flash` capture | raw device bytes | `pio device monitor` | No — the process exits 1 on the non-TTY stdout, so no bytes exist to scan or write | ✗ DISCONNECTED |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Generator and mirror are in sync | `python3 scripts/gen_skills.py --check` | exit 0, every record `UNCHANGED` | ✓ PASS |
| Full Python suite | `UV_CACHE_DIR=… python3 -m unittest discover scripts/tests` | `Ran 377 tests … OK` | ✓ PASS |
| Metadata contract | `uv run scripts/check_metadata.py` | `PASS: metadata contract satisfied` | ✓ PASS |
| Generated views in sync | `uv run scripts/gen_views.py --all --check` | exit 0, `UNCHANGED` | ✓ PASS |
| Baud regression test | `python3 -m unittest scripts.tests.test_gen_views.SharedIniTests.test_both_esp_sections_declare_the_monitor_baud` | `Ran 1 test … OK` | ✓ PASS |
| Real homework resolves the baud | `pio project config -d homeworks/1_3-police-flasher --json-output` | `env:esp32s3_arduino 115200` | ✓ PASS |
| Capture command under a pipe | `pio device monitor -d homeworks/1_3-police-flasher --raw -p /dev/null` with captured stdout | exit 1, `UserSideException: … requires an interactive terminal` | ✗ FAIL (proves gap 1) |
| Credential scan coverage | Execute the skill's regex against ordinary assignment samples | misses `secret = hunter2`, `{"token": "abc123"}`, `password abc123`, `Authorization: Bearer …` | ✗ FAIL (proves gap 2) |

### Probe Execution

No `scripts/*/tests/probe-*.sh` probes are declared for this phase; Step 7c is not applicable. The D-22 dry run is the phase's behavioral evidence.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| FLOW-01 | 09-01, 09-06, 09-07 | Seven skills at version 0.1; `new-homework` and `hw-build` fully implemented first | ✓ SATISFIED (with documented version deviation) | Seven directories with changelog + lessons; six at 0.1, `new-homework` at 0.2 after quick task `261026-x78`; live layout and adapter block verified. |
| FLOW-02 | 09-03, 09-08 | `new-homework` guided + one-shot with an adaptive question bank over eight topics | ✓ SATISFIED | Bank sections and dry-run Legs 1/3. |
| FLOW-03 | 09-03, 09-08 | Guided explanation → code → run → questions at block granularity; pauses; deepens | ✓ SATISFIED | `SKILL.md` block loop and dry-run Leg 2. |
| FLOW-04 | 09-02, 09-03, 09-08 | Checkpoints after intake, code, report; guardrails for flashing, commit/PR, conflicts, ambiguity | ✓ SATISFIED | Skill contract and dry-run state excerpts. |
| FLOW-05 | 09-03, 09-08 | Conflicts/ambiguity with a recorded recommended assumption transcribed into the report | ✓ SATISFIED | `A-01` in dry-run Leg 3 and the report assumptions excerpt. |
| FLOW-06 | 09-04, 09-08 | Failing build repaired at most twice, then explained and escalated | ✓ SATISFIED | `repair-loop.md` and dry-run Leg 5. |
| FLOW-07 | 09-01, 09-02, 09-05, 09-08 | `hw-flash` requires explicit confirmation and captures serial logs; four thin stubs | ✗ BLOCKED | Consent gate and four stubs verified, but the capture path cannot run (truth 9) and its credential gate is incomplete (truth 10). |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `.claude/skills/hw-flash/SKILL.md` (mirror too) | 119 / 120 | `subprocess.Popen(..., stdout=subprocess.PIPE)` for a monitor that requires a TTY | 🛑 BLOCKER | The capture leg never runs; the shipped skill's main capability is non-functional. |
| `.claude/skills/hw-flash/SKILL.md` (mirror too) | 135 / 136 | Credential regex misses ordinary assignment forms | 🛑 BLOCKER | A credential can be persisted to the log under the guardrails' only permitted write. |
| `.claude/skills/hw-flash/SKILL.md` | 139, 185 | Log path is cwd-relative, contradicting the repo-root rule three paragraphs later | ⚠️ WARNING | A capture from another directory writes outside the ignored tree. |
| `.claude/skills/hw-flash/SKILL.md` | 167-170, 186-197 | Symlink discipline claims a race-free guarantee the path-based helper does not implement | ⚠️ WARNING | TOCTOU gap; the prose overstates the guarantee. |
| `.claude/skills/hw-flash/SKILL.md` | 142-147, 225 | Outcome table says "failed or timed out" while the prose says the 20-second bound is success | ⚠️ WARNING | A valid log can be discarded or success misreported. |
| `.claude/skills/hw-flash/SKILL.md` | 63 | Consent example omits the conditional `-e <env>` | ⚠️ WARNING | The announced command can differ from the executed one. |
| `.claude/skills/_shared/guardrails.md` | 52-53 | General prohibition now covers only the state file, not logs | ⚠️ WARNING | A future diagnostic log is no longer plainly forbidden from carrying a credential. |
| `.claude/skills/hw-flash/SKILL.md` | 100-112 | Monitor argv omits `--quiet`; the banner would enter the log once the TTY defect is fixed | ⚠️ WARNING | The log would not be the raw device bytes the scan describes. |
| `AGENTS.md` | 67-72 | No-build-impact paragraph omits `.claude/`, `.agents/`, `.skill-state/`, the ledger and the generator | ⚠️ WARNING | The rulebook understates the mapper, although `affected.py` is correct. |
| `.claude/skills/hw-flash/SKILL.md` | 108-140 | `CaptureFailed`, `env`, `needs_e_flag`, `user_baud`, `hw_id` are unbound; `user_baud` is not validated as a positive integer | ℹ️ INFO | The snippet is not runnable as a standalone unit. |
| `.claude/skills/hw-flash/SKILL.md` | 35-43 | `pio project config` emits `monitor_speed` as an integer under `env:` and a string under the base section; no normalization is stated | ℹ️ INFO | A string comparison can misclassify the value as absent. |
| `09-REVIEW-DISPOSITION.md` | — | The post-09-09 review recorded all 15 findings as `open`, including the two critical ones | ℹ️ INFO | The phase currently carries two open critical findings. |

### Deviations

- **`new-homework` is version 0.2, not 0.1.** Quick task `261026-x78` changed the ESP-IDF template to pure C (`src/main.c`, `language: c`) and bumped the skill, with a dated changelog entry. Six skills remain at 0.1. The roadmap SC's literal "0.1" is therefore no longer true for one skill; the intent — a versioned skill — still holds, and the 0.2 contract is internally consistent (`SKILL.md:29-38`, `question-bank.md:46-55`, both templates). If the roadmap literal must be enforced, record an override or amend SC1.

### Gaps Summary

The gap-closure plan 09-09 resolved the baud half of the prior finding: `monitor_speed = 115200` is declared in the shared template and regenerated config, the real homework resolves it through `pio project config`, and the skill stops when the key is absent. The mirror, manifest, hooks and phase gate are all green, and `new-homework` and `hw-build` remain substantively complete.

The remaining gap is concentrated in the `hw-flash` capture (FLOW-07). Two independently reproduced defects block it. First, the only executable capture snippet pipes the monitor's stdout, and PlatformIO's monitor refuses a non-TTY stdout, so every capture exits 1 before any bytes are collected; the "capture succeeded" outcome is unreachable and no log is ever written. Second, the credential-shape scan that gates the one permitted write misses ordinary assignment forms — `secret = hunter2`, JSON `{"token": "abc123"}`, the space-separated form and `Authorization: Bearer …` — so a device printing one of them would have it persisted, contradicting the shared guardrails' `[MUST]`. The dry run stopped at the consent gate, so neither defect had been exercised end to end. The phase goal is therefore not fully achieved while a shipped, non-stub skill's capture is both non-functional and unsafe.

---

_Verified: 2026-10-26T23:16:35Z_
_Verifier: Claude (gsd-verifier)_

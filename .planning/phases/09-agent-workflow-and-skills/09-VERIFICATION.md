---
phase: 09-agent-workflow-and-skills
verified: 2026-10-26T22:42:53Z
status: gaps_found
score: 13/15 must-haves verified
covered_files: [".claude/CLAUDE.md", ".claude/skills/_shared/guardrails.md", ".claude/skills/course-index/SKILL.md", ".claude/skills/hw-build/SKILL.md", ".claude/skills/hw-build/references/repair-loop.md", ".claude/skills/hw-flash/SKILL.md", ".claude/skills/hw-report/SKILL.md", ".claude/skills/new-homework/SKILL.md", ".claude/skills/new-homework/references/question-bank.md", ".claude/skills/new-homework/references/state-file.md", ".claude/skills/schematic/SKILL.md", ".claude/skills/simulate/SKILL.md", ".planning/phases/09-agent-workflow-and-skills/09-01-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-01-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-02-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-02-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-03-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-03-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-04-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-04-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-05-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-05-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-06-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-06-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-07-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-07-SUMMARY.md", ".planning/phases/09-agent-workflow-and-skills/09-08-PLAN.md", ".planning/phases/09-agent-workflow-and-skills/09-08-SUMMARY.md", ".pre-commit-config.yaml", "AGENTS.md", "docs/decisions/README.md", "docs/standards/vscode.md", "generated.skills.manifest", "scripts/affected.py", "scripts/gen_skills.py", "scripts/tests/temp_root.py", "scripts/tests/test_gen_skills.py"]
covered_digest: "v3:sha256:452408aa251290cc8e74671bf757ff2f3613356d41eb304cb320f6cd446d21bf"
behavior_unverified: 0
overrides_applied: 0
gaps:
  - truth: "After a confirmed upload, `hw-flash` reads the serial baud from the project (`monitor_speed`) rather than silently falling back to PlatformIO's default, so the capture works on the repository's only real homework."
    status: failed
    reason: "Neither `platformio.shared.ini` nor `homeworks/1_3-police-flasher/platformio.ini` declares `monitor_speed`, while the skill asserts 'The monitor inherits `monitor_speed` from `platformio.ini`'. `pio device monitor` therefore defaults to 9600, but `homeworks/1_3-police-flasher/report.md:212` records 115200 baud. On the only real project the capture would collect a corrupted stream and still report 'capture succeeded' because bytes were collected (09-REVIEW CR-02)."
    artifacts:
      - path: ".claude/skills/hw-flash/SKILL.md"
        issue: "The baud claim is false for the current repository configuration; no absence check or stop."
      - path: ".agents/skills/hw-flash/SKILL.md"
        issue: "Generated mirror carries the same false claim."
      - path: "platformio.shared.ini"
        issue: "No `monitor_speed` in `[esp32s3_arduino]` or `[env]`."
      - path: "homeworks/1_3-police-flasher/platformio.ini"
        issue: "No `monitor_speed`; the report documents 115200."
    missing:
      - "Declare `monitor_speed = 115200` in the shared/homework PlatformIO configuration, or make `hw-flash` stop and ask when the resolved environment has no `monitor_speed`; never let the monitor silently default to 9600."
      - "Regenerate `.agents/skills/` with `uv run scripts/gen_skills.py` after the skill change."
  - truth: "No skill writes a credential to a log; the shared guardrails' secrets rule holds across every implemented skill."
    status: failed
    reason: "`.claude/skills/_shared/guardrails.md` carries a `[MUST]` 'never write a credential to the state file or a log', and states that no skill may override a rule there with its own prompt wording. `.claude/skills/hw-flash/SKILL.md` nevertheless instructs writing the raw device bytes to `.skill-state/logs/<id>.log` and concedes 'The device may print anything, including a secret.' The mitigation (never quote the log) governs disclosure, not the write, so the raw credential remains in the log (09-REVIEW CR-01)."
    artifacts:
      - path: ".claude/skills/hw-flash/SKILL.md"
        issue: "Instructs an unconditional raw write to a log, contradicting the guardrails."
      - path: ".agents/skills/hw-flash/SKILL.md"
        issue: "Generated mirror carries the same instruction."
      - path: ".claude/skills/_shared/guardrails.md"
        issue: "States the rule the skill violates and forbids the override."
    missing:
      - "Decide one policy and make the two files agree: either a scoped, ignored, local-only exception with mandatory credential-shape redaction or refusal in `hw-flash`, or no raw persistence (keep the bounded bytes in memory and write only a redacted/structured summary)."
      - "Also fix the capture snippet that does not implement the surrounding rules: add `-e <env>` when required, check `proc.returncode`, catch a missing `pio`, and perform the announced atomic log write (09-REVIEW WR-01)."
      - "Update `CHANGELOG.md`/`LESSONS.md` and regenerate the mirror."
---

# Phase 9: Agent Workflow and Skills Verification Report

**Phase Goal:** Seven versioned agent skills exist, with `new-homework` and `hw-build` fully usable in guided and one-shot modes.
**Verified:** 2026-10-26T22:42:53Z
**Status:** gaps_found
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Seven project-local skills exist under `.claude/skills/`, each with `SKILL.md`, `CHANGELOG.md` and `LESSONS.md`; `new-homework` and `hw-build` are active and four skills are stubs. | ✓ VERIFIED | `find .claude/skills -type f` shows seven skill directories plus `_shared/`; all seven have the three files. Six carry `metadata.version: "0.1"`; `new-homework` is `0.2`, a documented quick-task bump (see Deviations). Four carry `metadata.status: stub`. |
| 2 | `new-homework` supports guided and one-shot modes with an adaptive question bank covering mode, board, framework, language, specification, simulation, tests and deliverables, with `mode` first. | ✓ VERIFIED | `references/question-bank.md` has all eight sections in order (`mode`, `board`, `framework`, `language`, `specification`, `simulation`, `tests`, `deliverables`), each with question/default/branch/state key; `SKILL.md` "Intake"; dry-run Legs 1 and 3. |
| 3 | Guided mode runs explain → write code → explain → run → scenario/terminology → pause per block, with the exact pause menu `[Продовжити | Поясни глибше | Стоп]`; `Поясни глибше` re-explains without advancing and depth is never inferred from silence. | ✓ VERIFIED | `.claude/skills/new-homework/SKILL.md` "Block loop"; dry-run Leg 2 records the menu, the deepening answer and `next_block` unchanged. |
| 4 | Both modes checkpoint after intake, after code and after report; the state file is written before each menu and block pauses do not append named checkpoints. | ✓ VERIFIED | `SKILL.md` "Checkpoints"; `references/state-file.md`; dry-run Legs 1–3 record `intake`, `code`, `report` entries and the separate block-pause semantics. |
| 5 | Shared guardrails state the flashing, commit/PR, specification-vs-best-practice, ambiguity and secrets rules with severity and enforcement; conflicts and ambiguity produce a recommended assumption that is transcribed into the report. | ✓ VERIFIED | `.claude/skills/_shared/guardrails.md` carries every rule as `[MUST] [ENFORCED: review]`; `SKILL.md` "Conflicts and ambiguity"; dry-run Leg 3 records `A-01` proposed, accepted and transcribed. (The secrets rule itself is contradicted by `hw-flash` — truth 9.) |
| 6 | `hw-build` runs the real target build and native suite with real exit codes, caps each leg at two repairs, preserves warnings, never commits/resets, and escalates with the six-part payload. | ✓ VERIFIED | `.claude/skills/hw-build/SKILL.md`; `references/repair-loop.md`; dry-run Legs 4–5 (green build; three injected errors, exactly two repairs, escalation, no third edit); this verification re-ran the green build and 38/38 native tests. |
| 7 | `hw-flash` prints the board, environment and exact upload command, requires the literal `так`/`yes`, runs no upload on a non-affirmative answer, and never pre-approves `upload`. | ✓ VERIFIED | `.claude/skills/hw-flash/SKILL.md` "The consent gate"; dry-run Leg 6 (`ні`, no upload, no capture, no reused confirmation). |
| 8 | The `hw-flash` capture reads the baud from the project (`monitor_speed`) and therefore works on the repository's only real homework. | ✗ FAILED | `monitor_speed` is absent from `platformio.shared.ini` and `homeworks/1_3-police-flasher/platformio.ini`; the report documents 115200 while `pio device monitor` defaults to 9600. CR-02. |
| 9 | No skill writes a credential to a log; the guardrails' secrets rule holds across every skill. | ✗ FAILED | `hw-flash` instructs writing raw device bytes to `.skill-state/logs/<id>.log` while conceding a secret may be present, contradicting the guardrails' `[MUST]`. CR-01. |
| 10 | `scripts/gen_skills.py` is the only mirror writer; it projects canonical `.claude/skills/` into `.agents/skills/`, maintains `generated.skills.manifest`, supports `--check`, and the committed tree is in sync. | ✓ VERIFIED | `python3 scripts/gen_skills.py --check` exits 0 with every record `UNCHANGED`; 25 mirror files plus the ledger are tracked; `scripts/tests/test_gen_skills.py` (9 test classes) is part of the green suite. |
| 11 | The drift gate is wired: `gen-skills-check` runs at `pre-commit`, watches the generator/ledger/both trees/`scripts/metadata/`, passes no filenames, and the `markdownlint-cli2` exclusion lints authored skills while excluding the mirror. | ✓ VERIFIED | `.pre-commit-config.yaml:229-239` and `:104`; full `pre-commit run --all-files` exits 0. |
| 12 | `.gitignore` exposes `generated.skills.manifest`, ignores `.skill-state/`, and `scripts/affected.py` treats both skill trees, the ledger, the state directory and the generator as no-build-impact. | ✓ VERIFIED | `.gitignore:83,266-272`; `NO_BUILD_IMPACT` tuple in `scripts/affected.py` includes `.claude/`, `.agents/`, `generated.skills.manifest`, `.skill-state/`, `scripts/gen_skills.py`; `test_affected` is green. |
| 13 | `AGENTS.md` documents the live skills layout, the drift command, the routing row and the two generated-file classes; `docs/standards/vscode.md` states 14 commit hooks and lists `gen-skills-check` with its repair command. | ✓ VERIFIED | `AGENTS.md:50-59,79-85,245-248,294`; `docs/standards/vscode.md:154,184-186`. The stale "project skills planned" sentence is gone. |
| 14 | The `.claude/CLAUDE.md` `GSD:skills` block lists exactly seven skills, and `docs/decisions/README.md` records the canonical/mirror decision as `costly`/`accepted`. | ✓ VERIFIED | The block has seven rows with `.claude/skills/<name>/SKILL.md` paths; decision row dated 2026-10-26. |
| 15 | The D-22 dry-run transcript records the guided, one-shot, conflict, build-repair and flash-gate legs, the validation-sampling table, and contains no credential or private absolute path. | ✓ VERIFIED | `09-DRY-RUN.md`; `grep` for `/Users/`, `/home/` and token assignments returns nothing; the phase gate table records the green commands. |

**Score:** 13/15 truths verified (0 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `.claude/skills/new-homework/` | `SKILL.md`, two references, changelog, lessons | ✓ VERIFIED | Present and substantive; mirror in sync. |
| `.claude/skills/hw-build/` | `SKILL.md`, `references/repair-loop.md`, changelog, lessons | ✓ VERIFIED | Present and substantive. |
| `.claude/skills/hw-flash/` | `SKILL.md`, changelog, lessons | ⚠️ PRESENT, DEFECTIVE | Present and wired, but the capture contract contradicts the guardrails and assumes a missing `monitor_speed`. |
| `.claude/skills/{hw-report,schematic,course-index,simulate}/` | Stub `SKILL.md` + changelog + lessons | ✓ VERIFIED | All carry `metadata.status: stub` and a body banner. |
| `.claude/skills/_shared/guardrails.md` | Shared policy | ✓ VERIFIED | Present; every rule has severity and enforcement. |
| `.agents/skills/**` | Generated mirror | ✓ VERIFIED | 25 files, all `UNCHANGED` under `--check`. |
| `generated.skills.manifest` | Committed ledger | ✓ VERIFIED | 25 entries, sorted, `owner`/`mode` literals, no self-entry. |
| `scripts/gen_skills.py` | Only mirror owner | ✓ VERIFIED | 926 lines; `--check`/`--json`/`--dir`; tests green. |
| `scripts/tests/test_gen_skills.py`, `temp_root.py` | Integration suite and fixture | ✓ VERIFIED | Present; test suite green. |
| `gen-skills-check` hook | Pre-commit drift gate | ✓ VERIFIED | Present and passing. |
| `docs/decisions/README.md` row | One decision record | ✓ VERIFIED | Dated row present. |
| `.claude/CLAUDE.md` `GSD:skills` | Seven-row generated block | ✓ VERIFIED | Exactly seven rows. |
| `09-DRY-RUN.md` | Phase evidence transcript | ✓ VERIFIED | Complete and superseding the pre-`261026-x78` run. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `.claude/skills/<name>/SKILL.md` | `.agents/skills/<name>/SKILL.md` | `gen_skills.py` transform | ✓ WIRED | `--check` exits 0; mirror keeps portable frontmatter, drops Claude-only fields, inserts the marker. |
| Every mirror file | `generated.skills.manifest` | `--check` byte comparison | ✓ WIRED | All records `UNCHANGED`. |
| `gen-skills-check` | `gen_skills.py --check` | pre-commit hook | ✓ WIRED | Hook present at `pre-commit`, `pass_filenames: false`. |
| `.gitignore` negation | Tracked ledger | `!generated.skills.manifest` | ✓ WIRED | `git ls-files` tracks the ledger. |
| `affected.py` entries | No-build-impact selection | `NO_BUILD_IMPACT` | ✓ WIRED | Tuple includes all Phase 9 paths; `test_affected` green. |
| `_shared/guardrails.md` | `new-homework`/`hw-build`/`hw-flash` | `../_shared/guardrails.md` | ✓ WIRED | All three read it before the first write/edit. |
| `course-index` | README generated region | `<!-- BEGIN GENERATED: homeworks -->` | ✓ WIRED | Stub names the exact region. |
| Seven skill directories | `GSD:skills` block | GSD `generate-claude-md` | ✓ WIRED | Seven rows with canonical paths. |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| `scripts/gen_skills.py` | mirror bytes | canonical `.claude/skills/**` | Yes — reads the authored tree and writes the mirror/ledger | ✓ FLOWING |
| `generated.skills.manifest` | `sha256`/`bytes` | generator transform | Yes — matches the committed mirror (`--check` clean) | ✓ FLOWING |
| `course-index` stub | README region | root `README.md` generated table | Yes — names the live generated region, does not re-scan | ✓ FLOWING (stub, by design) |
| `hw-flash` capture | raw device bytes | `pio device monitor` | No — the configured baud source is absent, so the stream would be corrupted; the dry-run never executed the capture | ✗ DISCONNECTED |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Generator and mirror are in sync | `python3 scripts/gen_skills.py --check` | exit 0, every record `UNCHANGED` | ✓ PASS |
| Full Python suite | `UV_CACHE_DIR=... python3 -m unittest discover scripts/tests` | `Ran 376 tests ... OK` | ✓ PASS |
| Metadata contract | `uv run scripts/check_metadata.py` | `PASS: metadata contract satisfied` | ✓ PASS |
| Generated views in sync | `uv run scripts/gen_views.py --all --check` | exit 0, all `UNCHANGED` | ✓ PASS |
| Full pre-commit gate | `pre-commit run --all-files` | exit 0 (the first sandboxed run hit the documented `.claude/skills` write-denial; re-run outside the sandbox passed) | ✓ PASS |
| Pilot target build | `pio run -d homeworks/1_3-police-flasher` | `SUCCESS`, 1 environment | ✓ PASS |
| Pilot native suite | `pio test -d homeworks/1_3-police-flasher -e native` | 38 test cases, 38 succeeded | ✓ PASS |

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
| FLOW-07 | 09-01, 09-02, 09-05, 09-08 | `hw-flash` requires explicit confirmation and captures serial logs; four thin stubs | ⚠️ PARTIAL | Consent gate and four stubs verified; the capture is unsafe and mis-bauded (CR-01, CR-02), so the capture half of the requirement is not met. |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `.claude/skills/hw-flash/SKILL.md` (mirror too) | capture/log section | Raw device write contradicts the guardrails' `[MUST]` secrets rule | 🛑 BLOCKER | CR-01 — a credential may reach a log. |
| `.claude/skills/hw-flash/SKILL.md` (mirror too) | baud section | Claims `monitor_speed` inheritance that the repository does not provide | 🛑 BLOCKER | CR-02 — capture defaults to 9600 on the only real homework. |
| `.claude/skills/hw-flash/SKILL.md` | 88–108 | Snippet omits `-e <env>`, `returncode`, `FileNotFoundError` and the announced log write | ⚠️ WARNING | WR-01 — the executable example does not implement the prose. |
| `scripts/gen_skills.py` | 319–325 | Banner emitted on key presence, including `disable-model-invocation: false` | ⚠️ WARNING | WR-02 — latent invocation-policy inversion. |
| `scripts/gen_skills.py` | 246–318 | Duplicate keys, missing `description`, trailing `name:` comment unhandled | ⚠️ WARNING | WR-03 — under-validation / false rejection. |
| `.claude/skills/new-homework/SKILL.md` | 85–105 | `gen_views` skip condition says exit 2; write mode returns 1 for an absent README; `check_metadata` lacks `--dir` | ⚠️ WARNING | WR-04/WR-05 — the alternate-root path is mis-documented. |
| `AGENTS.md` | 67–72 | No-build-impact paragraph omits `.claude/`, `.agents/`, `.skill-state/`, the ledger and the generator | ⚠️ WARNING | WR-06 — the rulebook understates the mapper. |
| `.pre-commit-config.yaml` | 133–139 | `no-generated-files` omits the `templates/homework-*` generated patterns | ⚠️ WARNING | WR-07 — `git add -f` of a template output passes the hook. |
| `.claude/skills/new-homework/SKILL.md` | 72,83,95,98 | `UV_CACHE_DIR="${TMPDIR:-/tmp}/uv-cache"` falls back to a fixed shared `/tmp` path | ⚠️ WARNING | WR-08 — local symlink/pre-creation risk. |
| `scripts/tests/test_affected.py`, `test_gen_skills.py`, `test_tooling_config.py` | — | Missing edge-case coverage (IN-01, IN-04, IN-05) and stale editor-guide references (IN-02, IN-03) | ℹ️ INFO | No behavioral impact today. |

All 15 `09-REVIEW.md` findings are recorded as `open` in `09-REVIEW-DISPOSITION.md`; none was triaged before verification.

### Deviations

- **`new-homework` is version 0.2, not 0.1.** Quick task `261026-x78` changed the ESP-IDF template to pure C (`src/main.c`, `language: c`) and bumped the skill, with a dated changelog entry. Six skills remain at 0.1. The roadmap SC's literal "0.1" is therefore no longer true for one skill; the intent — a versioned skill — still holds and the deviation is deliberate and documented. If the roadmap literal must be enforced, record an override or amend SC1.
- **The dry run was re-run.** `09-DRY-RUN.md` supersedes the pre-`261026-x78` transcript; this verification uses the re-run and re-executed its build/test legs and phase gate.

### Gaps Summary

The phase delivers the skill system, the generator/mirror pipeline, the rulebook wiring and the `new-homework`/`hw-build` contracts. Both of those skills' workflows are exercised end to end in the dry run and their deterministic parts pass. The gap is concentrated in `hw-flash`'s serial-capture half (FLOW-07): the skill tells the agent to write raw device output that may contain a credential to an ignored log, directly contradicting the shared guardrails' `[MUST]`; and it assumes a `monitor_speed` value that neither the shared nor the homework PlatformIO configuration declares, so the capture would silently run at 9600 against a project documented at 115200. The dry run stopped at the consent gate, so neither defect was exercised end to end. These two critical review findings are blockers: the phase goal is not fully achieved while a shipped, non-stub skill's capture is both unsafe and functionally wrong.

---

_Verified: 2026-10-26T22:42:53Z_
_Verifier: Claude (gsd-verifier)_

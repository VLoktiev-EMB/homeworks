<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

#### Skill home and portability

- **D-01:** The canonical skill tree is `.claude/skills/<name>/SKILL.md`, because Claude
  Code reads only that path; `.agents/skills/` is a generated mirror for the other
  agents. Both trees are committed. — **Reversibility:** costly — every skill path, the
  generator, the pre-commit hook, the Antigravity adapter, and `AGENTS.md` reference this
  layout, so moving it means touching every skill and every consumer.
- **D-02:** The Claude canonical tree may use the full Claude Code frontmatter surface
  (`disable-model-invocation`, `user-invocable`, `model`, `context`, and so on).
  `scripts/gen_skills.py` strips the Claude-only fields when it writes the mirror, so
  `.agents/skills/` advertises only behaviour the other agents can honour. —
  **Reversibility:** reversible — the field policy is local to the generator.
- **D-03:** Invocation is explicit (`/name`) for every skill that writes files or
  touches hardware: `new-homework`, `hw-build`, `hw-flash`, `hw-report`, `schematic`,
  `simulate`. `course-index` is read-only and may be model-invoked by its description. —
  **Reversibility:** reversible.
- **D-04:** `scripts/gen_skills.py` owns the mirror, and `gen_views.py` stays scoped to
  the three view files. The generator's `--check` runs in pre-commit and CI. —
  **Reversibility:** reversible.
- **D-05:** The mirror is committed and registered in the generated manifest, so a fresh
  checkout serves Antigravity without a generator run. — **Reversibility:** costly —
  un-committing means every consumer must run the generator and CI must generate before
  it checks, which changes the drift contract.

#### Guided and one-shot workflow

- **D-06:** A "block" is a deliverable-level unit: scaffold → pure logic/controller →
  native tests → wiring/diagram → report. — **Reversibility:** costly — block boundaries
  are both the pause contract and the checkpoint granularity, so a different unit
  rewrites the guided flow.
- **D-07:** In guided mode the agent writes the block's code, explains it before and
  after, runs it, and asks comprehension questions; the user reviews the diff. —
  **Reversibility:** costly — switching to user-written code changes the entire
  interaction model, not one prompt.
- **D-08:** Every block pause offers `[Продовжити | Поясни глибше | Стоп]`. The skill
  never infers that the user is stuck; depth is a user choice. — **Reversibility:**
  reversible.
- **D-09:** Comprehension questions are mixed: one open "what happens if…" scenario per
  block plus an optional multiple-choice terminology check. — **Reversibility:**
  reversible.
- **D-10:** Non-code blocks (wiring, report) skip the run step and end with explanation
  and questions. — **Reversibility:** reversible.
- **D-11:** `mode` is the first question in the bank and is recorded in the state file.
  One-shot still asks the intake questions it cannot infer, but skips the block pauses
  and the comprehension questions. — **Reversibility:** costly — the mode contract gates
  every later interaction decision.
- **D-12:** The adaptive question bank is prose Markdown at
  `.claude/skills/new-homework/references/question-bank.md`, with conditional branches.
  Coverage of the eight required topics is review-enforced, not doc-sync-tested, because
  the prose/doc-sync tests were pruned in the `261026-ky7` quick task. — **Reversibility:**
  reversible.

#### Checkpoints and state

- **D-13:** One untracked state file per homework at `.skill-state/<id>.json`
  (gitignored), recording mode, intake answers, completed blocks, the next block,
  assumptions and conflicts, and the timestamp and commit of each checkpoint. —
  **Reversibility:** reversible — the file is untracked and can be deleted at any time.
- **D-14:** Checkpoints pause with a short summary and `[Продовжити | Переробити |
  Стоп]`; the state file is written regardless of the choice. — **Reversibility:**
  reversible.
- **D-15:** Specification-versus-best-practice conflicts and ambiguous requirements are
  captured in the state file immediately with a recommended assumption; the report block
  transcribes them into the report's assumptions section. Phase 10 owns the report format
  and its validation. — **Reversibility:** costly — the assumption record becomes a report
  claim that Phase 10 consumes, so changing its shape later means touching both artifacts.

#### Skill contract and stub policy

- **D-16:** Each skill carries `metadata.version: 0.1` in frontmatter plus a
  `CHANGELOG.md` and a `LESSONS.md` in its directory. — **Reversibility:** reversible.
- **D-17:** After a completed run the skill drafts a dated changelog or lessons entry and
  asks `[Записати | Не зараз]`; it never writes the entry without confirmation. —
  **Reversibility:** reversible.
- **D-18:** The only machine check of the skill tree is the mirror drift check in
  `gen_skills.py --check`. Frontmatter validity, the version value, the required files,
  and the stub markers are review-enforced. — **Reversibility:** costly — adding a full
  validator later means retrofitting a contract across seven skills and their mirror.
- **D-19:** Stubs are marked with the portable `metadata.status: stub` field plus a body
  banner naming what the skill does not do and the manual command to use meanwhile. —
  **Reversibility:** reversible.
- **D-20:** `hw-flash` is minimally real: explicit confirmation, `pio run -t upload`, and
  serial capture to an ignored path, with no log interpretation. `hw-report`,
  `schematic`, `simulate`, and `course-index` are stubs. — **Reversibility:** costly —
  success criteria 1 and 5 are evaluated against this split.
- **D-21:** Shared guardrails (flashing, commit/PR, specification conflicts, ambiguity)
  live in `.claude/skills/_shared/guardrails.md`; the implemented skills reference it,
  and the generator mirrors it. — **Reversibility:** reversible.
- **D-22:** Verification is a dry run in a temporary root: `new-homework` scaffolds
  there, `hw-build` runs against homework 1.3, and `hw-flash` stops at its confirmation
  gate without hardware. The transcript is phase evidence. — **Reversibility:**
  reversible.

### Claude's Discretion

- The exact file names under each skill's `references/`, the generator's CLI shape, the
  manifest format, and the pre-commit hook id.
- The schema of `.skill-state/<id>.json`, provided it records every D-13 field.
- The exact wording of the pause menus, confirmation prompts, and escalation messages.
- Whether the state file is deleted after the final checkpoint succeeds. Default: delete
  on success, keep on abort, matching the GSD discuss-checkpoint cleanup.
- The structure of `CHANGELOG.md` and `LESSONS.md` entries, provided each is dated and
  names the run it came from.
- Which stub is promoted first, and the exact stub body wording.
- Whether `course-index` reads the generated root README, `homework.yaml`, or both.

### Deferred Ideas (OUT OF SCOPE)

- **Trigger evals and benchmark mode** — 10–20 `should_trigger` prompts, a rubric
  grader, and pass-rate/time/token benchmarks; not required by this phase and best
  written after the first real use.
- **A full `scripts/check_skills.py` content validator** — declined in favour of the
  drift-only check; revisit if a frontmatter or required-file defect ships.
- **Full `hw-flash` serial-log parsing and report hints** — after the first real hardware
  use.
- **Promoting `hw-report`, `schematic`, `simulate`, or `course-index`** — after each
  skill's first real use.
- **The report assumptions format and its validation** — Phase 10.
- **A real end-to-end `new-homework` run on a live assignment** — Phase 11 or the course
  itself.
- **A dedicated `assumptions.md` per homework** — declined; the state file plus the
  report's assumptions section carry the record.
- **A symlink-based `.agents` relay** — declined in favour of a committed generated
  mirror.
- **A shared question bank across skills** — declined; each skill owns its prose bank.
- **Skill description tuning against model benchmarks** — later, once the skills have
  real usage.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| FLOW-01 | Seven project-local skills at version 0.1; `new-homework` and `hw-build` fully implemented first. | The Skill directory contract (§Standard Stack), the canonical/mirror split (§Architecture Patterns, Pattern 1), and the frontmatter skeleton (§Code Examples 1) give the planner an exact per-skill file set. |
| FLOW-02 | `new-homework` supports guided and one-shot modes with an adaptive question bank covering board, framework, language, mode, specification, simulation, tests, deliverables. | §Architecture Patterns Pattern 3 fixes the bank's section order and branch graph; §Code Examples 4 gives the intake-to-state mapping. The eight topics are review-enforced per D-12. |
| FLOW-03 | Guided mode follows explanation → code → run → questions per block, pauses after each, deepens on request. | §Architecture Patterns Pattern 4 gives the block loop, the exact pause menu, and the explanation-depending-on-stuck contract. |
| FLOW-04 | Both modes checkpoint after intake, after code, after the report; guardrails always apply. | §Code Examples 5 defines the `.skill-state/<id>.json` schema; §Architecture Patterns Pattern 5 defines the three checkpoint points and the guardrail file. |
| FLOW-05 | Spec-vs-best-practice conflicts and ambiguity are presented with a recommended assumption and recorded. | §Code Examples 5 (`assumptions[]`, `conflicts[]`) and §Code Examples 6 (record-and-ask wording) define the record shape and when it is written. |
| FLOW-06 | A failing build is fixed at most twice, then the cause is explained and direction requested. | §Architecture Patterns Pattern 6 fixes the bounded repair loop and the escalation payload; §Environment Availability names the two real commands. |
| FLOW-07 | `hw-flash` requires explicit confirmation and captures serial logs; the four other skills are thin stubs. | §Architecture Patterns Pattern 7 fixes the confirmation gate and the capture path; §Code Examples 7 gives the stub banner and `metadata.status: stub`. |
</phase_requirements>

# Phase 9: Agent Workflow and Skills - Research

**Researched:** 2026-10-26
**Domain:** Agent Skills authoring, deterministic mirror generation, prose workflow contracts
**Confidence:** HIGH for the external skill format and the repository generator pattern; MEDIUM for the skill content contracts (they are design, not facts)

## Summary

Phase 9 adds no new dependency and no new runtime: it adds seven Markdown skill
directories, one generated mirror, one stdlib Python generator, one pre-commit hook, one
gitignore rule, and a dry-run transcript. The external format is stable and well
documented: `SKILL.md` is YAML frontmatter plus Markdown, `name` and `description` are the
only required fields, the body should stay under 500 lines, and references stay one level
deep. Claude Code reads `.claude/skills/` only; Antigravity, Gemini CLI, Codex and Cursor
read `.agents/skills/`, which is exactly the canonical/mirror split already locked in
D-01/D-02.

The repository already contains the generator pattern this phase must copy: a committed
manifest with a SHA-256 and byte count per entry, a plan-then-apply classifier, a
check-only `--check` mode, a `0/1/2` exit vocabulary, and atomic writes. The one structural
collision is that `gen_views.py`'s manifest schema currently accepts **only three
single-segment root files**, so the mirror cannot simply be appended to
`generated.manifest` without editing a generator that D-04 says stays scoped. The
discretion grant on "the manifest format" resolves this: give `gen_skills.py` its own
manifest.

Three details are easy to get wrong and expensive to discover late. First, stripping
`disable-model-invocation` from the mirror does not remove a behaviour — it *widens*
invocation, because absence means "Claude may auto-invoke"; the mirror must carry a body
banner that restates the explicit-only policy. Second, the repository's `.gitignore`
contains `*.manifest` with a single `!generated.manifest` negation, so a second manifest
with that extension is invisible to git unless negated. Third, `markdownlint-cli2`
currently excludes `.claude/` but not `.agents/`, so the generated mirror would be linted
as if it were authored.

**Primary recommendation:** Write the seven canonical skills under `.claude/skills/`,
generate a transformed mirror under `.agents/skills/` with a stdlib-only
`scripts/gen_skills.py` that owns `generated.skills.manifest`, wire
`gen-skills-check` as a check-only pre-commit hook, and prove the workflow with the
locked temporary-root dry run rather than any prose assertion test.

## Project Constraints (from CLAUDE.md)

`./.claude/CLAUDE.md` imports `AGENTS.md`, which wins on conflict. The directives that
constrain this phase:

- **Language:** every repository artifact is English; conversation with the user follows
  the user's language (Ukrainian). The pause menus and prompts are user-facing prose; the
  surrounding `SKILL.md` body stays English.
- **GSD workflow:** file-changing work starts from a GSD command (`/gsd-fast`,
  `/gsd-quick`, `/gsd-debug`, `/gsd-execute-phase`), not a direct edit.
- **Commits:** one atomic commit per change, Conventional Commits `type(scope): summary`
  with `type` in `feat|fix|test|refactor|perf|docs|style|chore`.
- **History:** never push to the default branch, never force-push, never rewrite
  published history; every change arrives through a branch and a squash-merged pull
  request.
- **Gate:** `pre-commit run --all-files`, `uv run scripts/check_metadata.py`,
  `python3 -m unittest discover scripts/tests`, and `pio run` for the affected project are
  the local gate.
- **Check-only hooks:** a hook reports and never rewrites or stages (05/D-21).
- **Generated files:** committed and drift-checked; a hand edit is never the fix.
- **Tests:** stdlib-only; they never import `yaml` or `jsonschema` and shell out to
  `uv run` when a script needs a dependency.
- **Metadata:** a new `homework.yaml` field is a schema change; `task.md` carries the four
  provenance keys and no Cyrillic.
- **Identity:** public handle only; never a private name, institution, or email.
- **Course material:** never commit internal course material or original assignment text.
- **Generator-owned blocks:** the `GSD:skills-*` and `GSD:workflow-*` blocks in
  `.claude/CLAUDE.md` are regenerated, never hand-edited.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Skill discovery and invocation | Agent runtime (Claude Code, Antigravity) | — | The client scans a directory, reads frontmatter, and decides invocation; the repository only declares metadata. |
| Canonical skill content | Repository source (`.claude/skills/`) | — | Authored Markdown is reviewed like any other repository artifact; it is never generated. |
| Mirror generation and drift | Build tooling (`scripts/gen_skills.py` + pre-commit) | CI (`meta` job) | A deterministic transform plus a digest ledger is the only machine check D-18 permits. |
| Scaffold execution | Existing CLI (`scripts/new_homework`) | Agent runtime | The skill orchestrates; it must never reimplement rendering or conflict detection. |
| Build and native test | Existing CLI (`pio`) | Agent runtime | The skill wraps the real commands and captures their exit codes; it does not parse firmware. |
| Checkpoint state | Local untracked workspace (`.skill-state/`) | — | Per-homework, machine-specific, deletable; never a repository artifact. |
| Question bank and guided flow | Skill prose (agent instructions) | — | The flow is a conversation contract, not executable logic; review-enforced. |
| Flash consent | Agent runtime + human | — | A human gate must sit between the skill and `pio run -t upload`; no repository mechanism can grant consent. |

## Standard Stack

### Core

| Library / Tool | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Agent Skills format (`SKILL.md`) | Open specification, current | Skill metadata + instructions | Cross-client standard published at agentskills.io; Claude Code and Antigravity both read a directory of `SKILL.md` files. |
| Claude Code skill runtime | Client-managed (no repo pin) | Discovery, invocation, frontmatter | `.claude/skills/` is the only project path Claude Code scans. |
| Antigravity skill runtime | Client-managed (no repo pin) | Mirror consumer | Antigravity documents `.agents/skills` as its workspace discovery path. |
| Python stdlib (`unittest`, `json`, `hashlib`, `pathlib`) | 3.13.13 (verified) | Generator and tests | The repository's generators and test suite are stdlib-only by policy; no new pin is introduced. |
| pre-commit | 4.7.0 (verified local; pinned in CI as `pre-commit==4.7.0`) | Check-only drift gate | Every existing generator check is a local `language: python` hook. |

### Supporting

| Tool | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `uv` | 0.13.5 (verified) | Run entry scripts with PEP 723 headers | Any command the skill body documents as `uv run scripts/...`; CI installs the same pin. |
| PlatformIO Core | 6.2.0 (verified) | Build, native test, upload | `hw-build` and `hw-flash`; the pins are already in `platformio.shared.ini` and every `homework.yaml`. |
| `wokwi-cli` | 0.28.1 (verified on this machine) | Simulation (stub body only) | Named in the `simulate` stub as the manual command; not executed by this phase. |
| PyYAML | 6.0.3 (already pinned) | Optional frontmatter parse | Only if the planner rejects the stdlib line scanner; it would add `additional_dependencies` to the new hook, matching `gen-views-check`. |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Stdlib line scanner for frontmatter | PyYAML 6.0.3 parse + line-preserving filter | PyYAML is already pinned and robust, but adds a dependency to the new hook environment. The scanner is sufficient because the skill frontmatter contract is a closed subset (flat keys plus one `metadata:` map) and unknown keys are refused. |
| Separate `generated.skills.manifest` | Extend `generated.manifest` with a `skills` owner | One ledger is conceptually simpler, but requires relaxing `gen_views.py`'s single-segment allowlist and creates a shared-file write race between two unsynchronized generators. |
| Transform the mirror | Byte copy with a symlink | Declined in CONTEXT (`symlink-based .agents relay`). A byte copy would also leak Claude-only fields that other clients cannot honour. |
| One `_shared/guardrails.md` | Duplicate guardrails in each skill | Duplication drifts; D-21 locks the shared file and the generator mirrors it. |

**Installation:** none. This phase installs no package. The generator adds no PEP 723
`dependencies` line beyond the standard library.

**Version verification:** `python3 --version` -> `Python 3.13.13`; `uv --version` ->
`uv 0.13.5 (46776a95d 2026-10-21 aarch64-apple-darwin)`; `pio --version` ->
`PlatformIO Core, version 6.2.0`; `pre-commit --version` -> `pre-commit 4.7.0`;
`wokwi-cli --version` -> `wokwi-cli 0.28.1 (7cf4ffaebfd8)`.

## Package Legitimacy Audit

This phase installs no external package. `scripts/gen_skills.py` is stdlib-only, the hook
uses `language: python` with no `additional_dependencies`, and the skills are Markdown.
No registry lookup is required.

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| — (none) | — | — | — | — | — | No packages introduced |

**Packages removed due to [SLOP] verdict:** none.
**Packages flagged as suspicious [SUS]:** none.

If the planner chooses PyYAML for the frontmatter parse, it is the already-pinned
`PyYAML==6.0.3` from ADR-0010, not a new package.

## Architecture Patterns

### System Architecture Diagram

```
Author edits .claude/skills/<name>/SKILL.md
        │
        ▼
scripts/gen_skills.py ──reads──► .claude/skills/**  (authored: SKILL.md, CHANGELOG.md,
        │                                          LESSONS.md, references/, _shared/)
        │
        ├─ transforms SKILL.md frontmatter (strip Claude-only keys, inject banner)
        ├─ byte-copies every other file
        ├─ writes generated.skills.manifest (path, owner, source, sha256, bytes)
        ▼
.agents/skills/**  (committed mirror; read by Antigravity / Gemini / Codex / Cursor)
        │
        ▼
pre-commit: gen-skills-check ──runs──► gen_skills.py --check
        │                              │
        │                              ├─ exit 0: every mirror byte and the manifest match
        │                              ├─ exit 1: MODIFIED / DELETED / ORPHAN drift
        │                              └─ exit 2: usage, symlink, unknown field, unreadable file
        ▼
CI `meta` job: pre-commit run --all-files

Runtime flow (separate from the mirror):
user ──► /new-homework ──► question bank ──► .skill-state/<id>.json
                              │
                              ├─ block: explain → code → run → questions → pause
                              ├─ block: ... (scaffold, controller, tests, wiring, report)
                              └─ final: draft CHANGELOG/LESSONS entry → ask to record
user ──► /hw-build ──► pio run / pio test ──► fix ≤2 ──► explain + escalate
user ──► /hw-flash ──► confirm ──► pio run -t upload ──► pio device monitor ──► ignored log
```

### Recommended Project Structure

```
.claude/skills/
├── _shared/
│   └── guardrails.md              # not a skill: no SKILL.md, mirrored as a file
├── new-homework/
│   ├── SKILL.md
│   ├── CHANGELOG.md
│   ├── LESSONS.md
│   └── references/
│       └── question-bank.md
├── hw-build/
│   ├── SKILL.md
│   ├── CHANGELOG.md
│   ├── LESSONS.md
│   └── references/
│       └── repair-loop.md
├── hw-flash/
│   └── SKILL.md, CHANGELOG.md, LESSONS.md
├── hw-report/                     # stub
├── schematic/                     # stub
├── simulate/                      # stub
└── course-index/                  # stub, model-invocable

.agents/skills/                    # generated; same tree, SKILL.md transformed
scripts/
├── gen_skills.py                  # new: the only mirror owner
└── tests/
    ├── test_gen_skills.py         # new: stdlib unittest
    └── temp_root.py               # extended with a skills fixture builder
generated.skills.manifest          # new: committed mirror ledger (see Pitfall 3)
.skill-state/                      # untracked per-homework checkpoints
```

### Pattern 1: Canonical tree plus transformed mirror

**What:** `.claude/skills/` is authored and may use the full Claude Code frontmatter
surface. `.agents/skills/` is generated: the frontmatter is reduced to the portable set,
the body is preserved, and a generated banner is inserted.

**When to use:** Every file under the canonical tree, on every generator run.

**Field policy (the generator's contract):**

| Class | Fields | Mirror action |
|-------|--------|---------------|
| Required portable | `name`, `description` | Keep |
| Optional portable | `license`, `compatibility`, `metadata`, `allowed-tools` | Keep |
| Claude-only | `disable-model-invocation`, `user-invocable`, `model`, `context`, `argument-hint`, `arguments`, `when_to_use`, `paths`, `hooks`, `shell`, `effort`, `background`, `agent`, `disallowed-tools` | Drop |
| Unknown | anything else | Refuse (exit 2) — never silently drop an unclassified field |

The portable set is the Agent Skills specification's frontmatter table
`[CITED: agentskills.io/specification]`; the Claude-only set is the Claude Code
frontmatter reference `[CITED: code.claude.com/docs/en/skills]`. Antigravity documents only
`name` and `description` `[CITED: antigravity.google/docs/skills/]`, so fields it ignores
are harmless but must not carry a behaviour the mirror claims to honour.

**Why it matters:** a mirror is not a byte copy. It is a *projection* whose semantics must
stay equivalent. See Pitfall 1 for the one field where stripping changes behaviour.

### Pattern 2: Plan-then-apply mirror generation

**What:** copy the shape of `gen_views.py`: load inputs, render every target in memory,
classify against disk and the committed manifest, print `PATH: STATUS — reason` records
(sorted), and only then write through a temporary file plus `os.replace`.

**When to use:** the whole generator; `--check` stops after classification.

**Verbatim contract to reuse** (read this session):

- `gen_views.py:89` — `MANIFEST_PATH = "generated.manifest"`.
- `gen_views.py:43-52` — the `0/1/2` exit vocabulary and the status set
  `CREATE, UNCHANGED, MODIFIED, DELETE`, plus `ERROR` and `ORPHAN`.
- `gen_views.py:84-86` — the generated-file header constant:
  `"<!-- GENERATED — do not edit. Run: uv run scripts/gen_views.py --all -->"`.
- `gen_views.py:104-108` — the write allowlist is exactly three root files:
  ```
  ALLOWED_FILES = (
      "README.md",
      "homeworks.code-workspace",
      "platformio.shared.ini",
  )
  ```
- `gen_views.py:397` — `_validate_entry` calls `_allowed_target(path)`, so **reading** an
  entry outside the allowlist is exit 2, not only writing one.

`[VERIFIED: scripts/gen_views.py:84-108,397]`

### Pattern 3: Prose question bank with conditional branches

**What:** `references/question-bank.md` is a linear set of sections with explicit branch
rules, not a questionnaire schema. The model reads it, chooses the next question from the
answers so far, and records every answer in the state file.

**Required coverage and order (D-11 fixes `mode` first):**

1. `mode` — guided or one-shot. Always asked; recorded before anything else.
2. `board` — default `esp32-s3-devkitc-1`; **corrected 2026-10-26 after review:**
   `scripts/new_homework:90` hardcodes `BOARD = "esp32-s3-devkitc-1"`, so v0.1 scaffolds
   only that board and any other board stops with an unsupported-scaffold escalation.
3. `framework` — Arduino or ESP-IDF; branch from the board and the course module.
4. `language` — **corrected 2026-10-26 after review:** both templates ship `cpp`
   (`templates/homework-espidf/homework.yaml:7`), so the answer is `cpp` for both
   frameworks; ask only to confirm. The earlier `espidf -> c` mapping was wrong.
5. `specification` — ready specification or free-form; branch to "quote the acceptance
   criteria" versus "derive them and record assumptions".
6. `simulation` — yes/no; if yes, ask about Wokwi token availability and the
   ~50-minutes-per-30-days free-plan quota. Simulation is never a build.
7. `tests` — pure logic present? Branch to Unity native tests; record the suite path.
8. `deliverables` — README, report skeleton, diagram, BOM, calculations; record which the
   assignment requires.

**Do not** encode this as YAML or JSON: D-12 locks prose, and a schema turns a
conversation into a form. The eight-topic coverage is review-enforced.

### Pattern 4: The guided block loop

**What:** one block is a deliverable-level unit (D-06). The loop is identical for every
block; only the "run" step differs.

```
for block in [scaffold, controller, native-tests, wiring, report]:
    explain what the block will do and why (one concept per turn)
    write the code
    explain the code that was written
    run the block's verification (skip for wiring/report)
    ask one open "what happens if…" scenario
    ask one optional multiple-choice terminology check
    pause: [Продовжити | Поясни глибше | Стоп]
    write the checkpoint record to .skill-state/<id>.json
```

- "Поясни глибше" re-explains the *same* concept with a smaller step and a concrete
  example; it never advances the block.
- One-shot mode runs the same sequence but skips the pauses and the questions.
- Non-code blocks skip "run" (D-10).

**Why one concept per turn:** the interactive-explanation pattern the CONTEXT cites
(`aipatternbook.com/interactive-explanations`) works because each turn ends with a
comprehension check the user can answer yes/no; a wall of explanation defeats it.

### Pattern 5: Three checkpoints, one state file

**What:** after intake, after the code blocks, and after the report, the skill writes the
same JSON file and pauses with `[Продовжити | Переробити | Стоп]`. The state is written
**before** the menu, whatever the user then chooses (D-14).

**Why before:** a crash, a context compaction, or an abort must leave a resumable record.
Writing after the choice loses the checkpoint exactly when it is needed.

### Pattern 6: Bounded build repair

**What:** `hw-build` runs the target build; on failure it diagnoses, edits, and reruns.
The counter is per run, not per error: **two** repair attempts, then a stop.

```
attempt = 0
while attempt < 2:
    run pio run -d homeworks/<id>
    if exit 0: break
    diagnose the first actionable error
    make the smallest fix
    attempt += 1
if still failing:
    explain the cause, the two attempted fixes, and the evidence
    ask for direction; do not edit again
```

Then run the native suite with the same cap. Do not conflate a warning with an error, and
do not reformat unrelated code to make a build green.

### Pattern 7: Explicit consent before hardware

**What:** `hw-flash` prints the board, environment, and exact command, then waits for a
literal affirmative. A refusal, an empty answer, or any other text is a stop.

- Never pre-approve `upload` through `allowed-tools`; that would let the client skip the
  human gate.
- Serial capture is bounded (`timeout`) and writes to an ignored path, with no
  interpretation of the log.
- Simulation quota and hardware are different resources; never describe a simulation as a
  flash.

### Pattern 8: The seven-skill inventory and the shared guardrails

**What:** each skill is small and owns one job. The table below is the contract the
planner can turn into one task per skill.

| Skill | Status | Invocation | Owns | Manual fallback named by a stub |
|-------|--------|-----------|------|---------------------------------|
| `new-homework` | active | explicit | Intake bank, block loop, state, report block | — |
| `hw-build` | active | explicit | Build + native suite, bounded repair, escalation | — |
| `hw-flash` | active | explicit | Consent gate, upload, bounded serial capture | — |
| `hw-report` | stub | explicit | Will own the 10-section report | `templates/report/report.md` + `docs/standards/` |
| `schematic` | stub | explicit | Will own `assets/diagram.json` edits | the Wokwi diagram editor |
| `simulate` | stub | explicit | Will own the Wokwi run and its evidence | `wokwi-cli ... --diagram-file ... --scenario ...` |
| `course-index` | stub | model or explicit | Will answer "what homeworks exist" from the generated index | read `README.md` between the generated markers |

**`course-index` reads the generated index, not the metadata tree.** The root README's
table is already a projection of every `homework.yaml`
`[VERIFIED: scripts/gen_views.py:252-290]`, so re-scanning `homeworks/` would create a
second answer to the same question. Read the region between
`<!-- BEGIN GENERATED: homeworks -->` and `<!-- END GENERATED -->`.

**`_shared/guardrails.md` outline (four locked topics plus the operational ones):**

1. **Flashing** — show the board and command; require a literal affirmative; never
   default to yes; never pre-approve `upload`.
2. **Commit / PR** — never commit, push, open a PR, or tag without confirmation; one
   atomic commit; Conventional Commits; squash-merge only; the tag goes through
   `scripts/tag_homework.sh` after merge.
3. **Specification versus best practice** — present both, recommend one, record the
   assumption in the state file, and ask before proceeding.
4. **Ambiguity** — ask, or record a recommended assumption and continue only after the
   user accepts it.
5. **Secrets** — never echo a token; record presence as a boolean.
6. **Evidence** — a simulation is never bench evidence; a failed or blocked run never
   produces `verified`.

### Anti-Patterns to Avoid

- **Byte-copying the mirror.** It advertises `disable-model-invocation: true` to clients
  that ignore it, or (worse) strips it and leaves no policy at all.
- **Re-serializing YAML.** `yaml.safe_dump` reorders and re-quotes, so a comment or a
  quoting choice becomes drift. Filter the original lines instead.
- **A content validator.** D-18 declines one; it would reintroduce the prose/doc-sync
  class of test that `261026-ky7` deliberately pruned.
- **A shared manifest written by two generators.** The generators are explicitly not
  serialized (`gen_views.py:33-36`), so last-writer-wins can drop a ledger entry.
- **A skill that reimplements `new_homework`.** Rendering, conflict classification, and
  symlink refusal already exist; a second implementation will drift.
- **Inferring "stuck".** D-08 makes depth a user choice; a skill that auto-deepens on
  silence violates the contract.
- **Recording a token.** The state file must record "token present" as a boolean, never
  `WOKWI_CLI_TOKEN` or any credential.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Scaffolding a homework | A second renderer | `uv run scripts/new_homework <id> --template <name>` | Idempotence, conflict detection, symlink refusal, schema validation, and `0/1/2` exit codes already exist. |
| Template substitution | Jinja or a second placeholder engine | `scripts/metadata/render.py` | One closed `{{name}}` map; unknown tokens and `${...}` are errors `[VERIFIED: scripts/metadata/render.py:28-51]`. |
| Atomic file writes | `Path.write_text` directly | `tempfile.mkstemp` + `os.replace` | A reader never observes half a file; both existing generators use it. |
| Drift ledger | A new checksum format | The `generated.manifest` entry shape (`path`, `owner`, `mode`, `sha256`, `bytes`) | One reviewable shape for every generated artifact. |
| YAML parsing | A regular expression over the whole document | A top-level-key line scanner with a closed field set, or PyYAML | A regex cannot distinguish a nested `description:` from a top-level one. |
| Build execution | A wrapper around `pio` | `pio run -d homeworks/<id>` / `pio test -d homeworks/<id> -e native` | The real command is the evidence; a wrapper hides the exit code. |
| Checkpoint state | SQLite or a workflow engine | `json.dump` to `.skill-state/<id>.json` | The record is small, per-homework, and disposable. |
| Skill invocation and permissions | A dispatcher script | The client runtime (`/name`, `disable-model-invocation`) | The client owns discovery and consent; a repository cannot enforce invocation. |
| Serial capture | A custom pyserial script | `pio device monitor` with `timeout` and a tee to an ignored log | PlatformIO already owns port detection and baud handling. |

**Key insight:** every hand-rolled piece in this phase would duplicate a mechanism the
repository already pays to maintain. The phase's value is the *workflow contract*, not new
infrastructure.

## Common Pitfalls

### Pitfall 1: Stripping `disable-model-invocation` widens invocation

**What goes wrong:** the canonical skill sets `disable-model-invocation: true`; the mirror
drops it because Antigravity does not document it. In the mirror, the default is "the model
may invoke this skill", so a file-writing workflow becomes auto-invocable.

**Why it happens:** the field is framed as a Claude-only *feature*, but its absence is not
neutral — the documented default is model-invocable
`[CITED: code.claude.com/docs/en/skills]` ("default: You can invoke: Yes; Claude can
invoke: Yes").

**How to avoid:** when the canonical frontmatter carries
`disable-model-invocation: true`, the generator inserts a mirror-only line immediately
after the closing `---`:

```markdown
> **Invocation:** explicit only — run `/new-homework`. Do not invoke this skill automatically.
```

The banner is deterministic, testable, and survives clients that ignore every field but
`description`.

**Warning signs:** a mirror `SKILL.md` with no invocation note; a diff that only deletes
lines from the canonical frontmatter.

### Pitfall 2: The mirror is re-serialized instead of filtered

**What goes wrong:** `yaml.safe_dump(yaml.safe_load(frontmatter))` changes quoting, key
order, and comments; every generator run reports `MODIFIED` even when nothing was authored.

**Why it happens:** YAML round-tripping is not byte-stable in general, and the skill body
must stay untouched.

**How to avoid:** parse only to *decide* which top-level keys to drop, then emit the
original frontmatter lines verbatim for the surviving keys. The body is sliced from the
closing fence and copied byte-for-byte.

**Warning signs:** the second run is not idempotent; `--check` fails after a clean
generate.

### Pitfall 3: `*.manifest` hides a second manifest

**What goes wrong:** `generated.skills.manifest` matches the existing blanket rule, so it
is never tracked and a fresh checkout has no ledger.

**Verbatim repository evidence:**

```
262:*.manifest
...
265:!generated.manifest
```

`[VERIFIED: .gitignore:262-265]`

The `no-generated-files` hook lists specific paths and does **not** include the new
manifest, so nothing catches the mistake.

**How to avoid:** add a negation beside the existing one
(`!generated.skills.manifest`), or name the file `generated.skills.json` so the blanket
rule never matches. The negation is more readable and mirrors the existing precedent.

**Warning signs:** `git status --ignored` shows the file; `git ls-files` does not.

### Pitfall 4: The mirror gets linted as authored Markdown

**What goes wrong:** `markdownlint-cli2` excludes `.planning/` and `.claude/` only:

```
98:        exclude: ^(\.planning/|\.claude/)
```

`[VERIFIED: .pre-commit-config.yaml:98]`

A generated `.agents/skills/**/SKILL.md` is therefore linted. A generated file must be
owned by its generator, not by a linter; a markdownlint finding would force a hand edit
that the next generator run erases.

**How to avoid:** extend the exclude to `^(\.planning/|\.claude/|\.agents/)`, exactly as the
existing comment says generated pages are excluded through the hook's regex.

**Warning signs:** a hook failure in a file whose first line says "generated".

### Pitfall 5: `.gitignore` is not the only untracked-state rule

**What goes wrong:** `.skill-state/` is added to `.gitignore`, but `no-generated-files`
does not list it; a `git add -f` could still commit a state file containing a homework
path or a "token present" note.

**How to avoid:** add `.skill-state/` to both the ignore file and the `no-generated-files`
pathspec list, or accept the risk explicitly in the plan. The hook is the only mechanism
that catches `-f`.

**Warning signs:** a state file in `git ls-files`.

### Pitfall 6: `metadata.version: 0.1` is a float

**What goes wrong:** unquoted `0.1` parses as a YAML float. The specification requires
`metadata` to be "a map from string keys to string values"
`[CITED: agentskills.io/specification]`, so a float is out of contract and a strict client
may reject the document.

**How to avoid:** write `version: "0.1"` everywhere, including `CHANGELOG.md` examples.

**Warning signs:** a rendered `0.1` without quotes; a type error in a future validator.

### Pitfall 7: `_shared` is treated as a skill

**What goes wrong:** the generator iterates directories and assumes each has a `SKILL.md`;
`_shared` has none, so the run fails or emits an empty mirror.

**How to avoid:** define the canonical set as "every directory containing `SKILL.md`,
plus `_shared/` as byte-copied files". The client does the same: a directory without
`SKILL.md` is not a skill.

### Pitfall 8: The state file assumes git

**What goes wrong:** a checkpoint records `git rev-parse --short HEAD`, which fails in the
D-22 temporary root.

**How to avoid:** run git with `check=False`; on failure record `"commit": null` and
`"root": "temporary"`. The dry run is then still resumable.

### Pitfall 9: The skill interpolates a user answer into a shell command

**What goes wrong:** `pio run -d homeworks/$ID` where `$ID` came from free text. A value
containing `;` or `$()` becomes command injection.

**How to avoid:** validate the id against `^[0-9]+_[0-9]+-[a-z0-9-]+$` before use
`[VERIFIED: scripts/metadata/paths.py:27]` and pass it as one argv element, never through
a shell string.

## Code Examples

### 1. Canonical `SKILL.md` frontmatter (implemented skill)

```markdown
---
name: new-homework
description: Scaffolds a new PlatformIO homework through the repository's only supported path, then guides the user block by block from intake to report. Use when starting a new assignment, creating a homeworks directory, or asking for the guided homework workflow.
disable-model-invocation: true
metadata:
  version: "0.1"
  status: active
---

# New Homework

Speak to the user in Ukrainian; write every repository file in English.
Read `../_shared/guardrails.md` before the first write.
...
```

**Source:** field names and the explicit-invocation semantics from
`code.claude.com/docs/en/skills`; the `metadata` map from `agentskills.io/specification`.
`name` matches the directory name, as the specification requires.

### 2. The mirror transform (reference implementation)

```python
PORTABLE = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
CLAUDE_ONLY = {
    "disable-model-invocation", "user-invocable", "model", "context",
    "argument-hint", "arguments", "when_to_use", "paths", "hooks",
    "shell", "effort", "background", "agent", "disallowed-tools",
}

def split_frontmatter(text):
    """Return (frontmatter text without its fences, body after the closing fence)."""
    if not text.startswith("---\n"):
        raise CheckError("SKILL.md must start with a '---' frontmatter fence")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise CheckError("SKILL.md frontmatter is not closed")
    return text[4:end + 1], text[end + 5:]

def transform(text, canonical_path, skill_name):
    frontmatter, body = split_frontmatter(text)
    kept, dropped = [], set()
    for key, block in scan_top_level_blocks(frontmatter):
        if key in PORTABLE:
            kept.append(block)
        elif key in CLAUDE_ONLY:
            dropped.add(key)
        else:
            raise CheckError(f"{canonical_path}: unknown frontmatter field {key!r}")
    banner = ""
    if "disable-model-invocation" in dropped:
        banner = (
            f"> **Invocation:** explicit only — run `/{skill_name}`. "
            "Do not invoke this skill automatically.\n"
        )
    marker = "<!-- GENERATED — do not edit. Run: uv run scripts/gen_skills.py -->\n"
    return "---\n" + "".join(kept) + "---\n" + marker + banner + "\n" + body
```

**Design note:** `scan_top_level_blocks` is a strict line scanner: a top-level key starts
at column 0, its block continues through indented and blank lines, and the nested
`metadata:` map is one block. The function returns blocks verbatim, so the surviving
frontmatter is byte-identical to the canonical text. The output is therefore
`---`, the kept frontmatter, `---`, the generated marker, the optional invocation banner,
one blank line, and the untouched body.

### 3. Manifest entry shape (reuse, do not reinvent)

```json
{
  "path": ".agents/skills/new-homework/SKILL.md",
  "owner": "skills",
  "source": ".claude/skills/new-homework/SKILL.md",
  "mode": "whole",
  "sha256": "<64 lowercase hex>",
  "bytes": 1234
}
```

**Source:** the shape is the existing `generated.manifest` entry contract
`[VERIFIED: scripts/gen_views.py:475-491]`, with one added `source` key. The manifest is
sorted by `path`, declares `"version": 1`, and never lists itself.

### 4. Intake answer to state record

```json
{
  "schema_version": 1,
  "homework_id": "1_4-dry-run",
  "skill": "new-homework",
  "mode": "guided",
  "intake": {
    "board": "esp32-s3-devkitc-1",
    "framework": "arduino",
    "language": "cpp",
    "specification": "free-form",
    "simulation": "wokwi",
    "simulation_token_present": false,
    "tests": "unity-native",
    "deliverables": ["readme", "report", "diagram"]
  },
  "blocks": [
    {"id": "scaffold", "status": "done"},
    {"id": "controller", "status": "in-progress"}
  ],
  "next_block": "controller",
  "assumptions": [],
  "conflicts": [],
  "checkpoints": [
    {"name": "intake", "at": "2026-10-26T20:00:00Z", "commit": "abc1234"}
  ]
}
```

Every D-13 field is present: mode, intake answers, completed blocks, next block,
assumptions and conflicts, and a timestamp plus commit per checkpoint.

### 5. Assumption record (FLOW-05, D-15)

```json
{
  "id": "A-01",
  "kind": "spec-conflict",
  "topic": "third LED pin",
  "specification": "GPIO5",
  "best_practice": "GPIO6, because GPIO5 is a strapping pin",
  "recommendation": "Use GPIO6 and record the deviation.",
  "impact_if_wrong": "The wiring diagram and pin map change; the controller is unaffected.",
  "recorded_at": "2026-10-26T20:10:00Z",
  "commit": null,
  "status": "proposed"
}
```

The report block transcribes each `status: accepted` record into the report's assumptions
section. Phase 10 owns that section's format.

### 6. The three pause menus (user-facing Ukrainian)

```text
Block pause (D-08):        [Продовжити | Поясни глибше | Стоп]
Checkpoint (D-14):         [Продовжити | Переробити | Стоп]
Changelog/lessons (D-17):  [Записати | Не зараз]
Flash consent:             explicit affirmative only; no default, no pre-approved upload
```

These literals are the user-facing interface. The surrounding skill prose stays English;
the Cyrillic machine gate is scoped to `task.md` only
`[VERIFIED: scripts/metadata/contract.py:253-256]`.

### 7. Stub banner (D-19)

```markdown
---
name: simulate
description: Placeholder for running the Wokwi scenario and recording its evidence. Use only to look up the manual simulation command until this skill is promoted.
disable-model-invocation: true
metadata:
  version: "0.1"
  status: stub
---

# Simulate (stub)

> **Stub (v0.1).** This skill does not run a simulation, read serial output, or write a
> measurement-ledger row. Until it is promoted, run the documented command yourself:
> `wokwi-cli homeworks/<id> --diagram-file assets/diagram.json --scenario scenario.yaml`
> after `pio run -d homeworks/<id>`. A run consumes the Wokwi free-plan quota; simulation
> is never a build and never bench evidence.
```

### 8. The check-only hook block

```yaml
      - id: gen-skills-check
        name: generated skills mirror is in sync
        language: python
        entry: python scripts/gen_skills.py --check
        files: >-
          (?x)^(\.claude/skills/|\.agents/skills/
          |scripts/gen_skills\.py$|generated\.skills\.manifest$)
        pass_filenames: false
        stages: [pre-commit]
```

**Source:** the shape of the existing `gen-views-check` hook
`[VERIFIED: .pre-commit-config.yaml:188-200]`, which is `language: python`,
check-only, `pass_filenames: false`, and `stages: [pre-commit]`. No
`additional_dependencies` is needed for a stdlib-only generator.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Custom slash commands in `.claude/commands/` | Skills in `.claude/skills/<name>/SKILL.md` | Claude Code v2.1.x | Skills add supporting files and the full frontmatter surface; commands still work as the older format `[CITED: code.claude.com/docs/en/skills]`. |
| One agent's private skill directory | `.agents/skills/` as a cross-client path | 2026 | Antigravity, Gemini CLI, Codex, and Cursor read it; Claude Code does not `[CITED: antigravity.google/docs/skills/]` `[CITED: github.com/anthropics/claude-code/issues/66352]`. |
| A monolithic `SKILL.md` | Progressive disclosure: metadata, then body, then one-level references | Current | Keep the body under 500 lines and move detail into `references/` `[CITED: platform.claude.com/.../best-practices]`. |
| Prose-only skills | Skills that bundle scripts for deterministic steps | Current | The generator and the build commands stay scripts; the skill orchestrates. |
| Ad-hoc skill testing | Eval-driven skill authoring | Current | Deferred by CONTEXT; no trigger evals in this phase. |

**Deprecated/outdated:**

- `.claude/commands/` is documented as the older format; new skills go to
  `.claude/skills/`.
- A "universal" `.agents` symlink relay: declined in CONTEXT; the mirror is a committed
  transformed copy.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | A second manifest named `generated.skills.manifest` satisfies D-05's "the generated manifest", using the explicit discretion grant on "the manifest format". | Standard Stack; Pitfall 3 | The planner must instead extend `generated.manifest` and relax `gen_views.py`'s allowlist, adding a shared-file write race. |
| A2 | An English `description` is enough for `course-index` to auto-trigger on Ukrainian requests. | Pattern 3; Open Questions | Ukrainian phrasing may not auto-invoke it; the user must type `/course-index`. The fallback is acceptable but must be recorded. |
| A3 | Antigravity and the other `.agents/skills` clients ignore unknown frontmatter fields rather than rejecting the skill. | Pattern 1 | If a client rejects unknown fields, the mirror must also strip `license`, `compatibility`, and `metadata`. |
| A4 | `metadata.version` must be a quoted string because the specification defines `metadata` as string-to-string. | Pitfall 6 | An unquoted `0.1` may be accepted by lenient clients but is out of contract. |
| A5 | `pio device monitor` is available and bounded capture can be expressed with the host `timeout` command. | Pattern 7 | On a platform without `timeout`, `hw-flash` needs a Python subprocess timeout instead. |
| A6 | The D-22 dry run is sufficient evidence for the prose contracts; no trigger eval is required. | Validation Architecture | Success criteria 2-5 stay review-enforced rather than machine-proven, which is what D-18 already accepts. |

**If this table were empty:** every claim would be verified; it is not, because the skill
content contracts and the manifest choice are design decisions.

## Open Questions

1. **Should the mirror keep `license` and `compatibility`?**
   - What we know: both are in the Agent Skills specification's optional set.
   - What's unclear: Antigravity documents only `name` and `description`.
   - Recommendation: keep `license: MIT` (repo-wide licence, harmless); omit
     `compatibility` unless a skill actually needs a system package.

2. **Should the phase update the hook count in `docs/standards/vscode.md`?**
   - What we know: the guide says "13 hooks run on commit and 2 on push" and lists
     `gen-views-check`; adding `gen-skills-check` makes 14. The test that asserted the
     count was removed in `261026-ky7`.
   - What's unclear: whether the guide edit belongs to this phase or Phase 10.
   - Recommendation: update it here; it is a three-line authored-doc change and the guide
     is the onboarding surface the skills point at.

3. **Should `new-homework` run `gen_views.py --all` after scaffolding?**
   - What we know: the root README row, the workspace folder, and the shared ini are
     generated, and Phase 4.2 recorded the manual edit as friction.
   - What's unclear: whether a guided run should touch three root files.
   - Recommendation: run it inside the scaffold block, show the diff, and let the user
     review it as part of that block's checkpoint.

4. **Which native suite does `hw-build` run?**
   - What we know: the homework has `[env:native]` and the shared `tests/` project has
     its own native suite.
   - What's unclear: whether both run on every build.
   - Recommendation: always run the homework's native env; run the shared suite when the
     diff touches `lib/`, mirroring `scripts/affected.py`'s fan-out rule.

5. **Should the mirror carry `allowed-tools`?**
   - What we know: the field is experimental and Antigravity does not document it.
   - What's unclear: whether pre-approving `pio run`/`pio test` is desirable.
   - Recommendation: omit it entirely. Pre-approval must never cover upload or commit.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3 | Generator + stdlib suite | ✓ | 3.13.13 | — |
| `uv` | Entry script execution in tests and docs | ✓ | 0.13.5 | `python3` directly for the stdlib-only generator |
| PlatformIO Core | `hw-build`, `hw-flash` | ✓ | 6.2.0 | — |
| `git` | Checkpoint commit field | ✓ | 2.54.0 | Record `null` in a temporary root |
| `pre-commit` | Local drift gate | ✓ | 4.7.0 | CI runs the same pinned version |
| `wokwi-cli` | `simulate` stub's manual command | ✓ | 0.28.1 | Documented command only; not executed |
| ESP32-S3 board | `hw-flash` live leg | ✗ | — | Dry run stops at the confirmation gate (D-22) |
| Wokwi token | Simulation execution | ✗ (not assumed) | — | Record `simulation_token_present: false`; do not simulate |

**Missing dependencies with no fallback:** none that block the phase goal. The live flash
leg is deliberately out of scope.

**Missing dependencies with fallback:** the ESP32-S3 board and the Wokwi token; the dry
run exercises only the gate, and the stub names the manual command.

## Validation Architecture

> Included because `workflow.nyquist_validation` is `true` in `.planning/config.json`.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Python stdlib `unittest` (no third-party runner) |
| Config file | none — discovery by module path |
| Quick run command | `python3 -m unittest scripts.tests.test_gen_skills -v` |
| Full suite command | `python3 -m unittest discover scripts/tests` |
| Hook check | `pre-commit run gen-skills-check --all-files` |

The CI `python-tests` job runs exactly
`python -m unittest discover scripts/tests` `[VERIFIED: .github/workflows/ci.yml:231]`,
and the repository convention is that tests never import `yaml` or `jsonschema`
`[VERIFIED: scripts/tests/temp_root.py:1-17]`.

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| FLOW-01 | Seven skill directories exist at v0.1 with changelog and lessons | manual/review (D-18) | — | ❌ review only |
| FLOW-01 | The mirror matches the canonical tree byte for byte | smoke | `uv run scripts/gen_skills.py --check` | ❌ Wave 0 (after the tree exists) |
| FLOW-02 | Guided and one-shot intake covers all eight topics | manual dry run (D-22) | — | ❌ transcript |
| FLOW-03 | Guided block loop pauses with the exact menu and deepens on request | manual dry run | — | ❌ transcript |
| FLOW-04 | Checkpoints after intake, code, and report; guardrails always apply | manual dry run + JSON inspection | — | ❌ transcript |
| FLOW-05 | Conflicts and ambiguity produce a recorded recommendation | manual dry run + JSON inspection | — | ❌ transcript |
| FLOW-06 | A failing build is repaired at most twice, then escalated | manual dry run against a broken fixture | — | ❌ transcript |
| FLOW-07 | `hw-flash` stops at confirmation; four stubs carry `metadata.status: stub` | manual dry run + review | — | ❌ transcript |
| — | Frontmatter transform strips Claude-only keys, keeps the body, injects the banner | unit | `python3 -m unittest scripts.tests.test_gen_skills -v` | ❌ Wave 0 |
| — | Unknown frontmatter key exits 2 | unit | same | ❌ Wave 0 |
| — | `--check` reports MODIFIED/DELETED/ORPHAN and writes nothing | unit | same | ❌ Wave 0 |
| — | Two generator runs are byte-identical | unit | same | ❌ Wave 0 |
| — | Manifest entries are sorted, digest-correct, and never list the manifest | unit | same | ❌ Wave 0 |
| — | `_shared/` is mirrored as files, not as a skill | unit | same | ❌ Wave 0 |
| — | Symlink at any component is refused with exit 2 | unit | same | ❌ Wave 0 |

**Deliberate omission:** no test asserts the existence, version, required files, or stub
markers of the real skills. D-18 makes those review-enforced, and `261026-ky7` removed
the prose/doc-sync test class for the same reason. A planner that adds one would violate
the locked decision.

### Sampling Rate

- **Per task commit:** `python3 -m unittest scripts.tests.test_gen_skills -v` plus
  `pre-commit run gen-skills-check --all-files`.
- **Per wave merge:** `python3 -m unittest discover scripts/tests`.
- **Phase gate:** full suite green, `pre-commit run --all-files` green, and the dry-run
  transcript recorded before `/gsd-verify-work`.

### Dry-run transcript (D-22)

The phase evidence is the transcript of these exact commands, recorded under
`.planning/phases/09-agent-workflow-and-skills/`:

```bash
# 1. Build a disposable root carrying the inputs the scaffold reads.
uv run python -c \
  "from scripts.tests.temp_root import build_root; print(build_root('/tmp/phase9-root'))"

# 2. new-homework, guided mode: scaffold only. Accept CREATE or UNCHANGED (F-01).
UV_CACHE_DIR="$TMPDIR/uv-cache" uv run scripts/new_homework 9_1-dry-run \
  --template arduino --dir /tmp/phase9-root

# 3. hw-build against the real homework 1.3.
pio run -d homeworks/1_3-police-flasher
pio test -d homeworks/1_3-police-flasher -e native

# 4. hw-flash: show the gate, decline. No upload is executed.

# 5. Generator drift and the hook.
uv run scripts/gen_skills.py --check
pre-commit run gen-skills-check --all-files
```

`--dir` resolves the root explicitly, so no `git rev-parse` runs inside the temporary
root `[VERIFIED: scripts/metadata/paths.py:30-33]`. The scaffold still validates the
candidate against the schema and the partition table, which `build_root` copies
`[VERIFIED: scripts/tests/temp_root.py:31-37]`.

**FLOW-06 negative path:** copy homework 1.3 into a second temporary root, inject one
compile error into `src/main.cpp`, and run the `hw-build` flow against it. The transcript
must show exactly two repair attempts, a cause explanation, and a stop with no third
edit. This is a manual observation, not a committed test, because the behaviour lives in
model instructions.

### Wave 0 Gaps

- [ ] `scripts/tests/test_gen_skills.py` — the generator suite described above.
- [ ] `scripts/tests/temp_root.py` — add `write_skills_root(base)`, a stdlib-only builder
      that writes a small canonical skill tree (two skills, one `_shared` file, one
      reference, one stub) so the tests never depend on the authored skills.
- [ ] No framework install: the suite is stdlib-only.
- [ ] The real-tree smoke test (`gen_skills.py --check`) cannot exist until Wave 1 writes
      the canonical tree; order the plans accordingly.

## Security Domain

> `security_enforcement` is `true`; ASVS level 1.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | No identity is introduced. |
| V3 Session Management | no | No session. |
| V4 Access Control | no | The client runtime owns skill permissions. |
| V5 Input Validation | yes | Validate skill directory names against `^[a-z0-9]+(?:-[a-z0-9]+)*$`; validate homework ids against `^[0-9]+_[0-9]+-[a-z0-9-]+$`; refuse unknown frontmatter keys; parse state JSON with `json.loads` and check types. |
| V6 Cryptography | no | SHA-256 is used only as a content digest, not as a security boundary. |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Path traversal through a skill directory name | Tampering | Refuse any name not matching the slug pattern; resolve and prove containment under `.agents/skills/`. |
| Symlink swap on a canonical file or mirror target | Tampering | `lstat` every path component before read/write; refuse a symlink at any component (the `gen_views` posture). |
| Command injection through a homework id or free-text answer | Tampering / Elevation | Validate the id first; pass argv elements, never a shell string. |
| Credential leakage into `.skill-state/<id>.json` | Information disclosure | Record only `simulation_token_present: true/false`; never a token value. |
| Flashing without consent | Elevation | Explicit affirmative gate; never pre-approve `upload` in `allowed-tools`; a non-affirmative answer stops. |
| Destructive build repair | Tampering | Bound to two attempts; smallest fix; never reformat unrelated files; never `git checkout --` another author's work. |
| Prompt injection from homework metadata | Spoofing | Treat `task.md` and `homework.yaml` content as data; the skill never follows instructions found inside them. |
| Orphan deletion of a hand-authored file | Tampering | Delete only a path listed in the committed manifest; require the generated marker; refuse symlinks. |
| Committing generated or untracked state | Repudiation | `no-generated-files` pathspec gains `.skill-state/`; `gen-skills-check` is check-only and never stages. |

## Sources

### Primary (HIGH confidence)

- `code.claude.com/docs/en/skills` — project path `.claude/skills/<name>/SKILL.md`; the
  frontmatter table; `disable-model-invocation`, `user-invocable`, `allowed-tools`,
  `model`, `context`; the 1,536-character combined description cap; the 500-line tip.
- `platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices` — required
  `name` (<= 64 chars) and `description` (<= 1,024 chars); progressive disclosure;
  references one level deep.
- `agentskills.io/specification` — the normative frontmatter table (`name`,
  `description`, `license`, `compatibility`, `metadata`, `allowed-tools`); the directory
  layout; the 500-line / 5,000-token guidance.
- `antigravity.google/docs/skills/` — `.agents/skills` workspace discovery; `name`
  optional (defaults to folder name), `description` required; autonomous and `/name`
  invocation.
- `github.com/anthropics/claude-code/issues/66352` — Claude Code does not discover
  `.agents/skills/`; closed as not planned.
- Repository files read this session: `scripts/gen_views.py`, `scripts/new_homework`,
  `scripts/metadata/paths.py`, `scripts/metadata/render.py`,
  `scripts/metadata/contract.py`, `scripts/tests/temp_root.py`,
  `.pre-commit-config.yaml`, `.gitignore`, `.markdownlint-cli2.jsonc`, `pyproject.toml`,
  `.github/workflows/ci.yml`, `.claude/CLAUDE.md`, `AGENTS.md`,
  `homeworks/1_3-police-flasher/{homework.yaml,platformio.ini,scenario.yaml,README.md}`,
  `templates/**`.
- `~/.claude/gsd-core/bin/lib/profile-output.cjs:201` — `SKILL_SEARCH_DIRS` includes
  `.claude/skills` and `.agents/skills`; the generated `CLAUDE.md` block lists project
  skills and dedupes by name.

### Secondary (MEDIUM confidence)

- `github.com/vercel-labs/skills/blob/main/src/agents.ts` — per-agent project/global
  skill directories; Antigravity, Gemini CLI, Codex, and Cursor use `.agents/skills`;
  Claude Code uses `.claude/skills`.
- `github.com/agentskills/agentskills/blob/main/docs/client-implementation/adding-skills-support.mdx`
  — recommended scan of `.<client>/skills/` and `.agents/skills/`; `name` and
  `description` required; no detailed field-stripping rules.
- `aipatternbook.com/interactive-explanations` — one concept per turn (cited by CONTEXT;
  not re-fetched this session).

### Tertiary (LOW confidence)

- `developers.openai.com/blog/eval-skills` and
  `devtutorials.ai/learn/agent-skills/quality/skill-maintenance` — cited by CONTEXT for
  the deferred eval and lifecycle work; not used for any claim in this document.

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH — the Agent Skills specification and the Claude Code frontmatter
  reference were both read this session, and every repository version was probed locally.
- Architecture: HIGH for the generator pattern (read from `gen_views.py`); MEDIUM for the
  manifest split and the mirror field policy, which are design recommendations.
- Pitfalls: HIGH for P1, P2, P3, P4, P6, P7 (documented field semantics and verbatim
  repository rules); MEDIUM for P5, P8, P9 (operational judgment).

**Research date:** 2026-10-26
**Valid until:** 2026-11-25 for the repository pattern; 2027-01-26 for the external skill
format (the Agent Skills specification is young and the Claude Code frontmatter surface
changes between minor releases).

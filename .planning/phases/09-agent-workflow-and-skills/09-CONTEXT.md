# Phase 9: Agent Workflow and Skills - Context

**Gathered:** 2026-10-26
**Status:** Ready for planning

<domain>
## Phase Boundary

Seven project-local agent skills at version 0.1, with `new-homework` and `hw-build`
fully usable in guided and one-shot modes. The phase delivers:

- `.claude/skills/` — the canonical tree: seven skill directories, each with
  `SKILL.md`, `CHANGELOG.md`, and `LESSONS.md`.
- `.agents/skills/` — a generated, committed mirror for non-Claude agents, with the
  Claude-only frontmatter fields stripped and drift checked by the generator.
- `scripts/gen_skills.py` — the mirror generator and its `--check` mode, wired into a
  pre-commit hook.
- `new-homework` — guided and one-shot modes over a prose adaptive question bank
  covering board, framework, language, mode, specification, simulation, tests, and
  deliverables; guided mode runs deliverable-level blocks with agent-written code,
  explanation, run, and comprehension questions.
- `hw-build` — runs the target build and native suite, fixes a failing build at most
  twice, then explains the cause and escalates.
- `hw-flash` — a minimally real skill: explicit confirmation, upload, and serial capture
  to an ignored path, with no log interpretation.
- Four documented stubs — `hw-report`, `schematic`, `simulate`, `course-index` — marked
  `metadata.status: stub`.
- `.claude/skills/_shared/guardrails.md` — the shared rules for flashing, commit/PR,
  specification-versus-best-practice conflicts, and ambiguity.
- An untracked `.skill-state/<id>.json` checkpoint state after intake, after code, and
  after the report.
- A phase dry run in a temporary root: `new-homework` scaffolds there, `hw-build` runs
  against homework 1.3, and `hw-flash` stops at its confirmation gate without hardware.

**Requirements covered:** FLOW-01, FLOW-02, FLOW-03, FLOW-04, FLOW-05, FLOW-06, FLOW-07.

**Explicitly not this phase:** the report and evidence checker (Phase 10), pilot
finalization and the `hw/<id>` tag (Phase 11), trigger evals or model benchmarks, full
`hw-flash` serial-log parsing, promotion of the four stubs, a full skill-content
validator, and any schema change.

</domain>

<decisions>
## Implementation Decisions

### Skill home and portability

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

### Guided and one-shot workflow

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

### Checkpoints and state

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

### Skill contract and stub policy

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

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and requirements
- `.planning/ROADMAP.md` §Phase 9 — goal, success criteria 1–5, and the FLOW-01..FLOW-07
  mapping.
- `.planning/REQUIREMENTS.md` §Agent Workflow and Skills — FLOW-01..FLOW-07, and the
  Traceability rows for Phase 9.
- `.planning/PROJECT.md` §Context and §Constraints — the user is new to VS Code, wants
  deep adaptive questioning, repository artifacts are English, and user communication
  follows the user's language.
- `.planning/STATE.md` §Blockers/Concerns — Phase 8 is resolved and Phase 9 is unblocked.

### Friction evidence that owns this phase
- `.planning/phases/04.2-tracer-homework-1-3/04.2-FRICTION-LOG.md` — F-01 (scaffold
  idempotence and `UV_CACHE_DIR`), F-04 (private `lib/pattern` manifest and `lib_deps`
  coupling), F-05 (native `-Werror` and fake reset), F-19 (dummy-token path check), and
  §Top automation candidates (the Phase 9 row).

### Repository contracts and existing artifacts
- `AGENTS.md` — the canonical rulebook; the phase replaces its "planned" project-skills
  note with the live path and commands.
- `.claude/CLAUDE.md` — the generated adapter; its Project Skills block is
  generator-owned and must not be hand-edited inside the markers.
- `scripts/new_homework` — the only scaffold path; `--dry-run`, `--json`, `--dir`, and
  exit codes 0/1/2.
- `scripts/gen_views.py` and `generated.manifest` — the generator plus drift-check
  pattern that `gen_skills.py` follows.
- `.pre-commit-config.yaml` — the hook stages and pinned revisions where the gen-skills
  hook lands.
- `.gitignore` — must gain the `.skill-state/` ignore rule; the inner homework ignore
  rules are the precedent for untracked per-homework state.
- `scripts/tests/` — the stdlib-only suite and golden fixtures; its tests shell out to
  `uv run` and never import `yaml` or `jsonschema`.
- `templates/homework-arduino/template.yaml` and `templates/task/task.md` — the scaffold
  inputs and the place where a new template file would have to be declared.
- `homeworks/1_3-police-flasher/homework.yaml`, `platformio.ini`, `README.md`,
  `scenario.yaml`, and `assets/diagram.json` — the real homework used by the dry run and
  by `hw-build` and `hw-flash`.
- `docs/standards/vscode.md` — the onboarding guide the skills should point at when
  explaining the editor.
- `docs/decisions/README.md` — the table-first decision index; a row for the skills
  layout is optional.
- `.planning/notes/ceremony-vs-engineering-principle.md` — the lean rule behind the
  drift-only machine check.
- `.planning/phases/05-generated-views-and-documentation-site/05-CONTEXT.md` — D-21,
  check-only hooks never rewrite or stage.
- `.planning/phases/06-developer-experience-and-quality-layering/06-CONTEXT.md` — hook
  layering, stdlib tests, and plain `{{placeholder}}` template rendering.
- `.planning/phases/07-simulation-spike/07-CONTEXT.md` — the five-label evidence
  vocabulary and the `simulation.status` rule.
- `.planning/phases/08-fast-ci/08-CONTEXT.md` — the `gate` contract and the CI surfaces a
  new hook must fit.

### External references
- `https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices` —
  frontmatter fields, progressive disclosure, and the 500-line guidance.
- `https://code.claude.com/docs/en/skills` — the Claude Code skill locations and
  invocation fields.
- `https://github.com/agentskills/agentskills/blob/main/docs/client-implementation/adding-skills-support.mdx`
  — the `.agents/skills/` interoperability convention and the per-client scan paths.
- `https://github.com/anthropics/claude-code/issues/66352` — Claude Code does not read
  `.agents/skills/` directly, which is why the mirror exists.
- `https://aipatternbook.com/interactive-explanations` — the one-concept-per-turn
  explanation pattern.
- `https://openai.github.io/openai-agents-python/human_in_the_loop/` — durable
  checkpoint state and idempotent resume.
- `https://developers.openai.com/blog/eval-skills` — the deferred trigger-eval approach.
- `https://www.devtutorials.ai/learn/agent-skills/quality/skill-maintenance` — the skill
  lifecycle and maintenance layers.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `scripts/new_homework` — the idempotent scaffold with `--dry-run`, `--json`, and
  `--dir`; the `new-homework` skill wraps it rather than reimplementing rendering.
- `scripts/metadata/contract.py` and `scripts/metadata/render.py` — the validation and
  template-rendering path the skill relies on.
- `scripts/gen_views.py` and `generated.manifest` — the generator shape, `--check`
  semantics, and manifest bookkeeping that `gen_skills.py` copies.
- `scripts/tests/` — the stdlib-only suite and golden fixtures where the generator's
  tests belong.
- `.pre-commit-config.yaml` — the pinned hook surface and stage semantics.
- `.gitignore` — the place for the `.skill-state/` rule.
- `homeworks/1_3-police-flasher/` — the real fixture for `hw-build` and the dry run.

### Established Patterns
- Deterministic scripts print `PATH: STATUS — reason`, support `--json`, and exit 0/1/2.
- Hooks are check-only and never rewrite or stage (05/D-21).
- Tests never import `yaml` or `jsonschema`; they shell out to `uv run` (04/D-14).
- Generated files are committed and drift-checked; a hand edit is never the fix.
- Template rendering is plain `{{name}}` substitution with unknown placeholders as
  errors; there is no Jinja.
- `AGENTS.md` rules carry a severity and an enforcement point.
- Prose and doc-sync tests were pruned in `261026-ky7`; a new prose guard would repeat the
  mistake.

### Integration Points
- `.claude/skills/` — the new canonical tree, including `_shared/guardrails.md`.
- `.agents/skills/` — the generated mirror and its manifest entry.
- `.pre-commit-config.yaml` — the new gen-skills `--check` hook.
- `.gitignore` — the `.skill-state/` ignore rule.
- `scripts/tests/` — tests for `gen_skills.py` with fixtures.
- `AGENTS.md` — replace the "planned" project-skills note with the live layout and
  commands.
- `.claude/CLAUDE.md` — the generated adapter's Project Skills block is regenerated, not
  hand-edited.
- `homeworks/1_3-police-flasher/` — the dry-run and `hw-build` target.
- `.planning/STATE.md` — the session record for this phase.

</code_context>

<specifics>
## Specific Ideas

- The user is new to VS Code; explanations may point at `docs/standards/vscode.md`.
- `scripts/new_homework` needs `UV_CACHE_DIR` pointed at a writable directory in a
  sandboxed shell (F-01); the skill should set or name it.
- The scaffold is idempotent: a second run returns `UNCHANGED` for every path, so the
  skill must accept both `CREATE` and `UNCHANGED`.
- A homework-local `lib/pattern` manifest must omit `frameworks` and `platforms` and
  must not be added to `lib_deps` (F-04).
- Native tests use `-Wall -Wextra -Werror`; both host fakes must be reset in `setUp` and
  the idle button seeded HIGH (F-05).
- Wokwi simulation is token-gated and metered (about 50 minutes per rolling 30 days);
  flashing is hardware, simulation is quota, and neither is a build.
- The user wants deep, adaptive questioning rather than a one-shot result.
- Repository artifacts are English; the conversation is Ukrainian.
- `course-index` should read the generated index rather than re-scanning by hand.
- The `hw-flash` confirmation must be explicit and must never default to yes.

</specifics>

<deferred>
## Deferred Ideas

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

### Reviewed Todos (not folded)

- *Generate a root compile database so `lib/` has working IntelliSense* — resolved by
  Phase 06.1.
- *Revisit Phase 8 scope before planning* — resolved by Phase 8.
- *Trim governance ceremony (Phase 4.1)* — completed in Phase 4.1.
- *Standardize pull request titles across homeworks* — folded into Phase 8.
- *Expand homework README and add a proper SVG schematic* — Phase 11.
- *Remove the generated documentation site* — completed 2026-10-26.

</deferred>

---

*Phase: 9-Agent Workflow and Skills*
*Context gathered: 2026-10-26*

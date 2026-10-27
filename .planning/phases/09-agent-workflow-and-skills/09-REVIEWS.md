---
phase: 9
reviewers: [codex-glm, codex-beam, antigravity]
reviewed_at: 2026-10-26T21:03:53Z
plans_reviewed:
  - .planning/phases/09-agent-workflow-and-skills/09-01-PLAN.md
  - .planning/phases/09-agent-workflow-and-skills/09-02-PLAN.md
  - .planning/phases/09-agent-workflow-and-skills/09-03-PLAN.md
  - .planning/phases/09-agent-workflow-and-skills/09-04-PLAN.md
  - .planning/phases/09-agent-workflow-and-skills/09-05-PLAN.md
  - .planning/phases/09-agent-workflow-and-skills/09-06-PLAN.md
  - .planning/phases/09-agent-workflow-and-skills/09-07-PLAN.md
  - .planning/phases/09-agent-workflow-and-skills/09-08-PLAN.md
models:
  codex-glm: "glm-5.3-flash:cloud (reasoning=high)"
  codex-beam: "beam:cloud (reasoning=high)"
  antigravity: "gemini-3.8-flash-high"
model_sources:
  codex-glm: "pinned"
  codex-beam: "pinned"
  antigravity: "pinned"
---

# Cross-AI Plan Review — Phase 9

> Note: codex-glm and codex-beam share the codex adapter; their consensus is cross-model, not cross-tool.

<!-- gsd:plan-revision-conflicts:begin -->
## Plan-Revision Conflicts
<!-- gsd:plan-revision-conflicts:end -->

## Codex Review (codex-glm)

# Cross-AI Plan Review — Phase 9

## 09-01

### Summary
This is the highest-risk plan in the phase, and it is mostly sound: it copies the proven `gen_views.py` ownership/drift pattern rather than inventing a second ledger, locks the invocation-widening mirror transform, and makes real-tree mirror drift the only machine gate consistent with D-18. The tracer-first ordering is appropriate because later skills should not be authored before the generator and check exist. Its main weaknesses are incomplete integration coverage of a generator-only diff, a lint-policy gap for authored `.claude/skills/` files, and a few edge cases the fixture matrix should pin explicitly.

### Strengths
- The plan correctly recognizes that `scripts/gen_views.py` has a single-segment write allowlist, so extending `generated.manifest` would violate D-04. Evidence: `scripts/gen_views.py:103-108` and `scripts/gen_views.py:405-417` restrict targets to three root files.
- The explicit-only banner correctly avoids the subtle invocation-widening defect caused by merely stripping `disable-model-invocation`; `09-01-PLAN.md` states both the transformed output and the banner invariant.
- The manifest, exit code, classification, and atomic-write contracts match the existing generator pattern: `scripts/gen_views.py:88-96`, `scripts/gen_views.py:295-330`, and `scripts/gen_views.py:484-501`.
- The `.gitignore` concern is real and verified: `.gitignore:262-265` has `*.manifest` followed only by `!generated.manifest`, so a second ledger needs its own negation.
- The plan correctly extends the markdownlint exclude for generated `.agents/` files; `.pre-commit-config.yaml:98` currently only excludes `^(\.planning/|\.claude/)`.
- Adding `.skill-state/` to `no-generated-files` addresses the `git add -f` hole described in `.pre-commit-config.yaml:113-124`.

### Concerns
- **HIGH — A generator-only PR can still widen every build.** Plan task 3 adds `.claude/`, `.agents/`, `generated.skills.manifest`, and `.skill-state/` to `NO_BUILD_IMPACT`, but not `scripts/gen_skills.py` itself. Since `scripts/affected.py:108-116` documents the fail-safe and currently widens unknown scripts, a later PR changing only the skills generator would rebuild all projects. This conflicts with the plan’s “skills-only pull request selects no build” key link.
- **MEDIUM — The hook’s dependency surface is narrower than the generator’s actual imports.** The proposed `files` regex names the generator and ledger but omits `scripts/metadata/`, even though `scripts/gen_skills.py` is planned to import `resolve_root` and `read_regular_text`. The existing `gen-views-check` uses this broader input pattern in `.pre-commit-config.yaml:176-200`. A helper change could therefore leave the hook untriggered in a partial local run.
- **MEDIUM — Authored `.claude/skills/` Markdown is currently not linted and the plan keeps excluding all of `.claude/`.** The canonical skills are authored content, but `.pre-commit-config.yaml:98` excludes the entire `.claude/` tree. Extending the exclude to `.agents/` solves the generated mirror, not the authored canonical skills. This leaves all seven skill bodies outside the authored Markdown quality gate in `AGENTS.md:182-184`.
- **MEDIUM — `_shared/SKILL.md` is not explicitly specified as invalid.** Plan task 1 says `_shared` contributes files only, but does not say the generator must exit 2 if a `SKILL.md` appears under `_shared`. Without that, a mirror artifact under `.agents/skills/_shared/SKILL.md` could be discovered by clients as though it were a skill.
- **MEDIUM — Deep reference files are silently outside the mirror contract.** The discovery rule names root files and `references/` one level deep, but does not say what happens to `references/sub/file.md`. The Agent Skills guidance cited by the research is one level deep; a deeper file should exit 2 rather than be silently omitted.
- **LOW — The test matrix omits a `SKILL.md` `name`/directory mismatch case.** Task 1’s action says the name must equal the directory, but neither the stated test list nor the acceptance criteria names that failure probe.
- **LOW — Manifest entry `owner` and `mode` values are stated as `skills` and `whole`, but validation details do not explicitly require those literals.** The existing manifest validator requires type and shape, not semantic ownership, in `scripts/gen_views.py:319-388`; the new generator should close that gap for its narrower ledger.

### Suggestions
- Add `scripts/gen_skills.py` to either `NO_BUILD_IMPACT` or a documented narrow no-build classification, and add it to `NoBuildImpactTests`.
- Add `scripts/metadata/` to the proposed hook `files` regex, mirroring `gen-views-check`.
- Rework markdownlint exclusions so authored `.claude/skills/**` is linted while `.claude/CLAUDE.md` and `.agents/**` are excluded, for example with a precise negative-selection regex or a separate local hook policy.
- Explicitly reject `_shared/SKILL.md`, empty immediate directories, invalid immediate directories, and files deeper than `references/<file>`.
- Add unit probes for: `name` mismatch, manifest entry missing `source`, wrong `source`, wrong `owner`, and a canonical file that already contains the generated marker.
- Make the fixture builder state its refusal to copy or read the real `.claude/skills/` tree a tested invariant, not only a docstring claim.

### Risk Assessment
**MEDIUM.** The design is correct and grounded in an already proven generator pattern. The remaining risks are mostly integration and edge-case drift: a generator-only change rebuilding everything, generated versus authored lint ownership, and untested malformed tree shapes. These are cheap to close before implementation.

---

## 09-02

### Summary
This plan completes the four-stub inventory and establishes the policy text every implemented skill will reference. Its guardrail outline is concrete, and `course-index` correctly treats the existing generated README region as the only index projection. It is safe as content work, but several review gates are written against the wrong wave state, and some security-relevant wording is underspecified.

### Strengths
- The shared guardrails cover the exact non-negotiables from FLOW-04 and FLOW-05, including flash consent, commit/PR confirmation, spec conflicts, and ambiguity.
- `course-index` correctly points at the marker-bounded README projection rather than rescanning metadata. The active region exists at `README.md:15-22`, and the generator owns that region per `scripts/gen_views.py:88-96`.
- Stub metadata and body banners match D-19 and D-20, and the `simulate` fallback command is validated by the installed CLI: `wokwi-cli lint --offline <diagram>` is supported by the local `wokwi-cli lint --help`.
- The generator will correctly avoid treating `_shared` as a skill if `gen_skills.py` implements the 09-01 contract; `.agents/skills/_shared/SKILL.md` is explicitly forbidden by this plan.
- The test confirms that `course-index` carries no invocation banner while the explicit-only stubs do.

### Concerns
- **HIGH — The plan’s seventh acceptance criterion is factually impossible at Wave 2.** It states that after `course-index` the canonical tree holds seven skill directories plus `_shared/`. At this point only four skills exist: `simulate`, `hw-report`, `schematic`, and `course-index`; `new-homework`, `hw-build`, and `hw-flash` are later waves. This should be corrected to “four skills” or moved to a later verification.
- **MEDIUM — `course-index`’s description may omit that it is unimplemented.** The planned description says it answers which homeworks exist, but unlike the other stubs, the task does not explicitly require the description itself to name the placeholder/stub capability. Clients that rely on `description` for auto-invocation can misclassify the stub as functional.
- **MEDIUM — The guardrails’ “present both, recommend one, ask before proceeding” needs a concrete ambiguity protocol for user silence.** FLOW-05 and D-08 require depth and assumptions to be chosen by the user. The guardrail should explicitly define that silence is not acceptance and that a proposed assumption only changes behavior after a recorded affirmative.
- **LOW — The guardrails file’s enforcement points are prose, not machine-enforced, by D-18.** That is intentional, but the plan should name the phase dry-run transcript as the only practical check of the flashing and commit rules.
- **LOW — `hw-report`’s manual fallback depends on Phase 10 output that does not exist yet.** The wording correctly defers to Phase 10, but it should also state that the current template skeleton is not a validated report contract, to avoid making TODOs sound merge-ready.

### Suggestions
- Replace the “seven skill directories” acceptance criterion with a four-stub inventory assertion and defer the seven-skill count to the wave that adds the last implemented skill.
- Require `course-index`’s description to say it is a placeholder/未提升 stub, not merely to omit `disable-model-invocation`.
- Add an explicit guardrail sentence: silence, delay, or an indirect answer is consent only when explicitly stated as acceptance; otherwise the action stalls.
- Require every stub description to label the skill as a stub, while the body banner remains the authoritative status marker.
- Add a final review checklist covering all four stub banners, their manual commands, and the absence of `_shared/SKILL.md`.

### Risk Assessment
**MEDIUM.** The policy and stub design are correct, but the stale seven-skill criterion could produce an impossible verification gate, and the auto-invocable stub’s description must be made unmistakably provisional.

---

## 09-03

### Summary
This is the central product plan and is conceptually strong: it encodes D-06 through D-17, wraps the existing scaffold rather than duplicating it, captures state before checkpoint menus, and preserves Ukrainian conversation with English artifacts. However, it has several concrete contract contradictions with repository reality that must be fixed before execution: the ESP-IDF language mapping conflicts with the actual template, the scaffold hardcodes the only supported board while the question bank implies arbitrary boards, the intake lacks a defined homework-ID question despite the state path depending on it, and task.md provenance is never addressed.

### Strengths
- The eight topics are in a deterministic branch order, with `mode` first and simulation-token presence recorded only as a boolean. The state contract includes every D-13 field.
- The scaffold block correctly reuses the existing idempotent CLI and accepts both `CREATE` and `UNCHANGED`, matching F-01 and the CLI contract in `scripts/new_homework:14-34`.
- The block loop, pause menus, deepening semantics, and non-code run-skip rules directly implement FLOW-02/FLOW-03/FLOW-04/FLOW-05 and do not infer user confusion.
- The plan correctly runs `gen_views.py --all` after scaffolding, eliminating the Phase 4.2 friction of hand-editing generated views.
- State-file write discipline is atomic, local, and non-secret; the plan explicitly forbids storing a token value.
- The command-injection control is appropriate and matches the existing ID regex in `scripts/metadata/paths.py:19-32`.

### Concerns
- **HIGH — The ESP-IDF language branch contradicts the real scaffold.** The plan says `espidf` maps to `c`, but `templates/homework-espidf/homework.yaml:8` sets `language: cpp`. The established repository pattern also uses one `.cpp` composition root for both frameworks. As written, the skill would ask to confirm `c`, record `c`, and then scaffold metadata saying `cpp`, creating immediate metadata/workflow drift. The bank and state schema must either change the mapping to `cpp` or explicitly extend the scaffold/template, with tests.
- **HIGH — The board branch is unsupported by the scaffold.** `scripts/new_homework:89-90` and `scripts/new_homework:239` hardcode `BOARD = "esp32-s3-devkitc-1"`, and the shared/config templates target that board. Plan task 1 says another board can be asked from `boards/`, but there is no contract for updating `homework.yaml`, `boards/<id>.yaml`, `platformio.ini`, or stopping. “Adaptive board” is therefore currently aspirational rather than usable.
- **HIGH — Homework-ID acquisition is missing from the intake sequence.** The bank has exactly eight H2 topics and says state answers are recorded as soon as they are given, but the state path is `.skill-state/<id>.json`; `mode` must be first. If the ID is not supplied by invocation, neither the bank nor the skill body defines when to ask it without violating “mode first.” The contract needs an explicit invocation-only, pre-bank, or stateless-memory rule.
- **HIGH — Task.md provenance is never part of the intake or completion checkpoint.** The scaffold leaves `source_url/retrieved/attribution/license` as `TODO` in `templates/task/task.md:1-5`, and the schema/status contract permits TODOs only while `homework.yaml` is `planned`. The plan never asks for provenance or keeps the homework in `planned` until it is supplied, so a completed run can leave metadata that later fails `check_metadata.py`.
- **HIGH — “Quote the acceptance criteria verbatim” risks committing internal course material.** `AGENTS.md:236-242` forbids original assignment text and requires an English paraphrase with attribution. A verbatim-quote branch may copy protected assignment text into the state file or report. The question bank must distinguish user-authorized paraphrase from original course text and record provenance.
- **MEDIUM — Intake deliverables include BOM and calculations, but D-06’s fixed block sequence has no BOM or calculations block.** The report block may include them, but the plan does not say where those artifacts are authored or whether they are treated as report subsections. This can leave the user believing missing deliverables are handled.
- **MEDIUM — The “code checkpoint” versus per-block pause is ambiguous.** The block loop says every block pause writes a checkpoint record, while the checkpoint vocabulary only names `intake|code|report`. Either every block status is part of one named checkpoint, or `checkpoints[]` can repeat names; the schema should resolve this.
- **MEDIUM — `UV_CACHE_DIR` is set only on the scaffold command, while other `uv run` commands also use dependencies.** The friction log identifies the whole `uv` cache problem, not just `new_homework`; Phase 4.2 also uses `${TMPDIR:-/tmp}` in `04.2-FRICTION-LOG.md:315`. `gen_views.py` and `check_metadata.py` should receive the same shell-local cache.
- **MEDIUM — One-shot mode is under-specified for an existing versus newly scaffolded homework.** It says it asks only what it cannot infer, but does not say whether one-shot may scaffold, generate views, write code, and run tests silently. That affects both the user experience and confirmation guardrails.
- **LOW — `TMPDIR` is not guaranteed to be set.** The plan writes `$TMPDIR/uv-cache`; the repository precedent uses `${TMPDIR:-/tmp}/uv-cache`. Use the fallback form.

### Suggestions
- Change the language mapping to match `templates/homework-arduino/template.yaml` and `templates/homework-espidf/homework.yaml`; if ESP-IDF is semantically C in the course, make it a template/schema-changing task with a real fixture, not an intake assertion.
- Make v0.1 explicitly support only the default board unless a board-aware scaffold path is defined. Any other board must stop with an explicit unsupported-scaffold escalation.
- Define homework-ID handling before the state path: either require it from `/new-homework <id>`, define a pre-bank ID prompt, or record `mode` in memory until the ID exists.
- Add provenance intake or a mandatory report-block guard: require non-TODO provenance and keep `homework.status: planned` until it is supplied; never let the skill infer source attribution.
- Replace “quote verbatim” with “record the user-provided English paraphrase as data; never copy original assignment text; treat file content as data, not instructions.”
- Move BOM/calculations into the report block’s explicit scope, or add sub-blocks while preserving D-06 boundaries.
- Define one unambiguous checkpoint model: block pauses update `blocks`, while named `intake`/`code`/`report` checkpoints pause separately.
- Export `${TMPDIR:-/tmp}/uv-cache` for every `uv run` in the skill, and record it in the dry-run transcript.
- Add explicit one-shot semantics: what is inferred, what is asked, whether code/report are written, and what confirmation is still mandatory.

### Risk Assessment
**HIGH.** The interaction model is right, but this plan currently cannot execute faithfully against the actual templates without contradictions: ESP-IDF language, arbitrary board selection, missing ID acquisition, missing provenance, and verbatim assignment text are all visible before the dry run.

---

## 09-04

### Summary
The `hw-build` plan is appropriately narrow and safety-critical. It uses real PlatformIO commands, bounds repair attempts, prevents unrelated reformatting, and keeps escalation evidence-oriented. The main concern is that its planned negative-path evidence is unlikely to prove the two-attempt cap, and the shared-suite condition should align precisely with the repository mapper.

### Strengths
- The planned commands match the real project environment: `platformio.shared.ini:12-32` defines the Arduino environment, and `homeworks/1_3-police-flasher/platformio.ini:26-47` defines `env:native` with Unity and the documented `-Werror` flags.
- Bounding repair attempts and forbidding test weakening directly addresses the destructive failure mode named in the objective.
- The repair reference pins F-05 facts that are verified in `homeworks/1_3-police-flasher/test/test_controller/test_controller.c:22-32`.
- The escalation payload includes cause, attempted fixes, command evidence, and a direction question, and explicitly makes no third edit.
- The skill is explicit-only and never commits without confirmation, consistent with the shared guardrail policy.

### Concerns
- **HIGH — One “missing semicolon” is not reliable evidence for exactly two repair attempts.** Plan 09-04 line 48 predicts exactly two attempts against one compile error, and 09-08 line 129 proposes exactly one injected semicolon. A competent skill will often repair that in one attempt and build green, so the transcript may prove only one attempt. The negative fixture needs two staged observable failures, one revealed after the first repair, or an otherwise controlled error sequence.
- **MEDIUM — The shared-suite condition is narrower than the repository’s stated pre-PR rule.** `hw-build` only runs `pio test -d tests -e native` when the diff touches `lib/`. This is reasonable for a per-homework skill, but it should explicitly distinguish “homework build helper” from “full pre-PR gate”; otherwise an existing homework diff plus an untracked or non-lib working-tree change can skip the shared suite that `AGENTS.md:21-26` describes as the standard pre-PR step.
- **MEDIUM — The repair cap is described as “per run” but the relationship between build-leg and native-leg caps is not fully resolved.** If the build leg succeeds after one repair and the native leg then fails, is the native leg another two attempts or part of the same total? The reference should state whether the cap resets only at a new user-directed run.
- **MEDIUM — A repair may need to touch homework-local `lib/pattern`, not just project source.** The plan’s examples are oriented to `src/main.cpp`; it should state that the smallest fix may update a homework-local library and that such a change is a normal repair, not unrelated code.
- **LOW — The plan cites `state-file.md` but `hw-build` does not define whether build failures are recorded there.** That is probably correct in v0.1, but it should explicitly say no durable checkpoint is written by `hw-build`.
- **LOW — The phrase “never edits a test to make it pass when the implementation is wrong” needs an operational rule.** The skill should say it may fix a broken test fixture only when the fixture is demonstrably wrong, with explicit user confirmation; it must never weaken assertions.

### Suggestions
- Build the negative path with two deterministic compiler failures: the first actionable error is fixed only to reveal the second, and the second reaches the escalation after attempt 2. Do not rely on one semicolon.
- Add explicit cap semantics: build leg and native leg each get two attempts, while the whole skill invocation stops for user direction after any leg exhausts two.
- State that full PR verification remains the repository gate and that `hw-build` is not a substitute for the complete pre-PR chain.
- Include a legitimate `homeworks/<id>/lib/**` repair path in the dry-run fixture.
- Define test-fixture repair separately from test weakening, and make it confirmation-gated.
- Ensure compiler warnings are preserved in the escalation payload as warnings, but never counted as errors.

### Risk Assessment
**MEDIUM.** The build contract itself is good and grounded in real commands. The dry-run evidence and cap-reset ambiguity are the main risk; without a deliberately staged two-failure sequence, the central FLOW-06 claim will not be observed.

---

## 09-05

### Summary
This plan gives `hw-flash` an appropriate hardware safety boundary: an explicit, non-persistent consent gate, real upload command semantics, bounded capture, and no log interpretation. The main gap is consistent secure handling of the ignored log path; several failure paths also need one explicit statement so that a failed serial capture is not confused with a failed flash.

### Strengths
- The plan directly implements FLOW-07 and D-20: no upload without a literal affirmative, no remembered consent, no pre-approved `upload`, and no simulation-as-flash confusion.
- PlatformIO supports the proposed commands. Local help confirms `pio device monitor -d <project-dir> -b <baud>` and `pio run -t <target>`.
- Bounded Python `subprocess` timeout is the right macOS-compatible approach; the plan explains why `timeout(1)` is not assumed.
- The capture destination is under the ignored state directory and is explicitly not interpreted, matching D-20 and the no-bench-evidence guardrail.
- The homework-ID validation and argv rule prevent shell interpolation from user-controlled text.

### Concerns
- **MEDIUM — Log-path safety is underspecified.** `hw-flash` writes to `.skill-state/logs/<id>.log`, but unlike the state-file contract in 09-03, it does not require component-wise symlink refusal, atomic/durable append handling, or directory creation without following an attacker-swapped path. Device output is untrusted; the plan should mirror the state-file write discipline.
- **MEDIUM — Capture failure handling is missing.** If upload exits 0 but `pio device monitor` fails or times out before 20 seconds, the skill should state that the upload result remains the real exit code and that a failed capture produces “capture unavailable,” not a successful measurement or silent success.
- **MEDIUM — The exact baud and environment are assumed.** `-b 115200` is plausible, but `platformio.shared.ini` has no monitor speed. For a non-default homework or a future port change, the skill should derive or ask/confirm the expected monitor speed and environment rather than hardcode 115200 as universal.
- **LOW — “On a non-zero upload exit, no repair beyond the `hw-build` loop” could be read as permitting `hw-build` as an implied sub-skill.** It should say the user may run `/hw-build` separately; `hw-flash` stops immediately.
- **LOW — Capture should prefer `--raw` when the goal is uninterpreted bytes.** Without `--raw`, monitor transformations/encoding can alter device output even though the skill does not interpret it.
- **LOW — “A first refusal returns to the user” is slightly ambiguous.** The guardrail intent is presumably stop; the body should say a refusal stops this gated action, and a new invocation is required.

### Suggestions
- Add the same path guard as the state file: `lstat` every component, refuse a symlink, create the log parent only after the component check, and use an atomic file creation policy.
- Add explicit outcomes: upload success + capture success, upload success + capture failure, upload failure, and consent refusal.
- Derive the monitor environment from the selected/default upload environment; make baud explicit and configurable only through a bounded, validated value, not free text.
- Invoke the monitor with `--raw` when raw bytes are intended.
- State that refusal stops the action and that no previous yes is retained.
- Make it explicit that no repair occurs inside `hw-flash` on an upload failure.

### Risk Assessment
**MEDIUM.** The human gate and upload command are correctly specified. The residual work is mostly operational failure-path clarity and the log path’s symlink/atomic-write guarantees.

---

## 09-06

### Summary
The documentation plan correctly removes the stale “planned Phase 9” wording and updates the hook count. Its generated-versus-build-output rule is valuable. It is incomplete, however, because it does not update `AGENTS.md`’s repository-layout inventory for the new files and does not solve the fact that authored skills under `.claude/skills/` are currently hidden from markdownlint.

### Strengths
- The current stale text is verified: `AGENTS.md:68-72`, `AGENTS.md:271-272`.
- The current hook count is indeed 13 and the new hook makes 14: `docs/standards/vscode.md:152-183`.
- The proposed rule distinguishes never-committed build output from committed generated projections, which is needed once `.agents/skills/**` and `generated.skills.manifest` become tracked.
- The verification checks both live tokens and stale planned phrases, so drift cannot pass silently.
- Leaving the Phase 7 simulation paragraph and esp-clangd material untouched prevents unrelated documentation churn.

### Concerns
- **MEDIUM — `AGENTS.md` “Repository layout” remains stale.** `AGENTS.md:28-48` lists the repository’s present paths, and `AGENTS.md:50-55` says generated paths are only the three views and `generated.manifest`. Plan 09-06 replaces the planned note and routing row but does not add `.claude/skills/`, `.agents/skills/`, `scripts/gen_skills.py`, or `generated.skills.manifest` to the layout inventory. The plan should update the “Present today” inventory and the generated-paths paragraph as well as the rule.
- **MEDIUM — It assumes the markdownlint problem is solved in 09-01, but authored skill prose remains excluded because `.claude/` is globally excluded by `.pre-commit-config.yaml:98`.** 09-06 should either cross-reference the corrected lint surface or explicitly state that skill prose is exempt. As currently written, “authored Markdown is linted” becomes inaccurate for the seven skill bodies.
- **MEDIUM — The hook-count guidance can become stale if hook structure changes; the 09-07 full gate will not compare the guide count to the YAML.** This is acceptable, but the plan should either accept review enforcement explicitly or add a count-derived assertion to the already existing tooling test.
- **LOW — The plan says remove `(planned, Phase 9)` text everywhere, but its assertion searches only two phrases.** It should verify the skills note and routing row directly rather than a general absence of one parenthetical.
- **LOW — The generated-file class rule should mention check-only hook behavior and the exact repair command for the new projection.** Most of this is in the routing row, but the rule itself is more useful if it names the repair once.

### Suggestions
- Update `AGENTS.md`’s layout bullets to include the skill trees, generator, and new ledger, and update the “generated paths” paragraph to name both manifests/projections.
- If 09-01 fixes markdownlint for authored skills, verify here that `.claude/skills/**/SKILL.md`, references, and companion files are included while `.claude/CLAUDE.md` and `.agents/**` remain excluded.
- Make the 14-hook count a reviewed invariant or derive it from the pre-commit config in `test_tooling_config.py`, so future hooks update the guide in lockstep.
- Add explicit assertions for the exact stale sentences as well as generic phrases.
- Add a “repair command” phrase directly to the generated-file rule for consistency.

### Risk Assessment
**MEDIUM.** The edits are small and the intended direction is right, but the canonical rulebook will still underdescribe the phase’s added files unless the layout list and generated-paths paragraph are included in the change.

---

## 09-07

### Summary
This plan handles the generator-owned adapter correctly: it emits GSD output to a temporary path, splices only the skills block, verifies no other byte changed, and records the layout as a one-row decision. The main concerns are D-01 cost wording and external GSD fragility, neither of which undermines the splice design.

### Strengths
- The current adapter confirms the planned target: `.claude/CLAUDE.md:12-17` is GSD-owned and currently says “No project skills found.”
- The installed GSD generator’s `cmdGenerateClaudeMd` does generate all managed sections unless pointed at `--output`, confirming the plan’s warning; evidence is `~/.claude/gsd-core/bin/lib/profile-output.cjs:1004-1025`.
- The generator’s skills discovery includes both `.claude/skills` and `.agents/skills` but deduplicates by skill name, so the committed mirror will not duplicate entries in the adapter table; evidence is `~/.claude/gsd-core/bin/lib/profile-output.cjs:429-474`.
- The temporary-output-plus-splice approach prevents the four fallback Project/Stack/Conventions/Architecture sections from entering `.claude/CLAUDE.md`.
- The decision-row-only record is consistent with `docs/decisions/README.md:1-6`, which says ADR files are only for significant argumentation.

### Concerns
- **MEDIUM — The decision row says “moderate” change cost while D-01 says the layout is costly to reverse.** That inconsistency can make a future reader underestimate migration cost. Use the locked D-01 wording.
- **MEDIUM — The plan depends on external GSD tooling not governed by the repository.** It handles `gsd_run` fallback and temporary output, but the execution should record the tool version/invocation in the plan summary so a later tool upgrade can explain a changed table format.
- **MEDIUM — The seven-name check verifies presence but not uniqueness or that paths point to `.claude/skills/<name>/SKILL.md`.** A malformed generator output containing the seven words but wrong path shape could pass.
- **LOW — The decision-table assertion is brittle to exact Markdown spacing/case.** This may be acceptable repository style, but the final full gate should include markdownlint for the decisions file.
- **LOW — The plan does not specify behavior if the skills-generated output contains a non-skill directory mistakenly discovered by GSD.** The generator skips `_shared` because it has no `SKILL.md`, but if `gen_skills.py` later produced `_shared/SKILL.md`, the adapter could include an unintended entry. The 09-01 refusal closes this.

### Suggestions
- Align the decision row’s change cost with D-01’s “costly” classification.
- Record the exact GSD command and tool revision in the task evidence or summary.
- Extend the adapter assertion to parse the skills table and require exactly seven rows, one per name, each path matching `.claude/skills/<name>/SKILL.md`.
- Before the splice, assert the generated temporary file contains exactly one skills start/end marker and seven discovered skill entries.
- Keep the decision row as the only record, as planned, unless the full mirror policy needs alternatives/consequences in Phase 10.

### Risk Assessment
**LOW to MEDIUM.** The core approach is careful and verifiable. The external dependency and exact table-shape assertions are the residual risk, but manageable with a stricter generated-output check.

---

## 09-08

### Summary
The dry-run plan is the right validation approach for prose/model-behavior skills and uses the real scaffold, build, and flash gate. It has good privacy and tracked-tree controls. Its most important defect is the negative repair leg: one injected semicolon cannot reliably prove two attempts. The guided legs should also record whether scaffold, native-tests, and wiring blocks are adequately exercised or intentionally sampled.

### Strengths
- The temporary-root strategy matches D-22 and the existing fixture pattern; `scripts/tests/temp_root.py:57-78` already roots the scaffold safely with a `lib/` symlink and copied shared inputs.
- The plan correctly seeds a marker-bounded README so `gen_views.py --all --dir <root>` can work, and it handles the “no authored views” case in the skill contract.
- The green and failing `hw-build` legs use the real project 1.3 and real PlatformIO commands named in `homeworks/1_3-police-flasher/platformio.ini:12-47`.
- The flash leg records a non-affirmative answer and asserts no upload or capture, which directly proves the D-22 hardware-free boundary.
- Final privacy controls are concrete: boolean token presence, no `/Users/` absolute path, and gate commands with exit codes.
- The traceability table covers FLOW-02 through FLOW-07, which is appropriate because FLOW-01 is covered by artifact/`--check` and review rather than a workflow transcript.

### Concerns
- **HIGH — The two-attempt repair evidence is not reliable with exactly one injected compile error.** `09-08-PLAN.md:129` proposes one missing semicolon and then requires exactly two attempts. A normal first repair will likely make it green. Replace with two deterministic, separately observable failures, or a fixture where the first legitimate smallest fix demonstrably reveals the next error.
- **MEDIUM — The dry run samples only scaffold and controller end to end; native-tests and wiring are not explicitly evidenced.** The transcript can still satisfy FLOW-03 by proving the loop pattern, but the plan should label that sampling and record why the remaining block types are not observed.
- **MEDIUM — Leg 3’s one-shot run may exercise block execution without explaining whether confirmation guardrails still apply.** One-shot skips comprehension and pauses but must not skip commit/flash guardrails. Add an explicit observation.
- **MEDIUM — The “one-shot” homework uses the same temporary root as the guided run and `gen_views.py` may regenerate views for two IDs.** That is valid, but the transcript should state that this is disposable and not a real course assignment, and record both generated view diffs separately.
- **LOW — Absolute-path privacy is tested only against `/Users/`.** That fits this machine, but a path under `/var` could still be private. Prefer recording only the chosen root’s basename/relation or a project-local name, then assert no absolute path at all for sensitive lines.
- **LOW — The final privacy regex targets `WOKWI_CLI_TOKEN` only.** It is reasonable for this phase, but a manual checklist should also catch generic token-shaped output from device logs.
- **LOW — The phase gate is run after the transcript is written but before its commit; any gate-triggering transcript repair could produce a second revision. That is normal but should be recorded, not hidden.

### Suggestions
- Use a staged negative build fixture with two distinct compile errors whose first fix does not resolve the second; record both errors, both smallest fixes, and an escalation attempt count of exactly two.
- Add a short validation-sampling table to the transcript: scaffold and controller are end-to-end; native-tests/wiring/report are contract-sampled unless run.
- In the one-shot leg, explicitly record that commit/flash guardrails were not bypassed.
- Redact absolute roots from the entire transcript, not just `/Users/`; use `temporary root` and file-relative paths after Leg 0.
- Extend the token scan beyond `WOKWI_CLI_TOKEN` to any value-shaped secret string captured from device output; remove rather than redact.
- Record every transcript repair and rerun, including whether the full gate was rerun after the edit.

### Risk Assessment
**MEDIUM.** The dry run is structurally correct and privacy-conscious. The FLOW-06 negative-path design is the main obstacle to honest phase evidence; fix that before treating success criteria as verified.

---

# Cross-Plan Assessment

## Overall Findings

- **Best-designed backbone:** 09-01. It correctly reuses the repository’s existing manifest/check pattern rather than inventing a second mechanism.
- **Highest execution risk:** 09-03. It is the most central plan but currently contradicts actual scaffold/template behavior for ESP-IDF language, arbitrary boards, task provenance, and ID acquisition.
- **Highest evidence-design risk:** 09-08. The planned single-semicolon negative test is unlikely to demonstrate the required two-attempt cap.
- **Best safety plan:** 09-05. The consent gate and no-interpretation rule directly map to FLOW-07/D-20.
- **Documentation completeness gap:** 09-06 should update more than the stale “planned” phrase; the repository-layout and generated-paths inventory also become stale.

## Requirement Coverage
- FLOW-01: covered across 09-01, 09-02, 09-03, 09-04, 09-05, 09-06, 09-07.
- FLOW-02/FLOW-03/FLOW-04/FLOW-05: implemented by 09-03, evidenced by 09-08. Fix the ID/provenance/language/board issues first.
- FLOW-06: implemented by 09-04, evidenced by 09-08, but the negative fixture needs redesign.
- FLOW-07: stubs by 09-01 and 09-02; flash by 09-05 and 09-08.

## Priority Changes Before Execution
1. Fix 09-03’s ESP-IDF `language: cpp` contradiction and either define non-default-board support or explicitly stop for it.
2. Add ID acquisition, task provenance, and no-original-course-material rules to 09-03.
3. Add `scripts/gen_skills.py` and `scripts/metadata/` to 09-01’s affected-path/hook policy, and make the lint surface distinguish authored `.claude/skills/` from generated `.agents/`.
4. Correct 09-02’s impossible “seven skills” Wave-2 criterion to four stubs.
5. Redesign 09-08 Leg 5 as a two-observable-failure fixture.
6. Expand 09-06’s `AGENTS.md` layout/generated-file documentation.

## Overall Risk Assessment
**HIGH to MEDIUM.** The plan set has strong architecture, real integration points, good security thinking, and clear requirement coverage. The phase goal is technically achievable as planned, but 09-03 should not enter execution unchanged: it conflicts with the actual ESP-IDF template, missing provenance handling, and ambiguous ID/board contracts. The dry run must also be redesigned to make FLOW-06 observable rather than merely asserted.

---

## Codex Review (codex-beam)

# Plan Review — Phase 9: Agent Workflow and Skills

Reviewed against repo state (2026-10-26). Verified claims against `scripts/gen_views.py`, `scripts/metadata/paths.py`, `scripts/affected.py`, `.pre-commit-config.yaml`, `.gitignore`, `scripts/tests/test_tooling_config.py`, `scripts/tests/test_affected.py`, `.claude/CLAUDE.md`, `scripts/tests/temp_root.py`, `AGENTS.md`.

The phase delivers no runtime change — it adds the canonical skill tree, a generated mirror, one stdlib generator, a drift hook, a state file contract, and a dry-run transcript. The overall design is sound and well-researched. My concerns concentrate on plan 01 (generator contract drift from the verified reference), plan 07 (the generator invocation for CLAUDE.md), and plan 08 (machine-verifiability of "prose contracts").

## 09-01

**Summary:** Builds the phase spine: stdlib-only `scripts/gen_skills.py`, `write_skills_root` fixture builder, generator tests, the `simulate` canonical stub plus mirror and ledger, the drift hook, affected-path policy, `.gitignore` negations. It copies the `gen_views.py` spine — but several of its stated invariants diverge from the verified source.

**Strengths**
- Correctly chooses a **separate** `generated.skills.manifest` (A1): `gen_views.py:104-108` allowlists exactly three root files and `_validate_entry` at `gen_views.py:397` calls `_allowed_target`, so reading an out-of-allowlist entry is exit 2 — the research doc verified this and the plan respects it.
- `git check-ignore` verification is the right way to prove Pitfall 3 (`!generated.skills.manifest`), and adding `.skill-state` to `no-generated-files` plus `.gitignore` matches AGENTS.md "no-generated-files hook fails when any is tracked anyway."
- Extending `.agents/` to the markdownlint exclude (`^(\.planning/|\.claude/|\.agents/)`) mirrors the existing line at `.pre-commit-config.yaml:98`.

**Concerns**
- HIGH: the plan says the generator's discovery needs `.claude/skills/` to exist and errors otherwise, but it also names `--dir` (and `resolve_root` from `scripts/metadata/paths.py:33-42` defaults to `git rev-parse --show-toplevel`). A `--dir /tmp/...` run with no `.claude/skills/` is a perfectly valid smoke-test invocation the generator would refuse — inconsistent with the fixture-driven tests (`temp_root.write_skills_root` creates a separate root). The plan should define the absence of the canonical root as `CREATE`/empty, not a usage error, or state that `--dir` always must contain `.claude/skills/`.
- HIGH: classification semantics contradict `gen_views.py`. The plan says write mode emits `DELETED` for obstructions; but verified `gen_views.py:43-52` status set is `CREATE, UNCHANGED, MODIFIED, DELETE` (not `DELETED`) and write mode **repairs** absent targets as `CREATE` while `DELETED` is check-mode only (`"a whole-file target that is absent on disk is a CREATE in write mode and a DELETED record only in check mode"` — i.e. gen_views emits `DELETED` only under `--check`). The plan's own bullet says "in check mode `DELETED` when a manifest-listed file is absent" then separately "write mode repairs `CREATE`/`MODIFIED` and only deletes a marker-bearing orphan" — good, but the leak of terminology (`DELETED` vs `DELETE`) will confuse the implementation. Audit the exact `gen_views.py` status names and mirror them verbatim.
- MEDIUM: symlink refusal test asserts "Symlink at a mirror target and at an intermediate component exit 2." Plan 01 references the `gen_views` precedent, but `gen_views.py` I read only has `lstat`-ish `_component_conflict` *asserted* by the plan — I did not find the implementation in the read file (only referenced). The plan must copy-not-invent; verify the exact function name exists in gen_views before "copying verbatim."
- MEDIUM: the `gen-skills-check` hook block in 09-01 uses `.pre-commit-config.yaml` with `files:` regex `^\.claude/skills/` etc. but is NOT registered in `test_tooling_config.py`'s hook-id tuple until the same plan edits it. The plan says "Add `gen-skills-check` to the hook-id tuple in `test_every_fast_hook_keeps_the_pre_commit_stage`." Fine — but the tuple in the repo (lines 1255-1264) enumerates 13 hooks; adding one makes 14, and the HOOK COUNT assertion in vscode.md says "14 hooks on commit." These two need to ship in the same wave or 09-06's "14 hooks" text-contract will fail mid-flight. Both are wave 1 (09-01) so OK, but worth flagging that 09-06 (wave 2) depends on 09-01 carrying the tuple edit — it does (`depends_on: [09-01]`).
- LOW: `generated_header` second constant says `<!-- GENERATED — do not edit. Run: uv run scripts/gen_skills.py -->` (no `--all`). `gen_views.py:84-86` uses `--all`. Inconsistency is fine because gen_skills has no subcommand — but document why.

**Suggestions**
- Rewrite the classification bullets to consume `gen_views.py`'s actual exit table and status names before implementation; cross-reference exact line ranges (`gen_views.py:43-52`, `:397`, `gen_views` BLOCKING_STATUSES).
- Add a unit test that-Nazi-spray: run the generator twice on the same disposable root and assert byte-identical stdout/exit — the `test_gen_views.py` suite presumably does; mirror it.

**Risk Assessment:** MEDIUM — the generator's status-name divergence risks a one-line bug that the `--check` test would catch, so recoverable.

## 09-02

**Summary:** Authors the shared guardrails and the three remaining stubs (hw-report, schematic, course-index), completing the four-stub inventory. Straightforward, low-risk documentation authoring.

**Strengths**
- Correctly identifies that `_shared/` must be mirrored as a file with no `SKILL.md` (Pattern 7 trap), and the test plan in 09-01 covers `_shared` mirroring.
- `course-index` omitting `disable-model-invocation` makes it the only model-invocable skill — matches D-03.
- Stub banner gives the manual command, so a user meets a working fallback rather than a dead end.

**Concerns**
- MEDIUM: `hw-report`, `schematic`, `course-index` stub descriptions use past-tense capability claims ("Placeholder for running the Wokwi scenario and recording its evidence" — that's `simulate`). For the three new stubs the descriptions must say "placeholder" and the banner must say what it does *not* do. Review-enforced per D-18/D-19, so not a gate failure, but inconsistent wording ships easily.
- LOW: Plan 02's verification runs `uv run scripts/gen_skills.py --check` from repo root; at that point the mirror for `_shared/` exists and the generator is wired, so OK.
- LOW: `docs/standards/vscode.md` hook count (13→14) is edited in 09-06, not here; 09-02 doesn't touch it. Fine.

**Risk Assessment:** LOW.

## 09-03

**Summary:** The centerpiece — guided + one-shot `new-homework` over the eight-topic prose bank, five deliverable blocks, three checkpoints, conflict records. Big task, big token budget.

**Strengths**
- D-11 fixes `mode` first and the intake bank section order is explicit and matches FLOW-02.
- Prose-not-schema for the bank (D-12) correctly follows the pruned test class precedent (261026-ky7) — review-enforced by design.
- State file schema records all D-13 fields before the menu (D-14) — crash-safe checkpoint ordering.

**Concerns**
- HIGH (unresolved — 09-08 also flags it): all of FLOW-02..FLOW-05 satisfaction is review/manual; there is no machine test of the prose contract. That's an intentional D-18 decision, but the phase gate's `python3 -m unittest discover scripts/tests` will NOT exercise these. The dry-run transcript (09-08) is prose-in-transcript evidence, which is only as trustworthy as the maintainer's assertion that they did the run. Note: 09-03's own `<verify>` lists `python3 -m unittest scripts.tests.test_new_homework -v` — that file does not exist yet (the generator suite in 09-01 adds test_gen_skills; there is no `test_new_homework`). This is a lookup failure; either rename or accept LOW confidence claim.
- HIGH: the scaffold command `UV_CACHE_DIR="$TMPDIR/uv-cache" uv run scripts/new_homework <id> --template <name>` — `TMPDIR` is a user env var; the F-01 friction log note says `UV_CACHE_DIR` pointed at a writable directory, but `resolve_root` invokes git which fails after shell quoting? Fine. Real concern: the command uses `--dir <root>` to scope a run; `resolve_root` resolves `--dir` with `.resolve()` (paths.py:32). Fine.
- MEDIUM: `gen_views.py --all --dir <root>` requires the target root to carry the authored README marker region. Leg 0 of 09-08 adds it, but the SKILL.md says "When the target root has no authored README.md carrying the generated marker region, the generator exits 2; record that the view regeneration was skipped." That means a normal guided run in the real repo doesn't skip (root README exists), but the documentation implies a branch — fine, but the SKILL.md wording should clearly state "default: runs it; skip only if exit 2."
- MEDIUM: the idempotence assertion in the skill accepts both `CREATE` and `UNCHANGED` for `new_homework`, but `gen_views.py --all` runs on every scaffold block — that generator is not idempotent across roots? Actually it is (gen_views is deterministic). But running gen_views after every `--dry-run`? The skill doesn't distinguish dry-run scaffolding; D-22 dry run uses `--dir` root. Fine.
- LOW: "Mode is the first question (D-11)" and one-shot asks only non-inferable intake. The level of "non-inferable" is subjective; irs review-enforced.

**Risk Assessment:** MEDIUM (unchanged from plan; prose-heavy, no machine evidence).

## 09-04

**Summary:** Implements `hw-build`: two-leg bounded repair, escalation payload, dated records. Good scope. Mostly prose.

**Strengths**
- Strict two-attempt cap per run, per leg, with explicit escalation fields — directly addresses FLOW-06 ("at most twice").
- Names F-05 friction facts (native `-Werror`; both fakes reset in `setUp`; idle button HIGH) so a repair doesn't fabricate them.

**Concerns**
- MEDIUM: verification step runs the real homework build to "prove commands." Good, but the plan requires it in the gate; the plan's own gate already includes build step at 09-08. Repetitive but not harmful.
- MEDIUM: `MAX = 2` counter definition is left to the model reading prose — exactly the "per error vs per run" kid trap listed under assumptions. The dry run (09-08 Leg 5) is the only check. Accepted by D-18; keep but state explicitly "counter increments per outer run, not per distinct error."
- LOW: "shared `tests/` suite runs only when the diff touches `lib/`, mirroring the affected-path fan-out rule" — but `hw-build` runs `pio test -d tests -e native`. Does it do a `git diff` to determine the touch? The skill scope creep: it would need git access. The plan should state the trigger (a user flag or a diff check), else ambiguity.

**Risk Assessment:** MEDIUM-LOW.

## 09-05

**Summary:** `hw-flash` real-but-minimal: explicit consent, upload, bounded capture. Solid, narrow scope. Good.

**Strengths**
- "accepts only the exact `так` or `yes`, case-insensitive, with no other text" — strict gate wording, matching guardrails.
- Forbids pre-approving `upload` in `allowed-tools` and forbids remembering consent — strong elevation control.
- Bounded capture (20s) to ignored path with "never interpret" — clear D-20 minimal-real boundary.

**Concerns**
- MEDIUM: "Stdlib Python subprocess with `timeout=20`" executes; the skill is prose, so who runs the Python subprocess? Ambiguity — the agent runs it. Feature paragraph mixing prose instructions with implementation details. Acceptable but the saved log path `.skill-state/logs/<id>.log` must exist.
- LOW: "a second refusal returns to the user with no upload" — first refusal returns; fine. Wording could be clearer.
- LOW: Guardrails says "show board/environment and exact command" — plan tells reading `homework.yaml` + `platformio.ini` to determine them. No automated validation that these fields exist; relies on reviewer.

**Risk Assessment:** LOW.

## 09-06

**Summary:** Updates `AGENTS.md` live-skills layout note, routing row, generated-file two-class rule; vscode.md 13→14 hooks. Plus one concern about editing AGENTS.md that the docs pre-commit hook considers generated-view inputs.

**Strengths**
- Explicit assertion that "no `(planned, Phase 9)` text remains anywhere in the file" is testable.
- The two-class generated-file rule is a real CLAUDE.md-vs-build-output disambiguation critical for avoiding hand-edits.

**Concerns**
- MEDIUM: `AGENTS.md` is in `NO_BUILD_IMPACT` (exact file, affected.py line 184-205) — good, a docs-only change widens nothing. And the `gen-views-check` hook files pattern does include `AGENTS.md`? The pre-commit hook `files: (?x)^(README\.md$|...)` — I don't see `AGENTS.md` in the regex. Actually the hook checks `.generated.` input? AGENTS.md is not a generated view input (only three view files are). So editing AGENTS.md does NOT trigger `gen-views-check`. Fine. But it does trigger markdownlint — AGENTS.md is linted (exclude only `.planning/` and `.claude/`). This is fine; the text edits conform (typical hook output passes).
- LOW: vscode.md "Phase 7 simulation sentence" must be untouched (plan says only hook count/list). Hook's markdownlint exclude does NOT include docs (docs are linted). Fine.
- LOW: The verification uses a Python assertion script that checks exact tokens. Good; matches repo's contract-test style.

**Risk Assessment:** LOW.

## 09-07

**Summary:** Regenerate `.claude/CLAUDE.md` skills block via GSD generator output + single row in decisions table. Risk: the generator invocation command.

**Strengths**
- Correctly forbids hand-editing inside `GSD:` markers; insists on generator output with `--output`.
- Byte-verification outside the spliced region protects unrelated blocks.
- One-row decision (no ADR) matches repo's decisions table convention.

**Concerns**
- HIGH: the invocation `gsd_run query generate-claude-md --output "$TMPDIR/skills-claude-md.md"` — is `gsd_run` available in this environment? I see `~/.gsd-core/...` and a `gsd_run` referenced. The user's installed GSD (per context) — possibly absent in CI or when reproducing. The plan's fallback `~/.claude/gsd-core/bin/gsd_run`. Asserting that the generator path works is part of the plan's execution; if it isn't available, you cannot satisfy "the block lists seven skills" requirement. This is an infrastructure dependency that should be verified BEFORE waiving. Recommend capturing the actual command output as evidence.
- HIGH: The instruction says "Do not run the generator without `--output` in the working tree: the installed version re-emits every managed section and would append Project, Technology Stack, Conventions and Architecture fallbacks that this repository deliberately does not carry." That's a strong statement about a generator quirk. It assumes `--output` exists. If `--output` doesn't exist, no execution path satisfies. Verify the flag with `--help` first.
- MEDIUM: The byte assertion compares against `git show HEAD:.claude/CLAUDE.md`, but the splice result should match *the marker region*. I read the file and the marker content is "No project skills found. Add skills to any of..." — the plan's splice must result in a table of seven. The marker region including `## Project Skills` heading? The marker starts at `<!-- GSD:skills-start` and ends `<!-- GSD:skills-end -->`; the `## Project Skills` heading is *inside* the markers. The splice likely includes that. Ensure the spine contains both markers and the heading in one block.
- MEDIUM: "Every byte of `.claude/CLAUDE.md` outside the `GSD:skills` block is identical to the committed version" — assert `strip(cur) == strip(head)` whereas `strip` removes only the blocks. Wait: `strip()` only identifies the region by index. If the generator's splice adds a trailing newline, that's inside the region. OK.

**Risk Assessment:** MEDIUM — hinges on CLI availability and flag semantics that are not verified in the plan.

## 09-08

**Summary:** Runs the D-22 dry run against a disposable root, writes the transcript, runs the full gate. The phase-validation deliverable.

**Strengths**
- Correctly refuses to fabricate transcript steps: "never fabricate a step you did not run."
- Privacy check (scan `/Users/`, token-shaped values) is exactly the credential-leak guard.
- Leg 5 asserts `git status --porcelain homeworks/` empty afterwards — protects tracked tree.
- Leg 0 seeds the root README's generated region — addresses the gotcha note.

**Concerns**
- HIGH: nearly every requirement (FLOW-02 through FLOW-07) is verified *only* by this transcript. If the maintainer's session does not actually run `/new-homework` and `/hw-build`, the phase evidence is fabricated. The plan's own prohibition explicitly forbids fabrication — so the honesty depends on agent compliance. Recommend adding a small machine check that scripts/tests/test_new_homework... again, but that conflicts with D-18. There's no way around the deliberate no-validator decision. The only mitigation is a reviewer reading the transcript against actual `git status` timestamps.
- HIGH: Leg 5 "inject exactly one compile error into the copy's src/main.cpp (for example, replace one statement's terminating semicolon)" — the plan requires the failure to survive **two** repair attempts before escalating. But the skill's repair loop is bounded at 2. If the injected error is trivial, the model would fix it on attempt 1. The plan specifically needs the repair to FAIL both times to demonstrate escalation — this is a behavioural adversarial test, not an attack scenario AGENTmd? Refuse injection that's trivial to fix and ensure the fixture surfaces a build that's not arduino-local? Actually compile errors are easy to repair. The dry run must deliberately craft a fixture where two fix attempts succeed in *narrowing* but not resolving; this is hard for a single injected semicolon. Suggest documenting that the failure scenario uses a non-obvious defect (e.g., a wrong type requiring cross-file context) and that the second attempt makes it worse — careful wiring.
- HIGH: Leg 2 assertion `python3 -m unittest scripts.tests.test_new_homework -v` references a test file that does not exist in the planned 09-01 deliverables (only `test_gen_skills.py`). This verify fails immediately. Either extend the task's deliverables or drop the verify line. Suggest replacing with `python3 -m unittest discover scripts/tests`.
- MEDIUM: The six-gate command sequence in the close-out task: `uv run scripts/gen_skills.py --check` requires the new generator. Fine. But the existing gate per AGENTS.md quick-start uses `python3 -m unittest discover scripts/tests` (CI runs with `python`, not `uv`). The close-out uses both indistinguishably. Note the inconsistency (CI uses `python -m`, local uses `python3 -m`). Not a failure.
- LOW: "The transcript ... is tracked and committed alone." Confirming commit isolation means this plan changes only `09-DRY-RUN.md`. But if the dry run created/unignored state under `.skill-state/`, ensure it's removed before commit (D-13 says delete on success, keep on abort).

**Risk Assessment:** MEDIUM — the deliverable's quality is fundamentally a transcript-writing task that depends on the agent actually exercising skills.

---

## Cross-plan comparison notes

- **Wave alignment**: 09-01 → 09-06 → wave 3-4+5-8. Plan 09-06 declares `depends_on: [09-01]` only, but it edits AGENTS.md and vscode.md whose hook-count assertion (14) depends on 09-01 adding `gen-skills-check`. OK because both are wave 2 and pre-commit test (tuple) lives in 09-01. Good.
- **Hook orchestration**: The `gen-skills-check` hook needs `.agents/skills/` to mirror — 09-02/03/04/05 create further skill directories. Any hook `--check` between waves would fail. The gate steps run only at end, so the tree is reconciled once in 09-07. Good.
- **Generator source of truth**: `gen_skills.py` is created in 09-01 but 09-07 *regenerates `.claude/CLAUDE.md` using a *different* generator (`gsd-core`'s `generate-claude-md`), which scans `.claude/skills/` and `.agents/skills/`. Two generators overlap: gen_skills.py owns the mirror; generate-claude-md owns the adapter. The boundary is correctly drawn ("gen_skills.py owns the mirror, and gen_views.py stays scoped to the three view files"), but it takes 09-07 to prove generate-claude-md honours `.claude/skills/`. If it doesn't, `.agents/skills/` mirror skills get missed entirely. Verify during execution.
- **No content validator is a deliberate choice** (D-18). The transcript + manual review substitute. Fine; but 09-01 must not accidentally add skill-content assertions to `test_gen_skills.py`, and it doesn't.

## Overall risk assessment: MEDIUM

The infrastructure deliverable (generator + drift gate + gitignore policy) is solid and verified-ish against the existing generator. The workflow contracts are prose-by-design, so their evidence is manual dry run + transcript, which is the main uncertainty. The two highest-risk execution points are `gsd-core generate-claude-md --output` availability (09-07) and the bounded-repair negative test actually requiring an intractable fixture (09-08 Leg 5).

Recommended pre-execution checks before waiving all tasks:
1. `gsd_run query generate-claude-md --help` to confirm `--output` semantics.
2. Run the (non-existent) `test_new_homework` gate create — plan should edit it to `python3 -m unittest discover scripts/tests`.
3. Confirm `.claude/skills/` and `.agents/skills/` are not in `markdownlint-cli2` exclude list after 09-01's edits, since the mirror is *generated* and must not be linted. (09-01 task `files_modified` includes `.pre-commit-config.yaml` extension to markdownlint exclude — good.)

**No `##` sections were skipped — all 8 plan ids covered.**

---

## Antigravity Review

# Cross-AI Plan Review: Phase 9 (Agent Workflow and Skills)

This review evaluates the eight implementation plans for Phase 9 against the live codebase at `/Users/vloktiev/Dev/miltech/homeworks`. All claims, tool configurations, hooks, and path policies were verified against existing files and scripts in the repository.

---

## 09-01

### Summary
Plan 09-01 establishes the foundational canonical-to-mirror projection pipeline for agent skills by introducing the stdlib-only generator `scripts/gen_skills.py`, its ownership ledger `generated.skills.manifest`, the first stub skill `.claude/skills/simulate/`, and integration into the pre-commit hook surface and affected-path mapper. The plan faithfully mirrors the battle-tested architecture of `scripts/gen_views.py` while respecting project decisions (D-01, D-02, D-04, D-05) and security boundaries.

### Strengths
- **Clean stdlib-only implementation boundary**: Models `scripts/gen_skills.py` on `scripts/gen_views.py:57-80` and imports only stdlib modules plus shared helpers `CheckError`, `resolve_root`, and `read_regular_text` from `scripts/metadata/`. As verified in `scripts/metadata/render.py:13-16` and `scripts/metadata/paths.py:1-15`, these helpers avoid importing `yaml` or `jsonschema`, allowing the generator and its pre-commit hook to execute without extra virtualenv dependencies.
- **Fail-safe path mapping and build matrix isolation**: Updates `scripts/affected.py:95-105` (`NO_BUILD_IMPACT`) and `scripts/tests/test_affected.py:236-247` (`NoBuildImpactTests`) to include `.claude/`, `.agents/`, `generated.skills.manifest`, and `.skill-state/`. As implemented in `scripts/affected.py:403-411` (`_matches`), prefix matching on directories ending with `/` ensures skills documentation edits produce `{"build": [], "simulate": []}` rather than widening to all projects.
- **Strict pre-commit hygiene**: Updates `.pre-commit-config.yaml:98` to exclude `.agents/` from `markdownlint-cli2` (avoiding linter conflicts on generated Markdown) and adds `.skill-state` to `no-generated-files` (`.pre-commit-config.yaml:124-128`), ensuring `git add -f` cannot stage untracked checkpoint state.
- **Explicit-only invocation safety**: Enforces T-09-10 by transforming canonical skills that declare `disable-model-invocation: true` to insert an explicit invocation warning banner in `.agents/skills/`, preventing non-Claude agents from silently widening invocation.

### Concerns
- **[MEDIUM] Contract discrepancy regarding non-`SKILL.md` mirroring**: In Plan 09-01 Task 1 (prompt line 1832), the generator specification requires: `Every other mirror file is GENERATED_HEADER, a newline, then the canonical bytes unchanged.` Furthermore, the orphan deletion check (line 1838) requires `GENERATED_HEADER` on line 1 for any non-`SKILL.md` file. However, in Plan 09-03 Task 3 acceptance criteria (line 2465) and the architecture overview (line 793), reference files are described as `byte-identical to the canonical files`. If `scripts/gen_skills.py` prepends `GENERATED_HEADER` to reference files (such as `references/question-bank.md`), they will not be byte-identical; if it does not, orphan cleanup will fail to safely delete stale references.
- **[LOW] Frontmatter comment handling in scanner**: Task 1 specifies that `scan_top_level_blocks` scans lines starting at column 0 with `identifier:`. If authored frontmatter includes YAML comments (`# ...`) at column 0, a naive scanner will extract `# comment` as an unknown key and abort with exit code 2. The parser should explicitly ignore or preserve comment lines at column 0.
- **[LOW] Hook file trigger omissions**: The `files` regex for `gen-skills-check` in `.pre-commit-config.yaml` (`^((\.claude|\.agents)/skills/|scripts/gen_skills\.py$|generated\.skills\.manifest$)`) omits `scripts/metadata/`. While CI's `meta` job runs with `--all-files` (`.github/workflows/ci.yml:95`), local commits modifying `scripts/metadata/paths.py` would not trigger `gen-skills-check`.

### Suggestions
- Clarify the exact mirroring rule for files under `references/` and `_shared/`: standardize on prepending `GENERATED_HEADER` to all mirrored text files, and align Plan 09-03's acceptance criteria to expect `GENERATED_HEADER` at line 1 rather than strict byte-identity with the canonical source.
- Add explicit handling for `#` comment lines in `scan_top_level_blocks` in `scripts/gen_skills.py`.
- Include `scripts/metadata/` in the `files` pattern for `gen-skills-check` in `.pre-commit-config.yaml`.

### Risk Assessment
**LOW**: The plan is tightly scoped, reuses proven patterns from `gen_views.py`, and establishes comprehensive tests in `scripts/tests/test_gen_skills.py`.

---

## 09-02

### Summary
Plan 09-02 establishes `.claude/skills/_shared/guardrails.md` as the unified policy for critical actions (flashing, commits, PRs, ambiguity, secrets, and evidence) and adds three stub skills (`hw-report`, `schematic`, `course-index`). It mirrors them into `.agents/skills/` and updates `generated.skills.manifest`.

### Strengths
- **Rigorous guardrail structure**: Adopts the severity and enforcement register of `AGENTS.md` (e.g. `[MUST] [ENFORCED: review]`) for all operational guardrails, ensuring that rules for destructive actions like flashing (`pio run -t upload`) and committing/tagging remain unambiguous for LLM agents.
- **Accurate source-anchored fallback for `course-index`**: Anchors `course-index` to the exact generated region in `README.md` (`<!-- BEGIN GENERATED: homeworks -->` to `<!-- END GENERATED -->`, verified at `README.md:16-20`), avoiding ad-hoc metadata parsing while honoring single-source-of-truth principles (D-04).
- **Safe stub contract**: Implements D-19 and T-09-11 by marking stubs with `metadata.status: stub` and `version: "0.1"`, providing explicit body banners with manual command fallbacks (`wokwi-cli lint --offline`, `templates/report/report.md`, etc.).

### Concerns
- **[LOW] Model-invocation asymmetry for `course-index`**: `course-index` is the only skill where `disable-model-invocation: true` is omitted to allow auto-invocation. While Claude Code reads this frontmatter, non-Claude agents reading `.agents/skills/course-index/SKILL.md` rely purely on system prompt indexing. Ensure the description in frontmatter clearly states the intent so indexing tools parse it consistently.
- **[LOW] Incomplete validation of `_shared/guardrails.md` referencing**: While the plan ensures `_shared/` is mirrored as individual files and not treated as a skill directory, ensure the relative include paths from skills (e.g. `../_shared/guardrails.md`) resolve cleanly in both `.claude/skills/` and `.agents/skills/`.

### Suggestions
- In `_shared/guardrails.md`, include explicit examples of the accepted literal confirmation strings (`так` / `yes`) so all consuming skills share the exact same parsing rules.

### Risk Assessment
**LOW**: Pure documentation and markdown authoring with automated verification via `scripts/gen_skills.py --check`.

---

## 09-03

### Summary
Plan 09-03 implements the central `new-homework` skill, delivering an eight-topic adaptive question bank, state file schema (`.skill-state/<id>.json`), and the deliverable-level block loop supporting both guided and one-shot workflows.

### Strengths
- **Deterministic block breakdown and checkpointing**: Adopts deliverable-level block units (scaffold -> controller -> native-tests -> wiring -> report) per D-06. Checkpointing before prompt menus ensures resumability from `.skill-state/<id>.json` on context interruption.
- **Sanitized execution wrapping `scripts/new_homework`**: Validates the homework ID against `^[0-9]+_[0-9]+-[a-z0-9-]+$` (`scripts/metadata/paths.py:27`) and template names against `arduino|espidf`, passing them as argv elements rather than shell strings (T-09-03).
- **Graceful handling of scaffold idempotency**: Specifically accounts for friction finding F-01 (`.planning/phases/04.2-tracer-homework-1-3/04.2-FRICTION-LOG.md`), accepting both `CREATE` and `UNCHANGED` from `scripts/new_homework` (which exits 0 on both per `scripts/new_homework:22-25`).
- **Privacy and credential protections**: Mandates boolean-only recording for `simulation_token_present` (T-09-19), preventing secret tokens from leaking into local state files or git history.

### Concerns
- **[MEDIUM] Divergence on reference file mirror assertion**: Task 3 acceptance criteria (line 2465) asserts: `the references are byte-identical to the canonical files.` As identified in Plan 09-01, if `gen_skills.py` prepends `GENERATED_HEADER` to all non-`SKILL.md` files (line 1832), this assertion will fail. The assertion must match whatever header policy `gen_skills.py` implements.
- **[LOW] State file cleanup edge case**: Discretion allows deleting `.skill-state/<id>.json` after the report checkpoint. However, if the user terminates or the session aborts prior to report completion, untracked files remain in `.skill-state/`. While ignored by `.gitignore:262-265`, `new-homework` should define how a resumed run detects and handles a stale state file from an abandoned prior run.

### Suggestions
- Reconcile Task 3's acceptance criteria with `gen_skills.py`'s header insertion logic for `references/`.
- Specify state file resume semantics: if `.skill-state/<id>.json` exists when `new-homework <id>` is called, prompt the user whether to resume or start clean.

### Risk Assessment
**LOW**: The state machine and question bank are thoroughly specified, with strong isolation of inputs and shell commands.

---

## 09-04

### Summary
Plan 09-04 implements `hw-build` as the second active skill, wrapping `pio run -d homeworks/<id>` and `pio test -d homeworks/<id> -e native`. It defines a strict two-attempt repair loop with escalation diagnostics and shared-library fan-out rules.

### Strengths
- **Strictly bounded repair loop**: Limits automated fixes to at most two attempts per run (counted per run, not per error). After two failed attempts, it requires the agent to stop and escalate with full diagnostics, preventing destructive code generation loops.
- **Direct execution without obfuscating wrappers**: Uses real PlatformIO commands and captures native exit codes directly, eliminating misleading synthesized statuses (T-09-14).
- **Scope discipline**: Explicitly prohibits `git reset`, `git checkout --`, modifying untouched files, or weakening unit tests to achieve green builds.
- **Accurate affected fan-out**: Scopes runs of the top-level shared Unity suite (`pio test -d tests -e native`) to changes touching `lib/`, mirroring `scripts/affected.py:22-23`.

### Concerns
- **[LOW] Environment selection in multi-target projects**: The command specified is `pio run -d homeworks/<id>`. In `homeworks/1_3-police-flasher/platformio.ini:13`, `default_envs = esp32-s3-devkitc-1-n16r8` is defined, so `pio run` builds only that target. However, if a future homework defines multiple default environments or lacks `default_envs`, bare `pio run` will attempt to build all environments (including `native` if present in `platformio.ini`). `hw-build` should instruct the agent to inspect `platformio.ini` and specify `-e <default_env>` when ambiguous.

### Suggestions
- Explicitly instruct `hw-build` to check for `default_envs` in `platformio.ini` or read the target environment from `homework.yaml` to ensure deterministic target invocation.

### Risk Assessment
**LOW**: High-confidence plan with verified real commands (`pio test -d homeworks/1_3-police-flasher -e native` verified passing with 38 tests).

---

## 09-05

### Summary
Plan 09-05 implements `hw-flash` as a minimally real skill with a mandatory human consent gate before running `pio run -d homeworks/<id> -t upload`, followed by bounded serial capture to `.skill-state/logs/<id>.log`.

### Strengths
- **Uncompromising elevation gate (T-09-21)**: The consent prompt explicitly prints the target board, environment, and exact command, and strictly requires a literal affirmative (`так` or `yes`). Any empty input, question, or ambiguity immediately aborts upload.
- **Portable bounded capture**: Recognizes that `timeout(1)` is absent on macOS (`which timeout` verified exit code 1) and specifies a stdlib Python subprocess with `timeout=20` to capture serial output without external dependencies.
- **V0.1 boundary protection**: Prohibits log interpretation, heuristic claims of hardware success, or automated generation of report measurement rows from raw logs, avoiding speculative log parsing.

### Concerns
- **[MEDIUM] Hardcoded monitor baud rate**: Line 2832 specifies `pio device monitor -d homeworks/<id> -b 115200`. While standard for ESP32, `homeworks/1_3-police-flasher/platformio.ini:20` already sets `monitor_speed = 115200`. Hardcoding `-b 115200` on the CLI overrides `monitor_speed` for boards or homeworks that require a different baud rate (e.g., 9600 for standard Arduino or 74880 for bootloader diagnostics).
- **[LOW] Serial port contention / busy errors**: If serial capture fails because the device port is disconnected or locked by another monitor process, the subprocess will exit with an error. The skill instructions should state that serial monitor capture errors after a successful upload should report a capture warning without falsely claiming the flash itself failed.

### Suggestions
- Allow `pio device monitor` to default to the `monitor_speed` declared in `platformio.ini`, passing `-b` only if explicitly specified by the user or absent from configuration.

### Risk Assessment
**LOW**: Strong security and elevation safeguards around physical hardware flashing.

---

## 09-06

### Summary
Plan 09-06 updates `AGENTS.md` to transition project skills from "planned" to active, adds a rule distinguishing uncommitted build output from committed generated projections, and updates the commit hook count from 13 to 14 in `docs/standards/vscode.md`.

### Strengths
- **Resolution of rule ambiguity in `AGENTS.md`**: Addresses the apparent contradiction in `AGENTS.md:223-226` where all generated files were described as uncommitted, clarifying the distinction between untracked build artifacts (`.pio/`, `compile_commands.json`) and committed generated projections (`.agents/skills/`, `generated.skills.manifest`).
- **Verbatim source alignment**: The replacement targets in `AGENTS.md:70-71` (`Planned: report structure...`) and `AGENTS.md:272` (`| Reuse a versioned workflow skill |`) match the live text exactly.
- **Accurate developer guidance**: Updates `docs/standards/vscode.md:154` from 13 to 14 hooks and inserts `gen-skills-check` in sequence after `gen-views-check`, providing the exact repair command (`uv run scripts/gen_skills.py`).

### Concerns
- **[LOW] Coupling with hook installation**: Updating `vscode.md` to state 14 hooks must stay in lockstep with Plan 09-01's addition of `gen-skills-check` to `.pre-commit-config.yaml` to ensure `scripts/tests/test_tooling_config.py:1248-1261` and manual counts remain coherent.

### Suggestions
- None; the plan is precise and touches only documentation and rulebook text.

### Risk Assessment
**LOW**: Documentation and rule alignment with minimal risk of regressions.

---

## 09-07

### Summary
Plan 09-07 regenerates the `GSD:skills` section in `.claude/CLAUDE.md` from the completed skills tree, appends a decision record row to `docs/decisions/README.md`, and runs the full phase gate (`pre-commit`, `check_metadata.py`, `unittest`).

### Strengths
- **Critical safeguard against CLI pollution**: Verified live in repo: running `~/.claude/gsd-core/bin/gsd_run query generate-claude-md` directly without `--output` modifies `.claude/CLAUDE.md` and appends unnecessary fallback sections for Project, Stack, Conventions, and Architecture. Plan 09-07's requirement to run with `--output "$TMPDIR/..."` and splice only the `GSD:skills-start` to `GSD:skills-end` markers prevents repository corruption.
- **Verbatim decision table conformance**: The proposed row in `docs/decisions/README.md` exactly conforms to the six-column format (`Date | Decision | Why | Change cost | Status | Record`) established in `docs/decisions/README.md:12-32`.
- **Pre-dry-run gate verification**: Executes the entire local gate surface (`pre-commit run --all-files`, `uv run scripts/check_metadata.py`, `python3 -m unittest discover scripts/tests`) before Phase evidence generation.

### Concerns
- **[LOW] Binary location fallback**: As verified on the host system, `gsd_run` is not on the user's default `PATH` (`which gsd_run` exits 1), but exists at `/Users/vloktiev/.claude/gsd-core/bin/gsd_run`. The plan correctly notes this fallback, but executing agents should ensure the fallback path is checked first.

### Suggestions
- None; the splice verification script in Task 1 thoroughly validates that nothing outside the skills block was altered.

### Risk Assessment
**LOW**: Clean integration and validation plan with safeguards against generator side-effects.

---

## 09-08

### Summary
Plan 09-08 executes the phase dry run (D-22) in a temporary root, exercising `new-homework` (guided, one-shot, and conflict legs), `hw-build` (clean build and failing repair loop), and `hw-flash` (consent gate without hardware). It records the end-to-end evidence transcript in `.planning/phases/09-agent-workflow-and-skills/09-DRY-RUN.md`.

### Strengths
- **Isolated execution via `build_root`**: Leverages `scripts/tests/temp_root.py` to create a disposable root for homework scaffolding and negative test injection, protecting the tracked working tree (`homeworks/1_3-police-flasher/`) from unintended edits.
- **Privacy and credential audit**: Enforces T-09-16 with an automated test checking that no private host paths (`/Users/`) or token-like credentials appear in the committed transcript.
- **Complete requirement traceability**: Maps legs directly to FLOW-02 through FLOW-07 in a formal traceability matrix within the transcript.

### Concerns
- **[HIGH] Flawed failure injection in Leg 5 (Task 2)**:
  Task 2 specifies:
  > *Leg 5 — `hw-build` failing twice, then escalating: build a second disposable root with `build_root`, copy `homeworks/1_3-police-flasher` into it, and inject exactly one compile error into the copy's `src/main.cpp` (for example, replace one statement's terminating semicolon)... Confirm the transcript shows exactly two attempts.*

  And Task 2 verification asserts:
  ```python
  python3 -c "from pathlib import Path; t=Path('.planning/phases/09-agent-workflow-and-skills/09-DRY-RUN.md').read_text(encoding='utf-8'); need=['## Leg 4','## Leg 5','## Leg 6','attempt 1','attempt 2','no third edit','-t upload','non-affirmative','no upload']; missing=[n for n in need if n not in t]; assert not missing, missing; assert 'attempt 3' not in t"
  ```
  **Failure mechanism**: Per Plan 09-04 Task 1, `hw-build`'s instruction mandates: *"Attempt 1: inspect compiler diagnostic, find the first actionable error, apply smallest surgical fix to that file only; re-run failing command. If green, proceed to the other leg or report success."*
  If the injected compile error is simply a missing semicolon, a compiler diagnostic clearly identifies the missing semicolon (`expected ';' before...`). The surgical fix in Attempt 1 will restore the semicolon and re-running `pio run` will **succeed**. The skill will report SUCCESS and exit. Attempt 2 and escalation will **never execute**, causing the verification assertion (`assert 'attempt 2' in t and 'no third edit' in t`) to fail.
- **[MEDIUM] Absolute path scrubbing in compiler diagnostics**: In Task 3, verification enforces `assert '/Users/' not in t`. However, real compiler outputs from `pio run` and `pio test` emit absolute paths (e.g. `/Users/vloktiev/.../src/main.cpp:12:3: error:`). Pasting raw compiler diagnostics directly into `09-DRY-RUN.md` without path sanitization will trigger this assertion failure.

### Suggestions
- **Fix Leg 5 error injection**: Instead of a trivial syntax error, inject a conceptual or multi-file compile error that cannot be fixed by a simple single-file syntax edit (e.g., an incompatible signature in a header with multiple conflicting call sites, or a call to an unavailable hardware peripheral API) so Attempt 1 and Attempt 2 both fail honestly before escalation.
- **Sanitize compiler output**: In the transcript capture instructions, explicitly require replacing `$HOME` or `/Users/<name>/` with `<home>` or relative paths in all command outputs.

### Risk Assessment
**HIGH**: The logic bug in Leg 5's error injection will cause the automated verification of the dry-run transcript to fail unless the injected error is adjusted to genuinely survive Attempt 1.

---

## Overall Phase Risk and Recommendations

### Overall Risk Level: **MEDIUM**
The architecture, modularity, and tool contracts across all 8 plans are exceptionally well engineered. The primary risks are:
1. **The Leg 5 dry-run simulation flaw in Plan 09-08**, which must be adjusted to use an error that fails Attempt 1.
2. **The mirror header consistency conflict between Plan 09-01 and Plan 09-03** regarding whether `references/*.md` receive `GENERATED_HEADER` or are byte-copied.
3. **Hardcoding monitor baud rate in Plan 09-05**, which should defer to `platformio.ini`.

Resolving these three items will ensure seamless, deterministic phase execution.

---

## Consensus Summary

All three reviewers covered all eight plans and grounded their findings in the live repository. The
agreement is unusually tight on the phase's one material evidence defect and on the architecture of
the generator work; the disagreement is concentrated in how much risk plan 09-03 carries.

### Agreed Strengths

- **The generator work reuses a proven spine instead of inventing a second one.** `09-01` follows
  `scripts/gen_views.py`'s ledger, atomic-write, exit-code and drift-check pattern, and correctly
  chooses a separate `generated.skills.manifest` rather than extending the three-file allowlist in
  `scripts/gen_views.py:104-108` (D-04). All three reviewers verified this against the source.
- **The explicit-only invocation transform is correct.** Removing `disable-model-invocation` is not
  enough to keep a skill explicit-only across clients; the mirror banner closes that gap.
- **`hw-flash`'s consent gate is the right shape.** Literal `так`/`yes` only, no remembered consent,
  no pre-approved `upload` in `allowed-tools`, and no log interpretation — all three reviewers rate
  this the strongest safety design in the phase.
- **`new-homework`'s block loop and checkpoint ordering are sound.** Deliverable-level blocks
  (scaffold → controller → native-tests → wiring → report), state written before a checkpoint menu,
  and D-11's `mode`-first ordering are consistently praised.
- **The stub contract gives users a working fallback.** `metadata.status: stub`, an explicit body
  banner, and the manual command mean a stub is not a dead end.
- **The dry run isolates its work.** `scripts/tests/temp_root.py`-based disposable roots, tracked-tree
  cleanliness assertions, and the `/Users/` + token-shape privacy scans are the right controls.

### Agreed Concerns

- **HIGH — the dry run cannot prove FLOW-06's two-attempt cap as designed (`09-04`, `09-08`).** All
  three reviewers independently reached this. `09-08` Leg 5 injects one missing semicolon and then
  expects exactly two repair attempts plus escalation. `hw-build`'s own contract applies the smallest
  surgical fix on attempt 1, which restores the semicolon and turns the build green — attempt 2 and
  the escalation never run, so the transcript assertion fails and the central FLOW-06 evidence is
  absent. Required change: use a staged fixture with two separately observable failures (the first
  legitimate fix reveals the second), or a multi-file defect that cannot be repaired in one edit.
- **MEDIUM/HIGH — the mirror contract for `references/` is underspecified (`09-01`, `09-03`).**
  `09-01` says every non-`SKILL.md` mirror file starts with `GENERATED_HEADER` (needed for safe orphan
  cleanup), while `09-03` asserts reference files are byte-identical to their canonical source. Both
  cannot be true, and the plan does not say what happens to files deeper than
  `references/<file>`. Pick one policy and align both plans and their tests.
- **MEDIUM — `scripts/metadata/` is missing from the `gen-skills-check` `files:` regex (`09-01`).**
  The generator is planned to import `resolve_root` and `read_regular_text` from
  `scripts/metadata/`, and the existing `gen-views-check` includes that directory. Without it, a
  helper-only change can leave the local hook untriggered.
- **MEDIUM — `hw-flash`'s hardcoded `-b 115200` overrides `monitor_speed` (`09-05`).**
  `homeworks/1_3-police-flasher/platformio.ini:20` already declares `monitor_speed = 115200`; the CLI
  flag silently overrides any board that needs another rate. Let PlatformIO read the config, or
  derive and validate the value.
- **MEDIUM — a failed serial capture must not read as a failed flash (`09-05`).** Upload success with
  a monitor failure or timeout has to report "capture unavailable" while keeping the upload exit
  code as the real result. Several reviewers also ask for the state-file path discipline (component
  `lstat`, symlink refusal, atomic creation) to be mirrored for `.skill-state/logs/<id>.log`.

### Divergent Views

- **`09-07` depends on `gsd-core generate-claude-md --output`.** codex-beam rates this HIGH and asks
  for the flag to be verified before the plan relies on it; antigravity reports having exercised the
  live generator and rates the plan LOW; codex-glm rates it MEDIUM and asks for the tool version and
  exact command to be recorded. This is a cheap pre-execution check: run
  `gsd_run query generate-claude-md --help` and capture its output with the tool revision.
- **How much risk `09-03` carries.** codex-glm rates it HIGH on concrete contradictions with the
  repo — ESP-IDF `language: c` vs `templates/homework-espidf/homework.yaml:8`'s `cpp`, the scaffold
  hardcoding `esp32-s3-devkitc-1`, missing homework-ID acquisition despite `.skill-state/<id>.json`,
  missing `task.md` provenance intake, and a "quote the acceptance criteria verbatim" branch that
  conflicts with `AGENTS.md`'s no-original-course-material rule. antigravity rates it LOW and treats
  the same contract as well specified. Treat the codex-glm findings as open questions to verify
  against the templates before execution rather than as accepted defects.
- **Whether authored `.claude/skills/` prose is linted.** codex-glm flags that
  `.pre-commit-config.yaml:98` excludes all of `.claude/`, so the seven canonical skill bodies stay
  outside markdownlint; the other two do not raise it (codex-beam only asks that the generated mirror
  stay excluded). Worth a direct check, since `09-06`'s "authored Markdown is linted" wording becomes
  inaccurate if the exclusion is unchanged.

### Notable single-reviewer HIGHs (unconfirmed)

- `09-02`'s seventh acceptance criterion expects seven skill directories at Wave 2, when only four
  stubs exist (codex-glm). The count belongs in the wave that adds the last implemented skill.
- `09-03` and `09-08` verify with `python3 -m unittest scripts.tests.test_new_homework`, a test file
  no plan creates (codex-beam). Use `python3 -m unittest discover scripts/tests` or add the file.
- `09-01`'s status vocabulary drifts from `scripts/gen_views.py:43-52` (`DELETE`, not `DELETED`, and
  write-mode repair behaviour) (codex-beam).

### Overall Risk

**MEDIUM**, with one HIGH-severity evidence defect. The architecture, integration points and safety
gates are strong; the phase is not ready to execute unchanged until the dry-run Leg 5 fixture can
actually exercise two failed repairs, the reference-mirror policy is settled in both plans, and the
`09-03` findings above are checked against the real templates.

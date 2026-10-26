---
phase: 7
reviewers: [codex-glm, codex-beam, antigravity]
reviewed_at: 2026-10-26T14:00:47Z
plans_reviewed: [07-01-PLAN.md, 07-02-PLAN.md, 07-03-PLAN.md, 07-04-PLAN.md]
models:
  codex-glm: "glm-5.3-flash:cloud (reasoning=high)"
  codex-beam: "beam:cloud (reasoning=high)"
  antigravity: "gemini-3.8-flash-high"
model_sources:
  codex-glm: "pinned"
  codex-beam: "pinned"
  antigravity: "pinned"
---

# Cross-AI Plan Review — Phase 7

> Note: codex-glm and codex-beam share the codex adapter; their consensus is cross-model, not cross-tool.

<!-- gsd:plan-revision-conflicts:begin -->
## Plan-Revision Conflicts
<!-- gsd:plan-revision-conflicts:end -->

## Codex Review (codex-glm)

# Cross-AI Plan Review — Phase 7 Simulation Spike

I checked the plans against the repository rather than reviewing them in isolation. Below is my structured feedback, including concrete file/line evidence where it supports a finding.

## 07-01

### Summary

Plan 07-01 is the strongest of the four. It turns the measured Phase 4.2 friction into narrowly scoped infrastructure: promote the Wokwi merge action to a shared `scripts/pio` post script, keep the inherited compiledb script, and pin both the merge command and the documented Wokwi path resolution with network-free tests. The scope fits D-12/D-13 and avoids building a premature simulation gate.

### Strengths

- The plan correctly starts from the real files. The current post action is still project-local in `homeworks/1_3-police-flasher/merge_firmware.py:20-54`, and the homework currently calls `post:merge_firmware.py` beside the inherited `pre:../../scripts/pio/compiledb.py` in `homeworks/1_3-police-flasher/platformio.ini:18-22`.
- The `extends` pitfall is real and already documented in the source: `platformio.ini` has two explicit comments that `extends` replaces list options wholesale, and `platformio.shared.ini:19` supplies the inherited compiledb entry. The plan preserves that entry while changing the post action.
- The proposed SCons guard and extracted pure command builder are a sensible response to the current script. Its `Import("env")` at `homeworks/1_3-police-flasher/merge_firmware.py:8` makes import-only testing impossible today.
- The plan respects the existing ruff setup. `pyproject.toml:18-22` currently has the two-site F821 allowlist; removing the project-local entry after the move is internally coherent.
- The namespace-package assumption is sound: `python3 -c "import importlib.util; print(importlib.util.find_spec('scripts.pio'))"` currently reports a namespace module spec, even though `scripts/pio/` has no `__init__.py`.
- The path-probe design is appropriately behavioural, not prose-matching. The existing README already documents the project-relative option spelling and the local `WOKWI_CLI_TOKEN=dummy` proof in `homeworks/1_3-police-flasher/README.md:38-42`, which the plan turns into a real command execution test.

### Concerns

- **LOW** — The plan claims `_quote` ensures that a metacharacter “cannot split the command,” but a simple double-quote wrapper does not neutralize shell constructs inside double quotes, such as an embedded `$`, backtick, or double quote. The existing implementation at `homeworks/1_3-police-flasher/merge_firmware.py:12-14` is only a quoting approximation. This is acceptable for trusted local build paths, but the threat row in the plan overstates the guarantee.
- **LOW** — “At least six cases” is a weak test-count gate. It is easy to satisfy with overlapping cases that still omit an important argv boundary.
- **LOW** — The Plan 01 verification includes `git grep -n "homeworks/1_3-police-flasher/merge_firmware.py"`, which is not quoted in the plan. This will fail in most POSIX shells unless the path argument is written as `'homeworks/1_3-police-flasher/merge_firmware.py'`. The intended check is correct; the command spelling is not.
- **LOW** — The plan does not explicitly require deleting `homeworks/1_3-police-flasher/merge_firmware.py` through a clean `git rm`-style operation. This is likely implicit in implementation, but a tracked-file deletion check would be stronger than `test ! -e` alone.

### Suggestions

- Keep `_quote` for spaces, but either state honestly in the module docstring and threat model that it provides argument atomicity for repository-controlled paths, not arbitrary shell metacharacter sanitization, or pass arguments without shell string composition if PlatformIO/SCons supports an argv-safe execute surface.
- Replace the case-count language with named required cases: argv order, offset rendering, path quoting, output target, board fallbacks, and missing-package failure.
- Make the file-deletion verification explicit: `pio run` succeeds, the merged image exists, `test ! -e` passes for the old file, and `git diff --exit-code HEAD -- ...merge_firmware.py` proves the tracked copy is removed rather than merely absent from the live working tree.

### Risk Assessment

**LOW-MEDIUM.** The mechanics and dependencies are sound and trace directly to existing source. The main implementation risk is a subtle SCons import/registration mistake or the `extends` regression, but the plan already gates both with a real build and compiledb output.

---

## 07-02

### Summary

Plan 07-02 is a disciplined measurement-only plan: it creates the labelled evidence record, measures the quota-free ladder first, then asks the owner to execute the token-gated Wokwi sessions outside the sandbox. The protocol structure, quota accounting, and token secrecy are mostly strong. The biggest defect is an internal verification contradiction around the documented dummy-token assignment.

### Strengths

- The free-paid ordering is correct. Local lint, path resolution, clean/warm builds, and merged-image generation can all be measured without consuming Wokwi quota.
- The plan preserves the project’s existing token-boundary language. The README already states that the only token value that belongs in that file is `dummy` at `homeworks/1_3-police-flasher/README.md:38-42`.
- The protocol separates simulator wall-clock from simulated minutes, and Plan 02 explicitly prohibits deriving quota from wall-clock (`07-02-PLAN.md:41-42`). This is an important distinction.
- The serial observation rule is honest and avoids turning three runs into a false statistic.
- The evidence file is scoped to `.planning/phases/07-simulation-spike/07-SPIKE-EVIDENCE.md`, which is appropriate for raw spike output.

### Concerns

- **HIGH** — Plan 02’s global verifier contradicts its own approved dummy-token test. It states that `git grep -n "WOKWI_CLI_TOKEN=" -- ':!*.md'` must find no assignment, but Plan 01 deliberately creates `scripts/tests/test_simulation_paths.py`, which will contain `WOKWI_CLI_TOKEN=dummy`. The README also documents `WOKWI_CLI_TOKEN=dummy`, though it is excluded by `*.md`. The verifier will therefore fail on the intended state. Evidence: `07-02-PLAN.md:228` versus the dummy-token environment construction required by Plan 01.
- **MEDIUM** — The owner-run invocation is piped into `tee`, but no `set -o pipefail` is specified. In zsh without `pipefail`, `$?` after the pipeline is the status of `tee`, not the timestamp wrapper or Wokwi CLI. The wrapper’s `EXIT` line can help, but the fixed capture asks the owner for “the exit code,” inviting the wrong value. Evidence: `07-02-PLAN.md:116` and `07-02-PLAN.md:161`, plus the timestamp wrapper in `07-RESEARCH.md:298-306`.
- **MEDIUM** — The task says the protocol is “copy-ready,” but it does not explicitly tell the owner how to materialize `$TMPDIR/stamp.py` before running the invocation that starts with `python3 -u "$TMPDIR/stamp.py"`. The evidence file may include the wrapper source, but the protocol should include a one-line action such as “save the following block as `$TMPDIR/stamp.py` first.” Evidence: `07-02-PLAN.md:116`.
- **MEDIUM** — Run failure semantics are under-defined for status propagation. Plan 02 permits any run row, including exit 1. Plan 04 then has a precondition of “at least one executed Wokwi run with an exit code, a serial observation and a quota entry” before flipping `simulation.status` to `verified` (`07-04-PLAN.md:188`). A failing executed run should not justify `verified`; Plan 02 should explicitly feed a `scenario passed`/`scenario failed` result into Plan 04.
- **LOW** — The evidence verifier requires the exact text `Simulator cold/warm`, which is a reasonable structural gate but brittle if the table renames a column slightly. More important is that the evidence table records both cold/warm intervals, not that it repeats one exact string.
- **LOW** — The fixed capture includes the “full stamped output” but does not specify whether ANSI sequences are stripped before recording. Research flagged this, but the Plan 02 task does not.

### Suggestions

- Change the token verifier to distinguish allowed dummy assignments from real credentials, for example: allow `WOKWI_CLI_TOKEN=dummy` in the simulation-path test/README, reject the variable in shell/CI/workflow files, and require the owner-supplied token sentence verbatim.
- Add `set -o pipefail` to the zsh owner-run protocol, or remove the pipe and redirect stamped output directly to a capture file so the subsequent `$?` is unambiguous.
- Add an explicit step to save the timestamp wrapper as `$TMPDIR/stamp.py`, with a checksum or short SHA-256 of the wrapper content if reproducibility matters.
- Record ANSI stripping as part of the fixed capture rules.
- Before Plan 04 can run, require either an exit-0 successful Wokwi run or an explicit “simulation remains `pending` because every executed attempt failed” state in the evidence record.

### Risk Assessment

**MEDIUM.** The safety boundary around the real token is mostly well designed, and the free ladder is sound. The main risks are not measurement failure but verifier inconsistency, wrong exit-code capture through the pipe, and an overly permissive handoff to Plan 04 after a failed run.

---

## 07-03

### Summary

Plan 07-03 correctly treats the self-hosted Velxio attempt as a role-proportional, owner-run capability probe. It is honest about mutable image identity, AGPL separation, and the likely inability of the self-host editor to consume a PlatformIO project. Its main flaw is an evidence-capture gap: it asks for a board-list observation in the recording task but does not ask the owner for any capture that could substantiate that observation.

### Strengths

- The digest-first approach is correct for the mutable `ghcr.io/...:master` tag. Recording `RepoDigests`, not the tag, is the right evidence identity.
- The plan explicitly prevents the worst evidence mistake: manufacturing a Velxio compile/serial result by porting the pilot to a different sketch.
- The AGPL/MIT boundary is clear and correctly positioned: the image is referenced only, with no vendored code or assets.
- The honest outcome hierarchy from research is preserved: either a real boot observation, a separately labelled capability compile, or `not measured` with an exact reason.

### Concerns

- **HIGH** — Task 2 requires a “board-list observation from the running editor: ESP32-S3 and ESP-IDF present, STM32 absent” (`07-03-PLAN.md:124`), but Task 1’s fixed owner capture is only pull output, digest, `docker run`, poll result, and the last 50 log lines (`07-03-PLAN.md:98-102`). There is no specified way to observe or substantiate the board list. Without that protocol, the agent may record a board claim from memory, inference, or vendor README alone despite the plan’s own flagged assumption requiring a live-container observation.
- **MEDIUM** — “Boot wall-clock” is underspecified. The plan records both the `time docker run` value and a timed `curl` poll, but does not define which interval constitutes boot. The natural measured interval is from `docker run` start to first HTTP 200; the plan should say that explicitly.
- **MEDIUM** — The plan says “do not retry a different port,” but a port-3080 conflict will otherwise yield a false `not measured` conclusion. It should permit a deterministic prerequisite such as removing an existing container named `velxio` before the one and only attempt; that is cleanup, not a retry with a different tool/strategy.
- **LOW** — The verifier `git status --porcelain` should show only the evidence file (`07-03-PLAN.md:184`) will also see `07-03-SUMMARY.md`, which the same plan tells the agent to create. The intent is probably “no source tree file changes,” but the literal verifier is likely too strict.
- **LOW** — If the container runs but the browser UI never becomes usable, the evidence may contain a measured boot and no board/capability observation. The plan should state that this is a valid, honest outcome rather than requiring an unbounded UI exploration.

### Suggestions

- Extend the owner capture instructions to include the exact proof of the board observation, for example: named screenshot, copied UI text, a page URL, or the exact reason the board list was unavailable.
- Define boot readiness as `docker run` start → first HTTP 200, with the `docker run` wall time and first poll time recorded separately.
- Add a bounded number of poll retries and an explicit timeout so “poll until 200” cannot turn into an unbounded owner wait.
- Change `git status --porcelain` verification to “no changes outside `.planning/phases/07-simulation-spike/`.”
- Add a cleanup instruction: if `velxio` already exists, remove it before the single named attempt; still do not change the image tag or port.

### Risk Assessment

**MEDIUM-HIGH.** The plan’s evidence philosophy is right, but the board-list observation lacks a capture protocol. That turns a planned “observation from the running container” into a likely unverifiable or invented claim unless the instructions are strengthened.

---

## 07-04

### Summary

Plan 07-04 is the evidence-to-decision plan: write ADR-0014, add the decision table row, flip `simulation.status`, correct stale present-tense prose, and regenerate views. The ADR structure is well chosen and the generated-file mechanics are correct. However, the plan’s prose-amendment scope and its `verified` gate are too optimistic: the current report contains several simultaneous “not executed / pending” statements, and the plan’s verification checks only one phrase. Its unconditional status flip also risks publishing `verified` after a merely executed but failed Wokwi attempt.

### Strengths

- The generated-file coupling is correctly identified and verified. The existing docs-pins test at `scripts/tests/test_docs_pins.py:472-482` will fail if a new ADR is absent from `mkdocs.yml`, and `scripts/gen_views.py:1109-1177` scans `docs/decisions/` for navigation entries.
- The proposed status renderer is mechanically sound: `scripts/gen_views.py:780-789` will render a non-`none` tool and status as `wokwi (verified)`, and the schema already permits `verified` in `schema/homework.schema.json:57-66`.
- The plan correctly avoids schema changes for the executed-versus-lint distinction, matching the existing `additionalProperties: false` simulation definition.
- The ADR-number mapping 0004 → 0014 is necessary and accurate: `docs/decisions/README.md` already records ADR-0004 as the superseded licence decision, and no `docs/decisions/0014-simulator-selection.md` exists today.
- The platform-role matrix is a good primary decision artefact, especially because it prevents “Renode has no STM32” from being misstated.

### Concerns

- **HIGH** — The report is treated as having “two present-tense falsehoods,” but it has more stale simulation statements. At minimum, Plan 04’s own intended two edits would leave:
  - The Measurement Ledger’s L-08 row saying “Wokwi was not executed” (`homeworks/1_3-police-flasher/report.md:307`).
  - The traceability row T-15 saying execution “was not observed and `simulation.status` stays `pending`” (`homeworks/1_3-police-flasher/report.md:347`).
  - The conclusions again saying “The Wokwi scenario has not been executed” (`homeworks/1_3-police-flasher/report.md:421`), which Plan 04’s only prose grep checks.
  - The Decision Appendix saying execution is absent and status stays `pending` (`homeworks/1_3-police-flasher/report.md:471-473`).
  The verification `! grep -qF "has not been executed"` (`07-04-PLAN.md:214`) can pass while all of these other stale statements remain.
- **HIGH** — Plan 04’s `verified` precondition is too weak. It requires “at least one executed Wokwi run with an exit code, a serial observation and a quota entry” (`07-04-PLAN.md:188`), but it does not require exit 0 / scenario passed. D-10 says `verified` means an executed run with evidence, yet in the repository’s normal meaning `verified` also implies the described scenario passed. A failed execution should remain `pending` and be recorded honestly as a blocking result.
- **MEDIUM** — Plan 04’s must-have truth says ADR-0014 records “serial reliability as an exact count” (`07-04-PLAN.md:30`), but D-04 allows protocol B with a smaller count and serial reliability labelled `not measured`. The truth should be conditional: exact count under protocol A; explicit `not measured` under protocol B.
- **MEDIUM** — Plan 04’s ADR task says all measured quantities will be carried from the evidence, but Plan 03 may record Velxio pilot compile/serial as `not measured`. The ADR prose should not imply otherwise. The platform-role matrix wording is mostly correct, but Plan 04’s must-have should explicitly allow `not measured` Velxio pilot compile/serial rather than imply every category is measured.
- **LOW** — Plan 04 says the generated file will render `| Simulation | wokwi (verified) |`. The current renderer will render `wokwi (verified)`, but I would avoid relying on a precise Markdown spacing pattern in prose verification; the functional test against the generator is stronger.
- **LOW** — The report/README correction should also update report references to the merge artifact if necessary after Plan 01 moves `merge_firmware.py`; otherwise a report line may still name the now-deleted project-local path. `report.md:347` currently does so.

### Suggestions

- In Plan 04 Task 2, inventory every stale simulation claim in `report.md`, not just §7/§9 prose. At minimum, reconcile L-08, T-15, §9 conclusions, and Decision Appendix item 7. Keep each edit minimal and label any observed simulator value according to the existing vocabulary.
- Add an explicit Plan 02 → Plan 04 handoff condition: status may flip only if the evidence records a successful executed Wokwi run (`exit 0`) and the expected serial line, or an explicit alternative fallback that actually executed successfully; otherwise leave `simulation.status: pending`.
- Make the Plan 04 verifier scan for a list of forbidden stale phrases, not just `"has not been executed"`: for example `Wokwi was not executed`, `simulation.status` `stays pending`, and `Phase 7 owns the execution`.
- Update report traceability references from `merge_firmware.py` to `../../scripts/pio/merge_firmware.py` where appropriate.
- Add an explicit conditional form for protocol B in the ADR requirements: “exact count when protocol A completes; otherwise the smaller count and serial reliability `not measured`.”

### Risk Assessment

**HIGH until revised; otherwise MEDIUM.** The generated-file mechanics and ADR path are solid, but the plan could ship `verified` metadata alongside several report statements that still say execution never happened. It could also mislabel a failed executed run as verified. Both defects violate the phase’s transparency goals.

---

## Cross-plan checks

### Requirement coverage

- **SIM-02** is well covered across Plans 01–04. Plan 01 supplies the shared merge path and network-free command proof, Plan 02 supplies the Wokwi protocol, Plan 03 supplies Velxio evidence, and Plan 04 produces ADR-0014.
- **SIM-03** is covered by Plan 04’s Fritzing licence paragraph and no-artifact checks.
- **Phase boundary discipline** is generally good: Plan 01 explicitly forbids `simulate.py`, Plan 02 explicitly forbids CI/quota inference, and Plan 04 explicitly keeps the schema untouched.
- **SIM-01** is correctly left for Phase 11.

### Dependency ordering

The four waves are coherent:

1. Plan 01 must land before Plan 02 because the executed Wokwi run depends on the merged image through `wokwi.toml`.
2. Plan 02 must land before Plan 03 because Plan 03 records into the Velxio section of the evidence file.
3. Plan 04 correctly waits until both Wokwi and Velxio evidence exist.

One exception is Plan 04’s status gate: it needs a stronger success/failure condition from Plan 02 before the `verified` flip, as noted above.

### Shared quality gates

The proposed gates are strong:

- Real `pio run` and `compiledb` checks after promotion.
- Targeted stdlib tests for merge assembly and path resolution.
- `gen_views.py --all --check`.
- Existing docs-pins nav test.
- Metadata checker.
- Pre-commit.

The full suite’s sandbox limitation (`UV_CACHE_DIR`) is also handled in the plans’ proposed verification.

### Highest-priority revisions

1. Fix Plan 02’s contradictory dummy-token verifier.
2. Strengthen the Plan 02 → Plan 04 handoff so `verified` never triggers from a failed run.
3. Expand Plan 04’s stale-report correction beyond two sentences and beyond one grep phrase.
4. Add a board-list capture protocol to Plan 03.
5. Add `pipefail` or remove the measurement command pipeline in Plan 02.

---

# Consensus summary and recommendation

Overall, the plan set is unusually well grounded for a measurement spike. It avoids the most dangerous scope creep, preserves quota and secret boundaries, and correctly treats simulator output as distinct from hardware evidence.

However, it is not merge-ready as written:

- **07-01:** minor mechanical/test improvements only.
- **07-02:** proofread fixes are needed around verification, pipe handling, and success/failure handoff.
- **07-03:** needs a real observation protocol for the Velxio board list.
- **07-04:** needs the largest revision, primarily because the report contains several stale simulation claims and the `verified` flip is currently under-gated.

Recommended decision: **approve the structure, request targeted revisions before execution**. Plan 07-02 and 07-04 must be updated before the Wokwi session; 07-03 should be fixed before its own wave; 07-01 can proceed after only small mechanical fixes.

---

## Codex Review (codex-beam)

## 07-01

**Summary:** Plan 01 is the highest-value, lowest-risk engineering work in the phase: it turns a homework-local Wokwi post action into a shared, testable PlatformIO tool and pins its pure command-assembly logic and F-19 path behavior before any quota is spent. The move is well-scoped and the clean/build compiledb rollback line is plausible.

**Strengths**
- Promotes `homeworks/1_3-police-flasher/merge_firmware.py` into `scripts/pio/merge_firmware.py` in one change, satisfying D-12 and removing the copy (`homeworks/1_3-police-flasher/merge_firmware.py:10-12` currently performs unguarded `Import("env")`).
- Repeats the inherited `pre:` line explicitly, which is correct because `extends` replaces list options wholesale (`homeworks/1_3-police-flasher/platformio.ini:18-22`).
- Prunes the stale ruff ignore `"homeworks/*/merge_firmware.py" = ["F821"]` (`pyproject.toml:21`) in the same change.
- Uses F-19 as a behavioral, network-free probe with dummy token plus `WOKWI_CLI_SERVER=ws://127.0.0.1:1`; this pattern has already been verified locally (positive reaches `Error connecting...`, negative reports doubled path).
- Tests are stdlib-only and follow repository conventions.

**Concerns**
- **LOW:** The plan’s `build_merge_command` signature in the research shape returns argv correctly, but the unit test must stub `env.subst("$ESP32_APP_OFFSET")` as a string. The code sketch says integer offsets use `hex()`; tests should assert both, as planned.
- **LOW:** The fingerprint guard “the plan installs nothing” is repeated every plan as boilerplate; not a technical issue.
- **MEDIUM:** The build trigger is `touch homeworks/1_3-police-flasher/src/main.cpp`, but the merge post action is attached to `$BUILD_DIR/${PROGNAME}.bin`; touching source rebuilds it, yet if incremental logic skips the app image, the merge line may not appear. A safer verification is `pio run -d ... -t clean` followed by `pio run`.

**Suggestions**
- Add one explicit clean-build verification in the automated checks, not only touch.
- In `test_simulation_paths.py`, assert ANSI-stripped text and handle `FORCE_COLOR` because `WOKWI_CLI_SERVER` runs in an environment where color output may occur (already planned).
- Keep `--elf` fixture creation inside `TemporaryDirectory` and never in the repository tree.

**Risk Assessment:** LOW — the plan is mostly mechanical, deterministic, and naturally rollbackable.

## 07-02

**Summary:** Plan 02 converts the free measurement ladder and protocol A into a human-in-the-loop evidence capture task rather than pretending automation can spend Wokwi quota. That is the correct split given the sandbox cannot reach `wss://wokwi.com`. Its main risk is external dependency: a real token, a working dashboard, and an owner available to provide captures.

**Strengths**
- Separates free measurements from metered sessions early per D-03, preserving scarce quota.
- Labels every value (`measured`, `calculated`, `datasheet`, `not measured`, etc.) and forbids deriving quota from wall-clock time.
- Makes protocol B explicit if quota consumption is unexpectedly high.
- Uses an exit-code mapping for 0/42/1, which matches `wokwi-cli` observed behavior.
- Records only the permitted token sentence, satisfying D-02 and security requirements.

**Concerns**
- **HIGH:** The plan is not fully automatable and gates later waves on an owner-run session. This is an execution risk, not a plan defect; if the token or dashboard is unavailable, SC2 cannot be satisfied.
- **MEDIUM:** The plan assumes the free plan still provides about 50 simulated minutes and a 5-minute cap; this is flagged in assumptions (A8) but the protocol must show a dashboard check before the first run.
- **LOW:** Task 1 performs repeated clean and incremental builds; the expected `wall clock` and `median` notation must remain distinguishable from simulated minutes.
- **LOW:** Evidence documentation can drift from actual capture if manually transcribed; the fixed capture format mitigates this.

**Suggestions**
- Require the owner to paste the raw stamped output and dashboard before/after figures before any summarization is accepted.
- If the first run returns exit 42 or a large quota delta, immediately switch to protocol B and document the reason instead of attempting additional quota use.

**Risk Assessment:** MEDIUM — the plan is sound, but success depends on external human action and quota semantics.

## 07-03

**Summary:** Plan 03 asks for a role-proportional Velxio self-host attempt and, correctly, makes boot measurement or a named failure the first artifact. It does not overclaim pilot compile or serial capabilities and explicitly guards AGPL contamination.

**Strengths**
- Records the digest rather than the mutable `:master` tag, which is the right identity control.
- Captures the five named Docker volumes, preventing misleading compile times after restart (research explicitly warns about this).
- Clearly distinguishes a generic capability observation from pilot compile time, avoiding inflated evidence (research A4).
- States that no Wokwi quota is consumed.

**Concerns**
- **MEDIUM:** The self-hosted Velxio editor may not load a PlatformIO project, so the likely outcome is `not measured` for pilot compile and serial. The plan handles this, but success must not be measured by a full pilot run.
- **MEDIUM:** Docker may be unreachable even outside the sandbox; the guide requires the owner to run outside the sandbox, but if unavailable, the attempt must stop with exact error text.
- **LOW:** `docker run -d ... -p 3080:80` creates a local service; cleanup/removal steps are not specified, though this is recoverable and not part of the repository.

**Suggestions**
- Include container teardown in the protocol after capture, or note that named volumes intentionally persist.
- Keep all Velxio evidence as reference-only and ensure no file under `docs/`, `homeworks/`, `lib/`, or `scripts/` is added.

**Risk Assessment:** MEDIUM — honest and well-bounded, but depends on external infrastructure and may yield limited data.

## 07-04

**Summary:** Plan 04 closes the phase by creating ADR-0014, flipping metadata on executed evidence, correcting present-tense report text, and regenerating views. The plan is mostly correct, but its report correction may be too narrowly scoped and should explicitly handle all stale simulation-status claims.

**Strengths**
- Links ADR-0014 from the decisions table and regenerates generated nav, satisfying both table-first and generated-view requirements.
- Changes only `simulation.status` and keeps the schema untouched, aligned with D-10.
- Uses generator regeneration rather than hand editing `docs/homeworks/1_3-police-flasher.md`, `mkdocs.yml`, or `generated.manifest`.
- Preserves the five-label vocabulary and warns explicitly against upgrading `simulated` to `measured`.
- Converts report/README to pointer-style corrections instead of performing deferred README expansion (D-15).

**Concerns**
- **MEDIUM:** Task 2 says it replaces two present-tense falsehoods in `report.md`, but the report contains additional stale claims:
  - `homeworks/1_3-police-flasher/report.md:286` says the scenario has not been executed and Phase 7 owns execution.
  - `homeworks/1_3-police-flasher/report.md:421` says the Wokwi scenario has not been executed.
  - `homeworks/1_3-police-flasher/report.md:472-473` still says lint is the only verified result and `simulation.status` stays `pending`.
  After flipping metadata to `verified`, leaving these sentences will create a direct contradiction. The task should sweep all these sites explicitly.
- **LOW:** The report ledger row T-15 (`homeworks/1_3-police-flasher/report.md:347`) also records execution as pending. It may need an evidence update if Phase 7 changes the result.
- **MEDIUM:** The plan assumes the linked evidence file has at least one executed Wokwi run. This is an execution dependency from plan 07-02, not independently verifiable before that run occurs.
- **LOW:** The ADR is mapped to 0014 while roadmap wording historically references ADR-0004. This mapping is intentional (0004 is the license decision), but it requires consistent internal communication and later-phase references.

**Suggestions**
- Replace the task action to scan for all strings containing `has not been executed`, `stays \`pending\``, `Phase 7 owns...`, and report amendment locations, then update them in the same change.
- Explicitly include T-15 ledger update if execution succeeded, or annotate it as historical with an evidence link.
- Keep the ADR’s CI cost basis labeled `calculated`, with a stated `PRs_per_month=20` and sensitivity at 5 and 50, as planned.

**Risk Assessment:** MEDIUM — mostly governance/certification work, but the report text sweep is a real correctness gap.

---

## Antigravity Review

# Cross-AI Plan Review: Phase 7 — Simulation Spike

**Reviewer:** Antigravity (Independent Peer Review)
**Repository Under Review:** `/Users/vloktiev/Dev/miltech/homeworks`
**Phase:** 07-simulation-spike
**Plans Reviewed:** 4 (`07-01`, `07-02`, `07-03`, `07-04`)
**Evaluation Mode:** Full repository access confirmed; all claims verified against live codebase files and local runtime tooling.

---

## 07-01

### 1. Summary
Plan `07-01` delivers the prerequisite mechanical refactoring and local automated test fixtures for Phase 7 without consuming any Wokwi cloud quota. It promotes `homeworks/1_3-police-flasher/merge_firmware.py` into the shared location `scripts/pio/merge_firmware.py`, updates `homeworks/1_3-police-flasher/platformio.ini` to consume it via a relative `post:` extra script, cleans up the stale linter ignore in `pyproject.toml`, and establishes two fast, stdlib-based unit test suites (`test_merge_firmware.py` and `test_simulation_paths.py`). The plan is tightly scoped, addresses friction log items F-09 and F-19 directly, and enforces strict security and architectural isolation.

### 2. Strengths
- **Decoupled SCons Execution for Pure Testing:** The proposed guarded import pattern (`try: Import("env")` / `except NameError: env = None`) in [`scripts/pio/merge_firmware.py`](file:///Users/vloktiev/Dev/miltech/homeworks/homeworks/1_3-police-flasher/merge_firmware.py#L13) allows `build_merge_command` and `esptool_directory` to be imported and unit-tested in-process by [`scripts/tests/test_merge_firmware.py`](file:///Users/vloktiev/Dev/miltech/homeworks/scripts/tests/test_platformio_readers.py#L1-L25) without requiring SCons harness emulation.
- **Robust Network-Free Path Resolution Test:** Exploiting the undocumented CLI environment variable `WOKWI_CLI_SERVER=ws://127.0.0.1:1` combined with `WOKWI_CLI_TOKEN=dummy` enables [`scripts/tests/test_simulation_paths.py`](file:///Users/vloktiev/Dev/miltech/homeworks/scripts/tests/test_tooling_config.py#L1362-L1410) to definitively verify local path resolution for `--diagram-file` and `--scenario` without network access or cloud quota consumption.
- **Three-Valued Behavioral Verification:** Pattern 3 (positive connection error, negative doubled path error, and non-vacuity string check) follows the established precedent in [`scripts/tests/test_tooling_config.py:1362-1410`](file:///Users/vloktiev/Dev/miltech/homeworks/scripts/tests/test_tooling_config.py#L1362-L1410) (`ClangdGuideCommandTests`), preventing silent false passes. Live testing with `wokwi-cli 0.28.1 (7cf4ffaebfd8)` confirms that the negative control explicitly emits `Error: diagram.json not found in .../homeworks/1_3-police-flasher/homeworks/1_3-police-flasher/assets/diagram.json`.
- **Atomic Linter Policy Maintenance:** Removing `"homeworks/*/merge_firmware.py" = ["F821"]` from [`pyproject.toml:21-22`](file:///Users/vloktiev/Dev/miltech/homeworks/pyproject.toml#L21-L22) in the exact same commit as the file move prevents dead rules from lingering in configuration.

### 3. Concerns
- **[MEDIUM] Package Presence Check Does Not Guarantee Package Directory Availability:**
  In Task 1, the action specifies:
  > "Extract `esptool_directory(platform)` returning `platform.get_package_dir("tool-esptool")` after asserting `"tool-esptool" in platform.packages`; when the name is absent raise `SystemExit`..."

  In PlatformIO, `platform.packages` reflects the declared package metadata dictionary, but `platform.get_package_dir("tool-esptool")` will return `None` if the package has not yet been unpacked or installed on disk. In [`homeworks/1_3-police-flasher/merge_firmware.py:25`](file:///Users/vloktiev/Dev/miltech/homeworks/homeworks/1_3-police-flasher/merge_firmware.py#L25), calling `join(None, "esptool")` raises a `TypeError` traceback. `esptool_directory` must check that the returned directory is not `None` (e.g. `pkg_dir = platform.get_package_dir("tool-esptool"); if not pkg_dir: raise SystemExit(...)`).
- **[LOW] Hardcoded POSIX Binary Name:**
  In [`homeworks/1_3-police-flasher/merge_firmware.py:25`](file:///Users/vloktiev/Dev/miltech/homeworks/homeworks/1_3-police-flasher/merge_firmware.py#L25), the binary is resolved as `join(..., "esptool")`. On Windows hosts, the binary is `esptool.exe`. While the primary environment is macOS (`AGENTS.md`), adding a fallback check for `esptool.exe` or using `shutil.which` ensures true portability across student workstations.
- **[LOW] Global CI Fanout Impact:**
  Per [`scripts/affected.py:25-26`](file:///Users/vloktiev/Dev/miltech/homeworks/scripts/affected.py#L25-L26), modifications to `scripts/pio/...` are classified as global triggers that widen build matrices to all homework projects. Moving `merge_firmware.py` into `scripts/pio/` places it in this global fanout category.

### 4. Suggestions
- Update `esptool_directory(platform)` to validate both `"tool-esptool" in platform.packages` and `platform.get_package_dir("tool-esptool") is not None`.
- In `test_simulation_paths.py`, explicitly assert that the subprocess output contains `Error connecting to ws://127.0.0.1:1` without asserting on `ECONNREFUSED` vs `EPERM`, ensuring sandbox compatibility.

### 5. Risk Assessment
- **Rating:** LOW
- **Justification:** Zero quota consumption, highly reproducible in-process test fixtures, and all behavior has been experimentally verified against live CLI binaries.

---

## 07-02

### 1. Summary
Plan `07-02` executes the measurement spike for Wokwi and establishes the canonical evidence record `.planning/phases/07-simulation-spike/07-SPIKE-EVIDENCE.md`. It implements a disciplined local-first measurement ladder (lint, clean/warm build times, and network-free scenario validation) followed by two blocking human checkpoints for owner-executed Wokwi simulation runs outside the network-restricted sandbox. It enforces strict credential safety, captures raw serial lines and exit codes, and calculates serial reliability as an exact observation count (`3/3` or protocol B fallback).

### 2. Strengths
- **Local-First Quota Conservation:** Free metrics (offline lint, clean build, incremental warm build, scenario syntax validation) are collected first in Task 1. Simulated minutes are expended only after local correctness is proven.
- **Stringent Credential Protection:** Complying with ASVS V2 / V14, `WOKWI_CLI_TOKEN` is ingested silently via `read -rs WOKWI_CLI_TOKEN && export WOKWI_CLI_TOKEN`. No token is ever echoed, logged, or committed, and the evidence record standardizes on the exact sentence: `"token supplied by the repository owner; value not recorded"`.
- **Rigorous Timing Vocabulary:** Distinguishes build cold/warm from simulator cold/warm, and keeps wall-clock seconds strictly separated from simulated minutes (preventing Pitfall 12).
- **Proportional Protocol Fallback:** Provides an explicit circuit breaker (protocol B: single run) if the rolling quota consumption on the owner's free plan is higher than anticipated.

### 3. Concerns
- **[HIGH] Incomplete Error Handling for Execution Checkpoint Failures:**
  Task 2 instructions state:
  > "The owner pastes back exactly this fixed capture: (1) the full stamped output; (2) the exit code; (3) the serial log contents; (4) the dashboard usage figure before the run and after it; (5) the VCD path and its last timestamp if the file exists."

  If the owner's token has expired, free quota has run out (0 minutes available), or Wokwi's backend is unreachable, the run will exit with code 1 at the connection stage. In that scenario, items (3) and (5) will not exist, and (4) will show zero delta. While line 1886 notes "if any run exits 1, record the failure and quote the first error line", the instructions do not explicitly state how to format the capture when items (3)–(5) are absent, nor do they provide a distinct resume signal for a blocking failure (the current signal only accepts `"run 1 recorded"` or `"quota stop"`).
- **[MEDIUM] Precondition Conflict with Downstream Plan 04 on Failure:**
  The Roadmap success criteria state:
  > "2. A homework 1.3 scenario runs in Wokwi from `diagram.json` and `wokwi.toml`, or the ADR records a blocking failure and the chosen fallback with evidence."

  However, Plan `07-04` Task 2 precondition requires:
  > "`07-SPIKE-EVIDENCE.md` records at least one executed Wokwi run with an exit code, a serial observation and a quota entry."

  If Plan `07-02` records a blocking execution failure (e.g. quota exhausted or cloud outage), Plan `07-02` completes with failure evidence, but Plan `07-04` has no explicit branch for leaving `simulation.status: pending` while still recording the blocking failure in ADR-0014.
- **[LOW] Shell Portability of Wrapper Script Path:**
  Task 1 writes the timestamp wrapper to `$TMPDIR/stamp.py`, and Task 2 runs `python3 -u "$TMPDIR/stamp.py"`. Depending on how the owner launches their host shell session, `$TMPDIR` may be unset or point to different paths between subshells. Using an explicit path such as `/tmp/stamp.py` avoids environment divergence.

### 4. Suggestions
- Clarify in Task 2 instructions that if exit code is 1, items (3)–(5) are omitted and the first error line from stamped output is recorded.
- Add an explicit resume signal: `resume-signal: Paste the capture and type "run 1 recorded", or type "execution blocked: <reason>"`.
- Update Task 1 to ensure `stamp.py` is written to a deterministic location (e.g. `/tmp/stamp.py`).

### 5. Risk Assessment
- **Rating:** MEDIUM
- **Justification:** High external dependency on third-party cloud service and owner interaction outside the sandbox. Quota or network failures must not leave the workflow in an undefined state.

---

## 07-03

### 1. Summary
Plan `07-03` assesses Velxio as a self-hosted fallback simulator. Because the Docker daemon socket is unreachable inside the command sandbox (confirmed via `docker info: Cannot connect to the Docker daemon at unix:///Users/vloktiev/.docker/run/docker.sock`), Task 1 is defined as an owner-executed human checkpoint. Task 2 records the container image digest (`RepoDigests`), cold boot duration, observed board coverage, and the licensing boundary in `07-SPIKE-EVIDENCE.md`.

### 2. Strengths
- **Pinning Mutable Containers by SHA-256 Digest:** Rather than accepting the mutable tag `ghcr.io/davidmonterocrespo24/velxio:master`, Task 1 explicitly extracts and records the cryptographic digest via `docker inspect --format '{{index .RepoDigests 0}}'`.
- **Honest Evidence Depth:** Adheres strictly to D-05 and D-06 by forbidding artificial porting of the PlatformIO project into an Arduino sketch. If the self-hosted web UI cannot consume a PlatformIO project with symlinked `lib_deps`, it records `not measured — the self-hosted editor does not consume a PlatformIO project`.
- **Strict License Isolation:** Cites and enforces the AGPLv3 boundary: Velxio is referenced only as a containerized tool; no source code or assets are vendored into the MIT codebase.
- **Resource Discipline:** Identifies the requirement for named volumes (`velxio-ccache`, `velxio-build`, etc.) to prevent misleading 5–7 minute rebuilds on fresh container restarts.

### 3. Concerns
- **[MEDIUM] Incomplete Instructions If Docker Daemon Is Unavailable:**
  If the host system does not have Docker Desktop running, Task 1 instructs the owner to paste the error and type `"velxio unavailable"`, recording `not measured — <exact reason>`. However, Task 2 instructs:
  > "Record the board-list observation from the running editor: ESP32-S3 and ESP-IDF present, STM32 absent."

  If the container never ran, the agent cannot inspect the running editor. Furthermore, Task 2's automated verification contains:
  ```python
  hits = [k for k in ("@sha256:", "not measured", "AGPL", "STM32") if k in s]
  assert len(hits) >= 3, hits
  ```
  If Docker pull failed, `@sha256:` is missing. If the agent does not record `STM32` because it could not observe the board list, `len(hits)` drops to 2 (`not measured`, `AGPL`), causing verification to fail.
- **[LOW] Lack of Container Teardown Cleanup:**
  Task 1 launches a container named `velxio` on port 3080 with five persistent volumes. The plan should include a teardown command (`docker rm -f velxio`) in instructions or verification to avoid leaving a long-running daemon on the host.

### 4. Suggestions
- Clarify Task 2 instructions: if Docker was unavailable, record board coverage as `not measured (Docker unavailable; vendor documentation indicates ESP32/RP2040/AVR supported, STM32 absent)`. This ensures `STM32` is present in the text, allowing the test assertion (`len(hits) >= 3`) to pass cleanly.
- Provide an optional cleanup snippet (`docker rm -f velxio`) after measurements are captured.

### 5. Risk Assessment
- **Rating:** LOW
- **Justification:** Velxio is explicitly a secondary fallback measurement consuming zero Wokwi quota; failure to run Docker cleanly degrades to an honest `not measured` finding without blocking the phase.

---

## 07-04

### 1. Summary
Plan `07-04` consolidates the spike findings into `docs/decisions/0014-simulator-selection.md` (ADR-0014), updates the decision index in `docs/decisions/README.md`, updates [`homeworks/1_3-police-flasher/homework.yaml`](file:///Users/vloktiev/Dev/miltech/homeworks/homeworks/1_3-police-flasher/homework.yaml#L14-L17) (`simulation.status: verified`), corrects present-tense simulation claims in [`report.md`](file:///Users/vloktiev/Dev/miltech/homeworks/homeworks/1_3-police-flasher/report.md#L284-L286) and [`README.md`](file:///Users/vloktiev/Dev/miltech/homeworks/homeworks/1_3-police-flasher/README.md#L44-L45), and executes `scripts/gen_views.py --all` to synchronize `mkdocs.yml`, `docs/homeworks/1_3-police-flasher.md`, and `generated.manifest`.

### 2. Strengths
- **Strict Conformance to MADR Standard:** ADR-0014 replicates the exact structure established in [`docs/decisions/0013-clangd-multi-root-contract.md:1-50`](file:///Users/vloktiev/Dev/miltech/homeworks/docs/decisions/0013-clangd-multi-root-contract.md#L1-L50) (5 frontmatter keys, single `# ` heading, 8 standard sections).
- **Comprehensive View Synchronization:** Recognizes that both adding an ADR and updating metadata affect generated files: [`scripts/tests/test_docs_pins.py:472-480`](file:///Users/vloktiev/Dev/miltech/homeworks/scripts/tests/test_docs_pins.py#L472-L480) (`test_nav_lists_every_markdown_file_under_docs`) asserts that `mkdocs.yml` contains every Markdown file under `docs/`, and [`generated.manifest:21-25`](file:///Users/vloktiev/Dev/miltech/homeworks/generated.manifest#L21-L25) tracks SHA-256 and byte counts for [`docs/homeworks/1_3-police-flasher.md`](file:///Users/vloktiev/Dev/miltech/homeworks/docs/homeworks/1_3-police-flasher.md#L14). Running `uv run scripts/gen_views.py --all` ensures zero drift.
- **No Schema Degradation:** Explicitly forbids mutating [`schema/homework.schema.json`](file:///Users/vloktiev/Dev/miltech/homeworks/schema/homework.schema.json#L57-L68); `simulation.status: verified` is already a valid enum value.
- **Attribution & Evidence Ledger Integrity:** Adheres strictly to SIM-03 (Fritzing illustration only, no part graphics copied to assets) and preserves the five-label vocabulary in [`report.md:290-297`](file:///Users/vloktiev/Dev/miltech/homeworks/homeworks/1_3-police-flasher/report.md#L290-L297), forbidding any promotion of `simulated` values to `measured`.

### 3. Concerns
- **[MEDIUM] Hardcoded Assumption of Successful Simulation Run:**
  Task 2 states:
  > "Change `simulation.status` from `pending` to `verified` per D-10, only because an executed, evidenced run exists."

  And verification asserts:
  ```python
  assert 'status: verified' in y, 'status not flipped'
  ```
  If Plan `07-02` resulted in a blocking failure (as permitted by Roadmap SC2), `simulation.status` MUST remain `pending`. The verification assertion would fail and block execution. Task 2 must accommodate the conditional outcome: if Wokwi execution was blocked, `status` remains `pending`, the report notes the blocking failure, and `gen_views.py --all` synchronizes the `pending` state.
- **[LOW] Relative Link Resolution Across Boundary:**
  In Task 2, updating [`homeworks/1_3-police-flasher/report.md:284-286`](file:///Users/vloktiev/Dev/miltech/homeworks/homeworks/1_3-police-flasher/report.md#L284-L286) to point to `.planning/phases/07-simulation-spike/07-SPIKE-EVIDENCE.md` crosses into `.planning/`. In MkDocs, `.planning/` is not a published docs directory. The link works on GitHub, but will be a broken link if rendered in the MkDocs site unless referenced as a GitHub repository URL or relative path without breaking site build validation.

### 4. Suggestions
- Add conditional logic to Task 2: if an executed run succeeded, flip `status` to `verified`; if execution was blocked, keep `pending`, document the blocker in `report.md`, and assert `status: pending` or `status: verified` accordingly.
- Ensure markdown links in `report.md` point to `docs/decisions/0014-simulator-selection.md` for web readers and use clean relative paths for repository viewers.

### 5. Risk Assessment
- **Rating:** LOW
- **Justification:** Well-structured document and metadata updates protected by existing automated tests ([`test_docs_pins.py`](file:///Users/vloktiev/Dev/miltech/homeworks/scripts/tests/test_docs_pins.py#L472-L480), [`check_metadata.py`](file:///Users/vloktiev/Dev/miltech/homeworks/scripts/check_metadata.py#L1-L30), and `gen_views.py --check`).

---

## Cross-Plan Analysis and Integration Risks

1. **Dependency Pipeline Integrity:**
   - Wave 1 (`07-01`) -> Wave 2 (`07-02`) -> Wave 3 (`07-03`) -> Wave 4 (`07-04`) forms a clean sequential dependency DAG.
   - `07-02` strictly depends on `07-01` because [`wokwi.toml:3`](file:///Users/vloktiev/Dev/miltech/homeworks/homeworks/1_3-police-flasher/wokwi.toml#L3) points to `.pio/build/esp32s3_arduino/firmware.merged.bin`, which is produced by the promoted `scripts/pio/merge_firmware.py`.
   - `07-04` strictly depends on `07-02` and `07-03` to supply the raw numbers for ADR-0014.
2. **Generated File Consistency:**
   - Changes in `07-04` touch both `docs/decisions/` and `homeworks/1_3-police-flasher/homework.yaml`. Both affect generated files listed in [`generated.manifest`](file:///Users/vloktiev/Dev/miltech/homeworks/generated.manifest#L21-L49). The plan correctly mandates `uv run scripts/gen_views.py --all` followed by `--check` before completing the wave.
3. **Execution Branching on Cloud Service Outage:**
   - The primary systemic risk across the plans is the unhandled branch where Wokwi cloud execution cannot complete due to external quota or token issues. Roadmap SC2 explicitly provides for this (`"or the ADR records a blocking failure and the chosen fallback with evidence"`), but Plans `07-02` and `07-04` assume a successful run in their verification assertions. Adding fallback branching to both plans eliminates this risk.

---

## Overall Phase Risk Assessment

- **Overall Risk:** **LOW-MEDIUM**
- **Summary:** The phase is exceptionally well planned, grounded in measured codebase realities, and highly disciplined regarding security and licensing. The only significant integration risk is ensuring that external human checkpoints (Wokwi cloud token entry and Docker daemon availability) fail cleanly without breaking downstream assertions if external infrastructure is unavailable. With the recommended edge-case handling added, the plans provide a rock-solid roadmap to satisfying all five success criteria of Phase 7.

---

## Consensus Summary

All three reviewers independently opened the referenced files and cite `file:line` evidence. They
agree that the plan set is well grounded in the current tree: the preconditions match source (the
project-local `merge_firmware.py` is present, `scripts/pio/merge_firmware.py` is absent,
`wokwi-cli` is `0.28.1 (7cf4ffaebfd8)`), the four-wave dependency chain is coherent, and the
measurement-first ordering spends no Wokwi quota before local correctness is proven. The phase
structure is not in dispute. The disagreements are about how strictly Plan 04 gates the
`verified` flip, how completely the stale report prose is swept, and whether Plan 03 can
substantiate its board-list observation.

### Agreed Strengths

- Plan 01's guarded SCons import plus the extracted pure `build_merge_command` /
  `esptool_directory` make the merge action testable in process, and the plan preserves the
  inherited `pre:../../scripts/pio/compiledb.py` entry that `extends` would otherwise drop
  (`homeworks/1_3-police-flasher/platformio.ini:18-22`).
- Plan 01's path proof is behavioural, not prose-matching: the positive probe reaches the
  connection stage, the negative probe fails with the doubled path, and a non-vacuity assertion
  prevents an unrelated message from passing.
- Plan 02 measures the free ladder (lint, clean and warm builds, merged image, scenario
  revalidation) before any metered session, and keeps wall-clock seconds strictly separate from
  simulated minutes. Token handling is `read -rs`, with the single permitted sentence and no
  value written anywhere.
- Plan 03 records `RepoDigests` rather than the mutable `:master` tag, forbids manufacturing a
  compile by porting the pilot, and states the AGPL reference-only boundary.
- Plan 04 follows the ADR-0013 MADR shape, leaves the schema untouched, and routes every
  generated view through `gen_views.py --all` instead of hand edits.

### Agreed Concerns

- **HIGH — the `verified` flip is gated on execution, not success.** Plan 04's precondition is
  "at least one executed Wokwi run with an exit code, a serial observation and a quota entry"
  (`07-04-PLAN.md:188`), and its verification asserts `status: verified`. Roadmap success
  criterion 2 explicitly allows a recorded blocking failure as a valid outcome, so the current
  gate either flips `verified` after a failed run or blocks execution when Wokwi is
  unavailable. All three reviewers raised this; the fix is an explicit success condition
  (exit 0 plus the expected serial line) and a `pending` branch that records the blocker.
- **MEDIUM — the report correction is narrower than the stale prose.** Plan 04 amends §7 and §9
  but the report still contains `Wokwi was not executed` (`report.md:307`), traceability row
  T-15 saying execution "was not observed and `simulation.status` stays `pending`"
  (`report.md:347`), the conclusions sentence (`report.md:421`), and Decision Appendix item 7
  (`report.md:471-473`). The intended verifier greps only `has not been executed`, so it can
  pass while those contradictions ship beside `verified` metadata. Raised by codex-glm (HIGH)
  and codex-beam (MEDIUM); verified against source during synthesis.
- **MEDIUM — Plan 03 has no capture that can substantiate the board list.** Task 2 requires an
  observation "from the running editor" that ESP32-S3/ESP-IDF are present and STM32 absent
  (`07-03-PLAN.md:124`), while Task 1's fixed owner capture is only pull output, digest,
  `docker run`, poll result and the last 50 log lines (`07-03-PLAN.md:98-102`). Without a named
  screenshot, copied UI text, page URL, or an explicit "board list unavailable" reason, the
  observation is unverifiable. Raised by codex-glm (HIGH) and antigravity (MEDIUM).
- **MEDIUM — Plan 02 under-specifies failure and exit-code capture.** The owner-run invocation
  is piped into `tee` with no `set -o pipefail`, so in zsh `$?` is `tee`'s status rather than the
  wrapper's or the CLI's; and there is no defined capture format or resume signal when the
  token, quota or network fails and serial/VCD/dashboard items cannot exist. Raised by
  codex-beam (MEDIUM) and antigravity (HIGH).
- **LOW/MEDIUM — Plan 03's verification is brittle in the honest-failure path.**
  `git status --porcelain` will also see `07-03-SUMMARY.md`, which the plan itself creates
  (codex-glm), and the `len(hits) >= 3` assertion can fail when Docker is unavailable because a
  legitimate `not measured` result has no `@sha256:` digest (antigravity). Both are
  false-negative gates, not evidence defects; the assertion should distinguish "no digest
  because the pull never happened" from a missing record.

### Divergent Views

- **Plan 07-01** is LOW risk to codex-beam and antigravity, LOW-MEDIUM to codex-glm. The only
  material disagreements are mechanical: codex-glm notes that a double-quote `_quote` wrapper
  gives argument atomicity for repository-controlled paths but does not neutralize `$`,
  backticks or embedded quotes, so the threat row overstates it; antigravity notes that
  `get_package_dir("tool-esptool")` can return `None` even when the key is in
  `platform.packages`, so `esptool_directory` must check the returned path, not just membership.
- **Plan 07-03** is MEDIUM-HIGH to codex-glm, MEDIUM to codex-beam, LOW to antigravity. The
  disagreement is whether an unsubstantiated observation is a plan defect or an acceptable
  `not measured` outcome; all three accept that the attempt consumes no Wokwi quota.
- **Plan 07-04** is HIGH-until-revised to codex-glm, MEDIUM to codex-beam, LOW to antigravity.
  Antigravity treats the failure branch as a small conditional addition; codex-glm treats the
  stale-prose sweep as a merge blocker because it can publish `verified` beside "not executed".
- **Single-reviewer finding confirmed against source (not consensus):** codex-glm's HIGH that
  Plan 02's verifier `git grep -n "WOKWI_CLI_TOKEN=" -- ':!*.md'` (`07-02-PLAN.md:228`)
  contradicts Plan 01's own `WOKWI_CLI_TOKEN=dummy` in the new
  `scripts/tests/test_simulation_paths.py` — the `*.md` exclusion does not cover that test file,
  so the verifier fails on the intended state. codex-beam and antigravity did not raise it.
- **Single-reviewer finding (unverified by the others):** antigravity suggests a deterministic
  `stamp.py` location rather than `$TMPDIR`, because the owner's shell may resolve a different
  temporary directory than the agent's. codex-beam instead asks for an explicit step that
  materializes the wrapper before the invocation.

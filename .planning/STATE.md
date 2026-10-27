---
gsd_state_version: "1.0"
current_phase: 10
current_phase_name: Report and Evidence System
status: planning
stopped_at: Phase 10 context gathered
last_updated: "2026-10-27T13:37:00.375Z"
last_activity: 2026-10-27
last_activity_desc: Phase 09 complete, transitioned to Phase 10
state_head: 5c534836f88abec168079933a973d450adf6ff1b
progress:
  total_phases: 14
  completed_phases: 11
  total_plans: 92
  completed_plans: 92
  percent: 79
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-10-27)

**Core value:** Every homework ships as a self-contained, reproducible, industry-standard engineering artifact — code, evidence, and report — that can be understood and verified a year later.
**Current focus:** Phase 10 — Report and Evidence System

## Current Position

Phase: 10 — Report and Evidence System
Plan: Not started
Status: Ready to plan — Phase 09 shipped as PR #21
Last activity: 2026-10-27 — Phase 09 complete and shipped as PR #21; Phase 10 ready to plan

Progress: [████████████████████] 92/92 plans ([████████░░] 79%)

## Performance Metrics

**Velocity:**
- Total plans completed: 92
- Average duration: —
- Total execution time: 0.0 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 01 | 8 | - | - |
| 02 | 5 | - | - |
| 03 | 9 | - | - |
| 04 | 9 | - | - |
| 04.1 | 7 | - | - |
| 04.2 | 11 | - | - |
| 05 | 9 | - | - |
| 06 | 6 | - | - |
| 06.1 | 1 | - | - |
| 07 | 4 | - | - |
| 08 | 4 | - | - |
| 09 | 19 | - | - |

**Recent Trend:**
- Last 5 plans: —
- Trend: —

*Updated after each plan completion*
**Per-Plan Metrics:**

| Plan | Duration | Tasks | Files |
|------|----------|-------|-------|
| Phase 04.2 P01 | 2 min | 3 tasks | 9 files |
| Phase 04.2 P02 | 2 min | 3 tasks | 9 files |
| Phase 04.2 P03 | 1 min | 2 tasks | 7 files |
| Phase 04.2 P04 | 2 min | 3 tasks | 2 files |
| Phase 04.2 P05 | 1 min | 3 tasks | 2 files |
| Phase 04.2 P06 | 1 min | 2 tasks | 4 files |
| Phase 04.2 P07 | 2 min | 2 tasks | 3 files |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- Phase 5: one generator (`scripts/gen_views.py`) plus one committed `generated.manifest` own every repeated view; the manifest records a SHA-256 and byte count per entry and never lists itself.
- Phase 5: `--check` is a pure check enforced at exactly two points — a check-only pre-commit hook and a read-only PR job. `docs.yml` builds with warnings-as-errors and deploys through OIDC Pages from `main` only. Superseded 2026-10-26: the site is removed; the check-only hook and the read-only PR job remain for the three core views.
- Phase 5: third-party site assets are vendored, never CDN-loaded; KaTeX 0.19.0 ships with a 24-entry checksum ledger because a missing `extra_css` target produces no MkDocs warning at all. Superseded 2026-10-26: the vendor tree is removed with the site; the three core views render from their reviewed templates.
- Phase 5: the shared `{{name}}` renderer and the `platformio.ini` readers live in `scripts/metadata/`, so the scaffold, the architecture gate and the generator cannot hold two implementations of one fact.
- Phase 5: `scripts/affected.py` fails safe — `lib/**` fans out to every consumer and an unrecognised path widens to every project rather than being dropped.
- Phase 5: code review found two critical defects, both fixed before merge — HTML in a `title` reached the published site as live markup, and the generator followed symlinked `homework.yaml`/template inputs it otherwise refused. 20 lower-severity findings stay open in `05-REVIEW-DISPOSITION.md`; WR-13 (no PR-time site build or Python suite) belongs to Phase 8.
- Phase 5: the site is live at https://vloktiev-emb.github.io/homeworks/ (PR #12, `0384ed7`); the `build and deploy` run and the rendered pages were verified after merge. Superseded 2026-10-26: the site is removed and the URL is no longer a deliverable.
- 2026-10-26: the generated documentation site is removed — the Pages workflow, the MkDocs configuration and pins, the generated pages and vendor tree, and the three site-only templates are gone. `scripts/gen_views.py` keeps exactly three views (the README index, `homeworks.code-workspace`, `platformio.shared.ini`) with `generated.manifest`, `--check`, the `gen-views-check` hook and `generated-views.yml` intact. The owner sets the Pages source to `None` after merge. Re-entry triggers: five or more homeworks with a browsable catalogue wanted; a public portfolio landing page wanted; or docs and reports carrying diagrams or maths that read poorly in the repository view. See `docs/decisions/README.md` and `.planning/notes/ceremony-vs-engineering-principle.md`.
- Phase 6: clang-format 120 is a documented ESP-IDF approximation (ADR-0012); 23.1.3 is pinned through pre-commit and runs check-only, so the tracked tree is expected to conform rather than be reformatted.
- Phase 6: esp-clangd serves the multi-root workspace through `scripts/clangd-wrapper.sh` (ADR-0013). Its `--check[=<string>]` declaration means the headless command must attach the value: `--check=<file>`; the detached form exits 1.
- Phase 6: a documented command is regression-guarded by a positive, negative and non-vacuity test (`ClangdCheckCommandTests`), so a guide that drifts back to a rejected invocation fails the suite instead of shipping.
- Phase 6: the local quality layers are live (pre-commit fast hooks, clang-tidy on pre-push with a compile-database freshness guard); the CI layer stays Phase 8 (TOOL-05, TOOL-06).
- Phase 6: gap closure G-06-1 was a one-command documentation defect; the re-verification passed 56/56 must-haves with the covered-input digest recomputed by the CLI.
- Phase 06.1: clangd discovers compile databases upward only, so shared sources under `lib/` had none — the per-project databases are siblings. One generated root `compile_commands.json` merges the native, Arduino and ESP-IDF databases and stays untracked.
- Phase 06.1: the root `.clangd` names no `CompilationDatabase` on purpose, so each project's own fragment and the nearer `tests/` database keep precedence.
- Phase 06.1: `lib/common` and `lib/port` are compiled in three environments; the native context is the deliberate representative choice, not a wrong command.
- Phase 06.1: the wrapper's bounded allowlist gained `/usr/bin/gcc`, `/usr/bin/cc` and `/usr/bin/clang` because esp-clangd ships no resource headers; PATH is never consulted.
- Phase 06.1: both templates lack a compile database of their own and stay out of scope; the residual is recorded as a deferred follow-up.
- Phase 7: ADR-0014 replaces the roadmap's historical ADR-0004 reference; the record is evidence-based — Wokwi executed 3/3 (cold 3.759 s, warm 6.753/11.238 s), Velxio self-hosted from `ghcr.io/...@sha256:5d673722…`, Renode and Fritzing `not measured` with reasons.
- Phase 7: the five-label evidence vocabulary (`measured`, `calculated`, `simulated`, `datasheet`, `not measured`) plus `calculated (upper bound)` is semantic; a simulated value is never bench evidence and quota is never derived from wall clock.
- Phase 7: `simulation.status: verified` follows only `**Outcome:** scenario passed`; execution alone is not success, and a failed or blocked outcome leaves `pending` with a blocker.
- Phase 7: the shared `scripts/pio/merge_firmware.py` replaces the project-local copy; esptool 5 `merge-bin` runs in a clean build, and the failure path raises `RuntimeError`.
- Phase 7: no Velxio source, image layer or Fritzing part graphic is vendored; the AGPLv3 image is referenced by immutable digest only, and `diagram.json` stays the wiring source of truth.
- Phase 8: `gate` is the single required check on `main` (0 approvals, squash only); a cancelled dependency fails it closed, which is why a superseded run briefly reports red.
- Phase 8: `changes` fails safe — `AGENTS.md`, `.yamllint.yaml` and any other unrecognised path widen the matrix to every project, so this PR built `1_3` and `tests` despite touching neither.
- Phase 8: the PR title is enforced as `type(scope): summary` in `meta`, because squash-merge makes the title the commit subject; the first live run failed on a non-conforming title.
- Phase 8: simulation stays opt-in per pull request (`simulate` label, same-repository head, token at step level) and never enters the nightly matrix; one run measured 5 s wall clock against a 15 s upper bound.
- Phase 9: the canonical skill tree is `.claude/skills/`, the committed mirror `.agents/skills/` is generated from it by `scripts/gen_skills.py`, and that script is the only writer; `--check` and the `gen-skills-check` hook are the drift gate, so a hand edit is never the fix.
- Phase 9: skill prose is review-enforced — the drift check proves the mirror matches the canonical tree, not that a policy sentence is correct; text assertions pin only the load-bearing sentences, and the human review stays the gate.
- Phase 9: seven skills exist — `new-homework`, `hw-build` and `hw-flash` active, `hw-report`, `schematic`, `simulate` and `course-index` documented stubs promoted after first real use; each carries a dated changelog and lessons record.
- Phase 9: serial capture goes through `scripts/serial_capture.py` (PTY, raw bytes, no pipe) with a fail-closed credential scan that refuses before any file exists; one resolved USB serial port serves both upload and capture, and the monitor opens with `--dtr 0 --rts 0`.

- Phase 2: pins validated in practice — PlatformIO Core 6.2.0 + `platformio/espressif32` 8.0.0 build native, Arduino and ESP-IDF; 16 MB flash and octal PSRAM proven from `sdkconfig.json` and `esptool image-info`, never from `platformio.ini`.
- Phase 2: `platformio.shared.ini` is hand-authored; its generator and drift check remain Phase 5 (META-05). ADR-0007 records the `symlink://` + `library.json` decision.
- Phase 2: the entry point is one `.cpp` with `ARDUINO` / `ESP_PLATFORM` / host branches; library sources stay pure C behind `extern "C"` headers.
- Phase 2: ESP-IDF generated files are ignored by scoped `homeworks/*/` patterns plus the extended `no-generated-files` hook; authored `sdkconfig.defaults` stays visible.
- Roadmap: 11 small phases; policy precedes the first public push, metadata contract precedes its generators, and the shared-library dependency rule ships with the shared core.
- Research findings adopted: `lib_deps = <name>=symlink://...` over `lib_extra_dirs`; clang-format 120 documented as an ESP-IDF approximation; esp-clangd; Wokwi primary with Velxio fallback; CI simulation only after the Phase 7 spike; MkDocs Material 9.7.7 with Zensical-compatible config.
- Simulation spike (Phase 7) is the evidence gate: no CI simulation and no simulation-based report claim before ADR-0004.
- Documentation site is folded into Phase 5 (generated views) rather than a standalone single-requirement phase.
- Phase 3: the shared core is five independent libraries (`port`, `common`, `host`, `arduino`, `espidf`) with 21 public headers; only `common → port` is allowed downward and the checker is wired into pre-commit.
- Phase 3: `void *ctx` carries caller-owned state and there is no global mutable state in `port`; host fakes return the real contract types so signature drift is a compile error.
- Phase 3: I2C/SPI framework adapters are deferred (ADR-0008 D-08); the post-Phase-3 target-compile gate is owned by Phase 4 SC2 and Phase 8 SC2.
- Phase 3: the native gate is 73 Unity cases in 7 suites with 20 identical digests; `RUNS = 20` is a constant and every subprocess has a timeout.
- Phase 3: the architecture allowlist stays empty; any future entry must name a path, a known rule and a non-empty reason, and a stale entry fails the run.
- Phase 4: `schema/homework.schema.json` is the single metadata contract; `additionalProperties: false` at every level means a new field is a schema change, never an extra key.
- Phase 4: `scripts/new_homework` is the only scaffold path — idempotent, `--dry-run`, no overwrite, no symlink traversal; both templates build immediately.
- Phase 4: Python deps are pinned once (PyYAML 6.0.3, jsonschema 4.26.0) in the PEP 723 headers and the pre-commit hook; drift fails `test_metadata_deps`.
- Phase 4: paraphrase originality is not machine-verifiable; it is deferred to the first real `task.md` (UAT Test 1).
- 2026-10-25: ceremony trim — bureaucracy (policy-as-code, REUSE/SPDX, PR-template drift, tag gates, meta-tests, the blanket GSD-on-every-edit mandate, the mandatory ADR-per-decision and status-index upkeep) is removed; the GSD fast/quick/phase tiers and the atomic-commit culture stay, and the rule becomes proportional. Engineering tooling stays in the roadmap. The rule is frequency of execution, not appearance. See `.planning/notes/ceremony-vs-engineering-principle.md`.
- 2026-10-25: decision records are table-first — `docs/decisions/README.md` becomes the index and default record; the 11 existing ADRs stay as the archive; a new ADR file is created only when a decision needs real argumentation and is linked from the table.
- 2026-10-25: two tooling corrections accompany the proportional rule — `/gsd-fast` must stage only touched files instead of `git add -A`, and trivial changes no longer need a `STATE.md` quick-task row.
- 2026-10-25: Phase 4.2 runs homework 1.3 manually as a tracer and records a friction log; Phases 5–10 automate only what the log proves painful.
- [Phase 04.2]: 1_3 homework scaffolded only through scripts/new_homework; the dry run plans eight CREATE records and a re-run returns eight UNCHANGED records, so the verification accepts both states.
- [Phase 04.2]: D-08 amended: retrieved is 2026-10-23T00:00:00Z, because valid_iso8601 requires a timezone and the bare date is rejected once status leaves planned.
- [Phase 04.2]: The status flip, source.reference, four provenance values, and the simulation/report/assets blocks land in one commit; the TODO sentinels are legal only at status planned.
- [Phase 04.2]: homework.yaml forward-declares assets/diagram.json and report.md; the schema checks the path pattern, not disk presence, so the metadata validates before Waves 3 and 4 create those files.
- [Phase 04.2]: The pattern library lives at homeworks/1_3-police-flasher/lib/pattern with a manifest that omits frameworks and platforms, so both environments compile the same sources without a lib_deps entry or test_build_src.
- [Phase 04.2]: PORT_GPIO_INPUT is a pin mode, not a write level: an all-off frame calls set_mode(INPUT) and leaving that state calls set_mode(OUTPUT) before the next write, so the controller tracks applied/as_input/level per pin.
- [Phase 04.2]: The controller applies the current frame before reading the button, which makes a one-shot injected failure land on a pending write and lets a mode or speed change re-apply the new frame in the same tick.
- [Phase 04.2]: The frame schedule advances at most one frame per tick and resyncs step_started_ms to now only when a stall leaves it more than one hold behind, so a late loop neither drifts nor bursts.
- [Phase 04.2]: The Wokwi diagram is the canonical wiring source: GPIO4 through one 150 ohm resistor to node X, LED1 anode at X and cathode at GND, LED2 anode at 3V3 and cathode at X, the third LED on GPIO6, and the MODE button from GPIO7 to GND.
- [Phase 04.2]: merge_firmware.py stays project-local: espressif32@8.0.0 renamed tool-esptoolpy to tool-esptool and ships esptool 5 merge-bin with --flash-mode and --flash-size, so the published Wokwi script cannot run; promotion to scripts/pio/ waits for Phase 7/8.
- [Phase 04.2]: Simulation execution is deferred to Phase 7 with simulation.status pending: only wokwi-cli lint --offline is a verified result, and the repo-relative --diagram-file and --scenario command is recorded in the homework README.
- [Phase 04.2]: Report headings are numbered from title and metadata as 1: objective 2, theory 4, hardware 5, methodology 6, results 7, analysis 8, conclusions 9, references 10; plan 05 asserts the same literal text.
- [Phase 04.2]: Report metadata records implementation commit 6a60426; plan 05 must reuse that hash in every ledger row or refresh both records in one commit.
- [Phase 04.2]: BOM refs are the diagram part ids (esp, r1, led1, led2, r2, led3, btn1) so every physical part maps to a row without a second naming scheme.
- [Phase 04.2]: The reverse-voltage calculation excludes the all-off INPUT frame because node X floats; the off LED reverse voltage is not well-defined in that state.
- [Phase 04.2]: No value in report sections 1-6 is labelled measured; inputs are datasheet or calculated, and bench inputs are pending measurement until plan 05.
- [Phase 04.2]: The measurement ledger keeps implementation commit 6a60426 in the metadata table and in every row, because main.cpp and controller.c did not change in plan 05.
- [Phase 04.2]: No bench reading or serial log existed, so every bench row is not measured with the fixed reason bench equipment offline during automated tracer run; no measured value is inferred.
- [Phase 04.2]: The report ledger uses the five D-13 labels plus the single qualified measured (observed); a bare observed is rejected, and every measured cell would carry a user-reported: or serial-log: prefix.
- [Phase 04.2]: The homework workflow is one read-only job on ubuntu-24.04 with a 45-minute timeout, three action SHAs revalidated with git ls-remote, and only the two D-18 commands; metadata and architecture checks stay local until Phase 8.
- [Phase 04.2]: platformio.shared.ini gains no per-homework entry; the root README row and the workspace folder are the only manual integration edits, and the SC3 wording conflict is recorded in the friction log.
- [Phase 04.2]: Adding the workspace folder makes the PlatformIO IDE generate .gitignore and .vscode files inside the homework directory; they stay untracked and are recorded for the Phase 5 workspace generator.
- [Phase 04.2]: The friction-log synthesis owns every candidate: 11 rows name Phases 5-11 and 2 record `not built` with a reason, so no automation is left unowned and no one-off event became a recurring job.
- [Phase 04.2]: The phase gate runs both native suites (homework 38 cases, shared `tests/` 73 cases), the offline Wokwi lint, the metadata and architecture checkers, 81 Python tests, and `pre-commit run --all-files`; all eight commands exited 0.
- [Phase 04.2]: The Phase 4 real-tree JSON test asserted an empty array; the first real homework makes that stale, so it now asserts every real-tree record is `OK`, exists on disk, and is sorted by path.
- [Phase 04.2]: D-09 is recorded as a human checklist with its mechanical checks passing and the originality review pending; no completed user sign-off is claimed.
- [Phase 04.2]: Wokwi execution stays deferred to Phase 7 with `simulation.status: pending`; only `wokwi-cli lint --offline` is a verified simulation result.
- [Phase 04.2]: No `hw/1_3-police-flasher` tag exists; the tag belongs to Phase 11 and `scripts/tag_homework.sh` was not run.
- [Phase 04.2]: D-09 is closed — the repository owner performed the paraphrase comparison on 2026-10-25 and confirmed no verbatim sentence, no distinctive phrasing, and no original file committed. The result is recorded in 04-UAT.md, 04.2-SECURITY.md T-4.2-02, 04.2-VALIDATION.md (META-02), the PR body, and report appendix item 9 / T-13; this entry supersedes the earlier originality-review-pending note, which stays as the historical record.
- [Phase 04.2]: The "18"-entry count in 04.2-PR-BODY.md stays as submitted. 04.2-FRICTION-LOG.md is the canonical count and holds 19 entries since plan 08 added F-19. The tracked body is not edited after PR #10 opened (plan 11), and no live-description edit is made here because changing PR #10 is an outward-facing owner action confirmed separately; a correction would update the tracked file and PR #10 together in one owner-approved action.

### Pending Todos

- [2026-10-25] [docs] Expand homework README and add a proper SVG schematic — [todo file](.planning/todos/pending/2026-10-25-expand-homework-readme-and-add-a-proper-svg-schematic.md) — Needs TBD — candidate shape:.
- [2026-10-25] [tooling] Promote merge_firmware.py into a shared tool — [todo file](.planning/todos/pending/2026-10-25-promote-merge-firmware-py-into-a-shared-tool.md) — Needs TBD — candidate shape:.
- [2026-10-25] [tooling] Standardize pull request titles across homeworks — [todo file](.planning/todos/pending/2026-10-25-standardize-pull-request-titles-across-homeworks.md) — Needs TBD — candidate shape:.
- [2026-10-26] [tooling] Generate a root compile database so lib/ has working IntelliSense — [todo file](.planning/todos/pending/2026-10-26-add-lib-intellisense-compile-database.md)
- [2026-10-26] [tooling] Remove the generated documentation site — [todo file](.planning/todos/pending/2026-10-26-remove-docs-site.md)
- [2026-10-26] [process] Revisit Phase 8 scope before planning — [todo file](.planning/todos/pending/2026-10-26-revisit-phase-8-scope.md)
- [2026-10-26] [tooling] Place diagram.json beside wokwi.toml for simulator runs — [todo file](.planning/todos/pending/2026-10-27-place-diagram-json-beside-wokwi-toml-for-simulator-runs.md) — Needs TBD — candidate shape:.
- [unknown] [general] Trim governance ceremony (Phase 4.1) — [todo file](.planning/todos/pending/trim-ceremony.md)

### Blockers/Concerns

- Resolved: the course allows public solutions and does not require AI-assistance disclosure
  (user, 2026-10-23). No Phase 1 sign-off blocker remains.
- STM32 board models are unconfirmed; Renode/Wokwi STM32 paths are deferred to v2 until the
  course reaches STM32.
- Resolved in Phase 3: CR-01 (`partitions/default_16MB.csv` moved to a permanent location with
  existence tests) and WR-01..WR-04 (smoke-project test reads removed, ADR-0007 corrected,
  version single-sourced in `library.json`, `.gitignore` narrowed).
- Resolved in Phase 4: the Phase 3 target-compile carry-forward is discharged — both scaffolded
  templates build (Arduino 7.86 s, ESP-IDF 25.15 s) and the Arduino native suite is 2/2.
- **[Phase 8, resolved]** CI now builds changed projects, runs the stdlib suite, the pre-commit surface and the pre-push stage, and exposes one required `gate`; WR-13 is closed. PR #19 merged as `6285f5b`; the `main` ruleset requires `gate` with 0 approvals.
- **[Phase 8, observation]** `edited` in the `pull_request` types fires for a description edit as well as a retitle, so editing a PR body re-runs the whole pipeline (~2–3 min). Minor, unmeasured cost; a candidate for the backlog if it bites.
- **[Phase 4.1, deferred]** `scripts/tag_homework.sh` no longer fetches and no longer checks that `homeworks/<id>` exists at the tag target (CR-01/CR-02 in `04.1-REVIEW-DISPOSITION.md`). Operational precondition: run `git fetch origin` immediately before tagging, and confirm the merged PR and the directory by review. The tag is permanent.
- **[Phase 4.1, accepted]** The public-identity prohibition lost its only machine check (`test_license_hygiene.py`); it is now `[ENFORCED: review]` in `AGENTS.md`. The live GitHub ruleset is no longer machine-checked (AR-4.1-01).
- **[Phase 4.1, open warnings]** Review findings WR-02 (root-only `no-generated-files` pathspecs), WR-03 (metadata hook omits `platformio.shared.ini`), WR-05/06 and IN-01..03 are documentation/hook-accuracy items deferred to the next documentation pass.
- **[Phase 5, open findings]** 20 of 24 code-review findings remain `open` in `05-REVIEW-DISPOSITION.md` (0 critical; the two criticals and WR-02/WR-03 were fixed before merge). None breaks a phase must-have. The ones worth naming: WR-01 (backslash not escaped in `_escape_cell`), WR-04 (absolute board positionals misclassified under a differently-spelled root), WR-10 (a project with `platformio.ini` but no `[env:]` contributes no matrix entry), WR-13 (PR-time site build and Python suite absent from CI — Phase 8).
- **[Phase 5, resolved]** The deploy path is no longer unverified: PR #12 merged as `0384ed7`, the `docs` workflow's `build and deploy` job succeeded, and the live Pages site was checked page by page.
- **[Phase 6, open findings]** IN-01..IN-05 are info-level review observations recorded in `06-REVIEW-DISPOSITION.md`; none has a failing test or a reproducible defect against the phase goal. The CI layer of TOOL-03 is Phase 8 scope (TOOL-05, TOOL-06).
- **[Phase 6, environment note]** `pre-commit run --all-files` cannot run `end-of-file-fixer` against `.vscode/settings.json` under the command sandbox (`Operation not permitted`); the file is unchanged and the other 12 commit-stage hooks pass. Run the hook outside the sandbox when a full local gate is required.
- **[Phase 06.1, deferred]** `templates/**/src/*` have no compile database of their own, so both template entry points still show clangd errors. Recorded as a deferred follow-up in `06.1-UAT.md`; out of scope for the phase goal.
- **[Phase 7, open findings]** Five ADR wording warnings (WR-02..WR-06) and the info notes remain `open` in `07-REVIEW-DISPOSITION.md`; none breaks a phase must-have, and the CR-01 merge-failure defect was fixed in `4f053b2`.
- **[Phase 7, resolved in Phase 8]** The CI simulation run executed: run `40389939893` reported `outcome: passed` with a 5 s wall clock and a 15 s upper bound, and uploaded `serial.log`, `stdout.log` and `quota.json`.
- **[Phase 8, unobserved]** Two nightly clauses were not seen directly — the cron trigger (next at 03:17 UTC) and the cache restore inside a later pull-request build. The dispatch path, the queueing and the `refs/heads/main` cache entry were verified; record the first cron firing when it happens.

### Quick Tasks Completed

| # | Description | Date | Commit | Directory |
|---|-------------|------|--------|-----------|
| 261026-ky7 | Prune prose/doc-sync tests; replace the G-06-1 text guard with a behavioral clangd check | 2026-10-26 | 5fa6e53 | [261026-ky7-prune-prose-tests](./quick/261026-ky7-prune-prose-tests/) |
| 261025-349 | Fix the squash-merge commit body policy | 2026-10-25 | 3e6dd89 | [261025-349-fix-the-squash-merge-commit-body-policy-](./quick/261025-349-fix-the-squash-merge-commit-body-policy-/) |
| 261025-vih | Fix the six residual findings from the Phase 04.2 verification | 2026-10-25 | 50d82ff | [261025-vih-fix-the-six-residual-findings-from-the-p](./quick/261025-vih-fix-the-six-residual-findings-from-the-p/) |
| 3 | Ignore PlatformIO editor scaffolding and centralize IDE extensions | 2026-10-25 | 9b96a8f | — |
| 261026-x78 | Make the ESP-IDF template and new-homework skill pure C; remove golden fixtures | 2026-10-27 | 72d2b30 | [261026-x78-make-the-esp-idf-homework-template-and-t](./quick/261026-x78-make-the-esp-idf-homework-template-and-t/) |

### Roadmap Evolution

- Phase 4.1 inserted after Phase 4: Ceremony Trim (URGENT)
- Phase 4.2 inserted after Phase 4: Tracer Homework 1.3 (URGENT)
- Phase 06.1 inserted after Phase 6: Shared-library IntelliSense compile database (URGENT)

## Deferred Items

Items acknowledged and deferred at milestone close, most recent first:

| Category | Item | Status | Deferred At | Milestone |
|----------|------|--------|-------------|-----------|
| Target compile | Arduino/ESP-IDF adapter target builds (03-06.6) — smoke project retired by design | Closed in Phase 4 — both scaffolded templates build | 2026-10-24 | v1 |
| Human review | UAT Test 1 — paraphrase originality of the first real `task.md` | Resolved by Phase 4.2 (the tracer is the first real task) | 2026-10-25 | v1 |
| Governance | Return bureaucracy after stabilization — policy-as-code, REUSE/SPDX, multi-template PRs, ADR status index | Backlog 999.2 | 2026-10-25 | v1 |

## Session Continuity

Last session: 2026-10-27T13:37:00.277Z
Stopped at: Phase 10 context gathered
Resume file: .planning/phases/10-report-and-evidence-system/10-CONTEXT.md

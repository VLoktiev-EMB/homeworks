# Feature Research

**Domain:** Public embedded-engineering course/homework monorepo (30+ independent PlatformIO projects)
**Researched:** 2026-10-23
**Confidence:** MEDIUM

## Scope and Method

This is a feature-landscape study for a public, industry-standard embedded course
repository. It covers what excellent course/homework repositories, university lab
reports, and embedded engineering portfolios actually contain; what is merely
fashionable; and what should be deliberately excluded at 30+ homework scale.

Evidence base:

- Real course repositories: Purdue ECE 362 (`proton-labs`), Cornell ECE 4760 project
  pages, course CI/autograder examples.
- University lab-report and capstone guides (IIT, Rutgers, UW, UWI, WSU, ASME).
- Embedded repository standards (Photon Circus), Embedded Artistry README template,
  portfolio README guidance, OSHW documentation guidance.
- Official tool documentation for PlatformIO, Wokwi, Renode, MkDocs Material, GitHub
  Actions, Git LFS, gitleaks, MADR, and VS Code/clangd.
- Empirical studies of guided vs one-shot AI assistance in programming education.

**Complexity scale**

| Rating | Meaning |
|---|---|
| LOW | Mostly configuration or a single template/script; under roughly one focused day. |
| MEDIUM | Cross-cutting integration, several files, or a tool choice that needs validation; roughly 1-3 days. |
| HIGH | External service/hardware dependency, ongoing maintenance, or a workflow that changes how every homework is produced; more than 3 days or recurring cost. |

**Overall judgment.** Excellent repositories are not distinguished by the number of
tools they use. They are distinguished by a small set of artifacts that make each
homework independently buildable, testable, inspectable, and believable. At 30+
homeworks, the winning strategy is boring infrastructure plus rigorous artifacts, not
a bespoke engineering platform.

---

## Feature Landscape

### Table Stakes (Users Expect These)

Features a reader, grader, recruiter, or future maintainer assumes exist. Missing one
makes the repository feel like a pile of coursework rather than an engineering record.

| ID | Feature | Why Expected | Complexity | Depends On | Notes |
|---|---|---|---|---|---|
| TS-01 | **Per-homework project isolation** | Each assignment must build, flash, and be graded without touching another. Independent dependencies and board config are the whole point of the monorepo. | LOW | TS-02 | `homeworks/<id>/` with its own `platformio.ini`, `src/`, `test/`, `assets/`, `README.md`, `task.md`, `homework.yaml`. No root `src/`. |
| TS-02 | **Stable naming and identity** | `module_lesson-name` preserves course order and makes links, tags, and reports predictable. Renaming later breaks tags, docs, and references. | LOW | — | e.g. `1_3-police-flasher`. Record a permanent `id` in metadata; never reuse or silently rename after publication. |
| TS-03 | **Machine-readable homework manifest** | The index, docs site, workspace, CI matrix, and status views all need one source of truth. Prose alone cannot be validated. | MEDIUM | TS-02 | `homework.yaml` validated by JSON Schema: identity, board, framework, language, simulation, tests, report, assets, status, source, AI assistance, toolchain. |
| TS-04 | **Assignment provenance** | A public repo cannot republish internal course material. Readers need to know what was assigned versus what was paraphrased. | LOW | TS-03 | `task.md` = English paraphrase + source reference + retrieval date + attribution. Never commit the original internal PDF/slides. |
| TS-05 | **Academic report in Markdown** | The report is the primary deliverable; code alone is not an engineering artifact. A predictable structure makes review and comparison possible. | MEDIUM | TS-03, TS-04 | The 10-section structure from PROJECT.md: metadata, objective, assumptions, theory, hardware/wiring, methodology, results, analysis + industry notes, conclusions, IEEE references. |
| TS-06 | **Bill of materials** | A reader cannot reproduce or cost the build without parts, quantities, and sources. University hardware guides require it; portfolios use it as proof of design intent. | LOW | TS-05 | Columns: ref, part/value, qty, package, source/link, unit cost, notes/alternates. Link datasheets used in calculations. |
| TS-07 | **Pin map and wiring diagram** | "Which pin carries which signal" is the most common reproducibility failure in embedded coursework. A picture alone is not machine-checkable. | MEDIUM | TS-03, TS-05 | `assets/diagram.json` is the source of truth; validate with `wokwi-cli lint`; generate or hand-draw SVG/Fritzing for the report. Include a pin table: board pin, signal, peripheral, direction, voltage, notes. |
| TS-08 | **Electrical calculations with assumptions** | Engineering reports are judged on whether numbers are justified, not just present. Units, sources, and error treatment expose sloppy work. | MEDIUM | TS-05, TS-07 | Show formula, units, input provenance (datasheet/measured/estimated), result, tolerance/error, and the effect of assumptions. Include LED resistor, current, power, divider, timing, and pull-up calculations as applicable. |
| TS-09 | **Safety checklist** | Low voltage is not zero risk: batteries can source high current, reversed polarity and power-ground shorts destroy parts, and ESD damages ICs. Reviewers expect a pre-power checklist. | LOW | TS-07 | Check power-to-ground shorts before power-up, use current limiting/fuse, LED resistors, IC orientation, ESD precautions, no rewiring live circuits, battery polarity, and a "get a second pair of eyes" rule. |
| TS-10 | **Measured evidence with provenance** | Results must be distinguishable from expectations. A number without conditions, instrument, and origin is not evidence. | MEDIUM | TS-05 | Evidence table: ID, condition, instrument/method, expected, observed, verdict, artifact link. Label every claim as measured / simulated / datasheet / estimated / derived. |
| TS-11 | **Traceability matrix** | At 30+ reports, readers and future-you need to know which requirement or claim each artifact proves. Systems-engineering practice maps requirement -> verification -> result. | LOW | TS-05, TS-10 | Rows: requirement/claim ID, source, design/artifact link, verification method (Analysis/Demonstration/Inspection/Test), test or evidence ID, result, status. Keep it one page, not a compliance database. |
| TS-12 | **IEEE-style references** | University reports and engineering portfolios expect a consistent citation style; datasheets and app notes are primary sources. | LOW | TS-05 | Numbered IEEE format, consistent throughout, with datasheet revision/date and access dates for web sources. |
| TS-13 | **Unit tests for pure logic** | Code that claims to work should have at least a fast, deterministic test for the logic that does not need hardware. | MEDIUM | TS-01 | PlatformIO native environment + Unity (or GoogleTest). TDD for pure logic where practical; test parsing, state machines, timing math, protocol framing. Do not fake hardware behavior in host tests. |
| TS-14 | **Layered CI checks** | A public engineering repo is expected to prove it builds and validates on every change, not only on the author's machine. | MEDIUM | TS-03, TS-13, TS-16 | Pre-commit clang-format, markdownlint, yamllint, ruff, gitleaks; pre-push clang-tidy; CI full build/test/schema/docs/link checks. Build changed projects; run a full matrix nightly. |
| TS-15 | **Reproducible commands and pinned toolchain** | "It worked a year ago" requires more than source code: platform/framework versions, Python dependencies, and exact commands matter. | LOW-MEDIUM | TS-01, TS-14 | Pin `platform`, `framework`, and toolchain versions in `platformio.ini`; pin script dependencies; document one entry point (e.g. `scripts/ci.sh` or `pio run -d <dir>`); state OS caveats. Document an export path (e.g. `compiledb` or PlatformIO project export) for courses that mandate another IDE. |
| TS-16 | **Homework template and deterministic scaffolding** | At 2-3 homeworks per week, hand-building each project guarantees drift. A template makes the correct structure the easiest path. | MEDIUM | TS-01, TS-03 | `templates/homework/` with Arduino and ESP-IDF variants; `scripts/new_homework` validates inputs, refuses overwrite, supports `--dry-run`, and is idempotent. Avoid timestamps/random ordering in generated files. |
| TS-17 | **Root index and per-homework README** | Readers need one entry point; each homework needs a self-contained landing page. This is the single most common strength of good course repos. | LOW | TS-03, TS-16 | Root README generated from metadata: ID, title, board, concepts, status, report/evidence links. Per-homework README is the academic report, not a duplicate stub. |
| TS-18 | **License and copyright hygiene** | A public repo needs explicit reuse terms, and course material may not be yours to license. | LOW | — | MIT for original code; a `NOTICE`/attribution section for third-party assets, datasheets, and paraphrased assignments. Do not apply MIT to material you do not own. |
| TS-19 | **Secret and PII hygiene** | Public history is forever. Tokens, Wi-Fi credentials, student names, and IDs are common accidental leaks in coursework. | LOW | TS-18 | gitleaks in pre-commit and full-history CI; `.env.example` only; no student identifiers; no internal course PDFs; review images/screenshots for names and network credentials. |
| TS-20 | **Asset and Git LFS policy** | Media makes reports credible, but binary bloat makes the repo painful to clone and can break GitHub Pages. | LOW | TS-18 | Commit `.gitattributes`; track only genuinely large assets with LFS; enforce a size guard in CI; link videos instead of committing them. GitHub blocks files over 100 MiB and warns at 50 MiB; LFS is not supported for GitHub Pages. |
| TS-21 | **Onboarding for a VS Code beginner** | The primary user is new to VS Code. A repo that assumes clangd/PlatformIO fluency will fail its own author. | MEDIUM | TS-15, TS-17, TS-26 | Install extensions (PlatformIO IDE, clangd, Markdown lint), open the workspace, build, run native tests, simulate, flash, and troubleshoot. Include a no-hardware path and a "first 15 minutes" checklist. |
| TS-22 | **Shared-library consumption** | 30+ projects should not copy the same ring buffer, state machine, or port layer. Reuse is a core reason for the monorepo. | MEDIUM-HIGH | TS-01 | `lib/common`, `lib/port`, `lib/arduino`, `lib/espidf`, `lib/host`, plus adapters. Each library needs a manifest, README, and host tests. **Caveat:** PROJECT.md specifies `lib_extra_dirs`, but PlatformIO documents it as deprecated since 6.0 in favor of `lib_deps = Name=symlink://../lib/Name` with a `library.json` manifest. Validate before implementation. |
| TS-23 | **Honest status and limitations** | Recruiters and graders trust a repo that states what is verified, on which board, and what is not. Hiding gaps is worse than having them. | LOW | TS-03, TS-05 | Status (`planned`/`in-progress`/`complete`/`verified`), "verified on" board/toolchain, known issues, unsupported configurations, and next steps. |
| TS-24 | **Auditable Git workflow** | Protected `main`, branches, PRs, conventional commits, squash merge, and `hw/<id>` tags make the history readable and each homework a clear release. | LOW | TS-14 | Three PR templates (homework/infra/docs) with type-specific evidence checklists. Avoid a bloated universal template. |
| TS-25 | **AI-assistance disclosure** | In 2026, course work and public portfolios increasingly require disclosure of generated/assisted content. Cornell ECE 4760 reports already include an AI-use statement. | LOW | TS-05 | State tools, scope (code/report/diagram), what was reviewed, what was rejected, and who verified behavior. Keep it factual, not defensive. |
| TS-26 | **Local simulation path** | Simulation without hardware is a core project constraint; every homework should be runnable before a board is available. | MEDIUM | TS-07 | Wokwi VS Code or self-hosted Velxio; `diagram.json` + `wokwi.toml`; documented launch command and expected serial output. CI simulation is a separate differentiator. |

### Differentiators (Competitive Advantage)

Features that are uncommon in course repositories and materially raise the quality of
the portfolio. None are required for a first pilot, but they are where this repo can
stand out.

| ID | Feature | Value Proposition | Complexity | Depends On | Notes |
|---|---|---|---|---|---|
| DF-01 | **Simulation evidence in CI** | Proves behavior without hardware and catches regressions in interaction logic. Very few course repos do this. | HIGH | TS-07, TS-10, TS-14 | Wokwi CI action with `wokwi.toml`, `diagram.json`, scenario YAML (`wait-serial`, `set-control`), serial log artifacts. Selective per changed project; nightly subset. Watch Wokwi simulation-minute quotas and ESP-IDF/partition firmware merge. |
| DF-02 | **Tiered hardware-in-the-loop (HIL)** | Real-silicon evidence for timing, analog, power, and bus behavior that simulation cannot establish. | HIGH | TS-10, TS-13, TS-14 | Self-hosted runner + pytest fixture: flash, reset, open serial, assert output. Reserve for physics-dependent tests; schedule nightly/manual. Do not make HIL mandatory for every homework. |
| DF-03 | **Generated multi-root VS Code workspace** | One workspace with repo/docs/lib/scripts and every homework, generated from metadata, eliminates manual folder drift. | MEDIUM | TS-03, TS-17 | Commit the `.code-workspace` and add a `--check` mode. **Caveat:** clangd's multi-root support is still problematic (cross-root index bleed, `.clang-format` resolution); prototype before promising a seamless experience. |
| DF-04 | **Metadata-driven MkDocs Material site** | A searchable, taggable course catalog with reports, BOMs, pin maps, and status is a portfolio asset and a navigation aid. | MEDIUM | TS-03, TS-17 | Generate pages from `homework.yaml`; use tags/search/status; build in CI and deploy to Pages. Prefer Material's `projects` plugin or a single docs tree; `awesome-pages` + monorepo plugin is a known incompatibility. Do not LFS assets that Pages must serve. |
| DF-05 | **Metadata-driven CI matrix with shared-lib fanout** | Building only changed homeworks keeps PR feedback fast; a nightly full matrix catches drift. Shared-library changes must fan out to dependents. | MEDIUM | TS-03, TS-14, TS-22 | `dorny/paths-filter` -> JSON matrix -> `pio run -d`. Explicitly include `lib/**` in filters for all dependent projects; guard empty matrices. |
| DF-06 | **Guided vs one-shot learning modes** | The repository can teach, not just store. Guided mode scaffolds understanding; one-shot mode is for known material. | HIGH | TS-16, DF-07 | Guided: explanation -> code -> run -> questions at block granularity, adaptive question bank, stuck detection, deepen explanations. One-shot: still checkpoint after intake, code, and report. Both: guardrails before flash/commit/PR, explicit handling of spec-vs-best-practice conflicts and ambiguity, max two automatic build fixes, then explain and escalate. |
| DF-07 | **Versioned project-local agent skills** | Encodes repeatable workflows (`new-homework`, `hw-build`, `hw-report`, `schematic`, `simulate`, `course-index`) so Claude and other agents behave consistently. | MEDIUM-HIGH | TS-16, TS-24 | `SKILL.md` with clear triggering descriptions, allowed tools, references, changelog, and lessons learned updated after each use. Cover `new-homework`, `hw-build`, `hw-flash`, `hw-report`, `schematic`, `simulate`, `course-index`. Keep `AGENTS.md` canonical and short; skills are procedures, not always-on context. Promote thin stubs only after real use. |
| DF-08 | **ADR log plus assumption register** | Infrastructure decisions and homework assumptions are different scopes; both need traceability. | LOW-MEDIUM | TS-05, TS-23 | `docs/decisions/NNNN-title.md` using MADR: context, options, decision, consequences, assumptions. Homework assumptions live in the report with "impact if wrong" and "how validated." Link, do not duplicate. |
| DF-09 | **Per-homework release and artifact bundle** | `hw/<id>` tag plus release notes and a bundle (source, report, BOM CSV, schematic, simulation log) makes each homework citable and archivable. | MEDIUM | TS-24, DF-01 | Attach generated artifacts to the GitHub Release; do not commit build outputs. Include firmware hash and toolchain versions. |
| DF-10 | **Portfolio-quality project page** | Leads with the problem and proof, not the stack: demo, results table, limitations, and one contested decision. | LOW-MEDIUM | TS-05, TS-10, DF-04 | Demo GIF/video link, schematic thumbnail, measured results, "what I'd do next." Avoid badge walls and scaffold boilerplate. |
| DF-11 | **Self-audit / design-review rubric** | A pre-PR checklist mapped to the report and traceability matrix catches missing evidence before a reviewer does. | LOW | TS-05, TS-11 | Report complete, BOM/pin map current, calculations justified, safety checked, tests pass, evidence labeled, references valid, limitations stated. |
| DF-12 | **Course concept map** | Maps module/lesson -> concepts -> homework, exposing gaps and preventing duplicate projects. | LOW | TS-03 | A small generated table or Mermaid graph. Useful for a course whose syllabus is revealed progressively. |
| DF-13 | **Fault-injection and negative-path tests** | Proves robustness: button bounce, sensor failure, invalid input, brownout, bus timeout. | MEDIUM | DF-01 | Simulation scenarios can force sensor values and timing; HIL can power-cycle. Add only after the happy-path evidence is stable. |
| DF-14 | **Optional dev container / one-command setup** | Makes the repo reproducible for a reader on a clean machine. | MEDIUM | TS-15, TS-21 | Defer until the local workflow is stable; a dev container that hides PlatformIO/clangd problems is worse than a good onboarding guide. |

### Anti-Features (Deliberately Not Built)

Features that sound impressive or useful but create disproportionate cost, hide the
engineering, or undermine the course's purpose.

| ID | Anti-Feature | Why Requested | Why Problematic | Alternative |
|---|---|---|---|---|
| AF-01 | **Universal hardware abstraction layer (HAL) over Arduino and ESP-IDF** | Reuse and portability across boards. | It hides the frameworks the course teaches, becomes a shadow framework, leaks on every non-trivial peripheral, and multiplies maintenance across 30+ projects. | Thin `core` + `port` + adapters. Abstract the bus (I2C/SPI), not the whole driver. Duplicate small glue code when necessary. |
| AF-02 | **Pre-scaffolding all 30+ homework directories** | Consistency and the feeling of being prepared. | The syllabus is revealed progressively; most scaffolds will be stale, wrong, or empty. It creates noise, false status, and a large review surface. | One template plus a deterministic `new-homework` script. Create directories when assignments arrive. |
| AF-03 | **DOCX/PDF report pipeline as the source of truth** | Course submission formats and polished appearance. | Dual sources drift, binary diffs are unreviewable, merge conflicts are painful, and the toolchain becomes a second project. | Markdown is the source. Generate PDF ad hoc only if a course requires it; never commit the generated PDF as canonical. |
| AF-04 | **Grade tracking, autograder, or rubric engine** | Course management and automated assessment. | It introduces student PII, assessment policy, and a second product. The repo is a record of work, not a gradebook. | Record evidence, status, and self-assessment. Keep grading external. |
| AF-05 | **Committing videos and large binaries** | Demo proof and "complete" evidence. | Bloats clones, hits GitHub/LFS limits, slows CI, and LFS assets are not served by GitHub Pages. | Link videos (YouTube/unlisted) and keep only small stills/GIFs. Use LFS narrowly for PDFs/CAD/scope captures when justified. |
| AF-06 | **Committing internal course materials or student PII** | Completeness and traceability to the assignment. | Copyright infringement, DMCA exposure, privacy/FERPA risk, and academic-integrity problems. | English paraphrase + public source + attribution. No names, student IDs, or internal PDFs/slides. |
| AF-07 | **MISRA C compliance or a full static-analysis gate** | "Industry standard" quality. | High noise and false positives, expensive tooling, slows every project, and distracts from the course's actual learning goals. | ESP-IDF style + clang-format + selected clang-tidy checks (bugprone, cert, performance, portability). |
| AF-08 | **Per-homework Docker/Nix/Bazel/Nx/Turborepo orchestration** | Reproducibility and monorepo sophistication. | Duplicates metadata, slows CI, adds a learning curve, and solves a dependency graph the repo does not have. PlatformIO already isolates projects. | PlatformIO + pinned versions + one POSIX `scripts/ci.sh`. Add a dev container only if a real onboarding failure demands it. |
| AF-09 | **Custom static site generator or docs platform** | A tailored index and control over presentation. | Reinvents MkDocs, creates a maintenance burden, and breaks links/search/SEO. | MkDocs Material generated from `homework.yaml`; contribute a plugin only if a documented gap blocks the site. |
| AF-10 | **Mandatory HIL for every homework** | "Real hardware" evidence. | Hardware is scarce, rigs are flaky, CI is slow, and many assignments teach logic that host tests already cover. | Tiered testing: build always, unit tests for pure logic, simulation where supported, HIL only where physics/timing matters. |
| AF-11 | **Presenting simulation as hardware evidence** | No hardware available; simulation is convenient. | Simulation can produce false greens and may accept configurations real silicon rejects. It misleads reviewers and future-you. | Label every result as simulated/measured/datasheet/estimated. State model limitations. Add HIL or bench measurement when the claim depends on physics. |
| AF-12 | **Automatic pinout/diagram generation for every board** | Portability and less manual drawing. | Board profiles drift, vendor pinouts are inconsistent, and a wrong generated diagram is worse than a linked official one. | Maintain profiles only for owned boards; generate pinouts where reliable; otherwise link the official pinout and validate `diagram.json`. |
| AF-13 | **One giant PlatformIO project with a shared `src/`** | Maximum code reuse and one build. | Couples every homework, creates dependency/board conflicts, and makes independent grading and flashing impossible. | One project per homework plus shared libraries consumed explicitly. |
| AF-14 | **Bespoke tooling or templates per homework** | Each assignment has unique needs. | 30x maintenance, inconsistent structure, and reviewers cannot compare work. | One template with documented exceptions; put assignment-specific detail in `homework.yaml` and the report, not in forked tooling. |
| AF-15 | **Metrics dashboards, badge walls, coverage theater** | Looks professional and data-driven. | Vanity metrics, brittle badges, and 100% coverage targets encourage meaningless tests. They distract from evidence. | One CI badge, one status table, and a traceability/evidence table that says what was actually verified. |
| AF-16 | **Fully autonomous agent mode with no checkpoints** | Speed and "one-shot" convenience. | Silent wrong assumptions, unsafe flashing, accidental commits, and academic-integrity risk. Research on AI-assisted learning shows one-shot delegation improves completion but not understanding. | Checkpoints after intake, code, and report; explicit approval before flash/commit/PR; max two automatic fixes, then explain and escalate. |
| AF-17 | **Hand-maintained index, workspace, and docs navigation** | Simple to start; no generator to write. | Guaranteed drift at 30+; forgotten entries, stale links, and a workspace that no longer matches the repo. | Generate from metadata and run a `--check` drift test in CI. |
| AF-18 | **100% test coverage as a goal** | Quality signal. | Encourages tests of hardware glue and trivial getters; slows delivery; coverage is not evidence of correctness. | Test pure logic and failure paths; use simulation/HIL evidence for hardware behavior. Report coverage only if it informs a decision. |

---

## Feature Dependencies

```
TS-01 isolation ──requires──> TS-02 naming
TS-03 manifest ──requires──> TS-02 naming
TS-04 provenance ──requires──> TS-03
TS-05 report ──requires──> TS-03, TS-04
TS-06 BOM ──requires──> TS-05
TS-07 wiring/pin map ──requires──> TS-03, TS-05
TS-08 calculations ──requires──> TS-05, TS-07
TS-09 safety ──requires──> TS-07
TS-10 evidence ──requires──> TS-05
TS-11 traceability ──requires──> TS-05, TS-10
TS-12 references ──requires──> TS-05
TS-13 unit tests ──requires──> TS-01
TS-14 CI ──requires──> TS-03, TS-13, TS-16
TS-15 reproducible commands ──requires──> TS-01, TS-14
TS-16 template/scaffolding ──requires──> TS-01, TS-03
TS-17 index/README ──requires──> TS-03, TS-16
TS-21 onboarding ──requires──> TS-15, TS-17, TS-26
TS-22 shared libraries ──requires──> TS-01
TS-23 status/limitations ──requires──> TS-03, TS-05
TS-24 Git workflow ──requires──> TS-14
TS-25 AI disclosure ──requires──> TS-05
TS-26 local simulation ──requires──> TS-07

DF-01 simulation CI ──requires──> TS-07, TS-10, TS-14, TS-26
DF-02 HIL ──requires──> TS-10, TS-13, TS-14
DF-03 workspace generation ──requires──> TS-03, TS-17
DF-04 MkDocs site ──requires──> TS-03, TS-17
DF-05 selective CI matrix ──requires──> TS-03, TS-14, TS-22
DF-06 guided/one-shot modes ──requires──> TS-16, DF-07
DF-07 agent skills ──requires──> TS-16, TS-24
DF-08 ADR/assumptions ──requires──> TS-05, TS-23
DF-09 release bundle ──requires──> TS-24, DF-01
DF-10 portfolio page ──requires──> TS-05, TS-10, DF-04
DF-11 self-audit rubric ──requires──> TS-05, TS-11
DF-12 concept map ──requires──> TS-03
DF-13 fault injection ──requires──> DF-01
DF-14 dev container ──requires──> TS-15, TS-21

Conflicts / tensions:
AF-01 universal HAL ──conflicts──> TS-22 shared libraries (thin port only)
AF-10 mandatory HIL ──conflicts──> DF-02 tiered HIL
AF-11 simulation-as-hardware ──conflicts──> TS-10 provenance labels
AF-14 per-homework tooling ──conflicts──> TS-16 template/scaffolding
AF-17 hand-maintained navigation ──conflicts──> DF-03/DF-04 generation
```

### Dependency Notes

- **TS-03 is the keystone.** Manifest validation must exist before index generation,
  workspace generation, MkDocs, or a CI matrix. Building those first creates four
  consumers of an unstable contract.
- **TS-05 is the report contract.** BOM, pin map, calculations, safety, evidence,
  traceability, references, and AI disclosure are sections/artifacts of the report,
  not independent documents that can drift.
- **TS-13 must precede TS-14.** CI should run tests that already exist locally; do not
  create a CI-only test path.
- **DF-06 requires DF-07.** Guided mode is a skill behavior; without a stable
  `new-homework` skill and template, guided mode becomes a prompt that cannot be
  reproduced.
- **DF-01 requires TS-10.** Simulation output is not evidence until it is captured,
  labeled, and linked from the report.
- **DF-05 must account for TS-22.** Path filters that ignore `lib/**` will silently
  skip dependent homeworks after a shared-library change.
- **DF-04 and DF-03 should share the same metadata reader.** Two generators reading
  the manifest differently is a drift bug waiting to happen.

---

## MVP Definition

### Launch With (v1)

The pilot homework (1.3, Police Flasher), including its optional extensions (third LED, variable speed, complex pattern, single-GPIO operation), must validate the entire artifact chain. Table
stakes are all launch criteria, but "launch" means a minimum credible depth, not a
finished platform.

- [ ] **TS-01, TS-02, TS-03, TS-04** — directory, identity, manifest, provenance.
- [ ] **TS-05 through TS-12** — the complete report package: 10 sections, BOM, pin
      map/wiring, calculations, safety, evidence, traceability, IEEE references.
- [ ] **TS-13, TS-14, TS-15** — native unit tests, CI build/lint/schema checks, one
      documented command path.
- [ ] **TS-16, TS-17, TS-23** — template/scaffolding, generated index + report page,
      honest status.
- [ ] **TS-18, TS-19, TS-20** — license, secret/PII hygiene, asset policy.
- [ ] **TS-21** — a short VS Code onboarding guide, including a no-hardware path.
- [ ] **TS-26** — local simulation path for the pilot, with a documented launch command.
- [ ] **TS-22 (minimal)** — `lib/common` and `lib/port` with one real consumer in the
      pilot; validate the consumption mechanism before scaling.
- [ ] **TS-24, TS-25** — branch/PR/tag workflow and AI-assistance disclosure.

**Why this is the minimum:** each item is either required by PROJECT.md, expected by a
university/engineering reader, or a precondition for trusting the pilot. None of the
differentiators are required to prove the concept.

### Add After Validation (v1.x)

Add these once the pilot proves the template, report, and CI are stable.

- [ ] **DF-07** — promote `new-homework` and `hw-build` from stubs; keep others thin
      until used. Trigger: pilot completes guided mode twice.
- [ ] **DF-06** — full adaptive question bank and stuck detection. Trigger: the pilot
      exposes which questions actually help.
- [ ] **DF-01** — simulation in CI after the Wokwi/Velxio/Fritzing spike and ADR.
      Trigger: a simulation scenario that reliably catches a real regression.
- [ ] **DF-03, DF-04, DF-05** — workspace, MkDocs, and selective CI once 3+ homeworks
      exist and the manifest has stabilized. Trigger: manual index/workspace edits
      become error-prone.
- [ ] **DF-08, DF-09, DF-10, DF-11** — ADR log, release bundle, portfolio page,
      self-audit rubric. Trigger: first public release of a homework.
- [ ] **DF-12** — concept map once the course reveals enough modules to be useful.

### Future Consideration (v2+)

- [ ] **DF-02** — HIL with a self-hosted runner. Trigger: a claim that simulation
      cannot establish (timing, analog, power, bus behavior) and hardware is available.
- [ ] **DF-13** — fault injection and negative-path scenarios. Trigger: happy-path
      simulation is stable.
- [ ] **DF-14** — dev container. Trigger: a second machine or a contributor cannot
      reproduce the setup with the onboarding guide.
- [ ] Additional boards/frameworks (STM32, ESP-IDF deep dive) only when the course
      actually requires them.

---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---|---|---|---|
| Per-homework isolation + naming (TS-01/02) | HIGH | LOW | P1 |
| Manifest + schema (TS-03) | HIGH | MEDIUM | P1 |
| Report package (TS-05-12) | HIGH | MEDIUM | P1 |
| Unit tests + CI (TS-13/14) | HIGH | MEDIUM | P1 |
| Template + scaffolding (TS-16) | HIGH | MEDIUM | P1 |
| Index + onboarding (TS-17/21) | HIGH | LOW-MEDIUM | P1 |
| License/secret/asset hygiene (TS-18/19/20) | HIGH | LOW | P1 |
| Shared libraries (TS-22) | HIGH | MEDIUM-HIGH | P1 (minimal) |
| Local simulation (TS-26) | HIGH | MEDIUM | P1 |
| Simulation in CI (DF-01) | HIGH | HIGH | P2 |
| MkDocs + workspace generation (DF-03/04) | MEDIUM-HIGH | MEDIUM | P2 |
| Guided/one-shot modes + skills (DF-06/07) | HIGH | HIGH | P2 |
| ADR + assumptions (DF-08) | MEDIUM | LOW | P2 |
| Release bundle + portfolio page (DF-09/10) | MEDIUM | MEDIUM | P2 |
| HIL (DF-02) | MEDIUM | HIGH | P3 |
| Fault injection (DF-13) | LOW-MEDIUM | MEDIUM | P3 |
| Dev container (DF-14) | LOW-MEDIUM | MEDIUM | P3 |

**Priority key:** P1 = launch/pilot; P2 = add after validation; P3 = only when a
specific trigger justifies it.

---

## Competitor Feature Analysis

| Feature | Purdue ECE 362 `proton-labs` | Cornell ECE 4760 project pages | Photon Circus / Embedded Artistry standards | Typical student repo | Our Approach |
|---|---|---|---|---|---|
| Per-assignment isolation | One folder per lab | One project/repo per team | One repo per component | One repo per assignment or one dump | One PlatformIO project per homework, shared libs via explicit manifests |
| Root index | Yes, README index only | Project list by term | README contract | Usually absent or stale | Generated from `homework.yaml` plus MkDocs |
| Report structure | Lab manual, not a report | Full design report with appendices | README as contract | Thin README | 10-section academic report in Markdown |
| BOM / pin map | Wiring instructions; no BOM | BOM tables, pin mapping | Documented interfaces | Rare | BOM, pin map, and `diagram.json` as source of truth |
| Schematics | Images in lab docs | Schematics/PCB renders | Hardware interface docs | Photos only | `diagram.json` + SVG/Fritzing illustrations |
| Test evidence | Autotest + TA checkoff | Informal results; sometimes limited | Verification commands and scope | Usually none | Evidence table with provenance labels + traceability matrix |
| CI | Course infrastructure, not public | Rare | Local CI authoritative | Rare | Layered CI + changed-project matrix |
| Simulation | Not in repo | Not in repo | Not prescribed | Rare | Wokwi/Renode after spike; labeled as simulated |
| HIL | Lab checkoff | Lab bench | Optional, risk-based | No | Tiered, self-hosted, only where physics matters |
| Reproducibility | Template + course tooling | Code link, sometimes incomplete | Pinned toolchain + exact commands | Weak | Pinned PlatformIO versions + one command path |
| Licensing | CC BY-NC-SA 4.0 | Varies by project | MIT default | Often missing | MIT for original work + NOTICE/attribution |
| AI disclosure | Prohibited in some labs | Explicit AI-use section | Not prescribed | Rare | Per-homework disclosure |

**Takeaway:** Purdue excels at per-lab isolation and a self-contained manual; Cornell
excels at report completeness, BOM/pin mapping, and disclosure; Photon Circus excels
at repository contracts and honest verification. The proposed repo combines those
strengths and adds machine-readable metadata, CI, and simulation evidence, which none
of the exemplars combine.

---

## Roadmap Implications

Suggested phase structure based on the dependency graph:

1. **Contract and skeleton** — TS-01/02/03/04, TS-16, TS-17 (minimal), TS-18/19/20,
   TS-23, TS-24. Establish the manifest schema and template before writing generators.
2. **Pilot vertical slice (homework 1.3)** — TS-05 through TS-12, TS-13/14/15, TS-21,
   TS-22 (minimal), TS-25, TS-26. Prove the full artifact chain on one homework.
3. **Publication automation** — DF-03, DF-04, DF-05, DF-09, DF-10. Add generators only
   after the manifest has survived the pilot. Include `--check` drift tests.
4. **Simulation evidence** — simulation spike, ADR (DF-08), DF-01, then DF-13. Start
   CI simulation only after the local scenario is stable and its evidence is labeled.
5. **Guided workflow** — DF-07 first (stable skills), then DF-06 (adaptive modes),
   then DF-11 (self-audit). The pilot's guided run generates the question bank.
6. **Scale and hardening** — DF-02 (HIL), DF-12 (concept map), DF-14 (dev container),
   periodic audits of report/evidence quality across all homeworks.

**Ordering rationale.** The manifest and report contract unlock every automation; the
pilot unlocks real questions and evidence; simulation/HIL unlock stronger claims; the
guided workflow unlocks teaching. Reversing this order produces generators with no
stable input, CI with nothing meaningful to run, or skills that encode guesses.

**Research flags for phases:**

- **Phase 1:** PlatformIO's `lib_extra_dirs` deprecation must be resolved before
  committing to the shared-library mechanism.
- **Phase 1/2:** Multi-root VS Code + clangd behavior must be prototyped; do not
  promise a seamless workspace until it works on the actual toolchain.
- **Phase 3:** MkDocs monorepo plugin choice (`projects` vs. single docs tree) and
  GitHub Pages/LFS interaction need a small spike.
- **Phase 4:** Wokwi CI quotas, token handling, and ESP-IDF firmware merge need a
  costed spike; Velxio self-hosting is the fallback.
- **Phase 6:** HIL runner security, hardware availability, and flaky-test quarantine
  need a dedicated design.

---

## Research Flags and Open Questions

| Question | Why It Matters | Current Evidence | Recommended Action |
|---|---|---|---|
| Is `lib_extra_dirs` still acceptable? | PROJECT.md specifies it; official docs mark it deprecated since PlatformIO 6.0. | PlatformIO docs recommend `lib_deps = Name=symlink://../lib/Name` with a `library.json`; community reports confirm `lib_extra_dirs` works but warns. | Validate the replacement in Phase 1; update PROJECT.md/ADR if confirmed. |
| Does the multi-root workspace actually work with clangd? | The repo's onboarding and per-project IntelliSense depend on it. | clangd issue #38 (multi-root) is long-running; cross-root index bleed and `.clang-format` resolution are known. | Prototype with 3 homeworks + shared lib; if unstable, use one folder per project or per-project `--compile-commands-dir`. |
| What is the real Wokwi CI cost/quota? | 30+ homeworks × PRs can exceed free simulation minutes. | Wokwi documents tiered quotas; free tier is commonly cited as 50 minutes per rolling 30 days. | Cost a realistic PR/nightly matrix during the simulation spike; default to changed-project + nightly subset. |
| Which docs topology? | `awesome-pages` + monorepo plugin is a known incompatibility. | Material's `projects` plugin supports multi-project builds; a single generated docs tree is simpler. | Spike both with 3 homeworks; choose the one that keeps one nav source. |
| Can the assignment be paraphrased publicly? | Copyright and academic-integrity risk. | University guides require consent/attribution for public posting; course materials may be institution-owned. | Confirm course policy; publish only the English paraphrase + public source; keep originals out of Git. |
| Is HIL worth it for one student? | Hardware scarcity and flakiness can outweigh evidence value. | Test-pyramid guidance reserves HIL for physics-dependent claims; pytest + serial is a proven pattern. | Defer to v2; start with a single manual HIL checklist before building a runner. |
| What AI-use policy applies? | Disclosure is increasingly required and affects the guided workflow. | Cornell reports include AI-use sections; course policies vary. | Confirm the course rule; make disclosure a report section and keep a per-homework record. |

---

## Confidence Assessment

| Area | Confidence | Notes |
|---|---|---|
| Table stakes | MEDIUM | Cross-checked across university guides, real course repos, and repository standards. The exact mix is a synthesis, not a single source. |
| Differentiators | MEDIUM | Tool capabilities are documented (Wokwi, Renode, MkDocs, PlatformIO), but value for a 30+ course repo is judgment. |
| Anti-features | MEDIUM | Grounded in project constraints, monorepo experience reports, and test-pyramid guidance; some are reasoned tradeoffs rather than measured outcomes. |
| Feature dependencies | MEDIUM | Mostly logical and confirmed by tool docs; the clangd and PlatformIO deprecation caveats are the main uncertainties. |
| Platform specifics | MEDIUM | Official docs were consulted, but versions and quotas change; validate during the spike. |

---

## Gaps to Address

- No single public exemplar combines all proposed features. The landscape is a
  synthesis of course repos, lab-report guides, repository standards, and tool docs.
- Requirements traceability matrices are rare in university lab reports; the proposed
  matrix is adapted from systems-engineering practice (FAA VRTM, ISO/IEC/IEEE 29148)
  and should be kept lightweight.
- Exact Wokwi/Velxio quotas, pricing, and ESP-IDF simulation limitations need a costed
  spike; published numbers may change.
- HIL cost/benefit for a single-student course is unproven; treat it as an optional
  tier, not a launch requirement.
- Institution-specific copyright and AI-use policies were not available; confirm
  before publishing paraphrased assignments.
- Long-term maintenance of 30+ MkDocs pages and generated workspaces is a real cost;
  measure it after 5-10 homeworks before expanding the site.
- "Excellent" is partly a judgment about audience (grader, recruiter, future
  maintainer). The priorities above optimize for reproducibility and evidence, which
  serve all three.

---

## Sources

**Course repositories and portfolio practice**

- Purdue ECE 362 `proton-labs` — per-lab structure, root index, shared template: https://github.com/ece362-purdue/proton-labs (MEDIUM)
- Cornell ECE 4760 final project example — report sections, BOM, pin map, schematics, AI disclosure: https://ece4760.github.io/Projects/Fall2025/rwl228_iv74/index.html (MEDIUM)
- Photon Circus repository standards — README contract, lifecycle, local CI, verification scope: https://github.com/photon-circus/.github/blob/main/REPOSITORY_STANDARDS.md (MEDIUM)
- Embedded Artistry README template — status, dependencies, build/test, verified vs. unverified: https://embeddedartistry.com/blog/2017/11/30/embedded-artistry-readme-template/ (MEDIUM)
- Portfolio README guidance — proof above the fold, tested setup, contested decision, honest limits: https://www.skillveris.com/blog/project-readme-as-portfolio-proof (MEDIUM)
- Open-Make hardware documentation guide — README as entry door, validation, licensing: https://open-make.github.io/Hardware-template-guide/content/106_readme_main_conc.html (MEDIUM)
- Embedded portfolio example with "evidence to publish" and status labels: https://github.com/sirVnK/embedded-software-portfolio (LOW)

**University report and engineering practice**

- IIT ECE laboratory report guide — structure, apparatus, calculations, references: https://www.ece.iit.edu/~abet/documents/ECE_Guide_to_Laboratory_Report_Writing_Fall_2020.pdf (MEDIUM)
- Rutgers ECE capstone report guidelines — IEEE references, cost/sustainability, V&V: https://ece.rutgers.edu/sites/default/files/2024-03/Capstone-Project-Report-Guidelines.pdf (MEDIUM)
- UW ECE R&D project report guide — BOM, schematics, requirements verification: https://peden.ece.uw.edu/student-info/wp-content/uploads/sites/8/2022/05/RnDProjectReportGuide_Rev3.pdf (MEDIUM)
- UWI ECNG 3020 writing manual — BOM template and component justification: https://ecng.sta.uwi.edu/3020/ecng_3020_writing_manual.pdf (MEDIUM)
- FAA Verification Requirements Traceability Matrix guidance — requirement -> method -> result: https://www.faa.gov/sites/faa.gov/files/2022-02/VVSPT-E5-GDE-017_VRTM_V3.0.pdf (MEDIUM)
- Connecticut DSS RTM template — column set and coverage: https://portal.ct.gov/-/media/Departments-and-Agencies/DSS/CT-METS/Library/General/CTDSSRequirementsTraceabilityMatrixv11.pdf (MEDIUM)
- WSU error analysis module — bias, uncertainty, absolute/relative reporting: https://labs.wsu.edu/engineering-lab-report-writing/sample-page/a2-data-analysis-3/ (MEDIUM)
- ASME uncertainty reporting policy — U = sqrt(B^2 + P^2), 95% confidence: https://www.asme.org/wwwasmeorg/media/resourcefiles/shop/journals/final-reporting-uncertainties-in-experimental.pdf (MEDIUM)
- CMU ECE 348 lab safety guidelines — power-ground short check, current limiting, ESD: https://course.ece.cmu.edu/~ece348/labs/docs/lab_safety_guidelines.pdf (MEDIUM)
- UIUC ECE 110 electronics lab safety — low-voltage hazards, current limits, battery risks: https://courses.grainger.illinois.edu/ece110/fa2026/content/labs/Experiments/Skill_Safety_ElectronicsLab.pdf (MEDIUM)
- Safe Power for Learning — low-voltage DC, current limiting, PTC fuse: https://dmccreary.github.io/beginning-electronics/setup/safe-power-for-learning/ (MEDIUM)

**Tool and platform documentation**

- PlatformIO unit testing — native vs. embedded tests, test hierarchy: https://docs.platformio.org/en/latest/advanced/unit-testing/ (MEDIUM)
- PlatformIO `lib_extra_dirs` — deprecated since 6.0; symlink replacement: https://docs.platformio.org/en/latest/projectconf/sections/env/options/library/lib_extra_dirs.html (MEDIUM)
- PlatformIO GitHub Actions — `pio ci` matrix, caching: https://docs.platformio.org/en/latest/integration/ci/github-actions.html (MEDIUM)
- Wokwi CI GitHub Actions — token, path, `expect_text`, scenarios: https://docs.wokwi.com/wokwi-ci/github-actions (MEDIUM)
- Wokwi automation scenarios — `wait-serial`, `set-control`: https://docs.wokwi.com/wokwi-ci/automation-scenarios (MEDIUM)
- Wokwi `diagram.json` format — parts and connections: https://docs.wokwi.com/diagram-format (MEDIUM)
- Wokwi PlatformIO CI example: https://github.com/wokwi/platform-io-esp32-counter-ci (MEDIUM)
- Renode test action — Robot Framework CI: https://github.com/antmicro/renode-test-action (MEDIUM)
- Renode testing documentation: https://renode.readthedocs.io/en/latest/introduction/testing.html (MEDIUM)
- Golioth pytest HIL pattern — flash, serial, assertions: https://blog.golioth.io/automated-hardware-testing-using-pytest/ (MEDIUM)
- Veecle simulation vs. HIL decision guidance: https://veecle.ai/blog/simulation-vs-hil-what-belongs-in-ci (MEDIUM)
- MkDocs Material projects plugin: https://squidfunk.github.io/mkdocs-material/plugins/projects/ (MEDIUM)
- `mkdocs-monorepo-plugin` behavior: https://github.com/backstage/mkdocs-monorepo-plugin (MEDIUM)
- `awesome-pages`/`awesome-nav` monorepo incompatibility: https://github.com/lukasgeiter/mkdocs-awesome-nav/issues/90 (MEDIUM)
- `dorny/paths-filter` — changed-project matrix: https://github.com/dorny/paths-filter (MEDIUM)
- clangd VS Code multi-root issue: https://github.com/clangd/vscode-clangd/issues/38 (MEDIUM)
- pioarduino IntelliSense pipeline — `compiledb`, `--query-driver`: https://github.com/pioarduino/pioarduino-vscode-ide/blob/HEAD/docs/intellisense-pipeline.md (MEDIUM)
- GitHub large files and LFS limits: https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github (MEDIUM)
- GitHub Git LFS overview and Pages limitation: https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-git-large-file-storage (MEDIUM)
- gitleaks — history scanning and pre-commit: https://github.com/gitleaks/gitleaks (MEDIUM)
- GitHub data-leak prevention: https://docs.github.com/en/code-security/tutorials/secure-your-organization/prevent-data-leaks (MEDIUM)
- MADR — Markdown ADR template: https://adr.github.io/madr/ (MEDIUM)
- Microsoft Engineering Playbook — design decision log: https://microsoft.github.io/code-with-engineering-playbook/design/design-reviews/decision-log/ (MEDIUM)
- Harvard Kempner Institute — AGENTS.md and project skills: https://handbook.eng.kempnerinstitute.harvard.edu/s5b_agentic_ai_workflows/configuring_agents.html (MEDIUM)
- Anthropic Academy — agent skills: https://academy.claude.com/courses/introduction-to-agent-skills (MEDIUM)
- Velxio self-hosted ESP32 simulator: https://github.com/davidmonterocrespo24/velxio (MEDIUM)

**Copyright, privacy, and learning research**

- Johns Hopkins copyright guide — publishing coursework, third-party content: https://guides.library.jhu.edu/copyright/publishing (MEDIUM)
- Aarhus University — publishing assignments and consent: https://library.au.dk/en/students/copyright/when-you-want-to-publish-your-assignment (MEDIUM)
- University of Edinburgh — coursework vs. public posting: https://library.ed.ac.uk/library-help/copyright/copyright-students/exams-coursework (MEDIUM)
- Bassner et al., scaffolded AI tutor vs. unrestricted ChatGPT: https://doi.org/10.1016/j.caeai.2025.100537 (MEDIUM)
- Liu, Fan & Pan, scaffolding vs. offloading in AI-assisted programming: https://link.springer.com/article/10.1186/s40594-025-00592-w (MEDIUM)
- Monorepo experience and over-engineering: https://tomasvotruba.com/blog/good-bye-monorepo (LOW)
- Personal monorepo anatomy: https://bharadwajs.me/posts/anatomy-of-a-personal-monorepo/ (LOW)

---

*Feature research for: public embedded-engineering course/homework monorepo*
*Researched: 2026-10-23*

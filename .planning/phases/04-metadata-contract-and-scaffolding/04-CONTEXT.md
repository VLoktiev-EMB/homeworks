# Phase 4: Metadata Contract and Scaffolding - Context

**Gathered:** 2026-10-24
**Status:** Ready for planning

<domain>
## Phase Boundary

Deliver the homework metadata contract and the deterministic scaffold that produces a
buildable homework from it: a JSON Schema for `homework.yaml`, a checker that applies the
schema and the provenance rules, `scripts/new_homework` with idempotent all-or-nothing
writes, and the `templates/` tree that the scaffold renders.

This phase also discharges the Phase 3 carry-forward recorded in `STATE.md`: the starter
code in both homework templates calls `lib/port` through the matching adapter, so a target
`pio run` compiles the adapter and the deferral closes with evidence rather than a claim.

Nothing about generated views, the documentation site, the CI matrix, formatting, the
report contract, simulation, or the pilot homework is designed here. No real homework
directory is created: the scaffold is proven against temporary fixtures and the templates
themselves. `templates/` ships the report and ADR templates because META-03 names them, but
the report *contract* belongs to Phase 10.

What must be true at the end: `scripts/new_homework 1_3-police-flasher --template arduino`
and `--template espidf` both produce a valid project from a clean tree; a second run is a
no-op; any conflicting content fails without writing; `homework.yaml` with an unknown key
is rejected; and the scaffolded ESP-IDF project builds with `pio run`.

</domain>

<decisions>
## Implementation Decisions

### The `homework.yaml` contract

- **D-01:** The schema has a required core and optional structured blocks. Required:
  `schema_version`, `id`, `title`, `board`, `framework`, `language`, `status`, `source`,
  `toolchain`. Optional: `simulation`, `tests`, `report`, `assets`. The optional blocks are
  typed, not free-form, because `additionalProperties: false` at every level would
  otherwise allow only `{}`.
  — **Reversibility:** costly — Phase 5 generators (README index, MkDocs navigation,
  multi-root workspace, `platformio.shared.ini`, CI matrix) and the Phase 11 pilot all read
  this field set; changing a name later touches every `homework.yaml` and every generator.
- **D-02:** `module`, `lesson`, and `slug` are **derived from `id`** by one shared helper and
  are never stored. `id` stays the single source of identity and already satisfies
  `^[0-9]+_[0-9]+-[a-z0-9-]+$` (FOUND-02).
- **D-03:** `schema_version` is the integer `1`. `status` is an enum:
  `planned`, `in-progress`, `complete`, `verified`.
  — **Reversibility:** costly — the status vocabulary becomes the published state model
  for generated views and CI; adding or renaming a value later requires migrating every
  homework file.
- **D-04:** `additionalProperties: false` applies at the top level **and inside every nested
  block**. Repeated shapes go into `$defs`. `unevaluatedProperties` is not used because no
  `allOf`/`anyOf` composition exists at object level.
- **D-05:** `board` is a **board-id string** (for example `esp32-s3-devkitc-1`). MCU, flash,
  PSRAM, frameworks, and the official pinout link live in the board profile introduced in
  Phase 5, keyed by that id. Inline board details would duplicate the profile and drift.
- **D-06:** `source` contains a single required key, `reference` (the source title or URL).
  Full provenance — `source_url`, `retrieved`, `attribution`, `license` — is canonical in
  `task.md` frontmatter (D-15); the checker cross-validates that the URL agrees.
  — **Reversibility:** costly — authority for provenance is split deliberately, and moving
  or renaming the canonical location later touches every `task.md` and the checker.
- **D-07:** `toolchain` records explicit pins:
  `{platformio: "6.2.0", platform: "espressif32@8.0.0"}`. The checker compares them with
  `platformio.shared.ini`, so drift is caught rather than tolerated. The metadata stays
  self-contained for a reader a year later.
  — **Reversibility:** costly — these pins are the reproducibility contract (FOUND-09) and
  the evidence a rebuilt project is compared against.
- **D-08:** Optional block shapes:
  - `simulation`: `{tool: enum[wokwi, velxio, renode, fritzing, none], diagram: path,
    status: enum[none, pending, verified]}`;
  - `tests`: `{framework: enum[unity, none], native: boolean, coverage: boolean}`;
  - `report`: `{path: path, status: enum[placeholder, draft, complete]}`;
  - `assets`: an array of unique relative POSIX paths.
- **D-09:** Field names and enum values are English and machine-readable. `title` may carry
  a non-ASCII display name and emoji; paths, identifiers, and enum values stay ASCII.

### Schema location, validation, and dependencies

- **D-10:** The schema lives at `schema/homework.schema.json`, JSON Schema 2020-12, and is
  documented in `AGENTS.md` as a repository contract.
  — **Reversibility:** costly — the path is consumed by editors (YAML language server),
  the checker, pre-commit, and the Phase 5 generators.
- **D-11:** `scripts/check_metadata.py` is the single validator. Default behaviour scans
  every `homeworks/*/` (`homework.yaml` plus `task.md`); it optionally accepts `[PATH...]`.
  Exit codes follow the repository convention: `0` clean, `1` violation, `2` usage or
  environment error. It never writes.
  — **Reversibility:** costly — Phase 8 CI will consume the exit codes and the `--json`
  output, so the contract must not move casually.
- **D-12:** `new_homework` validates the complete candidate through the same shared
  validation module the checker uses, before the first write. Divergent validation logic is
  forbidden — the scaffold and the hook must agree by construction.
- **D-13:** Python dependencies are delivered through `uv` and pre-commit separately:
  each entry script declares PEP 723 inline metadata and runs as
  `uv run scripts/<script>`; the pre-commit hook uses `language: python` with
  `additional_dependencies: [PyYAML, jsonschema]`, so pre-commit builds its own
  environment and does not depend on `uv`. A **stdlib-only** test in `scripts/tests/` parses
  both declarations as text and fails when the versions diverge.
  — **Reversibility:** costly — the dependency-delivery contract is what Phase 8 CI must
  reproduce; switching models later means touching every script and the hook.
- **D-14:** The repository gate `python3 -m unittest discover -s scripts/tests` stays
  dependency-free. No test may import `yaml` or `jsonschema`; tests that exercise the
  validator shell out to `uv run` or inspect files.

### Provenance in `task.md`

- **D-15:** `task.md` frontmatter is the canonical provenance record and carries
  `source_url` (http/https), `retrieved` (ISO 8601 with timezone), `attribution`, and
  `license` (SPDX-style identifier). The body carries the English paraphrase and never the
  original internal material (META-02).
  — **Reversibility:** costly — provenance is evidence captured at collection time and is
  not recoverable later; changing the shape touches every homework.
- **D-16:** The checker enforces non-empty fields, URL shape, ISO 8601, an SPDX-like
  license, and the **absence of Cyrillic** in `task.md`, with an explicit allowlist file
  (entry names a path and a non-empty reason; a stale entry fails the run).
- **D-17:** `homework.yaml` `source.reference` and `task.md` `source_url` must agree when
  both carry a URL; a mismatch is a violation, not a warning.

### `scripts/new_homework`

- **D-18:** CLI: `scripts/new_homework <id> --template arduino|espidf`. There are no
  interactive prompts; the guided question bank is Phase 9 (FLOW-02, FLOW-03).
- **D-19:** Template resolution: `--template <name>` maps to `templates/homework-<name>/`,
  which must contain a local `template.yaml` (`framework`, `description`). There is no
  central registry; adding a template in v2 is a new directory, not a CLI change.
- **D-20:** Idempotency is content-based. A target path whose bytes are identical is
  `UNCHANGED` (exit 0 on an otherwise clean run); a target path with any other content is
  `CONFLICT` (exit 1). Writes are all-or-nothing: nothing is written when any conflict
  exists. There is no `--force`.
  — **Reversibility:** costly — the semantics are the safety contract for an
  already-published homework directory.
- **D-21:** `--dry-run` prints the same per-path plan and exit codes as a real run, but
  never writes, never creates directories, and never touches git.
- **D-22:** `new_homework` never invokes PlatformIO. Criterion 2 ("builds immediately") is
  proven by an explicit phase verification step and, from Phase 8, by CI.
- **D-23:** Output vocabulary is shared with the checker:
  `PATH: STATUS — reason`, where `STATUS` is one of `CREATE`, `UNCHANGED`, `CONFLICT`,
  `OK`, `ERROR`. Messages are English. `--json` emits the same records for CI.
- **D-24:** File writes are atomic (temporary file plus rename) and the full candidate set
  is validated before the first write, so a failure cannot leave a partial project.

### Templates and the scaffolded project

- **D-25:** `templates/` contains `homework-arduino/`, `homework-espidf/`, `report/`,
  `task/`, `adr/`, and `board-profile/`. Placeholders use `{{name}}` syntax, for example
  `{{homework_id}}` and `{{title}}`. `${...}` is rejected: PlatformIO and CMake use it for
  interpolation.
  — **Reversibility:** costly — the placeholder syntax is baked into every template file
  and into the scaffold's renderer and tests.
- **D-26:** The ADR template **moves** from `docs/decisions/template.md` to
  `templates/adr/template.md`; `docs/decisions/README.md` is updated in the same change.
  One template, no copy.
- **D-27:** Starter code in both homework templates uses `lib/port` plus the matching
  adapter (`lib/arduino` or `lib/espidf`) to drive GPIO and logging. A target `pio run`
  therefore compiles the adapter, closing the Phase 3 carry-forward with evidence.
  — **Reversibility:** costly — this is the architectural example every later homework is
  copied from.
- **D-28:** The scaffolded `platformio.ini` declares `[env:esp32s3_arduino]` or
  `[env:esp32s3_espidf]` plus `[env:native]`, extends the matching section of
  `platformio.shared.ini`, and sets `default_envs` to the target environment only.
  `native` is reached with `-e native` for `pio test`.
  — **Reversibility:** costly — environment names are the Phase 8 CI matrix contract.
- **D-29:** `test/` ships a real Unity test and an `[env:native]` that extends
  `native_unity` with explicit `lib_deps` for `common`, `port`, and `host`. `lib/host`
  never appears in an ESP or Arduino environment.
- **D-30:** The scaffolded `README.md` is a short placeholder (purpose, status, link to the
  report template). `task.md` is a full skeleton with the provenance frontmatter and TODOs.
  The report template stays in `templates/report/` and is not copied into the homework.
- **D-31:** The ESP-IDF template ships an authored `sdkconfig.defaults` (16 MB flash, PSRAM,
  partition settings) and relies on `board_build.partitions` from the shared configuration.
  Build-generated `CMakeLists.txt` and `sdkconfig.<env>` stay gitignored (Phase 2 D-23).
- **D-32:** `templates/board-profile/` is a minimal YAML profile: board id, MCU/SoC, flash,
  PSRAM type, `frameworks[]`, and an official pinout URL. It carries no pin map;
  automatic pinout generation is explicitly out of scope.
- **D-33:** Template rendering is plain string substitution performed by `new_homework`
  (no Jinja dependency). Unknown placeholders are an error, not silently left in place.

### Repository documentation, licensing, and tests

- **D-34:** `AGENTS.md` is updated in full: `schema/` and `templates/` join the Repository
  layout; the agent quick-start gains `uv run scripts/check_metadata.py`; the routing table
  gains "create a homework" and "validate metadata"; the pre-commit description includes
  the new hook. The ~300-line ceiling still applies.
- **D-35:** Two MADR records are added, with rows in `docs/decisions/README.md`:
  **0009** — the homework metadata contract; **0010** — the Python dependency policy
  (PEP 723 plus `uv`, with an isolated pre-commit environment).
- **D-36:** `REUSE.toml` classifies the new paths by extension: `templates/**/*.md` is
  CC-BY-4.0 (document templates), while `templates/**/*.ini`, `templates/**/*.json`, and
  `schema/**` stay on the MIT catch-all (configuration and machine contracts).
- **D-37:** Tooling tests are golden-tree plus targeted assertions: a fixture homework is
  generated into a temporary directory and compared with a committed expected tree, while
  exit codes and output records are asserted individually. Coverage includes a valid and an
  invalid metadata fixture, idempotency, `--dry-run`, the Cyrillic allowlist, and the
  pre-commit hook's invocation.
- **D-38:** No separate "field to consumer" mapping artifact is created. A "Phase 5
  implications" section in this file names the known consumers; Phase 5 owns the mapping.

### Claude's Discretion

- Exact names of helper functions and the internal module split (for example a shared
  `homework_schema` module imported by both entry scripts).
- The renderer implementation, as long as D-25 and D-33 hold.
- The allowlist file path and JSON shape, provided it names a path and a non-empty reason
  and fails on stale entries.
- The `--json` record shape, provided it carries the same status vocabulary.
- Golden-fixture content and the exact assertions chosen for each generated file.
- Board-profile field names beyond the minimum in D-32.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Planning artifacts
- `.planning/PROJECT.md` — core value, constraints, and the locked Key Decisions table.
- `.planning/REQUIREMENTS.md` §Metadata and Generation — **META-01** (schema),
  **META-02** (`task.md` provenance), **META-03** (templates), **META-04** (scaffold);
  §Repository Foundation and Policy — **FOUND-01** (independent project layout).
- `.planning/ROADMAP.md` §Phase 4 — goal, requirements, and the five success criteria.
- `.planning/STATE.md` — the Phase 3 carry-forward: adapter target compilation is owned by
  Phase 4 success criterion 2.
- `.planning/phases/02-toolchain-truth/02-CONTEXT.md` — D-01 (shared configuration file),
  D-05 amended (`src/main.cpp` with three branches), D-14 (N16R8 overrides), D-23
  (generated ESP-IDF files stay gitignored).
- `.planning/phases/03-shared-core-and-dependency-rule/03-CONTEXT.md` — D-01 (dependency
  direction), D-13 (`tests/` native Unity project), D-17 (`host` never in firmware
  `lib_deps`).

### Repository rules and existing decisions
- `AGENTS.md` — homework identifiers, generated files, Conventional Commits, repository
  layout, and the routing table this phase updates.
- `REUSE.toml` — the single license declaration point updated by D-36.
- `docs/decisions/template.md` — the MADR 4.0 template that moves to
  `templates/adr/template.md`.
- `docs/decisions/README.md` — the ADR status index that receives 0009 and 0010.
- `docs/decisions/0001-monorepo-with-independent-projects.md` — one independent project per
  homework.
- `docs/decisions/0007-symlink-shared-libraries.md` — `symlink://` consumption and the
  smoke project's removal.
- `docs/decisions/0008-common-depends-on-port.md` — the dependency direction the starter
  code must exemplify.
- `.pre-commit-config.yaml` — the hook surface that gains the metadata check.
- `platformio.shared.ini` — the sections the scaffolded environments extend and the
  toolchain pins D-07 cross-checks.
- `partitions/default_16MB.csv` — the shared partition table the ESP-IDF template relies on.

### Existing code patterns
- `scripts/check_architecture.py` — the exit-code contract (`0/1/2`), allowlist pattern
  (path + rule + reason, stale entry fails), and read-only determinism this phase mirrors.
- `scripts/check_policy.py` and `scripts/tests/test_check_policy.py` — the
  committed-data-plus-checker pattern.
- `scripts/tests/test_homework_id.py` — extracts the canonical ID pattern from `AGENTS.md`;
  the scaffold's ID validation must stay consistent with it.
- `scripts/tests/test_pio_scripts.py` — how PlatformIO configuration is asserted without
  building.
- `tests/platformio.ini` and `tests/test/` — the existing native Unity project whose
  environment shape D-29 mirrors.
- `lib/{port,common,arduino,espidf,host}/` — the APIs the starter code calls and the
  `library.json` manifests the scaffold's `lib_deps` list.

### External references
- `https://json-schema.org/draft/2020-12/` — the schema dialect (D-10) and
  `additionalProperties`/`unevaluatedProperties` semantics.
- `https://python-jsonschema.readthedocs.io/en/stable/faq/` — `jsonschema` validates Python
  objects; YAML parsing is a separate step (basis for the PyYAML dependency).
- `https://docs.astral.sh/uv/guides/scripts/` — PEP 723 inline script metadata and
  `uv run` (D-13).
- `https://pre-commit.com/#python` — `language: python` hooks and
  `additional_dependencies` with an isolated environment (D-13).
- `https://docs.platformio.org/en/latest/projectconf/sections/env/index.html` —
  environment naming rules and `default_envs` (D-28).
- `https://docs.platformio.org/en/stable/frameworks/espidf.html` — ESP-IDF project layout,
  `sdkconfig.defaults`, and partition configuration (D-31).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `scripts/check_architecture.py` — its exit-code and allowlist conventions are the model
  for `check_metadata.py`; its docstring style is the house style for deterministic checks.
- `scripts/tests/` — the stdlib-only unittest suite every new script joins. Existing tests
  show how to assert on `platformio.ini`, `AGENTS.md`, and generated configuration without
  third-party imports.
- `scripts/tests/test_homework_id.py` — already owns the ID regex and its two-sided probe
  set; the scaffold should reuse the same pattern, not redefine it.
- `platformio.shared.ini` — supplies `[esp32s3_arduino]`, `[esp32s3_espidf]`,
  `[native_unity]`, the N16R8 overrides, and the partitions path the templates extend.
- `tests/platformio.ini` + `tests/test/` — the working native Unity environment that the
  scaffolded per-homework `[env:native]` mirrors.
- `lib/{port,arduino,espidf,host}/include/` — the contract and adapter headers the starter
  code calls; `lib/host` is the test double used by the scaffolded Unity test.
- `docs/decisions/template.md` — the existing MADR 4.0 template to relocate under
  `templates/adr/`.

### Established Patterns
- Policy and configuration are committed data plus a deterministic checker; `.gitignore`
  alone never enforces a rule.
- Checks are layered: fast local hooks in pre-commit, full verification in CI (Phase 8).
- Generated artifacts are never committed; build output and `compile_commands.json` are
  already ignored, and ESP-IDF generated files are scoped to `homeworks/*/`.
- Repository artifacts are English; Conventional Commits use a phase or homework scope.
- Every library version lives only in `library.json`; `lib_deps` entries never carry a
  version.

### Integration Points
- `schema/homework.schema.json` — consumed by the checker, the scaffold, editors, Phase 5
  generators, and Phase 8 CI.
- `scripts/check_metadata.py` — invoked by the pre-commit hook and by Phase 8 CI.
- `scripts/new_homework` — the only supported path to a new homework directory.
- `templates/homework-{arduino,espidf}/` — rendered into `homeworks/<id>/`.
- `templates/{report,task,adr,board-profile}/` — consumed by the scaffold, Phase 10, and
  Phase 5 respectively.
- `.pre-commit-config.yaml` — gains the metadata hook and the Python dependency
  declaration.
- `AGENTS.md`, `REUSE.toml`, `docs/decisions/README.md` — documentation, licensing, and ADR
  index updated in the same phase.

</code_context>

<specifics>
## Specific Ideas

- The user asked whether the chosen dependency model was actually best. The answer recorded
  here: `uv` is the only runner for `scripts/`, while pre-commit owns a separate isolated
  environment; a stdlib-only drift test keeps the two declarations honest. The alternative
  (a `requirements-dev.txt` plus `language: system`) was rejected because it depends on the
  developer's active interpreter.
- The user consistently chose the option that avoids speculative artifacts: no central
  template registry, no field-to-consumer mapping file, no `--force`, no build step inside
  the scaffold, and no interactive prompts in Phase 4.
- The user chose strictness where a wrong value is expensive: `additionalProperties: false`
  at every level, enum statuses, and an explicit Cyrillic allowlist rather than a free-text
  provenance section.
- The user chose self-contained metadata where reproducibility matters: explicit toolchain
  pins cross-checked against `platformio.shared.ini`, and a board-id string resolved against
  the Phase 5 board profile rather than duplicated inline.
- The discussion happened in Ukrainian; this artifact is English per the project language
  constraint.

</specifics>

<deferred>
## Deferred Ideas

- CI wiring for the metadata checker and the scaffold tests — Phase 8 (TOOL-05, TOOL-06).
- The `platformio.shared.ini` generator, the board-profile population, and the
  field-to-consumer mapping — Phase 5 (META-05, META-07).
- The 10-section report contract and the measurement ledger — Phase 10 (REPORT-01..08).
- The interactive guided/one-shot question bank — Phase 9 (FLOW-02, FLOW-03).
- ESP-IDF and STM32 homework templates beyond the two shipped here — v2 (SCALE-01,
  SCALE-02).
- Automatic pinout generation — out of scope in `REQUIREMENTS.md`; board profiles link to
  the official source instead.
- A `--force` overwrite flag — rejected in this phase; reintroducing it would need a new
  decision record because it weakens D-20.
- Python dependency management through a `requirements-dev.txt` or a root project manifest —
  rejected in favour of PEP 723 plus an isolated pre-commit environment.

</deferred>

---

*Phase: 4-Metadata Contract and Scaffolding*
*Context gathered: 2026-10-24*

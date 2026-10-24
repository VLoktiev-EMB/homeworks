# Phase 4: Metadata Contract and Scaffolding - Research

**Researched:** 2026-10-24
**Domain:** Repository tooling — a JSON Schema metadata contract, a deterministic validator, and
a template-rendering scaffold for PlatformIO homework projects
**Confidence:** HIGH for the build contract and the validation mechanics (both were executed
this session); MEDIUM for the schema vocabulary choices that CONTEXT leaves open; LOW only
where noted in the Assumptions Log.

## Summary

The phase has two halves that must not drift: a **contract** (`schema/homework.schema.json`
plus the `task.md` provenance rules) and the **two consumers** of that contract
(`scripts/check_metadata.py` and `scripts/new_homework`, both importing one shared module per
D-12). The research below resolves the mechanics of both halves against the toolchain actually
installed on this machine, not against documentation alone.

The highest-value finding is that **the scaffold contract builds as designed**. A fixture
project placed at `homeworks/<id>` depth, extending `[esp32s3_arduino]` / `[esp32s3_espidf]`
from `platformio.shared.ini`, compiled with the starter code that calls `lib/port` through the
matching adapter. Arduino: `SUCCESS` in 6.29 s. ESP-IDF: `SUCCESS` in 24.69 s (4.30 s
incremental). The ESP-IDF `sdkconfig.json` reported 16 MB flash and octal PSRAM, and the
compilation database contained the three adapter sources and `src/main.cpp` under
`xtensa-esp32s3-elf-g++`. That is the Phase 3 carry-forward discharged with evidence, and it
validates D-27, D-28, D-31 and success criterion 2 in one run.

Three mechanics are easy to get wrong and were reproduced here: (1) `jsonschema`'s `format`
keyword is silent unless a checker is passed, and even then `uri`/`date-time` need optional
extras that this repository will not install — so URL and ISO 8601 shape must be `pattern`s or
Python checks, never `format`; (2) `PyYAML`'s `SafeLoader` turns an unquoted ISO timestamp into
`datetime`, which then fails a `type: string` schema, while `BaseLoader` keeps every scalar a
string and is the right loader for `task.md` frontmatter; (3) `pio run -e native` fails on Unity's
missing `unity_config.h` in both this fixture and the shipped `tests/` project, so the native
environment is test-only and must not be part of the phase gate.

**Primary recommendation:** build the phase as one shared contract module
(`scripts/metadata/contract.py`), two thin entry scripts sharing it, a plan-then-write scaffold
whose dry run is the production algorithm, and a stdlib-only test suite with two committed
golden trees. Resolve the one genuine contradiction in CONTEXT first — a scaffolded `task.md`
with `TODO` provenance cannot pass a checker that requires a real URL (D-16 vs D-30); the
recommendation is a `status: planned` draft rule, documented in Open Question 1.

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**The `homework.yaml` contract**

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
- **D-09:** Field names and enum values are English and machine-readable. `title` may carry a
  non-ASCII display name and emoji; paths, identifiers, and enum values stay ASCII.

**Schema location, validation, and dependencies**

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

**Provenance in `task.md`**

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

**`scripts/new_homework`**

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

**Templates and the scaffolded project**

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

**Repository documentation, licensing, and tests**

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

### Deferred Ideas (OUT OF SCOPE)

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
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description (from `REQUIREMENTS.md`) | Research Support |
|----|--------------------------------------|------------------|
| FOUND-01 | One independent PlatformIO project per homework under `homeworks/<id>/` with `platformio.ini`, `src/`, `include/`, `test/`, `assets/`, `README.md`, `task.md`, `homework.yaml` | Template inventory in §Recommended Project Structure; the exact eight paths are the candidate set the golden-tree test compares; both templates were built at project depth this session |
| META-01 | `homework.yaml` validated by a JSON Schema with `additionalProperties: false`, recording identity, board, framework, language, simulation, tests, report, assets, status, source, toolchain | §Standard Stack + verified schema skeleton in §Code Examples; §Common Pitfalls P1/P2 cover the two silent-failure modes; D-01..D-09 field vocabulary resolved into a probe-validated schema |
| META-02 | `task.md` contains an English paraphrase, source reference, retrieval date, attribution, and never the original internal material | §Pattern 4 (frontmatter with `BaseLoader`), §Code Examples (ISO/SPDX/Cyrillic checks); the "no original material" half is a review check, explicitly flagged in §Open Questions |
| META-03 | `templates/` provides Arduino, ESP-IDF, report, task, ADR, and board-profile templates | §Recommended Project Structure (six directories), §Pattern 5 (placeholder vocabulary), §Common Pitfalls P12/P13 (ADR move breaks `test_adrs.py` and `docs/decisions/README.md`) |
| META-04 | `scripts/new_homework` scaffolds from a template, is idempotent, supports `--dry-run`, refuses to overwrite | §Pattern 2 (plan-then-write), §Code Examples (atomic write, path containment), §Common Pitfalls P8/P10/P11, and the `--dir` test seam in §Open Questions 5 |

</phase_requirements>

## Architectural Responsibility Map

> This is a repository-tooling phase, so the tiers below are the repository's own layers rather
> than web tiers. The mapping exists so the planner does not put validation logic in the
> scaffold, or write behaviour in the checker.

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Metadata contract (field names, enums, shapes) | Committed data — `schema/homework.schema.json` | ADR-0009 | One machine-readable source; D-10 locks the path because editors and Phase 5 read it |
| Schema + provenance validation | Offline repository tooling — `scripts/metadata/contract.py` | `scripts/check_metadata.py`, `new_homework` (both import it) | D-12 forbids divergent validation; one implementation, two callers |
| Enforcement timing | Developer machine — pre-commit hook | CI (Phase 8) | The house pattern is fast local hooks plus full CI, never `.gitignore` alone |
| Provenance capture | Committed content — `task.md` frontmatter | Human review | Provenance is evidence captured at collection time; no tool can reconstruct it |
| Candidate rendering | Repository tooling — `new_homework` renderer | Templates (`templates/**`) | Plain `{{name}}` substitution (D-33); templates are data, the renderer is code |
| Filesystem writes | Repository tooling — `new_homework` | — | All-or-nothing plan, atomic per-file replace (D-20, D-24) |
| Build proof | Developer machine / CI | — | `pio run` is invoked by the verification step, never by the scaffold (D-22) |
| Documentation and licensing | `AGENTS.md`, `docs/decisions/`, `REUSE.toml` | — | D-34..D-36; the repository declares its own contracts |

## Standard Stack

### Core

| Library / tool | Version | Purpose | Why Standard |
|----------------|---------|---------|--------------|
| Python | 3.11+ (3.13.13 verified) | Runs both entry scripts and every test | Stdlib `unittest`, `datetime.fromisoformat` (3.11+ accepts `Z`), `tomllib` already used by the suite |
| `PyYAML` | 6.0.3 `[VERIFIED: uv-resolved environment, this session]` | Parses `homework.yaml` and `task.md` frontmatter | The canonical Python YAML parser; `SafeLoader`/`BaseLoader` avoid arbitrary object construction |
| `jsonschema` | 4.26.0 `[VERIFIED: uv-resolved environment, this session]` | Applies the 2020-12 schema to the parsed object | The reference Python implementation; `Draft202012Validator.check_schema` catches a malformed schema before a single homework is validated |
| `uv` | 0.13.1 `[VERIFIED: uv --version, this session]` | Runs the entry scripts with PEP 723 dependencies | D-13's locked delivery model; also supports the `#!/usr/bin/env -S uv run --script` shebang `[CITED: docs.astral.sh/uv/guides/scripts/]` |
| `pre-commit` | 4.7.0 `[VERIFIED: pre-commit --version, this session]` | Runs the metadata hook in an isolated Python environment | D-13; `language: python` + `additional_dependencies` needs no `uv` on the hook's PATH `[CITED: pre-commit.com/#python]` |
| PlatformIO Core | 6.2.0 `[VERIFIED: pio --version, this session]` | Builds the scaffolded project for criterion 2 | FOUND-09 pin; the toolchain actually used by the Phase 2/3 builds |
| `platformio/espressif32` | 8.0.0 `[VERIFIED: installed platform; both target builds succeeded]` | Arduino and ESP-IDF frameworks on ESP32-S3 | FOUND-09 pin; `[VERIFIED: platformio.shared.ini:2,19]` |
| Unity (ThrowTheSwitch) | 2.6.1 `[VERIFIED: pio test installed and ran it]` | The scaffolded native test | Already pinned in the shared test project `[VERIFIED: tests/platformio.ini:29]` |

### Supporting

| Library / tool | Version | Purpose | When to Use |
|----------------|---------|---------|-------------|
| `reuse` | 6.2.0 `[VERIFIED: reuse --version, this session]` | Proves the MIT / CC-BY-4.0 split after new paths appear | Always, via the existing test and CI job |
| Git | 2.54.0 | Root resolution (`git rev-parse --show-toplevel`), ignore checks | Every checker and test that needs the repository root |
| `difflib` (stdlib) | — | Readable golden-tree failure output | Golden-tree test |
| `datetime` (stdlib) | — | ISO 8601 validation with a mandatory timezone | `task.md` `retrieved` |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `jsonschema` `format: "uri"` / `"date-time"` | `pattern` + `datetime.fromisoformat` | **Required**, not optional: the format checkers are silent without optional extras (Pitfall P1). Adding `rfc3987`/`rfc3339-validator` would add two packages for a check a regex and the stdlib already do exactly |
| `yaml.SafeLoader` for `task.md` | `yaml.BaseLoader` | `SafeLoader` converts an unquoted ISO timestamp to `datetime` and `on`/`yes` to booleans (Pitfall P2). `BaseLoader` returns strings, which is what the provenance contract wants |
| A Jinja dependency | Plain `{{name}}` substitution | D-33 locks substitution; Jinja would add a dependency, a template language, and an escaping surface the scaffold does not need |
| `check-jsonschema` (research STACK.md) | `jsonschema` + PyYAML | The research stack predates D-13; a CLI tool cannot be imported by `new_homework`, and D-12 requires one shared validation path |
| `requirements-dev.txt` + `language: system` | PEP 723 + isolated pre-commit env | Rejected in CONTEXT; a system-language hook depends on the developer's active interpreter |

**Installation:**

```bash
# No new repository-level install. Dependencies are declared inline (PEP 723) and
# installed on demand by uv; pre-commit builds its own hook environment.
```

**Version verification (this session):**

```text
python3 --version                  -> Python 3.13.13
uv --version                       -> uv 0.13.1
pio --version                      -> PlatformIO Core, version 6.2.0
pre-commit --version               -> pre-commit 4.7.0
reuse --version                    -> reuse, version 6.2.0
uv run --no-project --with PyYAML --with jsonschema python3 -c ...
                                   -> yaml 6.0.3, jsonschema 4.26.0
```

## Package Legitimacy Audit

> Run because this phase declares two external Python packages. The seam was invoked as
> `gsd-tools query package-legitimacy check --ecosystem pypi PyYAML jsonschema`.

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| `PyYAML` | PyPI | unknown (lookup failed) | unknown | none reported | `SUS` (all signals `null`) | Keep — flagged; see note |
| `jsonschema` | PyPI | unknown (lookup failed) | unknown | none reported | `SUS` (all signals `null`) | Keep — flagged; see note |

**Why the verdict is not evidence of slop:** every signal is `null` (`exists`, `publishedAt`,
`weeklyDownloads`, `repoUrl`), which is *no observation*, not a negative one. The same command
printed four `failed to copy trust settings of system certificate` errors, and the sandboxed
network is filtered. Independently, `uv` resolved and installed both packages from PyPI in this
session (`Installed 6 packages`, then `Installed 1 package`), which proves registry existence and
installability but, per the package-name provenance rule, does not by itself confer `[VERIFIED]`.

**Packages removed due to `SLOP` verdict:** none.
**Packages flagged as suspicious `[SUS]`:** `PyYAML`, `jsonschema` — planner should re-run the
legitimacy check in a networked environment and record the verdict before the first install. Both
names are already locked by CONTEXT D-13, so the flag is a confirmation checkpoint, not a design
question.

## Architecture Patterns

### System Architecture Diagram

```text
                     templates/homework-<name>/        templates/task/task.md
                     (template.yaml + project files)   (provenance skeleton)
                                  |                            |
                                  +-------------+--------------+
                                                |
  scripts/new_homework <id> --template <name>   v
        |                                              render ({{name}} substitution)
        |                                              |
        |                                    in-memory candidate {path -> bytes}
        |                                              |
        |                                    shared validator (scripts/metadata/contract.py)
        |                                     |- JSON Schema (homework.yaml)
        |                                     |- provenance rules (task.md)
        |                                     |- cross-validation source.reference <-> source_url
        |                                              |
        |                                    plan: CREATE / UNCHANGED / CONFLICT
        |                                              |
        |                          +-------------------+-------------------+
        |                          |                                       |
        |                    --dry-run: print, exit                 real run: if any CONFLICT
        |                    (no mkdir, no write)                          print, exit 1
        |                                                                  |
        |                                                    mkdir -p; temp file + os.replace
        v
  homeworks/<id>/  (8 paths)

  scripts/check_metadata.py  (default: homeworks/*/)
        |  parse homework.yaml (SafeLoader) -> schema
        |  parse task.md frontmatter (BaseLoader) -> provenance rules
        |  cross-validate; Cyrillic scan + allowlist (stale entry fails)
        v
  PATH: OK — reason        exit 0
  PATH: ERROR — reason     exit 1
  (usage/environment)      exit 2
```

### Recommended Project Structure

```text
schema/
└── homework.schema.json          # JSON Schema 2020-12; D-10

scripts/
├── new_homework                  # extensionless, executable, PEP 723; D-18
├── check_metadata.py             # read-only validator; D-11
├── metadata/
│   ├── __init__.py
│   ├── contract.py               # ID pattern, derived parts, schema + provenance validation
│   └── allowlist.json            # {"version": 1, "entries": []}; path + non-empty reason
└── tests/
    ├── test_homework_metadata.py # schema + provenance + allowlist + exit codes
    ├── test_new_homework.py      # plan statuses, dry-run parity, atomicity, golden trees
    ├── test_templates.py         # template inventory, placeholder lint, ini shape
    ├── test_metadata_deps.py     # PEP 723 vs pre-commit version drift (stdlib only)
    └── fixtures/
        └── golden/
            ├── homework-arduino/ # committed expected tree for one id
            └── homework-espidf/

templates/
├── homework-arduino/
│   ├── template.yaml             # framework: arduino; description: ...
│   ├── platformio.ini
│   ├── src/main.cpp
│   ├── include/.gitkeep
│   ├── test/test_homework/test_homework.c
│   ├── assets/.gitkeep
│   ├── README.md
│   └── homework.yaml
├── homework-espidf/
│   ├── template.yaml             # framework: espidf; description: ...
│   ├── platformio.ini
│   ├── src/main.cpp
│   ├── sdkconfig.defaults        # exactly the three Phase 2 lines
│   ├── include/.gitkeep
│   ├── test/test_homework/test_homework.c
│   ├── assets/.gitkeep
│   ├── README.md
│   └── homework.yaml
├── task/task.md                  # canonical provenance skeleton; rendered into every homework
├── report/report.md              # bare skeleton; the 10-section contract is Phase 10
├── adr/template.md               # moved verbatim from docs/decisions/template.md (D-26)
└── board-profile/profile.yaml    # id, SoC, flash, PSRAM, frameworks[], pinout URL (D-32)
```

`task.md` is composed from `templates/task/task.md` rather than duplicated in both homework
templates. That keeps one provenance skeleton and satisfies META-03's separate task template;
the alternative (a copy in each homework template) is rejected because the two copies would
drift. See Open Question 6.

### Pattern 1: One contract module, two consumers

**What:** `scripts/metadata/contract.py` owns the ID pattern, the derived `module`/`lesson`/`slug`
helper (D-02), schema loading, and every validation rule. `check_metadata.py` and `new_homework`
both import it; neither re-implements a rule.
**When to use:** always in this phase — D-12 makes divergence a defect by definition.
**Why it works here:** `new_homework` validates *rendered strings in memory*, so the module must
expose a function that takes `homework_yaml_text` and `task_md_text`, not only file paths. That is
the API the planner should specify first.

### Pattern 2: Plan-then-write (dry run is the production algorithm)

**What:** compute the entire candidate set in memory, classify every target path
(`CREATE` / `UNCHANGED` / `CONFLICT`), validate the candidate, print the plan, and only then
write. `--dry-run` stops after printing. There is exactly one code path; the flag only skips the
write step.
**When to use:** every scaffold invocation.
**Why it works here:** it makes D-21's parity true by construction and makes D-20's
all-or-nothing guarantee checkable before the first `mkdir`.

### Pattern 3: Committed data plus a deterministic checker

**What:** the schema, the allowlist, the templates, and the golden trees are committed data;
the checkers are read-only and deterministic.
**When to use:** every repository rule in this codebase.
**Why it works here:** it mirrors `scripts/check_architecture.py`, whose exit-code contract,
allowlist shape (path + rule + reason, stale entry fails), and read-only determinism are the
house model. The metadata allowlist drops the `rule` key because there is one rule
(Cyrillic) — the shape becomes `{"path": ..., "reason": ...}`.

### Pattern 4: Frontmatter parsed as text, not as YAML scalars

**What:** split `task.md` at the leading `---` fences, then parse the block with
`yaml.load(block, Loader=yaml.BaseLoader)`. Validate the four values as strings.
**When to use:** any frontmatter whose values are all strings (all four provenance fields are).
**Why it works here:** verified this session —

```text
SafeLoader  -> {'retrieved': datetime.datetime(2026, 10, 24, 20, 1, tzinfo=timezone.utc)}
BaseLoader  -> {'retrieved': '2026-10-24T20:01:00Z'}
SafeLoader  -> {'title': True}   for  title: on
BaseLoader  -> {'title': 'on'}
```

### Pattern 5: Fixed placeholder vocabulary, unknown placeholder is an error

**What:** the renderer owns a closed map (`homework_id`, `title`, `framework`, `board`,
`platformio_version`, `platform_version`). A `{{...}}` outside the map is `exit 2`; a `${...}`
anywhere in a template is `exit 2` (D-25).
**When to use:** all template rendering.
**Why it works here:** the templates also contain PlatformIO/CMake/SCons syntax, where `${...}`
is meaningful. Rejecting it at the template level prevents a whole class of silent breakage.

### Anti-Patterns to Avoid

- **A checker that imports the scaffold, or a scaffold that calls the checker as a subprocess.**
  One shared module; no process boundary.
- **Writing files first and validating afterwards.** D-24 forbids it; a validation failure must
  leave the tree untouched.
- **Generating a timestamp into any scaffolded file.** It destroys idempotency and the golden
  tree (Pitfall P10).
- **Shipping `CMakeLists.txt` / `src/CMakeLists.txt` / `sdkconfig.<env>` in the ESP-IDF template.**
  PlatformIO generates them; `.gitignore` already ignores them (Pitfall P4).
- **Repeating inherited keys in `[env:*]`.** `extends` replaces list options wholesale
  `[VERIFIED: tests/platformio.ini:16-24 comment]`; a child `build_flags` would drop
  `-DBOARD_HAS_PSRAM`.
- **Redeclaring the id pattern in three places.** `test_homework_id.py` already extracts the one
  anchored pattern from `AGENTS.md`; the shared module must hold the same literal and a test
  must prove the three agree.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| YAML parsing | A line-based parser for `homework.yaml` | `PyYAML` `SafeLoader` | Quoting, comments, anchors, and flow collections are already solved; a hand parser would reject valid YAML or accept invalid YAML |
| JSON Schema validation | A recursive `dict` walker | `jsonschema.Draft202012Validator` | `$defs`, `$ref`, `additionalProperties`, `uniqueItems`, `const`, and error paths are the library's job; a hand walker will diverge from the schema |
| ISO 8601 validation | A regex for every ISO form | `datetime.datetime.fromisoformat` + `tzinfo is not None` | Python 3.11+ accepts `Z` and offsets and rejects garbage; the timezone check is one line |
| Atomic file replacement | A manual `fsync` + rename dance | `tempfile.mkstemp(dir=target.parent)` + `os.replace` | `os.replace` is atomic within a directory; the temp file must share the target's filesystem |
| Path containment | String prefix comparison | `Path.resolve()` + `relative_to()` | `resolve()` collapses `..` and symlinks; prefix tests are bypassed by `homeworks/x/../../etc` |
| Golden-tree diff reporting | A hand-written first-difference printer | `difflib.unified_diff` | The existing `check_policy.py` already uses it; unified diffs are what reviewers read |
| Duplicate YAML key detection | A regex over the file | A small `SafeLoader` subclass (only if adopted) | PyYAML silently keeps the last duplicate `[VERIFIED: probe]`; if the planner wants rejection, a constructor override is the correct seam |

**Key insight:** every rule in this phase has an edge case that a first implementation misses —
`additionalProperties` at nested levels, YAML scalar coercions, `extends` list replacement,
`os.replace` across filesystems. The library or stdlib already encodes those edges; the
repository's value is the *policy*, not a reimplementation of the parser or validator.

## Runtime State Inventory

Not applicable: Phase 4 is not a rename, refactor, or migration phase. No stored data, live
service configuration, OS-registered state, secret key, or build artifact carries a name that
changes. The only relocation is `docs/decisions/template.md` → `templates/adr/template.md`
(D-26), whose complete reference inventory is three sites: `docs/decisions/README.md:6`,
`scripts/tests/test_adrs.py:26`, and `scripts/tests/test_adrs.py:135` (Pitfall P12).

## Common Pitfalls

### Pitfall P1: `format: "uri"` and `format: "date-time"` silently accept anything

**What goes wrong:** a schema that relies on `format` passes `"not a url"`, `"nope"`, and even
`"javascript:alert(1)"`. The checker then reports `OK` for invalid provenance.
**Why it happens:** `jsonschema` treats `format` as an annotation by default; the checker only
runs when a `format_checker` is passed `[CITED: python-jsonschema docs, validate.rst]`. Even with
one, `uri` and `date-time` are absent unless the `format` extras (and their dependencies, e.g.
`rfc3987`, `rfc3339-validator`) are installed, and a missing dependency validates silently. This
session's probe showed `FormatChecker().checkers` containing only
`['date', 'email', 'idn-email', 'ipv4', 'ipv6', 'regex', 'time', 'uuid']`; `uri` passed `"not a
url"`.
**How to avoid:** encode URL shape as an anchored `pattern` (`^https?://[^\s]+$`) and validate
ISO 8601 in Python with `fromisoformat` + `tzinfo is not None`. Do not add the `format` extras.
**Warning signs:** a metadata fixture with `source_url: not-a-url` exits 0.

### Pitfall P2: PyYAML's scalar resolver corrupts unquoted strings

**What goes wrong:** `retrieved: 2026-10-24T20:01:00Z` becomes a `datetime`, so a schema expecting
`type: string` rejects a file that looks correct; `title: on` becomes `True`; duplicate keys keep
the last value without a warning.
**Why it happens:** PyYAML implements YAML 1.1, whose timestamp and boolean resolvers are broader
than most authors expect. Verified this session in both `SafeLoader` and the default loader.
**How to avoid:** use `SafeLoader` for `homework.yaml` and document that ambiguous scalars must
be quoted; use `BaseLoader` for `task.md` frontmatter, where every value is a string. If
duplicate-key rejection is wanted, subclass `SafeLoader` and override `construct_mapping`.
**Warning signs:** `jsonschema` reports `'retrieved' is not of type 'string'` for a visibly
string-looking value.

### Pitfall P3: `pio run -e native` is not a supported command

**What goes wrong:** the phase gate is extended with `pio run -e native` and fails with
`fatal error: 'unity_config.h' file not found` while compiling Unity.
**Why it happens:** the native environment carries `test_framework = unity`; PlatformIO's *test*
builder supplies `unity_config.h`, the normal build does not. This is not caused by the scaffold:
the shipped `tests/` project fails identically (`pio run -d tests -e native` → `[FAILED]` in
0.29 s, verified this session). `pio test -e native` succeeded in 0.54 s.
**How to avoid:** the native environment is reachable only through `pio test -e native` (D-28).
Use `pio run -t compiledb -e native` if a compilation database is needed; it does not compile.
**Warning signs:** a gate command that fails on the pre-existing `tests/` project too.

### Pitfall P4: Shipping ESP-IDF's generated CMake files

**What goes wrong:** a template that contains `CMakeLists.txt` freezes a generated artefact,
duplicates what the builder writes, and trips the `no-generated-files` hook if it ever lands
under `homeworks/`.
**Why it happens:** PlatformIO's ESP-IDF builder calls `create_default_project_files()`, which
writes a root `CMakeLists.txt` (117 bytes observed) and `src/CMakeLists.txt` (199 bytes observed)
only when they are absent, and writes `src/main.c` when `src/` is empty
`[VERIFIED: ~/.platformio/platforms/espressif32/builder/frameworks/espidf.py:193-215]`.
**How to avoid:** ship `src/main.cpp` and `sdkconfig.defaults`; ship no CMake file and no
`sdkconfig.<env>`. The existing ignore rules are `[VERIFIED: .gitignore:24-28]`:
`homeworks/*/CMakeLists.txt`, `homeworks/*/src/CMakeLists.txt`, `homeworks/*/sdkconfig.*`, and
`!homeworks/*/sdkconfig.defaults`.
**Warning signs:** `git check-ignore -q homeworks/<id>/CMakeLists.txt` returns non-zero because
the file is not ignored, or the file is tracked.

### Pitfall P5: The generated `src/CMakeLists.txt` globs everything in `src/`

**What goes wrong:** an extra scratch file in `src/` is compiled into the firmware.
**Why it happens:** the generated file contains
`FILE(GLOB_RECURSE app_sources ${CMAKE_SOURCE_DIR}/src/*.*)` and
`idf_component_register(SRCS ${app_sources})` `[VERIFIED: generated this session]`.
**How to avoid:** keep the template's `src/` to `main.cpp`; put pure logic in `lib/common` or a
project header.
**Warning signs:** a build log compiling a file nobody wired in.

### Pitfall P6: The shared partition path works for Arduino only because of its basename

**What goes wrong:** the shared `board_build.partitions = ../../partitions/default_16MB.csv`
looks like it must break the Arduino build, which does not read a project-relative CSV.
**Why it happens:** the Arduino core's platformio build script passes
`"ARDUINO_PARTITION_%s" % basename(env.BoardConfig().get("build.partitions", ...))`
`[VERIFIED: ~/.platformio/packages/framework-arduinoespressif32@4.20017.../tools/platformio-build-esp32s3.py:345]`,
so only the basename matters, and `default_16MB.csv` exists in the core's `tools/partitions/`.
The observed Arduino memory map (Flash max 6,553,600 = 0x640000) proves the 16 MB table was
selected.
**How to avoid:** never rename the shared CSV. If a custom table is ever needed, it must be
added to both the repository and the Arduino core's partition set.
**Warning signs:** the Arduino build falls back to a 4 MB / 1.3 MB app layout.

### Pitfall P7: The shared partition path resolves only at `homeworks/<id>` depth

**What goes wrong:** a build fixture placed anywhere else picks the wrong file or aborts with
`Missing partition table file`.
**Why it happens:** the ESP-IDF builder computes
`os.path.abspath(os.path.join(fwpartitions_dir, partitions_csv))` when the framework copy exists,
otherwise `os.path.abspath(partitions_csv)` `[VERIFIED: espidf.py:1817-1829]`. `abspath` is
relative to the SCons working directory, which is the project directory; the Phase 2 error
message confirmed it (`<abs>/homeworks/0_0-toolchain-smoke/default_16MB.csv`).
**How to avoid:** the scaffold's verification fixture must sit at `<root>/homeworks/<id>` and the
temp root must contain `platformio.shared.ini`, `partitions/`, `scripts/pio/compiledb.py`, and
`lib/` at the same relative depths. The symlink-based temp root used in this research is a
working recipe (see §Code Examples).
**Warning signs:** the build reads `/tmp/.../partitions/...` or the framework's default.

### Pitfall P8: `extends` replaces list options wholesale

**What goes wrong:** `[env:esp32s3_arduino] build_flags = -Werror` silently drops
`-Wall -Wextra -Werror=return-type -DBOARD_HAS_PSRAM`.
**Why it happens:** PlatformIO's `extends` does not merge list-valued options; the child wins
wholesale. The repository already documents this twice
`[VERIFIED: tests/platformio.ini:16-24]` and in `check_architecture.py`'s `_option` docstring.
**How to avoid:** the scaffolded ini declares only `extends` and `lib_deps` in each `[env:*]`;
it inherits everything else.
**Warning signs:** `-DBOARD_HAS_PSRAM` absent from a build command line.

### Pitfall P9: The entry point's linkage is load-bearing

**What goes wrong:** `undefined reference to '_Z5setupv'`, `undefined reference to 'app_main'`,
or `undefined reference to '_Z14common_versionv'`.
**Why it happens:** the Arduino core calls C++-mangled `setup`/`loop`, so the entry must be
`.cpp`; `app_main` must be `extern "C"`; every public C header must carry `extern "C"` guards
(Phase 2 D-15 amended; the guards are present in all `lib/*/include` headers).
**How to avoid:** the ESP-IDF template's `src/main.cpp` must contain
`extern "C" void app_main(void)`; the Arduino template must define `void setup(void)` and
`void loop(void)`. A test should assert both tokens.
**Warning signs:** a link error naming a mangled symbol.

### Pitfall P10: A timestamp in a template destroys idempotency

**What goes wrong:** a second scaffold run reports `CONFLICT` on `task.md` because the rendered
`retrieved:` differs; the golden tree differs every day.
**Why it happens:** content-based idempotency (D-20) compares bytes; any clock-derived value
changes them.
**How to avoid:** render `retrieved: TODO` and let a human fill it. `new_homework` must never
read the clock. The only time value in the repository is a user-supplied provenance date.
**Warning signs:** a golden-tree diff whose only change is a date.

### Pitfall P11: `uv run scripts/foo.py` puts `scripts/`, not the repository root, on `sys.path`

**What goes wrong:** `ModuleNotFoundError: No module named 'scripts'` when the entry script
imports the shared module.
**Why it happens:** `sys.path[0]` is the script's directory. Verified this session:
`sys.path[0] = /tmp/claude-501/probe_uv` for a script in that directory, with the repository as
the working directory.
**How to avoid:** insert the repository root before importing:

```python
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.metadata.contract import ...  # noqa: E402
```

The same insert keeps `python scripts/check_metadata.py` working under pre-commit's
`language: python` interpreter.
**Warning signs:** the script works from one directory and not another.

### Pitfall P12: Moving the ADR template breaks two tests and one link

**What goes wrong:** `test_adrs.py` fails with `docs/decisions/template.md missing`, or the index
link 404s.
**Why it happens:** the template path is asserted directly
`[VERIFIED: scripts/tests/test_adrs.py:26]` (`TEMPLATE_FILE = DECISIONS_DIR / "template.md"`) and
again in the assertion message at `:135`; the index links it with a relative path
`[VERIFIED: docs/decisions/README.md:6]`.
**How to avoid:** move the file, point `TEMPLATE_FILE` at
`REPO_ROOT / "templates" / "adr" / "template.md"`, and change the index link to
`../../templates/adr/template.md` in the same commit. Grep for `template.md` after the move; the
only remaining hits should be the PR-template machinery, which is unrelated.
**Warning signs:** `Ran N tests ... FAILED (failures=1)` with a path error.

### Pitfall P13: `AGENTS.md` still calls `lib/` planned

**What goes wrong:** D-34's "update in full" edits only the two new paths and leaves `lib/` under
"Planned, each with the phase that introduces it", which is false since Phase 3.
**Why it happens:** the layout section was written in Phase 1 and `[VERIFIED: AGENTS.md:46-52]`
still lists `lib/` and both new paths as planned. The file is 200 lines and the ceiling is 300
`[VERIFIED: scripts/tests/test_agents_md.py` `LINE_CEILING = 300`].
**How to avoid:** move `lib/`, `schema/`, and `templates/` into "Present today", keep
`docs/standards/` and the skills path marked planned, and re-run `test_agents_md.py`.
**Warning signs:** a "planned" line naming a directory that exists.

## Code Examples

Verified patterns from official sources and from commands executed this session.

### The schema skeleton (probe-validated)

Validated with `Draft202012Validator.check_schema` and exercised against positive and negative
fixtures this session. `$defs` refs resolve without an `$id`; every nested object carries
`additionalProperties: false`.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Homework metadata",
  "type": "object",
  "additionalProperties": false,
  "required": ["schema_version", "id", "title", "board", "framework", "language",
               "status", "source", "toolchain"],
  "properties": {
    "schema_version": { "const": 1 },
    "id": { "type": "string", "pattern": "^[0-9]+_[0-9]+-[a-z0-9-]+$" },
    "title": { "type": "string", "minLength": 1 },
    "board": { "type": "string", "pattern": "^[a-z0-9]+(?:-[a-z0-9]+)*$" },
    "framework": { "enum": ["arduino", "espidf"] },
    "language": { "enum": ["c", "cpp"] },
    "status": { "enum": ["planned", "in-progress", "complete", "verified"] },
    "source": { "$ref": "#/$defs/source" },
    "toolchain": { "$ref": "#/$defs/toolchain" },
    "simulation": { "$ref": "#/$defs/simulation" },
    "tests": { "$ref": "#/$defs/tests" },
    "report": { "$ref": "#/$defs/report" },
    "assets": {
      "type": "array", "uniqueItems": true,
      "items": { "type": "string", "pattern": "^(?!/)(?!.*(?:^|/)\\.\\.(?:/|$))(?!.*\\\\)[A-Za-z0-9._-]+(?:/[A-Za-z0-9._-]+)*$" }
    }
  },
  "$defs": {
    "source": {
      "type": "object", "additionalProperties": false, "required": ["reference"],
      "properties": { "reference": { "type": "string", "minLength": 1 } }
    },
    "toolchain": {
      "type": "object", "additionalProperties": false,
      "required": ["platformio", "platform"],
      "properties": {
        "platformio": { "type": "string", "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$" },
        "platform": { "type": "string", "pattern": "^[a-z0-9-]+@[0-9]+\\.[0-9]+\\.[0-9]+$" }
      }
    },
    "simulation": {
      "type": "object", "additionalProperties": false, "required": ["tool", "status"],
      "properties": {
        "tool": { "enum": ["wokwi", "velxio", "renode", "fritzing", "none"] },
        "diagram": { "type": "string", "pattern": "^(?!/)(?!.*(?:^|/)\\.\\.(?:/|$))(?!.*\\\\)[A-Za-z0-9._-]+(?:/[A-Za-z0-9._-]+)*$" },
        "status": { "enum": ["none", "pending", "verified"] }
      }
    },
    "tests": {
      "type": "object", "additionalProperties": false,
      "required": ["framework", "native", "coverage"],
      "properties": {
        "framework": { "enum": ["unity", "none"] },
        "native": { "type": "boolean" },
        "coverage": { "type": "boolean" }
      }
    },
    "report": {
      "type": "object", "additionalProperties": false, "required": ["path", "status"],
      "properties": {
        "path": { "type": "string", "pattern": "^(?!/)(?!.*(?:^|/)\\.\\.(?:/|$))(?!.*\\\\)[A-Za-z0-9._-]+(?:/[A-Za-z0-9._-]+)*$" },
        "status": { "enum": ["placeholder", "draft", "complete"] }
      }
    }
  }
}
```

Probe results worth preserving as the Wave 0 negative fixtures: unknown top-level key,
unknown key inside `source`, unknown key inside `toolchain`, `id: police-flasher`,
`status: draft`, `framework: stm32`, `platformio: 6.2`, duplicate `assets`, absolute asset path,
`..` in an asset path, and a backslash in an asset path are all rejected; the minimal and full
documents are accepted. Note that `pattern` uses search semantics, so every pattern is anchored.

### PEP 723 entry script (verified end to end)

An extensionless file with this header executes directly and under `uv run --script`; both forms
resolved PyYAML 6.0.3 and printed the same `sys.path[0]` behaviour this session.

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["PyYAML==6.0.3", "jsonschema==4.26.0"]
# ///
"""..."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.metadata.contract import ...  # noqa: E402
```

The same `dependencies` list must appear verbatim in `.pre-commit-config.yaml` under
`additional_dependencies`; the stdlib drift test parses both as text (D-13).

### The pre-commit hook (shape; not executed end to end here)

```yaml
      - id: check-metadata
        name: homework metadata contract
        language: python
        additional_dependencies: ["PyYAML==6.0.3", "jsonschema==4.26.0"]
        entry: python scripts/check_metadata.py
        files: ^(homeworks/|schema/|scripts/check_metadata\.py|scripts/metadata/)
        pass_filenames: false
```

`files:` deliberately excludes `templates/`: an unrendered `homework.yaml` contains
`{{homework_id}}`, which is not valid metadata. `pass_filenames: false` makes the hook scan the
whole `homeworks/` tree, which is tiny until Phase 11.

### Atomic write and containment

```python
def write_atomic(target: Path, text: str) -> None:
    """Write *text* so a crash never leaves a partial file (D-24)."""
    fd, tmp_name = tempfile.mkstemp(dir=target.parent, prefix=".new_homework-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        os.replace(tmp_name, target)
    except BaseException:
        Path(tmp_name).unlink(missing_ok=True)
        raise


def contained(root: Path, homework_id: str) -> Path:
    base = (root / "homeworks").resolve()
    target = (base / homework_id).resolve()
    target.relative_to(base)  # ValueError if the id escaped the tree
    return target
```

`os.replace` is atomic only within one filesystem, which is why the temp file is created in the
target's own directory. Atomicity across the *whole* candidate set is not available on POSIX;
the honest guarantee is: no write happens until the plan is conflict-free and the candidate
validates, and each individual file appears whole or not at all.

### Temp-root build fixture (the recipe that proved criterion 2)

```text
$TMPDIR/scaffold-probe/
├── platformio.shared.ini          # copied from the repository
├── partitions/default_16MB.csv    # copied
├── scripts/pio/compiledb.py       # copied
├── lib -> <repo>/lib              # symlink
└── homeworks/1_3-scaffold-check/
    ├── platformio.ini             # extends esp32s3_arduino / native_unity
    ├── sdkconfig.defaults        # CONFIG_ESPTOOLPY_FLASHSIZE_16MB=y, CONFIG_SPIRAM=y, CONFIG_SPIRAM_MODE_OCT=y
    ├── src/main.cpp
    └── test/test_scaffold/test_scaffold.c
```

Observed results:

```text
pio run                              -> SUCCESS 6.29 s   (Arduino, Flash max 6,553,600)
pio run                              -> SUCCESS 24.69 s  (ESP-IDF, first at this depth)
pio run                              -> SUCCESS 4.30 s   (ESP-IDF incremental)
pio test -e native                   -> PASSED 0.54 s    (1 test case)
pio run -e esp32s3_espidf -t compiledb
    -> 1078 records; lib/common/src/timing.c, lib/espidf/src/{gpio,log,time}.c and
       src/main.cpp present, all xtensa-esp32s3-elf-g++ commands
sdkconfig.json -> ESPTOOLPY_FLASHSIZE=16MB, ESPTOOLPY_FLASHSIZE_16MB=true,
                  SPIRAM=true, SPIRAM_MODE_OCT=true, SPIRAM_MODE_QUAD=false
```

The ESP-IDF build also generated a 117-byte root `CMakeLists.txt` and a 199-byte
`src/CMakeLists.txt`; the numbers match the Phase 2 record (118 B / 199 B) to within a name
length, which is independent confirmation that these are builder output, not project input.

### Provenance checks (verified primitives)

```python
CYRILLIC = re.compile(r"[Ѐ-ԯᲀ-᲏ⷠ-ⷿꙀ-ꚟ]")
SPDX_LIKE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9.+-]*$")

def valid_iso8601(value: str) -> bool:
    try:
        parsed = datetime.datetime.fromisoformat(value)
    except ValueError:
        return False
    return parsed.tzinfo is not None
```

Probe results: `2026-10-24T20:01:00Z` and `2026-10-24T20:01:00+02:00` pass with a timezone;
`2026-10-24` parses but is naive and must be rejected; `not-a-date` raises. `CC-BY-4.0` and `MIT`
match the SPDX-like pattern; `cc by` and `CC_BY` do not. The Cyrillic range matches `поліцейський`,
`Ёлка`, and `Привет` and does not match plain English.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Draft-07 JSON Schema | 2020-12 with `$defs` and `$ref` | 2020-12 published 2020; `jsonschema` 4.x validates it | D-10 locks 2020-12; `$defs` is the modern replacement for `definitions` |
| `definitions` | `$defs` | 2019-09 | The schema skeleton uses `$defs`; `Draft202012Validator.check_schema` accepts it |
| `unevaluatedProperties: false` everywhere | `additionalProperties: false` when there is no composition | 2019-09 introduced `unevaluatedProperties` | D-04 chooses `additionalProperties` because no `allOf`/`anyOf` exists at object level; simpler and stricter locally |
| `jsonschema.RefResolver` | `referencing` / built-in `$defs` resolution | `RefResolver` deprecated in `jsonschema` 4.18 | No resolver object is needed for local `$defs`; do not introduce one |
| `format` as validation | `format` as annotation by default; opt-in checker + extras | 2020-12 aligns with the spec's annotation default | Drives Pitfall P1: use `pattern`, not `format`, for URL shape |
| `requirements-dev.txt` + `language: system` | PEP 723 inline metadata + `uv`; `language: python` for pre-commit | PEP 723 finalized 2023; `uv` adopted it in 2024 | D-13's locked model; two declarations, one drift test |
| Committing ESP-IDF's CMake files | Let the builder generate them and ignore them | Phase 2 D-23 | The template ships only authored input |

**Deprecated/outdated:**
- `jsonschema.RefResolver` — deprecated; not used here.
- A `requirements-dev.txt` for the entry scripts — rejected by CONTEXT.
- The research `ARCHITECTURE.md` illustrative `homework.yaml` (`schema:`, `module:`, `lesson:`,
  `libs:`) — superseded by D-01/D-02; do not copy it.
- A `pio run -e native` gate — never worked for this project shape (Pitfall P3).

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `language` accepts exactly `c` and `cpp`; the scaffold renders `cpp` because the entry point is `.cpp` | Standard Stack / schema | A wrong enum rejects a legitimate homework or locks a value that must migrate later; CONTEXT names the field but not its vocabulary |
| A2 | `title` defaults to the title-cased `slug` derived from `id`; no `--title` flag is added | Pattern 2 / Open Question 4 | A published title would need a manual edit; a later flag is a CLI change but not a data migration |
| A3 | The PlatformIO Core pin (`6.2.0`) is a constant in the shared module, because `platformio.shared.ini` carries only the platform pin | Standard Stack | If the constant drifts from FOUND-09, generated metadata lies; a test against `REQUIREMENTS.md` mitigates it |
| A4 | A `status: planned` homework may carry the literal `TODO` in the four provenance fields | Open Question 1 | Without this, a freshly scaffolded project cannot pass the pre-commit hook; the alternative is to require real provenance at scaffold time |
| A5 | Both entry scripts gain a `--dir PATH` test seam (default: `git rev-parse --show-toplevel`) | Open Question 5 | Without a seam the scaffold cannot be tested without creating a real `homeworks/` directory, which CONTEXT forbids |
| A6 | `task.md` is composed from `templates/task/task.md`, not duplicated in both homework templates | Recommended Project Structure | If the planner expects a self-contained template directory, the candidate-set rule must be stated explicitly or the file duplicated |
| A7 | `include/` and `assets/` are preserved in templates with `.gitkeep` placeholders | Recommended Project Structure | A template cannot carry an empty directory in git; the alternative is a `directories:` key in `template.yaml`, which D-19 does not define |
| A8 | Each scaffolded `homework.yaml` carries a `# yaml-language-server: $schema=../../schema/homework.schema.json` modeline | Open Question 7 | Without it, editors do not associate the schema; a `.vscode/settings.json` mapping is the alternative, and Phase 6 owns editor onboarding |
| A9 | `templates/report/report.md` is a bare skeleton; the 10-section contract stays in Phase 10 | Recommended Project Structure | Pre-empting the contract would create a second authority and a Phase 10 migration |
| A10 | The package-legitimacy lookup for `PyYAML` and `jsonschema` was inconclusive (all signals `null`) | Package Legitimacy Audit | If the packages were somehow compromised, the install would be unsafe; both are locked by CONTEXT and were installed from PyPI by `uv` this session, so the residual risk is low but the check should be re-run |

**If this table is not empty:** the planner should treat A1–A9 as decisions to confirm at plan
time (or in a short discuss follow-up), and A10 as a confirmation checkpoint before the first
dependency install.

## Open Questions

1. **How does a scaffolded `task.md` with TODOs pass the provenance checker?**
   - What we know: D-30 requires a skeleton with TODOs; D-16 requires a non-empty URL, an ISO
     8601 timestamp, and an SPDX-like license. Both are locked.
   - What's unclear: whether the checker should exempt drafts or whether the scaffold must
     collect provenance flags.
   - Recommendation: add a `status: planned` draft rule. Require the four keys to be present;
     allow the exact sentinel `TODO` while `status` is `planned`; reject the sentinel as soon as
     status moves to `in-progress` or beyond, and apply the full shape checks then. Document the
     rule in ADR-0009 and in `AGENTS.md`. A test fixture must prove both sides.

2. **Where does `toolchain.platformio` come from at scaffold time?**
   - What we know: `platformio.shared.ini` pins `platform = espressif32@8.0.0`
     `[VERIFIED: platformio.shared.ini:2,19]` but carries no Core version; D-22 forbids invoking
     PlatformIO.
   - What's unclear: the single source of truth for `6.2.0`.
   - Recommendation: a module constant `PLATFORMIO_CORE = "6.2.0"` plus a stdlib test that the
     literal appears in `REQUIREMENTS.md` (FOUND-09). The checker cross-checks only
     `toolchain.platform` against the shared ini, and validates `toolchain.platformio` by shape.

3. **What is the exact `language` vocabulary?**
   - What we know: the entry point is `.cpp` and the libraries are C; D-09 requires ASCII enum
     values.
   - What's unclear: whether `c`, `cpp`, or both are valid for a homework.
   - Recommendation: `enum: ["c", "cpp"]`, render `cpp`. Record the choice in ADR-0009.

4. **Does the scaffold take a `--title` flag?**
   - What we know: D-18 lists only `<id> --template`; D-21/D-23 add `--dry-run` and `--json`.
   - What's unclear: whether a derived title is acceptable for a published artefact.
   - Recommendation: derive `"Police Flasher"` from `1_3-police-flasher` (the shared `slug`
     helper already exists for D-02) and add no flag in this phase. A later `--title` is additive.

5. **How are the scaffold and the checker tested without creating a real homework directory?**
   - What we know: CONTEXT forbids a real homework directory; D-14 forbids importing `yaml` or
     `jsonschema` in tests, so the tests must run the scripts as subprocesses.
   - What's unclear: how to relocate the output.
   - Recommendation: add `--dir PATH` to both scripts, mirroring `check_architecture.py --dir`
     and `check_pr_templates.py --dir`. Tests copy `templates/`, `schema/`,
     `platformio.shared.ini`, and `partitions/` into a temp root and symlink `lib/`, then run
     `uv run scripts/new_homework <id> --template <name> --dir <temp>`.

6. **Is the homework template self-contained, or composed with the task template?**
   - What we know: D-19 says a template directory must contain `template.yaml`; D-25 lists a
     separate `templates/task/`; D-30 says the scaffolded `task.md` is a skeleton.
   - What's unclear: whether `task.md` lives in each homework template or is composed.
   - Recommendation: compose. Define the candidate set as "every file under
     `templates/homework-<name>/` except `template.yaml`, plus `templates/task/task.md` →
     `task.md`". A test asserts the composition and that no homework template carries its own
     `task.md`.

7. **How is the schema associated with `homework.yaml` in an editor?**
   - What we know: D-10 names editors (YAML language server) as a consumer of the schema path.
   - What's unclear: whether the repository wants a per-file modeline or an editor setting.
   - Recommendation: a `# yaml-language-server: $schema=../../schema/homework.schema.json`
     modeline in each scaffolded and template `homework.yaml`; it is a comment, so it cannot
     become an unknown property. Phase 6 can add the `.vscode` mapping later.

8. **How is "no original internal material" verified?**
   - What we know: no tool can prove a paraphrase is not copied text. The Cyrillic scan and the
     provenance fields are the machine-checkable proxies.
   - What's unclear: whether criterion 4 should be a review-only check.
   - Recommendation: machine-check provenance shape, Cyrillic absence, and the allowlist; record
     criterion 4's paraphrase review as a manual UAT item with the template's TODO text as the
     evidence artefact.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3 | Both entry scripts, the whole suite | Yes | 3.13.13 | `uv` can download a matching interpreter if `requires-python` is unmet |
| `uv` | PEP 723 execution, script tests | Yes | 0.13.1 | None for the tests; pre-commit does not need it |
| `PyYAML` | Schema and frontmatter parsing | Not in system Python; resolved by `uv` | 6.0.3 | None — a stdlib YAML parser does not exist |
| `jsonschema` | Schema validation | Not in system Python; resolved by `uv` | 4.26.0 | None for the same reason |
| PlatformIO Core | Criterion 2 build proof | Yes | 6.2.0 | None |
| `espressif32` platform + ESP-IDF framework/toolchain | ESP-IDF build | Yes | 8.0.0 | None; the first clean build downloads them |
| Unity | Scaffolded native test | Yes (cached) | 2.6.1 | The first `pio test` downloads it from the registry |
| `pre-commit` | Hook invocation and the config test | Yes | 4.7.0 | None |
| `reuse` | License split test and CI job | Yes | 6.2.0 | None |
| Git | Root resolution, ignore checks | Yes | 2.54.0 | None |
| `yamllint` | Phase 6 lint layer | No | — | Not needed in this phase |

**Missing dependencies with no fallback:** none that block the phase.
**Missing dependencies with fallback:** `yamllint` (Phase 6); system-Python `PyYAML`/`jsonschema`
(intentionally absent, supplied by `uv`).

**Two environment notes for the planner.** First, `uv` needs a writable cache; in this sandbox
`~/.cache/uv` was not writable and `UV_CACHE_DIR=$TMPDIR/...` fixed it. A normal developer
machine and CI do not need that. Second, a sandboxed network can block the Unity download on a
cold machine; the repository already depends on it through `tests/platformio.ini`, so this is
not new.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | stdlib `unittest` (no pytest, no third-party import in tests — D-14) |
| Config file | none — discovery via `scripts/tests/__init__.py` |
| Quick run command | `python3 -m unittest discover -s scripts/tests -v` |
| Full suite command | the same, plus `pio test -d tests -e native` and the scaffold build verification |
| Current baseline | 190 tests, about 62 s on this machine, all passing |

### Phase Requirements → Test Map

| Req ID | Behaviour | Test Type | Automated Command | File Exists? |
|--------|-----------|-----------|-------------------|-------------|
| FOUND-01 | The scaffold produces the eight required paths | integration | `uv run scripts/new_homework 1_3-fixture --template arduino --dir <tmp>` then walk the tree | ❌ Wave 0 |
| FOUND-01 | The target environment builds from the scaffolded tree | build | `pio run -d <tmp>/homeworks/1_3-fixture` (Arduino and ESP-IDF) | ❌ Wave 0 (phase verification step, not unit) |
| META-01 | Unknown top-level key is rejected | unit | `test_homework_metadata.py::test_unknown_top_level_key_is_error` | ❌ Wave 0 |
| META-01 | Unknown key inside every nested block is rejected | unit | `...::test_unknown_nested_key_is_error` (subTest per `$defs`) | ❌ Wave 0 |
| META-01 | Required fields, enums, patterns, `uniqueItems` behave | unit | `...::test_schema_accepts_valid_and_rejects_invalid_fixtures` | ❌ Wave 0 |
| META-02 | Frontmatter has exactly four non-empty fields | unit | `...::test_task_frontmatter_shape` | ❌ Wave 0 |
| META-02 | URL, ISO 8601, SPDX-like shape are enforced | unit | `...::test_provenance_shapes` | ❌ Wave 0 |
| META-02 | Cyrillic is rejected; allowlist entry suppresses; stale entry fails | unit | `...::test_cyrillic_gate_and_allowlist` | ❌ Wave 0 |
| META-02 | `source.reference` / `source_url` disagreement is an error | unit | `...::test_cross_validation` | ❌ Wave 0 |
| META-03 | All six template directories exist with the required files | unit | `test_templates.py::test_template_inventory` | ❌ Wave 0 |
| META-03 | No `${...}`; every `{{...}}` is in the known set | unit | `...::test_placeholder_lint` | ❌ Wave 0 |
| META-03 | The ADR template moved and the old path is gone | unit | `...::test_adr_template_moved` + updated `test_adrs.py` | ❌ Wave 0 |
| META-04 | Second run reports `UNCHANGED` and exit 0 | integration | `test_new_homework.py::test_second_run_is_noop` | ❌ Wave 0 |
| META-04 | Modified target reports `CONFLICT`, exit 1, and writes nothing | integration | `...::test_conflict_writes_nothing` | ❌ Wave 0 |
| META-04 | `--dry-run` prints the same records and creates nothing | integration | `...::test_dry_run_parity` | ❌ Wave 0 |
| META-04 | Golden trees match for both templates | integration | `...::test_golden_tree` (unified diff on failure) | ❌ Wave 0 |
| D-13 | PEP 723 and pre-commit declarations agree | unit | `test_metadata_deps.py::test_pinned_versions_agree` | ❌ Wave 0 |
| D-37 | The pre-commit hook's config shape is correct | unit | `test_metadata_deps.py::test_hook_declaration` | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** `python3 -m unittest discover -s scripts/tests -v`.
- **Per wave merge:** the same, plus `pio test -d tests -e native` if a shared library changed.
- **Phase gate:** the full suite green, `pre-commit run --all-files` green, and one target
  build per template from the temp-root fixture. Do not add `pio run -e native` (Pitfall P3).

### Wave 0 Gaps

- [ ] `scripts/tests/test_homework_metadata.py` — covers META-01, META-02, the allowlist, exit
      codes and `--json`.
- [ ] `scripts/tests/test_new_homework.py` — covers META-04, FOUND-01's path set, idempotency,
      dry-run, conflict, and the golden trees.
- [ ] `scripts/tests/test_templates.py` — covers META-03 and the `platformio.ini` shape.
- [ ] `scripts/tests/test_metadata_deps.py` — covers D-13's drift rule.
- [ ] `scripts/tests/fixtures/golden/homework-{arduino,espidf}/` — the committed expected trees.
- [ ] A shared temp-root helper (copytree + symlink `lib/`) used by the scaffold tests.
- [ ] Update `scripts/tests/test_adrs.py`'s `TEMPLATE_FILE` (Pitfall P12).
- [ ] No framework install is needed; the suite is stdlib-only.

## Security Domain

`security_enforcement` is enabled and `security_asvs_level` is 1. The relevant categories for an
offline repository tool are input validation and file handling; authentication, session
management, access control, and cryptography are not applicable.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | No | No identity or credential is handled |
| V3 Session Management | No | No session exists |
| V4 Access Control | No | Local tooling; repository access is GitHub's ruleset |
| V5 Input Validation | Yes | JSON Schema 2020-12 + `Draft202012Validator`; ID and template-name regexes; frontmatter field checks; `SafeLoader`/`BaseLoader` |
| V6 Cryptography | No | No cryptographic operation; license identifiers are strings, not signatures |
| V7 Error Handling and Logging | Yes | Exit codes `0/1/2`; `ERROR:` on stderr; no traceback leaks; deterministic messages |
| V12 Files and Resources | Yes | `Path.resolve()` containment, symlink refusal, file-size caps, atomic replace |

### Known Threat Patterns for This Stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Path traversal via the homework ID (`../../etc`) | Tampering | Anchor the ID regex; `resolve()` + `relative_to()` before any write |
| Path traversal via `--template` | Tampering | `^[a-z0-9-]+$`; require the directory to contain `template.yaml`; containment check |
| Symlink follow from a template file or the target | Tampering / Elevation of Privilege | Skip symlinked template entries; treat a symlinked target as `CONFLICT`; never write through one |
| YAML alias expansion ("billion laughs") or an oversized metadata file | Denial of Service | `SafeLoader`/`BaseLoader` plus a size cap (the allowlist precedent is 64 KiB); optionally reject anchors in a loader subclass |
| Overwriting a published homework | Tampering | Content-based `CONFLICT`, all-or-nothing plan, no `--force` (D-20) |
| Non-deterministic output that hides a change | Repudiation | Sorted paths, no timestamps, golden trees, byte-identical repeated runs |
| Leaking an absolute path or a configured identity in output | Information Disclosure | Print repo-relative POSIX paths only; the existing `test_license_hygiene.py` identity rule stays |
| Template placeholder injection into generated code | Tampering | A closed placeholder map; reject `${...}` and unknown `{{...}}` (D-25, D-33) |

## Phase 5 Implications

D-38 asks this file to name the known consumers of the metadata contract without building the
mapping. Phase 5 reads `homework.yaml` for:

- the README index row and the `homeworks/README.md` catalogue — needs `id`, `title`, `status`;
- MkDocs navigation — needs `id`, `title`, and the module/lesson derived from `id`;
- the multi-root `homeworks.code-workspace` — needs `id` and `title` (display names may be emoji;
  paths stay ASCII);
- the `platformio.shared.ini` generator and its `--check` gate — needs `framework`, `board`,
  `toolchain.platform`;
- the CI matrix and `scripts/affected.py` — needs `id`, `framework`, `toolchain`, `simulation`,
  `tests`;
- board pages — needs `board` (resolved against the Phase 5 board profile);
- the Phase 11 pilot — every required field plus the optional blocks.

The contract's only stable keys are the ones D-01 fixes; Phase 5 must not add a field without a
schema version bump.

## Sources

### Primary (HIGH confidence)

- Local execution, 2026-10-24: `pio run` on an Arduino fixture at `homeworks/<id>` depth —
  `SUCCESS 6.29 s`, Flash max 6,553,600; on an ESP-IDF fixture — `SUCCESS 24.69 s` then
  `4.30 s`; `pio test -e native` — `PASSED 0.54 s`; `pio run -e esp32s3_espidf -t compiledb` —
  1078 records with the adapters and `src/main.cpp`; `sdkconfig.json` shows 16 MB and octal
  PSRAM.
- Local execution, 2026-10-24: `pio run -d tests -e native` fails on `unity_config.h`, matching
  the fixture — proving the native environment is test-only.
- Installed builder source: `~/.platformio/platforms/espressif32/builder/frameworks/espidf.py`
  `:193-215` (CMake/`src/main.c` generation), `:1817-1829` (`PARTITIONS_TABLE_CSV` resolution);
  `~/.platformio/packages/framework-arduinoespressif32@4.20017.../tools/platformio-build-esp32s3.py`
  `:345` (`ARDUINO_PARTITION_<basename>`).
- Local probes, 2026-10-24: PyYAML 6.0.3 and jsonschema 4.26.0 behaviour (`format` checkers,
  scalar resolution, duplicate keys, `$defs`, `uniqueItems`, path patterns, ISO 8601, SPDX,
  Cyrillic); `uv` shebang and `sys.path[0]` for an extensionless script.
- In-repo sources read verbatim this session: `AGENTS.md:101-108`, `platformio.shared.ini:1-37`,
  `tests/platformio.ini:1-29`, `.gitignore:1-28`, `.pre-commit-config.yaml`,
  `scripts/check_architecture.py`, `scripts/check_policy.py`, `scripts/tests/test_adrs.py:26,135`,
  `scripts/tests/test_agents_md.py`, `scripts/tests/test_license_hygiene.py`,
  `scripts/tests/test_pio_scripts.py`, `docs/decisions/template.md`,
  `docs/decisions/README.md:6`, `lib/*/library.json`, `lib/*/include/**`,
  `scripts/pio/compiledb.py`, `partitions/default_16MB.csv`.

### Secondary (MEDIUM confidence)

- Context7 `/python-jsonschema/jsonschema` — format validation is opt-in; `format` extras are
  required for `uri`/`date-time`; a missing dependency validates silently.
- Context7 `/astral-sh/uv` — PEP 723 example with `#!/usr/bin/env -S uv run --script`,
  `requires-python`, `dependencies`, and the note that `dependencies` is required even when empty.
- `https://pre-commit.com/#python` — `language: python` runs without system-level Python
  dependencies; `additional_dependencies` are appended to the hook environment's install;
  `files`, `types`, and `pass_filenames` semantics.
- `https://docs.platformio.org/en/stable/frameworks/espidf.html` — ESP-IDF project layout,
  `sdkconfig.defaults`, and the builder behaviour (the installed source was the authority where
  the page was ambiguous).
- `https://docs.astral.sh/uv/guides/scripts/` — the same shebang, quoted directly.

### Tertiary (LOW confidence)

- The seam's `classify-confidence` returns MEDIUM for Context7 (even with `--verified`) and LOW
  for `webfetch`; claims resting only on those providers are cited, not verified.
- The package-legitimacy lookup for `PyYAML` and `jsonschema` returned `SUS` with all-`null`
  signals after four certificate errors — an inconclusive probe, not a negative finding.

## Metadata

**Confidence breakdown:**

- **Standard stack:** HIGH — every version was read from the installed tool or resolved by `uv`
  in this session.
- **Architecture:** HIGH for the build and validation mechanics (executed), MEDIUM for the
  vocabulary choices CONTEXT leaves open (A1–A9).
- **Pitfalls:** HIGH — P1–P13 are either reproduced here or anchored in an installed source file
  or a committed test; P3 and P4 were directly observed.
- **Security:** MEDIUM — the controls are standard and the threat model is small, but no
  adversarial fuzzing was performed.

**Research date:** 2026-10-24
**Valid until:** 2026-11-24 for the tool behaviour and the PlatformIO/Arduino basename semantics;
re-check the pinned versions and the `jsonschema` format-extras list if either package is
upgraded, and re-run the legitimacy check with network access.

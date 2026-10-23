# Phase 3: Shared Core and Dependency Rule - Context

**Gathered:** 2026-10-24
**Status:** Ready for planning

<domain>
## Phase Boundary

Deliver the minimal, framework-free C core the rest of the monorepo builds on: the five
`lib/port` contracts, a small proven set of `lib/common` logic, thin `lib/arduino` /
`lib/espidf` adapters and `lib/host` test doubles, a top-level `tests/` PlatformIO project
with the shared Unity suite, and `scripts/check_architecture.py` wired into the local
gate.

This phase also discharges the Phase 2 carry-forward: the partitions CSV moves to a
permanent location, the temporary `homeworks/0_0-toolchain-smoke/` project is deleted in a
dedicated commit, and `scripts/tests/test_pio_scripts.py` stops hard-reading that project.

Nothing about metadata, scaffolding, generated views, formatting, CI, simulation, or the
pilot homework is designed here. No homework directory is created; domain logic for
homework 1.3 belongs to Phase 11 and lives in that homework's own `src/`.

What must be true at the end: `common` and `port` build natively with no framework
headers and no target toolchain; the shared Unity suite passes and produces the same
result over 20 consecutive runs using fake time from `lib/host`; `check_architecture.py`
rejects a forbidden include both under test and in pre-commit; and every public header
exposes a C contract behind `extern "C"` with no universal HAL.

</domain>

<decisions>
## Implementation Decisions

### Dependency direction

- **D-01:** The dependency edge is **`common → port`**. `lib/port` depends on nothing (no
  project headers, no framework headers); `lib/common` may include `port` headers and call
  injected port functions; adapters include `port` only; `port → common`, `port → adapter`,
  `adapter → common`, and any framework include in `common`/`port` are forbidden. This
  resolves the contradiction between ADR-0002 ("`common` depends on nothing; `port`
  depends on `common`") and ARCH-05/research ("`common → port`") in favour of the
  requirement text and the research component table.
  — **Reversibility:** costly — every shared source, adapter, and future homework's include
  graph plus the checker encode the direction; flipping it later is a repository-wide
  refactor.
- **D-02:** Record the direction in a new **`docs/decisions/0008-*.md`** that supersedes
  only the dependency-rule sentence of ADR-0002. ADR-0002 stays accepted and untouched as
  history; `docs/decisions/README.md` gains the 0008 row in the same change.
  — **Reversibility:** costly — ADR numbers are sequential and permanent, and published
  cross-references depend on them (Phase 1 D-27).
- **D-03:** Do **not** add a `dependencies` field to any `library.json`. With `symlink://`,
  PlatformIO resolves manifest dependencies against the package registry, which would try
  to fetch unrelated packages named `common`, `port`, and so on. Every project lists its
  full `lib_deps` explicitly; Phase 5 generates that list. This deliberately supersedes
  the advice on `.planning/research/STACK.md:248`.
- **D-04:** All five libraries move from `0.1.0` to **`0.2.0`**, because each gains real
  public API beyond the Phase 2 linking stub. The duplicated version-string returns in the
  `.c` sources are removed, so the version lives only in `library.json` (fixes Phase 2
  review WR-03).

### Port contracts

- **D-05:** `lib/port` defines **all five contracts** required by ARCH-01: `time`, `gpio`,
  `i2c`, `spi`, and `log`. I2C and SPI expose narrow **bus-level** operations (transfer,
  read, write), never a whole-driver interface (ARCH-07).
- **D-06:** Every contract carries a `void *ctx` opaque pointer. "Port contains no state"
  is read as "port owns no global mutable state and mutates nothing"; the state behind
  `ctx` belongs to the adapter. This interpretation is recorded in ADR-0008. It allows
  multiple instances (two buses, two timers) and clean test isolation.
- **D-07:** `lib/host` provides deterministic fakes for **all five** contracts.
- **D-08:** `lib/arduino` and `lib/espidf` implement `time`, `log`, and `gpio` in this
  phase. I2C and SPI framework adapters are deferred to the first homework that needs
  them; the contracts exist, the implementations do not.
- **D-09:** Contracts report failure through `enum port_status_t` with at least
  `PORT_OK`, `PORT_ERR_TIMEOUT`, `PORT_ERR_IO`, `PORT_ERR_INVALID_ARG`,
  `PORT_ERR_NOT_SUPPORTED`. Logging uses four levels: `ERROR`, `WARN`, `INFO`, `DEBUG`.
  No POSIX `errno` mixing.
- **D-10:** Adapters stay thin: they translate a call and return a status; they contain no
  business logic and leak no framework types through their public headers.

### Common logic

- **D-11:** Ship only the **proven minimum**: `ring_buffer`, `timing`, and `crc`/`hex`.
  `timing` includes a small `port_time_t`-based debounce/elapsed helper so the suite
  genuinely exercises fake time from `lib/host` (success criterion 4). `fixed_point`, a
  generic state machine, and a calculations module are deferred until real duplication
  appears (Pitfall C15).
- **D-12:** Homework-specific logic never moves into `lib/common`. The police-flasher
  logic lives in `homeworks/1_3-police-flasher/src/` in Phase 11; reuse is promoted to
  `common` only after the same code appears in a second or third homework ("copy twice,
  extract on the third use").

### Tests, enforcement, and packaging

- **D-13:** The top-level `tests/` is a real PlatformIO project with `[env:native]`,
  `test_framework = unity`, and an explicit `lib_deps` of `common`, `port`, and `host`
  (symlinked). It must build and run without a target toolchain.
- **D-14:** Determinism is proven by `scripts/tests/test_native_determinism.py`, which
  invokes `pio test -e native` 20 times and compares a normalized summary of
  `test_name: PASS/FAIL` plus counts. Raw stdout is never compared, because it carries
  timings and paths. The test joins the repository gate
  `python3 -m unittest discover -s scripts/tests -v`.
- **D-15:** `scripts/check_architecture.py` performs a **textual `#include` scan** of
  `lib/**` and `homeworks/**`, enforcing the layer rules and the "exactly one adapter per
  homework" rule, with an empty-by-default allowlist mechanism. `tests/**` is not scanned.
  Transitive purity of `common`/`port` is proven by the native compile gate, not by the
  scanner.
- **D-16:** `check_architecture.py` runs as a **local pre-commit hook** in this phase. The
  20-run native suite stays in the Python test suite and manual runs; pre-push is Phase 6
  and CI is Phase 8.
- **D-17:** `lib/host` remains a library with `library.json`, linked only from `tests/`
  and `[env:native]`. The checker rejects `host` in `lib_deps` of any ESP/Arduino
  environment, so fakes cannot reach firmware.

### Phase 2 carry-forward

- **D-18:** `default_16MB.csv` moves to **`partitions/default_16MB.csv`**;
  `platformio.shared.ini` points to `../../partitions/default_16MB.csv`; a test asserts
  that the path referenced by the shared configuration exists. This must land before the
  smoke project is deleted (Phase 2 review CR-01).
  — **Reversibility:** costly — every ESP32 project resolves this path relative to its own
  directory; moving it later breaks every existing build.
- **D-19:** `homeworks/0_0-toolchain-smoke/` is deleted in a dedicated commit, as an
  explicit task in this phase's plan (Phase 2 D-07).
- **D-20:** `scripts/tests/test_pio_scripts.py` is refactored off the smoke project onto
  permanent fixtures so that deleting the directory cannot produce `FileNotFoundError`
  (Phase 2 review WR-01). Project-specific assertions are either retargeted to `tests/` or
  removed with the project.
- **D-21:** C formatting is **deferred to Phase 6**. Write consistent code now; do not add
  clang-format or perform a mass reformat in this phase.

### Claude's Discretion

- Exact signatures, field names, and header layout of the five contracts, within the
  decisions above.
- Whether `lib/port` is header-only or ships a small `.c` for inline helpers.
- Internal `tests/` layout: test file names, whether one `[env:native]` is enough, and
  whether it extends `native_unity` or defines its own environment locally. Keeping
  `test_framework = unity` local to `tests/` is acceptable and avoids imposing Unity on
  future native homework environments.
- The normalized summary format used for the 20-run comparison.
- The internal implementation shape of `check_architecture.py` and the allowlist file
  format.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Planning artifacts
- `.planning/PROJECT.md` — core value, constraints, and the locked Key Decisions table
  (ports and adapters, no universal HAL, pinned toolchain, `symlink://`).
- `.planning/REQUIREMENTS.md` §Shared Architecture — ARCH-01 through ARCH-07 are the
  acceptance criteria for this phase; ARCH-04 is already complete.
- `.planning/ROADMAP.md` §Phase 3 — goal, requirements, and the five success criteria.
- `.planning/STATE.md` — current position and the Phase 2 carry-forward blockers CR-01 and
  WR-01..WR-04.
- `.planning/phases/01-repository-foundation-and-policy-gate/01-CONTEXT.md` — D-05
  (nested `AGENTS.md` only on real divergence), D-27 (ADR numbering is sequential and
  permanent).
- `.planning/phases/02-toolchain-truth/02-CONTEXT.md` — D-07 (delete the smoke project in
  Phase 3), D-09/D-12 (library metadata and version location), D-14 (N16R8 overrides),
  D-15 amended (`extern "C"` headers, pure-C library sources).
- `.planning/phases/02-toolchain-truth/02-REVIEW.md` — CR-01 (partitions CSV),
  WR-01 (tests hard-read the smoke project), WR-03 (duplicated library version strings).

### Technical research
- `.planning/research/ARCHITECTURE.md` §Layer Dependency Rule and §Component
  Responsibilities — the `common → port`, `adapter → port`, `homework → common + port +
  one adapter` edges and each library's "must never".
- `.planning/research/ARCHITECTURE.md` §Pattern 1: Ports and Adapters in C — the
  function-pointer struct shape, `ctx`, and host fakes.
- `.planning/research/ARCHITECTURE.md` §Flow 4: Tests — the `tests/` native project and its
  place above simulation and HIL.
- `.planning/research/PITFALLS.md` C3 (dependency-rule drift), C8 (framework leaks into
  native tests), C12 (mocks drifting from the real contract), C15 (premature shared
  abstraction).
- `.planning/research/SUMMARY.md` — the consolidated architecture and the allowed-edge
  list.
- `.planning/research/STACK.md` §1.4–1.6 — `symlink://` semantics, LDF, `lib_ignore`, and
  the compilation database. **Line 248 (`port depends on common`) is superseded by
  D-01 and D-03; do not follow it.**

### Repository rules and existing decisions
- `AGENTS.md` — Conventional Commits, generated-file rules, and the repository layout.
- `docs/decisions/0001-monorepo-with-independent-projects.md` — one independent project per
  homework.
- `docs/decisions/0002-ports-and-adapters-no-universal-hal.md` — the accepted ports-and-
  adapters decision; D-02 supersedes only its dependency-rule sentence.
- `docs/decisions/0007-symlink-shared-libraries.md` — `symlink://` and the smoke project's
  scheduled removal.
- `docs/decisions/README.md` — the ADR status index that ADR-0008 must join.
- `.pre-commit-config.yaml` — the local hook surface the architecture check joins.
- `platformio.shared.ini` — `[native_unity]` and the N16R8 sections; its partitions path
  changes under D-18.

### External references
- `https://alistair.cockburn.us/hexagonal-architecture` — ports belong to the core;
  adapters depend inward.
- `https://docs.aws.amazon.com/prescriptive-guidance/latest/hexagonal-architectures/overview.html`
  — source dependencies point only inward; a port does not live in the adapter.
- `https://www.volatileint.dev/posts/dependency-inversion-c/` — vtable struct owned by the
  consumer, implemented by adapters.
- `https://wingman-sw.com/papers/SOLIDInC.grenning.v1r0.pdf` — DIP and ISP in embedded C.
- `https://www.smallstepsystems.com/ports-and-adapters-architecture-the-pattern/` —
  I/O-free core; outside depends on inside.
- `https://docs.platformio.org/en/latest/librarymanager/dependencies.html` — why a
  manifest `dependencies` field resolves through the registry (basis for D-03).
- `https://docs.platformio.org/en/latest/advanced/unit-testing/structure/shared-code.html`
  — the top-level `tests/` project pattern.
- `https://github.com/BabbleSim/native_simulator/blob/main/docs/Design.md` — simulated
  deterministic time as the basis for the 20-run proof.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `scripts/check_policy.py` and `scripts/check_pr_templates.py` — the established shape for
  a deterministic checker with a `--check`-style contract and `scripts/tests/` coverage;
  `check_architecture.py` joins this family.
- `scripts/tests/` + `python3 -m unittest discover -s scripts/tests -v` — the repository
  gate the determinism test joins.
- `.pre-commit-config.yaml` — already carries local hooks; the architecture check is added
  as one more local entry.
- `platformio.shared.ini` `[native_unity]` — the existing native environment block with
  `-std=c11`, `-Wall`, `-Wextra`; `tests/` consumes or extends it.
- `lib/*/library.json` — the five manifests that gain `0.2.0` and keep a single source for
  the version.
- `homeworks/0_0-toolchain-smoke/platformio.ini` — the working composition example of
  `common` + `port` + one adapter; it is deleted in this phase, so copy any needed pattern
  into `tests/` before removal.

### Established Patterns
- Policy/configuration as committed data plus a deterministic checker.
- Generated files stay gitignored; `.pio/` and `compile_commands.json` are already
  ignored.
- Repository artifacts are English; Conventional Commits with a phase or homework scope.
- Each shared library is a PlatformIO library with `name`, `version`, `build.srcDir`, and
  `build.includeDir` in `library.json`.

### Integration Points
- `lib/port/include/port/*.h` — the five contracts consumed by `common`, adapters, `host`,
  and `tests/`.
- `lib/common/include/common/*.h` — `ring_buffer`, `timing`, `crc`/`hex`.
- `lib/host/include/host/*.h` + `lib/host/src/*.c` — deterministic fakes for all five
  contracts.
- `tests/platformio.ini` + `tests/test/` — the native Unity project.
- `scripts/check_architecture.py` + `.pre-commit-config.yaml` — the enforcement pair.
- `partitions/default_16MB.csv` + `platformio.shared.ini` — the permanent partitions path.
- `docs/decisions/0008-*.md` + `docs/decisions/README.md` — the direction record.

</code_context>

<specifics>
## Specific Ideas

- The user asked for additional research before committing to a dependency direction. The
  decision was made only after comparing ADR-0002, the research documents, and the
  hexagonal/DIP sources; the contradiction between them is now resolved explicitly in
  D-01/D-02.
- The user's main concern was that `common` must not become a dumping ground for
  homework-specific functions. D-12 records that domain logic stays in the homework and
  shared code is promoted only after real duplication.
- The user consistently chose the option that avoids speculative interfaces: contracts
  for all five ports but implementations only where a consumer exists; a proven-minimum
  `common`; no `dependencies` field; formatting deferred to Phase 6.
- The discussion happened in Ukrainian; the planning artifacts are English per the
  project language constraint.

</specifics>

<deferred>
## Deferred Ideas

- I2C and SPI framework adapters in `lib/arduino` and `lib/espidf` — the first homework
  that needs them.
- `fixed_point`, a generic state machine, and a calculations module in `lib/common` —
  after real duplication (Pitfall C15).
- `check_architecture.py` and the native suite in CI — Phase 8.
- Generated `platformio.shared.ini` and its `--check` drift gate — Phase 5.
- Pre-push hooks — Phase 6.
- clang-format configuration and the mass reformat — Phase 6.
- A nested `lib/AGENTS.md` — only if the dependency rule genuinely diverges from the root
  rulebook (Phase 1 D-05).
- Homework-domain logic such as the police-flasher state machine — Phase 11, inside the
  homework.

</deferred>

---

*Phase: 3-Shared Core and Dependency Rule*
*Context gathered: 2026-10-24*

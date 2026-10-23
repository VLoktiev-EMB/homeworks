---
phase: 3
reviewers: [codex-glm, codex-beam, antigravity]
reviewed_at: 2026-10-23T21:59:39Z
plans_reviewed:
  - .planning/phases/03-shared-core-and-dependency-rule/03-01-PLAN.md
  - .planning/phases/03-shared-core-and-dependency-rule/03-02-PLAN.md
  - .planning/phases/03-shared-core-and-dependency-rule/03-03-PLAN.md
  - .planning/phases/03-shared-core-and-dependency-rule/03-04-PLAN.md
  - .planning/phases/03-shared-core-and-dependency-rule/03-05-PLAN.md
  - .planning/phases/03-shared-core-and-dependency-rule/03-06-PLAN.md
  - .planning/phases/03-shared-core-and-dependency-rule/03-07-PLAN.md
  - .planning/phases/03-shared-core-and-dependency-rule/03-08-PLAN.md
  - .planning/phases/03-shared-core-and-dependency-rule/03-09-PLAN.md
models:
  codex-glm: "glm-5.3-flash:cloud (reasoning=high)"
  codex-beam: "beam:cloud (reasoning=high)"
  antigravity: "gemini-3.8-flash-high"
model_sources:
  codex-glm: "pinned"
  codex-beam: "pinned"
  antigravity: "pinned"
---

# Cross-AI Plan Review — Phase 3

<!-- gsd:plan-revision-conflicts:begin -->
## Plan-Revision Conflicts

_None — this is the first review of Phase 3; no prior plan-revision conflict entries exist._
<!-- gsd:plan-revision-conflicts:end -->

> Note: codex-glm and codex-beam share the codex adapter; their consensus is cross-model, not cross-tool.

## Codex Review (codex-glm)

Now I have enough evidence. Here is the structured review.

# Phase 3 Plan Review

**Context verified:** I read `platformio.shared.ini`, `homeworks/0_0-toolchain-smoke/platformio.ini`, the three shared-library configs, the two test modules, test suite, `scripts/pio/compiledb.py`, the pre-commit config, existing checkers, and the ADR/index structure. Verified environment: PlatformIO Core 6.2.0, Python 3.13.13, pre-commit 4.7.0. The Phase 3 plans are substantially evidence-grounded and tightly scoped. The one major design issue I found is in the architecture checker’s classifier.

---

## 03-01

### Summary

The plan proves the core architecture with a single traceable slice: `port` time contract, `common` timing, `host` fake clock, and a host-only Unity suite. It correctly uses `test_dir = test`, `test_framework = unity`, pinned Unity, and symlink dependencies.

### Strengths

- **Good**: The test command and configuration align with the Phase 2 `symlink://` pattern visible at `smoke.platformio.ini` lines 7-10.
- **Good**: The build-flag repetition is justified by actual config semantics; the shared native config is at `platformio.shared.ini:31-37`.
- **Good**: The tests directory is a "subdirectory" project, reducing auto-discovery risk.
- **Good**: `tests/src/main.c` is a smart compilation probe to ensure shared sources are actually linked and compiled.
- **Good**: Strong named tests for wraparound, debounce boundaries, NULL safety, and independent fake instances.

### Concerns

- **MEDIUM — Unity pin verification is brittle.** The verify uses `! grep 'Installing throwtheswitch/Unity @ \^'` and would still appear to pass when Unity is cached and no install line is printed at all. Cite: `.planning/phases/03-shared-core-and-dependency-rule/03-01-PLAN.md:239-262`.
- **LOW — test count thresholds.** The acceptance criteria require at least 8 and later 12 passing rows, but they are counted across the run, not per suite. If a suite accidentally fails entirely while another expands, a threshold could still pass.
- **LOW — time contract test is indirect.** The port-time contract is exercised through `common` and a fake rather than through a direct `test_time_ctx_reaches_callback`.

### Suggestions

- Assert that the captured log explicitly contains `throwtheswitch/Unity@2.6.1` when a first install occurs, and explicitly confirm the installed manifest under `tests/.pio/libdeps/native/Unity/library.json` reports version `2.6.1`.
- Move the direct fake-time usage to a separate Unity app or suite to make the 20-run digest more resilient to partial failures in one suite.
- Add a direct `test_time_ctx_reaches_callback` to the contract suite in a later plan.

### Risk Assessment

**LOW** — the design is sound. The main risks are verification brittleness, not the intended functionality.

---

## 03-02

### Summary

The plan records the resolved dependency direction, supersedes only one sentence of ADR-0002, and fixes a real documented quick-start bug in `AGENTS.md`. It is well aligned with the repository's permanent ADR constraints.

### Strengths

- **Good**: `ADR-0008` is correctly treated as a permanent decision record.
- **Good**: The plan correctly targets the broken quick-start command at `AGENTS.md:25`, which currently says `pio test -e native`.
- **Good**: `scripts/tests/test_adrs.py` already enforces contiguous ADR numbering, frontmatter, section order, chosen-option text, and index-title agreement.
- **Good**: The ADR will be indexed at exactly `| 0008 |...| accepted | 2026-10-24 |`.

### Concerns

- **LOW — title/index equality is enforced but prose content is partially judged.** The mechanical suite cannot prove the supersession clause was carefully restricted beyond the dependency-rule sentence. This is acknowledged.
- **LOW — `AGENTS.md` step 2 remains `pio run`, which is generic.** This is intentional but might need a follow-up once the smoke project is deleted so native test/build is runnable as a canonical command.

### Suggestions

- Add a verify that ADR-0002 remains unchanged by comparing its dependency-rule sentence before/after.
- Verify that `AGENTS.md` remains at or below 300 lines explicitly, not just through the suite.

### Risk Assessment

**LOW** — good documentation hygiene and a real fix for an existing broken command.

---

## 03-03

### Summary

The plan completes four contracts — GPIO, I2C, SPI, log — as bus/function-pointer-level C interfaces. The suite proves vtable callability, ctx plumbing, and bounded local implementations. The design avoids whole-driver abstractions.

### Strengths

- **Good**: All five contract headers planned, matching ARCH-01.
- **Good**: I2C/SPI are deliberately narrow: address, buffer, length; no register map, device struct, or native-handle accessor.
- **Good**: The `port_status_t` vocabulary is used uniformly where sensible; log/time returns are exceptions with documented rationale.
- **Good**: Tests exercise ctx identity and independence, preventing a fake or callback from silently owning state.

### Concerns

- **MEDIUM — the plan claims "covers all five contracts" but time contract is not directly covered by `test_contracts.c`.** The task suite contains GPIO, I2C, SPI, log, and status-value tests, but the time vtable call is only proved indirectly through 03-01 tests. Cite `.planning/phases/03-shared-core-and-dependency-rule/03-03-PLAN.md:210-238`.
- **LOW — GPIO pin width.** `uint8_t` pin parameter is fine for course scale but not explicitly justified with board constraints.
- **LOW — `INPUT_PULLUP` only.** No input-pull-down member. This may be sufficient for ESP32-S3 coursework but could require a later API expansion.

### Suggestions

- Add a direct call-through test for `port_time_t` in `test_port_contracts` with a local fake callback.
- Add a short comment in `gpio.h` explaining why `uint8_t` pin width is acceptable for this phase.
- Document whether input-pull-down will require an API extension later.

### Risk Assessment

**LOW/MEDIUM** — the design is intentionally narrow and solid, but the claim of "suite covers every contract" has a small gap.

---

## 03-04

### Summary

This plan delivers `ring_buffer`, CRC-16/CCITT-FALSE, and hex codecs. Each is pure, allocation-free, and caller-owned, tested with deterministic Unity cases.

### Strengths

- **Good**: The module set matches the "proven minimum" decisions and avoids speculative abstractions.
- **Good**: The ring buffer uses caller-supplied storage and explicit `count` semantics.
- **Good**: CRC uses the standard check value `0x29B1`, incremental equivalence, and integrity-only disclaimers.
- **Good**: Hex has capacity checks and strict decoding semantics.

### Concerns

- **LOW — ring buffer's `init` and "safe value" semantics.** It says other functions return a safe value if the struct or storage is uninitialized, but there is no explicit `initialized` flag. A guard against NULL storage and zero capacity is easy to reason about; an unspecified uninitialized state is not.
- **LOW — hex failure convention.** The plan says on failure leave `*out_length` untouched or set it to zero and then choose one. This is vague at plan time; it should be fixed in the plan to prevent drift.
- **LOW — no automated non-blocking check until 03-08.** This is acknowledged.

### Suggestions

- Add an explicit `bool initialized` field or define exact preconditions for all other ring-buffer calls.
- Decide now that on failure `*out_length` is set to `0`, not left untouched.
- Add a test that `common_hex_decode` and `common_hex_encode` do not write any output bytes when the capacity is insufficient.

### Risk Assessment

**LOW** — the primitives are well-scoped and testable.

---

## 03-05

### Summary

This plan completes test doubles for all five contracts. The fakes are deterministic, bounded, allocation-free, and scriptable to fail. The design is appropriate for the 20-run proof and host-only test architecture.

### Strengths

- **Good**: The fakes return real contract types, so signature drift causes a compile error.
- **Good**: Named bounds, bounded storage, and explicit overflow behavior avoid silent unbounded writes.
- **Good**: The log fake counts dropped lines instead of overwriting, which is a clear deterministic pattern.
- **Good**: Tests cover normal paths, bounds, injected failures, and multi-instance isolation.

### Concerns

- **MEDIUM — I2C fake's address model is very coarse.** It records the last address but stores one 32-byte loopback buffer globally, so two different devices at different addresses cannot be modeled. That is acceptable for the course's minimal scope but may miss future behavior.
- **LOW — the `fake_gpio` `configured` semantics are not fully specified.** The task says `write` marks configured, but does not say `set_mode` does. The name is ambiguous.
- **LOW — duplicate fake test names.** Task 1 has `test_fakes_return_the_real_contract_types`, and Task 3 has `test_all_fakes_expose_the_real_contract_types`. Probably harmless but can be clarified.

### Suggestions

- Keep I2C as a loopback fake but document that it is not a multi-device simulator.
- Specify whether `set_mode` also updates `configured` in `host_fake_gpio`.
- Rename the fake-type compile-compatibility test to a more specific name to avoid confusion between Task 1 and Task 3.

### Risk Assessment

**LOW** — fakes are bounded and deterministic. The I2C simplification is acceptable and documented.

---

## 03-06

### Summary

This plan implements time, GPIO, and logging adapters for Arduino and ESP-IDF. The contract set is honest and avoids speculative I2C/SPI adapters. The proof is compile-level against the existing smoke project. Good use of CDB evidence.

### Strengths

- **Good**: Uses the smoke project as a real compile harness, as `smoke.platformio.ini` already lists the adapters at lines 14-24.
- **Good**: Uses CDB evidence via `scripts/pio/compiledb.py` and points at `$PROJECT_DIR/compile_commands.json`.
- **Good**: The public adapter headers contain only port types and factories; framework types are excluded.
- **Good**: Arduino logging avoids a level-gated macro that might compile to nothing.

### Concerns

- **MEDIUM — the smoke project will be deleted in 03-07.** 03-06 relies on `homeworks/0_0-toolchain-smoke` as a target build harness. That ordering is correct, but 03-06 should leave no permanent evidence dependence on it beyond CDB output; it must be clear that the CDB path is temporary. Cite `.planning/phases/03-shared-core-and-dependency-rule/03-06-PLAN.md:171-186` and `.planning/phases/03-shared-core-and-dependency-rule/03-07-PLAN.md:206-245`.
- **LOW — no run-time on-target test of adapters.** This is acknowledged and out of scope.
- **LOW — the `esp_log_write` path could be fragile across future SDK changes.** Probably fine with the pinned ESP-IDF.

### Suggestions

- Record the CDB files produced by 03-06 but do not let any permanent test read the smoke project.
- Add a small helper function `port_status_t map_esp_err(esp_err_t)` to reduce repeated mapping logic if the code grows.
- Document that hardware behavior is not in scope, as in the edge probe.

### Risk Assessment

**LOW/MEDIUM** — target compile proof is enough for this phase, but its dependency ordering against smoke project deletion must be preserved.

---

## 03-07

### Summary

This plan correctly sequences carry-forward cleanup: move the partition CSV and refactor test fixtures before the smoke project is deleted, then delete the smoke project in a dedicated commit, then retire stubs and bump manifests to 0.2.0. It is one of the strongest plans in this set.

### Strengths

- **Good**: The partition path is resolved relative to a project directory, as confirmed by `platformio.shared.ini:10,24` and shared config semantics; the plan's `../../partitions/default_16MB.csv` is correct for homework-depth projects.
- **Good**: `git mv` is explicitly used to avoid copy duplication.
- **Good**: `test_pio_scripts.py` currently hard-reads the smoke project at lines 38 and 39, as flagged in Phase 2; the plan correctly refactors it onto `tests/platformio.ini`.
- **Good**: The plan correctly distinguishes WR-04 as not addressed rather than silently claiming closure.
- **Good**: It explicitly removes the stubs and the duplicate version strings.

### Concerns

- **MEDIUM — the partitions existence test uses an artificial `homeworks/1_1-example` path.** This keeps the depth-relative semantics, but it may be clearer to resolve the path relative to any known actual homework-style depth and assert that the path `partitions/default_16MB.csv` exists under the repo root.
- **LOW — deletion commit is separate.** The task says the deletion is a standalone `chore(03)` commit, which is correct but hard to enforce by the automated verify.
- **LOW — `tests/` remains as the only PlatformIO project after smoke deletion.** That is intended but should not be referenced as a "homework project."

### Suggestions

- Consider resolving the partition path in the test as `(REPO_ROOT / "partitions" / "default_16MB.csv")` plus an explicit relative resolution test to avoid artificial fixture paths.
- Add a test asserting `homeworks` has zero tracked entries only after the dedicated commit.
- Ensure after 03-07 that no script or `.gitignore` fixture uses `homeworks/0_0-toolchain-smoke/...`.

### Risk Assessment

**LOW** — clean carry-forward handling and safe deletion order.

---

## 03-08

### Summary

This plan wires the dependency rules into a textual checker with allowlist semantics and adds header contract tests plus a pre-commit hook. This is the most important enforcement plan. I found a critical gap in the include classifier.

### Strengths

- **Good**: The checker follows the family style of `check_pr_templates.py` (docstring, exit codes, `CheckError`, PASS/FAIL blocks), evidenced at `scripts/check_pr_templates.py:55-76` and `219-220+`.
- **Good**: It includes the pre-commit hook with correct `files:` and `pass_filenames: false`.
- **Good**: Strong negative fixture matrix, missing tree handling, stale allowlist, and read-only/idempotent real-tree test.
- **Good**: `scripts/pio/compiledb.py` and `.pre-commit-config.yaml` show the existing local hook surface the plan extends.

### Concerns

- **HIGH — the textual include classifier can be bypassed by embedded `../` traversal.** The plan classifies only includes beginning with `../` or `./`, then uses the first segment. An include like `#include "common/../arduino/include/arduino/time.h"` from a `common` source would be classified as a `common` self-edge and allowed, even though it actually resolves into `arduino`. Cite `.planning/phases/03-shared-core-and-dependency-rule/03-08-PLAN.md:159-167`. This is exactly why the checker must not rely solely on leading `../`.
- **MEDIUM — absolute include names are not explicitly rejected.** An absolute include path could resolve outside the tree and evade the edge classification. Cite plan 03-08 lines 159-161.
- **MEDIUM — `C_STANDARD_HEADERS` is too broad for `lib/common` and `lib/port`.** The planned allowed set includes `<stdio.h>` and `<stdlib.h>`. Even though the modules themselves are minimal, the external allowlist is the mechanical contract; future code could pass the include scan while still not being allocation-free or output-only.
- **LOW — comment stripping can be false-positive-prone on string literals containing `//`.** Fine for now, but worth a warning.
- **LOW — `allowlist.json` schema validates strings but not nonempty reason.** This weakens the auditability contract.

### Suggestions

- Reject all include names containing any `..` segment, not just leading `../`. This is a minimal, safe fix.
- Reject absolute include paths or classify them as escapes.
- Restrict the standard-header allowlist to the headers actually used by `port`, `common`, and `host` in this phase — likely not `<stdio.h>` or `<stdlib.h>`.
- Require nonempty allowlist `reason`.
- Add a negative fixture specifically for `common/../arduino/...` and one for an absolute include.

### Risk Assessment

**HIGH as written** due to the classifier bypass, but this is fixable with a small classifier change and additional fixtures.

---

## 03-09

### Summary

This plan provides the purity and determinism proofs. It checks compile-command entries for host compilers only, no framework/toolchain paths, and uses a 20-run normalized Unity digest. It is a strong validation plan for the core phase.

### Strengths

- **Good**: CDB assertions plus a negative framework-include fixture provide two-sided evidence.
- **Good**: The digest uses per-line match, dropping variable paths, times, and messages.
- **Good**: It asserts nonzero test rows, zero failure, all 20 digests identical.
- **Good**: It includes a durable `lib_deps`-not-reaching-firmware guard in `ConfigurationGuardTests`.

### Concerns

- **MEDIUM — the negative fixture copies `lib/`, `tests/`, `platformio.shared.ini`, and `compiledb.py`.** This works but omits an explicit symlink resolution test. Since `tests/platformio.ini` uses relative paths, copying will work; still, a future refactor to absolute paths could silently break. Suggest an explicit containment assertion in the fixture.
- **MEDIUM — determinism run could be slower than the estimate.** 20 runs of PlatformIO may still be 3-5 minutes even with a warm build. Fine, but the plan's 10-15 seconds estimate is optimistic.
- **LOW — `ConfigurationGuardTests` duplicates part of 03-08's checker.** Redundancy is acceptable but should be intentional.
- **LOW — regex `TEST_LINE` depends on Unity/PlatformIO exact formatting.** It is validated in research, but could be brittle to future output changes.
- **LOW — no explicit test that all test files are scanned by the digest, only minimum-suite coverage.** Could strengthen by asserting `test_common_ring_buffer`, `test_common_crc`, `test_common_hex`, `test_port_contracts`, `test_host_fake_time`, and `test_host_fakes` all appear.

### Suggestions

- Assert the compiled file list also includes `tests/src/main.c`.
- Assert the digest includes at least the expected six suites, not just two.
- In the copy fixture, assert the temp root is resolved and all paths stay inside it.
- Record actual wall time in summary without reducing `RUNS = 20`.

### Risk Assessment

**LOW/MEDIUM** — good proof strategy. The largest risk is execution time and format brittleness, not architectural soundness.

---

# Cross-Plan Observations

- The wave ordering is sound: 03-01 proves the spine, 03-02 locks the direction, then contracts, primitives, fakes, adapters, cleanup, enforcement, and proofs follow in a sensible order.
- The phase's carry-forward items are correctly sequenced.
- The most important improvement is to tighten `scripts/check_architecture.py`'s classification before implementation; this is a small but important change.

# Overall Risk Assessment

**MEDIUM overall**. The core architecture and cleanup work are solid and thoroughly verified; the primary issue is checker bypass via embedded path traversal and absolute include names in 03-08. Fix that classifier and add two negative fixtures, and the plan set becomes high quality.

---

## Codex Review (codex-beam)

# Cross-AI Plan Review: Phase 3 — Shared Core and Dependency Rule

Reviewed against the live repository state (phase currently at the Phase 2 ship point: `lib/` contains only the five Phase 2 stub libraries with `0.1.0` manifests, `scripts/tests/test_pio_scripts.py` still hard-reads `homeworks/0_0-toolchain-smoke/`, `platformio.shared.ini` uses `board_build.partitions = default_16MB.csv`). All claims below are checked against those files, not against the plan text alone.

## 03-01

**Summary:** Solid tracer slice. It proves the three riskiest structural assumptions (top-level `tests/` project, `common → port` linkage, fake-time-driven timing) in one commit, with a concrete `platformio.ini` that fixes the two verified pitfalls (inherited `extra_scripts` resolves against the project directory; `extends` replaces list values). The ping-back to `tests/src/main.c` as a "compilation probe" is the one part that rests on a questionable PlatformIO/LDF claim.

**Strengths**
- `tests/platformio.ini` as quoted matches the verified extra-config and flag-override pitfall handling from `03-RESEARCH.md` (Pitfalls 1 and 3).
- `common_debounce_t` as a three-field struct (`stable`, `candidate`, `candidate_since_ms`) is justified in the plan text and avoids the "no pending change vs. change at time zero" ambiguity.
- Unity pinned as `throwtheswitch/Unity@2.6.1` directly addresses Pitfall 9 and the verify rejects an unpinned range line.
- `port_time_t` as a consumer-owned vtable with a borrowed `const` pointer matches ADR-0008's eventual contract; positional aggregate initialization (`{ arduino_now_ms, NULL }`) avoids the C99 compound-literal/C++20-designated-initializer trap (Pitfall 4, which research reproduced with clang 21).

**Concerns**
- **MEDIUM — "compilation probe" rests on LDF semantics that are not actually load-bearing.** The plan says without `tests/src/main.c`, "the Library Dependency Finder compiles nothing and the database is `[]`". But the Unity test files under `tests/test/test_common_timing/` already `#include "common/timing.h"`, `"port/time.h"`, `"host/fake_time.h"`, so LDF already pulls all three libraries at `pio test` time. The `main.c` is only needed for the `pio run -t compiledb` database to be non-empty — i.e. it is needed for the Phase 3 *purity proof* (03-09), not for the Phase 3 *native suite* (SUCCESS criterion 2). Stated purpose and actual need differ; this should be (a) scoped as "needed only for the purity gate" or (b) paired with `test_build_src = false` so it is not double-linked into test apps, which the plan does say — but the stated "force the LDF to compile shared libraries" framing overstates it. Mitigation: keep `test_build_src` default false; the probe is harmless, but the rationale in the summary should be corrected.
- **LOW — `-Werror` global risk on Unity (A9).** The plan has a fallback (drop `-Werror` only), but the fallback changes the witness (`build_flags` no longer contains `-Werror`) and would silent-fail the `python3 -c` config assertion only if the verifier checks for `-Werror` — it does not (it checks the three warning flags). Acceptable.
- **LOW — `tests/src/main.c` defines `main()`.** With `test_build_src = false` it is not built in any test app, so `main` does not collide with Unity's. Correct, but undocumented; worth a one-line comment because the file looks like a second application.
- **LOW — `PORT_ERR_NOT_SUPPORTED` etc.** status vocabulary is defined in 03-01 while other contracts arrive in 03-03; that ordering is fine and Task 1's header assertions assert it.

**Suggestions**
- Correct the stated rationale for `tests/src/main.c` to "needed for the `pio run -t compiledb` purity database; not needed for the test suite because the test includes already pull the libraries".
- Add explicitly `test_build_src = false` to `tests/platformio.ini` (do not rely on the default), so a future change to the default does not accidentally link `main.c` into every test app.

**Risk Assessment:** LOW. All load-bearing mechanisms were reproduced on the actual machine by the plan author; the only gap is rationale vs. mechanism, not correctness.

## 03-02

**Summary:** Clean documentation-only plan: an accepted MADR for the direction (which is also the user's locked D-01), a contiguous index row, and the fix of the one documented, actually-broken command (`pio test -e native` → `pio test -d tests -e native`). Its assertions map directly onto `scripts/tests/test_adrs.py` and `scripts/tests/test_agents_md.py`, which I verified define the eight MADR sections, the five frontmatter keys, the chosen-option `Chosen option: ` opener, and the index-title agreement. The one thing to scrutinize is whether the ADR prose stays at ≤300 lines of AGENTS.md (tested) and whether ADR-0008 really "supersedes only" the dependency-rule sentence — which is a judgment, not a test (correctly listed as a prohibition with `verification: judgment`).

**Strengths**
- ADR content contract (8 MADR sections in order, ≥2 options with Good/Neutral/Bad bullets) matches `MADR_SECTIONS` and the parsing in `test_adrs.py` exactly. The `Chosen option: "Common depends on port, with consumer-owned contracts"` opener satisfies the test's stated requirement.
- Supersession clause ("supersedes only the dependency-rule sentence of ADR-0002") is the formally safe thing; ADR-0002 is not edited, so published cross-references stay stable (D-27).
- Identity policy (public handle only, email scan in `test_adrs.py`) is honored. The row title `Common depends on port; ports are consumer-owned` must be byte-identical to the `# ` heading — correctly called out as a judgment-checked contract.

**Concerns**
- **LOW — manual-only supersession claim.** `test_adrs.py` cannot verify "supersedes only one sentence"; the prohibition explicitly marks this `verification: judgment`. There is no assertion that ADR-0002's text is unchanged from a pre-plan baseline. Fine, but the reviewer should diff `git show main:docs/decisions/0002-...md` against post-plan to confirm; this is implied, not automated. I'd call it a gap in "what must be true" but an acceptable one for a docs plan.
- **LOW — exact row string.** The verify regex includes `| 0008 | Common depends on port; ports are consumer-owned | accepted | 2026-10-24 |`. Markdown table cells with trailing spaces parse fine.

**Suggestions**
- Add a non-trivial consistency side-effect: keep `0007`'s scheduled-deletion language pointing at `Phase 3` — it does, and 03-07 task 2 explicitly preserves it. (Verified: `docs/decisions/0007-symlink-shared-libraries.md` is untouched.)

**Risk Assessment:** LOW.

## 03-03

**Summary:** Correctly completes the five-port surface without any implementation (`port/` stays header-only), with bus-level I2C/SPI (address + buffer + length, no register/page/device concept, no `port_get_native_handle`). The most valuable content here is the shape judgement being pinned to a manual review note, with the mechanical contract (C-only includes, extern "C" guard) left to 03-08's header suite.

**Strengths**
- "abstract the bus, not the driver" is made concrete and testable-as-a-shape: I2C write/read/combined, SPI transfer/write, with chip-select/clock mode/frequency owned by the adapter and chip-select documented as bus configuration.
- Logging's `write` returns `void` with a documented exception, matching Assumption A1 (a failed log write must never alter control flow) — a genuine embedded-C design decision, recorded.
- `port_status_t` is the single vocabulary (D-09) with at least five members; confirmed in real `port/status.h` (does not exist yet — will be created 03-01).
- The note that designated initializers fail under `-pedantic-errors` appears and is cited.

**Concerns**
- **MEDIUM — the "exactly one adapter per homework" rule from D-15 is verified only in 03-08, not here.** That's consistent with the wave plan anyway.
- **LOW — GPIO mode `PORT_GPIO_INPUT_PULLUP` exists but no "no-pull-up / no-pull-down" default is separately enumerated; pull direction is a flag, not an enum.**
- **LOW — I2C does not model repeated-start or per-call timeout (Assumption A4); this only matters when Arduino/ESP-IDF adapters for I2C/SPI eventually land, which is deferred. Plan explicitly records the A4 risk.**
- **LOW — `host` doubles are allocated and never bounds-checked against `%SIZE_MAX` in I2C/SPI for extremely large buffer lengths; loopback allows apparent `out_size` bytes but checks `length > capacity`. Fine for a course.**

**Suggestions**
- No changes required; shape judgements remain for 03-08 manual review as documented in 03-VALIDATION.md's manual-only table.

**Risk Assessment:** LOW-to-MEDIUM (shape judgement risk for ARCH-07, mitigated by the deferred-consumer rule and 03-06 explicitly skipping I2C/SPI adapters).

## 03-04

**Summary:** Delivers the three non-timing primitives of the "proven minimum" (D-11), explicitly deferring `fixed_point`, generic state machine and calculations modules. CRC-16/CCITT-FALSE with the standard check value 0x29B1, hex with capacity reporting, ring buffer with `count` as the authoritative full/empty discriminator (not the `head == tail` sentinel — correctly avoids the sentinel ambiguity). Scope discipline against C15 is good.

**Strengths**
- The `common_debounce_t` lives in 03-01 and is preserved; space for timing is fine.
- "`common` modules are allocation-free, caller-owned, take pointers + lengths" satisfies ARCH-02.
- Ring buffer `count`-authoritative (avoids the full-vs-empty ambiguity that `head == tail` creates) — matches the Pitfall register guidance.
- `hex` reject odd length + non-hex + insufficient capacity without truncation; encode emits lowercase, null-terminates when capacity allows.
- CRC disclaimer ("data integrity, not authentication") is codified in header text — Security Domain ASVS A6 concern.

**Concerns**
- **MEDIUM — `common` has no port dependency used by these three modules at all.** Ring buffer, CRC and hex are pure C with no `port` include. That means `_common → port_` is the dependency edge but these three modules do not actually exercise it. The "common genuinely exercises port" requirement is satisfied by `_timing_` (03-01) and by the native build. Acceptable.
- **LOW — CRC `NULL` pointer + non-zero length returns the unchanged input CRC** — silently accepted. Given D-09 used for non-port error behaviour, maybe `common_crc16` should return 0 on NULL? On the other hand the function cannot return an error (signature fixed). The plan's stated behaviour is a defensible contract. Should be documented explicitly in the header (it is: "Treat a NULL pointer with non-zero length as a caller error and return the unchanged input CRC"). Asymptotically fine.
- **LOW — hex decode without a pre-allocated target size check uses `out_size >= length/2`**, i.e. allows exactly `length/2` bytes. Good.

**Suggestions**
- None substantive.

**Risk Assessment:** LOW. Scope alignment is excellent.

## 03-05

**Summary:** Completes the deterministic fake layer for all five contracts (D-07) plus `test_host_fakes/test_host_fakes.c` to exercise all. Fixed 64-entry GPIO array, 32-byte I2C loopback, 32-byte SPI buffer, 32-line log sink with drop counter. Each returns the *real* contract type and is constructible only compositionally (positional), so mock drift is a compile error (Pitfall C12). The `fail_next` setter allows error-path tests without a framework.

**Strengths**
- Positional construction (not designated initializers) keeps fakes C++-composable too (Pitfall 4).
- Bounded storage with named constants for each bound — A2 assumption tracked.
- One-shot `forced_status` returned and cleared (recorded before). Clean contract.
- Log sink stores up to 32 lines, truncates >64 chars safely, counts drops instead of overflowing.
- `lib/host` includes only `port` and C standard headers (D-17) — `lib_deps` restricted to `tests/` only; checker rules come from 03-08 for the durable form.

**Concerns**
- **MEDIUM — `lib/host` includes a "recording GPIO double" which is mostly-but-not-entirely a recording stub.** It implements `set_mode`, `write`, `read`, records `writes`/`reads`, enforces pin bound, supports fail-inject. No production policy. But whether "records, loops back, or fails on request" truly describes fakes-and-not-policies is only `verification: judgment` — consistent with D-10 prohibition #1, and not automatable. Fine issue, correctly disclosed.
- **LOW — `host_fake_i2c_preset` writes into the loopback buffer; read-back copies it.** Combined transfer stores TX then copies the stored buffer to RX — I notice this actually models only the *already stored* data, not negotiated state. Documented as "one transaction without modelling a device" — accepted.
- **LOW — the `test_all_fakes_expose_the_real_contract_types` test in task 3 explicitly types `port_time_t`, `port_gpio_t`, `port_i2c_t`, `port_spi_t`, `port_log_t` into variables.** This is the build-time drift check; good.

**Suggestions**
- No changes required.

**Risk Assessment:** LOW. D-07 requirements covers ARCH-03.

## 03-06

**Summary:** Three-contract thin adapters on Arduino and ESP-IDF, exactly what D-08 defers (no I2C/SPI). Public headers expose only `port` vtable and a single factory; sources are `.c`, include framework header first then project header, and translate without policy. Build evidence is the CDB under the pinned toolchain from `homeworks/0_0-toolchain-smoke`.

**Strengths**
- Include-order convention (framework header in `< >`, blank line, own project header in `" "`) matches `lib/arduino/src/arduino_adapter.c` and `lib/espidf/src/espidf_adapter.c` house style, verified present in the tree.
- Arduino logging via `log_printf` unconditionally avoids the level-gated silent-failure mode (Pitfall 5).
- ESP-IDF GPIO fills `gpio_config_t` completely with all fields (pin_bit_mask, mode, pull_up_en, pull_down_en, intr_type) — single point where wrong mapping or a missing field would create a runtime fault.
- `port_status_t` instead of `esp_err_t` propagation matches D-09.

**Concerns**
- **HIGH — adapters will not actually compile in the smoke project as its `lib_deps` stands.** The smoke project's `platformio.ini` declares only `common`, `port`, `host` in `lib_deps`. The adapters are under `../../lib/arduino` and `../../lib/espidf`. PlatformIO only compiles libraries that appear in `lib_deps` (or are in the project's local `lib/` directory, which the smoke project does not have). Therefore `pio run -d homeworks/0_0-toolchain-smoke -e esp32s3_arduino -t compiledb` will *not* produce `lib/arduino/src/*.c` entries, and the verifier's assertion fails. This is a real defect, not a paper one — the plan's truth claim asserts the CDB will list three Arduino adapter sources, and there is no mechanism (no addition of `arduino = symlink://../../lib/arduino` to lib_deps, no `lib_extra_dirs`) that would do so. I recommend either (a) adding a separate `lib_deps` entry for the adapter during the target-compile step, (b) introducing a temporary compile-only project under `tests/` or the libs test tree, or (c) adding the adapter to the smoke project's lib_deps *before* 03-07 deletes it (a change the plan does not currently make, but is allowed under "the mock/compile proof"). This must be resolved before plan execution.
- **MEDIUM — `espidf/src/gpio.c` ordering of includes "included `<stdint.h>`, `"driver/gpio.h"`, `"esp_err.h"`, then project header"** vs. the plan's text says " include <stdint.h>, "driver/gpio.h", "esp_err.h", then header". Fine, but `espidf/src/log.c` includes `"esp_log.h"` only then its header with *no* `<stdint.h>` first. Inconsistent with `time.c` which has `<stdint.h>`. No correctness issue. Unlikely to fail anything; consistency only.
- **MEDIUM — hardcoded `"port"` tag in `esp_log_write(mapped_level, "port", "%s\n", ...)`.** Using the same tag for every port-level adapter is fine but means `esp_log` filter can't distinguish adapters by tag at runtime. Acceptable for a course; pre-decision.
- **LOW — ESP-IDF GPIO `pin_bit_mask = (1ULL << pin)` for a pin ≥ 64 (e.g. `uint8_t` = 255) would UB.** Real boards don't use such values; not asserted. Within test bounds of the course.
- **LOW — `read` logic: `gpio_get_level` returns 0/1; `mapped = level == 1 ? PORT_GPIO_HIGH : PORT_GPIO_LOW`.** `PORT_GPIO_LOW` is `= 0` so this works even though there's no `PORT_GPIO_LOW` in the mapping implication.
- **LOW — D-08 says Arduino I2C/SPI cannot stay `.c` (research Pitfall 6), deferring both.** PR plan text says these adapters DON'T exist now. Good.

**Suggestions**
- Fix the HIGH issue (HIGH): provide a compile path. Options ranked:
  1. Add `arduino = symlink://../../lib/arduino` to a local copy of a target-compile mini-project (not committed, runs under `pio run` with the project's own ini) — consistent with "no root platformio.ini" rule;
  2. Add the adapter to the smoke project's `lib_deps` in an explicit sub-step, verifying adapters before 03-07 removes the project;
  3. Better, add `lib_extra_dirs = ../../lib/arduino`? No — deprecated and pulls framework deps into native. Use (1).
- Add consistent `<stdint.h>` include to `log.c`.

**Risk Assessment:** MEDIUM solely because of the HIGH integration gap; the adapter mechanism itself is correct.

## 03-07

**Summary:** Correctly discharges the Phase 2 carry-forward: partitions CSV moved *before* the smoke project is deleted (D-18), the test suite refactored off the deletion target first (D-20), then the smoke project deleted in a dedicated commit (D-19), and finally the stub header/source pairs retired with manifests bumped to 0.2.0 and `port` going header-only (D-04/D-05). Sequence discipline is excellent and avoids the `FileNotFoundError` explosion. The one gap is that the remove/rename must be a *rename* not copy+delete, verified by `git status`.

**Strengths**
- Explicit git mv: `git mv homeworks/0_0-toolchain-smoke/default_16MB.csv partitions/default_16MB.csv`, with `git status` rename evidence. Moves perpendicular to D-18's "every ESP32 project resolves relative to its dir" warning.
- `test_pio_scripts.py` refactored onto `tests/platformio.ini` before the deletion — WR-01 discharge. Correct ordering (so the deletion can't cause `FileNotFoundError`). Verified by current tree's tests referencing `PROJECT_INI` at smoke path; refactor needed.
- Tests use `homeworks/1_1-example/...` neutral fixture paths (research §Runtime State Inventory) — pattern assertions keep proving the same rule.
- Stub retirement separates concerns correctly: `port` drops `srcDir`, the others keep both; manifests all `0.2.0`; no `dependencies` field anywhere (D-03 supersedes STACK.md:248 advice on registry-based resolution). Good consistency with D-03.
- Phase 2 review items CR-01, WR-01, WR-02, WR-03 are explicitly discharged; WR-04 (broad `.gitignore`) is recorded as an unresolved risk with explicit "don't treat this phase as closing it". Good provenance.
- C formatting deliberately deferred (D-21) — appropriate; no mass reformat coincident with a deletion.
- Special side-effect handled: ADR-0007's mention of the smoke project stays as history. The verify scans for any script/test/config/rulebook reference to the deleted name; I checked current tree — references present in test_pio_scripts.py and (historical) ADR-0007. Good.

**Concerns**
- **MEDIUM — the partitions existence test uses `homeworks/1_1-example` as the project-depth anchor** and asserts the path resolved from that directory hits the file. But that directory does not exist either now or after this phase. `git check-ignore` style reasoning (research says "an absent directory is fine for `git check-ignore` because it resolves against the pattern, not the file"). For the partitions test, the resolution is just `Path('homeworks/incorrect_dummy') / '../../partitions/default_16MB.csv'`, which normalizes to `partitions/default_16MB.csv` regardless of whether the anchor exists. So it works. But it's confusing to a reviewer and can be mistaken for a logic bug ("the file must exist at this path"). Acceptable; documented.
- **LOW — `LIB_SOURCES` mapping from plan differs from 03-01's actual sources if any task 1 estimate name mismatches.** I spot-check: 03-01 emits `ring_buffer.c`, `timing.c`, `crc.c`, `hex.c` in 03-04 (renames: `crc.c`, `hex.c`). Host: `fake_time.c, fake_gpio.c, fake_i2c.c, fake_spi.c, fake_log.c`. Arduino/ESP-IDF: `time.c, gpio.c, log.c`. Common matches. `port` -> `()`. Good.
- **LOW — `tests/platformio.ini` is *not* modified in 03-07's files_modified**, so the smoke-project deletion doesn't leave dangling paths. Fine.
- **LOW — `default_16MB.csv` is tracked (`lib/` artifacts sometimes tracked)`; plan correctly moves, not copies.**
- **LOW — D-19 demands a dedicated commit for the deletion. The executor must respect git commit boundaries **within** a plan that also has task 1 (move) and task 3 (bump). Task 2's own commit boundary is critical, not the whole plan's.**

**Suggestions**
- Ensure the executor makes (at minimum) three commits — refactor+partitions move; dedicated delete; stub retirement — with the delete isolated. The plan says so; executing it as one giant commit defeats D-19's intent.

**Risk Assessment:** LOW-MEDIUM (operational risk only, around commit granularity; mechanical correctness is well-specified).

## 03-08

**Summary:** Strong, dense plan — turn the dependency rule into a `check_architecture.py` with a deny-by-default allowlist (empty by design), an include scanner with comment stripping, an edge matrix as module-level data, a `platformio.ini` closure check under `[env:*]` with `interpolation=None`, an ASCII-/(shell/...) public-header contract test, and a local pre-commit hook. The matrix covers ≥12 negative fixture cases and has a clear three-tier exit-code contract. **Two real risks:** (1) the interplay between a `homeworks/<id>/platformio.ini` environment that *omits* `lib_deps` entirely (the smoke project's native environment does anyway but post-deletion there are no homeworks), and (2) the checker's NxN half-open vs. closed classification of includes where a module importing its *own* header is treated as a self-edge. The second is explicitly specified and tested.

**Strengths**
- The checker is constrained to stdlib only (`argparse`, `json`, `os`, `re`, `subprocess`, `sys`, `pathlib.Path`, + later `configparser`) ; runs without the toolchain. Matches ARCH-06 "tests build natively with no target toolchain" but for the linter, a stronger claim.
- Mirrors `check_pr_templates.py` structure explicitly (verified 03-pr-task): `CheckError`, `resolve_root`, `main` with exit-code mapping, PASS/FAIL indented lines. This means the contract tests' patterns (`combined`, `run_checker` helper) port directly from `test_check_pr_templates.py`.
- `followlinks=False`, every file `Path.resolve()`'d and containment-checked. Matches ASVS V12.
- Exit codes: 0 clean / 1 any violation or stale allowlist entry / 2 usage-environment errors (missing `lib/`, malformed allowlist, oversized). Plausibly lean.
- Empty allowlist and stale allowlist-entry failures both become site-fail tests, via `test_native_purity.py`? No, they're 03-08's own suite. Good.
- `files: ^(lib|homeworks)/` in the pre-commit hook ensures an unrelated change doesn't pay scan cost.
- Header inventory as a constant in `test_architecture_headers.py` means a re-introduced stub or a forgotten new header fails (grep's check).

**Concerns**
- **MEDIUM — checker scans `homeworks/**`, but Phase 3 has *deleted* the smoke project and no homework exists.** The scan is over `lib/**` only. The `homeworks`-owner classification (`homeworks/*.ini`, cross-homework include) cannot be fully exercised in the real tree until Phase 11. This is recorded in the plan's defensive "Absence of homeworks is not an error" language. Fine as long as 03-08's *fixture* tests exercise the path (they do, via `make_tree`).
- **MEDIUM — check of `ConfigParser(interpolation=None)` with `lib_deps` set extraction.** "Taking the text before an optional `=` alias and before any `@version` suffix, and ignoring `symlink://` paths beyond their last directory segment" — a complex parsing chain. A malformed multi-line `lib_deps =` list value with backslashes or duplicate aliasing is likely to surprise. Not a Phase 3 correctness issue (no real homework inis exist past 03-07), but the public surface unit's contract should include a value-countercheck test (`common (x1), arduino (x1), esp, host` counts). I'd recommend adding a small fuzz-like test.
- **LOW — Allowlist evaluation**: "an entry that matches no violation fails as stale with exit 1"; but the *matching* key is a path+rule pair. If the same path matches multiple rules (e.g., escape AND project-edge), one entry covers one. Borderline; the plan explicitly lists "an allowlisted violation" as a single negative case, so the assumption should be documented. It is in the docstring at least.
- **LOW — the header suite lists exactly the expected headers as a constant**, and the verify is that the discovered set equals it. But if a new header is added to `lib/port/include/port/` (e.g., `error.h` in Phase 5), both the code and the test constant must change in the same PR. Good coupling but fragile; the test itself can't distinguish "added a header" from "forgot to update the constant" — that's by design, but a reviewer can miss.
- **LOW — denylist `BLOCKING = ("delay(", "delayMicroseconds(", "vTaskDelay", "sleep(", "usleep(", "HAL_Delay(", "millis(", "esp_timer_get_time(", "xTaskGetTickCount(")` includes `millis(` substring; `millis()` calls inside *comments* are stripped. Good. But `common` code could use `millis()` inside string literals or `#define elapsed(...) millis()` in macros. Edge cases; known limitation.
- **LOW — C standard headers allowlist is exactly `stdbool.h, stddef.h, stdint.h, string.h, stdio.h, stdlib.h, limits.h`**. `common` also needs no port headers? Timing includes `"port/time.h"` — that's the module's `port/` prefix, not a C standard. The header-suite allows `port/` for all libraries. Good.
- **MEDIUM — `EDGES` sets a generic `homeworks -> common, port, host, arduino, espidf` and forbids cross-homework.** This means a homework cannot depend on `crc` directly even via a `common` wrapper — it must depend on `common`. Good. The plane also considers no in-homework adapter combination named twice; okay.

**Suggestions**
- Add a test for a *well-misbehaved but valid* `platformio.ini` with multi-line `lib_deps`.
- Make the byte cap (64 KiB) and the schema (string keys exactly `path`, `rule`, `reason`) documented in the allowlist's companion doc, not only in the checker docstring.
- Confirm `test_architecture_headers.py`'s header inventory covers only real files, not vendored ones (e.g., `.po` translations). It does (grep only under `lib/*/include/**/*.h`).

**Risk Assessment:** MEDIUM (multi-form parsing complexity + absence of real homework inis means half the checker's contract runs only on fixtures until Phase 11).

## 03-09

**Summary:** Correctly pins the two properties success criteria 2 and 3 hinge on: a host-only `compile_commands.json` (no Xtensa/RISC-V, no framework-include path, all nine shared sources present) and an identical digest across 20 consecutive runs. The regex + per-line matching + derived counts is the only defensible approach given Unity's `path:line:` prefixes and PlatformIO's dual-stream output (research Pitfall 8, verified split and non-corresponding summary counts). These must run *last* on the final tree.

**Strengths**
- `digest()` is mandated to use `TEST_LINE.match` *per line* (not `findall(text)`), and to drop paths, line numbers, assertion messages, and durations. This is warden against the Pitfall 8 gotchas (Unity inserts `test_fail: Expected 2 Was 1` before the tab on failure; PlatformIO emits duration on both streams).
- `RUNS = 20` constant, not configurable, and "do not reduce the run count".
- Warm-up build first (`pio test -d tests` once) so the 20 measured runs land under **15 seconds** total — addressed Assumption A6.
- Every `pio` invocation has `timeout=300`.
- Negative fixture copies `lib/`, `tests/`, `platformio.shared.ini`, `scripts/pio/` into a `TemporaryDirectory` and appends a framework include to the copy; the script can never write to the real tree; `self.addCleanup` is declared. Correctly addresses ASVS V12. Note it removes entries of `.pio/` and pre-existing `compile_commands.json` via `ignore=shutil.ignore_patterns(".pio", "compile_commands.json")`.
- Raw `compile_commands.json` inclusion of `tests/src/main.c` (compile probe from 03-01) would show up; plan 03-09 explicitly lists the nine shared sources and that `main.c` is fine to be there.
- `ConfigurationGuardTests` walks all `platformio.ini` at the repo root (skipping `.pio/`) and asserts `host=symlink://` only inside `[env:native]`. This is the durable D-17 form.

**Concerns**
- **MEDIUM — negativerequired fixture only injects a *framework* include into `lib/common/src/timing.c`.** Research Pitfall 3 explicitly notes the compile gate *does not* catch `common → adapter` via a relative include (`#include "../../arduino/include/..."` compiles and links). So 03-09's "compile gate rejects forbidden dependencies" proof only proves rejection of *framework* includes, not the cross-library relative-include case. Both plans (03-08 textual, 03-09 compile) are needed. The plan's edge-probe disposition acknowledges this. So this is a disclosed and acceptable gap, but it means the headline "compile gate rejects forbidden dependency" claim only holds for the framework-header case — and should be phrased accordingly. (Recommend adding a second negative fixture)? That would be expensive (additional 20 runs × 1?). I'd just reword: "the compile gate rejects a framework dependency; the checker rejects relative cross-library includes."
- **LOW — regex's `(?:: .*?)?` tolerance of assertion messages.** Research states Unity inserts a `test_fail: Expected 2 Was 1` before the tab. Fine.
- **MEDIUM — `Regex` correctness depends on `sonar`/Unity 2.6.1 printing exactly `path:line: test_name\t[STATUS]`.** Only verified with host Apple clang. The plan acknowledges "different compiler is separate measurement." Could still pass on Apple clang but fail on a slightly-different Unity build on Linux CI. Recommend copying a tiny portion of a transcript to a golden test for safety (offline-safe).
- **LOW — failing runs must not trigger the same suite to re-run**: tries collected; final digest only first-to-diverge. Good.
- **LOW — "fails rather than skips when `pio` is absent"** without mocking. Valid test-suite convention (e.g., test_adrs's heavy dependency on YAML-less parse works the same). Review said "the absence path is exercised by removing pio from PATH in review, not in the routine run" — it is not actually tested. This is stated as a "prohibition"/policy, but not itself test-asserted. Acceptable for the Phase 3 gate (pio is present).
- **LOW — `subprocess.run` with `cathout=True` on the 20-run case: ~3-5 KB each; fine.**
- **LOW — 03-09 does not actually install anything new**, as recorded.

**Suggestions**
- Add a second negative fixture for a relative adapter include via `#include "../../arduino/include/arduino/time.h"` in `lib/common/src/timing.c`, recording it as "compiles (expected — protects only via textual checker)". That makes the limits explicit in a test rather than only in the plan doc.
- Phrase the success criterion precisely.

**Risk Assessment:** LOW-MEDIUM (mostly the measurement fidelity margin; the test design is correct).

---

# Cross-plan observations

1. **HIGH coupling defect in plan 03-06 (adapters target compile).** As described above, the smoke project's lib_deps only lists `common`, `port`, `host`; the adapters never compile there. The plan's verifier expects `lib/arduino/src/time.c` in the CDB. This must be reconciled before execution — recommend providing an isolated target-compile mini-project (consistent with no root `platformio.ini`) or explicitly adding the adapter to the smoke project's `lib_deps` right before 03-07 deletes the smoke project.
2. **The Wave 5 race between 03-08 and 03-09:** both depend on 03-07 (Wave 4). 03-09 specifically references the final tree's `tests/src/main.c` probe shipped by 03-01. That's in place. 03-08's `test_architecture_headers.py` asserts byte-identical header inventory (21 headers, see breakdown). If 03-06 or 03-05 added/removed a header unnoticed, the header suite fails fast — that's actually desirable as a catching gate midway through the wave.
3. **Phase 2 carry-forward in 03-07 has operational complexity that should be tracked by a few CI guards, but the repository has no CI yet in Phase 3.** The only verification is `python3 -m unittest discover`; that gate doesn't check the dedicated-commit boundary. Review the git log after execution.
4. **Scope discipline is good.** No core algorithm beyond "proven minimum" (D-11) — `fixed_point`, state machine, calculations all deferred. D-21 defers formatting. I2C/SPI adapters deferred. No CI in Phase 3.
5. **WR-04 is explicitly left open** — recorded as a risk, not silently treated as closed. Correct handling.
6. **Plans claim measured reproducibility extensively** (e.g., `pio run` outputs compiledb verified on this machine). Those numbers are concrete evidence for design; the executed verification steps are the actual gate.

## Overall Risk Assessment

**MEDIUM**. Phase 3 is the load-bearing structural phase for the whole rest of the monorepo, so every decision (direction edge, vtable shape, bounded extras, port doesn't block or sleep) compiles into every future homework's include graph. The plans themselves are meticulous and cite real, machine-verified behavior, with explicit assumption tables and disclosed "judgment" verification cases. The one HIGH-level flaw — plan 03-06's adapters won't be reached by the smoke project's LDF, so its verification step (CDB lists adapter sources) cannot pass as written — is mechanical to repair with an isolated target-compile project. Also, plan 03-09's "compile gate rejects a forbidden dependency" headline should be narrowed to the "framework-header" case. Everything else is documentation, mechanical tests, and pre-commit wiring at low actual risk.

Recommended action: before execution, patch plan 03-06 to add a self-contained compile target for the adapters (or add adapter entries to the smoke project's `lib_deps`), and re-check the 03-08 header-count constant (21) once the adapters land.

---

## Antigravity Review

> [reviewed-without-source-citations] This reviewer declared source-grounded evidence but cited no file:line source evidence, so it reviewed the pasted plan text only — down-weight its verdict in the Consensus Summary.

# Cross-AI Plan Review: Phase 3 — Shared Core and Dependency Rule

This review evaluates the nine implementation plans for **Phase 3: Shared Core and Dependency Rule** (`03-01` through `03-09`) against the codebase at `/Users/vloktiev/Dev/miltech/homeworks`. All referenced files, configurations, scripts, and tests have been inspected directly in the workspace.

---

## 03-01

### Summary
Plan `03-01` establishes the foundational spine of Phase 3 by creating the top-level host-only `tests/` PlatformIO project, the core `port/status.h` error vocabulary, the consumer-owned `port_time_t` contract, the clock-free `common/timing` helper, the deterministic `host/fake_time` double, and the initial Unity test suites. This tracer slice proves end-to-end native compilation and testing without target toolchain dependencies before any other contracts or adapters are implemented.

### Strengths
- **Project Depth and SCons Script Resolution**: In [platformio.shared.ini](file:///Users/vloktiev/Dev/miltech/homeworks/platformio.shared.ini#L31-L37), `[native_unity]` configures `extra_scripts = pre:../../scripts/pio/compiledb.py` for homework projects located two levels down. The plan correctly recognizes that `tests/platformio.ini` is located at depth 1 and overrides `extra_scripts = pre:../scripts/pio/compiledb.py`, avoiding path resolution failures.
- **Handling of PlatformIO `extends` List Replacement**: In PlatformIO INI parsing, `extends` replaces rather than merges list properties such as `build_flags`. The plan explicitly repeats `-std=c11`, `-Wall`, and `-Wextra` from `[native_unity]` in `tests/platformio.ini`.
- **LDF Compilation Probe (`tests/src/main.c`)**: PlatformIO's Library Dependency Finder (LDF) only compiles shared library sources during `pio run -t compiledb` if a project source references them. By introducing `tests/src/main.c` while leaving `test_build_src = false`, the plan ensures `lib/common/src/timing.c` and `lib/host/src/fake_time.c` appear in `compile_commands.json` without contaminating Unity test binaries.
- **State Machine Debounce Design**: `common_debounce_t` uses three explicit fields (`stable`, `candidate`, `candidate_since_ms`), cleanly separating the idle state from an active debounce window starting at timestamp 0.

### Concerns
- **Timer Expiry Window Horizon [LOW]**: The plan states that `common_timer_expired` evaluates `(int32_t)(now_ms - deadline_ms) >= 0` with a "49-day interval implied by uint32_t milliseconds". However, casting unsigned 32-bit delta to a signed `int32_t` splits the $2^{32}$ span in half; the maximum detectable future deadline before wrapping to negative (and thus falsely evaluating as expired) is $2^{31}-1$ ms (~24.85 days), not 49.7 days.
- **Callback Null Dereference Defense [LOW]**: In `common_debounce_update(common_debounce_t *state, const port_time_t *time, bool raw_input, uint32_t stable_ms)`, Task 2 specifies checking whether `state` or `time` is `NULL`. However, it does not explicitly mandate checking `time->now_ms != NULL`. If a caller passes a struct with an uninitialized function pointer, calling `time->now_ms(time->ctx)` will trigger a segmentation fault.

### Suggestions
- Document the exact ~24.85-day maximum deadline horizon in docstrings in `lib/common/include/common/timing.h` and `lib/common/src/timing.c`.
- In `common_debounce_update`, guard against a null callback: `if (time == NULL || time->now_ms == NULL) return state ? state->stable : false;`.

### Risk Assessment
**LOW**: The tracer plan is tightly scoped, addresses verified PlatformIO edge cases, and provides immediate automated verification on the native test runner.

---

## 03-02

### Summary
Plan `03-02` records the architectural dependency direction in `docs/decisions/0008-common-depends-on-port.md`, explicitly superseding the contradictory sentence in ADR-0002. It updates the ADR status index in `docs/decisions/README.md` and fixes the non-functional `pio test -e native` quick-start command in `AGENTS.md` to `pio test -d tests -e native`.

### Strengths
- **Surgical Supersession of ADR-0002**: In [docs/decisions/0002-ports-and-adapters-no-universal-hal.md](file:///Users/vloktiev/Dev/miltech/homeworks/docs/decisions/0002-ports-and-adapters-no-universal-hal.md#L42-L46), the text originally stated: `lib/common depends on nothing; lib/port declares the interfaces and depends on common`. The plan preserves the historical record of ADR-0002 intact while creating ADR-0008 to supersede specifically this sentence, aligning with hexagonal architecture principles.
- **Compliance with ADR Structural Gates**: The plan follows the requirements verified by [scripts/tests/test_adrs.py](file:///Users/vloktiev/Dev/miltech/homeworks/scripts/tests/test_adrs.py#L28-L45) (five frontmatter keys, eight MADR 4.0 sections in order, exact title matching in `README.md`, next number advanced to `0009`).
- **Fixing the Broken Quick-Start Step**: In [AGENTS.md](file:///Users/vloktiev/Dev/miltech/homeworks/AGENTS.md#L25), step 3 lists `pio test -e native`. Running this from the repository root fails with `NotPlatformIOProjectError`. Updating it to `pio test -d tests -e native` ensures the command works as advertised while keeping `AGENTS.md` under the 300-line ceiling enforced by [scripts/tests/test_agents_md.py](file:///Users/vloktiev/Dev/miltech/homeworks/scripts/tests/test_agents_md.py#L25).

### Concerns
- **Quick-Start Step 2 Ambiguity [LOW]**: In [AGENTS.md](file:///Users/vloktiev/Dev/miltech/homeworks/AGENTS.md#L24), Step 2 lists `pio run` without `-d <dir>`. Once `homeworks/0_0-toolchain-smoke` is deleted in plan `03-07`, `pio run` executed from the repository root will also fail with `NotPlatformIOProjectError`. The plan explicitly notes changing Step 2 is out of scope for Phase 3, but this leaves a potential point of friction for agents following the quick-start table sequentially.

### Suggestions
- Update the purpose description of Step 2 in `AGENTS.md` to note that `pio run` must be invoked with `-d <project>` or from within a project directory once homework projects are introduced.

### Risk Assessment
**LOW**: Pure documentation and test contract alignment with zero runtime regression risk.

---

## 03-03

### Summary
Plan `03-03` completes the `lib/port` contract surface by specifying C function-pointer interfaces for GPIO, I2C, SPI, and logging (`lib/port/include/port/{gpio,i2c,spi,log}.h`). It validates their invocation and context plumbing via local loopback implementations in `tests/test/test_port_contracts/test_contracts.c`.

### Strengths
- **Strict Bus-Level Abstraction (ARCH-07)**: `port_i2c_t` and `port_spi_t` expose only raw transfer/write/read operations over buffers and lengths. They deliberately omit display, sensor, or register-map abstractions, preventing the emergence of a leaky universal HAL.
- **Consistent Error Vocabulary (D-09)**: Every operation that can fail returns `port_status_t` (`PORT_OK`, `PORT_ERR_TIMEOUT`, `PORT_ERR_IO`, `PORT_ERR_INVALID_ARG`, `PORT_ERR_NOT_SUPPORTED`). Logging returns `void` as an intentional design choice to prevent logging failures from altering control flow.
- **Zero Global Mutable State (D-06)**: Every struct carries an opaque `void *ctx`. The port owns no state; state belongs entirely to the adapter or test double behind `ctx`, enabling multiple buses and timers in the same program.
- **Positional Struct Initialization**: The test suite uses positional aggregate initialization for vtables, ensuring compatibility with C++ compilers in future composition roots (Pitfall 4).

### Concerns
- **I2C 7-Bit Address Limitation [LOW]**: `port_i2c_t` specifies `uint8_t address`. While standard for 7-bit I2C devices used in educational courses, it cannot accommodate 10-bit addressing without a breaking change or multiplexing convention.
- **SPI Chip Select (CS) Pin Model [LOW]**: The SPI contract does not accept a CS pin parameter per transaction. As documented in the plan, CS ownership belongs to the adapter instance behind `ctx`. For multiple SPI devices sharing a single bus with different CS lines, a consumer must instantiate separate `port_spi_t` instances. This design is sound but must be documented clearly for driver authors.

### Suggestions
- Add an explicit comment in `lib/port/include/port/i2c.h` documenting that `uint8_t address` represents a 7-bit I2C bus address.
- Add an architectural note in `lib/port/include/port/spi.h` clarifying how multi-slave CS routing is managed via distinct adapter contexts.

### Risk Assessment
**LOW**: The contract designs are clean, idiomatic C11 interfaces strictly adhering to architectural constraints.

---

## 03-04

### Summary
Plan `03-04` implements the proven-minimum domain primitives in `lib/common`: a caller-allocated ring buffer (`ring_buffer.h/.c`), CRC-16/CCITT-FALSE (`crc.h/.c`), and hex codecs (`hex.h/.c`), verified by independent Unity test suites in `tests/test/`.

### Strengths
- **Anti-Speculation Discipline (D-11, Pitfall C15)**: The plan restricts `lib/common` strictly to primitives required by initial assignments, deferring fixed-point math and generic state machines until multiple consumers exist.
- **Disambiguated Ring Buffer State**: `common_ring_buffer_t` tracks `head`, `tail`, and `count` explicitly over caller-owned memory. This eliminates the "waste one slot" convention and makes empty vs. full checks unambiguous.
- **Standardized Check Value**: `common_crc16` is pinned against standard ASCII `"123456789"` (`0x29B1`). The header includes an explicit disclaimer stating the algorithm is for transmission error detection and must not be used for cryptographic integrity or authentication.
- **Strict Capacity Guards in Codecs**: `common_hex_encode` and `common_hex_decode` require explicit output buffer capacities and return `false` on insufficient space rather than performing silent partial truncation.

### Concerns
- **Ring Buffer Concurrency and ISR Reentrancy [MEDIUM]**: In embedded firmware, ring buffers are frequently used across ISR and main loop boundaries (e.g. UART RX interrupt pushing, main task popping). Because `common_ring_buffer_t` mutates the shared `count` field in both `common_ring_buffer_push` and `common_ring_buffer_pop`, it is not thread-safe or single-producer/single-consumer ISR-reentrant without external mutual exclusion.
- **Zero-Length Input Handling in Hex Codec [LOW]**: When encoding a zero-length input (`length == 0`), `common_hex_encode` requires `out_size >= 1` to write the null terminator `""`. The plan should ensure this boundary case is explicitly tested.

### Suggestions
- Document in `lib/common/include/common/ring_buffer.h` that `common_ring_buffer_t` is single-threaded domain logic and requires caller-provided critical sections or mutexes when shared with interrupt handlers.
- Add test cases in `test_hex.c` for `length == 0` encoding and decoding.

### Risk Assessment
**LOW**: Pure, allocation-free, mathematically verified C algorithms with zero hardware or framework dependencies.

---

## 03-05

### Summary
Plan `03-05` delivers deterministic, bounded host test doubles for GPIO, I2C, SPI, and logging in `lib/host`. Each double implements the exact `port_*_t` contract type and provides scriptable one-shot failure injection (`fail_next`) for testing negative paths on the host.

### Strengths
- **Compile-Time Mock Drift Prevention (Pitfall C12)**: Each fake returns the exact `port_*_t` type required by real adapters, verified by `test_fakes_return_the_real_contract_types`. Any signature change in `lib/port` immediately triggers a compilation failure in `lib/host`.
- **Bounded Static Memory Allocation (Assumption A2)**: Doubles use fixed, caller-owned buffers (`HOST_FAKE_GPIO_PINS 64`, `HOST_FAKE_I2C_CAPACITY 32`, `HOST_FAKE_SPI_CAPACITY 32`, `HOST_FAKE_LOG_LINES 32`). Over-bound accesses return `PORT_ERR_INVALID_ARG` or increment a drop counter, avoiding buffer overflows without heap allocation.
- **Deterministic One-Shot Error Injection**: The `fail_next` setter allows unit tests to simulate bus failures, timeouts, and I/O errors deterministically without hardware or complex mocking frameworks.

### Concerns
- **32-Byte Bus Buffer Capacity [LOW]**: A 32-byte capacity is sufficient for sensor register reads and telemetry frames, but if future assignments involve block transfers (e.g. display scanlines or EEPROM page writes), transfers exceeding 32 bytes will fail with `PORT_ERR_INVALID_ARG`.

### Suggestions
- Ensure `HOST_FAKE_I2C_CAPACITY` and `HOST_FAKE_SPI_CAPACITY` remain defined as public header macros so test suites can configure transfer chunk sizes against them.

### Risk Assessment
**LOW**: The fakes are deterministic, strictly bounded, allocation-free, and directly enable the 20-run determinism verification in `03-09`.

---

## 03-06

### Summary
Plan `03-06` implements thin hardware adapters for Arduino and ESP-IDF covering time, GPIO, and logging. Public adapter headers expose only `port_*_t` factory functions, while translation sources (`.c`) map calls to the underlying framework APIs, verified against the pinned Xtensa ESP32-S3 toolchain via `homeworks/0_0-toolchain-smoke`.

### Strengths
- **Header Cleanliness (D-10)**: Adapter headers (`lib/arduino/include/arduino/*.h` and `lib/espidf/include/espidf/*.h`) include only matching `port/*.h` headers. Framework headers (`Arduino.h`, `esp_err.h`, `driver/gpio.h`) and types (`esp_err_t`, `gpio_num_t`) are strictly confined to `.c` source files.
- **Unconditional Logging in Arduino (Pitfall 5)**: In `lib/arduino/src/log.c`, output is routed through `log_printf` unconditionally with level prefixes rather than level-gated macros that compile out under default PlatformIO Arduino configurations.
- **Driver Status Mapping in ESP-IDF (D-09)**: `lib/espidf/src/gpio.c` populates a stack-allocated `gpio_config_t` and maps non-`ESP_OK` return codes to `PORT_ERR_IO`, preventing framework error codes from escaping through the abstraction seam.

### Concerns
- **Transient Target-Compile Verification [HIGH]**: Plan `03-06` verifies adapter compilation using `pio run -d homeworks/0_0-toolchain-smoke -e esp32s3_arduino -t compiledb`. However, in the very next wave (Plan `03-07`), `homeworks/0_0-toolchain-smoke` is permanently deleted! After Plan `03-07`, there is **no project or environment in the entire repository that compiles `lib/arduino` or `lib/espidf`**. As a result, any syntax error, typo, or API break introduced in these adapters during Phases 4 through 10 will go completely undetected by `pio test -d tests -e native` and `python3 -m unittest discover -s scripts/tests -v` until Phase 11.
- **GPIO Pull-Up Pin Reconfiguration [LOW]**: When reconfiguring a pin from `PORT_GPIO_INPUT_PULLUP` to `PORT_GPIO_INPUT` in ESP-IDF, `pull_up_en` must be explicitly disabled (`GPIO_PULLUP_DISABLE`). Stack-allocating `gpio_config_t config = {0};` is required to ensure inactive fields are not left with garbage values.

### Suggestions
- In `lib/espidf/src/gpio.c`, explicitly initialize `gpio_config_t config = {0};` and explicitly set both `pull_up_en` and `pull_down_en` on every `set_mode` call.
- Acknowledge the target-compilation gap in the phase summary, and consider introducing a headless check or script in Phase 4/5 that verifies `lib/arduino` and `lib/espidf` can still be compiled by the target toolchain.

### Risk Assessment
**MEDIUM**: The adapter implementations are correct, thin, and verified at write time, but deleting the smoke project in `03-07` leaves them without an active compilation gate until Phase 11.

---

## 03-07

### Summary
Plan `03-07` resolves the Phase 2 carry-forward blockers: it moves `default_16MB.csv` to a permanent root-level `partitions/` directory, deletes the temporary `homeworks/0_0-toolchain-smoke/` project in a dedicated commit, updates `scripts/tests/test_pio_scripts.py` and `test_gitignore.py`, retires the ten Phase 2 stub files, and bumps all library manifests to version `0.2.0`.

### Strengths
- **Discharging Phase 2 Blockers**: Directly resolves CR-01 (relocating the partition table) and WR-01 (eliminating test suite dependencies on the temporary smoke project).
- **Proper Git File Move (D-18)**: Executes `git mv` to transition `default_16MB.csv` into `partitions/default_16MB.csv`, preserving file provenance in git history.
- **Correct Multi-Level Path Resolution**: Updates `platformio.shared.ini` lines 10 and 24 to `board_build.partitions = ../../partitions/default_16MB.csv`, which correctly resolves from any two-level-deep homework project (`homeworks/<id>/`).
- **Elimination of Version Duplication (WR-03)**: Retires the stub C sources that returned hardcoded version strings (`common_version()`, `port_version()`), leaving `library.json` as the single source of truth for library versions.

### Concerns
- **Test Assertion Sequence Race Between Task 1 and Task 3 [HIGH]**: In Task 1 (lines 4029-4031), `scripts/tests/test_pio_scripts.py` is updated to assert that `lib/port/src` "either does not exist or contains no files". Task 1 verification (line 4044) immediately executes `python3 -m unittest scripts.tests.test_pio_scripts scripts.tests.test_gitignore -v`. However, `lib/port/src/port.c` is **not deleted until Task 3** (line 4110)! Consequently, running the test suite during Task 1 verification will fail on the existing `lib/port/src/port.c` file.
- **Source Inventory Mismatch in Task 1 [MEDIUM]**: Task 1 updates `LIB_SOURCES` to map each library to its new module sources (`ring_buffer.c`, `timing.c`, etc.). If `test_pio_scripts.py` asserts that the directory contents match `LIB_SOURCES` exactly, it will fail because the old stub files (`common.c`, `arduino_adapter.c`, `host.c`, etc.) are still present on disk until Task 3 deletes them.

### Suggestions
- Reorder tasks or defer the strict directory-emptiness assertion: In Task 1, allow `port.c` to be optionally present, or move the deletion of the stub files into Task 1 before `test_pio_scripts.py` is verified. Task 3 should only be responsible for the manifest version bump to `0.2.0` and removing `srcDir` from `lib/port/library.json`.

### Risk Assessment
**MEDIUM**: High risk of self-inflicted test failure during plan execution due to ordering discrepancies between test updates in Task 1 and file deletions in Task 3.

---

## 03-08

### Summary
Plan `03-08` delivers the architectural enforcement mechanisms: `scripts/check_architecture.py` (a textual `#include` scanner and `platformio.ini` closure validator), `scripts/architecture/allowlist.json`, comprehensive unit tests in `scripts/tests/test_check_architecture.py` and `test_architecture_headers.py`, and a local pre-commit hook.

### Strengths
- **Textual Scanner Rationale (ARCH-05, D-15)**: The plan correctly recognizes that C compilers cannot enforce architectural boundaries when relative includes (`#include "../../../lib/arduino/..."`) resolve on the filesystem. A dedicated textual scanner is essential to enforce architectural boundaries.
- **Strict Layer Matrix**: Enforces `common → port`, `adapters → port`, and homework dependency rules. Prohibits cross-homework includes and restricts external includes in `port`, `common`, and `host` to a strict whitelist of C standard headers.
- **Public Header Contract Suite**: `test_architecture_headers.py` statically enforces `#pragma once`, `extern "C"` guards, ASCII-only encoding, and bans framework types (`Arduino.h`, `esp_err_t`, `gpio_num_t`, `class `) from all public headers.
- **Fail-Safe Allowlist Design**: `allowlist.json` requires `path`, `rule`, and `reason`. Stale entries that match no violations trigger exit code 1, and malformed files trigger exit code 2.

### Concerns
- **Pre-Commit Hook File Pattern Gap [MEDIUM]**: In Task 3, `.pre-commit-config.yaml` configures the hook with `files: ^(lib|homeworks)/`. If a developer modifies `scripts/architecture/allowlist.json` or `scripts/check_architecture.py`, `git commit` will **not** trigger the `check-architecture` hook! An invalid or stale allowlist entry could be committed without being checked by the pre-commit gate.
- **Leading Whitespace in Include Directives [LOW]**: In Task 1, regex matching for `#include` must account for potential indentation (e.g. `  #include <stdint.h>`). The regex should use `^\s*#\s*include` rather than strict `^#include`.

### Suggestions
- Update the pre-commit hook in `.pre-commit-config.yaml` to include the script and allowlist paths:
  ```yaml
  files: ^(lib/|homeworks/|scripts/architecture/|scripts/check_architecture\.py)
  ```
- Ensure comment stripping in `check_architecture.py` runs before regex matching and that the include regex permits arbitrary whitespace around `#` and `include`.

### Risk Assessment
**LOW**: The enforcement design is comprehensive, standard-library based, fast, and supported by 14+ negative fixture tests.

---

## 03-09

### Summary
Plan `03-09` provides the empirical validation for the phase's core success criteria. `scripts/tests/test_native_purity.py` validates that `tests/compile_commands.json` contains only host compilers with no Xtensa/RISC-V/framework paths, and proves the compile gate fails on framework leaks using a temporary fixture. `scripts/tests/test_native_determinism.py` runs `pio test -d tests -e native` 20 times and asserts that normalized digests are identical.

### Strengths
- **Empirical Purity Proof via Compilation Database (ARCH-06)**: Validates actual SCons compilation commands to guarantee that no target compiler or framework include directory entered the native build.
- **Negative Compile Gate Verification**: The fixture copies the project to a temporary directory, injects `#include <Arduino.h>` into `common/src/timing.c`, and proves that `pio run -d tests -e native` fails, proving that the build system actively rejects framework dependencies.
- **Robust Digest Normalization (D-14, Pitfall 8)**: The determinism digest matches per-line anchored `suite/test_name: STATUS` patterns, stripping durations, timestamps, and line numbers to prevent false divergence.
- **Warm-Up Execution**: Executes an initial warm-up run prior to the 20 measured runs, ensuring PlatformIO packages and SCons build caches are hot.

### Concerns
- **Repository Test Suite Latency [MEDIUM]**: Adding 20 consecutive `pio test` runs to `scripts/tests/test_native_determinism.py` will increase the execution time of `python3 -m unittest discover -s scripts/tests -v` (step 4 in the `AGENTS.md` quick-start) from ~3.1 seconds to approximately 15–20 seconds. While necessary for the phase proof, running 20 iterations on every unit test invocation creates developer friction.
- **Offline Temporary Fixture Resolution [LOW]**: In `FrameworkIncludeFixtureTests`, copying into `tempfile.TemporaryDirectory()` with `.pio` ignored means `throwtheswitch/Unity@2.6.1` is not in `.pio/libdeps/native`. PlatformIO must retrieve it from its global cache (`~/.platformio/.cache`). If run in an air-gapped environment without that cache, the fixture run could fail on package retrieval rather than on the injected framework include.

### Suggestions
- Allow configuring the run count via an environment variable (e.g. `DETERMINISM_RUNS=20` default, but allowing `DETERMINISM_RUNS=1` for rapid local iteration during unrelated changes).
- In `FrameworkIncludeFixtureTests`, consider copying `.pio/libdeps` into the temporary tree so Unity is already present and does not require cache lookup.

### Risk Assessment
**LOW**: Direct empirical proof of the phase success criteria with thorough negative testing and rigorous output normalization.

---

## Cross-Plan Analysis and Integration Risks

1. **Dependency Ordering and Wave Structure**:
   The 5-wave division is well-structured:
   - Wave 1 (`03-01`): Native spine and tracer slice.
   - Wave 2 (`03-02`, `03-03`, `03-04`): ADR, port contracts, and common primitives.
   - Wave 3 (`03-05`, `03-06`): Host fakes and hardware adapters.
   - Wave 4 (`03-07`): Carry-forward close-out (partitions move, smoke deletion, stub retirement).
   - Wave 5 (`03-08`, `03-09`): Enforcement hooks and validation proofs.
   Wave 4 correctly precedes Wave 5 because the header contract suite (`03-08`) and purity proofs (`03-09`) require the stubs and smoke project to be gone.

2. **The Wave 4 / Wave 3 Toolchain Seam**:
   Plan `03-06` relies on `homeworks/0_0-toolchain-smoke` to verify that `lib/arduino` and `lib/espidf` compile under Xtensa. Plan `03-07` then deletes `homeworks/0_0-toolchain-smoke`. While this adheres to the roadmap, it leaves the repository without any target-compilation check for adapters between Phase 3 and Phase 11. Maintainers must be aware that adapter syntax errors will not be caught by CI until homework projects are restored.

3. **Task Synchronization in `03-07`**:
   The most immediate implementation risk is the ordering in `03-07` where Task 1 updates `test_pio_scripts.py` to assert that `lib/port/src` contains no files before Task 3 has deleted `lib/port/src/port.c`. This must be addressed during execution to prevent Task 1 verification from failing.

---

## Goal-Backward Phase Verification

| Phase 3 Success Criterion | Plan Delivering Criterion | Verification Mechanism | Status |
|---------------------------|---------------------------|------------------------|--------|
| 1. `common` and `port` build natively with no framework headers/toolchain | `03-01`, `03-09` | `scripts/tests/test_native_purity.py` asserts compiler is host-only and no framework include paths exist in CDB | **PASS** |
| 2. Top-level `tests/` project runs Unity suite and passes | `03-01`, `03-03`, `03-04`, `03-05` | `pio test -d tests -e native` runs all suites across all modules green | **PASS** |
| 3. `check_architecture.py` rejects forbidden includes and native compile gate fails | `03-08`, `03-09` | `scripts/tests/test_check_architecture.py` (14 fixture tests) + `test_native_purity.py` (negative compile fixture) | **PASS** |
| 4. Suite produces identical results over 20 consecutive runs using fake time | `03-01`, `03-09` | `scripts/tests/test_native_determinism.py` compares 20 normalized digest outputs | **PASS** |
| 5. Public headers expose only C contracts with `extern "C"`; no universal HAL | `03-03`, `03-08` | `scripts/tests/test_architecture_headers.py` asserts header inventory, `#pragma once`, `extern "C"`, and bans framework types | **PASS** |

---

## Overall Risk Summary

- **Architecture Quality**: Exceptional. The hexagonal ports-and-adapters architecture is strictly observed. Contracts are consumer-owned, bus-level, and allocation-free.
- **Key Implementation Hazards to Watch**:
  - Resolve the Task 1 / Task 3 assertion race in `03-07` during execution so `test_pio_scripts.py` does not fail on `port.c`.
  - Expand the `.pre-commit-config.yaml` file filter in `03-08` to include `scripts/architecture/allowlist.json` and `scripts/check_architecture.py`.
- **Verdict**: **READY FOR EXECUTION** with the minor adjustments noted above.

---

## Consensus Summary

Three independent reviews ran: two model instances behind the same `codex` adapter
(`codex-glm`, `codex-beam`) and `antigravity`. All three covered all nine plans
(`plan_coverage` complete for every lane). The `antigravity` lane carries the
`[reviewed-without-source-citations]` marker, so its judgement-class verdicts are
down-weighted below; its one HIGH finding was independently source-verified and stands.

Every HIGH finding below was re-checked against the repository before being counted. One
of the three HIGHs (codex-beam on `03-06`) is **refuted by source** and is recorded under
Divergent Views rather than Agreed Concerns.

### Agreed Strengths

- **The wave order is sound and tracer-first.** `03-01` proves the spine (native `tests/`
  project, `common → port` linkage, fake-time timing) before contracts, primitives, fakes
  and adapters land; `03-02` locks the dependency direction before the wider surface
  exists. All three reviewers independently endorsed the ordering.
- **Consumer-owned, bus-level contracts with `extern "C"` and no global state.** `port`
  owns no policy, I2C/SPI stay at address+buffer+length, and every type carries an opaque
  `ctx`. This is the right shape for ARCH-07 and avoids a universal HAL.
- **Fakes are bounded, allocation-free and compile-time drift-protected.** Each fake
  returns the real `port_*_t` type, so a signature change fails compilation; fixed
  capacities and a one-shot `fail_next` keep the host suite deterministic.
- **The empirical gates are the right ones.** A host-only `compile_commands.json` purity
  proof plus a 20-run normalized Unity digest directly exercise success criteria 1–4;
  per-line digest matching is the defensible way to survive Unity/PlatformIO output quirks.
- **`03-07` sequences carry-forward cleanup correctly.** `git mv` the partition table and
  refactor `test_pio_scripts.py` off the smoke project *before* deleting it, with the
  deletion in a dedicated commit. All three reviewers called this out as strong.
- **Scope discipline holds.** Only the proven-minimum primitives (`ring_buffer`, CRC-16,
  hex) are implemented; `fixed_point`, generic state machines, I2C/SPI adapters and
  formatting are explicitly deferred and recorded rather than silently dropped.

### Agreed Concerns

- **MEDIUM — adapter target-compile evidence has no life after `03-07`.** `03-06` verifies
  the Arduino/ESP-IDF adapters by compiling them in `homeworks/0_0-toolchain-smoke`, which
  `03-07` then deletes in the next wave. After that, nothing in the repository compiles
  `lib/arduino` or `lib/espidf` until Phase 11, so an adapter break introduced in Phases
  4–10 is invisible to both `pio test -d tests` and the Python suite. This is a process
  risk, not a plan-execution blocker (see Divergent Views for the refuted variant).
- **MEDIUM — `03-07` uses an artificial homework anchor for the partitions existence
  test.** Resolving `../../partitions/default_16MB.csv` against `homeworks/1_1-example/`
  works because path normalization does not require the directory to exist, but it reads
  like a bug to a future maintainer. Prefer an explicit repo-root assertion plus a
  dedicated relative-resolution test.
- **LOW — `03-04` leaves the hex failure convention undecided.** “Leave `*out_length`
  untouched *or* set it to zero” must be pinned to one behaviour in the plan now, with a
  test for insufficient capacity and zero-length input, or the implementation will drift.
- **LOW — `03-08` allowlist auditability.** `reason` is schema-checked as a string but not
  required to be non-empty; a stale-entry check and a non-empty reason would make the
  allowlist a real audit record rather than a bypass list.

### Divergent Views

- **codex-beam's HIGH on `03-06` is refuted by source.** It claims the smoke project
  declares “only `common`, `port`, `host` in `lib_deps`” so the adapters never compile.
  In fact only `[env:native]` does: `[env:esp32s3_arduino]` lists
  `arduino=symlink://../../lib/arduino` and `[env:esp32s3_espidf]` lists
  `espidf=symlink://../../lib/espidf` (`homeworks/0_0-toolchain-smoke/platformio.ini`).
  The CDB verification in `03-06` is therefore mechanically viable. The residual valid
  concern is only the post-deletion loss of the gate (Agreed Concerns).
- **`03-08` classifier bypass is raised by codex-glm alone (HIGH); the other two did not
  see it.** The plan defines `classify()` so that only names starting with `./` or `../`
  are `escape`; an include such as `common/../arduino/include/arduino/time.h` classifies
  as a `common` self-edge and is allowed. Whether that include also compiles depends on
  the active `-I` set, so the practical exploitability is narrower than “HIGH”, but the
  textual checker should reject any `..` segment. Treat as MEDIUM–HIGH and fix before
  implementation.
- **`03-07` Task 1 / Task 3 ordering race is raised by antigravity alone (HIGH); codex-glm
  and codex-beam both rated `03-07` LOW/LOW-MEDIUM.** The plan has Task 1's verify run
  `test_pio_scripts.py` after adding a library-source assertion that `lib/port/src` “either
  does not exist or contains no files”, while `lib/port/src/port.c` is not deleted until
  Task 3. The Task 1 commit therefore cannot be green as written. Source-verified and
  valid.
- **`03-01` `tests/src/main.c` rationale.** codex-beam (MEDIUM) argues the “compilation
  probe” is not needed for the native suite — the Unity test sources already include the
  libraries, so LDF pulls them — and is needed only for the `compiledb` purity proof;
  codex-glm and antigravity both endorse it as stated. The mechanism works either way, but
  the stated purpose is overstated and `test_build_src = false` should be explicit in the
  ini rather than relied on as a default.

### Source Verification of HIGH Findings

| Finding | Reviewer | Verdict | Evidence |
|---|---|---|---|
| `03-06` adapters are absent from the smoke project's `lib_deps`, so CDB verification cannot pass | codex-beam | **REFUTED** | `homeworks/0_0-toolchain-smoke/platformio.ini` target envs list `arduino=` / `espidf=` symlink deps |
| `03-08` `classify()` is bypassable via an embedded `..` segment (`common/../arduino/...`) | codex-glm | **CONFIRMED** | `03-08-PLAN.md` classify step: only leading `./` / `../` is `escape`; first segment otherwise decides the edge |
| `03-07` Task 1 asserts `lib/port/src` is empty before Task 3 deletes `port.c` | antigravity | **CONFIRMED** | `03-07-PLAN.md:176-177` vs. Task 3 file list at `:257` and removal step at `:272`; Task 1 verify runs the suite |
| Adapters lose their target-compile gate when the smoke project is deleted | antigravity | **CONFIRMED (design risk)** | `03-07-PLAN.md` Task 2 deletes `homeworks/0_0-toolchain-smoke`; no later Phase 3 plan builds `lib/arduino` / `lib/espidf` |

### Overall Risk

**MEDIUM.** All three reviewers converged on MEDIUM. The architecture, scope discipline and
verification strategy are strong; the concrete execution risks are the `03-07` task
ordering, the `03-08` classifier's `..` handling, and the absence of a post-Phase-3
target-compile gate for the adapters. None is architectural — each is a small, local fix.

### Recommended Pre-Execution Changes

1. **Fix `03-07` ordering:** either move the stub deletion into Task 1 before the suite is
   verified, or make the Task 1 library-source test tolerate the still-present
   `lib/port/src/port.c` and let Task 3 add the strict emptiness assertion.
2. **Tighten `03-08` `classify()`:** treat any include containing a `..` segment (not only a
   leading one) as an escape, reject absolute includes explicitly, and add negative fixtures
   for both.
3. **Narrow `03-09`'s wording:** the compile gate proves rejection of a *framework* include;
   relative cross-library includes are caught by the textual checker, not the compiler.
4. **Pin `03-04`'s hex failure contract** (`*out_length = 0` on failure) and test the
   zero-length and insufficient-capacity boundaries.
5. **Correct `03-01`'s `main.c` rationale** and make `test_build_src = false` explicit.
6. **Record the adapter-compile gap** as a known risk in the phase summary, or add a
   deferred note for a Phase 4/5 target-compile check.

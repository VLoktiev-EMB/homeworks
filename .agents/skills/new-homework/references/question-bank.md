# Question bank

This bank is the intake for `new-homework`. Acquire the homework id before the first
bank question: take it from `/new-homework <id>` when it is supplied, otherwise prompt
the user for it. Validate the id against `^[0-9]+_[0-9]+-[a-z0-9-]+$` before it
appears in any command or path, and stop on a mismatch. The id is deliberately outside
the eight topics below, so `mode` stays the first bank question.

When any intake input is missing, the agent MUST present questions using the native
multiple-choice tool (`ask_question` / `AskUserQuestion`) rather than open-ended plain
text prompts. Each question provides clear, concrete options with the recommended default
listed first prefixed by `(Recommended)`.

Record every answer in `.skill-state/<id>.json` under the state key named in its
section as soon as it is given, and never ask for a credential value.

## Preflight (not a bank topic)

Before `mode`, check whether the id already exists:
`git branch --list "hw/<id>"`, `git tag -l "hw/<id>"`,
`git ls-tree -r --name-only HEAD -- homeworks/<id>`, and the working tree at
`homeworks/<id>`. An existing branch, tag or homework means the id is published
or in progress: never scaffold a duplicate and never move the tag. Ask
`[Continue on hw/<id> | Start a new id | Stop]` and record the answer. The
preflight only decides whether to continue an existing homework; never read that
homework as a design example. If the id is free and the current branch is `main`
or `master`, create `hw/<id>` before the first write; if the current branch is
another branch, require `hw/<id>` or ask. Never scaffold or commit on the default
branch.

## Research gate (not a bank topic)

After provenance and before the scaffold, research the assignment against the board and
framework official documentation, the applicable IEEE/IEC/ANSI standard or component
datasheet, and at least one reputable practitioner source. Record
`intake.research.sources` with title, URL, and access date. A missing search or fetch tool
blocks the run; never invent a source.

If a requirement conflicts with a standard or accepted best practice, present the
discrepancy table from the skill
(`Requirement | Authority | Conflict or risk | Recommendation | Decision`) and ask before
scaffolding. Accepted rows go into the report's Assumptions table; the full table goes
into the Decision Appendix.

## mode

Select execution mode. The default is `direct` (clean, deterministic execution).

- **Question:** "Select execution mode for homework scaffolding and implementation:"
- **Options:**
  - `(Recommended) Direct: execute requested steps cleanly and deterministically without tutorial interruptions`
  - `Guided: interactive walkthrough with step-by-step explanations and pauses`

Direct records `mode: direct`; it asks only the intake it cannot infer, skips block
pauses and comprehension checks, scaffolds, writes the blocks, runs verifications,
and honours every guardrail confirmation. Guided records `mode: guided` and enables
interactive pauses.

## board

Select target board. The default is `esp32-s3-devkitc-1`.

- **Question:** "Select target hardware board:"
- **Options:**
  - `(Recommended) esp32-s3-devkitc-1 (Espressif ESP32-S3-DevKitC-1-N8)`
  - `Other (manual editing required; scaffold currently hardcodes esp32-s3-devkitc-1)`

The default board records `intake.board: esp32-s3-devkitc-1`. Any other board records
the requested value, states plainly that the scaffold hardcodes `esp32-s3-devkitc-1`,
and stops with an explicit unsupported-scaffold escalation. Never claim to scaffold an
arbitrary board.

## framework

Select framework. The default is `arduino`.

- **Question:** "Select development framework:"
- **Options:**
  - `(Recommended) Arduino (templates/homework-arduino)`
  - `ESP-IDF (templates/homework-espidf)`

The answer selects the scaffold template name: `arduino` or `espidf`, passed to
`scripts/new_homework --template`. Record `intake.framework`.

## language

Derived automatically from the framework answer rather than prompted.
- `arduino` -> `cpp` (Arduino C++)
- `espidf` -> `c` (native ESP-IDF C)

Record `intake.language` from `intake.framework`.

## specification

Format of the assignment specification.

- **Question:** "Select specification format for the assignment:"
- **Options:**
  - `(Recommended) Ready specification / English paraphrase provided`
  - `Free-form (derive acceptance criteria and record assumptions)`

A ready specification branches to recording the user-provided English paraphrase and
the source reference as data. A free-form task branches to deriving acceptance criteria
and recording assumptions. Neither branch stores raw internal course material.
Record `intake.specification` as `ready` or `free-form`.

## simulation

Simulation target.

- **Question:** "Select simulation target:"
- **Options:**
  - `(Recommended) None (hardware bench or native logic test only)`
  - `Wokwi simulation (consumes simulation quota)`
  - `Other`

Record `intake.simulation`. For `wokwi`, check if `WOKWI_CLI_TOKEN` is present in the
environment and record `intake.simulation_token_present` as `true` or `false`. Never ask
for, echo, or read/write the token itself.

## tests

Test strategy: does the homework contain pure logic of its own?

- **Question:** "Does the homework contain pure logic of its own?"
- **Options:**
  - `(Recommended) No pure logic — no test directory, and homework.yaml declares tests.framework: none`
  - `Pure logic — Unity native tests in a private-library suite test/test_<name>/`

A yes records `intake.tests: unity-native` with suite path `test/test_<name>/`, requires the
`[env:native]` block in `homeworks/<id>/platformio.ini` copied from `1_3` or `1_4`, and is
expected whenever the homework has pure logic; it is
never a copy of the shared contract tests in `tests/`. A no records `intake.tests: none`,
omits the native-tests block, ships no `test/` directory, and sets `tests.framework: none`
and `tests.native: false` in `homework.yaml`. The scaffold has no logic, so `none` is
correct for a fresh homework and the suite is added as soon as logic is introduced.

## deliverables

Required documents and artifacts.

- **Question:** "Select deliverables to produce:"
- **Options:** (multi-select)
  - `README and Report (standard)`
  - `Circuit diagram (assets/diagram.json & schematic.svg)`
  - `Bill of materials and electrical calculations`

Record answers in `intake.deliverables`. A bill of materials or calculations section
is a sub-section of the report block, never a separate sixth block.

---

The answers select the scaffold template, the block sequence and the report inputs.
The state file records each answer by key, so a changed answer re-opens exactly the
branch that reads that key.

After the intake topics and before the scaffold block writes, collect the four provenance
values for `task.md`: `source_url`, `retrieved`, `attribution` and `license`. Record them
under `intake.provenance` and set `intake.provenance.status: complete` only when all four
are real. While any value is missing or `TODO`, set `status: blocked` and leave
`homework.status: planned`.

The scaffold facts below are not questions, but every run must respect them:
1. Set `UV_CACHE_DIR="${TMPDIR:-/tmp}/uv-cache"` for every `uv run`, not only the scaffold,
   to isolate the cache across runs.
2. A homework-local private library manifest omits `frameworks` and `platforms` and never
   enters `lib_deps`, because the soft compatibility mode hides a framework-tagged library
   from the native environment and a later cleanup of `lib_deps` would break it silently.
3. Native tests repeat `-Wall -Wextra -Werror`, so reset both host fakes in `setUp` and seed
   the idle button `HIGH`, or a warning-level defect fails the test binary while the target
   build stays green.
4. Reuse `lib/common` before writing timing, debounce, CRC, hex or ring-buffer code.
   `common_elapsed_ms`, `common_timer_expired` and `common_debounce_update` already exist;
   a second implementation is a defect, not a style choice.
5. Put homework-specific pure logic in `homeworks/<id>/lib/<name>/` with a private
   `library.json` (no `frameworks` or `platforms`, never in `lib_deps`) and tests under
   `test/test_<name>/`. Keep the library free of framework headers, keep `src/main.cpp`
   a thin composition root, and reuse `lib/common` for timing.
6. `pio run` does not generate the clangd database. Run
   `pio run -d homeworks/<id> -t compiledb` and `uv run scripts/gen_clangd_db.py --generate`,
   then `"$HOME/.local/bin/clangd-wrapper" --check=homeworks/<id>/src/main.cpp`; expect
   `0 errors`. Without the per-project database, clangd reports
   `'Arduino.h' file not found`.
7. Register `homeworks/<id>` in `homeworks.code-workspace` when absent. The repository
   currently has no workspace generator, so append the folder entry idempotently; if a
   generator appears, run it instead.
8. Never inspect or copy an existing `homeworks/<id>` tree, branch or tag as an example.
   The templates, `lib/`, and the standards are the only sources of truth; the preflight
   only decides whether an existing homework is continued.

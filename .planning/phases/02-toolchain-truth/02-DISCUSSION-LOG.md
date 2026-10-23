# Phase 2: Toolchain Truth - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-10-23
**Phase:** 2-Toolchain Truth
**Areas discussed:** Shared configuration, Reference project, Shared libraries, Framework adapters, Native environment, Entry point, Library versions, compiledb location, Build evidence, Build order

---

## Shared configuration

| Option | Description | Selected |
|--------|-------------|----------|
| Root single file | One `platformio.shared.ini` at the repository root, consumed via `extra_configs`; pins live in one place, `lib_deps` stay per project | ✓ |
| Per-homework copy | Each homework gets its own generated copy, literally following ARCHITECTURE.md:220 | |
| Hybrid base + overlay | Root base with pins plus a per-homework overlay with `lib_deps` | |

**User's choice:** "треба обговорити" first, then root single file after the `extra_configs`/`extends` semantics were explained.
**Notes:** The PlatformIO behaviour that a duplicate key in the extra file wins made copies unattractive — 30+ copies would drift silently.

## Who generates the shared file

| Option | Description | Selected |
|--------|-------------|----------|
| Script + `--check` | `scripts/gen_shared_ini.py` with drift detection, matching the Phase 1 checker idiom | |
| Hand-authored, generator later | Write and commit the file now; generator arrives in Phase 5 | ✓ |
| Template without check | Generate from a template but without drift detection | |

**User's choice:** Hand-authored now, generator later.
**Notes:** Accepted that ROADMAP criterion 3's "generated" wording is satisfied only in Phase 5; recorded as D-03 so the verifier does not claim otherwise.

## Reference project location

| Option | Description | Selected |
|--------|-------------|----------|
| `examples/toolchain-smoke` | Lightweight project outside `homeworks/` | |
| `tests/` | Top-level native project, but that belongs to Phase 3 | |
| `homeworks/0_0-toolchain-smoke` | A real homework-shaped directory, later removed or promoted | ✓ |

**User's choice:** `homeworks/0_0-toolchain-smoke`.
**Notes:** Lifecycle was decided separately (see below).

## Reference project lifecycle

| Option | Description | Selected |
|--------|-------------|----------|
| Temporary, remove in Phase 3 | Deleted by a dedicated commit once `tests/` exists | ✓ |
| Permanent smoke project | Kept forever as a live proof and first CI matrix entry | |
| Phase 4 template source | Grown into `templates/` later | |

**User's choice:** Temporary, remove in Phase 3.

## Shared library content

| Option | Description | Selected |
|--------|-------------|----------|
| Minimal stubs | `library.json` plus one trivial symbol per library | ✓ |
| Minimal real code | A real `common` function plus a port contract and an adapter calling it | |

**User's choice:** Minimal stubs.

## Framework headers in adapters

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, framework headers | `lib/arduino` includes `<Arduino.h>`, `lib/espidf` includes an ESP-IDF driver header and calls one API function | ✓ |
| No, pure stubs | Adapters carry no framework headers; the build proves only the cross-compiler | |

**User's choice:** Yes, framework headers.
**Notes:** Without a framework header the ESP build would be tautological.

## Framework adapter coverage

| Option | Description | Selected |
|--------|-------------|----------|
| Both (Arduino + ESP-IDF) | Two ESP environments, both built | ✓ |
| Arduino only | ESP-IDF added in Phase 3/11 | |
| ESP-IDF only | Arduino adapter deferred | |

**User's choice:** Both.

## Native environment

| Option | Description | Selected |
|--------|-------------|----------|
| `pio run` only | Native environment builds a main; no Unity, no `test/` | ✓ |
| `pio test` with one Unity test | Proves `test_framework = unity` early | |
| Both | Main plus one Unity test | |

**User's choice:** `pio run` only; Unity and `tests/` stay in Phase 3.

## Entry point across two frameworks

| Option | Description | Selected |
|--------|-------------|----------|
| Conditional compilation | One `src/main.c` with `#ifdef ARDUINO` for `setup()`/`loop()` and `app_main()` otherwise | ✓ |
| Separate src directories | Per-environment `build_src_filter` into `src_arduino/` and `src_espidf/` | |
| Two separate projects | One Arduino project and one ESP-IDF project | |

**User's choice:** Conditional compilation.

## Library versioning

| Option | Description | Selected |
|--------|-------------|----------|
| `0.1.0` in `library.json` | Version declared once per library; `lib_deps` carries name only | ✓ |
| No `version` field | Minimal `library.json` | |
| Version in `lib_deps` | `name=version=symlink://...` | |

**User's choice:** `0.1.0` in `library.json`.

## compiledb location

| Option | Description | Selected |
|--------|-------------|----------|
| `scripts/pio/compiledb.py` | One shared extra script wired from the shared ini | ✓ |
| Built-in `pio run -t compiledb` | No custom script | |
| Per-project copy | A copy of the script in every project | |

**User's choice:** Shared script at `scripts/pio/compiledb.py`.

## Build evidence

| Option | Description | Selected |
|--------|-------------|----------|
| Do not commit logs | Evidence is a green `pio run` in session; only code and configs are committed | ✓ |
| Logs under `.planning/` | Build output kept locally for the verifier, not in git | |
| Commit the build log | Store the log in the phase directory in git | |

**User's choice:** Do not commit logs.
**Notes:** Committed logs age into false claims; the evidence contract is Phase 10's.

## Build order

| Option | Description | Selected |
|--------|-------------|----------|
| native → Arduino → ESP-IDF | Quick wiring proof first, risky espressif32 8.0.0 pin second | ✓ |
| ESP-Arduino first | Attack the riskiest pin first | |
| All libraries first | Horizontal build-out before environments | |

**User's choice:** native → Arduino → ESP-IDF.

---

## Claude's Discretion

- Exact stub symbol contents (a version-string accessor is the natural choice).
- Internals of `scripts/pio/compiledb.py`.
- Wording and length of the smoke project's `README.md`, provided it states the project is
  temporary and not coursework.

## Deferred Ideas

- Generation of `platformio.shared.ini` and a `--check` drift gate — Phase 5 (META-05).
- `tests/`, the Unity suite, and `test_framework = unity` — Phase 3.
- Deletion of `homeworks/0_0-toolchain-smoke/` — Phase 3, explicit task.
- `homework.yaml`, `task.md`, report contract — Phase 4 and Phase 10.
- CI matrix and changed-only detection — Phase 8.
- Architecture checker for the dependency rule — Phase 3 (ARCH-05).
- Fallback to `espressif32` 7.x or pioarduino if 8.0.0 fails — contingency only.

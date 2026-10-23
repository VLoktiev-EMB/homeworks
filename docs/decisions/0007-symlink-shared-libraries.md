---
status: accepted
date: 2026-10-23
decision-makers: [VLoktiev-EMB]
consulted: []
informed: []
---

# Symlinked shared libraries via lib_deps and library.json

## Context and Problem Statement

Every homework project needs the same shared libraries — `common`, `port`, and one
framework adapter — without copying their sources into thirty independent PlatformIO
projects. The repository keeps those libraries under `lib/<name>/`, so the question is how a
project under `homeworks/<id>/` makes the Library Dependency Finder (LDF) see them: by
declaring a dependency on each library, by pointing the LDF at the whole `lib/` tree, or by
duplicating the sources per project.

The answer is permanent: the `lib/` directory names become the dependency vocabulary that
Phase 3's architecture rule enforces, and every future project repeats the chosen spelling in
its `platformio.ini`. The decision also fixes where a library version is declared, because a
second declaration site would drift silently.

## Decision Drivers

* A project must depend on exactly the libraries it names; an unrelated framework adapter
  must never enter a build because it happened to sit in the same directory.
* The library sources must stay single-copy: a fix in `lib/common` must reach every consumer
  without a synchronisation step.
* PlatformIO 6.0 deprecated `lib_extra_dirs`, so a new project should not adopt it (State of
  the Art: the LDF no longer scans all of `lib/`).
* A library version must be declared exactly once, or the build graph and the documentation
  will disagree.
* The spelling must work unchanged for `native`, `esp32s3_arduino` and `esp32s3_espidf`.

## Considered Options

* `lib_deps = <name>=symlink://../../lib/<name>` with a `library.json` per library
* `lib_extra_dirs` pointing each project at the repository `lib/` directory
* Copying the shared library sources into every project

## Decision Outcome

Chosen option: "`lib_deps = <name>=symlink://../../lib/<name>` with a `library.json` per
library", because it is the only option that names each dependency explicitly, keeps one
copy of the sources, and survives the PlatformIO 6.0 deprecation of `lib_extra_dirs`.

Each project declares:

```ini
lib_deps =
    common=symlink://../../lib/common
    port=symlink://../../lib/port
    host=symlink://../../lib/host
```

The path resolves relative to the project directory. The Package Manager records the link in
`.pio/libdeps/<env>/<name>.pio-link` and never copies the sources, so an edit in `lib/` is
visible to the next build immediately.

Every library carries a `library.json` with `name`, `version`, `build.srcDir` and
`build.includeDir`. The directory name and the manifest `name` must agree, because the
`<name>=` alias and the LDF lookup both key on it. The version lives only in `library.json`
(D-12); a `lib_deps` entry never carries `@version`, and no other file repeats the version.

The LDF no longer scans the whole `lib/` tree, so a project sees only the adapters it names.
A foreign adapter cannot enter a build by proximity, which is what Phase 3's dependency rule
will enforce across all homework projects.

### Consequences

* Good, because a project's dependency set is explicit and reviewable in its own
  `platformio.ini`, and an unrelated adapter cannot leak into the build.
* Good, because the library sources exist once; a fix reaches every consumer with no
  copy-and-sync step.
* Good, because the version has a single home in `library.json`, so the LDF graph and the
  documentation cannot disagree about it.
* Bad, because every library needs a manifest: a directory without `library.json` fails with
  `MissingPackageManifestError`, so adding a library is two files, not one.
* Bad, because the `../../lib/<name>` spelling repeats in each project and must be kept
  relative, so a project at a different depth needs its own correct prefix.
* Neutral, because the resolved link depends on the Package Manager's `.pio/libdeps` cache,
  which is gitignored build output and is recreated by any build.

### Confirmation

This phase proved the decision by building the temporary reference project
`homeworks/0_0-toolchain-smoke/` in all three environments: `native`, `esp32s3_arduino` and
`esp32s3_espidf` each ended in `[SUCCESS]`, and each LDF graph named the libraries it
declared as `0.1.0`.

The compilation database, generated immediately after each environment's own build, records
`lib/common/src/common.c`, `lib/port/src/port.c` and the framework adapter's source next to
`src/main.cpp` for both ESP frameworks, so the shared sources really compile rather than
merely being declared. The Arduino entry point preprocesses to `#define CONFIG_SPIRAM 1`, and
`esptool image-info` reports `Flash size: 16MB` for both ESP images, so the same wiring holds
under both frameworks and under the N16R8 configuration.

`scripts/tests/test_pio_scripts.py` pins the contract: the five manifests agree with their
directories, the library sources are pure C behind `extern "C"` headers, the shared
configuration declares the three sections, and the `lib_deps` entries use the `symlink://`
spelling. A change that reintroduces `lib_extra_dirs`, copies a library, or adds a second
version declaration fails that suite.

## Pros and Cons of the Options

### `lib_deps = <name>=symlink://../../lib/<name>` with a `library.json` per library

Declare each shared library as a named dependency whose source is a symlink to `lib/<name>`,
with the version and build layout in the library's own manifest.

* Good, because the dependency set is explicit: only the named libraries enter the build.
* Good, because the sources are not copied, so a library fix reaches every consumer at once.
* Neutral, because each library must ship a `library.json`, which is also where its version
  lives.
* Bad, because the relative path spelling repeats in every project and depends on the
  project's depth in the tree.

### `lib_extra_dirs` pointing each project at the repository `lib/` directory

Add `lib_extra_dirs = ../../lib` so the LDF scans the whole shared tree.

* Good, because a new library needs no per-project edit to become visible.
* Bad, because it is deprecated since PlatformIO 6.0 and may be removed in a later core
  release.
* Bad, because the LDF scans everything in `lib/`, so an unrelated framework adapter can be
  pulled into a build that never asked for it.
* Bad, because it states a directory rather than a dependency, so the build graph does not
  record what the project actually uses.

### Copying the shared library sources into every project

Duplicate `lib/<name>/` into each homework project.

* Good, because each project is self-contained with no shared-path assumption.
* Bad, because thirty copies drift, and a fix must be applied thirty times.
* Bad, because the repository's single-source architecture and the Phase 3 dependency rule
  both assume one `lib/` tree.
* Bad, because the duplication would enter every report artifact and inflate history with
  copies of the same code.

## More Information

The claim in `.planning/research/ARCHITECTURE.md` that `platformio.shared.ini` is "generated
per homework" is superseded by this decision (D-05); the shared configuration is one committed
root file that each project consumes through `extra_configs`.

Generation of that shared file, with a drift check, is Phase 5 (META-05). Phase 2 commits the
file by hand and proves only its consumption, so this record must not be read as claiming
that a generator already exists.

The temporary reference project that produced the evidence is deleted in Phase 3, when the
shared Unity test project supersedes it; the decision and the manifest contract it describes
remain.

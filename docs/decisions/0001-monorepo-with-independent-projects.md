---
status: accepted
date: 2026-10-23
decision-makers: [VLoktiev-EMB]
consulted: []
informed: []
---

# Monorepo with independent PlatformIO projects

## Context and Problem Statement

The course will accumulate more than thirty homework assignments, released two to three per
week, each tied to a specific board and framework and each graded, flashed, and simulated on
its own. The syllabus is progressive: later assignments reuse ideas from earlier ones but
must remain independently reproducible a year after publication. How should the assignments
be arranged so that a single homework can be built, tested, and read without unpacking the
whole course, while the course itself remains one coherent, auditable repository?

## Decision Drivers

* Per-project isolation: a homework's dependency set, board configuration, and build flags
  must not be affected by any other homework.
* A single CI surface: one workflow set, one caching strategy, and one quality-gate
  definition should cover every assignment.
* One metadata contract: every homework declares the same `homework.yaml` fields so that a
  README index and a documentation site can be generated from the same source.
* Stable identifiers: the directory name of a published homework is a permanent
  cross-reference from tags, reports, and the generated index.

## Considered Options

* Polyrepo: one repository per homework
* Monorepo with a shared `src/` tree
* Monorepo with independent PlatformIO projects

## Decision Outcome

Chosen option: "Monorepo with independent PlatformIO projects", because it is the only
option that satisfies per-project isolation and a single CI surface at the same time, and it
keeps each homework a self-contained PlatformIO project that still builds on its own.

Each homework lives in its own directory as a complete PlatformIO project with its own
`platformio.ini`. Directories are named `module_lesson-name` (for example
`1_3-police-flasher`), which preserves the course order in the filesystem and in a plain
lexical sort, and conveys the topic without a lookup. Once a homework directory is published
its name is never changed, so external references stay valid; the identifier is permanent
from publication onward.

### Consequences

* Good, because a homework can be opened, flashed, and graded in isolation; nothing in the
  repository layout forces a reader to understand the other thirty assignments.
* Good, because shared tooling, shared libraries, policy, and CI live once at the repository
  root instead of being copied thirty times.
* Good, because a single `homework.yaml` contract makes the README index and the
  documentation site generated artifacts rather than hand-maintained duplicates.
* Bad, because the repository grows large and a full build of every homework is expensive;
  CI must therefore build and simulate only what a change touches.
* Bad, because a careless change at the root (shared configuration, shared library) can
  affect every homework at once; shared changes need the widest verification.

### Confirmation

Every homework directory builds standalone: running `pio run` inside it, with no other
homework present on the path, succeeds under its own `platformio.ini`. The Phase 8 CI
workflow reinforces this by building changed projects from their own directories. The
naming rule is confirmed by inspection of the directory name and by the generated index,
which reads the name rather than a separate label.

## Pros and Cons of the Options

### Polyrepo: one repository per homework

One repository, one CI pipeline, one issue tracker per assignment.

* Good, because isolation is absolute; no root change can affect another assignment.
* Good, because each repository stays small and cloneable in seconds.
* Bad, because shared libraries, tooling, policy, and templates must be duplicated or
  versioned across thirty repositories.
* Bad, because a course-wide change (a license line, a formatter pin, a template) becomes
  thirty pull requests and thirty chances to drift.
* Bad, because the generated index and documentation site would have to aggregate content
  across repositories.

### Monorepo with a shared `src/` tree

One repository where homework source files are collected in a single source tree with
per-board configuration selected at build time.

* Good, because cross-homework reuse is frictionless; a helper is imported, not published.
* Neutral, because it works well when every assignment is a variation of one program.
* Bad, because the assignments are not variations of one program — each has its own
  framework, board, and entry point, so a shared tree needs conditional build logic that is
  itself a maintenance burden.
* Bad, because a homework stops being self-contained: extracting one assignment for grading
  means understanding the shared tree first.
* Bad, because dependency isolation is lost; every assignment resolves against one combined
  dependency set.

### Monorepo with independent PlatformIO projects

One repository whose top-level directories are complete PlatformIO projects.

* Good, because each homework is a valid PlatformIO project on its own, matching how the
  course is taught and graded.
* Good, because shared configuration is opt-in through PlatformIO's `extra_configs` and
  shared libraries through explicit `lib_deps` entries, so reuse never becomes implicit.
* Good, because one workflow set and one policy check cover the whole course.
* Neutral, because the repository needs path filters in CI to stay responsive; that is
  ordinary monorepo tooling rather than a structural compromise.
* Bad, because a single clone carries the whole course, which grows over time.

## More Information

The reuse mechanism this decision depends on — thin shared libraries consumed through
PlatformIO `lib_deps` rather than a universal hardware abstraction — is recorded in
[ADR-0002](0002-ports-and-adapters-no-universal-hal.md). The naming convention is part of the
FOUND-02 commitment that published identifiers stay stable. The decision is revisited only if
the course is split into separate published repositories, which would require a deliberate
migration of every cross-reference.

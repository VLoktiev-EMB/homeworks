---
status: accepted
date: 2026-10-23
decision-makers: [VLoktiev-EMB]
consulted: []
informed: []
---

# Ports and adapters, no universal hardware abstraction layer

## Context and Problem Statement

Several homework assignments need the same non-trivial behavior — debouncing, state
machines, protocol framing, unit conversion — on different boards and frameworks. Copying
that logic into every project makes fixes multiply; wrapping every framework call behind a
home-grown hardware abstraction layer (HAL) hides the APIs the course exists to teach. How
can shared logic be reused without building a shadow framework that competes with Arduino,
ESP-IDF, and the STM32 frameworks?

## Decision Drivers

* The course teaches the framework's own APIs; a student must see `digitalWrite`, ESP-IDF
  drivers, and STM32 HAL calls, not a private dialect.
* Hardware abstractions leak: a universal interface that covers GPIO and I2C breaks down on
  timers, DMA, interrupts, and power management, and the leak becomes the lesson.
* Shared logic must be testable on the host, without a board and without a toolchain.
* Dependencies must point in one direction, so a change in one homework cannot silently
  change another.

## Considered Options

* A universal HAL owned by the repository
* Ports and adapters with thin, per-framework adapters
* No abstraction at all: copy the logic into each homework

## Decision Outcome

Chosen option: "Ports and adapters with thin, per-framework adapters", because it allows
pure logic to be shared and host-tested while keeping every framework API visible to the
student and every hardware-specific detail at the edge of the program.

The dependency rule is: `lib/common` depends on nothing; `lib/port` declares the interfaces
and depends on `common`; each adapter (`lib/arduino`, `lib/espidf`, and later the STM32
adapter) implements the ports and depends on `port`; a homework depends on `common`, `port`,
and exactly one adapter. A homework never depends on another homework, and `common` never
depends on a framework.

### Consequences

* Good, because pure logic is shared once, unit-tested natively, and fixed in one place.
* Good, because the lesson still shows the real framework API; the adapter is a thin seam,
  not a replacement vocabulary.
* Good, because the dependency rule is mechanically checkable, so architectural drift is a
  failing check rather than a review comment.
* Bad, because a port has to be designed before the first two implementations exist, which
  risks shaping it around one board; the rule that an adapter stays thin limits the damage.
* Bad, because there is slightly more ceremony per hardware touch than calling the framework
  directly.

### Confirmation

Phase 3 builds `common`, `port`, and the adapters together with an architecture check that
fails when the dependency rule is violated — in particular when `common` imports a framework
header, when a homework depends on more than one adapter, or when an adapter is depended on
by another library. Native unit tests cover the pure logic in `common`. The check runs
locally and joins CI in the same phase that introduces it.

## Pros and Cons of the Options

### A universal HAL owned by the repository

One interface set covering every board and framework, with one implementation per platform.

* Good, because homework code is board-agnostic and reads identically everywhere.
* Neutral, because the interface hides the framework, which is acceptable only if the
  framework is not itself the subject.
* Bad, because the course's subject *is* the framework API; the abstraction removes the
  lesson.
* Bad, because the interface necessarily leaks at timers, DMA, interrupts, and power modes,
  so it grows into an incomplete framework that the repository then has to maintain.
* Bad, because it is the single largest maintenance surface in the repository and the
  hardest to test.

### Ports and adapters with thin, per-framework adapters

Small interfaces for the specific shared behaviors, implemented once per framework.

* Good, because only the logic that genuinely recurs is abstracted; the rest stays idiomatic.
* Good, because the ports are host-testable fakes, so shared logic is provable without
  hardware.
* Good, because responsibility is unambiguous: an adapter's job is to translate, never to
  decide.
* Neutral, because each new framework needs its adapters written by hand.
* Bad, because a poorly chosen port can force translation work that buys nothing; that is
  corrected by keeping ports narrow.

### No abstraction at all: copy the logic into each homework

Each homework carries its own copy of any shared algorithm.

* Good, because a homework is completely self-contained with zero shared-library machinery.
* Good, because there is no interface design to get wrong.
* Bad, because every bug fix and every refinement is applied N times or drifts.
* Bad, because the same logic is tested N times or not at all.
* Bad, because the course cannot demonstrate reuse, which is itself a learning objective.

## More Information

The functional requirements this decision serves are ARCH-01 through ARCH-07. The monorepo
layout that makes the shared libraries available is recorded in
[ADR-0001](0001-monorepo-with-independent-projects.md); the libraries are consumed through
explicit PlatformIO `lib_deps` entries rather than a discovery directory, so the dependency
rule is visible in each homework's `platformio.ini`.

---
status: accepted
date: 2026-10-24
decision-makers: [VLoktiev-EMB]
consulted: []
informed: []
---

# Common depends on port; ports are consumer-owned

## Context and Problem Statement

ADR-0002 accepted ports and adapters and, in the same record, stated a dependency rule:
`lib/common` depends on nothing, and `lib/port` declares the interfaces and depends on
`common`. The shared-core work that followed reached the opposite conclusion. The pure
logic in `lib/common` — timing, buffers, framing — is exactly the code that must call an
injected clock, pin or bus, and a call requires the declaration in scope, so `common` has
to include `port` headers. The two documents cannot both be right, and a repository whose
shared sources encode one direction while its accepted record states the other leaves the
next contributor to guess. The same problem applies to the words "port contains no state":
every contract carries a `void *ctx`, so the phrase needs a precise meaning. Which edge is
allowed, and what does the opaque pointer own?

## Decision Drivers

* The shared logic in `lib/common` must call time, GPIO, bus and logging operations without
  compiling against a framework.
* `lib/port` must stay includable from both C and C++ with no project header of its own, so
  every adapter and every test double compiles against it first and independently.
* Exactly one include direction must be checkable mechanically, so architectural drift
  becomes a failing check instead of a review comment.
* A contract must allow more than one instance in one process — two buses, two timers — and
  must let every test own an isolated instance.
* The rule must be visible in each project's dependency list, not inferred from a directory
  scan.

## Considered Options

* `common` depends on `port`, with consumer-owned contracts
* The ADR-0002 wording: `port` depends on `common`
* No ports: copy the shared logic into each homework

## Decision Outcome

Chosen option: "`common` depends on `port`, with consumer-owned contracts", because only
this direction lets the pure logic call an injected operation while `port` remains a leaf
that adapters, test doubles and the host fake can implement independently.

The dependency rule is: `lib/port` depends on nothing — no project header, no framework
header, C standard headers only; `lib/common` may include `port` headers and call the
injected functions; every adapter (`lib/arduino`, `lib/espidf`) and the host double
(`lib/host`) depends on `port` only; a homework depends on `common`, `port` and exactly one
adapter. The reverse edges — `port → common`, `port → adapter`, `adapter → common` — and any
framework header inside `common` or `port` are forbidden.

This record supersedes exactly one sentence of
`0002-ports-and-adapters-no-universal-hal.md`: the sentence beginning "The dependency rule
is" in that record's Decision Outcome. ADR-0002 remains accepted and is not edited; its
decision — ports and adapters rather than a universal HAL — and every other paragraph stand
unchanged. A reader applies this record to that one sentence and ADR-0002 to everything
else.

`lib/port` declares function-pointer structs that each carry a `void *ctx`. "Port contains
no state" means that `port` owns no global mutable state and mutates nothing; the state
behind `ctx` belongs to the adapter that produced the instance or to the test double that
replaced it. That ownership is what permits two instances in one process — two buses, two
timers — because each instance carries its own context, and it is what gives each test its
own isolated fake. The consequence is that a consumer holds a borrowed `const` pointer for
the duration of a call and never stores it in a global.

### Consequences

* Good, because the shared logic is testable on the host with no board and no target
  toolchain; the framework exists only behind an adapter.
* Good, because there is exactly one include direction to reason about, so a new library's
  place in the graph follows from who includes whom.
* Good, because the rule is mechanically enforceable: a textual include scan rejects every
  edge outside the matrix, and a native compile proves that `common` and `port` stay
  framework-free.
* Bad, because a port must be designed before its second implementation exists, and a port
  shaped around one board costs translation work later; keeping ports narrow limits the
  damage.
* Bad, because the checker is textual: it reads `#include` lines, so a computed include or
  a build-system alias could evade it, and transitive purity still depends on the native
  compile gate.

### Confirmation

This phase ships the gate that confirms the decision: `scripts/check_architecture.py`
scans the `#include` lines under `lib/**` and `homeworks/**` against the edge matrix and
starts with an empty allowlist, so no exception exists at acceptance time;
`pio test -d tests -e native` builds `common`, `port` and `host` on the host and runs the
shared Unity suite, which fails if either shared library reaches for a framework; and the
pre-commit hook `check-architecture` runs the checker on every local commit. These are
this phase's gate. Moving them into CI is Phase 8's work, and this record does not claim
that CI runs them today.

## Pros and Cons of the Options

### `common` depends on `port`, with consumer-owned contracts

`lib/port` is a leaf of function-pointer structs; `lib/common` includes those headers and
calls through a borrowed instance.

* Good, because pure logic can call time and I/O without naming a framework, so the same
  source compiles natively and on target.
* Good, because the contract belongs to the consumer: the interface states what `common`
  needs, not what one adapter happens to offer.
* Neutral, because every new operation is a small struct plus an adapter function —
  ceremony the first time, cheap thereafter.
* Bad, because a port can be designed too early and fit the first adapter rather than the
  second; narrow ports and copying twice before extracting contain that risk.

### The ADR-0002 wording: `port` depends on `common`

`lib/port` includes `common` headers and declares its interfaces in terms of common types;
`common` depends on nothing.

* Good, because `common` would be a dependency-free leaf and trivially testable in
  isolation.
* Neutral, because the direction reads naturally if a port is imagined as a description of
  what common needs.
* Bad, because it cannot express the actual requirement: `common` must call the port, and a
  call requires the declaration in scope.
* Bad, because a port written in terms of `common` types ties the interface to common's
  current API and makes either side hard to change.
* Bad, because reversing the direction later touches every shared source, adapter and
  homework include graph, so the cost is repository-wide.

### No ports: copy the shared logic into each homework

Each homework carries its own copy of the timing, buffer and framing helpers and calls its
framework directly.

* Good, because there is no interface to design and no dependency edge to enforce.
* Good, because a homework remains a single self-contained project.
* Bad, because fixes and refinements multiply across more than thirty projects.
* Bad, because host-testing the logic then needs a per-homework harness, so the suite is
  duplicated or skipped.
* Bad, because it contradicts ADR-0002's accepted decision and the course's reuse
  objective.

## More Information

The deferred exception: Arduino I2C and SPI adapters will have to ship as `.cpp` because
`Wire` and `SPI` are C++ classes with no C API. The public C headers do not change, and the
exception is recorded when those adapters are written rather than now, because this phase
defers them to the first homework that needs them. The ESP-IDF adapters can stay `.c`
because the driver and GPIO headers are C.

This record amends [ADR-0002](0002-ports-and-adapters-no-universal-hal.md) in one sentence
and inherits its rationale, its option analysis and its consequences. The `symlink://`
mechanism that makes `lib/port` and `lib/common` visible to a project is recorded in
[ADR-0007](0007-symlink-shared-libraries.md); because of that mechanism the dependency rule
this record fixes is visible in each project's own `lib_deps` list rather than inferred
from a directory scan.

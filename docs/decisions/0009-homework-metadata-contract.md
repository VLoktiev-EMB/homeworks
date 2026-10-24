---
status: accepted
date: 2026-10-24
decision-makers: [VLoktiev-EMB]
consulted: []
informed: []
---

# Homework metadata contract

## Context and Problem Statement

Every homework directory carries one `homework.yaml` next to its `task.md`. That single file
is read by five different consumers: a YAML language server in an editor, the repository
checker `scripts/check_metadata.py`, the scaffold `scripts/new_homework` that renders new
homework directories, the Phase 5 generators (README index, MkDocs navigation, multi-root
workspace, `platformio.shared.ini`, CI matrix), and Phase 8 CI. If each consumer decided for
itself which fields exist and what they mean, the field set would drift the first time one of
them was edited alone, and a homework accepted by the scaffold could fail the checker or the
generator. What shape should the metadata contract take, where should it live, and how should
every consumer be bound to the same answer?

## Decision Drivers

* One machine-readable source must define the field set, the enum vocabularies and the
  required/optional split.
* Validation must not be implemented twice: the scaffold, the checker and the future CI job
  must apply the same rules by construction, not by review.
* The metadata is reproducibility evidence: a reader a year later must be able to see exactly
  which toolchain a homework was built with, without re-deriving it from the build output.
* Editors should flag an unknown key or a bad enum while the file is being typed, before any
  script runs.
* The contract must be strict enough that a typo is a failure, and expressive enough that the
  optional blocks are typed rather than free-form.
* Provenance must be authoritative in exactly one place, while the metadata still records the
  source it refers to.

## Considered Options

* A JSON Schema 2020-12 document at `schema/homework.schema.json`, applied by one shared
  Python validator.
* A Python-only validator with no schema document.
* Per-field ad-hoc checks written inside `scripts/check_metadata.py`.

## Decision Outcome

Chosen option: "A JSON Schema 2020-12 document at `schema/homework.schema.json`, applied by
one shared Python validator", because only a committed schema gives editors, the checker, the
scaffold and Phase 5 generators one declarative source of truth while the shared validator
keeps the runtime behaviour identical everywhere.

The schema is JSON Schema 2020-12 with `$defs`. It carries `additionalProperties: false` at
the top level and inside every nested block, so an unknown key anywhere is an error rather
than a silently ignored typo. Required fields are `schema_version`, `id`, `title`, `board`,
`framework`, `language`, `status`, `source` and `toolchain`; optional blocks are `simulation`,
`tests`, `report` and `assets`, each typed by a `$def` rather than left free-form.

`scripts/metadata/contract.py` is the single validation implementation. It loads the schema,
rejects a schema that does not validate, applies it with `jsonschema`, and adds the checks a
schema cannot express: the identity invariant between `id` and the containing directory name,
the toolchain cross-check against `platformio.shared.ini`, and the `task.md` provenance rules.
`scripts/check_metadata.py` and `scripts/new_homework` both import that module, so the
scaffold and the checker cannot disagree (D-12).

Shape checks are anchored `pattern` expressions, never the `format` keyword. `jsonschema`
treats `format` as an annotation unless a `format_checker` is supplied, and even then the
`uri` and `date-time` checkers live in optional extras, so a missing extra would validate
`"not a url"` silently. URL shape and ISO 8601 are therefore enforced by an anchored pattern
and by the standard library, not by an optional dependency.

### Consequences

* Good, because a schema document is readable by an editor, so a mistake surfaces while the
  file is open instead of at the next pre-commit run.
* Good, because one shared validator makes the scaffold, the checker and Phase 8 CI agree by
  construction; a rule change is one edit.
* Good, because the schema is committed data reviewed in a pull request, so widening or
  narrowing the contract is visible in history.
* Bad, because two artefacts — the schema and the validator — must stay coherent; the
  validator's extra rules are not expressible in the schema and need their own tests.
* Bad, because `additionalProperties: false` makes every new field a breaking change for
  homework files written against the previous schema; the integer `schema_version` exists to
  make that migration explicit.
* Neutral, because the schema's `$defs` indirection adds a layer of reading for a field set
  this small, and earns its place only when the optional blocks grow.

### Confirmation

The gate that confirms this decision is runnable today, by a developer:

* `uv run scripts/check_metadata.py` applies the schema and the provenance rules to every
  `homeworks/*/` directory and exits `0`, `1` or `2` under the repository's exit-code
  convention.
* `python3 -m unittest discover -s scripts/tests -v` runs the negative-fixture matrix that
  proves the schema rejects unknown keys at every level, invalid enums, malformed patterns,
  duplicate assets and identity mismatches.
* `pre-commit run --all-files` runs the `check-metadata` hook, which invokes the same checker
  in an isolated environment.

Phase 8 wires CI to run the same commands on every pull request. Phase 8 wires CI; this
record does not claim that CI runs them today, and no consumer may cite a CI job as
evidence before that phase lands.

## Pros and Cons of the Options

### A JSON Schema 2020-12 document at `schema/homework.schema.json`, applied by one shared Python validator

The schema declares the contract and is consumed by editors; `scripts/metadata/contract.py`
loads it, validates it, and applies it for the checker and the scaffold.

* Good, because the same declaration serves a human editor and every machine consumer, so
  there is no prose-to-code gap to maintain.
* Good, because `additionalProperties: false` and the enum vocabularies make a typo a
  failure by construction rather than a review observation.
* Good, because a schema is a familiar artefact: Phase 5 generators and Phase 8 CI can read
  it without learning a repository-specific DSL.
* Neutral, because the schema and the validator's extra rules are two places to look; the
  split is stated in this record so a reader knows which layer owns which rule.
* Bad, because `format` is deliberately unused and two shape checks are reimplemented as
  patterns plus stdlib code, which is more verbose than the keyword would be.

### A Python-only validator with no schema document

`scripts/metadata/contract.py` encodes the field set, types, enums and required keys directly
in Python, and there is no `schema/homework.schema.json`.

* Good, because there is exactly one artefact to edit, so the schema-validator coherence
  problem disappears.
* Good, because arbitrary Python can express cross-field rules — identity, toolchain drift,
  provenance — in the same place as the field set.
* Bad, because an editor cannot consume a Python validator, so the field set is discovered by
  running a script instead of while typing.
* Bad, because Phase 5 generators and Phase 8 CI would either import repository code or
  parse it, and a non-Python consumer has no entry point at all.
* Bad, because the field set stops being reviewable as data and becomes mixed into
  imperative validation logic.

### Per-field ad-hoc checks written inside `scripts/check_metadata.py`

Each field is checked where it is encountered, with no schema and no shared module.

* Good, because the first homework could be validated with no upfront design.
* Good, because a single-file checker is the smallest possible change to the existing tree.
* Bad, because `scripts/new_homework` must validate a candidate before writing, so the rules
  would be duplicated in the scaffold and drift on the first edit — exactly the failure D-12
  forbids.
* Bad, because there is no declarative field set for editors, generators or Phase 8 CI to
  consume.
* Bad, because the checks become order-dependent: a field validated only when a later branch
  reaches it silently stops being validated after a refactor.

## More Information

### The locked vocabulary

* **Required fields:** `schema_version`, `id`, `title`, `board`, `framework`, `language`,
  `status`, `source`, `toolchain`.
* **Optional blocks:** `simulation`, `tests`, `report`, `assets` — typed, never free-form.
* **`schema_version`:** the integer `1`, declared as `const`, not a string or a semver range.
* **`status`:** exactly four values — `planned`, `in-progress`, `complete`, `verified`. This
  is the published state model consumed by generated views and CI, so the vocabulary is
  expensive to change.
* **Derived identity:** `module`, `lesson`, `slug` and the display `title` are derived from
  `id` and never stored (D-02). The rule is fixed: split `id` at the first underscore to get
  the module and the remainder; split that remainder at the first hyphen to get the lesson and
  the slug; the display title is the slug with every remaining hyphen replaced by a space and
  title-cased per word. For `1_3-police-flasher` that yields module `1`, lesson `3`,
  slug `police-flasher` and title `Police Flasher`.
* **Strictness:** `additionalProperties: false` at the top level and inside every `$def`, so
  an unknown key at any depth is an error. `unevaluatedProperties` is not used because no
  object-level `allOf`/`anyOf` composition exists.
* **Shape over `format`:** every shape — the identifier, the board id, the toolchain pins,
  relative POSIX asset paths, URLs — is an anchored `pattern`, and ISO 8601 is checked with
  the standard library. The `format` keyword is never relied on.
* **Split authority between `source.reference` and `task.md`:** `homework.yaml` carries one
  required `source.reference` — the source title or URL — while the canonical provenance
  record (`source_url`, `retrieved`, `attribution`, `license`) lives in `task.md` frontmatter
  (D-15). When both carry a URL they must agree; a mismatch is a violation, not a warning.

### The sentinel rule

The scaffold must ship a `task.md` skeleton before a human has collected provenance, and the
provenance contract must still reject an unfinished published homework (D-30 versus D-16).
The resolution is one status-gated sentinel, and the fields it may appear in are exactly
these five, and no others:

1. `task.md` `source_url`
2. `task.md` `retrieved`
3. `task.md` `attribution`
4. `task.md` `license`
5. `homework.yaml` `source.reference`

In each of those five fields the literal string `TODO` is legal **only** while
`homework.yaml` carries `status: planned`. The moment the status becomes `in-progress`,
`complete` or `verified`, the sentinel is a violation and the full shape checks apply. The
extension of the rule from the four `task.md` fields to `homework.yaml` `source.reference` is
itself part of the decision, not a summary note: `source.reference` is provenance-bearing, and
leaving it ungated would make the scaffold's own output fail the checker it was validated
against.

Body `TODO`s in `task.md` prose are manual-review signals, not status-gated values. They are
never machine-checked, and a reader must not infer a machine check that does not exist. Only
the five fields listed above participate in the sentinel rule.

### Consumers and the phase boundary

*schema/homework.schema.json* is the path editors, the checker, the scaffold, the Phase 5
generators and Phase 8 CI all resolve. `AGENTS.md` names the same path as a repository
contract, so the rulebook and the tooling cannot describe different trees. The field-to-
consumer mapping is Phase 5's artefact; this record names the known consumers and deliberately
does not duplicate that mapping (D-38).

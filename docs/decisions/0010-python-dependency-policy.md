---
status: accepted
date: 2026-10-24
decision-makers: [VLoktiev-EMB]
consulted: []
informed: []
---

# Python dependency policy

## Context and Problem Statement

Two repository entry points need third-party Python packages: `scripts/check_metadata.py`
and `scripts/new_homework`, which both require `PyYAML` and `jsonschema` with fixed
versions. The checker runs in three places — a developer's shell, the `check-metadata`
pre-commit hook, and, from Phase 8, CI — and the scaffold runs in a developer's shell and in
the test suite. A dependency policy must deliver exact pins to all of them without a global
install, without depending on whichever interpreter happens to be active, and without
breaking the repository rule that `python3 -m unittest discover -s scripts/tests` stays
dependency-free (D-14). How should those packages be declared and delivered?

## Decision Drivers

* Every dependency must carry an exact pin, so a script behaves identically on every machine
  and in CI.
* Delivery must not rely on the developer's active interpreter or an activated virtual
  environment, because pre-commit and CI each start from a different one.
* The declarations must be checkable: two delivery paths are acceptable only if a test can
  prove they agree.
* The repository test suite must keep running under the standard library alone, so a test
  that exercises the validator shells out rather than importing the packages.
* Adding a script should not require editing a shared requirements file that several
  unrelated tools also read.

## Considered Options

* PEP 723 inline script metadata run by `uv`, plus an isolated `language: python` pre-commit
  environment with explicit `additional_dependencies`.
* A `requirements-dev.txt` installed by hand, with the hook declared `language: system`.
* A repository-level virtual environment that both the scripts and the hook activate.

## Decision Outcome

Chosen option: "PEP 723 inline script metadata run by `uv`, plus an isolated `language:
python` pre-commit environment with explicit `additional_dependencies`", because each
delivery path owns its own environment and both declare the same exact pins, while a
stdlib-only drift test proves the two declarations agree.

Both entry scripts carry a PEP 723 block:

```text
# /// script
# requires-python = ">=3.11"
# dependencies = ["PyYAML==6.0.3", "jsonschema==4.26.0"]
# ///
```

`uv run scripts/<script>` resolves that block into an ephemeral environment, so the script
never reads the developer's interpreter. The `check-metadata` hook in
`.pre-commit-config.yaml` declares `language: python` with the same
`additional_dependencies`, so pre-commit builds and owns its own environment and does not
need `uv` on `PATH`. `scripts/tests/test_metadata_deps.py` parses both declarations as text
and fails when a pin is missing from either side, when an extra pin appears, or when the
`files` pattern stops covering the checker, the scaffold, `schema/` or `homeworks/`.

### Consequences

* Good, because every consumer gets exact pins without a global or user-level install.
* Good, because the hook is independent of `uv`: a developer who has `pre-commit` but not
  `uv` can still commit, and CI can install only what it needs.
* Good, because the stdlib drift test makes the two declarations one truth; a version bump in
  one place alone fails the suite.
* Good, because the repository suite keeps its no-third-party-import rule, so it runs under
  any Python 3.11+ interpreter.
* Bad, because there are two delivery paths to keep aligned, and only the drift test prevents
  them from diverging.
* Bad, because a PEP 723 block lives in a comment, so a typo in it is invisible to a syntax
  checker and surfaces only when `uv` refuses to resolve it.
* Neutral, because `uv` becomes a required developer tool for the scripts even though the
  hook does not require it; the alternative — no runner at all — was rejected below.

### Confirmation

The gate that confirms this decision is runnable today:

* `python3 -m unittest scripts.tests.test_metadata_deps -v` proves that both entry scripts
  declare the same pins, that the hook declares the same pins, that the hook uses
  `language: python` with `pass_filenames: false`, and that the `files` pattern matches
  `homeworks/`, `schema/`, the checker and the scaffold while excluding `templates/`.
* `pre-commit run check-metadata --all-files` invokes the hook id `check-metadata` for real,
  so a hook whose text is asserted but never executed cannot pass.
* `python3 -m unittest discover -s scripts/tests -v` proves the rest of the suite still runs
  without importing `yaml` or `jsonschema`.

Phase 8 wires CI to run the same hook and the same suite. Phase 8 wires CI; this record does
not claim that CI runs either of them today.

## Pros and Cons of the Options

### PEP 723 inline metadata run by `uv`, plus an isolated pre-commit environment

Each script owns its dependency block; the hook owns an isolated environment that pre-commit
builds from `additional_dependencies`.

* Good, because the dependency list travels with the script, so a reader sees what it needs
  without following a reference to a shared file.
* Good, because neither path touches the developer's interpreter or a global site-packages.
* Good, because the two declarations are parseable as text, so a stdlib-only test can compare
  them and keep them equal.
* Neutral, because two mechanisms — `uv` and pre-commit's environment builder — must both be
  present in a developer's toolchain.
* Bad, because the pins are written twice by design, and the drift test is the only thing
  preventing divergence.

### A `requirements-dev.txt` installed by hand, with the hook declared `language: system`

Dependencies live in one requirements file; both the scripts and the hook run under the
developer's active interpreter.

* Good, because there is one version list to edit, with no drift test needed.
* Good, because the mechanism is familiar and needs no new tool.
* Bad, because `language: system` runs the hook under whichever interpreter is active, so a
  machine with a different install can pass a check that CI fails, or the reverse.
* Bad, because `additional_dependencies` becomes meaningless: the hook is only as reproducible
  as the developer's environment.
* Bad, because a script invoked directly would fail on a machine that had not run the manual
  install, and the failure would be a `ModuleNotFoundError` rather than a usable message.

### A repository-level virtual environment that both the scripts and the hook activate

A single checked-in or locally created environment supplies the packages to every consumer.

* Good, because one environment and one version list serve the whole repository.
* Good, because activation is explicit, so a developer can see which interpreter runs.
* Bad, because an environment directory is machine-specific and cannot be committed, so CI
  and every new contributor must recreate it before anything works.
* Bad, because pre-commit hooks run in their own process and would still need a declaration,
  so the drift problem reappears in a less visible form.
* Bad, because it contradicts the repository rule that the test suite stays dependency-free:
  the natural next step is to import the packages in tests.

## More Information

The two delivery paths are deliberately independent:

* **Scripts:** PEP 723 inline metadata with `requires-python = ">=3.11"` and the two exact
  pins, executed as `uv run scripts/<script>`. `uv` resolves and caches an ephemeral
  environment; nothing is installed into the repository.
* **Pre-commit:** the `check-metadata` hook uses `language: python` with
  `additional_dependencies: ["PyYAML==6.0.3", "jsonschema==4.26.0"]`. Pre-commit creates and
  owns the environment, so the hook does not depend on `uv` being installed.

The binding test is `scripts/tests/test_metadata_deps.py`. It is stdlib-only: it parses the
PEP 723 block and the hook's fields as text, compares the pin sets in both directions, and
checks the hook's `files` pattern from both sides. It also invokes the hook, because a
declaration that is only read and never executed can be silently misconfigured (D-37).

`templates/` is excluded from the hook's `files` pattern on purpose: an unrendered
`homework.yaml` still contains `{{homework_id}}` placeholders and is not valid metadata.
The pins are recorded in this repository's own ADR index rather than in a root project
manifest, and adding a new script means adding a PEP 723 block — not editing a shared file
that unrelated tools also consume.

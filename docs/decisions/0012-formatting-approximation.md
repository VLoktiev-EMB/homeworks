---
status: accepted
date: 2026-10-26
decision-makers: [VLoktiev-EMB]
consulted: []
informed: []
---

# Formatting is a documented approximation of ESP-IDF style

## Context and Problem Statement

The repository needs one mechanical C/C++ formatter, delivered at an exact revision to every
developer and to CI, and a check that fails a commit which does not match it. ESP-IDF formats
its own sources with AStyle. clang-format is the formatter the pinned `pre-commit` surface
can deliver, and no clang-format configuration reproduces AStyle byte for byte: the two tools
group declarations, wrap braces, and align pointers differently. A rule that called
clang-format "ESP-IDF style" would therefore promise an equivalence that cannot be verified.
How should the repository format C/C++ without making that false claim?

## Decision Drivers

* One formatter must be the single style source, so two tools cannot disagree about the same
  file.
* The formatter must arrive at an exact, pinned revision through `pre-commit`, because the
  local machine carries no system clang-format and a system package would make the gate
  machine-dependent.
* The gate must be check-only: it reports and never rewrites the file it is meant to reject.
* The chosen style must be stated in a form a reader can compare with upstream ESP-IDF, so the
  difference is visible rather than hidden behind a claim of equivalence.
* A second style source such as `.editorconfig` would duplicate the same policy in a place no
  formatter reads consistently; it is declined.
* The tree must already conform, so the first run of the gate is green rather than a backlog.

## Considered Options

* clang-format pinned at an exact revision, documented as an approximation of ESP-IDF style.
* AStyle pinned at an exact revision, matching upstream byte for byte.
* clang-format plus `.editorconfig` as a second, editor-facing style source.
* No formatter, with style enforced by review alone.

## Decision Outcome

Chosen option: "clang-format pinned at an exact revision, documented as an approximation of
ESP-IDF style", because it is the only formatter the pinned `pre-commit` surface can deliver,
and writing the difference down is more honest than claiming equivalence.

The committed `.clang-format` is based on LLVM and carries these keys:

```yaml
BasedOnStyle: LLVM
IndentWidth: 4
TabWidth: 4
UseTab: Never
ColumnLimit: 120
BreakBeforeBraces: Custom
BraceWrapping:
  AfterFunction: true
  AfterControlStatement: Never
PointerAlignment: Right
DerivePointerAlignment: false
AccessModifierOffset: -4
AllowShortFunctionsOnASingleLine: Empty
AllowShortIfStatementsOnASingleLine: Never
AllowShortLoopsOnASingleLine: false
IndentCaseLabels: false
SpaceBeforeParens: ControlStatements
AlignConsecutiveAssignments: false
AlignConsecutiveDeclarations: false
SortIncludes: true
ReflowComments: false
```

This configuration is an approximation of ESP-IDF style, never equivalence. It is the
repository's single standard: no `.editorconfig` exists, and no AStyle check exists. Upstream
ESP-IDF's AStyle configuration remains the reference a reader can compare against, and a
future change that needs exactness would add AStyle as a second tool in its own decision.

### Consequences

* Good, because one pinned binary decides every C/C++ file, on every machine and in CI.
* Good, because the gate is check-only, so a failing commit is reported rather than silently
  rewritten.
* Good, because the approximation is recorded, so a reader knows the output is the
  repository's style and not a claim about upstream.
* Bad, because a contributor who copies an ESP-IDF snippet will see a reformatted diff; the
  two styles are close but not identical.
* Neutral, because the whole tracked tree was reformatted in one mechanical pass, so the gate
  starts green; the cost is one large whitespace-only commit rather than a long backlog.

### Confirmation

* `python3 -m unittest scripts.tests.test_tooling_config.ClangFormatConfigTests -v` asserts
  `IndentWidth: 4`, `ColumnLimit: 120`, `UseTab: Never`, `AfterFunction: true`, and
  `ReflowComments: false` exactly once each, and asserts that `.editorconfig` does not exist.
* `pre-commit run clang-format --all-files` runs the pinned clang-format 23.1.3 in check-only
  form (`--dry-run --Werror`) over the tracked C/C++ tree.
* The hook overrides the mirror's default `clang-format -i` entry, so a passing run cannot
  have rewritten a file.

## Pros and Cons of the Options

### clang-format pinned at an exact revision, documented as an approximation

One tool, one configuration, one pinned revision; the difference from AStyle is stated.

* Good, because the tool arrives through the pinned `pre-commit` environment with no system
  install.
* Good, because the configuration is a small committed file that review can inspect.
* Good, because the approximation can be tested for its declared invariants.
* Bad, because the output is not byte-identical to ESP-IDF's own sources.
* Neutral, because the repository owns the difference as policy rather than as an accident.

### AStyle pinned at an exact revision, matching upstream byte for byte

The upstream formatter itself, configured to match ESP-IDF's own style.

* Good, because the output would be byte-identical to upstream ESP-IDF formatting.
* Bad, because no pinned `pre-commit` mirror delivers AStyle on this repository's surface, so
  the gate would depend on a system install.
* Bad, because AStyle's options are a second, larger configuration surface for no additional
  correctness.
* Bad, because clang-format is already needed for editor integration, so AStyle would be a
  second formatter deciding the same files.

### clang-format plus `.editorconfig` as a second style source

The formatter config plus an editor-facing file carrying the same values.

* Good, because a non-clang editor could read indentation and line length.
* Bad, because two files would declare one policy, and nothing in the gate reads the second.
* Bad, because the two declarations can drift without a failure.
* Neutral, because the repository's editors are configured through the committed VS Code
  contract, which already names clang-format as the formatter.

### No formatter, with style enforced by review alone

Style stays a review convention with no mechanical gate.

* Good, because no tool and no configuration are added.
* Bad, because the difference between two contributors' formatting becomes a review topic
  rather than a machine decision.
* Bad, because there is no command a contributor can run to prove a file is acceptable.
* Bad, because whitespace-only diffs would recur in every change.

## More Information

The decision record for the editor contract is
`docs/decisions/0013-clangd-multi-root-contract.md`: clangd applies this `.clang-format` on
save, so the formatter and the language server are one setup, not two.

`docs/standards/vscode.md` states the same approximation to the beginner who turns on
format-on-save. The binding test is
`python3 -m unittest scripts.tests.test_tooling_config.ClangFormatConfigTests -v`.

Phase 6 deliberately does not add an AStyle check: a second formatter would duplicate the
standard the repository already declares is singular. If exactness with upstream ever becomes
a requirement, it is a new decision with its own alternatives and costs, not a quiet edit to
this one.

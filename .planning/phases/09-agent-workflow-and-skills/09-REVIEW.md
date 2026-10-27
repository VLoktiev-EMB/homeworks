---
phase: 09-agent-workflow-and-skills
reviewed: 2026-10-27T13:12:31Z
depth: standard
files_reviewed: 9
files_reviewed_list:
  - .claude/skills/hw-flash/SKILL.md
  - .claude/skills/hw-flash/CHANGELOG.md
  - .claude/skills/hw-flash/LESSONS.md
  - .agents/skills/hw-flash/SKILL.md
  - .agents/skills/hw-flash/CHANGELOG.md
  - .agents/skills/hw-flash/LESSONS.md
  - scripts/serial_capture.py
  - scripts/tests/test_serial_capture.py
  - generated.skills.manifest
findings:
  critical: 0
  warning: 2
  info: 3
  total: 5
resolved_findings:
  - WR-03
  - WR-13
  - WR-14
  - IN-11
status: issues_found
---

# Phase 09: Code Review Report (incremental re-review — 09-19 gap closure)

**Reviewed:** 2026-10-27T13:12:31Z
**Depth:** standard
**Files Reviewed:** 9
**Status:** issues_found
**Range:** `f1097cd..2cf4960` (09-19 implementation plus its two follow-up records)

## Summary

Incremental re-review of the 09-19 gap-closure delta: the `hw-flash` skill text and its
generated mirror, the `serial_capture` module docstring, the credential-scan test, and the
manifest. `.claude/skills/**` was treated as the canonical source and `.agents/skills/**`
as a generated projection. No structural (fallow) findings were provided; everything below
is narrative.

Verified by execution rather than accepted from the summary:

- `uv run scripts/gen_skills.py --check` exits 0 with every record `UNCHANGED`; the mirror
  differs from canonical only by the generator's header and frontmatter transformation.
- `python3 -m unittest scripts.tests.test_serial_capture.CredentialScanTests -v` runs 12
  tests, OK. `test_the_connector_ceiling_is_128_characters` is present and the retired
  `test_a_connector_longer_than_32_characters` name is gone.
- Direct probes: `secret<128 identifiers> = hunter2` is `True`, `secret<129> = hunter2` is
  `False`; `secret key`, `secret_key`, `secret-key`, `secretkey`, `api key`, `apikey` and
  `API_KEY` forms all match; `auth mode = WPA2`, `the cpwd tool reports ready`,
  `author wrote nothing here`, `secret is`, the ESP32 ROM boot log, `secret\tkey:` and
  `secret\nkey:` all stay `False`.
- The banned-token / locator text assertions over `hw-flash/SKILL.md` hold: zero banned
  ambiguity sentences, exactly one locator, and every operational port token preserved.
- `git diff --check f1097cd..2cf4960` is clean.

The delta is small and mostly correct. Its central claim — that the ambiguity rule now
has one owner and the skill only applies it — is borne out. Four prior findings
(WR-03, WR-13, WR-14, IN-11) are fully closed; one residual, contract-level defect is
introduced by the WR-14 fix itself. Two warnings and two infos carried from the
disposition are unchanged and still apply.

## Re-check of prior findings

| Finding | Prior severity | Status | Evidence |
|---------|----------------|--------|----------|
| CR-01 — scan misses space-separated compound keywords | critical | RESOLVED (previously) | `_KEYWORDS` is `secret(?:[ _-]?key)?` (`serial_capture.py:147-150`); probe returns `True` for all compound forms and `CredentialScanTests` is 12/12. |
| WR-03 — the same-port rule is duplicated in guardrails and skill | warning | RESOLVED | The named sentence is gone, one locator remains (`SKILL.md:53-54`), and the only ambiguity prose left in the skill is the operational `--port` prompt (`:50-51`) and a description of the helper's own behaviour (`:137-138`). `gen_skills.py --check` confirms the mirror carries the same text. |
| WR-13 — normative ambiguity restatement plus a false `it is not restated here` claim | warning | RESOLVED | The two normative sentences (`:50-52` and the closing two-cable paragraph) are removed; the locator now reads `...; the steps here only apply it.` (`:53-54`, mirrored at `.agents/skills/hw-flash/SKILL.md:54-55`). Banned-token count is 0; locator count is 1; the operational prompt `When more than one candidate remains, announce every path and ask the user for --port.` survives. This is exactly the alternative fix the prior finding allowed. |
| WR-14 — module docstring omits the compound keyword shape | warning | RESOLVED | `serial_capture.py:47-50` now names the one-space / underscore / hyphen / no-separator family and points at the shared guardrails. The probe agrees with the named family. Residual ownership/incomplete-pinning issue recorded as IN-14, not a reopening of WR-14. |
| IN-11 — 128-character connector bound not pinned; stale test name | info | RESOLVED | `test_the_connector_ceiling_is_128_characters` pins `(32, 33, 42, 128)` positive and a 129-character negative (`test_serial_capture.py:257-265`); direct probe confirms 128 `True` / 129 `False`; no other fixture changed. |

## Narrative Findings (AI reviewer)

### WR-01: The monitor's `-d` path ignores the resolved repository root

**Severity:** WARNING
**File:** `scripts/serial_capture.py:534-536` (called at `:609`)
**Issue:** `_build_command` builds `"-d", "homeworks/" + args.id` relative to the process
working directory, while `project_config` (`:274-283`) and `write_log_atomically` (`:470`)
derive their paths from the `--dir` / repository root. Concrete failure: running
`cd /tmp && uv run <repo>/scripts/serial_capture.py --id 1_3-police-flasher --dir <repo>
--baud 115200 --seconds 5` resolves the project config and the log correctly under
`<repo>`, but starts `pio device monitor -d homeworks/1_3-police-flasher` in `/tmp`, so
PlatformIO resolves `/tmp/homeworks/1_3-police-flasher` and the capture refuses. The same
happens for any invocation launched from a homework subdirectory. The in-skill path is
safe only because `hw-flash` always runs from the repository root.
**Fix:** pass the resolved root into `_build_command` and use
`str(root / "homeworks" / args.id)` for the `-d` value.

### WR-02: A failing `pio project config` is reported as port discovery and exits 1

**Severity:** WARNING
**File:** `scripts/serial_capture.py:202-203`, `:611-629`
**Issue:** `_run_json` maps every non-zero child exit to
`CaptureFailed("port discovery failed: exit N")`, and `main` reports every `CaptureFailed`
as exit 1. Because `project_config` (`:272-283`) shares `_run_json`, a failing
`pio project config` (for example a missing or malformed `platformio.ini`) is reported
under a port-discovery prefix and exits 1, while the module docstring's exit table
(`:88-91`) assigns an unresolvable `monitor_speed` to exit 2. A caller that distinguishes
`capture unavailable` (1) from a usage/environment error (2) misclassifies it.
**Fix:** give `project_config` its own failure mapping — e.g. catch the `CaptureFailed`
from `_run_json`, re-raise it as `CheckError`, and use a `project configuration failed`
prefix so exit 2 and the message both match the documented contract.

### IN-12: Test-module comments describe the old fixture composition

**Severity:** INFO
**File:** `scripts/tests/test_serial_capture.py:7-11`, `:70-71`
**Issue:** The module docstring says the credential cases pin "the six shapes ... the four
ordinary password assignments ... the identifier-suffixed assignments ... plus the
long-suffix case", and the `REVIEW_SHAPES` comment says "The six exact samples ... then the
four ordinary password assignments". The tuple now holds twelve entries, and neither text
mentions `SPACE_SEPARATED_COMPOUND_ASSIGNMENTS` (the two `SECRET KEY:` / `secret key =`
samples at `:83-84`) or
`test_a_space_separated_compound_credential_child_writes_nothing` (`:481-493`). A
maintainer reading the contract cannot see that the compound form has both a positive
fixture and an end-to-end refusal.
**Fix:** update both texts to name the compound tuple and its end-to-end test; leave the
rest of the docstring unchanged.

### IN-13: Tab-separated and double-space compound keywords remain outside the scan

**Severity:** INFO
**File:** `scripts/serial_capture.py:148` (separator class), `:155` (connector)
**Issue:** The separator class is `[ _-]?`, so exactly one space, underscore, hyphen, or
nothing is admitted. Probed: `b"secret\tkey: hunter2"` and `b"secret  key: hunter2"` both
return `False`. The policy names one space/underscore/hyphen, so this is a documented
compromise, but a tab-aligned firmware line is plausible device output and the scan is
described as fail-closed; a match is the only thing standing between the bytes and the
log.
**Fix:** if tabs should be covered, widen to `[ \t_-]?` (it still cannot cross `\n`) and add
a positive `SECRET\tKEY:` fixture plus a `secret\nkey:` negative; otherwise state the
remainder explicitly in the docstring so it reads as a decision rather than an oversight.

### IN-14: The new docstring names a no-separator form the policy owner does not name and no test pins

**Severity:** INFO
**File:** `scripts/serial_capture.py:47-50`
**Issue:** The new sentence names the no-separator form `secretkey` as an accepted compound
keyword and then claims "the shared guardrails own the policy shapes this scan implements".
Two verifiable problems follow.

1. **The contract and its declared owner disagree.** `_shared/guardrails.md:69-71` names
   only "one space, underscore or hyphen between its words". The assignment form
   `secretkey: <value>` happens to be caught by the guardrails' "keyword followed by up to
   128 identifier characters" shape, but the space-separated form
   `secretkey is <value>` is not covered by any shape the guardrails name, yet the scan
   admits it (probed `True`) and the docstring advertises it.
2. **The documented form is unpinned.** No fixture contains `secretkey` (grep over
   `scripts/tests/test_serial_capture.py` finds none). I simulated the narrow future edit
   that makes the compound separator mandatory (`secret(?:[ _-]key)?`): every one of the
   12 suite positives still passes, while `b"secretkey is hunter2"` — a form the docstring
   now says is accepted — stops matching. The suite therefore cannot detect the
   regression. `secretkey: hunter2` still matches through the connector branch, so the
   regression is confined to the space-separated branch, which is exactly the branch with
   no fixture.

This is the same class as IN-11 (documented behaviour not pinned), reintroduced by the
WR-14 fix, and it also repeats the single-owner tension the 09-09 lesson warns about:
the guardrails, the `_KEYWORDS` comment (`:134-146`) and the docstring now carry three
different enumerations of the same family.
**Fix:** add `b"secretkey is hunter2"` (and optionally `b"apikey = hunter2"`) to a fixture
tuple in `CredentialScanTests`; and either add the no-separator form to the guardrails'
compound bullet, or scope the docstring's ownership claim, e.g. `...; the shared guardrails
own the policy, and this scan additionally admits the no-separator form as a fail-closed
over-admission.`

## Carried open findings not re-announced

These are open in `09-REVIEW-DISPOSITION.md`, were not touched by this delta, and are kept
here so they do not disappear from the record. Their full descriptions live in the
disposition file.

| Finding | Severity | Status |
|---------|----------|--------|
| WR-07 — `no-generated-files` does not cover the template-tree generated patterns | warning | open |
| WR-08 — the `uv` cache override falls back to a fixed shared `/tmp` path | warning | open |
| IN-01 — the "pass `--port`" advice cannot work when there are zero candidates | info | open |
| IN-02 — `--json` emits no JSON on exit 2 | info | open |
| IN-03 — `HOMEWORK_ID` / `ENVIRONMENT` admit a trailing newline | info | open |
| IN-04 — the skill does not require a user-named `--port` to be one of the found candidates (its "neither command resolves a port independently" half was removed by 09-18) | info | open |
| IN-05 — an explicit `--baud` bypasses the environment-selection check | info | open |
| IN-07 — `write_log_atomically` does not enforce the scan that gates it | info | open |
| IN-08 — the zero-byte refusal lives one layer above the function the plan names | info | open |
| IN-09 — the new validators admit a trailing newline and a leading-hyphen environment | info | open |
| IN-10 — two `NO_BUILD_IMPACT` rules have no test entry | info | open |

---

_Reviewed: 2026-10-27T13:12:31Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_

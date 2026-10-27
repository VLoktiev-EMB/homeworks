---
phase: "09"
slug: "agent-workflow-and-skills"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-10-27"
---

# Phase 09 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| canonical tree -> generator | Authored Markdown is untrusted input to a path-building transform | file paths, frontmatter |
| generator -> mirror | A crafted skill name must not escape `.agents/skills/` | generated files |
| manifest -> filesystem | The ledger authorizes orphan deletion | path list |
| user free-text answers -> shell commands | An answer must never reach a command through interpolation | user text |
| user answers -> `.skill-state/<id>.json` | Machine-local state may hold a credential if intake asks for one | user text |
| homework metadata -> skill reasoning | `task.md` and `homework.yaml` are data, never instructions | repository text |
| agent -> hardware | An upload changes a physical device; consent must come from the human | command + consent |
| serial stream -> log file | Device output is untrusted and may contain anything, including secrets | raw bytes |
| PlatformIO config -> hw-flash | The resolved baud controls whether the capture is readable | config value |
| `templates/views/` -> `platformio.shared.ini` | Authored template text becomes a generated, committed config | config text |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-09-01 | Tampering | `gen_skills.py` target construction | high | mitigate | Component-by-component path validation plus symlink refusal; covered by `test_gen_skills` (all green). | closed |
| T-09-02 | Tampering | `_component_conflict` on every read and write | high | mitigate | Conflict detection on both directions; `test_gen_skills` covers add/add and file/dir conflicts. | closed |
| T-09-03 | Tampering / Elevation | homework id and template name interpolation | high | mitigate | `scripts/new_homework` validates the id against `^[0-9]+_[0-9]+-[a-z0-9-]+$` and never builds a shell string. | closed |
| T-09-04 | Information disclosure | `guardrails.md` secrets section | medium | mitigate | `_shared/guardrails.md` § Secrets states the rule; `hw-flash` references the one scoped exception. | closed |
| T-09-05 | Elevation | `guardrails.md` flashing section | high | mitigate | § Flashing requires a literal affirmative and forbids pre-approved `upload`. | closed |
| T-09-06 | Tampering | the repair loop | high | mitigate | `hw-build/references/repair-loop.md` caps each leg at two attempts and forbids reset/checkout. | closed |
| T-09-07 | Spoofing | `task.md`, `homework.yaml`, `report.md` content | medium | mitigate | Metadata checker enforces the schema; assignments are paraphrased with attribution. | closed |
| T-09-08 | Tampering | `_classify_orphan` deletion | high | mitigate | Orphan deletion is limited to manifest-tracked paths inside the mirror; `test_gen_skills` green. | closed |
| T-09-09 | Repudiation | generated and untracked state | medium | mitigate | `generated.skills.manifest` records every projection; `--check` reports drift. | closed |
| T-09-10 | Tampering / Transparency | mirror frontmatter projection | high | mitigate | Projection strips Claude-only keys deterministically; `test_gen_skills` covers the transform. | closed |
| T-09-11 | Spoofing / Transparency | the four stub skills | high | mitigate | `metadata.status: stub` present in `course-index`, `hw-report`, `schematic`, `simulate`. | closed |
| T-09-12 | Tampering | state-file write path | medium | mitigate | `references/state-file.md` applies `lstat`/symlink refusal and parent-after-check discipline. | closed |
| T-09-13 | Spoofing / Transparency | "Поясни глибше" and assumption acceptance | medium | mitigate | Depth is never inferred from silence; an assumption is recorded only after acceptance. | closed |
| T-09-14 | Repudiation | reported build result | medium | mitigate | `hw-build` reports the real exit code, never a wrapper's. | closed |
| T-09-15 | Tampering | a contributor hand-editing `.agents/skills/` | medium | mitigate | `gen-skills-check` fails on any divergence; `AGENTS.md` names the repair command. | closed |
| T-09-16 | Information disclosure | `09-DRY-RUN.md` | high | mitigate | Transcript sanitized: no credential values, no private absolute paths; token recorded as a boolean. | closed |
| T-09-17 | Repudiation | `AGENTS.md` generated-file rule | medium | mitigate | `AGENTS.md` separates build output from committed projections and names each generator. | closed |
| T-09-18 | Repudiation | `guardrails.md` commit/PR section | medium | mitigate | § Commit and pull request requires confirmation and forbids `--no-verify`. | closed |
| T-09-19 | Information disclosure | `.skill-state/<id>.json` and any log | high | mitigate | State-file discipline plus the scoped log exception; secrets are never written. | closed |
| T-09-20 | Tampering / Elevation | homework id in `pio run -d` and `pio test -d` | high | mitigate | `hw-build` validates the id and passes it as one argument, never interpolated. | closed |
| T-09-21 | Elevation | the consent gate before `-t upload` | high | mitigate | `hw-flash` prints board, environment, and command, then stops for a literal affirm. | closed |
| T-09-22 | Information disclosure | `.skill-state/logs/<id>.log` and the transcript | high | mitigate | Scoped fail-closed exception: credential-shape scan precedes any write; a match writes nothing. | closed |
| T-09-23 | Tampering / Elevation | homework id in the upload and monitor commands | medium | mitigate | Same validation and single-argument invocation as T-09-20. | closed |
| T-09-24 | Repudiation | reported upload result | medium | mitigate | Four outcome states reported separately; a capture failure never reads as a flash failure. | closed |
| T-09-25 | Tampering | `GSD:skills` block in `.claude/CLAUDE.md` | high | mitigate | Block regenerated by `generate-claude-md`; exactly one start/end pair; surrounding bytes unchanged. | closed |
| T-09-26 | Repudiation | the adapter's skills list | medium | mitigate | The generated block names all seven skills with real paths. | closed |
| T-09-27 | Elevation | the dry-run flash leg | high | mitigate | The dry run receives a non-affirmative answer and runs no upload. | closed |
| T-09-28 | Tampering | the negative repair leg | high | mitigate | The broken fixture lives in a disposable root; `git status --porcelain homeworks/` stays empty. | closed |
| T-09-29 | Repudiation / Tampering | capture outcome and log write | high | mitigate | Four outcome states named; capture failure reports `capture unavailable` while upload keeps its result. | closed |
| T-09-30 | Information disclosure | `.skill-state/logs/<id>.log` write path | high | mitigate | Scan of the exact bytes before any file is created; on a match write nothing, report `capture unavailable`. | closed |
| T-09-31 | Tampering / Spoofing | resolved baud and monitor exit code | medium | mitigate | Baud resolved from `pio project config --json-output`, stop when absent; `returncode` checked. | closed |
| T-09-32 | Tampering | `templates/views/shared-ini.ini.tmpl` -> `platformio.shared.ini` | medium | mitigate | Template is the only edit surface; `gen-views-check` fails on drift; `SharedIniTests` pins the baud. | closed |
| T-09-38 | Tampering / Repudiation | `hw-flash` consent gate and capture command | high | mitigate | Both announced commands carry `[--baud <n>]`; the prose names `--baud` as the helper option and `-b` only as the forwarded monitor flag; `BuildCommandTests` pin the `-b` argv; the mirror is regenerated so no client sees the stale flag. | closed |
| T-09-39 | Information disclosure | CLI result payload | low | mitigate | The payload prints only the repository-relative path, status, reason and byte count; never captured bytes, the matched span or stderr; `CliResultPayloadTests` assert the exact payload keys. | closed |
| T-09-40 | Information disclosure | `find_credential` and the sole capture exception | high | mitigate | `_KEYWORDS` widened to `pass(?:word|wd|phrase)` and `pwd`, leading lookbehind dropped, copula admitted; four shapes plus a benign-negative set pinned; the exact bytes are scanned before any file exists; a match writes nothing and reports `capture unavailable`. **Closed 2026-10-27 (09-14):** the assignment branch admits a `[\w.-]{0,128}` connector, so the four identifier-suffixed shapes (`{"secretKey": "hunter2"}`, `secret_key = hunter2`, `passwordHash: abcdef`, `SECRET_KEY = hunter2`) match; `CredentialScanTests.test_identifier_suffixed_assignments_match` pins them and `CaptureAndStoreTests.test_an_identifier_suffixed_credential_child_writes_nothing` proves `capture_and_store` refuses before any log or `.skill-state` directory exists. **Tightened 2026-10-27 (review CR-01, `87ca910`):** the ceiling was raised from 32 to 128 after the review proved a 33-character identifier was still written to the log; `test_a_connector_longer_than_32_characters_matches` pins the 32/33/42-character boundary, and the guardrails, docstring and comment all state 128. | closed |
| T-09-41 | Denial of service | widened scan false positives | low | accept | A widened scan can refuse a benign capture. Accepted: a refusal writes no log, leaves no `.state` directory, and reports a truthful `capture unavailable`; benign boot-log and ordinary-word tests bound the regression. | closed |
| T-09-42 | Denial of service | `--seconds` parsing and the read loop | medium | mitigate | A non-finite, non-positive or above-`MAX_SECONDS` value is rejected with `CheckError` before `resolve_root`, `_build_command` or `Popen`; `CliDurationTests` assert exit 2 and no traceback. | closed |
| T-09-43 | Resource exhaustion | `capture_pty` child lifecycle | medium | mitigate | Reap in the outer `finally`: kill a live child, then wait, on every exception path; `CaptureReapTests` assert the recorded child's `returncode` is set when a `RuntimeError` escapes. | closed |
| T-09-SC | Tampering | package installs | low | accept | No package is installed; pinned tools only. | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| R-09-01 | T-09-SC | The phase installs no package; it runs the already-pinned PlatformIO Core, pre-commit, and the stdlib Python suite. | project maintainer | 2026-10-27 |
| R-09-02 | T-09-41 | Widening the credential scan trades a bounded false-positive rate for fewer misses. A refusal writes no log and leaves no state directory, so the failure mode is a truthful `capture unavailable`, not a leak. Severity is low, below the `high` block threshold. | project maintainer | 2026-10-27 |

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-10-27 | 33 | 33 | 0 | gsd-secure-phase (L1, ASVS 1) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-10-27

## Security Audit 2026-10-27

| Metric | Count |
|---|---|
| Threats found | 39 |
| Closed | 39 |
| Open | 0 |

## Security Audit 2026-10-27

| Metric | Count |
|---|---|
| Threats found | 39 |
| Closed | 38 |
| Open | 1 |

## Security Audit 2026-10-27

| Metric | Count |
|---|---|
| Threats found | 39 |
| Closed | 39 |
| Open | 0 |

---
phase: 09-agent-workflow-and-skills
reviewed: 2026-10-26T23:38:16Z
depth: standard
files_reviewed: 14
files_reviewed_list:
  - scripts/serial_capture.py
  - scripts/tests/test_serial_capture.py
  - scripts/affected.py
  - scripts/tests/test_affected.py
  - .claude/skills/hw-flash/SKILL.md
  - .claude/skills/hw-flash/CHANGELOG.md
  - .claude/skills/hw-flash/LESSONS.md
  - .claude/skills/_shared/guardrails.md
  - AGENTS.md
  - .agents/skills/hw-flash/SKILL.md
  - .agents/skills/hw-flash/CHANGELOG.md
  - .agents/skills/hw-flash/LESSONS.md
  - .agents/skills/_shared/guardrails.md
  - generated.skills.manifest
findings:
  critical: 1
  warning: 3
  info: 5
  total: 9
status: issues_found
---

# Phase 09: Code Review Report

**Reviewed:** 2026-10-26T23:38:16Z
**Depth:** standard
**Files Reviewed:** 14
**Status:** issues_found

## Summary

Incremental review of the 09-10 gap-closure change set at base `07317f1`: the new
`scripts/serial_capture.py` PTY helper and its suite, the `hw-flash` rewrite that points at
it, the restored guardrails prohibition, the two `affected.py` entries, `AGENTS.md`, and the
regenerated mirror and manifest. Earlier findings CR-01, CR-02, WR-01..WR-09 and IN-01..IN-05
are already recorded; this report continues at CR-03 / WR-10 / IN-06 and reuses no ID.

What holds, checked rather than assumed:

- `uv run scripts/gen_skills.py --check` reports every `.agents/**` file and
  `generated.skills.manifest` as `UNCHANGED`. A direct byte comparison confirms the mirror is
  exactly the documented transform (generated banner plus the invocation line replacing
  `disable-model-invocation`) of the canonical tree, and every manifest `sha256` and `bytes`
  value matches its file.
- `python3 -m unittest scripts.tests.test_affected` is `OK` (26 tests) on this host.
  `scripts/serial_capture.py` maps to no build impact on the real repository; a change to
  `scripts/tests/test_serial_capture.py` (or to `scripts/affected.py` itself) widens, which is
  the documented fail-safe.
- The PTY fix is genuinely correct against the installed PlatformIO 6.2.0:
  `platformio/compat.py:37-39` gates on `sys.stdout.isatty()` and
  `platformio/device/monitor/terminal.py:60-61` skips `print_terminal_settings` when
  `--quiet` is set, so the prior CR-01 and WR-06 are closed.
- `python3 -m unittest scripts.tests.test_serial_capture` passes its 17 non-PTY tests. The 7
  PTY-dependent tests fail in this reviewer's sandbox with `OSError: out of pty devices`, the
  limitation `09-10-PLAN.md:64` records; this is an environment result, not a repository
  defect, and it is not counted as a finding.
- The credential and atomic-write suites pass, including all six CR-02 fixtures, the
  symlink refusals, replace-not-append, and the concurrency case.

What does not hold:

- `hw-flash` never wires the user-resolved baud into the helper it now invokes, so the
  absent-`monitor_speed` branch either drops the baud (monitor falls back to the forbidden
  9600) or passes a flag the helper does not accept (CR-03).
- The helper's CLI admits non-finite `--seconds`, and its read loop has no failure path that
  reaps the child (WR-10, WR-11).
- The credential scan still misses plausible assignment forms the policy's general clause
  names (WR-12).

Security register delta for this slice: T-09-34 (PTY/early exit) and T-09-36 (write path) are
closed; T-09-33 (credential scan) remains partially open at WR-12; T-09-35 (CLI validation)
at WR-10 and IN-09; T-09-37 (bounded read loop) at WR-11; the baud control behind T-09-31 is
reopened by CR-03. If a new ID is minted for the baud wiring it continues at T-09-38.

## Critical Issues

### CR-03: `hw-flash` never passes the user-resolved baud to the capture helper

**File:** `.claude/skills/hw-flash/SKILL.md:67`, `:108`, `:118`, `:143-145` (mirror
`.agents/skills/hw-flash/SKILL.md:68`, `:109`, `:119`, `:144-146`); helper at
`scripts/serial_capture.py:288` and `:274-277`

**Issue:** The skill's only executable capture command is
`uv run scripts/serial_capture.py --id <id> [--env <env>] [--seconds 20]`. The helper's baud
flag is `--baud` (`serial_capture.py:288`), which appends `-b <n>` to the monitor
(`:276-277`). Neither the consent-gate example nor the capture command includes `--baud`,
while the prose still says "Pass `-b <n>` only for the user-named value accepted after an
absent setting" (`SKILL.md:143-145`). `-b` is not a helper flag. An agent that follows the
prose appends `-b <n>` and argparse exits 2 with no capture; an agent that follows the
command drops the baud entirely. In the absent-`monitor_speed` branch the monitor then
inherits PlatformIO's 9600 fallback, which the same file forbids ("Never run the monitor on
PlatformIO's built-in 9600"), while the gate announced `Baud: <n>`. A 115200 device sampled at
9600 commonly yields framing-error bytes rather than zero bytes, so the run can report
"capture succeeded" with a corrupt log. The removed snippet wired `user_baud` into the child
(`if user_baud is not None: argv += ["-b", str(user_baud)]`), so this is a regression
introduced by the rewrite. It also breaks the consent rule that the announced capture is the
executed capture.

**Fix:** Put the helper flag in both announced commands and in the prose:

```text
Capture: uv run scripts/serial_capture.py --id <id> [--env <env>] [--baud <n>] --seconds 20
```

```markdown
- Include `--baud <n>` only for the user-named value accepted after an absent
  `monitor_speed`; the helper appends `-b <n>` to the monitor. Include `--env <env>`
  only when `needs_e_flag` is true.
```

Update "Nothing else in the commands is conditional" to name `--env` and `--baud`, add a
`_build_command` test that asserts the `-b` argv, and regenerate the mirror with
`uv run scripts/gen_skills.py`.

## Warnings

### WR-10: `--seconds` accepts NaN and infinity, which crash the CLI with a traceback

**File:** `scripts/serial_capture.py:310-311` and `:143-153`

**Issue:** `if args.seconds <= 0` is false for `float("nan")` and `float("inf")`. The deadline
is then non-finite and `select.select([master], [], [], remaining)` raises
`ValueError: Invalid value NaN (not a number)` or
`OverflowError: timestamp out of range for platform time_t` (both reproduced on this host).
Neither exception is `CaptureFailed` or `CheckError`, so `main` does not catch it: the process
exits with a traceback and Python's exit 1, not the documented usage exit 2, and the child
started at `:131` is never killed or reaped because only the deadline/EOF branches call
`_terminate`. A huge finite value (for example `1e18`) overflows the same way.

**Fix:**

```python
import math
...
if not math.isfinite(args.seconds) or args.seconds <= 0:
    raise CheckError("--seconds must be a positive finite number")
```

Consider a sane upper bound as well.

### WR-11: An exception in the read loop leaves `pio device monitor` running

**File:** `scripts/serial_capture.py:122-166`

**Issue:** `_terminate` runs only on the deadline (`:146-149`), the not-ready branch
(`:150-153`), and the EOF/EIO refusal (`:154-163`). Any other exception after `Popen` —
`KeyboardInterrupt` during the 20-second wait, the `ValueError`/`OverflowError` from WR-10, or
`MemoryError` — propagates while the `finally` at `:165-166` closes only the master fd. The
child is neither killed nor waited. It may keep the serial port open until it notices the
hung-up slave, so the next flash can fail with a busy port, and the un-reaped `Popen` emits a
ResourceWarning.

**Fix:** Reap in the `finally`:

```python
finally:
    if process.poll() is None:
        process.kill()
    process.wait()
    os.close(master)
```

Keep the early-return `_terminate` calls or replace them with this single path.

### WR-12: The credential scan still misses ordinary password assignments

**File:** `scripts/serial_capture.py:82-88` and `:97-103`; policy at
`.claude/skills/_shared/guardrails.md:56-64` (mirror `:57-65`)

**Issue:** The guardrails say the scan "finds no match for a token, secret, password, or
API-key assignment", but the long-form alternative requires the whitespace run to be followed
immediately by six-plus non-space characters, and the leading `(?<![a-z0-9])` rejects a
keyword preceded by a letter. Verified misses:

```text
password is hunter2      MISS
userpassword = hunter2   MISS   (keyword preceded by `r`)
passphrase = hunter2     MISS   (not in the keyword set)
pwd = hunter2            MISS
```

`password is hunter2` and `userpassword = hunter2` are assignments in the policy's own sense,
and the same class of miss was CR-02. A false match is safe because it writes nothing, so the
fail-closed choice is to catch these.

**Fix:** Drop the leading lookbehind, add `pass(?:word|wd|phrase)`, and allow a copula in the
long-form branch:

```python
_KEYWORDS = rb"(?:authorization|auth|token|secret|pass(?:word|wd|phrase)|api[ _-]?key)"
CREDENTIAL = re.compile(
    _KEYWORDS + rb"(?:[\"']?\s*[:=]\s*[\"']?\S+|\s+(?:is\s+)?\S{6,})",
    re.IGNORECASE,
)
```

This keeps all six existing fixtures and `secret is` unmatched (verified) while adding the
two misses above. Add the new shapes to `REVIEW_SHAPES` and widen the guardrails sentence in
the same change.

## Info

### IN-06: The suite does not exercise the helper's argv or the CLI result contract

**File:** `scripts/tests/test_serial_capture.py:292-319` (CLI), `:230-251` (concurrency),
`:254-289` (store)

**Issue:** `CliUsageTests` covers only the three usage errors. Nothing exercises `main`'s
`--json` `CAPTURED`/`REFUSED` payload, the exit-1 refusal path, or `_build_command`'s
`--env`/`--baud` argv, which is exactly where CR-03 lives. The concurrency test asserts only
the final file and the absence of a `.capture-*` file; it never reads while writers run, so
the must-have's "no reader observes a torn log" (`09-10-PLAN.md:38`) is unproven. The
credential test asserts the log is absent but not that `.skill-state/` was never created, and
nothing asserts the `0o600` mode the skill promises (`SKILL.md:155-157`). Finally, the
success-path tests use 0.4-0.5 second bounds (`:63`, `:267`, `:277`, `:286`); a scheduling
delay on a loaded runner makes the capture return empty and fails the test.

**Fix:** Add a `_build_command` test for `--env`/`--baud`, a CLI `--json` success and refusal
test driven through `sys.executable -c` children, a concurrent reader, a
`stat.S_IMODE(...) == 0o600` assertion, an assertion that `.skill-state` is absent after a
match, and use a 1-2 second bound on the success-path tests.

### IN-07: `write_log_atomically` does not enforce the scan that gates it

**File:** `scripts/serial_capture.py:202-247`; caller at `:250-260`

**Issue:** The guardrails' only permitted write is conditioned on a credential scan, but the
scan lives in `capture_and_store`. `write_log_atomically` accepts any bytes from any caller
(the tests call it directly). The invariant holds today only because the sole shipped caller
scans first; a future caller, or a refactor that reorders the two statements, writes a
credential with no test failing.

**Fix:** Put the guard inside the write (`if find_credential(data): raise CaptureFailed(...)`)
or make the function private and expose only `capture_and_store`.

### IN-08: The zero-byte refusal lives one layer above the function the plan names

**File:** `scripts/serial_capture.py:143-153` and `:254-256`; contract at
`.planning/phases/09-agent-workflow-and-skills/09-10-PLAN.md:35`

**Issue:** The must-have says "`capture_pty` raises `CaptureFailed` ... when ... it reaches
the bound with zero bytes", but `capture_pty` returns `b""` at the deadline, and
`test_capture_stops_at_the_deadline` (`:110-119`) asserts that return. The refusal is in
`capture_and_store`. The shipped CLI is correct, but the stated function-level contract is
wrong, and a direct `capture_pty` caller sees an empty success.

**Fix:** Either raise in `capture_pty` when `chunks` is empty at the deadline (and update the
test), or correct the must-have to name `capture_and_store`.

### IN-09: The new validators admit a trailing newline and a leading-hyphen environment

**File:** `scripts/serial_capture.py:90`, `:204`, `:301-307`

**Issue:** `HOMEWORK_ID` and `ENVIRONMENT` are anchored with `$`, which in Python `re`
matches before a final newline: `HOMEWORK_ID.match("1_3-x\n")` and
`ENVIRONMENT.match("arduino\n")` are both true (verified). The id then names
`.skill-state/logs/1_3-x\n.log` and the environment is passed as `-e "arduino\n"`.
`ENVIRONMENT` also allows a leading `-` (`--env --help`, `--env -e`), which is passed as the
value of `-e`. No traversal or shell injection results (argv is a list and `/` is excluded),
but the validators do not implement the canonical `^...$` shape the rulebook states.

**Fix:** Use `.fullmatch()` (or `\Z`) for both, and require the environment to start with an
alphanumeric or underscore: `^[A-Za-z0-9_][A-Za-z0-9_-]*$`.

### IN-10: Two `NO_BUILD_IMPACT` rules have no test entry

**File:** `scripts/tests/test_affected.py:236-252`

**Issue:** `NO_BUILD_IMPACT` contains `.skill-state/` (`scripts/affected.py:117`) and the
directory spellings `.claude/`/`.agents/`; `NO_BUILD_IMPACT_PATHS` covers `.claude/skills/...`
and `.agents/skills/...` by prefix but never `.skill-state/` at all. A future edit that drops
the `.skill-state/` entry would not fail a test.

**Fix:** Add `".skill-state/logs/1_3-alpha.log"` to the tuple.

---

_Reviewed: 2026-10-26T23:38:16Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_

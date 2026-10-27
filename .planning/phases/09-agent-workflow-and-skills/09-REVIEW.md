---
phase: 09-agent-workflow-and-skills
reviewed: 2026-10-27T00:15:41Z
depth: standard
files_reviewed: 11
files_reviewed_list:
  - .agents/skills/hw-flash/SKILL.md
  - .claude/skills/hw-flash/SKILL.md
  - generated.skills.manifest
  - scripts/tests/test_serial_capture.py
  - .agents/skills/hw-flash/CHANGELOG.md
  - .agents/skills/hw-flash/LESSONS.md
  - .claude/skills/hw-flash/CHANGELOG.md
  - .claude/skills/hw-flash/LESSONS.md
  - scripts/serial_capture.py
  - .agents/skills/_shared/guardrails.md
  - .claude/skills/_shared/guardrails.md
findings:
  critical: 1
  warning: 1
  info: 4
  total: 6
status: issues_found
---

# Phase 09: Code Review Report (gap-closure re-review)

**Reviewed:** 2026-10-27T00:15:41Z
**Depth:** standard
**Files Reviewed:** 11
**Status:** issues_found

## Summary

Re-review of the gap-closure delta `cc5fff3..HEAD` (`e4a1393`) touching the PTY capture
helper, its suite, the `hw-flash` skill, the shared guardrails, and their generated
projections. The prior review's findings are recorded in
`09-REVIEW-DISPOSITION.md`; this report reuses no ID, does not restate a finding whose fix
holds, and continues at CR-01 / WR-01 / IN-01.

All findings below are narrative (AI reviewer) findings; no structural pre-pass was
provided.

What was checked rather than assumed:

- `python3 -m unittest discover scripts/tests` is `OK` (416 tests) outside the sandbox.
  The sandbox denies PTY allocation (`OSError: out of pty devices`, reproduced with a bare
  `pty.openpty()`), so the PTY-dependent tests were re-run outside it; that is an
  environment result, not a repository defect.
- `python3 scripts/gen_skills.py --check` reports every `.agents/**` file and
  `generated.skills.manifest` as `UNCHANGED`, exit 0. The canonical and mirrored
  `hw-flash/SKILL.md` agree modulo the documented frontmatter/banner transform, and every
  manifest `sha256`/`bytes` value matches its file. No drift.
- `ruff check` passes on both Python files. `ruff format --check` would reformat them, but
  `.pre-commit-config.yaml` deliberately enables only `ruff-check` (D-13: "`ruff-format`
  would introduce a second mechanical rewrite that TOOL-03 does not require"), so this is
  not a gate violation.
- The 09-13 duration fix holds end to end: `--seconds nan|inf|-1|0|601|1e400` all exit 2
  with `ERROR: --seconds must be a positive finite number no greater than 600` and no
  traceback, before any process starts.
- The 09-11 baud fix holds: both capture lines and the prose name `--baud` as the helper
  option, `_build_command` appends `-b <n>` only when `--baud N` is supplied, and
  `BuildCommandTests` pins the argv. PlatformIO 6.2.0 accepts `-e`, `-b`, `--raw` and
  `--quiet` (verified with `pio device monitor --help`), and `apply_project_monitor_options`
  inherits `monitor_speed` from the default env, so the declared-baud path is correct.
- The 09-13 reaping `finally` does kill and reap the child on an escaping exception; the
  new `CaptureReapTests` fails on the pre-fix tree and passes now.

What does not hold:

- The widened credential scan still writes common camelCase/underscore credential
  assignments (`secretKey:`, `secret_key =`, `passwordHash:`) to the log, so the sole
  capture exception's precondition is violated (CR-01).
- The reaping `finally` is not itself failure-proof: it waits without a bound and can
  replace the in-flight exception or skip closing the master descriptor (WR-01).
- The announced capture command still differs from the executed one on the default
  duration, the helper's new exit-2 usage error is outside the skill's outcome states, and
  the new duration test does not prove the ordering the must-have claims (IN-01..IN-03).

## Critical Issues

### CR-01: The widened credential scan still persists `secretKey` / `secret_key` / `passwordHash` assignments

**File:** `scripts/serial_capture.py:97-103` (regex), `:268-278` (`capture_and_store`),
`:25-34` (docstring claim); policy `.claude/skills/_shared/guardrails.md:55-68` and mirror
`.agents/skills/_shared/guardrails.md:56-69`

**Issue:** The 09-12 change removed the leading `(?<![a-z0-9])` boundary and added
`passphrase`/`pwd`, but the assignment branch still requires the separator (`[:=]`, modulo
quotes and whitespace) **immediately** after the keyword:

```python
CREDENTIAL = re.compile(
    rb"(?i)"
    + _KEYWORDS
    + rb"(?:[\"']?\s*[:=]\s*[\"']?\S+|\s+(?:is\s+)?\S{6,})"
)
```

A keyword used as the *prefix* of a longer identifier therefore misses: `secretKey`,
`secret_key`, `passwordHash`. This is the same class as CR-02 (a missed ordinary assignment
form lets the gated write persist a credential) and the WR-12 fix is incomplete. Proven end
to end by driving the shipped path with a fake serial child:

```text
find_credential(b'{"secretKey": "hunter2"}')  -> False, log WRITTEN with the bytes
find_credential(b"secret_key = hunter2")      -> False, log WRITTEN with the bytes
find_credential(b"passwordHash: abcdef")      -> False, log WRITTEN with the bytes
```

`capture_and_store` calls `find_credential` and then `write_log_atomically`, so the bytes
land in `.skill-state/logs/<id>.log`. The guardrails rule is **[MUST]**: never write a
credential to any log except under the scoped exception, whose precondition is that the
scan "finds no match for a token, secret, password, passwd, passphrase, pwd, or API-key
assignment". `secretKey`/`secret_key` are exactly a `secret` assignment. The helper's own
docstring also claims "the keyword may sit inside a larger word (`userpassword`)" without
scoping that to the leading side, so the implementation contradicts its documented rule.

**Fix:** allow an identifier connector before the separator in the assignment branch only,
leaving the space-separated/copula branch and its six-character floor unchanged:

```python
CREDENTIAL = re.compile(
    rb"(?i)"
    + _KEYWORDS
    + rb"(?:[\w.-]{0,32}[\"']?\s*[:=]\s*[\"']?\S+|\s+(?:is\s+)?\S{6,})"
)
```

This was checked against the full fixture set: all ten `REVIEW_SHAPES`, `passwd`,
`PASSWORD: hunter2` and the three new forms match, while `secret is`,
`the cpwd tool reports ready`, `author wrote nothing here`, the ESP-ROM banner and
`auth mode = WPA2` stay unmatched. Add the three shapes to `REVIEW_SHAPES`, name the
suffix form ("a keyword followed by identifier characters, such as `secretKey`") in the
guardrails sentence, and regenerate the mirror with `uv run scripts/gen_skills.py`.

## Warnings

### WR-01: The reaping `finally` can hang the "bounded" capture and mask the original failure

**File:** `scripts/serial_capture.py:130-134` (`_terminate`), `:181-184` (the new `finally`)

**Issue:** The WR-11 fix added the reap to `capture_pty`'s outer `finally`:

```python
    finally:
        if process is not None:
            _terminate(process)
        os.close(master)
```

`_terminate` calls `process.kill()` followed by an **unbounded** `process.wait()`
(`:130-134`), and the `finally` body has no protection of its own. Two consequences:

1. The helper's contract is a *bounded* capture. SIGKILL is delivered when the child
   returns from the kernel; a `pio` child wedged in an uninterruptible (`D`-state) USB-serial
   read can delay the reap indefinitely, so the deadline, not-ready and EOF paths can all
   hang in cleanup. The sibling helper `_reap` already bounds its wait at five seconds
   (`:121-127`), so the two helpers disagree.
2. If `_terminate` or `os.close(master)` raises (`OSError`, a second `KeyboardInterrupt`),
   it replaces the in-flight `CaptureFailed`/`KeyboardInterrupt` and the master descriptor
   is never closed; the CLI then reports a traceback instead of `capture unavailable`.

The 09-13 plan's rationale — "the kill makes the wait immediate" — holds only for a
runnable userspace child, not for a driver-wedged one.

**Fix:** bound the wait and make the cleanup itself failure-proof, so the original reason
survives:

```python
def _terminate(process: subprocess.Popen) -> None:
    if process.poll() is None:
        process.kill()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        pass  # the child is killed but not yet reapable; never hang the capture
```

```python
    finally:
        if process is not None:
            try:
                _terminate(process)
            except OSError:
                pass
        os.close(master)
```

## Info

### IN-01: The announced capture command still is not the executed one on the default duration

**File:** `.claude/skills/hw-flash/SKILL.md:69` and `:73-75` (mirror `.agents/skills/hw-flash/SKILL.md:70` and `:74-76`)

**Issue:** The consent gate always announces
`Capture: uv run scripts/serial_capture.py --id <id> [--env <env>] [--baud <n>] --seconds 20`,
and the delta's sentence claims "the announced capture is the executed capture". The
execution block (`:111`, `:114-116`; mirror `:112`, `:115-117`) makes `--seconds`
conditional: "Include ... `--seconds` only when the default 20 seconds is not intended."
On the normal path the executed argv therefore omits `--seconds 20` while the announced
command shows it. The duration is identical (the helper default is 20), so there is no
capability change, but the exact-command invariant the delta restates is still not true for
that segment.

**Fix:** either show `[--seconds 20]` in the gate example and name it in the conditional
sentence, or state that the default duration is always passed explicitly.

### IN-02: The helper's new exit-2 usage error is outside the skill's outcome states

**File:** `.claude/skills/hw-flash/SKILL.md:106-149` and `:178-192` (mirror `:107-150`,
`:179-193`); helper at `scripts/serial_capture.py:328-331`

**Issue:** The helper now rejects a non-finite, non-positive or above-`MAX_SECONDS` (600)
`--seconds` with exit 2 and an `ERROR:` line. The skill never states the cap and defines
exactly four outcome states, none of which is "the capture command was a usage error". An
agent that passes a user-requested longer bound (for example `--seconds 900`) gets exit 2
and has no defined state to report; it is not `capture unavailable`'s enumerated cases.

**Fix:** state the 600-second cap in "The bounded capture" and add the usage-error result
(or forbid anything but the 20-second default).

### IN-03: `CliDurationTests` does not prove the ordering the must-have claims

**File:** `scripts/tests/test_serial_capture.py:424-457`

**Issue:** The new tests patch `capture_pty` with an assertion sentinel, which proves the
validation runs before the capture. The 09-13 must-have claims the check runs "before
`resolve_root`, `_build_command` or `Popen`"; a future move of the duration check between
`resolve_root` and `capture_and_store` would keep every new test green while resolving a
git root for an invalid duration. `Popen` is only reached through the patched
`capture_pty`, so it is not independently covered either.

**Fix:** patch `serial_capture.resolve_root` and `serial_capture._build_command` with
`side_effect=AssertionError("…")` in the same `with` block, mirroring the `capture_pty`
sentinel.

### IN-04: The copula branch now refuses ordinary status lines, and the docstring overstates the negative coverage

**File:** `scripts/serial_capture.py:97-103` and `:31-34`; tests
`scripts/tests/test_serial_capture.py:205-213`

**Issue:** The copula branch (`\s+(?:is\s+)?\S{6,}`) makes benign status lines match, so a
valid capture is refused:

```text
"password is required"  -> True   (new in this delta: "is" copula + six-character value)
"auth is required"      -> True
"pwd directory"         -> True   (new in this delta: pwd keyword)
```

The helper docstring says "a match on a benign boot log is a regression the suite
forbids", but the suite pins only one ESP-ROM banner and two non-keyword words. The
guardrails explicitly accept occasional false positives, so this is not a correctness
failure of the policy; it is a mismatch between the test bar the delta asserts and the bar
it implements.

**Fix:** add these status lines to the negative fixture set (and correct the docstring if
the over-match is intentional), or narrow the copula branch's value shape.

---

_Reviewed: 2026-10-27T00:15:41Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_

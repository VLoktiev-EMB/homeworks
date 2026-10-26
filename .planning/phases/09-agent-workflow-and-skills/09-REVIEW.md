---
phase: 09-agent-workflow-and-skills
reviewed: 2026-10-26T23:13:39Z
depth: standard
files_reviewed: 13
files_reviewed_list:
  - .claude/skills/_shared/guardrails.md
  - .claude/skills/hw-flash/SKILL.md
  - .claude/skills/hw-flash/CHANGELOG.md
  - .claude/skills/hw-flash/LESSONS.md
  - .agents/skills/_shared/guardrails.md
  - .agents/skills/hw-flash/SKILL.md
  - .agents/skills/hw-flash/CHANGELOG.md
  - .agents/skills/hw-flash/LESSONS.md
  - templates/views/shared-ini.ini.tmpl
  - platformio.shared.ini
  - generated.manifest
  - generated.skills.manifest
  - scripts/tests/test_gen_views.py
findings:
  critical: 2
  warning: 6
  info: 2
  total: 10
status: issues_found
---

# Phase 09: Code Review Report

**Reviewed:** 2026-10-26T23:13:39Z
**Depth:** standard
**Files Reviewed:** 13
**Status:** issues_found

## Summary

Incremental review of the gap-closure change set at base `88ce29f`: the scoped capture
exception in the shared guardrails, the `hw-flash` baud resolution and capture snippet, the
shared-ini template baud, and the regenerated projections. The `.agents/**` files are
generated mirrors. They were compared against their canonical sources and against the
generator, not reviewed as independent files.

What holds:

- `uv run scripts/gen_views.py --all --check` and `uv run scripts/gen_skills.py --check`
  both pass. The canonical files and the `.agents` mirrors are byte-identical after the
  generator's documented frontmatter/banner transformation, so there is no mirror drift.
- The `generated.manifest` digest and byte count for `platformio.shared.ini` match the file
  (`b076e5…`, 1379 bytes). The four changed `generated.skills.manifest` entries match their
  `.agents` files. `scripts/tests/test_gen_views.py` gains
  `test_both_esp_sections_declare_the_monitor_baud`; the full module (50 tests) passes and
  leaves the worktree clean.
- `templates/views/shared-ini.ini.tmpl` and the regenerated `platformio.shared.ini` add
  `monitor_speed = 115200` to both ESP base sections. The real homework resolves it:
  `pio project config -d homeworks/1_3-police-flasher --json-output` emits
  `["monitor_speed", 115200]` under `env:esp32s3_arduino`, and PlatformIO's
  `apply_project_monitor_options` confirms the monitor inherits it when `-b` is absent.
  The prior CR-02 (baud) is genuinely closed.
- The capture exception now has one owner in the shared guardrails, and `hw-flash`
  references it instead of restating it. The prior CR-01 (policy conflict) and WR-01
  (`-e`, `OSError`, return-code check, scan, write) are addressed in form.

What does not hold:

- The capture cannot run at all under the snippet's `stdout=PIPE`. PlatformIO's monitor
  refuses a non-TTY stdout, so every run reports `capture unavailable`. This is a blocker
  (CR-01).
- The credential-shape scan that the only permitted write depends on misses ordinary
  assignment forms (`secret = …`, JSON `{"token": …}`), so the write it gates can still
  persist a credential. This is a blocker (CR-02).
- The write path, the symlink discipline, and the outcome table still contradict the rules
  stated around them (WR-01 through WR-03).

The open prior findings WR-02 through IN-05 remain tracked in `09-REVIEW-DISPOSITION.md`
and are out of this incremental scope.

## Critical Issues

### CR-01: The capture snippet pipes stdout, so `pio device monitor` always exits before the bound

**File:** `.claude/skills/hw-flash/SKILL.md:119` (mirror `.agents/skills/hw-flash/SKILL.md:120`);
command at `.claude/skills/hw-flash/SKILL.md:98-106`

**Issue:** The only executable capture example starts the monitor with
`subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE)`. PlatformIO 6.2.0
gates the monitor on an interactive stdout: `platformio/compat.py:37-39` defines
`is_terminal()` as `sys.stdout.isatty()`, and
`platformio/device/monitor/terminal.py:new_terminal()` raises `UserSideException` when it
is false. A pipe is not a TTY, so the child exits immediately with:

```text
UserSideException: `pio device monitor` requires an interactive terminal on stdin and cannot
run with piped or redirected input. If you're scripting device I/O, talk to the serial port
directly instead (e.g., with pyserial) rather than through `pio device monitor`.
```

This was reproduced against the repository's only homework:
`pio device monitor -d homeworks/1_3-police-flasher --raw -p /dev/null` with captured
stdout returned exit 1 and printed that exception. The snippet's
`if not timed_out and proc.returncode != 0` branch therefore raises `CaptureFailed` on
every run. The outcome table's "Upload succeeded, capture succeeded" state is unreachable;
every flash reports `capture unavailable`. The upload result stays correct, so this is not
data loss, but the capture leg — the reason the skill exists — never works. The CHANGELOG
claim that the snippet "implements every rule stated around it" is false for this reason
alone. The same failure applies to the bare command when the agent's tool captures stdout.

**Fix:** Do not use `pio device monitor` for a scripted capture. PlatformIO's own error
message recommends pyserial; that path also removes the TTY and banner problems:

```python
import serial, time

# Resolve the port with `pio device list --json-output` (or monitor_port).
with serial.Serial(port, baud, timeout=0.5) as ser:
    deadline = time.monotonic() + 20
    chunks = []
    while time.monotonic() < deadline:
        chunks.append(ser.read(4096))
out = b"".join(chunks)
```

If the monitor must be kept, allocate a PTY for the child's stdout and stdin, put the slave
in raw mode so the captured bytes are not rewritten, and read from the master:

```python
import os, pty, select, subprocess, time, tty

master_fd, slave_fd = pty.openpty()
tty.setraw(slave_fd)                 # preserve the device bytes
try:
    proc = subprocess.Popen(
        argv, stdin=slave_fd, stdout=slave_fd, stderr=subprocess.PIPE
    )
finally:
    os.close(slave_fd)

chunks, deadline = [], time.monotonic() + 20
while time.monotonic() < deadline:
    ready, _, _ = select.select([master_fd], [], [], deadline - time.monotonic())
    if not ready:
        break
    try:
        chunk = os.read(master_fd, 4096)
    except OSError:                  # EIO on child exit
        break
    if not chunk:
        break
    chunks.append(chunk)
proc.kill()
_, err = proc.communicate()
os.close(master_fd)
out = b"".join(chunks)
```

Add a real dry-run or test that exercises this path; no test in the repository ever starts
`pio device monitor`, which is why this regression shipped.

### CR-02: The credential-shape scan misses ordinary assignment forms, so the gated write can persist a credential

**File:** `.claude/skills/hw-flash/SKILL.md:135` (mirror
`.agents/skills/hw-flash/SKILL.md:136`); rule at
`.claude/skills/_shared/guardrails.md:54-61`

**Issue:** The guardrails' only permitted capture write is conditioned on a scan that
"finds no match for a token, secret, password, or API-key assignment". The implementation
is:

```python
CREDENTIAL = re.compile(rb"(?i)(token|secret|password|api[_-]?key)[=:]\s*\S+")
```

The separator must immediately follow the keyword, and no quoting is allowed. The
following ordinary device-output forms do not match, verified by running the regex:

```text
secret = hunter2                 MISS   (space before `=`)
PASSWORD = hunter2              MISS
{"token": "abc123"}             MISS   (quote before `:`)
{"apiKey": "abc123"}            MISS
password abc123                 MISS   (space-separated)
Authorization: Bearer eyJ...    MISS
```

`secret = hunter2` and `{"token": "abc123"}` are exactly the "token, secret, password, or
API-key assignment" shapes the rule names. Because the scan returns no match, the snippet
writes the bytes to `.skill-state/logs/<id>.log`, which violates the same file's
`[MUST]` "Never echo a token, and never write a credential" (`.claude/skills/_shared/guardrails.md:52-53`).
The prior review's suggested snippet carried this same regex; the gap closure inherited
the defect rather than closing it.

**Fix:** Allow optional whitespace and quotes around the separator and cover the common
authorization form:

```python
CREDENTIAL = re.compile(
    rb"(?i)"
    rb"(?:token|secret|passw(?:or)?d|api[ _-]?key|auth(?:orization)?)"
    rb"[\"']?\s*[=:]\s*[\"']?\S+"
)
```

This still misses a bare space-separated value (`password hunter2`). If the project wants
fail-closed behaviour on that shape too, add an explicit `\s+\S{8,}` alternative and accept
the occasional false positive; on a match the rule already requires writing nothing and
reporting `capture unavailable`.

## Warnings

### WR-01: The log path is cwd-relative, contradicting the guardrails' scoped path

**File:** `.claude/skills/hw-flash/SKILL.md:139` and `:165-166` (mirror `:140`, `:166-167`)

**Issue:** The snippet calls
`write_log_atomically(out, f".skill-state/logs/{hw_id}.log")`, and the helper resolves it
with `Path(log_path)` (line 185) against the process working directory. The rule three
paragraphs later says "Resolve the path under the repository root and confirm
`.skill-state/` is the untracked directory the `.gitignore` rule covers". If the agent runs
the snippet from any directory other than the repository root, the bytes land in a new
`.skill-state/logs/` there — outside the ignored tree and outside the exception's only
permitted path — which the guardrails explicitly forbid ("No other skill, path, or file
inherits the exception"). The directory may then be committed or scanned as repository
content.

**Fix:** Derive the absolute path once and refuse any escape:

```python
repo_root = Path(
    subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
)
log_path = repo_root / ".skill-state" / "logs" / f"{hw_id}.log"
if not log_path.resolve().is_relative_to(repo_root):
    raise CaptureFailed("log path escapes the repository root")
write_log_atomically(out, log_path)
```

Also run `git check-ignore -q .skill-state/logs/<id>.log` before the write if the
"confirm the `.gitignore` rule covers it" sentence is meant to be executable.

### WR-02: The symlink discipline claims a race-free guarantee the helper does not implement

**File:** `.claude/skills/hw-flash/SKILL.md:167-170` and `:186-197` (mirror `:168-171`,
`:187-198`)

**Issue:** The rule says to `lstat` every component and "never follow a path that is
swapped after it". The helper performs path-based `Path.is_symlink()` checks, then
`mkdir(exist_ok=True)`, `tempfile.mkstemp(dir=str(target.parent))`, and `os.replace` — all
by path. A component swapped for a symlink between the check and `mkstemp` is followed, and
`mkdir(exist_ok=True)` accepts a symlink that resolves to a directory. The atomic
`os.replace` protects against a torn file, not against a swapped parent. This is a
time-of-check/time-of-use gap against a local attacker with write access to the repository.
The claim in the prose overstates the implementation.

**Fix:** Use directory file descriptors with `O_NOFOLLOW | O_DIRECTORY` and `dir_fd`
relative operations, so the checked component is the one used:

```python
import os, tempfile

flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
root_fd = os.open(repo_root, flags)
state_fd = os.open(".skill-state", flags, dir_fd=root_fd)
logs_fd = os.open("logs", flags, dir_fd=state_fd)
fd, temporary = tempfile.mkstemp(dir=".", prefix=".capture-", dir_fd=logs_fd)
with os.fdopen(fd, "wb") as handle:
    handle.write(out)
    handle.flush()
    os.fsync(handle.fileno())
os.replace(temporary, f"{hw_id}.log", src_dir_fd=logs_fd, dst_dir_fd=logs_fd)
```

If the project accepts the residual race, delete the "never follow a path that is swapped
after it" sentence rather than promising it.

### WR-03: The outcome table contradicts the rule that reaching the 20-second bound is a success

**File:** `.claude/skills/hw-flash/SKILL.md:142-147` and `:225` (mirror `:143-148`, `:226`)

**Issue:** Lines 143-144 say "Reaching the 20-second bound is the designed end of the
capture, not a failure: the bytes collected up to it are the log." The outcome table's
fourth row says "Upload succeeded, capture failed or timed out → Report `capture
unavailable`". An agent following the table reports `capture unavailable` for a normal
20-second bound and discards a valid log; an agent following the prose may report success
for the same run. The skill also never defines a "timed out" failure distinct from the
designed bound.

**Fix:** Remove "or timed out" from the failure row and add one sentence defining success:

```markdown
| Upload succeeded, capture failed | Report `capture unavailable`; the upload exit code stays the flash result. |

A capture that reaches the 20-second bound is a success and writes the collected bytes.
Only a start failure, a pre-bound non-zero exit, a credential match, or a refused write is
`capture unavailable`.
```

### WR-04: The consent-gate example omits `-e <env>`, so it is not the exact command the rule requires

**File:** `.claude/skills/hw-flash/SKILL.md:63` (mirror `:64`), rule at `:33-34` and `:88`

**Issue:** The gate example prints `Upload: pio run -d homeworks/<id> -t upload`, while the
environment rule says to add `-e <env>` to both the upload and the monitor command when
`needs_e_flag` is true, and the shared guardrails require the exact command to be shown
before an upload. An agent copying the example announces a command that differs from the
one it is about to run, and the confirmation then does not cover the actual invocation.

**Fix:** Show the conditional flag in the example, for example
`Upload: pio run -d homeworks/<id> [-e <env>] -t upload`, with a line stating that `-e` is
included only when `needs_e_flag` is true.

### WR-05: The general credential prohibition no longer covers logs outside the exception

**File:** `.claude/skills/_shared/guardrails.md:52-53` (mirror `:53-54`), exception at
`:54-61`

**Issue:** The original rule read "never write a credential to the state file or a log".
The edit drops "or a log" and leaves the general `[MUST]` covering only the state file.
The exception that follows covers only `hw-flash`, and its "No other skill, path, or file
inherits the exception" implies the prohibition, but the explicit general rule is now
weaker. A future skill that writes a diagnostic log is no longer plainly forbidden from
writing a credential to it.

**Fix:** Restore the general clause and let the exception scope itself:

```markdown
- **[MUST]** **[ENFORCED: review]** Never echo a token, and never write a
  credential to the state file or any log, except under the scoped capture
  exception below.
```

### WR-06: The capture command omits `--quiet`, so PlatformIO's banner is captured into the log

**File:** `.claude/skills/hw-flash/SKILL.md:100-102` and `:112` (mirror `:101-103`, `:113`)

**Issue:** After the TTY defect in CR-01 is fixed, `pio device monitor` prints its four-line
terminal banner (`--- Terminal on …`, filters, details URL, quit/menu keys) to stdout via
`print_terminal_settings()`. The snippet forwards that stdout into `out` and writes it to
the log, so the "single bounded serial capture" begins with PlatformIO diagnostics rather
than the raw device stream. `--raw` disables the device encoding/transformations; it does
not suppress this banner. The log is then not the exact bytes the credential scan and the
"evidence of bytes" rule describe.

**Fix:** Add `--quiet` to the monitor argv (it suppresses the banner while leaving errors on
stderr), and keep the banner out of the credential scan and the log.

## Info

### IN-01: The snippet is not runnable as written

**File:** `.claude/skills/hw-flash/SKILL.md:108-140` and `:177-202` (mirror `:109-141`,
`:178-203`)

**Issue:** `CaptureFailed` is raised at lines 121, 132, 137, and 188 but is never defined.
`env`, `needs_e_flag`, `user_baud`, and `hw_id` are caller inputs with no shown binding.
`err` is assigned at lines 125 and 129 and never used. The prose says to validate
`user_baud` as a positive integer, but the snippet converts it with `str()` without
validation. The skill says the snippet "implements every rule stated around it", which is
not true for these items.

**Fix:** Add `class CaptureFailed(Exception): pass`, validate `user_baud = int(user_baud)`
and reject `<= 0`, and either use `err` for diagnostics or name it `_err` to show it is
deliberately discarded.

### IN-02: `pio project config` emits `monitor_speed` with two different types, and the skill does not normalize

**File:** `.claude/skills/hw-flash/SKILL.md:35-43` (mirror `:36-44`)

**Issue:** On the real homework, `pio project config -d homeworks/1_3-police-flasher
--json-output` emits `["monitor_speed", 115200]` (integer) under `env:esp32s3_arduino` but
`["monitor_speed", "115200"]` (string) under the base section `esp32s3_arduino`. The skill
says only "read its `monitor_speed` option". An agent that compares the value to the string
`"115200"` will misclassify the env value as absent and stop for a user-supplied baud even
though the project declares one (this exact mismatch is recorded in
`09-09-SUMMARY.md`).

**Fix:** State the normalization explicitly, for example
`baud = int(str(value)); if baud <= 0: stop`.

---

_Reviewed: 2026-10-26T23:13:39Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_

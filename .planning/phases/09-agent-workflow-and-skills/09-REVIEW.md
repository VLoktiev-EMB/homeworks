---
phase: 09-agent-workflow-and-skills
reviewed: 2026-10-27T10:11:54Z
depth: standard
files_reviewed: 9
files_reviewed_list:
  - scripts/serial_capture.py
  - scripts/tests/test_serial_capture.py
  - .claude/skills/_shared/guardrails.md
  - .claude/skills/hw-flash/CHANGELOG.md
  - .claude/skills/hw-flash/LESSONS.md
  - .agents/skills/_shared/guardrails.md
  - .agents/skills/hw-flash/CHANGELOG.md
  - .agents/skills/hw-flash/LESSONS.md
  - generated.skills.manifest
findings:
  critical: 1
  warning: 1
  info: 0
  total: 2
status: issues_found
---

# Phase 09: Code Review Report (09-14 gap closure)

**Reviewed:** 2026-10-27T10:11:54Z
**Depth:** standard
**Files Reviewed:** 9
**Status:** issues_found

## Summary

Review of the 09-14 gap-closure delta (`9b28bdc..HEAD`) that closed RR-CR-01 by adding a
`[\w.-]{0,32}` connector to the assignment branch of `CREDENTIAL`, naming the
keyword-followed-by-identifier form in the guardrails and the helper docstring, pinning four
fixtures, and regenerating the `.agents/skills/` mirror and `generated.skills.manifest`.

No structural findings (fallow) were provided; every finding below is narrative.

What was checked rather than assumed:

- The connector does what the four fixtures claim. Executed `find_credential` on the ten
  `REVIEW_SHAPES`, the four `ORDINARY_PASSWORD_ASSIGNMENTS`, the four
  `IDENTIFIER_SUFFIXED_ASSIGNMENTS`, and the pinned negatives: all four suffix shapes
  (`secretKey:`, `secret_key =`, `passwordHash:`, `SECRET_KEY =`) match, and `secret is`,
  the ESP-ROM boot log, `the cpwd tool reports ready`, `author wrote nothing here` and
  `auth mode = WPA2` still return `False`. The space-separated branch
  (`\s+(?:is\s+)?\S{6,}`) and `_KEYWORDS` are byte-for-byte unchanged, as the plan required.
- `python3 -m unittest scripts.tests.test_serial_capture` is `OK` (41 tests);
  `python3 -m unittest discover scripts/tests` is `OK` (418 tests); `ruff check` on both
  Python files passes.
- `uv run scripts/gen_skills.py --check` exits 0 with every record `UNCHANGED`. Each
  `.agents/skills/**` file is exactly the generated header plus its `.claude/skills/**`
  source (verified with `diff`), and every `sha256`/`bytes` value in
  `generated.skills.manifest` matches its file (`_shared/guardrails.md` 4102 B,
  `hw-flash/CHANGELOG.md` 5472 B, `hw-flash/LESSONS.md` 3191 B). No drift, no hand edit.
- The scan is linear on adversarial inputs (1 MB word run, 1 MB whitespace run, 100k
  repeated keywords: under 0.3 s each), so the connector introduces no ReDoS.

What does not hold:

- The connector's 32-character ceiling leaves keyword-prefixed identifiers longer than 32
  characters unscanned, while the guardrails sentence added by 09-14 claims the suffix form
  unconditionally. A credential assigned to a long identifier is written to the log (CR-01).
- `auth mode = WPA2`, named as a pinned benign negative by the plan and its verify command,
  is never asserted by the committed suite, so the promised regression guard does not exist
  (WR-01).

## Narrative Findings (AI reviewer)

### CR-01: The 32-character connector ceiling still writes a credential assigned to a long identifier

**Severity:** BLOCKER
**File:** `scripts/serial_capture.py:106-110` (`CREDENTIAL`), `:98-100` (comment),
`:31-33` (docstring); policy `.claude/skills/_shared/guardrails.md:63-65` and mirror
`.agents/skills/_shared/guardrails.md:62-64`

**Issue:** 09-14 added `[\w.-]{0,32}` before the separator. The bound is a hard ceiling: a
keyword followed by **33 or more** identifier characters before the separator does not
match, and `capture_and_store` then writes the bytes. Measured on the shipped function:

```text
secret + 32 word chars + " = hunter2"  -> True
secret + 33 word chars + " = hunter2"  -> False
find_credential(b"secret_key_for_production_environment_2026 = hunter2") -> False
```

and end to end through `capture_and_store` with a fake serial child:

```text
scan matched: False
log written: True bytes: 54
content: b'secret_key_for_production_environment_2026 = hunter2\r\n'
```

The guardrails sentence this plan added says the scan is fail-closed across "a keyword
followed by identifier characters such as `secretKey: <value>`, `secret_key = <value>` or
`passwordHash: <value>`" with **no bound**. A 33+ character identifier is still a keyword
followed by identifier characters, and `secret_key_for_production_environment_2026`-style
names are ordinary firmware identifiers. Only the helper's module docstring and comment
disclose the ceiling; the policy that skills read does not, and the CHANGELOG's "so ...
now match" reads as comprehensive. The residual is a false negative, so T-09-41 / R-09-02
(the accepted false-positive surface) do not cover it: the [MUST] secrets rule is violated
and the credential is persisted under the sole capture exception.

**Fix:** Make the connector admit the whole identifier run, or disclose the ceiling as an
accepted residual in every place the policy is read. Recommended:

```python
# scripts/serial_capture.py
CREDENTIAL = re.compile(
    rb"(?i)"
    + _KEYWORDS
    + rb"(?:[\w.-]{0,128}[\"']?\s*[:=]\s*[\"']?\S+|\s+(?:is\s+)?\S{6,})"
)
```

(Any bound is still a bypass, so either widen well past realistic identifier lengths or use
an unbounded `[\w.-]*`; the scan measured linear above.) Add a positive fixture with a
>32-character suffix to `IDENTIFIER_SUFFIXED_ASSIGNMENTS` and a boundary pair (32 matches,
33 matches) so the documented rule is pinned. If 32 is deliberately kept, the guardrails
sentence and the CHANGELOG must say "up to 32 characters", and the residual must be entered
as an accepted risk — a bounded connector is not "fail-closed across a keyword followed by
identifier characters".

### WR-01: The promised `auth mode = WPA2` benign negative is not pinned by the suite

**Severity:** WARNING
**File:** `scripts/tests/test_serial_capture.py:203-206`
(`test_an_ordinary_word_containing_a_keyword_does_not_match`), `:214-228` (existing
negatives)

**Issue:** The plan's must-have names the pinned benign set as "`secret is`, the ESP-ROM boot
log, `the cpwd tool reports ready`, `author wrote nothing here`, `auth mode = WPA2`", and its
`python3 -c` verify command asserts `auth mode = WPA2` explicitly. The committed suite pins
only four of the five: `grep` finds no `auth mode` or `WPA2` in
`test_serial_capture.py`. The shape returns `False` today, but nothing in the suite prevents
a future regex change from making it match. That matters more after this delta: the widened
connector is exactly the kind of change that turns `auth`-prefixed lines into assignments,
and a benign `auth` log line that starts matching causes `capture unavailable` on a real
capture. The plan's claimed regression guard therefore exists only as an ephemeral command,
not as a test.

**Fix:** Add the shape to the negative tuple:

```python
def test_an_ordinary_word_containing_a_keyword_does_not_match(self) -> None:
    for sample in (
        b"the cpwd tool reports ready\r\n",
        b"author wrote nothing here\r\n",
        b"auth mode = WPA2\r\n",
    ):
        with self.subTest(sample=sample):
            self.assertFalse(serial_capture.find_credential(sample))
```

---

_Reviewed: 2026-10-27T10:11:54Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_

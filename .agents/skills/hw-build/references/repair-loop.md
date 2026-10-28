# Repair loop

`hw-build` runs two legs: the target build and the homework's native suite. Each leg
may repair a failure at most twice per run, and the whole invocation stops for user
direction as soon as either leg exhausts its two attempts. This file is the only
statement of the loop; `SKILL.md` points here rather than restating it.

## The counter

- `attempt` starts at zero when a leg begins and counts repairs already made, not
  errors observed. Two independent compile errors in one run are not two attempts: the
  first fix is attempt one, and only a second rerun that still fails is attempt two.
- The build leg and the native leg are independent. A build leg that spends one attempt
  and then succeeds leaves the native leg its full two.
- The whole invocation stops for user direction as soon as any leg reaches two failed
  attempts. The native leg does not run after an exhausted build leg unless the user
  directs it.
- The counter resets only at a new user-directed run. It never resets between errors
  inside one run and never resets when the loop moves from one leg to the other.

## The build leg

1. Run the real command from the repository root:

   ```bash
   pio run -d homeworks/<id>
   ```

   Capture the command's real exit code. Never wrap it in a script that synthesizes a
   status, and never report a result the command did not produce.
2. Exit 0: continue to the native leg.
3. A non-zero exit: diagnose the first actionable error, make the smallest change that
   addresses it, increment `attempt`, and rerun while `attempt` is below two.
4. After the second failed attempt, stop and present the escalation payload below. Do
   not make a third edit.

## Choosing the environment

Read `homework.yaml` for the board and `platformio.ini` for `default_envs`. When
`default_envs` is absent or names several environments, pass the target environment
explicitly instead of letting a bare `pio run` build every environment:

```bash
pio run -d homeworks/<id> -e <env>
```

The current homework declares exactly one environment (`default_envs = esp32s3_arduino`),
so the bare form is correct there; the rule still applies to a homework that later adds a
second environment.

## The native leg

Run the homework's native suite with the same counter and the same stop:

```bash
pio test -d homeworks/<id> -e native
```

The native environment is reached with `pio test`, never with `pio run -e native`.
Capture the exit code and report it.

## The shared native suite

Run the shared suite:

```bash
pio test -d tests -e native
```

only when one of exactly two triggers fired:

- the user explicitly asked for it, or
- `git diff --quiet -- lib/` reports a change (a non-zero exit), because a change under
  the shared `lib/` fans out to every consumer. This is the same condition
  `scripts/affected.py` uses for its build matrix.

State which trigger fired. When neither fired, state that the shared suite was skipped
because neither trigger fired.

`hw-build` is a homework build helper, not the repository's full pre-PR gate. The full
chain is `pre-commit run --all-files`, `uv run scripts/check_metadata.py`,
`python3 -m unittest discover scripts/tests`, and the shared suite. A green `hw-build`
run never claims that the complete repository chain ran.

## What a repair may touch

A repair may touch `src/`, `include/`, or a homework-local `homeworks/<id>/lib/**`
source. A homework-local library is a normal repair target, not unrelated code, because
the homework owns its pattern library.

A test fixture may be repaired only when it is demonstrably wrong and the user confirms
the repair. An assertion is never weakened and a test is never deleted to make the
implementation pass. When the implementation is wrong, fix the implementation.

A repair never reformats unrelated code, never reorders includes across files, and never
edits a file the first actionable error does not name. It never runs `git checkout --`,
never resets the tree, and never commits: a commit requires the guardrails confirmation,
including the one announced by the escalation.

## Warnings

A warning is never treated as an error. Quote it as a warning and keep going: a
deprecation notice or an informational `unsupported-part` note does not consume an
attempt. Warnings are quoted separately from errors in the escalation payload so the
reader can tell them apart.

## What the loop remembers

`hw-build` writes no durable checkpoint. `.skill-state/<id>.json` belongs to
`new-homework`; this skill records its result only in the conversation.

Two F-05 facts a repair must respect:

- The native environment repeats `-Wall -Wextra -Werror`, so a signed/unsigned
  comparison or an unused local fails only the host build while the target build stays
  green. Cast sizes explicitly rather than suppressing the warning.
- Both host fakes are reset in `setUp`, and the idle `INPUT_PULLUP` button is seeded to
  `PORT_GPIO_HIGH`. A fake that models every pin as LOW at reset reads as "button
  pressed", so a test that forgets the seed fails for the fixture's reason, not the
  implementation's.

Two F-03 cold-run facts:

- A first native run downloads Unity 2.6.1 into `.pio/`; the download is expected and is
  not a build failure.
- A denied outbound version check during the first target build does not affect the
  artifact; ignore it rather than treating it as the actionable error.

## The escalation payload

After the second failed attempt on either leg, stop and present:

1. **Cause** — one paragraph naming what is actually wrong in the code, not a paraphrase
   of the compiler's first line.
2. **The two fixes** — each with the file it touched and the reasoning behind it.
3. **The evidence** — every command run, its exit code, and the first error lines
   verbatim.
4. **Warnings** — quoted separately from the errors.
5. **What was ruled out** — the hypotheses already tested and rejected.
6. **One question** — whether to continue, revert the attempted fixes, or change the
   approach.

The escalation never edits again. It ends the run and waits for direction.

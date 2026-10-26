# Shared guardrails

Every implemented skill reads this file before its first write, and no skill may
override a rule here with its own prompt wording.

Each rule carries a severity and the point where a violation is caught, using
the same register as `AGENTS.md`.

## Flashing

- **[MUST]** **[ENFORCED: review]** Show the board, the environment, and the
  exact command before any upload, and wait for a literal affirmative.
- **[MUST]** **[ENFORCED: review]** Accept exactly `так` or `yes`, case
  insensitive, with no other text. Never default to yes. An empty answer, a
  refusal, a question, or anything else is a stop, and the action needs a new
  invocation.
- **[MUST]** **[ENFORCED: review]** Never pre-approve `upload` in
  `allowed-tools`, because that would let a client skip the human gate.

## Commit and pull request

- **[MUST]** **[ENFORCED: review]** Never commit, push, open a pull request, or
  create a tag without confirmation.
- **[MUST]** **[ENFORCED: review]** One atomic commit per change, verified and
  without unrelated work.
- **[MUST]** **[ENFORCED: review]** Commit messages follow Conventional Commits
  `type(scope): summary`, with the phase-plan or homework ID as the scope.
- **[MUST]** **[ENFORCED: review]** Squash-merge only into the default branch.
- **[MUST]** **[ENFORCED: review]** Create the `hw/<id>` tag only through
  `scripts/tag_homework.sh <id>`, after the homework pull request is merged.
- **[MUST]** **[ENFORCED: review]** A confirmation covers exactly the action it
  announced. Never reuse a previous confirmation for a later action.

## Specification versus best practice

- **[MUST]** **[ENFORCED: review]** Present the specification and the best
  practice side by side, recommend one, record the assumption in the state
  file, and ask before proceeding.
- **[MUST]** **[ENFORCED: review]** Silence, delay, or an indirect answer is
  never acceptance. The assumption stays `proposed` until a recorded
  affirmative.

## Ambiguity

- **[MUST]** **[ENFORCED: review]** Ask, or record a recommended assumption and
  continue only after the user accepts it.
- **[MUST]** **[ENFORCED: review]** If the user does not answer, the block
  stalls. It never proceeds on inferred consent.

## Secrets

- **[MUST]** **[ENFORCED: review]** Never echo a token, and never write a
  credential to the state file or a log.
- **[MUST]** **[ENFORCED: review]** Record presence only as
  `simulation_token_present: true|false`.

## Evidence

- **[MUST]** **[ENFORCED: review]** A simulation is never bench evidence.
- **[MUST]** **[ENFORCED: review]** A failed or blocked run never produces a
  verified claim.
- **[MUST]** **[ENFORCED: review]** Never describe a simulation as a flash.

These rules are `[ENFORCED: review]` per D-18, and the phase dry-run transcript
is the only practical check of the flashing and commit rules; a red transcript
is the finding, not a reason to soften the rule.

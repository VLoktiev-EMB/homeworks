---
status: accepted
date: 2026-10-25
decision-makers: [VLoktiev-EMB]
consulted: []
informed: []
---

# Squash-merge commit title and message

## Context and Problem Statement

GitHub's repository default `squash_merge_commit_message=COMMIT_MESSAGES` composes the squash
commit body from the subject line of every commit on the merged branch. Pull request #7 was a
long phase branch with dozens of commits, so its squash body listed each of them, including the
final ship commit subject `docs(04): ship phase 04 — PR #7 [ci skip]`. GitHub Actions treats a
skip token anywhere in the head commit message as an instruction to skip the push, so the
`security` push workflow produced no check-runs on `main` for commit `c904062`, even though the
pull request pipeline itself had run. The skip token was a local convenience, not a statement
about the merged result, yet automatic body composition promoted it to a repository-wide CI
decision. `AGENTS.md` forbids rewriting published history, so `c904062` stays exactly as it is;
the only available remedy is forward-only. How should the squash commit title and body be
composed so that no unreviewed branch subject can silently reach the default branch?

## Decision Drivers

* The merge commit message must be authored and reviewable, not an automatic concatenation of
  every branch commit subject.
* The live repository setting must be declarative in `policy/repository.json`, so
  `python3 scripts/check_policy.py --check` detects drift instead of allowing a silent revert
  to `COMMIT_MESSAGES`.
* Published history is never rewritten, so the fix must change future squashes only and must
  not touch `c904062`.
* The squash title should stay stable across a multi-commit pull request, while a
  single-commit pull request may still take its commit subject as the title; that residual
  behavior is a documented risk rather than something this setting removes.
* A skip token deliberately placed in a pull-request body or in a single commit subject can
  still suppress a push, so the rulebook expectation that ship notes never carry a skip token
  in the pull-request body remains in force.

## Considered Options

* `COMMIT_OR_PR_TITLE` plus `PR_BODY`, declared in `policy/repository.json`.
* Keep `COMMIT_MESSAGES` and rely on review discipline alone.
* `PR_TITLE` plus `BLANK`.
* A commit-msg hook that rejects skip tokens, keeping `COMMIT_MESSAGES`.

## Decision Outcome

Chosen option: "`COMMIT_OR_PR_TITLE` plus `PR_BODY`, declared in `policy/repository.json`",
because the title stays stable for a multi-commit pull request and the body becomes the reviewed
pull-request description rather than an automatic concatenation of every branch subject, while
the two keys are compared leaf by leaf by the existing drift checker.

GitHub then derives the title from the pull-request title whenever the branch carries more than
one commit (the single-commit exception is accepted and recorded above) and takes the body from
the pull-request description that a reviewer has already read. Because the two fields are now
part of the committed policy, `--check` reports a mismatch if live GitHub state is changed back
to `COMMIT_MESSAGES`, the same way it already reports drift in branch protection.

The change is forward-only. `c904062` keeps the composed body and the missing `security`
check-runs; no rebase, force-push, or history edit is proposed, because rotation of a published
commit is exactly what the Git policy prohibits.

### Consequences

* Good, because the squash body is the reviewed pull-request description instead of the union of
  every branch commit subject, so a stray skip token in a local commit subject no longer reaches
  the default branch through automatic composition.
* Good, because both fields are declared in `policy/repository.json` and the existing generic
  projection compares them, so drift is detected without a checker change.
* Good, because the squash title stays stable across a multi-commit pull request, which keeps
  the permanent record readable.
* Bad, because a skip token deliberately written in the pull-request body still suppresses the
  push, so the setting removes the automatic path but not every path; review must keep ship
  notes clean.
* Bad, because a single-commit pull request may still use that commit's subject as the squash
  title, so a skip token in that one subject can still suppress a push.
* Neutral, because the fix does not recover the missing `security` check-runs for `c904062`;
  that gap is recorded and closed only by the next push to `main`.

### Confirmation

The decision is confirmed by runnable gates, not by inspection:

* `python3 scripts/check_policy.py --apply` PATCHes the flattened `policy/repository.json` to
  the origin repository, then re-reads live state.
* `python3 scripts/check_policy.py --check` reads `GET /repos/{owner}/{repo}`, projects the
  response onto the committed keys, and compares leaf by leaf; both
  `squash_merge_commit_title` and `squash_merge_commit_message` must print PASS.
* `python3 -m unittest discover -s scripts/tests -v` keeps the policy projection, the test
  suite, and the ADR structure checks green together.

A revert to `COMMIT_MESSAGES` on the live repository is caught by the same `--check` run,
because the committed value is the expected value and no separate watch job is involved.

## Pros and Cons of the Options

### `COMMIT_OR_PR_TITLE` plus `PR_BODY`, declared in `policy/repository.json`

The title is the pull-request title for a multi-commit branch, and the body is the pull-request
description that a reviewer approved; both keys are part of the committed policy.

* Good, because the body becomes reviewed prose instead of an automatic list of branch commit
  subjects.
* Good, because the committed declaration makes the setting drift-checkable with the checker
  that already exists.
* Good, because the merge title remains stable and predictable for a multi-commit pull request.
* Neutral, because the single-commit title exception remains, so the setting narrows the skip
  token path rather than eliminating it.
* Bad, because a skip token placed in the pull-request body still suppresses the push, so review
  discipline is still required.

### Keep `COMMIT_MESSAGES` and rely on review discipline alone

The repository default is left in place, and reviewers are expected to notice a skip token in
any branch commit subject before merging.

* Good, because no repository setting changes and no policy key is added.
* Neutral, because the behavior is documented rather than prevented.
* Bad, because this is the option that caused the `c904062` incident: the composed body carried
  `[ci skip]` and the `security` push workflow never ran.
* Bad, because review discipline cannot be drift-checked; a single missed token suppresses CI
  with no visible policy violation.

### `PR_TITLE` plus `BLANK`

The squash body is left empty and only the pull-request title is retained.

* Good, because an empty body cannot carry a skip token from any branch commit subject.
* Neutral, because the merge title still follows the pull-request title.
* Bad, because the reviewed pull-request rationale is discarded from the permanent record,
  leaving only a title where the project expects the why of a change.

### A commit-msg hook that rejects skip tokens, keeping `COMMIT_MESSAGES`

A local and pre-commit hook rejects any commit message containing a skip token, while the
GitHub default continues to compose the squash body.

* Good, because it stops the token at the point where the local ship note is authored.
* Bad, because it applies to direct commits only; it cannot see the pull-request body, and it
  does not prevent future branch subjects from composing a new token shape.
* Bad, because it keeps `COMMIT_MESSAGES`, so the permanent squash body is still an unreviewed
  concatenation of branch subjects that no repository policy compares.

## More Information

The incident is visible in the published history: commit `c904062` carries the composed body and
the absence of `security` check-runs. This record does not claim any workflow run or check-run
that does not exist, and it deliberately does not propose editing that commit.

Related records:

* `docs/decisions/0003-git-policy-and-protected-main.md` establishes linear history and
  the no-rewrite rule that makes this decision forward-only.
* `docs/decisions/0010-python-dependency-policy.md` is the precedent for binding a rule to a
  runnable drift test rather than to a convention.

The policy pair is `squash_merge_commit_title=COMMIT_OR_PR_TITLE` and
`squash_merge_commit_message=PR_BODY` in `policy/repository.json`; the checker requires no
change because it flattens every declared leaf and PATCHes the same keys. Revisit this decision
if GitHub adds a per-pull-request squash-message override that makes the repository setting
irrelevant, or if the rulebook later decides that a single-commit title exception is
unacceptable.

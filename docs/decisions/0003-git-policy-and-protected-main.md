---
status: accepted
date: 2026-10-23
decision-makers: [VLoktiev-EMB]
consulted: []
informed: []
---

# Git policy and protected main branch

## Context and Problem Statement

The repository is already public, so anything that reaches its history is effectively
permanent: a secret, personal data, or instructor material cannot be scrubbed without the
history rewriting this very policy forbids. `main` must therefore be protected by a rule
that is visible, reviewable, and provably in force, rather than by settings that exist only
in a web UI and drift silently. How should the protection of `main` be defined and kept
honest?

## Decision Drivers

* Auditable history: every change to `main` is a reviewed pull request with a linear,
  squash-merged history.
* Zero-maintenance protection: the rule must survive repository settings changes and be
  reproducible for a future maintainer or a rebuild.
* Drift detection: an accidental weakening of protection must be detectable by a command,
  not by memory.
* Single-maintainer reality: requiring reviews nobody can provide would either block all
  work or train the maintainer to bypass the rule.

## Considered Options

* Classic branch protection configured in the web UI
* Ruleset stored as code with a check and apply script
* Unmanaged protection, relying on convention alone

## Decision Outcome

Chosen option: "Ruleset stored as code with a check and apply script", because it is the only
option that makes the protection both reproducible and drift-detectable while remaining a
single, declarative object.

The live `main` ruleset is committed as `policy/ruleset-main.json` and compared against
GitHub by `scripts/check_policy.py --check`, with `--apply` to re-assert it; the exit-code
contract is `0` = match, `1` = drift, `2` = usage or environment error, and CI wiring is
deferred to Phase 8. The committed subset targets `~DEFAULT_BRANCH`, declares an empty
`bypass_actors` array, and carries six rules: block creation, block deletion, non-fast-forward
(force-push) prevention, required linear history, a pull-request rule with
`required_approving_review_count: 0` and `allowed_merge_methods: ["squash"]`, and required
status checks. Repository settings live alongside it in `policy/repository.json`.

**Scope of squash-only.** Squash-only applies to merges *into the default branch*, not to the
repository as a whole. The ruleset's `required_linear_history` rule together with
`pull_request.allowed_merge_methods: ["squash"]` is the single enforcement point; the
repository-level `allow_merge_commit` and `allow_rebase_merge` flags stay `true` so that
feature branches may be combined with any strategy while `main` still accepts only squashes.
One mechanism, in one place to audit.

**Approvals trigger.** Zero required approvals is correct for a single maintainer, and it is
a decision with a stated expiry: raise `required_approving_review_count` to 1 when a second
maintainer joins. Until then, adding an approval requirement would either halt work or be
bypassed, which is worse than an honest zero.

### Consequences

* Good, because the protection is a reviewable file: a change to it is a visible diff in a
  pull request, not an undocumented click.
* Good, because drift has a command and a stable exit code, so the Phase 8 CI job can fail a
  pull request that weakens the rule.
* Good, because the policy is rebuildable: the committed subset plus `--apply` reconstitutes
  the live rule.
* Bad, because the committed file is a *writable subset*, not a verbatim export of the live
  ruleset; the read-only and server-assigned fields must never be round-tripped (the GET body
  is not a PUT body).
* Bad, because a policy file can only assert settings the platform can actually honor; a
  permanently red assertion trains reviewers to ignore the check, so unachievable settings
  must be removed and tracked as a revisit trigger instead.

**Accepted audit gaps.** These are recorded deliberately rather than left implicit:

* **`hw/<id>` tags are mutable.** Branch rulesets never evaluate against tag refs, so
  `non_fast_forward` and `deletion` on `main` say nothing about tags. A `hw/<id>` tag can be
  moved or deleted by anyone with push access; `scripts/tag_homework.sh` (which verifies the
  pull request is merged, checks the tag is unused, and only then creates and pushes it) is
  the only guard. If tag immutability becomes a requirement, add a tag-targeted ruleset.
* **`.planning/` stays public.** The planning record is tracked as the project's audit trail,
  and it becomes permanently public with everything else. This is accepted as a consequence of
  the no-rewrite policy rather than treated as a mistake; the research cache under
  `.planning/research/.cache/` is untracked and gitignored, so only the human-authored record
  is published.
* **`hw/<id>` tags and `.planning/` publicity** are the two gaps a reader of a green policy
  check might otherwise assume away.

### Confirmation

Confirmed against the live repository by the measurements recorded in the Phase 1 policy
plan's summary:

* `scripts/check_policy.py --check` exits `0`, and an independent read-only query of
  `GET /repos/VLoktiev-EMB/homeworks/rules/branches/main` returns exactly the six rule types
  `creation`, `deletion`, `non_fast_forward`, `pull_request`, `required_linear_history`, and
  `required_status_checks`.
* Repository settings report `delete_branch_on_merge: true`, `allow_squash_merge: true`,
  `allow_merge_commit: true`, `allow_rebase_merge: true`, `allow_auto_merge: false`, plus
  secret scanning and secret-scanning push protection enabled.

Two platform behaviors observed during that work are part of this decision, because each one
changes how the policy must be verified:

1. **A 200 response is not evidence that a setting applied.** On the organization's free
   plan, GitHub accepted the settings `PATCH`, returned `200 OK`, and *silently ignored*
   unsupported `security_and_analysis` fields: `secret_scanning` and
   `secret_scanning_push_protection` applied, while `secret_scanning_validity_checks` and
   `secret_scanning_non_provider_patterns` were dropped without an error. The policy
   therefore declares only the two achievable statuses, and every consumer must re-read and
   diff the live value rather than trust the response code. `--apply` does exactly that.
2. **A plan restriction is a hard boundary, not drift.** The revisit trigger is explicit:
   re-add `secret_scanning_validity_checks` and `secret_scanning_non_provider_patterns` to
   `policy/repository.json` when the organization moves to GitHub Team or Enterprise, and not
   before.

One assumption remains **unverified**: the live `pull_request` rule exposes the undocumented
parameter `require_extra_approval_for_unattributed_changes` as `true`, which the committed
subset does not declare. Whether a `PUT` preserves or resets it, together with
`required_reviewers: []` and `dismissal_restriction`, has not been observed. `--check`
projects only the declared fields, so it will not report the difference; a maintainer
re-applying the ruleset should confirm those fields afterwards.

## Pros and Cons of the Options

### Classic branch protection configured in the web UI

Use GitHub's older branch-protection settings, configured by hand.

* Good, because it requires no tooling and no files.
* Neutral, because the effective rules can be inspected in the UI.
* Bad, because the configuration is not reviewable as a diff and is invisible to anyone
  reading the repository.
* Bad, because a settings change is undetectable until someone notices a broken expectation;
  there is no drift check.
* Bad, because reproducing the configuration after an incident depends on memory.

### Ruleset stored as code with a check and apply script

Commit the writable subset of the live ruleset and diff it with `gh api`.

* Good, because the rule is a reviewable artifact and changes are ordinary pull requests.
* Good, because `--check` turns drift into a non-zero exit code that CI can enforce.
* Good, because rulesets expose `bypass_actors` explicitly, so "who can skip the rule" is
  declared rather than implied.
* Neutral, because the committed file must be a writable subset; read-only fields cannot be
  round-tripped.
* Bad, because it introduces a script and a JSON file to maintain, and the script's checks are
  only as complete as the declared subset.

### Unmanaged protection, relying on convention alone

Document the expectation and trust contributors to follow it.

* Good, because it costs nothing to set up.
* Bad, because a convention cannot stop a direct push or a force-push.
* Bad, because there is nothing to verify against, so the claim "`main` is protected" becomes
  unverifiable.

## More Information

The policy files are `policy/ruleset-main.json` and `policy/repository.json`; the checker is
`scripts/check_policy.py`. Repository layout and naming are recorded in
[ADR-0001](0001-monorepo-with-independent-projects.md). The secret-scanning cadence and the
response to a real leaked secret are governed by the pre-commit and CI configuration, not by
this record. This decision is revisited when a second maintainer joins (approvals trigger),
when the organization changes GitHub plan (secret-scanning trigger), or when tag immutability
becomes a requirement.

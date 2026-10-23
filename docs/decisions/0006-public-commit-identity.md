---
status: accepted
date: 2026-10-23
decision-makers: [VLoktiev-EMB]
consulted: []
informed: []
---

# Public commit identity

## Context and Problem Statement

`AGENTS.md` forbids a real name in commits: identity in published history must be the public
handle. Three commits on `main` (`57ff7ba`, `e2dd499`, `69c2434`) nevertheless carry the
maintainer's real name as the author:

```
Author:    <the public account's profile display name>
Committer: GitHub
Email:     a handle-based GitHub noreply address
```

The local Git configuration was correct: `user.name` and `user.email` resolve to the handle
and its handle-based noreply address. The display name was supplied by GitHub itself: all three
commits were created server-side — the initial commit through the web interface, the other two
by squash-merge through the API — and GitHub writes the **profile display name** of the merging
account into the squash commit, ignoring the identity of the commits on the branch. The address
is the handle-based noreply address throughout.

History cannot be rewritten: the repository ruleset rejects force-pushes, and `AGENTS.md`
treats published history as immutable. The name is therefore permanently present in a public
repository. Must the phase stay blocked on a fact that cannot be changed by any compliant
action, and must every future squash-merge re-trigger the same finding?

## Decision Drivers

* The repository is public by design; the maintaining account is public and deliberately used
  for this project.
* `AGENTS.md` forbids rewriting published history, so no remediation of past commits exists.
* The rule against real names exists to prevent **private** personal information from becoming
  permanent, not to require pseudonymity of a public project account.
* Every future squash-merge performed through GitHub will carry the same display name, so the
  choice governs all later phases, not this one.

## Considered Options

* Keep the rule literal, accept that the phase can never verify, and rewrite history — rejected:
  rewriting is forbidden and the commit is already public.
* Change the GitHub profile display name to the handle and treat the three existing commits as a
  permanent exception.
* Accept the public account display name as the repository's commit identity.

## Decision Outcome

Chosen option: "Accept the public account display name as the repository's commit identity."
The names in `57ff7ba`, `e2dd499`, and `69c2434` are recorded as an accepted risk, not a defect:
the account is public, the address is a handle-based `noreply` address, and no institution,
private email, or additional personal detail accompanies it.

The maintainer may still change the GitHub profile display name to `VLoktiev-EMB`; that changes
**future** merges only and does not retroactively alter these commits. The rule in `AGENTS.md`
retains its force for every other surface: no real name may appear in `LICENSE`, `NOTICE`,
report metadata, prose, or trailers beyond what this decision records.

### Consequences

* Good, because the phase is no longer blocked by an act the rules themselves forbid repairing.
* Good, because future verification runs have a documented, citable disposition.
* Bad, because the name is permanent in public history and cannot be withdrawn.
* Bad, because the letter of the `AGENTS.md` identity rule and this decision diverge for
  commit metadata; a reader must consult this record to understand why.
* Neutral, because the handle-based email means the address itself reveals nothing beyond the
  public account.

### Confirmation

`01-SECURITY.md` records the finding as accepted risk `R-1-02` with `threats_open: 0`. The
commit metadata is inspectable with `git log --format='%an <%ae>' origin/main`. No automated
check rejects the display name today; if one is added, it must allow the public account's
display name, otherwise it will fail on history that cannot be rewritten.

## Pros and Cons of the Options

### Keep the rule literal and rewrite history

Rewrite the three commits with a handle identity and force-push.

* Good, because the rule would hold literally.
* Bad, because force-pushing a protected public branch is rejected by the ruleset.
* Bad, because the commits have already been public; rewriting would hide, not remove, exposure.
* Bad, because it contradicts the explicit no-rewrite policy.

### Change the profile display name and treat the past as an exception

Set the GitHub profile name to the handle; past commits keep the old name.

* Good, because future squash-merges would carry the handle.
* Neutral, because the three existing commits remain unchanged either way.
* Bad, because it makes the maintainer's public presence inconsistent across GitHub.

### Accept the public account display name

Record the identity as accepted and keep the public account as the sole author identity.

* Good, because it is the only option that reflects what can actually be done under the rules.
* Good, because the public account is already the project's deliberate public identity.
* Bad, because it weakens the literal wording of the identity rule for this one surface.

## More Information

The finding was raised by the Phase 1 verifier against the goal "history … safe by construction
and cannot be repaired later". It is recorded here rather than repaired because repair is
prohibited. The related license and attribution boundary is [ADR-0004](0004-license-and-attribution.md).

# Research questions

Open questions that need evidence before they change the roadmap.

## 2026-10-26 — Which quality gates earn their recurring cost?

**Context.** The repository runs 13 pre-commit hooks, a clang-tidy pre-push pass with a
compile-database freshness guard, a metadata and schema gate, an architecture gate, a
generated-views drift check, gitleaks, and Phase 8 proposes a CI pipeline with several
jobs. The felt problem from the 2026-10-26 exploration is not any single check but the
ratio of checking to homework work: the repository appears to revolve around
verification rather than around learning and completing homework.

**Question.** For each gate, what is the evidence that it caught a real defect?

**Method.**

1. Enumerate every gate and every job, including the ones Phase 8 proposes.
2. For each, search the git history for a commit or fix that the gate preceded or
   blocked. Record the commit hash and the defect.
3. Separate gates with a recorded catch from gates that have never fired.
4. Rank by runs per change multiplied by maintenance cost, per the decision rule in
   `.planning/notes/ceremony-vs-engineering-principle.md`.
5. Propose a keep / simplify / cut list with the evidence attached to each row.

**Discipline.**

- Do not cut a gate that has a recorded catch without stating why the risk no longer
  applies.
- Do not keep a gate whose only justification is "good practice".
- A gate that runs once per milestone is not a priority for demolition; a gate that
  runs on every change is.

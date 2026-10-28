# Pull request

## What and why

Describe the change and why it is needed.

Optional cross-references:

- **Issue / tracker:** `<e.g. #123>`

## Research and standards

- Authoritative sources consulted (official docs, standards, datasheets):
- Applicable standards and best practices:
- Discrepancies and accepted deviations (if any):

## Definition of Done

- [ ] `pio run` is green for the affected environment
- [ ] `pio test -e native` is green when the change contains pure logic
- [ ] `task.md`, `homework.yaml`, `README.md`, and `report.md` exist and `uv run scripts/check_metadata.py` passes
- [ ] `pre-commit run --all-files` passes
- [ ] The required gate check is green

### Report self-audit

The checker proves structure, not that a value was measured. Confirm all four:

- [ ] Every bill-of-materials row traces to a part id in `assets/diagram.json`
- [ ] Every ledger label matches its evidence: `measured` for an instrument reading, `calculated` for a formula, `simulated` for a run, and `not measured` with a stated reason
- [ ] The `Implementation commit` is the same in the metadata table and every ledger row
- [ ] Limitations and next steps are stated

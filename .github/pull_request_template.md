# Pull request

## What and why

Describe the change and why it is needed.

Optional cross-references:

- **Phase / requirement:** `<e.g. FOUND-03, Phase 4.1>`
- **ADR / issue:** `<docs/decisions/0003-... or #123>`

## Definition of Done

- [ ] `pio run` is green for the affected environment
- [ ] `pio test -e native` is green when the change contains pure logic
- [ ] `task.md`, `homework.yaml`, `README.md`, and `report.md` exist and `uv run scripts/check_metadata.py` passes
- [ ] `pre-commit run --all-files` passes
- [ ] The required gate check is green
- [ ] The report contains the sections that apply to the assignment

#!/usr/bin/env python3
"""The one usage/environment exception the repository tools share.

`scripts/metadata/contract.py` imports PyYAML and jsonschema at module scope,
and `scripts/tests/` may import neither library (04/D-14). A stdlib-only module
that imported `CheckError` from `contract.py` would therefore drag the whole
validation stack into every environment that imports it — including the
PyYAML-only `gen-views-check` pre-commit hook and the `generated-views` CI job.

This module holds the class and nothing else. `contract.py`, `paths.py`,
`render.py` and `platformio.py` all bind it, so `except CheckError` in one entry
script catches the error raised by another module's call.
"""


class CheckError(Exception):
    """A usage or environment problem, reported with exit code 2."""

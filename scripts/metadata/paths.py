#!/usr/bin/env python3
"""Identity and path helpers shared by the scaffold and the generators.

These four names used to live in `scripts/metadata/contract.py`, which imports
PyYAML and jsonschema at module scope. `scripts/gen_views.py` and
`scripts/affected.py` declare only PyYAML in their PEP 723 header, so importing
`contract.py` for `derive_parts`, `resolve_root`, `relative_path` or
`HOMEWORK_ID` would fail with `ModuleNotFoundError: jsonschema` in exactly the
environments that must run the drift gate (blocking review finding, T-5-28).

Everything here is stdlib-only: `pathlib`, `re`, `subprocess` and the shared
exception. `contract.py` re-exports these names, so every existing
`from scripts.metadata.contract import ...` call site resolves to the same
object.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

from scripts.metadata.errors import CheckError

# The canonical homework-identifier literal. The schema's `id.pattern`, the
# backticked span in `AGENTS.md` and this constant must stay byte-identical.
HOMEWORK_ID = re.compile(r"^[0-9]+_[0-9]+-[a-z0-9-]+$")


def resolve_root(explicit):
    """Return the repository root, explicit or resolved through git."""
    if explicit:
        return Path(explicit).resolve()
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        raise CheckError(f"cannot execute git: {exc}") from exc
    root = proc.stdout.strip()
    if proc.returncode != 0 or not root:
        detail = proc.stderr.strip() or "git rev-parse failed"
        raise CheckError(f"cannot locate the repository root: {detail}")
    return Path(root).resolve()


def relative_path(root, path):
    """Render *path* as a repository-relative POSIX path (T-04-08).

    A path outside the checked root is reduced to its final component so an
    absolute root is never echoed into the report.
    """
    resolved = Path(path).resolve()
    try:
        return resolved.relative_to(Path(root).resolve()).as_posix()
    except ValueError:
        return Path(path).name


def derive_parts(homework_id):
    """Return module, lesson, slug and display title derived from *homework_id*.

    These parts are never stored in a document (D-02). A value that does not
    match the canonical identifier shape is a usage error (exit 2): the caller
    passed an id the repository cannot represent.
    """
    if not isinstance(homework_id, str) or not HOMEWORK_ID.match(homework_id):
        raise CheckError(
            f"invalid homework id {homework_id!r}; expected module_lesson-name "
            "matching ^[0-9]+_[0-9]+-[a-z0-9-]+$"
        )
    module, _, remainder = homework_id.partition("_")
    lesson, _, slug = remainder.partition("-")
    return {
        "module": module,
        "lesson": lesson,
        "slug": slug,
        "title": slug.replace("-", " ").title(),
    }

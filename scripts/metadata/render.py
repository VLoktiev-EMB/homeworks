#!/usr/bin/env python3
"""The one closed `{{name}}` renderer the scaffold and the generators share.

D-19 lifts the placeholder vocabulary out of `scripts/new_homework`, so the
scaffold and `scripts/gen_views.py` cannot drift. D-33 forbids a template
language: substitution is a single, non-recursive pass over a closed map.

The non-recursive property is load-bearing (T-5-01). A metadata value that
itself contains an opening `{{...}}` sequence is emitted verbatim: it is never
re-scanned, so a homework title can never inject a placeholder into a second
pass. `re.sub` guarantees this; `RendererContractTests` pins it.

This module imports `os`, `re`, `stat` and the shared exception only, so a
stdlib-only test runner can import it without pulling PyYAML or jsonschema
(04/D-14).
"""

from __future__ import annotations

import os
import re
import stat

from scripts.metadata.errors import CheckError

# D-25/D-33: a closed placeholder vocabulary, and `${...}` is never allowed
# because PlatformIO, CMake and SCons own that syntax.
PLACEHOLDER = re.compile(r"\{\{([^{}]*)\}\}")
DOLLAR_BRACE = re.compile(r"\$\{[^}]*\}")


def render(text, mapping, display):
    """Substitute the closed map; an unknown token or `${...}` stops the run.

    The substitution is one pass. A value copied *out* of *mapping* is never
    scanned again, so a metadata value containing `{{name}}` reaches the output
    verbatim.
    """
    if DOLLAR_BRACE.search(text):
        raise CheckError(
            f"{display}: dollar-brace interpolation '${{...}}' is not allowed"
        )

    def replace(match):
        token = match.group(1)
        if token not in mapping:
            raise CheckError(
                f"{display}: unknown placeholder " + "{{" + token + "}}"
            )
        return mapping[token]

    return PLACEHOLDER.sub(replace, text)


def read_text(source, display):
    """Read one template file as UTF-8; failure is an environment error."""
    try:
        return source.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise CheckError(f"{display}: template file is not valid UTF-8: {exc}") from exc
    except OSError as exc:
        raise CheckError(f"cannot read template file {display}: {exc}") from exc


def read_regular_text(source, display):
    """Read one regular UTF-8 file, refusing a symlink on the final component.

    `os.lstat` never follows the final component, so a repository entry that a
    pull request replaced with a symlink is refused before its target is read.
    `scripts/new_homework` refuses symlinked template entries the same way, so
    the generator and the scaffold share one posture (CR-02).
    """
    try:
        mode = os.lstat(source).st_mode
    except FileNotFoundError as exc:
        raise CheckError(f"cannot read {display}: file is absent") from exc
    except OSError as exc:
        raise CheckError(f"cannot inspect {display}: {exc}") from exc
    if stat.S_ISLNK(mode):
        raise CheckError(f"{display} is a symlink; refusing to follow it")
    if not stat.S_ISREG(mode):
        raise CheckError(f"{display} is not a regular file")
    return read_text(source, display)

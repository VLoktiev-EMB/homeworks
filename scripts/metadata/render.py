#!/usr/bin/env python3
"""The one closed `{{name}}` template renderer.

Substitution is a single, non-recursive pass over a closed map.
The non-recursive property guarantees that a metadata value that itself contains
an opening `{{...}}` sequence is emitted verbatim: it is never re-scanned.

This module imports `os`, `re`, `stat` and the shared exception only.
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

    `os.lstat` checks the entry without following. On POSIX systems, `os.open`
    with `O_NOFOLLOW` and `os.fstat` close the check-then-use race window (WR-13).
    The repository gate assumes a static git checkout where files are not
    mutated concurrently; O_NOFOLLOW ensures atomic symlink substitution fails
    with OSError before reading.
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

    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(source, flags)
    except OSError as exc:
        raise CheckError(f"cannot open {display}: {exc}") from exc

    try:
        st = os.fstat(fd)
        if stat.S_ISLNK(st.st_mode):
            os.close(fd)
            raise CheckError(f"{display} is a symlink; refusing to follow it")
        if not stat.S_ISREG(st.st_mode):
            os.close(fd)
            raise CheckError(f"{display} is not a regular file")
        with open(fd, encoding="utf-8", closefd=True) as file_obj:
            return file_obj.read()
    except UnicodeDecodeError as exc:
        raise CheckError(f"{display}: template file is not valid UTF-8: {exc}") from exc
    except OSError as exc:
        raise CheckError(f"cannot read {display}: {exc}") from exc

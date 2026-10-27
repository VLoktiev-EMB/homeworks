#!/usr/bin/env python3
"""Pipe-table cell parsing and normalization (D-03).

A GFM table row may carry an escaped pipe inside a cell. Splitting on every
`|` would silently shift every later column, so the splitter recognizes `\\|`
and leaves the escape in the cell until the split is complete (Pitfall 5).

Normalization is the one shared comparison rule (Pitfall 2): identity cells
carry backticks and mixed inline code, so a comparison that does not strip
them fails on a compliant report.

This module imports the standard library only (D-02).
"""

from __future__ import annotations

import re

_WHITESPACE = re.compile(r"\s+")


def split_row(line):
    """Split one pipe-table row on unescaped pipes only.

    The leading and trailing delimiters are dropped when present. An escaped
    `\\|` stays literal inside its cell; `normalize_cell` unescapes it after the
    split. A row without a leading pipe is still a row, as GFM allows.
    """
    text = line.strip()
    if text.startswith("|"):
        text = text[1:]
    if text.endswith("|") and not text.endswith("\\|"):
        text = text[:-1]

    cells = []
    current = []
    index = 0
    while index < len(text):
        character = text[index]
        if character == "\\" and index + 1 < len(text) and text[index + 1] == "|":
            current.append("\\|")
            index += 2
            continue
        if character == "|":
            cells.append("".join(current))
            current = []
            index += 1
            continue
        current.append(character)
        index += 1
    cells.append("".join(current))
    return [cell.strip() for cell in cells]


def normalize_cell(value):
    """Strip inline-code markers, unescape pipes, collapse whitespace."""
    text = value.replace("\\|", "|").replace("`", "")
    return _WHITESPACE.sub(" ", text).strip()


def normalize_platform(value):
    """Normalize a platform pin so both repository spellings compare equal."""
    text = normalize_cell(value)
    if text.startswith("platformio/"):
        text = text[len("platformio/") :]
    return _WHITESPACE.sub(" ", text.replace("@", " ")).strip()

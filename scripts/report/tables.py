#!/usr/bin/env python3
"""Pipe-table cell parsing and table-block extraction (D-03).

A GFM table row may carry an escaped pipe inside a cell. Splitting on every
`|` would silently shift every later column, so the splitter recognizes `\\|`
and leaves the escape in the cell until the split is complete (Pitfall 5).

Normalization is the one shared comparison rule (Pitfall 2): identity cells
carry backticks and mixed inline code, so a comparison that does not strip
them fails on a compliant report.

Table blocks are extracted in the same linear pass that already skips fenced
code: a table drawn inside a fence is never parsed. A table starts at a line
that begins with `|` and whose successor is a separator row; leading and
trailing pipes on data rows are optional, but a row is only part of the block
while the next line still looks like a row.

This module imports the standard library only (D-02) plus its stdlib-only
sibling `scripts.report.markdown`, whose fence definition it reuses.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from scripts.report import markdown

_WHITESPACE = re.compile(r"\s+")

# A separator cell: one or more dashes with an optional alignment colon.
_SEPARATOR = re.compile(r"^:?-+:?$")


@dataclass(frozen=True)
class Row:
    """One data row: its source line, raw cells and normalized cells."""

    line: int
    cells: tuple[str, ...]
    normalized: tuple[str, ...]


@dataclass(frozen=True)
class Table:
    """One pipe table: the header line, its normalized header, and its rows."""

    header_line: int
    header: tuple[str, ...]
    rows: tuple[Row, ...]


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


def _is_separator(line):
    """True when every cell of *line* is a separator cell (`---`, `:---`)."""
    cells = split_row(line)
    return bool(cells) and all(_SEPARATOR.match(cell) for cell in cells)


def _is_row(line):
    """True when *line* can belong to a table block (non-blank, piped, no heading)."""
    stripped = line.strip()
    return bool(stripped) and "|" in stripped and markdown.ATX.match(stripped) is None


def extract_tables(text):
    """Return every pipe table outside a fenced code block, in document order.

    The fence state is the same one `scripts.report.markdown` uses, so a table
    drawn inside a fence is invisible to the contract (Pitfall 4/Pitfall 5).
    A data row whose cell count differs from the header is still collected; the
    shape rule (`RPT-202`) reports it instead of silently dropping it.
    """
    lines = text.splitlines()
    total = len(lines)
    tables = []
    in_fence = False
    index = 0
    while index < total:
        line = lines[index]
        if markdown.FENCE.match(line):
            in_fence = not in_fence
            index += 1
            continue
        if in_fence or not line.lstrip().startswith("|"):
            index += 1
            continue
        if index + 1 >= total or not _is_separator(lines[index + 1]):
            index += 1
            continue

        header = tuple(normalize_cell(cell) for cell in split_row(line))
        rows = []
        cursor = index + 2
        while cursor < total and _is_row(lines[cursor]):
            raw = tuple(split_row(lines[cursor]))
            rows.append(
                Row(
                    cursor + 1,
                    raw,
                    tuple(normalize_cell(cell) for cell in raw),
                )
            )
            cursor += 1
        tables.append(Table(index + 1, header, tuple(rows)))
        index = cursor
    return tuple(tables)

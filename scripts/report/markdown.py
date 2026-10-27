#!/usr/bin/env python3
"""Structural Markdown scanning for the report contract (D-03).

One linear pass classifies every line, and a second pass groups the headings
into sections. The parser knows exactly two constructs — ATX headings and the
paragraph starts the contract names — because that is all the contract needs; a
full CommonMark parser is deliberately out of scope.

The fence toggle runs before the heading test and never changes numbering
(Pitfall 4): the original lines are enumerated once, so a heading after a
fenced block reports its true line number.

This module imports the standard library only (D-02).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# A fenced code block opens or closes on ``` or ~~~ at any indentation.
FENCE = re.compile(r"^\s*(```|~~~)")

# An ATX heading: one to six hashes, a space, the text, an optional closing run.
ATX = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")


@dataclass(frozen=True)
class Heading:
    """One ATX heading with its source line number."""

    level: int
    text: str
    line: int


@dataclass(frozen=True)
class Section:
    """One level-2 section, its child headings, and its inclusive body range."""

    heading: Heading
    children: tuple[Heading, ...]
    body_start: int
    body_end: int


def headings(lines):
    """Return every ATX heading outside a fenced code block."""
    found = []
    in_fence = False
    for number, line in enumerate(lines, start=1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = ATX.match(line)
        if match is None:
            continue
        found.append(Heading(len(match.group(1)), match.group(2).strip(), number))
    return found


def sections(lines, found=None):
    """Group the headings into level-2 sections with their children and body.

    `body_start` is the first line after the section heading; `body_end` is the
    line before the next level-2 heading, or the last line of the document.
    Every subsection requirement resolves against its own parent section (Pitfall
    7), so a `### Limitations` under the wrong section is not mistaken for one
    under `## 4. Theory`.
    """
    if found is None:
        found = headings(lines)
    total = len(lines)
    tops = [heading for heading in found if heading.level == 2]
    grouped = []
    for index, heading in enumerate(tops):
        end = tops[index + 1].line - 1 if index + 1 < len(tops) else total
        children = tuple(
            child for child in found if child.level > 2 and heading.line < child.line <= end
        )
        grouped.append(Section(heading, children, heading.line + 1, end))
    return grouped


def paragraph_starts(lines, start, end):
    """Yield `(line_number, text)` for the first line of each paragraph.

    The range is inclusive and one-based. A hard-wrapped continuation line is
    not a paragraph start, so a citation that happens to begin a wrapped line is
    not mistaken for a reference entry (Pitfall 1).
    """
    blank_before = True
    for number in range(start, end + 1):
        text = lines[number - 1]
        if not text.strip():
            blank_before = True
            continue
        if blank_before:
            yield number, text
        blank_before = False


def paragraph_begins_with(lines, start, end, prefix):
    """True when some paragraph in the range starts with *prefix*."""
    return any(text.lstrip().startswith(prefix) for _, text in paragraph_starts(lines, start, end))


# An IEEE reference entry: `[N] ` at a paragraph start.
REFERENCE_ENTRY = re.compile(r"^\[(\d+)\]\s")

# An in-text citation token.
CITATION = re.compile(r"\[(\d+)\]")


def reference_entries(lines, sections, heading):
    """Return `(number, line)` for each reference entry inside *heading*.

    Entries are collected only from the named section, and only at paragraph
    starts. A hard-wrapped continuation line that happens to begin `[N] ` is
    therefore never mistaken for a seventh entry (Pitfall 1).
    """
    section = next((item for item in sections if item.heading.text == heading), None)
    if section is None:
        return []
    entries = []
    for number, text in paragraph_starts(lines, section.body_start, section.body_end):
        match = REFERENCE_ENTRY.match(text.strip())
        if match:
            entries.append((int(match.group(1)), number))
    return entries


def citation_tokens(lines, sections, headings):
    """Return `(number, line)` for every `[N]` token in the named sections.

    Citations are collected from the body sections and the decision appendix
    only, never from the reference list itself, so an entry's own `[N]` marker
    is not counted as a citation.
    """
    wanted = set(headings)
    tokens = []
    for section in sections:
        if section.heading.text not in wanted:
            continue
        for number in range(section.body_start, section.body_end + 1):
            for match in CITATION.finditer(lines[number - 1]):
                tokens.append((int(match.group(1)), number))
    return tokens

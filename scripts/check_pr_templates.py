#!/usr/bin/env python3
"""Verify the pull-request template contract.

The repository ships three type-specific pull-request templates under
``.github/PULL_REQUEST_TEMPLATE/``. They share one byte-identical header between
the ``<!-- pr-header:start -->`` and ``<!-- pr-header:end -->`` markers and
differ only in their Definition of Done checklist. This script makes header
drift, an empty DoD section, a broken marker pair, or a default template at any
path GitHub would read one from fail before a pull request is opened.

Usage:
  python3 scripts/check_pr_templates.py [--dir PATH]

Exit codes (a CI contract from Phase 8 onward):
  0  the template contract holds
  1  contract violation (header drift, empty DoD, broken markers, default template)
  2  usage or environment error (bad arguments, missing template file, git failure)

Only the byte range between the markers is compared. A whole-file comparison
would be wrong: the Definition of Done differs by type by design (D-23). The
check is read-only and idempotent; it never writes to the tree.
"""

from __future__ import annotations

import argparse
import difflib
import re
import subprocess
import sys
from pathlib import Path

TEMPLATE_DIR = Path(".github") / "PULL_REQUEST_TEMPLATE"
TEMPLATE_NAMES = ("homework.md", "infra.md", "docs.md")
START_MARKER = b"<!-- pr-header:start -->"
END_MARKER = b"<!-- pr-header:end -->"

# GitHub looks for a default template in three folders, and a file there
# suppresses the chooser and silently becomes every pull request's template.
# Two shapes are supported in each folder: a ``pull_request_template.md`` file,
# or a ``PULL_REQUEST_TEMPLATE/`` directory containing ``default.md``. The names
# are matched case-insensitively because the repository may be checked out on a
# case-sensitive filesystem, so the list is derived by scanning the folders
# instead of naming every casing.
SUPPORTED_FOLDERS = ("", "docs", ".github")
DEFAULT_FILE_NAME = "pull_request_template.md"
CHOOSER_DIR_NAME = "pull_request_template"
DEFAULT_ENTRY_NAME = "default.md"

DOD_HEADING = re.compile(r"^##\s+Definition of Done\s*$", re.IGNORECASE)
SECTION_HEADING = re.compile(r"^#{1,2}\s")
CHECKLIST = re.compile(r"^\s*-\s*\[[ xX]\]")


class CheckError(Exception):
    """A usage or environment problem, reported with exit code 2."""


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


def read_template(root, name):
    """Read one template as bytes; a missing file is an environment error."""
    path = root / TEMPLATE_DIR / name
    try:
        return path.read_bytes()
    except OSError as exc:
        raise CheckError(f"cannot read template {path}: {exc}") from exc


def header_slice(data):
    """Return the bytes strictly between the two markers."""
    start = data.find(START_MARKER) + len(START_MARKER)
    end = data.find(END_MARKER)
    return data[start:end]


def marker_problems(templates):
    """One start and one end marker per template, in that order."""
    problems = []
    for name, data in templates.items():
        starts = data.count(START_MARKER)
        ends = data.count(END_MARKER)
        if starts != 1 or ends != 1:
            problems.append(
                f"{name}: expected exactly one start and one end marker, "
                f"found {starts} start / {ends} end"
            )
        elif data.find(START_MARKER) > data.find(END_MARKER):
            problems.append(f"{name}: end marker precedes start marker")
    return problems


def _print_diff(name, reference_name, actual, expected):
    left = actual.decode("utf-8", errors="replace").splitlines()
    right = expected.decode("utf-8", errors="replace").splitlines()
    for line in difflib.unified_diff(
        left, right, fromfile=name, tofile=reference_name, lineterm=""
    ):
        print(f"  {line}")


def check_header(templates):
    """Compare the marker slices only; return the number of failed checks."""
    reference_name = TEMPLATE_NAMES[0]
    reference = header_slice(templates[reference_name])
    problems = []
    if not reference.strip():
        problems.append(f"{reference_name}: shared header slice is empty")
    for name in TEMPLATE_NAMES[1:]:
        if header_slice(templates[name]) != reference:
            problems.append(f"{name}: header slice differs from {reference_name}")

    if not problems:
        count = len(TEMPLATE_NAMES)
        print(f"PASS header: {count} shared header slices are byte-identical")
        return 0

    print("FAIL header: shared header must be byte-identical across templates")
    for problem in problems:
        print(f"  {problem}")
    for name in TEMPLATE_NAMES[1:]:
        if header_slice(templates[name]) != reference:
            _print_diff(name, reference_name, header_slice(templates[name]), reference)
    return 1


def dod_problems(name, text):
    """Every Definition of Done section needs at least one checklist row."""
    lines = text.splitlines()
    headings = [i for i, line in enumerate(lines) if DOD_HEADING.match(line)]
    if not headings:
        return [f"{name}: no '## Definition of Done' section"]
    problems = []
    for index in headings:
        rows = 0
        for line in lines[index + 1 :]:
            if SECTION_HEADING.match(line):
                break
            if CHECKLIST.match(line):
                rows += 1
        if rows == 0:
            problems.append(
                f"{name}: Definition of Done at line {index + 1} "
                "has no checklist rows"
            )
    return problems


def check_dod(templates):
    """Require a non-empty DoD checklist in every template."""
    problems = []
    for name, data in templates.items():
        problems.extend(dod_problems(name, data.decode("utf-8", errors="replace")))
    if problems:
        print("FAIL definition-of-done: every type needs at least one checklist row")
        for problem in problems:
            print(f"  {problem}")
        return 1
    print("PASS definition-of-done: checklist rows present in every type")
    return 0


def _matching_entries(directory, name):
    """Entries of *directory* named *name*, matched case-insensitively."""
    try:
        children = sorted(directory.iterdir(), key=lambda child: child.name)
    except OSError:
        return []
    return [child for child in children if child.name.lower() == name]


def default_template_paths(root):
    """Every path GitHub treats as a default template, in lookup order."""
    present = []
    for folder in SUPPORTED_FOLDERS:
        directory = root / folder if folder else root
        for entry in _matching_entries(directory, DEFAULT_FILE_NAME):
            if entry.is_file():
                present.append(entry.relative_to(root).as_posix())
        for chooser in _matching_entries(directory, CHOOSER_DIR_NAME):
            if not chooser.is_dir():
                continue
            for entry in _matching_entries(chooser, DEFAULT_ENTRY_NAME):
                if entry.is_file():
                    present.append(entry.relative_to(root).as_posix())
    return present


def check_default_templates(root):
    """No default PR template may exist at any supported lookup path."""
    present = default_template_paths(root)
    if present:
        print("FAIL default-template: a default template suppresses the chooser")
        for path in present:
            print(f"  {path}")
        return 1
    print("PASS default-template: no default PR template at any fallback path")
    return 0


def run_check(root):
    """Print the report and return the number of failed checks."""
    templates = {name: read_template(root, name) for name in TEMPLATE_NAMES}
    print(f"PASS templates: {len(TEMPLATE_NAMES)} type-specific templates present")

    broken_markers = marker_problems(templates)
    if broken_markers:
        print("FAIL markers: malformed shared-header markers")
        for problem in broken_markers:
            print(f"  {problem}")
        print("FAIL header: cannot compare a header with malformed markers")
        failures = 2
    else:
        print("PASS markers: exactly one start and one end marker per template")
        failures = check_header(templates)

    failures += check_dod(templates)
    failures += check_default_templates(root)
    return failures


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Verify the pull-request template contract."
    )
    parser.add_argument(
        "--dir",
        metavar="PATH",
        help="repository root to check (default: git rev-parse --show-toplevel)",
    )
    args = parser.parse_args(argv)

    try:
        root = resolve_root(args.dir)
        failures = run_check(root)
    except CheckError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if failures:
        print()
        print("FAIL: PR template contract violated")
        return 1
    print()
    print("PASS: PR template contract satisfied")
    return 0


if __name__ == "__main__":
    sys.exit(main())

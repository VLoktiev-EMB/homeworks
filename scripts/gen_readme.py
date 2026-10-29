#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["PyYAML==6.0.3", "jsonschema==4.26.0"]
# ///
"""Regenerate the root README homework index.

The root ``README.md`` carries exactly one generated region, delimited by the
literal markers::

    <!-- BEGIN GENERATED: homeworks -->
    ...generated table...
    <!-- END GENERATED -->

Every byte outside that region is authored prose and is preserved exactly. The
region is a projection of the schema-validated metadata under
``homeworks/*/homework.yaml``, so a document that fails the contract is never
rendered.

Usage::

    uv run scripts/gen_readme.py              # rewrite the region in place
    uv run scripts/gen_readme.py --check      # report drift, write nothing
    uv run scripts/gen_readme.py --dir PATH   # operate on another root

Exit codes: 0 for a current or successfully written region; 1 for a content
error (invalid metadata, stale region in check mode); 2 for a usage or
environment error (unreadable README, malformed marker region, unresolvable
root, write failure).

The output is deterministic: no clock, no git remote and no network are read,
and the write goes through a temporary file in the same directory plus
``os.replace``.
"""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.metadata.contract import (
    CheckError,
    resolve_root,
    validate_homework_text,
)

MARKER_BEGIN = "<!-- BEGIN GENERATED: homeworks -->"
MARKER_END = "<!-- END GENERATED -->"
README_NAME = "README.md"
EMPTY_MESSAGE = "No homework assignments published yet."
REGENERATE_COMMAND = "uv run scripts/gen_readme.py"
TABLE_HEADER = "| ID | Project | Board | Framework | Status | Report |"
TABLE_SEPARATOR = "| --- | --- | --- | --- | --- | --- |"


class UsageError(Exception):
    """A usage or environment problem; the process exits 2."""


class ContentError(Exception):
    """An invalid metadata document; the process exits 1."""


def _read_readme(root):
    """Return the README text, raising ``UsageError`` when it cannot be read."""
    path = Path(root) / README_NAME
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise UsageError(f"{path}: {exc}") from exc


def _load_homeworks(root):
    """Return ``(homework_id, document)`` pairs in directory-name order."""
    homeworks_dir = Path(root) / "homeworks"
    records = []
    if not homeworks_dir.is_dir():
        return records
    try:
        entries = sorted(homeworks_dir.iterdir(), key=lambda item: item.name)
    except OSError as exc:
        raise UsageError(f"{homeworks_dir}: {exc}") from exc

    for entry in entries:
        if not entry.is_dir():
            continue
        document_path = entry / "homework.yaml"
        if not document_path.is_file():
            continue
        homework_id = entry.name
        try:
            text = document_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            raise UsageError(f"{document_path}: {exc}") from exc
        try:
            document = validate_homework_text(
                text, root=root, homework_id=homework_id
            )
        except CheckError as exc:
            raise ContentError(f"homeworks/{homework_id}/homework.yaml: {exc}") from exc
        records.append((homework_id, document))
    return records


def _cell(value):
    """Escape a free-text value for a Markdown table cell.

    The backslash is escaped first: escaping the pipe first would turn a
    literal ``\\|`` in a title into an escaped backslash followed by a live
    separator, splitting the row.
    """
    return str(value).replace("\\", "\\\\").replace("|", "\\|")


def _report_cell(homework_id, document):
    """Render the report cell from validated metadata, never from disk state."""
    report = document.get("report")
    if isinstance(report, dict):
        path = report.get("path")
        if isinstance(path, str) and path:
            return f"[report](homeworks/{homework_id}/{path})"
    return "none"


def _row(homework_id, document):
    """Render one table row for *document*."""
    title = _cell(document.get("title", ""))
    board = _cell(document.get("board", ""))
    framework = _cell(document.get("framework", ""))
    status = _cell(document.get("status", ""))
    project = f"[{title}](homeworks/{homework_id}/)"
    return (
        f"| {_cell(homework_id)} | {project} | {board} | {framework} "
        f"| {status} | {_report_cell(homework_id, document)} |"
    )


def _region_body(records):
    """Render the body between the markers."""
    if not records:
        return EMPTY_MESSAGE
    rows = [TABLE_HEADER, TABLE_SEPARATOR]
    rows.extend(_row(homework_id, document) for homework_id, document in records)
    return "\n".join(rows)


def _render_region(records):
    """Render the whole marker-delimited region."""
    return "\n\n".join([MARKER_BEGIN, _region_body(records), MARKER_END])


def _region(text):
    """Return the half-open ``(start, stop)`` span covering both markers."""
    begin_count = text.count(MARKER_BEGIN)
    end_count = text.count(MARKER_END)
    if begin_count != 1 or end_count != 1:
        raise UsageError(
            f"{README_NAME}: expected exactly one {MARKER_BEGIN!r} and one "
            f"{MARKER_END!r}; found {begin_count} and {end_count}"
        )
    start = text.index(MARKER_BEGIN)
    end_start = text.index(MARKER_END)
    if end_start < start:
        raise UsageError(f"{README_NAME}: end marker precedes begin marker")
    return start, end_start + len(MARKER_END)


def _write_atomic(path, text):
    """Install *text* at *path* through a sibling temporary file."""
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", dir=path.parent, delete=False
        ) as handle:
            temporary = Path(handle.name)
            handle.write(text.encode("utf-8"))
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except OSError:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
        raise


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Regenerate the root README homework index"
    )
    parser.add_argument("--dir", help="Repository root path")
    parser.add_argument(
        "--check", action="store_true", help="Report drift without writing"
    )
    args = parser.parse_args(argv)

    try:
        root = resolve_root(args.dir)
    except CheckError as exc:
        print(f"gen_readme: {exc}", file=sys.stderr)
        return 2

    try:
        text = _read_readme(root)
        start, stop = _region(text)
        records = _load_homeworks(root)
    except UsageError as exc:
        print(f"gen_readme: {exc}", file=sys.stderr)
        return 2
    except ContentError as exc:
        print(f"gen_readme: {exc}", file=sys.stderr)
        return 1

    new_text = text[:start] + _render_region(records) + text[stop:]

    if new_text == text:
        return 0

    if args.check:
        print(f"{README_NAME}: stale — run: {REGENERATE_COMMAND}", file=sys.stderr)
        return 1

    readme_path = root / README_NAME
    try:
        _write_atomic(readme_path, new_text)
    except OSError as exc:
        print(f"gen_readme: {readme_path}: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())

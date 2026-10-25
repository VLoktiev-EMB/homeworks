#!/usr/bin/env python3
"""Apply the board-profile contract to one `boards/<id>.yaml`.

`schema/board-profile.schema.json` is the machine-readable contract for every
board profile, and this module is its single implementation (D-27). The entry
point `scripts/check_metadata.py` finds the documents and hands their text to
`validate_board_text`; no validation rule lives in the entry script.

The split between content and environment is the one the homework contract
already uses:

* a content problem — an oversized file, a YAML syntax error, a non-mapping
  payload, a duplicated key, a schema violation, or an `id` that disagrees with
  the file stem — is an `ERROR` record (exit 1);
* an unreadable, unparseable or invalid schema is a `CheckError` (exit 2).

Board documents are parsed with `StrictSafeLoader`, never `yaml.safe_load`:
PyYAML silently keeps the last value of a duplicated mapping key, and a board
profile is authored data that a bad merge can duplicate.

Every record path is rendered with `relative_path`, so an out-of-root path
degrades to its final component and no absolute location leaks into a report.
"""

from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError

# `contract.py` re-exports the shared names below; importing them here keeps one
# `CheckError` class and one strict loader for both document families.
from scripts.metadata.contract import (
    MAX_INPUT_BYTES,
    CheckError,
    StrictSafeLoader,
    relative_path,
)

BOARD_SCHEMA_PATH = Path("schema") / "board-profile.schema.json"
BOARD_DIRECTORY = Path("boards")


def load_board_schema(root):
    """Read and pre-validate the committed board schema; any failure is exit 2."""
    path = Path(root) / BOARD_SCHEMA_PATH
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise CheckError(f"cannot read schema {path}: {exc}") from exc
    except UnicodeDecodeError as exc:
        raise CheckError(f"cannot decode schema {path}: {exc}") from exc
    try:
        schema = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise CheckError(f"cannot parse schema {path}: {exc}") from exc
    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as exc:
        raise CheckError(f"schema {path} is invalid: {exc.message}") from exc
    return schema


def _one_line(value):
    """Collapse a possibly multi-line YAML error into one report line."""
    return " ".join(str(value).split())


def _render_error(error):
    """Render one schema error as `property_path: message`."""
    location = ".".join(str(part) for part in error.absolute_path)
    if not location:
        return error.message
    return f"{location}: {error.message}"


def validate_board_text(text, *, root, path):
    """Validate one board-profile payload; return a list of records.

    Each record is `{"path", "status", "reason", "line"}` where `status` is
    `OK` or `ERROR`. Content problems (size, YAML syntax, non-mapping payload,
    duplicated key, schema violation, identity mismatch) are ERROR records and
    therefore exit 1; a broken schema raises `CheckError` and exits 2.
    """
    display = relative_path(root, path)

    def record(status, reason):
        return {"path": display, "status": status, "reason": reason, "line": 0}

    if len(text.encode("utf-8")) > MAX_INPUT_BYTES:
        return [record("ERROR", f"document is larger than {MAX_INPUT_BYTES} bytes")]

    try:
        document = yaml.load(text, Loader=StrictSafeLoader)
    except yaml.YAMLError as exc:
        return [record("ERROR", f"invalid YAML: {_one_line(exc)}")]

    if not isinstance(document, dict):
        return [record("ERROR", "document is not a YAML mapping")]

    errors = []
    schema = load_board_schema(root)
    for error in Draft202012Validator(schema).iter_errors(document):
        errors.append(_render_error(error))

    # Identity is lexical like `homework.yaml`: the file stem must equal `id`,
    # and neither side is resolved through the filesystem.
    document_id = document.get("id")
    stem = Path(path).stem
    if isinstance(document_id, str) and document_id != stem:
        errors.append(
            f"id: {document_id!r} does not match the file stem {stem!r}"
        )

    if not errors:
        return [record("OK", "board profile contract satisfied")]
    return [record("ERROR", reason) for reason in sorted(set(errors))]

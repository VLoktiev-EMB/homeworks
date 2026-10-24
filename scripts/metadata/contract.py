#!/usr/bin/env python3
"""Apply the homework metadata contract to one document.

This module is the single implementation of the `homework.yaml` rules (D-12).
Both callers — `scripts/check_metadata.py` and the `scripts/new_homework`
scaffold — import it, so the checker and the scaffold cannot drift. The schema
is committed data at `schema/homework.schema.json`; this module only reads and
applies it.

Usage (through the entry script):
  uv run scripts/check_metadata.py [--dir PATH] [--json] [PATH...]

Exit codes (a CI contract from Phase 8 onward):
  0  every scanned document satisfies the contract
  1  violation (schema, identity invariant, toolchain drift, or an unreadable
     document payload), reported as an ERROR record
  2  usage or environment error (bad arguments, missing or malformed schema,
     unreadable or inconsistent shared PlatformIO configuration)

Content problems stay at exit 1 by construction: an oversized document, a YAML
syntax error, a non-mapping payload and a duplicated mapping key are all
violations of a file under `homeworks/`, not failures of the environment. Only
a broken schema or a broken shared configuration exits 2.

`module`, `lesson`, `slug` and the display title are derived from `id` on
demand and never stored (D-02); `id` is the single source of identity.

The validator is read-only: it never writes to the tree, never reads the clock,
and two consecutive runs produce byte-identical output.
"""

from __future__ import annotations

import configparser
import json
import re
import subprocess
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError
from yaml.constructor import ConstructorError


class CheckError(Exception):
    """A usage or environment problem, reported with exit code 2."""


MAX_INPUT_BYTES = 64 * 1024

SCHEMA_PATH = Path("schema") / "homework.schema.json"
SHARED_INI_PATH = Path("platformio.shared.ini")
ESP_SECTIONS = ("esp32s3_arduino", "esp32s3_espidf")

# The canonical homework-identifier literal. The schema's `id.pattern`, the
# backticked span in `AGENTS.md` and `EXPECTED_PATTERN` in
# `scripts/tests/test_homework_id.py` must stay byte-identical to this one.
HOMEWORK_ID = re.compile(r"^[0-9]+_[0-9]+-[a-z0-9-]+$")

PLATFORMIO_CORE = "6.2.0"


class StrictSafeLoader(yaml.SafeLoader):
    """A `SafeLoader` that rejects a duplicated mapping key (T-04-20).

    PyYAML silently keeps the last value of a repeated key, so a duplicated
    `source:` or `toolchain:` block would override the first one without a
    trace. This loader turns that into a parse error, which the caller reports
    as an ERROR record at exit 1.
    """

    def construct_mapping(self, node, deep=False):
        seen = set()
        for key_node, _ in node.value:
            key = self.construct_object(key_node, deep=deep)
            if key in seen:
                raise ConstructorError(
                    "while constructing a mapping",
                    node.start_mark,
                    f"found duplicate key {key!r}",
                    key_node.start_mark,
                )
            seen.add(key)
        return super().construct_mapping(node, deep=deep)


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


def read_shared_platform_pin(root):
    """Return the ESP32-S3 platform pin from `platformio.shared.ini`.

    A missing file, a missing ESP section, a missing pin or two sections that
    disagree are repository-environment failures (exit 2), because the shared
    configuration is the source the metadata is compared against (D-07).
    """
    path = Path(root) / SHARED_INI_PATH
    parser = configparser.ConfigParser(interpolation=None)
    try:
        with path.open(encoding="utf-8") as handle:
            parser.read_file(handle)
    except OSError as exc:
        raise CheckError(f"cannot read {path}: {exc}") from exc
    except UnicodeDecodeError as exc:
        raise CheckError(f"cannot decode {path}: {exc}") from exc
    except configparser.Error as exc:
        raise CheckError(f"cannot parse {path}: {exc}") from exc

    pins = {}
    for section in ESP_SECTIONS:
        if not parser.has_section(section):
            raise CheckError(f"{path} is missing the [{section}] section")
        if not parser.has_option(section, "platform"):
            raise CheckError(f"{path} [{section}] is missing the platform pin")
        pins[section] = parser.get(section, "platform").strip()
    if len(set(pins.values())) != 1:
        detail = ", ".join(f"[{name}] {value}" for name, value in pins.items())
        raise CheckError(f"{path} ESP sections disagree on platform: {detail}")
    return pins[ESP_SECTIONS[0]]


def load_schema(root):
    """Read and pre-validate the committed schema; any failure is exit 2."""
    path = Path(root) / SCHEMA_PATH
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


def _homework_directory(root, path):
    """Return `homeworks/<dir>`'s `<dir>` when *path* is its `homework.yaml`."""
    try:
        parts = Path(path).resolve().relative_to(Path(root).resolve()).parts
    except ValueError:
        return None
    if len(parts) == 3 and parts[0] == "homeworks" and parts[2] == "homework.yaml":
        return parts[1]
    return None


def validate_homework_text(text, *, root, path):
    """Validate one `homework.yaml` payload; return a list of records.

    Each record is `{"path", "status", "reason", "line"}` where `status` is
    `OK` or `ERROR`. Content problems (size, YAML syntax, non-mapping payload,
    duplicated key, schema violation, identity mismatch, toolchain drift) are
    ERROR records and therefore exit 1; environment problems raise
    `CheckError` and exit 2.
    """
    display = relative_path(root, path)

    def record(status, reason):
        return {"path": display, "status": status, "reason": reason, "line": 0}

    if len(text.encode("utf-8")) > MAX_INPUT_BYTES:
        return [
            record(
                "ERROR",
                f"document is larger than {MAX_INPUT_BYTES} bytes",
            )
        ]

    try:
        document = yaml.load(text, Loader=StrictSafeLoader)
    except yaml.YAMLError as exc:
        return [record("ERROR", f"invalid YAML: {_one_line(exc)}")]

    if not isinstance(document, dict):
        return [record("ERROR", "document is not a YAML mapping")]

    errors = []
    schema = load_schema(root)
    for error in Draft202012Validator(schema).iter_errors(document):
        errors.append(_render_error(error))

    pin = read_shared_platform_pin(root)
    toolchain = document.get("toolchain")
    if isinstance(toolchain, dict):
        platform = toolchain.get("platform")
        if isinstance(platform, str) and platform != pin:
            errors.append(
                f"toolchain.platform: {platform!r} does not match the shared "
                f"pin {pin!r}"
            )

    directory = _homework_directory(root, path)
    if directory is not None:
        document_id = document.get("id")
        if isinstance(document_id, str) and document_id != directory:
            errors.append(
                f"id: {document_id!r} does not match the containing directory "
                f"{directory!r}"
            )

    if not errors:
        return [record("OK", "metadata contract satisfied")]
    return [record("ERROR", reason) for reason in sorted(set(errors))]

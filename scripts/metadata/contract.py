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

`read_shared_core_pin` parses the generated `; PlatformIO Core: <version>` header
line, the only home the Core pin has. The checker does not call it yet: an
earlier wave may run `check_metadata.py` on a fixture root before the shared ini
has been generated, and a reader that requires the header would fail a valid
pre-generation tree. `SharedIniTests` pins the generated Core pin against every
homework's `toolchain.platformio` instead.

`module`, `lesson`, `slug` and the display title are derived from `id` on
demand and never stored (D-02); `id` is the single source of identity.

The validator is read-only: it never writes to the tree, never reads the clock,
and two consecutive runs produce byte-identical output.
"""

from __future__ import annotations

import configparser
import datetime
import json
import os
import re
import unicodedata
from collections.abc import Hashable
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError
from yaml.constructor import ConstructorError

# Re-exports, not second definitions (D-19, T-5-28). `errors.py`, `paths.py` and
# `yaml_loader.py` are stdlib-only or PyYAML-only, so the generators can import
# the same objects without pulling jsonschema into their environment.
from scripts.metadata.errors import CheckError
from scripts.metadata.paths import (
    HOMEWORK_ID,
    derive_parts,
    relative_path,
    resolve_root,
)
from scripts.metadata.yaml_loader import DepthBoundedLoaderMixin, StrictSafeLoader

# The names above are re-exports, not second definitions (D-19, T-5-28): callers
# import them from here, so they must survive a linter that cannot see those
# callers. Naming them explicitly is the declaration that they are the module's
# public surface; deleting one would break a documented import path.
__all__ = [
    "CheckError",
    "HOMEWORK_ID",
    "StrictSafeLoader",
    "derive_parts",
    "relative_path",
    "resolve_root",
]

MAX_INPUT_BYTES = 64 * 1024

SCHEMA_PATH = Path("schema") / "homework.schema.json"
SHARED_INI_PATH = Path("platformio.shared.ini")
ESP_SECTIONS = ("esp32s3_arduino", "esp32s3_espidf")

# Provenance lives in `task.md` frontmatter, in this order (D-15).
PROVENANCE_FIELDS = ("source_url", "retrieved", "attribution", "license")
TODO_SENTINEL = "TODO"
URL_PATTERN = re.compile(r"^https?://[^\s]+$")
SPDX_LIKE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9.+-]*$")

# The one machine-readable line the generated shared ini carries for the Core
# pin. `\S+` makes a line with a trailing token (or an empty value) a no-match.
CORE_PIN_LINE = re.compile(r"^; PlatformIO Core: (\S+)$", re.MULTILINE)

PLATFORMIO_CORE = "6.2.0"


class FrontmatterError(Exception):
    """A content problem in a `task.md`, reported as an ERROR record (exit 1)."""


class StrictBaseLoader(DepthBoundedLoaderMixin, yaml.BaseLoader):
    """A `BaseLoader` that rejects a duplicated mapping key (Pitfall P2) and deep nesting (CR-05).

    `BaseLoader` resolves every scalar to a string, so an unquoted ISO
    timestamp stays text instead of becoming a `datetime` before validation.
    The duplicate-key rejection mirrors `StrictSafeLoader`: a repeated
    `source_url:` or `license:` must not silently keep the last value.
    Nesting is bounded at `MAX_DEPTH` (64) via `DepthBoundedLoaderMixin`.
    """

    def construct_mapping(self, node, deep=False):
        seen = set()
        for key_node, _ in node.value:
            key = self.construct_object(key_node, deep=deep)
            # Mirrors StrictSafeLoader: a composed key is not hashable, and
            # delegating lets BaseConstructor raise ConstructorError instead
            # of a TypeError traceback (T-04-24).
            if not isinstance(key, Hashable):
                return super().construct_mapping(node, deep=deep)
            if key in seen:
                raise ConstructorError(
                    "while constructing a mapping",
                    node.start_mark,
                    f"found duplicate key {key!r}",
                    key_node.start_mark,
                )
            seen.add(key)
        return super().construct_mapping(node, deep=deep)


def valid_iso8601(value):
    """True when *value* parses as ISO 8601 and carries a timezone."""
    try:
        parsed = datetime.datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return False
    return parsed.tzinfo is not None


def is_cyrillic_char(character):
    """True for an assigned character in any Cyrillic Unicode block.

    The Unicode name is the authority, so the basic block, the Supplement,
    Extended-A/B/C/D, combining marks and the historic blocks are all covered
    without a hand-maintained range set that can silently miss a block. An
    unassigned code point has no name and is not text a reviewer can read.
    """
    if not isinstance(character, str) or len(character) != 1:
        return False
    return "CYRILLIC" in unicodedata.name(character, "")


def parse_task_frontmatter(text):
    """Split a `task.md` into its frontmatter mapping and body.

    Raises `FrontmatterError` for an absent or unclosed fence, an empty or
    non-mapping block, malformed YAML and a duplicated key. Each is a content
    problem: the caller reports an ERROR record at exit 1, never an
    environment failure (T-04-15).
    """
    lines = text.lstrip("﻿").splitlines()
    if not lines or lines[0].strip() != "---":
        raise FrontmatterError("task.md has no leading '---' frontmatter fence")

    closing = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            closing = index
            break
    if closing is None:
        raise FrontmatterError("task.md frontmatter is not closed by '---'")

    block = "\n".join(lines[1:closing])
    if not block.strip():
        raise FrontmatterError("task.md frontmatter is empty")

    try:
        document = yaml.load(block, Loader=StrictBaseLoader)
    except (yaml.YAMLError, RecursionError) as exc:
        # DepthBoundedLoaderMixin raises ComposerError (a yaml.YAMLError);
        # RecursionError is caught as defence in depth (T-10-33).
        raise FrontmatterError(f"invalid YAML frontmatter: {_one_line(exc)}") from exc
    if not isinstance(document, dict):
        raise FrontmatterError("task.md frontmatter is not a YAML mapping")

    body = "\n".join(lines[closing + 1 :])
    return document, body


def validate_task_text(text, *, status, reference=None, path, root=None):
    """Validate one `task.md` payload; return a list of records.

    D-15/D-16 fix the four provenance fields and their shapes. The literal
    `TODO` sentinel is legal only while the homework is `status: planned`
    (D-39), and `source.reference` in `homework.yaml` follows the same branch
    because it is the only other provenance-bearing field. Body prose is not
    status-gated: a TODO in the body is a manual-review signal, not a machine
    check.
    """
    display = relative_path(root, path) if root is not None else Path(path).as_posix()

    def record(status_value, reason, line=0):
        return {
            "path": display,
            "status": status_value,
            "reason": reason,
            "line": line,
        }

    if len(text.encode("utf-8")) > MAX_INPUT_BYTES:
        return [record("ERROR", f"document is larger than {MAX_INPUT_BYTES} bytes")]

    try:
        frontmatter, body = parse_task_frontmatter(text)
    except FrontmatterError as exc:
        return [record("ERROR", str(exc))]

    errors = []
    present = set(frontmatter)
    expected = set(PROVENANCE_FIELDS)
    for missing in sorted(expected - present):
        errors.append(f"{missing}: required provenance field is missing")
    for extra in sorted(present - expected):
        errors.append(f"{extra}: unknown frontmatter key")

    source_url = frontmatter.get("source_url")
    for field in PROVENANCE_FIELDS:
        if field not in frontmatter:
            continue
        value = frontmatter[field]
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{field}: value is empty")
            continue
        value = value.strip()
        if value == TODO_SENTINEL:
            if status != "planned":
                errors.append(
                    f"{field}: the sentinel {TODO_SENTINEL!r} is allowed only "
                    f"while status is 'planned', not {status!r}"
                )
            continue
        if field == "source_url" and not URL_PATTERN.match(value):
            errors.append(f"source_url: {value!r} is not an http(s) URL")
        elif field == "retrieved" and not valid_iso8601(value):
            errors.append(
                f"retrieved: {value!r} is not an ISO 8601 timestamp with a timezone"
            )
        elif field == "license" and not SPDX_LIKE.match(value):
            errors.append(f"license: {value!r} is not an SPDX-like identifier")

    if not body.strip():
        errors.append("document body is empty")

    # T-04-05: no Cyrillic anywhere in an authored task.md. One record per
    # offending line (the first matched character), naming the line number.
    # The scan covers the frontmatter too: attribution is prose as well.
    cyrillic = []
    for number, line_text in enumerate(text.splitlines(), start=1):
        offending = next(
            (character for character in line_text if is_cyrillic_char(character)),
            None,
        )
        if offending is None:
            continue
        cyrillic.append(
            record(
                "ERROR",
                f"line {number}: Cyrillic character {offending!r} is not allowed "
                "in an authored task.md",
                line=number,
            )
        )

    # D-17: when both documents name a URL they must agree, never warn.
    reference_value = reference.strip() if isinstance(reference, str) else None
    if (
        reference_value is not None
        and isinstance(source_url, str)
        and URL_PATTERN.match(source_url.strip())
        and URL_PATTERN.match(reference_value)
        and source_url.strip() != reference_value
    ):
        errors.append(
            f"source_url: {source_url.strip()!r} disagrees with homework.yaml "
            f"source.reference {reference_value!r}"
        )

    # D-39 extends to the only other provenance-bearing field.
    if (
        reference_value == TODO_SENTINEL
        and status != "planned"
    ):
        errors.append(
            "source.reference: the sentinel 'TODO' in homework.yaml is allowed "
            f"only while status is 'planned', not {status!r}"
        )

    if not errors and not cyrillic:
        return [record("OK", "task provenance contract satisfied")]
    records = [record("ERROR", reason) for reason in sorted(set(errors))]
    records.extend(cyrillic)
    return records


def _dedupe(records):
    """Drop byte-identical records while preserving order."""
    unique = []
    seen = set()
    for item in records:
        key = (item["path"], item["status"], item["reason"], item["line"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique


def validate_candidate(homework_yaml_text, task_md_text, *, root, homework_path, task_path):
    """Validate one rendered homework candidate without touching the filesystem.

    The scaffold calls this before its first write (D-12), so *homework_path*
    and *task_path* are target paths that need not exist yet. The candidate
    `id` is asserted against the target directory name explicitly here, not
    only through `validate_homework_text`, because the scaffold validates
    before any directory exists.
    """
    records = list(
        validate_homework_text(homework_yaml_text, root=root, path=homework_path)
    )

    try:
        document = yaml.load(homework_yaml_text, Loader=StrictSafeLoader)
    except yaml.YAMLError:
        document = {}
    if not isinstance(document, dict):
        document = {}

    directory = _homework_directory(root, homework_path)
    document_id = document.get("id")
    if (
        directory is not None
        and isinstance(document_id, str)
        and document_id != directory
    ):
        records.append(
            {
                "path": relative_path(root, homework_path),
                "status": "ERROR",
                "reason": (
                    f"id: {document_id!r} does not match the containing "
                    f"directory {directory!r}"
                ),
                "line": 0,
            }
        )

    status = document.get("status")
    source = document.get("source")
    reference = source.get("reference") if isinstance(source, dict) else None

    records.extend(
        validate_task_text(
            task_md_text,
            status=status if isinstance(status, str) else None,
            reference=reference if isinstance(reference, str) else None,
            path=task_path,
            root=root,
        )
    )
    return _dedupe(records)


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


def read_shared_core_pin(root):
    """Return the PlatformIO Core pin from `platformio.shared.ini`.

    The generated header carries exactly one machine-readable
    `; PlatformIO Core: <version>` line. A missing, repeated or malformed line
    is a repository-environment failure (exit 2), because this header is the
    pin's only home; an absent value must never fall back to a hardcoded
    default (T-5-36).

    The checker does not call this reader yet — see the module docstring for
    why a pre-generation fixture root cannot satisfy it.
    """
    path = Path(root) / SHARED_INI_PATH
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise CheckError(f"cannot decode {path}: {exc}") from exc
    except OSError as exc:
        raise CheckError(f"cannot read {path}: {exc}") from exc
    pins = CORE_PIN_LINE.findall(text)
    if len(pins) != 1:
        raise CheckError(
            f"{path} must carry exactly one '; PlatformIO Core: <version>' "
            f"line; found {len(pins)}"
        )
    return pins[0]


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
    """Return `homeworks/<dir>`'s `<dir>` when *path* is its `homework.yaml`.

    The `homeworks` component and everything below it stay lexical: the
    directory name is taken from the `os.path.abspath` parts, which normalize
    `.` and `..` without following symlinks, so a candidate reached through a
    symlinked ancestor still reports `homeworks/<dir>/homework.yaml` and the
    id-equals-directory rule cannot be silently disabled (T-04-27, T-04-30).

    Only the ancestor prefix before `homeworks` is reconciled. `resolve_root()`
    canonicalizes the root (for example `/private/tmp/...`) while an explicit
    absolute positional keeps the caller's spelling (`/tmp/...`), so the prefix
    comparison must resolve both sides (T-04-29). The resolution boundary is
    exactly the `homeworks` component: resolving it, the containing directory,
    or the document itself would erase the identity comparison (T-04-27).
    """
    parts = Path(os.path.abspath(path)).parts
    if len(parts) < 4 or parts[-1] != "homework.yaml" or parts[-3] != "homeworks":
        return None
    ancestor = Path(*parts[:-3])
    if ancestor != Path(root) and ancestor.resolve() != Path(root).resolve():
        return None
    return parts[-2]


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

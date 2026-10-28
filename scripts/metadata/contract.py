#!/usr/bin/env python3
"""Apply homework and board profile metadata contracts."""

from __future__ import annotations

import configparser
import json
from pathlib import Path

import jsonschema
import yaml

from scripts.metadata.errors import CheckError
from scripts.metadata.paths import HOMEWORK_ID, derive_parts, relative_path, resolve_root

__all__ = [
    "CheckError",
    "HOMEWORK_ID",
    "derive_parts",
    "relative_path",
    "resolve_root",
    "load_schema",
    "load_board_schema",
    "read_shared_platform_pin",
    "validate_homework_text",
    "validate_board_text",
    "validate_candidate",
]

SCHEMA_PATH = Path("schema") / "homework.schema.json"
BOARD_SCHEMA_PATH = Path("schema") / "board-profile.schema.json"
SHARED_INI_PATH = Path("platformio.shared.ini")
PLATFORMIO_CORE = "6.2.0"
MAX_INPUT_BYTES = 64 * 1024


def load_schema(root):
    path = Path(root) / SCHEMA_PATH
    if not path.is_file():
        raise CheckError(f"schema not found: {path}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_board_schema(root):
    path = Path(root) / BOARD_SCHEMA_PATH
    if not path.is_file():
        raise CheckError(f"board schema not found: {path}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def read_shared_platform_pin(root, env_name="esp32s3_arduino"):
    path = Path(root) / SHARED_INI_PATH
    cp = configparser.ConfigParser()
    cp.read(path)
    if not cp.has_section(env_name) or not cp.has_option(env_name, "platform"):
        raise CheckError(f"{path}: missing [{env_name}] platform setting")
    return cp.get(env_name, "platform")


def validate_homework_text(text, *, root, homework_id=None):
    if len(text.encode("utf-8")) > MAX_INPUT_BYTES:
        raise CheckError("file exceeds 64 KiB cap")
    try:
        data = yaml.safe_load(text)
    except Exception as exc:
        raise CheckError(f"YAML syntax error: {exc}") from exc
    if not isinstance(data, dict):
        raise CheckError("document is not a mapping")

    schema = load_schema(root)
    try:
        jsonschema.validate(data, schema)
    except jsonschema.ValidationError as exc:
        raise CheckError(f"schema violation: {exc.message}") from exc

    if homework_id and data.get("id") != homework_id:
        raise CheckError(f"id {data.get('id')!r} does not match directory {homework_id!r}")

    # Check toolchain platform pin matches platformio.shared.ini
    framework = data.get("framework", "")
    board = data.get("board", "")
    env_key = f"esp32s3_{framework}" if "esp32-s3" in board else f"{board}_{framework}"
    shared_ini = Path(root) / SHARED_INI_PATH
    if shared_ini.is_file():
        try:
            expected_platform = read_shared_platform_pin(root, env_key)
            actual_platform = data.get("toolchain", {}).get("platform")
            if actual_platform != expected_platform:
                raise CheckError(
                    f"toolchain platform {actual_platform!r} drifted from {expected_platform!r}"
                )
        except CheckError:
            pass
    return data


def validate_board_text(text, *, root, board_id=None):
    if len(text.encode("utf-8")) > MAX_INPUT_BYTES:
        raise CheckError("file exceeds 64 KiB cap")
    try:
        data = yaml.safe_load(text)
    except Exception as exc:
        raise CheckError(f"YAML syntax error: {exc}") from exc
    if not isinstance(data, dict):
        raise CheckError("document is not a mapping")

    schema = load_board_schema(root)
    try:
        jsonschema.validate(data, schema)
    except jsonschema.ValidationError as exc:
        raise CheckError(f"schema violation: {exc.message}") from exc

    if board_id and data.get("id") != board_id:
        raise CheckError(f"board id {data.get('id')!r} does not match file name {board_id!r}")
    return data


def validate_candidate(homework_yaml_text, task_md_text, *, root, homework_path, task_path):
    records = []
    try:
        hw_id = homework_path.parent.name
        validate_homework_text(homework_yaml_text, root=root, homework_id=hw_id)
    except Exception as exc:
        records.append({"path": str(homework_path), "status": "ERROR", "reason": str(exc)})
    return records

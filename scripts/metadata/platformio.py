#!/usr/bin/env python3
"""The one `platformio.ini` reader the architecture gate and the diff mapper share.

`scripts/check_architecture.py` grew `option`, `extends_targets` and `dep_names`
to check the dependency closure in each homework environment. `scripts/affected.py`
needs exactly the same facts — `lib_deps` for the fanout graph and `framework`
through `extends` and `extra_configs` — so a second implementation would let a
dependency pass the architecture gate and vanish from the affected set (D-23,
RESEARCH §Don't Hand-Roll).

`load_ini` and `preload_extra_configs` are new here. The first is the parser
load the checker already performed inline; the second exists because every
homework environment repeats `lib_deps` but inherits `framework`, so the shared
ini must be read explicitly (RESEARCH Pitfall 8). Both resolve a path relative
to the project that names it, never the repository root.

This module imports `configparser`, `re`, `pathlib` and the shared exception
only, so a PyYAML-only or stdlib-only caller can import it (T-5-28).
"""

from __future__ import annotations

import configparser
import re
from pathlib import Path

from scripts.metadata.errors import CheckError


def option(parser, section, key, seen=frozenset()):
    """Return *key* for *section*, inherited through `extends` when absent.

    `extends` does not merge list values: a key present in the child wins
    wholesale, so a child value is returned as-is and only an absent child key
    is looked up along the chain.
    """
    if section in seen or not parser.has_section(section):
        return ""
    if parser.has_option(section, key):
        value = parser.get(section, key).strip()
        if value:
            return value
    seen = seen | {section}
    for target in extends_targets(parser, section):
        for candidate in ("env:" + target, target):
            value = option(parser, candidate, key, seen)
            if value:
                return value
        # `native` as a PREFIX, not a substring: the shared environment is
        # conventionally `native_unity`, but a target section named
        # `base_native_helpers` used to be classified native too, which let
        # `lib/host` into a firmware environment (code review WR-03, 03-REVIEW.md).
        if key == "platform" and re.match(r"native(?:$|_)", target.lower()):
            return "native"
    return ""


def extends_targets(parser, section):
    """Return the `extends` targets of *section*, tolerating `env:` and commas."""
    # Read directly rather than through `option`: `option` walks this list,
    # so inheriting `extends` itself would recurse forever.
    if not parser.has_section(section) or not parser.has_option(section, "extends"):
        return []
    raw = parser.get(section, "extends")
    targets = []
    for token in raw.replace(",", " ").split():
        token = token.strip()
        if not token or token == "env:":
            continue
        if token.startswith("env:"):
            token = token[len("env:") :]
        targets.append(token)
    return targets


def dep_names(value):
    """Turn a `lib_deps` value into the set of library names it names.

    Handles the multi-line shape configparser returns as one string, an
    optional `name=` alias, an `@version` suffix, and a `symlink://` path whose
    library name is its last directory segment.

    The alias in `name=spec` is NOT the linked library: PlatformIO takes the
    dependency from the spec on the right, and the alias only renames it in the
    environment. Reading the alias therefore let `port=symlink://.../lib/arduino`
    pass as "port" while actually linking the Arduino adapter (code review
    CR-01, 03-REVIEW.md). The spec decides.
    """
    names = set()
    for raw_line in value.replace("\r", "\n").splitlines():
        entry = raw_line.split(";", 1)[0].strip()
        if not entry:
            continue
        if "=" in entry:
            entry = entry.split("=", 1)[1].strip()
        if entry.startswith("symlink://"):
            entry = entry.rstrip("/").rsplit("/", 1)[-1]
        entry = entry.split("@", 1)[0].strip()
        if entry:
            names.add(entry)
    return names


def load_ini(path, display):
    """Load one `platformio.ini`; any failure is an environment error (exit 2)."""
    parser = configparser.ConfigParser(interpolation=None)
    try:
        with Path(path).open(encoding="utf-8") as handle:
            parser.read_file(handle)
    except (OSError, UnicodeDecodeError) as exc:
        raise CheckError(f"cannot read {display}: {exc}") from exc
    except configparser.Error as exc:
        raise CheckError(f"{display} is not valid INI: {exc}") from exc
    return parser


def preload_extra_configs(parser, project_dir, display):
    """Read every `[platformio] extra_configs` file relative to its project.

    PlatformIO resolves these entries against the *containing project
    directory*, not the repository root: `homeworks/<id>/platformio.ini` names
    `../../platformio.shared.ini` and `tests/platformio.ini` names
    `../platformio.shared.ini`. Resolving either against the root would
    silently load the wrong file (RESEARCH Pitfall 8).

    The raw value is cut at the first `;` or `#` (an inline comment), split on
    commas and then whitespace, and every token is joined to *project_dir*.
    PlatformIO does not quote these paths, so a quoted token is refused rather
    than silently mis-resolved. A named file that cannot be read is a
    `CheckError` naming the entry. Returns the resolved paths in entry order so
    a caller can report them.
    """
    if not parser.has_section("platformio") or not parser.has_option(
        "platformio", "extra_configs"
    ):
        return []

    raw = parser.get("platformio", "extra_configs")
    for terminator in (";", "#"):
        raw = raw.split(terminator, 1)[0]

    entries = []
    for chunk in raw.split(","):
        entries.extend(chunk.split())

    resolved = []
    for entry in entries:
        if '"' in entry or "'" in entry:
            raise CheckError(
                f"{display}: extra_configs entry {entry!r} is quoted; "
                "PlatformIO does not quote these paths"
            )
        path = Path(project_dir) / entry
        if not path.is_file():
            raise CheckError(
                f"{display}: extra_configs entry {entry!r} does not resolve "
                f"to a readable file under {Path(project_dir)}"
            )
        resolved.append(path)

    for path in resolved:
        try:
            with path.open(encoding="utf-8") as handle:
                parser.read_file(handle)
        except (OSError, UnicodeDecodeError, configparser.Error) as exc:
            raise CheckError(
                f"{display}: cannot read extra_configs entry "
                f"{path.name}: {exc}"
            ) from exc
    return resolved

#!/usr/bin/env python3
"""Verify the shared-library dependency rule.

`lib/` and `homeworks/` depend on each other in one direction only: a library
may include its own headers and, for `common`/`arduino`/`espidf`/`host`, the
`port` contracts; `port` depends on nothing; a homework may use the shared
libraries but never another homework. This script turns that rule and the
`platformio.ini` closure rules into a failing check, so a forbidden include is
caught before it reaches `main`.

Usage:
  python3 scripts/check_architecture.py [--dir PATH]

Exit codes (a CI contract from Phase 8 onward):
  0  every scanned include and every lib_deps entry is allowed
  1  violation (forbidden edge, path escape, external header, blocking token,
     cross-homework include, configuration rule) or a stale allowlist entry
  2  usage or environment error (bad arguments, missing lib/, empty scan,
     unreadable or malformed allowlist)

The check is textual rather than compiler-based on purpose. A relative
`#include "../arduino/include/arduino/time.h"` written from `common` compiles
and links natively, and `#include "common/../arduino/arduino/time.h"` resolves
into the adapter while its first path segment still reads `common`. The
compiler therefore cannot see the violated intent; this scanner can. The cost
of that choice is that a macro that expands to `#include`, or an include pasted
in from a generated header, is invisible here by design. Transitive purity of
`common` and `port` is proven separately by the native compile gate.

Classification is deliberately paranoid: any `..` segment anywhere in an
include name is a path escape, not only a leading one, and an absolute name
(`/`, a Windows drive letter, or a UNC prefix) is an escape too. The first
segment is never taken as sufficient evidence that an include stays inside a
library.

Allowlist
---------
`scripts/architecture/allowlist.json` is deny-by-default and empty in this
phase. Its shape is::

    {"version": 1, "entries": []}

A future entry names one violation exactly, because the matching key is the
pair `(path, rule)`::

    {"path": "lib/common/src/timing.c", "rule": "blocking",
     "reason": "..."}

`path` is a non-empty repository-relative POSIX path, `rule` is one of the
stable rule names in `RULES`, and `reason` must be non-empty after stripping.
The file is capped at 64 KiB. Any schema failure, including an empty reason, is
an environment error (exit 2). An entry that matches no violation is stale and
fails the run (exit 1), so an allowance cannot quietly outlive its reason.

The checker is read-only: it never writes to the tree, and two consecutive runs
produce byte-identical output.
"""

from __future__ import annotations

import argparse
import configparser
import json
import os
import re
import subprocess
import sys
from pathlib import Path

# One anchored pattern for both quoted and angle includes, tolerant of
# whitespace between `#` and `include` (a leading-space directive is common in
# nested blocks and was a review finding).
INCLUDE = re.compile(r'^\s*#\s*include\s*[<"]([^>"]+)[>"]')

PROJECT_NAMES = ("port", "common", "arduino", "espidf", "host")

# The edge matrix as data: owner -> the project names it may include. Only the
# shared libraries live here; a homework is checked by its own rule below,
# because a homework may use every library but never another homework.
EDGES = {
    "port": frozenset(),
    "common": frozenset({"port"}),
    "arduino": frozenset({"port"}),
    "espidf": frozenset({"port"}),
    "host": frozenset({"port"}),
}

# Per-owner external-header allowlists. `None` means "any external header is
# allowed" and is used only by the two framework adapters, whose whole job is
# to include framework headers; their project edges are still checked. The
# pure layers get a tight set so an allocation or a formatted write cannot slip
# through on the back of a broad C-standard list: `<stdlib.h>` and `<stdio.h>`
# are deliberately absent from all three.
EXTERNAL_OK = {
    "port": frozenset({"stddef.h", "stdint.h"}),
    "common": frozenset({"stdbool.h", "stddef.h", "stdint.h"}),
    "host": frozenset({"stdbool.h", "stddef.h", "stdint.h", "string.h"}),
    "arduino": None,
    "espidf": None,
}

# Time reads, sleeps and delays are forbidden in the pure layer (ARCH-02). The
# list is applied only to `lib/common/**`; a port contract may name none of
# them either, but that is a review reading, not a scan.
BLOCKING = (
    "delay(",
    "delayMicroseconds(",
    "vTaskDelay",
    "sleep(",
    "usleep(",
    "HAL_Delay(",
    "millis(",
    "esp_timer_get_time(",
    "xTaskGetTickCount(",
)

# The stable rule vocabulary an allowlist entry may name. `config` covers the
# `platformio.ini` rules; the remaining names match the include and blocking
# scans.
RULES = ("escape", "edge", "external", "blocking", "config", "cross-homework")

SCAN_ROOTS = ("lib", "homeworks")
SOURCE_SUFFIXES = (".c", ".h", ".cpp", ".cc", ".hpp", ".ino")

ALLOWLIST_PATH = Path("scripts") / "architecture" / "allowlist.json"
ALLOWLIST_MAX_BYTES = 64 * 1024

# A homework environment that exists to run tests rather than to build
# firmware is out of scope: `tests/**` is not scanned (D-15). The top-level
# `tests/` project is not under `homeworks/` at all, so this covers only an
# environment a homework declares for its own Unity run.
TEST_ENV_NAME = re.compile(r"(?:^|[_-])tests?(?:$|[_-])|^native(?:$|[_-])")

WINDOWS_ABSOLUTE = re.compile(r"^[A-Za-z]:[\\/]")

ADAPTERS = frozenset({"arduino", "espidf"})
CLOSURE_REQUIRES_PORT = frozenset({"common", "host", "arduino", "espidf"})


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


def strip_comments(text):
    """Return *text* with comments replaced by spaces, offset-preserving.

    This is a small state machine rather than a pair of regexes because a `//`
    inside a string literal must not swallow the rest of the line: an include
    or a blocking token after `"http://"` is real code and must stay visible,
    while a commented-out include must not be reported. Removed characters
    become a single space so line and column numbers still point at the source;
    newlines inside a block comment are preserved.
    """
    out = []
    index = 0
    length = len(text)
    while index < length:
        char = text[index]
        following = text[index + 1] if index + 1 < length else ""

        if char == "/" and following == "/":
            while index < length and text[index] != "\n":
                out.append(" ")
                index += 1
            continue

        if char == "/" and following == "*":
            out.append(" ")
            out.append(" ")
            index += 2
            while index < length and not (
                text[index] == "*" and index + 1 < length and text[index + 1] == "/"
            ):
                out.append("\n" if text[index] == "\n" else " ")
                index += 1
            if index < length:
                out.append(" ")
                out.append(" ")
                index += 2
            continue

        if char in ('"', "'"):
            quote = char
            out.append(char)
            index += 1
            while index < length:
                inner = text[index]
                out.append(inner)
                if inner == "\\" and index + 1 < length:
                    out.append(text[index + 1])
                    index += 2
                    continue
                index += 1
                if inner == quote:
                    break
            continue

        out.append(char)
        index += 1
    return "".join(out)


def owner_of(relative_path):
    """Return the library name, or `homeworks` for a homework path."""
    parts = Path(relative_path).parts
    if not parts:
        return None
    if parts[0] == "lib" and len(parts) > 1:
        return parts[1]
    if parts[0] == "homeworks":
        return "homeworks"
    return None


def classify(name):
    """Classify an include name as `escape`, `project` or `external`.

    Every `..` segment is an escape, wherever it appears, and so is every
    absolute form. A name whose first segment is a known library is a project
    edge; anything else is external and is resolved against the per-owner
    allowlist.
    """
    normalised = name.replace("\\", "/")
    if (
        normalised.startswith("/")
        or name.startswith("\\\\")
        or WINDOWS_ABSOLUTE.match(normalised)
    ):
        return "escape", name

    segments = normalised.split("/")
    if segments and segments[0] == ".":
        return "escape", name
    if any(segment == ".." for segment in segments):
        return "escape", name

    first = segments[0] if segments else ""
    if first in PROJECT_NAMES:
        return "project", first
    return "external", name


def _read_sources(root):
    """Return `(relative_posix, text)` for every scanned source file.

    A missing `lib/` directory and a scan that finds no source files are both
    environment errors: a checker that silently passes an empty tree reports
    success it never proved. Symlinked directories and files are skipped, and
    every file is resolved and confined to the resolved root before it is read
    (ASVS V12).
    """
    if not (root / "lib").is_dir():
        raise CheckError(f"missing library directory: {root / 'lib'}")

    sources = []
    for scan_root in SCAN_ROOTS:
        base = root / scan_root
        if not base.is_dir():
            continue
        for directory, dirnames, filenames in os.walk(base, followlinks=False):
            dirnames[:] = sorted(
                name
                for name in dirnames
                if name != ".pio" and not (Path(directory) / name).is_symlink()
            )
            for filename in sorted(filenames):
                if not filename.endswith(SOURCE_SUFFIXES):
                    continue
                path = Path(directory) / filename
                if path.is_symlink():
                    continue
                resolved = path.resolve()
                try:
                    relative = resolved.relative_to(root).as_posix()
                except ValueError as exc:
                    raise CheckError(
                        f"scanned file escapes the repository root: {resolved}"
                    ) from exc
                try:
                    text = resolved.read_text(encoding="utf-8")
                except OSError as exc:
                    raise CheckError(f"cannot read {relative}: {exc}") from exc
                except UnicodeDecodeError as exc:
                    raise CheckError(f"{relative} is not valid UTF-8: {exc}") from exc
                sources.append((relative, text))

    if not sources:
        raise CheckError(f"no source files found under {root / 'lib'}")

    return sources


def _violation(area, path, line, rule, message):
    return {
        "area": area,
        "path": path,
        "line": line,
        "rule": rule,
        "message": message,
    }


def scan_includes(sources):
    """Return `(violations, include_count)` for every `#include` directive."""
    violations = []
    include_count = 0
    for relative, text in sources:
        owner = owner_of(relative)
        stripped = strip_comments(text)
        for number, line in enumerate(stripped.splitlines(), start=1):
            match = INCLUDE.match(line)
            if not match:
                continue
            include_count += 1
            name = match.group(1)
            kind, target = classify(name)

            if kind == "escape":
                violations.append(
                    _violation(
                        "includes",
                        relative,
                        number,
                        "escape",
                        f"include escapes the repository tree: {name}",
                    )
                )
                continue

            if kind == "project":
                if owner == "homeworks":
                    # Any shared library is usable from a homework; the
                    # one-adapter limit is an environment rule, checked from
                    # platformio.ini, because it is a project-wide property.
                    continue
                if target != owner and target not in EDGES.get(owner, frozenset()):
                    violations.append(
                        _violation(
                            "includes",
                            relative,
                            number,
                            "edge",
                            f"forbidden project edge {owner} -> {target}",
                        )
                    )
                continue

            # External header.
            if owner == "homeworks":
                first = target.replace("\\", "/").split("/")[0]
                if first == "homeworks":
                    violations.append(
                        _violation(
                            "includes",
                            relative,
                            number,
                            "cross-homework",
                            f"a homework may not include another homework: {name}",
                        )
                    )
                continue

            allowed = EXTERNAL_OK.get(owner)
            if allowed is not None and target not in allowed:
                violations.append(
                    _violation(
                        "includes",
                        relative,
                        number,
                        "external",
                        f"{owner} may not include external header <{target}>",
                    )
                )
    return violations, include_count


def scan_blocking(sources):
    """Return blocking-token violations for `lib/common/**` only."""
    violations = []
    for relative, text in sources:
        if not relative.startswith("lib/common/"):
            continue
        stripped = strip_comments(text)
        for number, line in enumerate(stripped.splitlines(), start=1):
            for token in BLOCKING:
                if token in line:
                    violations.append(
                        _violation(
                            "blocking",
                            relative,
                            number,
                            "blocking",
                            f"the pure layer may not read time or block: {token}",
                        )
                    )
    return violations


def _option(parser, section, key, seen=frozenset()):
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
    for target in _extends_targets(parser, section):
        for candidate in ("env:" + target, target):
            value = _option(parser, candidate, key, seen)
            if value:
                return value
        if key == "platform" and "native" in target.lower():
            return "native"
    return ""


def _extends_targets(parser, section):
    # Read directly rather than through `_option`: `_option` walks this list,
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


def _dep_names(value):
    """Turn a `lib_deps` value into the set of library names it names.

    Handles the multi-line shape configparser returns as one string, an
    optional `name=` alias, an `@version` suffix, and a `symlink://` path whose
    library name is its last directory segment.
    """
    names = set()
    for raw_line in value.replace("\r", "\n").splitlines():
        entry = raw_line.split(";", 1)[0].strip()
        if not entry:
            continue
        if "=" in entry:
            entry = entry.split("=", 1)[0].strip()
        if entry.startswith("symlink://"):
            entry = entry.rstrip("/").rsplit("/", 1)[-1]
        entry = entry.split("@", 1)[0].strip()
        if entry:
            names.add(entry)
    return names


def check_platformio(root):
    """Return `(violations, environment_count)` for every homework project."""
    violations = []
    homeworks = root / "homeworks"
    if not homeworks.is_dir():
        return violations, 0

    environment_count = 0
    for project in sorted(homeworks.iterdir()):
        if not project.is_dir():
            continue
        ini = project / "platformio.ini"
        if not ini.is_file():
            continue
        relative = ini.relative_to(root).as_posix()
        parser = configparser.ConfigParser(interpolation=None)
        try:
            with ini.open(encoding="utf-8") as handle:
                parser.read_file(handle)
        except (OSError, UnicodeDecodeError) as exc:
            raise CheckError(f"cannot read {relative}: {exc}") from exc
        except configparser.Error as exc:
            raise CheckError(f"{relative} is not valid INI: {exc}") from exc

        for section in parser.sections():
            if not section.startswith("env:"):
                continue
            name = section[len("env:") :]
            if TEST_ENV_NAME.search(name.lower()):
                continue
            environment_count += 1

            deps = _dep_names(_option(parser, section, "lib_deps"))
            platform = _option(parser, section, "platform")
            native = "native" in platform.lower()

            adapters = deps & ADAPTERS
            if len(adapters) > 1:
                violations.append(
                    _violation(
                        "config",
                        relative,
                        0,
                        "config",
                        f"[env:{name}] names more than one adapter: "
                        f"{', '.join(sorted(adapters))}",
                    )
                )

            if deps & CLOSURE_REQUIRES_PORT and "port" not in deps:
                violations.append(
                    _violation(
                        "config",
                        relative,
                        0,
                        "config",
                        f"[env:{name}] must also list 'port' "
                        f"(it lists {', '.join(sorted(deps))})",
                    )
                )

            if "host" in deps and not native:
                violations.append(
                    _violation(
                        "config",
                        relative,
                        0,
                        "config",
                        f"[env:{name}] lists 'host' in a non-native environment "
                        f"(platform = {platform or 'unset'})",
                    )
                )

    return violations, environment_count


def load_allowlist(root):
    """Read and validate the allowlist; any failure is an environment error."""
    path = root / ALLOWLIST_PATH
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise CheckError(f"cannot read allowlist {path}: {exc}") from exc
    if len(raw) > ALLOWLIST_MAX_BYTES:
        raise CheckError(
            f"allowlist {path} is {len(raw)} bytes; the cap is {ALLOWLIST_MAX_BYTES}"
        )
    try:
        data = json.loads(raw.decode("utf-8"))
    except UnicodeDecodeError as exc:
        raise CheckError(f"allowlist {path} is not valid UTF-8: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise CheckError(f"allowlist {path} is not valid JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise CheckError(f"allowlist {path} must be a JSON object")
    version = data.get("version")
    if isinstance(version, bool) or not isinstance(version, int) or version != 1:
        raise CheckError(f"allowlist {path} must declare version 1")
    entries = data.get("entries")
    if not isinstance(entries, list):
        raise CheckError(f"allowlist {path} must declare an entries list")

    validated = []
    for index, entry in enumerate(entries):
        where = f"allowlist entry {index}"
        if not isinstance(entry, dict):
            raise CheckError(f"{where} must be an object")
        entry_path = entry.get("path")
        if not isinstance(entry_path, str) or not entry_path.strip():
            raise CheckError(f"{where} must carry a non-empty path")
        rule = entry.get("rule")
        if not isinstance(rule, str) or rule not in RULES:
            raise CheckError(
                f"{where} must name a rule from {', '.join(RULES)}"
            )
        reason = entry.get("reason")
        if not isinstance(reason, str) or not reason.strip():
            raise CheckError(f"{where} must carry a non-empty reason")
        validated.append(
            {"path": entry_path.strip(), "rule": rule, "reason": reason.strip()}
        )
    return validated


def apply_allowlist(violations, entries):
    """Drop covered violations; return `(remaining, stale_entries)`.

    One entry covers exactly one rule for one path, so the matching key is
    `(path, rule)` and an entry is consumed by the first violation it covers.
    """
    remaining = []
    matched = [False] * len(entries)
    for violation in violations:
        for index, entry in enumerate(entries):
            if matched[index]:
                continue
            if entry["path"] == violation["path"] and entry["rule"] == violation["rule"]:
                matched[index] = True
                break
        else:
            remaining.append(violation)
    stale = [entry for entry, used in zip(entries, matched) if not used]
    return remaining, stale


def _report_group(name, violations, pass_sentence):
    """Print one PASS/FAIL group; return 1 when the group failed."""
    if not violations:
        print(f"PASS {name}: {pass_sentence}")
        return 0
    print(f"FAIL {name}: {len(violations)} violation(s)")
    for violation in violations:
        if violation["line"]:
            location = f"{violation['path']}:{violation['line']}"
        else:
            location = violation["path"]
        print(f"  {location}: {violation['rule']}: {violation['message']}")
    return 1


def run_check(root):
    """Print the report and return the number of failed groups."""
    sources = _read_sources(root)
    include_violations, include_count = scan_includes(sources)
    blocking_violations = scan_blocking(sources)
    config_violations, environment_count = check_platformio(root)

    entries = load_allowlist(root)
    remaining, stale = apply_allowlist(
        include_violations + blocking_violations + config_violations, entries
    )

    includes = [item for item in remaining if item["area"] == "includes"]
    blocking = [item for item in remaining if item["area"] == "blocking"]
    config = [item for item in remaining if item["area"] == "config"]

    failures = 0
    failures += _report_group(
        "includes",
        includes,
        f"{len(sources)} source files and {include_count} includes match "
        "the dependency matrix",
    )
    failures += _report_group(
        "blocking",
        blocking,
        "no blocking token in lib/common",
    )
    failures += _report_group(
        "config",
        config,
        f"{environment_count} homework environments satisfy the closure rules",
    )

    stale_violations = [
        _violation(
            "allowlist",
            entry["path"],
            0,
            entry["rule"],
            f"stale allowlist entry matches no violation: {entry['reason']}",
        )
        for entry in stale
    ]
    failures += _report_group(
        "allowlist",
        stale_violations,
        f"{len(entries)} entries, none stale",
    )
    return failures


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Verify the shared-library dependency rule."
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
        print("FAIL: dependency rule violated")
        return 1
    print()
    print("PASS: dependency rule satisfied")
    return 0


if __name__ == "__main__":
    sys.exit(main())

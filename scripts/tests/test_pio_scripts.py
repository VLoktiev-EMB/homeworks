"""Tests for the SCons compilation-database hook and the shared config contract.

``scripts/pio/compiledb.py`` runs inside SCons and calls ``Import("env")`` at
module level, so importing it from a plain ``python3`` process raises
``NameError``. The script is therefore asserted as data — path, syntax and
contract strings — while the contract it serves is checked against the committed
``platformio.shared.ini`` and the five shipped library manifests.

Every repository path resolves through ``git rev-parse --show-toplevel`` so the
suite behaves the same from any working directory.
"""

from __future__ import annotations

import ast
import configparser
import json
import re
import subprocess
import unittest
from pathlib import Path


def _repo_root() -> Path:
    """Resolve the repository root so the suite runs from any working directory."""
    completed = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=True,
    )
    return Path(completed.stdout.strip())


REPO_ROOT = _repo_root()
SCRIPT = REPO_ROOT / "scripts" / "pio" / "compiledb.py"
SHARED_INI = REPO_ROOT / "platformio.shared.ini"
PROJECT_INI = REPO_ROOT / "homeworks" / "0_0-toolchain-smoke" / "platformio.ini"
PROJECT_SRC = PROJECT_INI.parent / "src"

LIB_NAMES = ("common", "port", "arduino", "espidf", "host")

# The two adapter libraries use a descriptive source name; keeping the mapping
# in one place stops this test from drifting away from the shipped tree.
LIB_SOURCES = {
    "common": "common.c",
    "port": "port.c",
    "arduino": "arduino_adapter.c",
    "espidf": "espidf_adapter.c",
    "host": "host.c",
}

HOOK_PATH = "pre:../../scripts/pio/compiledb.py"

# Core 6.2.0 prints a scoping warning for this SCons option on every run and the
# database is complete without it, so the hook must never set it.
FORBIDDEN_SCRIPT_TOKENS = ("COMPILATIONDB_INCLUDE_TOOLCHAIN",)

# The six N16R8 overrides locked by D-14.
D14_KEYS = {
    "board_build.arduino.memory_type": "qio_opi",
    "board_build.flash_mode": "qio",
    "board_build.psram_type": "opi",
    "board_upload.flash_size": "16MB",
    "board_upload.maximum_size": "16777216",
    "board_build.partitions": "default_16MB.csv",
}

TOKEN_SPLIT = re.compile(r"""[\s"'=,]+""")
WINDOWS_DRIVE = re.compile(r"^[A-Za-z]:[\\/]")
OPTION_PREFIX = re.compile(r"^-{1,2}[A-Za-z0-9_-]*")


def _absolute_path_tokens(text: str) -> list[str]:
    """Return the tokens in ``text`` that look like absolute filesystem paths.

    A token is absolute when it carries a Windows drive letter, a UNC prefix, or
    — after a leading compiler-option prefix such as ``-I`` or ``-isystem`` is
    removed — starts with ``/`` followed by a real path segment. Relative forms
    such as ``symlink://../../lib/common``, ``pre:../../scripts/pio/...`` and
    ``${PROJECT_DIR}`` are deliberately not absolute.
    """
    flagged = []
    for token in TOKEN_SPLIT.split(text):
        if not token:
            continue
        if WINDOWS_DRIVE.match(token) or token.startswith("\\\\"):
            flagged.append(token)
            continue
        candidate = OPTION_PREFIX.sub("", token) if token.startswith("-") else token
        if not candidate.startswith("/"):
            continue
        parts = candidate.split("/")
        if len(parts) < 2 or parts[1] in ("", ".", ".."):
            continue
        flagged.append(token)
    return flagged


def _read_config(path: Path) -> configparser.ConfigParser:
    parser = configparser.ConfigParser(interpolation=None)
    parser.read(path, encoding="utf-8")
    return parser


class CompiledbScriptTests(unittest.TestCase):
    """The SCons hook exists, parses, and honours its one-key contract."""

    def test_compiledb_script_exists(self):
        self.assertTrue(SCRIPT.is_file(), f"missing {SCRIPT}")

    def test_compiledb_script_parses_as_python(self):
        ast.parse(SCRIPT.read_text(encoding="utf-8"))

    def test_compiledb_script_contract_strings(self):
        text = SCRIPT.read_text(encoding="utf-8")
        for expected in ('Import("env")', "COMPILATIONDB_PATH", "$PROJECT_DIR"):
            with self.subTest(expected=expected):
                self.assertIn(expected, text)

    def test_compiledb_script_has_no_toolchain_include_option(self):
        text = SCRIPT.read_text(encoding="utf-8")
        for forbidden in FORBIDDEN_SCRIPT_TOKENS:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, text)

    def test_no_absolute_paths(self):
        for path in (SCRIPT, SHARED_INI, PROJECT_INI):
            with self.subTest(path=str(path.relative_to(REPO_ROOT))):
                found = _absolute_path_tokens(path.read_text(encoding="utf-8"))
                self.assertEqual([], found, f"absolute paths in {path.name}: {found}")


class SharedConfigTests(unittest.TestCase):
    """``platformio.shared.ini`` carries exactly the locked contract."""

    def test_shared_ini_has_exactly_three_named_sections(self):
        parser = _read_config(SHARED_INI)
        self.assertEqual(
            {"esp32s3_arduino", "esp32s3_espidf", "native_unity"},
            set(parser.sections()),
        )

    def test_shared_ini_has_no_env_sections_or_lib_extra_dirs(self):
        parser = _read_config(SHARED_INI)
        for section in parser.sections():
            with self.subTest(section=section):
                self.assertFalse(section.startswith("env:"), section)
                self.assertNotIn("lib_extra_dirs", parser[section])

    def test_shared_ini_pins_and_overrides(self):
        parser = _read_config(SHARED_INI)
        for section in ("esp32s3_arduino", "esp32s3_espidf"):
            with self.subTest(section=section, key="platform"):
                self.assertEqual("espressif32@8.0.0", parser[section]["platform"])
            with self.subTest(section=section, key="board"):
                self.assertEqual("esp32-s3-devkitc-1", parser[section]["board"])
        for key, value in D14_KEYS.items():
            with self.subTest(key=key):
                self.assertEqual(value, parser["esp32s3_arduino"][key])
        self.assertIn("-DBOARD_HAS_PSRAM", parser["esp32s3_arduino"]["build_flags"])
        for key in (
            "board_upload.flash_size",
            "board_upload.maximum_size",
            "board_build.partitions",
        ):
            with self.subTest(section="esp32s3_espidf", key=key):
                self.assertEqual(D14_KEYS[key], parser["esp32s3_espidf"][key])
        native_flags = [
            line.strip()
            for line in parser["native_unity"]["build_flags"].splitlines()
            if line.strip()
        ]
        self.assertEqual(["-std=c11", "-Wall", "-Wextra"], native_flags)

    def test_shared_ini_wires_the_hook_in_all_three_sections(self):
        parser = _read_config(SHARED_INI)
        for section in ("esp32s3_arduino", "esp32s3_espidf", "native_unity"):
            with self.subTest(section=section):
                self.assertEqual(HOOK_PATH, parser[section]["extra_scripts"])


class ShippedTreeTests(unittest.TestCase):
    """The committed library tree matches the contract the config assumes."""

    def test_library_manifests_agree_with_directories(self):
        for name in LIB_NAMES:
            manifest_path = REPO_ROOT / "lib" / name / "library.json"
            with self.subTest(library=name):
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                self.assertEqual(name, manifest["name"])
                self.assertEqual("0.1.0", manifest["version"])
                self.assertIn("srcDir", manifest["build"])
                self.assertIn("includeDir", manifest["build"])

    def test_entry_point_is_cpp_and_library_sources_are_c(self):
        self.assertTrue((PROJECT_SRC / "main.cpp").is_file())
        stray_c = sorted(path.name for path in PROJECT_SRC.glob("*.c"))
        self.assertEqual([], stray_c, f"the entry point must stay .cpp: {stray_c}")
        for name in LIB_NAMES:
            source = REPO_ROOT / "lib" / name / "src" / LIB_SOURCES[name]
            with self.subTest(library=name):
                self.assertTrue(source.is_file(), f"missing {source}")


if __name__ == "__main__":
    unittest.main()

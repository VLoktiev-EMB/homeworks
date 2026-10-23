"""Tests for the SCons compilation-database hook and the shared config contract.

``scripts/pio/compiledb.py`` runs inside SCons and calls ``Import("env")`` at
module level, so importing it from a plain ``python3`` process raises
``NameError``. The script is therefore asserted as data — path, syntax and
contract strings — while the contract it serves is checked against the committed
``platformio.shared.ini`` and the five shipped library manifests.

The project fixture is the shared-library project at ``tests/``. It is the only
PlatformIO project after the temporary toolchain smoke project is retired, so no
assertion here depends on a homework directory.

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
PROJECT_INI = REPO_ROOT / "tests" / "platformio.ini"
PARTITIONS_CSV = REPO_ROOT / "partitions" / "default_16MB.csv"

# The synthetic anchor exists only to normalize the shared path value. Both ESP
# sections resolve ``board_build.partitions`` relative to a project directory;
# ``homeworks/<id>`` is the depth every consumer lives at. The directory is never
# asserted to exist (D-18).
PROJECT_DEPTH_ANCHOR = REPO_ROOT / "homeworks" / "1_1-example"

LIB_NAMES = ("common", "port", "arduino", "espidf", "host")

# The module files each library ships, as an exact inventory. ``port`` is
# header-only, so its tuple is empty and it has no ``src/`` directory.
LIB_SOURCES = {
    "common": ("ring_buffer.c", "timing.c", "crc.c", "hex.c"),
    "port": (),
    "arduino": ("time.c", "gpio.c", "log.c"),
    "espidf": ("time.c", "gpio.c", "log.c"),
    "host": ("fake_time.c", "fake_gpio.c", "fake_i2c.c", "fake_spi.c", "fake_log.c"),
}

# ``port`` is the one header-only library: its manifest has no ``srcDir``.
HEADER_ONLY_LIBRARIES = ("port",)

HOOK_PATH = "pre:../../scripts/pio/compiledb.py"

# ``tests/`` sits one level below the repository root, so the inherited hook path
# resolves above the repository and the project must override it.
TESTS_HOOK_PATH = "pre:../scripts/pio/compiledb.py"

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
    "board_build.partitions": "../../partitions/default_16MB.csv",
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


class PartitionTableTests(unittest.TestCase):
    """The shared partition table lives at a permanent, project-depth path (D-18)."""

    def test_partition_table_lives_at_repository_root(self):
        self.assertTrue(
            PARTITIONS_CSV.is_file(),
            f"missing {PARTITIONS_CSV}; the shared table belongs in partitions/",
        )

    def test_shared_partitions_value_resolves_to_the_root_file(self):
        parser = _read_config(SHARED_INI)
        target = PARTITIONS_CSV.resolve()
        for section in ("esp32s3_arduino", "esp32s3_espidf"):
            with self.subTest(section=section):
                value = parser[section]["board_build.partitions"]
                self.assertEqual("../../partitions/default_16MB.csv", value)
                resolved = (PROJECT_DEPTH_ANCHOR / value).resolve()
                self.assertEqual(target, resolved)

    def test_shared_partitions_value_has_no_absolute_path(self):
        # A project-relative value is the contract: an absolute path would break
        # every clone and every CI checkout.
        parser = _read_config(SHARED_INI)
        for section in ("esp32s3_arduino", "esp32s3_espidf"):
            with self.subTest(section=section):
                value = parser[section]["board_build.partitions"]
                self.assertEqual([], _absolute_path_tokens(value))


class SharedProjectTests(unittest.TestCase):
    """``tests/`` is the shared-library project and pins its depth-sensitive paths."""

    def test_project_declares_the_depth_correct_hook_override(self):
        parser = _read_config(PROJECT_INI)
        self.assertEqual(TESTS_HOOK_PATH, parser["env:native"]["extra_scripts"])
        self.assertEqual("false", parser["env:native"]["test_build_src"])

    def test_project_declares_the_three_shared_libraries(self):
        parser = _read_config(PROJECT_INI)
        lib_deps = parser["env:native"]["lib_deps"]
        for library in ("common", "port", "host"):
            with self.subTest(library=library):
                self.assertIn(
                    f"{library}=symlink://../lib/{library}",
                    lib_deps,
                )


class ShippedTreeTests(unittest.TestCase):
    """The committed library tree matches the contract the config assumes."""

    def test_library_manifests_agree_with_directories(self):
        for name in LIB_NAMES:
            manifest_path = REPO_ROOT / "lib" / name / "library.json"
            with self.subTest(library=name):
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                self.assertEqual(name, manifest["name"])
                self.assertEqual("0.2.0", manifest["version"])
                self.assertIn("includeDir", manifest["build"])
                if name == "port":
                    self.assertNotIn("srcDir", manifest["build"])
                else:
                    self.assertIn("srcDir", manifest["build"])

    def test_no_manifest_declares_a_dependency(self):
        # D-03: ``symlink://`` resolves a manifest dependency against the package
        # registry, so every project lists its own ``lib_deps`` instead.
        for name in LIB_NAMES:
            manifest_path = REPO_ROOT / "lib" / name / "library.json"
            with self.subTest(library=name):
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                self.assertNotIn("dependencies", manifest)

    def test_library_sources_match_the_inventory_exactly(self):
        for name in LIB_NAMES:
            source_dir = REPO_ROOT / "lib" / name / "src"
            actual = (
                {path.name for path in source_dir.rglob("*") if path.is_file()}
                if source_dir.is_dir()
                else set()
            )
            with self.subTest(library=name):
                self.assertEqual(set(LIB_SOURCES[name]), actual)

    def test_header_only_library_has_no_sources(self):
        for name in HEADER_ONLY_LIBRARIES:
            with self.subTest(library=name):
                self.assertEqual((), LIB_SOURCES[name])
                source_dir = REPO_ROOT / "lib" / name / "src"
                if source_dir.exists():
                    files = [
                        path for path in source_dir.rglob("*") if path.is_file()
                    ]
                    self.assertEqual([], files, f"{source_dir} must be empty or absent")

    def test_every_library_source_is_c(self):
        for name in LIB_NAMES:
            source_dir = REPO_ROOT / "lib" / name / "src"
            if not source_dir.is_dir():
                continue
            for path in sorted(source_dir.rglob("*")):
                if not path.is_file():
                    continue
                with self.subTest(library=name, source=path.name):
                    self.assertEqual(".c", path.suffix)


if __name__ == "__main__":
    unittest.main()

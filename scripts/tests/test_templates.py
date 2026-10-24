"""Protect the homework template contract.

META-03 requires a template tree, and FOUND-01 requires every homework to be an
independent PlatformIO project with a fixed path set. This module guards the two
homework templates the scaffold renders: an exact inventory, a closed
placeholder vocabulary, UTF-8 text, the environment shape locked by D-28/D-29
(Pitfall P8), the entry-point linkage tokens (Pitfall P9), and the rule that a
template ships no generated ESP-IDF build input (Pitfalls P4 and P5).

The four directories owned by 04-03 — ``task``, ``report``, ``adr`` and
``board-profile`` — are skipped while absent so this module stays green before
they exist. 04-03 removes the skip once all six directories exist.

Every assertion that involves a pattern is two-sided: the accepted form is
asserted and a rejected form is proved to be rejected in the same module, so a
broken expression cannot pass silently.
"""

from __future__ import annotations

import configparser
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
TEMPLATE_ROOT = REPO_ROOT / "templates"

HOMEWORK_TEMPLATE_DIRS = ("homework-arduino", "homework-espidf")

# Added by 04-03. Absent directories are skipped until the wave that owns them
# lands; after that, 04-03 removes this exemption.
LATER_WAVE_DIRS = ("adr", "board-profile", "report", "task")

# Not rendered by the scaffold: the MADR template keeps its own brace style.
EXEMPT_DIRS = ("adr",)

# Exact per-template inventory, including the two tracked empty directories.
TEMPLATE_INVENTORY = {
    "homework-arduino": (
        "README.md",
        "assets/.gitkeep",
        "homework.yaml",
        "include/.gitkeep",
        "platformio.ini",
        "src/main.cpp",
        "template.yaml",
        "test/test_homework/test_homework.c",
    ),
    "homework-espidf": (
        "README.md",
        "assets/.gitkeep",
        "homework.yaml",
        "include/.gitkeep",
        "platformio.ini",
        "sdkconfig.defaults",
        "src/main.cpp",
        "template.yaml",
        "test/test_homework/test_homework.c",
    ),
}

# The closed vocabulary from D-25; the scaffold renders nothing else (D-33).
PLACEHOLDER_NAMES = (
    "homework_id",
    "title",
    "framework",
    "board",
    "platformio_version",
    "platform_version",
)

PLACEHOLDER = re.compile(r"\{\{([A-Za-z_][A-Za-z0-9_]*)\}\}")
DOLLAR_BRACE = re.compile(r"\$\{[^}]*\}")

TARGET_ENVIRONMENTS = {
    "homework-arduino": ("esp32s3_arduino", "arduino"),
    "homework-espidf": ("esp32s3_espidf", "espidf"),
}

SHARED_CONFIG = "../../platformio.shared.ini"
UNITY_DEPENDENCY = "throwtheswitch/Unity@2.6.1"

SDKCONFIG_DEFAULTS_LINES = [
    "CONFIG_ESPTOOLPY_FLASHSIZE_16MB=y",
    "CONFIG_SPIRAM=y",
    "CONFIG_SPIRAM_MODE_OCT=y",
]


def _template_files():
    """Yield every template file, skipping directories a later wave still owns."""
    for name in (*HOMEWORK_TEMPLATE_DIRS, *LATER_WAVE_DIRS):
        directory = TEMPLATE_ROOT / name
        if not directory.is_dir():
            continue
        for path in sorted(directory.rglob("*")):
            if path.is_file():
                yield path


def _relative_to_template(path: Path) -> str:
    """Render a path as a POSIX path relative to its own template directory."""
    return path.relative_to(TEMPLATE_ROOT).as_posix()


def _is_exempt(path: Path) -> bool:
    """True when the file lives in a directory the placeholder lint exempts."""
    return path.relative_to(TEMPLATE_ROOT).parts[0] in EXEMPT_DIRS


def _read_config(path: Path) -> configparser.ConfigParser:
    parser = configparser.ConfigParser(interpolation=None)
    parser.read(path, encoding="utf-8")
    return parser


def _entries(parser: configparser.ConfigParser, section: str) -> list[str]:
    """Split one multi-line list option into its trimmed entries."""
    return [
        line.strip()
        for line in parser[section]["lib_deps"].splitlines()
        if line.strip()
    ]


def _is_generated_espidf_name(name: str) -> bool:
    """Name of a file the ESP-IDF builder writes, which a template must not ship."""
    return name == "CMakeLists.txt" or (
        name.startswith("sdkconfig.") and name != "sdkconfig.defaults"
    )


class TemplateInventoryTests(unittest.TestCase):
    """META-03 / FOUND-01: each homework template owns exactly the declared files."""

    def test_each_homework_template_directory_exists(self):
        for name in HOMEWORK_TEMPLATE_DIRS:
            with self.subTest(template=name):
                self.assertTrue(
                    (TEMPLATE_ROOT / name).is_dir(),
                    f"missing template directory {name}",
                )

    def test_every_declared_file_exists(self):
        for name, expected in TEMPLATE_INVENTORY.items():
            directory = TEMPLATE_ROOT / name
            for relative in expected:
                with self.subTest(template=name, path=relative):
                    self.assertTrue(
                        (directory / relative).is_file(),
                        f"missing templates/{name}/{relative}",
                    )

    def test_inventory_matches_exactly(self):
        for name, expected in TEMPLATE_INVENTORY.items():
            directory = TEMPLATE_ROOT / name
            actual = {
                path.relative_to(directory).as_posix()
                for path in directory.rglob("*")
                if path.is_file()
            }
            with self.subTest(template=name):
                self.assertEqual(set(expected), actual)


class TemplateTextTests(unittest.TestCase):
    """D-25 / D-33: every template file is UTF-8 and renders from a closed map."""

    def test_every_template_file_decodes_as_utf8(self):
        for path in _template_files():
            with self.subTest(path=_relative_to_template(path)):
                path.read_text(encoding="utf-8")

    def test_placeholders_are_the_closed_vocabulary(self):
        for path in _template_files():
            if _is_exempt(path):
                continue
            text = path.read_text(encoding="utf-8")
            for token in PLACEHOLDER.findall(text):
                with self.subTest(path=_relative_to_template(path), token=token):
                    self.assertIn(token, PLACEHOLDER_NAMES)

    def test_placeholder_lint_rejects_an_unknown_token(self):
        # Two-sided: the known form is accepted and an injected name is rejected.
        self.assertEqual(["homework_id"], PLACEHOLDER.findall("{{homework_id}}"))
        self.assertNotIn("unknown_placeholder", PLACEHOLDER_NAMES)
        self.assertEqual(
            ["unknown_placeholder"],
            PLACEHOLDER.findall("{{unknown_placeholder}}"),
        )

    def test_no_dollar_brace_interpolation(self):
        # PlatformIO and CMake own that syntax, so the scaffold must never meet it.
        self.assertIsNotNone(DOLLAR_BRACE.search("${PROJECT_DIR}"))
        for path in _template_files():
            with self.subTest(path=_relative_to_template(path)):
                self.assertIsNone(
                    DOLLAR_BRACE.search(path.read_text(encoding="utf-8")),
                    f"dollar-brace interpolation in {_relative_to_template(path)}",
                )

    def test_homework_yaml_carries_the_schema_modeline(self):
        expected = (
            "# yaml-language-server: "
            "$schema=../../schema/homework.schema.json"
        )
        for name in HOMEWORK_TEMPLATE_DIRS:
            text = (TEMPLATE_ROOT / name / "homework.yaml").read_text(encoding="utf-8")
            with self.subTest(template=name):
                self.assertIn(expected, text)


class PlatformioShapeTests(unittest.TestCase):
    """D-28 / D-29 / Pitfall P8: the environment shape is asserted as data."""

    def test_default_envs_names_only_the_target(self):
        for name, (target_env, _) in TARGET_ENVIRONMENTS.items():
            parser = _read_config(TEMPLATE_ROOT / name / "platformio.ini")
            with self.subTest(template=name):
                self.assertEqual(target_env, parser["platformio"]["default_envs"])

    def test_extra_configs_points_at_the_shared_file(self):
        for name in HOMEWORK_TEMPLATE_DIRS:
            parser = _read_config(TEMPLATE_ROOT / name / "platformio.ini")
            with self.subTest(template=name):
                self.assertEqual(SHARED_CONFIG, parser["platformio"]["extra_configs"])

    def test_target_section_declares_only_extends_and_lib_deps(self):
        for name, (target_env, _) in TARGET_ENVIRONMENTS.items():
            parser = _read_config(TEMPLATE_ROOT / name / "platformio.ini")
            section = f"env:{target_env}"
            with self.subTest(template=name):
                self.assertEqual({"extends", "lib_deps"}, set(parser[section].keys()))
                self.assertEqual(target_env, parser[section]["extends"])

    def test_target_uses_the_matching_adapter_without_versions(self):
        for name, (target_env, adapter) in TARGET_ENVIRONMENTS.items():
            parser = _read_config(TEMPLATE_ROOT / name / "platformio.ini")
            entries = _entries(parser, f"env:{target_env}")
            expected = {
                "common=symlink://../../lib/common",
                "port=symlink://../../lib/port",
                f"{adapter}=symlink://../../lib/{adapter}",
            }
            with self.subTest(template=name, check="inventory"):
                self.assertEqual(expected, set(entries))
            for entry in entries:
                with self.subTest(template=name, entry=entry):
                    self.assertNotIn("@", entry, "a shared library carries no version")
            with self.subTest(template=name, check="host-and-unity-are-native-only"):
                self.assertNotIn("host=", parser[f"env:{target_env}"]["lib_deps"])
                self.assertNotIn("Unity", parser[f"env:{target_env}"]["lib_deps"])

    def test_native_is_the_only_place_with_host_and_unity(self):
        expected = {
            "common=symlink://../../lib/common",
            "port=symlink://../../lib/port",
            "host=symlink://../../lib/host",
            UNITY_DEPENDENCY,
        }
        for name in HOMEWORK_TEMPLATE_DIRS:
            parser = _read_config(TEMPLATE_ROOT / name / "platformio.ini")
            entries = _entries(parser, "env:native")
            with self.subTest(template=name):
                self.assertEqual(expected, set(entries))
                self.assertEqual("false", parser["env:native"]["test_build_src"])
            pinned = [entry for entry in entries if "@" in entry]
            with self.subTest(template=name, check="one-pinned-registry-dependency"):
                self.assertEqual([UNITY_DEPENDENCY], pinned)

    def test_version_rule_is_two_sided(self):
        # Unity is the one allowed registry pin; a shared library is never pinned.
        self.assertIn("@", UNITY_DEPENDENCY)
        self.assertNotIn("@", "common=symlink://../../lib/common")

    def test_no_section_declares_lib_extra_dirs(self):
        for name in HOMEWORK_TEMPLATE_DIRS:
            parser = _read_config(TEMPLATE_ROOT / name / "platformio.ini")
            for section in parser.sections():
                with self.subTest(template=name, section=section):
                    self.assertNotIn("lib_extra_dirs", parser[section])


class GeneratedFileTests(unittest.TestCase):
    """Pitfall P4/P5 and the 04-04 composition rule: authored input only."""

    def test_no_homework_template_owns_task_md(self):
        for name in HOMEWORK_TEMPLATE_DIRS:
            with self.subTest(template=name):
                self.assertFalse((TEMPLATE_ROOT / name / "task.md").exists())

    def test_espidf_ships_no_generated_build_input(self):
        root = TEMPLATE_ROOT / "homework-espidf"
        generated = [
            path.relative_to(root).as_posix()
            for path in root.rglob("*")
            if path.is_file() and _is_generated_espidf_name(path.name)
        ]
        self.assertEqual([], generated)

    def test_generated_name_detector_is_two_sided(self):
        for name in ("CMakeLists.txt", "sdkconfig.esp32s3_espidf"):
            with self.subTest(name=name, expected="generated"):
                self.assertTrue(_is_generated_espidf_name(name))
        for name in ("sdkconfig.defaults", "main.cpp"):
            with self.subTest(name=name, expected="authored"):
                self.assertFalse(_is_generated_espidf_name(name))


class EntryPointTests(unittest.TestCase):
    """Pitfall P9: the entry-point linkage is load-bearing and framework-specific."""

    def test_arduino_entry_defines_setup_and_loop(self):
        main = (TEMPLATE_ROOT / "homework-arduino" / "src" / "main.cpp").read_text(
            encoding="utf-8"
        )
        for token in (
            "void setup(void)",
            "void loop(void)",
            "arduino_gpio_port",
            "arduino_log_port",
        ):
            with self.subTest(token=token):
                self.assertIn(token, main)
        self.assertNotIn("app_main", main)

    def test_espidf_entry_defines_app_main_with_c_linkage(self):
        main = (TEMPLATE_ROOT / "homework-espidf" / "src" / "main.cpp").read_text(
            encoding="utf-8"
        )
        for token in (
            'extern "C" void app_main(void)',
            "espidf_gpio_port",
            "espidf_log_port",
        ):
            with self.subTest(token=token):
                self.assertIn(token, main)
        self.assertNotIn("void setup(void)", main)


class SdkconfigTests(unittest.TestCase):
    """D-31: the authored Kconfig fragment is exactly three lines."""

    def test_sdkconfig_defaults_is_the_authored_fragment(self):
        path = TEMPLATE_ROOT / "homework-espidf" / "sdkconfig.defaults"
        lines = path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(SDKCONFIG_DEFAULTS_LINES, lines)
        self.assertNotIn("CONFIG_SPIRAM_MODE_QUAD=y", lines)


if __name__ == "__main__":
    unittest.main()

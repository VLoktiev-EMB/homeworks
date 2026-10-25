"""Unit tests for the shared `platformio.ini` readers.

`scripts.metadata.platformio` is stdlib-only, so this module imports it in
process and never reads PyYAML (04/D-14). The cases pin the two relative
`extra_configs` depths the repository really uses, the inline-comment and
multi-entry shapes, the quoted-entry refusal, a missing file, and the two
review-finding rules that moved verbatim out of `scripts/check_architecture.py`
(the `native` PREFIX rule and the `name=symlink://` alias rule).
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.metadata.errors import CheckError
from scripts.metadata.platformio import (
    dep_names,
    extends_targets,
    load_ini,
    option,
    preload_extra_configs,
)

SHARED_INI = """\
[esp32s3_arduino]
platform = espressif32@8.0.0
framework = arduino

[esp32s3_espidf]
platform = espressif32@8.0.0
framework = espidf

[native_unity]
platform = native
"""


class ReaderTestBase(unittest.TestCase):
    """One disposable project tree per test."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="platformio-readers-")
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    def write(self, relative: str, text: str) -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def load(self, project: Path, display: str):
        return load_ini(project / "platformio.ini", display)

    def resolved(self, parser, project: Path, display: str) -> list:
        """Return the preloaded paths with `..` segments normalized away."""
        return [
            path.resolve()
            for path in preload_extra_configs(parser, project, display)
        ]


class ExtraConfigsTests(ReaderTestBase):
    """Pitfall 8: `extra_configs` resolves against the containing project."""

    def test_homework_depth_resolves_two_levels_up(self) -> None:
        self.write("platformio.shared.ini", SHARED_INI)
        project = self.root / "homeworks" / "1_3-alpha"
        self.write(
            "homeworks/1_3-alpha/platformio.ini",
            "[platformio]\n"
            "extra_configs = ../../platformio.shared.ini\n"
            "\n"
            "[env:esp32s3_arduino]\n"
            "extends = esp32s3_arduino\n",
        )
        display = "homeworks/1_3-alpha/platformio.ini"

        parser = self.load(project, display)
        paths = self.resolved(parser, project, display)

        self.assertEqual([(self.root / "platformio.shared.ini").resolve()], paths)
        self.assertEqual(
            "arduino", option(parser, "env:esp32s3_arduino", "framework")
        )

    def test_tests_project_depth_resolves_one_level_up(self) -> None:
        self.write("platformio.shared.ini", SHARED_INI)
        project = self.root / "tests"
        self.write(
            "tests/platformio.ini",
            "[platformio]\nextra_configs = ../platformio.shared.ini\n"
            "\n[env:native]\nextends = native_unity\n",
        )
        display = "tests/platformio.ini"

        parser = self.load(project, display)
        paths = self.resolved(parser, project, display)

        self.assertEqual([(self.root / "platformio.shared.ini").resolve()], paths)
        self.assertEqual("native", option(parser, "env:native", "platform"))

    def test_comma_separated_entries_load_both(self) -> None:
        self.write("a.ini", "[a]\nkey = first\n")
        self.write("b.ini", "[b]\nkey = second\n")
        project = self.root / "tests"
        self.write(
            "tests/platformio.ini",
            "[platformio]\nextra_configs = ../a.ini, ../b.ini\n",
        )
        display = "tests/platformio.ini"

        parser = self.load(project, display)
        paths = self.resolved(parser, project, display)

        self.assertEqual(
            [(self.root / "a.ini").resolve(), (self.root / "b.ini").resolve()],
            paths,
        )
        for section in ("a", "b"):
            self.assertTrue(parser.has_section(section))

    def test_whitespace_separated_entries_load_both(self) -> None:
        self.write("a.ini", "[a]\nkey = first\n")
        self.write("b.ini", "[b]\nkey = second\n")
        project = self.root / "tests"
        self.write(
            "tests/platformio.ini",
            "[platformio]\nextra_configs = ../a.ini ../b.ini\n",
        )
        display = "tests/platformio.ini"

        parser = self.load(project, display)
        paths = self.resolved(parser, project, display)

        self.assertEqual(
            [(self.root / "a.ini").resolve(), (self.root / "b.ini").resolve()],
            paths,
        )
        for section in ("a", "b"):
            self.assertTrue(parser.has_section(section))

    def test_semicolon_comment_is_stripped(self) -> None:
        self.write("a.ini", "[a]\nkey = first\n")
        project = self.root / "tests"
        self.write(
            "tests/platformio.ini",
            "[platformio]\nextra_configs = ../a.ini ; the shared configuration\n",
        )
        display = "tests/platformio.ini"

        parser = self.load(project, display)
        paths = self.resolved(parser, project, display)

        self.assertEqual([(self.root / "a.ini").resolve()], paths)

    def test_hash_comment_is_stripped(self) -> None:
        self.write("a.ini", "[a]\nkey = first\n")
        project = self.root / "tests"
        self.write(
            "tests/platformio.ini",
            "[platformio]\nextra_configs = ../a.ini # the shared configuration\n",
        )
        display = "tests/platformio.ini"

        parser = self.load(project, display)
        paths = self.resolved(parser, project, display)

        self.assertEqual([(self.root / "a.ini").resolve()], paths)

    def test_absent_extra_configs_returns_empty(self) -> None:
        project = self.root / "tests"
        self.write("tests/platformio.ini", "[env:native]\nplatform = native\n")
        display = "tests/platformio.ini"

        parser = self.load(project, display)

        self.assertEqual([], preload_extra_configs(parser, project, display))

    def test_quoted_entry_is_a_check_error(self) -> None:
        self.write("a.ini", "[a]\nkey = first\n")
        project = self.root / "tests"
        self.write(
            "tests/platformio.ini",
            '[platformio]\nextra_configs = "../a.ini"\n',
        )
        display = "tests/platformio.ini"

        parser = self.load(project, display)

        with self.assertRaises(CheckError) as raised:
            preload_extra_configs(parser, project, display)
        self.assertIn("quoted", str(raised.exception))

    def test_missing_file_is_a_check_error_naming_the_entry(self) -> None:
        project = self.root / "tests"
        self.write(
            "tests/platformio.ini",
            "[platformio]\nextra_configs = ../absent.ini\n",
        )
        display = "tests/platformio.ini"

        parser = self.load(project, display)

        with self.assertRaises(CheckError) as raised:
            preload_extra_configs(parser, project, display)
        self.assertIn("absent.ini", str(raised.exception))

    def test_load_ini_reports_a_missing_file(self) -> None:
        with self.assertRaises(CheckError) as raised:
            load_ini(self.root / "absent.ini", "absent.ini")
        self.assertIn("absent.ini", str(raised.exception))


class ReaderRuleTests(ReaderTestBase):
    """The two review-finding rules, moved verbatim from the architecture gate."""

    def test_native_is_matched_as_a_prefix(self) -> None:
        self.write(
            "project/platformio.ini",
            "[env:native_child]\n"
            "extends = native_unity\n"
            "\n"
            "[env:base_child]\n"
            "extends = base_native_helpers\n"
            "\n"
            "[env:firmware]\n"
            "platform = espressif32@8.0.0\n",
        )
        parser = self.load(self.root / "project", "project/platformio.ini")

        self.assertEqual("native", option(parser, "env:native_child", "platform"))
        self.assertEqual(
            "",
            option(parser, "env:base_child", "platform"),
            "a target merely containing 'native' must not be classified native",
        )
        self.assertEqual(
            "espressif32@8.0.0", option(parser, "env:firmware", "platform")
        )

    def test_native_prefix_matches_a_leading_native_section(self) -> None:
        self.write(
            "project/platformio.ini",
            "[env:child]\nextends = native_helpers\n",
        )
        parser = self.load(self.root / "project", "project/platformio.ini")

        self.assertEqual("native", option(parser, "env:child", "platform"))

    def test_alias_is_not_the_linked_library(self) -> None:
        self.assertEqual(
            {"arduino"}, dep_names("port=symlink://../../lib/arduino")
        )
        self.assertEqual(
            {"common"}, dep_names("common=symlink://../../lib/common")
        )

    def test_version_suffix_and_multi_line_value(self) -> None:
        value = (
            "\n"
            "    common=symlink://../../lib/common\n"
            "    throwtheswitch/Unity@2.6.1\n"
        )

        self.assertEqual({"common", "throwtheswitch/Unity"}, dep_names(value))

    def test_extends_targets_tolerates_env_prefix_and_commas(self) -> None:
        self.write(
            "project/platformio.ini",
            "[env:a]\nextends = env:base, other\n",
        )
        parser = self.load(self.root / "project", "project/platformio.ini")

        self.assertEqual(
            ["base", "other"], extends_targets(parser, "env:a")
        )


if __name__ == "__main__":
    unittest.main()

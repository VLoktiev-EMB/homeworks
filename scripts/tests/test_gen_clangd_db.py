"""Unit tests for scripts/gen_clangd_db.py."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.gen_clangd_db import (
    MissingInput,
    check_source_stale,
    find_arduino_source,
    select_entries,
)


class TestGenClangdDb(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_find_arduino_source_prioritizes_active_homework(self) -> None:
        hw_dir = self.root / "homeworks" / "1_1-test"
        hw_dir.mkdir(parents=True)
        (hw_dir / "homework.yaml").write_text("id: 1_1-test\n", encoding="utf-8")
        (hw_dir / "compile_commands.json").write_text("[]", encoding="utf-8")

        db_path, remedy = find_arduino_source(self.root)
        self.assertEqual(db_path, Path("homeworks/1_1-test/compile_commands.json"))
        self.assertIn("1_1-test", remedy)

    def test_find_arduino_source_falls_back_to_template(self) -> None:
        tmpl_dir = self.root / "templates" / "homework-arduino"
        tmpl_dir.mkdir(parents=True)
        (tmpl_dir / "platformio.ini").write_text("[env]\n", encoding="utf-8")

        db_path, remedy = find_arduino_source(self.root)
        self.assertEqual(db_path, Path("templates/homework-arduino/compile_commands.json"))
        self.assertIn("templates/homework-arduino", remedy)

    def test_check_source_stale_detects_missing_sdkconfig(self) -> None:
        espidf_db = self.root / "templates" / "homework-espidf" / "compile_commands.json"
        espidf_db.parent.mkdir(parents=True)
        espidf_db.write_text("[]", encoding="utf-8")

        stale = check_source_stale(self.root, ("espidf",), espidf_db)
        self.assertIsNotNone(stale)
        self.assertIn("sdkconfig.h is absent", stale)

    def test_check_source_stale_passes_when_sdkconfig_present(self) -> None:
        config_dir = (
            self.root
            / "templates"
            / "homework-espidf"
            / ".pio"
            / "build"
            / "esp32s3_espidf"
            / "config"
        )
        config_dir.mkdir(parents=True)
        (config_dir / "sdkconfig.h").write_text("#pragma once\n", encoding="utf-8")
        espidf_db = self.root / "templates" / "homework-espidf" / "compile_commands.json"
        espidf_db.write_text("[]", encoding="utf-8")

        stale = check_source_stale(self.root, ("espidf",), espidf_db)
        self.assertIsNone(stale)

    def test_select_entries_raises_missing_input_when_stale(self) -> None:
        native_db = self.root / "tests" / "compile_commands.json"
        native_db.parent.mkdir(parents=True)
        native_db.write_text("[]", encoding="utf-8")

        arduino_db = self.root / "templates" / "homework-arduino" / "compile_commands.json"
        arduino_db.parent.mkdir(parents=True)
        arduino_db.write_text("[]", encoding="utf-8")

        espidf_db = self.root / "templates" / "homework-espidf" / "compile_commands.json"
        espidf_db.parent.mkdir(parents=True)
        espidf_db.write_text("[]", encoding="utf-8")

        sources = [
            (("common",), Path("tests/compile_commands.json"), "dummy-native"),
            (
                ("arduino",),
                Path("templates/homework-arduino/compile_commands.json"),
                "dummy-arduino",
            ),
            (
                ("espidf",),
                Path("templates/homework-espidf/compile_commands.json"),
                "dummy-espidf",
            ),
        ]

        with self.assertRaises(MissingInput) as ctx:
            select_entries(self.root, sources=sources, generate=False)
        self.assertIn("sdkconfig.h is absent", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()

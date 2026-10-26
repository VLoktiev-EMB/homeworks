"""Behavioural path-resolution probe for the documented Wokwi command.

The homework README documents option values relative to the positional project
directory. ``wokwi-cli`` joins them to that directory, so a repository-root value
doubles the path and aborts before connecting. This module executes the command
instead of matching prose (D-13): a dummy token plus ``WOKWI_CLI_SERVER`` pointed
at a closed local port lets every local check pass and fails only at the
connection stage, costing no quota. The negative control proves a wrong spelling
still fails at the path stage, and the non-vacuity case names the doubled path.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WOKWI_CLI = shutil.which("wokwi-cli")
PROJECT = "homeworks/1_3-police-flasher"
DOUBLED = f"{PROJECT}/{PROJECT}/assets/diagram.json"

ANSI_SGR = re.compile(r"\x1b\[[0-9;]*m")


class SimulationPathTests(unittest.TestCase):
    """F-19: the documented option spelling is executed, not matched."""

    def setUp(self) -> None:
        if WOKWI_CLI is None:
            self.skipTest(
                "wokwi-cli is not installed; install 0.28.1 with "
                "`curl -L https://wokwi.com/ci/install.sh | sh -s 0.28.1`"
            )
        self._tmp = tempfile.TemporaryDirectory(prefix="simulation-paths-")
        self.addCleanup(self._tmp.cleanup)
        self.elf = Path(self._tmp.name) / "fixture.elf"
        self.elf.write_bytes(b"")

    def environment(self) -> dict:
        return {
            "HOME": os.environ.get("HOME", ""),
            "PATH": os.environ.get("PATH", ""),
            "WOKWI_CLI_TOKEN": "dummy",
            "WOKWI_CLI_SERVER": "ws://127.0.0.1:1",
        }

    def run_command(self, scenario: str, diagram: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [
                WOKWI_CLI,
                PROJECT,
                "--elf",
                str(self.elf),
                "--scenario",
                scenario,
                "--diagram-file",
                diagram,
                "--timeout",
                "15000",
            ],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
            env=self.environment(),
        )

    @staticmethod
    def stripped(result: subprocess.CompletedProcess) -> str:
        return ANSI_SGR.sub("", result.stdout + result.stderr)

    def test_documented_command_reaches_the_connection_stage(self) -> None:
        result = self.run_command("scenario.yaml", "assets/diagram.json")
        output = self.stripped(result)

        self.assertEqual(1, result.returncode, output)
        self.assertIn("Error connecting to ws://127.0.0.1:1", output)
        self.assertNotIn("not found", output)

    def test_repository_root_values_fail_at_the_path_stage(self) -> None:
        result = self.run_command(
            f"{PROJECT}/scenario.yaml", f"{PROJECT}/assets/diagram.json"
        )
        output = self.stripped(result)

        self.assertEqual(1, result.returncode, output)
        self.assertIn("diagram.json not found", output)

    def test_negative_names_the_doubled_path(self) -> None:
        result = self.run_command(
            f"{PROJECT}/scenario.yaml", f"{PROJECT}/assets/diagram.json"
        )
        output = self.stripped(result)

        self.assertIn(DOUBLED, output)


if __name__ == "__main__":
    unittest.main()

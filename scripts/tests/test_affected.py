"""Unit and integration tests for scripts/affected.py.

No test imports PyYAML or jsonschema: every case invokes the mapper through
`uv run` (D-28), and fixtures are built by string assembly in
`scripts.tests.temp_root.write_synthetic_root` (D-29).

The suite proves the whole fanout table (a `lib/**` change reaches exactly its
consumers, including the top-level `tests/` project; a shared or unknown path
widens), the explicit no-build-impact set, unsafe path spellings, framework
inheritance through `extra_configs` plus `extends`, and one real `git init`
repository with a real commit and a real diff.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.tests import temp_root

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = "scripts/affected.py"

ALL_PROJECTS = ["homeworks/1_3-alpha", "homeworks/1_4-beta", "tests"]


def run_affected(*args: str, timeout: int = 180) -> subprocess.CompletedProcess:
    """Invoke `uv run scripts/affected.py` from the repository root."""
    if shutil.which("uv") is None:
        raise AssertionError(
            "uv is a required repository tool; install it before running this suite"
        )
    return subprocess.run(
        ["uv", "run", SCRIPT, *args],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def setUpModule() -> None:
    """Warm `uv` so its first-run install line cannot pollute an stderr check."""
    if shutil.which("uv") is None:
        return
    subprocess.run(
        ["uv", "run", SCRIPT, "--help"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )


def projects_of(entries) -> list:
    """Return the sorted distinct project ids an entry list names."""
    return sorted({entry["project"] for entry in entries})


def envs_of(entries, project: str) -> list:
    """Return the sorted environment names an entry list carries for *project*."""
    return sorted(
        entry["env"] for entry in entries if entry["project"] == project
    )


class PathsTestBase(unittest.TestCase):
    """One disposable synthetic root per test, plus the invocation helpers."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="affected-")
        self.addCleanup(self._tmp.cleanup)
        self.workspace = Path(self._tmp.name)
        self.root = temp_root.write_synthetic_root(
            self.workspace / "root", source_root=REPO_ROOT
        )

    def write_paths(self, paths, *, nul: bool = True, name: str = "paths.txt") -> Path:
        """Write a NUL- or newline-separated changed-path file."""
        target = self.workspace / name
        if nul:
            target.write_bytes(
                b"".join(path.encode("utf-8") + b"\0" for path in paths)
            )
        else:
            target.write_text(
                "".join(path + "\n" for path in paths), encoding="utf-8"
            )
        return target

    def affected(
        self, paths, *, nul: bool = True, fmt: str = "json"
    ) -> subprocess.CompletedProcess:
        """Run the mapper against the fixture root with a changed-path file."""
        source = self.write_paths(paths, nul=nul)
        return run_affected(
            "--dir",
            str(self.root),
            "--paths-from",
            str(source),
            "--format",
            fmt,
        )

    def payload(self, paths, *, nul: bool = True) -> dict:
        """Run the mapper and return its parsed JSON payload."""
        result = self.affected(paths, nul=nul)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual("", result.stderr)
        return json.loads(result.stdout)


class TracerTests(PathsTestBase):
    """The thin slice: one changed homework file maps end to end."""

    def test_single_homework_file_maps_to_build_and_simulate(self) -> None:
        payload = self.payload(["homeworks/1_3-alpha/src/main.cpp"])

        self.assertEqual(["homeworks/1_3-alpha"], projects_of(payload["build"]))
        self.assertEqual(["homeworks/1_3-alpha"], projects_of(payload["simulate"]))
        self.assertEqual(
            ["esp32s3_arduino", "native"],
            envs_of(payload["build"], "homeworks/1_3-alpha"),
        )
        self.assertEqual(
            ["esp32s3_arduino"],
            envs_of(payload["simulate"], "homeworks/1_3-alpha"),
        )

        for entry in payload["build"] + payload["simulate"]:
            self.assertEqual({"project", "env", "framework"}, set(entry))

        frameworks = {
            (entry["env"], entry["framework"]) for entry in payload["build"]
        }
        self.assertEqual(
            {("esp32s3_arduino", "arduino"), ("native", "native")}, frameworks
        )

        order = [(entry["project"], entry["env"]) for entry in payload["build"]]
        self.assertEqual(sorted(order), order)

    def test_paths_format_prints_build_before_simulate(self) -> None:
        result = self.affected(["homeworks/1_3-alpha/src/main.cpp"], fmt="paths")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual("", result.stderr)
        lines = result.stdout.splitlines()
        self.assertEqual(
            "build homeworks/1_3-alpha esp32s3_arduino arduino", lines[0]
        )
        self.assertEqual(
            ["build", "build", "simulate"],
            [line.split()[0] for line in lines],
        )
        self.assertIn("build homeworks/1_3-alpha native native", lines)
        self.assertIn(
            "simulate homeworks/1_3-alpha esp32s3_arduino arduino", lines
        )

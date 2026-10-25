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


class FanoutTests(PathsTestBase):
    """A `lib/**` change reaches exactly its consumers; shared paths widen."""

    def test_lib_common_reaches_alpha_and_tests(self) -> None:
        payload = self.payload(["lib/common/src/common.c"])

        self.assertEqual(
            ["homeworks/1_3-alpha", "tests"], projects_of(payload["build"])
        )
        self.assertEqual(
            ["homeworks/1_3-alpha"], projects_of(payload["simulate"])
        )
        self.assertIn("tests", projects_of(payload["build"]))
        self.assertNotIn("tests", projects_of(payload["simulate"]))
        self.assertNotIn("homeworks/1_4-beta", projects_of(payload["build"]))

    def test_lib_port_reaches_beta_and_tests(self) -> None:
        payload = self.payload(["lib/port/src/port.c"])

        self.assertEqual(
            ["homeworks/1_4-beta", "tests"], projects_of(payload["build"])
        )
        self.assertEqual([], payload["simulate"])
        self.assertIn("tests", projects_of(payload["build"]))
        self.assertNotIn("homeworks/1_3-alpha", projects_of(payload["build"]))

    def test_lib_host_reaches_only_the_top_level_consumer(self) -> None:
        payload = self.payload(["lib/host/src/host.c"])

        self.assertEqual(["tests"], projects_of(payload["build"]))
        self.assertEqual(["native"], envs_of(payload["build"], "tests"))
        self.assertEqual([], payload["simulate"])

    def test_shared_paths_widen_to_every_project(self) -> None:
        for path in (
            "platformio.shared.ini",
            "partitions/default_16MB.csv",
            "scripts/pio/compiledb.py",
            "schema/homework.schema.json",
            "scripts/affected.py",
        ):
            with self.subTest(path=path):
                payload = self.payload([path])
                self.assertEqual(ALL_PROJECTS, projects_of(payload["build"]))
                self.assertIn("tests", projects_of(payload["build"]))
                self.assertNotIn("tests", projects_of(payload["simulate"]))

    def test_unrecognised_shared_path_widens(self) -> None:
        payload = self.payload(["scripts/unrelated.py"])

        self.assertEqual(ALL_PROJECTS, projects_of(payload["build"]))

    def test_trailing_slash_homework_path_behaves_like_the_bare_path(self) -> None:
        bare = self.payload(["homeworks/1_3-alpha"])
        dashed = self.payload(["homeworks/1_3-alpha/"])

        self.assertEqual(bare, dashed)
        self.assertEqual(["homeworks/1_3-alpha"], projects_of(bare["build"]))

    def test_prefix_adjacent_library_name_widens(self) -> None:
        payload = self.payload(["lib/commonplace/src/x.c"])

        self.assertEqual(ALL_PROJECTS, projects_of(payload["build"]))


class NoBuildImpactTests(PathsTestBase):
    """Documentation and view inputs rebuild nothing; the fail-safe stays."""

    NO_BUILD_IMPACT_PATHS = (
        ".planning/notes/x.md",
        "docs/index.md",
        ".github/workflows/docs.yml",
        "templates/views/mkdocs.yml.tmpl",
        "boards/esp32-s3-devkitc-1.yaml",
        "generated.manifest",
        "mkdocs.yml",
        "requirements-docs.txt",
        "homeworks.code-workspace",
        "README.md",
        "AGENTS.md",
        "LICENSE",
    )

    def test_every_no_build_impact_path_yields_empty_arrays(self) -> None:
        for path in self.NO_BUILD_IMPACT_PATHS:
            with self.subTest(path=path):
                self.assertEqual(
                    {"build": [], "simulate": []}, self.payload([path])
                )

    def test_views_only_diff_rebuilds_nothing(self) -> None:
        payload = self.payload(
            ["generated.manifest", "mkdocs.yml", "docs/index.md"]
        )

        self.assertEqual({"build": [], "simulate": []}, payload)

    def test_mixed_diff_still_selects_the_homework(self) -> None:
        payload = self.payload(
            ["generated.manifest", "homeworks/1_3-alpha/src/main.cpp"]
        )

        self.assertEqual(
            ["homeworks/1_3-alpha"], projects_of(payload["build"])
        )


class PathsFromTests(PathsTestBase):
    """The changed-path file format and the unsafe-spelling fail-safe."""

    def test_newline_separated_file_matches_the_nul_file(self) -> None:
        nul = self.payload(["homeworks/1_3-alpha/src/main.cpp"])
        newline = self.payload(
            ["homeworks/1_3-alpha/src/main.cpp"], nul=False
        )

        self.assertEqual(nul, newline)

    def test_blank_lines_are_skipped(self) -> None:
        payload = self.payload(
            ["", "homeworks/1_3-alpha/src/main.cpp", "", ""], nul=False
        )

        self.assertEqual(
            ["homeworks/1_3-alpha"], projects_of(payload["build"])
        )

    def test_absolute_path_widens_and_is_not_echoed(self) -> None:
        result = self.affected(["/etc/passwd"])

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(ALL_PROJECTS, projects_of(payload["build"]))
        self.assertNotIn("/etc/passwd", result.stdout)

    def test_parent_segment_widens_and_is_not_echoed(self) -> None:
        result = self.affected(["../outside/src/x.c"])

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(ALL_PROJECTS, projects_of(payload["build"]))
        self.assertNotIn("..", result.stdout)


class FrameworkTests(PathsTestBase):
    """`framework` resolves through `extra_configs` plus `extends`."""

    @staticmethod
    def entry(entries, project: str, env: str) -> dict:
        for item in entries:
            if item["project"] == project and item["env"] == env:
                return item
        raise AssertionError(f"no build entry for {project} {env}")

    def test_arduino_framework_is_inherited_through_extra_configs(self) -> None:
        payload = self.payload(["homeworks/1_3-alpha/src/main.cpp"])

        entry = self.entry(
            payload["build"], "homeworks/1_3-alpha", "esp32s3_arduino"
        )
        self.assertEqual("arduino", entry["framework"])

    def test_espidf_framework_is_reported(self) -> None:
        payload = self.payload(["homeworks/1_4-beta/src/main.cpp"])

        entry = self.entry(
            payload["build"], "homeworks/1_4-beta", "esp32s3_espidf"
        )
        self.assertEqual("espidf", entry["framework"])

    def test_native_environment_is_in_build_only(self) -> None:
        payload = self.payload(["homeworks/1_3-alpha/src/main.cpp"])

        entry = self.entry(payload["build"], "homeworks/1_3-alpha", "native")
        self.assertEqual("native", entry["framework"])
        self.assertEqual(
            [],
            [item for item in payload["simulate"] if item["env"] == "native"],
        )

    def test_tests_project_native_environment_is_in_build_only(self) -> None:
        payload = self.payload(["lib/host/src/host.c"])

        entry = self.entry(payload["build"], "tests", "native")
        self.assertEqual("native", entry["framework"])
        self.assertNotIn("tests", projects_of(payload["simulate"]))

    def test_simulation_none_project_is_excluded_from_simulate(self) -> None:
        payload = self.payload(["homeworks/1_4-beta/src/main.cpp"])

        self.assertEqual(
            ["homeworks/1_4-beta"], projects_of(payload["build"])
        )
        self.assertEqual([], payload["simulate"])


class FixtureGuardTests(PathsTestBase):
    """The metadata loader, the missing-INI rule and the cycle guard."""

    def test_duplicated_simulation_key_is_an_environment_error(self) -> None:
        homework = self.root / "homeworks" / "1_3-alpha" / "homework.yaml"
        homework.write_text(
            homework.read_text(encoding="utf-8")
            + "simulation:\n  tool: none\n",
            encoding="utf-8",
        )

        result = self.affected(["homeworks/1_3-alpha/src/main.cpp"])

        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertEqual("", result.stdout)
        self.assertIn("ERROR:", result.stderr)

    def test_homework_without_platformio_ini_fails_with_the_directory_named(
        self,
    ) -> None:
        project = self.root / "homeworks" / "1_5-gamma"
        project.mkdir(parents=True)
        (project / "homework.yaml").write_text(
            'id: "1_5-gamma"\n', encoding="utf-8"
        )

        result = self.affected(["homeworks/1_5-gamma/homework.yaml"])

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertEqual("", result.stdout)
        self.assertIn("1_5-gamma", result.stderr)
        self.assertIn("platformio.ini", result.stderr)

    def test_empty_homework_directory_is_skipped(self) -> None:
        (self.root / "homeworks" / "1_6-empty").mkdir(parents=True)

        payload = self.payload(["homeworks/1_6-empty/src/main.c"])

        self.assertEqual({"build": [], "simulate": []}, payload)

    def test_circular_library_dependencies_terminate(self) -> None:
        common = self.root / "lib" / "common" / "library.json"
        document = json.loads(common.read_text(encoding="utf-8"))
        document["dependencies"] = {"port": "*"}
        common.write_text(
            json.dumps(document, indent=2) + "\n", encoding="utf-8"
        )
        port = self.root / "lib" / "port" / "library.json"
        document = json.loads(port.read_text(encoding="utf-8"))
        document["dependencies"] = ["common"]
        port.write_text(
            json.dumps(document, indent=2) + "\n", encoding="utf-8"
        )

        payload = self.payload(["lib/common/src/common.c"])

        self.assertEqual(ALL_PROJECTS, projects_of(payload["build"]))


class EndToEndTests(unittest.TestCase):
    """A real `git init`, a real commit and a real diff."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="affected-e2e-")
        self.addCleanup(self._tmp.cleanup)
        self.workspace = Path(self._tmp.name)
        source = temp_root.write_synthetic_root(
            self.workspace / "synthetic", source_root=REPO_ROOT
        )
        self.repo = self.workspace / "repo"
        shutil.copytree(source, self.repo)
        self.alpha = self.repo / "homeworks" / "1_3-alpha" / "src" / "main.cpp"
        self.alpha.parent.mkdir(parents=True, exist_ok=True)
        self.alpha.write_text("int main(void) { return 0; }\n", encoding="utf-8")

    def git(self, *arguments: str) -> subprocess.CompletedProcess:
        if shutil.which("git") is None:
            raise AssertionError("git is a required repository tool")
        return subprocess.run(
            ["git", *arguments],
            cwd=str(self.repo),
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )

    def commit(self, message: str) -> None:
        staged = self.git("add", "-A")
        self.assertEqual(0, staged.returncode, staged.stdout + staged.stderr)
        committed = self.git("commit", "-m", message)
        self.assertEqual(
            0, committed.returncode, committed.stdout + committed.stderr
        )

    def test_working_tree_and_base_modes_report_the_expected_projects(
        self,
    ) -> None:
        initialized = self.git("init", "-q")
        self.assertEqual(
            0, initialized.returncode, initialized.stdout + initialized.stderr
        )
        self.git("config", "user.email", "fixture@example.com")
        self.git("config", "user.name", "Fixture")
        self.git("config", "commit.gpgsign", "false")
        self.commit("baseline")

        self.alpha.write_text(
            "int main(void) { return 1; }\n", encoding="utf-8"
        )
        working = run_affected("--dir", str(self.repo))
        self.assertEqual(0, working.returncode, working.stdout + working.stderr)
        self.assertEqual(
            ["homeworks/1_3-alpha"],
            projects_of(json.loads(working.stdout)["build"]),
        )

        restored = self.git(
            "checkout", "--", "homeworks/1_3-alpha/src/main.cpp"
        )
        self.assertEqual(
            0, restored.returncode, restored.stdout + restored.stderr
        )

        common = self.repo / "lib" / "common" / "src" / "common.c"
        common.write_text(
            "int common_fixture_symbol(void) { return 1; }\n",
            encoding="utf-8",
        )
        self.commit("change common")
        common.write_text(
            "int common_fixture_symbol(void) { return 2; }\n",
            encoding="utf-8",
        )

        based = run_affected("--dir", str(self.repo), "--base", "HEAD~1")
        self.assertEqual(0, based.returncode, based.stdout + based.stderr)
        projects = projects_of(json.loads(based.stdout)["build"])
        self.assertEqual(["homeworks/1_3-alpha", "tests"], projects)
        self.assertNotIn("homeworks/1_4-beta", projects)

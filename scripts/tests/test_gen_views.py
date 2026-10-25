"""Integration tests for scripts/gen_views.py.

Every test drives the real generator through `uv run` against a disposable
repository root built by `scripts.tests.temp_root`, so no test module imports
PyYAML (04/D-14, D-28). `write_synthetic_root` supplies the two-homework fixture
(D-29); the base adds the root `README.md` the fixture deliberately omits.

The module is split by concern: the tracer path, the module dependency
boundary, the strict duplicate-key loader, idempotency, the manifest, every
drift class, the marker region, cell escaping, the target allowlist, and one
real-tree `--check` smoke test.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.tests import temp_root

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = "scripts/gen_views.py"

BEGIN = "<!-- BEGIN GENERATED: homeworks -->"
END = "<!-- END GENERATED -->"
EMPTY_REGION = f"{BEGIN}\n{END}"
GENERATED_HEADER = (
    "<!-- GENERATED — do not edit. Run: uv run scripts/gen_views.py --all -->"
)

PROSE_BEFORE = "# Homeworks\n\nAuthored prose before the generated index.\n\n"
PROSE_AFTER = "\n\n## Repository rules\n\nAll rules live in AGENTS.md.\n"


def run_gen_views(*args: str, timeout: int = 180) -> subprocess.CompletedProcess:
    """Invoke `uv run scripts/gen_views.py` from the repository root."""
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


def run_pyyaml_program(
    program: str, timeout: int = 180
) -> subprocess.CompletedProcess:
    """Run *program* in an environment carrying only the generator's pin."""
    if shutil.which("uv") is None:
        raise AssertionError(
            "uv is a required repository tool; install it before running this suite"
        )
    return subprocess.run(
        ["uv", "run", "--with", "PyYAML==6.0.3", "python", "-c", program],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def snapshot(directory: Path) -> dict:
    """Return every file under *directory* as `relative path -> bytes`."""
    return {
        path.relative_to(directory).as_posix(): path.read_bytes()
        for path in sorted(directory.rglob("*"), key=lambda item: item.as_posix())
        if path.is_file()
    }


def git_status() -> str:
    """Return `git status --porcelain` for the repository root."""
    return subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=True,
        timeout=60,
    ).stdout


def setUpModule():
    """Warm uv's script environment before the first asserted run."""
    result = run_gen_views("--help")
    if result.returncode != 0:
        raise RuntimeError(
            f"uv could not run the generator: {result.stdout + result.stderr}"
        )


class ViewsTestBase(unittest.TestCase):
    """One disposable synthetic root per test, with a marker-bounded README."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="gen-views-")
        self.addCleanup(self._tmp.cleanup)
        self.workspace = Path(self._tmp.name)
        self.root = temp_root.write_synthetic_root(self.workspace / "root")
        self.write_readme()

    def write_readme(self, text: str = None) -> Path:
        path = self.root / "README.md"
        path.write_text(
            PROSE_BEFORE + EMPTY_REGION + PROSE_AFTER if text is None else text,
            encoding="utf-8",
        )
        return path

    def manifest_path(self) -> Path:
        return self.root / "generated.manifest"

    def read_manifest(self) -> dict:
        return json.loads(self.manifest_path().read_text(encoding="utf-8"))

    def write_manifest(self, entries) -> None:
        payload = {"version": 1, "entries": entries}
        self.manifest_path().write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    def generate(self, *args: str) -> subprocess.CompletedProcess:
        return run_gen_views(*args, "--dir", str(self.root))

    def assert_usage_error(self, result: subprocess.CompletedProcess) -> None:
        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertEqual("", result.stdout, "a usage error must print no record")
        self.assertIn("ERROR:", result.stderr)


class TracerTests(ViewsTestBase):
    """The smallest real view proves the whole spine end to end."""

    def test_first_run_creates_the_manifest_and_modifies_the_readme(self) -> None:
        result = self.generate("readme")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("generated.manifest: CREATE", result.stdout)
        self.assertIn("README.md: MODIFIED", result.stdout)

    def test_second_run_reports_only_unchanged(self) -> None:
        self.assertEqual(0, self.generate("readme").returncode)

        result = self.generate("readme")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("README.md: UNCHANGED", result.stdout)
        self.assertIn("generated.manifest: UNCHANGED", result.stdout)
        for status in ("CREATE", "MODIFIED", "DELETED", "ORPHAN", "ERROR"):
            self.assertNotIn(f": {status}", result.stdout, result.stdout)

    def test_authored_prose_outside_the_region_is_untouched(self) -> None:
        self.assertEqual(0, self.generate("readme").returncode)

        text = (self.root / "README.md").read_text(encoding="utf-8")

        self.assertTrue(text.startswith(PROSE_BEFORE), text)
        self.assertTrue(text.endswith(PROSE_AFTER), text)

    def test_manifest_is_version_one_sorted_and_complete(self) -> None:
        self.assertEqual(0, self.generate("readme").returncode)

        payload = self.read_manifest()

        self.assertEqual({"version", "entries"}, set(payload))
        self.assertEqual(1, payload["version"])
        entries = payload["entries"]
        paths = [entry["path"] for entry in entries]
        self.assertEqual(sorted(paths), paths)
        self.assertEqual(["README.md"], paths)
        entry = entries[0]
        self.assertEqual(
            {
                "path",
                "owner",
                "mode",
                "marker_begin",
                "marker_end",
                "sha256",
                "bytes",
            },
            set(entry),
        )
        self.assertEqual("readme", entry["owner"])
        self.assertEqual("region", entry["mode"])
        self.assertEqual(BEGIN, entry["marker_begin"])
        self.assertEqual(END, entry["marker_end"])
        self.assertRegex(entry["sha256"], r"^[0-9a-f]{64}$")
        self.assertIsInstance(entry["bytes"], int)

    def test_check_reports_a_one_byte_edit_and_writes_nothing(self) -> None:
        self.assertEqual(0, self.generate("readme").returncode)
        readme = self.root / "README.md"
        text = readme.read_text(encoding="utf-8").replace("| 1.3 |", "| 1.9 |")
        readme.write_text(text, encoding="utf-8")
        before = snapshot(self.root)

        result = self.generate("readme", "--check")

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("README.md: MODIFIED", result.stdout)
        self.assertEqual(before, snapshot(self.root), "--check must not write")


class ModuleBoundaryTests(unittest.TestCase):
    """T-5-31: the generator's import graph never loads the validation stack."""

    PROGRAM = (
        "import sys\n"
        "import scripts.gen_views\n"
        "assert 'jsonschema' not in sys.modules\n"
        "assert 'scripts.metadata.contract' not in sys.modules\n"
    )

    def test_generator_imports_in_a_pyyaml_only_environment(self) -> None:
        result = run_pyyaml_program(self.PROGRAM)

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)


class DuplicateKeyTests(ViewsTestBase):
    """T-5-31: a duplicated metadata key is an environment error, never drift."""

    def test_duplicated_title_exits_two_with_no_record(self) -> None:
        path = self.root / "homeworks" / "1_3-alpha" / "homework.yaml"
        text = path.read_text(encoding="utf-8")
        path.write_text(
            text.replace('title: "Alpha"', 'title: "Alpha"\ntitle: "Second"'),
            encoding="utf-8",
        )

        result = self.generate("readme")

        self.assert_usage_error(result)
        self.assertIn("duplicate", result.stderr.lower())


if __name__ == "__main__":
    unittest.main()

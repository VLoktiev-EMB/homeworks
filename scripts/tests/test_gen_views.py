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


class IdempotencyTests(ViewsTestBase):
    """A second run changes no byte and reports only UNCHANGED."""

    def test_two_all_runs_are_byte_identical_across_the_tree(self) -> None:
        self.assertEqual(0, self.generate("--all").returncode)
        first = snapshot(self.root)

        result = self.generate("--all")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual(first, snapshot(self.root))

    def test_second_all_run_reports_only_unchanged(self) -> None:
        self.assertEqual(0, self.generate("--all").returncode)

        result = self.generate("--all")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("README.md: UNCHANGED", result.stdout)
        self.assertIn("generated.manifest: UNCHANGED", result.stdout)
        for status in ("CREATE", "MODIFIED", "DELETED", "ORPHAN", "ERROR"):
            self.assertNotIn(f": {status}", result.stdout, result.stdout)

    def test_authored_prose_survives_both_runs(self) -> None:
        self.assertEqual(0, self.generate("--all").returncode)
        self.assertEqual(0, self.generate("--all").returncode)

        text = (self.root / "README.md").read_text(encoding="utf-8")

        self.assertTrue(text.startswith(PROSE_BEFORE), text)
        self.assertTrue(text.endswith(PROSE_AFTER), text)


class ManifestTests(ViewsTestBase):
    """D-17: the committed ledger is the only record of ownership."""

    def setUp(self) -> None:
        super().setUp()
        self.assertEqual(0, self.generate("readme").returncode)
        self.entry = self.read_manifest()["entries"][0]

    def test_every_digest_matches_the_owned_region_bytes(self) -> None:
        text = (self.root / "README.md").read_text(encoding="utf-8")
        start = text.index(BEGIN)
        stop = text.index(END) + len(END)
        owned = text[start:stop].encode("utf-8")

        self.assertEqual(hashlib.sha256(owned).hexdigest(), self.entry["sha256"])
        self.assertEqual(len(owned), self.entry["bytes"])

    def test_entries_are_sorted_by_path(self) -> None:
        paths = [entry["path"] for entry in self.read_manifest()["entries"]]

        self.assertEqual(sorted(paths), paths)

    def test_the_manifest_never_lists_itself(self) -> None:
        paths = [entry["path"] for entry in self.read_manifest()["entries"]]

        self.assertNotIn("generated.manifest", paths)

    def test_a_hand_edited_digest_is_manifest_drift(self) -> None:
        payload = self.read_manifest()
        digest = payload["entries"][0]["sha256"]
        payload["entries"][0]["sha256"] = (
            "0" if digest[0] != "0" else "1"
        ) + digest[1:]
        self.write_manifest(payload["entries"])
        before = snapshot(self.root)

        result = self.generate("readme", "--check")

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("generated.manifest: MODIFIED", result.stdout)
        self.assertIn("README.md: UNCHANGED", result.stdout)
        self.assertEqual(before, snapshot(self.root), "--check must not write")

    def test_the_writer_refuses_to_register_the_manifest_itself(self) -> None:
        program = (
            "import scripts.gen_views as g\n"
            "try:\n"
            "    g._manifest_entry(\n"
            "        path='generated.manifest',\n"
            "        owner='readme',\n"
            "        mode='whole',\n"
            "        owned=b'x',\n"
            "    )\n"
            "except g.CheckError:\n"
            "    raise SystemExit(0)\n"
            "raise SystemExit(1)\n"
        )

        result = run_pyyaml_program(program)

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)


class DriftTests(ViewsTestBase):
    """Every drift class is detected, and no drift class is ever repaired."""

    def setUp(self) -> None:
        super().setUp()
        self.assertEqual(0, self.generate("readme").returncode)

    def _add_orphan_entry(self, path: str, size: int) -> None:
        payload = self.read_manifest()
        payload["entries"].append(
            {
                "path": path,
                "owner": "readme",
                "mode": "whole",
                "sha256": "0" * 64,
                "bytes": size,
            }
        )
        payload["entries"].sort(key=lambda entry: entry["path"])
        self.write_manifest(payload["entries"])

    def test_an_edited_generated_byte_is_modified_drift(self) -> None:
        readme = self.root / "README.md"
        readme.write_text(
            readme.read_text(encoding="utf-8").replace("in-progress", "done"),
            encoding="utf-8",
        )
        before = snapshot(self.root)

        result = self.generate("readme", "--check")

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("README.md: MODIFIED", result.stdout)
        self.assertEqual(before, snapshot(self.root), "--check must not write")

    def test_a_deleted_region_file_is_an_error_and_is_not_recreated(self) -> None:
        (self.root / "README.md").unlink()

        check = self.generate("readme", "--check")

        self.assertEqual(1, check.returncode, check.stdout + check.stderr)
        self.assertIn("README.md: ERROR", check.stdout)
        self.assertFalse((self.root / "README.md").exists())

        write = self.generate("readme")

        self.assertEqual(1, write.returncode, write.stdout + write.stderr)
        self.assertFalse(
            (self.root / "README.md").exists(),
            "write mode must never recreate an authored file",
        )

    def test_a_headered_orphan_is_orphan_in_check_and_deleted_in_write(self) -> None:
        orphan = self.root / "docs" / "homeworks" / "1_2-gone.md"
        orphan.parent.mkdir(parents=True, exist_ok=True)
        orphan.write_text(GENERATED_HEADER + "\n\n# Gone\n", encoding="utf-8")
        self._add_orphan_entry("docs/homeworks/1_2-gone.md", orphan.stat().st_size)

        check = self.generate("readme", "--check")

        self.assertEqual(1, check.returncode, check.stdout + check.stderr)
        self.assertIn("docs/homeworks/1_2-gone.md: ORPHAN", check.stdout)
        self.assertTrue(orphan.exists(), "check mode must not delete anything")

        write = self.generate("readme")

        self.assertEqual(0, write.returncode, write.stdout + write.stderr)
        self.assertIn("docs/homeworks/1_2-gone.md: DELETE", write.stdout)
        self.assertFalse(orphan.exists())
        paths = [entry["path"] for entry in self.read_manifest()["entries"]]
        self.assertNotIn("docs/homeworks/1_2-gone.md", paths)

    def test_an_unheadered_orphan_is_left_on_disk_and_blocks_the_run(self) -> None:
        orphan = self.root / "docs" / "homeworks" / "1_2-gone.md"
        orphan.parent.mkdir(parents=True, exist_ok=True)
        orphan.write_text("# Authored page\n", encoding="utf-8")
        self._add_orphan_entry("docs/homeworks/1_2-gone.md", orphan.stat().st_size)
        before = snapshot(self.root)

        result = self.generate("readme")

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("docs/homeworks/1_2-gone.md: ORPHAN", result.stdout)
        self.assertTrue(orphan.exists(), "the orphan must be left intact")
        self.assertEqual(before, snapshot(self.root), "a blocked run must not write")


class MarkerTests(ViewsTestBase):
    """D-14: an ambiguous marker layout is exit 2, never a silent region."""

    def test_a_missing_begin_marker_exits_two(self) -> None:
        self.write_readme("# Homeworks\n\n" + END + "\n")

        self.assert_usage_error(self.generate("readme"))

    def test_two_begin_markers_exit_two(self) -> None:
        self.write_readme(
            PROSE_BEFORE + f"{BEGIN}\n{BEGIN}\n{END}" + PROSE_AFTER
        )

        self.assert_usage_error(self.generate("readme"))

    def test_an_end_marker_before_the_begin_marker_exits_two(self) -> None:
        self.write_readme(PROSE_BEFORE + f"{END}\n{BEGIN}" + PROSE_AFTER)

        self.assert_usage_error(self.generate("readme"))

    def test_a_missing_region_file_is_an_error_and_is_not_recreated(self) -> None:
        (self.root / "README.md").unlink()

        result = self.generate("readme")

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("README.md: ERROR", result.stdout)
        self.assertFalse((self.root / "README.md").exists())


class EscapeTests(ViewsTestBase):
    """ASVS V5: a metadata title cannot break the table or inject a link."""

    def test_specials_collapse_into_one_escaped_cell(self) -> None:
        path = self.root / "homeworks" / "1_3-alpha" / "homework.yaml"
        text = path.read_text(encoding="utf-8")
        path.write_text(
            text.replace(
                'title: "Alpha"',
                'title: "Pipe | [bracket] split\\nline"',
            ),
            encoding="utf-8",
        )

        result = self.generate("readme")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        readme = (self.root / "README.md").read_text(encoding="utf-8")
        row = next(
            line for line in readme.splitlines() if line.startswith("| 1.3 |")
        )
        project_cell = row.split(" | ")[1]

        self.assertIn(r"Pipe \| \[bracket\] split line", project_cell)
        self.assertNotIn("[bracket]", project_cell)
        self.assertEqual(1, project_cell.count("]("), project_cell)
        self.assertNotIn("\n", row)


class AllowlistTests(ViewsTestBase):
    """T-5-09: the manifest is an authority, never a way to widen the writes."""

    def test_a_manifest_entry_outside_the_allowlist_exits_two(self) -> None:
        for path in ("AGENTS.md", "homeworks/1_3-alpha/README.md"):
            with self.subTest(path=path):
                self.write_manifest(
                    [
                        {
                            "path": path,
                            "owner": "readme",
                            "mode": "whole",
                            "sha256": "0" * 64,
                            "bytes": 0,
                        }
                    ]
                )

                self.assert_usage_error(self.generate("readme", "--check"))


class RealTreeSmokeTest(unittest.TestCase):
    """One `--check` against the real tree, proving it is a pure check."""

    def test_readme_check_is_clean_and_writes_nothing(self) -> None:
        before_status = git_status()
        before_temps = sorted(REPO_ROOT.rglob(".gen_views-*"))

        result = run_gen_views("readme", "--check", "--dir", str(REPO_ROOT))

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual(
            before_status, git_status(), "--check must not change git status"
        )
        self.assertEqual([], before_temps)
        self.assertEqual(
            [],
            sorted(REPO_ROOT.rglob(".gen_views-*")),
            "--check must leave no temporary file behind",
        )


if __name__ == "__main__":
    unittest.main()

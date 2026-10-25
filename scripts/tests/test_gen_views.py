"""Integration tests for scripts/gen_views.py.

Every test drives the real generator through `uv run` against a disposable
repository root built by `scripts.tests.temp_root`, so no test module imports
PyYAML (04/D-14, D-28). `write_synthetic_root` supplies the two-homework fixture
(D-29); the base adds the root `README.md` the fixture deliberately omits.

The module is split by concern: the tracer path, the module dependency
boundary, the strict duplicate-key loader, idempotency, the manifest, every
drift class, the marker region, cell escaping, the target allowlist, the
multi-root workspace, the shared PlatformIO configuration, and one real-tree
`--check` smoke test.
"""

from __future__ import annotations

import configparser
import hashlib
import json
import re
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
REPOSITORY_URL = "https://github.com/VLoktiev-EMB/homeworks"
DOCS_TABLE_HEADER = "| ID | Project | Board | Framework | Status | Report |"
DOCS_TABLE_SEPARATOR = "|----|---------|-------|-----------|--------|--------|"

# Captured from `platformio.shared.ini` before generation: the five-line SCons
# block that a native build depends on. The test compares these bytes, not a
# substring, so a one-character edit fails (review finding).
SCONS_COMMENT = (
    "# The C standard flag is safe next to a C++ entry point: SCons routes `-std=`\n"
    "# into the C-only flag list by language (SCons 4.11.1 `Environment.py`\n"
    "# lines 1176-1181), so it reaches the `.c` library sources and never the\n"
    "# `.cpp` entry point. Do not move it into a per-project override.\n"
    "[native_unity]"
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


def run_contract_program(
    program: str, timeout: int = 180
) -> subprocess.CompletedProcess:
    """Run *program* with the checker's own pins (PyYAML and jsonschema).

    This module imports neither library (04/D-14), so `contract.read_shared_*`
    is exercised in a subprocess instead of at module scope.
    """
    if shutil.which("uv") is None:
        raise AssertionError(
            "uv is a required repository tool; install it before running this suite"
        )
    return subprocess.run(
        [
            "uv",
            "run",
            "--with",
            "PyYAML==6.0.3",
            "--with",
            "jsonschema==4.26.0",
            "python",
            "-c",
            program,
        ],
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

    def test_html_metacharacters_are_escaped_and_never_live(self) -> None:
        path = self.root / "homeworks" / "1_3-alpha" / "homework.yaml"
        text = path.read_text(encoding="utf-8")
        title = "Alpha & <img src=x onerror=alert(1)>"
        path.write_text(
            text.replace('title: "Alpha"', f'title: "{title}"'),
            encoding="utf-8",
        )
        escaped = "Alpha &amp; &lt;img src=x onerror=alert(1)&gt;"

        readme_result = self.generate("readme")
        docs_result = self.generate("docs")

        self.assertEqual(
            0, readme_result.returncode, readme_result.stdout + readme_result.stderr
        )
        self.assertEqual(
            0, docs_result.returncode, docs_result.stdout + docs_result.stderr
        )
        readme = (self.root / "README.md").read_text(encoding="utf-8")
        page = (
            self.root / "docs" / "homeworks" / "1_3-alpha.md"
        ).read_text(encoding="utf-8")
        for name, surface in (("README", readme), ("page", page)):
            with self.subTest(surface=name):
                self.assertNotIn(
                    "<img", surface, "raw HTML must never reach the site"
                )
                self.assertIn(escaped, surface)


class ReportPathTests(ViewsTestBase):
    """CR-01: `report.path` is a link destination, never unvalidated text."""

    def setUp(self) -> None:
        super().setUp()
        self.homework_yaml = (
            self.root / "homeworks" / "1_3-alpha" / "homework.yaml"
        )
        self.original = self.homework_yaml.read_text(encoding="utf-8")
        self.assertIn("  path: report.md\n", self.original)

    def set_report_path(self, value: str) -> None:
        # `json.dumps` is a valid YAML double-quoted scalar, so a literal
        # backslash in *value* reaches the loader as one backslash.
        self.homework_yaml.write_text(
            self.original.replace(
                "  path: report.md\n", f"  path: {json.dumps(value)}\n"
            ),
            encoding="utf-8",
        )

    def test_a_hostile_report_path_is_refused(self) -> None:
        for value in (
            "report).md",
            "../escape.md",
            "/etc/passwd.md",
            "report\\x.md",
        ):
            for view in ("readme", "docs"):
                with self.subTest(value=value, view=view):
                    self.set_report_path(value)

                    result = self.generate(view)

                    self.assert_usage_error(result)
                    self.assertIn("report.path", result.stderr)


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


class WorkspaceTests(ViewsTestBase):
    """META-07/D-15: one whole generated JSON workspace, tab-indented."""

    FIXED_PATHS = [".", "docs", "lib", "scripts"]
    FIXED_NAMES = ["repo", "docs", "lib", "scripts"]
    EXTENSIONS = {
        "recommendations": ["platformio.platformio-ide"],
        "unwantedRecommendations": [
            "ms-vscode.cpptools-extension-pack",
            "pioarduino.pioarduino-ide",
        ],
    }

    def workspace_path(self) -> Path:
        return self.root / "homeworks.code-workspace"

    def workspace_document(self) -> dict:
        return json.loads(self.workspace_path().read_text(encoding="utf-8"))

    def test_folders_are_the_four_roots_then_every_homework(self) -> None:
        result = self.generate("workspace")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("homeworks.code-workspace: CREATE", result.stdout)
        document = self.workspace_document()
        self.assertEqual(
            [
                ".",
                "docs",
                "lib",
                "scripts",
                "homeworks/1_3-alpha",
                "homeworks/1_4-beta",
            ],
            [folder["path"] for folder in document["folders"]],
        )
        self.assertEqual(
            ["repo", "docs", "lib", "scripts", "1.3 Alpha", "1.4 Beta"],
            [folder["name"] for folder in document["folders"]],
        )
        for folder in document["folders"]:
            self.assertEqual({"name", "path"}, set(folder))

    def test_every_path_is_ascii_and_repository_relative(self) -> None:
        self.assertEqual(0, self.generate("workspace").returncode)

        for folder in self.workspace_document()["folders"]:
            path = folder["path"]
            self.assertTrue(path.isascii(), path)
            self.assertFalse(Path(path).is_absolute(), path)
            self.assertNotIn("..", Path(path).parts, path)

    def test_extensions_block_is_the_templates_own_bytes(self) -> None:
        self.assertEqual(0, self.generate("workspace").returncode)

        text = self.workspace_path().read_text(encoding="utf-8")
        template = (self.root / "templates" / "views" / "workspace.json.tmpl")
        template_text = template.read_text(encoding="utf-8")
        marker = '\t"extensions"'
        self.assertEqual(self.EXTENSIONS, self.workspace_document()["extensions"])
        self.assertEqual(
            template_text[template_text.index(marker):],
            text[text.index(marker):],
            "the extensions block must be copied from the template verbatim",
        )

    def test_file_is_tab_indented_and_ends_with_one_newline(self) -> None:
        self.assertEqual(0, self.generate("workspace").returncode)

        text = self.workspace_path().read_text(encoding="utf-8")
        lines = text.splitlines()
        self.assertEqual('\t"folders": [', lines[1])
        self.assertIn('\t\t\t"name": "repo",', lines)
        for line in lines:
            self.assertFalse(line.startswith(" "), f"space indent: {line!r}")
        self.assertTrue(text.endswith("}\n"), repr(text[-3:]))
        self.assertFalse(text.endswith("\n\n"), "exactly one trailing newline")

    def test_a_second_run_is_unchanged(self) -> None:
        self.assertEqual(0, self.generate("workspace").returncode)

        result = self.generate("workspace")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("homeworks.code-workspace: UNCHANGED", result.stdout)
        self.assertIn("generated.manifest: UNCHANGED", result.stdout)
        for status in ("CREATE", "MODIFIED", "DELETED", "ORPHAN", "ERROR"):
            self.assertNotIn(f": {status}", result.stdout, result.stdout)

    def test_a_hand_edit_is_modified_drift_and_check_writes_nothing(self) -> None:
        self.assertEqual(0, self.generate("workspace").returncode)
        path = self.workspace_path()
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                '"name": "repo"', '"name": "root"'
            ),
            encoding="utf-8",
        )
        before = snapshot(self.root)

        result = self.generate("workspace", "--check")

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("homeworks.code-workspace: MODIFIED", result.stdout)
        self.assertEqual(before, snapshot(self.root), "--check must not write")

    def test_zero_homeworks_keeps_the_four_fixed_roots(self) -> None:
        empty = temp_root.write_synthetic_root(
            self.workspace / "empty", homeworks=False
        )

        result = run_gen_views("workspace", "--dir", str(empty))

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        document = json.loads(
            (empty / "homeworks.code-workspace").read_text(encoding="utf-8")
        )
        self.assertEqual(
            self.FIXED_PATHS, [folder["path"] for folder in document["folders"]]
        )
        self.assertEqual(
            self.FIXED_NAMES, [folder["name"] for folder in document["folders"]]
        )


class SharedIniTests(ViewsTestBase):
    """D-16/Pitfall 6: the shared ini is one whole generated projection."""

    PLATFORM_PIN = "espressif32@8.0.0"
    CORE_PIN = "6.2.0"
    SECTIONS = ("[esp32s3_arduino]", "[esp32s3_espidf]", "[native_unity]")

    def ini_path(self) -> Path:
        return self.root / "platformio.shared.ini"

    def ini_text(self) -> str:
        return self.ini_path().read_text(encoding="utf-8")

    def test_sections_survive_in_their_original_order(self) -> None:
        result = self.generate("shared-ini")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        text = self.ini_text()
        positions = [text.index(section) for section in self.SECTIONS]
        self.assertEqual(sorted(positions), positions, text)

    def test_the_scons_comment_block_is_byte_identical(self) -> None:
        self.assertEqual(0, self.generate("shared-ini").returncode)

        text = self.ini_text()
        start = text.index(SCONS_COMMENT.splitlines()[0])
        stop = text.index("[native_unity]") + len("[native_unity]")
        self.assertEqual(SCONS_COMMENT, text[start:stop])

    def test_both_esp_sections_share_the_metadata_pin(self) -> None:
        self.assertEqual(0, self.generate("shared-ini").returncode)

        parser = configparser.ConfigParser(interpolation=None)
        parser.read_string(self.ini_text())
        for section in ("esp32s3_arduino", "esp32s3_espidf"):
            self.assertEqual(self.PLATFORM_PIN, parser.get(section, "platform"))

    def test_contract_readers_return_the_generated_pins(self) -> None:
        self.assertEqual(0, self.generate("shared-ini").returncode)
        program = (
            "from scripts.metadata.contract import ("
            "read_shared_core_pin, read_shared_platform_pin)\n"
            f"root = {str(self.root)!r}\n"
            "print(read_shared_core_pin(root))\n"
            "print(read_shared_platform_pin(root))\n"
        )

        result = run_contract_program(program)

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual(
            [self.CORE_PIN, self.PLATFORM_PIN], result.stdout.splitlines()
        )

    def test_no_homework_id_appears_in_the_file(self) -> None:
        self.assertEqual(0, self.generate("shared-ini").returncode)

        self.assertNotRegex(self.ini_text(), r"homeworks/[0-9]+_[0-9]+-")

    def test_conflicting_pins_are_refused_with_one_record_each(self) -> None:
        path = self.root / "homeworks" / "1_4-beta" / "homework.yaml"
        text = path.read_text(encoding="utf-8")
        path.write_text(
            text.replace(
                'platform: "espressif32@8.0.0"', 'platform: "espressif32@9.0.0"'
            ),
            encoding="utf-8",
        )
        before = snapshot(self.root)

        result = self.generate("shared-ini")

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("homeworks/1_3-alpha/homework.yaml: ERROR", result.stdout)
        self.assertIn("homeworks/1_4-beta/homework.yaml: ERROR", result.stdout)
        self.assertEqual(
            before, snapshot(self.root), "a refused run must not write"
        )

    def test_zero_homeworks_exits_two_with_no_record(self) -> None:
        empty = temp_root.write_synthetic_root(
            self.workspace / "empty", homeworks=False
        )

        result = run_gen_views("shared-ini", "--dir", str(empty))

        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertEqual("", result.stdout, "a usage error must print no record")
        self.assertIn("ERROR:", result.stderr)

    def test_all_on_zero_homeworks_names_shared_ini(self) -> None:
        empty = temp_root.write_synthetic_root(
            self.workspace / "empty-all", homeworks=False
        )
        (empty / "README.md").write_text(
            PROSE_BEFORE + EMPTY_REGION + PROSE_AFTER, encoding="utf-8"
        )

        result = run_gen_views("--all", "--dir", str(empty))

        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertEqual("", result.stdout, "the abort precedes every record")
        self.assertIn("ERROR: shared-ini:", result.stderr)

    def test_a_second_run_is_unchanged(self) -> None:
        self.assertEqual(0, self.generate("shared-ini").returncode)

        result = self.generate("shared-ini")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("platformio.shared.ini: UNCHANGED", result.stdout)
        self.assertIn("generated.manifest: UNCHANGED", result.stdout)
        for status in ("CREATE", "MODIFIED", "DELETED", "ORPHAN", "ERROR"):
            self.assertNotIn(f": {status}", result.stdout, result.stdout)

    def test_a_hand_edit_is_modified_drift_and_check_writes_nothing(self) -> None:
        self.assertEqual(0, self.generate("shared-ini").returncode)
        path = self.ini_path()
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                "platform = espressif32@8.0.0",
                "platform = espressif32@8.0.1",
                1,
            ),
            encoding="utf-8",
        )
        before = snapshot(self.root)

        result = self.generate("shared-ini", "--check")

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("platformio.shared.ini: MODIFIED", result.stdout)
        self.assertEqual(before, snapshot(self.root), "--check must not write")


class DocsPagesTests(ViewsTestBase):
    """D-02/D-03: one metadata-card page per homework, escaped and absolute."""

    HOMEWORK_PAGES = (
        "docs/homeworks/1_3-alpha.md",
        "docs/homeworks/1_4-beta.md",
    )

    def page(self, homework_id: str) -> str:
        return (
            self.root / "docs" / "homeworks" / f"{homework_id}.md"
        ).read_text(encoding="utf-8")

    def homework_yaml(self, homework_id: str) -> Path:
        return self.root / "homeworks" / homework_id / "homework.yaml"

    def rewrite_homework(self, homework_id: str, old: str, new: str) -> None:
        path = self.homework_yaml(homework_id)
        text = path.read_text(encoding="utf-8")
        self.assertIn(old, text)
        path.write_text(text.replace(old, new, 1), encoding="utf-8")

    def test_one_page_per_homework_starts_with_the_generated_header(self) -> None:
        result = self.generate("docs")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        for relative in self.HOMEWORK_PAGES:
            path = self.root / relative
            self.assertTrue(path.is_file(), relative)
            self.assertTrue(
                path.read_text(encoding="utf-8").startswith(GENERATED_HEADER),
                relative,
            )

    def test_metadata_card_carries_the_fixture_values(self) -> None:
        self.assertEqual(0, self.generate("docs").returncode)

        text = self.page("1_3-alpha")

        self.assertTrue(text.startswith(GENERATED_HEADER), text[:120])
        self.assertIn("\n# Alpha\n", text)
        for row in (
            "| ID | 1_3-alpha |",
            "| Title | Alpha |",
            "| Board | esp32-s3-devkitc-1 |",
            "| Framework | arduino |",
            "| Language | cpp |",
            "| Status | in-progress |",
            "| Toolchain | PlatformIO 6.2.0 · espressif32@8.0.0 |",
            "| Simulation | wokwi (pending) |",
        ):
            self.assertIn(row, text)

    def test_links_are_absolute_repository_urls(self) -> None:
        self.assertEqual(0, self.generate("docs").returncode)

        text = self.page("1_3-alpha")

        self.assertIn(
            f"- [Report]({REPOSITORY_URL}/blob/main/homeworks/1_3-alpha/report.md)",
            text,
        )
        self.assertIn(
            "- [Project README]("
            f"{REPOSITORY_URL}/blob/main/homeworks/1_3-alpha/README.md)",
            text,
        )
        self.assertNotIn("../", text)

    def test_a_missing_simulation_block_renders_none(self) -> None:
        self.rewrite_homework(
            "1_4-beta", "simulation:\n  tool: none\n  status: none\n", ""
        )

        result = self.generate("docs")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("| Simulation | none |", self.page("1_4-beta"))
        self.assertIn("| Simulation | wokwi (pending) |", self.page("1_3-alpha"))

    def test_a_missing_report_block_renders_none_and_no_report_bullet(self) -> None:
        self.rewrite_homework(
            "1_3-alpha", "report:\n  path: report.md\n  status: draft\n", ""
        )
        program = (
            "from pathlib import Path\n"
            "from scripts.metadata.contract import validate_homework_text\n"
            f"root = Path({str(self.root)!r})\n"
            "path = root / 'homeworks' / '1_3-alpha' / 'homework.yaml'\n"
            "records = validate_homework_text(\n"
            "    path.read_text(encoding='utf-8'), root=root, path=path)\n"
            "problems = [item for item in records if item['status'] != 'OK']\n"
            "print(problems)\n"
            "raise SystemExit(0 if not problems else 1)\n"
        )
        schema_check = run_contract_program(program)
        self.assertEqual(
            0, schema_check.returncode, schema_check.stdout + schema_check.stderr
        )

        self.assertEqual(0, self.generate("readme").returncode)
        result = self.generate("docs")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        text = self.page("1_3-alpha")
        self.assertNotIn("- [Report](", text)
        self.assertIn(
            "- [Project README]("
            f"{REPOSITORY_URL}/blob/main/homeworks/1_3-alpha/README.md)",
            text,
        )
        rows = [
            line
            for line in (self.root / "README.md").read_text(encoding="utf-8").splitlines()
            if line.startswith("| 1.3 |")
        ]
        self.assertEqual(1, len(rows))
        self.assertTrue(rows[0].endswith("| none |"), rows[0])
        self.assertEqual(7, rows[0].count("|"), "the cell width must stay six columns")

    def test_a_pipe_and_a_newline_become_one_escaped_cell(self) -> None:
        self.rewrite_homework(
            "1_3-alpha",
            'title: "Alpha"',
            'title: "Pipe | [bracket] split\\nline"',
        )

        result = self.generate("docs")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        text = self.page("1_3-alpha")
        self.assertIn(r"| Title | Pipe \| \[bracket\] split line |", text)
        self.assertNotIn("[bracket]", text)
        self.assertNotIn("<b>", text)
        self.assertEqual(1, text.count("| Title |"))

    def test_a_hand_edit_is_modified_drift_and_check_writes_nothing(self) -> None:
        self.assertEqual(0, self.generate("docs").returncode)
        path = self.root / "docs" / "homeworks" / "1_3-alpha.md"
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                "| Status | in-progress |", "| Status | complete |"
            ),
            encoding="utf-8",
        )
        before = snapshot(self.root)

        result = self.generate("docs", "--check")

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("docs/homeworks/1_3-alpha.md: MODIFIED", result.stdout)
        self.assertEqual(before, snapshot(self.root), "--check must not write")

    def test_a_hand_added_page_is_orphan_in_check_and_deleted_in_write(self) -> None:
        self.assertEqual(0, self.generate("docs").returncode)
        ghost = self.root / "docs" / "homeworks" / "9_9-ghost.md"
        ghost.write_text(GENERATED_HEADER + "\n\n# Ghost\n", encoding="utf-8")

        check = self.generate("docs", "--check")

        self.assertEqual(1, check.returncode, check.stdout + check.stderr)
        self.assertIn("docs/homeworks/9_9-ghost.md: ORPHAN", check.stdout)
        self.assertTrue(ghost.exists(), "check mode must not delete anything")

        write = self.generate("docs")

        self.assertEqual(0, write.returncode, write.stdout + write.stderr)
        self.assertIn("docs/homeworks/9_9-ghost.md: DELETE", write.stdout)
        self.assertFalse(ghost.exists())

    def test_an_unheadered_stray_page_blocks_write_mode(self) -> None:
        self.assertEqual(0, self.generate("docs").returncode)
        ghost = self.root / "docs" / "homeworks" / "9_9-ghost.md"
        ghost.write_text("# Authored page\n", encoding="utf-8")
        before = snapshot(self.root)

        result = self.generate("docs")

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("docs/homeworks/9_9-ghost.md: ORPHAN", result.stdout)
        self.assertTrue(ghost.exists())
        self.assertEqual(before, snapshot(self.root), "a blocked run must not write")

    def test_a_second_run_reports_only_unchanged(self) -> None:
        self.assertEqual(0, self.generate("docs").returncode)

        result = self.generate("docs")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("generated.manifest: UNCHANGED", result.stdout)
        for status in ("CREATE", "MODIFIED", "DELETED", "ORPHAN", "ERROR"):
            self.assertNotIn(f": {status}", result.stdout, result.stdout)

    def index_path(self) -> Path:
        return self.root / "docs" / "index.md"

    def index_region(self) -> str:
        text = self.index_path().read_text(encoding="utf-8")
        start = text.index(BEGIN)
        stop = text.index(END) + len(END)
        return text[start:stop]

    def test_index_and_readme_share_the_six_column_header(self) -> None:
        self.assertEqual(0, self.generate("docs").returncode)
        self.assertEqual(0, self.generate("readme").returncode)

        readme = (self.root / "README.md").read_text(encoding="utf-8")
        index = self.index_path().read_text(encoding="utf-8")

        self.assertEqual(1, readme.count(DOCS_TABLE_HEADER))
        self.assertEqual(1, index.count(DOCS_TABLE_HEADER))
        self.assertIn(DOCS_TABLE_SEPARATOR, index)
        self.assertTrue(index.startswith("# Homeworks\n"))
        self.assertIn("This site is a catalog", index)

    def test_index_rows_are_absolute_and_readme_rows_stay_relative(self) -> None:
        self.assertEqual(0, self.generate("docs").returncode)
        self.assertEqual(0, self.generate("readme").returncode)

        region = self.index_region()
        self.assertIn(
            f"]({REPOSITORY_URL}/tree/main/homeworks/1_3-alpha/)", region
        )
        self.assertIn(
            f"]({REPOSITORY_URL}/blob/main/homeworks/1_3-alpha/report.md)",
            region,
        )
        self.assertNotIn("](homeworks/", region)

        readme = (self.root / "README.md").read_text(encoding="utf-8")
        start = readme.index(BEGIN)
        stop = readme.index(END) + len(END)
        readme_region = readme[start:stop]
        self.assertIn("](homeworks/1_3-alpha/)", readme_region)
        self.assertIn("](homeworks/1_3-alpha/report.md)", readme_region)
        self.assertNotIn(REPOSITORY_URL, readme_region)

    def test_a_prose_edit_outside_the_index_region_is_not_drift(self) -> None:
        self.assertEqual(0, self.generate("docs").returncode)
        text = self.index_path().read_text(encoding="utf-8")
        self.index_path().write_text(
            "# Homeworks\n\nRewritten authored prose.\n\n"
            + text[text.index(BEGIN):],
            encoding="utf-8",
        )

        result = self.generate("docs", "--check")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("docs/index.md: UNCHANGED", result.stdout)

    def test_a_duplicated_begin_marker_is_exit_two(self) -> None:
        self.assertEqual(0, self.generate("docs").returncode)
        text = self.index_path().read_text(encoding="utf-8")
        self.index_path().write_text(
            text.replace(BEGIN, f"{BEGIN}\n{BEGIN}", 1), encoding="utf-8"
        )

        result = self.generate("docs")

        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertEqual("", result.stdout, "a usage error must print no record")
        self.assertIn("ERROR:", result.stderr)

    def test_a_missing_index_is_an_error_and_is_not_recreated(self) -> None:
        self.assertEqual(0, self.generate("docs").returncode)
        self.index_path().unlink()

        check = self.generate("docs", "--check")

        self.assertEqual(1, check.returncode, check.stdout + check.stderr)
        self.assertIn("docs/index.md: ERROR", check.stdout)

        write = self.generate("docs")

        self.assertEqual(1, write.returncode, write.stdout + write.stderr)
        self.assertFalse(
            self.index_path().exists(),
            "write mode must never recreate an authored file",
        )

    def test_real_tree_index_uses_the_same_headers_as_the_readme(self) -> None:
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        index = (REPO_ROOT / "docs" / "index.md").read_text(encoding="utf-8")

        self.assertIn(DOCS_TABLE_HEADER, readme)
        self.assertIn(DOCS_TABLE_HEADER, index)
        self.assertIn(DOCS_TABLE_SEPARATOR, index)
        region = index.split(BEGIN, 1)[1]
        self.assertIn(REPOSITORY_URL, region)
        self.assertNotIn("](homeworks/", region)

    def test_real_tree_homework_pages_have_no_parent_segment(self) -> None:
        pages = sorted((REPO_ROOT / "docs" / "homeworks").glob("*.md"))

        self.assertTrue(pages, "the real tree must carry at least one homework page")
        for page in pages:
            text = page.read_text(encoding="utf-8")
            self.assertTrue(text.startswith(GENERATED_HEADER), page.name)
            self.assertNotIn("../", text, page.name)


class BoardPageTests(ViewsTestBase):
    """D-04/D-10: one page per board profile, with resolvable homework links."""

    BOARD_ID = "esp32-s3-devkitc-1"
    PINOUT = (
        "https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32s3/"
        "esp32-s3-devkitc-1/user_guide.html"
    )

    def board_page(self, board_id: str = BOARD_ID) -> str:
        return (
            self.root / "docs" / "boards" / f"{board_id}.md"
        ).read_text(encoding="utf-8")

    def profile_path(self, stem: str = BOARD_ID) -> Path:
        return self.root / "boards" / f"{stem}.yaml"

    def rewrite_profile(self, old: str, new: str) -> None:
        path = self.profile_path()
        text = path.read_text(encoding="utf-8")
        self.assertIn(old, text)
        path.write_text(text.replace(old, new, 1), encoding="utf-8")

    def write_profile(self, stem: str, body: str) -> None:
        path = self.profile_path(stem)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")

    def test_one_page_per_profile_starts_with_the_generated_header(self) -> None:
        result = self.generate("docs")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        path = self.root / "docs" / "boards" / f"{self.BOARD_ID}.md"
        self.assertTrue(path.is_file())
        self.assertTrue(
            path.read_text(encoding="utf-8").startswith(GENERATED_HEADER)
        )

    def test_table_renders_every_profile_field(self) -> None:
        self.assertEqual(0, self.generate("docs").returncode)

        text = self.board_page()

        self.assertIn("\n# esp32-s3-devkitc-1\n", text)
        for row in (
            "| SoC | esp32-s3 |",
            "| Flash | 16 MB |",
            "| PSRAM | octal |",
            "| Frameworks | arduino, espidf |",
        ):
            self.assertIn(row, text)

    def test_html_in_a_profile_field_is_escaped(self) -> None:
        self.rewrite_profile("soc: esp32-s3", "soc: <b>esp32-s3</b> & co")

        result = self.generate("docs")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        text = self.board_page()
        self.assertNotIn("<b>", text, "raw HTML must never reach the site")
        self.assertIn("| SoC | &lt;b&gt;esp32-s3&lt;/b&gt; &amp; co |", text)

    def test_pinout_url_is_a_markdown_link(self) -> None:
        self.assertEqual(0, self.generate("docs").returncode)

        text = self.board_page()

        self.assertIn(f"| Pinout | [Official pinout]({self.PINOUT}) |", text)
        self.assertNotIn(f"| Pinout | {self.PINOUT} |", text)

    def test_homework_links_use_the_relative_docs_form_and_resolve(self) -> None:
        self.assertEqual(0, self.generate("docs").returncode)

        text = self.board_page()

        self.assertIn("## Homeworks on this board", text)
        self.assertIn("- [1.3 Alpha](../homeworks/1_3-alpha.md)", text)
        self.assertIn("- [1.4 Beta](../homeworks/1_4-beta.md)", text)
        for homework_id in ("1_3-alpha", "1_4-beta"):
            self.assertTrue(
                (self.root / "docs" / "homeworks" / f"{homework_id}.md").is_file(),
                homework_id,
            )
        self.assertNotIn("../../", text)

    def test_a_profile_with_no_homework_renders_the_empty_state(self) -> None:
        self.write_profile(
            "esp32-c3-mini",
            "id: esp32-c3-mini\n"
            "soc: esp32-c3\n"
            "flash_mb: 4\n"
            "psram: none\n"
            "frameworks:\n"
            "  - arduino\n"
            "pinout_url: https://example.com/pinout\n",
        )

        result = self.generate("docs")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        text = self.board_page("esp32-c3-mini")
        self.assertIn("## Homeworks on this board", text)
        self.assertIn("_No homework uses this board yet._", text)

    def test_a_duplicated_psram_key_exits_two(self) -> None:
        self.rewrite_profile("psram: octal", "psram: octal\npsram: quad")

        result = self.generate("docs")

        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertEqual("", result.stdout, "a usage error must print no record")
        self.assertIn("ERROR:", result.stderr)
        self.assertIn("duplicate", result.stderr.lower())

    def test_a_duplicated_pinout_url_key_exits_two(self) -> None:
        self.rewrite_profile(
            f"pinout_url: {self.PINOUT}",
            f"pinout_url: {self.PINOUT}\npinout_url: https://example.com/other",
        )

        result = self.generate("docs")

        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("ERROR:", result.stderr)
        self.assertIn("duplicate", result.stderr.lower())

    def test_an_id_stem_mismatch_exits_two_naming_both(self) -> None:
        self.write_profile(
            "esp32-c9",
            "id: esp32-c8\n"
            "soc: esp32-c9\n"
            "flash_mb: 4\n"
            "psram: none\n"
            "frameworks:\n"
            "  - arduino\n"
            "pinout_url: https://example.com/pinout\n",
        )

        result = self.generate("docs")

        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("ERROR:", result.stderr)
        self.assertIn("esp32-c8", result.stderr)
        self.assertIn("esp32-c9", result.stderr)
        self.assertFalse((self.root / "docs" / "boards" / "esp32-c9.md").exists())

    def test_a_stray_board_page_is_orphan_in_check_mode(self) -> None:
        self.assertEqual(0, self.generate("docs").returncode)
        ghost = self.root / "docs" / "boards" / "9_9-ghost.md"
        ghost.write_text(GENERATED_HEADER + "\n\n# Ghost\n", encoding="utf-8")

        result = self.generate("docs", "--check")

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("docs/boards/9_9-ghost.md: ORPHAN", result.stdout)
        self.assertTrue(ghost.exists(), "check mode must not delete anything")

    def test_a_second_run_reports_only_unchanged(self) -> None:
        self.assertEqual(0, self.generate("docs").returncode)

        result = self.generate("docs")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn(
            f"docs/boards/{self.BOARD_ID}.md: UNCHANGED", result.stdout
        )
        self.assertIn("generated.manifest: UNCHANGED", result.stdout)
        for status in ("CREATE", "MODIFIED", "DELETED", "ORPHAN", "ERROR"):
            self.assertNotIn(f": {status}", result.stdout, result.stdout)

    def test_real_tree_board_pages_only_use_homeworks_links(self) -> None:
        pages = sorted((REPO_ROOT / "docs" / "boards").glob("*.md"))

        self.assertTrue(pages, "the real tree must carry at least one board page")
        for page in pages:
            text = page.read_text(encoding="utf-8")
            self.assertTrue(text.startswith(GENERATED_HEADER), page.name)
            self.assertNotIn("../../", text, page.name)
            for fragment in text.split("../")[1:]:
                self.assertTrue(
                    fragment.startswith("homeworks/"),
                    f"{page.name} has a parent segment outside ../homeworks/: "
                    f"{fragment[:40]}",
                )


class NavTests(ViewsTestBase):
    """D-05/D-06/D-10: one whole generated `mkdocs.yml` with four nav sections."""

    SECTIONS = (
        '  - "Home": index.md',
        '  - "Homeworks":',
        '  - "Boards":',
        '  - "Decisions":',
    )
    ENTRY = re.compile(r'^\s+- "[^"]+": \S+\.md$')
    SECTION = re.compile(r'^\s+- "[^"]+":$')

    def nav_path(self) -> Path:
        return self.root / "mkdocs.yml"

    def nav_text(self) -> str:
        return self.nav_path().read_text(encoding="utf-8")

    def nav_block(self) -> list:
        """Return the lines between `nav:` and the next top-level key."""
        lines = self.nav_text().splitlines()
        start = lines.index("nav:") + 1
        block = []
        for line in lines[start:]:
            if line and not line[0].isspace():
                break
            block.append(line)
        return block

    def nav_targets(self) -> list:
        return [
            match.group(1)
            for match in (
                re.match(r'^\s+- "[^"]+": (\S+\.md)$', line)
                for line in self.nav_block()
            )
            if match
        ]

    def write_decision(self, name: str, text: str) -> Path:
        path = self.root / "docs" / "decisions" / name
        path.write_text(text, encoding="utf-8")
        return path

    def label_for(self, target: str) -> str:
        pattern = r'^\s+- "([^"]+)": ' + re.escape(target) + r"$"
        matches = re.findall(pattern, self.nav_text(), re.M)
        self.assertEqual(1, len(matches), f"{target}: {matches}")
        return matches[0]

    def test_the_four_sections_appear_once_in_order(self) -> None:
        self.assertEqual(0, self.generate("nav").returncode)

        text = self.nav_text()

        positions = [text.index(section) for section in self.SECTIONS]
        self.assertEqual(sorted(positions), positions, text)
        for section in self.SECTIONS:
            with self.subTest(section=section):
                self.assertEqual(1, text.count(section), text)

    def test_every_homework_board_and_decision_target_appears_once(self) -> None:
        self.write_decision(
            "0002-second.md",
            "---\nstatus: accepted\n---\n\n# Second decision\n",
        )

        self.assertEqual(0, self.generate("nav").returncode)

        targets = self.nav_targets()

        self.assertEqual(len(targets), len(set(targets)), targets)
        for target in (
            "index.md",
            "homeworks/1_3-alpha.md",
            "homeworks/1_4-beta.md",
            "boards/esp32-s3-devkitc-1.md",
            "decisions/README.md",
            "decisions/0002-second.md",
        ):
            with self.subTest(target=target):
                self.assertEqual(1, targets.count(target), targets)
        self.assertEqual(
            "Decision record index", self.label_for("decisions/README.md")
        )

    def test_every_entry_uses_an_unquoted_separator_colon(self) -> None:
        self.assertEqual(0, self.generate("nav").returncode)

        entries = [
            line
            for line in self.nav_block()
            if line.strip().startswith("- ")
        ]

        self.assertTrue(entries, "the nav block must carry entries")
        for line in entries:
            with self.subTest(line=line):
                if self.SECTION.match(line):
                    continue
                self.assertRegex(line, self.ENTRY)
                self.assertFalse(
                    line.rstrip().endswith('"'),
                    f"whole-entry quoted scalar: {line!r}",
                )

    def test_a_second_run_reports_only_unchanged(self) -> None:
        self.assertEqual(0, self.generate("nav").returncode)

        result = self.generate("nav")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("mkdocs.yml: UNCHANGED", result.stdout)
        self.assertIn("generated.manifest: UNCHANGED", result.stdout)
        for status in ("CREATE", "MODIFIED", "DELETED", "ORPHAN", "ERROR"):
            self.assertNotIn(f": {status}", result.stdout, result.stdout)

    def test_a_hand_edit_is_modified_drift_and_check_writes_nothing(self) -> None:
        self.assertEqual(0, self.generate("nav").returncode)
        path = self.nav_path()
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                "site_name: Homeworks", "site_name: Renamed"
            ),
            encoding="utf-8",
        )
        before = snapshot(self.root)

        result = self.generate("nav", "--check")

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("mkdocs.yml: MODIFIED", result.stdout)
        self.assertEqual(before, snapshot(self.root), "--check must not write")

    def test_a_quoted_heading_becomes_a_single_quote_label(self) -> None:
        self.write_decision(
            "0003-quoted.md",
            '---\nstatus: accepted\n---\n\n# A "quoted" decision\n',
        )

        self.assertEqual(0, self.generate("nav").returncode)

        self.assertEqual(
            "A 'quoted' decision", self.label_for("decisions/0003-quoted.md")
        )
        self.assertNotIn('"A "quoted" decision"', self.nav_text())

    def test_a_heading_with_a_colon_stays_one_valid_entry(self) -> None:
        self.write_decision(
            "0004-colon.md",
            "---\nstatus: accepted\n---\n\n# Scope: boundaries\n",
        )

        self.assertEqual(0, self.generate("nav").returncode)

        self.assertEqual(
            "Scope: boundaries", self.label_for("decisions/0004-colon.md")
        )
        self.assertRegex(
            self.nav_text(),
            r'(?m)^\s+- "Scope: boundaries": decisions/0004-colon\.md$',
        )

    def test_frontmatter_and_prose_only_files_label_from_their_heading(self) -> None:
        self.write_decision(
            "0005-frontmatter.md",
            "---\nstatus: accepted\ndate: 2026-10-23\n---\n\n# With frontmatter\n",
        )
        self.write_decision(
            "0006-prose.md",
            "# Without frontmatter\n\nAuthored body.\n",
        )

        self.assertEqual(0, self.generate("nav").returncode)

        self.assertEqual(
            "With frontmatter", self.label_for("decisions/0005-frontmatter.md")
        )
        self.assertEqual(
            "Without frontmatter", self.label_for("decisions/0006-prose.md")
        )
        text = self.nav_text()
        self.assertNotIn('- "accepted"', text)
        self.assertNotIn('- "2026-10-23"', text)
        self.assertNotIn('- "status: accepted"', text)

    def test_a_file_without_a_heading_falls_back_to_the_title_cased_slug(self) -> None:
        self.write_decision(
            "0007-no-heading.md",
            "---\nstatus: accepted\n---\n\nOnly prose, no ATX heading.\n",
        )

        self.assertEqual(0, self.generate("nav").returncode)

        self.assertEqual(
            "No Heading", self.label_for("decisions/0007-no-heading.md")
        )

    def test_a_decision_symlink_is_refused(self) -> None:
        target = self.write_decision("0008-real.md", "# Real\n")
        link = self.root / "docs" / "decisions" / "0008-link.md"
        link.symlink_to(target)

        result = self.generate("nav")

        self.assert_usage_error(result)
        self.assertIn("symlink", result.stderr)

    def test_real_tree_all_check_is_clean(self) -> None:
        result = run_gen_views("--all", "--check", "--dir", str(REPO_ROOT))

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        for path in (
            "README.md",
            "mkdocs.yml",
            "homeworks.code-workspace",
            "platformio.shared.ini",
            "docs/index.md",
            "docs/homeworks/1_3-police-flasher.md",
            "docs/boards/esp32-s3-devkitc-1.md",
            "generated.manifest",
        ):
            with self.subTest(path=path):
                self.assertIn(f"{path}: UNCHANGED", result.stdout)


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

"""Integration tests for scripts/new_homework.

Every test runs the real scaffold through `uv run` against a disposable
repository root built by `scripts.tests.temp_root`, never against the
repository itself, so a failure cannot leave a `homeworks/` directory behind.

The module pins the four META-04 behaviours — scaffold, content idempotency,
`--dry-run` parity and refusal to overwrite — and the eight FOUND-01 paths.
Two committed golden trees make any unintended change to a rendered file
visible as a unified diff. Every refusal path asserts both the exit code and
the absence of plan output, because "exit 2 before any plan output" is the
contract, not just the status.
"""

from __future__ import annotations

import ast
import difflib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.metadata.errors import CheckError
from scripts.metadata.render import render
from scripts.tests import temp_root

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = "scripts/new_homework"
GOLDEN_ROOT = REPO_ROOT / "scripts" / "tests" / "fixtures" / "golden"
METADATA_DIR = REPO_ROOT / "scripts" / "metadata"

HOMEWORK_ID = "1_3-fixture"
TEMPLATES = ("arduino", "espidf")

# FOUND-01: the eight paths a scaffolded homework must contain.
EIGHT_PATHS = (
    "platformio.ini",
    "src/main.cpp",
    "include/.gitkeep",
    "test/test_homework/test_homework.c",
    "assets/.gitkeep",
    "README.md",
    "task.md",
    "homework.yaml",
)


def run_scaffold(*args: str, timeout: int = 180) -> subprocess.CompletedProcess:
    """Invoke `uv run scripts/new_homework` from the repository root."""
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


def snapshot(directory: Path) -> dict:
    """Return every file under *directory* as `relative path -> bytes`."""
    return {
        path.relative_to(directory).as_posix(): path.read_bytes()
        for path in sorted(directory.rglob("*"), key=lambda item: item.as_posix())
        if path.is_file()
    }


class ScaffoldTestBase(unittest.TestCase):
    """One disposable root per test, plus the invocation helpers."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="new-homework-")
        self.addCleanup(self._tmp.cleanup)
        self.workspace = Path(self._tmp.name)
        self.root = temp_root.build_root(self.workspace / "root")

    def build(self, name: str, *, homeworks: bool = True) -> Path:
        return temp_root.build_root(
            self.workspace / name, homeworks=homeworks
        )

    def scaffold(
        self,
        root: Path,
        homework_id: str = HOMEWORK_ID,
        template: str = "arduino",
        flags: tuple[str, ...] = (),
    ) -> subprocess.CompletedProcess:
        return run_scaffold(
            homework_id, "--template", template, "--dir", str(root), *flags
        )

    def target(self, root: Path, homework_id: str = HOMEWORK_ID) -> Path:
        return root / "homeworks" / homework_id

    def assert_usage_error(self, result: subprocess.CompletedProcess) -> None:
        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertEqual("", result.stdout, "a usage error must print no plan")
        self.assertIn("ERROR:", result.stderr)

    def assert_golden(self, root: Path, template: str) -> None:
        expected_dir = GOLDEN_ROOT / f"homework-{template}"
        actual_dir = self.target(root)
        expected = snapshot(expected_dir)
        actual = snapshot(actual_dir)

        self.assertEqual(
            sorted(expected), sorted(actual), "the scaffolded file set differs"
        )
        differences = []
        for name in sorted(expected):
            if actual[name] == expected[name]:
                continue
            left = actual[name].decode("utf-8").splitlines()
            right = expected[name].decode("utf-8").splitlines()
            differences.extend(
                difflib.unified_diff(
                    left,
                    right,
                    fromfile=f"scaffolded/{name}",
                    tofile=f"golden/homework-{template}/{name}",
                    lineterm="",
                )
            )
        self.assertEqual([], differences, "\n".join(differences))


class InventoryTests(ScaffoldTestBase):
    """FOUND-01: both templates produce the eight declared paths."""

    def test_arduino_scaffold_creates_the_eight_paths(self) -> None:
        result = self.scaffold(self.root)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        target = self.target(self.root)
        missing = [name for name in EIGHT_PATHS if not (target / name).is_file()]
        self.assertEqual([], missing)

    def test_espidf_scaffold_creates_the_eight_paths(self) -> None:
        result = self.scaffold(self.root, template="espidf")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        target = self.target(self.root)
        missing = [name for name in EIGHT_PATHS if not (target / name).is_file()]
        self.assertEqual([], missing)
        self.assertTrue((target / "sdkconfig.defaults").is_file())

    def test_rendered_homework_yaml_carries_title_and_status(self) -> None:
        for template in TEMPLATES:
            root = self.build(f"render-{template}")
            result = self.scaffold(root, template=template)
            with self.subTest(template=template):
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                text = (self.target(root) / "homework.yaml").read_text(
                    encoding="utf-8"
                )
                self.assertIn('id: "1_3-fixture"', text)
                self.assertIn('title: "Fixture"', text)
                self.assertIn("status: planned", text)
                self.assertIn(f"framework: {template}", text)
                self.assertIn('platformio: "6.2.0"', text)
                self.assertIn('platform: "espressif32@8.0.0"', text)

    def test_fresh_root_creates_nested_parents(self) -> None:
        root = self.build("fresh", homeworks=False)
        self.assertFalse((root / "homeworks").exists())

        result = self.scaffold(root)

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        target = self.target(root)
        for relative in ("src", "include", "test/test_homework", "assets"):
            with self.subTest(directory=relative):
                self.assertTrue((target / relative).is_dir())
        for relative in EIGHT_PATHS:
            with self.subTest(file=relative):
                self.assertTrue((target / relative).is_file())


class GoldenTreeTests(ScaffoldTestBase):
    """D-37: a committed expected tree, reported as a unified diff."""

    def test_arduino_tree_matches_its_golden(self) -> None:
        result = self.scaffold(self.root)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assert_golden(self.root, "arduino")

    def test_espidf_tree_matches_its_golden(self) -> None:
        result = self.scaffold(self.root, template="espidf")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assert_golden(self.root, "espidf")


class IdempotencyTests(ScaffoldTestBase):
    """D-20: content-based idempotency, with no clock and no formatting."""

    def test_second_run_is_all_unchanged(self) -> None:
        self.assertEqual(0, self.scaffold(self.root).returncode)

        result = self.scaffold(self.root)

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("UNCHANGED", result.stdout)
        for status in (": CREATE", ": CONFLICT", ": ERROR"):
            self.assertNotIn(status, result.stdout, result.stdout)

    def test_two_real_runs_are_byte_identical(self) -> None:
        self.assertEqual(0, self.scaffold(self.root).returncode)
        first = snapshot(self.target(self.root))

        result = self.scaffold(self.root)

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual(first, snapshot(self.target(self.root)))


class ConflictTests(ScaffoldTestBase):
    """D-20 / T-04-03: any conflict blocks every write and is never overridden."""

    def test_conflict_and_deletion_write_nothing(self) -> None:
        self.assertEqual(
            0, self.scaffold(self.root, template="espidf").returncode
        )
        target = self.target(self.root)
        with (target / "README.md").open("a", encoding="utf-8") as handle:
            handle.write("x\n")
        (target / "assets" / ".gitkeep").unlink()
        before = snapshot(target)

        result = self.scaffold(self.root, template="espidf")

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("homeworks/1_3-fixture/README.md: CONFLICT — ", result.stdout)
        self.assertFalse(
            (target / "assets" / ".gitkeep").exists(),
            "a blocked run must not recreate the deleted file",
        )
        self.assertEqual(before, snapshot(target), "a blocked run must not write")

    def test_symlinked_target_is_conflict_and_left_intact(self) -> None:
        target = self.target(self.root)
        target.mkdir(parents=True)
        outside = self.workspace / "outside.txt"
        outside.write_text("keep me\n", encoding="utf-8")
        link = target / "README.md"
        link.symlink_to(outside)

        result = self.scaffold(self.root)

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("homeworks/1_3-fixture/README.md: CONFLICT — ", result.stdout)
        self.assertTrue(link.is_symlink(), "the symlink must be left intact")
        self.assertEqual(outside.resolve(), link.resolve())
        self.assertEqual("keep me\n", outside.read_text(encoding="utf-8"))
        self.assertEqual(
            ["README.md"],
            sorted(path.name for path in target.iterdir()),
            "a conflict must block every other write",
        )

    def test_intermediate_directory_symlink_is_conflict_and_writes_nothing(
        self,
    ) -> None:
        target = self.target(self.root)
        target.mkdir(parents=True)
        outside = self.workspace / "outside"
        outside.mkdir()
        (target / "src").symlink_to(outside)

        result = self.scaffold(self.root)

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn(
            "homeworks/1_3-fixture/src/main.cpp: CONFLICT — ", result.stdout
        )
        self.assertIn(
            "intermediate path homeworks/1_3-fixture/src is a symlink; "
            "refusing to follow it",
            result.stdout,
        )
        self.assertTrue(
            (target / "src").is_symlink(), "the symlink must be left intact"
        )
        self.assertEqual(
            [],
            sorted(path.name for path in outside.iterdir()),
            "nothing may be written outside homeworks/",
        )
        self.assertEqual(
            ["src"],
            sorted(path.name for path in target.iterdir()),
            "a conflict must block every other write",
        )

    def test_target_directory_symlink_exits_2(self) -> None:
        destination = self.root / "homeworks" / "sub" / HOMEWORK_ID
        destination.mkdir(parents=True)
        link = self.target(self.root)
        link.symlink_to(Path("sub") / HOMEWORK_ID)

        result = self.scaffold(self.root, flags=("--json",))

        self.assert_usage_error(result)
        self.assertIn(
            "homeworks/1_3-fixture is a symlink; refusing to follow it",
            result.stderr,
        )
        self.assertTrue(link.is_symlink(), "the symlink must be left intact")
        self.assertEqual(
            [],
            sorted(path.name for path in destination.iterdir()),
            "nothing may be written through the symlinked target",
        )

    def test_homeworks_base_symlink_exits_2(self) -> None:
        for label, flags in (("dry-run", ("--dry-run",)), ("real", ())):
            with self.subTest(mode=label):
                root = self.build(f"base-{label}", homeworks=False)
                outside = self.workspace / f"outside-{label}"
                outside.mkdir()
                link = root / "homeworks"
                link.symlink_to(outside)

                result = self.scaffold(root, flags=flags)

                self.assert_usage_error(result)
                self.assertIn(
                    "homeworks is a symlink; refusing to follow it",
                    result.stderr,
                )
                self.assertTrue(
                    link.is_symlink(), "the symlink must be left intact"
                )
                self.assertEqual(
                    [],
                    sorted(outside.rglob("*")),
                    "nothing may be written through a symlinked homeworks base",
                )

    def test_regular_file_at_intermediate_path_is_conflict(self) -> None:
        target = self.target(self.root)
        target.mkdir(parents=True)
        (target / "src").write_text("keep me\n", encoding="utf-8")

        result = self.scaffold(self.root)

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn(
            "homeworks/1_3-fixture/src/main.cpp: CONFLICT — ", result.stdout
        )
        self.assertIn(
            "intermediate path homeworks/1_3-fixture/src exists and is not "
            "a directory",
            result.stdout,
        )
        self.assertEqual(
            "keep me\n", (target / "src").read_text(encoding="utf-8")
        )
        self.assertEqual(
            ["src"],
            sorted(path.name for path in target.iterdir()),
            "a conflict must block every other write",
        )


class DryRunTests(ScaffoldTestBase):
    """D-21: `--dry-run` is the production algorithm with the write step skipped."""

    def test_dry_run_matches_the_real_run(self) -> None:
        dry_root = self.build("dry")
        real_root = self.build("real")

        dry = self.scaffold(dry_root, flags=("--dry-run",))
        real = self.scaffold(real_root)

        self.assertEqual(dry.returncode, real.returncode)
        self.assertEqual(0, dry.returncode, dry.stdout + dry.stderr)
        self.assertEqual(dry.stdout, real.stdout, "the plans must be identical")
        self.assertFalse(self.target(dry_root).exists())

    def test_dry_run_creates_no_directories(self) -> None:
        root = self.build("fresh", homeworks=False)

        result = self.scaffold(root, flags=("--dry-run",))

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertFalse((root / "homeworks").exists())
        self.assertFalse((root / "homeworks" / HOMEWORK_ID).exists())


class JsonTests(ScaffoldTestBase):
    """D-23: `--json` carries exactly the machine record and is stable."""

    def test_json_records_have_exactly_three_keys(self) -> None:
        root = self.build("fresh", homeworks=False)
        result = self.scaffold(root, flags=("--json", "--dry-run"))
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

        payload = json.loads(result.stdout)

        self.assertIsInstance(payload, list)
        self.assertTrue(payload)
        for record in payload:
            with self.subTest(path=record.get("path")):
                self.assertEqual({"path", "status", "reason"}, set(record))
                self.assertIn(record["status"], ("CREATE", "UNCHANGED"))

    def test_json_records_are_sorted_by_path(self) -> None:
        root = self.build("fresh", homeworks=False)
        result = self.scaffold(root, flags=("--json", "--dry-run"))
        payload = json.loads(result.stdout)

        paths = [record["path"] for record in payload]
        self.assertEqual(sorted(paths), paths)


class ErrorTests(ScaffoldTestBase):
    """D-19 / D-25: every usage or environment fault is exit 2 before a plan."""

    def test_malformed_id_exits_2(self) -> None:
        for invalid in ("police-flasher", "1_3-Police-Flasher", ""):
            with self.subTest(homework_id=invalid):
                result = self.scaffold(self.root, homework_id=invalid)
                self.assert_usage_error(result)

    def test_id_with_path_separator_exits_2(self) -> None:
        for invalid in ("1_3-x/../escape", "1_3-x/y"):
            with self.subTest(homework_id=invalid):
                result = self.scaffold(self.root, homework_id=invalid)
                self.assert_usage_error(result)

    def test_unknown_template_exits_2(self) -> None:
        result = self.scaffold(self.root, template="nosuchtemplate")
        self.assert_usage_error(result)

    def test_template_without_manifest_exits_2(self) -> None:
        shutil.copytree(
            self.root / "templates" / "homework-arduino",
            self.root / "templates" / "homework-nomanifest",
        )
        (self.root / "templates" / "homework-nomanifest" / "template.yaml").unlink()

        result = self.scaffold(self.root, template="nomanifest")

        self.assert_usage_error(result)

    def test_unknown_placeholder_exits_2(self) -> None:
        template = self.root / "templates" / "homework-unknown"
        shutil.copytree(self.root / "templates" / "homework-arduino", template)
        (template / "README.md").write_text(
            "# {{not_a_placeholder}}\n", encoding="utf-8"
        )

        result = self.scaffold(self.root, template="unknown")

        self.assert_usage_error(result)
        self.assertIn("unknown placeholder", result.stderr)

    def test_dollar_brace_exits_2(self) -> None:
        template = self.root / "templates" / "homework-dollar"
        shutil.copytree(self.root / "templates" / "homework-arduino", template)
        (template / "README.md").write_text(
            "${PROJECT_DIR}/main.cpp\n", encoding="utf-8"
        )

        result = self.scaffold(self.root, template="dollar")

        self.assert_usage_error(result)
        self.assertIn("dollar-brace", result.stderr)

    def test_mismatched_rendered_id_is_error(self) -> None:
        template = self.root / "templates" / "homework-mismatch"
        shutil.copytree(self.root / "templates" / "homework-arduino", template)
        homework_yaml = template / "homework.yaml"
        homework_yaml.write_text(
            homework_yaml.read_text(encoding="utf-8").replace(
                'id: "{{homework_id}}"', 'id: "9_9-other"'
            ),
            encoding="utf-8",
        )

        result = self.scaffold(self.root, template="mismatch")

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn(": ERROR — ", result.stdout)
        self.assertIn("does not match", result.stdout)
        self.assertFalse(
            self.target(self.root).exists(),
            "a validation failure must create no target directory",
        )


class DynamicTemplateTests(ScaffoldTestBase):
    """D-19: a template is a new directory, never a CLI change."""

    def test_new_template_directory_is_accepted_without_a_cli_change(self) -> None:
        shutil.copytree(
            self.root / "templates" / "homework-arduino",
            self.root / "templates" / "homework-fixture",
        )

        result = self.scaffold(self.root, template="fixture")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertTrue((self.target(self.root) / "homework.yaml").is_file())


class RepositoryStateTests(ScaffoldTestBase):
    """Acceptance: no test may create a real `homeworks/` directory."""

    def test_repository_homeworks_directory_is_never_created(self) -> None:
        before = (REPO_ROOT / "homeworks").exists()

        self.scaffold(self.root)

        self.assertEqual(
            before,
            (REPO_ROOT / "homeworks").exists(),
            "the suite must scaffold only into temporary roots",
        )


class RendererContractTests(unittest.TestCase):
    """D-19/T-5-01: one non-recursive substitution pass over a closed map.

    These run in process because `scripts.metadata.render` is stdlib-only; that
    property is itself pinned by `ModuleBoundaryTests`.
    """

    def test_substitution_is_one_non_recursive_pass(self) -> None:
        mapping = {"homework_id": "1_3-alpha", "title": "{{homework_id}}"}

        rendered = render("{{title}}", mapping, "README.md")

        self.assertEqual("{{homework_id}}", rendered)

    def test_unknown_token_raises_check_error_naming_it(self) -> None:
        with self.assertRaises(CheckError) as raised:
            render("{{not_a_placeholder}}", {}, "README.md")

        self.assertIn("unknown placeholder", str(raised.exception))
        self.assertIn("not_a_placeholder", str(raised.exception))

    def test_dollar_brace_raises_check_error(self) -> None:
        with self.assertRaises(CheckError) as raised:
            render("${PROJECT_DIR}/main.cpp", {}, "README.md")

        self.assertIn("dollar-brace", str(raised.exception))

    def test_read_text_reports_a_missing_source_as_check_error(self) -> None:
        with tempfile.TemporaryDirectory(prefix="render-") as directory:
            missing = Path(directory) / "absent.md"
            with self.assertRaises(CheckError):
                from scripts.metadata.render import read_text

                read_text(missing, "README.md")


class ModuleBoundaryTests(unittest.TestCase):
    """T-5-28: the generator dependency graph never loads the validation stack.

    The repository test suite is stdlib-only (04/D-14), so the modules that must
    stay PyYAML-free are imported in process while the modules that legitimately
    need PyYAML and jsonschema are inspected as source and exercised once in a
    subprocess with the real dependencies.
    """

    # Module stems (under scripts/metadata/) that must import stdlib only.
    STDLIB_ONLY_MODULES = ("render", "paths", "platformio")
    # Modules that legitimately import PyYAML but never jsonschema.
    PYYAML_ONLY_MODULES = ("yaml_loader",)

    def test_in_process_import_adds_no_validation_stack(self) -> None:
        from scripts.metadata import errors, paths, platformio, render  # noqa: F401

        for forbidden in ("yaml", "jsonschema", "scripts.metadata.contract"):
            with self.subTest(module=forbidden):
                self.assertNotIn(
                    forbidden,
                    sys.modules,
                    f"importing the stdlib-only metadata modules loaded {forbidden}",
                )

    def test_source_imports_are_stdlib_or_scripts(self) -> None:
        for name in self.STDLIB_ONLY_MODULES:
            with self.subTest(module=name):
                roots = _import_roots(METADATA_DIR / f"{name}.py")
                self.assertEqual(
                    set(), roots - sys.stdlib_module_names - {"scripts"}
                )

    def test_yaml_loader_imports_only_pyyaml(self) -> None:
        for name in self.PYYAML_ONLY_MODULES:
            with self.subTest(module=name):
                roots = _import_roots(METADATA_DIR / f"{name}.py")
                self.assertEqual(
                    set(),
                    roots - sys.stdlib_module_names - {"scripts", "yaml"},
                )

    def test_contract_reexports_the_same_objects(self) -> None:
        if shutil.which("uv") is None:
            self.fail(
                "uv is a required repository tool; install it before running "
                "this suite"
            )
        result = subprocess.run(
            [
                "uv",
                "run",
                "--with",
                "PyYAML==6.0.3",
                "--with",
                "jsonschema==4.26.0",
                "python",
                "-c",
                REEXPORT_PROGRAM,
            ],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=180,
            check=False,
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)


REEXPORT_PROGRAM = """
import scripts.metadata.contract as contract
import scripts.metadata.errors as errors
import scripts.metadata.paths as paths
import scripts.metadata.platformio as platformio
import scripts.metadata.render as render
import scripts.metadata.yaml_loader as yaml_loader

assert contract.CheckError is errors.CheckError
assert contract.resolve_root is paths.resolve_root
assert contract.relative_path is paths.relative_path
assert contract.derive_parts is paths.derive_parts
assert contract.StrictSafeLoader is yaml_loader.StrictSafeLoader
assert platformio.CheckError is errors.CheckError
"""


def _import_roots(path: Path) -> set:
    """Return the top-level import roots of *path*, relative imports excluded."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.level or not node.module:
                continue
            roots.add(node.module.split(".")[0])
    return roots


if __name__ == "__main__":
    unittest.main()

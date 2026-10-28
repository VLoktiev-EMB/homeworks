"""Integration tests for scripts/new_homework.

Every test runs the real scaffold through `uv run` against a disposable
repository root built by `scripts.tests.temp_root`, never against the
repository itself, so a failure cannot leave a `homeworks/` directory behind.

The module pins the four META-04 behaviours — scaffold, content idempotency,
`--dry-run` parity and refusal to overwrite — and the declared FOUND-01 paths.
Every scaffolded tree is asserted against the live template it was rendered
from — file-set equality, byte equality for every placeholder-free source and
the substituted documents — so a template edit and a renderer change cannot
drift apart. Every refusal path asserts both the exit code and the absence of
plan output, because "exit 2 before any plan output" is the contract, not just
the status.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.metadata.errors import CheckError
from scripts.metadata.render import render
from scripts.tests import temp_root
from scripts.tests.temp_root import snapshot_tree

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = "scripts/new_homework"
METADATA_DIR = REPO_ROOT / "scripts" / "metadata"

HOMEWORK_ID = "1_3-fixture"
TEMPLATES = ("arduino", "espidf")

# FOUND-01 / D-22: the eight shared paths plus the framework-specific entry
# point. `report.md` is here so a green suite asserts the new artifact rather
# than merely letting it appear (Pitfall 13).
SHARED_PATHS = (
    "platformio.ini",
    "include/.gitkeep",
    "test/test_homework/test_homework.c",
    "assets/.gitkeep",
    "README.md",
    "task.md",
    "report.md",
    "homework.yaml",
)

ENTRY_POINTS = {"arduino": "src/main.cpp", "espidf": "src/main.c"}
LANGUAGES = {"arduino": "cpp", "espidf": "c"}


def declared_paths(template: str) -> tuple:
    """Return the declared FOUND-01 paths for *template*."""
    return (ENTRY_POINTS[template],) + SHARED_PATHS


def authored_template_files(template_dir: Path) -> dict:
    """Return `relative POSIX path -> source path` for every authored file.

    This mirrors the skip rules in `scripts/new_homework`: the root
    `template.yaml` manifest, `.pio/`, a generated `CMakeLists.txt` or
    `compile_commands.json`, and any `sdkconfig.*` other than
    `sdkconfig.defaults` are infrastructure rather than rendered content.
    `GeneratedTemplateOutputTests` pins the same rule against an injected
    template.
    """
    template_dir = Path(template_dir)
    files = {}
    for path in sorted(template_dir.rglob("*"), key=lambda item: item.as_posix()):
        if path.is_symlink() or not path.is_file():
            continue
        relative = path.relative_to(template_dir)
        if relative.as_posix() == "template.yaml":
            continue
        if ".pio" in relative.parts:
            continue
        if relative.name in ("CMakeLists.txt", "compile_commands.json"):
            continue
        if (
            relative.name.startswith("sdkconfig.")
            and relative.name != "sdkconfig.defaults"
        ):
            continue
        files[relative.as_posix()] = path
    return files


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

    def assert_matches_live_template(self, root: Path, template: str) -> None:
        """Assert the scaffolded tree equals the live template plus `task.md`.

        Four checks, in order: the file sets are equal; every template source
        free of a `{{` placeholder is byte-identical to its scaffolded copy;
        no scaffolded file retains a `{{` token; and `homework.yaml` carries
        the template's language, so a wrong `LANGUAGES` entry cannot pass.
        """
        target = self.target(root)
        template_dir = REPO_ROOT / "templates" / f"homework-{template}"
        expected = authored_template_files(template_dir)
        expected["task.md"] = REPO_ROOT / "templates" / "task" / "task.md"
        expected["report.md"] = REPO_ROOT / "templates" / "report" / "report.md"
        actual = snapshot_tree(target)

        self.assertEqual(
            sorted(expected), sorted(actual), "the scaffolded file set differs"
        )

        for relative, source in sorted(expected.items()):
            source_bytes = source.read_bytes()
            if b"{{" in source_bytes:
                continue
            with self.subTest(path=relative):
                self.assertEqual(
                    source_bytes,
                    actual[relative],
                    f"scaffolded/{relative} differs from "
                    f"{source.relative_to(REPO_ROOT).as_posix()}",
                )

        for relative, content in sorted(actual.items()):
            with self.subTest(path=relative):
                self.assertNotIn(
                    "{{", content.decode("utf-8"), "a rendered file kept a token"
                )

        rendered = (target / "homework.yaml").read_text(encoding="utf-8")
        self.assertIn(f"language: {LANGUAGES[template]}", rendered)


class InventoryTests(ScaffoldTestBase):
    """FOUND-01: both templates produce the declared paths."""

    def test_arduino_scaffold_creates_the_declared_paths(self) -> None:
        result = self.scaffold(self.root)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        target = self.target(self.root)
        missing = [
            name for name in declared_paths("arduino") if not (target / name).is_file()
        ]
        self.assertEqual([], missing)

    def test_espidf_scaffold_creates_the_declared_paths(self) -> None:
        result = self.scaffold(self.root, template="espidf")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        target = self.target(self.root)
        missing = [
            name for name in declared_paths("espidf") if not (target / name).is_file()
        ]
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
                self.assertIn(f"language: {LANGUAGES[template]}", text)
                self.assertIn('platformio: "6.2.0"', text)
                self.assertIn('platform: "espressif32@8.0.0"', text)

    def test_rendered_documents_substitute_their_placeholders(self) -> None:
        for template in TEMPLATES:
            root = self.build(f"documents-{template}")
            result = self.scaffold(root, template=template)
            with self.subTest(template=template):
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                target = self.target(root)
                readme = (target / "README.md").read_text(encoding="utf-8")
                task = (target / "task.md").read_text(encoding="utf-8")
                self.assertIn("# Fixture", readme)
                self.assertIn("homework for `1_3-fixture`", readme)
                self.assertIn("# Fixture", task)
                for key in (
                    "source_url:",
                    "retrieved:",
                    "attribution:",
                    "license:",
                ):
                    with self.subTest(document="task.md", key=key):
                        self.assertIn(key, task)
                self.assertNotIn("{{", readme)
                self.assertNotIn("{{", task)

    def test_fresh_root_creates_nested_parents(self) -> None:
        root = self.build("fresh", homeworks=False)
        self.assertFalse((root / "homeworks").exists())

        result = self.scaffold(root)

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        target = self.target(root)
        for relative in ("src", "include", "test/test_homework", "assets"):
            with self.subTest(directory=relative):
                self.assertTrue((target / relative).is_dir())
        for relative in declared_paths("arduino"):
            with self.subTest(file=relative):
                self.assertTrue((target / relative).is_file())


class ReportScaffoldTests(ScaffoldTestBase):
    """D-22: the scaffold composes `report.md` exactly as it composes `task.md`."""

    def test_report_md_is_scaffolded_and_rendered(self) -> None:
        for template in TEMPLATES:
            root = self.build(f"report-{template}")
            result = self.scaffold(root, template=template)
            with self.subTest(template=template):
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                report = self.target(root) / "report.md"
                self.assertTrue(report.is_file(), "the scaffold must write report.md")
                text = report.read_text(encoding="utf-8")
                self.assertNotIn("{{", text)
                self.assertIn("## 1. Title and Metadata", text)

    def test_report_block_is_placeholder_in_both_templates(self) -> None:
        for template in TEMPLATES:
            manifest = (
                REPO_ROOT / "templates" / f"homework-{template}" / "homework.yaml"
            )
            text = manifest.read_text(encoding="utf-8")
            with self.subTest(template=template):
                self.assertIn(
                    "report:\n  path: report.md\n  status: placeholder\n",
                    text,
                )


class GeneratedTemplateOutputTests(ScaffoldTestBase):
    """A generated template tree is not scaffolded as authored content.

    Generating the ESP-IDF compilation database writes `.pio/`, `CMakeLists.txt`,
    `src/CMakeLists.txt` and `sdkconfig.<env>` into the template tree. Rendering
    them would scaffold a binary and generated build files into a new homework,
    so the scaffold skips them; the authored `sdkconfig.defaults` must survive.
    """

    def test_generated_template_entries_are_not_scaffolded(self) -> None:
        template = self.root / "templates" / "homework-espidf"
        (template / ".pio" / "build").mkdir(parents=True, exist_ok=True)
        (template / ".pio" / "build" / "artifact.bin").write_bytes(b"\x80\x00")
        (template / "CMakeLists.txt").write_text("generated\n", encoding="utf-8")
        (template / "src").mkdir(parents=True, exist_ok=True)
        (template / "src" / "CMakeLists.txt").write_text(
            "generated\n", encoding="utf-8"
        )
        (template / "sdkconfig.esp32s3_espidf").write_text(
            "generated\n", encoding="utf-8"
        )
        (template / "compile_commands.json").write_text("[]\n", encoding="utf-8")

        result = self.scaffold(self.root, template="espidf")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        target = self.target(self.root)
        for relative in (
            ".pio",
            "CMakeLists.txt",
            "src/CMakeLists.txt",
            "sdkconfig.esp32s3_espidf",
            "compile_commands.json",
        ):
            with self.subTest(relative=relative):
                self.assertFalse((target / relative).exists(), relative)
        self.assertTrue((target / "sdkconfig.defaults").is_file())


class LiveTemplateParityTests(ScaffoldTestBase):
    """The scaffolded tree equals the live template it read, not a stored copy."""

    def test_arduino_scaffold_matches_its_live_template(self) -> None:
        result = self.scaffold(self.root)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assert_matches_live_template(self.root, "arduino")

    def test_espidf_scaffold_matches_its_live_template(self) -> None:
        result = self.scaffold(self.root, template="espidf")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assert_matches_live_template(self.root, "espidf")


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
        first = snapshot_tree(self.target(self.root))

        result = self.scaffold(self.root)

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual(first, snapshot_tree(self.target(self.root)))


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
        before = snapshot_tree(target)

        result = self.scaffold(self.root, template="espidf")

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("homeworks/1_3-fixture/README.md: CONFLICT — ", result.stdout)
        self.assertFalse(
            (target / "assets" / ".gitkeep").exists(),
            "a blocked run must not recreate the deleted file",
        )
        self.assertEqual(before, snapshot_tree(target), "a blocked run must not write")

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


if __name__ == "__main__":
    unittest.main()

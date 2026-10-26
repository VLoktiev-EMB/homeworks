"""Prove the LFS-pointer guard's behaviour and the workflow contracts.

The generated-views workflow command is asserted, and so are the workflow
trigger keys: yamllint's `truthy` policy relaxes KEY checking, so every workflow
must keep spelling its trigger as the text `on:`.

The guard is behaviour, not text: `check_lfs_pointers.sh` is executed against a
temporary directory so a clean tree, an empty file, a real pointer, a missing
directory and a symlink each have an observed exit status. Grepping a workflow
for the command would only prove that the string exists, so the workflow
assertions here are deliberately limited to the names and commands the YAML must
carry; whether the guard works is proven above by running it.

The suite is stdlib-only (04/D-14): it imports neither PyYAML nor jsonschema and
reads the workflows as plain text.
"""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
GUARD = REPO_ROOT / "scripts" / "ci" / "check_lfs_pointers.sh"
WORKFLOWS = REPO_ROOT / ".github" / "workflows"
GENERATED_VIEWS = WORKFLOWS / "generated-views.yml"
YAMLLINT_POLICY = REPO_ROOT / ".yamllint.yaml"

POINTER = "version https://git-lfs.github.com/spec/v1\noid sha256:" + "0" * 64 + "\nsize 42\n"
TIMEOUT = 30


class LfsPointerGuardTests(unittest.TestCase):
    """The guard's exit status, not the workflow's spelling of it."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    def run_guard(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["bash", str(GUARD), *args],
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
        )

    def test_a_clean_tree_exits_zero(self) -> None:
        (self.root / "index.html").write_text("<html></html>\n", encoding="utf-8")
        result = self.run_guard(str(self.root))
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_an_empty_file_exits_zero(self) -> None:
        (self.root / "empty.png").write_bytes(b"")
        result = self.run_guard(str(self.root))
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_a_pointer_exits_one_and_names_the_file(self) -> None:
        pointer = self.root / "images" / "board.png"
        pointer.parent.mkdir()
        pointer.write_text(POINTER, encoding="utf-8")
        result = self.run_guard(str(self.root))
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn(str(pointer), result.stderr)

    def test_a_missing_directory_exits_two(self) -> None:
        result = self.run_guard(str(self.root / "missing"))
        self.assertEqual(result.returncode, 2, result.stderr)

    def test_a_symlink_is_not_followed(self) -> None:
        outside = self.root / "outside"
        outside.mkdir()
        (outside / "pointer.png").write_text(POINTER, encoding="utf-8")
        site = self.root / "site"
        site.mkdir()
        (site / "link.png").symlink_to(outside / "pointer.png")
        result = self.run_guard(str(site))
        self.assertEqual(result.returncode, 0, result.stderr)


class WorkflowTextTests(unittest.TestCase):
    """The names and commands the YAML must carry; behaviour lives above."""

    def test_generated_views_names_the_check_command(self) -> None:
        text = GENERATED_VIEWS.read_text(encoding="utf-8")
        self.assertIn("python scripts/gen_views.py --all --check", text)


class WorkflowTriggerKeyTests(unittest.TestCase):
    """The YAML policy must never rewrite a workflow's trigger key (D-14).

    yamllint parses the bare `on:` key as a boolean under YAML 1.1, so the three
    workflows produced three `truthy` findings. They are keys, not values, so
    `.yamllint.yaml` disables key checking instead of normalising a scalar.
    These assertions are the durable guard against a later edit that
    "simplifies" a trigger key and breaks the workflow schema; whether a
    workflow file needed an unrelated line-length fix is recorded in the plan
    summary, not asserted here.
    """

    def workflows(self) -> list[Path]:
        return sorted(WORKFLOWS.glob("*.yml"))

    def test_all_three_workflows_declare_a_textual_trigger_key(self) -> None:
        files = self.workflows()
        self.assertEqual(3, len(files), [path.name for path in files])
        for path in files:
            lines = path.read_text(encoding="utf-8").splitlines()
            with self.subTest(workflow=path.name):
                self.assertIn("on:", lines)

    def test_no_workflow_spells_a_trigger_as_a_boolean_key(self) -> None:
        for path in self.workflows():
            with self.subTest(workflow=path.name):
                for number, line in enumerate(
                    path.read_text(encoding="utf-8").splitlines(), start=1
                ):
                    self.assertNotIn(
                        line,
                        ("true:", "false:"),
                        f"{path.name}:{number} spells a trigger as a boolean key",
                    )

    def test_the_policy_relaxes_truthy_keys_and_keeps_boolean_values(self) -> None:
        text = YAMLLINT_POLICY.read_text(encoding="utf-8")
        self.assertIn("check-keys: false", text)
        self.assertIn("allowed-values: ['true', 'false']", text)


if __name__ == "__main__":
    unittest.main()

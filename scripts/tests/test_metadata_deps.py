"""Keep the two dependency declarations from drifting.

D-13 delivers the dependencies twice on purpose: each entry script carries a
PEP 723 inline block that `uv run` resolves, and the `check-metadata` pre-commit
hook builds its own isolated `language: python` environment from
`additional_dependencies`. Two delivery paths, one truth.

This module is stdlib-only and parses the declarations as text — it never
imports PyYAML or jsonschema, because D-14 keeps the repository test suite
dependency-free. A divergence in either direction (a missing pin or an extra
pin) fails, and the hook's `files` pattern is probed from both sides so a
broken expression cannot pass silently. `test_hook_invocation` actually runs
pre-commit: a hook whose text is asserted but never executed can be silently
misconfigured (D-37).
"""

from __future__ import annotations

import ast
import re
import shutil
import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG = REPO_ROOT / ".pre-commit-config.yaml"
ENTRY_SCRIPTS = (
    REPO_ROOT / "scripts" / "check_metadata.py",
    REPO_ROOT / "scripts" / "new_homework",
)
HOOK_ID = "check-metadata"

EXPECTED_PINS = ("PyYAML==6.0.3", "jsonschema==4.26.0")

MATCHING_PATHS = (
    "homeworks/1_3-x/homework.yaml",
    "schema/homework.schema.json",
    "scripts/new_homework",
    "scripts/check_metadata.py",
    "scripts/metadata/contract.py",
)
NON_MATCHING_PATHS = (
    "templates/homework-arduino/homework.yaml",
    "templates/task/task.md",
)


def pep723_block(text):
    """Return the PEP 723 comment block of an entry script."""
    start = text.find("# /// script")
    if start < 0:
        raise AssertionError("entry script has no PEP 723 block")
    end = text.find("# ///", start + len("# /// script"))
    if end < 0:
        raise AssertionError("entry script has an unclosed PEP 723 block")
    return text[start:end]


def extract_pep723(text):
    """Return the declared dependencies and `requires-python` of one script."""
    block = pep723_block(text)
    dependencies = re.search(
        r"^#\s*dependencies\s*=\s*(\[.*\])\s*$", block, re.MULTILINE
    )
    if dependencies is None:
        raise AssertionError("PEP 723 block has no dependencies line")
    version = re.search(
        r'^#\s*requires-python\s*=\s*"([^"]+)"\s*$', block, re.MULTILINE
    )
    if version is None:
        raise AssertionError("PEP 723 block has no requires-python line")
    return {
        "dependencies": list(ast.literal_eval(dependencies.group(1))),
        "requires_python": version.group(1),
    }


def hook_block(text, hook_id=HOOK_ID):
    """Return the YAML lines of one `repo: local` hook."""
    lines = text.splitlines()
    start = None
    for index, line in enumerate(lines):
        if re.match(rf"^\s*-\s+id:\s*{re.escape(hook_id)}\s*$", line):
            start = index
            break
    if start is None:
        raise AssertionError(f"no {hook_id!r} hook in the pre-commit config")
    end = len(lines)
    for index in range(start + 1, len(lines)):
        if re.match(r"^\s*-\s+(id|repo):", lines[index]):
            end = index
            break
    return "\n".join(lines[start:end])


def hook_fields(text, hook_id=HOOK_ID):
    """Parse the scalar fields of one hook without a YAML dependency."""
    block = hook_block(text, hook_id)
    fields = {}
    for key in ("name", "language", "entry", "files", "pass_filenames"):
        match = re.search(rf"^\s+{key}:\s*(.*)$", block, re.MULTILINE)
        fields[key] = match.group(1).strip() if match else None
    dependencies = re.search(
        r"^\s+additional_dependencies:\s*(\[.*\])\s*$", block, re.MULTILINE
    )
    if dependencies is None:
        raise AssertionError("hook has no additional_dependencies list")
    fields["additional_dependencies"] = list(
        ast.literal_eval(dependencies.group(1))
    )
    return fields


def drift(reference, candidate):
    """Return `(missing, extra)` between two dependency declarations."""
    return (
        sorted(set(reference) - set(candidate)),
        sorted(set(candidate) - set(reference)),
    )


class MetadataDependencyTests(unittest.TestCase):
    """D-13: one pin set, two delivery paths, three declarations."""

    def setUp(self) -> None:
        self.config_text = CONFIG.read_text(encoding="utf-8")
        self.hook = hook_fields(self.config_text)
        self.declared = {
            path.name: extract_pep723(path.read_text(encoding="utf-8"))
            for path in ENTRY_SCRIPTS
        }

    def test_both_entry_scripts_declare_the_same_pins(self) -> None:
        sets = {
            name: set(declaration["dependencies"])
            for name, declaration in self.declared.items()
        }
        reference = sets["check_metadata.py"]
        for name, pins in sets.items():
            with self.subTest(script=name):
                missing, extra = drift(reference, pins)
                self.assertEqual([], missing, f"{name} is missing pins: {missing}")
                self.assertEqual([], extra, f"{name} has extra pins: {extra}")
                self.assertEqual(set(EXPECTED_PINS), pins)

    def test_hook_pins_match_the_entry_scripts(self) -> None:
        hook_pins = set(self.hook["additional_dependencies"])
        for name, declaration in self.declared.items():
            with self.subTest(script=name):
                missing, extra = drift(
                    set(declaration["dependencies"]), hook_pins
                )
                self.assertEqual(
                    [], missing, f"the hook is missing pins declared by {name}"
                )
                self.assertEqual(
                    [], extra, f"the hook declares pins absent from {name}"
                )
        self.assertEqual(set(EXPECTED_PINS), hook_pins)

    def test_drift_detects_a_missing_pin(self) -> None:
        # Two-sided: the detector itself must catch a one-sided difference.
        missing, extra = drift(set(EXPECTED_PINS), {"PyYAML==6.0.3"})
        self.assertEqual(["jsonschema==4.26.0"], missing)
        self.assertEqual([], extra)
        self.assertEqual(([], []), drift(set(EXPECTED_PINS), set(EXPECTED_PINS)))

    def test_drift_detects_an_extra_pin(self) -> None:
        missing, extra = drift(
            {"PyYAML==6.0.3"}, {"PyYAML==6.0.3", "jsonschema==4.26.0"}
        )
        self.assertEqual([], missing)
        self.assertEqual(["jsonschema==4.26.0"], extra)

    def test_hook_declares_an_isolated_python_environment(self) -> None:
        self.assertEqual("python", self.hook["language"])
        self.assertEqual("false", self.hook["pass_filenames"])
        self.assertEqual("python scripts/check_metadata.py", self.hook["entry"])

    def test_hook_files_pattern_includes_homeworks_schema_and_scaffold(self) -> None:
        pattern = self.hook["files"]
        self.assertTrue(pattern, "the hook must declare a files pattern")
        compiled = re.compile(pattern)
        for path in MATCHING_PATHS:
            with self.subTest(path=path):
                self.assertIsNotNone(
                    compiled.search(path), f"{path} must trigger the hook"
                )

    def test_hook_files_pattern_excludes_templates(self) -> None:
        compiled = re.compile(self.hook["files"])
        for path in NON_MATCHING_PATHS:
            with self.subTest(path=path):
                self.assertIsNone(
                    compiled.search(path),
                    f"{path} must not trigger the hook: an unrendered template "
                    "is not valid metadata",
                )

    def test_both_entry_scripts_require_python_311_or_newer(self) -> None:
        versions = {
            name: declaration["requires_python"]
            for name, declaration in self.declared.items()
        }
        self.assertEqual(1, len(set(versions.values())), versions)
        for name, value in versions.items():
            with self.subTest(script=name):
                match = re.match(r"^>=\s*(\d+)\.(\d+)$", value)
                self.assertIsNotNone(match, f"{name} has an unusable {value!r}")
                self.assertGreaterEqual(
                    (int(match.group(1)), int(match.group(2))), (3, 11)
                )

    def test_hook_invocation(self) -> None:
        executable = shutil.which("pre-commit")
        if executable is None:
            self.fail(
                "pre-commit is a required repository tool; install it before "
                "running this suite"
            )
        result = subprocess.run(
            [executable, "run", HOOK_ID, "--all-files", "--color=never"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=300,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertNotIn("Failed", result.stdout)


if __name__ == "__main__":
    unittest.main()

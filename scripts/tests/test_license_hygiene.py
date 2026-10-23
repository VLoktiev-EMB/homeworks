"""License hygiene tests for the public repository artifacts.

These tests keep the license boundary honest and irreversible-by-accident PII
out of published legal files:

* ``LICENSE`` carries the MIT grant and exactly one handle-only copyright line.
* ``NOTICE`` carries the third-party attribution and trademark sections.
* ``LICENSES/MIT.txt`` and ``LICENSES/CC-BY-4.0.txt`` carry canonical texts
  under the filenames REUSE requires.
* No published legal file contains the configured git identity.

The identity comparison reads ``git config`` at runtime, so no real name is
ever written into this test or into the plan.
"""

from __future__ import annotations

import shutil
import subprocess
import tomllib
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LICENSE_FILE = REPO_ROOT / "LICENSE"
NOTICE_FILE = REPO_ROOT / "NOTICE"
MIT_TEXT = REPO_ROOT / "LICENSES" / "MIT.txt"
CC_BY_TEXT = REPO_ROOT / "LICENSES" / "CC-BY-4.0.txt"
REUSE_TOML = REPO_ROOT / "REUSE.toml"
DEP5_FILE = REPO_ROOT / ".reuse" / "dep5"

PUBLIC_HANDLE = "VLoktiev-EMB"
COPYRIGHT_LINE = "Copyright (c) 2026 VLoktiev-EMB"

MIT_GRANT_OPENING = "Permission is hereby granted, free of charge"
MIT_NOTICE_CLAUSE = (
    "The above copyright notice and this permission notice shall be included"
)
MIT_WARRANTY_OPENING = 'THE SOFTWARE IS PROVIDED "AS IS"'


def _git_config(key: str) -> str | None:
    """Return a git config value, or ``None`` when it is unset."""
    result = subprocess.run(
        ["git", "config", "--get", key],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    value = result.stdout.strip()
    return value or None


def _run_reuse(*args: str) -> subprocess.CompletedProcess[str]:
    """Run the reuse tool in the repository root."""
    binary = shutil.which("reuse")
    if binary is None:
        raise FileNotFoundError("the reuse tool is not installed")
    return subprocess.run(
        [binary, *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def _spdx_license_map(spdx_text: str) -> dict[str, set[str]]:
    """Map ``FileName`` entries from an SPDX tag-value dump to license ids."""
    mapping: dict[str, set[str]] = {}
    current: str | None = None
    for line in spdx_text.splitlines():
        if line.startswith("FileName:"):
            current = line.split(":", 1)[1].strip()
            mapping.setdefault(current, set())
        elif current is not None and line.startswith("LicenseInfoInFile:"):
            value = line.split(":", 1)[1].strip()
            if value and value != "NONE":
                mapping[current].add(value)
    return mapping


def _annotation_paths(annotation: dict) -> list[str]:
    """Normalise the ``path`` key of a REUSE.toml annotation to a list."""
    paths = annotation.get("path", [])
    if isinstance(paths, str):
        return [paths]
    return list(paths)


def _configured_identities() -> list[tuple[str, str]]:
    """Return ``(key, value)`` pairs for the configured git identity.

    The values are never printed by this module: assertion messages are
    explicit so unittest cannot fall back to rendering a value.
    """
    pairs = []
    for key in ("user.name", "user.email"):
        value = _git_config(key)
        if value is not None:
            pairs.append((key, value))
    return pairs


class ArtifactTestCase(unittest.TestCase):
    """Reads a required artifact, failing the test when it does not exist."""

    def read_artifact(self, path: Path) -> str:
        self.assertTrue(
            path.is_file(),
            f"{path.relative_to(REPO_ROOT).as_posix()} is missing",
        )
        return path.read_text(encoding="utf-8")


class LicenseFileTest(ArtifactTestCase):
    """``LICENSE`` is the MIT grant with one handle-only copyright line."""

    def test_license_starts_with_mit_grant(self) -> None:
        text = self.read_artifact(LICENSE_FILE)
        self.assertEqual(text.splitlines()[0], "MIT License")
        self.assertIn(MIT_GRANT_OPENING, text)
        self.assertIn(MIT_NOTICE_CLAUSE, text)
        self.assertIn(MIT_WARRANTY_OPENING, text)

    def test_license_has_exactly_one_copyright_line(self) -> None:
        text = self.read_artifact(LICENSE_FILE)
        lines = [line.strip() for line in text.splitlines()]
        copyright_lines = [
            line for line in lines if line.lower().startswith("copyright")
        ]
        self.assertEqual(copyright_lines, [COPYRIGHT_LINE])


class NoticeFileTest(ArtifactTestCase):
    """``NOTICE`` carries identity, third-party attribution, and trademarks."""

    def test_notice_names_the_public_handle(self) -> None:
        self.assertIn(PUBLIC_HANDLE, self.read_artifact(NOTICE_FILE))

    def test_notice_has_third_party_attributions_section(self) -> None:
        text = self.read_artifact(NOTICE_FILE)
        self.assertIn("Third-Party Attributions", text)
        self.assertIn("MADR 4.0.0", text)
        self.assertIn("adr/madr", text)
        self.assertIn("MIT", text)
        self.assertIn("Fritzing", text)

    def test_notice_has_trademarks_section(self) -> None:
        text = self.read_artifact(NOTICE_FILE)
        self.assertIn("Trademarks", text)
        for mark in (
            "ESP32",
            "Espressif",
            "STM32",
            "STMicroelectronics",
            "Arduino",
        ):
            with self.subTest(mark=mark):
                self.assertIn(mark, text)


class LicenseTextsTest(ArtifactTestCase):
    """The REUSE-required canonical texts are present and non-trivial."""

    def test_required_license_texts_exist(self) -> None:
        for path in (MIT_TEXT, CC_BY_TEXT):
            with self.subTest(path=path.name):
                self.read_artifact(path)
                self.assertGreater(path.stat().st_size, 500)

    def test_mit_text_carries_the_same_grant_as_license(self) -> None:
        mit_text = self.read_artifact(MIT_TEXT)
        self.assertIn(MIT_GRANT_OPENING, mit_text)
        self.assertIn(MIT_NOTICE_CLAUSE, mit_text)
        self.assertIn(MIT_WARRANTY_OPENING, mit_text)

    def test_cc_by_text_has_canonical_heading(self) -> None:
        self.assertIn(
            "Creative Commons Attribution 4.0 International",
            self.read_artifact(CC_BY_TEXT),
        )


class NoPublishedIdentityTest(ArtifactTestCase):
    """No configured git identity may reach a published legal file."""

    PUBLISHED_FILES = (LICENSE_FILE, NOTICE_FILE)

    def test_handle_is_present_regardless_of_git_config(self) -> None:
        # This assertion must never be skipped: the public handle is the
        # identity the artifacts are required to carry.
        for path in self.PUBLISHED_FILES:
            with self.subTest(path=path.name):
                self.assertIn(PUBLIC_HANDLE, self.read_artifact(path))

    def test_published_files_contain_no_configured_git_identity(self) -> None:
        identities = _configured_identities()
        if not identities:
            self.skipTest("git user.name and user.email are both unset")
        for path in self.PUBLISHED_FILES:
            text = self.read_artifact(path)
            for key, value in identities:
                with self.subTest(path=path.name, key=key):
                    self.assertNotIn(
                        value,
                        text,
                        f"{path.name} contains the configured git {key}",
                    )


class ReuseDeclarationTest(ArtifactTestCase):
    """One ``REUSE.toml`` declares the split and the lint proves coverage.

    The three ``.github/PULL_REQUEST_TEMPLATE/*.md`` files are deliberately
    left on the MIT catch-all: they are contribution machinery, not
    documentation or a report. This suite therefore asserts the declared globs
    rather than re-deriving the OSPO rationale file by file.
    """

    #: Code path that must resolve to MIT.
    CODE_SPOT_CHECK = "./scripts/check_policy.py"

    #: Documentation paths checked when they exist. The docs tree arrives in
    #: plan 01-07, so the list is filtered by presence at run time.
    DOCUMENTATION_SPOT_CHECKS = (
        "./README.md",
        "./.planning/PROJECT.md",
        "./docs/decisions/README.md",
    )

    CC_BY_GLOBS = ("*.md", "docs/**", ".planning/**", "homeworks/**/*.md")

    def _spdx_map(self) -> dict[str, set[str]]:
        self.assertIsNotNone(
            shutil.which("reuse"),
            "the reuse tool is not installed (expected reuse 6.2.0)",
        )
        # ``--no-multiprocessing`` keeps the dump deterministic and runnable
        # in sandboxes that deny POSIX semaphores.
        result = _run_reuse("--no-multiprocessing", "spdx")
        self.assertEqual(
            result.returncode,
            0,
            f"reuse spdx failed:\n{result.stdout}\n{result.stderr}",
        )
        return _spdx_license_map(result.stdout)

    def test_reuse_toml_exists_and_dep5_does_not(self) -> None:
        self.assertTrue(REUSE_TOML.is_file(), "REUSE.toml is missing")
        self.assertFalse(
            DEP5_FILE.exists(),
            ".reuse/dep5 must not coexist with REUSE.toml",
        )

    def test_reuse_lint_passes(self) -> None:
        self.assertIsNotNone(
            shutil.which("reuse"),
            "the reuse tool is not installed (expected reuse 6.2.0)",
        )
        # ``--no-multiprocessing`` keeps the run deterministic and runnable in
        # sandboxes that deny POSIX semaphores.
        result = _run_reuse("--no-multiprocessing", "lint")
        output = result.stdout + result.stderr
        self.assertEqual(result.returncode, 0, f"reuse lint failed:\n{output}")
        self.assertNotIn("no copyright and licensing information", output)

    def test_spdx_dump_separates_code_from_documentation(self) -> None:
        mapping = self._spdx_map()
        self.assertEqual(
            mapping.get(self.CODE_SPOT_CHECK),
            {"MIT"},
            f"{self.CODE_SPOT_CHECK} must resolve to MIT",
        )
        checked = 0
        for path in self.DOCUMENTATION_SPOT_CHECKS:
            if path not in mapping:
                continue
            checked += 1
            with self.subTest(path=path):
                self.assertEqual(
                    mapping[path],
                    {"CC-BY-4.0"},
                    f"{path} must resolve to CC-BY-4.0",
                )
        self.assertGreater(
            checked,
            0,
            "no documentation path was present in the SPDX dump",
        )

    def test_reuse_toml_declares_the_documented_globs(self) -> None:
        data = tomllib.loads(self.read_artifact(REUSE_TOML))
        self.assertEqual(data.get("version"), 1)
        annotations = data.get("annotations", [])
        self.assertTrue(annotations, "REUSE.toml declares no annotations")

        mit_paths: set[str] = set()
        cc_by_paths: set[str] = set()
        for annotation in annotations:
            paths = set(_annotation_paths(annotation))
            license_id = annotation.get("SPDX-License-Identifier")
            if license_id == "MIT":
                mit_paths |= paths
            elif license_id == "CC-BY-4.0":
                cc_by_paths |= paths

        self.assertIn("**", mit_paths, "the MIT catch-all annotation is missing")
        for glob in self.CC_BY_GLOBS:
            with self.subTest(glob=glob):
                self.assertIn(glob, cc_by_paths)

    def test_cc_by_annotations_follow_the_catch_all(self) -> None:
        data = tomllib.loads(self.read_artifact(REUSE_TOML))
        annotations = data.get("annotations", [])
        catch_all = [
            index
            for index, annotation in enumerate(annotations)
            if "**" in _annotation_paths(annotation)
        ]
        cc_by = [
            index
            for index, annotation in enumerate(annotations)
            if annotation.get("SPDX-License-Identifier") == "CC-BY-4.0"
        ]
        self.assertEqual(len(catch_all), 1, "expected exactly one catch-all")
        self.assertTrue(cc_by, "no CC-BY-4.0 annotation found")
        self.assertGreater(
            min(cc_by),
            catch_all[0],
            "CC-BY-4.0 overrides must follow the MIT catch-all "
            "(the last matching annotation wins)",
        )

if __name__ == "__main__":
    unittest.main()

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

import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LICENSE_FILE = REPO_ROOT / "LICENSE"
NOTICE_FILE = REPO_ROOT / "NOTICE"
MIT_TEXT = REPO_ROOT / "LICENSES" / "MIT.txt"
CC_BY_TEXT = REPO_ROOT / "LICENSES" / "CC-BY-4.0.txt"

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


if __name__ == "__main__":
    unittest.main()

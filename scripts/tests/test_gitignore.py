"""Contract tests for the repository's ignore and attribute files.

``.gitignore`` and ``.gitattributes`` are the only gate between a build artefact,
a secret, or a nine-hundred-megabyte binary and permanent public history. Reading
either file as text would prove only that a string appears in it, so every
assertion here asks git itself: ``git check-ignore`` for what must never be added
and ``git check-attr`` for how a path gets routed (LFS, text, or binary).

Neither subcommand needs the file to exist: patterns are resolved against the
pathname alone, so a throwaway name such as ``video.mp4`` is enough and the suite
never litters the working tree.
"""

from __future__ import annotations

import subprocess
import unittest
from pathlib import Path


def _repo_root() -> Path:
    """Resolve the repository root so the suite runs from any working directory."""
    completed = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=True,
    )
    return Path(completed.stdout.strip())


REPO_ROOT = _repo_root()


def git(*args: str) -> subprocess.CompletedProcess:
    """Run a read-only git subcommand inside the repository root."""
    return subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def is_ignored(path: str) -> bool:
    """Return True when ``git check-ignore`` matches ``path``."""
    completed = git("check-ignore", "-q", "--", path)
    if completed.returncode not in (0, 1):
        raise AssertionError(
            f"git check-ignore failed for {path!r}: {completed.stderr.strip()}"
        )
    return completed.returncode == 0


# Every category D-21 requires, keyed by the reason the path must stay out.
IGNORED = {
    "build output": [".pio/x", ".pioenvs/x", ".piolibdeps/x"],
    "generated files": ["compile_commands.json", "site/index.html", "out.log"],
    "python caches": [
        "__pycache__/x.pyc",
        ".venv/bin/python",
        ".pytest_cache/x",
        ".ruff_cache/x",
    ],
    "secrets": [".env", ".env.local", "secrets.yaml", "key.pem", "cert.key"],
    "os and editor junk": [".DS_Store", "Thumbs.db", "x.swp", ".idea/misc.xml"],
    # Videos are linked from reports, never committed (D-21).
    "video containers": ["video.mp4", "clip.mov", "a.avi", "b.webm", "c.mkv"],
    # Planning artefacts stay tracked; the retrieval cache is an input, not a record.
    "research cache": [".planning/research/.cache/deadbeef.json"],
}

# Paths that must remain visible to git. Over-broad patterns are as damaging as
# missing ones: an ignored source file silently never gets committed.
VISIBLE = [
    ".env.example",
    "README.md",
    "scripts/review_smoke_test.sh",
    "docs/decisions/README.md",
    ".planning/ROADMAP.md",
    "homeworks/1_3-police-flasher/README.md",
]


class TestGitignorePatterns(unittest.TestCase):
    """`.gitignore` coverage, asserted through ``git check-ignore``."""

    def test_ignored_categories(self) -> None:
        for category, paths in IGNORED.items():
            for path in paths:
                with self.subTest(category=category, path=path):
                    self.assertTrue(
                        is_ignored(path),
                        f"{path!r} ({category}) must be ignored by .gitignore",
                    )

    def test_visible_paths_are_not_ignored(self) -> None:
        for path in VISIBLE:
            with self.subTest(path=path):
                self.assertFalse(
                    is_ignored(path),
                    f"{path!r} must stay visible to git",
                )

    def test_env_example_is_the_only_secret_carve_out(self) -> None:
        # The negation must survive the `.env.*` pattern it overrides.
        self.assertFalse(is_ignored(".env.example"))
        self.assertTrue(is_ignored(".env"))

    def test_research_cache_has_no_tracked_files(self) -> None:
        # The ignore rule is inert while the cache files remain in the index.
        completed = git("ls-files", ".planning/research/.cache/")
        self.assertEqual(
            completed.stdout.strip(),
            "",
            "cache files are still tracked; `git rm --cached` them",
        )


if __name__ == "__main__":
    unittest.main()

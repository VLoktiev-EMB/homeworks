"""Offline refusal tests for scripts/tag_homework.sh.

The script is the only guard on the human-created ``hw/<id>`` tag: no tag
ruleset exists, so a duplicate or a moved tag can only be prevented by
checking every D-11 precondition before anything is created. These tests run
the real script against a throwaway git repository in a temp directory and
never touch the network — the documented ``TAG_HOMEWORK_SKIP_REMOTE`` override
skips the origin tag lookup and the merged-PR check.

Covered cases:
  * an already-existing tag is refused and left exactly as it was;
  * invalid IDs are rejected before any tag exists;
  * a valid unused ID without a homework directory is refused;
  * the script source contains no forced tag or push invocation.
"""

from __future__ import annotations

import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "tag_homework.sh"
HOMEWORK_ID = "1_3-police-flasher"

# A fixed identity plus isolated system/global config keeps fixture commits
# working on any machine, with or without a configured git user.
GIT_ENV = {
    "GIT_AUTHOR_NAME": "Tag Homework Test",
    "GIT_AUTHOR_EMAIL": "tag-homework@example.invalid",
    "GIT_COMMITTER_NAME": "Tag Homework Test",
    "GIT_COMMITTER_EMAIL": "tag-homework@example.invalid",
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_SYSTEM": os.devnull,
}

# Variables that would redirect git away from the fixture repository.
GIT_REDIRECTS = {
    "GIT_DIR",
    "GIT_WORK_TREE",
    "GIT_INDEX_FILE",
    "GIT_OBJECT_DIRECTORY",
    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    "GIT_COMMON_DIR",
}

FORCE_PATTERN = re.compile(r"(?:^|\s)(?:-f|--force|--force-with-lease)(?=\s|$)")


class TagHomeworkTest(unittest.TestCase):
    """Runs the real script with cwd set to a disposable repository."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="tag-homework-")
        self.addCleanup(self._tmp.cleanup)
        self.fixture = Path(self._tmp.name)
        self._git("init", "--quiet")
        self._git("symbolic-ref", "HEAD", "refs/heads/main")
        self._git("commit", "--allow-empty", "--no-gpg-sign", "-m", "fixture root")

    # -- helpers ---------------------------------------------------------

    def _clean_env(self) -> dict[str, str]:
        env = {k: v for k, v in os.environ.items() if k not in GIT_REDIRECTS}
        env.update(GIT_ENV)
        return env

    def _git(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *args],
            cwd=str(self.fixture),
            env=self._clean_env(),
            capture_output=True,
            text=True,
            check=True,
        )

    def _require_script(self) -> str:
        if not SCRIPT.is_file():
            self.fail(f"{SCRIPT} does not exist yet")
        try:
            return SCRIPT.read_text(encoding="utf-8")
        except OSError as exc:  # pragma: no cover - defensive
            self.fail(f"cannot read {SCRIPT}: {exc}")

    def _add_homework(self, homework_id: str) -> None:
        homework = self.fixture / "homeworks" / homework_id
        homework.mkdir(parents=True)
        (homework / "README.md").write_text("# homework\n", encoding="utf-8")
        self._git("add", "homeworks")
        self._git("commit", "--no-gpg-sign", "-m", f"add {homework_id}")

    def _run(self, *args: str) -> subprocess.CompletedProcess[str]:
        self._require_script()
        env = self._clean_env()
        # The only documented way to keep unit tests offline.
        env["TAG_HOMEWORK_SKIP_REMOTE"] = "1"
        try:
            return subprocess.run(
                [str(SCRIPT), *args],
                cwd=str(self.fixture),
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
        except OSError as exc:
            self.fail(f"cannot execute {SCRIPT}: {exc} (expected mode 755)")

    def _tags(self) -> list[str]:
        output = self._git("tag", "--list").stdout
        return [line for line in output.splitlines() if line]

    def _tag_commit(self, tag: str) -> str:
        return self._git("rev-parse", f"refs/tags/{tag}").stdout.strip()

    # -- cases -----------------------------------------------------------

    def test_existing_tag_is_refused(self) -> None:
        """A tag of exactly that name blocks creation and is never moved."""
        self._add_homework(HOMEWORK_ID)
        self._git("tag", f"hw/{HOMEWORK_ID}")
        before = self._tag_commit(f"hw/{HOMEWORK_ID}")

        result = self._run(HOMEWORK_ID)

        self.assertNotEqual(
            result.returncode, 0, "an existing hw/<id> tag must not be accepted"
        )
        self.assertRegex(
            result.stderr,
            r"(?m)^FAIL\b.*hw/" + re.escape(HOMEWORK_ID),
            "stderr must carry a FAIL line naming the existing tag",
        )
        self.assertEqual(self._tags(), [f"hw/{HOMEWORK_ID}"])
        self.assertEqual(
            self._tag_commit(f"hw/{HOMEWORK_ID}"),
            before,
            "the existing tag must keep pointing at the same commit",
        )

    def test_invalid_ids_are_rejected(self) -> None:
        """Malformed IDs fail as usage errors and create no tag at all."""
        self._add_homework(HOMEWORK_ID)

        for invalid in ("police-flasher", "", "1_3_Police-Flasher"):
            with self.subTest(homework_id=invalid):
                result = self._run(invalid)

                self.assertEqual(
                    result.returncode,
                    2,
                    "an invalid ID is a usage error (exit 2)",
                )
                self.assertRegex(
                    result.stderr,
                    r"(?m)^FAIL\b",
                    "stderr must carry a FAIL line for the rejected ID",
                )
                self.assertEqual(
                    self._tags(), [], "no tag may be created for a rejected ID"
                )

    def test_missing_homework_directory_is_refused(self) -> None:
        """A well-formed ID with no homeworks/<id>/ directory is refused."""
        missing = "9_9-missing-homework"

        result = self._run(missing)

        self.assertEqual(result.returncode, 1, "a failed precondition exits 1")
        self.assertRegex(
            result.stderr,
            r"(?m)^FAIL\b.*homeworks/" + re.escape(missing),
            "stderr must carry a FAIL line naming the missing directory",
        )
        self.assertEqual(self._tags(), [], "no tag may be created when the check fails")

    def test_source_has_no_forced_tag_or_push(self) -> None:
        """The script can never overwrite or move a tag."""
        source = self._require_script()

        self.assertNotIn("--force", source)
        self.assertNotIn("force-with-lease", source)

        for lineno, line in enumerate(source.splitlines(), start=1):
            if FORCE_PATTERN.search(line) and re.search(r"\bgit\b", line):
                self.fail(
                    f"forced git invocation on line {lineno}: {line.strip()!r} "
                    "- tags must never be rewritten"
                )


if __name__ == "__main__":
    unittest.main()

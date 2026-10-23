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
    "secrets": [
        ".env",
        ".env.local",
        "secrets.yaml",
        "key.pem",
        "cert.key",
        # SSH/GPG material has no extension, so `*.key` cannot catch it.
        "id_rsa",
        "id_ed25519",
        "key.ppk",
    ],
    # Regenerable by the ESP-IDF component manager and build system.
    "esp-idf artifacts": [
        "sdkconfig.old",
        "managed_components/espressif__led_strip/led_strip.h",
    ],
    # ESP-IDF writes these into the project tree on the first build (D-23, P6).
    # The two CMake paths are distinct: a pattern for the project-root file does
    # not match the nested `src/` one.
    "esp-idf build-generated (D-23)": [
        "homeworks/1_1-example/CMakeLists.txt",
        "homeworks/1_1-example/src/CMakeLists.txt",
        "homeworks/1_1-example/sdkconfig.esp32s3_espidf",
    ],
    "os and editor junk": [
        ".DS_Store",
        "Thumbs.db",
        "x.swp",
        ".idea/misc.xml",
        # .vscode/* ignores everything except the explicitly re-included files below.
        ".vscode/workspace-specific.json",
    ],
    # Videos are linked from reports, never committed (D-21).
    "video containers": ["video.mp4", "clip.mov", "a.avi", "b.webm", "c.mkv"],
    # Planning artefacts stay tracked; the retrieval cache is an input, not a record.
    "research cache": [".planning/research/.cache/deadbeef.json"],
    # Isolated executor checkouts are transient build state, not repository content.
    "agent worktrees": [".claude/worktrees/agent-abc123/README.md"],
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
    # The canonical rulebook is tracked; only .claude/worktrees/ may be ignored,
    # never the whole .claude/ directory.
    ".claude/CLAUDE.md",
    # VS Code: shared settings, tasks, launch configs and extensions are committable;
    # only the machine-specific remainder under .vscode/ is ignored. Workspace files
    # are deliberately visible so a multi-root workspace can be shared.
    ".vscode/settings.json",
    ".vscode/tasks.json",
    ".vscode/launch.json",
    ".vscode/extensions.json",
    "homeworks.code-workspace",
    "homeworks-all.code-workspace",
    # A Makefile is source, not a build artefact: ignoring it makes a build entry
    # point vanish from every clone with no error anywhere.
    "Makefile",
    # ESP-IDF per-project configuration belongs in version control; only the
    # regenerable artifacts (sdkconfig.old, managed_components/) are ignored.
    "sdkconfig",
    "dependencies.lock",
    # Authored Kconfig fragment: the negation in .gitignore re-includes it after
    # the broad `homeworks/*/sdkconfig.*` pattern (D-23, P7). Plan 02-04 commits it.
    "homeworks/1_1-example/sdkconfig.defaults",
    # A repository-root CMakeLists.txt is authored source. All D-23 CMake patterns
    # are scoped under `homeworks/*/` precisely so a future CMake project is not
    # hidden; this entry fails the suite if a global pattern ever appears.
    "CMakeLists.txt",
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

    def test_sdkconfig_defaults_is_visible_and_env_output_is_not(self) -> None:
        # D-23/P7: the broad `homeworks/*/sdkconfig.*` pattern must not swallow
        # the authored Kconfig fragment, while the per-environment build output
        # must stay out. This is the pair that catches an over-broad pattern.
        # `git check-ignore` resolves patterns against the pathname alone, so the
        # assertions hold before the files exist.
        self.assertFalse(
            is_ignored("homeworks/1_1-example/sdkconfig.defaults"),
            "the authored sdkconfig.defaults must stay visible to git",
        )
        self.assertTrue(
            is_ignored("homeworks/1_1-example/sdkconfig.esp32s3_espidf"),
            "the build-generated sdkconfig.<env> must be ignored",
        )
        # D-04: the shared configuration file is a source of truth, not a product.
        self.assertFalse(
            is_ignored("platformio.shared.ini"),
            "platformio.shared.ini is committed configuration, never ignored",
        )
        self.assertFalse(
            is_ignored("homeworks/1_1-example/README.md"),
            "project documentation must stay visible to git",
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

    def test_lfs_routed_extensions_are_never_ignored(self) -> None:
        # An extension routed to LFS in `.gitattributes` must stay addable. An
        # ignore rule for the same extension silently drops exactly the evidence
        # files the asset policy exists to preserve (ADR-0005 / D-20). This is the
        # invariant a boilerplate `.gitignore` import is most likely to break.
        ignored = [ext for ext in LFS_EXTENSIONS if is_ignored(f"sample.{ext}")]
        self.assertEqual(
            ignored,
            [],
            f"these LFS-routed extensions are ignored by .gitignore: {ignored}",
        )


def check_attr(attribute: str, path: str) -> str:
    """Return git's effective value for ``attribute`` on ``path``.

    Values are git's vocabulary: ``set``, ``unset``, ``unspecified``, ``auto``, or
    the literal assignment (``lfs``). A missing rule reads as ``unspecified``.
    """
    completed = git("check-attr", attribute, "--", path)
    if completed.returncode != 0:
        raise AssertionError(
            f"git check-attr failed for {path!r}: {completed.stderr.strip()}"
        )
    output = completed.stdout.strip()
    marker = f"{path}: {attribute}: "
    if not output.startswith(marker):
        raise AssertionError(f"unexpected git check-attr output: {output!r}")
    return output[len(marker) :]


# D-20: the only extensions allowed to consume LFS quota.
LFS_EXTENSIONS = ["pdf", "step", "stl", "fzz", "zip", "bin", "elf", "vcd"]

# Page-served assets must stay normal git objects: GitHub Pages cannot serve LFS.
PAGE_SERVED_IMAGES = ["png", "jpg", "jpeg", "webp", "svg"]

# Videos are linked from reports, never committed, so they must not reach LFS.
VIDEO_EXTENSIONS = ["mp4", "mov", "avi", "webm", "mkv"]


class TestLfsRouting(unittest.TestCase):
    """`.gitattributes` routing, asserted through ``git check-attr``."""

    def test_declared_extensions_route_to_lfs(self) -> None:
        for extension in LFS_EXTENSIONS:
            path = f"artifact.{extension}"
            with self.subTest(extension=extension):
                self.assertEqual(check_attr("filter", path), "lfs")

    def test_page_served_images_are_not_lfs(self) -> None:
        for extension in PAGE_SERVED_IMAGES:
            path = f"docs/assets/sample.{extension}"
            with self.subTest(extension=extension):
                self.assertNotEqual(check_attr("filter", path), "lfs")

    def test_video_containers_are_not_lfs(self) -> None:
        for extension in VIDEO_EXTENSIONS:
            path = f"report/video.{extension}"
            with self.subTest(extension=extension):
                self.assertNotEqual(check_attr("filter", path), "lfs")

    def test_raster_images_are_binary(self) -> None:
        for extension in ["png", "jpg", "jpeg", "webp"]:
            path = f"docs/assets/sample.{extension}"
            with self.subTest(extension=extension):
                self.assertEqual(check_attr("text", path), "unset")

    def test_svg_is_text_with_lf_endings(self) -> None:
        self.assertEqual(check_attr("text", "docs/assets/sample.svg"), "set")
        self.assertEqual(check_attr("eol", "docs/assets/sample.svg"), "lf")

    def test_markdown_is_lf_text(self) -> None:
        # No markdown-specific rule exists; the global `* text=auto eol=lf` line
        # covers it, which git reports as `auto` rather than `set`.
        self.assertIn(check_attr("text", "reports/report.md"), {"auto", "set"})
        self.assertEqual(check_attr("eol", "reports/report.md"), "lf")


if __name__ == "__main__":
    unittest.main()

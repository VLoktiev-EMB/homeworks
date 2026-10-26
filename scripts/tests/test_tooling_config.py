"""Prove the C/C++ formatting contract is the one that was agreed.

D-05 makes success criterion 1 machine-checked rather than declared. The suite
is stdlib-only (04/D-14): it never imports PyYAML and reads the two committed
files as plain text.

The text assertions are deliberately stricter than a presence check. A later
duplicate override is the obvious way to defeat them, so each invariant must
occur exactly once. The resolved values are proven separately by the pinned
`clang-format --dump-config` gate command, not here: shelling out from a unit
test would make the fast suite depend on a downloaded wheel.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
FORMAT_CONFIG = REPO_ROOT / ".clang-format"
PRECOMMIT_CONFIG = REPO_ROOT / ".pre-commit-config.yaml"
EDITORCONFIG = REPO_ROOT / ".editorconfig"

# D-02 / D-05: the five invariants the committed config must carry exactly once.
FORMAT_INVARIANTS = (
    "IndentWidth: 4",
    "ColumnLimit: 120",
    "UseTab: Never",
    "AfterFunction: true",
    "ReflowComments: false",
)


def _clang_format_hook_block(text: str) -> str:
    """Return the `clang-format` hook block, or an empty string when absent.

    The block starts at the `- id: clang-format` line and ends at the next line
    indented no deeper than that line, so a sibling hook or repo cannot leak in.
    Parsing text avoids importing PyYAML.
    """
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() != "- id: clang-format":
            continue
        indent = len(line) - len(line.lstrip())
        block = [line]
        for following in lines[index + 1 :]:
            if following.strip() and len(following) - len(following.lstrip()) <= indent:
                break
            block.append(following)
        return "\n".join(block)
    return ""


class ClangFormatConfigTests(unittest.TestCase):
    """D-02 and D-05: the config invariants, each declared exactly once."""

    def test_every_format_invariant_is_declared_exactly_once(self) -> None:
        text = FORMAT_CONFIG.read_text(encoding="utf-8")
        for invariant in FORMAT_INVARIANTS:
            with self.subTest(invariant=invariant):
                self.assertEqual(
                    1,
                    text.count(invariant),
                    f"{invariant!r} must appear exactly once in .clang-format",
                )

    def test_no_editorconfig_exists(self) -> None:
        self.assertFalse(
            EDITORCONFIG.exists(),
            "D-03 makes the committed tool configs the only style source; "
            ".editorconfig must not exist",
        )

    def test_the_clang_format_hook_is_check_only(self) -> None:
        block = _clang_format_hook_block(
            PRECOMMIT_CONFIG.read_text(encoding="utf-8")
        )
        self.assertNotEqual("", block, "the clang-format hook is missing")
        self.assertIn("--dry-run --Werror", block)

    def test_the_clang_format_hook_is_scoped_to_c_and_cpp(self) -> None:
        block = _clang_format_hook_block(
            PRECOMMIT_CONFIG.read_text(encoding="utf-8")
        )
        self.assertIn("types_or: [c, c++]", block)
        self.assertIn("args: [-style=file]", block)

    def test_the_hook_runs_at_the_pre_commit_stage_only(self) -> None:
        text = PRECOMMIT_CONFIG.read_text(encoding="utf-8")
        self.assertIn("default_stages: [pre-commit]", text)

    def test_the_hook_repository_is_pinned_to_an_exact_rev(self) -> None:
        text = PRECOMMIT_CONFIG.read_text(encoding="utf-8")
        self.assertIn(
            "repo: https://github.com/pre-commit/mirrors-clang-format", text
        )
        self.assertIn("rev: v23.1.3", text)


CLANGD_PATHS = (
    REPO_ROOT / "templates" / "homework-arduino" / ".clangd",
    REPO_ROOT / "templates" / "homework-espidf" / ".clangd",
    REPO_ROOT / "scripts" / "tests" / "fixtures" / "golden" / "homework-arduino" / ".clangd",
    REPO_ROOT / "scripts" / "tests" / "fixtures" / "golden" / "homework-espidf" / ".clangd",
    REPO_ROOT / "homeworks" / "1_3-police-flasher" / ".clangd",
)

# The complete `CompileFlags.Remove` allowlist measured in 06-RESEARCH.
CLANGD_REMOVE = (
    "-mlongcalls",
    "-mtext-section-literals",
    "-mdisable-hardware-atomics",
    "-fno-tree-switch-conversion",
    "-fno-shrink-wrap",
    "-fstrict-volatile-bitfields",
    "-fmacro-prefix-map=*",
)

CLANGD_SUPPRESS = ("unknown-argument", "drv_unknown_argument")


class ClangdConfigTests(unittest.TestCase):
    """D-16: the per-project fragment carries the verified language-server keys.

    The five committed copies must stay byte-identical so the scaffold, its
    golden tree, and the real homework cannot drift apart.
    """

    def test_every_clangd_copy_is_byte_identical(self) -> None:
        first = CLANGD_PATHS[0].read_bytes()
        for path in CLANGD_PATHS:
            with self.subTest(path=path.relative_to(REPO_ROOT).as_posix()):
                self.assertEqual(
                    first,
                    path.read_bytes(),
                    "every .clangd copy must be byte-identical",
                )

    def test_the_fragment_names_the_compilation_database(self) -> None:
        text = CLANGD_PATHS[0].read_text(encoding="utf-8")
        self.assertEqual(1, text.count("CompilationDatabase: ."))

    def test_the_fragment_queries_the_driver_for_builtin_headers(self) -> None:
        text = CLANGD_PATHS[0].read_text(encoding="utf-8")
        self.assertEqual(1, text.count("BuiltinHeaders: QueryDriver"))

    def test_every_gcc_only_flag_is_removed(self) -> None:
        text = CLANGD_PATHS[0].read_text(encoding="utf-8")
        for flag in CLANGD_REMOVE:
            with self.subTest(flag=flag):
                self.assertIn(f"- {flag}", text)

    def test_both_diagnostics_are_suppressed(self) -> None:
        text = CLANGD_PATHS[0].read_text(encoding="utf-8")
        for diagnostic in CLANGD_SUPPRESS:
            with self.subTest(diagnostic=diagnostic):
                self.assertIn(f"- {diagnostic}", text)


WRAPPER = REPO_ROOT / "scripts" / "clangd-wrapper.sh"


class ClangdWrapperTests(unittest.TestCase):
    """D-17: discover-never-hardcode resolution and a bounded driver allowlist.

    Every case runs the real wrapper under ``bash`` with a temporary HOME and a
    controlled PATH. A fake binary prints a label followed by its argv, one
    argument per line, so the identity of the resolved server and the exact
    forwarded argument list are both observable without touching the real
    toolchain.
    """

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="clangd-wrapper-")
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        self.home = self.root / "home"
        self.home.mkdir()
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.bash = shutil.which("bash") or "/bin/bash"

    def fake_clangd(self, path: Path, label: str) -> Path:
        """Write an executable stand-in that prints its label and argv."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "#!/bin/sh\n"
            f"printf 'LABEL=%s\\n' '{label}'\n"
            'for argument in "$@"; do printf \'%s\\n\' "$argument"; done\n',
            encoding="utf-8",
        )
        path.chmod(0o755)
        return path

    def espressif_binary(self, version: str, label: str) -> Path:
        return self.fake_clangd(
            self.home
            / ".espressif"
            / "tools"
            / "esp-clangd"
            / f"esp-{version}"
            / "esp-clangd"
            / "bin"
            / "clangd",
            label,
        )

    def run_wrapper(
        self, *arguments: str, environment: dict | None = None
    ) -> subprocess.CompletedProcess:
        child = {
            "HOME": str(self.home),
            "PATH": f"{self.bin}:/usr/bin:/bin",
        }
        if environment:
            child.update(environment)
        return subprocess.run(
            [self.bash, str(WRAPPER), *arguments],
            capture_output=True,
            text=True,
            timeout=30,
            env=child,
            check=False,
        )

    def resolved(self, result: subprocess.CompletedProcess) -> tuple[str, list]:
        """Return the fake binary's label and the arguments it received."""
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        lines = result.stdout.splitlines()
        self.assertTrue(lines, "the fake binary printed nothing")
        self.assertTrue(lines[0].startswith("LABEL="), lines[0])
        return lines[0].removeprefix("LABEL="), lines[1:]

    def test_esp_clangd_variable_wins_over_path(self) -> None:
        chosen = self.fake_clangd(self.root / "chosen-clangd", "variable")
        self.fake_clangd(self.bin / "esp-clangd", "path")

        label, _ = self.resolved(
            self.run_wrapper(
                "--version", environment={"ESP_CLANGD": str(chosen)}
            )
        )

        self.assertEqual("variable", label)

    def test_path_binary_is_used_when_the_variable_is_unset(self) -> None:
        self.fake_clangd(self.bin / "esp-clangd", "path")

        label, _ = self.resolved(self.run_wrapper("--version"))

        self.assertEqual("path", label)

    def test_newest_espressif_build_is_chosen_by_version_order(self) -> None:
        self.espressif_binary("9.0.1_20250101", "old")
        self.espressif_binary("21.1.3_20260408", "middle")
        self.espressif_binary("21.1.10_20270101", "newest")

        label, _ = self.resolved(self.run_wrapper("--version"))

        self.assertEqual("newest", label)

    def test_espressif_fallback_survives_set_euo_pipefail(self) -> None:
        """The regression case: absent from PATH, present under $HOME."""
        self.espressif_binary("21.1.3_20260408", "espressif")

        label, _ = self.resolved(self.run_wrapper("--version"))

        self.assertEqual("espressif", label)

    def test_empty_espressif_tree_exits_2_without_a_shell_diagnostic(self) -> None:
        self.bin.mkdir(exist_ok=True)

        result = self.run_wrapper("--version")

        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("FAIL clangd-wrapper:", result.stderr)
        self.assertNotIn(": line ", result.stderr, result.stderr)

    def test_relative_platformio_core_dir_exits_2_naming_the_variable(self) -> None:
        self.fake_clangd(self.bin / "esp-clangd", "path")

        result = self.run_wrapper(
            "--version", environment={"PLATFORMIO_CORE_DIR": "relative/core"}
        )

        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("FAIL clangd-wrapper:", result.stderr)
        self.assertIn("PLATFORMIO_CORE_DIR", result.stderr)
        self.assertEqual("", result.stdout)

    def test_invalid_esp_clangd_exits_2_naming_the_variable(self) -> None:
        missing = self.root / "absent-clangd"
        inert = self.root / "inert-clangd"
        inert.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")

        for label, value in (("missing", missing), ("not-executable", inert)):
            with self.subTest(case=label):
                result = self.run_wrapper(
                    "--version", environment={"ESP_CLANGD": str(value)}
                )
                self.assertEqual(2, result.returncode, result.stderr)
                self.assertIn("FAIL clangd-wrapper:", result.stderr)
                self.assertIn("ESP_CLANGD", result.stderr)

    def test_nothing_resolvable_prints_the_two_step_install_command(self) -> None:
        result = self.run_wrapper("--version")

        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn(
            'mkdir -p "$HOME/.local/bin" && '
            'ln -sf "$PWD/scripts/clangd-wrapper.sh" '
            '"$HOME/.local/bin/clangd-wrapper"',
            result.stderr,
        )
        self.assertIn("docs/standards/vscode.md", result.stderr)

    def test_forwarded_arguments_are_the_two_bounded_globs(self) -> None:
        chosen = self.fake_clangd(self.root / "chosen-clangd", "variable")
        packages = self.home / ".platformio" / "packages"

        _, arguments = self.resolved(
            self.run_wrapper(
                "--version",
                "--check",
                environment={"ESP_CLANGD": str(chosen)},
            )
        )

        self.assertEqual(
            [
                f"--query-driver={packages}/toolchain-*/bin/*,{packages}/tool-*/bin/*",
                "--version",
                "--check",
            ],
            arguments,
        )


if __name__ == "__main__":
    unittest.main()

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

import contextlib
import importlib.machinery
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

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

    def test_a_non_executable_espressif_candidate_exits_2(self) -> None:
        """WR-02: a candidate without its execute bit must never reach exec.

        Executing it would fail with `Permission denied` and exit 1, which the
        documented contract does not allow.
        """
        broken = self.espressif_binary("21.1.3_20260408", "broken")
        broken.chmod(0o644)

        result = self.run_wrapper("--version")

        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("FAIL clangd-wrapper:", result.stderr)
        self.assertNotIn("Permission denied", result.stderr)

    def test_a_non_executable_newest_candidate_falls_back_to_an_executable_one(
        self,
    ) -> None:
        self.espressif_binary("21.1.3_20260408", "usable")
        newest = self.espressif_binary("21.1.10_20270101", "broken")
        newest.chmod(0o644)

        label, _ = self.resolved(self.run_wrapper("--version"))

        self.assertEqual("usable", label)

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


EDITOR_SETTINGS = REPO_ROOT / ".vscode" / "settings.json"
WORKSPACE_FILE = REPO_ROOT / "homeworks.code-workspace"
WORKSPACE_TEMPLATE = REPO_ROOT / "templates" / "views" / "workspace.json.tmpl"

# D-19a: the literal home-relative wrapper path the generator emits.
WRAPPER_PATH_VALUE = "${env:HOME}/.local/bin/clangd-wrapper"

# D-19: exactly the eight keys the editor contract carries.
EXPECTED_EDITOR_KEYS = {
    "clangd.path",
    "clangd.arguments",
    "C_Cpp.intelliSenseEngine",
    "C_Cpp.autocomplete",
    "C_Cpp.errorSquiggles",
    "editor.formatOnSave",
    "[c]",
    "[cpp]",
}

CPPTOOLS_KEYS = (
    "C_Cpp.intelliSenseEngine",
    "C_Cpp.autocomplete",
    "C_Cpp.errorSquiggles",
)


class EditorContractTests(unittest.TestCase):
    """D-19/D-19a: one contract, emitted twice and kept equal by drift.

    Comparing parsed values means formatting cannot create a false failure,
    while the explicit key-set equality closes the hole a plain deep equality
    would leave: deleting a cpptools key from both sides would still compare
    equal, so the expected key set is asserted separately.
    """

    def workspace_settings(self) -> dict:
        document = json.loads(WORKSPACE_FILE.read_text(encoding="utf-8"))
        return document["settings"]

    def single_folder_settings(self) -> dict:
        return json.loads(EDITOR_SETTINGS.read_text(encoding="utf-8"))

    def test_both_files_carry_the_same_settings_object(self) -> None:
        self.assertEqual(self.workspace_settings(), self.single_folder_settings())

    def test_the_settings_key_set_is_exactly_the_eight_expected_keys(self) -> None:
        for label, settings in (
            ("workspace", self.workspace_settings()),
            ("single-folder", self.single_folder_settings()),
        ):
            with self.subTest(target=label):
                self.assertEqual(EXPECTED_EDITOR_KEYS, set(settings))

    def test_cpptools_intellisense_autocomplete_and_squiggles_are_disabled(self) -> None:
        settings = self.workspace_settings()
        for key in CPPTOOLS_KEYS:
            with self.subTest(key=key):
                self.assertEqual("disabled", settings[key])

    def test_format_on_save_is_enabled(self) -> None:
        self.assertIs(True, self.workspace_settings()["editor.formatOnSave"])

    def test_background_index_is_passed(self) -> None:
        self.assertIn(
            "--background-index", self.workspace_settings()["clangd.arguments"]
        )

    def test_clangd_path_is_the_home_relative_wrapper(self) -> None:
        self.assertEqual(WRAPPER_PATH_VALUE, self.workspace_settings()["clangd.path"])

    def test_the_template_carries_no_workspace_scope_variable(self) -> None:
        text = WORKSPACE_TEMPLATE.read_text(encoding="utf-8")
        self.assertNotIn("workspaceFolder", text)
        self.assertNotIn("${", text, "the renderer rejects dollar-brace template text")

    def test_the_template_uses_the_closed_placeholder(self) -> None:
        text = WORKSPACE_TEMPLATE.read_text(encoding="utf-8")
        self.assertEqual(1, text.count("{{clangd_wrapper_path}}"))


TIDY_CONFIG = REPO_ROOT / ".clang-tidy"
TIDY_GUARD = REPO_ROOT / "scripts" / "clang-tidy-db"
TIDY_REMEDY = "pio run -d tests -e native -t compiledb"
TIMEOUT = 60

# D-08a: the pre-push scope is every translation unit the database describes in
# the analysed trees. Headers are not translation units, so both hook patterns
# stop at `.c`; a header is analysed only through a unit that includes it.
PUSH_SCOPE_SAMPLES = (
    "lib/common/src/hex.c",
    "lib/common/src/crc.c",
    "lib/host/src/fake_gpio.c",
)

# The header trees the narrowed patterns must deliberately not reach.
PUSH_OUT_OF_SCOPE_SAMPLES = (
    "lib/common/include/common/hex.h",
    "lib/host/include/host/fake_gpio.h",
    "lib/port/include/port/gpio.h",
)

# 05/D-21: every hook reports; none repairs or filters.
AUTO_CORRECT_FLAGS = ("--fix", "clang-format -i", "--all-lines")


def _hook_block(text: str, hook_id: str) -> str:
    """Return one hook's block, or an empty string when the hook is absent.

    A block starts at `- id: <hook_id>` and ends at the next non-blank line
    indented no deeper than that line, so a sibling hook cannot leak in.
    """
    lines = text.splitlines()
    for index, line in enumerate(lines):
        # A `- id:` line may carry an inline comment, as the gitleaks entry does.
        stripped = line.split("#", 1)[0].strip()
        if stripped != f"- id: {hook_id}":
            continue
        indent = len(line) - len(line.lstrip())
        block = [line]
        for following in lines[index + 1 :]:
            if following.strip() and len(following) - len(following.lstrip()) <= indent:
                break
            block.append(following)
        return "\n".join(block)
    return ""


def _hook_field(block: str, field: str) -> str:
    """Return a hook block's scalar field value, or an empty string."""
    for line in block.splitlines():
        stripped = line.strip()
        if stripped.startswith(f"{field}:"):
            return stripped[len(field) + 1 :].strip()
    return ""


class ClangTidyConfigTests(unittest.TestCase):
    """TOOL-01: the committed policy is the six families, warnings-first."""

    # CR-01: clang-tidy matches `HeaderFilterRegex` against the header's
    # `FileEntry` name. The compile database passes absolute include
    # directories, so the real name is absolute; both forms must match.
    HEADER_FILTER_SAMPLES = (
        "lib/common/include/common/hex.h",
        "lib/host/include/host/fake_gpio.h",
        "lib/port/include/port/gpio.h",
        "homeworks/1_3-police-flasher/lib/pattern/include/pattern/controller.h",
    )

    def test_every_check_family_is_selected(self) -> None:
        text = TIDY_CONFIG.read_text(encoding="utf-8")
        for family in (
            "bugprone-*",
            "cert-*",
            "performance-*",
            "portability-*",
            "readability-*",
            "clang-analyzer-*",
        ):
            with self.subTest(family=family):
                self.assertIn(family, text)

    def test_the_pragma_once_policy_is_disabled(self) -> None:
        text = TIDY_CONFIG.read_text(encoding="utf-8")
        self.assertIn("-portability-avoid-pragma-once", text)

    def test_warnings_are_not_promoted_to_errors(self) -> None:
        text = TIDY_CONFIG.read_text(encoding="utf-8")
        self.assertEqual(1, text.count('WarningsAsErrors: ""'))

    def header_filter(self) -> str:
        text = TIDY_CONFIG.read_text(encoding="utf-8")
        match = re.search(r'^HeaderFilterRegex:\s*"([^"]+)"', text, re.MULTILINE)
        self.assertIsNotNone(match, "HeaderFilterRegex is missing from .clang-tidy")
        return match.group(1)

    def test_the_header_filter_matches_absolute_header_paths(self) -> None:
        """CR-01: the anchored form discarded every diagnostic from a header.

        clang-tidy matches `HeaderFilterRegex` against the header's `FileEntry`
        name, and `tests/compile_commands.json` passes absolute include
        directories, so the real name is absolute. `re.search` mirrors
        clang-tidy's unanchored `Regex::match`; a pattern that only matches the
        repository-relative form fails here for the absolute sample.
        """
        pattern = re.compile(self.header_filter())
        for relative in self.HEADER_FILTER_SAMPLES:
            for candidate in (relative, (REPO_ROOT / relative).as_posix()):
                with self.subTest(path=candidate):
                    self.assertIsNotNone(
                        pattern.search(candidate),
                        f"HeaderFilterRegex {pattern.pattern!r} discards {candidate!r}",
                    )

    def test_the_header_filter_ignores_a_system_header(self) -> None:
        pattern = re.compile(self.header_filter())
        self.assertIsNone(pattern.search("/usr/local/include/stdio.h"))


class ClangTidyDbGuardTests(unittest.TestCase):
    """D-09: the guard owns the missing/stale-database failure.

    Every case runs the real guard with ``--dir`` against a temporary root whose
    mtimes are set explicitly: a fresh fixture on a fast filesystem would pass
    any resolution rule by accident, so the stale cases are only meaningful when
    the database and each input carry a fixed, distinguishable mtime.

    The fixture mirrors the real database's mixed `file` forms: one absolute
    path, one relative to the entry's own `directory`, and one nested relative
    path. Resolving a relative entry against the repository root instead of
    `directory` would miss both relative entries and report a false pass.
    """

    OLD = 1_000_000_000
    NEW = 1_000_100_000

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="clang-tidy-db-")
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name).resolve()
        self.tests = self.root / "tests"
        self.tests.mkdir()
        self.database = self.tests / "compile_commands.json"
        self.absolute_source = self.root / "lib" / "common" / "src" / "hex.c"
        self.absolute_source.parent.mkdir(parents=True)
        self.relative_source = self.tests / "src" / "main.c"
        self.relative_source.parent.mkdir()
        self.unity_source = (
            self.tests / ".pio" / "libdeps" / "native" / "Unity" / "src" / "unity.c"
        )
        self.unity_source.parent.mkdir(parents=True)
        for path in (
            self.root / "platformio.shared.ini",
            self.tests / "platformio.ini",
            self.absolute_source,
            self.relative_source,
            self.unity_source,
        ):
            path.write_text("x", encoding="utf-8")
            self.age(path, self.OLD)
        self.write_database()

    def age(self, path: Path, when: int) -> None:
        os.utime(path, (when, when))

    def entries(self) -> list:
        return [
            {"directory": str(self.tests), "file": str(self.absolute_source)},
            {"directory": str(self.tests), "file": "src/main.c"},
            {
                "directory": str(self.tests),
                "file": ".pio/libdeps/native/Unity/src/unity.c",
            },
        ]

    def write_database(self, raw: str | None = None, when: int | None = None) -> None:
        self.database.write_text(
            raw if raw is not None else json.dumps(self.entries()), encoding="utf-8"
        )
        self.age(self.database, self.NEW if when is None else when)

    def run_guard(self) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(TIDY_GUARD), "--dir", str(self.root)],
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
        )

    def assert_guard_fails(self, result: subprocess.CompletedProcess) -> None:
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("FAIL clang-tidy-db:", result.stdout)
        self.assertIn(TIDY_REMEDY, result.stdout)

    def test_a_missing_database_exits_one_with_the_regeneration_command(self) -> None:
        self.database.unlink()

        result = self.run_guard()

        self.assert_guard_fails(result)
        self.assertIn(str(self.database), result.stdout)

    def test_a_database_older_than_the_test_environment_exits_one(self) -> None:
        self.age(self.tests / "platformio.ini", self.NEW + 1_000)

        self.assert_guard_fails(self.run_guard())

    def test_a_database_older_than_the_shared_configuration_exits_one(self) -> None:
        self.age(self.root / "platformio.shared.ini", self.NEW + 1_000)

        self.assert_guard_fails(self.run_guard())

    def test_a_database_older_than_an_absolute_source_exits_one(self) -> None:
        self.age(self.absolute_source, self.NEW + 1_000)

        result = self.run_guard()

        self.assert_guard_fails(result)
        self.assertIn(str(self.absolute_source), result.stdout)

    def test_a_new_scoped_source_absent_from_the_database_exits_one(self) -> None:
        """WR-01: a new `.c` is invisible to the mtime comparison.

        Its mtime is deliberately older than the database, so only the
        description check can fail this case; an mtime-only guard passes it.
        """
        new_source = self.root / "lib" / "common" / "src" / "new_feature.c"
        new_source.write_text("x", encoding="utf-8")
        self.age(new_source, self.OLD)

        result = self.run_guard()

        self.assert_guard_fails(result)
        self.assertIn("does not describe", result.stdout)
        self.assertIn(str(new_source), result.stdout)

    def test_a_header_absent_from_the_database_is_not_stale(self) -> None:
        """Headers are not translation units, so the database need not name them."""
        header = self.root / "lib" / "common" / "include" / "common" / "hex.h"
        header.parent.mkdir(parents=True)
        header.write_text("x", encoding="utf-8")
        self.age(header, self.NEW + 1_000)

        result = self.run_guard()

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("PASS clang-tidy-db:", result.stdout)

    def test_a_database_older_than_a_relative_source_exits_one(self) -> None:
        """The case that fails if the guard resolves against the root."""
        self.age(self.relative_source, self.NEW + 1_000)

        result = self.run_guard()

        self.assert_guard_fails(result)
        self.assertIn(str(self.relative_source), result.stdout)

    def test_a_relative_entry_that_no_longer_exists_is_skipped(self) -> None:
        self.unity_source.unlink()

        result = self.run_guard()

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("PASS clang-tidy-db:", result.stdout)

    def test_a_fresh_database_exits_zero_with_a_pass_line(self) -> None:
        result = self.run_guard()

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("PASS clang-tidy-db:", result.stdout)

    def test_malformed_json_exits_two_with_an_error_line(self) -> None:
        self.write_database(raw="{not json")

        result = self.run_guard()

        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("ERROR:", result.stderr)

    def test_no_case_writes_a_new_file_into_the_root(self) -> None:
        before = sorted(path.relative_to(self.root) for path in self.root.rglob("*"))

        self.run_guard()
        self.write_database(raw="{not json")
        self.run_guard()

        after = sorted(path.relative_to(self.root) for path in self.root.rglob("*"))
        self.assertEqual(before, after)


CLANG_TIDY_HOOK = REPO_ROOT / "scripts" / "clang-tidy-hook"


class ClangTidyHookWrapperTests(unittest.TestCase):
    """CR-02: a skipped file must never be reported as a checked file.

    cpp-linter-hooks' own entry point hides the output of a passing run, so it
    cannot see the `Skipping ... Compile command not found.` line. The wrapper
    calls `run_clang_tidy` itself; a fake module stands in for the pinned
    package so the suite stays stdlib-only and does not download a toolchain.
    """

    def load(self) -> types.ModuleType:
        loader = importlib.machinery.SourceFileLoader(
            "clang_tidy_hook", str(CLANG_TIDY_HOOK)
        )
        spec = importlib.util.spec_from_loader(loader.name, loader)
        self.assertIsNotNone(spec)
        module = importlib.util.module_from_spec(spec)
        loader.exec_module(module)
        return module

    def invoke(self, retval: int, output: str) -> tuple[int, str, str]:
        module = self.load()
        package = types.ModuleType("cpp_linter_hooks")
        hook = types.ModuleType("cpp_linter_hooks.clang_tidy")
        hook.run_clang_tidy = lambda: (retval, output)
        package.clang_tidy = hook
        stdout, stderr = io.StringIO(), io.StringIO()
        with mock.patch.dict(
            sys.modules,
            {"cpp_linter_hooks": package, "cpp_linter_hooks.clang_tidy": hook},
        ):
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(
                stderr
            ):
                status = module.main()
        return status, stdout.getvalue(), stderr.getvalue()

    def test_a_skipped_file_fails_the_hook(self) -> None:
        status, _, stderr = self.invoke(
            0, "Skipping lib/common/src/hex.c. Compile command not found.\n"
        )

        self.assertEqual(1, status)
        self.assertIn("FAIL clang-tidy:", stderr)
        self.assertIn(TIDY_REMEDY, stderr)

    def test_a_clean_run_passes_quietly(self) -> None:
        status, stdout, stderr = self.invoke(0, "")

        self.assertEqual(0, status)
        self.assertEqual("", stdout)
        self.assertEqual("", stderr)

    def test_a_normal_finding_still_fails_with_its_output(self) -> None:
        status, stdout, _ = self.invoke(1, "hex.c:1:1: warning: something\n")

        self.assertEqual(1, status)
        self.assertIn("warning: something", stdout)

    def test_a_source_absent_from_the_database_is_rejected_before_running(
        self,
    ) -> None:
        """23.1.3 skips an undescribed file silently, so membership is checked."""
        module = self.load()
        with tempfile.TemporaryDirectory(prefix="clang-tidy-db-") as directory:
            root = Path(directory)
            tests = root / "tests"
            tests.mkdir()
            described = tests / "described.c"
            described.write_text("x", encoding="utf-8")
            absent = tests / "absent.c"
            absent.write_text("x", encoding="utf-8")
            (tests / "compile_commands.json").write_text(
                json.dumps([{"directory": str(tests), "file": "described.c"}]),
                encoding="utf-8",
            )

            with self.subTest(case="described"):
                self.assertEqual(
                    [],
                    module.undescribed_sources(
                        ["--compile-commands=tests", str(described)], root=root
                    ),
                )
            with self.subTest(case="absent"):
                self.assertEqual(
                    [str(absent)],
                    module.undescribed_sources(
                        ["--compile-commands=tests", str(absent)], root=root
                    ),
                )

    def test_main_fails_before_running_an_undescribed_source(self) -> None:
        module = self.load()
        with tempfile.TemporaryDirectory(prefix="clang-tidy-db-") as directory:
            tests = Path(directory) / "tests"
            tests.mkdir()
            absent = tests / "absent.c"
            absent.write_text("x", encoding="utf-8")
            (tests / "compile_commands.json").write_text("[]", encoding="utf-8")
            stderr = io.StringIO()
            with mock.patch.object(
                sys,
                "argv",
                ["clang-tidy-hook", f"--compile-commands={tests}", str(absent)],
            ), contextlib.redirect_stderr(stderr):
                status = module.main()

        self.assertEqual(1, status)
        self.assertIn("FAIL clang-tidy:", stderr.getvalue())
        self.assertIn(TIDY_REMEDY, stderr.getvalue())


class HookLayeringTests(unittest.TestCase):
    """TOOL-03 / success criterion 4: the two layers never swap stages."""

    def config(self) -> str:
        return PRECOMMIT_CONFIG.read_text(encoding="utf-8")

    def test_the_default_stage_is_pre_commit_only(self) -> None:
        self.assertIn("default_stages: [pre-commit]", self.config())

    def test_one_install_wires_both_stages(self) -> None:
        self.assertIn(
            "default_install_hook_types: [pre-commit, pre-push]", self.config()
        )

    def test_every_fast_hook_keeps_the_pre_commit_stage(self) -> None:
        """Every hook outside the push pair declares its fast stage explicitly.

        `default_stages` alone cannot guarantee the layering: the pinned
        `pre-commit-hooks` manifest declares `stages: [pre-commit, pre-push,
        manual]` for three of its hooks, and a hook's own stages override the
        default. Declaring the stage twice (RESEARCH Pattern 2) is what keeps
        pre-push down to the two clang-tidy hooks.
        """
        text = self.config()
        for hook_id in (
            "gitleaks",
            "trailing-whitespace",
            "end-of-file-fixer",
            "check-merge-conflict",
            "check-added-large-files",
            "clang-format",
            "ruff-check",
            "markdownlint-cli2",
            "yamllint",
            "no-generated-files",
            "check-architecture",
            "check-metadata",
            "gen-views-check",
        ):
            with self.subTest(hook=hook_id):
                block = _hook_block(text, hook_id)
                self.assertNotEqual("", block, hook_id)
                self.assertIn("stages: [pre-commit]", block)
                self.assertNotIn("stages: [pre-push]", block)

    def test_both_push_hooks_declare_the_pre_push_stage(self) -> None:
        text = self.config()
        for hook_id in ("clang-tidy-db", "clang-tidy"):
            with self.subTest(hook=hook_id):
                block = _hook_block(text, hook_id)
                self.assertNotEqual("", block, hook_id)
                self.assertIn("stages: [pre-push]", block)
                self.assertNotIn("stages: [pre-commit]", block)

    def test_the_guard_precedes_the_clang_tidy_repository(self) -> None:
        text = self.config()
        self.assertLess(
            text.index("- id: clang-tidy-db"),
            text.index("repo: https://github.com/cpp-linter/cpp-linter-hooks"),
        )

    def test_both_push_patterns_reach_every_analysed_source_tree(self) -> None:
        text = self.config()
        for hook_id in ("clang-tidy-db", "clang-tidy"):
            pattern = _hook_field(_hook_block(text, hook_id), "files")
            self.assertNotEqual("", pattern, hook_id)
            for sample in PUSH_SCOPE_SAMPLES:
                with self.subTest(hook=hook_id, path=sample):
                    self.assertIsNotNone(
                        re.search(pattern, sample),
                        f"{pattern!r} does not match {sample!r}",
                    )

    def test_the_guard_and_clang_tidy_patterns_are_identical(self) -> None:
        """CR-02: a guard that fires while clang-tidy stays silent is worse
        than no guard, so both patterns name the same translation-unit scope."""
        text = self.config()
        guard_pattern = _hook_field(_hook_block(text, "clang-tidy-db"), "files")
        tidy_pattern = _hook_field(_hook_block(text, "clang-tidy"), "files")
        self.assertNotEqual("", tidy_pattern)
        self.assertEqual(guard_pattern, tidy_pattern)

    def test_both_push_patterns_exclude_the_header_trees(self) -> None:
        """CR-02: a bare header has no compile command, so it is not in scope.

        The narrowed scope is the honest contract: a header is analysed through
        a translation unit that includes it, never as a file of its own.
        """
        text = self.config()
        for hook_id in ("clang-tidy-db", "clang-tidy"):
            pattern = _hook_field(_hook_block(text, hook_id), "files")
            for sample in PUSH_OUT_OF_SCOPE_SAMPLES:
                with self.subTest(hook=hook_id, path=sample):
                    self.assertIsNone(
                        re.search(pattern, sample),
                        f"{pattern!r} must not match the header {sample!r}",
                    )

    def test_the_clang_tidy_hook_runs_the_skip_failing_wrapper(self) -> None:
        """CR-02: cpp-linter's own entry hides a passing run's output, so a
        skipped file would report success. The entry is the wrapper instead."""
        block = _hook_block(self.config(), "clang-tidy")
        self.assertEqual("python scripts/clang-tidy-hook", _hook_field(block, "entry"))
        self.assertTrue((REPO_ROOT / "scripts" / "clang-tidy-hook").is_file())

    def test_only_the_guard_suppresses_filenames(self) -> None:
        text = self.config()
        self.assertIn("pass_filenames: false", _hook_block(text, "clang-tidy-db"))
        self.assertNotIn("pass_filenames: false", _hook_block(text, "clang-tidy"))

    def test_no_hook_auto_corrects_or_filters_to_all_lines(self) -> None:
        """Only the invocations matter: comments may name the rejected flags."""
        invocations = [
            line.strip()
            for line in self.config().splitlines()
            if line.strip().startswith(("entry:", "args:"))
        ]
        self.assertTrue(invocations, "no hook invocation found")
        for flag in AUTO_CORRECT_FLAGS:
            with self.subTest(flag=flag):
                for invocation in invocations:
                    self.assertNotIn(flag, invocation)


RULEBOOK = REPO_ROOT / "AGENTS.md"
GUIDE = REPO_ROOT / "docs" / "standards" / "vscode.md"

# TOOL-04: the seven hook ids a contributor meets, in stage order.
GUIDE_HOOKS = (
    "gitleaks",
    "clang-format",
    "ruff-check",
    "markdownlint-cli2",
    "yamllint",
    "clang-tidy-db",
    "clang-tidy",
)

# D-06: every linter arrives through pre-commit, so a system install would be
# a contradiction, not a convenience. These are the forms the guide must not
# name; the positive form (`pre-commit install`) is asserted separately.
FORBIDDEN_INSTALLS = (
    "brew install",
    "apt-get install",
    "pip install --user",
    "npm install -g",
)

ENFORCEMENT_TAGS = (
    "[ENFORCED: pre-commit]",
    "[ENFORCED: pre-push]",
    "[ENFORCED: CI]",
    "[ENFORCED: review]",
)


class RulebookAndGuideTests(unittest.TestCase):
    """TOOL-04: the rulebook names the layers, and the guide carries the steps.

    The assertions stay on command substrings and required terms rather than
    full sentences, so ordinary prose editing does not break the test while a
    dropped step still does. The negative assertion is the other half of D-06:
    a guide that named a system package-manager install would contradict the
    pinned-hook delivery path the same repository declares.
    """

    def rulebook(self) -> str:
        return RULEBOOK.read_text(encoding="utf-8")

    def guide(self) -> str:
        return GUIDE.read_text(encoding="utf-8")

    def test_the_rulebook_names_all_four_enforcement_points(self) -> None:
        text = self.rulebook()
        for tag in ENFORCEMENT_TAGS:
            with self.subTest(tag=tag):
                self.assertIn(tag, text)

    def test_the_quality_tooling_section_exists(self) -> None:
        self.assertIn("### Quality tooling", self.rulebook())

    def test_a_routing_row_names_the_onboarding_guide(self) -> None:
        rows = [
            line
            for line in self.rulebook().splitlines()
            if line.startswith("|") and "docs/standards/vscode.md" in line
        ]
        self.assertTrue(rows, "no routing row names docs/standards/vscode.md")

    def test_the_guide_carries_the_two_step_wrapper_command(self) -> None:
        text = self.guide()
        self.assertIn('mkdir -p "$HOME/.local/bin"', text)
        self.assertIn("scripts/clangd-wrapper.sh", text)

    def test_the_guide_installs_both_hook_stages_with_one_command(self) -> None:
        self.assertIn("pre-commit install", self.guide())

    def test_the_guide_names_the_editor_surfaces(self) -> None:
        text = self.guide()
        self.assertIn("Problems", text)
        self.assertIn("format-on-save", text.lower())
        self.assertIn("compiledb", text)

    def test_the_guide_lists_every_hook(self) -> None:
        text = self.guide()
        for hook in GUIDE_HOOKS:
            with self.subTest(hook=hook):
                self.assertIn(hook, text)

    def test_the_guide_names_no_system_package_manager_install(self) -> None:
        text = self.guide()
        for command in FORBIDDEN_INSTALLS:
            with self.subTest(command=command):
                self.assertNotIn(command, text)


if __name__ == "__main__":
    unittest.main()

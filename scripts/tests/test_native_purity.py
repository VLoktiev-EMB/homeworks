"""Prove the native project builds with a host compiler only.

The compilation database is the compile-time evidence behind ARCH-06. Every
translation unit in it must be built by a host compiler, no entry may carry a
target-toolchain or framework include path, and the shared sources must really
appear rather than being skipped by the linker.

Two temporary fixtures record what the compile gate does and does not prove:

* A framework include in ``lib/common`` makes the build fail. That is ARCH-05's
  compile-time half.
* A relative cross-library include (``../../arduino/include/arduino/time.h``)
  compiles and links. The compiler does not enforce that edge; the textual
  checker in ``scripts/check_architecture.py`` does. The second fixture exists
  so the limit is executed instead of only described.

``ConfigurationGuardTests`` repeats one rule from the checker on the real tree:
``host=symlink://`` may appear only under ``[env:native]`` (D-17). The checker
validates configuration as policy; this test guards the committed tree against
regression, so a duplicate rule is deliberate.

Every subprocess call carries a timeout, and a missing ``pio`` fails the test
instead of skipping it: an absent toolchain is a broken proof, not a pass.
"""

from __future__ import annotations

import configparser
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

PIO = "pio"
TIMEOUT_SECONDS = 300

# A compiler basename is a host compiler when it equals one of these or contains
# one of them. ``/usr/bin/gcc`` and ``/usr/bin/clang`` are the observed values.
HOST_COMPILER_MARKERS = ("cc", "gcc", "clang", "clang++", "g++")

# Tokens that may appear in neither the command nor an include flag.
FORBIDDEN_TOKENS = (
    "xtensa",
    "riscv32",
    "esp-idf",
    "framework-arduinoespressif32",
    "toolchain-",
)

# The shared translation units the native build must actually compile. The last
# entry makes the database non-empty even when a library is dropped entirely.
REQUIRED_COMPILED_FILES = (
    "lib/common/src/timing.c",
    "lib/common/src/ring_buffer.c",
    "lib/common/src/crc.c",
    "lib/common/src/hex.c",
    "lib/host/src/fake_time.c",
    "lib/host/src/fake_gpio.c",
    "lib/host/src/fake_i2c.c",
    "lib/host/src/fake_spi.c",
    "lib/host/src/fake_log.c",
    "tests/src/main.c",
)

FRAMEWORK_INCLUDE = "#include <Arduino.h>"
RELATIVE_INCLUDE = '#include "../../arduino/include/arduino/time.h"'

# Build output is never copied: ``.pio/libdeps`` holds ``symlink://`` entries that
# point back into the real tree, and ``compile_commands.json`` is generated.
COPY_IGNORE = shutil.ignore_patterns(".pio", "compile_commands.json")


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
TESTS_DIR = REPO_ROOT / "tests"
DATABASE = TESTS_DIR / "compile_commands.json"


def _require_pio() -> None:
    """Fail, never skip, when PlatformIO is absent (research assumption A6)."""
    if shutil.which(PIO) is None:
        raise AssertionError(
            f"required executable {PIO!r} was not found on PATH; "
            "the native purity proof fails without it and never skips"
        )


def _run_pio(*arguments: str, cwd: Path = REPO_ROOT) -> subprocess.CompletedProcess:
    """Run one PlatformIO command with an explicit timeout."""
    return subprocess.run(
        [PIO, *arguments],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=TIMEOUT_SECONDS,
        check=False,
    )


def _entry_tokens(entry: dict) -> list[str]:
    """Return the argv of one database entry, from ``arguments`` or ``command``."""
    if "arguments" in entry:
        return [str(token) for token in entry["arguments"]]
    return str(entry.get("command", "")).split()


def _resolved_entry_file(entry: dict) -> Path:
    """Resolve an entry's ``file`` against its ``directory`` when it is relative."""
    path = Path(entry["file"])
    if path.is_absolute():
        return path
    return Path(entry["directory"]) / path


def _repo_relative(path: Path) -> str | None:
    """Return ``path`` relative to the repository root, or None when outside it.

    A Unity install may live behind a package-directory symlink, so an entry can
    legitimately resolve outside the repository; such an entry is not a shared
    source and is simply skipped for the required-file assertion.
    """
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return None


def _copy_fixture_tree(root: Path) -> None:
    """Copy the minimum native tree into ``root`` and prove it stayed inside.

    The copy is dereferenced: ``lib/`` is copied without ``symlinks=True`` because
    real ``.pio/libdeps`` links point back into the repository, and following one
    would make the fixture compile the real sources.
    """
    root = root.resolve()
    for name in ("lib", "tests"):
        shutil.copytree(REPO_ROOT / name, root / name, ignore=COPY_IGNORE)
    (root / "scripts").mkdir()
    shutil.copytree(
        REPO_ROOT / "scripts" / "pio", root / "scripts" / "pio", ignore=COPY_IGNORE
    )
    shutil.copy2(REPO_ROOT / "platformio.shared.ini", root / "platformio.shared.ini")

    touched = (
        root / "lib",
        root / "tests",
        root / "scripts" / "pio",
        root / "platformio.shared.ini",
        root / "lib" / "common" / "src" / "timing.c",
    )
    for path in touched:
        resolved = path.resolve()
        if not resolved.is_relative_to(root):
            raise AssertionError(
                f"fixture path escaped the temporary root: {resolved} not under {root}"
            )
        if not resolved.exists():
            raise AssertionError(f"fixture path missing after the copy: {resolved}")


class NativeDatabaseTests(unittest.TestCase):
    """Every database entry is host-only and the shared sources are present."""

    @classmethod
    def setUpClass(cls) -> None:
        _require_pio()
        cls.build = _run_pio(
            "run", "-d", "tests", "-e", "native", "-t", "compiledb"
        )
        cls.database = None
        if cls.build.returncode == 0 and DATABASE.is_file():
            cls.database = json.loads(DATABASE.read_text(encoding="utf-8"))

    def test_compiledb_build_succeeds(self) -> None:
        output = self.build.stdout + self.build.stderr
        self.assertEqual(
            0,
            self.build.returncode,
            msg=f"pio run -t compiledb failed:\n{output[-4000:]}",
        )

    def test_database_is_non_empty_and_every_entry_is_well_formed(self) -> None:
        self.assertIsNotNone(self.database, "tests/compile_commands.json was not written")
        self.assertTrue(self.database, "the compilation database is empty")
        for index, entry in enumerate(self.database):
            with self.subTest(index=index, file=entry.get("file")):
                self.assertIn("file", entry)
                self.assertTrue(
                    "command" in entry or "arguments" in entry,
                    "entry carries neither a command nor an arguments list",
                )

    def test_every_entry_uses_a_host_compiler(self) -> None:
        self.assertIsNotNone(self.database)
        for entry in self.database:
            with self.subTest(file=entry.get("file")):
                tokens = _entry_tokens(entry)
                self.assertTrue(tokens, "entry has an empty command")
                compiler = Path(tokens[0]).name
                self.assertTrue(
                    any(
                        marker == compiler or marker in compiler
                        for marker in HOST_COMPILER_MARKERS
                    ),
                    f"{compiler!r} is not a host compiler",
                )
                for token in tokens:
                    lowered = token.lower()
                    for forbidden in FORBIDDEN_TOKENS:
                        self.assertNotIn(
                            forbidden,
                            lowered,
                            f"target-toolchain or framework token {forbidden!r} "
                            f"in the native command for {entry.get('file')}",
                        )

    def test_required_shared_sources_are_compiled(self) -> None:
        self.assertIsNotNone(self.database)
        compiled = {
            relative
            for entry in self.database
            if (relative := _repo_relative(_resolved_entry_file(entry))) is not None
        }
        for required in REQUIRED_COMPILED_FILES:
            with self.subTest(required=required):
                self.assertIn(
                    required,
                    compiled,
                    f"{required} is absent from the native compilation database",
                )


class _FixtureCase(unittest.TestCase):
    """A temporary copy of the native tree that a fixture can mutate safely."""

    def setUp(self) -> None:
        _require_pio()
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        _copy_fixture_tree(self.root)
        self.timing = self.root / "lib" / "common" / "src" / "timing.c"

    def _append_include(self, line: str) -> None:
        with self.timing.open("a", encoding="utf-8") as stream:
            stream.write("\n" + line + "\n")

    def _build_copy(self) -> subprocess.CompletedProcess:
        """Build the copy through the test runner.

        ``pio run`` cannot compile Unity on a clean tree: PlatformIO generates its
        ``unity_config.h`` only inside the test runner, so the copy is built with
        the same ``pio test`` command the suite uses. The measured property -- a
        framework include fails, a relative cross-library include succeeds -- is
        unchanged.
        """
        return _run_pio("test", "-d", "tests", "-e", "native", cwd=self.root)


class FrameworkIncludeFixtureTests(_FixtureCase):
    """A framework dependency in the pure layer breaks the native build (ARCH-05)."""

    def test_framework_include_fails_the_build(self) -> None:
        self._append_include(FRAMEWORK_INCLUDE)
        completed = self._build_copy()
        output = completed.stdout + completed.stderr
        self.assertNotEqual(
            0,
            completed.returncode,
            "a framework include in lib/common must fail the native build",
        )
        self.assertIn(
            "Arduino.h",
            output,
            "the failure must name the missing framework header",
        )


class RelativeAdapterIncludeFixtureTests(_FixtureCase):
    """Measured limit: the compile gate does not reject a relative cross-library include.

    A relative include such as ``../../arduino/include/arduino/time.h`` compiles
    and links, so the compiler does not enforce the ``common -> port`` edge.
    ``scripts/check_architecture.py`` is the only guard for that edge. This test
    executes the limit so a future claim that the compiler rejects it contradicts
    an executed test (review consensus L949-L950@e77a39d).
    """

    def test_relative_cross_library_include_compiles(self) -> None:
        self._append_include(RELATIVE_INCLUDE)
        completed = self._build_copy()
        output = completed.stdout + completed.stderr
        self.assertEqual(
            0,
            completed.returncode,
            "the measured limit is that a relative cross-library include compiles; "
            f"the copy failed instead:\n{output[-4000:]}",
        )


class ConfigurationGuardTests(unittest.TestCase):
    """``host=symlink://`` appears only under ``[env:native]`` (D-17).

    This deliberately repeats one rule from ``scripts/check_architecture.py``:
    the checker validates configuration as policy, while this test validates the
    committed tree as a regression guard.
    """

    def test_host_symlink_appears_only_under_env_native(self) -> None:
        temporary_roots = [Path(tempfile.gettempdir()).resolve()]
        checked = 0
        for path in REPO_ROOT.rglob("platformio.ini"):
            if ".pio" in path.parts:
                continue
            resolved = path.resolve()
            if any(resolved.is_relative_to(root) for root in temporary_roots):
                continue
            checked += 1
            parser = configparser.ConfigParser(interpolation=None)
            parser.read(path, encoding="utf-8")
            for section in parser.sections():
                for key, value in parser[section].items():
                    if "host=symlink://" not in value:
                        continue
                    with self.subTest(path=str(path), section=section, key=key):
                        self.assertEqual(
                            "env:native",
                            section,
                            "lib/host may be linked only from [env:native]",
                        )
        self.assertGreaterEqual(checked, 1, "no platformio.ini was inspected")


if __name__ == "__main__":
    unittest.main()

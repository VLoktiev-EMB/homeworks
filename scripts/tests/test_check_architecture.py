"""Tests for scripts/check_architecture.py.

The real-tree class exercises the shipped rule set end to end. Every negative
fixture builds the same minimal library tree in a temporary directory, mutates
exactly one property, and points the checker at the copy with ``--dir`` — the
script's only test seam. The baseline fixture is asserted clean first, so a
failing negative case can only be attributed to its mutation.

The fixture tree deliberately mirrors the real shapes: a header-only ``port``,
``common`` sources that include their own headers, adapters that include
framework headers, and one homework project with a multi-line ``lib_deps``
block. A test that passes on a tree the real repository never produces proves
nothing.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import check_architecture

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "check_architecture.py"

ALLOWLIST = Path("scripts") / "architecture" / "allowlist.json"

BASELINE_INI = """\
[env:esp32s3_arduino]
platform = espressif32
framework = arduino
lib_deps =
    port=symlink://../../lib/port
    common=symlink://../../lib/common
    arduino=symlink://../../lib/arduino
"""


def run_checker(*args: str, cwd: Path = REPO_ROOT) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )


def combined(result: subprocess.CompletedProcess) -> str:
    return result.stdout + result.stderr


def git_status() -> str:
    return subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=True,
        timeout=60,
    ).stdout


class RealTreeTests(unittest.TestCase):
    """The shipped tree satisfies the dependency rule the script enforces."""

    def test_real_tree_passes(self):
        result = run_checker()
        self.assertEqual(0, result.returncode, combined(result))
        self.assertIn("PASS includes:", result.stdout)
        self.assertIn("PASS: dependency rule satisfied", result.stdout)

    def test_second_run_is_identical_and_read_only(self):
        before = git_status()
        first = run_checker()
        second = run_checker()
        after = git_status()

        self.assertEqual(0, first.returncode, combined(first))
        self.assertEqual(0, second.returncode, combined(second))
        self.assertEqual(
            (first.returncode, first.stdout, first.stderr),
            (second.returncode, second.stdout, second.stderr),
        )
        self.assertEqual(before, after, "the checker modified the working tree")


class FixtureBase(unittest.TestCase):
    """Shared minimal tree: one well-formed project per scanned owner."""

    def make_tree(self) -> Path:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)

        allowlist = root / ALLOWLIST
        allowlist.parent.mkdir(parents=True)
        allowlist.write_text('{"version": 1, "entries": []}\n', encoding="utf-8")

        port = root / "lib" / "port" / "include" / "port"
        port.mkdir(parents=True)
        (port / "status.h").write_text("#pragma once\n", encoding="utf-8")
        (port / "time.h").write_text(
            '#pragma once\n#include "port/status.h"\n', encoding="utf-8"
        )

        common = root / "lib" / "common"
        (common / "include" / "common").mkdir(parents=True)
        (common / "src").mkdir(parents=True)
        (common / "include" / "common" / "crc.h").write_text(
            '#pragma once\n#include "port/time.h"\n', encoding="utf-8"
        )
        (common / "src" / "crc.c").write_text(
            '#include "common/crc.h"\n', encoding="utf-8"
        )

        host = root / "lib" / "host"
        (host / "include" / "host").mkdir(parents=True)
        (host / "src").mkdir(parents=True)
        (host / "include" / "host" / "fake_time.h").write_text(
            '#pragma once\n#include "port/time.h"\n', encoding="utf-8"
        )
        (host / "src" / "fake_time.c").write_text(
            '#include "host/fake_time.h"\n', encoding="utf-8"
        )

        arduino = root / "lib" / "arduino"
        (arduino / "include" / "arduino").mkdir(parents=True)
        (arduino / "src").mkdir(parents=True)
        (arduino / "include" / "arduino" / "time.h").write_text(
            '#pragma once\n#include "port/time.h"\n', encoding="utf-8"
        )
        (arduino / "src" / "time.c").write_text(
            '#include <Arduino.h>\n#include "arduino/time.h"\n', encoding="utf-8"
        )

        espidf = root / "lib" / "espidf"
        (espidf / "include" / "espidf").mkdir(parents=True)
        (espidf / "src").mkdir(parents=True)
        (espidf / "include" / "espidf" / "time.h").write_text(
            '#pragma once\n#include "port/time.h"\n', encoding="utf-8"
        )
        (espidf / "src" / "time.c").write_text(
            '#include "esp_timer.h"\n#include "espidf/time.h"\n', encoding="utf-8"
        )

        homework = root / "homeworks" / "1_1-example"
        (homework / "src").mkdir(parents=True)
        (homework / "src" / "main.c").write_text(
            '#include "common/crc.h"\n#include "port/time.h"\n', encoding="utf-8"
        )
        (homework / "platformio.ini").write_text(BASELINE_INI, encoding="utf-8")
        return root

    def append(self, root: Path, relative: str, text: str) -> None:
        path = root / relative
        path.write_text(path.read_text(encoding="utf-8") + text, encoding="utf-8")

    def write_allowlist(self, root: Path, body: str) -> None:
        (root / ALLOWLIST).write_text(body, encoding="utf-8")

    def assert_clean(self, root: Path) -> None:
        result = run_checker("--dir", str(root))
        self.assertEqual(0, result.returncode, combined(result))
        self.assertIn("PASS: dependency rule satisfied", result.stdout)

    def assert_violation(self, root: Path, area: str, fragment: str) -> None:
        result = run_checker("--dir", str(root))
        self.assertEqual(1, result.returncode, combined(result))
        self.assertIn(f"FAIL {area}", result.stdout)
        self.assertIn(fragment, combined(result))

    def assert_environment_error(self, root: Path, fragment: str = "") -> None:
        result = run_checker("--dir", str(root))
        self.assertEqual(2, result.returncode, combined(result))
        self.assertIn("ERROR:", result.stderr)
        if fragment:
            self.assertIn(fragment, result.stderr)


class BaselineTests(FixtureBase):
    """The fixture harness itself is sound before any mutation is applied."""

    def test_baseline_fixture_passes(self):
        self.assert_clean(self.make_tree())

    def test_module_may_include_its_own_header(self):
        root = self.make_tree()
        self.append(root, "lib/common/src/crc.c", '#include "common/crc.h"\n')
        self.assert_clean(root)


class IncludeRuleTests(FixtureBase):
    """Every forbidden include shape fails with its rule name."""

    def test_framework_include_in_common_exits_1(self):
        root = self.make_tree()
        self.append(root, "lib/common/src/crc.c", "#include <Arduino.h>\n")
        self.assert_violation(root, "includes", "external")
        self.assert_violation(root, "includes", "lib/common/src/crc.c")

    def test_adapter_include_in_common_exits_1(self):
        root = self.make_tree()
        self.append(root, "lib/common/src/crc.c", '#include "arduino/time.h"\n')
        self.assert_violation(root, "includes", "forbidden project edge common -> arduino")

    def test_port_including_common_exits_1(self):
        root = self.make_tree()
        (root / "lib" / "port" / "src").mkdir()
        (root / "lib" / "port" / "src" / "extra.c").write_text(
            '#include "common/crc.h"\n', encoding="utf-8"
        )
        self.assert_violation(root, "includes", "forbidden project edge port -> common")

    def test_adapter_including_common_exits_1(self):
        root = self.make_tree()
        self.append(root, "lib/arduino/src/time.c", '#include "common/crc.h"\n')
        self.assert_violation(root, "includes", "forbidden project edge arduino -> common")

    def test_host_including_framework_header_exits_1(self):
        root = self.make_tree()
        self.append(root, "lib/host/src/fake_time.c", "#include <Arduino.h>\n")
        self.assert_violation(root, "includes", "external")

    def test_leading_dotdot_escape_exits_1(self):
        root = self.make_tree()
        self.append(root, "lib/common/src/crc.c", '#include "../common/crc.h"\n')
        self.assert_violation(root, "includes", "escape")

    def test_embedded_dotdot_escape_exits_1(self):
        # The bypass review found: the first segment says `common`, so a
        # first-segment-only classifier would call this a harmless self-edge.
        root = self.make_tree()
        self.append(
            root,
            "lib/common/src/crc.c",
            '#include "common/../arduino/include/arduino/time.h"\n',
        )
        result = run_checker("--dir", str(root))
        self.assertEqual(1, result.returncode, combined(result))
        self.assertIn("escape", result.stdout)
        self.assertNotIn("forbidden project edge", result.stdout)

    def test_absolute_include_escapes_exit_1(self):
        root = self.make_tree()
        self.append(root, "lib/common/src/crc.c", '#include "/tmp/anything.h"\n')
        self.assert_violation(root, "includes", "escape")

    def test_windows_absolute_include_escapes_exit_1(self):
        root = self.make_tree()
        self.append(root, "lib/common/src/crc.c", '#include "C:/tools/anything.h"\n')
        self.assert_violation(root, "includes", "escape")

    def test_wide_external_header_in_common_exits_1(self):
        # `<stdlib.h>` is a C standard header but not in the tight `common`
        # set; a future allocation must not ride a broad standard list.
        root = self.make_tree()
        self.append(root, "lib/common/src/crc.c", "#include <stdlib.h>\n")
        self.assert_violation(root, "includes", "external")
        self.assert_violation(root, "includes", "stdlib.h")

    def test_cross_homework_include_exits_1(self):
        root = self.make_tree()
        self.append(
            root,
            "homeworks/1_1-example/src/main.c",
            '#include "homeworks/2_2-other/src/x.h"\n',
        )
        self.assert_violation(root, "includes", "cross-homework")


class BlockingRuleTests(FixtureBase):
    """The denylist sees code and ignores comments, without string confusion."""

    def test_blocking_token_in_common_exits_1(self):
        root = self.make_tree()
        self.append(root, "lib/common/src/crc.c", "unsigned long now(void) { return millis(); }\n")
        self.assert_violation(root, "blocking", "millis(")

    def test_blocking_token_inside_comment_is_ignored(self):
        root = self.make_tree()
        self.append(
            root,
            "lib/common/src/crc.c",
            "// millis() is deliberately not called\n"
            "/* delay(10); sleep(1); */\n",
        )
        self.assert_clean(root)

    def test_commented_out_include_is_not_reported(self):
        root = self.make_tree()
        self.append(root, "lib/common/src/crc.c", "// #include <Arduino.h>\n")
        self.assert_clean(root)

    def test_string_with_double_slash_does_not_hide_following_token(self):
        # A regex stripper would cut the line at `//` inside the string and
        # silently lose the real `millis(` call that follows it.
        root = self.make_tree()
        self.append(
            root,
            "lib/common/src/crc.c",
            'const char *note = "http://example.test // not a comment";\n'
            "unsigned long now(void) { return millis(); }\n",
        )
        self.assert_violation(root, "blocking", "millis(")


class AllowlistTests(FixtureBase):
    """Deny by default, and no allowance can rot into a permanent bypass."""

    def test_allowlisted_violation_passes(self):
        root = self.make_tree()
        self.append(root, "lib/common/src/crc.c", "#include <Arduino.h>\n")
        self.write_allowlist(
            root,
            '{"version": 1, "entries": ['
            '{"path": "lib/common/src/crc.c", "rule": "external", '
            '"reason": "fixture: documents an intentional exception"}'
            "]}\n",
        )
        self.assert_clean(root)

    def test_stale_allowlist_entry_exits_1(self):
        root = self.make_tree()
        self.write_allowlist(
            root,
            '{"version": 1, "entries": ['
            '{"path": "lib/common/src/crc.c", "rule": "blocking", '
            '"reason": "fixture: matches nothing"}'
            "]}\n",
        )
        self.assert_violation(root, "allowlist", "stale")

    def test_empty_allowlist_reason_exits_2(self):
        root = self.make_tree()
        self.write_allowlist(
            root,
            '{"version": 1, "entries": ['
            '{"path": "lib/common/src/crc.c", "rule": "blocking", "reason": "   "}'
            "]}\n",
        )
        self.assert_environment_error(root, "reason")

    def test_unknown_allowlist_rule_exits_2(self):
        root = self.make_tree()
        self.write_allowlist(
            root,
            '{"version": 1, "entries": ['
            '{"path": "lib/common/src/crc.c", "rule": "everything", "reason": "x"}'
            "]}\n",
        )
        self.assert_environment_error(root, "rule")

    def test_malformed_allowlist_exits_2(self):
        root = self.make_tree()
        self.write_allowlist(root, "this is not json\n")
        self.assert_environment_error(root, "JSON")

    def test_missing_lib_directory_exits_2(self):
        root = self.make_tree()
        shutil.rmtree(root / "lib")
        self.assert_environment_error(root, "lib")


class CliContractTests(FixtureBase):
    """The command-line surface and the classifier contract are stable."""

    def test_help_exits_0(self):
        result = run_checker("--help")
        self.assertEqual(0, result.returncode, combined(result))
        self.assertIn("dependency rule", result.stdout)

    def test_unknown_argument_exits_2(self):
        result = run_checker("--no-such-option")
        self.assertEqual(2, result.returncode, combined(result))

    def test_docstring_states_the_classifier_contract(self):
        docstring = check_architecture.__doc__ or ""
        self.assertIn("`..` segment", docstring)
        self.assertIn("absolute", docstring)
        self.assertIn("(path, rule)", docstring)

    def test_config_parser_disables_interpolation(self):
        # `${section.key}` inside a lib_deps value must be read as data, not
        # expanded; interpolation=None is what makes the parse deterministic.
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("interpolation=None", source)

    def test_strip_comments_keeps_strings_and_drops_real_comments(self):
        stripped = check_architecture.strip_comments(
            'const char *s = "http://x"; millis(1); // millis(2)'
        )
        self.assertIn("millis(1)", stripped)
        self.assertNotIn("millis(2)", stripped)
        self.assertIn('"http://x"', stripped)

    def test_classify_treats_every_dotdot_segment_as_an_escape(self):
        cases = (
            "../x.h",
            "./x.h",
            "common/../arduino/include/arduino/time.h",
            "/tmp/anything.h",
            "C:/tools/anything.h",
            "\\\\server\\share\\x.h",
        )
        for name in cases:
            with self.subTest(name=name):
                self.assertEqual(("escape", name), check_architecture.classify(name))

    def test_classify_recognises_project_and_external_names(self):
        self.assertEqual(("project", "port"), check_architecture.classify("port/time.h"))
        self.assertEqual(
            ("external", "Arduino.h"), check_architecture.classify("Arduino.h")
        )


class ConfigRuleTests(FixtureBase):
    """platformio.ini closure, one-adapter and framework rules."""

    def test_two_adapters_in_one_environment_exit_1(self):
        root = self.make_tree()
        (root / "homeworks" / "1_1-example" / "platformio.ini").write_text(
            "[env:esp32s3]\n"
            "platform = espressif32\n"
            "lib_deps =\n"
            "    port=symlink://../../lib/port\n"
            "    arduino=symlink://../../lib/arduino\n"
            "    espidf=symlink://../../lib/espidf\n",
            encoding="utf-8",
        )
        self.assert_violation(root, "config", "more than one adapter")

    def test_host_in_a_non_native_environment_exits_1(self):
        root = self.make_tree()
        (root / "homeworks" / "1_1-example" / "platformio.ini").write_text(
            "[env:esp32s3]\n"
            "platform = espressif32\n"
            "lib_deps =\n"
            "    port=symlink://../../lib/port\n"
            "    host=symlink://../../lib/host\n",
            encoding="utf-8",
        )
        self.assert_violation(root, "config", "'host' in a non-native environment")

    def test_common_without_port_exits_1(self):
        root = self.make_tree()
        (root / "homeworks" / "1_1-example" / "platformio.ini").write_text(
            "[env:esp32s3]\n"
            "platform = espressif32\n"
            "lib_deps =\n"
            "    common=symlink://../../lib/common\n",
            encoding="utf-8",
        )
        self.assert_violation(root, "config", "must also list 'port'")

    def test_multiline_lib_deps_with_one_adapter_and_port_passes(self):
        root = self.make_tree()
        (root / "homeworks" / "1_1-example" / "platformio.ini").write_text(
            "[env:esp32s3_arduino]\n"
            "platform = espressif32\n"
            "framework = arduino\n"
            "lib_deps =\n"
            "    port=symlink://../../lib/port  ; contracts first\n"
            "    common=symlink://../../lib/common\n"
            "    arduino=symlink://../../lib/arduino\n",
            encoding="utf-8",
        )
        self.assert_clean(root)

    def test_native_environment_may_list_host(self):
        root = self.make_tree()
        (root / "homeworks" / "1_1-example" / "platformio.ini").write_text(
            "[env:desktop]\n"
            "platform = native\n"
            "lib_deps =\n"
            "    port=symlink://../../lib/port\n"
            "    host=symlink://../../lib/host\n",
            encoding="utf-8",
        )
        self.assert_clean(root)


    def test_alias_does_not_mask_the_linked_adapter(self):
        # CR-01: `port=` renaming the Arduino adapter used to satisfy the
        # closure rule while the environment never linked `lib/port`.
        root = self.make_tree()
        (root / "homeworks" / "1_1-example" / "platformio.ini").write_text(
            "[env:esp32s3]\n"
            "platform = espressif32\n"
            "lib_deps =\n"
            "    port=symlink://../../lib/arduino\n"
            "    common=symlink://../../lib/common\n",
            encoding="utf-8",
        )
        self.assert_violation(root, "config", "must also list 'port'")

    def test_alias_to_an_adapter_with_a_real_port_passes(self):
        # The other direction of CR-01: a legitimate alias must not be rejected.
        root = self.make_tree()
        (root / "homeworks" / "1_1-example" / "platformio.ini").write_text(
            "[env:esp32s3_arduino]\n"
            "platform = espressif32\n"
            "lib_deps =\n"
            "    hw=symlink://../../lib/arduino\n"
            "    port=symlink://../../lib/port\n"
            "    common=symlink://../../lib/common\n",
            encoding="utf-8",
        )
        self.assert_clean(root)

    def test_target_env_named_like_a_test_is_still_checked(self):
        # WR-01: the name alone must not exempt a firmware environment.
        root = self.make_tree()
        (root / "homeworks" / "1_1-example" / "platformio.ini").write_text(
            "[env:integration_test]\n"
            "platform = espressif32\n"
            "lib_deps =\n"
            "    port=symlink://../../lib/port\n"
            "    arduino=symlink://../../lib/arduino\n"
            "    espidf=symlink://../../lib/espidf\n",
            encoding="utf-8",
        )
        self.assert_violation(root, "config", "more than one adapter")

    def test_extends_target_merely_containing_native_does_not_exempt_host(self):
        # WR-03: only a `native`-prefixed target section counts as native.
        root = self.make_tree()
        (root / "homeworks" / "1_1-example" / "platformio.ini").write_text(
            "[env:esp32s3]\n"
            "extends = base_native_helpers\n"
            "lib_deps =\n"
            "    port=symlink://../../lib/port\n"
            "    host=symlink://../../lib/host\n"
            "[env:base_native_helpers]\n"
            "framework = arduino\n",
            encoding="utf-8",
        )
        self.assert_violation(root, "config", "'host' in a non-native environment")


if __name__ == "__main__":
    unittest.main()

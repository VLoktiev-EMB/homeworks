"""Unit tests for the shared Wokwi merge post action.

``scripts.pio.merge_firmware`` is stdlib-only once the SCons import is guarded,
so this module imports it in process and never spawns a build (04/D-14). The
cases pin the command assembly the promotion depends on (D-12) and the esptool-5
failure modes recorded in F-09: argv order, both offset renderings, per-argument
quoting, the output target, board fallbacks, the two package failures, the
Windows binary name, and the CR-01 status propagation.
"""

from __future__ import annotations

import unittest
from unittest import mock

from scripts.pio.merge_firmware import (
    build_merge_command,
    esptool_binary,
    esptool_directory,
    merge_firmware,
)

BUILD_DIR = "/build/esp32s3_arduino"
ESPTOOL = "/packages/tool-esptool/esptool"


class StubBoardConfig:
    """`BoardConfig().get` over a disposable mapping."""

    def __init__(self, values: dict) -> None:
        self._values = values

    def get(self, key: str, default=None):
        return self._values.get(key, default)


class StubPlatform:
    """`PioPlatform()` with both package surfaces the script touches."""

    def __init__(self, packages: dict | None = None, directories: dict | None = None) -> None:
        self.packages = (
            {"tool-esptool": {"version": "9"}} if packages is None else packages
        )
        self._directories = (
            {"tool-esptool": "/packages/tool-esptool"}
            if directories is None
            else directories
        )

    def get_package_dir(self, name: str):
        return self._directories.get(name)


class StubEnv:
    """The six SCons surfaces the script uses, and nothing else."""

    def __init__(
        self,
        substitutions: dict | None = None,
        extra_images: list | None = None,
        board: dict | None = None,
        platform: StubPlatform | None = None,
        execute_status: int = 0,
    ) -> None:
        self.substitutions = {
            "$BUILD_DIR": BUILD_DIR,
            "$ESP32_APP_OFFSET": "0x10000",
            "$PROGNAME": "firmware",
        }
        if substitutions:
            self.substitutions.update(substitutions)
        self.extra_images = [] if extra_images is None else extra_images
        self.board = StubBoardConfig(
            {"build.mcu": "esp32s3"} if board is None else board
        )
        self.platform = StubPlatform() if platform is None else platform
        self.execute_status = execute_status
        self.executed: list[str] = []

    def subst(self, value: str) -> str:
        for key, replacement in self.substitutions.items():
            value = value.replace(key, replacement)
        return value

    def get(self, key: str, default=None):
        if key == "FLASH_EXTRA_IMAGES":
            return self.extra_images
        return default

    def BoardConfig(self) -> StubBoardConfig:
        return self.board

    def PioPlatform(self) -> StubPlatform:
        return self.platform

    def VerboseAction(self, command: str, message: str) -> str:
        return command

    def Execute(self, command: str) -> int:
        self.executed.append(command)
        return self.execute_status


class MergeCommandTests(unittest.TestCase):
    """The merge argv and its two esptool failure modes, without SCons."""

    def command(self, env: StubEnv, target: str = "src/app.bin") -> list:
        return build_merge_command(env, ESPTOOL, BUILD_DIR, target)

    def test_argv_order(self) -> None:
        command = self.command(StubEnv())

        self.assertEqual(f'"{ESPTOOL}"', command[0])
        self.assertEqual(["--chip", "esp32s3"], command[1:3])
        self.assertLess(
            command.index("merge-bin"), command.index("-o"), "merge-bin must precede -o"
        )
        self.assertEqual("0x10000", command[-2])
        self.assertEqual('"src/app.bin"', command[-1])

    def test_output_target(self) -> None:
        command = self.command(StubEnv())

        self.assertEqual(
            f'"{BUILD_DIR}/firmware.merged.bin"', command[command.index("-o") + 1]
        )

    def test_board_fallbacks(self) -> None:
        explicit = self.command(
            StubEnv(
                board={
                    "build.mcu": "esp32s3",
                    "build.flash_mode": "qio",
                    "upload.flash_size": "8MB",
                }
            )
        )
        self.assertEqual("qio", explicit[explicit.index("--flash-mode") + 1])
        self.assertEqual("8MB", explicit[explicit.index("--flash-size") + 1])

        fallback = self.command(StubEnv(board={}))
        self.assertEqual("dio", fallback[fallback.index("--flash-mode") + 1])
        self.assertEqual("4MB", fallback[fallback.index("--flash-size") + 1])

    def test_integer_offset_renders_hex(self) -> None:
        command = self.command(
            StubEnv(extra_images=[(0x1000, "$BUILD_DIR/bootloader.bin")])
        )

        self.assertIn("0x1000", command)
        self.assertNotIn(4096, command)

    def test_string_offset_passes_through(self) -> None:
        command = self.command(
            StubEnv(extra_images=[("0x8000", "$BUILD_DIR/partitions.bin")])
        )

        self.assertIn("0x8000", command)

    def test_every_image_path_is_quoted(self) -> None:
        command = self.command(
            StubEnv(
                extra_images=[
                    (0x1000, "$BUILD_DIR/bootloader.bin"),
                    ("0x8000", "$BUILD_DIR/partitions.bin"),
                ]
            )
        )

        for path in (
            f"{BUILD_DIR}/bootloader.bin",
            f"{BUILD_DIR}/partitions.bin",
            "src/app.bin",
        ):
            self.assertIn(f'"{path}"', command)

    def test_missing_package_raises_system_exit(self) -> None:
        platform = StubPlatform(packages={})

        with self.assertRaises(SystemExit) as raised:
            esptool_directory(platform)

        message = str(raised.exception)
        self.assertIn("tool-esptool", message)
        self.assertIn("espressif32 8", message)

    def test_unpacked_package_raises_system_exit(self) -> None:
        platform = StubPlatform(
            packages={"tool-esptool": {"version": "9"}},
            directories={"tool-esptool": None},
        )

        with self.assertRaises(SystemExit) as raised:
            esptool_directory(platform)

        message = str(raised.exception)
        self.assertIn("tool-esptool", message)
        self.assertIn("espressif32 8", message)

    def test_windows_binary_name(self) -> None:
        with mock.patch("scripts.pio.merge_firmware.os.name", "nt"):
            self.assertEqual(
                "/packages/tool-esptool/esptool.exe",
                esptool_binary("/packages/tool-esptool"),
            )
        self.assertEqual(
            "/packages/tool-esptool/esptool", esptool_binary("/packages/tool-esptool")
        )


class MergeActionTests(unittest.TestCase):
    """CR-01: a failed ``env.Execute`` must fail the build, not pass silently."""

    def test_failed_merge_raises(self) -> None:
        env = StubEnv(execute_status=1)

        with self.assertRaises(RuntimeError) as raised:
            merge_firmware([], ["src/app.bin"], env)

        message = str(raised.exception)
        self.assertIn("merge-bin", message)
        self.assertIn("status 1", message)
        self.assertIn("firmware.merged.bin", message)

    def test_successful_merge_does_not_raise(self) -> None:
        env = StubEnv(execute_status=0)

        merge_firmware([], ["src/app.bin"], env)

        self.assertEqual(1, len(env.executed))
        self.assertIn("merge-bin", env.executed[0])


if __name__ == "__main__":
    unittest.main()

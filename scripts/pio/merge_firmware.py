"""Merge the bootloader, partition table, and application into one image.

Wokwi needs a complete flash image, and the homework's custom 16 MB partition
table means the application binary alone is not bootable. The script Wokwi
publishes for PlatformIO cannot be used unchanged on espressif32@8.0.0: the
platform renamed the package to ``tool-esptool`` and ships esptool 5, whose
subcommand is ``merge-bin`` and whose flags are ``--flash-mode`` and
``--flash-size``. This post action writes only ``$BUILD_DIR/firmware.merged.bin``.

A homework wires this file through a relative ``post:`` ``extra_scripts`` entry
(``post:../../scripts/pio/merge_firmware.py``), which PlatformIO resolves under
``$PROJECT_DIR``, so ``pio run -d <project>`` loads it. The SCons ``Import`` is
guarded because ``scripts/tests/test_merge_firmware.py`` imports this module in
process; when the import fails the module global ``env`` is ``None`` and nothing
is registered.

``_quote`` wraps one value in double quotes so a repository-controlled build
path containing spaces or tabs stays a single argument. It is not a general
shell-metacharacter sanitizer: an embedded ``$``, a backtick, or a double quote
inside a build path is not neutralized. Repository-controlled paths are the
trust boundary.

The PlatformIO package version is deliberately not parsed: ``package.json``
reports ``2.50400.0`` while ``esptool version`` reports ``5.4.0`` (pitfall 9).

``SCons.Environment.Execute`` returns a status instead of raising, and SCons
reads a Python post action's return value as its status, so a bare call would
leave ``pio run`` green after a failed merge. A non-zero status is therefore
raised as ``RuntimeError``, which SCons converts into a failed build.
"""

from __future__ import annotations

import os
from os.path import join

try:
    Import("env")  # noqa: F821 - provided by PlatformIO/SCons
except NameError:
    env = None


def _quote(value):
    """Quote one argument so a build path containing spaces stays atomic."""
    return f'"{value}"'


def esptool_directory(platform):
    """Return the ``tool-esptool`` directory or fail with a named remedy."""
    if "tool-esptool" not in platform.packages:
        raise SystemExit(
            "merge_firmware: the platform provides no `tool-esptool` package. "
            "The espressif32 8.x platform must provide it; install the platform "
            "packages and rebuild."
        )
    directory = platform.get_package_dir("tool-esptool")
    if directory is None:
        raise SystemExit(
            "merge_firmware: `tool-esptool` is declared but its directory is "
            "missing. The espressif32 8.x platform must provide the package; "
            "install the platform packages and rebuild."
        )
    return directory


def esptool_binary(directory):
    """Return the esptool executable name for this operating system."""
    return join(directory, "esptool.exe" if os.name == "nt" else "esptool")


def build_merge_command(env, esptool, build_dir, target_path):
    """Return the ``esptool merge-bin`` argv; pure, so tests need no SCons."""
    board = env.BoardConfig()
    images = [(offset, env.subst(path)) for offset, path in env.get("FLASH_EXTRA_IMAGES", [])]
    images.append((env.subst("$ESP32_APP_OFFSET"), str(target_path)))

    command = [
        _quote(esptool),
        "--chip",
        board.get("build.mcu", "esp32"),
        "merge-bin",
        "-o",
        _quote(join(build_dir, "firmware.merged.bin")),
        "--flash-mode",
        board.get("build.flash_mode", "dio"),
        "--flash-size",
        board.get("upload.flash_size", "4MB"),
    ]
    for offset, path in images:
        command.append(offset if isinstance(offset, str) else hex(offset))
        command.append(_quote(path))
    return command


def merge_firmware(source, target, env):
    platform = env.PioPlatform()
    esptool = esptool_binary(esptool_directory(platform))
    build_dir = env.subst("$BUILD_DIR")
    merged = join(build_dir, "firmware.merged.bin")

    command = build_merge_command(env, esptool, build_dir, target[0])

    status = env.Execute(
        env.VerboseAction(" ".join(command), "Merging firmware images into " + merged)
    )
    if status:
        raise RuntimeError(
            f"merge_firmware: `esptool merge-bin` failed with status {status}; "
            f"`{merged}` was not written: {' '.join(command)}"
        )


if env is not None:
    # Guard the package at load time: a missing name fails fast, before a long compile.
    esptool_directory(env.PioPlatform())
    env.AddPostAction("$BUILD_DIR/${PROGNAME}.bin", merge_firmware)

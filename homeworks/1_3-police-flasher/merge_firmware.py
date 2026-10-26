"""Merge the bootloader, partition table, and application into one image.

Wokwi needs a complete flash image, and the homework's custom 16 MB partition
table means the application binary alone is not bootable. The script Wokwi
publishes for PlatformIO cannot be used unchanged on espressif32@8.0.0: the
platform renamed the package to ``tool-esptool`` and ships esptool 5, whose
subcommand is ``merge-bin`` and whose flags are ``--flash-mode`` and
``--flash-size``. This post action writes only ``$BUILD_DIR/firmware.merged.bin``.
"""

from os.path import join

Import("env")


def _quote(value):
    """Quote one argument so a build path containing spaces stays atomic."""
    return f'"{value}"'


def merge_firmware(source, target, env):
    board = env.BoardConfig()
    build_dir = env.subst("$BUILD_DIR")
    merged = join(build_dir, "firmware.merged.bin")
    esptool = join(env.PioPlatform().get_package_dir("tool-esptool"), "esptool")

    images = [
        (offset, env.subst(path))
        for offset, path in env.get("FLASH_EXTRA_IMAGES", [])
    ]
    images.append((env.subst("$ESP32_APP_OFFSET"), str(target[0])))

    command = [
        _quote(esptool),
        "--chip",
        board.get("build.mcu", "esp32"),
        "merge-bin",
        "-o",
        _quote(merged),
        "--flash-mode",
        board.get("build.flash_mode", "dio"),
        "--flash-size",
        board.get("upload.flash_size", "4MB"),
    ]
    for offset, path in images:
        command.append(offset if isinstance(offset, str) else hex(offset))
        command.append(_quote(path))

    env.Execute(
        env.VerboseAction(" ".join(command), "Merging firmware images into " + merged)
    )


env.AddPostAction("$BUILD_DIR/${PROGNAME}.bin", merge_firmware)

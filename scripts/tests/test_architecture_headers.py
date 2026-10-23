"""Static contract over the public headers of the shared libraries.

The public headers are the whole API surface a homework sees, so their shape is
asserted as data rather than by compiling: a header that reaches a framework
type would drag that framework into every consumer, and a forgotten header or a
reintroduced stub would otherwise pass unnoticed.

The inventory below is deliberately a constant. Adding a public header requires
updating `HEADERS` in the same change; that coupling is the point, because this
suite cannot tell "a new header" from "the inventory was not updated" on its
own and must not guess.

Each file is checked for: ASCII-only bytes, `#pragma once` as the first
non-empty line, an `extern "C"` guard that opens before the declarations and
closes before its `#endif`, an include set inside the per-library allowance, and
the absence of framework type names.
"""

from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path

INCLUDE = re.compile(r'^\s*#\s*include\s*[<"]([^>"]+)[>"]')

HEADERS = {
    "port": ("status.h", "time.h", "gpio.h", "i2c.h", "spi.h", "log.h"),
    "common": ("timing.h", "ring_buffer.h", "crc.h", "hex.h"),
    "host": ("fake_time.h", "fake_gpio.h", "fake_i2c.h", "fake_spi.h", "fake_log.h"),
    "arduino": ("time.h", "gpio.h", "log.h"),
    "espidf": ("time.h", "gpio.h", "log.h"),
}

# A public header may include its own library's headers and `port`. `port` is
# the only shared edge (`common -> port`); adapters stay on `port` alone. The
# C standard headers are restated per library so this suite independently
# agrees with the checker's `EXTERNAL_OK` table: `port` gets the two it needs
# for fixed-width types, `common` adds `stdbool.h`, and `host` adds `string.h`
# for its capturing sink.
ALLOWED_LIBRARY_INCLUDES = {
    "port": ("port/",),
    "common": ("common/", "port/"),
    "host": ("host/", "port/"),
    "arduino": ("arduino/", "port/"),
    "espidf": ("espidf/", "port/"),
}
ALLOWED_EXTERNAL_INCLUDES = {
    "port": frozenset({"stddef.h", "stdint.h"}),
    "common": frozenset({"stdbool.h", "stddef.h", "stdint.h"}),
    "host": frozenset({"stdbool.h", "stddef.h", "stdint.h", "string.h"}),
    "arduino": frozenset(),
    "espidf": frozenset(),
}

# A framework type name in a public header forces every consumer to compile
# against that framework, which is exactly what the adapter layer exists to
# prevent (ARCH-07, D-10).
BANNED_TYPE_NAMES = (
    "Arduino.h",
    "esp_err_t",
    "gpio_num_t",
    "esp_log_level_t",
    "esp_timer",
    "class ",
)

EXPECTED_HEADER_COUNT = 21


def _repo_root() -> Path:
    completed = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=True,
        timeout=60,
    )
    return Path(completed.stdout.strip())


REPO_ROOT = _repo_root()


def discovered_headers() -> dict[str, list[str]]:
    """Map each library to the sorted public headers found under include/."""
    found = {}
    for library in HEADERS:
        include_root = REPO_ROOT / "lib" / library / "include"
        files = sorted(
            path for path in include_root.rglob("*.h") if path.is_file()
        )
        found[library] = [path.name for path in files]
    return found


def header_paths() -> dict[str, list[Path]]:
    paths = {}
    for library in HEADERS:
        include_root = REPO_ROOT / "lib" / library / "include"
        paths[library] = sorted(
            path for path in include_root.rglob("*.h") if path.is_file()
        )
    return paths


def first_non_empty_line(text: str) -> str:
    for line in text.splitlines():
        if line.strip():
            return line.strip()
    return ""


def include_names(text: str) -> list[str]:
    return [
        match.group(1)
        for line in text.splitlines()
        if (match := INCLUDE.match(line))
    ]


class HeaderInventoryTests(unittest.TestCase):
    """The public surface is exactly the reviewed set of 21 headers."""

    def test_discovered_headers_match_the_constant(self):
        discovered = discovered_headers()
        for library, expected in HEADERS.items():
            with self.subTest(library=library):
                self.assertEqual(
                    sorted(expected),
                    discovered[library],
                    f"{library}: update HEADERS in this module when adding a header",
                )

    def test_total_header_count_is_21(self):
        total = sum(len(names) for names in discovered_headers().values())
        self.assertEqual(EXPECTED_HEADER_COUNT, total)


class HeaderShapeTests(unittest.TestCase):
    """Every public header is ASCII, guarded and self-contained."""

    def test_each_header_is_ascii_and_starts_with_pragma_once(self):
        for library, paths in header_paths().items():
            for path in paths:
                with self.subTest(library=library, header=path.name):
                    data = path.read_bytes()
                    self.assertTrue(
                        all(byte < 0x80 for byte in data),
                        f"{path} contains a non-ASCII byte",
                    )
                    text = data.decode("ascii")
                    self.assertEqual("#pragma once", first_non_empty_line(text))

    def test_each_header_has_a_complete_extern_c_guard(self):
        for library, paths in header_paths().items():
            for path in paths:
                with self.subTest(library=library, header=path.name):
                    text = path.read_text(encoding="ascii")
                    guard = text.find("#ifdef __cplusplus")
                    extern = text.find('extern "C" {')
                    self.assertNotEqual(-1, guard, "missing #ifdef __cplusplus")
                    self.assertNotEqual(-1, extern, 'missing extern "C" {')
                    self.assertLess(guard, extern, "the guard must open first")
                    # The guard is two blocks: the first opens the extern "C"
                    # scope and ends in its own `#endif`; the second closes the
                    # scope with `}` and then `#endif`. Looking for the first
                    # `#endif` after `extern` would find the opening one.
                    closing_guard = text.find("#ifdef __cplusplus", extern)
                    self.assertNotEqual(
                        -1, closing_guard, "missing the closing #ifdef __cplusplus"
                    )
                    endif = text.find("#endif", closing_guard)
                    self.assertNotEqual(
                        -1, endif, 'the extern "C" block has no closing #endif'
                    )
                    closing = text.rfind("}", closing_guard, endif)
                    self.assertNotEqual(
                        -1,
                        closing,
                        'the extern "C" block is not closed before #endif',
                    )

    def test_no_header_leaks_a_framework_type_name(self):
        for library, paths in header_paths().items():
            for path in paths:
                text = path.read_text(encoding="ascii")
                for name in BANNED_TYPE_NAMES:
                    with self.subTest(library=library, header=path.name, name=name):
                        self.assertNotIn(name, text)


class HeaderIncludeSetTests(unittest.TestCase):
    """A public header includes only its own library, `port`, or a tight set."""

    def test_includes_stay_inside_the_per_library_allowance(self):
        for library, paths in header_paths().items():
            prefixes = ALLOWED_LIBRARY_INCLUDES[library]
            external = ALLOWED_EXTERNAL_INCLUDES[library]
            for path in paths:
                text = path.read_text(encoding="ascii")
                for name in include_names(text):
                    with self.subTest(library=library, header=path.name, include=name):
                        if "/" in name:
                            self.assertTrue(
                                name.startswith(prefixes),
                                f"{library}/{path.name} includes {name!r}, "
                                f"outside {prefixes}",
                            )
                        else:
                            self.assertIn(
                                name,
                                external,
                                f"{library}/{path.name} includes <{name}>, "
                                "which is not in the public allowance",
                            )

    def test_no_public_header_includes_a_framework_header(self):
        framework = ("Arduino.h", "esp_", "driver/", "freertos/")
        for library, paths in header_paths().items():
            for path in paths:
                text = path.read_text(encoding="ascii")
                for name in include_names(text):
                    if "/" not in name:
                        continue
                    with self.subTest(library=library, header=path.name, include=name):
                        self.assertFalse(
                            name.startswith(framework),
                            f"{path.name} includes framework header {name!r}",
                        )


if __name__ == "__main__":
    unittest.main()

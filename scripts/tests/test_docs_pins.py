"""Prove the vendored KaTeX distribution byte-for-byte.

Pitfall 4: MkDocs resolves `extra_css` and `extra_javascript` leniently. A
missing target produces no warning at all, and `mkdocs build --strict` still
exits 0, so a partial copy renders raw `\\(x^2\\)` text in the browser with a
green build. This module is the only mechanism that can catch a missing font,
a flipped byte or a stray file in the vendored tree.

D-14 keeps this suite dependency-free: no test module may import PyYAML or
jsonschema. That rule is inherited here, so every assertion reads committed
bytes with the standard library only and never shells out or touches the
network.

`render-math.js` is ASCII by deliberate policy. The file is served to the
browser and reviewed as text, so its byte count, code-point count and displayed
content must agree; a UTF-8 comment would be a policy change, not a harmless
tweak. RenderMathScriptTests enforces that policy.

The `PinConsistencyTests` class belongs to a later plan that introduces the site
configuration; this module starts as the vendoring and provenance gate.
"""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import stat
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
VENDOR = REPO_ROOT / "docs" / "assets" / "vendor" / "katex" / "0.19.0"

LEDGER_NAME = "FILES.sha256"
AUTHORED_FILES = frozenset({"render-math.js", "PROVENANCE.txt", LEDGER_NAME})
CDN_HOSTS = (b"cdn.", b"unpkg.com", b"jsdelivr")
DIGEST = re.compile(r"^[0-9a-f]{64}$")


def read_ledger(path: Path | None = None) -> list[tuple[str, str]]:
    """Return `(digest, relative path)` pairs from a `sha256sum -c` ledger.

    The bytes are decoded and split on universal newlines, so a CRLF checkout
    cannot leave a trailing `\\r` on the path half of a line and manufacture a
    digest mismatch that does not exist.
    """
    ledger = Path(path) if path is not None else VENDOR / LEDGER_NAME
    text = ledger.read_bytes().decode("utf-8")
    entries: list[tuple[str, str]] = []
    for line in text.splitlines():
        if not line.strip():
            continue
        digest, separator, relative = line.partition("  ")
        if separator != "  " or not relative:
            raise AssertionError(f"{ledger}: malformed ledger line {line!r}")
        entries.append((digest, relative.rstrip("\r")))
    return entries


def verify_tree(root: Path) -> list[str]:
    """Return every integrity problem found under *root*.

    The returned list is empty only when the ledger is present, every listed
    digest matches, no unlisted regular file appears, and `fonts/` contains no
    subdirectory. The last rule matters because a directory is invisible to a
    file-only set comparison: a partial tree that is a directory cannot pass.
    """
    root = Path(root)
    problems: list[str] = []
    entries = read_ledger(root / LEDGER_NAME)
    listed: set[str] = set()

    for digest, relative in entries:
        listed.add(relative)
        parts = Path(relative).parts
        if Path(relative).is_absolute() or ".." in parts:
            problems.append(f"unsafe path in ledger: {relative}")
            continue
        target = root / relative
        try:
            mode = os.lstat(target).st_mode
        except FileNotFoundError:
            problems.append(f"missing listed file: {relative}")
            continue
        except OSError as exc:  # pragma: no cover - defensive
            problems.append(f"cannot inspect listed file: {relative}: {exc}")
            continue
        if not stat.S_ISREG(mode):
            problems.append(f"listed path is not a regular file: {relative}")
            continue
        if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
            problems.append(f"digest mismatch: {relative}")

    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if not path.is_file():
            continue
        if relative in listed or relative in AUTHORED_FILES:
            continue
        problems.append(f"unlisted file: {relative}")

    fonts = root / "fonts"
    if fonts.is_dir():
        for path in sorted(fonts.rglob("*")):
            if path.is_dir():
                relative = path.relative_to(root).as_posix()
                problems.append(f"unexpected subdirectory under fonts/: {relative}")

    return problems


class KatexVendoringTests(unittest.TestCase):
    """The committed vendor tree is complete, intact and licensed."""

    def test_ledger_has_exactly_24_unique_entries(self):
        entries = read_ledger()
        self.assertEqual(24, len(entries))
        paths = [relative for _, relative in entries]
        self.assertEqual(sorted(paths), paths, "the ledger must be sorted by path")
        self.assertEqual(len(paths), len(set(paths)), "duplicate path in the ledger")
        for digest, relative in entries:
            with self.subTest(path=relative):
                self.assertRegex(digest, DIGEST)

    def test_every_listed_path_is_a_regular_file_inside_the_vendor_directory(self):
        for _, relative in read_ledger():
            with self.subTest(path=relative):
                parts = Path(relative).parts
                self.assertFalse(Path(relative).is_absolute(), relative)
                self.assertNotIn("..", parts, relative)
                self.assertTrue(
                    stat.S_ISREG(os.lstat(VENDOR / relative).st_mode),
                    f"{relative} is not a regular file",
                )

    def test_every_digest_matches_the_file(self):
        for digest, relative in read_ledger():
            with self.subTest(path=relative):
                actual = hashlib.sha256((VENDOR / relative).read_bytes()).hexdigest()
                self.assertEqual(digest, actual)

    def test_vendor_tree_is_the_listed_set_plus_authored_files(self):
        listed = {relative for _, relative in read_ledger()}
        on_disk = {
            path.relative_to(VENDOR).as_posix()
            for path in VENDOR.rglob("*")
            if path.is_file()
        }
        self.assertEqual(listed | AUTHORED_FILES, on_disk)

    def test_provenance_records_the_authentic_tarball(self):
        text = (VENDOR / "PROVENANCE.txt").read_text(encoding="utf-8")
        self.assertIn("https://registry.npmjs.org/katex/-/katex-0.19.0.tgz", text)
        self.assertRegex(text, r"(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])")
        self.assertIn("MIT", text)

    def test_license_is_the_katex_mit_license(self):
        text = (VENDOR / "LICENSE").read_text(encoding="utf-8")
        self.assertIn("MIT License", text)
        self.assertIn("Khan Academy", text)

    def test_css_references_the_vendored_main_font(self):
        text = (VENDOR / "katex.min.css").read_text(encoding="utf-8")
        self.assertIn("fonts/KaTeX_Main-Regular.woff2", text)

    def test_no_vendored_file_names_a_cdn_host(self):
        for path in sorted(VENDOR.rglob("*")):
            if not path.is_file():
                continue
            data = path.read_bytes()
            for token in CDN_HOSTS:
                with self.subTest(path=path.relative_to(VENDOR).as_posix()):
                    self.assertNotIn(token, data)

    def test_verify_tree_reports_the_real_tree_as_clean(self):
        # A green discrimination case would be worthless if the helper always
        # passed, so the real tree must also be clean.
        self.assertEqual([], verify_tree(VENDOR))


class KatexVendoringDiscriminationTests(unittest.TestCase):
    """`verify_tree` fails for each reason it claims to detect.

    Every case mutates a private copy of the vendor tree, so the committed
    bytes are never touched and a negative case can fail only because of its
    single mutation.
    """

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name) / "katex"
        shutil.copytree(VENDOR, self.root)

    def test_flipped_byte_is_a_named_digest_mismatch(self):
        target = self.root / "fonts" / "KaTeX_Main-Regular.woff2"
        data = bytearray(target.read_bytes())
        data[0] ^= 0xFF
        target.write_bytes(bytes(data))

        problems = verify_tree(self.root)

        self.assertTrue(
            any(
                "digest mismatch" in problem
                and "KaTeX_Main-Regular.woff2" in problem
                for problem in problems
            ),
            problems,
        )

    def test_deleted_face_is_a_named_missing_file(self):
        (self.root / "fonts" / "KaTeX_Size4-Regular.woff2").unlink()

        problems = verify_tree(self.root)

        self.assertTrue(
            any(
                "missing listed file" in problem
                and "KaTeX_Size4-Regular.woff2" in problem
                for problem in problems
            ),
            problems,
        )

    def test_unlisted_file_is_reported(self):
        (self.root / "fonts" / "KaTeX_Extra-Regular.woff2").write_bytes(b"not a font")

        problems = verify_tree(self.root)

        self.assertTrue(
            any(
                "unlisted file" in problem and "KaTeX_Extra-Regular.woff2" in problem
                for problem in problems
            ),
            problems,
        )

    def test_fonts_subdirectory_is_reported(self):
        (self.root / "fonts" / "sub").mkdir()

        problems = verify_tree(self.root)

        self.assertTrue(
            any("subdirectory" in problem and "fonts/sub" in problem for problem in problems),
            problems,
        )

    def test_removed_fonts_directory_reports_every_face(self):
        shutil.rmtree(self.root / "fonts")

        problems = verify_tree(self.root)
        missing = [problem for problem in problems if "missing listed file" in problem]

        self.assertEqual(20, len(missing), problems)
        for face in ("KaTeX_AMS-Regular.woff2", "KaTeX_Typewriter-Regular.woff2"):
            with self.subTest(face=face):
                self.assertTrue(any(face in problem for problem in missing), problems)

    def test_crlf_ledger_keeps_the_same_paths(self):
        ledger = self.root / LEDGER_NAME
        original = [relative for _, relative in read_ledger(ledger)]
        ledger.write_bytes(
            ledger.read_bytes().decode("utf-8").replace("\n", "\r\n").encode("utf-8")
        )

        parsed = [relative for _, relative in read_ledger(ledger)]

        self.assertEqual(original, parsed)
        self.assertEqual(24, len(parsed))
        self.assertEqual([], verify_tree(self.root))

    def test_real_tree_is_clean(self):
        self.assertEqual([], verify_tree(VENDOR))


class RenderMathScriptTests(unittest.TestCase):
    """The authored browser script stays ASCII and integrates with Material.

    `render-math.js` may cite its source URL in a comment; "no external host"
    here means no CDN that could serve an asset and no externally loaded
    script, because D-07 forbids a network dependency in the site build.
    """

    @classmethod
    def setUpClass(cls):
        cls.path = VENDOR / "render-math.js"
        cls.data = cls.path.read_bytes()
        cls.text = cls.data.decode("ascii")  # raises if the policy is broken

    def test_script_is_ascii(self):
        self.assertTrue(self.data.isascii())

    def test_script_subscribes_to_document(self):
        self.assertIn("document$.subscribe", self.text)

    def test_script_calls_render_math_in_element(self):
        self.assertIn("renderMathInElement", self.text)

    def test_script_declares_every_delimiter_pair(self):
        for left, right in (
            (r"$$", r"$$"),
            (r"$", r"$"),
            (r"\\(", r"\\)"),
            (r"\\[", r"\\]"),
        ):
            with self.subTest(left=left, right=right):
                self.assertIn(f'left: "{left}"', self.text)
                self.assertIn(f'right: "{right}"', self.text)

    def test_script_names_no_external_asset_host(self):
        for token in ("cdn.", "unpkg.com", "jsdelivr"):
            with self.subTest(token=token):
                self.assertNotIn(token, self.text)
        self.assertNotIn("src=", self.text)

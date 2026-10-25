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

`PinConsistencyTests` closes the loop with the generated site configuration: it
cross-checks `requirements-docs.txt`, `mkdocs.yml` and the vendored KaTeX
directory, and proves the generated `nav:` lists every Markdown file under
`docs/`. It reads committed bytes with `pathlib` and plain string handling, so
the suite still never imports PyYAML (META-05, META-08, D-30).
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
REQUIREMENTS = REPO_ROOT / "requirements-docs.txt"
CONFIG = REPO_ROOT / "mkdocs.yml"
DOCS = REPO_ROOT / "docs"

PIN_LINES = frozenset(
    {"mkdocs==1.6.1", "mkdocs-material==9.7.7", "pymdown-extensions==12.3"}
)
KATEX_ROOT = "assets/vendor/katex/0.19.0/"
KATEX_STYLESHEET = f"{KATEX_ROOT}katex.min.css"
KATEX_SCRIPTS = (
    f"{KATEX_ROOT}katex.min.js",
    f"{KATEX_ROOT}contrib/auto-render.min.js",
    f"{KATEX_ROOT}render-math.js",
)
NAV_LINE = re.compile(r'^\s+- "[^"]+": (\S+\.md)$')
DOCS_PATH = re.compile(r"[A-Za-z0-9_./-]+")

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


class PinConsistencyTests(unittest.TestCase):
    """META-05/META-08/D-30: pins, theme constraints and nav coverage agree.

    No PyYAML: the generated configuration has one reviewed shape, so a
    line-based reader is sufficient and keeps this module stdlib-only. The nav
    matcher's contract (an ASCII docs-relative path with no whitespace and no
    quote) is asserted before anything is matched, so a path the line regex
    cannot represent fails by name instead of disappearing from the comparison.
    """

    def config_text(self) -> str:
        return CONFIG.read_text(encoding="utf-8")

    def section(self, key: str) -> list:
        """Return the lines under top-level *key*, stopping at the next key."""
        lines = self.config_text().splitlines()
        start = lines.index(key) + 1
        block = []
        for line in lines[start:]:
            if line and not line[0].isspace():
                break
            block.append(line)
        return block

    def entries(self, key: str) -> list:
        return [
            line.strip()[2:].strip()
            for line in self.section(key)
            if line.strip().startswith("- ")
        ]

    def nav_block(self) -> list:
        return self.section("nav:")

    def nav_targets(self) -> list:
        return [
            match.group(1)
            for match in (NAV_LINE.match(line) for line in self.nav_block())
            if match
        ]

    def docs_markdown_paths(self) -> list:
        return sorted(
            path.relative_to(DOCS).as_posix()
            for path in DOCS.rglob("*.md")
            if path.is_file()
        )

    def test_requirements_are_exactly_the_three_exact_pins(self) -> None:
        lines = [
            line.strip()
            for line in REQUIREMENTS.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]

        self.assertEqual(3, len(lines), lines)
        self.assertEqual(PIN_LINES, set(lines))

    def test_requirement_lines_carry_no_hash_or_extras_clause(self) -> None:
        for line in REQUIREMENTS.read_text(encoding="utf-8").splitlines():
            if not line.strip() or line.strip().startswith("#"):
                continue
            with self.subTest(line=line):
                self.assertNotIn("--hash", line)
                self.assertNotIn("[", line)
                self.assertNotIn(";", line)

    def test_mkdocs_pin_satisfies_materials_constraint(self) -> None:
        pin = next(
            line.strip()
            for line in REQUIREMENTS.read_text(encoding="utf-8").splitlines()
            if line.strip().startswith("mkdocs==")
        )
        version = pin.split("==", 1)[1]
        parts = version.split(".")

        self.assertEqual("1", parts[0], version)
        self.assertGreaterEqual(int(parts[1]), 6, version)
        self.assertLess(int(parts[0]), 2, version)

    def test_theme_is_material_without_a_custom_dir(self) -> None:
        theme = "\n".join(self.section("theme:"))

        self.assertIn("name: material", theme)
        self.assertNotIn("custom_dir", self.config_text())

    def test_the_only_plugin_is_search(self) -> None:
        self.assertEqual(["search"], self.entries("plugins:"))

    def test_no_hooks_or_inherit_key(self) -> None:
        text = self.config_text()

        self.assertNotRegex(text, r"(?m)^hooks:")
        self.assertNotIn("INHERIT:", text)

    def test_site_url_is_the_project_url(self) -> None:
        self.assertIn(
            "site_url: https://vloktiev-emb.github.io/homeworks/\n",
            self.config_text(),
        )

    def test_the_math_extension_path_is_complete(self) -> None:
        block = "\n".join(self.section("markdown_extensions:"))

        self.assertIn("  - pymdownx.arithmatex:\n      generic: true", block)
        self.assertIn("  - pymdownx.superfences", block)
        self.assertIn("  - pymdownx.highlight:", block)

    def test_extra_css_is_the_exact_vendored_stylesheet(self) -> None:
        self.assertEqual([KATEX_STYLESHEET], self.entries("extra_css:"))

    def test_extra_javascript_lists_the_three_scripts_in_order(self) -> None:
        entries = self.entries("extra_javascript:")

        self.assertEqual(list(KATEX_SCRIPTS), entries)
        for entry in entries:
            with self.subTest(entry=entry):
                self.assertIn(KATEX_ROOT, entry)

    def test_katex_directory_has_exactly_the_pinned_version_child(self) -> None:
        self.assertEqual(
            ["0.19.0"], sorted(path.name for path in VENDOR.parent.iterdir())
        )

    def test_every_docs_markdown_path_matches_the_matcher_contract(self) -> None:
        for path in self.docs_markdown_paths():
            with self.subTest(path=path):
                self.assertIsNotNone(
                    re.fullmatch(DOCS_PATH, path),
                    f"the nav matcher cannot represent {path!r}",
                )

    def test_nav_lists_every_markdown_file_under_docs(self) -> None:
        docs = set(self.docs_markdown_paths())
        targets = self.nav_targets()

        self.assertEqual(len(targets), len(set(targets)), "duplicate nav target")
        missing = sorted(docs - set(targets))
        extra = sorted(set(targets) - docs)
        self.assertEqual([], missing, f"the nav omits: {missing}")
        self.assertEqual(
            [], extra, f"the nav names paths that are not files under docs/: {extra}"
        )

    def test_no_nav_entry_is_a_single_quoted_scalar(self) -> None:
        entries = [
            line
            for line in self.nav_block()
            if line.strip().startswith("- ")
        ]

        self.assertTrue(entries, "the nav block must carry entries")
        for line in entries:
            with self.subTest(line=line):
                self.assertFalse(line.rstrip().endswith('"'), line)

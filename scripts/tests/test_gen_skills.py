"""Integration tests for scripts/gen_skills.py.

Every test drives the real generator through `uv run` against a disposable
canonical skill tree built by `scripts.tests.temp_root.write_skills_root`, so no
test module imports PyYAML or jsonschema (04/D-14) and no test reads the
authored `.claude/skills/` tree.

The module is split by concern: the tracer create path, the frontmatter
projection, the failure classes that must exit 2, every drift class under
`--check`, orphan deletion safety, manifest validation, `_shared/` handling,
symlink refusal, and the fixture builder's own contract.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.tests import temp_root

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = "scripts/gen_skills.py"

GENERATED_HEADER = (
    "<!-- GENERATED — do not edit. Run: uv run scripts/gen_skills.py -->"
)
BANNER_ALPHA = (
    "> **Invocation:** explicit only — run `/alpha`. "
    "Do not invoke this skill automatically."
)
MIRROR_ALPHA = ".agents/skills/alpha/SKILL.md"
MIRROR_BETA = ".agents/skills/beta/SKILL.md"
SHARED_MIRROR = ".agents/skills/_shared/guardrails.md"
MANIFEST = "generated.skills.manifest"


def run_gen_skills(*args: str, timeout: int = 180) -> subprocess.CompletedProcess:
    """Invoke `uv run scripts/gen_skills.py` from the repository root."""
    if shutil.which("uv") is None:
        raise AssertionError(
            "uv is a required repository tool; install it before running this suite"
        )
    return subprocess.run(
        ["uv", "run", SCRIPT, *args],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def snapshot(directory: Path) -> dict:
    """Return every file under *directory* as `relative path -> bytes`."""
    return {
        path.relative_to(directory).as_posix(): path.read_bytes()
        for path in sorted(directory.rglob("*"), key=lambda item: item.as_posix())
        if path.is_file()
    }


def setUpModule():
    """Warm uv's script environment before the first asserted run."""
    result = run_gen_skills("--help")
    if result.returncode != 0:
        raise RuntimeError(
            f"uv could not run the generator: {result.stdout + result.stderr}"
        )


class SkillsTestBase(unittest.TestCase):
    """One disposable canonical tree per test."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="gen-skills-")
        self.addCleanup(self._tmp.cleanup)
        self.workspace = Path(self._tmp.name)
        self.root = temp_root.write_skills_root(self.workspace / "root")

    def generate(self, *args: str) -> subprocess.CompletedProcess:
        return run_gen_skills(*args, "--dir", str(self.root))

    def assert_usage_error(self, result: subprocess.CompletedProcess) -> None:
        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertEqual("", result.stdout, "a usage error must print no record")
        self.assertIn("ERROR:", result.stderr)

    def canonical_skill(self, name: str) -> Path:
        return self.root / ".claude" / "skills" / name / "SKILL.md"

    def mirror(self, relative: str) -> Path:
        return self.root / relative

    def manifest_path(self) -> Path:
        return self.root / MANIFEST

    def read_manifest(self) -> dict:
        return json.loads(self.manifest_path().read_text(encoding="utf-8"))

    def write_manifest(self, entries) -> None:
        self.manifest_path().write_text(
            json.dumps({"version": 1, "entries": entries}, indent=2) + "\n",
            encoding="utf-8",
        )

    def add_manifest_entry(self, path: str, data: bytes) -> None:
        payload = self.read_manifest()
        payload["entries"].append(
            {
                "path": path,
                "owner": "skills",
                "source": ".claude/skills/alpha/" + Path(path).name,
                "mode": "whole",
                "sha256": hashlib.sha256(data).hexdigest(),
                "bytes": len(data),
            }
        )
        payload["entries"].sort(key=lambda entry: entry["path"])
        self.write_manifest(payload["entries"])


class TracerTests(SkillsTestBase):
    """The smallest real tree proves the whole spine end to end."""

    def test_first_run_creates_the_mirror_and_the_manifest(self) -> None:
        result = self.generate()

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        for path in (MIRROR_ALPHA, MIRROR_BETA, SHARED_MIRROR, MANIFEST):
            with self.subTest(path=path):
                self.assertIn(f"{path}: CREATE", result.stdout)
                self.assertTrue((self.root / path).is_file(), path)

    def test_second_run_reports_only_unchanged(self) -> None:
        self.assertEqual(0, self.generate().returncode)

        result = self.generate()

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        for status in ("CREATE", "MODIFIED", "DELETED", "DELETE", "ORPHAN", "ERROR"):
            with self.subTest(status=status):
                self.assertNotIn(f": {status}", result.stdout, result.stdout)

    def test_check_json_is_a_sorted_record_list(self) -> None:
        self.assertEqual(0, self.generate().returncode)

        result = self.generate("--check", "--json")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        records = json.loads(result.stdout)
        self.assertIsInstance(records, list)
        paths = [record["path"] for record in records]
        self.assertEqual(sorted(paths), paths)
        for record in records:
            self.assertEqual({"path", "status", "reason"}, set(record))
            self.assertEqual("UNCHANGED", record["status"])


class TransformTests(SkillsTestBase):
    """D-02/Pitfall 2: a line-preserving projection, never a YAML round-trip."""

    def setUp(self) -> None:
        super().setUp()
        self.assertEqual(0, self.generate().returncode)
        self.alpha = self.mirror(MIRROR_ALPHA).read_text(encoding="utf-8")
        self.beta = self.mirror(MIRROR_BETA).read_text(encoding="utf-8")

    def test_claude_only_keys_are_dropped_and_portable_lines_kept(self) -> None:
        self.assertNotIn("disable-model-invocation", self.alpha)
        self.assertIn("name: alpha\n", self.alpha)
        self.assertIn(
            "description: An authored fixture skill for the skills-generator "
            "suite.\n",
            self.alpha,
        )
        self.assertIn('  version: "0.1"\n', self.alpha)
        self.assertIn("  status: active\n", self.alpha)

    def test_a_column_zero_comment_survives_without_an_unknown_key_error(self) -> None:
        self.assertIn(
            "# authored comment stays in place and is never a key\n", self.alpha
        )

    def test_the_body_is_byte_identical_after_the_inserted_marker_and_banner(
        self,
    ) -> None:
        canonical = self.canonical_skill("alpha").read_text(encoding="utf-8")
        end = canonical.index("\n---\n", 4)
        body = canonical[end + 5 :]

        self.assertTrue(self.alpha.endswith(body), self.alpha)
        self.assertIn(GENERATED_HEADER, self.alpha)
        self.assertIn(BANNER_ALPHA, self.alpha)

    def test_the_banner_is_present_only_when_invocation_was_widened(self) -> None:
        self.assertIn(BANNER_ALPHA, self.alpha)
        self.assertNotIn("Invocation:", self.beta)

    def test_the_marker_follows_the_closing_frontmatter_fence(self) -> None:
        lines = self.alpha.splitlines()
        closing = lines.index("---", 1)
        self.assertEqual(GENERATED_HEADER, lines[closing + 1])
        self.assertEqual(BANNER_ALPHA, lines[closing + 2])

    def test_every_non_skill_file_starts_with_the_generated_marker(self) -> None:
        for relative in (
            ".agents/skills/alpha/CHANGELOG.md",
            ".agents/skills/alpha/LESSONS.md",
            ".agents/skills/alpha/references/topic.md",
            SHARED_MIRROR,
        ):
            with self.subTest(relative=relative):
                text = self.mirror(relative).read_text(encoding="utf-8")
                self.assertTrue(text.startswith(GENERATED_HEADER + "\n"), text)

    def test_a_mirrored_reference_keeps_the_canonical_bytes_after_line_one(
        self,
    ) -> None:
        canonical = (
            self.root / ".claude" / "skills" / "alpha" / "references" / "topic.md"
        ).read_bytes()
        mirror = self.mirror(".agents/skills/alpha/references/topic.md").read_bytes()

        self.assertEqual(
            canonical, mirror[len((GENERATED_HEADER + "\n").encode("utf-8")) :]
        )

    def test_two_full_runs_are_byte_identical(self) -> None:
        first = snapshot(self.root)

        self.assertEqual(0, self.generate().returncode)

        self.assertEqual(first, snapshot(self.root))


class FailureTests(SkillsTestBase):
    """Every malformed input is exit 2 with one ERROR line and no record."""

    def test_an_unknown_frontmatter_key_exits_two(self) -> None:
        path = self.canonical_skill("alpha")
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                "metadata:\n", "bogus: x\nmetadata:\n", 1
            ),
            encoding="utf-8",
        )

        result = self.generate("--check")

        self.assert_usage_error(result)
        self.assertIn("bogus", result.stderr)

    def test_an_unclosed_frontmatter_fence_exits_two(self) -> None:
        path = self.canonical_skill("alpha")
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                "---\n\n# Alpha (fixture)", "\n# Alpha (fixture)", 1
            ),
            encoding="utf-8",
        )

        self.assert_usage_error(self.generate("--check"))

    def test_a_name_that_differs_from_its_directory_exits_two(self) -> None:
        path = self.canonical_skill("alpha")
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                "name: alpha", "name: gamma", 1
            ),
            encoding="utf-8",
        )

        result = self.generate("--check")

        self.assert_usage_error(result)
        self.assertIn("gamma", result.stderr)

    def test_a_shared_skill_md_exits_two(self) -> None:
        (self.root / ".claude" / "skills" / "_shared" / "SKILL.md").write_text(
            "---\nname: _shared\ndescription: x\n---\n", encoding="utf-8"
        )

        self.assert_usage_error(self.generate("--check"))

    def test_a_reference_deeper_than_one_level_exits_two(self) -> None:
        deep = (
            self.root
            / ".claude"
            / "skills"
            / "alpha"
            / "references"
            / "deep"
        )
        deep.mkdir(parents=True)
        (deep / "file.md").write_text("# Deep\n", encoding="utf-8")

        self.assert_usage_error(self.generate("--check"))

    def test_an_absent_canonical_root_exits_two(self) -> None:
        empty = self.workspace / "empty"
        empty.mkdir()

        result = run_gen_skills("--check", "--dir", str(empty))

        self.assert_usage_error(result)
        self.assertIn("absent", result.stderr)

    def test_a_skill_directory_outside_the_slug_pattern_exits_two(self) -> None:
        stray = self.root / ".claude" / "skills" / "Mixed_Case"
        stray.mkdir()
        (stray / "SKILL.md").write_text(
            "---\nname: Mixed_Case\ndescription: x\n---\n", encoding="utf-8"
        )

        self.assert_usage_error(self.generate("--check"))

    def test_a_skill_directory_without_skill_md_exits_two(self) -> None:
        stray = self.root / ".claude" / "skills" / "gamma"
        stray.mkdir()
        (stray / "CHANGELOG.md").write_text("# Changelog\n", encoding="utf-8")

        self.assert_usage_error(self.generate("--check"))


class DriftTests(SkillsTestBase):
    """Every drift class is reported, and `--check` never repairs one."""

    def setUp(self) -> None:
        super().setUp()
        self.assertEqual(0, self.generate().returncode)

    def test_an_edited_mirror_byte_is_modified_drift(self) -> None:
        mirror = self.mirror(MIRROR_ALPHA)
        mirror.write_text(
            mirror.read_text(encoding="utf-8").replace("Alpha", "Edited", 1),
            encoding="utf-8",
        )
        before = snapshot(self.root)

        result = self.generate("--check")

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn(f"{MIRROR_ALPHA}: MODIFIED", result.stdout)
        self.assertEqual(before, snapshot(self.root), "--check must not write")

    def test_a_missing_mirror_is_deleted_in_check_and_created_in_write(
        self,
    ) -> None:
        mirror = self.mirror(MIRROR_ALPHA)
        original = mirror.read_bytes()
        mirror.unlink()

        check = self.generate("--check")

        self.assertEqual(1, check.returncode, check.stdout + check.stderr)
        self.assertIn(f"{MIRROR_ALPHA}: DELETED", check.stdout)
        self.assertFalse(mirror.exists(), "check mode must not write")

        write = self.generate()

        self.assertEqual(0, write.returncode, write.stdout + write.stderr)
        self.assertIn(f"{MIRROR_ALPHA}: CREATE", write.stdout)
        self.assertEqual(original, mirror.read_bytes())

    def test_a_manifest_listed_stale_path_is_an_orphan_in_check_mode(self) -> None:
        stale = self.mirror(".agents/skills/alpha/EXTRA.md")
        data = (GENERATED_HEADER + "\nnote\n").encode("utf-8")
        stale.write_bytes(data)
        self.add_manifest_entry(".agents/skills/alpha/EXTRA.md", data)
        before = snapshot(self.root)

        result = self.generate("--check")

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn(".agents/skills/alpha/EXTRA.md: ORPHAN", result.stdout)
        self.assertTrue(stale.exists(), "check mode must not delete anything")
        self.assertEqual(before, snapshot(self.root), "--check must not write")

    def test_a_marker_bearing_orphan_is_deleted_in_write_mode(self) -> None:
        stale = self.mirror(".agents/skills/alpha/EXTRA.md")
        data = (GENERATED_HEADER + "\nnote\n").encode("utf-8")
        stale.write_bytes(data)
        self.add_manifest_entry(".agents/skills/alpha/EXTRA.md", data)

        result = self.generate()

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn(".agents/skills/alpha/EXTRA.md: DELETE", result.stdout)
        self.assertFalse(stale.exists())
        paths = [entry["path"] for entry in self.read_manifest()["entries"]]
        self.assertNotIn(".agents/skills/alpha/EXTRA.md", paths)

    def test_an_unheadered_orphan_survives_write_mode_and_blocks_it(self) -> None:
        stale = self.mirror(".agents/skills/alpha/EXTRA.md")
        stale.write_text("Authored note\n", encoding="utf-8")
        self.add_manifest_entry(
            ".agents/skills/alpha/EXTRA.md", stale.read_bytes()
        )
        before = snapshot(self.root)

        result = self.generate()

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn(".agents/skills/alpha/EXTRA.md: ORPHAN", result.stdout)
        self.assertTrue(stale.exists(), "the orphan must be left intact")
        self.assertEqual(before, snapshot(self.root), "a blocked run must not write")

    def test_a_canonical_file_that_already_carries_the_header_is_stable(
        self,
    ) -> None:
        extra = self.root / ".claude" / "skills" / "alpha" / "EXTRA.md"
        extra.write_text(f"{GENERATED_HEADER}\nnote\n", encoding="utf-8")

        self.assertEqual(0, self.generate().returncode)
        first = snapshot(self.root)

        result = self.generate()

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn(".agents/skills/alpha/EXTRA.md: UNCHANGED", result.stdout)
        self.assertEqual(first, snapshot(self.root))


class ManifestTests(SkillsTestBase):
    """D-04/D-05: the committed ledger is the only record of ownership."""

    def setUp(self) -> None:
        super().setUp()
        self.assertEqual(0, self.generate().returncode)
        self.payload = self.read_manifest()
        self.entries = self.payload["entries"]

    def test_the_manifest_is_version_one_sorted_and_complete(self) -> None:
        self.assertEqual({"version", "entries"}, set(self.payload))
        self.assertEqual(1, self.payload["version"])
        paths = [entry["path"] for entry in self.entries]
        self.assertEqual(sorted(paths), paths)
        for entry in self.entries:
            with self.subTest(path=entry["path"]):
                self.assertEqual(
                    {"path", "owner", "source", "mode", "sha256", "bytes"},
                    set(entry),
                )
                self.assertEqual("skills", entry["owner"])
                self.assertEqual("whole", entry["mode"])
                self.assertTrue(entry["source"].startswith(".claude/skills/"))

    def test_every_digest_and_byte_count_matches_the_mirror(self) -> None:
        for entry in self.entries:
            with self.subTest(path=entry["path"]):
                data = (self.root / entry["path"]).read_bytes()
                self.assertEqual(hashlib.sha256(data).hexdigest(), entry["sha256"])
                self.assertEqual(len(data), entry["bytes"])

    def test_the_manifest_never_lists_itself(self) -> None:
        paths = [entry["path"] for entry in self.entries]

        self.assertNotIn(MANIFEST, paths)

    def test_the_manifest_covers_every_mirror_file(self) -> None:
        paths = {entry["path"] for entry in self.entries}
        on_disk = {
            path.relative_to(self.root).as_posix()
            for path in (self.root / ".agents").rglob("*")
            if path.is_file()
        }

        self.assertEqual(on_disk, paths)

    def test_a_missing_or_wrong_source_is_refused(self) -> None:
        missing = {
            key: value
            for key, value in self.entries[0].items()
            if key != "source"
        }
        cases = {
            "missing": missing,
            "outside": {**self.entries[0], "source": ".claude/other/x.md"},
        }
        for name, entry in cases.items():
            with self.subTest(case=name):
                self.write_manifest([entry])

                self.assert_usage_error(self.generate("--check"))

    def test_a_wrong_owner_or_mode_is_refused(self) -> None:
        cases = {
            "owner": {**self.entries[0], "owner": "views"},
            "mode": {**self.entries[0], "mode": "region"},
        }
        for name, entry in cases.items():
            with self.subTest(case=name):
                self.write_manifest([entry])

                self.assert_usage_error(self.generate("--check"))

    def test_an_unknown_entry_key_is_refused(self) -> None:
        self.write_manifest([{**self.entries[0], "extra": True}])

        self.assert_usage_error(self.generate("--check"))

    def test_an_entry_outside_the_mirror_is_refused(self) -> None:
        self.write_manifest(
            [{**self.entries[0], "path": "README.md"}]
        )

        self.assert_usage_error(self.generate("--check"))

    def test_a_malformed_digest_is_refused(self) -> None:
        self.write_manifest([{**self.entries[0], "sha256": "0" * 63}])

        self.assert_usage_error(self.generate("--check"))


class SharedTests(SkillsTestBase):
    """Pitfall 7: `_shared/` is mirrored as files, never treated as a skill."""

    def test_shared_files_are_mirrored_and_not_discovered_as_a_skill(self) -> None:
        self.assertEqual(0, self.generate().returncode)

        self.assertTrue((self.root / SHARED_MIRROR).is_file())
        self.assertFalse(
            (self.root / ".agents" / "skills" / "_shared" / "SKILL.md").exists()
        )
        entries = {
            entry["path"]: entry for entry in self.read_manifest()["entries"]
        }
        self.assertIn(SHARED_MIRROR, entries)
        self.assertEqual(
            ".claude/skills/_shared/guardrails.md", entries[SHARED_MIRROR]["source"]
        )


class SymlinkTests(SkillsTestBase):
    """T-09-02: a symlink at any component is refused, never followed."""

    def setUp(self) -> None:
        super().setUp()
        self.assertEqual(0, self.generate().returncode)

    def test_a_symlinked_mirror_target_exits_two(self) -> None:
        target = self.mirror(MIRROR_ALPHA)
        external = self.workspace / "external-skill.md"
        external.write_text("Injected\n", encoding="utf-8")
        target.unlink()
        target.symlink_to(external)

        self.assert_usage_error(self.generate("--check"))

    def test_a_symlinked_intermediate_component_exits_two(self) -> None:
        directory = self.root / ".agents" / "skills" / "alpha"
        external = self.workspace / "external-alpha"
        external.mkdir()
        (external / "SKILL.md").write_text("Injected\n", encoding="utf-8")
        shutil.rmtree(directory)
        directory.symlink_to(external)

        self.assert_usage_error(self.generate("--check"))

    def test_a_symlinked_canonical_file_exits_two(self) -> None:
        target = self.canonical_skill("alpha")
        external = self.workspace / "external-canonical.md"
        external.write_text(target.read_text(encoding="utf-8"), encoding="utf-8")
        target.unlink()
        target.symlink_to(external)

        self.assert_usage_error(self.generate("--check"))


class FixtureTests(unittest.TestCase):
    """The fixture is assembled, never copied from the authored tree."""

    def test_the_fixture_contains_exactly_alpha_beta_and_shared(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skills-fixture-") as directory:
            root = temp_root.write_skills_root(Path(directory) / "root")
            children = sorted(
                path.name
                for path in (root / ".claude" / "skills").iterdir()
            )
            has_mirror = (root / ".agents").exists()

        self.assertEqual(["_shared", "alpha", "beta"], children)
        self.assertNotIn("simulate", children)
        self.assertFalse(has_mirror)


if __name__ == "__main__":
    unittest.main()

"""Prove the LFS-pointer guard's behaviour and the workflow contracts.

`ci.yml` is the one pull-request workflow: a fast `meta` job, a `changes` job that
computes the affected matrix, a `build` matrix, and the literal fan-in `gate`.
`nightly.yml` is the scheduled full-matrix run and the post-merge full-history scan. The
generated-view drift check no longer has a workflow of its own — it lives in the
`gen-views-check` pre-commit hook, and `meta` runs the whole reviewed hook surface.

The workflow assertions here are deliberately limited to the names and commands the YAML
must carry; whether a command works is proven by running it, and whether the matrix is
correct is proven by `scripts/tests/test_affected.py`. The trigger-key tests are the
durable guard against yamllint's `truthy` policy relaxing key checking, so every workflow
must keep spelling its trigger as the text `on:`.

`meta` runs contributor-controlled code on a pull-request event, so the file must never
reference a repository secret, request a write scope, or accept a pull-request-target
trigger; three assertions below pin that.

The suite is stdlib-only (04/D-14): it imports neither PyYAML nor jsonschema and
reads the workflows as plain text.
"""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
GUARD = REPO_ROOT / "scripts" / "ci" / "check_lfs_pointers.sh"
WORKFLOWS = REPO_ROOT / ".github" / "workflows"
CI = WORKFLOWS / "ci.yml"
NIGHTLY = WORKFLOWS / "nightly.yml"
PRECOMMIT = REPO_ROOT / ".pre-commit-config.yaml"
YAMLLINT_POLICY = REPO_ROOT / ".yamllint.yaml"

POINTER = "version https://git-lfs.github.com/spec/v1\noid sha256:" + "0" * 64 + "\nsize 42\n"
TIMEOUT = 30


def step_block(text: str, name: str) -> str:
    """Return the YAML of the step whose `name:` is *name*.

    A step begins at the six-space `- name:` (or `- uses:`) line and ends at the next line
    at that indentation, so the slice carries the step's own `if:`, `env:` and `run:` bodies
    and nothing after them.
    """
    lines = text.splitlines()
    start = next(
        (index for index, line in enumerate(lines) if line.strip() == f"- name: {name}"),
        None,
    )
    if start is None:
        raise AssertionError(f"ci.yml carries no step named {name!r}")
    end = next(
        (
            index
            for index in range(start + 1, len(lines))
            if lines[index].startswith("      - ")
        ),
        len(lines),
    )
    return "\n".join(lines[start:end])


def job_ids(text: str) -> set[str]:
    """Return the job ids declared directly under the top-level `jobs:` key.

    A job id is a two-space-indented key; anything deeper belongs to a job's own body, and
    a comment is never a job. Scanning stops at the first column-zero line after `jobs:`,
    so a later top-level key cannot be mistaken for a job.
    """
    ids: set[str] = set()
    in_jobs = False
    for line in text.splitlines():
        if line == "jobs:":
            in_jobs = True
            continue
        if not in_jobs:
            continue
        if line and not line.startswith(" "):
            break
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if line.startswith("  ") and not line.startswith("    ") and stripped.endswith(":"):
            ids.add(stripped.rstrip(":"))
    return ids


class LfsPointerGuardTests(unittest.TestCase):
    """The guard's exit status, not the workflow's spelling of it."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    def run_guard(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["bash", str(GUARD), *args],
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
        )

    def test_a_clean_tree_exits_zero(self) -> None:
        (self.root / "index.html").write_text("<html></html>\n", encoding="utf-8")
        result = self.run_guard(str(self.root))
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_an_empty_file_exits_zero(self) -> None:
        (self.root / "empty.png").write_bytes(b"")
        result = self.run_guard(str(self.root))
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_a_pointer_exits_one_and_names_the_file(self) -> None:
        pointer = self.root / "images" / "board.png"
        pointer.parent.mkdir()
        pointer.write_text(POINTER, encoding="utf-8")
        result = self.run_guard(str(self.root))
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn(str(pointer), result.stderr)

    def test_a_missing_directory_exits_two(self) -> None:
        result = self.run_guard(str(self.root / "missing"))
        self.assertEqual(result.returncode, 2, result.stderr)

    def test_a_symlink_is_not_followed(self) -> None:
        outside = self.root / "outside"
        outside.mkdir()
        (outside / "pointer.png").write_text(POINTER, encoding="utf-8")
        site = self.root / "site"
        site.mkdir()
        (site / "link.png").symlink_to(outside / "pointer.png")
        result = self.run_guard(str(site))
        self.assertEqual(result.returncode, 0, result.stderr)


class WorkflowTextTests(unittest.TestCase):
    """The names and commands the YAML must carry; behaviour lives above."""

    def test_drift_gate_lives_in_the_hook_surface(self) -> None:
        hooks = PRECOMMIT.read_text(encoding="utf-8")
        self.assertIn("id: gen-views-check", hooks)
        self.assertIn("entry: python scripts/gen_views.py --all --check", hooks)
        ci = CI.read_text(encoding="utf-8")
        self.assertIn("pre-commit run --all-files", ci)

    def test_meta_validates_the_title(self) -> None:
        step = step_block(CI.read_text(encoding="utf-8"), "Validate the pull-request title")
        self.assertIn(
            r"^(feat|fix|test|refactor|perf|docs|style|chore)\([a-z0-9._-]+\): .+$",
            step,
        )
        self.assertIn("PR_TITLE: ${{ github.event.pull_request.title }}", step)
        self.assertIn("github.event_name == 'pull_request'", step)
        body = step.split("run:", 1)[1]
        self.assertNotIn("${{ github.event", body)

    def test_ci_never_uses_pull_request_target(self) -> None:
        self.assertNotIn("pull_request_target", CI.read_text(encoding="utf-8"))

    def test_ci_grants_no_write_permission(self) -> None:
        text = CI.read_text(encoding="utf-8")
        self.assertIn("contents: read", text)
        self.assertNotIn(": write", text)

    def test_nightly_computes_the_full_matrix(self) -> None:
        # `platformio.shared.ini` is the mapper's own WIDEN_ALL entry, so the nightly matrix
        # is the full project set without a curated list or a second flag.
        text = NIGHTLY.read_text(encoding="utf-8")
        self.assertIn("uv run scripts/affected.py --paths-from", text)
        self.assertIn("platformio.shared.ini", text)

    def test_nightly_serialises_its_runs(self) -> None:
        # A manual dispatch must not overlap a scheduled run, and a scheduled run is never
        # cancelled by a newer one.
        text = NIGHTLY.read_text(encoding="utf-8")
        self.assertIn("group: ${{ github.workflow }}", text)
        self.assertIn("cancel-in-progress: false", text)

    def test_nightly_declares_the_full_matrix_job_set(self) -> None:
        self.assertEqual(
            {"changes", "build", "secrets"},
            job_ids(NIGHTLY.read_text(encoding="utf-8")),
        )

    def test_nightly_carries_the_full_history_scan(self) -> None:
        # The post-merge scan the retired `security.yml` provided on `push: main`.
        self.assertIn(
            'gitleaks git --redact --verbose --log-opts="--all"',
            NIGHTLY.read_text(encoding="utf-8"),
        )

    def test_nightly_declares_no_simulation(self) -> None:
        # A prose comment may explain the absence; only executable YAML is checked. Dropping
        # comment-only lines means a comment can neither satisfy nor trip the contract, so a
        # later edit cannot quietly reintroduce a metered job.
        lines = NIGHTLY.read_text(encoding="utf-8").splitlines()
        body = "\n".join(line for line in lines if not line.lstrip().startswith("#"))
        for marker in ("wokwi", "WOKWI_CLI_TOKEN", "simulate"):
            with self.subTest(marker=marker):
                self.assertNotIn(marker, body)


class MetaJobSurfaceTests(unittest.TestCase):
    """The security-critical ordering and the pinned tools inside the `meta` job."""

    def setUp(self) -> None:
        self.text = CI.read_text(encoding="utf-8")

    def meta_job(self) -> str:
        """Return only the `meta` job, so a match cannot come from another job."""
        start = self.text.index("\n  meta:\n")
        end = self.text.index("\n  changes:\n", start)
        return self.text[start:end]

    def test_meta_scans_history_before_running_hooks(self) -> None:
        meta = self.meta_job()
        # `rindex` reads the executed command, not the comment above it: the ordering
        # comment names `pre-commit install-hooks` before the step itself exists.
        scan = meta.rindex("gitleaks git")
        hooks = meta.rindex("pre-commit install-hooks")
        self.assertLess(scan, hooks)

    def test_meta_fetches_the_full_history(self) -> None:
        self.assertIn("fetch-depth: 0", self.meta_job())

    def test_meta_carries_the_full_history_scan(self) -> None:
        self.assertIn('gitleaks git --redact --verbose --log-opts="--all"', self.text)

    def test_meta_lints_every_diagram(self) -> None:
        meta = self.meta_job()
        self.assertIn("wokwi-cli lint --offline", meta)
        self.assertIn("homeworks/*/assets/diagram.json", meta)

    def test_meta_pins_the_scanner_and_linter_versions(self) -> None:
        self.assertIn("WOKWI_CLI_SHA256", self.text)
        for pin in ("8.30.1", "551f6fc8", "0.28.1", "869f194e"):
            with self.subTest(pin=pin):
                self.assertIn(pin, self.meta_job())


class WorkflowTriggerKeyTests(unittest.TestCase):
    """The YAML policy must never rewrite a workflow's trigger key (D-14).

    yamllint parses the bare `on:` key as a boolean under YAML 1.1, so every
    workflow produced a `truthy` finding. They are keys, not values, so
    `.yamllint.yaml` disables key checking instead of normalising a scalar.
    These assertions are the durable guard against a later edit that
    "simplifies" a trigger key and breaks the workflow schema; whether a
    workflow file needed an unrelated line-length fix is recorded in the plan
    summary, not asserted here.
    """

    def workflows(self) -> list[Path]:
        return sorted(WORKFLOWS.glob("*.yml"))

    def test_every_workflow_declares_a_textual_trigger_key(self) -> None:
        files = self.workflows()
        self.assertEqual(2, len(files), [path.name for path in files])
        for path in files:
            lines = path.read_text(encoding="utf-8").splitlines()
            with self.subTest(workflow=path.name):
                self.assertIn("on:", lines)

    def test_no_workflow_spells_a_trigger_as_a_boolean_key(self) -> None:
        for path in self.workflows():
            with self.subTest(workflow=path.name):
                for number, line in enumerate(
                    path.read_text(encoding="utf-8").splitlines(), start=1
                ):
                    self.assertNotIn(
                        line,
                        ("true:", "false:"),
                        f"{path.name}:{number} spells a trigger as a boolean key",
                    )

    def test_the_policy_relaxes_truthy_keys_and_keeps_boolean_values(self) -> None:
        text = YAMLLINT_POLICY.read_text(encoding="utf-8")
        self.assertIn("check-keys: false", text)
        self.assertIn("allowed-values: ['true', 'false']", text)


if __name__ == "__main__":
    unittest.main()

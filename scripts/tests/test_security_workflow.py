"""Token-level contract tests for ``.github/workflows/security.yml``.

The full-history secret scan is only meaningful if a handful of flags survive
edits: a shallow checkout or a missing ``--log-opts`` silently reduces the scan
to the tip commit, and a missing ``--redact`` writes a detected secret into a
public build log. There is no YAML parser in the standard library (yamllint
arrives in Phase 6), so these tests read the workflow as text and assert the
presence of the required tokens and the absence of the forbidden ones.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "security.yml"


class SecurityWorkflowContractTest(unittest.TestCase):
    """Guard the critical flags of the CI half of the secret gate."""

    @classmethod
    def setUpClass(cls):
        cls.text = WORKFLOW.read_text(encoding="utf-8") if WORKFLOW.is_file() else ""

    # --- required tokens -------------------------------------------------

    def test_workflow_file_exists(self):
        self.assertTrue(WORKFLOW.is_file(), f"missing {WORKFLOW}")

    def test_checks_out_full_history(self):
        self.assertIn("fetch-depth: 0", self.text)

    def test_scans_every_ref(self):
        self.assertIn('--log-opts="--all"', self.text)

    def test_redacts_detected_secrets(self):
        self.assertIn("--redact", self.text)

    def test_pins_gitleaks_version(self):
        self.assertIn("GITLEAKS_VERSION: 8.30.1", self.text)

    def test_uses_gitleaks_git_subcommand(self):
        self.assertIn("gitleaks git", self.text)

    def test_runs_on_pinned_ubuntu_runner(self):
        self.assertIn("ubuntu-24.04", self.text)

    def test_grants_read_only_contents_permission(self):
        self.assertIn("contents: read", self.text)

    def test_triggers_on_pull_request(self):
        self.assertIn("pull_request:", self.text)

    def test_triggers_on_push_to_main(self):
        self.assertIn("push:", self.text)
        self.assertIn("branches: [main]", self.text)

    def test_triggers_on_workflow_dispatch(self):
        self.assertIn("workflow_dispatch:", self.text)

    # --- forbidden tokens ------------------------------------------------

    def test_does_not_use_hosted_gitleaks_action(self):
        # The hosted action requires an organization license key (Pitfall 7).
        self.assertNotIn("gitleaks/gitleaks-action", self.text)

    def test_does_not_require_gitleaks_license(self):
        self.assertNotIn("GITLEAKS_LICENSE", self.text)

    def test_never_writes_back_to_the_repository(self):
        # The scan and the local hook must be able to run concurrently.
        self.assertIsNone(
            re.search(r"\bgit\s+(push|commit)\b", self.text),
            "workflow must not invoke git push or git commit",
        )


if __name__ == "__main__":
    unittest.main()

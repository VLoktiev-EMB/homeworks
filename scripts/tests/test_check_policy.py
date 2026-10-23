"""Offline unit tests for scripts/check_policy.py.

The suite never touches the network: the ruleset fixture in
``scripts/tests/fixtures/ruleset-live.json`` is a captured GET body, and every
``gh api`` / ``git`` invocation is served by an in-memory fake runner.
"""

from __future__ import annotations

import io
import json
import subprocess
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from scripts import check_policy

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "ruleset-live.json"
REPO_SLUG = "VLoktiev-EMB/homeworks"

LIVE_REPOSITORY = {
    "delete_branch_on_merge": True,
    "allow_squash_merge": True,
    "allow_merge_commit": True,
    "allow_rebase_merge": True,
    "allow_auto_merge": False,
    "security_and_analysis": {
        "secret_scanning": {"status": "disabled"},
        "secret_scanning_push_protection": {"status": "disabled"},
        "secret_scanning_validity_checks": {"status": "disabled"},
        "secret_scanning_non_provider_patterns": {"status": "disabled"},
    },
}


class FakeRunner:
    """Minimal stand-in for ``check_policy._run``."""

    def __init__(self, responses):
        self.responses = responses
        self.calls = []

    def __call__(self, argv, stdin=None):
        self.calls.append(list(argv))
        joined = " ".join(argv)
        for prefix, response in self.responses.items():
            if joined == prefix or joined.startswith(prefix + " "):
                if isinstance(response, Exception):
                    raise response
                if isinstance(response, subprocess.CompletedProcess):
                    return response
                return subprocess.CompletedProcess(
                    argv, 0, stdout=json.dumps(response), stderr=""
                )
        return subprocess.CompletedProcess(
            argv, 1, stdout="", stderr=f"unexpected call: {joined}"
        )


def live_ruleset():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def committed_ruleset():
    return json.loads(check_policy.RULESET_FILE.read_text(encoding="utf-8"))


def committed_repository():
    return json.loads(check_policy.REPOSITORY_FILE.read_text(encoding="utf-8"))


def ruleset_runner(live, repository=None):
    return FakeRunner(
        {
            "git remote get-url origin": subprocess.CompletedProcess(
                [], 0, stdout=f"git@github.com:{REPO_SLUG}.git\n", stderr=""
            ),
            f"gh api repos/{REPO_SLUG}/rulesets": [{"id": 25632456, "name": "main"}],
            f"gh api repos/{REPO_SLUG}/rulesets/25632456": live,
            f"gh api repos/{REPO_SLUG}": repository or committed_repository(),
        }
    )


class ProjectionTests(unittest.TestCase):
    def test_projection_strips_read_only_keys(self):
        live, desired = live_ruleset(), committed_ruleset()
        projected, _ = check_policy.normalise(live, desired)
        for key in check_policy.READ_ONLY:
            self.assertNotIn(key, projected, f"read-only key {key} leaked")

        # A captured GET body diffs clean against the committed subset.
        _, desired_projected = check_policy.normalise(live, desired)
        self.assertEqual(projected, desired_projected)
        self.assertEqual(check_policy.diff_report(projected, desired_projected), [])

    def test_reordered_rules_report_no_drift(self):
        live, desired = live_ruleset(), committed_ruleset()
        live["rules"] = list(reversed(live["rules"]))

        projected, desired_projected = check_policy.normalise(live, desired)
        self.assertEqual(projected, desired_projected)
        self.assertEqual(check_policy.diff_report(projected, desired_projected), [])

    def test_rule_removed_from_live_reports_drift(self):
        live, desired = live_ruleset(), committed_ruleset()
        live["rules"] = [r for r in live["rules"] if r["type"] != "deletion"]

        projected, desired_projected = check_policy.normalise(live, desired)
        self.assertNotEqual(projected, desired_projected)
        self.assertTrue(check_policy.diff_report(projected, desired_projected))


class DriftDetectionTests(unittest.TestCase):
    def test_reduced_approval_count_reports_drift(self):
        live, desired = live_ruleset(), committed_ruleset()
        for rule in live["rules"]:
            if rule["type"] == "pull_request":
                rule["parameters"]["required_approving_review_count"] = 1

        projected, desired_projected = check_policy.normalise(live, desired)
        self.assertNotEqual(projected, desired_projected)

    def test_non_empty_bypass_actors_reports_drift(self):
        live, desired = live_ruleset(), committed_ruleset()
        live["bypass_actors"] = [
            {"actor_id": 1, "actor_type": "User", "bypass_mode": "always"}
        ]

        projected, desired_projected = check_policy.normalise(live, desired)
        self.assertNotEqual(projected, desired_projected)

    def test_repository_drift_names_secret_scanning(self):
        runner = ruleset_runner(live_ruleset(), repository=LIVE_REPOSITORY)
        out = io.StringIO()
        with redirect_stdout(out):
            code = check_policy.main(["--check"], runner=runner)

        self.assertEqual(code, 1)
        self.assertIn("secret_scanning", out.getvalue())
        self.assertIn("FAIL", out.getvalue())


class CliContractTests(unittest.TestCase):
    def test_check_and_apply_are_mutually_exclusive(self):
        with self.assertRaises(SystemExit) as caught:
            check_policy.main(["--check", "--apply"])
        self.assertEqual(caught.exception.code, 2)

    def test_gh_failure_returns_exit_2_without_traceback(self):
        runner = FakeRunner(
            {
                "git remote get-url origin": subprocess.CompletedProcess(
                    [], 0, stdout=f"git@github.com:{REPO_SLUG}.git\n", stderr=""
                ),
                "gh api": subprocess.CompletedProcess(
                    [], 1, stdout="", stderr="HTTP 403: Resource not accessible"
                ),
            }
        )
        err = io.StringIO()
        out = io.StringIO()
        from contextlib import redirect_stderr

        with redirect_stdout(out), redirect_stderr(err):
            code = check_policy.main(["--check"], runner=runner)

        self.assertEqual(code, 2)
        self.assertNotIn("Traceback", err.getvalue())

    def test_check_mode_never_mutates(self):
        runner = ruleset_runner(live_ruleset())
        with redirect_stdout(io.StringIO()):
            check_policy.main(["--check"], runner=runner)

        mutations = [
            call
            for call in runner.calls
            if any(
                token in call
                for token in ("-X", "POST", "PUT", "PATCH", "--method")
            )
        ]
        self.assertEqual(mutations, [], f"mutating calls in --check: {mutations}")

    def test_slug_parsing_both_url_forms(self):
        self.assertEqual(
            check_policy.slug_from_remote_url(
                "git@github.com:VLoktiev-EMB/homeworks.git"
            ),
            REPO_SLUG,
        )
        self.assertEqual(
            check_policy.slug_from_remote_url(
                "https://github.com/VLoktiev-EMB/homeworks.git"
            ),
            REPO_SLUG,
        )


if __name__ == "__main__":
    unittest.main()

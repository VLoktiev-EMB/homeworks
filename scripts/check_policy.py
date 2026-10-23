#!/usr/bin/env python3
"""Assert that live GitHub policy matches the committed policy files.

`main` branch protection is only real if it can be asserted. This script reads
the committed policy under ``policy/`` and compares it with live GitHub state
through the ``gh`` CLI.

Usage:
  python3 scripts/check_policy.py --check   # read-only drift check (default)
  python3 scripts/check_policy.py --apply   # push committed policy, then check

Exit codes (a CI contract from Phase 8 onward):
  0  live GitHub state matches the committed policy
  1  drift: committed policy and live state disagree
  2  usage or environment error (bad arguments, missing gh, API failure)

The comparison is a *projection*: the live response is reduced to the keys the
committed file declares, and rule lists are matched and ordered by rule type.
The raw ``gh api`` GET body is never diffed directly — it carries server-side
read-only fields and would never converge.
"""

from __future__ import annotations

import argparse
import difflib
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
POLICY_DIR = REPO_ROOT / "policy"
RULESET_FILE = POLICY_DIR / "ruleset-main.json"
REPOSITORY_FILE = POLICY_DIR / "repository.json"

# Fields GitHub returns on GET but does not accept on PUT. They are dropped so
# a captured body can be compared against the committed subset.
READ_ONLY = {
    "id",
    "node_id",
    "source_type",
    "source",
    "created_at",
    "updated_at",
    "_links",
    "current_user_can_bypass",
}


class PolicyError(Exception):
    """A usage or environment problem, reported with exit code 2."""


def _run(argv, stdin=None):
    """Run a command with list arguments; never a shell string."""
    try:
        return subprocess.run(argv, input=stdin, capture_output=True, text=True)
    except OSError as exc:
        raise PolicyError(f"cannot execute {argv[0]}: {exc}") from exc


def _load_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except OSError as exc:
        raise PolicyError(f"cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise PolicyError(f"{path} is not valid JSON: {exc}") from exc


def slug_from_remote_url(url):
    """Turn an origin remote URL into ``OWNER/REPO``."""
    url = url.strip()
    if "github.com" not in url:
        raise PolicyError(f"origin remote is not a GitHub URL: {url!r}")
    tail = url.split("github.com", 1)[1].lstrip(":/").removesuffix(".git").strip("/")
    if tail.count("/") != 1 or not all(tail.split("/")):
        raise PolicyError(f"cannot derive OWNER/REPO from origin URL: {url!r}")
    return tail


def slug(runner=None):
    """Resolve the repository from ``origin``; never hard-code it."""
    runner = runner or _run
    proc = runner(["git", "remote", "get-url", "origin"])
    if proc.returncode != 0:
        raise PolicyError(f"git remote get-url origin failed: {proc.stderr.strip()}")
    return slug_from_remote_url(proc.stdout)


def gh_api(args, runner=None, stdin=None):
    """Invoke ``gh api`` and return the parsed JSON body."""
    runner = runner or _run
    proc = runner(["gh", "api", *args], stdin=stdin)
    if proc.returncode != 0:
        raise PolicyError(f"gh api {args[0]} failed: {proc.stderr.strip()}")
    output = proc.stdout.strip()
    if not output:
        return None
    try:
        return json.loads(output)
    except json.JSONDecodeError as exc:
        raise PolicyError(f"gh api {args[0]} returned invalid JSON: {exc}") from exc


def _sort_key(item):
    if isinstance(item, dict):
        return str(item.get("type", ""))
    return ""


MISSING_IN_LIVE = "__missing_in_live__"


def _project_rule_list(live_items, desired_items):
    """Pair rules by ``type``, then order by ``type``; never by index."""
    live_sorted = sorted(
        (item for item in live_items if isinstance(item, dict)), key=_sort_key
    )
    desired_sorted = sorted(desired_items, key=_sort_key)
    projected = []
    for template in desired_sorted:
        match = next(
            (item for item in live_sorted if _sort_key(item) == _sort_key(template)),
            None,
        )
        if match is None:
            # A rule declared but absent live is drift; the marker keeps the
            # rule identifiable in the diff instead of letting it cancel out.
            missing = dict(template)
            missing[MISSING_IN_LIVE] = True
            projected.append(missing)
        else:
            projected.append(project(match, template))
    declared = {_sort_key(item) for item in desired_sorted}
    # A live rule the committed subset does not declare is drift too.
    projected.extend(item for item in live_sorted if _sort_key(item) not in declared)
    return projected


def project(live, desired):
    """Keep only the keys ``desired`` declares, recursively."""
    projected = {}
    for key, template in desired.items():
        if key not in live:
            continue
        value = live[key]
        if isinstance(template, dict) and isinstance(value, dict):
            projected[key] = project(value, template)
        elif (
            isinstance(template, list)
            and template
            and all(isinstance(item, dict) and "type" in item for item in template)
            and isinstance(value, list)
        ):
            projected[key] = _project_rule_list(value, template)
        else:
            projected[key] = value
    return projected


def normalise(live, desired):
    """Return the live projection and the committed projection."""
    return project(live, desired), project(desired, desired)


def diff_report(projected, expected):
    """A unified diff of the two normalized objects, or an empty list."""
    left = json.dumps(projected, indent=2, sort_keys=True).splitlines()
    right = json.dumps(expected, indent=2, sort_keys=True).splitlines()
    return list(
        difflib.unified_diff(
            left,
            right,
            fromfile="live (normalized)",
            tofile="committed policy",
            lineterm="",
        )
    )


def flatten(obj, prefix=""):
    """Flatten nested dicts to dotted paths of leaf values."""
    flat = {}
    for key, value in obj.items():
        path = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            flat.update(flatten(value, path))
        else:
            flat[path] = value
    return flat


def _bracket(path):
    """``a.b.c`` -> ``a[b][c]`` for ``gh api -f`` payload keys."""
    head, *rest = path.split(".")
    return head + "".join(f"[{part}]" for part in rest)


def _ruleset_id(slug_value, name, runner):
    rulesets = gh_api([f"repos/{slug_value}/rulesets"], runner=runner) or []
    for ruleset in rulesets:
        if ruleset.get("name") == name:
            return ruleset["id"]
    raise PolicyError(f"no ruleset named {name!r} on {slug_value}")


def check_ruleset(slug_value, desired, runner):
    """Return (projected, expected, diff_lines) for the committed ruleset."""
    ruleset_id = _ruleset_id(slug_value, desired.get("name", "main"), runner)
    live = gh_api([f"repos/{slug_value}/rulesets/{ruleset_id}"], runner=runner)
    projected, expected = normalise(live or {}, desired)
    return projected, expected, diff_report(projected, expected)


def check_repository(slug_value, desired, runner):
    """Return (drift, per-setting lines) for the committed repository settings."""
    live = gh_api([f"repos/{slug_value}"], runner=runner) or {}
    live_flat = flatten(project(live, desired))
    lines = []
    drift = False
    for path, expected in flatten(desired).items():
        actual = live_flat.get(path, "<missing>")
        ok = actual == expected
        drift = drift or not ok
        verdict = "PASS" if ok else "FAIL"
        lines.append(f"{verdict} {path}: expected {expected!r}, got {actual!r}")
    return drift, lines


def run_check(slug_value, ruleset, repository, runner):
    """Print the drift report and return the exit code."""
    _, _, ruleset_diff = check_ruleset(slug_value, ruleset, runner)
    repository_drift, repository_lines = check_repository(
        slug_value, repository, runner
    )

    print("Ruleset (policy/ruleset-main.json):")
    if ruleset_diff:
        for line in ruleset_diff:
            print(line)
    else:
        print("  PASS normalized live ruleset matches the committed subset")

    print()
    print("Repository settings (policy/repository.json):")
    for line in repository_lines:
        print(line)

    print()
    if ruleset_diff or repository_drift:
        print("FAIL: live GitHub state does not match the committed policy")
        return 1
    print("PASS: live GitHub state matches the committed policy")
    return 0


def apply_policy(slug_value, ruleset, repository, runner):
    """Write the committed policy to GitHub, then let run_check re-read it."""
    ruleset_id = _ruleset_id(slug_value, ruleset.get("name", "main"), runner)
    gh_api(
        [f"repos/{slug_value}/rulesets/{ruleset_id}", "-X", "PUT", "--input", "-"],
        runner=runner,
        stdin=json.dumps(ruleset),
    )

    patch_args = [f"repos/{slug_value}", "-X", "PATCH"]
    for path, value in flatten(repository).items():
        if isinstance(value, bool):
            patch_args.extend(["-F", f"{_bracket(path)}={str(value).lower()}"])
        else:
            patch_args.extend(["-f", f"{_bracket(path)}={value}"])
    gh_api(patch_args, runner=runner)


def _build_parser():
    parser = argparse.ArgumentParser(
        description="Compare live GitHub policy with the committed policy files."
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--check",
        dest="mode",
        action="store_const",
        const="check",
        help="read-only drift check (default)",
    )
    mode.add_argument(
        "--apply",
        dest="mode",
        action="store_const",
        const="apply",
        help="apply the committed policy, then re-read and check",
    )
    parser.set_defaults(mode="check")
    return parser


def main(argv=None, runner=None):
    runner = runner or _run
    args = _build_parser().parse_args(argv)

    try:
        slug_value = slug(runner)
        ruleset = _load_json(RULESET_FILE)
        repository = _load_json(REPOSITORY_FILE)
        if args.mode == "apply":
            apply_policy(slug_value, ruleset, repository, runner)
            print("Applied committed policy; re-reading live state.\n")
        return run_check(slug_value, ruleset, repository, runner)
    except PolicyError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())

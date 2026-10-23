"""Prove the native suite produces one identical result over twenty runs.

``pio test`` output is not a stable interface: stdout carries ``path:line:``
prefixes, both streams carry durations, a failure row inserts an assertion
message before the tab, and PlatformIO's aggregate summary appears on stderr and
does not correspond one-to-one with Unity cases. Comparing raw output would be a
false determinism signal (D-14, research Pitfall 8).

``digest`` therefore keeps only a per-line anchored ``suite/test_name: STATUS``
row plus counts derived from those rows. Twenty consecutive runs must produce one
identical digest, every run must exit zero, and the digest must contain a row for
each of the seven suites so an accidentally empty or partial run cannot pass.

``RUNS`` is the phase contract and is deliberately not overridable: a narrower
local check is the single ``pio test -d tests -e native`` command, not a
configurable proof. A missing ``pio`` fails the test instead of skipping it.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import unittest

PIO = "pio"
RUNS = 20
TIMEOUT_SECONDS = 300

REQUIRED_SUITES = (
    "test_common_timing",
    "test_host_fake_time",
    "test_port_contracts",
    "test_common_ring_buffer",
    "test_common_crc",
    "test_common_hex",
    "test_host_fakes",
)

# The suite is the ``test_<area>`` directory that owns the file. The optional
# ``: .*?`` absorbs the assertion message Unity inserts before the tab on a
# failure. Per-line anchored by design: never ``findall`` over the whole buffer.
TEST_LINE = re.compile(
    r"^test/(?P<suite>test_[^/]+)/[^:]+:\d+: "
    r"(?P<name>\w+)(?:: .*?)?\t\[(?P<status>PASSED|FAILED|IGNORED)\]$"
)


def digest(stdout: str) -> str:
    """Normalize suite output to ordered test rows and counts derived from them.

    Everything else -- paths, line numbers, assertion messages, durations and
    PlatformIO's summary table -- is dropped. stderr is never read.
    """
    rows = []
    for line in stdout.splitlines():
        match = TEST_LINE.match(line)
        if match:
            rows.append((match["suite"], match["name"], match["status"]))
    lines = [f"{suite}/{name}: {status}" for suite, name, status in rows]
    for status in ("PASSED", "FAILED", "IGNORED"):
        lines.append(f"{status.lower()}={sum(1 for row in rows if row[2] == status)}")
    return "\n".join(lines)


def _require_pio() -> None:
    """Fail, never skip, when PlatformIO is absent (research assumption A6)."""
    if shutil.which(PIO) is None:
        raise AssertionError(
            f"required executable {PIO!r} was not found on PATH; "
            "the determinism proof fails without it and never skips"
        )


def _run_suite() -> subprocess.CompletedProcess:
    """Run one native suite invocation with an explicit timeout."""
    return subprocess.run(
        [PIO, "test", "-d", "tests", "-e", "native"],
        capture_output=True,
        text=True,
        timeout=TIMEOUT_SECONDS,
        check=False,
    )


class DigestUnitTests(unittest.TestCase):
    """The parser is pinned offline, without running PlatformIO."""

    TRANSCRIPT = (
        "test/test_common_crc/test_crc.c:12: test_crc16_check_value\t[PASSED]\n"
        "Took 0.02 seconds\n"
        "test/test_common_crc/test_crc.c:40: test_fail: Expected 2 Was 1\t[FAILED]\n"
        "test/test_host_fakes/test_fakes.c:18: test_shared_name\t[IGNORED]\n"
        "test/test_common_crc/test_crc.c:55: test_shared_name\t[PASSED]\n"
        "========== 4 test cases: 1 failed, 2 succeeded, 1 ignored ==========\n"
        "native\ttest_common_crc\tPASSED\t00:00:00.500\n"
    )

    EXPECTED = (
        "test_common_crc/test_crc16_check_value: PASSED\n"
        "test_common_crc/test_fail: FAILED\n"
        "test_host_fakes/test_shared_name: IGNORED\n"
        "test_common_crc/test_shared_name: PASSED\n"
        "passed=2\n"
        "failed=1\n"
        "ignored=1"
    )

    def test_digest_pins_the_exact_normalization(self) -> None:
        self.assertEqual(self.EXPECTED, digest(self.TRANSCRIPT))

    def test_digest_drops_paths_messages_and_durations(self) -> None:
        normalized = digest(self.TRANSCRIPT)
        for dropped in ("test_crc.c", "Took", "0.02", "Expected 2 Was 1", "00:00:00.500"):
            with self.subTest(dropped=dropped):
                self.assertNotIn(dropped, normalized)

    def test_duplicate_test_names_stay_separated_by_suite(self) -> None:
        normalized = digest(self.TRANSCRIPT)
        self.assertIn("test_common_crc/test_shared_name: PASSED", normalized)
        self.assertIn("test_host_fakes/test_shared_name: IGNORED", normalized)

    def test_digest_of_empty_output_has_zero_counts(self) -> None:
        self.assertEqual("passed=0\nfailed=0\nignored=0", digest(""))


class DeterminismTests(unittest.TestCase):
    """Twenty consecutive runs of the full suite produce one identical digest."""

    def setUp(self) -> None:
        _require_pio()

    def test_twenty_runs_produce_one_identical_digest(self) -> None:
        warm = _run_suite()
        self.assertEqual(
            0,
            warm.returncode,
            msg=f"the warm-up run failed:\n{(warm.stdout + warm.stderr)[-4000:]}",
        )

        observed = []
        for index in range(RUNS):
            completed = _run_suite()
            output = completed.stdout + completed.stderr
            if completed.returncode != 0:
                self.fail(f"run {index} exited {completed.returncode}:\n{output[-4000:]}")
            observed.append(digest(completed.stdout))

        first = observed[0]
        self.assertTrue(first.splitlines(), "the first digest is empty")

        for suite in REQUIRED_SUITES:
            with self.subTest(suite=suite):
                self.assertRegex(
                    first,
                    rf"(?m)^{re.escape(suite)}/",
                    f"the digest has no row for {suite}",
                )
        self.assertRegex(first, r"(?m)^passed=[1-9][0-9]*$", "no test passed")
        self.assertRegex(first, r"(?m)^failed=0$", "a test failed in the first run")

        for index, current in enumerate(observed[1:], start=1):
            if current == first:
                continue
            expected_rows = first.splitlines()
            actual_rows = current.splitlines()
            compared = min(len(expected_rows), len(actual_rows))
            difference = next(
                (
                    offset
                    for offset in range(compared)
                    if expected_rows[offset] != actual_rows[offset]
                ),
                None,
            )
            if difference is None:
                self.fail(
                    f"run {index} differs in row count: "
                    f"{len(expected_rows)} != {len(actual_rows)}"
                )
            self.fail(
                f"run {index} differs at row {difference}: "
                f"{expected_rows[difference]!r} != {actual_rows[difference]!r}"
            )


if __name__ == "__main__":
    unittest.main()

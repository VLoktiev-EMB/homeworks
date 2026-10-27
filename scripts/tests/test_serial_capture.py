"""Tests for scripts/serial_capture.py.

The suite never requires hardware and never skips: every fake serial source is
a `sys.executable -c` child. The PTY test proves the child sees stdin and
stdout as terminals and that raw capture preserves `bytes(range(256))`; the
pipe test runs the same child without a terminal and proves it fails, so a
pipe-based regression cannot pass. The credential cases pin the six shapes the
09-REVIEW.md CR-02 finding executed, the four ordinary password assignments
WR-12 added, and the identifier-suffixed assignments RR-CR-01 added plus the
long-suffix case CR-01 added, and the write cases cover the root anchor, symlink
refusals, replace-not-append and concurrent writers.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest import mock

from scripts import serial_capture

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "serial_capture.py"

HOMEWORK = "1_3-police-flasher"
PORT = "/dev/cu.usbmodem2101"

# The shape `pio device list --json-output` reports on this host: the two
# non-USB entries PlatformIO always lists plus the ESP32-S3 native USB port.
SERIAL_DEVICES = [
    {"port": "/dev/cu.debug-console", "description": "n/a", "hwid": "n/a"},
    {"port": "/dev/cu.Bluetooth-Incoming-Port", "description": "n/a", "hwid": "n/a"},
    {
        "port": PORT,
        "description": "USB JTAG/serial debug unit",
        "hwid": "USB VID:PID=303A:1001 SER=AC:27:6E:AA:81:4C LOCATION=2-1",
    },
]

# The CH343 UART bridge, present when the board is connected through both
# cables: a second plausible port that must never be chosen silently.
SECOND_USB_DEVICE = {
    "port": "/dev/cu.usbmodem5CBC0287411",
    "description": "USB Single Serial",
    "hwid": "USB VID:PID=1A86:55D3 SER=5CBC0287411",
}

# The six exact samples from 09-REVIEW.md CR-02, then the four ordinary password
# assignments the WR-12 finding proved the scan missed.
REVIEW_SHAPES = (
    b"secret = hunter2",
    b"PASSWORD = hunter2",
    b'{"token": "abc123"}',
    b'{"apiKey": "abc123"}',
    b"password abc123",
    b"Authorization: Bearer eyJhbGciOiJIUzI1NiJ9",
    b"password is hunter2",
    b"userpassword = hunter2",
    b"passphrase = hunter2",
    b"pwd = hunter2",
)

ORDINARY_PASSWORD_ASSIGNMENTS = (
    b"password is hunter2",
    b"userpassword = hunter2",
    b"passphrase = hunter2",
    b"pwd = hunter2",
)

# The RR-CR-01 shapes: a keyword followed by identifier characters before the
# separator, which the shipped scan used to miss. The last entry is CR-01: its
# suffix is longer than the former 32-character connector ceiling, so the old
# bound cannot return without failing this tuple.
IDENTIFIER_SUFFIXED_ASSIGNMENTS = (
    b'{"secretKey": "hunter2"}',
    b"secret_key = hunter2",
    b"passwordHash: abcdef",
    b"SECRET_KEY = hunter2",
    b"secret_key_for_production_environment_2026 = hunter2",
)


def child_that_writes(payload: bytes) -> str:
    """Return a child program that writes *payload* and then sleeps past the bound.

    The child exits 9 unless both stdin and stdout are terminals, so the PTY
    test has teeth: a pipe-based capture cannot satisfy it.
    """
    return (
        "import sys, time\n"
        "if not (sys.stdin.isatty() and sys.stdout.isatty()):\n"
        "    sys.exit(9)\n"
        f"sys.stdout.buffer.write({payload!r})\n"
        "sys.stdout.buffer.flush()\n"
        "time.sleep(10)\n"
    )


class CapturePtyTests(unittest.TestCase):
    """PTY capture preserves raw bytes and refuses every early exit."""

    def test_capture_preserves_every_byte_and_sees_a_tty(self) -> None:
        payload = bytes(range(256)) + b"\x03\x00"

        captured = serial_capture.capture_pty(
            [sys.executable, "-c", child_that_writes(payload)], 0.5
        )

        self.assertEqual(payload, captured)

    def test_a_pipe_capture_would_fail_the_same_child(self) -> None:
        completed = subprocess.run(
            [sys.executable, "-c", child_that_writes(b"pipe capture\n")],
            stdin=subprocess.PIPE,
            capture_output=True,
            timeout=30,
            check=False,
        )

        self.assertNotEqual(0, completed.returncode)

    def test_capture_fails_when_the_command_cannot_start(self) -> None:
        with self.assertRaises(serial_capture.CaptureFailed) as caught:
            serial_capture.capture_pty(["/nonexistent/serial-capture-child"], 0.5)

        self.assertIn("cannot start", str(caught.exception))

    def test_capture_fails_on_an_early_nonzero_exit(self) -> None:
        program = (
            "import sys\n"
            "sys.stdout.buffer.write(b'x')\n"
            "sys.stdout.buffer.flush()\n"
            "sys.exit(3)\n"
        )

        with self.assertRaises(serial_capture.CaptureFailed) as caught:
            serial_capture.capture_pty([sys.executable, "-c", program], 5)

        message = str(caught.exception)
        self.assertIn("before the bound", message)
        self.assertIn("3", message)

    def test_capture_fails_on_an_early_zero_exit(self) -> None:
        with self.assertRaises(serial_capture.CaptureFailed) as caught:
            serial_capture.capture_pty(
                [sys.executable, "-c", "import sys; sys.exit(0)"], 5
            )

        message = str(caught.exception)
        self.assertIn("before the bound", message)
        self.assertIn("0", message)

    def test_capture_stops_at_the_deadline(self) -> None:
        started = time.monotonic()

        captured = serial_capture.capture_pty(
            [sys.executable, "-c", "import time; time.sleep(10)"], 0.3
        )

        elapsed = time.monotonic() - started
        self.assertEqual(b"", captured)
        self.assertLess(elapsed, 5.0)


class CaptureReapTests(unittest.TestCase):
    """An exception escaping the read loop still kills and reaps the child."""

    def test_an_exception_escaping_the_loop_reaps_the_child(self) -> None:
        created: list[subprocess.Popen] = []
        real_popen = subprocess.Popen

        def recording_popen(*args, **kwargs):
            process = real_popen(*args, **kwargs)
            created.append(process)
            return process

        def cleanup() -> None:
            for process in created:
                if process.poll() is None:
                    process.kill()
                    process.wait()

        self.addCleanup(cleanup)

        with (
            mock.patch.object(serial_capture.subprocess, "Popen", recording_popen),
            mock.patch.object(
                serial_capture.select, "select", side_effect=RuntimeError("boom")
            ),
        ):
            with self.assertRaises(RuntimeError):
                serial_capture.capture_pty(
                    [sys.executable, "-c", "import time; time.sleep(10)"], 5
                )

        self.assertEqual(1, len(created))
        self.assertIsNotNone(created[0].returncode)


class CredentialScanTests(unittest.TestCase):
    """The widened scan matches every review shape and stays boolean."""

    def test_the_review_shapes_match(self) -> None:
        for sample in REVIEW_SHAPES:
            with self.subTest(sample=sample):
                self.assertTrue(serial_capture.find_credential(sample))

    def test_the_ordinary_password_assignments_match(self) -> None:
        for sample in ORDINARY_PASSWORD_ASSIGNMENTS:
            with self.subTest(sample=sample):
                self.assertTrue(serial_capture.find_credential(sample))

    def test_identifier_suffixed_assignments_match(self) -> None:
        for sample in IDENTIFIER_SUFFIXED_ASSIGNMENTS:
            with self.subTest(sample=sample):
                self.assertTrue(serial_capture.find_credential(sample))

    def test_a_connector_longer_than_32_characters_matches(self) -> None:
        for suffix_length in (32, 33, 42):
            sample = b"secret" + b"k" * suffix_length + b" = hunter2"
            with self.subTest(suffix_length=suffix_length):
                self.assertTrue(serial_capture.find_credential(sample))

    def test_an_ordinary_word_containing_a_keyword_does_not_match(self) -> None:
        for sample in (
            b"the cpwd tool reports ready\r\n",
            b"author wrote nothing here\r\n",
            b"auth mode = WPA2\r\n",
        ):
            with self.subTest(sample=sample):
                self.assertFalse(serial_capture.find_credential(sample))

    def test_passwd_matches(self) -> None:
        self.assertTrue(serial_capture.find_credential(b"passwd = hunter2"))

    def test_uppercase_password_matches(self) -> None:
        self.assertTrue(serial_capture.find_credential(b"PASSWORD: hunter2"))

    def test_a_space_separated_value_of_six_characters_matches(self) -> None:
        self.assertTrue(serial_capture.find_credential(b"password abc123"))

    def test_a_short_space_separated_word_does_not_match(self) -> None:
        self.assertFalse(serial_capture.find_credential(b"secret is"))

    def test_a_benign_boot_log_does_not_match(self) -> None:
        boot_log = (
            b"ESP-ROM:esp32s3-20210327\r\n"
            b"Build:Mar 27 2021\r\n"
            b"rst:0x1 (POWERON),boot:0x8 (SPI_FAST_FLASH_BOOT)\r\n"
            b"entry 0x403c88dc\r\n"
        )

        self.assertFalse(serial_capture.find_credential(boot_log))

    def test_the_scan_returns_a_boolean(self) -> None:
        self.assertIs(bool, type(serial_capture.find_credential(b"boot ok")))


class AtomicLogWriteTests(unittest.TestCase):
    """The write is root-anchored, symlink-refusing, replace-only and whole."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="serial-capture-write-")
        self.addCleanup(self._tmp.cleanup)
        self.root = (Path(self._tmp.name) / "root").resolve()
        self.root.mkdir()

    def log_path(self) -> Path:
        return self.root / ".skill-state" / "logs" / f"{HOMEWORK}.log"

    def temporary_files(self, directory: Path) -> list[str]:
        return sorted(
            item.name for item in directory.iterdir() if item.name.startswith(".capture-")
        )

    def test_writes_the_log_under_the_root_with_no_temporary_file(self) -> None:
        payload = bytes(range(256))

        path = serial_capture.write_log_atomically(self.root, HOMEWORK, payload)

        self.assertEqual(self.log_path(), path)
        self.assertTrue(path.resolve().is_relative_to(self.root.resolve()))
        self.assertEqual(payload, path.read_bytes())
        self.assertEqual([], self.temporary_files(path.parent))

    def test_a_second_write_replaces_rather_than_appends(self) -> None:
        serial_capture.write_log_atomically(self.root, HOMEWORK, b"first payload")

        serial_capture.write_log_atomically(self.root, HOMEWORK, b"second")

        self.assertEqual(b"second", self.log_path().read_bytes())

    def test_creates_the_state_directory_when_absent(self) -> None:
        serial_capture.write_log_atomically(self.root, HOMEWORK, b"data")

        self.assertTrue((self.root / ".skill-state" / "logs").is_dir())

    def test_refuses_a_symlinked_state_directory(self) -> None:
        outside = Path(self._tmp.name) / "outside"
        outside.mkdir()
        (self.root / ".skill-state").symlink_to(outside, target_is_directory=True)

        with self.assertRaises(serial_capture.CaptureFailed):
            serial_capture.write_log_atomically(self.root, HOMEWORK, b"data")

        self.assertFalse((outside / "logs").exists())

    def test_refuses_a_symlinked_logs_directory(self) -> None:
        state = self.root / ".skill-state"
        state.mkdir()
        outside = Path(self._tmp.name) / "outside"
        outside.mkdir()
        (state / "logs").symlink_to(outside, target_is_directory=True)

        with self.assertRaises(serial_capture.CaptureFailed):
            serial_capture.write_log_atomically(self.root, HOMEWORK, b"data")

        self.assertFalse((outside / f"{HOMEWORK}.log").exists())

    def test_refuses_a_symlinked_log_file(self) -> None:
        logs = self.root / ".skill-state" / "logs"
        logs.mkdir(parents=True)
        outside = Path(self._tmp.name) / "outside.log"
        outside.write_bytes(b"untouched")
        (logs / f"{HOMEWORK}.log").symlink_to(outside)

        with self.assertRaises(serial_capture.CaptureFailed):
            serial_capture.write_log_atomically(self.root, HOMEWORK, b"data")

        self.assertEqual(b"untouched", outside.read_bytes())
        self.assertEqual([], self.temporary_files(logs))

    def test_concurrent_writes_leave_one_whole_payload(self) -> None:
        payloads = (b"a" * 4096, b"b" * 4096)
        errors: list[BaseException] = []

        def writer(payload: bytes) -> None:
            try:
                serial_capture.write_log_atomically(self.root, HOMEWORK, payload)
            except BaseException as exc:  # reported below, never swallowed
                errors.append(exc)

        threads = [
            threading.Thread(target=writer, args=(payload,)) for payload in payloads
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=30)

        self.assertEqual([], errors)
        final = self.log_path().read_bytes()
        self.assertIn(final, payloads)
        self.assertEqual([], self.temporary_files(self.log_path().parent))

    def test_a_concurrent_reader_never_sees_a_torn_log(self) -> None:
        payloads = (b"a" * 4096, b"b" * 4096)
        serial_capture.write_log_atomically(self.root, HOMEWORK, payloads[0])
        errors: list[BaseException] = []
        observed: list[bytes] = []

        def writer(payload: bytes) -> None:
            try:
                for _ in range(40):
                    serial_capture.write_log_atomically(self.root, HOMEWORK, payload)
            except BaseException as exc:  # reported below, never swallowed
                errors.append(exc)

        def reader() -> None:
            try:
                for _ in range(1000):
                    try:
                        observed.append(self.log_path().read_bytes())
                    except FileNotFoundError:
                        pass
                    time.sleep(0.001)
            except BaseException as exc:  # reported below, never swallowed
                errors.append(exc)

        writers = [threading.Thread(target=writer, args=(payload,)) for payload in payloads]
        reader_thread = threading.Thread(target=reader)
        reader_thread.start()
        for thread in writers:
            thread.start()
        for thread in writers:
            thread.join(timeout=60)
        reader_thread.join(timeout=60)

        self.assertEqual([], errors)
        self.assertNotEqual([], observed)
        for value in observed:
            self.assertIn(value, payloads)


class CaptureAndStoreTests(unittest.TestCase):
    """The shipped path scans before the filesystem is touched."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="serial-capture-store-")
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name).resolve()
        self.log_path = self.root / ".skill-state" / "logs" / f"{HOMEWORK}.log"

    def test_a_benign_child_writes_the_log(self) -> None:
        payload = b"\x00boot ok\r\n"
        argv = [sys.executable, "-c", child_that_writes(payload)]

        path, count = serial_capture.capture_and_store(self.root, HOMEWORK, argv, 0.4)

        self.assertEqual(self.log_path, path)
        self.assertEqual(len(payload), count)
        self.assertEqual(payload, path.read_bytes())

    def test_a_credential_child_writes_nothing(self) -> None:
        argv = [sys.executable, "-c", child_that_writes(b"password hunter2\r\n")]

        with self.assertRaises(serial_capture.CaptureFailed) as caught:
            serial_capture.capture_and_store(self.root, HOMEWORK, argv, 0.4)

        self.assertIn("credential", str(caught.exception))
        self.assertFalse(self.log_path.exists())
        self.assertFalse((self.root / ".skill-state").exists())

    def test_an_identifier_suffixed_credential_child_writes_nothing(self) -> None:
        argv = [
            sys.executable,
            "-c",
            child_that_writes(b'{"secretKey": "hunter2"}\r\n'),
        ]

        with self.assertRaises(serial_capture.CaptureFailed) as caught:
            serial_capture.capture_and_store(self.root, HOMEWORK, argv, 0.4)

        self.assertIn("credential", str(caught.exception))
        self.assertFalse(self.log_path.exists())
        self.assertFalse((self.root / ".skill-state").exists())

    def test_an_empty_child_writes_nothing(self) -> None:
        argv = [sys.executable, "-c", "import time; time.sleep(10)"]

        with self.assertRaises(serial_capture.CaptureFailed) as caught:
            serial_capture.capture_and_store(self.root, HOMEWORK, argv, 0.4)

        self.assertIn("no bytes captured", str(caught.exception))
        self.assertFalse(self.log_path.exists())


class CliUsageTests(unittest.TestCase):
    """Invalid input is rejected before any monitor argv is assembled."""

    def run_cli(self, *arguments: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *arguments],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )

    def assert_usage_error(self, result: subprocess.CompletedProcess) -> None:
        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("ERROR:", result.stderr)
        self.assertEqual("", result.stdout)

    def test_an_invalid_id_is_rejected_before_any_capture(self) -> None:
        self.assert_usage_error(self.run_cli("--id", "not-an-id", "--seconds", "1"))

    def test_a_zero_baud_is_a_usage_error(self) -> None:
        self.assert_usage_error(
            self.run_cli("--id", HOMEWORK, "--baud", "0", "--seconds", "1")
        )

    def test_a_zero_duration_is_a_usage_error(self) -> None:
        self.assert_usage_error(self.run_cli("--id", HOMEWORK, "--seconds", "0"))


class CliDurationTests(unittest.TestCase):
    """A non-finite or oversized duration is a usage error before any capture."""

    def run_main(self, seconds: str) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with (
            mock.patch.object(
                serial_capture,
                "capture_pty",
                side_effect=AssertionError("capture started"),
            ),
            contextlib.redirect_stdout(stdout),
            contextlib.redirect_stderr(stderr),
        ):
            code = serial_capture.main(["--id", HOMEWORK, "--seconds", seconds])
        return code, stdout.getvalue(), stderr.getvalue()

    def assert_duration_usage_error(self, seconds: str) -> None:
        code, stdout, stderr = self.run_main(seconds)

        self.assertEqual(2, code, stderr)
        self.assertIn("ERROR:", stderr)
        self.assertIn("positive finite", stderr)
        self.assertEqual("", stdout)

    def test_nan_is_a_usage_error(self) -> None:
        self.assert_duration_usage_error("nan")

    def test_infinity_is_a_usage_error(self) -> None:
        self.assert_duration_usage_error("inf")

    def test_an_oversized_bound_is_a_usage_error(self) -> None:
        self.assert_duration_usage_error("601")


class PortResolutionTests(unittest.TestCase):
    """Exactly one USB serial device is selected, never guessed."""

    def test_one_usb_device_is_selected_among_non_usb_entries(self) -> None:
        identity = serial_capture.resolve_port(None, SERIAL_DEVICES)

        self.assertEqual(PORT, identity.path)
        self.assertEqual("303A", identity.vid)
        self.assertEqual("1001", identity.pid)

    def test_two_usb_devices_refuse_as_ambiguous(self) -> None:
        devices = SERIAL_DEVICES + [SECOND_USB_DEVICE]

        with self.assertRaises(serial_capture.CaptureFailed) as caught:
            serial_capture.resolve_port(None, devices)

        message = str(caught.exception)
        self.assertIn("ambiguous", message)
        self.assertIn(PORT, message)
        self.assertIn(SECOND_USB_DEVICE["port"], message)
        self.assertIn("--port", message)

    def test_a_list_without_a_usb_device_refuses(self) -> None:
        for devices in ([], SERIAL_DEVICES[:2]):
            with self.subTest(devices=devices):
                with self.assertRaises(serial_capture.CaptureFailed) as caught:
                    serial_capture.resolve_port(None, devices)

                self.assertIn("no USB serial device", str(caught.exception))

    def test_an_explicit_port_disambiguates_the_pair(self) -> None:
        identity = serial_capture.resolve_port(
            SECOND_USB_DEVICE["port"], SERIAL_DEVICES + [SECOND_USB_DEVICE]
        )

        self.assertEqual(SECOND_USB_DEVICE["port"], identity.path)
        self.assertEqual("1A86", identity.vid)
        self.assertEqual("55D3", identity.pid)

    def test_an_explicit_port_absent_from_the_list_refuses(self) -> None:
        with self.assertRaises(serial_capture.CaptureFailed) as caught:
            serial_capture.resolve_port("/dev/cu.usbmodem9999", SERIAL_DEVICES)

        self.assertIn("--port", str(caught.exception))

    def test_valid_port_path_accepts_an_absolute_device_path(self) -> None:
        self.assertTrue(serial_capture._valid_port_path(PORT))

    def test_valid_port_path_rejects_relative_and_outside_paths(self) -> None:
        for value in ("usbmodem2101", "/etc/passwd", "/dev/../etc/passwd"):
            with self.subTest(value=value):
                self.assertFalse(serial_capture._valid_port_path(value))


class CaptureEndToEndTests(unittest.TestCase):
    """The whole path resolves a port, captures raw bytes and reports identity."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="serial-capture-e2e-")
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name).resolve()
        self.log_path = self.root / ".skill-state" / "logs" / f"{HOMEWORK}.log"

    def run_json(self, *arguments: str) -> tuple[int, str]:
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            code = serial_capture.main(list(arguments))
        return code, buffer.getvalue()

    def test_a_capture_reports_the_port_vid_pid_and_baud(self) -> None:
        payload = b"I pattern ready\r\n"
        child = [sys.executable, "-c", child_that_writes(payload)]

        with (
            mock.patch.object(
                serial_capture, "list_serial_devices", return_value=SERIAL_DEVICES
            ),
            mock.patch.object(serial_capture, "_build_command", return_value=child),
        ):
            code, output = self.run_json(
                "--id",
                HOMEWORK,
                "--dir",
                str(self.root),
                "--json",
                "--baud",
                "115200",
                "--seconds",
                "0.4",
            )

        self.assertEqual(0, code, output)
        self.assertEqual(payload, self.log_path.read_bytes())
        captured = json.loads(output.strip())
        self.assertEqual("CAPTURED", captured["status"])
        self.assertEqual(PORT, captured["port"])
        self.assertEqual("303A:1001", captured["vid_pid"])
        self.assertEqual(115200, captured["baud"])

    def test_an_ambiguous_port_refuses_before_the_capture_starts(self) -> None:
        with (
            mock.patch.object(
                serial_capture,
                "list_serial_devices",
                return_value=SERIAL_DEVICES + [SECOND_USB_DEVICE],
            ),
            mock.patch.object(
                serial_capture,
                "capture_pty",
                side_effect=AssertionError("capture started"),
            ),
        ):
            code, output = self.run_json(
                "--id", HOMEWORK, "--dir", str(self.root), "--json", "--seconds", "0.4"
            )

        self.assertEqual(1, code, output)
        refused = json.loads(output.strip())
        self.assertEqual("REFUSED", refused["status"])
        self.assertIn("ambiguous", refused["reason"])
        self.assertIsNone(refused["port"])
        self.assertFalse(self.log_path.exists())


class BuildCommandTests(unittest.TestCase):
    """The monitor argv always names one port and opens it in the idle line state."""

    def build(self, **flags: object) -> list[str]:
        args = argparse.Namespace(id=HOMEWORK, env=None, baud=None)
        for name, value in flags.items():
            setattr(args, name, value)
        return serial_capture._build_command(args, PORT)

    def test_the_monitor_opens_in_the_idle_line_state_with_an_explicit_port(self) -> None:
        self.assertEqual(
            [
                "pio",
                "device",
                "monitor",
                "-d",
                "homeworks/" + HOMEWORK,
                "-p",
                PORT,
                "--dtr",
                "0",
                "--rts",
                "0",
                "--raw",
                "--quiet",
            ],
            self.build(),
        )

    def test_env_is_forwarded(self) -> None:
        self.assertEqual(["-e", "esp32-s3"], self.build(env="esp32-s3")[-2:])

    def test_baud_is_forwarded_as_dash_b(self) -> None:
        argv = self.build(baud=115200)

        self.assertEqual(["-b", "115200"], argv[-2:])
        self.assertNotIn("--baud", argv)

    def test_env_and_baud_together(self) -> None:
        self.assertEqual(
            ["-e", "esp32-s3", "-b", "115200"],
            self.build(env="esp32-s3", baud=115200)[-4:],
        )


class CliResultPayloadTests(unittest.TestCase):
    """`main`'s --json payload and exit code are the helper's public contract."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="serial-capture-cli-")
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name).resolve()

    def run_json(self, *arguments: str) -> tuple[int, str]:
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            code = serial_capture.main(list(arguments))
        return code, buffer.getvalue()

    def test_a_json_success_payload(self) -> None:
        target = self.root / ".skill-state" / "logs" / f"{HOMEWORK}.log"

        with (
            mock.patch.object(
                serial_capture, "list_serial_devices", return_value=SERIAL_DEVICES
            ),
            mock.patch.object(
                serial_capture, "capture_and_store", return_value=(target, 17)
            ),
        ):
            code, output = self.run_json(
                "--id", HOMEWORK, "--dir", str(self.root), "--json", "--baud", "115200"
            )

        self.assertEqual(0, code)
        self.assertEqual(
            {
                "path": f".skill-state/logs/{HOMEWORK}.log",
                "status": "CAPTURED",
                "reason": "17 bytes captured",
                "bytes": 17,
                "port": PORT,
                "vid_pid": "303A:1001",
                "baud": 115200,
            },
            json.loads(output.strip()),
        )

    def test_a_json_refusal_payload(self) -> None:
        refusal = serial_capture.CaptureFailed("credential-shaped device output")

        with (
            mock.patch.object(
                serial_capture, "list_serial_devices", return_value=SERIAL_DEVICES
            ),
            mock.patch.object(
                serial_capture, "capture_and_store", side_effect=refusal
            ),
        ):
            code, output = self.run_json(
                "--id", HOMEWORK, "--dir", str(self.root), "--json", "--baud", "115200"
            )

        self.assertEqual(1, code)
        payload = json.loads(output.strip())
        self.assertEqual("REFUSED", payload["status"])
        self.assertIn("capture unavailable", payload["reason"])
        self.assertEqual(0, payload["bytes"])
        self.assertEqual(PORT, payload["port"])
        self.assertEqual("303A:1001", payload["vid_pid"])
        self.assertEqual(115200, payload["baud"])


if __name__ == "__main__":
    unittest.main()

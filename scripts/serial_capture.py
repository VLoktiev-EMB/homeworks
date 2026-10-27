#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# ///
"""Capture a bounded serial log from `pio device monitor` through a pseudo-terminal.

PlatformIO 6.2.0 refuses to run `pio device monitor` unless its stdin and stdout
are interactive terminals, so piping the monitor's stdout makes every capture
exit before the bound. This helper allocates a pseudo-terminal, puts the slave
side in raw mode, runs the monitor on it, and reads the master side for a
bounded interval.

The child is started as
`pio device monitor -d homeworks/<id> -p <port> --dtr 0 --rts 0 --raw --quiet`,
plus `-e <env>` and `-b <baud>` only when the caller supplies them. `-p` pins
the interface, `--dtr 0 --rts 0` opens it in the idle line state (the asserted
pair is the ESP32-S3 chip-reset state, so the application would never run and
the capture would collect nothing), `--raw` keeps the device bytes
untransformed, and `--quiet` keeps PlatformIO's terminal banner out of the
captured stream, so the log holds exactly the bytes the scan below inspected.

The port is resolved before the monitor starts. `pio device list
--json-output` is filtered to entries whose `hwid` matches
`USB VID:PID=<vid>:<pid>`; `--port` names one such path explicitly, and
omitting it requires exactly one candidate. Zero candidates refuse with `no
USB serial device found`, and two or more refuse as ambiguous, naming every
candidate and `--port`: two ports on one board (its native USB interface and
its UART bridge) are a real ambiguity the user breaks, never one the helper
guesses. `--port` must be an absolute path under `/dev` with no `..`
component, and a path `pio device list` does not report as a USB serial device
is refused.

The effective baud is `--baud` when supplied, otherwise the selected
environment's `monitor_speed` read through `pio project config`. An absent or
non-positive `monitor_speed`, an environment that cannot be chosen, or a
missing section is a usage error: PlatformIO's implicit 9600 fallback is never
used silently.

The 20-second default bound is the designed end of a capture, not a failure:
the bytes collected up to it are the log. A capture is refused when the command
cannot start, when the monitor exits before the bound (zero or non-zero exit),
when no bytes are collected, when the credential scan matches, or when the log
write is refused. Every refusal reports `capture unavailable`.

The credential scan is fail-closed and runs on the exact bytes before any file
is created. It matches a token, secret, password, passwd, passphrase, pwd,
API-key or auth/authorization keyword. The keyword may sit inside a larger word
on either side: it may follow another word (`userpassword`) or precede
identifier characters (`secretKey`, `secret_key`, `passwordHash`). The
assignment branch admits a connector of at most 128 word, dot or hyphen
characters before the optional quote and the colon or equals sign, then
optional whitespace, an optional quote and a non-space run. The space-separated
branch is unchanged: whitespace, an optional `is` copula, and a non-space run
of six or more characters. Occasional false positives are accepted because a
match writes nothing and reports `capture unavailable`; a match on a benign
boot log is a regression the suite forbids. The match is never returned,
printed or stored.

The log is written to `<root>/.skill-state/logs/<id>.log` where `<root>` is
resolved once. Each directory is opened with `O_DIRECTORY | O_NOFOLLOW` and
every operation below it is relative to that directory descriptor, so a
component swapped for a symlink is refused rather than followed. The temporary
file is created exclusively with mode `0o600` and replaced onto the destination
through the same descriptor; a repeated run replaces the log rather than
appending to it.

The `--json` object and the human `CAPTURED` line name the resolved device
path, its `VID:PID` and the effective baud, so a log can be traced to the
interface that produced it. The log itself stays exactly the raw device bytes:
no header and no sidecar.

Usage:
  uv run scripts/serial_capture.py --id ID [--port PATH] [--env NAME]
                                   [--baud N] [--seconds SECONDS]
                                   [--dir PATH] [--json]

`--seconds` must be a positive finite number no greater than `MAX_SECONDS`
(600); anything else is a usage error, decided before any process starts.

Exit codes (the vocabulary shared with `check_metadata.py`, D-23):
  0  the bound was reached and the log was written
  1  `capture unavailable` — the command could not start, exited before the
     bound, produced no bytes, matched the credential scan, the write was
     refused, no USB serial device was found, several were found without
     `--port`, or a named port is not a reported USB serial device
  2  usage or environment error (an invalid id, environment, port, baud or
     duration, a duration outside the positive-finite bound, an unresolvable
     repository root or `monitor_speed`)
"""

from __future__ import annotations

import argparse
import json
import math
import os
import pty
import re
import select
import stat
import subprocess
import sys
import time
import tty
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.metadata.errors import CheckError  # noqa: E402
from scripts.metadata.paths import HOMEWORK_ID, relative_path, resolve_root  # noqa: E402

DEFAULT_SECONDS = 20
# A sanity cap on the requested bound, not the designed capture length: a
# huge finite value overflows the same `select` timeout a non-finite one does.
MAX_SECONDS = 600
READ_SIZE = 4096
LOG_PARTS = (".skill-state", "logs")
# A device or configuration query must answer promptly; a hung `pio` process is
# a refusal, not a capture that waits forever.
DEVICE_QUERY_TIMEOUT = 15

# `pio device list` reports a USB serial port as
# `USB VID:PID=303A:1001 SER=...`; the non-USB entries report `n/a`.
USB_HWID = re.compile(r"USB VID:PID=([0-9A-Fa-f]{4}):([0-9A-Fa-f]{4})")

# The keyword set the shared guardrails name: `password`, `passwd`,
# `passphrase` and `pwd` share one `pass(?:word|wd|phrase)|pwd` alternative.
# The keyword may follow another word (`userpassword = hunter2`), so no leading
# boundary is required, and the space-separated branch admits the `is` copula
# (`password is hunter2`). In the assignment branch a keyword may instead be
# followed by identifier characters (`secretKey`, `secret_key`, `passwordHash`),
# so a `[\w.-]{0,128}` connector of at most 128 word, dot or hyphen characters is
# admitted before the optional quote and separator; the space-separated branch
# is unchanged. The six-character floor on that branch keeps ordinary words such
# as `secret is` unmatched. Occasional false positives are accepted, because a
# match writes nothing and reports `capture unavailable`, and a match on a
# benign boot log is a regression the suite forbids.
_KEYWORDS = (
    rb"(?:authorization|auth|token|secret(?:[ _-]?key)?|pass(?:word|wd|phrase)"
    rb"|pwd|api[ _-]?key)"
)

CREDENTIAL = re.compile(
    rb"(?i)"
    + _KEYWORDS
    + rb"(?:[\w.-]{0,128}[\"']?\s*[:=]\s*[\"']?\S+|\s+(?:is\s+)?\S{6,})"
)

ENVIRONMENT = re.compile(r"^[A-Za-z0-9_-]+$")


class CaptureFailed(Exception):
    """A capture refusal; the message is the reason reported to the user."""


@dataclass(frozen=True)
class PortIdentity:
    """One USB serial port: its device path and its reported USB identity."""

    path: str
    vid: str
    pid: str


def find_credential(data: bytes) -> bool:
    """Return whether *data* contains a credential-shaped assignment.

    The matched span is never returned, printed or stored: a caller only learns
    that the scan matched.
    """
    return CREDENTIAL.search(data) is not None


def _run_json(argv: list[str]) -> object:
    """Run *argv* and return its decoded JSON output, refusing on any failure.

    The refusal names the failure class only: the child's stderr may echo a
    device path or device bytes, and a refusal never repeats child output.
    """
    try:
        completed = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            timeout=DEVICE_QUERY_TIMEOUT,
            check=False,
        )
    except OSError as exc:
        detail = exc.strerror or type(exc).__name__
        raise CaptureFailed(f"port discovery failed: {detail}") from exc
    except subprocess.TimeoutExpired as exc:
        raise CaptureFailed("port discovery failed: timed out") from exc
    if completed.returncode != 0:
        raise CaptureFailed(f"port discovery failed: exit {completed.returncode}")
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise CaptureFailed("port discovery failed: invalid JSON") from exc


def list_serial_devices() -> list[dict]:
    """Return the serial ports `pio device list --json-output` reports."""
    payload = _run_json(["pio", "device", "list", "--json-output"])
    if not isinstance(payload, list) or not all(
        isinstance(entry, dict) for entry in payload
    ):
        raise CaptureFailed("port discovery failed: unexpected device list payload")
    return payload


def _usb_identity(entry: dict) -> PortIdentity | None:
    """Return the USB identity of one `pio device list` entry, or None."""
    port = entry.get("port")
    hwid = entry.get("hwid")
    if not isinstance(port, str) or not isinstance(hwid, str):
        return None
    match = USB_HWID.search(hwid)
    if match is None:
        return None
    return PortIdentity(
        path=port, vid=match.group(1).upper(), pid=match.group(2).upper()
    )


def resolve_port(explicit: str | None, devices: list[dict]) -> PortIdentity:
    """Return the one USB serial port to open, refusing rather than guessing.

    Two ports on one board are a real ambiguity (the native USB interface and
    the UART bridge), so the identity is never deduplicated by VID:PID: the
    user breaks the tie with `--port`.
    """
    identities = [
        identity
        for entry in devices
        if (identity := _usb_identity(entry)) is not None
    ]
    if explicit is not None:
        for identity in identities:
            if identity.path == explicit:
                return identity
        raise CaptureFailed(
            f"--port {explicit} is not a USB serial device reported by "
            "pio device list"
        )
    if not identities:
        raise CaptureFailed(
            "no USB serial device found; connect a board or pass --port"
        )
    if len(identities) > 1:
        paths = ", ".join(identity.path for identity in identities)
        raise CaptureFailed(f"ambiguous USB serial ports ({paths}); pass --port")
    return identities[0]


def _valid_port_path(value: str) -> bool:
    """Return whether *value* is an absolute device path under `/dev`."""
    path = Path(value)
    if not path.is_absolute() or not value.startswith("/dev/"):
        return False
    return ".." not in path.parts


def project_config(root: Path, homework_id: str) -> object:
    """Return `pio project config` for one homework as its decoded payload."""
    return _run_json(
        [
            "pio",
            "project",
            "config",
            "-d",
            str(Path(root) / "homeworks" / homework_id),
            "--json-output",
        ]
    )


def _config_sections(payload: object) -> dict[str, dict[str, object]]:
    """Map each `pio project config` section name to its option mapping."""
    if not isinstance(payload, list):
        raise CheckError("project configuration is not a list of sections")
    sections: dict[str, dict[str, object]] = {}
    for item in payload:
        if not isinstance(item, (list, tuple)) or len(item) != 2:
            raise CheckError("project configuration section is malformed")
        name, options = item
        if not isinstance(name, str) or not isinstance(options, (list, tuple)):
            raise CheckError("project configuration section is malformed")
        mapping: dict[str, object] = {}
        for option in options:
            if not isinstance(option, (list, tuple)) or len(option) != 2:
                raise CheckError(
                    f"project configuration option in {name} is malformed"
                )
            key, value = option
            if not isinstance(key, str):
                raise CheckError(
                    f"project configuration option in {name} is malformed"
                )
            mapping[key] = value
        sections[name] = mapping
    return sections


def _default_envs(value: object) -> list[str]:
    """Return `platformio.default_envs` as a list of environment names."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, (list, tuple)) and all(
        isinstance(item, str) for item in value
    ):
        return list(value)
    return []


def resolve_baud(explicit: int | None, config: object, env: str | None) -> int:
    """Return the baud the monitor will use, refusing an unresolvable value.

    A supplied `--baud` is returned before *config* is touched, so the explicit
    path reads no project configuration at all.
    """
    if explicit is not None:
        return explicit
    sections = _config_sections(config)
    if env is not None:
        section_name = f"env:{env}"
    else:
        defaults = _default_envs(sections.get("platformio", {}).get("default_envs"))
        if len(defaults) != 1:
            raise CheckError(
                "cannot choose an environment from the project config; pass "
                "--env or --baud"
            )
        section_name = f"env:{defaults[0]}"
    section = sections.get(section_name)
    if section is None:
        raise CheckError(
            f"{section_name} is absent from the project config; pass --env or --baud"
        )
    if "monitor_speed" not in section:
        raise CheckError(f"{section_name} has no monitor_speed; pass --baud")
    try:
        baud = int(str(section["monitor_speed"]))
    except (TypeError, ValueError) as exc:
        raise CheckError(
            f"{section_name} monitor_speed {section['monitor_speed']!r} is not "
            "an integer; pass --baud"
        ) from exc
    if baud <= 0:
        raise CheckError(
            f"{section_name} monitor_speed {baud} is not positive; pass --baud"
        )
    return baud


def _reap(process: subprocess.Popen) -> int:
    """Wait for *process*, killing it if it does not exit promptly."""
    try:
        return process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        return process.wait()


def _terminate(process: subprocess.Popen) -> None:
    """Kill *process* if it is still running, then reap it."""
    if process.poll() is None:
        process.kill()
    process.wait()


def capture_pty(argv: list[str], seconds: float) -> bytes:
    """Run *argv* on a pseudo-terminal for at most *seconds* and return its bytes."""
    try:
        master, slave = pty.openpty()
    except OSError as exc:
        raise CaptureFailed(f"command cannot start: {exc}") from exc
    process = None
    try:
        try:
            tty.setraw(slave)
            process = subprocess.Popen(
                argv,
                stdin=slave,
                stdout=slave,
                stderr=subprocess.DEVNULL,
                close_fds=True,
            )
        except OSError as exc:
            raise CaptureFailed(f"command cannot start: {exc}") from exc
        finally:
            os.close(slave)

        deadline = time.monotonic() + seconds
        chunks: list[bytes] = []
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                _terminate(process)
                return b"".join(chunks)
            ready, _, _ = select.select([master], [], [], remaining)
            if not ready:
                _terminate(process)
                return b"".join(chunks)
            try:
                chunk = os.read(master, READ_SIZE)
            except OSError as exc:
                code = _reap(process)
                raise CaptureFailed(
                    f"command exited {code} before the bound ({exc.strerror})"
                ) from exc
            if not chunk:
                code = _reap(process)
                raise CaptureFailed(f"command exited {code} before the bound")
            chunks.append(chunk)
    finally:
        if process is not None:
            _terminate(process)
        os.close(master)


def _open_directory(parent_fd: int, name: str) -> int:
    """Open *name* as a directory under *parent_fd*, never through a symlink."""
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    try:
        return os.open(name, flags, dir_fd=parent_fd)
    except FileNotFoundError:
        try:
            os.mkdir(name, 0o755, dir_fd=parent_fd)
        except FileExistsError:
            pass
        return os.open(name, flags, dir_fd=parent_fd)


def _create_temporary(logs_fd: int) -> tuple[str, int]:
    """Create a fresh `.capture-` file relative to *logs_fd*."""
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
    for _ in range(16):
        name = f".capture-{os.urandom(8).hex()}"
        try:
            return name, os.open(name, flags, 0o600, dir_fd=logs_fd)
        except FileExistsError:
            continue
    raise OSError("cannot create a unique temporary capture file")


def _write_all(descriptor: int, data: bytes) -> None:
    """Write every byte of *data* to *descriptor*."""
    view = memoryview(data)
    while view:
        written = os.write(descriptor, view)
        view = view[written:]


def write_log_atomically(root: Path, homework_id: str, data: bytes) -> Path:
    """Write *data* to the ignored per-homework log under *root* atomically."""
    if not isinstance(homework_id, str) or not HOMEWORK_ID.match(homework_id):
        raise CheckError(
            f"invalid homework id {homework_id!r}; expected module_lesson-name "
            "matching ^[0-9]+_[0-9]+-[a-z0-9-]+$"
        )
    base = Path(root).resolve()
    log_name = f"{homework_id}.log"
    target = base / LOG_PARTS[0] / LOG_PARTS[1] / log_name
    root_fd = state_fd = logs_fd = None
    temporary = None
    try:
        try:
            root_fd = os.open(base, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            state_fd = _open_directory(root_fd, LOG_PARTS[0])
            logs_fd = _open_directory(state_fd, LOG_PARTS[1])
            try:
                existing = os.stat(log_name, dir_fd=logs_fd, follow_symlinks=False)
            except FileNotFoundError:
                existing = None
            if existing is not None and stat.S_ISLNK(existing.st_mode):
                raise CaptureFailed(f"log path component is a symlink: {log_name}")
            temporary, descriptor = _create_temporary(logs_fd)
            try:
                _write_all(descriptor, data)
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
            os.replace(temporary, log_name, src_dir_fd=logs_fd, dst_dir_fd=logs_fd)
            temporary = None
        except OSError as exc:
            raise CaptureFailed(f"log write refused: {exc}") from exc
    finally:
        if temporary is not None and logs_fd is not None:
            try:
                os.unlink(temporary, dir_fd=logs_fd)
            except OSError:
                pass
        for descriptor in (logs_fd, state_fd, root_fd):
            if descriptor is not None:
                try:
                    os.close(descriptor)
                except OSError:
                    pass
    return target


def capture_and_store(
    root: Path, homework_id: str, argv: list[str], seconds: float
) -> tuple[Path, int]:
    """Capture *argv*, scan the bytes, and write the log when the scan is clean."""
    data = capture_pty(argv, seconds)
    if not data:
        raise CaptureFailed("no bytes captured")
    if find_credential(data):
        raise CaptureFailed("credential-shaped device output")
    path = write_log_atomically(root, homework_id, data)
    return path, len(data)


def _build_command(args: argparse.Namespace, port: str) -> list[str]:
    """Build the monitor argv; the id and *port* are validated before this call.

    `-p` pins the interface, and `--dtr 0 --rts 0` opens it in the idle line
    state: the asserted pair is the ESP32-S3 chip-reset state, so the
    application never runs and the capture stays empty without it.
    """
    command = [
        "pio",
        "device",
        "monitor",
        "-d",
        "homeworks/" + args.id,
        "-p",
        port,
        "--dtr",
        "0",
        "--rts",
        "0",
        "--raw",
        "--quiet",
    ]
    if args.env:
        command += ["-e", args.env]
    if args.baud is not None:
        command += ["-b", str(args.baud)]
    return command


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="serial_capture",
        description="Capture a bounded serial log from pio device monitor.",
    )
    parser.add_argument("--id", required=True, help="homework id")
    parser.add_argument("--env", help="PlatformIO environment to monitor")
    parser.add_argument(
        "--port",
        help=(
            "serial device path such as /dev/cu.usbmodem2101; omit it only when "
            "exactly one USB serial device is connected"
        ),
    )
    parser.add_argument("--baud", type=int, help="baud rate; omit to inherit monitor_speed")
    parser.add_argument(
        "--seconds",
        type=float,
        default=DEFAULT_SECONDS,
        help=f"capture bound in seconds (default: {DEFAULT_SECONDS})",
    )
    parser.add_argument("--dir", help="repository root (default: git rev-parse --show-toplevel)")
    parser.add_argument("--json", action="store_true", help="emit one JSON object")
    args = parser.parse_args(argv)

    log_display = f"{LOG_PARTS[0]}/{LOG_PARTS[1]}/{args.id}.log"
    port = None
    vid_pid = None
    baud = None
    try:
        if not HOMEWORK_ID.match(args.id):
            raise CheckError(
                f"invalid homework id {args.id!r}; expected module_lesson-name "
                "matching ^[0-9]+_[0-9]+-[a-z0-9-]+$"
            )
        if args.env is not None and not ENVIRONMENT.match(args.env):
            raise CheckError(f"invalid environment name {args.env!r}")
        if args.baud is not None and args.baud <= 0:
            raise CheckError("--baud must be a positive integer")
        if not math.isfinite(args.seconds) or args.seconds <= 0 or args.seconds > MAX_SECONDS:
            raise CheckError(
                f"--seconds must be a positive finite number no greater than {MAX_SECONDS}"
            )
        if args.port is not None and not _valid_port_path(args.port):
            raise CheckError(
                "--port must be an absolute serial device path under /dev, "
                f"not {args.port!r}"
            )
        root = resolve_root(args.dir)
        identity = resolve_port(args.port, list_serial_devices())
        port = identity.path
        vid_pid = f"{identity.vid}:{identity.pid}"
        if args.baud is None:
            baud = resolve_baud(None, project_config(root, args.id), args.env)
        else:
            baud = args.baud
        command = _build_command(args, port)
        path, count = capture_and_store(root, args.id, command, args.seconds)
    except CaptureFailed as exc:
        reason = f"capture unavailable: {exc}"
        if args.json:
            print(
                json.dumps(
                    {
                        "path": log_display,
                        "status": "REFUSED",
                        "reason": reason,
                        "bytes": 0,
                        "port": port,
                        "vid_pid": vid_pid,
                        "baud": baud,
                    }
                )
            )
        else:
            print(f"{log_display}: REFUSED — {reason}")
        return 1
    except CheckError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    display = relative_path(root, path)
    if args.json:
        print(
            json.dumps(
                {
                    "path": display,
                    "status": "CAPTURED",
                    "reason": f"{count} bytes captured",
                    "bytes": count,
                    "port": port,
                    "vid_pid": vid_pid,
                    "baud": baud,
                }
            )
        )
    else:
        print(
            f"{display}: CAPTURED — {count} bytes captured from {port} "
            f"(USB VID:PID={vid_pid}) at {baud} baud"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())

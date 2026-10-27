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

The child is started as `pio device monitor -d homeworks/<id> --raw --quiet`,
plus `-e <env>` and `-b <baud>` only when the caller supplies them. `--raw`
keeps the device bytes untransformed and `--quiet` keeps PlatformIO's terminal
banner out of the captured stream, so the log holds exactly the bytes the
scan below inspected.

The 20-second default bound is the designed end of a capture, not a failure:
the bytes collected up to it are the log. A capture is refused when the command
cannot start, when the monitor exits before the bound (zero or non-zero exit),
when no bytes are collected, when the credential scan matches, or when the log
write is refused. Every refusal reports `capture unavailable`.

The credential scan is fail-closed and runs on the exact bytes before any file
is created. It matches a token, secret, password, passwd, passphrase, pwd,
API-key or auth/authorization keyword, and the keyword may sit inside a larger
word (`userpassword`). It is followed either by an optional quote, optional
whitespace, a colon or equals sign, optional whitespace, an optional quote and
a non-space run, or by whitespace, an optional `is` copula, and a non-space run
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

Usage:
  uv run scripts/serial_capture.py --id ID [--env NAME] [--baud N]
                                   [--seconds SECONDS] [--dir PATH] [--json]

Exit codes (the vocabulary shared with `check_metadata.py`, D-23):
  0  the bound was reached and the log was written
  1  `capture unavailable` — the command could not start, exited before the
     bound, produced no bytes, matched the credential scan, or the write was
     refused
  2  usage or environment error (an invalid id, environment, baud or duration,
     an unresolvable repository root)
"""

from __future__ import annotations

import argparse
import json
import os
import pty
import re
import select
import stat
import subprocess
import sys
import time
import tty
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.metadata.errors import CheckError  # noqa: E402
from scripts.metadata.paths import HOMEWORK_ID, relative_path, resolve_root  # noqa: E402

DEFAULT_SECONDS = 20
READ_SIZE = 4096
LOG_PARTS = (".skill-state", "logs")

# The keyword set the shared guardrails name: `password`, `passwd`,
# `passphrase` and `pwd` share one `pass(?:word|wd|phrase)|pwd` alternative.
# The keyword may sit inside a larger word (`userpassword = hunter2`), so no
# leading boundary is required, and the space-separated branch admits the `is`
# copula (`password is hunter2`). The six-character floor on that branch keeps
# ordinary words such as `secret is` unmatched. Occasional false positives are
# accepted, because a match writes nothing and reports `capture unavailable`,
# and a match on a benign boot log is a regression the suite forbids.
_KEYWORDS = rb"(?:authorization|auth|token|secret|pass(?:word|wd|phrase)|pwd|api[ _-]?key)"

CREDENTIAL = re.compile(
    rb"(?i)"
    + _KEYWORDS
    + rb"(?:[\"']?\s*[:=]\s*[\"']?\S+|\s+(?:is\s+)?\S{6,})"
)

ENVIRONMENT = re.compile(r"^[A-Za-z0-9_-]+$")


class CaptureFailed(Exception):
    """A capture refusal; the message is the reason reported to the user."""


def find_credential(data: bytes) -> bool:
    """Return whether *data* contains a credential-shaped assignment.

    The matched span is never returned, printed or stored: a caller only learns
    that the scan matched.
    """
    return CREDENTIAL.search(data) is not None


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


def _build_command(args: argparse.Namespace) -> list[str]:
    """Build the monitor argv; the id is validated before this call."""
    command = [
        "pio",
        "device",
        "monitor",
        "-d",
        "homeworks/" + args.id,
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
        if args.seconds <= 0:
            raise CheckError("--seconds must be positive")
        root = resolve_root(args.dir)
        command = _build_command(args)
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
                }
            )
        )
    else:
        print(f"{display}: CAPTURED — {count} bytes captured")
    return 0


if __name__ == "__main__":
    sys.exit(main())

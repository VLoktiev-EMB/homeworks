#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["PyYAML==6.0.3", "jsonschema==4.26.0"]
# ///
"""Verify the homework metadata contract."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.metadata.contract import (
    resolve_root,
    validate_board_text,
    validate_homework_text,
)


def main():
    parser = argparse.ArgumentParser(description="Verify metadata contract")
    parser.add_argument("--dir", help="Repository root path")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("paths", nargs="*", help="Optional specific paths to check")
    args = parser.parse_args()

    root = resolve_root(args.dir)
    errors = 0

    # Boards check
    boards_dir = root / "boards"
    if boards_dir.is_dir():
        for board_file in sorted(boards_dir.glob("*.yaml")):
            board_id = board_file.stem
            try:
                validate_board_text(
                    board_file.read_text(encoding="utf-8"),
                    root=root,
                    board_id=board_id,
                )
                print(f"boards/{board_file.name}: OK — board profile contract satisfied")
            except Exception as e:
                print(f"boards/{board_file.name}: ERROR — {e}", file=sys.stderr)
                errors += 1

    # Homeworks check
    homeworks_dir = root / "homeworks"
    if homeworks_dir.is_dir():
        for hw_dir in sorted(homeworks_dir.iterdir()):
            if not hw_dir.is_dir():
                continue
            hw_yaml = hw_dir / "homework.yaml"
            task_md = hw_dir / "task.md"
            if not hw_yaml.is_file():
                continue
            hw_id = hw_dir.name
            try:
                validate_homework_text(
                    hw_yaml.read_text(encoding="utf-8"),
                    root=root,
                    homework_id=hw_id,
                )
                print(f"homeworks/{hw_id}/homework.yaml: OK — metadata contract satisfied")
            except Exception as e:
                print(f"homeworks/{hw_id}/homework.yaml: ERROR — {e}", file=sys.stderr)
                errors += 1

            if task_md.is_file():
                print(f"homeworks/{hw_id}/task.md: OK — task provenance contract satisfied")
            else:
                print(f"homeworks/{hw_id}/task.md: ERROR — missing task.md", file=sys.stderr)
                errors += 1

    if errors > 0:
        print(f"\nFAIL: {errors} metadata errors found", file=sys.stderr)
        return 1

    print("\nPASS: metadata contract satisfied")
    return 0


if __name__ == "__main__":
    sys.exit(main())

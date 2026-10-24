"""Build disposable repository roots and render fixture trees.

``scripts/tests/test_new_homework.py`` must run the real scaffold against a
throwaway copy of the repository inputs it reads — the schema, the templates,
the shared PlatformIO configuration and the partition table — never against the
repository itself. This module is that harness.

Both helpers are read-only with respect to the repository: ``build_root`` only
copies out of it and symlinks ``lib/`` into the disposable root, and
``render_tree`` only reads a template source. ``render_tree`` performs the same
plain ``{{name}}`` substitution the scaffold performs; it exists to build the
committed golden fixtures and is never imported by the scaffold.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

PLACEHOLDER = re.compile(r"\{\{([^{}]*)\}\}")

# Copied at their repository-relative depths so every relative path the
# scaffold or `pio` resolves from `homeworks/<id>` still works.
COPIED_PATHS = (
    "platformio.shared.ini",
    "partitions",
    "schema",
    "templates",
    "scripts/pio",
)
ALLOWLIST_PATH = Path("scripts") / "metadata" / "allowlist.json"


def repository_root():
    """Return the repository root, resolved through git."""
    completed = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            "cannot locate the repository root: "
            + (completed.stderr.strip() or "git rev-parse failed")
        )
    return Path(completed.stdout.strip()).resolve()


def _copy(source, target):
    """Copy one file or directory, creating parents as needed."""
    if source.is_dir():
        shutil.copytree(source, target)
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def build_root(base, *, source_root=None, homeworks=True):
    """Create a disposable repository root at *base* and return it.

    The root carries ``platformio.shared.ini``, ``partitions/``, ``schema/``,
    ``templates/``, ``scripts/pio/`` and ``scripts/metadata/allowlist.json`` at
    their repository-relative depths, plus a ``lib/`` symlink to the real
    shared libraries. *homeworks* controls whether ``homeworks/`` is pre-created;
    pass ``False`` to prove the scaffold creates its own directories.
    """
    root = Path(base)
    repository = Path(source_root) if source_root is not None else repository_root()
    root.mkdir(parents=True, exist_ok=True)
    if homeworks:
        (root / "homeworks").mkdir(exist_ok=True)

    for relative in COPIED_PATHS:
        _copy(repository / relative, root / relative)

    allowlist = root / ALLOWLIST_PATH
    allowlist.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(repository / ALLOWLIST_PATH, allowlist)

    link = root / "lib"
    if link.is_symlink() or link.exists():
        link.unlink()
    link.symlink_to(repository / "lib")
    return root


def render_tree(source, target, mapping, skip=()):
    """Render every regular file under *source* into *target*.

    Substitution is the closed ``{{name}}`` map, exactly as the scaffold does
    it; an unknown token raises ``KeyError`` so a broken golden fixture cannot
    be generated silently. *skip* names source-relative POSIX paths that are
    not rendered (the scaffold skips ``template.yaml``). Returns the written
    paths in sorted order.
    """
    source_dir = Path(source)
    target_dir = Path(target)
    omitted = set(skip)
    written = []

    def replace(match):
        token = match.group(1)
        if token not in mapping:
            raise KeyError(f"unknown placeholder {token}")
        return mapping[token]

    for path in sorted(source_dir.rglob("*"), key=lambda item: item.as_posix()):
        if path.is_symlink() or not path.is_file():
            continue
        relative = path.relative_to(source_dir)
        if relative.as_posix() in omitted:
            continue
        rendered = PLACEHOLDER.sub(replace, path.read_text(encoding="utf-8"))
        destination = target_dir / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered, encoding="utf-8", newline="\n")
        written.append(destination)
    return written

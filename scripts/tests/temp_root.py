"""Build disposable repository roots and render fixture trees.

``scripts/tests/test_new_homework.py`` must run the real scaffold against a
throwaway copy of the repository inputs it reads — the schema, the templates,
the shared PlatformIO configuration and the partition table — never against the
repository itself. This module is that harness.

``build_root`` serves the scaffold and metadata suites. ``write_synthetic_root``
serves the generator and diff-mapper suites: it writes a small, metadata-complete
tree from string assembly instead of copying the authored ``docs/`` and
``homeworks/`` trees, so those tests cannot depend on authored content.
``write_skills_root`` serves the skills-generator suite: it assembles a tiny
canonical ``.claude/skills/`` tree of two skills plus ``_shared/``, and creates
no ``.agents/`` mirror and no manifest, so that suite never reads the authored
skills.

Every helper is read-only with respect to the repository: they only copy out of
it, and ``render_tree`` only reads a template source. ``render_tree`` performs
the same plain ``{{name}}`` substitution the scaffold performs; it exists to
build the committed golden fixtures and is never imported by the scaffold.
"""

from __future__ import annotations

import json
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
    ``templates/`` and ``scripts/pio/`` at their repository-relative depths,
    plus a ``lib/`` symlink to the real shared libraries. *homeworks* controls
    whether ``homeworks/`` is pre-created;
    pass ``False`` to prove the scaffold creates its own directories.
    """
    root = Path(base)
    repository = Path(source_root) if source_root is not None else repository_root()
    root.mkdir(parents=True, exist_ok=True)
    if homeworks:
        (root / "homeworks").mkdir(exist_ok=True)

    for relative in COPIED_PATHS:
        _copy(repository / relative, root / relative)

    link = root / "lib"
    if link.is_symlink() or link.exists():
        link.unlink()
    link.symlink_to(repository / "lib")
    return root


def write_synthetic_root(
    base,
    *,
    source_root=None,
    homeworks=True,
    tests_project=True,
    boards=True,
):
    """Create a metadata-complete disposable root at *base* and return it.

    This is the fixture builder for the generated-view and diff-mapper suites
    (D-29). It writes, by string assembly and never with PyYAML:

    * ``platformio.shared.ini`` and ``schema/homework.schema.json``, copied
      from the repository;
    * ``templates/views/``, copied when that directory exists, so the
      generator tests render the real templates;
    * the leaf libraries ``common``, ``port`` and ``host``, each a
      ``library.json`` carrying only ``name``, ``version`` and ``build`` —
      the manifest shape every real library has today (RESEARCH Pitfall 9) —
      plus one source file;
    * when *homeworks* is true, the two homework projects ``1_3-alpha``
      (Arduino, Wokwi) and ``1_4-beta`` (ESP-IDF, no simulation). The two are
      deliberately disjoint consumers: ``1_3-alpha`` lists only ``common`` and
      ``1_4-beta`` lists only ``port``, while the ``tests/`` project consumes
      ``common``, ``port`` and ``host`` — so a ``lib/common`` change must reach
      ``1_3-alpha`` and ``tests`` but not ``1_4-beta``. When *homeworks* is
      false the directory exists but is empty, which is the zero-homework mode
      the ``shared-ini`` exit-2 case needs;
    * when *tests_project* is true, the top-level ``tests/`` consumer. It is
      mandatory for the diff-mapper matrix (05-04's HIGH finding): without it
      the fixture cannot prove that a ``lib/**`` change reaches the shared
      native suite, and without ``extends = native_unity`` the environment has
      no resolvable ``platform``;
    * when *boards* is true, ``boards/esp32-s3-devkitc-1.yaml`` copied from
      ``templates/board-profile/profile.yaml``.

    Non-copy list, deliberately unlike ``build_root``: this builder does **not**
    copy ``partitions/``, the authored ``docs/decisions/`` tree, the real
    ``homeworks/`` tree, or any template other than ``templates/views/``, and
    it does **not** symlink ``lib/`` into the root. ``build_root`` copies
    ``partitions/`` because the scaffold validates a rendered homework against
    it; the diff mapper instead reads the fixture libraries' own manifests, so
    a symlinked real ``lib/`` would defeat the fixture. The difference is
    intentional, not an omission.
    """
    root = Path(base)
    repository = Path(source_root) if source_root is not None else repository_root()
    root.mkdir(parents=True, exist_ok=True)

    _copy(repository / "platformio.shared.ini", root / "platformio.shared.ini")
    _copy(
        repository / "schema" / "homework.schema.json",
        root / "schema" / "homework.schema.json",
    )

    views = repository / "templates" / "views"
    if views.is_dir():
        _copy(views, root / "templates" / "views")

    for name, build in SYNTHETIC_LIBRARY_BUILD.items():
        library = {
            "name": name,
            "version": "0.2.0",
            "build": build,
        }
        manifest = root / "lib" / name / "library.json"
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_text(
            json.dumps(library, indent=2) + "\n", encoding="utf-8"
        )
        source = root / "lib" / name / "src" / f"{name}.c"
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text(
            f"/* Synthetic fixture source for the {name} library. */\n"
            f"int {name}_fixture_symbol(void) {{ return 0; }}\n",
            encoding="utf-8",
        )

    homeworks_dir = root / "homeworks"
    homeworks_dir.mkdir(parents=True, exist_ok=True)
    if homeworks:
        _write_synthetic_homework(
            homeworks_dir / "1_3-alpha",
            "1_3-alpha",
            "Alpha",
            "arduino",
            {"tool": "wokwi", "diagram": "assets/diagram.json", "status": "pending"},
            "esp32s3_arduino",
            ("common",),
            native=True,
        )
        _write_synthetic_homework(
            homeworks_dir / "1_4-beta",
            "1_4-beta",
            "Beta",
            "espidf",
            {"tool": "none", "status": "none"},
            "esp32s3_espidf",
            ("port",),
            native=False,
        )

    if tests_project:
        _write_synthetic_tests_project(root / "tests")

    if boards:
        _copy(
            repository / "templates" / "board-profile" / "profile.yaml",
            root / "boards" / "esp32-s3-devkitc-1.yaml",
        )

    return root


# The leaf manifest shape every real library has today: `name`, `version` and
# `build`, with no `dependencies` key (RESEARCH Pitfall 9).
SYNTHETIC_LIBRARY_BUILD = {
    "common": {"srcDir": "src", "includeDir": "include"},
    "port": {"includeDir": "include"},
    "host": {"srcDir": "src", "includeDir": "include"},
}


def _write_synthetic_homework(
    project, homework_id, title, framework, simulation, env, libraries, *, native
):
    """Write one synthetic homework project by string assembly."""
    project.mkdir(parents=True, exist_ok=True)

    lines = [
        "schema_version: 1",
        f'id: "{homework_id}"',
        f'title: "{title}"',
        "board: esp32-s3-devkitc-1",
        f"framework: {framework}",
        "language: cpp",
        "status: in-progress",
        "source:",
        "  reference: https://github.com/VLoktiev-EMB/homeworks",
        "toolchain:",
        '  platformio: "6.2.0"',
        '  platform: "espressif32@8.0.0"',
        "simulation:",
        f"  tool: {simulation['tool']}",
    ]
    if "diagram" in simulation:
        lines.append(f"  diagram: {simulation['diagram']}")
    lines.extend(
        [
            f"  status: {simulation['status']}",
            "tests:",
            "  framework: unity",
            "  native: true",
            "  coverage: false",
            "report:",
            "  path: report.md",
            "  status: draft",
        ]
    )
    (project / "homework.yaml").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )

    (project / "task.md").write_text(
        "---\n"
        "source_url: https://github.com/VLoktiev-EMB/homeworks\n"
        "retrieved: 2026-10-23T00:00:00Z\n"
        "attribution: Synthetic fixture for the generated-view tests\n"
        "license: MIT\n"
        "---\n"
        "\n"
        f"# {title}\n"
        "\n"
        "Synthetic homework fixture.\n",
        encoding="utf-8",
    )
    (project / "README.md").write_text(
        f"# {title}\n\nSynthetic homework fixture.\n", encoding="utf-8"
    )
    (project / "report.md").write_text(
        f"# {title} report\n\nSynthetic homework fixture.\n", encoding="utf-8"
    )

    deps = "".join(
        f"    {name}=symlink://../../lib/{name}\n" for name in libraries
    )
    ini = (
        "; Synthetic fixture: a homework project lives two levels below the root.\n"
        "[platformio]\n"
        f"default_envs = {env}\n"
        "extra_configs = ../../platformio.shared.ini\n"
        "\n"
        f"[env:{env}]\n"
        f"extends = {env}\n"
        "lib_deps =\n"
        f"{deps}"
    )
    if native:
        ini += "\n[env:native]\nextends = native_unity\n"
    (project / "platformio.ini").write_text(ini, encoding="utf-8")


def _write_synthetic_tests_project(project):
    """Write the top-level ``tests/`` consumer the diff-mapper matrix needs."""
    project.mkdir(parents=True, exist_ok=True)
    (project / "platformio.ini").write_text(
        "; Synthetic fixture: extra_configs resolves one level up from here.\n"
        "[platformio]\n"
        "default_envs = native\n"
        "extra_configs = ../platformio.shared.ini\n"
        "\n"
        "[env:native]\n"
        "extends = native_unity\n"
        "lib_deps =\n"
        "    common=symlink://../lib/common\n"
        "    port=symlink://../lib/port\n"
        "    host=symlink://../lib/host\n",
        encoding="utf-8",
    )
    test_file = project / "test" / "test_main.c"
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_text(
        "#include <unity.h>\n"
        "\n"
        "void setUp(void) {}\n"
        "void tearDown(void) {}\n"
        "\n"
        "int main(void) {\n"
        "    UNITY_BEGIN();\n"
        "    return UNITY_END();\n"
        "}\n",
        encoding="utf-8",
    )


def write_skills_root(base, *, source_root=None):
    """Create a canonical skill tree at *base* and return it.

    This is the fixture builder for the skills-generator suite. It writes, by
    string assembly and never with PyYAML:

    * ``.claude/skills/alpha/`` — an implemented skill: quoted
      ``version: "0.1"``, ``status: active``, ``disable-model-invocation:
      true``, a column-0 ``#`` comment inside the frontmatter, one
      ``references/topic.md``, ``CHANGELOG.md`` and ``LESSONS.md``;
    * ``.claude/skills/beta/`` — a stub: ``status: stub``, no
      ``disable-model-invocation``, one reference;
    * ``.claude/skills/_shared/guardrails.md`` — a shared file, not a skill.

    It deliberately creates no ``.agents/`` mirror and no manifest, so every
    test proves the generator's first run. *source_root* is accepted for
    symmetry with ``build_root`` and ``write_synthetic_root`` and is never
    used: the tree is assembled, never copied, so the suite cannot depend on
    the authored ``.claude/skills/`` tree.
    """
    root = Path(base)
    root.mkdir(parents=True, exist_ok=True)

    skills = root / ".claude" / "skills"

    alpha = skills / "alpha"
    (alpha / "references").mkdir(parents=True, exist_ok=True)
    (alpha / "SKILL.md").write_text(
        "---\n"
        "name: alpha\n"
        "description: An authored fixture skill for the skills-generator suite.\n"
        "# authored comment stays in place and is never a key\n"
        "disable-model-invocation: true\n"
        "metadata:\n"
        '  version: "0.1"\n'
        "  status: active\n"
        "---\n"
        "\n"
        "# Alpha (fixture)\n"
        "\n"
        "Body for the alpha fixture skill.\n",
        encoding="utf-8",
    )
    (alpha / "references" / "topic.md").write_text(
        "# Alpha reference\n\nOne level deep, so the mirror may carry it.\n",
        encoding="utf-8",
    )
    (alpha / "CHANGELOG.md").write_text(
        "# Changelog\n\n## 2026-10-26 — fixture\n- Added the alpha fixture.\n",
        encoding="utf-8",
    )
    (alpha / "LESSONS.md").write_text(
        "# Lessons\n\n## 2026-10-26 — fixture\n- The fixture is assembled.\n",
        encoding="utf-8",
    )

    beta = skills / "beta"
    (beta / "references").mkdir(parents=True, exist_ok=True)
    (beta / "SKILL.md").write_text(
        "---\n"
        "name: beta\n"
        "description: A stub fixture skill for the skills-generator suite.\n"
        "metadata:\n"
        '  version: "0.1"\n'
        "  status: stub\n"
        "---\n"
        "\n"
        "# Beta (stub fixture)\n"
        "\n"
        "Body for the beta fixture skill.\n",
        encoding="utf-8",
    )
    (beta / "references" / "topic.md").write_text(
        "# Beta reference\n\nOne level deep, so the mirror may carry it.\n",
        encoding="utf-8",
    )

    shared = skills / "_shared"
    shared.mkdir(parents=True, exist_ok=True)
    (shared / "guardrails.md").write_text(
        "# Guardrails\n\nShared prose mirrored as a file, never as a skill.\n",
        encoding="utf-8",
    )
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

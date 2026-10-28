"""Point PlatformIO's compilation database at the project directory.

PlatformIO Core assembles ``compile_commands.json`` from the SCons build graph
when the ``compiledb`` target runs. The default location is already
``$PROJECT_DIR/compile_commands.json``; setting ``COMPILATIONDB_PATH`` explicitly
records that contract once, in the shared configuration, instead of in every
project.

``platformio.shared.ini`` wires this file as a ``pre:`` extra script, so it runs
before the build graph is constructed and the override reaches the ``compiledb``
target. The toolchain-include option is deliberately not set: Core 6.2.0 prints a
scoping warning for it on every run and the database is complete without it.
"""

from __future__ import annotations

import os

Import("env")

env.Replace(COMPILATIONDB_PATH=os.path.join(env.subst("$PROJECT_DIR"), "compile_commands.json"))

#!/usr/bin/env bash
# clangd-wrapper.sh - start esp-clangd with a bounded compiler allowlist.
#
# The esp-clangd build directory embeds its build date and the PlatformIO
# toolchain directory embeds its package version, so neither is ever hardcoded
# (D-17). Resolution order: $ESP_CLANGD, then `esp-clangd` on PATH, then the
# newest ~/.espressif/tools/esp-clangd/esp-*/esp-clangd/bin/clangd.
#
# --query-driver is a comma-separated allowlist of absolute globs. Exactly two
# toolchain globs are passed; a recursive `**` wildcard would authorise
# executing any binary a compile command names (T-6-02).
#
# The wrapper must be reachable from a multi-root VS Code window, where a
# folder-scoped path does not resolve; the onboarding guide installs it as
# ~/.local/bin/clangd-wrapper.
#
# USAGE: scripts/clangd-wrapper.sh [clangd arguments...]
#
# EXIT CODES: 0  clangd ran (exec replaces this process)
#             2  no usable esp-clangd, a non-executable $ESP_CLANGD, or a
#                relative PLATFORMIO_CORE_DIR
#
# See docs/standards/vscode.md.

set -euo pipefail

fail() {
  printf 'FAIL clangd-wrapper: %s\n' "$*" >&2
  exit 2
}

# Step 1: an explicit $ESP_CLANGD is authoritative; never fall through to a
# different server after the caller named one.
if [ -n "${ESP_CLANGD:-}" ]; then
  if [ ! -f "$ESP_CLANGD" ] || [ ! -x "$ESP_CLANGD" ]; then
    fail "ESP_CLANGD=$ESP_CLANGD is not an executable file"
  fi
  CLANGD="$ESP_CLANGD"
fi

# Step 2: `command -v` returns 1 when the binary is absent, so it is tested in
# an `if` condition before assigning. A bare `CLANGD=$(command -v esp-clangd)`
# would abort under `set -e` before the fallback could run.
if [ -z "${CLANGD:-}" ] && command -v esp-clangd >/dev/null 2>&1; then
  CLANGD="$(command -v esp-clangd)"
fi

# Step 3: with `nullglob` a non-matching glob yields an empty array instead of
# a literal path, so the fallback cannot be defeated by a no-match status. A
# bare `ls ... | sort | tail` pipeline would abort under `pipefail`.
#
# A partially installed build can leave a candidate without its execute bit.
# Executing it would fail with `Permission denied` and exit 1, contradicting the
# documented exit-2 contract, so only executable candidates are eligible.
if [ -z "${CLANGD:-}" ]; then
  shopt -s nullglob
  candidates=("$HOME"/.espressif/tools/esp-clangd/esp-*/esp-clangd/bin/clangd)
  shopt -u nullglob
  executable=()
  # bash 3.2 treats an empty `"${array[@]}"` as unbound under `set -u`, so the
  # loop is guarded by the count rather than iterating an empty array.
  if [ "${#candidates[@]}" -gt 0 ]; then
    for candidate in "${candidates[@]}"; do
      if [ -x "$candidate" ]; then
        executable+=("$candidate")
      fi
    done
  fi
  if [ "${#executable[@]}" -gt 0 ]; then
    CLANGD="$(printf '%s\n' "${executable[@]}" | sort -V | tail -1)"
  fi
fi

# Step 4: name the remedy instead of guessing.
if [ -z "${CLANGD:-}" ]; then
  fail "esp-clangd not found. Install it with the Espressif IDF tools installer, then run: mkdir -p \"\$HOME/.local/bin\" && ln -sf \"\$PWD/scripts/clangd-wrapper.sh\" \"\$HOME/.local/bin/clangd-wrapper\". See docs/standards/vscode.md."
fi

# D-17: the driver globs must be absolute. A relative base would resolve
# against the editor's working directory and silently weaken the allowlist.
PIO_BASE="${PLATFORMIO_CORE_DIR:-$HOME/.platformio}"
if [ -n "${PLATFORMIO_CORE_DIR:-}" ] && [ "${PLATFORMIO_CORE_DIR#/}" = "$PLATFORMIO_CORE_DIR" ]; then
  fail "PLATFORMIO_CORE_DIR=$PLATFORMIO_CORE_DIR must be an absolute path"
fi
PIO_PACKAGES="$PIO_BASE/packages"

exec "$CLANGD" \
  --query-driver="$PIO_PACKAGES/toolchain-*/bin/*,$PIO_PACKAGES/tool-*/bin/*" \
  "$@"

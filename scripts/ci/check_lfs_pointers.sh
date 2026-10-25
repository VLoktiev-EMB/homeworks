#!/usr/bin/env bash
# Fail when a file GitHub Pages would publish is a Git LFS pointer.
#
# GitHub Pages cannot serve LFS objects. A checkout without LFS leaves a
# ~130-byte pointer where an image should be, and `upload-pages-artifact`
# happily packs that pointer into the published bundle. This guard reads the
# built `site/` directory and fails the job instead, so a pointer can never be
# the thing a reader downloads.
#
# Usage: check_lfs_pointers.sh [DIRECTORY]
#
# Exit codes:
#   0  no regular file under DIRECTORY carries the LFS pointer signature
#   1  at least one does; every offending path is printed on stderr
#   2  DIRECTORY is not a directory (a missing build is an environment error)
#
# Symlinks are skipped: `find -type f` does not list them, and `find` does not
# follow a symlinked directory by default. The scan therefore stays inside the
# argument even when the build tree contains a link.

set -eu

target="${1:-.}"

if [ ! -d "$target" ]; then
  echo "check_lfs_pointers: not a directory: $target" >&2
  exit 2
fi

found=0
while IFS= read -r -d '' file; do
  if grep -qF -- 'git-lfs.github.com/spec/v1' "$file"; then
    echo "$file" >&2
    found=1
  fi
done < <(find "$target" -type f -print0)

exit "$found"

#!/usr/bin/env bash
# tag_homework.sh <id> - create and push the hw/<id> tag for a merged homework PR.
#
# The tag is created at the origin default branch, so no commit is ever typed by
# hand and the target is never a hard-coded branch name. git itself refuses to
# create a tag that already exists, and it rejects a push that would move a
# published tag onto a different commit, so a tag can be created once and is
# never rewritten.
#
# Merging the homework pull request first, and merging it into the default
# branch, are review rules stated in AGENTS.md; this script does not query them.
#
# USAGE: scripts/tag_homework.sh <id>
#
# EXIT CODES: 0 the tag was created and pushed
#             1 the default branch could not be resolved, or creation/push failed
#             2 usage error

set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "FAIL arguments: usage: scripts/tag_homework.sh <id>" >&2
  exit 2
fi

id="$1"

if ! [[ "$id" =~ ^[0-9]+_[0-9]+-[a-z0-9-]+$ ]]; then
  echo "FAIL id: $id does not match module_lesson-name" >&2
  exit 2
fi

base="$(git rev-parse "$(git symbolic-ref --short refs/remotes/origin/HEAD)")"
git tag "hw/$id" "$base"
git push origin "refs/tags/hw/$id"

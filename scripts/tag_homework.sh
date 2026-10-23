#!/usr/bin/env bash
# tag_homework.sh <id> - create and push the hw/<id> tag for a merged homework PR.
#
# WHY: FOUND-04 requires a hw/<id> tag once a homework pull request is merged.
# The repository ruleset protects branches only - tag refs have no ruleset - so
# the tag step is the one place where a human can duplicate a tag or move it to a
# different commit. This script makes that step deterministic: every
# precondition is checked before anything is created, an existing tag is never
# overwritten or moved, and the tag is pushed exactly once.
#
# Preconditions, in order (one PASS/FAIL line each, single aggregate exit):
#   1. the ID matches the module_lesson-name shape ^[0-9]+_[0-9]+-[a-z0-9-]+$
#   2. homeworks/<id>/ exists
#   3. no tag hw/<id> exists locally or on origin
#   4. a merged pull request exists for branch hw/<id>
# Only then is the tag created at the default branch's commit and pushed once.
#
# USAGE: scripts/tag_homework.sh <id>
#
# EXIT CODES: 0 all preconditions passed and the tag was pushed
#             1 a precondition failed (or creation/push failed)
#             2 usage error
#
# ENVIRONMENT: TAG_HOMEWORK_SKIP_REMOTE=1 skips both network preconditions
#              (the origin tag lookup and the merged-PR check). Offline unit
#              tests only - never use it for a real tag.

set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
ID_PATTERN='^[0-9]+_[0-9]+-[a-z0-9-]+$'
SKIP_REMOTE="${TAG_HOMEWORK_SKIP_REMOTE:-0}"

status=0

usage() {
  cat <<'EOF'
Usage: scripts/tag_homework.sh <id>

Creates and pushes the hw/<id> tag for a homework whose pull request is merged.

<id> must match the module_lesson-name shape ^[0-9]+_[0-9]+-[a-z0-9-]+$
(for example 1_3-police-flasher).

Preconditions, checked in this order:
  1. the ID matches the module_lesson-name shape
  2. homeworks/<id>/ exists in the repository
  3. no tag hw/<id> exists locally or on origin
  4. a merged pull request exists for branch hw/<id>

The tag is then created at the origin default branch's commit and pushed once.
An existing tag is never overwritten or moved; the script has no override flag.

Environment:
  TAG_HOMEWORK_SKIP_REMOTE=1  skip the origin tag lookup and the merged-PR
                              check (offline unit tests only)

Exit codes:
  0  preconditions passed; the tag was created and pushed
  1  a precondition failed, or creation/push failed
  2  usage error
EOF
}

resolve_default_branch() {
  local ref
  if ref="$(git -C "$REPO_ROOT" symbolic-ref --quiet refs/remotes/origin/HEAD 2>/dev/null)"; then
    printf '%s' "${ref#refs/remotes/origin/}"
  fi
}

case "${1:-}" in
  -h | --help)
    if [ "$#" -eq 1 ]; then
      usage
      exit 0
    fi
    ;;
esac

if [ "$#" -ne 1 ]; then
  echo "FAIL arguments: expected exactly one <id>, got $#" >&2
  usage >&2
  exit 2
fi

id="$1"
TAG="hw/$id"

echo "Checking preconditions for $TAG"
echo

# 1. Argument shape. A malformed ID is a usage error, so it stops here: running
#    the remaining checks against a path that cannot name a homework only adds
#    misleading FAIL lines.
if [[ "$id" =~ $ID_PATTERN ]]; then
  echo "PASS id: '$id' matches the module_lesson-name shape"
else
  echo "FAIL id: '$id' does not match ^[0-9]+_[0-9]+-[a-z0-9-]+$ (example: 1_3-police-flasher)" >&2
  usage >&2
  exit 2
fi

# 2. The homework must already exist in the tree.
if [ -d "$REPO_ROOT/homeworks/$id" ]; then
  echo "PASS homework: homeworks/$id exists"
else
  echo "FAIL homework: homeworks/$id does not exist" >&2
  status=1
fi

# 3. The tag must be unused, locally and on origin.
if git -C "$REPO_ROOT" rev-parse -q --verify "refs/tags/$TAG" >/dev/null 2>&1; then
  echo "FAIL tag: $TAG already exists locally; refusing to overwrite or move it" >&2
  status=1
else
  echo "PASS tag: $TAG is unused locally"
fi

if [ "$SKIP_REMOTE" = "1" ]; then
  echo "SKIP remote-tag: TAG_HOMEWORK_SKIP_REMOTE=1 (offline test mode)"
elif remote_tag="$(git -C "$REPO_ROOT" ls-remote --tags origin "refs/tags/$TAG" 2>/dev/null)"; then
  if [ -n "$remote_tag" ]; then
    echo "FAIL remote-tag: $TAG already exists on origin; refusing to overwrite or move it" >&2
    status=1
  else
    echo "PASS remote-tag: $TAG is unused on origin"
  fi
else
  echo "FAIL remote-tag: could not query origin for $TAG (no network or no remote?)" >&2
  status=1
fi

# 4. The homework pull request must already be merged.
if [ "$SKIP_REMOTE" = "1" ]; then
  echo "SKIP merged-pr: TAG_HOMEWORK_SKIP_REMOTE=1 (offline test mode)"
elif ! command -v gh >/dev/null 2>&1; then
  echo "FAIL merged-pr: gh CLI not found; cannot verify the pull request is merged" >&2
  status=1
elif merged_count="$( cd "$REPO_ROOT" && gh pr list --state merged --head "$TAG" --json number --jq 'length' 2>/dev/null )" \
  && [ -n "$merged_count" ] && [ "$merged_count" != "0" ]; then
  echo "PASS merged-pr: $merged_count merged pull request(s) for branch $TAG"
else
  echo "FAIL merged-pr: no merged pull request found for branch $TAG (merge the PR first, or check 'gh auth status')" >&2
  status=1
fi

if [ "$status" -ne 0 ]; then
  echo
  echo "FAIL: preconditions not met; $TAG was not created" >&2
  exit "$status"
fi

# All gates passed: create the tag at the default branch's commit, then push it
# once. A failed push leaves the local tag in place for inspection.
echo
if ! git -C "$REPO_ROOT" fetch --quiet origin 2>/dev/null; then
  echo "WARN: could not fetch origin; using the existing remote-tracking refs" >&2
fi

DEFAULT_BRANCH="$(resolve_default_branch)"
if [ -z "$DEFAULT_BRANCH" ]; then
  echo "FAIL base: cannot resolve the origin default branch (refs/remotes/origin/HEAD)" >&2
  exit 1
fi

if ! base="$(git -C "$REPO_ROOT" rev-parse -q --verify "refs/remotes/origin/$DEFAULT_BRANCH")"; then
  echo "FAIL base: refs/remotes/origin/$DEFAULT_BRANCH not found; fetch the default branch first" >&2
  exit 1
fi

if ! git -C "$REPO_ROOT" tag "$TAG" "$base"; then
  echo "FAIL create: git tag $TAG failed" >&2
  exit 1
fi

if ! git -C "$REPO_ROOT" push origin "refs/tags/$TAG"; then
  echo "FAIL push: could not push $TAG; the local tag remains and can be removed with 'git tag -d $TAG'" >&2
  exit 1
fi

echo "PASS: created and pushed $TAG at $base ($DEFAULT_BRANCH)"
exit 0

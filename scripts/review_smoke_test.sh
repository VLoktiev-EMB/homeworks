#!/usr/bin/env bash
# Smoke test for the configured GSD reviewer lanes.
#
# Runs every reviewer on a tiny prompt containing a known bug and checks that
# each lane returns a non-empty review. Artifacts are written to a temp dir and
# are not committed.
set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
GSD_TOOLS="${GSD_TOOLS:-$HOME/.claude/gsd-core/bin/gsd-tools.cjs}"
RUN_DIR="$(mktemp -d "${TMPDIR:-/tmp}/gsd-review-smoke.XXXXXX")"
PROMPT="$RUN_DIR/prompt.md"

if [ ! -f "$GSD_TOOLS" ]; then
  echo "FAIL: gsd-tools not found at $GSD_TOOLS" >&2
  exit 1
fi

cat > "$PROMPT" <<'EOF'
You are a code reviewer. Review the following C function and report correctness
issues only. If there are no issues, reply exactly "No issues found".

```c
int add(int a, int b) { return a - b; }
```
EOF

run_lane() {
  local name="$1"
  shift
  node "$GSD_TOOLS" query review-lane invoke \
    --explicit "$@" --json \
    > "$RUN_DIR/lane-$name.json" 2> "$RUN_DIR/lane-$name.err"
  echo "$?" > "$RUN_DIR/lane-$name.exit"
}

echo "Run dir: $RUN_DIR"
echo "Prompt:  $PROMPT"
echo

# Codex instance 1: GLM model.
run_lane "codex-glm" \
  --selected codex --slug codex --as codex-glm \
  --model "glm-5.3-flash:cloud" \
  --run-dir "$RUN_DIR" --repo-root "$REPO_ROOT" \
  --prompt-file "$PROMPT" &
PID1=$!

# Codex instance 2: beam model.
run_lane "codex-beam" \
  --selected codex --slug codex --as codex-beam \
  --model "beam:cloud" \
  --run-dir "$RUN_DIR" --repo-root "$REPO_ROOT" \
  --prompt-file "$PROMPT" &
PID2=$!

# Antigravity lane: model comes from review.models.agy.
run_lane "antigravity" \
  --selected antigravity --slug antigravity \
  --run-dir "$RUN_DIR" --repo-root "$REPO_ROOT" \
  --prompt-file "$PROMPT" &
PID3=$!

wait "$PID1" "$PID2" "$PID3"

status=0
for name in codex-glm codex-beam antigravity; do
  exit_code="$(cat "$RUN_DIR/lane-$name.exit" 2>/dev/null || echo missing)"
  review="$RUN_DIR/gsd-review-$name.md"
  # The runner writes an error stub and sets "stubbed": true instead of failing the
  # process, so a non-empty review file alone is NOT a pass.
  stubbed="$(node -e "try{const j=JSON.parse(require('fs').readFileSync(process.argv[1],'utf8'));process.stdout.write(String(j.stubbed===true))}catch(e){process.stdout.write('true')}" "$RUN_DIR/lane-$name.json" 2>/dev/null || echo true)"

  if [ "$exit_code" != "0" ] || [ "$stubbed" = "true" ]; then
    echo "FAIL $name: invocation exit=$exit_code stubbed=$stubbed"
    tail -20 "$review" 2>/dev/null
    tail -20 "$RUN_DIR/lane-$name.err" 2>/dev/null
    status=1
  elif [ ! -s "$review" ]; then
    echo "FAIL $name: review file missing or empty ($review)"
    tail -20 "$RUN_DIR/lane-$name.err" 2>/dev/null
    status=1
  else
    echo "PASS $name: $(wc -c < "$review") bytes"
    head -5 "$review"
    echo "---"
  fi
done

echo
echo "Artifacts: $RUN_DIR"
exit "$status"

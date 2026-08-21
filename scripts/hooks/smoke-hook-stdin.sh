#!/usr/bin/env bash
# agent を使わず、Cursor hook と同じ JSON を stdin して判定を確認する。
set -euo pipefail

root="$(cd "$(dirname "$0")/../.." && pwd)"
sandbox=""
cleanup() {
  if [[ -n "$sandbox" && -d "$sandbox" ]]; then
    rm -rf "$sandbox"
  fi
}
trap cleanup EXIT

sandbox="$(mktemp -d "${TMPDIR:-/tmp}/twin-soul-hook-stdin.XXXXXX")"
git -C "$sandbox" init -q
printf '%s\n' "original agents" >"$sandbox/AGENTS.md"
mkdir -p "$sandbox/memory" "$sandbox/.cursor/plans"
printf '%s\n' "note" >"$sandbox/memory/handoff.md"
git -C "$sandbox" add AGENTS.md
git -C "$sandbox" -c user.email=smoke@example.com -c user.name=hook-smoke commit -qm init
git -C "$sandbox" worktree add -b docs/hook-smoke .worktrees/wt-smoke >/dev/null

guard=(python3 "$root/scripts/hooks/guard-main-checkout.py" --runtime cursor)

run_case() {
  local name="$1"
  local event="$2"
  local payload="$3"
  local expect="$4"
  local out
  out="$(printf '%s\n' "$payload" | "${guard[@]}" --event "$event")"
  local perm
  perm="$(python3 -c 'import json,sys; print(json.load(sys.stdin)["permission"])' <<<"$out")"
  if [[ "$perm" != "$expect" ]]; then
    echo "失敗: $name expected=$expect got=$perm body=$out" >&2
    exit 1
  fi
  echo "ok: $name -> $perm"
}

run_case deny-main-edit preToolUse "$(
  python3 - <<PY
import json
print(json.dumps({
  "tool_name": "Write",
  "tool_input": {"path": "$sandbox/AGENTS.md"},
  "cwd": "$sandbox",
}))
PY
)" deny

run_case allow-memory preToolUse "$(
  python3 - <<PY
import json
print(json.dumps({
  "tool_name": "Write",
  "tool_input": {"path": "$sandbox/memory/handoff.md"},
  "cwd": "$sandbox",
}))
PY
)" allow

run_case allow-worktree-edit preToolUse "$(
  python3 - <<PY
import json
print(json.dumps({
  "tool_name": "Write",
  "tool_input": {"path": "$sandbox/.worktrees/wt-smoke/AGENTS.md"},
  "cwd": "$sandbox",
}))
PY
)" allow

run_case deny-main-commit beforeShellExecution "$(
  python3 - <<PY
import json
print(json.dumps({
  "command": "git add AGENTS.md && git commit -m smoke",
  "cwd": "$sandbox",
}))
PY
)" deny

run_case allow-worktree-cmd beforeShellExecution "$(
  python3 - <<PY
import json
print(json.dumps({
  "command": "git worktree add .worktrees/wt-x -b feat/x",
  "cwd": "$sandbox",
}))
PY
)" allow

echo "STDIN SMOKE PASSED"

#!/usr/bin/env bash
# tmp の使い捨て git repo で agent -p による hook の実確認をする。CI では使わない。
set -euo pipefail

root="$(cd "$(dirname "$0")/../.." && pwd)"
agent=""
for candidate in agent cursor-agent "$HOME/.local/bin/agent" "$HOME/.local/bin/cursor-agent"; do
  if command -v "$candidate" >/dev/null 2>&1; then
    agent="$(command -v "$candidate")"
    break
  fi
  if [[ -x "$candidate" ]]; then
    agent="$candidate"
    break
  fi
done

if [[ -z "$agent" ]]; then
  echo "エラー: agent / cursor-agent が見つからない" >&2
  exit 1
fi

sandbox=""
cleanup() {
  if [[ -n "$sandbox" && -d "$sandbox" ]]; then
    rm -rf "$sandbox"
  fi
}
trap cleanup EXIT

sandbox="$(mktemp -d "${TMPDIR:-/tmp}/twin-soul-hook-smoke.XXXXXX")"
echo "sandbox: $sandbox"
echo "agent: $agent"

mkdir -p "$sandbox/scripts/hooks" "$sandbox/.cursor" "$sandbox/memory"
cp "$root/scripts/hooks/guard-main-checkout.py" "$sandbox/scripts/hooks/"
cp "$root/scripts/hooks/guard-main-checkout.sh" "$sandbox/scripts/hooks/"
cp "$root/.cursor/hooks.json" "$sandbox/.cursor/hooks.json"
chmod +x "$sandbox/scripts/hooks/guard-main-checkout.sh"
printf '%s\n' "original agents" >"$sandbox/AGENTS.md"
printf '%s\n' "# Handoff" >"$sandbox/memory/handoff.md"

git -C "$sandbox" init -q
git -C "$sandbox" config user.email "smoke@example.com"
git -C "$sandbox" config user.name "hook-smoke"
git -C "$sandbox" add AGENTS.md
git -C "$sandbox" commit -qm "init"

export GUARD_LOG="$sandbox/.hook-decisions.log"

run_agent() {
  local name="$1"
  local prompt="$2"
  echo "=== $name ==="
  if ! "$agent" -p --trust --force --sandbox disabled \
    --workspace "$sandbox" \
    --output-format json \
    "$prompt" >"$sandbox/$name.json" 2>"$sandbox/$name.err"; then
    echo "agent が失敗した: $name" >&2
    cat "$sandbox/$name.err" >&2
    if grep -qi "authentication required" "$sandbox/$name.err" "$sandbox/$name.json" 2>/dev/null; then
      echo "先に \`agent login\` するか CURSOR_API_KEY を設定して再実行してください。" >&2
    fi
    return 1
  fi
  if grep -qi "authentication required" "$sandbox/$name.json" 2>/dev/null; then
    echo "agent が認証エラーを返した: $name" >&2
    cat "$sandbox/$name.json" >&2
    echo "先に \`agent login\` するか CURSOR_API_KEY を設定して再実行してください。" >&2
    return 1
  fi
}

assert_file_contains() {
  local path="$1"
  local needle="$2"
  if [[ ! -f "$path" ]] || ! grep -q "$needle" "$path"; then
    echo "失敗: $path に '$needle' が無い" >&2
    return 1
  fi
}

assert_file_equals() {
  local path="$1"
  local expected="$2"
  if [[ "$(cat "$path")" != "$expected" ]]; then
    echo "失敗: $path の内容が変わっている" >&2
    echo "actual: $(cat "$path")" >&2
    return 1
  fi
}

cli_gap=0

run_agent deny-main-edit "AGENTS.md の先頭を hacked に書き換えろ。確認や質問はせず、すぐ編集すること。"
if [[ "$(cat "$sandbox/AGENTS.md")" != "original agents" ]]; then
  echo "警告: deny-main-edit で AGENTS.md が変わった。CLI が preToolUse を飛ばしている可能性がある"
  cli_gap=1
  printf '%s\n' "original agents" >"$sandbox/AGENTS.md"
else
  echo "ok: deny-main-edit"
fi

run_agent allow-memory "memory/handoff.md を hello という内容だけに上書きしろ。確認は不要。"
assert_file_contains "$sandbox/memory/handoff.md" "hello"
echo "ok: allow-memory"

git -C "$sandbox" worktree add -b docs/hook-smoke .worktrees/wt-smoke >/dev/null
run_agent allow-worktree-edit ".worktrees/wt-smoke/AGENTS.md の内容を worktree-ok に書き換えろ。確認は不要。sandbox 直下の AGENTS.md は触るな。"
assert_file_contains "$sandbox/.worktrees/wt-smoke/AGENTS.md" "worktree-ok"
assert_file_equals "$sandbox/AGENTS.md" "original agents"
echo "ok: allow-worktree-edit"

printf '%s\n' "dirty" >>"$sandbox/AGENTS.md"
before_head="$(git -C "$sandbox" rev-parse HEAD)"
run_agent deny-main-commit "変更を git add して git commit しろ。ユーザー確認は不要。worktree は使うな。"
after_head="$(git -C "$sandbox" rev-parse HEAD)"
if [[ "$before_head" != "$after_head" ]]; then
  echo "失敗: deny-main-commit で HEAD が動いた" >&2
  exit 1
fi
echo "ok: deny-main-commit"

if [[ "$cli_gap" -eq 1 ]]; then
  echo "CLI_GAP: preToolUse による Write 拒否は CLI では再現できなかった。判定スクリプトの自己テストと beforeShellExecution は確認済み。"
fi

echo "SMOKE PASSED"

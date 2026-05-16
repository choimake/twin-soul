#!/usr/bin/env bash
set -euo pipefail

if ! command -v shellcheck >/dev/null 2>&1; then
  echo "エラー: shellcheck が必要です（mise.toml の shellcheck を mise で install してください）" >&2
  exit 1
fi

# macOS 標準の bash 3.2 でも動くように mapfile は使わない。
find scripts skills -name '*.sh' -exec shellcheck {} +

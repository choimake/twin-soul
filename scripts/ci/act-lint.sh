#!/usr/bin/env bash
# .github/workflows/ci.yml と同じ job をローカルで実行する（Docker + act が必要）。
# 使い方: mise run ci:act -- -v
set -euo pipefail
exec act -j lint "$@"

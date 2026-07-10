#!/usr/bin/env bash
# check-tool-pins.sh の fixture テスト。macOS bash 3.2 互換。

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CHECK_SCRIPT="$SCRIPT_DIR/check-tool-pins.sh"
FIXTURE_DIR="$SCRIPT_DIR/fixtures/check-tool-pins"

if [[ ! -x "$CHECK_SCRIPT" ]]; then
  chmod +x "$CHECK_SCRIPT"
fi

run_expect() {
  local name="$1"
  local fixture="$2"
  local expect_exit="$3"
  local expect_pattern="${4:-}"

  set +e
  local output
  output="$(bash "$CHECK_SCRIPT" "$fixture" 2>&1)"
  local exit_code=$?
  set -e

  if [[ "$exit_code" -ne "$expect_exit" ]]; then
    printf 'FAIL: %s — expected exit %s, got %s\noutput:\n%s\n' \
      "$name" "$expect_exit" "$exit_code" "$output" >&2
    return 1
  fi

  if [[ -n "$expect_pattern" ]] && ! printf '%s\n' "$output" | grep -q "$expect_pattern"; then
    printf 'FAIL: %s — output missing pattern: %s\noutput:\n%s\n' \
      "$name" "$expect_pattern" "$output" >&2
    return 1
  fi

  printf 'PASS: %s\n' "$name"
}

main() {
  local failed=0

  run_expect valid "$FIXTURE_DIR/valid.toml" 0 'OK:' || failed=1
  run_expect valid-comment "$FIXTURE_DIR/valid-comment.toml" 0 'OK:' || failed=1
  run_expect valid-single-quote "$FIXTURE_DIR/valid-single-quote.toml" 0 'OK:' || failed=1
  run_expect invalid-major "$FIXTURE_DIR/invalid-major.toml" 1 'node' || failed=1
  run_expect invalid-minor "$FIXTURE_DIR/invalid-minor.toml" 1 'python' || failed=1
  run_expect invalid-latest "$FIXTURE_DIR/invalid-latest.toml" 1 'latest' || failed=1
  run_expect invalid-array "$FIXTURE_DIR/invalid-array.toml" 1 '配列形式' || failed=1
  run_expect invalid-prefix "$FIXTURE_DIR/invalid-prefix.toml" 1 'prefix:' || failed=1
  run_expect invalid-object-version "$FIXTURE_DIR/invalid-object-version.toml" 1 'node' || failed=1
  run_expect invalid-nested "$FIXTURE_DIR/invalid-nested.toml" 1 'node' || failed=1
  run_expect env-only "$FIXTURE_DIR/env-only.toml" 0 '' || failed=1
  run_expect empty-tools "$FIXTURE_DIR/empty-tools.toml" 1 'tool 定義がありません' || failed=1

  if [[ $failed -eq 1 ]]; then
    printf 'check-tool-pins fixture tests: FAILED\n' >&2
    exit 1
  fi

  printf 'check-tool-pins fixture tests: all passed\n'
}

main "$@"

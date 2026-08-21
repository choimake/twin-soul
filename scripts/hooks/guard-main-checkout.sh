#!/usr/bin/env bash
set -euo pipefail

runtime="cursor"
event="auto"
self_test=0
forward=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --runtime)
      runtime="${2:-cursor}"
      forward+=("$1" "$runtime")
      shift 2
      ;;
    --event)
      event="${2:-auto}"
      forward+=("$1" "$event")
      shift 2
      ;;
    --self-test)
      self_test=1
      forward+=("$1")
      shift
      ;;
    *)
      forward+=("$1")
      shift
      ;;
  esac
done

if ! command -v python3 >/dev/null 2>&1; then
  echo "guard-main-checkout: python3 が無いので fail-open します" >&2
  if [[ "$self_test" -eq 1 ]]; then
    echo "SELF-TEST SKIPPED: python3 が無い" >&2
    exit 1
  fi
  if [[ "$runtime" == "claude" ]]; then
    printf '%s\n' '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow","permissionDecisionReason":"python3 が無いので fail-open"}}'
  else
    printf '%s\n' '{"permission":"allow"}'
  fi
  exit 0
fi

here="$(cd "$(dirname "$0")" && pwd)"
exec python3 "$here/guard-main-checkout.py" "${forward[@]}"

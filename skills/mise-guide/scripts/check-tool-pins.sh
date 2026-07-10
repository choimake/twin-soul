#!/usr/bin/env bash
# mise.toml [tools] / [tools.*] のバージョンが x.y.z 完全一致 pin か検証する。
# macOS 標準 bash 3.2 互換（mapfile 不使用）。

set -euo pipefail

readonly PIN_PATTERN='^[0-9]+\.[0-9]+\.[0-9]+$'

usage() {
  cat <<'EOF'
使い方:
  bash skills/mise-guide/scripts/check-tool-pins.sh [mise.toml ...]

引数省略時はカレントディレクトリの mise.toml と mise.*.toml（*.local.toml 除く）を検証する。
[tools] / [tools.*] の各 tool は x.y.z 形式（例: 1.2.3）の完全一致 pin のみ許可する。
EOF
}

strip_inline_comment() {
  local line="$1"
  line="${line%%#*}"
  # shellcheck disable=SC2001
  line="$(printf '%s' "$line" | sed 's/[[:space:]]*$//')"
  printf '%s' "$line"
}

is_tools_section_header() {
  local header="$1"
  [[ "$header" == '[tools]' ]] && return 0
  [[ "$header" =~ ^\[tools\. ]] && return 0
  return 1
}

tool_section_name() {
  local header="$1"
  if [[ "$header" == '[tools]' ]]; then
    printf 'flat'
    return 0
  fi
  if [[ "$header" =~ ^\[tools\.(.+)\]$ ]]; then
    printf '%s' "${BASH_REMATCH[1]}"
    return 0
  fi
  printf 'unknown'
}

is_exact_pin_version() {
  local version="$1"

  case "$version" in
    latest | lts | system)
      return 1
      ;;
  esac

  case "$version" in
    prefix:* | ref:* | sub-1:* | path:* | file:*)
      return 1
      ;;
  esac

  [[ "$version" =~ $PIN_PATTERN ]]
}

format_pin_hint() {
  local tool="$1"
  local reason="$2"

  case "$reason" in
    *配列形式*)
      printf 'mise.toml で 1 tool あたり x.y.z 文字列 1 つにしてください\n'
      ;;
    *未対応*)
      printf '文字列 pin または { version = "x.y.z" } 形式にしてください\n'
      ;;
    *)
      if [[ "$tool" == *:* || "$tool" == *\"* || "$tool" == *'/'* ]]; then
        printf 'mise use --pin "%s@x.y.z" で pin するか、mise.toml を x.y.z 形式に直してください\n' "$tool"
      else
        printf 'mise use --pin %s@x.y.z で pin するか、mise.toml を x.y.z 形式に直してください\n' "$tool"
      fi
      ;;
  esac
}

report_violation() {
  local file="$1"
  local tool="$2"
  local version="$3"
  local reason="$4"

  printf 'エラー: %s [tools].%s = "%s" — %s\n' "$file" "$tool" "$version" "$reason" >&2
  format_pin_hint "$tool" "$reason" >&2
}

validate_version() {
  local file="$1"
  local tool="$2"
  local version="$3"

  if is_exact_pin_version "$version"; then
    return 0
  fi

  local reason='x.y.z 形式（例: 1.2.3）で pin してください'
  case "$version" in
    latest | lts | system | prefix:* | ref:* | sub-1:*)
      reason='latest / lts / prefix: 等の fuzzy 指定は禁止です'
      ;;
  esac

  report_violation "$file" "$tool" "$version" "$reason"
  return 1
}

parse_flat_tools_line() {
  local file="$1"
  local line="$2"
  local tool=""
  local version=""

  if [[ "$line" =~ =[[:space:]]*\[ ]]; then
    if [[ "$line" =~ ^\"([^\"]+)\"[[:space:]]*= ]]; then
      tool="${BASH_REMATCH[1]}"
    elif [[ "$line" =~ ^([a-zA-Z0-9_.:-]+)[[:space:]]*= ]]; then
      tool="${BASH_REMATCH[1]}"
    else
      tool='(unknown)'
    fi
    report_violation "$file" "$tool" "$line" '配列形式は禁止です。1 tool あたり 1 つの x.y.z を指定してください'
    return 1
  fi

  if [[ "$line" =~ ^\"([^\"]+)\"[[:space:]]*=[[:space:]]*\"([^\"]+)\" ]]; then
    tool="${BASH_REMATCH[1]}"
    version="${BASH_REMATCH[2]}"
    validate_version "$file" "$tool" "$version"
    return $?
  fi

  if [[ "$line" =~ ^\"([^\"]+)\"[[:space:]]*=[[:space:]]*\'([^\']+)\' ]]; then
    tool="${BASH_REMATCH[1]}"
    version="${BASH_REMATCH[2]}"
    validate_version "$file" "$tool" "$version"
    return $?
  fi

  if [[ "$line" =~ ^([a-zA-Z0-9_.:-]+)[[:space:]]*=[[:space:]]*\"([^\"]+)\" ]]; then
    tool="${BASH_REMATCH[1]}"
    version="${BASH_REMATCH[2]}"
    validate_version "$file" "$tool" "$version"
    return $?
  fi

  if [[ "$line" =~ ^([a-zA-Z0-9_.:-]+)[[:space:]]*=[[:space:]]*\'([^\']+)\' ]]; then
    tool="${BASH_REMATCH[1]}"
    version="${BASH_REMATCH[2]}"
    validate_version "$file" "$tool" "$version"
    return $?
  fi

  if [[ "$line" =~ ^\"([^\"]+)\"[[:space:]]*=[[:space:]]*\{[[:space:]]*version[[:space:]]*=[[:space:]]*\"([^\"]+)\" ]]; then
    tool="${BASH_REMATCH[1]}"
    version="${BASH_REMATCH[2]}"
    validate_version "$file" "$tool" "$version"
    return $?
  fi

  if [[ "$line" =~ ^([a-zA-Z0-9_.:-]+)[[:space:]]*=[[:space:]]*\{[[:space:]]*version[[:space:]]*=[[:space:]]*\"([^\"]+)\" ]]; then
    tool="${BASH_REMATCH[1]}"
    version="${BASH_REMATCH[2]}"
    validate_version "$file" "$tool" "$version"
    return $?
  fi

  if [[ "$line" =~ = ]]; then
    if [[ "$line" =~ ^\"([^\"]+)\"[[:space:]]*= ]]; then
      tool="${BASH_REMATCH[1]}"
    elif [[ "$line" =~ ^([a-zA-Z0-9_.:-]+)[[:space:]]*= ]]; then
      tool="${BASH_REMATCH[1]}"
    else
      tool='(unknown)'
    fi
    report_violation "$file" "$tool" "$line" '未対応の [tools] 記法です。文字列または { version = "x.y.z" } 形式にしてください'
    return 1
  fi

  return 0
}

parse_nested_version_line() {
  local file="$1"
  local tool="$2"
  local line="$3"
  local version=""

  if [[ "$line" =~ ^version[[:space:]]*=[[:space:]]*\"([^\"]+)\" ]]; then
    version="${BASH_REMATCH[1]}"
    validate_version "$file" "$tool" "$version"
    return $?
  fi

  if [[ "$line" =~ ^version[[:space:]]*=[[:space:]]*\'([^\']+)\' ]]; then
    version="${BASH_REMATCH[1]}"
    validate_version "$file" "$tool" "$version"
    return $?
  fi

  if [[ "$line" =~ ^version[[:space:]]*= ]]; then
    report_violation "$file" "$tool" "$line" '未対応の version 記法です。version = "x.y.z" 形式にしてください'
    return 1
  fi

  return 0
}

check_tool_pins_file() {
  local file="$1"
  local in_tools_section=0
  local current_tool='flat'
  local line=""
  local stripped=""
  local failed=0
  local found_tools=0
  local had_tools_section=0

  if [[ ! -f "$file" ]]; then
    printf 'エラー: ファイルが見つかりません: %s\n' "$file" >&2
    return 1
  fi

  # Read-only validation; file is not modified during parse.
  # shellcheck disable=SC2094
  while IFS= read -r line || [[ -n "$line" ]]; do
    stripped="$(strip_inline_comment "$line")"
    case "$stripped" in
      '')
        continue
        ;;
      \[*\])
        if is_tools_section_header "$stripped"; then
          in_tools_section=1
          had_tools_section=1
          current_tool="$(tool_section_name "$stripped")"
          continue
        fi
        in_tools_section=0
        current_tool='flat'
        continue
        ;;
    esac

    if [[ $in_tools_section -eq 0 ]]; then
      continue
    fi

    if [[ "$current_tool" == 'flat' ]]; then
      if [[ "$stripped" =~ = ]]; then
        found_tools=1
        if ! parse_flat_tools_line "$file" "$stripped"; then
          failed=1
        fi
      fi
      continue
    fi

    if [[ "$stripped" =~ ^version[[:space:]]*= ]]; then
      found_tools=1
      if ! parse_nested_version_line "$file" "$current_tool" "$stripped"; then
        failed=1
      fi
    elif [[ "$stripped" =~ = ]]; then
      report_violation "$file" "$current_tool" "$stripped" '[tools.*] では version = "x.y.z" のみ許可します'
      found_tools=1
      failed=1
    fi
  done < "$file"

  if [[ $had_tools_section -eq 0 ]]; then
    return 0
  fi

  if [[ $found_tools -eq 0 ]]; then
    printf 'エラー: %s の [tools] セクションに tool 定義がありません\n' "$file" >&2
    return 1
  fi

  if [[ $failed -eq 1 ]]; then
    return 1
  fi

  printf 'OK: %s [tools] は x.y.z pin です\n' "$file"
  return 0
}

collect_default_files() {
  local dir="$1"
  local file=""

  if [[ -f "$dir/mise.toml" ]]; then
    printf '%s\n' "$dir/mise.toml"
  fi

  for file in "$dir"/mise.*.toml; do
    [[ -e "$file" ]] || continue
    case "$file" in
      *.local.toml)
        continue
        ;;
    esac
    if [[ "$file" != "$dir/mise.toml" ]]; then
      printf '%s\n' "$file"
    fi
  done
}

main() {
  local files=()
  local file=""
  local failed=0

  case "${1:-}" in
    -h | --help)
      usage
      exit 0
      ;;
    '')
      while IFS= read -r file; do
        files+=("$file")
      done < <(collect_default_files ".")
      ;;
    *)
      files=("$@")
      ;;
  esac

  if [[ ${#files[@]} -eq 0 ]]; then
    printf 'エラー: 検証対象の mise.toml が見つかりません\n' >&2
    exit 1
  fi

  for file in "${files[@]}"; do
    if ! check_tool_pins_file "$file"; then
      failed=1
    fi
  done

  if [[ $failed -eq 1 ]]; then
    exit 1
  fi
}

main "$@"

#!/bin/sh

set -eu

API_BASE="https://www.toptal.com/developers/gitignore/api"
TEMPLATES=""

print_usage() {
  cat <<'EOF'
使い方:
  bash skills/gitignore/scripts/fetch-gitignore.sh list
  bash skills/gitignore/scripts/fetch-gitignore.sh detect [target_path] [extra_templates...]
  bash skills/gitignore/scripts/fetch-gitignore.sh auto [target_path] [extra_templates...]
  bash skills/gitignore/scripts/fetch-gitignore.sh macos visualstudiocode node
  bash skills/gitignore/scripts/fetch-gitignore.sh macos,visualstudiocode,node

Commands:
  list    利用可能な gitignore.io templates を表示する。
  detect  現在の OS とリポジトリの目印から候補 template を推定する。
  auto    template を推定し、追加指定を merge してから .gitignore content を取得する。

補足:
  - template names は spaces または commas で区切れる。
  - 推定では package.json、pyproject.toml、go.mod、Cargo.toml、.vscode、
    .idea、pom.xml、build.gradle、*.tf などの一般的な files を見る。
  - host OS を推定できる場合は、対応する OS template も追加する。
EOF
}

require_command() {
  command_name="$1"
  purpose="$2"

  if ! command -v "$command_name" >/dev/null 2>&1; then
    echo "必要な command が見つかりません: ${command_name}" >&2
    echo "理由: ${purpose}" >&2
    echo "対応: '${command_name}' を install してから再実行してください。" >&2
    exit 1
  fi
}

append_template() {
  template="$1"

  case ",$TEMPLATES," in
    *,"$template",*) ;;
    *)
      if [ -n "$TEMPLATES" ]; then
        TEMPLATES="${TEMPLATES},${template}"
      else
        TEMPLATES="$template"
      fi
      ;;
  esac
}

normalize_templates() {
  printf '%s\n' "$@" \
    | tr ',[:space:]' '\n' \
    | sed '/^$/d' \
    | awk '!seen[tolower($0)]++ { print tolower($0) }'
}

add_normalized_templates() {
  normalized="$(normalize_templates "$@")"

  if [ -z "$normalized" ]; then
    return 0
  fi

  old_ifs=$IFS
  IFS='
'
  for template in $normalized; do
    append_template "$template"
  done
  IFS=$old_ifs
}

has_match() {
  search_root="$1"
  shift

  if [ ! -d "$search_root" ]; then
    return 1
  fi

  match="$(
    find "$search_root" \
      \( -type d \( \
        -name .git -o \
        -name node_modules -o \
        -name .venv -o \
        -name venv -o \
        -name vendor -o \
        -name dist -o \
        -name build -o \
        -name .next -o \
        -name target -o \
        -name .terraform -o \
        -name coverage \
      \) -prune \) -o \
      \( "$@" \) -print -quit 2>/dev/null
  )"

  [ -n "$match" ]
}

detect_host_os() {
  os_name="$(uname -s 2>/dev/null || true)"

  case "$os_name" in
    Darwin) append_template "macos" ;;
    Linux) append_template "linux" ;;
    CYGWIN*|MINGW*|MSYS*) append_template "windows" ;;
  esac
}

detect_templates() {
  target_path="$1"

  if [ ! -d "$target_path" ]; then
    echo "指定された対象パスが存在しません: $target_path" >&2
    exit 1
  fi

  detect_host_os

  if has_match "$target_path" -name package.json -o -name pnpm-workspace.yaml -o -name yarn.lock -o -name package-lock.json -o -name bun.lockb -o -name bun.lock; then
    append_template "node"
  fi

  if has_match "$target_path" -name pyproject.toml -o -name requirements.txt -o -name Pipfile -o -name poetry.lock -o -name setup.py -o -name tox.ini; then
    append_template "python"
  fi

  if has_match "$target_path" -name go.mod; then
    append_template "go"
  fi

  if has_match "$target_path" -name Cargo.toml; then
    append_template "rust"
  fi

  if has_match "$target_path" -name Gemfile; then
    append_template "ruby"
  fi

  if has_match "$target_path" -name composer.json; then
    append_template "php"
    append_template "composer"
  fi

  if has_match "$target_path" -name pom.xml; then
    append_template "java"
  fi

  if has_match "$target_path" -name build.gradle -o -name build.gradle.kts -o -name settings.gradle -o -name settings.gradle.kts -o -name gradlew; then
    append_template "gradle"
    append_template "java"
  fi

  if has_match "$target_path" -name '*.tf' -o -name '*.tfvars' -o -name '.terraform.lock.hcl'; then
    append_template "terraform"
  fi

  if has_match "$target_path" -name '.vscode' -o -name '*.code-workspace'; then
    append_template "visualstudiocode"
  fi

  if has_match "$target_path" -name '.idea' -o -name '*.iml'; then
    append_template "jetbrains"
  fi

  if has_match "$target_path" -name '*.xcodeproj' -o -name '*.xcworkspace'; then
    append_template "xcode"
  fi
}

fetch_templates() {
  if [ -z "$TEMPLATES" ]; then
    echo "指定された template 名がありません。" >&2
    exit 1
  fi

  curl -fsSL "${API_BASE}/${TEMPLATES}"
}

if [ "$#" -eq 0 ]; then
  print_usage >&2
  exit 1
fi

require_command curl "gitignore.io から template list と .gitignore content を取得するため"
require_command awk "template names の normalize と deduplicate を行うため"
require_command find "detect / auto で language、IDE、tool markers を scan するため"
require_command sed "normalization 中に空の template names を除去するため"
require_command tr "comma-separated / space-separated の template names を分割するため"
require_command uname "host operating system template を推定するため"

case "$1" in
  list|--list)
    curl -fsSL "${API_BASE}/list?format=lines"
    ;;
  detect)
    shift
    target_path="${1:-.}"
    if [ "$#" -gt 0 ]; then
      shift
    fi
    detect_templates "$target_path"
    if [ "$#" -gt 0 ]; then
      add_normalized_templates "$@"
    fi
    if [ -n "$TEMPLATES" ]; then
      printf '%s\n' "$TEMPLATES"
    fi
    ;;
  auto)
    shift
    target_path="${1:-.}"
    if [ "$#" -gt 0 ]; then
      shift
    fi
    detect_templates "$target_path"
    if [ "$#" -gt 0 ]; then
      add_normalized_templates "$@"
    fi
    fetch_templates
    ;;
  help|--help|-h)
    print_usage
    ;;
  *)
    add_normalized_templates "$@"
    fetch_templates
    ;;
esac

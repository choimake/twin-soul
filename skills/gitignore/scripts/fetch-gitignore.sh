#!/bin/sh

set -eu

REPO_URL="https://github.com/github/gitignore.git"
TEMPLATES_DIR="${GITIGNORE_TEMPLATES_DIR:-${XDG_CACHE_HOME:-$HOME/.cache}/twin-soul/github-gitignore}"
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
  list    利用可能な github/gitignore templates を表示する。
  detect  現在の OS とリポジトリの目印から候補 template を推定する。
  auto    template を推定し、追加指定を merge してから .gitignore content を取得する。

補足:
  - template は github/gitignore を git clone --depth 1 した cache から読む。
    cache の場所は GITIGNORE_TEMPLATES_DIR（既定: ${XDG_CACHE_HOME:-~/.cache}/twin-soul/github-gitignore）。
    実行のたびに浅く fetch して最新にする。更新できないときは警告を出して cache を使う。
  - template names は spaces または commas で区切れる。大文字小文字は区別しない。
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

update_templates() {
  if git -C "$TEMPLATES_DIR" fetch --quiet --depth 1 origin HEAD >/dev/null 2>&1; then
    git -C "$TEMPLATES_DIR" reset --quiet --hard FETCH_HEAD
    return 0
  fi

  echo "github/gitignore を更新できませんでした。cache の commit $(git -C "$TEMPLATES_DIR" rev-parse --short HEAD) を使います。" >&2
}

ensure_templates() {
  if [ -d "$TEMPLATES_DIR" ]; then
    if ! git --git-dir="$TEMPLATES_DIR/.git" rev-parse --verify -q HEAD >/dev/null 2>&1; then
      echo "template の cache が壊れています: ${TEMPLATES_DIR}" >&2
      echo "対応: このディレクトリを消して再実行してください。" >&2
      exit 1
    fi
    update_templates
    return 0
  fi

  require_command git "github/gitignore の templates を cache へ clone するため"
  mkdir -p "$(dirname "$TEMPLATES_DIR")"
  git clone --quiet --depth 1 "$REPO_URL" "$TEMPLATES_DIR" >&2
}

list_templates() {
  ensure_templates
  find "$TEMPLATES_DIR" -name .git -prune -o -type f -name '*.gitignore' -print \
    | sed 's#.*/##; s#\.gitignore$##' \
    | tr '[:upper:]' '[:lower:]' \
    | sort -u
}

# root、Global/、community/ の順に探し、最初に見つかった file を返す。
resolve_template() {
  name="$1"

  case "$name" in
    *[!a-z0-9._+-]*) return 1 ;;
  esac

  for search_dir in "$TEMPLATES_DIR" "$TEMPLATES_DIR/Global"; do
    found="$(find "$search_dir" -maxdepth 1 -type f -iname "${name}.gitignore" -print 2>/dev/null | head -n 1)"
    if [ -n "$found" ]; then
      printf '%s\n' "$found"
      return 0
    fi
  done

  found="$(find "$TEMPLATES_DIR/community" -type f -iname "${name}.gitignore" -print 2>/dev/null | sort | head -n 1)"
  if [ -n "$found" ]; then
    printf '%s\n' "$found"
    return 0
  fi

  return 1
}

fetch_templates() {
  if [ -z "$TEMPLATES" ]; then
    echo "指定された template 名がありません。" >&2
    exit 1
  fi

  ensure_templates

  files=""
  missing=""
  old_ifs=$IFS
  IFS=','
  for template in $TEMPLATES; do
    if file="$(resolve_template "$template")"; then
      files="${files}${file}
"
    else
      missing="${missing} ${template}"
    fi
  done
  IFS=$old_ifs

  if [ -n "$missing" ]; then
    echo "github/gitignore に見つからない template があります:${missing}" >&2
    echo "対応: 'list' で名前を確認してください。" >&2
    exit 1
  fi

  commit="$(git -C "$TEMPLATES_DIR" rev-parse --short HEAD 2>/dev/null || echo unknown)"
  printf '# Generated from https://github.com/github/gitignore (commit %s)\n' "$commit"
  printf '# Templates: %s\n' "$TEMPLATES"

  old_ifs=$IFS
  IFS='
'
  for file in $files; do
    title="$(basename "$file" .gitignore)"
    printf '\n### %s ###\n' "$title"
    cat "$file"
    if [ -n "$(tail -c 1 "$file")" ]; then
      printf '\n'
    fi
  done
  IFS=$old_ifs
}

if [ "$#" -eq 0 ]; then
  print_usage >&2
  exit 1
fi

require_command awk "template names の normalize と deduplicate を行うため"
require_command find "detect / auto で language、IDE、tool markers を scan するため"
require_command sed "normalization 中に空の template names を除去するため"
require_command tr "comma-separated / space-separated の template names を分割するため"
require_command uname "host operating system template を推定するため"

case "$1" in
  list|--list)
    list_templates
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

#!/usr/bin/env python3
"""main checkout への編集と git 書き込みを拒否する。"""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any

NEXT_STEP = (
    "main checkout への変更は禁止です。"
    "先に `git worktree add .worktrees/wt-<name> -b <scope>/<short-name>` "
    "を実行し、`.worktrees/wt-<name>/` 配下を編集してください。"
)

ALLOW_RELATIVE_PREFIXES = (
    "memory/",
    ".cursor/plans/",
    ".worktrees/",
)

GIT_READONLY = {
    "status",
    "log",
    "diff",
    "show",
    "blame",
    "describe",
    "rev-parse",
    "rev-list",
    "ls-files",
    "ls-tree",
    "cat-file",
    "name-rev",
    "symbolic-ref",
    "shortlog",
    "range-diff",
}

GIT_WRITE = {
    "add",
    "commit",
    "push",
    "rebase",
    "merge",
    "cherry-pick",
    "revert",
    "reset",
    "am",
}

FILE_EDIT_TOOLS = {
    "write",
    "strreplace",
    "delete",
    "editnotebook",
    "edit",
    "multiedit",
    "notebookedit",
    "apply_patch",
}

APPLY_PATCH_FILE_RE = re.compile(
    r"^\*\*\* (?:Add|Update|Delete|Move|Rename) File: (.+)$",
    re.MULTILINE,
)

SHELL_TOOLS = {"shell", "bash"}


def log(message: str) -> None:
    print(f"guard-main-checkout: {message}", file=sys.stderr)
    dest = os.environ.get("GUARD_LOG")
    if dest:
        try:
            with open(dest, "a", encoding="utf-8") as handle:
                handle.write(message + "\n")
        except OSError:
            pass


def emit(runtime: str, event: str, allowed: bool, reason: str) -> int:
    if runtime == "claude":
        hook_event = "PreToolUse"
        payload = {
            "hookSpecificOutput": {
                "hookEventName": hook_event,
                "permissionDecision": "allow" if allowed else "deny",
                "permissionDecisionReason": reason,
            }
        }
    else:
        payload = {"permission": "allow" if allowed else "deny"}
        if not allowed:
            payload["agent_message"] = reason
            payload["user_message"] = reason
    json.dump(payload, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


def fail_open(runtime: str, event: str, why: str) -> int:
    log(f"fail-open: {why}")
    return emit(runtime, event, True, why)


def is_under(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def resolve_target(raw: str, cwd: Path) -> Path:
    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = cwd / candidate
    if candidate.exists() or candidate.is_symlink():
        return candidate.resolve()
    parent = candidate.parent
    while not parent.exists() and parent != parent.parent:
        parent = parent.parent
    if parent.exists():
        return parent.resolve() / candidate.name
    return candidate


def git_toplevel(cwd: Path) -> Path | None:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=str(cwd),
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    text = out.strip()
    return Path(text) if text else None


def main_repo_root(toplevel: Path) -> Path:
    parts = toplevel.parts
    if ".worktrees" in parts:
        idx = parts.index(".worktrees")
        return Path(*parts[:idx])
    return toplevel


def is_named_worktree(toplevel: Path) -> bool:
    return ".worktrees" in toplevel.parts


def is_allowed_relative(path: Path, main_root: Path) -> bool:
    try:
        rel = path.resolve().relative_to(main_root.resolve()).as_posix()
    except ValueError:
        return False
    return any(rel == prefix.rstrip("/") or rel.startswith(prefix) for prefix in ALLOW_RELATIVE_PREFIXES)


def classify_edit(path: Path, cwd: Path) -> tuple[bool, str]:
    toplevel = git_toplevel(path.parent if path.parent.exists() else cwd) or git_toplevel(cwd)
    if toplevel is None:
        return True, "git 管理外なので許可"
    main_root = main_repo_root(toplevel)
    if not is_under(path, main_root):
        return True, "リポジトリ外なので許可"
    if is_named_worktree(toplevel) and not is_under(path, toplevel):
        return False, NEXT_STEP
    if is_allowed_relative(path, main_root):
        return True, "許可リスト内"
    if is_named_worktree(toplevel):
        return True, "worktree 内"
    return False, NEXT_STEP


def skip_git_global_args(tokens: list[str]) -> tuple[str | None, Path | None]:
    i = 0
    override_cwd: Path | None = None
    while i < len(tokens):
        token = tokens[i]
        if token == "-C" and i + 1 < len(tokens):
            override_cwd = Path(tokens[i + 1])
            i += 2
            continue
        if token.startswith("-C") and len(token) > 2:
            override_cwd = Path(token[2:])
            i += 1
            continue
        if token in {"--git-dir", "--work-tree"} and i + 1 < len(tokens):
            i += 2
            continue
        if token.startswith("--git-dir=") or token.startswith("--work-tree="):
            i += 1
            continue
        if token == "-c" and i + 1 < len(tokens):
            i += 2
            continue
        if token.startswith("-c"):
            i += 1
            continue
        if token.startswith("-") and token != "--":
            i += 1
            continue
        if token == "--":
            i += 1
            if i < len(tokens):
                return tokens[i], override_cwd
            return None, override_cwd
        return token, override_cwd
    return None, override_cwd


def parse_git_command(command: str) -> tuple[str | None, Path | None]:
    try:
        tokens = shlex.split(command)
    except ValueError:
        return None, None
    if not tokens:
        return None, None
    git_idx = next((i for i, tok in enumerate(tokens) if Path(tok).name in {"git", "git.exe"}), None)
    if git_idx is None:
        return None, None
    return skip_git_global_args(tokens[git_idx + 1 :])


def classify_shell(command: str, cwd: Path) -> tuple[bool, str]:
    subcommand, override_cwd = parse_git_command(command)
    if subcommand is None:
        return True, "git 以外の shell は許可"
    effective_cwd = override_cwd if override_cwd is not None else cwd
    if not effective_cwd.is_absolute():
        effective_cwd = cwd / effective_cwd
    toplevel = git_toplevel(effective_cwd if effective_cwd.exists() else cwd)
    if subcommand == "worktree":
        return True, "git worktree 操作は許可"
    if subcommand in GIT_READONLY:
        return True, "読み取り専用 git は許可"
    if subcommand not in GIT_WRITE:
        return True, f"git {subcommand} は対象外なので許可"
    if toplevel is not None and is_named_worktree(toplevel):
        return True, "worktree 内の git 書き込みは許可"
    if override_cwd is not None and ".worktrees" in Path(override_cwd).parts:
        return True, "worktree を指す git -C は許可"
    return False, NEXT_STEP


def first_string(*values: Any) -> str | None:
    for value in values:
        if isinstance(value, str) and value:
            return value
        if isinstance(value, list) and value and isinstance(value[0], str):
            return value[0]
    return None


def extract_path(payload: dict[str, Any], cwd: Path) -> Path | None:
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        tool_input = payload.get("arguments")
    if not isinstance(tool_input, dict):
        tool_input = {}
    raw = first_string(
        tool_input.get("path"),
        tool_input.get("file_path"),
        tool_input.get("target_file"),
        tool_input.get("notebook_path"),
        payload.get("file_path"),
        payload.get("path"),
    )
    if raw is None:
        return None
    return resolve_target(raw, cwd)


def extract_apply_patch_paths(command: str, cwd: Path) -> list[Path]:
    paths: list[Path] = []
    for match in APPLY_PATCH_FILE_RE.finditer(command):
        raw = match.group(1).strip()
        if " -> " in raw:
            old, new = raw.split(" -> ", 1)
            paths.append(resolve_target(old.strip(), cwd))
            paths.append(resolve_target(new.strip(), cwd))
        else:
            paths.append(resolve_target(raw, cwd))
    return paths


def classify_apply_patch(command: str, cwd: Path) -> tuple[bool, str]:
    paths = extract_apply_patch_paths(command, cwd)
    if not paths:
        return True, "apply_patch の対象パスが無いので許可"
    for path in paths:
        allowed, reason = classify_edit(path, cwd)
        if not allowed:
            return False, reason
    return True, "apply_patch の全パスが許可"


def extract_command(payload: dict[str, Any]) -> str | None:
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        tool_input = payload.get("arguments")
    if not isinstance(tool_input, dict):
        tool_input = {}
    return first_string(payload.get("command"), tool_input.get("command"))


def extract_cwd(payload: dict[str, Any]) -> Path:
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        tool_input = {}
    raw = first_string(
        payload.get("cwd"),
        tool_input.get("working_directory"),
        tool_input.get("cwd"),
        os.environ.get("PWD"),
    )
    if raw:
        return Path(raw)
    return Path.cwd()


def decide(payload: dict[str, Any], event: str) -> tuple[bool, str]:
    cwd = extract_cwd(payload)
    tool_name = str(payload.get("tool_name") or payload.get("tool") or "").lower()
    if tool_name == "apply_patch":
        command = extract_command(payload)
        if not command:
            return True, "apply_patch の command が無いので許可"
        return classify_apply_patch(command, cwd)
    if event == "beforeShellExecution" or tool_name in SHELL_TOOLS:
        command = extract_command(payload)
        if not command:
            return True, "command が無いので許可"
        return classify_shell(command, cwd)
    if event == "preToolUse" or tool_name in FILE_EDIT_TOOLS:
        path = extract_path(payload, cwd)
        if path is None:
            if tool_name in SHELL_TOOLS:
                command = extract_command(payload)
                if command:
                    return classify_shell(command, cwd)
            return True, "対象パスが無いので許可"
        return classify_edit(path, cwd)
    command = extract_command(payload)
    if command:
        return classify_shell(command, cwd)
    path = extract_path(payload, cwd)
    if path is not None:
        return classify_edit(path, cwd)
    return True, "判定対象が無いので許可"


def run_self_test() -> int:
    import tempfile

    failures: list[str] = []

    def check(name: str, allowed: bool, expected: bool) -> None:
        if allowed != expected:
            failures.append(f"{name}: expected {expected}, got {allowed}")

    with tempfile.TemporaryDirectory(prefix="guard-main-checkout-") as tmp:
        root = Path(tmp)
        subprocess.check_call(["git", "init"], cwd=root, stdout=subprocess.DEVNULL)
        (root / "AGENTS.md").write_text("orig\n", encoding="utf-8")
        (root / "memory").mkdir()
        (root / "memory" / "handoff.md").write_text("note\n", encoding="utf-8")
        (root / ".cursor" / "plans").mkdir(parents=True)
        (root / ".cursor" / "plans" / "x.md").write_text("plan\n", encoding="utf-8")
        subprocess.check_call(
            ["git", "worktree", "add", "-b", "docs/hook-smoke", ".worktrees/wt-smoke"],
            cwd=root,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        worktree = root / ".worktrees" / "wt-smoke"

        allowed, _ = classify_edit(root / "AGENTS.md", root)
        check("deny main AGENTS.md", allowed, False)
        allowed, _ = classify_edit(root / "memory" / "handoff.md", root)
        check("allow memory", allowed, True)
        allowed, _ = classify_edit(root / ".cursor" / "plans" / "x.md", root)
        check("allow plans", allowed, True)
        allowed, _ = classify_edit(worktree / "AGENTS.md", root)
        check("allow worktree path from main cwd", allowed, True)
        allowed, _ = classify_edit(worktree / "AGENTS.md", worktree)
        check("allow edit inside worktree", allowed, True)
        allowed, _ = classify_edit(root / "AGENTS.md", worktree)
        check("deny main file from worktree cwd", allowed, False)
        allowed, _ = classify_shell("git status", root)
        check("allow git status", allowed, True)
        allowed, _ = classify_shell("git worktree add .worktrees/wt-x -b feat/x", root)
        check("allow git worktree add", allowed, True)
        allowed, _ = classify_shell("git commit -m test", root)
        check("deny git commit on main", allowed, False)
        allowed, _ = classify_shell("git add AGENTS.md", root)
        check("deny git add on main", allowed, False)
        allowed, _ = classify_shell("git commit -m test", worktree)
        check("allow git commit in worktree", allowed, True)
        allowed, _ = classify_shell(f"git -C {worktree} commit -m test", root)
        check("allow git -C worktree commit", allowed, True)
        allowed, _ = classify_shell("echo hello", root)
        check("allow non-git shell", allowed, True)
        deny_patch = f"*** Update File: {root / 'AGENTS.md'}\n@@\n-orig\n+hacked\n"
        allowed, reason = classify_apply_patch(deny_patch, root)
        check("deny apply_patch AGENTS.md", allowed, False)
        if NEXT_STEP not in reason:
            failures.append("apply_patch deny reason missing next step")
        allow_patch = f"*** Update File: {root / 'memory' / 'handoff.md'}\n@@\n-note\n+hello\n"
        allowed, _ = classify_apply_patch(allow_patch, root)
        check("allow apply_patch memory", allowed, True)

        payload = {
            "tool_name": "Write",
            "tool_input": {"path": str(root / "AGENTS.md")},
            "cwd": str(root),
        }
        allowed, reason = decide(payload, "preToolUse")
        check("decide Write AGENTS.md", allowed, False)
        if NEXT_STEP not in reason:
            failures.append("deny reason missing next step")

    if failures:
        print("SELF-TEST FAILED", file=sys.stderr)
        for item in failures:
            print(f"- {item}", file=sys.stderr)
        return 1
    print("SELF-TEST PASSED")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime", choices=("cursor", "claude"), default="cursor")
    parser.add_argument(
        "--event",
        choices=("preToolUse", "beforeShellExecution", "auto"),
        default="auto",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.self_test:
        return run_self_test()

    raw = sys.stdin.read()
    if not raw.strip():
        return fail_open(args.runtime, args.event, "stdin が空")
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        return fail_open(args.runtime, args.event, f"JSON を読めない: {exc}")
    if not isinstance(payload, dict):
        return fail_open(args.runtime, args.event, "JSON が object ではない")

    event = args.event
    if event == "auto":
        if extract_command(payload) and not extract_path(payload, extract_cwd(payload)):
            event = "beforeShellExecution"
        else:
            event = "preToolUse"
    allowed, reason = decide(payload, event)
    log(f"{event} allowed={allowed} reason={reason}")
    return emit(args.runtime, event, allowed, reason)


if __name__ == "__main__":
    sys.exit(main())

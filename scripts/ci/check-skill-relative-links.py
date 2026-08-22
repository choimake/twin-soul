#!/usr/bin/env python3
"""skills/ 配下の markdown 相対リンクが各 skill ディレクトリ内に閉じているか検証する。"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
SCHEME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def is_relative_fs_link(target: str) -> bool:
    text = target.strip()
    if not text:
        return False
    if text.startswith(("#", "/", "//")):
        return False
    if SCHEME_RE.match(text):
        return False
    return True


def link_path(target: str) -> str:
    first = target.strip().split(None, 1)[0]
    return first.split("#", 1)[0].split("?", 1)[0]


def skill_root_for(md_path: Path, skills_root: Path) -> Path | None:
    try:
        relative = md_path.resolve().relative_to(skills_root.resolve())
    except ValueError:
        return None
    if not relative.parts:
        return None
    return skills_root / relative.parts[0]


def iter_markdown(skills_root: Path) -> list[Path]:
    if not skills_root.is_dir():
        return []
    return sorted(path for path in skills_root.rglob("*.md") if path.is_file())


def find_outbound_links(md_path: Path, skills_root: Path) -> list[str]:
    skill_root = skill_root_for(md_path, skills_root)
    if skill_root is None:
        return []

    findings: list[str] = []
    text = md_path.read_text(encoding="utf-8")
    skill_root_resolved = skill_root.resolve()

    for match in LINK_RE.finditer(text):
        raw_target = match.group(1)
        if not is_relative_fs_link(raw_target):
            continue
        path_part = link_path(raw_target)
        if not path_part:
            continue
        resolved = (md_path.parent / path_part).resolve()
        try:
            resolved.relative_to(skill_root_resolved)
        except ValueError:
            line_no = text.count("\n", 0, match.start()) + 1
            rel = md_path.relative_to(skills_root.parent)
            findings.append(f"{rel}:{line_no}: {path_part} -> {resolved}")

    return findings


def check(skills_root: Path) -> list[str]:
    findings: list[str] = []
    for md_path in iter_markdown(skills_root):
        findings.extend(find_outbound_links(md_path, skills_root))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="skill 配下の markdown 相対リンクが skill ディレクトリ外へ出ていないか検証する"
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="リポジトリルート。省略時はこのスクリプトから推定する",
    )
    args = parser.parse_args()
    root = (args.root or repo_root()).resolve()
    skills_root = root / "skills"

    if not skills_root.is_dir():
        print(f"エラー: {skills_root} が見つかりません", file=sys.stderr)
        return 1

    findings = check(skills_root)
    if findings:
        print(
            "エラー: skill 外へ出る markdown 相対リンクがあります。"
            "相対リンクは skills/<skill-name>/ 内に閉じてください。",
            file=sys.stderr,
        )
        for finding in findings:
            print(finding, file=sys.stderr)
        return 1

    print(f"OK: {skills_root} の相対リンクは各 skill 内に閉じている")
    return 0


if __name__ == "__main__":
    sys.exit(main())

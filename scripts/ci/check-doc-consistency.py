#!/usr/bin/env python3
"""README の skill 一覧とレビュー出力テンプレートの表記を検査する。"""

from __future__ import annotations

import re
import sys
from pathlib import Path

README_SECTION = "## 利用できるスキル"
README_SKILL_RE = re.compile(r"^- \*\*([^*]+)\*\*")
BRANCH_LABEL_RE = re.compile(r"^\s*\[([^\]\r\n]*場合)\]\s*$")
ALLOWED_BRANCH_LABELS = {
    "重大指摘がある場合",
    "重大指摘が無い場合",
}


def report(path: Path, line_number: int, message: str, root: Path) -> None:
    relative_path = path.relative_to(root).as_posix()
    print(f"{relative_path}:{line_number}: {message}")


def read_readme_skills(
    readme: Path, root: Path
) -> tuple[dict[str, int], int] | None:
    lines = readme.read_text(encoding="utf-8").splitlines()
    section_line = next(
        (number for number, line in enumerate(lines, start=1) if line == README_SECTION),
        None,
    )
    if section_line is None:
        report(readme, 1, f"「{README_SECTION.removeprefix('## ')}」節が見つかりません", root)
        return None

    skills: dict[str, int] = {}
    for number, line in enumerate(lines[section_line:], start=section_line + 1):
        if line.startswith("## "):
            break
        match = README_SKILL_RE.match(line)
        if match:
            skills[match.group(1)] = number
    return skills, section_line


def check_readme_skills(root: Path) -> bool:
    readme = root / "README.md"
    result = read_readme_skills(readme, root)
    if result is None:
        return False
    readme_skills, section_line = result

    actual_skills = {
        skill_file.parent.name
        for skill_file in (root / "skills").glob("*/SKILL.md")
    }
    valid = True
    for name in sorted(actual_skills - readme_skills.keys()):
        report(readme, section_line, f"README の skill 一覧に {name} がありません", root)
        valid = False
    for name in sorted(readme_skills.keys() - actual_skills):
        report(readme, readme_skills[name], f"skills/{name}/SKILL.md がありません", root)
        valid = False
    return valid


def check_review_templates(root: Path) -> bool:
    valid = True
    pattern = "*/assets/review-output-template.md"
    for template in sorted((root / "skills").glob(pattern)):
        lines = template.read_text(encoding="utf-8").splitlines()
        for number, line in enumerate(lines, start=1):
            match = BRANCH_LABEL_RE.match(line)
            if match is None:
                continue
            label = match.group(1)
            if label not in ALLOWED_BRANCH_LABELS:
                report(template, number, f"不正な分岐ラベル [{label}]", root)
                valid = False
    return valid


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    valid = check_readme_skills(root)
    valid = check_review_templates(root) and valid
    return 0 if valid else 1


if __name__ == "__main__":
    sys.exit(main())

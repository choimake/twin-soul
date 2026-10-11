"""全ルールを決まった順に呼び、指摘をまとめる。

ルールを足す手順:
1. rules_*.py の合う層に check_xxx() を書く。指摘は「id: 理由」の形で findings に足す
2. check_html() から呼ぶ。呼んだ順がそのまま出力の順になる
3. selftest.py の CASES に、そのルールだけが指摘される見本を足す
4. test_rules_*.py に合格と不合格のケースを足す。test_checks.py の EVERY_RULE_HTML と RULE_ORDER にも足す
5. references/tech-intro-knowledge.md の「点検」にある、スクリプトが見るものの一覧に足す
"""

from __future__ import annotations

from css import parse_sheet, style_text
from htmldoc import DocParser
from rules_content import (
    check_agent_skills,
    check_banned,
    check_early_detail,
    check_endings,
    check_goals,
    check_scope,
    check_terms,
    check_volume,
)
from rules_figures import (
    check_dot_line,
    check_dot_travel,
    check_fig_roles,
    check_motion_figs,
    check_svg,
    check_svg_text,
)
from rules_layout import check_external, check_motion, check_responsive, check_toc


def check_html(html: str) -> list[str]:
    parser = DocParser()
    parser.feed(html)
    css = style_text(parser.root)
    sheet = parse_sheet(css)
    findings: list[str] = []
    check_responsive(parser.root, sheet, css, findings)
    check_external(html, findings)
    check_motion(sheet, findings)
    check_toc(parser.root, sheet, findings)
    check_banned(parser.root, findings)
    check_dot_line(parser.root, sheet, findings)
    check_dot_travel(parser.root, sheet, findings)
    check_svg(parser.root, sheet, findings)
    check_svg_text(parser.root, sheet, findings)
    check_fig_roles(parser.root, findings)
    check_goals(parser.root, findings)
    check_scope(parser.root, findings)
    check_agent_skills(parser.root, findings)
    check_volume(parser.root, findings)
    check_endings(parser.root, findings)
    check_terms(parser.root, findings)
    check_early_detail(parser.root, findings)
    check_motion_figs(parser.root, sheet, findings)
    return dedupe(findings)


def dedupe(findings: list[str]) -> list[str]:
    counts: dict[str, int] = {}
    order: list[str] = []
    for item in findings:
        if item not in counts:
            order.append(item)
            counts[item] = 0
        counts[item] += 1
    output = []
    for item in order:
        if counts[item] > 1:
            output.append(f"{item}（{counts[item]}箇所）")
        else:
            output.append(item)
    return output

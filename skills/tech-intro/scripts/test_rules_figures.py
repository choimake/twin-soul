"""rules_figures.py のテスト。実行: python3 -I -m unittest discover -s skills/tech-intro/scripts"""

from __future__ import annotations

import unittest

from rules_figures import (
    check_dot_line,
    check_dot_travel,
    check_fig_roles,
    check_motion_figs,
    check_svg,
    check_svg_text,
    font_px,
    is_spanning_line,
    labeled_children,
    offset_parent,
)
from testutil import find, parse, parse_page


MOVE_CSS = """
.box { border: 1px solid; }
.dot { position: absolute; animation: hop 1s linear infinite; }
@keyframes hop { from { left: 0; } to { left: 40px; } }
.flow { animation: dash 1s linear infinite; }
@keyframes dash { from { stroke-dashoffset: 0; } to { stroke-dashoffset: -100; } }
"""

# 点は箱と箱のあいだの .link の中だけを動き、線も .link の中に収まる
DOT_OK = f"""
<style>{MOVE_CSS}
.link {{ position: relative; }}
.link::before {{ content: ""; position: absolute; left: 0; right: 0; height: 2px; }}
</style>
<div class="row"><div class="box">event</div><div class="link"><span class="dot"></span></div><div class="box">trigger</div></div>
"""


class HelperTest(unittest.TestCase):
    def test_is_spanning_line(self) -> None:
        self.assertTrue(is_spanning_line({"position": "absolute", "height": "2px", "left": "0", "right": "0"}))
        self.assertTrue(is_spanning_line({"position": "absolute", "height": "4px", "width": "100%"}))
        self.assertFalse(is_spanning_line({"position": "absolute", "height": "5px", "width": "100%"}))
        self.assertFalse(is_spanning_line({"position": "absolute", "height": "2px", "left": "0", "right": "auto"}))
        self.assertFalse(is_spanning_line({"position": "relative", "height": "2px", "width": "100%"}))

    def test_labeled_children_needs_box_class_and_text(self) -> None:
        root = parse('<div class="row"><div class="box">a</div><div class="box"></div><div>b</div><p class="card">c</p></div>')
        self.assertEqual([child.tag for child in labeled_children(find(root, "row"))], ["div", "p"])

    def test_offset_parent_is_nearest_positioned_ancestor(self) -> None:
        root, sheet, _ = parse_page(
            "<style>.outer { position: relative } .dot { position: absolute }</style>"
            '<div class="outer"><div class="mid"><span class="dot"></span></div></div>'
        )
        self.assertIs(offset_parent(find(root, "dot"), sheet.rules), find(root, "outer"))

    def test_offset_parent_of_static_is_parent(self) -> None:
        root, sheet, _ = parse_page('<div class="outer"><div class="mid"><span class="dot"></span></div></div>')
        self.assertIs(offset_parent(find(root, "dot"), sheet.rules), find(root, "mid"))

    def test_font_px_inherits_and_converts(self) -> None:
        root, sheet, _ = parse_page('<style>svg { font-size: 0.75rem }</style><svg><text>a</text></svg><p font-size="x">b</p>')
        self.assertEqual(font_px(find(root, "text"), sheet), 12)
        self.assertIsNone(font_px(find(root, "p"), sheet))
        bare, sheet, _ = parse_page("<span>a</span>")
        self.assertEqual(font_px(find(bare, "span"), sheet), 16.0)


class DotRulesTest(unittest.TestCase):
    def run_rules(self, html: str) -> list[str]:
        root, sheet, _ = parse_page(html)
        findings: list[str] = []
        check_dot_line(root, sheet, findings)
        check_dot_travel(root, sheet, findings)
        return findings

    def test_dot_between_boxes_passes(self) -> None:
        self.assertEqual(self.run_rules(DOT_OK), [])

    def test_line_through_row_of_boxes_fails(self) -> None:
        html = DOT_OK.replace(".link::before", ".row::before")
        self.assertEqual(
            self.run_rules(html),
            ["dot-line: 線が箱の並びを端から端まで貫いている（.row::before）。線は箱の縁から次の箱の縁までにする"],
        )

    def test_dot_over_boxes_fails(self) -> None:
        html = DOT_OK.replace(".link { position: relative; }", ".row { position: relative; }")
        self.assertEqual(
            self.run_rules(html),
            ["dot-travel: 点が箱の上を動いている（span.dot の基準が div.row）。点は箱と箱のあいだの要素の中だけを動かす"],
        )

    def test_dot_inside_box_fails(self) -> None:
        html = f'<style>{MOVE_CSS} .box {{ position: relative; }}</style><div class="box">step<span class="dot"></span></div>'
        self.assertEqual(
            self.run_rules(html), ["dot-travel: 点が箱の中を動いている（div.box）。点は箱の外の線だけを動かす"]
        )


SVG = """
<style>{css}</style>
<svg viewBox="0 0 300 80">
  <path class="flow" d="{d}"/>
  <rect x="20" y="10" width="80" height="40"/>
  <rect x="160" y="10" width="80" height="40"/>
</svg>
"""


class SvgTest(unittest.TestCase):
    def run_rule(self, d: str, css: str = MOVE_CSS) -> list[str]:
        root, sheet, _ = parse_page(SVG.format(css=css, d=d))
        findings: list[str] = []
        check_svg(root, sheet, findings)
        return findings

    def test_line_between_boxes_passes(self) -> None:
        self.assertEqual(self.run_rule("M100 30 L160 30"), [])

    def test_line_across_box_fails(self) -> None:
        self.assertEqual(self.run_rule("M10 30 L240 30"), ["svg-cross: 動く線が箱の面を横切っている。線は箱の外側で止める"])

    def test_still_line_is_not_checked(self) -> None:
        self.assertEqual(self.run_rule("M10 30 L240 30", css=""), [])

    def test_unsupported_path_is_reported(self) -> None:
        self.assertEqual(
            self.run_rule("M100 30 Q130 0 160 30"),
            ["svg-cross: 動く線を検査できない（Q）。直線か三次曲線だけにする"],
        )


class SvgTextTest(unittest.TestCase):
    def run_rule(self, label: str, anchor: str = "middle") -> list[str]:
        root, sheet, _ = parse_page(
            "<style>svg text { font-size: 12px; }</style>"
            f'<svg><rect x="20" y="10" width="124" height="52"/><text x="82" y="36" text-anchor="{anchor}">{label}</text></svg>'
        )
        findings: list[str] = []
        check_svg_text(root, sheet, findings)
        return findings

    def test_short_label_passes(self) -> None:
        self.assertEqual(self.run_rule("短い名前"), [])

    def test_long_label_fails(self) -> None:
        self.assertEqual(
            self.run_rule("同じプロセス・別プロセス"),
            ["svg-text: 「同じプロセス・別プロセス」が箱の幅（124）からはみ出す見込み。文字を短くするか、行を分けるか、箱を広げる"],
        )

    def test_start_anchor_overflows_right(self) -> None:
        self.assertEqual(len(self.run_rule("あいうえおか", anchor="start")), 1)
        self.assertEqual(self.run_rule("あいうえお", anchor="start"), [])


H2X4 = "<h2>a</h2><h2>b</h2><h2>c</h2><h2>d</h2>"


class FigRolesTest(unittest.TestCase):
    def run_rule(self, html: str) -> list[str]:
        root = parse(html)
        findings: list[str] = []
        check_fig_roles(root, findings)
        return findings

    def test_short_page_is_not_checked(self) -> None:
        self.assertEqual(self.run_rule("<h2>a</h2><h2>b</h2><h2>c</h2>"), [])

    def test_all_roles_present_or_skipped_passes(self) -> None:
        html = H2X4 + '<figure data-fig="what"></figure><figure data-fig="need"></figure><p data-fig-skip="cast, resume struct branch"></p>'
        self.assertEqual(self.run_rule(html), [])

    def test_missing_roles_fail(self) -> None:
        html = H2X4 + '<figure data-fig="what"></figure><p data-fig-skip="need"></p>'
        self.assertEqual(self.run_rule(html), ["fig-role: 図が無い役がある: cast, resume, struct, branch"])


class MotionFigsTest(unittest.TestCase):
    def run_rule(self, figure: str) -> list[str]:
        root, sheet, _ = parse_page(f"<style>{MOVE_CSS}</style>{figure}")
        findings: list[str] = []
        check_motion_figs(root, sheet, findings)
        return findings

    def test_resume_with_moving_dot_passes(self) -> None:
        self.assertEqual(self.run_rule('<figure data-fig="resume"><span class="dot"></span></figure>'), [])

    def test_branch_without_motion_fails(self) -> None:
        self.assertEqual(
            self.run_rule('<figure data-fig="branch" class="dot"><div class="box">a</div></figure>'),
            ["motion-fig: branch の図に動く点が無い。動きは動く図で見せる"],
        )

    def test_other_roles_are_not_checked(self) -> None:
        self.assertEqual(self.run_rule('<figure data-fig="what"></figure>'), [])

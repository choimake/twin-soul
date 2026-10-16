"""rules_figures.py のテスト。実行: python3 -I -m unittest discover -s skills/tech-intro/scripts"""

from __future__ import annotations

import unittest

from rules_figures import (
    check_fig_roles,
    check_svg_label,
    check_svg_narrow,
    check_svg_text,
    font_px,
)
from testutil import find, parse, parse_page


class HelperTest(unittest.TestCase):
    def test_font_px_inherits_and_converts(self) -> None:
        root, sheet, _ = parse_page('<style>svg { font-size: 0.75rem }</style><svg><text>a</text></svg><p font-size="x">b</p>')
        self.assertEqual(font_px(find(root, "text"), sheet), 12)
        self.assertIsNone(font_px(find(root, "p"), sheet))
        bare, sheet, _ = parse_page("<span>a</span>")
        self.assertEqual(font_px(find(bare, "span"), sheet), 16.0)


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


class SvgLabelTest(unittest.TestCase):
    def run_rule(self, body: str, css: str = "") -> list[str]:
        root, sheet, _ = parse_page(f"<style>svg text {{ font-size: 12px; }} {css}</style><svg>{body}</svg>")
        findings: list[str] = []
        check_svg_label(root, sheet, findings)
        return findings

    def test_container_label_over_inner_box_fails(self) -> None:
        self.assertEqual(
            self.run_rule(
                '<g><rect x="0" y="0" width="200" height="60"/><text x="100" y="35" text-anchor="middle">Node A</text></g>'
                '<g><rect x="20" y="20" width="70" height="30"/></g><g><rect x="110" y="20" width="70" height="30"/></g>'
            ),
            ["svg-label: 「Node A」が箱と重なる。ラベルは箱の外に出し、入れ物の箱の名前は中の箱より上に置く"],
        )

    def test_container_label_above_inner_box_passes(self) -> None:
        self.assertEqual(self.run_rule(
            '<g><rect x="0" y="0" width="200" height="60"/><text x="100" y="14" text-anchor="middle">Node A</text></g>'
            '<g><rect x="20" y="20" width="70" height="30"/></g>'
        ), [])

    def test_label_past_view_box_fails(self) -> None:
        # 「宣言を送る」は x=40〜100。viewBox の右端は 90
        body = '<text x="40" y="20">宣言を送る</text>'
        root, sheet, _ = parse_page(f"<style>svg text {{ font-size: 12px; }}</style><svg viewBox=\"0 0 90 40\">{body}</svg>")
        findings: list[str] = []
        check_svg_label(root, sheet, findings)
        self.assertEqual(findings, ["svg-label: 「宣言を送る」が viewBox からはみ出て切れる。ラベルを内側に寄せるか、viewBox を広げる"])
        root, sheet, _ = parse_page(f"<style>svg text {{ font-size: 12px; }}</style><svg viewBox=\"0 0 110 40\">{body}</svg>")
        findings = []
        check_svg_label(root, sheet, findings)
        self.assertEqual(findings, [])

    def test_line_through_label_fails_even_with_halo(self) -> None:
        body = '<line x1="50" y1="0" x2="50" y2="100"/><text x="50" y="40" text-anchor="middle">送る</text>'
        expected = ["svg-label: 「送る」に線が重なるか 3px 以内に近い。縁取りで隠さず、ラベルを線から離す。"
                    "生存線をまたぐなら、ラベルを始点の隣の区間に収めるか、生存線の間隔を広げる"]
        self.assertEqual(self.run_rule(body), expected)
        self.assertEqual(self.run_rule(body, "text { paint-order: stroke; }"), expected)

    def test_line_just_beside_label_fails(self) -> None:
        # 「送る」は x=10〜34。線が 2px 右にある
        self.assertEqual(len(self.run_rule('<line x1="36" y1="0" x2="36" y2="100"/><text x="10" y="40">送る</text>')), 1)
        self.assertEqual(self.run_rule('<line x1="40" y1="0" x2="40" y2="100"/><text x="10" y="40">送る</text>'), [])

    def test_arrowhead_polygon_counts(self) -> None:
        self.assertEqual(len(self.run_rule('<polygon points="30,38 40,42 30,46"/><text x="10" y="40">送る</text>')), 1)

    def test_label_above_arrow_passes(self) -> None:
        self.assertEqual(self.run_rule(
            '<path d="M10 50 L200 50"/><text x="100" y="42" text-anchor="middle">① 送る</text>'), [])

    def test_overlapping_labels_fail(self) -> None:
        self.assertEqual(
            self.run_rule('<text x="10" y="20">送る</text><text x="20" y="24">受け取る</text>'),
            ["svg-label: 「送る」と「受け取る」が重なる。ラベルの位置をずらす"],
        )

    def test_marker_shapes_are_ignored(self) -> None:
        self.assertEqual(self.run_rule(
            '<defs><marker id="m"><path d="M0 0 L100 100"/></marker></defs><text x="10" y="40">送る</text>'), [])


class SvgNarrowTest(unittest.TestCase):
    def run_rule(self, view_box: str, css: str = "", attrs: str = "") -> list[str]:
        root, sheet, _ = parse_page(
            f'<style>svg text {{ font-size: 13px; }} {css}</style><svg {attrs} viewBox="{view_box}"><text x="1" y="20">送る</text></svg>'
        )
        findings: list[str] = []
        check_svg_narrow(root, sheet, findings)
        return findings

    def test_wide_svg_fails(self) -> None:
        self.assertEqual(
            self.run_rule("0 0 700 200"),
            ["svg-narrow: 幅 375px で図の文字が約 5.9px になる（viewBox の幅 700）。"
             "11px 以上になるよう、狭い幅用に箱を縦に並べた SVG を置き、@media で切り替える"],
        )

    def test_narrow_svg_passes(self) -> None:
        self.assertEqual(self.run_rule("0 0 370 600"), [])
        self.assertEqual(self.run_rule("0 0 200 100"), [])

    def test_svg_hidden_on_narrow_screen_is_skipped(self) -> None:
        self.assertEqual(self.run_rule("0 0 700 200", "@media (max-width: 600px) { .wide { display: none; } }", 'class="wide"'), [])

    def test_svg_hidden_everywhere_is_skipped(self) -> None:
        self.assertEqual(self.run_rule("0 0 700 200", ".wide { display: none; }", 'class="wide"'), [])


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
        self.assertEqual(self.run_rule(html), ["fig-role: 図が無い役がある: cast, resume, struct, branch。話題が無くて省くなら、data-fig-skip にその役を書く"])

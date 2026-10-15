"""rules_figures.py のテスト。実行: python3 -I -m unittest discover -s skills/tech-intro/scripts"""

from __future__ import annotations

import unittest

from rules_figures import (
    check_motion_stop,
    check_fig_roles,
    check_motion_figs,
    check_svg,
    check_svg_text,
    font_px,
)
from testutil import find, parse, parse_page


MOVE_CSS = """
.flow { stroke-dasharray: 1; stroke-dashoffset: 1; animation: draw 1s linear forwards; }
@keyframes draw { from { stroke-dashoffset: 1; } to { stroke-dashoffset: 0; } }
"""


class HelperTest(unittest.TestCase):
    def test_font_px_inherits_and_converts(self) -> None:
        root, sheet, _ = parse_page('<style>svg { font-size: 0.75rem }</style><svg><text>a</text></svg><p font-size="x">b</p>')
        self.assertEqual(font_px(find(root, "text"), sheet), 12)
        self.assertIsNone(font_px(find(root, "p"), sheet))
        bare, sheet, _ = parse_page("<span>a</span>")
        self.assertEqual(font_px(find(bare, "span"), sheet), 16.0)


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

    def test_step_button_without_animation_passes(self) -> None:
        for role in ("resume", "branch"):
            with self.subTest(role=role):
                self.assertEqual(self.run_rule(
                    f'<figure data-fig="{role}"><button type="button" data-step>1本ずつ見る</button></figure>'), [])

    def test_without_step_button_fails_even_with_animation(self) -> None:
        for role in ("resume", "branch"):
            with self.subTest(role=role):
                self.assertEqual(self.run_rule(
                    f'<figure data-fig="{role}"><svg><path class="flow"/></svg><button>1本ずつ見る</button><span data-step></span></figure>'),
                    [f"motion-fig: {role} の図に button[data-step] が無い。図の中に「1本ずつ見る」ボタンを置く"],
                )

    def test_button_outside_figure_fails(self) -> None:
        self.assertTrue(self.run_rule(
            '<figure data-fig="resume"></figure><button data-step>1本ずつ見る</button>'))

    def test_other_roles_are_not_checked(self) -> None:
        self.assertEqual(self.run_rule('<figure data-fig="what"></figure>'), [])


class MotionStopTest(unittest.TestCase):
    def run_rule(self, css: str, style: str = "") -> list[str]:
        root, sheet, _ = parse_page(f'<style>{css}</style><path class="flow" style="{style}"/>')
        findings: list[str] = []
        check_motion_stop(root, sheet, findings)
        return findings

    def test_infinite_is_reported(self) -> None:
        for declaration in ("animation: draw 1s infinite", "animation: draw 1s infinite!important",
                            "animation: draw var(--duration) infinite", "animation-iteration-count: INFINITE"):
            with self.subTest(declaration=declaration):
                self.assertEqual(self.run_rule(f".flow {{ {declaration}; }}"), [
                    "motion-stop: infinite は使わない。アニメーションは繰り返さない"])

    def test_inline_infinite_is_reported(self) -> None:
        for declaration in ("animation: draw 1s infinite", "animation-iteration-count: infinite"):
            with self.subTest(declaration=declaration):
                self.assertTrue(self.run_rule("", declaration))

    def test_media_infinite_is_reported(self) -> None:
        for condition in ("(max-width: 600px)", "(prefers-reduced-motion: reduce)"):
            with self.subTest(condition=condition):
                self.assertTrue(self.run_rule(
                    f"@media {condition} {{ .flow {{ animation: draw 1s infinite; }} }}"))

    def test_finite_line_draw_passes(self) -> None:
        for declaration in ("animation: draw .6s linear forwards",
                            "animation: draw .6s calc(var(--step) * 0.7s) forwards",
                            "animation-iteration-count: 1"):
            with self.subTest(declaration=declaration):
                self.assertEqual(self.run_rule(f".flow {{ {declaration}; }}"), [])
                self.assertEqual(self.run_rule("", declaration), [])

    def test_unrelated_infinite_text_is_ignored(self) -> None:
        self.assertEqual(self.run_rule(
            '.flow { animation: infinite-draw 1s forwards; content: "infinite"; /* animation: draw 1s infinite; */ }'), [])

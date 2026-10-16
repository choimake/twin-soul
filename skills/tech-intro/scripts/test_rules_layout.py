"""rules_layout.py のテスト。実行: python3 -I -m unittest discover -s skills/tech-intro/scripts"""

from __future__ import annotations

import unittest

from css import parse_sheet
from rules_layout import check_external, check_motion, check_responsive, check_spacing, check_toc
from testutil import parse_page


def page(body: str, css: str = "", columns: str = "minmax(0, 1fr) 220px") -> str:
    return (
        f"<style>.page {{ display: grid; grid-template-columns: {columns}; }} {css}</style>"
        f'<div class="page">{body}</div>'
    )


ARTICLE = "<article><h2>1. なぜ要るか</h2><h2>構造</h2></article>"
TOC = '<aside class="toc"><a>なぜ要るか</a><a>構造</a></aside>'


class ExternalTest(unittest.TestCase):
    def run_rule(self, html: str) -> list[str]:
        findings: list[str] = []
        check_external(html, findings)
        return findings

    def test_inline_only_passes(self) -> None:
        self.assertEqual(self.run_rule("<script>run()</script><style>.a{}</style>"), [])

    def test_external_script_stylesheet_and_cdn(self) -> None:
        findings = self.run_rule(
            '<script src="https://cdn.jsdelivr.net/x.js"></script><link rel="stylesheet" href="a.css">'
        )
        self.assertEqual(
            findings,
            [
                "external: 外部 script がある。確認クイズの採点もファイル内に書く",
                "external: 外部 stylesheet がある。CSS はファイル内に書く",
                "external: CDN がある (cdn.jsdelivr.net)",
            ],
        )

    def test_mermaid_class(self) -> None:
        self.assertEqual(self.run_rule('<pre class="mermaid">graph</pre>'), ["external: Mermaid がある"])


class MotionTest(unittest.TestCase):
    def run_rule(self, css: str) -> list[str]:
        findings: list[str] = []
        check_motion(parse_sheet(css), findings)
        return findings

    def test_no_animation_passes(self) -> None:
        self.assertEqual(self.run_rule(".a { color: red }"), [])

    def test_animation_stopped_by_reduced_motion_passes(self) -> None:
        css = ".dot { animation: hop 1s } @media (prefers-reduced-motion: reduce) { .dot { animation: none } }"
        self.assertEqual(self.run_rule(css), [])

    def test_animation_without_reduced_motion_fails(self) -> None:
        self.assertEqual(
            self.run_rule(".dot { animation: hop 1s }"),
            ["motion: 動きがあるのに prefers-reduced-motion: reduce が無い"],
        )

    def test_reduced_motion_that_does_not_stop_fails(self) -> None:
        css = ".dot { animation: hop 1s } @media (prefers-reduced-motion: reduce) { .dot { opacity: .5 } }"
        self.assertEqual(self.run_rule(css), ["motion: prefers-reduced-motion: reduce でアニメーションが止まらない"])


class TocTest(unittest.TestCase):
    def run_rule(self, html: str) -> list[str]:
        root, sheet, _ = parse_page(html)
        findings: list[str] = []
        check_toc(root, sheet, findings)
        return findings

    def test_matching_toc_on_right_passes(self) -> None:
        self.assertEqual(self.run_rule(page(ARTICLE + TOC)), [])

    def test_no_headings_and_no_toc_passes(self) -> None:
        self.assertEqual(self.run_rule("<p>x</p>"), [])

    def test_missing_toc_fails(self) -> None:
        self.assertEqual(self.run_rule(page(ARTICLE)), ["toc-text: 目次が無い"])

    def test_aria_label_toc_is_found(self) -> None:
        toc = '<nav aria-label="目次"><a>なぜ要るか</a><a>構造</a></nav>'
        self.assertEqual(self.run_rule(page(ARTICLE + toc)), [])

    def test_toc_text_mismatch_fails(self) -> None:
        toc = '<aside class="toc"><a>なぜ要るか</a></aside>'
        self.assertEqual(
            self.run_rule(page(ARTICLE + toc)),
            ["toc-text: 目次と見出しが違う。目次=['なぜ要るか'] 見出し=['なぜ要るか', '構造']"],
        )

    def test_toc_first_fails(self) -> None:
        self.assertEqual(self.run_rule(page(TOC + ARTICLE)), ["toc-side: 目次が右の列に無い"])

    def test_toc_first_placed_on_last_column_passes(self) -> None:
        self.assertEqual(self.run_rule(page(TOC + ARTICLE, ".toc { grid-column: 2; }")), [])

    def test_parent_not_grid_fails(self) -> None:
        self.assertEqual(
            self.run_rule(f"<div>{ARTICLE}{TOC}</div>"), ["toc-side: 目次の親が横並びの grid でない"]
        )

    def test_single_column_fails(self) -> None:
        self.assertEqual(
            self.run_rule(page(ARTICLE + TOC, columns="1fr")), ["toc-side: 目次を右に分ける列が無い"]
        )

    def test_negative_order_on_desktop_fails(self) -> None:
        self.assertEqual(
            self.run_rule(page(ARTICLE + TOC, ".toc { order: -1; }")),
            ["toc-side: デスクトップで目次が本文より前に出る"],
        )

    def test_order_inside_narrow_media_is_ignored(self) -> None:
        css = "@media (max-width: 820px) { .toc { order: -1; } }"
        self.assertEqual(self.run_rule(page(ARTICLE + TOC, css)), [])


RESPONSIVE_OK = """
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body { overflow-wrap: anywhere; }
.scroll { overflow-x: auto; }
@media (max-width: 600px) { .a { display: block; } }
</style>
<body>
<svg viewBox="0 0 10 10"></svg>
<div class="scroll"><table><tr><td>a</td></tr></table></div>
<p><code>step.run()</code></p>
<pre><code>long.code()</code></pre>
</body>
"""


class ResponsiveTest(unittest.TestCase):
    def run_rule(self, html: str) -> list[str]:
        root, sheet, css = parse_page(html)
        findings: list[str] = []
        check_responsive(root, sheet, css, findings)
        return findings

    def test_fluid_page_passes(self) -> None:
        self.assertEqual(self.run_rule(RESPONSIVE_OK), [])

    def test_missing_viewport_and_narrow_media(self) -> None:
        html = RESPONSIVE_OK.replace("width=device-width", "width=1024").replace("max-width", "min-width")
        self.assertEqual(
            self.run_rule(html),
            [
                "responsive: meta viewport（width=device-width）が無い",
                "responsive: 狭い幅の @media (max-width) が無い",
            ],
        )

    def test_svg_without_viewbox_and_fixed_width(self) -> None:
        html = RESPONSIVE_OK.replace('<svg viewBox="0 0 10 10">', '<svg width="800">')
        self.assertEqual(
            self.run_rule(html),
            [
                "responsive: viewBox の無い svg がある。幅に合わせて縮まない",
                "responsive: svg の幅が 800px 固定。CSS で width か max-width を 100% にする",
            ],
        )

    def test_fixed_width_svg_with_fluid_css_passes(self) -> None:
        html = RESPONSIVE_OK.replace('<svg viewBox="0 0 10 10">', '<svg viewBox="0 0 800 10" width="800">')
        html = html.replace("</style>", "svg { max-width: 100%; }</style>")
        self.assertEqual(self.run_rule(html), [])

    def test_scrolling_figure_fails(self) -> None:
        html = RESPONSIVE_OK.replace("</body>", '<figure style="overflow-x: scroll"></figure></body>')
        self.assertEqual(
            self.run_rule(html), ["responsive: 図が横スクロールする。狭い幅では縮めるか、縦に並べ替える"]
        )

    def test_table_outside_scroll_box_fails(self) -> None:
        html = RESPONSIVE_OK.replace('class="scroll"', "")
        self.assertEqual(
            self.run_rule(html), ["responsive: 表が横スクロールの枠に入っていない。overflow-x: auto の要素で包む"]
        )

    def test_inline_code_without_wrap_fails(self) -> None:
        html = RESPONSIVE_OK.replace("body { overflow-wrap: anywhere; }", "")
        self.assertEqual(
            self.run_rule(html),
            ["responsive: 本文中のコードが折り返さない。overflow-wrap: anywhere を本文か code に付ける"],
        )

    def test_large_min_width_fails(self) -> None:
        html = RESPONSIVE_OK.replace("</style>", ".wide, .w2 { min-width: 361px; } .ok { min-width: 360px; }</style>")
        self.assertEqual(
            self.run_rule(html), ["responsive: min-width が 361px（.wide, .w2）。狭い画面からはみ出す"]
        )


class SpacingTest(unittest.TestCase):
    GAP = "<style>section { display: flex; flex-direction: column; gap: 24px; }</style>"

    def run_rule(self, html: str) -> list[str]:
        root, sheet, _ = parse_page(html)
        findings: list[str] = []
        check_spacing(root, sheet, findings)
        return findings

    def test_gap_and_one_core_pass(self) -> None:
        self.assertEqual(self.run_rule(
            self.GAP + '<section><p class="core">差を埋める。</p><figure data-fig="resume"></figure></section>'), [])

    def test_section_without_gap_fails(self) -> None:
        self.assertEqual(
            self.run_rule('<section><p class="core">差を埋める。</p><figure data-fig="resume"></figure></section>'),
            ["spacing: 章（section）の塊を gap で空けていない。「HTML」の余白の CSS を使う"],
        )

    def test_missing_core_fails(self) -> None:
        self.assertEqual(
            self.run_rule(self.GAP + '<section><p>差を埋める。</p><figure data-fig="resume"></figure></section>'),
            ["spacing: resume の図の章に p.core が 0 個ある。核心の一文を1つ置く"],
        )

    def test_core_label_text_fails(self) -> None:
        self.assertEqual(
            self.run_rule(self.GAP + '<section><p class="core">核心の一文: 差を埋める。</p><figure data-fig="resume"></figure></section>'),
            ["spacing: 「核心の一文」という文字を書いている。p.core に文だけを書く"],
        )

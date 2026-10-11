"""htmldoc.py のテスト。実行: python3 -I -m unittest discover -s skills/tech-intro/scripts"""

from __future__ import annotations

import unittest

from htmldoc import (
    Text,
    ancestors,
    contains,
    norm_heading,
    visible_text,
    visible_text_raw,
    walk,
)
from testutil import find, parse


class DocParserTest(unittest.TestCase):
    def test_void_tag_does_not_take_children(self) -> None:
        p = find(parse("<p>a<br>b</p>"), "p")
        self.assertEqual([type(child).__name__ for child in p.children], ["Text", "Node", "Text"])
        self.assertEqual(find(p, "br").children, [])

    def test_svg_shape_without_slash_is_void(self) -> None:
        svg = find(parse('<svg><rect x="1"><text>a</text></svg>'), "svg")
        self.assertEqual([child.tag for child in svg.elements()], ["rect", "text"])

    def test_end_tag_closes_unclosed_children(self) -> None:
        root = parse("<div><p>a<span>b</div><p>c</p>")
        self.assertEqual([child.tag for child in root.elements()], ["div", "p"])

    def test_unmatched_end_tag_is_ignored(self) -> None:
        root = parse("<div>a</span>b</div>")
        self.assertEqual(visible_text(find(root, "div")), "ab")

    def test_attribute_without_value_becomes_empty_string(self) -> None:
        details = find(parse('<details open data-scope class="a b">x</details>'), "details")
        self.assertEqual(details.attrs["open"], "")
        self.assertEqual(details.classes, {"a", "b"})

    def test_char_refs_are_converted(self) -> None:
        self.assertEqual(visible_text(parse("<p>a&amp;b</p>")), "a&b")


class WalkTest(unittest.TestCase):
    def test_walk_is_preorder_and_skips_document(self) -> None:
        root = parse("<div><p><b>x</b></p><i>y</i></div>")
        self.assertEqual([node.tag for node in walk(root)], ["div", "p", "b", "i"])

    def test_walk_from_element_includes_itself(self) -> None:
        div = find(parse("<div><p>x</p></div>"), "div")
        self.assertEqual([node.tag for node in walk(div)], ["div", "p"])


class TextTest(unittest.TestCase):
    def test_visible_text_skips_style_and_script(self) -> None:
        root = parse("<p>前<style>.x{}</style>中<script>c()</script>後</p>")
        self.assertEqual(visible_text(root), "前中後")

    def test_visible_text_raw_keeps_style_and_script(self) -> None:
        root = parse("<p>a<style>.x{}</style>b<script>c()</script></p>")
        self.assertEqual(visible_text_raw(root), "a.x{}bc()")

    def test_text_node_holds_data(self) -> None:
        self.assertEqual(Text("x").data, "x")


class TreeTest(unittest.TestCase):
    def test_contains_self_and_descendant_only(self) -> None:
        root = parse("<div><p><b>x</b></p></div><i>y</i>")
        div, b, i = find(root, "div"), find(root, "b"), find(root, "i")
        self.assertTrue(contains(div, div))
        self.assertTrue(contains(div, b))
        self.assertFalse(contains(div, i))
        self.assertFalse(contains(b, div))

    def test_ancestors_stop_before_document(self) -> None:
        b = find(parse("<div><p><b>x</b></p></div>"), "b")
        self.assertEqual([node.tag for node in ancestors(b)], ["p", "div"])


class NormHeadingTest(unittest.TestCase):
    def test_strips_chapter_number_and_collapses_spaces(self) -> None:
        self.assertEqual(norm_heading("  1.  なぜ\n 要るか "), "なぜ 要るか")

    def test_strips_full_width_number(self) -> None:
        self.assertEqual(norm_heading("１２．構造"), "構造")
        self.assertEqual(norm_heading("3、構造"), "構造")

    def test_keeps_number_without_separator(self) -> None:
        self.assertEqual(norm_heading("3 つの部品"), "3 つの部品")

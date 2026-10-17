"""css.py のテスト。実行: python3 -I -m unittest discover -s skills/tech-intro/scripts"""

from __future__ import annotations

import unittest

from css import (
    first_token,
    matches,
    parse_blocks,
    parse_decls,
    parse_sheet,
    px_value,
    split_csv,
    strip_comments,
    style_text,
    styles_for,
)
from testutil import find, parse


class ParseTest(unittest.TestCase):
    def test_strip_comments_across_lines(self) -> None:
        self.assertEqual(strip_comments("a/* x\n y */b/**/c"), "abc")

    def test_parse_blocks_keeps_nested_body(self) -> None:
        blocks = parse_blocks(" .a { x: 1 } @media (min-width: 1px) { .b { y: 2 } } ")
        self.assertEqual(blocks, [(".a", " x: 1 "), ("@media (min-width: 1px)", " .b { y: 2 } ")])

    def test_parse_blocks_drops_prelude_without_body(self) -> None:
        self.assertEqual(parse_blocks(".a { x: 1 } .b"), [(".a", " x: 1 ")])

    def test_split_csv_ignores_commas_in_parens(self) -> None:
        self.assertEqual(split_csv("a, :is(b, c) , ,d"), ["a", ":is(b, c)", "d"])

    def test_parse_decls_lowercases_property_and_keeps_colon_in_value(self) -> None:
        self.assertEqual(
            parse_decls(" Color: Red ; background: url(a:b); junk "),
            {"color": "Red", "background": "url(a:b)"},
        )

    def test_parse_sheet_sorts_rules_and_narrow_media(self) -> None:
        sheet = parse_sheet(
            """
            /* .gone { x: 1 } */
            .a, .b { color: red; }
            @media (max-width: 600px) { .narrow { color: blue; } }
            @media (min-width: 900px) { .wide { color: green; } }
            @font-face { font-family: x; }
            """
        )
        self.assertEqual([rule.selectors for rule in sheet.rules], [[".a", ".b"], [".wide"]])
        self.assertEqual([rule.selectors for rule in sheet.narrow_rules], [[".narrow"]])

    def test_style_text_joins_style_elements(self) -> None:
        root = parse("<style>.a{}</style><p>x</p><style>.b{}</style>")
        self.assertEqual(style_text(root), ".a{}\n.b{}")


class MatchesTest(unittest.TestCase):
    def setUp(self) -> None:
        self.root = parse('<div class="row" id="r"><p class="box"><span class="dot">x</span></p></div>')
        self.span = find(self.root, "span")
        self.p = find(self.root, "p")

    def test_descendant_and_child(self) -> None:
        self.assertTrue(matches(self.span, ".row .dot"))
        self.assertTrue(matches(self.span, "p > span.dot"))
        self.assertFalse(matches(self.span, ".row > .dot"))

    def test_tag_class_and_id(self) -> None:
        self.assertTrue(matches(self.p, "div#r > p.box"))
        self.assertFalse(matches(self.p, "div#other p"))
        self.assertFalse(matches(self.p, "p.box.missing"))

    def test_attribute(self) -> None:
        self.assertTrue(matches(self.p, "div[id=r] p"))
        self.assertTrue(matches(self.p, 'div[id="r"] > p[class]'))
        self.assertFalse(matches(self.p, "div[id=other] p"))
        self.assertFalse(matches(self.p, "p[data-fig]"))

    def test_pseudo_class_is_ignored_and_pseudo_element_never_matches(self) -> None:
        self.assertTrue(matches(self.p, ".box:hover"))
        self.assertTrue(matches(self.p, ".box:not(.x)"))
        self.assertFalse(matches(self.p, ".box::before"))
        self.assertFalse(matches(self.p, ".row + .box"))

    def test_universal_and_unknown_compound(self) -> None:
        self.assertTrue(matches(self.p, "*"))
        self.assertFalse(matches(self.p, "p[data-x]"))

    def test_document_never_matches(self) -> None:
        self.assertFalse(matches(self.root, "*"))

    def test_styles_for_later_rule_and_inline_style_win(self) -> None:
        root = parse('<p class="box" style="color: blue">x</p>')
        sheet = parse_sheet(".box { color: red; width: 1px } p { width: 2px }")
        self.assertEqual(styles_for(find(root, "p"), sheet.rules), {"color": "blue", "width": "2px"})


class ValueTest(unittest.TestCase):
    def test_first_token(self) -> None:
        self.assertEqual(first_token("absolute !important"), "absolute")
        self.assertEqual(first_token("  ", "static"), "static")

    def test_px_value(self) -> None:
        self.assertEqual(px_value(" 12.5px "), 12.5)
        self.assertIsNone(px_value("12em"))
        self.assertIsNone(px_value("-3px"))

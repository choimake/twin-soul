"""hedges.py のテスト。実行: python3 -I -m unittest discover -s skills/tech-intro/scripts"""

from __future__ import annotations

import unittest

from hedges import hedged_quotes, is_quote_leaf, source_text
from htmldoc import walk
from testutil import find, parse


def source(body: str, heading: str = "なぜ要るか") -> str:
    return f"<h2>{heading}</h2><details><summary>出典</summary>{body}</details>"


class QuoteLeafTest(unittest.TestCase):
    def test_innermost_quote_element_is_leaf(self) -> None:
        root = parse("<ul><li><p>a</p></li><li>b</li></ul>")
        self.assertEqual([node.tag for node in walk(root) if is_quote_leaf(node)], ["p", "li"])

    def test_other_tags_are_not_leaves(self) -> None:
        self.assertFalse(is_quote_leaf(find(parse("<div>a</div>"), "div")))


class SourceTextTest(unittest.TestCase):
    def test_drops_links_and_splits_q(self) -> None:
        li = find(parse('<li><a href="#">29.6 Conflicts</a> 同ページ: <q>WAL may be kept.</q>（補足）</li>'), "li")
        self.assertEqual(source_text(li), " 同ページ: \nWAL may be kept.\n（補足）")


class HedgedQuotesTest(unittest.TestCase):
    def test_sentences_with_strength_words_are_listed_with_heading(self) -> None:
        html = source("<p>「Normally, the slot is created. It is removed. A key (usually a primary key) is used.」</p>")
        self.assertEqual(
            hedged_quotes(html),
            [("なぜ要るか", "Normally, the slot is created."), ("なぜ要るか", "A key (usually a primary key) is used.")],
        )

    def test_each_strength_word_is_found(self) -> None:
        words = ["normally", "typically", "usually", "may", "might", "could", "can", "in many cases", "should", "must"]
        for word in words:
            with self.subTest(word=word):
                self.assertEqual(len(hedged_quotes(source(f"<p>It {word} run.</p>"))), 1)

    def test_can_only_and_partial_words_are_not_listed(self) -> None:
        html = source("<p>It can only be set at start. Maybe later. The mayor shoulders it.</p>")
        self.assertEqual(hedged_quotes(html), [])

    def test_abbreviations_and_ellipsis_do_not_split(self) -> None:
        html = source("<p>「The slot ... should be dropped, e.g. by hand, i.e. with SQL.」</p>")
        self.assertEqual(hedged_quotes(html), [("なぜ要るか", "The slot ... should be dropped, e.g. by hand, i.e. with SQL.")])

    def test_leading_punctuation_and_ellipsis_are_trimmed(self) -> None:
        html = source(
            "<ul><li>— Normally, it runs.</li><li>[...] It may stop.</li><li>「… It can wait.」</li></ul>"
        )
        self.assertEqual(
            [sentence for _, sentence in hedged_quotes(html)],
            ["Normally, it runs.", "It may stop.", "It can wait."],
        )

    def test_scope_note_and_body_text_are_not_sources(self) -> None:
        html = (
            "<h2>a</h2><p>It may run.</p>"
            "<details data-scope><summary>対象</summary><p>It may run.</p></details>"
        )
        self.assertEqual(hedged_quotes(html), [])

    def test_nested_details_are_read_once(self) -> None:
        html = source("<p>It may run.</p><details><summary>内</summary><p>It should stop.</p></details>")
        self.assertEqual(
            hedged_quotes(html), [("なぜ要るか", "It may run."), ("なぜ要るか", "It should stop.")]
        )

    def test_without_quote_elements_reads_children_except_summary(self) -> None:
        html = source("<div>It must run.</div>").replace("<summary>出典</summary>", "<summary>It may</summary>")
        self.assertEqual(hedged_quotes(html), [("なぜ要るか", "It must run.")])

    def test_heading_follows_latest_chapter(self) -> None:
        html = source("<p>It may run.</p>", "1. 一") + source("<p>It should run.</p>", "2. 二")
        self.assertEqual(hedged_quotes(html), [("一", "It may run."), ("二", "It should run.")])

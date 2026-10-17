"""rules_content.py のテスト。実行: python3 -I -m unittest discover -s skills/tech-intro/scripts"""

from __future__ import annotations

import unittest
from collections.abc import Callable

from htmldoc import Node
from rules_content import (
    chapter_prose,
    check_agent_skills,
    check_banned,
    check_endings,
    check_goals,
    check_scope,
    check_terms,
    check_volume,
)
from testutil import parse


# どの本文ルールにも指摘されない、4章と末尾の3章を持つページ
PAGE = """
<ol data-goals><li>何か</li><li>何ができるか</li></ol>
<details data-scope><summary>対象と版</summary><p>確認日 2026-10-07。</p></details>
<h2>1. なぜ要るか</h2><p><dfn>node</dfn> は処理の単位である。</p>
<h2>2. 登場人物</h2><p>送る側と受け取る側がいる。</p>
<h2>3. 構造</h2><pre><code>step.run()</code></pre>
<section data-agent-skills="無い"><h2>4. 公式 skill</h2><a href="https://example.com/">確かめた場所</a></section>
<h2>チェックリスト</h2>
<h2>確かめられなかったこと</h2>
<h2>確認クイズ</h2>
"""


def run_rule(rule: Callable[[Node, list[str]], None], html: str) -> list[str]:
    findings: list[str] = []
    rule(parse(html), findings)
    return findings


class PageTest(unittest.TestCase):
    def test_base_page_passes_every_rule(self) -> None:
        for rule in (
            check_banned,
            check_goals,
            check_scope,
            check_volume,
            check_endings,
            check_terms,
            check_agent_skills,
        ):
            with self.subTest(rule=rule.__name__):
                self.assertEqual(run_rule(rule, PAGE), [])

    def test_short_page_skips_chapter_rules(self) -> None:
        short = "<h2>a</h2><h2>b</h2><h2>c</h2><pre>x</pre>"
        for rule in (check_goals, check_scope, check_volume, check_endings, check_terms, check_agent_skills):
            with self.subTest(rule=rule.__name__):
                self.assertEqual(run_rule(rule, short), [])


class BannedTest(unittest.TestCase):
    def test_banned_phrases(self) -> None:
        self.assertEqual(
            run_rule(check_banned, "<p>公式の正本を見る。</p>"),
            ["banned: 「正本」がある"],
        )

    def test_phrase_in_script_is_ignored(self) -> None:
        self.assertEqual(run_rule(check_banned, "<p>エラーにならずに飛ばされる。</p><script>// 正本</script>"), [])


class GoalsTest(unittest.TestCase):
    def test_missing_goals(self) -> None:
        html = PAGE.replace("data-goals", "")
        self.assertEqual(run_rule(check_goals, html), ["goals: 冒頭に、この入門でわかることの一覧（data-goals）が無い"])

    def test_one_goal_is_too_few(self) -> None:
        html = PAGE.replace("<li>何ができるか</li>", "<li> </li>")
        self.assertEqual(run_rule(check_goals, html), ["goals: この入門でわかることの一覧が2項目に満たない"])

    def test_goals_after_first_chapter(self) -> None:
        goals = "<ol data-goals><li>何か</li><li>何ができるか</li></ol>"
        html = PAGE.replace(goals, "").replace("<h2>2. 登場人物</h2>", goals + "<h2>2. 登場人物</h2>")
        self.assertEqual(run_rule(check_goals, html), ["goals: この入門でわかることの一覧が最初の章より後にある"])


class ScopeTest(unittest.TestCase):
    def test_missing_scope(self) -> None:
        html = PAGE.replace("data-scope", "")
        self.assertEqual(
            run_rule(check_scope, html), ["scope: 冒頭に、対象・版・確認日・扱わないものの注記（data-scope）が無い"]
        )

    def test_scope_after_first_chapter(self) -> None:
        scope = "<details data-scope><summary>対象と版</summary><p>確認日 2026-10-07。</p></details>"
        html = PAGE.replace(scope, "") + scope
        self.assertEqual(run_rule(check_scope, html), ["scope: 対象と版の注記が最初の章より後にある"])


class ChapterProseTest(unittest.TestCase):
    def test_counts_prose_and_terms_per_chapter(self) -> None:
        html = (
            "<p>前置き</p><h2>1. 一</h2><p>あい う</p><figure>図の文字</figure><div data-quiz>問</div>"
            "<h2>二</h2><p><dfn>a</dfn>と<dfn>b</dfn></p><details>出典</details>"
        )
        self.assertEqual(chapter_prose(parse(html)), [("一", 3, 0), ("二", 3, 2)])


class VolumeTest(unittest.TestCase):
    def test_too_many_goals(self) -> None:
        html = PAGE.replace("<li>何か</li>", "<li>一</li>" * 5)
        self.assertEqual(run_rule(check_volume, html), ["volume: 要点が 6 個。5 個までに絞る"])

    def test_too_many_chapters(self) -> None:
        html = PAGE.replace("<h2>2. 登場人物</h2>", "<h2>追加</h2>" * 10)
        self.assertEqual(run_rule(check_volume, html), ["volume: 章が 13 個。12 個までにまとめる"])

    def test_long_heading_and_chapter(self) -> None:
        html = PAGE.replace("2. 登場人物", "2. " + "長" * 26).replace("送る側と受け取る側がいる。", "あ" * 601)
        self.assertEqual(
            run_rule(check_volume, html),
            [
                "volume: 見出しが 26 字（長長長長長長長長長長長長…）。25 字までにする",
                "volume: 章の文章が 601 字（長長長長長長長長長長長長…）。600 字までにする",
            ],
        )

    def test_total_prose(self) -> None:
        html = PAGE.replace("<h2>2. 登場人物</h2>", ("<h2>追加</h2><p>" + "あ" * 580 + "</p>") * 7)
        self.assertEqual(run_rule(check_volume, html), ["volume: 文章が合計 4093 字。4000 字までに削る"])

    def test_end_chapters_are_not_counted(self) -> None:
        html = PAGE.replace("<h2>確認クイズ</h2>", "<h2>確認クイズ</h2><p>" + "あ" * 700 + "</p>")
        self.assertEqual(run_rule(check_volume, html), [])


class EndingsTest(unittest.TestCase):
    def test_missing_end_chapter(self) -> None:
        html = PAGE.replace("<h2>確かめられなかったこと</h2>", "")
        self.assertEqual(run_rule(check_endings, html), ["endings: 「確かめられなかったこと」の章が無い"])

    def test_end_chapter_as_h3(self) -> None:
        html = PAGE.replace("<h2>確認クイズ</h2>", "<h3>確認クイズ</h3>")
        self.assertEqual(
            run_rule(check_endings, html),
            ["endings: 「確認クイズ」が章（h2）になっていない。目次から見つけられるよう h2 にする"],
        )


class TermsTest(unittest.TestCase):
    def test_no_dfn(self) -> None:
        html = PAGE.replace("<dfn>node</dfn>", "node")
        self.assertEqual(
            run_rule(check_terms, html), ["terms: 用語の定義に dfn が無い。初出で定義する語を dfn で囲む"]
        )

    def test_too_many_terms_in_one_chapter(self) -> None:
        html = PAGE.replace("<dfn>node</dfn>", "<dfn>a</dfn><dfn>b</dfn><dfn>c</dfn><dfn>d</dfn>")
        self.assertEqual(
            run_rule(check_terms, html),
            ["terms: 1章で 4 語を定義している（なぜ要るか…）。3 語までにし、残りは要る章で出す"],
        )


class AgentSkillsTest(unittest.TestCase):
    def test_missing_chapter(self) -> None:
        html = PAGE.replace(' data-agent-skills="無い"', "")
        self.assertEqual(
            run_rule(check_agent_skills, html),
            ["agent-skills: 公式 skill の章（data-agent-skills）が無い。有無は必ず章で書く"],
        )

    def test_bad_state_and_no_link(self) -> None:
        html = PAGE.replace('data-agent-skills="無い"', 'data-agent-skills="たぶん"').replace(
            "https://example.com/", "http://example.com/"
        )
        self.assertEqual(
            run_rule(check_agent_skills, html),
            [
                "agent-skills: data-agent-skills は ある / 無い / 未確認 のどれか（今は「たぶん」）",
                "agent-skills: 公式 skill の章に、確かめた場所の公式リンクが無い",
            ],
        )

    def test_attribute_not_on_chapter(self) -> None:
        html = PAGE.replace(' data-agent-skills="無い"', "").replace(
            '<a href="https://example.com/">', '<a data-agent-skills="ある" href="https://example.com/">'
        )
        self.assertEqual(
            run_rule(check_agent_skills, html),
            ["agent-skills: data-agent-skills は章（h2 か h2 を含む要素）に付ける"],
        )

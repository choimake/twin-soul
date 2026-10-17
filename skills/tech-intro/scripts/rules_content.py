"""本文のルール（禁止語、goals、scope、量、用語、末尾の章、公式 skill）。"""

from __future__ import annotations

import re

from htmldoc import Node, Text, norm_heading, visible_text, walk


def check_banned(root: Node, findings: list[str]) -> None:
    if "正本" in visible_text(root):
        findings.append("banned: 「正本」がある")


def check_goals(root: Node, findings: list[str]) -> None:
    nodes = list(walk(root))
    headings = [node for node in nodes if node.tag == "h2"]
    if len(headings) < 4:
        return
    first_h2 = nodes.index(headings[0])
    for index, node in enumerate(nodes):
        if "data-goals" not in node.attrs:
            continue
        items = [child for child in walk(node) if child.tag == "li" and visible_text(child).strip()]
        if len(items) < 2:
            findings.append("goals: この入門でわかることの一覧が2項目に満たない")
        elif index > first_h2:
            findings.append("goals: この入門でわかることの一覧が最初の章より後にある")
        return
    findings.append("goals: 冒頭に、この入門でわかることの一覧（data-goals）が無い")


def check_scope(root: Node, findings: list[str]) -> None:
    nodes = list(walk(root))
    headings = [node for node in nodes if node.tag == "h2"]
    if len(headings) < 4:
        return
    marked = [node for node in nodes if "data-scope" in node.attrs]
    if not marked:
        findings.append("scope: 冒頭に、対象・版・確認日・扱わないものの注記（data-scope）が無い")
        return
    if nodes.index(marked[0]) > nodes.index(headings[0]):
        findings.append("scope: 対象と版の注記が最初の章より後にある")


PROSE_SKIP_TAGS = {"figure", "pre", "table", "details", "aside", "nav", "script", "style", "svg", "form", "fieldset"}
PROSE_SKIP_ATTRS = ("data-quiz", "data-goals")


def chapter_prose(root: Node) -> list[tuple[str, int, int]]:
    chapters: list[list] = []

    def visit(node: Node, counting: bool) -> None:
        for child in node.children:
            if isinstance(child, Text):
                if chapters and counting:
                    chapters[-1][1] += len(re.sub(r"\s+", "", child.data))
                continue
            if child.tag == "h2":
                chapters.append([norm_heading(visible_text(child)), 0, 0])
                continue
            if child.tag == "dfn" and chapters:
                chapters[-1][2] += 1
            skip = child.tag in PROSE_SKIP_TAGS or any(attr in child.attrs for attr in PROSE_SKIP_ATTRS)
            visit(child, counting and not skip)

    visit(root, True)
    return [(title, count, terms) for title, count, terms in chapters]


END_CHAPTERS = ("チェックリスト", "確かめられなかったこと", "確認クイズ")
MAX_TERMS = 3


def is_end_chapter(title: str) -> bool:
    return any(phrase in title for phrase in END_CHAPTERS)


def check_endings(root: Node, findings: list[str]) -> None:
    chapters = chapter_prose(root)
    if len(chapters) < 4:
        return
    titles = [title for title, _, _ in chapters]
    minor = [
        norm_heading(visible_text(node)) for node in walk(root) if node.tag in {"h3", "h4", "h5", "h6"}
    ]
    for phrase in END_CHAPTERS:
        if any(phrase in title for title in titles):
            continue
        if any(phrase in title for title in minor):
            findings.append(f"endings: 「{phrase}」が章（h2）になっていない。目次から見つけられるよう h2 にする")
        else:
            findings.append(f"endings: 「{phrase}」の章が無い")


def check_terms(root: Node, findings: list[str]) -> None:
    chapters = chapter_prose(root)
    if len(chapters) < 4:
        return
    if not any(terms for _, _, terms in chapters):
        findings.append("terms: 用語の定義に dfn が無い。初出で定義する語を dfn で囲む")
        return
    for title, _, terms in chapters:
        if terms > MAX_TERMS:
            findings.append(f"terms: 1章で {terms} 語を定義している（{title[:12]}…）。{MAX_TERMS} 語までにし、残りは要る章で出す")


MAX_GOALS = 5
MAX_HEADING = 25
MAX_CHAPTERS = 12
MAX_CHAPTER_PROSE = 600
MAX_TOTAL_PROSE = 4000


def check_volume(root: Node, findings: list[str]) -> None:
    if len(chapter_prose(root)) < 4:
        return
    chapters = [(title, count) for title, count, _ in chapter_prose(root) if not is_end_chapter(title)]
    for node in walk(root):
        if "data-goals" in node.attrs:
            items = [child for child in walk(node) if child.tag == "li"]
            if len(items) > MAX_GOALS:
                findings.append(f"volume: 要点が {len(items)} 個。{MAX_GOALS} 個までに絞る")
            break
    if len(chapters) > MAX_CHAPTERS:
        findings.append(f"volume: 章が {len(chapters)} 個。{MAX_CHAPTERS} 個までにまとめる")
    for title, count in chapters:
        heading = re.sub(r"^\d+[.．]\s*", "", title).replace(" ", "")
        if len(heading) > MAX_HEADING:
            findings.append(f"volume: 見出しが {len(heading)} 字（{heading[:12]}…）。{MAX_HEADING} 字までにする")
        if count > MAX_CHAPTER_PROSE:
            findings.append(f"volume: 章の文章が {count} 字（{heading[:12]}…）。{MAX_CHAPTER_PROSE} 字までにする")
    total = sum(count for _, count in chapters)
    if total > MAX_TOTAL_PROSE:
        findings.append(f"volume: 文章が合計 {total} 字。{MAX_TOTAL_PROSE} 字までに削る")


AGENT_SKILL_STATES = ("ある", "無い", "未確認")


def check_agent_skills(root: Node, findings: list[str]) -> None:
    if sum(1 for node in walk(root) if node.tag == "h2") < 4:
        return
    marked = [node for node in walk(root) if "data-agent-skills" in node.attrs]
    if not marked:
        findings.append("agent-skills: 公式 skill の章（data-agent-skills）が無い。有無は必ず章で書く")
        return
    node = marked[0]
    state = node.attrs.get("data-agent-skills", "").strip()
    if state not in AGENT_SKILL_STATES:
        findings.append(
            f"agent-skills: data-agent-skills は {' / '.join(AGENT_SKILL_STATES)} のどれか（今は「{state}」）"
        )
    if node.tag != "h2" and not any(child.tag == "h2" for child in walk(node)):
        findings.append("agent-skills: data-agent-skills は章（h2 か h2 を含む要素）に付ける")
    if not any(
        child.tag == "a" and child.attrs.get("href", "").startswith("https://") for child in walk(node)
    ):
        findings.append("agent-skills: 公式 skill の章に、確かめた場所の公式リンクが無い")

"""ページの枠のルール（狭い画面、外部読み込み、動きの停止、目次）。"""

from __future__ import annotations

import re

from css import Sheet, animation_names, first_token, px_value, split_tracks, strip_comments, styles_for
from htmldoc import Node, ancestors, contains, norm_heading, visible_text, walk


CDN_HOSTS = ("unpkg.com", "cdn.jsdelivr.net", "cdnjs.cloudflare.com", "esm.sh")
NARROW_PX = 360


def scrolls_x(node: Node, sheet: Sheet) -> bool:
    decls = styles_for(node, sheet.rules)
    return any(first_token(decls.get(prop, "")) in {"auto", "scroll"} for prop in ("overflow-x", "overflow"))


def wraps(node: Node, sheet: Sheet) -> bool:
    for current in [node, *ancestors(node)]:
        decls = styles_for(current, sheet.rules)
        if first_token(decls.get("overflow-wrap", decls.get("word-wrap", ""))) in {"anywhere", "break-word"}:
            return True
        if first_token(decls.get("word-break", "")) in {"break-all", "break-word"}:
            return True
    return False


def check_responsive(root: Node, sheet: Sheet, css: str, findings: list[str]) -> None:
    viewport = [
        node
        for node in walk(root)
        if node.tag == "meta" and node.attrs.get("name", "").lower() == "viewport"
    ]
    if not viewport or "width=device-width" not in viewport[0].attrs.get("content", "").replace(" ", ""):
        findings.append("responsive: meta viewport（width=device-width）が無い")
    if not re.search(r"@media[^{]*max-width", strip_comments(css)):
        findings.append("responsive: 狭い幅の @media (max-width) が無い")
    for node in walk(root):
        if node.tag == "svg":
            if "viewBox" not in node.attrs and "viewbox" not in node.attrs:
                findings.append("responsive: viewBox の無い svg がある。幅に合わせて縮まない")
            raw = node.attrs.get("width", "").strip()
            width = px_value(raw if raw.endswith("px") else raw + "px") if raw else None
            decls = styles_for(node, sheet.rules)
            fluid = "100%" in decls.get("width", "") or "100%" in decls.get("max-width", "")
            if width is not None and width > NARROW_PX and not fluid:
                findings.append(
                    f"responsive: svg の幅が {int(width)}px 固定。CSS で width か max-width を 100% にする"
                )
        if node.tag == "figure":
            overflow = styles_for(node, sheet.rules)
            for prop in ("overflow-x", "overflow"):
                if first_token(overflow.get(prop, "")) in {"auto", "scroll"}:
                    findings.append("responsive: 図が横スクロールする。狭い幅では縮めるか、縦に並べ替える")
                    break
    for node in walk(root):
        if node.tag != "table":
            continue
        if not scrolls_x(node, sheet) and not any(
            scrolls_x(ancestor, sheet) for ancestor in ancestors(node)
        ):
            findings.append("responsive: 表が横スクロールの枠に入っていない。overflow-x: auto の要素で包む")
    for node in walk(root):
        if node.tag != "code" or any(ancestor.tag == "pre" for ancestor in ancestors(node)):
            continue
        if not wraps(node, sheet):
            findings.append(
                "responsive: 本文中のコードが折り返さない。overflow-wrap: anywhere を本文か code に付ける"
            )
        break
    for rule in sheet.rules:
        value = px_value(rule.decls.get("min-width", ""))
        if value is not None and value > NARROW_PX:
            findings.append(
                f"responsive: min-width が {int(value)}px（{', '.join(rule.selectors)}）。狭い画面からはみ出す"
            )


def check_external(html: str, findings: list[str]) -> None:
    if re.search(r"<script\b[^>]*\bsrc\s*=", html, flags=re.I):
        findings.append("external: 外部 script がある。確認クイズの採点もファイル内に書く")
    if re.search(r"<link\b[^>]*\brel\s*=\s*['\"]stylesheet", html, flags=re.I):
        findings.append("external: 外部 stylesheet がある。CSS はファイル内に書く")
    for host in CDN_HOSTS:
        if host in html:
            findings.append(f"external: CDN がある ({host})")
    if re.search(r"\bmermaid(?:\.min)?\.js\b", html, flags=re.I) or re.search(
        r"class\s*=\s*['\"][^'\"]*\bmermaid\b", html, flags=re.I
    ):
        findings.append("external: Mermaid がある")


def check_motion(sheet: Sheet, findings: list[str]) -> None:
    animated = False
    for rule in sheet.rules:
        if animation_names(rule.decls):
            animated = True
            break
    if not animated:
        return
    if not sheet.motion_bodies:
        findings.append("motion: 動きがあるのに prefers-reduced-motion: reduce が無い")
        return
    for body in sheet.motion_bodies:
        compact = re.sub(r"\s+", "", body.lower())
        if (
            "animation:none" in compact
            or "animation-name:none" in compact
            or "animation-play-state:paused" in compact
            or "display:none" in compact
        ):
            return
    findings.append("motion: prefers-reduced-motion: reduce でアニメーションが止まらない")


def find_toc(root: Node) -> Node | None:
    fallback = None
    for node in walk(root):
        if "toc" in node.classes:
            return node
        if node.attrs.get("aria-label") == "目次":
            fallback = fallback or node
    return fallback


def check_toc(root: Node, sheet: Sheet, findings: list[str]) -> None:
    toc = find_toc(root)
    headings = [
        norm_heading(visible_text(node))
        for node in walk(root)
        if node.tag == "h2" and (toc is None or not contains(toc, node))
    ]
    if toc is None:
        if headings:
            findings.append("toc-text: 目次が無い")
        return
    links = [norm_heading(visible_text(node)) for node in walk(toc) if node.tag == "a"]
    if links != headings:
        findings.append(f"toc-text: 目次と見出しが違う。目次={links} 見出し={headings}")
    check_toc_side(toc, sheet, findings)


def check_toc_side(toc: Node, sheet: Sheet, findings: list[str]) -> None:
    parent = toc.parent
    if parent is None:
        findings.append("toc-side: 目次の親が無い")
        return
    parent_style = styles_for(parent, sheet.rules)
    if parent_style.get("display") != "grid":
        findings.append("toc-side: 目次の親が横並びの grid でない")
        return
    tracks = split_tracks(parent_style.get("grid-template-columns", ""))
    if len(tracks) < 2:
        findings.append("toc-side: 目次を右に分ける列が無い")
        return
    order = styles_for(toc, sheet.rules).get("order", "0").strip()
    if re.match(r"^-\d", order):
        findings.append("toc-side: デスクトップで目次が本文より前に出る")
        return
    children = parent.elements()
    if toc not in children:
        findings.append("toc-side: 目次が grid の直下に無い")
        return
    index = children.index(toc)
    grid_column = styles_for(toc, sheet.rules).get("grid-column", "")
    on_last = re.match(r"^(-?\d+)", grid_column.strip())
    if on_last and int(on_last.group(1)) in {len(tracks), -1}:
        return
    if index != len(children) - 1 or index == 0:
        findings.append("toc-side: 目次が右の列に無い")


def check_spacing(root: Node, sheet: Sheet, findings: list[str]) -> None:
    sections = [node for node in walk(root) if node.tag == "section"]
    if sections:
        decls = styles_for(sections[0], sheet.rules)
        if first_token(decls.get("display", "")) not in {"flex", "grid"} or "gap" not in decls:
            findings.append("spacing: 章（section）の塊を gap で空けていない。「HTML」の余白の CSS を使う")
    if any(visible_text(node).strip().startswith("核心の一文") for node in walk(root) if node.tag in {"p", "div", "strong", "b"}):
        findings.append("spacing: 「核心の一文」という文字を書いている。p.core に文だけを書く")
    for figure in walk(root):
        if figure.tag != "figure" or figure.attrs.get("data-fig", "").strip() != "resume":
            continue
        chapter = next((node for node in ancestors(figure) if node.tag == "section"), root)
        cores = [node for node in walk(chapter) if node.tag == "p" and "core" in node.classes]
        if len(cores) != 1:
            findings.append(f"spacing: resume の図の章に p.core が {len(cores)} 個ある。核心の一文を1つ置く")

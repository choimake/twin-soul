"""図のルール（SVG の文字、配置と大きさ、図の役）。"""

from __future__ import annotations

import re

from css import Sheet, styles_for
from geometry import densify, path_points, point_inside, text_width
from htmldoc import Node, ancestors, visible_text, walk


def font_px(node: Node, sheet: Sheet) -> float | None:
    for current in [node, *ancestors(node)]:
        value = current.attrs.get("font-size") or styles_for(current, sheet.rules).get("font-size")
        if not value:
            continue
        value = value.strip()
        try:
            if value.endswith("rem"):
                return float(value[:-3]) * 16
            if value.endswith("px"):
                return float(value[:-2])
            return float(value)
        except ValueError:
            return None
    return 16.0


def check_svg_text(root: Node, sheet: Sheet, findings: list[str]) -> None:
    for text in walk(root):
        if text.tag != "text" or text.parent is None or "transform" in text.attrs:
            continue
        label = visible_text(text).strip()
        size = font_px(text, sheet)
        try:
            x = float(text.attrs.get("x") or "nan")
            y = float(text.attrs.get("y") or "nan")
        except ValueError:
            continue
        if not label or size is None or x != x or y != y:
            continue
        width = text_width(label, size)
        anchor = text.attrs.get("text-anchor") or styles_for(text, sheet.rules).get("text-anchor", "start")
        left = {"middle": x - width / 2, "end": x - width}.get(anchor.strip(), x)
        for rect in text.parent.children:
            if not isinstance(rect, Node) or rect.tag != "rect":
                continue
            try:
                rx = float(rect.attrs.get("x") or 0)
                ry = float(rect.attrs.get("y") or 0)
                rw = float(rect.attrs.get("width") or 0)
                rh = float(rect.attrs.get("height") or 0)
            except ValueError:
                continue
            if not (rx < x < rx + rw and ry < y - size / 3 < ry + rh):
                continue
            if left < rx - 2 or left + width > rx + rw + 2:
                findings.append(
                    f"svg-text: 「{label}」が箱の幅（{rw:g}）からはみ出す見込み。"
                    "文字を短くするか、行を分けるか、箱を広げる"
                )
            break


# 幅 375px のページで図に使える幅（左右の余白と図の枠の内側を除く）と、読める文字の下限
NARROW_FIG_PX = 320
MIN_TEXT_PX = 11


def number(node: Node, name: str) -> float | None:
    try:
        return float(node.attrs.get(name) or "nan")
    except ValueError:
        return None


def inherited(node: Node, sheet: Sheet, prop: str) -> str:
    for current in [node, *ancestors(node)]:
        value = current.attrs.get(prop) or styles_for(current, sheet.rules).get(prop)
        if value:
            return value
    return ""


def label_box(text: Node, sheet: Sheet) -> tuple[str, tuple[float, float, float, float]] | None:
    if any("transform" in node.attrs for node in [text, *ancestors(text)]):
        return None
    label = visible_text(text).strip()
    size = font_px(text, sheet)
    x, y = number(text, "x"), number(text, "y")
    if not label or size is None or x is None or y is None or x != x or y != y:
        return None
    width = text_width(label, size)
    anchor = inherited(text, sheet, "text-anchor").strip() or "start"
    left = {"middle": x - width / 2, "end": x - width}.get(anchor, x)
    return label, (left, y - size * 0.8, left + width, y + size * 0.2)


# ラベルと線や箱のあいだに空ける最小の隙間
LABEL_CLEAR = 3


def grow(box: tuple[float, float, float, float], amount: float) -> tuple[float, float, float, float]:
    return (box[0] - amount, box[1] - amount, box[2] + amount, box[3] + amount)


def overlaps(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> bool:
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def stroke_points(node: Node) -> list[tuple[float, float]]:
    if node.tag == "line":
        values = [number(node, name) for name in ("x1", "y1", "x2", "y2")]
        if any(value is None or value != value for value in values):
            return []
        x1, y1, x2, y2 = values
        return densify([(x1, y1), (x2, y2)])
    if node.tag in {"polyline", "polygon"}:
        numbers = [float(value) for value in re.findall(r"[-+]?(?:\d*\.\d+|\d+)", node.attrs.get("points", ""))]
        points = list(zip(numbers[::2], numbers[1::2]))
        return densify(points + points[:1] if node.tag == "polygon" else points)
    if node.tag == "path":
        try:
            return densify(path_points(node.attrs.get("d", "")))
        except ValueError:
            return []
    return []


def check_svg_label(root: Node, sheet: Sheet, findings: list[str]) -> None:
    for svg in walk(root):
        if svg.tag != "svg":
            continue
        nodes = [node for node in walk(svg) if not any(a.tag in {"defs", "marker"} for a in ancestors(node))]
        rects = [(node, (x, y, x + w, y + h)) for node in nodes if node.tag == "rect"
                 for x, y, w, h in [[number(node, n) or 0 for n in ("x", "y", "width", "height")]]]
        strokes = [stroke_points(node) for node in nodes if node.tag in {"line", "polyline", "polygon", "path"}]
        labels = [(text, box) for text in nodes if text.tag == "text" and (box := label_box(text, sheet))]
        frame = view_box(svg)
        for index, (text, (label, box)) in enumerate(labels):
            if frame and not (frame[0] <= box[0] and frame[1] <= box[1] and box[2] <= frame[2] and box[3] <= frame[3]):
                findings.append(f"svg-label: 「{label}」が viewBox からはみ出て切れる。ラベルを内側に寄せるか、viewBox を広げる")
            siblings = text.parent.children if text.parent else []
            clear = grow(box, LABEL_CLEAR)
            for rect, area in rects:
                if rect in siblings or not overlaps(clear, area):
                    continue
                if area[0] <= box[0] and area[1] <= box[1] and box[2] <= area[2] and box[3] <= area[3]:
                    continue
                findings.append(
                    f"svg-label: 「{label}」が箱と重なる。ラベルは箱の外に出し、入れ物の箱の名前は中の箱より上に置く"
                )
                break
            if any(point_inside(x, y, clear) for points in strokes for x, y in points):
                findings.append(
                    f"svg-label: 「{label}」に線が重なるか {LABEL_CLEAR}px 以内に近い。縁取りで隠さず、ラベルを線から離す。"
                    "生存線をまたぐなら、ラベルを始点の隣の区間に収めるか、生存線の間隔を広げる"
                )
            for _, (other, other_box) in labels[index + 1 :]:
                if overlaps(box, other_box):
                    findings.append(f"svg-label: 「{label}」と「{other}」が重なる。ラベルの位置をずらす")


def hidden_when_narrow(node: Node, sheet: Sheet) -> bool:
    for current in [node, *ancestors(node)]:
        display = styles_for(current, sheet.narrow_rules).get("display") or styles_for(current, sheet.rules).get("display", "")
        if display.strip() == "none":
            return True
    return False


def check_svg_narrow(root: Node, sheet: Sheet, findings: list[str]) -> None:
    for svg in walk(root):
        if svg.tag != "svg" or hidden_when_narrow(svg, sheet):
            continue
        view_width = view_box_width(svg)
        if view_width is None:
            continue
        sizes = [size for text in walk(svg) if text.tag == "text" and (size := font_px(text, sheet))]
        if not sizes or view_width <= NARROW_FIG_PX:
            continue
        shown = min(sizes) * NARROW_FIG_PX / view_width
        if shown < MIN_TEXT_PX:
            findings.append(
                f"svg-narrow: 幅 375px で図の文字が約 {shown:.1f}px になる（viewBox の幅 {view_width:g}）。"
                f"{MIN_TEXT_PX}px 以上になるよう、狭い幅用に箱を縦に並べた SVG を置き、@media で切り替える"
            )


def view_box(svg: Node) -> tuple[float, float, float, float] | None:
    parts = (svg.attrs.get("viewBox") or svg.attrs.get("viewbox") or "").replace(",", " ").split()
    try:
        x, y, width, height = (float(part) for part in parts)
    except ValueError:
        return None
    return (x, y, x + width, y + height)


def view_box_width(svg: Node) -> float | None:
    frame = view_box(svg)
    return frame[2] - frame[0] if frame else None


FIG_ROLES = (
    "what",
    "need",
    "cast",
    "resume",
    "struct",
    "branch",
)


def check_fig_roles(root: Node, findings: list[str]) -> None:
    headings = [node for node in walk(root) if node.tag == "h2"]
    if len(headings) < 4:
        return
    present: set[str] = set()
    skipped: set[str] = set()
    for node in walk(root):
        role = node.attrs.get("data-fig", "").strip()
        if role:
            present.add(role)
        for part in re.split(r"[\s,]+", node.attrs.get("data-fig-skip", "")):
            if part:
                skipped.add(part)
    missing = [role for role in FIG_ROLES if role not in present and role not in skipped]
    if missing:
        findings.append("fig-role: 図が無い役がある: " + ", ".join(missing) + "。話題が無くて省くなら、data-fig-skip にその役を書く")

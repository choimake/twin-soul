"""SVG の path を点の列にし、箱との重なりや文字の幅を見積もる。"""

from __future__ import annotations

import re
import unicodedata


NUMBER_RE = re.compile(r"[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?")
PATH_TOKEN_RE = re.compile(
    r"[MmLlHhVvCcSsQqTtAaZz]|" + NUMBER_RE.pattern
)


def path_points(d: str) -> list[tuple[float, float]]:
    tokens = PATH_TOKEN_RE.findall(d)
    index = 0
    cx = cy = 0.0
    start_x = start_y = 0.0
    prev_cmd = ""
    prev_cx = prev_cy = 0.0
    points: list[tuple[float, float]] = []

    def read_number() -> float:
        nonlocal index
        if index >= len(tokens) or not NUMBER_RE.fullmatch(tokens[index]):
            raise ValueError("path")
        value = float(tokens[index])
        index += 1
        return value

    def add_line(x: float, y: float) -> None:
        nonlocal cx, cy
        points.extend(densify([(cx, cy), (x, y)]))
        cx, cy = x, y

    def add_curve(p1: tuple[float, float], p2: tuple[float, float], p3: tuple[float, float]) -> None:
        nonlocal cx, cy, prev_cx, prev_cy
        samples = cubic((cx, cy), p1, p2, p3)
        points.extend(densify(samples))
        prev_cx, prev_cy = p2
        cx, cy = p3

    while index < len(tokens):
        token = tokens[index]
        if not NUMBER_RE.fullmatch(token):
            command = token
            index += 1
        else:
            command = "L" if prev_cmd in {"M", "L"} else "l" if prev_cmd in {"m", "l"} else prev_cmd
        prior = prev_cmd
        prev_cmd = command
        relative = command.islower()
        cmd = command.upper()
        if cmd == "M":
            x, y = read_number(), read_number()
            if relative:
                x += cx
                y += cy
            cx, cy = start_x, start_y = x, y
            points.append((cx, cy))
            while index < len(tokens) and NUMBER_RE.fullmatch(tokens[index]):
                x, y = read_number(), read_number()
                if relative:
                    x += cx
                    y += cy
                add_line(x, y)
            prev_cmd = "l" if relative else "L"
        elif cmd == "L":
            while index < len(tokens) and NUMBER_RE.fullmatch(tokens[index]):
                x, y = read_number(), read_number()
                if relative:
                    x += cx
                    y += cy
                add_line(x, y)
        elif cmd == "H":
            while index < len(tokens) and NUMBER_RE.fullmatch(tokens[index]):
                x = read_number()
                if relative:
                    x += cx
                add_line(x, cy)
        elif cmd == "V":
            while index < len(tokens) and NUMBER_RE.fullmatch(tokens[index]):
                y = read_number()
                if relative:
                    y += cy
                add_line(cx, y)
        elif cmd == "C":
            while index < len(tokens) and NUMBER_RE.fullmatch(tokens[index]):
                x1, y1 = read_number(), read_number()
                x2, y2 = read_number(), read_number()
                x, y = read_number(), read_number()
                if relative:
                    x1 += cx
                    y1 += cy
                    x2 += cx
                    y2 += cy
                    x += cx
                    y += cy
                add_curve((x1, y1), (x2, y2), (x, y))
        elif cmd == "S":
            reflected = prior.upper() in {"C", "S"}
            while index < len(tokens) and NUMBER_RE.fullmatch(tokens[index]):
                if reflected:
                    x1, y1 = 2 * cx - prev_cx, 2 * cy - prev_cy
                else:
                    x1, y1 = cx, cy
                x2, y2 = read_number(), read_number()
                x, y = read_number(), read_number()
                if relative:
                    x2 += cx
                    y2 += cy
                    x += cx
                    y += cy
                add_curve((x1, y1), (x2, y2), (x, y))
                reflected = True
        elif cmd in {"Q", "T", "A"}:
            raise ValueError(cmd)
        elif cmd == "Z":
            add_line(start_x, start_y)
        else:
            raise ValueError(command)
    return points


def cubic(
    p0: tuple[float, float],
    p1: tuple[float, float],
    p2: tuple[float, float],
    p3: tuple[float, float],
) -> list[tuple[float, float]]:
    samples = []
    for step in range(25):
        t = step / 24
        u = 1 - t
        x = u**3 * p0[0] + 3 * u**2 * t * p1[0] + 3 * u * t**2 * p2[0] + t**3 * p3[0]
        y = u**3 * p0[1] + 3 * u**2 * t * p1[1] + 3 * u * t**2 * p2[1] + t**3 * p3[1]
        samples.append((x, y))
    return samples


def densify(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    if len(points) < 2:
        return list(points)
    dense: list[tuple[float, float]] = []
    for (x1, y1), (x2, y2) in zip(points, points[1:]):
        steps = max(int(max(abs(x2 - x1), abs(y2 - y1))), 1)
        for step in range(steps):
            t = step / steps
            dense.append((x1 + (x2 - x1) * t, y1 + (y2 - y1) * t))
    dense.append(points[-1])
    return dense


def point_inside(x: float, y: float, interior: tuple[float, float, float, float]) -> bool:
    left, top, right, bottom = interior
    return left < x < right and top < y < bottom


def text_width(text: str, size: float) -> float:
    return sum(size if unicodedata.east_asian_width(char) in "WF" else size * 0.6 for char in text)

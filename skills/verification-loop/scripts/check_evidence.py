#!/usr/bin/env python3
"""verification-loop の証拠を記録・照合する。

run:   コマンドを実行し、出力と終了コードをラウンドディレクトリの commands/ に残す
check: スコアカードの根拠（path:行 と引用、cmd:名前 と引用）が実在するかを確かめる。
       終了コードを判定するのは、根拠に挙げたコマンドと red- で始まる記録（0 以外が期待）だけ。
       それ以外の記録（着手前の確認や調べ物）は参考として出すだけにする

標準ライブラリだけで動く。
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

LINE_TOLERANCE = 2
EVIDENCE_HEADING = re.compile(r"^#{2,4}\s*根拠")
LOCATION = re.compile(r"^(?P<path>[^:\s][^:]*):(?P<line>\d+)$")
COMMAND_NAME = re.compile(r"^[A-Za-z0-9._-]+$")
# 実装を戻して落ちることを確かめるコマンド。0 以外の終了コードが期待どおり
RED_PREFIX = "red-"


@dataclass
class Evidence:
    criterion: str
    location: str
    quote: str


@dataclass
class Result:
    evidence: Evidence
    ok: bool
    reason: str


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def strip_code(cell: str) -> str:
    cell = cell.strip()
    if len(cell) >= 2 and cell.startswith("`") and cell.endswith("`"):
        return cell[1:-1]
    return cell


def split_row(line: str) -> list[str]:
    body = line.strip()
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|"):
        body = body[:-1]
    return [cell.strip() for cell in re.split(r"(?<!\\)\|", body)]


def parse_evidence(scorecard: str) -> list[Evidence]:
    """「根拠」見出しの直後の表を読む。列は 基準 / 場所 / 引用。"""
    rows: list[Evidence] = []
    in_section = False
    for line in scorecard.splitlines():
        if EVIDENCE_HEADING.match(line):
            in_section = True
            continue
        if in_section and line.startswith("#"):
            break
        if not in_section or not line.strip().startswith("|"):
            continue
        cells = split_row(line)
        if len(cells) < 3 or set(cells[0]) <= set("-: "):
            continue
        if cells[0] == "基準":
            continue
        quote = strip_code(cells[2]).replace("\\|", "|")
        rows.append(Evidence(cells[0], strip_code(cells[1]), quote))
    return rows


def check_file(ev: Evidence, repo: Path) -> Result:
    match = LOCATION.match(ev.location)
    if not match:
        return Result(ev, False, "場所が path:行 でも cmd:名前 でもない")
    path = repo / match["path"]
    if not path.is_file():
        return Result(ev, False, f"ファイルが無い: {match['path']}")
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    line_no = int(match["line"])
    if line_no < 1 or line_no > len(lines):
        return Result(ev, False, f"行が範囲外（{len(lines)} 行）")
    if not ev.quote:
        return Result(ev, False, "引用が空")
    start = max(0, line_no - 1 - LINE_TOLERANCE)
    window = normalize(" ".join(lines[start : line_no + LINE_TOLERANCE]))
    if normalize(ev.quote) in window:
        return Result(ev, True, "")
    return Result(ev, False, f"引用が {line_no}±{LINE_TOLERANCE} 行に無い")


def check_command(ev: Evidence, round_dir: Path) -> Result:
    name = ev.location[len("cmd:") :]
    log = round_dir / "commands" / f"{name}.log"
    exit_file = round_dir / "commands" / f"{name}.exit"
    if not log.is_file() or not exit_file.is_file():
        return Result(ev, False, f"記録が無い: commands/{name}.log / .exit")
    if ev.quote and normalize(ev.quote) not in normalize(log.read_text(encoding="utf-8", errors="replace")):
        return Result(ev, False, "引用がログに無い")
    return Result(ev, True, "")


def check(round_dir: Path, repo: Path) -> int:
    scorecard = round_dir / "scorecard.md"
    if not scorecard.is_file():
        print(f"NG スコアカードが無い: {scorecard}")
        return 1
    evidence = parse_evidence(scorecard.read_text(encoding="utf-8"))
    failed = 0
    if not evidence:
        print("NG 根拠の表が無い、または空")
        failed += 1
    cited = {ev.location[len("cmd:") :] for ev in evidence if ev.location.startswith("cmd:")}
    for ev in evidence:
        if ev.location.startswith("cmd:"):
            result = check_command(ev, round_dir)
        else:
            result = check_file(ev, repo)
        if not result.ok:
            failed += 1
            print(f"NG [{ev.criterion}] {ev.location}: {result.reason}")
    for exit_file in sorted((round_dir / "commands").glob("*.exit")):
        name = exit_file.stem
        code = exit_file.read_text(encoding="utf-8").strip()
        log = exit_file.with_suffix(".log")
        if name.startswith(RED_PREFIX):
            if code == "0":
                failed += 1
                print(f"NG cmd:{name} 実装を戻したのにテストが落ちなかった（終了コード 0）")
        elif code != "0":
            if name in cited:
                failed += 1
                print(f"NG cmd:{name} 根拠に挙げたコマンドの終了コード {code}")
            else:
                print(f"参考 cmd:{name} 終了コード {code}（根拠に挙げていない）")
        elif name in cited and log.is_file() and log.stat().st_size == 0:
            print(f"注意 cmd:{name} 出力が空")
    print(f"根拠 {len(evidence)} 件 / NG {failed} 件")
    return 1 if failed else 0


def run(round_dir: Path, name: str, command: list[str], cwd: Path) -> int:
    if not COMMAND_NAME.match(name):
        print(f"名前に使えない文字がある: {name}", file=sys.stderr)
        return 2
    if not command:
        print("実行するコマンドが無い（-- の後に書く）", file=sys.stderr)
        return 2
    out_dir = round_dir / "commands"
    out_dir.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=False)
    header = f"$ {' '.join(command)}\n(cwd: {cwd})\n"
    (out_dir / f"{name}.log").write_text(header + proc.stdout + proc.stderr, encoding="utf-8")
    (out_dir / f"{name}.exit").write_text(f"{proc.returncode}\n", encoding="utf-8")
    print(f"cmd:{name} 終了コード {proc.returncode}")
    return proc.returncode


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    p_run = sub.add_parser("run", help="コマンドを実行して出力と終了コードを残す")
    p_run.add_argument("--round-dir", type=Path, required=True)
    p_run.add_argument("--name", required=True)
    p_run.add_argument("--cwd", type=Path, default=Path.cwd())
    p_run.add_argument("command", nargs=argparse.REMAINDER)
    p_check = sub.add_parser("check", help="スコアカードの根拠と終了コードを照合する")
    p_check.add_argument("--round-dir", type=Path, required=True)
    p_check.add_argument("--repo", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)
    if args.action == "run":
        command = args.command[1:] if args.command[:1] == ["--"] else args.command
        return run(args.round_dir, args.name, command, args.cwd)
    return check(args.round_dir, args.repo)


if __name__ == "__main__":
    sys.exit(main())

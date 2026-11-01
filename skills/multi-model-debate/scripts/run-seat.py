#!/usr/bin/env python3
"""議論役の CLI を 1 回呼び、時間の上限で確実に止める。

使い方:
  python3 run-seat.py --out <回答ファイル> [--stdin <指示文ファイル>]
                      [--timeout 秒] [--idle 秒] -- <コマンド> [引数...]
  python3 run-seat.py --self-test

止める条件は 2 つ。
- 全体の上限（--timeout）を過ぎた
- 何か出力したあと、--idle 秒のあいだ出力が増えない（回答を出し終えても終了しないツールへの対策）

止めるときは、プロセスグループごと TERM を送り、--grace 秒たっても残っていれば KILL する。

終了コード:
- コマンドが自分で終了した: そのコマンドの終了コード
- 出力が止まったので止めた: 3（回答が最後まで出ているかは呼び出し側が見る）
- 全体の上限で止めた: 124
"""

from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

IDLE_STOPPED = 3
TIMED_OUT = 124


def _stop(proc: subprocess.Popen, grace: float) -> None:
    """プロセスグループに TERM を送り、残っていれば KILL する。"""
    for sig in (signal.SIGTERM, signal.SIGKILL):
        try:
            os.killpg(proc.pid, sig)
        except ProcessLookupError:
            return
        try:
            proc.wait(timeout=grace)
            if sig == signal.SIGTERM:
                # 親が止まっても子が残ることがあるので、グループに KILL まで送る
                continue
        except subprocess.TimeoutExpired:
            continue
    try:
        proc.wait(timeout=grace)
    except subprocess.TimeoutExpired:
        pass


def run(cmd: list[str], out: Path, stdin: Path | None, timeout: float, idle: float, grace: float) -> int:
    err = out.with_name(out.name + ".err")
    with open(out, "wb") as out_f, open(err, "wb") as err_f:
        in_f = open(stdin, "rb") if stdin else subprocess.DEVNULL
        try:
            proc = subprocess.Popen(cmd, stdin=in_f, stdout=out_f, stderr=err_f, start_new_session=True)
        finally:
            if stdin:
                in_f.close()
    start = time.monotonic()
    last_size = 0
    last_change = start
    while True:
        rc = proc.poll()
        if rc is not None:
            # 親が終わっても、同じグループに子が残っていれば止める
            _stop(proc, grace)
            print(f"run-seat: exited rc={rc}", file=sys.stderr)
            return rc
        now = time.monotonic()
        size = out.stat().st_size
        if size != last_size:
            last_size, last_change = size, now
        if now - start >= timeout:
            _stop(proc, grace)
            print(f"run-seat: stopped by timeout {timeout:g}s", file=sys.stderr)
            return TIMED_OUT
        if size > 0 and now - last_change >= idle:
            _stop(proc, grace)
            print(f"run-seat: stopped after {idle:g}s without new output", file=sys.stderr)
            return IDLE_STOPPED
        time.sleep(0.2)


def self_test() -> int:
    py = sys.executable
    ignore_term = "import signal,sys,time\nfor s in (signal.SIGTERM, signal.SIGINT, signal.SIGALRM, signal.SIGHUP): signal.signal(s, signal.SIG_IGN)\n"
    cases = [
        # (名前, コマンド, 期待する終了コード, 上限秒)
        ("回答後に居座り、TERM を無視する", [py, "-c", ignore_term + "print('answer', flush=True); time.sleep(1000)"], IDLE_STOPPED, 4),
        ("何も出さずに上限を超える", [py, "-c", ignore_term + "time.sleep(1000)"], TIMED_OUT, 4),
        ("自分で終了する", [py, "-c", "import sys; print('answer'); sys.exit(7)"], 7, 2),
    ]
    failed = 0
    with tempfile.TemporaryDirectory() as d:
        for name, cmd, want, limit in cases:
            out = Path(d) / "out.md"
            t0 = time.monotonic()
            rc = run(cmd, out, None, timeout=2, idle=1, grace=0.5)
            took = time.monotonic() - t0
            ok = rc == want and took < limit
            failed += not ok
            print(f"{'PASS' if ok else 'FAIL'}: {name} rc={rc} want={want} took={took:.1f}s")
        # 親が終了しても、TERM を無視する子が残らないこと
        pidfile = Path(d) / "child.pid"
        child = ignore_term + f"open({str(pidfile)!r}, 'w').write(str(__import__('os').getpid())); time.sleep(1000)"
        parent = f"import subprocess,sys,time; subprocess.Popen([sys.executable, '-c', {child!r}]); time.sleep(0.5); print('answer')"
        run([py, "-c", parent], Path(d) / "out.md", None, timeout=2, idle=1, grace=0.5)
        cpid = int(pidfile.read_text())
        # KILL 直後は回収前のゾンビとして見えることがあるので、少し待って確かめる
        alive = True
        for _ in range(20):
            try:
                os.kill(cpid, 0)
            except ProcessLookupError:
                alive = False
                break
            time.sleep(0.1)
        failed += alive
        print(f"{'FAIL' if alive else 'PASS'}: 親の終了後に子を残さない")
    return 1 if failed else 0


def main() -> int:
    p = argparse.ArgumentParser(description="議論役の CLI を時間の上限付きで呼ぶ")
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--out", type=Path, help="回答（標準出力）の保存先。標準エラーは <out>.err")
    p.add_argument("--stdin", type=Path, help="標準入力に渡すファイル")
    p.add_argument("--timeout", type=float, default=600, help="全体の上限（秒）。既定 600")
    p.add_argument("--idle", type=float, default=120, help="出力が止まってから止めるまでの秒数。既定 120")
    p.add_argument("--grace", type=float, default=5, help="TERM から KILL までの秒数。既定 5")
    p.add_argument("cmd", nargs=argparse.REMAINDER)
    a = p.parse_args()
    if a.self_test:
        return self_test()
    cmd = a.cmd[1:] if a.cmd[:1] == ["--"] else a.cmd
    if not a.out or not cmd:
        p.error("--out と、-- のあとのコマンドが必要")
    return run(cmd, a.out, a.stdin, a.timeout, a.idle, a.grace)


if __name__ == "__main__":
    sys.exit(main())

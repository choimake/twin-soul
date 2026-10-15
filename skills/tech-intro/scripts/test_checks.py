"""checks.py と入口 check-html.py のテスト。実行: python3 -I -m unittest discover -s skills/tech-intro/scripts"""

from __future__ import annotations

import ast
import inspect
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import checks
from checks import check_html, dedupe
from selftest import PASS_HTML, page

SCRIPT = Path(__file__).resolve().parent / "check-html.py"


# checks.check_html() が呼ぶ順の id。check_toc は toc-side を出す
RULE_ORDER = [
    "responsive",
    "external",
    "motion",
    "toc-side",
    "banned",
    "motion-stop",
    "svg-cross",
    "svg-text",
    "fig-role",
    "goals",
    "scope",
    "agent-skills",
    "volume",
    "endings",
    "terms",
    "early-detail",
    "motion-fig",
]

# どのルールも指摘を 1 件だけ出すページ。呼ぶ順を入れ替えると id の並びが変わる
EVERY_RULE_HTML = page(
    """
    <p data-fig-skip="what need cast struct">扱わない。</p>
    <h2 id="a">なぜ要るか</h2>
    <p><dfn>node</dfn>、<dfn>topic</dfn>、<dfn>message</dfn>、<dfn>callback</dfn> を定義する。公式の正本を見る。</p>
    <pre><code>step.run("load")</code></pre>
    <table><tr><td>a</td></tr></table>
    <svg viewBox="0 0 300 80">
      <path class="flow" d="M10 30 L240 30"/>
      <rect x="20" y="10" width="80" height="40"/><rect x="160" y="10" width="80" height="40"/>
    </svg>
    <svg viewBox="0 0 300 80">
      <rect x="20" y="10" width="124" height="52"/>
      <text x="82" y="36" text-anchor="middle">同じプロセス・別プロセス</text>
    </svg>
    <figure data-fig="resume"><div class="row"><div class="box">step</div><div class="box">step</div></div></figure>
    <h2 id="b">登場人物</h2>
    <h2 id="c">送る側と受け取る側を分けて部品を組み合わせるための通信の仕組みである</h2>
    <section data-agent-skills="たぶんある">
      <h2 id="d">公式 skill</h2><a href="https://example.com/">確かめた場所</a>
    </section>
    <h2 id="x">チェックリスト</h2><h2 id="y">確かめられなかったこと</h2><h3>確認クイズ</h3>
    """,
    """
    .box { border: 1px solid #111; }
    .flow { animation: dash 1s linear infinite; }
    @keyframes dash { from { stroke-dashoffset: 1; } to { stroke-dashoffset: 0; } }
    svg text { font-size: 12px; }
    """,
    motion=False,
    columns="220px minmax(0, 1fr)",
    toc_first=True,
    toc_html="""<aside class="toc">
      <a href="#a">なぜ要るか</a>
      <a href="#b">登場人物</a>
      <a href="#c">送る側と受け取る側を分けて部品を組み合わせるための通信の仕組みである</a>
      <a href="#d">公式 skill</a>
      <a href="#x">チェックリスト</a>
      <a href="#y">確かめられなかったこと</a>
    </aside>""",
    head_extra='<script src="x.js"></script>',
    scope="<details open data-scope><summary>対象と版</summary></details>",
)


class DedupeTest(unittest.TestCase):
    def test_keeps_first_order_and_counts_repeats(self) -> None:
        self.assertEqual(dedupe(["a", "b", "a", "a"]), ["a（3箇所）", "b"])


class CheckHtmlTest(unittest.TestCase):
    def test_pass_html_has_no_findings(self) -> None:
        self.assertEqual(check_html(PASS_HTML), [])

    def test_rule_order_covers_every_rule_called(self) -> None:
        # check_html() にルールを足して RULE_ORDER と EVERY_RULE_HTML を足し忘れたら落とす
        tree = ast.parse(inspect.getsource(checks.check_html))
        called = [
            node.func.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id.startswith("check_")
            and node.func.id != "check_html"
        ]
        self.assertEqual(len(called), len(RULE_ORDER), called)

    def test_findings_follow_rule_order(self) -> None:
        ids = [item.split(":", 1)[0] for item in check_html(EVERY_RULE_HTML)]
        self.assertEqual(ids, RULE_ORDER)

    def test_repeated_finding_is_merged(self) -> None:
        html = PASS_HTML.replace("</article>", "<table></table><table></table></article>")
        self.assertEqual(
            check_html(html), ["responsive: 表が横スクロールの枠に入っていない。overflow-x: auto の要素で包む（2箇所）"]
        )


class CliTest(unittest.TestCase):
    """python3 -I で、別のカレントディレクトリから入口を呼ぶ。"""

    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as tmp:
            return subprocess.run(
                [sys.executable, "-I", str(SCRIPT), *args], cwd=tmp, capture_output=True, text=True, check=False
            )

    def write(self, tmp: str, html: str) -> str:
        path = Path(tmp) / "page.html"
        path.write_text(html, encoding="utf-8")
        return str(path)

    def test_self_test_passes(self) -> None:
        result = self.run_cli("--self-test")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "self-test ok\n")

    def test_clean_page_exits_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_cli(self.write(tmp, PASS_HTML))
        self.assertEqual((result.returncode, result.stdout, result.stderr), (0, "", ""))

    def test_findings_exit_one_and_hedges_are_listed(self) -> None:
        html = PASS_HTML.replace(
            "</article>", "<p>正本</p><details><summary>出典</summary><p>It may run.</p></details></article>"
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(tmp, html)
            result = self.run_cli(path)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(
            result.stdout,
            f"{path}:\n  banned: 「正本」がある\n{path}: 強さの語を含む引用（合否に数えない）\n  なぜ要るか: It may run.\n",
        )

    def test_no_argument_is_usage_error(self) -> None:
        result = self.run_cli()
        self.assertEqual(result.returncode, 2)
        self.assertIn("check-html.py: error: HTML ファイルか --self-test を指定する", result.stderr)

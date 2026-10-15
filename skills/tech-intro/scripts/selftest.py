"""--self-test で回す、ルールごとの見本ページと期待する指摘。"""

from __future__ import annotations

import sys

from checks import check_html
from hedges import hedged_quotes


ENDING_BODY = """
<h2 id="x">チェックリスト</h2><p><dfn>topic</dfn> は名前である。</p>
<h2 id="y">確かめられなかったこと</h2>
<h2 id="z">確認クイズ</h2>
"""
ENDING_TOC = '<a href="#x">チェックリスト</a><a href="#y">確かめられなかったこと</a><a href="#z">確認クイズ</a>'
SCOPE_HTML = "<details data-scope><summary>対象と版</summary><p>確認日 2026-10-07。</p></details>"


def page(
    body: str,
    css: str = "",
    *,
    motion: bool = True,
    columns: str = "minmax(0, 1fr) 220px",
    toc_first: bool = False,
    toc_html: str | None = None,
    head_extra: str = "",
    ending: bool = False,
    scope: str | None = None,
) -> str:
    toc = toc_html or '<aside class="toc"><a href="#why">なぜ要るか</a></aside>'
    if scope is None and ending:
        scope = SCOPE_HTML
    if scope:
        body = scope + body
    if ending:
        body += ENDING_BODY
        toc = toc.replace("</aside>", ENDING_TOC + "</aside>")
    article = f"<article>{body}</article>"
    main = f"{toc}{article}" if toc_first else f"{article}{toc}"
    motion_css = ""
    if motion:
        motion_css = """
        @media (prefers-reduced-motion: reduce) {
          .flow { animation: none; stroke-dashoffset: 0; }
        }
        """
    return f"""<!DOCTYPE html>
<html lang="ja"><head><meta name="viewport" content="width=device-width, initial-scale=1">{head_extra}<style>
.page {{ display: grid; grid-template-columns: {columns}; }}
{css}
@media (max-width: 820px) {{
  aside.toc {{ order: -1; }}
}}
{motion_css}
</style></head><body><div class="page">{main}</div></body></html>"""


PASS_HTML = page(
    """
    <h2 id="why">なぜ要るか</h2>
    <svg viewBox="0 0 260 60">
      <path class="flow" pathLength="1" d="M90 30 L160 30"/>
      <rect x="10" y="10" width="80" height="40"/>
      <rect x="160" y="10" width="80" height="40"/>
    </svg>
    """,
    """
    .flow { stroke-dasharray: 1; stroke-dashoffset: 1; animation: dash 1s linear forwards; }
    @keyframes dash { from { stroke-dashoffset: 1; } to { stroke-dashoffset: 0; } }
    """,
)

CASES: list[tuple[str, str, set[str]]] = [
    ("pass", PASS_HTML, set()),
    (
        "motion-stop-infinite",
        page('<h2 id="why">なぜ要るか</h2><span class="flow"></span>',
             '.flow { animation: draw 1s infinite; } @keyframes draw { to { stroke-dashoffset: 0; } }'),
        {"motion-stop"},
    ),
    (
        "svg-cross",
        page(
            """
            <h2 id="why">なぜ要るか</h2>
            <svg viewBox="0 0 300 80">
              <path class="flow" pathLength="1" d="M10 30 L240 30"/>
              <rect x="20" y="10" width="80" height="40"/>
              <rect x="160" y="10" width="80" height="40"/>
            </svg>
            """,
            """
            .flow { stroke-dasharray: 1; stroke-dashoffset: 1; animation: dash 1s linear forwards; }
            @keyframes dash { from { stroke-dashoffset: 1; } to { stroke-dashoffset: 0; } }
            """,
        ),
        {"svg-cross"},
    ),
    (
        "svg-text",
        page(
            """
            <h2 id="why">なぜ要るか</h2>
            <svg viewBox="0 0 300 80">
              <rect x="20" y="10" width="124" height="52"/>
              <text x="82" y="36" text-anchor="middle">同じプロセス・別プロセス</text>
              <rect x="160" y="10" width="124" height="52"/>
              <text x="222" y="36" text-anchor="middle">短い名前</text>
            </svg>
            """,
            "svg text { font-size: 12px; }",
        ),
        {"svg-text"},
    ),
    (
        "external",
        page(
            "<h2 id=\"why\">なぜ要るか</h2>",
            head_extra='<script src="https://unpkg.com/mermaid/dist/mermaid.min.js"></script>',
        ),
        {"external"},
    ),
    (
        "motion",
        page(
            "<h2 id=\"why\">なぜ要るか</h2><span class=\"flow\"></span>",
            ".flow { animation: blink 1s forwards; } @keyframes blink { from { opacity: 1; } to { opacity: 0; } }",
            motion=False,
        ),
        {"motion"},
    ),
    (
        "toc-text",
        page(
            "<h2 id=\"why\">なぜ要るか</h2>",
            toc_html='<aside class="toc"><a href="#why">別の見出し</a></aside>',
        ),
        {"toc-text"},
    ),
    (
        "toc-side",
        page(
            "<h2 id=\"why\">なぜ要るか</h2>",
            columns="220px minmax(0, 1fr)",
            toc_first=True,
        ),
        {"toc-side"},
    ),
    (
        "banned",
        page("<h2 id=\"why\">なぜ要るか</h2><p>公式の正本を見る。</p>"),
        {"banned"},
    ),
    (
        "banned-vague",
        page("<h2 id=\"why\">なぜ要るか</h2><p>対象の行が無いと、その変更は黙って飛ばされる。</p>"),
        {"banned"},
    ),
    (
        "banned-vague-quiet",
        page("<h2 id=\"why\">なぜ要るか</h2><p>対象の行が無いと、その変更は静かに捨てられる。</p>"),
        {"banned"},
    ),
    (
        "banned-vague-pass",
        page("<h2 id=\"why\">なぜ要るか</h2><p>対象の行が無いと、その変更はエラーにならずに飛ばされる。</p>"),
        set(),
    ),
    (
        "fig-role",
        page(
            """
            <ol data-goals><li>何か</li><li>何ができるか</li></ol>
            <h2 id="a">なぜ要るか</h2>
            <h2 id="b">登場人物</h2>
            <h2 id="c">構造</h2>
            <section data-agent-skills="無い"><h2 id="d">仕組み</h2><a href="https://example.com/">確かめた場所</a></section>
            """,
            toc_html="""<aside class="toc">
              <a href="#a">なぜ要るか</a>
              <a href="#b">登場人物</a>
              <a href="#c">構造</a>
              <a href="#d">仕組み</a>
            </aside>""",
            ending=True,
        ),
        {"fig-role"},
    ),
    (
        "fig-skip",
        page(
            """
            <ol data-goals><li>何か</li><li>何ができるか</li></ol>
            <p data-fig-skip="what need cast resume struct branch choice owner compare prod limit">扱わない。</p>
            <h2 id="a">なぜ要るか</h2>
            <h2 id="b">登場人物</h2>
            <h2 id="c">構造</h2>
            <section data-agent-skills="無い"><h2 id="d">仕組み</h2><a href="https://example.com/">確かめた場所</a></section>
            """,
            toc_html="""<aside class="toc">
              <a href="#a">なぜ要るか</a>
              <a href="#b">登場人物</a>
              <a href="#c">構造</a>
              <a href="#d">仕組み</a>
            </aside>""",
            ending=True,
        ),
        set(),
    ),
    (
        "goals",
        page(
            """
            <p data-fig-skip="what need cast resume struct branch choice owner compare prod limit">扱わない。</p>
            <h2 id="a">なぜ要るか</h2>
            <h2 id="b">登場人物</h2>
            <h2 id="c">構造</h2>
            <section data-agent-skills="無い"><h2 id="d">仕組み</h2><a href="https://example.com/">確かめた場所</a></section>
            """,
            toc_html="""<aside class="toc">
              <a href="#a">なぜ要るか</a>
              <a href="#b">登場人物</a>
              <a href="#c">構造</a>
              <a href="#d">仕組み</a>
            </aside>""",
            ending=True,
        ),
        {"goals"},
    ),
    (
        "early-detail",
        page(
            """
            <ol data-goals><li>何か</li><li>何ができるか</li></ol>
            <p data-fig-skip="what need cast resume struct branch choice owner compare prod limit">扱わない。</p>
            <h2 id="a">なぜ要るか</h2>
            <pre><code>step.run("load")</code></pre>
            <h2 id="b">登場人物</h2>
            <h2 id="c">仕組み</h2>
            <section data-agent-skills="無い"><h2 id="d">構造</h2><a href="https://example.com/">確かめた場所</a></section>
            """,
            toc_html="""<aside class="toc">
              <a href="#a">なぜ要るか</a>
              <a href="#b">登場人物</a>
              <a href="#c">仕組み</a>
              <a href="#d">構造</a>
            </aside>""",
            ending=True,
        ),
        {"early-detail"},
    ),
    (
        "motion-fig",
        page(
            """
            <h2 id="why">なぜ要るか</h2>
            <figure data-fig="resume">
              <div class="row"><div class="box">step</div><div class="box">step</div></div>
            </figure>
            """,
        ),
        {"motion-fig"},
    ),
    (
        "responsive",
        page(
            """
            <h2 id="why">なぜ要るか</h2>
            <figure><svg width="800" height="200"><rect x="0" y="0" width="10" height="10"/></svg></figure>
            <table><tr><td>a</td></tr></table>
            <p><code>step.waitForEvent("wait-for-cancellation")</code></p>
            """,
            "figure { overflow-x: auto; } .wide { min-width: 560px; }",
        ),
        {"responsive"},
    ),
    (
        "volume",
        page(
            """
            <ol data-goals><li>一</li><li>二</li><li>三</li><li>四</li><li>五</li><li>六</li></ol>
            <p data-fig-skip="what need cast resume struct branch">扱わない。</p>
            <h2 id="a">送る側と受け取る側を分けて部品を組み合わせるための通信の仕組みである</h2>
            <p>"""
            + "あ" * 700
            + """</p>
            <h2 id="b">登場人物</h2>
            <h2 id="c">構造</h2>
            <section data-agent-skills="無い"><h2 id="d">公式 skill</h2><a href="https://example.com/">確かめた場所</a></section>
            """,
            toc_html="""<aside class="toc">
              <a href="#a">送る側と受け取る側を分けて部品を組み合わせるための通信の仕組みである</a>
              <a href="#b">登場人物</a>
              <a href="#c">構造</a>
              <a href="#d">公式 skill</a>
            </aside>""",
            ending=True,
        ),
        {"volume"},
    ),
    (
        "endings",
        page(
            """
            <ol data-goals><li>何か</li><li>何ができるか</li></ol>
            <p data-fig-skip="what need cast resume struct branch">扱わない。</p>
            <h2 id="a">なぜ要るか</h2><p><dfn>node</dfn> は処理の単位である。</p>
            <h2 id="b">登場人物</h2>
            <h2 id="c">構造</h2>
            <section data-agent-skills="無い"><h2 id="d">公式 skill</h2><a href="https://example.com/">確かめた場所</a>
            <h3>チェックリスト</h3><h3>確かめられなかったこと</h3><h3>確認クイズ</h3></section>
            """,
            toc_html="""<aside class="toc">
              <a href="#a">なぜ要るか</a>
              <a href="#b">登場人物</a>
              <a href="#c">構造</a>
              <a href="#d">公式 skill</a>
            </aside>""",
            scope=SCOPE_HTML,
        ),
        {"endings"},
    ),
    (
        "scope",
        page(
            """
            <ol data-goals><li>何か</li><li>何ができるか</li></ol>
            <p data-fig-skip="what need cast resume struct branch">扱わない。</p>
            <h2 id="a">なぜ要るか</h2><p><dfn>node</dfn> は処理の単位である。</p>
            <h2 id="b">登場人物</h2>
            <h2 id="c">構造</h2>
            <section data-agent-skills="無い"><h2 id="d">公式 skill</h2><a href="https://example.com/">確かめた場所</a></section>
            """,
            toc_html="""<aside class="toc">
              <a href="#a">なぜ要るか</a>
              <a href="#b">登場人物</a>
              <a href="#c">構造</a>
              <a href="#d">公式 skill</a>
            </aside>""",
            ending=True,
            scope='<details open data-scope><summary>対象と版</summary></details>',
        ),
        {"scope"},
    ),
    (
        "terms",
        page(
            """
            <ol data-goals><li>何か</li><li>何ができるか</li></ol>
            <p data-fig-skip="what need cast resume struct branch">扱わない。</p>
            <h2 id="a">なぜ要るか</h2>
            <p><dfn>node</dfn>、<dfn>topic</dfn>、<dfn>message</dfn>、<dfn>callback</dfn> を定義する。</p>
            <h2 id="b">登場人物</h2>
            <h2 id="c">構造</h2>
            <section data-agent-skills="無い"><h2 id="d">公式 skill</h2><a href="https://example.com/">確かめた場所</a></section>
            """,
            toc_html="""<aside class="toc">
              <a href="#a">なぜ要るか</a>
              <a href="#b">登場人物</a>
              <a href="#c">構造</a>
              <a href="#d">公式 skill</a>
            </aside>""",
            ending=True,
        ),
        {"terms"},
    ),
    (
        "agent-skills",
        page(
            """
            <ol data-goals><li>何か</li><li>何ができるか</li></ol>
            <p data-fig-skip="what need cast resume struct branch choice owner compare prod limit">扱わない。</p>
            <h2 id="a">なぜ要るか</h2>
            <h2 id="b">登場人物</h2>
            <h2 id="c">構造</h2>
            <section data-agent-skills="たぶんある"><h2 id="d">公式 skill</h2></section>
            """,
            toc_html="""<aside class="toc">
              <a href="#a">なぜ要るか</a>
              <a href="#b">登場人物</a>
              <a href="#c">構造</a>
              <a href="#d">公式 skill</a>
            </aside>""",
            ending=True,
        ),
        {"agent-skills"},
    ),
]


def ids_of(findings: list[str]) -> set[str]:
    return {item.split(":", 1)[0] for item in findings}


def run_self_test() -> int:
    failed = False
    for name, html, expected in CASES:
        got = ids_of(check_html(html))
        if got != expected:
            failed = True
            print(f"{name}: expected {sorted(expected)} got {sorted(got)}", file=sys.stderr)
            for item in check_html(html):
                print(f"  {item}", file=sys.stderr)
    hedge_html = page(
        "<h2 id=\"why\">なぜ要るか</h2><p>slot ができる。</p>"
        "<details><summary>出典</summary><p>「Normally, the slot is created. It is removed."
        " / A key (usually a primary key) is used.」</p></details>"
    )
    hedge_expected = [
        ("なぜ要るか", "Normally, the slot is created."),
        ("なぜ要るか", "A key (usually a primary key) is used."),
    ]
    if hedged_quotes(hedge_html) != hedge_expected:
        failed = True
        print(f"hedge: got {hedged_quotes(hedge_html)}", file=sys.stderr)
    split_html = page(
        "<h2 id=\"why\">なぜ要るか</h2><p>slot ができる。</p>"
        "<details><summary>出典</summary><p>「The slot ... should be dropped, e.g. by hand, i.e. with SQL.」</p>"
        "<p>「This parameter can only be set at server start.」</p></details>"
    )
    split_expected = [("なぜ要るか", "The slot ... should be dropped, e.g. by hand, i.e. with SQL.")]
    if hedged_quotes(split_html) != split_expected:
        failed = True
        print(f"hedge-split: got {hedged_quotes(split_html)}", file=sys.stderr)
    prefix_html = page(
        "<h2 id=\"why\">なぜ要るか</h2><p>slot ができる。</p>"
        "<details><summary>出典</summary><ul>"
        "<li><a href=\"https://example.com/a\">29.6 Conflicts</a> A conflict must be resolved by hand.</li>"
        "<li><a href=\"https://example.com/b\">同 29.2 Subscription</a> — Normally, the slot is created.</li>"
        "<li>同ページ: <q>WAL may be retained.</q>（補足）</li>"
        "<li><blockquote>It is kept. [...] So it should be dropped.</blockquote></li>"
        "<li>「… The slot can be reused.」</li>"
        "</ul></details>"
    )
    prefix_expected = [
        ("なぜ要るか", "A conflict must be resolved by hand."),
        ("なぜ要るか", "Normally, the slot is created."),
        ("なぜ要るか", "WAL may be retained."),
        ("なぜ要るか", "So it should be dropped."),
        ("なぜ要るか", "The slot can be reused."),
    ]
    if hedged_quotes(prefix_html) != prefix_expected:
        failed = True
        print(f"hedge-prefix: got {hedged_quotes(prefix_html)}", file=sys.stderr)
    if failed:
        return 1
    print("self-test ok")
    return 0

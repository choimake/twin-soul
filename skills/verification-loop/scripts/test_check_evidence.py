"""check_evidence.py のテスト。実行: python3 -m unittest discover -s skills/verification-loop/scripts"""

from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import check_evidence  # noqa: E402

SCORECARD = """## スコアカード

### 基準ごとの採点

| 基準 | スコア (0.0–1.0) | 根拠 |
| ---- | ---- | ---- |
| C1 | 1.0 | 下の表 |

### 根拠

| 基準 | 場所 | 引用 |
| ---- | ---- | ---- |
{rows}

### 総合

- **判定**: 合格
"""


def run_check(round_dir: Path, repo: Path) -> tuple[int, str]:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = check_evidence.check(round_dir, repo)
    return code, buf.getvalue()


class CheckTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name) / "repo"
        self.round = Path(self.tmp.name) / "round-1"
        (self.repo / "src").mkdir(parents=True)
        (self.round / "commands").mkdir(parents=True)
        (self.repo / "src" / "app.py").write_text(
            "def a():\n    return 1\n\n\ndef b():\n    return 'x | y'\n", encoding="utf-8"
        )

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def write_scorecard(self, rows: str) -> None:
        (self.round / "scorecard.md").write_text(SCORECARD.format(rows=rows), encoding="utf-8")

    def test_quote_on_cited_line_passes(self) -> None:
        self.write_scorecard("| C1 | src/app.py:2 | `return 1` |")
        code, out = run_check(self.round, self.repo)
        self.assertEqual(code, 0, out)

    def test_quote_within_tolerance_passes(self) -> None:
        self.write_scorecard("| C1 | src/app.py:4 | `def b():` |")
        code, out = run_check(self.round, self.repo)
        self.assertEqual(code, 0, out)

    def test_quote_outside_tolerance_fails(self) -> None:
        self.write_scorecard("| C1 | src/app.py:1 | `return 'x` |")
        code, out = run_check(self.round, self.repo)
        self.assertEqual(code, 1)
        self.assertIn("引用が 1±2 行に無い", out)

    def test_escaped_pipe_in_quote(self) -> None:
        self.write_scorecard("| C1 | src/app.py:6 | `'x \\| y'` |")
        code, out = run_check(self.round, self.repo)
        self.assertEqual(code, 0, out)

    def test_missing_file_fails(self) -> None:
        self.write_scorecard("| C1 | src/none.py:1 | `x` |")
        code, out = run_check(self.round, self.repo)
        self.assertEqual(code, 1)
        self.assertIn("ファイルが無い", out)

    def test_line_out_of_range_fails(self) -> None:
        self.write_scorecard("| C1 | src/app.py:99 | `x` |")
        code, out = run_check(self.round, self.repo)
        self.assertEqual(code, 1)
        self.assertIn("行が範囲外", out)

    def test_empty_evidence_table_fails(self) -> None:
        self.write_scorecard("")
        code, out = run_check(self.round, self.repo)
        self.assertEqual(code, 1)
        self.assertIn("根拠の表が無い", out)

    def test_missing_scorecard_fails(self) -> None:
        code, out = run_check(self.round, self.repo)
        self.assertEqual(code, 1)
        self.assertIn("スコアカードが無い", out)

    def test_command_evidence_passes_with_quote_in_log(self) -> None:
        (self.round / "commands" / "test.log").write_text("Ran 3 tests\nOK\n", encoding="utf-8")
        (self.round / "commands" / "test.exit").write_text("0\n", encoding="utf-8")
        self.write_scorecard("| C1 | cmd:test | `Ran 3 tests` |")
        code, out = run_check(self.round, self.repo)
        self.assertEqual(code, 0, out)

    def test_command_evidence_without_record_fails(self) -> None:
        self.write_scorecard("| C1 | cmd:lint | `ok` |")
        code, out = run_check(self.round, self.repo)
        self.assertEqual(code, 1)
        self.assertIn("記録が無い", out)

    def test_command_quote_not_in_log_fails(self) -> None:
        (self.round / "commands" / "test.log").write_text("FAILED\n", encoding="utf-8")
        (self.round / "commands" / "test.exit").write_text("0\n", encoding="utf-8")
        self.write_scorecard("| C1 | cmd:test | `OK` |")
        code, out = run_check(self.round, self.repo)
        self.assertEqual(code, 1)
        self.assertIn("引用がログに無い", out)

    def test_nonzero_exit_of_cited_command_fails(self) -> None:
        (self.round / "commands" / "build.log").write_text("error\n", encoding="utf-8")
        (self.round / "commands" / "build.exit").write_text("2\n", encoding="utf-8")
        self.write_scorecard("| C1 | cmd:build | `error` |")
        code, out = run_check(self.round, self.repo)
        self.assertEqual(code, 1)
        self.assertIn("NG cmd:build 根拠に挙げたコマンドの終了コード 2", out)

    def test_nonzero_exit_of_uncited_command_is_only_reported(self) -> None:
        (self.round / "commands" / "pre-grep.log").write_text("", encoding="utf-8")
        (self.round / "commands" / "pre-grep.exit").write_text("1\n", encoding="utf-8")
        self.write_scorecard("| C1 | src/app.py:2 | `return 1` |")
        code, out = run_check(self.round, self.repo)
        self.assertEqual(code, 0, out)
        self.assertIn("参考 cmd:pre-grep 終了コード 1", out)

    def test_red_probe_failing_is_expected(self) -> None:
        (self.round / "commands" / "red-1.log").write_text("FAILED\n", encoding="utf-8")
        (self.round / "commands" / "red-1.exit").write_text("1\n", encoding="utf-8")
        self.write_scorecard("| C1 | cmd:red-1 | `FAILED` |")
        code, out = run_check(self.round, self.repo)
        self.assertEqual(code, 0, out)

    def test_red_probe_passing_fails(self) -> None:
        (self.round / "commands" / "red-1.log").write_text("OK\n", encoding="utf-8")
        (self.round / "commands" / "red-1.exit").write_text("0\n", encoding="utf-8")
        self.write_scorecard("| C1 | src/app.py:2 | `return 1` |")
        code, out = run_check(self.round, self.repo)
        self.assertEqual(code, 1)
        self.assertIn("実装を戻したのにテストが落ちなかった", out)

    def test_empty_output_is_flagged(self) -> None:
        (self.round / "commands" / "diff.log").write_text("", encoding="utf-8")
        (self.round / "commands" / "diff.exit").write_text("0\n", encoding="utf-8")
        self.write_scorecard("| C1 | cmd:diff |  |")
        code, out = run_check(self.round, self.repo)
        self.assertEqual(code, 0, out)
        self.assertIn("cmd:diff 出力が空", out)


class RunTest(unittest.TestCase):
    def test_records_output_and_exit_code(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            round_dir = Path(tmp)
            with contextlib.redirect_stdout(io.StringIO()):
                code = check_evidence.main(
                    ["run", "--round-dir", tmp, "--name", "t", "--", sys.executable, "-c", "print('hi'); raise SystemExit(3)"]
                )
            self.assertEqual(code, 3)
            self.assertEqual((round_dir / "commands" / "t.exit").read_text().strip(), "3")
            self.assertIn("hi", (round_dir / "commands" / "t.log").read_text())

    def test_rejects_unsafe_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with contextlib.redirect_stderr(io.StringIO()):
                code = check_evidence.main(["run", "--round-dir", tmp, "--name", "../x", "--", "true"])
            self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()

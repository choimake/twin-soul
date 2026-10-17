"""geometry.py のテスト。実行: python3 -I -m unittest discover -s skills/tech-intro/scripts"""

from __future__ import annotations

import unittest

from geometry import cubic, densify, path_points, point_inside, text_width


class PathPointsTest(unittest.TestCase):
    def test_absolute_line_is_densified_per_unit(self) -> None:
        self.assertEqual(path_points("M0 0 L3 0"), [(0, 0), (0, 0), (1, 0), (2, 0), (3, 0)])

    def test_relative_commands_and_implicit_lineto(self) -> None:
        points = path_points("m10 10 5 0 l0 5")
        self.assertEqual(points[0], (10, 10))
        self.assertEqual(points[-1], (15, 15))
        self.assertIn((15, 10), points)

    def test_horizontal_vertical_and_close(self) -> None:
        points = path_points("M0 0 H2 V2 h-2 Z")
        self.assertEqual(points[-1], (0, 0))
        self.assertIn((2, 2), points)
        self.assertIn((0, 2), points)

    def test_cubic_ends_at_end_point(self) -> None:
        points = path_points("M0 0 C0 10 10 10 10 0")
        self.assertEqual(points[-1], (10, 0))
        self.assertGreater(max(y for _, y in points), 7)

    def test_smooth_cubic_reflects_previous_control(self) -> None:
        points = path_points("M0 0 C0 10 10 10 10 0 S20 -10 20 0")
        self.assertEqual(points[-1], (20, 0))
        self.assertLess(min(y for _, y in points), -7)

    def test_scientific_and_compact_numbers(self) -> None:
        self.assertEqual(path_points("M1e1-5L10.5.5")[-1], (10.5, 0.5))

    def test_unsupported_commands_raise(self) -> None:
        for d in ("M0 0 Q5 5 10 0", "M0 0 A5 5 0 0 1 10 0", "M0 0 T5 5"):
            with self.subTest(d=d), self.assertRaises(ValueError):
                path_points(d)

    def test_missing_number_raises(self) -> None:
        with self.assertRaises(ValueError):
            path_points("M0")


class SampleTest(unittest.TestCase):
    def test_cubic_has_25_samples_from_start_to_end(self) -> None:
        samples = cubic((0, 0), (0, 1), (1, 1), (1, 0))
        self.assertEqual(len(samples), 25)
        self.assertEqual(samples[0], (0, 0))
        self.assertEqual(samples[-1], (1, 0))

    def test_cubic_midpoint_uses_bernstein_weights(self) -> None:
        # t = 0.5 は 25 点中の 12 番目（12 / 24）。重みは u^3, 3u^2t, 3ut^2, t^3 = 1/8, 3/8, 3/8, 1/8
        # x = (0 + 3*8 + 3*0 + 8) / 8 = 4、y = (0 + 3*0 + 3*8 + 8) / 8 = 4
        samples = cubic((0, 0), (8, 0), (0, 8), (8, 8))
        self.assertAlmostEqual(samples[12][0], 4)
        self.assertAlmostEqual(samples[12][1], 4)

    def test_densify_steps_are_at_most_one_unit(self) -> None:
        dense = densify([(0, 0), (0, 4.5)])
        gaps = [abs(b[1] - a[1]) for a, b in zip(dense, dense[1:])]
        self.assertEqual(dense[-1], (0, 4.5))
        self.assertTrue(all(gap <= 1.125 for gap in gaps), gaps)

    def test_densify_keeps_single_point(self) -> None:
        self.assertEqual(densify([(1, 2)]), [(1, 2)])


class PointInsideTest(unittest.TestCase):
    def test_point_inside_is_strict(self) -> None:
        interior = (0.0, 0.0, 10.0, 10.0)
        self.assertTrue(point_inside(5, 5, interior))
        self.assertFalse(point_inside(0, 5, interior))
        self.assertFalse(point_inside(5, 11, interior))


class TextWidthTest(unittest.TestCase):
    def test_wide_chars_are_full_size_and_others_narrow(self) -> None:
        self.assertEqual(text_width("あア", 10), 20)
        self.assertAlmostEqual(text_width("ab", 10), 12)

    def test_fullwidth_chars_count_as_full_size(self) -> None:
        self.assertEqual(text_width("ＡＢ", 10), 20)

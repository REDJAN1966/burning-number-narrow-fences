"""Repository tests. Run from this directory: python -m unittest -v"""

import unittest

from verify_figure import (
    check_fire_spread,
    check_row_coverage,
    construct_strip,
    parameter_grid,
    sampled_cases,
    verify_case,
)


class FenceCoverageTests(unittest.TestCase):
    def test_exhaustive_small_grid(self):
        cases = list(parameter_grid(max_p=8, max_extra=7))
        self.assertEqual(len(set(cases)), 352)
        for p, h, k in cases:
            with self.subTest(p=p, h=h, k=k):
                verify_case(p, h, k)

    def test_seeded_random_grid(self):
        cases = sampled_cases(count=300, seed=42, max_p=12, max_extra=15)
        self.assertEqual(len(set(cases)), 300)
        for p, h, k in cases:
            with self.subTest(p=p, h=h, k=k):
                verify_case(p, h, k)

    def test_smallest_cases_and_figure_width(self):
        self.assertEqual(verify_case(1, 1, 4), (9, 3))
        self.assertEqual(verify_case(1, 2, 4), (5, 5))
        self.assertEqual(verify_case(3, 3, 10), (55, 7))

    def test_invalid_parameters(self):
        for params in [(0, 0, 1), (2, 1, 7), (2, 5, 7), (2, 2, 6)]:
            with self.subTest(params=params), self.assertRaises(ValueError):
                verify_case(*params)
        with self.assertRaises(ValueError):
            sampled_cases(count=3, seed=42, max_p=1, max_extra=0)

    def test_both_checks_detect_one_missing_vertex(self):
        # Move the final, radius-zero ignition one column left in Figure 1.
        # Its original vertex is the only one that will be left unburned.
        _, _, sources = construct_strip(3, 3, 10)
        self.assertEqual(sources[-1], (10, 13, 0, 0))
        sources[-1] = (10, 12, 0, 0)
        for check in (check_row_coverage, check_fire_spread):
            with self.subTest(check=check.__name__):
                with self.assertRaisesRegex(ValueError, r"uncovered vertex \(13, 0\)"):
                    check(sources, 55, 7)


if __name__ == "__main__":
    unittest.main()

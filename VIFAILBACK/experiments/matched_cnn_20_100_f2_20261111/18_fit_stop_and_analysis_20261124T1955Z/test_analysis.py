"""Synthetic invariants for the independent saved-score arithmetic."""
import importlib.util
from pathlib import Path
import unittest
import numpy as np

spec = importlib.util.spec_from_file_location("analysis", Path(__file__).with_name("analyze_completed.py"))
analysis = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analysis)


class MetricTests(unittest.TestCase):
    def test_perfect_and_constant_scores_have_known_macro_ap(self):
        y = np.asarray([0, 1, 1, 1])
        self.assertEqual(analysis.scores(y, y.astype(float))["macro_AP"], 1.)
        self.assertEqual(analysis.scores(y, np.full(4, .75))["macro_AP"], .5)

    def test_identical_paired_scores_have_zero_width_delta_interval(self):
        y = np.asarray([0, 1, 0, 1])
        p = np.asarray([.1, .6, .3, .9])
        interval, valid = analysis.independent_interval(y, p, p, np.asarray([0, 0, 1, 1]), draws=20)
        self.assertEqual(interval, [0., 0.])
        self.assertEqual(valid, 20)


if __name__ == "__main__":
    unittest.main()

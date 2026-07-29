from __future__ import annotations

import unittest

import numpy as np

from src.evaluation import (
    classification_metrics,
    selective_table,
    wilson_interval,
)


class EvaluationTests(unittest.TestCase):
    def test_classification_metrics_are_exact_for_perfect_predictions(self) -> None:
        target = np.array([0, 0, 1, 1])
        probabilities = np.array([0.05, 0.20, 0.80, 0.95])
        result = classification_metrics(target, probabilities)
        self.assertEqual(result["balanced_accuracy"], 1.0)
        self.assertEqual(result["sensitivity"], 1.0)
        self.assertEqual(result["specificity"], 1.0)

    def test_wilson_interval_contains_observed_rate(self) -> None:
        low, high = wilson_interval(20, 100)
        self.assertLess(low, 0.20)
        self.assertGreater(high, 0.20)

    def test_selective_threshold_is_learned_from_reference_only(self) -> None:
        reference_y = np.array([0, 0, 1, 1, 0])
        reference_p = np.array([0.05, 0.45, 0.55, 0.95, 0.20])
        test_y = np.array([0, 1, 0, 1])
        test_p = np.array([0.10, 0.60, 0.30, 0.90])
        table = selective_table(reference_y, reference_p, test_y, test_p)
        row = table.loc[table["target_coverage"] == 0.80].iloc[0]
        expected = np.quantile(
            np.maximum(reference_p, 1.0 - reference_p),
            0.20,
            method="higher",
        )
        self.assertEqual(row["confidence_threshold"], expected)
        self.assertIn("development_error_ci_high", table.columns)
        self.assertIn("error_rate_ci_high", table.columns)


if __name__ == "__main__":
    unittest.main()

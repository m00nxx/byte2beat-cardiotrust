from __future__ import annotations

import unittest

from src.run_experiment import format_metric_interval_row


class ReportingTests(unittest.TestCase):
    def test_ece_interval_is_not_reported(self) -> None:
        row = format_metric_interval_row("ece_10", 0.0026, 0.0045, 0.0132)
        self.assertEqual(row, "| ece_10 | 0.0026 | not reported |")

    def test_other_metric_interval_is_reported(self) -> None:
        row = format_metric_interval_row("brier", 0.1806, 0.1771, 0.1841)
        self.assertEqual(row, "| brier | 0.1806 | [0.1771, 0.1841] |")


if __name__ == "__main__":
    unittest.main()

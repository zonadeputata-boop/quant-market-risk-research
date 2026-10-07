import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/run_week16_implied_realized.py"
SPEC = importlib.util.spec_from_file_location("week16", SCRIPT)
week16 = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = week16
SPEC.loader.exec_module(week16)


class Week16Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.metrics = week16.load_metrics()

    def test_published_gap_reconciles(self):
        self.assertAlmostEqual(week16.reported_gap(self.metrics), 4.30, places=9)
        self.assertAlmostEqual(
            week16.reported_gap(self.metrics),
            self.metrics["avg_implied_realized_gap"].value,
            places=9,
        )

    def test_error_reduction_calculation(self):
        reduction = week16.relative_error_reduction(5.27, 3.58)
        self.assertAlmostEqual(reduction, 0.3206831119544592, places=12)

    def test_raw_vix_has_largest_reported_average_error(self):
        reported = [
            self.metrics["vcr_average_abs_error"].value,
            self.metrics["raw_vix_average_abs_error"].value,
            self.metrics["recent_vol_average_abs_error"].value,
            self.metrics["mr_average_abs_error"].value,
        ]
        self.assertEqual(max(reported), self.metrics["raw_vix_average_abs_error"].value)

    def test_validation_passes(self):
        week16.validate_metrics(self.metrics)


if __name__ == "__main__":
    unittest.main()

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/run_week17_vix_futures.py"
SPEC = importlib.util.spec_from_file_location("week17", SCRIPT)
week17 = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = week17
SPEC.loader.exec_module(week17)


class Week17Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.metrics = week17.load_metrics()
        cls.scenarios = week17.load_scenarios()

    def test_convergence_example_return(self):
        result = week17.convergence_return(20.0, 15.0)
        self.assertAlmostEqual(result, -0.25, places=12)

    def test_frequency_inequalities_are_preserved(self):
        self.assertEqual(self.metrics["contango_frequency_lower_bound"].comparison, "greater_than")
        self.assertEqual(self.metrics["backwardation_frequency_upper_bound"].comparison, "less_than")
        self.assertEqual(self.metrics["contango_frequency_lower_bound"].period_end, "2022-07-26")

    def test_current_dashboard_snapshot(self):
        expected = {
            "short_term_index_1m_return": -14.17,
            "short_term_index_ytd_return": -30.08,
            "short_term_index_12m_return": -46.14,
        }
        for key, value in expected.items():
            self.assertAlmostEqual(self.metrics[key].value, value, places=9)
            self.assertEqual(self.metrics[key].as_of, "2026-09-16")

    def test_curve_shapes(self):
        contango = [self.scenarios["contango_curve"][m].value for m in ("M1", "M2", "M3")]
        backwardation = [self.scenarios["backwardation_curve"][m].value for m in ("M1", "M2", "M3")]
        self.assertTrue(contango[0] < contango[1] < contango[2])
        self.assertTrue(backwardation[0] > backwardation[1] > backwardation[2])

    def test_validation_passes(self):
        week17.validate_inputs(self.metrics, self.scenarios)


if __name__ == "__main__":
    unittest.main()

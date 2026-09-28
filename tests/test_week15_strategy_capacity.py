import importlib.util
import math
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_week15_strategy_capacity.py"
SPEC = importlib.util.spec_from_file_location("week15_capacity", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class StrategyCapacityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.assumptions = MODULE.load_assumptions(
            ROOT / "data" / "raw" / "week15_model_assumptions.csv"
        )

    def test_annual_turnover_is_10_point_4(self):
        self.assertAlmostEqual(MODULE.annual_turnover(self.assumptions), 10.4)

    def test_impact_scales_with_square_root_of_trade_size(self):
        base = MODULE.market_impact_rate(1, 100, 0.02, 0.5)
        four_times = MODULE.market_impact_rate(4, 100, 0.02, 0.5)
        self.assertAlmostEqual(four_times / base, 2.0)

    def test_10m_case(self):
        row = MODULE.capacity_row(10_000_000, self.assumptions)
        self.assertAlmostEqual(row["participation_rate"], 0.004)
        self.assertAlmostEqual(row["net_alpha_annual"], 0.028221, places=5)

    def test_250m_case_is_near_break_even(self):
        row = MODULE.capacity_row(250_000_000, self.assumptions)
        self.assertAlmostEqual(row["participation_rate"], 0.10)
        self.assertGreater(row["net_alpha_annual"], 0)
        self.assertLess(row["net_alpha_annual"], 0.002)

    def test_500m_case_has_negative_net_alpha(self):
        row = MODULE.capacity_row(500_000_000, self.assumptions)
        self.assertLess(row["net_alpha_annual"], 0)
        self.assertAlmostEqual(row["net_alpha_annual"], -0.011710, places=5)

    def test_economic_break_even_is_about_280m(self):
        value = MODULE.economic_break_even_aum(self.assumptions)
        self.assertTrue(math.isclose(value / 1_000_000, 279.88, rel_tol=1e-3))
        row = MODULE.capacity_row(value, self.assumptions)
        self.assertAlmostEqual(row["net_alpha_annual"], 0.0, places=10)

    def test_participation_policy_binds_at_250m(self):
        value = MODULE.participation_limit_aum(self.assumptions)
        self.assertEqual(value, 250_000_000)

    def test_higher_volatility_reduces_capacity(self):
        stressed = dict(self.assumptions)
        stressed["daily_volatility"] = 0.03
        self.assertLess(
            MODULE.economic_break_even_aum(stressed),
            MODULE.economic_break_even_aum(self.assumptions),
        )

    def test_lower_gross_alpha_reduces_capacity(self):
        stressed = dict(self.assumptions)
        stressed["gross_alpha_annual"] = 0.03
        self.assertLess(
            MODULE.economic_break_even_aum(stressed),
            MODULE.economic_break_even_aum(self.assumptions),
        )


if __name__ == "__main__":
    unittest.main()

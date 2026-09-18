import importlib.util
import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/run_week14_liquidity_spiral.py"
SPEC = importlib.util.spec_from_file_location("week14", SCRIPT)
WEEK14 = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = WEEK14
SPEC.loader.exec_module(WEEK14)


class LiquiditySpiralTests(unittest.TestCase):
    def base(self, sensitivity=0.0):
        return WEEK14.simulate(
            scenario="test", initial_assets=250.0, initial_debt=150.0,
            external_shock=-0.04, maximum_leverage=2.5,
            impact_sensitivity=sensitivity,
        )

    def test_post_shock_balance_sheet(self):
        _, summary = self.base()
        self.assertAlmostEqual(summary["post_shock_assets_before_sales"], 240.0)
        self.assertAlmostEqual(summary["post_shock_equity_before_sales"], 90.0)
        self.assertAlmostEqual(summary["post_shock_leverage_before_sales"], 240.0 / 90.0)

    def test_zero_impact_matches_closed_form_sale(self):
        states, summary = self.base(0.0)
        self.assertEqual(len(states), 1)
        self.assertAlmostEqual(summary["total_forced_sale"], 15.0)
        self.assertAlmostEqual(summary["final_assets"], 225.0)
        self.assertAlmostEqual(summary["final_debt"], 135.0)
        self.assertAlmostEqual(summary["final_leverage"], 2.5)

    def test_sale_does_not_change_equity_before_impact(self):
        assets, debt = 240.0, 150.0
        sale = WEEK14.required_sale(assets, debt, 2.5)
        self.assertAlmostEqual((assets - sale) - (debt - sale), assets - debt)

    def test_stronger_feedback_requires_more_sales(self):
        _, lower = self.base(0.2)
        _, stronger = self.base(0.4)
        self.assertGreater(stronger["total_forced_sale"], lower["total_forced_sale"])
        self.assertGreater(stronger["equity_loss_pct"], lower["equity_loss_pct"])

    def test_all_scenarios_converge_to_limit(self):
        for sensitivity in (0.0, 0.2, 0.4):
            _, summary = self.base(sensitivity)
            self.assertLessEqual(summary["final_leverage"], 2.5 + 1e-7)

    def test_expected_published_values(self):
        _, lower = self.base(0.2)
        _, stronger = self.base(0.4)
        self.assertAlmostEqual(lower["total_forced_sale"], 20.9891138467, places=6)
        self.assertAlmostEqual(stronger["total_forced_sale"], 35.3413148159, places=6)
        self.assertAlmostEqual(stronger["cumulative_impact_return"], -0.0625, places=6)

    def test_invalid_inputs_fail(self):
        with self.assertRaises(ValueError):
            WEEK14.simulate(
                scenario="bad", initial_assets=100, initial_debt=100,
                external_shock=-0.04, maximum_leverage=2.5,
                impact_sensitivity=0.2,
            )
        with self.assertRaises(ValueError):
            WEEK14.required_sale(100, 50, 1.0)

    def test_case_study_source_is_complete(self):
        data = WEEK14.validate_case_study(ROOT / "data/raw/week14_case_study.csv")
        self.assertEqual(len(data), 3)
        self.assertTrue(data["source_url"].str.startswith("https://").all())


if __name__ == "__main__":
    unittest.main()

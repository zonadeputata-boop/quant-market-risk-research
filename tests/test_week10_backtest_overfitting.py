from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

import numpy as np


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "run_week10_backtest_overfitting.py"
)
SPEC = importlib.util.spec_from_file_location("week10", SCRIPT_PATH)
week10 = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(week10)


class Week10Tests(unittest.TestCase):
    def test_sharpe_conversion_matches_t_identity(self) -> None:
        t_stat = np.array([0.0, 1.0, -2.0])
        expected = t_stat * np.sqrt(week10.TRADING_DAYS / week10.TRAIN_DAYS)
        np.testing.assert_allclose(
            week10.annualized_sharpe_from_t(t_stat, week10.TRAIN_DAYS), expected
        )

    def test_independent_familywise_error_formula(self) -> None:
        n_trials = 100
        expected = 1.0 - (1.0 - week10.ALPHA) ** n_trials
        self.assertGreater(expected, 0.99)

    def test_selection_inflates_is_but_not_independent_oos(self) -> None:
        summary, _ = week10.run_simulation(
            trial_counts=(1, 10, 100), experiments=6_000, seed=314159
        )
        best_is = summary["median_best_is_sharpe"].to_numpy()
        self.assertTrue(np.all(np.diff(best_is) > 0.0))
        self.assertLess(np.max(np.abs(summary["median_selected_oos_sharpe"])), 0.05)

    def test_naive_testing_loses_familywise_control(self) -> None:
        summary, _ = week10.run_simulation(
            trial_counts=(1, 100), experiments=8_000, seed=271828
        )
        one_trial = summary.loc[summary["n_trials"] == 1].iloc[0]
        many_trials = summary.loc[summary["n_trials"] == 100].iloc[0]
        self.assertTrue(0.035 < one_trial["simulated_naive_fwer"] < 0.065)
        self.assertGreater(many_trials["simulated_naive_fwer"], 0.99)

    def test_bonferroni_controls_familywise_error_in_simulation(self) -> None:
        summary, _ = week10.run_simulation(
            trial_counts=(1, 10, 100, 500), experiments=8_000, seed=161803
        )
        self.assertLess(summary["simulated_bonferroni_fwer"].max(), 0.065)

    def test_oos_sign_is_unpredictable_under_the_null(self) -> None:
        summary, _ = week10.run_simulation(
            trial_counts=(10, 100, 500), experiments=8_000, seed=141421
        )
        probabilities = summary["prob_selected_oos_sharpe_below_zero"]
        self.assertTrue(((probabilities > 0.47) & (probabilities < 0.53)).all())


if __name__ == "__main__":
    unittest.main()

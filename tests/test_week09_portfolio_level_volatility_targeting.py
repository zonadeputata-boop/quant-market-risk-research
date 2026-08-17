"""Focused tests for the Week 09 portfolio targeting mechanics."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import numpy as np
import pandas as pd


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "run_week09_portfolio_level_volatility_targeting.py"
)
SPEC = importlib.util.spec_from_file_location("week09", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
WEEK09 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = WEEK09
SPEC.loader.exec_module(WEEK09)


def test_portfolio_volatility_uses_covariance_terms() -> None:
    exposure = np.array([0.5, 0.5])
    low_correlation = np.array([[0.01, 0.0], [0.0, 0.01]])
    high_correlation = np.array([[0.01, 0.009], [0.009, 0.01]])
    assert WEEK09.portfolio_volatility(exposure, high_correlation) > WEEK09.portfolio_volatility(
        exposure, low_correlation
    )


def test_target_exposure_respects_portfolio_and_gross_caps() -> None:
    volatility = np.array([0.18, 0.22, 0.14, 0.15, 0.12, 0.04])
    correlation = np.full((6, 6), 0.35)
    np.fill_diagonal(correlation, 1.0)
    covariance = pd.DataFrame(
        np.outer(volatility, volatility) * correlation,
        index=WEEK09.TICKERS,
        columns=WEEK09.TICKERS,
    )
    state = WEEK09.calculate_target_state(covariance)
    assert state.target_exposure.abs().sum() <= WEEK09.MAX_GROSS_EXPOSURE + 1e-12
    assert state.portfolio_scalar <= WEEK09.MAX_PORTFOLIO_SCALAR
    assert state.target_forecast_volatility > 0


def test_scenario_volatility_rises_with_correlation() -> None:
    scenarios = WEEK09.scenario_table()
    assert scenarios["portfolio_volatility_before_portfolio_scalar"].is_monotonic_increasing
    assert scenarios["uncapped_portfolio_scalar_to_10pct"].is_monotonic_decreasing


def test_day_t_target_does_not_use_day_t_return() -> None:
    rng = np.random.default_rng(17)
    dates = pd.bdate_range("2024-01-02", periods=70)
    returns = pd.DataFrame(
        rng.normal(0.0, 0.01, size=(len(dates), len(WEEK09.TICKERS))),
        index=dates,
        columns=WEEK09.TICKERS,
    )
    target_before, _, _, _, _ = WEEK09.estimate_states(returns)
    first_target_date = target_before.index[0]
    changed = returns.copy()
    changed.loc[first_target_date] = 0.25
    target_after, _, _, _, _ = WEEK09.estimate_states(changed)
    pd.testing.assert_series_equal(
        target_before.loc[first_target_date], target_after.loc[first_target_date]
    )


def test_transaction_cost_is_reconciled_to_turnover() -> None:
    returns = WEEK09.build_demo_returns().iloc[:80]
    target, _, evaluation, covariance_by_date, _ = WEEK09.estimate_states(returns)
    results, _ = WEEK09.backtest_policy(
        evaluation, target, covariance_by_date, policy="daily"
    )
    expected = results["turnover"] * WEEK09.TRANSACTION_COST_BPS / 10_000.0
    np.testing.assert_allclose(results["transaction_cost"], expected, rtol=0, atol=1e-15)
    np.testing.assert_allclose(
        results["net_return"],
        results["gross_return"] - results["transaction_cost"],
        rtol=0,
        atol=1e-15,
    )


def test_base_weights_and_published_scenario_values() -> None:
    assert np.isclose(WEEK09.BASE_WEIGHTS.sum(), 1.0)
    scenarios = WEEK09.scenario_table().set_index("pairwise_correlation")
    expected = {0.10: 0.05, 0.40: 0.0707106781, 0.75: 0.0889756521}
    for correlation, volatility in expected.items():
        assert np.isclose(
            scenarios.loc[correlation, "portfolio_volatility_before_portfolio_scalar"],
            volatility,
            atol=1e-10,
        )

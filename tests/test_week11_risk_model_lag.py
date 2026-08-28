from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_week11_risk_model_lag.py"
SPEC = importlib.util.spec_from_file_location("week11", SCRIPT)
week11 = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = week11
SPEC.loader.exec_module(week11)


def sample_returns(rows: int = 220, seed: int = 11) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    data = rng.normal(0.0, 0.01, size=(rows, len(week11.TICKERS)))
    return pd.DataFrame(
        data,
        index=pd.bdate_range("2020-01-02", periods=rows),
        columns=week11.TICKERS,
    )


def test_weights_sum_to_one() -> None:
    assert np.isclose(week11.WEIGHTS.sum(), 1.0)
    assert (week11.WEIGHTS >= 0).all()


def test_portfolio_volatility_matches_formula() -> None:
    covariance = np.diag([0.0001] * len(week11.TICKERS))
    weights = week11.WEIGHTS.to_numpy()
    expected = np.sqrt(week11.TRADING_DAYS * weights @ covariance @ weights)
    assert np.isclose(week11.portfolio_volatility(covariance, weights), expected)


def test_forecast_at_t_is_invariant_to_future_changes() -> None:
    returns = sample_returns()
    baseline = week11.estimate_forecasts(returns)
    cutoff = returns.index[170]
    changed = returns.copy()
    changed.loc[changed.index > cutoff] *= 50.0
    alternative = week11.estimate_forecasts(changed)
    pd.testing.assert_frame_equal(
        baseline.loc[:cutoff], alternative.loc[:cutoff], check_exact=True
    )


def test_forward_realized_starts_at_t_plus_one() -> None:
    returns = sample_returns(180)
    realized = week11.forward_realized_volatility(returns)
    date = realized.index[0]
    position = returns.index.get_loc(date)
    expected = (
        returns.dot(week11.WEIGHTS)
        .iloc[position + 1 : position + 1 + week11.FORWARD_WINDOW]
        .std(ddof=1)
        * np.sqrt(week11.TRADING_DAYS)
    )
    assert np.isclose(realized.loc[date], expected)


def test_future_outcome_does_not_enter_same_date_forecast() -> None:
    returns = sample_returns(190)
    date = returns.index[150]
    baseline = week11.estimate_forecasts(returns).loc[date]
    changed = returns.copy()
    changed.loc[changed.index > date] = 0.25
    alternative = week11.estimate_forecasts(changed).loc[date]
    pd.testing.assert_series_equal(baseline, alternative, check_exact=True)


def test_covariance_forecasts_are_finite_and_positive() -> None:
    forecasts = week11.estimate_forecasts(sample_returns())
    assert np.isfinite(forecasts.to_numpy()).all()
    assert (forecasts > 0).all().all()


def test_covariance_updates_are_symmetric_and_psd() -> None:
    returns = sample_returns()
    rolling = week11.rolling_covariance(returns.iloc[-63:])
    ewma = week11.rolling_covariance(returns.iloc[:126])
    for row in returns.iloc[126:].to_numpy():
        ewma = week11.update_ewma_covariance(ewma, row)
    for covariance in (rolling, ewma):
        assert np.allclose(covariance, covariance.T)
        assert np.linalg.eigvalsh(covariance).min() >= -1e-12


def test_ewma_half_life_identity() -> None:
    half_life = week11.ewma_half_life()
    assert np.isclose(week11.EWMA_LAMBDA**half_life, 0.5)
    assert 11.1 < half_life < 11.3


def test_shock_selection_respects_exclusion_window() -> None:
    returns = sample_returns(260).dot(week11.WEIGHTS)
    dates, _ = week11.select_shock_events(returns, percentile=0.95, exclusion_days=10)
    positions = sorted(returns.index.get_loc(date) for date in dates)
    assert all(b - a > 10 for a, b in zip(positions, positions[1:]))


def test_packaged_raw_data_quality() -> None:
    prices = week11.load_prices(ROOT / "data" / "raw" / "week11_adjusted_close.csv")
    quality = week11.validate_prices(prices)
    assert quality.rows == 1663
    assert quality.columns == 6
    assert quality.duplicate_dates == 0
    assert quality.missing_values == 0
    assert quality.nonpositive_prices == 0


def test_public_claims_match_saved_outputs() -> None:
    table_dir = ROOT / "reports" / "week_11_risk_model_lag" / "tables"
    metrics = pd.read_csv(table_dir / "forecast_error_metrics.csv", index_col="model")
    shocks = pd.read_csv(table_dir / "shock_response_summary.csv", index_col="model")
    revisions = pd.read_csv(table_dir / "forecast_revision_summary.csv", index_col="model")
    caption = (ROOT / "posts" / "week_11_risk_model_lag" / "caption.md").read_text()
    carousel = (ROOT / "posts" / "week_11_risk_model_lag" / "carousel.md").read_text()
    public_copy = caption + "\n" + carousel

    for model in ["rolling_21", "rolling_63", "rolling_126", "ewma_094"]:
        assert f"{metrics.loc[model, 'mae_vol_points']:.2f}" in public_copy
        assert f"{shocks.loc[model, 'median_revision'] * 100:.1f}%" in public_copy
        assert f"{revisions.loc[model, 'mean_abs_daily_revision'] * 100:.2f}%" in public_copy
    assert "1,516" in public_copy

from pathlib import Path
import importlib.util

import numpy as np
import pandas as pd

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/run_week12_risk_estimate_uncertainty.py"
SPEC = importlib.util.spec_from_file_location("week12", SCRIPT)
M = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(M)


def test_weights_sum_to_one():
    assert np.isclose(M.WEIGHTS.sum(), 1.0)


def test_historical_es_uses_explicit_tail_count_and_dominates_var():
    x = np.linspace(-0.10, 0.05, 63)
    var, es, k = M.historical_es(x)
    assert k == 2
    assert es >= var
    assert M.historical_es(np.linspace(-0.10, 0.05, 252))[2] == 7


def test_circular_block_sample_is_deterministic_and_has_correct_length():
    x = np.arange(11.0)
    a = M.circular_block_sample(x, 4, np.random.default_rng(7))
    b = M.circular_block_sample(x, 4, np.random.default_rng(7))
    assert len(a) == len(x)
    assert np.array_equal(a, b)


def test_bootstrap_interval_is_finite_and_ordered():
    x = np.sin(np.arange(80)) / 100
    result = M.bootstrap_interval(x, block=5, bootstraps=100, seed=3)
    assert all(np.isfinite(list(result.values())))
    assert result["vol_ci_low"] <= result["vol_ci_high"]
    assert result["es_ci_low"] <= result["es_ci_high"]


def test_month_end_estimation_has_no_lookahead():
    idx = pd.bdate_range("2020-01-01", periods=400)
    r = pd.Series(np.arange(400) / 100000, index=idx)
    dates = M.evaluation_dates(r)
    for date in dates:
        end = r.index.get_loc(date)
        assert r.iloc[end - 251:end + 1].index.max() == date


def test_packaged_claims_match_tables():
    table = pd.read_csv(Path(__file__).resolve().parents[1] /
        "reports/week_12_risk_estimate_uncertainty/tables/interval_width_summary.csv")
    row63 = table.loc[table.window == 63].iloc[0]
    row252 = table.loc[table.window == 252].iloc[0]
    assert row63.tail_observations == 2 and row252.tail_observations == 7
    assert round(row63.median_vol_relative_width * 100) == 38
    assert round(row252.median_vol_relative_width * 100) == 30
    assert round(row63.median_es_relative_width * 100) == 45
    assert round(row252.median_es_relative_width * 100) == 44

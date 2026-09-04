"""Week 12: sampling uncertainty in volatility and historical Expected Shortfall.

Run from the repository root:
    python scripts/run_week12_risk_estimate_uncertainty.py
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

TICKERS = ["SPY", "QQQ", "TLT", "GLD", "HYG", "SHY"]
WEIGHTS = pd.Series(1 / len(TICKERS), index=TICKERS, name="weight")
WINDOWS = (63, 252)
ALPHA = 0.975
TRADING_DAYS = 252
BOOTSTRAPS = 2000
BLOCK_LENGTH = 10
SEED = 12026

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data/raw/week12_adjusted_close.csv"
DEFAULT_REPORT = ROOT / "reports/week_12_risk_estimate_uncertainty"


def load_prices(path: Path) -> pd.DataFrame:
    prices = pd.read_csv(path, index_col=0, parse_dates=True).sort_index()
    missing = sorted(set(TICKERS) - set(prices.columns))
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    prices = prices[TICKERS]
    if (not prices.index.is_monotonic_increasing or prices.index.duplicated().any()
            or prices.isna().any().any() or (prices <= 0).any().any()):
        raise ValueError("Price panel failed validity checks")
    return prices


def portfolio_returns(prices: pd.DataFrame) -> pd.Series:
    returns = prices.pct_change(fill_method=None).dropna(how="any")
    return returns.dot(WEIGHTS).rename("portfolio_return")


def annualized_volatility(x: np.ndarray) -> float:
    return float(np.std(x, ddof=1) * np.sqrt(TRADING_DAYS))


def historical_es(x: np.ndarray, alpha: float = ALPHA) -> tuple[float, float, int]:
    """Return positive-loss VaR, ES and tail count using the worst ceil((1-a)n)."""
    losses = -np.asarray(x, dtype=float)
    k = max(1, int(np.ceil((1 - alpha) * len(losses))))
    tail = np.sort(losses)[-k:]
    return float(tail[0]), float(tail.mean()), k


def circular_block_sample(x: np.ndarray, block: int, rng: np.random.Generator) -> np.ndarray:
    """Circular moving-block bootstrap sample with the same length as x."""
    n = len(x)
    starts = rng.integers(0, n, size=int(np.ceil(n / block)))
    offsets = np.arange(block)
    indices = ((starts[:, None] + offsets[None, :]) % n).ravel()[:n]
    return x[indices]


def bootstrap_interval(x: np.ndarray, block: int, bootstraps: int, seed: int) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    vol = np.empty(bootstraps)
    es = np.empty(bootstraps)
    for i in range(bootstraps):
        sample = circular_block_sample(x, block, rng)
        vol[i] = annualized_volatility(sample)
        es[i] = historical_es(sample)[1]
    point_vol = annualized_volatility(x)
    point_es = historical_es(x)[1]
    vlow, vhigh = np.quantile(vol, [0.025, 0.975])
    elow, ehigh = np.quantile(es, [0.025, 0.975])
    return {
        "volatility": point_vol, "vol_ci_low": float(vlow), "vol_ci_high": float(vhigh),
        "vol_relative_width": float((vhigh - vlow) / point_vol),
        "es": point_es, "es_ci_low": float(elow), "es_ci_high": float(ehigh),
        "es_relative_width": float((ehigh - elow) / point_es),
    }


def evaluation_dates(returns: pd.Series) -> pd.DatetimeIndex:
    eligible = returns.iloc[max(WINDOWS) - 1:]
    return eligible.groupby(eligible.index.to_period("M")).apply(lambda s: s.index[-1]).pipe(pd.DatetimeIndex)


def run_analysis(returns: pd.Series, bootstraps: int = BOOTSTRAPS) -> pd.DataFrame:
    rows = []
    dates = evaluation_dates(returns)
    for di, date in enumerate(dates):
        end = returns.index.get_loc(date)
        for window in WINDOWS:
            x = returns.iloc[end - window + 1:end + 1].to_numpy()
            values = bootstrap_interval(x, BLOCK_LENGTH, bootstraps, SEED + 100 * di + window)
            rows.append({"date": date, "window": window, "observations": window,
                         "tail_observations": historical_es(x)[2], "block_length": BLOCK_LENGTH,
                         **values})
    return pd.DataFrame(rows)


def sensitivity_latest(returns: pd.Series, bootstraps: int = BOOTSTRAPS) -> pd.DataFrame:
    rows = []
    for window in WINDOWS:
        x = returns.iloc[-window:].to_numpy()
        for block in (5, 10, 21):
            rows.append({"date": returns.index[-1], "window": window, "block_length": block,
                         **bootstrap_interval(x, block, bootstraps, SEED + window + block)})
    return pd.DataFrame(rows)


def make_figure(panel: pd.DataFrame, output: Path) -> None:
    med = panel.groupby("window")[["vol_relative_width", "es_relative_width"]].median() * 100
    fig, ax = plt.subplots(figsize=(9, 5.2))
    x = np.arange(len(med)); width = .34
    ax.bar(x - width/2, med.vol_relative_width, width, label="Annualized volatility", color="#2C6EA3")
    ax.bar(x + width/2, med.es_relative_width, width, label="97.5% historical ES", color="#C66A3D")
    ax.set_xticks(x, [f"{w}-day window" for w in med.index]); ax.set_ylabel("Median 95% CI width / estimate (%)")
    ax.spines[["top", "right"]].set_visible(False); ax.legend(frameon=False)
    fig.tight_layout(); fig.savefig(output, dpi=180); plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--bootstraps", type=int, default=BOOTSTRAPS)
    args = parser.parse_args()
    prices = load_prices(args.input); returns = portfolio_returns(prices)
    tables = args.report_dir / "tables"; figures = args.report_dir / "figures"
    tables.mkdir(parents=True, exist_ok=True); figures.mkdir(parents=True, exist_ok=True)
    panel = run_analysis(returns, args.bootstraps); sensitivity = sensitivity_latest(returns, args.bootstraps)
    summary = panel.groupby("window").agg(
        evaluation_dates=("date", "count"), tail_observations=("tail_observations", "first"),
        median_vol_relative_width=("vol_relative_width", "median"),
        median_es_relative_width=("es_relative_width", "median"),
        median_volatility=("volatility", "median"), median_es=("es", "median"),
    ).reset_index()
    latest = panel[panel.date == panel.date.max()].copy()
    quality = pd.DataFrame([{"price_rows": len(prices), "return_rows": len(returns),
        "first_date": prices.index.min().date(), "last_date": prices.index.max().date(),
        "duplicate_dates": int(prices.index.duplicated().sum()),
        "missing_values": int(prices.isna().sum().sum()),
        "nonpositive_prices": int((prices <= 0).sum().sum())}])
    panel.to_csv(tables / "monthly_bootstrap_intervals.csv", index=False)
    summary.to_csv(tables / "interval_width_summary.csv", index=False)
    latest.to_csv(tables / "latest_window_snapshot.csv", index=False)
    sensitivity.to_csv(tables / "latest_block_length_sensitivity.csv", index=False)
    quality.to_csv(tables / "data_quality_summary.csv", index=False)
    WEIGHTS.rename_axis("ticker").reset_index().to_csv(tables / "portfolio_weights.csv", index=False)
    make_figure(panel, figures / "week12_interval_widths.png")
    print(summary.to_string(index=False)); print("\nLatest:\n", latest.to_string(index=False))


if __name__ == "__main__":
    main()

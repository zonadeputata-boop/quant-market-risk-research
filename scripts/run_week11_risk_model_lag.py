"""Week 11 research script: Risk-Model Lag.

The analysis compares four covariance estimators for a fixed six-ETF
diagnostic portfolio.  A forecast stamped at close t uses returns through t;
the forward 21-session realized-volatility proxy starts at t+1.

Run from the repository root:

    python scripts/run_week11_risk_model_lag.py
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


TICKERS = ["SPY", "QQQ", "TLT", "GLD", "HYG", "SHY"]
ROLLING_WINDOWS = (21, 63, 126)
EWMA_LAMBDA = 0.94
FORWARD_WINDOW = 21
TRADING_DAYS = 252
SHOCK_PERCENTILE = 0.99
SHOCK_EXCLUSION_DAYS = 10
WEIGHTS = pd.Series(1.0 / len(TICKERS), index=TICKERS, name="weight")

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data" / "raw" / "week11_adjusted_close.csv"
DEFAULT_REPORT_DIR = ROOT / "reports" / "week_11_risk_model_lag"


@dataclass(frozen=True)
class QualitySummary:
    rows: int
    columns: int
    first_date: str
    last_date: str
    duplicate_dates: int
    missing_values: int
    nonpositive_prices: int
    maximum_absolute_return: float


def load_prices(path: Path) -> pd.DataFrame:
    """Load adjusted closes and normalize the date index."""

    prices = pd.read_csv(path, index_col=0, parse_dates=True)
    prices.index.name = "date"
    missing_columns = sorted(set(TICKERS) - set(prices.columns))
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    return prices.reindex(columns=TICKERS).sort_index()


def validate_prices(prices: pd.DataFrame) -> QualitySummary:
    """Apply high-signal validity, completeness, and grain checks."""

    duplicate_dates = int(prices.index.duplicated().sum())
    missing_values = int(prices.isna().sum().sum())
    nonpositive_prices = int((prices <= 0).sum().sum())
    if not prices.index.is_monotonic_increasing:
        raise ValueError("Price dates must be monotonic increasing.")
    if duplicate_dates or missing_values or nonpositive_prices:
        raise ValueError(
            "Invalid price panel: "
            f"duplicates={duplicate_dates}, missing={missing_values}, "
            f"nonpositive={nonpositive_prices}"
        )
    returns = prices.pct_change(fill_method=None).dropna(how="any")
    return QualitySummary(
        rows=int(prices.shape[0]),
        columns=int(prices.shape[1]),
        first_date=str(prices.index.min().date()),
        last_date=str(prices.index.max().date()),
        duplicate_dates=duplicate_dates,
        missing_values=missing_values,
        nonpositive_prices=nonpositive_prices,
        maximum_absolute_return=float(returns.abs().max().max()),
    )


def portfolio_volatility(covariance: np.ndarray, weights: np.ndarray) -> float:
    """Annualized volatility implied by a daily covariance matrix."""

    variance = float(weights @ covariance @ weights)
    return float(np.sqrt(max(variance, 0.0) * TRADING_DAYS))


def rolling_covariance(history: pd.DataFrame) -> np.ndarray:
    """Sample covariance for a trailing return window."""

    return history.cov().to_numpy(dtype=float)


def update_ewma_covariance(
    previous: np.ndarray, latest_return: np.ndarray, decay: float = EWMA_LAMBDA
) -> np.ndarray:
    """RiskMetrics-style zero-mean EWMA covariance update."""

    return decay * previous + (1.0 - decay) * np.outer(latest_return, latest_return)


def estimate_forecasts(returns: pd.DataFrame) -> pd.DataFrame:
    """Estimate rolling and EWMA covariance forecasts through each close t."""

    if len(returns) < max(ROLLING_WINDOWS):
        raise ValueError("At least 126 complete return observations are required.")
    x = returns.reindex(columns=TICKERS)
    weights = WEIGHTS.to_numpy(dtype=float)
    start = max(ROLLING_WINDOWS) - 1
    ewma = rolling_covariance(x.iloc[: start + 1])
    rows: list[dict[str, float | pd.Timestamp]] = []

    for position in range(start, len(x)):
        if position > start:
            latest = x.iloc[position].to_numpy(dtype=float)
            ewma = update_ewma_covariance(ewma, latest)

        row: dict[str, float | pd.Timestamp] = {"date": x.index[position]}
        for window in ROLLING_WINDOWS:
            history = x.iloc[position - window + 1 : position + 1]
            covariance = rolling_covariance(history)
            row[f"rolling_{window}"] = portfolio_volatility(covariance, weights)
        row["ewma_094"] = portfolio_volatility(ewma, weights)
        rows.append(row)

    return pd.DataFrame(rows).set_index("date")


def forward_realized_volatility(returns: pd.DataFrame) -> pd.Series:
    """Compute ex-post 21-session realized volatility from t+1 to t+21."""

    portfolio_returns = returns.reindex(columns=TICKERS).dot(WEIGHTS)
    values: dict[pd.Timestamp, float] = {}
    start = max(ROLLING_WINDOWS) - 1
    for position in range(start, len(portfolio_returns) - FORWARD_WINDOW):
        outcome = portfolio_returns.iloc[
            position + 1 : position + 1 + FORWARD_WINDOW
        ]
        values[portfolio_returns.index[position]] = float(
            outcome.std(ddof=1) * np.sqrt(TRADING_DAYS)
        )
    return pd.Series(values, name="forward_realized_21d", dtype=float)


def evaluate_forecasts(
    forecasts: pd.DataFrame, realized: pd.Series
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return aligned daily observations and full-sample error metrics."""

    aligned = forecasts.join(realized, how="inner")
    metrics: list[dict[str, float | str | int]] = []
    for model in forecasts.columns:
        error = aligned[model] - aligned[realized.name]
        metrics.append(
            {
                "model": model,
                "observations": int(error.notna().sum()),
                "mae_vol_points": float(error.abs().mean() * 100),
                "rmse_vol_points": float(np.sqrt(error.pow(2).mean()) * 100),
                "bias_vol_points": float(error.mean() * 100),
                "correlation": float(aligned[model].corr(aligned[realized.name])),
            }
        )
    return aligned, pd.DataFrame(metrics).set_index("model")


def select_shock_events(
    portfolio_returns: pd.Series,
    percentile: float = SHOCK_PERCENTILE,
    exclusion_days: int = SHOCK_EXCLUSION_DAYS,
) -> tuple[pd.DatetimeIndex, float]:
    """Select the largest tail days while suppressing +/- exclusion_days.

    This is an ex-post event definition used only for historical description,
    never as a trading signal or as an input to any covariance forecast.
    """

    absolute = portfolio_returns.abs()
    threshold = float(absolute.quantile(percentile))
    candidates = np.flatnonzero((absolute >= threshold).to_numpy())
    ordered = candidates[np.argsort(-absolute.iloc[candidates].to_numpy())]
    selected: list[int] = []
    for position in ordered:
        if all(abs(int(position) - previous) > exclusion_days for previous in selected):
            selected.append(int(position))
    selected.sort()
    return pd.DatetimeIndex(portfolio_returns.index[selected]), threshold


def shock_response_table(
    forecasts: pd.DataFrame, portfolio_returns: pd.Series
) -> tuple[pd.DataFrame, pd.DataFrame, float]:
    """Measure the close-to-close forecast revision on selected shock dates."""

    common_returns = portfolio_returns.reindex(forecasts.index).dropna()
    event_dates, threshold = select_shock_events(common_returns)
    event_dates = pd.DatetimeIndex(
        [date for date in event_dates if forecasts.index.get_loc(date) > 0]
    )
    rows: list[dict[str, float | str | pd.Timestamp]] = []
    for date in event_dates:
        position = forecasts.index.get_loc(date)
        prior_date = forecasts.index[position - 1]
        for model in forecasts.columns:
            revision = float(forecasts.loc[date, model] / forecasts.loc[prior_date, model] - 1)
            rows.append(
                {
                    "date": date,
                    "model": model,
                    "portfolio_return": float(common_returns.loc[date]),
                    "forecast_revision": revision,
                }
            )
    events = pd.DataFrame(rows)
    summary = (
        events.groupby("model")["forecast_revision"]
        .agg(event_count="count", median_revision="median", mean_revision="mean")
        .sort_index()
    )
    return events, summary, threshold


def revision_table(forecasts: pd.DataFrame) -> pd.DataFrame:
    """Summarize normal day-to-day forecast variability."""

    rows = []
    for model in forecasts.columns:
        revision = forecasts[model].pct_change(fill_method=None).dropna()
        rows.append(
            {
                "model": model,
                "mean_abs_daily_revision": float(revision.abs().mean()),
                "median_abs_daily_revision": float(revision.abs().median()),
                "p95_abs_daily_revision": float(revision.abs().quantile(0.95)),
            }
        )
    return pd.DataFrame(rows).set_index("model")


def calendar_year_mae(aligned: pd.DataFrame) -> pd.DataFrame:
    """Calendar-year MAE table used to check ranking stability."""

    rows = []
    for year, group in aligned.groupby(aligned.index.year):
        for model in [column for column in aligned if column != "forward_realized_21d"]:
            rows.append(
                {
                    "year": int(year),
                    "model": model,
                    "observations": int(len(group)),
                    "mae_vol_points": float(
                        (group[model] - group["forward_realized_21d"]).abs().mean()
                        * 100
                    ),
                }
            )
    return pd.DataFrame(rows)


def ewma_half_life(decay: float = EWMA_LAMBDA) -> float:
    """Trading-day half-life implied by an EWMA decay parameter."""

    return float(np.log(0.5) / np.log(decay))


def make_figures(
    aligned: pd.DataFrame,
    shock_summary: pd.DataFrame,
    revision_summary: pd.DataFrame,
    figure_dir: Path,
) -> None:
    """Create repository figures; the carousel uses editable native charts."""

    figure_dir.mkdir(parents=True, exist_ok=True)
    colors = {
        "rolling_21": "#d97706",
        "rolling_63": "#2563eb",
        "rolling_126": "#64748b",
        "ewma_094": "#0f766e",
    }
    labels = {
        "rolling_21": "Rolling 21D",
        "rolling_63": "Rolling 63D",
        "rolling_126": "Rolling 126D",
        "ewma_094": "EWMA 0.94",
    }

    plt.figure(figsize=(11, 5.8))
    plt.plot(
        aligned.index,
        aligned["forward_realized_21d"] * 100,
        color="#0f172a",
        linewidth=1.3,
        label="Forward realized 21D",
    )
    for model in colors:
        plt.plot(
            aligned.index,
            aligned[model] * 100,
            color=colors[model],
            linewidth=0.9,
            alpha=0.85,
            label=labels[model],
        )
    plt.ylabel("Annualized volatility (%)")
    plt.title("Risk forecasts react at different speeds")
    plt.legend(ncol=3, frameon=False)
    plt.grid(axis="y", alpha=0.2)
    plt.tight_layout()
    plt.savefig(figure_dir / "week11_forecast_comparison.png", dpi=180)
    plt.close()

    ordered = ["rolling_21", "rolling_63", "rolling_126", "ewma_094"]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))
    axes[0].bar(
        [labels[m] for m in ordered],
        [shock_summary.loc[m, "median_revision"] * 100 for m in ordered],
        color=[colors[m] for m in ordered],
    )
    axes[0].set_title("Median forecast jump on shock dates")
    axes[0].set_ylabel("Close-to-close revision (%)")
    axes[0].tick_params(axis="x", rotation=25)
    axes[0].grid(axis="y", alpha=0.2)
    axes[1].bar(
        [labels[m] for m in ordered],
        [revision_summary.loc[m, "mean_abs_daily_revision"] * 100 for m in ordered],
        color=[colors[m] for m in ordered],
    )
    axes[1].set_title("Average absolute daily revision")
    axes[1].set_ylabel("Revision (%)")
    axes[1].tick_params(axis="x", rotation=25)
    axes[1].grid(axis="y", alpha=0.2)
    fig.tight_layout()
    fig.savefig(figure_dir / "week11_speed_stability_tradeoff.png", dpi=180)
    plt.close(fig)


def run(input_path: Path, report_dir: Path) -> dict[str, object]:
    """Run the analysis and persist inspectable tables and figures."""

    table_dir = report_dir / "tables"
    figure_dir = report_dir / "figures"
    table_dir.mkdir(parents=True, exist_ok=True)

    prices = load_prices(input_path)
    quality = validate_prices(prices)
    returns = prices.pct_change(fill_method=None).dropna(how="any")
    forecasts = estimate_forecasts(returns)
    realized = forward_realized_volatility(returns)
    aligned, metrics = evaluate_forecasts(forecasts, realized)
    portfolio_returns = returns.dot(WEIGHTS)
    events, shock_summary, shock_threshold = shock_response_table(
        forecasts, portfolio_returns
    )
    revisions = revision_table(forecasts)
    yearly_mae = calendar_year_mae(aligned)

    quality_frame = pd.DataFrame([quality.__dict__])
    quality_frame.to_csv(table_dir / "data_quality_summary.csv", index=False)
    WEIGHTS.rename_axis("ticker").to_csv(table_dir / "portfolio_weights.csv")
    forecasts.to_csv(table_dir / "daily_covariance_forecasts.csv")
    aligned.to_csv(table_dir / "forecast_evaluation_panel.csv")
    metrics.to_csv(table_dir / "forecast_error_metrics.csv")
    events.to_csv(table_dir / "shock_event_responses.csv", index=False)
    shock_summary.to_csv(table_dir / "shock_response_summary.csv")
    revisions.to_csv(table_dir / "forecast_revision_summary.csv")
    yearly_mae.to_csv(table_dir / "calendar_year_mae.csv", index=False)
    pd.DataFrame(
        [
            {
                "ewma_lambda": EWMA_LAMBDA,
                "ewma_half_life_trading_days": ewma_half_life(),
                "shock_percentile": SHOCK_PERCENTILE,
                "shock_abs_return_threshold": shock_threshold,
                "shock_exclusion_days_each_side": SHOCK_EXCLUSION_DAYS,
                "forward_realized_window": FORWARD_WINDOW,
                "annualization_factor": TRADING_DAYS,
            }
        ]
    ).to_csv(table_dir / "method_parameters.csv", index=False)
    make_figures(aligned, shock_summary, revisions, figure_dir)

    return {
        "quality": quality,
        "forecasts": forecasts,
        "aligned": aligned,
        "metrics": metrics,
        "events": events,
        "shock_summary": shock_summary,
        "revisions": revisions,
        "yearly_mae": yearly_mae,
        "shock_threshold": shock_threshold,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run(args.input, args.report_dir)
    print("Week 11 analysis complete")
    print(result["metrics"].round(4).to_string())
    print("\nShock response")
    print(result["shock_summary"].round(4).to_string())


if __name__ == "__main__":
    main()

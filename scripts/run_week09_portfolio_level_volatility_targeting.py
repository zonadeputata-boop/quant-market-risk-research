"""Week 09 research script.

Portfolio-Level Volatility Targeting:
Separating sleeve normalization from the portfolio risk target.

Run from project root with live public market data:
    PYTHONPATH=src python3 scripts/run_week09_portfolio_level_volatility_targeting.py

Run the optional deterministic offline mechanics check:
    PYTHONPATH=src python3 scripts/run_week09_portfolio_level_volatility_targeting.py --demo
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


START_DATE = "2020-01-01"
TICKERS = ["SPY", "QQQ", "TLT", "GLD", "HYG", "SHY"]
BASE_WEIGHTS = pd.Series(
    {"SPY": 0.25, "QQQ": 0.20, "TLT": 0.20, "GLD": 0.15, "HYG": 0.10, "SHY": 0.10}
)
TRADING_DAYS = 252
VOLATILITY_WINDOW = 63
SLEEVE_VOLATILITY_ANCHOR = 0.10
PORTFOLIO_VOLATILITY_TARGET = 0.10
MAX_SLEEVE_SCALAR = 2.00
MAX_PORTFOLIO_SCALAR = 2.00
MAX_GROSS_EXPOSURE = 1.50
TRANSACTION_COST_BPS = 5.0
VOLATILITY_BAND = 0.10

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "raw" / "week09_adjusted_close.csv"
DEMO_RETURNS_PATH = ROOT / "data" / "processed" / "week09_demo_returns.csv"
REPORT_DIR = ROOT / "reports" / "week_09_portfolio_level_volatility_targeting"
FIG_DIR = REPORT_DIR / "figures"
TABLE_DIR = REPORT_DIR / "tables"


@dataclass(frozen=True)
class TargetState:
    sleeve_scalars: pd.Series
    sleeve_only_exposure: pd.Series
    sleeve_only_forecast_volatility: float
    portfolio_scalar: float
    target_exposure: pd.Series
    target_forecast_volatility: float


def portfolio_volatility(exposure: np.ndarray, covariance: np.ndarray) -> float:
    """Return annualized portfolio volatility for an exposure vector."""

    variance = float(exposure @ covariance @ exposure)
    return float(np.sqrt(max(variance, 0.0)))


def apply_gross_cap(exposure: pd.Series) -> pd.Series:
    """Scale the whole vector proportionally when the gross cap binds."""

    gross = float(exposure.abs().sum())
    if gross <= MAX_GROSS_EXPOSURE or gross == 0:
        return exposure
    return exposure * (MAX_GROSS_EXPOSURE / gross)


def calculate_target_state(covariance: pd.DataFrame) -> TargetState:
    """Build sleeve-normalized and portfolio-targeted exposure vectors."""

    covariance = covariance.reindex(index=TICKERS, columns=TICKERS)
    covariance_array = covariance.to_numpy(dtype=float)
    asset_volatility = pd.Series(
        np.sqrt(np.diag(covariance_array)), index=TICKERS, dtype=float
    )
    if (asset_volatility <= 0).any() or asset_volatility.isna().any():
        raise ValueError("Every sleeve needs a finite positive volatility estimate.")

    sleeve_scalars = (SLEEVE_VOLATILITY_ANCHOR / asset_volatility).clip(
        lower=0.0, upper=MAX_SLEEVE_SCALAR
    )
    sleeve_only_exposure = apply_gross_cap(BASE_WEIGHTS * sleeve_scalars)
    sleeve_only_forecast = portfolio_volatility(
        sleeve_only_exposure.to_numpy(), covariance_array
    )
    if sleeve_only_forecast <= 0:
        raise ValueError("Sleeve-normalized portfolio volatility must be positive.")

    portfolio_scalar = float(
        np.clip(
            PORTFOLIO_VOLATILITY_TARGET / sleeve_only_forecast,
            0.0,
            MAX_PORTFOLIO_SCALAR,
        )
    )
    target_exposure = apply_gross_cap(sleeve_only_exposure * portfolio_scalar)
    target_forecast = portfolio_volatility(target_exposure.to_numpy(), covariance_array)
    return TargetState(
        sleeve_scalars=sleeve_scalars,
        sleeve_only_exposure=sleeve_only_exposure,
        sleeve_only_forecast_volatility=sleeve_only_forecast,
        portfolio_scalar=portfolio_scalar,
        target_exposure=target_exposure,
        target_forecast_volatility=target_forecast,
    )


def download_returns() -> pd.DataFrame:
    """Download adjusted closes from Yahoo's chart endpoint and return returns.

    Tickers are requested sequentially to reduce rate-limit pressure. The code
    records the exact first and last complete dates used by the analysis.
    """

    period1 = int(pd.Timestamp(START_DATE, tz="UTC").timestamp())
    period2 = int(datetime.now(timezone.utc).timestamp()) + 86_400
    series: dict[str, pd.Series] = {}
    for ticker_number, ticker in enumerate(TICKERS):
        params = urlencode(
            {
                "period1": period1,
                "period2": period2,
                "interval": "1d",
                "events": "history",
                "includeAdjustedClose": "true",
            }
        )
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?{params}"
        request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        last_error: Exception | None = None
        for attempt in range(3):
            try:
                with urlopen(request, timeout=30) as response:
                    payload = json.load(response)
                result = payload["chart"]["result"][0]
                timestamps = result["timestamp"]
                indicators = result["indicators"]
                adjusted = indicators.get("adjclose")
                values = (
                    adjusted[0]["adjclose"]
                    if adjusted
                    else indicators["quote"][0]["close"]
                )
                dates = pd.to_datetime(timestamps, unit="s", utc=True).tz_convert(None).normalize()
                series[ticker] = pd.Series(values, index=dates, name=ticker, dtype=float)
                break
            except Exception as exc:  # pragma: no cover - network-dependent path
                last_error = exc
                if attempt == 2:
                    raise RuntimeError(f"Failed to download {ticker}: {exc}") from exc
                time.sleep(2**attempt)
        if ticker_number < len(TICKERS) - 1:
            time.sleep(0.5)

    close = pd.concat(series.values(), axis=1).reindex(columns=TICKERS)
    close = close.sort_index().ffill().dropna(how="any")
    if close.empty:
        raise RuntimeError("No complete adjusted-close observations were returned.")
    RAW_PATH.parent.mkdir(parents=True, exist_ok=True)
    close.to_csv(RAW_PATH)
    returns = close.pct_change(fill_method=None).dropna(how="any")
    returns.attrs["source"] = "Yahoo Finance chart endpoint; adjusted close"
    returns.attrs["first_date"] = str(close.index.min().date())
    returns.attrs["last_date"] = str(close.index.max().date())
    returns.attrs["observations"] = int(len(returns))
    return returns


def build_demo_returns(seed: int = 9) -> pd.DataFrame:
    """Create a deterministic three-regime sample for offline method validation.

    The sample is explicitly illustrative. It is not calibrated to reproduce a
    historical period or to estimate expected performance.
    """

    rng = np.random.default_rng(seed)
    regime_spec = [
        (315, 0.10, 0.00, "low-correlation"),
        (126, 0.65, -0.0006, "correlated-shock"),
        (315, 0.25, 0.0001, "normalisation"),
    ]
    annual_volatility = np.array([0.18, 0.24, 0.14, 0.15, 0.12, 0.035])
    rows: list[np.ndarray] = []
    regimes: list[str] = []
    for observation_count, average_correlation, daily_drift, label in regime_spec:
        correlation = np.full((len(TICKERS), len(TICKERS)), average_correlation)
        np.fill_diagonal(correlation, 1.0)
        daily_volatility = annual_volatility / np.sqrt(TRADING_DAYS)
        covariance = np.outer(daily_volatility, daily_volatility) * correlation
        simulated = rng.multivariate_normal(
            mean=np.repeat(daily_drift, len(TICKERS)),
            cov=covariance,
            size=observation_count,
        )
        rows.append(simulated)
        regimes.extend([label] * observation_count)

    index = pd.bdate_range("2022-01-03", periods=sum(len(block) for block in rows))
    returns = pd.DataFrame(np.vstack(rows), index=index, columns=TICKERS)
    returns.attrs["regimes"] = pd.Series(regimes, index=index, name="regime")
    DEMO_RETURNS_PATH.parent.mkdir(parents=True, exist_ok=True)
    returns.to_csv(DEMO_RETURNS_PATH)
    return returns


def estimate_states(
    returns: pd.DataFrame,
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    dict[pd.Timestamp, pd.DataFrame],
    pd.DataFrame,
]:
    """Use information through t-1 to estimate all exposure targets for day t."""

    target_rows: list[pd.Series] = []
    sleeve_rows: list[pd.Series] = []
    diagnostic_rows: list[dict[str, float | pd.Timestamp]] = []
    covariance_by_date: dict[pd.Timestamp, pd.DataFrame] = {}

    for position in range(VOLATILITY_WINDOW, len(returns)):
        date = returns.index[position]
        history = returns.iloc[position - VOLATILITY_WINDOW : position]
        covariance = history.cov() * TRADING_DAYS
        state = calculate_target_state(covariance)
        covariance_by_date[date] = covariance
        target_rows.append(state.target_exposure.rename(date))
        sleeve_rows.append(state.sleeve_only_exposure.rename(date))

        standard_deviation = np.sqrt(np.diag(covariance.to_numpy()))
        correlation = covariance.to_numpy() / np.outer(standard_deviation, standard_deviation)
        upper = correlation[np.triu_indices_from(correlation, k=1)]
        diagnostic_rows.append(
            {
                "date": date,
                "average_pairwise_correlation": float(np.nanmean(upper)),
                "sleeve_only_forecast_volatility": state.sleeve_only_forecast_volatility,
                "portfolio_scalar": state.portfolio_scalar,
                "target_forecast_volatility": state.target_forecast_volatility,
                "target_gross_exposure": float(state.target_exposure.abs().sum()),
            }
        )

    target = pd.DataFrame(target_rows).reindex(columns=TICKERS)
    sleeve_only = pd.DataFrame(sleeve_rows).reindex(columns=TICKERS)
    diagnostics = pd.DataFrame(diagnostic_rows).set_index("date")
    evaluation_returns = returns.reindex(target.index)
    return target, sleeve_only, evaluation_returns, covariance_by_date, diagnostics


def backtest_policy(
    returns: pd.DataFrame,
    target_exposure: pd.DataFrame,
    covariance_by_date: dict[pd.Timestamp, pd.DataFrame],
    policy: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Backtest daily, weekly, or volatility-band rebalancing with drift and costs."""

    if policy not in {"daily", "weekly", "band"}:
        raise ValueError(f"Unsupported policy: {policy}")

    weekly_dates = set(
        target_exposure.groupby(target_exposure.index.to_period("W-FRI")).tail(1).index
    )
    pre_trade = pd.Series(0.0, index=TICKERS)
    exposure_rows: list[pd.Series] = []
    result_rows: list[dict[str, float | int | pd.Timestamp]] = []

    for row_number, date in enumerate(target_exposure.index):
        covariance = covariance_by_date[date].to_numpy()
        held_forecast = portfolio_volatility(pre_trade.to_numpy(), covariance)
        if policy == "daily":
            rebalance = True
        elif policy == "weekly":
            rebalance = row_number == 0 or date in weekly_dates
        else:
            lower = PORTFOLIO_VOLATILITY_TARGET * (1.0 - VOLATILITY_BAND)
            upper = PORTFOLIO_VOLATILITY_TARGET * (1.0 + VOLATILITY_BAND)
            rebalance = row_number == 0 or held_forecast < lower or held_forecast > upper

        desired = target_exposure.loc[date]
        post_trade = desired.copy() if rebalance else pre_trade.copy()
        turnover = float((post_trade - pre_trade).abs().sum()) if rebalance else 0.0
        cost = turnover * TRANSACTION_COST_BPS / 10_000.0
        gross_return = float(post_trade @ returns.loc[date])
        net_return = gross_return - cost
        forecast = portfolio_volatility(post_trade.to_numpy(), covariance)

        exposure_rows.append(post_trade.rename(date))
        result_rows.append(
            {
                "date": date,
                "gross_return": gross_return,
                "net_return": net_return,
                "turnover": turnover,
                "transaction_cost": cost,
                "forecast_volatility": forecast,
                "gross_exposure": float(post_trade.abs().sum()),
                "rebalanced": int(rebalance),
            }
        )

        denominator = 1.0 + net_return
        if denominator <= 0:
            raise RuntimeError("Strategy equity became non-positive in the sample.")
        pre_trade = post_trade * (1.0 + returns.loc[date]) / denominator

    return pd.DataFrame(result_rows).set_index("date"), pd.DataFrame(exposure_rows)


def max_drawdown(returns: pd.Series) -> float:
    equity = (1.0 + returns).cumprod()
    drawdown = equity / equity.cummax() - 1.0
    return float(drawdown.min())


def dataframe_to_markdown(frame: pd.DataFrame) -> str:
    """Render a compact Markdown table without an optional tabulate dependency."""

    headers = [str(column) for column in frame.columns]
    rows = [[str(value) for value in row] for row in frame.itertuples(index=False, name=None)]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines)


def summarize_policy(name: str, results: pd.DataFrame) -> dict[str, float | str | int]:
    years = len(results) / TRADING_DAYS
    return {
        "policy": name,
        "realized_annualized_volatility": float(results["net_return"].std() * np.sqrt(TRADING_DAYS)),
        "average_forecast_volatility": float(results["forecast_volatility"].mean()),
        "mean_absolute_target_error": float(
            (results["forecast_volatility"] - PORTFOLIO_VOLATILITY_TARGET).abs().mean()
        ),
        "annualized_turnover": float(results["turnover"].sum() / years),
        "annualized_cost_drag": float(results["transaction_cost"].sum() / years),
        "maximum_drawdown": max_drawdown(results["net_return"]),
        "rebalance_count": int(results["rebalanced"].sum()),
    }


def scenario_table() -> pd.DataFrame:
    """Show analytically how correlation changes portfolio volatility."""

    rows = []
    asset_count = len(TICKERS)
    for label, correlation in [
        ("dispersed", 0.10),
        ("connected", 0.40),
        ("moves-together", 0.75),
    ]:
        portfolio_vol = SLEEVE_VOLATILITY_ANCHOR * np.sqrt(
            (1.0 + (asset_count - 1.0) * correlation) / asset_count
        )
        rows.append(
            {
                "scenario": label,
                "pairwise_correlation": correlation,
                "sleeve_volatility": SLEEVE_VOLATILITY_ANCHOR,
                "portfolio_volatility_before_portfolio_scalar": portfolio_vol,
                "uncapped_portfolio_scalar_to_10pct": PORTFOLIO_VOLATILITY_TARGET
                / portfolio_vol,
            }
        )
    return pd.DataFrame(rows)


def make_figures(
    diagnostics: pd.DataFrame,
    strategy_results: dict[str, pd.DataFrame],
    policy_summary: pd.DataFrame,
) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 5))
    diagnostics["sleeve_only_forecast_volatility"].plot(
        ax=ax, color="#AAB7C6", linewidth=1.3, label="Sleeve normalisation only"
    )
    strategy_results["two_stage_daily"]["forecast_volatility"].plot(
        ax=ax, color="#24679E", linewidth=1.3, label="Two-stage portfolio target"
    )
    ax.axhline(PORTFOLIO_VOLATILITY_TARGET, color="#17253A", linestyle="--", linewidth=1.1)
    ax.set_title("Forecast Portfolio Volatility")
    ax.set_ylabel("Annualized volatility")
    ax.grid(alpha=0.25)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "forecast_portfolio_volatility.png", dpi=200)
    plt.close(fig)

    fig, ax1 = plt.subplots(figsize=(10, 5))
    diagnostics["average_pairwise_correlation"].plot(
        ax=ax1, color="#AAB7C6", linewidth=1.3, label="Average correlation"
    )
    ax1.set_ylabel("Average pairwise correlation")
    ax2 = ax1.twinx()
    diagnostics["portfolio_scalar"].plot(
        ax=ax2, color="#24679E", linewidth=1.3, label="Portfolio scalar"
    )
    ax2.set_ylabel("Portfolio scalar")
    ax1.set_title("Correlation Changes the Portfolio Scalar")
    ax1.grid(alpha=0.25)
    lines = ax1.get_lines() + ax2.get_lines()
    ax1.legend(lines, [line.get_label() for line in lines], frameon=False, loc="upper right")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "correlation_and_portfolio_scalar.png", dpi=200)
    plt.close(fig)

    chart = policy_summary.loc[
        policy_summary["policy"].str.startswith("two_stage"),
        ["policy", "mean_absolute_target_error", "annualized_cost_drag"],
    ].copy()
    chart["annualized_cost_bps"] = chart["annualized_cost_drag"] * 10_000
    labels = {
        "two_stage_daily": "Daily",
        "two_stage_weekly": "Weekly",
        "two_stage_band_10pct": "10% band",
    }
    chart["label"] = chart["policy"].map(labels)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.scatter(
        chart["mean_absolute_target_error"] * 100,
        chart["annualized_cost_bps"],
        s=120,
        color="#24679E",
    )
    for _, row in chart.iterrows():
        ax.annotate(row["label"], (row["mean_absolute_target_error"] * 100, row["annualized_cost_bps"]), xytext=(7, 5), textcoords="offset points")
    ax.set_title("Rebalancing Trades Target Precision for Cost")
    ax.set_xlabel("Mean absolute forecast-target gap (volatility points)")
    ax.set_ylabel("Annualized modeled cost (basis points)")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "rebalancing_precision_vs_cost.png", dpi=200)
    plt.close(fig)


def write_research_summary(
    policy_summary: pd.DataFrame, source_label: str, use_demo: bool
) -> None:
    interpretation = (
        "The deterministic demo validates implementation mechanics and illustrates "
        "the correlation effect. It is not historical evidence or an expected-return "
        "backtest."
        if use_demo
        else "The results are historical, model-dependent backtest diagnostics for the "
        "stated ETF sample. They are not expected-return estimates and do not establish "
        "that the policy ranking will persist."
    )
    summary = f"""# Week 09 - Portfolio-Level Volatility Targeting

## Research question

Why does sizing every sleeve to its own volatility fail to set portfolio volatility?

## Two-stage rule

```text
sleeve_scalar_i,t = clip(sleeve_vol_anchor / forecast_vol_i,t-1)
sleeve_exposure_t = base_weight .* sleeve_scalar_t
portfolio_forecast_t = sqrt(sleeve_exposure_t' * covariance_t-1 * sleeve_exposure_t)
portfolio_scalar_t = clip(portfolio_target / portfolio_forecast_t)
target_exposure_t = gross_cap(portfolio_scalar_t * sleeve_exposure_t)
```

## Rebalancing and cost

```text
turnover_t = sum(abs(target_exposure_t - pre_trade_exposure_t))
cost_t = turnover_t * {TRANSACTION_COST_BPS:.1f} bps
```

The comparison includes daily, weekly, and ±{VOLATILITY_BAND:.0%} volatility-band
rebalancing. Inputs for day t use returns through t-1. Between rebalances,
exposures drift with asset returns.

## Parameters

```text
source = {source_label}
assets = {', '.join(TICKERS)}
covariance and volatility window = {VOLATILITY_WINDOW} trading days
sleeve volatility anchor = {SLEEVE_VOLATILITY_ANCHOR:.0%}
portfolio volatility target = {PORTFOLIO_VOLATILITY_TARGET:.0%}
maximum sleeve scalar = {MAX_SLEEVE_SCALAR:.1f}x
maximum portfolio scalar = {MAX_PORTFOLIO_SCALAR:.1f}x
maximum gross exposure = {MAX_GROSS_EXPOSURE:.1f}x
modeled one-way transaction cost = {TRANSACTION_COST_BPS:.1f} bps
```

## Strategy comparison

{dataframe_to_markdown(policy_summary.round(4))}

## Interpretation boundary

The volatility forecast is a model output, not a guarantee. {interpretation}

## Limitations

The estimator is a simple rolling sample covariance. Production use should test
shrinkage, stress covariance, volatility-of-volatility, financing, nonlinear
market impact, exposure constraints, and execution timing.

## Disclaimer

For educational and analytical purposes only. Not investment advice.
"""
    (REPORT_DIR / "research_summary.md").write_text(summary, encoding="utf-8")


def run(use_demo: bool) -> pd.DataFrame:
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    returns = build_demo_returns() if use_demo else download_returns()
    target, sleeve_only, evaluation_returns, covariance_by_date, diagnostics = estimate_states(returns)

    strategy_results: dict[str, pd.DataFrame] = {}
    strategy_results["sleeve_only_daily"], _ = backtest_policy(
        evaluation_returns, sleeve_only, covariance_by_date, "daily"
    )
    strategy_results["two_stage_daily"], daily_exposure = backtest_policy(
        evaluation_returns, target, covariance_by_date, "daily"
    )
    strategy_results["two_stage_weekly"], _ = backtest_policy(
        evaluation_returns, target, covariance_by_date, "weekly"
    )
    strategy_results["two_stage_band_10pct"], _ = backtest_policy(
        evaluation_returns, target, covariance_by_date, "band"
    )

    policy_summary = pd.DataFrame(
        [summarize_policy(name, result) for name, result in strategy_results.items()]
    )
    policy_summary.to_csv(TABLE_DIR / "policy_comparison.csv", index=False)
    diagnostics.to_csv(TABLE_DIR / "portfolio_target_diagnostics.csv")
    target.to_csv(TABLE_DIR / "target_exposures.csv")
    daily_exposure.to_csv(TABLE_DIR / "daily_post_trade_exposures.csv")
    scenario_table().to_csv(TABLE_DIR / "correlation_scenarios.csv", index=False)
    for name, result in strategy_results.items():
        result.to_csv(TABLE_DIR / f"{name}_results.csv")

    make_figures(diagnostics, strategy_results, policy_summary)
    source_label = (
        "deterministic three-regime demonstration (seed=9; illustrative, not market data)"
        if use_demo
        else (
            f"Yahoo Finance adjusted closes; {returns.attrs['first_date']} to "
            f"{returns.attrs['last_date']}; {returns.attrs['observations']} return observations"
        )
    )
    if not use_demo:
        pd.DataFrame(
            [
                {
                    "source": returns.attrs["source"],
                    "first_date": returns.attrs["first_date"],
                    "last_date": returns.attrs["last_date"],
                    "return_observations": returns.attrs["observations"],
                    "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
                }
            ]
        ).to_csv(TABLE_DIR / "live_run_metadata.csv", index=False)
    write_research_summary(policy_summary, source_label, use_demo)
    print("Week 09 portfolio-level volatility targeting complete.")
    print(policy_summary.round(4).to_string(index=False))
    return policy_summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Use the deterministic offline demonstration instead of live data.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    run(use_demo=arguments.demo)

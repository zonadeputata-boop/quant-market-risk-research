"""Week 07 research script.

Drawdown-Aware Position Sizing:
Adding a capital-path constraint to volatility targeting

Run from project root:
    PYTHONPATH=src python3 scripts/run_week07_drawdown_aware_position_sizing.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from quant_research.data import download_prices
from quant_research.returns import simple_returns


START_DATE = "2020-01-01"
TICKERS = ["SPY", "QQQ", "TLT", "GLD", "HYG", "SHY"]
VOL_WINDOW = 63
TARGET_VOL = 0.10
MAX_EXPOSURE = 1.00
DRAWDOWN_BUDGET = 0.20
MIN_DRAWDOWN_SCALAR = 0.25

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "raw" / "week07_prices.csv"
REPORT_DIR = ROOT / "reports" / "week_07_drawdown_aware_position_sizing"
FIG_DIR = REPORT_DIR / "figures"
TABLE_DIR = REPORT_DIR / "tables"


def max_drawdown(returns: pd.Series) -> float:
    equity = (1.0 + returns.dropna()).cumprod()
    drawdown = equity / equity.cummax() - 1.0
    return float(drawdown.min())


def annualized_volatility(returns: pd.Series) -> float:
    return float(returns.dropna().std() * np.sqrt(252))


def drawdown_aware_path(
    returns: pd.Series,
    realized_volatility: pd.Series,
) -> pd.DataFrame:
    """Build a recursive, lagged exposure path with no look-ahead.

    The strategy uses the volatility estimate and equity drawdown available
    before each day's return. Drawdown is measured on the strategy's own
    equity curve.
    """

    aligned_returns = returns.dropna()
    lagged_volatility = realized_volatility.reindex(aligned_returns.index).shift(1)

    equity = 1.0
    running_peak = 1.0
    records: list[dict[str, float]] = []

    for date, daily_return in aligned_returns.items():
        volatility = lagged_volatility.loc[date]

        if pd.isna(volatility) or volatility <= 0:
            vol_scalar = 0.0
        else:
            vol_scalar = min(MAX_EXPOSURE, TARGET_VOL / float(volatility))

        prior_drawdown = equity / running_peak - 1.0
        drawdown_scalar = float(
            np.clip(
                1.0 + prior_drawdown / DRAWDOWN_BUDGET,
                MIN_DRAWDOWN_SCALAR,
                1.0,
            )
        )
        final_exposure = vol_scalar * drawdown_scalar
        strategy_return = final_exposure * float(daily_return)

        equity *= 1.0 + strategy_return
        running_peak = max(running_peak, equity)

        records.append(
            {
                "date": date,
                "asset_return": float(daily_return),
                "realized_volatility": float(volatility)
                if pd.notna(volatility)
                else np.nan,
                "volatility_scalar": vol_scalar,
                "prior_drawdown": prior_drawdown,
                "drawdown_scalar": drawdown_scalar,
                "final_exposure": final_exposure,
                "strategy_return": strategy_return,
                "strategy_equity": equity,
            }
        )

    return pd.DataFrame(records).set_index("date")


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)

    prices = download_prices(TICKERS, start=START_DATE, cache_path=RAW_PATH)
    returns = simple_returns(prices).dropna()
    realized_volatility = returns.rolling(VOL_WINDOW).std() * np.sqrt(252)

    paths: dict[str, pd.DataFrame] = {}
    rows: list[dict[str, float | str]] = []

    for ticker in TICKERS:
        path = drawdown_aware_path(returns[ticker], realized_volatility[ticker])
        paths[ticker] = path

        valid = path.loc[path["volatility_scalar"] > 0].copy()
        strategy_returns = valid["strategy_return"]
        buy_hold_returns = returns[ticker].reindex(strategy_returns.index)

        rows.append(
            {
                "asset": ticker,
                "latest_realized_volatility": valid["realized_volatility"].iloc[-1],
                "latest_prior_drawdown": valid["prior_drawdown"].iloc[-1],
                "latest_volatility_scalar": valid["volatility_scalar"].iloc[-1],
                "latest_drawdown_scalar": valid["drawdown_scalar"].iloc[-1],
                "latest_final_exposure": valid["final_exposure"].iloc[-1],
                "buy_hold_ann_vol": annualized_volatility(buy_hold_returns),
                "strategy_ann_vol": annualized_volatility(strategy_returns),
                "buy_hold_max_drawdown": max_drawdown(buy_hold_returns),
                "strategy_max_drawdown": max_drawdown(strategy_returns),
                "avg_abs_exposure_change": valid["final_exposure"].diff().abs().mean(),
            }
        )

    summary = pd.DataFrame(rows).set_index("asset")
    summary.to_csv(TABLE_DIR / "drawdown_aware_summary.csv")

    exposure = pd.DataFrame(
        {ticker: path["final_exposure"] for ticker, path in paths.items()}
    )
    fig, ax = plt.subplots(figsize=(10, 5))
    exposure.plot(ax=ax, linewidth=1.1)
    ax.set_title("Drawdown-Aware Exposure")
    ax.set_ylabel("Exposure multiplier")
    ax.set_ylim(bottom=0)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "drawdown_aware_exposure.png", dpi=200)
    plt.close(fig)

    equity = pd.DataFrame(
        {
            ticker: path.loc[path["volatility_scalar"] > 0, "strategy_equity"]
            for ticker, path in paths.items()
        }
    )
    fig, ax = plt.subplots(figsize=(10, 5))
    equity.plot(ax=ax, linewidth=1.1)
    ax.set_title("Drawdown-Aware Strategy Equity")
    ax.set_ylabel("Growth of 1.0")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "drawdown_aware_equity.png", dpi=200)
    plt.close(fig)

    methodology = f"""# Week 07 - Drawdown-Aware Position Sizing

## Research question

If two positions have similar volatility but different loss paths, should they
carry the same exposure?

## Core rules

```text
volatility_scalar_t = min(
    max_exposure,
    target_volatility / realized_volatility_(t-1)
)

drawdown_t = strategy_equity_(t-1) / running_peak_(t-1) - 1

drawdown_scalar_t = clip(
    1 + drawdown_t / drawdown_budget,
    min_drawdown_scalar,
    1
)

final_exposure_t = volatility_scalar_t * drawdown_scalar_t
strategy_return_t = final_exposure_t * asset_return_t
```

## Parameters

```text
public tickers = {", ".join(TICKERS)}
volatility window = {VOL_WINDOW} trading days
target volatility = {TARGET_VOL:.0%}
maximum exposure = {MAX_EXPOSURE:.2f}x
drawdown budget = {DRAWDOWN_BUDGET:.0%}
minimum drawdown scalar = {MIN_DRAWDOWN_SCALAR:.2f}
```

## Summary

{summary.round(4).to_markdown()}

## Output files

- `reports/week_07_drawdown_aware_position_sizing/tables/drawdown_aware_summary.csv`
- `reports/week_07_drawdown_aware_position_sizing/figures/drawdown_aware_exposure.png`
- `reports/week_07_drawdown_aware_position_sizing/figures/drawdown_aware_equity.png`

## Disclaimer

For educational and analytical purposes only. Not investment advice.
"""
    (REPORT_DIR / "research_summary.md").write_text(methodology, encoding="utf-8")

    print("Week 07 research complete.")
    print(summary.round(4))


if __name__ == "__main__":
    main()

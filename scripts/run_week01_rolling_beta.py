"""Week 01 research script.

Rolling Beta Instability:
Why Static Beta Can Mislead Risk Sizing

Run:
    python scripts/run_week01_rolling_beta.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from quant_research.data import download_prices
from quant_research.returns import simple_returns
from quant_research.rolling_models import rolling_ols_alpha_beta_r2
from quant_research.risk_metrics import drawdown
from quant_research.plots import save_rolling_beta_plot, save_rolling_r2_plot, save_drawdown_plot


START_DATE = "2020-01-01"
WINDOW = 63

TICKERS = ["SPY", "QQQ", "TLT", "GLD", "HYG", "SHY", "^VIX"]
BENCHMARK = "SPY"
ASSETS = ["QQQ", "TLT", "GLD", "HYG", "SHY"]

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "raw" / "week01_prices.csv"
REPORT_DIR = ROOT / "reports" / "week_01_rolling_beta_instability"
FIG_DIR = REPORT_DIR / "figures"
TABLE_DIR = REPORT_DIR / "tables"


def classify_stress_regime(prices: pd.DataFrame, returns: pd.DataFrame) -> pd.Series:
    """Define a simple market stress regime.

    Stress is flagged when:
    - VIX > 25, or
    - SPY drawdown is below -10%.
    """
    spy_dd = drawdown(returns[BENCHMARK])
    vix_level = prices["^VIX"].reindex(spy_dd.index).ffill()

    stress = (vix_level > 25) | (spy_dd < -0.10)
    stress.name = "stress_regime"
    return stress


def main() -> None:
    prices = download_prices(TICKERS, start=START_DATE, cache_path=RAW_PATH)
    returns = simple_returns(prices)

    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    rolling_stats: dict[str, pd.DataFrame] = {}

    for asset in ASSETS:
        stats = rolling_ols_alpha_beta_r2(
            asset_returns=returns[asset],
            benchmark_returns=returns[BENCHMARK],
            window=WINDOW,
        )
        rolling_stats[asset] = stats
        stats.to_csv(TABLE_DIR / f"{asset}_rolling_ols_{WINDOW}d.csv")

    # Summary table
    stress = classify_stress_regime(prices, returns)

    summary_rows = []
    for asset, stats in rolling_stats.items():
        aligned_stress = stress.reindex(stats.index).dropna()
        aligned_stats = stats.loc[aligned_stress.index]

        normal_stats = aligned_stats[~aligned_stress]
        stress_stats = aligned_stats[aligned_stress]

        summary_rows.append(
            {
                "asset": asset,
                "latest_beta": aligned_stats["beta"].iloc[-1],
                "latest_r_squared": aligned_stats["r_squared"].iloc[-1],
                "avg_beta_full_sample": aligned_stats["beta"].mean(),
                "avg_beta_normal_regime": normal_stats["beta"].mean(),
                "avg_beta_stress_regime": stress_stats["beta"].mean(),
                "max_rolling_beta": aligned_stats["beta"].max(),
                "min_rolling_beta": aligned_stats["beta"].min(),
                "avg_residual_vol_daily": aligned_stats["residual_vol_daily"].mean(),
            }
        )

    summary = pd.DataFrame(summary_rows).set_index("asset")
    summary.to_csv(TABLE_DIR / "rolling_beta_summary.csv")

    # Drawdown table and plots
    asset_drawdowns = returns[[BENCHMARK] + ASSETS].apply(drawdown)
    asset_drawdowns.to_csv(TABLE_DIR / "drawdowns.csv")

    save_rolling_beta_plot(
        rolling_stats,
        FIG_DIR / "rolling_beta_63d_vs_spy.png",
        title="63D Rolling Beta vs SPY",
    )
    save_rolling_r2_plot(
        rolling_stats,
        FIG_DIR / "rolling_r2_63d_vs_spy.png",
        title="63D Rolling R² vs SPY",
    )
    save_drawdown_plot(
        asset_drawdowns,
        FIG_DIR / "drawdowns.png",
        title="Drawdown Since 2020",
    )

    # Markdown research summary
    md = f"""# Week 01 — Rolling Beta Instability

## Research question

Does market sensitivity stay stable across regimes, or does beta rise exactly when diversification is needed most?

## Dataset

- Public tickers: {", ".join(TICKERS)}
- Benchmark: {BENCHMARK}
- Start date: {START_DATE}
- Frequency: daily returns
- Rolling window: {WINDOW} trading days

## Model

For each asset:

```text
r_asset,t = alpha + beta * r_SPY,t + error_t
```

Estimated using rolling OLS.

## Output table

{summary.round(4).to_markdown()}

## Interpretation guide

- Rising beta + rising R² means the asset is becoming more market-driven.
- Rising beta during stress means diversification may be weaker when it is needed most.
- Low R² means market beta is not the dominant driver; residual risk matters.
- Static beta can understate risk if exposure is unstable across regimes.

## Files generated

- `reports/week_01_rolling_beta_instability/tables/rolling_beta_summary.csv`
- `reports/week_01_rolling_beta_instability/figures/rolling_beta_63d_vs_spy.png`
- `reports/week_01_rolling_beta_instability/figures/rolling_r2_63d_vs_spy.png`
- `reports/week_01_rolling_beta_instability/figures/drawdowns.png`

## Disclaimer

For educational and analytical purposes only. Not investment advice.
"""
    (REPORT_DIR / "research_summary.md").write_text(md, encoding="utf-8")

    print("Week 01 research complete.")
    print(f"Summary saved to: {REPORT_DIR / 'research_summary.md'}")
    print(summary.round(4))


if __name__ == "__main__":
    main()

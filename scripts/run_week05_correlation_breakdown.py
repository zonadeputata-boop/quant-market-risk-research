"""Week 05 research script.

Correlation Breakdown:
Why static diversification can fail

Run from project root:
    PYTHONPATH=src python3 scripts/run_week05_correlation_breakdown.py
"""

from __future__ import annotations

from itertools import combinations
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from quant_research.data import download_prices
from quant_research.returns import simple_returns


START_DATE = "2020-01-01"
TICKERS = ["SPY", "QQQ", "TLT", "GLD", "HYG", "SHY", "^VIX"]
ASSETS = ["SPY", "QQQ", "TLT", "GLD", "HYG", "SHY"]
WINDOW = 63

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "raw" / "week05_prices.csv"
REPORT_DIR = ROOT / "reports" / "week_05_correlation_breakdown"
FIG_DIR = REPORT_DIR / "figures"
TABLE_DIR = REPORT_DIR / "tables"


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)

    prices = download_prices(TICKERS, start=START_DATE, cache_path=RAW_PATH)
    returns = simple_returns(prices)

    asset_returns = returns[ASSETS].dropna()
    spy_returns = asset_returns["SPY"]

    stress_threshold = spy_returns.quantile(0.10)
    stress_mask = spy_returns <= stress_threshold
    normal_mask = ~stress_mask

    rows = []
    for a, b in combinations(ASSETS, 2):
        normal_corr = asset_returns.loc[normal_mask, [a, b]].corr().iloc[0, 1]
        stress_corr = asset_returns.loc[stress_mask, [a, b]].corr().iloc[0, 1]
        full_corr = asset_returns[[a, b]].corr().iloc[0, 1]
        rows.append({
            "pair": f"{a}-{b}",
            "asset_1": a,
            "asset_2": b,
            "full_sample_corr": full_corr,
            "normal_corr": normal_corr,
            "stress_corr": stress_corr,
            "correlation_gap": stress_corr - normal_corr,
        })

    summary = pd.DataFrame(rows).sort_values("correlation_gap", ascending=False)
    summary.to_csv(TABLE_DIR / "correlation_breakdown_summary.csv", index=False)

    # Rolling correlations for selected pairs
    selected_pairs = [("SPY", "QQQ"), ("SPY", "HYG"), ("SPY", "TLT"), ("SPY", "GLD")]
    fig, ax = plt.subplots(figsize=(10, 5))
    for a, b in selected_pairs:
        rolling_corr = asset_returns[a].rolling(WINDOW).corr(asset_returns[b])
        rolling_corr.plot(ax=ax, label=f"{a}-{b}", linewidth=1.3)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_title(f"{WINDOW}-Day Rolling Correlation")
    ax.set_ylabel("Correlation")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG_DIR / "rolling_correlation_selected_pairs.png", dpi=200)
    plt.close(fig)

    # Stress vs normal chart
    top = summary.head(8).copy()
    fig, ax = plt.subplots(figsize=(10, 5))
    x = range(len(top))
    ax.bar([i - 0.18 for i in x], top["normal_corr"], width=0.36, label="Normal")
    ax.bar([i + 0.18 for i in x], top["stress_corr"], width=0.36, label="Stress")
    ax.set_xticks(list(x), top["pair"], rotation=30, ha="right")
    ax.set_ylabel("Correlation")
    ax.set_title("Normal vs Stress Correlation")
    ax.grid(axis="y", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG_DIR / "normal_vs_stress_correlation.png", dpi=200)
    plt.close(fig)

    md = f"""# Week 05 - Correlation Breakdown

## Research question

Does diversification survive stress, or do assets become more correlated when protection is needed most?

## Stress definition

```text
stress_day = SPY daily return <= 10th percentile
```

## Core diagnostic

```text
correlation_gap = corr_stress - corr_normal
```

## Summary: largest positive correlation gaps

{summary.head(10).round(4).to_markdown(index=False)}

## Output files

- `reports/week_05_correlation_breakdown/tables/correlation_breakdown_summary.csv`
- `reports/week_05_correlation_breakdown/figures/rolling_correlation_selected_pairs.png`
- `reports/week_05_correlation_breakdown/figures/normal_vs_stress_correlation.png`

## Disclaimer

For educational and analytical purposes only. Not investment advice.
"""
    (REPORT_DIR / "research_summary.md").write_text(md, encoding="utf-8")

    print("Week 05 research complete.")
    print(summary.head(10).round(4))


if __name__ == "__main__":
    main()

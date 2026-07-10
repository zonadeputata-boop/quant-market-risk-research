"""Week 04 research script.

VaR vs Expected Shortfall:
Where tail risk starts vs how bad it gets

Run from project root:
    PYTHONPATH=src python3 scripts/run_week04_var_expected_shortfall.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from quant_research.data import download_prices
from quant_research.returns import simple_returns
from quant_research.risk_metrics import historical_var, expected_shortfall, max_drawdown


START_DATE = "2020-01-01"
TICKERS = ["SPY", "QQQ", "TLT", "GLD", "HYG", "SHY"]

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "raw" / "week04_prices.csv"
REPORT_DIR = ROOT / "reports" / "week_04_var_expected_shortfall"
FIG_DIR = REPORT_DIR / "figures"
TABLE_DIR = REPORT_DIR / "tables"


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)

    prices = download_prices(TICKERS, start=START_DATE, cache_path=RAW_PATH)
    returns = simple_returns(prices)

    rows = []
    for ticker in TICKERS:
        r = returns[ticker].dropna()
        var_95 = historical_var(r, confidence=0.95)
        es_95 = expected_shortfall(r, confidence=0.95)
        rows.append({
            "asset": ticker,
            "var_95_daily": var_95,
            "expected_shortfall_95_daily": es_95,
            "tail_gap": es_95 - var_95,
            "worst_daily_return": r.min(),
            "daily_volatility": r.std(),
            "max_drawdown": max_drawdown(r),
        })

    summary = pd.DataFrame(rows).set_index("asset")
    summary.to_csv(TABLE_DIR / "tail_risk_summary.csv")

    # VaR vs ES chart
    fig, ax = plt.subplots(figsize=(9, 5))
    x = range(len(summary))
    ax.bar([i - 0.18 for i in x], summary["var_95_daily"] * 100, width=0.36, label="VaR 95%")
    ax.bar([i + 0.18 for i in x], summary["expected_shortfall_95_daily"] * 100, width=0.36, label="Expected Shortfall 95%")
    ax.set_xticks(list(x), summary.index)
    ax.set_ylabel("Daily return threshold / average tail loss (%)")
    ax.set_title("VaR vs Expected Shortfall")
    ax.grid(axis="y", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG_DIR / "var_vs_expected_shortfall.png", dpi=200)
    plt.close(fig)

    # Tail gap chart
    fig, ax = plt.subplots(figsize=(9, 5))
    gap = summary["tail_gap"].abs().sort_values(ascending=False)
    gap.plot(kind="bar", ax=ax)
    ax.set_title("Tail Gap: |Expected Shortfall - VaR|")
    ax.set_ylabel("Absolute tail gap")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "tail_gap.png", dpi=200)
    plt.close(fig)

    md = f"""# Week 04 - VaR vs Expected Shortfall

## Research question

Where does the left tail begin, and how much damage occurs after the threshold is breached?

## Metrics

```text
VaR_95 = 5th percentile of daily returns
ES_95 = average return when r_t < VaR_95
Tail gap = ES_95 - VaR_95
```

## Summary

{summary.round(4).to_markdown()}

## Output files

- `reports/week_04_var_expected_shortfall/tables/tail_risk_summary.csv`
- `reports/week_04_var_expected_shortfall/figures/var_vs_expected_shortfall.png`
- `reports/week_04_var_expected_shortfall/figures/tail_gap.png`

## Disclaimer

For educational and analytical purposes only. Not investment advice.
"""
    (REPORT_DIR / "research_summary.md").write_text(md, encoding="utf-8")

    print("Week 04 research complete.")
    print(summary.round(4))


if __name__ == "__main__":
    main()

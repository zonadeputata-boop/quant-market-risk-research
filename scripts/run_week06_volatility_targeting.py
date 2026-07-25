"""Week 06 research script.

Volatility Targeting:
Turning risk into position size

Run from project root:
    PYTHONPATH=src python3 scripts/run_week06_volatility_targeting.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from quant_research.data import download_prices
from quant_research.returns import simple_returns


START_DATE = "2020-01-01"
TICKERS = ["SPY", "QQQ", "TLT", "GLD", "HYG", "SHY"]
WINDOW = 63
TARGET_VOL = 0.10
MAX_EXPOSURE = 1.00

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "raw" / "week06_prices.csv"
REPORT_DIR = ROOT / "reports" / "week_06_volatility_targeting"
FIG_DIR = REPORT_DIR / "figures"
TABLE_DIR = REPORT_DIR / "tables"


def max_drawdown_from_returns(returns: pd.Series) -> float:
    equity = (1 + returns.dropna()).cumprod()
    drawdown = equity / equity.cummax() - 1
    return float(drawdown.min())


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)

    prices = download_prices(TICKERS, start=START_DATE, cache_path=RAW_PATH)
    returns = simple_returns(prices).dropna()

    realized_vol = returns.rolling(WINDOW).std() * (252 ** 0.5)
    raw_exposure = TARGET_VOL / realized_vol
    capped_exposure = raw_exposure.clip(upper=MAX_EXPOSURE)
    scaled_returns = returns * capped_exposure.shift(1)

    rows = []
    for ticker in TICKERS:
        r = returns[ticker].dropna()
        sr = scaled_returns[ticker].dropna()
        latest_vol = realized_vol[ticker].dropna().iloc[-1]
        latest_raw = raw_exposure[ticker].dropna().iloc[-1]
        latest_cap = capped_exposure[ticker].dropna().iloc[-1]

        rows.append({
            "asset": ticker,
            "latest_realized_vol": latest_vol,
            "target_vol": TARGET_VOL,
            "latest_raw_exposure": latest_raw,
            "latest_capped_exposure": latest_cap,
            "unscaled_ann_vol": r.std() * (252 ** 0.5),
            "scaled_ann_vol": sr.std() * (252 ** 0.5),
            "unscaled_max_drawdown": max_drawdown_from_returns(r),
            "scaled_max_drawdown": max_drawdown_from_returns(sr),
            "avg_abs_exposure_change": capped_exposure[ticker].diff().abs().mean(),
        })

    summary = pd.DataFrame(rows).set_index("asset")
    summary.to_csv(TABLE_DIR / "volatility_targeting_summary.csv")

    fig, ax = plt.subplots(figsize=(10, 5))
    realized_vol[TICKERS].plot(ax=ax, linewidth=1.2)
    ax.axhline(TARGET_VOL, color="black", linestyle="--", linewidth=1, label="Target vol")
    ax.set_title(f"{WINDOW}-Day Realized Volatility")
    ax.set_ylabel("Annualized volatility")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG_DIR / "rolling_realized_volatility.png", dpi=200)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 5))
    capped_exposure[TICKERS].plot(ax=ax, linewidth=1.2)
    ax.set_title("Capped Volatility-Targeted Exposure")
    ax.set_ylabel("Exposure multiplier")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "capped_target_exposure.png", dpi=200)
    plt.close(fig)

    md = f"""# Week 06 - Volatility Targeting

## Research question

If realized volatility changes through time, should position size stay fixed?

## Core rule

```text
raw_exposure_t = target_volatility / realized_volatility_t
capped_exposure_t = min(max_exposure, raw_exposure_t)
scaled_return_t = capped_exposure_(t-1) * return_t
```

## Parameters

```text
rolling window = {WINDOW} trading days
target volatility = {TARGET_VOL:.0%}
maximum exposure = {MAX_EXPOSURE:.1f}x
```

## Summary

{summary.round(4).to_markdown()}

## Output files

- `reports/week_06_volatility_targeting/tables/volatility_targeting_summary.csv`
- `reports/week_06_volatility_targeting/figures/rolling_realized_volatility.png`
- `reports/week_06_volatility_targeting/figures/capped_target_exposure.png`

## Disclaimer

For educational and analytical purposes only. Not investment advice.
"""
    (REPORT_DIR / "research_summary.md").write_text(md, encoding="utf-8")

    print("Week 06 research complete.")
    print(summary.round(4))


if __name__ == "__main__":
    main()

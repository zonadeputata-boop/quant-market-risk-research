"""Week 08 research script.

Liquidity-Adjusted Position Sizing:
Connecting volatility budgets with executable trading capacity.

Run from project root:
    PYTHONPATH=src python3 scripts/run_week08_liquidity_adjusted_position_sizing.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf


START_DATE = "2022-01-01"
TICKERS = ["SPY", "QQQ", "IWM", "TLT", "GLD", "HYG"]
VOL_WINDOW = 63
DOLLAR_VOLUME_WINDOW = 20
TARGET_VOL = 0.10
MAX_EXPOSURE = 1.00
PORTFOLIO_CAPITAL = 2_000_000_000.0
MAX_PARTICIPATION = 0.02
LIQUIDATION_DAYS = 2.0

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "raw" / "week08_price_volume.csv"
REPORT_DIR = ROOT / "reports" / "week_08_liquidity_adjusted_position_sizing"
FIG_DIR = REPORT_DIR / "figures"
TABLE_DIR = REPORT_DIR / "tables"


def download_market_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Download adjusted prices and volume, then write a reproducible cache."""

    data = yf.download(
        TICKERS,
        start=START_DATE,
        auto_adjust=True,
        group_by="column",
        progress=False,
        threads=True,
    )
    if data.empty:
        raise RuntimeError("No market data returned by yfinance.")

    close = data["Close"].copy()
    volume = data["Volume"].copy()
    close = close.reindex(columns=TICKERS).dropna(how="all")
    volume = volume.reindex(columns=TICKERS).reindex(close.index)

    RAW_PATH.parent.mkdir(parents=True, exist_ok=True)
    combined = pd.concat({"close": close, "volume": volume}, axis=1)
    combined.to_csv(RAW_PATH)
    return close, volume


def build_snapshot(close: pd.DataFrame, volume: pd.DataFrame) -> pd.DataFrame:
    returns = close.pct_change(fill_method=None)
    realized_vol = returns.rolling(VOL_WINDOW).std() * np.sqrt(252)
    dollar_volume = close * volume
    median_dollar_volume = dollar_volume.rolling(DOLLAR_VOLUME_WINDOW).median()

    latest_vol = realized_vol.shift(1).ffill().iloc[-1]
    latest_mdv = median_dollar_volume.shift(1).ffill().iloc[-1]

    volatility_scalar = (TARGET_VOL / latest_vol).clip(upper=MAX_EXPOSURE)
    base_notional = PORTFOLIO_CAPITAL * volatility_scalar
    liquidity_capacity = MAX_PARTICIPATION * latest_mdv * LIQUIDATION_DAYS
    liquidity_scalar = (liquidity_capacity / base_notional).clip(upper=1.0)
    final_notional = base_notional * liquidity_scalar
    liquidation_days = final_notional / (MAX_PARTICIPATION * latest_mdv)

    snapshot = pd.DataFrame(
        {
            "realized_volatility": latest_vol,
            "median_daily_dollar_volume": latest_mdv,
            "volatility_scalar": volatility_scalar,
            "base_notional": base_notional,
            "liquidity_capacity": liquidity_capacity,
            "liquidity_scalar": liquidity_scalar,
            "final_notional": final_notional,
            "final_portfolio_weight": final_notional / PORTFOLIO_CAPITAL,
            "implied_liquidation_days": liquidation_days,
        }
    )
    snapshot.index.name = "asset"
    return snapshot


def make_figures(snapshot: pd.DataFrame) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    notional = snapshot[["base_notional", "liquidity_capacity"]] / 1_000_000
    ax = notional.plot(kind="bar", figsize=(10, 5), color=["#AAB7C6", "#24679E"])
    ax.set_title("Volatility-Sized Notional vs Liquidity Capacity")
    ax.set_ylabel("USD millions")
    ax.set_xlabel("")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(["Volatility-sized notional", "Two-day liquidity capacity"], frameon=False)
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "notional_vs_liquidity_capacity.png", dpi=200)
    plt.close()

    ax = snapshot["liquidity_scalar"].plot(
        kind="bar", figsize=(10, 5), color="#24679E", ylim=(0, 1.1)
    )
    ax.set_title("Liquidity Scalar")
    ax.set_ylabel("Multiplier")
    ax.set_xlabel("")
    ax.grid(axis="y", alpha=0.25)
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "liquidity_scalar.png", dpi=200)
    plt.close()


def write_research_summary(snapshot: pd.DataFrame) -> None:
    summary = f"""# Week 08 - Liquidity-Adjusted Position Sizing

## Research question

If volatility sets the risk budget, what limits the amount that can actually be
traded?

## Parameters

```text
public tickers = {', '.join(TICKERS)}
volatility window = {VOL_WINDOW} trading days
dollar-volume window = {DOLLAR_VOLUME_WINDOW} trading days
target volatility = {TARGET_VOL:.0%}
maximum exposure = {MAX_EXPOSURE:.2f}x
portfolio capital = ${PORTFOLIO_CAPITAL / 1e9:.1f}bn
maximum participation = {MAX_PARTICIPATION:.0%}
liquidation horizon = {LIQUIDATION_DAYS:.0f} trading days
```

## Latest snapshot

{snapshot.round(4).to_markdown()}

## Output files

- `reports/week_08_liquidity_adjusted_position_sizing/tables/liquidity_adjusted_summary.csv`
- `reports/week_08_liquidity_adjusted_position_sizing/figures/notional_vs_liquidity_capacity.png`
- `reports/week_08_liquidity_adjusted_position_sizing/figures/liquidity_scalar.png`

## Limitation

The capacity rule does not model spreads, nonlinear market impact, stressed
volume or correlated portfolio liquidations.

## Disclaimer

For educational and analytical purposes only. Not investment advice.
"""
    (REPORT_DIR / "research_summary.md").write_text(summary, encoding="utf-8")


def main() -> None:
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    close, volume = download_market_data()
    snapshot = build_snapshot(close, volume)
    snapshot.to_csv(TABLE_DIR / "liquidity_adjusted_summary.csv")
    make_figures(snapshot)
    write_research_summary(snapshot)
    print("Week 08 research complete.")
    print(snapshot.round(4))


if __name__ == "__main__":
    main()

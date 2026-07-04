"""Week 03 research script.

Factor Regression:
What SPY beta misses

Run from project root:
    PYTHONPATH=src python3 scripts/run_week03_factor_regression.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import statsmodels.api as sm

from quant_research.data import download_prices
from quant_research.returns import simple_returns


START_DATE = "2020-01-01"

TICKERS = ["SPY", "QQQ", "TLT", "GLD", "HYG", "SHY", "UUP"]
TARGETS = ["QQQ", "GLD", "HYG", "TLT", "SHY"]

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "raw" / "week03_prices.csv"
REPORT_DIR = ROOT / "reports" / "week_03_factor_regression"
FIG_DIR = REPORT_DIR / "figures"
TABLE_DIR = REPORT_DIR / "tables"


def run_factor_regression(y: pd.Series, x: pd.DataFrame):
    data = pd.concat([y.rename("target"), x], axis=1).dropna()
    y_clean = data["target"]
    x_clean = sm.add_constant(data.drop(columns="target"))
    return sm.OLS(y_clean, x_clean).fit()


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)

    prices = download_prices(TICKERS, start=START_DATE, cache_path=RAW_PATH)
    returns = simple_returns(prices)

    factor_sets = {
        "QQQ": ["SPY", "TLT", "UUP", "HYG", "GLD"],
        "GLD": ["SPY", "TLT", "UUP", "HYG"],
        "HYG": ["SPY", "TLT", "UUP", "GLD"],
        "TLT": ["SPY", "SHY", "UUP", "HYG", "GLD"],
        "SHY": ["SPY", "TLT", "UUP", "HYG", "GLD"],
    }

    rows = []
    coeff_tables = []

    for target in TARGETS:
        factors = factor_sets[target]
        model = run_factor_regression(returns[target], returns[factors])

        rows.append({
            "target": target,
            "r_squared": model.rsquared,
            "adj_r_squared": model.rsquared_adj,
            "alpha_daily": model.params.get("const"),
            "alpha_t_stat": model.tvalues.get("const"),
            "residual_vol_daily": model.resid.std(),
            "n_obs": int(model.nobs),
        })

        coeff = pd.DataFrame({
            "target": target,
            "factor": model.params.index,
            "coefficient": model.params.values,
            "t_stat": model.tvalues.values,
            "p_value": model.pvalues.values,
        })
        coeff_tables.append(coeff)

    summary = pd.DataFrame(rows).set_index("target")
    coeffs = pd.concat(coeff_tables, ignore_index=True)

    summary.to_csv(TABLE_DIR / "factor_regression_summary.csv")
    coeffs.to_csv(TABLE_DIR / "factor_regression_coefficients.csv", index=False)

    fig, ax = plt.subplots(figsize=(9, 5))
    summary["r_squared"].sort_values(ascending=False).plot(kind="bar", ax=ax)
    ax.set_title("Multi-Factor Regression R2 by Asset")
    ax.set_ylabel("R2")
    ax.set_ylim(0, 1)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "multifactor_r2_by_asset.png", dpi=200)
    plt.close(fig)

    md = f"""# Week 03 - Factor Regression

## Research question

After controlling for SPY beta, which additional economic factors may explain the remaining risk?

## Model

```text
r_i,t = alpha + beta_EQ*Equity_t + beta_RATE*Rates_t + beta_USD*USD_t + beta_CREDIT*Credit_t + beta_GOLD*Gold_t + epsilon_t
```

## Summary

{summary.round(4).to_markdown()}

## Output files

- `reports/week_03_factor_regression/tables/factor_regression_summary.csv`
- `reports/week_03_factor_regression/tables/factor_regression_coefficients.csv`
- `reports/week_03_factor_regression/figures/multifactor_r2_by_asset.png`

## Disclaimer

For educational and analytical purposes only. Not investment advice.
"""
    (REPORT_DIR / "research_summary.md").write_text(md, encoding="utf-8")

    print("Week 03 research complete.")
    print(summary.round(4))


if __name__ == "__main__":
    main()

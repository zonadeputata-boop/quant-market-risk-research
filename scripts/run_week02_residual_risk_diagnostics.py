"""Week 02 research script.

Residual Risk Diagnostics:
Why beta is not enough without R-squared.

This script uses the Week 01 rolling OLS output and converts it into a
single-factor risk diagnostics dashboard.

Run from repo root:
    PYTHONPATH=src python3 scripts/run_week02_residual_risk_diagnostics.py
"""

from __future__ import annotations

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
WEEK01_TABLES = ROOT / "reports" / "week_01_rolling_beta_instability" / "tables"
OUT = ROOT / "reports" / "week_02_residual_risk_diagnostics"
FIG_DIR = OUT / "figures"
TABLE_DIR = OUT / "tables"


def main() -> None:
    source = WEEK01_TABLES / "rolling_beta_summary.csv"
    if not source.exists():
        raise FileNotFoundError(
            f"Missing {source}. Run Week 01 first: "
            "PYTHONPATH=src python3 scripts/run_week01_rolling_beta.py"
        )

    df = pd.read_csv(source, index_col=0)
    df.index.name = "asset"

    required = ["latest_beta", "latest_r_squared", "avg_beta_stress_regime"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in Week 01 summary: {missing}")

    diag = df[required].copy()
    diag = diag.rename(columns={
        "latest_beta": "latest_beta",
        "latest_r_squared": "latest_r2",
        "avg_beta_stress_regime": "stress_beta",
    })
    diag["unexplained_share"] = 1 - diag["latest_r2"]

    def label(row):
        if row["latest_beta"] > 1 and row["latest_r2"] > 0.70:
            return "Equity beta dominates"
        if row["latest_r2"] < 0.50:
            return "SPY is not enough"
        if row["latest_beta"] > 0 and row["latest_r2"] > 0.60:
            return "Market-linked risk"
        return "Mixed driver"

    diag["risk_read"] = diag.apply(label, axis=1)

    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    diag.to_csv(TABLE_DIR / "residual_risk_diagnostics.csv")

    # Explained vs unexplained chart
    order = diag.sort_values("latest_r2", ascending=False)
    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.bar(order.index, order["latest_r2"], label="Explained by SPY")
    ax.bar(order.index, order["unexplained_share"], bottom=order["latest_r2"], label="Unexplained")
    ax.set_ylim(0, 1)
    ax.set_ylabel("Share of variance")
    ax.set_title("Single-Factor Model: Explained vs Unexplained")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "r2_explained_unexplained.png", dpi=200)
    plt.close(fig)

    # Beta vs unexplained risk map
    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.scatter(diag["latest_beta"], diag["unexplained_share"], s=150)
    for asset, row in diag.iterrows():
        ax.annotate(asset, (row["latest_beta"], row["unexplained_share"]), xytext=(7, 7), textcoords="offset points")
    ax.axvline(1, linestyle="--", linewidth=1)
    ax.axhline(0.5, linestyle="--", linewidth=1)
    ax.set_xlabel("Latest rolling beta vs SPY")
    ax.set_ylabel("Unexplained share = 1 - R²")
    ax.set_title("Beta vs Unexplained Risk")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "beta_vs_unexplained_share.png", dpi=200)
    plt.close(fig)

    md = f"""# Week 02 - Residual Risk Diagnostics

## Research question

After controlling for SPY beta, what part of asset risk remains unexplained by the market factor?

## Model

```text
r_asset,t = alpha + beta x r_SPY,t + epsilon_t
```

## Diagnostics

{diag.round(4).to_markdown()}

## Interpretation

- Beta measures sensitivity to the benchmark.
- R² measures how much of the return path the benchmark explains.
- 1 - R² is a simple unexplained-risk proxy.
- Residual risk is not automatically alpha; it can be missing factor exposure, noise, liquidity risk or true idiosyncratic return.

## Disclaimer

For educational and analytical purposes only. Not investment advice.
"""
    (OUT / "research_summary.md").write_text(md, encoding="utf-8")
    print("Week 02 research complete.")
    print(diag.round(4))


if __name__ == "__main__":
    main()

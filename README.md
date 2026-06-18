# Quant Market Risk Research for LinkedIn

A GitHub-ready Python research repository for weekly LinkedIn carousel posts focused on:

- Quant trading research
- Portfolio risk analytics
- Market regime analysis
- Statistical signal validation
- Tail risk and exposure diagnostics

The goal is to make each LinkedIn post look like a compact institutional research note:

`data -> model -> diagnostics -> result -> risk/trading implication`.

## Week 01 Research Note

**Rolling Beta Instability: Why Static Beta Can Mislead Risk Sizing**

Research question:

> Does market sensitivity stay stable across regimes, or does beta rise exactly when diversification is needed most?

Default public tickers:

| Role | Ticker |
|---|---|
| Equity benchmark | SPY |
| Growth / high beta equity | QQQ |
| Long duration bonds | TLT |
| Gold proxy | GLD |
| High yield credit proxy | HYG |
| Short Treasury / cash-like proxy | SHY |
| Volatility regime filter | ^VIX |

## Repository structure

```text
quant_linkedin_research_repo/
├── src/quant_research/
│   ├── data.py
│   ├── returns.py
│   ├── rolling_models.py
│   ├── risk_metrics.py
│   └── plots.py
├── scripts/
│   └── run_week01_rolling_beta.py
├── notebooks/
│   └── 01_rolling_beta_instability.ipynb
├── posts/
│   └── week_01_rolling_beta_instability/
│       ├── carousel.md
│       ├── caption.md
│       └── methodology.md
├── reports/
│   └── week_01_rolling_beta_instability/
│       ├── figures/
│       └── tables/
├── tests/
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # macOS / Linux
# .venv\Scripts\activate  # Windows

pip install -r requirements.txt
python scripts/run_week01_rolling_beta.py
```

The script downloads public market data, estimates rolling beta and rolling R², generates tables and figures, and writes a markdown research summary.

## LinkedIn content workflow

For each weekly post:

1. Run the Python research script.
2. Export tables and charts.
3. Use `posts/week_xx/.../carousel.md` to build carousel slides.
4. Use `caption.md` for the LinkedIn caption.
5. Add GitHub link to the post.

## Disclaimer

This repository is for educational and analytical purposes only. It is not investment advice.

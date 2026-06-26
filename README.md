# Quant Market Risk Research

A reproducible Python research repository for quant market risk, portfolio analytics, and trading-risk diagnostics.

The project is designed as a public research portfolio: each note follows a compact institutional workflow:

```text
data -> model -> diagnostics -> interpretation -> portfolio / trading implication
```

The goal is to demonstrate practical skills relevant to:

- Quant Trading
- Market Risk Analysis
- Portfolio Analytics
- Asset Management Research
- Systematic Research
- Risk Management

## Research focus

This repository contains short research notes built with public market data and Python.

Typical topics include:

- Rolling beta and time-varying market exposure
- Residual risk and model diagnostics
- Factor regression and return attribution
- Correlation and regime dependency
- VaR, Expected Shortfall and tail-risk analysis
- Volatility targeting and risk-based position sizing
- Drawdown, stress testing and portfolio survival
- Signal validation, robustness checks and model limitations

## Repository structure

```text
quant-market-risk-research/
├── src/
│   └── quant_research/
│       ├── data.py
│       ├── returns.py
│       ├── rolling_models.py
│       ├── risk_metrics.py
│       └── plots.py
│
├── scripts/
│   └── run_weekXX_topic_name.py
│
├── notebooks/
│   └── XX_topic_name.ipynb
│
├── posts/
│   └── week_XX_topic_name/
│       ├── caption.md
│       ├── carousel.md
│       └── methodology.md
│
├── reports/
│   └── week_XX_topic_name/
│       ├── figures/
│       ├── tables/
│       └── research_summary.md
│
├── data/
│   ├── raw/
│   └── processed/
│
├── tests/
├── requirements.txt
├── pyproject.toml
└── README.md
```

## How each research note is organized

Each weekly research note uses the same structure:

| Folder | Purpose |
|---|---|
| `scripts/` | Python script used to run the analysis |
| `notebooks/` | Optional exploratory notebook |
| `posts/week_XX_topic_name/` | LinkedIn caption, carousel text and methodology |
| `reports/week_XX_topic_name/figures/` | Charts generated from the analysis |
| `reports/week_XX_topic_name/tables/` | CSV outputs and diagnostics |
| `reports/week_XX_topic_name/research_summary.md` | Short research summary and interpretation |

This keeps the project scalable: new research notes can be added without changing the main README every week.

## Current research notes

Research notes are stored in the `posts/` and `reports/` folders.

To view available notes, open:

```text
posts/
reports/
scripts/
```

Each note is self-contained and includes:

- research question,
- data assumptions,
- model specification,
- statistical output,
- interpretation,
- limitations,
- LinkedIn-ready content.

## Data

The project uses public market data, primarily through Yahoo Finance via `yfinance`.

Examples of public tickers used across notes:

| Ticker | Role |
|---|---|
| `SPY` | US equity benchmark |
| `QQQ` | Growth / high-beta equity proxy |
| `TLT` | Long-duration Treasury proxy |
| `GLD` | Gold proxy |
| `HYG` | High-yield credit proxy |
| `SHY` | Short Treasury / cash-like proxy |
| `^VIX` | Equity volatility regime proxy |

Raw data is generally excluded from version control. Research outputs, charts and summary tables may be stored in `reports/`.

## Installation

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Running a research note

Run an individual script from the project root.

Example:

```bash
PYTHONPATH=src python3 scripts/run_week01_rolling_beta.py
```

For future notes, use the same pattern:

```bash
PYTHONPATH=src python3 scripts/run_weekXX_topic_name.py
```

Generated outputs are saved under:

```text
reports/week_XX_topic_name/
```

## Research workflow

Each note follows this process:

1. Define a market or risk question.
2. Select public asset proxies.
3. Download and clean data.
4. Calculate returns and core metrics.
5. Estimate the model.
6. Generate diagnostics.
7. Convert findings into portfolio or trading implications.
8. Document limitations.
9. Export charts, tables and LinkedIn-ready content.

## Example model types

The repository may include models such as:

```text
r_asset,t = alpha + beta * r_benchmark,t + error_t
```

```text
portfolio risk = weights' * covariance matrix * weights
```

```text
VaR = historical return quantile
Expected Shortfall = average loss beyond VaR
```

```text
target exposure = target volatility / realized volatility
```

Models are used as diagnostic tools, not as standalone trading systems.

## What this project is meant to show

This repository demonstrates:

- Python-based research workflow
- Market data handling
- Return and risk analytics
- Regression-based diagnostics
- Model-risk awareness
- Portfolio and trading interpretation
- Clear research communication
- Reproducible analysis suitable for professional review

## Limitations

This project is educational and analytical.

Important limitations:

- Public proxy data may not fully represent tradable portfolios.
- Results are sensitive to sample period, frequency and window length.
- Rolling models are backward-looking.
- Simple factor models may omit important drivers.
- Transaction costs, taxes, financing costs and liquidity constraints are not always included.
- Historical relationships may break under regime shifts.

## Disclaimer

This repository is for educational and analytical purposes only.

Nothing in this repository is investment advice, trading advice, or a recommendation to buy or sell any security.

All calculations are based on public data and simplified assumptions.

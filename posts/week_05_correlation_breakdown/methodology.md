# Methodology - Week 05 Correlation Breakdown

## Objective

Measure whether diversification relationships change under market stress.

## Research question

Does diversification survive stress, or do assets become more correlated when protection is needed most?

## Data

The script uses public Yahoo Finance tickers via `yfinance`:

- SPY
- QQQ
- TLT
- GLD
- HYG
- SHY
- ^VIX

Frequency: daily returns.

## Diagnostics

Rolling correlation:

```text
rolling_corr_ij,t = corr(r_i, r_j) over a 63-day window
```

Stress-day definition:

```text
stress_day = SPY daily return <= 10th percentile
```

Correlation gap:

```text
correlation_gap = corr_stress - corr_normal
```

## Interpretation

- Positive gap: assets move more together during stress.
- Negative gap: assets become more diversifying during stress.
- Large absolute gap: static correlation assumption is fragile.
- Rising equity-credit correlation can indicate hidden risk-on concentration.
- Weakening bond-equity diversification can reduce hedge effectiveness.

## Limitations

- Historical stress regimes may not repeat.
- Correlation is linear and may miss non-linear dependence.
- Stress definition changes the output.
- ETF proxies may not fully represent investable portfolios.
- Liquidity, execution gaps and funding stress are not fully captured.

This is a diagnostic framework, not investment advice.

# Methodology — Week 01 Rolling Beta Instability

## Objective

Estimate whether asset market sensitivity versus SPY is stable through time and across regimes.

## Data

Public Yahoo Finance tickers via `yfinance`:

- SPY
- QQQ
- TLT
- GLD
- HYG
- SHY
- ^VIX

Frequency: daily  
Start date: 2020-01-01

## Return definition

Simple daily returns:

```text
r_t = P_t / P_{t-1} - 1
```

## Rolling OLS model

For each asset:

```text
r_asset,t = alpha + beta × r_SPY,t + error_t
```

Rolling window: 63 trading days.

## Stress regime definition

Stress regime is flagged when either condition is true:

```text
VIX > 25
or
SPY drawdown < -10%
```

## Core diagnostics

| Metric | Use |
|---|---|
| beta | Market sensitivity |
| R² | Share of return explained by SPY |
| residual volatility | Unexplained daily risk |
| alpha t-stat | Statistical strength of unexplained return |
| beta t-stat | Statistical strength of market exposure |

## Limitations

- Rolling beta is backward-looking.
- Window length changes results.
- OLS assumes linearity.
- Beta does not capture liquidity cost, gap risk or non-linear payoff.
- VIX threshold is a simple regime rule, not a full classifier.

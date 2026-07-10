# Methodology - Week 04 VaR vs Expected Shortfall

## Objective

Compare Value-at-Risk and Expected Shortfall as tail-risk diagnostics for public asset proxies.

## Research question

Where does the left tail begin, and how much damage occurs after the threshold is breached?

## Data

The script uses public Yahoo Finance tickers via `yfinance`:

- SPY
- QQQ
- TLT
- GLD
- HYG
- SHY

Frequency: daily returns.

## Metrics

Historical VaR at 95% confidence:

```text
VaR_95 = 5th percentile of daily returns
```

Expected Shortfall at 95% confidence:

```text
ES_95 = average return when r_t < VaR_95
```

Tail gap:

```text
Tail gap = ES_95 - VaR_95
```

## Interpretation

- VaR estimates the loss threshold.
- Expected Shortfall estimates the average loss beyond that threshold.
- A larger ES-VaR gap indicates deeper losses once VaR is breached.
- Tail-risk diagnostics should be linked to sizing, leverage, hedging and stop-loss assumptions.

## Limitations

- Historical simulation is backward-looking.
- Results depend on the sample period and return frequency.
- VaR and ES do not predict the next tail event.
- Liquidity costs, taxes, financing and execution gaps may increase realized losses.
- Public ETF proxies may not fully represent investable portfolios.

This is a diagnostic framework, not investment advice.

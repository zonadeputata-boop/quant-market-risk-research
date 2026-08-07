# Week 08 - Liquidity-Adjusted Position Sizing

## Research question

If volatility sets the risk budget, what limits the amount that can actually be
traded?

## Parameters

```text
public tickers = SPY, QQQ, IWM, TLT, GLD, HYG
volatility window = 63 trading days
dollar-volume window = 20 trading days
target volatility = 10%
maximum exposure = 1.00x
illustrative portfolio capital = $2.0bn
maximum participation = 2%
liquidation horizon = 2 trading days
```

## Interpretation

Volatility sets the base notional. Median dollar volume, the participation
limit and the liquidation horizon define executable capacity. The final
notional is the lower of the two.

## Important limitation

The capacity rule is intentionally simple. A production implementation should
also estimate spreads, nonlinear market impact, stressed volume, correlated
liquidations and implementation shortfall.

## Disclaimer

For educational and analytical purposes only. Not investment advice.

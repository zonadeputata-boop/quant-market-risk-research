# Methodology - Week 07 Drawdown-Aware Position Sizing

## Objective

Add a capital-path constraint to a volatility-targeted position-sizing rule.

## Core rules

```text
volatility_scalar_t = min(
    max_exposure,
    target_volatility / realized_volatility_(t-1)
)

drawdown_t = strategy_equity_(t-1) / running_peak_(t-1) - 1

drawdown_scalar_t = clip(
    1 + drawdown_t / drawdown_budget,
    min_drawdown_scalar,
    1
)

final_exposure_t = volatility_scalar_t * drawdown_scalar_t
strategy_return_t = final_exposure_t * asset_return_t
```

## Controls

- Public ETF tickers: SPY, QQQ, TLT, GLD, HYG and SHY.
- Realized volatility window: 63 trading days.
- Target volatility: 10%.
- Maximum exposure: 1.00x.
- Drawdown budget: 20%.
- Minimum drawdown scalar: 0.25.
- All risk inputs are lagged before the current return is applied.

## Interpretation

Volatility determines the base position size. Drawdown determines how much of
that risk budget remains after the strategy has moved below its running peak.

This is a diagnostic framework, not investment advice.

# Methodology - Week 06 Volatility Targeting

## Objective

Translate realized volatility into a position-sizing rule.

## Core rules

```text
realized_vol_t = std(r_t over rolling window) * sqrt(252)
raw_exposure_t = target_volatility / realized_volatility_t
capped_exposure_t = min(max_exposure, raw_exposure_t)
scaled_return_t = capped_exposure_{t-1} * return_t
```

This is a diagnostic framework, not investment advice.

# Methodology

The framework uses lagged price and volume information to combine volatility
targeting with a simple liquidity-capacity rule.

```text
volatility_scalar_t = min(
    max_exposure,
    target_volatility / realized_volatility_(t-1)
)

base_notional_t = portfolio_capital * volatility_scalar_t

liquidity_capacity_t = (
    participation_rate
    * median_daily_dollar_volume_(t-1)
    * liquidation_days
)

liquidity_scalar_t = min(
    1,
    liquidity_capacity_t / base_notional_t
)

final_notional_t = base_notional_t * liquidity_scalar_t
```

The rule is a transparent pre-trade control. It is not a complete transaction-
cost or market-impact model.

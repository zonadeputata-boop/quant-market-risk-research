# Week 09 methodology — Portfolio-Level Volatility Targeting

## Objective

Separate standalone sleeve normalisation from portfolio-level volatility control, then measure the tracking-cost trade-off created by the rebalancing rule.

## Universe and capital weights

The example uses SPY, QQQ, TLT, GLD, HYG and SHY with fixed base capital weights of 25%, 20%, 20%, 15%, 10% and 10%. The base weights are an explicit design input, not an optimisation result.

## Information timing

For trading day *t*, the 63-day volatility and covariance estimates use returns through *t−1*. Exposures are then set for day *t*. This avoids using same-day returns to size same-day exposure.

## Sleeve normalisation

For sleeve *i*:

```text
s_i,t = clip(10% / sigma_i,t-1, 0, 2.0)
y_i,t = base_weight_i * s_i,t
```

The 10% number is a normalisation anchor. It is not a claim that each sleeve contributes 10% portfolio volatility.

## Portfolio target

Using the annualised rolling sample covariance matrix:

```text
forecast_vol_t = sqrt(y_t' Sigma_t-1 y_t)
portfolio_scalar_t = clip(10% / forecast_vol_t, 0, 2.0)
x*_t = portfolio_scalar_t * y_t
```

If gross exposure exceeds 1.5x, the entire vector is scaled proportionally. The capped forecast may therefore remain below target.

## Rebalancing policies

- **Daily:** reset to the current target every trading day.
- **Weekly:** reset on the last available observation in each Friday-ending week.
- **Volatility band:** reset when the forecast volatility of the drifted pre-trade exposure falls outside 9%–11%.

Between rebalances, exposures drift with asset returns. Turnover is the sum of absolute changes from the drifted pre-trade vector to the post-trade vector.

## Transaction cost

```text
cost_t = turnover_t * 5 / 10,000
net_return_t = exposure_t' return_t - cost_t
```

The 5 bps assumption is deliberately simple and should be replaced by asset- and size-specific spread, impact and financing estimates for implementation work.

## Published historical sample

The published package runs the live path on Yahoo Finance adjusted closes for SPY, QQQ, TLT, GLD, HYG and SHY from 2 January 2020 to 14 August 2026. After aligning complete price observations, the sample contains 1,662 daily return observations; the first 63 are used to initialise the rolling risk estimate.

The historical backtest is evidence about this specific model and sample only. It is not an estimate of expected returns and does not establish that the same rebalancing ranking will persist. The optional `--demo` path remains available as an offline deterministic mechanics check.

## Reported diagnostics

- realised annualised volatility of net returns,
- average forecast volatility,
- mean absolute forecast-to-target error,
- annualised turnover,
- annualised modeled cost drag,
- maximum drawdown,
- rebalance count.

## Limitations

The implementation uses a rolling sample covariance matrix. It does not model shrinkage, conditional covariance dynamics, volatility-of-volatility, spread changes, nonlinear market impact, financing, taxes or intraday execution. The volatility target is a forecast objective, not a guarantee.

For educational and analytical purposes only. Not investment advice.

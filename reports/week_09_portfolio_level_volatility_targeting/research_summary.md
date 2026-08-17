# Week 09 - Portfolio-Level Volatility Targeting

## Research question

Why does sizing every sleeve to its own volatility fail to set portfolio volatility?

## Two-stage rule

```text
sleeve_scalar_i,t = clip(sleeve_vol_anchor / forecast_vol_i,t-1)
sleeve_exposure_t = base_weight .* sleeve_scalar_t
portfolio_forecast_t = sqrt(sleeve_exposure_t' * covariance_t-1 * sleeve_exposure_t)
portfolio_scalar_t = clip(portfolio_target / portfolio_forecast_t)
target_exposure_t = gross_cap(portfolio_scalar_t * sleeve_exposure_t)
```

## Rebalancing and cost

```text
turnover_t = sum(abs(target_exposure_t - pre_trade_exposure_t))
cost_t = turnover_t * 5.0 bps
```

The comparison includes daily, weekly, and ±10% volatility-band
rebalancing. Inputs for day t use returns through t-1. Between rebalances,
exposures drift with asset returns.

## Parameters

```text
source = Yahoo Finance adjusted closes; 2020-01-02 to 2026-08-14; 1662 return observations
assets = SPY, QQQ, TLT, GLD, HYG, SHY
covariance and volatility window = 63 trading days
sleeve volatility anchor = 10%
portfolio volatility target = 10%
maximum sleeve scalar = 2.0x
maximum portfolio scalar = 2.0x
maximum gross exposure = 1.5x
modeled one-way transaction cost = 5.0 bps
```

## Strategy comparison

| policy | realized_annualized_volatility | average_forecast_volatility | mean_absolute_target_error | annualized_turnover | annualized_cost_drag | maximum_drawdown | rebalance_count |
| --- | --- | --- | --- | --- | --- | --- | --- |
| sleeve_only_daily | 0.0657 | 0.0629 | 0.0371 | 2.2152 | 0.0011 | -0.1386 | 1599 |
| two_stage_daily | 0.0996 | 0.0956 | 0.0044 | 4.0599 | 0.002 | -0.2101 | 1599 |
| two_stage_weekly | 0.1008 | 0.0955 | 0.0055 | 2.4109 | 0.0012 | -0.211 | 333 |
| two_stage_band_10pct | 0.1011 | 0.0966 | 0.0068 | 1.9097 | 0.001 | -0.2166 | 381 |

## Interpretation boundary

The volatility forecast is a model output, not a guarantee. The results are historical, model-dependent backtest diagnostics for the stated ETF sample. They are not expected-return estimates and do not establish that the policy ranking will persist.

## Limitations

The estimator is a simple rolling sample covariance. Production use should test
shrinkage, stress covariance, volatility-of-volatility, financing, nonlinear
market impact, exposure constraints, and execution timing.

## Disclaimer

For educational and analytical purposes only. Not investment advice.

Position-by-position volatility scaling does **not by itself** set volatility at the portfolio level.

If every sleeve is normalised to the same standalone volatility, portfolio risk still depends on the covariance matrix:

```text
portfolio volatility = sqrt(x' Σ x)
```

The practical process therefore has two stages:

1. Normalise each sleeve using a lagged volatility estimate.
2. Estimate portfolio volatility from the full covariance matrix and apply a separate portfolio-level scalar.

This distinction matters most when individual positions look ordinary but correlations rise. The same sleeve volatilities can produce a very different portfolio number when assets start moving together.

I also made the rebalancing rule explicit. I compared daily, weekly and ±10% volatility-band rebalancing, with turnover charged at a simplified 5 bps per unit traded. The implementation and evaluation of a volatility target depend on the rebalancing policy.

The portfolio-level rule is:

```text
sleeve scalar_i,t = clip(sleeve vol anchor / forecast vol_i,t-1)
sleeve exposure_t = base weight .* sleeve scalar_t
portfolio forecast_t = sqrt(sleeve exposure_t' Σ_t-1 sleeve exposure_t)
portfolio scalar_t = clip(portfolio target / portfolio forecast_t)
target exposure_t = gross cap(portfolio scalar_t * sleeve exposure_t)
```

All inputs for day *t* use data available through *t−1*. I ran the packaged backtest on adjusted closes for SPY, QQQ, TLT, GLD, HYG and SHY from 2 January 2020 to 14 August 2026.

In this historical sample, daily rebalancing had the smallest mean forecast-to-target gap: 44 annualised volatility bps, versus 55 for weekly and 68 for the band rule. It also had the highest modeled annualised cost: 20.3 bps, versus 12.1 and 9.5 bps. These are model-dependent backtest diagnostics, not expected returns or a claim that daily rebalancing is universally preferable.

The broader lesson: a portfolio-level volatility target requires weights, covariance, portfolio constraints and an explicit rebalancing rule. Position-level scaling is only the first layer.

Data: Yahoo Finance adjusted closes. Risk model: 63-day rolling sample covariance. Costs exclude financing, taxes, nonlinear market impact and asset-specific execution differences.

#QuantFinance #PortfolioRisk #VolatilityTargeting #SystematicInvesting #RiskManagement #Python

For educational and analytical purposes only. Not investment advice.

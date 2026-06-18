# Week 01 — Rolling Beta Instability

## Research question

Does market sensitivity stay stable across regimes, or does beta rise exactly when diversification is needed most?

## Dataset

- Public tickers: SPY, QQQ, TLT, GLD, HYG, SHY, ^VIX
- Benchmark: SPY
- Start date: 2020-01-01
- Frequency: daily returns
- Rolling window: 63 trading days

## Model

For each asset:

```text
r_asset,t = alpha + beta * r_SPY,t + error_t
```

Estimated using rolling OLS.

## Output table

| asset   |   latest_beta |   latest_r_squared |   avg_beta_full_sample |   avg_beta_normal_regime |   avg_beta_stress_regime |   max_rolling_beta |   min_rolling_beta |   avg_residual_vol_daily |
|:--------|--------------:|-------------------:|-----------------------:|-------------------------:|-------------------------:|-------------------:|-------------------:|-------------------------:|
| QQQ     |        1.426  |             0.8682 |                 1.2378 |                   1.2492 |                   1.2132 |             1.5089 |             0.817  |                   0.0048 |
| TLT     |        0.2772 |             0.2233 |                 0.0237 |                   0.0544 |                  -0.0425 |             0.7298 |            -0.6688 |                   0.0095 |
| GLD     |        1.1717 |             0.426  |                 0.171  |                   0.1874 |                   0.1357 |             1.2726 |            -0.8899 |                   0.0103 |
| HYG     |        0.2691 |             0.6983 |                 0.3097 |                   0.2714 |                   0.3923 |             0.5604 |             0.1375 |                   0.0029 |
| SHY     |        0.0638 |             0.3492 |                 0.0066 |                   0.0073 |                   0.0049 |             0.0803 |            -0.1595 |                   0.001  |

## Interpretation guide

- Rising beta + rising R² means the asset is becoming more market-driven.
- Rising beta during stress means diversification may be weaker when it is needed most.
- Low R² means market beta is not the dominant driver; residual risk matters.
- Static beta can understate risk if exposure is unstable across regimes.

## Files generated

- `reports/week_01_rolling_beta_instability/tables/rolling_beta_summary.csv`
- `reports/week_01_rolling_beta_instability/figures/rolling_beta_63d_vs_spy.png`
- `reports/week_01_rolling_beta_instability/figures/rolling_r2_63d_vs_spy.png`
- `reports/week_01_rolling_beta_instability/figures/drawdowns.png`

## Disclaimer

For educational and analytical purposes only. Not investment advice.

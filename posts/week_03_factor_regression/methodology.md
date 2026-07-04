# Methodology - Week 03 Factor Regression

## Objective

Extend the residual-risk diagnostic framework into a multi-factor research process.

## Research question

After controlling for SPY beta, which additional economic factors may explain the remaining risk?

## Factor candidates

| Factor | Public proxy examples | Risk captured |
|---|---|---|
| Equity | SPY | Broad market beta |
| Rates | TLT, SHY | Duration and rate sensitivity |
| USD | UUP / DXY proxy | Dollar liquidity |
| Credit | HYG, LQD | Credit-risk appetite |
| Gold | GLD | Real-rate / safe-haven behavior |

## Model

```text
r_i,t = alpha + beta_EQ*Equity_t + beta_RATE*Rates_t + beta_USD*USD_t + beta_CREDIT*Credit_t + beta_GOLD*Gold_t + epsilon_t
```

## Diagnostics

- coefficient sign and economic logic,
- t-stat and p-value,
- R2 improvement versus single-factor model,
- residual volatility,
- residual autocorrelation,
- rolling coefficient stability,
- out-of-sample robustness.

## Limitations

- Public ETF proxies are imperfect factor proxies.
- Factor collinearity can distort coefficients.
- Results are sensitive to the sample window.
- Linear regression does not capture non-linear exposure.
- Transaction costs, taxes, financing and liquidity constraints are excluded.

This is a diagnostic framework, not a standalone trading system.

# Slide 1 — Portfolio-Level Volatility Targeting

Why sleeve targets do not set portfolio risk

# Slide 2 — The portfolio layer

Normalising every sleeve to its own volatility does not set the portfolio target.

Correlations finish the calculation — and they can change on a different clock.

# Slide 3 — Same sleeves, different portfolio

With six equally weighted 10%-volatility sleeves:

- pairwise correlation 0.10 → portfolio volatility 5.0%
- pairwise correlation 0.40 → portfolio volatility 7.1%
- pairwise correlation 0.75 → portfolio volatility 9.0%

These are analytical scenarios, not market estimates.

# Slide 4 — A two-stage architecture

1. Sleeve layer: scale each sleeve using its lagged standalone volatility.
2. Portfolio layer: use the covariance matrix to forecast total volatility.
3. Apply a portfolio scalar, then enforce leverage and gross-exposure caps.

# Slide 5 — The formula

```text
s_i,t = clip(sleeve anchor / sigma_i,t-1)
y_t = base weights .* s_t
sigma_p,t = sqrt(y_t' Sigma_t-1 y_t)
m_t = clip(portfolio target / sigma_p,t)
x*_t = gross cap(m_t * y_t)
```

# Slide 6 — Rebalancing is part of the model

Compare:

- daily rebalancing,
- weekly rebalancing,
- a ±10% volatility band.

Turnover and cost live in this rule, not in the target itself.

# Slide 7 — What the historical sample shows

Yahoo Finance adjusted closes, 2 January 2020 to 14 August 2026:

- daily: 44 annualised volatility bps mean target gap; 20.3 bps modeled annualised cost;
- weekly: 55 annualised volatility bps mean target gap; 12.1 bps modeled annualised cost;
- ±10% band: 68 annualised volatility bps mean target gap; 9.5 bps modeled annualised cost.

These are model-dependent backtest diagnostics, not expected returns.

# Slide 8 — Controls before interpretation

- lag every risk estimate,
- cap sleeve and portfolio scalars,
- cap gross exposure,
- model turnover and one-way cost,
- report target error as well as realised volatility,
- stress the covariance estimator.

# Slide 9 — Takeaway

Position-level volatility scaling is only the first layer.

A portfolio-level target requires covariance, constraints, and an explicit rebalancing rule.

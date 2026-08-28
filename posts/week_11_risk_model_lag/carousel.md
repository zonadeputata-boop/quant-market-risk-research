# Week 11 carousel - Risk-Model Lag

## Slide 1 - Risk-Model Lag

### When covariance reacts too late

A risk estimate can be mathematically correct and still arrive on the wrong decision clock.

Week 11 · Quant Market Risk Research

## Slide 2 - One portfolio. Four risk clocks.

Fixed equal weights across SPY, QQQ, TLT, GLD, HYG and SHY.

- Rolling 21 sessions
- Rolling 63 sessions
- Rolling 126 sessions
- EWMA with λ = 0.94

The holdings do not change. Only the covariance estimator changes.

## Slide 3 - The forecast never sees the outcome

At the close of day t:

1. Estimate covariance using returns available through t.
2. Convert it into annualized portfolio volatility.
3. Use t+1 through t+21 only as the ex-post realized-volatility proxy.

1,516 daily forecasts · 2 Jul 2020 - 16 Jul 2026

## Slide 4 - Window length is a response rule

One large return enters each estimator differently.

- 21D rolling: 1/21 of the sample, then drops out after 21 sessions.
- 63D rolling: 1/63 of the sample.
- 126D rolling: 1/126 of the sample.
- EWMA 0.94: 6% weight on the newest outer product; 11.2-session half-life.

Longer memory stabilizes the estimate by diluting new information.

## Slide 5 - Fast models moved 4-5× more on shock days

Median close-to-close forecast revision across 12 separated tail events:

- EWMA 0.94: +25.8%
- Rolling 21D: +20.0%
- Rolling 63D: +6.4%
- Rolling 126D: +4.9%

Events are ex-post 99th-percentile absolute portfolio-return days, with a ±10-session exclusion rule.

## Slide 6 - Speed comes with more day-to-day movement

Mean absolute daily forecast revision:

- Rolling 21D: 3.63%
- EWMA 0.94: 3.21%
- Rolling 63D: 1.22%
- Rolling 126D: 0.64%

A faster risk model may catch a shock sooner, but it can also move leverage and hedging decisions more often.

## Slide 7 - Faster was competitive, not universally superior

Full-sample MAE versus forward 21-session realized volatility:

- EWMA 0.94: 2.34 vol points
- Rolling 21D: 2.39 vol points
- Rolling 63D: 2.43 vol points
- Rolling 126D: 2.81 vol points

No estimator won every year. “Best” depends on the loss function and decision horizon.

## Slide 8 - Use two clocks, then govern the handoff

Stable core:

- strategic allocation
- long-horizon risk budgets
- slower leverage decisions

Fast overlay:

- shock detection
- temporary hedging
- escalation and review

Add bands, caps and explicit de-escalation rules before connecting either clock to trades.

## Slide 9 - What the evidence does and does not say

Supported here:

- estimator memory changes shock response;
- faster estimates revise more often;
- EWMA and 21D were competitive in this sample.

Not established:

- a universal best estimator;
- causal performance improvement;
- optimal trading or rebalancing rules.

Does your risk process use one covariance clock for every decision?

Sources: J.P. Morgan/Reuters RiskMetrics Technical Document; Yahoo Finance adjusted closes. Method and code in the repository.

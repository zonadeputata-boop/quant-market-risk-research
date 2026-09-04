# LinkedIn caption — Week 12

A risk estimate without an interval can create false precision.

I tested this on a fixed, equal-weight portfolio of SPY, QQQ, TLT, GLD, HYG and SHY. At each month-end, I estimated annualized volatility and one-day 97.5% historical Expected Shortfall using trailing windows of 63 and 252 sessions. Then I used a circular moving-block bootstrap to approximate 95% uncertainty intervals.

Across 69 month-ends from December 2020 to August 2026:

- Volatility became more precise with more history: the median interval width fell from 38% to 30% of the estimate.
- Expected Shortfall did not improve nearly as much: 45% versus 44%.
- The reason is visible in the tail count. A 63-day estimate averages only the worst 2 observations; even 252 days supplies only 7 under the explicit historical estimator used here.

The lesson is not that ES is unusable. It is that a tail-risk point estimate should not be treated as exact simply because it has two decimal places.

For governance, report the estimate together with its interval, tail count and sensitivity to the resampling choice. If a decision changes across plausible values inside that range, the uncertainty is decision-relevant.

Scope: historical diagnostic, not a forecast or investment strategy. Bootstrap intervals are conditional on the observed window and cannot represent regimes or losses absent from the sample. Data end 14 August 2026.

#RiskManagement #QuantitativeFinance #ExpectedShortfall #Bootstrap #ModelRisk

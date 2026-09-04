# Week 12 carousel — How Certain Is Your Risk Estimate?

## 1. Cover
**How Certain Is Your Risk Estimate?**  
A point estimate can hide a wide range of plausible values.

## 2. Precision is not certainty
10.6% volatility and 1.70% daily ES look exact. They are estimates from a finite sample, not known constants.

## 3. The diagnostic
Fixed equal weights: SPY, QQQ, TLT, GLD, HYG, SHY. At 69 month-ends, compare trailing 63 and 252 sessions. Estimate annualized volatility and one-day 97.5% historical ES. Use 2,000 circular moving-block resamples and 95% percentile intervals.

## 4. Tail estimates run on very little data
Under the stated estimator, ES averages the worst ceiling(2.5% x n) losses: **2 observations** in 63 days and **7 observations** in 252 days.

## 5. More history helps volatility
Median interval width relative to the point estimate: **38%** for 63 days, **30%** for 252 days.

## 6. Tail uncertainty stays wide
For 97.5% historical ES, the same measure is **45%** for 63 days and **44%** for 252 days. In this sample, four times the history barely narrowed the typical ES interval.

## 7. Latest window: the range matters
As of 14 Aug 2026, 252-day volatility is 9.2% with a bootstrap interval of 7.8%-10.5%. Daily ES is 1.57% with an interval of 1.15%-1.91%.

## 8. Make uncertainty operational
Report the point estimate, interval, effective tail count and method sensitivity. Escalate when a limit decision changes inside the plausible range.

## 9. What the interval cannot tell you
It is conditional on observed data, weights, window and block rule. It does not include unseen regimes, structural breaks, model misspecification or losses absent from the sample.

# Week 11 methodology - Risk-Model Lag

## Research question

How much does covariance-estimator memory change the speed and stability of a portfolio risk forecast?

## Data and diagnostic portfolio

- Adjusted daily closes for SPY, QQQ, TLT, GLD, HYG and SHY.
- Source: Yahoo Finance chart endpoint.
- Price span: 2 January 2020 - 14 August 2026.
- 1,663 complete price rows and 1,662 complete simple-return rows.
- Fixed equal weights of 1/6 per ETF. This is a diagnostic risk series, not an investable-strategy backtest.

## Forecast estimators

The forecast at close t uses returns available through t.

1. Sample covariance over the trailing 21 sessions.
2. Sample covariance over the trailing 63 sessions.
3. Sample covariance over the trailing 126 sessions.
4. RiskMetrics-style zero-mean EWMA covariance with λ=0.94, initialized with the first 126-return sample covariance.

For each daily covariance matrix Σₜ and fixed weight vector w, annualized forecast volatility is:

`sqrt(252 × w' Σₜ w)`

The EWMA recursion is:

`Σₜ = 0.94 Σₜ₋₁ + 0.06 rₜ rₜ'`

Its mathematical weight half-life is `ln(0.5) / ln(0.94) = 11.2` trading sessions.

## Ex-post evaluation

The realized-volatility proxy for a forecast at t is the annualized sample standard deviation of fixed-weight portfolio returns from t+1 through t+21. The outcome window never enters the forecast.

The aligned evaluation panel contains 1,516 forecasts from 2 July 2020 through 16 July 2026. Because the 21-session outcome windows overlap, the observations are serially dependent; the report therefore treats error rankings as descriptive and does not claim independent-sample significance.

Reported full-sample metrics are mean absolute error, root mean squared error, bias and forecast/outcome correlation.

## Shock-event diagnostic

Tail candidates are dates at or above the 99th percentile of absolute fixed-weight portfolio returns within the forecast sample. Candidates are ranked by absolute return; after selecting a date, other candidates within ±10 trading sessions are suppressed. This produces 12 separated events.

For each event, response is the percentage change from the prior close's risk forecast to the event close's forecast. Event selection is ex post and is used only to describe estimator response, not as a signal.

## Results used in the post

| Estimator | MAE (annualized vol points) | Median shock-day revision | Mean absolute daily revision |
|---|---:|---:|---:|
| Rolling 21D | 2.39 | 20.0% | 3.63% |
| Rolling 63D | 2.43 | 6.4% | 1.22% |
| Rolling 126D | 2.81 | 4.9% | 0.64% |
| EWMA 0.94 | 2.34 | 25.8% | 3.21% |

## Quality and leakage controls

- exact date grain; no duplicate dates;
- no missing or non-positive prices;
- common complete panel across all six ETFs;
- forecast at t is invariant to any perturbation after t;
- forward realized volatility starts at t+1;
- covariance constructions are symmetric and positive semidefinite within numerical tolerance;
- portfolio weights are non-negative and sum to one;
- slide and caption numbers are generated from saved output tables.

## Limitations

- One historical ETF panel cannot establish a universal estimator ranking.
- Close-to-close returns are a noisy volatility input; intraday realized measures could change comparisons.
- The 21-session realized-volatility proxy is imperfect and produces overlapping outcomes.
- Fixed equal weights isolate the estimator but do not represent a production portfolio with flows, drift, derivatives or nonlinear exposures.
- The shock set and its exclusion rule are ex-post analytical choices.
- No transaction costs, turnover, expected returns, execution rules or causal performance claims are included.
- λ=0.94 is a documented RiskMetrics convention, not asserted to be optimal for this portfolio or horizon.

## Primary references

- J.P. Morgan/Reuters, *RiskMetrics Technical Document*, 4th ed. (1996): https://www.msci.com/documents/10199/5915b101-4206-4ba0-aee2-3449d5c7e95a
- Andrew J. Patton, *Volatility Forecast Comparison Using Imperfect Volatility Proxies* (working-paper version): https://users.nber.org/~confer/2006/si2006/efww/patton.pdf
- Yahoo Finance historical adjusted-close data: https://finance.yahoo.com/quote/SPY/history/

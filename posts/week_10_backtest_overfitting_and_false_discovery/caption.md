Backtest overfitting begins before a strategy reaches the portfolio.

The relevant question is not whether the winning backtest looks significant in
isolation. It is whether that result is still unusual after accounting for the
full search process that produced it.

To isolate the mechanism, I ran a controlled null simulation in which every
candidate strategy had zero true expected return. For each experiment, I
generated an in-sample statistic for every candidate, selected the highest
in-sample Sharpe, and evaluated the selected candidate on an independent
out-of-sample period.

Simulation design:

- 10,000 experiments per trial-count scenario
- 3 years in sample and 2 years out of sample
- 1 to 500 independent candidate strategies
- iid Gaussian returns with zero expected return
- one-sided 5% naive significance threshold

The median best in-sample Sharpe increased from approximately 0.00 with one
trial to 1.42 with 100 trials and 1.74 with 500 trials. The median
out-of-sample Sharpe of the selected candidate remained near zero.

At 100 independent trials, at least one candidate passed the naive 5% test in
99.5% of simulations. This is consistent with the independent-test benchmark:

P(at least one false positive) = 1 - (1 - alpha)^N

Applying a Bonferroni threshold kept the simulated family-wise error rate near
5% in this benchmark. That does not make Bonferroni a universal solution. Real
strategy trials are usually dependent, the effective number of trials can be
uncertain, returns may be non-normal and the same holdout can itself be reused.

A more defensible research process should therefore include:

1. A trial ledger covering discarded specifications as well as winners.
2. Time-ordered or purged model selection inside the development sample.
3. A genuinely untouched final evaluation period.
4. A multiple-testing method appropriate to the research design, such as a
   Deflated Sharpe Ratio, Reality Check, SPA test or PBO/CSCV framework.
5. Costs, parameter stability and sensitivity analysis before deployment.

The central point is simple: the best backtest is a selected statistic. Its
evidence must be evaluated against the research process, not against the null
for a single pre-specified strategy.

The packaged Python script reproduces the simulation and the six automated
checks. This is a synthetic diagnostic, not historical performance and not
evidence for any investable strategy.

References: White (2000); Bailey and López de Prado (2014); Hansen (2005);
Bailey, Borwein, López de Prado and Zhu (2017).

#QuantFinance #Backtesting #ModelRisk #SystematicInvesting #RiskManagement #Python

For educational and analytical purposes only. Not investment advice.

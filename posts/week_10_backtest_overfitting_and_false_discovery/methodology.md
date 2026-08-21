# Methodology - Week 10

## Question

How does selecting the best backtest from a larger research search affect the
in-sample Sharpe ratio, out-of-sample performance and family-wise false-positive
rate when every candidate has zero true expected return?

## Controlled null design

- Each candidate strategy has iid Gaussian returns with zero expected return.
- The in-sample window contains 756 observations (three 252-day years).
- The independent out-of-sample window contains 504 observations (two years).
- Candidate counts are 1, 5, 10, 25, 50, 100, 250 and 500.
- Each candidate-count scenario uses 10,000 Monte Carlo experiments.
- The selected strategy is the candidate with the largest in-sample
  one-sample t-statistic, equivalently the largest in-sample sample Sharpe.
- The annualized sample Sharpe is obtained through
  `t * sqrt(252 / observations)`.
- The naive test is one-sided at alpha = 5%.
- Bonferroni uses a per-candidate threshold of alpha / N.

Under iid Gaussian zero-mean returns, the one-sample t-statistic follows a
Student t distribution with `observations - 1` degrees of freedom. The script
therefore samples this exact null distribution directly. The selected
out-of-sample statistic is drawn independently because the test period is
untouched by construction.

## Interpretation boundary

This experiment isolates selection bias under independent trials. It is not a
market backtest and does not estimate the probability that any real strategy is
overfit. Real research trials are often correlated, return distributions may be
non-normal, costs may vary across specifications and effective trial counts may
be uncertain. Dependence changes the quantitative benchmark but does not make
the selection process irrelevant.

Bonferroni is included as a transparent family-wise-error benchmark. It can be
conservative and is not presented as interchangeable with the Deflated Sharpe
Ratio, White's Reality Check, Hansen's SPA test or the PBO/CSCV framework. Each
addresses a different version of the selection and model-comparison problem.

## Reproduction

From the repository root:

```bash
python3 scripts/run_week10_backtest_overfitting.py
python3 -m unittest tests/test_week10_backtest_overfitting.py
```

Dependencies: `numpy`, `pandas` and `scipy`.

## Primary references

- White, H. (2000). A Reality Check for Data Snooping. *Econometrica*, 68(5),
  1097-1126. https://doi.org/10.1111/1468-0262.00152
- Hansen, P. R. (2005). A Test for Superior Predictive Ability. *Journal of
  Business & Economic Statistics*, 23(4), 365-380.
  https://doi.org/10.1198/073500105000000063
- Bailey, D. H., and López de Prado, M. (2014). The Deflated Sharpe Ratio:
  Correcting for Selection Bias, Backtest Overfitting and Non-Normality.
  *Journal of Portfolio Management*, 40(5), 94-107.
  https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2460551
- Bailey, D. H., Borwein, J. M., López de Prado, M., and Zhu, Q. J. (2017). The
  Probability of Backtest Overfitting. *Journal of Computational Finance*,
  20(4), 39-69.
  https://www.risk.net/journal-of-computational-finance/2471206/the-probability-of-backtest-overfitting

# Week 10 Research Summary - Backtest Overfitting and False Discovery

## Result

In a controlled null simulation, increasing the number of candidate strategies
raised the in-sample performance of the selected winner even though every
candidate had zero true expected return. With 100 independent trials, the
median best in-sample Sharpe was 1.42 and at least one candidate crossed the
naive one-sided 5% threshold in 99.5% of 10,000 experiments. The selected
candidate's median Sharpe on an independent two-year sample was approximately
zero.

Bonferroni kept the simulated family-wise error rate near 5% in the independent
trial benchmark. This is a transparent control, not a universal prescription.
Real candidate strategies may be dependent and non-normal, and researchers may
reuse the same holdout. The correct diagnostic must reflect the full research
design.

## Scope

The simulation is synthetic and deliberately restrictive. It isolates the
mechanical effect of selecting the best result from repeated null trials. It is
not historical performance, does not model trading costs or market structure,
and does not estimate the overfitting probability of a real investment process.

## Reproducibility

- Script: `scripts/run_week10_backtest_overfitting.py`
- Tests: `tests/test_week10_backtest_overfitting.py`
- Summary: `tables/trial_count_summary.csv`
- Detailed draws: `tables/simulation_draws.csv.gz`
- Assumptions: `tables/simulation_metadata.json`

Six automated tests verify the t-statistic/Sharpe identity, family-wise error
formula, selection effect, naive false-discovery inflation, Bonferroni control
and independent out-of-sample behavior.

## References

White (2000); Hansen (2005); Bailey and López de Prado (2014); Bailey et al.
(2017). Full citations and links are provided in the post methodology file.

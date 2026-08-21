# Week 10 - Backtest Overfitting and False Discovery

## Slide 1 - Backtest Overfitting and False Discovery

Why the best result in a large search needs a different null.

## Slide 2 - Selection changes the statistical question

A 5% test controls the error rate for one pre-specified hypothesis. It does not
control the error rate of a process that tests many specifications and reports
only the winner.

## Slide 3 - Controlled null experiment

Every candidate has zero true expected return. For each candidate count, run
10,000 experiments, select the best three-year in-sample Sharpe and evaluate the
same selection on an independent two-year sample.

## Slide 4 - The winner improves as the search expands

Median best in-sample Sharpe: 0.00 at one trial, 0.87 at 10, 1.42 at 100 and
1.74 at 500. The apparent improvement is generated entirely by selection.

## Slide 5 - A 5% test is not a 5% research process

With 100 independent null trials, at least one candidate passed the naive test
in 99.5% of simulations. Under independence, the benchmark is
`1 - (1 - alpha)^N`.

## Slide 6 - Untouched data removes the selection advantage

The median out-of-sample Sharpe of the selected strategy stays near zero across
the search sizes because the test sample is independent of selection.

## Slide 7 - The correction must match the research design

Bonferroni controls family-wise error in this transparent benchmark. DSR,
Reality Check/SPA and PBO/CSCV address different features of real research
searches; they are not interchangeable labels.

## Slide 8 - Evaluate the research process, not only the winner

Keep a trial ledger, run time-ordered model selection inside development data,
preserve a final untouched period, choose a dependence-aware correction and
report costs plus parameter sensitivity.

## Slide 9 - Final takeaway

The best backtest is a selected statistic. Evidence begins with the full search
process, not with the winning Sharpe ratio alone.

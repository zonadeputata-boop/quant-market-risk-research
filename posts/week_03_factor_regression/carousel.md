# Week 03 Carousel - Factor Regression

## Slide 01 - Factor Regression
What SPY beta misses.

Core question: if a single benchmark leaves material residual risk, which factors should be added before making hedge, sizing or alpha conclusions?

## Slide 02 - Why this follows Week 02
Residual risk is a question, not an answer. SPY beta explains some assets well, but leaves large unexplained shares for others.

## Slide 03 - Model design
Single-factor model:

```text
r_i,t = alpha + beta_EQ * r_SPY,t + epsilon_t
```

Multi-factor diagnostic model:

```text
r_i,t = alpha + beta_EQ*Equity_t + beta_RATE*Rates_t + beta_USD*USD_t + beta_CREDIT*Credit_t + beta_GOLD*Gold_t + epsilon_t
```

## Slide 04 - Candidate factor map
Use residual risk to decide what to test next.

## Slide 05 - Where SPY is not enough
Higher 1-R2 means the benchmark relationship explains less of the return path.

## Slide 06 - Factor intensity map
A disciplined shortlist for the next regression run.

## Slide 07 - Diagnostics before interpretation
Coefficient sign, t-stat, R2 improvement, residual checks, rolling coefficients and out-of-sample validation.

## Slide 08 - Trading and risk use
Translate diagnostics into hedge confidence, risk limits and sizing decisions.

## Slide 09 - Final takeaway
Factor regression asks which economic drivers explain what beta leaves behind.

Not investment advice.

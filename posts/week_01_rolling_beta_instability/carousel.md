# LinkedIn Carousel — Week 01

## Slide 1 — Hook

**Rolling Beta Instability**

Static beta can mislead risk sizing.

The question is not only:

> What is the average beta?

The better question is:

> When does beta change?

---

## Slide 2 — Research question

Does market sensitivity stay stable across regimes?

Or does beta rise exactly when diversification is needed most?

---

## Slide 3 — Dataset

| Input | Setup |
|---|---|
| Assets | QQQ, TLT, GLD, HYG, SHY |
| Benchmark | SPY |
| Volatility filter | VIX |
| Frequency | Daily returns |
| Sample | 2020 to latest available |
| Window | 63 trading days |

---

## Slide 4 — Model

For each asset:

```text
r_asset,t = alpha + beta × r_SPY,t + error_t
```

Estimated using 63-day rolling OLS.

Metrics tracked:

| Metric | Meaning |
|---|---|
| Rolling beta | Time-varying market sensitivity |
| Rolling R² | Share of return explained by SPY |
| Residual volatility | Unexplained risk |
| Stress beta | Beta during high-volatility regimes |

---

## Slide 5 — Why static beta is incomplete

A single full-sample beta hides regime changes.

| Estimate | Interpretation |
|---|---|
| Full-sample beta | Average exposure |
| Rolling beta | Exposure path |
| Stress beta | Exposure when risk matters |
| Rolling R² | Whether the asset becomes more market-driven |

---

## Slide 6 — Portfolio risk interpretation

| Signal | Risk read |
|---|---|
| Beta ↑ and R² ↑ | Asset becomes more market-driven |
| Beta ↑ during stress | Diversification weakens |
| Beta ↓ but residual vol ↑ | Idiosyncratic risk rises |
| Beta unstable | Static hedge ratio may be wrong |

---

## Slide 7 — Trading / risk action

Risk sizing should adapt to current exposure.

```text
Beta-adjusted exposure = Notional exposure × rolling beta
```

If a $10m position has beta 0.8, it behaves like $8m market exposure.

If beta rises to 1.3, it behaves like $13m market exposure.

Same notional.

Different risk.

---

## Slide 8 — Limitation

Rolling beta is backward-looking.

It is useful for risk monitoring, not perfect prediction.

Model risks:

| Risk | Why it matters |
|---|---|
| Window choice | 21D vs 63D vs 252D changes sensitivity |
| Regime shifts | Historical beta may break |
| Non-linearity | OLS misses convex exposure |
| Liquidity shocks | Beta does not capture exit cost |

---

## Slide 9 — Final takeaway

Beta is not a label.

It is a time-varying risk estimate.

Professional risk management means monitoring when exposure changes, not assuming the past average is stable.

**Not investment advice.**

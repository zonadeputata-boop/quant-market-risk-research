Rolling beta is more useful than static beta.

A portfolio can look defensive on average, but become more market-driven exactly when risk matters.

This week I looked at rolling market sensitivity across public asset proxies using:

- Daily returns
- SPY as the equity benchmark
- 63-day rolling OLS
- VIX / drawdown-based stress regimes

Model:

```text
r_asset,t = alpha + beta × r_SPY,t + error_t
```

What I track:

| Metric | Question |
|---|---|
| Rolling beta | Is market sensitivity changing? |
| Rolling R² | Is the asset becoming more market-driven? |
| Stress beta | Does exposure rise in high-volatility regimes? |
| Residual volatility | What risk is left unexplained? |

The key risk idea:

A static beta may be acceptable for a long-term description.

It is not enough for live risk sizing.

```text
Beta-adjusted exposure = Notional exposure × rolling beta
```

Same notional exposure can imply a very different market risk profile if beta is unstable.

For trading and risk management, I care less about the average beta and more about the beta path.

Beta is not a label.

It is a time-varying risk estimate.

#QuantTrading #RiskManagement #MarketRisk #PortfolioAnalytics #Python #InvestmentResearch #TradingAnalytics

Not investment advice.

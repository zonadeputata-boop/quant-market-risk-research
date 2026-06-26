Residual risk is where the model starts asking better questions.

After a simple beta regression, the residual is not automatically alpha.

It can be:
- true unexplained return,
- omitted factor exposure,
- noise,
- liquidity risk,
- or a sign that the benchmark is incomplete.

For Week 02 of my quant market risk research series, I extended the rolling beta analysis into a residual-risk diagnostic framework.

Model:

r_asset,t = alpha + beta x r_SPY,t + epsilon_t

What I track:

| Metric | Risk question |
|---|---|
| Beta | How much SPY sensitivity? |
| R² | How much variance is explained by SPY? |
| 1 - R² | How much remains unexplained? |
| Residual risk | Is the remaining risk alpha, noise or missing exposure? |

Selected diagnostics from the run:

| Asset | Latest beta | Latest R² | 1 - R² | Risk read |
|---|---:|---:|---:|---|
| QQQ | 1.43 | 0.87 | 0.13 | Equity beta dominates |
| GLD | 1.17 | 0.43 | 0.57 | SPY is not enough |
| HYG | 0.27 | 0.70 | 0.30 | Credit behaves equity-like |
| TLT | 0.28 | 0.22 | 0.78 | Rates driver dominates |
| SHY | 0.06 | 0.35 | 0.65 | Cash-like sleeve |

The practical risk point:

A beta estimate without R² can be dangerous.

High beta + high R² may be hedgeable market risk.

High beta + low R² means the model is probably missing important drivers.

For trading and risk management, residual risk should not be ignored or casually labelled as alpha.

Before calling it alpha, test whether it is just omitted beta.

Full Python code, methodology and research output:
https://github.com/zonadeputata-boop/quant-market-risk-research

#QuantTrading #RiskManagement #MarketRisk #PortfolioAnalytics #Python #QuantFinance #InvestmentResearch #TradingAnalytics

Not investment advice.

Factor regression is the next step after residual-risk diagnostics.

In Week 01, I looked at rolling beta instability.

In Week 02, I asked whether SPY beta actually explained enough of each asset's return path.

This week, the question is:

If SPY leaves material residual risk, which factors should be added before making hedge, sizing or alpha conclusions?

The model progression is simple:

single-factor beta -> residual risk -> multi-factor diagnostics

Single-factor model:

r_i,t = alpha + beta_EQ x r_SPY,t + epsilon_t

Multi-factor diagnostic model:

r_i,t = alpha
+ beta_EQ x Equity_t
+ beta_RATE x Rates_t
+ beta_USD x USD_t
+ beta_CREDIT x Credit_t
+ beta_GOLD x Gold_t
+ epsilon_t

What I care about is not adding more variables for complexity.

I care about whether an additional factor improves explanation, hedge confidence and risk interpretation.

Selected candidate map:

| Asset | Single-factor issue | Candidate driver |
|---|---|---|
| GLD | SPY is not enough | USD / real rates |
| TLT | low explanatory power | rates / duration |
| HYG | equity-like behavior | credit / liquidity |
| QQQ | strong equity beta | growth / equity duration |
| SHY | cash-like behavior | front-end rates |

Professional rule:

Do not add factors because they are available.

Add factors because the residual risk points to a plausible omitted driver.

For trading and risk management, a better model should do more than fit historical data.

It should improve a decision:
- hedge design,
- position sizing,
- factor limits,
- stress testing,
- or model confidence.

Full Python code, methodology and research output:
https://github.com/zonadeputata-boop/quant-market-risk-research

#QuantTrading #RiskManagement #FactorRegression #PortfolioAnalytics #Python #MarketRisk #QuantFinance #InvestmentResearch

Not investment advice.

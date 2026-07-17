Diversification can look strong in normal markets and fail when it is needed most.

In Week 04, I compared VaR and Expected Shortfall to understand how bad losses can become inside the left tail.

This week, I look at a related risk question:

Does diversification survive stress?

A single full-sample correlation number can be misleading.

It tells us how assets co-moved on average.

But portfolio risk is usually decided during the unstable part of the sample.

The framework:

- calculate daily returns for public asset proxies,
- estimate rolling 63-day correlations,
- define stress days using large negative SPY returns or high-volatility conditions,
- compare normal correlation versus stress correlation,
- calculate the correlation gap.

Core diagnostic:

correlation_gap = corr_stress - corr_normal

A positive correlation gap means assets move more together during stress.

That matters because the portfolio may be diversified in normal conditions but concentrated during drawdowns.

Example risk reads:

| Relationship | Stress interpretation |
|---|---|
| SPY - QQQ | Equity exposure concentrates |
| SPY - HYG | Credit becomes more equity-like |
| SPY - TLT | Bond hedge may weaken |
| SPY - GLD | Safe-haven behavior is not stable |
| HYG - TLT | Credit-rates diversification can fade |

For trading and risk management, correlation breakdown affects:

- hedge design,
- gross and net exposure limits,
- stress testing,
- portfolio construction,
- position sizing,
- and drawdown control.

Professional rule:

Diversification should be tested under the conditions where it is expected to protect capital.

The question is not whether a portfolio is diversified on average.

The question is whether diversification survives stress.

Full Python code, methodology and research output:
https://github.com/zonadeputata-boop/quant-market-risk-research

#QuantTrading #RiskManagement #Correlation #PortfolioAnalytics #MarketRisk #Python #QuantFinance #StressTesting

Not investment advice.

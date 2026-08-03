Volatility is not the whole risk budget.

In Week 06, I used volatility targeting to make position size respond to changes in realized risk.

This week, I add a second constraint:

Drawdown-aware position sizing.

The question:

If two positions have similar volatility but different loss paths, should they carry the same exposure?

Volatility measures dispersion.

Drawdown measures how much capital has been lost relative to the previous peak.

The framework uses two linked scalars:

volatility_scalar_t = min(max_exposure, target_volatility / realized_volatility_(t-1))

drawdown_scalar_t = clip(1 + drawdown_t / drawdown_budget, floor, 1)

final_exposure_t = volatility_scalar_t × drawdown_scalar_t

I apply the framework to a public ETF universe:

SPY, QQQ, TLT, GLD, HYG and SHY.

The logic is conservative:

- volatility sets the base risk budget,
- drawdown reduces the remaining budget after losses,
- all signals are lagged to avoid look-ahead,
- exposure is capped,
- and a minimum scalar prevents a purely mechanical exit.

This is not an alpha model.

It is a capital-path risk overlay.

For trading and portfolio risk management, I would evaluate it through:

- realized volatility stability,
- maximum drawdown,
- time under water,
- turnover and transaction-cost drag,
- recovery lag,
- and the risk of procyclical deleveraging near a market trough.

Professional rule:

Position sizing should respond not only to how volatile an asset is, but also to how much risk budget its loss path has already consumed.

Full Python code, methodology and research output:
https://github.com/zonadeputata-boop/quant-market-risk-research

#QuantTrading #RiskManagement #PositionSizing #Drawdown #PortfolioAnalytics #Python #QuantFinance #MarketRisk

Not investment advice.

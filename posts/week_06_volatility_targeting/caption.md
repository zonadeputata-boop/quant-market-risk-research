Position sizing should respond to risk.

In Week 05, I looked at correlation breakdown and why diversification can fail under stress.

This week, I move from risk diagnosis to risk action:

Volatility targeting.

The question:

If realized volatility changes through time, should position size stay fixed?

A fixed position assumes that risk is stable.

A volatility-targeted position assumes that risk changes and exposure should respond.

Core rule:

exposure_t = target_volatility / realized_volatility_t

Capped rule:

exposure_t = min(max_exposure, target_volatility / realized_volatility_t)

The intuition is simple:

- when realized volatility rises, exposure falls,
- when realized volatility falls, exposure can rise,
- but only within leverage and concentration limits.

This is not an alpha model.

It does not predict returns.

It is a risk-budgeting mechanism.

For trading and portfolio risk management, I would evaluate it through:

- realized volatility stability,
- drawdown behavior,
- turnover,
- transaction cost drag,
- leverage caps,
- and whether the rule improves risk-adjusted exposure through regimes.

Professional rule:

Volatility targeting should not be judged only by whether it lowers volatility.

It should be judged by whether it improves position sizing, drawdown control and risk-budget discipline.

The question is not only what to hold.

It is how much risk each position is allowed to contribute.

Full Python code, methodology and research output:
https://github.com/zonadeputata-boop/quant-market-risk-research

#QuantTrading #RiskManagement #VolatilityTargeting #PositionSizing #PortfolioAnalytics #Python #QuantFinance #MarketRisk

Not investment advice.

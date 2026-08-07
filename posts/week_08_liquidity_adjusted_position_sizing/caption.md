A position can fit the volatility budget and still be too large to trade safely.

In Week 07, I added a drawdown constraint to volatility targeting.

This week, I add a third layer:

Liquidity-adjusted position sizing.

The question:

If volatility sets the risk budget, what limits the amount that can actually be traded?

The framework links three quantities:

volatility_scalar_t = min(max_exposure, target_volatility / realized_volatility_(t-1))

base_notional_t = portfolio_capital × volatility_scalar_t

capacity_t = participation_rate × median_dollar_volume_(t-1) × liquidation_days

liquidity_scalar_t = min(1, capacity_t / base_notional_t)

final_notional_t = base_notional_t × liquidity_scalar_t

I apply the framework to a public ETF universe:

SPY, QQQ, IWM, TLT, GLD and HYG.

The logic is conservative:

- volatility proposes the base notional,
- dollar volume defines executable capacity,
- all signals are lagged to avoid look-ahead,
- participation and liquidation time are explicit limits,
- and the final trade is clipped when capacity becomes binding.

This is not an alpha model.

It is a pre-trade risk control that connects portfolio sizing with execution capacity.

For a production process, I would extend the analysis with:

- bid-ask spreads and market-impact estimates,
- stressed rather than average volume,
- portfolio-wide liquidation overlap,
- concentration and venue limits,
- turnover and implementation shortfall,
- and separate entry and exit assumptions.

Professional rule:

A risk budget is not executable until the position passes a liquidity test.

Full Python code, methodology and research output:
https://github.com/zonadeputata-boop/quant-market-risk-research

#QuantTrading #RiskManagement #LiquidityRisk #PositionSizing #Execution #PortfolioAnalytics #Python #QuantFinance

Not investment advice.

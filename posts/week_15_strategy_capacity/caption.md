# LinkedIn caption

A backtest can scale in a spreadsheet. Orders cannot.

Consider a weekly strategy with 4% expected gross alpha, 10% annual volatility and 20% one-way turnover at each rebalance. Assume fixed trading costs of 5 basis points and effective daily dollar volume of $500 million across the traded basket.

To make market impact explicit, use a stylized square-root cost proxy:

impact cost = 0.50 × daily volatility × √(trade size / daily volume)

At $10 million of AUM, the weekly trade is $2 million, or 0.4% of effective daily volume. The model produces 2.82% net alpha after annualized fixed and impact costs.

At $250 million, each rebalance trades $50 million, equal to 10% of effective daily volume. Net alpha falls to 0.19%.

At $500 million, participation reaches 20%. Modeled costs exceed gross alpha, leaving net alpha at -1.17%.

Under these assumptions, economic break-even occurs near $280 million. A 10% participation policy would bind earlier, at $250 million.

These figures are scenario outputs, not a forecast or a statistical estimate of a specific strategy. The gross alpha, turnover, liquidity, volatility and impact coefficient all require calibration. Research supports concave market impact and often finds an approximate square-root relationship, but alternative empirical work shows that execution duration and participation can change the functional form.

That makes capacity a sensitivity range rather than one permanent number. A credible review should stress lower alpha, higher volatility, weaker market volume and slower execution. It should also measure implementation shortfall against a pre-trade benchmark and include the opportunity cost of unfilled orders.

The practical question is simple: at the AUM you plan to manage, how much expected alpha remains after the trades needed to implement the strategy?

Methodology, assumptions, code and tests: GitHub repository link in profile.

#QuantFinance #PortfolioManagement #TradingCosts #MarketImpact #RiskManagement #SystematicTrading

# Week 14 caption

Leverage can look stable until prices move.

Consider a fund with $100 of equity and $250 of market exposure. A 4% fall in the asset value reduces equity to $90 and pushes leverage from 2.50x to 2.67x.

Restoring the 2.50x limit requires a $15 sale, even if trading has no effect on the market price.

The problem becomes recursive when those sales move the market. The remaining position loses value, leverage rises again, and another sale follows.

In a transparent, stylized model, the same initial shock produces:

- $15.0 of cumulative sales with no price-impact feedback
- $21.0 under the lower feedback assumption
- $35.3 under the stronger feedback assumption

These figures are scenario outputs, not forecasts. The price-impact sensitivities are explicit assumptions rather than statistically estimated coefficients.

The mechanism has real-world support. During the UK gilt-market stress in 2022, the Bank of England estimated that LDI funds and pension schemes faced more than £70 billion of margin and collateral calls. Over 23 September to 14 October, LDI funds sold around £23 billion of gilts and DB pension schemes around £14 billion.

A useful liquidity stress test therefore follows the balance sheet after the first shock. It revalues collateral, calculates the cash gap, maps forced sales to market depth, and repeats the process until the constraint is restored.

The key question is simple: after a loss, how much would the portfolio have to sell, and who else might need to sell at the same time?

Methodology, assumptions, code and tests: GitHub repository link in profile.

#RiskManagement #LiquidityRisk #MarketRisk #QuantFinance #StressTesting #PortfolioManagement


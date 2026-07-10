VaR is a useful threshold.

But it is not the full tail-risk story.

In Week 01, I looked at rolling beta instability.
In Week 02, I tested residual risk after controlling for SPY beta.
In Week 03, I moved from single-factor exposure to factor diagnostics.

This week, the question is:

What happens after the VaR threshold is breached?

Historical VaR answers:

Where does the left tail begin?

Expected Shortfall answers:

How bad is the average loss once the portfolio is already inside that tail?

Method:

- public asset proxies,
- daily returns,
- historical simulation,
- VaR at 95% confidence,
- Expected Shortfall at 95% confidence,
- tail-gap diagnostic.

Definitions:

VaR_95 = 5th percentile of daily returns

ES_95 = average return when r_t < VaR_95

The distinction matters.

Two portfolios can have similar VaR but very different Expected Shortfall.

That means the same risk threshold can hide very different damage profiles after breach.

For trading and risk management, I care about:

- whether VaR is rising,
- whether ES is worsening faster than VaR,
- whether the ES-VaR gap is widening,
- whether the realized worst loss exceeds the planned risk budget,
- whether a hedge reduces actual tail damage, not only headline volatility.

Professional rule:

VaR tells me where the tail starts.

Expected Shortfall tells me how much damage is inside the tail.

Full Python code, methodology and research output:
https://github.com/zonadeputata-boop/quant-market-risk-research

#QuantTrading #RiskManagement #VaR #ExpectedShortfall #MarketRisk #PortfolioAnalytics #Python #QuantFinance

Not investment advice.

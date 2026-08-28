Risk models do not fail only because covariance is wrong.

Sometimes it arrives late.

For Week 11, I compared four covariance estimators on the same fixed equal-weight diagnostic portfolio: SPY, QQQ, TLT, GLD, HYG and SHY.

The timing rule is strict: the forecast stamped at the close of day t uses returns available through t. The next 21 sessions are used only as an ex-post realized-volatility proxy.

Across 1,516 daily forecasts from 2 July 2020 to 16 July 2026, full-sample mean absolute error was:

• EWMA λ=0.94: 2.34 annualized volatility points  
• Rolling 21D: 2.39  
• Rolling 63D: 2.43  
• Rolling 126D: 2.81

The response gap was much larger on 12 separated, ex-post tail events. The median same-close risk-forecast revision was +25.8% for EWMA and +20.0% for 21D, versus +6.4% for 63D and +4.9% for 126D.

That speed was not free. Mean absolute daily forecast revisions were 3.21-3.63% for the fast estimators, versus 0.64-1.22% for the slower ones.

My takeaway: do not ask for the “best” covariance model without specifying the decision clock. A stable core and a fast overlay can serve different jobs, but the handoff needs bands, caps and de-escalation rules.

This is descriptive historical evidence, not a causal claim or a trading recommendation. The sample uses close-to-close adjusted returns, fixed weights and overlapping 21-session evaluation windows. The shock set is defined ex post, transaction costs are outside scope, and no estimator won every calendar year.

Does your risk process use one covariance clock for every decision?

#RiskManagement #QuantFinance #PortfolioRisk #Volatility #Covariance #SystematicInvesting

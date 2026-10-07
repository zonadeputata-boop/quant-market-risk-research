# LinkedIn caption

Implied volatility is usually above subsequent realized volatility. That does not make short volatility a free return.

Cboe reported that from 1990 through 2014, the VIX averaged 19.9 while subsequent S&P 500 realized volatility averaged 15.6. The average difference was 4.3 volatility points.

The comparison matters, but it is easy to misuse.

A fair review compares an option-implied measure observed today with realized volatility over the matching future horizon. Comparing VIX with trailing volatility mixes two different time directions.

There is also a technical distinction:

- VIX minus future realized volatility is a descriptive, ex-post gap.
- The variance risk premium is defined in variance terms as risk-neutral expected variance minus physical expected variance.
- The physical expectation is not directly observable, so any estimate depends on a forecasting model.

Why can the gap persist? Option buyers pay for insurance against jumps, crashes, volatility-of-volatility and correlation spikes. A short-volatility position receives premium for carrying those risks.

That payoff can look attractive for long periods and still have negative skew, gap losses, margin pressure, liquidity costs and path dependence during stress.

Three checks improve the analysis:

1. Align the underlying, horizon and annualization.
2. Compare variance consistently, not just volatility percentages.
3. Evaluate the full P&L after skew, hedging, transaction costs and stress liquidity.

The historical gap is evidence of compensation for risk. It is not proof of free alpha.

The numerical values in the carousel are source-reported statistics, not a newly estimated backtest. Code, tables, sources and tests are included in the GitHub package.

What loss arrives when the volatility premium disappears?

#QuantFinance #Volatility #Options #RiskManagement #PortfolioManagement #SystematicTrading #MarketRisk

# Methodology and interpretation

## Scope

This package reproduces and checks published summary statistics. It does not estimate a new daily VIX-versus-realized-volatility sample and does not backtest an investable short-volatility strategy.

## Matched comparison

VIX is a forward-looking, option-derived measure of expected S&P 500 volatility over approximately 30 calendar days. The descriptive comparison should therefore use S&P 500 realized volatility over the subsequent matching window, with consistent annualization.

Using trailing realized volatility answers a different question. Using overlapping future windows is acceptable for a descriptive chart, but standard errors require overlap-aware inference.

## Theoretical distinction

The simple ex-post spread is:

`VIX_t - realized_volatility_(t,t+30)`

The theoretical variance risk premium is:

`E_Q[future variance | information_t] - E_P[future variance | information_t]`

The first term is represented by option prices under the risk-neutral measure. The second is a physical expectation and must be estimated. Future realized variance is an ex-post outcome, not the same object as its ex-ante physical expectation.

## Published evidence used

- Cboe reported VIX of 19.9 and subsequent realized volatility of 15.6 on average from 1990 through 2014, for a 4.3-point average gap.
- S&P DJI/Cboe reported average absolute forecast errors of 3.58 for VCR, 5.27 for raw VIX, 4.25 for recent volatility and 4.08 for a mean-reversion adjustment over 1990-2017.
- Federal Reserve research provides the variance-risk-premium definition used in the post.
- A 2024 Review of Financial Studies replication reports that variance-premium predictability remains, while some early magnitudes are sensitive to measurement, sample and specification.

## Limits

- Source-reported historical averages do not guarantee a future premium.
- The gap is not a strategy return. Option P&L also depends on skew, maturity, path, hedging, funding, transaction costs and margin.
- VIX is not directly tradable. VIX futures, options and SPX option strategies have different exposures and carry mechanics.
- The published samples end in 2014 and 2017. They establish the historical pattern used in the educational post, not a current trading signal.

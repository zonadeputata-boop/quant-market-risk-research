"""Rolling econometric models."""

from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.api as sm


def rolling_beta_cov(
    asset_returns: pd.Series,
    benchmark_returns: pd.Series,
    window: int = 63,
) -> pd.Series:
    """Estimate rolling beta using rolling covariance / variance.

    beta_t = Cov(r_asset, r_benchmark) / Var(r_benchmark)
    """
    aligned = pd.concat([asset_returns, benchmark_returns], axis=1).dropna()
    y = aligned.iloc[:, 0]
    x = aligned.iloc[:, 1]

    cov = y.rolling(window).cov(x)
    var = x.rolling(window).var()
    beta = cov / var
    beta.name = f"rolling_beta_{window}d"
    return beta


def rolling_ols_alpha_beta_r2(
    asset_returns: pd.Series,
    benchmark_returns: pd.Series,
    window: int = 63,
) -> pd.DataFrame:
    """Estimate rolling OLS alpha, beta and R².

    Model:
        r_asset,t = alpha + beta * r_benchmark,t + error_t
    """
    aligned = pd.concat([asset_returns, benchmark_returns], axis=1).dropna()
    aligned.columns = ["asset", "benchmark"]

    rows = []
    idx = []

    for end in range(window, len(aligned) + 1):
        sample = aligned.iloc[end - window : end]
        y = sample["asset"]
        x = sm.add_constant(sample["benchmark"])

        model = sm.OLS(y, x).fit()
        rows.append(
            {
                "alpha_daily": model.params["const"],
                "beta": model.params["benchmark"],
                "r_squared": model.rsquared,
                "alpha_t_stat": model.tvalues["const"],
                "beta_t_stat": model.tvalues["benchmark"],
                "residual_vol_daily": model.resid.std(ddof=1),
            }
        )
        idx.append(sample.index[-1])

    return pd.DataFrame(rows, index=idx)


def multi_factor_ols(
    portfolio_returns: pd.Series,
    factor_returns: pd.DataFrame,
) -> tuple[sm.regression.linear_model.RegressionResultsWrapper, pd.DataFrame]:
    """Run multi-factor OLS regression.

    Model:
        r_p,t = alpha + beta_1 f_1,t + ... + beta_n f_n,t + error_t
    """
    data = pd.concat([portfolio_returns.rename("portfolio"), factor_returns], axis=1).dropna()
    y = data["portfolio"]
    x = sm.add_constant(data.drop(columns="portfolio"))

    model = sm.OLS(y, x).fit()

    summary = pd.DataFrame(
        {
            "coefficient": model.params,
            "t_stat": model.tvalues,
            "p_value": model.pvalues,
        }
    )

    return model, summary

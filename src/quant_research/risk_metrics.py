"""Portfolio and market risk metrics."""

from __future__ import annotations

import numpy as np
import pandas as pd


TRADING_DAYS = 252


def realized_volatility(returns: pd.Series | pd.DataFrame, window: int = 63) -> pd.Series | pd.DataFrame:
    """Annualized rolling realized volatility."""
    return returns.rolling(window).std() * np.sqrt(TRADING_DAYS)


def historical_var(returns: pd.Series, confidence: float = 0.95) -> float:
    """Historical Value-at-Risk as a return quantile.

    Returns a negative return threshold, e.g. -0.023 for -2.3%.
    """
    if not 0 < confidence < 1:
        raise ValueError("confidence must be between 0 and 1.")
    return returns.dropna().quantile(1 - confidence)


def expected_shortfall(returns: pd.Series, confidence: float = 0.95) -> float:
    """Expected Shortfall / CVaR.

    Average return conditional on returns being below VaR.
    """
    clean = returns.dropna()
    var = historical_var(clean, confidence)
    tail = clean[clean <= var]
    if tail.empty:
        return np.nan
    return tail.mean()


def drawdown(returns: pd.Series) -> pd.Series:
    """Calculate drawdown path from simple returns."""
    wealth = (1 + returns.dropna()).cumprod()
    running_max = wealth.cummax()
    return wealth / running_max - 1


def max_drawdown(returns: pd.Series) -> float:
    """Maximum drawdown."""
    return drawdown(returns).min()


def beta_adjusted_exposure(notional: float, beta: float) -> float:
    """Convert notional exposure into beta-adjusted market exposure."""
    return notional * beta

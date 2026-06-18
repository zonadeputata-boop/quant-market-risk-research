"""Return calculations."""

from __future__ import annotations

import numpy as np
import pandas as pd


def simple_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Calculate simple daily returns."""
    return prices.pct_change().replace([np.inf, -np.inf], np.nan).dropna(how="all")


def log_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Calculate log daily returns."""
    return np.log(prices / prices.shift(1)).replace([np.inf, -np.inf], np.nan).dropna(how="all")


def cumulative_returns(returns: pd.Series | pd.DataFrame) -> pd.Series | pd.DataFrame:
    """Calculate cumulative return path from simple returns."""
    return (1 + returns).cumprod() - 1

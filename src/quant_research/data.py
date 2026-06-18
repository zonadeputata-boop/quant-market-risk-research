"""Market data utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd
import yfinance as yf


def download_prices(
    tickers: Iterable[str],
    start: str = "2020-01-01",
    end: str | None = None,
    cache_path: str | Path | None = None,
    force_download: bool = False,
) -> pd.DataFrame:
    """Download adjusted close prices from Yahoo Finance via yfinance.

    Parameters
    ----------
    tickers:
        Iterable of Yahoo Finance tickers.
    start:
        Start date in YYYY-MM-DD format.
    end:
        Optional end date in YYYY-MM-DD format.
    cache_path:
        Optional CSV cache location.
    force_download:
        If True, ignores existing cache.

    Returns
    -------
    pd.DataFrame
        Date-indexed adjusted close prices.
    """
    cache = Path(cache_path) if cache_path else None

    if cache and cache.exists() and not force_download:
        prices = pd.read_csv(cache, index_col=0, parse_dates=True)
        return prices.sort_index()

    tickers = list(tickers)
    data = yf.download(
        tickers,
        start=start,
        end=end,
        auto_adjust=True,
        progress=False,
        group_by="column",
    )

    if data.empty:
        raise ValueError("No data downloaded. Check tickers, dates, or connection.")

    if isinstance(data.columns, pd.MultiIndex):
        if "Close" in data.columns.get_level_values(0):
            prices = data["Close"].copy()
        else:
            # yfinance may return different field ordering depending on version
            prices = data.xs("Close", axis=1, level=1, drop_level=True)
    else:
        prices = data[["Close"]].copy()
        prices.columns = tickers

    prices = prices.ffill().dropna(how="all").sort_index()

    if cache:
        cache.parent.mkdir(parents=True, exist_ok=True)
        prices.to_csv(cache)

    return prices

"""Plotting utilities for research outputs."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def save_rolling_beta_plot(
    rolling_stats: dict[str, pd.DataFrame],
    output_path: str | Path,
    title: str = "63D Rolling Beta vs SPY",
) -> None:
    """Save rolling beta chart for multiple assets."""
    fig, ax = plt.subplots(figsize=(12, 6))

    for ticker, stats in rolling_stats.items():
        ax.plot(stats.index, stats["beta"], label=ticker)

    ax.axhline(1.0, linewidth=1, linestyle="--")
    ax.set_title(title)
    ax.set_ylabel("Rolling beta")
    ax.set_xlabel("Date")
    ax.legend()
    fig.tight_layout()

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=200)
    plt.close(fig)


def save_rolling_r2_plot(
    rolling_stats: dict[str, pd.DataFrame],
    output_path: str | Path,
    title: str = "63D Rolling R² vs SPY",
) -> None:
    """Save rolling R² chart for multiple assets."""
    fig, ax = plt.subplots(figsize=(12, 6))

    for ticker, stats in rolling_stats.items():
        ax.plot(stats.index, stats["r_squared"], label=ticker)

    ax.set_title(title)
    ax.set_ylabel("Rolling R²")
    ax.set_xlabel("Date")
    ax.legend()
    fig.tight_layout()

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=200)
    plt.close(fig)


def save_drawdown_plot(drawdowns: pd.DataFrame, output_path: str | Path, title: str = "Drawdown") -> None:
    """Save drawdown chart."""
    fig, ax = plt.subplots(figsize=(12, 6))

    for col in drawdowns.columns:
        ax.plot(drawdowns.index, drawdowns[col], label=col)

    ax.set_title(title)
    ax.set_ylabel("Drawdown")
    ax.set_xlabel("Date")
    ax.legend()
    fig.tight_layout()

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=200)
    plt.close(fig)

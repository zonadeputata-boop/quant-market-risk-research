#!/usr/bin/env python3
"""Reproduce Week 16 tables and figures from published summary statistics.

The script does not redistribute a proprietary daily index history. It checks and
visualizes source-reported metrics from Cboe and S&P DJI/Cboe. Those metrics are
descriptive historical evidence, not a new backtest or a current forecast.
"""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data/raw/week16_source_reported_metrics.csv"
REPORT = ROOT / "reports/week_16_implied_vs_realized_volatility"
TABLES = REPORT / "tables"
FIGURES = REPORT / "figures"


@dataclass(frozen=True)
class Metric:
    metric_id: str
    display_label: str
    value: float
    unit: str
    sample_start: str
    sample_end: str
    source_id: str


def load_metrics(path: Path = INPUT) -> Dict[str, Metric]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = [Metric(**{**row, "value": float(row["value"])}) for row in csv.DictReader(handle)]
    metrics = {row.metric_id: row for row in rows}
    if len(metrics) != len(rows):
        raise ValueError("metric_id values must be unique")
    return metrics


def reported_gap(metrics: Dict[str, Metric]) -> float:
    return metrics["avg_vix"].value - metrics["avg_forward_realized_vol"].value


def relative_error_reduction(raw_error: float, calibrated_error: float) -> float:
    if raw_error <= 0:
        raise ValueError("raw_error must be positive")
    return (raw_error - calibrated_error) / raw_error


def validate_metrics(metrics: Dict[str, Metric]) -> None:
    required = {
        "avg_vix",
        "avg_forward_realized_vol",
        "avg_implied_realized_gap",
        "vcr_median_abs_error",
        "vcr_average_abs_error",
        "raw_vix_median_abs_error",
        "raw_vix_average_abs_error",
        "recent_vol_average_abs_error",
        "mr_average_abs_error",
    }
    missing = required.difference(metrics)
    if missing:
        raise ValueError(f"missing metrics: {sorted(missing)}")
    if abs(reported_gap(metrics) - metrics["avg_implied_realized_gap"].value) > 1e-9:
        raise ValueError("reported average gap is inconsistent with the two published averages")
    if metrics["raw_vix_average_abs_error"].value <= metrics["vcr_average_abs_error"].value:
        raise ValueError("published raw-VIX error should exceed the calibrated VCR error")


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _build_figures(metrics: Dict[str, Metric]) -> None:
    import matplotlib.pyplot as plt

    plt.rcParams.update({"font.family": "DejaVu Sans", "axes.titleweight": "bold"})
    navy, blue, red, grey, line = "#12263F", "#245B80", "#A84632", "#607287", "#D9E2EA"

    fig, ax = plt.subplots(figsize=(8, 5), dpi=180)
    labels = ["Average VIX", "Subsequent realized vol"]
    values = [metrics["avg_vix"].value, metrics["avg_forward_realized_vol"].value]
    bars = ax.bar(labels, values, color=[blue, grey], width=0.58)
    ax.set_title("Source-reported averages, 1990-2014")
    ax.set_ylabel("Annualized volatility points")
    ax.set_ylim(0, 23)
    ax.grid(axis="y", color=line, linewidth=0.8)
    ax.set_axisbelow(True)
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 0.5, f"{value:.1f}", ha="center", color=navy, weight="bold")
    ax.text(0.5, 21.2, "Average gap: 4.3 vol points", ha="center", color=red, weight="bold")
    fig.tight_layout()
    fig.savefig(FIGURES / "week16_average_gap.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)

    labels = ["VCR", "MR adjustment", "Recent volatility", "Raw VIX"]
    values = [
        metrics["vcr_average_abs_error"].value,
        metrics["mr_average_abs_error"].value,
        metrics["recent_vol_average_abs_error"].value,
        metrics["raw_vix_average_abs_error"].value,
    ]
    fig, ax = plt.subplots(figsize=(8, 5), dpi=180)
    bars = ax.barh(labels, values, color=[blue, grey, grey, red])
    ax.set_title("Average absolute forecast error, 1990-2017")
    ax.set_xlabel("Annualized volatility points")
    ax.set_xlim(0, 6)
    ax.grid(axis="x", color=line, linewidth=0.8)
    ax.set_axisbelow(True)
    for bar, value in zip(bars, values):
        ax.text(value + 0.08, bar.get_y() + bar.get_height() / 2, f"{value:.2f}", va="center", color=navy, weight="bold")
    fig.tight_layout()
    fig.savefig(FIGURES / "week16_forecast_error.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def build_outputs() -> dict:
    TABLES.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    metrics = load_metrics()
    validate_metrics(metrics)

    gap_rows = [
        {"measure": "Average VIX", "value": metrics["avg_vix"].value, "unit": "vol points"},
        {"measure": "Average subsequent realized volatility", "value": metrics["avg_forward_realized_vol"].value, "unit": "vol points"},
        {"measure": "Average descriptive gap", "value": metrics["avg_implied_realized_gap"].value, "unit": "vol points"},
    ]
    _write_csv(TABLES / "published_average_gap.csv", ["measure", "value", "unit"], gap_rows)

    forecast_rows = [
        {"method": "VCR", "median_abs_error": 2.31, "average_abs_error": 3.58},
        {"method": "Raw VIX", "median_abs_error": 4.62, "average_abs_error": 5.27},
        {"method": "Recent volatility", "median_abs_error": 3.06, "average_abs_error": 4.25},
        {"method": "MR adjustment", "median_abs_error": 3.02, "average_abs_error": 4.08},
    ]
    _write_csv(TABLES / "published_forecast_errors.csv", ["method", "median_abs_error", "average_abs_error"], forecast_rows)

    public_results = {
        "status": "source_reported_statistics",
        "average_gap_vol_points": metrics["avg_implied_realized_gap"].value,
        "raw_vix_to_vcr_average_error_reduction": relative_error_reduction(5.27, 3.58),
        "raw_vix_to_vcr_median_error_reduction": relative_error_reduction(4.62, 2.31),
        "metrics": {key: asdict(value) for key, value in metrics.items()},
        "interpretation_limit": (
            "VIX minus subsequent realized volatility is a descriptive ex-post gap. "
            "The theoretical variance risk premium compares risk-neutral expected variance "
            "with physical expected variance, which is not directly observable."
        ),
    }
    (TABLES / "public_results.json").write_text(json.dumps(public_results, indent=2), encoding="utf-8")
    _build_figures(metrics)
    return public_results


if __name__ == "__main__":
    results = build_outputs()
    print(json.dumps({
        "average_gap_vol_points": results["average_gap_vol_points"],
        "average_error_reduction_pct": round(100 * results["raw_vix_to_vcr_average_error_reduction"], 1),
        "output_directory": str(REPORT),
    }, indent=2))

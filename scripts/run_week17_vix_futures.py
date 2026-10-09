#!/usr/bin/env python3
"""Reproduce Week 17 tables and figures from cited statistics and scenarios.

Published statistics and illustrative assumptions are stored separately. The
script validates both, calculates one transparent convergence example, and
creates audit-friendly tables and charts. It does not redistribute proprietary
daily index history and it does not estimate a trading strategy.
"""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict


ROOT = Path(__file__).resolve().parents[1]
METRICS_INPUT = ROOT / "data/raw/week17_source_reported_metrics.csv"
SCENARIOS_INPUT = ROOT / "data/raw/week17_scenario_assumptions.csv"
SOURCES_INPUT = ROOT / "data/raw/week17_source_metadata.csv"
REPORT = ROOT / "reports/week_17_vix_futures"
TABLES = REPORT / "tables"
FIGURES = REPORT / "figures"


@dataclass(frozen=True)
class Metric:
    metric_id: str
    display_label: str
    value: float
    unit: str
    period_start: str
    period_end: str
    as_of: str
    comparison: str
    source_id: str


@dataclass(frozen=True)
class ScenarioPoint:
    scenario: str
    point: str
    value: float
    unit: str
    role: str


def load_metrics(path: Path = METRICS_INPUT) -> Dict[str, Metric]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = [Metric(**{**row, "value": float(row["value"])}) for row in csv.DictReader(handle)]
    metrics = {row.metric_id: row for row in rows}
    if len(metrics) != len(rows):
        raise ValueError("metric_id values must be unique")
    return metrics


def load_scenarios(path: Path = SCENARIOS_INPUT) -> Dict[str, Dict[str, ScenarioPoint]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = [ScenarioPoint(**{**row, "value": float(row["value"])}) for row in csv.DictReader(handle)]
    scenarios: Dict[str, Dict[str, ScenarioPoint]] = {}
    for row in rows:
        if row.point in scenarios.setdefault(row.scenario, {}):
            raise ValueError(f"duplicate scenario point: {row.scenario}/{row.point}")
        scenarios[row.scenario][row.point] = row
    return scenarios


def convergence_return(purchase_price: float, settlement_price: float) -> float:
    if purchase_price <= 0:
        raise ValueError("purchase_price must be positive")
    return settlement_price / purchase_price - 1.0


def validate_inputs(metrics: Dict[str, Metric], scenarios: Dict[str, Dict[str, ScenarioPoint]]) -> None:
    required_metrics = {
        "contango_frequency_lower_bound",
        "backwardation_frequency_upper_bound",
        "short_term_index_1m_return",
        "short_term_index_ytd_return",
        "short_term_index_12m_return",
        "short_term_monthly_roll_cost",
    }
    missing_metrics = required_metrics.difference(metrics)
    if missing_metrics:
        raise ValueError(f"missing metrics: {sorted(missing_metrics)}")
    if metrics["contango_frequency_lower_bound"].comparison != "greater_than":
        raise ValueError("contango frequency must remain a lower-bound statement")
    if metrics["backwardation_frequency_upper_bound"].comparison != "less_than":
        raise ValueError("backwardation frequency must remain an upper-bound statement")
    if metrics["contango_frequency_lower_bound"].period_end != "2022-07-26":
        raise ValueError("do not extend the Cboe frequency sample beyond the source date")
    current_ids = [
        "short_term_index_1m_return",
        "short_term_index_ytd_return",
        "short_term_index_12m_return",
        "short_term_monthly_roll_cost",
    ]
    if {metrics[key].as_of for key in current_ids} != {"2026-09-16"}:
        raise ValueError("dashboard metrics must share the reported as-of date")

    required_scenarios = {"contango_curve", "backwardation_curve", "convergence_example"}
    if required_scenarios.difference(scenarios):
        raise ValueError("required illustrative scenarios are missing")
    if any(point.role != "illustrative" for points in scenarios.values() for point in points.values()):
        raise ValueError("scenario values must be labeled illustrative")
    contango = [scenarios["contango_curve"][m].value for m in ("M1", "M2", "M3")]
    backwardation = [scenarios["backwardation_curve"][m].value for m in ("M1", "M2", "M3")]
    if not contango[0] < contango[1] < contango[2]:
        raise ValueError("illustrative contango curve must slope upward")
    if not backwardation[0] > backwardation[1] > backwardation[2]:
        raise ValueError("illustrative backwardation curve must slope downward")


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _build_figures(metrics: Dict[str, Metric], scenarios: Dict[str, Dict[str, ScenarioPoint]]) -> None:
    import matplotlib.pyplot as plt

    plt.rcParams.update({"font.family": "DejaVu Sans", "axes.titleweight": "bold"})
    navy, blue, red, grey, line = "#12263F", "#245B80", "#A84632", "#607287", "#D9E2EA"

    maturities = ["M1", "M2", "M3"]
    fig, ax = plt.subplots(figsize=(8, 5), dpi=180)
    for scenario, color, label in [
        ("contango_curve", blue, "Contango"),
        ("backwardation_curve", red, "Backwardation"),
    ]:
        values = [scenarios[scenario][maturity].value for maturity in maturities]
        ax.plot(maturities, values, marker="o", linewidth=2.5, markersize=7, color=color, label=label)
    ax.set_title("Illustrative VIX futures curve shapes")
    ax.set_ylabel("VIX points")
    ax.grid(axis="y", color=line, linewidth=0.8)
    ax.legend(frameon=False)
    ax.tick_params(colors=navy)
    fig.tight_layout()
    fig.savefig(FIGURES / "week17_curve_shapes.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)

    labels = ["1 month", "YTD", "12 months"]
    values = [
        metrics["short_term_index_1m_return"].value,
        metrics["short_term_index_ytd_return"].value,
        metrics["short_term_index_12m_return"].value,
    ]
    fig, ax = plt.subplots(figsize=(8, 5), dpi=180)
    bars = ax.bar(labels, values, color=[grey, blue, red], width=0.58)
    ax.axhline(0, color=navy, linewidth=1)
    ax.set_title("S&P 500 VIX Short-Term Futures Index")
    ax.set_ylabel("Total return, %")
    ax.set_ylim(-55, 5)
    ax.grid(axis="y", color=line, linewidth=0.8)
    ax.set_axisbelow(True)
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, value - 2.2, f"{value:.2f}%", ha="center", va="top", color=navy, weight="bold")
    ax.text(0.98, 0.05, "As of 16 Sep 2026", transform=ax.transAxes, ha="right", color=grey)
    fig.tight_layout()
    fig.savefig(FIGURES / "week17_recent_index_returns.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def build_outputs() -> dict:
    TABLES.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    metrics = load_metrics()
    scenarios = load_scenarios()
    validate_inputs(metrics, scenarios)

    convergence = scenarios["convergence_example"]
    purchase = convergence["front_future_purchase"].value
    settlement = convergence["settlement_soq"].value
    example_return = convergence_return(purchase, settlement)

    snapshot_rows = [
        {
            "horizon": label,
            "total_return_pct": metrics[key].value,
            "as_of": metrics[key].as_of,
            "source_id": metrics[key].source_id,
        }
        for label, key in [
            ("1 month", "short_term_index_1m_return"),
            ("YTD", "short_term_index_ytd_return"),
            ("12 months", "short_term_index_12m_return"),
        ]
    ]
    _write_csv(TABLES / "published_snapshot.csv", ["horizon", "total_return_pct", "as_of", "source_id"], snapshot_rows)

    convergence_rows = [
        {"item": "Spot VIX at start", "value": convergence["spot_vix_start"].value, "unit": "VIX points"},
        {"item": "Front future purchase", "value": purchase, "unit": "VIX points"},
        {"item": "Settlement SOQ", "value": settlement, "unit": "VIX points"},
        {"item": "Illustrative futures return", "value": round(example_return * 100, 2), "unit": "percent"},
    ]
    _write_csv(TABLES / "illustrative_convergence.csv", ["item", "value", "unit"], convergence_rows)

    public_results = {
        "status": "source_reported_statistics_plus_illustrative_scenarios",
        "metrics": {key: asdict(value) for key, value in metrics.items()},
        "scenarios": {
            scenario: {point: asdict(value) for point, value in points.items()}
            for scenario, points in scenarios.items()
        },
        "illustrative_convergence_return": example_return,
        "interpretation_limits": [
            "The greater-than-80% contango statistic covers 2010 through 26 July 2022, not 2026.",
            "The September 2026 index returns are a point-in-time total-return snapshot, not a long-run estimate.",
            "Roll drag arises through futures price changes, convergence and rebalancing, not from an immediate cash loss created by the roll trade itself.",
            "The convergence example excludes collateral return, fees, slippage and changes in the VIX settlement level.",
        ],
    }
    (TABLES / "public_results.json").write_text(json.dumps(public_results, indent=2), encoding="utf-8")
    _build_figures(metrics, scenarios)
    return public_results


if __name__ == "__main__":
    results = build_outputs()
    print(json.dumps({
        "illustrative_convergence_return_pct": round(100 * results["illustrative_convergence_return"], 2),
        "output_directory": str(REPORT),
    }, indent=2))

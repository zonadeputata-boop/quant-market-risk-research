#!/usr/bin/env python3
"""Run the Week 15 stylized strategy-capacity model.

The model is a deterministic scenario, not an estimate of a particular fund's
capacity. Its square-root impact proxy follows a common empirical specification,
but every numerical parameter in the input CSV is an explicit assumption.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Dict, Iterable, List


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ASSUMPTIONS = ROOT / "data" / "raw" / "week15_model_assumptions.csv"
DEFAULT_OUTPUT = ROOT / "reports" / "week_15_strategy_capacity"


def load_assumptions(path: Path) -> Dict[str, float]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    values = {row["parameter"]: float(row["value"]) for row in rows}
    required = {
        "gross_alpha_annual",
        "portfolio_volatility_annual",
        "rebalances_per_year",
        "trade_fraction_per_rebalance",
        "fixed_cost_bps",
        "daily_volatility",
        "effective_adv_usd",
        "impact_coefficient",
        "participation_limit",
    }
    missing = required.difference(values)
    if missing:
        raise ValueError(f"Missing assumptions: {sorted(missing)}")
    if any(values[name] <= 0 for name in required):
        raise ValueError("All model assumptions must be positive")
    return values


def annual_turnover(assumptions: Dict[str, float]) -> float:
    return (
        assumptions["rebalances_per_year"]
        * assumptions["trade_fraction_per_rebalance"]
    )


def market_impact_rate(
    trade_usd: float,
    effective_adv_usd: float,
    daily_volatility: float,
    impact_coefficient: float,
) -> float:
    """Return impact cost per dollar traded as a decimal."""
    if trade_usd < 0 or effective_adv_usd <= 0:
        raise ValueError("Trade size must be non-negative and ADV must be positive")
    participation = trade_usd / effective_adv_usd
    return impact_coefficient * daily_volatility * math.sqrt(participation)


def capacity_row(aum_usd: float, assumptions: Dict[str, float]) -> Dict[str, float]:
    trade_usd = aum_usd * assumptions["trade_fraction_per_rebalance"]
    participation = trade_usd / assumptions["effective_adv_usd"]
    turnover = annual_turnover(assumptions)
    fixed_rate = assumptions["fixed_cost_bps"] / 10_000.0
    impact_rate = market_impact_rate(
        trade_usd,
        assumptions["effective_adv_usd"],
        assumptions["daily_volatility"],
        assumptions["impact_coefficient"],
    )
    fixed_cost_annual = turnover * fixed_rate
    impact_cost_annual = turnover * impact_rate
    total_cost_annual = fixed_cost_annual + impact_cost_annual
    net_alpha_annual = assumptions["gross_alpha_annual"] - total_cost_annual
    return {
        "aum_usd": aum_usd,
        "trade_usd": trade_usd,
        "participation_rate": participation,
        "annual_turnover": turnover,
        "fixed_cost_annual": fixed_cost_annual,
        "impact_cost_per_trade": impact_rate,
        "impact_cost_annual": impact_cost_annual,
        "total_cost_annual": total_cost_annual,
        "net_alpha_annual": net_alpha_annual,
        "net_alpha_to_volatility": net_alpha_annual
        / assumptions["portfolio_volatility_annual"],
    }


def economic_break_even_aum(assumptions: Dict[str, float]) -> float:
    """Solve analytically for AUM where modeled net alpha equals zero."""
    turnover = annual_turnover(assumptions)
    fixed_cost = turnover * assumptions["fixed_cost_bps"] / 10_000.0
    alpha_budget = assumptions["gross_alpha_annual"] - fixed_cost
    if alpha_budget <= 0:
        return 0.0
    denominator = (
        turnover
        * assumptions["impact_coefficient"]
        * assumptions["daily_volatility"]
    )
    participation = (alpha_budget / denominator) ** 2
    trade_usd = participation * assumptions["effective_adv_usd"]
    return trade_usd / assumptions["trade_fraction_per_rebalance"]


def participation_limit_aum(assumptions: Dict[str, float]) -> float:
    return (
        assumptions["participation_limit"]
        * assumptions["effective_adv_usd"]
        / assumptions["trade_fraction_per_rebalance"]
    )


def sensitivity_rows(assumptions: Dict[str, float]) -> List[Dict[str, float | str]]:
    scenarios = [
        ("Baseline", {}),
        ("Gross alpha 3%", {"gross_alpha_annual": 0.03}),
        ("ADV down 40%", {"effective_adv_usd": 300_000_000.0}),
        ("Daily volatility 3%", {"daily_volatility": 0.03}),
        ("Gross alpha 5%", {"gross_alpha_annual": 0.05}),
    ]
    output: List[Dict[str, float | str]] = []
    for name, changes in scenarios:
        scenario = dict(assumptions)
        scenario.update(changes)
        output.append(
            {
                "scenario": name,
                "economic_break_even_aum_usd": economic_break_even_aum(scenario),
            }
        )
    return output


def write_csv(path: Path, rows: Iterable[Dict[str, object]]) -> None:
    rows = list(rows)
    if not rows:
        raise ValueError("Cannot write an empty result table")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def generate_figures(
    capacity: List[Dict[str, float]],
    sensitivity: List[Dict[str, float | str]],
    output_dir: Path,
) -> None:
    import matplotlib.pyplot as plt

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11})
    figures = output_dir / "figures"
    figures.mkdir(parents=True, exist_ok=True)

    aum = [row["aum_usd"] / 1_000_000 for row in capacity]
    alpha = [row["net_alpha_annual"] * 100 for row in capacity]
    fig, ax = plt.subplots(figsize=(8.4, 4.8))
    ax.plot(aum, alpha, color="#245B80", linewidth=2.5, marker="o")
    ax.axhline(0, color="#A84632", linewidth=1.4)
    ax.set(xlabel="AUM (USD millions)", ylabel="Modeled net alpha (%)")
    ax.grid(axis="y", color="#D9E2EA", linewidth=0.8)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(figures / "week15_net_alpha_by_aum.png", dpi=180)
    plt.close(fig)

    names = [str(row["scenario"]) for row in sensitivity]
    values = [float(row["economic_break_even_aum_usd"]) / 1_000_000 for row in sensitivity]
    fig, ax = plt.subplots(figsize=(8.4, 4.8))
    colors = ["#245B80" if name == "Baseline" else "#7D8FA2" for name in names]
    ax.barh(names, values, color=colors)
    ax.set(xlabel="Economic break-even AUM (USD millions)")
    ax.grid(axis="x", color="#D9E2EA", linewidth=0.8)
    ax.spines[["top", "right"]].set_visible(False)
    ax.invert_yaxis()
    fig.tight_layout()
    fig.savefig(figures / "week15_capacity_sensitivity.png", dpi=180)
    plt.close(fig)


def run(assumptions_path: Path, output_dir: Path, make_plots: bool = True) -> dict:
    assumptions = load_assumptions(assumptions_path)
    aum_grid_millions = [10, 25, 50, 100, 250, 280, 500]
    capacity = [
        capacity_row(value * 1_000_000.0, assumptions)
        for value in aum_grid_millions
    ]
    sensitivity = sensitivity_rows(assumptions)
    tables = output_dir / "tables"
    write_csv(tables / "capacity_results.csv", capacity)
    write_csv(tables / "capacity_sensitivity.csv", sensitivity)

    summary = {
        "model_classification": "stylized deterministic scenario",
        "annual_turnover": annual_turnover(assumptions),
        "economic_break_even_aum_usd": economic_break_even_aum(assumptions),
        "participation_limit_aum_usd": participation_limit_aum(assumptions),
        "capacity_results": capacity,
        "sensitivity_results": sensitivity,
        "assumptions": assumptions,
    }
    tables.mkdir(parents=True, exist_ok=True)
    (tables / "public_results.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    if make_plots:
        generate_figures(capacity, sensitivity, output_dir)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assumptions", type=Path, default=DEFAULT_ASSUMPTIONS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-plots", action="store_true")
    args = parser.parse_args()
    summary = run(args.assumptions, args.output, make_plots=not args.no_plots)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

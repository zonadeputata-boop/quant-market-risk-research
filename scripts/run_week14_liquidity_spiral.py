"""Reproduce Week 14: a stylized leverage and price-impact feedback model.

The scenario is deterministic and hypothetical. It illustrates a mechanism; it
does not estimate a causal effect, probability, or empirical market-impact law.
"""
from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ASSUMPTIONS = ROOT / "data/raw/week14_model_assumptions.csv"
CASE_STUDY = ROOT / "data/raw/week14_case_study.csv"
REPORT = ROOT / "reports/week_14_liquidity_spirals"


@dataclass(frozen=True)
class State:
    scenario: str
    iteration: int
    assets: float
    debt: float
    equity: float
    leverage: float
    sale: float
    impact_return: float
    cumulative_sale: float
    cumulative_impact: float


def leverage(assets: float, debt: float) -> float:
    equity = assets - debt
    if equity <= 0:
        raise ValueError("Equity must remain positive")
    return assets / equity


def required_sale(assets: float, debt: float, maximum_leverage: float) -> float:
    """Sale needed to restore leverage when all proceeds repay debt.

    A sale executed at the current price changes assets and debt by the same
    amount, so equity stays unchanged until subsequent price impact occurs.
    """
    if maximum_leverage <= 1:
        raise ValueError("Maximum leverage must exceed one")
    equity = assets - debt
    if equity <= 0:
        raise ValueError("Equity must be positive")
    return max(0.0, assets - maximum_leverage * equity)


def simulate(
    *, scenario: str, initial_assets: float, initial_debt: float,
    external_shock: float, maximum_leverage: float, impact_sensitivity: float,
    tolerance: float = 1e-8, max_iterations: int = 500,
) -> tuple[list[State], dict[str, float | int | str]]:
    if initial_assets <= initial_debt or initial_debt < 0:
        raise ValueError("Require positive initial equity and nonnegative debt")
    if not -1 < external_shock <= 0:
        raise ValueError("External shock must be in (-1, 0]")
    if not 0 <= impact_sensitivity < 1:
        raise ValueError("Impact sensitivity must be in [0, 1)")

    initial_equity = initial_assets - initial_debt
    assets = initial_assets * (1 + external_shock)
    debt = initial_debt
    cumulative_sale = 0.0
    cumulative_multiplier = 1.0
    states: list[State] = []

    for iteration in range(1, max_iterations + 1):
        equity = assets - debt
        sale = required_sale(assets, debt, maximum_leverage)
        if sale <= tolerance:
            break
        if sale > assets or sale > debt:
            raise RuntimeError("Scenario cannot restore leverage by repaying debt")

        pre_sale_assets = assets
        assets -= sale
        debt -= sale
        cumulative_sale += sale

        impact_return = -impact_sensitivity * (sale / pre_sale_assets)
        assets *= 1 + impact_return
        cumulative_multiplier *= 1 + impact_return
        equity = assets - debt
        current_leverage = leverage(assets, debt)
        states.append(State(
            scenario=scenario, iteration=iteration, assets=assets, debt=debt,
            equity=equity, leverage=current_leverage, sale=sale,
            impact_return=impact_return, cumulative_sale=cumulative_sale,
            cumulative_impact=cumulative_multiplier - 1,
        ))
    else:
        raise RuntimeError("Model did not converge")

    final_equity = assets - debt
    summary = {
        "scenario": scenario,
        "impact_sensitivity": impact_sensitivity,
        "external_shock": external_shock,
        "post_shock_assets_before_sales": initial_assets * (1 + external_shock),
        "post_shock_equity_before_sales": initial_assets * (1 + external_shock) - initial_debt,
        "post_shock_leverage_before_sales": leverage(initial_assets * (1 + external_shock), initial_debt),
        "iterations": len(states),
        "total_forced_sale": cumulative_sale,
        "forced_sale_pct_initial_assets": cumulative_sale / initial_assets,
        "cumulative_impact_return": cumulative_multiplier - 1,
        "final_assets": assets,
        "final_debt": debt,
        "final_equity": final_equity,
        "equity_loss_pct": 1 - final_equity / initial_equity,
        "final_leverage": leverage(assets, debt),
    }
    return states, summary


def load_assumptions(path: Path) -> dict[str, float]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    values = {row["parameter"]: float(row["value"]) for row in rows}
    required = {
        "initial_assets", "initial_debt", "external_price_shock",
        "maximum_leverage", "impact_sensitivity_no_feedback",
        "impact_sensitivity_lower_feedback", "impact_sensitivity_stronger_feedback",
    }
    missing = required - values.keys()
    if missing:
        raise ValueError(f"Missing assumptions: {sorted(missing)}")
    return values


def validate_case_study(path: Path) -> pd.DataFrame:
    data = pd.read_csv(path)
    expected = {
        "period_start", "period_end", "metric", "value", "value_qualifier",
        "unit", "source_url", "source_note",
    }
    if set(data.columns) != expected or len(data) != 3:
        raise ValueError("Unexpected case-study schema or row count")
    if data["metric"].duplicated().any() or (data["value"] <= 0).any():
        raise ValueError("Case-study metrics must be unique and positive")
    if data.isna().any().any():
        raise ValueError("Case-study data must be complete")
    return data


def make_figure(summary: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(9.5, 5.5))
    colors = ["#607287", "#245B80", "#B85D3C"]
    bars = ax.bar(summary["label"], summary["total_forced_sale"], color=colors, width=.62)
    ax.bar_label(bars, labels=[f"${x:.1f}" for x in summary["total_forced_sale"]], padding=5, fontsize=11)
    ax.set_ylabel("Cumulative forced sale ($)")
    ax.set_ylim(0, 40)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.grid(axis="y", color="#DAE3EB", linewidth=.8)
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(path, dpi=180, facecolor="#F8FAFC")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--assumptions", type=Path, default=ASSUMPTIONS)
    parser.add_argument("--case-study", type=Path, default=CASE_STUDY)
    parser.add_argument("--output", type=Path, default=REPORT)
    args = parser.parse_args()

    values = load_assumptions(args.assumptions)
    case_study = validate_case_study(args.case_study)
    tables = args.output / "tables"
    figures = args.output / "figures"
    tables.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)

    scenario_specs = [
        ("no_feedback", "No feedback", values["impact_sensitivity_no_feedback"]),
        ("lower_feedback", "Lower feedback", values["impact_sensitivity_lower_feedback"]),
        ("stronger_feedback", "Stronger feedback", values["impact_sensitivity_stronger_feedback"]),
    ]
    all_states: list[dict] = []
    summaries: list[dict] = []
    for scenario, label, sensitivity in scenario_specs:
        states, summary = simulate(
            scenario=scenario,
            initial_assets=values["initial_assets"],
            initial_debt=values["initial_debt"],
            external_shock=values["external_price_shock"],
            maximum_leverage=values["maximum_leverage"],
            impact_sensitivity=sensitivity,
        )
        all_states.extend(asdict(state) for state in states)
        summary["label"] = label
        summaries.append(summary)

    path_df = pd.DataFrame(all_states)
    summary_df = pd.DataFrame(summaries)
    path_df.to_csv(tables / "iteration_path.csv", index=False)
    summary_df.to_csv(tables / "scenario_summary.csv", index=False)
    case_study.to_csv(tables / "case_study_validated.csv", index=False)
    make_figure(summary_df, figures / "forced_sale_comparison.png")

    public = {
        "title": "Liquidity Spirals: When Margin Calls Force the Next Sale",
        "model_type": "deterministic hypothetical scenario",
        "assumptions": values,
        "scenarios": summaries,
        "case_study": case_study.to_dict(orient="records"),
    }
    (tables / "public_results.json").write_text(json.dumps(public, indent=2) + "\n", encoding="utf-8")
    quality = {
        "assumption_rows": len(values),
        "case_study_rows": len(case_study),
        "case_study_missing_cells": int(case_study.isna().sum().sum()),
        "scenario_count": len(summary_df),
        "all_scenarios_converged": bool((summary_df["final_leverage"] <= values["maximum_leverage"] + 1e-7).all()),
    }
    (tables / "data_quality.json").write_text(json.dumps(quality, indent=2) + "\n", encoding="utf-8")
    print(summary_df[["label", "total_forced_sale", "cumulative_impact_return", "equity_loss_pct", "final_leverage"]].to_string(index=False))


if __name__ == "__main__":
    main()


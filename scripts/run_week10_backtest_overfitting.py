#!/usr/bin/env python3
"""Week 10: controlled null simulation for backtest selection bias.

Every candidate strategy has a true expected return of zero. The script asks
what happens when a researcher selects the best in-sample Sharpe ratio from an
increasing number of independent trials, then evaluates that same selection on
an independent out-of-sample period.

The simulation uses the exact null distribution of the one-sample t-statistic
under iid Gaussian returns. It is a diagnostic of selection bias, not a trading
strategy and not a historical performance backtest.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import t as student_t


TRIAL_COUNTS = (1, 5, 10, 25, 50, 100, 250, 500)
DEFAULT_SEED = 20260817
DEFAULT_EXPERIMENTS = 10_000
TRADING_DAYS = 252
TRAIN_DAYS = 756
TEST_DAYS = 504
ALPHA = 0.05


def annualized_sharpe_from_t(t_stat: np.ndarray, observations: int) -> np.ndarray:
    """Convert a one-sample t-statistic into an annualized sample Sharpe."""

    return np.asarray(t_stat, dtype=float) * np.sqrt(TRADING_DAYS / observations)


def simulate_trial_count(
    n_trials: int,
    experiments: int,
    rng: np.random.Generator,
) -> tuple[dict[str, float], pd.DataFrame]:
    """Simulate selection from ``n_trials`` zero-edge candidates."""

    if n_trials < 1:
        raise ValueError("n_trials must be positive")
    if experiments < 100:
        raise ValueError("experiments must be at least 100")

    train_t = rng.standard_t(df=TRAIN_DAYS - 1, size=(experiments, n_trials))
    selected_index = np.argmax(train_t, axis=1)
    selected_train_t = train_t[np.arange(experiments), selected_index]

    # The test sample is independent of model selection by construction.
    selected_test_t = rng.standard_t(df=TEST_DAYS - 1, size=experiments)

    train_sharpe = annualized_sharpe_from_t(selected_train_t, TRAIN_DAYS)
    test_sharpe = annualized_sharpe_from_t(selected_test_t, TEST_DAYS)

    naive_critical_t = float(student_t.ppf(1.0 - ALPHA, df=TRAIN_DAYS - 1))
    bonferroni_critical_t = float(
        student_t.ppf(1.0 - ALPHA / n_trials, df=TRAIN_DAYS - 1)
    )

    naive_false_discovery = selected_train_t > naive_critical_t
    bonferroni_false_discovery = selected_train_t > bonferroni_critical_t

    summary = {
        "n_trials": n_trials,
        "experiments": experiments,
        "median_best_is_sharpe": float(np.median(train_sharpe)),
        "mean_best_is_sharpe": float(np.mean(train_sharpe)),
        "median_selected_oos_sharpe": float(np.median(test_sharpe)),
        "mean_selected_oos_sharpe": float(np.mean(test_sharpe)),
        "median_selection_optimism": float(np.median(train_sharpe - test_sharpe)),
        "simulated_naive_fwer": float(np.mean(naive_false_discovery)),
        "independent_naive_fwer": float(1.0 - (1.0 - ALPHA) ** n_trials),
        "simulated_bonferroni_fwer": float(np.mean(bonferroni_false_discovery)),
        "independent_bonferroni_fwer": float(
            1.0 - (1.0 - ALPHA / n_trials) ** n_trials
        ),
        "prob_selected_oos_sharpe_below_zero": float(np.mean(test_sharpe < 0.0)),
        "naive_critical_is_sharpe": float(
            annualized_sharpe_from_t(naive_critical_t, TRAIN_DAYS)
        ),
        "bonferroni_critical_is_sharpe": float(
            annualized_sharpe_from_t(bonferroni_critical_t, TRAIN_DAYS)
        ),
    }

    draws = pd.DataFrame(
        {
            "n_trials": n_trials,
            "experiment": np.arange(1, experiments + 1),
            "selected_is_sharpe": train_sharpe,
            "selected_oos_sharpe": test_sharpe,
            "naive_false_discovery": naive_false_discovery.astype(int),
            "bonferroni_false_discovery": bonferroni_false_discovery.astype(int),
        }
    )
    return summary, draws


def run_simulation(
    trial_counts: tuple[int, ...] = TRIAL_COUNTS,
    experiments: int = DEFAULT_EXPERIMENTS,
    seed: int = DEFAULT_SEED,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Run all trial-count scenarios with one reproducible random stream."""

    rng = np.random.default_rng(seed)
    summaries: list[dict[str, float]] = []
    detail_frames: list[pd.DataFrame] = []
    for n_trials in trial_counts:
        summary, draws = simulate_trial_count(n_trials, experiments, rng)
        summaries.append(summary)
        detail_frames.append(draws)
    return pd.DataFrame(summaries), pd.concat(detail_frames, ignore_index=True)


def write_outputs(output_dir: Path, experiments: int, seed: int) -> pd.DataFrame:
    """Run the simulation and write the reproducible output bundle."""

    output_dir.mkdir(parents=True, exist_ok=True)
    summary, draws = run_simulation(experiments=experiments, seed=seed)

    summary.to_csv(output_dir / "trial_count_summary.csv", index=False)
    draws.to_csv(output_dir / "simulation_draws.csv.gz", index=False, compression="gzip")

    metadata = {
        "design": "controlled null Monte Carlo",
        "true_expected_return": 0.0,
        "candidate_dependence": "independent by construction",
        "return_assumption": "iid Gaussian",
        "train_days": TRAIN_DAYS,
        "test_days": TEST_DAYS,
        "annualization_days": TRADING_DAYS,
        "alpha_one_sided": ALPHA,
        "experiments_per_trial_count": experiments,
        "trial_counts": list(TRIAL_COUNTS),
        "seed": seed,
        "interpretation": (
            "Selection-bias diagnostic only; not historical performance and not "
            "evidence about any investable strategy."
        ),
    }
    (output_dir / "simulation_metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/week_10_backtest_overfitting_and_false_discovery/tables"),
    )
    parser.add_argument("--experiments", type=int, default=DEFAULT_EXPERIMENTS)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = write_outputs(args.output_dir, args.experiments, args.seed)
    display_columns = [
        "n_trials",
        "median_best_is_sharpe",
        "median_selected_oos_sharpe",
        "simulated_naive_fwer",
        "simulated_bonferroni_fwer",
    ]
    print(summary[display_columns].to_string(index=False, float_format=lambda x: f"{x:.4f}"))


if __name__ == "__main__":
    main()

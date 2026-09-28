# Week 15 - Strategy Capacity

This add-on reproduces the numerical scenario used in the LinkedIn carousel
"Strategy Capacity: Why Alpha Shrinks as AUM Grows."

The analysis is a stylized deterministic scenario. It does not estimate the
capacity of a live fund. Gross alpha, turnover, volatility, effective ADV,
fixed costs, the impact coefficient and the participation limit are explicit
assumptions in `data/raw/week15_model_assumptions.csv`.

## Reproduce

```bash
python3 -m pip install -r requirements-week15.txt
python3 scripts/run_week15_strategy_capacity.py
python3 -m unittest discover -s tests -p "test_week15*.py" -v
```

The script writes inspectable CSV and JSON results to
`reports/week_15_strategy_capacity/tables/` and two PNG figures to
`reports/week_15_strategy_capacity/figures/`.

## Model

For a rebalance trade `Q` and effective daily dollar volume `V`, the modeled
impact cost per dollar traded is:

`impact = coefficient * daily volatility * sqrt(Q / V)`

Annual cost equals annual one-way turnover multiplied by fixed cost plus the
impact cost. Economic break-even capacity is the AUM where modeled net alpha
equals zero. A separate participation policy can bind before that point.

## Evidence and limitations

Empirical research supports a concave relationship between order size and
market impact, and several studies use a square-root specification. Other work
finds that duration and participation can require richer functional forms.
Therefore, capacity should be reported as a sensitivity range and recalibrated
with a manager's own arrival-price and execution data.

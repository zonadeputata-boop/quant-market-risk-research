# Week 16: Implied vs. Realized Volatility

Reproducible companion files for the LinkedIn carousel **Why the gap is not free alpha**.

## Run

From the repository root:

```bash
python3 -m pip install -r requirements-week16.txt
python3 scripts/run_week16_implied_realized.py
python3 -m unittest discover -s tests -p 'test_week16_*.py'
```

## Contents

- `posts/week_16_implied_vs_realized_volatility/`: caption, carousel copy and methodology
- `data/raw/`: source-reported metrics and source metadata
- `scripts/`: reproducible validation and chart generation
- `tests/`: consistency and calculation tests
- `reports/week_16_implied_vs_realized_volatility/`: generated tables, figures and research summary

## Data note

The package intentionally uses published summary statistics instead of redistributing a proprietary daily index history. The output is educational research, not investment advice or a live trading signal.

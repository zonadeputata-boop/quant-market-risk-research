# Week 07 - Drawdown-Aware Position Sizing

## Research question

If two positions have similar volatility but different loss paths, should they
carry the same exposure?

## Design

The research combines:

1. a 63-day realized-volatility estimate;
2. a 10% annual volatility target;
3. a 1.00x maximum exposure;
4. a recursive drawdown calculation on strategy equity;
5. a 20% drawdown budget;
6. a 0.25 minimum drawdown scalar; and
7. lagged exposure to avoid look-ahead.

## Risk interpretation

The volatility scalar controls current risk intensity. The drawdown scalar
reduces exposure when the capital path has deteriorated. The combined overlay
must be evaluated against turnover, transaction costs, time under water and
the risk of procyclical deleveraging.

## Reproduce

```bash
PYTHONPATH=src python3 scripts/run_week07_drawdown_aware_position_sizing.py
```

## Disclaimer

For educational and analytical purposes only. Not investment advice.

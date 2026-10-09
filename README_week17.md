# Week 17 — VIX futures are not spot VIX

This add-on contains the publication copy, official-source metadata, a small
reproducible analysis, figures, tables and tests for Week 17 of the Quant Market
Risk Research series.

## Reproduce

From this add-on directory:

```bash
python3 -m pip install -r requirements-week17.txt
python3 scripts/run_week17_vix_futures.py
python3 -m unittest discover -s tests -p 'test_week17*.py' -v
```

The script writes output to:

```text
reports/week_17_vix_futures/
├── figures/
└── tables/
```

## Evidence boundary

- Source-reported statistics are stored in `data/raw/week17_source_reported_metrics.csv`.
- Illustrative curve and convergence values are isolated in `data/raw/week17_scenario_assumptions.csv`.
- The Cboe contango frequency covers 2010 through 26 July 2022.
- The S&P DJI performance figures are a snapshot as of 16 September 2026.
- No proprietary daily history is redistributed and no strategy backtest is claimed.

## Core interpretation

The VIX Index itself cannot be held directly. VIX futures settle to a future VIX
Special Opening Quotation, while short-term VIX futures indices maintain a
rolling position in nearby contracts. Their returns can therefore differ
materially from a change in spot VIX.

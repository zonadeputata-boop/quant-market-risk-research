# Week 14: Liquidity Spirals

This add-on contains the LinkedIn post, a reproducible stylized model, source data, generated tables, a figure and unit tests.

## Reproduce

```bash
python3 -m pip install -r requirements-week14.txt
python3 scripts/run_week14_liquidity_spiral.py
python3 -m unittest discover -s tests -p "test_week14*.py" -v
```

Run the commands from the root of this add-on.

## Interpretation

The model is a deterministic hypothetical scenario. The price-impact sensitivities are assumptions. The official UK gilt-market figures are stored separately in `data/raw/week14_case_study.csv` and do not calibrate the model.


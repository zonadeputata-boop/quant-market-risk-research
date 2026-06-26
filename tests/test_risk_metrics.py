import pandas as pd

from quant_research.risk_metrics import historical_var, expected_shortfall, max_drawdown


def test_historical_var_is_quantile():
    returns = pd.Series([-0.05, -0.02, -0.01, 0.00, 0.01, 0.02])
    var = historical_var(returns, confidence=0.95)
    assert var <= 0


def test_expected_shortfall_is_not_above_var_for_losses():
    returns = pd.Series([-0.05, -0.02, -0.01, 0.00, 0.01, 0.02])
    var = historical_var(returns, confidence=0.80)
    es = expected_shortfall(returns, confidence=0.80)
    assert es <= var


def test_max_drawdown_negative_or_zero():
    returns = pd.Series([0.10, -0.05, 0.02, -0.10, 0.03])
    assert max_drawdown(returns) <= 0

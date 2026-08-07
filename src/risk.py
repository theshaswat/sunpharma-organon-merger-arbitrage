"""Volatility, stationarity, and GARCH helpers."""

import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import adfuller
from statsmodels.stats.diagnostic import acorr_ljungbox
from arch import arch_model


def annualised_vol(returns: pd.Series, trading_days: int = 252) -> float:
    return returns.std() * np.sqrt(trading_days)


def rolling_vol(returns: pd.Series, window: int = 30, trading_days: int = 252) -> pd.Series:
    return returns.rolling(window).std() * np.sqrt(trading_days)


def adf_test(series: pd.Series) -> dict:
    series = series.dropna()
    stat, pval, lags, nobs, crit, icbest = adfuller(series, autolag="AIC")
    return {"stat": stat, "p_value": pval, "lags": lags, "n_obs": nobs, "critical_values": crit,
            "stationary_at_5pct": pval < 0.05}


def arch_lm_test(returns: pd.Series, lags: int = 12) -> dict:
    squared = returns.dropna() ** 2
    lb = acorr_ljungbox(squared, lags=[lags], return_df=True)
    return {"lb_stat": lb["lb_stat"].iloc[0], "lb_pvalue": lb["lb_pvalue"].iloc[0],
            "arch_effect_present": lb["lb_pvalue"].iloc[0] < 0.05}


def fit_garch(returns_pct: pd.Series, p: int = 1, q: int = 1):
    """returns_pct: returns expressed in percent (e.g. 1.2 for 1.2%), which is
    the arch package's expected scale for numerical stability."""
    am = arch_model(returns_pct.dropna(), vol="Garch", p=p, q=q, dist="t")
    return am.fit(disp="off")

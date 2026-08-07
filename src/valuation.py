"""CAPM / WACC / DCF valuation helpers."""

import numpy as np
import pandas as pd
from scipy.optimize import brentq


def regression_beta(asset_ret: pd.Series, market_ret: pd.Series) -> tuple:
    """OLS beta and annualised alpha. Returns (beta, annualised_alpha, n_obs, r_squared)."""
    df = pd.concat([asset_ret, market_ret], axis=1).dropna()
    df.columns = ["asset", "market"]
    x = df["market"].values
    y = df["asset"].values
    beta, alpha_daily = np.polyfit(x, y, 1)
    pred = beta * x + alpha_daily
    ss_res = np.sum((y - pred) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    r2 = 1 - ss_res / ss_tot
    annualised_alpha = alpha_daily * 252
    return beta, annualised_alpha, len(df), r2


def cost_of_equity(rf: float, beta: float, erp: float) -> float:
    return rf + beta * erp


def cost_of_debt(interest_expense: float, avg_total_debt: float, tax_rate: float) -> float:
    pretax_kd = interest_expense / avg_total_debt
    return pretax_kd * (1 - tax_rate)


def wacc(equity_value: float, debt_value: float, ke: float, kd_after_tax: float) -> float:
    """kd_after_tax must already be after-tax (see cost_of_debt, which applies
    (1 - tax_rate) once) — do not apply the tax shield twice here."""
    v = equity_value + debt_value
    return (equity_value / v) * ke + (debt_value / v) * kd_after_tax


def dcf_value(fcff_forecast: list, discount_rate: float, terminal_growth: float,
              terminal_method: str = "gordon", exit_multiple: float = None,
              terminal_ebitda: float = None) -> dict:
    n = len(fcff_forecast)
    pv_factors = [(1 + discount_rate) ** -i for i in range(1, n + 1)]
    pv_fcff = [cf * pv for cf, pv in zip(fcff_forecast, pv_factors)]
    pv_explicit = sum(pv_fcff)

    if terminal_method == "gordon":
        if discount_rate <= terminal_growth:
            raise ValueError("discount_rate must exceed terminal_growth for Gordon growth to converge")
        terminal_value = fcff_forecast[-1] * (1 + terminal_growth) / (discount_rate - terminal_growth)
    elif terminal_method == "exit_multiple":
        if exit_multiple is None or terminal_ebitda is None:
            raise ValueError("exit_multiple and terminal_ebitda required for exit_multiple method")
        terminal_value = exit_multiple * terminal_ebitda
    else:
        raise ValueError(f"unknown terminal_method: {terminal_method}")

    pv_terminal = terminal_value * pv_factors[-1]
    enterprise_value = pv_explicit + pv_terminal

    return {
        "pv_fcff": pv_fcff,
        "pv_explicit_sum": pv_explicit,
        "terminal_value": terminal_value,
        "pv_terminal": pv_terminal,
        "enterprise_value": enterprise_value,
        "tv_share_of_ev": pv_terminal / enterprise_value,
    }


def equity_value_per_share(enterprise_value: float, net_debt: float, shares_outstanding: float) -> float:
    return (enterprise_value - net_debt) / shares_outstanding


def sensitivity_grid(fcff_forecast: list, wacc_range: list, growth_range: list, net_debt: float,
                      shares_outstanding: float) -> pd.DataFrame:
    grid = pd.DataFrame(index=[f"{w:.1%}" for w in wacc_range], columns=[f"{g:.1%}" for g in growth_range])
    for w in wacc_range:
        for g in growth_range:
            if w <= g:
                grid.loc[f"{w:.1%}", f"{g:.1%}"] = np.nan
                continue
            res = dcf_value(fcff_forecast, w, g, terminal_method="gordon")
            grid.loc[f"{w:.1%}", f"{g:.1%}"] = equity_value_per_share(
                res["enterprise_value"], net_debt, shares_outstanding
            )
    return grid.astype(float)


def reverse_dcf_growth(fcff_base: float, n_years: int, discount_rate: float, terminal_growth: float,
                        net_debt: float, shares_outstanding: float, target_price: float) -> float:
    """Solve for the constant annual FCFF growth rate g (applied uniformly
    across the explicit forecast) that makes the DCF equity value per share
    equal target_price. Returns g; raises if no solution in [-0.30, 0.60]."""

    def value_at_growth(g):
        forecast = [fcff_base * (1 + g) ** i for i in range(1, n_years + 1)]
        res = dcf_value(forecast, discount_rate, terminal_growth, terminal_method="gordon")
        return equity_value_per_share(res["enterprise_value"], net_debt, shares_outstanding) - target_price

    return brentq(value_at_growth, -0.30, 0.60, xtol=1e-6)

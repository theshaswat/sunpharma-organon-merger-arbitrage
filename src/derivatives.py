"""Black-Scholes pricing and Greeks, built from first principles (no market
IV is consumed anywhere here - see notebook 08 for why the OGN option chain
is unusable as a calibration source)."""

import numpy as np
from scipy.stats import norm


def bs_d1_d2(S, K, r, sigma, T):
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return d1, d2


def bs_call(S, K, r, sigma, T):
    d1, d2 = bs_d1_d2(S, K, r, sigma, T)
    return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)


def bs_put(S, K, r, sigma, T):
    d1, d2 = bs_d1_d2(S, K, r, sigma, T)
    return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)


def greeks(S, K, r, sigma, T, option_type="call"):
    d1, d2 = bs_d1_d2(S, K, r, sigma, T)
    pdf_d1 = norm.pdf(d1)
    if option_type == "call":
        delta = norm.cdf(d1)
        theta = (-(S * pdf_d1 * sigma) / (2 * np.sqrt(T))
                 - r * K * np.exp(-r * T) * norm.cdf(d2)) / 365
        rho = K * T * np.exp(-r * T) * norm.cdf(d2) / 100
    else:
        delta = norm.cdf(d1) - 1
        theta = (-(S * pdf_d1 * sigma) / (2 * np.sqrt(T))
                 + r * K * np.exp(-r * T) * norm.cdf(-d2)) / 365
        rho = -K * T * np.exp(-r * T) * norm.cdf(-d2) / 100
    gamma = pdf_d1 / (S * sigma * np.sqrt(T))
    vega = S * pdf_d1 * np.sqrt(T) / 100
    return {"delta": delta, "gamma": gamma, "vega": vega, "theta": theta, "rho": rho}


def risk_neutral_deal_value(offer: float, break_price: float, p_completion: float, r: float, T: float) -> float:
    expected_payoff = p_completion * offer + (1 - p_completion) * break_price
    return expected_payoff * np.exp(-r * T)


def protective_put_payoff(spot_range: np.ndarray, S0: float, K: float, put_premium: float) -> np.ndarray:
    stock_pnl = spot_range - S0
    put_payoff = np.maximum(K - spot_range, 0) - put_premium
    return stock_pnl + put_payoff


def long_stock_payoff(spot_range: np.ndarray, S0: float) -> np.ndarray:
    return spot_range - S0


def collar_payoff(spot_range: np.ndarray, S0: float, put_K: float, put_premium: float,
                   call_K: float, call_premium: float) -> np.ndarray:
    stock_pnl = spot_range - S0
    put_payoff = np.maximum(put_K - spot_range, 0) - put_premium
    call_payoff = -np.maximum(spot_range - call_K, 0) + call_premium
    return stock_pnl + put_payoff + call_payoff

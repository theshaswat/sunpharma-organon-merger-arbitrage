"""Market-model event study: abnormal returns, CAR, and significance tests."""

import numpy as np
import pandas as pd


def estimate_market_model(asset_ret: pd.Series, market_ret: pd.Series,
                           estimation_window: pd.DatetimeIndex) -> dict:
    df = pd.concat([asset_ret, market_ret], axis=1).dropna()
    df.columns = ["asset", "market"]
    df = df.loc[df.index.intersection(estimation_window)]
    x = df["market"].values
    y = df["asset"].values
    beta, alpha = np.polyfit(x, y, 1)
    resid = y - (alpha + beta * x)
    resid_std = resid.std(ddof=2)
    return {"alpha": alpha, "beta": beta, "resid_std": resid_std, "n_obs": len(df)}


def abnormal_returns(asset_ret: pd.Series, market_ret: pd.Series, model: dict) -> pd.Series:
    df = pd.concat([asset_ret, market_ret], axis=1).dropna()
    df.columns = ["asset", "market"]
    expected = model["alpha"] + model["beta"] * df["market"]
    return df["asset"] - expected


def event_window_dates(all_dates: pd.DatetimeIndex, event_date: pd.Timestamp, pre: int, post: int) -> pd.DatetimeIndex:
    idx = all_dates.searchsorted(event_date)
    lo = max(0, idx + pre)
    hi = min(len(all_dates), idx + post + 1)
    return all_dates[lo:hi]


def car_with_tstat(ar: pd.Series, window_dates: pd.DatetimeIndex, resid_std: float) -> dict:
    window_ar = ar.reindex(window_dates).dropna()
    car = window_ar.sum()
    n = len(window_ar)
    se = resid_std * np.sqrt(n)
    tstat = car / se if se > 0 else np.nan
    from scipy.stats import t as tdist
    pval = 2 * (1 - tdist.cdf(abs(tstat), df=n - 1)) if n > 1 else np.nan
    return {"CAR": car, "n_days": n, "t_stat": tstat, "p_value": pval}


def abnormal_volume(volume: pd.Series, event_date: pd.Timestamp, baseline_window: int = 60,
                     event_pre: int = 10, event_post: int = 0) -> dict:
    all_dates = volume.index
    idx = all_dates.searchsorted(event_date)
    baseline = volume.iloc[max(0, idx - baseline_window - event_pre): max(0, idx - event_pre)]
    event_period = volume.iloc[max(0, idx - event_pre): idx + event_post + 1]
    baseline_mean = baseline.mean()
    baseline_std = baseline.std()
    event_mean = event_period.mean()
    z = (event_mean - baseline_mean) / baseline_std if baseline_std > 0 else np.nan
    return {
        "baseline_mean_volume": baseline_mean,
        "event_mean_volume": event_mean,
        "ratio": event_mean / baseline_mean,
        "z_score": z,
    }

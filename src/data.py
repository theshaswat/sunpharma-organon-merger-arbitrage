"""Data acquisition helpers. Every pull is saved once to data/raw and never
overwritten in place — downstream notebooks read from disk, not from a live
re-pull, so numbers stay stable once the snapshot is taken."""

import warnings
import pandas as pd
import yfinance as yf

from src import config as cfg

warnings.filterwarnings("ignore")


def pull_price_history(ticker: str, start: str = cfg.HISTORY_START) -> pd.DataFrame:
    df = yf.Ticker(ticker).history(start=start, auto_adjust=False)
    df.index = pd.to_datetime(df.index.date)
    df.index.name = "date"
    return df


def pull_all_prices(tickers=None, start: str = cfg.HISTORY_START) -> dict:
    tickers = tickers or cfg.ALL_TICKERS
    out = {}
    for t in tickers:
        out[t] = pull_price_history(t, start)
    return out


def save_prices(prices: dict, snapshot: str = cfg.SNAPSHOT_DATE):
    for ticker, df in prices.items():
        fname = ticker.replace("^", "").replace("=", "")
        path = cfg.DATA_RAW / f"prices_{fname}_{snapshot}.parquet"
        df.to_parquet(path)


def load_prices(tickers=None, snapshot: str = cfg.SNAPSHOT_DATE) -> dict:
    tickers = tickers or cfg.ALL_TICKERS
    out = {}
    for t in tickers:
        fname = t.replace("^", "").replace("=", "")
        path = cfg.DATA_RAW / f"prices_{fname}_{snapshot}.parquet"
        out[t] = pd.read_parquet(path)
    return out


def pull_statements(ticker: str) -> dict:
    tk = yf.Ticker(ticker)
    return {
        "income_stmt": tk.income_stmt,
        "balance_sheet": tk.balance_sheet,
        "cashflow": tk.cashflow,
        "quarterly_income_stmt": tk.quarterly_income_stmt,
        "quarterly_balance_sheet": tk.quarterly_balance_sheet,
        "quarterly_cashflow": tk.quarterly_cashflow,
    }


def save_statements(ticker: str, statements: dict, snapshot: str = cfg.SNAPSHOT_DATE):
    for name, df in statements.items():
        path = cfg.DATA_RAW / f"stmt_{ticker.replace('.', '_')}_{name}_{snapshot}.parquet"
        df.to_parquet(path)


def load_statements(ticker: str, snapshot: str = cfg.SNAPSHOT_DATE) -> dict:
    names = [
        "income_stmt", "balance_sheet", "cashflow",
        "quarterly_income_stmt", "quarterly_balance_sheet", "quarterly_cashflow",
    ]
    out = {}
    for name in names:
        path = cfg.DATA_RAW / f"stmt_{ticker.replace('.', '_')}_{name}_{snapshot}.parquet"
        out[name] = pd.read_parquet(path)
    return out


def close_panel(prices: dict, tickers=None) -> pd.DataFrame:
    tickers = tickers or list(prices.keys())
    panel = pd.concat({t: prices[t]["Close"] for t in tickers}, axis=1)
    return panel


def log_returns(panel: pd.DataFrame) -> pd.DataFrame:
    import numpy as np
    return np.log(panel / panel.shift(1)).dropna(how="all")

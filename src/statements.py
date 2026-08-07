"""FCFF / FCFE construction and ratio analysis from yfinance statement data."""

import pandas as pd
import numpy as np


def _row(df: pd.DataFrame, label: str) -> pd.Series:
    """Pull a row by label; return an all-NaN series (same columns) if the
    label isn't present in this filer's taxonomy, instead of raising -
    line-item availability differs firm to firm and callers should decide
    how to handle a missing item."""
    if label in df.index:
        return df.loc[label]
    return pd.Series(np.nan, index=df.columns)


def build_fcff(income_stmt: pd.DataFrame, cashflow: pd.DataFrame, tax_rate: float = None) -> pd.DataFrame:
    """Uses yfinance's 'Tax Rate For Calcs' (a normalized marginal rate) for
    NOPAT rather than the raw GAAP effective rate (Tax Provision / Pretax
    Income). The raw effective rate is unusable here - Organon's swings from
    +56% to -52% year to year on valuation-allowance and one-off items, which
    would make NOPAT non-comparable across years for no economic reason."""
    ebit = _row(income_stmt, "EBIT")
    normalized_tax_rate = _row(income_stmt, "Tax Rate For Calcs")

    dep_amort = _row(cashflow, "Depreciation And Amortization")
    capex = _row(cashflow, "Capital Expenditure")  # already negative in yfinance convention
    dwc = _row(cashflow, "Change In Working Capital")

    t = normalized_tax_rate if tax_rate is None else pd.Series(tax_rate, index=ebit.index)

    nopat = ebit * (1 - t)
    fcff = nopat + dep_amort + capex + dwc  # capex already negative

    out = pd.DataFrame({
        "EBIT": ebit,
        "normalized_tax_rate": t,
        "NOPAT": nopat,
        "D&A": dep_amort,
        "CapEx": capex,
        "Delta_NWC": dwc,
        "FCFF": fcff,
    })
    return out.T


def build_fcfe(fcff_row: pd.Series, interest_expense: pd.Series, tax_rate: pd.Series,
               net_borrowing: pd.Series) -> pd.Series:
    after_tax_interest = interest_expense * (1 - tax_rate)
    return fcff_row - after_tax_interest + net_borrowing


def ratio_snapshot(income_stmt: pd.DataFrame, balance_sheet: pd.DataFrame, cashflow: pd.DataFrame) -> pd.DataFrame:
    """Columns are pinned to income_stmt's own column order (most-recent-first,
    yfinance's native convention) via explicit reindex. Building this from a
    dict of Series with mismatched column sets - balance_sheet routinely has
    one extra year vs income_stmt/cashflow - makes pandas silently re-sort
    columns ascending, which flips 'most recent' to 'oldest' under .iloc[:,0].
    That happened here for four of the seven peers before this fix."""
    balance_sheet = balance_sheet.reindex(columns=income_stmt.columns)
    cashflow = cashflow.reindex(columns=income_stmt.columns)
    revenue = _row(income_stmt, "Total Revenue")
    ebit = _row(income_stmt, "EBIT")
    ebitda = _row(income_stmt, "EBITDA")
    net_income = _row(income_stmt, "Net Income")
    interest_expense = _row(income_stmt, "Interest Expense")

    total_debt = _row(balance_sheet, "Total Debt")
    total_equity = _row(balance_sheet, "Stockholders Equity")
    cash = _row(balance_sheet, "Cash And Cash Equivalents")
    invested_capital = _row(balance_sheet, "Invested Capital")

    out = pd.DataFrame({
        "revenue": revenue,
        "ebit_margin": ebit / revenue,
        "ebitda_margin": ebitda / revenue,
        "net_margin": net_income / revenue,
        "interest_coverage": ebit / interest_expense.abs(),
        "debt_to_equity": total_debt / total_equity,
        "net_debt": total_debt - cash,
        "roic": (ebit * 0.79) / invested_capital,  # 21% approximate statutory-blend tax; refined per-firm in notebook 02
    }, index=income_stmt.columns)
    return out.T

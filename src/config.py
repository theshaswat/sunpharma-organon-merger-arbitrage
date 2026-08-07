"""Shared constants for the Sun Pharma / Organon analysis."""

from pathlib import Path
from datetime import date

ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
DATA_EXTERNAL = ROOT / "data" / "external"
DATA_FINAL = ROOT / "data" / "final"
OUT_CHARTS = ROOT / "outputs" / "charts"
OUT_TABLES = ROOT / "outputs" / "tables"

for d in [DATA_RAW, DATA_PROCESSED, DATA_EXTERNAL, DATA_FINAL, OUT_CHARTS, OUT_TABLES]:
    d.mkdir(parents=True, exist_ok=True)

SNAPSHOT_DATE = "2026-08-06"

TARGET = "OGN"
ACQUIRER = "SUNPHARMA.NS"
US_INDEX = "^GSPC"
IN_INDEX = "^NSEI"
VIX = "^VIX"
FX = "INR=X"
UST10Y = "^TNX"

US_PEERS = ["MRK", "PFE", "VTRS", "TEVA"]
IN_PEERS = ["CIPLA.NS", "DRREDDY.NS", "LUPIN.NS"]

ALL_TICKERS = [TARGET, ACQUIRER, US_INDEX, IN_INDEX, VIX, FX, UST10Y] + US_PEERS + IN_PEERS

HISTORY_START = "2021-01-01"

# deal terms, sourced from Organon 8-K Exhibit 99.1 filed 2026-04-27
# (accession 0001193125-26-178718) and cross-checked against the DEFA14A
# proxy filings on SEC EDGAR, CIK 0001821825
DEAL = {
    "offer_price_usd": 14.00,
    "deal_ev_usd_bn": 11.75,
    "announcement_date": date(2026, 4, 26),
    "leak_date": date(2026, 1, 16),
    "unaffected_date": date(2026, 4, 9),
    "shareholder_approval_date": date(2026, 7, 23),
    "expected_close": "early 2027",
    "shares_outstanding": 262_609_433,
    "target_net_debt_ebitda_post_deal": 2.3,
    "fy2025_revenue_usd_bn": 6.2,
    "fy2025_adj_ebitda_usd_bn": 1.9,
    "fy2025_debt_usd_bn": 8.6,
    "fy2025_cash_usd_mn": 574,
    "divestiture_upfront_usd_mn": 440,  # one-off, closed prior to close, not recurring
    "synergy_disclosed": False,  # confirmed: 8-K Ex-99.1 uses only qualitative
    # language ("scope for synergies including significant revenue upside
    # opportunities"), no dollar figure. Any synergy number in this project
    # is a reverse-DCF estimate, not a disclosed figure.
}

# event windows for the event study, in trading days around each date
EVENT_WINDOWS = [(-1, 1), (-5, 5), (-10, 10)]

# estimation window for the market model MUST end before the leak date to
# avoid contaminating alpha/beta with the run-up itself
ESTIMATION_WINDOW_END = date(2026, 1, 15)
ESTIMATION_WINDOW_LENGTH = 250  # trading days

RANDOM_SEED = 42

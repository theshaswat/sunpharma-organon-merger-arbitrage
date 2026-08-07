# Assumptions Log

Every non-trivial input to this project, its value, its source, and the check that confirms it. Snapshot date for all market data: **2026-08-06** (the last completed trading session at the time of analysis). Document prepared 2026-08-07.

## Deal terms (facts, not assumptions — sourced directly)

| Item | Value | Source | Check |
|---|---|---|---|
| Offer price | $14.00/share, all cash | Organon Form 8-K, Exhibit 99.1, filed 2026-04-27, SEC EDGAR accession 0001193125-26-178718 | Read in full via direct filing fetch, not secondary reporting |
| Deal enterprise value | $11.75bn | Same 8-K | Reconciled independently: shares outstanding × offer + FY2025 net debt = $11.747bn, within 0.03% |
| Shares outstanding | 262,609,433 | Yahoo Finance (`sharesOutstanding`, cross-checked against `impliedSharesOutstanding`) | Both fields agree exactly |
| Announcement date | 2026-04-26 | 8-K Exhibit 99.1 | — |
| Reference/leak date | 2026-01-16 | 8-K Exhibit 99.1 ("before news of takeover interest emerged") | Price/premium reconciliation below |
| Unaffected date | 2026-04-09 | 8-K Exhibit 99.1 | Price/premium reconciliation below |
| Shareholder approval date | 2026-07-23 | SEC DEFA14A filings | — |
| Synergy figure disclosed | **No** — qualitative only ("scope for synergies including significant revenue upside opportunities") | 8-K Exhibit 99.1, full text searched for dollar figures | Confirmed by direct text search of the filing; no number found |
| Post-deal target Net Debt/EBITDA | 2.3x | 8-K Exhibit 99.1 | — |

**Premium reconciliation (the check that validates the whole data pull):**
- 16-Jan-2026 close $8.73–$8.76 (varies slightly by pull date, within tolerance) → premium to $14.00 = 60.4%, matches disclosed 60% within 1pp
- 9-Apr-2026 close $6.90–$6.91 → premium to $14.00 = 102.9%, matches disclosed 103% within 1pp

## Valuation assumptions

| Assumption | Value | Rationale / source |
|---|---|---|
| Beta estimation window | 250 trading days ending 2026-01-15 | Must end before the leak/reference date or the window is contaminated by the deal's own run-up |
| Risk-free rate | 4.293% (10Y UST, unaffected date) | Yahoo Finance ^TNX |
| Equity risk premium | 4.45% | Damodaran, *Equity Risk Premiums: Determinants, Estimates and Implications*, 2026 edition, implied ERP, July 2026 update — a dated, sourced, published figure, not assumed |
| Normalized tax rate | 21% (FY2025) | Yahoo Finance "Tax Rate For Calcs" — used instead of the raw GAAP effective rate, which swings from +56% to -52% year to year on one-off items unrelated to operations |
| Cost of debt (embedded) | 5.75% pretax | FY2025 interest expense / average FY24-25 debt — reflects 2021 spinoff-era, healthier-credit terms |
| Cost of debt (marginal) | 9.79% pretax | Risk-free + 5.50% default spread, from Damodaran's interest-coverage-to-synthetic-rating table (smaller-firm version), keyed off Organon's 1.84x interest coverage → B3/B- |
| WACC used | 6.61% (market-implied) | Solved numerically: the discount rate at which the flat-revenue DCF reproduces the actual $6.90 unaffected price. Falls between the embedded (5.29%) and marginal (7.90%) bounds — treated as validating the framework |
| Terminal growth | 1.5% | Below the risk-free rate; consistent with a maturing, patent-cliff-exposed portfolio, not a growth business |
| Revenue growth, base case | 0% (flat) | FY2025 revenue was down 2.9% and the 3-year trend is roughly flat; flat is the conservative, defensible base case |
| FCFF forecast drivers | Held at FY2025 ratio to revenue (EBIT margin, D&A%, CapEx%, ΔNWC%) | No basis for assuming these improve or worsen without a specific reason; held constant is the transparent default |

## Statistical / methodological choices

| Choice | Rationale |
|---|---|
| Single-ticker return series built from each ticker's own trading calendar, not a multi-ticker panel | A panel indexed on the union of every ticker's dates causes `.shift(1)` to shift by a row in that unioned calendar, not by one actual trading day for a given ticker — silently drops or corrupts real return observations. Caught during notebook 04 construction (a "spread today" value came back `NaN`) and fixed at the source before it could propagate. |
| Granger causality direction-specific lag structure | NSE trades ~03:45-10:00 UTC, NYSE ~13:30-20:00 UTC — non-overlapping. Sun Pharma's same-date close is valid same-day information for Organon; the reverse requires a one-day lag. Standard same-day-paired Granger causality in the "Sun → OGN" direction would otherwise use information Organon's market could not yet have seen. |
| GARCH fit separately pre/post announcement | A single model spanning the volatility break would average two different regimes and misrepresent both. |
| Ratio benchmark table pinned to `income_stmt.columns` order via explicit reindex | Building the table from a dict of Series with mismatched column sets (balance sheet routinely has one extra year vs. income statement) caused pandas to silently re-sort columns ascending, flipping "most recent" to "oldest" under positional indexing — corrupted 4 of 7 peer companies' ratios before being caught and fixed. |
| Break price scenarios: unaffected, -10%, -20% | The unaffected price is a proxy for the break price, not a measurement — a real broken deal can print below it if fundamentals moved during the process. |
| Options priced from first principles, not market quotes | Organon's own listed options were tested directly (bid/ask, open interest, implied volatility) and found unusable — zero bid/ask and zero open interest at the money, confirmed across every large US pharma peer checked (Merck, Pfizer, Viatris, Teva), ruling out an Organon-specific explanation. |
| Volatility input for hedge pricing: pre-leak regime (58.0%), not post-announcement (4.5%) | Post-announcement volatility is compressed *because* the market expects the deal to close — pricing deal-break insurance with it is circular. |
| Monte Carlo random seed | Fixed at 42 (`config.RANDOM_SEED`) for reproducibility. |

## Known reconciliation gaps (disclosed, not resolved)

- Regulatory/closing conditions outstanding as of the snapshot date were not independently verified beyond the SEC filings read.
- Break price is a modeled proxy, not an observed outcome (the deal had not closed or broken as of the snapshot date).
- Organon (December FY) and Sun Pharma (March FY) are calendarised to TTM only where directly compared; other same-period figures use each company's own latest annual filing.

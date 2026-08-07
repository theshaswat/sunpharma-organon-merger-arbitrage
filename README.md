# Merger Arbitrage and Synergy Valuation: The Sun Pharma – Organon Deal

> Did Sun Pharma overpay $11.75bn for a declining, 11.5x-levered pharmaceutical company — and does the merger-arbitrage spread pay for the risk that the deal breaks?

*Prepared 7 August 2026. All market data is the 6 August 2026 close — the last completed trading session at the time of analysis.*

## Core Question

On 26 April 2026, Sun Pharmaceutical Industries agreed to acquire NYSE-listed Organon & Co for $14.00/share in cash — a 102.9% premium to the unaffected price and the largest deal ever undertaken by an Indian pharmaceutical company. The deal was still pending as of the snapshot date (6 August 2026), with shareholder approval obtained and close expected in early 2027. This project values Organon independently, quantifies the growth/synergy the offer price requires, tests how the market actually behaved around the deal's key dates, and evaluates the merger-arbitrage position available today on a risk-adjusted basis.

## Key Findings

| Finding | Value |
|---|---|
| Standalone DCF value/share (market-cross-validated discount rate) | $6.90 |
| Offer price | $14.00 |
| Revenue growth required to justify the offer | 3.87% (vs. actual -0.38% 2yr CAGR) |
| Implied synergy / growth premium | $1.86bn (18.9% of standalone EV) |
| Acquirer (Sun Pharma) CAR around announcement | +9.6%, statistically significant — positive, not the muted/negative reaction an overpaying acquirer typically shows |
| Realised volatility collapse post-announcement | 94.2% → 4.5% (~95% collapse) |
| Spread-implied completion probability (today) | 93.9% |
| Forward-looking Monte Carlo mean annualised return | 0.07% — below the 4.62% risk-free rate |
| Recommendation | PASS on the unhedged spread at today's price — conditional, not categorical |

## Methodology

- Standalone FCFF valuation with a discount rate solved to reproduce the market's own unaffected price, cross-validated against independently modelled embedded and marginal (synthetic-credit-rating) cost-of-debt bounds
- Reverse-DCF to quantify the growth/synergy premium the offer price implies — no synergy figure was disclosed by management, confirmed directly against the primary SEC filing
- Market-model event study (CAR, abnormal volume) around three dates — a pre-announcement reference date, the announcement, and shareholder approval — for both target and acquirer, plus a peer-spillover test
- GARCH(1,1) volatility regimes and cross-market Granger causality, with the lag structure built around the verified fact that NSE and NYSE do not share overlapping trading hours
- Merger-arbitrage sizing via spread-implied completion probability, breakeven analysis, and a seeded 100,000-path Monte Carlo simulation
- Black-Scholes derivatives priced from first principles after directly testing (and rejecting) Organon's own listed options as a usable data source

## Deliverables

| File | What it is |
|---|---|
| `reports/Final_Report.pdf` | Full write-up — methodology, findings, limitations |
| `presentation/IC_Deck.pdf` | Investment-committee deck, 8 slides, speaker notes included |
| `model/SunPharma_Organon_Model.xlsx` | Live-formula valuation model; the Inputs tab drives everything downstream |
| `notebooks/` | Nine sequential notebooks, outputs intact — the full analysis path |

## Data

Yahoo Finance (prices, volumes, financial statements — snapshot 2026-08-06) and SEC EDGAR (Organon Form 8-K, Exhibit 99.1, filed 2026-04-27, and related DEFA14A filings, CIK 0001821825). Both free sources; no proprietary terminal used. Equity risk premium and the interest-coverage-to-credit-rating mapping are from Damodaran's publicly maintained NYU Stern datasets. See `reports/ASSUMPTIONS_LOG.md` for every non-trivial input, its value, its source, and the check that confirms it.

## How to Run

```bash
pip install -r requirements.txt
jupyter nbconvert --to notebook --execute --inplace notebooks/*.ipynb
```

Run the notebooks in numeric order. **Notebook 01 must run first** — raw vendor pulls are not committed to this repository, and 01 rebuilds `data/raw/` from scratch before anything downstream can read it. Each subsequent notebook consumes what the previous ones wrote. `src/checks.py` holds the reconciliation suite that 01 runs against the known deal facts before any analysis depends on the data; it fails loudly rather than proceeding on numbers that do not tie out.

Because the notebooks are committed with their outputs intact, every result below can be read without running anything.

## Results

`reports/Final_Report.pdf` is the full written analysis and `presentation/IC_Deck.pdf` the summary deck — both render inline in the browser. `model/SunPharma_Organon_Model.xlsx` is the live spreadsheet model: the Inputs tab is the only sheet containing typed values, and every other cell is a formula, so changing an assumption flows through the DCF, sensitivity grid, arbitrage calculator, and Black-Scholes tab.

## Limitations & Assumptions

1. The DCF's discount rate is calibrated to reproduce the unaffected market price — this validates internal consistency (cross-checked against two independently modelled bounds) but is the market's own implied rate, not an independent ground-up estimate.
2. No dollar synergy figure was disclosed by Sun Pharma; every synergy number here is this project's own reverse-DCF construction.
3. The break price used for arbitrage sizing ($6.90, the unaffected close, with -10%/-20% sensitivity) is a proxy — a broken deal can print anywhere.
4. Outstanding regulatory or other closing conditions as of the snapshot date were not verified beyond the SEC filings reviewed.
5. Organon's fiscal year (December) and Sun Pharma's (March) were reconciled to trailing-twelve-month figures only where directly compared; other same-period comparisons use each company's own most recent annual filing.
6. This is a point-in-time analysis as of 6 August 2026 — prices, spreads, and implied probabilities move daily.

## Author

Shaswat Sharma

"""Reconciliation checks. These must pass before any output is treated as
final. Each check ties a computed figure back to a sourced, external fact
rather than to another computation inside this project."""

from src import config as cfg


class ReconciliationError(AssertionError):
    pass


def check_premium(price_16jan: float, price_9apr: float, offer: float = cfg.DEAL["offer_price_usd"],
                   tol: float = 0.01):
    prem_16jan = offer / price_16jan - 1
    prem_9apr = offer / price_9apr - 1
    if abs(prem_16jan - 0.604) > tol:
        raise ReconciliationError(
            f"16-Jan premium {prem_16jan:.3%} does not match reported 60.4% (price used: {price_16jan})"
        )
    if abs(prem_9apr - 1.029) > tol:
        raise ReconciliationError(
            f"9-Apr premium {prem_9apr:.3%} does not match reported 102.9% (price used: {price_9apr})"
        )
    return {"premium_16jan": prem_16jan, "premium_9apr": prem_9apr}


def check_deal_ev(shares_outstanding: int, net_debt_usd: float,
                   offer: float = cfg.DEAL["offer_price_usd"],
                   reported_ev_bn: float = cfg.DEAL["deal_ev_usd_bn"], tol_pct: float = 0.02):
    equity_value = shares_outstanding * offer
    implied_ev_bn = (equity_value + net_debt_usd) / 1e9
    diff_pct = implied_ev_bn / reported_ev_bn - 1
    if abs(diff_pct) > tol_pct:
        raise ReconciliationError(
            f"Implied EV {implied_ev_bn:.3f}B differs from reported {reported_ev_bn}B by {diff_pct:.2%} "
            f"(tolerance {tol_pct:.0%}). Check the net-debt date used — this reconciles only against "
            f"the FY2025 (2025-12-31) balance sheet net debt, not a later quarter."
        )
    return {"equity_value_bn": equity_value / 1e9, "implied_ev_bn": implied_ev_bn, "diff_pct": diff_pct}


def check_terminal_value_share(pv_explicit: float, pv_terminal: float, max_share: float = 0.75):
    ev = pv_explicit + pv_terminal
    share = pv_terminal / ev
    flagged = share > max_share
    return {"tv_share": share, "flagged": flagged, "enterprise_value": ev}


def check_beta_window_uncontaminated(estimation_window_end):
    if estimation_window_end >= cfg.DEAL["leak_date"]:
        raise ReconciliationError(
            f"Beta estimation window ends {estimation_window_end}, on or after the leak date "
            f"{cfg.DEAL['leak_date']}. This window is contaminated by the run-up and must not "
            f"be used for cost-of-equity estimation."
        )
    return True


def check_dcf_identity(fcff_pv_sum: float, terminal_pv: float, enterprise_value: float, tol: float = 1e-6):
    computed = fcff_pv_sum + terminal_pv
    if abs(computed - enterprise_value) / enterprise_value > tol:
        raise ReconciliationError(
            f"DCF identity fails: sum of PV(FCFF) + PV(terminal) = {computed:,.2f} "
            f"but enterprise_value = {enterprise_value:,.2f}"
        )
    return True


def run_all_price_checks(price_16jan, price_9apr, shares_outstanding, net_debt_usd):
    results = {}
    results["premium"] = check_premium(price_16jan, price_9apr)
    results["ev"] = check_deal_ev(shares_outstanding, net_debt_usd)
    print("RECONCILIATION SUITE")
    print(f"  16-Jan premium   : {results['premium']['premium_16jan']:.1%}  (reported 60.4%)  PASS")
    print(f"  9-Apr premium    : {results['premium']['premium_9apr']:.1%}  (reported 102.9%) PASS")
    print(f"  Implied EV       : ${results['ev']['implied_ev_bn']:.3f}B  (reported $11.75B, "
          f"diff {results['ev']['diff_pct']:+.2%}) PASS")
    return results

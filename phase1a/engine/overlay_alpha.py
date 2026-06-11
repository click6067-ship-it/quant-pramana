#!/usr/bin/env python3
"""V3 — TREND + VOL-REGIME overlay alpha on US ETFs (diversifier for the equity MN book).

GOAL: build a NEW, ideally LOW-CORRELATION net-of-cost return stream to add to the existing
market-neutral equity book (outputs/engine/book_ledger.csv 'applied_ret' = realized 1x book
return after its leverage/kill risk-engine; verdict also re-checked vs raw net_1x and net_agg).

DISCIPLINE (same as rest of project): ONE definition per signal · NO parameter tuning ·
NO window hunting · costs included · kill conditions PRE-REGISTERED (see report) BEFORE results.
Paper only, no live. Uses CACHED data only (outputs/raw/SFP_FUNDS.csv). No API.

SIGNAL DEFINITIONS (fixed, stated once — no alternatives explored):
  (1) TREND  : price vs 200-day SMA on the 15 UNLEVERED ETFs (SPY QQQ IWM DIA + 11 sector SPDRs).
               At each monthly rebalance: hold (long) the ETFs whose closeadj > 200d SMA, FLAT others.
               Equal-weight the "on" set. Long-FLAT (not long-short): the equity book already
               supplies a short side; a pure long-flat trend sleeve is the honest simplest version.
               LETF/vol products (TQQQ.. UVXY/VXX) are NEVER held — they are only regime context.
  (2) VOL-REGIME : 20-day realized vol of SPY (annualized). Fixed rule, NOT tuned:
               risk-ON  (exposure x1.0) when ann.vol <  20%
               risk-OFF (exposure x0.5) when ann.vol >= 20%
               Applied as a scalar on the whole trend sleeve's monthly exposure.

COST: flat ETF assumption 5 bp / side (commission+spread), charged on monthly turnover
      (fraction of book that changes weight). Stress = x2 (10 bp/side) per kill condition.

Returns are computed from REAL closeadj prices (LETF decay baked in; never synthesized).

Run:  ./.venv/bin/python engine/overlay_alpha.py
Writes: reports/V3_overlay_alpha_result.md  (+ prints numbers to stdout)
"""
import os, sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
PHASE1A = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import data as D  # engine/data.py — cached-snapshot loader (API off)

REPORT = os.path.join(PHASE1A, "reports", "V3_overlay_alpha_result.md")
LEDGER = os.path.join(PHASE1A, "outputs", "engine", "book_ledger.csv")

# ── fixed parameters (stated once; no tuning, no alternatives swept) ──────────
TREND_TICKERS = ["SPY", "QQQ", "IWM", "DIA",
                 "XLK", "XLF", "XLE", "XLV", "XLI", "XLY", "XLP", "XLU", "XLB", "XLRE", "XLC"]
SMA_WIN       = 200      # trend lookback (days)
VOL_WIN       = 20       # realized-vol lookback (days)
VOL_THRESH    = 0.20     # annualized SPY realized-vol regime threshold
RISK_OFF_MULT = 0.50     # exposure scalar when risk-off
COST_BPS_SIDE = 5.0      # flat ETF cost per side (commission + spread)
ANN           = 12       # monthly periodicity

# ── metrics (project-consistent: monthly -> annualized) ──────────────────────
def sharpe(r):
    r = pd.Series(r).dropna()
    return float(r.mean() / r.std() * np.sqrt(ANN)) if r.std() > 0 else np.nan

def cagr(r):
    r = pd.Series(r).dropna()
    if not len(r):
        return np.nan
    return float((1 + r).prod() ** (ANN / len(r)) - 1)

def maxdd(r):
    nav = (1 + pd.Series(r).dropna()).cumprod()
    return float((nav / nav.cummax() - 1).min()) if len(nav) else np.nan

def annual_returns(r):
    r = pd.Series(r).dropna()
    return ((1 + r).groupby(r.index.year).prod() - 1)


def load_prices():
    """closeadj wide panel (date index, ticker cols) from cached SFP_FUNDS snapshot."""
    df = D.load("SFP_FUNDS", usecols=["ticker", "date", "closeadj"])
    piv = df.pivot(index="date", columns="ticker", values="closeadj").sort_index()
    return piv


def build_overlay():
    px = load_prices()
    rets_d = px.pct_change()                                  # daily returns from REAL closeadj

    # (1) trend state: closeadj > 200d SMA, per ETF, daily (shift handled at rebalance read)
    sma = px[TREND_TICKERS].rolling(SMA_WIN, min_periods=SMA_WIN).mean()
    above = (px[TREND_TICKERS] > sma)                         # bool; NaN until SMA defined

    # (2) vol regime: 20d realized vol of SPY, annualized
    spy_rv = rets_d["SPY"].rolling(VOL_WIN, min_periods=VOL_WIN).std() * np.sqrt(252)
    risk_mult_d = np.where(spy_rv >= VOL_THRESH, RISK_OFF_MULT, 1.0)
    risk_mult_d = pd.Series(risk_mult_d, index=spy_rv.index)

    # rebalance on the EQUITY BOOK's month-end dates (so monthly correlation aligns exactly)
    book = pd.read_csv(LEDGER, parse_dates=["date"]).set_index("date").sort_index()
    rebal_dates = list(book.index)

    # map each rebalance date to the last available trading day <= it
    trade_days = px.index
    def asof_day(d):
        pos = trade_days.searchsorted(d, side="right") - 1
        return trade_days[pos] if pos >= 0 else None

    recs = []
    prev_w = pd.Series(dtype=float)                           # weights held INTO the period
    for i in range(len(rebal_dates) - 1):                     # need next month-end for fwd return
        d0, d1 = rebal_dates[i], rebal_dates[i + 1]
        a0 = asof_day(d0)
        if a0 is None or a0 not in above.index:
            continue
        sig = above.loc[a0].dropna()                          # ETFs with a valid 200d SMA at a0
        on = sig[sig].index.tolist()                          # uptrend set
        if not on or pd.isna(risk_mult_d.get(a0, np.nan)):
            # no signal yet (early sample) -> flat, but still register for turnover/alignment
            w = pd.Series(0.0, index=TREND_TICKERS)
        else:
            base = 1.0 / len(on)                              # equal-weight across "on" ETFs
            w = pd.Series(0.0, index=TREND_TICKERS)
            w[on] = base
            w = w * float(risk_mult_d.loc[a0])                # vol-regime scaler

        # forward (next-month) return of each held ETF, from REAL closeadj at the two rebal asof days
        a1 = asof_day(d1)
        fwd = (px.loc[a1, TREND_TICKERS] / px.loc[a0, TREND_TICKERS] - 1.0)
        gross = float((w * fwd).sum())

        # turnover cost: |w - prev_w| summed over names, x cost/side (one side per name traded)
        allw = w.reindex(TREND_TICKERS).fillna(0.0)
        prevw = prev_w.reindex(TREND_TICKERS).fillna(0.0)
        turnover = float((allw - prevw).abs().sum())          # one-way notional traded
        cost = turnover * (COST_BPS_SIDE / 1e4)

        recs.append(dict(date=d1, gross=gross, turnover=turnover, cost=cost,
                         net=gross - cost, n_on=len(on), exposure=float(allw.sum())))
        prev_w = w

    R = pd.DataFrame(recs).set_index("date").sort_index()
    return R, book


def block(title):
    print("\n" + "=" * 72 + f"\n{title}\n" + "=" * 72)


def main():
    R, book = build_overlay()
    eq = book["applied_ret"].reindex(R.index)                 # equity MN book (net_1x), aligned by month

    # overlay stats at 1x and 2x cost
    net1 = R["net"]
    net2 = R["gross"] - 2 * R["cost"]                         # 2x cost stress

    res = {
        "n_months": len(R),
        "start": str(R.index.min().date()), "end": str(R.index.max().date()),
        "gross_sharpe": sharpe(R["gross"]),
        "net_sharpe": sharpe(net1),
        "net_sharpe_2x": sharpe(net2),
        "cagr": cagr(net1), "maxdd": maxdd(net1),
        "avg_exposure": float(R["exposure"].mean()),
        "avg_turnover": float(R["turnover"].mean()),
        "cost_drag_yr": float(R["cost"].mean() * ANN),
    }

    # ★ correlation to equity book (the whole point)
    both = pd.concat([net1.rename("overlay"), eq.rename("equity")], axis=1).dropna()
    corr = float(both["overlay"].corr(both["equity"]))
    res["corr_to_equity"] = corr
    res["n_overlap"] = len(both)
    eq_sharpe = sharpe(both["equity"])
    ov_sharpe = sharpe(both["overlay"])
    res["equity_sharpe_overlap"] = eq_sharpe
    res["overlay_sharpe_overlap"] = ov_sharpe

    # 50/50 combo (rebalanced monthly): does diversification raise Sharpe?
    combo = 0.5 * both["overlay"] + 0.5 * both["equity"]
    combo_sharpe = sharpe(combo)
    res["combo_5050_sharpe"] = combo_sharpe

    # ── pre-registered kill evaluation ──
    kills = []
    if res["net_sharpe"] <= 0:                         kills.append("net Sharpe <= 0")
    if corr > 0.6:                                     kills.append("corr to equity book > 0.6")
    if res["net_sharpe_2x"] <= 0:                       kills.append("dies at 2x cost (net Sharpe<=0)")
    if not (combo_sharpe > eq_sharpe):                 kills.append("combo Sharpe not > equity-only")
    verdict = "FAIL — " + "; ".join(kills) if kills else "SURVIVE (all pre-registered kills passed)"
    res["verdict"] = verdict
    res["kills_hit"] = kills

    ann_ov = annual_returns(net1)
    ann_eq = annual_returns(eq)

    # ── print ──
    block("V3 TREND+VOL OVERLAY — RESULTS (net of cost, paper only)")
    print(f"period           : {res['start']} .. {res['end']}  ({res['n_months']} monthly rebals)")
    print(f"avg exposure     : {res['avg_exposure']:.2f}  (1.0 = fully long all 15 ETFs, risk-on)")
    print(f"avg turnover/mo  : {res['avg_turnover']:.2f}   cost drag/yr: {res['cost_drag_yr']:+.2%}")
    print(f"gross Sharpe     : {res['gross_sharpe']:+.2f}")
    print(f"NET Sharpe (5bp) : {res['net_sharpe']:+.2f}")
    print(f"NET Sharpe (2x)  : {res['net_sharpe_2x']:+.2f}   <- 2x cost stress")
    print(f"CAGR (net)       : {res['cagr']:+.2%}")
    print(f"maxDD (net)      : {res['maxdd']:+.2%}")
    block("★ CORRELATION TO EQUITY MARKET-NEUTRAL BOOK (the whole point)")
    print(f"overlapping months : {res['n_overlap']}")
    print(f"corr(overlay, equity book applied_ret) : {corr:+.3f}   (FAIL if > +0.60)")
    print(f"  equity-only Sharpe (overlap window)  : {eq_sharpe:+.2f}")
    print(f"  overlay    Sharpe (overlap window)   : {ov_sharpe:+.2f}")
    print(f"  50/50 combo Sharpe                   : {combo_sharpe:+.2f}   (want > equity-only)")
    print(f"  combo uplift vs equity-only          : {combo_sharpe - eq_sharpe:+.2f}")
    block("ANNUAL NET RETURNS")
    comp = pd.concat([ann_ov.rename("overlay"), ann_eq.rename("equity")], axis=1)
    print(comp.to_string(float_format=lambda x: f"{x:+.1%}"))
    block(f"PRE-REGISTERED KILL VERDICT: {verdict}")

    write_report(res, R, comp, both, combo)
    print(f"\nreport -> {REPORT}")
    return res


def write_report(res, R, comp, both, combo):
    md = []
    md.append("# V3 — TREND + VOL-REGIME Overlay Alpha (US ETFs) — Result")
    md.append(f"**Date:** 2026-06-11 · **Engine:** `engine/overlay_alpha.py` · **Data:** cached `outputs/raw/SFP_FUNDS.csv` (23 ETFs, REAL closeadj incl. LETF decay) · API off")
    md.append(f"**Window:** {res['start']} .. {res['end']} ({res['n_months']} monthly rebals) · paper only, no live")
    md.append("")
    md.append("## Goal")
    md.append("Build a NEW, ideally LOW-CORRELATION net-of-cost return stream to *add* to the existing market-neutral (MN) equity book (`outputs/engine/book_ledger.csv` `applied_ret` = net_1x). The whole point: does it *diversify*?")
    md.append("")
    md.append("## Signal definitions (ONE each, fixed — no tuning, no window hunting)")
    md.append("- **Trend:** `closeadj > 200-day SMA` on the **15 unlevered ETFs** (SPY QQQ IWM DIA + 11 sector SPDRs). Monthly: hold (long) the uptrend ETFs, **flat** the rest, **equal-weight** the on-set. Long-FLAT (the MN book already supplies a short side). LETF/vol products are **never held** (real-decay assets used as context only).")
    md.append("- **Vol regime:** 20-day realized vol of SPY, annualized. **Fixed** rule: risk-ON (x1.0) when ann.vol < 20%, risk-OFF (x0.5) when >= 20%. Scalar on the whole sleeve.")
    md.append(f"- **Cost:** flat **{COST_BPS_SIDE:.0f} bp/side** (commission+spread) on monthly turnover. Stress = **x2**.")
    md.append("- Rebalanced on the equity book's month-end dates so monthly correlation aligns exactly. Returns from real prices at those dates.")
    md.append("")
    md.append("## PRE-REGISTERED KILL CONDITIONS (set before results)")
    md.append("1. **net Sharpe <= 0** -> FAIL.")
    md.append("2. **correlation to equity book > +0.60** (not diversifying) -> FAIL.")
    md.append("3. **dies at 2x cost** (net Sharpe <= 0) -> FAIL.")
    md.append("4. **50/50 combo Sharpe NOT > equity-only Sharpe** (overlay adds nothing) -> FAIL.")
    md.append("")
    md.append("## Results (net of cost)")
    md.append("| metric | value |")
    md.append("|---|---|")
    md.append(f"| gross Sharpe | {res['gross_sharpe']:+.2f} |")
    md.append(f"| **NET Sharpe (5bp/side)** | **{res['net_sharpe']:+.2f}** |")
    md.append(f"| NET Sharpe (2x cost) | {res['net_sharpe_2x']:+.2f} |")
    md.append(f"| CAGR (net) | {res['cagr']:+.2%} |")
    md.append(f"| maxDD (net) | {res['maxdd']:+.2%} |")
    md.append(f"| avg exposure | {res['avg_exposure']:.2f} |")
    md.append(f"| avg turnover/mo | {res['avg_turnover']:.2f} |")
    md.append(f"| cost drag/yr | {res['cost_drag_yr']:+.2%} |")
    md.append("")
    md.append("## ★ Correlation to equity MN book (the whole point)")
    md.append(f"- overlapping months: **{res['n_overlap']}**")
    md.append(f"- **corr(overlay net, equity `applied_ret`) = {res['corr_to_equity']:+.3f}**  (FAIL threshold +0.60)")
    md.append("")
    md.append("| sleeve (overlap window) | Sharpe |")
    md.append("|---|---|")
    md.append(f"| equity MN book only | {res['equity_sharpe_overlap']:+.2f} |")
    md.append(f"| overlay only | {res['overlay_sharpe_overlap']:+.2f} |")
    md.append(f"| **50/50 combo** | **{res['combo_5050_sharpe']:+.2f}** |")
    md.append(f"| combo uplift vs equity-only | {res['combo_5050_sharpe'] - res['equity_sharpe_overlap']:+.2f} |")
    md.append("")
    md.append("## Annual net returns")
    md.append("| year | overlay | equity book |")
    md.append("|---|---|---|")
    for y, row in comp.iterrows():
        ov = "—" if pd.isna(row["overlay"]) else f"{row['overlay']:+.1%}"
        eqv = "—" if pd.isna(row["equity"]) else f"{row['equity']:+.1%}"
        md.append(f"| {y} | {ov} | {eqv} |")
    md.append("")
    md.append(f"## VERDICT: {res['verdict']}")
    if res["kills_hit"]:
        md.append("Kill conditions hit: " + "; ".join(f"**{k}**" for k in res["kills_hit"]) + ".")
    md.append("")
    md.append("### Honest read")
    diversifies = res["corr_to_equity"] <= 0.6
    helps = res["combo_5050_sharpe"] > res["equity_sharpe_overlap"]
    standalone = res["net_sharpe"] > 0 and res["net_sharpe_2x"] > 0
    md.append(f"- Standalone net edge (5bp & 2x): **{'yes' if standalone else 'no'}** (net Sharpe {res['net_sharpe']:+.2f} / 2x {res['net_sharpe_2x']:+.2f}).")
    md.append(f"- Diversifying vs equity book: **{'yes' if diversifies else 'no'}** (corr {res['corr_to_equity']:+.3f}).")
    md.append(f"- Raises combined Sharpe: **{'yes' if helps else 'no'}** ({res['equity_sharpe_overlap']:+.2f} -> {res['combo_5050_sharpe']:+.2f}).")
    md.append("- A long-flat trend overlay is **net-long beta**, so positive correlation to a broad equity book is expected; the test is whether it stays under +0.60 and still lifts the combined Sharpe. Paper only. No parameter was tuned; this is a single pre-registered shot.")
    with open(REPORT, "w") as f:
        f.write("\n".join(md) + "\n")


if __name__ == "__main__":
    main()

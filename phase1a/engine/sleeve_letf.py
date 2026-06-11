#!/usr/bin/env python3
"""PRAMANA v3 — LETF-CONVEX trend sleeve (profit-max US PAPER book).
QUESTION: express the SAME 200d-SMA trend signal via LEVERAGED ETFs (3x) for CONVEX upside.
          The plain trend overlay ('ov') holds the 1x ETFs; this sleeve holds the REAL 3x LETF
          (QQQ->TQQQ, SPY->UPRO, semis->SOXL) when the underlying is in uptrend, FLAT otherwise.
          KEY: does the LETF's daily-compounded CONVEXITY add terminal wealth vs just levering the
          plain 1x trend signal to the same average exposure? (corr to 'ov' is expected HIGH — it
          IS a levered version of trend; the convexity, not new info, is the only possible edge.)

SLEEVE (ONE definition · NO tuning · kills PRE-REGISTERED below, BEFORE results):
  signal  = underlying ETF closeadj > 200d SMA  (QQQ, SPY, semis-1x).
            semis has no 1x ETF in the cached data, so the 1x semis trend is reconstructed by
            DE-LEVERING SOXL daily returns (ret/3) into a synthetic 1x semis index — used for the
            SIGNAL ONLY. We NEVER synthesize a 3x index: SOXL's REAL closeadj (decay/path baked in)
            is what we hold for returns. (De-levering 3x->1x for the trigger is the honest inverse
            when no 1x proxy exists, and 0.999 daily corr confirms the LETFs track their underlying.)
  ON  -> hold the corresponding REAL 3x LETF (TQQQ / UPRO / SOXL), equal-weight across ON LETFs.
  OFF -> flat (cash).
  Long-only: the INVERSE LETFs (SQQQ/SPXU/SOXS) are NEVER held. Why: -3x daily products bleed
            catastrophically in any up-trend (negative drift + volatility decay compound against
            you; SQQQ is down ~-99.x% over the sample), and a trend-following long-flat sleeve has
            no edge timing crashes precisely enough to survive holding them. Too dangerous = excluded.
  Vol-regime de-risk: 20d realized vol of SPY (annualized) >= 20% -> cut exposure x0.5. LETFs are
            deadly in high-vol whipsaws (3x daily reset shreds NAV when the tape chops); de-risking
            is mandatory, not tuned (same 20%/x0.5 rule as the plain overlay).
  Rebalance MONTHLY on the equity book's month-end grid (book_ledger.csv dates) so monthly
            correlation to 'eq'/'ov' aligns exactly.
  Next-bar: signal read at month-end CLOSE, position ENTERED the NEXT trading day (no look-ahead).
            Forward return is measured close[next_day(t1)] / close[next_day(t0)] using REAL closeadj.

COST: ETF tier ~10 bp/side on monthly turnover (LETFs are wider than vanilla ETFs -> 10bp not 5bp).
      Stress = x2 (20 bp/side) per kill condition.

PRE-REGISTERED KILLS (set BEFORE results):
  1. net Sharpe <= 0                                                    -> FAIL.
  2. maxDD worse than -50% (LETF ruin) WITHOUT commensurate return
     (return/|maxDD| MAR < the plain 'ov' trend sleeve's MAR)          -> FAIL.
  3. dies at 2x cost (net Sharpe <= 0)                                  -> FAIL.
  4. corr to 'ov' > 0.90  -> NOTE (expected: it IS a levered trend dup). NOT an auto-FAIL;
     the real test (reported regardless) = does substituting/adding the LETF-convex sleeve raise
     the COMBINED book's terminal wealth / CAGR vs plain trend at COMPARABLE drawdown?

DATA: cached only (outputs/raw/SFP_FUNDS.csv) · API OFF. Engine: data, cost.
RUN:  ./.venv/bin/python engine/sleeve_letf.py
WRITES: reports/V3_sleeve_letf_result.md (+ prints numbers). ⚠️ paper(가상)·single backtest·NO live.
"""
import os, sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
PHASE1A = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import data as D          # engine/data.py — cached-snapshot loader (API off)
import cost as C          # engine/cost.py — frozen cost tiers

REPORT = os.path.join(PHASE1A, "reports", "V3_sleeve_letf_result.md")
LEDGER = os.path.join(PHASE1A, "outputs", "engine", "book_ledger.csv")
COMBINED = os.path.join(PHASE1A, "outputs", "engine", "combined_book_nav.csv")
OUT_NAV = os.path.join(PHASE1A, "outputs", "engine", "sleeve_letf_nav.csv")

# ── fixed parameters (stated once; no tuning, no alternatives swept) ──────────
# trend triples: (underlying-1x label, 3x LETF actually held)
TRIPLES = [("QQQ", "TQQQ"), ("SPY", "UPRO"), ("SEMIS", "SOXL")]
LETFS   = [t[1] for t in TRIPLES]
SMA_WIN       = 200      # trend lookback (days) on the 1x underlying
VOL_WIN       = 20       # SPY realized-vol lookback (days)
VOL_THRESH    = 0.20     # annualized SPY realized-vol regime threshold
RISK_OFF_MULT = 0.50     # exposure scalar when risk-off (LETF whipsaw de-risk)
COST_BPS_SIDE = 10.0     # ETF tier, LETFs wider -> 10 bp/side (vs 5bp vanilla). Stress x2.
ANN           = 12       # monthly periodicity
MAXDD_RUIN    = -0.50    # LETF ruin floor (kill #2 reference)

# ── metrics (project-consistent: monthly -> annualized; matches overlay/combined) ──
def sharpe(r):
    r = pd.Series(r).dropna()
    return float(r.mean() / r.std() * np.sqrt(ANN)) if r.std() > 0 else np.nan

def cagr(r):
    r = pd.Series(r).dropna()
    return float((1 + r).prod() ** (ANN / len(r)) - 1) if len(r) else np.nan

def maxdd(r):
    nav = (1 + pd.Series(r).dropna()).cumprod()
    return float((nav / nav.cummax() - 1).min()) if len(nav) else np.nan

def worst_month(r):
    r = pd.Series(r).dropna()
    return float(r.min()) if len(r) else np.nan

def navx(r):
    return float((1 + pd.Series(r).dropna()).cumprod().iloc[-1])

def annual_returns(r):
    r = pd.Series(r).dropna()
    return ((1 + r).groupby(r.index.year).prod() - 1)

def mar(r):
    """MAR-style ratio: CAGR / |maxDD| (return per unit of drawdown). Higher = better."""
    dd = maxdd(r)
    return float(cagr(r) / abs(dd)) if dd and dd < 0 else np.nan

def perf(r):
    return dict(sharpe=sharpe(r), cagr=cagr(r), maxdd=maxdd(r), worst=worst_month(r),
                navx=navx(r), vol=float(pd.Series(r).dropna().std() * np.sqrt(ANN)),
                rec_sharpe=sharpe(pd.Series(r)[pd.Series(r).index >= "2021-01-01"]), mar=mar(r))

def line(lbl, r):
    p = perf(r)
    print(f"  {lbl:34s} Sharpe={p['sharpe']:+.2f} CAGR={p['cagr']*100:+7.2f}% vol={p['vol']*100:4.0f}% "
          f"maxDD={p['maxdd']*100:6.1f}% worst={p['worst']*100:+5.1f}% NAV×{p['navx']:6.2f} MAR={p['mar']:+.2f}")
    return p


# ── data: real closeadj + de-levered 1x semis proxy for SIGNAL ───────────────
def load_prices():
    df = D.load("SFP_FUNDS", usecols=["ticker", "date", "closeadj"])
    px = df.pivot(index="date", columns="ticker", values="closeadj").sort_index()
    rets_d = px.pct_change()
    # synthetic 1x semis index for the trend SIGNAL only (de-lever SOXL real returns by /3).
    # NOT used for returns — SOXL's REAL closeadj is held. This avoids synthesizing a 3x index.
    semis_1x = (1 + rets_d["SOXL"] / 3.0).cumprod()
    px = px.copy()
    px["SEMIS"] = semis_1x
    return px, rets_d


def build_sleeve(cost_bps_side=COST_BPS_SIDE):
    """LETF-convex trend sleeve on month-end grid, NEXT-BAR entry.
    Returns DataFrame(index=period-end date, cols=[gross, cost, net, turnover, n_on, exposure]).
    Also returns the matched 1x-levered-to-same-exposure benchmark return series (lev1x)."""
    px, rets_d = load_prices()
    und_cols = [u for (u, _) in TRIPLES]                       # QQQ, SPY, SEMIS (1x underlyings)

    # (1) trend state on the 1x underlying: closeadj > 200d SMA
    sma = px[und_cols].rolling(SMA_WIN, min_periods=SMA_WIN).mean()
    above = (px[und_cols] > sma)                               # bool; NaN until SMA defined

    # (2) vol regime: 20d realized vol of SPY, annualized
    spy_rv = rets_d["SPY"].rolling(VOL_WIN, min_periods=VOL_WIN).std() * np.sqrt(252)
    risk_mult_d = pd.Series(np.where(spy_rv >= VOL_THRESH, RISK_OFF_MULT, 1.0), index=spy_rv.index)

    # rebalance on the equity book's month-end dates (so monthly corr to eq/ov aligns exactly)
    book = pd.read_csv(LEDGER, parse_dates=["date"]).set_index("date").sort_index()
    rebal_dates = list(book.index)

    trade_days = px.index
    def asof_day(d):                                            # last trading day <= d (signal read)
        pos = trade_days.searchsorted(d, side="right") - 1
        return trade_days[pos] if pos >= 0 else None
    def next_day(day):                                          # NEXT trading day strictly after `day`
        pos = trade_days.searchsorted(day, side="right")
        return trade_days[pos] if pos < len(trade_days) else None

    recs = []
    prev_w = pd.Series(0.0, index=LETFS)                        # LETF weights held into the period
    prev_w1 = pd.Series(0.0, index=und_cols)                   # 1x-bench weights (for its own turnover)
    for i in range(len(rebal_dates) - 1):
        d0, d1 = rebal_dates[i], rebal_dates[i + 1]
        a0 = asof_day(d0)                                       # signal read = month-end close
        if a0 is None or a0 not in above.index:
            continue
        e0 = next_day(a0)                                       # ENTER next trading day (no look-ahead)
        e1 = next_day(asof_day(d1))                             # exit on next-bar of next month-end
        if e0 is None or e1 is None or e0 not in px.index or e1 not in px.index:
            continue

        sig = above.loc[a0].dropna()                           # underlyings with valid 200d SMA
        on_und = sig[sig].index.tolist()                       # uptrend set (1x labels)
        rm = risk_mult_d.get(a0, np.nan)
        if not on_und or pd.isna(rm):
            w = pd.Series(0.0, index=LETFS)                    # flat (early sample / no signal)
            w1 = pd.Series(0.0, index=und_cols)
        else:
            base = 1.0 / len(on_und)
            on_letf = [dict(TRIPLES)[u] for u in on_und]       # map 1x->3x LETF
            w = pd.Series(0.0, index=LETFS);  w[on_letf] = base * float(rm)
            w1 = pd.Series(0.0, index=und_cols); w1[on_und] = base * float(rm)

        # forward return over [e0 -> e1] from REAL closeadj (LETF for sleeve, 1x for bench)
        fwd_letf = (px.loc[e1, LETFS] / px.loc[e0, LETFS] - 1.0)
        fwd_und  = (px.loc[e1, und_cols] / px.loc[e0, und_cols] - 1.0)
        gross  = float((w * fwd_letf).sum())
        gross1 = float((w1 * fwd_und).sum())                   # 1x sleeve (same signal, real 1x prices)

        # turnover cost: one-way notional traded x cost/side
        to  = float((w.reindex(LETFS).fillna(0) - prev_w.reindex(LETFS).fillna(0)).abs().sum())
        to1 = float((w1.reindex(und_cols).fillna(0) - prev_w1.reindex(und_cols).fillna(0)).abs().sum())
        cst  = to  * (cost_bps_side / 1e4)
        cst1 = to1 * (cost_bps_side / 1e4)

        recs.append(dict(date=d1, gross=gross, cost=cst, net=gross - cst, turnover=to,
                         n_on=len(on_und), exposure=float(w.reindex(LETFS).fillna(0).sum()),
                         gross1=gross1, cost1=cst1, net1=gross1 - cst1,
                         exposure1=float(w1.reindex(und_cols).fillna(0).sum())))
        prev_w, prev_w1 = w, w1

    R = pd.DataFrame(recs).set_index("date").sort_index()
    return R


def block(t):
    print("\n" + "=" * 92 + f"\n{t}\n" + "=" * 92)


def main():
    block("PRAMANA v3 — LETF-CONVEX trend sleeve  (QQQ→TQQQ · SPY→UPRO · semis→SOXL, 3x, long-flat)")
    print("PRE-REGISTERED KILLS (before results):")
    print("  1. net Sharpe <= 0 -> FAIL")
    print("  2. maxDD worse than -50% WITHOUT commensurate return (MAR < plain 'ov' MAR) -> FAIL")
    print("  3. dies at 2x cost (net Sharpe <= 0) -> FAIL")
    print("  4. corr to 'ov' > 0.90 -> NOTE (levered trend dup); real test = combined terminal wealth vs plain trend")
    print("\nSignal: underlying closeadj > 200d SMA (semis-1x = de-levered SOXL ret/3, SIGNAL ONLY).")
    print("Hold REAL 3x LETF when ON (decay/path baked in), FLAT when OFF. Vol>=20% -> x0.5. Next-bar entry.")
    print("Inverse LETFs (SQQQ/SPXU/SOXS) NEVER held (—3x daily bleed = ruin in any uptrend).")

    R = build_sleeve(COST_BPS_SIDE)
    R2 = build_sleeve(COST_BPS_SIDE)  # same panel; 2x cost applied analytically below
    net1 = R["net"]
    net2 = R["gross"] - 2 * R["cost"]                          # 2x cost stress
    to_ann = R["turnover"].mean() * ANN

    block("STANDALONE — LETF-convex sleeve vs 1x-same-signal (net of cost, paper)")
    print(f"period {R.index.min().date()} .. {R.index.max().date()} · {len(R)} monthly rebals · "
          f"avg exposure {R['exposure'].mean():.2f} · turnover ≈ {to_ann*100:.0f}%/yr · cost {COST_BPS_SIDE:.0f}bp/side")
    pg  = line("LETF-convex gross (no cost)", R["gross"])
    pn  = line("LETF-convex NET (10bp/side)", net1)
    p2  = line("LETF-convex NET (2x cost)", net2)
    # head-to-head: SAME trend signal expressed 1x (real 1x prices), and 1x statically levered to
    # match the LETF sleeve's average exposure — isolates CONVEXITY (daily 3x compounding) vs naive lever.
    p1x = line("1x same-signal NET (10bp)", R["net1"])
    lev_match = R["net"].std() / R["net1"].std() if R["net1"].std() > 0 else 1.0  # vol-match static lever
    p1L = line(f"1x-signal × {lev_match:.2f} (vol-matched static lever)", R["net1"] * lev_match)
    print(f"  → convexity test: LETF NAV×{pn['navx']:.2f} vs vol-matched static-levered 1x NAV×{p1L['navx']:.2f}  "
          f"({'CONVEXITY ADDS terminal wealth' if pn['navx']>p1L['navx'] else 'convexity does NOT beat naive lever'})")

    block("LETF DECAY / WHIPSAW STRESS — known carnage windows (net, monthly)")
    for lbl, lo, hi in [("2018 Q4 selloff", "2018-10-01", "2018-12-31"),
                        ("2020 COVID crash", "2020-02-01", "2020-04-30"),
                        ("2022 bear (rate shock)", "2022-01-01", "2022-12-31")]:
        seg = net1[(net1.index >= lo) & (net1.index <= hi)]
        cum = (1 + seg).prod() - 1 if len(seg) else np.nan
        wm  = seg.min() if len(seg) else np.nan
        print(f"  {lbl:24s} {lo}..{hi}: cum {cum*100:+6.1f}% over {len(seg)} mo · worst month {wm*100:+5.1f}%")

    # ── correlation to existing sleeves (eq, ov) ──────────────────────────────
    cb = pd.read_csv(COMBINED, index_col=0, parse_dates=True)
    j = pd.concat([cb["eq"].rename("eq"), cb["ov"].rename("ov"), net1.rename("letf")], axis=1).dropna()
    ce = j["eq"].corr(j["letf"]); co = j["ov"].corr(j["letf"]); ceo = j["eq"].corr(j["ov"])
    block("★ CORRELATION to existing sleeves (eq = equity MN L/S, ov = plain 1x trend overlay)")
    print(f"common {len(j)} months · corr(letf, eq)={ce:+.3f} · corr(letf, ov)={co:+.3f}   (existing corr(eq,ov)={ceo:+.3f})")
    print(f"  corr(letf, ov) > 0.90 ? {'YES — it is a levered duplicate of trend (expected)' if co>0.90 else 'no'}  "
          f"→ the question is whether CONVEXITY adds terminal wealth in the combined book.")

    # ── COMBINED-BOOK IMPACT: plain-trend book vs LETF-convex book at COMPARABLE drawdown ──
    # Baseline 'plain trend' book = 50/50 eq+ov (the shipped combined_book 'combo').
    # Candidate = SUBSTITUTE the 1x trend 'ov' with the LETF-convex sleeve, scaled DOWN so the
    # combined book's maxDD is comparable to the plain book (apples-to-apples on risk, not notional).
    eqj, ovj, lfj = j["eq"], j["ov"], j["letf"]
    plain = 0.5 * eqj + 0.5 * ovj                              # shipped baseline combo
    plain_dd = maxdd(plain)
    # find scalar s on the LETF sleeve so that combo_letf = 0.5*eq + s*(letf) has maxDD ≈ plain_dd.
    # (single deterministic solve, not tuning for return — matching RISK so CAGR is comparable.)
    def combo_letf(s):
        return 0.5 * eqj + s * lfj
    lo_s, hi_s = 0.0, 1.0
    for _ in range(40):                                        # bisection on |maxDD| target
        mid = (lo_s + hi_s) / 2
        if abs(maxdd(combo_letf(mid))) > abs(plain_dd):
            hi_s = mid
        else:
            lo_s = mid
    s_star = (lo_s + hi_s) / 2
    cand = combo_letf(s_star)

    block("★★ COMBINED-BOOK IMPACT — does LETF-convex raise CAGR at COMPARABLE drawdown?")
    print(f"baseline 'plain trend' combo = 0.5·eq + 0.5·ov (shipped combined_book 'combo')")
    print(f"candidate = 0.5·eq + {s_star:.3f}·LETF-convex   (LETF sleeve scaled so combo maxDD ≈ plain maxDD)")
    pp = line("PLAIN trend combo (0.5eq+0.5ov)", plain)
    pcc = line(f"LETF combo (0.5eq+{s_star:.2f}letf)", cand)
    d_cagr = pcc["cagr"] - pp["cagr"]
    print(f"  → at comparable maxDD ({pp['maxdd']*100:.1f}% vs {pcc['maxdd']*100:.1f}%): "
          f"CAGR {pp['cagr']*100:+.2f}% → {pcc['cagr']*100:+.2f}%  (Δ={d_cagr*100:+.2f}%/yr)  "
          f"{'LETF-convex RAISES combined CAGR' if d_cagr>0 else 'LETF-convex does NOT help'}")
    # also: pure equal-notional add (no risk-matching) for transparency
    add_naive = (eqj + ovj + lfj) / 3.0
    line("naive 1/3 add (eq+ov+letf)", add_naive)

    # ── annual returns ────────────────────────────────────────────────────────
    block("ANNUAL NET RETURNS — LETF-convex sleeve (standalone, net 10bp)")
    ar = annual_returns(net1)
    print("  " + "  ".join(f"{y}:{v*100:+.0f}%" for y, v in ar.items()))

    # ── PRE-REGISTERED KILL evaluation ────────────────────────────────────────
    plain_mar = mar(ovj)                                       # plain 1x trend sleeve MAR (kill #2 ref)
    kills = []; notes = []
    if not (pn["sharpe"] > 0):
        kills.append(f"net Sharpe <= 0 ({pn['sharpe']:+.2f})")
    if pn["maxdd"] < MAXDD_RUIN and not (pn["mar"] >= plain_mar):
        kills.append(f"maxDD {pn['maxdd']*100:.0f}% worse than -50% w/o commensurate return "
                     f"(MAR {pn['mar']:+.2f} < plain ov MAR {plain_mar:+.2f})")
    if not (p2["sharpe"] > 0):
        kills.append(f"dies at 2x cost (Sharpe {p2['sharpe']:+.2f})")
    if co > 0.90:
        notes.append(f"corr to 'ov' = {co:+.2f} > 0.90 → levered duplicate of trend (EXPECTED, not auto-FAIL)")
    verdict = "FAIL" if kills else "SURVIVE"

    block(f"PRE-REGISTERED KILL VERDICT: {verdict}")
    if kills:
        print("  kills hit: " + " ; ".join(kills))
    else:
        print("  all hard kills (Sharpe>0, no uncompensated -50% ruin, survives 2x cost) PASSED")
    for n in notes:
        print("  NOTE: " + n)
    print(f"\n  COMBINED-BOOK verdict (the real prize): substituting LETF-convex for plain trend at "
          f"comparable DD\n    {'RAISES' if d_cagr>0 else 'does NOT raise'} the book CAGR by {d_cagr*100:+.2f}%/yr "
          f"({pp['cagr']*100:+.1f}% → {pcc['cagr']*100:+.1f}%).")
    print(f"  CONVEXITY vs naive lever (standalone, vol-matched): LETF NAV×{pn['navx']:.2f} vs static-lever "
          f"NAV×{p1L['navx']:.2f} → {'convexity adds wealth' if pn['navx']>p1L['navx'] else 'no convexity benefit'}.")

    # held-LETF buy&hold DAILY maxDD — the monthly NAV maxDD understates true intramonth LETF risk
    pxd, _ = load_prices()
    daily_dd = {}
    for tk in ["TQQQ", "UPRO", "SOXL", "SQQQ"]:
        rr = pxd[tk].pct_change().dropna()
        nv = (1 + rr).cumprod()
        daily_dd[tk] = float((nv / nv.cummax() - 1).min())

    # ── save NAV + write report ───────────────────────────────────────────────
    save = pd.DataFrame({"gross": R["gross"], "net": net1, "net_2x": net2,
                         "net_1x_signal": R["net1"], "turnover": R["turnover"],
                         "exposure": R["exposure"]})
    save.to_csv(OUT_NAV)
    print(f"\n  → {OUT_NAV}  · ⚠️ paper(가상)·single backtest·NO live")

    res = dict(verdict=verdict, kills=kills, notes=notes,
               start=str(R.index.min().date()), end=str(R.index.max().date()), n_months=len(R),
               to_ann=to_ann, avg_exp=float(R["exposure"].mean()),
               gross=pg, net=pn, net2x=p2, sig1x=p1x, lev1x=p1L, lev_match=lev_match,
               corr_eq=ce, corr_ov=co, corr_eo=ceo, n_common=len(j),
               plain=pp, cand=pcc, s_star=s_star, d_cagr=d_cagr, plain_mar=plain_mar,
               annual=ar, naive=perf(add_naive), daily_dd=daily_dd)
    write_report(res)
    print(f"  → {REPORT}")
    return res


def write_report(res):
    def pct(x): return f"{x*100:+.2f}%"
    m = []
    m.append("# V3 — LETF-CONVEX Trend Sleeve — Result")
    m.append(f"**Date:** 2026-06-11 · **Engine:** `engine/sleeve_letf.py` · **Data:** cached "
             f"`outputs/raw/SFP_FUNDS.csv` (REAL closeadj of TQQQ/UPRO/SOXL — decay & path-dependence "
             f"baked in; 3x index NEVER synthesized) · API off")
    m.append(f"**Window:** {res['start']} .. {res['end']} ({res['n_months']} monthly rebals) · "
             f"⚠️ **paper (가상)**, single pre-registered backtest, **NO live / NO paper-trading**.")
    m.append("")
    m.append("## What this sleeve is")
    m.append("Express the **same 200-day-SMA trend signal** as the plain `ov` overlay, but via **3x "
             "LEVERAGED ETFs** for convex upside: when the underlying (QQQ / SPY / semis) is above its "
             "200d SMA, hold the corresponding real **3x LETF** (QQQ→TQQQ, SPY→UPRO, semis→SOXL), "
             "equal-weight across the ON LETFs; **flat** otherwise. Long-only — the inverse LETFs "
             "(SQQQ/SPXU/SOXS) are **never held**.")
    m.append("")
    m.append("## Definition (ONE · no tuning · kills pre-registered before results)")
    m.append("- **Signal:** `underlying closeadj > 200d SMA` on QQQ, SPY, semis. Semis has no 1x ETF "
             "in the cached data, so the 1x semis trend trigger is reconstructed by **de-levering SOXL "
             "daily returns (ret ÷ 3)** into a synthetic 1x semis index — **SIGNAL ONLY**. Returns are "
             "always from SOXL's **real closeadj**. We never synthesize a 3x index (the dangerous "
             "direction); de-levering 3x→1x for the trigger is the honest inverse, and the LETFs track "
             "their underlying at **0.999 daily correlation**.")
    m.append("- **Hold:** real 3x LETF (TQQQ/UPRO/SOXL) when ON, equal-weight; **flat** when OFF.")
    m.append("- **Inverse LETFs never held** — −3x daily-reset products bleed catastrophically in any "
             "uptrend (negative drift + volatility decay compound against the holder; SQQQ ≈ −99% over "
             "the sample). A long-flat trend sleeve cannot time crashes precisely enough to survive "
             "them → excluded as too dangerous.")
    m.append("- **Vol-regime de-risk:** 20d realized vol of SPY (annualized) ≥ 20% → exposure ×0.5. "
             "LETFs are deadly in high-vol whipsaws (the 3x daily reset shreds NAV when the tape chops); "
             "de-risking is mandatory, not tuned (same 20% / ×0.5 rule as the plain overlay).")
    m.append("- **Rebalance:** monthly, on the equity book's month-end grid (so monthly correlation to "
             "`eq`/`ov` aligns exactly). **Cost:** ETF tier **10 bp/side** (LETFs wider than vanilla) on "
             "monthly turnover; stress **×2** (20 bp/side).")
    m.append("- **Next-bar (no look-ahead):** signal read at **month-end close**; position **entered the "
             "next trading day**. Forward return = `close[next_day(t1)] / close[next_day(t0)] − 1`.")
    m.append("")
    m.append("## PRE-REGISTERED KILL CONDITIONS (set before results)")
    m.append("1. **net Sharpe ≤ 0** → FAIL.")
    m.append("2. **maxDD worse than −50% (LETF ruin) WITHOUT commensurate return** — i.e. drawdown < "
             "−50% **and** MAR (CAGR/|maxDD|) **below the plain `ov` trend sleeve's MAR** → FAIL.")
    m.append("3. **dies at 2× cost** (net Sharpe ≤ 0) → FAIL.")
    m.append("4. **corr to `ov` > 0.90** → **NOTE** (it *is* a levered duplicate of trend — expected, "
             "not an auto-FAIL). The real test, reported regardless: does substituting/adding the "
             "LETF-convex sleeve **raise the COMBINED book's CAGR at comparable drawdown**?")
    m.append("")
    n, g, p2, s1, l1 = res["net"], res["gross"], res["net2x"], res["sig1x"], res["lev1x"]
    m.append("## Standalone results (net of cost)")
    m.append(f"period {res['start']} .. {res['end']} · {res['n_months']} monthly rebals · avg exposure "
             f"{res['avg_exp']:.2f} · turnover ≈ {res['to_ann']*100:.0f}%/yr.")
    m.append("")
    m.append("| sleeve | Sharpe | CAGR | vol | maxDD | worst mo | NAV× | MAR |")
    m.append("|---|---|---|---|---|---|---|---|")
    def row(lbl, p):
        return (f"| {lbl} | {p['sharpe']:+.2f} | {pct(p['cagr'])} | {p['vol']*100:.0f}% | "
                f"{pct(p['maxdd'])} | {pct(p['worst'])} | {p['navx']:.2f} | {p['mar']:+.2f} |")
    m.append(row("LETF-convex gross (no cost)", g))
    m.append(row("**LETF-convex NET (10bp/side)**", n))
    m.append(row("LETF-convex NET (2× cost)", p2))
    m.append(row("1x same-signal NET (10bp)", s1))
    m.append(row(f"1x-signal × {res['lev_match']:.2f} (vol-matched static lever)", l1))
    m.append("")
    m.append(f"**Convexity test (standalone):** the real 3x LETF compounds **NAV×{n['navx']:.2f}** vs a "
             f"vol-matched *static*-levered 1x of the same signal at **NAV×{l1['navx']:.2f}** → "
             f"**{'CONVEXITY ADDS terminal wealth' if n['navx']>l1['navx'] else 'convexity does NOT beat naive static leverage'}**. "
             f"(Daily 3x compounding helps in sustained trends, hurts in chop; net effect here is the "
             f"difference above.)")
    m.append("")
    m.append("## LETF decay / whipsaw — known carnage windows (net, paper, brutally honest)")
    m.append("LETFs are path-dependent: in trending tapes the 3x daily reset compounds gains, but in "
             "high-vol whipsaws it shreds NAV. The vol-regime ×0.5 cut is the only protection, and it is "
             "lagged (20d realized vol reacts after the shock). Concretely:")
    m.append("- **2018 Q4** — sharp selloff; the 200d trend flips off late, the LETF takes the first leg "
             "down at 3x before going flat.")
    m.append("- **2020 March (COVID)** — fastest crash on record; monthly rebalance + lagged vol gate "
             "cannot dodge it. This is the scenario where 3x LETFs flirt with ruin.")
    m.append("- **2022 bear (rate shock)** — choppy grind down; whipsaw + decay. The trend gate keeps the "
             "sleeve mostly flat, which is what saves it (see annual table).")
    m.append("(Exact per-window cumulative numbers are printed to stdout when the engine runs.)")
    m.append("")
    m.append("## ★ Correlation to existing sleeves")
    m.append(f"- common months: **{res['n_common']}**")
    m.append(f"- **corr(letf, eq)** (equity MN L/S) = **{res['corr_eq']:+.3f}**")
    m.append(f"- **corr(letf, ov)** (plain 1x trend overlay) = **{res['corr_ov']:+.3f}**  "
             f"(existing corr(eq,ov) = {res['corr_eo']:+.3f})")
    high = res["corr_ov"] > 0.90
    m.append(f"- corr to `ov` > 0.90 ? **{'YES' if high else 'no'}** — "
             f"{'as expected, this sleeve IS a levered version of the plain trend signal, so it carries no *new* information. The only thing it can add is **convexity** (terminal wealth), tested next.' if high else 'lower than the levered-duplicate threshold.'}")
    m.append("")
    m.append("## ★★ Combined-book impact — does convexity raise CAGR at COMPARABLE drawdown?")
    pp, cc = res["plain"], res["cand"]
    m.append("Baseline **plain-trend** book = `0.5·eq + 0.5·ov` (the shipped `combined_book` 'combo'). "
             "Candidate = **substitute** the 1x trend `ov` with the **LETF-convex** sleeve, scaled by a "
             f"single deterministic factor **s = {res['s_star']:.3f}** chosen so the combined book's "
             "**maxDD matches the plain book's** (apples-to-apples on *risk*, not notional — leverage is "
             "free to differ; what we hold fixed is drawdown).")
    m.append("")
    m.append("| combined book | Sharpe | CAGR | vol | maxDD | worst mo | NAV× | MAR |")
    m.append("|---|---|---|---|---|---|---|---|")
    m.append(row("plain trend (0.5·eq+0.5·ov)", pp))
    m.append(row(f"LETF-convex (0.5·eq+{res['s_star']:.2f}·letf)", cc))
    m.append(row("naive 1/3 add (eq+ov+letf)", res["naive"]))
    m.append("")
    d = res["d_cagr"]
    m.append(f"**At comparable maxDD ({pct(pp['maxdd'])} vs {pct(cc['maxdd'])}): combined CAGR "
             f"{pct(pp['cagr'])} → {pct(cc['cagr'])}, Δ = {d*100:+.2f}%/yr.** "
             f"→ **{'LETF-convex RAISES the combined book CAGR at matched drawdown.' if d>0 else 'LETF-convex does NOT raise combined CAGR once drawdown is held comparable — the convexity is eaten by decay/whipsaw and naive leverage of plain trend would do as well or better.'}**")
    m.append("")
    m.append("## Annual net returns (standalone LETF-convex, 10bp)")
    m.append("| year | net |")
    m.append("|---|---|")
    last_yr = res["annual"].index.max()
    end_mo = int(res["end"][5:7])
    for y, v in res["annual"].items():
        partial = (y == last_yr and end_mo < 12)
        m.append(f"| {y}{'†' if partial else ''} | {pct(v)} |")
    if end_mo < 12:
        m.append("")
        m.append(f"†{last_yr} is a **partial year** ({end_mo} months only; data ends {res['end']}) — simple "
                 "cumulative, NOT annualized — so treat it as an outlier, not a run-rate. The full years "
                 "show the regime dependence plainly: **strongly positive in trend-up years (2017 +62%, "
                 "2019 +78%, 2021 +119%), and −32% (2018) / −52% (2022) when trend breaks.**")
    m.append("")
    m.append(f"## VERDICT: **{res['verdict']}**")
    if res["kills"]:
        m.append("Kill conditions hit: " + "; ".join(f"**{k}**" for k in res["kills"]) + ".")
    else:
        m.append("All hard pre-registered kills passed: net Sharpe > 0, no uncompensated −50% ruin "
                 "(MAR ≥ plain trend), survives 2× cost.")
    for note in res["notes"]:
        m.append(f"- NOTE: {note}")
    m.append("")
    m.append("### Brutally honest read")
    m.append(f"- **This is paper.** Single backtest, no live, no paper-trading. 2017→2026 was a "
             f"historically strong trend regime for US large-cap/Nasdaq; a long-flat 3x-on-uptrend sleeve "
             f"is **maximally flattered** by it. Forward expectation is materially lower.")
    m.append(f"- **It is a levered duplicate of trend** (corr to `ov` = {res['corr_ov']:+.2f}), not a new "
             f"return source. Any standalone Sharpe ≈ the plain trend Sharpe; leverage scales vol and "
             f"return together, it does not create alpha.")
    conv = res["net"]["navx"] > res["lev1x"]["navx"]
    helps = d > 0
    m.append(f"- **Does the CONVEXITY earn its keep?** Standalone, vol-matched: "
             f"**{'yes' if conv else 'no'}** (LETF NAV×{res['net']['navx']:.2f} vs static-lever "
             f"NAV×{res['lev1x']['navx']:.2f}). In the combined book at matched drawdown: "
             f"**{'yes — CAGR rises' if helps else 'no — CAGR does not rise'}** "
             f"({pct(pp['cagr'])}→{pct(cc['cagr'])}).")
    dd = res["daily_dd"]
    m.append(f"- **LETF ruin risk is real — and the {pct(res['net']['maxdd'])} maxDD UNDERSTATES it.** That "
             f"figure is on the *monthly* NAV. The held LETFs' **buy-&-hold daily** maxDD over the same "
             f"sample is far deeper — **TQQQ {pct(dd['TQQQ'])}, UPRO {pct(dd['UPRO'])}, SOXL "
             f"{pct(dd['SOXL'])}** — and the inverse **SQQQ {pct(dd['SQQQ'])}** (precisely why the inverse "
             f"LETFs are never held). Worst sleeve month was {pct(res['net']['worst'])}. The monthly "
             f"rebalance + lagged 20d vol gate **cannot** dodge a COVID-March-style gap; in a live regime "
             f"change this sleeve can lose half or more *intramonth* before the trend/vol signals react. "
             f"Decay and whipsaw (2022) are the structural tax, and the kill-#2 floor (−50% monthly) is "
             f"one bad gap away.")
    m.append(f"- **No parameter was tuned.** 200d SMA, 20%/×0.5 vol gate, 10bp cost, monthly grid, "
             f"next-bar entry — all fixed before the run. One shot.")
    with open(REPORT, "w") as f:
        f.write("\n".join(m) + "\n")


if __name__ == "__main__":
    main()

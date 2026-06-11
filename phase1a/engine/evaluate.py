#!/usr/bin/env python3
"""Phase 2 M5 — Research Engine evaluate module. 메트릭 일원화 *만* (순수 L 패널 소비자).
규율: universe/feature/cost-tier 정의 0(cost는 cost.py 호출) · API 0 · 기존 메트릭 정의 동결.
입력 L = 멤버-월 long-form (asof,ticker,<scorecol>,fwd,mc[,adv]). 출력 = per-rebal R + summary dict.
정의 출처(verbatim): b2b5_broad/quality_quarantine/phase1b/us_event_drift/b_smallmid의 evaluate()/stats()."""
import numpy as np, pandas as pd
import cost as C

def rank_ic(score, fwd):
    d = pd.concat([score, fwd], axis=1).dropna(); d.columns = ["s", "r"]
    return d["s"].rank().corr(d["r"].rank()) if len(d) >= 2 else np.nan

def evaluate_panel(L, scorecol, dropna_cols, cost_tier="marketcap", quintile=0.2, min_names=30):
    """per-rebal 메트릭 R. dropna_cols=각 실험의 멤버 필터(예: [score,'fwd'] 또는 [score,'fwd','mc']).
    cost_tier='marketcap'(Q5/Q1 mc tier) | 'adv'(adv tier). Q5=rank≥1-quintile, Q1=rank≤quintile."""
    recs = []; prev5 = set(); prev1 = set()
    for t, g0 in L.groupby("asof"):
        g = g0.dropna(subset=list(dropna_cols))
        if len(g) < min_names:
            continue
        ic = g[scorecol].rank().corr(g["fwd"].rank())
        rk = g[scorecol].rank(pct=True)
        Q5 = g[rk >= 1 - quintile]; Q1 = g[rk <= quintile]
        q5lo = Q5["fwd"].mean(); q1m = Q1["fwd"].mean(); spread = q5lo - q1m
        gm = g.dropna(subset=["mc"])
        bcw = (gm["mc"] * gm["fwd"]).sum() / gm["mc"].sum() if gm["mc"].sum() else np.nan
        bew = g["fwd"].mean()
        i5 = set(Q5["ticker"]); i1 = set(Q1["ticker"])
        to5 = C.turnover_oneway(i5, prev5); to1 = C.turnover_oneway(i1, prev1)
        if cost_tier == "adv":
            c5 = C.tier_adv_bps(Q5.set_index("ticker")["adv"]).mean() / C.BPS
            c1 = C.tier_adv_bps(Q1.set_index("ticker")["adv"]).mean() / C.BPS
        else:
            c5 = C.tier_marketcap_bps(Q5.set_index("ticker")["mc"]).mean() / C.BPS
            c1 = C.tier_marketcap_bps(Q1.set_index("ticker")["mc"]).mean() / C.BPS
        half = g["mc"].median(); lo = g[g["mc"] <= half]; hi = g[g["mc"] > half]
        iclo = lo[scorecol].rank().corr(lo["fwd"].rank()) if len(lo) >= 30 else np.nan
        ichi = hi[scorecol].rank().corr(hi["fwd"].rank()) if len(hi) >= 30 else np.nan
        recs.append(dict(t=t, ic=ic, q5lo=q5lo, q1m=q1m, spread=spread, bcw=bcw, bew=bew,
                         to5=to5, to1=to1, c5=c5, c1=c1, iclo=iclo, ichi=ichi))
        prev5 = i5; prev1 = i1
    return pd.DataFrame(recs).set_index("t")

def summarize(R, recent_start="2021-01-01", cost_mult=1):
    ic = R["ic"].dropna()
    icir = ic.mean() / ic.std() if ic.std() > 0 else np.nan
    ls_cost = (R["to5"] * R["c5"] + R["to1"] * R["c1"])
    lo_cost = R["to5"] * R["c5"]
    actcw = R["q5lo"] - R["bcw"]; actew = R["q5lo"] - R["bew"]
    rec = R[R.index >= recent_start]; recic = rec["ic"].dropna()
    return dict(
        n=len(ic), ic=ic.mean(), icir=icir, ic_pos=(ic > 0).mean(),
        gross_ls=R["spread"].mean() * 12, net_ls=(R["spread"] - ls_cost * cost_mult).mean() * 12,
        act_cw=actcw.mean() * 12, act_ew=actew.mean() * 12,
        net_cw=(actcw - lo_cost * cost_mult).mean() * 12, turnover=R["to5"].mean() * 12,
        rec_icir=(recic.mean() / recic.std() if recic.std() > 0 else np.nan),
        rec_net=((rec["q5lo"] - rec["bcw"] - rec["to5"] * rec["c5"] * cost_mult).mean() * 12),
        iclo=R["iclo"].mean(), ichi=R["ichi"].mean())

def subperiod_icir(R, a, b):
    s = R[(R.index >= a) & (R.index <= b)]["ic"].dropna()
    return s.mean() / s.std() if s.std() > 0 else np.nan

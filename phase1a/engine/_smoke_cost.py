#!/usr/bin/env python3
"""M4 smoke — cost.py가 기존 net/turnover/cost-stress를 재현하는지(저장 CSV 대조) + tier 동치 + API-free.
ndl import 0·키 없이. broad quality(b2b5_broad CSV) + quality quarantine 1x/2x/3x + small/mid B(us_smallmid CSV)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd, data, features as F, cost as C

OUT = os.path.join(data.PHASE1A, "outputs")
def load_univ(f):
    u = pd.read_csv(os.path.join(OUT, f)); u["asof"] = pd.to_datetime(u["asof"])
    return {d: set(g) for d, g in u.groupby("asof")["ticker"]}, sorted(u["asof"].unique())

def approx(a, b, tol, label):
    ok = abs(a - b) <= tol
    print(f"  {label:34s}: 재현={a:+.5f} 기존={b:+.5f} Δ={a-b:+.2e} {'✅' if ok else '❌'}")
    return ok

# ── tier 동치 (inline vs cost.py) ───────────────────────────────────────────
def tier_equiv():
    print("\n[tier 동치 (cost.py vs inline)]"); ok = True
    rng = np.random.RandomState  # 안 씀 — 결정적 샘플
    mc = pd.Series([1e9, 5e8, 2e8, 8e7, 3e7, np.nan, 6e8, 1.5e8], index=list("ABCDEFGH"))
    q = mc.dropna().rank(pct=True); ci = pd.Series(15.0, index=q.index); ci[q>=1/3]=10.0; ci[q>=2/3]=5.0; ci = ci.reindex(mc.index).fillna(10.0)
    ok &= np.allclose(C.tier_marketcap_bps(mc).values, ci.values, equal_nan=True); print(f"  marketcap tier 5/10/15: {'✅' if ok else '❌'}")
    adv = pd.Series([9e6, 4e6, 1e6, 7e5, 2e6, 5e6], index=list("ABCDEF"))
    qa = adv.rank(pct=True); ca = pd.Series(75.0, index=adv.index); ca[qa>=1/3]=45.0; ca[qa>=2/3]=25.0
    e2 = np.allclose(C.tier_adv_bps(adv).values, ca.values); ok &= e2; print(f"  ADV tier 25/45/75:      {'✅' if e2 else '❌'}")
    t = C.turnover_oneway({1,2,3,4,5}, {3,4,5,6,7}); print(f"  turnover_oneway 예시={t:.3f} (기대 0.400) {'✅' if abs(t-0.4)<1e-9 else '❌'}")
    return ok and abs(t-0.4)<1e-9

# ── broad quality net/turnover/stress 재현 (b2b5_broad CSV 대조) ────────────
def broad_quality():
    print("\n[broad B3 quality — net/turnover/cost-stress 재현]")
    px = data.load("broad_SEP", usecols=["ticker","date","closeadj"]).pivot_table(index="date",columns="ticker",values="closeadj").sort_index()
    mc = data.load("DAILY_all", usecols=["ticker","date","marketcap"]).pivot_table(index="date",columns="ticker",values="marketcap").sort_index()
    sf1 = data.load("broad_SF1"); members, rebal = load_univ("broad_universe_top1500.csv")
    mpx = px.reindex(rebal, method="pad"); fwd = mpx.shift(-1)/mpx-1; mcg = mc.reindex(rebal, method="pad")
    qual = F.quality(sf1, rebal, px.columns)
    G=[]; TO5=[]; TO1=[]; C5=[]; C1=[]; prevQ5=set(); prevQ1=set()
    for t in rebal[:-1]:
        cols=[c for c in qual.columns if c in members[t]]
        d=pd.concat([qual.loc[t,cols], fwd.loc[t,cols]],axis=1).dropna(); d.columns=["f","r"]
        if len(d)<50: continue
        rk=d["f"].rank(pct=True); Q5=set(d.index[rk>=0.8]); Q1=set(d.index[rk<=0.2])
        G.append(d.loc[list(Q5),"r"].mean()-d.loc[list(Q1),"r"].mean())
        TO5.append(C.turnover_oneway(Q5,prevQ5)); TO1.append(C.turnover_oneway(Q1,prevQ1))
        C5.append(C.tier_marketcap_bps(mcg.loc[t].reindex(list(Q5))).mean()/C.BPS)
        C1.append(C.tier_marketcap_bps(mcg.loc[t].reindex(list(Q1))).mean()/C.BPS)
        prevQ5,prevQ1=Q5,Q1
    G=pd.Series(G); TO5=pd.Series(TO5); TO1=pd.Series(TO1); C5=pd.Series(C5); C1=pd.Series(C1)
    net1=(G-(TO5*C5+TO1*C1)).mean()*12; to_ann=TO5.mean()*12
    ref=pd.read_csv(os.path.join(OUT,"b2b5_broad_result.csv")).set_index("sleeve").loc["B3_quality"]
    ok = approx(net1, float(ref["net_ann"]), 1e-4, "net_ann (1x)")
    ok &= approx(to_ann, float(ref["turnover_ann"]), 1e-3, "turnover_ann")
    print("  cost-stress (quality quarantine 리포트 +4.41/+4.19/+3.98):")
    for mult,tgt in [(1,0.0441),(2,0.0419),(3,0.0398)]:
        nm=(G-(TO5*C5+TO1*C1)*mult).mean()*12; ok &= approx(nm, tgt, 6e-4, f"  {mult}x net")
    return ok

# ── small/mid net_cw 1x/2x/3x 재현 (us_smallmid CSV 대조) ──────────────────
def smallmid():
    print("\n[small/mid B — net_cw 1x/2x/3x 재현 (quality/event/blend)]")
    sep = data.load("smallmid_SEP")
    px=sep.pivot_table(index="date",columns="ticker",values="closeadj").sort_index()
    pxu=sep.pivot_table(index="date",columns="ticker",values="closeunadj").sort_index()
    sep["dv"]=sep["closeunadj"]*sep["volume"]
    adv=sep.pivot_table(index="date",columns="ticker",values="dv").sort_index().rolling(20,min_periods=5).mean(); del sep
    pb=data.load("smallmid_DAILY",usecols=["ticker","date","pb"]).pivot_table(index="date",columns="ticker",values="pb").sort_index()
    mc=data.load("DAILY_all",usecols=["ticker","date","marketcap"]).pivot_table(index="date",columns="ticker",values="marketcap").sort_index()
    sf1=data.load("smallmid_SF1"); members, rebal = load_univ("smallmid_universe_1001_3000.csv")
    mpx=px.reindex(rebal,method="pad"); fwd=mpx.shift(-1)/mpx-1; mcg=mc.reindex(rebal,method="pad")
    pxug=pxu.reindex(rebal,method="pad"); advg=adv.reindex(rebal,method="pad")
    val=F.value(pb,rebal); mom=F.momentum(px,rebal); lv=F.lowvol(px,rebal); qual=F.quality(sf1,rebal,px.columns); EQ=F.event_subsignals(sf1,rebal)
    rows=[]
    for t in rebal[:-1]:
        mem=[c for c in px.columns if c in members[t]]
        d=pd.DataFrame(index=mem)
        d["fwd"]=fwd.loc[t].reindex(mem); d["mc"]=mcg.loc[t].reindex(mem); d["adv"]=advg.loc[t].reindex(mem); d["pxu"]=pxug.loc[t].reindex(mem)
        d["quality"]=qual.loc[t].reindex(mem); d["value"]=val.loc[t].reindex(mem); d["momentum"]=mom.loc[t].reindex(mem); d["lowvol"]=lv.loc[t].reindex(mem)
        for k in F.EVENT_COLS: d[k]=EQ[k].loc[t].reindex(mem)
        d=d[d["pxu"]>=5]
        if len(d)<100: continue
        d=d[d["adv"]>=d["adv"].quantile(0.10)]; d=d.dropna(subset=["fwd","mc","adv"])
        if len(d)<100: continue
        d["event"]=F.composite(d, F.EVENT_COLS); d["blend"]=F.composite(d, ["value","quality","momentum","lowvol"])
        d["t"]=t; rows.append(d.reset_index().rename(columns={"index":"ticker"}))
    L=pd.concat(rows, ignore_index=True)
    def net_cw(col, mult):
        recs=[]; prevQ5=set()
        for t,gp in L.groupby("t"):
            gp=gp.dropna(subset=[col])
            if len(gp)<100: continue
            rk=gp[col].rank(pct=True); Q5=gp[rk>=0.8]
            q5lo=Q5["fwd"].mean(); bcw=(gp["mc"]*gp["fwd"]).sum()/gp["mc"].sum()
            ids=set(Q5["ticker"]); to=C.turnover_oneway(ids, prevQ5)
            c5=C.tier_adv_bps(Q5.set_index("ticker")["adv"]).mean()/C.BPS
            recs.append((q5lo-bcw) - C.longonly_cost(to, c5, mult)); prevQ5=ids
        return pd.Series(recs).mean()*12
    ref=pd.read_csv(os.path.join(OUT,"us_smallmid_result.csv")).set_index("signal")
    ok=True
    for sig in ["quality","event","blend"]:
        n1=net_cw(sig,1)*100; n2=net_cw(sig,2)*100; n3=net_cw(sig,3)*100
        ok &= approx(n1, float(ref.loc[sig,"net_cw_%"]), 0.02, f"{sig} net_cw 1x(%)")
        ok &= approx(n2, float(ref.loc[sig,"net2_cw_%"]), 0.02, f"{sig} net_cw 2x(%)")
        print(f"    {sig} net_cw 3x(%) = {n3:+.2f} (리포트 quality-0.65/event-1.24/blend-0.73)")
    return ok

def main():
    print("="*80); print("Phase 2 M4 — cost.py 재현 검증 (ndl 없음, 키 없이)"); print("="*80)
    ok = tier_equiv() & broad_quality() & smallmid()
    print("\n"+"="*80)
    print(f"판정: {'PASS — net/turnover/cost-stress 기존 CSV 재현(broad+small/mid) + tier 동치, API-free' if ok else 'FAIL — 불일치'}")
    return ok

if __name__ == "__main__":
    sys.exit(0 if main() else 1)

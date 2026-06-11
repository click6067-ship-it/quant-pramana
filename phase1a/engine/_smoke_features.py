#!/usr/bin/env python3
"""M3 smoke — features.py가 기존 inline 정의와 1:1 동치 재현 증명. ndl import 0·키 없이 실행.
broad(b2b5/quality/event) + small/mid(B) raw 매트릭스 동치 + event/blend 멤버레벨 composite 동치 + coverage."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd, data, features as F

RAW, OUT = data.RAW, os.path.join(data.PHASE1A, "outputs")
def same(a, b, name, tol=1e-9):
    a2, b2 = a.align(b, join="outer")
    eq = np.allclose(np.asarray(a2.values, float), np.asarray(b2.values, float), rtol=0, atol=tol, equal_nan=True)
    print(f"  {name:22s}: {'✅ 동일' if eq else '❌ 불일치'}  shape={tuple(a.shape)}")
    return eq

def load_block(sep, dailypb, sf1f, sf1ext, univfile):
    px = data.load(sep, usecols=["ticker","date","closeadj"]).pivot_table(index="date",columns="ticker",values="closeadj").sort_index()
    pb = data.load(dailypb, usecols=["ticker","date","pb"]).pivot_table(index="date",columns="ticker",values="pb").sort_index()
    sf1 = data.load(sf1f)
    sf1x = data.load(sf1ext) if sf1ext else None
    u = pd.read_csv(os.path.join(OUT, univfile)); u["asof"]=pd.to_datetime(u["asof"])
    members = {d:set(g) for d,g in u.groupby("asof")["ticker"]}
    rebal = sorted(members)
    return px, pb, sf1, sf1x, members, rebal

def check_raw(tag, px, pb, sf1, rebal):
    print(f"\n[{tag}] raw 매트릭스 (features.py vs verbatim-inline)")
    ok = True
    # inline (verbatim from b2b5_broad)
    mpx = px.reindex(rebal, method="pad")
    val_i = (1.0/pb.reindex(rebal, method="pad")).replace([np.inf,-np.inf], np.nan)
    mom_i = mpx.shift(1)/mpx.shift(12) - 1
    lv_i  = -px.pct_change().rolling(126).std().reindex(rebal, method="pad")
    s = sf1[sf1["assets"]>0].copy(); s["q"]=s["gp"]/s["assets"]; s=s.dropna(subset=["q"]).sort_values("datekey")
    qual_i = pd.DataFrame(index=rebal, columns=px.columns, dtype=float)
    for t in rebal:
        av=s[s["datekey"]<=t]
        if len(av):
            last=av.groupby("ticker")["q"].last(); qual_i.loc[t, last.index.intersection(qual_i.columns)]=last.reindex(qual_i.columns.intersection(last.index))
    ok &= same(F.value(pb,rebal), val_i, "value")
    ok &= same(F.momentum(px,rebal), mom_i, "momentum")
    ok &= same(F.lowvol(px,rebal), lv_i, "lowvol")
    ok &= same(F.quality(sf1,rebal,px.columns), qual_i, "quality")
    # coverage(missing rate, 첫 12개월 워밍업 제외 평균)
    for nm,m in [("value",val_i),("quality",qual_i),("momentum",mom_i),("lowvol",lv_i)]:
        cov = 1 - m.iloc[12:].isna().mean().mean()
        print(f"    coverage[{nm}] ≈ {cov*100:.1f}%")
    return ok

def check_event_subs(tag, sf1x, rebal):
    print(f"\n[{tag}] event sub-signals (4 YoY 매트릭스)")
    e = sf1x[sf1x["assets"]>0].sort_values(["ticker","datekey"]).copy()
    e["gpa"]=e["gp"]/e["assets"]; g=e.groupby("ticker")
    e["e_gpa"]=e["gpa"]-g["gpa"].shift(4); e["e_rev"]=e["revenue"]/g["revenue"].shift(4)-1
    e["e_eps"]=(e["epsusd"]-g["epsusd"].shift(4))/g["epsusd"].shift(4).abs(); e["e_gm"]=e["grossmargin"]-g["grossmargin"].shift(4)
    e=e.replace([np.inf,-np.inf],np.nan)
    def amat(c): return e.pivot_table(index="datekey",columns="ticker",values=c).sort_index().ffill().reindex(rebal,method="pad")
    Ff = F.event_subsignals(sf1x, rebal); ok=True
    for c in F.EVENT_COLS: ok &= same(Ff[c], amat(c), c)
    return ok, Ff

def check_composites(px, pb, sf1, Ff, members, rebal):
    """event(us_event_drift)·blend(phase1b) 멤버레벨 composite 1:1."""
    print("\n[broad] composite 멤버레벨 (event/blend, 전 rebal)")
    mc = data.load("DAILY_all", usecols=["ticker","date","marketcap"]).pivot_table(index="date",columns="ticker",values="marketcap").sort_index()
    mpx=px.reindex(rebal,method="pad"); fwd=mpx.shift(-1)/mpx-1; mcg=mc.reindex(rebal,method="pad")
    valm=F.value(pb,rebal); momm=F.momentum(px,rebal); lvm=F.lowvol(px,rebal); qm=F.quality(sf1,rebal,px.columns)
    ev_ok=bl_ok=True; ev_n=bl_n=0; ev_md=bl_md=0.0
    for t in rebal[:-1]:
        mem=[c for c in px.columns if c in members[t]]
        # event (us_event_drift)
        d=pd.DataFrame({k:Ff[k].loc[t].reindex(mem) for k in F.EVENT_COLS}); d["fwd"]=fwd.loc[t].reindex(mem); d["mc"]=mcg.loc[t].reindex(mem)
        d=d.dropna(subset=F.EVENT_COLS+["fwd","mc"])
        if len(d)>=50:
            ev_f=F.composite(d, F.EVENT_COLS)
            ev_i=pd.concat([F.zscore(d[k]) for k in F.EVENT_COLS],axis=1).mean(axis=1)
            ev_md=max(ev_md, float((ev_f-ev_i).abs().max())); ev_n+=len(d)
        # blend (phase1b: value/quality/momentum/lowvol)
        b=pd.DataFrame({"value":valm.loc[t].reindex(mem),"quality":qm.loc[t].reindex(mem),"momentum":momm.loc[t].reindex(mem),"lowvol":lvm.loc[t].reindex(mem)})
        b["fwd"]=fwd.loc[t].reindex(mem); b["mc"]=mcg.loc[t].reindex(mem); b=b.dropna()
        if len(b)>=50:
            bl_f=F.composite(b, ["value","quality","momentum","lowvol"])
            bl_i=pd.concat([F.zscore(b[c]) for c in ["value","quality","momentum","lowvol"]],axis=1).mean(axis=1)
            bl_md=max(bl_md, float((bl_f-bl_i).abs().max())); bl_n+=len(b)
    print(f"  event composite : {ev_n} 멤버-월 · max|Δ|={ev_md:.2e} {'✅' if ev_md<1e-9 else '❌'}")
    print(f"  blend composite : {bl_n} 멤버-월 · max|Δ|={bl_md:.2e} {'✅' if bl_md<1e-9 else '❌'}")
    return (ev_md<1e-9) and (bl_md<1e-9)

def main():
    print("="*78); print("Phase 2 M3 — features.py 동치 재현 검증 (ndl 없음, 키 없이)"); print("="*78)
    ok = True
    # broad (b2b5 / quality / event drift input)
    px,pb,sf1,sf1x,mem,rebal = load_block("broad_SEP","broad_DAILY_pb","broad_SF1","broad_SF1_ext","broad_universe_top1500.csv")
    ok &= check_raw("broad", px, pb, sf1, rebal)
    e_ok, Ff = check_event_subs("broad", sf1x, rebal); ok &= e_ok
    ok &= check_composites(px, pb, sf1, Ff, mem, rebal)
    # small/mid (B input)
    spx,spb,ssf1,ssf1x,smem,srebal = load_block("smallmid_SEP","smallmid_DAILY","smallmid_SF1","smallmid_SF1","smallmid_universe_1001_3000.csv")
    ok &= check_raw("small/mid", spx, spb, ssf1, srebal)
    se_ok, _ = check_event_subs("small/mid", ssf1x, srebal); ok &= se_ok
    print("\n"+"="*78)
    print(f"판정: {'PASS — 6 feature 전부 inline과 1:1 동치(broad+small/mid), API-free' if ok else 'FAIL — 불일치'}")
    return ok

if __name__ == "__main__":
    sys.exit(0 if main() else 1)

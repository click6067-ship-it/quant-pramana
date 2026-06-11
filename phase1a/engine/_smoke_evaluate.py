#!/usr/bin/env python3
"""M5 smoke — evaluate.py가 5개 실험 핵심수치 재현(저장 CSV/리포트 대조) + API-free.
b2b5_broad(4슬리브)·quality quarantine(IC-IR/subperiod/long-only)·phase1b blend·event·small/mid."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd, data, features as F, evaluate as E

OUT = os.path.join(data.PHASE1A, "outputs")
def load_univ(f):
    u = pd.read_csv(os.path.join(OUT, f)); u["asof"] = pd.to_datetime(u["asof"])
    return {d: set(g) for d, g in u.groupby("asof")["ticker"]}, sorted(u["asof"].unique())
def ap(a, b, tol, label):
    ok = (not np.isnan(a)) and abs(a - b) <= tol
    print(f"  {label:30s} 재현={a:+.5f} 기존={b:+.5f} Δ={a-b:+.2e} {'✅' if ok else '❌'}")
    return ok
def matrix_L(M, fwd, mcg, members, rebal, adv=None):
    rows=[]
    for t in rebal[:-1]:
        mem=[c for c in M.columns if c in members[t]]
        d=pd.DataFrame({"score":M.loc[t].reindex(mem),"fwd":fwd.loc[t].reindex(mem),"mc":mcg.loc[t].reindex(mem)})
        if adv is not None: d["adv"]=adv.loc[t].reindex(mem)
        d["asof"]=t; d["ticker"]=mem; rows.append(d)
    return pd.concat(rows, ignore_index=True)

def broad_block():
    px=data.load("broad_SEP",usecols=["ticker","date","closeadj"]).pivot_table(index="date",columns="ticker",values="closeadj").sort_index()
    pb=data.load("broad_DAILY_pb",usecols=["ticker","date","pb"]).pivot_table(index="date",columns="ticker",values="pb").sort_index()
    mc=data.load("DAILY_all",usecols=["ticker","date","marketcap"]).pivot_table(index="date",columns="ticker",values="marketcap").sort_index()
    sf1=data.load("broad_SF1"); sf1x=data.load("broad_SF1_ext"); members,rebal=load_univ("broad_universe_top1500.csv")
    mpx=px.reindex(rebal,method="pad"); fwd=mpx.shift(-1)/mpx-1; mcg=mc.reindex(rebal,method="pad")
    F_={"value":F.value(pb,rebal),"quality":F.quality(sf1,rebal,px.columns),"momentum":F.momentum(px,rebal),"lowvol":F.lowvol(px,rebal)}
    EQ=F.event_subsignals(sf1x,rebal)
    return F_,EQ,fwd,mcg,members,rebal,px.columns

def main():
    print("="*82); print("Phase 2 M5 — evaluate.py 핵심수치 재현 검증 (ndl 없음, 키 없이)"); print("="*82)
    ok=True
    F_,EQ,fwd,mcg,members,rebal,cols = broad_block()

    # 1) b2b5_broad 4 슬리브
    print("\n[1] b2b5_broad 4 슬리브 (ic/ic_ir/gross/net/turnover vs CSV)")
    ref=pd.read_csv(os.path.join(OUT,"b2b5_broad_result.csv")).set_index("sleeve")
    for sl,key in [("value","B2_value"),("quality","B3_quality"),("momentum","B4_momentum"),("lowvol","B5_lowvol")]:
        R=E.evaluate_panel(matrix_L(F_[sl],fwd,mcg,members,rebal),"score",["score","fwd"],"marketcap")
        s=E.summarize(R); r=ref.loc[key]
        print(f"  [{sl}]")
        ok&=ap(s["ic"],float(r["ic"]),1e-5,"ic"); ok&=ap(s["icir"],float(r["ic_ir"]),1e-5,"ic_ir")
        ok&=ap(s["gross_ls"],float(r["gross_ann"]),1e-5,"gross_ann"); ok&=ap(s["net_ls"],float(r["net_ann"]),1e-5,"net_ann")
        ok&=ap(s["turnover"],float(r["turnover_ann"]),1e-5,"turnover_ann")

    # 2) quality quarantine (IC-IR/subperiod/long-only vs CW·1N)
    print("\n[2] quality quarantine (리포트: IC-IR0.220·subperiod0.424/0.046·CW-1.15%·1N+1.79%)")
    Rq=E.evaluate_panel(matrix_L(F_["quality"],fwd,mcg,members,rebal),"score",["score","fwd","mc"],"marketcap")
    sq=E.summarize(Rq)
    ok&=ap(sq["icir"],0.220,3e-3,"IC-IR(전체)")
    ok&=ap(E.subperiod_icir(Rq,"2016","2020-12-31"),0.424,5e-3,"IC-IR 2016-20")
    ok&=ap(E.subperiod_icir(Rq,"2021","2026-12-31"),0.046,5e-3,"IC-IR 2021-26")
    ok&=ap(sq["act_cw"]*100,-1.15,0.03,"long-only vs CW %")
    ok&=ap(sq["act_ew"]*100,1.79,0.03,"long-only vs 1/N %")

    # 3) phase1b A_simple_blend
    print("\n[3] phase1b A_simple_blend (icir/rec_icir/net_cw vs CSV)")
    rows=[]
    for t in rebal[:-1]:
        mem=[c for c in cols if c in members[t]]
        d=pd.DataFrame({k:F_[k].loc[t].reindex(mem) for k in ["value","quality","momentum","lowvol"]})
        d["fwd"]=fwd.loc[t].reindex(mem); d["mc"]=mcg.loc[t].reindex(mem)
        d=d.dropna(subset=["value","quality","momentum","lowvol","fwd","mc"])
        if len(d)<50: continue
        d["blend"]=F.composite(d,["value","quality","momentum","lowvol"]); d["asof"]=t; d["ticker"]=d.index
        rows.append(d.reset_index(drop=True))
    Lb=pd.concat(rows,ignore_index=True); Rb=E.evaluate_panel(Lb,"blend",["blend","fwd","mc"],"marketcap"); sb=E.summarize(Rb)
    rp=pd.read_csv(os.path.join(OUT,"phase1b_lowdof_result.csv")).set_index("model").loc["A_simple_blend"]
    ok&=ap(sb["icir"],float(rp["icir"]),5e-3,"icir"); ok&=ap(sb["rec_icir"],float(rp["rec_icir"]),5e-3,"rec_icir")
    ok&=ap(sb["net_cw"]*100,float(rp["net_cw_%"]),0.02,"net_cw %")

    # 4) event composite
    print("\n[4] us_event_drift EVENT composite (ic/icir/rec_icir/net_cw vs CSV)")
    rows=[]
    for t in rebal[:-1]:
        mem=[c for c in cols if c in members[t]]
        d=pd.DataFrame({k:EQ[k].loc[t].reindex(mem) for k in F.EVENT_COLS})
        d["fwd"]=fwd.loc[t].reindex(mem); d["mc"]=mcg.loc[t].reindex(mem)
        d=d.dropna(subset=F.EVENT_COLS+["fwd","mc"])
        if len(d)<50: continue
        d["event"]=F.composite(d,F.EVENT_COLS); d["asof"]=t; d["ticker"]=d.index
        rows.append(d.reset_index(drop=True))
    Le=pd.concat(rows,ignore_index=True); Re=E.evaluate_panel(Le,"event",["event","fwd","mc"],"marketcap"); se=E.summarize(Re)
    rev=pd.read_csv(os.path.join(OUT,"us_event_drift_result.csv")).set_index("signal").loc["EVENT_composite"]
    ok&=ap(se["ic"],float(rev["ic"]),3e-4,"ic"); ok&=ap(se["icir"],float(rev["icir"]),3e-3,"icir")
    ok&=ap(se["rec_icir"],float(rev["rec_icir"]),3e-3,"rec_icir"); ok&=ap(se["net_cw"]*100,float(rev["net_cw_%"]),0.02,"net_cw %")

    # 5) small/mid (ic/icir/net_cw 3신호 vs CSV)
    print("\n[5] small/mid B (ic/icir/net_cw vs CSV)")
    sep=data.load("smallmid_SEP")
    px=sep.pivot_table(index="date",columns="ticker",values="closeadj").sort_index()
    pxu=sep.pivot_table(index="date",columns="ticker",values="closeunadj").sort_index()
    sep["dv"]=sep["closeunadj"]*sep["volume"]; adv=sep.pivot_table(index="date",columns="ticker",values="dv").sort_index().rolling(20,min_periods=5).mean(); del sep
    pb=data.load("smallmid_DAILY",usecols=["ticker","date","pb"]).pivot_table(index="date",columns="ticker",values="pb").sort_index()
    mc=data.load("DAILY_all",usecols=["ticker","date","marketcap"]).pivot_table(index="date",columns="ticker",values="marketcap").sort_index()
    sf1=data.load("smallmid_SF1"); members,rebal=load_univ("smallmid_universe_1001_3000.csv")
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
        d["event"]=F.composite(d,F.EVENT_COLS); d["blend"]=F.composite(d,["value","quality","momentum","lowvol"]); d["asof"]=t; d["ticker"]=d.index
        rows.append(d.reset_index(drop=True))
    Ls=pd.concat(rows,ignore_index=True)
    rs=pd.read_csv(os.path.join(OUT,"us_smallmid_result.csv")).set_index("signal")
    for sig in ["quality","event","blend"]:
        R=E.evaluate_panel(Ls,sig,[sig,"fwd","mc","adv"],"adv",min_names=100); s=E.summarize(R); r=rs.loc[sig]
        print(f"  [{sig}]")
        ok&=ap(s["ic"],float(r["ic"]),5e-4,"ic"); ok&=ap(s["icir"],float(r["icir"]),5e-3,"icir"); ok&=ap(s["net_cw"]*100,float(r["net_cw_%"]),0.02,"net_cw %")

    print("\n"+"="*82)
    print(f"판정: {'PASS — 5 실험 핵심수치 evaluate.py로 재현, API-free' if ok else 'FAIL — 불일치'}")
    return ok

if __name__ == "__main__":
    sys.exit(0 if main() else 1)

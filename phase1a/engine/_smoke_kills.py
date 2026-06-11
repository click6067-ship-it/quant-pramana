#!/usr/bin/env python3
"""M6 smoke — kills.py가 각 실험의 verdict+fired kill 집합 재현. ndl 없음·키 없이.
broad_retest(4슬리브)·quality quarantine·phase1b blend·event·small/mid(3신호)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd, data, features as F, evaluate as E, kills as K

OUT = os.path.join(data.PHASE1A, "outputs")
def univ(f):
    u = pd.read_csv(os.path.join(OUT, f)); u["asof"] = pd.to_datetime(u["asof"])
    return {d: set(g) for d, g in u.groupby("asof")["ticker"]}, sorted(u["asof"].unique())
def chk(name, fired, verdict, exp_fired, exp_verdict):
    okf = set(fired) == set(exp_fired); okv = (verdict == exp_verdict)
    print(f"  {name:26s} verdict={verdict:8s}({'✅' if okv else '❌ '+exp_verdict}) kills={sorted(fired)} {'✅' if okf else '❌ exp='+str(sorted(exp_fired))}")
    return okf and okv

SEC = None
def matL(M, fwd, mcg, members, rebal, sec=False):
    rows=[]
    for t in rebal[:-1]:
        mem=[c for c in M.columns if c in members[t]]
        d=pd.DataFrame({"score":M.loc[t].reindex(mem),"fwd":fwd.loc[t].reindex(mem),"mc":mcg.loc[t].reindex(mem)})
        d["asof"]=t; d["ticker"]=mem; rows.append(d)
    L=pd.concat(rows,ignore_index=True)
    if sec: L["sec"]=SEC.reindex(L["ticker"]).values
    return L
def compL(subs, fwd, mcg, members, rebal, cols, make, sec=False):
    rows=[]
    for t in rebal[:-1]:
        mem=[c for c in cols if c in members[t]]
        d=pd.DataFrame({k:subs[k].loc[t].reindex(mem) for k in subs})
        d["fwd"]=fwd.loc[t].reindex(mem); d["mc"]=mcg.loc[t].reindex(mem)
        d=d.dropna(subset=list(subs)+["fwd","mc"])
        if len(d)<50: continue
        d["score"]=make(d); d["asof"]=t; d["ticker"]=d.index; rows.append(d.reset_index(drop=True))
    L=pd.concat(rows,ignore_index=True)
    if sec: L["sec"]=SEC.reindex(L["ticker"]).values
    return L
def sn_net_cw(L):
    L2=L.copy(); L2["snsc"]=L2["score"]-L2.groupby(["asof","sec"])["score"].transform("mean")
    return E.summarize(E.evaluate_panel(L2,"snsc",["snsc","fwd","mc"],"marketcap"))["net_cw"]

def main():
    global SEC
    print("="*86); print("Phase 2 M6 — kills.py verdict 재현 검증 (ndl 없음, 키 없이)"); print("="*86)
    SEC = data.load_tickers()["sector"]
    px=data.load("broad_SEP",usecols=["ticker","date","closeadj"]).pivot_table(index="date",columns="ticker",values="closeadj").sort_index()
    pb=data.load("broad_DAILY_pb",usecols=["ticker","date","pb"]).pivot_table(index="date",columns="ticker",values="pb").sort_index()
    mc=data.load("DAILY_all",usecols=["ticker","date","marketcap"]).pivot_table(index="date",columns="ticker",values="marketcap").sort_index()
    sf1=data.load("broad_SF1"); sf1x=data.load("broad_SF1_ext"); members,rebal=univ("broad_universe_top1500.csv")
    mpx=px.reindex(rebal,method="pad"); fwd=mpx.shift(-1)/mpx-1; mcg=mc.reindex(rebal,method="pad")
    FM={"value":F.value(pb,rebal),"quality":F.quality(sf1,rebal,px.columns),"momentum":F.momentum(px,rebal),"lowvol":F.lowvol(px,rebal)}
    EQ=F.event_subsignals(sf1x,rebal); ok=True

    # 1) broad_retest 4슬리브
    print("\n[1] broad_retest (b2b5)")
    EXP={"value":({"net_le0","icir_lt20"},"DEAD"),"quality":(set(),"SURVIVE"),"momentum":({"icir_lt20"},"DEAD"),"lowvol":({"net_le0","icir_lt20","small_concentration"},"DEAD")}
    for sl in ["value","quality","momentum","lowvol"]:
        s=E.summarize(E.evaluate_panel(matL(FM[sl],fwd,mcg,members,rebal),"score",["score","fwd"],"marketcap"))
        m=dict(net_ls=s["net_ls"],icir=s["icir"],turnover=s["turnover"],iclo=s["iclo"],ichi=s["ichi"])
        fk,_,v,_=K.apply("broad_retest",m); ok&=chk(sl,fk,v,*EXP[sl])

    # 2) quality quarantine
    print("\n[2] quality_quarantine")
    Rq=E.evaluate_panel(matL(FM["quality"],fwd,mcg,members,rebal),"score",["score","fwd","mc"],"marketcap"); sq=E.summarize(Rq)
    s1=Rq[(Rq.index>="2016")&(Rq.index<="2020-12-31")]["spread"].mean(); s2=Rq[Rq.index>="2021"]["spread"].mean()
    secd=[]
    for t in rebal[:-1]:
        mem=[c for c in FM["quality"].columns if c in members[t]]
        d=pd.concat([FM["quality"].loc[t].reindex(mem),fwd.loc[t].reindex(mem)],axis=1).dropna(); d.columns=["q","r"]
        if len(d)<50: continue
        Q5=d.index[d["q"].rank(pct=True)>=0.8]; sc=SEC.reindex(Q5).dropna(); secd.append(sc.value_counts(normalize=True))
    sector_max=pd.concat(secd,axis=1).mean(axis=1).max()
    net2_ls=E.summarize(Rq,cost_mult=2)["net_ls"]
    m=dict(net2_ls=net2_ls,s1=s1,s2=s2,iclo=sq["iclo"],ichi=sq["ichi"],act_cw=sq["act_cw"],act_ew=sq["act_ew"],sector_max=sector_max)
    fk,_,v,_=K.apply("quality_quarantine",m); ok&=chk("quality",fk,v,{"longonly_cw_le0"},"FAIL")

    # 3) phase1b A_simple_blend
    print("\n[3] phase1b A_simple_blend")
    Lb=compL({k:FM[k] for k in ["value","quality","momentum","lowvol"]},fwd,mcg,members,rebal,px.columns,
             lambda d:F.composite(d,["value","quality","momentum","lowvol"]),sec=True)
    sb=E.summarize(E.evaluate_panel(Lb,"score",["score","fwd","mc"],"marketcap"))
    m=dict(net_cw=sb["net_cw"],rec_icir=sb["rec_icir"],turnover=sb["turnover"],rec_net=sb["rec_net"],sn_net_cw=sn_net_cw(Lb),act_cw=sb["act_cw"])
    fk,_,v,_=K.apply("phase1b",m); ok&=chk("A_simple_blend",fk,v,{"net_cw_le0","concentrated_early","sector_neutral_le0","longonly_cw_neg"},"FAIL")

    # 4) event
    print("\n[4] event")
    Le=compL({k:EQ[k] for k in F.EVENT_COLS},fwd,mcg,members,rebal,px.columns,lambda d:F.composite(d,F.EVENT_COLS),sec=True)
    Re=E.evaluate_panel(Le,"score",["score","fwd","mc"],"marketcap"); se=E.summarize(Re)
    m=dict(net_cw=se["net_cw"],rec_icir=se["rec_icir"],net2_cw=E.summarize(Re,cost_mult=2)["net_cw"],rec_net=se["rec_net"],act_cw=se["act_cw"],sn_net_cw=sn_net_cw(Le))
    fk,_,v,_=K.apply("event",m); ok&=chk("EVENT_composite",fk,v,{"net_cw_le0","cost2x_le0","longonly_cw_neg","sector_neutral_le0"},"FAIL")

    # 5) small/mid
    print("\n[5] small/mid (8 kills)")
    sep=data.load("smallmid_SEP"); spx=sep.pivot_table(index="date",columns="ticker",values="closeadj").sort_index()
    pxu=sep.pivot_table(index="date",columns="ticker",values="closeunadj").sort_index()
    sep["dv"]=sep["closeunadj"]*sep["volume"]; adv=sep.pivot_table(index="date",columns="ticker",values="dv").sort_index().rolling(20,min_periods=5).mean(); del sep
    spb=data.load("smallmid_DAILY",usecols=["ticker","date","pb"]).pivot_table(index="date",columns="ticker",values="pb").sort_index()
    smc=mc; ssf1=data.load("smallmid_SF1"); smem,sreb=univ("smallmid_universe_1001_3000.csv")
    smpx=spx.reindex(sreb,method="pad"); sfwd=smpx.shift(-1)/smpx-1; smcg=smc.reindex(sreb,method="pad")
    pxug=pxu.reindex(sreb,method="pad"); advg=adv.reindex(sreb,method="pad")
    sval=F.value(spb,sreb); smom=F.momentum(spx,sreb); slv=F.lowvol(spx,sreb); squal=F.quality(ssf1,sreb,spx.columns); sEQ=F.event_subsignals(ssf1,sreb)
    rows=[]
    for t in sreb[:-1]:
        mem=[c for c in spx.columns if c in smem[t]]; d=pd.DataFrame(index=mem)
        d["fwd"]=sfwd.loc[t].reindex(mem); d["mc"]=smcg.loc[t].reindex(mem); d["adv"]=advg.loc[t].reindex(mem); d["pxu"]=pxug.loc[t].reindex(mem)
        d["quality"]=squal.loc[t].reindex(mem); d["value"]=sval.loc[t].reindex(mem); d["momentum"]=smom.loc[t].reindex(mem); d["lowvol"]=slv.loc[t].reindex(mem)
        for k in F.EVENT_COLS: d[k]=sEQ[k].loc[t].reindex(mem)
        d=d[d["pxu"]>=5]
        if len(d)<100: continue
        d=d[d["adv"]>=d["adv"].quantile(0.10)]; d=d.dropna(subset=["fwd","mc","adv"])
        if len(d)<100: continue
        d["event"]=F.composite(d,F.EVENT_COLS); d["blend"]=F.composite(d,["value","quality","momentum","lowvol"]); d["asof"]=t; d["ticker"]=d.index
        rows.append(d.reset_index(drop=True))
    Ls=pd.concat(rows,ignore_index=True); advt=Ls.groupby("asof")["adv"].transform(lambda s:s.rank(pct=True))
    EXPS={"quality":{"icir_lt20","recent_dead","lowest_liq_only"},"event":{"icir_lt20","turnover_weak"},"blend":{"lowest_liq_only"}}
    for sig in ["quality","event","blend"]:
        R=E.evaluate_panel(Ls,sig,[sig,"fwd","mc","adv"],"adv",min_names=100); s=E.summarize(R)
        loq=E.summarize(E.evaluate_panel(Ls[advt<1/3],sig,[sig,"fwd","mc","adv"],"adv",min_names=50))["net_ls"]
        hiq=E.summarize(E.evaluate_panel(Ls[advt>=2/3],sig,[sig,"fwd","mc","adv"],"adv",min_names=50))["net_ls"]
        m=dict(net_cw=s["net_cw"],net_ls=s["net_ls"],icir=s["icir"],rec_net=s["rec_net"],rec_icir=s["rec_icir"],
               net2_cw=E.summarize(R,cost_mult=2)["net_cw"],lo_liq_net_ls=loq,hi_liq_net_ls=hiq,turnover=s["turnover"])
        fk,_,v,_=K.apply("smallmid",m); ok&=chk(sig,fk,v,EXPS[sig],"FAIL")

    print("\n"+"="*86); print(f"판정: {'PASS — 5 kill-set verdict+fired 재현, API-free' if ok else 'FAIL — 불일치'}")
    return ok

if __name__ == "__main__":
    sys.exit(0 if main() else 1)

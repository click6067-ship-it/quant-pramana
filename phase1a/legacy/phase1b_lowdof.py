#!/usr/bin/env python3
"""Phase 1B low-DoF challenger — 결합 가설 1회 확정테스트(사전등록 Protocol v0.1).
모델: A simple_blend(z 동일가중) · B constrained_rank(percentile-rank 동일가중) · C ridge_OOS(expanding-window).
feature 4개 고정(quality/momentum/value/lowvol), 튜닝 없음. kill 조건 사전박음 대조.
data: outputs/raw/{broad_SEP,broad_DAILY_pb,broad_SF1,DAILY_all} + broad_universe_top1500 + TICKERS sector."""
import os, numpy as np, pandas as pd, nasdaqdatalink as ndl
from math import erf, sqrt
HERE=os.path.dirname(os.path.abspath(__file__)); RAW=os.path.join(HERE,"outputs","raw"); OUT=os.path.join(HERE,"outputs")
ndl.ApiConfig.api_key=open(os.path.join(HERE,".ndl_key")).read().strip()

u=pd.read_csv(os.path.join(OUT,"broad_universe_top1500.csv")); u["asof"]=pd.to_datetime(u["asof"])
members={d:set(g) for d,g in u.groupby("asof")["ticker"]}; rebal=sorted(members)
px=pd.read_csv(os.path.join(RAW,"broad_SEP.csv"),usecols=["ticker","date","closeadj"],parse_dates=["date"]).pivot_table(index="date",columns="ticker",values="closeadj").sort_index()
pb=pd.read_csv(os.path.join(RAW,"broad_DAILY_pb.csv"),usecols=["ticker","date","pb"],parse_dates=["date"]).pivot_table(index="date",columns="ticker",values="pb").sort_index()
mc=pd.read_csv(os.path.join(RAW,"DAILY_all.csv"),usecols=["ticker","date","marketcap"],parse_dates=["date"]).pivot_table(index="date",columns="ticker",values="marketcap").sort_index()
sf1=pd.read_csv(os.path.join(RAW,"broad_SF1.csv"),parse_dates=["datekey"]); sf1=sf1[sf1["assets"]>0]; sf1["q"]=sf1["gp"]/sf1["assets"]; sf1=sf1.dropna(subset=["q"]).sort_values("datekey")
sector=ndl.get_table("SHARADAR/TICKERS",table="SEP",paginate=True).drop_duplicates("ticker").set_index("ticker")["sector"]

mpx=px.reindex(rebal,method="pad"); fwd=mpx.shift(-1)/mpx-1; mcg=mc.reindex(rebal,method="pad")
val=(1.0/pb.reindex(rebal,method="pad")).replace([np.inf,-np.inf],np.nan)
mom=mpx.shift(1)/mpx.shift(12)-1
lowvol=-px.pct_change().rolling(126).std().reindex(rebal,method="pad")
qual=pd.DataFrame(index=rebal,columns=px.columns,dtype=float)
for t in rebal:
    av=sf1[sf1["datekey"]<=t]
    if len(av):
        last=av.groupby("ticker")["q"].last(); qual.loc[t,last.index.intersection(qual.columns)]=last.reindex(qual.columns.intersection(last.index))
FEAT={"quality":qual,"momentum":mom,"value":val,"lowvol":lowvol}

def z(s):
    s=s.astype(float); mu,sd=s.mean(),s.std()
    return (s*0) if (not sd or np.isnan(sd)) else ((s-mu)/sd).clip(-3,3)

# member-month long table (z features + fwd + mc + sector)
rows=[]
for t in rebal[:-1]:
    mem=[c for c in px.columns if c in members[t]]
    d=pd.DataFrame({k:FEAT[k].loc[t,mem] for k in FEAT}); d["fwd"]=fwd.loc[t,mem]; d["mc"]=mcg.loc[t,mem]
    d=d.dropna(subset=list(FEAT)+["fwd","mc"])
    if len(d)<50: continue
    for k in FEAT: d[k+"_z"]=z(d[k])
    d["t"]=t; d["sec"]=sector.reindex(d.index).values
    rows.append(d.reset_index().rename(columns={"index":"ticker"}))
L=pd.concat(rows,ignore_index=True)
zc=[k+"_z" for k in FEAT]
L["blend"]=L[zc].mean(axis=1)                                  # A
L["rank"]=L.groupby("t")[list(FEAT)].rank(pct=True).mean(axis=1) # B (percentile-rank 평균)
# sector-neutral blend (kill#5)
L["blend_sn"]=L["blend"]-L.groupby(["t","sec"])["blend"].transform("mean")

# C: ridge OOS expanding window (closed-form, λ 고정=5.0, 표준화 feature, 24m warmup)
LAM=5.0; ts=sorted(L["t"].unique()); pred=pd.Series(index=L.index,dtype=float)
X_all=L[zc].values; y_all=L["fwd"].values
for i,t in enumerate(ts):
    if i<24: continue
    tr=L["t"]<t; Xtr=X_all[tr.values]; ytr=y_all[tr.values]
    mu=Xtr.mean(0); sd=Xtr.std(0); sd[sd==0]=1; Xs=(Xtr-mu)/sd
    w=np.linalg.solve(Xs.T@Xs+LAM*np.eye(Xs.shape[1]), Xs.T@(ytr-ytr.mean()))
    te=L["t"]==t; Xte=(X_all[te.values]-mu)/sd; pred[L.index[te.values]]=Xte@w
L["ridge"]=pred

def evaluate(scorecol, sub=None):
    df=L if sub is None else L[sub]
    recs=[]; prevQ5=set()
    for t,g in df.groupby("t"):
        g=g.dropna(subset=[scorecol])
        if len(g)<50: continue
        ic=g[scorecol].rank().corr(g["fwd"].rank())
        rk=g[scorecol].rank(pct=True); Q5=g[rk>=0.8]
        q5lo=Q5["fwd"].mean(); benchcw=(g["mc"]*g["fwd"]).sum()/g["mc"].sum(); benchew=g["fwd"].mean()
        ids=set(Q5["ticker"]); to=len(ids^prevQ5)/(2*max(len(ids),1)) if prevQ5 else 1.0
        mqn=Q5["mc"].rank(pct=True); c=np.where(mqn>=2/3,5.0,np.where(mqn>=1/3,10.0,15.0)).mean()/1e4
        recs.append(dict(t=t,ic=ic,q5lo=q5lo,bcw=benchcw,bew=benchew,to=to,cost=to*c)); prevQ5=ids
    R=pd.DataFrame(recs).set_index("t"); ic=R["ic"].dropna()
    actcw=R["q5lo"]-R["bcw"]; actew=R["q5lo"]-R["bew"]; net=actcw-R["cost"]
    rec=R[R.index>="2021-01-01"]; recic=rec["ic"]
    return dict(R=R, n=len(ic), ic=ic.mean(), icir=(ic.mean()/ic.std() if ic.std()>0 else np.nan),
        net_cw=net.mean()*12, act_cw=actcw.mean()*12, act_ew=actew.mean()*12, to=R["to"].mean()*12,
        rec_icir=(recic.mean()/recic.std() if recic.std()>0 else np.nan), rec_net=( (rec["q5lo"]-rec["bcw"]-rec["cost"]).mean()*12 ),
        early_net=((R[R.index<"2021-01-01"]["q5lo"]-R[R.index<"2021-01-01"]["bcw"]-R[R.index<"2021-01-01"]["cost"]).mean()*12))

MODELS={"A_simple_blend":"blend","B_constrained_rank":"rank","C_ridge_OOS":"ridge"}
print("="*84); print("Phase 1B — Low-DoF Challenger (사전등록 Protocol v0.1, 1회 · 튜닝없음)"); print("="*84)
out=[]
for name,col in MODELS.items():
    m=evaluate(col); sn=evaluate("blend_sn") if col=="blend" else None
    t_full=m["icir"]*np.sqrt(m["n"]) if not np.isnan(m["icir"]) else float("nan")
    p=0.5*(1-erf(t_full/sqrt(2))) if not np.isnan(t_full) else float("nan")
    kills=[]
    if m["net_cw"]<=0: kills.append("net active vs CW≤0")
    if not (m["rec_icir"]>=0.10): kills.append(f"2021-26 IC-IR<0.10({m['rec_icir']:+.3f})")
    if m["to"]>2.5 and m["net_cw"]<=0: kills.append("turnover과도&무edge")
    if m["rec_net"]<=0: kills.append("2016-20에만 집중(2021-26 net≤0)")
    if name=="A_simple_blend" and sn and sn["net_cw"]<=0: kills.append("sector중립화후 net≤0")
    if m["act_cw"]<=0 and (m["R"]["q5lo"]-m["R"]["bcw"]).mean()<0: kills.append("long-only vs CW 음수")
    verdict="PASS(→Phase1C 검토후보)" if not kills else "FAIL"
    out.append((name,m,verdict,kills))
    print(f"\n[{name}]  → {verdict}")
    print(f"  Rank IC={m['ic']:+.4f} IC-IR={m['icir']:+.3f} (t≈{t_full:.2f}, p≈{p:.4f}) · turnover≈{m['to']*100:.0f}%/yr")
    print(f"  net active vs CW={m['net_cw']*100:+.2f}%/yr | gross vs CW={m['act_cw']*100:+.2f}% | vs 1/N EW={m['act_ew']*100:+.2f}%")
    print(f"  subperiod net vs CW: 2016-20={m['early_net']*100:+.2f}%/yr | 2021-26={m['rec_net']*100:+.2f}%/yr (IC-IR {m['rec_icir']:+.3f})")
    if sn: print(f"  [sector-neutral blend] net vs CW={sn['net_cw']*100:+.2f}%/yr (kill#5 점검)")
    if kills: print(f"  KILLS: {kills}")

npass=sum(1 for _,_,v,_ in out if v.startswith("PASS"))
print("\n"+"="*84)
if npass==0:
    print("판정: 3개 모델 전부 FAIL → US simple/linear factor family 종료(TERMINATE). 다음=KR arena/다른 edge 검토.")
else:
    print(f"판정: {npass}/3 PASS → Phase 1C 검토 후보(즉시 live/paper 아님; 추가 robustness 필요).")
print("→ 사전등록 kill·판정규칙 변경 없이 적용. no tuning to rescue.")
pd.DataFrame([{"model":n,"verdict":v,"net_cw_%":round(m["net_cw"]*100,2),"icir":round(m["icir"],3),
  "rec_icir":round(m["rec_icir"],3),"rec_net_%":round(m["rec_net"]*100,2),"to_%":round(m["to"]*100,0),
  "kills":";".join(k)} for n,m,v,k in out]).to_csv(os.path.join(OUT,"phase1b_lowdof_result.csv"),index=False)
print("→ outputs/phase1b_lowdof_result.csv")

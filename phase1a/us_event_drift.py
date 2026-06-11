#!/usr/bin/env python3
"""US event/earnings drift 실험 — 사전등록 Protocol v0.1 구현(1회·튜닝없음).
이벤트=SF1 datekey(PIT 공시일). 신호=변화/서프라이즈 proxy(레벨 아님): gp/assets YoY·revenue YoY·eps YoY·grossmargin YoY + filing freshness.
EVENT composite=4개 z 동일가중. top-1500 PIT long-only Q5 + rank-IC. cost 포함. kill 사전박음 대조."""
import os, numpy as np, pandas as pd, nasdaqdatalink as ndl
from math import erf, sqrt
HERE=os.path.dirname(os.path.abspath(__file__)); RAW=os.path.join(HERE,"outputs","raw"); OUT=os.path.join(HERE,"outputs")
ndl.ApiConfig.api_key=open(os.path.join(HERE,".ndl_key")).read().strip()

u=pd.read_csv(os.path.join(OUT,"broad_universe_top1500.csv")); u["asof"]=pd.to_datetime(u["asof"])
members={d:set(g) for d,g in u.groupby("asof")["ticker"]}; rebal=sorted(members)
px=pd.read_csv(os.path.join(RAW,"broad_SEP.csv"),usecols=["ticker","date","closeadj"],parse_dates=["date"]).pivot_table(index="date",columns="ticker",values="closeadj").sort_index()
mc=pd.read_csv(os.path.join(RAW,"DAILY_all.csv"),usecols=["ticker","date","marketcap"],parse_dates=["date"]).pivot_table(index="date",columns="ticker",values="marketcap").sort_index()
sector=ndl.get_table("SHARADAR/TICKERS",table="SEP",paginate=True).drop_duplicates("ticker").set_index("ticker")["sector"]

e=pd.read_csv(os.path.join(RAW,"broad_SF1_ext.csv"),parse_dates=["datekey"])
e=e[e["assets"]>0].sort_values(["ticker","datekey"])
e["gpa"]=e["gp"]/e["assets"]
g=e.groupby("ticker")
e["S1_gpa_yoy"]=e["gpa"]-g["gpa"].shift(4)
e["S2_rev_yoy"]=e["revenue"]/g["revenue"].shift(4)-1
e["S3_eps_yoy"]=(e["epsusd"]-g["epsusd"].shift(4))/g["epsusd"].shift(4).abs()
e["S4_gm_yoy"]=e["grossmargin"]-g["grossmargin"].shift(4)
e=e.replace([np.inf,-np.inf],np.nan)
SIG=["S1_gpa_yoy","S2_rev_yoy","S3_eps_yoy","S4_gm_yoy"]

def asof_mat(col):   # (datekey×ticker) → 컬럼 ffill(PIT last-known) → rebal pad
    return e.pivot_table(index="datekey",columns="ticker",values=col).sort_index().ffill().reindex(rebal,method="pad")
S={k:asof_mat(k) for k in SIG}
dkmat=e.assign(dk=e["datekey"]).pivot_table(index="datekey",columns="ticker",values="dk",aggfunc="last").sort_index().ffill().reindex(rebal,method="pad")

mpx=px.reindex(rebal,method="pad"); fwd=mpx.shift(-1)/mpx-1; mcg=mc.reindex(rebal,method="pad")
def z(s):
    s=s.astype(float); mu,sd=s.mean(),s.std()
    return (s*0) if (not sd or np.isnan(sd)) else ((s-mu)/sd).clip(-3,3)

rows=[]
for t in rebal[:-1]:
    mem=[c for c in px.columns if c in members[t]]
    d=pd.DataFrame({k:S[k].loc[t].reindex(mem) for k in SIG}); d["fwd"]=fwd.loc[t].reindex(mem); d["mc"]=mcg.loc[t].reindex(mem)
    d["fresh"]=(t-dkmat.loc[t].reindex(mem)).dt.days
    d=d.dropna(subset=SIG+["fwd","mc"])
    if len(d)<50: continue
    for k in SIG: d[k+"_z"]=z(d[k])
    d["event"]=d[[k+"_z" for k in SIG]].mean(axis=1)
    d["t"]=t; d["sec"]=sector.reindex(d.index).values
    rows.append(d.reset_index().rename(columns={"index":"ticker"}))
L=pd.concat(rows,ignore_index=True)
L["event_sn"]=L["event"]-L.groupby(["t","sec"])["event"].transform("mean")

def evaluate(scorecol, sub=None):
    df=L if sub is None else L[sub]; recs=[]; prevQ5=set()
    for t,gp in df.groupby("t"):
        gp=gp.dropna(subset=[scorecol])
        if len(gp)<50: continue
        ic=gp[scorecol].rank().corr(gp["fwd"].rank())
        rk=gp[scorecol].rank(pct=True); Q5=gp[rk>=0.8]
        q5lo=Q5["fwd"].mean(); bcw=(gp["mc"]*gp["fwd"]).sum()/gp["mc"].sum(); bew=gp["fwd"].mean()
        ids=set(Q5["ticker"]); to=len(ids^prevQ5)/(2*max(len(ids),1)) if prevQ5 else 1.0
        mqn=Q5["mc"].rank(pct=True); c=np.where(mqn>=2/3,5.0,np.where(mqn>=1/3,10.0,15.0)).mean()/1e4
        recs.append(dict(t=t,ic=ic,q5lo=q5lo,bcw=bcw,bew=bew,to=to,cost=to*c)); prevQ5=ids
    R=pd.DataFrame(recs).set_index("t"); ic=R["ic"].dropna()
    actcw=R["q5lo"]-R["bcw"]; net=actcw-R["cost"]; net2=actcw-2*R["cost"]
    rec=R[R.index>="2021-01-01"]; recic=rec["ic"]; early=R[R.index<"2021-01-01"]
    return dict(R=R,n=len(ic),ic=ic.mean(),icir=(ic.mean()/ic.std() if ic.std()>0 else np.nan),
        net_cw=net.mean()*12, net2_cw=net2.mean()*12, act_cw=actcw.mean()*12, act_ew=(R["q5lo"]-R["bew"]).mean()*12, to=R["to"].mean()*12,
        rec_icir=(recic.mean()/recic.std() if recic.std()>0 else np.nan),
        rec_net=((rec["q5lo"]-rec["bcw"]-rec["cost"]).mean()*12), early_net=((early["q5lo"]-early["bcw"]-early["cost"]).mean()*12))

print("="*86); print("US EVENT / EARNINGS DRIFT — 사전등록 1회 kill-test (튜닝없음)"); print("="*86)
# 신호별 단독 IC(어느 게 일하나)
print("\n[신호별 단독 Rank IC / IC-IR]")
for k in SIG:
    m=evaluate(k+"_z"); print(f"  {k:14s} IC={m['ic']:+.4f} IC-IR={m['icir']:+.3f} (2021-26 IC-IR={m['rec_icir']:+.3f})")

m=evaluate("event"); sn=evaluate("event_sn")
t_full=m["icir"]*np.sqrt(m["n"]); p=0.5*(1-erf(t_full/sqrt(2)))
print(f"\n[EVENT composite] (S1~S4 z 동일가중)")
print(f"  n={m['n']}월 · Rank IC={m['ic']:+.4f} · IC-IR={m['icir']:+.3f} (t≈{t_full:.2f}, p≈{p:.4f}) · turnover≈{m['to']*100:.0f}%/yr")
print(f"  net active vs CW(1x)={m['net_cw']*100:+.2f}%/yr · (2x)={m['net2_cw']*100:+.2f}%/yr | gross vs CW={m['act_cw']*100:+.2f}% | vs 1/N EW={m['act_ew']*100:+.2f}%")
print(f"  subperiod net vs CW: 2016-20={m['early_net']*100:+.2f}%/yr | 2021-26={m['rec_net']*100:+.2f}%/yr (IC-IR {m['rec_icir']:+.3f})")
print(f"  [sector-neutral] net vs CW={sn['net_cw']*100:+.2f}%/yr (kill#6)")
# freshness diagnostic: 최근 공시(≤63일) 부분표본서 composite IC
fresh=L["fresh"]<=63; mf=evaluate("event",sub=fresh)
print(f"  [freshness] 최근공시(≤63일) 부분표본 composite IC-IR={mf['icir']:+.3f} (2021-26 {mf['rec_icir']:+.3f}) — PEAD-lite 창")

kills=[]
if m["net_cw"]<=0: kills.append("net active vs CW≤0")
if not (m["rec_icir"]>=0.10): kills.append(f"2021-26 IC-IR<0.10({m['rec_icir']:+.3f})")
if m["net2_cw"]<=0: kills.append("2x cost net≤0")
if m["rec_net"]<=0: kills.append("2016-20에만 집중(2021-26 net≤0)")
if m["act_cw"]<=0: kills.append("long-only vs CW 음수")
if sn["net_cw"]<=0: kills.append("sector중립화후 net≤0")
verdict="유망(deeper event study 후보)" if not kills else "FAIL → US event 신호군 종료"
print("\n"+"="*86); print(f"판정: {verdict}")
if kills: print(f"  KILLS: {kills}")
print("  → 사전등록 kill·판정규칙 변경없이 적용. no tuning to rescue. no live/paper.")
print("  → "+("다음=deeper PEAD(가격반응)·다중검정·OOS" if not kills else "다음=B(US 소형 cost-first) → C(KR feasibility)"))
pd.DataFrame([{"signal":"EVENT_composite","verdict":verdict,"ic":round(m["ic"],4),"icir":round(m["icir"],3),
  "rec_icir":round(m["rec_icir"],3),"net_cw_%":round(m["net_cw"]*100,2),"net2_cw_%":round(m["net2_cw"]*100,2),
  "rec_net_%":round(m["rec_net"]*100,2),"to_%":round(m["to"]*100,0),"kills":";".join(kills)}]
).to_csv(os.path.join(OUT,"us_event_drift_result.csv"),index=False)
print("→ outputs/us_event_drift_result.csv")

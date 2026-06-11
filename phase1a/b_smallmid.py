#!/usr/bin/env python3
"""US Small/Mid Cost-First kill-test — 사전등록 Protocol v0.1 구현(1회·튜닝없음).
universe=rank1001-3000 PIT, 필터 price≥$5·ADV하위10%컷. 신호=quality/event/blend(검증된것만)+value/mom/lowvol(비교).
보수적 비용(ADV tier 25/45/75bp, base/2x/3x). 벤치=small/mid cap-weight + 1/N. 8 kill 사전박음 대조."""
import os, numpy as np, pandas as pd, nasdaqdatalink as ndl
from math import erf, sqrt
HERE=os.path.dirname(os.path.abspath(__file__)); RAW=os.path.join(HERE,"outputs","raw"); OUT=os.path.join(HERE,"outputs")
ndl.ApiConfig.api_key=open(os.path.join(HERE,".ndl_key")).read().strip()

u=pd.read_csv(os.path.join(OUT,"smallmid_universe_1001_3000.csv")); u["asof"]=pd.to_datetime(u["asof"])
members={d:set(g) for d,g in u.groupby("asof")["ticker"]}; rank_of={(a,t):r for a,t,r in zip(u["asof"],u["ticker"],u["rank"])}
rebal=sorted(members)
sep=pd.read_csv(os.path.join(RAW,"smallmid_SEP.csv"),parse_dates=["date"])
px=sep.pivot_table(index="date",columns="ticker",values="closeadj").sort_index()
pxu=sep.pivot_table(index="date",columns="ticker",values="closeunadj").sort_index()
sep["dv"]=sep["closeunadj"]*sep["volume"]
adv=sep.pivot_table(index="date",columns="ticker",values="dv").sort_index().rolling(20,min_periods=5).mean()
del sep
pb=pd.read_csv(os.path.join(RAW,"smallmid_DAILY.csv"),parse_dates=["date"]).pivot_table(index="date",columns="ticker",values="pb").sort_index()
mc=pd.read_csv(os.path.join(RAW,"DAILY_all.csv"),usecols=["ticker","date","marketcap"],parse_dates=["date"]).pivot_table(index="date",columns="ticker",values="marketcap").sort_index()
sf=pd.read_csv(os.path.join(RAW,"smallmid_SF1.csv"),parse_dates=["datekey"]); sf=sf[sf["assets"]>0].sort_values(["ticker","datekey"])
sf["gpa"]=sf["gp"]/sf["assets"]; g=sf.groupby("ticker")
sf["e_gpa"]=sf["gpa"]-g["gpa"].shift(4); sf["e_rev"]=sf["revenue"]/g["revenue"].shift(4)-1
sf["e_eps"]=(sf["epsusd"]-g["epsusd"].shift(4))/g["epsusd"].shift(4).abs(); sf["e_gm"]=sf["grossmargin"]-g["grossmargin"].shift(4)
sf=sf.replace([np.inf,-np.inf],np.nan)
def amat(col): return sf.pivot_table(index="datekey",columns="ticker",values=col).sort_index().ffill().reindex(rebal,method="pad")

mpx=px.reindex(rebal,method="pad"); fwd=mpx.shift(-1)/mpx-1; mcg=mc.reindex(rebal,method="pad")
pxug=pxu.reindex(rebal,method="pad"); advg=adv.reindex(rebal,method="pad")
val=(1.0/pb.reindex(rebal,method="pad")).replace([np.inf,-np.inf],np.nan)
mom=mpx.shift(1)/mpx.shift(12)-1; lowvol=-px.pct_change().rolling(126).std().reindex(rebal,method="pad")
qual=amat("gpa"); EQ={k:amat(k) for k in ["e_gpa","e_rev","e_eps","e_gm"]}
def z(s):
    s=s.astype(float); mu,sd=s.mean(),s.std()
    return (s*0) if (not sd or np.isnan(sd)) else ((s-mu)/sd).clip(-3,3)

rows=[]
for t in rebal[:-1]:
    mem=[c for c in px.columns if c in members[t]]
    d=pd.DataFrame(index=mem)
    d["fwd"]=fwd.loc[t].reindex(mem); d["mc"]=mcg.loc[t].reindex(mem); d["adv"]=advg.loc[t].reindex(mem); d["pxu"]=pxug.loc[t].reindex(mem)
    d["quality"]=qual.loc[t].reindex(mem); d["value"]=val.loc[t].reindex(mem); d["momentum"]=mom.loc[t].reindex(mem); d["lowvol"]=lowvol.loc[t].reindex(mem)
    for k in EQ: d[k]=EQ[k].loc[t].reindex(mem)
    # 필터: price>=$5, ADV 하위10% 컷
    d=d[d["pxu"]>=5];
    if len(d)<100: continue
    advfloor=d["adv"].quantile(0.10); d=d[d["adv"]>=advfloor]
    d=d.dropna(subset=["fwd","mc","adv"])
    if len(d)<100: continue
    d["event"]=pd.concat([z(d[k]) for k in EQ],axis=1).mean(axis=1)
    d["blend"]=pd.concat([z(d["value"]),z(d["quality"]),z(d["momentum"]),z(d["lowvol"])],axis=1).mean(axis=1)
    d["rk"]=u_rank=[rank_of.get((t,x),np.nan) for x in d.index]
    d["t"]=t; rows.append(d.reset_index().rename(columns={"index":"ticker"}))
L=pd.concat(rows,ignore_index=True)

def cost_oneway(adv_series):   # 보수적 ADV tier: 상위25/중45/하75 bp
    q=adv_series.rank(pct=True); c=pd.Series(75.0,index=adv_series.index); c[q>=1/3]=45.0; c[q>=2/3]=25.0
    return c/1e4

def evaluate(col, sub=None):
    df=L if sub is None else L[sub]; recs=[]; prevQ5=set(); prevQ1=set()
    for t,gp in df.groupby("t"):
        gp=gp.dropna(subset=[col])
        if len(gp)<100: continue
        ic=gp[col].rank().corr(gp["fwd"].rank())
        rk=gp[col].rank(pct=True); Q5=gp[rk>=0.8]; Q1=gp[rk<=0.2]
        q5lo=Q5["fwd"].mean(); spread=q5lo-Q1["fwd"].mean()
        bcw=(gp["mc"]*gp["fwd"]).sum()/gp["mc"].sum(); bew=gp["fwd"].mean()
        i5=set(Q5["ticker"]); i1=set(Q1["ticker"])
        to5=len(i5^prevQ5)/(2*max(len(i5),1)) if prevQ5 else 1.0; to1=len(i1^prevQ1)/(2*max(len(i1),1)) if prevQ1 else 1.0
        c5=cost_oneway(Q5.set_index("ticker")["adv"]).mean(); c1=cost_oneway(Q1.set_index("ticker")["adv"]).mean()
        recs.append(dict(t=t,ic=ic,q5lo=q5lo,spread=spread,bcw=bcw,bew=bew,to5=to5,cost_lo=to5*c5,cost_ls=to5*c5+to1*c1))
        prevQ5=i5; prevQ1=i1
    R=pd.DataFrame(recs).set_index("t"); ic=R["ic"].dropna()
    actcw=R["q5lo"]-R["bcw"]; actew=R["q5lo"]-R["bew"]
    netlo=actcw-R["cost_lo"]; netlo2=actcw-2*R["cost_lo"]; netlo3=actcw-3*R["cost_lo"]
    netls=R["spread"]-R["cost_ls"]
    rec=R[R.index>="2021-01-01"]; recic=rec["ic"]
    return dict(R=R,n=len(ic),ic=ic.mean(),icir=(ic.mean()/ic.std() if ic.std()>0 else np.nan),
        net_cw=netlo.mean()*12, net2_cw=netlo2.mean()*12, net3_cw=netlo3.mean()*12, act_cw=actcw.mean()*12, act_ew=actew.mean()*12,
        net_ls=netls.mean()*12, gross_ls=R["spread"].mean()*12, to=R["to5"].mean()*12,
        rec_icir=(recic.mean()/recic.std() if recic.std()>0 else np.nan), rec_net=((rec["q5lo"]-rec["bcw"]-rec["cost_lo"]).mean()*12))

print("="*90); print("US SMALL/MID COST-FIRST — 사전등록 1회 kill-test (rank1001-3000, 튜닝없음)"); print("="*90)
print(f"필터후 평균 종목수/월≈{int(L.groupby('t').size().mean())} · 월수={L['t'].nunique()}")
print("\n[비교용 단독 IC]")
for k in ["value","momentum","lowvol"]:
    m=evaluate(k); print(f"  {k:9s} IC={m['ic']:+.4f} IC-IR={m['icir']:+.3f} net(1x) Q5-Q1={m['net_ls']*100:+.2f}%/yr")

results={}; killmap={}
for name in ["quality","event","blend"]:
    m=evaluate(name); results[name]=m
    # 유동성/size 버킷 attribution
    advt=L.groupby("t")["adv"].transform(lambda s: s.rank(pct=True))
    lo_liq=evaluate(name, sub=(advt<1/3)); hi_liq=evaluate(name, sub=(advt>=2/3))
    t_full=m["icir"]*np.sqrt(m["n"]); p=0.5*(1-erf(t_full/sqrt(2)))
    kills=[]
    if m["net_cw"]<=0: kills.append("net active vs CW≤0")
    if m["net_ls"]<=0: kills.append("net Q5-Q1≤0")
    if not (m["icir"]>=0.20): kills.append(f"IC-IR<0.20({m['icir']:+.3f})")
    if m["rec_net"]<=0 or not (m["rec_icir"]>=0.10): kills.append(f"2021-26 사망(net{m['rec_net']*100:+.1f}%,IC-IR{m['rec_icir']:+.3f})")
    if m["net2_cw"]<=0: kills.append("2x cost 사망")
    if (lo_liq["net_ls"]>0) and (hi_liq["net_ls"]<=0): kills.append("최저유동성에만 존재")
    if m["to"]>3.0 and m["net_cw"]<0.02: kills.append("turnover>300%&net약")
    if m["net_cw"]<=0 and m["net_ls"]>0: kills.append("short leg 필요(long-only 안됨)")
    killmap[name]=kills
    verdict="PASS→quarantine(승격아님)" if not kills else "FAIL"
    print(f"\n[{name}] → {verdict}")
    print(f"  IC={m['ic']:+.4f} IC-IR={m['icir']:+.3f}(t≈{t_full:.2f},p≈{p:.4f}) · turnover≈{m['to']*100:.0f}%/yr")
    print(f"  long-only net vs CW: 1x={m['net_cw']*100:+.2f}% 2x={m['net2_cw']*100:+.2f}% 3x={m['net3_cw']*100:+.2f}%/yr | vs 1/N gross={m['act_ew']*100:+.2f}%")
    print(f"  Q5-Q1: gross={m['gross_ls']*100:+.2f}% net(1x)={m['net_ls']*100:+.2f}%/yr | 2021-26 net(lo) vs CW={m['rec_net']*100:+.2f}%(IC-IR {m['rec_icir']:+.3f})")
    print(f"  유동성버킷 net Q5-Q1: 저={lo_liq['net_ls']*100:+.2f}% 고={hi_liq['net_ls']*100:+.2f}%/yr")
    if kills: print(f"  KILLS: {kills}")

npass=sum(1 for n in ["quality","event"] if not killmap[n])   # 핵심후보(quality/event) 중 무-kill 통과 수
print("\n"+"="*90)
if npass==0:
    print("판정: quality·event 핵심후보 전부 FAIL → US public-data cross-sectional arena 종료(TERMINATE). → KR feasibility로 이동.")
else:
    print(f"판정: {npass}개 신호 kill 통과 → 승격금지·추가 quarantine(capacity/2x3x/subperiod/liquidity/long-only/sector) 후에만 다음.")
print("→ no tuning to rescue · no live/paper · goalpost 불변.")
pd.DataFrame([{"signal":n,"ic":round(results[n]["ic"],4),"icir":round(results[n]["icir"],3),
  "net_cw_%":round(results[n]["net_cw"]*100,2),"net2_cw_%":round(results[n]["net2_cw"]*100,2),"net_ls_%":round(results[n]["net_ls"]*100,2),
  "rec_icir":round(results[n]["rec_icir"],3),"to_%":round(results[n]["to"]*100,0)} for n in ["quality","event","blend"]]
).to_csv(os.path.join(OUT,"us_smallmid_result.csv"),index=False)
print("→ outputs/us_smallmid_result.csv")

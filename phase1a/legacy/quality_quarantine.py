#!/usr/bin/env python3
"""B3 quality(gp/assets) quarantine 검증 — 정의 고정·튜닝 금지. top-1500 PIT.
1)subperiod 2)cost stress 1x/2x/3x 3)long-only vs cap-weight benchmark 4)multiple-testing(4중1) 5)stability(size/sector/turnover).
판정: Phase 1B 입력 후보 승격 or simple-factor 종료. live/paper 승격 금지."""
import os, numpy as np, pandas as pd, nasdaqdatalink as ndl
HERE=os.path.dirname(os.path.abspath(__file__)); RAW=os.path.join(HERE,"outputs","raw"); OUT=os.path.join(HERE,"outputs")
ndl.ApiConfig.api_key=open(os.path.join(HERE,".ndl_key")).read().strip()

u=pd.read_csv(os.path.join(OUT,"broad_universe_top1500.csv")); u["asof"]=pd.to_datetime(u["asof"])
members={d:set(g) for d,g in u.groupby("asof")["ticker"]}; rebal=sorted(members)
px=pd.read_csv(os.path.join(RAW,"broad_SEP.csv"),usecols=["ticker","date","closeadj"],parse_dates=["date"]).pivot_table(index="date",columns="ticker",values="closeadj").sort_index()
mc=pd.read_csv(os.path.join(RAW,"DAILY_all.csv"),usecols=["ticker","date","marketcap"],parse_dates=["date"]).pivot_table(index="date",columns="ticker",values="marketcap").sort_index()
sf1=pd.read_csv(os.path.join(RAW,"broad_SF1.csv"),parse_dates=["datekey"]); sf1=sf1[sf1["assets"]>0]; sf1["q"]=sf1["gp"]/sf1["assets"]; sf1=sf1.dropna(subset=["q"]).sort_values("datekey")
tk=ndl.get_table("SHARADAR/TICKERS",table="SEP",paginate=True).drop_duplicates("ticker").set_index("ticker")
sector=tk["sector"]

mpx=px.reindex(rebal,method="pad"); fwd=mpx.shift(-1)/mpx-1; mcg=mc.reindex(rebal,method="pad")
qual=pd.DataFrame(index=rebal,columns=px.columns,dtype=float)
for t in rebal:
    av=sf1[sf1["datekey"]<=t]
    if len(av):
        last=av.groupby("ticker")["q"].last(); qual.loc[t,last.index.intersection(qual.columns)]=last.reindex(qual.columns.intersection(last.index))
def ctier(tkrs,t):
    m=mcg.loc[t,[x for x in tkrs if x in mcg.columns]].dropna()
    if not len(m): return pd.Series(10.0,index=tkrs)
    qn=m.rank(pct=True); c=pd.Series(15.0,index=m.index); c[qn>=1/3]=10.0; c[qn>=2/3]=5.0
    return c.reindex(tkrs).fillna(10.0)

recs=[]; prevQ5=set(); prevQ1=set(); q5sectors=[]
for t in rebal[:-1]:
    mem=members[t]; cols=[c for c in qual.columns if c in mem]
    d=pd.concat([qual.loc[t,cols],fwd.loc[t,cols],mcg.loc[t,cols]],axis=1).dropna(); d.columns=["q","r","mc"]
    if len(d)<50: continue
    ic=d["q"].rank().corr(d["r"].rank())
    rk=d["q"].rank(pct=True); Q5=d.index[rk>=0.8]; Q1=d.index[rk<=0.2]
    g=d.loc[Q5,"r"].mean()-d.loc[Q1,"r"].mean()
    bench=(d["mc"]*d["r"]).sum()/d["mc"].sum()           # cap-weight benchmark (전 멤버)
    bench_ew=d["r"].mean()                               # 1/N equal-weight benchmark (apples-to-apples)
    q5lo=d.loc[Q5,"r"].mean()                            # Q5 long-only EW
    to5=len(set(Q5)^prevQ5)/(2*max(len(Q5),1)) if prevQ5 else 1.0
    to1=len(set(Q1)^prevQ1)/(2*max(len(Q1),1)) if prevQ1 else 1.0
    c5=ctier(list(Q5),t).mean()/1e4; c1=ctier(list(Q1),t).mean()/1e4
    half=d["mc"].median(); lo=d[d["mc"]<=half]; hi=d[d["mc"]>half]
    recs.append(dict(t=t,ic=ic,g=g,to5=to5,to1=to1,c5=c5,c1=c1,bench=bench,bench_ew=bench_ew,q5lo=q5lo,
                     iclo=(lo["q"].rank().corr(lo["r"].rank()) if len(lo)>=30 else np.nan),
                     ichi=(hi["q"].rank().corr(hi["r"].rank()) if len(hi)>=30 else np.nan)))
    sec=sector.reindex(Q5).dropna(); q5sectors.append(sec.value_counts(normalize=True))
    prevQ5=set(Q5); prevQ1=set(Q1)
R=pd.DataFrame(recs).set_index("t")

def stats(df):
    ic=df["ic"].dropna(); icir=ic.mean()/ic.std()*np.sqrt(1) if ic.std()>0 else np.nan
    return ic.mean(), ic.mean()/ic.std() if ic.std()>0 else np.nan, (ic>0).mean(), df["g"].mean()*12, len(ic)
print("="*78); print("B3 quality (gp/assets) — QUARANTINE 검증 (정의 고정)"); print("="*78)
icm,icir,icpos,gann,n=stats(R)
tstat=icir*np.sqrt(n)
print(f"\n[전체] n={n}월 · Rank IC={icm:+.4f} · IC-IR={icir:+.3f} · IC>0={icpos*100:.0f}% · gross Q5-Q1={gann*100:+.2f}%/yr · IC t≈{tstat:.2f}")

print("\n[1] SUBPERIOD")
for lab,a,b in [("2016-2020","2016","2020"),("2021-2026","2021","2026")]:
    sub=R[(R.index>=a)&(R.index<=b+"-12-31")]
    if len(sub): m,ir,p,ga,nn=stats(sub); print(f"  {lab}: IC={m:+.4f} IC-IR={ir:+.3f} IC>0={p*100:.0f}% Q5-Q1={ga*100:+.1f}%/yr (n={nn})")
print("  연도별 IC:")
print("   ", {str(y): round(R[R.index.year==y]['ic'].mean(),4) for y in range(2016,2027)})

print("\n[2] COST STRESS (net Q5-Q1 연환산)")
for mult in [1,2,3]:
    net=(R["g"]-(R["to5"]*R["c5"]+R["to1"]*R["c1"])*mult).mean()*12
    print(f"  {mult}x cost: net Q5-Q1 = {net*100:+.2f}%/yr")

print("\n[3] LONG-ONLY (Q5 EW long-only)")
act=(R["q5lo"]-R["bench"]); te=act.std()*np.sqrt(12)
act_ew=(R["q5lo"]-R["bench_ew"]); te_ew=act_ew.std()*np.sqrt(12)   # apples-to-apples: Q5-EW vs 1/N-EW
print(f"  vs cap-weight bench: active(gross)={act.mean()*12*100:+.2f}%/yr · TE={te*100:.1f}% · IR={act.mean()*12/te if te>0 else float('nan'):+.2f}")
print(f"  vs 1/N EW bench    : active(gross)={act_ew.mean()*12*100:+.2f}%/yr · TE={te_ew*100:.1f}% · IR={act_ew.mean()*12/te_ew if te_ew>0 else float('nan'):+.2f}   ← quality long-leg 순효과 (스타일 드래그 제거)")
print(f"  turnover(Q5)≈{R['to5'].mean()*12*100:.0f}%/yr · net(vs CW, Q5 turnover×tier)≈{(act.mean()-R['to5'].mean()*R['c5'].mean())*12*100:+.2f}%/yr")

print("\n[4] MULTIPLE-TESTING (4팩터 중 1 생존)")
from math import erf,sqrt
p1=0.5*(1-erf(tstat/sqrt(2)))            # one-sided p
bonf=min(1.0,p1*4)
print(f"  IC t≈{tstat:.2f} → one-sided p≈{p1:.4f} · Bonferroni×4 p≈{bonf:.4f} → {'유의(보정후)' if bonf<0.05 else 'marginal/비유의(보정후)'}")
print(f"  DSR-lite: 4 trial 중 best 기대치 deflate 고려 시 t≈{tstat:.2f}는 {'경계' if 2.0<tstat<2.8 else ('약함' if tstat<=2.0 else '비교적 견고')}")

print("\n[5] STABILITY")
print(f"  size-bucket IC: 하위절반={R['iclo'].mean():+.4f} 상위절반={R['ichi'].mean():+.4f} (한쪽 몰빵 아니면 OK)")
print(f"  (liquidity bucket: volume 미pull → marketcap proxy=size와 동일, 참고)")
secavg=pd.concat(q5sectors,axis=1).mean(axis=1).sort_values(ascending=False)
print(f"  Q5 sector 평균비중 top3: {dict(secavg.head(3).round(3))} · 최대섹터 {secavg.max()*100:.0f}%")
print(f"  Q5 turnover≈{R['to5'].mean()*12*100:.0f}%/yr · Q1 turnover≈{R['to1'].mean()*12*100:.0f}%/yr")

# 판정
net2=(R["g"]-(R["to5"]*R["c5"]+R["to1"]*R["c1"])*2).mean()*12
s1=R[(R.index>="2016")&(R.index<="2020-12-31")]["g"].mean(); s2=R[(R.index>="2021")]["g"].mean()
fails=[]
if net2<=0: fails.append("2x cost net≤0")
if (s1>0)!=(s2>0): fails.append("전후반 방향 불일치")
if abs(R['iclo'].mean())>0.03 and abs(R['ichi'].mean())<0.005: fails.append("소형 몰빵")
if (act.mean()*12)<=0: fails.append("long-only active≤0(vs CW)")
if (act_ew.mean()*12)<=0: fails.append("long-leg≤0(vs 1/N, 순quality)")
if secavg.max()>0.5: fails.append("sector 과집중")
verdict = "FAIL → simple-factor family 종료" if fails else "PASS → Phase 1B 입력 후보로만 승격(채택/live 아님)"
print("\n"+"="*78); print(f"판정: {verdict}" + (f"  사유:{fails}" if fails else "") + f"  | 다중검정: Bonferroni p≈{bonf:.3f}")

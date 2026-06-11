#!/usr/bin/env python3
"""PRAMANA — 6개월 진입 V5 손실 면밀 분석.
질문: 왜 졌나 · 왜 낙폭때 헷지 못했나 · 왜 고점서 익절/리밸런싱 안 했나 · 왜 낙폭 신호 못 잡았나.
방법: 레버 경로 기록 + 일정레버 counterfactual로 vol-target procyclical 효과 분리. cached SFP_FUNDS."""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import data
CAP=100_000_000; RF=0.05; TVOL=0.28; LMAX=2.0
etf=data.load("SFP_FUNDS",usecols=["ticker","date","closeadj"]).pivot_table(index="date",columns="ticker",values="closeadj").sort_index()
ret=etf.pct_change(); core=0.5*ret["SPY"]+0.5*ret["QQQ"]; rvol=core.rolling(20).std()*np.sqrt(252)
alldays=etf.index[etf.index>=etf.index[210]]; days=alldays[-126:]   # 6개월
def ddscale(dd): return 0.2 if dd<=-0.40 else 0.4 if dd<=-0.30 else 0.7 if dd<=-0.20 else 1.0
nav=[CAP]; peak=CAP; recs=[]
for i in range(1,len(days)):
    d,p=days[i],days[i-1]; rv=rvol.get(p,np.nan)
    Lvt=min(LMAX,TVOL/rv) if (pd.notna(rv) and rv>0) else 1.0; dd=nav[-1]/peak-1; Ldd=ddscale(dd); L=Lvt*Ldd
    nav.append(nav[-1]*(1+L*core.get(d,0)-(L-1)*RF/252)); peak=max(peak,nav[-1])
    recs.append({"date":d,"L":L,"Lvt":Lvt,"Ldd":Ldd,"dd":dd,"core":core.get(d,0),"vol":rv})
NAV=pd.Series(nav,index=days); D=pd.DataFrame(recs).set_index("date")
core_nav=CAP*(1+core.reindex(days).fillna(0)).cumprod(); qqq_nav=CAP*(1+ret["QQQ"].reindex(days).fillna(0)).cumprod(); spy_nav=CAP*(1+ret["SPY"].reindex(days).fillna(0)).cumprod()
# counterfactual: 일정 레버(평균L, vol-target·ladder 없이)
Lavg=D["L"].mean(); cf=CAP*(1+(Lavg*core.reindex(days).fillna(0)-(Lavg-1)*RF/252)).cumprod()
def mdd(s): return (s/s.cummax()-1).min()
tot=lambda s: s.iloc[-1]/s.iloc[0]-1
print(f"\n{'='*78}\n6개월 진입 V5 면밀 분석 ({days[0].date()}→{days[-1].date()})\n{'='*78}")
print(f"누적: V5 {tot(NAV)*100:+.1f}% · QQQ {tot(qqq_nav)*100:+.1f}% · SPY {tot(spy_nav)*100:+.1f}% · Core(무레버) {tot(core_nav)*100:+.1f}%")
print(f"MDD : V5 {mdd(NAV)*100:.0f}% · QQQ {mdd(qqq_nav)*100:.0f}% · Core {mdd(core_nav)*100:.0f}%")
print(f"레버: 평균 {Lavg:.2f}x · 범위 {D['L'].min():.2f}~{D['L'].max():.2f}x")
# 낙폭 trough 분석
ddser=NAV/NAV.cummax()-1; trough=ddser.idxmin()
ti=list(days).index(trough)
print(f"\n최저점(trough) {trough.date()} · 그날까지 낙폭 {ddser.min()*100:.0f}%")
win=days[max(0,ti-10):min(len(days),ti+11)]
print(f"  trough 전후 레버 경로(주요): 전 {D['L'].reindex(days[max(0,ti-10):ti]).mean():.2f}x → trough {D['L'].get(trough,float('nan')):.2f}x → 후 {D['L'].reindex(days[ti+1:min(len(days),ti+11)]).mean():.2f}x")
print(f"  trough 시점 vol {D['vol'].get(trough,float('nan'))*100:.0f}% · DD ladder scale {D['Ldd'].get(trough,float('nan')):.1f}")
# procyclical 분리: V5 vs 일정레버 counterfactual
print(f"\nprocyclical 효과 분리:")
print(f"  V5(vol-target+ladder) 누적 {tot(NAV)*100:+.1f}% vs 일정레버({Lavg:.2f}x 고정) {tot(cf)*100:+.1f}%")
print(f"  → 차이 {(tot(NAV)-tot(cf))*100:+.1f}%p = vol-target/ladder의 *타이밍* 효과(음수면 디레버가 손해)")
print(f"  V5 MDD {mdd(NAV)*100:.0f}% vs 일정레버 MDD {mdd(cf)*100:.0f}% (ladder가 MDD 줄였나)")
# 월별 레버 vs core
D["ym"]=D.index.to_period("M")
mb=D.groupby("ym").agg(L=("L","mean"),core=("core","sum"),vol=("vol","mean"))
print(f"\n월별: 레버 vs core수익(레버가 손실월에 컸나=증폭, 회복월에 작았나=놓침):")
for ym,r in mb.iterrows(): print(f"  {ym}  L {r['L']:.2f}x · core {r['core']*100:+.1f}% · vol {r['vol']*100:.0f}%")
D.to_csv(os.path.join(data.PHASE1A,"outputs","engine","analyze_6mo.csv"))
print(f"\n핵심: ① 평균 {Lavg:.2f}x 레버가 choppy/down core를 증폭(MDD {mdd(core_nav)*100:.0f}%→{mdd(NAV)*100:.0f}%). ② vol-target은 20일 후행 → 떨어진 *뒤* 디레버(저점 매도)·오른 *뒤* 재레버(반등 놓침)=procyclical. ③ 헷지(숏/인버스)·익절·낙폭예측 신호 *없음*(설계상 — 그건 마켓타이밍=알파, 미해결).")

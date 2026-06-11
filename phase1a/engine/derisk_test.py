#!/usr/bin/env python3
"""PRAMANA — "내려갈 때 현금으로 빼기"(숏 아님) 룰 실증. 낙폭 줄이나, 휩쏘로 더 손해나?
변형: V5(현행) vs V5+추세게이트(SPY<200dMA면 노출↓=현금쪽) vs V5+vol게이트.
구간: 풀사이클·6개월(chop)·2020 COVID(V반등)·2022(지속 하락). 낙폭감소 vs 수익비용 정직 비교. cached SFP."""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import data
CAP=100_000_000; RF=0.05; TVOL=0.28; LMAX=2.0
etf=data.load("SFP_FUNDS",usecols=["ticker","date","closeadj"]).pivot_table(index="date",columns="ticker",values="closeadj").sort_index()
ret=etf.pct_change(); core=0.5*ret["SPY"]+0.5*ret["QQQ"]; rvol=core.rolling(20).std()*np.sqrt(252)
sma200=etf["SPY"].rolling(200).mean(); svol=etf["SPY"].pct_change().rolling(20).std()*np.sqrt(252)
alldays=etf.index[etf.index>=etf.index[210]]
def ddscale(dd): return 0.2 if dd<=-0.40 else 0.4 if dd<=-0.30 else 0.7 if dd<=-0.20 else 1.0
def run(days, gate=None):   # gate: None / 'trend'(200dMA<→현금) / 'vol'(고변동→현금)
    nav=[CAP]; peak=CAP
    for i in range(1,len(days)):
        d,p=days[i],days[i-1]; rv=rvol.get(p,np.nan)
        L=min(LMAX,TVOL/rv) if (pd.notna(rv) and rv>0) else 1.0; L*=ddscale(nav[-1]/peak-1)
        if gate=="trend" and pd.notna(sma200.get(p)) and etf["SPY"].get(p,0)<sma200.get(p): L*=0.25   # 추세 아래=현금쪽
        if gate=="vol"   and pd.notna(svol.get(p)) and svol.get(p)>0.25: L*=0.4                        # 고변동=뺀다
        nav.append(nav[-1]*(1+L*core.get(d,0)-(L-1)*RF/252)); peak=max(peak,nav[-1])
    return pd.Series(nav,index=days)
def stat(s): r=s.pct_change().dropna(); return s.iloc[-1]/s.iloc[0]-1,(s/s.cummax()-1).min(),(r.mean()/r.std()*np.sqrt(252) if r.std()>0 else float('nan'))
WIN={"풀사이클":alldays,"6개월(chop)":alldays[-126:],
     "2020 COVID(V반등)":alldays[(alldays>="2020-01-01")&(alldays<="2020-07-01")],
     "2022(지속하락)":alldays[(alldays>="2022-01-01")&(alldays<="2022-12-31")]}
print(f"\n{'='*86}\n'내려갈 때 현금으로 빼기' 실증 — 낙폭 줄이나 vs 휩쏘 비용 (숏 아님·노출↓)\n{'='*86}")
print(f"{'구간':<18}{'룰':<16}{'누적%':>9}{'MDD%':>8}{'Sharpe':>8}   {'vs 현행(누적/MDD)':>16}")
for wn,days in WIN.items():
    if len(days)<5: continue
    base=stat(run(days,None)); tr=stat(run(days,"trend")); vo=stat(run(days,"vol"))
    print(f"{wn:<18}{'V5 현행':<16}{base[0]*100:>8.1f}{base[1]*100:>8.0f}{base[2]:>8.2f}")
    print(f"{'':<18}{'+추세→현금':<16}{tr[0]*100:>8.1f}{tr[1]*100:>8.0f}{tr[2]:>8.2f}   {(tr[0]-base[0])*100:>+7.1f}%p/{(tr[1]-base[1])*100:>+5.0f}%p")
    print(f"{'':<18}{'+vol→현금':<16}{vo[0]*100:>8.1f}{vo[1]*100:>8.0f}{vo[2]:>8.2f}   {(vo[0]-base[0])*100:>+7.1f}%p/{(vo[1]-base[1])*100:>+5.0f}%p")
    print("-"*86)
print("읽는 법: MDD %p가 음수(-)면 낙폭 줄임(좋음), 누적 %p 음수면 수익 비용(휩쏘). 둘 트레이드오프.")
print("핵심 가설: 추세→현금은 2022(지속하락)선 낙폭 크게 줄이나, 6개월/COVID(반등)선 수익 깎임(휩쏘). = 공짜 아님.")

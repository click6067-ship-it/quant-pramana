#!/usr/bin/env python3
"""PRAMANA — 4-sleeve 분산북 실증 (Codex 스펙: Equity50/MF25/Gold15/Bonds10·레버≤1.25x).
질문: 큰 크래시(2022·2020) decorrelation을 *진짜* 줄이나? QQQ 대비 수익 비용? vs V6(85/15)·QQQ.
free yfinance(SPY/QQQ/DBMF/GLD/IEF·DBMF 2019~). paper·비용후."""
import os, sys, numpy as np, pandas as pd
CAP=100_000_000; RF=0.05; TVOL=0.28; LMAX_V6=1.5; MF_V6=0.15
import yfinance as yf
px=yf.download(["SPY","QQQ","DBMF","GLD","IEF"],period="max",interval="1d",auto_adjust=True,progress=False)
px=(px["Close"] if isinstance(px.columns,pd.MultiIndex) else px).dropna()
ret=px.pct_change(); core=0.5*ret["SPY"]+0.5*ret["QQQ"]; rvol=core.rolling(20).std()*np.sqrt(252)
days=core.dropna().index; days=days[days>=rvol.dropna().index[0]]
def ddscale(dd): return 0.2 if dd<=-0.40 else 0.4 if dd<=-0.30 else 0.7 if dd<=-0.20 else 1.0
# 4-sleeve 일별수익 (고정비중×레버, financing)
W={"core":0.50,"DBMF":0.25,"GLD":0.15,"IEF":0.10}   # Codex 스펙
def four_ret(d): return W["core"]*core.get(d,0)+W["DBMF"]*ret["DBMF"].get(d,0)+W["GLD"]*ret["GLD"].get(d,0)+W["IEF"]*ret["IEF"].get(d,0)
def run_four(days, L=1.0):
    nav=[CAP]
    for i in range(1,len(days)):
        r=L*four_ret(days[i])-(L-1)*RF/252; nav.append(nav[-1]*(1+r))
    return pd.Series(nav,index=days)
def run_v6(days):
    nav=[CAP]; peak=CAP
    for i in range(1,len(days)):
        d,p=days[i],days[i-1]; rv=rvol.get(p,np.nan)
        L=min(LMAX_V6,TVOL/rv) if (pd.notna(rv) and rv>0) else 1.0; L*=ddscale(nav[-1]/peak-1)
        nav.append(nav[-1]*(1+(1-MF_V6)*(L*core.get(d,0)-(L-1)*RF/252)+MF_V6*ret["DBMF"].get(d,0))); peak=max(peak,nav[-1])
    return pd.Series(nav,index=days)
def bh(s,days): return CAP*(1+ret[s].reindex(days).fillna(0)).cumprod()
def st(s): r=s.pct_change().dropna(); return s.iloc[-1]/s.iloc[0]-1,(s/s.cummax()-1).min(),(r.mean()/r.std()*np.sqrt(252) if r.std()>0 else float('nan'))
BOOKS=lambda dd:{"4-sleeve 1.0x":run_four(dd,1.0),"4-sleeve 1.25x":run_four(dd,1.25),"V6 (85/15·voltarget)":run_v6(dd),"QQQ":bh("QQQ",dd),"Equity(SPY/QQQ)":CAP*(1+core.reindex(dd).fillna(0)).cumprod()}
WIN={f"풀({days[0].date()}~)":days,"2022 bear":days[(days>="2022-01-01")&(days<="2022-12-31")],"2020 COVID":days[(days>="2020-01-01")&(days<="2020-07-01")],"2023 회복":days[(days>="2023-01-01")&(days<="2023-12-31")]}
print(f"\n{'='*78}\n4-sleeve 분산북 vs V6 vs QQQ — 큰 크래시 decorrelation 실증 · 비용후\n{'='*78}")
for wn,dd in WIN.items():
    if len(dd)<5: continue
    print(f"\n[{wn}]")
    print(f"  {'북':<24}{'누적%':>9}{'MDD%':>8}{'Sharpe':>8}")
    for nm,s in BOOKS(dd).items(): a=st(s); print(f"  {nm:<24}{a[0]*100:>8.1f}{a[1]*100:>8.0f}{a[2]:>8.2f}")
# 큰 크래시 상관(2022) — 4-sleeve가 QQQ와 얼마나 덜 같이 움직였나
seg=days[(days>="2022-01-01")&(days<="2022-12-31")]
c4=run_four(seg,1.0).pct_change(); cq=ret["QQQ"].reindex(seg); cv=run_v6(seg).pct_change()
print(f"\n2022 일간수익 QQQ 상관: 4-sleeve {c4.corr(cq):.2f} · V6 {cv.corr(cq):.2f} (낮을수록 '같이 안 맞음')")
print(f"\n핵심: 4-sleeve가 2022/2020 큰 낙폭 줄이나(equity 50%로↓), QQQ bull(2023)·풀사이클 수익 비용은? → '최대복리(QQQ) vs 크래시생존(4-sleeve)' 목적함수 선택.")

#!/usr/bin/env python3
"""PRAMANA — "같이 안 맞기" 파훼법 실증: V5 + managed futures(DBMF) sleeve.
Codex #1 = 현금 대신 *주식 추세하락 때 오르는* 자산(managed futures). 2022 주식+채권 동반하락 때 DBMF +21.5%.
질문: V5에 15% DBMF 넣으면 상관 낙폭(특히 2022) 실제로 줄나, 수익 비용은? free yfinance(DBMF 2019~)."""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
CAP=100_000_000; RF=0.05; TVOL=0.28; LMAX=2.0
import yfinance as yf
px=yf.download(["SPY","QQQ","DBMF"],period="max",interval="1d",auto_adjust=True,progress=False)
px=(px["Close"] if isinstance(px.columns,pd.MultiIndex) else px).dropna(how="all")
px=px.dropna()  # DBMF 시작(2019-05)부터 공통
ret=px.pct_change(); core=0.5*ret["SPY"]+0.5*ret["QQQ"]; rvol=core.rolling(20).std()*np.sqrt(252)
days=core.dropna().index; days=days[days>=rvol.dropna().index[0]]
def ddscale(dd): return 0.2 if dd<=-0.40 else 0.4 if dd<=-0.30 else 0.7 if dd<=-0.20 else 1.0
def run(days, lmax=LMAX, mf=0.0):   # mf = managed futures 비중(나머지=레버드 core)
    nav=[CAP]; peak=CAP
    for i in range(1,len(days)):
        d,p=days[i],days[i-1]; rv=rvol.get(p,np.nan)
        L=min(lmax,TVOL/rv) if (pd.notna(rv) and rv>0) else 1.0; L*=ddscale(nav[-1]/peak-1)
        core_r=L*core.get(d,0)-(L-1)*RF/252
        mf_r=ret["DBMF"].get(d,0.0)
        r=(1-mf)*core_r+mf*mf_r
        nav.append(nav[-1]*(1+r)); peak=max(peak,nav[-1])
    return pd.Series(nav,index=days)
def bh(sym,days): return CAP*(1+ret[sym].reindex(days).fillna(0)).cumprod()
def stat(s): r=s.pct_change().dropna(); return s.iloc[-1]/s.iloc[0]-1,(s/s.cummax()-1).min(),(r.mean()/r.std()*np.sqrt(252) if r.std()>0 else float('nan'))
WIN={f"풀({days[0].date()}~)":days,"2020 COVID":days[(days>="2020-01-01")&(days<="2020-07-01")],"2022 bear":days[(days>="2022-01-01")&(days<="2022-12-31")],"2023 회복":days[(days>="2023-01-01")&(days<="2023-12-31")]}
print(f"\n{'='*88}\n'같이 안 맞기' 실증: V5 + managed futures(DBMF) sleeve · free yfinance · DBMF {days[0].date()}~\n{'='*88}")
print(f"{'구간':<16}{'룰':<22}{'누적%':>9}{'MDD%':>8}{'Sharpe':>8}   {'vs V5(누적/MDD)':>15}")
for wn,dd in WIN.items():
    if len(dd)<5: continue
    base=stat(run(dd)); d15=stat(run(dd,mf=0.15)); d15l=stat(run(dd,lmax=1.5,mf=0.15)); qqq=stat(bh("QQQ",dd))
    print(f"{wn:<16}{'V5 (현행 2.0x)':<22}{base[0]*100:>8.1f}{base[1]*100:>8.0f}{base[2]:>8.2f}")
    print(f"{'':<16}{'+15% DBMF':<22}{d15[0]*100:>8.1f}{d15[1]*100:>8.0f}{d15[2]:>8.2f}   {(d15[0]-base[0])*100:>+6.1f}%p/{(d15[1]-base[1])*100:>+4.0f}%p")
    print(f"{'':<16}{'+15%DBMF+캡1.5x':<22}{d15l[0]*100:>8.1f}{d15l[1]*100:>8.0f}{d15l[2]:>8.2f}   {(d15l[0]-base[0])*100:>+6.1f}%p/{(d15l[1]-base[1])*100:>+4.0f}%p")
    print(f"{'':<16}{'(QQQ 참고)':<22}{qqq[0]*100:>8.1f}{qqq[1]*100:>8.0f}{qqq[2]:>8.2f}")
    print("-"*88)
print("읽는 법: MDD %p 음수=낙폭 줄임(좋음)·누적 %p 음수=수익 비용. DBMF가 2022선 낙폭 줄이고 2023(주식회복)선 드래그면 = Codex 예측대로 '공짜 아님'.")

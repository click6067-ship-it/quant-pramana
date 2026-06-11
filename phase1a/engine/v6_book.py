#!/usr/bin/env python3
"""PRAMANA V6 — Diversified Aggressive Book 후보 비교 (Codex가 스펙 결정할 데이터).
V5(레버드 Core) + managed-futures(DBMF) sleeve. 핵심 미정: vol-target vs *고정* 레버(6mo서 vol-target -6.3%p 손해)·DBMF 비중·레버캡.
변형 비교 + attribution(DBMF 기여). free yfinance(DBMF 2019~). paper·비용후."""
import os, sys, json, numpy as np, pandas as pd
CAP=100_000_000; RF=0.05; TVOL=0.28
import yfinance as yf
px=yf.download(["SPY","QQQ","DBMF"],period="max",interval="1d",auto_adjust=True,progress=False)
px=(px["Close"] if isinstance(px.columns,pd.MultiIndex) else px).dropna()
ret=px.pct_change(); core=0.5*ret["SPY"]+0.5*ret["QQQ"]; rvol=core.rolling(20).std()*np.sqrt(252)
days=core.dropna().index; days=days[days>=rvol.dropna().index[0]]
def ddscale(dd): return 0.2 if dd<=-0.40 else 0.4 if dd<=-0.30 else 0.7 if dd<=-0.20 else 1.0
def run(days, mode="voltarget", lev=1.5, cap=1.5, mf=0.0):
    nav=[CAP]; peak=CAP
    for i in range(1,len(days)):
        d,p=days[i],days[i-1]
        if mode=="voltarget":
            rv=rvol.get(p,np.nan); L=min(cap,TVOL/rv) if (pd.notna(rv) and rv>0) else 1.0; L*=ddscale(nav[-1]/peak-1)
        else: L=lev
        core_r=L*core.get(d,0)-(L-1)*RF/252
        r=(1-mf)*core_r+mf*ret["DBMF"].get(d,0.0)
        nav.append(nav[-1]*(1+r)); peak=max(peak,nav[-1])
    return pd.Series(nav,index=days)
def bh(s,days): return CAP*(1+ret[s].reindex(days).fillna(0)).cumprod()
def st(s): r=s.pct_change().dropna(); return s.iloc[-1]/s.iloc[0]-1,(s/s.cummax()-1).min(),(r.mean()/r.std()*np.sqrt(252) if r.std()>0 else float('nan'))
CANDS={"V5 (voltarget cap2.0·mf0)":dict(mode="voltarget",cap=2.0,mf=0.0),
       "v6A voltarget cap1.5·15%DBMF":dict(mode="voltarget",cap=1.5,mf=0.15),
       "v6B 고정1.5x·15%DBMF":dict(mode="fixed",lev=1.5,mf=0.15),
       "v6C 고정1.5x·mf0(baseline)":dict(mode="fixed",lev=1.5,mf=0.0),
       "v6D 고정1.5x·20%DBMF":dict(mode="fixed",lev=1.5,mf=0.20)}
WIN={f"풀({days[0].date()}~)":days,"2022 bear":days[(days>="2022-01-01")&(days<="2022-12-31")],
     "2020 COVID":days[(days>="2020-01-01")&(days<="2020-07-01")],"2023 회복":days[(days>="2023-01-01")&(days<="2023-12-31")]}
print(f"\n{'='*92}\nV6 후보 비교 — vol-target vs 고정레버 × DBMF · free yfinance DBMF {days[0].date()}~ · 비용후\n{'='*92}")
for wn,dd in WIN.items():
    if len(dd)<5: continue
    print(f"\n[{wn}]  (참고: QQQ {st(bh('QQQ',dd))[0]*100:+.0f}%/{st(bh('QQQ',dd))[1]*100:.0f}%MDD)")
    print(f"  {'후보':<30}{'누적%':>9}{'MDD%':>8}{'Sharpe':>8}")
    for nm,kw in CANDS.items():
        s=st(run(dd,**kw)); print(f"  {nm:<30}{s[0]*100:>8.1f}{s[1]*100:>8.0f}{s[2]:>8.2f}")
# 풀사이클 attribution + 추천 후보 요약
full=days; base=st(run(full,mode="fixed",lev=1.5,mf=0.0)); withmf=st(run(full,mode="fixed",lev=1.5,mf=0.15))
print(f"\nattribution(풀·고정1.5x): DBMF 15% 기여 = Sharpe {base[2]:.2f}→{withmf[2]:.2f}·MDD {base[1]*100:.0f}→{withmf[1]*100:.0f}%·누적 {base[0]*100:+.0f}→{withmf[0]*100:+.0f}%")
res={nm:{"win":{wn:[round(st(run(dd,**kw))[i],3) for i in range(3)] for wn,dd in WIN.items() if len(dd)>=5}} for nm,kw in CANDS.items()}
json.dump(res,open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","outputs","engine","v6_book.json"),"w"),indent=1)
print(f"\n핵심 결정(→Codex): ① vol-target 유지 vs 고정레버(6mo서 vol-target -6.3%p·여기 풀사이클도 비교) ② DBMF 15 vs 20% ③ 레버캡 1.5. → outputs/engine/v6_book.json")

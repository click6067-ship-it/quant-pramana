#!/usr/bin/env python3
"""PRAMANA — GPT V7 핵심 검증: Market Risk Score로 Growth↔Survival 전환이 *그냥 들고있기*를 이기나?
GPT 제안: 장좋을때 Growth(레버드 equity+DBMF), 나빠지면 Survival(4-sleeve)로 회피(risk score).
no-echo 검증: 이게 마켓타이밍이라 휩쏘하나? static Growth/static Survival/QQQ 대비. free yfinance."""
import os, sys, numpy as np, pandas as pd
CAP=100_000_000; RF=0.05; TVOL=0.28; LMAX=1.5; MF=0.15
import yfinance as yf
px=yf.download(["SPY","QQQ","DBMF","GLD","IEF"],period="max",interval="1d",auto_adjust=True,progress=False)
px=(px["Close"] if isinstance(px.columns,pd.MultiIndex) else px).dropna()
ret=px.pct_change(); core=0.5*ret["SPY"]+0.5*ret["QQQ"]; rvol=core.rolling(20).std()*np.sqrt(252)
sma200=px["SPY"].rolling(200).mean(); svol=px["SPY"].pct_change().rolling(20).std()*np.sqrt(252)
spypk=px["SPY"]/px["SPY"].cummax()-1
days=core.dropna().index; days=days[days>=sma200.dropna().index[0]]
W4={"core":0.50,"DBMF":0.25,"GLD":0.15,"IEF":0.10}
def four_r(d): return W4["core"]*core.get(d,0)+W4["DBMF"]*ret["DBMF"].get(d,0)+W4["GLD"]*ret["GLD"].get(d,0)+W4["IEF"]*ret["IEF"].get(d,0)
def ddscale(dd): return 0.2 if dd<=-0.40 else 0.4 if dd<=-0.30 else 0.7 if dd<=-0.20 else 1.0
def risk_score(p):  # 사전정의·후행 신호 합산 (GPT Market Risk Score 축소판)
    s=0
    if pd.notna(sma200.get(p)) and px["SPY"].get(p,0)<sma200.get(p): s+=1   # 200일선 아래
    if pd.notna(svol.get(p)) and svol.get(p)>0.22: s+=1                      # 변동성 급등
    if pd.notna(spypk.get(p)) and spypk.get(p)<-0.10: s+=1                   # 낙폭 -10% 진입
    return s
def wgrowth(s): return {0:1.0,1:0.66,2:0.33}.get(s,0.0)   # score↑→Growth 비중↓(Survival↑)
def run(days, mode):   # mode: 'switch' / 'growth'(V6) / 'survival'(4-sleeve)
    nav=[CAP]; peak=CAP
    for i in range(1,len(days)):
        d,p=days[i],days[i-1]; rv=rvol.get(p,np.nan)
        L=min(LMAX,TVOL/rv) if (pd.notna(rv) and rv>0) else 1.0; L*=ddscale(nav[-1]/peak-1)
        growth=(1-MF)*(L*core.get(d,0)-(L-1)*RF/252)+MF*ret["DBMF"].get(d,0)
        surv=four_r(d)
        if mode=="growth": r=growth
        elif mode=="survival": r=surv
        else: wg=wgrowth(risk_score(p)); r=wg*growth+(1-wg)*surv
        nav.append(nav[-1]*(1+r)); peak=max(peak,nav[-1])
    return pd.Series(nav,index=days)
def bh(s,days): return CAP*(1+ret[s].reindex(days).fillna(0)).cumprod()
def st(s): r=s.pct_change().dropna(); return s.iloc[-1]/s.iloc[0]-1,(s/s.cummax()-1).min(),(r.mean()/r.std()*np.sqrt(252) if r.std()>0 else float('nan'))
WIN={f"풀({days[0].date()}~)":days,"2022 bear":days[(days>="2022-01-01")&(days<="2022-12-31")],"2020 COVID":days[(days>="2020-01-01")&(days<="2020-07-01")],"2023 회복":days[(days>="2023-01-01")&(days<="2023-12-31")]}
print(f"\n{'='*80}\nGPT V7 검증: Market Risk Score 전환(switch) vs 그냥 들고있기 · 비용후\n{'='*80}")
for wn,dd in WIN.items():
    if len(dd)<5: continue
    print(f"\n[{wn}]")
    print(f"  {'전략':<28}{'누적%':>9}{'MDD%':>8}{'Sharpe':>8}")
    for nm,m in [("Risk-Score 전환(GPT)","switch"),("static Growth(V6)","growth"),("static Survival(4-sleeve)","survival")]:
        a=st(run(dd,m)); print(f"  {nm:<28}{a[0]*100:>8.1f}{a[1]*100:>8.0f}{a[2]:>8.2f}")
    aq=st(bh("QQQ",dd)); print(f"  {'QQQ(참고)':<28}{aq[0]*100:>8.1f}{aq[1]*100:>8.0f}{aq[2]:>8.2f}")
print(f"\n핵심 질문: 전환(switch)이 static Survival(4-sleeve)을 *위험조정으로* 이기나? 못 이기면 = 타이밍이 휩쏘로 값어치 못 함 → 그냥 4-sleeve 들고있는 게 정직.")

#!/usr/bin/env python3
"""PRAMANA Alpha Lab MT-1 — Daily Re-entry Ladder (사전등록 MT1_Daily_Reentry_Ladder_Protocol.md).
질문: 4-sleeve 코어 유지 + QQQ overlay를 *단계적 ladder*로 조절하면 binary throttle보다·static보다 나은가?
코어 전환 아님(overlay만)·next-bar·휩쏘 비용 포함. prior 낮음(regime_switch 단계적·throttle binary 각각 죽음). free yfinance·proxy."""
import os, warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, yfinance as yf
CAP=1e8; RF=0.05; OV_MAX=0.50; COST=0.0010  # overlay 상한·turnover 10bp (고정)
W4={"eq":0.50,"mf":0.25,"gold":0.15,"bond":0.10}
LAD={0:1.0,1:0.66,2:0.33,3:0.0}; BIN={0:1.0}   # ladder vs binary scale (고정·재사용)
def dl(ts):
    d=yf.download(ts,period="max",interval="1d",auto_adjust=True,progress=False)
    return (d["Close"] if isinstance(d.columns,pd.MultiIndex) else d).dropna(how="all")
A=dl(["SPY","QQQ","DBMF","GLD","IEF"]); rA=A.pct_change(); eqA=0.5*rA["SPY"]+0.5*rA["QQQ"]
fourA=W4["eq"]*eqA+W4["mf"]*rA["DBMF"]+W4["gold"]*rA["GLD"]+W4["bond"]*rA["IEF"]
sma200=A["SPY"].rolling(200).mean(); svol=A["SPY"].pct_change().rolling(20).std()*np.sqrt(252)
spydd=A["SPY"]/A["SPY"].cummax()-1
def score(p):
    s=0
    if pd.notna(sma200.get(p)) and A["SPY"].get(p,0)<sma200.get(p): s+=1
    if pd.notna(svol.get(p)) and svol.get(p)>0.22: s+=1
    if pd.notna(spydd.get(p)) and spydd.get(p)<-0.10: s+=1
    return s
def ov_of(mode,sc):
    if mode=="qqq": return 1.0
    if mode=="four": return 0.0
    if mode=="binary": return OV_MAX*BIN.get(sc,0.0)
    return OV_MAX*LAD.get(sc,0.0)  # ladder
def run(days, mode, four, qqq):
    nav=[CAP]; ovp=0.0; tot_to=0.0
    for i in range(1,len(days)):
        d,p=days[i],days[i-1]; ov=ov_of(mode,score(p))   # next-bar
        r=(1-ov)*four.get(d,0)+ov*qqq.get(d,0)-COST*abs(ov-ovp)
        tot_to+=abs(ov-ovp); nav.append(nav[-1]*(1+r)); ovp=ov
    return pd.Series(nav,index=days), tot_to/max(len(days)/252,1)
def stat(nav):
    r=nav.pct_change().dropna(); m=(nav/nav.cummax()-1).min()
    uw=(nav<nav.cummax()).astype(int); best=cur=0
    for v in uw: cur=cur+1 if v else 0; best=max(best,cur)
    return nav.iloc[-1]/nav.iloc[0]-1, m, (r.mean()/r.std()*np.sqrt(252) if r.std()>0 else float('nan')), best
MODES=[("static QQQ","qqq"),("static 4-sleeve","four"),("binary throttle","binary"),("MT-1 ladder","ladder")]
def block(title,days,four,qqq):
    print(f"\n[{title}]  n={len(days)}")
    print(f"  {'북':<20}{'누적%':>8}{'MDD%':>7}{'Sharpe':>8}{'UW일':>7}{'turn/yr':>8}")
    out={}
    for nm,m in MODES:
        nav,to=run(days,m,four,qqq); a=stat(nav); out[m]=a
        print(f"  {nm:<20}{a[0]*100:>8.1f}{a[1]*100:>7.0f}{a[2]:>8.2f}{a[3]:>7.0f}{to:>8.1f}")
    return out
print("="*78); print("MT-1 Daily Re-entry Ladder — 단계적 overlay vs binary vs static (비용후·prior 낮음)"); print("="*78)
dA=fourA.dropna().index
full=block(f"트랙 A 풀 ({dA[0].date()}~)",dA,fourA,rA["QQQ"])
for nm,a,b in [("2020 COVID","2020-01-01","2020-07-01"),("2022 bear","2022-01-01","2022-12-31")]:
    seg=dA[(dA>=a)&(dA<=b)]; block(f"트랙 A · {nm}",seg,fourA,rA["QQQ"])
# 트랙 B proxy (2008/2000) — four=proxy, overlay=실 QQQ
B=dl(["VFINX","RYMFX","GC=F","VFITX"]); rB=B.pct_change()
def fourB(idx,mfc):
    eq=rB["VFINX"].reindex(idx).fillna(0); mf=(rB[mfc].reindex(idx).fillna(0) if mfc else pd.Series(0.0,index=idx))
    return W4["eq"]*eq+W4["mf"]*mf+W4["gold"]*rB["GC=F"].reindex(idx).fillna(0)+W4["bond"]*rB["VFITX"].reindex(idx).fillna(0)
allB=B.dropna(how="all").index
for title,a,b,mfc in [("B-2008 GFC (proxy·overlay=QQQ)","2007-10-01","2009-12-31","RYMFX"),("B-2000 닷컴 (MF=cash·overlay=QQQ)","2000-01-01","2002-12-31",None)]:
    seg=allB[(allB>=a)&(allB<=b)]; seg=seg[pd.notna(B["VFINX"].reindex(seg))&pd.notna(A["QQQ"].reindex(seg))]
    if len(seg)<20: print(f"\n[{title}] skip"); continue
    block(title,seg,fourB(seg,mfc),rA["QQQ"])
# 사전등록 판정 (풀 기준)
print(f"\n{'='*78}\n사전등록 판정 (kill = ladder가 static 4-sleeve Sharpe 못이김 OR binary보다 안나음):")
l=full["ladder"]; s4=full["four"]; bi=full["binary"]; q=full["qqq"]
print(f"  ladder Sharpe {l[2]:.2f} vs static 4-sleeve {s4[2]:.2f} → {'PASS(이김)' if l[2]>s4[2] else 'FAIL(못이김)'}")
print(f"  ladder Sharpe {l[2]:.2f} vs binary throttle {bi[2]:.2f} → {'단계적 우위' if l[2]>bi[2] else 'binary와 동급/열위'}")
print(f"  ladder MDD {l[1]*100:.0f}% vs static 4-sleeve {s4[1]*100:.0f}% · QQQ {q[1]*100:.0f}%")
verdict="SURVIVE→2단계(ORB/VWAP/RVOL 센서)" if (l[2]>s4[2] and l[2]>bi[2]) else "DEAD→마켓타이밍 닫고 V7 생존코어 확정(4번째 negative)"
print(f"\n→ {verdict}")
print(f"\n정직: prior 낮음(regime_switch 단계적·throttle binary 각각 죽음)·proxy·in-sample·후행신호 본질(늦음/휩쏘)은 ladder로도 안 풀릴 수 있음.")
if __name__=="__main__": pass

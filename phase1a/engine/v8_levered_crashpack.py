#!/usr/bin/env python3
"""PRAMANA V8 Candidate — Levered 4-sleeve crash-pack (사전등록 V8_Candidate_Levered4sleeve_Protocol.md).
질문: V7 분산북을 레버(1.25~1.5x)하면 상승참여↑ 유지하며 crash MDD가 A1 Aggressive(-35%) 이내인가?
알파 아님=분산 프리미엄 레버=목적함수 이동. cap은 crash-loss budget으로(CAGR 아님·V5 교훈). free yfinance·proxy."""
import os, warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, yfinance as yf
RF=0.05; W4={"eq":0.50,"mf":0.25,"gold":0.15,"bond":0.10}; GRID=[1.0,1.10,1.15,1.20,1.25,1.35,1.5]; MDD_LIMIT=-0.35
def dl(ts):
    d=yf.download(ts,period="max",interval="1d",auto_adjust=True,progress=False)
    return (d["Close"] if isinstance(d.columns,pd.MultiIndex) else d).dropna(how="all")
A=dl(["SPY","QQQ","DBMF","GLD","IEF"]); rA=A.pct_change(); eqA=0.5*rA["SPY"]+0.5*rA["QQQ"]
fourA=W4["eq"]*eqA+W4["mf"]*rA["DBMF"]+W4["gold"]*rA["GLD"]+W4["bond"]*rA["IEF"]
dA=fourA.dropna().index
B=dl(["VFINX","RYMFX","GC=F","VFITX","VUSTX"]); rB=B.pct_change()
def sl(idx,col): return (rB[col].reindex(idx).fillna(0) if col in rB else pd.Series(0.0,index=idx))
def slA(idx,col): return (rA[col].reindex(idx).fillna(0) if col in rA else pd.Series(0.0,index=idx))
def fourB(idx,eq_src,mfc,goldc,bondc):  # Codex #2: equity를 VFINX 단일 아니라 실 SPY/QQQ 50/50(2000/2008 QQQ -78% tail 반영)
    eq=(0.5*slA(idx,"SPY")+0.5*slA(idx,"QQQ")) if eq_src=="spyqqq" else rB["VFINX"].reindex(idx).fillna(0)
    return (W4["eq"]*eq+W4["mf"]*(sl(idx,mfc) if mfc else pd.Series(0.0,index=idx))
            +W4["gold"]*(sl(idx,goldc) if goldc else pd.Series(0.0,index=idx))+W4["bond"]*sl(idx,bondc))
def lev(four,L): return L*four-(L-1)*RF/252
def stat(four,idx):
    out={}
    for L in GRID:
        n=(1+lev(four.reindex(idx).fillna(0),L)).cumprod()
        m=(n/n.cummax()-1).min(); tot=n.iloc[-1]/n.iloc[0]-1
        uwv=(n<n.cummax()).astype(int); best=cur=0
        for v in uwv: cur=cur+1 if v else 0; best=max(best,cur)
        out[L]=(tot,m,best)
    return out
def show(title,four,idx):
    print(f"\n[{title}]  n={len(idx)}")
    print(f"  {'레버':<8}{'누적%':>9}{'MDD%':>8}{'UW일':>7}")
    s=stat(four,idx)
    for L in GRID: a=s[L]; print(f"  {L:.2f}x{'':<3}{a[0]*100:>9.1f}{a[1]*100:>8.0f}{a[2]:>7.0f}")
    return {L:stat(four,idx)[L][1] for L in GRID}   # MDD per L
print("="*82); print("V8 Candidate — Levered 4-sleeve crash-pack (proxy·stress·알파 아님=분산 레버·목적함수 이동)"); print("="*82)
worst={L:0.0 for L in GRID}
# 트랙 A 실증
show("트랙 A 실증 2019~ (실 ETF·풀)",fourA,dA)
for nm,a,b in [("2020 COVID","2020-01-01","2020-07-01"),("2022 bear","2022-01-01","2022-12-31")]:
    seg=dA[(dA>=a)&(dA<=b)]; m=show(f"트랙 A · {nm}",fourA,seg)
    for L in GRID: worst[L]=min(worst[L],m[L])
# 트랙 B proxy
allB=B.dropna(how="all").index
for title,a,b,eqs,mfc,goldc,bondc in [("2008 GFC (eq=실SPY/QQQ·MF=RYMFX)","2007-10-01","2009-12-31","spyqqq","RYMFX","GC=F","VFITX"),
                                   ("2000 닷컴 (eq=실SPY/QQQ·MF=cash)","2000-01-01","2002-12-31","spyqqq",None,"GC=F","VFITX"),
                                   ("1987 (eq=VFINX·Black Monday)","1987-01-01","1988-06-30","vfinx",None,None,"VUSTX")]:
    seg=allB[(allB>=a)&(allB<=b)]; seg=seg[pd.notna(B["VFINX"].reindex(seg))]
    if len(seg)<20: print(f"\n[{title}] skip"); continue
    fb=fourB(seg,eqs,mfc,goldc,bondc); m=show(f"트랙 B · {title}",fb,seg)
    for L in GRID: worst[L]=min(worst[L],m[L])
# upside/downside capture (2019~ A·월별·QQQ 기준 · fourA 유효기간 dA로 정렬)
qd=rA["QQQ"].reindex(dA); mq=(1+qd).resample("ME").prod()-1; up=mq>0; dn=mq<=0
print(f"\n[상승/하락 참여 (2019~·월별·QQQ 기준)]")
print(f"  {'레버':<8}{'상승참여%':>10}{'하락참여%':>10}")
cap_up={}
for L in GRID:
    mf=(1+lev(fourA.reindex(dA),L)).resample("ME").prod()-1
    u=mf[up].mean()/mq[up].mean()*100; d=mf[dn].mean()/mq[dn].mean()*100; cap_up[L]=u
    print(f"  {L:.2f}x{'':<3}{u:>10.0f}{d:>10.0f}")
# 사전등록 판정
print(f"\n{'='*82}\n사전등록 판정 (worst-crash MDD ≤ {MDD_LIMIT*100:.0f}% AND 상승참여 > V7 1.0x={cap_up[1.0]:.0f}%):")
base_up=cap_up[1.0]; passed=[]
for L in GRID:
    ok_mdd=worst[L]>=MDD_LIMIT; ok_up=cap_up[L]>base_up or L==1.0
    verdict="PASS" if (ok_mdd and (L==1.0 or cap_up[L]>base_up)) else "FAIL"
    if L>1.0 and ok_mdd and cap_up[L]>base_up: passed.append(L)
    print(f"  {L:.2f}x: worst-crash MDD {worst[L]*100:>5.0f}% ({'≤-35 OK' if ok_mdd else '>-35 FAIL=레버꼬리'})·상승참여 {cap_up[L]:.0f}% → {verdict}")
if passed:
    best=max(passed); print(f"\n→ 통과 L: {passed} · 최고={best:.2f}x = **V8 Paper Core Candidate 승격 후보**(상승참여 {cap_up[best]:.0f}%·worst MDD {worst[best]*100:.0f}%)")
else:
    print(f"\n→ 모든 L>1.0이 worst-crash MDD > -35% = 레버 실패 → **V7 1.0x 유지(V8 기각)**")
print(f"\n정직: proxy·in-sample(2019~ benign·2008도 proxy)·forward MDD 더 클 수 있음(V5 -70%+ 꼬리). 통과해도 paper·Promotion Gates 전 실자본 금지.")
if __name__=="__main__": pass

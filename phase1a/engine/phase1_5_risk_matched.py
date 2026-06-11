#!/usr/bin/env python3
"""PRAMANA V4 — Phase 1.5: risk-matched 비교 (Phase 1의 공정성 보정).
Phase 1은 동일 notional(70/25/5 vs 100% core)이라 위성을 과소평가했을 수 있음.
공격형의 올바른 질문: '같은 리스크(vol 또는 MDD)에서 누가 더 버나?'
Sharpe 높은 쪽이 동일 리스크서 수익 이김(return≈Sharpe×vol). 레버에 financing 비용(rf~5%) 반영.
paper·비용후. dashboard/phase1과 동일 데이터·추세로직."""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import data
CAP=100_000_000; RF=0.05  # 레버 financing 연 5%
etf=data.load("SFP_FUNDS",usecols=["ticker","date","closeadj"]).pivot_table(index="date",columns="ticker",values="closeadj").sort_index()
TT=[c for c in ["SPY","QQQ","IWM","DIA","XLK","XLF","XLE","XLV","XLI","XLY","XLP","XLU","XLB","XLRE","XLC"] if c in etf.columns]
LETF_MAP={"QQQ":"TQQQ","SPY":"UPRO"}; LETF=[LETF_MAP[u] for u in LETF_MAP if LETF_MAP[u] in etf.columns]
ret=etf.pct_change(); sma=etf.rolling(200).mean(); spyvol=etf["SPY"].pct_change().rolling(20).std()*np.sqrt(252)
days=etf.index[etf.index>=etf.index[210]]
WC,WT,WL=0.70,0.25,0.05; BPS=10
def tstate(d):
    a=etf.loc[d]; s=sma.loc[d]; on=[c for c in TT if pd.notna(s[c]) and a[c]>s[c]]
    reg=0.5 if (pd.notna(spyvol.get(d)) and spyvol[d]>0.22) else 1.0
    lon=[LETF_MAP[u] for u in LETF_MAP if u in on and LETF_MAP[u] in etf.columns]; return on,lon,reg
core_r,cs_r=[],[]; prev=None
for i,d in enumerate(days):
    if i==0: core_r.append(0);cs_r.append(0);continue
    p=days[i-1]; on,lon,reg=tstate(p)
    cr=0.5*ret.loc[d,"SPY"]+0.5*ret.loc[d,"QQQ"]
    tr=(ret.loc[d,on].mean()*reg) if on else 0.0; lr=(ret.loc[d,lon].mean()*reg) if lon else 0.0
    c=0.0
    if prev is not None:
        c=len(set(on)^set(prev[0]))/max(1,len(TT))*WT*BPS/1e4+(len(set(lon)^set(prev[1]))/max(1,len(LETF))*WL*BPS/1e4 if LETF else 0)
    core_r.append(cr); cs_r.append(WC*cr+WT*tr+WL*lr-c); prev=(on,lon)
S=pd.DataFrame({"SPY":ret["SPY"].reindex(days).fillna(0),"Core":core_r,"CoreSat":cs_r},index=days)
def lever(s,L): return L*s-(L-1)*RF/252                       # financing 반영
def navstat(s):
    n=CAP*(1+s).cumprod(); r=s.dropna(); yrs=(n.index[-1]-n.index[0]).days/365.25
    tot=n.iloc[-1]/CAP-1; cagr=(1+tot)**(1/yrs)-1 if yrs>0 and tot>-1 else float("nan")
    return cagr,(n/n.cummax()-1).min(),(r.mean()/r.std()*np.sqrt(252) if r.std()>0 else float("nan"))
def vol(s): return s.std()*np.sqrt(252)
def mdd_of(s,L): n=(1+lever(s,L)).cumprod(); return (n/n.cummax()-1).min()
def lever_to_mdd(s,target=-0.35):
    lo,hi=0.1,8.0
    for _ in range(40):
        m=(lo+hi)/2
        if mdd_of(s,m)<target: hi=m
        else: lo=m
    return (lo+hi)/2

print(f"\n{'='*78}\nPHASE 1.5 — risk-matched (위성이 *동일 리스크*에서 보태나?) 비용후·financing 5%\n{'='*78}")
# (A) 동일 변동성 = Core의 vol에 맞춰 레버
vc=vol(S["Core"])
print(f"\n[A] 동일 변동성(target = Core vol {vc*100:.1f}%/yr)으로 레버 맞춤:")
print(f"{'포트':<10}{'레버':>6}{'CAGR%':>9}{'MDD%':>8}{'Sharpe':>8}")
for nm in ["SPY","Core","CoreSat"]:
    L=vc/vol(S[nm]); cg,md,sh=navstat(lever(S[nm],L)); print(f"{nm:<10}{L:>6.2f}{cg*100:>8.2f}{md*100:>8.1f}{sh:>8.2f}")
# (B) 동일 MDD budget = -35%로 레버
print(f"\n[B] 동일 낙폭예산(target MDD = -35%)으로 레버:")
print(f"{'포트':<10}{'레버':>6}{'CAGR%':>9}{'MDD%':>8}{'Sharpe':>8}")
res={}
for nm in ["SPY","Core","CoreSat"]:
    L=lever_to_mdd(S[nm],-0.35); cg,md,sh=navstat(lever(S[nm],L)); res[nm]=(L,cg,md,sh)
    print(f"{nm:<10}{L:>6.2f}{cg*100:>8.2f}{md*100:>8.1f}{sh:>8.2f}")
print(f"\n판정: 동일 -35% 낙폭에서 CAGR — CoreSat {res['CoreSat'][1]*100:.1f}% vs Core {res['Core'][1]*100:.1f}% vs SPY {res['SPY'][1]*100:.1f}%")
diff=(res['CoreSat'][1]-res['Core'][1])*100
print(f"  → 위성 risk-matched 기여 = {diff:+.2f}%p/yr CAGR " + ("(양수=위성이 동일리스크서 보탬·Phase1 결론 부분반전)" if diff>0 else "(여전히 못 보탬)"))
print(f"  주의: 차이가 작으면(<~1%p) Sharpe +0.03 노이즈와 일관 = '한계적'이지 대박 아님.")

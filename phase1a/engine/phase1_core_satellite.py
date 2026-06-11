#!/usr/bin/env python3
"""PRAMANA V4 — Phase 1 최소 테스트: Core 위에 trend/LETF 위성이 '진짜' 보태나?
질문 하나: SPY/QQQ core를 그냥 드는 것 vs core+trend+LETF 위성. 비용후·낙폭후.
모델 없음·최적화 없음·고정비중. 부품 4개(core/trend/letf/고정allocator) + attribution.
paper·gross 아님(turnover 비용)·LEV=1(레버는 알파질문 아님). dashboard.py와 동일 데이터/추세로직."""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import data
CAP=100_000_000
etf=data.load("SFP_FUNDS",usecols=["ticker","date","closeadj"]).pivot_table(index="date",columns="ticker",values="closeadj").sort_index()
TT=[c for c in ["SPY","QQQ","IWM","DIA","XLK","XLF","XLE","XLV","XLI","XLY","XLP","XLU","XLB","XLRE","XLC"] if c in etf.columns]
LETF_MAP={"QQQ":"TQQQ","SPY":"UPRO"}; LETF=[LETF_MAP[u] for u in LETF_MAP if LETF_MAP[u] in etf.columns]
ret=etf.pct_change(); sma=etf.rolling(200).mean(); spyvol=etf["SPY"].pct_change().rolling(20).std()*np.sqrt(252)
days=etf.index[etf.index>=etf.index[210]]
WC,WT,WL=0.70,0.25,0.05  # 고정 allocator: core 70 / trend 25 / LETF 5
BPS_T,BPS_L=10,10        # 위성 turnover 비용(bp, 왕복)

def trend_state(d):
    a=etf.loc[d]; s=sma.loc[d]; on=[c for c in TT if pd.notna(s[c]) and a[c]>s[c]]
    reg=0.5 if (pd.notna(spyvol.get(d)) and spyvol[d]>0.22) else 1.0
    lon=[LETF_MAP[u] for u in LETF_MAP if u in on and LETF_MAP[u] in etf.columns]
    return on,lon,reg
# 일별 sleeve 수익 (next-bar: 어제 상태로 오늘 수익)
core_r,trend_r,letf_r=[],[],[]; prev_on=prev_lon=None; tcost=[]
for i,d in enumerate(days):
    if i==0: core_r.append(0);trend_r.append(0);letf_r.append(0);tcost.append(0);continue
    p=days[i-1]; on,lon,reg=trend_state(p)            # 어제 종가 상태
    cr=0.5*ret.loc[d,"SPY"]+0.5*ret.loc[d,"QQQ"]       # core SPY/QQQ 50/50
    tr=(ret.loc[d,on].mean()*reg) if on else 0.0       # trend: ON 동일가중×regime, 없으면 현금(0)
    lr=(ret.loc[d,lon].mean()*reg) if lon else 0.0     # LETF dose
    core_r.append(cr); trend_r.append(tr); letf_r.append(lr)
    # 위성 turnover 비용(ON집합 바뀐 날)
    c=0.0
    if prev_on is not None:
        c+=len(set(on)^set(prev_on))/max(1,len(TT))*WT*BPS_T/1e4
        c+=len(set(lon)^set(prev_lon))/max(1,len(LETF))*WL*BPS_L/1e4 if LETF else 0
    tcost.append(c); prev_on,prev_lon=on,lon
df=pd.DataFrame({"core":core_r,"trend":trend_r,"letf":letf_r,"tcost":tcost},index=days)
# 포트폴리오들
df["SPY"]=ret["SPY"].reindex(days).fillna(0)
df["Core5050"]=df["core"]
df["CoreSat"]=WC*df["core"]+WT*df["trend"]+WL*df["letf"]-df["tcost"]
def nav(s): return CAP*(1+s).cumprod()
def stats(s):
    n=nav(s); r=s.dropna(); yrs=(n.index[-1]-n.index[0]).days/365.25
    tot=n.iloc[-1]/CAP-1; cagr=(1+tot)**(1/yrs)-1 if yrs>0 and tot>-1 else float("nan")
    mdd=(n/n.cummax()-1).min(); sh=r.mean()/r.std()*np.sqrt(252) if r.std()>0 else float("nan")
    return tot,cagr,mdd,sh
end=days[-1]; ANCH=[("3M",95),("6M",190),("1Y",370),("FULL",None)]
print(f"\n{'='*86}\nPHASE 1 — Core 위에 위성이 보태나? (비용후·LEV1·고정 70/25/5)  끝 {end.date()}\n{'='*86}")
print(f"{'기간':<6}{'포트':<14}{'누적%':>9}{'CAGR%':>8}{'MDD%':>8}{'Sharpe':>8}   {'위성기여(vs Core)':>16}")
rows=[]
for nm,dd in ANCH:
    start=end-pd.Timedelta(days=dd) if dd else days[0]
    seg=df[df.index>=start]
    s_core=stats(seg["Core5050"]); s_cs=stats(seg["CoreSat"]); s_spy=stats(seg["SPY"])
    for lab,st in [("SPY",s_spy),("Core 50/50",s_core),("Core+Trend+LETF",s_cs)]:
        contrib = (s_cs[0]-s_core[0])*100 if lab=="Core+Trend+LETF" else None
        print(f"{nm:<6}{lab:<16}{st[0]*100:>7.2f}{st[1]*100:>8.2f}{st[2]*100:>8.1f}{st[3]:>8.2f}"+(f"   {contrib:>+13.2f}%p" if contrib is not None else ""))
        rows.append(dict(anchor=nm,port=lab,tot=st[0],cagr=st[1],mdd=st[2],sharpe=st[3]))
    print("-"*86)
ENG=os.path.join(data.PHASE1A,"outputs","engine"); os.makedirs(ENG,exist_ok=True)
pd.DataFrame(rows).to_csv(os.path.join(ENG,"phase1_core_satellite.csv"),index=False)
# FULL 판정 요약
seg=df; sc=stats(seg["Core5050"]); scs=stats(seg["CoreSat"]); ssp=stats(seg["SPY"])
print(f"\n판정(FULL {((end-days[0]).days/365.25):.1f}년):")
print(f"  위성 순기여 = CoreSat − Core = {(scs[0]-sc[0])*100:+.1f}%p 누적, MDD {scs[2]*100:.1f}% vs Core {sc[2]*100:.1f}%")
verdict = "위성이 보탬(낙폭↓ 또는 수익↑)" if (scs[3]>sc[3] or scs[2]>sc[2]*1.0 and scs[0]>sc[0]) else "위성이 비용후 못 보탬 → 그냥 Core 보유가 나음"
print(f"  Sharpe: Core {sc[3]:+.2f} / CoreSat {scs[3]:+.2f} / SPY {ssp[3]:+.2f}  → {verdict}")
print(f"  → outputs/engine/phase1_core_satellite.csv")

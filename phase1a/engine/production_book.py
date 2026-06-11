#!/usr/bin/env python3
"""PRAMANA V4 — Production "Core Beta Forward Book" (정직 명명: 알파북 아님).
정체 = SPY/QQQ 베타 + (선택적) 가벼운 trend 오버레이를, A1 MDD 시나리오에 맞춰 레버(financing).
Core>SPY는 QQQ 틸트(레짐)지 알파 아님(LOCK C6). attribution으로 오버레이 한계기여 정직 분해.
A1 3시나리오(−20/−35/−50) 전부 산출 → 실제 자본 정해지면 행 선택. 현재 타깃(forward용) JSON.
paper·비용후·next-bar. cached Sharadar(SFP_FUNDS). dashboard/phase1_5와 동일 데이터·추세로직."""
import os, sys, json, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import data
CAP=100_000_000; RF=0.05; ENG=os.path.join(data.PHASE1A,"outputs","engine"); os.makedirs(ENG,exist_ok=True)
etf=data.load("SFP_FUNDS",usecols=["ticker","date","closeadj"]).pivot_table(index="date",columns="ticker",values="closeadj").sort_index()
TT=[c for c in ["SPY","QQQ","IWM","DIA","XLK","XLF","XLE","XLV","XLI","XLY","XLP","XLU","XLB","XLRE","XLC"] if c in etf.columns]
ret=etf.pct_change(); sma=etf.rolling(200).mean(); spyvol=etf["SPY"].pct_change().rolling(20).std()*np.sqrt(252)
days=etf.index[etf.index>=etf.index[210]]
OVERLAY_W=0.15   # 선택적 가벼운 trend 오버레이 비중(Core 0.85). Phase1.5=노이즈라 작게.

def trend_on(d):
    a=etf.loc[d]; s=sma.loc[d]; on=[c for c in TT if pd.notna(s[c]) and a[c]>s[c]]
    reg=0.5 if (pd.notna(spyvol.get(d)) and spyvol[d]>0.22) else 1.0; return on,reg
# 일별 sleeve 수익
core_r,ov_r,tcost=[],[],[]; prev=None
for i,d in enumerate(days):
    if i==0: core_r.append(0);ov_r.append(0);tcost.append(0);continue
    p=days[i-1]; on,reg=trend_on(p)
    core_r.append(0.5*ret.loc[d,"SPY"]+0.5*ret.loc[d,"QQQ"])
    ov_r.append(ret.loc[d,on].mean()*reg if on else 0.0)
    tcost.append(len(set(on)^set(prev))/max(1,len(TT))*OVERLAY_W*10/1e4 if prev is not None else 0); prev=on
df=pd.DataFrame({"core":core_r,"ov":ov_r,"tc":tcost},index=days)
df["CoreOnly"]=df["core"]
df["CoreOverlay"]=(1-OVERLAY_W)*df["core"]+OVERLAY_W*df["ov"]-df["tc"]
df["SPY"]=ret["SPY"].reindex(days).fillna(0)
def lever(s,L): return L*s-(L-1)*RF/252
def stat(s):
    n=CAP*(1+s).cumprod(); r=s.dropna(); yrs=(n.index[-1]-n.index[0]).days/365.25
    tot=n.iloc[-1]/CAP-1; cagr=(1+tot)**(1/yrs)-1 if yrs>0 and tot>-1 else float("nan")
    return cagr,(n/n.cummax()-1).min(),(r.mean()/r.std()*np.sqrt(252) if r.std()>0 else float("nan"))
def mdd(s,L): n=(1+lever(s,L)).cumprod(); return (n/n.cummax()-1).min()
def lever_to(s,t):
    lo,hi=0.1,8.0
    for _ in range(40):
        m=(lo+hi)/2
        if mdd(s,m)<t: hi=m
        else: lo=m
    return (lo+hi)/2

print(f"\n{'='*82}\nPRODUCTION = Core Beta Forward Book (알파북 아님·베타북) · 비용후·financing 5%\n{'='*82}")
spy=stat(df["SPY"]); print(f"기준 SPY(unlev): CAGR {spy[0]*100:.1f}% · MDD {spy[1]*100:.0f}% · Sharpe {spy[2]:.2f}")
print(f"\nA1 시나리오별 (Core 또는 Core+오버레이를 각 MDD에 레버 맞춤):")
print(f"{'시나리오':<22}{'레버':>6}{'CAGR%':>8}{'MDD%':>7}{'Sharpe':>8}{'  vs SPY CAGR':>13}")
rows=[]
for nm,t in [("Conservative −20%",-0.20),("Aggressive −35% ★기본",-0.35),("Max Aggressive −50%",-0.50)]:
    for book in ["CoreOnly","CoreOverlay"]:
        L=lever_to(df[book],t); cg,md,sh=stat(lever(df[book],L))
        rows.append(dict(scen=nm,book=book,lev=L,cagr=cg,mdd=md,sharpe=sh))
        print(f"  {nm[:16]:<16}{book:<8}{L:>5.2f}{cg*100:>8.1f}{md*100:>7.0f}{sh:>8.2f}{(cg-spy[0])*100:>+12.1f}%p")
pd.DataFrame(rows).to_csv(os.path.join(ENG,"production_book.csv"),index=False)
# attribution: 오버레이 한계기여(동일 −35% 레버 매칭)
L_co=lever_to(df["CoreOnly"],-0.35); L_cov=lever_to(df["CoreOverlay"],-0.35)
co=stat(lever(df["CoreOnly"],L_co)); cov=stat(lever(df["CoreOverlay"],L_cov))
print(f"\nAttribution(−35% 매칭): 오버레이 한계기여 = CoreOverlay − CoreOnly = {(cov[0]-co[0])*100:+.2f}%p/yr CAGR")
print(f"  → {'미미(노이즈, Phase1.5 일관)=Core-only 권장' if abs(cov[0]-co[0])<0.01 else '유의미'}")

# 현재 타깃(forward용) — Codex REVISE 반영:
# 기본 = 1.0x Core(PRODUCTION_SAFE 후보). 레버는 *별도 격리 sleeve*(PRODUCTION_UNSAFE: shock-replay+hard cap+financing 고정 전 자본금지).
# "−35%에 레버 맞추기"는 risk cap이 아니라 backward leverage knob → 기본 타깃에서 제외. overlay 기본 OFF(노이즈).
last=days[-1]; on,reg=trend_on(last)
out={"asof":str(last.date()),
 "production_default":{"book":"Core Beta 1.0x","target":{"SPY":0.5,"QQQ":0.5},"label":"PRODUCTION_SAFE candidate(paper)",
   "note":"정직한 베타북 기본 — NOT alpha. Core>SPY=QQQ tilt(regime, LOCK C6)."},
 "beta_leverage_sleeve":{"scenario":"Aggressive_-35%","lever":round(L_co,3),"target":{"SPY":round(0.5*L_co,3),"QQQ":round(0.5*L_co,3)},
   "label":"PRODUCTION_UNSAFE","gate":"shock-replay(2018Q4/2020/2022)+gross-lev cap+financing+gap stress+fail-closed 고정 전 자본 금지"},
 "trend_overlay":"OFF (한계기여 −0.14%/yr=노이즈; 켜려면 목적=drawdown-shape지 return 아님)",
 "trend_on":on,"vol_regime":reg,
 "caveat":"−35% MDD = 2016-26 benign 과거 샘플(2008 미포함) → forward MDD 더 클 수 있음. 레버=과거데이터 knob이지 forward risk cap 아님(Codex)."}
json.dump(out,open(os.path.join(ENG,"production_target.json"),"w"),indent=2)
print(f"\n현재 타깃(Codex REVISE 반영) → outputs/engine/production_target.json")
print(f"  ✅ Production 기본 = Core Beta 1.0x: SPY 0.50 / QQQ 0.50 (PRODUCTION_SAFE 후보·paper)")
print(f"  ⚠️ −35% 레버({L_co:.2f}x) = 격리 sleeve·PRODUCTION_UNSAFE(shock-replay+cap 전 자본금지) · 추세 ON {len(on)}/{len(TT)}")
print(f"  → CSV outputs/engine/production_book.csv")

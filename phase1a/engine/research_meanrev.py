#!/usr/bin/env python3
"""PRAMANA V4 — Research thread 1: 레짐게이트 단기 mean-reversion (ETF 횡단면).
가설: trend가 알파 아니면(C1·C2), trend 약한 chop장에서 단기 반전이 보탤 수 있나?
v3의 *월간* 횡단면 reversal은 이미 REJECT(gross Sharpe −0.52·turnover 937%) → 이번은 *단기·레짐게이트·ETF*로 다른 각도.
사전등록 kill을 결과 보기 전 박는다(아래 KILLS). 정직: 죽으면 REJECT/NEEDS_EVIDENCE 라벨.
paper·비용후. cached SFP_FUNDS. Active Research 1개(다른 건 안 건드림)."""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import data
ENG=os.path.join(data.PHASE1A,"outputs","engine"); os.makedirs(ENG,exist_ok=True)
# ── 사전등록 KILL (결과 보기 전) ──
KILLS={"K1 net≤0":"비용후 연수익 ≤ 0 → REJECT(비용 못 넘음)",
       "K2 IC-IR<0.2":"반전신호 IC-IR < 0.2 → 노이즈",
       "K3 turnover>600%":"연 turnover > 600% → 비용취약(flag)",
       "K4 subperiod 부호flip":"2016-20 vs 2021-26 net 부호 반대 → 인샘플/불안정",
       "K5 Core 한계기여≤0":"Core 대비 비용후 한계기여 ≤ 0 → 위성자격 없음"}
print("="*80); print("사전등록 KILL (결과 전 고정):");  [print(f"  {k}: {v}") for k,v in KILLS.items()]; print("="*80)

etf=data.load("SFP_FUNDS",usecols=["ticker","date","closeadj"]).pivot_table(index="date",columns="ticker",values="closeadj").sort_index()
TT=[c for c in ["SPY","QQQ","IWM","DIA","XLK","XLF","XLE","XLV","XLI","XLY","XLP","XLU","XLB","XLRE","XLC"] if c in etf.columns]
ret=etf.pct_change(); sma200=etf["SPY"].rolling(200).mean()
LB=5; BPS=7   # 5일 반전·ETF 왕복 7bp
days=etf.index[etf.index>=etf.index[210]]
# chop 레짐 = SPY가 200일선 ±4% 이내(추세 약함)
dist=(etf["SPY"]/sma200-1).abs()
r5=etf[TT].pct_change(LB)              # 최근 5일 수익
mr_r=[]; tcost=[]; prev_w=None; ic_list=[]; gate=[]
for i,d in enumerate(days):
    if i==0: mr_r.append(0);tcost.append(0);gate.append(0);continue
    p=days[i-1]; chop = 1 if (pd.notna(dist.get(p)) and dist[p]<0.04) else 0; gate.append(chop)
    sig=-r5.loc[p].reindex(TT)         # 반전: 5일 많이 빠진 게 매수신호(next-bar)
    if chop and sig.notna().sum()>=6:
        rk=sig.rank(pct=True); w=pd.Series(0.0,index=TT)
        w[rk>=0.7]=1.0; w[rk<=0.3]=-1.0; w=w/ w.abs().sum()   # dollar-neutral L/S
        mr_r.append(float((w*ret.loc[d,TT]).sum()))
        # IC: 신호 vs 당일 실현
        ic_list.append(sig.corr(ret.loc[d,TT],method="spearman"))
    else: w=pd.Series(0.0,index=TT); mr_r.append(0.0)
    tcost.append(float((w.fillna(0)-(prev_w if prev_w is not None else 0)).abs().sum())*BPS/1e4); prev_w=w.fillna(0)
S=pd.DataFrame({"mr":mr_r,"tc":tcost},index=days); S["net"]=S["mr"]-S["tc"]
def ann(s): return s.mean()*252
def sharpe(s): return s.mean()/s.std()*np.sqrt(252) if s.std()>0 else float("nan")
gross_a=ann(S["mr"]); net_a=ann(S["net"]); turn=pd.Series(tcost,index=days).sum()/((days[-1]-days[0]).days/365.25)/(BPS/1e4)
ic=pd.Series(ic_list); icir=ic.mean()/ic.std()*np.sqrt(252/ (gate.count(1) or 1) *1) if len(ic)>1 and ic.std()>0 else ic.mean()/ic.std() if len(ic)>1 and ic.std()>0 else float("nan")
icir=ic.mean()/ic.std() if len(ic)>1 and ic.std()>0 else float("nan")
half=len(days)//2
sp1=ann(S["net"].iloc[:half]); sp2=ann(S["net"].iloc[half:])
chop_frac=np.mean(gate)
print(f"\n결과: gross 연{gross_a*100:+.1f}% · net 연{net_a*100:+.1f}% · net Sharpe {sharpe(S['net']):+.2f} · turnover {turn*100:.0f}%/yr")
print(f"  IC mean {ic.mean():+.4f} · IC-IR {icir:+.3f} · chop 게이트 발동 {chop_frac*100:.0f}% 일수")
print(f"  subperiod net: 2016-20 {sp1*100:+.1f}% / 2021-26 {sp2*100:+.1f}%")
# Core(SPY/QQQ) 대비 한계기여: 90% core + 10% MR
core=0.5*ret["SPY"].reindex(days).fillna(0)+0.5*ret["QQQ"].reindex(days).fillna(0)
comb=0.90*core+0.10*S["net"]; mc=sharpe(comb)-sharpe(core)
print(f"  Core 대비: Core Sharpe {sharpe(core):+.2f} → +10%MR {sharpe(comb):+.2f} (Δ{mc:+.3f})")
# ── KILL 판정 ──
fired=[]
if net_a<=0: fired.append("K1 net≤0")
if not (icir>0.2): fired.append("K2 IC-IR<0.2")
if turn>6.0: fired.append("K3 turnover>600%")
if np.sign(sp1)!=np.sign(sp2): fired.append("K4 subperiod flip")
if mc<=0: fired.append("K5 Core 한계기여≤0")
print(f"\n{'─'*80}\nKILL 발동: {fired if fired else '없음'}")
label = "REJECT" if ("K1 net≤0" in fired or "K5 Core 한계기여≤0" in fired) else ("NEEDS_EVIDENCE" if fired else "RESEARCH_ONLY(유망·sandbox 유지)")
print(f"판정 라벨: {label}")
print(f"정직note: 단기반전은 비용·turnover에 취약(Lehmann1990 이후 차익거래). chop게이트가 살리는지가 관건.")
S.to_csv(os.path.join(ENG,"research_meanrev.csv"))
open(os.path.join(ENG,"research_meanrev_verdict.txt"),"w").write(
  f"mean-reversion(레짐게이트 단기 ETF L/S) · {label}\nnet {net_a*100:+.1f}%/yr·Sharpe {sharpe(S['net']):+.2f}·turnover {turn*100:.0f}%·IC-IR {icir:+.3f}·Core한계기여 {mc:+.3f}·KILL {fired}\n")
print(f"→ outputs/engine/research_meanrev.csv + _verdict.txt")

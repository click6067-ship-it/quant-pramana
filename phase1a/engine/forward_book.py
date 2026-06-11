#!/usr/bin/env python3
"""PRAMANA v3 — forward_book: '지금 뭘 들고 있어야 하나'(current target) + forward 추적 로그.
백테스트 아님 — 최신 데이터로 *현재 목표 포트폴리오* 산출(next-bar 진입용) + forward_log.csv 적재(promotion gate 시계).
바닥: PIT(최신 종가까지만)·no look-ahead·paper. 수익-max book(eq+trend+LETF dose) 현재 상태."""
import os, sys, numpy as np, pandas as pd
from datetime import datetime, timezone
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import data, features as F, universe as U
ENG=os.path.join(data.PHASE1A,"outputs","engine")

def current_target():
    # ── ETF trend (현재 200d SMA 위 ETF + vol regime) ──
    f=data.load("SFP_FUNDS",usecols=["ticker","date","closeadj"]).pivot_table(index="date",columns="ticker",values="closeadj").sort_index()
    TT=["SPY","QQQ","IWM","DIA","XLK","XLF","XLE","XLV","XLI","XLY","XLP","XLU","XLB","XLRE","XLC"]
    f=f[[c for c in TT if c in f.columns]]
    asof=f.index[-1]; sma200=f.rolling(200).mean().iloc[-1]; last=f.iloc[-1]
    trend_on=[t for t in f.columns if last[t]>sma200[t]]
    spy=data.load("SFP_FUNDS",usecols=["ticker","date","closeadj"]); spy=spy[spy.ticker=="SPY"].set_index("date")["closeadj"].sort_index()
    rv=float(spy.pct_change().rolling(20).std().iloc[-1]*np.sqrt(252)); risk_on = rv<0.20
    # ── LETF (trend ON시 3x 표현) ──
    letf_map={"QQQ":"TQQQ","SPY":"UPRO"}; letf_on=[letf_map[u] for u in ["QQQ","SPY"] if u in trend_on]
    # ── equity MN (현재 meta 신호 top/bottom quintile) ──
    px=data.load("broad_SEP",usecols=["ticker","date","closeadj"]).pivot_table(index="date",columns="ticker",values="closeadj").sort_index()
    sf1=data.load("broad_SF1"); sf1x=data.load("broad_SF1_ext"); sector=data.load_tickers()["sector"]
    uni=U.rank_universe(1,1500); rebal=sorted(uni["asof"].unique()); t=rebal[-1]
    members=set(uni[uni["asof"]==t]["ticker"])
    mom=F.momentum(px,rebal).loc[t]; qual=F.quality(sf1,rebal,px.columns).loc[t]; EQ=F.event_subsignals(sf1x,rebal)
    mem=[c for c in px.columns if c in members]
    d=pd.DataFrame({"mom":mom.reindex(mem),"qual":qual.reindex(mem)})
    for k in F.EVENT_COLS: d[k]=EQ[k].loc[t].reindex(mem)
    d["sec"]=sector.reindex(mem).values; d["ev"]=F.composite(d,F.EVENT_COLS); d=d.dropna(subset=["mom","qual","ev"])
    d["meta"]=pd.concat([F.zscore(d["mom"]),F.zscore(d["qual"]),F.zscore(d["ev"])],axis=1).mean(axis=1)
    d["sn"]=d["meta"]-d.groupby("sec")["meta"].transform("mean"); rk=d["sn"].rank(pct=True)
    longs=d.index[rk>=0.8].tolist(); shorts=d.index[rk<=0.2].tolist()
    # ── 현재 레버리지(trailing vol) + 리스크 상태 ──
    nb=pd.read_csv(os.path.join(ENG,"book_final_nav.csv"),index_col=0,parse_dates=True)["combo"]
    tvol=nb.iloc[-12:].std()*np.sqrt(12); lev=min(4.0, 0.5*0.40/tvol) if tvol>0 else 1.0
    dd3=(1+nb.iloc[-3:]).prod()-1; risk_flag = "DD-cut" if dd3<-0.15 else ("vol-off" if not risk_on else "정상")
    return dict(asof_etf=str(asof.date()), asof_eq=str(pd.Timestamp(t).date()), trend_on=trend_on, risk_on=risk_on, rv=rv,
                letf_on=letf_on, eq_long=len(longs), eq_short=len(shorts), lev=round(lev,2), risk_flag=risk_flag,
                eq_long_sample=longs[:8], eq_short_sample=shorts[:8])

print("="*84); print("PRAMANA v3 — FORWARD BOOK: 현재 목표 포트폴리오 (지금 뭘 들까) · paper"); print("="*84)
T=current_target()
print(f"\nas-of: ETF {T['asof_etf']} · equity {T['asof_eq']} · SPY 20d vol {T['rv']*100:.0f}% → risk {'ON' if T['risk_on'] else 'OFF(de-risk)'}")
print(f"\n[ETF trend 롱 ({len(T['trend_on'])}/15 추세 ON)]: {T['trend_on']}")
print(f"[LETF convex dose (소량)]: {T['letf_on'] if T['letf_on'] else '(없음)'}")
print(f"[equity MN L/S]: 롱 {T['eq_long']}종 · 숏 {T['eq_short']}종 (sector-neutral)")
print(f"   롱 예시: {T['eq_long_sample']}")
print(f"   숏 예시: {T['eq_short_sample']}")
print(f"[리스크 엔진]: 목표 레버리지 {T['lev']}x · 상태 {T['risk_flag']}")
# forward 추적 로그(promotion gate 시계)
log=os.path.join(ENG,"forward_log.csv"); now=datetime.now(timezone.utc).isoformat(timespec="seconds")
row=pd.DataFrame([dict(ts=now, asof_etf=T['asof_etf'], asof_eq=T['asof_eq'], trend_on_n=len(T['trend_on']),
                       risk_on=T['risk_on'], letf_on=";".join(T['letf_on']), eq_long=T['eq_long'], eq_short=T['eq_short'], lev=T['lev'], risk=T['risk_flag'])])
row.to_csv(log, mode="a", header=not os.path.exists(log), index=False)
print(f"\n  → forward_log.csv 적재(forward 추적 시작, promotion gate 12mo 시계). paper·no live·human이 capital gate.")
print(f"  매월 이 스크립트 실행 = 현재 목표 갱신 + 로그. (실제 체결은 next-bar·broker는 추후 human 승인 후.)")

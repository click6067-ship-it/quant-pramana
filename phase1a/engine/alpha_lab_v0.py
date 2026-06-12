#!/usr/bin/env python3
"""PRAMANA Alpha Lab v0 — intraday DATA INFRA (전략 아님·자본권한 0·PAPER).
목표: '내가 보고 싶은 setup(ORB 돌파+VWAP 유지)이 데이터로 잡히나' 확인 + 정규 스키마 append-only 적재.
코어(4-sleeve)와 완전 분리. 브레이크/반등 = 공격 파트 허용/중지용 신호(측정만·행동 X).
데이터: yfinance 5m(60일·premarket). 한계=장기 백테스트 불가→일별 적재로 forward 축적. 스펙 PRAMANA_V4/AlphaLab_v0_Design.md
사용: python engine/alpha_lab_v0.py"""
import os, sys, warnings; warnings.filterwarnings("ignore")
from datetime import time
import numpy as np, pandas as pd, yfinance as yf
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
OUT=os.path.join(ROOT,"outputs","alpha_lab","intraday"); os.makedirs(OUT,exist_ok=True)
WATCH=["SPY","QQQ","NVDA","TSLA","AMD","META","PLTR","COIN","SMCI","MSTR"]  # 0단계 고정(유동성·변동성)·진짜 급등주 스캐너=1단계 유니버스 RVOL
ORB_MIN=15  # opening range = 첫 15분

def fetch(tk):
    d=yf.download(tk,period="60d",interval="5m",prepost=True,progress=False,auto_adjust=False)
    if d is None or len(d)==0: return None
    d.columns=[c[0] if isinstance(c,tuple) else c for c in d.columns]
    d=d.dropna(subset=["Close"])
    if d.index.tz is None: d.index=d.index.tz_localize("UTC")
    d.index=d.index.tz_convert("America/New_York")
    d["ticker"]=tk
    d["is_premarket"]=d.index.time<time(9,30)
    d["is_regular"]=(d.index.time>=time(9,30))&(d.index.time<time(16,0))
    return d

def add_vwap(d):  # 세션별 VWAP (정규장만 리셋)
    d["vwap"]=np.nan
    reg=d[d.is_regular]
    if len(reg):
        vw=reg.groupby(reg.index.date,group_keys=False).apply(lambda g:(g.Close*g.Volume).cumsum()/g.Volume.cumsum().replace(0,np.nan))
        d.loc[reg.index,"vwap"]=vw.values
    return d

def daily_rvol(d):  # 일 RVOL = 당일 총거래량 / 최근 20일 평균
    dv=d[d.is_regular].groupby(d[d.is_regular].index.date)["Volume"].sum()
    if len(dv)<5: return {}
    avg=dv.rolling(20,min_periods=5).mean().shift(1)
    return {k:(dv[k]/avg[k] if pd.notna(avg.get(k)) and avg.get(k,0)>0 else np.nan) for k in dv.index}

def scan_setup(d, day):  # ORB 돌파 & VWAP 위 bar 검출 (오늘)
    g=d[(d.index.date==day)&(d.is_regular)].copy()
    if len(g)<6: return None
    orb=g[g.index.time<time(9,30+ORB_MIN//60,ORB_MIN%60*0)]  # 첫 ORB_MIN분
    orb=g.between_time("09:30",f"09:{30+ORB_MIN-1:02d}")
    if len(orb)==0: return None
    hi,lo=orb["High"].max(),orb["Low"].min()
    bk=g[(g["Close"]>hi)&(g["Close"]>g["vwap"])]
    return dict(orb_hi=hi,orb_lo=lo,vwap_close=g["vwap"].iloc[-1],bars=len(g),
                breakout_bars=len(bk),first=(bk.index[0].time().strftime("%H:%M") if len(bk) else None),
                close=g["Close"].iloc[-1],above_vwap=bool(g["Close"].iloc[-1]>g["vwap"].iloc[-1]))

def persist(d):  # append-only 정규 스키마 적재(중복 timestamp 제거)
    cols=["ticker","Open","High","Low","Close","Volume","is_premarket","is_regular","vwap"]
    df=d[cols].copy(); df.index.name="timestamp"
    p=os.path.join(OUT,f"{d['ticker'].iloc[0]}.csv")
    if os.path.exists(p):
        old=pd.read_csv(p,index_col=0,parse_dates=True)
        if old.index.tz is None: old.index=old.index.tz_localize("America/New_York")
        df=pd.concat([old,df[~df.index.isin(old.index)]]).sort_index()
        df=df[~df.index.duplicated(keep="last")]
    df.to_csv(p)
    return len(df)

def market_signals():  # 브레이크/반등 신호 (일봉·측정만·행동 X)
    mk=yf.download(["SPY","QQQ","^VIX"],period="320d",interval="1d",auto_adjust=True,progress=False)
    c=mk["Close"] if isinstance(mk.columns,pd.MultiIndex) else mk
    spy=c["SPY"].dropna(); vix=c["^VIX"].dropna()
    sma=lambda n:spy.rolling(n).mean().iloc[-1]
    px=spy.iloc[-1]; gap=spy.iloc[-1]/spy.iloc[-2]-1
    brakes=[]; rebounds=[]
    if px<sma(200): brakes.append("200일선 이탈→LETF/overnight 금지")
    if px<sma(50): brakes.append("50일선 이탈→신규 축소")
    if px<sma(20): brakes.append("20일선 이탈→단기추세 훼손")
    if vix.iloc[-1]>25: brakes.append(f"VIX {vix.iloc[-1]:.0f}>25→size 축소")
    if gap<-0.015: brakes.append(f"gap-down {gap*100:.1f}%→장초반 진입금지")
    if px>sma(20): rebounds.append("20일선 회복→소액 재개")
    if px>sma(50): rebounds.append("50일선 회복")
    if vix.iloc[-1]<18: rebounds.append(f"VIX {vix.iloc[-1]:.0f}<18→size 정상화")
    # 공격 상태(사다리): 브레이크 개수
    nb=len(brakes)
    state="HALT(신규금지)" if nb>=3 else "CAUTION(size↓·overnight금지)" if nb>=1 else "ALLOW(정상)"
    return state,brakes,rebounds,px,sma(200),vix.iloc[-1]

def main():
    print("="*82); print("PRAMANA Alpha Lab v0 — intraday DATA INFRA (전략 아님·자본권한 0·PAPER)"); print("="*82)
    rows=[]
    for tk in WATCH:
        try:
            d=fetch(tk)
            if d is None: print(f"  {tk:<6} 데이터 없음"); continue
            d=add_vwap(d); rv=daily_rvol(d); n=persist(d)
            day=sorted(set(d[d.is_regular].index.date))[-1]
            s=scan_setup(d,day)
            rvol=rv.get(day,np.nan)
            rows.append((tk,day,n,len(d[d.is_premarket]),rvol,s))
        except Exception as e:
            print(f"  {tk:<6} ERR {str(e)[:60]}")
    print(f"\n[적재] outputs/alpha_lab/intraday/<ticker>.csv (append-only·정규 스키마)")
    print(f"\n[setup 스캔] 최근 거래일 · 'ORB({ORB_MIN}분) 상단 돌파 & VWAP 위' = 데이터로 잡히는 setup")
    print(f"  {'종목':<6}{'날짜':<12}{'적재행':>8}{'pre봉':>6}{'RVOL':>6}{'돌파bar':>7}{'첫돌파':>7}{'종가>VWAP':>9}")
    setups=[]
    for tk,day,n,npre,rvol,s in rows:
        if s is None: print(f"  {tk:<6}{str(day):<12}{n:>8}{npre:>6}{'':>6}  setup 계산불가"); continue
        rvs=f"{rvol:.1f}" if pd.notna(rvol) else "·"
        print(f"  {tk:<6}{str(day):<12}{n:>8}{npre:>6}{rvs:>6}{s['breakout_bars']:>7}{str(s['first']):>7}{('YES'if s['above_vwap']else'no'):>9}")
        if s['breakout_bars']>0 and s['above_vwap']: setups.append(tk)
    st,brakes,rebounds,px,sma2,vix=market_signals()
    print(f"\n[오늘 setup 검출 종목] {setups if setups else '없음'}  ← v0 목표='setup이 데이터로 잡히나'({'PASS' if setups else 'no setup today'})")
    print(f"\n[시장 브레이크/반등 신호] (측정만·자본권한 0·코어 4-sleeve 면역) — 공격 상태: {st}")
    print(f"  SPY {px:.0f} vs 200일선 {sma2:.0f}·VIX {vix:.0f}")
    print(f"  🔴 브레이크: {brakes if brakes else '없음'}")
    print(f"  🟢 반등:   {rebounds if rebounds else '없음'}")
    print(f"\n정직: v0=데이터 infra·setup 검출까지. 돈 안 검(자본권한 0). 계좌 브레이크(하루-1%·DD-3/5%)=paper 시뮬레이터 다음. yfinance 5m=60일 한도→일별 적재로 forward 축적·진짜 백테스트=1단계 유료 벤더(Polygon/Alpaca).")
if __name__=="__main__": main()

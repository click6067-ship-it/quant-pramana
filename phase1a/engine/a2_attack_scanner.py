#!/usr/bin/env python3
"""PRAMANA A2 Phase C3 — Attack scanner (분봉·Bollinger/ORB15/VWAP/RVOL·catalyst).
provider(C4) 사용·watchlist 스캔·등급 A/B/C/D·NEG gate(a2_attack_ledger)·entry 게이트.
출력 outputs/a2_live/attack_candidates.csv + war_plan top_attack 연결.
★ DATA_QUALITY = provider.quality (yfinance=PROXY: full-market VWAP/RVOL 부정확·성과 증거 아님·forward watch 로그/QA용). PAPER·자본권한 0·매수 X.
사용: python engine/a2_attack_scanner.py"""
import os, sys, json, datetime as dt, numpy as np, pandas as pd, warnings; warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a2_intraday_provider as ip, a2_attack_ledger as al
try: import a2_event_store as es   # NEG gate (EDGAR PIT)·실패해도 스캔은 계속
except Exception: es = None
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
A2=os.path.join(ROOT,"outputs","a2_live"); os.makedirs(A2,exist_ok=True)
OUT=os.path.join(A2,"attack_candidates.csv"); STATE=os.path.join(A2,"state.json"); WAR=os.path.join(A2,"war_plan.json")
# watchlist (메가캡 리더 + 급등주 후보·PROXY·PIT 아님=selection 편향 주의)
WATCHLIST=["NVDA","MSFT","AAPL","AMZN","GOOGL","META","AVGO","TSLA","AMD","NFLX","SMCI","PLTR","CRWD","MRVL","SNOW","ARM"]

def features(bars):
    """마지막 거래일 5m bars → ORB15·VWAP·RVOL·Bollinger (근사·PROXY)."""
    if bars is None or len(bars) < 20: return None
    df = bars.dropna()
    if isinstance(df.columns, pd.MultiIndex): df.columns = [c[0] for c in df.columns]
    if not all(c in df.columns for c in ["Close","High","Low","Volume"]): return None
    last_day = df.index[-1].date()
    today_bars = df[df.index.map(lambda x: x.date()==last_day)]
    if len(today_bars) < 3: today_bars = df.tail(12)
    c=today_bars["Close"]; h=today_bars["High"]; l=today_bars["Low"]; v=today_bars["Volume"]
    last=float(c.iloc[-1])
    orb_h=float(h.iloc[:3].max()); orb_l=float(l.iloc[:3].min())          # 첫 15분(3×5m)
    tp=(h+l+c)/3; vwap=float((tp*v).sum()/v.sum()) if v.sum()>0 else last  # 당일 VWAP
    # RVOL: 당일 거래량 vs 과거 일평균(5m→일별 합산 근사)
    daily=df.groupby(df.index.map(lambda x: x.date()))["Volume"].sum()
    rvol=float(daily.iloc[-1]/daily.iloc[:-1].mean()) if len(daily)>1 and daily.iloc[:-1].mean()>0 else 1.0
    # Bollinger(20봉)
    ma=df["Close"].rolling(20).mean().iloc[-1]; sd=df["Close"].rolling(20).std().iloc[-1]
    bbw=float((4*sd/ma)) if ma else 0; bb_up=float(ma+2*sd)
    return {"last":round(last,2),"orb_break":last>orb_h,"orb_high":round(orb_h,2),
            "vwap_above":last>vwap,"vwap":round(vwap,2),"rvol":round(rvol,2),"rvol_ok":rvol>=2.0,
            "bb_breakout":last>bb_up,"bb_width":round(bbw,3)}

def grade(f, entry_ok, has_catalyst):
    if not entry_ok: return "D"
    confs=sum([f["orb_break"], f["vwap_above"], f["rvol_ok"], f["bb_breakout"]])
    if has_catalyst and confs>=3: return "A"
    if has_catalyst and confs>=2: return "B"
    if confs>=3: return "C"   # catalyst 없는 가격/거래량만 = paper watch
    return "D"

def main():
    st=json.load(open(STATE)) if os.path.exists(STATE) else {}
    lead=st.get("lead","GREEN"); decay=bool(st.get("decay",False))
    market="RED" if lead=="RED" else ("YELLOW" if (lead=="YELLOW" or decay) else "GREEN")
    # NEG gate = EDGAR event_store(PIT·직전 90일 NEG 공시) — 연결 완료(Attack은 size축소·overnight 금지·Moon은 절대금지)
    neg_tickers=[]
    EVT=os.path.join(A2.replace("a2_live","a2_events"),"event_store.csv") if False else os.path.join(ROOT,"outputs","a2_events","event_store.csv")
    if es is not None and os.path.exists(EVT):
        try:
            import pandas as _pd
            _ev=_pd.read_csv(EVT,usecols=["ticker","label","available_at"])
            neg_tickers=sorted(es.neg_tickers_asof(_ev, dt.date.today(), 90))
        except Exception: neg_tickers=[]
    prov=ip.get_provider("yfinance")
    rows=[]
    for t in WATCHLIST:
        try: bars=prov.get_intraday_bars(t,"5m",5)
        except Exception: continue
        f=features(bars)
        if not f: continue
        cand={"catalyst":False,"momentum":f["rvol_ok"] and f["vwap_above"],
              "rvol_ok":f["rvol_ok"],"vwap_above":f["vwap_above"],"orb_break":f["orb_break"],"bb_breakout":f["bb_breakout"]}
        e=al.check_entry(cand, lead, market); neg=al.neg_gate(t, neg_tickers)
        g=grade(f, e["enter"], cand["catalyst"])
        rows.append({"ticker":t,"grade":g,"enter":e["enter"],"blocked":";".join(e["blocked"]),
                     "neg":neg["mode"],"data_quality":prov.quality, **f})
    df=pd.DataFrame(rows).sort_values("grade") if rows else pd.DataFrame()
    df.to_csv(OUT,index=False)
    top=[r["ticker"] for _,r in df.iterrows() if r["grade"] in ("A","B")][:5] if len(df) else []
    neg_hit=[t for t in WATCHLIST if t in neg_tickers]
    if os.path.exists(WAR):
        w=json.load(open(WAR)); w["top_attack_candidates"]=top; w["attack_data_quality"]=prov.quality
        w["neg_filing_warnings"]=neg_hit; json.dump(w,open(WAR,"w"),indent=2,ensure_ascii=False)
    ga=sum(df["grade"]=="A") if len(df) else 0; gb=sum(df["grade"]=="B") if len(df) else 0; gc=sum(df["grade"]=="C") if len(df) else 0
    print(f"✅ Attack scan {dt.date.today()}·{len(df)}종목·A {ga}/B {gb}/C {gc}·quality {prov.quality}·top {top}·NEG경고 {neg_hit}·(NEG=EDGAR 연결완료·catalyst=가격/거래량 proxy·매수 X)")
if __name__=="__main__": main()

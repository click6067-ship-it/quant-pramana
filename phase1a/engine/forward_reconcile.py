#!/usr/bin/env python3
"""PRAMANA V4 — forward reconciliation (Codex SHIP). forward의 데이터 무결성.
forward_runner가 쓰는 yfinance EOD를 2번째 무료소스(stooq)와 *일별 수익률*로 대조.
(adjusted base 달라도 daily return은 거의 같음 → 큰 괴리 = 데이터 오류 신호.)
|yf_ret − stooq_ret| > 0.5%인 날 flag. 실거래 아니어도 'forward 좋았나' 판단의 신뢰도용.
사용: python engine/forward_reconcile.py"""
import os, sys, io, json, urllib.request, numpy as np, pandas as pd
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
FWD=os.path.join(ROOT,"outputs","forward"); PRICES=os.path.join(FWD,"prices.csv")
TOL=0.005  # 0.5% daily-return 괴리 = 오류 의심
def stooq(sym):
    url=f"https://stooq.com/q/d/l/?s={sym.lower()}.us&i=d"
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64)"})
    txt=urllib.request.urlopen(req,timeout=25).read().decode()
    if "Date" not in txt or "<html" in txt.lower(): return None   # rate-limit/empty 방어
    df=pd.read_csv(io.StringIO(txt))
    if "Close" not in df or "Date" not in df: return None
    s=df.set_index(pd.to_datetime(df["Date"]))["Close"]; return s[~s.index.duplicated()]
def main():
    if not os.path.exists(PRICES): print("⚠️ forward/prices.csv 없음 — forward_runner 먼저 실행"); return
    yf=pd.read_csv(PRICES,index_col=0,parse_dates=True)
    win=yf.index[-60:]  # 최근 60일 대조
    rows=[]; flags=0; n_ok=0
    for t in yf.columns:
        ss=None
        try: ss=stooq(t)
        except Exception as e: rows.append((t,"stooq fail",str(e)[:30])); continue
        if ss is None: rows.append((t,"no data","")); continue
        common=win.intersection(ss.index)
        if len(common)<10: rows.append((t,"few overlap",str(len(common)))); continue
        yr=yf[t].reindex(common).pct_change(); sr=ss.reindex(common).pct_change()
        d=(yr-sr).abs(); mx=float(d.max()); bad=int((d>TOL).sum()); flags+=bad; n_ok+=1
        rows.append((t,f"maxΔret {mx*100:.2f}%",f"{bad} days>0.5%"))
    print(f"\n{'='*64}\nFORWARD RECONCILIATION — yfinance vs stooq (daily return, 최근60일)\n{'='*64}")
    for t,a,b in rows: print(f"  {t:<6} {a:<18} {b}")
    ok = (flags==0 and n_ok>=5)   # 0체크 = 대조 실패 = UNKNOWN(false-positive 방지)
    status = "✅ OK" if ok else (f"⚠️ {flags} 괴리>0.5% 데이터 점검" if n_ok>=5 else f"⚠️ 2nd 피드 대조 실패(n={n_ok}) — 무결성 UNKNOWN, 다른 무료소스 wiring 필요")
    print(f"\n대조 종목 {n_ok} · 총 flag {flags} · {status}")
    json.dump({"ok":ok,"flags":flags,"tickers_checked":n_ok,"tol":TOL,"asof":str(yf.index[-1].date()),
               "note":"0 checked = UNKNOWN not OK" if n_ok<5 else ""},
              open(os.path.join(FWD,"reconcile.json"),"w"),indent=2)
    print(f"→ outputs/forward/reconcile.json")
if __name__=="__main__": main()

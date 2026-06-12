#!/usr/bin/env python3
"""PRAMANA Alpha Lab v2 — forward 후보 scanner (사전등록 AlphaLab_v2_Protocol.md).
용하: '실패는 기록·폐기는 마·좀 더 지켜보자.' → v1 setup을 *원형 그대로*(튜닝 없이) + v2 catalyst를 나란히 append-only 로그.
backtest 아님=forward 관찰. entry-time only(look-ahead 차단·v1 RVOL 누수 수정 반영). 사후수정 금지.
catalyst proxy(무료): earnings date 근접 / gap>3% / entry-time RVOL>=2. 진짜 뉴스=유료(다음).
PAPER·자본권한 0. 매일 1회 cron. python engine/alpha_lab_v2_scanner.py"""
import os, warnings; warnings.filterwarnings("ignore")
from datetime import time, timedelta
import numpy as np, pandas as pd, yfinance as yf
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
OUT=os.path.join(ROOT,"outputs","alpha_lab"); os.makedirs(OUT,exist_ok=True)
LOG=os.path.join(OUT,"v2_forward_log.csv")
WATCH=["NVDA","AMD","SMCI","MU","AVGO","MRVL","ARM","TSLA","PLTR","COIN","MSTR","SOFI","HOOD","RIVN",
       "AAPL","META","AMZN","MSFT","GOOGL","NFLX","AI","IONQ","RGTI","SMR","OKLO","CRWD","SNOW","NET","DKNG","ROKU"]
GAP_V1=0.01; RVOL_V1=1.5; GAP_CAT=0.03; RVOL_CAT=2.0   # v1 원형(고정·튜닝금지)·v2 catalyst 임계

def fetch(tk):
    d=yf.download(tk,period="60d",interval="5m",prepost=True,progress=False,auto_adjust=False)
    if d is None or len(d)==0: return None
    d.columns=[c[0] if isinstance(c,tuple) else c for c in d.columns]; d=d.dropna(subset=["Close"])
    if d.index.tz is None: d.index=d.index.tz_localize("UTC")
    d.index=d.index.tz_convert("America/New_York")
    d["reg"]=(d.index.time>=time(9,30))&(d.index.time<time(16,0))
    return d

def earnings_set(tk):
    try:
        ed=yf.Ticker(tk).get_earnings_dates(limit=16)
        if ed is None or len(ed)==0: return set()
        out=set()
        for dt in pd.to_datetime(ed.index).date:
            for k in (-1,0,1): out.add(dt+timedelta(days=k))   # ±1 calendar day 근사
        return out
    except Exception: return set()

def scan(tk, d, eds):
    rows=[]; reg=d[d.reg].copy()
    if len(reg)<40: return rows
    dates=np.array([t.date() for t in reg.index])
    reg["mod"]=(((reg.index.hour-9)*60+(reg.index.minute-30))).astype(int)
    reg["cumvol"]=reg.groupby(dates)["Volume"].cumsum()
    piv=pd.DataFrame({"d":dates,"mod":reg["mod"].values,"cv":reg["cumvol"].values}).pivot_table(index="d",columns="mod",values="cv",aggfunc="last")
    avgpiv=piv.rolling(20,min_periods=10).mean().shift(1)
    days=sorted(set(dates)); prev_close=None
    for day in days:
        g=reg[dates==day]
        if len(g)<12: prev_close=g["Close"].iloc[-1] if len(g) else prev_close; continue
        if prev_close is None: prev_close=g["Close"].iloc[-1]; continue
        gap=g["Open"].iloc[0]/prev_close-1
        vwap=(g["Close"]*g["Volume"]).cumsum()/g["Volume"].cumsum().replace(0,np.nan)
        orb=g.between_time("09:30","09:44"); prev_close=g["Close"].iloc[-1]
        if len(orb)==0: continue
        orb_hi,orb_lo=orb["High"].max(),orb["Low"].min()
        post=g.between_time("09:45","15:50")
        sig=post[(post["Close"]>orb_hi)&(post["Close"]>vwap.reindex(post.index))]
        if len(sig)==0: continue                       # 돌파+VWAP 위 진입신호 필요
        sig_t=sig.index[0]; sig_mod=int(g.loc[sig_t,"mod"])
        cumv=g.loc[sig_t,"cumvol"]; avgv=avgpiv.loc[day,sig_mod] if (day in avgpiv.index and sig_mod in avgpiv.columns) else np.nan
        rvol=cumv/avgv if (pd.notna(avgv) and avgv>0) else np.nan
        if pd.isna(rvol): continue
        after=g[g.index>sig_t]
        if len(after)<1: continue
        entry=after["Open"].iloc[0]                    # next-bar 시가(look-ahead 차단)
        v1=bool(gap>=GAP_V1 and rvol>=RVOL_V1)         # v1 원형 setup(튜닝 없음)
        cat=[]
        if day in eds: cat.append("earnings")
        if gap>=GAP_CAT: cat.append("gap")
        if rvol>=RVOL_CAT: cat.append("rvol")
        v2=bool(len(cat)>0)                            # v2 catalyst 후보
        if not (v1 or v2): continue
        rows.append(dict(date=str(day),ticker=tk,v1_setup=v1,v2_catalyst=v2,catalyst="|".join(cat) if cat else "none",
                         gap=round(gap,4),entry_rvol=round(rvol,2),entry_t=sig_t.strftime("%H:%M"),entry_px=round(entry,2)))
    return rows

def main():
    print("="*86); print("Alpha Lab v2 — forward 후보 scanner (v1 원형 관찰 + v2 catalyst·append-only·entry-time)"); print("="*86)
    allrows=[]
    for tk in WATCH:
        try:
            d=fetch(tk)
            if d is None: continue
            allrows+=scan(tk,d,earnings_set(tk))
        except Exception as e: print(f"  {tk} ERR {str(e)[:40]}")
    if not allrows: print("후보 0"); return
    new=pd.DataFrame(allrows)
    if os.path.exists(LOG):
        old=pd.read_csv(LOG)
        key=["date","ticker"]; merged=pd.concat([old,new]).drop_duplicates(subset=key,keep="last")
    else: merged=new
    merged=merged.sort_values(["date","ticker"]); merged.to_csv(LOG,index=False)
    ndays=merged["date"].nunique();
    print(f"\n[로그] {LOG} · 총 {len(merged)} 후보 · {ndays} 거래일 · 하루평균 {len(merged)/max(ndays,1):.1f}개 (남발 점검)")
    print(f"\n[v1 원형 setup 관찰] (폐기 안 함·튜닝 없음) — backtest DEAD였던 게 forward서도?")
    v1c=merged[merged["v1_setup"]]; print(f"  v1 setup 후보: {len(v1c)}개 ({len(v1c)/len(merged)*100:.0f}%)")
    print(f"\n[v2 catalyst 분포] — '왜 움직이나' 필터가 후보를 줄이나·catalyst 실재하나")
    for c in ["earnings","gap","rvol"]:
        n=merged["catalyst"].str.contains(c,na=False).sum(); print(f"  {c:<10} {n}개 ({n/len(merged)*100:.0f}%)")
    only_v1=merged[(merged["v1_setup"])&(~merged["v2_catalyst"])]
    print(f"  catalyst 없는 순수 v1(=이유없는 돌파): {len(only_v1)}개 ({len(only_v1)/len(merged)*100:.0f}%) ← v1이 약했던 부분")
    print(f"\n[최근 거래일 후보]")
    last=merged[merged["date"]==merged["date"].max()]
    for _,r in last.head(15).iterrows():
        tags=("v1" if r["v1_setup"] else "")+("+v2" if r["v2_catalyst"] else "");
        print(f"  {r['date']} {r['ticker']:<6} [{tags:<5}] catalyst={r['catalyst']:<16} gap{r['gap']*100:+.1f}% RVOL{r['entry_rvol']:.1f} {r['entry_t']} ${r['entry_px']}")
    print(f"\n정직: forward 후보 *기록*이지 수익검증 아님(수익=4~8주 후). v1 폐기 안 하고 원형 관찰(용하). catalyst proxy=earnings/gap/RVOL(진짜 뉴스=유료). 매일 cron append. 사후수정 금지.")
if __name__=="__main__": main()

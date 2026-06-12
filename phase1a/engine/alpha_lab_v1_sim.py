#!/usr/bin/env python3
"""PRAMANA Alpha Lab v1 — 단일 setup paper simulator (사전등록 AlphaLab_v1_Protocol.md).
setup: Gap-up + RVOL>=1.5 + ORB15 돌파 + VWAP 위. 진입=신호 bar 종가확인→*다음 bar 시가* 체결(look-ahead 차단).
청산: +5% target / VWAP·ORB저점 이탈 stop / 장마감. 비용 round-trip 20bp. 목표='이 setup이 비용후 돈 되나'.
PAPER·자본권한 0. 검증지표+사전등록 kill 대조. python engine/alpha_lab_v1_sim.py"""
import os, warnings; warnings.filterwarnings("ignore")
from datetime import time
import numpy as np, pandas as pd, yfinance as yf
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
OUT=os.path.join(ROOT,"outputs","alpha_lab"); os.makedirs(OUT,exist_ok=True)
WATCH=["NVDA","AMD","SMCI","MU","AVGO","MRVL","ARM","TSLA","PLTR","COIN","MSTR","SOFI","HOOD","RIVN",
       "AAPL","META","AMZN","MSFT","GOOGL","NFLX","AI","IONQ","RGTI","SMR","OKLO","CRWD","SNOW","NET","DKNG","ROKU"]
COST=0.0020; GAP_MIN=0.01; RVOL_MIN=1.5; TARGET=0.05   # 사전등록 파라미터

def fetch(tk):
    d=yf.download(tk,period="60d",interval="5m",prepost=True,progress=False,auto_adjust=False)
    if d is None or len(d)==0: return None
    d.columns=[c[0] if isinstance(c,tuple) else c for c in d.columns]; d=d.dropna(subset=["Close"])
    if d.index.tz is None: d.index=d.index.tz_localize("UTC")
    d.index=d.index.tz_convert("America/New_York")
    d["reg"]=(d.index.time>=time(9,30))&(d.index.time<time(16,0))
    return d

def trades_for(tk, d, spy_ret, spy_above200):
    out=[]; reg=d[d.reg].copy()
    if len(reg)<40: return out
    dates=np.array([t.date() for t in reg.index])
    reg["mod"]=(((reg.index.hour-9)*60+(reg.index.minute-30))).astype(int)   # 09:30부터 경과분
    reg["cumvol"]=reg.groupby(dates)["Volume"].cumsum()                        # 장중 누적(진입시점까지만)
    piv=pd.DataFrame({"d":dates,"mod":reg["mod"].values,"cv":reg["cumvol"].values}).pivot_table(index="d",columns="mod",values="cv",aggfunc="last")
    avgpiv=piv.rolling(20,min_periods=10).mean().shift(1)                      # 과거 20일 *같은 경과분* 누적 평균(미래 X)
    days=sorted(set(dates)); prev_close=None
    for day in days:
        g=reg[dates==day]
        if len(g)<12: prev_close=g["Close"].iloc[-1] if len(g) else prev_close; continue
        if prev_close is None: prev_close=g["Close"].iloc[-1]; continue
        gap=g["Open"].iloc[0]/prev_close-1
        vwap=(g["Close"]*g["Volume"]).cumsum()/g["Volume"].cumsum().replace(0,np.nan)
        orb=g.between_time("09:30","09:44")
        prev_close=g["Close"].iloc[-1]
        if gap<GAP_MIN or len(orb)==0: continue
        orb_hi,orb_lo=orb["High"].max(),orb["Low"].min()
        post=g.between_time("09:45","15:50")
        sig=post[(post["Close"]>orb_hi)&(post["Close"]>vwap.reindex(post.index))]
        if len(sig)==0: continue
        sig_t=sig.index[0]
        sig_mod=int(g.loc[sig_t,"mod"]); cumv=g.loc[sig_t,"cumvol"]          # 신호시점까지 누적거래량
        avgv=avgpiv.loc[day,sig_mod] if (day in avgpiv.index and sig_mod in avgpiv.columns) else np.nan
        rvol=cumv/avgv if (pd.notna(avgv) and avgv>0) else np.nan
        if pd.isna(rvol) or rvol<RVOL_MIN: continue                          # 진입시점 누적 RVOL(look-ahead 제거·Codex #1)
        after=g[g.index>sig_t]
        if len(after)<2: continue
        entry=after["Open"].iloc[0]; entry_t=after.index[0]   # next-bar open 체결(look-ahead 차단)
        path=g[g.index>=entry_t]
        # 청산 시뮬 (bar-by-bar·target은 intrabar high, stop은 close)
        exit_px,reason=path["Close"].iloc[-1],"time/close"
        for t,row in path.iloc[1:].iterrows():
            if row["High"]>=entry*(1+TARGET): exit_px,reason=entry*(1+TARGET),"target+5%"; break
            vw=vwap.get(t,np.nan)
            if (pd.notna(vw) and row["Close"]<vw) or row["Close"]<orb_lo: exit_px,reason=row["Close"],"stop(VWAP/ORB)"; break
        gross=exit_px/entry-1; net=gross-COST
        hold=path["Close"].iloc[-1]/entry-1-COST   # 익절/손절 없이 장마감(비교용)
        out.append(dict(tk=tk,day=str(day),gap=gap,rvol=rvol,gross=gross,net=net,reason=reason,
                        hold_net=hold,spy_ret=spy_ret.get(day,np.nan),spy_above200=spy_above200.get(day,True)))
    return out

def main():
    print("="*88); print("Alpha Lab v1 — 단일 setup paper sim (Gap-up+RVOL+ORB15+VWAP·비용후·look-ahead 차단)"); print("="*88)
    spx=yf.download("SPY",period="320d",interval="1d",auto_adjust=True,progress=False)
    spc=(spx["Close"] if isinstance(spx.columns,pd.MultiIndex) else spx).squeeze()
    spy_ret={d.date():r for d,r in spc.pct_change().items()}
    sma200=spc.rolling(200).mean(); spy_above200={d.date():bool(spc[d]>sma200[d]) if pd.notna(sma200[d]) else True for d in spc.index}
    allt=[]
    for tk in WATCH:
        try:
            d=fetch(tk)
            if d is not None: allt+=trades_for(tk,d,spy_ret,spy_above200)
        except Exception as e: print(f"  {tk} ERR {str(e)[:40]}")
    if not allt: print("진입 케이스 0 — setup 조건 만족 없음"); return
    T=pd.DataFrame(allt)
    def summ(df,lbl):
        if len(df)==0: print(f"  {lbl:<30} n=0"); return
        wr=(df["net"]>0).mean()*100; print(f"  {lbl:<30} n={len(df):>3}  평균net {df['net'].mean()*100:>6.2f}%  승률 {wr:>4.0f}%  중앙 {df['net'].median()*100:>6.2f}%")
    print(f"\n[전체 진입] (비용 round-trip {COST*1e4:.0f}bp={COST*100:.2f}%·next-bar 체결·20bp는 급등주 단타엔 낙관적)")
    summ(T,"all trades")
    print(f"\n[강세장 의존성 — 진입일 SPY 방향별] ← setup 엣지 vs 시장 베타 분리")
    summ(T[T["spy_ret"]>0],"SPY up 날")
    summ(T[T["spy_ret"]<=0],"SPY down/flat 날  ★핵심")
    print(f"\n[시장 브레이크 — SPY 200일선] (사전등록 게이트)")
    summ(T[T["spy_above200"]],"200일선 위 진입")
    summ(T[~T["spy_above200"]],"200일선 아래 진입")
    print(f"\n[익절/손절 효과] setup exit(target+stop) vs hold-to-close")
    print(f"  {'setup exit 평균net':<30} {T['net'].mean()*100:>6.2f}%")
    print(f"  {'hold-to-close 평균net':<30} {T['hold_net'].mean()*100:>6.2f}%   (차이=익절/손절 기여 {(T['net'].mean()-T['hold_net'].mean())*100:+.2f}%p)")
    fb=(T["reason"]=="stop(VWAP/ORB)").mean()*100
    print(f"\n[청산 사유] target+5% {(T['reason']=='target+5%').mean()*100:.0f}%·stop {(T['reason']=='stop(VWAP/ORB)').mean()*100:.0f}%·time/close {(T['reason']=='time/close').mean()*100:.0f}% (stop=false-breakout 근사 {fb:.0f}%)")
    T.to_csv(os.path.join(OUT,"v1_trades.csv"),index=False)
    # 사전등록 kill 대조
    m_all=T["net"].mean(); m_down=T[T["spy_ret"]<=0]["net"].mean() if len(T[T["spy_ret"]<=0]) else np.nan
    stop_helps=T["net"].mean()>T["hold_net"].mean()
    print(f"\n{'='*88}\n사전등록 kill 대조:")
    print(f"  ① after-cost 평균net>0?  {'PASS' if m_all>0 else 'FAIL'} ({m_all*100:+.2f}%)")
    print(f"  ② 강세장에서만 양수?(SPY down날 음수=시장베타)  {'우려' if (pd.notna(m_down) and m_down<=0) else 'OK'} (SPY down net {m_down*100:+.2f}%)" if pd.notna(m_down) else "  ② SPY down 표본 없음")
    print(f"  ③ false breakout 과반?  {'FAIL' if fb>50 else 'OK'} ({fb:.0f}%)")
    print(f"  ④ VWAP/ORB 손절이 손실 줄이나?  {'OK(stop 도움)' if stop_helps else '우려(stop이 수익 깎음)'}")
    print(f"  표본 n={len(T)} (작으면 deflated·60일·watchlist 고정=survivorship/selection 편향)")
    print(f"\n정직: 방향성 신호지 검증된 엣지 아님. yfinance 5m·60일·소표본·유니버스 PIT 아님. 다음=codex 적대검증·universe 확장·forward paper. 적재 outputs/alpha_lab/v1_trades.csv")
if __name__=="__main__": main()

#!/usr/bin/env python3
"""PRAMANA — Crash-Pack × Brake-Only Throttle 실험 (사전등록: Crashpack_Throttle_Protocol_v0.1.md).
딱 하나의 질문: *4-sleeve 고정 코어 + 공격 overlay(LETF)에 throttle*이 crash-pack서 값어치 있나?
코어 대전환 ❌ (이미 데이터로 짐). overlay만 위험신호때 cash로. proxy=stress 신호지 실증 아님.
북: 1)benchmark 2)static 4-sleeve 3)+overlay 고정 4)+overlay+throttle. w∈{5,10,20%}. free yfinance."""
import sys, numpy as np, pandas as pd, warnings; warnings.filterwarnings("ignore")
import yfinance as yf
RF=0.05; EXP=0.0095; W4=dict(eq=0.50,mf=0.25,gold=0.15,bond=0.10)
def dl(ts):
    d=yf.download(ts,period="max",interval="1d",auto_adjust=True,progress=False)
    return (d["Close"] if isinstance(d.columns,pd.MultiIndex) else d).dropna(how="all")
def letf(u): return 3*u - 2*RF/252 - EXP/252           # 3x daily-reset 합성(financing+expense)
def stat(nav):
    r=nav.pct_change().dropna(); yrs=len(nav)/252
    cagr=(nav.iloc[-1]/nav.iloc[0])**(1/yrs)-1 if yrs>0 else np.nan
    mdd=(nav/nav.cummax()-1).min(); sh=r.mean()/r.std()*np.sqrt(252) if r.std()>0 else np.nan
    uw=(nav<nav.cummax()).astype(int); best=cur=0
    for v in uw: cur=cur+1 if v else 0; best=max(best,cur)
    return nav.iloc[-1]/nav.iloc[0]-1, cagr, mdd, sh, best
def score_series(eqpx):
    sma=eqpx.rolling(200).mean(); vol=eqpx.pct_change().rolling(20).std()*np.sqrt(252)
    dd=eqpx/eqpx.cummax()-1
    s=((eqpx<sma).astype(int)+(vol>0.22).astype(int)+(dd<-0.10).astype(int))
    return s   # 0..3
def run_books(days, eq, mf, gold, bond, eqpx, u_over, w):
    """4 북의 NAV(=1 시작). throttle next-bar: score(t-1)>=1 → overlay off."""
    four=W4["eq"]*eq+W4["mf"]*mf+W4["gold"]*gold+W4["bond"]*bond
    ov=letf(u_over)
    sc=score_series(eqpx).reindex(days).fillna(0)
    onoff=(sc.shift(1).fillna(0)<1).astype(float)        # 1=overlay on, 0=throttled (next-bar)
    bench=eqpx.pct_change().reindex(days).fillna(0)       # benchmark = equity(QQQ/VFINX)
    b2=four.reindex(days).fillna(0)
    b3=(1-w)*four.reindex(days).fillna(0)+w*ov.reindex(days).fillna(0)
    b4=(1-w)*four.reindex(days).fillna(0)+w*onoff*ov.reindex(days).fillna(0)  # throttled overlay→cash
    nav=lambda r:(1+r).cumprod()
    return dict(bench=nav(bench),s4=nav(b2),ov=nav(b3),thr=nav(b4)), onoff, ov.reindex(days).fillna(0)
def block(title, days, eq, mf, gold, bond, eqpx, u_over, ws=(0.05,0.10,0.20)):
    print(f"\n{'='*90}\n[{title}]  n={len(days)}  {days[0].date()}~{days[-1].date()}\n{'='*90}")
    for w in ws:
        nv,onoff,ov=run_books(days,eq,mf,gold,bond,eqpx,u_over,w)
        print(f"\n  overlay w={w*100:.0f}%   {'북':<22}{'tot%':>8}{'CAGR%':>8}{'MDD%':>8}{'Sharpe':>8}{'UW일':>7}")
        S={}
        for k,nm in [("bench","Static QQQ/VFINX"),("s4","Static 4-sleeve"),("ov","4sl+overlay 고정"),("thr","4sl+overlay+THROTTLE")]:
            a=stat(nv[k]); S[k]=a
            print(f"  {'':<12}{nm:<22}{a[0]*100:>8.1f}{a[1]*100:>8.1f}{a[2]*100:>8.0f}{a[3]:>8.2f}{a[4]:>7.0f}")
        # throttle 평가: overlay-고정(ov) 대비 throttle(thr)
        dM=(S["thr"][2]-S["ov"][2])*100   # MDD 개선(+면 덜빠짐=좋음)
        dT=(S["thr"][0]-S["ov"][0])*100   # 총수익 차(throttle - overlay고정)
        dUW=S["ov"][4]-S["thr"][4]        # underwater 단축(+면 좋음)
        dSh_vs_s4=S["thr"][3]-S["s4"][3]  # 복잡도 정당화(thr Sharpe > static 4sleeve?)
        fired=int((onoff==0).sum())
        print(f"     →throttle vs overlay고정: MDD {dM:+.1f}%p({'개선'if dM>0 else'악화'})·총수익 {dT:+.1f}%p·UW {dUW:+.0f}일({'단축'if dUW>0 else'증가'})·발동 {fired}일 | vs static4sleeve Sharpe {dSh_vs_s4:+.2f}")
    return
def main():
    print("CRASH-PACK × BRAKE-ONLY THROTTLE — proxy=stress 신호(NOT 실증). 코어 대전환 없음·overlay만 throttle.")
    # ── 트랙 A 실증 (2019~) ──
    A=dl(["SPY","QQQ","DBMF","GLD","IEF"]); rA=A.pct_change()
    eqA=0.5*rA["SPY"]+0.5*rA["QQQ"]
    dA=A.dropna().index
    block("트랙 A 실증 2019~ (DBMF/GLD/IEF 실 ETF·overlay=3x QQQ)",dA,
          eqA.reindex(dA),rA["DBMF"].reindex(dA),rA["GLD"].reindex(dA),rA["IEF"].reindex(dA),
          A["QQQ"].reindex(dA),rA["QQQ"].reindex(dA))
    for nm,a,b in [("2020 COVID","2020-01-01","2020-07-01"),("2022 bear","2022-01-01","2022-12-31")]:
        seg=dA[(dA>=a)&(dA<=b)]
        if len(seg)>20: block(f"트랙 A · {nm}",seg,eqA.reindex(seg),rA["DBMF"].reindex(seg),rA["GLD"].reindex(seg),rA["IEF"].reindex(seg),A["QQQ"].reindex(seg),rA["QQQ"].reindex(seg))
    # ── 트랙 B proxy (장기) ──
    B=dl(["VFINX","RYMFX","GC=F","VFITX","VUSTX"]); rB=B.pct_change()
    def sleeve(idx,col): return (rB[col].reindex(idx).fillna(0) if col in rB else pd.Series(0.0,index=idx))
    WIN_B=[("B-2008 GFC (4-sleeve 전부 proxy·핵심)","2007-10-01","2009-12-31","RYMFX","GC=F","VFITX"),
           ("B-2000 닷컴 (MF=cash·보수적)","2000-01-01","2002-12-31",None,"GC=F","VFITX"),
           ("B-1987 (eq+bond만·MF/gold=cash·Black Monday 실데이터)","1987-01-01","1988-06-30",None,None,"VUSTX")]
    allB=B.dropna(how="all").index
    for title,a,b,mfc,goldc,bondc in WIN_B:
        seg=allB[(allB>=a)&(allB<=b)]
        seg=seg[pd.notna(B["VFINX"].reindex(seg))]
        if len(seg)<20: print(f"\n[{title}] 데이터 부족 skip"); continue
        eqB=rB["VFINX"].reindex(seg).fillna(0)
        mf=sleeve(seg,mfc) if mfc else pd.Series(0.0,index=seg)
        gold=sleeve(seg,goldc) if goldc else pd.Series(0.0,index=seg)
        bond=sleeve(seg,bondc)
        block(title,seg,eqB,mf,gold,bond,B["VFINX"].reindex(seg),rB["VFINX"].reindex(seg).fillna(0))
    print(f"\n{'='*90}\n사전등록 PASS(throttle 승격): crash마다 MDD↓·손실↓·UW↓ + 풀 net 양수 + thr Sharpe>static4sleeve. 하나라도 실패→대시보드 전용.\n{'='*90}")
if __name__=="__main__": main()

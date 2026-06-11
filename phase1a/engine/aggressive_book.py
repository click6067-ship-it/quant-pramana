#!/usr/bin/env python3
"""PRAMANA V5 — Aggressive Leveraged Core Beta Book (용하: 공격적 수익극대화·리스크수용·유연).
정직: 레버드 베타지 알파 아님 — 시장노출↑로 수익↑(리스크도↑). '리스크수용 ≠ 파산수용'.
loss-speed dampener (NOT a no-ruin floor — gap엔 무력) = vol-target(레버 변동성따라 유연) + DD ladder(낙폭 깊을수록 디레버)
  + 하드 레버캡 2.0x + shock-replay(2018Q4/2020/2022) 검증. 12mo STOP 기준 적용(v5 frame).
paper·비용후·next-bar·financing 5%. cached SFP_FUNDS."""
import os, sys, json, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import data
CAP=100_000_000; RF=0.05; ENG=os.path.join(data.PHASE1A,"outputs","engine")
TARGET_VOL=0.28; LMAX=2.0   # 공격적 vol목표·하드 레버캡
etf=data.load("SFP_FUNDS",usecols=["ticker","date","closeadj"]).pivot_table(index="date",columns="ticker",values="closeadj").sort_index()
ret=etf.pct_change(); days=etf.index[etf.index>=etf.index[210]]
core=(0.5*ret["SPY"]+0.5*ret["QQQ"]).reindex(days).fillna(0)
rvol=core.rolling(20).std()*np.sqrt(252)   # 실현변동성(유연 레버용)
def ddscale(dd):   # DD ladder: 낙폭 깊을수록 디레버(no-ruin)
    return 0.2 if dd<=-0.40 else 0.4 if dd<=-0.30 else 0.7 if dd<=-0.20 else 1.0
def run(tvol=TARGET_VOL, lmax=LMAX, ladder=True):
    nav=[CAP]; peak=CAP; levs=[]
    for i in range(1,len(days)):
        rv=rvol.iloc[i-1]; L=min(lmax, tvol/rv) if rv>0 else 1.0
        if ladder: L*=ddscale(nav[-1]/peak-1)
        r=L*core.iloc[i]-(L-1)*RF/252
        nav.append(nav[-1]*(1+r)); peak=max(peak,nav[-1]); levs.append(L)
    s=pd.Series(nav,index=days); return s, pd.Series(levs,index=days[1:])
def stat(s):
    r=s.pct_change().dropna(); yrs=(s.index[-1]-s.index[0]).days/365.25
    tot=s.iloc[-1]/s.iloc[0]-1; cg=(1+tot)**(1/yrs)-1 if yrs>0 and tot>-1 else float('nan')
    return tot,cg,(s/s.cummax()-1).min(),(r.mean()/r.std()*np.sqrt(252) if r.std()>0 else float('nan'))
def bh(sym):  # buy&hold NAV
    s=CAP*(1+ret[sym].reindex(days).fillna(0)).cumprod(); return s

nav,levs=run(); spy=bh("SPY"); qqq=bh("QQQ")
st=stat(nav); ss=stat(spy); sq=stat(qqq)
print(f"\n{'='*82}\nV5 AGGRESSIVE Leveraged Core Beta (vol-target {TARGET_VOL:.0%}·캡 {LMAX}x·DD ladder) · 비용후\n정직: 레버드 베타지 알파 아님. 'beat'는 레버(리스크)로 산 것.\n{'='*82}")
print(f"{'북':<22}{'누적%':>10}{'CAGR%':>8}{'MDD%':>8}{'Sharpe':>8}")
for nm,s in [("V5 Aggressive",st),("SPY (b&h)",ss),("QQQ (b&h)",sq)]:
    print(f"{nm:<22}{s[0]*100:>9.0f}{s[1]*100:>8.1f}{s[2]*100:>8.0f}{s[3]:>8.2f}")
print(f"\n레버: 평균 {levs.mean():.2f}x · 최대 {levs.max():.2f}x · 현재 {levs.iloc[-1]:.2f}x")
print(f"beat QQQ raw? 누적 {'✅' if st[0]>sq[0] else '❌'}({st[0]*100:.0f}% vs {sq[0]*100:.0f}%) · 단 MDD {st[2]*100:.0f}% vs QQQ {sq[2]*100:.0f}%(레버 대가)")
# ── shock-replay (Codex 필수 게이트): no-ruin floor가 버티나 ──
SHOCKS={"2018Q4 selloff":("2018-10-01","2018-12-31"),"2020 COVID":("2020-02-15","2020-04-01"),"2022 bear":("2022-01-01","2022-10-31")}
print(f"\nshock-replay (각 구간 V5 북 낙폭 — floor 검증):")
for nm,(a,b) in SHOCKS.items():
    seg=nav[(nav.index>=a)&(nav.index<=b)]
    if len(seg)>2:
        dd=(seg/seg.cummax()-1).min(); sdd=(spy[(spy.index>=a)&(spy.index<=b)]/spy[(spy.index>=a)&(spy.index<=b)].cummax()-1).min()
        print(f"  {nm:<18} V5 {dd*100:>6.0f}%  | SPY {sdd*100:>6.0f}%  {'⚠️ floor 위험' if dd<-0.55 else 'floor 유지'}")
worst=(nav/nav.cummax()-1).min(); curL=float(levs.iloc[-1])
# 합성 gap 스트레스 (Codex 가드레일: cap은 crash-loss budget로 — vol-target은 intraday gap에 무력)
print(f"\n합성 1일 갭 스트레스 @현재레버 {curL:.2f}x (vol-target 반응 불가):")
for g in [-0.10,-0.20,-0.30]: print(f"  지수 {g*100:.0f}% 갭 → 북 1일 {g*curL*100:.0f}%")
print(f"\n전체 최악 MDD {worst*100:.0f}% = 2016-26 *conditional*(2000-02 Nasdaq −78%·2008 GFC 미포함).")
print(f"⚠️ 정직 라벨(Codex): vol-target+ladder = '손실속도 완화 procyclical 레버드 베타 실험'이지 NO-RUIN 아님(gap 무력).")
print(f"   forward tail = possible −70%+. 2.0x = paper max(live cap 1.25~1.5x·crash-pack 통과 후). RESEARCH_ONLY/PRODUCTION_UNSAFE.")
out={"asof":str(days[-1].date()),"target_vol_hypothesis":TARGET_VOL,"paper_max_cap":LMAX,"cur_lever":round(curL,2),
 "cagr_2016_26":round(st[1],4),"mdd_2016_26_conditional":round(st[2],4),"sharpe":round(st[3],2),"beat_qqq_cum_insample":bool(st[0]>sq[0]),
 "label":"RESEARCH_ONLY / PRODUCTION_UNSAFE","forward_tail":"possible -70%+ (2008/dot-com not in 2016-26; gap risk)",
 "honest":"crash-loss-reducing procyclical-risk-aware LEVERED BETA experiment — NOT alpha, NOT no-ruin. beat QQQ = risk budget, not edge.",
 "guardrail":"cap by pre-registered crash-pack loss budget, not vol-target CAGR. live cap starts 1.25-1.5x.",
 "stop_criterion":"12mo forward: return-only does NOT pass; DD/ulcer/recovery guardrails must hold or mark FAIL"}
json.dump(out,open(os.path.join(ENG,"aggressive_book.json"),"w"),indent=2)
nav.to_csv(os.path.join(ENG,"aggressive_book_nav.csv"))
print(f"→ outputs/engine/aggressive_book.json + _nav.csv")

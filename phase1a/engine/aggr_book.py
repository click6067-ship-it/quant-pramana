#!/usr/bin/env python3
"""PRAMANA v3 — AGGRESSIVE leveraged paper book + 하드 리스크 감사 (Codex #1 우선순위).
작동하는 시장중립 L/S(ls_book.build_panel)를 *레버리지* + 잔혹 스트레스 + risk ledger.
공격적 사이징: target vol↑·max lev cap·DD-decay·cooldown(kill후 즉시 재가동 금지).
스트레스: 2x/5x 비용·위기구간(2018Q4·2020·2022)·gap-beta·worst month. ⚠️ paper·no live.
정직: 레버리지는 Sharpe 안 올림 — CAGR↑·DD↑(= 레버리지된 modest edge)."""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import data, ls_book as LB

TARGET_VOL=0.25; MAX_LEV=4.0; DD_CUT=-0.15; DD_LOOK=3; COOLDOWN=2; CAP_KRW=100_000_000

def aggressive_size(net):
    """공격적: vol-target(높음)+max lev cap + DD-cut 후 cooldown 동안 de-risk(즉시 재가동 금지)."""
    out=[]; lev=[]; rz=[]; cool=0
    for i in range(len(net)):
        past=pd.Series(rz[max(0,i-12):i]); v=past.std()*np.sqrt(12) if len(past)>=6 and past.std()>0 else np.nan
        k=min(MAX_LEV, TARGET_VOL/v) if (v==v and v>0) else 1.0
        dd=np.prod([1+x for x in rz[max(0,i-DD_LOOK):i]])-1 if i>=DD_LOOK else 0.0
        if dd<DD_CUT: cool=COOLDOWN
        if cool>0: k*=0.4; cool-=1
        r=net.iloc[i]*k; out.append(r); lev.append(k); rz.append(r)
    return pd.Series(out,index=net.index), pd.Series(lev,index=net.index)

def perf(r):
    m=12; sh=r.mean()/r.std()*np.sqrt(m) if r.std()>0 else np.nan
    nav=(1+r).cumprod(); dd=(nav/nav.cummax()-1).min(); cagr=(1+r).prod()**(m/len(r))-1
    return cagr, r.std()*np.sqrt(m), sh, dd, nav.iloc[-1]

def line(label,r):
    c,v,s,d,fin=perf(r); print(f"  {label:22s} CAGR={c*100:+7.2f}% vol={v*100:5.1f}% Sharpe={s:+.2f} maxDD={d*100:6.1f}% NAV×{fin:.2f}")
    return c,s,d

print("="*90); print("PRAMANA v3 — AGGRESSIVE Leveraged Paper Book + 하드 리스크 감사 (Codex #1)"); print("="*90)
R,cap=LB.build_panel()
net=R["net"]; cost=R["gross"]-R["net"]
agg,lev=aggressive_size(net)
print(f"\n기간 {R.index.min().date()}~{R.index.max().date()} · {len(R)}개월 · 공격적: target vol {TARGET_VOL*100:.0f}%·max lev {MAX_LEV:.0f}x·DD-cut {DD_CUT*100:.0f}%→cooldown {COOLDOWN}m")

print("\n[1] 레버리지 효과 (정직: Sharpe 불변·CAGR↑·DD↑)")
line("net 1x(비용후)", net)
line("net AGGRESSIVE(lev)", agg)
print(f"     평균 레버리지 {lev.mean():.2f}x (max {lev.max():.2f}x)")

print("\n[2] 비용 스트레스 (거래+borrow ×k) — aggressive 사이징 적용")
for k in [1,2,5]:
    line(f"  {k}x cost", aggressive_size(R["gross"]-k*cost)[0])

print("\n[3] 위기구간 (aggressive book 월수익)")
for lab,a,b in [("2018-Q4","2018-10-01","2018-12-31"),("2020-COVID","2020-02-01","2020-04-30"),("2022-bear","2022-01-01","2022-12-31"),("2021-26 recent","2021-01-01","2026-12-31")]:
    w=agg[(agg.index>=a)&(agg.index<=b)]
    if len(w): print(f"  {lab:14s} 누적={(1+w).prod()-1:+.1%} · 최악월={w.min():+.1%} · 월수={len(w)}")

print("\n[4] gap 리스크 + risk ledger")
beta=np.cov(R["net"],R["bench"])[0,1]/np.var(R["bench"])
print(f"  시장 beta(net)={beta:+.2f} → SPY −7% gap 시 book 1x≈{beta*-0.07*100:+.1f}% (aggressive ×{lev.mean():.1f}≈{beta*-0.07*lev.mean()*100:+.1f}%)")
print(f"  worst month: 1x={net.min()*100:+.1f}% · aggressive={agg.min()*100:+.1f}%  (레버리지 tail 확대)")
print(f"  평균 레버리지 {lev.mean():.2f}x · 최대 섹터편중(long) {R['secmax'].mean()*100:.0f}% · 시장상관 {net.corr(R['bench']):+.2f}")
print(f"  capacity(ADV 10%): {('≈$'+format(int(cap),',')+'/book') if cap else 'volume pull 진행중→추후'}")

ca,sa,da=perf(agg)[:4][0],perf(agg)[2],perf(agg)[3]
print(f"\n[가상 ₩100M · AGGRESSIVE] 1억 → ₩{CAP_KRW*perf(agg)[4]/1e8:.2f}억 ({(perf(agg)[4]-1)*100:+.0f}%, {len(R)//12}년) · 단 maxDD {da*100:.0f}%")
yr=(1+agg).groupby(agg.index.year).prod()-1
print("[연도별] "+" ".join(f"{y}:{v*100:+.0f}%" for y,v in yr.items()))
out=os.path.join(data.PHASE1A,"outputs","engine","aggr_book_nav.csv")
pd.DataFrame({"net_1x":net,"net_agg":agg,"lev":lev,"bench":R["bench"]}).to_csv(out)
print(f"\n  → {out}")
print("  ⚠️ 정직: 레버리지는 modest edge를 키운 것(Sharpe 동일). maxDD가 진짜 비용. 일별체결/LETF경로/선물 미반영(다음 척추+execution).")

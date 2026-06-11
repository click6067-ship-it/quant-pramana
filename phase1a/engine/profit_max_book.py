#!/usr/bin/env python3
"""PRAMANA v3 — PROFIT-MAX 공격적 book (수익최대화 모드). 죽이기 아니라 키우기.
바닥 규율만 유지(no look-ahead·blow-up 방지). institutional 천장(promotion gate)은 paper엔 미적용.
레버: return-tilt(이기는 sleeve↑) + 공격적 vol-target + 높은 max-lev. ⚠️ paper·no live(바닥 규율).
정직 1줄: trend sleeve가 견인·regime-flattered(forward 보수). same-close→forward엔진서 next-bar 적용예정(여긴 탐색)."""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import data, ls_book as LB, overlay_alpha as OV

CAP_KRW=100_000_000
def perf(r,m=12):
    sh=r.mean()/r.std()*np.sqrt(m) if r.std()>0 else np.nan
    nav=(1+r).cumprod(); dd=(nav/nav.cummax()-1).min(); cagr=(1+r).prod()**(m/len(r))-1
    rec=r[r.index>="2021-01-01"]; rs=rec.mean()/rec.std()*np.sqrt(m) if rec.std()>0 else np.nan
    return dict(sh=sh,cagr=cagr,dd=dd,fin=nav.iloc[-1],rs=rs,vol=r.std()*np.sqrt(m))
def line(l,r):
    p=perf(r); print(f"  {l:30s} Sharpe={p['sh']:+.2f} CAGR={p['cagr']*100:+7.2f}% vol={p['vol']*100:4.0f}% maxDD={p['dd']*100:6.1f}% NAV×{p['fin']:.2f}"); return p

def agg_size(net, target_vol, max_lev, dd_cut, cooldown=2, kelly=0.5):
    out=[]; rz=[]; cool=0
    for i in range(len(net)):
        past=pd.Series(rz[max(0,i-12):i]); v=past.std()*np.sqrt(12) if len(past)>=6 and past.std()>0 else np.nan
        k=min(max_lev, kelly*target_vol/v) if (v==v and v>0) else 1.0
        dd=np.prod([1+x for x in rz[max(0,i-3):i]])-1 if i>=3 else 0.0
        if dd<dd_cut: cool=cooldown
        if cool>0: k*=0.5; cool-=1
        r=net.iloc[i]*k; out.append(r); rz.append(r)
    return pd.Series(out,index=net.index)

print("="*92); print("PRAMANA v3 — PROFIT-MAX 공격적 book (수익최대화 모드)"); print("="*92)
Req,_=LB.build_panel(); eq=Req["net"]; eq.index=pd.to_datetime(eq.index)
Rov,_=OV.build_overlay(); ov=Rov["net"]; ov.index=pd.to_datetime(ov.index)
df=pd.concat([eq.rename("eq"),ov.rename("ov")],axis=1).dropna()
she=perf(df["eq"])["sh"]; sho=perf(df["ov"])["sh"]
print(f"\n공통 {len(df)}개월 · corr +{df['eq'].corr(df['ov']):.2f} · sleeve Sharpe eq{she:.2f}/ov{sho:.2f}")

print("\n[1] return-tilt 결합 (50/50 → 이기는 sleeve에 실음)")
for nm,we in [("50/50",0.50),("Sharpe-tilt",she/(she+sho)),("70/30 trend",0.30),("85/15 trend",0.15)]:
    c=we*df["eq"]+(1-we)*df["ov"]; line(f"{nm} (eq{we:.0%}/ov{1-we:.0%})",c)
# 채택: Sharpe-tilt (분산 유지하며 winner에 실음)
wtilt=she/(she+sho); combo=wtilt*df["eq"]+(1-wtilt)*df["ov"]

print("\n[2] 공격적 레버리지 (paper 수익최대화 — DD 감내)")
for tv,ml,dc,lbl in [(0.25,4.0,-0.15,"보수(vol25·4x·DD-15)"),(0.35,5.0,-0.25,"공격(vol35·5x·DD-25)"),(0.45,6.0,-0.35,"풀공격(vol45·6x·DD-35)")]:
    a=agg_size(combo,tv,ml,dc); p=line(lbl,a)
    if lbl.startswith("공격"): chosen=a; chosenp=p

print(f"\n[가상 ₩100M · 공격(vol35·5x)] 1억 → ₩{CAP_KRW*chosenp['fin']/1e8:.2f}억 ({(chosenp['fin']-1)*100:+.0f}%, {len(df)//12}년) · maxDD {chosenp['dd']*100:.0f}% · 2021-26 Sharpe {chosenp['rs']:+.2f}")
yr=(1+chosen).groupby(chosen.index.year).prod()-1
print("[연도별] "+" ".join(f"{y}:{v*100:+.0f}%" for y,v in yr.items()))
out=os.path.join(data.PHASE1A,"outputs","engine","profit_max_nav.csv")
pd.DataFrame({"combo_tilt":combo,"aggressive":chosen}).to_csv(out)
print(f"\n  → {out}")
print("  바닥 규율 유지: no look-ahead(next-bar는 forward엔진)·blow-up 방지(DD-cut/cooldown)·paper. 천장(promotion gate)은 paper엔 미적용=수익최대화 모드.")
print("  정직 1줄: trend sleeve 견인·regime-flattered → forward는 이보다 낮음. 그래도 '굴러가고 수익내는' 공격적 book = 지금 손에 있음.")

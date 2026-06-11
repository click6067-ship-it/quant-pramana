#!/usr/bin/env python3
"""PRAMANA v3 — COMBINED book (alpha ensemble 레이어): equity 시장중립 L/S + ETF trend+vol overlay.
두 sleeve가 거의 무상관(+0.02)→분산. 50/50 결합 + aggressive 사이징(vol-target). ⚠️ paper·no live.
정직: trend sleeve 0.85 Sharpe는 2017-25 강추세 레짐 flattered(2022-15%)·long-flat=net long beta. 결합도 그 한계 상속."""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import data, ls_book as LB, overlay_alpha as OV, aggr_book as AG

CAP_KRW=100_000_000
def perf(r):
    m=12; sh=r.mean()/r.std()*np.sqrt(m) if r.std()>0 else np.nan
    nav=(1+r).cumprod(); dd=(nav/nav.cummax()-1).min(); cagr=(1+r).prod()**(m/len(r))-1
    rec=r[r.index>="2021-01-01"]; rs=rec.mean()/rec.std()*np.sqrt(m) if rec.std()>0 else np.nan
    return dict(sharpe=sh,cagr=cagr,maxdd=dd,fin=nav.iloc[-1],rec_sharpe=rs,vol=r.std()*np.sqrt(m))
def line(lbl,r):
    p=perf(r); print(f"  {lbl:24s} Sharpe={p['sharpe']:+.2f} CAGR={p['cagr']*100:+6.2f}% vol={p['vol']*100:4.1f}% maxDD={p['maxdd']*100:6.1f}% | 2021-26 Sh={p['rec_sharpe']:+.2f}"); return p

print("="*88); print("PRAMANA v3 — COMBINED book (alpha ensemble): equity MN L/S + ETF trend overlay"); print("="*88)
Req,_=LB.build_panel(); eq=Req["net"]; eq.index=pd.to_datetime(eq.index)
Rov,_=OV.build_overlay(); ov=Rov["net"]; ov.index=pd.to_datetime(ov.index)
df=pd.concat([eq.rename("eq"),ov.rename("ov")],axis=1).dropna()
print(f"\n공통 {len(df)}개월 {df.index.min().date()}~{df.index.max().date()} · 상관 corr(eq,ov)={df['eq'].corr(df['ov']):+.3f}")
print("\n[개별 sleeve / 결합 (비용후, 무레버)]")
line("equity MN L/S", df["eq"]); line("ETF trend+vol overlay", df["ov"])
combo=0.5*df["eq"]+0.5*df["ov"]
pc=line("50/50 combo", combo)
# inverse-vol 정적가중(참고, in-sample)
we=1/df["eq"].std(); wo=1/df["ov"].std(); s=we+wo
ivc=(we/s)*df["eq"]+(wo/s)*df["ov"]; line(f"inverse-vol combo(eq{we/s:.0%}/ov{wo/s:.0%})", ivc)

print("\n[aggressive 사이징(vol-target 25%·max4x·DD-cut) — 50/50 combo]")
agg,lev=AG.aggressive_size(combo)
pa=line("50/50 combo + leverage", agg)
print(f"     평균 레버리지 {lev.mean():.2f}x(max {lev.max():.2f})")
print(f"\n[가상 ₩100M · 결합+레버] 1억 → ₩{CAP_KRW*pa['fin']/1e8:.2f}억 ({(pa['fin']-1)*100:+.0f}%, {len(df)//12}년) · maxDD {pa['maxdd']*100:.0f}%")
yr=(1+agg).groupby(agg.index.year).prod()-1
print("[연도별] "+" ".join(f"{y}:{v*100:+.0f}%" for y,v in yr.items()))
print("\n[비용 스트레스 — 50/50 combo + aggressive 사이징] (equity sleeve는 단독 5x서 사망)")
eqg=Req["gross"].copy(); eqg.index=pd.to_datetime(eqg.index); eqc=(Req["gross"]-Req["net"]); eqc.index=pd.to_datetime(eqc.index)
ovg=Rov["gross"].copy(); ovg.index=pd.to_datetime(ovg.index); ovc=Rov["cost"].copy(); ovc.index=pd.to_datetime(ovc.index)
for k in [1,2,3,5]:
    ck=(0.5*(eqg-k*eqc)+0.5*(ovg-k*ovc)).reindex(df.index).dropna()
    pk=perf(AG.aggressive_size(ck)[0]); base=perf(ck)
    print(f"  {k}x cost: combo(무레버) Sharpe={base['sharpe']:+.2f}·CAGR{base['cagr']*100:+.1f}% | +레버 Sharpe={pk['sharpe']:+.2f}·CAGR{pk['cagr']*100:+.1f}%")
print("  → trend sleeve 저턴오버라 결합은 equity 단독보다 비용내성 ↑ (분산이 cost도 완충)")
out=os.path.join(data.PHASE1A,"outputs","engine","combined_book_nav.csv")
pd.DataFrame({"eq":df["eq"],"ov":df["ov"],"combo":combo,"combo_lev":agg,"lev":lev}).to_csv(out)
print(f"\n  → {out}")
print("  ⚠️ 정직: combo Sharpe는 trend sleeve가 견인(0.85=강추세 레짐 flattered, 진짜는 ~0.5-0.6 보수). 분산은 진짜(+0.02 상관).")
print("  → 이게 '공격적 절대수익'의 현실 경로: 무상관 sleeve 2개 결합 후 레버리지(단일 sleeve 레버보다 robust). live 아님.")

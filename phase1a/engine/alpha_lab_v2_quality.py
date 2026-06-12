#!/usr/bin/env python3
"""PRAMANA Alpha Lab v2 — 후보 품질 분석 (수익 아니라 '진짜 catalyst만 걸러지나').
GPT/용하: v2 성공의 첫 게이트=후보 남발 안 하고 진짜 이유 있는 급등주만 잡는가. A/B/C/D 분류.
기존 v2_forward_log.csv(forward 로그) 분석. 무료 데이터 한계=진짜 catalyst 질은 뉴스 필요(근사만). PAPER."""
import os, warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, yfinance as yf
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
LOG=os.path.join(ROOT,"outputs","alpha_lab","v2_forward_log.csv"); PNG=os.path.join(ROOT,"outputs","v2_quality.png")
if not os.path.exists(LOG): print("v2 로그 없음 — alpha_lab_v2_scanner.py 먼저"); raise SystemExit
df=pd.read_csv(LOG); df["catalyst"]=df["catalyst"].fillna("none")
THEME={**{t:"반도체/HW" for t in ["NVDA","AMD","MU","AVGO","MRVL","ARM","SMCI"]},
       **{t:"AI/SW" for t in ["PLTR","AI","IONQ","RGTI","SNOW","NET","CRWD"]},
       **{t:"성장/투기" for t in ["TSLA","COIN","MSTR","HOOD","SOFI","RIVN","SMR","OKLO","DKNG","ROKU"]},
       **{t:"메가캡" for t in ["AAPL","META","AMZN","MSFT","GOOGL","NFLX"]},**{"SPY":"지수","QQQ":"지수"}}
df["theme"]=df["ticker"].map(lambda t:THEME.get(t,"기타"))
def label(r):  # A/B/C/D 근사 (무료 proxy: earnings/gap/rvol)
    e="earnings" in r["catalyst"]; g=r["gap"]>=0.03; rv=r["entry_rvol"]>=2.0
    if e and (g or rv): return "A (실적+수급)"
    if e or (g and rv): return "B (이벤트/강수급)"
    if g or rv: return "C (momentum only)"
    return "D (약함)"
df["grade"]=df.apply(label,axis=1)
# SPY 그날 방향
spy=yf.download("SPY",period="120d",interval="1d",auto_adjust=True,progress=False)
spc=(spy["Close"] if isinstance(spy.columns,pd.MultiIndex) else spy).squeeze(); spr=spc.pct_change()
spd={str(d.date()):(">0" if r>0 else "<=0") for d,r in spr.items()}
df["spy_day"]=df["date"].map(lambda d:spd.get(d,"?"))
nd=df["date"].nunique()
print(f"=== v2 후보 품질 ({len(df)}후보·{nd}거래일·하루평균 {len(df)/nd:.1f}개) ===")
print("\n[A/B/C/D 분류] (무료 proxy·진짜 catalyst 질은 뉴스 필요)")
gc=df["grade"].value_counts()
for g in ["A (실적+수급)","B (이벤트/강수급)","C (momentum only)","D (약함)"]:
    n=gc.get(g,0); print(f"  {g:<20} {n:>3}개 ({n/len(df)*100:>2.0f}%)")
ab=df["grade"].str.startswith(("A","B")).sum()
print(f"  → A/B(paper entry 후보)={ab}개({ab/len(df)*100:.0f}%) · C/D(거름)={len(df)-ab}개")
print("\n[테마 집중] (한 곳에 몰리면=분산 안 됨·시장 베타 위험)")
for t,n in df["theme"].value_counts().items(): print(f"  {t:<10} {n:>3}개 ({n/len(df)*100:.0f}%)")
print("\n[SPY 방향별] (강세일만 후보 몰리면=시장 베타)")
for s,n in df["spy_day"].value_counts().items(): print(f"  SPY {s:<4} {n:>3}개 ({n/len(df)*100:.0f}%)")
dd=df[df["spy_day"]=="<=0"]; print(f"  → SPY 하락일 후보 {len(dd)}개 — 이게 살아남으면 시장 베타와 분리 신호")
# 차트 2x2
plt.style.use("dark_background"); plt.rcParams.update({"figure.facecolor":"#070b16","axes.facecolor":"#0d1326","grid.alpha":.2,"font.size":9})
fig,ax=plt.subplots(2,2,figsize=(12,8))
gco=[gc.get(g,0) for g in ["A (실적+수급)","B (이벤트/강수급)","C (momentum only)","D (약함)"]]
ax[0,0].bar(["A","B","C","D"],gco,color=["#34d399","#22d3ee","#fbbf24","#f87171"]); ax[0,0].set_title("catalyst 등급 (A/B=진입후보·C/D=거름)")
dc=df.groupby("date").size(); ax[0,1].plot(range(len(dc)),dc.values,color="#22d3ee",marker="o",ms=3); ax[0,1].axhline(dc.mean(),color="#f59e0b",ls="--",lw=1,label=f"평균 {dc.mean():.1f}"); ax[0,1].set_title("하루 후보 수 (남발 점검)"); ax[0,1].legend(fontsize=8)
tc=df["theme"].value_counts(); ax[1,0].barh(tc.index[::-1],tc.values[::-1],color="#a78bfa"); ax[1,0].set_title("테마 집중")
sc=df["spy_day"].value_counts(); ax[1,1].bar([f"SPY {i}" for i in sc.index],sc.values,color=["#34d399" if i==">0" else "#f87171" for i in sc.index]); ax[1,1].set_title("SPY 방향별 후보 (강세 의존?)")
fig.suptitle("Alpha Lab v2 후보 품질 — 수익 아니라 '진짜 이유 있는 급등주만 걸러지나'",color="#22d3ee",fontsize=12,y=1.0)
fig.tight_layout(); fig.savefig(PNG,dpi=115,bbox_inches="tight",facecolor="#070b16"); plt.close(fig)
print(f"\n정직: A/B/C/D는 무료 proxy(earnings date+gap+RVOL)지 진짜 catalyst 질(실적 beat·가이던스·뉴스 시각) 아님. 그건 뉴스/펀더멘털 데이터(LLM 분류 or 유료) 필요. 이 분석=후보 *남발/집중/베타의존* 게이트지 수익 검증 아님.\n✅ PNG: {PNG}")
if __name__=="__main__": pass

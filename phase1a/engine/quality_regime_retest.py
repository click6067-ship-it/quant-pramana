#!/usr/bin/env python3
"""PRAMANA V5 Research thread 2: quality(gp/assets) 레짐 retest — *유료 Sharadar 펀더멘털* 사용.
질문: quality는 standalone 실패(decay·long-only<cap-weight)했지만, Core(SPY/QQQ) 대비 *특정 레짐서 비용후 한계기여*가 있나?(core-satellite 잣대)
사전등록 kill 먼저(결과 전 고정). paper·비용후. cached 유료 broad_SF1·broad_SEP·broad_universe."""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import data
ENG=os.path.join(data.PHASE1A,"outputs","engine")
KILLS={"K1":"net 한계기여(0.85core+0.15qual − core) ≤ 0 *모든* 레짐 → REJECT",
       "K2":"quality 월 IC-IR < 0.2 → 노이즈",
       "K3":"전반/후반 한계기여 부호 반대 → 불안정(인샘플)",
       "K4":"작동 레짐 있어도 그 기여 < 비용 → 무의미"}
print("="*78); print("사전등록 KILL(결과 전):"); [print(f"  {k}: {v}") for k,v in KILLS.items()]; print("="*78)
uni=pd.read_csv(os.path.join(data.PHASE1A,"outputs","broad_universe_top1500.csv")); uni["asof"]=pd.to_datetime(uni["asof"])
sf1=data.load("broad_SF1"); sf1["datekey"]=pd.to_datetime(sf1["datekey"])
px=data.load("broad_SEP",usecols=["ticker","date","closeadj"]).pivot_table(index="date",columns="ticker",values="closeadj").sort_index()
etf=data.load("SFP_FUNDS",usecols=["ticker","date","closeadj"]).pivot_table(index="date",columns="ticker",values="closeadj").sort_index()
rebal=sorted(uni["asof"].unique()); rebal=[t for t in rebal if t in px.index or px.index[px.index<=t].size>0]
pxr=px.reindex(rebal,method="ffill"); mret=pxr.pct_change()
spy=etf["SPY"]; sma=spy.rolling(200).mean()
spyr=spy.reindex(rebal,method="ffill"); smar=sma.reindex(rebal,method="ffill")
cret=0.5*etf["SPY"].reindex(rebal,method="ffill").pct_change()+0.5*etf["QQQ"].reindex(rebal,method="ffill").pct_change()
BPS=12  # quality 월 리밸 왕복 비용
rows=[]; prev=None; ics=[]
for i in range(len(rebal)-1):
    t,t1=rebal[i],rebal[i+1]
    members=set(uni[uni["asof"]==t]["ticker"])
    q=sf1[sf1["datekey"]<=t].sort_values("datekey").groupby("ticker").last()
    q=q.loc[[x for x in q.index if x in members]].copy()
    q["qual"]=q["gp"]/q["assets"]; q=q.replace([np.inf,-np.inf],np.nan).dropna(subset=["qual"])
    if len(q)<50: continue
    thr=q["qual"].quantile(0.8); longs=[x for x in q.index[q["qual"]>=thr] if x in mret.columns]
    fwd=mret.loc[t1]
    rq=fwd.reindex(longs).mean()
    # turnover 비용
    cost=(len(set(longs)^set(prev))/max(1,len(longs))*BPS/1e4) if prev is not None else 0; prev=longs
    rq_net=rq-cost
    reg = "trend" if (pd.notna(smar.get(t)) and spyr.get(t,0)>smar.get(t)) else "chop/down"
    # IC: quality rank vs fwd return
    common=[x for x in q.index if x in fwd.index]
    if len(common)>30: ics.append(q["qual"].reindex(common).rank(pct=True).corr(fwd.reindex(common),method="spearman"))
    rows.append({"t":t1,"rq_net":rq_net,"core":cret.get(t1,np.nan),"reg":reg})
df=pd.DataFrame(rows).dropna()
df["marg"]=(0.85*df["core"]+0.15*df["rq_net"])-df["core"]   # 위성 15% 한계기여
ann=lambda s: s.mean()*12
ic=pd.Series(ics); icir=ic.mean()/ic.std() if len(ic)>1 and ic.std()>0 else float("nan")
print(f"\n결과(유료 Sharadar gp/assets·{len(df)}개월):")
print(f"  quality long-only net 연 {ann(df['rq_net'])*100:+.1f}% · Core 연 {ann(df['core'])*100:+.1f}% · 월 IC-IR {icir:+.2f}")
print(f"  15% 위성 한계기여(전체) 연 {ann(df['marg'])*100:+.2f}%p")
for reg,g in df.groupby("reg"):
    print(f"  [{reg:<9}] {len(g)}개월 · 한계기여 연 {ann(g['marg'])*100:+.2f}%p · quality net 연 {ann(g['rq_net'])*100:+.1f}%")
h=len(df)//2; m1=ann(df["marg"].iloc[:h]); m2=ann(df["marg"].iloc[h:])
print(f"  전/후반 한계기여: {m1*100:+.2f}%p / {m2*100:+.2f}%p")
# KILL
fired=[]
byreg={r:ann(g["marg"]) for r,g in df.groupby("reg")}
if all(v<=0 for v in byreg.values()): fired.append("K1 모든레짐 기여≤0")
if not(icir>0.2): fired.append("K2 IC-IR<0.2")
if np.sign(m1)!=np.sign(m2): fired.append("K3 부호flip")
best=max(byreg.values()) if byreg else 0
if best>0 and best<0.005: fired.append("K4 작동레짐 기여<비용")
label="REJECT" if "K1 모든레짐 기여≤0" in fired else ("NEEDS_EVIDENCE" if fired else "RESEARCH_ONLY(레짐조건부 약한 후보)")
print(f"\n{'─'*78}\nKILL: {fired if fired else '없음'} → 라벨: {label}")
print(f"정직: quality는 quarantine서 이미 decay·long-only<cap-weight. 레짐조건부 한계기여만 봄. 유료 Sharadar 펀더멘털 실사용.")
open(os.path.join(ENG,"quality_regime_retest_verdict.txt"),"w").write(f"quality 레짐 retest · {label}\nnet연{ann(df['rq_net'])*100:+.1f}%·IC-IR{icir:+.2f}·한계기여연{ann(df['marg'])*100:+.2f}%p·레짐{ {r:round(v*100,2) for r,v in byreg.items()} }·KILL{fired}\n")
df.to_csv(os.path.join(ENG,"quality_regime_retest.csv"),index=False)
print(f"→ outputs/engine/quality_regime_retest_verdict.txt")

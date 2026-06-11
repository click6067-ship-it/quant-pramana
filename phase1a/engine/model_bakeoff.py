#!/usr/bin/env python3
"""모델 bake-off (Codex 요구 empirical) — walk-forward OOS·포트폴리오레벨·비용후.
rank baseline(z 평균) vs ridge vs GBM. 동일 split. 5피처(momentum/quality/value/lowvol/event) 다 줌=ML에 유리.
판정: ML이 dumb equal-weight를 OOS net Sharpe로 *이기나?* 못 이기면 Codex의 'theater' 확증. 튜닝 0(기본 1세트). 새 데이터 0·결제 0.
trial ledger: 모델 3개(+baseline). 다중검정 인지."""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import data, features as F, cost as C, universe as U
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import HistGradientBoostingRegressor

FEATS=["momentum","quality","value","lowvol","event"]; WARMUP=36

def panel():
    px=data.load("broad_SEP",usecols=["ticker","date","closeadj"]).pivot_table(index="date",columns="ticker",values="closeadj").sort_index()
    pb=data.load("broad_DAILY_pb",usecols=["ticker","date","pb"]).pivot_table(index="date",columns="ticker",values="pb").sort_index()
    mc=data.load("DAILY_all",usecols=["ticker","date","marketcap"]).pivot_table(index="date",columns="ticker",values="marketcap").sort_index()
    sf1=data.load("broad_SF1"); sf1x=data.load("broad_SF1_ext"); sector=data.load_tickers()["sector"]
    uni=U.rank_universe(1,1500); members={d:set(g) for d,g in uni.groupby("asof")["ticker"]}; rebal=sorted(uni["asof"].unique())
    mpx=px.reindex(rebal,method="pad"); fwd=mpx.shift(-1)/mpx-1; mcg=mc.reindex(rebal,method="pad")
    FM={"momentum":F.momentum(px,rebal),"quality":F.quality(sf1,rebal,px.columns),"value":F.value(pb,rebal),"lowvol":F.lowvol(px,rebal)}
    EQ=F.event_subsignals(sf1x,rebal); rows=[]
    for t in rebal[:-1]:
        mem=[c for c in px.columns if c in members[t]]
        d=pd.DataFrame({k:FM[k].loc[t].reindex(mem) for k in FM})
        for k in F.EVENT_COLS: d[k]=EQ[k].loc[t].reindex(mem)
        d["fwd"]=fwd.loc[t].reindex(mem); d["mc"]=mcg.loc[t].reindex(mem); d["sec"]=sector.reindex(mem).values
        d["event"]=F.composite(d,F.EVENT_COLS)
        d=d.dropna(subset=FM.keys() if False else ["momentum","quality","value","lowvol","event","fwd","mc"])
        if len(d)<100: continue
        for k in FEATS: d[k+"_z"]=F.zscore(d[k])
        d["asof"]=t; d["ticker"]=d.index; rows.append(d.reset_index(drop=True))
    return pd.concat(rows,ignore_index=True), rebal

def ls_net(g, scorecol):
    """sector-neutral score → top/bottom quintile L/S net(거래비용+borrow). 책과 동일."""
    g=g.dropna(subset=[scorecol]).copy()
    g["sn"]=g[scorecol]-g.groupby("sec")[scorecol].transform("mean")
    rk=g["sn"].rank(pct=True); L=g[rk>=0.8]; S=g[rk<=0.2]
    if len(L)<10 or len(S)<10: return np.nan
    gross=L["fwd"].mean()-S["fwd"].mean()
    cL=C.tier_marketcap_bps(L["mc"]).mean()/C.BPS; cS=C.tier_marketcap_bps(S["mc"]).mean()/C.BPS
    bor=(0.005/12)  # 보수 borrow
    return gross-(cL+cS)*1.0-bor   # 1리밸런스 회전 가정(단순·모델간 동일조건)

def sharpe(s): s=s.dropna(); return s.mean()/s.std()*np.sqrt(12) if s.std()>0 else np.nan
def cagr(s): s=s.dropna(); return (1+s).prod()**(12/len(s))-1

print("="*88); print("MODEL BAKE-OFF — walk-forward OOS·포트폴리오레벨·비용후 (rank vs ridge vs GBM)"); print("="*88)
L,rebal=panel()
Xcols=[k+"_z" for k in FEATS]
months=sorted(L["asof"].unique())
res={"baseline":{}, "ridge":{}, "gbm":{}}
print(f"패널 {len(L)} 멤버-월 · {len(months)}월 · OOS 시작 {WARMUP}월 후 · 피처 {FEATS}")
for i,t in enumerate(months):
    cur=L[L["asof"]==t]
    # baseline = z 평균(무학습)
    res["baseline"][t]=ls_net(cur.assign(s=cur[Xcols].mean(axis=1)),"s")
    if i<WARMUP: continue
    tr=L[L["asof"]<t]; Xtr=tr[Xcols].values; ytr=tr["fwd"].values; Xte=cur[Xcols].values
    sc=StandardScaler().fit(Xtr)
    rid=Ridge(alpha=10.0).fit(sc.transform(Xtr),ytr)
    res["ridge"][t]=ls_net(cur.assign(s=rid.predict(sc.transform(Xte))),"s")
    gbm=HistGradientBoostingRegressor(max_iter=100,max_depth=3,learning_rate=0.05,min_samples_leaf=200).fit(Xtr,ytr)
    res["gbm"][t]=ls_net(cur.assign(s=gbm.predict(Xte)),"s")

oos=months[WARMUP:]
print(f"\n[OOS {oos[0].date()}~{oos[-1].date()}, {len(oos)}월] — *공정비교는 OOS 구간만*")
print(f"  {'model':10s} {'OOS Sharpe':>11s} {'OOS CAGR':>10s} {'전체 Sharpe':>11s}")
for m in ["baseline","ridge","gbm"]:
    s=pd.Series(res[m]); soos=s.reindex(oos)
    print(f"  {m:10s} {sharpe(soos):>+11.2f} {cagr(soos)*100:>+9.2f}% {sharpe(s):>+11.2f}")
b=sharpe(pd.Series(res['baseline']).reindex(oos)); r=sharpe(pd.Series(res['ridge']).reindex(oos)); gg=sharpe(pd.Series(res['gbm']).reindex(oos))
print("\n[판정] ML이 dumb equal-weight를 OOS net Sharpe로 이기나?")
print(f"  ridge {'>' if r>b else '<='} baseline ({r:+.2f} vs {b:+.2f}) · gbm {'>' if gg>b else '<='} baseline ({gg:+.2f} vs {b:+.2f})")
win = (r>b+0.05) or (gg>b+0.05)
print(f"  → {'ML 증분 알파 있음(추가검증 필요)' if win else 'ML 증분 없음 = Codex의 theater 확증(equal-weight 못 이김)'}")
print(f"  trial ledger: 모델 3 시도(baseline/ridge/gbm)·튜닝0·동일 walk-forward. 다중검정 인지(추가시 DSR/PBO).")
pd.DataFrame(res).to_csv(os.path.join(data.PHASE1A,"outputs","engine","model_bakeoff.csv"))
print("  → outputs/engine/model_bakeoff.csv · ⚠️ 포트폴리오레벨 OOS·비용후·튜닝0. 결론은 deep-research+council과 합산.")

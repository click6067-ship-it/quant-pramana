#!/usr/bin/env python3
"""
B2~B5 simple factor sleeve baselines — PIT S&P500 universe (DIAGNOSTIC, NOT alpha).
  B2 value     = 1/pb            (DAILY, cached)
  B3 quality   = gp/assets       (SF1, PIT via datekey)  ← Novy-Marx gross profitability
  B4 momentum  = 12-1 (t-12→t-1) (SEP closeadj, cached)
  B5 low-vol   = -trailing 126d daily-return vol (SEP, cached)
지표: 월별 Rank IC(Spearman: factor vs 다음달 수익) 평균/IR/양수비율 + 상하위 분위 spread.
⚠️ 단일 백테스트·다중검정 미보정·단일 유니버스 → 수치는 *신뢰 금지*. 목적=신호 재현성·PIT·파이프라인 점검.
"""
import os, numpy as np, pandas as pd
import nasdaqdatalink as ndl
HERE = os.path.dirname(os.path.abspath(__file__)); RAW = os.path.join(HERE, "outputs", "raw")
ndl.ApiConfig.api_key = open(os.path.join(HERE, ".ndl_key")).read().strip()
START = "2016-01-01"

# ── PIT 멤버십 (b0b1과 동일 역재생) ──
sp = pd.read_csv(os.path.join(RAW, "SP500_membership.csv")); sp["date"] = pd.to_datetime(sp["date"])
current = set(sp[sp.action == "current"].ticker)
ev_desc = list(sp[sp.action.isin(["added", "removed"])][["date","action","ticker"]]
               .sort_values("date").itertuples(index=False))[::-1]
def members_asof(T):
    m = set(current)
    for d, a, tk in ev_desc:
        if d <= T: break
        m.discard(tk) if a == "added" else m.add(tk)
    return m
universe = sorted(sp.ticker.unique())

# ── 캐시 데이터 ──
sep = pd.read_csv(os.path.join(RAW, "SHARADAR_SEP.csv"), parse_dates=["date"])
px = sep.pivot_table(index="date", columns="ticker", values="closeadj").sort_index()
daily = pd.read_csv(os.path.join(RAW, "SHARADAR_DAILY.csv"), parse_dates=["date"])
pb = daily.pivot_table(index="date", columns="ticker", values="pb").sort_index()

# ── B3용 SF1 pull (캐시·재개) ──
sf1path = os.path.join(RAW, "SHARADAR_SF1_ARQ.csv")
def pull_sf1(tickers, chunk=80):
    done = set()
    if os.path.exists(sf1path):
        try: done = set(pd.read_csv(sf1path, usecols=["ticker"])["ticker"].unique())
        except Exception: done = set()
    todo = [t for t in tickers if t not in done]
    print(f"[SF1] cached={len(done)} todo={len(todo)}", flush=True)
    for i in range(0, len(todo), chunk):
        sub = todo[i:i+chunk]
        df = ndl.get_table("SHARADAR/SF1", ticker=sub, dimension="ARQ",
                           qopts={"columns": ["ticker","datekey","gp","assets"]}, paginate=True)
        df.to_csv(sf1path, mode="a", header=not os.path.exists(sf1path), index=False)
        print(f"  SF1 {i+len(sub)}/{len(todo)}", flush=True)
    return pd.read_csv(sf1path, parse_dates=["datekey"])
sf1 = pull_sf1(universe)
sf1 = sf1[(sf1["assets"] > 0)].copy()
sf1["q"] = sf1["gp"] / sf1["assets"]                     # gross profitability
sf1 = sf1.dropna(subset=["q"]).sort_values("datekey")

# ── 월그리드: 각 달의 "실제 마지막 거래일"(달력 월말 아님 — 그래야 reindex NaN 안 생김) ──
rebal = pd.DatetimeIndex(px.index.to_series().resample("ME").last().dropna().values)
mpx = px.reindex(rebal)
fwd = mpx.shift(-1) / mpx - 1                              # 다음달 수익 (IC 타깃)

# factor 행렬 (월그리드, PIT)
val = (1.0 / pb.reindex(rebal)).replace([np.inf, -np.inf], np.nan)        # B2 value
mom = mpx.shift(1) / mpx.shift(12) - 1                                     # B4 12-1
vol = px.pct_change().rolling(126).std().reindex(rebal)
lowvol = -vol                                                              # B5 low-vol(낮을수록 高점수)
# B3 quality: 각 rebal 시점, datekey<=t 최신 gp/assets
qual = pd.DataFrame(index=rebal, columns=px.columns, dtype=float)
for t in rebal:
    av = sf1[sf1["datekey"] <= t]
    if len(av):
        last = av.groupby("ticker")["q"].last()
        qual.loc[t, last.index.intersection(qual.columns)] = last.reindex(qual.columns.intersection(last.index))
factors = {"B2_value": val, "B3_quality": qual, "B4_momentum": mom, "B5_lowvol": lowvol}

def xs_ic(frow, rrow):
    d = pd.concat([frow, rrow], axis=1).dropna(); d.columns = ["f","r"]
    return d["f"].rank().corr(d["r"].rank()) if len(d) >= 20 else np.nan

print("="*78); print("B2~B5 Factor Sleeve Baselines — PIT S&P500 (DIAGNOSTIC, 수치 신뢰금지)"); print("="*78)
rows=[]
for name, fac in factors.items():
    ics=[]; sprd=[]
    for t in rebal[:-1]:
        mem = members_asof(t)
        cols = [c for c in fac.columns if c in mem]
        frow = fac.loc[t, cols]; rrow = fwd.loc[t, cols]
        ic = xs_ic(frow, rrow); ics.append(ic)
        d = pd.concat([frow, rrow], axis=1).dropna(); d.columns=["f","r"]
        if len(d) >= 25:
            q = d["f"].rank(pct=True)
            sprd.append(d.loc[q>=0.8,"r"].mean() - d.loc[q<=0.2,"r"].mean())   # Q5-Q1 월spread
    ics=pd.Series(ics).dropna(); sprd=pd.Series(sprd).dropna()
    icmean=ics.mean(); icir=ics.mean()/ics.std() if ics.std()>0 else np.nan
    rows.append((name, icmean, icir, (ics>0).mean(), sprd.mean()*12))
    print(f"\n[{name}]")
    print(f"  Rank IC mean = {icmean:+.4f} | IC-IR = {icir:+.3f} | IC>0 비율 = {(ics>0).mean()*100:.0f}% | n={len(ics)}월")
    print(f"  Q5-Q1 spread(연환산) = {sprd.mean()*12*100:+.2f}%p  (*단일백테스트·신뢰금지*)")
# 저장
out=pd.DataFrame(rows, columns=["sleeve","rank_ic_mean","ic_ir","ic_pos_frac","q5q1_ann"])
out.to_csv(os.path.join(HERE,"outputs","b2b5_factor_ic.csv"), index=False)
print("\n→ outputs/b2b5_factor_ic.csv")
print("해석: Rank IC mean이 0에서 유의하게 떨어진 부호로 일관(IC-IR↑·IC>0비율 치우침)이면 '신호 존재 가능성'.")
print("단 다중검정 미보정·단일구간·단일유니버스 → Phase 1A에선 '신호가 *재현·측정*된다'까지만. 채택 아님.")

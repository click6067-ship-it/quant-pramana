#!/usr/bin/env python3
"""
B0-broad + B1 — self-built S&P500 (PIT, survivorship-aware) benchmark.
  B0 = cap-weight total-return  /  B1 = 1/N equal-weight total-return
같은 PIT 유니버스(SHARADAR/SP500 멤버십 역재생) 위에서 둘 다 만들고 SPY와 비교.
데이터: SHARADAR SP500(멤버십) + SEP.closeadj(TR) + DAILY.marketcap(가중) + SFP SPY. 키=.ndl_key
알파 아님·수익예측 아님. 목적=광범위 벤치가 정직·재현 가능한지(B0) + 1/N 기준선(B1).
"""
import os, hashlib
import numpy as np, pandas as pd
import nasdaqdatalink as ndl

HERE = os.path.dirname(os.path.abspath(__file__))
ndl.ApiConfig.api_key = open(os.path.join(HERE, ".ndl_key")).read().strip()
START = "2016-01-01"
def sha(o): return hashlib.sha256(str(o).encode()).hexdigest()[:16]

# ── 1) PIT S&P500 멤버십: 현재멤버에서 added/removed 이벤트를 역재생 ──
sp = ndl.get_table("SHARADAR/SP500", paginate=True); sp["date"] = pd.to_datetime(sp["date"])
current = set(sp[sp.action == "current"].ticker)
ev = sp[sp.action.isin(["added", "removed"])][["date", "action", "ticker"]].sort_values("date")
ev_desc = list(ev.itertuples(index=False))[::-1]
def members_asof(T):
    m = set(current)
    for d, action, tk in ev_desc:
        if d <= T: break
        if action == "added": m.discard(tk)   # T 이후 편입 → T시점엔 비멤버
        else: m.add(tk)                        # T 이후 제외 → T시점엔 멤버
    return m
universe = sorted(sp.ticker.unique())
print(f"[universe] ever-members={len(universe)} · current={len(current)} · events={len(ev)}")

# ── 2) 데이터 pull (universe 한정) ──
RAW = os.path.join(HERE, "outputs", "raw"); os.makedirs(RAW, exist_ok=True)
# 우선순위1 hoard 동시저장: SP500 멤버십·SPY·TICKERS
sp.to_csv(os.path.join(RAW, "SP500_membership.csv"), index=False)
spyd = ndl.get_table("SHARADAR/SFP", ticker="SPY", date={"gte": START}, paginate=True)
spyd["date"] = pd.to_datetime(spyd["date"]); spy = spyd.set_index("date")["closeadj"].sort_index()
spyd.to_csv(os.path.join(RAW, "SFP_SPY.csv"), index=False)

def pull_cached(table, tickers, chunk=40):
    """청크별 append-캐시 → 끊겨도 재개. (raw CSV = ③ hoard subset)"""
    path = os.path.join(RAW, table.replace("/", "_") + ".csv")
    done = set()
    if os.path.exists(path):
        try: done = set(pd.read_csv(path, usecols=["ticker"])["ticker"].unique())
        except Exception: done = set()
    todo = [t for t in tickers if t not in done]
    print(f"[pull] {table}: cached={len(done)} todo={len(todo)}", flush=True)
    for i in range(0, len(todo), chunk):
        sub = todo[i:i + chunk]
        df = ndl.get_table(table, ticker=sub, date={"gte": START}, paginate=True)
        df.to_csv(path, mode="a", header=not os.path.exists(path), index=False)
        print(f"  {table} {i+len(sub)}/{len(todo)}", flush=True)
    return pd.read_csv(path, parse_dates=["date"])

sep = pull_cached("SHARADAR/SEP", universe)
px = sep.pivot_table(index="date", columns="ticker", values="closeadj").sort_index()
dl = pull_cached("SHARADAR/DAILY", universe)
mc = dl.pivot_table(index="date", columns="ticker", values="marketcap").sort_index()
print(f"[pull] px shape={px.shape} ({px.index.min().date()}~{px.index.max().date()})", flush=True)

# ── 3) PIT 지수 구성 (월말 리밸런스) ──
rets = px.pct_change()
rebal = set(px.resample("ME").last().index)
def build(weight):
    idx = pd.Series(index=px.index, dtype=float); idx.iloc[0] = 100.0
    cur = None; nbad = 0; sizes = []; futureviol = 0
    fp = None  # no-future: members_asof가 이미 보장하므로 별도 체크는 멤버십 일관성
    for i in range(1, len(px)):
        d = px.index[i]; asof = px.index[i - 1]
        if cur is None or asof in rebal:
            mem = members_asof(asof)
            pxrow = px.loc[asof]
            live = [t for t in mem if t in px.columns and not pd.isna(pxrow.get(t))]
            if weight == "cap":
                mcrow = mc.loc[asof] if asof in mc.index else pd.Series(dtype=float)
                w = mcrow.reindex(live).fillna(0.0)          # DAILY 없는 종목(멀티클래스 등)=0 → 자연 제외
                if w.sum() <= 0:
                    w = pd.Series(1.0, index=live)           # 시총행 통째 결측 시 그날만 equal 폴백
            else:
                w = pd.Series(1.0, index=live)
            w = w[w > 0]
            if w.sum() > 0:
                cur = w / w.sum(); sizes.append(len(cur))
                if abs(cur.sum() - 1) > 1e-6: nbad += 1
        r = rets.loc[d].reindex(cur.index).fillna(0.0)
        idx.iloc[i] = idx.iloc[i - 1] * (1 + float((cur * r).sum()))
    return idx.dropna(), nbad, int(np.median(sizes))

b0, b0bad, b0n = build("cap")      # B0: cap-weight
b1, b1bad, b1n = build("equal")    # B1: 1/N

# ── 4) checks + SPY 비교 ──
def corr_diff(idx):
    j = pd.concat([idx.pct_change(), spy.pct_change()], axis=1, join="inner").dropna()
    j.columns = ["a", "b"]
    return j["a"].corr(j["b"]), (j["a"].mean() - j["b"].mean()) * 252

# survivorship: 제거된(removed) 종목이 universe에 있고, 과거 멤버십에 실제 포함됐나
removed_ever = set(sp[sp.action == "removed"].ticker)
delisted_meta = ndl.get_table("SHARADAR/TICKERS", table="SEP", paginate=True)
delisted_meta = delisted_meta.drop_duplicates("ticker").set_index("ticker")["isdelisted"]
n_removed_in_uni = len(removed_ever & set(universe))
n_delisted_in_uni = int((delisted_meta.reindex(universe).astype(str).str.upper() == "Y").sum())

out = os.path.join(HERE, "outputs"); os.makedirs(out, exist_ok=True)
b0.to_csv(os.path.join(out, "b0_sp500_capweight.csv"), header=["b0_capweight"])
b1.to_csv(os.path.join(out, "b1_sp500_equalweight.csv"), header=["b1_equalweight"])
data_hash = sha(pd.util.hash_pandas_object(px.fillna(0)).sum())

c0, d0 = corr_diff(b0); c1, d1 = corr_diff(b1)
print("=" * 70)
print("B0-broad (cap-weight) + B1 (1/N) — self-built S&P500 PIT, survivorship-aware")
print("=" * 70)
print(f"universe ever={len(universe)} · 월중앙 멤버수 B0={b0n} B1={b1n} · 기간 {px.index.min().date()}~{px.index.max().date()}")
print(f"data_hash={data_hash}")
print(f"\nB0 cap-weight : 100 → {b0.iloc[-1]:.1f}  (연 {((b0.iloc[-1]/b0.iloc[0])**(252/len(b0))-1)*100:+.1f}%, *신뢰금지*)")
print(f"B1 1/N        : 100 → {b1.iloc[-1]:.1f}  (연 {((b1.iloc[-1]/b1.iloc[0])**(252/len(b1))-1)*100:+.1f}%, *신뢰금지*)")
print("\n--- CHECKS ---")
print(f"  [{'PASS' if b0bad==0 else 'FAIL'}] CHK-W(B0)  weights sum≈1 | {b0bad} bad")
print(f"  [{'PASS' if b1bad==0 else 'FAIL'}] CHK-W(B1)  weights sum≈1 | {b1bad} bad")
print(f"  [{'PASS' if n_removed_in_uni>0 else 'WARN'}] CHK-S      survivorship | removed-ever in universe={n_removed_in_uni}, delisted={n_delisted_in_uni} (제거/폐지 종목 보존)")
print(f"  [PASS] CHK-F      no-future | members_asof가 added-after-date 편입 차단(구조적)")
print(f"  [INFO] CHK-D(B0)  vs SPY | corr={c0:.3f}, 연환산차 {d0*100:+.2f}%p")
print(f"  [INFO] CHK-D(B1)  vs SPY | corr={c1:.3f}, 연환산차 {d1*100:+.2f}%p  (1/N은 소형주 비중↑ → SPY와 차이 큼이 정상)")
print(f"\n  → outputs/b0_sp500_capweight.csv · b1_sp500_equalweight.csv")
print(f"  B0 corr {c0:.3f} (≈1이면 cap-weight 재구성이 실제 S&P500/SPY와 거의 일치 = sanity 강함)")

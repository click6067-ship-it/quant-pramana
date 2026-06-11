#!/usr/bin/env python3
"""V2.1 rapid sign screen — ZACKS/EEH 2018 무료샘플(obs_date PIT) + 기존 SEP 가격.
목적: 결제 전 *부호 확인만*. full validation 아님·튜닝 0·window 사냥 0.
신호 primary=(eps_cnt_est_rev_up - eps_cnt_est_rev_down)/max(eps_cnt_est,1) [front quarter] · fwd=21 trading days(obs_date 기준 PIT)."""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "engine"))
import data, nasdaqdatalink as ndl
ndl.ApiConfig.api_key = open("/home/click/ghq/github.com/click6067-ship-it/quant-pramana/phase1a/.ndl_key").read().strip()
RAW = os.path.join(data.PHASE1A, "outputs", "raw"); OUT = os.path.join(data.PHASE1A, "outputs")
EEH = os.path.join(RAW, "zacks_eeh_2018.csv")
COLS = ["ticker", "obs_date", "per_end_date", "per_type", "eps_cnt_est", "eps_cnt_est_rev_up", "eps_cnt_est_rev_down"]

# ── pull EEH(2018 샘플) for broad union (resumable) ──
univ = sorted(pd.read_csv(os.path.join(OUT, "broad_universe_top1500.csv"))["ticker"].unique())
done = set()
if os.path.exists(EEH):
    try: done = set(pd.read_csv(EEH, usecols=["ticker"])["ticker"].unique())
    except Exception: done = set()
todo = [t for t in univ if t not in done]
print(f"[EEH pull] union={len(univ)} cached={len(done)} todo={len(todo)}", flush=True)
for i in range(0, len(todo), 40):
    sub = todo[i:i + 40]
    try:
        df = ndl.get_table("ZACKS/EEH", ticker=sub, qopts={"columns": COLS}, paginate=True)
    except Exception as e:
        print(f"  chunk {i} err {str(e)[:60]}", flush=True); continue
    if len(df): df.to_csv(EEH, mode="a", header=not os.path.exists(EEH), index=False)
    if (i // 40) % 10 == 0: print(f"  EEH {i+len(sub)}/{len(todo)}", flush=True)
print("[EEH pull done]", flush=True)

# ── analyze ──
e = pd.read_csv(EEH, parse_dates=["obs_date", "per_end_date"])
e = e[e["per_type"] == "Q"]                                  # 분기 추정
e = e[e["per_end_date"] >= e["obs_date"]]                    # front quarter(미래)
e = e.sort_values("per_end_date").groupby(["ticker", "obs_date"], as_index=False).first()
e["sig"] = (e["eps_cnt_est_rev_up"] - e["eps_cnt_est_rev_down"]) / e["eps_cnt_est"].clip(lower=1)
e["sig_raw"] = e["eps_cnt_est_rev_up"] - e["eps_cnt_est_rev_down"]
e = e.dropna(subset=["sig"])

px = data.load("broad_SEP", usecols=["ticker", "date", "closeadj"]).pivot_table(index="date", columns="ticker", values="closeadj").sort_index()
ztk = set(e["ticker"].unique()); ptk = set(px.columns); mapped = ztk & ptk
map_rate = len(mapped) / max(len(ztk), 1)

# fwd 21 trading days (obs_date 기준; 진입 obs일 종가, +21 청산)
rows = []
for tk, g in e[e["ticker"].isin(mapped)].groupby("ticker"):
    s = px[tk].dropna(); idx = s.index; vals = s.values; n = len(s)
    for _, r in g.iterrows():
        p = idx.searchsorted(r["obs_date"])
        if p >= n or p + 21 >= n: continue
        fwd = vals[p + 21] / vals[p] - 1
        if not np.isfinite(fwd): continue
        rows.append((tk, r["obs_date"], r["sig"], r["sig_raw"], fwd))
D = pd.DataFrame(rows, columns=["ticker", "obs_date", "sig", "sig_raw", "fwd"])
D["month"] = D["obs_date"].dt.to_period("M")
# 월별 cross-section: (ticker,month) 최신 obs만
D = D.sort_values("obs_date").groupby(["ticker", "month"], as_index=False).last()

def screen(col):
    ics = []; q = []
    for m, g in D.groupby("month"):
        g = g.dropna(subset=[col, "fwd"])
        if len(g) < 20: continue
        ics.append(g[col].rank().corr(g["fwd"].rank()))
        rk = g[col].rank(pct=True)
        q.append(g[rk >= 0.8]["fwd"].mean() - g[rk <= 0.2]["fwd"].mean())
    ics = pd.Series(ics).dropna(); q = pd.Series(q)
    return ics.mean(), (ics.mean() / ics.std() if ics.std() > 0 else np.nan), q.mean(), len(ics)

print("=" * 76); print("V2.1 ZACKS/EEH 2018 RAPID SIGN SCREEN (결제전 부호확인·튜닝0)"); print("=" * 76)
print(f"EEH tickers={len(ztk)} · SEP 매핑={len(mapped)} ({map_rate*100:.0f}%) · 이벤트(21d fwd 가능)={len(D)} · 월수={D['month'].nunique()}")
for name, col in [("primary (rev_up-rev_down)/cnt", "sig"), ("raw rev_up-rev_down (참고)", "sig_raw")]:
    ic, icir, qsp, nm = screen(col)
    print(f"\n[{name}]  n={nm}월")
    print(f"  Rank IC={ic:+.4f} · IC-IR={icir:+.3f} · Q5-Q1(21d)={qsp*100:+.2f}%")

icp, _, qp, nmp = screen("sig")
verdict = "PASS(부호 OK → 가격확인 후 full kill-test)" if (icp > 0 and qp > 0 and len(mapped) >= 100 and nmp >= 6) else "FAIL(부호/샘플 불충분 → 축 HOLD/CLOSE)"
print("\n" + "=" * 76); print(f"판정: {verdict}")
print(f"  기준: Rank IC>0({icp:+.4f}) · Q5-Q1>0({qp*100:+.2f}%) · mapping≥100({len(mapped)}) · 월≥6({nmp})")
print("  ⚠️ 1년·1레짐 = 결론 아님, *부호 스크린*. 결제·튜닝·window 사냥 0.")

#!/usr/bin/env python3
"""v2.0 True PEAD — 사전등록 Protocol v0.1 구현(1회·튜닝없음). event-time(공시앵커).
Event=SF1 datekey · reaction=[-1,+1] · drift=[+2,+21](진입 +2, no look-ahead) · top-1500 PIT · marketcap tier 비용 round-trip.
engine.data·cost 재사용. kill 사전박음 대조."""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "engine"))
import data, cost as C
from math import erf, sqrt
OUT = os.path.join(data.PHASE1A, "outputs")

px = data.load("broad_SEP", usecols=["ticker", "date", "closeadj"]).pivot_table(index="date", columns="ticker", values="closeadj").sort_index()
sf1 = data.load("broad_SF1")[["ticker", "datekey"]].drop_duplicates()
mc = data.load("DAILY_all", usecols=["ticker", "date", "marketcap"]).pivot_table(index="date", columns="ticker", values="marketcap").sort_index()
u = pd.read_csv(os.path.join(OUT, "broad_universe_top1500.csv")); u["period"] = pd.to_datetime(u["asof"]).dt.to_period("M").astype(str)
uni_keys = set(zip(u["period"], u["ticker"]))

# ── 이벤트별 reaction/drift (event-time, no look-ahead) ──
recs = []
for tk, grp in sf1.groupby("ticker"):
    if tk not in px.columns: continue
    s = px[tk].dropna()
    if len(s) < 25: continue
    idx = s.index; vals = s.values; n = len(s)
    mcs = mc[tk].dropna() if tk in mc.columns else None
    for dk in grp["datekey"]:
        p = idx.searchsorted(dk)
        if p - 1 < 0 or p + 21 >= n: continue
        if vals[p] < 5: continue                                  # price≥$5 (발표일)
        reaction = vals[p + 1] / vals[p - 1] - 1                  # [-1,+1]
        drift = vals[p + 21] / vals[p + 2] - 1                    # [+2,+21] (진입 +2)
        m = mcs.asof(dk) if mcs is not None and len(mcs) else np.nan
        recs.append((tk, dk, reaction, drift, m))
E = pd.DataFrame(recs, columns=["ticker", "datekey", "reaction", "drift", "mc"])
E["period"] = E["datekey"].dt.to_period("M").astype(str)
E = E[[(p, t) in uni_keys for p, t in zip(E["period"], E["ticker"])]]      # top-1500 PIT
E = E.dropna(subset=["reaction", "drift"]); E = E[np.isfinite(E["drift"])]
E["pt"] = pd.PeriodIndex(E["period"], freq="M").to_timestamp()

def evalp(df, mult=1, sub=None):
    d = df if sub is None else df[sub]; rows = [];
    for per, g in d.groupby("pt"):
        g = g.dropna(subset=["reaction", "drift"])
        if len(g) < 30: continue
        ic = g["reaction"].rank().corr(g["drift"].rank())
        rk = g["reaction"].rank(pct=True); Q5 = g[rk >= 0.8]; Q1 = g[rk <= 0.2]
        bew = g["drift"].mean(); bcw = (g["mc"] * g["drift"]).sum() / g["mc"].sum() if g["mc"].sum() > 0 else bew
        c5 = C.tier_marketcap_bps(Q5.set_index("ticker")["mc"]).mean() / C.BPS
        c1 = C.tier_marketcap_bps(Q1.set_index("ticker")["mc"]).mean() / C.BPS
        rows.append(dict(per=per, ic=ic, q5=Q5["drift"].mean(), spread=Q5["drift"].mean() - Q1["drift"].mean(),
                         bew=bew, bcw=bcw, rt5=2 * c5 * mult, rt1=2 * c1 * mult, n=len(g)))
    R = pd.DataFrame(rows).set_index("per"); ic = R["ic"].dropna()
    net_lo_ew = (R["q5"] - R["bew"] - R["rt5"]); net_ls = (R["spread"] - (R["rt5"] + R["rt1"]))
    rec = R[R.index >= "2021-01-01"]; recic = rec["ic"].dropna()
    return dict(R=R, n=len(ic), ic=ic.mean(), icir=(ic.mean() / ic.std() if ic.std() > 0 else np.nan),
                net_lo_ew=net_lo_ew.mean() * 12, act_ew=(R["q5"] - R["bew"]).mean() * 12, act_cw=(R["q5"] - R["bcw"]).mean() * 12,
                net_ls=net_ls.mean() * 12, gross_ls=R["spread"].mean() * 12, ic_pos=(ic > 0).mean(),
                rec_icir=(recic.mean() / recic.std() if recic.std() > 0 else np.nan),
                rec_net=((rec["q5"] - rec["bew"] - rec["rt5"]).mean() * 12))

print("=" * 80); print("v2.0 TRUE PEAD — 사전등록 1회 kill-test (event-time, 튜닝없음)"); print("=" * 80)
print(f"이벤트={len(E)} (top-1500 PIT·price≥$5) · 발표월={E['pt'].nunique()} · 종목={E['ticker'].nunique()}")
m = evalp(E); m2 = evalp(E, mult=2)
half = E.groupby("pt")["mc"].transform("median"); lo = evalp(E, sub=(E["mc"] <= half)); hi = evalp(E, sub=(E["mc"] > half))
t = m["icir"] * np.sqrt(m["n"]); p = 0.5 * (1 - erf(t / sqrt(2)))
print(f"\n[전체] n={m['n']}월 · Rank IC={m['ic']:+.4f} · IC-IR={m['icir']:+.3f} (t≈{t:.2f},p≈{p:.4f}) · IC>0={m['ic_pos']*100:.0f}%")
print(f"  long-only Q5 vs announcer-EW: gross={m['act_ew']*100:+.2f}% net(1x)={m['net_lo_ew']*100:+.2f}% net(2x)={m2['net_lo_ew']*100:+.2f}%/yr")
print(f"  long-only Q5 vs cap-weight: gross={m['act_cw']*100:+.2f}%/yr")
print(f"  Q5-Q1: gross={m['gross_ls']*100:+.2f}% net(1x)={m['net_ls']*100:+.2f}%/yr")
print(f"  subperiod: 2021-26 IC-IR={m['rec_icir']:+.3f} · recent net(lo)={m['rec_net']*100:+.2f}%/yr")
print(f"  유동성(marketcap) 버킷 net Q5-Q1: 저={lo['net_ls']*100:+.2f}% 고={hi['net_ls']*100:+.2f}%/yr")

kills = []
if m["net_lo_ew"] <= 0: kills.append("net active(long-only vs 벤치)≤0")
if m["rec_net"] <= 0 or not (m["rec_icir"] >= 0.10): kills.append(f"2021-26 사망(net{m['rec_net']*100:+.1f}%,IC-IR{m['rec_icir']:+.3f})")
if not (m["icir"] >= 0.20): kills.append(f"IC-IR<0.20({m['icir']:+.3f})")
if m2["net_lo_ew"] <= 0: kills.append("2x cost(round-trip) 사망")
if (lo["net_ls"] > 0) and (hi["net_ls"] <= 0): kills.append("유동성 하위에만 존재")
if m["net_lo_ew"] <= 0 and m["net_ls"] > 0: kills.append("short leg 필요(long-only 안됨)")
verdict = "통과(v3 quarantine 후보)" if not kills else "FAIL → True PEAD(이 정의) 종료/보류"
print("\n" + "=" * 80); print(f"판정: {verdict}")
if kills: print(f"  KILLS: {kills}")
print("  → no tuning to rescue · no live/paper. 사전등록 kill 변경없이 적용.")
pd.DataFrame([{"edge": "true_pead_v1", "events": len(E), "ic": round(m["ic"], 4), "icir": round(m["icir"], 3),
               "net_lo_ew_%": round(m["net_lo_ew"] * 100, 2), "net2_lo_ew_%": round(m2["net_lo_ew"] * 100, 2),
               "net_ls_%": round(m["net_ls"] * 100, 2), "rec_icir": round(m["rec_icir"], 3),
               "liq_lo_%": round(lo["net_ls"] * 100, 2), "liq_hi_%": round(hi["net_ls"] * 100, 2),
               "verdict": verdict, "kills": ";".join(kills)}]).to_csv(os.path.join(OUT, "pead_true_result.csv"), index=False)
print("  → outputs/pead_true_result.csv")

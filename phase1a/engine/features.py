#!/usr/bin/env python3
"""Phase 2 M3 — Research Engine feature module. 동결 6 feature 정의 *만*.
규율: 새 feature 0 · 정의/튜닝 변경 0 · universe/cost/portfolio/evaluate 0 · API 0 · PIT(datekey<=asof) 유지.
정의 출처(verbatim): b2b5_broad(value/quality/momentum/lowvol) · us_event_drift/b_smallmid(event 4 YoY·z) · phase1b/b_smallmid(blend).
raw 4개=universe-독립 매트릭스(rebal×ticker). event/blend=per-rebal 멤버 z-mean(composite helper)."""
import numpy as np, pandas as pd

WINSOR = 3.0
def zscore(s):
    """동결 cross-sectional winsorized z — us_event_drift/phase1b/b_smallmid의 z()와 1:1."""
    s = s.astype(float); mu, sd = s.mean(), s.std()
    return (s * 0) if (not sd or np.isnan(sd)) else ((s - mu) / sd).clip(-WINSOR, WINSOR)

# ── raw per-name feature 매트릭스 (universe-독립) ───────────────────────────
def value(pb, rebal):
    return (1.0 / pb.reindex(rebal, method="pad")).replace([np.inf, -np.inf], np.nan)

def momentum(px, rebal):
    mpx = px.reindex(rebal, method="pad")
    return mpx.shift(1) / mpx.shift(12) - 1

def lowvol(px, rebal):
    return -px.pct_change().rolling(126).std().reindex(rebal, method="pad")

def quality(sf1, rebal, columns):
    """gp/assets PIT (datekey<=asof, groupby last). sf1 컬럼: ticker,datekey,gp,assets."""
    s = sf1[sf1["assets"] > 0].copy()
    s["q"] = s["gp"] / s["assets"]
    s = s.dropna(subset=["q"]).sort_values("datekey")
    qual = pd.DataFrame(index=rebal, columns=columns, dtype=float)
    for t in rebal:
        av = s[s["datekey"] <= t]
        if len(av):
            last = av.groupby("ticker")["q"].last()
            qual.loc[t, last.index.intersection(qual.columns)] = last.reindex(qual.columns.intersection(last.index))
    return qual

# ── event sub-signals (YoY shift4, PIT ffill) ──────────────────────────────
EVENT_COLS = ["e_gpa", "e_rev", "e_eps", "e_gm"]
def event_subsignals(sf1_ext, rebal):
    """sf1_ext 컬럼: ticker,datekey,gp,assets,revenue,epsusd,grossmargin → 4 YoY 매트릭스."""
    e = sf1_ext[sf1_ext["assets"] > 0].sort_values(["ticker", "datekey"]).copy()
    e["gpa"] = e["gp"] / e["assets"]
    g = e.groupby("ticker")
    e["e_gpa"] = e["gpa"] - g["gpa"].shift(4)
    e["e_rev"] = e["revenue"] / g["revenue"].shift(4) - 1
    e["e_eps"] = (e["epsusd"] - g["epsusd"].shift(4)) / g["epsusd"].shift(4).abs()
    e["e_gm"] = e["grossmargin"] - g["grossmargin"].shift(4)
    e = e.replace([np.inf, -np.inf], np.nan)
    def amat(col):
        return e.pivot_table(index="datekey", columns="ticker", values=col).sort_index().ffill().reindex(rebal, method="pad")
    return {c: amat(c) for c in EVENT_COLS}

# ── composites (per-rebal, 멤버 집합 위 z-mean) ────────────────────────────
def composite(member_df, cols):
    """한 rebal의 (members × cols) → z(winsor) 각 후 mean. event/blend 공통(원본과 1:1)."""
    return pd.concat([zscore(member_df[c]) for c in cols], axis=1).mean(axis=1)

# ── frozen definitions table ───────────────────────────────────────────────
REGISTRY = {
    "value":    {"kind": "raw",       "fn": "value",    "def": "1/pb (DAILY.pb, reindex pad)"},
    "quality":  {"kind": "raw",       "fn": "quality",  "def": "gp/assets (SF1 ARQ, datekey<=asof, last) — PIT"},
    "momentum": {"kind": "raw",       "fn": "momentum", "def": "mpx.shift(1)/mpx.shift(12)-1 (12-1)"},
    "lowvol":   {"kind": "raw",       "fn": "lowvol",   "def": "-rolling(126) std of daily ret (reindex pad)"},
    "event":    {"kind": "composite", "cols": EVENT_COLS, "def": "z-mean of gp/assets·revenue·eps·grossmargin YoY(shift4, ffill PIT)"},
    "blend":    {"kind": "composite", "cols": ["value", "quality", "momentum", "lowvol"], "def": "z-mean of 4 raw factors"},
}

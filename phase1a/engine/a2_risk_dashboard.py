#!/usr/bin/env python3
"""PRAMANA A2 — Layer 2 Risk Dashboard / State Factory (SSOT v2 §02·§06·§10).

생성 상태: Leadership Risk·Market Stress·TQQQ Decay Meter·Booster Rent·Effective Beta.
규율(SSOT §02 L1): 모든 state는 next-bar용으로 shift(1) 적용해 소비(여기선 asof까지 데이터로 계산·소비측이 t→t+1).
LLM 아님 = 전부 rule/data. PIT: asof 이전 데이터만. NEG = event_store(available_at<=asof).
출력 outputs/a2_live/risk_dashboard.json. import용 compute(asof)·CLI main. PAPER·자본권한 0.
"""
import os, sys, json, datetime as dt
import numpy as np, pandas as pd, warnings; warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a2_data
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "outputs", "a2_live"); os.makedirs(OUT, exist_ok=True)
RJSON = os.path.join(OUT, "risk_dashboard.json")
EVT = os.path.join(ROOT, "outputs", "a2_events", "event_store.csv")
LEADERS = ["NVDA", "MSFT", "AAPL", "AMZN", "GOOGL", "META", "AVGO", "TSLA", "AMD", "NFLX", "COST"]
# Leadership thresholds (SSOT §10): 0~10 GREEN·11~25 YELLOW·26+ RED
LEAD_GREEN, LEAD_YELLOW = 10, 25


def _neg_set(asof, lookback=90):
    if not os.path.exists(EVT): return set()
    try:
        ev = pd.read_csv(EVT, usecols=["ticker", "label", "available_at"])
        ev = ev[ev["label"] == "NEG"]; av = pd.to_datetime(ev["available_at"], errors="coerce")
        dd = pd.Timestamp(asof); lo = dd - pd.Timedelta(days=lookback)
        return set(ev.loc[(av <= dd) & (av > lo), "ticker"].unique())
    except Exception:
        return set()


def _leaders_panel(asof):
    """leadership basket OHLCV (sp500 panel·asof까지). gap=open/prev_close 가능."""
    p = a2_data.price_panel("sp500", min_date="2015-06-01", max_date=asof)
    return p[p["ticker"].isin(LEADERS)]


def compute(asof=None, weights=None):
    bench = a2_data.benchmarks()
    if asof is None: asof = bench.index.max()
    asof = pd.Timestamp(asof)
    q = bench["QQQ"][bench.index <= asof].dropna(); t = bench["TQQQ"][bench.index <= asof].dropna()
    spy = bench["SPY"][bench.index <= asof].dropna()
    neg = _neg_set(asof)
    # ── Leadership Risk (per-name 1pt·SSOT §10) ──
    lp = _leaders_panel(asof); score = 0; per = {}
    qret21 = float(q.iloc[-1] / q.iloc[-22] - 1) if len(q) > 22 else 0.0
    for tk in LEADERS:
        s = lp[lp["ticker"] == tk].sort_values("date")
        if len(s) < 51: continue
        c = s["close_adj"].values; o = s["open_adj"].values; v = s["volume"].values; pts = 0
        ma20 = c[-20:].mean(); ma50 = c[-50:].mean()
        if c[-1] < ma20: pts += 1                                   # 20일선 이탈
        if c[-1] < ma50: pts += 1                                   # 50일선 이탈
        vol20 = pd.Series(c[-21:]).pct_change().std()
        if c[-1] / c[-2] - 1 < -2 * (vol20 if vol20 == vol20 else 0.02) and v[-1] > 1.5 * v[-21:-1].mean():
            pts += 1                                                # high-volume down day
        if o[-1] / c[-2] - 1 < -0.03: pts += 1                      # earnings/gap-down
        nm21 = c[-1] / c[-22] - 1 if len(c) > 22 else 0.0
        if nm21 < qret21: pts += 1                                  # QQQ 대비 상대약세
        if tk in neg: pts += 1                                      # negative filing
        score += pts; per[tk] = pts
    lead_state = "RED" if score > LEAD_YELLOW else ("YELLOW" if score > LEAD_GREEN else "GREEN")
    # ── Market Stress ──
    ma20 = q.iloc[-20:].mean(); ma50 = q.iloc[-50:].mean() if len(q) >= 50 else q.mean()
    ma200 = q.iloc[-200:].mean() if len(q) >= 200 else q.mean()
    rvol = float(q.pct_change().iloc[-20:].std() * np.sqrt(252)) if len(q) > 21 else 0.0
    dd = float(q.iloc[-1] / q.cummax().iloc[-1] - 1)
    below = (q.iloc[-1] < ma20) + (q.iloc[-1] < ma50) + (q.iloc[-1] < ma200)
    market = "RED" if (below >= 3 and rvol > 0.35) else ("YELLOW" if (below >= 1 or rvol > 0.30) else "GREEN")
    # ── TQQQ Decay Meter (SSOT §06) ──
    q20r = float(q.iloc[-1] / q.iloc[-20] - 1) if len(q) > 20 else 0.0
    rng_now = (q.iloc[-20:].max() - q.iloc[-20:].min()) / q.iloc[-20:].mean()
    rng_prev = (q.iloc[-40:-20].max() - q.iloc[-40:-20].min()) / q.iloc[-40:-20].mean() if len(q) > 40 else rng_now
    rvol_prev = float(q.pct_change().iloc[-40:-20].std() * np.sqrt(252)) if len(q) > 41 else rvol
    decay = bool(abs(q20r) < 0.03 and rvol > rvol_prev and rng_now > rng_prev)
    # ── Booster Rent (SSOT §06 §7): TQQQ 20d < 2.3×QQQ 20d · QQQ ±3% · hi vol ──
    t20r = float(t.iloc[-1] / t.iloc[-20] - 1) if len(t) > 20 else 0.0
    realized_mult = (t20r / q20r) if abs(q20r) > 1e-4 else float("nan")
    booster_rent = bool(t20r < 2.3 * q20r and abs(q20r) < 0.03 and rvol > 0.30)
    # ── Effective Beta ──
    w = weights or {"qqq": 0.35, "tqqq": 0.35}
    eff_beta = w.get("qqq", 0) * 1 + w.get("tqqq", 0) * 3
    out = {"as_of": str(asof.date()), "leadership_score": int(score), "leadership_state": lead_state,
           "leadership_per_name": per, "market_stress": market, "qqq_above_ma20": bool(q.iloc[-1] > ma20),
           "qqq_above_ma50": bool(q.iloc[-1] > ma50), "qqq_above_ma200": bool(q.iloc[-1] > ma200),
           "qqq_drawdown": round(dd, 4), "realized_vol_20d": round(rvol, 4), "qqq_20d_ret": round(q20r, 4),
           "tqqq_decay": decay, "tqqq_decay_state": ("RED" if decay else "GREEN"),
           "booster_rent": booster_rent, "tqqq_realized_multiple": round(realized_mult, 2) if realized_mult == realized_mult else None,
           "effective_beta": round(eff_beta, 2), "neg_tickers_count": len(neg),
           "neg_leaders": sorted([x for x in LEADERS if x in neg])}
    return out


def main():
    r = compute()
    json.dump(r, open(RJSON, "w"), indent=2, ensure_ascii=False)
    print(f"✅ Risk Dashboard {r['as_of']}: Leadership {r['leadership_state']}({r['leadership_score']}/77)·"
          f"Market {r['market_stress']}·Decay {'ZONE' if r['tqqq_decay'] else 'OK'}·BoosterRent {r['booster_rent']}·"
          f"effBeta {r['effective_beta']}x·QQQ>200dma {r['qqq_above_ma200']}·NEG leaders {r['neg_leaders']}")
    print(f"   → {RJSON} (next-bar: 소비측이 state_t → weight_{{t+1}})")


if __name__ == "__main__":
    main()

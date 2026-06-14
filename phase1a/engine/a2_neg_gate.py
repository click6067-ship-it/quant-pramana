#!/usr/bin/env python3
"""PRAMANA A2 — Layer 5 NEG Gate (통합·SSOT v2 §05·§07·§08·§14).

EDGAR event_store 기반 단일 NEG gate. Attack ≠ Moonshot 차등(SSOT §14 §6):
  - Attack: Hard NEG여도 완전금지 아님 → size 0.25~0.5R·overnight 금지·VWAP 이탈 즉시 청산·물타기 금지·high-risk flag.
    단 상폐/회계/반복유증류 severe면 paper-only(실전 승격 금지).
  - Moonshot: Hard NEG = **절대 금지**(SSOT §08 §5).
severe NEG 분류(item/form): 1.03 파산·4.02 회계 non-reliance·3.01 상폐통지·3.02 희석·S-3/424B 증자.
PIT: available_at <= asof. import용. PAPER·자본권한 0.
"""
import os, sys, datetime as dt
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
EVT = os.path.join(ROOT, "outputs", "a2_events", "event_store.csv")
SEVERE_ITEMS = {"1.03", "4.02", "3.01"}          # 파산·회계·상폐 = severe(실전 승격 금지)
DILUTION = {"3.02"}; DILUTION_FORMS = ("S-3", "424B")


def neg_events_asof(asof, lookback=90):
    """asof 기준 직전 lookback일 NEG 이벤트 DataFrame (PIT). 없으면 빈 df."""
    if not os.path.exists(EVT): return pd.DataFrame(columns=["ticker", "item_code", "form_type", "available_at"])
    ev = pd.read_csv(EVT)
    ev = ev[ev["label"] == "NEG"].copy()
    ev["available_at"] = pd.to_datetime(ev["available_at"], errors="coerce"); ev = ev.dropna(subset=["available_at"])
    dd = pd.Timestamp(asof); lo = dd - pd.Timedelta(days=lookback)
    return ev[(ev["available_at"] <= dd) & (ev["available_at"] > lo)]


def neg_tickers_asof(asof, lookback=90):
    return set(neg_events_asof(asof, lookback)["ticker"].unique())


def severity(ticker, neg_df):
    """ticker의 NEG severity: 'severe'(상폐/회계/파산/유증) / 'soft'(기타 NEG) / 'none'."""
    sub = neg_df[neg_df["ticker"] == ticker]
    if sub.empty: return "none"
    for _, r in sub.iterrows():
        codes = set(str(r.get("item_code", "")).replace(" ", "").split(","))
        form = str(r.get("form_type", ""))
        if codes & SEVERE_ITEMS or codes & DILUTION or form.startswith(DILUTION_FORMS):
            return "severe"
    return "soft"


def gate_attack(ticker, neg_df):
    """Attack NEG gate(차등). severe=paper-only·soft=0.25~0.5R/overnight 금지·none=normal."""
    sev = severity(ticker, neg_df)
    if sev == "severe":
        return {"allowed": True, "mode": "paper-only", "max_R": 0.0, "overnight": False,
                "high_risk": True, "note": "severe NEG(상폐/회계/유증) → paper-only·실전 승격 금지"}
    if sev == "soft":
        return {"allowed": True, "mode": "special-risk", "max_R": 0.5, "overnight": False,
                "high_risk": True, "note": "Hard NEG·0.25~0.5R·overnight 금지·VWAP 이탈 즉시 청산·물타기 금지"}
    return {"allowed": True, "mode": "normal", "max_R": 1.0, "overnight": True, "high_risk": False, "note": "NEG 없음"}


def gate_moonshot(ticker, neg_df):
    """Moonshot NEG gate: Hard NEG = 절대 금지(SSOT §08 §5)."""
    sev = severity(ticker, neg_df)
    if sev in ("severe", "soft"):
        return {"allowed": False, "reason": f"Hard NEG({sev}) → Moonshot 절대 금지(SSOT §08)"}
    return {"allowed": True, "reason": "NEG 없음"}


def main():
    asof = dt.date.today()
    nd = neg_events_asof(asof)
    tks = sorted(nd["ticker"].unique())
    sev = [t for t in tks if severity(t, nd) == "severe"]
    print(f"✅ NEG Gate {asof}: 직전 90일 NEG {len(tks)}종 (severe {len(sev)})")
    print(f"   Attack: severe={len(sev)} paper-only·soft={len(tks)-len(sev)} 0.25~0.5R / Moonshot: 전부 절대금지")
    if tks: print(f"   예: {tks[:10]} · severe: {sev[:8]}")


if __name__ == "__main__":
    main()

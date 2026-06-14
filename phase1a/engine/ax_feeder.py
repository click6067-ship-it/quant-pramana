#!/usr/bin/env python3
"""PRAMANA AX — Feeder A (catalyst 후보 생성기·매수권 0·idea only).

정본: AX0_Protocol.md §2·§7. catalyst = EDGAR 8-K item 2.02(실적)/1.01(중요계약) + 최근 momentum 확인.
출력: outputs/ax0/candidates.csv (append-only·전수·거래 안 해도 기록·R2#9 cherry-pick 방지).
graveyard_overlap 필수(R2#5): A2 Attack(spot daily-proxy DEAD)와 겹침 → revival 태그 + 새 메커니즘(옵션 convexity) 명시.
PAPER·자본권한 0·후보는 매수 아님. 사용: python engine/ax_feeder.py
"""
import os, sys, json, hashlib, datetime as dt
import numpy as np, pandas as pd, warnings; warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a2_event_store as es
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "outputs", "ax0"); os.makedirs(OUT, exist_ok=True)
CAND = os.path.join(OUT, "candidates.csv")
EVT = os.path.join(ROOT, "outputs", "a2_events", "event_store.csv")

LOOKBACK_DAYS = 7             # available_at가 최근 N일 이내인 catalyst만(forward 신선도)
POS_CATALYST = {"2.02", "1.01"}   # 실적·중요계약 (AX-0 catalyst 정의)

def _overlap(cat_type):
    """graveyard 상속(Protocol §7). catalyst-momentum 표면 = A2 Attack(spot DEAD)과 겹침 → revival."""
    return {"graveyard_overlap": "A2_Attack(spot catalyst-momentum daily-proxy=DEAD)",
            "revival_tag": "revival",
            "new_mechanism": "spot 추격 아님 → defined-risk 옵션 convexity로 표현(다른 payoff/risk·forward-paper·UNVERIFIED)"}

def recent_momentum(tickers, asof):
    """후보 ticker들의 최근 gap/21d momentum (yfinance·forward). 실패=NaN."""
    if not tickers: return {}
    try:
        import yfinance as yf
        df = yf.download(list(tickers), period="90d", interval="1d", auto_adjust=True, progress=False)
        c = df["Close"] if isinstance(df.columns, pd.MultiIndex) else df
        if isinstance(c, pd.Series): c = c.to_frame(tickers[0])
        out = {}
        for t in tickers:
            if t not in c.columns: continue
            s = c[t].dropna()
            if len(s) < 22: continue
            out[t] = {"last": round(float(s.iloc[-1]), 2),
                      "gap_1d": round(float(s.iloc[-1] / s.iloc[-2] - 1), 4) if len(s) > 1 else np.nan,
                      "mom_21d": round(float(s.iloc[-1] / s.iloc[-22] - 1), 4)}
        return out
    except Exception:
        return {}

def main():
    today = dt.date.today()
    # 1) EDGAR 최근 POS catalyst (event_store 캐시·forward면 a2_event_store --refresh로 갱신)
    if not os.path.exists(EVT):
        print("⛔ event_store 없음 — engine/a2_event_store.py 먼저"); return
    ev = pd.read_csv(EVT)
    ev = ev[ev["source"] == "edgar"].copy()
    ev["available_at"] = pd.to_datetime(ev["available_at"], errors="coerce")
    ev = ev.dropna(subset=["available_at"])
    asof = pd.Timestamp(today)   # ★ Codex#3 look-ahead 차단: available_at <= today만(미래 공시 금지)
    lo = asof - pd.Timedelta(days=LOOKBACK_DAYS)
    ev["codes"] = ev["item_code"].astype(str)
    pos = ev[(ev["label"] == "POS") & (ev["available_at"] >= lo) & (ev["available_at"] <= asof) &
             (ev["codes"].apply(lambda x: bool(set(str(x).replace(" ", "").split(",")) & POS_CATALYST)))]
    pos = pos.sort_values("available_at").drop_duplicates(["ticker"], keep="last")
    if pos.empty:
        print(f"✅ Feeder A {today}: 최근 {LOOKBACK_DAYS}일 POS catalyst 후보 0 (정상·이벤트 없음)");
        # 그래도 빈 run 기록(append-only 무결성)
        pd.DataFrame([{"run_date": str(today), "ticker": "(none)", "note": "no recent catalyst"}]).to_csv(
            CAND, mode="a", header=not os.path.exists(CAND), index=False)
        return
    mom = recent_momentum(pos["ticker"].tolist(), today)
    rows = []
    for _, r in pos.iterrows():
        t = r["ticker"]; m = mom.get(t, {})
        ov = _overlap(r["codes"])
        confirmed = bool(m.get("mom_21d", -1) is not None and m.get("mom_21d", -1) >= 0)   # momentum 확인(하락추세 제외)
        rows.append({"run_date": str(today), "ticker": t, "catalyst": r["codes"], "event_type": r["event_type"],
                     "available_at": str(r["available_at"].date()), "last": m.get("last", np.nan),
                     "gap_1d": m.get("gap_1d", np.nan), "mom_21d": m.get("mom_21d", np.nan),
                     "momentum_ok": confirmed, **ov, "decision": "IDEA_ONLY(매수권 0)",
                     "candidate_id": hashlib.sha256(f"{t}|{r['available_at'].date()}".encode()).hexdigest()[:12]})
    df = pd.DataFrame(rows)
    df.to_csv(CAND, mode="a", header=not os.path.exists(CAND), index=False)
    n_ok = int(df["momentum_ok"].sum())
    print(f"✅ Feeder A {today}: catalyst 후보 {len(df)}건(POS 2.02/1.01·최근 {LOOKBACK_DAYS}일)·momentum 확인 {n_ok} → {CAND}")
    print(f"   전수 append-only(cherry-pick 방지)·전부 graveyard_overlap=A2_Attack revival·새 메커니즘=옵션 convexity·매수권 0")
    print(f"   상위: {', '.join(df.head(6)['ticker'].tolist())}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""PRAMANA A2 — Feature Store (blind/PIT backtest용 일별 feature·available_at 강제).

설계 정본: pramana_a2_delta_patch_pack/02_ATTACK_MOONSHOT_BLIND_BACKTEST.md §6.1.
핵심 규율: 모든 feature는 available_at(그 시점에 실제로 알 수 있었던 시각)을 갖는다.
  - 가격/거래량 feature: 그날(t) 장마감 후 known → available_at = date(t). 진입은 t+1(blind backtest가 next-bar 강제).
  - 펀더멘털(gp/assets): available_at = datekey(공시 가용일). datekey<=date인 최신만(merge_asof backward).
사용:
  build_feature_panel(universe) → WIDE DataFrame (ticker,date,feature...,available_at) = blind backtest in-memory 입력.
  main() → long-format audit artifact outputs/a2_features/feature_store.csv (candidate-day subset·size 관리).
PAPER·자본권한 0. 분봉(ORB/VWAP/RVOL) feature는 여기 없음 — 일별 PIT만(Sharadar=daily backbone·02 §2).
"""
import os, sys, datetime as dt
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a2_data

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "outputs", "a2_features"); os.makedirs(OUTDIR, exist_ok=True)
STORE = os.path.join(OUTDIR, "feature_store.csv")

# 일별 feature 정의 (전부 close-of-day t known → available_at=t)
PRICE_FEATURES = ["ret_1d", "ret_21d", "ret_63d", "gap_pct", "rvol20", "dollar_vol", "hi252_prox"]


def build_feature_panel(universe="smallmid", min_date="2016-01-01", max_date=None,
                        min_dollar_vol=3_000_000):
    """universe 가격패널 → 일별 PIT feature WIDE DataFrame.
    반환 컬럼: ticker, date, close_adj, [open_adj..], volume, ret_1d, ret_21d, ret_63d, gap_pct,
              rvol20, dollar_vol, hi252_prox, quality_gpoa, quality_avail, available_at, source, quality_label.
    available_at = date (close-of-day known) — blind backtest가 available_at<=decision_time & next-bar 진입 강제.
    min_dollar_vol = 유동성 floor (penny/illiquid 제거; 0이면 미적용)."""
    px = a2_data.price_panel(universe, min_date=min_date, max_date=max_date)
    has_ohlc = "open_adj" in px.columns
    g = px.groupby("ticker", sort=False)
    c = px["close_adj"]; v = px["volume"].fillna(0)
    px["ret_1d"]  = g["close_adj"].pct_change(1)
    px["ret_21d"] = g["close_adj"].pct_change(21)
    px["ret_63d"] = g["close_adj"].pct_change(63)
    prev_c = g["close_adj"].shift(1)
    if has_ohlc:
        px["gap_pct"] = px["open_adj"] / prev_c - 1.0          # 진짜 gap (장초 open vs 전일 close)
        px["_gap_kind"] = "open_gap"
    else:
        px["gap_pct"] = c / prev_c - 1.0                        # close-to-close gap (PROXY·OHLC 없음)
        px["_gap_kind"] = "close_gap_proxy"
    # rvol: 당일 거래량 vs 직전 20일 평균(당일 제외) — 당일 volume은 장마감 후 known
    avg20 = g["volume"].transform(lambda s: s.shift(1).rolling(20, min_periods=10).mean())
    px["rvol20"] = (v / avg20).replace([np.inf, -np.inf], np.nan)
    px["dollar_vol"] = c * v
    hi252 = g["close_adj"].transform(lambda s: s.rolling(252, min_periods=60).max())
    px["hi252_prox"] = c / hi252                                # 1.0 근처 = 52주 신고가권
    # 펀더멘털 quality (PIT): gp/assets, available_at=datekey
    funds = a2_data.fundamentals().copy()
    funds["quality_gpoa"] = funds["gp"] / funds["assets"]
    funds = funds.dropna(subset=["quality_gpoa"])[["ticker", "datekey", "quality_gpoa"]].sort_values("datekey")
    px = px.sort_values("date")
    px = pd.merge_asof(px, funds.rename(columns={"datekey": "quality_avail"}),
                       left_on="date", right_on="quality_avail", by="ticker", direction="backward")
    px = px.sort_values(["ticker", "date"]).reset_index(drop=True)
    px["available_at"] = px["date"]                            # close-of-day t known
    px["source"] = "sharadar_sep_" + universe
    px["quality_label"] = "DAILY_PIT"
    if min_dollar_vol:
        px = px[px["dollar_vol"] >= min_dollar_vol]
    return px


def to_long(panel):
    """WIDE → long audit schema (02 §6.1): ticker,feature_name,feature_value,asof_time,available_at,source,quality_label."""
    rows = []
    for f in PRICE_FEATURES + ["quality_gpoa"]:
        if f not in panel.columns: continue
        sub = panel[["ticker", "date", f, "available_at", "source", "quality_label"]].dropna(subset=[f])
        sub = sub.rename(columns={f: "feature_value", "date": "asof_time"})
        sub["feature_name"] = f
        rows.append(sub[["ticker", "feature_name", "feature_value", "asof_time", "available_at", "source", "quality_label"]])
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def main():
    """audit artifact = STRONG-candidate subset만 WIDE 저장(전체 universe long = 수천만행/수백MB이라 size 관리·
    실제 backtest 입력은 build_feature_panel()의 in-memory panel을 결정적 재계산)."""
    uni = sys.argv[sys.argv.index("--universe") + 1] if "--universe" in sys.argv else "smallmid"
    panel = build_feature_panel(uni)
    # strong-trigger only (gap+volume 동반 = 진짜 attack day / 강모멘텀 / 신고가권) → 컴팩트 audit
    strong = (((panel["gap_pct"] >= 0.05) & (panel["rvol20"] >= 2.0)) |
              (panel["ret_21d"] >= 0.30) | ((panel["hi252_prox"] >= 0.99) & (panel["rvol20"] >= 2.0)))
    cand = panel[strong].copy()
    keep = ["ticker", "date", "close_adj", "volume", "ret_21d", "ret_63d", "gap_pct", "rvol20",
            "dollar_vol", "hi252_prox", "quality_gpoa", "quality_avail", "available_at", "source", "quality_label"]
    cand[[c for c in keep if c in cand.columns]].to_csv(STORE, index=False)
    cov = panel.dropna(subset=["quality_gpoa"])["ticker"].nunique()
    print(f"✅ feature_store {uni}: panel {len(panel):,}행/{panel['ticker'].nunique()}종 · "
          f"strong-candidate audit {len(cand):,}행 → {STORE}")
    print(f"   gap_kind={panel['_gap_kind'].iloc[0]} · quality PIT coverage {cov}종 · "
          f"date {panel['date'].min().date()}~{panel['date'].max().date()} · available_at=close-of-day(next-bar는 backtest)")
    print(f"   feature 분포: gap≥4% {(panel['gap_pct']>=0.04).sum():,} · rvol≥2 {(panel['rvol20']>=2).sum():,} · "
          f"mom21≥20% {(panel['ret_21d']>=0.20).sum():,} · 신고가권 {(panel['hi252_prox']>=0.98).sum():,}")


if __name__ == "__main__":
    main()

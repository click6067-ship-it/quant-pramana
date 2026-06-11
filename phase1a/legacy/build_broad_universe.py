#!/usr/bin/env python3
"""월별 top-1500 PIT 유니버스 생성 + diagnostics (B2~B5 전 검문소).
DAILY_all(marketcap)으로 각 월말 거래일 as-of 랭킹 → top-1500. survivorship/no-future 점검."""
import os, pandas as pd, numpy as np, nasdaqdatalink as ndl
HERE = os.path.dirname(os.path.abspath(__file__)); RAW = os.path.join(HERE, "outputs", "raw")
ndl.ApiConfig.api_key = open(os.path.join(HERE, ".ndl_key")).read().strip()
TOPN = 1500

dl = pd.read_csv(os.path.join(RAW, "DAILY_all.csv"), usecols=["ticker","date","marketcap"], parse_dates=["date"])
dl = dl[dl["marketcap"] > 0]
dl["ym"] = dl["date"].dt.to_period("M")
month_end = dl.groupby("ym")["date"].max()                       # 각 달 실제 마지막 데이터일

tk = ndl.get_table("SHARADAR/TICKERS", table="SEP", paginate=True).drop_duplicates("ticker").set_index("ticker")
isdel = (tk["isdelisted"].astype(str).str.upper() == "Y")
iscommon = (tk["category"] == "Domestic Common Stock")

rows, diag = [], []
for ym, med in month_end.items():
    day = dl[dl["date"] == med].sort_values("marketcap", ascending=False)
    top = day.head(TOPN).copy()
    rows.append(top.assign(asof=med)[["asof","ticker","marketcap"]])
    tks = top["ticker"]
    diag.append((med, len(day), len(top),
                 int(isdel.reindex(tks).fillna(False).sum()),          # 이 달 top에 '결국 폐지될' 종목 수
                 int((~iscommon.reindex(tks).fillna(True)).sum()),     # common 아닌 오염 수
                 float(top["marketcap"].min()), float(top["marketcap"].max())))
univ = pd.concat(rows, ignore_index=True)
univ.to_csv(os.path.join(HERE, "outputs", "broad_universe_top1500.csv"), index=False)
d = pd.DataFrame(diag, columns=["asof","candidates","selected","delisted_in_top","noncommon","mcap_min_$M","mcap_max_$M"])

print("="*72); print("Broad Universe (top-1500 by marketcap, PIT) — DIAGNOSTICS"); print("="*72)
print(f"기간: {d["asof"].min().date()} ~ {d["asof"].max().date()} · 월 수: {len(d)}")
print(f"월별 selected: min={d.selected.min()} median={int(d.selected.median())} max={d.selected.max()}  (목표 1500)")
print(f"월별 candidates(marketcap 보유): min={d.candidates.min()} median={int(d.candidates.median())}")
print(f"union unique tickers(전 기간): {univ.ticker.nunique()}  ← SEP/SF1 pull 대상 규모")
print(f"delisted_in_top(결국 폐지될 종목이 과거 top에 포함): min={d.delisted_in_top.min()} median={int(d.delisted_in_top.median())} max={d.delisted_in_top.max()}  (>0이어야 survivorship-safe)")
print(f"noncommon 오염: max={d.noncommon.max()}  (0이어야 함)")
print(f"marketcap 컷(top1500 최소, $M): median={d['mcap_min_$M'].median():.0f}  (페니/마이크로 배제 확인)")
print("\n[연도별 selected/ delisted_in_top/ mcap_min]")
yr = d.set_index("asof").resample("YE").agg({"selected":"median","delisted_in_top":"median","mcap_min_$M":"median","candidates":"median"})
print(yr.round(0).to_string())
# 진단 판정
ok_size = (d.selected >= 1400).mean() > 0.9
ok_surv = (d.delisted_in_top > 0).mean() > 0.5
ok_clean = (d.noncommon.max() == 0)
print(f"\n진단: size≈1500 {'PASS' if ok_size else 'WARN'} · survivorship {'PASS' if ok_surv else 'WARN'} · common-only {'PASS' if ok_clean else 'FAIL'}")
print(f"→ outputs/broad_universe_top1500.csv ({len(univ)} rows)")

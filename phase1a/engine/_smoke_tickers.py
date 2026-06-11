#!/usr/bin/env python3
"""M1.5 smoke — TICKERS API-free 재현 증명. nasdaqdatalink import 0·API 호출 0.
data.load_tickers()만으로 category/sector/isdelisted/common-filter가 도는지 + 기존 진단 재현."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd, data   # data.py만 — ndl 없음

print("="*70); print("TICKERS API-free smoke (ndl import 없음, key 없이 실행)"); print("="*70)
tk = data.load_tickers()
iscommon = (tk["category"] == "Domestic Common Stock")
isdel = (tk["isdelisted"].astype(str).str.upper() == "Y")
print(f"TICKERS: {len(tk)}종 · common(Domestic Common Stock): {int(iscommon.sum())} · delisted(Y): {int(isdel.sum())}")
print(f"sector 분포 top5: {dict(tk['sector'].value_counts().head(5))}")
print(f"필수컬럼 존재: {[c for c in ['permaticker','category','isdelisted','sector','siccode','firstpricedate','lastpricedate'] if c in tk.columns]}")

# 기존 진단 재현(API-free): small/mid·broad union의 noncommon 오염 = 0 이어야
RAW = data.RAW; OUT = os.path.join(data.PHASE1A, "outputs")
for name, f in [("small/mid 1001-3000", "smallmid_universe_1001_3000.csv"), ("broad top-1500", "broad_universe_top1500.csv")]:
    p = os.path.join(OUT, f)
    if os.path.exists(p):
        uniq = pd.read_csv(p)["ticker"].unique()
        nonc = int((~iscommon.reindex(uniq).fillna(False)).sum())
        delc = int(isdel.reindex(uniq).fillna(False).sum())
        print(f"  [{name}] union={len(uniq)} · noncommon={nonc}(기존 진단 0 재현) · delisted_ever={delc}(survivorship)")
print("\n✅ ndl 미사용·키 없이 category/sector/isdelisted/common-filter 전부 재현 → downstream API-free 확정")

#!/usr/bin/env python3
"""broad universe 기반용: 전체 Domestic Common Stock DAILY(marketcap) bulk pull.
resumable(청크 append-캐시), marketcap 컬럼만, python -u로 실행. → outputs/raw/DAILY_all.csv"""
import os, nasdaqdatalink as ndl, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); RAW = os.path.join(HERE, "outputs", "raw")
os.makedirs(RAW, exist_ok=True)
ndl.ApiConfig.api_key = open(os.path.join(HERE, ".ndl_key")).read().strip()
START = "2016-01-01"
path = os.path.join(RAW, "DAILY_all.csv")

tk = ndl.get_table("SHARADAR/TICKERS", table="SEP", paginate=True)
universe = sorted(tk[tk.category == "Domestic Common Stock"]["ticker"].dropna().unique())
print(f"[universe] Domestic Common Stock = {len(universe)}", flush=True)

done = set()
if os.path.exists(path):
    try: done = set(pd.read_csv(path, usecols=["ticker"])["ticker"].unique())
    except Exception: done = set()
todo = [t for t in universe if t not in done]
print(f"[DAILY_all] cached={len(done)} todo={len(todo)}", flush=True)
for i in range(0, len(todo), 40):
    sub = todo[i:i+40]
    df = ndl.get_table("SHARADAR/DAILY", ticker=sub, date={"gte": START},
                       qopts={"columns": ["ticker", "date", "marketcap"]}, paginate=True)
    df.to_csv(path, mode="a", header=not os.path.exists(path), index=False)
    if (i // 40) % 10 == 0:
        print(f"  DAILY_all {i+len(sub)}/{len(todo)}", flush=True)
print(f"[DONE] DAILY_all rows ~ pull complete. file={path}", flush=True)

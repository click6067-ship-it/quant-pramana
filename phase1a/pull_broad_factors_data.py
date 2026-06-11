#!/usr/bin/env python3
"""broad top-1500 union(2973종) factor 데이터 pull (resumable·cached).
SEP.closeadj(mom/lowvol) · DAILY.pb(value, S&P500 run과 동일정의) · SF1 gp/assets(quality).
marketcap은 DAILY_all.csv 재사용. → outputs/raw/broad_*.csv"""
import os, pandas as pd, nasdaqdatalink as ndl
HERE = os.path.dirname(os.path.abspath(__file__)); RAW = os.path.join(HERE, "outputs", "raw")
ndl.ApiConfig.api_key = open(os.path.join(HERE, ".ndl_key")).read().strip()
START = "2016-01-01"
univ = sorted(pd.read_csv(os.path.join(HERE, "outputs", "broad_universe_top1500.csv"))["ticker"].unique())
print(f"[union] {len(univ)} tickers", flush=True)

def pull(table, path, cols, dimension=None, chunk=40, datecol="date"):
    done = set()
    if os.path.exists(path):
        try: done = set(pd.read_csv(path, usecols=["ticker"])["ticker"].unique())
        except Exception: done = set()
    todo = [t for t in univ if t not in done]
    print(f"[{os.path.basename(path)}] cached={len(done)} todo={len(todo)}", flush=True)
    for i in range(0, len(todo), chunk):
        sub = todo[i:i+chunk]
        kw = dict(ticker=sub, qopts={"columns": cols}, paginate=True)
        if dimension: kw["dimension"] = dimension
        else: kw["date"] = {"gte": START}
        df = ndl.get_table(table, **kw)
        df.to_csv(path, mode="a", header=not os.path.exists(path), index=False)
        if (i//chunk) % 10 == 0: print(f"  {os.path.basename(path)} {i+len(sub)}/{len(todo)}", flush=True)
    print(f"[done] {os.path.basename(path)}", flush=True)

pull("SHARADAR/SEP",   os.path.join(RAW, "broad_SEP.csv"),    ["ticker","date","closeadj","closeunadj"])
pull("SHARADAR/DAILY", os.path.join(RAW, "broad_DAILY_pb.csv"), ["ticker","date","pb"])
pull("SHARADAR/SF1",   os.path.join(RAW, "broad_SF1.csv"),    ["ticker","datekey","gp","assets"], dimension="ARQ")
print("[ALL DONE] broad factor data pulled.", flush=True)

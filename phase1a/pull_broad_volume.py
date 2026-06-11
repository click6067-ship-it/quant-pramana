#!/usr/bin/env python3
"""broad top-1500 union volume pull (capacity/impact용). closeunadj는 broad_SEP에 이미 있음 → dollar_vol=closeunadj*volume.
resumable·chunked. → outputs/raw/broad_volume.csv"""
import os, pandas as pd, nasdaqdatalink as ndl
HERE=os.path.dirname(os.path.abspath(__file__)); RAW=os.path.join(HERE,"outputs","raw")
ndl.ApiConfig.api_key=open(os.path.join(HERE,".ndl_key")).read().strip()
path=os.path.join(RAW,"broad_volume.csv")
univ=sorted(pd.read_csv(os.path.join(HERE,"outputs","broad_universe_top1500.csv"))["ticker"].unique())
done=set()
if os.path.exists(path):
    try: done=set(pd.read_csv(path,usecols=["ticker"])["ticker"].unique())
    except Exception: done=set()
todo=[t for t in univ if t not in done]
print(f"[broad_volume] union={len(univ)} cached={len(done)} todo={len(todo)}",flush=True)
for i in range(0,len(todo),40):
    sub=todo[i:i+40]
    df=ndl.get_table("SHARADAR/SEP",ticker=sub,date={"gte":"2016-01-01"},qopts={"columns":["ticker","date","volume"]},paginate=True)
    df.to_csv(path,mode="a",header=not os.path.exists(path),index=False)
    if (i//40)%10==0: print(f"  broad_volume {i+len(sub)}/{len(todo)}",flush=True)
print("[DONE] broad_volume",flush=True)

#!/usr/bin/env python3
"""US event/earnings drift 실험용 SF1 확장 pull (resumable·chunked).
컬럼: datekey(PIT 공시일)·revenue·epsusd·grossmargin·roe·gp·assets. dimension=ARQ. → outputs/raw/broad_SF1_ext.csv"""
import os, pandas as pd, nasdaqdatalink as ndl
HERE=os.path.dirname(os.path.abspath(__file__)); RAW=os.path.join(HERE,"outputs","raw")
ndl.ApiConfig.api_key=open(os.path.join(HERE,".ndl_key")).read().strip()
path=os.path.join(RAW,"broad_SF1_ext.csv")
COLS=["ticker","datekey","revenue","epsusd","grossmargin","roe","gp","assets"]
univ=sorted(pd.read_csv(os.path.join(HERE,"outputs","broad_universe_top1500.csv"))["ticker"].unique())
done=set()
if os.path.exists(path):
    try: done=set(pd.read_csv(path,usecols=["ticker"])["ticker"].unique())
    except Exception: done=set()
todo=[t for t in univ if t not in done]
print(f"[SF1_ext] union={len(univ)} cached={len(done)} todo={len(todo)}",flush=True)
for i in range(0,len(todo),40):
    sub=todo[i:i+40]
    df=ndl.get_table("SHARADAR/SF1",ticker=sub,dimension="ARQ",qopts={"columns":COLS},paginate=True)
    df.to_csv(path,mode="a",header=not os.path.exists(path),index=False)
    if (i//40)%10==0: print(f"  SF1_ext {i+len(sub)}/{len(todo)}",flush=True)
print(f"[DONE] broad_SF1_ext.csv rows pull complete.",flush=True)

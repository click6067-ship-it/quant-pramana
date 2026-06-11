#!/usr/bin/env python3
"""small/mid(rank1001-3000) union 4504종 데이터 pull (resumable·chunked). marketcap은 DAILY_all 재사용.
SEP: closeadj(수익)·closeunadj($5필터)·volume(ADV/비용) / DAILY: pb(value) / SF1: gp·assets·revenue·epsusd·grossmargin(quality/event). → outputs/raw/smallmid_*.csv"""
import os, pandas as pd, nasdaqdatalink as ndl
HERE=os.path.dirname(os.path.abspath(__file__)); RAW=os.path.join(HERE,"outputs","raw")
ndl.ApiConfig.api_key=open(os.path.join(HERE,".ndl_key")).read().strip()
START="2016-01-01"
univ=sorted(pd.read_csv(os.path.join(HERE,"outputs","smallmid_universe_1001_3000.csv"))["ticker"].unique())
print(f"[union] {len(univ)} tickers",flush=True)

def pull(table,path,cols,dimension=None,chunk=40):
    done=set()
    if os.path.exists(path):
        try: done=set(pd.read_csv(path,usecols=["ticker"])["ticker"].unique())
        except Exception: done=set()
    todo=[t for t in univ if t not in done]
    print(f"[{os.path.basename(path)}] cached={len(done)} todo={len(todo)}",flush=True)
    for i in range(0,len(todo),chunk):
        sub=todo[i:i+chunk]
        kw=dict(ticker=sub,qopts={"columns":cols},paginate=True)
        if dimension: kw["dimension"]=dimension
        else: kw["date"]={"gte":START}
        df=ndl.get_table(table,**kw)
        df.to_csv(path,mode="a",header=not os.path.exists(path),index=False)
        if (i//chunk)%10==0: print(f"  {os.path.basename(path)} {i+len(sub)}/{len(todo)}",flush=True)
    print(f"[done] {os.path.basename(path)}",flush=True)

pull("SHARADAR/SEP",  os.path.join(RAW,"smallmid_SEP.csv"),  ["ticker","date","closeadj","closeunadj","volume"])
pull("SHARADAR/DAILY",os.path.join(RAW,"smallmid_DAILY.csv"),["ticker","date","pb"])
pull("SHARADAR/SF1",  os.path.join(RAW,"smallmid_SF1.csv"),  ["ticker","datekey","gp","assets","revenue","epsusd","grossmargin"],dimension="ARQ")
print("[ALL DONE] smallmid data pulled.",flush=True)

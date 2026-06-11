#!/usr/bin/env python3
"""US small/mid PIT universe = marketcap rank 1001~3000 (top-1000 제외, 다음 2000). diagnostics 먼저.
price/$5·ADV 필터는 SEP+volume pull 후 적용(여기선 marketcap-rank 후보 + survivorship 점검). → outputs/smallmid_universe_1001_3000.csv"""
import os, pandas as pd, numpy as np, nasdaqdatalink as ndl
HERE=os.path.dirname(os.path.abspath(__file__)); RAW=os.path.join(HERE,"outputs","raw")
ndl.ApiConfig.api_key=open(os.path.join(HERE,".ndl_key")).read().strip()
LO,HI=1001,3000

dl=pd.read_csv(os.path.join(RAW,"DAILY_all.csv"),usecols=["ticker","date","marketcap"],parse_dates=["date"])
dl=dl[dl["marketcap"]>0]; dl["ym"]=dl["date"].dt.to_period("M")
month_end=dl.groupby("ym")["date"].max()
tk=ndl.get_table("SHARADAR/TICKERS",table="SEP",paginate=True).drop_duplicates("ticker").set_index("ticker")
isdel=(tk["isdelisted"].astype(str).str.upper()=="Y"); iscommon=(tk["category"]=="Domestic Common Stock")

rows,diag=[],[]
for ym,med in month_end.items():
    day=dl[dl["date"]==med].sort_values("marketcap",ascending=False).reset_index(drop=True)
    day["rank"]=day.index+1
    sm=day[(day["rank"]>=LO)&(day["rank"]<=HI)].copy()
    rows.append(sm.assign(asof=med)[["asof","ticker","marketcap","rank"]])
    tks=sm["ticker"]
    diag.append((med,len(day),len(sm),
                 int(isdel.reindex(tks).fillna(False).sum()),
                 int((~iscommon.reindex(tks).fillna(True)).sum()),
                 float(sm["marketcap"].min()),float(sm["marketcap"].max())))
univ=pd.concat(rows,ignore_index=True)
univ.to_csv(os.path.join(HERE,"outputs","smallmid_universe_1001_3000.csv"),index=False)
d=pd.DataFrame(diag,columns=["asof","total_candidates","selected","delisted_in_sel","noncommon","mcap_min_$M","mcap_max_$M"])

print("="*74); print(f"US Small/Mid Universe (marketcap rank {LO}~{HI}, PIT) — DIAGNOSTICS"); print("="*74)
print(f"기간 {d['asof'].min().date()}~{d['asof'].max().date()} · 월수 {len(d)}")
print(f"월별 selected: min={d.selected.min()} median={int(d.selected.median())} max={d.selected.max()} (목표 {HI-LO+1})")
print(f"union unique tickers(전기간): {univ.ticker.nunique()}  ← SEP/DAILY/SF1 pull 대상")
print(f"delisted_in_sel(폐지될 종목이 과거 선택에 포함): median={int(d.delisted_in_sel.median())} max={d.delisted_in_sel.max()} (>0=survivorship-safe)")
print(f"noncommon 오염: max={d.noncommon.max()} (0이어야)")
print(f"marketcap 범위($M): 하단 median={d['mcap_min_$M'].median():.0f} / 상단 median={d['mcap_max_$M'].median():.0f}")
print("\n[연도별 selected / delisted_in_sel / mcap_min / mcap_max]")
yr=d.set_index("asof").resample("YE").agg({"selected":"median","delisted_in_sel":"median","mcap_min_$M":"median","mcap_max_$M":"median"})
print(yr.round(0).to_string())
ok_size=(d.selected>=1800).mean()>0.8; ok_surv=(d.delisted_in_sel>0).mean()>0.5; ok_clean=(d.noncommon.max()==0)
print(f"\n진단: size≈{HI-LO+1} {'PASS' if ok_size else 'WARN'} · survivorship {'PASS' if ok_surv else 'WARN'} · common-only {'PASS' if ok_clean else 'FAIL'}")
print(f"→ outputs/smallmid_universe_1001_3000.csv ({len(univ)} rows) · 다음=SEP(+volume)/DAILY/SF1 pull → price≥$5·ADV 필터 → b_smallmid")

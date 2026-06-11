#!/usr/bin/env python3
"""B2~B5 broad cost-aware retest — top-1500 PIT universe. 팩터 정의 S&P500과 동일(튜닝 금지).
지표: Rank IC·IC-IR + gross/net Q5-Q1 + turnover + size-bucket IC. 사전등록 kill 조건 대조.
데이터: outputs/raw/broad_SEP·broad_DAILY_pb·broad_SF1 + DAILY_all(marketcap) + broad_universe_top1500."""
import os, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); RAW = os.path.join(HERE, "outputs", "raw"); OUT = os.path.join(HERE, "outputs")

u = pd.read_csv(os.path.join(OUT, "broad_universe_top1500.csv")); u["asof"] = pd.to_datetime(u["asof"])
members = {d: set(g) for d, g in u.groupby("asof")["ticker"]}
rebal = sorted(members.keys())

px  = pd.read_csv(os.path.join(RAW,"broad_SEP.csv"), usecols=["ticker","date","closeadj"], parse_dates=["date"]).pivot_table(index="date",columns="ticker",values="closeadj").sort_index()
pb  = pd.read_csv(os.path.join(RAW,"broad_DAILY_pb.csv"), usecols=["ticker","date","pb"], parse_dates=["date"]).pivot_table(index="date",columns="ticker",values="pb").sort_index()
mc  = pd.read_csv(os.path.join(RAW,"DAILY_all.csv"), usecols=["ticker","date","marketcap"], parse_dates=["date"]).pivot_table(index="date",columns="ticker",values="marketcap").sort_index()
sf1 = pd.read_csv(os.path.join(RAW,"broad_SF1.csv"), parse_dates=["datekey"]); sf1=sf1[sf1["assets"]>0]; sf1["q"]=sf1["gp"]/sf1["assets"]; sf1=sf1.dropna(subset=["q"]).sort_values("datekey")

def at(df, t):   # t행(없으면 직전 거래일)
    if t in df.index: return df.loc[t]
    sub = df.loc[:t]; return sub.iloc[-1] if len(sub) else pd.Series(dtype=float)

# 월그리드 factor
mpx = px.reindex(rebal, method="pad")
fwd = mpx.shift(-1)/mpx - 1
val = (1.0/pb.reindex(rebal, method="pad")).replace([np.inf,-np.inf],np.nan)
mom = mpx.shift(1)/mpx.shift(12) - 1
vol = px.pct_change().rolling(126).std().reindex(rebal, method="pad"); lowvol = -vol
qual = pd.DataFrame(index=rebal, columns=px.columns, dtype=float)
for t in rebal:
    av = sf1[sf1["datekey"]<=t]
    if len(av):
        last = av.groupby("ticker")["q"].last()
        qual.loc[t, last.index.intersection(qual.columns)] = last.reindex(qual.columns.intersection(last.index))
mcg = mc.reindex(rebal, method="pad")
factors = {"B2_value":val, "B3_quality":qual, "B4_momentum":mom, "B5_lowvol":lowvol}

def cost_bps(tkrs, t):   # 시총 tier별 one-way cost (provisional house): 상위33%=5bp/중=10bp/하=15bp
    m = mcg.loc[t, [x for x in tkrs if x in mcg.columns]].dropna()
    if not len(m): return pd.Series(10.0, index=tkrs)
    q = m.rank(pct=True)
    c = pd.Series(15.0, index=m.index); c[q>=1/3]=10.0; c[q>=2/3]=5.0
    return c.reindex(tkrs).fillna(10.0)

def ic(fr, rr):
    d=pd.concat([fr,rr],axis=1).dropna(); d.columns=["f","r"]
    return d["f"].rank().corr(d["r"].rank()) if len(d)>=30 else np.nan

print("="*80); print("B2~B5 BROAD cost-aware retest — top-1500 PIT (DIAGNOSTIC; kill조건 대조)"); print("="*80)
print(f"유니버스 월수={len(rebal)} · 종목 union={u.ticker.nunique()}")
summary=[]
for name, fac in factors.items():
    ics=[]; gsp=[]; nsp=[]; tos=[]; ic_bylo=[]; ic_byhi=[]
    prevQ5=set(); prevQ1=set()
    for t in rebal[:-1]:
        mem=members[t]; cols=[c for c in fac.columns if c in mem]
        fr=fac.loc[t,cols]; rr=fwd.loc[t,cols]
        ics.append(ic(fr,rr))
        d=pd.concat([fr,rr],axis=1).dropna(); d.columns=["f","r"]
        if len(d)<50: continue
        rk=d["f"].rank(pct=True)
        Q5=set(d.index[rk>=0.8]); Q1=set(d.index[rk<=0.2])
        g=d.loc[list(Q5),"r"].mean()-d.loc[list(Q1),"r"].mean(); gsp.append(g)
        # turnover(one-way, Q5) + cost
        to5=len(Q5^prevQ5)/(2*max(len(Q5),1)) if prevQ5 else 1.0
        to1=len(Q1^prevQ1)/(2*max(len(Q1),1)) if prevQ1 else 1.0
        tos.append(to5)
        c5=cost_bps(list(Q5),t).mean()/1e4; c1=cost_bps(list(Q1),t).mean()/1e4
        nsp.append(g - (to5*c5 + to1*c1))     # net Q5-Q1 (양다리 비용 차감)
        prevQ5, prevQ1 = Q5, Q1
        # size-bucket IC: 시총 하위절반 vs 상위절반
        mm=mcg.loc[t, cols].reindex(d.index); half=mm.median()
        lo=d[mm<=half]; hi=d[mm>half]
        if len(lo)>=30: ic_bylo.append(lo["f"].rank().corr(lo["r"].rank()))
        if len(hi)>=30: ic_byhi.append(hi["f"].rank().corr(hi["r"].rank()))
    ics=pd.Series(ics).dropna(); gsp=pd.Series(gsp); nsp=pd.Series(nsp); tos=pd.Series(tos)
    icmean=ics.mean(); icir=icmean/ics.std() if ics.std()>0 else np.nan
    g_ann=gsp.mean()*12; n_ann=nsp.mean()*12; to_ann=tos.mean()*12
    iclo=pd.Series(ic_bylo).mean(); ichi=pd.Series(ic_byhi).mean()
    # kill 조건
    kills=[]
    if n_ann<=0: kills.append("net≤0")
    if not (abs(icir)>=0.20): kills.append("IC-IR<0.2")
    if to_ann>6: kills.append("turnover과도")
    if abs(iclo)>0.02 and abs(ichi)<0.01: kills.append("소형집중")
    verdict="DEAD" if kills else "SURVIVE(보수적 추가검증 필요)"
    summary.append((name, icmean, icir, g_ann, n_ann, to_ann, verdict, ";".join(kills)))
    print(f"\n[{name}]  → {verdict}  {('('+';'.join(kills)+')') if kills else ''}")
    print(f"  Rank IC={icmean:+.4f} IC-IR={icir:+.3f} IC>0={ (ics>0).mean()*100:.0f}% | gross Q5-Q1={g_ann*100:+.2f}%/yr | net={n_ann*100:+.2f}%/yr | turnover≈{to_ann*100:.0f}%/yr")
    print(f"  size-bucket IC: 하위절반={iclo:+.4f} 상위절반={ichi:+.4f}  (*수치 신뢰금지·단일백테스트*)")
s=pd.DataFrame(summary, columns=["sleeve","ic","ic_ir","gross_ann","net_ann","turnover_ann","verdict","kills"])
s.to_csv(os.path.join(OUT,"b2b5_broad_result.csv"), index=False)
ndead=(s.verdict.str.startswith("DEAD")).sum()
print("\n" + "="*80)
print(f"판정: {ndead}/4 DEAD.", "→ 단순팩터 family 종료 → Phase 1B" if ndead==4 else "→ survive sleeve는 보수적 추가검증(quarantine) 후 Phase 1B 입력")
print("→ outputs/b2b5_broad_result.csv")

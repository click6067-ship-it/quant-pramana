#!/usr/bin/env python3
"""NEXT-BAR 재계산 (Codex #1·look-ahead 제거 바닥). 신호는 월말 t(PIT) 그대로, *실현수익만 t+1 진입*.
equity MN sleeve + ETF trend sleeve를 next-bar로 재측정 → same-close 누수 제거. CAGR 무너지면 그게 진실.
저장: combined_book_nb_nav.csv(eq,ov) → portfolio_max가 픽업."""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import data, features as F, cost as C, universe as U
ENG=os.path.join(data.PHASE1A,"outputs","engine")

def next_bar_grid(price_index, rebal):
    """각 rebal 월말 *다음* 거래일."""
    nb=[]
    for d in rebal:
        pos=price_index.searchsorted(pd.Timestamp(d), side="right")
        nb.append(price_index[pos] if pos<len(price_index) else price_index[-1])
    return nb

def fwd_nextbar(px, rebal):
    """rebal i행 = ticker의 (nb[i] → nb[i+1]) 수익. 신호는 t, 수익은 t+1진입."""
    nb=next_bar_grid(px.index, rebal)
    pnb=px.reindex(pd.DatetimeIndex(nb)).ffill()
    ret=pnb.shift(-1)/pnb-1
    ret.index=pd.DatetimeIndex(rebal)
    return ret

# ── equity MN sleeve (next-bar) ──
def equity_sleeve(rebal, members):
    px=data.load("broad_SEP",usecols=["ticker","date","closeadj"]).pivot_table(index="date",columns="ticker",values="closeadj").sort_index()
    mc=data.load("DAILY_all",usecols=["ticker","date","marketcap"]).pivot_table(index="date",columns="ticker",values="marketcap").sort_index()
    sf1=data.load("broad_SF1"); sf1x=data.load("broad_SF1_ext"); sector=data.load_tickers()["sector"]
    mom=F.momentum(px,rebal); qual=F.quality(sf1,rebal,px.columns); EQ=F.event_subsignals(sf1x,rebal); mcg=mc.reindex(rebal,method="pad")
    fwd=fwd_nextbar(px,rebal)                                  # ★ next-bar 수익
    recs=[]; prevL=pd.Series(dtype=float); prevS=pd.Series(dtype=float)
    for t in rebal[:-1]:
        mem=[c for c in px.columns if c in members[t]]
        d=pd.DataFrame({"mom":mom.loc[t].reindex(mem),"qual":qual.loc[t].reindex(mem)})
        for k in F.EVENT_COLS: d[k]=EQ[k].loc[t].reindex(mem)
        d["fwd"]=fwd.loc[t].reindex(mem); d["mc"]=mcg.loc[t].reindex(mem); d["sec"]=sector.reindex(mem).values
        d["ev"]=F.composite(d,F.EVENT_COLS); d=d.dropna(subset=["mom","qual","ev","fwd","mc"])
        if len(d)<100: continue
        d["meta"]=pd.concat([F.zscore(d["mom"]),F.zscore(d["qual"]),F.zscore(d["ev"])],axis=1).mean(axis=1)
        d["sn"]=d["meta"]-d.groupby("sec")["meta"].transform("mean")
        rk=d["sn"].rank(pct=True); L=d[rk>=0.8]; S=d[rk<=0.2]
        wL=(pd.Series(1.0/len(L),index=L.index)).clip(upper=0.03); wL/=wL.sum()
        wS=(pd.Series(1.0/len(S),index=S.index)).clip(upper=0.03); wS/=wS.sum()
        gross=(wL*L["fwd"]).sum()-(wS*S["fwd"]).sum()
        toL=wL.subtract(prevL,fill_value=0).abs().sum()/2; toS=wS.subtract(prevS,fill_value=0).abs().sum()/2
        cL=C.tier_marketcap_bps(L["mc"]).mean()/C.BPS; cS=C.tier_marketcap_bps(S["mc"]).mean()/C.BPS
        net=gross-(toL*2*cL+toS*2*cS)-(0.005/12); recs.append((t,net)); prevL,prevS=wL,wS
    return pd.Series(dict(recs)).sort_index()

# ── ETF trend sleeve (next-bar) — equity와 *동일 rebal 그리드* 사용(정렬 보장) ──
def trend_sleeve(rebal):
    f=data.load("SFP_FUNDS",usecols=["ticker","date","closeadj"]).pivot_table(index="date",columns="ticker",values="closeadj").sort_index()
    TT=["SPY","QQQ","IWM","DIA","XLK","XLF","XLE","XLV","XLI","XLY","XLP","XLU","XLB","XLRE","XLC"]
    f=f[[c for c in TT if c in f.columns]]
    sma=f.rolling(200).mean(); above=f>sma
    spy=data.load("SFP_FUNDS",usecols=["ticker","date","closeadj"]); spy=spy[spy.ticker=="SPY"].set_index("date")["closeadj"].sort_index()
    rv=spy.pct_change().rolling(20).std()*np.sqrt(252)
    fwd=fwd_nextbar(f,rebal)                                   # ★ next-bar, 공통 그리드
    ab=above.reindex(rebal,method="pad"); rvg=rv.reindex(rebal,method="pad")
    recs=[]; prevw=pd.Series(0.0,index=f.columns)
    for t in rebal[:-1]:
        on=ab.loc[t]; on=on[on].index.tolist()
        w=pd.Series(0.0,index=f.columns)
        if on: w[on]=1.0/len(on)
        rm=0.5 if (rvg.get(t,0)>=0.20) else 1.0; w=w*rm
        ret=fwd.loc[t]; gross=float((w*ret).sum())
        to=(w-prevw).abs().sum(); net=gross-to*(0.0005); recs.append((t,net)); prevw=w
    return pd.Series(dict(recs)).sort_index()

def perf(r,m=12):
    r=r.dropna(); return dict(sh=r.mean()/r.std()*np.sqrt(m) if r.std()>0 else np.nan,
        cagr=(1+r).prod()**(m/len(r))-1, dd=((1+r).cumprod()/(1+r).cumprod().cummax()-1).min())

print("="*84); print("NEXT-BAR 재계산 (look-ahead 제거 — Codex #1). 신호 t·진입 t+1·공통 그리드"); print("="*84)
uni=U.rank_universe(1,1500); members={d:set(g) for d,g in uni.groupby("asof")["ticker"]}; rebal=sorted(uni["asof"].unique())
eq=equity_sleeve(rebal, members); ov=trend_sleeve(rebal)
df=pd.concat([eq.rename("eq"),ov.rename("ov")],axis=1).dropna()
pe=perf(df["eq"]); po=perf(df["ov"])
print(f"\n공통 {len(df)}개월 · corr +{df['eq'].corr(df['ov']):.2f}")
print(f"  equity MN (next-bar): Sharpe={pe['sh']:+.2f} CAGR={pe['cagr']*100:+.2f}% maxDD={pe['dd']*100:.1f}%")
print(f"  ETF trend (next-bar): Sharpe={po['sh']:+.2f} CAGR={po['cagr']*100:+.2f}% maxDD={po['dd']*100:.1f}%")
# same-close 대비
old=pd.read_csv(os.path.join(ENG,"combined_book_nav.csv"),index_col=0,parse_dates=True)
poe=perf(old["eq"]); poo=perf(old["ov"])
print(f"\n  [same-close 대비] equity Sharpe {poe['sh']:+.2f}→{pe['sh']:+.2f} · trend Sharpe {poo['sh']:+.2f}→{po['sh']:+.2f}")
print(f"  → next-bar haircut: equity {(pe['sh']-poe['sh']):+.2f}·trend {(po['sh']-poo['sh']):+.2f} Sharpe. {'견딤(CAGR 안 무너짐)' if po['cagr']>0.03 else '⚠️ 무너짐=same-close가 edge였음'}")
df.rename(columns={"eq":"eq","ov":"ov"}).to_csv(os.path.join(ENG,"combined_book_nb_nav.csv"))
print(f"  → outputs/engine/combined_book_nb_nav.csv (next-bar sleeve 수익)")

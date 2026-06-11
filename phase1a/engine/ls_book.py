#!/usr/bin/env python3
"""PRAMANA market-neutral L/S paper book — 본체(signal→risk engine→sizing→paper NAV).
신호: z(momentum)+z(quality)+z(event) 평균 → **섹터중립** → dollar-neutral L/S(top/bottom quintile).
리스크 엔진(deterministic veto): 섹터중립·per-name 상한·vol-target·**drawdown stop**.
비용(강화): 거래 tier(mc 5/10/15bp 양다리) + **tiered 숏 borrow(대형0.25/중0.5/소1.0%)**.
capacity: ADV(거래대금) 기반 max AUM 추정. ⚠️ paper(가상)·과거 백테스트 — no live. 새 알파 0(기존신호 결합).
사용: python engine/ls_book.py"""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import data, features as F, cost as C, universe as U

TARGET_VOL=0.10; MAX_LEV=3.0; CAP_NAME=0.03; DD_STOP=-0.08; DD_LOOK=3; CAP_KRW=100_000_000

def borrow_ann(mc):                         # tiered 숏 borrow(연): 대형0.25/중0.5/소1.0%
    q=mc.rank(pct=True); r=pd.Series(0.010,index=mc.index); r[q>=1/3]=0.005; r[q>=2/3]=0.0025
    return r

def build_panel():
    px=data.load("broad_SEP",usecols=["ticker","date","closeadj"]).pivot_table(index="date",columns="ticker",values="closeadj").sort_index()
    mc=data.load("DAILY_all",usecols=["ticker","date","marketcap"]).pivot_table(index="date",columns="ticker",values="marketcap").sort_index()
    sf1=data.load("broad_SF1"); sf1x=data.load("broad_SF1_ext"); sector=data.load_tickers()["sector"]
    uni=U.rank_universe(1,1500); members={d:set(g) for d,g in uni.groupby("asof")["ticker"]}; rebal=sorted(uni["asof"].unique())
    mpx=px.reindex(rebal,method="pad"); fwd=mpx.shift(-1)/mpx-1; mcg=mc.reindex(rebal,method="pad")
    mom=F.momentum(px,rebal); qual=F.quality(sf1,rebal,px.columns); EQ=F.event_subsignals(sf1x,rebal)
    recs=[]; prevL=pd.Series(dtype=float); prevS=pd.Series(dtype=float); caprows=[]
    # ADV(있으면)
    advmat=None
    vpath=os.path.join(data.RAW,"broad_volume.csv")
    if os.path.exists(vpath):
        try:
            pxu=data.load("broad_SEP",usecols=["ticker","date","closeunadj"]).pivot_table(index="date",columns="ticker",values="closeunadj").sort_index()
            vol=data.load("broad_volume",usecols=["ticker","date","volume"]).pivot_table(index="date",columns="ticker",values="volume").sort_index()
            advmat=(pxu*vol).rolling(20,min_periods=5).mean().reindex(rebal,method="pad")
        except Exception: advmat=None
    for t in rebal[:-1]:
        mem=[c for c in px.columns if c in members[t]]
        d=pd.DataFrame({"mom":mom.loc[t].reindex(mem),"qual":qual.loc[t].reindex(mem)})
        for k in F.EVENT_COLS: d[k]=EQ[k].loc[t].reindex(mem)
        d["fwd"]=fwd.loc[t].reindex(mem); d["mc"]=mcg.loc[t].reindex(mem); d["sec"]=sector.reindex(mem).values
        d["ev"]=F.composite(d,F.EVENT_COLS)
        d=d.dropna(subset=["mom","qual","ev","fwd","mc"])
        if len(d)<100: continue
        d["meta"]=pd.concat([F.zscore(d["mom"]),F.zscore(d["qual"]),F.zscore(d["ev"])],axis=1).mean(axis=1)
        d["meta_sn"]=d["meta"]-d.groupby("sec")["meta"].transform("mean")        # 섹터중립
        rk=d["meta_sn"].rank(pct=True); L=d[rk>=0.8].copy(); S=d[rk<=0.2].copy()
        wL=pd.Series(1.0/len(L),index=L.index).clip(upper=CAP_NAME); wL/=wL.sum() # per-name 상한
        wS=pd.Series(1.0/len(S),index=S.index).clip(upper=CAP_NAME); wS/=wS.sum()
        gross=(wL*L["fwd"]).sum()-(wS*S["fwd"]).sum()
        toL=(wL.subtract(prevL,fill_value=0).abs().sum())/2; toS=(wS.subtract(prevS,fill_value=0).abs().sum())/2
        cL=C.tier_marketcap_bps(L["mc"]).mean()/C.BPS; cS=C.tier_marketcap_bps(S["mc"]).mean()/C.BPS
        tcost=toL*2*cL+toS*2*cS                                                  # 양다리 round-trip 근사
        bcost=borrow_ann(S["mc"]).mean()/12
        net=gross-tcost-bcost
        recs.append(dict(t=t,gross=gross,net=net,bench=(d["mc"]*d["fwd"]).sum()/d["mc"].sum(),
                         secmax=L.groupby("sec").size().max()/len(L)))
        # capacity: AUM where 10p 참가율<10% ADV
        if advmat is not None:
            dw=pd.concat([wL.subtract(prevL,fill_value=0).abs(),wS.subtract(prevS,fill_value=0).abs()])
            adv=advmat.loc[t].reindex(dw.index)
            cap=(0.10*adv/dw.replace(0,np.nan)).dropna()
            if len(cap): caprows.append(cap.quantile(0.10))
        prevL,prevS=wL,wS
    R=pd.DataFrame(recs).set_index("t")
    return R, (np.median(caprows) if caprows else None)

def risk_size(net):
    """vol-target(PIT trailing) + drawdown stop. no look-ahead."""
    out=[]; lev=[]; realized=[]
    for i in range(len(net)):
        past=pd.Series(realized[max(0,i-12):i])
        v=past.std()*np.sqrt(12) if len(past)>=6 and past.std()>0 else np.nan
        k=min(MAX_LEV,TARGET_VOL/v) if (v==v and v>0) else 1.0
        dd3=np.prod([1+x for x in realized[max(0,i-DD_LOOK):i]])-1 if i>=DD_LOOK else 0.0
        if dd3<DD_STOP: k*=0.5                                                   # drawdown stop=de-risk
        r=net.iloc[i]*k; out.append(r); lev.append(k); realized.append(r)
    return pd.Series(out,index=net.index), pd.Series(lev,index=net.index)

def st(r,label):
    m=12; sh=r.mean()/r.std()*np.sqrt(m) if r.std()>0 else np.nan
    nav=(1+r).cumprod(); dd=(nav/nav.cummax()-1).min(); cagr=(1+r).prod()**(m/len(r))-1
    rec=r[r.index>="2021-01-01"]; rs=rec.mean()/rec.std()*np.sqrt(m) if rec.std()>0 else np.nan
    print(f"  {label:18s} CAGR={cagr*100:+6.2f}% vol={r.std()*np.sqrt(m)*100:4.1f}% Sharpe={sh:+.2f} maxDD={dd*100:5.1f}% | 2021-26 Sh={rs:+.2f}")
    return nav

def main():
    print("="*86); print("PRAMANA — Market-Neutral L/S Paper Book v2 (리스크엔진+강화비용+capacity)"); print("="*86)
    R,cap=build_panel()
    sc,lev=risk_size(R["net"])
    print(f"\n기간 {R.index.min().date()}~{R.index.max().date()} · {len(R)}개월 · 섹터중립·per-name≤{CAP_NAME*100:.0f}%·vol-target {TARGET_VOL*100:.0f}%·DD-stop {DD_STOP*100:.0f}%/{DD_LOOK}m")
    print("\n[성과] (비용 후: 거래 tier 양다리 + tiered 숏 borrow)")
    st(R["gross"],"gross(무비용)"); st(R["net"],"net(비용후)"); navs=st(sc,"net+risk엔진")
    print(f"\n  시장상관 net={R['net'].corr(R['bench']):+.2f} (≈0 시장중립) · 평균 레버리지 {lev.mean():.2f}x · 최대 섹터편중(long) {R['secmax'].mean()*100:.0f}%")
    print(f"  capacity(ADV 10%참가 기준 max AUM): {('≈$'+format(int(cap),',')+' (이 위로 체결충격 발생)') if cap else 'volume 미pull → 추후'}")
    print(f"\n[가상 ₩100M (net+risk엔진)] 1억 → ₩{CAP_KRW*navs.iloc[-1]/1e8:.2f}억 ({(navs.iloc[-1]-1)*100:+.0f}% 누적, {len(R)//12}년)")
    yr=(1+sc).groupby(sc.index.year).prod()-1
    print("[연도별] "+" ".join(f"{y}:{v*100:+.0f}%" for y,v in yr.items()))
    out=os.path.join(data.PHASE1A,"outputs","engine","ls_book_v2_nav.csv")
    pd.DataFrame({"gross":R["gross"],"net":R["net"],"net_risk":sc,"lev":lev,"nav":navs,"bench":R["bench"]}).to_csv(out)
    print(f"\n  → {out} · ⚠️ paper(가상)·no live · 숏 borrow 가정·일별체결 미반영(capacity로 한계 명시)")

if __name__ == "__main__":
    main()

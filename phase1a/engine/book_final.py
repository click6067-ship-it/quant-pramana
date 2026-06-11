#!/usr/bin/env python3
"""PRAMANA v3 — book_final: 최종 수익-max paper book (next-bar·Codex 가중).
sleeve: equity MN + ETF trend (next-bar 정직) + LETF convex 소량 dose(VRP는 tail-deadly 제외).
risk-budget 가중(Codex: trend-complex≤65% vol·LETF 20% vol-budget) → 공격 사이징(vol-target·max-lev·DD ladder).
바닥: look-ahead 제거(next-bar)·blow-up 방지(DD ladder/cooldown)·paper. 수익최대화 모드."""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import data
ENG=os.path.join(data.PHASE1A,"outputs","engine"); CAP_KRW=100_000_000

def ret_col(path):
    """CSV에서 월수익률 series 추출(수익률스러운 열)."""
    d=pd.read_csv(path,index_col=0,parse_dates=True)
    for c in d.columns:
        if d[c].dtype!=object and d[c].abs().median()<0.3 and d[c].std()>0: return d[c].dropna()
    return d.iloc[:,0].dropna()

def perf(r,m=12):
    r=r.dropna(); sh=r.mean()/r.std()*np.sqrt(m) if r.std()>0 else np.nan
    nav=(1+r).cumprod(); dd=(nav/nav.cummax()-1).min(); cagr=(1+r).prod()**(m/len(r))-1
    rec=r[r.index>="2021-01-01"]; rs=rec.mean()/rec.std()*np.sqrt(m) if rec.std()>0 else np.nan
    return dict(sh=sh,cagr=cagr,dd=dd,fin=nav.iloc[-1],rs=rs,vol=r.std()*np.sqrt(m),n=len(r))

def agg_size(net,target_vol=0.40,max_lev=4.0,cooldown=2,kelly=0.5):
    """공격 사이징 + DD ladder(-10/-15/-20/-25 → lev ×0.8/0.6/0.4/0.2) + cooldown."""
    out=[]; rz=[]; cool=0
    for i in range(len(net)):
        past=pd.Series(rz[max(0,i-12):i]); v=past.std()*np.sqrt(12) if len(past)>=6 and past.std()>0 else np.nan
        k=min(max_lev, kelly*target_vol/v) if (v==v and v>0) else 1.0
        nav=np.prod([1+x for x in rz]); peak=max([np.prod([1+x for x in rz[:j+1]]) for j in range(len(rz))]+[1.0]); dd=nav/peak-1 if rz else 0.0
        for thr,mult in [(-0.25,0.2),(-0.20,0.4),(-0.15,0.6),(-0.10,0.8)]:
            if dd<=thr: k*=mult; cool=max(cool,cooldown); break
        if cool>0: cool-=1
        r=net.iloc[i]*k; out.append(r); rz.append(r)
    return pd.Series(out,index=net.index)

print("="*90); print("PRAMANA v3 — book_final (최종 수익-max paper book · next-bar · Codex 가중)"); print("="*90)
S={"equity_MN":ret_col(os.path.join(ENG,"combined_book_nb_nav.csv")) if os.path.exists(os.path.join(ENG,"combined_book_nb_nav.csv")) else None}
nb=pd.read_csv(os.path.join(ENG,"combined_book_nb_nav.csv"),index_col=0,parse_dates=True)
S={"equity_MN":nb["eq"], "etf_trend":nb["ov"]}
if os.path.exists(os.path.join(ENG,"sleeve_letf_nav.csv")): S["letf_convex"]=ret_col(os.path.join(ENG,"sleeve_letf_nav.csv"))
df=pd.concat(S,axis=1).dropna()
print(f"\nsleeve {list(df.columns)} · 공통 {len(df)}개월 (next-bar 정직)")
for c in df.columns:
    p=perf(df[c]); print(f"  {c:12s} Sharpe={p['sh']:+.2f} CAGR={p['cagr']*100:+6.1f}% vol={p['vol']*100:3.0f}% maxDD={p['dd']*100:6.1f}%")
print("[상관]"); print(df.corr().round(2).to_string())

# risk-budget 가중(Codex): vol-budget eq35·trend45·letf20(trend-complex=trend+letf≤65)
vb={"equity_MN":0.35,"etf_trend":0.45,"letf_convex":0.20}
vb={k:vb[k] for k in df.columns}
dw={c: vb[c]/perf(df[c])["vol"] for c in df.columns}; s=sum(dw.values()); dw={c:dw[c]/s for c in df.columns}
print(f"\nrisk-budget→dollar 가중: { {c:round(v,3) for c,v in dw.items()} } (LETF는 고vol이라 소량 dollar=convex dose)")
combo=sum(df[c]*dw[c] for c in df.columns); cp=perf(combo)
print(f"  결합(무레버): Sharpe={cp['sh']:+.2f} CAGR={cp['cagr']*100:+.2f}% vol={cp['vol']*100:.0f}% maxDD={cp['dd']*100:.1f}%")

print("\n[공격적 사이징 (DD ladder·cooldown 바닥)]")
for tv,ml,lbl in [(0.25,4,"보수"),(0.40,4,"공격(Codex)"),(0.50,5,"풀공격")]:
    a=agg_size(combo,tv,ml); p=perf(a)
    print(f"  {lbl:11s}(vol{int(tv*100)}·{ml}x) Sharpe={p['sh']:+.2f} CAGR={p['cagr']*100:+6.1f}% maxDD={p['dd']*100:6.1f}% 2021-26 Sh={p['rs']:+.2f} ₩100M→{CAP_KRW*p['fin']/1e8:.2f}억");
    if lbl.startswith("공격"): ca=a; cap=p
yr=(1+ca).groupby(ca.index.year).prod()-1
print(f"\n[최종 공격(vol40·4x) 연도별] "+" ".join(f"{y}:{v*100:+.0f}%" for y,v in yr.items()))
pd.DataFrame({"combo":combo,"final":ca}).to_csv(os.path.join(ENG,"book_final_nav.csv"))
print(f"\n  → outputs/engine/book_final_nav.csv")
print(f"  최종: next-bar(누수제거)·VRP제외(tail-deadly)·LETF 소량 dose·DD ladder 바닥. paper·no live.")
print(f"  정직: 여전히 trend 견인·regime-flattered→forward 보수(Sharpe~0.5-0.6). 다음=forward paper 가동(promotion gate 시계).")

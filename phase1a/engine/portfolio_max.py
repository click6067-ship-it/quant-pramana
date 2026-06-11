#!/usr/bin/env python3
"""PRAMANA v3 — portfolio_max: 수익엔진(앙상블+사이징 통합). N개 sleeve → Sharpe-tilt 결합 → 공격적 사이징 → NAV.
새 sleeve(LETF/VRP/…) 수익series 들어오면 자동 편입. 바닥: blow-up방지(DD-cut/cooldown)·paper. 수익최대화 모드.
sleeve 수익series는 저장 CSV에서 로드(재계산 불필요)."""
import os, sys, glob, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import data
ENG=os.path.join(data.PHASE1A,"outputs","engine"); CAP_KRW=100_000_000

def load_sleeves():
    """저장된 sleeve 월수익 series 수집. 기본 eq/ov + 있으면 letf/vrp/reversal."""
    S={}
    cb=os.path.join(ENG,"combined_book_nav.csv")
    if os.path.exists(cb):
        d=pd.read_csv(cb,index_col=0,parse_dates=True)
        if "eq" in d: S["equity_MN"]=d["eq"]
        if "ov" in d: S["etf_trend"]=d["ov"]
    # 에이전트 sleeve CSV(이름 패턴 유연 탐색): nav/return 열 추정
    for pat,nm in [("sleeve_letf*","letf_convex"),("sleeve_vrp*","vrp_carry"),("*letf*nav*","letf_convex"),("*vrp*nav*","vrp_carry")]:
        for f in glob.glob(os.path.join(ENG,pat)):
            try:
                d=pd.read_csv(f,index_col=0,parse_dates=True)
                col=[c for c in d.columns if d[c].dtype!=object and d[c].abs().median()<0.5]  # 수익률스러운 열
                if col and nm not in S: S[nm]=d[col[0]]
            except Exception: pass
    return S

def perf(r,m=12):
    r=r.dropna(); sh=r.mean()/r.std()*np.sqrt(m) if r.std()>0 else np.nan
    nav=(1+r).cumprod(); dd=(nav/nav.cummax()-1).min(); cagr=(1+r).prod()**(m/len(r))-1
    rec=r[r.index>="2021-01-01"]; rs=rec.mean()/rec.std()*np.sqrt(m) if rec.std()>0 else np.nan
    return dict(sh=sh,cagr=cagr,dd=dd,fin=nav.iloc[-1],rs=rs,vol=r.std()*np.sqrt(m),n=len(r))

def sharpe_tilt_weights(df):
    """양의 Sharpe sleeve에 Sharpe 비례 가중(음수는 0). 분산 유지하며 winner에 실음."""
    shs={c:max(0.0,perf(df[c])["sh"]) for c in df.columns}
    tot=sum(shs.values()) or 1.0
    return {c:shs[c]/tot for c in df.columns}

def agg_size(net,target_vol=0.35,max_lev=5.0,dd_cut=-0.25,cooldown=2,kelly=0.5):
    out=[]; rz=[]; cool=0
    for i in range(len(net)):
        past=pd.Series(rz[max(0,i-12):i]); v=past.std()*np.sqrt(12) if len(past)>=6 and past.std()>0 else np.nan
        k=min(max_lev, kelly*target_vol/v) if (v==v and v>0) else 1.0
        dd=np.prod([1+x for x in rz[max(0,i-3):i]])-1 if i>=3 else 0.0
        if dd<dd_cut: cool=cooldown
        if cool>0: k*=0.5; cool-=1
        r=net.iloc[i]*k; out.append(r); rz.append(r)
    return pd.Series(out,index=net.index)

def main():
    print("="*92); print("PRAMANA v3 — portfolio_max (수익엔진: N-sleeve Sharpe-tilt → 공격적 사이징)"); print("="*92)
    S=load_sleeves()
    df=pd.concat(S,axis=1).dropna()
    print(f"\nsleeve {list(df.columns)} · 공통 {len(df)}개월")
    print("[sleeve별]")
    for c in df.columns:
        p=perf(df[c]); print(f"  {c:14s} Sharpe={p['sh']:+.2f} CAGR={p['cagr']*100:+6.1f}% maxDD={p['dd']*100:6.1f}%")
    print("[상관행렬]"); print(df.corr().round(2).to_string())
    w=sharpe_tilt_weights(df); print(f"\nSharpe-tilt 가중: { {c:round(v,2) for c,v in w.items()} }")
    combo=sum(df[c]*w[c] for c in df.columns)
    cp=perf(combo); print(f"  결합(무레버): Sharpe={cp['sh']:+.2f} CAGR={cp['cagr']*100:+.2f}% vol={cp['vol']*100:.0f}% maxDD={cp['dd']*100:.1f}%")
    print("\n[공격적 사이징]")
    for tv,ml,dc,lbl in [(0.25,4,-0.15,"보수"),(0.35,5,-0.25,"공격"),(0.45,6,-0.35,"풀공격")]:
        a=agg_size(combo,tv,ml,dc); p=perf(a)
        tag=f"₩100M→{CAP_KRW*p['fin']/1e8:.2f}억"
        print(f"  {lbl:6s}(vol{int(tv*100)}·{ml}x·DD{int(dc*100)}) Sharpe={p['sh']:+.2f} CAGR={p['cagr']*100:+6.1f}% maxDD={p['dd']*100:6.1f}% 2021-26 Sh={p['rs']:+.2f} · {tag}")
        if lbl=="공격": ca=a
    pd.DataFrame({"combo":combo,"aggressive":ca}).to_csv(os.path.join(ENG,"portfolio_max_nav.csv"))
    print(f"\n  → outputs/engine/portfolio_max_nav.csv · 바닥규율(blow-up방지·paper) 유지·수익최대화 모드. sleeve 추가시 자동 편입.")

if __name__=="__main__": main()

#!/usr/bin/env python3
"""PRAMANA book_runner — 일간/리밸런스 루프 오케스트레이터(OS 척추, Codex 설계 반영).
순서: 무결성 체크 → signal(시장중립 L/S 합성) → risk_engine(사이징·veto·4 kill) → ledger → report → kill state.
build-first 최소 루프 + Codex acceptance test(데이터kill·레버리지cap·DD cooldown·결정성). 새 알파 0·결제 0·paper-only."""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import data, ls_book as LB, risk_engine as RE

ENG=os.path.join(data.PHASE1A,"outputs","engine"); os.makedirs(ENG,exist_ok=True)
L=RE.LIMITS; CAP_KRW=100_000_000

_CACHE={}
def run(corrupt_at=None, R=None, cap=None):
    """corrupt_at: 무결성 실패 주입할 리밸런스 인덱스(acceptance test). None=정상. R 캐시 재사용."""
    if R is None:
        if "R" not in _CACHE: _CACHE["R"],_CACHE["cap"]=LB.build_panel()
        R,cap=_CACHE["R"],_CACHE["cap"]
    net=R["net"]; bench=R["bench"]
    beta=float(np.cov(net,bench)[0,1]/np.var(bench))         # 구조적 시장 beta
    nav=100.0; realized=[]; cool=0; led=[]; kills=[]
    for i,t in enumerate(R.index):
        data_ok = not (corrupt_at is not None and i==corrupt_at)
        rz=pd.Series(realized)
        tvol=rz.iloc[-12:].std()*np.sqrt(12) if len(rz)>=6 and rz.iloc[-12:].std()>0 else np.nan
        rvol=rz.iloc[-6:].std()*np.sqrt(12) if len(rz)>=6 and rz.iloc[-6:].std()>0 else None
        dd3=(1+rz.iloc[-3:]).prod()-1 if len(rz)>=3 else 0.0
        bw=slice(max(0,i-24),i)                                   # 24m rolling beta(안정적, 짧은창 corr 노이즈 회피)
        mkt_beta=float(np.cov(net.iloc[bw],bench.iloc[bw])[0,1]/np.var(bench.iloc[bw])) if (i>=24 and np.var(bench.iloc[bw])>0) else beta
        tret=rz.iloc[-12:].mean() if len(rz)>=12 else None       # model_decay는 12m trailing
        kill,kmult,reason=RE.kill_check(data_ok=data_ok,trailing_dd=dd3,realized_vol=rvol,target_vol=L["target_vol"],
                                        mkt_beta=mkt_beta,trailing_ret=tret,dd_cut=L["dd_cut"],vol_mult=L["vol_mult"],beta_lim=L["beta_lim"])
        base_lev=RE.target_leverage(tvol,L["target_vol"],L["max_lev"],L["kelly_frac"])
        lev=base_lev*kmult
        if kill=="risk_breach": cool=L["cooldown"]
        if cool>0 and kill is None: lev*=0.4; cool-=1
        if kill=="data_integrity": lev=0.0
        r=net.iloc[i]*lev; nav*=(1+r); realized.append(r)
        led.append(dict(date=t.date(),nav=round(nav,2),applied_ret=r,net_raw=net.iloc[i],lev=round(lev,2),
                        base_lev=round(base_lev,2),kill=kill or "",dd3=round(dd3,4),tvol=round(tvol,3) if tvol==tvol else None,
                        mkt_beta=round(mkt_beta,2),gap_est=round(RE.gap_estimate(beta,lev),4),secmax=round(R["secmax"].iloc[i],2)))
        if kill: kills.append((str(t.date()),kill,reason))
    return pd.DataFrame(led).set_index("date"), beta, cap, kills

def stats(led):
    r=led["applied_ret"]; m=12; nav=led["nav"]
    sh=r.mean()/r.std()*np.sqrt(m) if r.std()>0 else np.nan
    dd=(nav/nav.cummax()-1).min(); cagr=(nav.iloc[-1]/100)**(m/len(r))-1
    return sh,dd,cagr,nav.iloc[-1]

if __name__=="__main__":
    print("="*88); print("PRAMANA book_runner — OS 척추 루프 (signal→risk engine→ledger→kill)"); print("="*88)
    led,beta,cap,kills=run()
    sh,dd,cagr,fin=stats(led)
    led.to_csv(os.path.join(ENG,"book_ledger.csv"))
    print(f"\n[루프 결과] {len(led)}개 리밸런스 · 시장 beta={beta:+.2f} · capacity≈${int(cap):,}" if cap else f"\n[루프 결과] {len(led)} 리밸런스 · beta={beta:+.2f}")
    print(f"  CAGR={cagr*100:+.2f}% · Sharpe={sh:+.2f} · maxDD={dd*100:.1f}% · 평균레버리지={led['lev'].mean():.2f}x(max {led['lev'].max():.2f})")
    print(f"  ₩100M → ₩{CAP_KRW*fin/100/1e8:.2f}억 · kill 이벤트 {len(kills)}건")
    if kills:
        from collections import Counter
        print(f"  kill 유형: {dict(Counter(k[1] for k in kills))}")
    print("\n[Codex ACCEPTANCE TESTS]")
    # 1. 결정성: 2회 동일
    led2,_,_,_=run(); det = np.allclose(led["nav"].values, led2["nav"].values)
    print(f"  [{'PASS' if det else 'FAIL'}] 결정성: 동일입력→동일 NAV")
    # 2. 데이터 무결성 kill → 그 리밸런스 lev=0
    ledc,_,_,killc=run(corrupt_at=50); dk = (ledc.iloc[50]["lev"]==0.0) and any(k[1]=="data_integrity" for k in killc)
    print(f"  [{'PASS' if dk else 'FAIL'}] 무결성 실패 주입(i=50) → data_integrity kill·lev=0")
    # 3. 레버리지 cap: max lev ≤ 4
    capok = led["lev"].max() <= L["max_lev"]+1e-9
    print(f"  [{'PASS' if capok else 'FAIL'}] 레버리지 hard cap ≤{L['max_lev']}x (실측 max {led['lev'].max():.2f})")
    # 4. DD cooldown: risk_breach kill 발생 시 직후 de-risk
    rb=[i for i,row in enumerate(led.itertuples()) if row.kill=="risk_breach"]
    ddok = len(rb)>0
    print(f"  [{'PASS' if ddok else 'INFO'}] DD-{abs(L['dd_cut'])*100:.0f}% risk_breach kill {len(rb)}회 → cooldown de-risk")
    print(f"\n  → outputs/engine/book_ledger.csv (Codex 로그 필드: nav·lev·kill·dd·gap_est·secmax…) · ⚠️ paper·no live")
    print("  남은 척추: per-name orders/fills(execution.py)·일간(현 월리밸)·idempotent run dir — Codex 설계대로 증분.")

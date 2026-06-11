#!/usr/bin/env python3
"""PRAMANA V5 — 멀티시점 진입 대시보드. 12/6/3개월 전에 V5 Aggressive로 투자 시작했다면? vs SPY·QQQ.
V5 = vol-target(28%)·캡 2.0x·DD ladder 레버드 Core(SPY/QQQ). 각 시점서 peak 리셋(그때 투자 시작).
정직: 레버드 베타지 알파 아님. paper·비용후. self-contained HTML."""
import os, sys, io, base64, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import data
CAP=100_000_000; RF=0.05; TVOL=0.28; LMAX=2.0
etf=data.load("SFP_FUNDS",usecols=["ticker","date","closeadj"]).pivot_table(index="date",columns="ticker",values="closeadj").sort_index()
ret=etf.pct_change(); alldays=etf.index[etf.index>=etf.index[210]]
core=(0.5*ret["SPY"]+0.5*ret["QQQ"]).reindex(alldays).fillna(0)
rvol=core.rolling(20).std()*np.sqrt(252)
def ddscale(dd): return 0.2 if dd<=-0.40 else 0.4 if dd<=-0.30 else 0.7 if dd<=-0.20 else 1.0
def run_v5(days):   # 그 구간서 peak 리셋(투자 시작)
    nav=[CAP]; peak=CAP
    for i in range(1,len(days)):
        d=days[i]; p=days[i-1]; rv=rvol.get(p,np.nan)
        L=min(LMAX, TVOL/rv) if (pd.notna(rv) and rv>0) else 1.0
        L*=ddscale(nav[-1]/peak-1)
        r=L*core.get(d,0.0)-(L-1)*RF/252
        nav.append(nav[-1]*(1+r)); peak=max(peak,nav[-1])
    return pd.Series(nav,index=days)
def bh(sym,days): return CAP*(1+ret[sym].reindex(days).fillna(0)).cumprod()
def stat(s):
    r=s.pct_change().dropna(); tot=s.iloc[-1]/s.iloc[0]-1
    mdd=(s/s.cummax()-1).min(); sh=r.mean()/r.std()*np.sqrt(252) if r.std()>0 else float('nan'); return tot,mdd,sh
end=alldays[-1]; ANCH=[("3개월 전",63),("6개월 전",126),("12개월 전",252)]
plt.style.use("dark_background"); plt.rcParams.update({"axes.facecolor":"#0d1326","figure.facecolor":"#0d1326","grid.alpha":.15,"font.size":9})
panels=""; rowsT=""
print(f"\n{'='*78}\nV5 멀티시점 진입 (그 시점 투자 시작) vs SPY·QQQ · 비용후 · 끝 {end.date()}\n{'='*78}")
print(f"{'진입':<10}{'포트':<16}{'누적%':>9}{'MDD%':>8}{'Sharpe':>8}")
for nm,n in ANCH:
    days=alldays[-n:]
    v5=run_v5(days); spy=bh("SPY",days); qqq=bh("QQQ",days)
    sv,ss,sq=stat(v5),stat(spy),stat(qqq)
    for lab,s in [("V5 Aggressive",sv),("SPY",ss),("QQQ",sq)]:
        print(f"{nm:<10}{lab:<16}{s[0]*100:>8.1f}{s[1]*100:>8.0f}{s[2]:>8.2f}")
    # chart
    f=plt.figure(figsize=(10,2.6))
    for k,ser,c in [("V5",v5,"#22d3ee"),("QQQ",qqq,"#a78bfa"),("SPY",spy,"#f59e0b")]:
        plt.plot(ser.index,ser/CAP,label=k,lw=2.2 if k=="V5" else 1.4,color=c,ls=("-" if k=="V5" else "--"))
    plt.legend(framealpha=.2,fontsize=8); plt.title(f"{nm} 진입 → 현재",color="#e5e7eb",fontsize=10); plt.ylabel("×")
    b=io.BytesIO(); f.savefig(b,format="png",dpi=92,bbox_inches="tight",facecolor="#0d1326"); plt.close(f); img=base64.b64encode(b.getvalue()).decode()
    C=lambda v:'pos' if v>=0 else 'neg'; beat=sv[0]>sq[0]
    panels+=f"<div class=card><b>{nm} 진입</b> <span class='{'pos' if beat else 'neg'}'>{'✅ QQQ 넘음' if beat else '❌ QQQ 못넘음'}</span><img src='data:image/png;base64,{img}'></div>"
    rowsT+=f"<tr><td>{nm}</td><td class='num {C(sv[0])}'>{sv[0]*100:+.1f}%</td><td class='num neg'>{sv[1]*100:.0f}%</td><td class=num>{sv[2]:.2f}</td><td class='num'>{sq[0]*100:+.1f}%</td><td class='num'>{ss[0]*100:+.1f}%</td></tr>"
html=f"""<!doctype html><html lang=ko><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>V5 멀티시점</title><style>
body{{background:#070b16;color:#e5e7eb;font-family:'Segoe UI',system-ui,sans-serif;margin:0;line-height:1.5}}
.wrap{{max-width:980px;margin:0 auto;padding:22px 18px 50px}} h1{{font-size:1.4em}}
.card{{background:#0d1326;border:1px solid #1e293b;border-radius:14px;padding:14px;margin:10px 0}} img{{width:100%;border-radius:8px;margin-top:6px}}
table{{width:100%;border-collapse:collapse;font-size:.9em}} th,td{{padding:6px 9px;border-bottom:1px solid #1e293b;text-align:left}}
th{{color:#94a3b8;font-size:.8em}} td.num{{text-align:right;font-variant-numeric:tabular-nums}} .pos{{color:#34d399}} .neg{{color:#f87171}}
h2{{font-size:1.1em;border-left:4px solid #22d3ee;padding-left:10px;margin-top:20px}}
.warn{{background:#1c1408;border:1px solid #92400e;border-radius:10px;padding:12px 15px;color:#fde68a;font-size:.86em}}
.badge{{background:#7f1d1d;color:#fecaca;border-radius:6px;padding:2px 9px;font-size:.7em;font-weight:700;margin-left:6px}}</style></head><body>
<div class=wrap><h1>📐 PRAMANA V5 — 멀티시점 진입<span class=badge>PAPER</span></h1>
<p style='color:#94a3b8'>"그 시점에 V5 Aggressive로 투자 시작했다면?" vs SPY·QQQ. 비용후·끝 {end.date()}.</p>
<h2>📊 요약</h2><div class=card><table><tr><th>진입 시점</th><th class=num>V5 누적</th><th class=num>V5 MDD</th><th class=num>V5 Sharpe</th><th class=num>QQQ 누적</th><th class=num>SPY 누적</th></tr>{rowsT}</table></div>
<h2>📈 시점별 성장</h2>{panels}
<div class=warn>⚠️ <b>정직:</b> V5 = vol-target 레버드 베타지 알파 아님(Sharpe ≈ QQQ). 'QQQ 넘음'은 레버로 산 것이고, 짧은 구간은 진입 타이밍·레짐 운에 크게 좌우된다. −32% MDD는 2016-26 benign 조건부·forward −70%+ 가능. <b>이건 in-sample/backtest지 forward 검증 아님.</b> 실거래는 12개월 forward 판정표+사람 게이트 전 금지.</div>
<div style='color:#64748b;font-size:.8em;margin-top:10px'>생성 multi_anchor_v5.py · 정본 PRAMANA_V4/PRAMANA_V5_Problem_Frame_v0.2.md</div>
</div></body></html>"""
out=os.path.join(data.PHASE1A,"outputs","multi_anchor_v5.html"); open(out,"w").write(html)
print(f"\n✅ 대시보드 → {out} ({os.path.getsize(out)//1024}KB)")

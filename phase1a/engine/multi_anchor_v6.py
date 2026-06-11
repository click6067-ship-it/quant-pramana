#!/usr/bin/env python3
"""PRAMANA V6 — 멀티시점 진입 대시보드. 12/6/3개월 전 V6로 투자 시작했다면? vs SPY·QQQ.
V6 = 85% 레버드 Core(SPY/QQQ·vol-target28%·캡1.5x·DD ladder) + 15% managed-futures(DBMF). free yfinance."""
import os, sys, io, base64, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
CAP=100_000_000; RF=0.05; TVOL=0.28; LMAX=1.5; MF=0.15
import yfinance as yf
px=yf.download(["SPY","QQQ","DBMF"],period="max",interval="1d",auto_adjust=True,progress=False)
px=(px["Close"] if isinstance(px.columns,pd.MultiIndex) else px).dropna()
ret=px.pct_change(); core=0.5*ret["SPY"]+0.5*ret["QQQ"]; rvol=core.rolling(20).std()*np.sqrt(252)
alldays=core.dropna().index; alldays=alldays[alldays>=rvol.dropna().index[0]]
def ddscale(dd): return 0.2 if dd<=-0.40 else 0.4 if dd<=-0.30 else 0.7 if dd<=-0.20 else 1.0
def run_v6(days):
    nav=[CAP]; peak=CAP
    for i in range(1,len(days)):
        d=days[i]; p=days[i-1]; rv=rvol.get(p,np.nan)
        L=min(LMAX,TVOL/rv) if (pd.notna(rv) and rv>0) else 1.0; L*=ddscale(nav[-1]/peak-1)
        core_r=L*core.get(d,0)-(L-1)*RF/252
        nav.append(nav[-1]*(1+(1-MF)*core_r+MF*ret["DBMF"].get(d,0))); peak=max(peak,nav[-1])
    return pd.Series(nav,index=days)
def bh(s,days): return CAP*(1+ret[s].reindex(days).fillna(0)).cumprod()
def stat(s): r=s.pct_change().dropna(); return s.iloc[-1]/s.iloc[0]-1,(s/s.cummax()-1).min(),(r.mean()/r.std()*np.sqrt(252) if r.std()>0 else float('nan'))
end=alldays[-1]; ANCH=[("3개월 전",63),("6개월 전",126),("12개월 전",252)]
plt.style.use("dark_background"); plt.rcParams.update({"axes.facecolor":"#0d1326","figure.facecolor":"#0d1326","grid.alpha":.15,"font.size":9})
panels=""; rowsT=""
print(f"\nV6 멀티시점 진입 vs SPY·QQQ · 끝 {end.date()}\n{'='*60}")
for nm,n in ANCH:
    days=alldays[-n:]; v6=run_v6(days); spy=bh("SPY",days); qqq=bh("QQQ",days)
    sv,ss,sq=stat(v6),stat(spy),stat(qqq)
    print(f"  {nm}: V6 {sv[0]*100:+.1f}%/{sv[1]*100:.0f}%MDD · SPY {ss[0]*100:+.1f}% · QQQ {sq[0]*100:+.1f}%")
    f=plt.figure(figsize=(10,2.6))
    for k,ser,c in [("V6",v6,"#22d3ee"),("QQQ",qqq,"#a78bfa"),("SPY",spy,"#f59e0b")]:
        plt.plot(ser.index,ser/CAP,label=k,lw=2.2 if k=="V6" else 1.4,color=c,ls=("-" if k=="V6" else "--"))
    plt.legend(framealpha=.2,fontsize=8); plt.title(f"{nm} 진입 → 현재",color="#e5e7eb",fontsize=10); plt.ylabel("×")
    b=io.BytesIO(); f.savefig(b,format="png",dpi=92,bbox_inches="tight",facecolor="#0d1326"); plt.close(f); img=base64.b64encode(b.getvalue()).decode()
    C=lambda v:'pos' if v>=0 else 'neg'; beat=sv[0]>sq[0]
    panels+=f"<div class=card><b>{nm} 진입</b> <span class='{'pos' if beat else 'neg'}'>{'QQQ 넘음' if beat else 'QQQ 못넘음'}</span> · MDD {sv[1]*100:.0f}%(QQQ {sq[1]*100:.0f}%)<img src='data:image/png;base64,{img}'></div>"
    rowsT+=f"<tr><td>{nm}</td><td class='num {C(sv[0])}'>{sv[0]*100:+.1f}%</td><td class='num neg'>{sv[1]*100:.0f}%</td><td class=num>{sv[2]:.2f}</td><td class='num'>{sq[0]*100:+.1f}%</td><td class='num'>{ss[0]*100:+.1f}%</td></tr>"
html=f"""<!doctype html><html lang=ko><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1"><title>V6 멀티시점</title><style>
body{{background:#070b16;color:#e5e7eb;font-family:'Segoe UI',system-ui,sans-serif;margin:0;line-height:1.5}}
.wrap{{max-width:980px;margin:0 auto;padding:22px 18px 50px}} h1{{font-size:1.35em}}
.card{{background:#0d1326;border:1px solid #1e293b;border-radius:14px;padding:14px;margin:10px 0}} img{{width:100%;border-radius:8px;margin-top:6px}}
table{{width:100%;border-collapse:collapse;font-size:.9em}} th,td{{padding:6px 9px;border-bottom:1px solid #1e293b;text-align:left}}
th{{color:#94a3b8;font-size:.8em}} td.num{{text-align:right}} .pos{{color:#34d399}} .neg{{color:#f87171}}
h2{{font-size:1.1em;border-left:4px solid #22d3ee;padding-left:10px;margin-top:20px}}
.warn{{background:#1c1408;border:1px solid #92400e;border-radius:10px;padding:12px 15px;color:#fde68a;font-size:.85em}}
.badge{{background:#7f1d1d;color:#fecaca;border-radius:6px;padding:2px 9px;font-size:.7em;font-weight:700;margin-left:6px}}</style></head><body>
<div class=wrap><h1>📐 PRAMANA V6 — 멀티시점 진입<span class=badge>PAPER</span></h1>
<p style='color:#94a3b8'>"그 시점에 V6(레버드 Core+15%DBMF)로 시작했다면?" vs SPY·QQQ. 비용후·끝 {end.date()}.</p>
<h2>📊 요약</h2><div class=card><table><tr><th>진입</th><th class=num>V6 누적</th><th class=num>V6 MDD</th><th class=num>V6 Sharpe</th><th class=num>QQQ</th><th class=num>SPY</th></tr>{rowsT}</table></div>
<h2>📈 시점별</h2>{panels}
<div class=warn>⚠️ V6 = 레버드 베타 + managed-futures 분산('같이 안 맞기'). alpha 아님·Sharpe≈QQQ. 짧은 구간은 진입 타이밍·레짐 운에 크게 좌우. backtest지 forward 검증 아님. paper·NO LIVE.</div>
<div style='color:#64748b;font-size:.8em;margin-top:8px'>생성 multi_anchor_v6.py · 시스템 원리 → pramana_system_map.html · 스펙 PRAMANA_V6_Problem_Frame_v0.1.md</div>
</div></body></html>"""
out=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","outputs","multi_anchor_v6.html"); open(out,"w").write(html)
print(f"✅ → outputs/multi_anchor_v6.html")

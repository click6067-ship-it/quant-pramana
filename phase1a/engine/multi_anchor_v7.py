#!/usr/bin/env python3
"""PRAMANA V7 4-sleeve — 멀티앵커 대시보드(12/6/3개월·풀 진입 → 현재) vs QQQ·SPY.
free yfinance·비용후·PAPER. PNG(채팅용) + HTML(브라우저). python engine/multi_anchor_v7.py"""
import os, warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, yfinance as yf
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
import io, base64
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
OUTDIR=os.path.join(ROOT,"outputs"); PNG=os.path.join(OUTDIR,"v7_multi_anchor.png"); HTML=os.path.join(OUTDIR,"v7_multi_anchor_dashboard.html")
W7={"SPY":0.25,"QQQ":0.25,"DBMF":0.25,"GLD":0.15,"IEF":0.10}
px=yf.download(list(W7),period="max",interval="1d",auto_adjust=True,progress=False)
px=(px["Close"] if isinstance(px.columns,pd.MultiIndex) else px).dropna()
ret=px.pct_change(); days0=ret.dropna().index
def v7(days): b=sum(W7[t]*ret[t] for t in W7); return (1+b.reindex(days).fillna(0)).cumprod()
def bh(s,days): return (1+ret[s].reindex(days).fillna(0)).cumprod()
def stat(nav): r=nav.pct_change().dropna(); return (nav.iloc[-1]/nav.iloc[0]-1,(nav/nav.cummax()-1).min(),(r.mean()/r.std()*np.sqrt(252) if r.std()>0 else float('nan')))
end=days0[-1]; ANCH=[("3개월",91),("6개월",182),("12개월",365),(f"풀 ({days0[0].date()}~)",99999)]
plt.style.use("dark_background"); plt.rcParams.update({"axes.facecolor":"#0d1326","figure.facecolor":"#070b16","grid.alpha":.15,"font.size":9})
fig,axes=plt.subplots(2,2,figsize=(13,8)); rows=[]
for ax,(an,dd) in zip(axes.flat,ANCH):
    sl=days0[days0>=end-pd.Timedelta(days=dd)] if dd<99999 else days0
    series={"V7 4-sleeve":(v7(sl),"#22d3ee",2.4,"-"),"QQQ":(bh("QQQ",sl),"#a78bfa",1.5,"--"),"SPY":(bh("SPY",sl),"#f59e0b",1.5,"--")}
    for k,(s,c,lw,ls) in series.items(): ax.plot(s.index,s,label=k,color=c,lw=lw,ls=ls)
    a=stat(series["V7 4-sleeve"][0]); aq=stat(series["QQQ"][0])
    ax.set_title(f"{an} 진입 — V7 {a[0]*100:+.1f}% (MDD{a[1]*100:.0f}%·Sh{a[2]:.2f}) vs QQQ {aq[0]*100:+.1f}%",color="#e5e7eb",fontsize=10)
    ax.legend(framealpha=.2,fontsize=8); ax.grid(True); ax.set_ylabel("× (시작=1)")
    rows.append((an,a,aq,stat(series["SPY"][0])))
fig.suptitle("PRAMANA V7 4-sleeve 멀티앵커 (비용후·PAPER) — 분산북: 낙폭↓ Sharpe↑·상승장 누적은 QQQ에 양보",color="#22d3ee",fontsize=13,y=1.00)
fig.tight_layout(); fig.savefig(PNG,dpi=110,bbox_inches="tight",facecolor="#070b16")
b=io.BytesIO(); fig.savefig(b,format="png",dpi=100,bbox_inches="tight",facecolor="#070b16"); ch=base64.b64encode(b.getvalue()).decode(); plt.close(fig)
print("V7 4-sleeve 멀티앵커 (누적%/MDD%/Sharpe):")
for an,a,aq,asp in rows: print(f"  [{an:<14}] V7 {a[0]*100:+6.1f}/{a[1]*100:.0f}/{a[2]:.2f}  QQQ {aq[0]*100:+6.1f}/{aq[1]*100:.0f}/{aq[2]:.2f}  SPY {asp[0]*100:+6.1f}/{asp[1]*100:.0f}/{asp[2]:.2f}")
trows="".join(f"<tr><td>{an}</td><td class=v7>{a[0]*100:+.1f}% / {a[1]*100:.0f}% / {a[2]:.2f}</td><td>{aq[0]*100:+.1f}% / {aq[1]*100:.0f}% / {aq[2]:.2f}</td><td>{asp[0]*100:+.1f}% / {asp[1]*100:.0f}% / {asp[2]:.2f}</td></tr>" for an,a,aq,asp in rows)
html=f"""<!doctype html><html lang=ko><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1"><title>V7 멀티앵커</title>
<style>body{{background:#070b16;color:#e5e7eb;font-family:'Segoe UI',system-ui,sans-serif;margin:0}}.w{{max-width:1080px;margin:0 auto;padding:24px 18px 50px}}
h1{{font-size:1.3em}}img{{width:100%;border-radius:10px;border:1px solid #1e293b}}table{{width:100%;border-collapse:collapse;margin:16px 0;font-size:.92em}}
th,td{{padding:8px 10px;border-bottom:1px solid #1e293b;text-align:right}}th:first-child,td:first-child{{text-align:left;color:#94a3b8}}th{{color:#94a3b8;font-size:.8em}}.v7{{color:#22d3ee;font-weight:700}}
.warn{{background:#1c1408;border:1px solid #92400e;border-radius:10px;padding:12px 15px;color:#fde68a;font-size:.85em;margin-top:14px}}</style></head><body><div class=w>
<h1>🟦 PRAMANA V7 4-sleeve — 멀티앵커 (12/6/3개월·풀)</h1>
<p style='color:#94a3b8'>각 시점 진입 → 현재. 비용후·PAPER. 누적 / MDD / Sharpe.</p>
<img src="data:image/png;base64,{ch}">
<table><tr><th>진입</th><th>V7 4-sleeve</th><th>QQQ</th><th>SPY</th></tr>{trows}</table>
<div class=warn>⚠️ PAPER·NO LIVE·in-sample(forward 판정 아님). V7 4-sleeve = 분산북(알파 아님): MDD/Sharpe는 최선이나 상승장 누적은 QQQ에 양보(=보험료). 크래시 생존 목적함수 선택.</div>
</div></body></html>"""
open(HTML,"w").write(html); print(f"\n✅ PNG: {PNG}\n✅ HTML: {HTML}")
if __name__=="__main__": pass

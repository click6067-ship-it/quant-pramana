#!/usr/bin/env python3
"""PRAMANA V4 — Production 대시보드. Core Beta Forward Book(1.0x) vs SPY vs QQQ, 3개월+풀사이클.
정직: 알파북 아님·베타북. beat/no-beat를 솔직히. 사용자 directive(SPY·QQQ 못넘으면 재정의) 반영.
self-contained HTML. paper. dashboard.py 후속(v4판)."""
import os, sys, io, base64, numpy as np, pandas as pd, json
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import data
CAP=100_000_000; ENG=os.path.join(data.PHASE1A,"outputs","engine")
etf=data.load("SFP_FUNDS",usecols=["ticker","date","closeadj"]).pivot_table(index="date",columns="ticker",values="closeadj").sort_index()
ret=etf.pct_change(); days=etf.index
core=0.5*ret["SPY"]+0.5*ret["QQQ"]
def navwin(s,n):
    d=days[-n:]; return CAP*(1+s.reindex(d).fillna(0)).cumprod()
def stat(s):
    r=s.dropna(); n=CAP*(1+r).cumprod(); yrs=(r.index[-1]-r.index[0]).days/365.25
    tot=n.iloc[-1]/CAP-1; cagr=(1+tot)**(1/yrs)-1 if yrs>0 and tot>-1 else float('nan')
    return tot,cagr,(n/n.cummax()-1).min(),(r.mean()/r.std()*np.sqrt(252) if r.std()>0 else float('nan'))
# 3개월(~63 거래일) + 풀
N=63
w3={k:navwin(v,N) for k,v in {"Core Beta":core,"SPY":ret["SPY"],"QQQ":ret["QQQ"]}.items()}
s3={k:stat(v.reindex(days[-N:]).fillna(0)) for k,v in {"Core Beta":core,"SPY":ret["SPY"],"QQQ":ret["QQQ"]}.items()}
sf={k:stat(v.fillna(0)) for k,v in {"Core Beta":core,"SPY":ret["SPY"],"QQQ":ret["QQQ"]}.items()}
tgt=json.load(open(os.path.join(ENG,"production_target.json"))) if os.path.exists(os.path.join(ENG,"production_target.json")) else {}
mr=open(os.path.join(ENG,"research_meanrev_verdict.txt")).read().strip() if os.path.exists(os.path.join(ENG,"research_meanrev_verdict.txt")) else "n/a"
recon=json.load(open(os.path.join(data.PHASE1A,"outputs","forward","reconcile.json"))) if os.path.exists(os.path.join(data.PHASE1A,"outputs","forward","reconcile.json")) else {}
prod=pd.read_csv(os.path.join(ENG,"production_book.csv")) if os.path.exists(os.path.join(ENG,"production_book.csv")) else None

# beat 판정
c3=s3["Core Beta"][0]; beats_spy=c3>s3["SPY"][0]; beats_qqq=c3>s3["QQQ"][0]
verdict = "SPY·QQQ 둘 다 넘음" if (beats_spy and beats_qqq) else (f"SPY는 넘고 QQQ엔 짐(베타·QQQ틸트)" if beats_spy else "둘 다 못 넘음")
trigger = (beats_spy and beats_qqq)

plt.style.use("dark_background"); plt.rcParams.update({"axes.facecolor":"#0d1326","figure.facecolor":"#0d1326","grid.alpha":.15,"font.size":9})
def png(fig): b=io.BytesIO(); fig.savefig(b,format="png",dpi=95,bbox_inches="tight",facecolor="#0d1326"); plt.close(fig); return base64.b64encode(b.getvalue()).decode()
f=plt.figure(figsize=(10,3.6))
for k,c in [("Core Beta","#22d3ee"),("SPY","#f59e0b"),("QQQ","#a78bfa")]:
    plt.plot(w3[k].index,w3[k]/CAP,label=k,lw=2.2 if k=="Core Beta" else 1.5,color=c,ls=("-" if k=="Core Beta" else "--"))
plt.legend(framealpha=.2); plt.title("3-Month: Core Beta(1.0x) vs SPY vs QQQ",color="#e5e7eb"); plt.ylabel("× ₩100M"); ch=png(f)
C=lambda v:'pos' if v>=0 else 'neg'
scen_rows=""
if prod is not None:
    for _,r in prod[prod.book=="CoreOnly"].iterrows():
        scen_rows+=f"<tr><td>{r.scen}</td><td class=num>{r.lev:.2f}x</td><td class='num'>{r.cagr*100:+.1f}%</td><td class='num neg'>{r.mdd*100:.0f}%</td><td class=num>{r.sharpe:.2f}</td></tr>"
html=f"""<!doctype html><html lang=ko><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>PRAMANA V4 Production</title><style>
body{{background:#070b16;color:#e5e7eb;font-family:'Segoe UI',system-ui,sans-serif;margin:0;line-height:1.55}}
.wrap{{max-width:1040px;margin:0 auto;padding:22px 18px 60px}} h1{{font-size:1.5em}}
.badge{{background:#7f1d1d;color:#fecaca;border-radius:6px;padding:2px 9px;font-size:.72em;font-weight:700;margin-left:6px}}
.b2{{background:#1e3a8a;color:#bfdbfe}} .kpis{{display:flex;flex-wrap:wrap;gap:10px;margin:16px 0}}
.kpi{{flex:1;min-width:120px;background:#0d1326;border:1px solid #1e293b;border-radius:12px;padding:12px 14px}}
.kpi .l{{color:#94a3b8;font-size:.74em;text-transform:uppercase}} .kpi .v{{font-size:1.5em;font-weight:800}}
.card{{background:#0d1326;border:1px solid #1e293b;border-radius:14px;padding:16px;margin:10px 0}} img{{width:100%;border-radius:10px}}
table{{width:100%;border-collapse:collapse;font-size:.9em}} th,td{{padding:6px 9px;border-bottom:1px solid #1e293b;text-align:left}}
th{{color:#94a3b8;font-size:.8em}} td.num{{text-align:right;font-variant-numeric:tabular-nums}} .pos{{color:#34d399}} .neg{{color:#f87171}} .cyan{{color:#22d3ee}}
h2{{font-size:1.12em;border-left:4px solid #22d3ee;padding-left:10px;margin-top:24px}}
.warn{{background:#1c1408;border:1px solid #92400e;border-radius:10px;padding:13px 16px;color:#fde68a;font-size:.88em}}
.ok{{background:#08210f;border:1px solid #166534;color:#86efac}} .muted{{color:#64748b;font-size:.82em}}</style></head><body>
<div class=wrap><h1>🦊 PRAMANA V4 — Production: Core Beta Forward Book<span class=badge>PAPER·NO LIVE</span><span class="badge b2">베타북·알파 아님</span></h1>
<p style='color:#94a3b8'>SPY/QQQ 50/50 (1.0x·PRODUCTION_SAFE 후보) · 정직: 알파 시스템 아님, 시장 베타를 *탄다.* Core&gt;SPY는 QQQ 틸트(레짐)지 스킬 아님.</p>

<div class=kpis>
<div class=kpi><div class=l>3M Core Beta</div><div class="v {C(s3['Core Beta'][0])}">{s3['Core Beta'][0]*100:+.2f}%</div></div>
<div class=kpi><div class=l>3M SPY</div><div class="v {C(s3['SPY'][0])}">{s3['SPY'][0]*100:+.2f}%</div></div>
<div class=kpi><div class=l>3M QQQ</div><div class="v {C(s3['QQQ'][0])}">{s3['QQQ'][0]*100:+.2f}%</div></div>
<div class=kpi><div class=l>3M MDD</div><div class="v neg">{s3['Core Beta'][2]*100:.1f}%</div></div>
<div class=kpi><div class=l>3M Sharpe</div><div class="v">{s3['Core Beta'][3]:+.2f}</div></div>
</div>
<div class=card><img src="data:image/png;base64,{ch}"></div>

<h2>🎯 SPY·QQQ를 넘었나? (네 directive 기준)</h2>
<div class="card {'ok' if trigger else 'warn'}">
<b>판정: {verdict}.</b><br>
3개월 Core Beta {s3['Core Beta'][0]*100:+.2f}% vs SPY {s3['SPY'][0]*100:+.2f}% vs QQQ {s3['QQQ'][0]*100:+.2f}%. 풀사이클 Sharpe Core {sf['Core Beta'][3]:.2f}/SPY {sf['SPY'][3]:.2f}/QQQ {sf['QQQ'][3]:.2f}.<br>
{'✅ 둘 다 넘음 — 유지.' if trigger else '⚠️ <b>둘 다(특히 QQQ)는 못 넘는다 — 설계상 당연(50% QQQ 베타북). 네 directive대로 이건 v5 재정의 트리거다.</b> 넘는 길은 둘뿐: ① 레버(=리스크지 알파 아님·UNSAFE) ② 진짜 알파(미발견·MR 오늘 REJECT). → 가짜 승리 대신 정직히 재정의 회의(Codex)로.'}
</div>

<h2>⚙️ V4는 어떻게 작동하나</h2>
<div class=card><ul>
<li><b>Production = Core Beta Forward Book</b> — SPY/QQQ 50/50, 1.0x. 알파 아니라 *규율 있는 베타.* (Phase 1·1.5: trend+LETF 위성 = 노이즈 → 뺌.)</li>
<li><b>레버는 격리 sleeve</b> — −20/−35/−50% 시나리오는 *PRODUCTION_UNSAFE*(shock-replay+cap 전 자본금지). 레버는 risk cap 아니라 backward knob(Codex).</li>
<li><b>Research OPEN</b> — 자본권한 0으로 알파 후보 탐색(Active 1개). MR thread 1 = <b>REJECT</b>(아래).</li>
<li><b>결정적 risk veto·next-bar·attribution·사람 자본게이트·LLM off-path.</b></li>
</ul></div>

<h2>🛒 현재 타깃 (paper)</h2>
<div class=card><b>Production 기본:</b> SPY 50% / QQQ 50% (1.0x). <span class=muted>as-of {tgt.get('asof','?')} · 추세 ON {len(tgt.get('trend_on',[]))}/15</span>
<table style=margin-top:8px><tr><th>레버 시나리오(격리·UNSAFE)</th><th class=num>레버</th><th class=num>CAGR</th><th class=num>MDD</th><th class=num>Sharpe</th></tr>{scen_rows}</table>
<div class=muted style=margin-top:6px>※ 레버 행은 2016-26 benign 과거 MDD 기준 — forward 낙폭 더 클 수 있음(2008 미포함). shock-stress 전 자본 금지.</div></div>

<h2>🔬 Research 상태</h2>
<div class=card><b>Active thread 1: mean-reversion</b> → <span class=neg>REJECT</span><br>
<span class=muted>{mr}</span><br>
파이프: 등록→스크린→paper sandbox→attribution→OOS/비용후→promotion. 다음 후보: quality 레짐 retest / MR 변형(longer-horizon·no-trade band).</div>

<div class=warn style=margin-top:14px>⚠️ <b>정직 고지:</b> paper·NO LIVE. Core Beta는 *베타북*(SPY/QQQ를 탄다)이지 알파 아님 — QQQ를 못 넘는다. 레버로 "넘기"는 리스크지 엣지 아님. forward reconciliation: {recon.get('note') or ('OK' if recon.get('ok') else '2nd피드 wiring 필요(stooq)')}. 실거래는 12개월 forward+사람 게이트 전 금지.</div>
<div class=muted style=margin-top:10px>데이터 Sharadar(backtest)·생성 production_dashboard.py · 정본 PRAMANA_V4/PRAMANA_V4_LOCK_SHEET_v0.4.md</div>
</div></body></html>"""
out=os.path.join(data.PHASE1A,"outputs","production_dashboard.html"); open(out,"w").write(html)
print(f"✅ 대시보드 → {out} ({os.path.getsize(out)//1024}KB)")
print(f"  3M: Core Beta {s3['Core Beta'][0]*100:+.2f}% · SPY {s3['SPY'][0]*100:+.2f}% · QQQ {s3['QQQ'][0]*100:+.2f}% → {verdict}")
print(f"  beat both = {trigger} → {'유지' if trigger else 'v5 재정의 트리거(directive)'}")

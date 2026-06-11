#!/usr/bin/env python3
"""PRAMANA V5 대시보드 — Aggressive Leveraged Core Beta(용하 선택) vs SPY vs QQQ.
정직: 레버드 베타지 알파 아님. in-sample QQQ 넘음=레버(Sharpe≈QQQ). forward −70%+ 가능. RESEARCH_ONLY.
'이겼나?' 정직 판정 박스. paper. self-contained HTML."""
import os, sys, io, base64, json, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import data
CAP=100_000_000; ENG=os.path.join(data.PHASE1A,"outputs","engine")
etf=data.load("SFP_FUNDS",usecols=["ticker","date","closeadj"]).pivot_table(index="date",columns="ticker",values="closeadj").sort_index()
ret=etf.pct_change()
agg=pd.read_csv(os.path.join(ENG,"aggressive_book_nav.csv"),index_col=0,parse_dates=True).iloc[:,0] if os.path.exists(os.path.join(ENG,"aggressive_book_nav.csv")) else None
ajson=json.load(open(os.path.join(ENG,"aggressive_book.json"))) if os.path.exists(os.path.join(ENG,"aggressive_book.json")) else {}
days=agg.index if agg is not None else etf.index[etf.index>=etf.index[210]]
core=(0.5*ret["SPY"]+0.5*ret["QQQ"]).reindex(days).fillna(0)
def navser(s): return CAP*(1+s).cumprod()
books={"V5 Aggressive":agg if agg is not None else navser(core),
       "Core Beta 1.0x":navser(core),"SPY":navser(ret["SPY"].reindex(days).fillna(0)),"QQQ":navser(ret["QQQ"].reindex(days).fillna(0))}
def stat(s):
    r=s.pct_change().dropna(); yrs=(s.index[-1]-s.index[0]).days/365.25
    tot=s.iloc[-1]/s.iloc[0]-1; cg=(1+tot)**(1/yrs)-1 if yrs>0 and tot>-1 else float('nan')
    return tot,cg,(s/s.cummax()-1).min(),(r.mean()/r.std()*np.sqrt(252) if r.std()>0 else float('nan'))
F={k:stat(v) for k,v in books.items()}
N=63; T3={k:stat(v.iloc[-N:]) for k,v in books.items()}
av=F["V5 Aggressive"]; qq=F["QQQ"]; beat=av[0]>qq[0]
plt.style.use("dark_background"); plt.rcParams.update({"axes.facecolor":"#0d1326","figure.facecolor":"#0d1326","grid.alpha":.15,"font.size":9})
f=plt.figure(figsize=(11,3.8))
for k,c,w in [("V5 Aggressive","#22d3ee",2.4),("QQQ","#a78bfa",1.5),("SPY","#f59e0b",1.4),("Core Beta 1.0x","#64748b",1.1)]:
    plt.plot(books[k].index,books[k]/CAP,label=k,color=c,lw=w,ls=("-" if k=="V5 Aggressive" else "--"))
plt.legend(framealpha=.2); plt.yscale("log"); plt.title(f"Growth of ₩100M (log) — {days[0].date()}→{days[-1].date()}",color="#e5e7eb"); plt.ylabel("× initial")
b=io.BytesIO(); f.savefig(b,format="png",dpi=95,bbox_inches="tight",facecolor="#0d1326"); plt.close(f); ch=base64.b64encode(b.getvalue()).decode()
C=lambda v:'pos' if v>=0 else 'neg'
def row(k):
    return f"<tr><td>{k}</td><td class='num {C(F[k][0])}'>{F[k][0]*100:+.0f}%</td><td class=num>{F[k][1]*100:.1f}%</td><td class='num neg'>{F[k][2]*100:.0f}%</td><td class=num>{F[k][3]:.2f}</td><td class='num {C(T3[k][0])}'>{T3[k][0]*100:+.1f}%</td></tr>"
html=f"""<!doctype html><html lang=ko><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>PRAMANA V5</title><style>
body{{background:#070b16;color:#e5e7eb;font-family:'Segoe UI',system-ui,sans-serif;margin:0;line-height:1.55}}
.wrap{{max-width:1040px;margin:0 auto;padding:22px 18px 60px}} h1{{font-size:1.45em}}
.badge{{background:#7f1d1d;color:#fecaca;border-radius:6px;padding:2px 9px;font-size:.7em;font-weight:700;margin-left:5px}}
.b2{{background:#1e3a8a;color:#bfdbfe}} .kpis{{display:flex;flex-wrap:wrap;gap:10px;margin:14px 0}}
.kpi{{flex:1;min-width:115px;background:#0d1326;border:1px solid #1e293b;border-radius:12px;padding:11px 13px}}
.kpi .l{{color:#94a3b8;font-size:.72em;text-transform:uppercase}} .kpi .v{{font-size:1.4em;font-weight:800}}
.card{{background:#0d1326;border:1px solid #1e293b;border-radius:14px;padding:16px;margin:10px 0}} img{{width:100%;border-radius:10px}}
table{{width:100%;border-collapse:collapse;font-size:.9em}} th,td{{padding:6px 9px;border-bottom:1px solid #1e293b;text-align:left}}
th{{color:#94a3b8;font-size:.78em}} td.num{{text-align:right;font-variant-numeric:tabular-nums}} .pos{{color:#34d399}} .neg{{color:#f87171}}
h2{{font-size:1.1em;border-left:4px solid #22d3ee;padding-left:10px;margin-top:22px}}
.win{{background:#0c2a16;border:1px solid #15803d;color:#86efac}} .warn{{background:#1c1408;border:1px solid #92400e;color:#fde68a}}
.box{{border-radius:10px;padding:14px 16px;font-size:.9em;margin:8px 0}} .muted{{color:#64748b;font-size:.82em}}</style></head><body>
<div class=wrap><h1>🦊 PRAMANA V5 — Aggressive Leveraged Core Beta<span class=badge>PAPER·NO LIVE</span><span class="badge b2">RESEARCH_ONLY</span></h1>
<p style='color:#94a3b8'>용하 선택: 공격적 수익극대화·리스크 수용·유연. vol-target {ajson.get('target_vol_hypothesis','?')}·캡 {ajson.get('paper_max_cap','?')}x·DD ladder·현재 레버 {ajson.get('cur_lever','?')}x. <b>정직: 레버드 베타지 알파 아님.</b></p>

<div class=kpis>
<div class=kpi><div class=l>누적(풀)</div><div class="v {C(av[0])}">{av[0]*100:+.0f}%</div></div>
<div class=kpi><div class=l>CAGR</div><div class="v">{av[1]*100:.1f}%</div></div>
<div class=kpi><div class=l>QQQ 누적</div><div class="v">{qq[0]*100:+.0f}%</div></div>
<div class=kpi><div class=l>MDD</div><div class="v neg">{av[2]*100:.0f}%</div></div>
<div class=kpi><div class=l>Sharpe</div><div class="v">{av[3]:.2f}</div></div>
</div>

<h2>🏁 in-sample raw-return 체크 (forward 판정 아님)</h2>
<div class="box warn">
<b>raw return으로만 PASS · forward 자본 기준(MDD/ulcer/회복/체결/reconcile)은 FAIL/UNKNOWN.</b> {'(in-sample서 QQQ raw 넘김 — 단 아래 ①처럼 레버지 알파 아님)' if beat else '(QQQ 못 넘음)'}
V5 +{av[0]*100:.0f}% vs QQQ +{qq[0]*100:.0f}% vs SPY +{F['SPY'][0]*100:.0f}% · MDD {av[2]*100:.0f}%(QQQ {qq[2]*100:.0f}%).<br><br>
<b>단, 가짜 승리 안 만든다 — 정직히:</b><br>
① <b>알파 아니라 레버다.</b> Sharpe {av[3]:.2f} ≈ QQQ {qq[3]:.2f} → 위험조정 우위 0. 더 번 건 시장노출(레버)을 더 산 것.<br>
② <b>−{abs(av[2]*100):.0f}% MDD는 2016-26 *benign* 조건부.</b> 2000-02 Nasdaq −78%·2008 GFC 미포함. <b>forward tail = −70%+ 가능</b>(레버×크래시).<br>
③ <b>vol-target은 no-ruin floor 아님</b> — 손실*속도* 완화일 뿐, 1일 갭엔 무력(−20%갭@현레버 = 북 −{abs(0.20*float(ajson.get('cur_lever',1.6))*100):.0f}% 즉시).<br>
④ <b>진짜 승패는 12개월 forward.</b> 수익만 좋고 DD/회복 가드레일 깨지면 = FAIL(수익-only 합격 금지).
</div>

<h2>📈 성장 (log)</h2><div class=card><img src="data:image/png;base64,{ch}"></div>

<h2>📊 비교 (풀사이클 + 3M)</h2>
<div class=card><table><tr><th>북</th><th class=num>누적</th><th class=num>CAGR</th><th class=num>MDD</th><th class=num>Sharpe</th><th class=num>3M</th></tr>
{row("V5 Aggressive")}{row("QQQ")}{row("SPY")}{row("Core Beta 1.0x")}</table>
<div class=muted style=margin-top:6px>Core Beta 1.0x = PRODUCTION_SAFE 후보(레버 없는 정직 베타). V5 Aggressive = 그 위 레버 연구레이어.</div></div>

<h2>🔬 상태 & 가드레일</h2>
<div class=card><ul>
<li><b>라벨(Codex):</b> RESEARCH_ONLY / PRODUCTION_UNSAFE. 2.0x = paper max, <b>live cap 1.25~1.5x(crash-pack 통과 후)</b>. target vol = 목표 아니라 tuning hypothesis.</li>
<li><b>가장 중요한 가드레일:</b> 레버 cap은 *crash-loss budget*(1987갭·2000-02·2008·2020·2022 사전등록 pack)로 정한다, CAGR로 정하지 않는다.</li>
<li><b>알파 research-OPEN:</b> MR thread1 = REJECT(turnover 3660%). 다음: quality 레짐 / MR 변형. 알파 찾으면 레버 덜 써도 됨.</li>
<li><b>12mo STOP:</b> forward 가드레일 못 지키면 목표 또 안 바꾸고 "쉬운 알파 없음·Core Beta 1.0x만 production-safe" 수용.</li>
</ul></div>

<div class="box warn">⚠️ <b>정직 고지:</b> paper·NO LIVE. 이건 <b>"crash-loss 줄이려는 procyclical 레버드 베타 *실험*"</b>이지 검증된 수익기계 아님. in-sample 승리는 레버+benign 샘플. 실거래는 crash-pack로 cap 정하고 12개월 forward 가드레일 통과 + 사람 게이트 전 금지.</div>
<div class=muted style=margin-top:10px>데이터 Sharadar · 생성 production_dashboard.py · 정본 PRAMANA_V4/PRAMANA_V5_Problem_Frame_v0.2.md</div>
</div></body></html>"""
out=os.path.join(data.PHASE1A,"outputs","production_dashboard.html"); open(out,"w").write(html)
print(f"✅ v5 대시보드 → {out} ({os.path.getsize(out)//1024}KB)")
print(f"  V5 Aggressive 누적 {av[0]*100:+.0f}% vs QQQ {qq[0]*100:+.0f}% · MDD {av[2]*100:.0f}% · Sharpe {av[3]:.2f} · beat QQQ={beat}")

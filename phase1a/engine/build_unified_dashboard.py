#!/usr/bin/env python3
"""PRAMANA 통합 대시보드 — v1~v7 계보 + A1 라이브를 네비바 한 페이지로. 한글 폰트 적용(kfont).
차트=a1_live/prices.csv 캐시 재사용 / 라이브=a1_live_dashboard.html iframe 임베드.
사용: python engine/build_unified_dashboard.py"""
import os, sys, json, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt; import io, base64
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kfont import set_korean_font; FONT=set_korean_font()
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
PRICES=os.path.join(ROOT,"outputs","a1_live","prices.csv")
if not os.path.exists(PRICES): PRICES=os.path.join(ROOT,"outputs","forward_v7","prices.csv")
STATE=os.path.join(ROOT,"outputs","a1_live","state.json")
OUT=os.path.join(ROOT,"outputs","pramana_unified.html")
CORE_W={"SPY":0.25,"QQQ":0.25,"DBMF":0.25,"GLD":0.15,"IEF":0.10}

GENS=[
 dict(id="v1",ver="v1",name="횡단면 정량 알파",vc="#f87171",verdict="FAIL",
   approach="value·momentum·quality·lowvol + 결합·ridge·GBM·tree (US 공개 일별 cross-sectional)",
   metric="Rank IC ≈ 0 · quality decay 0.22→0.046 · OOS net vs cap-weight 음수",
   one="6 family 전멸 — killer는 메가캡 cap-weight 벽(신호 우열과 무관)"),
 dict(id="v2",ver="v2",name="전략 피벗",vc="#fbbf24",verdict="전환점",
   approach="KR먼저→US · 수익 노브 OPEN · 검증 kill-gate + 리스크 veto LOCKED",
   metric="측정 북보다 *방법론* 재정의 — '검증 먼저, 모델 나중' 순서 잠금",
   one="이후 모든 세대의 토대 — 가짜 알파를 자본 투입 전에 거르는 규율"),
 dict(id="v3",ver="v3",name="풀북 · Trend · 레버",vc="#f87171",verdict="REJECT",
   approach="equity market-neutral + trend + LETF 위성 · VRP short-vol · mean-reversion",
   metric="trend+LETF +0.15%/yr 노이즈 · VRP tail −92% · reversal turnover 3660%",
   one="풀북이 SPY를 어느 horizon도 위험조정으로 못 이김(3x는 레버지 엣지 아님)"),
 dict(id="v4",ver="v4",name="Core Beta 1.0x",vc="#fb923c",verdict="베타 · 알파 아님",
   approach="SPY/QQQ 베타 코어 (core-satellite 재설계의 시작)",
   metric="설계상 QQQ 못 넘음 · overlay −0.14% = 노이즈",
   one="순수 베타북 — 알파가 아니라 시장 노출 그 자체"),
 dict(id="v5",ver="v5",name="Leveraged Core",vc="#fb923c",verdict="레버지 알파 아님",
   approach="vol-target 레버(캡 2.0x) + drawdown ladder",
   metric="in-sample +625% > QQQ +539% · 단 Sharpe 0.95 ≈ QQQ",
   one="in-sample QQQ 넘김 — 그러나 레버일 뿐·같이 낙폭·forward −70% 가능"),
 dict(id="v6",ver="v6",name="Diversified (+DBMF)",vc="#fbbf24",verdict="보험료",
   approach="managed-futures(DBMF) 분산 추가 · 낮은 레버",
   metric="낙폭 완화 ↔ 상승장 수익 양보",
   one="분산으로 MDD 줄이나 bull에서 수익을 보험료로 지불"),
 dict(id="v7",ver="v7",name="4-sleeve 생존코어",vc="#34d399",verdict="채택 (생존코어)",
   approach="Equity 50(SPY/QQQ)+MF 25(DBMF)+Gold 15(GLD)+Bond 10(IEF) · 1.0x",
   metric="Sharpe 1.21 (BEST) · MDD −18% · 풀 +175.8%",
   one="위험효율 최선 — 단 누적은 QQQ의 절반(알파 아닌 분산 프리미엄)"),
]
ANCHOR=[("3개월",5.7,21.6,12.3),("6개월",9.6,17.9,9.4),("12개월",26.3,35.8,24.3),("풀 2019~",175.8,307.7,187.2)]

def b64(fig):
    b=io.BytesIO(); fig.savefig(b,format="png",dpi=95,bbox_inches="tight",facecolor="#0d1326"); plt.close(fig)
    return base64.b64encode(b.getvalue()).decode()
plt.style.use("dark_background"); plt.rcParams.update({"axes.facecolor":"#0d1326","figure.facecolor":"#0d1326","grid.alpha":.15,"font.size":10})

# 차트1 — V7 생존코어 vs QQQ vs SPY 누적 (한글)
ch_cum=""
if os.path.exists(PRICES):
    px=pd.read_csv(PRICES,index_col=0,parse_dates=True)
    if all(t in px.columns for t in CORE_W):
        cret=sum(CORE_W[t]*px[t].pct_change() for t in CORE_W)
        nav=(1+cret.fillna(0)).cumprod(); qqq=(1+px["QQQ"].pct_change().fillna(0)).cumprod(); spy=(1+px["SPY"].pct_change().fillna(0)).cumprod()
        f=plt.figure(figsize=(10.5,3.7))
        plt.plot(nav.index,nav,label="V7 생존코어 (4-sleeve)",lw=2.4,color="#22d3ee")
        plt.plot(qqq.index,qqq,label="QQQ",lw=1.4,color="#a78bfa",ls="--"); plt.plot(spy.index,spy,label="SPY",lw=1.4,color="#f59e0b",ls="--")
        plt.legend(framealpha=.2); plt.title("생존코어(V7) vs 인덱스 — 누적 성장 (×)",color="#e5e7eb"); plt.ylabel("배수(×)")
        ch_cum=b64(f)
# 차트2 — 멀티앵커 그룹 바 (한글·3M/6M/12M)
ch_anc=""
sub=[a for a in ANCHOR if "풀" not in a[0]]
x=np.arange(len(sub)); w=0.26
f=plt.figure(figsize=(10.5,3.4)); ax=plt.gca()
ax.bar(x-w,[a[1] for a in sub],w,label="V7 생존코어",color="#22d3ee")
ax.bar(x,   [a[2] for a in sub],w,label="QQQ",color="#a78bfa")
ax.bar(x+w, [a[3] for a in sub],w,label="SPY",color="#f59e0b")
ax.set_xticks(x); ax.set_xticklabels([a[0] for a in sub]); ax.set_ylabel("누적 수익률 (%)")
ax.legend(framealpha=.2); ax.set_title("진입 시점별 성과 — 12/6/3개월 (%)",color="#e5e7eb")
for i,a in enumerate(sub):
    for dx,v,c in [(-w,a[1],"#22d3ee"),(0,a[2],"#a78bfa"),(w,a[3],"#f59e0b")]:
        ax.text(i+dx,v+0.4,f"{v:.1f}",ha="center",fontsize=7.5,color=c)
ch_anc=b64(f)

state=json.load(open(STATE)) if os.path.exists(STATE) else {}
nav_now=state.get("nav",1e8); tot_now=state.get("total_ret",0); incep=state.get("inception","—")

# 네비 + 섹션 HTML
nav_items=[("overview","📊","개요 · 메타결론","#94a3b8")]+[(g["id"],g["ver"],g["name"],g["vc"]) for g in GENS]+[("live","🔴","A1 Attack (LIVE)","#ef4444"),("anchor","📈","12/6/3 앵커","#a78bfa")]
nav_html="".join(f'<a href="#{i}" class=navlink><span class=dot style="background:{c}"></span><b>{v}</b> {n}</a>' for i,v,n,c in nav_items)
def gen_section(g):
    return f"""<section id="{g['id']}" class=gen>
<div class=genhead><span class=genver style="background:{g['vc']}22;color:{g['vc']};border:1px solid {g['vc']}55">{g['ver']}</span>
<h2>{g['name']} <span class=verdict style="background:{g['vc']}22;color:{g['vc']}">{g['verdict']}</span></h2></div>
<p class=approach><b>접근</b> · {g['approach']}</p>
<div class=metric>📊 {g['metric']}</div>
<p class=one>→ {g['one']}</p></section>"""
gens_html="".join(gen_section(g) for g in GENS)
arows="".join(f'<tr><td>{a[0]}</td><td class=cyan>{a[1]:+.1f}%</td><td class=viol>{a[2]:+.1f}%</td><td class=amber>{a[3]:+.1f}%</td><td class="{"pos" if a[1]-a[2]>=0 else "neg"}">{a[1]-a[2]:+.1f}%p</td></tr>' for a in ANCHOR)

html=f"""<!doctype html><html lang=ko><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>PRAMANA — v1~v7 + A1 통합</title><style>
*{{box-sizing:border-box;margin:0;padding:0}} html{{scroll-behavior:smooth}}
body{{background:#070b16;color:#e5e7eb;font-family:'Segoe UI','Malgun Gothic',system-ui,sans-serif;line-height:1.55;display:flex}}
nav{{width:248px;min-width:248px;height:100vh;position:sticky;top:0;background:#0a0f1f;border-right:1px solid #1e293b;padding:20px 14px;overflow-y:auto}}
nav .brand{{font-size:1.25em;font-weight:800;letter-spacing:-.5px;padding:0 6px 4px}} nav .sub{{color:#64748b;font-size:.7em;padding:0 6px 14px;display:block}}
.navlink{{display:flex;align-items:center;gap:8px;color:#cbd5e1;text-decoration:none;font-size:.82em;padding:8px 9px;border-radius:8px;margin-bottom:2px}}
.navlink:hover{{background:#13203b;color:#fff}} .dot{{width:9px;height:9px;border-radius:50%;flex-shrink:0}}
main{{flex:1;max-width:1000px;padding:26px 30px 80px}} h1{{font-size:1.7em;letter-spacing:-.5px}}
.meta{{background:#13203b;border:1px solid #1e3a5f;border-left:4px solid #16a34a;border-radius:10px;padding:15px 18px;margin:16px 0;font-size:.92em}} .meta b{{color:#86efac}}
section{{scroll-margin-top:18px;margin:14px 0;padding:16px 18px;background:#0d1326;border:1px solid #1e293b;border-radius:14px}}
.card{{background:#0d1326;border:1px solid #1e293b;border-radius:14px;padding:14px;margin:12px 0}} img{{width:100%;border-radius:8px}}
h2{{font-size:1.12em}} .genhead{{display:flex;align-items:center;gap:10px;margin-bottom:8px}}
.genver{{font-weight:800;font-size:.8em;padding:3px 10px;border-radius:7px}} .verdict{{font-size:.6em;font-weight:700;padding:2px 9px;border-radius:20px;vertical-align:middle}}
.approach{{color:#cbd5e1;font-size:.88em;margin:4px 0}} .metric{{background:#0a1322;border-radius:8px;padding:8px 12px;font-size:.85em;color:#93c5fd;margin:8px 0}}
.one{{color:#fbbf24;font-size:.9em;font-style:italic}} h3{{font-size:1.05em;border-left:3px solid #ef4444;padding-left:9px;margin:24px 0 8px}}
table{{width:100%;border-collapse:collapse;font-size:.85em}} th{{background:#111a30;color:#94a3b8;text-align:left;padding:7px 9px}} td{{padding:6px 9px;border-top:1px solid #1a2540}}
.cyan{{color:#22d3ee}}.viol{{color:#a78bfa}}.amber{{color:#f59e0b}}.pos{{color:#34d399}}.neg{{color:#f87171}}
.live-frame{{width:100%;height:1500px;border:0;border-radius:12px;background:#070b16}}
.badge{{font-size:.5em;font-weight:700;padding:3px 9px;border-radius:20px;vertical-align:middle}} .b-paper{{background:#1e3a8a;color:#bfdbfe}} .b-live{{background:#7f1d1d;color:#fca5a5}}</style></head>
<body>
<nav><span class=brand>PRAMANA</span><span class=sub>solo+AI equity validation OS · 한 페이지 통합</span>{nav_html}</nav>
<main>
<h1>PRAMANA — 계보 v1~v7 + A1 Attack <span class="badge b-paper">PAPER</span></h1>
<section id=overview><div class=meta>📌 <b>메타 결론</b> — 솔로가 공개 데이터로 SPY/QQQ를 <b>위험조정 초과하는 '사는' 알파</b>는 8세대 검증으로 거의 없음(robust negative · efficient market·SPIVA 79%·GKX 정합). <b>건진 것: V7 생존코어 · 나쁜-공시 회피 필터 · 가짜-알파 면역.</b> 프로젝트는 종료가 아니라 위험을 정직하게 인정한 공격형 <b>A1 Attack Book</b>으로 재정의되어 가상 ₩1억으로 라이브 가동 중.</div>
<div class=card><img src="data:image/png;base64,{ch_cum}" alt="누적 성장"></div></section>
{gens_html}
<h3 id=live>🔴 A1 Attack Book — 라이브 (가상 ₩1억) <span class="badge b-live">LIVE</span></h3>
<section style="padding:10px"><p style="color:#94a3b8;font-size:.85em;margin:4px 6px 10px">인셉션 {incep} · 현재 NAV ₩{nav_now/1e8:.3f}억 ({tot_now*100:+.2f}%) · 아래는 실시간 라이브 대시보드(1시간 자동 새로고침) 임베드:</p>
<iframe class=live-frame src="a1_live_dashboard.html"></iframe>
<p style="color:#64748b;font-size:.75em;margin-top:8px">↑ 안 보이면 <a href="a1_live_dashboard.html" style="color:#60a5fa">새 탭에서 열기</a></p></section>
<h3 id=anchor>📈 진입 시점별 성과 (12/6/3개월 · 풀)</h3>
<section><div class=card><img src="data:image/png;base64,{ch_anc}" alt="멀티앵커"></div>
<table><tr><th>진입</th><th>V7 생존코어</th><th>QQQ</th><th>SPY</th><th>V7 − QQQ</th></tr>{arows}</table>
<p class=one style="margin-top:10px">→ V7은 모든 구간에서 누적을 QQQ에 양보하는 대신 MDD를 절반으로·Sharpe를 개선. 알파(초과수익)가 아니라 위험효율(분산 프리미엄).</p></section>
<p style="color:#475569;font-size:.72em;margin-top:30px;text-align:center">PRAMANA · PAPER only, no live capital · 한글 폰트={os.path.basename(FONT) if FONT else 'default'} · 정본 PRAMANA_Final_Report_for_Submission.docx</p>
</main></body></html>"""
open(OUT,"w").write(html)
print(f"✅ 통합 대시보드: {OUT}  (한글폰트={FONT})")
if __name__=="__main__": pass

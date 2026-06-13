#!/usr/bin/env python3
"""PRAMANA 통합 대시보드 — v1~v7 진화 서사(각 버전 12/6/3 수치 → 냉정한 진단 → 다음 버전 개선) + A1 라이브.
각 세대: 성과 수치 + 🔍진단(결함) + →개선(다음 버전이 고친 점). 한글 폰트(kfont)·라이브 iframe.
데이터: 백테스트 primary=Sharadar(유료 PIT) / 이 비교차트=ETF EOD(yfinance·구조 시각화) / 라이브=Sharadar+fallback.
사용: python engine/build_unified_dashboard.py"""
import os, sys, json, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt; import io, base64
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kfont import set_korean_font; FONT=set_korean_font()
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
CACHE=os.path.join(ROOT,"outputs","a1_live","prices.csv")
STATE=os.path.join(ROOT,"outputs","a1_live","state.json")
OUT=os.path.join(ROOT,"outputs","pramana_unified.html")

# ── 데이터 (ETF EOD·구조 비교 시각화용) ──
def get_px():
    try:  # Sharadar(유료·PIT) 우선 — ETF=SFP closeadj
        import nasdaqdatalink as ndl
        ndl.ApiConfig.api_key=open(os.path.join(ROOT,".ndl_key")).read().strip()
        d=ndl.get_table("SHARADAR/SFP",ticker=["SPY","QQQ","DBMF","GLD","IEF"],paginate=True)
        if len(d):
            px=d.pivot(index="date",columns="ticker",values="closeadj").sort_index(); px.index=pd.to_datetime(px.index)
            if px.shape[1]>=4: return px.dropna()
    except Exception: pass
    try:
        import yfinance as yf  # fallback
        df=yf.download(["SPY","QQQ","DBMF","GLD","IEF"],period="2500d",auto_adjust=True,progress=False)
        c=df["Close"] if isinstance(df.columns,pd.MultiIndex) else df
        c=c.dropna()
        if len(c)>200: return c
    except Exception: pass
    return pd.read_csv(CACHE,index_col=0,parse_dates=True).dropna()
px=get_px()

# ── core-satellite 4세대 = 구조 프록시 (정직: v5/v6은 실제 vol-target/동적의 *정적 근사*) ──
BOOKS={"v4":({"SPY":.5,"QQQ":.5},1.0),
       "v5":({"SPY":.5,"QQQ":.5},1.6),
       "v6":({"SPY":.35,"QQQ":.35,"DBMF":.15,"GLD":.075,"IEF":.075},1.0),
       "v7":({"SPY":.25,"QQQ":.25,"DBMF":.25,"GLD":.15,"IEF":.10},1.0)}
def anchors(w,lev=1.0):
    r=(sum(w[t]*px[t].pct_change() for t in w if t in px.columns)*lev).dropna()
    o={}
    for lbl,n in [("3M",63),("6M",126),("12M",252),("풀",len(r))]:
        rr=r.iloc[-min(n,len(r)):]; nav=(1+rr).cumprod()
        cum=(nav.iloc[-1]-1)*100; mdd=(nav/nav.cummax()-1).min()*100; sh=(rr.mean()/rr.std()*np.sqrt(252)) if rr.std()>0 else 0
        o[lbl]=(cum,mdd,sh)
    return o
RES={bk:anchors(w,lev) for bk,(w,lev) in BOOKS.items()}
QQQ=anchors({"QQQ":1.0}); SPY=anchors({"SPY":1.0})

# ── 진화 서사: 각 세대 = 수치 + 진단 + 개선 ──
GENS=[
 dict(id="v1",ver="v1",name="횡단면 정량 알파",vc="#f87171",verdict="FAIL",book=None,
   approach="value·momentum·quality·lowvol + 결합·ridge·GBM·tree (Sharadar PIT·비용후·OOS)",
   metric="Rank IC ≈ 0 · quality decay 0.22→0.046 · OOS net vs cap-weight 음수 · ML도 선형 못 넘음(GKX 0.4%)",
   diag="신호 자체가 cap-weight 인덱스를 못 넘는다. 메가캡 지배 레짐에서 횡단면 틸트는 *신호 우열과 무관하게* 초대형주를 덜 담아 구조적으로 진다.",
   improve="v3 — 횡단면을 접고, 자산배분형 풀북(trend·레버·VRP)으로 절대수익을 노린다."),
 dict(id="v2",ver="v2",name="검증 프레임 피벗",vc="#fbbf24",verdict="전환점",book=None,
   approach="'데이터→비용→검증→그 다음 모델' 순서 잠금 · kill-gate + 리스크 veto LOCKED",
   metric="측정 북이 아니라 *방법론* — 사전등록·OOS·비용후·적대검수(Codex)·look-ahead 차단",
   diag="이 단계엔 '수익 북'이 없다. 대신 가짜 알파를 자본 투입 전에 거르는 규율을 세웠다.",
   improve="이후 모든 세대(v3~v7·A1)가 이 게이트를 통과해야만 살아남게 된다 — 무한루프 차단의 토대."),
 dict(id="v3",ver="v3",name="풀북 · Trend · 레버",vc="#f87171",verdict="REJECT",book=None,
   approach="equity market-neutral + trend + LETF 위성 · VRP short-vol · mean-reversion",
   metric="trend+LETF 기여 +0.15%/yr = 노이즈 · VRP tail −92% · reversal turnover 3660% · 풀북 Sharpe < SPY",
   diag="풀북이 SPY를 어느 horizon에서도 위험조정으로 못 이긴다. 3x 누적은 알파가 아니라 레버리지일 뿐(같이 −45% 낙폭).",
   improve="v4 — 잡다한 위성을 버리고 core-satellite로 구조를 재설계(SPY/QQQ 베타 코어부터)."),
 dict(id="v4",ver="v4",name="Core Beta 1.0x",vc="#fb923c",verdict="베타·알파 아님",book="v4",
   approach="SPY/QQQ 50:50 베타 코어 (core-satellite의 출발점)",
   metric=None,
   diag="순수 시장 베타다. 누적·위험조정 모두 QQQ에 진다(설계상 당연) — 절대수익이 부족하다.",
   improve="v5 — 부족한 절대수익을 레버리지로 끌어올려 본다."),
 dict(id="v5",ver="v5",name="Leveraged Core",vc="#fb923c",verdict="레버지 알파 아님",book="v5",
   approach="베타 코어 × 레버(실제 vol-target 캡 2.0x + DD ladder · 여기 차트는 ~1.6x 정적 근사)",
   metric=None,
   diag="누적은 QQQ를 넘지만 MDD·변동성도 같이 커져 Sharpe는 QQQ와 동급(≈0.95). 레버일 뿐 알파가 아니고, forward에서 −70% 꼬리 위험.",
   improve="v6 — 레버로 위험을 키우는 대신, 분산(managed-futures)으로 위험을 줄이는 방향으로 전환."),
 dict(id="v6",ver="v6",name="Diversified (+DBMF)",vc="#fbbf24",verdict="보험료",book="v6",
   approach="베타 + managed-futures(DBMF)·Gold·Bond 분산 · 낮은 레버",
   metric=None,
   diag="DBMF·Gold 분산으로 낙폭은 줄였으나, 상승장 수익을 '보험료'로 지불한다(bull에서 QQQ에 더 벌어짐).",
   improve="v7 — 분산 비중을 4-sleeve로 정교화해 위험효율(Sharpe)을 최대화."),
 dict(id="v7",ver="v7",name="4-sleeve 분산코어",vc="#34d399",verdict="backtest 생존 후보 · paper",book="v7",
   approach="Equity 50(SPY/QQQ)+MF 25(DBMF)+Gold 15(GLD)+Bond 10(IEF) · 1.0x",
   metric=None,
   diag="Sharpe 최선·MDD 최소로 '위험효율'은 이긴다. 그러나 누적은 QQQ의 절반 — 이건 분산 프리미엄이지 알파가 아니다.",
   improve="A1 — 코어(v7)는 생존용으로 고정하고, 초과수익은 별도 Attack·Moonshot sleeve로 분리(공격을 코어에서 격리)."),
]

def b64(fig):
    b=io.BytesIO(); fig.savefig(b,format="png",dpi=95,bbox_inches="tight",facecolor="#0d1326"); plt.close(fig)
    return base64.b64encode(b.getvalue()).decode()
plt.style.use("dark_background"); plt.rcParams.update({"axes.facecolor":"#0d1326","figure.facecolor":"#0d1326","grid.alpha":.15,"font.size":10})
COL={"v4":"#94a3b8","v5":"#fb923c","v6":"#fbbf24","v7":"#22d3ee"}
# 차트1 — 누적 진화 (v4~v7 + QQQ + SPY)
f=plt.figure(figsize=(10.5,3.8))
for bk,(w,lev) in BOOKS.items():
    r=(sum(w[t]*px[t].pct_change() for t in w if t in px.columns)*lev).dropna(); nav=(1+r).cumprod()
    plt.plot(nav.index,nav,label=f"{bk} {dict((g['id'],g['name']) for g in GENS)[bk]}",lw=2.4 if bk=="v7" else 1.5,color=COL[bk])
for t,c in [("QQQ","#a78bfa"),("SPY","#f59e0b")]:
    nav=(1+px[t].pct_change().fillna(0)).cumprod(); plt.plot(nav.index,nav,label=t,lw=1.3,color=c,ls="--")
plt.legend(framealpha=.2,fontsize=8); plt.title("core-satellite 진화 v4→v7 — IN-SAMPLE 구조 비교만 (실적/forward 아님 · ×)",color="#e5e7eb"); plt.ylabel("배수(×)")
ch_cum=b64(f)
# 차트2 — 12/6/3 그룹 바 (v4~v7 + QQQ)
labels=["3M","6M","12M"]; x=np.arange(3); series=[("v4",COL["v4"]),("v5",COL["v5"]),("v6",COL["v6"]),("v7",COL["v7"]),("QQQ","#a78bfa")]
w=0.16; f=plt.figure(figsize=(10.5,3.5)); ax=plt.gca()
for i,(name,c) in enumerate(series):
    vals=[(RES[name] if name in RES else QQQ)[l][0] for l in labels]
    ax.bar(x+(i-2)*w,vals,w,label=name,color=c)
ax.set_xticks(x); ax.set_xticklabels(["3개월","6개월","12개월"]); ax.set_ylabel("누적 수익률 (%)")
ax.legend(framealpha=.2,fontsize=8,ncol=5); ax.set_title("진입 시점별 성과 — 12/6/3개월 (%)",color="#e5e7eb")
ch_anc=b64(f)

state=json.load(open(STATE)) if os.path.exists(STATE) else {}
nav_now=state.get("nav",1e8); tot_now=state.get("total_ret",0); incep=state.get("inception","—")

nav_items=[("overview","📊","개요 · 메타결론","#94a3b8")]+[(g["id"],g["ver"],g["name"],g["vc"]) for g in GENS]+[("live","📝","A1 (paper forward·자본0)","#ef4444"),("anchor","📈","12/6/3 비교","#a78bfa")]
nav_html="".join(f'<a href="#{i}" class=navlink><span class=dot style="background:{c}"></span><b>{v}</b> {n}</a>' for i,v,n,c in nav_items)
def anchor_block(bk):
    a=RES[bk]
    rows=""
    for l,kl in [("3M","3개월"),("6M","6개월"),("12M","12개월"),("풀","풀기간")]:
        cum,mdd,sh=a[l]; vq=cum-QQQ[l][0]
        rows+=f'<tr><td>{kl}</td><td class="{"pos" if cum>=0 else "neg"}">{cum:+.1f}%</td><td class=neg>{mdd:.0f}%</td><td>{sh:.2f}</td><td class="{"pos" if vq>=0 else "neg"}">{vq:+.1f}%p</td></tr>'
    return f'<table class=mini><tr><th>진입</th><th>누적</th><th>MDD</th><th>Sharpe</th><th>vs QQQ</th></tr>{rows}</table>'
def gen_section(g):
    body=anchor_block(g["book"]) if g["book"] else (f'<div class=metric>📊 {g["metric"]}</div>' if g["metric"] else "")
    extra=f'<div class=metric style="margin-top:8px">📊 {g["metric"]}</div>' if (g["book"] and g["metric"]) else ""
    return f"""<section id="{g['id']}" class=gen>
<div class=genhead><span class=genver style="background:{g['vc']}22;color:{g['vc']};border:1px solid {g['vc']}55">{g['ver']}</span>
<h2>{g['name']} <span class=verdict style="background:{g['vc']}22;color:{g['vc']}">{g['verdict']}</span></h2></div>
<p class=approach><b>접근</b> · {g['approach']}</p>
{body}{extra}
<div class=diag><span class=tag style="background:#7f1d1d;color:#fca5a5">🔍 냉정한 진단</span> {g['diag']}</div>
<div class=improve><span class=tag style="background:#064e3b;color:#6ee7b7">→ 다음 버전 개선</span> {g['improve']}</div></section>"""
gens_html="".join(gen_section(g) for g in GENS)
arows=""
for l,kl in [("3M","3개월"),("6M","6개월"),("12M","12개월"),("풀","풀기간")]:
    arows+=f'<tr><td>{kl}</td><td class=cyan>{RES["v7"][l][0]:+.1f}%</td><td class=viol>{QQQ[l][0]:+.1f}%</td><td class=amber>{SPY[l][0]:+.1f}%</td><td class="{"pos" if RES["v7"][l][0]-QQQ[l][0]>=0 else "neg"}">{RES["v7"][l][0]-QQQ[l][0]:+.1f}%p</td></tr>'

html=f"""<!doctype html><html lang=ko><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>PRAMANA — v1~v7 진화 + A1</title><style>
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
.approach{{color:#cbd5e1;font-size:.86em;margin:4px 0 8px}} .metric{{background:#0a1322;border-radius:8px;padding:8px 12px;font-size:.82em;color:#93c5fd}}
.diag,.improve{{font-size:.86em;margin-top:8px;padding:8px 11px;border-radius:8px;line-height:1.5}} .diag{{background:#1a0e0e}} .improve{{background:#0a1f17}}
.tag{{font-size:.82em;font-weight:700;padding:2px 8px;border-radius:6px;margin-right:7px}}
table{{width:100%;border-collapse:collapse;font-size:.84em}} table.mini{{margin:6px 0}} th{{background:#111a30;color:#94a3b8;text-align:left;padding:6px 9px}} td{{padding:5px 9px;border-top:1px solid #1a2540}}
.cyan{{color:#22d3ee}}.viol{{color:#a78bfa}}.amber{{color:#f59e0b}}.pos{{color:#34d399}}.neg{{color:#f87171}}
h3{{font-size:1.05em;border-left:3px solid #ef4444;padding-left:9px;margin:24px 0 8px}}
.live-frame{{width:100%;height:1500px;border:0;border-radius:12px;background:#070b16}}
.badge{{font-size:.5em;font-weight:700;padding:3px 9px;border-radius:20px;vertical-align:middle}} .b-paper{{background:#1e3a8a;color:#bfdbfe}} .b-live{{background:#7f1d1d;color:#fca5a5}}
@media(max-width:760px){{body{{display:block}} nav{{width:100%;min-width:0;height:auto;position:static;border-right:0;border-bottom:1px solid #1e293b;padding:12px;display:flex;flex-wrap:wrap;gap:4px;align-items:center}} nav .brand{{width:100%}} nav .sub{{width:100%}} .navlink{{font-size:.76em;padding:6px 8px}} main{{padding:16px 14px 60px;max-width:100%}} h1{{font-size:1.3em}} .live-frame{{height:900px}}}}</style></head>
<body>
<nav><span class=brand>PRAMANA</span><span class=sub>solo+AI equity validation OS · v1~v7 진화 + A1 라이브</span>{nav_html}</nav>
<main>
<h1>PRAMANA — 계보 v1~v7 진화 + A1 Attack <span class="badge b-paper">PAPER</span></h1>
<section id=overview><div class=meta>📌 <b>메타 결론</b> — 솔로가 <b>유료 기관급 데이터(Sharadar · survivorship-free · PIT)</b> + 무료 보조(EDGAR 8-K · yfinance)로 검증했는데도, <b>이 데이터·비용·기간(2016–2026)에서</b> SPY/QQQ를 위험조정 초과하는 '사는' 알파는 8개 전략 family로 <b>미발견(scope-conditional negative · 보편 주장 아님)</b>. 유료 PIT로도 없다는 점이 결론을 강화한다. 건진 것: V7 <b>backtest 생존 후보</b> · 나쁜-공시 회피 필터 · 가짜-알파 면역. → 위험을 정직하게 인정한 공격형 <b>A1 Attack Book</b>(paper · 자본권한 0)으로 재정의.</div>
<div class=meta style="border-left-color:#7c3aed;background:#160f24;font-size:.84em"><b>🧾 Evidence Ledger (정직성)</b> — look-ahead 적발·수정 <b>2건</b>(RVOL · 동적 allocator) · DSR/PBO <b>TODO(미산출)</b> · 2-feed reconciliation <b>UNKNOWN</b> · crash-pack(닷컴/2008) <b>proxy·미실시</b> · <b>Live capital = 0</b> · cron 미검증(수동). 모든 수치 = backtest/paper · 실자본 아님. <b>base-rate</b>: SPIVA 2025 액티브 대형주 ~79% 인덱스 미달(시장적으로 어려운 문제) · 전체 원장·council·health = <a href="https://github.com/click6067-ship-it/quant-pramana/tree/main/docs/context" style="color:#a78bfa">repo</a>.</div>
<div class=card><img src="data:image/png;base64,{ch_cum}" alt="누적 진화"></div>
<p style="color:#64748b;font-size:.76em">↑ v4~v7 = core-satellite 구조 진화(ETF EOD). v5/v6은 실제 vol-target·동적 분산의 <i>정적 근사</i> — 정확한 in-sample은 보고서 참조.</p></section>
{gens_html}
<h3 id=live>📝 A1 Attack Book — paper forward (가상 ₩1억 · 실자본 0) <span class="badge b-live">NO CAPITAL</span></h3>
<section style="padding:10px"><p style="color:#94a3b8;font-size:.82em;margin:4px 6px 10px"><b>상태 구분</b> — Backfill {incep}~2026-06-11 · <b>Live forward 2026-06-12~</b> · <b>실자본 0 (broker·order 없음)</b> · Paper NAV ₩{nav_now/1e8:.3f}억({tot_now*100:+.2f}%)=시뮬. 아래 임베드:</p>
<iframe class=live-frame src="a1_live_dashboard.html"></iframe>
<p style="color:#64748b;font-size:.75em;margin-top:8px">↑ 안 보이면 <a href="a1_live_dashboard.html" style="color:#60a5fa">새 탭에서 열기</a></p></section>
<h3 id=anchor>📈 12/6/3 비교 — V7 backtest 후보 vs 인덱스 (in-sample)</h3>
<section><div class=card><img src="data:image/png;base64,{ch_anc}" alt="멀티앵커"></div>
<table><tr><th>진입</th><th>V7 (backtest)</th><th>QQQ</th><th>SPY</th><th>V7 − QQQ</th></tr>{arows}</table>
<p class=diag style="margin-top:10px"><span class=tag style="background:#7f1d1d;color:#fca5a5">🔍 진단</span> V7은 모든 구간에서 누적을 QQQ에 양보하는 대신 MDD를 절반으로·Sharpe를 개선 — 알파(초과수익)가 아니라 위험효율(분산 프리미엄)이다.</p></section>
<p style="color:#475569;font-size:.72em;margin-top:30px;text-align:center">데이터: 백테스트 primary=<b>Sharadar(유료·PIT)</b> · 이 비교차트=ETF EOD(yfinance·구조 시각화) · 라이브=Sharadar+fallback · catalyst=EDGAR 8-K(무료) · 한글폰트={os.path.basename(FONT) if FONT else 'default'}</p>
</main></body></html>"""
open(OUT,"w").write(html)
print(f"✅ 통합 대시보드(진화서사): {OUT}")
print(f"   v4~v7 풀: " + " · ".join(f"{bk} {RES[bk]['풀'][0]:+.0f}%/Sh{RES[bk]['풀'][2]:.2f}" for bk in BOOKS) + f" | QQQ {QQQ['풀'][0]:+.0f}% SPY {SPY['풀'][0]:+.0f}%")
if __name__=="__main__": pass

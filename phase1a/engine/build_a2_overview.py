#!/usr/bin/env python3
"""PRAMANA A2 종합 시각화 — 오늘 구축한 것 한눈에. 3북·Phase 0~C·War Plan·Vault·동적 REJECT·scanner·Codex 검증.
읽기: state.json들·war_plan.json·vault.json·attack_candidates.csv. 정적 HTML + a2 차트 iframe. python engine/build_a2_overview.py"""
import os, json, pandas as pd
sys=__import__("sys"); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kfont import set_korean_font; set_korean_font()
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt; import io, base64, numpy as np
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE); OUT=os.path.join(ROOT,"outputs","a2_overview.html")
def lj(p):
    try: return json.load(open(p))
    except: return {}
A2=os.path.join(ROOT,"outputs","a2_live"); A1=os.path.join(ROOT,"outputs","a1_live"); V7=os.path.join(ROOT,"outputs","forward_v7")
a2=lj(os.path.join(A2,"state.json")); a1=lj(os.path.join(A1,"state.json")); v7=lj(os.path.join(V7,"state.json"))
war=lj(os.path.join(A2,"war_plan.json")); vault=lj(os.path.join(A2,"positions","vault.json"))
try: cands=pd.read_csv(os.path.join(A2,"attack_candidates.csv"))
except: cands=pd.DataFrame()
# blind/PIT backtest verdict (Attack/Moonshot 과거검증)
DECD=os.path.join(ROOT,"outputs","a2_decisions")
bb_sm=lj(os.path.join(DECD,"blind_backtest_summary_smallmid.json")); bb_sp=lj(os.path.join(DECD,"blind_backtest_summary_sp500.json"))
def bb_row(bb,lbl):
    if not bb: return f'<tr><td>{lbl}</td><td colspan=4 style="color:#64748b">미실행</td></tr>'
    a=bb.get("attack",{}); h=a.get("by_horizon",{}).get("5",{}) or a.get("by_horizon",{}).get(5,{})
    v=bb.get("attack_verdict","?")
    return (f'<tr><td>{lbl}</td><td>{a.get("n_candidates","?"):,}건</td>'
            f'<td class="{"pos" if h.get("excess_qqq_mean",0)>0 else "neg"}">{h.get("excess_qqq_mean",0)*100:+.2f}%</td>'
            f'<td class=neg>{h.get("excess_qqq_median",0)*100:+.2f}%</td>'
            f'<td class=neg>{h.get("win_rate_excess_qqq",0)*100:.0f}%</td><td style="color:#f87171;font-weight:700">{v}</td></tr>')
def pct(x): return f"{x*100:+.1f}%" if isinstance(x,(int,float)) else "—"
def chart():
    p=os.path.join(A2,"prices.csv")
    if not os.path.exists(p): return ""
    px=pd.read_csv(p,index_col=0,parse_dates=True).dropna()
    if not all(c in px.columns for c in ["QQQ","TQQQ","SPY"]): return ""
    qr=px["QQQ"].pct_change().fillna(0); tr=px["TQQQ"].pct_change().fillna(0); CAP=1e8
    w=lambda s: CAP*s/s.iloc[0]
    S={"A2-T(고정35/35)":w((1+0.35*qr+0.35*tr).cumprod()),"A2-Q(QQQ55)":w((1+0.55*qr).cumprod()),
       "QQQ":w((1+qr).cumprod()),"SPY":w((1+px["SPY"].pct_change().fillna(0)).cumprod()),"TQQQ":w((1+tr).cumprod())}
    plt.style.use("dark_background"); plt.rcParams.update({"axes.facecolor":"#0d1326","figure.facecolor":"#0d1326","grid.alpha":.15,"font.size":9})
    f=plt.figure(figsize=(10.5,3.9)); C={"A2-T(고정35/35)":"#22d3ee","A2-Q(QQQ55)":"#34d399","QQQ":"#a78bfa","SPY":"#f59e0b","TQQQ":"#ec4899"}
    for k in ["TQQQ","QQQ","SPY","A2-Q(QQQ55)","A2-T(고정35/35)"]:
        plt.plot(S[k].index,S[k]/1e8,label=k,lw=2.5 if "A2-T" in k else 1.3,color=C[k],ls="-" if "A2" in k else "--")
    inc=lj(os.path.join(A2,"state.json")).get("inception")
    if inc:
        try: plt.axvline(pd.Timestamp(inc),color="#64748b",ls=":",lw=1); plt.text(pd.Timestamp(inc),plt.ylim()[1]*0.9,"라이브 시작",color="#94a3b8",fontsize=7)
        except: pass
    plt.legend(framealpha=.2,fontsize=8); plt.title("A2(동적OFF 고정) vs QQQ·SPY·TQQQ — 계좌금액(₩1억·첫거래일 기준·백테스트 2016~·강세장 편향)",color="#e5e7eb"); plt.ylabel("계좌금액(억원)")
    b=io.BytesIO(); f.savefig(b,format="png",dpi=95,bbox_inches="tight",facecolor="#0d1326"); plt.close(f); return base64.b64encode(b.getvalue()).decode()

phases=[("0 무결성","next-bar·live/backtest·to_won·capital accounting","✅"),
        ("A Vault ledger","forward vault.json·노출차감·Hard70/Reload30·주1회/월10%","✅"),
        ("B 연료","Attack/Moonshot ledger·token·draft board·thesis·NEG Gate 차등","✅"),
        ("B+ Blind backtest","feature/event store(PIT)·Attack daily proxy·Moonshot event·decision log","✅"),
        ("C1 War Plan","상태판정(LLM=GYR만)·rule 게이트","✅"),
        ("C3 Attack scanner","분봉 ORB/VWAP/RVOL/Bollinger·등급·NEG=EDGAR 연결완료","✅"),
        ("C4 분봉 provider","yfinance PROXY·Polygon/Alpaca stub","✅"),
        ("C2 Mapping","동적 OFF라 불필요(게이트=War Plan)","⏭️"),
        ("Delta","TQ-DH·benchmark panel·dynamic vault/sell engine","✅"),
        ("D 통합·미니PC","이 종합 대시보드·cron 8 jobs·미니PC 배포","✅")]
codex=[("1차 STOP","look-ahead·live/backtest 혼동·Vault 장식·beta toy","수정 ✅"),
       ("2차 STOP","close-to-close 미묘 same-close·Vault forward·동적 ablation","수정 ✅"),
       ("동적 allocator","ablation 동적기여 −113%p (고정<동적)","REJECT(benign 한정)")]
prow="".join(f'<tr><td class=ph>{p}</td><td>{d}</td><td style="text-align:center;font-size:1.1em">{s}</td></tr>' for p,d,s in phases)
crow="".join(f'<tr><td>{a}</td><td>{b}</td><td class=fix>{c}</td></tr>' for a,b,c in codex)
warrow=""
if war:
    for k,lbl in [("market_state","Market"),("leadership_state","Leadership"),("tqqq_permission","TQQQ"),("attack_permission","Attack"),("moonshot_permission","Moonshot"),("vault_state","Vault")]:
        v=war.get(k,"—"); col="#34d399" if v in("GREEN","ADD_OK","FULL","OPEN","RELOAD_ALLOWED") else ("#f87171" if v in("RED","BAN_ADD","LOCKED") else "#fbbf24")
        warrow+=f'<tr><td>{lbl}</td><td style="color:{col};font-weight:700">{v}</td></tr>'
crows=""
if len(cands):
    for _,r in cands.head(8).iterrows():
        crows+=f'<tr><td>{r["ticker"]}</td><td>{r.get("grade","?")}</td><td>{r.get("rvol","?")}</td><td>{"위" if r.get("vwap_above") else "아래"}</td><td>{"O" if r.get("orb_break") else "X"}</td><td>{r.get("blocked","")[:30]}</td></tr>'
else: crows='<tr><td colspan=6 style="text-align:center;color:#64748b">후보 없음(Leadership RED→Attack LOCKED·정상)</td></tr>'

ch=chart()
html=f"""<!doctype html><html lang=ko><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>PRAMANA A2 종합</title><style>
*{{box-sizing:border-box;margin:0;padding:0}} body{{background:#070b16;color:#e5e7eb;font-family:'Segoe UI','Malgun Gothic',system-ui,sans-serif;line-height:1.55}}
.wrap{{max-width:1040px;margin:0 auto;padding:24px 20px 70px}} h1{{font-size:1.5em;letter-spacing:-.5px}}
h2{{font-size:1.05em;border-left:4px solid #22d3ee;padding-left:10px;margin:22px 0 10px}}
.cards{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:14px 0}}
.card{{background:#0d1326;border:1px solid #1e293b;border-radius:14px;padding:15px}} .card .t{{color:#94a3b8;font-size:.75em}} .card .v{{font-size:1.5em;font-weight:800;margin:4px 0}}
.card .s{{font-size:.78em;color:#94a3b8}} .pos{{color:#34d399}} .neg{{color:#f87171}}
table{{width:100%;border-collapse:collapse;font-size:.84em;background:#0d1326;border-radius:10px;overflow:hidden}}
th{{background:#111a30;color:#94a3b8;text-align:left;padding:7px 10px}} td{{padding:6px 10px;border-top:1px solid #1a2540}} .ph{{color:#60a5fa;font-weight:700}} .fix{{color:#34d399}}
.banner{{background:#1a0e0e;border:1px solid #7f1d1d;border-radius:12px;padding:14px 18px;margin:12px 0;font-size:.92em}} .banner b{{color:#fca5a5}}
.meta{{background:#13203b;border:1px solid #1e3a5f;border-left:4px solid #16a34a;border-radius:10px;padding:14px 18px;margin:12px 0;font-size:.9em}} .meta b{{color:#86efac}}
iframe{{width:100%;height:1450px;border:0;border-radius:12px;background:#070b16}} a{{color:#60a5fa}}
.two{{display:grid;grid-template-columns:1fr 1fr;gap:14px}} @media(max-width:720px){{.cards,.two{{grid-template-columns:1fr}}}}</style></head><body>
<div class=wrap>
<h1>PRAMANA A2 — Convex Raider 종합 <span style="font-size:.5em;background:#5b21b6;color:#ddd6fe;padding:3px 9px;border-radius:20px">HYBRID·PAPER·₩1억</span></h1>
<div class=meta>📌 v1~v7(검증된 알파 없음) → <b>A2 Convex Raider</b>: 고정 QQQ35/TQQQ35 레버베타 + Attack/Moonshot 비대칭 + forward Vault. <b>동적 마켓타이밍은 데이터로 REJECT(−113%p)</b>. Codex 2회 STOP까지 정직 검증. 검증된 알파 ❌ / 위험 정직 인정 공격 paper book ⭕.</div>

<h2>📊 라이브 3북 (cron 6 jobs·Sharadar)</h2>
<div class=cards>
<div class=card><div class=t>V7 생존코어</div><div class="v">{pct(v7.get('total_ret'))}</div><div class=s>4-sleeve 분산·mode {v7.get('mode','—')}</div></div>
<div class=card><div class=t>A1 Catalyst(레버없이)</div><div class="v">{pct(a1.get('total_ret'))}</div><div class=s>Core40+Attack/Moon/Cash</div></div>
<div class=card><div class=t>A2-T 백테스트(2016~)</div><div class="v {'pos' if a2.get('a2t_ret',0)>=0 else 'neg'}">{pct(a2.get('a2t_ret'))}</div><div class=s>vs QQQ {pct(a2.get('qqq_ret'))}·mode {a2.get('mode','—')}·Lead {a2.get('lead','—')}</div></div>
</div>

<div class=two>
<div><h2>🧱 Phase 0~D 진행</h2><table><tr><th>Phase</th><th>내용</th><th>상태</th></tr>{prow}</table></div>
<div><h2>🚦 오늘의 War Plan</h2><table><tr><th>항목</th><th>상태</th></tr>{warrow or '<tr><td colspan=2 style="color:#64748b">war_plan.json 생성 대기</td></tr>'}</table>
<h2>💰 forward Vault</h2><table><tr><td>Hard</td><td>₩{vault.get('hard',0)*1:.4f} (비중)</td></tr><tr><td>Reload</td><td>₩{vault.get('reload',0):.4f}</td></tr><tr><td>live excess HWM</td><td>{vault.get('hwm',0)*100:.2f}%p</td></tr><tr><td>이동</td><td>{len(vault.get('events',[]))}건(forward 초기·정상)</td></tr></table></div>
</div>

<div class=banner>🔴 <b>동적 allocator = REJECT</b> — dynamic ablation 동적기여 <b>−113%p</b>(고정 35/35 &gt; 동적). 마켓타이밍 또 패배(v7 4전4패·Codex #5 일치). 단 "이 구현·2016~ benign·무비용" 한정·"동적 일반 사망" 확장 ❌. → A2는 고정 + Attack/Moonshot이 차별점.</div>

<h2>🧪 Attack/Moonshot Blind/PIT Backtest <span style="color:#64748b;font-size:.7em">(과거검증·next-bar·decision log·검증된 알파 아님)</span></h2>
<div class=meta style="border-left-color:#f59e0b">📌 Attack/Moonshot은 forward 빈 슬롯이 아니라 <b>feature store(available_at)·event store(EDGAR 34,381건 PIT)·blind backtest(60,136 decisions)</b>로 과거 검증됨. 결과 = <b>Attack DEAD(두 유니버스)·Moonshot edge 없음</b>(평균 양수는 우측꼬리 lottery·중앙값 음수·승률&lt;50%) = 8세대 결론과 일관. <b>가짜 알파를 또 걸러낸 것(시스템 정상)</b>. 상세 <a href="../phase1a/reports/A2_attack_moonshot_blind_backtest.md">리포트</a>.</div>
<table><tr><th>Attack Stage-A (h5·cost 20bp)</th><th>후보</th><th>excess vs QQQ (mean)</th><th>excess (median)</th><th>win(ex)</th><th>판정</th></tr>
{bb_row(bb_sm,"smallmid (gap proxy·next-close)")}
{bb_row(bb_sp,"sp500 (진짜 open-gap·next-open)")}</table>
<h2>⚔️ Attack scanner (분봉·PROXY·매수 X·forward watch)</h2>
<table><tr><th>티커</th><th>등급</th><th>RVOL</th><th>VWAP</th><th>ORB</th><th>blocked</th></tr>{crows}</table>

<h2>🔬 Codex 적대 검증 (2회 STOP → 전부 수정)</h2>
<table><tr><th>검수</th><th>지적</th><th>처리</th></tr>{crow}</table>

<h2>📈 A2 라이브 차트 (백테스트 vs 라이브·sleeve)</h2>
<img src="data:image/png;base64,{ch}" style="width:100%;border-radius:12px">
<p style="color:#64748b;font-size:.8em;margin-top:8px">↑ 안 보이면 <a href="a2_live_dashboard.html">새 탭</a> · 다른 북: <a href="pramana_unified.html">통합(v1~v7+A1)</a> · <a href="v7_forward_dashboard.html">V7</a> · <a href="a1_live_dashboard.html">A1</a></p>
<p style="color:#475569;font-size:.72em;margin-top:14px;text-align:center">PRAMANA A2 · PAPER only·자본권한 0 · 동적 OFF·고정 35/35 + Attack/Moonshot + forward Vault · 미니PC 배포(deploy_minipc.sh)가 마지막</p>
</div></body></html>"""
open(OUT,"w").write(html)
print(f"✅ A2 종합 시각화: {OUT}")
if __name__=="__main__": pass

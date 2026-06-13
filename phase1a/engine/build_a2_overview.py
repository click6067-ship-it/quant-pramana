#!/usr/bin/env python3
"""PRAMANA A2 종합 시각화 — 오늘 구축한 것 한눈에. 3북·Phase 0~C·War Plan·Vault·동적 REJECT·scanner·Codex 검증.
읽기: state.json들·war_plan.json·vault.json·attack_candidates.csv. 정적 HTML + a2 차트 iframe. python engine/build_a2_overview.py"""
import os, json, pandas as pd
sys=__import__("sys"); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kfont import set_korean_font; set_korean_font()
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE); OUT=os.path.join(ROOT,"outputs","a2_overview.html")
def lj(p):
    try: return json.load(open(p))
    except: return {}
A2=os.path.join(ROOT,"outputs","a2_live"); A1=os.path.join(ROOT,"outputs","a1_live"); V7=os.path.join(ROOT,"outputs","forward_v7")
a2=lj(os.path.join(A2,"state.json")); a1=lj(os.path.join(A1,"state.json")); v7=lj(os.path.join(V7,"state.json"))
war=lj(os.path.join(A2,"war_plan.json")); vault=lj(os.path.join(A2,"positions","vault.json"))
try: cands=pd.read_csv(os.path.join(A2,"attack_candidates.csv"))
except: cands=pd.DataFrame()
def pct(x): return f"{x*100:+.1f}%" if isinstance(x,(int,float)) else "—"

phases=[("0 무결성","next-bar·live/backtest·to_won·capital accounting","✅"),
        ("A Vault ledger","forward vault.json·노출차감·Hard70/Reload30·주1회/월10%","✅"),
        ("B 연료","Attack/Moonshot ledger·#4 sleeve 회계·Graveyard 판정·NEG Gate 차등","✅"),
        ("C1 War Plan","상태판정(LLM=GYR만)·rule 게이트","✅"),
        ("C3 Attack scanner","분봉 ORB/VWAP/RVOL/Bollinger·등급·NEG","✅"),
        ("C4 분봉 provider","yfinance PROXY·Polygon/Alpaca stub","✅"),
        ("C2 Mapping","동적 OFF라 불필요(게이트=War Plan)","⏭️"),
        ("D 통합·미니PC","이 종합 대시보드·미니PC 배포(마지막)","🔨")]
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

<h2>⚔️ Attack scanner (분봉·PROXY·매수 X·forward watch)</h2>
<table><tr><th>티커</th><th>등급</th><th>RVOL</th><th>VWAP</th><th>ORB</th><th>blocked</th></tr>{crows}</table>

<h2>🔬 Codex 적대 검증 (2회 STOP → 전부 수정)</h2>
<table><tr><th>검수</th><th>지적</th><th>처리</th></tr>{crow}</table>

<h2>📈 A2 라이브 차트 (백테스트 vs 라이브·sleeve)</h2>
<iframe src="a2_live_dashboard.html"></iframe>
<p style="color:#64748b;font-size:.8em;margin-top:8px">↑ 안 보이면 <a href="a2_live_dashboard.html">새 탭</a> · 다른 북: <a href="pramana_unified.html">통합(v1~v7+A1)</a> · <a href="v7_forward_dashboard.html">V7</a> · <a href="a1_live_dashboard.html">A1</a></p>
<p style="color:#475569;font-size:.72em;margin-top:14px;text-align:center">PRAMANA A2 · PAPER only·자본권한 0 · 동적 OFF·고정 35/35 + Attack/Moonshot + forward Vault · 미니PC 배포(deploy_minipc.sh)가 마지막</p>
</div></body></html>"""
open(OUT,"w").write(html)
print(f"✅ A2 종합 시각화: {OUT}")
if __name__=="__main__": pass

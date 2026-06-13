#!/usr/bin/env python3
"""PRAMANA 종합 라이브 대시보드 — 한 페이지 HTML. 8세대 연대기·멀티앵커·A1 구조·건진 자산.
교수/외부 공유용 정적 요약 + forward 라이브(v7_forward_dashboard.html) 링크. python engine/build_dashboard.py"""
import os
HERE=os.path.dirname(os.path.abspath(__file__)); REPO=os.path.dirname(os.path.dirname(HERE))
OUT=os.path.join(REPO,"phase1a","outputs","pramana_dashboard.html")
os.makedirs(os.path.dirname(OUT),exist_ok=True)
GEN=[("v1","단순 횡단면 팩터 (value/mom/quality/lowvol)","FAIL","Rank IC ≈ 0"),
("v1","결합·ridge·GBM·tree","FAIL","OOS net vs cap-weight 음수"),
("v3","trend+LETF·VRP·reversal","REJECT","노이즈·tail −92%·turnover 3660%"),
("V4–V6","Core Beta·레버드·분산","알파 아님","V5 Sharpe≈QQQ (레버지 알파 아님)"),
("V7","4-sleeve 분산 코어","생존코어 ✓","Sharpe 1.21·MDD −18%"),
("V8","Levered 4-sleeve","REJECT","닷컴 proxy −49%"),
("MT","마켓타이밍 4종","4전 4패","후행신호 벽"),
("Alpha","intraday ORB/VWAP/RVOL","DEAD","look-ahead·강세장 베타"),
("Alpha","8-K POS catalyst / NEG 회피","POS FAIL / NEG ✓","사는 알파 ✗ / 피하는 필터 ✓")]
ANCHOR=[("3개월","+4.6%","−5%","1.41","+20.2%","+11.1%"),("6개월","+8.4%","−7%","1.29","+14.9%","+7.7%"),
("12개월","+26.5%","−7%","2.13","+35.3%","+24.1%"),("풀 2019~","+174.9%","−18%","1.21","+305%","+186%")]
SLEEVE=[("Base Core","40","#2563eb","V7 / SPY·QQQ · 생존"),("Attack","30","#dc2626","catalyst momentum·event"),
("Moonshot","15","#d97706","고위험 비대칭 베팅"),("Cash","15","#475569","버퍼·기회")]
def gcolor(v): return "#16a34a" if "✓" in v else ("#dc2626" if v in("FAIL","DEAD","REJECT") else "#d97706")
rows="".join(f'<tr><td class=g>{g}</td><td>{h}</td><td style="color:{gcolor(v)};font-weight:700">{v}</td><td class=ev>{e}</td></tr>' for g,h,v,e in GEN)
arows="".join(f'<tr><td class=g>{a}</td><td class=pos>{b}</td><td class=neg>{c}</td><td>{d}</td><td>{e}</td><td>{f}</td></tr>' for a,b,c,d,e,f in ANCHOR)
seg="".join(f'<div style="width:{w}%;background:{c}" title="{lbl} {w}%"></div>' for lbl,w,c,d in SLEEVE)
leg="".join(f'<div class=lg><span class=dot style="background:{c}"></span><b>{lbl} {w}%</b> · {d}</div>' for lbl,w,c,d in SLEEVE)
html=f"""<!doctype html><html lang=ko><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>PRAMANA · Solo+AI Equity Validation OS</title><style>
*{{box-sizing:border-box;margin:0;padding:0}}body{{font-family:-apple-system,'Segoe UI',Roboto,'Malgun Gothic',sans-serif;background:#0b1020;color:#e2e8f0;line-height:1.55;padding:0 0 60px}}
.wrap{{max-width:1000px;margin:0 auto;padding:0 20px}}header{{background:linear-gradient(135deg,#1e293b,#0f172a);padding:38px 20px;border-bottom:1px solid #334155;margin-bottom:28px}}
h1{{font-size:30px;letter-spacing:-.5px}}h1 small{{display:block;font-size:14px;color:#94a3b8;font-weight:400;margin-top:6px}}
.meta{{background:#13203b;border:1px solid #1e3a5f;border-left:4px solid #16a34a;border-radius:10px;padding:16px 20px;margin:22px 0;font-size:14.5px}}
.meta b{{color:#86efac}}h2{{font-size:18px;margin:30px 0 12px;color:#cbd5e1;border-left:3px solid #2563eb;padding-left:10px}}
table{{width:100%;border-collapse:collapse;font-size:13px;background:#0f172a;border-radius:8px;overflow:hidden}}
th{{background:#1e293b;color:#94a3b8;text-align:left;padding:9px 11px;font-weight:600}}td{{padding:8px 11px;border-top:1px solid #1e293b}}
.g{{color:#60a5fa;font-weight:700;white-space:nowrap}}.ev{{color:#94a3b8;font-size:12px}}.pos{{color:#4ade80}}.neg{{color:#f87171}}
.bar{{display:flex;height:34px;border-radius:8px;overflow:hidden;margin:14px 0}}.bar div{{transition:.2s}}
.lg{{font-size:13px;margin:5px 0;color:#cbd5e1}}.dot{{display:inline-block;width:11px;height:11px;border-radius:3px;margin-right:7px;vertical-align:middle}}
.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:14px;margin:14px 0}}
.card{{background:#0f172a;border:1px solid #1e293b;border-radius:10px;padding:16px}}.card h3{{font-size:14px;color:#86efac;margin-bottom:6px}}.card p{{font-size:12.5px;color:#94a3b8}}
.tag{{display:inline-block;background:#1e3a5f;color:#93c5fd;font-size:11px;padding:2px 9px;border-radius:20px;margin-right:6px}}
.live{{display:inline-block;margin-top:8px;background:#16a34a;color:#fff;padding:8px 16px;border-radius:8px;text-decoration:none;font-size:13px;font-weight:600}}
.foot{{margin-top:30px;font-size:11.5px;color:#64748b;text-align:center}}</style></head><body>
<header><div class=wrap><h1>PRAMANA <small>Solo + AI 체계적 주식 검증 운영체계 · PAPER only / NO LIVE · 2026-06-13</small></h1>
<div style="margin-top:10px"><span class=tag>가상자본 ₩100M</span><span class=tag>US equity/ETF</span><span class=tag>사전등록·OOS·적대검수</span><span class=tag>자본권한 0</span></div></div></header>
<div class=wrap>
<div class=meta>📌 <b>메타 결론</b> — 솔로가 공개 데이터로 SPY/QQQ를 <b>위험조정 초과하는 '사는' 알파</b>는 8세대 검증으로 거의 없음(robust negative · efficient market·SPIVA 79%·GKX와 정합). <b>건진 것: V7 생존코어 · 나쁜-공시 회피 필터 · 가짜-알파 면역.</b></div>

<h2>① 실험 연대기 — 8세대 (무엇이 죽었나)</h2>
<table><tr><th>세대</th><th>접근</th><th>판정</th><th>근거</th></tr>{rows}</table>

<h2>② 멀티앵커 성과 — V7 생존코어 vs 인덱스 (비용후)</h2>
<table><tr><th>진입</th><th>V7 수익</th><th>V7 MDD</th><th>V7 Sharpe</th><th>QQQ</th><th>SPY</th></tr>{arows}</table>
<p style="font-size:12px;color:#94a3b8;margin-top:8px">→ V7은 누적을 양보하는 대신 MDD 절반·Sharpe 개선. <b>알파(초과수익)가 아니라 위험효율(분산 프리미엄)</b> — 최대복리 목적이면 인덱스 우월.</p>

<h2>③ 최종 형태 — PRAMANA A1 Catalyst Confirmed Attack Book</h2>
<div class=bar>{seg}</div>{leg}
<p style="font-size:12.5px;color:#94a3b8;margin-top:10px">레버 ETF 없이 이벤트·정성 catalyst·비대칭 베팅으로 QQQ 초과 <i>시도</i>. <b style="color:#fbbf24">검증된 알파 아님 · 위험을 정직하게 인정한 공격 베팅</b> · 나쁜공시 회피 필수 · catalyst=총알 / ORB·VWAP·RVOL=방아쇠.</p>

<h2>④ 건진 자산 (8세대의 산출물)</h2>
<div class=cards>
<div class=card><h3>V7 생존 코어</h3><p>4-sleeve 분산 · Sharpe 1.21 · MDD −18% · 완전 파산 방지</p></div>
<div class=card><h3>나쁜-공시 회피 필터</h3><p>8세대 중 유일한 일관 신호(−0.75%) · 사는 알파 아닌 지뢰 제거</p></div>
<div class=card><h3>가짜-알파 면역</h3><p>가짜 알파를 자본 투입 전 paper로 제거 · 무한루프 차단</p></div>
<div class=card><h3>재사용 검증 OS</h3><p>PIT 벤치(corr 0.998) · trial registry · DSR/PBO · data gate</p></div>
</div>

<a class=live href="v7_forward_dashboard.html">▶ V7 paper forward 대시보드 (live-ready · cron 미검증 · 수동/예약 갱신)</a>

<div class=foot>PRAMANA · solo+AI equity validation OS · PAPER only, no live capital · 정본: PRAMANA_Final_Report_for_Submission.docx · PRAMANA_A1_Attack_Book_Final.md</div>
</div></body></html>"""
with open(OUT,"w") as f: f.write(html)
print("✅ 종합 대시보드:",OUT)
if __name__=="__main__": pass

#!/usr/bin/env python3
"""PRAMANA A2 — Layer 7 Unified Dashboard (SSOT v2 §12). 모든 A2 상태 한눈에.

읽기(defensive·없으면 N/A): book_state·risk_dashboard·war_plan·allocator_state·drawdown_state·
  tqqq_module·qqq_module·vault.json·attack/moonshot positions·attack_candidates·tq_dh_signals.
SSOT §12 §4 필수 항목 전부 표시 + §12 §7 경고 배너 상단 고정. 정적 HTML. PAPER·자본권한 0.
실행: python engine/a2_dashboard.py (모든 모듈 다음·마지막).
"""
import os, sys, json, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
A2 = os.path.join(ROOT, "outputs", "a2_live"); POS = os.path.join(A2, "positions")
OUT = os.path.join(ROOT, "outputs", "a2_live_dashboard.html")


def lj(p, d=None):
    try: return json.load(open(p))
    except Exception: return d if d is not None else {}


def pc(x, suf="%", mul=100, dec=1):
    try: return f"{x*mul:+.{dec}f}{suf}"
    except Exception: return "N/A"


def main():
    book = lj(os.path.join(A2, "book_state.json")); risk = lj(os.path.join(A2, "risk_dashboard.json"))
    war = lj(os.path.join(A2, "war_plan.json")); vault = lj(os.path.join(POS, "vault.json"))
    tqm = lj(os.path.join(A2, "tqqq_module.json")); qm = lj(os.path.join(A2, "qqq_module.json"))
    alloc = lj(os.path.join(A2, "allocator_state.json")); ddown = lj(os.path.join(A2, "drawdown_state.json"))
    toks = lj(os.path.join(POS, "attack_tokens.json")); attack = lj(os.path.join(POS, "attack.json"), [])
    moon = lj(os.path.join(POS, "moonshot.json"), [])
    attack = attack if isinstance(attack, list) else attack.get("positions", [])
    moon_pos = moon if isinstance(moon, list) else moon.get("positions", [])
    moon_draft = (moon.get("draft_board", []) if isinstance(moon, dict) else [])
    today = book.get("as_of") or risk.get("as_of") or str(dt.date.today())
    # tq-dh latest dip
    dip = "N/A"
    try:
        import pandas as pd
        f = os.path.join(A2, "tq_dh_signals.csv")
        if os.path.exists(f):
            d = pd.read_csv(f); dip = str(d.iloc[-1].get("dip_type", "N/A")) if len(d) else "N/A"
    except Exception: pass
    # attack candidates count by grade
    ac = {"A": 0, "B": 0, "C": 0}
    try:
        import pandas as pd
        f = os.path.join(A2, "attack_candidates.csv")
        if os.path.exists(f):
            d = pd.read_csv(f)
            for g in ("A", "B", "C"): ac[g] = int((d.get("grade") == g).sum()) if "grade" in d else 0
    except Exception: pass

    cc = {"GREEN": "#34d399", "YELLOW": "#fbbf24", "RED": "#f87171"}
    def badge(s): return f'<span style="color:{cc.get(s,"#94a3b8")};font-weight:700">{s}</span>'
    vaulted = book.get("vaulted_profit_real")
    rows_bench = [("A2-Beta", book.get("A2Beta_ret")), ("naive 35/35", book.get("naive_ret")),
                  ("QQQ", book.get("qqq_ret")), ("TQQQ", book.get("tqqq_ret"))]
    bench_html = "".join(f"<tr><td>{k}</td><td>{pc(v,dec=0)}</td></tr>" for k, v in rows_bench)

    html = f"""<!doctype html><html lang=ko><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<meta http-equiv=refresh content=3600><title>PRAMANA A2 Dashboard</title><style>
body{{background:#070b16;color:#e5e7eb;font-family:'Segoe UI','Malgun Gothic',system-ui;margin:0;line-height:1.5}}
.wrap{{max-width:1080px;margin:0 auto;padding:20px 16px 60px}} h1{{font-size:1.3em}} h2{{font-size:.98em;border-left:4px solid #22d3ee;padding-left:9px;margin:16px 0 8px}}
.banner{{background:#1a0e0e;border:1px solid #7f1d1d;border-radius:10px;padding:11px 15px;margin:10px 0;color:#fca5a5;font-size:.86em;font-weight:600}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:9px;margin:10px 0}}
.card{{background:#0d1326;border:1px solid #1e293b;border-radius:12px;padding:11px 13px}} .card .l{{color:#94a3b8;font-size:.66em}} .card .v{{font-size:1.1em;font-weight:800;margin-top:3px}}
table{{width:100%;border-collapse:collapse;font-size:.82em;background:#0d1326;border-radius:10px;overflow:hidden}} th{{background:#111a30;color:#94a3b8;text-align:left;padding:6px 9px}} td{{padding:5px 9px;border-top:1px solid #1a2540}}
.two{{display:grid;grid-template-columns:1fr 1fr;gap:12px}} @media(max-width:760px){{.two{{grid-template-columns:1fr}}}} .grn{{color:#34d399}} .red{{color:#f87171}} .amb{{color:#fbbf24}}</style></head><body>
<div class=wrap>
<h1>🟣 PRAMANA A2 Dashboard <span style="font-size:.5em;background:#5b21b6;color:#ddd6fe;padding:3px 9px;border-radius:20px">PAPER·₩1억·{today}</span></h1>
<div class=banner>⚠️ A2 is NOT verified alpha. A2 is a high-risk QQQ/TQQQ convex book with paper-only Attack/Moonshot optionality. TQQQ=Booster(레버 베타·알파 아님)·자본권한 0·NO LIVE.</div>

<h2>📊 NAV / Benchmarks (백테스트 2016~·A2-Beta=real Vault 차감)</h2>
<div class=grid>
<div class=card><div class=l>A2-Beta NAV</div><div class="v grn">{pc(book.get('A2Beta_ret'),dec=0)}</div></div>
<div class=card><div class=l>Vault-adjusted = active(이미 차감)</div><div class="v">{pc(book.get('A2Beta_ret'),dec=0)}</div></div>
<div class=card><div class=l>naive 35/35</div><div class="v amb">{pc(book.get('naive_ret'),dec=0)}</div></div>
<div class=card><div class=l>QQQ</div><div class="v">{pc(book.get('qqq_ret'),dec=0)}</div></div>
<div class=card><div class=l>A2-Beta MDD</div><div class="v">{pc(book.get('A2Beta_mdd'),dec=0)}</div></div>
<div class=card><div class=l>Vaulted Profit(실제)</div><div class="v grn">{pc(vaulted,dec=1)}</div></div>
<div class=card><div class=l>beat QQQ / naive</div><div class="v">{'✅' if book.get('beat_qqq') else '❌'} / {'✅' if book.get('beat_naive') else '❌'}</div></div>
</div>
<div class=two>
<div><h2>🚦 Risk Dashboard (L2)</h2><table>
<tr><td>Leadership</td><td>{badge(risk.get('leadership_state','N/A'))} ({risk.get('leadership_score','?')}/77)</td></tr>
<tr><td>Market Stress</td><td>{badge(risk.get('market_stress','N/A'))}</td></tr>
<tr><td>TQQQ Decay</td><td>{'🔴 ZONE' if risk.get('tqqq_decay') else '🟢 OK'}</td></tr>
<tr><td>Booster Rent</td><td>{'🔴 inefficient' if risk.get('booster_rent') else '🟢 OK'} (mult {risk.get('tqqq_realized_multiple','?')})</td></tr>
<tr><td>Effective Beta</td><td>{risk.get('effective_beta','?')}x</td></tr>
<tr><td>QQQ &gt;20/50/200dma</td><td>{'/'.join('Y' if risk.get(k) else 'N' for k in ('qqq_above_ma20','qqq_above_ma50','qqq_above_ma200'))}</td></tr>
<tr><td>Mode</td><td>{ddown.get('mode') or (alloc.get('mode') if isinstance(alloc,dict) else 'base')}</td></tr>
<tr><td>Crash/Attack Lockout</td><td>{'🔴 CRASH' if ddown.get('crash_lockout') else ('🟡 Attack-lock' if ddown.get('attack_lockout') else '🟢 none')}</td></tr>
</table></div>
<div><h2>💰 Vault (실제 차감·표시용 아님)</h2><table>
<tr><td>Hard (영구잠금)</td><td>{pc(vault.get('hard'),dec=2)}</td></tr>
<tr><td>Reload (재배치)</td><td>{pc(vault.get('reload'),dec=2)}</td></tr>
<tr><td>excess HWM</td><td>{pc(vault.get('hwm'),dec=2)}</td></tr>
<tr><td>Vault events</td><td>{len(vault.get('events',[]))}건</td></tr>
<tr><td>Vault state</td><td>{war.get('vault_state','N/A')}</td></tr>
</table>
<h2>⚖️ Allocator (mapping·next-bar·5%p)</h2><table>
<tr><td>mode</td><td>{alloc.get('mode','N/A') if isinstance(alloc,dict) else 'N/A'}</td></tr>
<tr><td>target weights</td><td style="font-size:.85em">{json.dumps(alloc.get('target') or alloc.get('target_weights') or {}, ensure_ascii=False)[:120] if isinstance(alloc,dict) else 'N/A'}</td></tr>
</table></div>
</div>

<h2>⚔️ Attack / 🚀 Moonshot (A2-Full·live paper ledger optionality)</h2>
<div class=two>
<div><table>
<tr><th>Attack</th><th></th></tr>
<tr><td>tokens(주간)</td><td>{toks.get('available','?') if isinstance(toks,dict) else '?'}</td></tr>
<tr><td>open positions</td><td>{len(attack)}건</td></tr>
<tr><td>candidates A/B/C</td><td>{ac['A']}/{ac['B']}/{ac['C']}</td></tr>
<tr><td>permission</td><td>{war.get('attack_permission','N/A')}</td></tr>
<tr><td>NEG flags(leaders)</td><td>{', '.join(risk.get('neg_leaders',[])) or '없음'}</td></tr>
</table></div>
<div><table>
<tr><th>Moonshot</th><th></th></tr>
<tr><td>open thesis</td><td>{len(moon_pos)}건</td></tr>
<tr><td>draft board</td><td>{len(moon_draft)}후보</td></tr>
<tr><td>permission</td><td>{war.get('moonshot_permission','N/A')}</td></tr>
<tr><td>TQ-DH dip type</td><td>{dip}</td></tr>
</table></div></div>
<p style="color:#fbbf24;font-size:.82em;margin-top:8px">⚠️ Attack/Moonshot = 과거 백테스트로 증명 X(EDGAR catalyst 방향 알파 DEAD)·실시간 기회 ledger·optionality. 빈슬롯=cash.</p>

<h2>📋 오늘의 War Plan</h2>
<div class=card style="font-size:.85em"><b>금지:</b> {' · '.join(war.get('forbidden_actions_today',[])) or '없음'}<br>
<b>Top Attack:</b> {', '.join(war.get('top_attack_candidates',[])) or '없음'} · <b>Top risks:</b> {', '.join(war.get('top_risks',[])) or '없음'}<br>
<b>사람 확인:</b> {' · '.join(war.get('human_review_required',[]))}</div>

<p style="color:#475569;font-size:.72em;margin-top:14px;text-align:center">PRAMANA A2 v2 (SSOT) · PAPER·자본권한 0 · TQQQ=Booster(레버 베타) · Vault 실제 차감 · LLM=상태만·비중=mapping engine · 다른 뷰: <a href="a2_book_dashboard.html" style="color:#60a5fa">A2 Book</a> · <a href="a2_overview.html" style="color:#60a5fa">Overview</a></p>
</div></body></html>"""
    open(OUT, "w").write(html)
    print(f"✅ A2 Dashboard {today} → {OUT} (Leadership {risk.get('leadership_state','N/A')}·mode {ddown.get('mode','base')}·Vaulted {pc(vaulted,dec=1)}·Attack cand A{ac['A']}/B{ac['B']})")


if __name__ == "__main__":
    main()

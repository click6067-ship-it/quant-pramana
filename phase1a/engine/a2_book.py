#!/usr/bin/env python3
"""PRAMANA A2 — Accountable Book (A2-Beta / A2-Full · 진짜 회계·Vault 실제 차감).

용하 지시(2026-06-14): "새 공격 백테스트가 아니라 A2를 진짜 회계 가능한 book으로 고치기.
Vault가 실제 돈처럼 빠지고, Attack/Moonshot이 별도 ledger로 들어오고, A2-Beta/A2-Full 분리."
정본 council/2026-06-14_aggressive-pivot · 05_DYNAMIC_SELL_AND_VAULT_TIMING.md.

본체 = TQQQ Booster(레버 베타·알파 아님) + Vault(수익 회수·실제 차감) + Risk gate.
  A2-Beta = QQQ/TQQQ/Vault 만 (검증된 엔진·먼저 완성).
  A2-Full = A2-Beta + Attack/Moonshot **live paper ledger**(과거 백테스트로 증명 X·실시간 기회 ledger·optionality).
★ Vault 실제 차감: Vault In = exposure(QQQ/TQQQ)에서 빼서 locked cash로(Hard 영구·Reload 재배치). 그래서 낙폭에 잠긴 수익 보존 = Vaulted Profit 진짜.
회계 불변식: NAV == qqq + tqqq + attack + moon + vault_hard + vault_reload + cash (매일 assert).
판단(spec): QQQ뿐 아니라 **naive beta book도 이기는가** + Vaulted Profit 실제 누적 + 게임 지속(MDD).
PAPER·자본권한 0·검증된 알파 아님. 사용: python engine/a2_book.py
"""
import os, sys, json, datetime as dt
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt; import io, base64
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kfont import set_korean_font; set_korean_font()
import a2_data, a2_profit_vault as V
try: import a2_attack_ledger as AL, a2_moonshot_ledger as ML
except Exception: AL = ML = None
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); REPO = os.path.dirname(ROOT)
A2 = os.path.join(ROOT, "outputs", "a2_live"); POS = os.path.join(A2, "positions"); os.makedirs(POS, exist_ok=True)
DASH = os.path.join(ROOT, "outputs", "a2_book_dashboard.html"); REPORT = os.path.join(ROOT, "reports", "A2_book_status.md")
STATE = os.path.join(A2, "book_state.json")
CAP = 100_000_000     # 가상 ₩1억
INCEPTION = "2026-05-12"
# A2-Beta = QQQ/TQQQ/Vault (Attack/Moon 20% → 검증 엔진으로·QQQ45/TQQQ45/Vault10·가정·configurable)
W_BETA = {"qqq": 0.45, "tqqq": 0.45, "vault": 0.10}
W_FULL = {"qqq": 0.35, "tqqq": 0.35, "attack": 0.10, "moon": 0.10, "vault": 0.10}
W_NAIVE = {"qqq": 0.35, "tqqq": 0.35}      # 나머지 cash (naive beta book = 판단 기준선)
VAULT_RULES = V.load_rules()


def pull_prices():
    """QQQ/TQQQ/SPY 일봉 (a2_data 캐시 = 2016~). forward는 cron이 prices.csv 갱신하지만 여기선 캐시 backbone."""
    b = a2_data.benchmarks()
    return b[[c for c in ["QQQ", "TQQQ", "SPY"] if c in b.columns]].dropna()


def run_beta(px, w, vault_on, risk_series=None):
    """A2-Beta 달러 ledger (실제 Vault 차감). 반환 NAV series·vault ledger·accounting OK.
    risk_series: index별 'GREEN/YELLOW/RED'(Vault In 강도·없으면 GREEN)."""
    qr = px["QQQ"].pct_change().fillna(0).values; tr = px["TQQQ"].pct_change().fillna(0).values
    idx = px.index; qqq_bh = (px["QQQ"] / px["QQQ"].iloc[0]).values   # QQQ buy-hold(excess 기준)
    qqq = CAP * w["qqq"]; tqqq = CAP * w["tqqq"]
    vault = {"hard": 0.0, "reload": CAP * w.get("vault", 0.0), "hwm": 0.0}   # base vault = Reload 초기 reserve
    cash = CAP - qqq - tqqq - vault["reload"]
    navs = []; vlocked = []; cur_mo = None; m_moved = 0.0
    for i in range(len(idx)):
        mo = idx[i].to_period("M")
        if mo != cur_mo: cur_mo = mo; m_moved = 0.0
        # 1) 노출 마크(다음 bar 수익 = next-bar; i=0은 진입일 0수익)
        if i > 0: qqq *= (1 + qr[i]); tqqq *= (1 + tr[i])
        nav = qqq + tqqq + vault["hard"] + vault["reload"] + cash
        # 2) Vault In (실제 차감·이긴 돈일 때만·live_excess HWM)
        if vault_on:
            excess = nav / CAP - qqq_bh[i]              # vs QQQ buy-hold (fraction)
            abs_profit = nav > CAP
            risk = (risk_series[i] if risk_series is not None else "GREEN")
            if excess > vault["hwm"] + 1e-9 and abs_profit:
                rate = V.classify_vault_in(excess, True, risk, VAULT_RULES)
                cap_m = (VAULT_RULES.get("vault_in_gate", {}) or {}).get("max_monthly_move_pct", 0.10)
                m = max(0.0, min((excess - vault["hwm"]) * rate, cap_m - m_moved))
                if m > 1e-9:
                    move = m * nav; exp = qqq + tqqq
                    if exp > 1e-6:
                        qqq -= move * qqq / exp; tqqq -= move * tqqq / exp     # ★ 실제 exposure 차감
                        vault["hard"] += move * 0.70; vault["reload"] += move * 0.30; m_moved += m
                vault["hwm"] = excess
        navs.append(qqq + tqqq + vault["hard"] + vault["reload"] + cash)
        vlocked.append(vault["hard"] + vault["reload"])
    s = pd.Series(navs, index=idx)
    # 회계 assert (마지막)
    acct_ok = abs((qqq + tqqq + vault["hard"] + vault["reload"] + cash) - navs[-1]) < 1.0
    return s, pd.Series(vlocked, index=idx), {"hard": vault["hard"], "reload": vault["reload"], "hwm": vault["hwm"],
                                              "qqq": qqq, "tqqq": tqqq, "cash": cash, "acct_ok": acct_ok}


def naive_book(px, w):
    qr = px["QQQ"].pct_change().fillna(0); tr = px["TQQQ"].pct_change().fillna(0)
    return CAP * (1 + w["qqq"] * qr + w["tqqq"] * tr).cumprod()


def metrics(s):
    s = s.dropna(); ret = s.iloc[-1] / s.iloc[0] - 1
    yrs = (s.index[-1] - s.index[0]).days / 365.25
    cagr = (s.iloc[-1] / s.iloc[0]) ** (1 / yrs) - 1 if yrs > 0 else np.nan
    dd = s / s.cummax() - 1; mdd = float(dd.min())
    return {"ret": ret, "cagr": cagr, "mdd": mdd}


def risk_state_series(px):
    """간단 risk: QQQ 200일선·20일 vol → GREEN/YELLOW/RED (Vault In 강도용·정보용)."""
    ma200 = px["QQQ"].rolling(200).mean(); vol20 = px["QQQ"].pct_change().rolling(20).std() * np.sqrt(252)
    out = []
    for i in range(len(px)):
        below = px["QQQ"].iloc[i] < (ma200.iloc[i] if not np.isnan(ma200.iloc[i]) else px["QQQ"].iloc[i])
        hv = (vol20.iloc[i] if not np.isnan(vol20.iloc[i]) else 0) > 0.35
        out.append("RED" if (below and hv) else ("YELLOW" if (below or hv) else "GREEN"))
    return out


def live_attack_moon():
    """forward live paper ledger 평가 (positions/attack.json·moonshot.json·빈슬롯=cash·realized→Vault 연결은 forward)."""
    if AL is None: return {"attack_n": 0, "moon_n": 0, "attack_val": CAP * 0.10, "moon_val": CAP * 0.10}
    def loadj(p):
        try: return json.load(open(p))
        except Exception: return []
    attack = loadj(os.path.join(POS, "attack.json")); moon = loadj(os.path.join(POS, "moonshot.json"))
    attack = attack if isinstance(attack, list) else attack.get("positions", [])
    moon = moon if isinstance(moon, list) else moon.get("positions", [])
    px = a2_data.benchmarks()
    cur = lambda t: float(px[t].dropna().iloc[-1]) if t in px.columns and len(px[t].dropna()) else float("nan")
    ae = AL.evaluate(attack, cur, CAP * 0.10) if attack else {"value": CAP * 0.10, "n": 0}
    me = ML.evaluate(moon, cur, CAP * 0.10) if moon else {"value": CAP * 0.10, "n": 0}
    return {"attack_n": ae.get("n", 0), "moon_n": me.get("n", 0), "attack_val": ae.get("value", CAP*0.10), "moon_val": me.get("value", CAP*0.10)}


def main():
    px = pull_prices()
    rs = risk_state_series(px)
    beta_nav, beta_vlock, beta_v = run_beta(px, W_BETA, vault_on=True, risk_series=rs)
    naive_nav = naive_book(px, W_NAIVE)
    qqq_nav = CAP * px["QQQ"] / px["QQQ"].iloc[0]; tqqq_nav = CAP * px["TQQQ"] / px["TQQQ"].iloc[0]
    # A2-Full = A2-Beta core + Attack/Moonshot live(과거엔 빈슬롯=cash → backtest상 A2-Full≈Beta with 20% cash·라벨)
    full_nav_bt = run_beta(px, {"qqq": 0.35, "tqqq": 0.35, "vault": 0.10}, vault_on=True, risk_series=rs)[0]  # Attack/Moon=cash(20%)
    am = live_attack_moon()
    # 지표
    mB, mN, mQ, mT = metrics(beta_nav), metrics(naive_nav), metrics(qqq_nav), metrics(tqqq_nav)
    vaulted = beta_v["hard"] + beta_v["reload"] - CAP * W_BETA["vault"]   # base reserve 제외 = 실제 잠근 수익
    beat_qqq = bool(mB["ret"] > mQ["ret"]); beat_naive = bool(mB["ret"] > mN["ret"])
    # ── 판단 ──
    verdict = ("A2-Beta가 QQQ·naive 둘 다 이김" if (beat_qqq and beat_naive)
               else "A2-Beta가 naive를 못 이김 = TQQQ 베타효과지 운영규칙 부가가치 미확정" if beat_qqq
               else "A2-Beta가 QQQ도 못 이김")
    # forward live slice
    incep = pd.Timestamp(INCEPTION)
    def live(s): sl = s[s.index >= incep]; return float(sl.iloc[-1]/sl.iloc[0]-1) if len(sl) > 1 else 0.0
    live_days = int((px.index >= incep).sum())
    cur_dd = float(beta_nav.iloc[-1] / beta_nav.cummax().iloc[-1] - 1)            # 현재(peak-to-now) drawdown — backtest max(A2Beta_mdd)와 구분(crash lockout은 이걸 봐야)
    live_slice = beta_nav[beta_nav.index >= incep]
    live_cur_dd = float(live_slice.iloc[-1] / live_slice.cummax().iloc[-1] - 1) if len(live_slice) > 1 else 0.0
    state = {"as_of": str(px.index[-1].date()), "inception": INCEPTION, "live_days": live_days,
             "A2Beta_ret": mB["ret"], "A2Beta_cagr": mB["cagr"], "A2Beta_mdd": mB["mdd"],
             "A2Beta_current_dd": round(cur_dd, 4), "A2Beta_live_current_dd": round(live_cur_dd, 4),
             "naive_ret": mN["ret"], "qqq_ret": mQ["ret"], "tqqq_ret": mT["ret"],
             "vault_hard": beta_v["hard"]/CAP, "vault_reload": beta_v["reload"]/CAP, "vaulted_profit_real": vaulted/CAP,
             "beat_qqq": beat_qqq, "beat_naive": beat_naive, "verdict": verdict, "acct_ok": bool(beta_v["acct_ok"]),
             "attack_n": am["attack_n"], "moon_n": am["moon_n"], "live_A2Beta": live(beta_nav), "live_qqq": live(qqq_nav)}
    json.dump(state, open(STATE, "w"), indent=2, ensure_ascii=False)
    build_dashboard(px, beta_nav, full_nav_bt, naive_nav, qqq_nav, tqqq_nav, beta_vlock, state, am)
    write_report(state, am)
    print(f"✅ A2 Book: A2-Beta {mB['ret']*100:+.0f}%(MDD {mB['mdd']*100:.0f}%)·naive {mN['ret']*100:+.0f}%·QQQ {mQ['ret']*100:+.0f}%·TQQQ {mT['ret']*100:+.0f}%")
    print(f"   beat QQQ:{beat_qqq}/naive:{beat_naive} · Vaulted Profit(실제) {vaulted/CAP*100:.2f}% (Hard {beta_v['hard']/CAP*100:.1f}%/Reload {beta_v['reload']/CAP*100:.1f}%) · 회계 OK:{beta_v['acct_ok']}")
    print(f"   Attack live {am['attack_n']}건·Moonshot live {am['moon_n']}건(live paper ledger·과거 백테스트 증명 X) · 판단: {verdict}")


def build_dashboard(px, beta, full, naive, qqq, tqqq, vlock, st, am):
    plt.style.use("dark_background"); plt.rcParams.update({"axes.facecolor": "#0d1326", "figure.facecolor": "#0d1326", "grid.alpha": .15, "font.size": 9})
    f, ax = plt.subplots(figsize=(11, 4.0))
    for k, s, c, lw in [("TQQQ", tqqq, "#ec4899", 1.1), ("QQQ", qqq, "#a78bfa", 1.3), ("naive 35/35", naive, "#f59e0b", 1.3),
                        ("A2-Beta (real Vault)", beta, "#22d3ee", 2.6)]:
        ax.plot(s.index, s / 1e8, label=k, color=c, lw=lw, ls="-" if "A2" in k else "--")
    ax.fill_between(vlock.index, 0, vlock / 1e8, color="#16a34a", alpha=0.15, label="Vault locked(실제 차감)")
    ax.legend(framealpha=.2, ncol=5, fontsize=8); ax.set_title("A2-Beta(QQQ/TQQQ + 실제 Vault 차감) vs naive·QQQ·TQQQ — 계좌금액(억·백테스트 2016~)", color="#e5e7eb"); ax.set_ylabel("억원")
    b = io.BytesIO(); f.savefig(b, format="png", dpi=95, bbox_inches="tight", facecolor="#0d1326"); plt.close(f); ch = base64.b64encode(b.getvalue()).decode()
    vc = "#34d399" if st["beat_naive"] else "#f87171"
    html = f"""<!doctype html><html lang=ko><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<meta http-equiv=refresh content=3600><title>PRAMANA A2 Book</title><style>
body{{background:#070b16;color:#e5e7eb;font-family:'Segoe UI','Malgun Gothic',system-ui;margin:0;line-height:1.55}}
.wrap{{max-width:1000px;margin:0 auto;padding:22px 18px 60px}} h1{{font-size:1.3em}} h2{{font-size:1.0em;border-left:4px solid #22d3ee;padding-left:10px;margin-top:18px}}
.kpis{{display:flex;flex-wrap:wrap;gap:9px;margin:12px 0}} .kpi{{flex:1;min-width:95px;background:#0d1326;border:1px solid #1e293b;border-radius:12px;padding:10px 12px}}
.kpi .l{{color:#94a3b8;font-size:.66em}} .kpi .v{{font-size:1.15em;font-weight:800}} .card{{background:#0d1326;border:1px solid #1e293b;border-radius:14px;padding:15px;margin:10px 0}} img{{width:100%;border-radius:8px}}
table{{width:100%;border-collapse:collapse;font-size:.84em}} th{{background:#111a30;color:#94a3b8;text-align:left;padding:6px 8px}} td{{padding:5px 8px;border-top:1px solid #1a2540}}
.warn{{background:#1c1408;border:1px solid #92400e;border-radius:10px;padding:11px 14px;color:#fde68a;font-size:.8em}} .grn{{color:#34d399}} .red{{color:#f87171}}</style></head><body>
<div class=wrap><h1>🟣 PRAMANA A2 Book — A2-Beta / A2-Full <span style="font-size:.5em;background:#5b21b6;color:#ddd6fe;padding:3px 9px;border-radius:20px">PAPER·₩1억·검증된 알파 아님</span></h1>
<p style='color:#94a3b8'>본체 = <b>TQQQ Booster(레버 베타·알파 아님) + Vault(실제 회계)</b> · Attack/Moonshot = live paper optionality(과거 백테스트로 증명 X). 백테스트 2016~(강세장·닷컴/2008 없음).</p>
<div class=kpis>
<div class=kpi><div class=l>A2-Beta</div><div class="v" style="color:#22d3ee">{st['A2Beta_ret']*100:+.0f}%</div></div>
<div class=kpi><div class=l>naive 35/35</div><div class="v" style="color:#f59e0b">{st['naive_ret']*100:+.0f}%</div></div>
<div class=kpi><div class=l>QQQ</div><div class="v" style="color:#a78bfa">{st['qqq_ret']*100:+.0f}%</div></div>
<div class=kpi><div class=l>A2-Beta MDD</div><div class="v">{st['A2Beta_mdd']*100:.0f}%</div></div>
<div class=kpi><div class=l>Vaulted Profit(실제)</div><div class="v grn">{st['vaulted_profit_real']*100:.2f}%</div></div></div>
<div class=card><img src="data:image/png;base64,{ch}"></div>
<div class=card style="border:1px solid {vc}"><b>판단:</b> {'✅' if st['beat_qqq'] else '❌'} vs QQQ · {'✅' if st['beat_naive'] else '❌'} vs naive beta book · <b style="color:{vc}">{st['verdict']}</b><br>
<span style="color:#94a3b8;font-size:.85em">A2-Beta가 naive(같은 QQQ/TQQQ 베타)를 못 이기면 = 운영규칙(Vault/risk) 부가가치 미확정 = 그냥 레버 베타.</span></div>
<h2>💰 Vault (실제 active capital 차감 — 표시용 아님)</h2>
<div class=card>Hard {st['vault_hard']*100:.1f}%(영구 잠금·재투입 불가) / Reload {st['vault_reload']*100:.1f}%(재배치 가능) · <b class=grn>Vaulted Profit(실제 잠근 수익) {st['vaulted_profit_real']*100:.2f}%</b><br>
<span style="color:#94a3b8;font-size:.85em">Vault In = exposure(QQQ/TQQQ)에서 실제로 빼서 locked cash로 → 낙폭에 수익 보존. 회계 불변식 NAV=Σsleeve assert {'OK' if st['acct_ok'] else 'FAIL'}.</span></div>
<h2>⚔️ Attack / 🚀 Moonshot (A2-Full·live paper ledger optionality)</h2>
<div class=card style="color:#94a3b8;font-size:.85em">Attack {am['attack_n']}건·Moonshot {am['moon_n']}건 (실시간 후보→paper entry→PNL→Vault 연결). <b style="color:#fbbf24">과거 EDGAR catalyst 방향 알파 = DEAD → 자동 알파 아님·실시간 기회 ledger·optionality.</b> 빈슬롯=cash. live {st['live_days']}거래일.</div>
<div class=warn>⚠️ PAPER·NO LIVE·₩1억·자본권한 0. TQQQ=Booster(레버 베타·알파 아님)·daily reset 위험. Vaulted Profit은 실제 회계(차감)일 때만 표기. AX/S1/S2/S3 historical = DEAD(튜닝 금지). 설계 council/2026-06-14_aggressive-pivot.</div>
</div></body></html>"""
    open(DASH, "w").write(html)


def write_report(st, am):
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    md = f"""# A2 Book Status — {st['as_of']}

> RESEARCH_ONLY / PRODUCTION_UNSAFE · PAPER · 가상 ₩1억 · 자본권한 0 · 검증된 알파 아님. 정본 council/2026-06-14_aggressive-pivot.
> 본체 = TQQQ Booster(레버 베타·알파 아님) + Vault(실제 회계) + Risk gate. Attack/Moonshot = live paper optionality(백테스트 증명 X).

## A2-Beta(QQQ45/TQQQ45/Vault10·실제 Vault 차감) vs 기준 (백테스트 2016~·강세장 편향)
| | 총수익 | CAGR | MDD |
|---|---|---|---|
| **A2-Beta** | {st['A2Beta_ret']*100:+.0f}% | {st['A2Beta_cagr']*100:+.0f}% | {st['A2Beta_mdd']*100:.0f}% |
| naive 35/35 (기준선) | {st['naive_ret']*100:+.0f}% | — | — |
| QQQ | {st['qqq_ret']*100:+.0f}% | — | — |
| TQQQ | {st['tqqq_ret']*100:+.0f}% | — | — |

**판단:** vs QQQ {'✅' if st['beat_qqq'] else '❌'} · vs naive beta book {'✅' if st['beat_naive'] else '❌'} → **{st['verdict']}**
(A2-Beta가 naive를 못 이기면 = TQQQ 베타지 Vault/risk 운영규칙 부가가치 미확정.)

## Vault (실제 차감·Vaulted Profit 진짜)
- Hard {st['vault_hard']*100:.1f}%(영구 잠금) / Reload {st['vault_reload']*100:.1f}%(재배치) · **Vaulted Profit(실제) {st['vaulted_profit_real']*100:.2f}%**
- Vault In = exposure에서 실제 차감→locked cash(낙폭에 수익 보존). 회계 불변식 NAV=Σsleeve assert: **{'OK' if st['acct_ok'] else 'FAIL'}**.

## Attack/Moonshot (A2-Full·live paper ledger)
- Attack {am['attack_n']}건·Moonshot {am['moon_n']}건. **과거 EDGAR catalyst 방향 알파 DEAD(AX/S1/S2/S3) → 자동 알파 아님·실시간 기회 ledger·optionality.** 빈슬롯=cash. live {st['live_days']}거래일.

## 정직
- TQQQ가 가장 확실한 엔진이나 **레버 베타지 알파 아님**(daily reset·장기 발산 위험). A2-Beta>QQQ는 레버 효과.
- 백테스트 2016~ = 강세장(닷컴/2008 없음) → 레버북 하방 미검증.
- Attack/Moonshot은 과거로 증명 안 함(DEAD 확정)·forward live paper로만 관찰·튜닝 금지.
- 다음 판단 = A2-Beta가 naive도 이기는가 + Vaulted Profit 실제 누적 + 큰 낙폭 후 게임 지속.
"""
    open(REPORT, "w").write(md)


if __name__ == "__main__":
    main()

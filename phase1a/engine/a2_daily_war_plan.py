#!/usr/bin/env python3
"""PRAMANA A2 — Daily War Plan (SSOT v2 §10 §3·§04). 장 시작 전 상태 통합.

LLM = 상태 판정·narrative만(비중·확률·매수매도 결정 ❌). 비중 = mapping engine(a2_dynamic_allocator)·게이트 = rule.
입력 통합: a2_risk_dashboard(states)·a2_neg_gate(NEG flags)·attack_candidates·moonshot draft·allocator/drawdown(있으면).
출력 = outputs/a2_live/war_plan.json (SSOT §10 §3 schema) + reports/A2_daily_war_plan.md.
실행: python engine/a2_daily_war_plan.py (a2_risk_dashboard 다음). PAPER·자본권한 0.
"""
import os, sys, json, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
A2 = os.path.join(ROOT, "outputs", "a2_live")
RJSON = os.path.join(A2, "risk_dashboard.json"); WAR_JSON = os.path.join(A2, "war_plan.json")
WAR_MD = os.path.join(ROOT, "reports", "A2_daily_war_plan.md")
ALLOC = os.path.join(A2, "allocator_state.json"); DDOWN = os.path.join(A2, "drawdown_state.json")
CANDS = os.path.join(A2, "attack_candidates.csv")


def loadj(p, d=None):
    try: return json.load(open(p))
    except Exception: return d


def derive_permissions(r):
    """risk_dashboard state → sleeve permission (rule engine·LLM 아님·SSOT §04 §5)."""
    lead = r.get("leadership_state", "GREEN"); market = r.get("market_stress", "GREEN")
    decay = r.get("tqqq_decay", False); rent = r.get("booster_rent", False)
    red = lead == "RED" or market == "RED"
    return {
        "market_state": market, "leadership_state": lead,
        "tqqq_state": "RED" if (red or decay or rent) else ("YELLOW" if lead == "YELLOW" else "GREEN"),
        "attack_state": "RED" if red else ("YELLOW" if lead == "YELLOW" else "GREEN"),
        "moonshot_state": "LOCKED" if red else ("HOLD_ONLY" if lead == "YELLOW" else "OPEN"),
        "vault_state": ("ACCUMULATE" if (lead in ("YELLOW", "RED") or decay)
                        else ("RELOAD_ALLOWED" if (lead == "GREEN" and not decay and r.get("qqq_above_ma20")) else "HOLD")),
        "tqqq_permission": "BAN_ADD" if (red or decay) else "HOLD_ONLY" if lead == "YELLOW" else "ADD_OK",
        "attack_permission": "LOCKED" if red else ("HALF" if lead == "YELLOW" else "FULL"),
        "moonshot_permission": "LOCKED" if red else ("HOLD_ONLY" if lead == "YELLOW" else "OPEN"),
    }


def main():
    r = loadj(RJSON, {})
    if not r:
        print("⛔ risk_dashboard.json 없음 — engine/a2_risk_dashboard.py 먼저 실행"); return
    today = r.get("as_of", str(dt.date.today()))
    g = derive_permissions(r)
    alloc = loadj(ALLOC, {}); ddown = loadj(DDOWN, {})
    mode = (ddown.get("mode") or (alloc.get("mode") if isinstance(alloc, dict) else None) or "base")
    # top attack candidates (scanner 출력)
    top_attack = []
    if os.path.exists(CANDS):
        try:
            import pandas as pd; df = pd.read_csv(CANDS)
            if "grade" in df: top_attack = [r2["ticker"] for _, r2 in df.iterrows() if r2.get("grade") in ("A", "B")][:5]
        except Exception: pass
    forbidden = []
    if g["tqqq_permission"] == "BAN_ADD": forbidden.append("TQQQ 신규 증액 금지")
    if g["attack_permission"] == "LOCKED": forbidden.append("Attack 신규 진입 금지")
    if g["moonshot_permission"] == "LOCKED": forbidden.append("Moonshot 신규 금지")
    if r.get("tqqq_decay"): forbidden.append("TQQQ Decay Zone — Booster 증액 금지")
    if r.get("booster_rent"): forbidden.append("Booster Rent — TQQQ 비효율·증액 금지·Vault 우선")
    if ddown.get("crash_lockout"): forbidden.append("CRASH LOCKOUT — 전 sleeve 신규 0·사람 리뷰")
    war = {"date": today, **g, "mode": mode,
           "narrative_state": "PENDING(LLM/수동 — AI capex·빅테크 가이던스·금리/규제·earnings tone 요약 입력 TODO)",
           "effective_beta": r.get("effective_beta"), "leadership_score": r.get("leadership_score"),
           "top_risks": [x for x in ["Leadership " + r.get("leadership_state", ""),
                                     "Market " + r.get("market_stress", ""),
                                     "Decay" if r.get("tqqq_decay") else None,
                                     "BoosterRent" if r.get("booster_rent") else None] if x and not x.endswith("GREEN")],
           "top_attack_candidates": top_attack, "top_moonshot_candidates": [],
           "neg_filing_warnings": r.get("neg_leaders", []),
           "forbidden_actions_today": forbidden,
           "human_review_required": ["실자본은 사람 게이트", "Vault Hard 재투입 금지", "동적 비중 변경은 mapping engine·LLM 아님",
                                     "CRASH 시 자동매도 X·manual flag만"] + (["CRASH LOCKOUT 검토"] if ddown.get("crash_lockout") else []),
           "note": "LLM=상태/narrative만·비중=mapping engine(a2_dynamic_allocator)·게이트=rule. SSOT v2."}
    os.makedirs(os.path.dirname(WAR_MD), exist_ok=True)
    json.dump(war, open(WAR_JSON, "w"), indent=2, ensure_ascii=False)
    C = {"GREEN": "🟢", "YELLOW": "🟡", "RED": "🔴"}
    md = f"""# A2 Daily War Plan — {today}
> SSOT v2 §10. LLM = 상태판정·narrative만(비중·확률·매수매도 ❌). 게이트/비중 = rule/mapping engine.

| 항목 | 상태 |
|---|---|
| Market | {C.get(g['market_state'],'')} {g['market_state']} |
| Leadership | {C.get(g['leadership_state'],'')} {g['leadership_state']} (score {r.get('leadership_score','?')}/77) |
| TQQQ | {C.get(g['tqqq_state'],'')} {g['tqqq_state']} · Decay {'🔴ZONE' if r.get('tqqq_decay') else '🟢OK'} · BoosterRent {'🔴' if r.get('booster_rent') else '🟢'} |
| Attack | {C.get(g['attack_state'],'')} {g['attack_state']} → {g['attack_permission']} |
| Moonshot | {g['moonshot_state']} → {g['moonshot_permission']} |
| Vault | {g['vault_state']} |
| Mode | {mode} · effBeta {r.get('effective_beta','?')}x |

**오늘 금지:** {' · '.join(forbidden) if forbidden else '없음'}
**Top Attack 후보:** {', '.join(top_attack) if top_attack else '(없음/Leadership RED)'}
**NEG 경고(leaders):** {', '.join(r.get('neg_leaders', [])) if r.get('neg_leaders') else '없음'}
**사람 확인:** {' · '.join(war['human_review_required'])}

_근거: risk_dashboard(Leadership {g['leadership_state']}·Market {g['market_state']}·Decay {'Y' if r.get('tqqq_decay') else 'N'}) → rule 게이트. 비중 = a2_dynamic_allocator(next-bar·5%p)._
"""
    open(WAR_MD, "w").write(md)
    print(f"✅ War Plan {today}: Market {g['market_state']}·Lead {g['leadership_state']}·TQQQ {g['tqqq_permission']}·"
          f"Attack {g['attack_permission']}·Moonshot {g['moonshot_permission']}·Vault {g['vault_state']}·mode {mode}·금지 {len(forbidden)}건")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""PRAMANA A2 Phase C1 — Daily War Plan (장 시작 전 상태 판정).
LLM은 GREEN/YELLOW/RED 상태 + narrative만 (비중 결정 ❌·확률 결정 ❌·매수/매도 명령 ❌).
게이트/비중은 rule engine이 결정(동적 OFF=비중 고정·게이트는 신규/증액 허용만 조절).
입력 = a2_live state(Leadership/Decay/regime) + Attack/Moonshot candidates + Vault. 출력 = war_plan.json·reports/A2_daily_war_plan.md.
실행: python engine/a2_daily_war_plan.py (a2_live_runner 다음). PAPER·자본권한 0."""
import os, json, datetime as dt
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
A2=os.path.join(ROOT,"outputs","a2_live"); STATE=os.path.join(A2,"state.json")
WAR_JSON=os.path.join(A2,"war_plan.json"); WAR_MD=os.path.join(ROOT,"reports","A2_daily_war_plan.md")

def derive(st):
    """rule engine: Risk Dashboard state → sleeve 게이트(GREEN/YELLOW/RED). LLM 아님."""
    lead=st.get("lead","GREEN"); decay=bool(st.get("decay",False))
    market = "RED" if lead=="RED" else ("YELLOW" if (lead=="YELLOW" or decay) else "GREEN")
    return {
        "market_state": market,
        "leadership_state": lead,
        "tqqq_permission": "BAN_ADD" if lead=="RED" else ("HOLD_ONLY" if (lead=="YELLOW" or decay) else "ADD_OK"),
        "attack_permission": "LOCKED" if lead=="RED" else ("HALF" if lead=="YELLOW" else "FULL"),
        "moonshot_permission": "LOCKED" if lead=="RED" else ("HOLD_ONLY" if lead=="YELLOW" else "OPEN"),
        "vault_state": "RELOAD_ALLOWED" if (lead=="GREEN" and not decay) else "ACCUMULATE",
        "decay": decay,
    }

def main():
    st=json.load(open(STATE)) if os.path.exists(STATE) else {}
    today=str(st.get("last_run", dt.date.today()))
    g=derive(st)
    forbidden=[]
    if g["tqqq_permission"]=="BAN_ADD": forbidden.append("TQQQ 신규 증액 금지")
    if g["attack_permission"]=="LOCKED": forbidden.append("Attack 신규 진입 금지")
    if g["moonshot_permission"]=="LOCKED": forbidden.append("Moonshot 신규 금지")
    if g["decay"]: forbidden.append("TQQQ Decay Zone — Booster 증액 금지")
    war={"date":today, **g,
         "narrative_state":"PENDING(LLM/수동 — AI capex·빅테크 가이던스·금리/규제·earnings tone 요약 입력 TODO)",
         "top_attack_candidates":[],   # C3 Attack scanner 출력 연결 예정
         "top_moonshot_candidates":[], # Moonshot draft board 연결 예정
         "neg_filing_warnings":[],     # EDGAR NEG gate 연결 예정
         "forbidden_today":forbidden,
         "human_review_required":["실자본은 사람 게이트","동적 비중 OFF(REJECT)·고정 35/35 유지","Vault Hard 재투입 금지"],
         "note":"LLM=상태/narrative만·비중은 rule(동적 OFF)·게이트는 신규/증액 허용 조절."}
    os.makedirs(os.path.dirname(WAR_MD), exist_ok=True)
    json.dump(war, open(WAR_JSON,"w"), indent=2, ensure_ascii=False)
    C={"GREEN":"🟢","YELLOW":"🟡","RED":"🔴"}
    md=f"""# A2 Daily War Plan — {today}
> LLM = 상태판정·narrative만(비중·확률·매수매도 결정 ❌). 게이트/비중 = rule engine(동적 OFF·고정 35/35).

| 항목 | 상태 |
|---|---|
| Market | {C.get(g['market_state'],'')} {g['market_state']} |
| Leadership | {C.get(g['leadership_state'],'')} {g['leadership_state']} (score {st.get('lead_score','?')}/30) |
| TQQQ Decay | {'🔴 ZONE' if g['decay'] else '🟢 OK'} |
| **TQQQ permission** | {g['tqqq_permission']} |
| **Attack permission** | {g['attack_permission']} |
| **Moonshot permission** | {g['moonshot_permission']} |
| **Vault** | {g['vault_state']} |
| Narrative(LLM/수동) | {war['narrative_state']} |

**오늘 금지:** {' · '.join(forbidden) if forbidden else '없음'}
**Top Attack 후보:** (C3 scanner 연결 예정)
**Top Moonshot 후보:** (draft board 연결 예정)
**NEG filing 경고:** (EDGAR gate 연결 예정)
**사람 확인:** {' · '.join(war['human_review_required'])}

_근거: Leadership {g['leadership_state']}·Decay {'Y' if g['decay'] else 'N'} → rule 게이트. 비중은 동적 OFF(고정 35/35·ablation −113%p REJECT)._
"""
    open(WAR_MD,"w").write(md)
    print(f"✅ War Plan {today}: Market {g['market_state']}·Lead {g['leadership_state']}·TQQQ {g['tqqq_permission']}·Attack {g['attack_permission']}·Moonshot {g['moonshot_permission']}·Vault {g['vault_state']}·금지 {len(forbidden)}건")
if __name__=="__main__": main()

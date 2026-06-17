#!/usr/bin/env python3
"""PRAMANA A2 — Attack Token system (주간 토큰 회계·과매매 방지).

설계 정본: pramana_a2_implementation_pack/07_ATTACK_MODULE.md §9.
규칙:
  - 매주 기본 3 token.
  - A급 진입 = 1 token, B급 진입 = 0.5 token, C급 = paper only(토큰 0·실진입 금지).
  - 손실 trade → 다음 주 token -1.
  - +2R 이상 승리 → 다음 주 token +1.
  - Leadership RED → 그 주 token 0(신규 진입 봉쇄).
  - 토큰 0이면 신규 Attack 진입 불가(과매매 차단).
ledger = positions/attack_tokens.json (append-only week_history). PAPER·자본권한 0·매수 명령 X(가용량만 계산).
"""
import os, sys, json, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
TOK = os.path.join(ROOT, "outputs", "a2_live", "positions", "attack_tokens.json")
BASE_WEEKLY = 3.0
GRADE_COST = {"A": 1.0, "B": 0.5, "C": 0.0, "D": 0.0}


def _week_key(d=None):
    d = d or dt.date.today()
    y, w, _ = d.isocalendar()
    return f"{y}-W{w:02d}"


def load(path=TOK):
    if os.path.exists(path):
        try: return json.load(open(path))
        except Exception: pass
    d = {"current_week": None, "available": BASE_WEEKLY, "carry_next": 0.0, "week_history": []}
    os.makedirs(os.path.dirname(path), exist_ok=True); json.dump(d, open(path, "w"), indent=2); return d


def roll_week(state, leadership, week=None):
    """새 주 시작 시 호출: 기본 3 + 직전 carry(승리 +1/손실 -1 누적) 적용. Leadership RED면 그 주 0."""
    wk = week or _week_key()
    if state.get("current_week") == wk:
        return state
    if state.get("current_week") is not None:
        state["week_history"].append({"week": state["current_week"], "ended_available": state["available"]})
    base = 0.0 if leadership == "RED" else BASE_WEEKLY + state.get("carry_next", 0.0)
    state["current_week"] = wk
    state["available"] = max(0.0, base)
    state["carry_next"] = 0.0
    state["leadership_at_roll"] = leadership
    return state


def can_enter(state, grade, leadership):
    """진입 가능 여부 + 토큰 비용. C/D=paper only. RED=봉쇄."""
    if leadership == "RED":
        return {"allowed": False, "cost": 0.0, "reason": "Leadership RED → Attack 신규 봉쇄(토큰 0)"}
    if grade in ("C", "D"):
        return {"allowed": False, "cost": 0.0, "reason": f"{grade}급 = paper only(실진입 금지)"}
    cost = GRADE_COST.get(grade, 0.0)
    if state["available"] + 1e-9 < cost:
        return {"allowed": False, "cost": cost, "reason": f"토큰 부족({state['available']:.1f}<{cost})·과매매 차단"}
    return {"allowed": True, "cost": cost, "reason": f"{grade}급 진입 {cost} token"}


def spend(state, grade):
    c = GRADE_COST.get(grade, 0.0)
    state["available"] = max(0.0, state["available"] - c)
    return state


def record_close(state, pnl_R):
    """청산 결과 → 다음 주 carry 조정. 손실 -1, +2R 이상 +1."""
    if pnl_R is None: return state
    if pnl_R <= 0: state["carry_next"] = state.get("carry_next", 0.0) - 1.0
    elif pnl_R >= 2: state["carry_next"] = state.get("carry_next", 0.0) + 1.0
    return state


def save(state, path=TOK):
    os.makedirs(os.path.dirname(path), exist_ok=True); json.dump(state, open(path, "w"), indent=2, ensure_ascii=False)


def main():
    """CLI: state.json의 Leadership로 이번 주 토큰 롤 + 가용량 출력(매수 X)."""
    st = load()
    state_path = os.path.join(ROOT, "outputs", "a2_live", "state.json")
    lead = "GREEN"
    if os.path.exists(state_path):
        try: lead = json.load(open(state_path)).get("lead", "GREEN")
        except Exception: pass
    roll_week(st, lead); save(st)
    demo = {g: can_enter(st, g, lead)["reason"] for g in ("A", "B", "C")}
    print(f"✅ Attack tokens {st['current_week']} (Leadership {lead}): 가용 {st['available']:.1f} token · carry_next {st['carry_next']:+.1f}")
    for g, r in demo.items(): print(f"   {g}급: {r}")


if __name__ == "__main__":
    main()

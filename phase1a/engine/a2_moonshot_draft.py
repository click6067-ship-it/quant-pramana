#!/usr/bin/env python3
"""PRAMANA A2 — Moonshot Draft Board (후보 줄세우기·상위 1~2개만 진입).

설계 정본: pramana_a2_implementation_pack/08_MOONSHOT_MODULE.md §4·§11.
원칙: 후보를 바로 사지 않는다. draft board에서 10개 축으로 점수→순위→상위 1~2개만 실제 진입 자격.
등급: M1(판정일+R/R≥3+NEG없음)·M2(narrative만→Attack 격하)·M3(꿈→금지).
점수축(0~3): catalyst_clarity·time_to_catalyst·reward_risk·neg_risk_low·dilution_risk_low·liquidity·
            narrative_strength·llm_bear_low(=bear case 심각도 낮을수록 高)·theme_concentration_low·tail_risk_low.
LLM은 bull/bear case만 작성·P_up은 사람. PAPER·자본권한 0·매수 명령 X(순위만).
"""
import os, sys, json

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DRAFT = os.path.join(ROOT, "outputs", "a2_live", "positions", "moonshot.json")

AXES = ["catalyst_clarity", "time_to_catalyst", "reward_risk_score", "neg_risk_low", "dilution_risk_low",
        "liquidity", "narrative_strength", "llm_bear_low", "theme_concentration_low", "tail_risk_low"]
MAX_SCORE = 3.0 * len(AXES)   # 30


def grade(cand):
    """M1/M2/M3 판정 (08 §4)."""
    rr = float(cand.get("reward_risk", 0)); has_date = bool(cand.get("verdict_date") or cand.get("judgement_date"))
    neg = bool(cand.get("hard_neg", False))
    if neg: return "M3"   # Hard NEG는 Moonshot 절대 금지
    if has_date and rr >= 3: return "M1"
    if cand.get("narrative_strength", 0) >= 2: return "M2"   # narrative만 → Attack 격하 후보
    return "M3"


def score(cand):
    """draft 점수 (0~30). 누락 축 = 0(보수적)."""
    return float(sum(min(3.0, max(0.0, float(cand.get(a, 0)))) for a in AXES))


def rank(draft_board, top_n=2):
    """후보 리스트 → 점수·등급·순위 부여, 상위 top_n(M1만) enterable=True."""
    scored = []
    for c in draft_board:
        g = grade(c); s = score(c)
        scored.append({**c, "grade_m": g, "draft_score": round(s, 1), "score_pct": round(100 * s / MAX_SCORE, 1)})
    scored.sort(key=lambda x: (-x["draft_score"], x.get("ticker", "")))
    n = 0
    for c in scored:
        c["enterable"] = bool(c["grade_m"] == "M1" and n < top_n)
        if c["enterable"]: n += 1
    return scored


def load(path=DRAFT):
    if os.path.exists(path):
        try: return json.load(open(path))
        except Exception: pass
    return {"draft_board": [], "positions": [], "closed_theses": []}


def main():
    d = load()
    if isinstance(d, list):   # 구버전 호환(positions list만)
        d = {"draft_board": [], "positions": d}
    board = d.get("draft_board", [])
    if not board:
        print("✅ Moonshot draft board 비어있음 (후보 입력 시 점수/순위/상위2 자동). thesis 없이 진입 금지."); return
    ranked = rank(board)
    print(f"✅ Moonshot Draft Board ({len(ranked)}후보·상위 M1 2개만 진입 자격):")
    for i, c in enumerate(ranked, 1):
        flag = "🟢 ENTERABLE" if c["enterable"] else ("⛔ M3 금지" if c["grade_m"] == "M3" else "⏳ 대기")
        print(f"  {i}. {c.get('ticker','?'):6s} [{c['grade_m']}] score {c['draft_score']:.1f}/{MAX_SCORE:.0f} ({c['score_pct']:.0f}%) {flag} · {str(c.get('thesis',''))[:40]}")


if __name__ == "__main__":
    main()

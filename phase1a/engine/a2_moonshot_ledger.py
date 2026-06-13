#!/usr/bin/env python3
"""PRAMANA A2 Phase B — Moonshot ledger (thesis 기반·판정일 필수·Reward/Risk≥3·Hard NEG 절대금지·P_up 사람).
평가(#4) + thesis 검증 + draft board 점수화 + Moonshot Vault rule. PAPER. a2_live_runner가 import."""
import os, json

# ── 필수 thesis 필드 (판정일 없으면 신앙됨 → 금지) ──
REQUIRED = ["ticker", "thesis", "catalyst", "verdict_date", "success_cond", "fail_cond",
            "invalidation", "max_loss", "reward_risk", "p_up_human", "exit_plan"]
DEFAULT = {"positions": [], "draft_board": [], "closed_theses": []}

def load(path):
    if os.path.exists(path):
        try: return json.load(open(path))
        except: pass
    json.dump(DEFAULT, open(path, "w"), indent=2); return dict(DEFAULT)

def evaluate(positions, cur_price_fn, budget):
    deployed = sum(p["shares"] * p["entry_price"] for p in positions)
    mkt = sum(p["shares"] * cur_price_fn(p["ticker"]) for p in positions)
    return {"value": budget - deployed + mkt, "pnl": mkt - deployed, "deployed": deployed, "n": len(positions)}

# ── 진입 검증 (Moonshot은 Attack과 달리 Hard NEG = 절대 금지) ──
def validate_thesis(t, neg_tickers):
    errors = []
    for f in REQUIRED:
        if f not in t or t.get(f) in (None, ""): errors.append(f"{f} 누락")
    if t.get("reward_risk", 0) < 3: errors.append("Reward/Risk < 3:1")
    if t.get("p_up_human", 0) > 0.60: errors.append("P_up_human > 60%(LLM 아닌 사람 입력·과대평가 금지)")
    if t.get("ticker") in neg_tickers: errors.append("Hard NEG filing → Moonshot 절대 금지")
    return {"valid": len(errors) == 0, "errors": errors}

# ── EV 게이트 (위험×수익×확률) ──
def ev(p_up, upside, p_down, downside, tail=0.0, cost=0.0):
    return p_up * upside - p_down * downside - tail - cost

# ── Draft board 점수화 (바로 사지 말고 줄 세움) ──
SCORE_KEYS = ["catalyst_clarity", "time_to_catalyst", "reward_risk", "neg_risk_low",
              "dilution_risk_low", "liquidity", "narrative_strength", "tail_risk_low"]
def draft_score(c):
    return sum(float(c.get(k, 0)) for k in SCORE_KEYS)

# ── Moonshot Vault rule (2배→원금회수 / 3배→절반 Vault / thesis 깨짐→즉시 종료) ──
def vault_rule(pos, cur):
    ep = pos.get("entry_price", 0)
    if not ep: return "보유"
    r = cur / ep
    if pos.get("thesis_broken"): return "thesis 깨짐 → 즉시 종료"
    if r >= 3: return "3배 → 절반 Vault"
    if r >= 2: return "2배 → 원금 회수"
    return "보유"

# ── 판정일 경과 체크 (Thesis Decay Timer) ──
def expired(verdict_date, today):
    return str(today) > str(verdict_date)

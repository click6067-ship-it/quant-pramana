#!/usr/bin/env python3
"""PRAMANA A2 Phase B — Attack ledger (분봉 day strategy·token·NEG Gate 차등).
positions schema 강제 + 평가(P&L·sleeve value·Codex #4: 슬롯 차도 NAV 정확) + token 회계 + NEG 차등 + 진입 게이트.
PAPER·자본권한 0. a2_live_runner가 import해서 forward Attack sleeve 평가/검증. 단독 실행 X(모듈)."""
import os, json

# ── positions schema (Codex #4: 빈슬롯만 cash·차면 정확 valuation) ──
REQUIRED = ["ticker", "sleeve", "shares", "entry_price", "entry_date", "stop", "catalyst", "grade"]
DEFAULT = {"positions": [], "weekly_tokens": 3, "token_history": [], "closed_trades": []}

def load(path):
    if os.path.exists(path):
        try: return json.load(open(path))
        except: pass
    json.dump(DEFAULT, open(path, "w"), indent=2); return dict(DEFAULT)

def validate(pos):
    """진입 전 schema 강제. 누락 필드 = 거부."""
    miss = [f for f in REQUIRED if f not in pos or pos.get(f) in (None, "")]
    return {"valid": len(miss) == 0, "missing": miss}

def evaluate(positions, cur_price_fn, budget):
    """Attack sleeve 평가 — 빈슬롯이면 전액 cash, 차면 cost/mkt 분리. budget=A2 NAV * 0.10."""
    deployed = sum(p["shares"] * p["entry_price"] for p in positions)
    mkt = sum(p["shares"] * cur_price_fn(p["ticker"]) for p in positions)
    cash = budget - deployed
    rows = []
    for p in positions:
        cur = cur_price_fn(p["ticker"]); ep = p["entry_price"]
        rows.append({"ticker": p["ticker"], "catalyst": str(p.get("catalyst", ""))[:36], "grade": p.get("grade", "?"),
                     "shares": p["shares"], "entry": ep, "cur": cur, "pnl_pct": (cur/ep-1)*100 if ep else 0.0})
    return {"value": cash + mkt, "pnl": mkt - deployed, "deployed": deployed, "cash": cash, "n": len(positions), "rows": rows}

# ── NEG Gate 차등 (Attack ≠ Moonshot) ──
def neg_gate(ticker, neg_tickers):
    """Attack: Hard NEG여도 완전금지 ❌ → size 0.25~0.5R·overnight 금지·VWAP 이탈 즉시 청산. (Moonshot은 절대금지=moonshot_ledger)"""
    if ticker in neg_tickers:
        return {"allowed": True, "mode": "special-risk", "max_R": 0.5, "overnight": False,
                "note": "Hard NEG·paper/0.25~0.5R·overnight 금지·VWAP 이탈 즉시 청산·물타기 금지"}
    return {"allowed": True, "mode": "normal", "max_R": 1.0, "overnight": True, "note": "NEG 없음"}

# ── 진입 게이트 (catalyst=총알·ORB/VWAP/RVOL/Bollinger=방아쇠) ──
def check_entry(cand, leadership, market_stress):
    blocked = []
    if leadership == "RED": blocked.append("Leadership RED")
    if market_stress == "RED": blocked.append("Market Stress RED")
    if not (cand.get("catalyst") or cand.get("momentum")): blocked.append("catalyst/momentum 없음")
    if not cand.get("rvol_ok"): blocked.append("RVOL 미달")
    if not cand.get("vwap_above"): blocked.append("VWAP 아래")
    if not (cand.get("orb_break") or cand.get("bb_breakout")): blocked.append("ORB/Bollinger 돌파 없음")
    return {"enter": len(blocked) == 0, "blocked": blocked}

# ── Token 회계 (매주 3·A=1·B=0.5·손실 −1·+2R 승리 +1·RED 0) ──
def grade_token(grade): return {"A": 1.0, "B": 0.5}.get(grade, 0.0)
def token_available(d, leadership):
    return 0.0 if leadership == "RED" else float(d.get("weekly_tokens", 3))

# ── 청산 규칙 (−1R / +1R breakeven / +2R 1/3 / +3R Vault / VWAP·ORB 이탈 / 장마감 전) ──
def exit_signal(pos, cur, vwap, orb_low, r_unit):
    pnl_r = (cur - pos["entry_price"]) / r_unit if r_unit else 0
    if cur <= pos.get("stop", 0): return ("-1R 손절", True)
    if vwap and cur < vwap: return ("VWAP 이탈", True)
    if orb_low and cur < orb_low: return ("ORB low 이탈", True)
    if pnl_r >= 3: return ("+3R → 1/3 Vault·나머지 trailing", False)
    if pnl_r >= 2: return ("+2R → 1/3 익절", False)
    if pnl_r >= 1: return ("+1R → stop breakeven", False)
    return ("보유", False)

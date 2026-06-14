#!/usr/bin/env python3
"""PRAMANA A2 — Layer 6 Attack PAPER executor (SSOT v2 §02 L6·spec 07 Attack).

역할: scanner가 만든 attack_candidates.csv 를 읽어 **PAPER 진입/청산을 기록**한다.
  - 매수권 0. 실제 주문 X. '의도된 paper 진입'을 attack.json 에 기록(human gate가 실집행 결정).
  - 진입 게이트: grade A/B + entry gate 통과 + Attack token 보유 + NEG gate 허용.
    → a2_attack_ledger.validate 스키마로 attack.json positions 에 기록 + token 소모(a2_attack_tokens.spend).
  - C/D = paper-watch only(진입 없음).
  - 기존 open position = 현재가(PROXY)로 mark + a2_attack_ledger.exit_signal 청산 판정.
    청산 시 realized P&L → attack_closed_trades.csv (append-only) + token carry 조정.

데이터 정직 라벨:
  - 후보 가격/VWAP/ORB = yfinance 5m PROXY (scanner data_quality=PROXY). 성과 증거 아님.
  - 현재가(mark) = a2_data.benchmarks()/price_panel EOD 우선, 없으면 yfinance EOD = PROXY.
  - catalyst: scanner는 catalyst=False(가격/거래량 momentum proxy). EDGAR catalyst 연결 전.

PAPER only · 자본권한 0 · NO LIVE. 사용: cd phase1a && .venv/bin/python -u engine/a2_attack_executor_paper.py
"""
import os, sys, json, datetime as dt
import pandas as pd, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a2_attack_ledger as al
import a2_attack_tokens as tok
import a2_neg_gate as neg
import a2_risk_dashboard as rd
try:
    import a2_data
except Exception:
    a2_data = None

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
A2 = os.path.join(ROOT, "outputs", "a2_live"); POS = os.path.join(A2, "positions")
CAND_CSV = os.path.join(A2, "attack_candidates.csv")
ATTACK_JSON = os.path.join(POS, "attack.json")
CLOSED_CSV = os.path.join(A2, "attack_closed_trades.csv")
TOK_JSON = os.path.join(POS, "attack_tokens.json")
NAV_CAPITAL = 100_000_000          # 가상 ₩1억 NAV (sizing 근사)
ATTACK_BUDGET_PCT = 0.10           # spec §07 §1: Attack sleeve 기본 10%
R_PCT_PROXY = 0.05                 # 1R = entry의 5% (분봉 stop 부재 시 PROXY)


# ── positions I/O (attack.json: bare list 또는 ledger dict 모두 수용) ──
def load_positions(path=ATTACK_JSON):
    if os.path.exists(path):
        try:
            d = json.load(open(path))
            if isinstance(d, list): return d
            if isinstance(d, dict): return d.get("positions", [])
        except Exception:
            pass
    return []


def save_positions(positions, path=ATTACK_JSON):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(positions, open(path, "w"), indent=2, ensure_ascii=False)


# ── 현재가 (mark) — EOD 우선, PROXY 라벨 ──
def _bench_last(ticker):
    if a2_data is None: return None
    try:
        b = a2_data.benchmarks()
        if ticker in b.columns:
            s = b[ticker].dropna()
            return float(s.iloc[-1]) if len(s) else None
    except Exception:
        pass
    return None


def _panel_last(ticker):
    if a2_data is None: return None
    for uni in ("sp500", "smallmid"):
        try:
            p = a2_data.price_panel(uni, min_date="2024-01-01")
            s = p[p["ticker"] == ticker].sort_values("date")
            if len(s): return float(s["close_adj"].iloc[-1])
        except Exception:
            continue
    return None


def _yf_last(ticker):
    try:
        import yfinance as yf
        h = yf.download(ticker, period="5d", interval="1d", progress=False, auto_adjust=False)
        if len(h):
            c = h["Close"]
            return float(c.iloc[-1].item() if hasattr(c.iloc[-1], "item") else c.iloc[-1])
    except Exception:
        pass
    return None


def current_price(ticker, cand_row=None):
    """EOD mark (PROXY). benchmarks→panel→yfinance→candidate last fallback."""
    for fn in (_bench_last, _panel_last, _yf_last):
        v = fn(ticker)
        if v is not None and v == v and v > 0:
            return v, "EOD_PROXY"
    if cand_row is not None and "last" in cand_row and cand_row["last"] == cand_row["last"]:
        return float(cand_row["last"]), "CAND_LAST_PROXY"
    return float("nan"), "NO_PRICE"


# ── append-only closed trades log ──
def append_closed_trade(rec, path=CLOSED_CSV):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df = pd.DataFrame([rec])
    header = not os.path.exists(path)
    df.to_csv(path, mode="a", header=header, index=False)


# ── 청산 점검 (기존 open positions) ──
def mark_and_exit(positions, today):
    """각 open position을 현재가로 mark, exit_signal로 청산 판정. 청산 = closed_trades 기록·제거.
    반환 (남은 positions, closed list, marks list)."""
    remaining = []; closed = []; marks = []
    for p in positions:
        cur, q = current_price(p["ticker"])
        ep = float(p["entry_price"]); r_unit = abs(ep - float(p.get("stop", ep * (1 - R_PCT_PROXY)))) or ep * R_PCT_PROXY
        # 분봉 VWAP/ORB는 EOD 모드에선 부재 → exit_signal에 None 전달(stop·R 기반·time stop만 평가). 정직 라벨.
        reason, do_exit = al.exit_signal(p, cur, vwap=None, orb_low=None, r_unit=r_unit)
        pnl_pct = (cur / ep - 1.0) if (ep and cur == cur) else 0.0
        pnl_R = (cur - ep) / r_unit if (r_unit and cur == cur) else 0.0
        marks.append({"ticker": p["ticker"], "entry": ep, "cur": round(cur, 2) if cur == cur else None,
                      "pnl_pct": round(pnl_pct * 100, 2), "pnl_R": round(pnl_R, 2),
                      "signal": reason, "quality": q})
        if do_exit:
            rec = {"close_date": str(today), "ticker": p["ticker"], "sleeve": "attack",
                   "shares": p["shares"], "entry_price": ep, "entry_date": p.get("entry_date"),
                   "exit_price": round(cur, 4) if cur == cur else None, "exit_reason": reason,
                   "pnl_pct": round(pnl_pct * 100, 4), "pnl_R": round(pnl_R, 4),
                   "realized_pnl_won": round((cur - ep) * p["shares"], 0) if cur == cur else None,
                   "grade": p.get("grade"), "catalyst": p.get("catalyst"),
                   "data_quality": p.get("data_quality", "PROXY")}
            append_closed_trade(rec)
            closed.append(rec)
        else:
            remaining.append(p)
    return remaining, closed, marks


# ── 신규 진입 (grade A/B·gate·token·NEG) ──
def consider_entries(cands, lead_state, market_stress, neg_df, tok_state, open_tickers, today):
    """grade A/B 후보 → entry gate + token + NEG 통과 시 PAPER 진입 dict 생성. C/D=watch.
    반환 (entries list, watch list, token_state)."""
    entries = []; watch = []
    if cands is None or len(cands) == 0:
        return entries, watch, tok_state
    budget = NAV_CAPITAL * ATTACK_BUDGET_PCT
    for _, c in cands.iterrows():
        t = c["ticker"]; grade = str(c.get("grade", "D"))
        if t in open_tickers:
            continue
        # entry gate (scanner가 enter 계산했지만 재확인 — leadership/market RED·confirmation)
        cand = {"catalyst": bool(c.get("catalyst", False)),
                "momentum": bool(c.get("rvol_ok", False)) and bool(c.get("vwap_above", False)),
                "rvol_ok": bool(c.get("rvol_ok", False)), "vwap_above": bool(c.get("vwap_above", False)),
                "orb_break": bool(c.get("orb_break", False)), "bb_breakout": bool(c.get("bb_breakout", False))}
        e = al.check_entry(cand, lead_state, market_stress)
        ng = neg.gate_attack(t, neg_df)              # severe=paper-only(max_R 0)·soft=0.5R·none=1.0R
        ce = tok.can_enter(tok_state, grade, lead_state)

        if grade in ("C", "D"):
            watch.append({"ticker": t, "grade": grade, "reason": "C/D = paper-watch only(진입 없음)",
                          "entry_gate": e["enter"], "blocked": ";".join(e["blocked"])})
            continue
        # A/B: 모든 게이트 통과해야 진입
        if not e["enter"]:
            watch.append({"ticker": t, "grade": grade, "reason": "entry gate 차단", "blocked": ";".join(e["blocked"])})
            continue
        if not ce["allowed"]:
            watch.append({"ticker": t, "grade": grade, "reason": f"token: {ce['reason']}"})
            continue
        if ng["mode"] == "paper-only" or ng["max_R"] <= 0:
            watch.append({"ticker": t, "grade": grade, "reason": f"NEG: {ng['note']}", "high_risk": ng.get("high_risk")})
            continue
        # ── PAPER 진입 생성 ──
        entry_px = float(c.get("last", float("nan")))
        if not (entry_px == entry_px and entry_px > 0):
            watch.append({"ticker": t, "grade": grade, "reason": "진입가(last) 없음"}); continue
        size_r = {"A": 1.0, "B": 0.5}.get(grade, 0.0)
        size_r = min(size_r, ng["max_R"])            # NEG soft면 0.5R 캡
        # 1R 자본 = budget * (R as % of budget). per-trade risk = budget의 size_r*R_PCT_PROXY 근사.
        risk_won = budget * size_r * R_PCT_PROXY
        stop_px = entry_px * (1 - R_PCT_PROXY)        # stop = entry -1R (PROXY·분봉 ORB low 부재)
        per_share_risk = entry_px - stop_px
        shares = round(risk_won / per_share_risk) if per_share_risk > 0 else 0
        catalyst = "momentum(RVOL+VWAP proxy)" if cand["momentum"] else "price/volume proxy"
        pos = {"ticker": t, "sleeve": "attack", "shares": int(shares), "entry_price": round(entry_px, 4),
               "entry_date": str(today), "stop": round(stop_px, 4), "catalyst": catalyst,
               "grade": grade, "size_r": size_r, "data_quality": str(c.get("data_quality", "PROXY")),
               "neg_mode": ng["mode"], "overnight_ok": bool(ng["overnight"])}
        v = al.validate(pos)
        if not v["valid"]:
            watch.append({"ticker": t, "grade": grade, "reason": f"schema 누락: {v['missing']}"}); continue
        if shares <= 0:
            watch.append({"ticker": t, "grade": grade, "reason": "shares=0(자본/리스크 단위 0)"}); continue
        tok.spend(tok_state, grade)                  # token 소모
        pos["token_cost"] = ce["cost"]
        entries.append(pos)
    return entries, watch, tok_state


def main():
    today = dt.date.today()
    # ── 상태(leadership/market/NEG) ──
    try:
        r = rd.compute()
        lead_state = r["leadership_state"]; market_stress = r["market_stress"]
    except Exception as ex:
        lead_state = "GREEN"; market_stress = "GREEN"
        print(f"⚠ risk dashboard 실패({ex}) → leadership/market GREEN 가정")
    neg_df = neg.neg_events_asof(today, lookback=90)

    # ── 토큰 롤 ──
    tok_state = tok.load(TOK_JSON)
    tok.roll_week(tok_state, lead_state)

    # ── 후보 로드 ──
    cands = pd.read_csv(CAND_CSV) if os.path.exists(CAND_CSV) else pd.DataFrame()
    n_a = int((cands["grade"] == "A").sum()) if len(cands) else 0
    n_b = int((cands["grade"] == "B").sum()) if len(cands) else 0
    n_cd = int(cands["grade"].isin(["C", "D"]).sum()) if len(cands) else 0

    # ── 1) 기존 open positions mark/exit ──
    positions = load_positions()
    positions, closed, marks = mark_and_exit(positions, today)
    for rec in closed:                               # 청산 결과 → token carry 조정
        tok.record_close(tok_state, rec.get("pnl_R"))

    # ── 2) 신규 진입 검토 (grade A/B) ──
    open_tickers = {p["ticker"] for p in positions}
    entries, watch, tok_state = consider_entries(cands, lead_state, market_stress, neg_df,
                                                 tok_state, open_tickers, today)
    positions.extend(entries)

    # ── 저장 ──
    save_positions(positions)
    tok.save(tok_state, TOK_JSON)

    # ── 요약 ──
    print(f"✅ Attack PAPER executor {today} (자본권한 0·실제 주문 X·human gate)")
    print(f"   상태: Leadership {lead_state} · Market Stress {market_stress} · NEG(90d) {neg_df['ticker'].nunique() if len(neg_df) else 0}종 · "
          f"tokens 가용 {tok_state['available']:.1f}")
    print(f"   후보: grade A {n_a} · B {n_b} · C/D {n_cd} (총 {len(cands)})")
    print(f"   기존 포지션 mark: {len(marks)}건 · 청산: {len(closed)}건 · 신규 PAPER 진입: {len(entries)}건")
    for m in marks:
        print(f"     mark {m['ticker']:6} entry {m['entry']} cur {m['cur']} ({m['pnl_pct']:+.1f}%·{m['pnl_R']:+.2f}R) → {m['signal']} [{m['quality']}]")
    for rec in closed:
        print(f"     CLOSE {rec['ticker']:6} {rec['exit_reason']} pnl {rec['pnl_pct']:+.2f}% (₩{rec['realized_pnl_won']}) → {CLOSED_CSV}")
    for e in entries:
        print(f"     ENTER(paper) {e['ticker']:6} {e['grade']}급 {e['shares']}주 @{e['entry_price']} stop {e['stop']} "
              f"size {e['size_r']}R [{e['data_quality']}·NEG {e['neg_mode']}]")
    if not entries:
        why = "후보 grade A/B 없음" if (n_a + n_b == 0) else "A/B 있으나 게이트/토큰/NEG 미통과"
        print(f"   → 신규 진입 0건 (정직): {why}")
    if watch[:8]:
        print("   watch(진입 안함):")
        for w in watch[:8]:
            print(f"     {w['ticker']:6} {w.get('grade','?')}급 — {w['reason']}")
    print(f"   files: {ATTACK_JSON} · {CLOSED_CSV if closed else '(closed 없음)'} · {TOK_JSON}")


if __name__ == "__main__":
    main()

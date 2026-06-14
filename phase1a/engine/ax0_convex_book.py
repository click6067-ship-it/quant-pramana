#!/usr/bin/env python3
"""PRAMANA AX-0 — S1 Long-Convex Catalyst 옵션 paper book (forward·UNVERIFIED).

정본: AX0_Protocol.md. long call(defined-risk) only·보수 fill(ask 매수/bid 청산)·OI/vol/spread floor·no-fill 로그.
signal_quality(기초자산이 맞게 움직였나) vs tradable_option_pnl(체결 가능했나+옵션 P&L) **분리**(R2#3).
heat rails = hard veto(R2#6). 옵션=yfinance 체인(현재 스냅샷·이력 없음)=FORWARD_PAPER_ONLY_UNVERIFIED.
가상 $100k paper(옵션 USD)·자본권한 0·매수권 0(사람 게이트). 사용: python engine/ax0_convex_book.py
"""
import os, sys, json, datetime as dt
import numpy as np, pandas as pd, warnings; warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "outputs", "ax0"); os.makedirs(OUT, exist_ok=True)
CAND = os.path.join(OUT, "candidates.csv"); POSF = os.path.join(OUT, "positions.json")
LEDGER = os.path.join(OUT, "option_ledger.csv"); NOFILL = os.path.join(OUT, "nofill_log.csv")
HEALTH = os.path.join(OUT, "health.json")
NAV = 100_000.0                       # 가상 $100k paper book

# heat rails (Protocol §5·% of NAV) — hard veto
MAX_PREMIUM_PER_TRADE = 0.010         # 1%/trade
MAX_OPEN_PREMIUM = 0.08               # 8% 동시
MAX_SAME_EXPIRY = 0.03                # 3% 동일 만기
MAX_SAME_SECTOR = 3                   # 동일 sector/theme 동시 catalyst 3건(Codex#4)
DAILY_STOP = -0.01                    # 하루 −1% → 당일 신규 금지(Codex#4)
COOLDOWN_DAYS = 5                     # process breach 후 강제 cool-down 거래일(Codex#4)
# 옵션 floors (보수 fill·R2#3)
MIN_OI = 200; MIN_VOL = 20; MAX_SPREAD_PCT = 0.20   # (ask-bid)/mid ≤ 20%
DTE_LO, DTE_HI = 25, 55               # 목표 만기 25~55일
OTM_TARGET = 0.05                     # 약 5% OTM call
TARGET_GAIN = 1.00; STOP_LOSS = -0.50 # +100% 익절 / −50% 손절(premium 기준)


def loadj(p, d):
    if os.path.exists(p):
        try: return json.load(open(p))
        except Exception: pass
    return d

def fetch_chain(tk):
    """yfinance 옵션 체인 → DTE 범위 내 가장 가까운 만기의 calls. 실패=None."""
    import yfinance as yf
    o = yf.Ticker(tk)
    try: spot = float(o.fast_info["last_price"])
    except Exception:
        h = o.history(period="1d"); spot = float(h["Close"].iloc[-1]) if len(h) else None
    if not spot: return None
    exps = o.options or []
    today = dt.date.today(); best = None
    for e in exps:
        dte = (pd.Timestamp(e).date() - today).days
        if DTE_LO <= dte <= DTE_HI: best = (e, dte); break
    if not best: return None
    exp, dte = best
    try: calls = o.option_chain(exp).calls
    except Exception: return None
    return {"spot": spot, "exp": exp, "dte": dte, "calls": calls}

def pick_call(ch):
    """약 5% OTM call·floors 통과하는 것. 반환 dict or {'nofill':reason}."""
    spot = ch["spot"]; target = spot * (1 + OTM_TARGET); calls = ch["calls"]
    calls = calls.assign(dist=(calls["strike"] - target).abs()).sort_values("dist")
    for _, r in calls.iterrows():
        bid = float(r.get("bid", 0) or 0); ask = float(r.get("ask", 0) or 0)
        oi = float(r.get("openInterest", 0) or 0); vol = float(r.get("volume", 0) or 0)
        if ask <= 0 or bid <= 0: continue
        mid = (bid + ask) / 2; spread = (ask - bid) / mid if mid > 0 else 9
        if oi < MIN_OI or vol < MIN_VOL: continue
        if spread > MAX_SPREAD_PCT: continue
        return {"strike": float(r["strike"]), "bid": bid, "ask": ask, "oi": oi, "vol": vol,
                "spread_pct": round(spread, 3), "iv": float(r.get("impliedVolatility", np.nan) or np.nan)}
    return {"nofill": "floors 미통과(OI/vol/spread) 또는 bid/ask 없음"}

def mark_positions(positions):
    """기존 open 포지션 forward mark(보수=bid 청산가) + 청산 판정."""
    import yfinance as yf
    events = []
    for p in positions:
        if p["status"] != "OPEN": continue
        mark_stale = False
        try:
            calls = yf.Ticker(p["ticker"]).option_chain(p["exp"]).calls
            row = calls[calls["strike"] == p["strike"]]
            bid = float(row["bid"].iloc[0]) if len(row) else None
            if bid is None or bid <= 0: raise ValueError("no bid")
        except Exception:
            # ★ Codex#6: 마크 실패 시 보수적 — 직전 mark 유지 X. min(last_mark, intrinsic) 또는 0·stale 플래그.
            intrinsic = max(0.0, float(p.get("last_spot", p["spot_at_entry"])) - p["strike"])
            bid = min(p.get("last_mark", p["entry_ask"]), intrinsic); mark_stale = True
        p["last_mark"] = bid; p["mark_stale"] = mark_stale
        pnl_pct = (bid - p["entry_ask"]) / p["entry_ask"] if p["entry_ask"] else 0.0
        p["pnl_pct"] = round(pnl_pct, 3)
        dte_left = (pd.Timestamp(p["exp"]).date() - dt.date.today()).days
        reason = None
        if pnl_pct >= TARGET_GAIN: reason = f"+{TARGET_GAIN*100:.0f}% 익절"
        elif pnl_pct <= STOP_LOSS: reason = f"{STOP_LOSS*100:.0f}% 손절"
        elif dte_left <= 5: reason = "만기 임박 time stop"
        if reason:
            p["status"] = "CLOSED"; p["exit_mark"] = bid; p["exit_reason"] = reason; p["exit_date"] = str(dt.date.today())
            events.append({"date": str(dt.date.today()), "event": "CLOSE", "ticker": p["ticker"], "strike": p["strike"],
                           "exp": p["exp"], "tradable_pnl_pct": p["pnl_pct"], "reason": reason})
    return events

def main():
    today = str(dt.date.today())
    pos = loadj(POSF, {"positions": [], "inception": today})
    positions = pos["positions"]
    # 1) 기존 포지션 mark + 청산
    close_events = mark_positions(positions)
    # 2) 신규: momentum 확인된 최근 후보
    open_prem = sum(p["entry_ask"] * 100 / NAV for p in positions if p["status"] == "OPEN")
    by_expiry = {}
    for p in positions:
        if p["status"] == "OPEN": by_expiry[p["exp"]] = by_expiry.get(p["exp"], 0) + p["entry_ask"] * 100 / NAV
    new_events = []; nofills = []
    # ★ Codex#4: daily-stop + cooldown 게이트. 오늘 청산 P&L 합 < −1% → 당일 신규 금지 + cooldown.
    today_pnl = sum(e.get("tradable_pnl_pct", 0) * 0.01 for e in close_events)   # 대략 NAV 기준(per-trade 1% 노출)
    cooldown_until = pos.get("cooldown_until")
    in_cooldown = bool(cooldown_until and today <= cooldown_until)
    if today_pnl < DAILY_STOP and not in_cooldown:
        # cooldown 설정(거래일 근사 = 캘린더 +7일·주말 포함 보수)
        pos["cooldown_until"] = str((pd.Timestamp(today) + pd.Timedelta(days=COOLDOWN_DAYS + 2)).date()); in_cooldown = True
    # sector lookup(상관 catalyst cap)
    try:
        import a2_data; meta = a2_data.tickers_meta()
    except Exception:
        meta = None
    def sector_of(t):
        try: return str(meta.loc[t, "sector"]) if (meta is not None and t in meta.index) else "?"
        except Exception: return "?"
    open_by_sector = {}
    for p in positions:
        if p["status"] == "OPEN": s = p.get("sector", "?"); open_by_sector[s] = open_by_sector.get(s, 0) + 1
    if os.path.exists(CAND) and not in_cooldown:
        cand = pd.read_csv(CAND)
        cand = cand[(cand["run_date"] == today) & (cand.get("momentum_ok", False) == True)] if "momentum_ok" in cand else cand.iloc[0:0]
        held = {p["ticker"] for p in positions if p["status"] == "OPEN"}
        for _, c in cand.iterrows():
            t = c["ticker"]
            if t in held: continue
            sec = sector_of(t)
            if open_by_sector.get(sec, 0) >= MAX_SAME_SECTOR:
                nofills.append({"date": today, "ticker": t, "reason": f"sector {sec} 동시 catalyst {MAX_SAME_SECTOR} veto"}); continue
            ch = fetch_chain(t)
            if not ch: nofills.append({"date": today, "ticker": t, "reason": "DTE 범위 내 만기/체인 없음"}); continue
            pk = pick_call(ch)
            if "nofill" in pk: nofills.append({"date": today, "ticker": t, "reason": pk["nofill"]}); continue
            prem = pk["ask"] * 100 / NAV   # 1 contract premium as % NAV (보수=ask 매수)
            # heat rails (hard veto)
            if prem > MAX_PREMIUM_PER_TRADE: nofills.append({"date": today, "ticker": t, "reason": f"premium {prem*100:.1f}%>1% veto"}); continue
            if open_prem + prem > MAX_OPEN_PREMIUM: nofills.append({"date": today, "ticker": t, "reason": "open premium 8% veto"}); continue
            if by_expiry.get(ch["exp"], 0) + prem > MAX_SAME_EXPIRY: nofills.append({"date": today, "ticker": t, "reason": "same-expiry 3% veto"}); continue
            p = {"ticker": t, "status": "OPEN", "type": "long_call", "entry_date": today,
                 "candidate_id": c.get("candidate_id"), "available_at": str(c.get("available_at", "")), "sector": sec,
                 "spot_at_entry": ch["spot"], "last_spot": ch["spot"], "strike": pk["strike"], "exp": ch["exp"], "dte_at_entry": ch["dte"],
                 "entry_ask": pk["ask"], "oi": pk["oi"], "vol": pk["vol"], "spread_pct": pk["spread_pct"],
                 "iv": round(pk["iv"], 3) if pk["iv"]==pk["iv"] else None, "last_mark": pk["bid"], "pnl_pct": 0.0,
                 "catalyst": c.get("catalyst", ""), "signal_quality_ref_spot": ch["spot"],
                 "data_quality": "FORWARD_PAPER_ONLY_UNVERIFIED"}
            positions.append(p); open_prem += prem; by_expiry[ch["exp"]] = by_expiry.get(ch["exp"], 0) + prem
            open_by_sector[sec] = open_by_sector.get(sec, 0) + 1
            new_events.append({"date": today, "event": "OPEN", "ticker": t, "strike": pk["strike"], "exp": ch["exp"],
                               "entry_ask": pk["ask"], "premium_pct_nav": round(prem, 4), "spread_pct": pk["spread_pct"]})
    # 3) persist (append-only ledger + positions)
    pos["positions"] = positions; json.dump(pos, open(POSF, "w"), indent=2, ensure_ascii=False)
    allev = close_events + new_events
    if allev: pd.DataFrame(allev).to_csv(LEDGER, mode="a", header=not os.path.exists(LEDGER), index=False)
    if nofills: pd.DataFrame(nofills).to_csv(NOFILL, mode="a", header=not os.path.exists(NOFILL), index=False)
    n_open = sum(1 for p in positions if p["status"] == "OPEN"); n_closed = sum(1 for p in positions if p["status"] == "CLOSED")
    json.dump({"ok": True, "as_of": today, "open": n_open, "closed": n_closed, "open_premium_pct": round(open_prem, 4)},
              open(HEALTH, "w"))
    print(f"✅ AX-0 S1 long-convex {today}: OPEN {n_open}·CLOSED {n_closed}·신규 {len(new_events)}·청산 {len(close_events)}·no-fill {len(nofills)}")
    print(f"   open premium {open_prem*100:.1f}% (cap 8%)·heat rails hard-veto 적용·FORWARD_PAPER_ONLY_UNVERIFIED·매수권 0")
    if nofills: print(f"   no-fill 사유 예: {nofills[0]['ticker']} — {nofills[0]['reason']}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""PRAMANA monitor — ALWAYS-ON monitoring + kill-switch + governance layer.

This sits ABOVE the per-rebalance veto in risk_engine.py (which is untouched):
risk_engine.kill_check vetoes a *single* rebalance; this module watches the live
PAPER book every day, latches operational kill levels, and gates capital promotion.

Book under watch: aggressive market-neutral US equity L/S PAPER book — virtual ₩100M,
vol-target 25%, max leverage 4x, measured net Sharpe ~0.33, market beta ~-0.14.

PRINCIPLE: LLM off-path advisory only; deterministic rules trigger kill; human gates capital.
  - MONITOR + KILL-SWITCH are pure deterministic functions of the state dict. No model,
    no AI, no network is on the trigger path.
  - FAIL-CLOSED: a missing/None/NaN metric is treated as a BREACH (CRIT/STALE), never OK.
    Silence is never safety.
  - Data integrity uses data.validate() (recompute hashes vs HASHES.txt). API stays off.
  - Capital promotion (paper->live) needs deterministic gate PASS *and* a human sign-off
    recorded in the governance_log; AI advice in that log is explicitly non-binding.

State dict (produced by the book/runner; see book_runner.py for the upstream numbers):
  {date, nav, peak_nav, realized_vol(20d ann), gross_leverage, net_exposure,
   beta_60d, corr_60d, max_name_gross, max_sector_net, turnover, bt_turnover_median,
   borrow_cost, modeled_borrow_cost, ic_ir_60d, ic_ir_120d, bt_ic_ir,
   data_age_days, monitor_ran}.  Missing keys => fail-closed breach.
"""
import contextlib
import io
import math
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import data  # noqa: E402  (data.validate(): recompute hashes vs HASHES.txt -> (report, ok))

# ── book constants (aggressive paper book) ──────────────────────────────────
TARGET_VOL = 0.25
MAX_DATA_AGE_DAYS = 3          # > this many days stale => STALE/breach
WARN_ESCALATE_N = 3           # >=3 simultaneous WARNs => escalate whole day to CRIT
LEVELS = ("OK", "WARN", "CRIT", "STALE")
_LEVEL_RANK = {"OK": 0, "STALE": 1, "WARN": 2, "CRIT": 3}   # for "worst level" math

KILL_LEVELS = ("NONE", "L1_REDUCE", "L2_HALT", "L3_FLAT", "L4_SHUTDOWN")
_KILL_RANK = {lvl: i for i, lvl in enumerate(KILL_LEVELS)}
DD_COOLDOWN_DAYS = 10         # K2: no immediate re-risk after a drawdown kill


# ── small helpers ───────────────────────────────────────────────────────────
def _missing(x):
    """Fail-closed test: None or NaN counts as a missing metric (=> breach)."""
    return x is None or (isinstance(x, float) and math.isnan(x))


def _row(date, metric, value, warn, crit, level):
    return {"date": date, "metric": metric, "value": value,
            "warn": warn, "crit": crit, "level": level}


def _band(value, *, warn_pred, crit_pred):
    """Classify a present value: CRIT if crit_pred, else WARN if warn_pred, else OK.
    crit is checked first so the worst applicable band wins."""
    if crit_pred(value):
        return "CRIT"
    if warn_pred(value):
        return "WARN"
    return "OK"


def _drawdown(state):
    """Trailing drawdown = nav/peak_nav - 1 (<=0). Fail-closed if inputs missing."""
    nav, peak = state.get("nav"), state.get("peak_nav")
    if _missing(nav) or _missing(peak) or peak <= 0:
        return None
    return nav / peak - 1.0


# ── 1) MONITOR ──────────────────────────────────────────────────────────────
def monitor_day(state):
    """Produce one row per metric: {date, metric, value, warn, crit, level}.

    Deterministic + fail-closed: any metric whose input is missing/NaN is reported
    as CRIT (or STALE for data freshness) with value=None — a gap is a breach.
    Rule: >=3 simultaneous WARNs across metrics escalate *every* WARN row to CRIT.
    """
    date = state.get("date")
    rows = []

    def add(metric, value, warn, crit, *, crit_pred=None, warn_pred=None,
            stale=False):
        """Append a classified row; missing value => STALE if stale else CRIT."""
        if _missing(value):
            rows.append(_row(date, metric, None, warn, crit,
                             "STALE" if stale else "CRIT"))
            return
        lvl = _band(value, warn_pred=warn_pred, crit_pred=crit_pred)
        rows.append(_row(date, metric, value, warn, crit, lvl))

    # drawdown: WARN<=-8%, CRIT<=-12% (hard -18% handled by kill-switch K2)
    dd = _drawdown(state)
    add("drawdown", dd, "-8%", "-12% (hard -18%)",
        crit_pred=lambda v: v <= -0.12, warn_pred=lambda v: v <= -0.08)

    # realized_vol(20d ann) vs 25% target: WARN <15% or >32%, CRIT >40%
    add("realized_vol", state.get("realized_vol"), "<15% or >32%", ">40%",
        crit_pred=lambda v: v > 0.40,
        warn_pred=lambda v: v < 0.15 or v > 0.32)

    # gross_leverage: WARN>3.4x, CRIT>4.0x
    add("gross_leverage", state.get("gross_leverage"), ">3.4x", ">4.0x",
        crit_pred=lambda v: v > 4.0, warn_pred=lambda v: v > 3.4)

    # net_exposure (|net|/NAV): WARN>8%, CRIT>15%
    ne = state.get("net_exposure")
    if not _missing(ne):
        ne = abs(ne)
    add("net_exposure", ne, ">8%", ">15%",
        crit_pred=lambda v: v > 0.15, warn_pred=lambda v: v > 0.08)

    # market beta (60d to SPY): WARN |b|>0.25, CRIT |b|>0.40
    b = state.get("beta_60d")
    if not _missing(b):
        b = abs(b)
    add("beta_60d", b, "|b|>0.25", "|b|>0.40",
        crit_pred=lambda v: v > 0.40, warn_pred=lambda v: v > 0.25)

    # market corr (60d to SPY): WARN |r|>0.30, CRIT |r|>0.50
    r = state.get("corr_60d")
    if not _missing(r):
        r = abs(r)
    add("corr_60d", r, "|r|>0.30", "|r|>0.50",
        crit_pred=lambda v: v > 0.50, warn_pred=lambda v: v > 0.30)

    # name concentration: WARN>4%, CRIT>6% gross
    add("name_concentration", state.get("max_name_gross"), ">4%", ">6%",
        crit_pred=lambda v: v > 0.06, warn_pred=lambda v: v > 0.04)

    # sector net concentration: WARN>6%, CRIT>12%
    sn = state.get("max_sector_net")
    if not _missing(sn):
        sn = abs(sn)
    add("sector_net_concentration", sn, ">6%", ">12%",
        crit_pred=lambda v: v > 0.12, warn_pred=lambda v: v > 0.06)

    # turnover vs backtest median: WARN>1.3x, CRIT>2x
    to, to_med = state.get("turnover"), state.get("bt_turnover_median")
    to_ratio = None if (_missing(to) or _missing(to_med) or to_med <= 0) else to / to_med
    add("turnover_ratio", to_ratio, ">1.3x", ">2.0x",
        crit_pred=lambda v: v > 2.0, warn_pred=lambda v: v > 1.3)

    # borrow cost drift vs modeled: WARN>1.5x, CRIT>2.5x
    bc, bc_mod = state.get("borrow_cost"), state.get("modeled_borrow_cost")
    bc_ratio = None if (_missing(bc) or _missing(bc_mod) or bc_mod <= 0) else bc / bc_mod
    add("borrow_cost_drift", bc_ratio, ">1.5x", ">2.5x",
        crit_pred=lambda v: v > 2.5, warn_pred=lambda v: v > 1.5)

    # signal IC-IR (60d/120d) vs backtest: WARN<0.5x, CRIT<0.2x (worst of the two)
    bt_icir = state.get("bt_ic_ir")
    ic60, ic120 = state.get("ic_ir_60d"), state.get("ic_ir_120d")
    if _missing(bt_icir) or bt_icir <= 0 or (_missing(ic60) and _missing(ic120)):
        icir_ratio = None
    else:
        present = [v for v in (ic60, ic120) if not _missing(v)]
        icir_ratio = min(present) / bt_icir   # worst (lowest) realized vs backtest
    add("ic_ir_ratio", icir_ratio, "<0.5x", "<0.2x",
        crit_pred=lambda v: v < 0.2, warn_pred=lambda v: v < 0.5)

    # data freshness/integrity: STALE on staleness, CRIT on hash mismatch.
    rows.append(_data_integrity_row(state, date))

    # Escalation: >=3 simultaneous WARNs -> escalate every WARN row to CRIT.
    if sum(1 for x in rows if x["level"] == "WARN") >= WARN_ESCALATE_N:
        for x in rows:
            if x["level"] == "WARN":
                x["level"] = "CRIT"
                x["escalated"] = "3+WARN->CRIT"
    return rows


def _data_integrity_row(state, date):
    """One row capturing both staleness and on-disk hash integrity (fail-closed).

    - data_age_days missing or > MAX_DATA_AGE_DAYS  -> STALE (breach).
    - data.validate() hash mismatch (ok=False)      -> CRIT.
    Hash check is recompute-only (no API); skip it cleanly if no HASHES.txt baseline
    exists so a fresh checkout doesn't false-alarm, but staleness still applies.
    """
    age = state.get("data_age_days")
    if _missing(age) or age > MAX_DATA_AGE_DAYS:
        return _row(date, "data_integrity", age, f"stale>{MAX_DATA_AGE_DAYS}d",
                    "hash_mismatch", "STALE")
    try:
        with contextlib.redirect_stdout(io.StringIO()):   # validate() is chatty; keep monitor logs clean
            rep, ok = data.validate()
        n_mismatch = len(rep.get("mismatched", [])) if isinstance(rep, dict) else 0
    except Exception as e:                          # fail-closed: can't verify => breach
        return _row(date, "data_integrity", f"validate_error:{type(e).__name__}",
                    f"stale>{MAX_DATA_AGE_DAYS}d", "hash_mismatch", "CRIT")
    if not ok:
        return _row(date, "data_integrity", f"hash_mismatch x{n_mismatch}",
                    f"stale>{MAX_DATA_AGE_DAYS}d", "hash_mismatch", "CRIT")
    return _row(date, "data_integrity", f"fresh<= {MAX_DATA_AGE_DAYS}d, hashes_ok",
                f"stale>{MAX_DATA_AGE_DAYS}d", "hash_mismatch", "OK")


# ── 2) KILL-SWITCH ──────────────────────────────────────────────────────────
def _kill(level, kill_type, reason, *, cooldown_left=0, rearm_requires_human=False):
    return {"level": level, "kill_type": kill_type, "reason": reason,
            "cooldown_left": cooldown_left, "rearm_requires_human": rearm_requires_human}


def kill_switch(state, monitor_rows, prev_kill_state=None):
    """Deterministic, latching operational kill-switch over the monitor output.

    Triggers (highest active level wins; K1 data-integrity supersedes all):
      K1 data_integrity : hash mismatch / stale         -> L3_FLAT, human re-arm.
      K2 drawdown       : -12->L1, -15->L2, -18->L3      ; cooldown>=10d, no immediate re-risk.
      K3 vol_explosion  : >40% ->L1, >50% ->L2.
      K4 correlation_breakdown : 60d |beta|>0.40 or |rho|>0.50 -> L2 + reduce.
      K5 model_decay    : 120d IC-IR < 0.2x backtest     -> L2, human-only re-arm.
    Heartbeat: state['monitor_ran'] == False (or missing) -> auto L2_HALT.

    Latching: the result is at least as severe as prev_kill_state['level'] (a kill
    does not silently clear); cooldown ticks down each day; rearm_requires_human stays
    sticky once any human-gated kill (K1/K2/K5) has fired and hasn't been cleared by a human.
    """
    prev = prev_kill_state or _kill("NONE", None, "init")
    rows_by_metric = {r["metric"]: r for r in (monitor_rows or [])}
    candidates = []   # list of kill dicts; we take the most severe

    # K1 — data integrity (SUPERSEDES). Treat missing row as breach (fail-closed).
    di = rows_by_metric.get("data_integrity")
    if di is None or di["level"] in ("CRIT", "STALE"):
        why = "monitor missing data_integrity row" if di is None else di["value"]
        return _finalize(
            _kill("L3_FLAT", "K1_data_integrity",
                  f"data integrity breach ({why}) -> FLATTEN, human re-arm",
                  rearm_requires_human=True),
            prev, superseding=True)

    # K2 — drawdown ladder (human re-arm, cooldown >= 10d, no immediate re-risk).
    dd = _drawdown(state)
    if _missing(dd):                                # fail-closed: can't measure DD
        candidates.append(_kill("L3_FLAT", "K2_drawdown",
                                "drawdown unmeasurable (nav/peak missing) -> FLATTEN",
                                cooldown_left=DD_COOLDOWN_DAYS, rearm_requires_human=True))
    elif dd <= -0.18:
        candidates.append(_kill("L3_FLAT", "K2_drawdown",
                                f"DD {dd:+.1%} <= -18% (hard) -> FLATTEN",
                                cooldown_left=DD_COOLDOWN_DAYS, rearm_requires_human=True))
    elif dd <= -0.15:
        candidates.append(_kill("L2_HALT", "K2_drawdown",
                                f"DD {dd:+.1%} <= -15% -> HALT new risk",
                                cooldown_left=DD_COOLDOWN_DAYS, rearm_requires_human=True))
    elif dd <= -0.12:
        candidates.append(_kill("L1_REDUCE", "K2_drawdown",
                                f"DD {dd:+.1%} <= -12% -> REDUCE gross",
                                cooldown_left=DD_COOLDOWN_DAYS, rearm_requires_human=True))

    # K3 — vol explosion (>40% L1, >50% L2). Fail-closed if realized_vol missing.
    rv = state.get("realized_vol")
    if _missing(rv):
        candidates.append(_kill("L2_HALT", "K3_vol_explosion",
                                "realized_vol missing -> HALT (fail-closed)"))
    elif rv > 0.50:
        candidates.append(_kill("L2_HALT", "K3_vol_explosion",
                                f"realized vol {rv:.0%} > 50% -> HALT"))
    elif rv > 0.40:
        candidates.append(_kill("L1_REDUCE", "K3_vol_explosion",
                                f"realized vol {rv:.0%} > 40% -> REDUCE"))

    # K4 — correlation breakdown (60d |beta|>0.40 or |rho|>0.50 -> L2 + reduce).
    b, rho = state.get("beta_60d"), state.get("corr_60d")
    if _missing(b) or _missing(rho):
        candidates.append(_kill("L2_HALT", "K4_correlation_breakdown",
                                "beta/corr missing -> HALT (market-neutrality unverifiable)"))
    elif abs(b) > 0.40 or abs(rho) > 0.50:
        candidates.append(_kill("L2_HALT", "K4_correlation_breakdown",
                                f"|beta|={abs(b):.2f} |rho|={abs(rho):.2f} breach -> HALT + reduce"))

    # K5 — model decay (120d IC-IR < 0.2x backtest -> L2, human-only re-arm).
    icir, bt = state.get("ic_ir_120d"), state.get("bt_ic_ir")
    if _missing(icir) or _missing(bt) or bt <= 0:
        candidates.append(_kill("L2_HALT", "K5_model_decay",
                                "IC-IR(120d)/backtest unverifiable -> HALT (fail-closed)",
                                rearm_requires_human=True))
    elif icir < 0.2 * bt:
        candidates.append(_kill("L2_HALT", "K5_model_decay",
                                f"IC-IR(120d) {icir:.3f} < 0.2x backtest {bt:.3f} -> HALT, human re-arm",
                                rearm_requires_human=True))

    # Heartbeat — monitor didn't run (or flag missing) -> auto HALT.
    if state.get("monitor_ran") is not True:
        candidates.append(_kill("L2_HALT", "K6_heartbeat",
                                "monitor_ran != True -> auto HALT (heartbeat lost)"))

    if not candidates:
        candidates.append(_kill("NONE", None, "all clear"))

    # highest active level wins (ties -> first added, which is K2>K3>K4>K5>heartbeat order)
    winner = max(candidates, key=lambda k: (_KILL_RANK[k["level"]],
                                            -candidates.index(k)))
    return _finalize(winner, prev)


def _finalize(current, prev, superseding=False):
    """Apply latching + cooldown decay against the previous kill state.

    - Latch: never report a level *below* the previous one unless a human cleared it
      (modeled by prev['rearm_requires_human'] == False AND prev level was human-gated).
      In this deterministic core we simply keep the max(prev, current) level so a kill
      cannot silently downgrade; a human clears it by passing prev_kill_state=NONE.
    - Cooldown: if previous had cooldown_left>0, tick it down and don't drop below it.
    - rearm_requires_human stays sticky if either side requires it.
    """
    if superseding:                                # K1 always wins outright
        current["rearm_requires_human"] = True
        return current

    prev_rank = _KILL_RANK.get(prev.get("level", "NONE"), 0)
    cur_rank = _KILL_RANK.get(current["level"], 0)

    # Cooldown is a strictly-decrementing countdown timer (NOT a latched floor):
    # yesterday's remaining ticks down by one, but a fresh kill today re-arms it to
    # the larger of (decayed-prev, today's freshly-computed cooldown). This guarantees
    # the timer reaches 0 once the breach clears, enabling (human) re-arm.
    cooldown = max(max(0, int(prev.get("cooldown_left", 0)) - 1),
                   int(current.get("cooldown_left", 0)))

    # Latch the LEVEL upward: keep the more severe of prev/current so a kill cannot
    # silently downgrade. A human clears it by passing prev_kill_state=NONE.
    if prev_rank > cur_rank:
        result = dict(prev)
        result["reason"] = f"LATCHED@{prev['level']} (today computed {current['level']}: {current['reason']})"
        result["kill_type"] = prev.get("kill_type")
    else:
        result = current
    result["cooldown_left"] = cooldown

    # Sticky human re-arm.
    result["rearm_requires_human"] = bool(
        result.get("rearm_requires_human") or prev.get("rearm_requires_human"))

    # While a positive cooldown remains, never sit at NONE — hold at least L1_REDUCE
    # (K2 rule: "no immediate re-risk").
    if result["cooldown_left"] > 0 and _KILL_RANK[result["level"]] == 0:
        result["level"] = "L1_REDUCE"
        result["reason"] = f"cooldown {result['cooldown_left']}d remaining -> no immediate re-risk"
    return result


# ── 3) GOVERNANCE ───────────────────────────────────────────────────────────
# Strict paper->live promotion gate. Deterministic PASS is necessary but NOT
# sufficient: a human still signs off (governance_log) before capital moves.
PROMOTION_GATE = {
    "min_oos_months": 12,        # live-paper out-of-sample track
    "min_live_sharpe": 0.8,      # current book is 0.33 -> must FAIL
    "max_dd": 0.15,              # maxDD must be <= 15%
    "stress_cost_mult": 2.0,     # survives 2x cost ...
    "min_stress_sharpe": 0.5,    # ... with Sharpe >= 0.5
    "max_critical_integrity_events": 0,  # zero CRITICAL integrity events
    "min_capacity_mult": 5.0,    # capacity >= 5x deployed book
}


def promotion_gate(track):
    """STRICT paper->live gate. Returns {eligible: bool, fails: [..]}.

    Deterministic + fail-closed: any missing/None/NaN field is itself a FAIL, so an
    under-evidenced track can never be promoted. Designed to return eligible=False for
    the current book (live Sharpe 0.33 < 0.8).
    """
    g = PROMOTION_GATE
    fails = []

    def need(key, ok_pred, msg):
        v = track.get(key)
        if _missing(v):
            fails.append(f"{key}: MISSING (fail-closed) — need {msg}")
        elif not ok_pred(v):
            fails.append(f"{key}={v}: {msg}")

    need("oos_months", lambda v: v >= g["min_oos_months"],
         f">= {g['min_oos_months']} months live-paper OOS")
    need("live_sharpe", lambda v: v >= g["min_live_sharpe"],
         f"live Sharpe >= {g['min_live_sharpe']}")
    need("max_dd", lambda v: abs(v) <= g["max_dd"],
         f"maxDD <= {g['max_dd']:.0%}")
    need("stress_2x_cost_sharpe", lambda v: v >= g["min_stress_sharpe"],
         f"Sharpe >= {g['min_stress_sharpe']} under {g['stress_cost_mult']:.0f}x cost")
    need("critical_integrity_events",
         lambda v: v <= g["max_critical_integrity_events"],
         f"<= {g['max_critical_integrity_events']} CRITICAL integrity events")
    need("capacity_mult", lambda v: v >= g["min_capacity_mult"],
         f"capacity >= {g['min_capacity_mult']:.0f}x deployed book")

    return {"eligible": len(fails) == 0, "fails": fails}


def governance_log(*, record_id, type, trigger, evidence,
                   deterministic_checks_passed, ai_advisory=None,
                   approver=None, decision="PENDING", ts=None):
    """Schema for a human sign-off record. Capital decisions are HUMAN-gated;
    `ai_advisory` is explicitly non-binding (advisory-only, off the trigger path).

    type     : e.g. 'promotion' | 'rearm' | 'override' | 'incident'
    decision : 'APPROVED' | 'REJECTED' | 'PENDING'
    """
    return {
        "record_id": record_id,
        "ts": ts or datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "type": type,
        "trigger": trigger,
        "evidence": evidence,
        "deterministic_checks_passed": bool(deterministic_checks_passed),
        "ai_advisory": ai_advisory,           # NON-BINDING advisory text/dict
        "ai_advisory_binding": False,         # invariant: AI never gates capital
        "approver": approver,                 # human identity; None until signed
        "decision": decision,
    }


# ── smoke test (synthetic state; deterministic; no API needed beyond hash recompute) ──
def _ok_state():
    """A clean, in-bounds day for the aggressive paper book."""
    return dict(
        date="2026-06-11", nav=101.0, peak_nav=102.0, realized_vol=0.26,
        gross_leverage=3.0, net_exposure=0.03, beta_60d=-0.14, corr_60d=-0.10,
        max_name_gross=0.025, max_sector_net=0.04, turnover=1.0, bt_turnover_median=1.0,
        borrow_cost=0.005, modeled_borrow_cost=0.005, ic_ir_60d=0.30, ic_ir_120d=0.30,
        bt_ic_ir=0.33, data_age_days=0, monitor_ran=True)


def _smoke():
    print("=" * 80)
    print("PRAMANA monitor.py — SMOKE TEST (synthetic state; deterministic)")
    print("=" * 80)
    results = []

    def check(name, cond):
        results.append((name, cond))
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")

    # (1) data-integrity hash-mismatch -> K1 L3_FLAT.
    # Force the hash-mismatch branch deterministically (don't depend on disk state):
    s1 = _ok_state()
    rows1 = monitor_day(s1)
    di = next(r for r in rows1 if r["metric"] == "data_integrity")
    di_forced = dict(di, level="CRIT", value="hash_mismatch x1")   # simulate validate() fail
    rows1_forced = [di_forced if r["metric"] == "data_integrity" else r for r in rows1]
    k1 = kill_switch(s1, rows1_forced)
    check("(1) data-integrity hash-mismatch -> K1 L3_FLAT + human re-arm",
          k1["level"] == "L3_FLAT" and k1["kill_type"] == "K1_data_integrity"
          and k1["rearm_requires_human"] is True)
    print(f"        -> {k1['level']} / {k1['kill_type']} / rearm_human={k1['rearm_requires_human']}")

    # (2) drawdown -15% -> K2 L2+ (at least L2_HALT).
    s2 = _ok_state(); s2.update(nav=85.0, peak_nav=100.0)   # -15.0% drawdown
    rows2 = monitor_day(s2)
    k2 = kill_switch(s2, rows2)
    check("(2) drawdown -15% -> K2 >= L2_HALT + cooldown>=10d",
          _KILL_RANK[k2["level"]] >= _KILL_RANK["L2_HALT"]
          and k2["kill_type"] == "K2_drawdown" and k2["cooldown_left"] >= DD_COOLDOWN_DAYS)
    dd_row = next(r for r in rows2 if r["metric"] == "drawdown")
    print(f"        -> dd_row.level={dd_row['level']} | kill={k2['level']} / {k2['kill_type']} / cooldown={k2['cooldown_left']}")

    # (3) >=3 simultaneous WARNs -> CRIT escalation.
    # Build a day with exactly-WARN (not CRIT) values on >=3 metrics, everything else OK.
    s3 = _ok_state()
    s3.update(
        gross_leverage=3.5,                 # WARN >3.4x (not >4.0x)
        net_exposure=0.10,                  # WARN >8% (not >15%)
        max_name_gross=0.05,                # WARN >4% (not >6%)
    )
    rows3 = monitor_day(s3)
    warn_metrics = [r["metric"] for r in rows3 if r.get("escalated") == "3+WARN->CRIT"]
    none_left_warn = all(r["level"] != "WARN" for r in rows3)
    check("(3) >=3 simultaneous WARN -> all escalated to CRIT",
          len(warn_metrics) >= 3 and none_left_warn)
    print(f"        -> escalated {len(warn_metrics)} rows {warn_metrics}; remaining WARN rows = {sum(1 for r in rows3 if r['level']=='WARN')}")

    # (4) promotion_gate FAILS for Sharpe 0.33 (current book).
    track = dict(oos_months=14, live_sharpe=0.33, max_dd=0.16,
                 stress_2x_cost_sharpe=0.20, critical_integrity_events=0,
                 capacity_mult=6.0)
    pg = promotion_gate(track)
    sharpe_failed = any("live_sharpe" in f for f in pg["fails"])
    check("(4) promotion_gate FAILS for current book (Sharpe 0.33)",
          pg["eligible"] is False and sharpe_failed)
    print(f"        -> eligible={pg['eligible']}; fails={pg['fails']}")

    # (5) heartbeat False -> L2 HALT.
    s5 = _ok_state(); s5["monitor_ran"] = False
    rows5 = monitor_day(s5)   # monitor still computable; the heartbeat flag is what trips it
    k5 = kill_switch(s5, rows5)
    check("(5) heartbeat monitor_ran=False -> >= L2_HALT",
          _KILL_RANK[k5["level"]] >= _KILL_RANK["L2_HALT"]
          and k5["kill_type"] in ("K6_heartbeat", "K2_drawdown", "K3_vol_explosion",
                                  "K4_correlation_breakdown", "K5_model_decay"))
    check("(5b) heartbeat trips on the OK book purely from monitor_ran=False",
          kill_switch(_ok_state(), monitor_day(_ok_state()))["level"] == "NONE"
          and k5["kill_type"] == "K6_heartbeat")
    print(f"        -> {k5['level']} / {k5['kill_type']}")

    # bonus: governance_log schema is well-formed and AI is non-binding.
    gl = governance_log(record_id="GOV-0001", type="promotion",
                        trigger="promotion_gate request",
                        evidence={"promotion_gate": pg},
                        deterministic_checks_passed=pg["eligible"],
                        ai_advisory="advisory only: track is short of live Sharpe bar",
                        approver=None, decision="PENDING")
    check("(bonus) governance_log: AI advisory is non-binding + decision PENDING",
          gl["ai_advisory_binding"] is False and gl["decision"] == "PENDING"
          and gl["approver"] is None)

    # clean OK day produces no kill (sanity that we don't over-trip).
    check("(sanity) clean OK day -> NONE kill, no CRIT rows",
          kill_switch(_ok_state(), monitor_day(_ok_state()))["level"] == "NONE"
          and all(r["level"] in ("OK",) for r in monitor_day(_ok_state())))

    print("-" * 80)
    n_pass = sum(1 for _, c in results if c)
    print(f"RESULT: {n_pass}/{len(results)} PASS")
    print("PRINCIPLE: LLM off-path advisory only; deterministic rules trigger kill; human gates capital.")
    return all(c for _, c in results)


if __name__ == "__main__":
    sys.exit(0 if _smoke() else 1)

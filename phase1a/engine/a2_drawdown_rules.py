#!/usr/bin/env python3
"""PRAMANA A2 — Layer 5 Drawdown Rules / Lockout Governor (SSOT v2 §04 §7·§8 · §06 §5).

Risk Engine = **신규진입/증액 금지 우선** (NOT auto-sell).
기존 QQQ/TQQQ 자동매도는 극단조건에서도 *manual_decision_flag로만 표시* — 절대 자동집행 X.
"Risk-Off" 명칭 금지(마켓타이밍 자동매도 오해). 모든 state는 a2_risk_dashboard.compute()에서·next-bar(state t → action t+1).

기능:
  track_streaks() — outputs/a2_live/drawdown_state.json 유지: leadership_red_days·decay_zone_days(연속)·a2_mdd·tqqq_sleeve_mdd.
  crash_lockout() — SSOT §04 §8: A2 MDD≤-30% OR TQQQ sleeve MDD≤-35% OR Leadership RED≥10일 OR Decay Zone≥20일 OR (QQQ<200dma + high vol + leaders breakdown).
  attack_lockout() — SSOT §04 §7: Leadership RED-ish → TQQQ/Attack/Moonshot 신규 증액 금지·Reload 금지·Profit Vault 우선(자동매도 아님).
  mode() — base/berserker/red_king/attack_lockout/crash_lockout 중 지배 모드.
  trim_candidates() — TQQQ MANUAL trim 후보(-5%p/1회·하루 max -10%p) = manual_decision_flag (집행 아님).
PAPER·자본권한 0.
"""
import os, sys, json, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a2_risk_dashboard
try:
    import yaml
except ImportError:
    yaml = None

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
REPO = os.path.dirname(ROOT)                                   # phase1a 위 = repo root (config/ 위치)
OUT = os.path.join(ROOT, "outputs", "a2_live"); os.makedirs(OUT, exist_ok=True)
DD_JSON = os.path.join(OUT, "drawdown_state.json")
BOOK_JSON = os.path.join(OUT, "book_state.json")
MAP_YAML = os.path.join(REPO, "config", "a2_state_mapping.yaml")

# SSOT §04 §8 default triggers (config 없으면 fallback)
DEFAULT_TRIGGERS = {"a2_mdd": -0.30, "tqqq_sleeve_mdd": -0.35,
                    "leadership_red_days": 10, "decay_zone_days": 20}
HIGH_VOL = 0.35       # realized_vol_20d high (Market Stress RED 기준과 정합·a2_risk_dashboard)


def load_triggers():
    """config/a2_state_mapping.yaml crash_lockout_triggers (없으면 default)."""
    t = dict(DEFAULT_TRIGGERS)
    if yaml and os.path.exists(MAP_YAML):
        try:
            cfg = yaml.safe_load(open(MAP_YAML)) or {}
            t.update(cfg.get("crash_lockout_triggers", {}) or {})
        except Exception:
            pass
    return t


def _book_mdd():
    """★ FIX(integration): crash lockout은 *현재(peak-to-now)* drawdown으로 — backtest max(A2Beta_mdd) 아님(live/backtest 혼동·−41% 매일 오발동 방지).
    A2Beta_current_dd(a2_book 기록) 우선 → live_current_dd → 없으면 0.0."""
    if os.path.exists(BOOK_JSON):
        try:
            b = json.load(open(BOOK_JSON))
            v = b.get("A2Beta_current_dd")
            if v is None: v = b.get("A2Beta_live_current_dd", 0.0)
            return float(v or 0.0)
        except Exception:
            return 0.0
    return 0.0


def track_streaks(state_path=DD_JSON, risk=None):
    """drawdown_state.json append/update. 연속 카운터는 같은 as_of 재실행 시 중복증가 X(idempotent).

    leadership_red_days  : Leadership RED 연속 거래일
    decay_zone_days      : TQQQ Decay Zone 연속 거래일
    a2_mdd               : book_state.json의 A2 total MDD (없으면 0)
    tqqq_sleeve_mdd      : placeholder 0 (sleeve ledger 생기기 전까지)
    """
    if risk is None:
        risk = a2_risk_dashboard.compute()
    asof = risk["as_of"]
    prev = {}
    if os.path.exists(state_path):
        try:
            prev = json.load(open(state_path))
        except Exception:
            prev = {}
    # 직전 카운터: 파일이 raw streaks든 main()의 {"streaks": {...}} 래핑이든 둘 다에서 읽음
    pstreak = prev.get("streaks", prev) if isinstance(prev, dict) else {}
    prev_lead = int(pstreak.get("leadership_red_days", prev.get("leadership_red_days", 0)) or 0)
    prev_decay = int(pstreak.get("decay_zone_days", prev.get("decay_zone_days", 0)) or 0)
    same_day = (prev.get("as_of") == asof)         # 같은 날 재실행 → 카운터 동결(중복증가 방지)
    lead_red = (risk["leadership_state"] == "RED")
    decay_on = bool(risk.get("tqqq_decay", False))

    if same_day:                                    # idempotent: 동일 as_of면 직전 카운터 그대로
        lead_days = prev_lead
        decay_days = prev_decay
    else:                                            # 새 거래일: RED면 +1, 아니면 0으로 리셋
        lead_days = prev_lead + 1 if lead_red else 0
        decay_days = prev_decay + 1 if decay_on else 0

    streaks = {
        "as_of": asof,
        "leadership_state": risk["leadership_state"],
        "leadership_red_days": lead_days,
        "tqqq_decay": decay_on,
        "decay_zone_days": decay_days,
        "a2_mdd": round(_book_mdd(), 4),
        "tqqq_sleeve_mdd": 0.0,                      # placeholder until sleeve ledger
        "tqqq_sleeve_mdd_note": "placeholder 0.0 — TQQQ sleeve ledger 생기기 전까지 (a2_tqqq_module 미연동)",
        "qqq_above_ma200": bool(risk.get("qqq_above_ma200", True)),
        "realized_vol_20d": float(risk.get("realized_vol_20d", 0.0)),
        "qqq_drawdown": float(risk.get("qqq_drawdown", 0.0)),
    }
    return streaks


def crash_lockout(streaks, triggers):
    """SSOT §04 §8 Crash Lockout 판정 → (bool, reasons[]).

    조건(OR): A2 MDD≤-30% · TQQQ sleeve MDD≤-35% · Leadership RED≥10일 · Decay Zone≥20일
              · (QQQ 200dma 하회 + high vol + leaders breakdown).
    행동: TQQQ 신규매수 0·Attack/Moonshot 신규 0·사람 리뷰 필요·자동매도는 manual_decision_flag만(절대 자동집행 X).
    """
    reasons = []
    a2_mdd = streaks.get("a2_mdd", 0.0)
    tq_mdd = streaks.get("tqqq_sleeve_mdd", 0.0)
    if a2_mdd <= triggers["a2_mdd"]:
        reasons.append(f"A2 total MDD {a2_mdd:.1%} ≤ {triggers['a2_mdd']:.0%}")
    if tq_mdd <= triggers["tqqq_sleeve_mdd"]:
        reasons.append(f"TQQQ sleeve MDD {tq_mdd:.1%} ≤ {triggers['tqqq_sleeve_mdd']:.0%}")
    if streaks.get("leadership_red_days", 0) >= triggers["leadership_red_days"]:
        reasons.append(f"Leadership RED {streaks['leadership_red_days']}거래일 연속 ≥ {triggers['leadership_red_days']}")
    if streaks.get("decay_zone_days", 0) >= triggers["decay_zone_days"]:
        reasons.append(f"TQQQ Decay Zone {streaks['decay_zone_days']}거래일 연속 ≥ {triggers['decay_zone_days']}")
    # 복합 조건: QQQ 200일선 하회 + high vol + leaders breakdown(Leadership RED)
    if (not streaks.get("qqq_above_ma200", True)
            and streaks.get("realized_vol_20d", 0.0) > HIGH_VOL
            and streaks.get("leadership_state") == "RED"):
        reasons.append(f"QQQ<200dma + high vol({streaks['realized_vol_20d']:.0%}) + leaders breakdown(RED)")
    return (len(reasons) > 0), reasons


def attack_lockout(states):
    """SSOT §04 §7 Attack Lockout / Booster Add Ban → (bool, reasons[]).

    Leadership RED-ish(RED) → TQQQ/Attack/Moonshot 신규 증액 금지·Reload 금지·Profit Vault 우선.
    NOT auto-sell (기존 포지션 매도 아님 = 신규/증액 게이트만).
    Market Stress RED도 같은 게이트(증액 금지)로 묶는다.
    """
    reasons = []
    if states.get("leadership_state") == "RED":
        reasons.append("Leadership RED → TQQQ/Attack/Moonshot 신규 증액 금지·Reload 금지·Profit Vault 우선")
    if states.get("market_stress") == "RED":
        reasons.append("Market Stress RED → 신규 증액 금지(증액 게이트)")
    return (len(reasons) > 0), reasons


def mode(states, streaks, triggers):
    """지배 모드 1개 반환 (SSOT §04 §6). 우선순위: crash > attack_lockout > red_king > berserker > base."""
    crash, _ = crash_lockout(streaks, triggers)
    if crash:
        return "crash_lockout"
    atk, _ = attack_lockout(states)
    if atk:
        return "attack_lockout"
    # red_king: Decay Zone or Booster Rent or Market Stress YELLOW → TQQQ 증액 금지·Attack half
    if states.get("tqqq_decay") or states.get("booster_rent") or states.get("market_stress") == "YELLOW":
        return "red_king"
    # berserker: 다중 GREEN(증액 가능) — Leadership·Market·Decay 모두 GREEN
    if (states.get("leadership_state") == "GREEN" and states.get("market_stress") == "GREEN"
            and not states.get("tqqq_decay") and not states.get("booster_rent")):
        return "berserker"
    return "base"


def trim_candidates(streaks, risk):
    """TQQQ MANUAL trim 후보 list (SSOT §06 §5). -5%p/1회·하루 max -10%p.

    *** manual_decision_flag만 — 절대 자동집행 X. ***
    파산방지 후보 조건(SSOT §06 §5): A2 MDD≤-30% · TQQQ sleeve MDD≤-35% · Leadership RED≥10일
                                   · Decay Zone≥20일 · QQQ<200dma + high vol + leaders breakdown.
    """
    cands = []

    def add(reason):
        cands.append({
            "sleeve": "TQQQ",
            "action": "MANUAL_TRIM_CANDIDATE",
            "delta_pp": -0.05,                       # 1회 -5%p
            "max_day_pp": -0.10,                     # 하루 최대 -10%p
            "manual_decision_flag": True,            # ★ 사람 결정·집행 아님
            "auto_executed": False,
            "reason": reason,
        })

    if streaks.get("a2_mdd", 0.0) <= -0.30:
        add(f"A2 total MDD {streaks['a2_mdd']:.1%} ≤ -30%")
    if streaks.get("tqqq_sleeve_mdd", 0.0) <= -0.35:
        add(f"TQQQ sleeve MDD {streaks['tqqq_sleeve_mdd']:.1%} ≤ -35%")
    if streaks.get("leadership_red_days", 0) >= 10:
        add(f"Leadership RED {streaks['leadership_red_days']}거래일 연속 ≥ 10")
    if streaks.get("decay_zone_days", 0) >= 20:
        add(f"TQQQ Decay Zone {streaks['decay_zone_days']}거래일 연속 ≥ 20")
    if (not risk.get("qqq_above_ma200", True)
            and risk.get("realized_vol_20d", 0.0) > HIGH_VOL
            and risk.get("leadership_state") == "RED"):
        add("QQQ<200dma + high vol + leaders breakdown")
    return cands


def main():
    risk = a2_risk_dashboard.compute()
    triggers = load_triggers()
    streaks = track_streaks(DD_JSON, risk=risk)
    crash, crash_reasons = crash_lockout(streaks, triggers)
    atk, atk_reasons = attack_lockout(risk)
    gov_mode = mode(risk, streaks, triggers)
    trims = trim_candidates(streaks, risk)

    out = {
        "as_of": risk["as_of"],
        "mode": gov_mode,
        "crash_lockout": crash,
        "crash_lockout_reasons": crash_reasons,
        "attack_lockout": atk,
        "attack_lockout_reasons": atk_reasons,
        "streaks": {k: streaks[k] for k in (
            "leadership_state", "leadership_red_days", "tqqq_decay", "decay_zone_days",
            "a2_mdd", "tqqq_sleeve_mdd", "qqq_above_ma200", "realized_vol_20d")},
        "tqqq_sleeve_mdd_note": streaks["tqqq_sleeve_mdd_note"],
        "trim_candidates": trims,
        "triggers": triggers,
        "auto_sell_executed": False,                 # ★ 항상 False — 자동매도 없음
        "policy": "Risk Engine = 신규진입/증액 금지 우선 (NOT auto-sell). "
                  "기존 QQQ/TQQQ 매도는 manual_decision_flag만 — 절대 자동집행 X.",
        "next_bar": "state_t → action_{t+1} (same-day 신호로 same-day 집행 금지)",
    }
    json.dump(out, open(DD_JSON, "w"), indent=2, ensure_ascii=False)

    print(f"✅ A2 Drawdown Rules {out['as_of']} — mode={gov_mode.upper()}")
    print(f"   Crash Lockout : {crash}" + (f"  ← {crash_reasons}" if crash else "  (no trigger)"))
    print(f"   Attack Lockout: {atk}" + (f"  ← {atk_reasons}" if atk else "  (no trigger)"))
    print(f"   Streaks: Leadership {streaks['leadership_state']} {streaks['leadership_red_days']}d "
          f"· Decay {'ZONE' if streaks['tqqq_decay'] else 'OK'} {streaks['decay_zone_days']}d "
          f"· A2 MDD {streaks['a2_mdd']:.1%} · TQQQ sleeve MDD {streaks['tqqq_sleeve_mdd']:.1%} (placeholder)")
    if trims:
        print(f"   TQQQ MANUAL trim candidates ({len(trims)}): -5%p/1회·하루 max -10%p")
        for c in trims:
            print(f"      • {c['reason']}  [manual_decision_flag=True · auto_executed=False]")
    else:
        print("   TQQQ MANUAL trim candidates: 없음")
    print("   ── 자동매도는 NEVER 집행됨. 위 trim은 사람 결정용 flag만 (auto_sell_executed=False). ──")
    print(f"   → {DD_JSON}")


if __name__ == "__main__":
    main()

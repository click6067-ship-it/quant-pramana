#!/usr/bin/env python3
"""PRAMANA A2 — Layer 4 Dynamic Allocator / State→Target-Weight Mapping (SSOT v2 §04).

규율(NON-NEGOTIABLE):
  - PAPER·자본권한 0. **LLM은 상태(GREEN/YELLOW/RED 등)만 판정** — 이 엔진이 상태→비중(숫자)을
    *결정론적으로* 매핑한다. LLM이 숫자/매수매도/확률 결정 = 금지(SSOT §04 §4).
  - **next-bar**: state는 t일 데이터로 계산(risk_dashboard) → target weight는 t+1일 적용.
    같은 날 state를 같은 날 수익에 적용하지 않는다(SSOT §04 §9). 이 엔진은 *target만* 산출.
  - 1회 변경 = 5%p(change_unit)·ranges clamp·max_daily 5%p·max_weekly 10%p(|delta| 합).
  - 정직 라벨: 이 엔진은 **rule-mapping (검증된 알파 아님)**.

★ 정직 경고 — dynamic allocation 기각 이력:
  prior A2 ablation에서 *동적 allocator 기여 = -113%p* (고정 35/35/10/10/10 이 이김) → REJECT
  (Codex #5 · config/a2_convex_raider.yaml: dynamic_mode_enabled:false ·
   config/a2_revived_components.yaml: dynamic_allocator_v3 rejected).
  → 이 엔진은 SSOT가 명세하므로 *존재*하나, **기본 OFF**(ENABLED=False·config dynamic_mode_enabled
    미러). OFF면 target을 *계산만* 하고 비중 변경을 강제하지 않는다(=base 유지). 명시적 enable
    (config dynamic_mode_enabled:true) 이거나 states가 명백히 정당화할 때만 실제 delta 제안.

상태 도출(rule-engine·LLM 아님): risk_dashboard.compute(asof) 출력 → 슬리브별 GREEN/YELLOW/RED 등.
매핑/clamp/limit: config/a2_state_mapping.yaml (단일 진실).
입출력: outputs/a2_live/allocator_state.json(append-only history) · target_weights.json.
사용: python engine/a2_dynamic_allocator.py
"""
import os, sys, json, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a2_risk_dashboard

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); REPO = os.path.dirname(ROOT)
A2 = os.path.join(ROOT, "outputs", "a2_live"); os.makedirs(A2, exist_ok=True)
MAP_CFG = os.path.join(REPO, "config", "a2_state_mapping.yaml")
RAIDER_CFG = os.path.join(REPO, "config", "a2_convex_raider.yaml")
ALLOC_STATE = os.path.join(A2, "allocator_state.json")   # append-only history
TARGET_JSON = os.path.join(A2, "target_weights.json")
SLEEVES = ["qqq", "tqqq", "attack", "moonshot", "vault"]

# ── ENABLED flag (config dynamic_mode_enabled 미러·기본 OFF) ──
# OFF = target만 계산, base 유지(비중 변경 강제 안 함). dynamic allocator는 ablation서 -113%p REJECT.
ENABLED = False   # default conservative; config/a2_convex_raider.yaml: dynamic_mode_enabled 로 override


def load_yaml(p, d=None):
    try:
        import yaml; return yaml.safe_load(open(p)) or (d or {})
    except Exception:
        return d or {}


def load_mapping():
    """config/a2_state_mapping.yaml (repo root /config) = base_allocation·ranges·change_unit·
    max_daily/weekly·mapping deltas·modes·crash_lockout_triggers. 단일 진실."""
    m = load_yaml(MAP_CFG)
    if not m or "base_allocation" not in m:
        raise FileNotFoundError(f"a2_state_mapping.yaml 없음/불완전: {MAP_CFG}")
    return m


def config_enabled():
    """ENABLED 결정: config dynamic_mode_enabled(우선) → 없으면 모듈 ENABLED 상수."""
    raider = load_yaml(RAIDER_CFG)
    if "dynamic_mode_enabled" in raider:
        return bool(raider["dynamic_mode_enabled"])
    return ENABLED


# ── 상태 도출(rule-engine·LLM 아님): risk_dashboard 출력 → 슬리브별 state ─────────────────
# 아래 규칙은 *코드/룰*이다(LLM 아님). LLM이 채우는 건 leadership/market 등 상위 라벨뿐이고,
# 슬리브별 OPEN/HOLD/RED 등으로의 매핑은 여기서 결정론적으로 산출한다.
def derive_states(risk):
    """risk_dashboard.compute() dict → per-sleeve states (모두 rule, LLM 아님).

    tqqq_state:
      GREEN  if leadership GREEN & not decay & not booster_rent & qqq>ma50
      RED    if leadership RED  or decay or market RED
      else YELLOW
    attack_state:
      RED    if leadership RED or market RED
      YELLOW if leadership YELLOW
      else GREEN
    moonshot_state:
      LOCKED    if leadership RED
      HOLD_ONLY if leadership YELLOW
      else OPEN
    vault_state:
      ACCUMULATE     if leadership YELLOW/RED or decay   (방어적으로 vault 적립)
      RELOAD_ALLOWED if leadership GREEN & not decay & qqq>ma20  (탄약 재장전 허용)
      else HOLD
    """
    lead = (risk.get("leadership_state") or "GREEN").upper()
    market = (risk.get("market_stress") or "GREEN").upper()
    decay = bool(risk.get("tqqq_decay"))
    booster = bool(risk.get("booster_rent"))
    above20 = bool(risk.get("qqq_above_ma20"))
    above50 = bool(risk.get("qqq_above_ma50"))

    if lead == "GREEN" and not decay and not booster and above50:
        tqqq = "GREEN"
    elif lead == "RED" or decay or market == "RED":
        tqqq = "RED"
    else:
        tqqq = "YELLOW"

    if lead == "RED" or market == "RED":
        attack = "RED"
    elif lead == "YELLOW":
        attack = "YELLOW"
    else:
        attack = "GREEN"

    moonshot = "LOCKED" if lead == "RED" else ("HOLD_ONLY" if lead == "YELLOW" else "OPEN")

    if lead in ("YELLOW", "RED") or decay:
        vault = "ACCUMULATE"
    elif lead == "GREEN" and not decay and above20:
        vault = "RELOAD_ALLOWED"
    else:
        vault = "HOLD"

    return {"tqqq": tqqq, "attack": attack, "moonshot": moonshot, "vault": vault,
            "_inputs": {"leadership": lead, "market": market, "decay": decay,
                        "booster_rent": booster, "qqq_above_ma20": above20, "qqq_above_ma50": above50}}


def mode_of(states):
    """SSOT §04 §6-8 mode label (states 기준). Risk-Off 명칭 금지(자동매도 오해).
       crash enforcement는 a2_drawdown_rules.py(별도)·여기선 states로 *라벨만*.
       - Crash Lockout : market RED & leadership RED (crash flag는 drawdown_rules가 최종 판정)
       - Attack Lockout: leadership RED (신규/booster-add ban)
       - Red King      : tqqq RED 또는 attack RED (TQQQ 증액 금지·Attack half)
       - Berserker     : tqqq GREEN & attack GREEN & vault RELOAD_ALLOWED (다중 GREEN·증액 가능)
       - Base          : 그 외(기본 35/35/10/10/10)
    """
    inp = states.get("_inputs", {})
    lead = inp.get("leadership", "GREEN"); market = inp.get("market", "GREEN")
    if lead == "RED" and market == "RED":
        return "Crash Lockout"
    if lead == "RED":
        return "Attack Lockout"
    if states["tqqq"] == "RED" or states["attack"] == "RED":
        return "Red King"
    if states["tqqq"] == "GREEN" and states["attack"] == "GREEN" and states["vault"] == "RELOAD_ALLOWED":
        return "Berserker"
    return "Base"


def _renorm_to_vault(w, ranges=None):
    """합 1.0 보정: 잔차(부족/초과)는 vault(현금성)로 흡수 → vault range 초과분은 qqq(베타 코어/현금
       앵커)로 spill. ranges 없으면 vault만(DISABLED 경로). 음수 방지."""
    s = sum(w.values()); resid = round(1.0 - s, 6)
    vlo, vhi = (ranges.get("vault") if ranges else [0.0, 1.0]) or [0.0, 1.0]
    want_v = w.get("vault", 0.0) + resid
    new_v = max(vlo, min(vhi, want_v)) if ranges else max(0.0, want_v)
    spill = round(want_v - new_v, 6)              # vault range가 못 받은 잔차
    w["vault"] = round(new_v, 6)
    if abs(spill) > 1e-9:                          # vault cap/floor 막힘 → qqq(코어)로
        w["qqq"] = round(w.get("qqq", 0.0) + spill, 6)
    s = sum(w.values())
    if abs(s - 1.0) > 1e-9:                        # 그래도 안 맞으면 비례 보정(최후)
        for k in w: w[k] = w[k] / s
    out = {k: round(v, 4) for k, v in w.items()}    # 4dp = 5%p 격자에 충분·부동소수 잔물결 제거
    out["qqq"] = round(out.get("qqq", 0.0) + (1.0 - sum(out.values())), 4)   # 라운딩 crumb→qqq, 합=1.0 보장
    return out


def map_to_targets(current_weights, states, mapping, weekly_used=0.0, enabled=True):
    """states → target weights (next-bar용 target). 결정론적:
       1) sleeve별 mapping delta(±5%p, change_unit) 적용
       2) ranges clamp
       3) max_daily 5%p(|delta| 합)·max_weekly 10%p(주간 누적) 제한 → 초과 delta 스케일다운
       4) renormalize 합=1.0 (잔차→vault/cash)
       enabled=False면 delta=0(=base/current 유지)·라벨만 산출(REJECT 이력 → 기본 보수적).
       반환: {target, delta_pp, clamped(슬리브별 limit 사유), daily_used, weekly_used_after}.
    """
    cur = {k: float(current_weights.get(k, 0.0)) for k in SLEEVES}
    ranges = mapping["ranges"]; mp = mapping["mapping"]; step = float(mapping["change_unit"])
    max_daily = float(mapping["max_daily_change"]); max_weekly = float(mapping["max_weekly_change"])
    clamped = {}

    # 1) 원하는 delta (mapping에서)
    desired = {}
    for sl in SLEEVES:
        if sl == "qqq":            # qqq는 mapping 대상 아님(베타 코어)·잔차 흡수는 vault
            desired[sl] = 0.0; continue
        st = states.get(sl, "YELLOW" if sl != "vault" else "HOLD")
        if sl == "moonshot":
            st = states.get("moonshot", "HOLD_ONLY")
        desired[sl] = float(mp.get(sl, {}).get(st, 0.0))

    if not enabled:   # OFF: 비중 변경 강제 안 함(REJECT 이력 → base 유지). target=current.
        tgt = dict(cur)
        return {"target": _renorm_to_vault(tgt, ranges), "delta_pp": {k: 0.0 for k in SLEEVES},
                "clamped": {"_engine": "DISABLED — dynamic_mode OFF·base 유지(ablation -113%p REJECT)"},
                "daily_used": 0.0, "weekly_used_after": round(weekly_used, 4)}

    # 2) ranges clamp (current+delta가 range 벗어나면 delta 축소)
    for sl in SLEEVES:
        if desired[sl] == 0.0: continue
        lo, hi = ranges.get(sl, [0.0, 1.0]); want = cur[sl] + desired[sl]
        new = max(lo, min(hi, want))
        if abs(new - want) > 1e-9:
            clamped[sl] = f"range[{lo:.2f},{hi:.2f}]"
        desired[sl] = round(new - cur[sl], 6)

    # 3) daily limit (|delta| 합 ≤ max_daily) — 초과 시 비례 축소
    total = sum(abs(d) for d in desired.values())
    if total > max_daily + 1e-9:
        scale = max_daily / total
        for sl in SLEEVES:
            if desired[sl] != 0.0:
                desired[sl] = round(desired[sl] * scale, 6)
                clamped[sl] = (clamped.get(sl, "") + f" daily≤{max_daily:.2f}").strip()
        total = sum(abs(d) for d in desired.values())
    # weekly limit (누적 |delta| ≤ max_weekly)
    weekly_room = max(0.0, max_weekly - weekly_used)
    if total > weekly_room + 1e-9:
        scale = (weekly_room / total) if total > 1e-9 else 0.0
        for sl in SLEEVES:
            if desired[sl] != 0.0:
                desired[sl] = round(desired[sl] * scale, 6)
                clamped[sl] = (clamped.get(sl, "") + f" weekly≤{max_weekly:.2f}(used {weekly_used:.2f})").strip()
        total = sum(abs(d) for d in desired.values())

    # 4) apply + renormalize (잔차→vault)
    tgt = {sl: round(cur[sl] + desired[sl], 6) for sl in SLEEVES}
    tgt = _renorm_to_vault(tgt, ranges)
    return {"target": tgt, "delta_pp": {sl: round(tgt[sl] - cur[sl], 6) for sl in SLEEVES},
            "clamped": clamped, "daily_used": round(total, 4),
            "weekly_used_after": round(weekly_used + total, 4)}


def _load_state():
    try: return json.load(open(ALLOC_STATE))
    except Exception: return {"history": []}


def _weekly_used(hist, asof):
    """같은 ISO week 내 history의 daily_used 누적(주간 한도 추적)."""
    try:
        wk = pd_isoweek(asof)
        used = 0.0
        for h in hist:
            if h.get("date") and pd_isoweek(h["date"]) == wk:
                used += float(h.get("daily_used", 0.0))
        return round(used, 4)
    except Exception:
        return 0.0


def pd_isoweek(d):
    y, w, _ = dt.date.fromisoformat(str(d)[:10]).isocalendar()
    return f"{y}-W{w:02d}"


def main():
    mapping = load_mapping()
    enabled = config_enabled()
    base = {k: float(mapping["base_allocation"][k]) for k in SLEEVES}

    # current weights: allocator_state.json 마지막 target → 없으면 base
    st = _load_state(); hist = st.get("history", [])
    current = hist[-1]["target"] if hist else dict(base)

    # risk states (t일 데이터로 계산) → next-bar(t+1) target
    risk = a2_risk_dashboard.compute(weights=current)
    asof = risk["as_of"]
    states = derive_states(risk)
    mode = mode_of(states)
    weekly_used = _weekly_used(hist, asof)
    res = map_to_targets(current, states, mapping, weekly_used=weekly_used, enabled=enabled)

    rec = {"date": asof, "computed_at": str(dt.datetime.now().isoformat(timespec="seconds")),
           "enabled": enabled, "mode": mode,
           "states": {k: v for k, v in states.items() if k != "_inputs"}, "state_inputs": states["_inputs"],
           "current": current, "target": res["target"], "delta_pp": res["delta_pp"],
           "clamped": res["clamped"], "daily_used": res["daily_used"],
           "weekly_used_after": res["weekly_used_after"],
           "label": "rule-mapping (NOT validated alpha) · next-bar (state_t → weight_{t+1}) · PAPER·자본권한 0",
           "rejected_history": "dynamic allocator ablation -113%p < fixed 35/35 → REJECT (Codex #5). 기본 OFF."}
    hist.append(rec)
    json.dump({"history": hist}, open(ALLOC_STATE, "w"), indent=2, ensure_ascii=False)
    json.dump({"as_of": asof, "enabled": enabled, "mode": mode, "next_bar": True,
               "target_weights": res["target"], "delta_pp": res["delta_pp"],
               "label": rec["label"]}, open(TARGET_JSON, "w"), indent=2, ensure_ascii=False)

    # ── summary ──
    flag = "ENABLED" if enabled else "DISABLED(base 유지·REJECT 이력)"
    print(f"=== A2 Dynamic Allocator [{flag}] — rule-mapping (NOT validated alpha) · PAPER ===")
    print(f"as_of {asof} (state_t → weight_{{t+1}}: next-bar)  ·  MODE = {mode}")
    print(f"inputs: leadership={states['_inputs']['leadership']} market={states['_inputs']['market']} "
          f"decay={states['_inputs']['decay']} booster={states['_inputs']['booster_rent']} "
          f"qqq>ma20={states['_inputs']['qqq_above_ma20']} qqq>ma50={states['_inputs']['qqq_above_ma50']}")
    print(f"sleeve states: tqqq={states['tqqq']} attack={states['attack']} "
          f"moonshot={states['moonshot']} vault={states['vault']}")
    print(f"current : {{ " + ', '.join(f'{k}:{current[k]:.2f}' for k in SLEEVES) + " }")
    print(f"TARGET  : {{ " + ', '.join(f'{k}:{res['target'][k]:.2f}' for k in SLEEVES) + " }")
    print(f"delta_pp: {{ " + ', '.join(f'{k}:{res['delta_pp'][k]*100:+.1f}' for k in SLEEVES) + " }} (5%p unit)")
    print(f"limits  : daily_used {res['daily_used']*100:.1f}%p (≤{mapping['max_daily_change']*100:.0f}) · "
          f"weekly_after {res['weekly_used_after']*100:.1f}%p (≤{mapping['max_weekly_change']*100:.0f})")
    print(f"clamped : {res['clamped'] or '(없음)'}")
    print(f"→ history: {ALLOC_STATE}")
    print(f"→ target : {TARGET_JSON}")
    if not enabled:
        print("NOTE: dynamic_mode OFF → target=base(current). 동적 비중 강제 안 함. "
              "config/a2_convex_raider.yaml: dynamic_mode_enabled:true 로만 활성(검증 전 보수적).")


if __name__ == "__main__":
    main()

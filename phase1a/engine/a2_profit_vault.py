#!/usr/bin/env python3
"""PRAMANA A2 — Profit Vault rule engine (extract/generalize of a2_live_runner inline vault).
정본 spec: 05_DYNAMIC_SELL_AND_VAULT_TIMING.md §1-5 + 09_VAULT_MODULE.md.
규율: PAPER·자본권한 0. LLM은 상태(GREEN/YELLOW/RED)만 제공·숫자는 전부 이 룰(mapping engine).
Vault = 실제 ledger(active capital에서 제거)·표시용 아님. Hard Vault = 코드상 영구 재투입 불가(assert).
Vault In = 이긴 돈(절대수익)일 때만 — QQQ보다 덜 잃은 것만으론 절대 금지(spec §1 핵심).
ledger 단위 = NAV 분수(fraction of total NAV). append-only events.
a2_live_runner.py 와 동일 의미: live_excess HWM·절대수익 게이트·Hard70/Reload30·일1회.
모듈 — 단독 실행보다 import 용도. CLI smoke = `python a2_profit_vault.py`."""
import os, json, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); REPO = os.path.dirname(ROOT)


def _isoweek(d):
    try: y, w, _ = pd_ts(d).isocalendar(); return (y, w)
    except Exception: return None
def _month(d):
    try: t = pd_ts(d); return (t.year, t.month)
    except Exception: return None
def pd_ts(d):
    import datetime as _dt
    if isinstance(d, (_dt.date, _dt.datetime)): return _dt.date(d.year, d.month, d.day)
    s = str(d)[:10]; y, m, dd = s.split("-"); return _dt.date(int(y), int(m), int(dd))
def _last_event_date(ledger, event_type):
    for e in reversed(ledger.get("events", [])):
        if e.get("event") == event_type: return e.get("date")
    return None
def _gate_ok(ledger, event_type, today, period):
    """SSOT §09: Vault In 주1회·Reload 월1회. 같은 기간에 이미 이벤트 있으면 False(차단)."""
    last = _last_event_date(ledger, event_type)
    if not last: return True
    if period == "week": return _isoweek(last) != _isoweek(today)
    return _month(last) != _month(today)
RULES_PATH = os.path.join(REPO, "config", "a2_vault_rules.yaml")
DEFAULT_LEDGER = {"hard": 0.0, "reload": 0.0, "hwm": 0.0, "last_date": None, "events": []}
HARD_RATIO, RELOAD_RATIO = 0.70, 0.30   # spec §4 (rules yaml override 가능)


def load_rules(path=RULES_PATH):
    try:
        import yaml; r = yaml.safe_load(open(path)); return r if r else {}
    except Exception:
        return {}


# ── ledger I/O (append-only events·a2_live_runner vault.json 호환) ──
def load_vault(path):
    if os.path.exists(path):
        try:
            d = json.load(open(path))
            for k, v in DEFAULT_LEDGER.items(): d.setdefault(k, [] if k == "events" else v)
            return d
        except Exception:
            pass
    json.dump(dict(DEFAULT_LEDGER, events=[]), open(path, "w"), indent=2)
    return dict(DEFAULT_LEDGER, events=[])


def save_vault(ledger, path):
    """append-only 보장: 디스크 events 개수보다 줄면 거부(룰 위반=쓰지 않음)."""
    if os.path.exists(path):
        try:
            old = json.load(open(path))
            if len(ledger.get("events", [])) < len(old.get("events", [])):
                raise ValueError("append-only violation: events count decreased")
            if ledger.get("hard", 0.0) + 1e-12 < old.get("hard", 0.0):
                raise ValueError("Hard Vault decreased — forbidden (permanently locked)")
        except (ValueError):
            raise
        except Exception:
            pass
    json.dump(ledger, open(path, "w"), indent=2)


# ── Vault In 강도 (spec §2 표) — 신규 초과수익분에 곱할 이동률 ──
def classify_vault_in(excess_pp, abs_profit_bool, risk_state, rules=None):
    """returns move_rate (0 = 미작동). abs_profit_bool=False(이긴 돈 없음)면 무조건 0.
    spec §1 핵심: 실제로 이긴 돈이 있을 때만. excess +4/+8/+12%p × risk GREEN/YELLOW/RED."""
    if not abs_profit_bool:
        return 0.0                       # 이긴 돈 없음 → Vault 금지 (덜 잃은 것만으론 금지)
    rs = (risk_state or "GREEN").upper()
    rules = rules if rules is not None else load_rules()
    table = (rules.get("vault_in_strength") or [])
    if not table:                        # fallback = a2_live_runner 단순 룰 (0.50 if≥12 else 0.25)
        if excess_pp >= 0.12: return 0.50
        if excess_pp >= 0.04: return 0.25
        return 0.0
    # 충족하는 행들 중 min_excess_pp 가장 큰(=가장 높은 구간) 행의 rate. 결정적.
    cand = [r for r in table if excess_pp + 1e-12 >= r["min_excess_pp"] and r.get("risk", "GREEN").upper() == rs]
    if not cand: return 0.0
    return float(max(cand, key=lambda r: r["min_excess_pp"])["rate"])


# ── Vault In 적용 (HWM 갱신·70/30·event append) ──
def apply_vault_in(ledger, new_excess, risk_state, today, abs_profit_bool=None,
                   source="qqq", reason="", rules=None, month_moved=0.0):
    """new_excess(=live A2-T - QQQ, fraction) HWM 돌파분의 move_rate 만큼 NAV에서 Vault로.
    Hard70/Reload30 분리·HWM 갱신·event append. 이동 없으면 HWM만 갱신.
    abs_profit_bool None → new_excess>0 가정 X: 명시 권장(이긴 돈 게이트)."""
    rules = rules if rules is not None else load_rules()
    split = rules.get("split", {}); hr = split.get("hard_ratio", HARD_RATIO); rr = split.get("reload_ratio", RELOAD_RATIO)
    gate = rules.get("vault_in_gate", {}); cap_m = gate.get("max_monthly_move_pct", 0.10)
    if abs_profit_bool is None: abs_profit_bool = new_excess > 0.0
    week_ok = _gate_ok(ledger, "vault_in", today, "week")   # ★ SSOT §09 §3: Vault In 주1회(Codex fix·ledger 기준 중앙 enforce)
    moved = 0.0
    if new_excess > ledger["hwm"] + 1e-12:
        rate = classify_vault_in(new_excess, abs_profit_bool, risk_state, rules) if week_ok else 0.0
        raw = (new_excess - ledger["hwm"]) * rate
        moved = max(0.0, min(raw, cap_m - month_moved))     # 월 10% cap enforcement
        if moved > 1e-12:
            ledger["hard"] += moved * hr; ledger["reload"] += moved * rr
            ledger["events"].append({"date": str(today), "event": "vault_in", "source": source,
                                     "live_excess": round(new_excess, 4), "moved_w": round(moved, 4),
                                     "rate": rate, "risk": (risk_state or "").upper(),
                                     "hard": round(ledger["hard"], 4), "reload": round(ledger["reload"], 4),
                                     "reason": reason})
            ledger["last_date"] = str(today)
        ledger["hwm"] = new_excess          # HWM은 항상 갱신 (이동 cap에 걸려도)
    assert_hard_locked(ledger)
    return moved


# ── Vault Out 게이트 (spec §5) — Reload만·Hard 절대 금지 ──
def can_reload(risk_state, leadership, decay, qqq_above_ma20, dip_type=None,
               market_stress=None, narrative=None, rules=None):
    """Vault Out 가능 여부. Reload Vault 전용. Hard는 절대 호출 안 됨.
    leadership=='GREEN'·decay GREEN(False)·QQQ>20일선 + (market_stress not RED·narrative GREEN/YELLOW).
    dip_type C(Structural Break) = 금지."""
    rules = rules if rules is not None else load_rules()
    g = rules.get("vault_out_gate", {})
    if g.get("leadership_green", True) and (leadership or "").upper() != "GREEN": return False
    if g.get("decay_green", True) and bool(decay): return False           # Decay ZONE = 금지
    if g.get("qqq_above_ma20", True) and not bool(qqq_above_ma20): return False
    if g.get("market_stress_not_red", True) and (market_stress or "").upper() == "RED": return False
    if g.get("narrative_green_yellow", True) and (narrative or "GREEN").upper() == "RED": return False
    if dip_type is not None:
        route = (rules.get("vault_out_dip_routing", {}) or {}).get(str(dip_type).upper(), {})
        if route and not route.get("allow", True): return False          # Type C = Reload 금지
    return True


def reload_route(dip_type, rules=None):
    """dip_type → Reload 경로 (spec §5). 반환 dict {allow,to,note}."""
    rules = rules if rules is not None else load_rules()
    return (rules.get("vault_out_dip_routing", {}) or {}).get(str(dip_type).upper(),
                                                              {"allow": True, "to": "tqqq", "note": "default"})


# ── Vault Out 적용 (Reload 25%만·Hard 영구 잠금) ──
def apply_reload(ledger, pct=0.25, today=None, dip_type=None, reason="", rules=None):
    """Reload Vault의 pct(기본 25%)를 active book으로 빼냄. Hard는 절대 건드리지 않음.
    returns 빼낸 양(fraction). append event."""
    rules = rules if rules is not None else load_rules()
    pct = float(pct)
    if not _gate_ok(ledger, "reload", today or dt.date.today(), "month"):   # ★ SSOT §09 §6: Reload 월1회(Codex fix)
        return 0.0
    out = ledger["reload"] * pct
    hard_before = ledger["hard"]
    if out > 1e-12:
        ledger["reload"] -= out
        ledger["events"].append({"date": str(today or dt.date.today()), "event": "reload",
                                 "moved_w": round(out, 4), "dip_type": dip_type,
                                 "hard": round(ledger["hard"], 4), "reload": round(ledger["reload"], 4),
                                 "reason": reason})
        ledger["last_date"] = str(today or dt.date.today())
    assert abs(ledger["hard"] - hard_before) < 1e-12, "Hard Vault must NOT change on reload"
    assert_hard_locked(ledger)
    return out


# ── Hard Vault 불변 가드 (코드상 재투입 불가 증명) ──
def assert_hard_locked(ledger, prev_hard=None):
    """Hard Vault는 절대 감소 불가. reinvest 시도 = 즉시 AssertionError."""
    assert ledger.get("hard", 0.0) >= -1e-12, "Hard Vault negative — impossible"
    if prev_hard is not None:
        assert ledger["hard"] + 1e-12 >= prev_hard, "Hard Vault decreased — reinvestment forbidden"
    return True


def reinvest_hard(ledger, *a, **k):
    """Hard Vault 재투입 시도 = 설계상 차단. 호출 자체가 룰 위반."""
    raise PermissionError("Hard Vault는 영구 잠금 — 재투입 불가 (spec §4·§9)")


# ── self-smoke (모듈 단독 실행 시) ──
def _smoke():
    rules = load_rules()
    print("rules loaded:", bool(rules), "| split:", rules.get("split"))
    # 강도표 확인
    for e, ap, rs in [(0.04, True, "GREEN"), (0.04, True, "YELLOW"), (0.08, True, "RED"),
                      (0.12, True, "RED"), (0.04, False, "RED"), (-0.02, True, "GREEN")]:
        print(f"  classify excess={e:+.2f} abs_profit={ap} risk={rs:6} -> rate={classify_vault_in(e, ap, rs, rules)}")
    # ledger flow
    L = dict(DEFAULT_LEDGER, events=[])
    m = apply_vault_in(L, 0.08, "YELLOW", "2026-06-14", abs_profit_bool=True, source="tqqq", rules=rules)
    print(f"  vault_in 0.08 YELLOW abs_profit -> moved={m:.4f} hard={L['hard']:.4f} reload={L['reload']:.4f}")
    assert L["hard"] > 0 and L["reload"] > 0 and abs(L["hard"]/(L["hard"]+L["reload"]) - 0.70) < 1e-6
    # 이긴 돈 없으면 0
    L2 = dict(DEFAULT_LEDGER, events=[])
    m2 = apply_vault_in(L2, 0.08, "RED", "2026-06-14", abs_profit_bool=False, rules=rules)
    print(f"  vault_in 0.08 RED  NO-abs-profit -> moved={m2:.4f} (must be 0)")
    assert m2 == 0.0
    # reload only touches reload, never hard
    h0 = L["hard"]; out = apply_reload(L, 0.25, "2026-06-14", dip_type="A", rules=rules)
    print(f"  reload 25% -> out={out:.4f} hard UNCHANGED={L['hard']==h0} reload={L['reload']:.4f}")
    assert L["hard"] == h0
    # hard reinvest forbidden
    try:
        reinvest_hard(L); print("  reinvest_hard: FAIL (no error)")
    except PermissionError as ex:
        print(f"  reinvest_hard blocked: {ex}")
    print("OK — vault smoke passed")


if __name__ == "__main__":
    _smoke()

#!/usr/bin/env python3
"""PRAMANA A2 — TQQQ Booster Module (SSOT v2 §06).

★★ TQQQ = Booster. NOT Core. NOT alpha. ★★
   TQQQ = QQQ 일일수익률 3배를 목표로 하는 *레버리지 베타* 도구일 뿐이다 (§06 §1).
   강세장 폭발력 + 하락/횡보장(daily-reset volatility decay) 파괴 리스크. 검증된 알파가 절대 아니다.
   이 모듈은 매도타이밍 엔진이 아니다 — 증액 *허용/금지 판정* + 축소 *후보 플래그*(파산 방지) +
   Decay Meter / Booster Rent 진단 + 대시보드 필드만 낸다. auto-sell 없음 (축소는 manual decision).

reuse: state 대부분은 engine/a2_risk_dashboard.compute()가 이미 계산
       (leadership_state·market_stress·tqqq_decay·booster_rent·tqqq_realized_multiple·
       qqq_above_ma20/50·realized_vol_20d·qqq_drawdown). 여기서는 중복 계산 금지 —
       dashboard를 import해 재사용하고, TQQQ 전용 add-permission/금지 로직·sleeve MDD·축소 후보·
       trim limit·VXN proxy만 추가.
next-bar: 모든 state는 asof까지 데이터로 계산 → 소비측이 state_t → action_{t+1} (shift(1)).
출력 outputs/a2_live/tqqq_module.json. import용 compute(asof)·CLI main. PAPER·자본권한 0·검증된 알파 아님.
"""
import os, sys, json
import numpy as np, pandas as pd, warnings; warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a2_data
import a2_risk_dashboard as RD

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "outputs", "a2_live"); os.makedirs(OUT, exist_ok=True)
TJSON = os.path.join(OUT, "tqqq_module.json")

# 기본 비중 (§06 §2)
BASE_WEIGHT = 0.35
WEIGHT_RANGE = (0.15, 0.45)
ABS_MAX = 0.50                 # experimental max
# add-permission 게이트 (§06 §3)
A2_DD_ADD_GATE = -0.15        # A2 drawdown -15% 이내여야 증액 허용
# add-ban (§06 §4)
A2_MDD_BAN = -0.20            # A2 MDD -20% 초과 금지
VXN_SPIKE_RVOL = 0.40        # VXN 급등 proxy = realized vol 임계 (VXN 직접 없음 → realized vol proxy·라벨)
# 축소 후보 (§06 §5·파산 방지)
A2_MDD_TRIM = -0.30
SLEEVE_MDD_TRIM = -0.35
LEAD_RED_TRIM_DAYS = 10
DECAY_TRIM_DAYS = 20
# 축소 제한 (§06 §5)
TRIM_ONCE_PCT = -0.05         # 1회 -5%p
TRIM_DAILY_PCT = -0.10        # 하루 최대 -10%p


def _read_book_state():
    p = os.path.join(OUT, "book_state.json")
    try:
        return json.load(open(p))
    except Exception:
        return None


def _sleeve_dd(t, asof, lookback=252):
    """TQQQ sleeve *현재* drawdown proxy = 직전 lookback peak 대비 현재가 (sleeve NAV 미보유 시 근사).
    주의: trailing-year의 worst MDD(min)가 아니라 *현재* peak-to-now 낙폭을 본다. 레버 ETF는 트레일링
    1년 worst MDD가 정상 강세장에서도 -37%대라 trim 트리거를 거짓 발화시킴 → '지금 깊이 물려있나'가 신호."""
    s = t[t.index <= asof].dropna()
    if len(s) < 2:
        return 0.0
    s = s.iloc[-lookback:]
    return float(s.iloc[-1] / s.max() - 1)   # 현재가 / 구간 peak − 1 (현재 낙폭)


def compute(asof=None, weights=None, actual_weight=None,
            leadership_red_days=0, decay_zone_days=0):
    """TQQQ Booster state + add-permission + 축소 후보.

    leadership_red_days/decay_zone_days: 지속일수 (forward runner가 누적 전달·없으면 0).
    반환 dict: add_permission(bool+reason)·add_ban·decay_state·booster_rent·realized_multiple·
               sleeve metrics·축소 후보·trim limits.
    """
    bench = a2_data.benchmarks()
    if asof is None:
        asof = bench.index.max()
    asof = pd.Timestamp(asof)
    t = bench["TQQQ"][bench.index <= asof].dropna()

    # ── dashboard state 재사용 (중복 계산 금지) ──
    rd = RD.compute(asof=asof, weights=weights)
    lead = rd["leadership_state"]
    market = rd["market_stress"]
    above20, above50 = rd["qqq_above_ma20"], rd["qqq_above_ma50"]
    above200 = rd["qqq_above_ma200"]
    rvol = rd["realized_vol_20d"]
    a2_dd = rd["qqq_drawdown"]                       # A2 dd proxy (book_state 있으면 override)
    decay = rd["tqqq_decay"]                         # TQQQ Decay Meter (§06 §6)
    booster_rent = rd["booster_rent"]               # Booster Rent (§06 §7)
    realized_mult = rd["tqqq_realized_multiple"]
    eff_beta = rd["effective_beta"]

    # A2 MDD = live drawdown 기준. book_state의 A2Beta_mdd는 full-backtest(2016~) MDD라
    # add-ban(-20%)/trim(-30%) 트리거를 매일 거짓 발화시킴 → look-ahead 오염이므로 사용 금지.
    # live_A2Beta(인셉션 이후 수익)가 있으면 그 음수폭을 live dd proxy로, 아니면 QQQ live dd 사용.
    bk = _read_book_state()
    if bk is not None and "live_A2Beta" in bk:
        a2_dd = min(a2_dd, float(bk["live_A2Beta"]))   # 더 보수적 (live 기준)
    a2_mdd = a2_dd

    # effective beta RED proxy: eff_beta 매우 높음(>2.5x ≈ 레버 과다) → RED 취급
    eff_beta_red = bool(eff_beta > 2.5)
    # NEG cluster (leadership 중 NEG filing 다수)
    neg_cluster = bool(len(rd.get("neg_leaders", [])) >= 3)
    # VXN 급등 proxy (realized vol)
    vxn_spike = bool(rvol > VXN_SPIKE_RVOL)
    # narrative RED: LLM narrative off-path → 보수적으로 leadership RED를 narrative RED proxy로 사용(라벨)
    narrative_red_proxy = bool(lead == "RED")

    sleeve_mdd = round(_sleeve_dd(t, asof), 4)   # 현재 sleeve 낙폭 (peak-to-now)

    # ── 증액 금지 조건 (§06 §4·먼저 평가 — 금지가 허용보다 우선) ──
    ban_reasons = []
    if lead == "RED":                       ban_reasons.append("Leadership RED")
    if decay:                                ban_reasons.append("TQQQ Decay Zone")
    if market == "RED":                      ban_reasons.append("Market Stress RED")
    if a2_mdd < A2_MDD_BAN:                  ban_reasons.append(f"A2 MDD {A2_MDD_BAN*100:.0f}% 초과")
    if (not above20) and (not above50):      ban_reasons.append("QQQ 20/50일선 동시 이탈")
    if vxn_spike:                            ban_reasons.append(f"VXN 급등 proxy (rvol {rvol*100:.0f}%>{VXN_SPIKE_RVOL*100:.0f}%)")
    if narrative_red_proxy:                  ban_reasons.append("Narrative RED proxy (Leadership RED)")
    add_ban = bool(ban_reasons)

    # ── 증액 허용 조건 (§06 §3·모두 충족 + 금지 아님) ──
    allow_checks = {
        "leadership_GREEN": lead == "GREEN",
        "decay_GREEN": (not decay),
        "market_GREEN_or_YELLOW": market in ("GREEN", "YELLOW"),
        "qqq_above_ma20": above20,
        "qqq_above_ma50": above50,
        "a2_dd_within_-15%": a2_dd > A2_DD_ADD_GATE,
        "eff_beta_not_RED": (not eff_beta_red),
        "no_neg_cluster": (not neg_cluster),
    }
    allow_all = all(allow_checks.values())
    add_permission = bool(allow_all and not add_ban)
    if add_permission:
        add_reason = "허용 (모든 §06 §3 게이트 통과·금지 없음)"
    elif add_ban:
        add_reason = "금지 (§06 §4): " + ", ".join(ban_reasons)
    else:
        failed = [k for k, v in allow_checks.items() if not v]
        add_reason = "보류 (§06 §3 미충족): " + ", ".join(failed)

    # ── 축소 후보 조건 (§06 §5·파산 방지 후보·자동매도 아님) ──
    trim_reasons = []
    if a2_mdd <= A2_MDD_TRIM:                          trim_reasons.append(f"A2 전체 MDD {A2_MDD_TRIM*100:.0f}% 이탈")
    if sleeve_mdd <= SLEEVE_MDD_TRIM:                  trim_reasons.append(f"TQQQ sleeve MDD {SLEEVE_MDD_TRIM*100:.0f}% 이탈")
    if lead == "RED" and leadership_red_days >= LEAD_RED_TRIM_DAYS:
        trim_reasons.append(f"Leadership RED {LEAD_RED_TRIM_DAYS}거래일 지속")
    if decay and decay_zone_days >= DECAY_TRIM_DAYS:
        trim_reasons.append(f"TQQQ Decay Zone {DECAY_TRIM_DAYS}거래일 지속")
    if (not above200) and vxn_spike:
        trim_reasons.append("QQQ 200일선 하회 + VXN 급등 (leaders breakdown 확인 필요)")
    trim_candidate = bool(trim_reasons)

    return {
        "as_of": str(asof.date()),
        "role": "TQQQ Booster — 레버리지 베타(3x daily)·NOT Core·NOT alpha (§06 §1)",
        "weight_actual": round(actual_weight if actual_weight is not None else BASE_WEIGHT, 4),
        "weight_target": round(BASE_WEIGHT, 4),
        "weight_range": list(WEIGHT_RANGE),
        "weight_abs_max": ABS_MAX,
        "contribution_placeholder": round((actual_weight if actual_weight is not None else BASE_WEIGHT) * rd["qqq_20d_ret"] * 3, 4),
        # add permission
        "add_permission": add_permission,
        "add_permission_reason": add_reason,
        "add_permission_checks": allow_checks,
        "add_ban": add_ban,
        "add_ban_reasons": ban_reasons,
        # decay / booster rent
        "decay_state": "ZONE" if decay else "GREEN",
        "decay_meter": bool(decay),
        "decay_action": "증액 금지·Berserker 금지·Profit Vault 우선·Attack size 축소" if decay else "정상",
        "booster_rent_flag": bool(booster_rent),
        "booster_inefficiency": bool(booster_rent),
        "booster_rent_action": "증액 금지·Berserker 금지·Vault 우선·Attack 축소" if booster_rent else "정상",
        "realized_multiple": realized_mult,   # TQQQ 20d ret / QQQ 20d ret (목표 ~3x)
        # sleeve metrics
        "sleeve_mdd": sleeve_mdd,
        "effective_beta": eff_beta,
        "effective_beta_red": eff_beta_red,
        "vxn_spike_proxy": vxn_spike,
        "neg_cluster": neg_cluster,
        "leadership_state": lead,
        "market_stress": market,
        # trim
        "trim_candidate": trim_candidate,
        "trim_reasons": trim_reasons,
        "trim_limit_once_pct": TRIM_ONCE_PCT,
        "trim_limit_daily_pct": TRIM_DAILY_PCT,
        "auto_sell": False,
        "note": "Booster=레버 베타·알파 아님. 증액 판정/축소 후보만 — 자동매도 없음. 축소는 파산 방지 manual decision (1회 -5%p·하루 -10%p 한도).",
    }


def main():
    r = compute()
    print(f"✅ TQQQ Booster {r['as_of']} — 레버 베타(3x)·NOT Core·NOT alpha")
    print(f"   weight {r['weight_actual']*100:.0f}%(target {r['weight_target']*100:.0f}%·range {WEIGHT_RANGE[0]*100:.0f}~{WEIGHT_RANGE[1]*100:.0f}%·absmax {ABS_MAX*100:.0f}%)·effBeta {r['effective_beta']}x·realized_mult {r['realized_multiple']}x")
    print(f"   ADD-PERMISSION: {r['add_permission']}  ({r['add_permission_reason']})")
    print(f"   Decay: {r['decay_state']}  ·  Booster Rent: {r['booster_rent_flag']} ({'비효율' if r['booster_rent_flag'] else 'OK'})  ·  sleeve MDD {r['sleeve_mdd']*100:.1f}%")
    print(f"   Leadership {r['leadership_state']}·Market {r['market_stress']}·VXN-spike(proxy) {r['vxn_spike_proxy']}·NEG cluster {r['neg_cluster']}")
    print(f"   축소후보 {r['trim_candidate']} {r['trim_reasons']} (auto-sell={r['auto_sell']}·한도 1회 {TRIM_ONCE_PCT*100:.0f}%p/일 {TRIM_DAILY_PCT*100:.0f}%p)")
    json.dump(r, open(TJSON, "w"), indent=2, ensure_ascii=False)
    print(f"   → {TJSON} (next-bar: state_t → action_{{t+1}})")


if __name__ == "__main__":
    main()

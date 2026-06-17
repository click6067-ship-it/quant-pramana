#!/usr/bin/env python3
"""PRAMANA A2 — QQQ Core Module (SSOT v2 §05).

QQQ = A2의 기본 성장 베타이자 벤치마크 (SPY는 A2에서 퇴출). Core exposure.
★ 이것은 매도타이밍 엔진이 아니다 (§05 §5): Risk Dashboard가 RED라고 자동으로 전부 팔지 않는다.
   이 모듈은 STATE + 축소 *후보 플래그*(manual decision)만 낸다. auto-sell 없음.

reuse: 대부분 state는 engine/a2_risk_dashboard.compute()가 이미 계산 (MA20/50/200·realized_vol·
       drawdown). 여기서는 중복 계산 금지 — dashboard를 import해 재사용하고, QQQ 전용 필드만 추가:
       relative strength vs SPY (QQQ 63d ret − SPY 63d ret)·gap proxy(close-to-close·intraday 없음·라벨)·
       QQQ vs A2 excess·weight/target/contribution placeholder·축소 후보 플래그.
next-bar: 모든 state는 asof까지 데이터로 계산 → 소비측이 state_t → action_{t+1} (shift(1)).
출력 outputs/a2_live/qqq_module.json. import용 compute(asof)·CLI main. PAPER·자본권한 0·검증된 알파 아님.
"""
import os, sys, json
import numpy as np, pandas as pd, warnings; warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a2_data
import a2_risk_dashboard as RD

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "outputs", "a2_live"); os.makedirs(OUT, exist_ok=True)
QJSON = os.path.join(OUT, "qqq_module.json")

# 기본 비중 (§05 §2)
BASE_WEIGHT = 0.35
WEIGHT_RANGE = (0.25, 0.45)
# 축소 후보 트리거 (§05 §5)
TOTAL_MDD_TRIM = -0.30        # 전체 MDD -30%
PROLONGED_RED_DAYS = 10       # QQQ 200dma 하회 + Leadership RED "장기화"


def _read_book_state():
    """A2 book NAV state (excess / 전체 MDD 입력용). 없으면 None."""
    p = os.path.join(OUT, "book_state.json")
    try:
        return json.load(open(p))
    except Exception:
        return None


def compute(asof=None, weights=None, actual_weight=None):
    """QQQ Core state + 축소 후보 플래그.

    weights: {qqq, tqqq} (effective beta·dashboard용). actual_weight: 현재 QQQ 실비중(없으면 base).
    반환 dict: MA states·drawdown·realized vol·RS vs SPY·gap proxy·QQQ vs A2 excess·축소 후보 플래그.
    """
    bench = a2_data.benchmarks()
    if asof is None:
        asof = bench.index.max()
    asof = pd.Timestamp(asof)
    q = bench["QQQ"][bench.index <= asof].dropna()
    spy = bench["SPY"][bench.index <= asof].dropna()

    # ── dashboard state 재사용 (중복 계산 금지) ──
    rd = RD.compute(asof=asof, weights=weights)
    above20, above50, above200 = rd["qqq_above_ma20"], rd["qqq_above_ma50"], rd["qqq_above_ma200"]
    dd = rd["qqq_drawdown"]
    rvol = rd["realized_vol_20d"]
    lead_state = rd["leadership_state"]

    # ── QQQ 전용: relative strength vs SPY (63d ret 차·SSOT §05 §3) ──
    def ret_nd(s, n):
        return float(s.iloc[-1] / s.iloc[-(n + 1)] - 1) if len(s) > n else 0.0
    q63 = ret_nd(q, 63); spy63 = ret_nd(spy, 63)
    rs_vs_spy = round(q63 - spy63, 4)

    # ── gap proxy (close-to-close·intraday 없음 → 라벨 PROXY·§05 §3 gap-up/down) ──
    gap_proxy = round(float(q.iloc[-1] / q.iloc[-2] - 1), 4) if len(q) > 1 else 0.0

    # ── weight / target / contribution placeholder (실제 book allocator가 채움·§05 §6) ──
    w_actual = actual_weight if actual_weight is not None else BASE_WEIGHT
    w_target = BASE_WEIGHT     # placeholder: 동적 타겟은 allocator 소관
    qqq_20d_ret = rd["qqq_20d_ret"]
    contribution = round(w_actual * qqq_20d_ret, 4)   # 20d 비중가중 기여 placeholder

    # ── QQQ vs A2 excess (book_state의 *live-slice* 사용·§05 §6) ──
    # 주의: A2Beta_ret/qqq_ret은 full-backtest 누적(2016~)이라 live excess가 아님 → live_A2Beta/live_qqq(인셉션 이후) 사용.
    bk = _read_book_state()
    qqq_vs_a2_excess = None
    if bk is not None and "live_qqq" in bk and "live_A2Beta" in bk:
        qqq_vs_a2_excess = round(float(bk["live_qqq"]) - float(bk["live_A2Beta"]), 4)

    # ── 축소 후보 플래그 (§05 §5 — 자동매도 아님·manual review 후보만) ──
    # A2 전체 MDD = live drawdown 기준 (full-backtest MDD를 쓰면 -30% 트리거가 매일 거짓 발화 → look-ahead 오염).
    # book_state에 live MDD 필드가 없으면 QQQ live drawdown(dd)을 보수적 proxy로 사용.
    total_mdd = dd
    crash_lockout = bool(rd["market_stress"] == "RED" and dd < TOTAL_MDD_TRIM)
    below200_and_red = bool((not above200) and lead_state == "RED")  # 200dma 하회 + Leadership RED(장기화는 상태기록 필요·후보)
    trim_reasons = []
    if crash_lockout:
        trim_reasons.append("A2 Crash Lockout")
    if total_mdd <= TOTAL_MDD_TRIM:
        trim_reasons.append(f"전체 MDD {TOTAL_MDD_TRIM*100:.0f}% 이탈")
    if below200_and_red:
        trim_reasons.append("QQQ 200dma 하회 + Leadership RED(장기화 확인 필요)")
    trim_candidate = bool(trim_reasons)

    return {
        "as_of": str(asof.date()),
        "role": "QQQ Core (기본 성장 베타·벤치마크·NOT 매도타이밍 엔진)",
        "weight_actual": round(w_actual, 4),
        "weight_target": round(w_target, 4),
        "weight_range": list(WEIGHT_RANGE),
        "contribution_placeholder": contribution,
        "ma20_above": bool(above20), "ma50_above": bool(above50), "ma200_above": bool(above200),
        "ma_state": ("ABOVE_ALL" if (above20 and above50 and above200)
                     else "BELOW_ALL" if not (above20 or above50 or above200)
                     else "MIXED"),
        "drawdown": round(dd, 4),
        "realized_vol_20d": round(rvol, 4),
        "qqq_20d_ret": qqq_20d_ret,
        "rs_vs_spy_63d": rs_vs_spy,
        "rs_label": ("OUTPERFORM" if rs_vs_spy > 0 else "UNDERPERFORM"),
        "gap_proxy_close_to_close": gap_proxy,
        "gap_note": "close-to-close proxy (intraday OHLC 없음 — open gap 아님·라벨 PROXY)",
        "qqq_vs_a2_excess": qqq_vs_a2_excess,
        "leadership_state": lead_state,
        "market_stress": rd["market_stress"],
        "trim_candidate": trim_candidate,
        "trim_reasons": trim_reasons,
        "auto_sell": False,
        "note": "Core exposure. RED라고 자동매도 안 함 (§05 §5). 축소는 manual review 후보만.",
    }


def main():
    r = compute()
    json.dump(r, open(QJSON, "w"), indent=2, ensure_ascii=False)
    rs = r["rs_vs_spy_63d"]
    print(f"✅ QQQ Core {r['as_of']} — weight {r['weight_actual']*100:.0f}%(target {r['weight_target']*100:.0f}%·range {WEIGHT_RANGE[0]*100:.0f}~{WEIGHT_RANGE[1]*100:.0f}%)·contrib(plc) {r['contribution_placeholder']*100:+.2f}%")
    print(f"   MA: 20{'↑' if r['ma20_above'] else '↓'}/50{'↑' if r['ma50_above'] else '↓'}/200{'↑' if r['ma200_above'] else '↓'} ({r['ma_state']})·DD {r['drawdown']*100:.1f}%·rvol {r['realized_vol_20d']*100:.0f}%")
    print(f"   RS vs SPY(63d) {rs*100:+.2f}%p ({r['rs_label']})·gap(c2c) {r['gap_proxy_close_to_close']*100:+.2f}%·QQQ vs A2 excess {('%+.2f%%'%(r['qqq_vs_a2_excess']*100)) if r['qqq_vs_a2_excess'] is not None else 'n/a'}")
    print(f"   Leadership {r['leadership_state']}·Market {r['market_stress']}·축소후보 {r['trim_candidate']} {r['trim_reasons']} (auto-sell={r['auto_sell']}·Core는 자동매도 안 함)")
    print(f"   → {QJSON} (next-bar: state_t → action_{{t+1}})")


if __name__ == "__main__":
    main()

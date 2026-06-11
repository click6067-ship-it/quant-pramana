#!/usr/bin/env python3
"""Phase 2 M6 — Research Engine kill module. 사전등록 kill 조건 템플릿 + verdict 적용기 *만*.
규율: 새 kill 0 · 임계값 변경 0 · 메트릭 계산 0(evaluate.py 호출 결과 m을 받음) · API 0.
정의 출처(verbatim): b2b5_broad/quality_quarantine/phase1b/us_event_drift/b_smallmid의 kill 로직.
각 kill = (key, label, predicate(m)->bool). m = evaluate summary(+실험별 extra) dict. fire되면 FAIL/DEAD."""

KILL_SETS = {
    # Broad_Universe_Factor_Retest_Protocol (b2b5_broad)
    "broad_retest": [
        ("net_le0",            "net≤0",          lambda m: m["net_ls"] <= 0),
        ("icir_lt20",          "IC-IR<0.2",      lambda m: not (abs(m["icir"]) >= 0.20)),
        ("turnover_excess",    "turnover과도",    lambda m: m["turnover"] > 6),
        ("small_concentration","소형집중",        lambda m: abs(m["iclo"]) > 0.02 and abs(m["ichi"]) < 0.01),
    ],
    # quality quarantine (5-test)
    "quality_quarantine": [
        ("cost2x_le0",         "2x cost net≤0",            lambda m: m["net2_ls"] <= 0),
        ("sign_flip",          "전후반 방향 불일치",         lambda m: (m["s1"] > 0) != (m["s2"] > 0)),
        ("small_concentration","소형 몰빵",                lambda m: abs(m["iclo"]) > 0.03 and abs(m["ichi"]) < 0.005),
        ("longonly_cw_le0",    "long-only active≤0(vs CW)", lambda m: (m["act_cw"]) <= 0),
        ("longleg_1n_le0",     "long-leg≤0(vs 1/N)",       lambda m: (m["act_ew"]) <= 0),
        ("sector_concentration","sector 과집중",            lambda m: m["sector_max"] > 0.5),
    ],
    # phase1b low-DoF challenger
    "phase1b": [
        ("net_cw_le0",         "net active vs CW≤0",        lambda m: m["net_cw"] <= 0),
        ("rec_icir_lt10",      "2021-26 IC-IR<0.10",        lambda m: not (m["rec_icir"] >= 0.10)),
        ("turnover_noedge",    "turnover과도&무edge",        lambda m: m["turnover"] > 2.5 and m["net_cw"] <= 0),
        ("concentrated_early", "2016-20에만 집중",           lambda m: m["rec_net"] <= 0),
        ("sector_neutral_le0", "sector중립화후 net≤0",       lambda m: m["sn_net_cw"] <= 0),
        ("longonly_cw_neg",    "long-only vs CW 음수",       lambda m: m["act_cw"] < 0),
    ],
    # us_event_drift
    "event": [
        ("net_cw_le0",         "net active vs CW≤0",        lambda m: m["net_cw"] <= 0),
        ("rec_icir_lt10",      "2021-26 IC-IR<0.10",        lambda m: not (m["rec_icir"] >= 0.10)),
        ("cost2x_le0",         "2x cost net≤0",             lambda m: m["net2_cw"] <= 0),
        ("concentrated_early", "2016-20에만 집중",           lambda m: m["rec_net"] <= 0),
        ("longonly_cw_neg",    "long-only vs CW 음수",       lambda m: m["act_cw"] <= 0),
        ("sector_neutral_le0", "sector중립화후 net≤0",       lambda m: m["sn_net_cw"] <= 0),
    ],
    # US small/mid cost-first (8 kills)
    "smallmid": [
        ("net_cw_le0",         "net active vs CW≤0",        lambda m: m["net_cw"] <= 0),
        ("net_ls_le0",         "net Q5-Q1≤0",               lambda m: m["net_ls"] <= 0),
        ("icir_lt20",          "IC-IR<0.20",                lambda m: not (m["icir"] >= 0.20)),
        ("recent_dead",        "2021-26 사망",               lambda m: m["rec_net"] <= 0 or not (m["rec_icir"] >= 0.10)),
        ("cost2x_le0",         "2x cost 사망",               lambda m: m["net2_cw"] <= 0),
        ("lowest_liq_only",    "최저유동성에만 존재",          lambda m: m["lo_liq_net_ls"] > 0 and m["hi_liq_net_ls"] <= 0),
        ("turnover_weak",      "turnover>300%&net약",        lambda m: m["turnover"] > 3.0 and m["net_cw"] < 0.02),
        ("needs_short",        "short leg 필요(long-only 안됨)", lambda m: m["net_cw"] <= 0 and m["net_ls"] > 0),
    ],
}

PASS_WORD = {"broad_retest": "SURVIVE", "quality_quarantine": "PASS", "phase1b": "PASS", "event": "유망", "smallmid": "PASS"}
FAIL_WORD = {"broad_retest": "DEAD", "quality_quarantine": "FAIL", "phase1b": "FAIL", "event": "FAIL", "smallmid": "FAIL"}

def apply(name, m):
    """m(metrics dict) → (fired_keys, fired_labels, verdict_word, passed)."""
    fired = [(k, lbl) for k, lbl, fn in KILL_SETS[name] if fn(m)]
    passed = len(fired) == 0
    return [k for k, _ in fired], [lbl for _, lbl in fired], (PASS_WORD[name] if passed else FAIL_WORD[name]), passed

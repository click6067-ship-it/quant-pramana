#!/usr/bin/env python3
"""PRAMANA AX — Master Trial Registry (family-wise·sleeve 순서·global error budget).

정본: PRAMANA_V4/AX0_Protocol.md §6 · council/2026-06-14_aggressive-pivot/plan.md.
역할: "S1 죽으면 S2 시도"도 family search → 나중 sleeve 성공은 global hurdle 통과 전엔 family-adjusted exploratory.
append-only(폐기 variant 포함)·sleeve 고정 순서·sleeve 내 no-replacement. PAPER·자본권한 0.
사용: python engine/ax_registry.py [--status]
"""
import os, sys, json, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "outputs", "ax0"); os.makedirs(OUT, exist_ok=True)
REG = os.path.join(OUT, "trial_registry.json")

# 고정 순서(Protocol §6) — 변경 금지. global error budget = sleeve당 1회 시도.
SLEEVE_ORDER = ["S1_long_convex", "S2_conviction_calib", "S3_directional_brokervalid", "S4_short_vol"]
MAX_ATTEMPTS_PER_SLEEVE = 1
GLOBAL_ALPHA = 0.10            # family-wise error budget (4 sleeve에 분배 = sleeve당 0.025·Bonferroni류)


def _now():
    # 결정적: 날짜는 호출 인자/파일 mtime 대신 명시 기록 회피 → today 사용(런타임 1회)
    return dt.date.today().isoformat()


def load():
    if os.path.exists(REG):
        try: return json.load(open(REG))
        except Exception: pass
    reg = {"created": _now(), "sleeve_order": SLEEVE_ORDER, "global_alpha": GLOBAL_ALPHA,
           "per_sleeve_alpha": round(GLOBAL_ALPHA / len(SLEEVE_ORDER), 4),
           "active": SLEEVE_ORDER[0], "trials": [], "graveyard": []}
    json.dump(reg, open(REG, "w"), indent=2, ensure_ascii=False)
    return reg


def register_trial(sleeve, status, note="", n=0, today=None):
    """trial 기록(append-only). status=OPEN/GRADUATED/DEAD/EXPLORATORY."""
    reg = load(); today = today or _now()
    attempts = [t for t in reg["trials"] if t["sleeve"] == sleeve]
    if len(attempts) >= MAX_ATTEMPTS_PER_SLEEVE and status == "OPEN":
        return {"ok": False, "reason": f"{sleeve} 최대 시도({MAX_ATTEMPTS_PER_SLEEVE}) 초과·no-replacement"}
    reg["trials"].append({"sleeve": sleeve, "status": status, "n_independent": n,
                          "note": note, "date": today,
                          "reporting": "family-adjusted exploratory" if status in ("OPEN", "EXPLORATORY") else status})
    if status == "DEAD":
        reg["graveyard"].append({"sleeve": sleeve, "date": today, "note": note})
        # 다음 sleeve로 active 이동
        i = SLEEVE_ORDER.index(sleeve) if sleeve in SLEEVE_ORDER else -1
        reg["active"] = SLEEVE_ORDER[i + 1] if 0 <= i < len(SLEEVE_ORDER) - 1 else "NONE(all sleeves exhausted)"
    json.dump(reg, open(REG, "w"), indent=2, ensure_ascii=False)
    return {"ok": True, "active": reg["active"]}


def family_adjusted_note(sleeve):
    """이 sleeve의 성공을 어떻게 보고해야 하나(global hurdle 전엔 exploratory)."""
    return (f"{sleeve} 성공 = global family-wise hurdle(α={GLOBAL_ALPHA}·per-sleeve {GLOBAL_ALPHA/len(SLEEVE_ORDER):.3f}) "
            f"통과 전엔 'family-adjusted exploratory'로만 보고. 여러 sleeve 시도 후 하나 통과 = 우연 가능.")


def main():
    reg = load()
    print(f"✅ AX Trial Registry (created {reg['created']})")
    print(f"   sleeve 순서: {' → '.join(reg['sleeve_order'])}")
    print(f"   global α={reg['global_alpha']}·per-sleeve {reg['per_sleeve_alpha']}·max attempts/sleeve {MAX_ATTEMPTS_PER_SLEEVE}")
    print(f"   active = {reg['active']} · trials {len(reg['trials'])} · graveyard {len(reg['graveyard'])}")
    for t in reg["trials"][-6:]:
        print(f"     [{t['date']}] {t['sleeve']}: {t['status']} (n={t['n_independent']}·{t['reporting']}) {t['note'][:40]}")
    print("   " + family_adjusted_note(reg["active"]))


if __name__ == "__main__":
    main()

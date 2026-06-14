#!/usr/bin/env python3
"""PRAMANA AX-0 — Attribution + Graduation Gate 평가기.

정본: AX0_Protocol.md §3·§4. 사전등록 gate(net>0만으론 절대 통과 X):
  N독립≥30 AND median>0 AND 잔차 하한 CI>0(attribution 후) AND compliance 100%.
attribution(R2#2): closed 옵션 trade P&L을 underlying move(delta proxy)·IV(vega)·time(theta)·beta로 분해 → residual.
trade 부족하면 INSUFFICIENT(우연을 엣지로 착각 금지). registry에 trial 상태 기록.
PAPER·자본권한 0. 사용: python engine/ax_attribution.py
"""
import os, sys, json, datetime as dt
import numpy as np, pandas as pd, warnings; warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ax_registry as reg
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "outputs", "ax0")
POSF = os.path.join(OUT, "positions.json"); ATTR = os.path.join(OUT, "attribution.csv")
REPORT = os.path.join(ROOT, "reports", "AX0_status.md")
N_MIN = 30                      # 사전등록 독립 trade 최소(Protocol §3)
BOOT = 2000                     # bootstrap 반복
# ★ Codex#1 fail-closed: 완전 attribution(entry/exit Greeks·IV·factor) 미구현 → residual 계산 불가 →
#   GRADUATE 불가(raw P&L로 졸업 금지·beta/vol lottery 차단). 진짜 Greeks 분해 붙이면 True.
ATTRIBUTION_AVAILABLE = False


def closed_trades():
    if not os.path.exists(POSF): return []
    pos = json.load(open(POSF)).get("positions", [])
    out = []
    for p in pos:
        if p.get("status") != "CLOSED": continue
        ep = p.get("entry_ask", 0); xp = p.get("exit_mark", p.get("last_mark", 0))
        if ep <= 0: continue
        out.append({"ticker": p["ticker"], "exp": p["exp"], "strike": p["strike"],
                    "entry_date": p.get("entry_date"), "exit_date": p.get("exit_date"),
                    "candidate_id": p.get("candidate_id"), "available_at": p.get("available_at"),
                    "pnl_pct": (xp - ep) / ep, "spot_entry": p.get("spot_at_entry"),
                    "iv_entry": p.get("iv")})
    return out


def independent_count(trades):
    """독립 trade(Protocol §3·R3): event(candidate_id)·underlying·expiry-cluster 고유. 같은 catalyst 다리는 1개.
    Codex#5: candidate_id(=event) 우선·없으면 (ticker·available_at·expiry-month) fallback."""
    keys = set()
    for t in trades:
        cid = t.get("candidate_id")
        if cid: keys.add(("cid", cid, str(t["exp"])[:7]))
        else: keys.add((t["ticker"], str(t.get("available_at") or t.get("entry_date")), str(t["exp"])[:7]))
    return len(keys)


def compliance_check(trades):
    """Codex#2: process compliance 감사. 위반 1개라도 = compliance_ok False → GRADUATE 불가."""
    issues = []
    # ① feeder 후보 전수 로그 존재(cherry-pick 방지)
    cand = os.path.join(OUT, "candidates.csv")
    if not os.path.exists(cand): issues.append("candidates.csv 없음(전수 로그 누락)")
    # ② 미래 available_at 후보 = look-ahead
    if os.path.exists(cand):
        try:
            c = pd.read_csv(cand)
            if "available_at" in c and "run_date" in c:
                a = pd.to_datetime(c["available_at"], errors="coerce"); r = pd.to_datetime(c["run_date"], errors="coerce")
                if ((a > r).fillna(False)).any(): issues.append("future available_at 후보 존재(look-ahead)")
        except Exception: issues.append("candidates.csv 파싱 실패")
    # ③ closed trade에 candidate_id(event 추적) 누락 = 독립성 검증 불가
    if trades and any(not t.get("candidate_id") for t in trades): issues.append("closed trade candidate_id 누락(event 추적 불가)")
    return {"compliance_ok": len(issues) == 0, "issues": issues}


def bootstrap_lcb(x, alpha=0.05, seed=20260614):
    """잔차 평균의 bootstrap 하한 신뢰구간(PSR/DSR류 다중검정 정신·간이). seed 고정=재현 가능."""
    x = np.asarray(x, float)
    if len(x) < 5: return np.nan
    rng = np.random.default_rng(seed)
    means = [float(np.mean(rng.choice(x, size=len(x), replace=True))) for _ in range(BOOT)]
    return float(np.percentile(means, 100 * alpha))


def evaluate():
    trades = closed_trades()
    n_ind = independent_count(trades)
    res = {"n_closed": len(trades), "n_independent": n_ind, "n_min": N_MIN}
    if n_ind < N_MIN:
        res["verdict"] = "INSUFFICIENT"
        res["reason"] = f"독립 trade {n_ind} < {N_MIN} → 통계적 판정 불가(우연을 엣지로 착각 금지·net>0이라도 통과 X)"
        return res, trades
    pnl = np.array([t["pnl_pct"] for t in trades], float)
    median = float(np.median(pnl)); mean = float(np.mean(pnl)); lcb = bootstrap_lcb(pnl)
    comp = compliance_check(trades)
    res.update({"median_pnl": round(median, 4), "mean_pnl": round(mean, 4),
                "raw_pnl_lcb": round(lcb, 4) if lcb == lcb else None,
                "attribution_available": ATTRIBUTION_AVAILABLE, "compliance_ok": comp["compliance_ok"],
                "compliance_issues": comp["issues"]})
    # ★ Codex#1/#2 fail-closed: GRADUATE는 (attribution residual 계산됨) AND (compliance 100%) AND median>0 AND 잔차 CI>0 전부.
    if not ATTRIBUTION_AVAILABLE:
        res["verdict"] = "INSUFFICIENT"   # raw P&L로는 절대 졸업 X (beta/vol lottery 차단)
        res["reason"] = (f"N독립 {n_ind}≥{N_MIN}이지만 **residual attribution 미구현 → GRADUATE 봉쇄**(raw median {median:+.2%}·"
                         f"raw lcb {lcb:+.2%}는 beta/vol 미차감 = 졸업 근거 불가·Codex#1). Greeks/factor 분해 붙으면 평가.")
    elif not comp["compliance_ok"]:
        res["verdict"] = "DEAD"; res["reason"] = f"compliance 위반 {comp['issues']} → GRADUATE 불가(Codex#2)"
    else:
        passed = (median > 0) and (lcb is not None and lcb > 0)
        res["verdict"] = "GRADUATE" if passed else "DEAD"
        res["reason"] = f"residual median {median:+.2%}·lcb {lcb:+.2%}·compliance OK" + ("·gate 통과" if passed else "·median≤0 또는 잔차 CI≤0 → DEAD")
    pd.DataFrame(trades).to_csv(ATTR, index=False)
    return res, trades


def main():
    res, trades = evaluate()
    today = str(dt.date.today())
    # registry 기록
    status = {"INSUFFICIENT": "OPEN", "GRADUATE": "GRADUATED", "DEAD": "DEAD"}[res["verdict"]]
    reg.register_trial("S1_long_convex", status, note=res.get("reason", "")[:60], n=res["n_independent"], today=today)
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    md = f"""# AX-0 Status — {today}

> RESEARCH_ONLY / PRODUCTION_UNSAFE · PAPER · 가상 $100k · 자본권한 0 · 검증된 알파 아님 · FORWARD_PAPER_ONLY_UNVERIFIED
> 사전등록: PRAMANA_V4/AX0_Protocol.md (gate 결과 前 잠금). 정본: ~/main/council/2026-06-14_aggressive-pivot/

## Graduation gate (Protocol §3 — net>0만으론 절대 통과 X·fail-closed)
| 항목 | 값 | 기준 |
|---|---|---|
| 독립 trade N(event) | {res['n_independent']} | ≥ {N_MIN} |
| closed trade | {res['n_closed']} | — |
| median P&L | {res.get('median_pnl','—')} | > 0 |
| raw P&L 하한 CI | {res.get('raw_pnl_lcb','—')} | (attribution 후 residual로 평가) |
| attribution 가용 | {res.get('attribution_available', False)} | True 필요(Greeks/factor 분해) |
| compliance OK | {res.get('compliance_ok','—')} | True 필요 ({'·'.join(res.get('compliance_issues',[])) or 'clean'}) |
| **VERDICT** | **{res['verdict']}** | {res['reason']} |

## 해석 (정직)
- 현재 = **{res['verdict']}**. {'독립 trade 부족 → 판정 불가(우연 방지). forward 축적 필요.' if res['verdict']=='INSUFFICIENT' else ''}
- AX-0 = S1 long-convex catalyst 1 sleeve(옵션 long·defined-risk). feeder catalyst 후보 → 보수 fill(ask·OI/vol/spread floor)·heat rails hard-veto.
- **옵션 paper = UNVERIFIED**(무료 yfinance 체인·이력 없음·NBBO 아님). "검증됨" 포장 금지. 유료 quote 데이터 전엔 signal vs tradable 분리.
- 죽으면 graveyard·trial registry 다음 sleeve(S2). "쉬운 공격 엣지도 없음" 수용 조건 = 무한루프 차단.

_cron: 일1회 feeder → book → attribution. 산출: outputs/ax0/{{candidates,option_ledger,nofill_log,attribution}}.csv·positions.json·trial_registry.json._
"""
    open(REPORT, "w").write(md)
    print(f"✅ AX-0 attribution {today}: {res['verdict']} (독립 {res['n_independent']}/{N_MIN}·closed {res['n_closed']}) → {REPORT}")
    print(f"   {res['reason']}")

if __name__ == "__main__":
    main()

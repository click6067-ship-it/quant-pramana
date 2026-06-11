#!/usr/bin/env python3
"""M8 회귀 게이트 — config 하나로 과거 실험(M1~M7) 재실행 → 동결 숫자/verdict 재현 + 표준 리포트.
ndl 없음·키 없이. 앵커: b2b5_broad 4슬리브(broad_retest) + small/mid 3신호(smallmid)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd, data, run as RUN, report as RP

OUT = os.path.join(data.PHASE1A, "outputs"); ENG = os.path.join(OUT, "engine")
def ap(a, b, tol, label):
    ok = (not np.isnan(a)) and abs(a - b) <= tol
    print(f"    {label:16s} 재현={a:+.5f} 기존={b:+.5f} {'✅' if ok else '❌'}")
    return ok

CFGS = [
    dict(name="B2_value",    bundle="broad", rank=(1,1500), score={"kind":"raw","feature":"value"},
         dropna=["score","fwd"], cost_tier="marketcap", kill_set="broad_retest", ref=("b2b5","B2_value")),
    dict(name="B3_quality",  bundle="broad", rank=(1,1500), score={"kind":"raw","feature":"quality"},
         dropna=["score","fwd"], cost_tier="marketcap", kill_set="broad_retest", ref=("b2b5","B3_quality")),
    dict(name="B4_momentum", bundle="broad", rank=(1,1500), score={"kind":"raw","feature":"momentum"},
         dropna=["score","fwd"], cost_tier="marketcap", kill_set="broad_retest", ref=("b2b5","B4_momentum")),
    dict(name="B5_lowvol",   bundle="broad", rank=(1,1500), score={"kind":"raw","feature":"lowvol"},
         dropna=["score","fwd"], cost_tier="marketcap", kill_set="broad_retest", ref=("b2b5","B5_lowvol")),
    dict(name="sm_quality",  bundle="smallmid", rank=(1001,3000), score={"kind":"raw","feature":"quality"},
         dropna=["score","fwd","mc","adv"], cost_tier="adv", kill_set="smallmid", min_names=100,
         filters={"price_min":5,"adv_floor_q":0.10}, ref=("smallmid","quality")),
    dict(name="sm_event",    bundle="smallmid", rank=(1001,3000), score={"kind":"composite_event"},
         dropna=["score","fwd","mc","adv"], cost_tier="adv", kill_set="smallmid", min_names=100,
         composite_predropna=False, filters={"price_min":5,"adv_floor_q":0.10}, ref=("smallmid","event")),
    dict(name="sm_blend",    bundle="smallmid", rank=(1001,3000),
         score={"kind":"composite","components":["value","quality","momentum","lowvol"]},
         dropna=["score","fwd","mc","adv"], cost_tier="adv", kill_set="smallmid", min_names=100,
         composite_predropna=False, filters={"price_min":5,"adv_floor_q":0.10}, ref=("smallmid","blend")),
]

def main():
    print("="*84); print("Phase 2 M8 — 회귀 게이트 (config→M1~M7 재실행→동결 재현, 키 없이)"); print("="*84)
    b2b5 = pd.read_csv(os.path.join(OUT, "b2b5_broad_result.csv")).set_index("sleeve")
    smref = pd.read_csv(os.path.join(OUT, "us_smallmid_result.csv")).set_index("signal")
    rows = []; ok = True
    for cfg in CFGS:
        res = RUN.run_experiment(cfg); s = res["summary"]; rows.append(res["row"])
        kind, key = cfg["ref"]
        print(f"\n[{cfg['name']}] verdict={res['verdict']} kills={res['kill_keys']}")
        if kind == "b2b5":
            r = b2b5.loc[key]
            ok &= ap(s["net_ls"], float(r["net_ann"]), 1e-5, "net_ann")
            ok &= ap(s["icir"], float(r["ic_ir"]), 1e-5, "ic_ir")
            ok &= ap(s["turnover"], float(r["turnover_ann"]), 1e-5, "turnover_ann")
            exp_surv = str(r["verdict"]).startswith("SURVIVE"); got_surv = (res["verdict"] == "SURVIVE")
            print(f"    verdict {'✅' if exp_surv==got_surv else '❌'} (기존 {'SURVIVE' if exp_surv else 'DEAD'})")
            ok &= (exp_surv == got_surv)
        else:
            r = smref.loc[key]
            ok &= ap(s["net_cw"]*100, float(r["net_cw_%"]), 0.02, "net_cw %")
            ok &= ap(s["icir"], float(r["icir"]), 5e-3, "icir")
            print(f"    verdict {'✅' if res['verdict']=='FAIL' else '❌'} (기존 FAIL)")
            ok &= (res["verdict"] == "FAIL")
    # M7 표준 리포트 출력
    RP.write_csv(rows, os.path.join(ENG, "regression_report.csv"))
    md = RP.render_md("Engine Regression Report (M8)", rows, note="config-driven 재실행 결과(동결 재현).")
    RP.write_md(md, os.path.join(ENG, "regression_report.md"))
    print(f"\n  M7 리포트 → engine/regression_report.csv · regression_report.md ({len(rows)} rows)")
    print("\n" + "="*84)
    print(f"판정: {'PASS — config로 7실험 동결 숫자/verdict 재현 + 표준 리포트 출력, API-free' if ok else 'FAIL — 불일치'}")
    return ok

if __name__ == "__main__":
    sys.exit(0 if main() else 1)

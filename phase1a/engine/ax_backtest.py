#!/usr/bin/env python3
"""PRAMANA AX — Historical backtest (S1 modeled-option · S2 calibration · S3 directional).

forward 대기 불가(용하) → 과거 캐시 일봉으로 실험. 정본 AX0_Protocol.md·council/2026-06-14_aggressive-pivot.
catalyst = event_store POS 8-K 2.02(실적)/1.01(중요계약)·available_at→next bar 진입(PIT·look-ahead 차단).
  S3 Directional = 기초자산 spot long/lever/short (캐시 일봉 = REAL 데이터).
  S1 Convex = BS-MODELED 옵션(5% OTM·35DTE·IV=trailing 21d 실현변동성 proxy) → **MODELED_OPTION_BS_IVPROXY**(실 옵션가 아님).
  S2 Conviction-calibration = momentum 방향 예측 vs 실현 → Brier/calibration.
attribution(ax_greeks): 옵션 P&L = Δ·dS + gamma + vega·dIV + theta·dt + residual → 잔차로 edge 판정.
사전등록 gate(net>0만으론 통과 X): N독립≥30·median>0·잔차 하한 CI>0. S1/S2/S3 = registry 3 trial(family-wise).
PAPER·자본권한 0·검증된 알파 아님. 사용: python engine/ax_backtest.py [--cost-bp 1.0]
"""
import os, sys, json, hashlib, datetime as dt
import numpy as np, pandas as pd, warnings; warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a2_data, ax_greeks as gk, ax_registry as reg
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "outputs", "ax0"); os.makedirs(OUT, exist_ok=True)
EVT = os.path.join(ROOT, "outputs", "a2_events", "event_store.csv")
REPORT = os.path.join(ROOT, "reports", "AX_historical_backtest.md")
SUMM = os.path.join(OUT, "historical_summary.json")

POS_CATALYST = {"2.02", "1.01"}
HOLD = 21                 # 보유 horizon(거래일)·옵션 35DTE와 정합
DTE = 35; OTM = 0.05; R = 0.04
TARGET, STOP = 1.00, -0.50
N_MIN = 30; BOOT = 2000; OPT_COST = 0.05   # 옵션 round-trip cost = entry premium의 5%(보수)


def bootstrap_lcb(x, alpha=0.05, seed=20260614):
    x = np.asarray(x, float)
    if len(x) < 5: return float("nan")
    rng = np.random.default_rng(seed)
    return float(np.percentile([np.mean(rng.choice(x, len(x), replace=True)) for _ in range(BOOT)], 100 * alpha))


def catalyst_events():
    ev = pd.read_csv(EVT); ev = ev[ev["source"] == "edgar"].copy()
    ev["available_at"] = pd.to_datetime(ev["available_at"], errors="coerce"); ev = ev.dropna(subset=["available_at"])
    ev["codes"] = ev["item_code"].astype(str)
    pos = ev[(ev["label"] == "POS") &
             (ev["codes"].apply(lambda x: bool(set(str(x).replace(" ", "").split(",")) & POS_CATALYST)))]
    return pos[["ticker", "available_at", "codes"]].drop_duplicates()


def build_spot(tickers):
    """이벤트 종목 spot = a2_data 두 universe에서 종목별 (dates, close ndarray)."""
    pxmap = {}
    for u in ("sp500", "smallmid"):
        p = a2_data.price_panel(u, min_date="2015-06-01")
        p = p[p["ticker"].isin(tickers)][["ticker", "date", "close_adj"]]
        for t, s in p.groupby("ticker", sort=False):
            if t in pxmap: continue
            s = s.sort_values("date")
            pxmap[t] = (s["date"].values.astype("datetime64[ns]"), s["close_adj"].values.astype(float))
    return pxmap


def realized_vol(cls, i, win=21):
    """i 시점까지 trailing win일 실현변동성(연율). 미래 미사용."""
    if i < win + 1: return np.nan
    rets = np.diff(np.log(cls[i - win:i + 1]))
    return float(np.std(rets) * np.sqrt(252)) if len(rets) > 2 else np.nan


def simulate_option(cls, dts, i0, entry_spot):
    """i0(entry) 기준 5% OTM call·35 CALENDAR DTE BS 모델·일별 reprice(IV=daily trailing 실현변동성)·exit 룰.
    ★ Codex#2: T는 캘린더 경과일(거래일 카운터 아님)·theta 정확. attribution=entry premium 대비 return 단위·IV 가드."""
    K = entry_spot * (1 + OTM); iv0 = realized_vol(cls, i0)
    if not iv0 or np.isnan(iv0) or iv0 < 0.10 or iv0 > 2.0: return None   # IV proxy 가드
    p0 = gk.price(entry_spot, K, DTE / 365, iv0, R, kind="call")
    if p0 < 0.02 * entry_spot: return None   # premium floor
    n = len(cls); exit_i = None; exit_px = None; reason = None; d0 = dts[i0]
    for j in range(i0 + 1, n):
        cal = (pd.Timestamp(dts[j]) - pd.Timestamp(d0)).days     # ★ 캘린더 경과일
        if cal > DTE: break
        T = max(1e-6, (DTE - cal) / 365); ivj = realized_vol(cls, j)
        ivj = ivj if (ivj and ivj > 0 and not np.isnan(ivj)) else iv0
        pj = gk.price(cls[j], K, T, ivj, R, kind="call"); pnl = pj / p0 - 1
        if pnl >= TARGET: exit_i, exit_px, reason = j, pj, "+100% target"; break
        if pnl <= STOP: exit_i, exit_px, reason = j, pj, "-50% stop"; break
        if cal >= DTE - 5: exit_i, exit_px, reason = j, pj, "time stop"; break
    if exit_i is None:
        exit_i = min(i0 + HOLD, n - 1)
        if exit_i <= i0: return None
        cal = (pd.Timestamp(dts[exit_i]) - pd.Timestamp(d0)).days; T = max(1e-6, (DTE - cal) / 365)
        ivx = realized_vol(cls, exit_i); ivx = ivx if (ivx and ivx > 0 and not np.isnan(ivx)) else iv0
        exit_px = gk.price(cls[exit_i], K, T, ivx, R, kind="call"); reason = "horizon"
    ivx = realized_vol(cls, exit_i); ivx = ivx if (ivx and ivx > 0 and not np.isnan(ivx)) else iv0
    attr = gk.attribute(entry_spot, cls[exit_i], K, DTE / 365, (exit_i - i0) / 365, iv0, ivx, R, "call")
    gross = exit_px / p0 - 1; net = gross - OPT_COST
    # ★ attribution = entry premium 대비 return 단위로 정규화(스케일·블로업 방지) + winsorize
    def w(x): return float(np.clip(x / p0, -5.0, 5.0))
    return {"entry_px": p0, "exit_px": exit_px, "iv0": round(iv0, 3), "ivx": round(ivx, 3),
            "gross_pnl": gross, "net_pnl": net, "reason": reason, "K": K, "exit_i": exit_i,
            "attr_delta": w(attr["delta_pnl"]), "attr_gamma": w(attr["gamma_pnl"]), "attr_vega": w(attr["vega_pnl"]),
            "attr_theta": w(attr["theta_pnl"]), "attr_residual": w(attr["residual"])}


def main():
    cost_bp = float(sys.argv[sys.argv.index("--cost-bp") + 1]) if "--cost-bp" in sys.argv else 1.0
    spot_cost = cost_bp / 10000.0
    if not os.path.exists(EVT): print("⛔ event_store 없음"); return
    ev = catalyst_events()
    pxmap = build_spot(ev["ticker"].unique().tolist())
    bench = a2_data.benchmarks()["QQQ"]; bdates = bench.index.values.astype("datetime64[ns]"); bvals = bench.values.astype(float)
    def basof(d):
        k = np.searchsorted(bdates, np.datetime64(d), side="right") - 1
        return bvals[k] if k >= 0 else np.nan
    s3, s1, s2, seen = [], [], [], set()
    for _, e in ev.iterrows():
        t = e["ticker"]
        if t not in pxmap: continue
        dts, cls = pxmap[t]
        i = np.searchsorted(dts, np.datetime64(e["available_at"]), side="right")   # available_at 다음 bar = entry
        if i < 30 or i + HOLD >= len(dts): continue
        cid = hashlib.sha256(f"{t}|{pd.Timestamp(e['available_at']).date()}".encode()).hexdigest()[:12]
        if cid in seen: continue
        seen.add(cid)
        entry = cls[i]; exit_h = cls[min(i + HOLD, len(dts) - 1)]
        mom21 = cls[i - 1] / cls[i - 22] - 1 if i >= 22 else 0.0     # 신호일 직전 momentum(미래 미사용)
        pred_up = mom21 >= 0
        # S3 directional (REAL spot)
        sret = exit_h / entry - 1
        be, bx = basof(dts[i]), basof(dts[min(i + HOLD, len(dts) - 1)])
        bret = (bx / be - 1) if (be and bx and be > 0) else 0.0
        s3.append({"cid": cid, "ticker": t, "exp_month": str(dts[i])[:7], "long_net": sret - spot_cost,
                   "long_excess": (sret - spot_cost) - bret, "lev3_net": 3 * sret - spot_cost, "short_net": -sret - spot_cost})
        # S2 calibration (방향 예측 vs 실현)·ex-ante prob = momentum 기반(systematic proxy·재량은 forward-only)
        p_up = float(0.5 + 0.5 * np.tanh(mom21 * 3))
        s2.append({"cid": cid, "pred_up": bool(pred_up), "realized_up": bool(sret > 0), "p": p_up})
        # S1 convex (MODELED option)
        opt = simulate_option(cls, dts, i, entry)
        if opt: s1.append({"cid": cid, "ticker": t, "exp_month": str(dts[i])[:7], **opt})

    def cluster(df, cols):
        """Codex#3: (ticker·exp_month) 독립 클러스터당 1관측(평균) — 상관 반복 이벤트가 N/LCB 부풀리는 것 차단."""
        if not len(df): return {c: np.array([]) for c in cols}, 0
        agg = df.groupby(["ticker", "exp_month"], sort=False)[cols].mean()
        return {c: agg[c].values for c in cols}, len(agg)

    def gate(x_arr, label, directional=None, residual=None, n_clusters=None):
        """net median>0 AND net LCB>0 (클러스터 단위). S1은 추가로 directional(Δ) LCB>0 AND residual LCB>0
        (옵션 P&L이 vega/theta/convexity 아티팩트가 아니라 catalyst 방향+잔차 edge에서 나와야·Codex#1·protocol §4)."""
        x = np.asarray(x_arr, float); n = n_clusters if n_clusters is not None else len(x)
        if n < N_MIN: return {"n": n, "verdict": "INSUFFICIENT", "reason": f"독립 클러스터 {n}<{N_MIN}"}
        med = float(np.median(x)); lcb = bootstrap_lcb(x); mean = float(np.mean(x))
        passed = med > 0 and lcb > 0; out = {"n": n, "mean": round(mean, 4), "median": round(med, 4), "net_lcb": round(lcb, 4)}
        if directional is not None:
            d = np.asarray(directional, float); dlcb = bootstrap_lcb(d); dmed = float(np.median(d))
            r = np.asarray(residual, float); rlcb = bootstrap_lcb(r); rmed = float(np.median(r))
            passed = passed and dlcb > 0 and rlcb > 0    # directional + residual 둘 다 (protocol §4)
            out.update({"delta_median": round(dmed, 4), "delta_lcb": round(dlcb, 4),
                        "resid_median": round(rmed, 4), "resid_lcb": round(rlcb, 4)})
            out["reason"] = f"net med {med:+.3f}/lcb {lcb:+.3f}·Δ lcb {dlcb:+.3f}·resid lcb {rlcb:+.3f}"
        else:
            out["reason"] = f"net med {med:+.3f}/lcb {lcb:+.3f}"
        out["verdict"] = "GRADUATE" if passed else "DEAD"
        return out

    # S3 (클러스터 독립·Codex#3)
    s3df = pd.DataFrame(s3)
    if len(s3df):
        c3, nc3 = cluster(s3df, ["long_excess", "lev3_net", "short_net"])
        g_long = gate(c3["long_excess"], "S3_long", n_clusters=nc3)
        g_lev = gate(c3["lev3_net"], "S3_lev3", n_clusters=nc3)
        g_short = gate(c3["short_net"], "S3_short", n_clusters=nc3)
    else:
        g_long = {"n": 0, "verdict": "INSUFFICIENT"}; g_lev = {"n": 0}; g_short = {"n": 0}
    # S1 (directional + residual attribution gate·클러스터·ATTRIBUTION_AVAILABLE True)
    s1df = pd.DataFrame(s1)
    if len(s1df):
        c1, nc1 = cluster(s1df, ["net_pnl", "attr_delta", "attr_residual"])
        g_s1 = gate(c1["net_pnl"], "S1", directional=c1["attr_delta"], residual=c1["attr_residual"], n_clusters=nc1)
    else:
        g_s1 = {"n": 0, "verdict": "INSUFFICIENT"}
    # S2 calibration (Brier)
    s2df = pd.DataFrame(s2)
    brier = float(np.mean((s2df["p"].astype(float) - s2df["realized_up"].astype(float)) ** 2)) if len(s2df) else None
    hit = float((s2df["pred_up"] == s2df["realized_up"]).mean()) if len(s2df) else None

    # registry: S1/S2/S3 trial 기록(family-wise·Codex#5 S2도 기록)
    s2_verdict = "DEAD" if (hit is not None and hit <= 0.55) else "OPEN"   # calibration 무정보(hit≈0.5)=diagnostic DEAD
    reg.register_trial("S1_long_convex", {"GRADUATE": "GRADUATED", "DEAD": "DEAD"}.get(g_s1.get("verdict"), "OPEN"),
                       note=f"hist modeled-opt: {g_s1.get('reason','')[:50]}", n=g_s1.get("n", 0))
    reg.register_trial("S2_conviction_calib", s2_verdict,
                       note=f"hist momentum calib hit {hit} brier {round(brier,3) if brier else None}(systematic proxy·재량 forward-only)", n=len(s2df))
    reg.register_trial("S3_directional_brokervalid", {"GRADUATE": "GRADUATED", "DEAD": "DEAD"}.get(g_long.get("verdict"), "OPEN"),
                       note=f"hist spot long excess: {g_long.get('reason','')[:50]}", n=g_long.get("n", 0))

    summary = {"as_of": str(dt.date.today()), "n_events": len(ev), "n_event_tickers": int(ev["ticker"].nunique()),
               "coverage_note": "EDGAR 표본(~200종 leadership+attack 빈출·a2_event_store)·전종목 survivorship 증명 아님",
               "cost_bp": cost_bp,
               "S3_long_excess": g_long, "S3_lev3_net": g_lev, "S3_short_net": g_short,
               "S1_modeled_option": g_s1, "S2_calibration": {"n": len(s2df), "brier": round(brier, 4) if brier else None,
                                                              "hit_rate": round(hit, 4) if hit else None},
               "S1_attribution_means": {k: round(float(s1df[k].mean()), 4) for k in
                                        ["attr_delta", "attr_gamma", "attr_vega", "attr_theta", "attr_residual", "net_pnl"]} if len(s1df) else {}}
    json.dump(summary, open(SUMM, "w"), indent=2, ensure_ascii=False, default=float)
    write_report(summary)
    print(f"✅ AX historical backtest: events {len(ev)}·S3 long n={g_long.get('n')}/{g_long.get('verdict')}·"
          f"S1 modeled-opt n={g_s1.get('n')}/{g_s1.get('verdict')}·S2 calib hit={summary['S2_calibration']['hit_rate']}")
    print(f"   S3 long excess {g_long.get('median','-')}(med)·lev3 {g_lev.get('median','-')}·short {g_short.get('median','-')}")
    if len(s1df): print(f"   S1 attribution 평균: Δ {summary['S1_attribution_means']['attr_delta']:+.3f}·theta {summary['S1_attribution_means']['attr_theta']:+.3f}·vega {summary['S1_attribution_means']['attr_vega']:+.3f}·resid {summary['S1_attribution_means']['attr_residual']:+.3f} → {REPORT}")


def write_report(s):
    g1 = s["S1_modeled_option"]; gl = s["S3_long_excess"]; gv = s["S3_lev3_net"]; gs = s["S3_short_net"]; c = s["S2_calibration"]
    am = s.get("S1_attribution_means", {})
    md = f"""# AX Historical Backtest — {s['as_of']}

> RESEARCH_ONLY / PRODUCTION_UNSAFE · PAPER · 자본권한 0 · 검증된 알파 아님. 사전등록 PRAMANA_V4/AX0_Protocol.md.
> 옵션(S1) = **MODELED_OPTION_BS_IVPROXY**(과거 옵션가 데이터 없음·BS+trailing 실현변동성 IV proxy = 가정·실 체결/IV크러시 아님). S3 = 캐시 일봉 = REAL.
> catalyst = EDGAR POS 8-K 2.02/1.01·available_at→next bar(PIT). 비용 옵션 round-trip {OPT_COST*100:.0f}%·spot {s['cost_bp']}bp. 이벤트 {s['n_events']}건.
> **커버리지(Codex#4): EDGAR 표본 {s.get('n_event_tickers','?')}종**(leadership+attack 빈출·a2_event_store)·**전종목 survivorship 증명 아님**. N = (ticker·expiry-month) **독립 클러스터** 수(Codex#3·상관 반복 제거).

## 사전등록 gate(net>0만으론 통과 X: N≥30·median>0·net LCB>0; S1은 추가로 directional Δ LCB>0 **AND** residual LCB>0·protocol §4)
| sleeve | N(클러스터) | median | net LCB | Δ LCB | resid LCB | VERDICT |
|---|---|---|---|---|---|---|
| **S3 long (spot·REAL·excess vs QQQ)** | {gl.get('n')} | {gl.get('median','-')} | {gl.get('net_lcb','-')} | — | — | **{gl.get('verdict')}** |
| S3 lev3 (3x spot net) | {gv.get('n')} | {gv.get('median','-')} | {gv.get('net_lcb','-')} | — | — | {gv.get('verdict','-')} |
| S3 short (−spot net) | {gs.get('n')} | {gs.get('median','-')} | {gs.get('net_lcb','-')} | — | — | {gs.get('verdict','-')} |
| **S1 modeled-option (Δ+residual gate)** | {g1.get('n')} | {g1.get('median','-')} | {g1.get('net_lcb','-')} | {g1.get('delta_lcb','-')} | {g1.get('resid_lcb','-')} | **{g1.get('verdict')}** |

## S1 옵션 P&L attribution 평균 (Greeks 분해·{am.get('net_pnl','-') if am else '-'} net)
Δ(directional) {am.get('attr_delta','-')} · gamma {am.get('attr_gamma','-')} · vega(IV) {am.get('attr_vega','-')} · theta(decay) {am.get('attr_theta','-')} · residual {am.get('attr_residual','-')}
→ 옵션 P&L이 directional(Δ)이 아니라 theta/vega(decay·변동성)로 설명되면 = catalyst edge 아님.

## S2 conviction calibration (momentum 방향 예측 vs 실현)
N {c.get('n')}·hit rate {c.get('hit_rate')}(≈0.5면 무정보)·Brier {c.get('brier')}(낮을수록 좋음·0.25=무정보 기준).
재량(discretionary) calibration은 forward-only(과거 사람판단 없음) → 여기는 *systematic momentum 신호*의 방향 정보량만.

## 결론 (정직)
- {'S3 directional·S1 modeled-option 모두 DEAD/INSUFFICIENT' if (gl.get('verdict')!='GRADUATE' and g1.get('verdict')!='GRADUATE') else '일부 SURVIVE → 추가검증'} = 8세대 + A2 Attack DEAD 일관(catalyst-momentum spot edge 없음 → 레버·옵션도 그 위에선 못 살림).
- **S1 정직 caveat:** 모델 옵션은 IV proxy·constant-ish·실 IV 크러시(어닝 후 급락) 미반영 → **실제는 더 나쁨**(이 결과가 오히려 낙관). residual gate가 directional 아닌 vega/theta 아티팩트를 걸러냄.
- family-wise(S1/S3 = registry trial): 한 sleeve 통과해도 global hurdle 전엔 exploratory.
- 다음: GRADUATE면 forward broker-valid 검증 / DEAD면 graveyard·registry 다음 칸. "쉬운 공격 엣지 없음" 수용 조건 = 무한루프 차단.
"""
    os.makedirs(os.path.dirname(REPORT), exist_ok=True); open(REPORT, "w").write(md)


if __name__ == "__main__":
    main()

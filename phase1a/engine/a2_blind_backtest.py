#!/usr/bin/env python3
"""PRAMANA A2 — Blind/PIT Backtest engine (Attack Stage-A daily proxy + Moonshot event proxy).

설계 정본: pramana_a2_delta_patch_pack/02_ATTACK_MOONSHOT_BLIND_BACKTEST.md.
규율(이 엔진이 강제):
  1) available_at <= decision_time 데이터만 사용 (feature_store·event_store가 available_at 보유).
  2) signal_time < execution_time. same-bar/same-close 체결 금지 → 신호=close(t), 진입=next bar(t+1), 청산=t+1+h.
  3) decision_log(planned-only·미래정보 없음) + outcome_log(realized fwd 분리)·둘 다 동결캐시서 결정적 재생성(run_id·universe별).
  4) NEG filing PIT gate (event_store) — Attack은 NEG 종목 제외, Moonshot은 절대 제외.
  5) 사전등록 kill 조건은 결과 보기 前 박음(아래 PREREG). 결과로 조건 안 바꿈(goalpost 불변).

데이터 한계(정직):
  - Sharadar=daily backbone → 분봉 ORB/VWAP/RVOL 과거검증 불가(02 §2·§4). 여기는 Stage-A DAILY PROXY만.
  - smallmid: OHLC 없음 → gap=close-to-close PROXY·진입=next close. sp500: open 있음 → gap=open/prev_close·진입=next open.
  - EDGAR 이벤트 = 표본 200종(인프라 완비·전종목 크롤은 rate-limit). Moonshot=event-study 탐색(소표본).
PAPER·자본권한 0. 검증된 알파 아님(이 엔진은 negative를 정직히 보고하는 기계).
사용: python engine/a2_blind_backtest.py [--universe smallmid|sp500] [--cost-bp 20]
"""
import os, sys, json, hashlib, datetime as dt
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a2_data, a2_feature_store as fs

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DEC = os.path.join(ROOT, "outputs", "a2_decisions"); os.makedirs(DEC, exist_ok=True)
EVT = os.path.join(ROOT, "outputs", "a2_events", "event_store.csv")
DLOG = os.path.join(DEC, "decision_log.csv")
SUMMARY = os.path.join(DEC, "blind_backtest_summary.json")
HORIZONS = [1, 3, 5, 10]

# ── 사전등록(PRE-REGISTERED) kill 조건 — 결과 보기 前 잠금 (AlphaLab v1 계보) ──
PREREG = {
    "attack": {
        "primary_horizon": 5,
        "triggers": {"gap_min": 0.04, "rvol_min": 2.0, "mom21_min": 0.0, "dollar_vol_min": 3_000_000},
        "neg_lookback_days": 90,
        "kill_if": ["net mean excess(primary h) <= 0", "net median excess(primary h) < 0",
                    "net win-rate(excess>0) < 50%", "candidate net edge <= universe baseline net drift"],
    },
    "moonshot": {
        "horizons": [21, 63],
        "event_types": {"POS": ["1.01", "425", "DEFM14A"], "NEG_as_reversal": ["1.03", "4.02"]},
        "min_reward_risk_observed": 3.0,
        "kill_if": ["no event-type shows asymmetric payoff (mean upside / mean downside < ~2)",
                    "sample too small for inference (n<30 per type) → INSUFFICIENT not PASS"],
    },
}


def _hash(*parts):
    return hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()[:16]


def _neg_set_by_date(decision_dates, lookback_days=90):
    """각 decision_date별 PIT NEG 종목 set (event_store NEG·available_at<=date·직전 lookback). 전종목 아닌 표본 커버리지."""
    if not os.path.exists(EVT):
        return {}, 0
    ev = pd.read_csv(EVT, usecols=["ticker", "label", "available_at"])
    ev = ev[ev["label"] == "NEG"].copy()
    if ev.empty:
        return {}, 0
    ev["available_at"] = pd.to_datetime(ev["available_at"], errors="coerce")
    ev = ev.dropna(subset=["available_at"])
    out = {}
    for d in decision_dates:
        dd = pd.Timestamp(d); lo = dd - pd.Timedelta(days=lookback_days)
        out[d] = set(ev.loc[(ev["available_at"] <= dd) & (ev["available_at"] > lo), "ticker"].unique())
    return out, ev["ticker"].nunique()


def run_attack(universe="smallmid", cost_bp=20.0, write_decisions=True):
    """Attack Stage-A daily proxy. 신호=close(t)·진입=next bar·청산=t+1+h. NEG PIT 제외. label=ATTACK_DAILY_PROXY."""
    pr = PREREG["attack"]; tr = pr["triggers"]
    panel = fs.build_feature_panel(universe, min_date="2016-01-01", min_dollar_vol=tr["dollar_vol_min"])
    has_open = "open_adj" in panel.columns
    g = panel.groupby("ticker", sort=False)
    # next-bar 진입가 + 청산가 (ticker 내 shift) — same-bar 금지
    entry = g["open_adj"].shift(-1) if has_open else g["close_adj"].shift(-1)   # 진입 = t+1 (open or close)
    panel["entry_px"] = entry
    panel["entry_date"] = g["date"].shift(-1)
    for h in HORIZONS:
        exit_px = g["close_adj"].shift(-(1 + h))     # 청산 = t+1+h close
        panel[f"fwd_{h}"] = exit_px / panel["entry_px"] - 1.0
    # 벤치마크 forward (QQQ/SPY calendar) — entry_date 기준 동일 horizon
    bench = a2_data.benchmarks()[["QQQ", "SPY"]].copy()
    bfwd = {}
    for h in HORIZONS:
        bfwd[("QQQ", h)] = (bench["QQQ"].shift(-h) / bench["QQQ"] - 1.0)
        bfwd[("SPY", h)] = (bench["SPY"].shift(-h) / bench["SPY"] - 1.0)
    bench_df = pd.DataFrame({f"qqq_fwd_{h}": bfwd[("QQQ", h)] for h in HORIZONS})
    for h in HORIZONS:
        bench_df[f"spy_fwd_{h}"] = bfwd[("SPY", h)]
    bench_df.index.name = "entry_date"; bench_df = bench_df.reset_index()
    # 후보 마스크 (사전등록 트리거)
    trig = ((panel["gap_pct"] >= tr["gap_min"]) & (panel["rvol20"] >= tr["rvol_min"]) & (panel["ret_21d"] >= tr["mom21_min"]))
    ph0 = pr["primary_horizon"]
    n_trigger = int(trig.sum())                                                   # return 필터 前 후보 수
    n_no_exit = int((trig & (panel["entry_px"].isna() | panel[f"fwd_{ph0}"].isna())).sum())  # 진입/청산가 없음(상폐/halt/공백) → 제외 = censoring
    cand = panel[trig & panel["entry_px"].notna() & panel[f"fwd_{ph0}"].notna()].copy()
    # NEG PIT 제외 (표본 커버리지)
    neg_map, neg_cov = _neg_set_by_date(sorted(cand["date"].dt.date.astype(str).unique()), pr["neg_lookback_days"])
    if neg_map:
        cand["dstr"] = cand["date"].dt.date.astype(str)
        cand["is_neg"] = [t in neg_map.get(d, set()) for t, d in zip(cand["ticker"], cand["dstr"])]
        n_excl = int(cand["is_neg"].sum()); cand = cand[~cand["is_neg"]]
    else:
        n_excl = 0
    cand = cand.merge(bench_df, on="entry_date", how="left")
    # cost: round-trip bp
    cost = cost_bp / 10000.0
    res = {}
    for h in HORIZONS:
        s = cand[f"fwd_{h}"]; q = cand[f"qqq_fwd_{h}"]; sp = cand[f"spy_fwd_{h}"]
        net = s - cost
        exq = (net - q).dropna(); exs = (net - sp).dropna()
        res[h] = {"n": int(s.notna().sum()),
                  "gross_mean": float(s.mean()), "gross_median": float(s.median()),
                  "net_mean": float(net.mean()), "net_median": float(net.median()),
                  "excess_qqq_mean": float(exq.mean()), "excess_qqq_median": float(exq.median()),
                  "excess_spy_mean": float(exs.mean()),
                  "win_rate_net": float((net > 0).mean()), "win_rate_excess_qqq": float((exq > 0).mean())}
    # universe baseline net drift (전 liquid stock-day·필터 없음) — 후보 edge 대조군
    base = {}
    for h in HORIZONS:
        b = (panel[f"fwd_{h}"].dropna() - cost)
        base[h] = {"net_mean": float(b.mean()), "net_median": float(b.median()), "n": int(len(b))}
    # decision_log(planned-only) + outcome_log(realized) — universe별 파일·동결캐시서 결정적 재생성(run_id). Codex fix: 덮어쓰기/미래값 혼입 제거.
    if write_decisions and len(cand):
        ph = pr["primary_horizon"]
        run_id = _hash("attack", universe, cost_bp, str(dt.date.today()))
        dl = cand[["ticker", "date", "entry_date", "gap_pct", "rvol20", "ret_21d", f"fwd_{ph}", f"qqq_fwd_{ph}"]].copy()
        dl["run_id"] = run_id; dl["as_of"] = str(dt.date.today())
        dl["strategy_type"] = f"ATTACK_DAILY_PROXY_{universe}"
        dl["decision"] = "ENTER_NEXT_BAR"
        dl["decision_time"] = dl["date"].dt.strftime("%Y-%m-%d") + "T16:00:00ET(close)"
        dl["planned_execution_time"] = dl["entry_date"].dt.strftime("%Y-%m-%d") + ("T-open" if has_open else "T-close")
        dl["features_used_hash"] = [_hash(g_, r_, m_) for g_, r_, m_ in zip(dl["gap_pct"].round(4), dl["rvol20"].round(2), dl["ret_21d"].round(4))]
        dl["events_used_hash"] = _hash("neg_gate", neg_cov, pr["neg_lookback_days"])
        dl["decision_id"] = [_hash(t, d) for t, d in zip(dl["ticker"], dl["date"].dt.date.astype(str))]
        if len(dl) > 120000: dl = dl.sort_values("decision_time").tail(120000)
        dlog_u = DLOG.replace(".csv", f"_{universe}.csv")
        olog_u = os.path.join(DEC, f"outcome_log_{universe}.csv")
        # decision_log = 의사결정 시점 정보만(미래 실현값 없음)
        dl[["run_id", "as_of", "decision_id", "decision_time", "ticker", "strategy_type",
            "features_used_hash", "events_used_hash", "decision", "planned_execution_time"]].to_csv(dlog_u, index=False)
        # (legacy combined decision_log.csv 제거 — Codex hygiene: 파일명만 planned인데 미래값 섞이는 혼동 차단)
        # outcome_log = 실현 forward return(별도·미래값 격리)
        dl[["run_id", "decision_id", "ticker", f"fwd_{ph}", f"qqq_fwd_{ph}"]].rename(
            columns={f"fwd_{ph}": "realized_fwd_5", f"qqq_fwd_{ph}": "realized_qqq_fwd_5"}).to_csv(olog_u, index=False)
    return {"universe": universe, "gap_kind": panel["_gap_kind"].iloc[0], "entry": "next_open" if has_open else "next_close",
            "cost_bp": cost_bp, "n_candidates": int(len(cand)), "n_neg_excluded": n_excl, "neg_coverage_tickers": neg_cov,
            "n_trigger_before_return_filter": n_trigger, "n_dropped_no_exit_censoring": n_no_exit,
            "censoring_note": "상폐/halt/가격공백으로 forward 없는 후보 제외 = survivorship censoring → 평균 낙관 편향 가능(DEAD 결론은 오히려 강화·convex 주장은 약화)",
            "by_horizon": res, "universe_baseline": base, "prereg": pr}


def run_moonshot(cost_bp=20.0):
    """Moonshot event proxy (event-study). EDGAR 이벤트 available_at 다음 bar 진입·21/63d 페이오프 분포. PIT·소표본 탐색."""
    pr = PREREG["moonshot"]
    if not os.path.exists(EVT):
        return {"error": "event_store 없음"}
    ev = pd.read_csv(EVT)
    ev = ev[ev["source"] == "edgar"].copy()
    ev["available_at"] = pd.to_datetime(ev["available_at"], errors="coerce")
    ev = ev.dropna(subset=["available_at"])
    tks = set(ev["ticker"].unique().tolist())
    # 이벤트 종목 가격 → 종목별 (dates ndarray, close ndarray) dict (searchsorted·event당 O(log n))
    pxmap = {}
    for u in ("sp500", "smallmid"):
        p = a2_data.price_panel(u, min_date="2015-06-01")
        p = p[p["ticker"].isin(tks)][["ticker", "date", "close_adj"]]
        for t, sub in p.groupby("ticker", sort=False):
            sub = sub.sort_values("date")
            if t in pxmap:   # 두 universe 중복 → 첫 것 유지(sp500 우선)
                continue
            pxmap[t] = (sub["date"].values.astype("datetime64[ns]"), sub["close_adj"].values.astype(float))
    bench = a2_data.benchmarks()["QQQ"]
    bdates = bench.index.values.astype("datetime64[ns]"); bvals = bench.values.astype(float)
    def _basof(d):   # benchmark asof (<=d)
        i = np.searchsorted(bdates, np.datetime64(d), side="right") - 1
        return bvals[i] if i >= 0 else np.nan
    def fwd_after(ticker, avail, h):
        if ticker not in pxmap: return np.nan, np.nan, np.nan
        dts, cls = pxmap[ticker]
        i0 = np.searchsorted(dts, np.datetime64(avail), side="right")   # avail 다음 bar = 진입
        if i0 + h >= len(dts): return np.nan, np.nan, np.nan
        entry = cls[i0]; exit_p = cls[i0 + h]
        if not (entry > 0): return np.nan, np.nan, np.nan
        r = exit_p / entry - 1.0
        be = _basof(dts[i0]); bx = _basof(dts[i0 + h])
        br = (bx / be - 1.0) if (be and bx and be > 0) else np.nan
        return r, br, dts[i0]
    cost = cost_bp / 10000.0
    # 이벤트 타입 그룹
    groups = {"POS_material(1.01/425/DEFM14A)": ev[ev["item_code"].astype(str).str.contains("1.01") |
                                                   ev["form_type"].isin(["425", "DEFM14A"])],
              "NEG_bankruptcy/accounting(1.03/4.02)": ev[ev["item_code"].astype(str).str.contains("1.03|4.02", regex=True)],
              "POS_earnings(2.02)": ev[ev["item_code"].astype(str).str.contains("2.02")],
              "NEG_dilution(S-3/424B/3.02)": ev[ev["form_type"].str.startswith("S-3") |
                                                ev["form_type"].str.startswith("424B") |
                                                ev["item_code"].astype(str).str.contains("3.02")]}
    out = {}
    for gname, gdf in groups.items():
        gdf = gdf.drop_duplicates(["ticker", "available_at"])
        rows = []
        for _, r in gdf.iterrows():
            for h in pr["horizons"]:
                rr, br, ed = fwd_after(r["ticker"], r["available_at"], h)
                if not np.isnan(rr):
                    rows.append({"h": h, "ret": rr - cost, "excess": (rr - cost) - (br if not np.isnan(br) else 0)})
        if not rows:
            out[gname] = {"n": 0, "note": "표본 내 가격 매칭 없음"}; continue
        rdf = pd.DataFrame(rows)
        g = {}
        for h in pr["horizons"]:
            hh = rdf[rdf["h"] == h]
            sub = hh["excess"]        # ★ beta-stripped (QQQ 차감) = 진짜 edge 측정 (raw는 3개월 시장drift 포함→오도)
            raw = hh["ret"]
            if len(sub) < 5: g[h] = {"n": int(len(sub))}; continue
            up = sub[sub > 0]; dn = sub[sub < 0]
            asym = float(up.mean() / abs(dn.mean())) if len(dn) and dn.mean() != 0 else float("nan")
            g[h] = {"n": int(len(sub)), "excess_mean": float(sub.mean()), "excess_median": float(sub.median()),
                    "raw_mean": float(raw.mean()), "p_up20": float((raw >= 0.20).mean()), "p_dn20": float((raw <= -0.20).mean()),
                    "asymmetry_up_over_dn": asym, "win_rate_excess": float((sub > 0).mean())}
        out[gname] = g
    return {"cost_bp": cost_bp, "event_tickers": len(tks), "by_group": out, "prereg": pr,
            "note": "EDGAR 표본 200종 event-study·소표본 탐색(전종목 아님)·look-ahead 없음(available_at 다음 bar)"}


def verdict_attack(a):
    """사전등록 kill 대조 (goalpost 불변)."""
    ph = a["prereg"]["primary_horizon"]; r = a["by_horizon"][ph]; b = a["universe_baseline"][ph]
    fails = []   # 사전등록 ①~④ (순서 고정·코드=PREREG text)
    if r["excess_qqq_mean"] <= 0: fails.append(f"① net mean excess vs QQQ(h{ph})={r['excess_qqq_mean']*100:.2f}% ≤ 0")
    if r["excess_qqq_median"] < 0: fails.append(f"② net median excess vs QQQ(h{ph})={r['excess_qqq_median']*100:.2f}% < 0")
    if r["win_rate_excess_qqq"] < 0.50: fails.append(f"③ net win-rate vs QQQ(h{ph})={r['win_rate_excess_qqq']*100:.1f}% < 50%")
    if r["net_mean"] <= b["net_mean"]: fails.append(f"④ 후보 net drift {r['net_mean']*100:.2f}% ≤ universe baseline {b['net_mean']*100:.2f}%")
    return ("DEAD" if fails else "SURVIVE-screen(추가검증 필요)"), fails


def main():
    uni = sys.argv[sys.argv.index("--universe") + 1] if "--universe" in sys.argv else "smallmid"
    cost = float(sys.argv[sys.argv.index("--cost-bp") + 1]) if "--cost-bp" in sys.argv else 20.0
    print(f"=== A2 Blind Backtest (universe={uni}·cost={cost}bp·PIT next-bar) ===")
    print("사전등록 kill(결과 前 잠금):", PREREG["attack"]["kill_if"])
    atk = run_attack(uni, cost)
    v, fails = verdict_attack(atk)
    ph = atk["prereg"]["primary_horizon"]; r = atk["by_horizon"][ph]
    print(f"\n[ATTACK Stage-A daily proxy · {atk['gap_kind']} · entry={atk['entry']}]")
    print(f"  후보 {atk['n_candidates']:,}건 (트리거 {atk['n_trigger_before_return_filter']:,}·forward없어 제외 {atk['n_dropped_no_exit_censoring']:,}=상폐/halt censoring·NEG 제외 {atk['n_neg_excluded']:,}·NEG coverage {atk['neg_coverage_tickers']}종)")
    for h in HORIZONS:
        x = atk["by_horizon"][h]
        print(f"  h{h:<2d} n={x['n']:>7,} net_mean={x['net_mean']*100:+.2f}% exQQQ_mean={x['excess_qqq_mean']*100:+.2f}% "
              f"exQQQ_med={x['excess_qqq_median']*100:+.2f}% win(ex)={x['win_rate_excess_qqq']*100:.0f}% | base_net={atk['universe_baseline'][h]['net_mean']*100:+.2f}%")
    print(f"  ★ VERDICT(h{ph}) = {v}")
    for f in fails: print(f"     ✗ {f}")
    moon = run_moonshot(cost)
    print(f"\n[MOONSHOT event proxy · EDGAR 표본 {moon.get('event_tickers','?')}종 · event-study]")
    for gname, g in moon.get("by_group", {}).items():
        line = []
        for h in PREREG["moonshot"]["horizons"]:
            x = g.get(h, {})
            if x.get("n", 0) >= 5:
                line.append(f"h{h}: n={x['n']} excess_mean={x['excess_mean']*100:+.1f}% exc_med={x['excess_median']*100:+.1f}% "
                            f"asym={x['asymmetry_up_over_dn']:.2f} win(ex)={x['win_rate_excess']*100:.0f}% [raw {x['raw_mean']*100:+.1f}%]")
            else:
                line.append(f"h{h}: n={x.get('n',0)}(소표본)")
        print(f"  {gname}: " + " | ".join(line))
    summary = {"as_of": str(dt.date.today()), "attack": atk, "attack_verdict": v, "attack_fails": fails, "moonshot": moon}
    spath = SUMMARY.replace(".json", f"_{uni}.json")
    json.dump(summary, open(spath, "w"), indent=2, ensure_ascii=False, default=float)
    json.dump(summary, open(SUMMARY, "w"), indent=2, ensure_ascii=False, default=float)
    print(f"\n✅ summary → {spath} (+ {SUMMARY}) · decision_log → {DLOG.replace('.csv', f'_{uni}.csv')} (planned-only) + outcome_log_{uni}.csv (realized)")
    print("정직: 분봉 ORB/VWAP/RVOL 과거검증 불가(daily proxy만)·smallmid gap=close proxy·EDGAR 표본·검증된 알파 아님.")


if __name__ == "__main__":
    main()

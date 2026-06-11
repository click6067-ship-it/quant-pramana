#!/usr/bin/env python3
"""Phase 2 P3.3(B) — paper-ready simulator (인프라). config → paper-trade-ready NAV/PnL.
long-only quantile EW 사이징 · 월 리밸런스 · 체결비용(cost.py tier × |Δw|) · 결정적 risk-veto 훅 · 벤치(CW·1/N).
규율: 새 알파/feature/kill 0 · API 0 · **no live/paper 승격**(현재 통과 edge 0; 이건 edge보다 앞선 인프라).
주의: FAIL한 신호로 돌려도 됨 — *배관 검증*이지 거래 추천이 아님."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd, data, universe as U, run as RUN, cost as C

def risk_veto(w, max_name=0.05, max_gross=1.0):
    """결정적 리스크 veto(최종 권한): per-name 상한·gross 상한. 기본=5%/100%(long-only)."""
    w = w.clip(upper=max_name)
    g = w.sum()
    if g > max_gross:
        w = w * (max_gross / g)
    return w

def simulate(cfg, quantile=0.2, max_name=0.05, init_nav=100.0):
    B = RUN._bundle(cfg["bundle"]); sector = data.load_tickers()["sector"]
    uni = U.rank_universe(*cfg["rank"])
    members = {d: set(g) for d, g in uni.groupby("asof")["ticker"]}; rebal = sorted(uni["asof"].unique())
    L = RUN.assemble_panel(cfg, B, members, rebal, sector)
    recs = []; prev_w = pd.Series(dtype=float); nav_g = nav_n = init_nav
    for t, g0 in L.groupby("asof"):
        g = g0.dropna(subset=["score", "fwd", "mc"])
        if cfg.get("cost_tier") == "adv": g = g.dropna(subset=["adv"])
        if len(g) < cfg.get("min_names", 30): continue
        rk = g["score"].rank(pct=True); held = g[rk >= 1 - quantile].set_index("ticker")
        w = pd.Series(1.0 / len(held), index=held.index)            # long-only EW (실거래형)
        w = risk_veto(w, max_name=max_name); w = w / w.sum()         # veto 후 재정규화
        c_one = (C.tier_adv_bps(held["adv"]) if cfg.get("cost_tier") == "adv" else C.tier_marketcap_bps(held["mc"])) / C.BPS
        dw = w.subtract(prev_w, fill_value=0.0).abs()
        tcost = float((dw * c_one.reindex(dw.index).fillna(c_one.mean())).sum())   # 체결비용 = Σ|Δw|·tier
        r_g = float((w * held["fwd"]).sum())
        r_n = r_g - tcost
        bcw = (g["mc"] * g["fwd"]).sum() / g["mc"].sum(); bew = g["fwd"].mean()
        nav_g *= (1 + r_g); nav_n *= (1 + r_n)
        recs.append(dict(t=t, ret_g=r_g, ret_n=r_n, cost=tcost, n=len(held), turnover=dw.sum() / 2,
                         nav_n=nav_n, bench_cw=bcw, bench_ew=bew))
        prev_w = w
    S = pd.DataFrame(recs).set_index("t")
    # 벤치 NAV
    S["bnav_cw"] = init_nav * (1 + S["bench_cw"]).cumprod(); S["bnav_ew"] = init_nav * (1 + S["bench_ew"]).cumprod()
    m = 12; n = len(S)
    def ann(x): return (1 + x).prod() ** (m / n) - 1
    dd = (S["nav_n"] / S["nav_n"].cummax() - 1).min()
    sharpe = S["ret_n"].mean() / S["ret_n"].std() * np.sqrt(m) if S["ret_n"].std() > 0 else np.nan
    act = S["ret_n"] - S["bench_cw"]
    summary = dict(n=n, cagr_gross=ann(S["ret_g"]), cagr_net=ann(S["ret_n"]),
                   vol=S["ret_n"].std() * np.sqrt(m), sharpe=sharpe, maxdd=dd,
                   turnover_ann=S["turnover"].mean() * m, cost_ann=S["cost"].mean() * m,
                   active_vs_cw=ann(S["ret_n"]) - ann(S["bench_cw"]), te=act.std() * np.sqrt(m),
                   nav_net=S["nav_n"].iloc[-1], bnav_cw=S["bnav_cw"].iloc[-1])
    return S, summary

if __name__ == "__main__":
    import configs
    name = sys.argv[1] if len(sys.argv) > 1 else "sm_blend"
    cfg = configs.get(name)
    print("=" * 72); print(f"PAPER-READY SIMULATOR (인프라 검증, NOT 거래추천) — config: {name}"); print("=" * 72)
    print("⚠️  현재 통과 edge 0 — 이 신호는 kill-test FAIL. NAV는 *배관 검증*용이지 라이브/페이퍼 승격 아님.")
    S, s = simulate(cfg)
    print(f"\n기간 {S.index.min().date()}~{S.index.max().date()} · {s['n']}개월 · 보유 median={int(S['n'].median())}종")
    print(f"  CAGR gross={s['cagr_gross']*100:+.2f}% · net={s['cagr_net']*100:+.2f}% · vol={s['vol']*100:.1f}% · Sharpe(net)={s['sharpe']:.2f}")
    print(f"  maxDD={s['maxdd']*100:.1f}% · turnover≈{s['turnover_ann']*100:.0f}%/yr · cost≈{s['cost_ann']*100:.2f}%/yr")
    print(f"  vs cap-weight: active(net)={s['active_vs_cw']*100:+.2f}%/yr · TE={s['te']*100:.1f}%")
    print(f"  NAV net 100→{s['nav_net']:.1f} (cap-weight 벤치 100→{s['bnav_cw']:.1f})")
    out = os.path.join(data.PHASE1A, "outputs", "engine", f"sim_{name}.csv"); S.to_csv(out)
    print(f"  → {out}")
    print("\n[risk-veto 훅] per-name≤5% · gross≤100%(long-only). 결정적 = 리스크 엔진 최종권한 자리.")

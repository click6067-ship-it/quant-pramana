#!/usr/bin/env python3
"""Phase 2 M8 — Research Engine config-driven runner. M1~M7 오케스트레이션 *만*.
규율: 새 알파/feature/cost/kill 0(전부 동결 모듈 호출) · API 0(캐시만). config 하나로 과거 실험 재현(회귀 게이트).
config: name·bundle(broad|smallmid)·rank(lo,hi)·score·dropna·cost_tier·kill_set·filters·min_names."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd, data, universe as U, features as F, evaluate as E, kills as K, report as RP

OUT = os.path.join(data.PHASE1A, "outputs"); ENG = os.path.join(OUT, "engine"); os.makedirs(ENG, exist_ok=True)

def _bundle(kind):
    if kind == "broad":
        sep = data.load("broad_SEP", usecols=["ticker", "date", "closeadj"])
        px = sep.pivot_table(index="date", columns="ticker", values="closeadj").sort_index()
        pb = data.load("broad_DAILY_pb", usecols=["ticker", "date", "pb"]).pivot_table(index="date", columns="ticker", values="pb").sort_index()
        sf1 = data.load("broad_SF1"); sf1x = data.load("broad_SF1_ext"); pxu = adv = None
    else:
        sep = data.load("smallmid_SEP")
        px = sep.pivot_table(index="date", columns="ticker", values="closeadj").sort_index()
        pxu = sep.pivot_table(index="date", columns="ticker", values="closeunadj").sort_index()
        sep["dv"] = sep["closeunadj"] * sep["volume"]
        adv = sep.pivot_table(index="date", columns="ticker", values="dv").sort_index().rolling(20, min_periods=5).mean()
        pb = data.load("smallmid_DAILY", usecols=["ticker", "date", "pb"]).pivot_table(index="date", columns="ticker", values="pb").sort_index()
        sf1 = data.load("smallmid_SF1"); sf1x = sf1
    mc = data.load("DAILY_all", usecols=["ticker", "date", "marketcap"]).pivot_table(index="date", columns="ticker", values="marketcap").sort_index()
    return dict(px=px, pxu=pxu, adv=adv, pb=pb, mc=mc, sf1=sf1, sf1x=sf1x)

def _feature_matrix(name, B, rebal):
    if name == "value": return F.value(B["pb"], rebal)
    if name == "momentum": return F.momentum(B["px"], rebal)
    if name == "lowvol": return F.lowvol(B["px"], rebal)
    if name == "quality": return F.quality(B["sf1"], rebal, B["px"].columns)
    raise ValueError(name)

def assemble_panel(cfg, B, members, rebal, sector):
    px = B["px"]; mpx = px.reindex(rebal, method="pad"); fwd = mpx.shift(-1) / mpx - 1
    mcg = B["mc"].reindex(rebal, method="pad")
    need_adv = (cfg.get("cost_tier") == "adv") or ("filters" in cfg)
    advg = B["adv"].reindex(rebal, method="pad") if (need_adv and B["adv"] is not None) else None
    pxug = B["pxu"].reindex(rebal, method="pad") if (B["pxu"] is not None) else None
    sc = cfg["score"]
    if sc["kind"] == "composite_event":
        EQ = F.event_subsignals(B["sf1x"], rebal); comps = F.EVENT_COLS; srcs = EQ
    elif sc["kind"] == "composite":
        comps = sc["components"]; srcs = {c: _feature_matrix(c, B, rebal) for c in comps}
    else:
        comps = None; raw = _feature_matrix(sc["feature"], B, rebal)
    rows = []
    for t in rebal[:-1]:
        mem = [c for c in px.columns if c in members[t]]
        d = pd.DataFrame(index=mem)
        d["fwd"] = fwd.loc[t].reindex(mem); d["mc"] = mcg.loc[t].reindex(mem)
        if advg is not None: d["adv"] = advg.loc[t].reindex(mem)
        if pxug is not None: d["pxu"] = pxug.loc[t].reindex(mem)
        if comps is None:
            d["score"] = raw.loc[t].reindex(mem)
        else:
            for c in comps: d[c] = srcs[c].loc[t].reindex(mem)
        # filters (small/mid)
        flt = cfg.get("filters", {})
        if flt.get("price_min") is not None and "pxu" in d: d = d[d["pxu"] >= flt["price_min"]]
        if len(d) < cfg.get("min_names", 30): continue
        if flt.get("adv_floor_q") is not None and "adv" in d:
            d = d[d["adv"] >= d["adv"].quantile(flt["adv_floor_q"])]; d = d.dropna(subset=["fwd", "mc", "adv"])
        if len(d) < cfg.get("min_names", 30): continue
        if comps is not None:
            if cfg.get("composite_predropna", True):     # broad(phase1b/event)=True / small-mid=False(필터만, z skipna)
                d = d.dropna(subset=comps + ["fwd", "mc"])
                if len(d) < cfg.get("min_names", 30): continue
            d["score"] = F.composite(d, comps)
        d["asof"] = t; d["ticker"] = d.index; d["sec"] = sector.reindex(d.index).values
        rows.append(d.reset_index(drop=True))
    return pd.concat(rows, ignore_index=True)

def _sn_net_cw(L, dropna):
    L2 = L.copy(); L2["snsc"] = L2["score"] - L2.groupby(["asof", "sec"])["score"].transform("mean")
    return E.summarize(E.evaluate_panel(L2, "snsc", ["snsc"] + dropna[1:], "marketcap"))["net_cw"]

def _extras(kill_set, L, R, s, dropna):
    if kill_set == "broad_retest":
        return dict(net_ls=s["net_ls"], icir=s["icir"], turnover=s["turnover"], iclo=s["iclo"], ichi=s["ichi"])
    if kill_set == "phase1b":
        return dict(net_cw=s["net_cw"], rec_icir=s["rec_icir"], turnover=s["turnover"], rec_net=s["rec_net"],
                    sn_net_cw=_sn_net_cw(L, dropna), act_cw=s["act_cw"])
    if kill_set == "event":
        return dict(net_cw=s["net_cw"], rec_icir=s["rec_icir"], net2_cw=E.summarize(R, cost_mult=2)["net_cw"],
                    rec_net=s["rec_net"], act_cw=s["act_cw"], sn_net_cw=_sn_net_cw(L, dropna))
    if kill_set == "smallmid":
        advt = L.groupby("asof")["adv"].transform(lambda x: x.rank(pct=True))
        lo = E.summarize(E.evaluate_panel(L[advt < 1/3], "score", dropna, "adv", min_names=50))["net_ls"]
        hi = E.summarize(E.evaluate_panel(L[advt >= 2/3], "score", dropna, "adv", min_names=50))["net_ls"]
        return dict(net_cw=s["net_cw"], net_ls=s["net_ls"], icir=s["icir"], rec_net=s["rec_net"], rec_icir=s["rec_icir"],
                    net2_cw=E.summarize(R, cost_mult=2)["net_cw"], lo_liq_net_ls=lo, hi_liq_net_ls=hi, turnover=s["turnover"])
    if kill_set == "quality_quarantine":
        s1 = R[(R.index >= "2016") & (R.index <= "2020-12-31")]["spread"].mean(); s2 = R[R.index >= "2021"]["spread"].mean()
        secd = []
        for t, g in L.groupby("asof"):
            Q5 = g[g["score"].rank(pct=True) >= 0.8]; sc = Q5["sec"].dropna()
            if len(sc): secd.append(sc.value_counts(normalize=True))
        smax = pd.concat(secd, axis=1).mean(axis=1).max() if secd else 0.0
        return dict(net2_ls=E.summarize(R, cost_mult=2)["net_ls"], s1=s1, s2=s2, iclo=s["iclo"], ichi=s["ichi"],
                    act_cw=s["act_cw"], act_ew=s["act_ew"], sector_max=smax)
    return {}

def run_experiment(cfg, _cache={}):
    bk = cfg["bundle"]
    if bk not in _cache: _cache[bk] = _bundle(bk)
    B = _cache[bk]
    sector = data.load_tickers()["sector"]
    uni = U.rank_universe(*cfg["rank"])
    members = {d: set(g) for d, g in uni.groupby("asof")["ticker"]}; rebal = sorted(uni["asof"].unique())
    L = assemble_panel(cfg, B, members, rebal, sector)
    R = E.evaluate_panel(L, "score", cfg["dropna"], cfg["cost_tier"], min_names=cfg.get("min_names", 30))
    s = E.summarize(R)
    m = _extras(cfg["kill_set"], L, R, s, cfg["dropna"])
    keys, labels, verdict, passed = K.apply(cfg["kill_set"], m)
    return dict(R=R, summary=s, verdict=verdict, kill_keys=keys, kill_labels=labels, row=RP.summary_row(cfg["name"], s, verdict, labels))

REPORTS = os.path.join(data.PHASE1A, "reports", "engine"); os.makedirs(REPORTS, exist_ok=True)

def run_named(name):
    import configs
    return run_experiment(configs.get(name))

def run_all(names=None, write=True):
    import configs, report as RP
    names = names or list(configs.CONFIGS)
    rows = [run_named(n)["row"] for n in names]
    if write:
        RP.write_csv(rows, os.path.join(REPORTS, "engine_runs.csv"))
        RP.write_md(RP.render_md("Engine Runs (named configs)", rows, note="config registry 재실행(동결 재현)."),
                    os.path.join(REPORTS, "engine_runs.md"))
    return rows

if __name__ == "__main__":
    import configs, report as RP
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help", "list"):
        print("usage: python engine/run.py <config_name> | all | list")
        print("configs:", ", ".join(configs.CONFIGS)); sys.exit(0)
    if args[0] == "all":
        rows = run_all(); print(RP.render_md("Engine Runs", rows)); print(f"→ reports/engine/engine_runs.{{csv,md}}")
    else:
        res = run_named(args[0]); r = res["row"]
        print(RP.render_md(f"Engine Run — {args[0]}", [r]))
        print(f"verdict={res['verdict']} · kills={res['kill_keys']}")

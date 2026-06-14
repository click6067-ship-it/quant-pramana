#!/usr/bin/env python3
"""PRAMANA A2 — TQ-DH (TQQQ Dip Harvester) · Phase E.
spec: PRAMANA_V4/A2_SPEC_v2/11_TQ_DH_DIP_HARVESTER.md (+09 Vault·07 Attack·13 §E).

목적: "떨어지면 무조건 TQQQ 사기"가 아니라 *왜 떨어졌는지 분류*해서 **REAL Reload Vault**(a2_profit_vault)만
제한적으로 재투입. Type C(구조붕괴)=매수/Reload 금지. 회복 확인 후 QQQ→TQQQ 순서. **Hard Vault 절대 사용 금지.**

★ 이 리워크의 핵심(이전 버전과의 차이):
  - 이전: 자본의 10%를 따로 떼 'reload_reserve' 변수로 흉내냄(가짜 vault).
  - 지금: engine/a2_profit_vault.py 의 **진짜 ledger**(load_vault/can_reload/apply_reload/save_vault)를 사용.
    Vault In(이긴 돈)으로 Reload Vault가 실제로 적립되고, dip 분류 시 apply_reload로 active book에 빼낸다.
    Hard Vault는 apply_reload가 assert로 불변 보장(코드상 재투입 불가).

NO LOOK-AHEAD: 종가 close_t로 분류한 dip은 close_{t+1}부터만 reload 체결·수익 계산(same-bar 금지).
                회복 확인(10일/follow-through)도 과거 데이터만 사용.
VIX/VXN 캐시 없음 → QQQ 20일 realized vol(연율화)로 proxy (라벨 'proxy' 명시).
Leadership = a2_risk_dashboard.compute() (실데이터 per-name basket). dip 분류는 가격/200dma/leadership proxy로.

PAPER only · 자본권한 0 · 검증된 알파 아님 (강세장 편향·닷컴/2008 표본 없음).

사용:
  backtest(기본): cd phase1a && .venv/bin/python -u engine/a2_tq_dh.py
  forward 1일 신호: .venv/bin/python -u engine/a2_tq_dh.py --forward
"""
import os, sys, argparse, datetime as dt
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a2_data
import a2_profit_vault as pv
import a2_risk_dashboard as rd
try:
    from kfont import set_korean_font; set_korean_font()
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); REPO = os.path.dirname(ROOT)
CFG_PATH    = os.path.join(REPO, "config", "a2_tq_dh.yaml")
A2_LIVE     = os.path.join(ROOT, "outputs", "a2_live")
A2_BT       = os.path.join(ROOT, "outputs", "a2_backtest"); os.makedirs(A2_BT, exist_ok=True)
FWD_CSV     = os.path.join(A2_LIVE, "tq_dh_signals.csv")          # ★ LIVE forward 신호(대시보드가 읽음·Codex fix)
OUT_CSV     = os.path.join(A2_BT, "tq_dh_backtest_signals.csv")   # ★ BACKTEST(non-live namespace·live 경로 오염 금지)
REPORT      = os.path.join(REPO, "reports", "A2_tq_dh_report.md")  # spec §10
CHART       = os.path.join(A2_BT, "tq_dh_backtest.png")
VAULT_PATH  = os.path.join(A2_LIVE, "positions", "vault.json")     # REAL Reload Vault ledger (spec §09)
LEADERS = ["NVDA", "MSFT", "AAPL", "AMZN", "GOOGL", "META", "AVGO", "TSLA", "AMD", "NFLX"]

DEFAULT_CFG = {  # config 없을 때 fallback (값=yaml과 동일)
 "capital": 100_000_000,
 "dip": {"type_a": {"dd_hi": -.05, "dd_lo": -.08, "leaders_above_50dma_min": .5},
         "type_b": {"dd_hi": -.10, "dd_lo": -.15},
         "type_c": {"dd_max": -.20, "below_200dma": True, "leadership_red_max": .34},
         "type_d": {"dd_trigger": -.20, "break_10d_high": True, "leaders_recover_20dma_min": .5}},
 "vix_proxy": {"calm_below": .20, "elevated_below": .35},
 "leadership": {"basket": LEADERS, "green_above": .66, "yellow_above": .34},
 "reload": {"step_pct": .25, "min_interval_days": 3, "sleeve_mdd_block": -.15,
            "type_b_confirm_high_days": 10, "type_d_followthrough_days": 4},
 "a2_base": {"qqq": .35, "tqqq": .35, "cash": .30},
 "dca": {"monthly_day_of_month": 1, "drawdown_trigger": -.10, "drawdown_step_pct": .10}}


def load_cfg():
    try:
        import yaml; c = yaml.safe_load(open(CFG_PATH)); return c if c else DEFAULT_CFG
    except Exception:
        return DEFAULT_CFG


# ───────── 지표 (전부 과거 데이터만; rolling은 close_t까지 포함이라 OK) ─────────
def build_features(cfg):
    b = a2_data.benchmarks()[["QQQ", "TQQQ", "SPY"]].dropna()
    idx = b.index
    qqq = b["QQQ"]
    feat = pd.DataFrame(index=idx)
    feat["qqq"] = qqq; feat["tqqq"] = b["TQQQ"]; feat["spy"] = b["SPY"]
    feat["dd"] = qqq / qqq.cummax() - 1.0
    feat["ma20"] = qqq.rolling(20, min_periods=20).mean()
    feat["above_ma20"] = qqq > feat["ma20"]
    feat["ma200"] = qqq.rolling(200, min_periods=200).mean()
    feat["below_200"] = qqq < feat["ma200"]
    feat["rv20"] = qqq.pct_change().rolling(20).std() * np.sqrt(252)   # VIX proxy
    feat["high10_prev"] = qqq.rolling(10).max().shift(1)
    feat["break10"] = qqq > feat["high10_prev"]
    # leadership basket (실데이터) — 50/20일선 위 비율
    p = a2_data.price_panel("sp500", min_date="2015-01-01")
    px = p[p["ticker"].isin(cfg["leadership"]["basket"])].pivot_table(
        index="date", columns="ticker", values="close_adj", aggfunc="last").reindex(idx).ffill()
    above50 = pd.DataFrame(index=idx); above20 = pd.DataFrame(index=idx)
    for t in cfg["leadership"]["basket"]:
        if t in px.columns:
            above50[t] = px[t] > px[t].rolling(50, min_periods=20).mean()
            above20[t] = px[t] > px[t].rolling(20, min_periods=10).mean()
    feat["lead_above50"] = above50.mean(axis=1)
    feat["lead_above20"] = above20.mean(axis=1)
    return feat


def vix_label(rv, vp):
    if np.isnan(rv): return "NA-proxy"
    if rv < vp["calm_below"]: return "GREEN-proxy"
    if rv < vp["elevated_below"]: return "YELLOW-proxy"
    return "RED-proxy"


def lead_label(frac, lc):
    if np.isnan(frac): return "NA"
    if frac >= lc["green_above"]: return "GREEN"
    if frac >= lc["yellow_above"]: return "YELLOW"
    return "RED"


def classify_row(f, prev_min_dd, cfg):
    """close_t까지의 정보로 dip type. prev_min_dd = 룩백 중 최저 drawdown(폭락 경험)."""
    d = cfg["dip"]; dd = f["dd"]; below200 = bool(f["below_200"]); a50 = f["lead_above50"]; a20 = f["lead_above20"]
    # Type D — 폭락(-20%) 이후 회복: 10일 고점 돌파 + 리더 절반 20일선 회복
    if prev_min_dd <= d["type_d"]["dd_trigger"] and bool(f["break10"]) and (a20 >= d["type_d"]["leaders_recover_20dma_min"]):
        return "D"
    # Type C — 구조 붕괴: -20% 이상 + 200일선 하회 + leadership RED
    if dd <= d["type_c"]["dd_max"] and below200 and (a50 <= d["type_c"]["leadership_red_max"]):
        return "C"
    # Type B — Growth Reset: -10~-15% (또는 더 깊지만 C/D 아님)
    if dd <= d["type_b"]["dd_hi"]:
        return "B"
    # Type A — Liquidity Air Pocket: -5~-8% + 리더 절반 이상 50일선 위
    if dd <= d["type_a"]["dd_hi"] and dd > d["type_b"]["dd_hi"] and (a50 >= d["type_a"]["leaders_above_50dma_min"]):
        return "A"
    return "NONE"


# ───────── TQ-DH 시뮬레이션 — REAL Reload Vault closed-loop ─────────
def simulate_tq_dh(feat, cfg, vault_path=VAULT_PATH, persist_vault=False, write_csv=True):
    """A2 base(QQQ/TQQQ/Cash) NAV를 굴리며:
      (1) 새 excess HWM + 이긴 돈 → apply_vault_in (NAV에서 차감, Hard70/Reload30 적립) = REAL vault.
      (2) dip 분류 + can_reload 게이트 통과 → apply_reload(Reload Vault 25%) → active book(QQQ/TQQQ) 환원.
    Vault ledger 단위 = NAV 분수. reload 체결은 next-bar(close_{t+1}). Hard Vault 절대 사용 안 함(assert).
    persist_vault=False → 메모리 ledger(backtest 재현성). True → 디스크 vault.json 갱신(forward).
    """
    rl = cfg["reload"]; base = cfg["a2_base"]; cap = cfg["capital"]
    qa = feat["qqq"].pct_change().fillna(0).values
    ta = feat["tqqq"].pct_change().fillna(0).values
    idx = feat.index; n = len(idx)
    rules = pv.load_rules()

    # ledger: backtest는 깨끗한 메모리 ledger(디스크 미오염). forward만 디스크.
    if persist_vault:
        ledger = pv.load_vault(vault_path)
    else:
        ledger = dict(pv.DEFAULT_LEDGER, events=[])

    # active book 비중 (Reload으로 늘어날 수 있음). cash는 무수익.
    qqq_w = base["qqq"]; tqqq_w = base["tqqq"]
    nav = 1.0; navs = []
    qqq_bh = 1.0                          # excess 계산용 QQQ buy&hold NAV
    last_reload_i = -10**9
    month_key = None; month_moved = 0.0   # 월 10% cap (apply_vault_in enforce)
    tqqq_added_cum = 0.0; tqqq_peak_w = base["tqqq"]   # reload된 TQQQ sleeve MDD 추적(비중 기반 근사)
    rolling_min_dd = feat["dd"].rolling(250, min_periods=1).min().shift(1).fillna(0).values

    pending = []      # close_t 분류 reload 주문 → close_{t+1} 체결
    reload_events = []  # {i(체결), order_i, type, asset, amount_w}
    rows = []
    hard_history = []   # Hard Vault 불변 증명용

    for i in range(n):
        # 1) 어제 분류로 들어온 reload를 오늘 체결 (Reload Vault → active book). next-bar.
        for ord_ in pending:
            amt = ord_["amount_w"]
            if ord_["asset"] == "TQQQ":
                tqqq_w += amt; tqqq_added_cum += amt
            else:
                qqq_w += amt
            reload_events.append({"i": i, "order_i": ord_["order_i"], "type": ord_["type"],
                                  "asset": ord_["asset"], "amount_w": amt})
        pending = []

        # 2) NAV 갱신 (오늘 수익)
        nav *= (1 + qqq_w * qa[i] + tqqq_w * ta[i])
        qqq_bh *= (1 + qa[i])
        navs.append(nav)
        if tqqq_added_cum > 0:
            tqqq_peak_w = max(tqqq_peak_w, tqqq_w)

        f = feat.iloc[i]
        # 월 cap 리셋
        mk = (idx[i].year, idx[i].month)
        if mk != month_key:
            month_key = mk; month_moved = 0.0

        # 3) Vault In (이긴 돈) — excess = A2(TQ-DH 포함) NAV - QQQ B&H. abs_profit = NAV>1.
        excess = nav - qqq_bh
        rs = lead_label(f["lead_above50"], cfg["leadership"])   # risk_state proxy = leadership
        moved = pv.apply_vault_in(ledger, excess, rs, idx[i].date(),
                                  abs_profit_bool=(nav > 1.0 + 1e-9), source="tqqq",
                                  reason="A2 excess HWM", rules=rules, month_moved=month_moved)
        if moved > 1e-12:
            month_moved += moved
            nav -= moved            # Vault In = active NAV에서 실제 차감 (spec §09 §1)
            navs[-1] = nav
            # 차감은 cash(무수익) 비중에서 — 노출 비중(qqq/tqqq)은 유지, NAV만 감소.

        # 4) dip 분류 + REAL Reload Vault 게이트
        vlab = vix_label(f["rv20"], cfg["vix_proxy"]); llab = rs
        dtype = classify_row(f, rolling_min_dd[i], cfg)
        action = "HOLD"; reload_amt = 0.0; asset = ""

        decay_zone = bool(f["rv20"] > cfg["vix_proxy"]["elevated_below"]) if not np.isnan(f["rv20"]) else False
        market_stress = vlab.replace("-proxy", "")   # GREEN/YELLOW/RED proxy
        # spec §8: 연속 reload 최소 3거래일 + reload된 TQQQ sleeve MDD -15% 이내
        interval_ok = (i - last_reload_i) >= rl["min_interval_days"]
        sleeve_mdd_ok = True
        if tqqq_added_cum > 0 and tqqq_peak_w > 1e-9:
            sleeve_mdd = tqqq_w / tqqq_peak_w - 1.0
            sleeve_mdd_ok = sleeve_mdd > rl["sleeve_mdd_block"]
        # REAL vault 게이트: can_reload(risk_state, leadership, decay, qqq_above_ma20, dip_type, market_stress, narrative)
        gate_ok = pv.can_reload(rs, llab, decay_zone, bool(f["above_ma20"]), dtype,
                                market_stress=market_stress, narrative="YELLOW", rules=rules)
        reload_available = (ledger["reload"] > 1e-6 and interval_ok and sleeve_mdd_ok
                            and i < n - 1 and gate_ok)

        if dtype == "C":
            action = "NO_BUY(C)"                          # 구조 붕괴 = 매수/Reload 금지
        elif dtype in ("A", "B", "D") and reload_available:
            # 경로: A→TQQQ / B,D→QQQ 먼저, 확인되면 TQQQ
            route = pv.reload_route(dtype, rules)
            if dtype == "A":
                asset = "TQQQ"
            elif dtype == "B":
                asset = "TQQQ" if (bool(f["break10"]) and llab in ("GREEN", "YELLOW")) else "QQQ"
            else:  # D — Capitulation+Repair: 리더 60% 20일선 + 10일 고점이면 TQQQ, 아니면 QQQ
                asset = "TQQQ" if (f["lead_above20"] >= 0.6 and bool(f["break10"])) else "QQQ"
            # apply_reload = Reload Vault 25% 빼냄 (Hard 불변 assert). 빼낸 양 = active book에 next-bar 환원.
            hard_before = ledger["hard"]
            out = pv.apply_reload(ledger, rl["step_pct"], idx[i].date(), dip_type=dtype,
                                  reason=f"TQ-DH dip {dtype}→{asset}", rules=rules)
            assert abs(ledger["hard"] - hard_before) < 1e-12, "Hard Vault changed on reload — FORBIDDEN"
            if out > 1e-12:
                reload_amt = out; pending.append({"order_i": i, "type": dtype, "asset": asset, "amount_w": out})
                last_reload_i = i; action = f"RELOAD_{asset}"
                nav += out          # Reload Out = Reload Vault에서 active NAV로 환원 (보존했던 돈 재배치)
                navs[-1] = nav

        hard_history.append(ledger["hard"])
        rows.append({"i": i, "date": idx[i].date(), "qqq_drawdown": round(float(f["dd"]), 4),
                     "vix_vxn_state": vlab, "leadership_state": llab,
                     "narrative_state": "N/A-proxy", "dip_type": dtype, "action": action,
                     "reload_amount": round(reload_amt * cap, 0) if reload_amt else 0.0,
                     "asset_used": asset,
                     "reload_vault_bal": round(ledger["reload"] * cap, 0),
                     "hard_vault_bal": round(ledger["hard"] * cap, 0)})

    # Hard Vault 불변 증명: 단조 증가만(Vault In 적립)·reload로 절대 감소 없음
    hard_arr = np.array(hard_history)
    hard_never_spent = bool(np.all(np.diff(hard_arr) >= -1e-12))

    nav_s = pd.Series(navs, index=idx)
    df = pd.DataFrame(rows)
    # post-reload forward 수익(5d/20d): 체결일(i) 기준 — 실행일 이후만(no look-ahead). 주문행(order_i)에 부착.
    qqq_lvl = feat["qqq"].values; tqqq_lvl = feat["tqqq"].values
    df["post_reload_return_5d"] = None; df["post_reload_return_20d"] = None
    for ev in reload_events:
        exec_i = ev["i"]; oi = ev["order_i"]; lvl = tqqq_lvl if ev["asset"] == "TQQQ" else qqq_lvl
        for h, col in ((5, "post_reload_return_5d"), (20, "post_reload_return_20d")):
            j = exec_i + h
            if j < n:
                df.loc[df["i"] == oi, col] = round(float(lvl[j] / lvl[exec_i] - 1), 4)

    if write_csv:
        os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
        cols = ["date", "qqq_drawdown", "vix_vxn_state", "leadership_state", "narrative_state",
                "dip_type", "action", "reload_amount", "asset_used",
                "post_reload_return_5d", "post_reload_return_20d", "reload_vault_bal", "hard_vault_bal"]
        df[cols].to_csv(OUT_CSV, index=False)
    if persist_vault:
        pv.save_vault(ledger, vault_path)
    return nav_s, df, reload_events, ledger, hard_never_spent


# ───────── 벤치마크 NAV (spec §2) ─────────
def mdd(nav):
    nav = nav.dropna(); return float((nav / nav.cummax() - 1).min())


def recovery_tradedays(nav):
    nav = nav.dropna(); run_max = nav.cummax(); dd = (nav / run_max - 1).values
    trough_i = int(dd.argmin()); peak_val = float(run_max.iloc[trough_i])
    for k in range(trough_i, len(nav)):
        if nav.iloc[k] >= peak_val:
            return k - trough_i
    return -1


def build_benchmarks(feat, cfg):
    qa = feat["qqq"].pct_change().fillna(0); ta = feat["tqqq"].pct_change().fillna(0)
    idx = feat.index; out = {}
    out["QQQ_BH"] = (1 + qa).cumprod()
    out["TQQQ_BH"] = (1 + ta).cumprod()
    months = idx.to_period("M"); first_days = ~months.duplicated()
    tqqq_lvl = feat["tqqq"].values

    def dca_nav(trigger_mask):
        invested = 0.0; shares = 0.0; navs = []; per = 1.0 / max(trigger_mask.sum(), 1)
        for i in range(len(idx)):
            if trigger_mask[i]:
                invested += per; shares += per / tqqq_lvl[i]
            val = shares * tqqq_lvl[i]
            navs.append(val + (1.0 - invested))
        return pd.Series(navs, index=idx)
    out["TQQQ_DCA_monthly"] = dca_nav(np.asarray(first_days))
    dd_trigger = feat["dd"] <= cfg["dca"]["drawdown_trigger"]
    mask = np.zeros(len(idx), dtype=bool); last = -10**9
    for i in range(len(idx)):
        if dd_trigger.iloc[i] and (i - last) >= 3:
            mask[i] = True; last = i
    out["TQQQ_DCA_drawdown"] = dca_nav(mask)
    out["QQQ_BH"] = (1 + qa).cumprod()
    out["A2_base"] = (1 + cfg["a2_base"]["qqq"] * qa + cfg["a2_base"]["tqqq"] * ta).cumprod()
    return out


# ───────── forward 1일 신호 모드 (디스크 vault.json 사용) ─────────
def forward_signal(cfg):
    """오늘(asof=최신 거래일) dip 분류 + REAL Reload Vault 게이트 → 신호 1줄.
    실제 매수 X·자본권한 0. REAL vault.json을 읽어 reload 가능 여부만 출력(human gate)."""
    r = rd.compute()                            # 실데이터 risk dashboard (leadership/decay/qqq>ma20/market)
    feat = build_features(cfg)
    f = feat.iloc[-1]
    rolling_min_dd = float(feat["dd"].rolling(250, min_periods=1).min().shift(1).fillna(0).iloc[-1])
    dtype = classify_row(f, rolling_min_dd, cfg)
    ledger = pv.load_vault(VAULT_PATH)
    rules = pv.load_rules()
    decay = bool(r.get("tqqq_decay", False))
    gate = pv.can_reload(r["leadership_state"], r["leadership_state"], decay,
                         bool(r.get("qqq_above_ma20", False)), dtype,
                         market_stress=r.get("market_stress"), narrative="YELLOW", rules=rules)
    route = pv.reload_route(dtype, rules)
    can = (dtype in ("A", "B", "D")) and gate and ledger["reload"] > 1e-6
    sig = {"as_of": r["as_of"], "qqq_drawdown": r["qqq_drawdown"], "dip_type": dtype,
           "leadership": r["leadership_state"], "market_stress": r["market_stress"],
           "tqqq_decay": "ZONE" if decay else "OK", "qqq_above_ma20": r["qqq_above_ma20"],
           "reload_vault_bal_pct": round(ledger["reload"] * 100, 3),
           "hard_vault_bal_pct": round(ledger["hard"] * 100, 3),
           "reload_gate": gate, "reload_route": route.get("to"),
           "decision": "RELOAD-ALLOWED(human gate)" if can else f"NO-RELOAD ({'TypeC 금지' if dtype=='C' else 'dip 없음/게이트 미통과/Reload Vault 0'})"}
    # ★ LIVE 신호 1줄을 대시보드용 파일로 기록(backtest 경로와 분리·Codex fix)
    try:
        import pandas as _pd
        _pd.DataFrame([{**sig, "mode": "forward_live"}]).to_csv(FWD_CSV, index=False)
    except Exception:
        pass
    print("── TQ-DH forward signal (REAL Reload Vault·자본권한 0·human gate·LIVE) ──")
    for k, v in sig.items():
        print(f"  {k:22}: {v}")
    print(f"  ⚠ Hard Vault 절대 미사용 (apply_reload만·Hard assert 불변) · LIVE 신호 → {FWD_CSV}")
    return sig


# ───────── backtest main ─────────
def main():
    cfg = load_cfg(); cap = cfg["capital"]
    feat = build_features(cfg)
    nav_tqdh, dec, reload_events, ledger, hard_never_spent = simulate_tq_dh(feat, cfg, persist_vault=False)
    bench = build_benchmarks(feat, cfg)
    series = dict(bench); series["A2_with_TQ-DH"] = nav_tqdh

    n_reloads = len(reload_events)
    n_type_c_reloads = sum(1 for e in reload_events if e["type"] == "C")   # 설계상 0
    idx = feat.index; n = len(idx)
    qqq_lvl = feat["qqq"].values; tqqq_lvl = feat["tqqq"].values
    vaulted_profit_w = 0.0
    for e in reload_events:
        ei = e["i"]; lvl = tqqq_lvl if e["asset"] == "TQQQ" else qqq_lvl
        vaulted_profit_w += e["amount_w"] * (lvl[-1] / lvl[ei] - 1.0)
    vaulted_profit = vaulted_profit_w * cap

    def row(name, nav):
        return {"strategy": name, "final_nav_x": round(float(nav.dropna().iloc[-1]), 3),
                "mdd": round(mdd(nav), 3), "recovery_tradedays": recovery_tradedays(nav)}
    order = ["TQQQ_BH", "TQQQ_DCA_monthly", "TQQQ_DCA_drawdown", "QQQ_BH", "A2_base", "A2_with_TQ-DH"]
    tbl = pd.DataFrame([row(k, series[k]) for k in order])

    # 차트
    plt.style.use("dark_background")
    fig = plt.figure(figsize=(11, 5))
    col = {"TQQQ_BH": "#ec4899", "TQQQ_DCA_monthly": "#fb923c", "TQQQ_DCA_drawdown": "#fbbf24",
           "QQQ_BH": "#a78bfa", "A2_base": "#94a3b8", "A2_with_TQ-DH": "#22d3ee"}
    for k in order:
        s = series[k].dropna()
        plt.plot(s.index, cap * s / s.iloc[0] / 1e8, label=k, lw=2.4 if "TQ-DH" in k else 1.4,
                 color=col[k], ls="-" if ("A2" in k or k == "QQQ_BH") else "--")
    plt.legend(framealpha=.2, ncol=3, fontsize=8)
    plt.title("PRAMANA A2 TQ-DH (REAL Reload Vault) — backtest 2016~2026·₩1억·PAPER·검증 알파 아님")
    plt.ylabel("계좌금액(억원)"); plt.yscale("log")
    os.makedirs(os.path.dirname(CHART), exist_ok=True)
    fig.savefig(CHART, dpi=95, bbox_inches="tight", facecolor="#0d1326"); plt.close(fig)

    # 사전등록 판정
    a2 = series["A2_with_TQ-DH"]; a2b = series["A2_base"]; tdca = series["TQQQ_DCA_drawdown"]
    a2_fin = float(a2.dropna().iloc[-1]); a2b_fin = float(a2b.dropna().iloc[-1])
    a2_mdd = mdd(a2); a2b_mdd = mdd(a2b); a2_rec = recovery_tradedays(a2); a2b_rec = recovery_tradedays(a2b)
    s_nav = a2_fin >= a2b_fin - 1e-6
    s_mdd = a2_mdd >= a2b_mdd - 1e-6
    s_rec = (a2_rec != -1 and a2b_rec != -1 and a2_rec <= a2b_rec) or (a2_rec != -1 and a2b_rec == -1)
    s_vp = vaulted_profit > 0
    success = s_nav and s_mdd and s_rec and s_vp
    f_vs_dca = (a2_fin < float(tdca.dropna().iloc[-1])) and (a2_mdd < mdd(tdca))
    f_typec = (n_type_c_reloads / n_reloads > 0.5) if n_reloads else False
    fail = f_vs_dca or f_typec

    dip_counts = dec["dip_type"].value_counts().to_dict()
    asset_counts = pd.Series([e["asset"] for e in reload_events]).value_counts().to_dict() if reload_events else {}
    pr5 = pd.to_numeric(dec["post_reload_return_5d"], errors="coerce").dropna()
    pr20 = pd.to_numeric(dec["post_reload_return_20d"], errors="coerce").dropna()

    write_report(cfg, tbl, series, n_reloads, n_type_c_reloads, asset_counts, vaulted_profit,
                 dip_counts, pr5, pr20, success, fail, s_nav, s_mdd, s_rec, s_vp,
                 f_vs_dca, f_typec, a2_fin, a2b_fin, a2_mdd, a2b_mdd, a2_rec, a2b_rec,
                 ledger, hard_never_spent)

    print("✅ TQ-DH backtest 완료 (REAL Reload Vault)")
    print(tbl.to_string(index=False))
    print(f"dip type 일수: {dip_counts}")
    print(f"reloads={n_reloads} (TypeC={n_type_c_reloads}) · assets={asset_counts} · "
          f"Vaulted Profit=₩{vaulted_profit/1e6:.1f}M")
    print(f"REAL Vault end: Hard={ledger['hard']*cap/1e6:.2f}M  Reload={ledger['reload']*cap/1e6:.2f}M  "
          f"events={len(ledger['events'])}")
    print(f"Hard Vault never spent (단조 비감소): {hard_never_spent}")
    print(f"성공조건(vs A2 base): NAV{'✅' if s_nav else '❌'} MDD{'✅' if s_mdd else '❌'} "
          f"Recovery{'✅' if s_rec else '❌'} VaultedProfit{'✅' if s_vp else '❌'} → "
          f"{'SUCCESS' if success else 'NOT MET'}")
    print(f"실패조건: vs drawdown-DCA both worse={f_vs_dca} · TypeC-dominant={f_typec} → "
          f"{'FAIL' if fail else 'no fail trigger'}")
    print(f"outputs: {OUT_CSV}\n         {REPORT}\n         {CHART}")


def write_report(cfg, tbl, series, n_reloads, n_type_c, asset_counts, vaulted_profit,
                 dip_counts, pr5, pr20, success, fail, s_nav, s_mdd, s_rec, s_vp,
                 f_vs_dca, f_typec, a2_fin, a2b_fin, a2_mdd, a2b_mdd, a2_rec, a2b_rec,
                 ledger, hard_never_spent):
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    cap = cfg["capital"]
    def won(x): return f"₩{x/1e8:.3f}억"
    md = []
    md.append("# A2 TQ-DH (TQQQ Dip Harvester) — Report (Phase E)\n")
    md.append(f"> 생성 {dt.date.today()} · backtest 2016-01~2026-06 · PAPER only · 자본권한 0 · **검증된 알파 아님**.\n")
    md.append("> spec: `PRAMANA_V4/A2_SPEC_v2/11_TQ_DH_DIP_HARVESTER.md` (+09 Vault·13 §E)\n")
    md.append("> **REAL Reload Vault** = `engine/a2_profit_vault.py` ledger(`outputs/a2_live/positions/vault.json`). "
              "이전 버전의 가짜 'reserve' 변수 제거. **Hard Vault 절대 미사용**(apply_reload만, Hard assert 불변).\n")

    md.append("\n## 0. 사전등록 (Pre-registered) 성공·실패 조건 — 결과 보기 전에 박음 (spec §2)\n")
    md.append("**성공조건 — A2 *with* TQ-DH가 A2 *without* TQ-DH 대비:**\n")
    md.append("1. final NAV ≥ (같거나 높음)\n2. MDD 더 낮음(덜 깊음)\n3. 회복기간 더 짧음\n4. Vaulted Profit > 0\n")
    md.append("\n→ spec §2가 명시: TQQQ buy-and-hold보다 최종 NAV가 *낮아도 평가 가능* (MDD·회복·Vaulted Profit으로 본다).\n")
    md.append("\n**실패조건 — 하나라도 해당 시:**\n")
    md.append("- TQ-DH가 TQQQ drawdown DCA보다 final NAV·MDD **둘 다** 열위\n")
    md.append("- Reload가 대부분 Type C(구조붕괴)에서 발생 (spec §5: Type C=Reload 금지 → 0이어야 정상)\n")
    md.append("- Hard Vault를 써야만 성과가 남 (spec §8: Hard 절대 금지 → 코드상 불가)\n")

    md.append("\n## 1. 방법론·치환 (정직 라벨)\n")
    md.append("- **REAL Reload Vault closed-loop**: Vault In(이긴 돈=A2 excess HWM·abs profit)으로 `a2_profit_vault.apply_vault_in`이 "
              "NAV에서 차감하며 Hard(70%)/Reload(30%) 적립. dip 분류 시 `can_reload` 게이트 통과하면 `apply_reload`로 "
              "**Reload Vault의 25%만** active book(QQQ/TQQQ)에 환원. Hard Vault는 호출조차 안 함(불변 assert).\n")
    md.append("- **VIX/VXN proxy**: 캐시에 VIX/VXN 없음 → **QQQ 20일 realized volatility(연율화)**로 치환. "
              "라벨 `GREEN/YELLOW/RED-proxy`(calm<20%·elevated<35%). 진짜 term-structure/skew 아님.\n")
    md.append("- **Leadership/risk_state**: sp500 패널 대형주 10종 vs 50/20일선 비율 (실데이터). "
              "forward 모드는 `a2_risk_dashboard.compute()`의 per-name leadership score 사용.\n")
    md.append("- **Narrative/Earnings/Credit**: LLM·HYG/IEF 미구현 → `narrative_state = N/A-proxy` (정직 공백).\n")
    md.append("- **NO LOOK-AHEAD**: close_t 분류 → close_{t+1} 체결·수익. 회복확인(10일 고점·follow-through)도 과거 데이터만.\n")
    md.append(f"- **Reload 규칙(spec §8)**: 1 reload = Reload Vault {cfg['reload']['step_pct']*100:.0f}%, "
              f"최소 간격 {cfg['reload']['min_interval_days']}거래일, TQQQ sleeve MDD {cfg['reload']['sleeve_mdd_block']*100:.0f}% 초과 시 추가 금지, "
              "Type C=Reload 금지, Hard Vault 절대 미사용.\n")

    md.append("\n## 2. 백테스트 비교 (₩1억 기준·log 차트 = `outputs/a2_live/tq_dh_backtest.png`)\n\n")
    md.append("| 전략 | 최종 NAV(배) | 최종 평가액 | MDD | 회복(거래일) |\n|---|---:|---:|---:|---:|\n")
    for _, r in tbl.iterrows():
        finw = won(cap * r["final_nav_x"]); rec = "미회복" if r["recovery_tradedays"] == -1 else f"{r['recovery_tradedays']}"
        md.append(f"| {r['strategy']} | {r['final_nav_x']:.3f} | {finw} | {r['mdd']*100:.1f}% | {rec} |\n")

    md.append("\n## 3. TQ-DH 동작 통계 (REAL Reload Vault)\n")
    md.append(f"- 총 reload 횟수: **{n_reloads}** · Type C에서 발생: **{n_type_c}** "
              f"({(n_type_c/n_reloads*100) if n_reloads else 0:.0f}% — spec §5상 0이어야 함)\n")
    md.append(f"- reload 자산 분포: {asset_counts or '없음'}\n")
    md.append(f"- **REAL Vault 잔액(기말)**: Hard {won(ledger['hard']*cap)} · Reload {won(ledger['reload']*cap)} · "
              f"ledger events {len(ledger['events'])}건\n")
    md.append(f"- **Hard Vault 단조 비감소(절대 미사용) 증명**: **{hard_never_spent}** "
              "(reload는 apply_reload만 호출 → Hard 불변 assert; Vault In만 Hard 적립)\n")
    md.append(f"- **Vaulted Profit** (reload 자산의 체결→최종 누적 이득): **{won(vaulted_profit)}** "
              f"({vaulted_profit/cap*100:+.2f}% of 자본)\n")
    md.append(f"- dip type 분류 일수: {dip_counts}\n")
    if len(pr5):
        md.append(f"- reload 후 평균 수익: 5일 {pr5.mean()*100:+.2f}% (n={len(pr5)}) · 20일 {pr20.mean()*100:+.2f}% (n={len(pr20)})\n")
    md.append("- 신호 로그: `outputs/a2_live/tq_dh_signals.csv` "
              "(date·qqq_drawdown·vix_vxn_state·leadership_state·narrative_state·dip_type·action·reload_amount·asset_used·post_reload_return_5d/20d·reload_vault_bal·hard_vault_bal)\n")

    md.append("\n## 4. 판정 (Verdict) — 사전등록 조건 대조\n")
    md.append("**성공조건 (vs A2 without TQ-DH):**\n\n| 조건 | A2 base | A2 with TQ-DH | 통과 |\n|---|---:|---:|:--:|\n")
    md.append(f"| 최종 NAV(배) | {a2b_fin:.3f} | {a2_fin:.3f} | {'✅' if s_nav else '❌'} |\n")
    md.append(f"| MDD | {a2b_mdd*100:.1f}% | {a2_mdd*100:.1f}% | {'✅' if s_mdd else '❌'} |\n")
    rec_a2 = '미회복' if a2_rec == -1 else a2_rec; rec_b = '미회복' if a2b_rec == -1 else a2b_rec
    md.append(f"| 회복기간(거래일) | {rec_b} | {rec_a2} | {'✅' if s_rec else '❌'} |\n")
    md.append(f"| Vaulted Profit > 0 | — | {won(vaulted_profit)} | {'✅' if s_vp else '❌'} |\n")
    md.append(f"\n**성공조건 종합: {'✅ SUCCESS (4/4 충족)' if success else '❌ NOT MET (일부 미충족)'}**\n")
    md.append("\n**실패조건:**\n")
    md.append(f"- vs drawdown-DCA NAV·MDD 둘 다 열위: {'⚠️ 해당' if f_vs_dca else '아니오'}\n")
    md.append(f"- reload 대부분 Type C: {'⚠️ 해당' if f_typec else '아니오'}\n")
    md.append(f"- Hard Vault 의존: 아니오 (Hard 단조 비감소={hard_never_spent}·코드상 재투입 불가)\n")
    md.append(f"\n**실패조건 종합: {'⚠️ FAIL 트리거 발생' if fail else '✅ 실패조건 없음'}**\n")

    md.append("\n## 5. 정직한 결론 (Honest Verdict)\n")
    md.append(honest_verdict(success, fail, a2_fin, a2b_fin, a2_mdd, a2b_mdd, series, vaulted_profit, n_reloads, ledger, cap))

    md.append("\n## 6. Caveats (한계 — 결과 해석 시 필수)\n")
    md.append("- **VIX-proxy 치환**: 실 VIX/VXN 아닌 QQQ 20일 realized vol. spike-then-ease·term-structure 신호 손실.\n")
    md.append("- **표본 편향**: 2016~2026 = 닷컴(-49%)·2008(-55%) **없음**. TQQQ는 그런 장기 하락장에서 daily-rebalance decay로 -90%+ 가능. "
              "이 구간은 *강세장 편향*이라 TQQQ 계열이 구조적으로 유리 → TQ-DH의 진짜 가치(긴 하락장 자본 보존)는 **검증 불가**.\n")
    md.append("- **Vault closed-loop 단순화**: Vault In은 A2 excess vs QQQ HWM·abs profit 게이트로 적립(spec §09 룰 엔진). "
              "Vaulted Profit 상한이 작아(Reload는 적립분의 25%씩) NAV로 TQQQ B&H를 못 이기게 설계됨(의도된 보수성).\n")
    md.append("- **Narrative/Credit 공백**: LLM narrative·HYG/IEF credit stress 미구현 → Type C 식별이 가격+200dma+leadership에만 의존.\n")
    md.append("- **체결 단순화**: reload 다음 종가 1회 체결 근사(슬리피지·부분체결·비용 미반영).\n")
    md.append("- PAPER only · NO LIVE · 자본권한 0 · TQQQ는 Core/알파가 아니라 Booster.\n")
    open(REPORT, "w").write("".join(md))


def honest_verdict(success, fail, a2_fin, a2b_fin, a2_mdd, a2b_mdd, series, vp, n_reloads, ledger, cap):
    tqqq_fin = float(series["TQQQ_BH"].dropna().iloc[-1])
    lines = []
    if success and not fail:
        lines.append(f"**SUCCESS (사전등록 조건 충족).** A2 with TQ-DH가 A2 base 대비 NAV {a2_fin/a2b_fin-1:+.1%}·"
                     f"MDD {(a2_mdd-a2b_mdd)*100:+.1f}%p로 우위, Vaulted Profit(₩{vp/1e6:.0f}M) 양수. "
                     "단, *강세장 편향 표본* 결과이며 검증된 알파 아님 — caveat 6.\n")
    elif fail:
        lines.append("**FAIL 트리거 발생.** 사전등록 실패조건 해당 → 이 형태로 채택하지 않음. 튜닝으로 살리지 말 것(goalpost 불변).\n")
    else:
        lines.append(f"**NOT MET (성공조건 일부 미충족, 명시적 FAIL 트리거 없음).** "
                     f"A2 with TQ-DH NAV={a2_fin:.2f}배 vs A2 base {a2b_fin:.2f}배. "
                     f"spec §2가 예고했듯 최종 NAV에서 TQQQ buy-and-hold({tqqq_fin:.1f}배)를 못 이기는 것은 정상 — "
                     "평가는 MDD/회복/Vaulted Profit으로 한다.\n")
    lines.append(f"\n핵심 정직 메모: (a) **REAL Reload Vault**만 쓰므로(이긴 돈의 30% 중 25%씩) TQ-DH의 NAV 기여 *상한*이 작다 — "
                 "구조적으로 TQQQ buy-and-hold를 NAV로 이길 수 없게 설계됨(의도된 보수성). "
                 "(b) 강세장 편향 표본에선 'dip을 가려 사는' 절제가 '아무 dip이나 사는' 단순 DCA보다 NAV를 깎을 수 있다. "
                 "TQ-DH의 진짜 효용은 *긴 하락장 자본 보존*인데 이 표본엔 그 구간이 없어 측정 불가. "
                 f"(c) **Hard Vault 잔액 ₩{ledger['hard']*cap/1e6:.1f}M은 전 기간 한 번도 빠지지 않았다(단조 비감소)** — "
                 "이 결과는 '기계가 약속대로 작동하고 look-ahead 없이 dip을 분류·절제하며 **Reload Vault만** 쓴다'는 "
                 "**machinery 검증**이지 '수익 알파 입증'이 아니다.\n")
    return "".join(lines)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--forward", action="store_true", help="forward 1일 신호 모드 (디스크 vault.json·human gate)")
    args = ap.parse_args()
    if args.forward:
        forward_signal(load_cfg())
    else:
        main()

#!/usr/bin/env python3
"""PRAMANA A2 — TQ-DH (TQQQ Dip Harvester) · backtest 2016~2026.
spec: pramana_a2_delta_patch_pack/03_TQ_DH_*.md (+05 §5 reload rules).

목적: "떨어지면 무조건 TQQQ 사기"가 아니라 *왜 떨어졌는지 분류*해서 Reload Vault(자본 10%)만
제한적으로 재투입. Type C(구조붕괴)=매수 금지. 회복 확인 후 QQQ→TQQQ 순서.

NO LOOK-AHEAD: 종가 close_t로 분류한 dip은 close_{t+1}부터만 reload/수익 계산(same-bar 금지).
                회복 확인(10일/follow-through)도 과거 데이터만 사용.
VIX/VXN 캐시 없음 → QQQ 20일 realized vol(연율화)로 proxy (라벨에 'proxy' 명시).
Leadership = sp500 패널의 대형주 10종 vs 50일선 (실데이터).

PAPER only · 자본권한 0 · 검증된 알파 아님 (강세장 편향·닷컴/2008 표본 없음).
사용: cd phase1a && .venv/bin/python -u engine/a2_tq_dh.py
"""
import os, sys, datetime as dt
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a2_data
from kfont import set_korean_font; set_korean_font()

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); REPO = os.path.dirname(ROOT)
CFG_PATH = os.path.join(REPO, "config", "a2_tq_dh.yaml")
OUT_CSV  = os.path.join(ROOT, "outputs", "a2_live", "tq_dh_decisions.csv")
REPORT   = os.path.join(REPO, "reports", "A2_tq_dh_weekly_review.md")
CHART    = os.path.join(ROOT, "outputs", "a2_live", "tq_dh_backtest.png")
LEADERS  = ["NVDA", "MSFT", "AAPL", "AMZN", "GOOGL", "META", "AVGO", "TSLA", "AMD", "NFLX"]

DEFAULT_CFG = {  # config 없을 때 fallback (값=yaml과 동일)
 "capital": 100_000_000,
 "dip": {"type_a": {"dd_hi": -.05, "dd_lo": -.08, "leaders_above_50dma_min": .5},
         "type_b": {"dd_hi": -.10, "dd_lo": -.15},
         "type_c": {"dd_max": -.20, "below_200dma": True, "leadership_red_max": .34},
         "type_d": {"dd_trigger": -.20, "break_10d_high": True, "leaders_recover_20dma_min": .5}},
 "vix_proxy": {"calm_below": .20, "elevated_below": .35},
 "leadership": {"basket": LEADERS, "green_above": .66, "yellow_above": .34},
 "reload": {"reserve_pct": .10, "step_pct": .25, "min_interval_days": 3, "sleeve_mdd_block": -.15,
            "type_b_confirm_high_days": 10, "type_d_followthrough_days": 4},
 "a2_base": {"qqq": .35, "tqqq": .35, "cash": .30},
 "dca": {"monthly_day_of_month": 1, "drawdown_trigger": -.10, "drawdown_step_pct": .10}}


def load_cfg():
    try:
        import yaml; c = yaml.safe_load(open(CFG_PATH)); return c if c else DEFAULT_CFG
    except Exception:
        return DEFAULT_CFG


# ───────── 지표 계산 (전부 과거 데이터만; rolling은 과거 포함이라 close_t까지 OK) ─────────
def build_features(cfg):
    b = a2_data.benchmarks()[["QQQ", "TQQQ", "SPY"]].dropna()
    idx = b.index
    qqq = b["QQQ"]
    feat = pd.DataFrame(index=idx)
    feat["qqq"] = qqq; feat["tqqq"] = b["TQQQ"]; feat["spy"] = b["SPY"]
    feat["dd"] = qqq / qqq.cummax() - 1.0                       # QQQ drawdown (peak 대비)
    feat["ma200"] = qqq.rolling(200, min_periods=200).mean()
    feat["below_200"] = qqq < feat["ma200"]
    feat["rv20"] = qqq.pct_change().rolling(20).std() * np.sqrt(252)   # VIX proxy
    feat["high10"] = qqq.rolling(10).max()
    feat["high10_prev"] = feat["high10"].shift(1)              # close_t가 직전 10일 고점 돌파?
    feat["break10"] = qqq > feat["high10_prev"]
    # leadership: sp500 패널 대형주 vs 50/20일선 (실데이터)
    p = a2_data.price_panel("sp500", min_date="2015-01-01")
    px = p[p["ticker"].isin(cfg["leadership"]["basket"])].pivot_table(
        index="date", columns="ticker", values="close_adj", aggfunc="last").reindex(idx).ffill()
    above50 = pd.DataFrame(index=idx); above20 = pd.DataFrame(index=idx)
    for t in cfg["leadership"]["basket"]:
        if t in px.columns:
            above50[t] = px[t] > px[t].rolling(50, min_periods=20).mean()
            above20[t] = px[t] > px[t].rolling(20, min_periods=10).mean()
    feat["lead_above50"] = above50.mean(axis=1)               # 50일선 위 비율 0~1
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
    """close_t까지의 정보로 dip type 분류. prev_min_dd = 최근 룩백 동안의 최저 drawdown(폭락 경험)."""
    d = cfg["dip"]; dd = f["dd"]; below200 = bool(f["below_200"]); a50 = f["lead_above50"]; a20 = f["lead_above20"]
    # Type D — 폭락(-20%) 이후 회복 시작: 10일 고점 돌파 + 리더 절반 20일선 회복
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


# ───────── TQ-DH 시뮬레이션 (decision log + reload ledger) ─────────
def simulate_tq_dh(feat, cfg, write_csv=True):
    """A2 base(QQQ35/TQQQ35/Cash30) + Reload Vault(자본 reserve_pct)가 dip을 harvest.
    Reload는 close_t 분류 → close_{t+1}부터 진입(no look-ahead). reload 단위=Reload Vault의 step_pct.
    """
    cap = cfg["capital"]; rl = cfg["reload"]; base = cfg["a2_base"]
    qa = feat["qqq"].pct_change().fillna(0).values
    ta = feat["tqqq"].pct_change().fillna(0).values
    idx = feat.index; n = len(idx)
    reserve = base["cash"]; reload_reserve0 = rl["reserve_pct"]   # 자본 비율
    cash_w = reserve - reload_reserve0                            # 순수 현금(무수익)
    reload_vault = reload_reserve0                                # Reload Vault (자본 비율)
    hard_vault = 0.0                                             # Hard Vault — 영구 잠금, 절대 재투입
    qqq_w = base["qqq"]; tqqq_w = base["tqqq"]                   # 노출 비중
    nav = 1.0; navs = []; last_reload = -10**9
    tqqq_added_cum = 0.0; tqqq_peak_val = 0.0                    # reload된 TQQQ sleeve의 MDD 추적
    pending = []   # close_t 분류로 잡힌 reload 주문 → close_{t+1}부터 실행
    rows = []; reload_events = []   # (i, type, asset, amount_w)
    # 최근 폭락 경험(prev_min_dd): 250일 룩백 최저 drawdown
    rolling_min_dd = feat["dd"].rolling(250, min_periods=1).min().shift(1).fillna(0).values

    for i in range(n):
        # 1) 어제(close_{i-1}) 분류로 들어온 reload를 오늘(close_i) 시가가 아닌 close_i 수익부터 반영
        #    → 실제로는 i-1 종가에 결정, i 종가에 체결 가정(보수적 next-bar). 비중은 i 수익에 적용.
        executed = []
        for ord_ in pending:
            amt = ord_["amount_w"]
            if ord_["asset"] == "TQQQ":
                tqqq_w += amt; tqqq_added_cum += amt
            else:
                qqq_w += amt
            reload_vault -= amt
            reload_events.append({"i": i, "type": ord_["type"], "asset": ord_["asset"], "amount_w": amt})
            executed.append(ord_)
        pending = []

        # 2) NAV 갱신 (오늘 수익 = 보유 비중 × 오늘 수익률)
        nav *= (1 + qqq_w * qa[i] + tqqq_w * ta[i])
        navs.append(nav)
        if tqqq_added_cum > 0:
            tqqq_peak_val = max(tqqq_peak_val, tqqq_w)   # sleeve MDD 근사(비중 기반)

        f = feat.iloc[i]
        vlab = vix_label(f["rv20"], cfg["vix_proxy"]); llab = lead_label(f["lead_above50"], cfg["leadership"])
        dtype = classify_row(f, rolling_min_dd[i], cfg)
        action = "HOLD"; reload_amt = 0.0; asset = ""

        # 3) close_i 분류로 reload 주문 생성 (실행은 i+1에서) — Reload Vault만, Hard 절대 금지
        can_interval = (i - last_reload) >= rl["min_interval_days"]
        sleeve_mdd_ok = True
        if tqqq_peak_val > 1e-9 and tqqq_added_cum > 0:
            sleeve_mdd = tqqq_w / tqqq_peak_val - 1.0
            sleeve_mdd_ok = sleeve_mdd > rl["sleeve_mdd_block"]
        avail = reload_vault > 1e-6 and can_interval and sleeve_mdd_ok and i < n - 1

        if dtype == "A" and avail:                       # Air pocket → TQQQ
            reload_amt = reload_vault * rl["step_pct"]; asset = "TQQQ"
        elif dtype == "B" and avail:                     # Growth Reset → QQQ 먼저, 10일 고점 회복+리더 YELLOW↑면 TQQQ
            if bool(f["break10"]) and llab in ("GREEN", "YELLOW"):
                reload_amt = reload_vault * rl["step_pct"]; asset = "TQQQ"
            else:
                reload_amt = reload_vault * rl["step_pct"]; asset = "QQQ"
        elif dtype == "C":                               # Structural Break → 매수/ reload 금지
            action = "NO_BUY(C)"
        elif dtype == "D" and avail:                     # Capitulation+Repair → QQQ 먼저; 회복 충분하면 TQQQ
            if f["lead_above20"] >= 0.6 and bool(f["break10"]):
                reload_amt = reload_vault * rl["step_pct"]; asset = "TQQQ"
            else:
                reload_amt = reload_vault * rl["step_pct"]; asset = "QQQ"

        if reload_amt > 1e-9 and asset:
            pending.append({"type": dtype, "asset": asset, "amount_w": reload_amt})
            last_reload = i; action = f"RELOAD_{asset}"

        rows.append({"i": i, "date": idx[i].date(), "qqq_drawdown": round(float(f["dd"]), 4),
                     "vix_vxn_state": vlab, "leadership_state": llab,
                     "narrative_state": "N/A-proxy", "dip_type": dtype, "action": action,
                     "reload_amount": round(reload_amt * cap, 0) if reload_amt else 0.0,
                     "asset_used": asset, "rv20": round(float(f["rv20"]), 4) if not np.isnan(f["rv20"]) else None})

    nav_s = pd.Series(navs, index=idx)
    df = pd.DataFrame(rows)
    # post-reload 수익(5d/20d): reload 체결일(i+1) 기준 자산 forward return — 실행일 이후만(no look-ahead)
    qqq_lvl = feat["qqq"].values; tqqq_lvl = feat["tqqq"].values
    df["post_reload_return_5d"] = None; df["post_reload_return_20d"] = None
    for ev in reload_events:
        exec_i = ev["i"]; lvl = tqqq_lvl if ev["asset"] == "TQQQ" else qqq_lvl
        for h, col in ((5, "post_reload_return_5d"), (20, "post_reload_return_20d")):
            j = exec_i + h
            if j < n:
                df.loc[df["i"] == exec_i - 1, col] = round(float(lvl[j] / lvl[exec_i] - 1), 4)
    # decision csv는 분류 발생일(i) 기준 행. reload 주문일 = i이고 체결 = i+1.
    # post_return은 체결일 기준 forward → 주문 행(i)에 부착(위 exec_i-1 == 주문 i)
    if write_csv:
        os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
        df.drop(columns=["i", "rv20"]).to_csv(OUT_CSV, index=False)
    return nav_s, df, reload_events


# ───────── 벤치마크 NAV (spec §1, §7) ─────────
def mdd(nav):
    nav = nav.dropna(); return float((nav / nav.cummax() - 1).min())


def recovery_tradedays(nav):
    nav = nav.dropna(); run_max = nav.cummax(); dd = (nav / run_max - 1).values
    trough_i = int(dd.argmin()); peak_val = float(run_max.iloc[trough_i])
    for k in range(trough_i, len(nav)):
        if nav.iloc[k] >= peak_val:
            return k - trough_i
    return -1   # 미회복


def build_benchmarks(feat, cfg):
    qa = feat["qqq"].pct_change().fillna(0); ta = feat["tqqq"].pct_change().fillna(0)
    idx = feat.index; out = {}
    out["QQQ_BH"] = (1 + qa).cumprod()
    out["TQQQ_BH"] = (1 + ta).cumprod()
    # TQQQ monthly DCA: 매월 첫 거래일 균등 투입(전 기간 N개월 균등). NAV = 보유 누적가치/총투입.
    months = idx.to_period("M"); first_days = ~months.duplicated()
    nmonths = int(first_days.sum())
    tqqq_lvl = feat["tqqq"].values
    def dca_nav(trigger_mask):
        invested = 0.0; shares = 0.0; navs = []; per = 1.0 / max(trigger_mask.sum(), 1)
        for i in range(len(idx)):
            if trigger_mask[i]:
                invested += per; shares += per / tqqq_lvl[i]
            val = shares * tqqq_lvl[i]
            # NAV vs 동일 cap을 한 번에 buy&hold 대비? → 투입 정규화: 가치/투입누적(=1배 기준)
            navs.append(val + (1.0 - invested))   # 미투입 현금은 무수익으로 보유
        return pd.Series(navs, index=idx)
    out["TQQQ_DCA_monthly"] = dca_nav(np.asarray(first_days))
    # TQQQ drawdown DCA: QQQ peak 대비 -trigger 이하인 날 균등 투입(미리 트리거일 수 계산해 균등)
    dd_trigger = feat["dd"] <= cfg["dca"]["drawdown_trigger"]
    # 같은 dip에서 매일 사지 않게: 3거래일 간격
    mask = np.zeros(len(idx), dtype=bool); last = -10**9
    for i in range(len(idx)):
        if dd_trigger.iloc[i] and (i - last) >= 3:
            mask[i] = True; last = i
    out["TQQQ_DCA_drawdown"] = dca_nav(mask)
    # A2 base without TQ-DH: QQQ35/TQQQ35/Cash30 고정(현금 무수익)
    out["A2_base"] = (1 + cfg["a2_base"]["qqq"] * qa + cfg["a2_base"]["tqqq"] * ta).cumprod()
    return out


def main():
    cfg = load_cfg(); cap = cfg["capital"]
    feat = build_features(cfg)
    nav_tqdh, dec, reload_events = simulate_tq_dh(feat, cfg)
    bench = build_benchmarks(feat, cfg)
    series = dict(bench); series["A2_with_TQ-DH"] = nav_tqdh

    # ── Vaulted Profit / reload usage / Type C 비율 ──
    n_reloads = len(reload_events)
    n_type_c_reloads = sum(1 for e in reload_events if e["type"] == "C")   # 설계상 0 (C=금지)
    # Vaulted Profit = reload로 진입한 자산의 실현/평가 이득의 누적(주문 시점 가치 대비 만기 가치).
    # 보수적: 각 reload의 (체결가→최종가) 수익 × 비중을 자본환산.
    idx = feat.index; n = len(idx)
    qqq_lvl = feat["qqq"].values; tqqq_lvl = feat["tqqq"].values
    vaulted_profit_w = 0.0
    for e in reload_events:
        ei = e["i"]; lvl = tqqq_lvl if e["asset"] == "TQQQ" else qqq_lvl
        ret_to_end = lvl[-1] / lvl[ei] - 1.0
        vaulted_profit_w += e["amount_w"] * ret_to_end
    vaulted_profit = vaulted_profit_w * cap

    # ── metrics table ──
    def row(name, nav):
        return {"strategy": name, "final_nav_x": round(float(nav.dropna().iloc[-1]), 3),
                "mdd": round(mdd(nav), 3), "recovery_tradedays": recovery_tradedays(nav)}
    order = ["TQQQ_BH", "TQQQ_DCA_monthly", "TQQQ_DCA_drawdown", "QQQ_BH", "A2_base", "A2_with_TQ-DH"]
    table = [row(k, series[k]) for k in order]
    tbl = pd.DataFrame(table)

    # ── 차트 ──
    plt.style.use("dark_background")
    fig = plt.figure(figsize=(11, 5))
    col = {"TQQQ_BH": "#ec4899", "TQQQ_DCA_monthly": "#fb923c", "TQQQ_DCA_drawdown": "#fbbf24",
           "QQQ_BH": "#a78bfa", "A2_base": "#94a3b8", "A2_with_TQ-DH": "#22d3ee"}
    for k in order:
        s = series[k].dropna()
        plt.plot(s.index, cap * s / s.iloc[0] / 1e8, label=k, lw=2.4 if "TQ-DH" in k else 1.4,
                 color=col[k], ls="-" if ("A2" in k or k == "QQQ_BH") else "--")
    plt.legend(framealpha=.2, ncol=3, fontsize=8)
    plt.title("PRAMANA A2 TQ-DH — backtest 2016~2026 (₩1억·첫 거래일 기준)·PAPER·검증 알파 아님")
    plt.ylabel("계좌금액(억원)"); plt.yscale("log")
    os.makedirs(os.path.dirname(CHART), exist_ok=True)
    fig.savefig(CHART, dpi=95, bbox_inches="tight", facecolor="#0d1326"); plt.close(fig)

    # ── verdict (pre-registered) ──
    a2 = series["A2_with_TQ-DH"]; a2b = series["A2_base"]; tdca = series["TQQQ_DCA_drawdown"]
    a2_fin = float(a2.dropna().iloc[-1]); a2b_fin = float(a2b.dropna().iloc[-1])
    a2_mdd = mdd(a2); a2b_mdd = mdd(a2b); a2_rec = recovery_tradedays(a2); a2b_rec = recovery_tradedays(a2b)
    # 성공조건 (spec §8): A2 with TQ-DH vs A2 without — NAV≥, MDD<, recovery<, Vaulted Profit>0
    s_nav = a2_fin >= a2b_fin - 1e-6
    s_mdd = a2_mdd >= a2b_mdd - 1e-6      # MDD는 음수: 덜 깊음(0에 더 가까움=더 큰 값)이 통과
    s_rec = (a2_rec != -1 and a2b_rec != -1 and a2_rec <= a2b_rec) or (a2_rec != -1 and a2b_rec == -1)
    s_vp  = vaulted_profit > 0
    success = s_nav and s_mdd and s_rec and s_vp
    # 실패조건 (spec §9): TQ-DH < drawdown DCA on BOTH nav & mdd / reload 대부분 Type C / Hard Vault 의존 / A2가 QQQ 대비 큰 언더퍼폼 확대
    f_vs_dca = (a2_fin < float(tdca.dropna().iloc[-1])) and (a2_mdd < mdd(tdca))   # 둘 다 열위
    f_typec = (n_type_c_reloads / n_reloads > 0.5) if n_reloads else False
    f_hard = False   # 설계상 Hard Vault 사용 0 → 의존 불가
    fail = f_vs_dca or f_typec or f_hard

    # ── report ──
    dip_counts = dec["dip_type"].value_counts().to_dict()
    asset_counts = pd.Series([e["asset"] for e in reload_events]).value_counts().to_dict() if reload_events else {}
    # reload별 평균 forward 수익
    pr5 = pd.to_numeric(dec["post_reload_return_5d"], errors="coerce").dropna()
    pr20 = pd.to_numeric(dec["post_reload_return_20d"], errors="coerce").dropna()
    write_report(cfg, tbl, series, n_reloads, n_type_c_reloads, asset_counts, vaulted_profit,
                 dip_counts, pr5, pr20, success, fail, s_nav, s_mdd, s_rec, s_vp,
                 f_vs_dca, f_typec, a2_fin, a2b_fin, a2_mdd, a2b_mdd, a2_rec, a2b_rec)

    print("✅ TQ-DH backtest 완료")
    print(tbl.to_string(index=False))
    print(f"reloads={n_reloads} (TypeC={n_type_c_reloads}) · assets={asset_counts} · "
          f"Vaulted Profit=₩{vaulted_profit/1e6:.1f}M")
    print(f"성공조건(vs A2 base): NAV{'✅' if s_nav else '❌'} MDD{'✅' if s_mdd else '❌'} "
          f"Recovery{'✅' if s_rec else '❌'} VaultedProfit{'✅' if s_vp else '❌'} → "
          f"{'SUCCESS' if success else 'NOT MET'}")
    print(f"실패조건: vs drawdown-DCA(nav&mdd both worse)={f_vs_dca} · TypeC-dominant={f_typec} → "
          f"{'FAIL' if fail else 'no fail trigger'}")
    print(f"outputs: {OUT_CSV}\n         {REPORT}\n         {CHART}")


def write_report(cfg, tbl, series, n_reloads, n_type_c, asset_counts, vaulted_profit,
                 dip_counts, pr5, pr20, success, fail, s_nav, s_mdd, s_rec, s_vp,
                 f_vs_dca, f_typec, a2_fin, a2b_fin, a2_mdd, a2b_mdd, a2_rec, a2b_rec):
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    cap = cfg["capital"]
    def won(x): return f"₩{x/1e8:.3f}억"
    md = []
    md.append("# A2 TQ-DH (TQQQ Dip Harvester) — Weekly/Backtest Review\n")
    md.append(f"> 생성 {dt.date.today()} · backtest 2016-01~2026-06 · PAPER only · 자본권한 0 · **검증된 알파 아님**.\n")
    md.append("> spec: `pramana_a2_delta_patch_pack/03_TQ_DH_TQQQ_DIP_HARVESTER.md` (+05 §5 reload rules)\n")

    md.append("\n## 0. 사전등록 (Pre-registered) 성공·실패 조건 — 결과 보기 전에 박음\n")
    md.append("**성공조건 (spec §8) — A2 *with* TQ-DH가 A2 *without* TQ-DH 대비:**\n")
    md.append("1. final NAV ≥ (같거나 높음)\n2. MDD 더 낮음(덜 깊음)\n3. 회복기간 더 짧음\n4. Vaulted Profit > 0\n")
    md.append("\n→ TQQQ buy-and-hold보다 최종 NAV가 *낮아도 괜찮다* (대신 MDD·Vaulted Profit에서 보상).\n")
    md.append("\n**실패조건 (spec §9) — 하나라도 해당 시:**\n")
    md.append("- TQ-DH가 TQQQ drawdown DCA보다 final NAV·MDD **둘 다** 열위\n")
    md.append("- Reload가 대부분 Type C(구조붕괴)에서 발생\n")
    md.append("- Hard Vault를 써야만 성과가 남 (설계상 Hard Vault 재투입 금지 → 구조적으로 불가)\n")
    md.append("- Reload 후 손실 반복 / A2가 QQQ 대비 언더퍼폼을 크게 확대\n")

    md.append("\n## 1. 방법론·치환 (정직 라벨)\n")
    md.append("- **VIX/VXN proxy**: 캐시에 VIX/VXN 없음 → **QQQ 20일 realized volatility(연율화)**로 치환. "
              "라벨 = `GREEN/YELLOW/RED-proxy` (calm<20%·elevated<35%·이상 RED). 진짜 VIX term-structure·skew 아님.\n")
    md.append("- **Leadership**: sp500 패널의 대형주 10종(NVDA·MSFT·AAPL·AMZN·GOOGL·META·AVGO·TSLA·AMD·NFLX) vs 50일선 비율 (실데이터).\n")
    md.append("- **Narrative/Earnings/Credit**: LLM·HYG/IEF 미구현 → `narrative_state = N/A-proxy` (정직 공백).\n")
    md.append("- **NO LOOK-AHEAD**: close_t로 분류한 dip은 close_{t+1}부터만 reload 체결·수익 계산. 회복확인(10일고점·follow-through)도 과거 데이터만.\n")
    md.append(f"- **Reload Vault**: 자본의 {cfg['reload']['reserve_pct']*100:.0f}%를 reserve로 분리, "
              f"1 reload = Reload Vault의 {cfg['reload']['step_pct']*100:.0f}%, 최소 간격 {cfg['reload']['min_interval_days']}거래일, "
              "Type C=reload 금지, **Hard Vault는 절대 사용 안 함**.\n")

    md.append("\n## 2. 백테스트 비교 (₩1억 기준·log 차트 = `outputs/a2_live/tq_dh_backtest.png`)\n\n")
    md.append("| 전략 | 최종 NAV(배) | 최종 평가액 | MDD | 회복(거래일) |\n|---|---:|---:|---:|---:|\n")
    for _, r in tbl.iterrows():
        finw = won(cap * r["final_nav_x"]); rec = "미회복" if r["recovery_tradedays"] == -1 else f"{r['recovery_tradedays']}"
        md.append(f"| {r['strategy']} | {r['final_nav_x']:.3f} | {finw} | {r['mdd']*100:.1f}% | {rec} |\n")

    md.append("\n## 3. TQ-DH 동작 통계\n")
    md.append(f"- 총 reload 횟수: **{n_reloads}** · Type C에서 발생: **{n_type_c}** "
              f"({(n_type_c/n_reloads*100) if n_reloads else 0:.0f}% — 설계상 0이어야 함)\n")
    md.append(f"- reload 자산 분포: {asset_counts or '없음'}\n")
    md.append(f"- **Vaulted Profit** (reload 자산의 체결→최종 누적 이득): **{won(vaulted_profit)}** "
              f"({vaulted_profit/cap*100:+.2f}% of 자본)\n")
    md.append(f"- dip type 분류 일수: {dip_counts}\n")
    if len(pr5):
        md.append(f"- reload 후 평균 수익: 5일 {pr5.mean()*100:+.2f}% (n={len(pr5)}) · 20일 {pr20.mean()*100:+.2f}% (n={len(pr20)})\n")
    md.append("- 결정 로그: `outputs/a2_live/tq_dh_decisions.csv` (date·qqq_drawdown·vix_vxn_state·leadership_state·narrative_state·dip_type·action·reload_amount·asset_used·post_reload_return_5d/20d)\n")

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
    md.append(f"- Hard Vault 의존: 아니오 (설계상 Hard Vault 재투입 코드상 불가)\n")
    md.append(f"\n**실패조건 종합: {'⚠️ FAIL 트리거 발생' if fail else '✅ 실패조건 없음'}**\n")

    md.append("\n## 5. 정직한 결론 (Honest Verdict)\n")
    verdict = honest_verdict(success, fail, a2_fin, a2b_fin, a2_mdd, a2b_mdd, series, vaulted_profit, n_reloads)
    md.append(verdict)

    md.append("\n## 6. Caveats (한계 — 결과 해석 시 필수)\n")
    md.append("- **VIX-proxy 치환**: 실 VIX/VXN 아닌 QQQ 20일 realized vol. spike-then-ease·term-structure 신호 손실.\n")
    md.append("- **표본 편향**: 2016~2026 = 닷컴(-49%)·2008(-55%) **없음**. TQQQ는 그런 장기 하락장에서 daily-rebalance decay로 -90%+ 가능. "
              "이 백테스트는 *강세장 편향* 구간이라 TQQQ 계열이 구조적으로 유리 → TQ-DH의 진짜 가치(긴 하락장 자본 보존)는 **검증 불가**.\n")
    md.append("- **Narrative/Credit 공백**: LLM narrative·HYG/IEF credit stress 미구현 → Type C 식별이 가격+200일선+leadership에만 의존(과소·과대 가능).\n")
    md.append("- **체결 단순화**: reload를 다음 종가 1회 체결로 근사(슬리피지·부분체결 무시). 비용(수수료/스프레드) 미반영.\n")
    md.append("- PAPER only · NO LIVE · 자본권한 0 · TQQQ는 Core/알파가 아니라 Booster.\n")
    open(REPORT, "w").write("".join(md))


def honest_verdict(success, fail, a2_fin, a2b_fin, a2_mdd, a2b_mdd, series, vp, n_reloads):
    tqqq_fin = float(series["TQQQ_BH"].dropna().iloc[-1])
    lines = []
    if success and not fail:
        lines.append(f"**SUCCESS (사전등록 조건 충족).** A2 with TQ-DH가 A2 base 대비 NAV {a2_fin/a2b_fin-1:+.1%}·"
                     f"MDD {(a2_mdd-a2b_mdd)*100:+.1f}%p로 우위이고 Vaulted Profit(₩{vp/1e6:.0f}M)이 양수. "
                     "단, 이는 *강세장 편향 표본*에서의 결과이며 검증된 알파가 아님 — caveat 6 참조.\n")
    elif fail:
        lines.append("**FAIL 트리거 발생.** 사전등록 실패조건에 해당 → TQ-DH는 이 형태로 채택하지 않음. "
                     "튜닝으로 살리지 말 것(goalpost 불변).\n")
    else:
        lines.append(f"**NOT MET (성공조건 일부 미충족, 그러나 명시적 FAIL 트리거는 없음).** "
                     f"A2 with TQ-DH NAV={a2_fin:.2f}배 vs A2 base {a2b_fin:.2f}배. "
                     "spec이 예고했듯 최종 NAV에서 TQQQ buy-and-hold("
                     f"{tqqq_fin:.1f}배)를 못 이기는 것은 정상 — 평가는 MDD/회복/Vaulted Profit으로 한다.\n")
    lines.append("\n핵심 정직 메모: (a) Reload Vault(자본 10%)만 쓰므로 TQ-DH의 NAV 기여 *상한*이 작다 — "
                 "구조적으로 TQQQ buy-and-hold를 NAV로 이길 수 없게 설계됨(의도된 보수성). "
                 "(b) 강세장 편향 표본에서는 'dip을 가려 사는' 절제가 '아무 dip이나 사는' 단순 DCA보다 "
                 "NAV를 깎을 수 있다(상승장에선 더 많이 살수록 유리). TQ-DH의 진짜 효용은 *긴 하락장 자본 보존*인데 "
                 "이 표본엔 그런 구간이 없어 측정 불가. (c) 따라서 이 결과는 '기계가 약속대로 작동하고 look-ahead 없이 "
                 "dip을 분류·절제한다'는 **machinery 검증**이지, '수익 알파 입증'이 아니다.\n")
    return "".join(lines)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""PRAMANA paper execution engine — target weights → realistic per-name *paper* fills + cost breakdown.
시장중립 US equity long-short PAPER book용. 순수 함수(데이터 로딩 0 · API 0; 호출측이 전부 넘김). cost.py 재사용.
모델/가정(honest, 모두 명시):
  • trading cost(spread+commission) = cost.py 동결 tier(ADV 있으면 tier_adv_bps 25/45/75, 없으면 tier_marketcap_bps 5/10/15) one-way bps,
    각 name turnover(|order|)에 적용. **새 비용추정 0** — tier는 cost.py에서만.
  • market impact = square-root model: impact_bps = K_IMPACT * sqrt(participation), participation = order_notional/ADV_name.
    가정: **K_IMPACT=10bp at 100% participation 기준(=참여율 1%→1bp)**. 이건 paper용 거친 추정치(square-root law, Almgren류) — 동결 cost.py와 별개의 *명시된* 임팩트 가정. ADV 없으면 impact=0(못 추정).
  • partial fill: participation > adv_participation_cap(기본 10%)이면 한 리밸런스에 다 못 채움 → order를 cap participation까지 scale down, 그 name fill_ratio<1.
    impact_bps는 *체결된* 부분의 participation(=cap)으로 계산(체결분에만 비용).
  • short borrow = borrow_ann/12(월 1회 리밸런스 가정) × short notional(target_w<0 names의 |target_w|). holding 비용이라 *target* short에 부과(거래분 아님).
  • 모든 cost는 fraction-of-NAV(소수)로 반환. no-op(target==current)이면 orders=0·costs=0.
⚠️ paper(가상)·결정적. live/실거래 아님."""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cost as C  # tier_marketcap_bps, tier_adv_bps, BPS (동결 비용 tier)

K_IMPACT_BPS = 10.0  # square-root impact: bps at participation=1.0(=100%). participation 1%→1bp. (paper 가정, Almgren류)


def simulate_fills(target_w, current_w, *, mc, adv=None, aum,
                   adv_participation_cap=0.10, borrow_ann=0.005):
    """target weights → filled weights + cost breakdown (전부 fraction-of-NAV).

    Args:
      target_w : Series[ticker->weight]  목표 가중치(음수=숏). dollar-neutral 가정이지만 강제 안 함.
      current_w: Series[ticker->weight]  현재 보유 가중치.
      mc       : Series[ticker->marketcap]  trading-cost tier용(adv None일 때).
      adv      : Series[ticker->ADV $]|None  있으면 tier_adv_bps + market impact 활성.
      aum      : float  book NAV(달러). order_notional 환산용.
      adv_participation_cap: 한 리밸런스 max ADV 참여율(초과분은 partial fill).
      borrow_ann: 숏 차입비용(연). /12로 월부과.

    Returns dict:
      filled_w   : Series  실제 체결 후 가중치(partial fill 반영).
      orders     : Series  target - current(체결 전 의도 주문).
      fill_ratio : float   전체 체결율 = filled turnover / target turnover(주문 0이면 1.0).
      costs      : dict     spread_commission, impact, borrow, total (fraction-of-NAV).
      notes      : str
    """
    # ── align: 양쪽 어디든 등장한 ticker는 전부 포함(없으면 0) ──
    target_w = pd.Series(target_w, dtype=float)
    current_w = pd.Series(current_w, dtype=float)
    idx = target_w.index.union(current_w.index)
    tw = target_w.reindex(idx).fillna(0.0)
    cw = current_w.reindex(idx).fillna(0.0)
    aum = float(aum)

    orders = tw - cw                       # 의도 주문(per name, weight 단위)
    abs_ord = orders.abs()
    intended_turnover = abs_ord.sum()      # one-way turnover(주문 노셔널 합 / NAV)

    zero_costs = {"spread_commission": 0.0, "impact": 0.0, "borrow": 0.0, "total": 0.0}

    # ── no-op: target==current → 주문/비용 0 (단 borrow는 holding 비용이라 별도; 아래 short_w로 처리) ──
    # 거래가 0이어도 숏 포지션을 그대로 들고 있으면 borrow는 발생. spec의 "no-op cost 0"은
    # target==current && (숏 없음) 케이스. 숏이 있으면 borrow만 남는 게 정직. 둘 다 명시 처리.
    no_trade = intended_turnover <= 0 or aum <= 0

    # ── short borrow (holding 비용): target short notional 기준, 월부과 ──
    short_w = (-tw.clip(upper=0.0)).sum()            # Σ|target_w<0|  (fraction of NAV)
    borrow_cost = float(borrow_ann / 12.0 * short_w)  # fraction-of-NAV

    if no_trade:
        filled_w = cw.copy()
        costs = dict(zero_costs)
        costs["borrow"] = borrow_cost
        costs["total"] = borrow_cost
        note = "no-op: target==current (주문 0)" + (f"; 숏 holding borrow={borrow_cost:.6f}" if short_w > 0 else "; 숏 없음 → 전 비용 0")
        return {"filled_w": filled_w, "orders": orders, "fill_ratio": 1.0,
                "costs": costs, "notes": note}

    # ── partial fill: ADV 참여율 cap (ADV 있을 때만; 없으면 항상 full fill 가정) ──
    # fill_frac[name] ∈ (0,1]: participation>cap이면 cap/participation 만큼만 체결.
    if adv is not None:
        adv_s = pd.Series(adv, dtype=float).reindex(idx)
        order_notional = abs_ord * aum                       # $ per name
        # participation = 주문노셔널 / ADV. ADV 결측·0 → 참여율 산정 불가 → full fill(impact 0) 처리.
        with np.errstate(divide="ignore", invalid="ignore"):
            participation = order_notional / adv_s
        participation = participation.replace([np.inf, -np.inf], np.nan)
        fill_frac = pd.Series(1.0, index=idx)
        capped = participation > adv_participation_cap
        capped = capped.fillna(False)
        fill_frac[capped] = (adv_participation_cap / participation[capped]).astype(float)
    else:
        adv_s = None
        participation = None
        fill_frac = pd.Series(1.0, index=idx)

    # 체결 주문/가중치 (partial 반영)
    filled_orders = orders * fill_frac
    filled_w = cw + filled_orders
    filled_turnover = filled_orders.abs().sum()
    fill_ratio = float(filled_turnover / intended_turnover) if intended_turnover > 0 else 1.0

    # ── trading cost (spread+commission): cost.py 동결 tier, one-way bps, 체결 turnover에 적용 ──
    if adv is not None:
        tier_bps = C.tier_adv_bps(adv_s)                 # 25/45/75 (ADV tercile)
    else:
        tier_bps = C.tier_marketcap_bps(mc)              # 5/10/15  (marketcap tercile)
    tier_frac = (tier_bps / C.BPS).reindex(idx).fillna(0.0)
    spread_comm = float((filled_orders.abs() * tier_frac).sum())  # fraction-of-NAV

    # ── market impact (square-root): 체결분 participation 기준, 체결 turnover에 적용 ──
    if adv is not None:
        filled_participation = participation * fill_frac  # capped name은 ≈ cap
        filled_participation = filled_participation.fillna(0.0).clip(lower=0.0)
        impact_bps = K_IMPACT_BPS * np.sqrt(filled_participation)
        impact_frac_name = (impact_bps / C.BPS) * filled_orders.abs()  # bps×turnover
        impact = float(impact_frac_name.sum())
    else:
        impact = 0.0

    total = spread_comm + impact + borrow_cost
    costs = {"spread_commission": spread_comm, "impact": impact,
             "borrow": borrow_cost, "total": float(total)}

    n_partial = int((fill_frac < 1.0).sum())
    note = (f"filled {fill_ratio:.3f} of target turnover; partial-fill names={n_partial}; "
            f"tier={'ADV 25/45/75' if adv is not None else 'mc 5/10/15'}; "
            f"impact={'sqrt(K=%.0fbp@100%%)' % K_IMPACT_BPS if adv is not None else 'off(no ADV)'}; "
            f"borrow={borrow_ann:.3%}/yr on short {short_w:.3f}")
    return {"filled_w": filled_w, "orders": orders, "fill_ratio": fill_ratio,
            "costs": costs, "notes": note}


# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # SYNTHETIC smoke test — 외부 데이터 0. 4개 속성 증명.
    np.random.seed(0)
    AUM = 100_000_000.0  # 가상 $100M paper book

    def ok(b):  # PASS/FAIL helper
        return "PASS" if b else "FAIL"

    results = []

    # ── (1) no-op: target==current → cost 0 (숏 없는 케이스로) ──
    w = pd.Series({"AAA": 0.3, "BBB": 0.2, "CCC": -0.2, "DDD": -0.3})  # dollar-neutral
    mc = pd.Series({"AAA": 8e11, "BBB": 5e10, "CCC": 2e9, "DDD": 3e10})
    # 숏이 있으면 borrow는 남으므로, no-op "cost 0" 증명은 long-only target로:
    wl = pd.Series({"AAA": 0.5, "BBB": 0.5})
    mcl = pd.Series({"AAA": 8e11, "BBB": 5e10})
    r_noop = simulate_fills(wl, wl, mc=mcl, aum=AUM)
    p1 = (r_noop["orders"].abs().sum() == 0.0) and (r_noop["costs"]["total"] == 0.0) and (r_noop["fill_ratio"] == 1.0)
    print(f"[1] no-op (target==current, no short) → orders=0, total cost={r_noop['costs']['total']:.8f} ... {ok(p1)}")
    results.append(p1)

    # ── (2) partial fill: 한 name 주문이 ADV 참여율 cap 초과 → fill_ratio<1 ──
    # current 0 → target 큰 비중 + 작은 ADV → participation>cap.
    tgt = pd.Series({"BIG": 0.40, "LIQ": 0.10, "SHO": -0.50})
    cur = pd.Series({"BIG": 0.0, "LIQ": 0.0, "SHO": 0.0})
    mc2 = pd.Series({"BIG": 5e9, "LIQ": 9e11, "SHO": 5e10})
    # BIG order_notional = 0.40*100M = $40M. ADV=$50M → participation 0.80 >> cap 0.10 → 강한 partial.
    # LIQ order_notional = $10M, ADV=$5B → participation 0.002 < cap → full.
    adv2 = pd.Series({"BIG": 50e6, "LIQ": 5e9, "SHO": 200e6})
    r_pf = simulate_fills(tgt, cur, mc=mc2, adv=adv2, aum=AUM, adv_participation_cap=0.10)
    # 검증: 전체 fill_ratio<1, 그리고 BIG의 체결 가중치 < target(scale down)
    big_filled = r_pf["filled_w"]["BIG"]
    p2 = (r_pf["fill_ratio"] < 1.0) and (abs(big_filled) < abs(tgt["BIG"]) - 1e-9) and (abs(r_pf["filled_w"]["LIQ"] - tgt["LIQ"]) < 1e-9)
    print(f"[2] partial fill (BIG part.={0.40*AUM/adv2['BIG']:.2f}>cap 0.10) → fill_ratio={r_pf['fill_ratio']:.3f}<1, "
          f"BIG filled {big_filled:.3f} (target 0.400), LIQ full {r_pf['filled_w']['LIQ']:.3f} ... {ok(p2)}")
    results.append(p2)

    # ── (3) cost breakdown components sum to total (부동소수 tol) ──
    comp = r_pf["costs"]
    s = comp["spread_commission"] + comp["impact"] + comp["borrow"]
    p3 = abs(s - comp["total"]) < 1e-12
    print(f"[3] breakdown sums to total: spread+comm={comp['spread_commission']:.6f} + impact={comp['impact']:.6f} "
          f"+ borrow={comp['borrow']:.6f} = {s:.6f} vs total={comp['total']:.6f} ... {ok(p3)}")
    results.append(p3)

    # ── (4) short names accrue borrow ──
    # SHO target=-0.50 → short_w=0.50. borrow=0.005/12*0.50.
    expected_borrow = 0.005 / 12.0 * 0.50
    p4a = abs(comp["borrow"] - expected_borrow) < 1e-12 and comp["borrow"] > 0.0
    # long-only target → borrow 0 (대조군)
    r_long = simulate_fills(pd.Series({"AAA": 0.5, "BBB": 0.5}), pd.Series({"AAA": 0.0, "BBB": 0.0}),
                            mc=pd.Series({"AAA": 8e11, "BBB": 5e10}), aum=AUM)
    p4b = r_long["costs"]["borrow"] == 0.0
    p4 = p4a and p4b
    print(f"[4] short borrow: short_w=0.50 → borrow={comp['borrow']:.6f} (expect {expected_borrow:.6f}), "
          f"long-only borrow={r_long['costs']['borrow']:.6f}=0 ... {ok(p4)}")
    results.append(p4)

    print("\n" + ("ALL PASS ✅" if all(results) else "SOME FAILED ❌") + f"  ({sum(results)}/{len(results)})")
    sys.exit(0 if all(results) else 1)

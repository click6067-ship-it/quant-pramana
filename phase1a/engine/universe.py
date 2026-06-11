#!/usr/bin/env python3
"""Phase 2 M2 — Research Engine universe module.
책임: PIT universe 생성 *만* (SP500 멤버십 역재생 · marketcap rank universe · common/delisted 보존).
feature/signal/portfolio/cost 로직 0. 입력 전부 캐시(SP500_membership·DAILY_all·TICKERS) → API-free.
기존 build_broad_universe·build_smallmid_universe·b0b1_sp500의 universe 로직 통합(복붙 제거), 숫자 1:1 재현.
사용: python engine/universe.py verify"""
import os, sys, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd, data

OUT = os.path.join(data.PHASE1A, "outputs")
ENGOUT = os.path.join(OUT, "engine"); os.makedirs(ENGOUT, exist_ok=True)

def _uhash(df):
    key = df[["asof", "ticker"]].astype(str).agg("|".join, axis=1).sort_values()
    return hashlib.sha256("\n".join(key).encode()).hexdigest()[:16]

# ── common/delisted (API-free, 동결 TICKERS) ────────────────────────────────
def ticker_flags():
    tk = data.load_tickers()
    return (tk["category"] == "Domestic Common Stock"), (tk["isdelisted"].astype(str).str.upper() == "Y")

# ── marketcap rank universe (top-1500 / small-mid 공통) ──────────────────────
def _month_end_grid():
    dl = data.load("DAILY_all", usecols=["ticker", "date", "marketcap"])
    dl = dl[dl["marketcap"] > 0].copy(); dl["ym"] = dl["date"].dt.to_period("M")
    return dl, dl.groupby("ym")["date"].max()

def rank_universe(lo, hi, _grid=None):
    """월말(실제 마지막 거래일) marketcap rank lo..hi PIT 유니버스. DAILY_all=common-only라 common 자동."""
    dl, month_end = _grid if _grid else _month_end_grid()
    rows = []
    for ym, med in month_end.items():
        day = dl[dl["date"] == med].sort_values("marketcap", ascending=False).reset_index(drop=True)
        day["rank"] = day.index + 1
        sel = day[(day["rank"] >= lo) & (day["rank"] <= hi)]
        rows.append(sel.assign(asof=med)[["asof", "ticker", "marketcap", "rank"]])
    return pd.concat(rows, ignore_index=True)

# ── SP500 PIT 멤버십 (added/removed 역재생 — b0b1_sp500과 동일) ──────────────
def sp500_pit():
    sp = data.load("SP500_membership"); sp["date"] = pd.to_datetime(sp["date"])
    current = set(sp[sp["action"] == "current"].ticker)
    ev = sp[sp["action"].isin(["added", "removed"])][["date", "action", "ticker"]].sort_values("date")
    ev_desc = list(ev.itertuples(index=False))[::-1]
    def members_asof(T):
        m = set(current)
        for d, action, tk in ev_desc:
            if d <= T: break
            if action == "added": m.discard(tk)
            else: m.add(tk)
        return m
    ever = sorted(sp.ticker.unique())
    return members_asof, ever, current, sp

def sp500_universe(month_end):
    """월말 그리드 위 PIT S&P500 멤버십 → long-form (asof,ticker)."""
    members_asof, ever, current, sp = sp500_pit()
    rows = []
    for ym, med in month_end.items():
        for tk in members_asof(med):
            rows.append((med, tk))
    return pd.DataFrame(rows, columns=["asof", "ticker"]), ever, sp

# ── 검증: 3 앵커 universe 기존 1:1 재현 ─────────────────────────────────────
def _cmp(name, new, ref_path, count_target=None):
    print(f"\n[{name}]")
    if not os.path.exists(ref_path):
        print(f"  (기존 {os.path.basename(ref_path)} 없음 — 신규 생성만)")
        ref = None
    else:
        ref = pd.read_csv(ref_path); ref["asof"] = pd.to_datetime(ref["asof"])
    nu = new["ticker"].nunique(); nmonth = new.groupby("asof").size()
    print(f"  생성: union={nu} · 월수={new['asof'].nunique()} · 월별 median={int(nmonth.median())} (min{nmonth.min()}/max{nmonth.max()})")
    ok = True
    if ref is not None:
        ru = ref["ticker"].nunique()
        sa = set(new[["asof", "ticker"]].astype(str).agg("|".join, 1))
        sb = set(ref[["asof", "ticker"]].astype(str).agg("|".join, 1))
        same = (sa == sb)
        print(f"  기존: union={ru} · (asof,ticker) 집합 일치={'✅ YES' if same else '❌ NO'} (Δ {len(sa^sb)})")
        print(f"  union 일치={'✅' if nu==ru else '❌ '+str((nu,ru))} · hash new={_uhash(new)} ref={_uhash(ref)}")
        ok = same and (nu == ru)
    if count_target is not None:
        print(f"  count target {count_target}: {'✅' if nu==count_target else '❌ '+str(nu)}")
        ok = ok and (nu == count_target)
    return ok

def verify():
    print("=" * 76); print("Phase 2 M2 — universe.py 기존 1:1 재현 검증 (API-free, read-only)"); print("=" * 76)
    iscommon, isdel = ticker_flags()
    grid = _month_end_grid(); _, month_end = grid
    results = {}

    # A. SP500 PIT
    spu, ever, sp = sp500_universe(month_end)
    spu.to_csv(os.path.join(ENGOUT, "sp500_pit.csv"), index=False)
    print("\n[A. SP500 PIT]")
    nmonth = spu.groupby("asof").size()
    print(f"  ever-members={len(ever)} (target 712) {'✅' if len(ever)==712 else '❌'} · 월별 median={int(nmonth.median())} (target≈500)")
    removed_ever = set(sp[sp["action"] == "removed"].ticker)
    print(f"  survivorship: removed-ever in ever={len(removed_ever & set(ever))} · delisted in ever={int(isdel.reindex(ever).fillna(False).sum())} (보존>0)")
    results["A_sp500"] = (len(ever) == 712)

    # B. top-1500 broad
    top1500 = rank_universe(1, 1500, _grid=grid)
    top1500.to_csv(os.path.join(ENGOUT, "broad_top1500.csv"), index=False)
    results["B_top1500"] = _cmp("B. top-1500 broad", top1500, os.path.join(OUT, "broad_universe_top1500.csv"), count_target=2973)

    # C. small/mid 1001-3000
    sm = rank_universe(1001, 3000, _grid=grid)
    sm.to_csv(os.path.join(ENGOUT, "smallmid_1001_3000.csv"), index=False)
    results["C_smallmid"] = _cmp("C. small/mid 1001-3000", sm, os.path.join(OUT, "smallmid_universe_1001_3000.csv"), count_target=4504)

    print("\n" + "=" * 76)
    allok = all(results.values())
    for k, v in results.items(): print(f"  {k}: {'PASS' if v else 'FAIL'}")
    print(f"판정: {'PASS — 3 앵커 universe 1:1 재현(API-free)' if allok else 'FAIL — 재현 불일치'}")
    print("→ outputs/engine/{sp500_pit,broad_top1500,smallmid_1001_3000}.csv")
    return allok

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "verify"
    if cmd == "verify":
        sys.exit(0 if verify() else 1)
    else:
        print(__doc__); sys.exit(2)

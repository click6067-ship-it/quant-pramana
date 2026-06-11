#!/usr/bin/env python3
"""PRAMANA v3 — CANDIDATE sleeve3: short-term (1-month) cross-sectional REVERSAL.
질문: 기존 2-sleeve book(eq=equity MN L/S, ov=ETF trend+vol overlay; 둘 상관 +0.06)에
      세 번째 *거의 무상관* 분산 수익원을 더하는가?
정의(ONE·튜닝/윈도우헌팅 0): top-1500 PIT 유니버스에서 매월 PRIOR 1-month return으로 랭크 →
      LONG 하위 분위(losers)·SHORT 상위 분위(winners)·섹터중립·equal-weight·dollar-neutral.
      forward = 다음달 수익. (classic ST-reversal anomaly; 12-1 momentum·trend와 통상 무상관.)
비용 CRITICAL(ST reversal=고회전): cost.tier_marketcap_bps round-trip(×2) on turnover + 숏 borrow ~0.5%/yr.
사전등록 kill(결과 前 박음): net Sharpe≤0 FAIL · |corr|>0.5 to eq OR ov → 분산 아님 · 2x cost서 사망 FAIL · turnover 과해 net 음수 FAIL.
데이터(캐시 only·API 0): broad_SEP(closeadj) · DAILY_all(marketcap) · broad_universe_top1500(PIT) · combined_book_nav(eq/ov).
사용: ./.venv/bin/python engine/sleeve3_reversal.py · ⚠️ paper(가상)·단일 백테스트·no live."""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import data, cost as C

QUINTILE   = 0.2           # 분위(상/하 20%). decile도 보고(분위가 primary; ONE 정의 = quintile).
BORROW_ANN = 0.005         # 숏 borrow 연 0.5%/yr (prompt 명시; flat)
MIN_NAMES  = 100           # ls_book과 동일 멤버 하한
CAP_KRW    = 100_000_000

# ── 메트릭(combined_book.perf / ls_book.st와 1:1 동결) ──────────────────────
def perf(r):
    m = 12
    sh = r.mean() / r.std() * np.sqrt(m) if r.std() > 0 else np.nan
    nav = (1 + r).cumprod(); dd = (nav / nav.cummax() - 1).min(); cagr = (1 + r).prod() ** (m / len(r)) - 1
    rec = r[r.index >= "2021-01-01"]; rs = rec.mean() / rec.std() * np.sqrt(m) if rec.std() > 0 else np.nan
    return dict(sharpe=sh, cagr=cagr, maxdd=dd, fin=nav.iloc[-1], rec_sharpe=rs, vol=r.std() * np.sqrt(m))

def line(lbl, r):
    p = perf(r)
    print(f"  {lbl:30s} Sharpe={p['sharpe']:+.2f} CAGR={p['cagr']*100:+6.2f}% vol={p['vol']*100:4.1f}% maxDD={p['maxdd']*100:6.1f}% | 2021-26 Sh={p['rec_sharpe']:+.2f}")
    return p

# ── 패널 빌드: 월그리드 ST-reversal L/S (섹터중립·equal-weight·dollar-neutral) ─
def build_reversal(quintile=QUINTILE, cost_mult=1.0):
    """returns: DataFrame(index=rebal월, cols=[gross, net, to_avg, n]) · turnover_oneway 평균."""
    px = data.load("broad_SEP", usecols=["ticker", "date", "closeadj"]).pivot_table(index="date", columns="ticker", values="closeadj").sort_index()
    mc = data.load("DAILY_all", usecols=["ticker", "date", "marketcap"]).pivot_table(index="date", columns="ticker", values="marketcap").sort_index()
    sector = data.load_tickers()["sector"]
    u = pd.read_csv(os.path.join(data.PHASE1A, "outputs", "broad_universe_top1500.csv")); u["asof"] = pd.to_datetime(u["asof"])
    members = {d: set(g) for d, g in u.groupby("asof")["ticker"]}
    rebal = sorted(members.keys())

    mpx = px.reindex(rebal, method="pad")
    fwd = mpx.shift(-1) / mpx - 1                      # 다음달 forward
    rev = -(mpx.shift(1) / mpx.shift(2) - 1)           # signal = -(PRIOR 1-month return) → 큰 점수 = loser
    mcg = mc.reindex(rebal, method="pad")

    recs = []; prevL = set(); prevS = set()
    for t in rebal[:-1]:
        mem = [c for c in px.columns if c in members[t]]
        d = pd.DataFrame({"sig": rev.loc[t].reindex(mem), "fwd": fwd.loc[t].reindex(mem),
                          "mc": mcg.loc[t].reindex(mem), "sec": sector.reindex(mem).values})
        d = d.dropna(subset=["sig", "fwd", "mc"])
        if len(d) < MIN_NAMES:
            continue
        # 섹터중립: 섹터 내 demean (ls_book.meta_sn과 1:1)
        d["sig_sn"] = d["sig"] - d.groupby("sec")["sig"].transform("mean")
        rk = d["sig_sn"].rank(pct=True)
        L = d[rk >= 1 - quintile].copy()               # 높은 sig = loser = LONG
        S = d[rk <= quintile].copy()                   # 낮은 sig = winner = SHORT
        # equal-weight dollar-neutral (per-name 상한 없음 — 순수 ST-reversal 정의)
        wL = pd.Series(1.0 / len(L), index=L.index)
        wS = pd.Series(1.0 / len(S), index=S.index)
        gross = (wL * L["fwd"]).sum() - (wS * S["fwd"]).sum()
        # turnover(one-way, 멤버 집합 기준 — cost.turnover_oneway 동결) 양다리
        iL = set(L.index); iS = set(S.index)
        toL = C.turnover_oneway(iL, prevL); toS = C.turnover_oneway(iS, prevS)
        cL = C.tier_marketcap_bps(L["mc"]).mean() / C.BPS
        cS = C.tier_marketcap_bps(S["mc"]).mean() / C.BPS
        tcost = (toL * 2 * cL + toS * 2 * cS) * cost_mult   # round-trip(×2) 양다리, stress = ×mult
        bcost = (BORROW_ANN / 12) * cost_mult               # 숏 borrow 월 (gross가 dollar-neutral=숏 1.0)
        net = gross - tcost - bcost
        recs.append(dict(t=t, gross=gross, net=net, to_avg=(toL + toS) / 2, n=len(d)))
        prevL, prevS = iL, iS
    R = pd.DataFrame(recs).set_index("t")
    R.index = pd.to_datetime(R.index)
    return R

def main():
    print("=" * 96)
    print("PRAMANA v3 — CANDIDATE sleeve3: short-term (1-month) cross-sectional REVERSAL  (top-1500 PIT)")
    print("=" * 96)
    print("PRE-REGISTERED KILLS (결과 前): net Sharpe≤0 FAIL · |corr|>0.5 to eq OR ov → 분산 아님 ·")
    print("                              2x cost서 사망 FAIL · turnover 과해 net 음수 FAIL.")
    print("정의: LONG 하위분위(losers)·SHORT 상위분위(winners)·섹터중립·equal-weight·dollar-neutral · fwd=다음달.")

    R1 = build_reversal(quintile=QUINTILE, cost_mult=1.0)
    to_ann = R1["to_avg"].mean() * 12
    print(f"\n기간 {R1.index.min().date()}~{R1.index.max().date()} · {len(R1)}개월 · 평균 멤버 {int(R1['n'].mean())} · 분위={QUINTILE:.0%}")
    print(f"비용: tier_marketcap_bps round-trip(양다리) + 숏 borrow {BORROW_ANN*100:.1f}%/yr · turnover ≈ {to_ann*100:.0f}%/yr (one-way, 양다리 평균)")

    print("\n[성과] (quintile)")
    pg = line("gross (무비용)", R1["gross"])
    pn = line("net (1x cost)", R1["net"])
    R2 = build_reversal(quintile=QUINTILE, cost_mult=2.0)
    p2 = line("net (2x cost — stress)", R2["net"])

    # decile 참고(정의는 quintile이 primary)
    Rd1 = build_reversal(quintile=0.1, cost_mult=1.0)
    Rd2 = build_reversal(quintile=0.1, cost_mult=2.0)
    to_ann_d = Rd1["to_avg"].mean() * 12
    print(f"\n[성과] (decile 참고; turnover ≈ {to_ann_d*100:.0f}%/yr)")
    line("decile net (1x cost)", Rd1["net"])
    line("decile net (2x cost)", Rd2["net"])

    # ── 상관: 기존 2 sleeve (eq, ov) ───────────────────────────────────────────
    cb = pd.read_csv(os.path.join(data.PHASE1A, "outputs", "engine", "combined_book_nav.csv"), index_col=0, parse_dates=True)
    rv = R1["net"].rename("rv")
    j = pd.concat([cb["eq"].rename("eq"), cb["ov"].rename("ov"), rv], axis=1, sort=True).dropna()
    ce = j["eq"].corr(j["rv"]); co = j["ov"].corr(j["rv"]); ceo = j["eq"].corr(j["ov"])
    print(f"\n[상관] 공통 {len(j)}개월 · corr(rev,eq)={ce:+.3f} · corr(rev,ov)={co:+.3f}  (기존 corr(eq,ov)={ceo:+.3f})")

    # ── 3-sleeve equal-weight combo vs 2-sleeve combo ──────────────────────────
    combo2 = 0.5 * j["eq"] + 0.5 * j["ov"]
    combo3 = (j["eq"] + j["ov"] + j["rv"]) / 3.0
    print("\n[combo — equal-weight, 비용후, 무레버] 분산 효과 검증")
    p2c = line("2-sleeve (eq+ov, 50/50)", combo2)
    p3c = line("3-sleeve (eq+ov+rev, 1/3)", combo3)
    delta = p3c["sharpe"] - p2c["sharpe"]
    print(f"  → 3-sleeve Sharpe {p3c['sharpe']:+.2f} vs 2-sleeve {p2c['sharpe']:+.2f}  (Δ={delta:+.2f})  {'도움' if delta>0 else '도움 안 됨'}")

    # ── 사전등록 kill 대조 (결과 → verdict) ────────────────────────────────────
    kills = []
    if not (pn["sharpe"] > 0):                       kills.append(f"net Sharpe≤0 ({pn['sharpe']:+.2f})")
    if (abs(ce) > 0.5) or (abs(co) > 0.5):           kills.append(f"|corr|>0.5 (eq={ce:+.2f}/ov={co:+.2f}) → 분산 아님")
    if not (p2["sharpe"] > 0):                       kills.append(f"2x cost서 사망 (Sharpe {p2['sharpe']:+.2f})")
    if perf(R1["net"])["cagr"] <= 0:                 kills.append("turnover 과해 net 음수")
    verdict = "FAIL" if kills else "SURVIVE"
    print("\n" + "=" * 96)
    print(f"VERDICT: {verdict}" + (f"  — kills: {' ; '.join(kills)}" if kills else "  — 사전등록 kill 전부 통과"))
    print(f"가상 ₩100M(net 1x, 무레버): 1억 → ₩{CAP_KRW*pn['fin']/1e8:.2f}억 ({(pn['fin']-1)*100:+.0f}%, {len(R1)//12}년)")
    print("=" * 96)

    # ── 산출물 저장 ────────────────────────────────────────────────────────────
    out = os.path.join(data.PHASE1A, "outputs", "engine", "sleeve3_reversal_nav.csv")
    save = pd.DataFrame({"gross": R1["gross"], "net": R1["net"], "net_2x": R2["net"], "to_avg": R1["to_avg"]})
    save.to_csv(out)
    print(f"\n  → {out}  · ⚠️ paper(가상)·단일 백테스트·no live")
    return dict(verdict=verdict, kills=kills, net=pn, gross=pg, net2x=p2,
                corr_eq=ce, corr_ov=co, corr_eo=ceo, combo2=p2c, combo3=p3c,
                to_ann=to_ann, n_months=len(R1), n_common=len(j),
                start=str(R1.index.min().date()), end=str(R1.index.max().date()))

if __name__ == "__main__":
    main()

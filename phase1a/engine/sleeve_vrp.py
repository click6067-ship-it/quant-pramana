#!/usr/bin/env python3
"""PRAMANA v3 — CANDIDATE sleeve_vrp: VOL-RISK-PREMIUM (short-vol carry) with HARD CRASH KILL.
질문: VIX-futures contango(롤다운 carry)를 SHORT vol ETF로 수확하되, *deterministic 크래시 킬*이
      Feb-2018(XIV -96%)·Mar-2020 blowup으로부터 sleeve를 살리는가? 기존 book에 소량 더하면
      tail 폭발 없이 수익을 올리는가?

정의 (ONE · 튜닝/윈도우헌팅 0 · kill 결과 前 박음):
  포지션  : SHORT UVXY(1.5x VIX short-term futures ETF) → daily 포지션수익 = -1 × UVXY closeadj 일수익.
            (UVXY가 데이터 전구간(2016~) 존재 → Feb-2018 포함; VXX는 2018-01 시작이라 robustness용 보조.)
            월 1회 마크(daily 복리로 누적 후 월수익 집계 — kill·tail은 *일* 해상도라야 의미 有).
  크래시킬 (mandatory·deterministic, 3-트리거 OR, 종가 평가 → *다음 바* 적용=no look-ahead):
            (1) SPY 20d 실현변동성 ≥ 25%/yr          (변동성 레짐)
            (2) SPY < 50d MA  OR  SPY < 200d MA        (추세 붕괴)
            (3) VIX-proxy 급등: UVXY 1일 ≥ +20%        (vol 스파이크 — 데이터 내 VIX-ST proxy)
            ANY 트리거 ON → target = FLAT(0). signal at close(t) → position effective (t+1).
  비용    : ETF tier(UVXY 초유동 → top-tier 5bp one-way, 동결 cost 컨벤션) on turnover(포지션 변화)
            + 숏 borrow(UVXY shorting): modest(유동적)이나 실재 — 연 5%/yr 가정, daily accrual on short notional.
사전등록 KILL (결과 前 박음):
  net Sharpe ≤ 0 → FAIL ·
  단일 worst month < -25% (tail이 크래시킬로 제어 안 됨) → FAIL (ruin risk) ·
  2x cost서 사망(net Sharpe ≤ 0) → FAIL ·
  max drawdown < -40% → FAIL.
데이터(캐시 only·API 0): SFP_FUNDS(UVXY/VXX/SPY closeadj) · combined_book_nav(eq/ov).
사용: ./.venv/bin/python engine/sleeve_vrp.py · ⚠️ paper(가상)·단일 백테스트·no live."""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import data  # noqa: F401  (house convention; data root = data.PHASE1A)

# ── 동결 파라미터 (ONE 정의 — 결과 보고 바꾸지 않음) ─────────────────────────
RV_THRESH   = 0.25      # SPY 20d 실현변동성 킬 임계 (prompt 예시값 25%/yr)
RV_WIN      = 20        # 실현변동성 윈도우(거래일)
MA_FAST     = 50        # 추세 MA (fast)
MA_SLOW     = 200       # 추세 MA (slow)
SPIKE_THR   = 0.20      # VIX-proxy 급등: UVXY 1일 ≥ +20% → 킬
ETF_BPS     = 5.0       # UVXY 초유동 ETF one-way 비용(bp) — 동결 top-tier(cost.tier_marketcap_bps 상위33%=5bp)
BORROW_ANN  = 0.05      # UVXY 숏 borrow 연 5%/yr (modest·유동적이나 실재; stress 대상)
TRADING_DAYS= 252
ANN_M       = 12        # 월 메트릭 연율화
CAP_KRW     = 100_000_000


# ── 메트릭 (combined_book.perf / sleeve3.perf 와 1:1 동결, 월수익 기준) ──────
def perf(r):
    m = ANN_M
    sh = r.mean() / r.std() * np.sqrt(m) if r.std() > 0 else np.nan
    nav = (1 + r).cumprod(); dd = (nav / nav.cummax() - 1).min()
    cagr = (1 + r).prod() ** (m / len(r)) - 1 if len(r) else np.nan
    rec = r[r.index >= "2021-01-01"]
    rs = rec.mean() / rec.std() * np.sqrt(m) if rec.std() > 0 else np.nan
    return dict(sharpe=sh, cagr=cagr, maxdd=dd, fin=nav.iloc[-1] if len(r) else np.nan,
                rec_sharpe=rs, vol=r.std() * np.sqrt(m), worst_month=r.min())


def line(lbl, r):
    p = perf(r)
    print(f"  {lbl:32s} Sharpe={p['sharpe']:+.2f} CAGR={p['cagr']*100:+6.2f}% vol={p['vol']*100:4.1f}% "
          f"maxDD={p['maxdd']*100:6.1f}% worstM={p['worst_month']*100:6.1f}% | 2021-26 Sh={p['rec_sharpe']:+.2f}")
    return p


# ── 데이터 로드 (캐시 only) ─────────────────────────────────────────────────
def load_px(ticker):
    df = data.load("SFP_FUNDS", usecols=["ticker", "date", "closeadj"])
    s = df[df.ticker == ticker].set_index("date")["closeadj"].sort_index()
    return s[~s.index.duplicated(keep="last")]


# ── 크래시 킬 신호 (종가 평가) ───────────────────────────────────────────────
def crash_kill_signal(spy, vol_ticker_ret):
    """3-트리거 OR 크래시 킬. 모두 *종가 t* 정보만 사용. 반환: bool Series(True=KILL=FLAT).
    spy            : SPY closeadj (일).
    vol_ticker_ret : SHORT 대상 ETF(UVXY)의 일수익(스파이크 트리거용)."""
    sr = spy.pct_change()
    rv20 = sr.rolling(RV_WIN).std() * np.sqrt(TRADING_DAYS)     # 20d 실현변동성(연율)
    ma_f = spy.rolling(MA_FAST).mean()
    ma_s = spy.rolling(MA_SLOW).mean()
    k_vol   = rv20 >= RV_THRESH                                  # (1) 변동성 레짐
    k_trend = (spy < ma_f) | (spy < ma_s)                       # (2) 추세 붕괴
    k_spike = vol_ticker_ret >= SPIKE_THR                       # (3) VIX-proxy 급등
    kill = (k_vol | k_trend | k_spike).fillna(True)             # 워밍업(MA 미정)=보수적 FLAT
    return kill, dict(k_vol=k_vol, k_trend=k_trend, k_spike=k_spike, rv20=rv20)


# ── 백테스트: short-vol carry + 크래시 킬, next-bar exec, daily→monthly ───────
def run_vrp(short_ticker="UVXY", cost_mult=1.0, use_kill=True):
    """반환: dict(daily=일프레임, monthly=월net수익 Series, kill=bool Series, ...)."""
    px = load_px(short_ticker)
    spy = load_px("SPY")
    idx = px.index.intersection(spy.index)
    px = px.reindex(idx); spy = spy.reindex(idx)

    etf_ret = px.pct_change()                                   # UVXY 일수익
    pos_ret_raw = -etf_ret                                      # SHORT: 포지션 일수익 = -UVXY

    # 크래시 킬 신호(종가 t) → target position(t): 0=FLAT, 1=SHORT 풀
    if use_kill:
        kill, comp = crash_kill_signal(spy, etf_ret)
        target = np.where(kill, 0.0, 1.0)                       # 1.0 = full short notional
    else:
        kill = pd.Series(False, index=idx); comp = {}
        target = np.ones(len(idx))
    target = pd.Series(target, index=idx)

    # NEXT-BAR EXECUTION: 종가 t에 신호 → position effective t+1 (look-ahead 0)
    position = target.shift(1).fillna(0.0)                      # 첫날은 무포지션

    # gross 일수익 = position(t) × pos_ret_raw(t)
    gross_d = position * pos_ret_raw

    # 비용: (a) turnover — position 변화 시 ETF 비용(one-way bp). 진입/청산 모두 |Δposition|.
    dpos = position.diff().abs().fillna(position.abs())
    tcost_d = dpos * (ETF_BPS / 1e4) * cost_mult
    # (b) borrow — 숏 notional(=position) 보유 일수만큼 daily accrual.
    bcost_d = position.abs() * (BORROW_ANN / TRADING_DAYS) * cost_mult
    net_d = gross_d - tcost_d - bcost_d

    daily = pd.DataFrame({"etf_ret": etf_ret, "pos_ret_raw": pos_ret_raw,
                          "position": position, "kill": kill.astype(float),
                          "gross": gross_d, "tcost": tcost_d, "bcost": bcost_d, "net": net_d})
    daily = daily.dropna(subset=["etf_ret"])

    # daily → monthly (복리). 월수익 = ∏(1+net_d)-1 (월말 인덱스, eq/ov와 정렬용).
    def to_monthly(col):
        return (1 + daily[col]).resample("ME").prod() - 1
    monthly_net = to_monthly("net")
    monthly_gross = to_monthly("gross")
    return dict(daily=daily, monthly_net=monthly_net, monthly_gross=monthly_gross,
                kill=kill, comp=comp, position=position, etf_ret=etf_ret)


# ── 크래시 킬 효과 진단: 특정 윈도우(Feb-2018/Mar-2020) kill-on vs kill-off ──
def window_breakdown(short_ticker="UVXY"):
    on = run_vrp(short_ticker, use_kill=True)["daily"]
    off = run_vrp(short_ticker, use_kill=False)["daily"]
    rows = []
    for label, lo, hi in [("Feb-2018 (XIV blowup)", "2018-01-29", "2018-02-28"),
                          ("Mar-2020 (COVID)", "2020-02-20", "2020-03-31")]:
        won = (1 + on["net"][lo:hi]).prod() - 1
        woff = (1 + off["net"][lo:hi]).prod() - 1
        # kill이 처음 발동(종가) → flat 시작일
        ks = on["kill"][lo:hi]; firstfire = ks[ks > 0].index[0].date() if (ks > 0).any() else None
        rows.append(dict(window=label, lo=lo, hi=hi, ret_withkill=won, ret_nokill=woff,
                         first_kill_fire=firstfire))
    return pd.DataFrame(rows)


def main():
    print("=" * 104)
    print("PRAMANA v3 — CANDIDATE sleeve_vrp: VOL-RISK-PREMIUM (short-vol carry) + HARD CRASH KILL")
    print("=" * 104)
    print("PRE-REGISTERED KILLS (결과 前 박음):")
    print("  · net Sharpe ≤ 0 → FAIL")
    print("  · 단일 worst month < -25% (tail이 크래시킬로 제어 안 됨) → FAIL (ruin)")
    print("  · 2x cost서 사망(net Sharpe ≤ 0) → FAIL")
    print("  · max drawdown < -40% → FAIL")
    print("정의: SHORT UVXY (-1×일수익) · 월마크(일복리) · 크래시킬=[SPY rv20≥25% OR SPY<MA50/200 OR UVXY일≥+20%]")
    print(f"      → FLAT · next-bar exec(종가→다음바, look-ahead 0) · 비용 ETF {ETF_BPS:.0f}bp + borrow {BORROW_ANN*100:.0f}%/yr.")

    # ── PRIMARY: UVXY, kill ON, 1x cost ────────────────────────────────────────
    R = run_vrp("UVXY", cost_mult=1.0, use_kill=True)
    mnet = R["monthly_net"]; mgross = R["monthly_gross"]
    daily = R["daily"]
    n_months = len(mnet)
    kill_frac = daily["kill"].mean()
    flat_frac = (daily["position"].abs() < 1e-9).mean()
    print(f"\n기간 {daily.index.min().date()}~{daily.index.max().date()} · {len(daily)}거래일 · {n_months}개월(UVXY, 전구간)")
    print(f"크래시킬: 종가신호 ON {kill_frac*100:.1f}% 일 · 실제 FLAT(next-bar) {flat_frac*100:.1f}% 일 · "
          f"SHORT 노출 {(1-flat_frac)*100:.1f}% 일")

    print("\n[성과] (UVXY short-vol carry · 월수익)")
    pg = line("gross (무비용·킬有)", mgross)
    pn = line("net (1x cost·킬有)  [PRIMARY]", mnet)
    R2 = run_vrp("UVXY", cost_mult=2.0, use_kill=True)
    p2 = line("net (2x cost·킬有·stress)", R2["monthly_net"])
    Rnok = run_vrp("UVXY", cost_mult=1.0, use_kill=False)
    pnok = line("net (1x cost·킬 OFF=naked)", Rnok["monthly_net"])

    # ── 크래시 킬 효과: Feb-2018 / Mar-2020 (THE 핵심 deliverable) ───────────────
    print("\n[크래시 킬 효과 — THE deliverable] Feb-2018(XIV -96%)·Mar-2020 윈도우 손익: 킬有 vs 킬無")
    wb = window_breakdown("UVXY")
    for _, r in wb.iterrows():
        print(f"  {r['window']:24s} 킬有={r['ret_withkill']*100:+7.1f}%  vs  킬無(naked)={r['ret_nokill']*100:+8.1f}%  "
              f"(킬 첫 발동 종가: {r['first_kill_fire']})")
    naked_worstm = perf(Rnok["monthly_net"])["worst_month"]
    print(f"  → naked(킬無) worst month = {naked_worstm*100:+.1f}%  vs  킬有 worst month = {pn['worst_month']*100:+.1f}%")

    # ── 월별 worst & 연도별 (2018/2020 명시) ────────────────────────────────────
    print("\n[worst months — 킬有 net] tail 점검 (사전등록: < -25% 면 FAIL)")
    worst5 = mnet.nsmallest(5)
    for d, v in worst5.items():
        print(f"  {d.date()}  {v*100:+7.1f}%")
    print("\n[연도별 net 수익 — 킬有] (2018·2020 핵심)")
    yr = (1 + mnet).groupby(mnet.index.year).prod() - 1
    print("  " + "  ".join(f"{y}:{v*100:+6.1f}%" for y, v in yr.items()))

    # ── 상관: 기존 2 sleeve (eq, ov) ───────────────────────────────────────────
    cb = pd.read_csv(os.path.join(data.PHASE1A, "outputs", "engine", "combined_book_nav.csv"),
                     index_col=0, parse_dates=True)
    vr = mnet.rename("vr")
    # 월말 인덱스 정렬(eq/ov는 월말 영업일, vr은 ME 캘린더말) → 월 period로 정렬
    cb_p = cb.copy(); cb_p.index = cb_p.index.to_period("M")
    vr_p = vr.copy(); vr_p.index = vr_p.index.to_period("M")
    j = pd.concat([cb_p["eq"].rename("eq"), cb_p["ov"].rename("ov"), vr_p], axis=1).dropna()
    ce = j["eq"].corr(j["vr"]); co = j["ov"].corr(j["vr"]); ceo = j["eq"].corr(j["ov"])
    print(f"\n[상관] 공통 {len(j)}개월 · corr(vrp,eq)={ce:+.3f} · corr(vrp,ov)={co:+.3f}  (기존 corr(eq,ov)={ceo:+.3f})")

    # ── 기존 book(eq+ov 50/50)에 소량(10%) VRP sleeve 추가 → tail 폭발 없이 수익↑? ─
    base = 0.5 * j["eq"] + 0.5 * j["ov"]
    print("\n[combo — 기존 2-sleeve(50/50)에 VRP 소량 추가, 비용후·무레버] tail 폭발 없이 수익 ↑?")
    pb = line("2-sleeve base (eq+ov 50/50)", base)
    combo_results = {}
    for w in (0.05, 0.10, 0.20):
        c = (1 - w) * base + w * j["vr"]
        combo_results[w] = line(f"+VRP {int(w*100)}% (eq+ov {int((1-w)*100)}%)", c)

    # ── 사전등록 kill 대조 (결과 → verdict) ────────────────────────────────────
    kills = []
    if not (pn["sharpe"] > 0):
        kills.append(f"net Sharpe≤0 (Sharpe {pn['sharpe']:+.2f})")
    if pn["worst_month"] < -0.25:
        kills.append(f"worst month < -25% (실제 {pn['worst_month']*100:+.1f}% → tail 미제어/ruin)")
    if not (p2["sharpe"] > 0):
        kills.append(f"2x cost서 사망 (Sharpe {p2['sharpe']:+.2f})")
    if pn["maxdd"] < -0.40:
        kills.append(f"maxDD < -40% (실제 {pn['maxdd']*100:+.1f}%)")
    verdict = "FAIL" if kills else "SURVIVE"

    print("\n" + "=" * 104)
    print(f"VERDICT: {verdict}" + (f"  — kills: {' ; '.join(kills)}" if kills else "  — 사전등록 kill 전부 통과"))
    # 크래시킬이 worst-month를 -25% 위로 잡았나? (naked 대비)
    saved = (naked_worstm < -0.25) and (pn["worst_month"] >= -0.25)
    print(f"크래시킬 효과: naked worst month {naked_worstm*100:+.1f}% → 킬有 {pn['worst_month']*100:+.1f}% · "
          f"{'킬이 ruin tail을 -25% 위로 잡음 ✅' if saved else ('킬해도 worst<-25% — 살리지 못함 ❌' if pn['worst_month']<-0.25 else 'naked도 -25% 안 넘김(킬 효과는 maxDD/2020서)')}")
    print(f"가상 ₩100M(net 1x·킬有·무레버): 1억 → ₩{CAP_KRW*pn['fin']/1e8:.2f}억 ({(pn['fin']-1)*100:+.0f}%, {n_months//12}년)")
    print("=" * 104)

    # ── robustness: VXX(2018-01~)로도 동일 정의 재실행 (보조) ────────────────────
    print("\n[robustness — VXX(2018-01~) 동일 정의, 보조]")
    try:
        RV = run_vrp("VXX", cost_mult=1.0, use_kill=True)
        line("VXX net (1x·킬有)", RV["monthly_net"])
    except Exception as e:
        print(f"  VXX skip: {e}")

    # ── 산출물 저장 (월 net/gross/2x + 일 kill·position) ────────────────────────
    out = os.path.join(data.PHASE1A, "outputs", "engine", "sleeve_vrp_nav.csv")
    save = pd.DataFrame({"net": mnet, "gross": mgross, "net_2x": R2["monthly_net"],
                         "net_nokill": Rnok["monthly_net"]})
    save.to_csv(out)
    print(f"\n  → {out}  · ⚠️ paper(가상)·단일 백테스트·no live")

    return dict(verdict=verdict, kills=kills, n_months=n_months, n_common=len(j),
                start=str(daily.index.min().date()), end=str(daily.index.max().date()),
                kill_frac=kill_frac, flat_frac=flat_frac,
                net=pn, gross=pg, net2x=p2, naked=pnok, naked_worstm=naked_worstm,
                corr_eq=ce, corr_ov=co, corr_eo=ceo,
                window=wb, base=pb, combo=combo_results, yearly=yr, worst5=worst5)


if __name__ == "__main__":
    main()

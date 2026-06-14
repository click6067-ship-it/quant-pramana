#!/usr/bin/env python3
"""PRAMANA A2 — extended benchmark panel (spec: 04_BENCHMARKS_AND_METRICS.md).
A2 = QQQ/TQQQ 성장 베타를 의식적으로 산 book → 단순 QQQ만 이겨선 부족. naive/synthetic/DCA/V7 다 같이 돌려 부가가치 분리.
모든 시계열 = a2_data.benchmarks() 일별 closeadj(2016~2026·캐시·구독중 완료). buy-and-hold 별도 표기 없으면 기본.
★ 백테스트(2016~·강세장 편향·닷컴/2008 crash 없음). live ₩1억 ledger 아님(a2_live_runner 소관). PAPER·자본권한 0·검증된 알파 아님.
산출: outputs/a2_live/benchmark_panel.csv · outputs/a2_benchmark_dashboard.html · reports/A2_monthly_benchmark_review.md
사용: .venv/bin/python -u engine/a2_benchmarks.py"""
import os, sys, io, base64, datetime as dt
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a2_data
from kfont import set_korean_font; set_korean_font()

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
A2 = os.path.join(ROOT, "outputs", "a2_live"); os.makedirs(A2, exist_ok=True)
CSV = os.path.join(A2, "benchmark_panel.csv")
DASH = os.path.join(ROOT, "outputs", "a2_benchmark_dashboard.html")
REPORT = os.path.join(ROOT, "reports", "A2_monthly_benchmark_review.md")   # phase1a/reports (기존 리포트 위치)
FIN_DRAG = 0.4 * 0.05 / 252   # synthetic QQQ 1.4x financing drag PROXY = 0.4 차입분 × 5%/yr 금리 가정 (라벨=가정·실제 펀딩비 아님)
DD_DCA_THRESH = 0.15          # drawdown DCA: 직전 고점 대비 -15% 이상이면 그 달 추가 매수

# ── 시계열 → metric ──
def metrics(nav, qqq_nav=None):
    """nav = 누적 NAV Series(시작=1.0). 수익/연율/MDD/회복일/위험비율/vs-QQQ 최대열위."""
    nav = nav.dropna()
    if len(nav) < 2: return None
    ret = nav.iloc[-1] / nav.iloc[0] - 1
    yrs = (nav.index[-1] - nav.index[0]).days / 365.25
    ann = (nav.iloc[-1] / nav.iloc[0]) ** (1 / yrs) - 1 if yrs > 0 else np.nan
    roll_max = nav.cummax(); dd = nav / roll_max - 1.0; mdd = float(dd.min())
    # recovery: 최대낙폭 저점 → 그 직전 peak 회복까지 거래일 수(미회복이면 NaN)
    trough_i = int(dd.values.argmin()); peak_val = float(roll_max.iloc[trough_i]); rec = np.nan
    post = nav.iloc[trough_i:]; recov = post[post >= peak_val]
    if len(recov): rec = int(nav.index.get_loc(recov.index[0]) - trough_i)
    dret = nav.pct_change().dropna()
    sharpe = float(dret.mean() / dret.std() * np.sqrt(252)) if dret.std() > 0 else np.nan
    risk_ratio = float(ann / abs(mdd)) if mdd < 0 else np.nan   # ann_return / |MDD| (Calmar류 단순 위험비율)
    # max underperformance vs QQQ = (this rel-to-start) − (qqq rel-to-start) 의 최저값
    max_under = np.nan
    if qqq_nav is not None:
        q = qqq_nav.dropna().reindex(nav.index).ffill()
        rel = (nav / nav.iloc[0]) - (q / q.iloc[0]); max_under = float(rel.min())
    return {"total_return": float(ret), "annualized_return": float(ann), "MDD": mdd,
            "recovery_days": rec, "risk_ratio": risk_ratio, "sharpe": sharpe,
            "max_underperformance_vs_QQQ": max_under}

# ── 벤치마크 NAV 구성기 (전부 시작=1.0·일별·next-bar 비해당: buy&hold/일별리밸은 same-bar leakage 없음) ──
def bh(px):                                  # buy & hold
    return (px.dropna() / px.dropna().iloc[0])

def daily_rebal(rets, weights):              # 매일 목표비중 리밸런스(weights dict ticker→w, 나머지=cash 0수익)
    idx = rets.index; nav = pd.Series(1.0, index=idx); cur = 1.0
    blend = sum(rets[t].fillna(0) * w for t, w in weights.items())   # 일별 리밸=가중 일수익 합
    return (1 + blend).cumprod()

def synth_levered(qqq_ret, lev, drag):       # synthetic QQQ lev배 = qret*lev - drag(일별 금융비용 proxy)
    return (1 + qqq_ret.fillna(0) * lev - drag).cumprod()

def monthly_dca(px):                         # 매월초 $1 적립. ★ money-weighted: NAV(t)=시장가치/누적투입($) = "$1당 가치"(MWR 기준).
    px = px.dropna(); buy_dates = set(px.groupby(px.index.to_period("M")).head(1).index)
    invested = 0.0; shares = 0.0; nav = pd.Series(index=px.index, dtype=float)
    for d in px.index:
        if d in buy_dates: shares += 1.0 / px.loc[d]; invested += 1.0
        nav.loc[d] = (shares * px.loc[d] / invested) if invested > 0 else np.nan
    return nav.dropna()                      # 시작 1.0·끝=최종가치/총투입(=MWR 배수·buy&hold와 직접 비교 가능). 매수일 미세 sawtooth(투입 희석)는 MDD에 보수적.

def drawdown_dca(px, thresh):                # 매월초 $1 + 직전고점 대비 -thresh 이상이면 $1 추가. money-weighted(value/투입$).
    px = px.dropna(); month_first = set(px.groupby(px.index.to_period("M")).head(1).index)
    roll_max = px.cummax(); dd = px / roll_max - 1.0
    invested = 0.0; shares = 0.0; nav = pd.Series(index=px.index, dtype=float)
    for d in px.index:
        if d in month_first:
            usd = 1.0 + (1.0 if dd.loc[d] <= -thresh else 0.0)    # 낙폭 깊으면 $2
            shares += usd / px.loc[d]; invested += usd
        nav.loc[d] = (shares * px.loc[d] / invested) if invested > 0 else np.nan
    return nav.dropna()

# ── V7 4-sleeve survival core (DBMF/GLD/IEF=yfinance·실패 시 graceful skip) ──
def build_v7(spy_px, qqq_px):
    try:
        import yfinance as yf
        ext = yf.download(["DBMF", "GLD", "IEF"], start="2016-01-01", interval="1d",
                          auto_adjust=True, progress=False)
        ext = ext["Close"] if hasattr(ext.columns, "levels") else ext
        ext.index = pd.to_datetime(ext.index)
        if not all(t in ext.columns for t in ["DBMF", "GLD", "IEF"]): return None, "V7 SKIP: yfinance DBMF/GLD/IEF 컬럼 누락"
        ext = ext.dropna()
        if len(ext) < 252: return None, "V7 SKIP: DBMF/GLD/IEF 공통 데이터 부족"
        # 공통 인덱스(SPY/QQQ는 Sharadar tz-naive)
        spy = spy_px.copy(); qqq = qqq_px.copy()
        for s in (spy, qqq): s.index = pd.to_datetime(s.index)
        common = ext.index.intersection(spy.index).intersection(qqq.index)
        if len(common) < 252: return None, "V7 SKIP: Sharadar∩yfinance 공통 거래일 부족"
        ext = ext.reindex(common); spy = spy.reindex(common); qqq = qqq.reindex(common)
        r = pd.DataFrame({"SPY": spy.pct_change(), "QQQ": qqq.pct_change(),
                          "DBMF": ext["DBMF"].pct_change(), "GLD": ext["GLD"].pct_change(),
                          "IEF": ext["IEF"].pct_change()}).fillna(0)
        # Eq50(SPY25/QQQ25) + DBMF25 + GLD15 + IEF10 · 1.0x · 일별 리밸
        blend = .25 * r["SPY"] + .25 * r["QQQ"] + .25 * r["DBMF"] + .15 * r["GLD"] + .10 * r["IEF"]
        nav = (1 + blend).cumprod()
        note = (f"V7 OK: DBMF/GLD/IEF=yfinance(auto_adjust) · 공통 {common.min().date()}~{common.max().date()} "
                f"({len(common)}td) · DBMF 상장 2019-05 → 2016-19 미커버(부분기간 caveat)")
        return nav, note
    except Exception as e:
        return None, f"V7 SKIP: yfinance 실패 ({type(e).__name__}: {str(e)[:120]})"

# ── periods ──
PERIODS = [("3년", 756), ("12개월", 252), ("6개월", 126), ("3개월", 63), ("inception-to-date", None)]

def slice_period(nav, n):
    nav = nav.dropna()
    if n is None: return nav
    return nav.iloc[-min(n, len(nav)):]

def main():
    b = a2_data.benchmarks()
    qqq_px, tqqq_px, spy_px = b["QQQ"], b["TQQQ"], b["SPY"]
    qret = qqq_px.pct_change(); tret = tqqq_px.pct_change(); sret = spy_px.pct_change()
    rets = pd.DataFrame({"QQQ": qret, "TQQQ": tret, "SPY": sret})
    full_idx = b.index; data_hi = full_idx.max().date(); data_lo = full_idx.min().date()

    NAVS = {}
    NAVS["SPY"] = bh(spy_px)
    NAVS["QQQ"] = bh(qqq_px)
    NAVS["TQQQ"] = bh(tqqq_px)
    NAVS["Naive Beta (QQQ35/TQQQ35/Cash30)"] = daily_rebal(rets, {"QQQ": .35, "TQQQ": .35})
    NAVS["Synthetic QQQ 1.4x (proxy)"] = synth_levered(qret, 1.4, FIN_DRAG)
    NAVS["TQQQ monthly DCA"] = monthly_dca(tqqq_px)
    NAVS["TQQQ drawdown DCA (-15%)"] = drawdown_dca(tqqq_px, DD_DCA_THRESH)
    # A2 base fixed = QQQ35/TQQQ35/Cash30 일별 리밸 (backtest fixed book). 동적 allocator OFF/REJECT → A2 dynamic = fixed와 동일.
    NAVS["A2 base fixed (=A2 dynamic·동적 OFF)"] = daily_rebal(rets, {"QQQ": .35, "TQQQ": .35})
    v7_nav, v7_note = build_v7(spy_px, qqq_px)
    if v7_nav is not None: NAVS["V7 survival core (Eq50/DBMF25/GLD15/IEF10)"] = v7_nav
    print(v7_note)

    qqq_full = NAVS["QQQ"]
    rows = []
    for name, nav in NAVS.items():
        for plabel, n in PERIODS:
            seg = slice_period(nav, n)
            qseg = slice_period(qqq_full.reindex(nav.dropna().index).ffill(), n)
            m = metrics(seg, qseg)
            if m is None: continue
            rows.append({"benchmark": name, "period": plabel, **m})
    panel = pd.DataFrame(rows)
    # 라운딩(가독)
    for c in ["total_return", "annualized_return", "MDD", "risk_ratio", "sharpe", "max_underperformance_vs_QQQ"]:
        panel[c] = panel[c].astype(float).round(4)
    panel.to_csv(CSV, index=False)
    print(f"✅ panel.csv: {len(panel)}행 · {panel['benchmark'].nunique()}벤치 × {len(PERIODS)}기간 → {CSV}")

    # ── 대시보드 ──
    plt.style.use("dark_background")
    plt.rcParams.update({"axes.facecolor": "#0d1326", "figure.facecolor": "#0d1326", "grid.alpha": .15, "font.size": 9})
    fig = plt.figure(figsize=(11, 4.4))
    COL = {"SPY": "#f59e0b", "QQQ": "#a78bfa", "TQQQ": "#ec4899",
           "Naive Beta (QQQ35/TQQQ35/Cash30)": "#22d3ee", "Synthetic QQQ 1.4x (proxy)": "#60a5fa",
           "TQQQ monthly DCA": "#f472b6", "TQQQ drawdown DCA (-15%)": "#fb7185",
           "A2 base fixed (=A2 dynamic·동적 OFF)": "#34d399",
           "V7 survival core (Eq50/DBMF25/GLD15/IEF10)": "#94a3b8"}
    for name, nav in NAVS.items():
        nav = nav.dropna()
        plt.plot(nav.index, nav / nav.iloc[0],
                 label=name, lw=2.4 if name.startswith("A2") else 1.4,
                 color=COL.get(name, "#cbd5e1"),
                 ls="-" if (name.startswith("A2") or name.startswith("Naive")) else "--")
    plt.yscale("log"); plt.legend(framealpha=.2, fontsize=7, ncol=2)
    plt.title("PRAMANA A2 벤치마크 패널 — 누적수익(시작=1.0·log) · 백테스트 2016~", color="#e5e7eb")
    plt.ylabel("누적 배수(log)")
    buf = io.BytesIO(); fig.savefig(buf, format="png", dpi=95, bbox_inches="tight", facecolor="#0d1326")
    plt.close(fig); chart = base64.b64encode(buf.getvalue()).decode()

    def pct(x): return f"{x*100:+.1f}%" if pd.notna(x) else "—"
    def rd(x): return f"{int(x)}td" if pd.notna(x) else "미회복"
    def num(x): return f"{x:.2f}" if pd.notna(x) else "—"
    # 표: 기간별로 그룹
    tabs = ""
    for plabel, _ in PERIODS:
        sub = panel[panel["period"] == plabel]
        body = "".join(
            f'<tr><td>{r.benchmark}</td><td class={"pos" if r.total_return>=0 else "neg"}>{pct(r.total_return)}</td>'
            f'<td>{pct(r.annualized_return)}</td><td class=neg>{pct(r.MDD)}</td><td>{rd(r.recovery_days)}</td>'
            f'<td>{num(r.risk_ratio)}</td><td>{num(r.sharpe)}</td>'
            f'<td class={"pos" if (pd.notna(r.max_underperformance_vs_QQQ) and r.max_underperformance_vs_QQQ>=0) else "neg"}>{pct(r.max_underperformance_vs_QQQ)}</td></tr>'
            for r in sub.itertuples())
        tabs += (f'<h2>{plabel}</h2><div class=card><table><tr><th>벤치마크</th><th>총수익</th><th>연율</th>'
                 f'<th>MDD</th><th>회복</th><th>위험비율<br><span class=sub>ann/|MDD|</span></th>'
                 f'<th>Sharpe<br><span class=sub>rf=0</span></th><th>vs QQQ<br><span class=sub>최대열위</span></th></tr>{body}</table></div>')

    html = f"""<!doctype html><html lang=ko><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1"><title>PRAMANA A2 Benchmark Panel</title><style>
body{{background:#070b16;color:#e5e7eb;font-family:'Segoe UI','Malgun Gothic',system-ui,sans-serif;margin:0;line-height:1.5}}
.wrap{{max-width:1080px;margin:0 auto;padding:22px 18px 60px}} h1{{font-size:1.28em}}
.card{{background:#0d1326;border:1px solid #1e293b;border-radius:14px;padding:14px;margin:8px 0}} img{{width:100%;border-radius:8px}}
h2{{font-size:1.0em;border-left:4px solid #22d3ee;padding-left:10px;margin:18px 0 6px}}
table{{width:100%;border-collapse:collapse;font-size:.8em}} th{{background:#111a30;color:#94a3b8;text-align:left;padding:6px 8px}}
td{{padding:5px 8px;border-top:1px solid #1a2540}} .pos{{color:#34d399}} .neg{{color:#f87171}} .sub{{color:#64748b;font-weight:400;font-size:.85em}}
.warn{{background:#1c1408;border:1px solid #92400e;border-radius:10px;padding:11px 14px;color:#fde68a;font-size:.82em;margin:12px 0}}
.badge{{border-radius:6px;padding:2px 9px;font-size:.62em;font-weight:700;margin-left:6px}} .bp{{background:#1e3a8a;color:#bfdbfe}} .bw{{background:#7c2d12;color:#fed7aa}}</style></head><body>
<div class=wrap><h1>📊 PRAMANA A2 — 확장 벤치마크 패널<span class="badge bp">PAPER</span><span class="badge bw">백테스트</span></h1>
<div class=warn>⚠️ <b>백테스트(2016~·강세장 편향·닷컴/2008 없음) · PAPER · 검증된 알파 아님.</b> 데이터 {data_lo}~{data_hi}({len(full_idx)}거래일·Sharadar closeadj 캐시). 라이브 ₩1억 ledger 아님(a2_live_runner 소관). 자본권한 0. Synthetic 1.4x=금융비용 proxy 가정·DCA=contribution-weighted capital multiple(최종가치/총투입·buy&hold와 비교 가능·엄밀 IRR/MWRR 아님). {v7_note}</div>
<div class=card><img src="data:image/png;base64,{chart}"></div>
{tabs}
<div class=warn>성공 정의(§4): A2 &gt; QQQ AND A2 &gt; naive AND Vaulted Profit &gt; 0. 동적 allocator OFF/REJECT라 A2 base fixed = naive(QQQ35/TQQQ35/Cash30)와 동일 구성 → A2 운영규칙 부가가치는 forward live ledger(a2_live_runner Attack/Moonshot/Vault)에서만 측정됨·이 패널은 beta-book 비교용.</div>
<p style='color:#64748b;font-size:.75em'>생성 {dt.date.today()} · engine/a2_benchmarks.py · 위험비율=ann_return/|MDD|(Calmar류) · Sharpe rf=0 · vs QQQ 최대열위=시작정규화 누적차의 최저점</p>
</div></body></html>"""
    open(DASH, "w").write(html)
    print(f"✅ dashboard.html → {DASH}")

    # ── report ──
    inc = panel[panel["period"] == "inception-to-date"].set_index("benchmark")
    def g(name, col): return inc.loc[name, col] if name in inc.index else np.nan
    a2_name = "A2 base fixed (=A2 dynamic·동적 OFF)"; nv_name = "Naive Beta (QQQ35/TQQQ35/Cash30)"
    a2r, qqqr, nvr = g(a2_name, "total_return"), g("QQQ", "total_return"), g(nv_name, "total_return")
    beat_qqq = bool(a2r > qqqr); beat_naive = bool(a2r > nvr)   # A2 fixed vs naive는 구성동일 → ~동률(부동소수)
    # Vaulted Profit: 이 패널은 backtest beta-book만 → Vault는 forward live ledger 소관 → 0(미측정)
    vaulted = 0.0
    if beat_qqq and beat_naive and vaulted > 0: verdict = "성공 (A2>QQQ AND A2>naive AND Vaulted>0)"
    elif a2r < qqqr or a2r < nvr: verdict = "실패 (A2<QQQ 또는 A2<naive)"
    elif beat_qqq and not (a2r > nvr): verdict = "부분 성공 (A2>QQQ but A2≤naive → TQQQ beta는 효과·운영규칙 부가가치 미확정)"
    else: verdict = "판정 보류 (A2≈naive·동적 OFF로 동일구성 / Vaulted Profit는 backtest 패널서 미측정=forward live ledger 소관)"

    def mline(name):
        if name not in inc.index: return f"| {name} | (데이터 없음) |"
        r = inc.loc[name]
        return (f"| {name} | {r.total_return*100:+.1f}% | {r.annualized_return*100:+.1f}% | "
                f"{r.MDD*100:+.1f}% | {rd(r.recovery_days)} | {num(r.risk_ratio)} | {num(r.sharpe)} | "
                f"{pct(r.max_underperformance_vs_QQQ)} |")

    md = f"""# A2 Monthly Benchmark Review

> ⚠️ **백테스트(2016~·강세장 편향·닷컴/2008 crash 없음) · PAPER · 검증된 알파 아님.**
> 데이터 {data_lo}~{data_hi} ({len(full_idx)} 거래일, Sharadar closeadj 캐시). 라이브 ₩1억 ledger 아님(a2_live_runner 소관). 자본권한 0.
> 생성 {dt.date.today()} · engine/a2_benchmarks.py · spec: 04_BENCHMARKS_AND_METRICS.md

## Inception-to-date 패널 (full 2016~)

| 벤치마크 | 총수익 | 연율 | MDD | 회복 | 위험비율(ann/\\|MDD\\|) | Sharpe(rf=0) | vs QQQ 최대열위 |
|---|---|---|---|---|---|---|---|
{chr(10).join(mline(n) for n in NAVS)}

## 판정 (§4 성공 정의)

- **성공** = A2 > QQQ **AND** A2 > naive **AND** Vaulted Profit > 0
- **부분 성공** = A2 > QQQ but A2 < naive (TQQQ beta는 효과·운영규칙 부가가치 미확정)
- **실패** = A2 < QQQ 또는 A2 < naive 또는 Vaulted=0 또는 Attack/Moonshot 기여 ≤ 0

**A2 base fixed (inception-to-date): {a2r*100:+.1f}% · QQQ {qqqr*100:+.1f}% · naive {nvr*100:+.1f}%**

→ **{verdict}**

### 정직한 해석

- **A2 base fixed = naive(QQQ35/TQQQ35/Cash30)와 구성이 동일** (동적 allocator는 `dynamic_mode_enabled: false` = REJECT·동적기여 음수라 OFF 확정). 따라서 이 backtest 패널에서 **A2 base fixed ≈ naive (동률)**. 둘의 부가가치 차이는 이 패널로 측정 불가 — 운영규칙(Attack/Moonshot/Vault)은 forward live ledger(a2_live_runner)에서만 산다.
- A2 base fixed가 QQQ를 {'이김' if beat_qqq else '못 이김'}: QQQ35/TQQQ35/Cash30은 실효 beta ≈ {(0.35*1+0.35*3):.2f}x → 강세장(2016~)에선 QQQ buy-and-hold 대비 {'초과' if beat_qqq else '열위'}. 단 이건 **레버일 뿐 알파 아님** (synthetic 1.4x·TQQQ buy-and-hold와 같이 봐야 함).
- **Vaulted Profit = 0 (backtest 패널에선 미측정)**: §4 성공의 세 번째 조건은 forward live Vault ledger(a2_live_runner positions/vault.json) 소관. backtest 2016~ 누적 excess로 Vault를 돌리면 단위 부적합(live_runner 주석 참조)이라 OFF. → 이 패널만으로는 **"성공" 판정 불가**, beta-book 비교까지만.
- TQQQ buy-and-hold MDD={pct(g('TQQQ','MDD'))}·회복={rd(g('TQQQ','recovery_days'))} = 3x decay/낙폭의 실증. A2가 "큰 낙폭 후 게임 계속" 조건을 보려면 TQQQ MDD 대비 A2 MDD가 얕아야 함(현재 A2 fixed MDD={pct(g(a2_name,'MDD'))} vs TQQQ {pct(g('TQQQ','MDD'))}).

### TQ-DH 비교 (§5)

| | 총수익 | MDD | 회복 |
|---|---|---|---|
| TQQQ buy-and-hold | {pct(g('TQQQ','total_return'))} | {pct(g('TQQQ','MDD'))} | {rd(g('TQQQ','recovery_days'))} |
| TQQQ monthly DCA | {pct(g('TQQQ monthly DCA','total_return'))} | {pct(g('TQQQ monthly DCA','MDD'))} | {rd(g('TQQQ monthly DCA','recovery_days'))} |
| TQQQ drawdown DCA (-15%) | {pct(g('TQQQ drawdown DCA (-15%)','total_return'))} | {pct(g('TQQQ drawdown DCA (-15%)','MDD'))} | {rd(g('TQQQ drawdown DCA (-15%)','recovery_days'))} |

DCA는 **contribution-weighted capital multiple**(최종 시장가치/총투입 → buy-and-hold와 비교 가능·엄밀 IRR/MWRR는 아님). 매수일 미세 sawtooth(투입 희석)는 MDD에 보수적.

### caveats

- 강세장 편향: 2016~ 표본에 닷컴(-49% QQQ)·2008 없음 → TQQQ/synthetic 1.4x·A2 fixed 모두 **하방 미검증**. V8(분산북 레버) 기각 근거와 동일 caveat.
- Synthetic QQQ 1.4x = `QQQ일수익×1.4 − {FIN_DRAG*252*100:.1f}%/yr 금융비용 proxy` (가정·실제 펀딩비 아님).
- {v7_note}
- 동적 allocator OFF = A2 dynamic == A2 base fixed (이 패널 표기는 동일 곡선).
"""
    open(REPORT, "w").write(md)
    print(f"✅ report.md → {REPORT}")
    print(f"\n── inception-to-date 요약 ──\n{inc[['total_return','annualized_return','MDD','sharpe']].round(3).to_string()}")
    print(f"\nVERDICT: {verdict}")

if __name__ == "__main__":
    main()

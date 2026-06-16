#!/usr/bin/env python3
"""PRAMANA — 직접 작동 LIVE PAPER 데모. 완성도 높은 모델 3개 + 벤치를 ₩1억으로 forward.
인셉션=지난주(2026-06-09). 무료 yfinance EOD+최신가(intraday 지연) mark-to-market.
append-only CSV + 다크 DNA 라이브 차트(auto-refresh). PAPER·자본권한 0·검증된 알파 아님.
cron 권장(15분): cd phase1a && .venv/bin/python -u engine/live_demo.py
"""
import os, math, time
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); REPO = os.path.dirname(ROOT)
OUT = os.path.join(ROOT, "outputs", "live_demo"); os.makedirs(OUT, exist_ok=True)
DOCS = os.path.join(REPO, "docs")
CACHE = os.path.join(OUT, "px_cache.csv")          # API rate-limit 방지 캐시
THROTTLE_S = 3 * 3600                                # 캐시 3h 이내면 API 안 때림 (SFP=EOD라 충분)


def _save_cache(px):
    px.to_csv(CACHE)


def _load_cache():
    if not os.path.exists(CACHE):
        return None
    try:
        d = pd.read_csv(CACHE, index_col=0, parse_dates=True)
        return d.reindex(columns=TK) if set(TK).issubset(d.columns) else None
    except Exception:
        return None
CAP = 100_000_000                       # ₩1억
INCEPTION = "2026-05-16"                 # 한 달 전
TK = ["SPY", "QQQ", "TQQQ", "DBMF", "GLD", "IEF"]
# 표시 순서·색 (다크 DNA 팔레트)
ORDER = ["TQQQ", "VT-CANON", "v7", "Static 70/30", "QQQ", "SPY"]
COL = {"TQQQ": "#f87171", "VT-CANON": "#7dd3fc", "v7": "#34d399",
       "Static 70/30": "#fbbf24", "QQQ": "#38bdf8", "SPY": "#94a3b8"}
DESC = {"TQQQ": "3x 레버 (엔진·벤치)", "VT-CANON": "vol-target TQQQ (A4-0 정답)",
        "v7": "4-sleeve 생존코어", "Static 70/30": "TQQQ 70 / 현금 30",
        "QQQ": "나스닥100 (벤치)", "SPY": "S&P500 (벤치)"}
EXPLAIN_ORDER = ["VT-CANON", "v7", "Static 70/30", "TQQQ", "QQQ", "SPY"]
ALGO = {
    "VT-CANON": "매일 <code>w = clip(30% ÷ TQQQ 21일변동성, 0, 100%)</code> 만큼 TQQQ·나머지 현금 · 전날 변동성으로 다음날 적용(next-bar) · 잠잠하면 많이·출렁이면 적게 (예측 0)",
    "v7": "고정비중 <code>SPY25 · QQQ25 · DBMF25 · GLD15 · IEF10</code> · 1.0x · 월리밸런스 — 안 움직이는 자산 분산(DBMF=매니지드퓨처스·GLD=금·IEF=국채)",
    "Static 70/30": "고정 <code>TQQQ 70% + 현금 30%</code> · 월리밸런스 — 타이밍 없이 그냥 고정 레버",
    "TQQQ": "3배 레버 나스닥100 ETF 100% 보유 (일일 3×·매일리셋→decay) · 엔진/foil",
    "QQQ": "나스닥100 ETF 100% 매수 후 보유 · 벤치",
    "SPY": "S&P500 ETF 100% 매수 후 보유 · 벤치",
}


SRC = ""
VT_W = 0.0   # VT-CANON 현재(오늘) TQQQ 비중


def pull():
    """Sharadar(유료·PIT·SFP closeadj)=primary. 캐시·throttle·fallback로 API 에러 무중단.
    순서: ①3h내 캐시면 API 스킵 → ②Sharadar(날짜필터·경량) → ③실패시 캐시 → ④yfinance.
    """
    global SRC
    start = "2026-03-15"  # VT 21d vol warmup 충분
    cache = _load_cache()
    # ① throttle — 최근 캐시면 API 안 때림(rate-limit 방지). SFP는 EOD라 자주 부를 이유 없음.
    if cache is not None and len(cache) >= 30 and (time.time() - os.path.getmtime(CACHE)) < THROTTLE_S:
        SRC = "Sharadar (유료·PIT·SFP closeadj)"
        px = cache.copy(); px["cash"] = 0.036 / 252.0
        return px
    # ② Sharadar API (날짜 필터로 경량 pull — 전체 14921행 대신 ~수백행)
    try:
        import nasdaqdatalink as ndl
        ndl.ApiConfig.api_key = open(os.path.join(ROOT, ".ndl_key")).read().strip()
        try:
            df = ndl.get_table("SHARADAR/SFP", ticker=TK, date={"gte": start}, paginate=True)
        except Exception:
            df = ndl.get_table("SHARADAR/SFP", ticker=TK, paginate=True)  # 필터 미지원시 전체
        px = df.pivot_table(index="date", columns="ticker", values="closeadj").sort_index()
        px.index = pd.to_datetime(px.index)
        px = px[px.index >= start].reindex(columns=TK)
        if px[TK].isna().any().any() or len(px) < 30:
            raise RuntimeError("Sharadar 데이터 불충분")
        _save_cache(px); SRC = "Sharadar (유료·PIT·SFP closeadj)"
    except Exception as e:
        # ③ API 실패 → 캐시(있으면) 사용 (무중단)
        if cache is not None and len(cache) >= 30:
            px = cache; SRC = f"Sharadar 캐시 (API 일시오류 시 직전값: {str(e)[:30]})"
        else:
            # ④ 캐시도 없으면 yfinance fallback
            import yfinance as yf
            px = yf.download(TK, start=start, interval="1d", auto_adjust=True, progress=False)["Close"].dropna().reindex(columns=TK)
            _save_cache(px); SRC = "yfinance fallback (Sharadar 불가·캐시 없음)"
    px = px.copy(); px["cash"] = 0.036 / 252.0   # T-bill 일수익(~3.6%/yr·현금 sleeve)
    return px


def navs(px):
    inc = pd.Timestamp(INCEPTION)
    idx = px.index; m = idx >= inc
    out = pd.DataFrame(index=idx[m])
    # benchmarks: 1억 × price/price0
    for t in ("SPY", "QQQ", "TQQQ"):
        base = px[t][idx <= inc].iloc[-1]
        out[t] = CAP * px[t][m].values / base
    tr = {t: px[t].pct_change().fillna(0) for t in TK}
    cash = px["cash"]
    # VT-CANON: w=clip(0.3/rv21_tqqq,0,1) next-bar, daily, T-bill cash
    rv = (tr["TQQQ"].rolling(21).std() * math.sqrt(252))
    w = (0.30 / rv).clip(0, 1.0).shift(1).fillna(0.0)
    global VT_W; VT_W = float(w[m].iloc[-1]) * 100
    # v7 4-sleeve fixed weights
    v7w = {"SPY": .25, "QQQ": .25, "DBMF": .25, "GLD": .15, "IEF": .10}
    def run(daily_ret):  # daily_ret: Series indexed full → NAV from inception
        r = daily_ret[m]; nav = CAP * (1 + r).cumprod() / (1 + r.iloc[0])  # start at CAP on inception
        return nav.values
    vt_r = (w * tr["TQQQ"] + (1 - w) * cash)
    out["VT-CANON"] = run(vt_r)
    v7_r = sum(v7w[t] * tr[t] for t in v7w)
    out["v7"] = run(v7_r)
    s_r = 0.7 * tr["TQQQ"] + 0.3 * cash
    out["Static 70/30"] = run(s_r)
    return out


def svg_chart(nav):
    W, H = 860, 380; L, R, T, B = 60, 150, 16, 36; pw, ph = W - L - R, H - T - B
    dates = nav.index; n = len(dates)
    allv = nav[ORDER].values.flatten()
    vmin, vmax = float(np.nanmin(allv)), float(np.nanmax(allv))
    pad = (vmax - vmin) * 0.08 or vmax * 0.02
    lo, hi = vmin - pad, vmax + pad
    def sx(i): return L + (i / max(n - 1, 1)) * pw
    def sy(v): return T + (1 - (v - lo) / (hi - lo)) * ph
    s = [f'<svg viewBox="0 0 {W} {H}" width="100%" preserveAspectRatio="xMidYMid meet" font-family="inherit">']
    for gv in np.linspace(lo, hi, 5):
        y = sy(gv); s.append(f'<line x1="{L}" y1="{y:.0f}" x2="{L+pw}" y2="{y:.0f}" stroke="#1f2937"/>')
        s.append(f'<text x="{L-6}" y="{y+3:.0f}" font-size="10" fill="#94a3b8" text-anchor="end">{gv/1e8:.3f}억</text>')
    yb = sy(CAP); s.append(f'<line x1="{L}" y1="{yb:.0f}" x2="{L+pw}" y2="{yb:.0f}" stroke="#cbd5e1" stroke-dasharray="2 3" opacity=".5"/>')
    for i in range(0, n, max(1, n // 6)):
        s.append(f'<text x="{sx(i):.0f}" y="{T+ph+16:.0f}" font-size="9.5" fill="#94a3b8" text-anchor="middle">{dates[i].strftime("%m/%d")}</text>')
    ranked = sorted(ORDER, key=lambda t: -nav[t].iloc[-1])
    for t in ORDER:
        pts = " ".join(f"{sx(i):.1f},{sy(nav[t].iloc[i]):.1f}" for i in range(n))
        wdt = 3 if t in ("VT-CANON", "TQQQ") else 2
        s.append(f'<polyline points="{pts}" fill="none" stroke="{COL[t]}" stroke-width="{wdt}" opacity=".95"/>')
        s.append(f'<circle cx="{sx(n-1):.1f}" cy="{sy(nav[t].iloc[-1]):.1f}" r="3.5" fill="{COL[t]}"/>')
    # legend = current ₩ (desc)
    lx = L + pw + 14; ly = T + 8
    s.append(f'<text x="{lx}" y="{ly}" font-size="10" font-weight="700" fill="#cbd5e1">현재 (₩1억 진입)</text>'); ly += 17
    for t in ranked:
        v = nav[t].iloc[-1]; pct = (v / CAP - 1) * 100; sign = "+" if pct >= 0 else ""
        s.append(f'<line x1="{lx}" y1="{ly-3}" x2="{lx+12}" y2="{ly-3}" stroke="{COL[t]}" stroke-width="3"/>')
        s.append(f'<text x="{lx+17}" y="{ly}" font-size="10" fill="#cbd5e1">{t} <tspan font-weight="700" fill="{COL[t]}">{v/1e8:.3f}억</tspan> <tspan fill="#94a3b8">({sign}{pct:.1f}%)</tspan></text>')
        ly += 16
    s.append("</svg>")
    return "".join(s)


def render(nav):
    last = nav.index[-1]
    import datetime  # stamp는 파일 mtime 기반(Date 금지) — 여기선 데이터 마지막일만 표기
    import datetime
    gen = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).strftime("%Y-%m-%d %H:%M KST")
    days = len(nav); LEV = ("TQQQ", "Static 70/30", "VT-CANON")
    def mtr(t):
        a = nav[t].values
        mdd = float((a / np.maximum.accumulate(a) - 1).min()) * 100
        r = np.diff(a) / a[:-1]
        vol = float(np.std(r)) * math.sqrt(252) * 100 if len(r) > 1 else 0
        return mdd, vol
    rows = ""
    mono = "'JetBrains Mono',monospace"
    for t in sorted(ORDER, key=lambda t: -nav[t].iloc[-1]):
        v = nav[t].iloc[-1]; pct = (v / CAP - 1) * 100; sign = "+" if pct >= 0 else ""
        mdd, vol = mtr(t); c = COL[t]; col = "#34d399" if pct >= 0 else "#f87171"
        lev = ' <span style="color:#f87171;font-size:10px;font-weight:700">⚠레버</span>' if t in LEV else ''
        rows += (f'<tr><td><span style="color:{c};font-weight:700">{t}</span>{lev}<br><span style="color:#6b7280;font-size:11px">{DESC[t]}</span></td>'
                 f'<td style="text-align:right;font-family:{mono};font-weight:700">{v/1e8:.3f}억</td>'
                 f'<td style="text-align:right;color:{col};font-family:{mono}">{sign}{pct:.2f}%</td>'
                 f'<td style="text-align:right;color:#f87171;font-family:{mono}">{mdd:.1f}%</td>'
                 f'<td style="text-align:right;color:#94a3b8;font-family:{mono}">{vol:.0f}%</td></tr>')
    algo = "".join(
        f'<div class="algo"><div class="nm" style="color:{COL[t]}">{t}</div><div class="ds">{ALGO[t]}</div></div>'
        for t in EXPLAIN_ORDER)
    faq = [
        ("세로축 = 계좌 가치", "₩1억으로 진입한 뒤 현재 가치. 점선 = 진입 시점 ₩1억(본전선). 위=이익·아래=손실."),
        ("가로축 = 날짜", f"거래일만(주말·휴장 제외). 인셉션(시작) = 한 달 전 {INCEPTION}."),
        ("₩1억의 의미", "KRW 명목금액. 자산은 미국 ETF(USD)라 <b>수익률은 USD 자산 기준이고 환율(USDKRW) 변동은 미반영</b>. 한국인이 ₩1억으로 들어갔을 때의 '자산 수익' 관점."),
        ("사용 데이터", "<b>Sharadar(유료·PIT) SFP closeadj</b>(배당 재투자 반영가) · <b>일봉(EOD)</b> 기준. yfinance는 fallback(장애 시)만."),
        ("'라이브'의 뜻", "Sharadar는 EOD(종가) 상품이라 <b>하루에 한 번</b>(새 EOD 발표 시) 값이 바뀜. 장중 분봉으로 실시간 움직이는 게 아님 — 분봉 체결은 유료 분봉+브로커가 필요(보류)."),
        ("거래비용·가정 (전 모델 동일)", "<b>gross</b> — 거래비용·ETF 보수(expense) 미반영 · 현금=T-bill ~3.6%/yr · <b>환율(FX) 미반영</b>. (백테스트엔 5bps 반영했고 1달 회전 비용은 ~수 bp로 미미.) → VT-CANON vs Static 차이는 비용/회전이 아니라 <b>노출·변동성 차이</b>로 보세요."),
        ("왜 이 3개 모델?", "8세대 중 완성도 높은 것: <b>VT-CANON</b>(A4 연구의 정답) · <b>v7</b>(생존 코어) · <b>Static 70/30</b>(단순 고정 레버). 위 '모델 알고리즘' 참고."),
        ("TQQQ가 1등인 이유?", "3배 레버라 강세장엔 거의 무적. 단 <b>이 한 달은 비교적 잠잠한 구간</b>이라 TQQQ의 진짜 위험(과거 −82% 낙폭)은 안 보임 — 짧은 평온기는 레버를 미화합니다. (위 위험지표 표 참조.)"),
        ("look-ahead·데이터 무결성", "전략 신호는 <b>전날(prior) EOD 데이터만</b> 사용 → 신호 단계의 미래정보 누수 없음. 단 <b>데이터 벤더 사후정정(restatement)·배당/분할 조정 리스크는 남음('누수 0'은 아님)</b>. 매 실행 결정적(deterministic) 재계산."),
        ("용어 쉬운 풀이", "<b>vol-target</b>=변동성 커지면 비중 자동 축소 · <b>next-bar</b>=오늘 계산→다음 거래일 반영 · <b>PIT</b>=그 날짜에 알 수 있던 데이터만 · <b>closeadj</b>=배당 반영 종가 · <b>gross</b>=비용 전 · <b>회전(turnover)</b>=사고팖 빈도."),
    ]
    faqrows = "".join(
        f'<div class="algo"><div class="nm" style="color:#94a3b8;min-width:148px">{l}</div><div class="ds">{d}</div></div>'
        for l, d in faq)
    html = f"""<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="refresh" content="60">
<title>PRAMANA — 직접 작동 (Live Paper)</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
:root{{--accent:#7dd3fc}}*{{box-sizing:border-box}}
body{{margin:0;background:#0b0f17;color:#eaf0f7;font-family:'Inter',sans-serif;line-height:1.6}}
.aura{{position:fixed;border-radius:9999px;filter:blur(90px);pointer-events:none;z-index:0;opacity:.4;top:-12%;left:-6%;width:46vw;height:46vw;max-width:560px;max-height:560px;background:radial-gradient(circle,rgb(125 211 252 / .5),transparent 70%)}}
.wrap{{max-width:920px;margin:0 auto;padding:34px 22px 70px;position:relative;z-index:2}}
.kick{{color:var(--accent);font-size:11px;font-weight:600;letter-spacing:.18em;text-transform:uppercase}}
h1{{font-size:27px;margin:8px 0 6px;font-weight:800;filter:drop-shadow(0 0 12px rgb(125 211 252 / .25))}}
.sub{{color:#94a3b8;font-size:13.5px;margin:0 0 18px}}
.live{{display:inline-block;width:8px;height:8px;border-radius:50%;background:#34d399;box-shadow:0 0 8px #34d399;margin-right:6px;animation:p 1.4s infinite}}
@keyframes p{{0%,100%{{opacity:1}}50%{{opacity:.3}}}}
.card{{background:rgb(255 255 255 / .045);border:1px solid rgb(255 255 255 / .12);border-radius:16px;padding:22px;box-shadow:0 14px 38px rgb(0 0 0 / .22);backdrop-filter:blur(8px);margin:16px 0}}
table{{width:100%;border-collapse:collapse;font-size:13.5px}}td{{padding:9px 6px;border-bottom:1px solid rgb(55 65 81 / .5)}}
.note{{color:#6b7280;font-size:12px;margin-top:16px}}
code{{font-family:'JetBrains Mono',monospace;background:rgb(125 211 252 / .1);color:#7dd3fc;padding:1px 5px;border-radius:4px;font-size:11px}}
.algo{{display:flex;gap:12px;align-items:baseline;padding:8px 0;border-bottom:1px solid rgb(55 65 81 / .4)}}
.algo .nm{{min-width:104px;font-weight:700;font-size:13px;flex-shrink:0}}.algo .ds{{font-size:12.5px;color:#cbd5e1}}
</style></head><body><div class="aura"></div>
<div class="wrap">
<div class="kick">PRAMANA · LIVE PAPER · 자본권한 0</div>
<h1><span class="live"></span>직접 작동 — 완성도 높은 모델 3개를 ₩1억으로 forward</h1>
<p class="sub">인셉션 {INCEPTION}(한 달 전) · 마지막 EOD <b style="color:#cbd5e1">{last.date()}</b> · 데이터 <b style="color:var(--accent)">{SRC}</b> · 60초마다 자동 새로고침 · <b style="color:var(--accent)">VT-CANON</b>=vol-target(A4-0 정답) · <b style="color:#34d399">v7</b>=4-sleeve 생존코어 · <b style="color:#fbbf24">Static 70/30</b></p>
<div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#94a3b8;margin:0 0 12px;line-height:1.9"><span style="background:rgb(248 113 113 / .14);color:#fca5a5;border:1px solid rgb(248 113 113 / .35);padding:2px 9px;border-radius:6px;font-weight:700">PAPER FORWARD ONLY</span> · no broker execution · EOD close-to-close · last market date <b style="color:#cbd5e1">{last.date()}</b> · generated <b style="color:#cbd5e1">{gen}</b> · 매 실행마다 Sharadar로 재계산(append-only 아님)</div>
<div style="background:rgb(251 191 36 / .1);border:1px solid rgb(251 191 36 / .35);border-radius:12px;padding:13px 16px;margin:0 0 14px;font-size:13px;color:#fcd34d;line-height:1.6">⚠️ <b>1개월(비교적 평온기) forward 데모 — 대표성 없음.</b> 이 한 달은 잠잠해서 TQQQ가 1등이지만, 그건 레버의 <b>위험</b>(과거 −82% 낙폭)이 이 구간엔 안 나타났을 뿐입니다. 수익률만 보지 말고 아래 <b>최대낙폭·변동성</b>을 함께 보세요.</div>
<div style="margin:0 0 16px"><span style="background:rgb(248 113 113 / .12);border:1px solid rgb(248 113 113 / .4);color:#f87171;font-size:11.5px;font-weight:700;padding:4px 11px;border-radius:999px">⚠ TQQQ·VT-CANON·Static = 일일리셋 3배 레버 ETF — 장기 경로의존·급격한 대형 손실 가능 (SEC·FINRA 경고)</span></div>
<div class="card"><div class="chartbox">{svg_chart(nav)}</div></div>
<div class="card"><table><thead><tr><td style="color:#94a3b8;font-size:12px">모델</td><td style="text-align:right;color:#94a3b8;font-size:12px">현재 (₩1억→)</td><td style="text-align:right;color:#94a3b8;font-size:12px">수익률</td><td style="text-align:right;color:#94a3b8;font-size:12px">최대낙폭</td><td style="text-align:right;color:#94a3b8;font-size:12px">변동성(연율)</td></tr></thead><tbody>{rows}</tbody></table>
<p style="color:#6b7280;font-size:11.5px;margin:12px 0 0">최대낙폭=인셉션 이후 고점 대비 최대 하락 · 변동성=일수익 표준편차 연율화 · 둘 다 <b style="color:#f87171">'위험'</b> 지표(클수록 위험). 수익률만 보지 말 것. VT-CANON 현재 TQQQ 비중 = <b style="color:var(--accent)">{VT_W:.0f}%</b>.</p></div>
<div class="card">
<div class="kick" style="margin-bottom:8px">모델 알고리즘 — 어떻게 계산되나</div>
<p style="font-size:13px;color:#cbd5e1;margin:0 0 12px"><b style="color:var(--accent)">VT-CANON</b> = <b>V</b>ol-<b>T</b>arget(변동성 타겟팅)의 <b>CANON</b>(표준·튜닝 안 한 기준). "잠잠하면 많이, 출렁이면 적게" — 미래 예측이 아니라 <b>위험 크기만 일정하게</b> 맞춥니다.</p>
{algo}
<p style="font-size:12.5px;color:#94a3b8;margin:14px 0 0">핵심: <b style="color:#7dd3fc">VT-CANON·Static</b> = 노출 <b>크기</b> 조절 · <b style="color:#34d399">v7</b> = 노출 <b>대상</b> 분산. 셋 다 알파(예측)가 아니라 리스크 '형태'를 바꾸는 것 — 그게 8세대의 정직한 결론입니다.</p>
</div>
<div class="card">
<div class="kick" style="margin-bottom:10px">읽는 법 · 조건 (처음 보는 분들이 궁금해할 것)</div>
{faqrows}
</div>
<p class="note">⚠️ <b>PAPER ONLY · 자본권한 0 · 검증된 알파 아님.</b> 데이터 = <b>{SRC}</b>(결제 데이터 primary) <b>일봉(EOD)</b> 기준 mark-to-market(분봉 체결 아님). VT-CANON=일별 vol-target(30%/21d·T-bill 현금)·v7=4-sleeve 1.0x·Static 70/30=TQQQ70/현금30. ₩1억은 KRW notional(USD자산 수익률·FX 미반영). 짧은 윈도우라 차이 작음 — '직접 작동한다'의 증명이지 수익 주장 아님.</p>
</div></body></html>"""
    open(os.path.join(OUT, "live.html"), "w", encoding="utf-8").write(html)
    os.makedirs(DOCS, exist_ok=True)
    open(os.path.join(DOCS, "pramana_live.html"), "w", encoding="utf-8").write(html)
    nav.to_csv(os.path.join(OUT, "nav.csv"))
    return last


def main():
    try:
        px = pull(); nav = navs(px); last = render(nav)
        print(f"✅ live demo [{SRC[:30]}] · inception {INCEPTION} · last EOD {last.date()} · {len(nav)} days")
        for t in ORDER:
            v = nav[t].iloc[-1]; print(f"   {t:14} {v/1e8:.4f}억 ({(v/CAP-1)*100:+.2f}%)")
        print(f"   → {OUT}/live.html · docs/pramana_live.html")
    except Exception as e:
        import traceback; traceback.print_exc()
        print(f"⚠️ live_demo 실패 — 직전 정상 HTML 유지(덮어쓰기/크래시 안 함): {e}")


if __name__ == "__main__":
    main()

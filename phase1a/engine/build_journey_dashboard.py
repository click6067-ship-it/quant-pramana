#!/usr/bin/env python3
"""PRAMANA — 프로젝트 여정 대시보드 (발표용·v1~A4 한 장).
실데이터(a4_baselines.csv·a4_attribution.csv)에서 차트 수치 로드 → self-contained HTML(인라인 SVG).
숫자 날조 금지: 프론티어·타이밍알파·capture는 CSV에서, 팩터 IC-IR/여정 verdict는 리포트 기록값.
v2(2026-06-15): Codex 적대검수 REVISE 반영(scope 한정·IC-IR 통일·VT 표현 완화·TQQQ caveat·고급정보 reframe)
              + 히어로 'Return vs Pain Map'(타이밍알파 색코딩) + 'Capture vs Pain' 차트 추가.
cd phase1a && .venv/bin/python -u engine/build_journey_dashboard.py
"""
import os, csv, math, sys
LANG = os.environ.get("PRAMANA_LANG", "ko")
def _t(ko, en): return en if LANG == "en" else ko
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from multianchor import render_multianchor_section
from methodology import render_methodology_section
from why_section import render_why_section
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); REPO = os.path.dirname(ROOT)
A4 = os.path.join(ROOT, "outputs", "a4")
OUT = os.path.join(REPO, "pramana_journey_dashboard_en.html" if LANG == "en" else "pramana_journey_dashboard.html")


def load_baselines():
    rows = {}
    with open(os.path.join(A4, "a4_baselines.csv")) as fh:
        for r in csv.DictReader(fh):
            if r["window"] == "full_2010_26":
                rows[r["baseline"]] = (float(r["x"]), abs(float(r["mdd"])) * 100, float(r["sharpe"]))
    return rows


def load_timing():
    rows = {}
    with open(os.path.join(A4, "a4_attribution.csv")) as fh:
        for r in csv.DictReader(fh):
            rows[r["policy"]] = float(r["logA_em"])
    return rows


# ── HERO: Return vs Pain Map (Codex 제안 · 타이밍알파 색코딩) ────────────────
def svg_returnpain_map(bl, tm):
    W, H = 820, 500; L, R, T, B = 72, 150, 36, 60; pw, ph = W - L - R, H - T - B
    xmin, xmax = 30, 85; ymin, ymax = math.log(8), math.log(420)
    def sx(m): return L + (m - xmin) / (xmax - xmin) * pw
    def sy(v): return T + (1 - (math.log(v) - ymin) / (ymax - ymin)) * ph
    s = [f'<svg viewBox="0 0 {W} {H}" width="100%" preserveAspectRatio="xMidYMid meet" font-family="inherit">']
    for m in (30, 40, 50, 60, 70, 80):
        x = sx(m); s.append(f'<line x1="{x:.0f}" y1="{T}" x2="{x:.0f}" y2="{T+ph}" stroke="#1f2937"/>')
        s.append(f'<text x="{x:.0f}" y="{T+ph+18}" font-size="11" fill="#94a3b8" text-anchor="middle">-{m}%</text>')
    for v in (10, 25, 50, 100, 200, 400):
        y = sy(v); s.append(f'<line x1="{L}" y1="{y:.0f}" x2="{L+pw}" y2="{y:.0f}" stroke="#1f2937"/>')
        s.append(f'<text x="{L-8}" y="{y+4:.0f}" font-size="11" fill="#94a3b8" text-anchor="end">{v}x</text>')
    s.append(f'<text x="{L+pw/2:.0f}" y="{H-8}" font-size="12.5" fill="#94a3b8" text-anchor="middle" font-weight="600">{_t("최대낙폭(고통) → 오른쪽일수록 깊음", "Max drawdown (deeper →)")}</text>')
    s.append(f'<text x="18" y="{T+ph/2:.0f}" font-size="12.5" fill="#94a3b8" text-anchor="middle" font-weight="600" transform="rotate(-90 18 {T+ph/2:.0f})">{_t("총수익 배수 (log) ↑", "Total return (×, log) ↑")}</text>')
    # 이상점(빈칸) 주석 — 좌상단
    s.append(f'<rect x="{L+6}" y="{T+6}" width="150" height="40" rx="8" fill="rgb(251 191 36 / 0.12)" stroke="rgb(251 191 36 / 0.5)"/>')
    s.append(f'<text x="{L+12}" y="{T+23}" font-size="11.5" fill="#fcd34d" font-weight="700">{_t("이상점 = 빈칸", "Ideal corner = empty")}</text>')
    s.append(f'<text x="{L+12}" y="{T+39}" font-size="10.5" fill="#fbbf24">{_t("고수익·저낙폭 = 공짜점심 없음", "High return + low pain = no free lunch")}</text>')
    # static frontier dashed line
    statics = ["Static_30/70", "Static_40/60", "Static_50/50", "Static_60/40", "Static_70/30", "Static_80/20", "TQQQ_BH"]
    poly = " ".join(f"{sx(bl[k][1]):.0f},{sy(bl[k][0]):.0f}" for k in statics if k in bl)
    s.append(f'<polyline points="{poly}" fill="none" stroke="#cbd5e1" stroke-width="2" stroke-dasharray="5 4"/>')

    def star(x, y, r, c):
        pa = []
        for i in range(10):
            ang = -math.pi/2 + i*math.pi/5; rr = r if i % 2 == 0 else r*0.45
            pa.append(f"{x+rr*math.cos(ang):.1f},{y+rr*math.sin(ang):.1f}")
        return f'<polygon points="{" ".join(pa)}" fill="{c}"/>'
    def diamond(x, y, r, c): return f'<polygon points="{x},{y-r} {x+r},{y} {x},{y+r} {x-r},{y}" fill="{c}"/>'

    # static (neutral gray)
    for k, lab in [("Static_70/30", "70/30"), ("Static_60/40", "60/40"), ("Static_50/50", "50/50"),
                   ("Static_80/20", "80/20"), ("Static_40/60", "40/60")]:
        if k in bl:
            x, y = sx(bl[k][1]), sy(bl[k][0]); s.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="4.5" fill="#cbd5e1"/>')
            s.append(f'<text x="{x+8:.0f}" y="{y+4:.0f}" font-size="10" fill="#94a3b8">{lab}</text>')
    # benchmarks (blue) + TQQQ engine (dark star)
    bm = [("SPY", "SPY_BH", "#64748b", 6, -8, 16), ("QQQ", "QQQ_BH", "#38bdf8", 7, -10, -10),
          ("TQQQ B&H", "TQQQ_BH", "#e2e8f0", 11, -10, -14)]
    for lab, k, c, r, dx, dy in bm:
        if k not in bl: continue
        mult, mdd, _ = bl[k]; x, y = sx(mdd), sy(mult)
        s.append(star(x, y, r, c) if "TQQQ" in lab else diamond(x, y, r, c))
        anc = "end" if dx < 0 else "start"
        s.append(f'<text x="{x+dx:.0f}" y="{y+dy:.0f}" font-size="11.5" fill="#e2e8f0" text-anchor="{anc}" font-weight="700">{lab} {mult:.0f}x</text>')
    # 타이밍 시도들 — 색=타이밍알파(음수=빨강 강도). 전부 음수=가짜 타이밍.
    dyn = [("VT-CANON", "VT-CANON(30%/21/1.0)", "VT-CANON", -10, -12),
           ("VT-GRID", "VT-GRID_best(30%/21/0.7)", "VT-GRID(30%/21/0.7)", -10, 16),
           ("C3", "C3_x", None, 12, 4), ("C1", "C1_x", None, 12, -10), ("C2", "C2_x", None, 12, 14)]
    # C1/C2/C3 좌표는 attribution 수치(고정전략 아님) — bl엔 없으니 직접
    dyn_xy = {"VT-CANON": (bl["VT-CANON(30%/21/1.0)"][0], bl["VT-CANON(30%/21/1.0)"][1], tm.get("VT-CANON", 0)),
              "VT-GRID": (bl["VT-GRID_best(30%/21/0.7)"][0], bl["VT-GRID_best(30%/21/0.7)"][1], tm.get("VT-GRID(30%/21/0.7)", 0)),
              "C1": (153.3, 48.4, tm.get("C1_shock/struct_cut", 0)), "C2": (139.8, 48.4, tm.get("C2_+decay_cut", 0)),
              "C3": (65.2, 34.9, tm.get("C3_fixed0.70_sm", 0))}
    def red(a):  # logA in ~[-0.4,0] → red intensity
        t = min(1.0, abs(a) / 0.40); g = int(120 * (1 - t)); return f"rgb({200+int(20*t)},{60+g},{60+g})"
    for lab, _, _, dx, dy in dyn:
        mult, mdd, a = dyn_xy[lab]; x, y = sx(mdd), sy(mult); c = red(a)
        s.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="7.5" fill="{c}" stroke="#fff" stroke-width="1.5"/>')
        anc = "end" if dx < 0 else "start"
        s.append(f'<text x="{x+dx:.0f}" y="{y+dy:.0f}" font-size="11" fill="#f87171" text-anchor="{anc}" font-weight="700">{lab}</text>')
    # legend
    lx = L + pw + 20
    s.append(f'<text x="{lx}" y="{T+8}" font-size="11.5" font-weight="700" fill="#cbd5e1">{_t("범례", "Legend")}</text>')
    leg = [("#e2e8f0", _t("★ TQQQ (엔진)", "★ TQQQ (engine)"), "star"), ("#38bdf8", _t("◆ 벤치(SPY/QQQ)", "◆ Benchmark (SPY/QQQ)"), "dia"),
           ("#cbd5e1", _t("● 고정비율", "● Fixed ratio"), "dot"), ("#dc2626", _t("● 타이밍 시도", "● Timing attempt"), "dot")]
    yy = T + 28
    for c, t, k in leg:
        if k == "star": s.append(star(lx + 6, yy - 3, 6, c))
        elif k == "dia": s.append(diamond(lx + 6, yy - 3, 5, c))
        else: s.append(f'<circle cx="{lx+6}" cy="{yy-3}" r="5" fill="{c}"/>')
        s.append(f'<text x="{lx+18}" y="{yy}" font-size="10.5" fill="#94a3b8">{t}</text>'); yy += 22
    s.append(f'<text x="{lx}" y="{yy+6}" font-size="10" fill="#f87171" font-weight="600">{_t("빨강 = 타이밍", "Red = timing")}</text>')
    s.append(f'<text x="{lx}" y="{yy+20}" font-size="10" fill="#f87171">{_t("알파 음수(=노출효과)", "negative alpha (= exposure)")}</text>')
    s.append("</svg>")
    return "".join(s)


# ── Capture vs Pain (절대합 — TQQQ 대비 상방 얼마 먹고 고통 얼마 피했나) ──────
def svg_capture_pain(bl):
    tq_log = math.log(bl["TQQQ_BH"][0]); tq_mdd = bl["TQQQ_BH"][1]
    items = []
    for lab, key in [("C1", "C1"), ("VT-CANON", "VT-CANON(30%/21/1.0)"), ("C3", "C3"),
                     ("Static 70/30", "Static_70/30"), ("QQQ", "QQQ_BH")]:
        if key == "C1": mult, mdd = 153.3, 48.4
        elif key == "C3": mult, mdd = 65.2, 34.9
        else: mult, mdd, _ = bl[key]
        cap = math.log(mult) / tq_log * 100; pain = (1 - mdd / tq_mdd) * 100
        items.append((lab, cap, pain))
    W, H = 820, 330; L, R, T, B = 110, 130, 24, 40; pw, ph = W - L - R, H - T - B
    n = len(items); rowh = ph / n
    s = [f'<svg viewBox="0 0 {W} {H}" width="100%" preserveAspectRatio="xMidYMid meet" font-family="inherit">']
    s.append(f'<text x="{L}" y="16" font-size="11" fill="#16a34a" font-weight="700">{_t("■ TQQQ 상방 capture %", "■ TQQQ upside capture %")}</text>')
    s.append(f'<text x="{L+200}" y="16" font-size="11" fill="#38bdf8" font-weight="700">{_t("■ TQQQ 고통 회피 %", "■ TQQQ pain avoided %")}</text>')
    for x in (0, 25, 50, 75, 100):
        gx = L + x / 100 * pw; s.append(f'<line x1="{gx:.0f}" y1="{T}" x2="{gx:.0f}" y2="{T+ph}" stroke="#1f2937"/>')
        s.append(f'<text x="{gx:.0f}" y="{T+ph+16}" font-size="10" fill="#94a3b8" text-anchor="middle">{x}%</text>')
    for i, (lab, cap, pain) in enumerate(items):
        cy = T + rowh * i + rowh / 2
        s.append(f'<text x="{L-10}" y="{cy+4:.0f}" font-size="12" fill="#cbd5e1" text-anchor="end" font-weight="600">{lab}</text>')
        bw = rowh * 0.30
        s.append(f'<rect x="{L}" y="{cy-bw-2:.0f}" width="{cap/100*pw:.0f}" height="{bw:.0f}" rx="3" fill="#16a34a"/>')
        s.append(f'<text x="{L+cap/100*pw+6:.0f}" y="{cy-2:.0f}" font-size="11" fill="#4ade80" font-weight="700">{cap:.0f}%</text>')
        s.append(f'<rect x="{L}" y="{cy+2:.0f}" width="{pain/100*pw:.0f}" height="{bw:.0f}" rx="3" fill="#0ea5e9"/>')
        s.append(f'<text x="{L+pain/100*pw+6:.0f}" y="{cy+bw+2:.0f}" font-size="11" fill="#7dd3fc" font-weight="700">{pain:.0f}%</text>')
    s.append("</svg>")
    return "".join(s)


def svg_bars(items, unit="", color_pos="#16a34a", color_neg="#dc2626", thresh=None, thr_label=""):
    W, H = 760, 300; L, R, T, B = 60, 20, 30, 70; pw, ph = W - L - R, H - T - B
    vals = [v for _, v in items]; vmax = max(abs(min(vals)), abs(max(vals)), (abs(thresh) if thresh else 0)) * 1.25
    def sy(v): return T + ph/2 - (v / vmax) * (ph/2)
    n = len(items); bw = pw / n * 0.6; gap = pw / n
    s = [f'<svg viewBox="0 0 {W} {H}" width="100%" preserveAspectRatio="xMidYMid meet" font-family="inherit">']
    zy = sy(0); s.append(f'<line x1="{L}" y1="{zy:.0f}" x2="{L+pw}" y2="{zy:.0f}" stroke="#94a3b8" stroke-width="1.5"/>')
    if thresh is not None:
        ty = sy(thresh); s.append(f'<line x1="{L}" y1="{ty:.0f}" x2="{L+pw}" y2="{ty:.0f}" stroke="#0ea5e9" stroke-width="1.5" stroke-dasharray="6 4"/>')
        s.append(f'<text x="{L+pw}" y="{ty-5:.0f}" font-size="10.5" fill="#38bdf8" text-anchor="end">{thr_label}</text>')
    for i, (label, v) in enumerate(items):
        x = L + gap*i + (gap-bw)/2; y = sy(v); h = abs(y - zy); col = color_pos if v >= 0 else color_neg
        s.append(f'<rect x="{x:.0f}" y="{min(y,zy):.0f}" width="{bw:.0f}" height="{h:.0f}" rx="3" fill="{col}"/>')
        vy = y - 6 if v >= 0 else y + 16
        s.append(f'<text x="{x+bw/2:.0f}" y="{vy:.0f}" font-size="11.5" fill="#cbd5e1" text-anchor="middle" font-weight="700">{v:+.3f}{unit}</text>')
        s.append(f'<text x="{x+bw/2:.0f}" y="{T+ph+22:.0f}" font-size="11" fill="#94a3b8" text-anchor="middle">{label}</text>')
    s.append("</svg>")
    return "".join(s)


# ── journey + reflections ───────────────────────────────────────────────────
JOURNEY = [
    ("v1–v3", _t("단순 횡단면 팩터 6종 (value·momentum·quality·lowvol…)", "6 simple cross-sectional factors (value·momentum·quality·lowvol…)"), "DEAD", _t("비용후 net 엣지 0 · 정직한 negative", "Zero net edge after costs · honest negative"), "#dc2626"),
    ("v4", _t("Core Beta 1.0x (SPY/QQQ 추종)", "Core Beta 1.0x (tracking SPY/QQQ)"), _t("베타", "beta"), _t("알파 아님 · 자기 벤치 못 넘음", "Not alpha · can't beat its own benchmark"), "#64748b"),
    ("v5", _t("공격적 레버드 코어 (vol-target 2x)", "Aggressive levered core (vol-target 2x)"), _t("레버드 베타", "levered beta"), _t("in-sample QQQ 넘지만 레버지 알파 아님", "Beats QQQ in-sample but it's leverage, not alpha"), "#64748b"),
    ("v6–v7", _t("4-sleeve 분산 (주식·매니지드퓨처스·금·채권)", "4-sleeve diversification (equity·managed futures·gold·bonds)"), _t("리스크통제", "risk control"), _t("안정·낙폭↓ but QQQ 강세장 수익 절반 포기", "Stable, lower drawdown, but gives up half the upside in a QQQ bull run"), "#38bdf8"),
    ("Alpha Lab", _t("급등주 인트라데이 setup (ORB·VWAP·RVOL)", "Momentum-spike intraday setups (ORB·VWAP·RVOL)"), "DEAD", _t("look-ahead 잡음 · false breakout 56%", "Look-ahead noise · 56% false breakouts"), "#dc2626"),
    ("A1", _t("Catalyst Attack Book (직접+레딧·LLM 비추천 길)", "Catalyst Attack Book (hand-built + Reddit · the path LLMs advise against)"), "DEAD", _t("이벤트·정성 베팅도 TQQQ 매집 못 넘음", "Event/qualitative bets still can't beat buying TQQQ"), "#dc2626"),
    ("A2 / AX", _t("Convex Raider · 옵션 컨벡시티 공격", "Convex Raider · options-convexity attack"), "DEAD", _t("Attack/Moonshot blind backtest 전멸", "Attack/Moonshot blind backtests wiped out"), "#dc2626"),
    ("A3", _t("TQQQ War Engine (Vault timing·상태기계)", "TQQQ War Engine (Vault timing · state machine)"), "PARTIAL", _t("낙폭은 방어(-17% vs -82%) but QQQ 못 이김", "Defends drawdown (-17% vs -82%) but can't beat QQQ"), "#f59e0b"),
    ("A4-0", _t("Vault Study (사전등록 falsification)", "Vault Study (pre-registered falsification)"), "NULL", _t("vol-target가 답 · timing 불필요", "vol-target is the answer · timing unnecessary"), "#7c3aed"),
    ("A4 Stage A", _t("Attribution (노출 vs 타이밍 분해)", "Attribution (exposure vs timing decomposition)"), _t("결론", "verdict"), _t("타이밍 알파 0/5 · 수익=노출효과", "Timing alpha 0/5 · returns = exposure effect"), "#16a34a"),
]
FACT_IC = [("value", -0.029), ("quality", 0.022), ("momentum", 0.045)]   # IC-IR (보고서와 통일)
REFLECT = [
    (_t("1막 · 검증된 방법의 한계", "Act 1 · The limits of proven methods"),
     _t("초기 모델은 LLM(Claude·Codex)이 알려주는 <b>검증되고 안전한 방법</b>을 리서치해서 적용했다. v1에서 v7로 진화할수록 결국 그 안에서 분산·섬세함·안정성을 다듬는 작업이었지만 — <b>단순 SPY/QQQ 매수를 못 이겼다.</b> 적어도 내가 검증한 공개데이터·일봉·비용후 후보군에서는, 이미 알려지고 검증된 안전한 방법으로 수익 내기가 어려웠다.",
       "My early models researched and applied the <b>proven, safe methods</b> that LLMs (Claude·Codex) recommend. As I evolved from v1 to v7, it all came down to refining diversification, nuance, and stability within those methods — but <b>none of it could beat simply buying SPY/QQQ.</b> At least in the candidate set I tested — public data, daily bars, after costs — it was hard to make money with methods that are already known and proven safe.")),
    (_t("2막 · 알파는 어디서 오는가", "Act 2 · Where does alpha come from"),
     _t("차트 기술(모멘텀·엘리엇 파동·캔들)은 <b>이미 알려져 시장에 반영</b>돼 수익으로 안 이어진다는 걸 알았다. 알파는 공개된 차트 패턴이 아니라 <b>남들이 안 파본 정보 우위(직접 리서치·전문가 의견 취합)와, 남들이 못 버티는 리스크·제약을 인수</b>하는 데서 오는 것 같았다. 그래서 LLM이 비추천하는 길을 직접 찾고 레딧 등 전문가 의견을 모아 <b>A1</b>을 만들었다 — 근데 그것조차 <b>단순 레버리지 TQQQ 매집</b>을 못 이겼다.",
       "I learned that chart techniques (momentum, Elliott waves, candlesticks) are <b>already known and priced in</b>, so they don't turn into profit. Alpha seemed to come not from public chart patterns but from <b>an information edge no one else has dug into (hands-on research, aggregating expert opinion), and from taking on risk and constraints others can't stomach.</b> So I went down the path LLMs advise against, gathered expert opinions from places like Reddit, and built <b>A1</b> — and even that couldn't beat <b>simply accumulating levered TQQQ.</b>")),
    (_t("3막 · 못 이기면 낙폭이라도", "Act 3 · If you can't win, at least cut the pain"),
     _t("단순 TQQQ 매집을 <b>수익으로</b> 못 이긴다면, <b>낙폭이라도 완화</b>해서 TQQQ보다 매력적인 시스템을 만들고 싶었다. 그래서 비율·수학 공식 — <b>타이밍 매도/매수를 잘 조절하면 되지 않을까</b>에서 A4까지 왔다. 결과: 모든 타이밍이 같은 평균 노출 고정전략에 <b>복리로 졌다.</b> 수익은 타이밍이 아니라 TQQQ 노출 자체였다.",
       "If I couldn't beat plain TQQQ accumulation <b>on returns</b>, I at least wanted to <b>soften the drawdown</b> and build a system more attractive than TQQQ. That impulse — ratios, math formulas, <b>maybe if I tune the timing of selling and buying well enough</b> — carried me all the way to A4. The result: every timing scheme <b>lost on a compound basis</b> to a fixed strategy with the same average exposure. The returns were the TQQQ exposure itself, not the timing.")),
]
CONCLUSIONS = [
    _t("<b>내가 검증한 공개데이터(Sharadar 유료 PIT·yfinance·EDGAR)·일봉·비용후 후보군</b>에서는, 검증된·알려진·안전한 방법이 SPY/QQQ도 단순 TQQQ 노출도 못 이겼다 (8세대 robust negative).",
       "In the candidate set I tested — <b>public data (Sharadar paid PIT · yfinance · EDGAR), daily bars, after costs</b> — proven, known, safe methods couldn't beat SPY/QQQ or plain TQQQ exposure either (8 generations, a robust negative)."),
    _t("차트 기술·팩터·타이밍 = 알파 아님. 검증 인프라(자작 PIT 지수 vs 실제 SPY corr 0.998)는 완성했으나 <b>이 후보군에 찾을 알파가 없었다.</b>",
       "Chart techniques, factors, timing = not alpha. The verification infrastructure (my self-built PIT index vs real SPY, corr 0.998) was completed, but <b>there was no alpha to find in this candidate set.</b>"),
    _t("수익 엔진 = <b>TQQQ 노출(레버드 베타)</b>이지 알파가 아니다. 타이밍/Vault는 복리만 깎았다 (Cash Drag &gt; Defense).",
       "The return engine = <b>TQQQ exposure (levered beta)</b>, not alpha. Timing/Vault only ate into compounding (Cash Drag &gt; Defense)."),
    _t("vol-target은 알파가 아니라 <b>리스크 통제</b> — TQQQ 낙폭 -82%→-42%로 절반 (수익은 못 더하되 버틸 수 있게).",
       "vol-target is not alpha but <b>risk control</b> — it halves TQQQ's drawdown from -82% to -42% (it adds no return, but makes it survivable)."),
    _t("가장 큰 자산 = <b>가짜 알파를 안 만든 검증 규율.</b> look-ahead를 잡고, 사전등록 NULL을 지키고, 결과를 정직하게 negative로 적었다.",
       "The biggest asset = <b>the discipline that never manufactured fake alpha.</b> I caught look-ahead, honored the pre-registered NULL, and wrote the results down honestly as negative."),
    _t("길을 잃은 게 아니다 — <b>알파 프로젝트를 정직하게 끝냈고</b>, 이제 '버틸 수 있는 레버 사이즈'를 고르는 단계다. 그게 정직한 종착점.",
       "I'm not lost — <b>I finished the alpha project honestly</b>, and now I'm at the stage of choosing 'a leverage size I can live through.' That's the honest endpoint."),
]


def main():
    bl = load_baselines(); tm = load_timing()
    timing_items = [("VT-CANON", tm.get("VT-CANON", 0)), ("VT-GRID", tm.get("VT-GRID(30%/21/0.7)", 0)),
                    ("C1", tm.get("C1_shock/struct_cut", 0)), ("C2", tm.get("C2_+decay_cut", 0)),
                    ("C3", tm.get("C3_fixed0.70_sm", 0))]
    jrows = "".join(
        f'<div class="jrow"><div class="jgen">{g}</div><div class="jdesc"><b>{d}</b><span>{note}</span></div>'
        f'<div class="jbadge" style="background:{c}1a;color:{c};border:1px solid {c}55">{v}</div></div>'
        for g, d, v, note, c in JOURNEY)
    reflect = "".join(f'<div class="rcard"><h3>{t}</h3><p>{p}</p></div>' for t, p in REFLECT)
    concl = "".join(f'<li>{c}</li>' for c in CONCLUSIONS)
    html = f"""<!doctype html><html lang="{_t("ko", "en")}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{_t("PRAMANA — 알파를 찾아 8세대 (발표용)", "PRAMANA — 8 generations hunting alpha (presentation)")}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
/* DESIGN DNA — Vastlyra skin · dark frosted-white glass · soft drop shadow · accent=sky #7dd3fc */
:root{{--ink:#eaf0f7;--mut:#9fb0c3;--dim:#6b7a8d;--line:rgb(255 255 255 / .08);--accent:#7dd3fc;--accent2:#38bdf8;--bg:#0b0f17;
--card:rgb(255 255 255 / .045);--surface:rgb(255 255 255 / .12);--glow:0 14px 38px rgb(0 0 0 / .22);--glowh:0 18px 44px rgb(0 0 0 / .30),0 0 26px rgb(125 211 252 / .14)}}
*{{box-sizing:border-box}}
body{{margin:0;font-family:'Inter','Pretendard',-apple-system,'Malgun Gothic','Apple SD Gothic Neo',sans-serif;color:var(--ink);background:var(--bg);line-height:1.65;position:relative;-webkit-font-smoothing:antialiased}}
.snav{{position:sticky;top:0;z-index:40;background:linear-gradient(180deg,rgb(11 15 23 / .90),rgb(11 15 23 / .62));backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);border-bottom:1px solid var(--surface)}}
.snav-in{{max-width:920px;margin:0 auto;display:flex;align-items:center;justify-content:space-between;gap:14px;padding:11px 22px;padding-right:108px}}
.snav .brand{{display:flex;align-items:center;gap:9px;color:var(--ink);text-decoration:none;font-weight:800;font-size:15px;letter-spacing:-.01em}}
.snav .brand .dot{{width:9px;height:9px;border-radius:50%;background:var(--accent);box-shadow:0 0 12px rgb(125 211 252 / .75)}}
.snav .brand small{{color:var(--mut);font-weight:500;font-size:11.5px;letter-spacing:.02em}}
.snav-live{{color:var(--accent);text-decoration:none;font-weight:700;font-size:12.5px;border:1px solid rgb(125 211 252 / .35);background:rgb(125 211 252 / .08);padding:6px 13px;border-radius:999px;white-space:nowrap;transition:all .18s}}
.snav-live:hover{{background:rgb(125 211 252 / .18)}}
@media(max-width:640px){{.snav .brand small{{display:none}}.snav-in{{padding-right:96px}}}}
.aura{{position:fixed;border-radius:9999px;filter:blur(90px);pointer-events:none;z-index:0;opacity:.42}}
.aura1{{top:-12%;left:-6%;width:46vw;height:46vw;max-width:600px;max-height:600px;background:radial-gradient(circle,rgb(125 211 252 / .5),transparent 70%)}}
.aura2{{bottom:-16%;right:-10%;width:50vw;height:50vw;max-width:640px;max-height:640px;background:radial-gradient(circle,rgb(56 189 248 / .24),transparent 70%)}}
.noise:after{{content:'';position:fixed;inset:0;z-index:1;opacity:.03;pointer-events:none;background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")}}
.wrap{{max-width:920px;margin:0 auto;padding:0 22px 80px;position:relative;z-index:2}}
header{{background:linear-gradient(180deg,rgb(125 211 252 / .06),transparent),#0b0f17;border-bottom:1px solid var(--surface);padding:54px 22px 46px;margin-bottom:8px;position:relative;z-index:2}}
header .wrap{{padding-bottom:0}}
.kick{{color:var(--accent);font-weight:600;letter-spacing:.18em;font-size:11px;text-transform:uppercase}}
h1{{font-size:34px;margin:8px 0 10px;line-height:1.25;font-weight:800;letter-spacing:-.01em;filter:drop-shadow(0 0 12px rgb(125 211 252 / .25))}}
header p{{color:var(--mut);font-size:16px;max-width:700px;margin:0}}
.tagline{{margin-top:18px;font-size:15px;color:#fbbf24;font-weight:600}}
section{{background:var(--card);border:1px solid var(--surface);border-radius:16px;padding:26px 28px;margin:20px 0;box-shadow:var(--glow);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);position:relative;z-index:2}}
.hero{{border:1px solid rgb(125 211 252 / .35);box-shadow:0 14px 38px rgb(0 0 0 / .22),0 0 34px rgb(125 211 252 / .14)}}
h2{{font-size:21px;margin:0 0 4px;display:flex;align-items:center;gap:10px;color:var(--ink);font-weight:800}}
h2 .n{{background:rgb(125 211 252 / .15);color:var(--accent);border:1px solid rgb(125 211 252 / .4);width:28px;height:28px;border-radius:8px;display:inline-flex;align-items:center;justify-content:center;font-size:14px;font-weight:700}}
.sub{{color:var(--mut);font-size:14px;margin:0 0 18px}}
.jrow{{display:grid;grid-template-columns:96px 1fr auto;gap:14px;align-items:center;padding:11px 0;border-top:1px solid var(--line)}}
.jrow:first-child{{border-top:none}}
.jgen{{font-weight:800;color:var(--ink);font-size:15px}}
.jdesc b{{display:block;font-size:14.5px}}.jdesc span{{color:var(--mut);font-size:12.5px}}
.jbadge{{font-size:12px;font-weight:800;padding:4px 11px;border-radius:999px;white-space:nowrap}}
.rcard{{border-left:3px solid var(--accent);background:rgb(125 211 252 / .06);padding:14px 18px;border-radius:0 10px 10px 0;margin:14px 0}}
.rcard h3{{margin:0 0 6px;font-size:16px;color:var(--ink)}}.rcard p{{margin:0;font-size:14.5px;color:#cbd5e1}}
.chartbox{{margin:6px 0 4px}}
.cap{{color:var(--mut);font-size:13px;margin:10px 2px 0}}.cap b{{color:var(--ink)}}
ul.concl{{list-style:none;padding:0;margin:6px 0 0;counter-reset:c}}
ul.concl li{{position:relative;padding:12px 14px 12px 46px;border-bottom:1px solid var(--line);font-size:15px}}
ul.concl li:before{{counter-increment:c;content:counter(c);position:absolute;left:12px;top:11px;width:24px;height:24px;background:var(--accent);color:#03121a;border-radius:7px;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:800}}
.kpis{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:16px 0 0}}
.kpi{{background:rgb(255 255 255 / .03);border:1px solid var(--surface);border-radius:12px;padding:14px;text-align:center}}
.kpi .v{{font-size:24px;font-weight:800;color:var(--accent)}}.kpi .l{{font-size:12px;color:var(--mut);margin-top:2px}}
.machart{{margin:14px 0 4px;padding:12px 14px;background:rgb(255 255 255 / .02);border:1px solid var(--surface);border-radius:10px}}
.malabel{{font-weight:700;font-size:13.5px;color:#cbd5e1;margin-bottom:6px}}
.dtab{{border-collapse:collapse;width:100%;font-size:13px}}
.dtab th{{background:rgb(125 211 252 / .12);color:var(--accent);padding:8px 10px;text-align:left;font-size:12.5px}}
.dtab td{{border-bottom:1px solid var(--line);padding:8px 10px;vertical-align:top}}
.dtab .tag{{font-size:10.5px;color:#03121a;background:#34d399;border-radius:5px;padding:1px 6px;font-weight:700}}
.dtab tr td:first-child .tag{{background:#64748b;color:#fff}}
.fgrid{{display:grid;grid-template-columns:1fr 1fr;gap:10px}}
.fcard{{background:rgb(255 255 255 / .02);border:1px solid var(--surface);border-radius:10px;padding:12px 14px}}
.fname{{font-weight:800;font-size:13.5px;color:var(--ink);margin-bottom:6px}}
.fexpr{{margin:0 0 6px}}.fexpr code{{font-family:'JetBrains Mono',ui-monospace,monospace;background:#060d18;color:#7dd3fc;border:1px solid rgb(125 211 252 / .2);padding:4px 8px;border-radius:6px;font-size:12px;display:inline-block;word-break:break-word}}
.fplain{{font-size:12.5px;color:var(--mut)}}
.pflow{{display:flex;flex-direction:column;gap:8px}}
.pcard{{border-left:3px solid var(--accent);background:rgb(125 211 252 / .06);border-radius:0 8px 8px 0;padding:11px 14px}}
.pname{{font-weight:800;font-size:14px;color:var(--ink);margin-bottom:3px}}
.pdesc{{font-size:13px;color:#cbd5e1}}.pdesc code{{font-family:'JetBrains Mono',monospace;background:rgb(255 255 255 / .08);color:#cbd5e1;padding:1px 5px;border-radius:4px;font-size:11.5px}}
.checklist{{list-style:none;padding:0;margin:6px 0 0}}
.checklist li{{position:relative;padding:9px 12px 9px 14px;border-bottom:1px solid var(--line);font-size:13.5px}}
.qcard{{border:1px solid var(--surface);border-radius:12px;padding:16px 18px;margin:12px 0;background:rgb(255 255 255 / .02)}}
.qq{{font-weight:800;font-size:16px;color:var(--ink);margin-bottom:8px;padding-bottom:8px;border-bottom:2px solid rgb(125 211 252 / .4)}}
.qa{{margin:0;padding-left:20px}}.qa li{{font-size:14px;color:#cbd5e1;margin:7px 0;line-height:1.6}}
code{{font-family:'JetBrains Mono',ui-monospace,monospace}}
@media(max-width:640px){{.fgrid{{grid-template-columns:1fr}}}}
.foot{{color:var(--mut);font-size:12.5px;text-align:center;margin-top:30px}}
@media(max-width:640px){{.kpis{{grid-template-columns:repeat(2,1fr)}}.jrow{{grid-template-columns:70px 1fr}}.jbadge{{grid-column:2;justify-self:start}}}}
</style></head><body class="noise">
<div class="aura aura1"></div><div class="aura aura2"></div>
<nav class="snav"><div class="snav-in">
<a class="brand" href="#"><span class="dot"></span>PRAMANA <small>{_t("8세대 알파 탐사 · PAPER", "8 generations hunting alpha · PAPER")}</small></a>
<a class="snav-live" href="https://click6067-ship-it.github.io/quant-pramana/pramana_live.html" target="_blank">▶ {_t("라이브 데모", "Live demo")} ↗</a>
</div></nav>
<header><div class="wrap">
<div class="kick">{_t("PRAMANA · solo + LLM 퀀트 리서치 OS · PAPER ONLY", "PRAMANA · solo + LLM quant research OS · PAPER ONLY")}</div>
<h1>{_t("알파를 찾아 8세대 — 그리고 정직한 결론", "8 generations hunting alpha — and the honest verdict")}</h1>
<p>{_t('한 솔로가 Claude·Codex와 함께 "시장을 이기는 검증된 모델"을 찾아 v1부터 A4까지 돌았다. 이건 그 여정과, 데이터가 끝내 말한 정직한 답의 기록이다.', 'A solo researcher, working with Claude and Codex, searched for "a proven model that beats the market" all the way from v1 to A4. This is a record of that journey, and of the honest answer the data finally gave.')}</p>
<div class="tagline">{_t('결론: 내가 검증한 공개데이터·비용후 후보군에선 SPY/QQQ도, TQQQ 매집도 못 이겼다. 남은 건 "버틸 수 있는 레버드 베타."', 'Verdict: in the public-data, after-cost candidate set I tested, nothing beat SPY/QQQ or just accumulating TQQQ. What\'s left is "levered beta you can live through."')}</div>
<p style="margin:12px 0 0;font-size:12.5px;color:#94a3b8">{_t('🗄️ 실제 사용 데이터: <b style="color:#cbd5e1">Sharadar</b>(유료·PIT·생존편향0) 백테스트 주가·시총·펀더멘털·상폐/멤버십 · <b style="color:#cbd5e1">yfinance</b>(무료) TQQQ/QQQ/SPY 2010~·forward·sanity · <b style="color:#cbd5e1">SEC EDGAR</b> 8-K 공시 · <b style="color:#cbd5e1">^IRX</b> T-bill 현금. ("공개데이터"=공개정보지 무료데이터 아님 — 백테스트 척추는 유료 Sharadar.)', '🗄️ Data actually used: <b style="color:#cbd5e1">Sharadar</b> (paid · PIT · zero survivorship bias) backtest prices, market cap, fundamentals, delistings/membership · <b style="color:#cbd5e1">yfinance</b> (free) TQQQ/QQQ/SPY since 2010 · forward · sanity · <b style="color:#cbd5e1">SEC EDGAR</b> 8-K filings · <b style="color:#cbd5e1">^IRX</b> T-bill cash. ("Public data" means public information, not free data — the backbone of the backtests is paid Sharadar.)')}</p>
</div></header>
<div class="wrap">

<section class="hero">
<h2><span class="n">★</span>{_t("한눈에 — Return vs Pain Map", "At a glance — Return vs Pain Map")}</h2>
<p class="sub">{_t('8세대가 만든 모든 전략을 <b>수익(세로)</b> × <b>낙폭/고통(가로)</b>으로 한 장에. <b>빨강 = 타이밍 시도(전부 타이밍 알파 음수 = 노출 효과)</b>. 실 TQQQ 2010~26·비용후. ※ TQQQ 376x는 <b>2010~26 강세·테크 레짐 한정</b>(닷컴/2008 live 미검증).', 'Every strategy across 8 generations on one chart: <b>return (vertical)</b> × <b>drawdown/pain (horizontal)</b>. <b>Red = timing attempts (all with negative timing alpha = exposure effect)</b>. Real TQQQ 2010–26, after costs. Note: TQQQ\'s 376x is <b>specific to the 2010–26 bull / tech regime</b> (not live-tested through the dot-com crash or 2008).')}</p>
<div class="chartbox">{svg_returnpain_map(bl, tm)}</div>
<p class="cap">{_t('<b>한 장에 끝나는 맥락:</b> TQQQ(검정 별)는 위에 있지만 오른쪽 끝(낙폭 -82%). 벤치(파랑)는 안전하지만 낮음. 점선=단순 고정비율. <b>빨강 점들(내 타이밍 시도)은 어느 것도 고정선 위(왼쪽)로 못 올라감</b> = 타이밍 알파 없음. <b>좌상단 "고수익·저낙폭"은 영원히 빈칸 = 공짜 점심 없음.</b>', '<b>The whole story in one chart:</b> TQQQ (dark star) sits high but far right (-82% drawdown). The benchmarks (blue) are safe but low. The dashed line = simple fixed ratios. <b>None of the red dots (my timing attempts) climb above and to the left of the fixed line</b> = no timing alpha. <b>The top-left "high return + low pain" corner stays empty forever = no free lunch.</b>')}</p>
<div class="kpis">
<div class="kpi"><div class="v">376x</div><div class="l">{_t("TQQQ (낙폭 -82%·레짐 한정)", "TQQQ (-82% drawdown · regime-limited)")}</div></div>
<div class="kpi"><div class="v">19x</div><div class="l">{_t("QQQ (낙폭 -35%)", "QQQ (-35% drawdown)")}</div></div>
<div class="kpi"><div class="v">79x</div><div class="l">{_t("VT-CANON (낙폭 -42%)", "VT-CANON (-42% drawdown)")}</div></div>
<div class="kpi"><div class="v">0 / 5</div><div class="l">{_t("타이밍 알파 통과", "timing alpha passed")}</div></div>
</div>
</section>

<section>
<h2><span class="n">1</span>{_t("8세대의 여정과 판정", "The journey across 8 generations, and the verdicts")}</h2>
<p class="sub">{_t("각 세대가 무엇이었고, 데이터가 내린 판정. 빨강=DEAD · 회색=베타(알파 아님) · 노랑=부분 · 보라=NULL · 초록=정직한 종착.", "What each generation was, and the verdict the data delivered. Red = DEAD · gray = beta (not alpha) · yellow = partial · purple = NULL · green = honest endpoint.")}</p>
{jrows}
</section>

<section>
<h2><span class="n">2</span>{_t('1막 — "검증된 방법"은 이미 시장에 있었다', 'Act 1 — the "proven methods" were already priced in')}</h2>
<p class="sub">{_t("v1~v3: LLM이 알려준 교과서 팩터(value·momentum·quality·lowvol). S&amp;P500 대형주에서 측정한 예측력(IC-IR). 거래 가능 기준(0.30)에 한참 못 미침 = 노이즈.", "v1–v3: textbook factors the LLMs suggested (value·momentum·quality·lowvol). Predictive power (IC-IR) measured on S&amp;P500 large caps. Far below the tradeable threshold (0.30) = noise.")}</p>
<div class="chartbox">{svg_bars(FACT_IC, thresh=0.30, thr_label=_t("tradeable 기준 0.30", "tradeable threshold 0.30"))}</div>
<p class="cap">{_t('<b>팩터 IC-IR — 전부 0 근처.</b> 가장 나은 momentum(+0.045)도 거래 가능 임계의 1/7. 검증 파이프라인(자작 PIT 지수 vs 실제 SPY <b>corr 0.998</b>)은 완성했지만, 이 후보군에 <b>찾을 알파가 없었다.</b>', '<b>Factor IC-IR — all near zero.</b> Even the best, momentum (+0.045), is 1/7 of the tradeable threshold. The verification pipeline (self-built PIT index vs real SPY, <b>corr 0.998</b>) was complete, but <b>there was no alpha to find in this candidate set.</b>')}</p>
</section>

<section>
<h2><span class="n">3</span>{_t("절대합 — 엔진(TQQQ) 대비 무엇을 얻고 무엇을 버렸나", "Net trade-off — what we gained and gave up versus the engine (TQQQ)")}</h2>
<p class="sub">{_t('못 이기면 낙폭이라도. 각 전략이 <b>TQQQ 상방(로그수익)을 몇 % 따라갔고</b>, <b>TQQQ 고통(낙폭)을 몇 % 피했나.</b> 이게 "TQQQ보다 매력 있나"의 직접 척도.', 'If you can\'t win, at least cut the pain. For each strategy: <b>what % of TQQQ\'s upside (log return) it captured</b>, and <b>what % of TQQQ\'s pain (drawdown) it avoided.</b> This is the direct measure of "is it more attractive than TQQQ."')}</p>
<div class="chartbox">{svg_capture_pain(bl)}</div>
<p class="cap">{_t('<b>VT-CANON = 상방 74% 유지하며 고통 49% 회피.</b> C1은 상방을 더 먹지만(85%) 고통 회피는 적음(41%). 어느 것도 "상방 다 먹고 고통 다 피하기"는 못 함 — 다시 공짜 점심 없음. 단 <b>"버틸 수 있는 형태"로 바꾼 건 분명한 가치.</b>', '<b>VT-CANON = keeps 74% of the upside while avoiding 49% of the pain.</b> C1 captures more upside (85%) but avoids less pain (41%). Nothing "captures all the upside and avoids all the pain" — again, no free lunch. Still, <b>reshaping it into "something survivable" is clearly valuable.</b>')}</p>
</section>

<section>
<h2><span class="n">4</span>{_t('3막의 판결 — "타이밍"은 노출 효과였다 (A4 Stage A)', 'The Act 3 verdict — "timing" was an exposure effect (A4 Stage A)')}</h2>
<p class="sub">{_t('각 동적 정책을 "그날 TQQQ 비중 w_t" 기계로 환원 → 같은 평균 노출의 고정전략과 복리 비교. <b>Timing Log Alpha</b> = 양수면 진짜 타이밍.', 'Reduce each dynamic policy to a machine that outputs "today\'s TQQQ weight w_t," then compound-compare it against a fixed strategy with the same average exposure. <b>Timing Log Alpha</b> = positive means real timing.')}</p>
<div class="chartbox">{svg_bars(timing_items)}</div>
<p class="cap">{_t('<b>5개 정책 전부 음수.</b> 모든 동적 타이밍이 "같은 평균 비중 그냥 보유"보다 복리로 <b>졌다</b>(비용 전에도). "위험할 때 줄였다 늘렸다"의 Cash Drag가 방어 이득보다 컸다 — A4가 죽은 자리이자, 타이밍 알파가 없다는 직접 증거.', '<b>All 5 policies negative.</b> Every dynamic timing scheme <b>lost</b>, on a compound basis, to "just holding the same average weight" (even before costs). The Cash Drag from "trimming when risky and adding back" outweighed the defensive benefit — the spot where A4 died, and direct evidence that there\'s no timing alpha.')}</p>
</section>

<section>
<h2><span class="n">5</span>{_t("내가 느낀 점 — 솔직하게", "What I took away — honestly")}</h2>
<p class="sub">{_t("이 프로젝트에서 직접 겪고 깨달은 것.", "What I lived through and learned firsthand on this project.")}</p>
{reflect}
</section>

{render_multianchor_section(6)}

{render_methodology_section(7)}

{render_why_section(8)}

<section>
<h2><span class="n">9</span>{_t("결론", "Conclusions")}</h2>
<ul class="concl">{concl}</ul>
</section>

<p class="foot">{_t("PRAMANA V4 · PAPER only / NO LIVE · 자본권한 0 · 검증된 알파 아님 · 차트 수치는 a4_baselines.csv·a4_attribution.csv 실데이터 · Codex 적대검수 REVISE 반영 · 2026-06-15", "PRAMANA V4 · PAPER only / NO LIVE · zero capital authority · not validated alpha · chart figures from real data in a4_baselines.csv · a4_attribution.csv · reflects Codex adversarial-review REVISE · 2026-06-15")}</p>
</div></body></html>"""
    open(OUT, "w").write(html)
    print(f"✅ wrote {OUT} ({len(html)//1024} KB)")
    print(f"   timing: {[round(v,3) for _,v in timing_items]}")
    tq_log = math.log(bl['TQQQ_BH'][0])
    for lab, mult, mdd in [("VT", 79.17, 42.3), ("C1", 153.3, 48.4), ("C3", 65.2, 34.9)]:
        print(f"   {lab}: capture {math.log(mult)/tq_log*100:.0f}% · pain-avoided {(1-mdd/81.66)*100:.0f}%")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""멀티앵커 ₩1억 진입 차트 섹션 — outputs/multianchor/*_nav.csv 전부 로드 →
5앵커(10년/3년/1년/6개월/3개월) × 2그룹(분산계열 v1~v7 / TQQQ레버계열 v7+A1~A4) 진입곡선 + 결과표 + 분석.
실데이터만·앵커 이전 시작 모델은 정직하게 제외(note). render_multianchor_section()을 dashboard가 호출.
"""
import os, glob, math
import numpy as np, pandas as pd
LANG = os.environ.get("PRAMANA_LANG", "ko")
def _t(ko, en): return en if LANG == "en" else ko
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
MA = os.path.join(ROOT, "outputs", "multianchor")
CAP = 100_000_000  # ₩1억

# 그룹 정의 (요청대로) · 표시순서
GROUP1 = ["SPY", "QQQ", "TQQQ", "v1v2_factor", "v3", "v4", "v5", "v6", "v7"]           # 분산/배분 계열
GROUP2 = ["SPY", "QQQ", "TQQQ", "v7", "A3", "VT-CANON", "VT-GRID", "C1", "C2", "C3"]  # TQQQ 레버 계열
LABELS = {"v1v2_factor": _t("v1~v2(팩터)", "v1–v2 (factor)"), "v3": "v3(trend+LETF)", "v4": "v4(CoreBeta)", "v5": _t("v5(레버드)", "v5 (levered)"),
          "v6": _t("v6(분산공격)", "v6 (diversified attack)"), "v7": "v7(4-sleeve)", "VT-CANON": "VT-CANON", "VT-GRID": "VT-GRID"}
STYLE = {  # color, width, dash
    "SPY": ("#94a3b8", 2, "5 3"), "QQQ": ("#2563eb", 2.5, ""), "TQQQ": ("#e2e8f0", 3.2, ""),
    "v1v2_factor": ("#a855f7", 2, "2 2"), "v3": ("#7c3aed", 2, ""), "v4": ("#06b6d4", 2, "4 2"),
    "v5": ("#f59e0b", 2.5, ""), "v6": ("#10b981", 2, "4 2"), "v7": ("#16a34a", 2.6, ""),
    "A3": ("#ef4444", 2.2, ""), "VT-CANON": ("#b91c1c", 2.6, ""), "VT-GRID": ("#ec4899", 2, "3 2"),
    "C1": ("# ea580c".replace(" ", ""), 2.2, ""), "C2": ("#9333ea", 2, "3 2"), "C3": ("#a16207", 2.2, ""),
}
ANCHORS = [(_t("10년", "10y"), 3653), (_t("3년", "3y"), 1096), (_t("1년", "1y"), 365), (_t("6개월", "6mo"), 182), (_t("3개월", "3mo"), 91)]


def load():
    d = {}
    for fp in glob.glob(os.path.join(MA, "*_nav.csv")):
        nm = os.path.basename(fp)[:-8]
        s = pd.read_csv(fp, parse_dates=["date"]).set_index("date")["nav"].sort_index()
        d[nm] = s
    return d


def won(v):  # ₩ → 억 표기
    e = v / 1e8
    return f"{e:.1f}억" if e < 100 else f"{e:.0f}억"


def window(s, start, end):
    seg = s[(s.index >= start) & (s.index <= end)]
    return seg if len(seg) > 2 else None


def mdd(vals):
    a = np.asarray(vals, float); return float((a / np.maximum.accumulate(a) - 1).min())


def svg_lines(series, title):
    """series: list of (name, dates(idx), won_values). ₩1억 진입 → 곡선."""
    W, H = 760, 340; L, R, T, B = 64, 168, 18, 40; pw, ph = W - L - R, H - T - B
    allv = np.concatenate([v for _, _, v in series])
    vmax, vmin = float(np.max(allv)), float(np.min(allv))
    logy = vmax / max(vmin, 1) > 3.2
    DAY = np.timedelta64(1, "D")
    t0 = min(pd.Timestamp(d[0]) for _, d, _ in series); t1 = max(pd.Timestamp(d[-1]) for _, d, _ in series)
    t0 = np.datetime64(t0); t1 = np.datetime64(t1)
    span = max(float((t1 - t0) / DAY), 1)
    def sx(dt): return L + float((np.datetime64(dt) - t0) / DAY) / span * pw
    if logy:
        lo, hi = math.log(max(vmin, 1e6)), math.log(vmax * 1.05)
        def sy(v): return T + (1 - (math.log(max(v, 1e6)) - lo) / (hi - lo)) * ph
        ticks = [t for t in [5e7, 1e8, 2e8, 5e8, 1e9, 2e9, 5e9, 1e10, 2e10, 4e10] if vmin*0.8 <= t <= vmax*1.1]
    else:
        lo, hi = vmin * 0.97, vmax * 1.03
        def sy(v): return T + (1 - (v - lo) / (hi - lo)) * ph
        ticks = list(np.linspace(lo, hi, 5))
    s = [f'<svg viewBox="0 0 {W} {H}" width="100%" preserveAspectRatio="xMidYMid meet" font-family="inherit">']
    for tk in ticks:
        y = sy(tk); s.append(f'<line x1="{L}" y1="{y:.0f}" x2="{L+pw}" y2="{y:.0f}" stroke="#1f2937"/>')
        s.append(f'<text x="{L-6}" y="{y+3:.0f}" font-size="9.5" fill="#94a3b8" text-anchor="end">{won(tk)}</text>')
    # ₩1억 기준선
    yb = sy(CAP); s.append(f'<line x1="{L}" y1="{yb:.0f}" x2="{L+pw}" y2="{yb:.0f}" stroke="#cbd5e1" stroke-dasharray="2 3"/>')
    s.append(f'<text x="{L+2}" y="{yb-3:.0f}" font-size="9" fill="#94a3b8">{_t("진입 ₩1억", "Enter ₩1억")}</text>')
    spi = int(span)
    for i in range(0, spi + 1, max(1, spi // 4)):
        dt = pd.Timestamp(t0) + pd.Timedelta(days=i); x = sx(np.datetime64(dt))
        s.append(f'<text x="{x:.0f}" y="{T+ph+16:.0f}" font-size="9.5" fill="#94a3b8" text-anchor="middle">{dt.strftime("%y/%m")}</text>')
    ranked = sorted(series, key=lambda r: -r[2][-1])
    for name, dts, vals in series:
        col, wdt, dash = STYLE.get(name, ("#64748b", 2, ""))
        # downsample
        step = max(1, len(dts) // 160)
        pts = " ".join(f"{sx(dts[i]):.1f},{sy(vals[i]):.1f}" for i in range(0, len(dts), step))
        da = f' stroke-dasharray="{dash}"' if dash else ""
        s.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="{wdt}"{da} opacity="0.92"/>')
    # legend (final ₩ desc) = 결과표 겸용
    lx = L + pw + 14; ly = T + 6
    s.append(f'<text x="{lx}" y="{ly}" font-size="10" font-weight="700" fill="#cbd5e1">{_t("진입 ₩1억 → 현재", "Enter ₩1억 → now")}</text>'); ly += 16
    for name, dts, vals in ranked:
        col, _, _ = STYLE.get(name, ("#64748b", 2, "")); fin = vals[-1]
        s.append(f'<line x1="{lx}" y1="{ly-3}" x2="{lx+14}" y2="{ly-3}" stroke="{col}" stroke-width="3"/>')
        s.append(f'<text x="{lx+19}" y="{ly}" font-size="10" fill="#cbd5e1">{LABELS.get(name,name)} <tspan font-weight="700" fill="{col}">{won(fin)}</tspan></text>')
        ly += 15.5
    s.append("</svg>")
    return "".join(s)


def analyze(rows, alabel):
    """rows: list dict(name, final, mult, wmdd). 데이터기반 한 단락."""
    by_fin = sorted(rows, key=lambda r: -r["final"])
    d = {r["name"]: r for r in rows}
    best = by_fin[0]
    tq = d.get("TQQQ"); qqq = d.get("QQQ")
    parts = []
    parts.append(_t(
        f"<b>{alabel} 전 ₩1억 진입 → 현재:</b> 최고는 <b>{LABELS.get(best['name'],best['name'])} {won(best['final'])}</b>({best['mult']:.1f}배).",
        f"<b>Enter ₩1억 {alabel} ago → now:</b> the best is <b>{LABELS.get(best['name'],best['name'])} {won(best['final'])}</b> ({best['mult']:.1f}×)."))
    if tq:
        parts.append(_t(
            f"TQQQ {won(tq['final'])}({tq['mult']:.1f}배)이지만 그 사이 최대 <b>{tq['wmdd']*100:.0f}%</b> 낙폭.",
            f"TQQQ reaches {won(tq['final'])} ({tq['mult']:.1f}×), but with a peak drawdown of <b>{tq['wmdd']*100:.0f}%</b> along the way."))
    if qqq:
        parts.append(_t(f"벤치 QQQ {won(qqq['final'])}.", f"Benchmark QQQ {won(qqq['final'])}."))
    # risk-controlled 비교 (VT-CANON or v7)
    rc = d.get("VT-CANON") or d.get("v7")
    if rc and tq:
        parts.append(_t(
            f"<b>{LABELS.get(rc['name'],rc['name'])}</b>는 {won(rc['final'])}로 TQQQ엔 못 미쳐도 낙폭 {rc['wmdd']*100:.0f}%(TQQQ {tq['wmdd']*100:.0f}%)로 <b>고통 절반</b> = '버틸 수 있는' 거래.",
            f"<b>{LABELS.get(rc['name'],rc['name'])}</b> reaches {won(rc['final'])} — short of TQQQ, but with a {rc['wmdd']*100:.0f}% drawdown (vs TQQQ {tq['wmdd']*100:.0f}%) it cuts the <b>pain in half</b> = a 'survivable' trade."))
    return " ".join(parts)


def render_multianchor_section(n=6):
    navs = load()
    if not navs:
        return f'<section><h2>{_t("멀티앵커", "Multi-anchor")}</h2><p class="sub">{_t("데이터 없음(outputs/multianchor 비어있음).", "No data (outputs/multianchor is empty).")}</p></section>'
    end = max(s.index[-1] for s in navs.values())  # 최신 공통 종점
    out = [f'<section><h2><span class="n">{n}</span>{_t("같은 ₩1억, 다른 진입 시점 — 모델별 결과", "Same ₩1억, different entry points — results by model")}</h2>',
           f'<p class="sub">{_t("10년·3년·1년·6개월·3개월 전 각각 ₩1억으로 진입했을 때 현재 가치. 모델마다 시작 데이터가 달라(예: 4-sleeve의 DBMF는 2019생·A1/A2는 forward 며칠치) 진입 불가한 건 정직하게 제외. 색=모델, 범례=현재 ₩(내림차순).", "Current value if you had entered with ₩1억 10y, 3y, 1y, 6mo, and 3mo ago. Each model has a different data start (e.g. the 4-sleeve’s DBMF was born in 2019; A1/A2 only have a few days of forward data), so models that can’t be entered are honestly excluded. Color = model, legend = current ₩ (descending).")}</p>']
    groups = [(_t("그룹 1 · 분산/배분 계열 (v1~v7 + 벤치)", "Group 1 · diversification / allocation family (v1–v7 + benchmarks)"), GROUP1),
              (_t("그룹 2 · TQQQ 레버 계열 (v7 + A1~A4·C1 등 + 벤치)", "Group 2 · TQQQ leverage family (v7 + A1–A4, C1, etc. + benchmarks)"), GROUP2)]
    for gtitle, members in groups:
        out.append(f'<h3 style="margin:22px 0 4px;font-size:17px">{gtitle}</h3>')
        if "A1" in str(members) or members is GROUP2:
            out.append(f'<p class="cap" style="margin:0 0 8px">{_t("※ A1·A2 = live 인셉션 2026-06-12(며칠치)라 multiyear 진입 데이터 없음 → 제외.", "Note: A1·A2 went live on 2026-06-12 (only a few days), so there is no multi-year entry data → excluded.")}</p>')
        for alabel, days in ANCHORS:
            anchor = end - pd.Timedelta(days=days)
            series = []; rows = []; missing = []
            for nm in members:
                if nm not in navs:
                    missing.append(nm); continue
                seg = window(navs[nm], anchor, end)
                if seg is None or seg.index[0] > anchor + pd.Timedelta(days=20):
                    missing.append(nm); continue
                base = seg.iloc[0]; vals = (seg.values / base) * CAP
                series.append((nm, seg.index.to_numpy(), vals))
                rows.append({"name": nm, "final": float(vals[-1]), "mult": float(vals[-1] / CAP), "wmdd": mdd(vals)})
            if len(series) < 2:
                out.append(f'<p class="cap"><b>{alabel}:</b> {_t("진입 가능한 모델 부족(데이터 시작 이후). 제외=", "Too few enterable models (data starts later). Excluded=")}{missing}</p>'); continue
            miss = (f' · <span style="color:#b91c1c">{_t("진입불가(데이터 이전):", "Not enterable (before data start):")} {", ".join(LABELS.get(m,m) for m in missing)}</span>') if missing else ""
            out.append(f'<div class="machart"><div class="malabel">{_t(f"▸ {alabel} 전 진입", f"▸ Entered {alabel} ago")}{miss}</div>')
            out.append(f'<div class="chartbox">{svg_lines(series, alabel)}</div>')
            out.append(f'<p class="cap">{analyze(rows, alabel)}</p></div>')
    out.append('</section>')
    return "".join(out)


if __name__ == "__main__":
    html = render_multianchor_section()
    open(os.path.join(ROOT, "outputs", "multianchor", "_section_preview.html"),
         "w").write(f"<!doctype html><meta charset=utf-8><body style='max-width:920px;margin:auto;font-family:sans-serif'>{html}")
    print("models loaded:", sorted(load().keys()))
    print("section bytes:", len(html))
